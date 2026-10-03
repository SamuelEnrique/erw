// Energy Research Warehouse (ERW) site, session 75: the shoulder hours (/shoulder). The page's model: it picks rows of
// shoulder_hours_monthly (warehouse/derived/shoulder_hours.py; docs/methods/shoulder_hours.md) and does no arithmetic.
// Every number on the page is a row, carried with its check key (series|shoulder_hours_monthly|<entity>|<variable>|<ts>),
// which scripts/check-values.mjs reads like any series value. No imports from the app: Node runs this file as it is.

export const TABLE = "shoulder_hours_monthly";
export type Row = { entity: string; variable: string; ts_utc: string; value: number };

export const GRIDS = [
  { slug: "ercot", name: "ERCOT", entity: "iso:ercot", note: "EIA-930 hourly demand, solar, wind and battery output, from January 2019." },
  { slug: "caiso", name: "CAISO", entity: "iso:caiso", note: "EIA-930 hourly demand, solar and wind, January 2019 to November 2025: EIA's generation series for California changed on 16 December 2025, and this page does not mix the changed series in. Battery output is CAISO's own (Today's Outlook), from August 2025." },
] as const;
export type Grid = (typeof GRIDS)[number];

export const tsOf = (month: string) => `${month}-01T00:00:00Z`;
export const yearTs = (year: string) => `${year}-01-01T00:00:00Z`;
export const monthOf = (ts: string) => ts.slice(0, 7);

/** A number as the site writes it: whole numbers with separators, others to two decimals (as check-values reads). */
export function shown(v: number): string {
  return Number.isInteger(v) ? v.toLocaleString("en-US") : v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
/** The check key of a row: a month's rows and a year's (dated its first day) are both at <YYYY-MM>-01T00:00:00Z. */
export const checkKey = (r: Row) => `series|${TABLE}|${r.entity}|${r.variable}|${tsOf(monthOf(r.ts_utc))}`;
export const monthName = (m: string) => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });
export const hourName = (h: number) => (h >= 24 ? "midnight" : `${String(h).padStart(2, "0")}:00`);

/** An index of the rows: (entity, variable, month or year start) to the row. */
export function index(rows: Row[]): Map<string, Row> {
  return new Map(rows.map((r) => [`${r.entity}|${r.variable}|${monthOf(r.ts_utc)}`, { ...r, ts_utc: `${monthOf(r.ts_utc)}-01T00:00:00Z` }]));
}

/** The grid and the month from a query; the month defaults to the newest month held for the grid. */
export function choices(q: Record<string, string | undefined>, months: Record<string, string[]>) {
  const grid = GRIDS.find((g) => g.slug === q.grid) ?? GRIDS[0];
  const held = months[grid.slug] ?? [];
  const month = q.month && held.includes(q.month) ? q.month : held.at(-1) ?? null;
  return { grid, month };
}

export type Series = "demand" | "solar" | "wind" | "net_load" | "battery";
export type View = {
  grid: Grid; month: string; months: string[];
  hour: (s: Series, h: number) => Row | undefined;
  get: (v: string) => Row | undefined;
  hasBattery: boolean;
  monthly: { month: string; shoulder?: Row; covered?: Row; needed?: Row; fleetHours?: Row }[];
  years: { year: string; get: (v: string) => Row | undefined }[];
};

export function view(rows: Row[], grid: Grid, month: string): View {
  const ix = index(rows);
  const at = (v: string, m: string) => ix.get(`${grid.entity}|${v}|${m}`);
  const months = [...new Set(rows.filter((r) => r.entity === grid.entity && r.variable === "days_held").map((r) => monthOf(r.ts_utc)))].sort();
  const years = [...new Set(rows.filter((r) => r.entity === grid.entity && r.variable === "year_months_held").map((r) => monthOf(r.ts_utc)))].sort();
  return {
    grid, month, months,
    hour: (s, h) => at(`avg_${s}_mw_h${String(h).padStart(2, "0")}`, month),
    get: (v) => at(v, month),
    hasBattery: !!at("avg_battery_mw_h00", month),
    monthly: months.map((m) => ({ month: m, shoulder: at("shoulder_hours", m), covered: at("shoulder_hours_covered", m), needed: at("shoulder_hours_needed", m), fleetHours: at("fleet_hours", m) })),
    years: years.map((y) => ({ year: y.slice(0, 4), get: (v: string) => at(v, y) })),
  };
}
