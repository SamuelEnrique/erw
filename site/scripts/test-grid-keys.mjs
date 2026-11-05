// Energy Research Warehouse (ERW) site, session 1151 (chain 077): lib/gridKeys.ts, the keyed figures under the Grid
// tool's network component and the Clean tab's last 24 hours. On the committed snapshot (data/grid_network.json) as the
// fixture: every net| key the panels write is recomputed by lib/network.ts netValue (what scripts/check-values.mjs runs)
// to the panel's own value; the gravity panel's net import is the shape's own (lib/networkGravity.ts netImportAt); the
// hour is the component's (lib/networkV3.ts completeHour); the demand key is chosen as the component chooses it. Needs
// no build, no network and no node_modules.
//
//   node scripts/test-grid-keys.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as K from "../lib/gridKeys.ts";
import * as N from "../lib/network.ts";
import * as V3 from "../lib/networkV3.ts";
import * as G from "../lib/networkGravity.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const snap = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "grid_network.json"), "utf-8"));
const ISOS = ["ERCO", "CISO", "PJM", "MISO", "NYIS", "ISNE", "SWPP"];
let n = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };
const complete = V3.completeHour(snap.hours, snap.links);
const hour = K.shownHour(snap, complete);

test("the hour is the one the component opens on", () => {
  const open = complete.index >= 0 ? complete.index : snap.hours.length - 1;
  assert.equal(hour, snap.hours[open]);
});

test("each grid's panel: every key recomputes to the panel's value (ties, net, count)", () => {
  let keys = 0;
  for (const ba of ISOS) {
    const p = K.networkPanel(snap, ba, hour);
    for (const f of [...p.ties, p.count, ...(p.net ? [p.net] : [])]) {
      assert.equal(N.netValue(snap, f.check), f.raw, f.check);
      assert.ok(!Object.is(f.raw, -0), `${f.check} is never -0`);
      assert.ok(f.tip.includes("eia930_all_interchange") && f.tip.includes(snap.built.slice(0, 16).replace("T", " ")), `${f.check}: the tip names the table and the refresh`);
      keys += 1;
    }
    assert.equal(p.count.raw, p.ties.length);
    assert.equal(p.count.raw, N.tiesAt(snap, ba, hour).length);
    if (p.net) {
      assert.ok(p.net.raw >= 0, "a net is written as an export or an import, never negative");
      const sum = p.ties.reduce((a, t) => a + t.raw, 0);
      assert.equal(p.net.kind, sum >= 0 ? "export" : "import");
    }
    for (let i = 1; i < p.ties.length; i += 1) assert.ok(Math.abs(p.ties[i - 1].raw) >= Math.abs(p.ties[i].raw), "largest flow first");
    for (const t of p.ties) assert.equal(t.dir, t.raw > 0 ? "out" : t.raw < 0 ? "in" : "none");
  }
  assert.ok(keys > 20, `the seven grids' panels write ${keys} keys`);
});

test("ERCOT's panel matches the Exchange view's figures on the fixture", () => {
  const p = K.networkPanel(snap, "ERCO", hour);
  const ties = N.tiesAt(snap, "ERCO", hour);
  assert.ok(ties.length > 0, "the fixture holds ERCOT's ties in the hour");
  const net = ties.reduce((a, t) => a + t.mw, 0) || 0;
  assert.equal(p.net.check, `net|${net >= 0 ? "export" : "import"}|ERCO|${hour}`);
  assert.equal(p.net.raw, net >= 0 ? net : -net);
});

test("the Lower 48's panel: the seven grids' net export and ties, each recomputed", () => {
  const rows = K.lower48Panel(snap, ISOS, hour);
  assert.equal(rows.length, 7);
  const net = N.netExports(snap, hour);
  for (const r of rows) {
    assert.equal(N.netValue(snap, r.count.check), r.count.raw);
    if (r.net) { assert.equal(N.netValue(snap, r.net.check), r.net.raw); assert.ok(Math.abs(r.net.raw - (net.get(r.ba) || 0)) < 1e-9); }
    else assert.equal(r.count.raw, 0);
  }
});

test("an hour the snapshot does not hold gives no tie and no demand", () => {
  const p = K.networkPanel(snap, "ERCO", "1999-01-01T00:00:00Z");
  assert.equal(p.ties.length, 0);
  assert.equal(p.net, null);
  assert.equal(p.demand, null);
});

