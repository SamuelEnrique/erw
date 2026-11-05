// Session 505: check-holds.mjs judged on pages written here, no server and no request.
//   node scripts/test-check-holds.mjs
import assert from "node:assert/strict";
import { cardHolds, cardsOf, heldGridsOf, heldTables, judgeKey, judgePage, keysOf, multipleGridsOf, readStatusCsv } from "./check-holds.mjs";

const CSV = `table,status,from,publishers,verdict,permission,permission_ref,note
iso_hub_prices_history,license needed,2026-10-21,ISO-NE; MISO; NYISO,needs written permission,,,a note, with a comma
energy_deals,license needed,2026-10-21,Reuters; WSJ,needs written permission,,,
nyiso_dam_zone_prices,license needed,2026-10-21,NYISO,needs written permission,,,
later_table,license needed,2026-12-01,NYISO,needs written permission,,,
granted_table,public,2026-10-21,NYISO,needs written permission,yes,ref,
`;
const rows = readStatusCsv(CSV);
const held = heldTables(rows, "2026-10-21");
const grids = heldGridsOf(held);
let n = 0;
const test = (name, f) => { f(); n++; console.log(`ok ${n} ${name}`); };

test("the status file: held from its day, a recorded permission not held, a comma kept in the note", () => {
  assert.deepEqual([...held.keys()].sort(), ["energy_deals", "iso_hub_prices_history", "nyiso_dam_zone_prices"]);
  assert.equal(rows[0].note, "a note, with a comma");
  assert.equal(held.get("iso_hub_prices_history").byGrid, true);
  assert.equal(held.get("energy_deals").byGrid, false);
  assert.deepEqual([...grids].sort(), ["isone", "miso", "nyiso"]);
});

test("Num's own rule: a held grid's series figure is a leak, another grid's is not", () => {
  assert.ok(judgeKey("series|iso_hub_prices_history|nyiso:N.Y.C.|lmp|2026-01-01T05:00:00Z", held, grids));
  assert.equal(judgeKey("series|iso_hub_prices_history|ercot:HB_HUBAVG|lmp|2026-01-01T05:00:00Z", held, grids), null);
  assert.equal(judgeKey("series|eia930_all_generation|nyiso:NYIS|ng|2026-01-01", held, grids), null, "a public table's NYISO row shows");
});

test("a series key of a table held by grid with no grid in it asks about the table whole, as Num does", () => {
  const r = judgeKey("series|iso_hub_prices_history|-|mean", held, grids);
  assert.ok(r && /no grid in its key/.test(r.why));
});

test("a table held whole: every figure, by its first word (deals| is energy_deals)", () => {
  assert.ok(judgeKey("deals|comp_median|ppa|-", held, grids));
  assert.ok(judgeKey("entity|energy_deals|d1|mw", held, grids));
});

test("iso= in a model key names its grid, as gridEntityOfKey reads it", () => {
  assert.equal(judgeKey("mr|iso=ercot&asset=solar|revenue", new Map([["merchant_revenue_monthly", { byGrid: true, grids: new Set(["nyiso"]) }]]), grids), null);
  assert.ok(judgeKey("mr|iso=nyiso&asset=solar|revenue", new Map([["merchant_revenue_monthly", { byGrid: true, grids: new Set(["nyiso"]) }]]), grids));
});

test("a finding's figure is held by the grid its last word names; latest_prices by its entity's grid", () => {
  assert.ok(judgeKey("finding|peak_hour_grids|callout|0|after|nyiso", held, grids));
  assert.equal(judgeKey("finding|peak_hour_grids|callout|0|after|ercot", held, grids), null);
  assert.ok(judgeKey("latest_prices|isone:.H.INTERNAL_HUB|lmp", held, grids));
});

test("a first word Num does not read: a held table among its words, with the grid of its words", () => {
  assert.ok(judgeKey("digest_dam|NYISO|nyiso_dam_zone_prices|N.Y.C.|2026-10-20", held, grids));
  assert.equal(judgeKey("digest_dam|ERCOT|ercot_dam_hub_prices|HB_HUBAVG|2026-10-20", held, grids), null);
});

test("records about a table are passed by: catalogue counts, the licensing record, a header's counts", () => {
  assert.equal(judgeKey("catalogue|energy_deals|n_rows", held, grids), null);
  assert.equal(judgeKey("lic|held|count", held, grids), null);
  assert.equal(judgeKey("series_hdr|iso_hub_prices_history|iso:nyiso|counts|NYISO", held, grids), null);
});

test("keys read from the page, entities unescaped", () => {
  assert.deepEqual(keysOf('<span data-check="mr|iso=nyiso&amp;asset=solar|x" data-raw="1">1</span><span data-license-held="t">license needed</span>'), ["mr|iso=nyiso&asset=solar|x"]);
});

const CARD = { tables: ["iso_hub_prices_history", "eia930_daily_demand"], chart: { kind: "multiples", param: "lunch_grid", panels: [{ grid: "ercot", words: "ERCOT" }, { grid: "nyiso", words: "NYISO" }] } };
const PAGE = `<article class="finding-card" data-finding="lunch"><div data-multi="lunch_grid" data-multi-view="all">
<div data-option-kind="panels" data-finding-chart="multiples"><div class="mb-2" data-panel="0"><p class="x">ERCOT, West hub</p><g data-series="ERCOT: spread"></g></div>
<div class="mb-2" data-panel="1"><p class="x">NYISO, Zone J</p><g data-series="NYISO: spread"></g></div></div></div></article>
<article data-finding="other"><g data-series="NYISO: load"></g></article>
<p data-downloads="2"><span data-download-table="iso_hub_prices_history">x</span></p><g data-series="ISO-NE demand"></g>`;

test("the cards on a page and the grids their small multiples draw", () => {
  const cs = cardsOf(PAGE);
  assert.deepEqual(cs.map((c) => c.card), ["lunch", "other"]);
  assert.deepEqual([...multipleGridsOf(cs[0].html)].sort(), ["ercot", "nyiso"]);
  assert.equal(multipleGridsOf(cs[1].html).size, 0, "a card with no small multiples draws no panel");
});

test("a card's holds: the grids by which its tables are held", () => {
  const h = cardHolds(CARD, held);
  assert.deepEqual(h.tables, ["iso_hub_prices_history"]);
  assert.deepEqual([...h.grids].sort(), ["isone", "miso", "nyiso"]);
  assert.equal(h.whole, false);
});

test("a page judged: NYISO's panel is a leak, ERCOT's is not; a series on a page reading a held table is to read by hand", () => {
  const j = judgePage("/research/card/lunch", PAGE, held, grids, (c) => (c === "lunch" ? CARD : null));
  assert.deepEqual(j.leaks.map((x) => [x.kind, x.grid]), [["panel", "nyiso"]]);
  assert.deepEqual(j.possible.map((x) => x.key).sort(), ["ISO-NE demand", "NYISO: load", "NYISO: spread"]);
});

test("a page with no held figure has no leak", () => {
  const j = judgePage("/x", '<span data-check="series|ercot_dam_hub_prices|ercot:HB_HUBAVG|lmp|t" data-raw="1">1</span>', held, grids, () => null);
  assert.equal(j.leaks.length, 0);
  assert.equal(j.keys, 1);
});

console.log(`${n} tests passed`);
