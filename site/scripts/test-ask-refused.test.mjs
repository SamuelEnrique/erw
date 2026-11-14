// Energy Research Warehouse (ERW) site, session 5256 (chain 238): a table a tool refuses to read (lib/chat/refused.ts),
// as warehouse/chat/tools.py and warehouse/chat/ask.py hold the same words and the same rule
// (tests/test_session5256_ask.py holds the Python side and both loops turn by turn). No build, no network: node strips
// the file's types.
//
//   node --test site/scripts/test-ask-refused.test.mjs
import test from "node:test";
import assert from "node:assert/strict";
import { CUT_SHORT, HOLD_WORDS, REFUSAL_FIRST, REFUSAL_WORDS, cutShort, heldTables, notLiveWords, refusalFigureProblem, refusalFigures, refusedAgainNote, refusedRead,
  refusedWhole, tablesNamed, withHoldWords, withRefusalWords } from "../lib/chat/refused.ts";

// Session 6109 (chain 280): the lab's l02 of 14 November 2026, a refusal that reached the reader cut at an opening bracket
// (tests/test_session6108_ask.py holds the Python side and the stored runs).
test("an answer that stops in the middle of a sentence is told from a whole one", () => {
  const l02 = "This is not in the warehouse. The energy_deals table, which holds power purchase agreements, is held for a license (";
  assert.ok(cutShort(l02));
  for (const end of ["the price was,", "the tables are:", "it holds;", "see [", "  a set { \n"]) assert.ok(cutShort(end), end);
  for (const whole of ["49,421.92 MW (eia930_all_demand).", "It was 54.48 USD/MWh", "Not in the warehouse.", "The table is \"license needed\"", "100 percent", ""]) assert.ok(!cutShort(whole), whole);
  assert.match(CUT_SHORT, /^an answer that stops in the middle of a sentence: write the whole answer again/);
  // a refusal after a held table: the hold's words first, and then no "Not in the warehouse." is added to them
  const held = heldTables({ energy_deals: "table energy_deals is license needed: Reuters; Bloomberg" });
  assert.equal(withRefusalWords(withHoldWords("The deals table is held.", held)), "energy_deals: license needed, so no figure of it is given here. The deals table is held.");
  assert.equal(withRefusalWords(withHoldWords("The table holds no row.", [])), "Not in the warehouse. The table holds no row.");
});

