// Energy Research Warehouse (ERW) site, session 1413 (chain 107): the arithmetic the energy mix views
// (components/mix/views.tsx) apply to the committed files' arrays, moved here as it stood in the views, so the page and
// scripts/check-values.mjs apply one rule. No import: node runs this file with its types stripped, and
// scripts/check-filecalc.mjs imports it (with lib/mix2.ts, whose acrossYears, periodOf and highest the duck view and the
// average day already called) to recompute the filecalc| keys from the file in the repository. A node test holds each
// function to the expression that stood in the view, on every committed file (scripts/test-mix-view-calc.mjs).
//
// The key kind, filecalc|<function>|<data file>|<args>..., always behind fmt|<form>| (scripts/check-format.mjs):
//   duck_solar_peak|mix/<grid>.json|<cal>|<year>    the month's average day: solar at its peak hour, MW (lib/mix2.ts acrossYears)
//   duck_low|mix/<grid>.json|<cal>|<year>           net load's midday low, 09:00 to 16:00, MW (acrossYears)
//   duck_evening|mix/<grid>.json|<cal>|<year>       net load's evening high, from 16:00, MW (acrossYears)
//   duck_ramp|mix/<grid>.json|<cal>|<year>          the ramp between them, MW, when the low comes first (acrossYears)
//   day_peak|mix/<grid>.json|<period>|<solar|wind>  a month's or a year's average day: the source at its peak hour, MW
//                                                   (lib/mix2.ts highest over periodOf's avg)
//   hist_share|mix_history.json|<state>|<year>|<fuel>  the fuel's share of the state's net generation in the year, percent (historyCell)
//   hist_mwh|mix_history.json|<state>|<year>|<fuel>    the fuel's net generation in the year, million MWh (historyCell)
//   avail_mean|mixplus/<grid>.json|<year>|<season>|<fuel>  the mean of the 24 hours' availability, percent (availMean)
//   avail_min|...                                   the lowest hour (availMin)
//   avail_max|...                                   the highest hour (availMax)
//   clean_day_max|clean/<grid>.json|<month>         session 1414: the carbon-free share in the cleanest hour of the month's
//                                                   average day, percent (cleanDayMax)
//   clean_day_min|clean/<grid>.json|<month>         session 1414: the share in its dirtiest hour, percent (cleanDayMin)
//   carbon_left_out_n|carbon_left_out.json|<variable>  session 1415: the months of carbon_intensity_monthly the Clean tab's
//                                                   "Monthly since 2018" leaves out for the variable (session 118's rule,
//                                                   warehouse/derived/carbon_left_out.py), a count (leftOutCount)
// <cal> is a calendar month "01" to "12"; <period> is "YYYY-MM" or "YYYY"; <season> is winter, spring, summer, autumn or all;
// <month> is "YYYY-MM".

/** The function of each filecalc| key: the rule it applies and what its figure is, in words (the figure's tip). */
export const FILECALC = {
  duck_solar_peak: { rule: "lib/mix2.ts acrossYears", what: "solar at its peak hour of the month's average day, MW" },
  duck_low: { rule: "lib/mix2.ts acrossYears", what: "net load's midday low (09:00 to 16:00) of the month's average day, MW" },
  duck_evening: { rule: "lib/mix2.ts acrossYears", what: "net load's evening high (from 16:00) of the month's average day, MW" },
  duck_ramp: { rule: "lib/mix2.ts acrossYears", what: "the ramp from the midday low to the evening high, MW" },
  day_peak: { rule: "lib/mix2.ts highest", what: "the source at its peak hour of the average day, MW" },
  hist_share: { rule: "lib/mixViewCalc.ts historyCell", what: "the fuel's share of the state's net generation in the year, percent" },
  hist_mwh: { rule: "lib/mixViewCalc.ts historyCell", what: "the fuel's net generation in the year, million MWh" },
  avail_mean: { rule: "lib/mixViewCalc.ts availMean", what: "output as a share of installed capacity, the mean of the day's 24 hours, percent" },
  avail_min: { rule: "lib/mixViewCalc.ts availMin", what: "output as a share of installed capacity, the day's lowest hour, percent" },
  avail_max: { rule: "lib/mixViewCalc.ts availMax", what: "output as a share of installed capacity, the day's highest hour, percent" },
  clean_day_max: { rule: "lib/mixViewCalc.ts cleanDayMax", what: "the carbon-free share of generation in the cleanest hour of the month's average day, percent" },
  clean_day_min: { rule: "lib/mixViewCalc.ts cleanDayMin", what: "the carbon-free share of generation in the dirtiest hour of the month's average day, percent" },
  carbon_left_out_n: { rule: "lib/mixViewCalc.ts leftOutCount", what: "the months of carbon_intensity_monthly the chart leaves out for the variable (session 118's rule), a count" },   // session 1415
} as const;
export type FilecalcFn = keyof typeof FILECALC;

