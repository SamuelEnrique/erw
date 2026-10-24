// Energy Research Warehouse (ERW) site, session 1413 (chain 107): the energy mix views' computed figures, keyed
// filecalc|<function>|<data file>|<args> (lib/mixViewCalc.ts, scripts/check-filecalc.mjs). Needs no build, no server and
// no database: the committed files of site/data/.
//
//   node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-mix-view-calc.mjs
//
// 1. Each function moved out of components/mix/views.tsx gives, on every committed file, exactly what the expression
//    that stood in the view gave (written out here as it stood): the history's total, share and million MWh for every
//    state, year and fuel; availability's mean, lowest and highest hour for every grid, year, season and fuel. The duck
//    view's and the average day's functions (lib/mix2.ts acrossYears, highest) did not move: the key applies them.
// 2. The kind: a key parses to its function, file and arguments, and a key that does not fit is no key; its value is the
//    page's figure (the old expression's) on every case; a right value and text pass check-values' rule, a wrong value
//    or a wrong text does not; a case the file does not hold has no value.
// 3. The views drawn on the server (DayView, DuckView, HistoryView, SupplyView, for every grid and for several states):
//    every filecalc| key they write is recomputed from the file to the page's raw value and its text is the value in its
//    form; the keyed cells are the figures the views wrote before (the old expressions), every one, and none is drawn
//    for a case that is not held; the counts are printed.
// 4. check-values, check-methods and the method note know the kind: the note's section names every function and its
//    heading is the method link's fragment (lib/gridAnchors.ts METHOD_MIX_VIEWS).
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import * as FMT from "./check-format.mjs";
import * as FC from "./check-filecalc.mjs";
import * as CM from "./check-methods.mjs";
import * as mix from "../lib/mix2.ts";
import * as calc from "../lib/mixViewCalc.ts";
import * as clean from "../lib/clean.ts";   // session 1414: the clean files' days, as the view read them
import * as LEFT_OUT from "../lib/carbonLeftOut.ts";   // session 1415: the months the carbon chart leaves out, as the page lists them
import { choiceOf } from "../lib/mixpage.ts";
import { METHOD_MIX_VIEWS, MIX_VIEW_ANCHOR, mixViewAnchor } from "../lib/gridAnchors.ts";
import { render } from "../lib/markdown.ts";
import * as V from "../components/mix/views.tsx";

const here = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(here, "..", "..");
const DATA = path.join(here, "..", "data");
const read = (f) => JSON.parse(fs.readFileSync(path.join(DATA, f), "utf-8"));
const GRIDS = ["caiso", "ercot", "isone", "miso", "nyiso", "pjm", "spp"];
const HISTORY = read("mix_history.json");
const LIBS = { mix, calc };
const value = (check) => { const p = FC.filecalcParts(check); assert.ok(p, `${check}: a filecalc key`); return FC.filecalcValueWith(LIBS, p, read(p.file)); };

// The expressions as they stood in components/mix/views.tsx before session 1413 (HistoryView, SupplyView), word for word
// but for the file's name (HISTORY, PLUS[g] here)
const OLD = {
  total: (s, y) => HISTORY.fuels.reduce((a, f) => a + (HISTORY.states[s][y]?.[f] ?? 0), 0),
  share: (s, y, f) => { const r = HISTORY.states[s][y]; const v = r?.months === 12 ? r[f] : undefined; return v === undefined ? null : (100 * v) / OLD.total(s, y); },
  mwh: (s, y, f) => { const r = HISTORY.states[s][y]; const v = r?.months === 12 ? r[f] : undefined; return v === undefined ? null : v / 1e6; },
  mean: (v) => (v ? v.reduce((a, b) => a + b, 0) / v.length : null),
  min: (v) => (v ? Math.min(...v) : null),
  max: (v) => (v ? Math.max(...v) : null),
};

// ---- 1. the functions moved, against the expressions that stood in the view

