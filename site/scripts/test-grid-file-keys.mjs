// Energy Research Warehouse (ERW) site, session 1166 (chain 078): the keys of the Mix tab's last unkeyed figures and of
// the committed-file views, recomputed as scripts/check-values.mjs recomputes them. Needs no build, no server and no
// database: the committed files of site/data/ and a fixture of real rows (scripts/fixtures/grid_yesterday.json).
//
//   node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-file-keys.mjs
//
// 1. scripts/check-format.mjs: each form writes a number as the page writes it (lib/mixpage.ts n0, n1, n2; lib/format.ts
//    count; Conditions.tsx's toFixed(1) and its sign); fmt| keys parse, their inner key whole.
// 2. scripts/check-file.mjs: a path reads what the page's library reads (lib/clean.ts, lib/stress.ts, lib/mix2.ts) on the
//    committed files; each file's table row is named (or none); sameWithin holds the rounding.
// 3. lib/gridYesterday.ts, the calc op diffpct, lib/caisoAlerts.ts awe|rows and awe|newest, on real rows, against the
//    arithmetic that stood in the page.
// 4. The views drawn on the server (components/mix/views.tsx, through the tsx loader, client charts stubbed): every key
//    they write is recomputed from the committed file to the page's raw value, and its text is the value in its form.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import * as FMT from "./check-format.mjs";
import * as FILE from "./check-file.mjs";
import * as CALC from "./check-calc.mjs";
import * as Y from "../lib/gridYesterday.ts";
import * as A from "../lib/caisoAlerts.ts";
import * as clean from "../lib/clean.ts";
import * as stress from "../lib/stress.ts";
import * as mix from "../lib/mix2.ts";
import { n0, n1, n2, choiceOf } from "../lib/mixpage.ts";
import { count } from "../lib/format.ts";
import * as V from "../components/mix/views.tsx";

const here = path.dirname(fileURLToPath(import.meta.url));
const DATA = path.join(here, "..", "data");
const read = (f) => JSON.parse(fs.readFileSync(path.join(DATA, f), "utf-8"));
const FX = JSON.parse(fs.readFileSync(path.join(here, "fixtures", "grid_yesterday.json"), "utf-8"));
const GRIDS = ["caiso", "ercot", "isone", "miso", "nyiso", "pjm", "spp"];
const XS = [0, 0.04, -0.04, 0.05, 1.25, 12.345, -3.96, 999.95, 1234.5, -21876.4, 45.8367, 91075, 6599.5, -0.6];

// ---- 1. the forms

test("each form writes a number as the page's own function writes it", () => {
  for (const x of XS) {
    assert.equal(FMT.formText("n0", x), n0(x), `n0 ${x}`);
    assert.equal(FMT.formText("n0", x), count(x), `count ${x}`);
    assert.equal(FMT.formText("n1", x), n1(x), `n1 ${x}`);
    assert.equal(FMT.formText("n2", x), n2(x), `n2 ${x}`);
    assert.equal(FMT.formText("f1", x), x.toFixed(1), `f1 ${x}`);
    // Conditions.tsx: the miss at the peak, its sign then count of its size, U+2212 below zero
    assert.equal(FMT.formText("pm0", x), `${x >= 0 ? "+" : "−"}${count(Math.abs(x))}`, `pm0 ${x}`);
    // views.tsx: the forecast's mean error and the clean view's change, "+" above zero
    assert.equal(FMT.formText("sn0", x), `${x > 0 ? "+" : ""}${n0(x)}`, `sn0 ${x}`);
    assert.equal(FMT.formText("sn1", x), `${x > 0 ? "+" : ""}${n1(x)}`, `sn1 ${x}`);
  }
  assert.equal(FMT.formText("n1", null), undefined);
  assert.equal(FMT.formText("n1", "x"), undefined);
  assert.equal(FMT.formText("nope", 1), undefined);
});

