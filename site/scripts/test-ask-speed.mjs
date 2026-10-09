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
// Session 156: the query tool asks for a series by its entity alone, as a term of the request's "and"; when these reads
// were recorded it asked "this entity or this node" in one "or". The rows are the same (an entity is namespace:id, a
// node the id alone: no node bears an entity's name), so a recorded read is found by what it asks for, whichever way
// the entity is written. Everything else of a request must be as recorded, or the test fails as before.
const readKey = (url) => {
  const u = new URL(String(url)), q = Object.fromEntries(u.searchParams);
  let entity = null;
  const or = /^\(entity\.eq\.("[^"]*"),node\.eq\.\1\)$/.exec(q.or ?? "");
  if (or) { entity = or[1]; delete q.or; }
  const and = /^\(entity\.eq\.("[^"]*")(?:,(.*))?\)$/.exec(q.and ?? "");
  if (and) { entity = and[1]; if (and[2]) q.and = `(${and[2]})`; else delete q.and; }
  return JSON.stringify([u.pathname, entity, Object.keys(q).sort().map((k) => [k, q[k]])]);
};
const READS = new Map(Object.entries(FIX.reads).map(([k, v]) => [readKey(k), v]));
globalThis.fetch = async (url) => {
  requests += 1;
  const body = READS.get(readKey(url));
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
  // and what the live set returned when it was recorded; session 168 adds the local words beside each time (lib/chat/plaintime.ts),
  // which the recording, made before, does not hold: they are set apart and checked on their own
  const local = JSON.stringify(one, (k, v) => (k.endsWith("_local") ? undefined : v));
  assert.deepEqual(JSON.parse(local), FIX.results);
  assert.deepEqual([one[0].out.time_span.first_local, one[0].out.time_span.last_local], ["1 September 2026", "30 September 2026"]);
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

// ================================================================== session 148: the last seconds
// The tests above are session 143's, and their count line stands as it was. What session 148 added is tested below,
// counted apart, still with no model call and no request: the pages of one large read asked for together (on a read of
// three pages recorded from the live set, tests/fixtures/session148/paged_reads.json); the reserve prices by day and by
// month (the guide, the query tool's refusal of a long hourly read, on real rows of the trial table,
// tests/fixtures/session148/rollup_reads.json); the plan made by rule on the 100 questions; the two switches, off unless set.
const sb = await import("../lib/supabase.ts");
const roll = await import("../lib/chat/rollup.ts");
const { rulePlan, MAX_PLAN_GROUPS } = await import("../lib/chat/plan.ts");
const PAGED = JSON.parse(read("../../tests/fixtures/session148/paged_reads.json"));
const ROLLED = JSON.parse(read("../../tests/fixtures/session148/rollup_reads.json"));
const SET = JSON.parse(read("../../warehouse/chat/eval_ercot_panel.json")).questions;
let m = 0;
const test148 = async (name, fn) => { await fn(); m += 1; console.log(`ok   148: ${name}`); };
const fixtureFetch = globalThis.fetch;
const unhandled = [];
process.on("unhandledRejection", (e) => unhandled.push(e));

// A stand-in for the database that holds the recorded read: it answers any page of that one query by its limit and
// offset, as PostgREST does, later pages sooner than earlier ones; a request for another query fails the test. `fault`
// may answer a page otherwise (a failure, a cancelled statement). `log` keeps every request in the order it was sent.
function pagedDb({ rows = PAGED.rows, fault = () => null } = {}) {
  const log = [], tries = new Map();
  const fetch = async (url) => {
    const u = new URL(String(url));
    const q = Object.fromEntries(u.searchParams);
    const limit = Number(q.limit), offset = Number(q.offset);
    delete q.limit; delete q.offset;
    assert.equal(u.pathname, `/rest/v1/${PAGED.table}`);
    assert.deepEqual(q, PAGED.query, "a read that was not recorded");
    const page = offset / 1000;
    const n = (tries.get(offset) ?? 0) + 1;
    tries.set(offset, n);
    log.push({ offset, limit, at: Date.now() });
    await new Promise((r) => setTimeout(r, Math.max(1, 12 - 3 * page)));   // a later page answers sooner than an earlier one
    const f = fault(offset, n);
    if (f === "throw") throw new Error("socket hang up");
    if (f) return new Response(f.body, { status: f.status });
    return new Response(JSON.stringify(rows.slice(offset, offset + limit)), { status: 200, headers: { "content-type": "application/json" } });
  };
  return { fetch, log };
}
const withDb = async (db, f) => { globalThis.fetch = db.fetch; try { return await f(); } finally { globalThis.fetch = fixtureFetch; } };
const paged = (together, max = 50_000) => sb.restPaged(PAGED.table, PAGED.query, 3600, max, together);
const outcome = (p) => p.then((rows) => ({ rows }), (e) => ({ error: e.message, data: e instanceof sb.DataError }));

await test148("the pages of one large read asked for together are the rows the reader returned one page after another, in the same order", async () => {
  assert.equal(PAGED.rows.length, 2424);                               // three pages: 1,000, 1,000 and 424 rows, as recorded
  assert.deepEqual(Object.values(PAGED.pages).map((p) => p.rows), [1000, 1000, 424, 0, 0]);
  const serial = await withDb(pagedDb(), () => paged(1));
  assert.deepEqual(serial, PAGED.rows);
  for (const together of [2, 3, 4, 8]) {
    const db = pagedDb();
    const rows = await withDb(db, () => paged(together));
    assert.deepEqual(rows, serial, `together ${together}`);
    assert.equal(JSON.stringify(rows), JSON.stringify(serial));        // the same rows, the same order, the same fields in the same order
  }
  // every row keeps its place: the hours run in order with no hour twice
  assert.ok(serial.every((r, i) => i === 0 || r.t > serial[i - 1].t));
});

await test148("the first page is asked for alone by the request it always was, and a read of one page sends nothing more", async () => {
  const one = pagedDb(), four = pagedDb();
  await withDb(one, () => paged(1));
  await withDb(four, () => paged(4));
  assert.deepEqual(one.log.map((r) => r.offset), [0, 1000, 2000]);
  assert.deepEqual(four.log.map((r) => r.offset), [0, 1000, 2000, 3000, 4000]);
  assert.deepEqual(four.log[0], { ...one.log[0], at: four.log[0].at });
  assert.ok(four.log[1].at - four.log[0].at >= 5, "the second page was asked for before the first came back");
  assert.ok(four.log[4].at - four.log[1].at < 5, "the pages of one round were not asked for together");
  // fewer than 1,000 rows: one request either way, the same one
  const few = PAGED.rows.slice(0, 424);
  const a = pagedDb({ rows: few }), b = pagedDb({ rows: few });
  assert.deepEqual(await withDb(a, () => paged(1)), await withDb(b, () => paged(4)));
  assert.deepEqual([a.log.length, b.log.length], [1, 1]);
  assert.deepEqual(a.log.map((r) => [r.offset, r.limit]), b.log.map((r) => [r.offset, r.limit]));
  // exactly 1,000 and exactly 2,000 rows: the page after the last full one answers empty, and both readers stop there
  for (const n of [1000, 2000]) {
    const rows = PAGED.rows.slice(0, n);
    assert.deepEqual(await withDb(pagedDb({ rows }), () => paged(4)), await withDb(pagedDb({ rows }), () => paged(1)));
  }
});

await test148("the most rows a caller asks for is kept: the same pages, the same last page's limit", async () => {
  for (const max of [1, 999, 1000, 1001, 2000, 2400, 2424, 2500, 3000]) {
    const a = pagedDb(), b = pagedDb();
    const serial = await withDb(a, () => paged(1, max)), together = await withDb(b, () => paged(4, max));
    assert.deepEqual(together, serial, `max ${max}`);
    assert.equal(serial.length, Math.min(max, 2424));
    assert.ok(b.log.every((r) => r.offset < max && r.limit === Math.min(1000, max - r.offset)));
    assert.deepEqual(b.log.filter((r) => r.offset <= serial.length).map((r) => r.limit).slice(0, a.log.length), a.log.map((r) => r.limit));
  }
});

await test148("a failed page fails the read as it failed before: the same page, the same error, a DataError", async () => {
  const cases = {
    "the second page answers HTTP 500": (offset) => (offset === 1000 ? { status: 500, body: '{"message":"internal error"}' } : null),
    "the third page answers HTTP 503": (offset) => (offset === 2000 ? { status: 503, body: "upstream unavailable" } : null),
    "the first page answers HTTP 401": (offset) => (offset === 0 ? { status: 401, body: '{"message":"Invalid API key"}' } : null),
    "the request of the second page cannot be sent": (offset) => (offset === 1000 ? "throw" : null),
    "the second and the third page both fail: the second's error is the read's": (offset) => (offset === 1000 ? { status: 500, body: "second" } : offset === 2000 ? { status: 502, body: "third" } : null),
  };
  for (const [name, fault] of Object.entries(cases)) {
    const serial = await withDb(pagedDb({ fault }), () => outcome(paged(1)));
    const together = await withDb(pagedDb({ fault }), () => outcome(paged(4)));
    assert.ok(serial.error && serial.data, name);
    assert.deepEqual(together, serial, name);
  }
  // required and attempt keep their meaning over a read of many pages: one throws the failure, the other gives its reason
  const fault = (offset) => (offset === 2000 ? { status: 500, body: "the third page" } : null);
  const reason = "Supabase series: HTTP 500 the third page";
  assert.deepEqual(await withDb(pagedDb({ fault }), () => sb.attempt(() => paged(4))), { ok: false, reason });
  await assert.rejects(withDb(pagedDb({ fault }), () => sb.required(() => paged(4))), (e) => e instanceof sb.DataError && e.message === reason);
  assert.deepEqual(await withDb(pagedDb(), () => sb.required(() => paged(4))), { ok: true, data: PAGED.rows });
});

await test148("a page beyond the last is nobody's: its failure does not fail the read, and is not left unhandled", async () => {
  // the reader as it was never asked for the fourth and fifth page: whatever they answer, the rows are the same
  const fault = (offset) => (offset === 3000 ? { status: 500, body: "beyond the end" } : offset === 4000 ? "throw" : null);
  const serial = await withDb(pagedDb({ fault }), () => paged(1));
  const together = await withDb(pagedDb({ fault }), () => paged(4));
  assert.deepEqual(together, serial);
  assert.deepEqual(serial, PAGED.rows);
  await new Promise((r) => setTimeout(r, 40));
  assert.equal(unhandled.length, 0);
});

await test148("a statement cancelled for time is tried again on its own page, as before, and the rows are the same", async () => {
  // Postgres 57014 once on the second page: one wait of a second on that page, then the page; the same both ways
  const fault = (offset, n) => (offset === 1000 && n === 1 ? { status: 500, body: '{"code":"57014","message":"canceling statement due to statement timeout"}' } : null);
  const a = pagedDb({ fault }), b = pagedDb({ fault });
  const serial = await withDb(a, () => paged(1)), together = await withDb(b, () => paged(4));
  assert.deepEqual(together, serial);
  assert.deepEqual(serial, PAGED.rows);
  assert.equal(a.log.filter((r) => r.offset === 1000).length, 2);
  assert.equal(b.log.filter((r) => r.offset === 1000).length, 2);
});

await test148("while the site is built the reader is the one it was, and the server may ask for one page at a time", () => {
  assert.equal(sb.pagesTogether(undefined, false), 4);
  assert.equal(sb.pagesTogether("4", true), 1);                        // the build: one page after another, whatever is set
  assert.equal(sb.pagesTogether(undefined, true), 1);
  assert.equal(sb.pagesTogether("1"), 1);
  assert.equal(sb.pagesTogether("8"), 8);
  for (const v of ["0", "9", "2.5", "many", ""]) assert.equal(sb.pagesTogether(v), 4);
  const src = read("../lib/supabase.ts");
  assert.ok(src.includes("const PAGES_TOGETHER = pagesTogether(process.env.ERW_PAGES_TOGETHER, BUILDING);"));
  assert.ok(src.includes('const BUILDING = process.env.NEXT_PHASE === "phase-production-build";'));
  assert.ok(src.includes("const BUILD_READS = 2;"));                   // session 90's turns are as they were
  assert.ok(src.includes("[res, body] = await turn(async () => {"));   // and every page's request still takes its turn
  assert.ok(src.includes("return restPaged<T>(table, query, revalidate, max, PAGES_TOGETHER);"));
  assert.equal(src.split("await fetch(`${base}/rest/v1/${table}?${qs}`").length - 1, 1);   // one place sends a page's request
});

// ---- the reserve prices by day and by month
// A stand-in for the database: the catalogue and one table's real rows (ERCOT's ECRS by month, 2025), filtered as the
// query tool asks (the table, the variable, the dates), and the registry of sources, empty.
const rolledDb = (catalogue = ROLLED.catalogue) => {
  const log = [];
  const fetch = async (url) => {
    const u = new URL(String(url)), q = Object.fromEntries(u.searchParams);
    log.push(`${u.pathname.split("/").pop()} ${q.table_name ?? ""} ${q.variable ?? ""}`.trim());
    let body;
    if (u.pathname.endsWith("/catalogue")) body = catalogue;
    else if (u.pathname.endsWith("/sources") || u.pathname.endsWith("/headers")) body = [];
    else if (u.pathname.endsWith("/series")) {
      const table = q.table_name.replace(/^eq\./, ""), variable = (q.variable ?? "").replace(/^eq\./, "");
      const [, lo, hi] = /ts_utc\.gte\.([^,)]+),ts_utc\.lt\.([^,)]+)/.exec(q.and ?? "") ?? [];
      if (table !== "ercot_as_prices_monthly") throw new Error(`a read of ${table} that the fixture does not hold`);
      assert.ok(/entity\.eq\."ercot:ECRS"/.test(q.and ?? "") && q.or === undefined);          // session 156: the entity alone, a term of "and" (it was "entity or node")
      body = ROLLED.rows.filter((r) => r.table_name === table && (!variable || r.variable === variable) && (!lo || Date.parse(r.ts_utc) >= Date.parse(lo)) && (!hi || Date.parse(r.ts_utc) < Date.parse(hi)))
        .sort((x, y) => (x.ts_utc < y.ts_utc ? -1 : x.ts_utc > y.ts_utc ? 1 : 0)).map((r) => ({ t: r.ts_utc, v: r.value, entity: r.entity, variable: r.variable, unit: r.unit }));
    } else throw new Error(`a request the fixture does not hold: ${u.pathname}`);
    return new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } });
  };
  return { fetch, log };
};
// the catalogue is kept ten minutes by the tools: each case reads it in a fresh copy of the module
let copy = 0;
const freshTools = () => import(`../lib/chat/tools.ts?session148=${++copy}`);
const H12 = { table: "ercot_as_prices_monthly", aggregation: "mean", entity: "ercot:ECRS", variable: "mcpc_dam_mean", start: "2025-01-01", end: "2026-01-01", group_by: "month" };

