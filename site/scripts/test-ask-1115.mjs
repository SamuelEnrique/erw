// Energy Research Warehouse (ERW) site, session 1115: what an answer shows under it, the table and the window each
// figure came from (lib/chat/ask.ts readsOf), and the panel's words for a refused answer. No model and no request.
//
//   node --import ./scripts/alias-register.mjs scripts/test-ask-1115.mjs
import assert from "node:assert/strict";
import fs from "node:fs";

const { readsOf } = await import("../lib/chat/ask.ts");
const panel = fs.readFileSync(new URL("../components/ask/AskPanel.tsx", import.meta.url), "utf8");
const loop = fs.readFileSync(new URL("../lib/chat/ask.ts", import.meta.url), "utf8");
// session 1194: the reads are drawn by the answer's sources (components/ask/AnswerSources.tsx), under every chat's answer
const sources = fs.readFileSync(new URL("../components/ask/AnswerSources.tsx", import.meta.url), "utf8");

let n = 0, failed = 0;
const test = (name, f) => {
  n += 1;
  try { f(); console.log(`ok ${n} ${name}`); } catch (e) { failed += 1; console.log(`FAIL ${n} ${name}\n   ${e.message.split("\n").slice(0, 6).join("\n   ")}`); }
};

test("a query reads its table, its rows and its window, and no figure", () => {
  const q = { table: "battery_stack_monthly", aggregation: "sum", entity: "ercot:HB_HUBAVG", variable: "foresight_4h_revenue_total_usd_per_mw", start: "2025-10-01", end: "2026-10-01", percentile: 90 };
  assert.deepEqual(readsOf("query", q), [{ table: "battery_stack_monthly", entity: "ercot:HB_HUBAVG", variable: "foresight_4h_revenue_total_usd_per_mw", start: "2025-10-01", end: "2026-10-01", aggregation: "sum" }]);
});

test("a compare reads both sides; list_tables and describe_table read no rows", () => {
  const a = { table: "cost_of_power_monthly", aggregation: "mean", entity: "ercot:HB_HUBAVG" }, b = { table: "cost_of_power_monthly", aggregation: "mean", entity: "spp:SPPNORTH_HUB" };
  assert.deepEqual(readsOf("compare", { a, b }).map((r) => r.entity), ["ercot:HB_HUBAVG", "spp:SPPNORTH_HUB"]);
  assert.deepEqual(readsOf("list_tables", { sector: "power" }), []);
  assert.deepEqual(readsOf("describe_table", { table: "x" }), []);
  assert.deepEqual(readsOf("query", { aggregation: "sum" }), []);
});

test("the loop lists a read only when the call answered and was not a held grid's", () => {
  assert.ok(loop.includes("if (!isError && !out.held) for (const r of readsOf(name, input))"));
  assert.ok(loop.includes("...(readsLog.length ? { reads: readsLog } : {})"));
});

test("the panel draws the reads, the time it took, and the refusal in its own words", () => {
  assert.ok(panel.includes("<AnswerSources citations={res.citations} reads={res.reads} />") && sources.includes("data-reads={rs.length}"));
  assert.ok(panel.includes("Answered in {res.seconds.toFixed(1)} seconds"));
  assert.ok(panel.includes('refused_unverified: "The warehouse does not hold that figure"'));
});

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
