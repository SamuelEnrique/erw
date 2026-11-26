// Session 10401 (chain 720, part C): what the readers of /forecast/ledger need to know of its columns (the contract's
// change of 26 November 2026 names them), in one place for the Python and the Stata route.
import type { ReaderSpec } from "@/lib/csvreader";

export const LEDGER_HEAD = ["series", "place", "target_day", "ts_utc", "local_hour", "made_utc", "inputs_through_utc", "horizon_days", "method", "erw", "lo", "hi"];
export const LEDGER_READER: ReaderSpec = {
  what: "the ERW forecast's ledger, every forecast as made on its day, never rewritten",
  by: "warehouse/predict/run.py, served as written by /forecast/ledger",
  text: ["series", "place", "target_day", "ts_utc", "made_utc", "inputs_through_utc", "method"],
  figures: ["local_hour", "horizon_days", "erw", "lo", "hi"],
  show: ["place", "target_day", "ts_utc", "made_utc", "method", "erw", "lo", "hi"],
  count: "method",
  name: "ledger",
};