await test148("the panel offers the two tables, tells the model when to read them, and ASK_ROLLUP=off leaves it as it was", () => {
  assert.deepEqual(roll.ROLLUP_TABLES, ["ercot_as_prices_daily", "ercot_as_prices_monthly"]);
  assert.equal(roll.rollupOffered(undefined), true);
  assert.equal(roll.rollupOffered("off"), false);
  for (const t of roll.ROLLUP_TABLES) { assert.ok(profile.scope.tables.includes(t), t); assert.deepEqual(profile.scope.filters[t], {}); assert.ok(roll.ROLLUP_HOLDS[t]); }
  assert.deepEqual(profile.scope.rollup, { hourly: "ercot_as_prices", tables: roll.ROLLUP_TABLES });
  const guide = roll.rollupGuide();
  assert.ok(profile.system.includes(guide));
  for (const words of ["ercot_as_prices_daily", "ercot_as_prices_monthly", "mcpc_dam_mean", "mcpc_dam_min", "mcpc_dam_max", "mcpc_dam_hours_in_day", "mcpc_dam_hours_in_month", "is not whole", "nothing is filled",
    "Never scale a short period", `may span at most ${roll.MAX_HOURLY_DAYS} days`, "one hour, the hours of a day or of a few weeks", "plain dates and no tz", "not loaded yet"]) assert.ok(guide.includes(words), words);
  // switched off: the prompt and the scope are session 143's, to the letter
  const before = process.env.ASK_ROLLUP;
  process.env.ASK_ROLLUP = "off";
  try {
    const off = ercotProfile();
    assert.equal(off.system, profile.system.replace(guide, ""));
    assert.ok(!off.system.includes("ercot_as_prices_daily"));
    assert.ok(roll.ROLLUP_TABLES.every((t) => !off.scope.tables.includes(t)));
    assert.equal(off.scope.rollup, undefined);
    assert.equal(off.scope.tables.length, profile.scope.tables.length - 2);
  } finally { if (before === undefined) delete process.env.ASK_ROLLUP; else process.env.ASK_ROLLUP = before; }
});