test("session 1168: the span form writes a stretch of hours as lib/stress.ts span does", () => {
  for (const h of [0, 1, 2, 15, 18, 23, 24, 25, 38, 48, 62, 101, 23.6, 47.5, 240]) assert.equal(FMT.formText("span", h), stress.span(h), `span ${h}`);
  assert.equal(FMT.formText("span", 101), "4 days 5 hours");
  assert.equal(FMT.formText("span", 18), "18 hours");
  assert.equal(FMT.formText("span", 24), "1 day");
  assert.deepEqual(FMT.fmtParts("fmt|span|file|stress/ercot.json|years.2025.calm_longest_hours"), { form: "span", inner: "file|stress/ercot.json|years.2025.calm_longest_hours" });
  assert.equal(FMT.formText("span", null), undefined);
});

test("a fmt| key is its form and its inner key whole, the calc operands' ~ kept", () => {
  const inner = "calc|pct|series_sum~eia930_all_generation~net_generation_wind_mw,net_generation_wind_with_battery_mw~2026-10-21T00:00:00Z~2026-10-22T00:00:00Z~eia930:ERCO|series_sum~eia930_all_generation~net_generation_mw~2026-10-21T00:00:00Z~2026-10-22T00:00:00Z~eia930:ERCO";
  assert.deepEqual(FMT.fmtParts(`fmt|f1|${inner}`), { form: "f1", inner });
  assert.equal(FMT.fmtKey("n1", "file|clean/ercot.json|years.2025.carbon_free_share_pct"), "fmt|n1|file|clean/ercot.json|years.2025.carbon_free_share_pct");
  assert.equal(FMT.fmtParts("fmt|zz|series|t|e|v|2026"), null);
  assert.equal(FMT.fmtParts("series|t|e|v|2026"), null);
  assert.throws(() => FMT.fmtKey("zz", "x"));
});

// ---- 2. the files

test("a path reads what the page's libraries read, on every grid's committed files", () => {
  for (const g of GRIDS) {
    const c = read(`clean/${g}.json`), s = read(`stress/${g}.json`), m = read(`mix/${g}.json`);
    for (const y of clean.yearsOf(c)) {
      const v = clean.yearView(c, y);
      assert.equal(FILE.readPath(c, `years.${y}.carbon_free_share_pct`) ?? null, v.share, `${g} ${y}`);
      assert.equal(FILE.readPath(c, `years.${y}.shift20_cost_change_pct`) ?? null, v.cost.change[20] ?? null, `${g} ${y} cost`);
      for (const l of c.levels) assert.equal(FILE.readPath(c, `years.${y}.hours_cf_ge${l}_pct`) ?? null, v.ge[l], `${g} ${y} ${l}`);
    }
    for (const y of stress.yearsOf(s)) assert.equal(FILE.readPath(s, `years.${y}.evening_ramp_max_share_of_peak_pct`) ?? null, stress.get(s, y, "evening_ramp_max_share_of_peak_pct"), `${g} ${y}`);
    for (const r of mix.RECORD_ROWS) {
      assert.equal(FILE.readPath(m, `records[variable=${r.variable},period=all].value`), mix.recordOf(m, r.variable, "all")?.value, `${g} ${r.variable}`);
      assert.equal(FILE.readPath(m, `records[variable=year_${r.variable},period=2025].value`), mix.recordOf(m, r.variable, "2025")?.value, `${g} ${r.variable} 2025`);
    }
    const p = mix.periodOf(m, m.upto);
    for (const sh of mix.shares(p)) if (typeof p[`${sh.key}_share_pct`] === "number") assert.equal(FILE.readPath(m, `months.${m.upto}.${sh.key}_share_pct`), sh.share);
    const plus = read(`mixplus/${g}.json`);
    for (const r of plus.records.all ?? []) assert.equal(FILE.readPath(plus, `records.all[key=${r.key}].value`), r.value);
  }
  assert.equal(FILE.readPath(read("clean/ercot.json"), "years.1999.carbon_free_share_pct"), undefined);
  assert.equal(FILE.readPath(read("mix/ercot.json"), "records[variable=nothing,period=all].value"), undefined);
  assert.throws(() => FILE.segments("a.[x=1]"));
});

