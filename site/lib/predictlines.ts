// Energy Research Warehouse (ERW) site, session 10409 (chain 720, part E): what the forecast's page files gained on
// 27 November 2026 (the dated lines of that day at the foot of docs/state/page_files_predict.md, the desktop's second
// window's sessions 10602 and 10603), read for /forecast:
//
//   in each place file's series.demand: operator_filing (the operator's filed forecast checked by month),
//   with_weather_forecast (a separate line, never the ERW forecast), net_demand (demand less wind and solar);
//   in every shown series: band_coverage (how often what happened fell inside the band, below it and above it);
//   two files: wind_solar.json (the ERW forecast of wind and of solar output) and rt_price.json (of the real-time price).
//
// This module holds those shapes and the pure functions the page and its tests share. Nothing is filled or worked out
// beyond what a file holds: a value a file holds as null is a blank with the file's own reason, never a zero.
import type { Cell, Scored, SummaryPart } from "@/lib/predict";

const numOf = (v: Cell | undefined): number | null => (typeof v === "number" && Number.isFinite(v) ? v : null);
const strOf = (v: Cell | undefined): string | null => (typeof v === "string" && v ? v : null);

// ---- The operator's filing, checked by month (method note section 18) -----------------------------------------------

export type OperatorFiling = {
  what?: string; tolerance_pct?: number | null; months_columns?: string[]; months?: Cell[][];
  months_flagged?: number | null; months_held?: number | null;
  shift_mape_last_2_years?: Record<string, number | null> | null; best_shift_hours?: number | null;
  sound_last_2_years?: SummaryPart | null;
};
/** `i`: the month's place in the file's months[], for a figure's key into the file. */
export type FilingMonth = { i: number; month: string; hours: number | null; pct: number | null; flagged: boolean };
/** The months of the check in the file's own order, by the file's column names. */
export function filingMonths(f: OperatorFiling | null | undefined): FilingMonth[] {
  const cols = f?.months_columns ?? [];
  const at = (n: string) => cols.indexOf(n);
  return (f?.months ?? []).map((r, i) => ({ i, month: strOf(r[at("month")]) ?? "", hours: numOf(r[at("hours")]), pct: numOf(r[at("operator_pct_of_demand")]), flagged: r[at("flagged")] === (true as unknown as Cell) }))
    .filter((m) => m.month !== "");
}
/** The filing's hours fit best moved by this many hours; null when the file does not say or says none. */
export const filingShift = (f: OperatorFiling | null | undefined): number | null => (typeof f?.best_shift_hours === "number" && f.best_shift_hours !== 0 ? f.best_shift_hours : null);

// ---- The separate line "with the weather forecast" (section 19) -----------------------------------------------------

export type WeatherForecast = {
  what?: string; airport?: string | null; min_days?: number | null; days?: number | null; status?: string | null;
  all?: SummaryPart | null; tomorrow?: Cell[][] | null; tomorrow_columns?: string[]; tomorrow_issue_utc?: string | null;
};
export const WEATHER_FORECAST_LABEL = "With the weather forecast";
/** The line, the same coefficients on the airport's observed weather (not a forecast), then the methods beside them. */
export const WEATHER_FORECAST_METHODS = ["with_weather_forecast", "with_airport_weather_known", "erw", "operator", "regression", "regression_recent"] as const;
export const WEATHER_FORECAST_WORDS: Record<string, string> = { with_weather_forecast: WEATHER_FORECAST_LABEL, with_airport_weather_known: "With the airport's weather known" };
/** Whether the line has too few days to be judged (the file's status, or fewer days than its own minimum). */
export const tooFewDays = (w: WeatherForecast | null | undefined): boolean => !!w && (w.status === "too_few_days" || (typeof w.days === "number" && typeof w.min_days === "number" && w.days < w.min_days));