await test148("a read of hourly reserve prices needs a start and spans at most 35 days; a day or a week of hours is still read", () => {
  const now = Date.parse("2026-10-08T12:00:00Z");
  assert.equal(roll.MAX_HOURLY_DAYS, 35);
  assert.equal(roll.hourlyRefusal("2026-10-01T05:00:00.000Z", "2026-10-02T05:00:00.000Z", now), null);     // a day
  assert.equal(roll.hourlyRefusal("2026-10-01T05:00:00.000Z", "2026-10-08T05:00:00.000Z", now), null);     // a week
  assert.equal(roll.hourlyRefusal("2026-09-03T12:00:00.000Z", null, now), null);                           // 35 days to now
  assert.equal(roll.hourlyRefusal("2025-06-01T05:00:00.000Z", "2025-07-06T05:00:00.000Z", now), null);     // 35 days, long ago
  for (const [start, end] of [["2025-01-01T06:00:00.000Z", "2026-01-01T06:00:00.000Z"], ["2026-09-01T05:00:00.000Z", null], ["2025-06-01T05:00:00.000Z", "2025-07-07T05:00:00.000Z"], [null, null], [null, "2026-01-01T06:00:00.000Z"]]) {
    const why = roll.hourlyRefusal(start, end, now);
    assert.ok(why && why.includes("ercot_as_prices_monthly") && why.includes("ercot_as_prices_daily") && why.includes("mcpc_dam_mean"), `${start} ${end}`);
  }
  assert.equal(roll.spanDays("2025-01-01T06:00:00.000Z", "2026-01-01T06:00:00.000Z", now), 365);
  assert.equal(roll.spanDays(null, null, now), null);
});

await test148("the query tool refuses a year of hourly reserve prices before any row is read, and only once the site holds the two tables", async () => {
  const year = { table: "ercot_as_prices", aggregation: "mean", entity: "ercot:ECRS", variable: "mcpc_dam", start: "2025-01-01", end: "2026-01-01", group_by: "month", tz: "America/Chicago" };   // session 143's slow read
  const held = rolledDb();
  const t1 = await freshTools();
  const refused = await withDb(held, () => t1.runTool("query", year, profile.scope));
  assert.equal(refused.isError, true);
  assert.ok(refused.out.error.includes("spans 365 days") && refused.out.error.includes("ercot_as_prices_monthly"));
  assert.ok(held.log.every((l) => !l.startsWith("series")), "rows were read");
  const noStart = await withDb(rolledDb(), () => t1.runTool("query", { table: "ercot_as_prices", aggregation: "latest", entity: "ercot:ECRS", variable: "mcpc_dam" }, profile.scope));
  assert.ok(noStart.isError && noStart.out.error.includes("gives no start"));
  // not loaded yet (the catalogue holds the hourly table only): the hourly table is read as before
  const t2 = await freshTools();
  const early = rolledDb(ROLLED.catalogue.filter((r) => r.table_name === "ercot_as_prices"));
  // (the stand-in holds no hourly row: a read that reaches it comes back as the failure of that request, which is the proof the read was sent)
  const wentToHours = (r) => r.isError && r.out.error.includes("a read of ercot_as_prices that the fixture does not hold");
  assert.ok(wentToHours(await withDb(early, () => t2.runTool("query", year, profile.scope))));
  assert.ok(early.log.some((l) => l.startsWith("series eq.ercot_as_prices ")));
  // loaded but only one of the two: the same
  const t3 = await freshTools();
  assert.ok(wentToHours(await withDb(rolledDb(ROLLED.catalogue.filter((r) => r.table_name !== "ercot_as_prices_daily")), () => t3.runTool("query", year, profile.scope))));
  // a week of hours is read from the hourly table even when the two tables are held, and so is every chat without the profile
  const t4 = await freshTools();
  assert.ok(wentToHours(await withDb(rolledDb(), () => t4.runTool("query", { ...year, start: "2025-06-01", end: "2025-06-08" }, profile.scope))));
  assert.ok(wentToHours(await withDb(rolledDb(), () => t4.runTool("query", year, null))));
});

