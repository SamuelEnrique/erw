// Energy Research Warehouse (ERW) site, session 700: "Where can a large load go", the All grids tab of /cost-of-power
// (chain 050 of 23 October 2026, docs/methods/siting.md).
//
// The tab answers, for every grid, hub and zone the warehouse holds a price for, and for every ERCOT node of
// node_basis_daily, the questions "Your load" answers for one region: what a load pays, when it connects, how clean the
// power is. It is the same page and the same model: a row's energy is lib/datacenter.ts's arithmetic over the same files
// (data/datacenter), never a second one. This file holds what is pure: the four load profiles, the eight columns with
// their tips, the row sets, the inputs in the address, and the figure a check key names (scripts/check-values.mjs
// recomputes every key of the tab here). No imports but types: Node runs it as it is (tests/test_session700.py).
import type * as Datacenter from "./datacenter";
import type { Index, Month, YearFile } from "./datacenter";

// ---------------------------------------------------------------------------------------------------------------------
// the profiles: a profile sets three inputs (load factor, curtailment rule, interruptible) and nothing else
// ---------------------------------------------------------------------------------------------------------------------

export type ProfileId = "datacenter" | "flexible" | "electrolyzer" | "industry";
/** none: runs every hour. peaks_strike: off in ERCOT's four summer peak intervals and in hours at or above the strike.
 * below_strike: runs only in hours below the strike. interruptible: runs every hour the grid does not interrupt. */
export type Curtail = "none" | "peaks_strike" | "below_strike" | "interruptible";
export type Profile = {
  id: ProfileId; label: string; lf: number; lfRange: [number, number]; curtail: Curtail; strike: number | null; interruptible: boolean;
  /** each default's source, for its grey hover tip */
  source: { lf: string; curtail: string; strike?: string; interruptible: string };
};
const PROMPT = "the owner's chain prompt of 22 October 2026 (queue/done/050-night-23-october-code-allgrids.md)";
/** The page's scarcity level (lib/datacenter/answers.ts, SCARCITY_USD), the strike of a flexible load by default. */
export const SCARCITY_STRIKE = 1000;
export const PROFILES: Record<ProfileId, Profile> = {
  datacenter: {
    id: "datacenter", label: "Datacenter", lf: 0.9, lfRange: [0.9, 0.9], curtail: "none", strike: null, interruptible: false,
    source: { lf: `0.90, flat in every hour: ${PROMPT}`, curtail: `Never curtails: ${PROMPT}`, interruptible: `Firm service, not interruptible: ${PROMPT}` },
  },
  flexible: {
    id: "flexible", label: "Flexible compute", lf: 0.9, lfRange: [0.9, 0.9], curtail: "peaks_strike", strike: SCARCITY_STRIKE, interruptible: false,
    source: {
      lf: `0.90 while running, as the datacenter: ${PROMPT}`, curtail: `Off in ERCOT's four summer peak intervals and in hours at or above the strike: ${PROMPT}`,
      strike: "USD 1,000 per MWh: the scarcity level \"What a datacenter pays\" counts short hours at, for every grid (lib/datacenter/answers.ts, SCARCITY_USD)",
      interruptible: `Not interruptible: it chooses its own hours (${PROMPT})`,
    },
  },
  electrolyzer: {
    id: "electrolyzer", label: "Electrolyzer", lf: 0.55, lfRange: [0.4, 0.7], curtail: "below_strike", strike: null, interruptible: false,
    source: {
      lf: `0.55, the middle of the owner's range of 0.40 to 0.70: ${PROMPT}`, curtail: `Runs only in hours below a strike: ${PROMPT}`,
      strike: "By default the strike is each row's own price at the load factor: the load runs in the cheapest 55 percent of the row's hours",
      interruptible: `Not interruptible: it chooses its own hours (${PROMPT})`,
    },
  },
  industry: {
    id: "industry", label: "Heavy industry", lf: 0.8, lfRange: [0.8, 0.8], curtail: "interruptible", strike: null, interruptible: true,
    source: { lf: `0.80: ${PROMPT}`, curtail: `Off only when the grid interrupts it: ${PROMPT}`, interruptible: `Interruptible service: ${PROMPT}` },
  },
};
export const PROFILE_ORDER: ProfileId[] = ["datacenter", "flexible", "electrolyzer", "industry"];
export const CURTAIL_WORDS: Record<Curtail, string> = {
  none: "never curtails",
  peaks_strike: "off in ERCOT's four summer peaks and at or above the strike",
  below_strike: "runs only below the strike",
  interruptible: "off only when the grid interrupts it",
};

// ---------------------------------------------------------------------------------------------------------------------
// the columns
// ---------------------------------------------------------------------------------------------------------------------

export type ColumnId = "energy" | "transmission" | "capacity" | "connect" | "headroom" | "carbon" | "utility" | "allin";
export type Column = { id: ColumnId; head: string; unit: string; tip: string; tables: string[] };
/** The eight columns, in the order the table draws them. `tip` is the head's hover: its source and method in a line. */
export const COLUMNS: Column[] = [
  { id: "energy", head: "Energy", unit: "USD per MWh", tables: ["iso_dam_hub_prices", "iso_rtm_hub_prices", "iso_hub_prices_history", "ercot_all_hub_prices_history", "ercot_zone_prices_history", "node_basis_daily"],
    tip: "The day-ahead price over the last twelve whole months, a flat load, from the page's own hourly files (lib/datacenter.ts, as \"Your load\" computes it); an ERCOT node is its hub plus its mean daily basis (node_basis_daily)." },
  { id: "transmission", head: "Transmission and 4CP", unit: "USD per MWh", tables: ["ercot_4cp_intervals", "texas_transmission_matrix"],
    tip: "ERCOT: the load's demand in the four summer peak intervals of the newest summer held (ercot_4cp_intervals) at the Commission's approved rate, over its energy: the profile's own, then firm (on in all four) and off (curtailing). Elsewhere the utility's large-load tariff, not held." },
  { id: "capacity", head: "Capacity", unit: "USD per MWh", tables: ["iso_all_capacity_prices", "pjm_rpm_capacity_prices"],
    tip: "The latest cleared capacity price for the zone, over the load's energy (iso_all_capacity_prices, pjm_rpm_capacity_prices). ERCOT, CAISO and SPP have no capacity market." },
  { id: "connect", head: "Time to connect", unit: "months", tables: ["lbnl_interconnection_queue", "iso_queue_statistics", "large_load_rules", "large_load_waits", "ercot_large_load_status", "nyiso_load_queue"],
    tip: "The median months from queue entry to operation for projects finished in the last three years (lbnl_interconnection_queue), and the grid's large-load rule (large_load_rules)." },
  { id: "headroom", head: "Headroom", unit: "percent; MW", tables: ["eia930_demand_growth", "eia860m_planned_generators", "eia_state_capacity_annual"],
    tip: "Demand growth over the last twelve months (EIA-930), and generation planned in the next twelve months with an interconnection agreement (eia860m_planned_generators)." },
  { id: "carbon", head: "Carbon", unit: "kg CO2 per MWh", tables: ["egrid_power_plants", "carbon_intensity_hourly"],
    tip: "The generation-weighted CO2 rate of the row's eGRID subregion (egrid_power_plants); hourly where the profile runs in some hours and the grid's hourly intensity is held." },
  { id: "utility", head: "Utility", unit: "USD per MWh", tables: ["eia861_utility_sales"],
    tip: "The largest utility by industrial sales in the row's state, its industrial revenue per MWh and its sales growth (eia861_utility_sales). Service territories are not held." },
  { id: "allin", head: "All-in", unit: "USD per MWh", tables: [],
    tip: "Energy, transmission and capacity added, drawn only where each of the three is held or is zero by market design." },
];

