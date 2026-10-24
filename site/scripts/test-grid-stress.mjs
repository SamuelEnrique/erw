// Energy Research Warehouse (ERW) site, session 1168 (chain 078): "How hard the system works" on the Grid tool's Mix tab,
// year by year (lib/gridStress.ts, components/mix/views.tsx StressView). Needs no build, no server and no database: the
// committed files of site/data/stress/ and the view drawn on the server through the tsx loader (the client charts stubbed,
// so the props the view hands them are read as they are).
//
//   node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-stress.mjs
//
// 1. lib/gridStress.ts: the values are the file's figures, picked (a gap where the file holds none); each note says the
//    year's figures behind a point, as the page's tables write them; the tightest hours' lines are the fuels' shares.
// 2. The four lines of what each chart is not are in docs/methods/grid_stress.md word for word, and the link's anchor is
//    that section's heading, by the site's rule for a heading's id (lib/markdown.ts headingSlugs).
// 3. The view, drawn for every grid (none is held: grid_stress_yearly is public): four charts with a point a year, each
//    with its notes and its line, and a link to the line under each; the ramp's series as they stood.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import * as GS from "../lib/gridStress.ts";
import * as stress from "../lib/stress.ts";
import { licenseHeldRow } from "../lib/license.ts";
import { choiceOf } from "../lib/mixpage.ts";
import * as V from "../components/mix/views.tsx";

const here = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(here, "..", "..");
const read = (g) => JSON.parse(fs.readFileSync(path.join(here, "..", "data", "stress", `${g}.json`), "utf-8"));
const GRIDS = ["caiso", "ercot", "isone", "miso", "nyiso", "pjm", "spp"];

// ---- 1. the pure functions

test("the values are the file's figures over the years, a gap where a year or a figure is not held", () => {
  const fs7 = GRIDS.map(read);
  const years = GS.yearsOfAll(fs7);
  assert.deepEqual(years, [...new Set(fs7.flatMap((f) => Object.keys(f.years)))].sort());
  for (const f of fs7) {
    for (const k of ["net_load_min_share_of_peak_pct", "calm_longest_hours", "evening_ramp_max_share_of_peak_pct"]) {
      const v = GS.valuesOf(f, years, k);
      assert.equal(v.length, years.length);
      years.forEach((y, i) => assert.equal(v[i], f.years[y] ? stress.get(f, y, k) : null, `${f.grid} ${y} ${k}`));
    }
  }
  const spp = read("spp"), caiso = read("caiso");
  assert.equal(spp.years["2019"], undefined);   // SPP 2019 and 2026 are not written (the note: stale reports)
  assert.equal(GS.fig(spp, "2019", "net_load_min_mw"), null);
  assert.equal(GS.valuesOf(spp, years, "net_load_min_mw")[years.indexOf("2019")], null);
  assert.equal(GS.fig(caiso, "2025", "nothing_here"), null);
  assert.equal(GS.yearName(read("ercot"), "2025"), "2025");
  assert.equal(GS.yearName(read("ercot"), "2026"), "2026 to date");
});

test("each note says the year's figures as the tables write them (ERCOT and CAISO, 2025 and 2026)", () => {
  const e = read("ercot"), c = read("caiso");
  assert.equal(GS.rampNote(e, "2025"), "in one hour 15,940 MW, starting 19 January 2025, 16:00; over three hours 27,450 MW; peak demand 83,597 MW");
  assert.equal(GS.netLoadNote(e, "2025"), "9,586 MW, 2 March 2025, 09:00; peak demand 83,597 MW");
  assert.equal(GS.tightNote(e, "2025"), "mean net load in the 100 tightest hours 63,597 MW");
  assert.equal(GS.calmNote(e, "2025"), "18 hours, beginning 27 January 2025, 17:00; 322,188 MWh missing; 37.8 hours of the battery fleet at full power; 592 dark, calm hours in the year");
  assert.ok(GS.rampNote(e, "2026").endsWith("; the year to date"));
  assert.equal(GS.netLoadNote(c, "2026"), "-1,341 MW, 7 March 2026, 11:00; peak demand 49,959 MW; the year to date");
  for (const note of [GS.rampNote, GS.netLoadNote, GS.tightNote, GS.calmNote]) assert.equal(note(read("spp"), "2019"), null);
  // the figures in the notes are the file's, written as the tables write them (lib/mixpage.ts n0, lib/stress.ts when)
  for (const g of GRIDS) {
    const f = read(g);
    for (const y of stress.yearsOf(f)) {
      const mw = stress.get(f, y, "net_load_min_mw");
      if (mw !== null) assert.ok(GS.netLoadNote(f, y).startsWith(`${Math.round(mw).toLocaleString("en-US")} MW, ${stress.when(stress.at(f, y, "net_load_min_mw"), f.tz)}`), `${g} ${y}`);
      const h = stress.get(f, y, "calm_longest_hours");
      if (h !== null) assert.ok(GS.calmNote(f, y).startsWith(stress.span(h)), `${g} ${y}`);
    }
  }
});

