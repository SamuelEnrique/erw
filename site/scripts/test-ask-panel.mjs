// Energy Research Warehouse (ERW) site, session 137: Ask ERCOT as the answer panel. What lib/chat/panel.ts gives the
// ERCOT profile, tested without a model call or a request: the rows the page tool may read (ERCOT's and no grid's,
// never another grid's), what it returns for a search and for a series (the page's own figures, unchanged), and the
// addendum of the system prompt (the forms, the page's written content, what is refused).
//
//   node --import ./scripts/alias-register.mjs scripts/test-ask-panel.mjs
//
// Exit 1 on a failure.
import assert from "node:assert/strict";
import fs from "node:fs";
import * as p from "../lib/chat/panel.ts";
import { judge } from "./eval-judge.mjs";

let n = 0;
const test = (name, fn) => { fn(); n += 1; console.log(`ok   ${name}`); };
const board = JSON.parse(fs.readFileSync(new URL("../data/board.json", import.meta.url), "utf8"));
const supply = JSON.parse(fs.readFileSync(new URL("../data/supply.json", import.meta.url), "utf8"));
const OTHERS = ["CAISO", "ISO-NE", "MISO", "NYISO", "PJM", "SPP"];

test("the board's rows for ERCOT are ERCOT's and no grid's: never another grid's", () => {
  const rows = p.boardRows("ERCOT");
  assert.ok(rows.length > 100);
  assert.ok(rows.every((r) => !r.tags?.grid || r.tags.grid === "ERCOT"));
  assert.ok(rows.some((r) => r.id === "ercot-hb-hubavg-da") && rows.some((r) => r.id === "eia-henry-hub-spot"));
  // session 5264: every row tagged ERCOT and every row of no grid; of the hub spreads, which carry no grid tag, only ERCOT's own
  const own = board.rows.filter((r) => r.group === "hubspread" && JSON.stringify(p.gridsOf(r)) === '["ERCOT"]');
  assert.equal(rows.length, board.rows.filter((r) => r.group !== "hubspread" && (!r.tags?.grid || r.tags.grid === "ERCOT")).length + own.length);
  assert.ok(!rows.some((r) => OTHERS.includes(r.tags?.grid)));
  // told from the id alone, not through gridsOf: no row returned names another grid's hub
  assert.deepEqual(rows.filter((r) => /(^|-)(caiso|miso|pjm|nyiso|isone|spp)-/.test(r.id)).map((r) => r.id), []);
});

