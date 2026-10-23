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
// Session 1165 (chain 078), the Network tab's balance: calc|bal|<G>|<D>|<X> (a new op of calc: G less D less X, its
// arithmetic in scripts/check-calc.mjs) and a new kind, netbal|absmean|<BA>|<from>|<to> and netbal|hours|<BA>|<from>|<to>
// (netbalValue below, run by check-values on the snapshot and the two tables' rows).
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

/** A grid's net generation in the hour (eia930_all_generation, the week's hourly values aligned to the snapshot's
 * hours), the figure the gravity shape sizes a circle by; null where the hour is not held. */
export function generationAt(snap: Snapshot, ba: string, hour: string, week: (number | null)[] | undefined): Fig | null {
  const h = snap.hours.indexOf(hour);
  const v = h >= 0 ? week?.[h] : null;
  return v === null || v === undefined ? null
    : { check: `series|eia930_all_generation|eia930:${ba}|net_generation_mw|${hour}`, raw: v, tip: `eia930_all_generation, entity eia930:${ba}, net_generation_mw, hour ${hourName(hour)}, read with the snapshot refreshed ${refreshName(snap.built)}` };
}

// ------------------------------------------------------------------ the balance (session 1165, chain 078)
// The Grid pack's item 3 (docs/reviews/packs/grid.md, section 6): for CAISO, PJM, MISO and SPP the ties do not sum to net
// generation minus demand. Session 360 (docs/methods/eia930_balance.md) split the gap in two; the panel states it for the
// grid in view from the tables the tab already reads: in the hour shown, net generation (eia930_all_generation), demand
// (the panel's own demand figure), the net export over the reporting ties (the snapshot) and the gap, generation less
// demand less net export, keyed calc|bal|<G>|<D>|<X> ("~" for "|"), which check-values recomputes from the three keys;
// over the snapshot's week, the mean of the gap's absolute value (session 360's measure) and the count of hours that hold
// all three, keyed netbal|absmean|<BA>|<from>|<to> and netbal|hours|<BA>|<from>|<to>, recomputed by netbalValue below on
// the snapshot check-values reads and the two tables' rows. An hour holds the ties when every tie of the grid that holds
// a flow in some hour of the window holds one in it (as session 360 took PJM's "hours all seven ties are held").

/** The split session 360 found, in one line: the hover tip of the gap and of its mean. */
export const BALANCE_SPLIT = "Session 360 (docs/methods/eia930_balance.md): CAISO's and MISO's ties sum to their own total interchange, and their gap is that total against net generation minus demand; SPP's total interchange closes against net generation minus demand, and its ties do not sum to it; PJM has both; ERCOT, NYISO and ISO-NE close.";

/** Where session 360 found each grid's gap, in words, no figure. */
export const BALANCE_WHERE: Record<string, string> = {
  CISO: "its ties sum to its own total interchange, and the gap sits between that total and net generation minus demand",
  MISO: "its ties sum to its own total interchange, and the gap sits between that total and net generation minus demand",
  PJM: "in both places: its ties do not sum to its own total interchange, and that total does not equal net generation minus demand, the two partly offsetting",
  SWPP: "between its ties and its own total interchange: the total closes against net generation minus demand, the ties do not sum to it",
  ERCO: "nowhere of note: its ties, its total interchange and net generation minus demand agree",
  NYIS: "nowhere of note: its ties, its total interchange and net generation minus demand agree",
  ISNE: "nowhere of note: its ties, its total interchange and net generation minus demand agree",
};

/** The window's hours and one grid's links, each hour taken from the first snapshot that holds it (the hourly one first,
 * then the committed one, as check-values reads them); null when no snapshot holds an hour from `from` to `to`, or
 * none holds `from` or `to`. A link a snapshot lacks is null in that snapshot's hours. */
export function windowOf(snaps: Snapshot[], ba: string, from: string, to: string): { hours: string[]; links: { a: string; b: string; mw: (number | null)[] }[] } | null {
  const hours = [...new Set(snaps.flatMap((s) => s.hours.filter((h) => h >= from && h <= to)))].sort();
  if (!hours.length || hours[0] !== from || hours[hours.length - 1] !== to) return null;
  const own = (l: { a: string; b: string }) => l.a === ba || l.b === ba;
  const keys = [...new Set(snaps.flatMap((s) => s.links.filter(own).map((l) => `${l.a}|${l.b}`)))].sort();
  const src = hours.map((h) => { const s = snaps.find((x) => x.hours.includes(h))!; return { s, i: s.hours.indexOf(h) }; });
  const links = keys.map((k) => {
    const [a, b] = k.split("|");
    return { a, b, mw: src.map(({ s, i }) => { const v = s.links.find((l) => l.a === a && l.b === b)?.mw[i]; return v === undefined ? null : v; }) };
  });
  return { hours, links };
}

/** Rows of an hourly series ([ts_utc, value] or {ts_utc, value}) aligned to the hours, as the page aligns them
 * (app/network/data.ts liveExtras: an hour held by exactly one row, its value rounded to 0.1 MW); null where not held. */
export function alignHours(rows: ([string, number] | { ts_utc: string; value: number })[], hours: string[]): (number | null)[] {
  const by = new Map<string, { s: number; n: number }>();
  for (const r of rows) {
    const [ts, v] = Array.isArray(r) ? r : [r.ts_utc, r.value];
    const h = new Date(Math.floor(new Date(ts).getTime() / 3_600_000) * 3_600_000).toISOString().replace(".000Z", "Z");
    const a = by.get(h) ?? { s: 0, n: 0 };
    a.s += Number(v); a.n += 1; by.set(h, a);
  }
  return hours.map((h) => { const a = by.get(h); return a && a.n === 1 ? Math.round(a.s * 10) / 10 : null; });
}