export type HourValue = { i: number; ts: string; hour: number; v: number | null };
/** Rows of [ts_utc, local_hour, <column>] as hours, by the file's own column names. */
export function hourValues(columns: string[] | undefined, rows: Cell[][] | null | undefined, column: string): HourValue[] {
  const cols = columns ?? [];
  const t = cols.indexOf("ts_utc"), h = cols.indexOf("local_hour"), c = cols.indexOf(column);
  if (t < 0 || c < 0) return [];
  return (rows ?? []).map((r, i) => ({ i, ts: strOf(r[t]) ?? "", hour: numOf(h < 0 ? undefined : r[h]) ?? 0, v: numOf(r[c]) })).filter((x) => x.ts !== "");
}

// ---- Net demand: the demand less wind and solar (section 20) --------------------------------------------------------

/** A span's scores of net demand, or of wind or solar output: the error in MW, and the error over the mean of the
 *  same hours in percent (a percent of each hour means nothing where the hour is near zero). */
export type MwPart = { first_day: string | null; last_day: string | null; hours: number | null; mae_mw: Scored; nmae_pct: Scored };
export type NetDemand = {
  what?: string; status?: string | null; wind_solar_place?: string | null;
  last_2_years?: MwPart | null; backtest?: MwPart | null; with_operator?: MwPart | null;
  tomorrow_columns?: string[]; tomorrow?: Cell[][] | null;
  /** session 10411 (the contract's line of session 10603): why `tomorrow` holds no hour, `null` when it does */
  tomorrow_held?: string | null;
};
export type MwMetric = "nmae_pct" | "mae_mw";
/** The page's two scores, said for these lines: the percent is of the mean of the hours scored. */
export const mwMetricOf = (metric: "mape" | "mae"): MwMetric => (metric === "mape" ? "nmae_pct" : "mae_mw");
export const MW_SPANS: [string, string][] = [["last_2_years", "the last two years"], ["backtest", "the backtest"], ["with_operator", "the hours the operator also forecast"]];

// ---- The band: how often what happened fell inside it (section 21) --------------------------------------------------

export type BandCoverage = {
  nominal_pct?: number | null; hours?: number | null; inside_pct?: number | null; below_pct?: number | null; above_pct?: number | null;
  by_local_hour_inside_pct?: (number | null)[] | null; by_month_columns?: string[]; by_month?: Cell[][] | null;
};
export type BandMonth = { i: number; month: string; hours: number | null; inside: number | null };
export function bandMonths(b: BandCoverage | null | undefined): BandMonth[] {
  const cols = b?.by_month_columns ?? [];
  const at = (n: string) => cols.indexOf(n);
  return (b?.by_month ?? []).map((r, i) => ({ i, month: strOf(r[at("month")]) ?? "", hours: numOf(r[at("hours")]), inside: numOf(r[at("inside_pct")]) })).filter((m) => m.month !== "");
}
export const BAND_SHARES: [keyof Pick<BandCoverage, "inside_pct" | "below_pct" | "above_pct">, string, string][] = [
  ["inside_pct", "Inside the band", "the share of the hours scored on which what happened fell inside the band"],
  ["below_pct", "Below it", "the share of the hours scored on which what happened fell below the band's low"],
  ["above_pct", "Above it", "the share of the hours scored on which what happened rose above the band's high"],
];

// ---- wind_solar.json: the ERW forecast of wind and of solar output --------------------------------------------------

