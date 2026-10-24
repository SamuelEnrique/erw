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

// ---------------------------------------------------------------------------------------------------------------------
// Session 1167 (chain 078): the Exchange blocks under the gravity shape (components/grid/ExchangeView.tsx). Each
// neighbour's flow in the hour shown keeps its key (net|tie|<BA>|<other>|<hour>); beside it, the same tie over the
// snapshot's week, keyed by a new kind, nettie|<stat>|<BA>|<other>|<from>|<to> with stat mean, min, max or hours: the
// tie's flow signed from the grid's side in every hour of the window that holds one, its mean (whole MW), its lowest and
// highest, and the count of those hours. check-values recomputes it with nettieValue below on the snapshots the net| keys
// read (the hourly one in Storage first, then the committed one, each hour from the first that holds it: windowOf). The
// direction in words is the sign's: "sends to" above zero, "takes from" below, "none" at zero.

export type TieWeek = { mean: number; min: number; max: number; hours: number };
export type TieStat = keyof TieWeek;
export const TIE_STATS: readonly TieStat[] = ["mean", "min", "max", "hours"];

/** One tie of the grid over the window's hours, signed from the grid's side: its mean (rounded to whole MW), lowest,
 * highest and the count of hours that hold a flow; null when the window holds no flow on the tie. */
export function tieWeek(links: { a: string; b: string; mw: (number | null)[] }[], ba: string, other: string): TieWeek | null {
  const l = links.find((x) => (x.a === ba && x.b === other) || (x.a === other && x.b === ba));
  if (!l) return null;
  const s = l.a === ba ? 1 : -1;
  const vs = l.mw.filter((v): v is number => v !== null && v !== undefined && Number.isFinite(v)).map((v) => z(s * v));
  if (!vs.length) return null;
  return { mean: z(Math.round(vs.reduce((a, v) => a + v, 0) / vs.length)), min: z(Math.min(...vs)), max: z(Math.max(...vs)), hours: vs.length };
}

/** check-values' nettie|<stat>|<BA>|<other>|<from>|<to>: on the snapshots it reads. Undefined when the key is not one,
 * the window is not held, or the tie holds no flow in it. */
export function nettieValue(check: string, snaps: Snapshot[]): number | undefined {
  const [head, stat, ba, other, from, to] = check.split("|");
  if (head !== "nettie" || !TIE_STATS.includes(stat as TieStat) || !ba || !other || !from || !to) return undefined;
  const w = windowOf(snaps, ba, from, to);
  if (!w) return undefined;
  const t = tieWeek(w.links, ba, other);
  return t ? t[stat as TieStat] : undefined;
}

/** The direction of a flow signed from the grid's side, in words. */
export function directionWords(mw: number): "sends to" | "takes from" | "none" {
  return mw > 0 ? "sends to" : mw < 0 ? "takes from" : "none";
}

export type ExchangeTie = { other: string; dir: "sends to" | "takes from" | "none"; mean: Fig | null; min: Fig | null; max: Fig | null; hours: Fig | null; tip: string };

/** The Exchange block's week for each neighbour of the hour shown (`others`, in the block's order): the four keyed
 * figures and the hover line of the hour's flow, which names the tie, the hour and the refresh, and gives the week's
 * mean, lowest and highest in words. The hour's age is not repeated here: the block says it once (net|lag). */
export function exchangeTies(snap: Snapshot, ba: string, hour: string, ties: { other: string; mw: number }[]): ExchangeTie[] {
  const from = snap.hours[0], to = snap.hours[snap.hours.length - 1];
  const w = windowOf([snap], ba, from, to);
  const span = `${hourName(from)} to ${hourName(to)}`;
  return ties.map((t) => {
    const week = w ? tieWeek(w.links, ba, t.other) : null;
    const f = (stat: TieStat, what: string): Fig | null => (week ? { check: `nettie|${stat}|${ba}|${t.other}|${from}|${to}`, raw: week[stat],
      tip: `eia930_all_interchange (the hourly network snapshot refreshed ${refreshName(snap.built)}), ${ba}'s tie with ${t.other}, ${what}, signed from ${ba}'s side, over the hours from ${span} that hold a flow` } : null);
    const mw = (v: number) => v.toLocaleString("en-US");
    const weekWords = week ? ` Over the week (${span}, ${mw(week.hours)} hours with a flow): mean ${mw(week.mean)} MW, lowest ${mw(week.min)} MW, highest ${mw(week.max)} MW.` : " The week holds no flow on this tie.";
    return { other: t.other, dir: directionWords(t.mw), mean: f("mean", "the mean flow, MW, rounded to whole MW"), min: f("min", "the lowest flow, MW"),
      max: f("max", "the highest flow, MW"), hours: f("hours", "the count of hours"),
      tip: `eia930_all_interchange (the hourly network snapshot refreshed ${refreshName(snap.built)}), ${ba}'s tie with ${t.other}, MW signed from ${ba}'s side, hour ${hourName(hour)}.${weekWords}` };
  });
}