await test148("a year of reserve prices by month is twelve rows of the monthly table, and a number shown must equal a row fetched", async () => {
  const t = await freshTools();
  const db = rolledDb();
  const r = await withDb(db, () => t.runTool("query", H12, profile.scope));
  assert.equal(r.isError, false);
  assert.equal(db.log.filter((l) => l.startsWith("series")).length, 1);                // one page, one request
  assert.equal(r.out.rows_matched, 12);
  const want = ROLLED.rows.filter((x) => x.variable === "mcpc_dam_mean");
  assert.deepEqual(r.out.result.map((x) => [x.month, x.value]), want.map((x) => [x.ts_utc.slice(0, 7), x.value]));   // each month by its own label, each value the table's row
  assert.deepEqual(r.out.units, ["USD/MW-hour"]);
  assert.equal(r.out.tier, "derived");
  assert.equal(r.out.summary.rows, 12);
  // the number check, as it always was: a figure of the result passes, another does not
  const src = [JSON.stringify(r.out)];
  const jan = want[0].value, top = r.out.summary.highest.value;
  assert.deepEqual(ask.unverified(`ECRS averaged ${jan} USD per MW per hour in January and peaked at ${top} (ercot_as_prices_monthly).`, src), []);
  assert.deepEqual(ask.unverified(`ECRS averaged ${(jan + 0.5).toFixed(4)} USD per MW per hour in January.`, src), [(jan + 0.5).toFixed(4)]);
  // and the series the page would draw is the rows fetched: the profile's own check
  const records = [{ tool: "query", input: H12, out: { result_id: "r1", ...r.out }, isError: false }];
  const done = profile.finish("answered", { answer: "x", citations: [{ table: "ercot_as_prices_monthly", source_report: "", data_version: "", tier: "derived" }], not_in_warehouse: false, form: "chart", series: ["r1"], followups: [], premise: "" }, records);
  assert.equal(done.series.length, 1);
  assert.deepEqual(done.series[0].check, { rows_fetched: 12, rows: 12, same: true, points: 12, not_drawn: 0 });
  // the hours a month rests on come the same way: 2025 has one month an hour short of its calendar (the clocks) and none short of its own hours
  const hours = await withDb(rolledDb(), () => t.runTool("query", { ...H12, variable: "mcpc_dam_hours", aggregation: "sum" }, profile.scope));
  const inMonth = await withDb(rolledDb(), () => t.runTool("query", { ...H12, variable: "mcpc_dam_hours_in_month", aggregation: "sum" }, profile.scope));
  assert.deepEqual(hours.out.result, inMonth.out.result);
  assert.equal(hours.out.summary.sum_of_rows, 8760);
});

// ---- the plan made by rule
const TODAY = "2026-10-07";
const planOf = (q, rollup = true) => rulePlan(q, TODAY, { rollup });
const byId = Object.fromEntries(SET.map((q) => [q.id, q.q]));

await test148("the rule plans sixteen of the 100 questions, in three shapes, and no question about an idea or one to refuse", () => {
  const got = {};
  for (const q of SET) { const p = planOf(q.q); if (p) got[q.id] = p.shape; }
  assert.deepEqual(got, {
    h01: "hub price", h02: "hub price", h15: "hub price", h16: "hub price", s01: "hub price", s03: "hub price", s11: "hub price", s13: "hub price",
    h06: "generation", h07: "generation", h18: "generation", h20: "generation", s05: "generation", s08: "generation", s14: "generation",
    h12: "reserve",
    h05: "generation by fuel",   // session 161: every fuel over a stretch of days, one read grouped by fuel and one rolled up by day
  });
  assert.ok(SET.filter((q) => q.kind === "conceptual" || q.kind === "refuse").every((q) => planOf(q.q) === null));
  // without the two tables in the live set the reserve question is the model's: sixteen (fifteen until session 161 planned h05)
  assert.equal(SET.filter((q) => planOf(q.q, false)).length, 16);
  assert.equal(planOf(byId.h12, false), null);
});