// ---------------------------------------------------------------------------------------------------------------------
// the rows
// ---------------------------------------------------------------------------------------------------------------------

export const GRID_ORDER = ["ercot", "caiso", "nyiso", "isone", "spp", "miso", "pjm"] as const;
export const GRID_NAMES: Record<string, string> = { ercot: "ERCOT", caiso: "CAISO", nyiso: "NYISO", isone: "ISO-NE", spp: "SPP", miso: "MISO", pjm: "PJM" };
export type RowKind = "zone" | "hub" | "grid" | "node";
export type Row = {
  id: string; grid: string; region: string; label: string; kind: RowKind;
  /** a row whose prices the page's files do not hold: the words the existing tab shows for its grid, and why */
  blank?: { words: string; why: string };
};
/** A node of node_basis_daily, as data/siting/nodes.json holds it (warehouse/derived/siting_page.py). */
/** `dam_basis`: the node's day-ahead basis to HB_HUBAVG by Central month, [mean of the daily basis, days held] (session 701). */
export type NodeRow = { id: string; cls: string; types: string; dam_basis?: Record<string, [number, number]> };
export type NodeFile = { table: string; built: string; first: string; last: string; points: number; hubs: number; zones: number; nodes: NodeRow[] };

/** A region's kind as the index says it; a region of a grid whose index names no kind is a hub when its name says so. */
function kindOf(grid: string, id: string, kind: string | null | undefined): RowKind {
  if (kind === "zone" || kind === "hub") return kind;
  if (grid === "isone") return id.startsWith(".Z.") ? "zone" : "hub";
  if (grid === "nyiso") return "zone";
  return "hub";
}
const KIND_WORDS: Record<RowKind, string> = { zone: "load zone", hub: "hub", grid: "the grid", node: "node" };

/** The hub and zone rows: every region of the page's index; each region of a
 * grid the page names but does not price (MISO's hubs, paused), with the page's own words; then a grid with no region
 * held (PJM) as one row of its own, so that the columns a grid holds without a price (queues, carbon) have a row. In the
 * tab's default order, alphabetical by grid and then by name. */
export function hubRows(index: Pick<Index, "grids" | "blank">): Row[] {
  const out: Row[] = [];
  for (const grid of GRID_ORDER) {
    const g = index.grids[grid];
    if (g) {
      for (const r of g.regions) {
        const kind = kindOf(grid, r.id, r.kind);
        out.push({ id: `${grid}:${r.id}`, grid, region: r.id, kind, label: `${r.id}${r.name ? `, ${r.name}` : ""} (${KIND_WORDS[kind]})` });
      }
      continue;
    }
    const b = index.blank[grid];
    if (!b) continue;
    const why = grid === "miso"
      ? "MISO is paused while its terms are reviewed (docs/methods/miso_pause.md): its prices are held in the warehouse and not drawn here."
      : `No ${b.name} hub or zone price is held: ${b.words}.`;
    if (b.regions.length) for (const id of b.regions) out.push({ id: `${grid}:${id}`, grid, region: id, kind: "hub", label: `${id} (hub)`, blank: { words: b.words, why } });
    else out.push({ id: `${grid}:grid`, grid, region: "", kind: "grid", label: `${b.name}, the grid (no hub or zone price held)`, blank: { words: b.words, why } });
  }
  return out.sort(byGridThenName);
}
/** The tab's default order: alphabetical by the grid's name, then by the row's name. */
export const byGridThenName = (a: Row, b: Row) => GRID_NAMES[a.grid].localeCompare(GRID_NAMES[b.grid]) || a.region.localeCompare(b.region);
/** The node rows: every settlement point of node_basis_daily that is neither a hub nor a load zone, in name order. */
export function nodeRows(file: Pick<NodeFile, "nodes">): Row[] {
  return [...file.nodes].sort((a, b) => a.id.localeCompare(b.id)).map((n) => ({ id: `ercot:${n.id}`, grid: "ercot", region: n.id, kind: "node" as const, label: `${n.id} (node, ${n.cls})` }));
}

// ---------------------------------------------------------------------------------------------------------------------
// the inputs, in the address
// ---------------------------------------------------------------------------------------------------------------------

export type RowSet = "hubs" | "nodes";
/** `strike` (session 702): USD per MWh, for a profile whose rule has one; null is the profile's default (for the
 * electrolyzer, each row's own price at the load factor). */