test("a file| key names its file and path; a file outside site/data's names is not one", () => {
  assert.deepEqual(FILE.fileParts("file|stress/ercot.json|years.2025.calm_hours"), { file: "stress/ercot.json", path: "years.2025.calm_hours" });
  assert.deepEqual(FILE.fileParts("file|mix_forecast.json|grids.ercot.sources.wind.all.n"), { file: "mix_forecast.json", path: "grids.ercot.sources.wind.all.n" });
  assert.equal(FILE.fileParts("file|../secret.json|x"), null);
  assert.equal(FILE.fileParts("file|stress/ercot.csv|x"), null);
  assert.equal(FILE.fileParts("series|a|b|c|d"), null);
});

test("each file's value is named by the live-set row it was built from, or by none", () => {
  const m = read("mix/ercot.json");
  assert.deepEqual(FILE.tableRow("stress/ercot.json", "years.2025.calm_hours"), { table: "grid_stress_yearly", entity: "iso:ercot", variable: "calm_hours", ts_utc: "2025-01-01T00:00:00Z", freq: null });
  assert.deepEqual(FILE.tableRow("clean/miso.json", "years.2025.carbon_free_share_pct"), { table: "clean_energy_summary", entity: "iso:miso", variable: "year_carbon_free_share_pct", ts_utc: "2025-01-01T00:00:00Z", freq: "P1Y" });
  assert.deepEqual(FILE.tableRow("clean/miso.json", "months.2025-07.carbon_free_share_pct"), { table: "clean_energy_summary", entity: "iso:miso", variable: "carbon_free_share_pct", ts_utc: "2025-07-01T00:00:00Z", freq: "P1M" });
  assert.deepEqual(FILE.tableRow("mix/ercot.json", "months.2026-09.wind_share_pct"), { table: "generation_mix_hourly_profile", entity: "iso:ercot", variable: "wind_share_pct", ts_utc: "2026-09-01T00:00:00Z", freq: null });
  const rec = mix.recordOf(m, "solar_share_max_pct", "all");
  assert.deepEqual(FILE.tableRow("mix/ercot.json", "records[variable=solar_share_max_pct,period=all].value", m), { table: "generation_mix_records", entity: "iso:ercot", variable: "solar_share_max_pct", ts_utc: rec.ts_utc, freq: null });
  assert.equal(FILE.tableRow("mix/ercot.json", "years.2025.wind_share_pct"), null);   // the builder's year: the table holds months
  assert.equal(FILE.tableRow("mixplus/ercot.json", "records.all[key=x].value"), null);
  assert.equal(FILE.tableRow("mix_forecast.json", "grids.ercot.sources.wind.all.n"), null);
  assert.equal(FILE.tableRow("clean/ercot.json", "years.2025"), null);   // not a value's path
});

test("a file's value and its table's are the same within the less precise one's rounding", () => {
  assert.ok(FILE.sameWithin(19.651, 19.651));
  assert.ok(FILE.sameWithin(45.8367, 45.84));
  assert.ok(FILE.sameWithin(91075, 91075));
  assert.ok(!FILE.sameWithin(91075, 91076));
  assert.ok(!FILE.sameWithin(45.8367, 45.83));
  assert.ok(!FILE.sameWithin(1, undefined));
  assert.equal(FILE.decimals(1e-7), 9);
});

// ---- 3. the database figures' arithmetic, on real rows

