// Energy Research Warehouse (ERW) site, session 10401 (chain 720, part C): the ERW forecast page (/forecast).
//
// The page shows the ERW's own day-ahead forecast of demand and price for a place, the operator's own forecast beside
// it, and how each has scored against what happened. Every figure is read from the page files the data machine's
// forecast build writes (site/data/predict/: index.json, one file a place, scores.json; contract
// docs/state/page_files_predict.md; methods docs/methods/predict.md and predict_price.md). This module holds the files'
// shapes and the pure functions the page, its download routes and its tests share. Nothing is filled: a value a file
// holds as null is a blank with the file's own reason, never a zero.
//
// The word "forecast" in the code belongs to the Economic impact tool (lib/forecast*.ts, data/forecast, app/impact):
// nothing of it is imported here. This build's name in every path is "predict"; on the page it is "ERW forecast".

import type { BandCoverage, NetDemand, OperatorFiling, WeatherForecast } from "@/lib/predictlines";

export type SeriesKey = "demand" | "price";
export const SERIES: SeriesKey[] = ["demand", "price"];
export const SERIES_WORDS: Record<SeriesKey, string> = { demand: "Demand", price: "Price" };
/** The words every chart and table of the model's line carries (the contract's `label`). */
export const LABEL = "ERW forecast";

export type Cell = string | number | null;
export type IndexSeries = {
  status: string; held: string | null; method: string | null; fit_day: string | null; target_day: string | null;
  hub: string | null; market: string | null;
};
export type IndexPlace = { place: string; name: string; kind: "region" | "ba"; eia930: string; time: string; file: string; series: Record<SeriesKey, IndexSeries> };
export type PredictIndex = {
  example?: boolean; contract?: string; built: string | null; tier?: string; label?: string; method_notes?: Record<string, string>;
  made_rule: string | null; band_rule: string | null; choice_rule: string | null; places: IndexPlace[];
};
export type Scored = Record<string, number | null>;
export type SummaryPart = { first_day: string | null; last_day: string | null; hours: number | null; mae: Scored; mape: Scored };
export type PlaceSeries = IndexSeries & {
  unit: string; method_note: string; made_utc: string | null; inputs_through_utc: string | null;
  band: string | null; band_coverage_pct: number | null;
  tomorrow_columns: string[]; tomorrow: Cell[][]; operator_held: string | null;
  history_columns: string[]; history: Cell[][];
  summary: { last_30_days: SummaryPart; backtest: SummaryPart };
  // the contract's additions of 26 November 2026 (its "Changes"): how many days lie between the last whole day read
  // and the target day (2 for the day-ahead forecast; more when the warehouse's series is behind), the same for the
  // demand a price forecast reads, why `tomorrow` is empty when it is, and each method's error on the days the choice
  // of a method was made on
  horizon_days?: number | null; demand_horizon_days?: number | null; tomorrow_held?: string | null;
  method_mae_last_2_years?: Record<string, number | null>;
  // session 10405: the contract's change of session 10601, the day's peak (demand only; below)
  peak?: Peak | null;
  // session 10406: the contract's separate line "with the weather known" (demand only; below)
  with_weather_known?: WeatherKnown | null;
  // session 10409: the contract's dated lines of 27 November 2026 (lib/predictlines.ts): the operator's filing checked
  // by month, the separate line with the weather forecast and net demand (demand only), and the band's record (every
  // shown series); and its line of 26 November: `tomorrow_from`, present only when the ledger already held the target
  // day, so that the forecast drawn is the one first made for it
  operator_filing?: OperatorFiling | null; with_weather_forecast?: WeatherForecast | null; net_demand?: NetDemand | null; band_coverage?: BandCoverage | null;
  tomorrow_from?: string | null;
};
/** Session 10406 (chain 720, part E): the separate line "with the weather known" (the contract's change of session
 *  10601): the regression with the region's observed temperature of the target day itself added. It reads the day's
 *  own weather, so it is not a forecast, is never the ERW forecast, and is in no chart of one; a page that shows it
 *  labels it with those words. Scored apart, on the hours its weather is held, beside the regression and the
 *  operator's forecast on the same hours: over every such hour and over the last two years. `null` for a place whose
 *  region's temperature is not held. */
export type WeatherKnown = { what?: string; region?: string; all?: SummaryPart | null; last_2_years?: SummaryPart | null };
export const WEATHER_LABEL = "With the weather known";
export const WEATHER_METHODS = ["with_weather_known", "regression", "operator"] as const;
export const WEATHER_SPANS: [keyof Pick<WeatherKnown, "last_2_years" | "all">, string][] = [["last_2_years", "The last two years"], ["all", "Every hour its weather is held"]];
/** Session 10405 (chain 720, part E): the day's peak, as the contract's change of session 10601 writes it in a place
 *  file's `series.demand.peak`: the hour of the highest ERW forecast of the day forecast now, and how each method's
 *  own highest hour of a day has compared with the day's highest hour of demand (the size of the miss, and how often
 *  the hour was the same or one away), over the last two years and over the backtest. */