/** The key of a figure computed from a committed file by one of the functions above. */
export const filecalcKey = (fn: FilecalcFn, file: string, args: string[]): string => `filecalc|${fn}|${file}|${args.join("|")}`;

/** Where a committed file's figures come from, for a tip: the live-set table it is a build of, or the builder that writes it. */
export function sourceOf(file: string): string {
  const m = /^mix\/([a-z]+)\.json$/.exec(file);
  if (m) return `generation_mix_hourly_profile, iso:${m[1]}`;
  if (file === "mix_history.json") return "state_generation_mix_monthly by year (warehouse/derived/mix_views.py)";
  const c = /^clean\/([a-z]+)\.json$/.exec(file);   // session 1414: the clean files, the site's copy of clean_energy_summary
  if (c) return `clean_energy_summary, iso:${c[1]}`;
  if (file === "carbon_left_out.json") return "warehouse/derived/carbon_left_out.py";   // session 1415: the months the carbon chart leaves out
  return "warehouse/derived/mix_views.py";
}

// ---- since 2001: net generation by state and fuel (HistoryView), the file site/data/mix_history.json

/** The shape of mix_history.json the arithmetic reads: each state's years, each a row of MWh by fuel and its months held. */
export type HistoryLike = { fuels: string[]; states: Record<string, Record<string, Record<string, number>>> };

/** A state's net generation in a year: the sum over the file's fuels of the year's MWh, a fuel not listed counted 0. */
export function historyTotal(h: HistoryLike, s: string, y: string): number {
  return h.fuels.reduce((a, f) => a + (h.states[s]?.[y]?.[f] ?? 0), 0);
}

/** A cell of a state's table of shares: the fuel's share of the year's total, percent, and its MWh in millions; both
 *  null when the year does not hold twelve months or does not list the fuel. */
export function historyCell(h: HistoryLike, s: string, y: string, f: string): { share: number | null; mwh: number | null } {
  const r = h.states[s]?.[y];
  const v = r?.months === 12 ? r[f] : undefined;
  return { share: v === undefined ? null : (100 * v) / historyTotal(h, s, y), mwh: v === undefined ? null : v / 1e6 };
}

// ---- availability by source (SupplyView), the files site/data/mixplus/<grid>.json

/** The shape of a mixplus file the arithmetic reads: by year, by season, by fuel, the 24 local hours' availability. */
export type AvailabilityLike = { availability: Record<string, Record<string, Record<string, number[]>>> };

/** The 24 hours of a fuel's availability for a year and a season, or undefined when the file does not hold them. */
export const availOf = (p: AvailabilityLike, year: string, season: string, fuel: string): number[] | undefined => p.availability[year]?.[season]?.[fuel];
/** The mean of the hours, or null when there are none. */
export const availMean = (v: number[] | null | undefined): number | null => (v ? v.reduce((a, b) => a + b, 0) / v.length : null);
/** The lowest hour, or null. */
export const availMin = (v: number[] | null | undefined): number | null => (v ? Math.min(...v) : null);
/** The highest hour, or null. */
export const availMax = (v: number[] | null | undefined): number | null => (v ? Math.max(...v) : null);

// ---- session 1414: how clean, and when (CleanView), the files site/data/clean/<grid>.json

/** The shape of a clean file the arithmetic reads: by month, the average day's 24 local hours of carbon-free share. */
export type CleanLike = { months: Record<string, Record<string, unknown> | undefined> };

/** The hours of a month's average day the file holds, its unheld hours left out: lib/clean.ts dayOf (24 values, else
 *  none) with the filter that stood in the view's table of the cleanest hours by month. */
export function cleanDayHeld(f: CleanLike, m: string): number[] {
  const d = f.months[m]?.day;
  const day = Array.isArray(d) && d.length === 24 ? d.map((v) => (typeof v === "number" && Number.isFinite(v) ? v : null)) : [];
  return day.filter((x): x is number => x !== null);
}
/** The share in the month's cleanest hour, or null when no hour is held. */
export const cleanDayMax = (f: CleanLike, m: string): number | null => { const d = cleanDayHeld(f, m); return d.length ? Math.max(...d) : null; };
/** The share in the month's dirtiest hour, or null when no hour is held. */
export const cleanDayMin = (f: CleanLike, m: string): number | null => { const d = cleanDayHeld(f, m); return d.length ? Math.min(...d) : null; };

// ---- session 1415: the months the Clean tab's "Monthly since 2018" leaves out, the file site/data/carbon_left_out.json

/** The shape of carbon_left_out.json the count reads: the months left out, each with its variable. */
export type LeftOutLike = { months: { variable: string }[] };

/** The months left out for one variable: lib/carbonLeftOut.ts carbonLeftOutMonths(variable).length, the figure the
 *  chart's note writes ("Left out of this chart: <n> months the table still holds"). */
export const leftOutCount = (f: LeftOutLike, variable: string): number => f.months.filter((m) => m.variable === variable).length;
