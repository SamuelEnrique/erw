// Energy Research Warehouse (ERW) site, session 9811: a row of a table held by grid is known by its id, whatever the
// shape of the table (lib/supabase.ts restPaged). A series row by its entity; a thing by its entity_id; an event by its
// event_id. No server and no network: fetch is a stub that answers one page of rows.
//
//   node --import ./scripts/alias-register.mjs scripts/test-heldrow-ids.mjs
//
// Exits 1 on the first failure.
import assert from "node:assert/strict";

process.env.SUPABASE_URL = "https://stub.invalid";
process.env.SUPABASE_ANON_KEY = "stub-anon-key-not-a-secret";

let answer = [];
globalThis.fetch = async () => new Response(JSON.stringify(answer), { status: 200, headers: { "Content-Type": "application/json" } });

const { rest } = await import("../lib/supabase.ts");
const { licenseNeeded, licenseByGrid, licenseHeldRow } = await import("../lib/license.ts");

let n = 0;
const test = async (name, f) => { await f(); n += 1; console.log(`ok   ${name}`); };

const T = "energy_projects";
await test(`${T} is held by grid today (the premise of the cases below)`, () => {
  assert.equal(licenseNeeded(T), true);
  assert.equal(licenseByGrid(T), true);
  assert.equal(licenseHeldRow(T, "isone_queue:1630"), true);
  assert.equal(licenseHeldRow(T, "nyiso_queue:0001"), true);
  assert.equal(licenseHeldRow(T, "ercot_queue:21INR0001"), false);
});

await test("a thing's row is left out by its entity_id when its grid is held", async () => {
  answer = [
    { entity_id: "ercot_queue:21INR0001", capacity_mw: 100 },
    { entity_id: "isone_queue:1630", capacity_mw: 200 },
    { entity_id: "nyiso_queue:0001", capacity_mw: 300 },
    { entity_id: "miso_queue:J1234", capacity_mw: 400 },
    { entity_id: "eia860m:12345", capacity_mw: 500 },
  ];
  const rows = await rest("entities", { select: "entity_id,capacity_mw", table_name: `eq.${T}`, order: "entity_id" }, 3600);
  assert.deepEqual(rows.map((r) => r.entity_id), ["ercot_queue:21INR0001", "eia860m:12345"]);
});

await test("one row asked for by its id (the map's card) is not answered when its grid is held", async () => {
  answer = [{ entity_id: "isone_queue:1630", name: "x" }];
  const rows = await rest("entities", { select: "entity_id,name", table_name: `eq.${T}`, entity_id: "eq.isone_queue:1630" }, 3600, 1);
  assert.deepEqual(rows, []);
  answer = [{ entity_id: "ercot_queue:21INR0001", name: "y" }];
  const open = await rest("entities", { select: "entity_id,name", table_name: `eq.${T}`, entity_id: "eq.ercot_queue:21INR0001" }, 3600, 1);
  assert.equal(open.length, 1);
});

await test("a series row is still left out by its entity", async () => {
  const S = "iso_dam_hub_prices";
  assert.equal(licenseByGrid(S), true);
  assert.equal(licenseHeldRow(S, "miso:INDIANA.HUB"), true);
  answer = [
    { entity: "ercot:HB_HUBAVG", value: 1 },
    { entity: "miso:INDIANA.HUB", value: 2 },
  ];
  const rows = await rest("series", { select: "entity,value", table_name: `eq.${S}` }, 3600);
  assert.deepEqual(rows.map((r) => r.entity), ["ercot:HB_HUBAVG"]);
});

await test("the entity route asks the same reader (app/api/entity/route.ts reads through lib/data.ts entity)", async () => {
  const { entity } = await import("../lib/data.ts");
  answer = [{ entity_id: "nyiso_queue:0001", entity_type: "queue_position", name: "z", table_name: T }];
  assert.equal(await entity(T, "nyiso_queue:0001"), null);
});

console.log(`${n} passed`);