test("the history's total, share and million MWh are the view's old arithmetic, for every state, year and fuel", () => {
  let n = 0, held = 0;
  for (const s of Object.keys(HISTORY.states)) {
    for (const y of Object.keys(HISTORY.states[s])) {
      assert.equal(calc.historyTotal(HISTORY, s, y), OLD.total(s, y), `${s} ${y} total`);
      for (const f of [...HISTORY.fuels, "nothing"]) {
        const c = calc.historyCell(HISTORY, s, y, f);
        assert.equal(c.share, OLD.share(s, y, f), `${s} ${y} ${f} share`);
        assert.equal(c.mwh, OLD.mwh(s, y, f), `${s} ${y} ${f} mwh`);
        n++;
        if (c.share !== null) held++;
      }
    }
  }
  assert.ok(n > 10000 && held > 5000, `${n} cells, ${held} held`);
  assert.deepEqual(calc.historyCell(HISTORY, "ZZ", "2020", "coal"), { share: null, mwh: null });
});

test("availability's mean, lowest and highest hour are the view's old arithmetic, for every grid, year, season and fuel", () => {
  let n = 0;
  for (const g of GRIDS) {
    const p = read(`mixplus/${g}.json`);
    for (const y of Object.keys(p.availability)) for (const s of ["winter", "spring", "summer", "autumn", "all"]) for (const f of [...p.av_fuels, "nothing"]) {
      const v = calc.availOf(p, y, s, f);
      assert.equal(v, p.availability[y]?.[s]?.[f], `${g} ${y} ${s} ${f}`);
      assert.equal(calc.availMean(v), OLD.mean(v), `${g} ${y} ${s} ${f} mean`);
      assert.equal(calc.availMin(v), OLD.min(v), `${g} ${y} ${s} ${f} min`);
      assert.equal(calc.availMax(v), OLD.max(v), `${g} ${y} ${s} ${f} max`);
      if (v) n++;
    }
  }
  assert.ok(n > 500, `${n} cases held`);
  assert.equal(calc.availMean(undefined), null);
});

// ---- 2. the kind

test("a filecalc| key is its function, file and arguments; a key that does not fit is no key", () => {
  assert.deepEqual(FC.filecalcParts("filecalc|duck_ramp|mix/ercot.json|04|2025"), { fn: "duck_ramp", file: "mix/ercot.json", args: ["04", "2025"] });
  assert.deepEqual(FC.filecalcParts("filecalc|day_peak|mix/caiso.json|2026-09|solar"), { fn: "day_peak", file: "mix/caiso.json", args: ["2026-09", "solar"] });
  assert.deepEqual(FC.filecalcParts("filecalc|hist_share|mix_history.json|TX|2024|wind"), { fn: "hist_share", file: "mix_history.json", args: ["TX", "2024", "wind"] });
  assert.deepEqual(FC.filecalcParts("filecalc|avail_max|mixplus/spp.json|2025|summer|solar"), { fn: "avail_max", file: "mixplus/spp.json", args: ["2025", "summer", "solar"] });
  for (const bad of ["filecalc|nothing|mix/ercot.json|04|2025", "filecalc|duck_ramp|stress/ercot.json|04|2025", "filecalc|duck_ramp|mix/ercot.json|13|2025",
    "filecalc|duck_ramp|mix/ercot.json|04", "filecalc|avail_mean|mixplus/ercot.json|2025|monsoon|wind", "filecalc|hist_mwh|mix_history.json|Texas|2024|wind",
    "filecalc|day_peak|mix/ercot.json|2026-09|coal", "filecalc|toString|mix/ercot.json|04|2025", "file|mix/ercot.json|months.2026-09.days_held", "filecalc",
    // session 1414: the clean files' cleanest and dirtiest hour, a month of a year on clean/<grid>.json only
    "filecalc|clean_day_max|clean/ercot.json|2025", "filecalc|clean_day_max|clean/ercot.json|2025-13", "filecalc|clean_day_min|mix/ercot.json|2025-07", "filecalc|clean_day_min|clean/ercot.json|2025-07|x",
    // session 1415: the months the carbon chart leaves out, a variable of carbon_left_out.json only
    "filecalc|carbon_left_out_n|clean/ercot.json|intensity_generation", "filecalc|carbon_left_out_n|carbon_left_out.json|co2", "filecalc|carbon_left_out_n|carbon_left_out.json"]) assert.equal(FC.filecalcParts(bad), null, bad);
  assert.deepEqual(FC.filecalcParts("filecalc|clean_day_max|clean/ercot.json|2025-07"), { fn: "clean_day_max", file: "clean/ercot.json", args: ["2025-07"] });
  assert.deepEqual(FC.filecalcParts("filecalc|carbon_left_out_n|carbon_left_out.json|intensity_demand"), { fn: "carbon_left_out_n", file: "carbon_left_out.json", args: ["intensity_demand"] });
  // the functions check-filecalc.mjs knows are the ones lib/mixViewCalc.ts names (its words, the tip)
  assert.deepEqual(Object.keys(FC.SPEC).sort(), Object.keys(calc.FILECALC).sort());
  assert.equal(calc.filecalcKey("duck_low", "mix/pjm.json", ["07", "2024"]), "filecalc|duck_low|mix/pjm.json|07|2024");
});

