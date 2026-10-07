// Energy Research Warehouse (ERW) site, session 143: Ask ERCOT's speed. What the session added, tested with no model
// call and no request: the stage timings sum to the whole; tool calls read together return what the same calls return
// one after another (on reads recorded from the live set, tests/fixtures/session143/tool_reads.json); a grouped result
// carries a summary that is its own rows'; the summaries cache does not hide a newer day; the number check still
// refuses an unverified number, also for words shown before the whole answer; a repeated call is known as one; the
// spending cap of the runner stops before a question; the ceilings are as they were.
//
//   node --import ./scripts/alias-register.mjs scripts/test-ask-speed.mjs
//
// Exit 1 on a failure.
import assert from "node:assert/strict";
import fs from "node:fs";
import * as st from "../lib/chat/stages.ts";
import * as sm from "../lib/chat/summaries.ts";
import { mayAsk, sessionSpend } from "./eval-spend.mjs";

let n = 0;
const test = async (name, fn) => { await fn(); n += 1; console.log(`ok   ${name}`); };
const read = (p) => fs.readFileSync(new URL(p, import.meta.url), "utf8");
const FIX = JSON.parse(read("../../tests/fixtures/session143/tool_reads.json"));

// the recorded reads stand in for the database: a request that was not recorded fails the test
process.env.SUPABASE_URL = "https://fixture.invalid";
process.env.SUPABASE_ANON_KEY = "fixture";
let requests = 0;
globalThis.fetch = async (url) => {
  requests += 1;
  const body = FIX.reads[String(url)];
  if (body === undefined) throw new Error(`a read that was not recorded: ${String(url).slice(0, 200)}`);
  await new Promise((r) => setTimeout(r, 1 + (requests % 3)));       // reads end in another order than they began
  return new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } });
};
const { runTool, groupSummary } = await import("../lib/chat/tools.ts");
const ask = await import("../lib/chat/ask.ts");
const { ercotProfile, FIELD_ORDER, PLANNER } = await import("../lib/chat/ercot.ts");
const limits = await import("../lib/chat/limits.ts");
const profile = ercotProfile();

await test("the stages sum to the whole, exactly, and what is not a named stage is other", async () => {
  let now = 1000;
  const c = st.stageClock(1000, () => now);
  c.add("other", "admit", 120);
  now += 120;
  await c.time("planning", "model", async () => { now += 2301; });
  await c.time("fetching", "tools", async () => { now += 187; });
  await c.time("writing", "model", async () => { now += 2950; });
  c.wordsAt(now - 700);
  c.add("writing", "check", 1);
  now += 1;
  c.add("drawing", "series", 2);
  now += 2 + 37;                                                      // the ledger's rows: nobody's stage
  const s = c.done();
  assert.deepEqual(s, { planning: 2301, fetching: 187, drawing: 2, writing: 2951, other: 157, total: 5598 });
  assert.equal(s.planning + s.fetching + s.drawing + s.writing + s.other, s.total);
  assert.equal(c.wordsMs, 4858);
  c.wordsReset();
  assert.equal(c.wordsMs, null);
  // steps recorded by rounding cannot make the parts pass the whole
  const t = st.sumStages([{ stage: "planning", what: "model", ms: 10 }, { stage: "writing", what: "model", ms: 10 }], 19);
  assert.equal(t.planning + t.fetching + t.drawing + t.writing + t.other, t.total);
  assert.ok(t.other >= 0);
  assert.deepEqual(st.STAGES, ["planning", "fetching", "drawing", "writing", "other"]);
});

await test("the same stages on every answer of the first run of the session, summing to the whole", () => {
  const f = new URL("../../warehouse/chat/eval_ercot_speed_results.csv", import.meta.url);
  if (!fs.existsSync(f)) return;                                       // written at the end of the session
  const lines = fs.readFileSync(f, "utf8").split("\n").filter((l) => l && !l.startsWith("#"));
  // a field in quotes may hold commas (a question does)
  const cells = (l) => { const out = []; let cur = "", q = false; for (let i = 0; i < l.length; i++) { const ch = l[i]; if (q) { if (ch === '"' && l[i + 1] === '"') { cur += '"'; i++; } else if (ch === '"') q = false; else cur += ch; } else if (ch === '"') q = true; else if (ch === ",") { out.push(cur); cur = ""; } else cur += ch; } out.push(cur); return out; };
  const head = cells(lines[0]);
  const col = (k) => head.indexOf(k);
  let rows = 0;
  for (const l of lines.slice(1)) {
    const v = cells(l);
    for (const p of ["before", "after"]) {
      if (v[col(`${p}_total_ms`)] === "") continue;
      const parts = ["planning", "fetching", "drawing", "writing", "other"].map((k) => Number(v[col(`${p}_${k}_ms`)]));
      assert.equal(parts.reduce((a, b) => a + b, 0), Number(v[col(`${p}_total_ms`)]), `${v[0]} ${p}`);
      rows += 1;
    }
  }
  assert.ok(rows >= 20);
});

