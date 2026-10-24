// Energy Research Warehouse (ERW) site, session 1142 (chain 076's session 1130): the general chat's chart
// (lib/chat/generalseries.ts), on the stored answers of session 1113's run with their tool records
// (warehouse/chat/eval/eval_s1113_run.json). No model and no request.
//
//   node --import ./scripts/alias-register.mjs scripts/test-ask-1142.mjs
import assert from "node:assert/strict";
import fs from "node:fs";

const RUN = JSON.parse(fs.readFileSync(new URL("../../warehouse/chat/eval/eval_s1113_run.json", import.meta.url), "utf8"));
const Q = Object.fromEntries(RUN.questions.map((q) => [q.id, q]));
const { answerSeries, seriesOfResult } = await import("../lib/chat/generalseries.ts");
const loop = fs.readFileSync(new URL("../lib/chat/ask.ts", import.meta.url), "utf8");
const results = (q) => (q.trace ?? []).filter((t) => !t.isError && !t.out?.held).map((t) => ({ tool: t.tool, input: t.input, out: t.out }));
const cited = (q) => (q.citations ?? []).map((c) => c.table);

let n = 0, failed = 0;
const test = (name, f) => {
  n += 1;
  try { f(); console.log(`ok ${n} ${name}`); } catch (e) { failed += 1; console.log(`FAIL ${n} ${name}\n   ${e.message.split("\n").slice(0, 6).join("\n   ")}`); }
};

test("b07 (which month of 2025 earned most) rests on its months: the series is the tool's twelve rows, value by value", () => {
  const q = Q.b07, s = answerSeries(results(q), cited(q));
  assert.equal(s.length, 1);
  const t = results(q).filter((r) => r.tool === "query" && r.input.group_by === "month").pop();
  assert.equal(s[0].table, "battery_stack_monthly");
  assert.equal(s[0].group_by, "month");
  assert.deepEqual(s[0].rows.map((r) => [r.key, r.value]), t.out.result.map((r) => [String(r.month), r.value]));
  assert.ok(s[0].check.same && s[0].check.points === s[0].rows.length);
});

test("a series only of a cited table, only grouped by time, only with three rows or more", () => {
  const q = Q.b07;
  assert.deepEqual(answerSeries(results(q), ["merchant_revenue_monthly"]), []);
  assert.equal(seriesOfResult(1, { group_by: "entity" }, { table: "t", result: [{ entity: "a", value: 1 }, { entity: "b", value: 2 }, { entity: "c", value: 3 }] }), null);
  assert.equal(seriesOfResult(1, { group_by: "month" }, { table: "t", result: [{ month: "2025-01", value: 1 }, { month: "2025-02", value: 2 }] }), null);
});

test("a held grid's answer carries no series", () => {
  for (const id of ["g07", "g08", "d05", "d07"]) assert.deepEqual(answerSeries(results(Q[id]), cited(Q[id])).filter((s) => /nyiso|isone/.test(s.title)), [], id);
});

test("the loop: the general chat's answered answers only, and only a series that is the tool's rows", () => {
  assert.ok(loop.includes('if (!profile && !isError && !out.held && (name === "query" || name === "compare")) generalResults.push({ tool: name, input, out });'));
  assert.ok(loop.includes('if (!profile && status === "answered") {'));
});

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
