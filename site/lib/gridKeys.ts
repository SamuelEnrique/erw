// Energy Research Warehouse (ERW) site, session 1151 (chain 077): the figures the Grid tool's Network and Gravity tabs
// show in the browser, computed on the server from the same snapshot, so each one is drawn on the page as served with a
// check key scripts/check-values.mjs recomputes, and a one-line source in its hover tip. And the Clean tab's "The last
// 24 hours" headline figures. Pure functions, type imports only, so a node test can load this file
// (scripts/test-grid-keys.mjs).
//
// The keys are kinds check-values already knows:
// - net|tie|<BA>|<other>|<hour>, net|export|<BA>|<hour>, net|import|<BA>|<hour>, net|ties|<BA>|<hour> (lib/network.ts
//   netValue, on the snapshot that holds the hour);
// - netsnap|<BA>|demand_mw|<hour> (the hourly snapshot's demand_recent) or series|eia930_all_demand|eia930:<BA>|demand_mw|<hour>,
//   chosen as the network component chooses them (app/network/Network.tsx demandKey);
// - series|eia930_all_generation|eia930:<BA>|net_generation_mw|<hour>, the gravity shape's circles;
// - calc|pct|<A>|<B> with A the net import key and B the generation key ("~" for "|"), the shape's pull as a share;
// - series|carbon_intensity_hourly|<entity>|intensity_generation|<hour>, the last 24 hours' latest, lowest and highest.
// A tie's flow is signed from the grid's side (positive: power left the grid), as ExchangeView and netValue sign it.
import type { Snapshot } from "../app/network/Network";

export type Fig = { check: string; raw: number; tip: string };

const hourName = (t: string) => `${t.slice(0, 10)} ${t.slice(11, 13)}:00 UTC`;
const refreshName = (t: string) => `${t.slice(0, 16).replace("T", " ")} UTC`;
/** -0 is written 0, as netValue returns it */
const z = (v: number) => v || 0;

/** The hour the network component opens on: the newest hour every reporting pair holds, else the newest of all. */
export function shownHour(snap: Snapshot, complete: { hour: string | null }): string {
  return complete.hour ?? snap.hours[snap.hours.length - 1];
}

/** One grid's ties that reported a flow in the hour, signed from its side, largest first (by size, then by code). */
export function tiesOf(snap: Snapshot, ba: string, hour: string): { other: string; mw: number }[] {
  const h = snap.hours.indexOf(hour);
  if (h < 0) return [];
  return snap.links.filter((l) => (l.a === ba || l.b === ba) && l.mw[h] !== null && l.mw[h] !== undefined)
    .map((l) => ({ other: l.a === ba ? l.b : l.a, mw: z((l.a === ba ? 1 : -1) * (l.mw[h] as number)) }))
    .sort((x, y) => Math.abs(y.mw) - Math.abs(x.mw) || x.other.localeCompare(y.other));
}

export type NetworkPanel = {
  hour: string; ba: string;
  ties: (Fig & { other: string; dir: "out" | "in" | "none" })[];
  /** the net over the reporting ties: an export (raw positive or zero) or an import (raw positive), null with no tie */
  net: (Fig & { kind: "export" | "import" }) | null;
  count: Fig;
  /** the grid's demand in the hour, where the snapshot or the week's demand holds it */
  demand: Fig | null;
};

/** The grid's demand in the hour, as the network component reads it: the week's eia930_all_demand first (`week`, one
 * value per hour of the snapshot), else the hourly snapshot's demand_recent, else the node's own newest demand. */
export function demandAt(snap: Snapshot, ba: string, hour: string, week?: (number | null)[]): Fig | null {
  const n = snap.nodes.find((x) => x.id === ba);
  const h = snap.hours.indexOf(hour);
  if (!n || h < 0) return null;
  const w = week?.[h];
  const v = w !== null && w !== undefined ? w : n.demand_recent && hour in n.demand_recent ? n.demand_recent[hour] : n.demand_ts === hour ? n.demand_mw : null;
  if (v === null || v === undefined) return null;
  const fromSnap = n.demand_src === "hourly" && !!n.demand_recent && hour in n.demand_recent && n.demand_recent[hour] === v;
  return fromSnap
    ? { check: `netsnap|${ba}|demand_mw|${hour}`, raw: v, tip: `The hourly network snapshot's demand (eia930_all_demand as the hourly refresh read it), ${ba}, demand_mw, hour ${hourName(hour)}, refreshed ${refreshName(snap.built)}` }
    : { check: `series|eia930_all_demand|eia930:${ba}|demand_mw|${hour}`, raw: v, tip: `eia930_all_demand, entity eia930:${ba}, demand_mw, hour ${hourName(hour)}, read with the snapshot refreshed ${refreshName(snap.built)}` };
}

/** The Network tab's panel for one grid in the hour: each reporting tie's MW and direction, the net, the count of ties,
 * and the demand where it is held. */