export type PeakScore = { mae: number | null; mape: number | null; hour_exact_pct: number | null; hour_within_1_pct: number | null };
export type PeakSpan = { days: number | null; first_day: string | null; last_day: string | null; methods: Record<string, PeakScore | undefined> };
export type Peak = {
  what?: string;
  tomorrow?: { local_hour: number; ts_utc: string; erw: number | null; lo: number | null; hi: number | null } | null;
  last_2_years?: PeakSpan | null; backtest?: PeakSpan | null;
};
export type PlaceFile = {
  example?: boolean; contract?: string; built: string | null; tier?: string; label?: string;
  place: string; name: string; kind: "region" | "ba"; eia930: string; time: string; tables: string[];
  series: Record<SeriesKey, PlaceSeries>;
};
export type ScoresFile = {
  example?: boolean; contract?: string; built: string | null; tier?: string; label?: string; method_notes?: Record<string, string>;
  span: Record<SeriesKey, { first_day: string | null; last_day: string | null }>;
  methods: { id: string; what: string }[]; metrics: Record<string, string>; mape_rule: string | null;
  cuts: Record<string, string>; rows_columns: string[]; rows: Cell[][];
  /** session 10411 (the contract's line of session 10603): the words of the cuts of the price rows, whose `top10` is
   *  the ten days with the highest price hour and whose `spike` is the price's own; `cuts` names them by demand */
  cuts_price?: Record<string, string> | null;
};

// ---- What a reader is shown, and what is blank ----------------------------------------------------------------------

/** A series is drawn only when its file is not an example and its status is "shown" (the contract's sections 0 and 5). */
export const isShown = (file: { example?: boolean } | null, s: Pick<IndexSeries, "status"> | undefined | null): boolean =>
  !!file && file.example !== true && !!s && s.status === "shown";

/** The words a blank carries on the page, by the file's status. "license needed" is the catalogue's own phrase. */
export function blankWords(status: string | undefined | null, example = false): string {
  if (example) return "not built yet";
  switch (status) {
    case "license needed": return "license needed";
    case "paused": return "paused";
    case "too short": return "too short a history";
    case "not built": return "not built yet";
    default: return "not held";
  }
}
/** The hover of a blank: the file's own reason, else the status in a sentence. Never empty. */
export function blankWhy(s: Pick<IndexSeries, "status" | "held"> | undefined | null, example = false): string {
  if (example) return "The file on the site is the contract's example: no forecast has been written yet (docs/state/page_files_predict.md, section 5).";
  if (!s) return "The file of this place is not on the site.";
  // session 10407 (the browser read of 26 November, row FC3): the file's reason begins with its own status ("license
  // needed: PJM's prices ...", "paused: MISO's terms ..."), so the status was said twice. It is said once, and a reason
  // that ends in its own full stop gets no second one.
  const whole = (s.held ?? "").trim();
  const held = whole.toLowerCase().startsWith(`${(s.status ?? "").toLowerCase()}:`) ? whole.slice((s.status ?? "").length + 1).trim() : whole;
  if (s.status === "license needed") return `License needed: ${held && held !== "license needed" ? held.replace(/\.$/, "") : "the input is not public-licensed (docs/licenses.md)"}. Nothing of this series is shown.`;
  return held ? `${s.status}: ${held}` : s.status;
}

/** The words of a reason, short enough for a table's cell: what stands before its first colon ("not published" of "not
 *  published: no operator publishes a forecast of its day-ahead price"); the whole reason stays in the cell's hover.
 *  A reason with no such short head, or none, is "not held". */
export function shortHeld(reason: string | null | undefined, dflt = "not held"): string {
  const head = (reason ?? "").split(":")[0].trim();
  return head && head.length <= 24 ? head : dflt;
}

// ---- Names ---------------------------------------------------------------------------------------------------------

export const METHOD_WORDS: Record<string, string> = {
  erw: LABEL, operator: "Operator's forecast", yesterday: "Same hour yesterday", week_ago: "Same hour a week ago",
  regression: "Regression", flexible: "Flexible model", with_weather_known: "With the weather known",
  // session 10405: the fourth candidate of the choice rule (the contract's change of session 10601)
  regression_recent: "Regression with the recent days",
};
export const methodWords = (id: string) => METHOD_WORDS[id] ?? id.replace(/_/g, " ");
/** Session 10409: a sentence of a file that names a method by its id ("the method chosen now is regression_recent"),
 *  with the id put in the page's words; anything that is not a method's id is left as the file wrote it. */