export type SitingInputs = { profile: ProfileId; mw: number; lf: number; rows: RowSet; strike: number | null };
export const SITING_LIMITS = { mw: [1, 10000] as [number, number], lf: [0.05, 1] as [number, number], strike: [-500, 10000] as [number, number] };
/** Whether a profile's rule has a strike. */
export const hasStrike = (p: ProfileId) => PROFILES[p].curtail === "peaks_strike" || PROFILES[p].curtail === "below_strike";
export const SITING_DEFAULTS = { profile: "datacenter" as ProfileId, mw: 100, rows: "hubs" as RowSet };
const clampTo = (v: number, [lo, hi]: [number, number]) => Math.min(hi, Math.max(lo, v));
/** The tab's inputs from its address; a value it cannot read is the default, a number outside its bounds the nearest. */
export function sitingInputs(q: Record<string, string | undefined>): SitingInputs {
  const profile = (PROFILE_ORDER as string[]).includes(q.profile ?? "") ? (q.profile as ProfileId) : SITING_DEFAULTS.profile;
  const p = PROFILES[profile];
  const num = (s: string | undefined, d: number, lim: [number, number]) => { const v = s === undefined || s === "" ? NaN : Number(s); return Number.isFinite(v) ? clampTo(v, lim) : d; };
  const st = q.strike === undefined || q.strike === "" ? NaN : Number(q.strike);
  const strike = hasStrike(profile) && Number.isFinite(st) ? clampTo(st, SITING_LIMITS.strike) : p.strike;
  return { profile, mw: num(q.mw, SITING_DEFAULTS.mw, SITING_LIMITS.mw), lf: num(q.lf, p.lf, p.lfRange), rows: q.rows === "nodes" ? "nodes" : "hubs", strike };
}
/** The tab's address for its inputs, with a change; a value at its default is left out. */
export function sitingHref(x: SitingInputs, change: Partial<SitingInputs> = {}): string {
  const y = { ...x, ...change };
  if (change.profile && change.profile !== x.profile && change.lf === undefined) y.lf = PROFILES[change.profile].lf;
  if (change.profile && change.profile !== x.profile && change.strike === undefined) y.strike = PROFILES[change.profile].strike;
  const q = new URLSearchParams({ view: "allgrids" });
  if (y.profile !== SITING_DEFAULTS.profile) q.set("profile", y.profile);
  if (y.mw !== SITING_DEFAULTS.mw) q.set("mw", String(y.mw));
  if (y.lf !== PROFILES[y.profile].lf) q.set("lf", String(y.lf));
  if (y.rows !== SITING_DEFAULTS.rows) q.set("rows", y.rows);
  if (hasStrike(y.profile) && y.strike !== null && y.strike !== PROFILES[y.profile].strike) q.set("strike", String(y.strike));
  return `/cost-of-power?${q.toString()}`;
}

// ---------------------------------------------------------------------------------------------------------------------
// energy (session 701): the day-ahead price over the last twelve whole months, a flat load, real time beside it
// ---------------------------------------------------------------------------------------------------------------------

/** The functions of lib/datacenter.ts the tab computes with, handed in by the caller (the page imports them through
 * "@/lib/datacenter", the scripts through "../lib/datacenter.ts"), so this file stays free of imports and the arithmetic
 * is that file's own: one function for both views. */
export type DC = Pick<typeof Datacenter, "monthsRuled" | "lastTwelve" | "span" | "years" | "expand" | "monthsOfYear" | "monthStarts">;
export const FLAT_RUN = { run: "flat" as const, n: 0, pct: 0, shift: 0 };
/** Twelve months of a flat load at one region and market: the price per MWh (lib/datacenter.ts span().flat over
 * lastTwelve()), the months, each month's price, the hours held, and the newest complete calendar year in the market. */
export type Twelve = { per: number; from: string; to: string; months: { m: string; per: number }[]; hours: number; year: { y: string; per: number } | null };
export function flatTwelve(dc: DC, files: YearFile[], region: string, buy: "da" | "rt"): Twelve | null {
  const ms: Month[] = dc.monthsRuled(files, region, buy, FLAT_RUN, "forecast").months;
  const l12 = dc.lastTwelve(ms);
  if (!l12) return null;
  const s = dc.span(l12);
  if (s.flat === null) return null;
  const ys = dc.years(ms).filter((y) => y.complete && y.flat !== null);
  const y = ys.at(-1);
  return { per: s.flat, from: l12[0].m, to: l12[11].m, months: l12.map((r) => ({ m: r.m, per: r.flat / r.held })), hours: s.held, year: y ? { y: y.y, per: y.flat as number } : null };
}
/** A node's basis to its hub over the hub's twelve months: the mean of its daily day-ahead basis, the days held and the
 * days in the months. Drawn only when the days held are at least NODE_NEAR of the days due. */
export const NODE_NEAR = 0.9;
export const NODE_HUB = "HB_HUBAVG";
export type NodeEnergy = { hub: Twelve; basis: number; days: number; due: number; per: number };
const daysIn = (m: string) => new Date(Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)), 0)).getUTCDate();
export function nodeEnergy(hub: Twelve | null, node: Pick<NodeRow, "dam_basis">): NodeEnergy | { why: string } {
  if (!hub) return { why: `Twelve whole months of day-ahead prices are not held for ${NODE_HUB}.` };
  let sum = 0, days = 0, due = 0;
  for (const { m } of hub.months) {
    due += daysIn(m);
    const b = node.dam_basis?.[m];
    if (b) { sum += b[0] * b[1]; days += b[1]; }
  }
  if (days < NODE_NEAR * due) return { why: `node_basis_daily holds ${days} of the ${due} days from ${hub.from} to ${hub.to} for this node, fewer than ${Math.round(NODE_NEAR * 100)} percent: no twelve-month figure.` };
  const basis = sum / days;
  return { hub, basis, days, due, per: hub.per + basis };
}
/** What the energy cell holds for a row: the day-ahead and real-time figures, or the words and why when none. */
export type EnergyCell = { da: Twelve | null; rt: Twelve | null; node?: NodeEnergy; words?: string; why?: string };
const memo = new WeakMap<Files, Map<string, Twelve | null>>();
/** flatTwelve once a files object, grid, region and market: the node rows share their hub's. */
export function twelveOf(dc: DC, f: Files, grid: string, region: string, buy: "da" | "rt"): Twelve | null {
  let m = memo.get(f);
  if (!m) { m = new Map(); memo.set(f, m); }
  const k = `${grid}|${region}|${buy}`;
  if (!m.has(k)) m.set(k, flatTwelve(dc, f.years(grid), region, buy));
  return m.get(k) ?? null;
}
export function energyCell(dc: DC, f: Files, r: Row): EnergyCell {
  if (r.blank) return { da: null, rt: null, words: r.grid === "pjm" ? "license needed" : r.grid === "miso" ? "paused" : r.blank.words, why: r.blank.why };
  if (r.kind === "node") {
    const hub = twelveOf(dc, f, "ercot", NODE_HUB, "da");
    const n = f.nodes.nodes.find((x) => x.id === r.region);
    const e = nodeEnergy(hub, n ?? {});
    return "why" in e ? { da: null, rt: null, words: "not held", why: e.why } : { da: null, rt: null, node: e };
  }
  const da = twelveOf(dc, f, r.grid, r.region, "da"), rt = twelveOf(dc, f, r.grid, r.region, "rt");
  if (!da && !rt) return { da, rt, words: "not held", why: `Twelve whole months in a row are not held for ${r.region} in either market.` };
  return { da, rt };
}

// ---------------------------------------------------------------------------------------------------------------------
// the profiles' energy (session 702): the time-weighted day-ahead price over the hours the load runs
// ---------------------------------------------------------------------------------------------------------------------

