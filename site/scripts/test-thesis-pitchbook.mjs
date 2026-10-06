// Energy Research Warehouse (ERW) site, session 135: Thesis Builder (/thesis). The gate a PitchBook answer passes
// before it is stored (lib/thesis/pitchbook.ts), and what the page works out from a run (lib/thesis/view.ts).
//
//   node --import ./scripts/alias-register.mjs scripts/test-thesis-pitchbook.mjs
//
// Exit 1 on a failure. Nothing is written and nothing is requested: the figures below are made up for the test and
// are no company's.
import assert from "node:assert/strict";
import * as pb from "../lib/thesis/pitchbook.ts";
import * as v from "../lib/thesis/view.ts";

let n = 0;
const test = (name, fn) => { fn(); n += 1; console.log(`ok   ${name}`); };
const RUN = "20261006T140512Z-a1b2c3";
const good = () => ({
  format: "erw-pitchbook-1", run_id: RUN, pulled_on: "2026-10-06",
  companies: [
    { name: "  Example  Storage Inc. ", found: true, pitchbook_name: "Example Storage", hq: " Austin, TX ", founded_year: 2019, description: "x".repeat(450), employees: 42,
      financing_status: "Venture Capital-Backed", last_round: { date: "2025-03", type: "Series A", size_usd_m: 12.5, post_valuation_usd_m: null },
      total_raised_usd_m: 18, investors: [" Fund One ", "", "Fund Two"], lead_investors: ["Fund One"], founders: null },
    { name: "Nowhere Power", found: false, hq: "Reno, NV", total_raised_usd_m: 3 },
  ],
  additional_companies: [{ name: "Found Later LLC", found: true, why: "Named by PitchBook under the same keywords.", total_raised_usd_m: 0 }],
});
const refused = (payload, words, run = RUN) => {
  const r = pb.validatePitchbook(payload, run, 2026);
  assert.equal(r.ok, false, `accepted: ${JSON.stringify(payload).slice(0, 120)}`);
  assert.match(r.reason, words);
  return r.reason;
};
const change = (f) => { const p = good(); f(p); return p; };