await test("tool calls read together return what the same calls return one after another", async () => {
  const one = [];
  for (const c of FIX.calls) one.push(await runTool(c.name, c.input, profile.scope));
  const together = await Promise.all(FIX.calls.map((c) => runTool(c.name, c.input, profile.scope)));
  const again = await Promise.all([...FIX.calls].reverse().map((c) => runTool(c.name, c.input, profile.scope)));
  assert.deepEqual(together, one);
  assert.deepEqual(again.reverse(), one);
  assert.deepEqual(JSON.parse(JSON.stringify(one)), FIX.results);       // and what the live set returned when it was recorded
  assert.ok(one.every((r) => !r.isError));
});

await test("a grouped result carries a summary that is its own rows', and a single figure carries none", async () => {
  const [byDay, byYear, single] = await Promise.all(FIX.calls.map((c) => runTool(c.name, c.input, profile.scope)));
  const rows = byDay.out.result, s = byDay.out.summary;
  const vals = rows.map((r) => r.value);
  assert.equal(s.rows, rows.length);
  assert.equal(s.lowest.value, Math.min(...vals));
  assert.equal(s.highest.value, Math.max(...vals));
  assert.deepEqual(s.first, { day: rows[0].day, value: rows[0].value });
  assert.deepEqual(s.last, { day: rows.at(-1).day, value: rows.at(-1).value });
  assert.equal(rows.find((r) => r.day === s.highest.day).value, s.highest.value);
  assert.ok(Math.abs(s.change_first_to_last - (rows.at(-1).value - rows[0].value)) < 1e-6);
  assert.ok(Math.abs(s.mean_of_rows - vals.reduce((a, b) => a + b, 0) / vals.length) < 1e-5);
  assert.ok(byYear.out.summary && byYear.out.summary.rows === byYear.out.result.length);
  assert.equal(single.out.summary, undefined);
  assert.equal(groupSummary("day", [{ day: "2026-01-01", value: 1 }], [], "mean", undefined, "series"), null);
  // every number of the summary is in the tool result, so the number check passes an answer that states it
  assert.deepEqual(ask.unverified(`It ranged from ${s.lowest.value} to ${s.highest.value}.`, [JSON.stringify(byDay.out)]), []);
});

await test("the summaries cache gives the newer day once its life has passed, and never keeps a failed read", async () => {
  assert.ok(sm.LIFE_MS <= 600_000);
  let now = 0, last = "2026-10-05", fail = false, reads = 0;
  const cache = sm.keep(sm.LIFE_MS, async (table) => { reads += 1; if (fail) throw new Error("the read was cancelled"); return { table, first: "2026-08-26", last, rows: null }; }, () => now);
  assert.equal((await cache.get("eia930_all_demand")).last, "2026-10-05");
  last = "2026-10-06";                                                 // the table grows
  now = sm.LIFE_MS - 1;
  assert.equal((await cache.get("eia930_all_demand")).last, "2026-10-05");   // within its life: the held one
  now = sm.LIFE_MS;
  assert.equal((await cache.get("eia930_all_demand")).last, "2026-10-06");   // at its life's end: read again
  assert.equal(reads, 2);
  fail = true; now += sm.LIFE_MS;
  await assert.rejects(cache.get("eia930_all_demand"));
  await new Promise((r) => setTimeout(r, 0));
  fail = false; last = "2026-10-07";
  assert.equal((await cache.get("eia930_all_demand")).last, "2026-10-07");   // the failure was not kept: no wait, no stale day
  assert.equal(await sm.within(new Promise(() => {}), 5), null);              // a question does not wait for a summary
});

