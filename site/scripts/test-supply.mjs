// Energy Research Warehouse (ERW) site, session 134: Supply and trade's address and helpers (lib/supply.ts), on the
// site's own file (data/supply.json).
//
//   node --import ./scripts/alias-register.mjs scripts/test-supply.mjs
//
// Exit 1 on a failure. Nothing is written.
import assert from "node:assert/strict";
import fs from "node:fs";
import * as s from "../lib/supply.ts";

const file = JSON.parse(fs.readFileSync(new URL("../data/supply.json", import.meta.url), "utf-8"));
let n = 0;
const test = (name, fn) => { fn(); n += 1; console.log(`ok   ${name}`); };

test("more in storage, more production or more imports is looser; more exports or burn is tighter; no sense, no reading", () => {
  assert.equal(s.reading(1, 27.4), "looser");
  assert.equal(s.reading(1, -136), "tighter");
  assert.equal(s.reading(-1, 0.4), "tighter");
  assert.equal(s.reading(-1, -0.4), "looser");
  assert.equal(s.reading(0, 12), null);
  assert.equal(s.reading(1, 0), null);
  assert.equal(s.reading(1, null), null);
  assert.equal(s.reading(1, undefined), null);
});
test("an address with nothing chosen is every group and no chart open", () => {
  const c = s.choiceOf({}, file);
  assert.deepEqual(c, { groups: [], s: null });
  assert.equal(s.hrefOf(c), "/supply");
});
test("the groups chosen and the series opened are in the address; what the file does not hold is dropped", () => {
  const c = s.choiceOf({ g: "gasstor,nowhere,stocks,gasstor", s: "eia-wcestus1" }, file);
  assert.deepEqual(c, { groups: ["gasstor", "stocks"], s: "eia-wcestus1" });
  assert.equal(s.hrefOf(c), "/supply?g=gasstor%2Cstocks&s=eia-wcestus1");
  assert.equal(s.hrefOf(c, { s: null }), "/supply?g=gasstor%2Cstocks");
  assert.equal(s.choiceOf({ s: "not-a-series" }, file).s, null);
  assert.equal(s.choiceOf({ s: "cleared-miso" }, file).s, null);          // a row with no value has no chart to open
  assert.equal(s.choiceOf({ s: ["eia-wgtstus1", "eia-wdistus1"] }, file).s, "eia-wgtstus1");
});
test("a chip adds its group or takes it away", () => {
  assert.deepEqual(s.toggled([], "burn"), ["burn"]);
  assert.deepEqual(s.toggled(["burn", "stocks"], "burn"), ["stocks"]);
});
test("numbers are written by their size, with a sign where they are a difference", () => {
  assert.equal(s.fmt(3415, "bcf"), "3,415");
  assert.equal(s.fmt(427.32, "million bbl"), "427.3");
  assert.equal(s.fmt(24.3, "million bbl"), "24.30");
  assert.equal(s.fmt(0.92, "million bbl", 427.32), "0.9");                // a difference is written to the places of its level
  assert.equal(s.fmt(-132799, "contracts"), "-132,799");
  assert.equal(s.signed(64, "bcf"), "+64.00");
  assert.equal(s.signed(64, "bcf", 3415), "+64");
  assert.equal(s.signed(-24, "bcf", 3415), "−24");
  assert.equal(s.signed(0, "bcf", 3415), "0");
  assert.equal(s.pct(-3.8299), "−3.8%");
  assert.equal(s.pct(0.8088), "+0.8%");
  assert.equal(s.signed(-0.02, "percent", 82.5), "0.0");                  // a difference written as zero carries no sign
  assert.equal(s.pct(-0.02), "0.0%");
  assert.equal(s.withUnitWords(file).rows.find((r) => r.id === "eia-wcrfpus2").unit, "kb/d");
  assert.equal(s.fmt(92.5, "%"), s.fmt(92.5, "percent"));
});
test("dates: a week by its day, a month by its name, a release by its weekday and Eastern time", () => {
  assert.equal(s.dateWords("2026-09-25"), "25 Sep 2026");
  assert.equal(s.dateWords("2026-07-01", "M"), "Jul 2026");
  assert.equal(s.shortDate("2026-09-25"), "25 Sep");
  assert.equal(s.shortDate("2026-07-01", "M"), "Jul");
  assert.equal(s.releaseWords("2026-10-07T10:30"), "Wed 7 Oct, 10:30 Eastern");
  assert.equal(s.releaseWords("2026-10-15T12:00"), "Thu 15 Oct, 12:00 Eastern");
});
test("the next release is this week's standing day, or the date its publisher moved it to, as of the Eastern clock", () => {
  const by = (at) => Object.fromEntries(file.calendar.reports.map((r) => [r.id, s.nextRelease(r, at)]));
  const a = by("2026-10-06T06:00");                                        // a Tuesday morning
  assert.deepEqual([a.wpsr.next, a.wngsr.next, a.cot.next], ["2026-10-07T10:30", "2026-10-08T10:30", "2026-10-09T15:30"]);
  assert.equal(a.wpsr.moved, null);
  assert.equal(by("2026-10-07T10:29").wpsr.next, "2026-10-07T10:30");      // a minute before it is out
  const b = by("2026-10-07T11:00");                                        // after it is out: the next, which Columbus Day moves
  assert.equal(b.wpsr.next, "2026-10-15T12:00");
  assert.match(b.wpsr.moved, /Columbus Day/);
  assert.equal(by("2026-10-14T11:00").wpsr.next, "2026-10-15T12:00");      // on the standing day of a moved week, it is still to come
  assert.equal(by("2026-10-15T12:30").wpsr.next, "2026-10-21T10:30");
  assert.equal(by("2026-11-11T09:00").wngsr.next, "2026-11-13T10:30");     // Veterans Day
  const bare = { ...file.calendar.reports[0], weekday: undefined };
  assert.equal(s.nextRelease(bare, "2027-01-01T00:00").next, bare.next);   // a file with no rule: its own date stands
  assert.equal(s.easternNow(new Date("2026-10-07T14:29:00Z")), "2026-10-07T10:29");      // daylight time, four hours behind UTC
  assert.equal(s.easternNow(new Date("2026-12-02T04:30:00Z")), "2026-12-01T23:30");      // standard time, five hours behind
});
test("the surprises are the rows whose newest change is outside its five years, the farthest first", () => {
  const got = s.surprises(file);
  const want = file.rows.filter((r) => r.status === "ok" && r.change && r.change.outside && r.change.surprise !== null);
  assert.equal(got.length, want.length);
  assert.ok(got.every((r) => r.change.v < r.change.lo || r.change.v > r.change.hi));
  const far = (r) => Math.abs(r.change.surprise) / (r.change.hi - r.change.lo);
  for (let i = 1; i < got.length; i += 1) assert.ok(far(got[i - 1]) >= far(got[i]) || !Number.isFinite(far(got[i - 1])));
});
test("the five headline series are held, and a placeholder exists for every status but ok", () => {
  for (const id of s.HEADLINE) assert.equal(file.rows.find((r) => r.id === id)?.status, "ok", id);
  for (const r of file.rows) if (r.status !== "ok") assert.ok(s.PLACEHOLDER[r.status], r.id);
  assert.deepEqual(Object.values(s.PLACEHOLDER).sort(), ["licensed source needed", "not held yet", "paused while terms are reviewed", "working on it"]);
  assert.ok(s.rowsOf(file, "cleared").every((r) => r.status !== "ok"));
});
console.log(`${n} tests pass`);