export const plainMethods = (words: string) => words.replace(/\b[a-z]+(?:_[a-z0-9]+)+\b/g, (id) => (METHOD_WORDS[id] ? METHOD_WORDS[id].toLowerCase() : id));
/** A method's name at the head of a table's column, where its full name is on hover. The model's keeps its two words. */
export const METHOD_SHORT: Record<string, string> = { erw: LABEL, operator: "Operator", yesterday: "Yesterday", week_ago: "Week ago", regression: "Regression", flexible: "Flexible", regression_recent: "Regression, recent" };
export const methodShort = (id: string) => METHOD_SHORT[id] ?? methodWords(id);
/** The four methods the page sets side by side everywhere (the chain's list), then any other the score file names and
 *  scores for the series (a method with no row at all for a series has no column there: the flexible model of price
 *  is not a column of demand's tables). */
export const FOUR = ["erw", "operator", "yesterday", "week_ago"] as const;
export function methodsOf(scores: ScoresFile | null, series?: SeriesKey): string[] {
  const named = (scores?.methods ?? []).map((m) => m.id).filter((m) => !(FOUR as readonly string[]).includes(m));
  if (!scores || !series) return [...FOUR, ...named];
  const sc = scores.rows_columns.indexOf("series"), mc = scores.rows_columns.indexOf("method");
  const scored = new Set(scores.rows.filter((r) => r[sc] === series).map((r) => String(r[mc])));
  return [...FOUR, ...named.filter((m) => scored.has(m))];
}
export const methodWhat = (scores: ScoresFile | null, id: string): string => scores?.methods.find((m) => m.id === id)?.what ?? "";

/** The name of a place on the page: EIA's own, and its code for a balancing authority ("... (ERCO)"). */
export const placeWords = (p: Pick<IndexPlace, "name" | "kind" | "eia930">) => (p.kind === "ba" ? `${p.name} (${p.eia930})` : p.name);

// ---- Times ---------------------------------------------------------------------------------------------------------

/** "2026-11-26 07:00 CST": a UTC hour of a file in a place's clock; the hour as written when the zone cannot be read. */
export function localWords(ts: string | null | undefined, tz: string): string {
  if (!ts) return "";
  try {
    const parts = new Intl.DateTimeFormat("en-US", { timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hourCycle: "h23", timeZoneName: "short" }).formatToParts(new Date(ts));
    const p = (t: string) => parts.find((x) => x.type === t)?.value ?? "";
    return `${p("year")}-${p("month")}-${p("day")} ${p("hour")}:${p("minute")} ${p("timeZoneName")}`;
  } catch {
    return ts;
  }
}
export const utcWords = (ts: string | null | undefined) => (ts ? `${ts.slice(0, 10)} ${ts.slice(11, 16)} UTC` : "");
/** Session 10405 (the browser read of 26 November, row F2): the index's rule names the hour of the day a series'
 *  forecast is made ("The demand forecast ... is made at 20:00 UTC the day before ...; the day-ahead price forecast at
 *  14:00 UTC ..."), and a file records the hour its own forecast was made. Where the two hours differ (a build run
 *  outside its daily hour), a hover that prints both says so in a sentence between them: the hour of the rule for the
 *  series, the hour the file records, and which one the page gives. Null when they agree, or when the rule names no
 *  hour for the series or the file no hour. The reason for a difference is not in the files, and none is given. */