export type FuelKey = "wind" | "solar";
export const FUELS: FuelKey[] = ["wind", "solar"];
export const FUEL_WORDS: Record<FuelKey, string> = { wind: "Wind", solar: "Solar" };
export type FuelSeries = {
  status: string; method: string | null; method_mae_last_2_years?: Record<string, number | null>; target_series?: string | null;
  operator?: string | null; operator_held?: string | null; made_utc?: string | null; inputs_through_utc?: string | null;
  target_day?: string | null; horizon_days?: number | null; band?: string | null; band_coverage_pct?: number | null; band_coverage?: BandCoverage | null;
  tomorrow_columns?: string[]; tomorrow?: Cell[][] | null; tomorrow_held?: string | null;
  summary?: Record<string, MwPart | null | undefined> | null; history_columns?: string[]; history?: Cell[][] | null;
};
/** `shown_for` (session 10411; the contract's line of session 10603, in answer to this window's request 11): the place
 *  files that show the entry (`grid-caiso` for `ba-ciso`; `region-tex` for itself and `ba-erco`). */
export type WindSolarPlace = { place: string; name?: string; time?: string; shown_for?: string[] | null; fuels?: Partial<Record<FuelKey, FuelSeries>> };
/** A method's own words in a file: `words` in the wind and solar and the real-time files, `what` in the others. */
export type MethodWords = { id: string; words?: string; what?: string };
export type WindSolarFile = {
  example?: boolean; contract?: string; built: string | null; tier?: string; label?: string; method_note?: string; made_rule?: string | null; units?: string | null;
  methods?: MethodWords[]; places: WindSolarPlace[]; rows_columns?: string[]; rows?: Cell[][];
  /** session 10411: each cut's words, in the form of scores.json's (request 12) */
  cuts?: Record<string, string> | null;
};
/** The wind and solar entry a place shows, with its position: the entry whose `shown_for` names the place; in a file
 *  that carries no `shown_for` at all (the files before session 10603's), the entry the place's net demand names, or
 *  the one of the place's own id. An example file shows nothing. */
export function windSolarFor(file: WindSolarFile | null, place: string, named?: string | null): { pi: number; place: WindSolarPlace } | null {
  if (!file || file.example === true) return null;
  const places = file.places ?? [];
  const lists = places.some((p) => Array.isArray(p.shown_for));
  const pi = lists ? places.findIndex((p) => (p.shown_for ?? []).includes(place)) : places.findIndex((p) => p.place === (named ?? place));
  return pi < 0 ? null : { pi, place: places[pi] };
}
/** A place's entry in the wind and solar file with its position there (a figure's key names it), or null. An example
 *  file shows nothing. */
export function windSolarOf(file: WindSolarFile | null, place: string | null | undefined): { pi: number; place: WindSolarPlace } | null {
  if (!file || file.example === true || !place) return null;
  const pi = (file.places ?? []).findIndex((p) => p.place === place);
  return pi < 0 ? null : { pi, place: file.places[pi] };
}
/** A fuel's series is drawn only when its status is "shown". */
export const fuelShown = (f: FuelSeries | null | undefined): f is FuelSeries => !!f && f.status === "shown";
/** The methods a wind or solar table sets side by side: the ERW forecast, the operator's where it is scored, then
 *  the plain ones the file scores. */
export const FUEL_METHODS = ["erw", "operator", "yesterday", "profile7"] as const;
export const LINE_METHOD_WORDS: Record<string, string> = { profile7: "Mean of the same hour, seven days", day_ahead: "Day-ahead price" };
export const LINE_METHOD_SHORT: Record<string, string> = { profile7: "Seven-day mean", day_ahead: "Day-ahead" };
/** What a file says of a method, in its own words. */
export const wordsOfMethod = (methods: MethodWords[] | undefined, id: string): string => { const m = methods?.find((x) => x.id === id); return m?.words ?? m?.what ?? ""; };

// ---- rt_price.json: the ERW forecast of the real-time price ---------------------------------------------------------

