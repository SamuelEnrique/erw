// Energy Research Warehouse (ERW) site, session 5256 (chain 238): a table a tool refuses to read (lib/chat/refused.ts),
// as warehouse/chat/tools.py and warehouse/chat/ask.py hold the same words and the same rule
// (tests/test_session5256_ask.py holds the Python side and both loops turn by turn). No build, no network: node strips
// the file's types.
//
//   node --test site/scripts/test-ask-refused.test.mjs
import test from "node:test";
import assert from "node:assert/strict";
import { notLiveWords, refusedAgainNote, refusedRead, refusedWhole, tablesNamed } from "../lib/chat/refused.ts";

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
