// Energy Research Warehouse (ERW) site, session 1406 (chain 100): the Lower 48 on the Network tab, lib/gridKeys.ts
// lower48Demand, on the committed snapshot (data/grid_network.json) and real rows: the seven grids' demand of the week
// (fixtures/grid_balance.json, session 1165) and EIA-930's Lower 48 over the same week (fixtures/lower48_demand.json),
// aligned as the page aligns them (alignHours, app/network/data.ts liveExtras). Every key the block writes is recomputed
// as scripts/check-values.mjs recomputes it: a net| operand by lib/network.ts netValue on the snapshot, a series| operand
// from the rows, a calc| key by scripts/check-calc.mjs over its operands. The seven's demand is the grid in view's own
// figure (demandAt, as networkPanel draws it); the exchange's parts add up; no figure the Lower 48's table draws moves
// (lower48Panel's keys and values are those of before). Needs no build, no network and no node_modules.
//
//   node scripts/test-grid-lower48.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as K from "../lib/gridKeys.ts";
import * as N from "../lib/network.ts";
import * as V3 from "../lib/networkV3.ts";
import * as T from "../lib/gridtool.ts";
import * as CALC from "./check-calc.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const snap = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "grid_network.json"), "utf-8"));
const bal = JSON.parse(fs.readFileSync(path.join(here, "fixtures", "grid_balance.json"), "utf-8"));
const l48 = JSON.parse(fs.readFileSync(path.join(here, "fixtures", "lower48_demand.json"), "utf-8"));
const SEVEN = T.GRID_CHOICES.filter((g) => g.slug !== "us48").map((g) => g.ba);
const hour = K.shownHour(snap, V3.completeHour(snap.hours, snap.links));
let n = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };

// the week's demand by BA, as liveExtras gives it: the snapshot's hours, an hour held by one row
assert.equal(bal.snapshot_built, snap.built, "the balance fixture is of the committed snapshot");
assert.equal(l48.snapshot_built, snap.built, "the Lower 48's fixture is of the committed snapshot");
const week = Object.fromEntries(Object.entries(bal.demand).map(([ba, rows]) => [ba, K.alignHours(rows, snap.hours)]));
week.US48 = K.alignHours(l48.rows, snap.hours);
const rowsOf = (entity) => (entity === "eia930:US48" ? l48.rows : bal.demand[entity.slice(7)]);

/** A key's value as check-values recomputes it, on the snapshot and the fixtures' rows. */
function truth(key) {
  const p = key.split("|");
  if (p[0] === "net") return N.netValue(snap, key);
  if (p[0] === "series" && p[1] === "eia930_all_demand" && p[3] === "demand_mw") {
    const r = rowsOf(p[2]).filter(([ts]) => Date.parse(ts) === Date.parse(p[4]));
    return r.length === 1 ? Number(r[0][1]) : undefined;
  }
  if (p[0] === "netsnap") { const nd = snap.nodes.find((x) => x.id === p[1]); return nd?.demand_recent?.[p[3]]; }
  if (p[0] === "calc") return CALC.calcOf(p[1], CALC.calcOperands(p.slice(2)).map((k) => Number(truth(k))));
  return undefined;
}
const close = (a, b) => Math.abs(a - b) < 1e-9 * Math.max(1, Math.abs(a));
const d = K.lower48Demand(snap, SEVEN, hour, week);
const all = [...d.rows.map((r) => r.demand), d.us48, d.sum, d.share, d.total, d.rest, d.abroad].filter(Boolean);

test("the hour is the panel's, and every grid of the seven and the Lower 48 hold a demand in it", () => {
  assert.equal(d.hour, hour);
  assert.equal(hour, "2026-10-21T23:00:00Z");
  assert.deepEqual(d.rows.map((r) => r.ba), SEVEN);
  for (const r of d.rows) assert.ok(r.demand, `${r.ba} holds a demand`);
  assert.ok(d.us48 && d.sum && d.share, "the Lower 48's demand, the sum and the share are drawn");
  assert.equal(d.us48.check, `series|eia930_all_demand|eia930:US48|demand_mw|${hour}`);
  assert.equal(d.us48.raw, 497563);
});

test("each grid's demand is the grid in view's own figure, its key chosen the same way (demandAt, networkPanel)", () => {
  for (const r of d.rows) {
    const p = K.networkPanel(snap, r.ba, hour, week[r.ba]);
    assert.deepEqual(r.demand, p.demand, r.ba);
    assert.ok(/^(netsnap\||series\|eia930_all_demand\|)/.test(r.demand.check), r.demand.check);
  }
});

test("every key recomputes to the block's value (check-values' rules: netValue, the rows, check-calc)", () => {
  for (const f of all) {
    const t = truth(f.check);
    assert.ok(t !== undefined && close(t, f.raw), `${f.check.slice(0, 80)}...: ${t} against ${f.raw}`);
    assert.ok(f.tip && !f.tip.includes(String.fromCharCode(0x2014)), `${f.check.slice(0, 60)}: a tip without an em dash`);
  }
  assert.equal(all.length, 13);
});