export type RtHub = {
  hub: string; grid: string; time: string; status: string; method: string | null; method_mae_last_2_years?: Record<string, number | null>;
  made_utc?: string | null; inputs_through_utc?: string | null; target_day?: string | null; horizon_days?: number | null;
  band?: string | null; band_coverage_pct?: number | null; band_coverage?: BandCoverage | null;
  tomorrow_columns?: string[]; tomorrow?: Cell[][] | null; tomorrow_held?: string | null;
  summary?: Record<string, SummaryPart | null | undefined> | null; history_columns?: string[]; history?: Cell[][] | null;
  /** session 10411 (the contract's line of session 10603): the same backtest from 2016, scored by calendar year */
  long_backtest?: LongBacktest | null;
};
/** The backtest as far back as a hub's prices allow, scored over the whole span and year by year. The method is the
 *  one chosen now, so the earlier years test the rule and do not choose. */
export type LongBacktest = {
  what?: string; first_target?: string | null; method?: string | null; all?: SummaryPart | null; band_coverage_pct?: number | null;
  by_year?: (SummaryPart & { year: number })[] | null;
};
export type RtPriceFile = {
  example?: boolean; contract?: string; built: string | null; tier?: string; label?: string; method_note?: string; made_rule?: string | null; units?: string | null;
  methods?: MethodWords[]; hubs: RtHub[]; rows_columns?: string[]; rows?: Cell[][];
  /** session 10411: each cut's words (request 12): `top10` is the hub's ten days with the highest real-time price hour */
  cuts?: Record<string, string> | null;
};

// ---- price_hubs.json: the ERW forecast of the day-ahead price at more hubs (session 10411) ---------------------------

/** One more hub of a public grid: a place file's `series.price` block, with `place` ("hub-<grid>", the name its score
 *  rows carry), `grid`, `demand_place` (the place whose demand it reads) and `time` first. */
export type PriceHub = {
  place: string; grid: string; demand_place?: string | null; time: string; status: string; held?: string | null; method: string | null; hub: string; market?: string | null;
  unit?: string; method_note?: string; made_utc?: string | null; inputs_through_utc?: string | null; target_day?: string | null; fit_day?: string | null;
  horizon_days?: number | null; demand_horizon_days?: number | null; band?: string | null; band_coverage_pct?: number | null; band_coverage?: BandCoverage | null;
  tomorrow_columns?: string[]; tomorrow?: Cell[][] | null; tomorrow_held?: string | null; operator_held?: string | null;
  history_columns?: string[]; history?: Cell[][] | null; summary?: Record<string, SummaryPart | null | undefined> | null;
  method_mae_last_2_years?: Record<string, number | null>;
};
export type PriceHubsFile = {
  example?: boolean; contract?: string; built: string | null; tier?: string; label?: string; what?: string | null; method_note?: string; made_rule?: string | null;
  methods?: MethodWords[]; hubs: PriceHub[]; rows_columns?: string[]; rows?: Cell[][]; cuts?: Record<string, string> | null;
};
/** A hub's grid, as its id names it: "ercot" of "ercot:HB_HOUSTON". */
export const gridOfHub = (hub: string | null | undefined): string => (hub ?? "").split(":")[0];
/** The other hubs of the grid of a place's own price hub, in the files' order: every hub of the day-ahead hubs file
 *  and of the real-time file whose id names the same grid, the place's own hub left out. A hub's grid is the part of
 *  its id before the colon, in both files; neither file says which places a hub is shown for (asked of window B). */