export function networkPanel(snap: Snapshot, ba: string, hour: string, week?: (number | null)[]): NetworkPanel {
  const src = (what: string) => `eia930_all_interchange (the hourly network snapshot), ${what}, hour ${hourName(hour)}, refreshed ${refreshName(snap.built)}`;
  const raw = tiesOf(snap, ba, hour);
  const ties = raw.map((t) => ({ other: t.other, dir: (t.mw > 0 ? "out" : t.mw < 0 ? "in" : "none") as "out" | "in" | "none",
    check: `net|tie|${ba}|${t.other}|${hour}`, raw: t.mw, tip: src(`tie ${ba} with ${t.other}, MW signed from ${ba}'s side`) }));
  const sum = z(raw.reduce((a, t) => a + t.mw, 0));
  const net = raw.length
    ? sum >= 0
      ? { kind: "export" as const, check: `net|export|${ba}|${hour}`, raw: sum, tip: src(`${ba}'s ${raw.length} reporting ties summed, net export MW`) }
      : { kind: "import" as const, check: `net|import|${ba}|${hour}`, raw: z(-sum), tip: src(`${ba}'s ${raw.length} reporting ties summed, net import MW`) }
    : null;
  return { hour, ba, ties, net, count: { check: `net|ties|${ba}|${hour}`, raw: raw.length, tip: src(`ties of ${ba} with a flow`) }, demand: demandAt(snap, ba, hour, week) };
}

export type GridNet = { ba: string; net: Fig | null; count: Fig };

/** The Lower 48's panel: each grid's net export over its reporting ties in the hour (negative: a net import). */
export function lower48Panel(snap: Snapshot, bas: string[], hour: string): GridNet[] {
  return bas.map((ba) => {
    const t = tiesOf(snap, ba, hour);
    const sum = z(t.reduce((a, x) => a + x.mw, 0));
    const tip = (what: string) => `eia930_all_interchange (the hourly network snapshot), ${what}, hour ${hourName(hour)}, refreshed ${refreshName(snap.built)}`;
    return { ba, net: t.length ? { check: `net|export|${ba}|${hour}`, raw: sum, tip: tip(`${ba}'s ${t.length} reporting ties summed, net export MW`) } : null,
      count: { check: `net|ties|${ba}|${hour}`, raw: t.length, tip: tip(`ties of ${ba} with a flow`) } };
  });
}

export type GravityRow = { ba: string; gen: Fig | null; net: Fig | null; share: Fig | null };

/** The Gravity tab's panel: what the gravity shape draws for each grid in the hour, its net generation (the circle's
 * size), its net import (the pull) and the import as a percent of generation; the Lower 48's generation as the scale. */
export function gravityPanel(snap: Snapshot, bas: string[], center: string, hour: string, generation: Record<string, (number | null)[]> | undefined): { center: Fig | null; rows: GravityRow[] } {
  const h = snap.hours.indexOf(hour);
  const genOf = (ba: string): Fig | null => {
    const v = h >= 0 ? generation?.[ba]?.[h] : null;
    return v === null || v === undefined ? null
      : { check: `series|eia930_all_generation|eia930:${ba}|net_generation_mw|${hour}`, raw: v, tip: `eia930_all_generation, entity eia930:${ba}, net_generation_mw, hour ${hourName(hour)}, read with the snapshot refreshed ${refreshName(snap.built)}` };
  };
  const rows = bas.map((ba): GravityRow => {
    const gen = genOf(ba);
    const t = tiesOf(snap, ba, hour);
    const imp = z(-t.reduce((a, x) => a + x.mw, 0));
    const net = t.length ? { check: `net|import|${ba}|${hour}`, raw: imp, tip: `eia930_all_interchange (the hourly network snapshot), ${ba}'s ${t.length} reporting ties summed, net import MW (negative: a net export), hour ${hourName(hour)}, refreshed ${refreshName(snap.built)}` } : null;
    const share = gen && net && gen.raw > 0
      ? { check: `calc|pct|${net.check.replaceAll("|", "~")}|${gen.check.replaceAll("|", "~")}`, raw: (net.raw / gen.raw) * 100, tip: `The net import over the net generation, both above, hour ${hourName(hour)}` }
      : null;
    return { ba, gen, net, share };
  });
  return { center: genOf(center), rows };
}

export type IntensityRow = { entity: string; variable: string; ts_utc: string; value: number };
export type DayFigures = { entity: string; latest: Fig & { ts: string }; low: Fig & { ts: string }; high: Fig & { ts: string }; hours: number };

/** The Clean tab's "The last 24 hours": for each entity, its latest, lowest and highest intensity of generation in the
 * 24 hours to the newest hour of all (`newest`, ms; the chart's own window), the earliest hour on a tie. */
export function lastDayFigures(rows: IntensityRow[], entities: string[], newest: number, table = "carbon_intensity_hourly"): DayFigures[] {
  const out: DayFigures[] = [];
  for (const e of entities) {
    const day = rows.filter((r) => r.entity === e && r.variable === "intensity_generation" && Date.parse(r.ts_utc) > newest - 24 * 3_600_000)
      .sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
    if (!day.length) continue;
    const fig = (r: IntensityRow, what: string) => ({ check: `series|${table}|${r.entity}|${r.variable}|${r.ts_utc}`, raw: r.value, ts: r.ts_utc,
      tip: `${table}, entity ${r.entity}, intensity_generation, ${what}: hour ${hourName(r.ts_utc)}` });
    let low = day[0], high = day[0];
    for (const r of day) { if (r.value < low.value) low = r; if (r.value > high.value) high = r; }
    out.push({ entity: e, latest: fig(day[day.length - 1], "the latest hour"), low: fig(low, "the lowest of the 24 hours"), high: fig(high, "the highest of the 24 hours"), hours: day.length });
  }
  return out;
}
