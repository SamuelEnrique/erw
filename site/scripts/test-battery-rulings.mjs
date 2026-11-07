// Energy Research Warehouse (ERW) site, session 3600: the battery game against the owner's rulings of 14 October 2026
// and Kelsey's asks of 5 October, one test block per ruling.
//
//   node --test scripts/test-battery-rulings.mjs      (from site/; tests/test_session3600.py runs it)
//
// Node 23.6 or later runs lib/battery.ts as it is. No network, no model, no site build.
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {
  ADDONS, DEFAULT_SETTINGS, DIFFICULTIES, EMERGENCY, emergencyOf, glance, gridDownWords, noBattery, optimum, priceHover, rulesOf, simulate,
  START_MONEY, tally, validAddons, validSolar, vppHour,
} from "../lib/battery.ts";

const near = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) < eps, `${a} is not ${b}`);
const levels = JSON.parse(fs.readFileSync(new URL("../data/battery_levels.json", import.meta.url), "utf-8")).levels;
const game = fs.readFileSync(new URL("../app/play/battery/Game.tsx", import.meta.url), "utf-8");

test("ruling 1: Easy shows the whole day's real prices ahead as its forecast; Normal and Hard show none", () => {
  for (const l of levels) assert.ok(DIFFICULTIES.easy.forecastHours * 4 >= l.price.length, `${l.slug}: Easy's forecast covers the day`);
  assert.equal(DIFFICULTIES.normal.forecastHours, 0);
  assert.equal(DIFFICULTIES.hard.forecastHours, 0);
});

test("ruling 2: the day at a glance, the average and the spread, worked by hand", () => {
  // 10, 20, 30, 40: mean 25; squared deviations 225, 25, 25, 225, mean 125; sd = sqrt(125) = 11.18034
  const g = glance([10, 20, 30, 40]);
  near(g.avg, 25); near(g.sd, Math.sqrt(125)); assert.equal(g.lo, 10); assert.equal(g.hi, 40); assert.equal(g.n, 4);
  near(g.typicalLo, 25 - Math.sqrt(125)); near(g.typicalHi, 25 + Math.sqrt(125));
  // a flat day has no spread; the typical range never leaves the day's own lowest and highest
  const flat = glance([40, 40, 40]);
  assert.equal(flat.sd, 0); assert.equal(flat.typicalLo, 40); assert.equal(flat.typicalHi, 40);
  const skew = glance([0, 0, 0, 100]);   // mean 25, sd 43.30: 25 - 43.30 is below the lowest, so the range starts at 0
  assert.equal(skew.typicalLo, 0);
  assert.equal(glance([]), null);
  assert.equal(glance([1, Number.NaN]), null);
  for (const l of levels) { const x = glance(l.price); assert.ok(x && x.lo <= x.typicalLo && x.typicalLo <= x.avg && x.avg <= x.typicalHi && x.typicalHi <= x.hi, l.slug); }
  // the preview is shown before play in every mode (the phase "preview" sits between Start and the play, for each mode)
  assert.ok(game.includes('setPhase("preview")') && game.includes("<Preview level={level}"), "the preview phase");
  assert.ok(game.includes("const gl = glance(level.price)"), "the preview reads glance()");
  assert.ok(game.includes("data-glance-spread"), "the spread shown in the preview");
});

