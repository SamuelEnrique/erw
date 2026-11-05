// Energy Research Warehouse (ERW) site, session 1109: the query tool on session 320's eight per-kW questions, replayed
// on the saved rows of battery_stack_monthly (tests/fixtures/session1109/battery_reads.json, written by
// warehouse/chat/eval/fixture_s1109.py). No model and no request.
//
//   node --import ./scripts/alias-register.mjs scripts/test-ask-1109.mjs
//
// What is held here: each question is one query call (a sum over the months it names) that returns the table's figure
// in USD per MW; with ASK_PER_KW off, the default, the result carries no per-kW key, so the tool is what it was; with
// ASK_PER_KW=on, it carries value_usd_per_kw, the figure divided by 1,000, which is the question's key within its
// tolerance, and the number check (unverified) then traces the per-kW figure an answer would state.
import assert from "node:assert/strict";
import fs from "node:fs";

const read = (p) => fs.readFileSync(new URL(p, import.meta.url), "utf8");
const FIX = JSON.parse(read("../../tests/fixtures/session1109/battery_reads.json"));

process.env.SUPABASE_URL = "https://fixture.invalid";
process.env.SUPABASE_ANON_KEY = "fixture";
let reads = 0;
globalThis.fetch = async (url) => {
  const u = new URL(String(url)), q = Object.fromEntries(u.searchParams);
  let body;
  if (u.pathname.endsWith("/catalogue")) body = FIX.catalogue;
  else if (u.pathname.endsWith("/sources") || u.pathname.endsWith("/headers")) body = [];
  else if (u.pathname.endsWith("/series")) {
    reads += 1;
    const table = q.table_name.replace(/^eq\./, ""), variable = (q.variable ?? "").replace(/^eq\./, "");
    const [, lo] = /ts_utc\.gte\.([^,)]+)/.exec(q.and ?? "") ?? [], [, hi] = /ts_utc\.lt\.([^,)]+)/.exec(q.and ?? "") ?? [];
    const entity = /entity\.eq\."([^"]+)"/.exec(q.and ?? q.or ?? "")?.[1];
    if (/node\.eq\./.test(q.and ?? "")) return new Response("[]", { status: 200, headers: { "content-type": "application/json" } });
    body = FIX.rows.filter((r) => r.table_name === table && (!variable || r.variable === variable) && (!entity || r.entity === entity) && (!lo || Date.parse(r.ts_utc) >= Date.parse(lo)) && (!hi || Date.parse(r.ts_utc) < Date.parse(hi)))
      .sort((x, y) => (x.ts_utc < y.ts_utc ? -1 : 1)).map((r) => ({ t: r.ts_utc, v: r.value, entity: r.entity, variable: r.variable, unit: r.unit }));
  } else throw new Error(`a request the fixture does not hold: ${u.pathname}`);
  return new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } });
};

const { runTool, perKw, PER_KW_TABLES } = await import("../lib/chat/tools.ts");
const { unverified } = await import("../lib/chat/ask.ts");

let n = 0, failed = 0;
const test = async (name, f) => {
  n += 1;
  try { await f(); console.log(`ok ${n} ${name}`); } catch (e) { failed += 1; console.log(`FAIL ${n} ${name}\n   ${e.message.split("\n").slice(0, 6).join("\n   ")}`); }
};
const ask = (q) => runTool("query", { table: "battery_stack_monthly", aggregation: "sum", entity: q.entity, variable: q.variable, start: q.start, end: q.end });

await test("each of the eight is one query call over its twelve months, in USD per MW", async () => {
  delete process.env.ASK_PER_KW;
  for (const [id, q] of Object.entries(FIX.questions)) {
    const before = reads;
    const { out, isError } = await ask(q);
    assert.equal(isError, false, id);
    assert.equal(reads - before, 1, `${id}: one read`);
    assert.deepEqual(out.units, ["USD/MW"], id);
    assert.equal(out.rows_matched, q.months, id);
    assert.equal(out.result.length, 1, id);
    assert.ok(Math.abs(out.result[0].value - q.sum_usd_per_mw) < 1e-4, `${id}: ${out.result[0].value} against ${q.sum_usd_per_mw}`);
  }
});

await test("off by default: no per-kW key in any result", async () => {
  delete process.env.ASK_PER_KW;
  for (const q of Object.values(FIX.questions)) {
    const { out } = await ask(q);
    assert.equal(out.per_kw, undefined);
    assert.equal(out.result[0].value_usd_per_kw, undefined);
    assert.ok(!JSON.stringify(out).includes("usd_per_kw\""));
  }
});

await test("on: value_usd_per_kw is the key within its tolerance, and the number check traces it", async () => {
  process.env.ASK_PER_KW = "on";
  try {
    for (const [id, q] of Object.entries(FIX.questions)) {
      const { out } = await ask(q);
      const kw = out.result[0].value_usd_per_kw;
      assert.ok(Math.abs(kw - q.key_usd_per_kw) <= 0.01, `${id}: ${kw} against the key ${q.key_usd_per_kw}`);
      assert.equal(out.per_kw.unit, "USD/kW");
      assert.match(out.per_kw.rule, /battery_stack\.md/);
      const said = `The total is ${kw.toFixed(2)} USD per kW (battery_stack_monthly).`;
      assert.deepEqual(unverified(said, [JSON.stringify(out)]), [], id);
    }
  } finally { delete process.env.ASK_PER_KW; }
});

await test("off, the same per-kW sentence is sent back by the number check, as on 20 October", async () => {
  delete process.env.ASK_PER_KW;
  const q = FIX.questions.b01;
  const { out } = await ask(q);
  const said = `The total is ${q.key_usd_per_kw.toFixed(2)} USD per kW (battery_stack_monthly).`;
  assert.deepEqual(unverified(said, [JSON.stringify(out)]), [q.key_usd_per_kw.toFixed(2)]);
});

await test("only a table whose method names the conversion, and only rows all in USD/MW", async () => {
  assert.deepEqual(Object.keys(PER_KW_TABLES), ["battery_stack_monthly"]);
  const on = { ASK_PER_KW: "on" };
  const base = () => ({ units: ["USD/MW"], result: [{ value: 1234.5 }] });
  assert.equal(perKw(base(), "merchant_revenue_monthly", on).per_kw, undefined);
  assert.equal(perKw({ units: ["USD/MW", "count"], result: [{ value: 3 }] }, "battery_stack_monthly", on).per_kw, undefined);
  assert.equal(perKw(base(), "battery_stack_monthly", { ASK_PER_KW: "1" }).per_kw, undefined);
  assert.equal(perKw(base(), "battery_stack_monthly", on).result[0].value_usd_per_kw, 1.2345);
});

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