/** The gap in each hour of the window that holds all three: every tie of the grid (each one with a flow in some hour of
 * the window), its net generation and its demand. Gap = net generation less demand less net export, MW. */
export function balanceGaps(hours: string[], links: { a: string; b: string; mw: (number | null)[] }[], ba: string,
  generation: (number | null)[] | undefined, demand: (number | null)[] | undefined): { hour: string; gap: number }[] {
  const held = (v: number | null | undefined): v is number => v !== null && v !== undefined && Number.isFinite(v);
  const ties = links.filter((l) => (l.a === ba || l.b === ba) && l.mw.some(held));
  if (!ties.length || !generation || !demand) return [];
  const out: { hour: string; gap: number }[] = [];
  hours.forEach((hour, i) => {
    const g = generation[i], d = demand[i];
    if (!held(g) || !held(d) || !ties.every((l) => held(l.mw[i]))) return;
    const x = ties.reduce((a, l) => a + (l.a === ba ? 1 : -1) * (l.mw[i] as number), 0);
    out.push({ hour, gap: z(g - d - x) });
  });
  return out;
}

/** The week's figures of the balance: the mean of the gap's absolute value and the count of hours. */
export function balanceWeek(gaps: { gap: number }[]): { absmean: number; hours: number } | null {
  if (!gaps.length) return null;
  return { absmean: gaps.reduce((a, x) => a + Math.abs(x.gap), 0) / gaps.length, hours: gaps.length };
}

/** check-values' netbal|absmean|<BA>|<from>|<to> and netbal|hours|<BA>|<from>|<to>: on the snapshots it reads (the
 * hourly one first) and the grid's rows of eia930_all_generation (net_generation_mw) and eia930_all_demand (demand_mw)
 * in the window. Undefined when the window or its hours are not held. */
export function netbalValue(check: string, snaps: Snapshot[], generation: ([string, number] | { ts_utc: string; value: number })[],
  demand: ([string, number] | { ts_utc: string; value: number })[]): number | undefined {
  const [head, what, ba, from, to] = check.split("|");
  if (head !== "netbal" || (what !== "absmean" && what !== "hours")) return undefined;
  const w = windowOf(snaps, ba, from, to);
  if (!w) return undefined;
  const week = balanceWeek(balanceGaps(w.hours, w.links, ba, alignHours(generation, w.hours), alignHours(demand, w.hours)));
  return week ? week[what] : undefined;
}

export type BalancePanel = { ba: string; hour: string; gen: Fig | null; demand: Fig | null; net: Fig | null; gap: Fig | null;
  absmean: Fig | null; hours: Fig | null; from: string; to: string; where: string };

/** The Network tab's balance for one grid: in the hour shown, net generation, demand (the panel's own figure, `demand`),
 * the net export over the reporting ties and the gap; over the snapshot's week, the gap's mean size and its hours. */
export function balancePanel(snap: Snapshot, ba: string, hour: string, generation: (number | null)[] | undefined,
  demandWeek: (number | null)[] | undefined, demand: Fig | null): BalancePanel {
  const from = snap.hours[0], to = snap.hours[snap.hours.length - 1];
  const gen = generationAt(snap, ba, hour, generation);
  const t = tiesOf(snap, ba, hour);
  const sum = z(t.reduce((a, x) => a + x.mw, 0));
  const net = t.length ? { check: `net|export|${ba}|${hour}`, raw: sum, tip: `eia930_all_interchange (the hourly network snapshot), ${ba}'s ${t.length} reporting ties summed, net export MW (negative: a net import), hour ${hourName(hour)}, refreshed ${refreshName(snap.built)}` } : null;
  const k = (f: Fig) => f.check.replaceAll("|", "~");
  const gap = gen && demand && net
    ? { check: `calc|bal|${k(gen)}|${k(demand)}|${k(net)}`, raw: z(gen.raw - demand.raw - net.raw), tip: `Net generation less demand less net export, the three figures beside it, hour ${hourName(hour)}. ${BALANCE_SPLIT}` }
    : null;
  const w = windowOf([snap], ba, from, to);
  const week = w ? balanceWeek(balanceGaps(w.hours, w.links, ba, generation, demandWeek)) : null;
  const span = `${hourName(from)} to ${hourName(to)}`;
  const weekTip = (what: string) => `${what}, over the hours from ${span} of the snapshot refreshed ${refreshName(snap.built)} that hold every tie of ${ba}, its net generation (eia930_all_generation) and its demand (eia930_all_demand). ${BALANCE_SPLIT}`;
  return { ba, hour, gen, demand, net, gap, from, to, where: BALANCE_WHERE[ba] ?? "",
    absmean: week ? { check: `netbal|absmean|${ba}|${from}|${to}`, raw: week.absmean, tip: weekTip("The mean of the gap's absolute value, MW") } : null,
    hours: week ? { check: `netbal|hours|${ba}|${from}|${to}`, raw: week.hours, tip: weekTip("The count of hours") } : null };
}

export type GravityRow ={ ba: string; gen: Fig | null; net: Fig | null; share: Fig | null };

/** The Gravity tab's panel: what the gravity shape draws for each grid in the hour, its net generation (the circle's
 * size), its net import (the pull) and the import as a percent of generation; the Lower 48's generation as the scale. */
export function gravityPanel(snap: Snapshot, bas: string[], center: string, hour: string, generation: Record<string, (number | null)[]> | undefined): { center: Fig | null; rows: GravityRow[] } {
  const genOf = (ba: string): Fig | null => generationAt(snap, ba, hour, generation?.[ba]);
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