test("several grids' notes are each grid's, named", () => {
  const e = read("ercot"), c = read("spp");
  const n = GS.notesOf([e, c], ["2019", "2025"], GS.netLoadNote);
  assert.equal(n[0], `ERCOT: ${GS.netLoadNote(e, "2019")}`);   // SPP holds no 2019: ERCOT's alone
  assert.equal(n[1], `ERCOT: ${GS.netLoadNote(e, "2025")}. SPP: ${GS.netLoadNote(c, "2025")}`);
  assert.deepEqual(GS.notesOf([e], ["2025"], GS.netLoadNote), [GS.netLoadNote(e, "2025")]);
  assert.deepEqual(GS.notesOf([c], ["2019"], GS.netLoadNote), [null]);
});

test("the tightest hours' lines are each fuel's share of capacity by year, hydro and storage as their one line", () => {
  for (const g of GRIDS) {
    const f = read(g), ys = stress.yearsOf(f), ls = GS.tightLines(f, ys);
    assert.ok(ls.length >= 4, g);
    assert.ok(!ls.some((l) => l.fuel === "hydro" || l.fuel === "storage"), `${g}: hydro and storage apart have no share`);
    for (const l of ls) ys.forEach((y, i) => assert.equal(l.values[i], stress.fuelRows(f, y).find((r) => r.fuel === l.fuel).share, `${g} ${l.fuel} ${y}`));
    assert.deepEqual(ls.map((l) => l.fuel), f.fuels.filter((x) => ls.some((l) => l.fuel === x)));   // the file's order
  }
  const e = read("ercot");
  assert.equal(GS.tightLines(e, ["2025"]).find((l) => l.fuel === "solar").values[0], 5.022);   // the note: 5.0 in 2025
});

// ---- 2. the lines and the method note

/** lib/markdown.ts headingSlugs, its rule for one heading (the text lower case, no punctuation but - and _, spaces as -). */
const slug = (text) => text.trim().toLowerCase().replace(/[^\p{L}\p{M}\p{N}\p{Pc}\- ]/gu, "").replace(/ /g, "-");