// ---------------------------------------------------------------------------------------------------------------------
// Session 1406 (chain 100): the Lower 48 on the Network tab (grid_network_us48, components/grid/Lower48Demand.tsx). In
// the hour the panel shows, beside the seven grids' net exchange (lower48Panel above, unchanged): each grid's demand,
// chosen and keyed as the grid in view's demand is (demandAt: netsnap|... from the hourly snapshot's demand_recent, else
// series|eia930_all_demand|eia930:<BA>|demand_mw|<hour>); the Lower 48's own, EIA-930's US48
// (series|eia930_all_demand|eia930:US48|demand_mw|<hour>, the week's rows the page reads aligned as the seven's are); the
// seven's sum, calc|add|<D1>|...|<D7>, and its share of the Lower 48, calc|addpct|<D1>|...|<D7>|<US48> (two ops of calc,
// scripts/check-calc.mjs: the sum of the operands, and their sum over the last one, x 100), each only when all seven are
// held. And the seven's exchange with the grids around them, in words: the sum of the seven's net exports over their
// reporting ties (their ties with one another cancel in it), and its two parts, with the rest of the Lower 48 and with
// Canada's and Mexico's operators (OUTSIDE_US48, the snapshot's nodes that are not of the Lower 48). Each is written as a
// size with its direction in words, "sent out" or "took in", so each is keyed by the operands that give that size: the
// seven's net|export|<BA>|<hour> keys (or net|import|...), and each tie to Canada or Mexico signed from the side that
// makes the part, net|tie|<outside>|<BA>|<hour> or net|tie|<BA>|<outside>|<hour> (lib/network.ts netValue reads a tie
// from either side); one operand is its own key. No new key kind: check-values recomputes every operand as it does.

/** The balancing authorities of the network snapshot that are not of the Lower 48: Canada's and Mexico's operators. */
export const OUTSIDE_US48 = ["AESO", "BCHA", "CEN", "HQT", "IESO", "MHEB", "NBSO", "SPC"] as const;
const outside = (ba: string) => (OUTSIDE_US48 as readonly string[]).includes(ba);

/** The Lower 48's own demand in the hour (EIA-930's US48): the week's eia930_all_demand rows, aligned to the snapshot's
 * hours; null where the hour is not held. The snapshot has no US48 node, so there is no fallback. */
export function lower48DemandAt(snap: Snapshot, hour: string, week: (number | null)[] | undefined): Fig | null {
  const h = snap.hours.indexOf(hour);
  const v = h >= 0 ? week?.[h] : null;
  return v === null || v === undefined ? null
    : { check: `series|eia930_all_demand|eia930:US48|demand_mw|${hour}`, raw: v, tip: `eia930_all_demand, entity eia930:US48 (EIA-930's Lower 48), demand_mw, hour ${hourName(hour)}, read with the snapshot refreshed ${refreshName(snap.built)}` };
}

/** A figure that adds its operands' figures (calc|add, or the one operand itself), and its tip. */
function added(figs: { check: string; raw: number }[], tip: string): Fig {
  if (figs.length === 1) return { check: figs[0].check, raw: figs[0].raw, tip };
  return { check: `calc|add|${figs.map((f) => f.check.replaceAll("|", "~")).join("|")}`, raw: z(figs.reduce((a, f) => a + f.raw, 0)), tip };
}