test("the demand: the week's eia930_all_demand first, then the hourly snapshot's, then the node's newest", () => {
  const h = snap.hours.indexOf(hour);
  const week = snap.hours.map((_, i) => (i === h ? 61234 : null));
  const a = K.demandAt(snap, "ERCO", hour, week);
  assert.deepEqual([a.check, a.raw], [`series|eia930_all_demand|eia930:ERCO|demand_mw|${hour}`, 61234]);
  // the hourly snapshot's demand_recent, the same value: the netsnap key, as the component writes it
  const hourly = structuredClone(snap);
  const node = hourly.nodes.find((x) => x.id === "ERCO");
  node.demand_src = "hourly"; node.demand_recent = { [hour]: 61234 };
  assert.equal(K.demandAt(hourly, "ERCO", hour, week).check, `netsnap|ERCO|demand_mw|${hour}`);
  assert.equal(K.demandAt(hourly, "ERCO", hour).raw, 61234);
  // a different value in the week than in the snapshot: the week's, under the table's key
  assert.equal(K.demandAt(hourly, "ERCO", hour, snap.hours.map((_, i) => (i === h ? 60000 : null))).check, `series|eia930_all_demand|eia930:ERCO|demand_mw|${hour}`);
  // the committed snapshot: the node's own newest demand at its own hour, else none
  const own = snap.nodes.find((x) => x.id === "ERCO");
  const d = K.demandAt(snap, "ERCO", own.demand_ts);
  assert.deepEqual([d.check, d.raw], [`series|eia930_all_demand|eia930:ERCO|demand_mw|${own.demand_ts}`, own.demand_mw]);
  if (own.demand_ts !== hour) assert.equal(K.demandAt(snap, "ERCO", hour), null);
});

test("the gravity panel: generation, net import as the shape sums it, and the share as a calc|pct of the two keys", () => {
  const h = snap.hours.indexOf(hour);
  const gen = Object.fromEntries([...ISOS, "US48"].map((ba, i) => [ba, snap.hours.map((_, j) => (j === h ? 10000 * (i + 1) : null))]));
  gen.NYIS = undefined;  // a grid whose generation is not held
  const g = K.gravityPanel(snap, G.GRAVITY_GRIDS.map((x) => x.id), G.GRAVITY_CENTER, hour, gen);
  assert.equal(g.center.check, `series|eia930_all_generation|eia930:US48|net_generation_mw|${hour}`);
  assert.equal(g.center.raw, 80000);
  for (const r of g.rows) {
    const shape = G.netImportAt(snap.links, r.ba, h);
    if (shape === null) assert.equal(r.net, null);
    else { assert.ok(Math.abs(r.net.raw - shape) < 1e-9, r.ba); assert.equal(N.netValue(snap, r.net.check), r.net.raw); }
    if (r.ba === "NYIS") { assert.equal(r.gen, null); assert.equal(r.share, null); continue; }
    assert.equal(r.gen.check, `series|eia930_all_generation|eia930:${r.ba}|net_generation_mw|${hour}`);
    if (r.net) {
      const [, op, a, b] = r.share.check.split("|");
      assert.equal(op, "pct");
      assert.equal(a.replaceAll("~", "|"), r.net.check);
      assert.equal(b.replaceAll("~", "|"), r.gen.check);
      assert.ok(Math.abs(r.share.raw - (r.net.raw / r.gen.raw) * 100) < 1e-9);
    }
  }
  assert.equal(K.gravityPanel(snap, ["ERCO"], "US48", hour, undefined).center, null);
});

test("the last 24 hours: latest, lowest and highest per entity, inside the chart's window, earliest on a tie", () => {
  const t = (h) => new Date(Date.UTC(2026, 9, 20, h)).toISOString().replace(".000Z", "Z");
  const rows = [
    { entity: "eia930:ERCO", variable: "intensity_generation", ts_utc: t(0), value: 999 },     // 23 hours before the newest: in
    { entity: "eia930:ERCO", variable: "intensity_generation", ts_utc: t(5), value: 200 },
    { entity: "eia930:ERCO", variable: "intensity_generation", ts_utc: t(9), value: 200 },
    { entity: "eia930:ERCO", variable: "intensity_generation", ts_utc: t(12), value: 999 },
    { entity: "eia930:ERCO", variable: "intensity_demand", ts_utc: t(13), value: 1 },
    { entity: "eia930:ERCO", variable: "intensity_generation", ts_utc: t(23), value: 342.2921 },
    { entity: "eia930:PJM", variable: "intensity_generation", ts_utc: t(-1), value: 50 },     // 24 hours before: out
  ];
  const newest = Date.parse(t(23));
  const d = K.lastDayFigures(rows, ["eia930:ERCO", "eia930:PJM"], newest);
  assert.equal(d.length, 1, "an entity with no hour in the window is left out");
  const e = d[0];
  assert.equal(e.hours, 5);
  assert.deepEqual([e.latest.raw, e.latest.ts], [342.2921, t(23)]);
  assert.deepEqual([e.low.raw, e.low.ts], [200, t(5)]);
  assert.deepEqual([e.high.raw, e.high.ts], [999, t(0)]);
  assert.equal(e.low.check, `series|carbon_intensity_hourly|eia930:ERCO|intensity_generation|${t(5)}`);
  assert.ok(e.high.tip.startsWith("carbon_intensity_hourly, entity eia930:ERCO"));
});

console.log(`\n${n} tests passed`);
