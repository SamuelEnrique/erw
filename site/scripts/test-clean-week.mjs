// Energy Research Warehouse (ERW) site, session 1403 (chain 100): the cleanest hours, live (lib/cleanWeek.ts,
// components/grid/CleanWeekPanel.tsx, the `live` of components/mix/views.tsx CleanView, MixClean's read). On a committed
// fixture of real rows (scripts/fixtures/clean_week.json: carbon_intensity_hourly, intensity_generation, ERCOT's,
// California's and MISO's newest days and ERCOT's two clock-change weeks, read with the anon key on 24 October 2026) and
// the committed files the view beside it draws (site/data/clean/<grid>.json): every key the panel writes is recomputed
// here the way scripts/check-values.mjs recomputes it (the table's rows of the key's entity, variable and range, then
// weekStat, or Math.max for series_max, or heldHours for series_n), and again by plain arithmetic. Needs no build, no
// server and no database.
//
//   node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-clean-week.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import * as W from "../lib/cleanWeek.ts";
import * as clean from "../lib/clean.ts";
import { heldHours } from "../lib/scarcityStrip.ts";
import { licenseHeldRow } from "../lib/license.ts";
import { heldCarbon, CARBON_HOURLY_TABLE } from "../lib/gridHeld.ts";
import { CAISO_JOIN } from "../lib/caisoJoin.ts";
import { choiceOf } from "../lib/mixpage.ts";
import { CleanWeekPanel } from "../components/grid/CleanWeekPanel.tsx";
import * as V from "../components/mix/views.tsx";
import { CLEAN_WEEK_ANCHOR, METHOD_CLEAN_WEEK, cleanWeekAnchor, GRID_ANCHOR, GRID_METHOD } from "../lib/gridAnchors.ts";
import { render } from "../lib/markdown.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.join(here, "..");
const ROOT = path.join(SITE, "..");
const FIX = JSON.parse(fs.readFileSync(path.join(here, "fixtures", "clean_week.json"), "utf-8"));
const H = 3_600_000;
const AT = new Date(FIX.read_at);
const FILE = (g) => JSON.parse(fs.readFileSync(path.join(SITE, "data", "clean", `${g}.json`), "utf-8"));
const GRIDS = Object.fromEntries(JSON.parse(fs.readFileSync(path.join(ROOT, "docs", "grids", "grids.json"), "utf-8")).grids.map((g) => [g.slug, g]));
/** A part of the fixture as the live set's series rows. */
const rowsOf = (part, entity) => FIX[part].rows[`${entity}|intensity_generation`].map(([ts_utc, value]) => ({ entity, variable: "intensity_generation", ts_utc, value }));
const ALL = Object.entries(FIX.week.rows).flatMap(([k, rs]) => { const [entity, variable] = k.split("|"); return rs.map(([ts_utc, value]) => ({ entity, variable, ts_utc, value })); });
const text = (h) => h.replace(/<!-- -->/g, "").replace(/<[^>]+>/g, "").replace(/&#x27;/g, "'").replace(/&amp;/g, "&");

/** A key recomputed as scripts/check-values.mjs does: the rows of its entity, variable and [start, end), then its rule. */
function truth(check, rows = ALL) {
  const [kind, table, variable, start, end, entity] = check.split("|");
  assert.equal(table, "carbon_intensity_hourly");
  const mine = rows.filter((r) => r.entity === entity && r.variable === variable && Date.parse(r.ts_utc) >= Date.parse(start) && Date.parse(r.ts_utc) < Date.parse(end));
  if (kind === "series_n") return heldHours(mine);
  if (kind === "series_max") return mine.length ? Math.max(...mine.map((r) => r.value)) : undefined;
  return W.weekStat(mine.map((r) => ({ ts_utc: r.ts_utc, value: r.value })), kind.slice("series_".length), start, end);
}

/** The client components a tree draws (the tsx loader's stubs), each with its props. */
function clientsOf(node, out = []) {
  if (!node || typeof node !== "object") return out;
  if (Array.isArray(node)) { for (const x of node) clientsOf(x, out); return out; }
  const p = node.props ?? {};
  if (typeof node.type === "function" && node.type.__erwClient) { out.push({ name: node.type.__erwClient.split("#").pop(), props: p }); return clientsOf(p.children, out); }
  if (typeof node.type === "function") return clientsOf(node.type(p), out);
  return clientsOf(p.children, out);
}
/** Every href of a tree (a function component that is not a client stub called with its props). */
function linksOf(node, out = []) {
  if (!node || typeof node !== "object") return out;
  if (Array.isArray(node)) { for (const x of node) linksOf(x, out); return out; }
  const p = node.props ?? {};
  if (typeof p.href === "string") out.push(p.href);
  if (typeof node.type === "function" && !node.type.__erwClient) return linksOf(node.type(p), out);
  return linksOf(p.children, out);
}
const panelOf = (grid, read, week, year) => createElement(CleanWeekPanel, { grid, name: { ercot: "ERCOT", caiso: "CAISO", miso: "MISO" }[grid], i: 0, read, week, file: FILE(grid), year });

test("the table, its entities and the clocks: the site's own, public on the day, the committed view's time zone", () => {
  for (const [g, e] of Object.entries(W.CARBON_ENTITY)) {
    assert.equal(GRIDS[g].entity, e, g);
    assert.equal(licenseHeldRow(W.CARBON_TABLE, e, AT), false, `${g} is public on ${FIX.read_at}`);
    assert.equal(heldCarbon(g, AT), null, g);
    // the committed view's clock (its file's tz) is grids.json's for six grids; MISO's grids.json says Etc/GMT+5 (the note says why the file's is used)
    if (g === "miso") { assert.equal(FILE(g).tz, "America/Chicago"); assert.equal(GRIDS[g].tz, "Etc/GMT+5"); } else assert.equal(FILE(g).tz, GRIDS[g].tz, g);
  }
  assert.equal(CARBON_HOURLY_TABLE, W.CARBON_TABLE);
  assert.equal(W.CLEAN_VARIABLE, "intensity_generation");
  // the Clean tab's "The last 24 hours" draws the same variable (components/grid/Emissions.tsx)
  assert.ok(fs.readFileSync(path.join(SITE, "components", "grid", "Emissions.tsx"), "utf-8").includes(`of(i.entity, "intensity_generation")`));
});

test("the window: the 7 local days to the newest whole local day, on real rows (ERCOT, California's missing day)", () => {
  const w = W.cleanWeek(rowsOf("week", "eia930:ERCO"), "eia930:ERCO", "America/Chicago");
  assert.deepEqual(w.days, ["2026-10-13", "2026-10-14", "2026-10-15", "2026-10-16", "2026-10-17", "2026-10-18", "2026-10-19"]);
  assert.equal(W.isoZ(w.t0), "2026-10-13T05:00:00Z");
  assert.equal(W.isoZ(w.t1), "2026-10-20T05:00:00Z");
  assert.equal(w.of, 168);
  assert.equal(w.n.raw, 168);
  // the table's newest hour, 2026-10-20 23:00 UTC, is 18:00 CDT: the 20th is not whole, so it is not a row
  assert.equal(FIX.week.rows["eia930:ERCO|intensity_generation"].at(-1)[0], "2026-10-20T23:00:00Z");
  const c = W.cleanWeek(rowsOf("week", "eia930:CISO"), "eia930:CISO", "America/Los_Angeles");
  assert.equal(W.isoZ(c.t0), "2026-10-13T07:00:00Z");
  assert.equal(c.n.raw, 144);
  assert.deepEqual(c.cells[2], Array(24).fill(null), "no hour of Thursday 15 October (Pacific) is held: a row of blanks, never filled");
  assert.match(c.tips[2][9], /^Thu 15 Oct, 09:00 PDT \(2026-10-15 16:00 UTC\): not held$/);
  assert.equal(W.cleanWeek([], "eia930:ERCO", "America/Chicago"), null);
  // an hour written twice is held once (its last row): made inside this test only
  const rs = rowsOf("week", "eia930:ERCO");
  assert.deepEqual(W.hourValues([...rs, { ...rs[0] }]), W.hourValues(rs));
});

test("each cell is its hour's row, its hover the day, the local hour and the kg per MWh", () => {
  const rows = rowsOf("week", "eia930:ERCO");
  const w = W.cleanWeek(rows, "eia930:ERCO", "America/Chicago");
  const at = new Map(rows.map((r) => [Date.parse(r.ts_utc), r.value]));
  for (let t = w.t0, k = 0; t < w.t1; t += H, k++) {
    const r = Math.floor(k / 24), h = k % 24;   // a week of 24-hour days: row by row, hour by hour
    assert.equal(w.cells[r][h], at.get(t), W.isoZ(t));
  }
  assert.match(w.tips[3][16], /^Fri 16 Oct, 16:00 CDT \(2026-10-16 21:00 UTC\): 131\.2 kg CO2\/MWh$/);
});

test("the clocks: a week with 25 hours on 2 November 2025 and one with 23 on 8 March 2026 (ERCOT's real rows)", () => {
  const f = W.cleanWeek(rowsOf("fall", "eia930:ERCO"), "eia930:ERCO", "America/Chicago");
  assert.equal(f.of, 169);
  assert.equal(f.n.raw, 169);
  const d = f.days.indexOf("2025-11-02");
  assert.ok(d >= 0);
  assert.match(f.tips[d][1], /^Sun 2 Nov, 01:00 CDT \(2025-11-02 06:00 UTC\): [\d.]+ kg CO2\/MWh; then Sun 2 Nov, 01:00 CST \(2025-11-02 07:00 UTC\): [\d.]+ kg CO2\/MWh$/);
  assert.equal(f.cells[d][1], rowsOf("fall", "eia930:ERCO").find((r) => r.ts_utc === "2025-11-02T06:00:00Z").value, "the cell draws the first of the two");
  const s = W.cleanWeek(rowsOf("spring", "eia930:ERCO"), "eia930:ERCO", "America/Chicago");
  assert.equal(s.of, 167);
  const e = s.days.indexOf("2026-03-08");
  assert.equal(s.cells[e][2], null);
  assert.equal(s.tips[e][2], "Sun 8 Mar, 02:00: no such hour (the clocks went forward)");
  for (const wk of [f, s]) for (const fig of [wk.n, wk.min.fig, wk.max.fig, wk.mean]) assert.equal(truth(fig.check, rowsOf(wk === f ? "fall" : "spring", "eia930:ERCO")), fig.raw, fig.check);
});

test("every key recomputed as check-values does, and by plain arithmetic (ERCOT, California, MISO)", () => {
  for (const [e, tz] of [["eia930:ERCO", "America/Chicago"], ["eia930:CISO", "America/Los_Angeles"], ["eia930:MISO", "America/Chicago"]]) {
    const w = W.cleanWeek(ALL, e, tz);
    const k = `carbon_intensity_hourly|intensity_generation|${W.isoZ(w.t0)}|${W.isoZ(w.t1)}|${e}`;
    assert.equal(w.n.check, `series_n|${k}`);
    assert.equal(w.min.fig.check, `series_min|${k}`);
    assert.equal(w.max.fig.check, `series_max|${k}`);
    assert.equal(w.mean.check, `series_mean|${k}`);
    for (const fig of [w.n, w.min.fig, w.max.fig, w.mean]) assert.equal(truth(fig.check), fig.raw, fig.check);
    const vs = ALL.filter((r) => r.entity === e && Date.parse(r.ts_utc) >= w.t0 && Date.parse(r.ts_utc) < w.t1).map((r) => r.value);
    let lo = Infinity, hi = -Infinity, sum = 0;
    for (const v of vs) { if (v < lo) lo = v; if (v > hi) hi = v; sum += v; }
    assert.equal(w.n.raw, vs.length);
    assert.equal(w.min.fig.raw, lo);
    assert.equal(w.max.fig.raw, hi);
    assert.ok(Math.abs(w.mean.raw - sum / vs.length) < 1e-9);
    // the hour named is the row's, and the mark stands on its cell
    assert.equal(w.cells[w.min.at[0]][w.min.at[1]], lo);
    assert.equal(w.min.local, w.min.at[1]);
  }
  const w = W.cleanWeek(ALL, "eia930:ERCO", "America/Chicago");
  assert.equal(w.min.fig.raw, 131.1905);
  assert.equal(W.hourWords(w.min.t, w.tz), "Fri 16 Oct, 16:00 CDT (2026-10-16 21:00 UTC)");
  assert.equal(w.max.fig.raw, 446.2754);
  assert.equal(W.weekStat([], "n", W.isoZ(w.t0), W.isoZ(w.t1)), 0);
  assert.equal(W.weekStat([], "min", W.isoZ(w.t0), W.isoZ(w.t1)), undefined);
  assert.throws(() => W.weekStat(ALL, "median", W.isoZ(w.t0), W.isoZ(w.t1)));
});

test("the line against the committed average day: hours only, the month in the year in view, the join, a held file", () => {
  const f = FILE("ercot"), year = clean.defaultYear(f);
  const w = W.cleanWeek(ALL, "eia930:ERCO", f.tz);
  const m = W.refMonth(Object.keys(f.months), w.days[6], year);
  assert.equal(m, `${year}-10`);
  assert.equal(W.refMonth(["2024-10", "2025-10"], "2026-10-19", "2023"), "2025-10", "the newest year holding the month when the year in view does not");
  assert.equal(W.refMonth(["2025-09"], "2026-10-19", "2025"), null);
  const cl = clean.cleanestOf(f, m);
  const line = W.compareWords(w, { month: m, cleanest: cl, dirtiest: W.dirtiestOf(clean.dayOf(f, m)), hoursName: clean.hoursName(cl) });
  assert.equal(cl.includes(16), false);
  assert.match(line, /^Against the committed average day of October \d{4}: the week's cleanest hour, 16:00, is not one of October \d{4}'s four cleanest hours of the average day \([^)]+\); its dirtiest hour, 23:00, (is|is not) October \d{4}'s dirtiest hour of the average day/);
  assert.ok(!/\d+\.\d/.test(line), "no figure in the line, only hours");
  assert.equal(W.dirtiestOf([3, 1, null, 1]), 1);
  assert.equal(W.dirtiestOf([null, null]), null);
  // drawn: ERCOT's line; California's adds the join (the month before it, the week after); MISO's committed file is held
  const ercot = renderToStaticMarkup(panelOf("ercot", { ok: true, data: ALL }, w, year));
  assert.ok(text(ercot).includes(line));
  const cf = FILE("caiso"), cw = W.cleanWeek(ALL, "eia930:CISO", cf.tz);
  assert.ok(Date.parse(`${W.refMonth(Object.keys(cf.months), cw.days[6], clean.defaultYear(cf))}-01T00:00:00Z`) < Date.parse(CAISO_JOIN));
  const caiso = text(renderToStaticMarkup(panelOf("caiso", { ok: true, data: ALL }, cw, clean.defaultYear(cf))));
  assert.match(caiso, /California across the join of 16 December 2025 is two series: the week rests on CAISO's own supply by fuel, October \d{4}'s average day on EIA-930's\./);
  assert.equal(licenseHeldRow(clean.SUMMARY, "iso:miso", AT), true);
  const mw = W.cleanWeek(ALL, "eia930:MISO", "America/Chicago");
  const miso = renderToStaticMarkup(panelOf("miso", { ok: true, data: ALL }, mw, "2025"));
  assert.ok(miso.includes('data-cleanweek-compare="held"'));
  assert.ok(text(miso).includes("Against the committed average day: license needed"));
  assert.ok(!/four cleanest hours/.test(text(miso)), "no hour of a held file is named");
  assert.equal((miso.match(/data-check=/g) ?? []).length, 4, "the week itself is drawn: its four figures");
});

test("the panel drawn: its name, anchor, the chart's cells and hover, four keyed figures, its file and its method", () => {
  const w = W.cleanWeek(ALL, "eia930:ERCO", "America/Chicago");
  const el = panelOf("ercot", { ok: true, data: ALL }, w, "2024");
  const html = renderToStaticMarkup(el);
  assert.ok(html.includes(`id="${CLEAN_WEEK_ANCHOR}"`));
  assert.ok(html.includes('data-grid-panel="grid_cleanweek_ercot"'));
  const checks = [...html.matchAll(/data-check="([^"]+)"/g)].map((x) => x[1].replace(/&amp;/g, "&"));
  assert.deepEqual([...new Set(checks)].sort(), [w.max.fig.check, w.mean.check, w.min.fig.check, w.n.check].sort());
  assert.ok(html.includes('download="erw_grid_cleanweek_ercot.csv"'));
  assert.ok(text(html).includes("Fri 16 Oct, 16:00 CDT (2026-10-16 21:00 UTC), marked"));
  const heat = clientsOf(el).find((c) => c.name === "HeatChart");
  assert.ok(heat, "the shared HeatChart");
  assert.deepEqual(heat.props.cells, w.cells);
  assert.deepEqual(heat.props.tips, w.tips);
  assert.deepEqual(heat.props.marks, [w.min.at]);
  assert.equal(heat.props.rows.length, 7);
  assert.equal(heat.props.cols.length, 24);
  assert.deepEqual(heat.props.legend, ["cleaner", "dirtier"], "no unkeyed number in the legend");
  assert.ok(linksOf(el).includes(METHOD_CLEAN_WEEK));
  assert.equal(cleanWeekAnchor(1, "caiso"), "clean-week-caiso");
  assert.ok(!Object.values(GRID_ANCHOR).includes(CLEAN_WEEK_ANCHOR) && !Object.values(GRID_METHOD).includes(METHOD_CLEAN_WEEK), "outside the 17 pinned panels");
});

test("a failed read: could not be read, no figure; no whole day: said in words; the committed view as before without a caller", () => {
  for (const reason of ["HTTP 500", "statement timeout (57014)"]) {
    const html = renderToStaticMarkup(panelOf("ercot", { ok: false, reason }, null, "2024"));
    assert.ok(html.includes('data-grid-panel="grid_cleanweek_ercot"'));
    assert.ok(html.includes('data-cleanweek-unread="carbon_intensity_hourly"'));
    assert.ok(text(html).includes("could not be read"));
    assert.ok(html.includes(reason.replace(/\(/g, "(")));
    assert.ok(!html.includes("data-check="));
  }
  const none = renderToStaticMarkup(panelOf("ercot", { ok: true, data: [] }, null, "2024"));
  assert.ok(none.includes('data-cleanweek-none="1"') && !none.includes("data-check="));
  // CleanView with no caller's `live` draws no week; with it, the week stands after the grid's cleanest hours, and under a held grid's block too
  const c = choiceOf({ view: "clean", grids: "ercot,miso" });
  const before = renderToStaticMarkup(createElement(V.CleanView, { c }));
  assert.ok(!before.includes("grid_cleanweek"));
  const live = (g, year) => createElement("div", { "data-grid-panel": `grid_cleanweek_${g}`, "data-year": year });
  const after = renderToStaticMarkup(createElement(V.CleanView, { c, live }));
  const at = after.indexOf("grid_cleanweek_ercot");
  assert.ok(at > after.indexOf("ERCOT: the cleanest hours of the average day") && at < after.indexOf("ERCOT: moving a flat load into the cleanest hours"));
  assert.ok(after.includes("grid_cleanweek_miso"), "a held grid's committed block reads license needed; the week, public, stands under it");
  assert.equal(after.replace(/<section class="mb-8"><h2[^>]*>[^<]*the cleanest hours of the last 7 days held<\/h2><div data-grid-panel="grid_cleanweek_\w+" data-year="\d+"><\/div><\/section>/g, "").replace(/<div><section/g, "<section").replace(/<\/section><\/div>/g, "</section>"),
    before.replace(/<div><section/g, "<section").replace(/<\/section><\/div>/g, "</section>"), "the view is the same with the weeks taken out");
});

test("check-values and check-methods know the two kinds; the note names the figures and its heading is the link's", () => {
  const cv = fs.readFileSync(path.join(here, "check-values.mjs"), "utf-8");
  assert.ok(cv.includes('if (p[0] === "series_min" || p[0] === "series_mean") {'));
  assert.ok(cv.includes('return W.weekStat(rows, p[0].slice("series_".length), start, end);'));
  const cm = fs.readFileSync(path.join(here, "check-methods.mjs"), "utf-8");
  assert.ok(cm.includes("series_min: [1, 2], series_mean: [1, 2],"));
  const note = fs.readFileSync(path.join(ROOT, "docs", "methods", "generation_mix_hourly.md"), "utf-8");
  const html = render(note, "docs/methods/generation_mix_hourly.md");
  const id = METHOD_CLEAN_WEEK.split("#")[1];
  assert.ok(html.includes(`id="${id}"`), `the note has the heading ${id}`);
  const sec = note.split("## The cleanest hours, live (chain 100, 24 October 2026)")[1].split("\n## ")[0];
  for (const w of ["carbon_intensity_hourly", "intensity_generation", "series_n|", "series_min|", "series_max|", "series_mean|", "grid_cleanweek_<grid>", "caisoJoinDay()", "Decisions (chain 100, session 1403)"]) assert.ok(sec.includes(w), w);
  for (const f of ["lib/cleanWeek.ts", "components/grid/CleanWeekPanel.tsx", "scripts/test-clean-week.mjs"]) assert.ok(!fs.readFileSync(path.join(SITE, f), "utf-8").includes(String.fromCharCode(0x2014)), f);
});