test("ruling 3: the perfect battery on a hand-worked day, and the end table's three rows", () => {
  // A toy battery: 2 kWh, 1 kWh an interval (4 kW for 15 minutes), lossless, half full (1 kWh), $5, no reserve or wear.
  // Two hours of prices, USD/MWh. The fleet call is the dearest hour: hour 1, mean (-10 + 30 + 300 + 50) / 4 = 92.5,
  // a bonus of 92.5 on each MWh delivered in it.
  const r = { kwh: 2, kw: 4, eta: 1, reserveKwh: 0, deg: 0, start: 1, minutes: 15, money0: 5, emergency: false, houseKw: 1.5, voll: 35000, solarKw: 0 };
  const p = [-10, 30, 300, 50, 20, 10, 100, 40];
  assert.deepEqual(vppHour(p), { first: 0, last: 3, price: 92.5 });
  // By hand (USD/MWh x kWh, then / 1,000): charge at -10 (paid 10; full); hold at 30 (full); sell at 300 + 92.5 = 392.5;
  // sell at 50 + 92.5 = 142.5 (empty); charge at 20 and 10 (-30); sell at 100 and 40 (+140).
  // 10 + 392.5 + 142.5 - 30 + 140 = 655, so USD 0.655: cash 0.470 (10 + 300 + 50 - 20 - 10 + 100 + 40) and the bonus
  // 0.185 (2 kWh x 92.5). The rivals by hand: selling at 30 + 92.5 = 122.5 instead of 50 + 92.5 ends hour 1 at 525,
  // not 545; idling at -10 and charging at 30 ends it at 505; keeping 1 kWh past hour 1 (holding at 50) ends the day at
  // 10 + 392.5 - 10 + 140 = 532.5.
  const o = optimum(p, r);
  near(o.score, 0.655);
  const s = simulate(p, o.actions, r);
  near(s.score, 0.655); near(s.cash, 0.47); near(s.bonus, 0.185);
  assert.deepEqual(s.soc, [1, 2, 2, 1, 0, 1, 2, 1, 0]);
  // brute force over all 3^8 plays agrees
  let best = -Infinity;
  for (let c = 0; c < 3 ** 8; c++) {
    const a = []; let k = c;
    for (let i = 0; i < 8; i++) { a.push([1, 0, -1][k % 3]); k = Math.floor(k / 3); }
    best = Math.max(best, simulate(p, a, r).score);
  }
  near(best, 0.655);
  // the end table: bought 3 kWh at an average of 20 / 3, sold 4 kWh at 122.5; no battery earns nothing
  const t = tally(p, o.actions, r);
  near(t.boughtKwh, 3); near(t.soldKwh, 4); near(t.buyPrice, 20 / 3); near(t.sellPrice, 122.5);
  assert.equal(noBattery(p, r), 0);
  assert.ok(game.includes('[["You", mine, mine.score], ["The perfect battery", perfect, perfect.score], ["No battery", null, none]]'), "three rows");
  const done = game.slice(game.indexOf('{phase === "done" && result ? ('));
  assert.ok(done.indexOf("<EndTable") >= 0 && !/\{!easy \? <EndTable/.test(done), "the end table in every mode");
});

test("ruling 4: $5 to start, the game over below $0, and Hard's one grid-constrained moment said plainly", () => {
  assert.equal(START_MONEY, 5);
  // one charge interval buys 5 kW x 15 minutes = 1.25 kWh at the meter: at 4,100 USD/MWh that is $5.125, below $0
  const broke = simulate([4100, 10, 10, 10], [1, 0, 0, 0], rulesOf());
  assert.equal(broke.why, "bankrupt"); assert.equal(broke.end, 0); near(broke.money, 5 - 5.125);
  // at exactly 4,000 it is $5.00: the money is $0, not below it, so the game goes on
  const zero = simulate([4000, 10, 10, 10], [1, 0, 0, 0], rulesOf());
  assert.equal(zero.why, ""); assert.equal(zero.end, null);
  const ok = simulate([3000, 10, 10, 10], [1, 0, 0, 0], rulesOf());   // $3.75: still in the game
  assert.equal(ok.why, ""); assert.equal(ok.end, null);
  for (const l of levels) {
    for (const d of ["easy", "normal"]) assert.equal(emergencyOf(l.price, rulesOf(DEFAULT_SETTINGS, d)).outage, null, `${l.slug}, ${d}: no constraint`);
    const hard = rulesOf(DEFAULT_SETTINGS, "hard");
    const em = emergencyOf(l.price, hard);
    assert.ok(em.outage, `${l.slug}: Hard has the window`);
    assert.equal(em.outage.first, em.spike.last + 1);
    assert.ok(em.outage.last - em.outage.first + 1 <= EMERGENCY.outageIntervals);
    // in the window the battery cannot discharge to the grid: a sell there earns exactly what holding earns
    const idle = new Array(l.price.length).fill(0);
    const sell = idle.map((_, i) => (i >= em.outage.first && i <= em.outage.last ? -1 : 0));
    const a = simulate(l.price, idle, hard), b = simulate(l.price, sell, hard);
    near(a.score, b.score); assert.deepEqual(a.soc, b.soc);
  }
  const words = gridDownWords("19:00", "21:00");
  assert.equal(words, "The grid is down from 19:00 to 21:00: your battery cannot sell (discharge to the grid) or buy until it is back. It runs your house instead.");
  assert.ok(game.includes("gridDownWords("), "the page shows the words while the window lasts");
});

test("ruling 5: rooftop solar, on Hard only, off by default, its shape from EIA-930 over EIA-860M", () => {
  assert.equal(DIFFICULTIES.hard.addons, true);
  assert.equal(DIFFICULTIES.easy.addons, false); assert.equal(DIFFICULTIES.normal.addons, false);
  assert.equal(validAddons(["solar"], "easy"), false); assert.equal(validAddons(["solar"], "normal"), false); assert.equal(validAddons(["solar"], "hard"), true);
  assert.equal(rulesOf(DEFAULT_SETTINGS, "hard").solarKw, 0, "off by default");
  assert.equal(rulesOf(DEFAULT_SETTINGS, "easy", ["solar"]).solarKw, 0, "never on Easy");
  assert.ok(game.includes("useState<AddonKey[]>([])"), "the page starts with no add-on on");
  assert.ok("solar" in ADDONS);
  for (const l of levels) {
    assert.ok(validSolar(l.solar, l.price.length), `${l.slug}: a whole solar shape`);
    assert.match(l.solar_source, /EIA-930 hourly generation by fuel/);
    assert.match(l.solar_source, /EIA-860M/);
  }
});

test("the owner's rule: every shown price is a real stored price, its source a hover", () => {
  const h = priceHover("ERCOT real-time, hub average (HB_HUBAVG)", { date: "2026-04-26", table: "ercot_all_hub_prices_history", source: ["ercot:NP6-785-ER"], retrieved_at: "2026-09-26T00:36:19Z" });
  assert.equal(h, "Real prices: ERCOT real-time, hub average (HB_HUBAVG), 2026-04-26, USD per MWh, every 15 minutes. Source: ercot:NP6-785-ER, retrieved 2026-09-26T00:36:19Z. ERW table: ercot_all_hub_prices_history.");
  // a field the level does not hold is left out, never invented
  assert.equal(priceHover("x", { date: "2026-01-01" }), "Real prices: x, 2026-01-01, USD per MWh, every 15 minutes.");
  for (const l of levels) {
    assert.ok(l.table && l.source.length && l.retrieved_at, `${l.slug}: its table, source and retrieval are stored`);
    assert.ok(l.price.every((v) => Number.isFinite(v)), `${l.slug}: every price a number`);
  }
  assert.ok(game.includes("title={hover}") && game.includes("priceHover("), "the price now and the preview carry the hover");
});