test("a key's value is the page's figure, by the page's function, on every case of the files", () => {
  let n = 0;
  for (const g of GRIDS) {
    const m = read(`mix/${g}.json`), file = `mix/${g}.json`;
    for (const cal of ["01", "04", "07", "10"]) for (const y of mix.acrossYears(m, cal)) {
      assert.equal(value(`filecalc|duck_solar_peak|${file}|${cal}|${y.year}`), y.solarPeak?.value, `${g} ${cal} ${y.year} solar`);
      assert.equal(value(`filecalc|duck_low|${file}|${cal}|${y.year}`), y.low?.value, `${g} ${cal} ${y.year} low`);
      assert.equal(value(`filecalc|duck_evening|${file}|${cal}|${y.year}`), y.evening?.value, `${g} ${cal} ${y.year} evening`);
      assert.equal(value(`filecalc|duck_ramp|${file}|${cal}|${y.year}`), y.ramp ?? undefined, `${g} ${cal} ${y.year} ramp`);
      n += 4;
    }
    for (const period of [...Object.keys(m.months), ...Object.keys(m.years)]) for (const src of ["solar", "wind"]) {
      assert.equal(value(`filecalc|day_peak|${file}|${period}|${src}`), mix.highest(mix.periodOf(m, period).avg[src] ?? [])?.value, `${g} ${period} ${src}`);
      n++;
    }
    const p = read(`mixplus/${g}.json`);
    for (const y of Object.keys(p.availability)) for (const s of Object.keys(p.availability[y])) for (const f of p.av_fuels) {
      const v = p.availability[y][s][f];
      if (!v) continue;
      assert.equal(value(`filecalc|avail_mean|mixplus/${g}.json|${y}|${s}|${f}`), OLD.mean(v));
      assert.equal(value(`filecalc|avail_min|mixplus/${g}.json|${y}|${s}|${f}`), OLD.min(v));
      assert.equal(value(`filecalc|avail_max|mixplus/${g}.json|${y}|${s}|${f}`), OLD.max(v));
      n += 3;
    }
  }
  for (const s of ["US", "TX", "CA"]) for (const y of Object.keys(HISTORY.states[s])) for (const f of HISTORY.fuels) {
    assert.equal(value(`filecalc|hist_share|mix_history.json|${s}|${y}|${f}`), OLD.share(s, y, f) ?? undefined, `${s} ${y} ${f}`);
    assert.equal(value(`filecalc|hist_mwh|mix_history.json|${s}|${y}|${f}`), OLD.mwh(s, y, f) ?? undefined, `${s} ${y} ${f}`);
    n += 2;
  }
  // session 1414: the cleanest and the dirtiest hour of every month of every clean file, against the expression that stood
  // in CleanView (lib/clean.ts dayOf, its nulls filtered, then Math.max and Math.min when an hour is held)
  for (const g of GRIDS) {
    const f = read(`clean/${g}.json`);
    for (const m of [...Object.keys(f.months), "1999-01"]) {
      const d = clean.dayOf(f, m).filter((x) => x !== null);
      assert.deepEqual(calc.cleanDayHeld(f, m), d, `${g} ${m} the day held`);
      assert.equal(value(`filecalc|clean_day_max|clean/${g}.json|${m}`), d.length ? Math.max(...d) : undefined, `${g} ${m} max`);
      assert.equal(value(`filecalc|clean_day_min|clean/${g}.json|${m}`), d.length ? Math.min(...d) : undefined, `${g} ${m} min`);
      n += 2;
    }
  }
  // session 1415: the months the Clean tab's "Monthly since 2018" leaves out, for both variables, against the list the page
  // writes after it (lib/carbonLeftOut.ts carbonLeftOutMonths, on the same committed file)
  for (const v of ["intensity_generation", "intensity_demand"]) {
    assert.equal(value(`filecalc|carbon_left_out_n|carbon_left_out.json|${v}`), LEFT_OUT.carbonLeftOutMonths(v).length, v);
    n++;
  }
  assert.ok(n > 3000, `${n} keys`);
  // a case the file does not hold has no value (the page draws its placeholder and writes no key)
  assert.equal(value("filecalc|duck_ramp|mix/ercot.json|04|1999"), undefined);
  assert.equal(value("filecalc|day_peak|mix/ercot.json|1999-04|solar"), undefined);
  assert.equal(value("filecalc|hist_share|mix_history.json|ZZ|2024|wind"), undefined);
  assert.equal(value("filecalc|avail_mean|mixplus/ercot.json|1999|all|wind"), undefined);
});

