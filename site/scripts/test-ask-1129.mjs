// Energy Research Warehouse (ERW) site, session 1129: the general chat's conversation (lib/chat/history.ts). No model,
// no request.
//
//   node --import ./scripts/alias-register.mjs scripts/test-ask-1129.mjs
import assert from "node:assert/strict";
import fs from "node:fs";

const { cleanTurns, generalOpening } = await import("../lib/chat/history.ts");
const loop = fs.readFileSync(new URL("../lib/chat/ask.ts", import.meta.url), "utf8");
const route = fs.readFileSync(new URL("../app/api/ask/route.ts", import.meta.url), "utf8");

let n = 0, failed = 0;
const test = (name, f) => {
  n += 1;
  try { f(); console.log(`ok ${n} ${name}`); } catch (e) { failed += 1; console.log(`FAIL ${n} ${name}\n   ${e.message.split("\n").slice(0, 6).join("\n   ")}`); }
};

test("with no earlier turn the first message is byte for byte what it was", () => {
  assert.equal(generalOpening("What was X?", "2026-10-23", []), "Today is 2026-10-23 (UTC).\n\nQuestion: What was X?");
  assert.equal(generalOpening("What was X?", "2026-10-23", cleanTurns(undefined)), "Today is 2026-10-23 (UTC).\n\nQuestion: What was X?");
});

test("earlier turns come first, in Ask ERCOT's words, with what each read", () => {
  const past = cleanTurns([{ question: "Q1?", answer: "A1 was 36.70 USD/MWh.", reads: [{ table: "cost_of_power_monthly", entity: "ercot:HB_HUBAVG", aggregation: "mean" }], citations: [{ table: "cost_of_power_monthly" }] }]);
  const text = generalOpening("And the year before?", "2026-10-23", past);
  assert.ok(text.startsWith("The conversation so far, oldest first. The new question continues it.\n\nEarlier question 1: Q1?\nYour answer: A1 was 36.70 USD/MWh.\nQueries you ran: query {\"aggregation\":\"mean\",\"entity\":\"ercot:HB_HUBAVG\",\"table\":\"cost_of_power_monthly\"}"), text);
  assert.ok(text.endsWith("Today is 2026-10-23 (UTC).\n\nQuestion: And the year before?"));
  assert.deepEqual(past[0].tables, ["cost_of_power_monthly"]);
});

test("a turn is kept only with a question and an answer; the last three only; a bad table name dropped", () => {
  const many = Array.from({ length: 5 }, (_, i) => ({ question: `Q${i}`, answer: `A${i}` }));
  assert.deepEqual(cleanTurns(many).map((t) => t.question), ["Q2", "Q3", "Q4"]);
  assert.deepEqual(cleanTurns([{ question: "Q" }, { answer: "A" }, null, "x"]), []);
  assert.deepEqual(cleanTurns([{ question: "Q", answer: "A", citations: [{ table: "x; drop" }, { table: "ok_table" }] }])[0].tables, ["ok_table"]);
});

test("the loop counts an earlier answer's numbers as given and its tables as read; the route passes the turns", () => {
  assert.ok(loop.includes("const past = profile ? [] : cleanTurns(opts.history);"));
  assert.ok(loop.includes("...past.flatMap((t) => [t.answer, ...t.queries])]"));
  assert.ok(loop.includes("...past.flatMap((t) => t.tables)]"));
  assert.ok(route.includes("{ questionId: qid, history, ...ledgerOpts }"));
});

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