export function moreHubs(own: string | null | undefined, hubs: PriceHubsFile | null, rt: RtPriceFile | null): string[] {
  const grid = gridOfHub(own);
  if (!own || !grid) return [];
  const ids = [...(hubs && hubs.example !== true ? hubs.hubs.map((h) => h.hub) : []), ...(rt && rt.example !== true ? rt.hubs.map((h) => h.hub) : [])];
  return [...new Set(ids.filter((id) => id !== own && gridOfHub(id) === grid))];
}
/** A hub's day-ahead entry in the hubs file, with its position, or null. */
export function priceHubOf(file: PriceHubsFile | null, hub: string | null | undefined): { hi: number; hub: PriceHub } | null {
  if (!file || file.example === true || !hub) return null;
  const hi = (file.hubs ?? []).findIndex((h) => h.hub === hub);
  return hi < 0 ? null : { hi, hub: file.hubs[hi] };
}
/** The methods a table of a hub's day-ahead price sets side by side (no operator publishes a price forecast). */
export const HUB_METHODS = ["erw", "yesterday", "week_ago", "regression"] as const;
export const HUB_SPANS: [string, string][] = [["last_30_days", "The last 30 days"], ["backtest", "The backtest"]];
/** A cut's words on the page for a price: the ten days are those of the highest price hour, not of the highest demand. */
export const PRICE_CUT_WORDS: Record<string, string> = {
  all: "Every hour scored", last_2_years: "The last two years", top10: "The ten days with the highest price hour", spike: "Price spikes (hours above the hub's 99th percentile)",
};
/** The real-time price entry of a hub (the hub a place's day-ahead price forecast is of), with its position, or null. */
export function rtHubOf(file: RtPriceFile | null, hub: string | null | undefined): { hi: number; hub: RtHub } | null {
  if (!file || file.example === true || !hub) return null;
  const hi = (file.hubs ?? []).findIndex((h) => h.hub === hub);
  return hi < 0 ? null : { hi, hub: file.hubs[hi] };
}
/** The day-ahead price is the market's own forecast of the real-time price: the comparator, never an ERW method. */
export const RT_METHODS = ["erw", "day_ahead", "yesterday", "regression"] as const;
export const RT_SPANS: [string, string][] = [["last_2_years", "The last two years"], ["backtest", "The backtest"]];
export const RT_LABEL = "Real-time price";

/** One hour of a line's tomorrow or of a past day, by the file's own column names; `other` is the line beside the ERW
 *  forecast (the operator's forecast of wind or solar; the day-ahead price). */
export type LineHour = { i: number; ts: string; day: string | null; hour: number; erw: number | null; lo: number | null; hi: number | null; other: number | null; actual: number | null; yesterday: number | null };
export function lineHours(columns: string[] | undefined, rows: Cell[][] | null | undefined, other: string): LineHour[] {
  const cols = columns ?? [];
  const at = (n: string) => cols.indexOf(n);
  const get = (r: Cell[], n: string) => (at(n) < 0 ? undefined : r[at(n)]);
  return (rows ?? []).filter((r) => Array.isArray(r) && typeof get(r, "ts_utc") === "string").map((r, i) => ({
    i, ts: get(r, "ts_utc") as string, day: strOf(get(r, "local_day")), hour: numOf(get(r, "local_hour")) ?? 0,
    erw: numOf(get(r, "erw")), lo: numOf(get(r, "lo")), hi: numOf(get(r, "hi")), other: numOf(get(r, other)), actual: numOf(get(r, "actual")), yesterday: numOf(get(r, "yesterday")),
  }));
}
/** The past days a line holds, newest first. */
export const lineDays = (hours: LineHour[]): string[] => [...new Set(hours.map((h) => h.day).filter((d): d is string => !!d))].sort().reverse();
/** The newest past day that holds both a forecast and what happened; else the newest day held; else null. */
export function lineDefaultDay(hours: LineHour[]): string | null {
  const full = hours.filter((h) => h.erw !== null && h.actual !== null && h.day).map((h) => h.day as string).sort();
  if (full.length) return full[full.length - 1];
  const days = lineDays(hours);
  return days.length ? days[0] : null;
}

// ---- Score rows of a file other than scores.json --------------------------------------------------------------------

/** One score row: its place in the file's rows[] (a figure's key), its count of hours, and its two scores by the
 *  names of the file's own columns. */
export type LineScore = { i: number; hours: number | null; values: Record<string, number | null>; held: string | null };
/** The rows of a file that match `where` (column name to value), grouped by cut, with each cut's keys in the file's
 *  own order and each cell under "<key>|<method>". The score columns are named by the caller as the file names them
 *  (mae and mape; mae_mw and nmae_pct). */