/** check-values' rule for a fmt| figure (readOne): the value recomputed within a relative 1e-9 of the page's raw value,
 *  and the page's text exactly that value written in the key's form. */
function passes(check, raw, text) {
  const f = FMT.fmtParts(check);
  const p = FC.filecalcParts(f.inner);
  const t = FC.filecalcValueWith(LIBS, p, read(p.file));
  const same = t !== undefined && Math.abs(Number(t) - Number(raw)) < 1e-9 * Math.max(1, Math.abs(Number(t)));
  return same && text === FMT.formText(f.form, t);
}

test("a right value and text pass check-values' rule; a wrong value or a wrong text does not", async () => {
  const y = mix.acrossYears(read("mix/ercot.json"), "04").at(-1);
  const k = `fmt|n0|filecalc|duck_ramp|mix/ercot.json|04|${y.year}`;
  assert.ok(passes(k, String(y.ramp), FMT.formText("n0", y.ramp)), "right");
  assert.ok(!passes(k, String(y.ramp + 1), FMT.formText("n0", y.ramp + 1)), "a wrong value");
  assert.ok(!passes(k, String(y.ramp), FMT.formText("n0", y.ramp + 1000)), "a wrong text");
  const h = calc.historyCell(HISTORY, "TX", "2024", "wind");
  const hk = "fmt|n1|filecalc|hist_share|mix_history.json|TX|2024|wind";
  assert.ok(passes(hk, String(h.share), FMT.formText("n1", h.share)));
  assert.ok(!passes(hk, String(calc.historyCell(HISTORY, "TX", "2023", "wind").share), FMT.formText("n1", h.share)), "another year's share");
  // and check-filecalc's own loader (the one check-values uses, no library given) gives the same value
  assert.equal(await FC.filecalcValue(FC.filecalcParts(k.slice("fmt|n0|".length)), read("mix/ercot.json")), y.ramp);
});

// ---- 3. the views, drawn

const KEY = /<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)<\/span>/g;
const decode = (s) => s.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#x27;/g, "'");
const htmlOf = (el) => renderToStaticMarkup(el);
const keysOf = (html) => [...html.matchAll(KEY)].map((m) => ({ check: decode(m[1]), raw: decode(m[2]), text: decode(m[3].replace(/<!-- -->/g, "").replace(/<[^>]+>/g, "")).trim() }));
const calcKeys = (html) => keysOf(html).filter((k) => FMT.fmtParts(k.check) && FC.filecalcParts(FMT.fmtParts(k.check).inner));
function holds(k) {
  const f = FMT.fmtParts(k.check);
  const v = value(f.inner);
  assert.equal(typeof v, "number", `${k.check}: a value`);
  assert.ok(Math.abs(v - Number(k.raw)) <= 1e-9 * Math.max(1, Math.abs(v)), `${k.check}: file ${v}, page ${k.raw}`);
  assert.equal(k.text, FMT.formText(f.form, v), `${k.check}: the text`);
}
const counts = {};

