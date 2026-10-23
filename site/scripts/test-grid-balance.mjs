// Energy Research Warehouse (ERW) site, session 1165 (chain 078): the Network tab's balance (lib/gridKeys.ts
// balancePanel, netbalValue) and the arithmetic of check-values' calc| keys (scripts/check-calc.mjs), with check-methods'
// reading of a three-operand calc key. The fixture, scripts/fixtures/grid_balance.json, is the committed snapshot's week
// (its hours and the seven ISO grids' links, as built at its `snapshot_built`) and the seven grids' rows of
// eia930_all_generation and eia930_all_demand in that week, read once from Supabase with the anon key (its `read_at`).
// The current data/grid_network.json is read too, for the case where the week's generation is not held. Needs no
// build, no network and no node_modules.
//
//   node scripts/test-grid-balance.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as K from "../lib/gridKeys.ts";
import * as N from "../lib/network.ts";
import * as V3 from "../lib/networkV3.ts";
import * as CALC from "./check-calc.mjs";
import { figures } from "./check-methods.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const fx = JSON.parse(fs.readFileSync(path.join(here, "fixtures", "grid_balance.json"), "utf-8"));
const committed = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "grid_network.json"), "utf-8"));
const ISOS = ["CISO", "ERCO", "ISNE", "MISO", "NYIS", "PJM", "SWPP"];
const snap = { built: fx.snapshot_built, window: [fx.hours[0], fx.hours[fx.hours.length - 1]], hours: fx.hours, rule: "", nodes: [], links: fx.links };
const hour = K.shownHour(snap, V3.completeHour(snap.hours, snap.links));
const norm = (t) => new Date(t).toISOString().replace(".000Z", "Z");
/** a series| key's value in the fixture's rows, as check-values' series query returns it (the row at that time) */
const seriesValue = (key) => {
  const [, table, entity, , ts] = key.split("|");
  const rows = table === "eia930_all_generation" ? fx.generation : table === "eia930_all_demand" ? fx.demand : null;
  return rows?.[entity.replace("eia930:", "")]?.find(([t]) => norm(t) === ts)?.[1];
};
const truth = (key) => (key.startsWith("net|") ? N.netValue(snap, key) : key.startsWith("series|") ? seriesValue(key) : undefined);
const demandFig = (ba, i) => {
  const v = K.alignHours(fx.demand[ba], fx.hours)[i];
  return v === null ? null : { check: `series|eia930_all_demand|eia930:${ba}|demand_mw|${fx.hours[i]}`, raw: v, tip: "" };
};
const panelOf = (ba, h = hour) => K.balancePanel(snap, ba, h, K.alignHours(fx.generation[ba], fx.hours), K.alignHours(fx.demand[ba], fx.hours), demandFig(ba, fx.hours.indexOf(h)));
let n = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };

test("calc: ratio, diff and pct compute as before; bal is A less B less C", () => {
  assert.equal(CALC.calcOf("ratio", [6, 4]), 1.5);
  assert.equal(CALC.calcOf("diff", [6, 4]), 2);
  assert.equal(CALC.calcOf("pct", [1, 4]), 25);
  assert.equal(CALC.calcOf("bal", [23109, 27289, -4046]), 23109 - 27289 - -4046);
  assert.equal(CALC.calcOf("bal", [10, 3, 2]), 5);
});

test("calc: an unknown op, a wrong count of operands or a value not finite has no value", () => {
  assert.equal(CALC.calcOf("sum", [1, 2]), undefined);
  assert.equal(CALC.calcOf("pct", [1, 2, 3]), undefined);
  assert.equal(CALC.calcOf("bal", [1, 2]), undefined);
  assert.equal(CALC.calcOf("diff", [1, NaN]), undefined);
  assert.equal(CALC.calcOf("bal", [1, 2, Infinity]), undefined);
  assert.deepEqual(CALC.calcOperands(["net~export~PJM~2026-10-20T00:00:00Z", "a~b"]), ["net|export|PJM|2026-10-20T00:00:00Z", "a|b"]);
});