export function lineScores(columns: string[] | undefined, rows: Cell[][] | undefined, where: Record<string, string>, scoreColumns: readonly string[]): Map<string, { keys: string[]; cells: Map<string, LineScore> }> {
  const out = new Map<string, { keys: string[]; cells: Map<string, LineScore> }>();
  const cols = columns ?? [];
  const at = (n: string) => cols.indexOf(n);
  const want = Object.entries(where).map(([n, v]) => [at(n), v] as const);
  if (want.some(([i]) => i < 0) || at("cut") < 0 || at("method") < 0) return out;
  (rows ?? []).forEach((r, i) => {
    if (want.some(([c, v]) => r[c] !== v)) return;
    const cut = String(r[at("cut")] ?? ""), key = String(r[at("key")] ?? ""), method = String(r[at("method")] ?? "");
    const g = out.get(cut) ?? { keys: [], cells: new Map<string, LineScore>() };
    if (!g.keys.includes(key)) g.keys.push(key);
    g.cells.set(`${key}|${method}`, { i, hours: numOf(at("hours") < 0 ? undefined : r[at("hours")]), values: Object.fromEntries(scoreColumns.map((c) => [c, numOf(at(c) < 0 ? undefined : r[at(c)])])), held: strOf(at("held") < 0 ? undefined : r[at("held")]) });
    out.set(cut, g);
  });
  return out;
}

/** A share in percent, as the page writes it: the file's own digits kept to two decimals. */
export const shareWords = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

// ---- Downloads (session 10410): the lines of 27 November as CSVs -----------------------------------------------------