// Session 5264. The group "Hub spreads, within and across grids" (session 1606) tags its rows with a scope and no grid.
// The panel took a row with no grid tag for a row of no grid, so ERCOT's panel read CAISO's and SPP's own spreads and the
// spreads across grids, and this script failed on main at the search below (window P1 found it on 13 November 2026).
test("a hub spread is of its two hubs' grids: a panel reads its own grid's spreads and no other", () => {
  const hubs = (id, group = "hubspread", tags = { market: "da", scope: "within" }) => p.gridsOf({ id, group, tags });
  assert.deepEqual(hubs("ercot-hb-north-ercot-hb-houston-da"), ["ERCOT"]);
  assert.deepEqual(hubs("caiso-th-np15-gen-apnd-caiso-th-sp15-gen-apnd-rt"), ["CAISO"]);
  assert.deepEqual(hubs("caiso-th-sp15-gen-apnd-ercot-hb-hubavg-da", "hubspread", { market: "da", scope: "across" }), ["CAISO", "ERCOT"]);
  assert.deepEqual(hubs("ercot-hb-hubavg-spp-sppnorth-hub-rt", "hubspread", { market: "rt", scope: "across" }), ["ERCOT", "SPP"]);
  assert.equal(hubs("ercot-hb-hubavg-somewhere-else-da"), null);                       // a hub the board does not name: no panel's
  assert.equal(hubs("ercot-hb-hubavg-somewhere-else-da", "newgroup", { scope: "across" }), null);   // by its scope, whatever its group
  assert.deepEqual(p.gridsOf({ id: "ercot-hb-hubavg-da", group: "power", tags: { grid: "ERCOT", market: "da" } }), ["ERCOT"]);
  assert.deepEqual(p.gridsOf({ id: "eia-henry-hub-spot", group: "gas", tags: {} }), []);
  assert.deepEqual(p.gridsOf({ id: "gashub-transco-zone-6-new-york", group: "gas" }), []);
  assert.deepEqual(p.gridsOf({ id: "pjm-something-new", group: "later", tags: { market: "da" } }), ["PJM"]);   // an untagged row a grid's name begins: that grid's
  // the file as it stands: each spread is read by the panel of its one grid and by no other; a spread across grids by none
  const spreads = board.rows.filter((r) => r.group === "hubspread");
  assert.ok(spreads.length >= 14);
  for (const [iso, slug] of [["ERCOT", "ercot"], ["CAISO", "caiso"], ["SPP", "spp"], ["PJM", "pjm"]]) {
    const ids = new Set(p.boardRows(iso).map((r) => r.id));
    for (const r of spreads) {
      const mine = JSON.stringify(p.gridsOf(r)) === JSON.stringify([iso]);
      assert.equal(ids.has(r.id), mine, `${iso} ${r.id}`);
      if (!mine) assert.ok(String(p.pageFigures({ page: "board", series: r.id }, slug, iso).error).includes("no row"), `${iso} ${r.id} by its id`);
    }
  }
  const ercot = new Set(p.boardRows("ERCOT").map((r) => r.id));
  for (const id of ["ercot-hb-north-ercot-hb-houston-da", "ercot-hb-west-ercot-hb-north-rt"]) assert.ok(ercot.has(id), id);
  for (const id of ["caiso-th-np15-gen-apnd-caiso-th-sp15-gen-apnd-da", "spp-sppnorth-hub-spp-sppsouth-hub-rt", "caiso-th-sp15-gen-apnd-ercot-hb-hubavg-da", "ercot-hb-hubavg-spp-sppnorth-hub-da"]) assert.ok(!ercot.has(id), id);
  // the search that failed: "spread" finds ERCOT's own and never names another grid's hub
  const found = p.pageFigures({ page: "board", find: "hub spread less" }, "ercot", "ERCOT").rows.map((r) => r.row);
  assert.ok(found.includes("ercot-hb-north-ercot-hb-houston-da"));
  assert.deepEqual(found.filter((id) => /(^|-)(caiso|miso|pjm|nyiso|isone|spp)-/.test(id)), []);
});

test("Supply and trade's rows for ERCOT leave out every other grid's row and the seven grids together", () => {
  const ids = p.supplyRows("ercot").map((r) => r.id);
  for (const id of ["cleared-ercot", "burn-ercot-natural-gas", "eia-nw2-epg0-swo-r48-bcf"]) assert.ok(ids.includes(id), id);
  for (const id of supply.rows.map((r) => r.id).filter((i) => /^(burn|cleared)-/.test(i) && !/^(burn|cleared)-ercot/.test(i))) assert.ok(!ids.includes(id), id);
  assert.ok(!ids.some((i) => /caiso|miso|pjm|nyiso|iso-ne|spp|burn-all/.test(i)));
});

test("a search returns the page's own figures for a row, with its date and its changes", () => {
  const out = p.pageFigures({ page: "board", find: "hub average day-ahead" }, "ercot", "ERCOT");
  assert.equal(out.table, "site/data/board.json");
  const row = out.rows.find((r) => r.row === "ercot-hb-hubavg-da");
  const held = board.rows.find((r) => r.id === "ercot-hb-hubavg-da");
  assert.equal(row.latest.date, held.last.t);
  assert.equal(row.latest.value, Math.round(held.last.v * 10000) / 10000);
  assert.equal(row.change_on_a_week_before.date, held.moves.w.t);
  assert.ok(out.rows.length <= 12);
  assert.ok(out.rows.every((r) => !/^(caiso|miso|pjm|nyiso|isone|spp)-/.test(r.row)));
  assert.ok(out.rows.every((r) => !/(^|-)(caiso|miso|pjm|nyiso|isone|spp)-/.test(r.row)));   // session 5264: nor as a spread's second hub
});