await test148("the read the rule writes is the read the model made for the same question in session 143's record", () => {
  const one = (id) => planOf(byId[id]).calls.map((c) => c.input);
  assert.deepEqual(one("h01"), [{ table: "ercot_hub_prices_daily", aggregation: "mean", entity: "ercot:HB_HUBAVG", variable: "da_mean", start: "2026-09-07", end: "2026-10-07", group_by: "day" }]);
  assert.deepEqual(one("h02"), [{ table: "ercot_hub_prices_daily", aggregation: "mean", entity: "ercot:HB_HUBAVG", variable: "rt_mean", start: "2026-01-01", end: "2026-10-07", group_by: "month" }]);
  assert.deepEqual(one("h15"), [{ table: "ercot_hub_prices_daily", aggregation: "mean", entity: "ercot:HB_HUBAVG", variable: "da_mean", start: "2026-01-01", end: "2026-10-07", group_by: "month" },
    { table: "ercot_hub_prices_daily", aggregation: "mean", entity: "ercot:HB_HUBAVG", variable: "rt_mean", start: "2026-01-01", end: "2026-10-07", group_by: "month" }]);
  assert.deepEqual(one("h16"), [{ table: "ercot_hub_prices_daily", aggregation: "mean", entity: "ercot:HB_WEST", variable: "da_mean", start: "2026-09-01", end: "2026-10-01", group_by: "day" }]);
  assert.deepEqual(one("s03"), [{ table: "ercot_hub_prices_daily", aggregation: "max", entity: "ercot:HB_HUBAVG", variable: "rt_max", start: "2026-09-07", end: "2026-10-07" }]);
  assert.deepEqual(one("s11"), [{ table: "ercot_hub_prices_daily", aggregation: "mean", entity: "ercot:HB_NORTH", variable: "da_mean", start: "2026-10-01", end: "2026-10-02" }]);
  assert.deepEqual(one("s13"), [{ table: "ercot_hub_prices_daily", aggregation: "mean", entity: "ercot:HB_HUBAVG", variable: "da_mean", start: "2026-09-01", end: "2026-10-01" }]);
  assert.deepEqual(one("s01"), [{ table: "ercot_hub_prices_daily", aggregation: "mean", entity: "ercot:HB_HUBAVG", variable: "da_mean", start: "2026-10-06", end: "2026-10-07" }]);   // the model asked "latest" of the same day
  assert.deepEqual(one("h06"), [{ table: "generation_mix_hourly_profile", aggregation: "sum", entity: "iso:ercot", variable: "solar_mwh", group_by: "year" }]);
  assert.deepEqual(one("h18"), [{ table: "generation_mix_hourly_profile", aggregation: "sum", entity: "iso:ercot", variable: "coal_mwh", start: "2019-01-01", group_by: "year" }]);
  assert.deepEqual(one("h07"), [{ table: "generation_mix_hourly_profile", aggregation: "sum", entity: "iso:ercot", variable: "wind_mwh", end: "2026-01-01", group_by: "month" }]);
  assert.deepEqual(one("h20"), [{ table: "generation_mix_hourly_profile", aggregation: "sum", entity: "iso:ercot", variable: "natural_gas_mwh", start: "2026-01-01", end: "2027-01-01", group_by: "month" }]);
  assert.deepEqual(one("s08").slice(0, 2), [{ table: "generation_mix_hourly_profile", aggregation: "sum", entity: "iso:ercot", variable: "solar_mwh", start: "2026-07-01", end: "2026-08-01" },
    { table: "generation_mix_hourly_profile", aggregation: "sum", entity: "iso:ercot", variable: "days_held", start: "2026-07-01", end: "2026-08-01" }]);
  assert.deepEqual(one("s14").map((c) => c.variable), ["natural_gas_mwh", "days_held", "days_in_month"]);
  assert.deepEqual(one("s05").map((c) => [c.variable, c.start, c.end]), [["wind_share_pct", "2026-09-01", "2026-10-01"], ["days_held", "2026-09-01", "2026-10-01"], ["days_in_month", "2026-09-01", "2026-10-01"]]);
  assert.deepEqual(one("h12"), [H12]);                                                    // the monthly table, where session 143 read a year of hours
  // set against the record itself where this copy holds it (runs/session143 is not in git)
  const rec = new URL("../../runs/session143/after_rest.jsonl", import.meta.url), rec2 = new URL("../../runs/session143/after_sample.jsonl", import.meta.url);
  if (fs.existsSync(rec) && fs.existsSync(rec2)) {
    const lines = [rec, rec2].flatMap((f) => fs.readFileSync(f, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)));
    const firstRead = (id) => lines.find((l) => l.id === id).steps.find((s) => s.what === "tools").calls.map((c) => c.args);
    const sortKeys = (o) => Object.fromEntries(Object.keys(o).sort().map((k) => [k, o[k]]));
    for (const id of ["h01", "h02", "h16", "s03", "s11", "s13", "h06"]) assert.deepEqual(one(id).map(sortKeys), firstRead(id).map(sortKeys), id);
    assert.deepEqual(one("h15").map(sortKeys).map((c) => JSON.stringify(c)).sort(), firstRead("h15").map(sortKeys).map((c) => JSON.stringify(c)).sort());
  }
});

await test148("a near-miss is not planned: one word the rule cannot account for, and the question is the model's", () => {
  const no = [
    "What was the ERCOT Hub Average day-ahead price yesterday at noon?",          // an hour of the day
    "What was the ERCOT Hub Average price yesterday?",                             // no market named
    "What was the day-ahead price yesterday?",                                     // no hub named
    "What was the average day-ahead Hub Average price in September?",              // a month with no year
    "What was the average real-time Hub Average price last week?",                 // which week is the model's to say (s20)
    "What is the ERCOT Hub Average day-ahead price now?",
    "What will the ERCOT Hub Average day-ahead price be in 2027?",                 // a forecast
    "What was the ERCOT Hub Average day-ahead price in 2027?",
    "What was the ERCOT Hub Average day-ahead price on 31 June 2026?",             // not a date
    "What was the day-ahead price at ERCOT's North hub and West hub on 1 October 2026?",   // two hubs
    "What was the ERCOT Hub Average day-ahead price in 2024 and in 2025?",         // two periods
    "What was SPP's South Hub price yesterday?", "What was the PJM Western Hub price yesterday?", "What was the day-ahead price at the CAISO South hub yesterday?",
    "What was the ICE ERCOT North hub day-ahead futures price in 2025?",
    "How many hours was the ERCOT Hub Average real-time price above 200 in 2025?",
    "What was the median day-ahead Hub Average price in September 2026?",
    "Show the day-ahead Hub Average price hour by hour yesterday.",
    "Show the day-ahead Hub Average price day by day in 2025.",                    // more rows than a result shows
    "Show the day-ahead Hub Average price by month in September 2026.",            // one row is no series
    "How has solar capacity in ERCOT grown year by year?", "How has solar generation in CAISO grown year by year?", "How much solar electricity did ERCOT generate yesterday?",
    "How much electricity did ERCOT generate from gas last month?", "What share of ERCOT's generation came from wind in 2025?", "How has wind and solar generation in ERCOT grown year by year?",
    "Show ERCOT's wind output across the hours of an average day.", "What is the Henry Hub natural gas spot price now?", "How has the natural gas burned for power in ERCOT changed week by week this year?",
    "How has the real-time price of ECRS moved month by month in 2025?", "How many hours was the ECRS price above 100 in 2025?", "What was the price of ECRS and RRS reserves in 2025?",
    "What did a battery earn from ECRS in 2025?", "What is a hub?", "What do peak and off-peak mean?", "",
  ];
  for (const q of no) assert.equal(planOf(q), null, q);
  assert.equal(rulePlan(byId.s01, "7 October 2026", { rollup: true }), null);     // a date the rule cannot read
  assert.equal(rulePlan("x".repeat(201), TODAY), null);
  // what it does plan beyond the 100, so the shapes are shapes and not sixteen strings
  assert.deepEqual(planOf("What was the lowest day-ahead price at ERCOT's Houston hub in August 2026?").calls[0].input, { table: "ercot_hub_prices_daily", aggregation: "min", entity: "ercot:HB_HOUSTON", variable: "da_min", start: "2026-08-01", end: "2026-09-01" });
  assert.deepEqual(planOf("What was the highest ECRS price in 2025?").calls[0].input, { table: "ercot_as_prices_daily", aggregation: "max", entity: "ercot:ECRS", variable: "mcpc_dam_max", start: "2025-01-01", end: "2026-01-01" });
  assert.deepEqual(planOf("What was the average price of regulation up in June 2025?").calls.map((c) => [c.input.table, c.input.variable]),
    [["ercot_as_prices_monthly", "mcpc_dam_mean"], ["ercot_as_prices_monthly", "mcpc_dam_hours"], ["ercot_as_prices_monthly", "mcpc_dam_hours_in_month"]]);
  assert.equal(planOf("How has the price of non-spin reserves changed year by year?").calls[0].input.table, "ercot_as_prices_daily");
  // no plan reads the hourly table, and none asks for more groups than a result shows
  for (const q of SET) for (const c of planOf(q.q)?.calls ?? []) assert.notEqual(c.input.table, "ercot_as_prices");
  assert.equal(MAX_PLAN_GROUPS, JSON.parse(read("../lib/chat/spec_ercot.json")).max_groups);
});

