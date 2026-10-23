// Energy Research Warehouse (ERW) site, session 1110: the number check on six answers (three clean, three with a figure
// no tool returned in the unit stated), against two tool results recorded from session 1109's saved rows. No model and
// no request.
//
//   node --import ./scripts/alias-register.mjs scripts/test-ask-1110.mjs
//
// Prints one JSON line of what the check returns for each answer, then the tests; tests/test_session1110.py sets the
// JSON line against warehouse/chat/ask.py's own check on the same strings, so the two languages agree.
import assert from "node:assert/strict";
import fs from "node:fs";

const read = (p) => JSON.parse(fs.readFileSync(new URL(p, import.meta.url), "utf8"));
const SRC = read("../../tests/fixtures/session1110/sources.json");
const ANS = read("../../tests/fixtures/session1110/answers.json");
const spec = read("../lib/chat/spec.json");
const { unverified, unitMismatches, numbers, isName } = await import("../lib/chat/ask.ts");

const sources = [SRC.question, ...SRC.sources];
const got = Object.fromEntries(ANS.answers.map((a) => [a.id, { untraced: unverified(a.answer, sources), units: unitMismatches(a.answer, sources) }]));
console.log(JSON.stringify({ results: got }));

let n = 0, failed = 0;
const test = (name, f) => {
  n += 1;
  try { f(); console.log(`ok ${n} ${name}`); } catch (e) { failed += 1; console.log(`FAIL ${n} ${name}\n   ${e.message.split("\n").slice(0, 6).join("\n   ")}`); }
};

test("the six answers: three clean, three sent back for what each names", () => {
  for (const a of ANS.answers) assert.deepEqual(got[a.id], { untraced: a.untraced, units: a.units }, a.id);
  assert.equal(ANS.answers.filter((a) => !a.untraced.length && !a.units.length).length, 3);
});

test("a form name is not a figure; a minus after a space still is", () => {
  assert.deepEqual(numbers("from EIA-930 and EIA-860M"), []);
  assert.deepEqual(numbers("fell -3.2 to (-1.5)"), [[-3.2, 1], [-1.5, 1]]);
  assert.deepEqual(numbers("2026-09-22"), [[2026, 0], [9, 0], [22, 0]]);
  assert.equal(isName("EIA-930", 4), true);
  assert.equal(isName("a -930", 3), false);
});

test("a unit with no money in it, or a compound unit, is not judged", () => {
  const s = [JSON.stringify({ units: ["MWh/MW"], result: [{ value: 150.5 }] }), JSON.stringify({ units: ["USD/MW-month"], result: [{ value: 7.25 }] })];
  assert.deepEqual(unitMismatches("It discharged 150.5 MWh per MW, at USD 7.25 per MW-month.", s), []);
  assert.deepEqual(unitMismatches("It discharged 150.5 MWh per MW.", s), []);
});

test("a figure in a per-kW key traces as USD per kW", () => {
  const s = [JSON.stringify({ units: ["USD/MW"], result: [{ value: 81402.1896, value_usd_per_kw: 81.4022 }] })];
  assert.deepEqual(unitMismatches("The total is 81.40 USD per kW.", s), []);
  assert.deepEqual(unitMismatches("The total is $81,402.19/kW.", s), ["81402.19 USD/kW (the tools gave it in USD/MW)"]);
});

test("the refusal begins with the words of the rule", () => {
  assert.match(spec.refusal, /^The warehouse does not hold that figure: /);
});

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
