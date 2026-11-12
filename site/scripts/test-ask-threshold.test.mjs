// Energy Research Warehouse (ERW) site, session 3297: the query tool's value threshold (lib/chat/threshold.ts), as
// warehouse/chat/tools.py reads it (tests/test_session3297_ask.py holds the same cases on the Python side). No build,
// no network: node strips the file's types.
//
//   node --test site/scripts/test-ask-threshold.test.mjs
import test from "node:test";
import assert from "node:assert/strict";
import { ThresholdError, applyThreshold, readThreshold } from "../lib/chat/threshold.ts";

// session 1300's fixture: ERCOT's hub average peak premium by year, 2015 to 2026
const VALUES = [-0.16, 0.03, 0.09, 0.255, 0.49, 0.57, 3.135, 13.65, 6.495, 8.93, 14.52, 12.29];
const rows = VALUES.map((v, i) => ({ t: `${2015 + i}-01-01T00:00:00Z`, v }));

test("no threshold reads as null", () => {
  assert.equal(readThreshold(undefined), null);
  assert.equal(readThreshold(null), null);
});

test("above, below and a band", () => {
  assert.equal(applyThreshold(rows, readThreshold({ above: 10 }), "value").kept.length, 3);
  assert.equal(applyThreshold(rows, readThreshold({ below: 0 }), "value").kept.length, 1);
  assert.deepEqual(applyThreshold(rows, readThreshold({ above: 1, below: 10 }), "value").kept.map((r) => r.v), [3.135, 6.495, 8.93]);
});

test("strictly past the figure", () => {
  assert.equal(applyThreshold(rows, readThreshold({ above: 14.52 }), "value").kept.length, 0);
  assert.equal(applyThreshold(rows, readThreshold({ below: -0.16 }), "value").kept.length, 0);
});

test("a row with no value is never kept", () => {
  const some = [...rows, { t: "2027-01-01T00:00:00Z", v: null }, { t: "2028-01-01T00:00:00Z", v: Number.NaN }];
  const { kept, field } = applyThreshold(some, readThreshold({ above: -100 }), "value");
  assert.equal(kept.length, 12);
  assert.equal(field.rows_in_window, 14);
});

test("the answer's field: the same keys, in the same order, as tools.py", () => {
  const { field } = applyThreshold(rows, readThreshold({ above: 10 }), "value");
  assert.deepEqual(Object.keys(field), ["column", "above", "rows_in_window", "rows_kept", "note"]);
  assert.deepEqual({ ...field, note: undefined }, { column: "value", above: 10, rows_in_window: 12, rows_kept: 3, note: undefined });
  const band = applyThreshold(rows, readThreshold({ above: 1, below: 10 }), "value").field;
  assert.deepEqual(Object.keys(band), ["column", "above", "below", "rows_in_window", "rows_kept", "note"]);
});

test("bad thresholds are refused with words", () => {
  for (const bad of [{}, { over: 1 }, { above: "100" }, { above: true }, { above: 5, below: 5 }, { above: null }, [100], 100]) {
    assert.throws(() => readThreshold(bad), (e) => e instanceof ThresholdError && /threshold/.test(e.message), JSON.stringify(bad));
  }
});

test("the note of a count of none is the Python loop's", async () => {
  const { THRESHOLD_NONE } = await import("../lib/chat/threshold.ts");
  assert.match(THRESHOLD_NONE, /none of them is past the threshold/);
});
