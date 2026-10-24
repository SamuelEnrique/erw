// Energy Research Warehouse (ERW) site, session 1132: a refusal of the general chat names the tables it looked at, with
// what each holds from the catalogue (lib/chat/tools.ts holdsLine, nearestFor). No model and no request: the catalogue
// is session 1112's recorded rows.
//
//   node --import ./scripts/alias-register.mjs scripts/test-ask-1132.mjs
import assert from "node:assert/strict";
import fs from "node:fs";

const FIX = JSON.parse(fs.readFileSync(new URL("../../tests/fixtures/session1112/held_reads.json", import.meta.url), "utf8"));
process.env.SUPABASE_URL = "https://fixture.invalid";
process.env.SUPABASE_ANON_KEY = "fixture";
globalThis.fetch = async (url) => {
  const u = new URL(String(url));
  const body = u.pathname.endsWith("/catalogue") ? FIX.catalogue : [];
  return new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } });
};
const { holdsLine, nearestFor } = await import("../lib/chat/tools.ts");
const loop = fs.readFileSync(new URL("../lib/chat/ask.ts", import.meta.url), "utf8");

let n = 0, failed = 0;
const test = async (name, f) => {
  n += 1;
  try { await f(); console.log(`ok ${n} ${name}`); } catch (e) { failed += 1; console.log(`FAIL ${n} ${name}\n   ${e.message.split("\n").slice(0, 6).join("\n   ")}`); }
};

await test("what a table holds, from the catalogue's own fields", () => {
  assert.equal(holdsLine({ sector: "power", iso: "CAISO;ERCOT", interval: "P1M", ts_min: "2018-07-01T00:00:00+00:00", ts_max: "2026-10-01T00:00:00+00:00", source_report: "erw:cost_of_power" }),
    "power data; CAISO, ERCOT; step P1M; 2018-07-01 to 2026-10-01; from erw:cost_of_power");
  assert.equal(holdsLine({ sector: null, iso: "none", interval: null, ts_min: null, ts_max: null, source_report: null }), "");
});

await test("the nearest: the tables looked at that the catalogue holds, at most three, each once", async () => {
  const near = await nearestFor(["cost_of_power_monthly", "no_such_table", "merchant_revenue_monthly", "cost_of_power_monthly"]);
  assert.deepEqual(near.map((x) => x.table), ["cost_of_power_monthly", "merchant_revenue_monthly"]);
  assert.match(near[0].holds, /^power data; .*step P1M; .* to .*; from erw:cost_of_power$/);
  assert.deepEqual(await nearestFor([]), []);
});

await test("the loop names them on the general chat's two refusals only", () => {
  assert.ok(loop.includes('if (!profile && status === "not_in_warehouse" && looked.size)'));
  assert.ok(loop.includes("const nearest = profile ? [] : await nearestFor([...looked]);"));
  assert.ok(loop.includes('if (!isError && name === "describe_table" && typeof input.table === "string") looked.add(input.table);'));
});

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