/** ERCOT's four coincident-peak intervals by summer (data/siting/ercot_4cp.json, from ercot_4cp_intervals). */
export type CpFile = { table: string; built: string; note: string; summers: { year: number; intervals: { ts: string; local: string; mw: number }[] }[] };
/** A profile's twelve months at one region, day-ahead, over the flat load's own twelve whole months: the price per MWh
 * over the hours the load runs, the hours it ran and was off, the strike it used, and the peak hours in the window. */
export type ProfileTwelve = { per: number; from: string; to: string; run: number; lost: number; held: number; strike: number | null; peaks: number; atOrBelow: boolean };
/** The year file and hour (in the grid's standard time) that hold an instant: the steps of app/cost-of-power/model.ts's
 * four-peak block (session 354), so an interval falls in the same hour on both views. */
export function hourOf(ts: string, behind: number): { y: number; i: number } {
  const t = Date.parse(ts) - behind * 3_600_000, y = new Date(t).getUTCFullYear();
  return { y, i: Math.floor((t - Date.UTC(y, 0, 1)) / 3_600_000) };
}
/** ERCOT's four-peak intervals as hours of the year files, by year. */
export function peakHours(cp: CpFile | undefined, behind: number): Map<number, Set<number>> {
  const peaks = new Map<number, Set<number>>();
  for (const sm of cp?.summers ?? []) for (const iv of sm.intervals) {
    const { y, i } = hourOf(iv.ts, behind);
    if (!peaks.has(y)) peaks.set(y, new Set());
    peaks.get(y)!.add(i);
  }
  return peaks;
}
/** The load in one hour under a profile's rule: 1 runs, 0 off (session 702; shared by the energy and the four peaks). */
export function ruleWeight(curtail: Curtail, v: number | null, peak: boolean, strike: number | null, atOrBelow: boolean): number {
  if (v === null) return 0;
  if (curtail === "peaks_strike") return peak || (strike !== null && v >= strike) ? 0 : 1;
  if (curtail === "below_strike") return strike === null ? 1 : (atOrBelow ? v <= strike : v < strike) ? 1 : 0;
  return 1;
}
/** The k-th cheapest of a list of prices (1 = the cheapest). */
const kth = (v: number[], k: number) => [...v].sort((a, b) => a - b)[Math.min(v.length, Math.max(1, k)) - 1];
/** A profile's twelve months under its rule. The load in each hour is 1 (runs) or 0 (off):
 *   none, interruptible  every hour held (no table holds a grid's interruptions of a heavy load: it runs every hour);
 *   peaks_strike         off in an hour whose day-ahead price is at or above the strike, or that holds one of ERCOT's
 *                        four summer peak intervals (ERCOT rows; ercot_4cp_intervals);
 *   below_strike         runs in an hour whose price is below the strike; with no strike given, the strike is the row's
 *                        own k-th cheapest price of the window, k the load factor's share of its hours, and the load
 *                        runs at or below it (the cheapest share of the hours).
 * The load factor scales the energy and the cost alike, so the price per MWh is the load-weighted price of the hours it
 * runs. Each month is lib/datacenter.ts's monthsOfYear, over the flat load's own twelve whole months. */
const pmemo = new WeakMap<Files, Map<string, ProfileTwelve | null>>();
export function profileTwelve(dc: DC, f: Files, grid: string, region: string, x: Pick<SitingInputs, "profile" | "lf" | "strike">, cp?: CpFile): ProfileTwelve | null {
  let m = pmemo.get(f);
  if (!m) { m = new Map(); pmemo.set(f, m); }
  const k = `${grid}|${region}|${profileKey(x)}|${cp ? "cp" : ""}`;
  if (!m.has(k)) m.set(k, profileTwelveOnce(dc, f, grid, region, x, cp));
  return m.get(k) ?? null;
}
function profileTwelveOnce(dc: DC, f: Files, grid: string, region: string, x: Pick<SitingInputs, "profile" | "lf" | "strike">, cp?: CpFile): ProfileTwelve | null {
  const flat = twelveOf(dc, f, grid, region, "da");
  if (!flat) return null;
  const p = PROFILES[x.profile];
  const behind = f.index.grids[grid]?.std_hours_behind_utc ?? 0;
  const y0 = Number(flat.from.slice(0, 4)), y1 = Number(flat.to.slice(0, 4));
  const files = f.years(grid).filter((yf) => yf.year >= y0 && yf.year <= y1).sort((a, b) => a.year - b.year);
  const years = files.map((yf) => {
    const pr = dc.expand(yf, region, "da"), st = dc.monthStarts(yf.year);
    const win: boolean[] = pr.map(() => false);
    for (let m = 0; m < 12; m++) {
      const lab = `${yf.year}-${String(m + 1).padStart(2, "0")}`;
      if (lab < flat.from || lab > flat.to) continue;
      for (let i = st[m]; i < st[m + 1]; i++) win[i] = pr[i] !== null;
    }
    return { yf, pr, win };
  });
  const prices: number[] = [];
  for (const y of years) y.pr.forEach((v, i) => { if (y.win[i]) prices.push(v as number); });
  let strike = x.strike, atOrBelow = false;
  if (p.curtail === "below_strike" && strike === null) { strike = kth(prices, Math.round(x.lf * prices.length)); atOrBelow = true; }
  // the peak hours: ERCOT's four intervals of each summer held, as hours of the year files
  const peaks = p.curtail === "peaks_strike" && grid === "ercot" ? peakHours(cp, behind) : new Map<number, Set<number>>();
  let run = 0, lost = 0, held = 0, inPeaks = 0, cost = 0;
  for (const y of years) {
    const w = y.pr.map((v, i) => {
      const pk = peaks.get(y.yf.year)?.has(i) ?? false;
      if (v !== null && pk && y.win[i]) inPeaks++;
      return ruleWeight(p.curtail, v, pk, strike, atOrBelow);
    });
    for (const r of dc.monthsOfYear(y.yf.year, y.pr, w)) {
      if (r.m < flat.from || r.m > flat.to) continue;
      held += r.held; lost += r.down; run += r.energy; cost += r.cost;
    }
  }
  return { per: run > 0 ? cost / run : NaN, from: flat.from, to: flat.to, run, lost, held, strike, peaks: inPeaks, atOrBelow };
}
/** The profile's figure for a row: a hub or zone's own; a node's is its hub's (HB_HUBAVG) plus its mean daily basis, the
 * same basis as the flat figure (node_basis_daily is daily: no hour of a node is held for twelve months). */
