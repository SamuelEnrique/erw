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
export function href(c: { period: string; market: string; sort: string; dir?: string; a?: string; b?: string }): string {
  // session 7540: the A and B chosen ride along on every link of the page, so a change of period, market or order keeps them
  return `/prices/compare?period=${c.period}&market=${c.market}&sort=${c.sort}${c.dir ? `&dir=${c.dir}` : ""}${c.a ? `&a=${encodeURIComponent(c.a)}` : ""}${c.b ? `&b=${encodeURIComponent(c.b)}` : ""}`;
}

// ---------------------------------------------------------------------------------------------------------------------
// Session 7540 (chain 304, part C: the page read as a fund analyst setting two hubs side by side;
// docs/reviews/compare-read-2026-11-16.md): the license hold, A and B, and ERCOT's two averaged hubs in words.
// ---------------------------------------------------------------------------------------------------------------------

/** A row held under a license on the day: its name only, never a figure. */
export type HeldRow = { entity: string; grid: string; node: string };
/** The rows of a period split by the license hold of the day (`isHeld` is lib/license.ts licenseHeldRow(TABLE, entity):
 *  hub_price_comparison is held by grid, ISO-NE, MISO and NYISO). A held row keeps its name and loses every figure, so
 *  no held figure reaches the page or the browser (the price board's rule, lib/board.ts holdRows). */
export function hold(rows: Row[], isHeld: (entity: string) => boolean): { shown: Row[]; held: HeldRow[] } {
  const shown: Row[] = [], held: HeldRow[] = [];
  for (const r of rows) {
    if (isHeld(r.entity)) held.push({ entity: r.entity, grid: r.grid, node: r.node });
    else shown.push(r);
  }
  held.sort((x, y) => x.entity.localeCompare(y.entity));
  return { shown, held };
}
/** The grids of the held rows, in their order. */
export const heldGrids = (held: HeldRow[]) => [...new Set(held.map((h) => h.grid))];

/** A and B from the address: an entity as the table writes it ("ercot:HB_WEST"), or nothing. */
export type Pair = { a?: string; b?: string };
export function pairOf(q: Record<string, string | undefined>): Pair {
  const ok = (v?: string) => (v && v.length <= 80 && /^[a-z]+:[A-Za-z0-9_. -]+$/.test(v) ? v : undefined);
  return { a: ok(q.a), b: ok(q.b) };
}

/** What a name does not say, on hover: ERCOT's two hubs that are averages of other prices (ERCOT Nodal Protocols,
 *  section 3.5.2). On every window here the Hub Average's figure is the mean of the four hubs' own. */
export const NAME_WORDS: Record<string, string> = {
  "ercot:HB_HUBAVG": "ERCOT's Hub Average: the simple average of the prices of its four trading hubs, North, South, Houston and West (ERCOT Nodal Protocols, section 3.5.2). Its average here is the mean of the four hubs' averages.",
  "ercot:HB_BUSAVG": "ERCOT's Bus Average hub: the simple average of the prices at the hub buses of its four trading hubs, North, South, Houston and West (ERCOT Nodal Protocols, section 3.5.2).",
};

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
  // session 7052 (done-line request 142): ERCOT's eight load zones (ercot_zone_prices_history)
  "ercot:LZ_AEN": "Austin Energy load zone", "ercot:LZ_CPS": "CPS Energy (San Antonio) load zone", "ercot:LZ_HOUSTON": "Houston load zone", "ercot:LZ_LCRA": "LCRA load zone",
  "ercot:LZ_NORTH": "North load zone", "ercot:LZ_RAYBN": "Rayburn load zone", "ercot:LZ_SOUTH": "South load zone", "ercot:LZ_WEST": "West load zone",
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
