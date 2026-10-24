// Energy Research Warehouse (ERW) site, session 1412 (chain 107): the Flex Alert scorecard's small charts
// (/grid/caiso/alerts, "Each alert day through the evening") keep their drawing and answer a hover.
//
//   node scripts/test-alert-day-chart.mjs
//
// lib/alertDayChart.ts holds session 60's DayChart arithmetic, moved out of app/grid/caiso/alerts/page.tsx so the client
// chart (app/grid/caiso/alerts/DayChart.tsx) can draw it. Here session 60's code, copied as it stood at f448db93 (the
// reference below, its lines unchanged but for returning what it drew), and the lib are run on the committed real rows of
// fixtures/grid_older_reads.json (session 1411: flex_alert_effects, every PT1H row of seven alert days), and on rows made
// to miss a value: every drawn string (the two lines, the band, the boxed hours, the axis labels) must be the same. Then
// the hover: the nearest hour, and the card's figures, each the hour's own row (demand served, the model's estimate, its
// band, the estimate less demand). No build, no network, no node_modules. Exit 0 when every case holds.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as A from "../lib/alertDayChart.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const fx = JSON.parse(fs.readFileSync(path.join(here, "fixtures", "grid_older_reads.json"), "utf-8"));
let n = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };

// lib/flexalerts.ts pacificDay and pacificHour (the alert season is all daylight time, UTC-7)
const pacificDay = (ts) => new Date(Date.parse(ts) - 7 * 3600_000).toISOString().slice(0, 10);
const pacificHour = (ts) => new Date(Date.parse(ts) - 7 * 3600_000).getUTCHours();

// the rows of each alert day, as lib/flexalerts.ts shape() groups them (freq PT1H, by Pacific day)
const days = new Map();
for (const [k, rs] of Object.entries(fx.rows.flex_alert_effects)) {
  const [entity, variable, unit, freq] = k.split("|");
  if (freq !== "PT1H") continue;
  for (const [ts, value] of rs) {
    const d = pacificDay(ts);
    (days.get(d) ?? days.set(d, []).get(d)).push({ entity, variable, ts_utc: ts, value, unit, freq });
  }
}

/** Session 60's DayChart (app/grid/caiso/alerts/page.tsx at f448db93), its arithmetic line for line; it returns what the
 *  svg drew instead of drawing it. */
function reference(rows) {
  const by = new Map();
  for (const r of rows) {
    const h = pacificHour(r.ts_utc);
    (by.get(h) ?? by.set(h, {}).get(h))[r.variable] = r.value;
  }
  const hs = [...by.keys()].sort((a, b) => a - b);
  if (!hs.length) return null;
  const vals = hs.flatMap((h) => ["actual_mw", "predicted_mw_lo", "predicted_mw_hi"].map((k) => by.get(h)[k]).filter((v) => v !== undefined));
  const lo = Math.min(...vals), hi = Math.max(...vals), pad = (hi - lo) * 0.08 || 500;
  const W = 260, Hh = 120, L = 34, B = 16, x = (h) => L + ((h - hs[0]) / Math.max(1, hs.at(-1) - hs[0])) * (W - L - 6);
  const y = (v) => 4 + (1 - (v - (lo - pad)) / (hi - lo + 2 * pad)) * (Hh - B - 4);
  const path = (k) => hs.filter((h) => by.get(h)[k] !== undefined).map((h, i) => `${i ? "L" : "M"}${x(h).toFixed(1)},${y(by.get(h)[k]).toFixed(1)}`).join("");
  const band = hs.map((h) => `${x(h).toFixed(1)},${y(by.get(h).predicted_mw_hi).toFixed(1)}`).join(" ") + " " +
    [...hs].reverse().map((h) => `${x(h).toFixed(1)},${y(by.get(h).predicted_mw_lo).toFixed(1)}`).join(" ");
  const alertHs = hs.filter((h) => by.get(h).alert_hour === 1);
  const step = (W - L - 6) / Math.max(1, hs.at(-1) - hs[0]);
  return {
    viewBox: `0 0 ${W} ${Hh}`,
    rects: alertHs.map((h) => [x(h) - step / 2, 2, step, Hh - B - 2]),
    band, predicted: path("predicted_mw"), actual: path("actual_mw"),
    labels: [[2, 10, `${Math.round(hi / 1000)} GW`], [2, Hh - B, `${Math.round(lo / 1000)} GW`], ...hs.filter((h) => h % 3 === 0).map((h) => [x(h), Hh - 4, `${h}:00`])],
  };
}