export type ProfileCell = { t: ProfileTwelve; per: number; basis?: number; daily: boolean } | { why: string };
export function profileCell(dc: DC, f: Files, r: Row, x: Pick<SitingInputs, "profile" | "lf" | "strike">, cp?: CpFile): ProfileCell {
  if (r.blank) return { why: r.blank.why };
  const never = "The load does not run in any hour of the window at this strike.";
  if (r.kind === "node") {
    const e = energyCell(dc, f, r);
    if (!e.node) return { why: e.why ?? "not held" };
    const t = profileTwelve(dc, f, "ercot", NODE_HUB, x, cp);
    if (!t) return { why: `Twelve whole months of day-ahead prices are not held for ${NODE_HUB}.` };
    if (!Number.isFinite(t.per)) return { why: never };
    return { t, per: t.per + e.node.basis, basis: e.node.basis, daily: true };
  }
  const t = profileTwelve(dc, f, r.grid, r.region, x, cp);
  if (!t) return { why: `Twelve whole months of day-ahead prices in a row are not held for ${r.region}.` };
  if (!Number.isFinite(t.per)) return { why: never };
  return { t, per: t.per, daily: false };
}
/** The inputs a profile's figure depends on, as they stand in its check key. */
export const profileKey = (x: Pick<SitingInputs, "profile" | "lf" | "strike">) => `profile=${x.profile}&lf=${x.lf}&strike=${x.strike ?? "row"}`;
export function profileOfKey(s: string): Pick<SitingInputs, "profile" | "lf" | "strike"> | null {
  const q = Object.fromEntries(new URLSearchParams(s));
  if (!(PROFILE_ORDER as string[]).includes(q.profile)) return null;
  const lf = Number(q.lf), strike = q.strike === "row" ? null : Number(q.strike);
  return Number.isFinite(lf) && (strike === null || Number.isFinite(strike)) ? { profile: q.profile as ProfileId, lf, strike } : null;
}

// ---------------------------------------------------------------------------------------------------------------------
// transmission and the four peaks (session 703): ERCOT's four-peak charge for the load; elsewhere not held
// ---------------------------------------------------------------------------------------------------------------------

/** The Commission's wholesale transmission rate (the postage stamp rate), USD per kW of four-peak demand a year. */
export type Rate = { year: string; value: number };
/** The newest approved rate of the matrix rows (matrix A where a year has two), as "Your load"'s four-peak block takes it
 * (app/cost-of-power/model.ts): texas_transmission_matrix, through data/datacenter/texas_delivery.json. */
export function newestRate(rows: { quantity: string; status: string; matrix: string; year: string; value: number }[]): Rate | null {
  const r = rows.filter((x) => x.quantity === "postage_stamp_rate" && x.status === "approved" && x.matrix !== "B").sort((a, b) => a.year.localeCompare(b.year)).at(-1);
  return r ? { year: r.year, value: r.value } : null;
}
/** A row's four-peak charge, USD per MWh of the load's energy: the rate times the load's demand in the four intervals of
 * the newest summer held, over the energy it uses in a year. A load's demand in an interval is its draw while running
 * times the share of the interval's hour it runs, and its energy is its draw times the hours it runs, so the draw cancels:
 * USD per MWh = rate x 1,000 x share / hours run a year.
 *   firm        the load's full share: it runs in all four intervals (share 1);
 *   curtailing  a load off for those intervals: the weights of the four intervals' hours under the rule "off at the four
 *               peaks" (ruleWeight), computed, not assumed;
 *   own         the profile's own weights in those hours (its rule and strike, the strike of the window's twelve months).
 * Hours run a year: the profile's hours over its twelve months (ProfileTwelve.run). A node is charged as its hub's hours
 * (HB_HUBAVG; node_basis_daily is daily). */
export type CpCharge = { year: number; rate: Rate; hours: number; share: number | null; firm: number; curtailing: number | null; own: number | null;
  intervals: { ts: string; local: string; w: number | null }[]; region: string };
export function cpCharge(dc: DC, f: Files, r: Row, x: Pick<SitingInputs, "profile" | "lf" | "strike">): CpCharge | { why: string; words: string } {
  if (r.blank) return { why: r.blank.why, words: r.grid === "miso" ? "paused" : "not held" };
  if (r.grid !== "ercot") return { why: `The transmission and delivery charge a large load pays in ${GRID_NAMES[r.grid]} is set by its utility's large-load tariff, and no such tariff is held in the warehouse. Only ERCOT's four-peak charge is held (ercot_4cp_intervals, at the Commission's rate).`, words: "not held" };
  const rate = f.rate;
  if (!rate) return { why: "The Commission's approved postage stamp rate is not in the page's files (texas_transmission_matrix).", words: "not held" };
  const summer = [...(f.cp?.summers ?? [])].filter((s) => s.intervals.length === 4).at(-1);
  if (!summer) return { why: "ercot_4cp_intervals holds no whole summer.", words: "not held" };
  const region = r.kind === "node" ? NODE_HUB : r.region;
  if (r.kind === "node" && !energyCell(dc, f, r).node) return { why: energyCell(dc, f, r).why ?? "not held", words: "not held" };
  const t = profileTwelve(dc, f, "ercot", region, x, f.cp);
  if (!t || t.run <= 0) return { why: `Twelve whole months of day-ahead prices in a row are not held for ${region}, or the load never runs.`, words: "not held" };
  const behind = f.index.grids.ercot?.std_hours_behind_utc ?? 6;
  const p = PROFILES[x.profile];
  const files = new Map(f.years("ercot").map((yf) => [yf.year, yf]));
  const at = (ts: string, curtail: Curtail): number | null => {
    const { y, i } = hourOf(ts, behind), yf = files.get(y);
    if (!yf) return null;
    const v = dc.expand(yf, region, "da")[i];
    if (v === null || v === undefined) return null;
    return ruleWeight(curtail, v, true, curtail === p.curtail ? t.strike : null, t.atOrBelow);
  };
  const own = summer.intervals.map((iv) => at(iv.ts, p.curtail));
  const off = summer.intervals.map((iv) => at(iv.ts, "peaks_strike"));
  const mean = (ws: (number | null)[]) => (ws.every((w) => w !== null) ? (ws as number[]).reduce((a, w) => a + w, 0) / ws.length : null);
  const hours = (t.run * 8760) / t.held;  // hours run in a year of 8,760 hours held
  const per = (share: number | null) => (share === null ? null : (rate.value * 1000 * share) / hours);
  const share = mean(own);
  return { year: summer.year, rate, hours, share, firm: per(1) as number, curtailing: per(mean(off)), own: per(share),
    intervals: summer.intervals.map((iv, k) => ({ ts: iv.ts, local: iv.local, w: own[k] })), region };
}
/** The grids with no capacity market: their capacity part is zero by market design, with why (session 703). */
export const NO_CAPACITY_MARKET: Record<string, string> = {
  ercot: "ERCOT is an energy-only market: it has no capacity market and no capacity charge.",
  caiso: "California has no capacity market: resource adequacy is bought in bilateral contracts, and no public price of it is held.",
  spp: "SPP has no capacity market: each load-serving entity meets its planning reserve itself.",
};
/** A row's all-in figure: the profile's energy, its transmission and its capacity, each held or zero by design. */
export function allInCell(dc: DC, f: Files, r: Row, x: Pick<SitingInputs, "profile" | "lf" | "strike">): { v: number; parts: Record<string, number> } | { missing: string; words: string } {
  const e = profileCell(dc, f, r, x, f.cp);
  const energy: Part = "why" in e ? { missing: e.why } : { v: e.per };
  const c = cpCharge(dc, f, r, x);
  const transmission: Part = "why" in c ? { missing: c.why } : c.own === null ? { missing: "the load's hours in the four intervals are not held" } : { v: c.own };
  const cc = capacityCell(f, r, x);
  const capacity: Part = "zero" in cc ? { v: 0, zero: cc.zero } : "held" in cc ? { missing: `the zone's capacity price is in ${cc.held.table}, internal`, words: "license needed" } : { missing: cc.why, words: cc.words };
  const a = allIn({ energy, transmission, capacity });
  if ("missing" in a) return a;
  return { v: a.v, parts: { energy: (energy as { v: number }).v, transmission: (transmission as { v: number }).v, capacity: 0 } };
}