await test148("a question that continues a conversation is never planned by rule, and a reserve question only once the summaries say the tables are held", () => {
  const p = ercotProfile();
  assert.equal(p.plan(byId.s01, TODAY, null, []).shape, "hub price");
  assert.equal(p.plan(byId.s01, TODAY, null, [{ question: "What was the price in 2023?", answer: "48.36 USD/MWh (ercot_hub_prices_daily).", calls: [], citations: [] }]), null);
  assert.equal(p.plan(byId.h12, TODAY, null, []), null);                          // no summary has said the two tables are held
  const resume = p.resume("Today is 2026-10-07 (UTC).\n\nQuestion: q", [{ tool: "query", input: H12, out: { result_id: "r1", result: [{ month: "2025-01", value: 1.3737 }] }, isError: false }]);
  assert.ok(resume.startsWith("Today is 2026-10-07 (UTC).\n\nQuestion: q\n\nALREADY READ FOR THIS QUESTION"));
  assert.ok(resume.includes('CALL 1: query {"table":"ercot_as_prices_monthly"') && resume.includes('"value":1.3737') && resume.includes("Do not repeat them"));
});

await test148("the two switches are on unless the server turns them off (session 156, the owner's ruling), and the writing turn's effort is as it was", () => {
  // Session 148 left both off, and this test held that. The owner ruled on 8 October 2026 that both are set: the default
  // is lib/chat/switches.ts's, the server variable still turns each off, and the loop holds no default of its own.
  const loop = read("../lib/chat/ask.ts");
  assert.ok(loop.includes("if (profile?.plan && profile.writing && profile.resume && rulePlanOn()) {"));
  assert.equal(loop.split("rulePlanOn()").length - 1, 1);
  assert.ok(!loop.includes("process.env.ASK_RULE_PLAN") && !loop.includes("env.ASK_READER_EFFORT"));      // the loop reads neither variable itself
  // the rule's read is made before any model call, is written from under the same checks, and falls back to the loop
  assert.ok(loop.indexOf("rulePlanOn()) {") < loop.indexOf("for (;;) {"));
  assert.ok(loop.includes('const ruled = await fastWrite("rule");') && loop.includes('const fast = await fastWrite("fast");'));
  assert.ok(loop.includes("messages[0] = { role: \"user\", content: profile.resume(opening, records) };"));
  assert.ok(loop.includes("if (outs.every((o) => !o.isError)) {"));
  assert.equal(loop.split("const s = settle(draft,").length - 1, 1);              // one writing turn, one check, for both paths
  assert.deepEqual(ask.READER_EFFORTS, ["low", "medium", "high"]);
  assert.equal(ask.effortOf("planner", "medium", {}), "low");                      // nothing set: the reading turn is lower (it was "medium" until session 156)
  assert.equal(ask.effortOf("writer", "medium", {}), "medium");                    // the writing turn as it was
  assert.equal(ask.effortOf("planner", "medium", { ASK_READER_EFFORT: "off" }), "medium");           // the server turns it off
  assert.equal(ask.effortOf("planner", "medium", { ASK_READER_EFFORT: "low" }), "low");
  assert.equal(ask.effortOf("writer", "medium", { ASK_READER_EFFORT: "low" }), "medium");            // the writing turn as it is
  assert.equal(ask.effortOf("planner", "medium", { ASK_READER_EFFORT: "none" }), "medium");          // a value the API does not take is ignored
  assert.equal(ask.effortOf("planner", "medium", { ASK_READER_EFFORT: "low", ASK_WRITER_EFFORT: "high" }), "low");
  assert.equal(ask.effortOf("writer", "medium", { ASK_WRITER_EFFORT: "high" }), "high");             // session 143's switch, as it was
  assert.equal(ask.effortOf("planner", "medium", { ASK_WRITER_EFFORT: "high", ASK_READER_EFFORT: "off" }), "high");
  assert.ok(loop.includes('effort: effortOf(role, profile ? profile.effort : spec.effort)'));
  assert.equal(JSON.parse(read("../lib/chat/spec_ercot.json")).effort, "medium");
  for (const k of ["ASK_RULE_PLAN", "ASK_READER_EFFORT", "ASK_ROLLUP", "ERW_PAGES_TOGETHER"]) assert.equal(process.env[k], undefined, `${k} is set where the tests run`);
  // no switch touches a ceiling, and the ceilings are as they were
  assert.deepEqual(JSON.parse(read("../lib/chat/limits.json")), { ...JSON.parse(read("../lib/chat/limits.json")), daily_usd: 3, monthly_usd: 30, per_visitor_per_day: 15 });
});

// ---- the loop itself, with a stand-in for the model
// No model is called: every request the loop would send to the model's API is answered here, by a script, in the API's
// own streamed form, and the request's body is kept so that what the loop sent can be read. The reads are session 143's
// recorded reads (the West hub's day-ahead price by day, September 2026: real rows), and the cost ledger's row goes
// nowhere. The key is not a key: were the stand-in missed, the API would refuse the request and nothing would be spent.
const sse = (reply) => {
  const ev = (type, data) => `event: ${type}\ndata: ${JSON.stringify({ type, ...data })}\n\n`;
  const blocks = reply.tools ? reply.tools.map((t, i) => [{ type: "tool_use", id: `toolu_fixture_${i + 1}`, name: t.name, input: {} }, { type: "input_json_delta", partial_json: JSON.stringify(t.input) }])
    : [[{ type: "text", text: "" }, { type: "text_delta", text: reply.text }]];
  return ev("message_start", { message: { id: "msg_fixture", type: "message", role: "assistant", model: "claude-sonnet-5-5", content: [], stop_reason: null, stop_sequence: null,
    usage: { input_tokens: 100, output_tokens: 1, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 } } }) +
    blocks.map(([start, delta], index) => ev("content_block_start", { index, content_block: start }) + ev("content_block_delta", { index, delta }) + ev("content_block_stop", { index })).join("") +
    ev("message_delta", { delta: { stop_reason: reply.tools ? "tool_use" : "end_turn", stop_sequence: null }, usage: { output_tokens: 50 } }) + ev("message_stop", {});
};
function standIn(script) {
  const sent = [];
  const fetch = async (url, init) => {
    const u = new URL(typeof url === "string" ? url : url.url ?? String(url));
    if (u.hostname === "api.anthropic.com") {
      if (u.pathname === "/v1/models") return new Response(JSON.stringify({ data: [{ type: "model", id: "claude-sonnet-5-5", display_name: "a stand-in", created_at: "2026-01-01T00:00:00Z" }], has_more: false, first_id: "claude-sonnet-5-5", last_id: "claude-sonnet-5-5" }), { status: 200, headers: { "content-type": "application/json" } });
      assert.equal(u.pathname, "/v1/messages");
      const body = JSON.parse(String(init.body));
      sent.push(body);
      return new Response(sse(script(body, sent.length)), { status: 200, headers: { "content-type": "text/event-stream", "request-id": `req_fixture_${sent.length}` } });
    }
    if ((init?.method ?? "GET") === "POST") return new Response("", { status: 201 });      // the cost ledger's row
    return fixtureFetch(url);
  };
  return { fetch, sent };
}
const WEST = FIX.results[0].out;                                                       // what the recorded read returns
const WEST_CALL = FIX.calls[0].input;
const draft = (over = {}) => JSON.stringify({ form: "chart", not_in_warehouse: false, series: ["r1"], premise: "",
  answer: `The West hub's day-ahead price ranged from ${WEST.summary.lowest.value} to ${WEST.summary.highest.value} USD/MWh over the month (ercot_hub_prices_daily).`,
  citations: [{ table: "ercot_hub_prices_daily", source_report: WEST.source_report, data_version: WEST.data_version, tier: "derived" }], nearest: [],
  followups: ["How did the North hub compare over the same month?", "Which day of the month was the dearest?"], ...over });
