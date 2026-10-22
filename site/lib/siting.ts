// Energy Research Warehouse (ERW) site, session 700: "Where can a large load go", the All grids tab of /cost-of-power
// (chain 050 of 23 October 2026, docs/methods/siting.md).
//
// The tab answers, for every grid, hub and zone the warehouse holds a price for, and for every ERCOT node of
// node_basis_daily, the questions "Your load" answers for one region: what a load pays, when it connects, how clean the
// power is. It is the same page and the same model: a row's energy is lib/datacenter.ts's arithmetic over the same files
// (data/datacenter), never a second one. This file holds what is pure: the four load profiles, the eight columns with
// their tips, the row sets, the inputs in the address, and the figure a check key names (scripts/check-values.mjs
// recomputes every key of the tab here). No imports but types: Node runs it as it is (tests/test_session700.py).
import type { Index } from "./datacenter";

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
    tip: "ERCOT: the load's share of the four summer peak intervals at the Commission's rate (ercot_4cp_intervals), firm and curtailing. Elsewhere the utility's large-load tariff, not held." },
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
export type NodeRow = { id: string; cls: string; types: string };
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
export type SitingInputs = { profile: ProfileId; mw: number; lf: number; rows: RowSet };
export const SITING_LIMITS = { mw: [1, 10000] as [number, number], lf: [0.05, 1] as [number, number] };
export const SITING_DEFAULTS = { profile: "datacenter" as ProfileId, mw: 100, rows: "hubs" as RowSet };
const clampTo = (v: number, [lo, hi]: [number, number]) => Math.min(hi, Math.max(lo, v));
/** The tab's inputs from its address; a value it cannot read is the default, a number outside its bounds the nearest. */
export function sitingInputs(q: Record<string, string | undefined>): SitingInputs {
  const profile = (PROFILE_ORDER as string[]).includes(q.profile ?? "") ? (q.profile as ProfileId) : SITING_DEFAULTS.profile;
  const p = PROFILES[profile];
  const num = (s: string | undefined, d: number, lim: [number, number]) => { const v = s === undefined || s === "" ? NaN : Number(s); return Number.isFinite(v) ? clampTo(v, lim) : d; };
  return { profile, mw: num(q.mw, SITING_DEFAULTS.mw, SITING_LIMITS.mw), lf: num(q.lf, p.lf, p.lfRange), rows: q.rows === "nodes" ? "nodes" : "hubs" };
}
/** The tab's address for its inputs, with a change; a value at its default is left out. */
export function sitingHref(x: SitingInputs, change: Partial<SitingInputs> = {}): string {
  const y = { ...x, ...change };
  if (change.profile && change.profile !== x.profile && change.lf === undefined) y.lf = PROFILES[change.profile].lf;
  const q = new URLSearchParams({ view: "allgrids" });
  if (y.profile !== SITING_DEFAULTS.profile) q.set("profile", y.profile);
  if (y.mw !== SITING_DEFAULTS.mw) q.set("mw", String(y.mw));
  if (y.lf !== PROFILES[y.profile].lf) q.set("lf", String(y.lf));
  if (y.rows !== SITING_DEFAULTS.rows) q.set("rows", y.rows);
  return `/cost-of-power?${q.toString()}`;
}

// ---------------------------------------------------------------------------------------------------------------------
// the check keys: allgrids|<column>|<row>[|<inputs>]
// ---------------------------------------------------------------------------------------------------------------------

export type Files = { index: Pick<Index, "grids" | "blank">; nodes: Pick<NodeFile, "nodes"> };
/** The figure a check key names, from the files the page reads; undefined when the key names none. Session 700:
 * allgrids|rows|hubs and allgrids|rows|nodes, the count of each row set. */
export function sitingStat(f: Files, key: string): number | undefined {
  const p = key.split("|");
  if (p[0] !== "allgrids") return undefined;
  if (p[1] === "rows") return p[2] === "hubs" ? hubRows(f.index).length : p[2] === "nodes" ? nodeRows(f.nodes).length : undefined;
  return undefined;
}