// ---------------------------------------------------------------------------------------------------------------------
// capacity (session 704): the latest cleared capacity price for the row's zone, held internal; none where no market
// ---------------------------------------------------------------------------------------------------------------------

/** What data/siting/capacity.json holds of the capacity tables (warehouse/derived/siting_page.py): for each market, its
 * newest delivery period and auction and the zones it priced, and the license, with no price. The tables are internal
 * (iso_all_capacity_prices, pjm_rpm_capacity_prices: the publishers' terms bar republishing) and the repository is
 * public, so no price of them is written into the site's files; the figure is computed where the tables are held
 * (siting_page.py --internal) and drawn here as "license needed", session 408's rule. */
export type CapMarket = { market: string; table: string; license: string; unit: string; period_start: string; period_end: string; auction: string; zones: string[] };
export type CapFile = { built: string; tables: string[]; markets: Record<string, CapMarket> };
/** The capacity zone each row settles in, by grid: the zone's own entity where the newest auction priced it, else the
 * grid's system-wide price. MISO's hubs to their local resource zones; New York's zones to their localities; PJM's one
 * row to the RTO's price. */
export const CAPACITY_MARKET: Record<string, string> = { pjm: "pjm_bra", isone: "isone_fca", miso: "miso_pra", nyiso: "nyiso_icap_spot" };
const NY_LOCALITY: Record<string, string> = { "N.Y.C.": "NYC", LONGIL: "LI", "HUD VL": "G-J Locality", MILLWD: "G-J Locality", DUNWOD: "G-J Locality" };
const MISO_ZONE: Record<string, string> = { "MINN.HUB": "Z1", "ILLINOIS.HUB": "Z4", "INDIANA.HUB": "Z6", "MICHIGAN.HUB": "Z7", "ARKANSAS.HUB": "Z8", "LOUISIANA.HUB": "Z9", "TEXAS.HUB": "Z9", "MS.HUB": "Z10" };
const ISONE_ZONE: Record<string, string> = { ".Z.NEMASSBOST": "NEMA/Boston", ".Z.SEMASS": "SEMA/RI", ".Z.RHODEISLAND": "SEMA/RI", ".Z.MAINE": "NNE", ".Z.NEWHAMPSHIRE": "NNE", ".Z.VERMONT": "NNE" };
export function capacityZone(r: Pick<Row, "grid" | "region">, m: CapMarket | undefined): { entity: string; own: boolean } | null {
  if (!m) return null;
  const has = (z: string) => m.zones.includes(`${r.grid}:${z}`);
  const pick = (z: string | undefined, sys: string) => (z && has(z) ? { entity: `${r.grid}:${z}`, own: true } : has(sys) ? { entity: `${r.grid}:${sys}`, own: false } : null);
  if (r.grid === "nyiso") return pick(NY_LOCALITY[r.region] ?? "NYCA", "NYCA");
  if (r.grid === "miso") return pick(MISO_ZONE[r.region], "ERZ");
  if (r.grid === "isone") return pick(ISONE_ZONE[r.region], "System-wide");
  if (r.grid === "pjm") return pick("RTO", "RTO");
  return null;
}
/** The rule of conversion, for the tip and the offline computation: a capacity price in USD per MW-day is times 365, in
 * USD per kW-month times 12,000, to USD per MW a year; a load is charged on its demand at the grid's peak, taken as its
 * draw while running (the peak hours of PJM, ISO-NE, MISO and NYISO are not held, so a load is taken to run at them), and
 * that over the MWh it uses a year is USD per MW a year over its hours run a year. An interruptible load pays on its firm
 * demand only, which its utility's interruptible tariff sets; those tariffs are not held. */
export const CAPACITY_RULE = "A price in USD per MW-day is times 365, in USD per kW-month times 12,000, to USD per MW a year; the load is charged on its demand at the grid's peak, taken as its draw while running (no grid's peak hours are held here), so per MWh it is that over the hours it runs a year.";
export type CapacityCell = { zero: string } | { held: { table: string; market: CapMarket; entity: string; own: boolean } } | { why: string; words: string };
export function capacityCell(f: Files, r: Row, x: Pick<SitingInputs, "profile">): CapacityCell {
  if (NO_CAPACITY_MARKET[r.grid]) return { zero: NO_CAPACITY_MARKET[r.grid] };
  const m = f.cap?.markets[CAPACITY_MARKET[r.grid] ?? ""];
  const z = capacityZone(r, m);
  if (!m || !z) return { why: `No capacity price is held for ${r.region} (${GRID_NAMES[r.grid]}).`, words: "not held" };
  if (PROFILES[x.profile].interruptible) return { why: `An interruptible load pays capacity on its firm demand only, which its utility's interruptible tariff sets; no such tariff is held. The zone's price is held (${m.table}, ${m.auction}, internal).`, words: "not held" };
  return { held: { table: m.table, market: m, entity: z.entity, own: z.own } };
}

// ---------------------------------------------------------------------------------------------------------------------
// time to connect (session 705): how long a generator took to connect in the grid, and the large-load path
// ---------------------------------------------------------------------------------------------------------------------

/** data/siting/connect.json (warehouse/derived/siting_page.py, from lbnl_interconnection_queue): by grid, the median
 * months from queue entry to commercial operation of the requests that came online in the last three whole years the
 * file holds, with the quartiles and the count. A grid with fewer than `min_n` such requests has no median. */
