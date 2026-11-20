// Energy Research Warehouse (ERW) site, session 9812: every try of the internal token from one address is counted, right
// or wrong (lib/guard.ts, TOKEN_TRIES). No server and no network: no salt is set, so the limit is this instance's memory,
// the floor it keeps when the database cannot be asked.
//
//   node --import ./scripts/alias-register.mjs scripts/test-token-tries.mjs
//
// Exits 1 on the first failure.
import assert from "node:assert/strict";

delete process.env.ASK_VISITOR_SALT;
const guard = await import("../lib/guard.ts");

let n = 0;
const test = async (name, f) => { await f(); n += 1; console.log(`ok   ${name}`); };
const req = (ip) => new Request("https://erw.example/internal/unlock", { headers: { "x-forwarded-for": ip } });

await test(`${guard.TOKEN_TRIES} tries an hour from one address, then none, right token or wrong`, async () => {
  assert.equal(guard.TOKEN_TRIES, 30);
  for (let i = 0; i < guard.TOKEN_TRIES; i += 1) assert.equal(await guard.tokenTriesLeft(req("198.51.100.7")), true, `try ${i + 1}`);
  assert.equal(await guard.tokenTriesLeft(req("198.51.100.7")), false);
  assert.equal(await guard.tokenTriesLeft(req("198.51.100.7")), false);
});

await test("another address keeps its own count", async () => {
  assert.equal(await guard.tokenTriesLeft(req("198.51.100.8")), true);
});

await test("a page's headers are read for the same address", async () => {
  const h = new Headers({ "x-forwarded-for": "198.51.100.7", cookie: "not read" });
  assert.equal(await guard.pageTokenTriesLeft(h), false);
  assert.equal(await guard.pageTokenTriesLeft(new Headers({ "x-real-ip": "198.51.100.9" })), true);
});

console.log(`${n} passed`);
