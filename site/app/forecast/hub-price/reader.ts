// Session 10411 (chain 720, part E): what the readers of /forecast/hub-price need to know of its columns
// (lib/predictlines.ts HUB_HEAD), in one place for the Python and the Stata route.
import type { ReaderSpec } from "@/lib/csvreader";

export const HUB_READER: ReaderSpec = {
  what: "the ERW forecast of the day-ahead price at one more hub, hour by hour, as /forecast draws it",
  by: "site/lib/predictlines.ts hubCsv",
  text: ["hub", "part", "ts_utc", "local_day", "made_utc", "kind"],
  figures: ["local_hour", "erw_forecast", "band_low", "band_high", "actual", "same_hour_yesterday", "same_hour_week_ago"],
  show: ["part", "ts_utc", "erw_forecast", "band_low", "band_high", "actual"],
  count: "part",
  name: "hub_price",
};