export type ConnectGrid = { n: number; median: number | null; p25: number | null; p75: number | null };
export type ConnectFile = { table: string; built: string; vintage: string; from: number; to: number; min_n: number; grids: Record<string, ConnectGrid> };
/** The rules in motion for large loads by grid (data/datacenter/rules.json, "Your load"'s own file; large_load_rules). */
export type RuleRow = { date: string; regulator: string; docket: string; status_class: string; read: string | null; url: string; topic: string };
export type RulesFile = { as_of: string; grids: Record<string, { state: string; rows?: RuleRow[] }> };
/** ERCOT's large-load reports (data/large_load_status.json, ercot_large_load_status). */
export type LoadStatus = { table: string; reports: { day: string; document: string; url: string; approved: number | null; month_as_written?: string }[] };
/** The large-load waits measured by stage (data/datacenter/how_soon.json, from large_load_waits, internal). */
export type WaitsFile = { grids: Record<string, { state: string; stages?: { interval: string; measured?: { n: number; form: string } }[] }> };
export type ConnectCell = {
  gen: (ConnectGrid & { from: number; to: number; vintage: string }) | { why: string };
  rule: RuleRow | null; ruleWhy: string;
  status: { approved: number; day: string; document: string; url: string } | null;
  wait: { held: string } | { why: string };
};
export function connectCell(f: Files, r: Row): ConnectCell {
  const c = f.connect, g = c?.grids[r.grid];
  const gen = !c ? { why: "The interconnection queue file is not in the tab's files." }
    : !g || g.median === null ? { why: `Fewer than ${c.min_n} requests in ${GRID_NAMES[r.grid]} came online from ${c.from} to ${c.to} with both dates in Berkeley Lab's file (${g?.n ?? 0}): no median.` }
      : { ...g, from: c.from, to: c.to, vintage: c.vintage };
  const rg = f.rules?.grids[r.grid];
  const decided = (rg?.rows ?? []).filter((x) => x.status_class === "decided").sort((a, b) => b.date.localeCompare(a.date));
  const rule = decided[0] ?? null;
  const ruleWhy = rg?.state === "paused" ? "MISO is paused while its terms are reviewed: no rule is read for it."
    : rule ? "" : `No decided large-load rule for ${GRID_NAMES[r.grid]} is among the rules held (large_load_rules, as of ${f.rules?.as_of ?? "not held"}): ${(rg?.rows ?? []).length} open or undated.`;
  const rep = r.grid === "ercot" ? [...(f.status?.reports ?? [])].filter((x) => x.approved !== null).sort((a, b) => a.day.localeCompare(b.day)).at(-1) : undefined;
  const status = rep ? { approved: rep.approved as number, day: rep.day, document: rep.document, url: rep.url } : null;
  const w = f.waits?.grids[r.grid];
  const wait = w?.state === "measured" ? { held: `Measured waits by stage are held for ${GRID_NAMES[r.grid]} (large_load_waits, internal: ${(w.stages ?? []).filter((s) => s.measured && s.measured.n > 0).length} stages measured); computed, and drawn as "license needed".` }
    : { why: `No large-load wait is measured for ${GRID_NAMES[r.grid]} (large_load_waits): ${w?.state ?? "not held"}.` };
  return { gen, rule, ruleWhy, status, wait };
}

// ---------------------------------------------------------------------------------------------------------------------
// headroom (session 706): demand growth, generation coming in the next twelve months, capacity against the peak
// ---------------------------------------------------------------------------------------------------------------------

/** "Your load"'s copy of eia930_demand_growth (data/demand_growth.json, lib/demandgrowth.ts's DemandFile), as the tab
 * reads it: each balancing authority's mean demand by month and year, the last whole year's peak. */
export type DemandYears = { ytd_through: string; last_year: number; areas: Record<string, { name: string; years: Record<string, Record<string, number>> }> };
/** data/siting/headroom.json (warehouse/derived/siting_page.py): planned generators by grid from eia860m_planned_generators
 * (the twelve months after the table's vintage month, by EIA status), and the installed capacity of the grids that are
 * whole states (eia_state_capacity_annual). */
export type HeadroomFile = {
  built: string; planned_table: string; vintage: string; from: string; to: string;
  planned: Record<string, { construction_mw: number; construction_n: number; approved_mw: number; approved_n: number; other_mw: number; other_n: number }>;
  capacity_table: string; capacity: Record<string, { states: string[]; year: number; mw: number }>;
};
export const BA_OF: Record<string, string> = { ercot: "ERCO", caiso: "CISO", nyiso: "NYIS", isone: "ISNE", spp: "SWPP", miso: "MISO", pjm: "PJM" };
/** The calendar hours of a month label. */
const hoursOfMonth = (m: string) => daysIn(m) * 24;
const monthBack = (m: string, k: number) => {
  const d = new Date(Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)) - 1 - k, 1));
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
};
/** Demand growth: the mean demand of the last twelve months the file holds over the twelve before, from the monthly
 * means weighted by each month's hours. Null when a month of the 24 is not held. */
export type Growth = { pct: number; mw: number; before: number; from: string; to: string; ba: string };
export function demandGrowth(d: DemandYears | undefined, grid: string): Growth | { why: string } {
  const ba = BA_OF[grid], a = ba ? d?.areas[ba] : undefined;
  if (!d || !a) return { why: `No EIA-930 demand is held for ${GRID_NAMES[grid]}.` };
  const mean = (end: string) => {
    let s = 0, h = 0;
    for (let k = 0; k < 12; k++) {
      const m = monthBack(end, k), v = a.years[m.slice(0, 4)]?.[`avg_demand_mw_m${m.slice(5, 7)}`];
      if (v === undefined) return null;
      s += v * hoursOfMonth(m); h += hoursOfMonth(m);
    }
    return s / h;
  };
  const to = d.ytd_through, now = mean(to), before = mean(monthBack(to, 12));
  if (now === null || before === null) return { why: `Twenty-four months of EIA-930 demand ending ${to} are not all held for ${a.name}.` };
  return { pct: 100 * (now / before - 1), mw: now, before, from: monthBack(to, 11), to, ba };
}
/** The grid's installed capacity against its last whole year's peak, for a grid that is whole states; else why. */
export function capacityOverPeak(d: DemandYears | undefined, h: HeadroomFile | undefined, grid: string): { pct: number; mw: number; peak: number; year: number; peakYear: number; states: string[] } | { why: string } {
  const c = h?.capacity[grid], a = d?.areas[BA_OF[grid] ?? ""];
  if (!c) return { why: `${GRID_NAMES[grid]} is not a set of whole states, so the state capacity table (eia_state_capacity_annual) cannot be read as its own. Reserve margins by zone are not held.` };
  const peak = a?.years[String(d!.last_year)]?.peak_demand_mw;
  if (!peak) return { why: `${GRID_NAMES[grid]}'s peak demand of ${d?.last_year} is not held.` };
  return { pct: (100 * c.mw) / peak, mw: c.mw, peak, year: c.year, peakYear: d!.last_year, states: c.states };
}