export function madeOffRule(madeUtc: string | null | undefined, rule: string | null | undefined, series: SeriesKey): string | null {
  const made = /^\d{4}-\d{2}-\d{2}T(\d{2}:\d{2})/.exec(madeUtc ?? "")?.[1];
  const said = new RegExp(`${series} forecast[^;.]*?\\b(\\d{1,2}:\\d{2}) UTC`, "i").exec(rule ?? "")?.[1]?.padStart(5, "0");
  if (!made || !said || made === said) return null;
  return `The file records this forecast as made at ${made} UTC, not at the rule's ${said} UTC: the hour given here is the file's.`;
}
const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const DOW = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
/** "Friday 27 Nov 2026" from "2026-11-27". */
export function dayWords(day: string | null | undefined): string {
  if (!day || !/^\d{4}-\d{2}-\d{2}$/.test(day)) return day ?? "";
  const d = new Date(`${day}T12:00:00Z`);
  return `${DOW[d.getUTCDay()]} ${d.getUTCDate()} ${MON[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
}
/** "Nov 2026" from "2026-11". */
export const monthWords = (key: string) => (/^\d{4}-\d{2}$/.test(key) ? `${MON[Number(key.slice(5, 7)) - 1]} ${key.slice(0, 4)}` : key);
/** "17:00" from 17. */
export const hourWords = (h: number | string) => `${String(h).padStart(2, "0")}:00`;

// ---- Rows ----------------------------------------------------------------------------------------------------------

export type Hour = {
  /** the row's place in the file's array (tomorrow[] or history[]), for a figure's key into the file */
  i: number;
  ts: string; day: string | null; hour: number; label: string; made: string | null; kind: string | null;
  erw: number | null; lo: number | null; hi: number | null; operator: number | null;
  actual: number | null; yesterday: number | null; week_ago: number | null;
};
const numOf = (v: Cell | undefined): number | null => (typeof v === "number" && Number.isFinite(v) ? v : null);
const strOf = (v: Cell | undefined): string | null => (typeof v === "string" && v ? v : null);

/** Rows of a file as hours, by the file's own column names (a column the file does not name is null). The label of an
 *  hour is its local hour; the second of the two 01:00 hours of the autumn clock change says so. */
function hoursOf(columns: string[], rows: Cell[][]): Hour[] {
  const at = (name: string) => columns.indexOf(name);
  const c = { ts: at("ts_utc"), day: at("local_day"), hour: at("local_hour"), made: at("made_utc"), kind: at("kind"), erw: at("erw"), lo: at("lo"), hi: at("hi"),
    operator: at("operator"), actual: at("actual"), yesterday: at("yesterday"), week_ago: at("week_ago") };
  const get = (r: Cell[], i: number) => (i < 0 ? undefined : r[i]);
  const out = rows.map((r, i) => ({ r, i })).filter(({ r }) => Array.isArray(r) && typeof get(r, c.ts) === "string").map(({ r, i }): Hour => ({
    i, ts: get(r, c.ts) as string, day: strOf(get(r, c.day)), hour: numOf(get(r, c.hour)) ?? 0, label: "", made: strOf(get(r, c.made)), kind: strOf(get(r, c.kind)),
    erw: numOf(get(r, c.erw)), lo: numOf(get(r, c.lo)), hi: numOf(get(r, c.hi)), operator: numOf(get(r, c.operator)),
    actual: numOf(get(r, c.actual)), yesterday: numOf(get(r, c.yesterday)), week_ago: numOf(get(r, c.week_ago)),
  })).sort((a, b) => (a.ts < b.ts ? -1 : a.ts > b.ts ? 1 : 0));
  const seen = new Map<string, number>();
  for (const h of out) {
    const k = `${h.day ?? ""}|${h.hour}`;
    const n = (seen.get(k) ?? 0) + 1;
    seen.set(k, n);
    h.label = n > 1 ? `${hourWords(h.hour)} (again)` : hourWords(h.hour);
  }
  return out;
}
/** Tomorrow's hours of a series (the place's target day), in time order. */
export const tomorrowOf = (s: PlaceSeries): Hour[] => hoursOf(s.tomorrow_columns ?? [], s.tomorrow ?? []);
/** Every past hour a series holds, in time order. */
export const historyOf = (s: PlaceSeries): Hour[] => hoursOf(s.history_columns ?? [], s.history ?? []);
/** The place's past days the file holds, newest first. */
export function daysOf(s: PlaceSeries): string[] {
  return [...new Set(historyOf(s).map((h) => h.day).filter((d): d is string => !!d))].sort().reverse();
}
/** The newest past day that holds both a forecast and what happened; else the newest day held; else null. */
export function defaultDay(s: PlaceSeries): string | null {
  const hs = historyOf(s);
  const full = hs.filter((h) => h.erw !== null && h.actual !== null && h.day).map((h) => h.day as string).sort();
  if (full.length) return full[full.length - 1];
  const days = daysOf(s);
  return days.length ? days[0] : null;
}

export type Extreme = { v: number; hour: Hour };
/** The highest (or lowest) held value of one column over some hours, and its hour; the first such hour on a tie. */
export function extreme(hours: Hour[], key: "erw" | "operator" | "actual", lowest = false): Extreme | null {
  let best: Extreme | null = null;
  for (const h of hours) {
    const v = h[key];
    if (v === null) continue;
    if (!best || (lowest ? v < best.v : v > best.v)) best = { v, hour: h };
  }
  return best;
}

export type DayScore = { hours: number; methods: string[]; mae: Record<string, number> };
/** One past day's mean absolute error of each method, made as the contract makes every comparison (section 3): the
 *  methods compared are those with a forecast on the day, and an hour counts only when every one of them and what
 *  happened are held. Null when no hour counts. */
export function dayScore(hours: Hour[]): DayScore | null {
  const methods = (FOUR as readonly string[]).filter((m) => hours.some((h) => h[m as "erw"] !== null));
  const used = hours.filter((h) => h.actual !== null && methods.every((m) => h[m as "erw"] !== null));
  if (!methods.length || !used.length) return null;
  const mae: Record<string, number> = {};
  for (const m of methods) mae[m] = used.reduce((s, h) => s + Math.abs((h[m as "erw"] as number) - (h.actual as number)), 0) / used.length;
  return { hours: used.length, methods, mae };
}

// ---- The report card -----------------------------------------------------------------------------------------------

/** `i`: the row's place in the score file's rows[], for a figure's key into the file. */
export type Score = { i: number; hours: number | null; mae: number | null; mape: number | null; held: string | null };
export type Metric = "mape" | "mae";
export const METRIC_WORDS: Record<Metric, string> = { mape: "Mean absolute percent error", mae: "Mean absolute error" };

/** The score rows of one place and series, by cut, key and method, with each cut's keys in the file's own order (no
 *  sorting: a period the model lost stands where the file put it). */
export function scoresOf(scores: ScoresFile | null, place: string, series: SeriesKey): Map<string, { keys: string[]; cells: Map<string, Score> }> {
  const out = new Map<string, { keys: string[]; cells: Map<string, Score> }>();
  if (!scores || scores.example === true) return out;
  const col = (n: string) => scores.rows_columns.indexOf(n);
  const c = { place: col("place"), series: col("series"), method: col("method"), cut: col("cut"), key: col("key"), hours: col("hours"), mae: col("mae"), mape: col("mape"), held: col("held") };
  for (let i = 0; i < scores.rows.length; i++) {
    const r = scores.rows[i];
    if (r[c.place] !== place || r[c.series] !== series) continue;
    const cut = String(r[c.cut] ?? ""), key = String(r[c.key] ?? ""), method = String(r[c.method] ?? "");
    const g = out.get(cut) ?? { keys: [], cells: new Map<string, Score>() };
    if (!g.keys.includes(key)) g.keys.push(key);
    g.cells.set(`${key}|${method}`, { i, hours: numOf(r[c.hours]), mae: numOf(r[c.mae]), mape: numOf(r[c.mape]), held: strOf(r[c.held]) });
    out.set(cut, g);
  }
  return out;
}
/** The cuts that are one row each (or one row an event), in the order the page lists them under the month and hour
 *  tables. `last_2_years` came with the contract's change of 26 November: the 730 days a place's method is chosen on. */
export const OTHER_CUTS = ["all", "last_2_years", "operator_sound", "operator_sound_last_2_years", "top10", "spike", "event"] as const;
export const CUT_WORDS: Record<string, string> = {
  all: "Every hour scored", last_2_years: "The last two years", top10: "The ten highest-demand days", spike: "Price spikes (hours above the grid's 99th percentile)",
  // session 10409: the cuts of 27 November 2026 (the score file's `cuts_added`): the hours of the months whose operator
  // filing passes its check, over the backtest and over the last two years
  operator_sound: "The months whose operator filing passes its check", operator_sound_last_2_years: "The last two years, the months whose filing passes",
};
/** An event's key is its address on /events ("uri-2021"); only such a key is made a link. */
export const eventHref = (key: string): string | null => (/^[a-z0-9][a-z0-9-]*$/.test(key) ? `/events/${key}` : null);

/** A cut's keys in the order a reader expects where the file's order is not one: months oldest first, hours 0 to 23. */
export function orderedKeys(cut: string, keys: string[]): string[] {
  if (cut === "month") return [...keys].sort();
  if (cut === "hour") return [...keys].sort((a, b) => Number(a) - Number(b));
  return keys;
}
/** The hours behind a row of the score table: the methods' counts where they agree, else the largest (each cell's own
 *  count is in its hover). */
export function rowHours(cells: Map<string, Score>, key: string, methods: readonly string[]): number | null {
  const hs = methods.map((m) => cells.get(`${key}|${m}`)?.hours ?? null).filter((h): h is number => h !== null);
  return hs.length ? Math.max(...hs) : null;
}

// ---- Numbers as the page writes them ------------------------------------------------------------------------------

const fixed = (v: number, d: number) => v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
/** A value in its unit: whole megawatts, dollars to the cent. */
export const valueWords = (v: number, unit: string) => (unit === "MW" ? Math.round(v).toLocaleString("en-US") : fixed(v, 2));
/** A score: an error in the series' unit as a value, a percent error with two decimals. */
export const scoreWords = (v: number, metric: Metric, unit: string) => (metric === "mape" ? fixed(v, 2) : valueWords(v, unit));
export const metricUnit = (metric: Metric, unit: string) => (metric === "mape" ? "%" : unit);

// ---- The address ---------------------------------------------------------------------------------------------------

/** `hub` (session 10411): one more hub of a place's grid, drawn whole under "More hubs", with price only. The address
 *  gives a name of a hub's form; whether the files list it for a place chosen is the page's to check. */
export type Query = { a: string | null; b: string | null; s: SeriesKey; day: string | null; m: Metric | null; hub?: string | null };
export const HUB_FORM = /^[a-z0-9-]{1,24}:[A-Za-z0-9_.-]{1,48}$/;
type Raw = Record<string, string | string[] | undefined>;
const one = (q: Raw, k: string) => (typeof q[k] === "string" ? (q[k] as string) : undefined);
export const NONE = "none";
/** What the address asks for, held to what the index offers. Place A opens on Texas where the index holds it (the
 *  first place of the first example), else on the index's first place; B is none unless named. */
export function queryOf(q: Raw, index: PredictIndex | null): Query {
  const places = index?.places ?? [];
  const has = (id: string | undefined) => !!id && places.some((p) => p.place === id);
  const a = has(one(q, "a")) ? (one(q, "a") as string) : has("region-tex") ? "region-tex" : places[0]?.place ?? null;
  const bRaw = one(q, "b");
  const b = has(bRaw) && bRaw !== a ? (bRaw as string) : null;
  const s: SeriesKey = one(q, "s") === "price" ? "price" : "demand";
  const day = /^\d{4}-\d{2}-\d{2}$/.test(one(q, "day") ?? "") ? (one(q, "day") as string) : null;
  // a metric is kept only where it differs from the series' own, so a reader who changes the series without touching
  // the metric gets that series' own (the form sends the metric with every choice)
  const asked = one(q, "m") === "mae" ? "mae" : one(q, "m") === "mape" ? "mape" : null;
  const m = asked && asked !== metricDefault(s) ? asked : null;
  const hubRaw = one(q, "hub");
  const hub = s === "price" && hubRaw && HUB_FORM.test(hubRaw) ? hubRaw : null;
  return { a, b, s, day, m, hub };
}
/** The metric a series opens on: percent error for demand, error in USD/MWh for price (a percent of a price near zero
 *  is not defined: the score file's `mape_rule`). */
export const metricDefault = (s: SeriesKey): Metric => (s === "price" ? "mae" : "mape");
export const metricOf = (q: Query): Metric => q.m ?? metricDefault(q.s);
/** The page's address for a state, leaving out what is the default. */
export function hrefOf(q: Query, patch: Partial<Query> = {}, hash = ""): string {
  const x = { ...q, ...patch };
  const p = new URLSearchParams();
  if (x.a && x.a !== "region-tex") p.set("a", x.a);
  if (x.b) p.set("b", x.b);
  if (x.s !== "demand") p.set("s", x.s);
  if (x.day) p.set("day", x.day);
  if (x.m) p.set("m", x.m);
  if (x.hub && x.s === "price") p.set("hub", x.hub);
  const s = p.toString();
  return `/forecast${s ? `?${s}` : ""}${hash}`;
}

// ---- Downloads -----------------------------------------------------------------------------------------------------

const cell = (c: Cell | undefined) => (c === null || c === undefined ? "" : /[",\n]/.test(String(c)) ? `"${String(c).replace(/"/g, '""')}"` : String(c));
const lines = (head: string[], rows: (Cell | undefined)[][]) => [head, ...rows].map((r) => r.map(cell).join(",")).join("\n") + "\n";