const csvCell = (c: Cell | undefined) => (c === null || c === undefined ? "" : /[",\n]/.test(String(c)) ? `"${String(c).replace(/"/g, '""')}"` : String(c));
const csvLines = (head: string[], rows: (Cell | undefined)[][]) => [head, ...rows].map((r) => r.map(csvCell).join(",")).join("\n") + "\n";

export const NET_HEAD = ["place", "line", "part", "ts_utc", "local_day", "local_hour", "erw_forecast", "band_low", "band_high", "operator_forecast", "actual", "same_hour_yesterday"];
/** A place's net demand, wind and solar as a CSV, with the provenance first: net demand for the day forecast now (it
 *  has no band: the three bands are not combined), and wind and solar for that day and every past hour the wind and
 *  solar file holds. A line that is not shown has no row, and the header says why. */
export function netCsv(place: { place: string; name: string }, demand: { target_day?: string | null; net_demand?: NetDemand | null } | null | undefined, file: WindSolarFile | null, url: string): string {
  const net = demand?.net_demand ?? null;
  const entry = windSolarFor(file, place.place, net?.wind_solar_place);
  const head = [
    `# Energy Research Warehouse (ERW): the ERW forecast of net demand, wind and solar for ${place.name}, hour by hour (site/lib/predictlines.ts netCsv)`,
    "# ERW forecast: a model's output (tier derived), never a published or official figure. operator_forecast is the operator's own, where the warehouse holds it. MW.",
    `# Built: ${file?.built ?? "not built"} (site/data/predict/wind_solar.json) and the place's own file (site/data/predict/${place.place}.json)`,
    `# Net demand: ${net?.what ?? "the demand less the output of wind and solar"}`,
    `# Method: ${file?.method_note ?? "docs/methods/predict_wind_solar.md"} and docs/methods/predict.md. Contract: docs/state/page_files_predict.md`,
    "# part: tomorrow (the day forecast now) or history (a past day, with what happened). ts_utc is the start of an hour, UTC; local_day and local_hour are in the place's clock",
    `# From: ${url}`,
  ];
  const rows: (Cell | undefined)[][] = [];
  if (!net || net.status !== "shown") head.push(`# net_demand: no line. ${net ? `The file's status: ${net.status ?? "not said"}` : "The place's file holds no net demand"}`);
  else for (const h of hourValues(net.tomorrow_columns, net.tomorrow, "erw")) rows.push([place.place, "net_demand", "tomorrow", h.ts, demand?.target_day ?? null, h.hour, h.v, null, null, null, null, null]);
  for (const fuel of FUELS) {
    const f = entry?.place.fuels?.[fuel];
    const status = f?.status;
    if (!fuelShown(f)) { head.push(`# ${fuel}: no line. ${status ? `The file's status: ${status}` : "The wind and solar file holds no such line for this place"}`); continue; }
    head.push(`# ${fuel}: ${f.target_series ?? "the place's output"}; method ${f.method ?? "not said"}; made ${f.made_utc ?? "not said"}; band: ${f.band ?? "not said"}${f.operator ? `; operator_forecast: ${f.operator}` : ""}`);
    for (const h of lineHours(f.tomorrow_columns, f.tomorrow, "operator")) rows.push([place.place, fuel, "tomorrow", h.ts, f.target_day ?? null, h.hour, h.erw, h.lo, h.hi, h.other, null, null]);
    for (const h of lineHours(f.history_columns, f.history, "operator")) rows.push([place.place, fuel, "history", h.ts, h.day, h.hour, h.erw, h.lo, h.hi, h.other, h.actual, h.yesterday]);
  }
  return `${head.join("\n")}\n${csvLines(NET_HEAD, rows)}`;
}

export const RT_HEAD = ["hub", "part", "ts_utc", "local_day", "local_hour", "erw_forecast", "band_low", "band_high", "day_ahead_price", "actual", "same_hour_two_days_before"];
/** A hub's real-time price forecast as a CSV, with the provenance first: the day forecast now and every past hour the
 *  file holds, beside the hub's day-ahead price. A day with no forecast has no row, and the header says why. */
export function rtCsv(hub: RtHub, file: RtPriceFile, url: string): string {
  const head = [
    `# Energy Research Warehouse (ERW): the ERW forecast of the real-time price at ${hub.hub}, hour by hour (site/lib/predictlines.ts rtCsv)`,
    "# ERW forecast: a model's output (tier derived), never a published or official figure. day_ahead_price is the hub's day-ahead price, the market's own forecast of the real-time price: the comparator, never an ERW method. USD/MWh.",
    `# Built: ${file.built ?? "not built"} (site/data/predict/rt_price.json); made ${hub.made_utc ?? "not said"}; method ${hub.method ?? "not said"}; band: ${hub.band ?? "not said"}`,
    `# Rule: ${file.made_rule ?? "not said"}. Method: ${file.method_note ?? "docs/methods/predict_price.md"}. Contract: docs/state/page_files_predict.md`,
    `# part: tomorrow (the day forecast now) or history (a past day, with what happened). ts_utc is the start of an hour, UTC; local_day and local_hour are in the hub's clock (${hub.time})`,
    "# same_hour_two_days_before: the real-time price of the same local hour of the latest whole day read (the file's column yesterday)",
    ...(hub.tomorrow_held ? [`# tomorrow: no row. ${hub.tomorrow_held}`] : []),
    `# From: ${url}`,
  ];
  const rows: (Cell | undefined)[][] = [];
  if (hub.status === "shown") {
    for (const h of lineHours(hub.tomorrow_columns, hub.tomorrow, "day_ahead")) rows.push([hub.hub, "tomorrow", h.ts, hub.target_day ?? null, h.hour, h.erw, h.lo, h.hi, h.other, null, null]);
    for (const h of lineHours(hub.history_columns, hub.history, "day_ahead")) rows.push([hub.hub, "history", h.ts, h.day, h.hour, h.erw, h.lo, h.hi, h.other, h.actual, h.yesterday]);
  }
  return `${head.join("\n")}\n${csvLines(RT_HEAD, rows)}`;
}