// ---------------------------------------------------------------------------------------------------------------------
// the all-in column (session 702): drawn only where each part is held or is zero by market design
// ---------------------------------------------------------------------------------------------------------------------

/** One part of the all-in figure: a figure (with `zero`, the reason it is zero by market design), or not held, with
 * the cell's words ("not held", or "license needed" where the part is computed from an internal table, session 704). */
export type Part = { v: number; zero?: string } | { missing: string; words?: string };
export function allIn(parts: Record<"energy" | "transmission" | "capacity", Part>): { v: number } | { missing: string; words: string } {
  let v = 0;
  const gone = Object.entries(parts).filter(([, p]) => "missing" in p) as [string, { missing: string; words?: string }][];
  if (gone.length) return { missing: gone.map(([k, p]) => `${k}: ${p.missing}`).join(" "), words: gone.every(([, p]) => p.words === "license needed") ? "license needed" : "not held" };
  for (const p of Object.values(parts)) v += (p as { v: number }).v;
  return { v };
}

// ---------------------------------------------------------------------------------------------------------------------
// the check keys: allgrids|<column>|<row>[|<inputs>]
// ---------------------------------------------------------------------------------------------------------------------

export type Files = { index: Pick<Index, "grids" | "blank">; nodes: Pick<NodeFile, "nodes">; years: (grid: string) => YearFile[]; cp?: CpFile;
  /** session 703: the Commission's newest approved postage stamp rate (newestRate over texas_delivery.json's matrix) */
  rate?: Rate | null;
  /** session 704: the capacity tables' newest periods and zones, no price (data/siting/capacity.json) */
  cap?: CapFile;
  /** session 705: the queue durations (data/siting/connect.json), the rules, ERCOT's large-load reports and the waits */
  connect?: ConnectFile; rules?: RulesFile; status?: LoadStatus; waits?: WaitsFile;
  /** session 706: "Your load"'s demand file and the tab's planned generation and state capacity */
  demand?: DemandYears; headroom?: HeadroomFile };
/** The figure a check key names, from the files the page reads; undefined when the key names none.
 *   allgrids|rows|hubs, allgrids|rows|nodes                the count of each row set (session 700)
 *   allgrids|energy|<row>|da or rt                         a flat load's price over the last twelve whole months (701);
 *                                                          a node's da is its hub's plus its mean daily basis
 *   allgrids|basis|<node>                                  that mean daily basis (701)
 *   allgrids|energy|<row>|da|<profile key>                 the profile's day-ahead price over the hours it runs (702)
 *   allgrids|lost|<row>|<profile key>                      the hours of the window it was off (702)
 *   allgrids|tx|<row>|firm, curtailing or <profile key>    ERCOT's four-peak transmission charge, USD per MWh (703)
 *   allgrids|txshare|<row>|<profile key>                   the load's share of the four intervals it ran in (703)
 *   allgrids|allin|<row>|<profile key>                     energy plus transmission plus capacity (703)
 *   allgrids|connect|<row>                                 the grid's median months from queue entry to operation (705)
 *   allgrids|demand|<row>                                  demand growth, percent, last twelve months over the twelve before (706)
 *   allgrids|planned|<row>                                 MW under construction due in the twelve months after the vintage (706)
 *   allgrids|capratio|<row>                                installed capacity over the last whole year's peak, percent (706)
 *   allgrids|llapproved|<row>                              ERCOT's large loads approved to energize, MW, newest report (705)
 *   (capacity, session 704: zero where there is no market, drawn as a figure of 0 with no key; elsewhere held internal,
 *   "license needed", and computed only where the tables are, by warehouse/derived/siting_page.py --internal) */
export function sitingStat(f: Files, key: string, dc?: DC): number | undefined {
  const p = key.split("|");
  if (p[0] !== "allgrids") return undefined;
  if (p[1] === "rows") return p[2] === "hubs" ? hubRows(f.index).length : p[2] === "nodes" ? nodeRows(f.nodes).length : undefined;
  if (!dc) return undefined;
  const row = rowOf(f, p[2]);
  if (!row) return undefined;
  if ((p[1] === "energy" && p[4]) || p[1] === "lost") {
    const x = profileOfKey(p[1] === "lost" ? p[3] : p[4]);
    if (!x) return undefined;
    const c = profileCell(dc, f, row, x, f.cp);
    if ("why" in c) return undefined;
    return p[1] === "lost" ? c.t.lost : p[3] === "da" ? c.per : undefined;
  }
  if (p[1] === "energy") {
    const e = energyCell(dc, f, row);
    if (row.kind === "node") return p[3] === "da" ? e.node?.per : undefined;
    return p[3] === "da" ? e.da?.per : p[3] === "rt" ? e.rt?.per : undefined;
  }
  if (p[1] === "basis") return energyCell(dc, f, row).node?.basis;
  if (p[1] === "tx" || p[1] === "txshare") {
    const x = profileOfKey(p[1] === "tx" && (p[3] === "firm" || p[3] === "curtailing") ? p[4] ?? "" : p[3]);
    if (!x) return undefined;
    const c = cpCharge(dc, f, row, x);
    if ("why" in c) return undefined;
    if (p[1] === "txshare") return c.share ?? undefined;
    return p[3] === "firm" ? c.firm : p[3] === "curtailing" ? c.curtailing ?? undefined : c.own ?? undefined;
  }
  if (p[1] === "demand") { const g = demandGrowth(f.demand, row.grid); return "pct" in g ? g.pct : undefined; }
  if (p[1] === "planned") return f.headroom?.planned[row.grid]?.construction_mw;
  if (p[1] === "capratio") { const c = capacityOverPeak(f.demand, f.headroom, row.grid); return "pct" in c ? c.pct : undefined; }
  if (p[1] === "connect" || p[1] === "llapproved") {
    const c = connectCell(f, row);
    return p[1] === "connect" ? ("median" in c.gen ? c.gen.median ?? undefined : undefined) : c.status?.approved;
  }
  if (p[1] === "allin") {
    const x = profileOfKey(p[3]);
    if (!x) return undefined;
    const a = allInCell(dc, f, row, x);
    return "v" in a ? a.v : undefined;
  }
  return undefined;
}
/** A row by its id, in either row set. */
export function rowOf(f: Pick<Files, "index" | "nodes">, id: string): Row | undefined {
  return hubRows(f.index).find((r) => r.id === id) ?? (id.startsWith("ercot:") ? nodeRows(f.nodes).find((r) => r.id === id) : undefined);
}