test("the refusal of a table the live set lacks says where it is and how to answer", () => {
  const w = notLiveWords("eia_crude_imports_by_country");
  assert.ok(w.startsWith("table eia_crude_imports_by_country is not in this site's live set; its full history is on Redivis."));
  assert.match(w, /No tool here can read it, and no figure of it may be stated\./);
  // session 5258: the words do not forbid looking in another table (a derived table may carry the figure)
  assert.match(w, /Another table you can read may hold what is asked \(a derived table often carries a source table's figures\): look before you refuse\./);
  assert.match(w, /If none does, answer with not_in_warehouse true/);
  assert.match(w, /say that eia_crude_imports_by_country is on Redivis and not in the live set this chat reads$/);
});

test("a refusal of the table itself: not in the live set, held for a license, MISO's pause", () => {
  assert.equal(refusedRead(notLiveWords("x")), true);
  assert.equal(refusedRead('table energy_deals is license needed: the publishers. State no figure of it: answer with not_in_warehouse true and say that it is "license needed"'), true);
  assert.equal(refusedRead("MISO is paused while its terms are reviewed (since 4 October 2026): this site shows no figure of MISO's own data."), true);
});

test("any other tool error is not a refusal of the table", () => {
  for (const e of ["no column 'state' in this table; columns: entity, variable", "aggregation must be one of latest, mean", "unknown time zone 'Texas'",
    "no public table named \"x\"; call list_tables for the table names", "", undefined, null, 12, { error: "license needed" }]) assert.equal(refusedRead(e), false, String(e));
});

test("a table refused whole, and what is not: MISO's pause and a held grid refuse rows, not the table", () => {
  const w = notLiveWords("eia_crude_imports_by_country");
  assert.equal(refusedWhole(w, ["eia_crude_imports_by_country"]), "eia_crude_imports_by_country");
  assert.equal(refusedWhole(w, ["another", "eia_crude_imports_by_country"]), "eia_crude_imports_by_country");
  assert.equal(refusedWhole("table energy_deals is license needed: the publishers", ["energy_deals"]), "energy_deals");
  assert.equal(refusedWhole(w, ["another"]), null);
  assert.equal(refusedWhole("MISO is paused while its terms are reviewed (since 4 October 2026)", ["cost_of_power_monthly"]), null);
  assert.equal(refusedWhole("no column 'state' in this table", ["eia_crude_imports_by_country"]), null);
  assert.equal(refusedWhole(undefined, ["x"]), null);
});

test("the tables a call names", () => {
  assert.deepEqual(tablesNamed("query", { table: "a" }), ["a"]);
  assert.deepEqual(tablesNamed("describe_table", { table: "a" }), ["a"]);
  assert.deepEqual(tablesNamed("compare", { a: { table: "a" }, b: { table: "b" } }), ["a", "b"]);
  assert.deepEqual(tablesNamed("list_tables", { sector: "oil" }), []);
  assert.deepEqual(tablesNamed("query", null), []);
});

test("a later call that names a refused table is told so, with the refusal's own words", () => {
  const w = notLiveWords("t");
  const note = refusedAgainNote("t", w);
  assert.ok(note.startsWith("table t was already refused for this question and no call can read it: do not ask it again."));
  assert.ok(note.endsWith(w));
});

// Session 5276 (chain 256): a refusal's fixed words, by the loop (the platform set's gp02 of 14 November 2026; oi09 of 13 November)
test("a refusal that carries none of its fixed words is given the first, and one that has them is left as written", () => {
  assert.deepEqual(REFUSAL_WORDS, ["not in the warehouse", "license needed", "paused"]);
  assert.equal(REFUSAL_FIRST, "Not in the warehouse.");
  const gp02 = "The warehouse does not hold this figure. The CAISO SP15 hub has no 15-minute real-time rows for 7 November 2026 Pacific time.";
  assert.equal(withRefusalWords(gp02), `Not in the warehouse. ${gp02}`);
  assert.equal(withRefusalWords("I can't give this figure. The table is on Redivis."), "Not in the warehouse. I can't give this figure. The table is on Redivis.");
  for (const kept of ["Not in the warehouse. The table holds no hours for that day.", "Not in the warehouse this chat reads: x is on Redivis and not in the live set.",
    "not in the warehouse: no table holds futures.", "License needed. The only table that holds deals is held.", "NYISO's rows are held for a license (\"license needed\").",
    "MISO is paused while terms are reviewed, so no MISO figure is shown."]) assert.equal(withRefusalWords(kept), kept, kept);
  assert.equal(withRefusalWords("  The table holds no row.  "), "Not in the warehouse. The table holds no row.");
  assert.equal(withRefusalWords(""), "Not in the warehouse.");
  // the model's own sentence is not changed, and no figure is added
  assert.ok(!/\d/.test(REFUSAL_FIRST));
});

// Session 6106 (chain 280): the whole platform set asked once more on 14 November 2026 had two answers not right, pw13
// and pj08 (docs/reviews/ask-eval-2026-11-13.md). tests/test_session6106_ask.py holds the Python side and the stored runs.
test("a refusal states no figure: the figures of a refusal are found as the grader finds them", () => {
  const pw13 = "Not in the warehouse. It holds no forecast of ERCOT's summer 2028 peak demand, and I won't estimate one. The only peak figure I found is a past one: ERCOT's 2025 peak demand was 83,597 MW (grid_peak_vs_capacity, derived).";
  assert.deepEqual(refusalFigures(pw13, "What will ERCOT's peak demand be in the summer of 2028, in MW?"), ["83,597"]);
  // years, days of a month, hours held, a form's name and a list's markers are not figures
  assert.deepEqual(refusalFigures("Not in the warehouse. The table has no rows from 5 to 8 November 2026; it holds 72 of 168 hours and EIA-930 begins in 2018."), []);
  assert.deepEqual(refusalFigures("Not in the warehouse:\n1. no table holds futures\n2. none holds forwards"), []);
  // a number the question itself holds is the asker's
  assert.deepEqual(refusalFigures("Not in the warehouse: no plant of 1,227 MW is listed.", "Is there a 1,227 MW plant in the queue?"), []);
  assert.deepEqual(refusalFigures("Not in the warehouse. The nearest price is 41.81 USD/MWh, and the table holds 38,201 rows."), ["41.81", "38,201"]);
  assert.deepEqual(refusalFigures(""), []);
  const words = refusalFigureProblem(["83,597"]);
  assert.match(words, /^a refusal that states a figure \(83,597\): rule 3 says a refusal states no numbers\./);
  assert.match(words, /answer the question with not_in_warehouse false$/);
});

test("an answer written after a table was refused as license needed carries the hold's words", () => {
  const words = new Map([["isone_interconnection_queue", "table isone_interconnection_queue is license needed: ISO-NE: the publisher's own page asks for permission; none is recorded yet."],
    ["eia_crude_imports_by_country", notLiveWords("eia_crude_imports_by_country")]]);
  assert.deepEqual(heldTables(words), ["isone_interconnection_queue"]);
  assert.deepEqual(heldTables({ b: "table b is license needed: x", a: "table a is license needed: y" }), ["a", "b"]);
  const pj08 = "I can't give a figure from ISO-NE's own queue table. isone_interconnection_queue is held because it needs a license. Berkeley Lab's national queue file is a separate public source.";
  assert.equal(withHoldWords(pj08, heldTables(words)), `isone_interconnection_queue: license needed, so no figure of it is given here. ${pj08}`);
  assert.equal(withHoldWords(pj08, ["a", "b"]), `a, b: license needed, so no figure of them is given here. ${pj08}`);
  // an answer that carries the words, and an answer with no table held, are as the model wrote them
  for (const kept of ["energy_deals is held (license needed), so no price is given. ERCOT's was 54.481 USD/MWh.", "License needed for the deals table."]) assert.equal(withHoldWords(kept, ["energy_deals"]), kept);
  assert.equal(withHoldWords(pj08, []), pj08);
  assert.equal(HOLD_WORDS, "license needed");
  assert.ok(REFUSAL_WORDS.includes(HOLD_WORDS));
});