export const ROWS_HEAD = ["place", "series", "unit", "part", "ts_utc", "local_day", "local_hour", "made_utc", "kind", "erw_forecast", "band_low", "band_high",
  "operator_forecast", "actual", "same_hour_yesterday", "same_hour_week_ago"];
/** A place's hours as a CSV: tomorrow's forecast and every past hour held, both series, with the provenance first. A
 *  series that is not shown has no line, and the header says why. */
export function rowsCsv(file: PlaceFile, url: string): string {
  const head = [
    `# Energy Research Warehouse (ERW): the ERW forecast for ${placeWords(file)}, hour by hour (site/lib/predict.ts rowsCsv)`,
    "# ERW forecast: a model's output (tier derived), never a published or official figure. operator_forecast is the operator's own, as published.",
    `# Built: ${file.built ?? "not built"} (site/data/predict/${file.place}.json, written by warehouse/predict/run.py and backtest.py from the ERW's tables: ${(file.tables ?? []).join(", ") || "none named"})`,
    "# Methods: docs/methods/predict.md (demand), docs/methods/predict_price.md (price). Contract: docs/state/page_files_predict.md",
    `# Times: ts_utc is the start of an hour, UTC; local_day and local_hour are in the place's clock (${file.time}). part: tomorrow (the day forecast now) or history (a past day, with what happened)`,
    `# From: ${url}`,
  ];
  const rows: (Cell | undefined)[][] = [];
  for (const k of SERIES) {
    const s = file.series?.[k];
    if (!isShown(file, s)) { head.push(`# ${k}: no line. ${blankWhy(s, file.example === true)}`); continue; }
    head.push(`# ${k}: ${s.unit}; made ${s.made_utc ?? "not said"}; method ${s.method ?? "not said"}; band: ${s.band ?? "not said"}${k === "price" && s.hub ? `; hub ${s.hub}, ${s.market ?? ""}` : ""}`);
    for (const h of tomorrowOf(s)) rows.push([file.place, k, s.unit, "tomorrow", h.ts, s.target_day, h.hour, s.made_utc, "live", h.erw, h.lo, h.hi, h.operator, null, null, null]);
    for (const h of historyOf(s)) rows.push([file.place, k, s.unit, "history", h.ts, h.day, h.hour, h.made, h.kind, h.erw, h.lo, h.hi, h.operator, h.actual, h.yesterday, h.week_ago]);
  }
  return `${head.join("\n")}\n${lines(ROWS_HEAD, rows)}`;
}

