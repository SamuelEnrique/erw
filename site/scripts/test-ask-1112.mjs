// Energy Research Warehouse (ERW) site, session 1112: a question about a held grid's rows, on session 320's four
// (g07, g08, d05, d07), replayed on saved rows (tests/fixtures/session1112/held_reads.json, written by
// warehouse/chat/eval/fixture_s1112.py). No model and no request.
//
//   node --import ./scripts/alias-register.mjs scripts/test-ask-1112.mjs
//
// What is held here: the tool names the held grid and says its rows are "license needed", states no figure of it, and
// gives the same query's figure for each public grid of the table (ERCOT, CAISO, SPP), the held grids' and MISO's rows
// never in the result; the same in a chat scoped to the held grid; a public grid's question is answered as before; the
// number check traces an answer built from the held result in the brand's sentence structure.
import assert from "node:assert/strict";
import fs from "node:fs";

const FIX = JSON.parse(fs.readFileSync(new URL("../../tests/fixtures/session1112/held_reads.json", import.meta.url), "utf8"));
process.env.SUPABASE_URL = "https://fixture.invalid";
process.env.SUPABASE_ANON_KEY = "fixture";
globalThis.fetch = async (url) => {
  const u = new URL(String(url)), q = Object.fromEntries(u.searchParams);
  let body = [];
  if (u.pathname.endsWith("/catalogue")) body = FIX.catalogue;
  else if (u.pathname.endsWith("/series") && !/node\.eq\./.test(q.and ?? "")) {
    const table = (q.table_name ?? "").replace(/^eq\./, ""), variable = (q.variable ?? "").replace(/^eq\./, "");
    const [, lo] = /ts_utc\.gte\.([^,)]+)/.exec(q.and ?? "") ?? [], [, hi] = /ts_utc\.lt\.([^,)]+)/.exec(q.and ?? "") ?? [];
    const entity = /entity\.eq\."([^"]+)"/.exec(q.and ?? q.or ?? "")?.[1];
    const like = /entity\.like\.([a-z]+):\*/.exec(q.and ?? q.or ?? q.entity ?? "")?.[1];
    body = FIX.rows.filter((r) => r.table_name === table && (!variable || r.variable === variable) && (!entity || r.entity === entity) && (!like || r.entity.startsWith(`${like}:`))
      && (!lo || Date.parse(r.ts_utc) >= Date.parse(lo)) && (!hi || Date.parse(r.ts_utc) < Date.parse(hi)))
      .map((r) => ({ t: r.ts_utc, v: r.value, g: r.entity, entity: r.entity, variable: r.variable, unit: r.unit }));
  }
  return new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } });
};

const { runTool, heldGridOf, scopeOf } = await import("../lib/chat/tools.ts");
const { unverified } = await import("../lib/chat/ask.ts");
const HELD = /^(isone|nyiso|miso):/;

let n = 0, failed = 0;
const test = async (name, f) => {
  n += 1;
  try { await f(); console.log(`ok ${n} ${name}`); } catch (e) { failed += 1; console.log(`FAIL ${n} ${name}\n   ${e.message.split("\n").slice(0, 6).join("\n   ")}`); }
};
const ask = (q, scope = null, entity = q.entity) => runTool("query", { table: q.table, aggregation: "mean", entity, variable: q.variable, start: q.start, end: q.end }, scope);

await test("each of the four: the held grid named, license needed, no figure of it, every public grid's figure", async () => {
  for (const [id, q] of Object.entries(FIX.questions)) {
    const { out, isError } = await ask(q);
    assert.equal(isError, false, id);
    assert.equal(out.held, true, id);
    assert.equal(out.grid, q.entity.startsWith("nyiso:") ? "NYISO" : "ISO-NE", id);
    assert.equal(out.grid_license, "license needed");  // license stays the table's own tier, from its provenance
    assert.match(out.words, /are held for a license: license needed$/);
    const shown = Object.fromEntries(out.public_grids.map((r) => [r.entity, r.value]));
    assert.deepEqual(shown, q.public, id);
    assert.ok(out.public_grids.every((r) => ["ERCOT", "CAISO", "SPP"].includes(r.grid)), id);
    assert.ok(!HELD.test(JSON.stringify(out.public_grids)), id);
  }
});

await test("no figure of a held grid is anywhere in the result", async () => {
  for (const [id, q] of Object.entries(FIX.questions)) {
    const { out } = await ask(q);
    const text = JSON.stringify(out);
    for (const r of FIX.rows.filter((x) => HELD.test(x.entity) && x.variable === q.variable && x.ts_utc.startsWith(q.start))) {
      const pub = Object.values(q.public);
      if (!pub.some((v) => Math.abs(v - r.value) < 1e-9)) assert.ok(!text.includes(String(r.value)), `${id}: ${r.entity} ${r.value}`);
    }
  }
});

await test("a chat scoped to the held grid, asked with no entity, says the same", async () => {
  const q = FIX.questions.g08;
  assert.equal(heldGridOf({ table: q.table }, scopeOf("nyiso")), "nyiso");
  assert.equal(heldGridOf({ table: q.table }, scopeOf("ercot")), "");
  assert.equal(heldGridOf({ table: q.table, entity: "ercot:HB_HUBAVG" }, scopeOf("nyiso")), "");
  assert.equal(heldGridOf({ table: "battery_stack_monthly", entity: "nyiso:N.Y.C." }), "");
});

await test("a public grid's question is answered as before", async () => {
  const q = FIX.questions.g08;
  const { out } = await ask(q, null, "ercot:HB_HUBAVG");
  assert.equal(out.held, undefined);
  assert.equal(out.result[0].value, q.public["ercot:HB_HUBAVG"]);
});

await test("an answer in the brand's sentence structure passes the number check", async () => {
  const q = FIX.questions.g08;
  const { out } = await ask(q);
  const fig = (e) => out.public_grids.find((r) => r.entity === e).value.toFixed(2);
  const said = `NYISO's rows are held for a license (license needed). For the public grids, the flat price in July 2026: ERCOT ${fig("ercot:HB_HUBAVG")} USD/MWh, CAISO ${fig("caiso:TH_SP15_GEN-APND")} USD/MWh, SPP ${fig("spp:SPPNORTH_HUB")} USD/MWh (merchant_revenue_monthly).`;
  assert.deepEqual(unverified(said, [JSON.stringify(out), JSON.stringify({ start: q.start, end: q.end })]), []);
});

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