await test("the summaries tell the planner that a query governs, and the rule of session 137 stands", () => {
  const text = sm.summaryText([{ table: "eia930_all_demand", first: "2026-08-26T00:00:00Z", last: "2026-10-05T23:00:00Z", rows: null, held: true, dated: true },
    { table: "ercot_all_hub_prices_history", first: null, last: null, rows: null, held: false },
    { table: "clean_energy_summary", first: "2019-01-01", last: "2026-09-01", rows: null, held: true, dated: true, variables: ["carbon_free_share_pct", "cf_share_pct_h00", "cf_share_pct_h01", "cf_share_pct_h23"] }], "2026-10-07T10:30:00.000Z");
  for (const words of ["eia930_all_demand: rows dated 2026-08-26 to 2026-10-05", "a query's own rows govern", "is still queried before it is called not held", "not in this site's live set", "cf_share_pct_h00 to cf_share_pct_h23", "read at 2026-10-07T10:30Z"])
    assert.ok(text.includes(words), words);
  assert.equal(sm.summaryText([], "2026-10-07T10:30:00.000Z"), "");
  assert.ok(profile.system.includes("Never say that a recent day, yesterday or this week is not held without a query that came back empty"));
  assert.ok(profile.system.includes("ONE READING TURN"));
  assert.deepEqual(sm.foldHours(["a", "x_h00", "x_h01", "x_h02", "b"]), ["a", "x_h00 to x_h02", "b"]);
});

await test("the number check still refuses an unverified number", () => {
  const sources = [JSON.stringify(FIX.results[2].out)];
  assert.deepEqual(ask.unverified("ERCOT's carbon intensity was 340.35 kgCO2/MWh.", sources), []);
  assert.deepEqual(ask.unverified("ERCOT's carbon intensity was 340.35 kgCO2/MWh, down from 361.2.", sources), ["361.2"]);
  assert.deepEqual(ask.unverified("It was 341 kgCO2/MWh.", sources), ["341"]);
});

await test("words are shown only once the answer's string is whole, and never with an untraced number or a wrong form", () => {
  const whole = JSON.stringify({ form: "sentence", not_in_warehouse: false, series: [], premise: "", answer: "It was 340.35 kgCO2/MWh (carbon_intensity_monthly).", citations: [], nearest: [], followups: [] });
  const cut = whole.indexOf("(carbon");
  assert.equal(st.partialDraft(whole.slice(0, cut)), null);                           // the answer is still being written
  assert.equal(st.partialDraft('{"form":"sentence","not_in_warehouse":false'), null);
  const head = st.partialDraft(whole.slice(0, whole.indexOf('","citations"') + 1));
  assert.deepEqual(head, { form: "sentence", not_in_warehouse: false, series: [], premise: "", answer: "It was 340.35 kgCO2/MWh (carbon_intensity_monthly)." });
  assert.equal(st.partialDraft('{"premise":"the \\"answer\\": \\"x\\" is given","answer":"unfinished'), null);
  assert.equal(st.partialDraft('{"form":"words","answer":"a \\"quoted\\" word","citations":[').answer, 'a "quoted" word');
  const records = [{ tool: "query", input: FIX.calls[2].input, out: { result_id: "r1", ...FIX.results[2].out }, isError: false }];
  const sources = records.map((r) => JSON.stringify(r.out));
  // what lib/chat/ask.ts asks before it sends the words: the number check on the answer, and the profile's check of the head
  const shown = (h) => ask.unverified(String(h.answer), sources).length === 0 && profile.early(h, records, []).length === 0;
  assert.equal(shown(head), true);
  assert.equal(shown({ ...head, answer: "It was 999.9 kgCO2/MWh." }), false);
  assert.equal(shown({ ...head, series: ["r1"] }), false);                             // a series under one figure
  assert.equal(shown({ ...head, form: "chart" }), false);                              // a chart that names no series
  assert.equal(shown({ ...head, premise: "The question assumes 77 percent." }), false);
  assert.equal(shown({ ...head, form: undefined }), false);
  // the fields are written in the order that makes this possible, and they are the exported spec's fields
  const props = Object.keys(profile.schema.properties);
  assert.deepEqual(props, FIELD_ORDER);
  assert.ok(props.indexOf("answer") > props.indexOf("premise") && props.indexOf("answer") < props.indexOf("citations"));
  assert.deepEqual([...profile.schema.required].sort(), [...FIELD_ORDER].sort());
});