test("each chart's line is in the method note, word for word, under the heading the link opens", () => {
  const note = fs.readFileSync(path.join(ROOT, "docs", "methods", "grid_stress.md"), "utf-8").replace(/\r\n/g, "\n");
  const [page, anchor] = GS.STRESS_METHOD.split("#");
  assert.equal(page, "/data/methods/grid_stress");
  const heads = [...note.matchAll(/^#{1,6} (.+)$/gm)].map((m) => m[1]);
  const head = heads.find((h) => slug(h) === anchor);
  assert.equal(head, "What each chart is not (session 1168)");
  const section = note.slice(note.indexOf(`### ${head}`) + 4).split(/\n#{2,3} /)[0];
  for (const m of GS.MEASURES) {
    assert.ok(GS.NOT[m].length > 40, m);
    assert.ok(section.includes(GS.NOT[m]), `${m}: the line is in the section`);
  }
  // the two lines of "What the figures are not" kept in short: their opening words are that section's own
  const orig = note.slice(note.indexOf("## What the figures are not"), note.indexOf("## As built on 5 October 2026"));
  for (const words of ["Not what a plant could do.", "Not a reliability study.", "Not a sizing of storage.", "The definition of dark and calm is one line."]) assert.ok(orig.includes(words), words);
  assert.ok(GS.NOT.tight.startsWith("Not what a plant could do") && GS.NOT.calm.startsWith("Not a sizing of storage"));
  for (const m of GS.MEASURES) assert.ok(!GS.NOT[m].includes(String.fromCharCode(0x2014)), m);
});

// ---- 3. the view

/** The elements of a server render, the server components called, the client ones (stubbed) kept with their props. */
function walk(node, out = []) {
  if (node === null || node === undefined || typeof node !== "object") return out;
  if (Array.isArray(node)) { for (const n of node) walk(n, out); return out; }
  const t = node.type;
  if (typeof t === "function" && t.__erwClient && node.props?.["data-stress-not"]) { out.push({ name: "not", props: node.props }); return out; }   // next/link, stubbed
  if (typeof t === "function" && t.__erwClient) { out.push({ name: String(t.__erwClient).split("#").pop(), props: node.props }); walk(node.props?.children, out); return out; }
  if (typeof t === "function") return walk(t(node.props), out);
  if (node.props) {
    if (node.props["data-stress-not"]) out.push({ name: "not", props: node.props });
    walk(node.props.children, out);
  }
  return out;
}
const charts = (els) => els.filter((e) => e.name === "Lines" || e.name === "Bars");

test("every grid's view draws the four charts, a point a year, each with its notes and its line, and the link under each", () => {
  for (const g of GRIDS) {
    assert.equal(licenseHeldRow("grid_stress_yearly", `iso:${g}`), false, `${g}: the table is public`);
    const f = read(g), ys = stress.yearsOf(f);
    const els = walk(V.StressView({ c: choiceOf({ view: "stress", grids: g }) }));
    const byName = Object.fromEntries(charts(els).map((e) => [e.props.name, e]));
    assert.deepEqual(Object.keys(byName).sort(), ["erw-mix-calm-" + g, "erw-mix-netload", "erw-mix-ramp", "erw-mix-tight-" + g].sort(), g);
    const ramp = byName["erw-mix-ramp"];
    assert.equal(ramp.name, "Bars");
    assert.deepEqual(ramp.props.x, ys);
    // the ramp's series as they stood (session 133): the two shares, no digits set
    assert.deepEqual(ramp.props.series.map((s) => [s.name, s.values, s.digits]), [["In one hour", ys.map((y) => stress.get(f, y, "evening_ramp_max_share_of_peak_pct")), undefined],
      ["Over three hours", ys.map((y) => stress.get(f, y, "evening_ramp_3h_max_share_of_peak_pct")), undefined]]);
    assert.equal(ramp.props.unit, "% of peak demand");
    assert.deepEqual(ramp.props.notes, ys.map((y) => GS.rampNote(f, y)));
    const nl = byName["erw-mix-netload"];
    assert.deepEqual(nl.props.series.map((s) => s.values), [ys.map((y) => stress.get(f, y, "net_load_min_share_of_peak_pct"))]);
    assert.equal(nl.props.series[0].digits, 1);
    assert.deepEqual(nl.props.notes, ys.map((y) => GS.netLoadNote(f, y)));
    const tl = byName[`erw-mix-tight-${g}`];
    assert.deepEqual(tl.props.series.map((s) => s.values), GS.tightLines(f, ys).map((l) => l.values));
    assert.equal(tl.props.unit, "% of installed capacity");
    assert.deepEqual(tl.props.notes, ys.map((y) => GS.tightNote(f, y)));
    const cl = byName[`erw-mix-calm-${g}`];
    assert.deepEqual(cl.props.series[0].values, ys.map((y) => stress.get(f, y, "calm_longest_hours")));
    assert.equal(cl.props.unit, "hours");
    assert.deepEqual(cl.props.notes, ys.map((y) => GS.calmNote(f, y)));
    for (const [n, m] of [["erw-mix-ramp", "ramp"], ["erw-mix-netload", "netload"], [`erw-mix-tight-${g}`, "tight"], [`erw-mix-calm-${g}`, "calm"]]) {
      assert.equal(byName[n].props.tip, GS.NOT[m], `${g} ${n}`);
      assert.ok(byName[n].props.x.length <= 40, "few enough categories that each point is drawn (svgchart: n <= 40)");
    }
    const links = els.filter((e) => e.name === "not");
    assert.deepEqual(links.map((l) => l.props["data-stress-not"]), ["ramp", "netload", "tight", "calm"], g);
    for (const l of links) { assert.equal(l.props.href, GS.STRESS_METHOD); assert.equal(l.props.title, GS.NOT[l.props["data-stress-not"]]); }
  }
});

test("several grids: the ramp and the lowest net load a line a grid, named; the tightest hours and the stretches a chart a grid", () => {
  const gs = ["ercot", "caiso", "spp", "pjm"];
  const fs4 = gs.map(read), ys = GS.yearsOfAll(fs4);
  const els = charts(walk(V.StressView({ c: choiceOf({ view: "stress", grids: gs.join(",") }) })));
  const by = Object.fromEntries(els.map((e) => [e.props.name, e]));
  for (const n of ["erw-mix-ramp-1h", "erw-mix-ramp-3h", "erw-mix-netload", ...gs.map((g) => `erw-mix-tight-${g}`), ...gs.map((g) => `erw-mix-calm-${g}`)]) assert.ok(by[n], n);
  assert.deepEqual(by["erw-mix-netload"].props.series.map((s) => s.name), ["ERCOT", "CAISO", "SPP", "PJM"]);
  assert.deepEqual(by["erw-mix-netload"].props.series.map((s) => s.values), fs4.map((f) => GS.valuesOf(f, ys, "net_load_min_share_of_peak_pct")));
  assert.deepEqual(by["erw-mix-netload"].props.notes, GS.notesOf(fs4, ys, GS.netLoadNote));
  assert.deepEqual(by["erw-mix-ramp-1h"].props.notes, GS.notesOf(fs4, ys, GS.rampNote));
  assert.equal(by["erw-mix-ramp-3h"].props.tip, GS.NOT.ramp);
});
