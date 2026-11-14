// Energy Research Warehouse (ERW) site, session 6136 (chain 281): a date in words, and the list that says which table
// the question names and this site cannot read (lib/chat/refused.ts plainDates, withAskedAbout, as warehouse/chat/ask.py
// plain_dates, with_asked_about). No model, no request.
//
//   node scripts/test-ask-6136.mjs
//
// Prints one JSON line; tests/test_session6136_ask.py sets it against the Python functions on the same cases
// (tests/fixtures/session6136/cases.json).
import assert from "node:assert/strict";
import fs from "node:fs";
import { plainDates, withAskedAbout } from "../lib/chat/refused.ts";

const fx = JSON.parse(fs.readFileSync(new URL("../../tests/fixtures/session6136/cases.json", import.meta.url), "utf8"));
const dates = Object.fromEntries(fx.dates.map((c) => [c.id, plainDates(c.text)]));
const lists = Object.fromEntries(fx.lists.map((c) => {
  const r = withAskedAbout(c.out, c.question, c.input, fx.verdicts);
  return [c.id, { keys: Object.keys(r.out), told: Object.keys(r.told), words: Object.values(r.told) }];
}));
console.log(JSON.stringify({ dates, lists }));
for (const c of fx.dates) assert.equal(dates[c.id], c.plain, c.id);
for (const c of fx.lists) {
  assert.deepEqual(lists[c.id].told, c.told, c.id);
  assert.deepEqual(lists[c.id].keys, c.keys, c.id);
}
console.log("test-ask-6136: ok");