export const SCORES_HEAD = ["place", "series", "method", "cut", "key", "hours", "mae", "mape", "held"];
/** The report card as a CSV: every row of the score file, as the file holds it, with the provenance first. */
export function scoresCsv(scores: ScoresFile, url: string): string {
  const head = [
    "# Energy Research Warehouse (ERW): the ERW forecast's report card, every place, method, series and cut (site/lib/predict.ts scoresCsv)",
    "# ERW forecast: a model's output (tier derived). Every method is scored on the same hours within a row's place and cut; hours is the count",
    `# Built: ${scores.built ?? "not built"} (site/data/predict/scores.json, written by warehouse/predict/backtest.py)`,
    `# Backtest: demand ${scores.span?.demand?.first_day ?? "?"} to ${scores.span?.demand?.last_day ?? "?"}; price ${scores.span?.price?.first_day ?? "?"} to ${scores.span?.price?.last_day ?? "?"}`,
    `# mae: ${scores.metrics?.mae ?? "mean absolute error, in the series' unit"}. mape: ${scores.metrics?.mape ?? "mean absolute percent error, in percent"}${scores.mape_rule ? `. ${scores.mape_rule}` : ""}`,
    ...(scores.methods ?? []).map((m) => `# method ${m.id}: ${m.what}`),
    // session 10405: the rows of the day's peak (the contract's change of session 10601) count days, not hours
    ...((scores.rows ?? []).some((r) => r[scores.rows_columns.indexOf("series")] === "demand_peak") ? ["# series demand_peak: each method's highest hour of a day against the day's highest hour of demand; in these rows hours holds the count of days"] : []),
    // session 10406: the rows of the separate line are not a forecast's, and the file's own words say what they are
    ...((scores.rows ?? []).some((r) => r[scores.rows_columns.indexOf("series")] === "demand_weather_known") ? [`# series demand_weather_known: not a forecast. ${(scores as { separate_lines?: Record<string, string> | null }).separate_lines?.with_weather_known ?? "the regression with the target day's own observed temperature added, scored apart on the hours its weather is held"}`] : []),
    `# From: ${url}`,
  ];
  const at = SCORES_HEAD.map((n) => scores.rows_columns.indexOf(n));
  const rows = scores.example === true ? [] : scores.rows.map((r) => at.map((i) => (i < 0 ? null : r[i])));
  return `${head.join("\n")}\n${lines(SCORES_HEAD, rows)}`;
}

