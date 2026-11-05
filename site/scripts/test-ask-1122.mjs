// Energy Research Warehouse (ERW) site, session 1122: Ask reads the board. The tool board_rank (lib/chat/tools.ts) on
// the rows of price_board_latest and price_board_spreads recorded from the live set (tests/fixtures/session1122/
// board_reads.json). No model and no request.
//
//   node --import ./scripts/alias-register.mjs scripts/test-ask-1122.mjs
//
// What is held here: for each of the five board questions of warehouse/chat/eval/questions_s1122.yaml, board_rank gives
// every public hub's newest value of the measure, ranked as asked, the first being the key; the held grids' rows
// (ISO-NE, NYISO) are never in it; it is one read, and its figures are query's own (latest by entity); a bad measure is
// refused with the list.
import assert from "node:assert/strict";
import fs from "node:fs";

const read = (p) => JSON.parse(fs.readFileSync(new URL(p, import.meta.url), "utf8"));
const FIX = read("../../tests/fixtures/session1122/board_reads.json");
const KEYS = read("../../warehouse/chat/eval/expected_s1122.json");
process.env.SUPABASE_URL = "https://fixture.invalid";
process.env.SUPABASE_ANON_KEY = "fixture";
let reads = 0;
globalThis.fetch = async (url) => {
  const u = new URL(String(url)), q = Object.fromEntries(u.searchParams);
  let body = [];
  if (u.pathname.endsWith("/catalogue")) body = FIX.catalogue;
  else if (u.pathname.endsWith("/series") && !/node\.eq\./.test(q.and ?? "")) {
    reads += 1;
    const table = (q.table_name ?? "").replace(/^eq\./, ""), variable = (q.variable ?? "").replace(/^eq\./, "");
    body = FIX.rows.filter((r) => r.table_name === table && (!variable || r.variable === variable))
      .sort((a, b) => (a.ts_utc < b.ts_utc ? -1 : 1)).map((r) => ({ t: r.ts_utc, v: r.value, g: r.entity, entity: r.entity, variable: r.variable, unit: r.unit }));
  }
  return new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } });
};
const { runTool, rankRows, BOARD_MEASURES } = await import("../lib/chat/tools.ts");

let n = 0, failed = 0;
const test = async (name, f) => {
  n += 1;
  try { await f(); console.log(`ok ${n} ${name}`); } catch (e) { failed += 1; console.log(`FAIL ${n} ${name}\n   ${e.message.split("\n").slice(0, 6).join("\n   ")}`); }
};
const HELD = /^(isone|nyiso|miso):/;

await test("the five board questions: the first of the ranking is the key, every hub public", async () => {
  assert.equal(KEYS.questions.length, 5);
  for (const k of KEYS.questions) {
    const before = reads;
    const { out, isError } = await runTool("board_rank", { measure: k.measure, order: k.order });
    assert.equal(isError, false, k.id);
    assert.equal(reads - before, 1, `${k.id}: one read`);
    assert.equal(out.table, BOARD_MEASURES[k.measure]);
    assert.ok(out.ranked.length >= 3 && out.ranked.every((r) => !HELD.test(r.entity)), `${k.id}: ${out.ranked.map((r) => r.entity).join(", ")}`);
    assert.equal(out.ranked[0].entity, k.entity, k.id);
    assert.ok(Math.abs(out.ranked[0].value - k.value) < 1e-6, `${k.id}: ${out.ranked[0].value} against ${k.value}`);
    assert.deepEqual(out.ranked.map((r) => r.entity), k.ranking, k.id);
  }
});

await test("the ranking rule: highest, lowest, and the size of a move whatever its sign", () => {
  const rows = [{ entity: "a", value: 3 }, { entity: "b", value: -7 }, { entity: "c", value: 5 }, { entity: "d", value: null }];
  assert.deepEqual(rankRows(rows, "highest").map((r) => r.entity), ["c", "a", "b"]);
  assert.deepEqual(rankRows(rows, "lowest").map((r) => r.entity), ["b", "a", "c"]);
  assert.deepEqual(rankRows(rows, "largest_move").map((r) => r.entity), ["b", "c", "a"]);
});

await test("a measure the board does not have is refused with the list", async () => {
  const { out, isError } = await runTool("board_rank", { measure: "nonsense" });
  assert.equal(isError, true);
  assert.match(out.error, /measure must be one of .*spark_spread_7/);
});

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
