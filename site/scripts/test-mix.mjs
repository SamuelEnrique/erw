// Energy Research Warehouse (ERW) site, session 133: the one energy mix page's address and helpers (lib/mixpage.ts).
//
//   node --import ./scripts/alias-register.mjs scripts/test-mix.mjs
//
// Exit 1 on a failure. Nothing is written.
import assert from "node:assert/strict";
import * as m from "../lib/mixpage.ts";

let n = 0;
const test = (name, fn) => { fn(); n += 1; console.log(`ok   ${name}`); };

test("an address with nothing chosen is the original page: now and by state", () => {
  const c = m.choiceOf({});
  assert.deepEqual([c.view, c.grids, c.norm, c.factor, c.season, c.src, c.states], ["now", ["ercot"], "mw", "none", "all", "wind", ["US"]]);
  assert.equal(m.hrefOf(c), "/mix");
  assert.equal(m.hrefOf(m.choiceOf({ ba: "erco", state: "TX" })), "/mix?ba=erco&state=TX");
});
test("up to four grids, in the order chosen; an unknown grid is dropped", () => {
  const c = m.choiceOf({ view: "day", grids: "caiso,ercot,nowhere,pjm,miso,spp" });
  assert.deepEqual(c.grids, ["caiso", "ercot", "pjm", "miso"]);
  assert.equal(m.MAX_GRIDS, 4);
  assert.deepEqual(m.toggled(["ercot"], "ercot"), ["ercot"]);                     // the last grid stays
  assert.deepEqual(m.toggled(["ercot", "caiso"], "ercot"), ["caiso"]);
  assert.deepEqual(m.toggled(["a", "b", "c", "d"], "e"), ["a", "b", "c", "d"]);   // a fifth is not added
  assert.deepEqual(m.toggled(["a"], "b"), ["a", "b"]);
});
test("the address of a retired page opens the same grids in its view", () => {
  // /mix/v2?grid=caiso&vs=ercot&period=2026-04 redirects to /mix?view=day&grid=caiso&vs=ercot&period=2026-04
  const c = m.choiceOf({ view: "day", grid: "caiso", vs: "ercot", period: "2026-04" });
  assert.deepEqual([c.grids, c.period], [["caiso", "ercot"], "2026-04"]);
  assert.equal(m.hrefOf(c), "/mix?view=day&grids=caiso%2Cercot&period=2026-04");
  assert.deepEqual(m.choiceOf({ view: "clean", grid: "nyiso", year: "2024" }).grids, ["nyiso"]);
});
test("a choice and its address go round", () => {
  for (const q of [{ view: "day", grids: "ercot,caiso", period: "2025", norm: "peak", factor: "price" }, { view: "duck", grids: "caiso", cal: "07", factor: "carbon" },
    { view: "supply", grids: "pjm,miso", year: "2022", season: "summer" }, { view: "forecast", src: "solar" }, { view: "history", states: "TX,CA", norm: "peak" }, { view: "stress", year: "2021" }]) {
    const c = m.choiceOf(q);
    const back = m.choiceOf(Object.fromEntries(new URLSearchParams(m.hrefOf(c).split("?")[1] ?? "")));
    assert.deepEqual(back, c);
  }
});
test("what a view does not use is not written to its address", () => {
  const c = m.choiceOf({ view: "day", grids: "caiso", period: "2025-06", factor: "price", norm: "peak" });
  assert.equal(m.hrefOf(c, { view: "clean" }), "/mix?view=clean&grids=caiso");
  assert.equal(m.hrefOf(c, { view: "forecast" }), "/mix?view=forecast");
  assert.equal(m.hrefOf(c, { view: "now" }), "/mix");
});
test("bad values fall back", () => {
  const c = m.choiceOf({ view: "nonsense", period: "April", cal: "44", year: "20x6", factor: "gold", season: "monsoon", states: "tx,ZZ1" });
  assert.deepEqual([c.view, c.period, c.cal, c.year, c.factor, c.season, c.states], ["now", null, null, null, "none", "all", ["US"]]);
});
test("share of peak: a value over the peak, a blank stays a blank", () => {
  assert.equal(m.peakOf([10, null, 40, 25]), 40);
  assert.equal(m.peakOf([null, null]), null);
  assert.deepEqual(m.ofPeak([10, null, 40], 40), [25, null, 100]);
  assert.deepEqual(m.ofPeak([10, 20], null), [null, null]);
});
test("nine views, the first the original; six factors; five seasons", () => {
  assert.equal(m.VIEWS.length, 9);
  assert.equal(m.VIEWS[0][0], "now");
  assert.deepEqual(m.FACTORS.map((f) => f[0]), ["none", "price", "demand", "temperature", "carbon", "imports"]);
  assert.deepEqual(m.SEASON_NAMES.map((s) => s[0]), ["all", "winter", "spring", "summer", "autumn"]);
  assert.equal(m.HOURS.length, 24);
});
console.log(`${n} tests pass`);