test("the sum and the share: calc|add of the seven keys, calc|addpct with the Lower 48's last", () => {
  const ks = d.rows.map((r) => r.demand.check.replaceAll("|", "~"));
  assert.equal(d.sum.check, `calc|add|${ks.join("|")}`);
  assert.equal(d.share.check, `calc|addpct|${ks.join("|")}|${d.us48.check.replaceAll("|", "~")}`);
  const s = d.rows.reduce((a, r) => a + r.demand.raw, 0);
  assert.equal(d.sum.raw, s);
  assert.equal(d.share.raw, (s / d.us48.raw) * 100);
  assert.ok(d.share.raw > 0 && d.share.raw < 100, `the seven are part of the Lower 48: ${d.share.raw}`);
});

test("the exchange: the seven's net exports summed, split into the rest of the Lower 48 and Canada's and Mexico's operators", () => {
  const net = K.lower48Panel(snap, SEVEN, hour).filter((g) => g.net).map((g) => g.net.raw);
  const signed = (f) => (f.kind === "export" ? f.raw : -f.raw);
  assert.equal(d.reporting.length, 7);
  assert.ok(close(signed(d.total), net.reduce((a, v) => a + v, 0)), "the total is the sum of the table's net exports");
  assert.ok(close(signed(d.rest) + signed(d.abroad), signed(d.total)), "its two parts add up to it");
  // the ties among the seven cancel: the total is what crosses to a grid outside them
  let outside = 0;
  for (const ba of SEVEN) for (const t of K.tiesOf(snap, ba, hour)) if (!SEVEN.includes(t.other)) outside += t.mw;
  assert.ok(close(signed(d.total), outside), "the total is the ties to grids outside the seven");
  let abroad = 0;
  for (const ba of SEVEN) for (const t of K.tiesOf(snap, ba, hour)) if (K.OUTSIDE_US48.includes(t.other)) abroad += t.mw;
  assert.ok(close(signed(d.abroad), abroad), "Canada's and Mexico's part is the ties to their operators");
  // each part is keyed by the operands that give its size: a sent figure by net|export and the outside side's ties, a
  // taken one by net|import and the seven's side
  for (const f of [d.total, d.rest, d.abroad]) {
    assert.ok(f.raw >= 0, `${f.kind}: a size, its direction in words`);
    const ops = f.check.startsWith("calc|add|") ? CALC.calcOperands(f.check.split("|").slice(2)) : [f.check];
    for (const k of ops) assert.ok(/^net\|(export|import|tie)\|/.test(k), k);
    if (f !== d.abroad) assert.ok(ops.some((k) => k.startsWith(f.kind === "export" ? "net|export|" : "net|import|")), f.check.slice(0, 80));
  }
  for (const id of K.OUTSIDE_US48) assert.ok(snap.nodes.some((x) => x.id === id), `${id} is a node of the snapshot`);
});

test("no figure that stands moves: the Lower 48's table of net exchange keeps its keys and values", () => {
  const rows = K.lower48Panel(snap, SEVEN, hour);
  for (const r of rows) {
    if (r.net) assert.equal(N.netValue(snap, r.net.check), r.net.raw, r.net.check);
    assert.equal(N.netValue(snap, r.count.check), r.count.raw, r.count.check);
  }
  assert.equal(rows.flatMap((r) => [r.net, r.count]).filter(Boolean).length, 14);
});

test("not held, and a failed read: no Lower 48 demand, no share; a grid without demand, no sum", () => {
  const noUs = K.lower48Demand(snap, SEVEN, hour, { ...week, US48: undefined });
  assert.equal(noUs.us48, null);
  assert.equal(noUs.share, null);
  assert.deepEqual(noUs.sum, d.sum, "the sum stands without the Lower 48's demand");
  // the week's read failed: each grid's demand the snapshot holds for the hour still stands (session 1181), with its key
  const none = K.lower48Demand(snap, SEVEN, hour, {});
  assert.equal(none.us48, null);
  for (const r of none.rows) {
    const p = K.networkPanel(snap, r.ba, hour, undefined);
    assert.deepEqual(r.demand, p.demand, r.ba);
  }
  const some = K.lower48Demand(snap, SEVEN, hour, { ...week, ERCO: snap.hours.map(() => null) });
  if (!some.rows.find((r) => r.ba === "ERCO").demand) { assert.equal(some.sum, null); assert.equal(some.share, null); }
  assert.deepEqual(some.total, d.total, "the exchange does not read demand");
});

test("calc's add and addpct (scripts/check-calc.mjs): any count from the least, left to right; else no value", () => {
  assert.equal(CALC.calcOf("add", [1, 2]), 3);
  assert.equal(CALC.calcOf("add", [1, 2, 3, 4]), 10);
  assert.equal(CALC.calcOf("addpct", [1, 1, 8]), 25);
  assert.equal(CALC.calcOf("add", [1]), undefined);
  assert.equal(CALC.calcOf("addpct", [1, 4]), undefined);
  assert.equal(CALC.calcOf("add", [1, NaN]), undefined);
  assert.equal(CALC.calcOf("sum", [1, 2]), undefined, "session 1165's assertion: sum is not an op");
  assert.equal(CALC.calcOf("pct", [1, 4]), 25, "the two-operand ops as before");
});

console.log(`every test holds (${n} tests)`);