test("the duck view keys every figure of each grid's table by year, the old figures, and its hours stay words", () => {
  for (const g of GRIDS) {
    const c = choiceOf({ view: "duck", grids: g });
    const html = htmlOf(createElement(V.DuckView, { c }));
    const ks = calcKeys(html);
    ks.forEach(holds);
    const cal = c.cal ?? "04", m = read(`mix/${g}.json`), want = new Map();
    for (const y of mix.acrossYears(m, cal)) {
      if (y.solarPeak && y.solarPeak.value > 0) want.set(`fmt|n0|filecalc|duck_solar_peak|mix/${g}.json|${cal}|${y.year}`, y.solarPeak.value);
      if (y.low) want.set(`fmt|n0|filecalc|duck_low|mix/${g}.json|${cal}|${y.year}`, y.low.value);
      if (y.evening) want.set(`fmt|n0|filecalc|duck_evening|mix/${g}.json|${cal}|${y.year}`, y.evening.value);
      if (y.ramp !== null) want.set(`fmt|n0|filecalc|duck_ramp|mix/${g}.json|${cal}|${y.year}`, y.ramp);
    }
    assert.deepEqual(new Map(ks.map((k) => [k.check, Number(k.raw)])), want, g);
    const days = keysOf(html).filter((k) => k.check.includes("days_held"));
    assert.equal(days.length, mix.acrossYears(m, cal).length, `${g} days held`);
    assert.ok(html.includes(`id="${mixViewAnchor("duckYears", 0, g)}"`) && html.includes('data-grid-method="mix-views"') && html.includes(`data-grid-file="grid_duck_${g}"`), `${g}: anchor, method, file`);
    counts[`duck ${g}`] = ks.length + days.length;
  }
  // two grids: the second grid's table takes the anchor and its grid
  const two = htmlOf(createElement(V.DuckView, { c: choiceOf({ view: "duck", grids: "ercot,caiso" }) }));
  assert.ok(two.includes(`id="duck-by-year"`) && two.includes(`id="duck-by-year-caiso"`));
});

test("the average day keys solar and wind at their peak by lib/mix2.ts highest, for the period in view", () => {
  for (const g of GRIDS) {
    const c = choiceOf({ view: "day", grids: g });
    const html = htmlOf(createElement(V.DayView, { c }));
    const ks = calcKeys(html);
    ks.forEach(holds);
    const m = read(`mix/${g}.json`), period = m.upto, p = mix.periodOf(m, period);
    const want = ["solar", "wind"].filter((s) => (mix.highest(p.avg[s] ?? [])?.value ?? 0) > 0).map((s) => `fmt|n0|filecalc|day_peak|mix/${g}.json|${period}|${s}`);
    assert.deepEqual(ks.map((k) => k.check), want, g);
    for (const a of ["dayShares", "dayPeak"]) assert.ok(html.includes(`id="${MIX_VIEW_ANCHOR[a]}"`), `${g} ${a}`);
    assert.equal(html.split('data-grid-method="mix-views"').length - 1, 2, `${g}: two method lines`);
    assert.ok(html.includes('data-grid-file="grid_mixday_all_shares"') && html.includes('data-grid-file="grid_mixday_all_peak"'), `${g} files`);
    counts[`day ${g}`] = ks.length;
  }
});

test("the history keys every share and million MWh of each state's table, the old figures", () => {
  for (const states of ["US", "TX,CA", "NY,FL,WA,IL"]) {
    const c = choiceOf({ view: "history", states });
    const html = htmlOf(createElement(V.HistoryView, { c }));
    const ks = calcKeys(html);
    ks.forEach(holds);
    let want = 0;
    const st = states.split(",");
    const years = [...new Set(st.flatMap((s) => Object.keys(HISTORY.states[s]).filter((y) => HISTORY.states[s][y].months === 12)))].sort();
    const marks = [years[0], "2010", "2020", years.at(-1)].filter((y, i, a) => y && a.indexOf(y) === i && years.includes(y));
    for (const s of st) for (const f of HISTORY.fuels.filter((f) => marks.some((y) => (HISTORY.states[s][y]?.[f] ?? 0) !== 0))) for (const y of marks) {
      const share = OLD.share(s, y, f), mwh = OLD.mwh(s, y, f);
      if (share !== null) { want++; assert.ok(ks.some((k) => k.check === `fmt|n1|filecalc|hist_share|mix_history.json|${s}|${y}|${f}` && Number(k.raw) === share), `${s} ${y} ${f} share`); }
      if (mwh !== null) { want++; assert.ok(ks.some((k) => k.check === `fmt|n1|filecalc|hist_mwh|mix_history.json|${s}|${y}|${f}` && Number(k.raw) === mwh), `${s} ${y} ${f} mwh`); }
    }
    assert.equal(ks.length, want, states);
    st.forEach((s, i) => assert.ok(html.includes(`id="${mixViewAnchor("historyShares", i, s.toLowerCase())}"`) && html.includes(`data-grid-file="grid_history_${s.toLowerCase()}"`), `${s}: anchor, file`));
    counts[`history ${states}`] = ks.length;
  }
});

