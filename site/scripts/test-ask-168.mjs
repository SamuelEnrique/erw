// Energy Research Warehouse (ERW) site, session 168: Ask ERCOT's times in plain local words, and the question without a
// stray quote mark (lib/chat/plaintime.ts). No model call and no request: pure functions, a query result as the tool
// writes it (the recorded West hub read of tests/fixtures/session143), and the number check that guards every answer.
// The loop itself, with a stand-in for the model, is in scripts/test-ask-speed.mjs ("168: ...").
//
//   node --import ./scripts/alias-register.mjs scripts/test-ask-168.mjs
//
// Exit 1 on a failure.
import assert from "node:assert/strict";
import fs from "node:fs";
import * as pt from "../lib/chat/plaintime.ts";

let n = 0;
const test = (name, fn) => { fn(); n += 1; console.log(`ok   ${name}`); };
const read = (p) => fs.readFileSync(new URL(p, import.meta.url), "utf8");
// the number check of lib/chat/ask.ts, the one every answer passes (the module is loaded as scripts/test-ask-speed.mjs loads it)
const askSrc = read("../lib/chat/ask.ts");
const check = await import("../lib/chat/ask.ts");

test("an instant in ERCOT's own words, daylight saving by the zone database", () => {
  assert.equal(pt.plainTime("2026-10-03T21:00:00Z", "America/Chicago"), "4 pm Central, 3 October 2026");        // the owner's example: CDT, UTC-5
  assert.equal(pt.plainTime("2026-01-15T22:00:00Z", "America/Chicago"), "4 pm Central, 15 January 2026");       // CST, UTC-6
  assert.equal(pt.plainTime("2026-03-08T08:00:00Z", "America/Chicago"), "3 am Central, 8 March 2026");          // the spring change: 2 am does not exist
  assert.equal(pt.plainTime("2026-11-01T06:00:00Z", "America/Chicago"), "1 am Central, 1 November 2026");       // the autumn change: 1 am twice
  assert.equal(pt.plainTime("2026-11-01T07:00:00Z", "America/Chicago"), "1 am Central, 1 November 2026");
  assert.equal(pt.plainTime("2026-10-04T05:00:00Z", "America/Chicago"), "12 am Central, 4 October 2026");       // midnight
  assert.equal(pt.plainTime("2026-10-03T17:00:00Z", "America/Chicago"), "12 pm Central, 3 October 2026");       // noon
  assert.equal(pt.plainTime("2026-10-03T21:15:00Z", "America/Chicago"), "4:15 pm Central, 3 October 2026");     // a fifteen-minute interval
  assert.equal(pt.plainTime("2026-10-03T21:00:00Z", "America/Los_Angeles"), "2 pm Pacific, 3 October 2026");
  assert.equal(pt.plainTime("2026-10-03T21:00:00Z", "America/New_York"), "5 pm Eastern, 3 October 2026");
  assert.equal(pt.plainTime("not a time", "America/Chicago"), null);
});

test("each grid's zone, from the entity read", () => {
  assert.deepEqual(["ercot:HB_WEST", "eia930:ERCO", "caiso:TH_SP15_GEN-APND", "eia930:CISO", "nyiso:N.Y.C.", "eia930:ISNE", "spp:SPPSOUTH_HUB", "eia930:US48", null].map(pt.zoneOfEntity),
    ["America/Chicago", "America/Chicago", "America/Los_Angeles", "America/Los_Angeles", "America/New_York", "America/New_York", "America/Chicago", null, null]);
});

test("a tool result gains the local words beside each time; a table of days reads its label as a date", () => {
  const hourly = { result: [{ value: 81234.5, n: 24, at: "2026-10-03T21:00:00Z", entity: "eia930:ERCO" }], time_span: { first: "2026-10-03T05:00:00Z", last: "2026-10-04T04:00:00Z" } };
  const got = pt.addLocalTimes(hourly, false, "America/Chicago");
  assert.equal(hourly.result[0].at_local, "4 pm Central, 3 October 2026");
  assert.equal(hourly.result[0].at, "2026-10-03T21:00:00Z");                                                       // the stamp stays: the rows are the tool's
  assert.deepEqual([hourly.time_span.first_local, hourly.time_span.last_local], ["12 am Central, 3 October 2026", "11 pm Central, 3 October 2026"]);
  assert.equal(got.get("2026-10-03T21:00:00Z"), "4 pm Central, 3 October 2026");
  assert.ok(/Central time/.test(hourly.times_local) && !/\d/.test(hourly.times_local));
  const FIX = JSON.parse(read("../../tests/fixtures/session143/tool_reads.json"));
  const west = structuredClone(FIX.results[0].out);                                                                // ercot_hub_prices_daily: a table of days
  pt.addLocalTimes(west, true, "America/Chicago");
  assert.deepEqual([west.time_span.first_local, west.time_span.last_local], ["1 September 2026", "30 September 2026"]);
  assert.equal(west.times_local, undefined);
  const none = { result: [{ value: 1, at: "2026-10-03T21:00:00Z" }] };
  pt.addLocalTimes(none, false, null);                                                                              // no grid, no zone: nothing is guessed
  assert.equal(none.result[0].at_local, undefined);
});

