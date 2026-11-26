// Session 10405 (chain 720, part E): what the readers of /forecast/ahead need to know of its columns (lib/predict.ts
// AHEAD_HEAD), in one place for the Python and the Stata route.
import type { ReaderSpec } from "@/lib/csvreader";

export const AHEAD_READER: ReaderSpec = {
  what: "the ERW forecast of demand for the days after tomorrow, every place, hour by hour, as /forecast draws it",
  by: "site/lib/predict.ts aheadCsv",
  text: ["place", "target_day", "ts_utc", "method"],
  figures: ["days_after_last_whole_day", "local_hour", "erw_forecast", "band_low", "band_high"],
  show: ["place", "target_day", "local_hour", "erw_forecast", "band_low", "band_high"],
  count: "place",
  name: "ahead",
};