test("a row without a value is returned with its reason and no figure", () => {
  const out = p.pageFigures({ page: "board", find: "futures NYMEX" }, "ercot", "ERCOT");
  const blank = out.rows.filter((r) => r.status !== "ok");
  assert.ok(blank.length >= 1);
  assert.ok(blank.every((r) => !("latest" in r) && typeof r.note === "string" && r.note.length > 10));
});

test("a series is the row's own recent points, date for date and value for value, and can be charted", () => {
  const out = p.pageFigures({ page: "supply", series: "cleared-ercot" }, "ercot", "ERCOT");
  const held = supply.rows.find((r) => r.id === "cleared-ercot");
  assert.equal(out.group_by, "day");
  assert.deepEqual(out.result.map((r) => r.day), held.spark.t);
  assert.deepEqual(out.result.map((r) => r.value), held.spark.v.map((v) => Math.round(v * 10000) / 10000));
  const b = p.pageFigures({ page: "board", series: "eia-henry-hub-spot" }, "ercot", "ERCOT");
  const hh = board.rows.find((r) => r.id === "eia-henry-hub-spot");
  assert.equal(b.result.length, hh.spark.v.length);
  assert.equal(b.result.at(-1).day, hh.last.t);
  assert.deepEqual(b.units, [hh.unit]);
});

test("another grid's row cannot be asked for by its id", () => {
  for (const id of ["caiso-th-np15-gen-apnd-da", "cleared-caiso", "burn-pjm-natural-gas", "cleared-spp"]) {
    const page = id.startsWith("caiso-th") ? "board" : "supply";
    const out = p.pageFigures({ page, series: id }, "ercot", "ERCOT");
    assert.ok(typeof out.error === "string" && out.error.includes("no row"), id);
  }
  assert.ok("error" in p.pageFigures({ page: "mix" }, "ercot", "ERCOT"));
});

test("the addendum states the four forms, carries the page's written content and says what is refused", () => {
  const a = p.addendum("ercot", "ERCOT");
  for (const words of ['form "words"', 'form "sentence"', 'form "chart"', 'form "table"', "Call no tool", "a single figure is never charted", "Never add a series for its own sake",
    "docs/grids/ercot.md", "How its market sets prices", "A short history", "Glossary", "This panel answers for ERCOT only", "/grid/<slug>", "Licensed data", "What a named company earned", "A forecast", "do not answer from memory"])
    assert.ok(a.includes(words), words);
  assert.ok(!a.includes(String.fromCharCode(0x2014)));
  assert.deepEqual([...p.FORMS], ["words", "sentence", "chart", "table"]);
});

test("the rule that judges the 100 questions: one example of a pass and a fail for each kind", () => {
  const cite = [{ table: "docs/grids/ercot.md" }], t = [{ table: "ercot_hub_prices_daily" }];
  const s = [{ rows: [1, 2, 3].map((k) => ({ key: String(k), value: k })), check: { same: true } }];
  const long = "word ".repeat(20);
  assert.deepEqual(judge({ kind: "conceptual" }, { status: "answered", answer: long, citations: cite, series: [] }), []);
  assert.ok(judge({ kind: "conceptual" }, { status: "answered", answer: long, citations: cite, series: s }).length === 1);
  assert.deepEqual(judge({ kind: "chart" }, { status: "answered", answer: long, citations: t, series: s }), []);
  assert.ok(judge({ kind: "chart" }, { status: "answered", answer: long, citations: t, series: [{ ...s[0], check: { same: false } }] }).length === 1);
  assert.deepEqual(judge({ kind: "sentence" }, { status: "answered", answer: "It was 37.28 USD/MWh on 4 October.", citations: t, series: [] }), []);
  assert.ok(judge({ kind: "sentence" }, { status: "answered", answer: "It was 37.28 USD/MWh.", citations: t, series: s }).length === 1);
  assert.deepEqual(judge({ kind: "refuse", say: "PJM" }, { status: "not_in_warehouse", answer: "This panel answers for ERCOT only; PJM has its own page.", series: [] }), []);
  assert.ok(judge({ kind: "refuse", say: "PJM" }, { status: "answered", answer: "PJM was 40.", series: [] }).length === 1);
});

console.log(`${n} tests pass`);
