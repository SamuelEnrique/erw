// Energy Research Warehouse (ERW) site, session 5251 (chain 238): the parts of scripts/eval-ask-site-loop.mjs and
// scripts/eval-loader.mjs that decide without a model and without a network: the .env reader, the reserve kept before
// a question, the record of an answer and of an error, and which specifiers the loader treats as packages. No build.
//
//   node --test site/scripts/test-eval-ask-site-loop.test.mjs
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { GRID_SLUG, askedUnder, costOf, dotenv, recordOf, reserve, withRecord } from "./eval-ask-site-loop.mjs";
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

// Session 5269. On 14 November 2026 gp01 ended in "stop_reason max_tokens" after eight model calls: its record said USD 0
// and the ledger held USD 0.3132, so the run's own cost, which the cap is counted on, was short by a question.
test("an error after model calls were made is recorded at what the loop had counted, and the cap counts it", () => {
  const q = { id: "gp01", grid: "none", via: "general", question: "?" };
  const meter = { cost_usd: 0.3132, tool_calls: 7, usage: { input: 16, output: 17002, cache_write: 0, cache_read: 250000, requests: 8 }, stop: "max_tokens",
    trace: [{ tool: "query", input: { table: "eia930_all_demand" }, out: { rows_matched: 0 }, isError: false }] };
  const rec = recordOf(q, null, "t", "Error: stop_reason max_tokens", meter);
  assert.equal(rec.status, "error");
  assert.equal(rec.answer, null);
  assert.equal(rec.cost_usd, 0.3132);
  assert.equal(rec.tool_calls, 7);
  assert.equal(rec.usage.requests, 8);
  assert.equal(rec.stopped_at, "max_tokens");
  assert.deepEqual(rec.trace.map((t) => [t.tool, t.is_error]), [["query", false]]);
  assert.ok(Math.abs(costOf({ questions: [{ id: "a", cost_usd: 0.1 }, rec] }) - 0.4132) < 1e-9);
  // an error before any model call (no key, a refused ledger row at the first call) has an empty meter: no cost, as before
  assert.equal(recordOf(q, null, "t", "Error: x", {}).cost_usd, 0);
  // an answer that came back is its own count: the meter is not read, and it gains no field
  const ok = recordOf(q, { status: "answered", answer: "a", cost_usd: 0.05, tool_calls: 3, trace: [] }, "t", null, { cost_usd: 9, tool_calls: 99, stop: "end_turn" });
  assert.deepEqual([ok.cost_usd, ok.tool_calls, "stopped_at" in ok], [0.05, 3, false]);
  // the loop writes the meter after every model call, and the runner hands it one
  const loop = fs.readFileSync(new URL("../lib/chat/ask.ts", import.meta.url), "utf8");
  assert.ok(loop.includes("if (opts.meter) Object.assign(opts.meter, { cost_usd: spent, tool_calls: calls, usage: { ...usage }, stop: resp.stop_reason, ...(tracing ? { trace: traced } : {}) });"));
  const runner = fs.readFileSync(new URL("./eval-ask-site-loop.mjs", import.meta.url), "utf8");
  assert.ok(runner.includes('questionId: crypto.randomBytes(16).toString("hex"), meter });'));
  assert.ok(runner.includes("recordOf(q, r, at, error, meter)"));
});

// Session 5271: an asking at another effort than the spec's (ASK_WRITER_EFFORT, the loop's own switch) says so in every record
test("a record says what it was asked under: the effort, the output limit, the thinking switch when set", () => {
  const spec = { effort: "high", max_tokens: 16000, system: "You answer.\n\nRules:\n1. One.\n2. Two.\n\n# Briefing\n\n1. a numbered line of the briefing is not a rule\n" };
  assert.deepEqual(askedUnder({}, spec), { effort: "high", max_tokens: 16000, rules: 2 });
  assert.deepEqual(askedUnder({ ASK_WRITER_EFFORT: "medium" }, spec), { effort: "medium", max_tokens: 16000, rules: 2 });
  assert.deepEqual(askedUnder({ ASK_WRITER_EFFORT: "low", ASK_THINKING: "between_tools" }, spec), { effort: "low", max_tokens: 16000, rules: 2, thinking: "between_tools" });
  assert.equal(askedUnder({}, { effort: "high", max_tokens: 16000 }).rules, 0);
  assert.equal(askedUnder({}, JSON.parse(fs.readFileSync(new URL("../lib/chat/spec.json", import.meta.url), "utf8"))).rules, 11);   // the prompt as it stands
  const runner = fs.readFileSync(new URL("./eval-ask-site-loop.mjs", import.meta.url), "utf8");
  assert.ok(runner.includes("const rec = { ...recordOf(q, r, at, error, meter), asked_under: under };"));
  // the effort the record names is the one the loop sends: the same switch, read the same way
  const loop = fs.readFileSync(new URL("../lib/chat/ask.ts", import.meta.url), "utf8");
  assert.ok(loop.includes("return env.ASK_WRITER_EFFORT || own;"));
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
