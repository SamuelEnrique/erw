// Session 10401 (chain 720, part C): what the readers of /forecast/scores need to know of its columns (lib/predict.ts
// SCORES_HEAD), in one place for the Python and the Stata route.
import type { ReaderSpec } from "@/lib/csvreader";

export const SCORES_READER: ReaderSpec = {
  what: "the ERW forecast's report card, every place, method, series and cut, as /forecast draws it",
  by: "site/lib/predict.ts scoresCsv",
  text: ["place", "series", "method", "cut", "key", "held"],
  figures: ["hours", "mae", "mape"],
  show: ["place", "series", "method", "cut", "key", "hours", "mae", "mape"],
  count: "method",
  name: "scores",
};