test("check-methods reads calc|bal as its three figures, a two-operand calc as its two", () => {
  const p = K.balancePanel(snap, "PJM", hour, K.alignHours(fx.generation.PJM, fx.hours), K.alignHours(fx.demand.PJM, fx.hours), demandFig("PJM", fx.hours.indexOf(hour)));
  const ids = figures(p.gap.check).map((f) => f.id);
  assert.equal(ids.length, 3);
  assert.ok(ids.includes("eia930_all_generation net_generation_mw") && ids.includes("eia930_all_demand demand_mw"), ids.join("; "));
  assert.equal(figures("calc|pct|net~import~PJM~2026-10-20T00:00:00Z|series~eia930_all_generation~eia930:PJM~net_generation_mw~2026-10-20T00:00:00Z").length, 2);
});

test("alignHours aligns as the page does: one row an hour, rounded to 0.1, '+00:00' read as UTC", () => {
  const hours = ["2026-10-15T00:00:00Z", "2026-10-15T01:00:00Z", "2026-10-15T02:00:00Z"];
  assert.deepEqual(K.alignHours([["2026-10-15T00:00:00+00:00", 10.04], ["2026-10-15T01:00:00Z", 5], ["2026-10-15T01:00:00Z", 7]], hours), [10, null, null]);
  assert.deepEqual(K.alignHours([{ ts_utc: "2026-10-15T02:00:00+00:00", value: 3.26 }], hours), [null, null, 3.3]);
});

test("each grid's gap in the hour shown is net generation less demand less net export, and recomputes from its three keys", () => {
  for (const ba of ISOS) {
    const p = panelOf(ba);
    assert.ok(p.gen && p.demand && p.net && p.gap, `${ba}: all four held in ${hour}`);
    assert.equal(p.gap.raw, p.gen.raw - p.demand.raw - p.net.raw, ba);
    assert.ok(p.gap.check.startsWith("calc|bal|"), p.gap.check);
    const [, op, ...parts] = p.gap.check.split("|");
    const ops = CALC.calcOperands(parts);
    assert.deepEqual(ops, [p.gen.check, p.demand.check, p.net.check]);
    const xs = ops.map((k) => Number(truth(k)));
    assert.equal(CALC.calcOf(op, xs), p.gap.raw, `${ba}: check-values' recomputation of ${p.gap.check}`);
    assert.equal(N.netValue(snap, p.net.check), p.net.raw, `${ba}: net export`);
    assert.equal(p.net.check, `net|export|${ba}|${hour}`);
    assert.equal(seriesValue(p.gen.check), p.gen.raw, `${ba}: generation`);
  }
});

test("the week: the mean size of the gap and its hours, recomputed by netbalValue from the rows as check-values reads them", () => {
  for (const ba of ISOS) {
    const p = panelOf(ba);
    assert.ok(p.absmean && p.hours, ba);
    assert.equal(p.absmean.check, `netbal|absmean|${ba}|${fx.hours[0]}|${fx.hours[fx.hours.length - 1]}`);
    assert.equal(p.hours.check, `netbal|hours|${ba}|${fx.hours[0]}|${fx.hours[fx.hours.length - 1]}`);
    const rowsOf = (rs) => rs.map(([ts_utc, value]) => ({ ts_utc, value }));
    assert.equal(K.netbalValue(p.absmean.check, [snap], rowsOf(fx.generation[ba]), rowsOf(fx.demand[ba])), p.absmean.raw, `${ba} absmean`);
    assert.equal(K.netbalValue(p.hours.check, [snap], fx.generation[ba], fx.demand[ba]), p.hours.raw, `${ba} hours`);
    // by hand: every tie with a flow in the week, held in the hour, and both series held
    const ties = fx.links.filter((l) => (l.a === ba || l.b === ba) && l.mw.some((v) => v !== null));
    const g = K.alignHours(fx.generation[ba], fx.hours), d = K.alignHours(fx.demand[ba], fx.hours);
    const gaps = fx.hours.map((_, i) => (ties.every((l) => l.mw[i] !== null) && g[i] !== null && d[i] !== null
      ? g[i] - d[i] - ties.reduce((a, l) => a + (l.a === ba ? 1 : -1) * l.mw[i], 0) : null)).filter((x) => x !== null);
    assert.equal(p.hours.raw, gaps.length, `${ba}: hours by hand`);
    assert.ok(Math.abs(p.absmean.raw - gaps.reduce((a, x) => a + Math.abs(x), 0) / gaps.length) < 1e-9, `${ba}: mean by hand`);
  }
});