test("the number check passes the local words, because they are in the tool result", () => {
  const out = { result: [{ value: 81234.5, n: 24, at: "2026-10-03T21:00:00Z", entity: "eia930:ERCO" }] };
  pt.addLocalTimes(out, false, "America/Chicago");
  const sources = [JSON.stringify(out)];
  assert.deepEqual(check.unverified("ERCOT's peak demand was 81,234.5 MW, at 4 pm Central, 3 October 2026 (eia930_all_demand).", sources), []);
  assert.deepEqual(check.unverified("ERCOT's peak demand was 81,234.5 MW at 2026-10-03T21:00:00Z.", sources), []);  // the stamp as written passes as before
  assert.deepEqual(check.unverified("ERCOT's peak demand was 81,234.5 MW at 5 pm Central, 3 October 2026.", sources), ["5"]);   // a wrong hour is still caught
});

test("no UTC stamp is left in an answer: the tool's words where it gave them, else the grid's zone; a day's label is a date", () => {
  const known = new Map([["2026-10-03T21:00:00Z", "4 pm Central, 3 October 2026"]]);
  assert.equal(pt.plainTimes("The peak was 81,234 MW at 2026-10-03T21:00:00Z.", "America/Chicago", known), "The peak was 81,234 MW at 4 pm Central, 3 October 2026.");
  assert.equal(pt.plainTimes("The peak was at 2026-10-03T21:00Z.", "America/Chicago"), "The peak was at 4 pm Central, 3 October 2026.");
  assert.equal(pt.plainTimes("Held through 2026-10-04T00:00:00Z, the newest whole day.", "America/Chicago"), "Held through 4 October 2026, the newest whole day.");
  assert.equal(pt.plainTimes("From 2026-09-01 to 2026-09-30, the mean was 38.36 USD/MWh.", "America/Chicago"), "From 1 September 2026 to 30 September 2026, the mean was 38.36 USD/MWh.");
  assert.equal(pt.plainTimes("In 2026-09 the mean was 38.36; the hub is HB_WEST.", "America/Chicago"), "In 2026-09 the mean was 38.36; the hub is HB_WEST.");
  for (const t of ["2026-10-03T21:00:00Z", "2026-10-03T21:00:00.000Z", "2026-10-03T16:00:00-05:00"]) assert.ok(!/\d{4}-\d{2}-\d{2}T/.test(pt.plainTimes(`at ${t}`, "America/Chicago")), t);
  assert.equal(pt.plainTimes("at 2026-10-03T21:00:00Z", null), "at 2026-10-03T21:00:00Z");                           // the general chat: as it was
});

test("the question is shown and asked without a stray quote mark; an apostrophe stays", () => {
  assert.equal(pt.cleanQuestion("What was ERCOT's peak demand yesterday?\""), "What was ERCOT's peak demand yesterday?");   // the page showed this
  assert.equal(pt.cleanQuestion("\"What was ERCOT's peak demand yesterday?\""), "What was ERCOT's peak demand yesterday?");
  assert.equal(pt.cleanQuestion("“What was ERCOT's peak demand yesterday?” "), "What was ERCOT's peak demand yesterday?");
  assert.equal(pt.cleanQuestion("  \"What was ERCOT's peak demand yesterday?"), "What was ERCOT's peak demand yesterday?");
  assert.equal(pt.cleanQuestion("What does \"peak\" mean on the \"Hub Average\"?"), "What does \"peak\" mean on the \"Hub Average\"?");
  assert.equal(pt.cleanQuestion("What was ERCOT's peak demand yesterday?"), "What was ERCOT's peak demand yesterday?");
  // where it is applied: the panel before it echoes and sends the question, the route before it asks, logs and answers
  const panel = read("../components/ask/AskPanel.tsx"), route = read("../app/api/ask/route.ts");
  assert.ok(panel.includes("const question = cleanQuestion(typed);") && panel.includes("setAsked(question);"));
  assert.ok(route.includes("const asked = cleanQuestion(question);"));
});

test("only Ask ERCOT's answers are rewritten; the general chat and the other grids' panels are as they were", () => {
  assert.ok(read("../lib/chat/ercot.ts").includes('zone: "America/Chicago",'));
  assert.ok(askSrc.includes("const plain = (t: string) => (profile?.zone ? plainTimes(t, profile.zone, localWords) : t);"));
  assert.ok(askSrc.includes("const answer = plain(nodash(draft.answer));"));
  for (const f of ["../lib/chat/plaintime.ts", "./test-ask-168.mjs"]) assert.ok(!read(f).includes(String.fromCharCode(0x2014)), f);
});

console.log(`${n} tests pass`);
