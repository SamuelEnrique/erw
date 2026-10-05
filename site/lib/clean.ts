// Energy Research Warehouse (ERW) site, session 122: "How clean, and when" (/mix/clean, in review).
//
// The reading of the site's own copy of clean_energy_summary (site/data/clean/<grid>.json, written by
// warehouse/derived/mix_clean.py --snapshot). Pure functions, no imports (Node runs this file as it is, for
// tests/test_session122.py). The page does no arithmetic of its own: every figure is a row of the table, picked here.
// A figure that is not held is null and is shown as not held, never as zero.

export const SUMMARY = "clean_energy_summary";
export const HOURLY = "clean_energy_hourly";
export const GRIDS = ["caiso", "ercot", "isone", "miso", "nyiso", "pjm", "spp"] as const;
export type Grid = (typeof GRIDS)[number];
export const SHAPE_NAME: Record<string, string> = { mix: "the grid's own carbon-free mix", solar: "the grid's solar", wind: "the grid's wind" };
export const SOURCE_NAME: Record<string, string> = { nuclear: "nuclear", wind: "wind", solar: "solar", hydro: "hydro", natural_gas: "natural gas", coal: "coal", other: "other" };

type Vars = Record<string, number | (number | null)[] | undefined>;
export type GridFile = {
  grid: Grid; name: string; tz: string; built: string; join: string | null; first: string; upto: string | null;
  clean: string[]; not_clean: string[]; k: number; shifts: number[]; purchases: number[]; shapes: string[]; levels: number[];
  no_price: string | null; months: Record<string, Vars>; years: Record<string, Vars>;
};
export type Files = Record<Grid, GridFile>;

const num = (v: unknown): number | null => (typeof v === "number" && Number.isFinite(v) ? v : null);
/** One figure of a year or a month, or null when the table does not hold it. */
export const get = (o: Vars | undefined, k: string): number | null => (o ? num(o[k]) : null);

export const isGrid = (g: unknown): g is Grid => typeof g === "string" && (GRIDS as readonly string[]).includes(g);
/** The years the table holds for a grid, oldest first. */
export const yearsOf = (f: GridFile): string[] => Object.keys(f.years).sort();
/** A year is whole when every one of its twelve months is written. */
export const wholeYear = (f: GridFile, y: string): boolean => get(f.years[y], "months") === 12;
/** The newest whole year, else the newest year; null when none. */
export function defaultYear(f: GridFile): string | null {
  const ys = yearsOf(f);
  const whole = ys.filter((y) => wholeYear(f, y));
  return whole.length ? whole[whole.length - 1] : ys.length ? ys[ys.length - 1] : null;
}
/** The months of a year the table holds, in order. */
export const monthsOf = (f: GridFile, y: string): string[] => Object.keys(f.months).filter((m) => m.startsWith(`${y}-`)).sort();
/** The average day of a month: the carbon-free share by local hour, 24 values. */
export const dayOf = (f: GridFile, m: string): (number | null)[] => {
  const d = f.months[m]?.day;
  return Array.isArray(d) && d.length === 24 ? d.map(num) : Array(24).fill(null);
};
/** The four cleanest local hours of a month's average day, cleanest first. */
export const cleanestOf = (f: GridFile, m: string): number[] =>
  [1, 2, 3, 4].map((i) => get(f.months[m], `cleanest_hour_${i}`)).filter((h): h is number => h !== null);

/** Hours as a reader says them: a run of hours as "10:00 to 14:00" when they are consecutive, else each hour. */
export function hoursName(hours: number[]): string {
  if (!hours.length) return "not held";
  const s = [...hours].sort((a, b) => a - b);
  const hh = (h: number) => `${String(h % 24).padStart(2, "0")}:00`;
  return s.every((h, i) => i === 0 || h === s[i - 1] + 1) ? `${hh(s[0])} to ${hh(s[s.length - 1] + 1)}` : s.map(hh).join(", ");
}

/** A year's figures as the page shows them. */
export type YearView = {
  y: string; months: number | null; due: number | null; days: number | null; ownMonths: number | null;
  share: number | null; flat: number | null; ge: Record<number, number | null>;
  match: Record<string, Record<number, { energy: number | null; hours: number | null }>>;
  carbon: { flat: number | null; change: Record<number, number | null>; days: number | null };
  cost: { flat: number | null; change: Record<number, number | null>; days: number | null };
};
export function yearView(f: GridFile, y: string): YearView {
  const v = f.years[y];
  return {
    y, months: get(v, "months"), due: get(v, "months_due"), days: get(v, "days_held"), ownMonths: get(v, "own_data_months"),
    share: get(v, "carbon_free_share_pct"), flat: get(v, "carbon_free_share_flat_pct"),
    ge: Object.fromEntries(f.levels.map((l) => [l, get(v, `hours_cf_ge${l}_pct`)])),
    match: Object.fromEntries(f.shapes.map((s) => [s, Object.fromEntries(f.purchases.map((p) => [p, { energy: get(v, `match_${s}_${p}_energy_pct`), hours: get(v, `match_${s}_${p}_hours_pct`) }]))])),
    carbon: { flat: get(v, "flat_kgco2_per_mwh"), change: Object.fromEntries(f.shifts.map((s) => [s, get(v, `shift${s}_carbon_change_pct`)])), days: get(v, "shift_days") },
    cost: { flat: get(v, "flat_cost_usd_per_mwh"), change: Object.fromEntries(f.shifts.map((s) => [s, get(v, `shift${s}_cost_change_pct`)])), days: get(v, "cost_days") },
  };
}

/** Which source a grid's year rests on: EIA's, CAISO's own, or both (a year the join falls in). */
export function sideOf(v: YearView): "eia930" | "caiso" | "both" {
  if (!v.ownMonths) return "eia930";
  return v.months !== null && v.ownMonths >= v.months ? "caiso" : "both";
}

export const pct = (v: number | null, digits = 1): string => (v === null ? "not held" : `${v.toFixed(digits)}%`);
export const signedPct = (v: number | null, digits = 1): string => (v === null ? "not held" : `${v > 0 ? "+" : ""}${v.toFixed(digits)}%`);
export const one = (v: number | null): string => (v === null ? "not held" : v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 }));
export const two = (v: number | null): string => (v === null ? "not held" : v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
export const monthName = (m: string): string => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "long", timeZone: "UTC" });
export const href = (grid: string, year?: string | null): string => `/mix/clean?grid=${grid}${year ? `&year=${year}` : ""}`;