const SWITCHES = ["ASK_RULE_PLAN", "ASK_READER_EFFORT", "ANTHROPIC_API_KEY"];
// one question through the loop, with the switches given for its length only
const through = async (question, switches, script, mk = ercotProfile) => {
  const kept = Object.fromEntries(SWITCHES.map((k) => [k, process.env[k]]));
  Object.assign(process.env, { ANTHROPIC_API_KEY: "a-stand-in-not-a-key", ...switches });
  const w = standIn(script), events = [];
  try {
    const r = await withDb(w, () => ask.ask(question, TODAY, null, mk(), null, { onEvent: (e) => events.push(e.type) }));
    return { r, sent: w.sent, events };
  } finally { for (const k of SWITCHES) { if (kept[k] === undefined) delete process.env[k]; else process.env[k] = kept[k]; } }
};
const said = (body) => body.messages.map((x) => (typeof x.content === "string" ? x.content : JSON.stringify(x.content))).join("\n");

await test148("with the rule on, a planned question is one model call: the read is made by code and the writer writes from it under every check", async () => {
  assert.deepEqual(planOf(byId.h16).calls[0].input, WEST_CALL);
  const { r, sent, events } = await through(byId.h16, { ASK_RULE_PLAN: "on" }, () => ({ text: draft() }));
  assert.equal(sent.length, 1);                                                        // no reading turn by the model
  assert.equal(sent[0].tools, undefined);                                              // the writing turn can call no tool
  assert.equal(sent[0].tool_choice, undefined);
  assert.equal(sent[0].output_config.effort, "medium");                                // and is written at the effort it always was
  assert.ok(said(sent[0]).includes(`Question: ${byId.h16}`) && said(sent[0]).includes("THE READING IS DONE") && said(sent[0]).includes(`CALL 1: query ${JSON.stringify(WEST_CALL)}`));
  assert.equal(r.status, "answered");
  assert.deepEqual([r.planned_by, r.plan_shape, r.tool_calls, r.usage.requests, r.retried], ["rule", "hub price", 1, 1, false]);
  assert.deepEqual(events, ["reading", "words"]);
  // the series the page draws is the rows the rule's read fetched, row for row
  assert.equal(r.series.length, 1);
  assert.deepEqual(r.series[0].check, { rows_fetched: 30, rows: 30, same: true, points: 30, not_drawn: 0 });
  assert.deepEqual(r.series[0].rows.map((x) => [x.key, x.value]), WEST.result.map((x) => [x.day, x.value]));
  assert.deepEqual(r.calls, [{ tool: "query", input: WEST_CALL }]);
  // the stages are the same five and sum to the whole; the rule's step is a planning step of no model
  const st = r.stages_ms;
  assert.equal(st.planning + st.fetching + st.drawing + st.writing + st.other, st.total);
  assert.deepEqual(r.steps.filter((s) => s.stage !== "other").map((s) => `${s.stage} ${s.what}${s.path ? ` ${s.path}` : ""}`), ["planning rule", "fetching tools", "writing model rule", "writing check", "drawing series"]);
  assert.equal(r.steps.filter((s) => s.what === "model").length, 1);
});

await test148("with the rule off, the same question is the model's as before: a reading turn with the tools, then the writing turn", async () => {
  const script = (body, n) => (n === 1 ? { tools: [{ name: "query", input: WEST_CALL }] } : { text: draft() });
  const { r, sent, events } = await through(byId.h16, { ASK_RULE_PLAN: "off", ASK_READER_EFFORT: "off" }, script);      // session 156: off is now said, not left unset
  assert.equal(sent.length, 2);
  assert.ok(sent[0].tools.some((t) => t.name === "query") && sent[0].tool_choice.type === "auto");
  assert.equal(sent[1].tools, undefined);
  assert.deepEqual(sent.map((b) => b.output_config.effort), ["medium", "medium"]);     // nothing set: both turns as they were
  assert.equal(r.status, "answered");
  assert.deepEqual([r.planned_by, r.tool_calls, r.usage.requests], [undefined, 1, 2]);
  assert.deepEqual(events, ["reading", "words"]);
  assert.deepEqual(r.steps.filter((s) => s.stage !== "other").map((s) => `${s.stage} ${s.what}${s.path ? ` ${s.path}` : ""}`), ["planning model", "fetching tools", "writing model fast", "writing check", "drawing series"]);
  // the rule's answer and the model's rest on the same rows
  const ruled = await through(byId.h16, { ASK_RULE_PLAN: "on" }, () => ({ text: draft() }));
  assert.deepEqual(ruled.r.series[0].rows, r.series[0].rows);
  assert.equal(ruled.r.answer, r.answer);
});

