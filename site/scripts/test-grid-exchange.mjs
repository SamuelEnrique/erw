// Energy Research Warehouse (ERW) site, session 1167 (chain 078): the Exchange blocks under the gravity shape
// (components/grid/ExchangeView.tsx). Each neighbour's flow in the hour shown keeps its key; beside it the same tie over
// the snapshot's week, keyed nettie|<mean|min|max|hours>|<BA>|<other>|<from>|<to>, which check-values recomputes with
// lib/gridKeys.ts nettieValue on the snapshots it reads. The direction in words. No build, no server, no database: the
// committed snapshot (data/grid_network.json) and typed cases.
//
//   node scripts/test-grid-exchange.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import * as K from "../lib/gridKeys.ts";
import * as N from "../lib/network.ts";
import * as V3 from "../lib/networkV3.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const SNAP = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "grid_network.json"), "utf-8"));
const ISO = ["CISO", "ERCO", "ISNE", "MISO", "NYIS", "PJM", "SWPP"];
const H = ["2026-10-10T00:00:00Z", "2026-10-10T01:00:00Z", "2026-10-10T02:00:00Z", "2026-10-10T03:00:00Z"];
const tiny = (links, hours = H) => ({ built: "2026-10-12T05:30:00Z", window: [hours[0], hours[hours.length - 1]], hours, rule: "", nodes: [], links });
/** The hour ExchangeView opens on, and its ties as it orders them. */
function hourAndTies(snap, ba) {
  const hour = V3.completeHour(snap.hours, snap.links).hour ?? snap.hours[snap.hours.length - 1];
  const ties = N.tiesAt(snap, ba, hour).map((t) => ({ ...t, mw: t.mw || 0 })).sort((a, b) => Math.abs(b.mw) - Math.abs(a.mw));
  return { hour, ties };
}

test("tieWeek: signed from the grid's side, the held hours only, the mean in whole MW", () => {
  const links = [{ a: "ERCO", b: "SWPP", mw: [120, null, -30, 41] }, { a: "CEN", b: "ERCO", mw: [30, 5, null, null] }];
  assert.deepEqual(K.tieWeek(links, "ERCO", "SWPP"), { mean: 44, min: -30, max: 120, hours: 3 });
  assert.deepEqual(K.tieWeek(links, "SWPP", "ERCO"), { mean: -44, min: -120, max: 30, hours: 3 });
  assert.deepEqual(K.tieWeek(links, "ERCO", "CEN"), { mean: -17, min: -30, max: -5, hours: 2 });   // -17.5: Math.round, half up
  assert.equal(K.tieWeek(links, "ERCO", "PJM"), null);
  assert.equal(K.tieWeek([{ a: "ERCO", b: "SWPP", mw: [null, null] }], "ERCO", "SWPP"), null);
  assert.ok(Object.is(K.tieWeek([{ a: "A", b: "B", mw: [0, -0] }], "B", "A").mean, 0), "no -0");
});

test("nettieValue: the key's figure on the snapshots, undefined off the window or on a key not its own", () => {
  const snap = tiny([{ a: "ERCO", b: "SWPP", mw: [120, null, -30, 41] }]);
  const k = (stat, ba = "ERCO", other = "SWPP", from = H[0], to = H[3]) => `nettie|${stat}|${ba}|${other}|${from}|${to}`;
  assert.equal(K.nettieValue(k("mean"), [snap]), 44);
  assert.equal(K.nettieValue(k("min"), [snap]), -30);
  assert.equal(K.nettieValue(k("max"), [snap]), 120);
  assert.equal(K.nettieValue(k("hours"), [snap]), 3);
  assert.equal(K.nettieValue(k("mean", "SWPP", "ERCO"), [snap]), -44);
  assert.equal(K.nettieValue(k("mean", "ERCO", "SWPP", H[1], H[2]), [snap]), -30);       // a narrower window
  assert.equal(K.nettieValue(k("median"), [snap]), undefined);
  assert.equal(K.nettieValue(k("mean", "ERCO", "SWPP", "2026-10-09T00:00:00Z"), [snap]), undefined);   // the window's first hour not held
  assert.equal(K.nettieValue(k("mean", "ERCO", "PJM"), [snap]), undefined);
  assert.equal(K.nettieValue("netbal|absmean|ERCO|x|y", [snap]), undefined);
  assert.equal(K.nettieValue("nettie|mean|ERCO", [snap]), undefined);
});

test("nettieValue reads two snapshots, each hour from the first that holds it (the hourly one moved on, the committed one older)", () => {
  const older = tiny([{ a: "ERCO", b: "SWPP", mw: [10, 20, 30, 40] }]);
  const newer = tiny([{ a: "ERCO", b: "SWPP", mw: [25, 35, 45, 55] }], [H[2], H[3], "2026-10-10T04:00:00Z", "2026-10-10T05:00:00Z"]);
  // the window of the older one, H[0] to H[3]: H[2] and H[3] come from the newer (first), H[0] and H[1] from the older
  assert.equal(K.nettieValue(`nettie|mean|ERCO|SWPP|${H[0]}|${H[3]}`, [newer, older]), Math.round((10 + 20 + 25 + 35) / 4));
  assert.equal(K.nettieValue(`nettie|mean|ERCO|SWPP|${H[0]}|${H[3]}`, [older]), 25);
  assert.equal(K.nettieValue(`nettie|mean|ERCO|SWPP|${H[0]}|${H[3]}`, [newer]), undefined);
});