/** The same, through lib/alertDayChart.ts as the client chart draws it (the page's grouping, then the points). */
function lib(rows) {
  const by = new Map();
  for (const r of rows) {
    const h = pacificHour(r.ts_utc);
    (by.get(h) ?? by.set(h, {}).get(h))[r.variable] = r.value;
  }
  if (!by.size) return null;
  const g = A.dayGeometry(A.pointsOf(by));
  return {
    viewBox: `0 0 ${A.W} ${A.Hh}`,
    rects: g.alertHs.map((h) => [g.x(h) - g.step / 2, 2, g.step, A.Hh - A.B - 2]),
    band: g.band, predicted: g.predicted, actual: g.actual,
    labels: [[2, 10, `${Math.round(g.hi / 1000)} GW`], [2, A.Hh - A.B, `${Math.round(g.lo / 1000)} GW`], ...g.ticks.map((h) => [g.x(h), A.Hh - 4, `${h}:00`])],
  };
}

test("the fixture holds alert days with their evening hours (5 to 12 hours each, as session 1411 cut it)", () => {
  assert.equal(days.size, 7);
  for (const [d, rows] of days) assert.ok(new Set(rows.map((r) => pacificHour(r.ts_utc))).size >= 5, d);
});

for (const [d, rows] of [...days].sort()) {
  test(`${d}: the drawing is session 60's, string for string`, () => {
    const a = reference(rows), b = lib(rows);
    assert.deepEqual(b, a);
    assert.ok(a.actual.startsWith("M") && a.predicted.startsWith("M") && a.band.length > 0);
  });
}

test("an hour missing a value draws as it did (a gap in a line, the band as before)", () => {
  const [d, rows] = [...days].sort()[0];
  const drop = new Set([`actual_mw|${rows.find((r) => r.variable === "actual_mw").ts_utc}`, `predicted_mw|${rows.filter((r) => r.variable === "predicted_mw").at(-1).ts_utc}`]);
  const cut = rows.filter((r) => !drop.has(`${r.variable}|${r.ts_utc}`));
  assert.deepEqual(lib(cut), reference(cut), d);
  assert.equal(lib([]), null);
  assert.equal(reference([]), null);
});

test("a flat day takes 500 MW of room each side, as before", () => {
  const flat = [12, 13, 14].flatMap((h) => ["actual_mw", "predicted_mw", "predicted_mw_lo", "predicted_mw_hi"].map((variable) => ({ variable, value: 30000, ts_utc: new Date(Date.UTC(2022, 8, 6, h + 7)).toISOString() })));
  assert.deepEqual(lib(flat), reference(flat));
});

test("a point keeps every value of its hour, and a value not held is absent, not zero", () => {
  const by = new Map([[17, { actual_mw: 45000, predicted_mw: 46000, predicted_mw_lo: 44000, predicted_mw_hi: 48000, alert_hour: 1 }], [16, { actual_mw: 44000 }]]);
  const pts = A.pointsOf(by);
  assert.deepEqual(pts, [[16, 44000, null, null, null, null], [17, 45000, 46000, 44000, 48000, 1]]);
  assert.deepEqual(A.record(pts[0]), { actual_mw: 44000 });
  assert.deepEqual(A.record(pts[1]), by.get(17));
});

