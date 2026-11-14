// Energy Research Warehouse (ERW) site, session 5251 (chain 238): the parts of scripts/eval-ask-site-loop.mjs and
// scripts/eval-loader.mjs that decide without a model and without a network: the .env reader, the reserve kept before
// a question, the record of an answer and of an error, and which specifiers the loader treats as packages. No build.
//
//   node --test site/scripts/test-eval-ask-site-loop.test.mjs
import test from "node:test";
import assert from "node:assert/strict";
import { GRID_SLUG, costOf, dotenv, recordOf, reserve, withRecord } from "./eval-ask-site-loop.mjs";
import { bare } from "./eval-loader.mjs";

test("dotenv reads KEY=value lines, drops quotes and leaves comments", () => {
  const env = dotenv('SUPABASE_URL=https://x.example\n# A_COMMENT=1\nANTHROPIC_API_KEY="abc"\r\nEMPTY=\n  SPACED = \'v w\'  \nlower=no\n');
  assert.equal(env.SUPABASE_URL, "https://x.example");
  assert.equal(env.ANTHROPIC_API_KEY, "abc");
  assert.equal(env.SPACED, "v w");
  assert.equal(env.EMPTY, "");
  assert.equal("A_COMMENT" in env, false);
  assert.equal("lower" in env, false);
});

test("the reserve: USD 0.30 for the first ten questions, then the dearest so far, at least USD 0.15", () => {
  assert.equal(reserve(0, 0), 0.3);
  assert.equal(reserve(9, 0.9), 0.3);
  assert.equal(reserve(10, 0.05), 0.15);
  assert.equal(reserve(40, 0.22), 0.22);
});

test("an answered question's record has the shape eval_loop.py's has, and says it came from the site's loop", () => {
  const q = { id: "pw01", grid: "ERCOT", via: "general", question: "What was it?" };
  const r = { status: "answered", model: "m", answer: "49,421.92 MW (eia930_all_demand)", citations: [{ table: "eia930_all_demand" }], tool_calls: 3, retried: false,
    cost_usd: 0.0712, seconds: 21.5, usage: { input: 1 }, reads: [{ table: "eia930_all_demand" }], trace: [{ name: "query", input: {}, out: {}, isError: false }, { name: "query", input: {}, out: {}, isError: true }] };
  const rec = recordOf(q, r, "2026-11-13T19:00:00Z", null);
  assert.equal(rec.loop, "site");
  assert.equal(rec.status, "answered");
  assert.equal(rec.not_in_warehouse, false);
  assert.equal(rec.refused, false);
  assert.equal(rec.cost_usd, 0.0712);
  assert.deepEqual(rec.trace.map((t) => t.is_error), [false, true]);
  assert.deepEqual(rec.trace.map((t) => t.isError), [false, true]);
  for (const k of ["id", "grid", "via", "question", "asked_at_utc", "http", "model", "answer", "why", "citations", "tool_calls", "retried", "seconds", "error", "reads", "nearest", "usage"]) assert.ok(k in rec, k);
});

test("a refusal and the fixed refusal are told apart", () => {
  const q = { id: "x", grid: "none", via: "general", question: "?" };
  assert.equal(recordOf(q, { status: "not_in_warehouse", cost_usd: 0.03 }, "t", null).not_in_warehouse, true);
  assert.equal(recordOf(q, { status: "refused_unverified", cost_usd: 0.09 }, "t", null).refused, true);
});

test("an error is a record with no answer and no cost, never a guess", () => {
  const rec = recordOf({ id: "x", grid: "none", via: "general", question: "?" }, null, "t", "Error: the cost ledger refused the site_ask_eval row");
  assert.equal(rec.status, "error");
  assert.equal(rec.answer, null);
  assert.equal(rec.cost_usd, 0);
  assert.deepEqual(rec.trace, []);
  assert.match(rec.error, /ledger/);
});

test("every grid a set may name has a slug", () => {
  for (const g of ["ERCOT", "CAISO", "NYISO", "SPP", "ISO-NE", "MISO", "PJM"]) assert.equal(typeof GRID_SLUG[g], "string");
});

test("the loader looks elsewhere for packages only, never for a path, an alias or a builtin", () => {
  assert.equal(bare("@anthropic-ai/sdk"), true);
  assert.equal(bare("server-only"), true);
  for (const s of ["./ask.ts", "../lib/chat/ask.ts", "/abs/x.mjs", "C:\\x\\y.mjs", "file:///x.mjs", "node:fs", "@/lib/supabase", "data:text/javascript,1"]) assert.equal(bare(s), false, s);
});

test("a question asked again in the same run: the earlier answer is kept, and its cost is still counted", () => {
  const order = ["a", "b", "c"];
  let run = { questions: [{ id: "c", cost_usd: 0.3 }, { id: "a", cost_usd: 0.1 }] };
  assert.equal(costOf(run), 0.4);
  run = withRecord(run, { id: "b", cost_usd: 0.2 }, order);
  assert.deepEqual(run.questions.map((x) => x.id), ["a", "b", "c"], "in the set's order");
  assert.equal("superseded" in run, false, "nothing was asked twice");
  run = withRecord(run, { id: "a", cost_usd: 0.05, again: true }, order);
  assert.deepEqual(run.questions.map((x) => [x.id, x.cost_usd]), [["a", 0.05], ["b", 0.2], ["c", 0.3]]);
  assert.deepEqual(run.superseded, [{ id: "a", cost_usd: 0.1 }]);
  assert.ok(Math.abs(costOf(run) - 0.65) < 1e-9, "the run's cost is what was spent, not what stands");
  run = withRecord(run, { id: "a", cost_usd: 0.01 }, order);
  assert.deepEqual(run.superseded.map((x) => x.cost_usd), [0.1, 0.05]);
  assert.equal(costOf({}), 0);
});
