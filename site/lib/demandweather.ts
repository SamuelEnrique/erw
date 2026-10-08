// Session 126: demand growth with the weather taken out (since session 152 the second view of /demand, in review:
// lib/demandpage.ts; built as /demand/weather). Pure functions over the site's
// own copy of eia930_demand_weather (data/demand_weather.json, written by warehouse/derived/demand_weather.py
// --snapshot). Nothing is computed here that the table does not hold: these choose, order and format.

export type Figure = {
  actual: number; expected: number; base: number; growth_pct: number; weather_pct: number; unexplained_pct: number;
  uncertainty_pct: number | null; holdouts: number; finding: boolean; window: string; used: number; wanted: number; at: string | null; outside?: boolean;
};
export type Held = { growth_pct: number; weather_pct: number; unexplained_pct: number; actual: number; expected: number };
export type Fit = {
  hours: number; kinds: number; in_sample_mape_pct: number; oos_mape_pct: number; oos_daily_mape_pct: number; plain_oos_mape_pct: number;
  oos_by_year: Record<string, { mape_pct: number; hours: number }>; hours_not_used: number; hours_held: number; shed_hours: number;
};
export type Grid = {
  name: string; tz: string; fit: Fit; through: string; newest: number;
  years: Record<string, Record<string, Figure | null>>; holdout: Record<string, Record<string, Held | null>>;
};
export type Station = {
  ba: string; usaf: string; wban: string; weight: number; metro: string; name: string; state: string; hours: number; measured: number;
  population?: number; cbsa?: string; cbsa_name?: string; weight_stated?: number;
  interpolated: number; missing: number; longest_gap: number; agree: number; agree_synoptic: number; mean_diff_c: number; shared_hours: number;
};
export type Shift = { mape_pct: number | null; bias_pct: number | null; hours: number };
export type WeatherFile = {
  built_at: string; table: string; train: number[]; through: string; metrics: string[]; grids: Record<string, Grid>;
  equal_weights: { moved: { largest_energy: number; largest_any: number; figures: number } | null } | null;
  california: { late_to: string; join: string; windows: { label: string; start: string; end: string; a_year_earlier: boolean; shifts: Record<string, Shift> }[] };
  dew?: { adopted: boolean; threshold_f: number; by_grid: Record<string, { without: { hour: number; day: number }; with_dew: { hour: number; day: number } }> };
  isne_four_of_five?: { years: Record<string, Record<string, Figure | null>>; hours_held: number; hours: number; hours_on_four: number; least: number } | null;
  weather?: { rows_read: number; ceiling: number; through: string; rule_check?: string[]; stations: Record<string, Station>; grids: Record<string, { hours_held: number; hours: number; hours_with_interpolation: number; days: number }> };
};

export const TABLE = "eia930_demand_weather";
export const ORDER = ["ERCO", "CISO", "PJM", "MISO", "SWPP", "NYIS", "ISNE"];
export const FIGURES = [
  { slug: "energy", key: "energy", name: "The year's energy", what: "the mean of the year's hours" },
  { slug: "summer", key: "summer_peak", name: "The summer peak", what: "the highest hour of June to September" },
  { slug: "winter", key: "winter_peak", name: "The winter peak", what: "the highest hour of December of the year before to February" },
  { slug: "night", key: "overnight_min", name: "The overnight minimum", what: "the mean over the year's days of the lowest hour from midnight to 6 am, local time" },
] as const;

export const whole = (v: number) => Math.round(v).toLocaleString("en-US");
export const one = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
/** A growth figure with its sign, to one decimal: "+7.2" or "-0.4". */
export const signed = (v: number) => `${v > 0 ? "+" : ""}${one(v)}`;
/** The address of a figure and year: the second view of the one demand page (session 152; until then the page stood at
 *  /demand/weather, which now redirects here: next.config.ts). */
export const href = (figure: string, year: string | number) => `/demand?view=weather&figure=${figure}&year=${year}`;

/** The years after the fit's, in order. */
export function years(f: WeatherFile): string[] {
  return [...new Set(ORDER.flatMap((b) => Object.keys(f.grids[b].years)))].sort();
}
/** The newest year that is whole (the newest of all is partial unless its last day is 31 December). */
export function lastWholeYear(f: WeatherFile): string {
  const ys = years(f);
  const newest = Math.max(...ORDER.map((b) => f.grids[b].newest));
  const partial = ORDER.some((b) => f.grids[b].newest === newest && f.grids[b].through < "12-31");
  return partial ? String(ys.filter((y) => Number(y) < newest).pop() ?? ys[ys.length - 1]) : String(newest);
}
/** The figure and the year the address asks for, or the year's energy in the last whole year. */
export function choices(f: WeatherFile, q: Record<string, string | undefined>) {
  const figure = FIGURES.find((x) => x.slug === q.figure) ?? FIGURES[0];
  const ys = years(f);
  const year = q.year && ys.includes(q.year) ? q.year : lastWholeYear(f);
  return { figure, year };
}
export const figureOf = (f: WeatherFile, ba: string, year: string, key: string): Figure | null => f.grids[ba].years[year]?.[key] ?? null;

/** What a figure's remainder may be called: a finding only when it is larger than its uncertainty. */
export function reading(g: Figure | null): "not held" | "a finding" | "smaller than its uncertainty" | "beyond the weather the fit saw" {
  if (!g || g.uncertainty_pct === null) return "not held";
  if (g.finding) return "a finding";
  return g.outside ? "beyond the weather the fit saw" : "smaller than its uncertainty";
}
/** The grids of one figure and year, split by whether the growth the weather does not explain is a finding. */
export function split(f: WeatherFile, year: string, key: string) {
  const all = ORDER.map((ba) => ({ ba, name: f.grids[ba].name, g: figureOf(f, ba, year, key) }));
  const found = all.filter((x) => x.g && x.g.finding).sort((a, b) => Math.abs(b.g!.unexplained_pct) - Math.abs(a.g!.unexplained_pct));
  return { found, not: all.filter((x) => x.g && !x.g.finding), absent: all.filter((x) => !x.g) };
}
/** Every finding of the table, strongest first: by how many times its uncertainty the remainder is. */
export function strongest(f: WeatherFile, n = 5) {
  const out: { ba: string; name: string; year: string; key: string; g: Figure; times: number }[] = [];
  for (const ba of ORDER) for (const [year, row] of Object.entries(f.grids[ba].years)) for (const [key, g] of Object.entries(row)) {
    if (g && g.finding && g.uncertainty_pct) out.push({ ba, name: f.grids[ba].name, year, key, g, times: Math.abs(g.unexplained_pct) / g.uncertainty_pct });
  }
  return out.sort((a, b) => b.times - a.times).slice(0, n);
}
export const day = (ts: string) => new Date(ts).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });
