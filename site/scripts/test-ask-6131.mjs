// Energy Research Warehouse (ERW) site, session 6131 (chain 281): a period outside a table's own span
// (lib/chat/window.ts spanOutside, as warehouse/chat/window.py span_outside). No model, no request.
//
//   node scripts/test-ask-6131.mjs
//
// Prints one JSON line of what the function returns for each case; tests/test_session6131_ask.py sets the line against
// the Python function on the same cases, so the two languages agree.
import assert from "node:assert/strict";
import fs from "node:fs";
import { SPAN_OUTSIDE, spanOutside } from "../lib/chat/window.ts";

const FIRST = "2026-08-18T00:00:00Z", LAST = "2026-11-13T00:00:00Z";
export const CASES = [
  ["march", "2026-03-01T00:00:00Z", "2026-04-01T00:00:00Z"],          // wholly before: the new tables' ch09
  ["october", "2026-10-01T00:00:00Z", "2026-11-01T00:00:00Z"],        // inside
  ["across_the_first_day", "2026-08-01T00:00:00Z", "2026-09-01T00:00:00Z"],
  ["ends_on_the_first_day", "2026-08-01T00:00:00Z", "2026-08-18T00:00:00Z"],   // end is exclusive: nothing of the span is asked
  ["starts_on_the_last_day", "2026-11-13T00:00:00Z", "2026-12-01T00:00:00Z"],  // the last day itself is asked
  ["after", "2026-11-14T00:00:00Z", "2027-01-01T00:00:00Z"],
  ["open_start_before", null, "2026-01-01T00:00:00Z"],
  ["open_end_after", "2027-01-01T00:00:00Z", null],
  ["open_end_inside", "2026-09-01T00:00:00Z", null],
  ["no_bound", null, null],
];
const got = Object.fromEntries(CASES.map(([id, a, b]) => [id, spanOutside(a, b, FIRST, LAST)]));
console.log(JSON.stringify({ got, note: SPAN_OUTSIDE }));
const outside = ["march", "ends_on_the_first_day", "after", "open_start_before", "open_end_after"];
for (const [id] of CASES) {
  if (outside.includes(id)) assert.deepEqual(got[id], { first: FIRST, last: LAST, outside: true, note: SPAN_OUTSIDE }, id);
  else assert.equal(got[id], null, id);
}
// a span or a bound that cannot be read gives nothing, never a guess
assert.equal(spanOutside("2026-03-01T00:00:00Z", "2026-04-01T00:00:00Z", null, LAST), null);
assert.equal(spanOutside("not a time", "2026-04-01T00:00:00Z", FIRST, LAST), null);
assert.equal(spanOutside("2026-03-01T00:00:00Z", "2026-04-01T00:00:00Z", LAST, FIRST), null);
assert.match(SPAN_OUTSIDE, /is not a count of zero\. Answer with not_in_warehouse true/);
const tools = fs.readFileSync(new URL("../lib/chat/tools.ts", import.meta.url), "utf8");
assert.match(tools, /if \(shape !== "series" && !dcol && a\.day === undefined && \(a\.start \|\| a\.end\)\) \{/);
assert.match(tools, /if \(s\) out\.span = s;/);
console.log("test-ask-6131: ok");