test("the day's mean miss and its hours are the arithmetic that stood in Conditions.tsx", () => {
  const dem = FX.demand, fc = new Map(FX.forecast.map((x) => [x.ts_utc, x.value]));
  const pairs = dem.filter((x) => fc.has(x.ts_utc));
  const mape = pairs.length ? (100 * pairs.reduce((a, x) => a + Math.abs(x.value - fc.get(x.ts_utc)) / x.value, 0)) / pairs.length : null;
  const m = Y.forecastMiss(dem, FX.forecast);
  assert.equal(m.mape, mape);
  assert.equal(m.hours, pairs.length);
  assert.equal(m.hours, 24);
  assert.deepEqual(Y.forecastMiss(dem, []), { mape: null, hours: 0 });
  // the miss at the peak, demand less forecast, and as a percent of demand (calc|diff, calc|diffpct)
  const peak = dem.reduce((a, b) => (b.value > a.value ? b : a));
  const f = fc.get(peak.ts_utc);
  assert.equal(CALC.calcOf("diff", [peak.value, f]), peak.value - f);
  assert.equal(CALC.calcOf("diffpct", [peak.value, f]), ((peak.value - f) / peak.value) * 100);
  assert.equal(FMT.formText("f1", CALC.calcOf("diffpct", [peak.value, f])), (((peak.value - f) / peak.value) * 100).toFixed(1));
  assert.equal(CALC.calcOf("diffpct", [1, 2, 3]), undefined);
});

test("degree days are the arithmetic that stood in Conditions.tsx, on both sides of the base", () => {
  const kinds = [];
  for (const [st, h] of Object.entries(FX.temps)) {
    const mean = h.length ? h.reduce((a, x) => a + x.value, 0) / h.length : 0;
    assert.deepEqual(Y.dayMean(h), { n: h.length, mean });
    const dd = Y.degreeDay(h);
    assert.deepEqual(dd, mean >= 65 ? { kind: "cdd", value: mean - 65 } : { kind: "hdd", value: 65 - mean }, st);
    kinds.push(dd.kind);
    assert.equal(Y.degreeDay(h.slice(1)), null);   // 23 hours: none, as the page says "not computed"
  }
  assert.deepEqual(kinds.sort(), ["cdd", "hdd"]);
});

test("awe|rows and awe|newest count every notice and name the newest day, as the Reliability section writes them", () => {
  const rows = JSON.parse(fs.readFileSync(path.join(here, "fixtures", "caiso_alerts.json"), "utf-8")).rows ?? [];
  const asRead = rows.map((r) => ({ event_date: String(r.event_date), event_type: r.event_type }));
  assert.ok(asRead.length > 0);
  assert.equal(A.aweValue(asRead, "awe|rows|any"), asRead.length);
  const sorted = [...asRead].sort((a, b) => a.event_date.localeCompare(b.event_date));
  assert.equal(A.aweValue(asRead, "awe|newest|any"), sorted.at(-1).event_date.slice(0, 10));
  assert.equal(A.aweValue(asRead, "awe|rows|rmo"), asRead.filter((r) => r.event_type === "rmo").length);
  assert.equal(A.aweValue(asRead, "awe|rows|nothing"), undefined);
});

// ---- 4. the views, drawn

const KEY = /<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)<\/span>/g;
const decode = (s) => s.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#x27;/g, "'");
function keysOf(el) {
  const html = renderToStaticMarkup(el);
  return [...html.matchAll(KEY)].map((m) => ({ check: decode(m[1]), raw: decode(m[2]), text: decode(m[3].replace(/<!-- -->/g, "").replace(/<[^>]+>/g, "")).trim() }));
}
function recompute(k) {
  const f = FMT.fmtParts(k.check);
  assert.ok(f, `${k.check}: a file figure is written in a form`);
  const fk = FILE.fileParts(f.inner);
  assert.ok(fk, `${k.check}: a file key`);
  const v = FILE.readPath(read(fk.file), fk.path);
  assert.equal(typeof v, "number", `${k.check}: the file holds a number there`);
  assert.ok(Math.abs(v - Number(k.raw)) <= 1e-9 * Math.max(1, Math.abs(v)), `${k.check}: file ${v}, page ${k.raw}`);
  assert.equal(k.text, FMT.formText(f.form, v), `${k.check}: the text`);
  return fk;
}