export type Flow = Fig & { kind: "export" | "import" };
export type Lower48Demand = {
  hour: string;
  rows: { ba: string; demand: Fig | null }[];
  us48: Fig | null;
  /** the seven's demand summed, and as a percent of the Lower 48's: only when all seven are held */
  sum: Fig | null; share: Fig | null;
  /** the grids of the seven with a tie reporting in the hour, the sums are over them */
  reporting: string[];
  /** the seven's net exchange with every grid around them, and its two parts; null when no grid reports a tie (or, for
   *  `abroad`, no tie to Canada or Mexico reports) */
  total: Flow | null; rest: Flow | null; abroad: Flow | null;
};

/** The Lower 48's Network panel's demand and exchange in the hour (`demand`: the week's demand by BA, the page's
 * live.demand, the seven and US48). */
export function lower48Demand(snap: Snapshot, bas: string[], hour: string, demand: Record<string, (number | null)[] | undefined>): Lower48Demand {
  const rows = bas.map((ba) => ({ ba, demand: demandAt(snap, ba, hour, demand[ba]) }));
  const us48 = lower48DemandAt(snap, hour, demand.US48);
  const held = rows.every((r) => r.demand) ? rows.map((r) => r.demand!) : null;
  const ks = held ? held.map((f) => f.check.replaceAll("|", "~")) : [];
  const sumRaw = held ? z(held.reduce((a, f) => a + f.raw, 0)) : 0;
  const sum = held ? { check: `calc|add|${ks.join("|")}`, raw: sumRaw, tip: `The seven grids' demand in the hour, each beside it, summed, hour ${hourName(hour)}` } : null;
  const share = held && us48 && us48.raw > 0
    ? { check: `calc|addpct|${ks.join("|")}|${us48.check.replaceAll("|", "~")}`, raw: (sumRaw / us48.raw) * 100, tip: `The seven grids' demand summed over the Lower 48's (EIA-930's US48), both beside it, hour ${hourName(hour)}` }
    : null;

  const src = (what: string) => `eia930_all_interchange (the hourly network snapshot), ${what}, hour ${hourName(hour)}, refreshed ${refreshName(snap.built)}`;
  const grids = bas.map((ba) => ({ ba, ties: tiesOf(snap, ba, hour) })).filter((g) => g.ties.length);
  const nets = grids.map((g) => ({ ba: g.ba, mw: z(g.ties.reduce((a, t) => a + t.mw, 0)) }));
  const abroadTies = grids.flatMap((g) => g.ties.filter((t) => outside(t.other)).map((t) => ({ ba: g.ba, other: t.other, mw: t.mw })));
  const exp = (n: { ba: string; mw: number }) => ({ check: `net|export|${n.ba}|${hour}`, raw: n.mw });
  const imp = (n: { ba: string; mw: number }) => ({ check: `net|import|${n.ba}|${hour}`, raw: z(-n.mw) });
  const out = (t: { ba: string; other: string; mw: number }) => ({ check: `net|tie|${t.ba}|${t.other}|${hour}`, raw: t.mw });
  const back = (t: { ba: string; other: string; mw: number }) => ({ check: `net|tie|${t.other}|${t.ba}|${hour}`, raw: z(-t.mw) });
  const flow = (sent: { check: string; raw: number }[], taken: { check: string; raw: number }[], what: string): Flow | null => {
    if (!sent.length) return null;
    const s = added(sent, "");
    const sending = s.raw >= 0;
    const f = sending ? s : added(taken, "");
    return { ...f, kind: sending ? "export" : "import", tip: src(`${what}, ${sending ? "net export" : "net import"} MW`) };
  };
  const names = nets.map((n) => n.ba).join(", ");
  const total = flow(nets.map(exp), nets.map(imp), `the net exports of ${names} summed (their ties with one another cancel)`);
  const rest = nets.length
    ? flow([...nets.map(exp), ...abroadTies.map(back)], [...nets.map(imp), ...abroadTies.map(out)],
      `the net exports of ${names} summed, less their ties to Canada's and Mexico's operators (${abroadTies.map((t) => `${t.ba} with ${t.other}`).join(", ") || "none reporting"}): their exchange with the rest of the Lower 48`)
    : null;
  const abroad = flow(abroadTies.map(out), abroadTies.map(back), `the ties of ${names} to Canada's and Mexico's operators (${abroadTies.map((t) => `${t.ba} with ${t.other}`).join(", ")}) summed, signed from the seven's side`);
  return { hour, rows, us48, sum, share, reporting: nets.map((n) => n.ba), total, rest, abroad };
}