test("on this week the split of session 360 holds: ERCOT, NYISO and ISO-NE close, CAISO and MISO do not", () => {
  const m = Object.fromEntries(ISOS.map((ba) => [ba, panelOf(ba).absmean.raw]));
  for (const ba of ["ERCO", "NYIS", "ISNE"]) assert.ok(m[ba] < 5, `${ba} ${m[ba]}`);
  for (const ba of ["CISO", "MISO"]) assert.ok(m[ba] > 1000, `${ba} ${m[ba]}`);
  assert.ok(panelOf("CISO").hours.raw > 100);
});

test("netbalValue reads two snapshots, each hour from the first that holds it (the hourly one moved on, the committed one older)", () => {
  const cut = (lo, hi) => ({ ...snap, hours: fx.hours.slice(lo, hi), links: fx.links.map((l) => ({ ...l, mw: l.mw.slice(lo, hi) })) });
  const stored = cut(60, 168), older = cut(0, 100);
  for (const ba of ["CISO", "PJM", "SWPP"]) {
    const p = panelOf(ba);
    assert.equal(K.netbalValue(p.absmean.check, [stored, older], fx.generation[ba], fx.demand[ba]), p.absmean.raw, ba);
    assert.equal(K.netbalValue(p.hours.check, [stored, older], fx.generation[ba], fx.demand[ba]), p.hours.raw, ba);
    // neither holds the window's first hour: no value, never a value over other hours
    assert.equal(K.netbalValue(p.absmean.check, [stored], fx.generation[ba], fx.demand[ba]), undefined, ba);
  }
  assert.equal(K.netbalValue("netbal|median|PJM|a|b", [snap], [], []), undefined);
});

test("the tips name session 360's split in one line; the words of where each gap sits hold no figure", () => {
  const p = panelOf("CISO");
  for (const f of [p.gap, p.absmean, p.hours]) {
    assert.ok(f.tip.includes(K.BALANCE_SPLIT), f.check);
    assert.ok(!/\n/.test(f.tip), f.check);
  }
  assert.ok(!K.BALANCE_SPLIT.includes(String.fromCharCode(0x2014)));
  for (const ba of ISOS) {
    assert.ok(K.BALANCE_WHERE[ba], ba);
    assert.ok(!/\d/.test(K.BALANCE_WHERE[ba]), ba);
  }
  for (const name of ["CAISO", "MISO", "SPP", "PJM", "ERCOT", "NYISO", "ISO-NE"]) assert.ok(K.BALANCE_SPLIT.includes(name), name);
});

test("a part not held: no gap and no week (the committed snapshot without the week's generation)", () => {
  const h = K.shownHour(committed, V3.completeHour(committed.hours, committed.links));
  const p = K.balancePanel(committed, "PJM", h, undefined, undefined, null);
  assert.equal(p.gen, null);
  assert.equal(p.gap, null);
  assert.equal(p.absmean, null);
  assert.equal(p.hours, null);
  assert.equal(N.netValue(committed, p.net.check), p.net.raw, "the net export still recomputes");
});

test("the gravity shape's generation keys are unchanged by the move to generationAt", () => {
  const gen = Object.fromEntries(ISOS.map((ba) => [ba, K.alignHours(fx.generation[ba], fx.hours)]));
  const g = K.gravityPanel(snap, ISOS, "US48", hour, gen);
  for (const r of g.rows) {
    assert.equal(r.gen.check, `series|eia930_all_generation|eia930:${r.ba}|net_generation_mw|${hour}`);
    assert.deepEqual(r.gen, K.generationAt(snap, r.ba, hour, gen[r.ba]));
    assert.equal(r.gen.raw, panelOf(r.ba).gen.raw);
  }
  assert.equal(g.center, null);
});

console.log(`${n} tests passed`);