await test148("lower effort goes to the reading turn only; a question answered without reading has that one turn", async () => {
  const script = (body, n) => (n === 1 ? { tools: [{ name: "query", input: WEST_CALL }] } : { text: draft() });
  const low = await through(byId.h16, { ASK_RULE_PLAN: "off", ASK_READER_EFFORT: "low" }, script);   // session 156: the rule is on unless turned off, and this test is of the model's own reading turn
  assert.deepEqual(low.sent.map((b) => b.output_config.effort), ["low", "medium"]);    // the reading turn lower, the writing turn as it is
  assert.equal(low.r.status, "answered");
  assert.deepEqual(low.r.steps.filter((s) => s.what === "model").map((s) => `${s.role}:${s.effort}`), ["planner:low", "writer:medium"]);
  const odd = await through(byId.h16, { ASK_RULE_PLAN: "off", ASK_READER_EFFORT: "lowest" }, script);        // not a setting the API takes: ignored
  assert.deepEqual(odd.sent.map((b) => b.output_config.effort), ["medium", "medium"]);
  // with the rule on there is no reading turn to lower: the one call is the writer's
  const both = await through(byId.h16, { ASK_RULE_PLAN: "on", ASK_READER_EFFORT: "low" }, () => ({ text: draft() }));
  assert.deepEqual(both.sent.map((b) => b.output_config.effort), ["medium"]);
  // an idea is answered by the first turn alone, from the page's text: with the switch on, that turn's effort is the lower one
  const idea = JSON.stringify({ form: "words", not_in_warehouse: false, series: [], premise: "", answer: "A hub is a set of points on the grid whose prices are averaged into one price that traders use to buy and sell power.",
    citations: [{ table: "docs/grids/ercot.md", source_report: "docs/grids/ercot.md: text written for the ERW's ERCOT page; each section names its ISO and EIA sources", data_version: "the site's build", tier: "written" }], nearest: [],
    followups: ["How does ERCOT set prices?", "What is a load zone?"] });
  const c = await through(byId.c02, { ASK_READER_EFFORT: "low", ASK_RULE_PLAN: "on" }, () => ({ text: idea }));
  assert.deepEqual([c.r.status, c.r.form, c.r.tool_calls, c.r.planned_by, c.sent.length], ["answered", "words", 0, undefined, 1]);
  assert.equal(c.sent[0].output_config.effort, "low");
  assert.ok(c.sent[0].tools.length > 0);                                               // the rule did not plan it: the model had its tools, as before
});

await test148("when the writer cannot answer from the rule's read, nothing is shown and the model takes the question, told what was read", async () => {
  const empty = JSON.stringify({ form: "words", not_in_warehouse: false, series: [], premise: "", answer: "", citations: [], nearest: [], followups: [] });
  const { r, sent, events } = await through(byId.h16, { ASK_RULE_PLAN: "on" }, (body, n) => (n === 1 ? { text: empty } : { text: draft() }));
  assert.equal(sent.length, 2);
  assert.equal(sent[0].tools, undefined);
  assert.ok(sent[1].tools.some((t) => t.name === "query") && sent[1].tool_choice.type === "auto");   // the model, with its tools, as before
  assert.equal(sent[1].messages.length, 1);
  assert.ok(said(sent[1]).includes("ALREADY READ FOR THIS QUESTION") && said(sent[1]).includes(`CALL 1: query ${JSON.stringify(WEST_CALL)}`) && said(sent[1]).includes(String(WEST.summary.highest.value)));
  assert.deepEqual([r.status, r.planned_by, r.tool_calls, r.usage.requests], ["answered", undefined, 1, 2]);
  assert.deepEqual(events, ["reading", "words"]);                                      // the empty draft showed nothing
  assert.equal(r.series[0].check.same, true);
  // an error from the rule's read is not written from at all: the first call is already the model's, with its tools
  const broken = () => { const p = ercotProfile(); return { ...p, plan: () => ({ shape: "hub price", calls: [{ name: "query", input: { ...WEST_CALL, table: "no_such_table" } }] }) }; };
  const e = await through(byId.h16, { ASK_RULE_PLAN: "on" }, (body, n) => (n === 1 ? { tools: [{ name: "query", input: WEST_CALL }] } : { text: draft({ series: ["r2"] }) }), broken);
  assert.ok(e.sent[0].tools.length > 0 && said(e.sent[0]).includes("RESULT (an error)"));
  assert.deepEqual([e.r.status, e.r.planned_by, e.r.tool_calls, e.r.usage.requests], ["answered", undefined, 2, 2]);
});

await test148("on the rule's path a number that is in no row fetched is not shown: the draft is written again without it", async () => {
  const wrong = draft({ answer: `The West hub's day-ahead price ranged from ${WEST.summary.lowest.value} to 99.99 USD/MWh over the month (ercot_hub_prices_daily).` });
  const { r, sent, events } = await through(byId.h16, { ASK_RULE_PLAN: "on" }, (body, n) => (n === 1 ? { text: wrong } : { text: draft() }));
  assert.equal(sent.length, 2);
  assert.ok(sent.every((b) => b.tools === undefined));                                 // both are writing turns: no tool, no reading by the model
  assert.ok(said(sent[1]).includes("numbers in no tool result: 99.99"));
  assert.deepEqual([r.status, r.planned_by, r.retried, r.usage.requests], ["answered", "rule", true, 2]);
  assert.ok(!JSON.stringify(r.answer).includes("99.99"));
  assert.deepEqual(events, ["reading", "words"]);                                      // the first draft's words were never sent
  // and when the second draft fails too, the model takes the question: no unverified number is ever the answer
  const twice = await through(byId.h16, { ASK_RULE_PLAN: "on" }, (body, n) => (n <= 2 ? { text: wrong } : { text: draft() }));
  assert.equal(twice.sent.length, 3);
  assert.ok(twice.sent[2].tools.length > 0 && said(twice.sent[2]).includes("ALREADY READ FOR THIS QUESTION"));
  assert.deepEqual([twice.r.status, twice.r.planned_by], ["answered", undefined]);
  assert.ok(!JSON.stringify(twice.r.answer).includes("99.99"));
});

// session 168: a UTC stamp the model copies from a tool result passes the number check as written and reaches the
// reader in plain local words (lib/chat/plaintime.ts); the tool result carries the same words beside the stamp
// (its own count, so that the counts of sessions 143 and 148 that other tests read stay as they were)
const test168 = async (name, fn) => { await fn(); console.log(`ok   168: ${name}`); };
await test168("an answer that copies a stamp is answered, and the reader sees the date in words, never the stamp", async () => {
  const stamp = WEST.time_span.first;                                                   // 2026-09-01T00:00:00Z: a table of days labels its day so
  const answer = `The West hub's day-ahead price ranged from ${WEST.summary.lowest.value} to ${WEST.summary.highest.value} USD/MWh from ${stamp} (ercot_hub_prices_daily).`;
  const { r, sent } = await through(byId.h16, { ASK_RULE_PLAN: "on" }, () => ({ text: draft({ answer }) }));
  assert.equal(r.status, "answered");                                                  // the number check passed on the text as written
  assert.ok(!/\d{4}-\d{2}-\d{2}T/.test(r.answer) && r.answer.includes("from 1 September 2026 (ercot_hub_prices_daily)"), r.answer);
  assert.ok(said(sent[0]).includes('"first_local":"1 September 2026"'));               // what the writer read: the words beside the stamp
});

console.log(`${m} tests of session 148 pass`);
