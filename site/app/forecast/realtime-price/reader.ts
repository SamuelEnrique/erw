// Session 10410 (chain 720, part E): what the readers of /forecast/realtime-price need to know of its columns
// (lib/predictlines.ts RT_HEAD), in one place for the Python and the Stata route.
import type { ReaderSpec } from "@/lib/csvreader";

export const RT_READER: ReaderSpec = {
  what: "the ERW forecast of the real-time price at a hub, hour by hour, as /forecast draws it",
  by: "site/lib/predictlines.ts rtCsv",
  text: ["hub", "part", "ts_utc", "local_day"],
  figures: ["local_hour", "erw_forecast", "band_low", "band_high", "day_ahead_price", "actual", "same_hour_two_days_before"],
  show: ["part", "ts_utc", "erw_forecast", "band_low", "band_high", "day_ahead_price", "actual"],
  count: "part",
  name: "real_time",
};