await test("a follow-up question that fails its check is left out, and only then may the answer stand", () => {
  const records = [{ tool: "query", input: {}, out: { result: [{ value: 43.25 }] }, isError: false }];
  const mended = profile.mend({ answer: "x", citations: [], not_in_warehouse: false, followups: ["How many hours were above 200 USD/MWh?", "What was the price in 2025?", "And the day before?"] }, records);
  assert.deepEqual(mended.followups, ["What was the price in 2025?", "And the day before?"]);
  assert.equal(profile.tailOnly(["follow-up questions contain numbers in no tool result: 200"]), true);
  assert.equal(profile.tailOnly(["followups must be two or three questions (1 given)"]), true);
  assert.equal(profile.tailOnly(["follow-up questions contain numbers in no tool result: 200", "premise contains numbers in no tool result and not in the question: 5"]), false);
  assert.equal(profile.tailOnly([]), false);
  const loop = read("../lib/chat/ask.ts");
  assert.ok(loop.includes("if (!c.bad.length && !c.uncited.length && !c.noCite && profile?.mend && profile.tailOnly?.(c.more))"));
});

await test("a call made twice with the same arguments is known as one", () => {
  assert.equal(st.callKey("query", { table: "t", variable: "v", where: { b: "2", a: "1" } }), st.callKey("query", { where: { a: "1", b: "2" }, variable: "v", table: "t" }));
  assert.notEqual(st.callKey("query", { table: "t", aggregation: "mean" }), st.callKey("query", { table: "t", aggregation: "max" }));
  const loop = read("../lib/chat/ask.ts");
  assert.ok(loop.includes("const outs = await Promise.all(blocks.map((b, i) => (slots[i] ? runTool(b.name, b.input, scope) : null)));"));
  assert.ok(loop.includes("if (profile && blocks.length && fresh === 0) forceWrite = true;"));
});

await test("the planner is the writer's own model unless a priced model is named, and the model's own setting of thought is not changed", () => {
  assert.equal(PLANNER, "writer");
  assert.equal(profile.planner, "writer");
  assert.equal(profile.thinking, undefined);
  const spec = JSON.parse(read("../lib/chat/spec.json"));
  assert.ok(spec.prices["claude-haiku-4-5"] && spec.prices["claude-sonnet-5-5"]);
});

await test("the runner's cap is asked before a question, never after", () => {
  const file = { runs: [{ name: "before_sample", usd: 0.6467 }, { name: "probes", usd: 0.2322 }] };
  assert.ok(Math.abs(sessionSpend(file) - 0.8789) < 1e-9);
  assert.equal(mayAsk(2.64, 0.15, 2.8), true);
  assert.equal(mayAsk(2.66, 0.15, 2.8), false);                        // one more question could pass the stop: it is not asked
  assert.equal(mayAsk(2.8, 0.15, 2.8), false);
  const run = read("./eval-ask-speed.mjs");
  assert.ok(run.indexOf("if (!mayAsk(sessionSpend(spend), reserve, stop))") < run.indexOf("a = await one(q,"));
  assert.ok(run.includes("mine.usd + (known ? cost : reserve)"));     // an unknown cost counts as the reserve
  assert.ok(run.includes("fs.appendFileSync(out, JSON.stringify(line)"));  // an answer paid for is always written
  assert.ok(run.includes("this runner asks a local server only"));
});

await test("the ceilings and the per-visitor limit are as they were, and a question is admitted before any model call", () => {
  const file = JSON.parse(read("../lib/chat/limits.json"));
  assert.deepEqual([file.daily_usd, file.monthly_usd, file.per_visitor_per_day], [3, 30, 15]);
  assert.deepEqual(limits.readLimits({}, file), { daily_usd: 3, monthly_usd: 30, per_visitor_per_day: 15 });
  const route = read("../app/api/ask/route.ts");
  assert.ok(route.indexOf("const admitted = await admit(") < route.indexOf("await ask(asked"));
  assert.ok(route.indexOf("if (!admitted.ok) {") < route.indexOf("const timing = {"));
  assert.ok(!/ASK_DAILY_USD|ASK_MONTHLY_USD|ASK_PER_VISITOR/.test(read("../lib/chat/ask.ts") + read("../lib/chat/ercot.ts") + read("../lib/chat/tools.ts")));
});

console.log(`${n} tests pass`);
