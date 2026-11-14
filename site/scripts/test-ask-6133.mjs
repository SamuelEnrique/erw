// Energy Research Warehouse (ERW) site, session 6133 (chain 281): the loop names a table of the record the chat cannot
// read (lib/chat/refused.ts unlistedNamed, unlistedTables, withUnlistedWords, as warehouse/chat/ask.py). No model.
//
//   node scripts/test-ask-6133.mjs
//
// Prints one JSON line of what the functions return for the cases of tests/fixtures/session6133/unlisted.json;
// tests/test_session6133_ask.py sets the line against the Python functions on the same cases.
import assert from "node:assert/strict";
import fs from "node:fs";
import { unlistedNamed, unlistedTables, withUnlistedWords } from "../lib/chat/refused.ts";

const fx = JSON.parse(fs.readFileSync(new URL("../../tests/fixtures/session6133/unlisted.json", import.meta.url), "utf8"));
const verdictOf = (t) => fx.verdicts[t];
const named = Object.fromEntries(fx.questions.map((q) => [q.id, unlistedNamed(q.question, fx.names)]));
const said = Object.fromEntries(fx.answers.map((a) => [a.id, withUnlistedWords(a.answer, a.tables, verdictOf)]));
const lists = Object.fromEntries(fx.records.map((r) => [r.id, unlistedTables(r.records, fx.names)]));
console.log(JSON.stringify({ named, said, lists }));
for (const q of fx.questions) assert.deepEqual(named[q.id], q.named, q.id);
for (const a of fx.answers) assert.equal(said[a.id], a.said, a.id);
for (const r of fx.records) assert.deepEqual(lists[r.id], r.unlisted, r.id);
console.log("test-ask-6133: ok");