test("availability keys the mean, lowest and highest hour of every source held, the old figures", () => {
  for (const g of GRIDS) {
    const c = choiceOf({ view: "supply", grids: g });
    const html = htmlOf(createElement(V.SupplyView, { c }));
    const ks = calcKeys(html);
    ks.forEach(holds);
    const p = read(`mixplus/${g}.json`);
    const years = Object.keys(p.availability).sort();
    const year = years.filter((y) => p.availability[y]?.[c.season]).at(-2) ?? years.at(-1);
    const want = new Map();
    for (const f of p.av_fuels) {
      const v = p.availability[year]?.[c.season]?.[f];
      if (!v) continue;
      want.set(`fmt|n1|filecalc|avail_mean|mixplus/${g}.json|${year}|${c.season}|${f}`, OLD.mean(v));
      want.set(`fmt|n1|filecalc|avail_min|mixplus/${g}.json|${year}|${c.season}|${f}`, OLD.min(v));
      want.set(`fmt|n1|filecalc|avail_max|mixplus/${g}.json|${year}|${c.season}|${f}`, OLD.max(v));
    }
    assert.deepEqual(new Map(ks.map((k) => [k.check, Number(k.raw)])), want, g);
    for (const a of [MIX_VIEW_ANCHOR.supplyMean, MIX_VIEW_ANCHOR.supplyTight]) assert.ok(html.includes(`id="${a}"`), `${g} ${a}`);
    assert.ok(html.includes('data-grid-file="grid_supply_all_mean"') && html.includes(`data-grid-file="grid_supply_${g}_tight"`), `${g} files`);
    counts[`supply ${g}`] = ks.length;
  }
});

test("the counts of the figures keyed by this kind, by view", () => {
  console.log(`# keyed: ${JSON.stringify(counts)}`);
  assert.ok(Object.keys(counts).length >= 20);
});

// ---- 4. the scripts and the note know the kind

test("check-values reads the kind, check-methods names it, and the note names every function under the link's heading", () => {
  const cv = fs.readFileSync(path.join(here, "check-values.mjs"), "utf-8");
  assert.ok(cv.includes('if (p[0] === "filecalc") {'));
  // each method line links the method's constant (a link a visitor's page gates is drawn by SiteLink; the render test
  // scripts/test-grid-render.mjs reads the link on the page as the internal view draws it)
  const views = fs.readFileSync(path.join(here, "..", "components", "mix", "views.tsx"), "utf-8");
  assert.ok(views.includes("<SiteLink href={METHOD_MIX_VIEWS}>Method: the computed views, keyed</SiteLink>"));
  assert.ok(cv.includes("return FCALC.filecalcValue(f, dataFile(f.file));"));
  assert.deepEqual(CM.figures("fmt|n0|filecalc|duck_ramp|mix/ercot.json|04|2025"), [{ kind: "family", table: "filecalc", measure: "duck_ramp", id: "filecalc| duck_ramp" }]);
  assert.equal(CM.MEASURE_AT.filecalc, 1);
  const note = fs.readFileSync(path.join(ROOT, "docs", "methods", "generation_mix_hourly.md"), "utf-8");
  const html = render(note, "docs/methods/generation_mix_hourly.md");
  const id = METHOD_MIX_VIEWS.split("#")[1];
  assert.ok(html.includes(`id="${id}"`), `the note has the heading ${id}`);
  const sec = note.split("## The computed views, keyed (chain 107, 24 October 2026)")[1].split("\n## ")[0];
  const words = CM.noteWords(note);
  for (const fn of Object.keys(calc.FILECALC)) assert.ok(CM.named(words, CM.figures(`filecalc|${fn}|x`)[0]), `${fn} named`);
  for (const w of ["filecalc|", "lib/mixViewCalc.ts", "scripts/check-filecalc.mjs", "Decisions (chain 107"]) assert.ok(sec.includes(w), w);
});
