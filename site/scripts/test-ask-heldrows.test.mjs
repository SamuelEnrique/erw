// Energy Research Warehouse (ERW) site, session 5260 (chain 238): the hold by grid for a table of things, in the
// chat's tools (lib/chat/heldrows.ts), as warehouse/chat/license_hold.py and warehouse/chat/tools.py hold it
// (tests/test_session5260_ask.py). The license file is the repository's own (site/data/license_status.json). No build,
// no network.
//
//   node --import ./scripts/alias-register.mjs --test scripts/test-ask-heldrows.test.mjs
//   node --import ./scripts/alias-register.mjs scripts/test-ask-heldrows.test.mjs --own     prints ownGrid of every table of the license file, as JSON
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { heldRowsWords, keepRows, misoOwnId, ownGrid, ownTableWords, rowId } from "../lib/chat/heldrows.ts";

const status = JSON.parse(fs.readFileSync(new URL("../data/license_status.json", import.meta.url), "utf8"));

if (process.argv.includes("--own")) {
  console.log(JSON.stringify(Object.fromEntries(Object.keys(status.tables).sort().map((t) => [t, ownGrid(t)]))));
} else {
  test("a held grid's own table, by its name and the grids that decide it", () => {
    assert.equal(ownGrid("isone_interconnection_queue"), "isone");
    assert.equal(ownGrid("nyiso_interconnection_queue"), "nyiso");
    assert.equal(ownGrid("nyiso_dam_zone_prices"), "nyiso");
    assert.equal(ownGrid("isone_rtm_zone_prices"), "isone");
    assert.equal(ownGrid("miso_interconnection_queue"), "miso");
    // a table several grids share, a table held whole, a table not held
    for (const t of ["energy_projects", "iso_dam_hub_prices", "merchant_revenue_monthly", "energy_deals", "policy_actions", "ercot_interconnection_queue", "lbnl_interconnection_queue", "no_such_table"])
      assert.equal(ownGrid(t), "", t);
  });

  test("a row is its grid's by its entity, or by a thing's id", () => {
    assert.equal(rowId({ entity: "isone:.H.INTERNAL_HUB" }), "isone:.H.INTERNAL_HUB");
    assert.equal(rowId({ id: "isone_queue:1630" }), "isone_queue:1630");
    assert.equal(rowId({ entity_id: "nyiso_queue:7" }), "nyiso_queue:7");
    assert.equal(rowId({ v: 3 }), "");
    assert.equal(misoOwnId("miso_queue:J1234"), true);
    assert.equal(misoOwnId("miso:INDIANA.HUB"), true);
    assert.equal(misoOwnId("ercot_queue:1"), false);
  });

  test("a shared table of things is read without a held grid's rows and without MISO's own", () => {
    const rows = [{ id: "eia860:649:4", v: 1114 }, { id: "isone_queue:1630", v: 1 }, { id: "ercot_queue:9", v: 2 }, { id: "miso_queue:J1", v: 3 }, { v: 4 }];
    const k = keepRows("energy_projects", "entities", rows);
    assert.deepEqual(k.kept.map((r) => r.id ?? null), ["eia860:649:4", "ercot_queue:9", null]);
    assert.deepEqual([k.held, k.paused], [1, 1]);
    // a read that matched only a held grid's rows keeps none, and says how many it left out
    assert.deepEqual(keepRows("energy_projects", "entities", [{ id: "isone_queue:1" }, { id: "isone_queue:2" }]), { kept: [], held: 2, paused: 0 });
    // a table that is not held loses MISO's own rows only
    assert.deepEqual(keepRows("lbnl_interconnection_queue", "entities", [{ id: "isone_queue:1" }, { id: "miso_queue:2" }]).kept, [{ id: "isone_queue:1" }]);
  });

  test("a series table is left as lib/supabase.ts gave it", () => {
    const rows = [{ entity: "isone:.H.INTERNAL_HUB" }, { entity: "miso:INDIANA.HUB" }];
    assert.deepEqual(keepRows("iso_dam_hub_prices", "series", rows), { kept: rows, held: 0, paused: 0 });
  });

  test("the words of the two refusals", () => {
    const whole = ownTableWords("isone_interconnection_queue");
    assert.ok(whole.startsWith("table isone_interconnection_queue is license needed: ISO-NE: "), whole);
    assert.match(whole, /State no figure of it: answer with not_in_warehouse true and say that it is "license needed"$/);
    const rows = heldRowsWords("energy_projects");
    assert.ok(rows.startsWith("the rows of energy_projects that match are a held grid's own and are license needed: "), rows);
    assert.ok(!rows.startsWith("table "), "a refusal of rows, not of the table: the table's other rows are read");
  });

  test("every held grid's own table of the license file is known by its name", () => {
    const own = Object.keys(status.tables).filter((t) => ownGrid(t));
    assert.ok(own.length >= 5, String(own.length));
    for (const t of own) assert.match(t, /^(isone|nyiso|miso|pjm|spp|caiso|ercot)_/, t);
  });
}