// ---- Session 10405 (chain 720, part E): the day's peak, and the days after tomorrow ----------------------------------

/** The two spans the peak is scored over, in the file's own names, with the page's words. */
export const PEAK_SPANS: [keyof Pick<Peak, "last_2_years" | "backtest">, string][] = [["last_2_years", "The last two years"], ["backtest", "The backtest"]];
/** How often a method's highest hour of a day was the day's highest hour of demand, and how often one hour away. */
export const PEAK_HOURS: [keyof Pick<PeakScore, "hour_exact_pct" | "hour_within_1_pct">, string, string][] = [
  ["hour_exact_pct", "its hour, exactly", "the share of days on which the method's highest hour was the hour of the day's highest demand, in percent of the days scored"],
  ["hour_within_1_pct", "its hour, within one", "the share of days on which the method's highest hour was the hour of the day's highest demand or one hour from it, in percent of the days scored"],
];
/** A share of days, as the page writes it. */
export const pctWords = (v: number) => fixed(v, 2);

/** The file of the days after tomorrow (site/data/predict/ahead.json; the contract's change of session 10601): for each
 *  place, the demand forecast at each horizon from three to seven days after the last whole day read. A horizon is
 *  `shown` only where, over the last two years, its method beat the same hour a week ago; one that is not carries the
 *  reason in `held` and no forecast. */
export type AheadScore = Record<string, number | null>;
export type AheadHorizon = {
  horizon_days: number; days_after_tomorrow: number; target_day: string; shown: boolean; held: string | null; method?: string;
  last_2_years?: { hours: number | null; mae: AheadScore; mape: AheadScore; operator_day_ahead_mae_same_hours?: number | null } | null;
  band_coverage_pct?: number | null; forecast_columns: string[]; forecast: Cell[][] | null;
};
export type AheadPlace = { place: string; time: string; last_whole_day: string | null; horizons: AheadHorizon[] };
export type AheadFile = {
  example?: boolean; contract?: string; built: string | null; tier?: string; label?: string; method_notes?: Record<string, string>;
  made_utc?: string | null; what?: string | null; places: AheadPlace[];
};

