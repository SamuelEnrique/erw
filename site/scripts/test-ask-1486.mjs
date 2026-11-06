// Energy Research Warehouse (ERW) site, session 1486 (chain 158): a compare call without one of its two queries is a
// tool error the model sees, not a TypeError that ends the route with a 502 (the board's k03 of session 2918: "Cannot
// read properties of undefined (reading 'aggregation')"). No model and no request: the refusal comes before any read.
//
//   node --import ./scripts/alias-register.mjs scripts/test-ask-1486.mjs
import assert from "node:assert/strict";

process.env.SUPABASE_URL = "https://fixture.invalid";
process.env.SUPABASE_ANON_KEY = "fixture";
let reads = 0;
globalThis.fetch = async () => { reads += 1; return new Response("[]", { status: 200, headers: { "content-type": "application/json" } }); };
const T = await import("../lib/chat/tools.ts");
let n = 0;
const test = async (name, f) => { await f(); n += 1; console.log(`ok   ${name}`); };

await test("compare without b is a tool error", async () => {
  const r = await T.runTool("compare", { a: { table: "price_board_spreads", aggregation: "latest" } });
  assert.equal(r.isError, true);
  assert.match(r.out.error, /^compare needs b: the arguments of a query/);
});
await test("compare with no arguments at all is a tool error", async () => {
  const r = await T.runTool("compare", {});
  assert.equal(r.isError, true);
  assert.match(r.out.error, /^compare needs a:/);
});
await test("compare with a side that is not an object is a tool error", async () => {
  const r = await T.runTool("compare", { a: "price_board_spreads", b: [] });
  assert.equal(r.isError, true);
  assert.match(r.out.error, /^compare needs a:/);
});
await test("a query with no arguments is a tool error", async () => {
  const r = await T.runTool("query", undefined);
  assert.equal(r.isError, true);
  assert.match(r.out.error, /aggregation must be one of|query needs its arguments/);
});
assert.equal(reads, 0);
console.log(`${n} passed`);
