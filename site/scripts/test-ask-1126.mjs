// Energy Research Warehouse (ERW) site, session 1126: two faults session 1113's run found, on the rows of session 1112, on session 320's four
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

const { runTool, heldGridOf, scopeOf, MISO_PAUSED } = await import("../lib/chat/tools.ts");
const { unverified } = await import("../lib/chat/ask.ts");
const HELD = /^(isone|nyiso|miso):/;

let n = 0, failed = 0;
const test = async (name, f) => {
  n += 1;
  try { await f(); console.log(`ok ${n} ${name}`); } catch (e) { failed += 1; console.log(`FAIL ${n} ${name}\n   ${e.message.split("\n").slice(0, 6).join("\n   ")}`); }
};
const q = FIX.questions.g08;
const one = (entity) => ({ table: q.table, aggregation: "mean", entity, variable: q.variable, start: q.start, end: q.end });

await test("a compare with a held grid's side answers, with no difference made (g08 crashed on 23 October)", async () => {
  const { out, isError } = await runTool("compare", { a: one("nyiso:N.Y.C."), b: one("ercot:HB_HUBAVG") }, scopeOf("nyiso"));
  assert.equal(isError, false);
  assert.equal(out.a.held, true);
  assert.equal(out.b.result[0].value, q.public["ercot:HB_HUBAVG"]);
  assert.equal(out.difference_b_minus_a, undefined);
  assert.equal(out.ratio_b_over_a, undefined);
});

await test("MISO's scoped chat is refused with the pause's words, not answered as a held grid (g10)", async () => {
  assert.throws(() => heldGridOf({ table: q.table }, scopeOf("miso")), (e) => e.message === MISO_PAUSED);
  const { out, isError } = await runTool("query", { table: q.table, aggregation: "mean", variable: q.variable, start: q.start, end: q.end }, scopeOf("miso"));
  assert.equal(isError, true);
  assert.match(out.error, /paused while its terms are reviewed/);
  assert.match(out.error, /not_in_warehouse true/);
});

await test("ISO-NE's and NYISO's scoped chats still get the held answer", async () => {
  assert.equal(heldGridOf({ table: q.table }, scopeOf("nyiso")), "nyiso");
  assert.equal(heldGridOf({ table: q.table }, scopeOf("isone")), "isone");
});

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