test("directionWords: the sign in words", () => {
  assert.equal(K.directionWords(5), "sends to");
  assert.equal(K.directionWords(-0.4), "takes from");
  assert.equal(K.directionWords(0), "none");
  assert.equal(K.directionWords(-0), "none");
});

test("exchangeTies on the committed snapshot: every key recomputed to its raw value, the hour's flow inside the week", () => {
  let n = 0;
  for (const ba of ISO) {
    const { hour, ties } = hourAndTies(SNAP, ba);
    const rows = K.exchangeTies(SNAP, ba, hour, ties);
    assert.deepEqual(rows.map((r) => r.other), ties.map((t) => t.other), `${ba}: the block's order`);
    for (const [i, r] of rows.entries()) {
      const t = ties[i];
      assert.equal(r.dir, K.directionWords(t.mw));
      // the hour's flow keeps its key and value: the checker's own function
      assert.equal(N.netValue(SNAP, `net|tie|${ba}|${t.other}|${hour}`), t.mw, `${ba} ${t.other}: the hour's flow stands`);
      for (const stat of K.TIE_STATS) {
        const f = r[stat];
        assert.ok(f, `${ba} ${t.other} ${stat}: drawn (the hour shown holds a flow)`);
        assert.equal(f.check, `nettie|${stat}|${ba}|${t.other}|${SNAP.hours[0]}|${SNAP.hours[SNAP.hours.length - 1]}`);
        assert.equal(K.nettieValue(f.check, [SNAP]), f.raw, `${f.check}`);
        assert.ok(f.tip.includes("eia930_all_interchange") && f.tip.includes(SNAP.built.slice(0, 16).replace("T", " ")), `${f.check}: the tip names the table and the refresh`);
        n += 1;
      }
      assert.ok(r.min.raw <= t.mw && t.mw <= r.max.raw, `${ba} ${t.other}: the hour's flow within the week's lowest and highest`);
      assert.ok(r.min.raw <= r.mean.raw && r.mean.raw <= r.max.raw && r.hours.raw >= 1 && r.hours.raw <= SNAP.hours.length);
      // the hover line: the tie, the hour, the week in words; not the hour's age (said once by the block)
      assert.ok(r.tip.includes(`${ba}'s tie with ${t.other}`) && r.tip.includes(`hour ${hour.slice(0, 10)} ${hour.slice(11, 13)}:00 UTC`) && r.tip.includes("Over the week ("), r.tip);
      assert.ok(r.tip.includes(`mean ${r.mean.raw.toLocaleString("en-US")} MW`) && r.tip.includes(`lowest ${r.min.raw.toLocaleString("en-US")} MW`) && r.tip.includes(`highest ${r.max.raw.toLocaleString("en-US")} MW`));
      assert.ok(!/hours before/.test(r.tip), "no age in the row's tip");
    }
  }
  assert.ok(n > 40, `${n} week figures on the committed snapshot`);
});

test("the hour's age: net|lag on the hour the block opens on, the checker's own function", () => {
  const { hour } = hourAndTies(SNAP, "ERCO");
  const lag = Math.round((Date.parse(SNAP.built) - Date.parse(hour)) / 3_600_000);
  assert.equal(N.netValue(SNAP, `net|lag|${hour}|${SNAP.built}`), lag);
  assert.ok(lag > 24 && lag < 24 * 7, `${lag} hours`);
});

test("ExchangeView: the week's keys, the direction in words and the age once, as written", () => {
  const v = fs.readFileSync(path.join(here, "..", "components", "grid", "ExchangeView.tsx"), "utf-8");
  assert.equal((v.match(/<Age hour=\{hour\} built=\{snap\.built\} \/>/g) ?? []).length, 2, "the age once in each branch (the Lower 48, a grid)");
  assert.ok(v.includes("exchangeTies(snap, ba, hour, ties)"));
  assert.ok(v.includes("<Num check={`net|tie|${ba}|${t.other}|${hour}`} raw={t.mw}>{shown(t.mw)}</Num>"), "the hour's flow: its key and text as before");
  assert.ok(!v.includes('"out" : t.mw < 0 ? "in"'), "the direction in words");
  for (const k of ["net|export|${g.ba}|", 'net|${out ? "export" : "import"}|${ba}|', "net|ties|", "net|maxflow|", "net|topexport|", "bsup|${ba}|neighbour_mwh:", "bsup|${ba}|neighbour:", "bsup|${ba}|days_held"]) assert.ok(v.includes(k), k);
});
