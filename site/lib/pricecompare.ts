// Session 96: where power is cheap (/prices/compare, in review). The pure part: what the page chooses from its address,
// and how it orders the site's own copy of hub_price_comparison (data/price_compare.json, written by
// warehouse/derived/price_compare.py; docs/methods/hub_price_comparison.md). No arithmetic: every number is a row of
// the table.
export const TABLE = "hub_price_comparison";

export type Row = {
  entity: string; grid: string; node: string;
  dam_avg_price?: number; dam_negative_hours_share_pct?: number; dam_above_200_hours_share_pct?: number; dam_day_spread_top4_bottom4?: number; dam_hours_held?: number; dam_hours_in_window?: number; dam_basis?: string;
  rtm_avg_price?: number; rtm_negative_hours_share_pct?: number; rtm_above_200_hours_share_pct?: number; rtm_day_spread_top4_bottom4?: number; rtm_hours_held?: number; rtm_hours_in_window?: number; rtm_basis?: string;
  grid_carbon_intensity?: number; grid_carbon_days_held: number; grid_carbon_days_due: number;
};
export type Hidden = { entity: string; grid: string; node: string; reason: string };
export type CompareFile = {
  table: string; built: string; end_month: string; windows: Record<"year" | "month", { start: string; end: string; freq: string }>;
  near_hours: number; near_days: number; high: number; year: Row[]; month: Row[]; held_not_shown: Hidden[]; internal_tables: string[]; not_held: string[];
};

export const PERIODS = ["year", "month"] as const;
export const MARKETS = [{ slug: "dam", name: "Day-ahead" }, { slug: "rtm", name: "Real-time" }] as const;
export const MEASURES = [
  { slug: "avg", field: "avg_price", name: "Average price", unit: "USD per MWh", first: "asc" },
  { slug: "neg", field: "negative_hours_share_pct", name: "Hours below zero", unit: "percent", first: "desc" },
  { slug: "high", field: "above_200_hours_share_pct", name: "Hours above USD 200", unit: "percent", first: "desc" },
  { slug: "spread", field: "day_spread_top4_bottom4", name: "Spread, dearest four hours less cheapest four", unit: "USD per MWh", first: "desc" },
  { slug: "carbon", field: "grid_carbon_intensity", name: "The grid's carbon intensity", unit: "kg CO2 per MWh", first: "asc" },
] as const;
export type Period = (typeof PERIODS)[number];
export type Market = (typeof MARKETS)[number]["slug"];
export type Measure = (typeof MEASURES)[number];
export type Choice = { period: Period; market: Market; sort: Measure; dir: "asc" | "desc" };

/** The page's choices from its address; anything it does not understand is the default (twelve months, day-ahead,
 *  cheapest first). A measure sorts first the way it is usually read: the cheapest, the cleanest, the most hours. */
export function choices(q: Record<string, string | undefined>): Choice {
  const period = PERIODS.find((p) => p === q.period) ?? "year";
  const market = MARKETS.find((m) => m.slug === q.market)?.slug ?? "dam";
  const sort = MEASURES.find((m) => m.slug === q.sort) ?? MEASURES[0];
  const dir = q.dir === "asc" || q.dir === "desc" ? q.dir : sort.first;
  return { period, market, sort, dir };
}
export function href(c: { period: string; market: string; sort: string; dir?: string }): string {
  return `/prices/compare?period=${c.period}&market=${c.market}&sort=${c.sort}${c.dir ? `&dir=${c.dir}` : ""}`;
}

/** A measure of a row in a market: the grid's carbon intensity is the same in both markets. */
export function valueOf(r: Row, market: Market, m: Measure): number | undefined {
  const k = m.slug === "carbon" ? m.field : `${market}_${m.field}`;
  return (r as unknown as Record<string, number | undefined>)[k];
}

/** The rows of a period that hold the market, ordered by a measure; a row that lacks the measure goes last, whatever
 *  the direction. Ties keep the grid and the name's order. */
export function ordered(rows: Row[], c: Choice): Row[] {
  const held = rows.filter((r) => valueOf(r, c.market, MEASURES[0]) !== undefined);
  const sign = c.dir === "asc" ? 1 : -1;
  return [...held].sort((a, b) => {
    const x = valueOf(a, c.market, c.sort), y = valueOf(b, c.market, c.sort);
    if (x === undefined && y === undefined) return a.entity.localeCompare(b.entity);
    if (x === undefined) return 1;
    if (y === undefined) return -1;
    return x === y ? a.entity.localeCompare(b.entity) : sign * (x - y);
  });
}
/** The rows of a period that do not hold the market at all (too few hours): named on the page, with no number. */
export const lacking = (rows: Row[], market: Market) => rows.filter((r) => valueOf(r, market, MEASURES[0]) === undefined);

const NAMES: Record<string, string> = {
  "ercot:HB_BUSAVG": "Bus Average hub", "ercot:HB_HOUSTON": "Houston hub", "ercot:HB_HUBAVG": "Hub Average", "ercot:HB_NORTH": "North hub", "ercot:HB_SOUTH": "South hub", "ercot:HB_WEST": "West hub",
  "caiso:TH_NP15_GEN-APND": "NP15 hub (north)", "caiso:TH_SP15_GEN-APND": "SP15 hub (south)", "caiso:TH_ZP26_GEN-APND": "ZP26 hub (central)",
  "isone:.H.INTERNAL_HUB": "Internal Hub", "isone:.Z.CONNECTICUT": "Connecticut zone", "isone:.Z.MAINE": "Maine zone", "isone:.Z.NEMASSBOST": "Northeast Massachusetts and Boston zone",
  "isone:.Z.NEWHAMPSHIRE": "New Hampshire zone", "isone:.Z.RHODEISLAND": "Rhode Island zone", "isone:.Z.SEMASS": "Southeast Massachusetts zone", "isone:.Z.VERMONT": "Vermont zone",
  "isone:.Z.WCMASS": "West and Central Massachusetts zone",
  "nyiso:CAPITL": "Capital zone", "nyiso:CENTRL": "Central zone", "nyiso:DUNWOD": "Dunwoodie zone", "nyiso:GENESE": "Genesee zone", "nyiso:HUD VL": "Hudson Valley zone", "nyiso:LONGIL": "Long Island zone",
  "nyiso:MHK VL": "Mohawk Valley zone", "nyiso:MILLWD": "Millwood zone", "nyiso:N.Y.C.": "New York City zone", "nyiso:NORTH": "North zone", "nyiso:WEST": "West zone",
  "spp:SPPNORTH_HUB": "North hub", "spp:SPPSOUTH_HUB": "South hub",
};
/** A hub or zone as a reader names it: "ERCOT, North hub"; a node with no name here keeps its own. */
export const label = (r: { entity: string; grid: string; node: string }) => `${r.grid}, ${NAMES[r.entity] ?? r.node}`;

export const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
export const monthName = (m: string) => `${MONTHS[Number(m.slice(5, 7)) - 1]} ${m.slice(0, 4)}`;
/** The window in words: "the twelve months to September 2026" or "September 2026". */
export const periodName = (f: CompareFile, p: Period) => (p === "year" ? `the twelve months to ${monthName(f.end_month)}` : monthName(f.end_month));