/** A place's entry in the file of the days ahead, with its position there (a figure's key names it), or null. */
export function aheadOf(file: AheadFile | null, place: string): { pi: number; place: AheadPlace } | null {
  if (!file || file.example === true) return null;
  const pi = (file.places ?? []).findIndex((p) => p.place === place);
  return pi < 0 ? null : { pi, place: file.places[pi] };
}
/** The horizon's method: the one the file names, the regression where it names none (its first build). */
export const aheadMethod = (h: AheadHorizon): string => h.method ?? "regression";

export type AheadDay = {
  hi: number; h: AheadHorizon; method: string;
  hours: { i: number; ts: string; hour: number; label: string; erw: number | null; lo: number | null; hi: number | null }[];
  top: { v: number; i: number; hour: number; ts: string } | null; low: { v: number; i: number; hour: number; ts: string } | null;
};
/** The days after tomorrow of a place, the nearest first: every horizon the file holds that lies after the place's own
 *  target day (the file's first horizon is that day itself when the place's series is a day behind: the place's own
 *  file draws it, so it is not drawn twice), each with its hours when it is shown, and its highest and lowest hour. */
export function aheadDays(place: AheadPlace, tomorrow: string | null | undefined): AheadDay[] {
  return (place.horizons ?? []).map((h, hi) => ({ h, hi })).filter(({ h }) => (tomorrow ? h.target_day > tomorrow : h.days_after_tomorrow >= 1))
    .sort((a, b) => a.h.target_day.localeCompare(b.h.target_day))
    .map(({ h, hi }) => {
      const at = (n: string) => (h.forecast_columns ?? []).indexOf(n);
      const num = (r: Cell[], n: string) => { const v = r[at(n)]; return typeof v === "number" && Number.isFinite(v) ? v : null; };
      const hours = h.shown && h.forecast ? h.forecast.map((r, i) => {
        const hour = Number(r[at("local_hour")]);
        return { i, ts: String(r[at("ts_utc")]), hour, label: hourWords(hour), erw: num(r, "erw"), lo: num(r, "lo"), hi: num(r, "hi") };
      }) : [];
      const held = hours.filter((x) => x.erw !== null);
      const pick = (lowest: boolean) => (held.length ? held.reduce((a, b) => ((lowest ? (b.erw as number) < (a.erw as number) : (b.erw as number) > (a.erw as number)) ? b : a)) : null);
      const as = (x: (typeof hours)[number] | null) => (x ? { v: x.erw as number, i: x.i, hour: x.hour, ts: x.ts } : null);
      return { hi, h, method: aheadMethod(h), hours, top: as(pick(false)), low: as(pick(true)) };
    });
}

export const AHEAD_HEAD = ["place", "target_day", "days_after_last_whole_day", "ts_utc", "local_hour", "method", "erw_forecast", "band_low", "band_high"];
/** The days ahead as a CSV: every hour of every horizon shown, every place, with the provenance first. A horizon that
 *  is not shown has no line, and the header counts them. */
export function aheadCsv(file: AheadFile, url: string): string {
  const rows: (Cell | undefined)[][] = [];
  let hidden = 0;
  for (const p of file.example === true ? [] : file.places ?? []) for (const h of p.horizons ?? []) {
    if (!h.shown || !h.forecast) { hidden += 1; continue; }
    const at = (n: string) => h.forecast_columns.indexOf(n);
    for (const r of h.forecast) rows.push([p.place, h.target_day, h.horizon_days, r[at("ts_utc")], r[at("local_hour")], aheadMethod(h), r[at("erw")], r[at("lo")], r[at("hi")]]);
  }
  const head = [
    "# Energy Research Warehouse (ERW): the ERW forecast of demand for the days ahead, hour by hour, every place (site/lib/predict.ts aheadCsv)",
    "# ERW forecast: a model's output (tier derived), never a published or official figure. Demand in MW.",
    `# Built: ${file.built ?? "not built"}; made ${file.made_utc ?? "not said"} (site/data/predict/ahead.json, written by warehouse/predict/ahead.py)`,
    `# What: ${file.what ?? "the demand forecast at each horizon after the day-ahead one"}`,
    "# days_after_last_whole_day: the days between the last whole day of demand read and the day forecast (the file's horizon_days). ts_utc is the start of an hour, UTC; local_hour is in the place's clock",
    `# A horizon is in this file only where its method beat the same hour a week ago over the last two years; horizons left out: ${hidden}`,
    "# Method: docs/methods/predict.md. Contract: docs/state/page_files_predict.md",
    `# From: ${url}`,
  ];
  return `${head.join("\n")}\n${lines(AHEAD_HEAD, rows)}`;
}