const VIEWS = [["clean", V.CleanView], ["stress", V.StressView], ["day", V.DayView], ["records", V.RecordsView], ["supply", V.SupplyView], ["forecast", V.ForecastView]];

test("every key the views write is the committed file's value, written in its form", () => {
  const seen = {};
  for (const [view, View] of VIEWS) {
    for (const g of GRIDS) {
      const c = choiceOf({ view, grids: g });
      const ks = keysOf(createElement(View, { c }));
      for (const k of ks) recompute(k);
      seen[view] = (seen[view] ?? 0) + ks.length;
    }
  }
  for (const [view] of VIEWS) assert.ok(seen[view] > 0, `${view}: keys drawn`);
});

test("the clean view keys no figure of a grid held for a license (ISO-NE, MISO, NYISO: their cells as they were)", () => {
  const held = ["isone", "miso", "nyiso"];
  for (const g of GRIDS) {
    const ks = keysOf(createElement(V.CleanView, { c: choiceOf({ view: "clean", grids: g }) }));
    for (const h of held) assert.ok(!ks.some((k) => k.check.includes(`clean/${h}.json`)), `${g}: no key of ${h}`);
  }
});

test("session 1168: the stress view keys its large tables whole: every held figure of the fuels and the stretches, and the longest in days and hours", () => {
  for (const g of GRIDS) {
    const f = read(`stress/${g}.json`), ys = stress.yearsOf(f), year = stress.defaultYear(f);
    const ks = new Map(keysOf(createElement(V.StressView, { c: choiceOf({ view: "stress", grids: g }) })).map((k) => [FMT.fmtParts(k.check).inner, k]));
    const has = (y, v) => ks.has(`file|stress/${g}.json|years.${y}.${v}`);
    for (const r of stress.fuelRows(f, year)) {
      assert.equal(has(year, `tight_${r.fuel}_mw`), r.mw !== null, `${g} ${r.fuel} mw`);
      assert.equal(has(year, `capacity_${r.fuel}_mw`), r.capacity !== null, `${g} ${r.fuel} capacity`);
      assert.equal(has(year, `tight_${r.fuel}_share_of_capacity_pct`), r.share !== null, `${g} ${r.fuel} share`);
    }
    for (const y of ys) {
      for (const v of ["calm_hours", "calm_stretches_ge24h", "calm_longest_missing_mwh", "calm_longest_fleet_mw", "calm_longest_fleet_mwh", "calm_longest_fleet_full_power_hours", "calm_longest_fleet_energy_multiples", "calm_longest_hours"])
        assert.equal(has(y, v), stress.get(f, y, v) !== null, `${g} ${y} ${v}`);
      const k = ks.get(`file|stress/${g}.json|years.${y}.calm_longest_hours`);
      if (k) { assert.ok(k.check.startsWith("fmt|span|"), k.check); assert.equal(k.text, stress.span(stress.get(f, y, "calm_longest_hours"))); }
    }
  }
});

test("the views' file keys name a live-set row where the file is a build of one", () => {
  const ks = keysOf(createElement(V.StressView, { c: choiceOf({ view: "stress", grids: "ercot" }) }));
  const rows = ks.map((k) => FILE.tableRow(FILE.fileParts(FMT.fmtParts(k.check).inner).file, FILE.fileParts(FMT.fmtParts(k.check).inner).path));
  assert.ok(rows.length > 40);
  assert.ok(rows.every((r) => r && r.table === "grid_stress_yearly"));
  const fk = keysOf(createElement(V.ForecastView, { c: choiceOf({ view: "forecast", grids: "ercot" }) }));
  assert.ok(fk.length > 0 && fk.every((k) => FILE.tableRow(FILE.fileParts(FMT.fmtParts(k.check).inner).file, "x") === null));
});
