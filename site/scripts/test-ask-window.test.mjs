// Energy Research Warehouse (ERW) site, session 5267 (chain 256): whether a window of a series is whole
// (lib/chat/window.ts windowOf), held to the same answers as warehouse/chat/window.py on the made windows of
// tests/fixtures/session5267/window_cases.json (tests/test_session5267_ask.py holds the Python side). No build, no
// network: node strips the file's types.
//
//   node --test site/scripts/test-ask-window.test.mjs
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { MISSING_SHOWN, WINDOW_NONE_HELD, WINDOW_PART, WINDOW_UNKNOWN, WINDOW_WHOLE, WINDOW_WHOLE_ROWS, secondsOf, stepOf, windowOf } from "../lib/chat/window.ts";

const CASES = JSON.parse(fs.readFileSync(new URL("../../tests/fixtures/session5267/window_cases.json", import.meta.url), "utf8")).cases;
const plain = (x) => JSON.parse(JSON.stringify(x));

test("every made window is answered as the Python function answers it, key for key and in the same order", () => {
  assert.ok(CASES.length >= 35);
  for (const c of CASES) {
    const got = plain(windowOf(c.start, c.end, c.steps, c.series));
    assert.deepEqual(got, c.window, c.name);
    if (got) assert.deepEqual(Object.keys(got), Object.keys(c.window), `${c.name}: the order of the keys`);
  }
});

test("a step's seconds, and the steps this does not count by", () => {
  assert.deepEqual(["PT5M", "PT15M", "PT30M", "PT1H", "PT2H", "P1D", "P1W"].map(secondsOf), [300, 900, 1800, 3600, 7200, 86400, 604800]);
  for (const s of ["P1M", "P1Y", "P3M", "PT0M", "", null, undefined, "hourly"]) assert.equal(secondsOf(s), null, String(s));
});

test("one step is taken as it is; of several, the rows' own smallest gap when it is one of them", () => {
  assert.equal(stepOf(["PT1H"], {}), "PT1H");
  assert.equal(stepOf(["PT1H", "PT1H", null], { a: [] }), "PT1H");
  assert.equal(stepOf([], { a: [0, 3600] }), null);
  assert.equal(stepOf(["PT15M", "PT5M"], { a: [0, 300, 900] }), "PT5M");
  assert.equal(stepOf(["PT15M", "PT5M"], { a: [0, 900, 1800] }), "PT15M");
  assert.equal(stepOf(["PT15M", "PT5M"], { a: [0, 1800] }), null);            // a gap that is neither step: not told
  assert.equal(stepOf(["PT15M", "PT5M"], { a: [0], b: [300] }), null);        // one row a series: no gap inside a series
});

test("what the chat is told to say: whole, held in part, nothing held, not told", () => {
  const day = (skip = []) => Array.from({ length: 24 }, (_, i) => i).filter((i) => !skip.includes(i)).map((i) => `2026-11-10T${String(i).padStart(2, "0")}:00:00Z`);
  const w = (times, steps = ["PT1H"]) => windowOf("2026-11-10T00:00:00Z", "2026-11-11T00:00:00Z", steps, { "x|y": times });
  assert.equal(w(day()).note, WINDOW_WHOLE);
  assert.equal(w(day()).whole, true);
  assert.equal(w(day([3])).note, WINDOW_PART);
  assert.deepEqual(w(day([3])).missing, [{ from: "2026-11-10T03:00:00Z", until: "2026-11-10T04:00:00Z", steps: 1 }]);
  assert.equal(w([]).note, WINDOW_NONE_HELD);
  assert.equal(w([]).steps_missing, 24);
  assert.equal(w(day(), ["PT1H", "PT5M"]).step, "PT1H");
  assert.equal(w(day().slice(0, 1), ["PT1H", "PT5M"]).note, WINDOW_UNKNOWN);
  assert.equal(w(day().slice(0, 1), ["PT1H", "PT5M"]).whole, null);          // never "whole" and never "in part" on a guess
  // a table of days or longer: every row held is not every hour of the period held, and the note says whose that is to say
  const month = windowOf("2026-10-01", "2026-11-01", ["P1M"], { "x|y": ["2026-10-01T00:00:00Z"] });
  assert.deepEqual([month.whole, month.note], [true, WINDOW_WHOLE_ROWS]);
  assert.ok(WINDOW_WHOLE_ROWS.includes("Whether a row covers its whole period is the table's own to say"));
});

test("the runs of missing steps add up to the steps missing, and at most six are shown", () => {
  for (const c of CASES) {
    const got = windowOf(c.start, c.end, c.steps, c.series);
    if (!got || typeof got.steps_held !== "number" || got.steps_in_window === null) continue;
    assert.equal(got.steps_missing, got.steps_in_window - got.steps_held, c.name);
    if (got.missing) {
      assert.ok(got.missing.length <= MISSING_SHOWN, c.name);
      if (got.missing_runs === got.missing.length) assert.equal(got.missing.reduce((s, r) => s + r.steps, 0), got.steps_missing, c.name);
    } else assert.equal(got.steps_missing, 0, c.name);
    assert.equal(got.whole, got.steps_in_window === 0 ? null : got.steps_missing === 0, c.name);
  }
});

test("nothing is asked of the database: the module imports nothing", () => {
  const src = fs.readFileSync(new URL("../lib/chat/window.ts", import.meta.url), "utf8");
  assert.ok(!/^\s*import\s/m.test(src));
  assert.ok(!/fetch\(|supabase|rest\(/.test(src));
});
