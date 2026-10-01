// Session 54: which grid network snapshot /network draws. Two copies exist:
// - the hourly one, one JSON object in the public Supabase Storage bucket erw-public (network/grid_network.json), written
//   every hour by warehouse/derived/network_hourly.py (.github/workflows/hourly-network.yml): object storage, not the
//   database;
// - the committed one, data/grid_network.json, written by the daily run (warehouse/derived/grid_network.py): the fallback.
// The page reads the Storage object with a one-hour revalidation and draws it when it is whole and at least as new as the
// committed one; otherwise the committed one. No imports beyond types, so a test can load this file in Node.
import type { Snapshot } from "../app/network/Network";

export const NETWORK_OBJECT = "storage/v1/object/public/erw-public/network/grid_network.json";

export function storageUrl(supabaseUrl: string): string {
  return `${new URL(supabaseUrl).origin}/${NETWORK_OBJECT}`;
}

/** A snapshot the page can draw: nodes with positions, hours, and every link as long as the hours. */
export function isSnapshot(x: unknown): x is Snapshot {
  const s = x as Snapshot;
  return !!s && typeof s.built === "string" && Array.isArray(s.window) && Array.isArray(s.hours) && s.hours.length > 0
    && Array.isArray(s.nodes) && s.nodes.length > 0 && s.nodes.every((n) => typeof n.id === "string" && [n.x, n.y, n.z].every((v) => typeof v === "number"))
    && Array.isArray(s.links) && s.links.every((l) => Array.isArray(l.mw) && l.mw.length === s.hours.length);
}

/** The Storage snapshot when it is whole and its newest hour is not older than the committed one's; else the committed. */
export function pickSnapshot(fetched: unknown, committed: Snapshot): { snap: Snapshot; from: "storage" | "committed" } {
  if (isSnapshot(fetched) && fetched.hours[fetched.hours.length - 1] >= committed.hours[committed.hours.length - 1]) {
    return { snap: fetched, from: "storage" };
  }
  return { snap: committed, from: "committed" };
}

/** Session 55: the hourly snapshot from Storage (a one-hour revalidation), or null when it cannot be read. Shared by
 * /network and problem set E, so both draw the same snapshot. */
export async function fetchHourly(revalidate = 3600): Promise<unknown> {
  try {
    const url = process.env.SUPABASE_URL;
    if (!url) return null;
    const r = await fetch(storageUrl(url), { next: { revalidate }, signal: AbortSignal.timeout(8000) });
    return r.ok ? await r.json() : null;
  } catch {
    return null;
  }
}

/** Session 55 (problem set E, and check-values' net| keys): one BA's ties that reported a flow in an hour, each signed
 * from that BA's side (positive: it exported over the tie). */
export function tiesAt(snap: Snapshot, id: string, hour: string): { other: string; mw: number }[] {
  const h = snap.hours.indexOf(hour);
  if (h < 0) return [];
  return snap.links.filter((l) => (l.a === id || l.b === id) && l.mw[h] !== null)
    .map((l) => ({ other: l.a === id ? l.b : l.a, mw: (l.a === id ? 1 : -1) * (l.mw[h] as number) }));
}

/** Each BA's net export in an hour: the sum of its ties' flows in the snapshot, signed from its side. */
export function netExports(snap: Snapshot, hour: string): Map<string, number> {
  const h = snap.hours.indexOf(hour);
  const out = new Map<string, number>();
  if (h < 0) return out;
  for (const l of snap.links) {
    const v = l.mw[h];
    if (v === null) continue;
    out.set(l.a, (out.get(l.a) ?? 0) + v);
    out.set(l.b, (out.get(l.b) ?? 0) - v);
  }
  return out;
}

/** The BA with the largest net export in an hour (the first by code on a tie), or null. */
export function topExporter(snap: Snapshot, hour: string): { id: string; mw: number } | null {
  let best: { id: string; mw: number } | null = null;
  for (const [id, mw] of [...netExports(snap, hour)].sort((a, b) => a[0].localeCompare(b[0]))) if (!best || mw > best.mw) best = { id, mw };
  return best;
}

/** The value of a net| check key on a snapshot: net|ties|<BA>|<hour> (ties reporting), net|maxflow|<BA>|<hour> (the
 * largest flow on them, MW, either way), net|topexport|<hour> (the largest net export, MW). Undefined when the
 * snapshot does not hold the hour. */
export function netValue(snap: Snapshot, key: string): number | undefined {
  const p = key.split("|");
  const hour = p[0] === "net" && p[1] === "topexport" ? p[2] : p[3];
  if (!snap.hours.includes(hour)) return undefined;
  if (p[1] === "ties") return tiesAt(snap, p[2], hour).length;
  if (p[1] === "maxflow") { const t = tiesAt(snap, p[2], hour); return t.length ? Math.max(...t.map((x) => Math.abs(x.mw))) : undefined; }
  if (p[1] === "topexport") return topExporter(snap, hour)?.mw;
  return undefined;
}