test("a good answer passes and comes back normalized and labeled", () => {
  const r = pb.validatePitchbook(good(), RUN, 2026);
  assert.equal(r.ok, true, r.reason);
  const p = r.payload;
  assert.deepEqual(Object.keys(p), ["format", "run_id", "pulled_on", "label", "received_note", "companies", "additional_companies"]);
  assert.equal(p.label, "PitchBook");
  assert.equal(p.received_note, "Figures as returned from PitchBook through the user's own account; not checked by the ERW.");
  const c = p.companies[0];
  assert.equal(c.name, "Example Storage Inc.");                       // trimmed, inner spaces single
  assert.equal(c.hq, "Austin, TX");
  assert.equal(c.description.length, 400);                             // cut at its cap
  assert.deepEqual(c.investors, ["Fund One", "Fund Two"]);             // a blank name is dropped
  assert.deepEqual(c.last_round, { date: "2025-03", type: "Series A", size_usd_m: 12.5 });   // a null is dropped
  assert.ok(!("founders" in c));
  assert.equal(p.additional_companies[0].why, "Named by PitchBook under the same keywords.");
  assert.equal(p.additional_companies[0].total_raised_usd_m, 0);        // zero is a figure
});
test("a company that was not found keeps only its name and found", () => {
  const p = pb.validatePitchbook(good(), RUN, 2026).payload;
  assert.deepEqual(p.companies[1], { name: "Nowhere Power", found: false });
  const a = pb.validatePitchbook(change((x) => { x.additional_companies[0].found = false; }), RUN, 2026).payload;
  assert.deepEqual(a.additional_companies[0], { name: "Found Later LLC", found: false });
});
test("additional companies may be left out or null; companies may not", () => {
  const r = pb.validatePitchbook(change((x) => { delete x.additional_companies; }), RUN, 2026);
  assert.deepEqual(r.payload.additional_companies, []);
  assert.deepEqual(pb.validatePitchbook(change((x) => { x.additional_companies = null; }), RUN, 2026).payload.additional_companies, []);
  refused(change((x) => { delete x.companies; }), /"companies" is required/);
  refused(change((x) => { x.companies = {}; }), /"companies" is required/);
});
test("a wrong format, a wrong run and an answer that is not an object are refused", () => {
  refused(change((x) => { x.format = "erw-pitchbook-2"; }), /"format" must be "erw-pitchbook-1"/);
  refused(change((x) => { delete x.format; }), /"format"/);
  refused(good(), /"run_id" is not the run/, "20261006T140512Z-ffffff");
  refused(change((x) => { x.run_id = 7; }), /"run_id"/);
  for (const x of [null, [], "text", 3]) refused(x, /one JSON object/);
});
test("an unknown key is refused at every level", () => {
  refused(change((x) => { x.note = "hello"; }), /The answer holds a key the format does not have: "note"/);
  refused(change((x) => { x.label = "PitchBook"; }), /"label"/);                              // the label is the site's to write
  refused(change((x) => { x.companies[0].valuation = 100; }), /companies\[0\] holds a key .*"valuation"/);
  refused(change((x) => { x.companies[0].last_round.lead = "Fund One"; }), /companies\[0\]\.last_round holds a key .*"lead"/);
  refused(change((x) => { x.companies[0].why = "no"; }), /companies\[0\] holds a key .*"why"/);   // "why" belongs to additional companies only
  refused(change((x) => { x.additional_companies[0].score = 1; }), /additional_companies\[0\] holds a key/);
  refused(JSON.parse('{"format":"erw-pitchbook-1","run_id":"' + RUN + '","pulled_on":"2026-10-06","companies":[],"__proto__":{"x":1}}'), /"__proto__"/);
});
test("a number that is negative, not finite, not a number, or not whole where it must be is refused", () => {
  refused(change((x) => { x.companies[0].total_raised_usd_m = -1; }), /total_raised_usd_m must not be below zero/);
  refused(change((x) => { x.companies[0].last_round.size_usd_m = -0.5; }), /last_round\.size_usd_m must not be below zero/);
  refused(change((x) => { x.companies[0].last_round.post_valuation_usd_m = Infinity; }), /post_valuation_usd_m must be a finite number/);
  refused(change((x) => { x.companies[0].total_raised_usd_m = NaN; }), /finite number/);
  refused(JSON.parse(JSON.stringify(good()).replace('"total_raised_usd_m":18', '"total_raised_usd_m":1e999')), /finite number/);   // as JSON reads it
  refused(change((x) => { x.companies[0].total_raised_usd_m = "18"; }), /finite number/);
  refused(change((x) => { x.companies[0].employees = 4.5; }), /employees must be a whole number/);
  refused(change((x) => { x.companies[0].employees = -3; }), /employees must not be below zero/);
  refused(change((x) => { x.companies[0].founded_year = 1899; }), /founded_year must be 1900 or later/);
  refused(change((x) => { x.companies[0].founded_year = 2027; }), /founded_year must be 2026 or earlier/);
  assert.equal(pb.validatePitchbook(change((x) => { x.companies[0].founded_year = 2026; }), RUN, 2026).ok, true);
});
test("a date that is not a day of the calendar, or not written as the format asks, is refused", () => {
  for (const d of ["2026-13-01", "2026-02-30", "06/10/2026", "2026-10-6", "2026-10", "2026", "", 20261006]) refused(change((x) => { x.pulled_on = d; }), /"pulled_on"/);
  refused(change((x) => { delete x.pulled_on; }), /"pulled_on" is required/);
  for (const d of ["2025-13", "2025-02-30", "March 2025", "25-03", "1850"]) refused(change((x) => { x.companies[0].last_round.date = d; }), /last_round\.date/);
  for (const d of ["2025", "2025-03", "2025-03-31"]) assert.equal(pb.validatePitchbook(change((x) => { x.companies[0].last_round.date = d; }), RUN, 2026).payload.companies[0].last_round.date, d);
});
test("too many companies, too many names in a list and a name that is missing, empty or too long are refused", () => {
  const many = (k) => Array.from({ length: k }, (_, i) => ({ name: `Company ${i}`, found: false }));
  refused(change((x) => { x.companies = many(301); }), /"companies" holds 301; at most 300/);
  assert.equal(pb.validatePitchbook(change((x) => { x.companies = many(300); }), RUN, 2026).ok, true);
  refused(change((x) => { x.additional_companies = many(101).map((c) => ({ ...c, why: "w" })); }), /"additional_companies" holds 101; at most 100/);
  refused(change((x) => { x.companies[0].investors = Array.from({ length: 41 }, (_, i) => `Fund ${i}`); }), /investors holds 41 names; at most 40/);
  refused(change((x) => { x.companies[0].investors = ["Fund One", 7]; }), /investors\[1\] must be text/);
  refused(change((x) => { x.companies[0].name = "n".repeat(121); }), /name is longer than 120 characters/);
  refused(change((x) => { x.companies[0].name = "   "; }), /name is empty/);
  refused(change((x) => { delete x.companies[0].name; }), /name is required/);
  refused(change((x) => { x.companies[0].found = "yes"; }), /found is required and must be true or false/);
  refused(change((x) => { x.companies[0].found = null; }), /found is required/);                // null stands for an optional field only
  refused(change((x) => { delete x.additional_companies[0].why; }), /why is required/);
  refused(change((x) => { x.companies[1] = "Nowhere Power"; }), /companies\[1\] must be an object/);
  refused(change((x) => { x.companies[0].last_round = "Series A"; }), /last_round must be an object/);
});
test("a submission is { run_id, key, payload }, or the payload itself carrying its key", () => {
  const key = "k".repeat(43);
  const a = pb.readSubmission({ run_id: RUN, key, payload: good() });
  assert.deepEqual([a.ok, a.run_id, a.key], [true, RUN, key]);
  assert.equal(pb.validatePitchbook(a.payload, a.run_id, 2026).ok, true);
  const b = pb.readSubmission({ ...good(), key });                       // the pasted answer, whole
  assert.deepEqual([b.ok, b.run_id, b.key, "key" in b.payload], [true, RUN, key, false]);
  assert.equal(pb.validatePitchbook(b.payload, b.run_id, 2026).ok, true);
  const c = pb.readSubmission({ payload: { ...good(), key } });          // the key inside the payload
  assert.deepEqual([c.ok, c.run_id, c.key, "key" in c.payload], [true, RUN, key, false]);
  const d = pb.readSubmission({ run_id: "20261006T140512Z-ffffff", key, payload: good() });   // the route's run is the one that counts
  assert.equal(pb.validatePitchbook(d.payload, d.run_id, 2026).ok, false);
  assert.match(pb.readSubmission({ run_id: RUN, payload: good() }).reason, /key is missing/);
  assert.match(pb.readSubmission({ run_id: RUN, key: 12, payload: good() }).reason, /key is missing/);
  assert.match(pb.readSubmission({ run_id: RUN, key, payload: good(), extra: 1 }).reason, /"extra"/);
  assert.match(pb.readSubmission({ run_id: "../x", key, payload: good() }).reason, /run .* is not named/);
  assert.match(pb.readSubmission({ run_id: RUN, key, payload: [] }).reason, /one JSON object/);
  for (const x of [null, [], "x"]) assert.equal(pb.readSubmission(x).ok, false);
});
test("the JSON in a pasted answer is found bare, in a code fence, or with words around it", () => {
  const j = JSON.stringify(good());
  assert.deepEqual(pb.extractJson(j).value, good());
  assert.deepEqual(pb.extractJson("Here is the answer:\n```json\n" + j + "\n```\nLet me know.").value, good());
  assert.deepEqual(pb.extractJson("Answer: " + j + " (end)").value, good());
  assert.equal(pb.extractJson("   ").ok, false);
  assert.equal(pb.extractJson("no json here").ok, false);
  assert.equal(pb.extractJson("[1, 2]").ok, false);
});

