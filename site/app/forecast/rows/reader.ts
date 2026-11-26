// Session 10401 (chain 720, part C): what the readers of /forecast/rows need to know of its columns (lib/predict.ts
// ROWS_HEAD), in one place for the Python and the Stata route.
import type { ReaderSpec } from "@/lib/csvreader";

export const ROWS_READER: ReaderSpec = {
  what: "the ERW forecast for a place, hour by hour, as /forecast draws it",
  by: "site/lib/predict.ts rowsCsv",
  text: ["place", "series", "unit", "part", "ts_utc", "local_day", "made_utc", "kind"],
  figures: ["local_hour", "erw_forecast", "band_low", "band_high", "operator_forecast", "actual", "same_hour_yesterday", "same_hour_week_ago"],
  show: ["series", "part", "ts_utc", "erw_forecast", "band_low", "band_high", "operator_forecast", "actual"],
  count: "part",
  name: "forecast",
};