test("the hover takes the nearest hour held", () => {
  const [, rows] = [...days].sort()[0];
  const by = new Map();
  for (const r of rows) (by.get(pacificHour(r.ts_utc)) ?? by.set(pacificHour(r.ts_utc), {}).get(pacificHour(r.ts_utc)))[r.variable] = r.value;
  const g = A.dayGeometry(A.pointsOf(by));
  for (const h of g.hs) {
    assert.equal(A.nearestHour(g.hs, g.x, g.x(h)), h);
    assert.equal(A.nearestHour(g.hs, g.x, g.x(h) + g.step * 0.4), h);
  }
  assert.equal(A.nearestHour(g.hs, g.x, -50), g.hs[0]);
  assert.equal(A.nearestHour(g.hs, g.x, 9999), g.hs.at(-1));
});

test("the card's figures are the hour's own rows: demand, the estimate, its band, the estimate less demand", () => {
  for (const [d, rows] of days) {
    const h = pacificHour(rows.at(-1).ts_utc);
    const at = (v) => rows.find((r) => r.variable === v && pacificHour(r.ts_utc) === h)?.value;
    const by = new Map();
    for (const r of rows) (by.get(pacificHour(r.ts_utc)) ?? by.set(pacificHour(r.ts_utc), {}).get(pacificHour(r.ts_utc)))[r.variable] = r.value;
    const c = A.hourCard(A.dayGeometry(A.pointsOf(by)).by.get(h), h);
    assert.equal(c.hour, `${h}:00`, d);
    assert.equal(c.actual, at("actual_mw"), d);
    assert.equal(c.predicted, at("predicted_mw"), d);
    assert.equal(c.lo, at("predicted_mw_lo"), d);
    assert.equal(c.hi, at("predicted_mw_hi"), d);
    assert.equal(c.diff, at("predicted_mw") - at("actual_mw"), d);
    assert.equal(c.alert, at("alert_hour") === 1, d);
  }
  const none = A.hourCard({ actual_mw: 40000 }, 13);
  assert.equal(none.diff, undefined);
  assert.equal(none.predicted, undefined);
  assert.equal(none.alert, false);
});

test("the client chart draws the lib's strings with session 60's attributes, and its card is the shared one", () => {
  const c = fs.readFileSync(path.join(here, "..", "app", "grid", "caiso", "alerts", "DayChart.tsx"), "utf-8");
  assert.ok(c.startsWith('"use client";'));
  for (const s of [
    '<svg viewBox={`0 0 ${W} ${Hh}`} className="h-auto w-full" role="img" aria-label={ariaLabel}',
    '{alertHs.map((h) => <rect key={h} x={x(h) - step / 2} y={2} width={step} height={Hh - B - 2} fill="var(--color-panel)" stroke="var(--color-rule)" strokeWidth={0.4} />)}',
    '<polygon points={band} fill="var(--color-rule)" opacity={0.7} />',
    '<path d={predicted} fill="none" stroke="var(--color-muted)" strokeWidth={1.2} strokeDasharray="3 2" />',
    '<path d={actual} fill="none" stroke="var(--color-accent)" strokeWidth={1.6} />',
    '<text x={2} y={10} fontSize={8} fill="var(--color-muted)">{Math.round(hi / 1000)} GW</text>',
    '<text x={2} y={Hh - B} fontSize={8} fill="var(--color-muted)">{Math.round(lo / 1000)} GW</text>',
    '{ticks.map((h) => <text key={h} x={x(h)} y={Hh - 4} fontSize={8} textAnchor="middle" fill="var(--color-muted)">{h}:00</text>)}',
    'import { Card, num } from "@/components/svgchart";',
    "{hover && c ? (",
  ]) assert.ok(c.includes(s), s);
  // what the hover adds is drawn only while a card is open, after the drawing
  assert.ok(c.indexOf("data-alert-day-hover") > c.indexOf("{ticks.map("));
  // a finger: a tap opens and closes; its leave does not close
  assert.ok(c.includes('onPointerLeave={(e) => { if (!touch(e)) setHover(null); }}'));
  assert.ok(c.includes("setHover((o) => (o && o.h === n.h ? null : n))"));
  assert.ok(c.includes('document.addEventListener("pointerdown", off)'));
});

console.log(`every case holds (${n} cases)`);
