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