test("the address holds the run and the tab; what it cannot be is dropped", () => {
  assert.deepEqual(v.choiceOf({}), { run: null, tab: "scope" });
  assert.equal(v.hrefOf(v.choiceOf({})), "/thesis");
  const c = v.choiceOf({ run: RUN, tab: "funnel" });
  assert.deepEqual(c, { run: RUN, tab: "funnel" });
  assert.equal(v.hrefOf(c), `/thesis?run=${RUN}&tab=funnel`);
  assert.equal(v.hrefOf(c, { tab: "scope" }), `/thesis?run=${RUN}`);
  assert.equal(v.hrefOf(c, { tab: "trends" }, "trend-3"), `/thesis?run=${RUN}&tab=trends#trend-3`);
  assert.deepEqual(v.choiceOf({ run: "a b;drop", tab: "export" }), { run: null, tab: "scope" });
  assert.deepEqual(v.choiceOf({ run: [RUN, "x"], tab: ["policy"] }), { run: RUN, tab: "policy" });
  assert.deepEqual(v.TABS.map((t) => t.label), ["Scope and definitions", "Trends", "Company landscape", "Deal funnel", "Pipeline map", "Capital", "Incumbents", "Risks", "Policy"]);
});
test("a cell is a number only when it reads as one; anything else is not drawn", () => {
  assert.equal(v.numeric("1,234.5"), 1234.5);
  assert.equal(v.numeric("$1,200"), 1200);
  assert.equal(v.numeric("45%"), 45);
  assert.equal(v.numeric("45 GW", "GW"), 45);
  assert.equal(v.numeric("$45 billion", "USD billion"), 45);
  assert.equal(v.numeric("-3.2"), -3.2);
  assert.equal(v.numeric("−3.2"), -3.2);
  assert.equal(v.numeric(".5"), 0.5);
  assert.equal(v.numeric("0"), 0);
  for (const x of ["", "about 12", "3 to 5", "12-15", "1.2B", "45 GW", "1,23", "n/a", "2025 (est.)", "GW", "%", null, undefined, 12, { missing: "not_held", note: "x" }]) assert.equal(v.numeric(x), null, String(x));
  assert.equal(v.numeric("1.2B", "USD million"), null);                  // never drawn at another scale
});
test("a trend's chart is drawn from its own table; a row with no number is left out, never zero", () => {
  const trend = {
    n: 1, title: "A trend", fact: { text: "", sources: [] }, sources: [],
    table: { columns: ["Year", "Installed", "Planned"], rows: [["2023", "10 GW", "4 GW"], ["2024", { missing: "not_held", note: "not published" }, "about 6"], ["2025", "18.5 GW", { missing: "not_disclosed", note: "x" }], ["2026", "1,024 GW", "7 GW"]] },
    chart: { kind: "bar", title: "Capacity", category: 0, values: [1, 2], unit: "GW" },
  };
  const c = v.chartOf(trend);
  assert.deepEqual(c.categories, ["2023", "2025", "2026"]);            // 2024 holds no number in either column
  assert.deepEqual(c.series, [{ name: "Installed", data: [10, 18.5, 1024] }, { name: "Planned", data: [4, null, 7] }]);
  assert.deepEqual([c.kind, c.title, c.unit], ["bar", "Capacity", "GW"]);
  assert.equal(v.chartOf({ ...trend, chart: { ...trend.chart, kind: "none" } }), null);
  assert.equal(v.chartOf({ ...trend, chart: { ...trend.chart, values: [0] }, table: { columns: ["Year"], rows: [["n/a"]] } }), null);
  assert.equal(v.chartOf({ ...trend, table: undefined }), null);
  assert.equal(v.chartOf({ ...trend, chart: undefined }), null);
  assert.equal(v.chartOf(undefined), null);
});
test("a PitchBook company is matched by the name asked, and every figure is written with its own name", () => {
  const p = pb.validatePitchbook(good(), RUN, 2026).payload;
  assert.equal(v.pitchbookFor(p, "example storage, inc").name, "Example Storage Inc.");
  assert.equal(v.pitchbookFor(p, "Example Storage Holdings"), null);
  assert.equal(v.pitchbookFor(null, "Example Storage"), null);
  assert.equal(v.pitchbookFor(p, ""), null);
  const figs = Object.fromEntries(v.pbFigures(v.pitchbookFor(p, "Example Storage Inc.")).map((f) => [f.id, `${f.label}: ${f.value}`]));
  assert.equal(figs.total_raised, "Total raised: USD 18 million");
  assert.equal(figs.last_round, "Last round: Series A, Mar 2025, USD 12.5 million");
  assert.equal(figs.hq, "Headquarters: Austin, TX");
  assert.equal(figs.investors, "Investors: Fund One, Fund Two");
  assert.ok(!("pitchbook_name" in figs) && !("post_valuation" in figs) && !("founders" in figs));
  assert.deepEqual(v.pbFigures(v.pitchbookFor(p, "Nowhere Power")), []);  // not found: no figure
  assert.deepEqual(v.pbFigureFor(v.pitchbookFor(p, "Example Storage Inc."), "raised"), { id: "total_raised", label: "Total raised", value: "USD 18 million" });
  assert.equal(v.pbFigureFor(v.pitchbookFor(p, "Example Storage Inc."), "tam"), null);
  assert.equal(v.pbFigureFor(v.pitchbookFor(p, "Example Storage Inc."), "founders"), null);
});
test("links, dates and absent fields", () => {
  assert.equal(v.safeUrl("https://example.com/a?b=1"), "https://example.com/a?b=1");
  for (const u of ["javascript:alert(1)", "data:text/html,x", "/thesis", "", null, "ftp://x", "http://"]) assert.equal(v.safeUrl(u), null, String(u));
  assert.equal(v.whenWords("2026-10-06T14:05:12.123456+00:00"), "6 Oct 2026, 14:05 UTC");
  assert.equal(v.whenWords("2026-10-06"), "6 Oct 2026");
  assert.equal(v.whenWords("Q3 2026"), "Q3 2026");
  assert.equal(v.whenWords("2025-03"), "Mar 2025");
  assert.equal(v.whenWords("2025"), "2025");                             // a year is not the first of January
  assert.equal(v.whenWords("2026-10-06 14:05:12+00"), "6 Oct 2026, 14:05 UTC");
  assert.equal(v.whenWords(null), "");
  assert.deepEqual(v.arr(undefined), []);
  assert.deepEqual(v.arr("abc"), []);
  assert.equal(v.str(undefined), "");
  assert.equal(v.str({}), "");
  assert.equal(v.cellWords({ missing: "pitchbook_pending", note: "" }), "PitchBook pending");
  assert.equal(v.cellWords(undefined), "");
});
console.log(`${n} tests pass`);
