// Energy Research Warehouse (ERW) site, session 1166 (chain 078): the arithmetic of the Mix tab's "Yesterday" block
// (components/grid/Conditions.tsx GridYesterday) that no key recomputed until now, as pure functions the page and
// scripts/check-values.mjs both call, so a key is recomputed by the page's own rule:
//   fcerr|mape|<entity>|<from>|<to>    the day's mean absolute forecast error, percent of demand (forecastMiss().mape)
//   fcerr|hours|<entity>|<from>|<to>   the hours that hold both demand and the day-ahead forecast (forecastMiss().hours)
//   degday|<cdd|hdd>|<entity>|<day>    a UTC day's degree days at the load center's station, base 65 F, from its 24
//                                      hourly mean temperatures (degreeDay(); a day with another count has none)
// The rows are eia930_all_demand's demand_mw and demand_forecast_mw for <entity> in [from, to), and
// weather_obs_hourly's temperature_f for <entity> (nws:<station>) in the UTC day. No import: node runs this file with
// its types stripped (scripts/check-values.mjs, scripts/test-grid-file-keys.mjs).

export type Row = { ts_utc: string; value: number };

/** Degree days: the US convention, base 65 degrees F. */
export const BASE_F = 65;

/** The day's forecast miss: the mean over the hours that hold both of |demand - forecast| / demand, in percent, and
 *  the count of those hours (null mean when none). Each hour's forecast is the last row of that hour. */
export function forecastMiss(demand: Row[], forecast: Row[]): { mape: number | null; hours: number } {
  const fc = new Map(forecast.map((x) => [x.ts_utc, x.value]));
  const pairs = demand.filter((x) => fc.has(x.ts_utc));
  const mape = pairs.length ? (100 * pairs.reduce((a, x) => a + Math.abs(x.value - fc.get(x.ts_utc)!) / x.value, 0)) / pairs.length : null;
  return { mape, hours: pairs.length };
}

/** A UTC day's mean temperature from its hourly rows, and how many rows it had (mean 0 when none). */
export function dayMean(temps: Row[]): { n: number; mean: number } {
  return { n: temps.length, mean: temps.length ? temps.reduce((a, x) => a + x.value, 0) / temps.length : 0 };
}

/** The day's degree days, cooling at or above the base and heating below it; null unless the day holds 24 hours. */
export function degreeDay(temps: Row[]): { kind: "cdd" | "hdd"; value: number } | null {
  const { n, mean } = dayMean(temps);
  if (n !== 24) return null;
  return mean >= BASE_F ? { kind: "cdd", value: mean - BASE_F } : { kind: "hdd", value: BASE_F - mean };
}
