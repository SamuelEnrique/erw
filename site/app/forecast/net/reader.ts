// Session 10410 (chain 720, part E): what the readers of /forecast/net need to know of its columns (lib/predictlines.ts
// NET_HEAD), in one place for the Python and the Stata route.
import type { ReaderSpec } from "@/lib/csvreader";

export const NET_READER: ReaderSpec = {
  what: "the ERW forecast of net demand, wind and solar for a place, hour by hour, as /forecast draws it",
  by: "site/lib/predictlines.ts netCsv",
  text: ["place", "line", "part", "ts_utc", "local_day"],
  figures: ["local_hour", "erw_forecast", "band_low", "band_high", "operator_forecast", "actual", "same_hour_yesterday"],
  show: ["line", "part", "ts_utc", "erw_forecast", "band_low", "band_high", "operator_forecast", "actual"],
  count: "line",
  name: "net",
};
