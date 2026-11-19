// Energy Research Warehouse (ERW) site, session 8450 (chain 503, part E): every figure "The whole country" of /demand
// (?view=country, components/demand/Country.tsx) prints, for each region and balancing authority whose file is on the
// site, written to one JSON file for the replication (replication/demand/replicate_regions.py), which recomputes each
// from the files on its own.
//
//   node --import ./scripts/battery-awards-page-register.mjs scripts/demand-regions-figures.mjs <out.json> [--places ten,ba-tva]
//   node --import ./scripts/battery-awards-page-register.mjs scripts/demand-regions-figures.mjs --fixture <dir>
//
// The files are read where the site reads them (site/data/regions/, or ERW_REGIONS_DIR in a test). With --fixture the
// test's fixture (scripts/regions-fixture-demand.mjs: values made by a rule, not data) is written to <dir> as the data
// machine lays its files out, and nothing is drawn. A held file gives no figure, as the page gives none.
//
// What is drawn, each view by the site's own component, and what is kept of it:
//   place    one place alone, nothing else chosen: every figure, and the points of its chart of days
//   days     the same with one year of days chosen, for each year its file holds: the figures of the table of days
//   figure   a region with each other figure of the weather view: the figures of the weather table, chart and check
//   year     a region with each year of the weather view chosen: the figures of the weather chart
//   pair     two places side by side (the view as it opens, and each region beside its grid): every figure but the points
// A figure is a checked number of the view (a span that carries data-n) under its own key; a figure a chart shows on
// hover (data-tip) under a key made here (cd|<a or b>|tip|...); and, for the chart of days, whose points are not words
// in the first HTML, the points the view hands the chart (lib/countrydemand.ts, dailyPoints) written as the chart's
// card and its table write a value (components/TimeChart.tsx, `num`, copied below and held to the source by the
// Python test). The counts of the tables at the foot are kept once, under index|...
import fs from "node:fs";
import path from "node:path";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { writeFixtureFolder } from "./regions-fixture-demand.mjs";

// the chart's own way of writing a value, as components/TimeChart.tsx has it
const num = (v) => (Math.abs(v) >= 100 ? Math.round(v).toLocaleString("en-US") : Number(v.toFixed(2)).toLocaleString("en-US", { maximumFractionDigits: 2 }));

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const NUM = "[+-]?[\\d,]+(?:\\.\\d+)?";
const args = process.argv.slice(2);
const opt = (name) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : null; };

/** The checked numbers of a drawn view, by key; a key drawn twice with two values is a clash. */
function checked(html, clashes) {
  const out = {};
  for (const m of html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)) {
    if (m[1] in out && out[m[1]] !== m[2]) clashes.push(m[1]);
    out[m[1]] = m[2];
  }
  return out;
}

/** The figures the charts carry as hovers, keyed cd|<mark>|tip|...: the chart of the years, the cells by month and
 *  hour, the bars by month and by hour (each under the place whose block it stands in), and the weather chart (each
 *  row under the place it names). A mark that reads "not held" carries no figure. */
function hovers(html, keyOfMark) {
  const out = {};
  const blocks = [...html.matchAll(/data-cd-(?:years|where)="(a|b)"/g)].map((m) => [m.index, m[1]]);
  const markAt = (pos) => { let k = null; for (const [p, m] of blocks) if (p < pos) k = m; return k; };
  for (const m of html.matchAll(/<svg[^>]*data-chart="([^"]+)"[^>]*>([\s\S]*?)<\/svg>/g)) {
    const chart = m[1], body = m[2];
    if (chart === "explained") {
      for (const part of body.split('<g data-grid="').slice(1)) {
        const key = part.slice(0, part.indexOf('"'));
        const mark = Object.keys(keyOfMark).find((k) => keyOfMark[k] === key);
        const w = new RegExp(`data-tip="[^"]*, (\\d{4}): the weather explains (${NUM}) percent of (${NUM}) percent growth"`).exec(part);
        const u = new RegExp(`data-tip="[^"]*, (\\d{4}): (${NUM}) percent the weather does not explain(?:, give or take (${NUM}))?`).exec(part);
        if (!mark) continue;
        if (w) { out[`cd|${mark}|tip|w|${w[1]}|w`] = w[2]; out[`cd|${mark}|tip|w|${w[1]}|g`] = w[3]; }
        if (u) { out[`cd|${mark}|tip|w|${u[1]}|u`] = u[2]; if (u[3] !== undefined) out[`cd|${mark}|tip|w|${u[1]}|pm`] = u[3]; }
      }
      continue;
    }
    const mark = markAt(m.index);
    if (!mark) continue;
    if (chart === "years") {
      for (const t of body.matchAll(new RegExp(`data-year="(\\d{4})" data-tip="[^"]*: average (${NUM}) MW(?:, highest hour (${NUM}) MW)?"`, "g"))) {
        out[`cd|${mark}|tip|year|${t[1]}|avg`] = t[2];
        if (t[3] !== undefined) out[`cd|${mark}|tip|year|${t[1]}|peak`] = t[3];
      }
    } else if (chart === "heat") {
      for (const t of body.matchAll(new RegExp(`data-cell="(\\d+)\\|(\\d+)" data-tip="[^"]*: (${NUM}) percent, (${NUM}) MW"`, "g"))) {
        out[`cd|${mark}|tip|cell|${t[1]}|${t[2]}|pct`] = t[3];
        out[`cd|${mark}|tip|cell|${t[1]}|${t[2]}|mw`] = t[4];
      }
    } else if (chart === "by month") {
      for (const t of body.matchAll(new RegExp(`data-tip="([A-Z][a-z]+): (${NUM}) percent from`, "g"))) out[`cd|${mark}|tip|month|${MONTHS.indexOf(t[1]) + 1}|pct`] = t[2];
    } else if (chart === "by hour") {
      for (const t of body.matchAll(new RegExp(`data-tip="(\\d{2}):00: (${NUM}) percent from`, "g"))) out[`cd|${mark}|tip|hour|${Number(t[1])}|pct`] = t[2];
    }
  }
  return out;
}

/** The counts of the tables at the foot: the balancing authorities of each region, and how many the index lists. */
function footCounts(html) {
  const out = {};
  const rows = html.split('data-cd-region="').slice(1);
  for (const row of rows) {
    const code = row.slice(0, row.indexOf('"'));
    const m = /<span title="[^"]*" class="cursor-help">(\d+)<\/span>/.exec(row.split("</tr>")[0]);
    if (m) out[`index|${code}|bas`] = m[1];
  }
  const all = /The balancing authorities \((\d+)\)/.exec(html);
  if (all) out["index|bas"] = all[1];
  return out;
}

if (args[0] === "--fixture") {
  const dir = args[1];
  if (!dir) { console.error("usage: demand-regions-figures.mjs --fixture <dir>"); process.exitCode = 2; }
  else { writeFixtureFolder(dir); console.log(`wrote the fixture to ${dir}`); }
} else if (!args[0] || args[0].startsWith("--")) {
  console.error("usage: demand-regions-figures.mjs <out.json> [--places ten,ba-tva] | --fixture <dir>");
  process.exitCode = 2;
} else {
  const C = await import("../lib/countrydemand.ts");
  const F = await import("../lib/countryfiles.ts");
  const W = await import("../lib/demandweather.ts");
  const V = await import("../components/demand/Country.tsx");

  const index = C.regionsIndex();
  const read = new Map();
  const fileOf = (p) => { const k = C.placeKey(p); if (!read.has(k)) read.set(k, C.demandPlaceFile(p)); return read.get(k); };
  const baDir = path.join(F.regionsDir(), "demand", "ba");
  const baCodes = index?.bas?.map((b) => b.code) ?? (fs.existsSync(baDir) ? fs.readdirSync(baDir).filter((n) => /^[a-z0-9]{2,8}\.json$/.test(n)).map((n) => n.slice(0, -5).toUpperCase()).sort() : []);
  const only = opt("--places")?.split(",") ?? null;
  const places = [...F.REGION_CODES.map((code) => ({ level: "region", code })), ...baCodes.map((code) => ({ level: "ba", code }))].filter((p) => !only || only.includes(C.placeKey(p)));

  const out = {
    what: "The figures of the view The whole country of /demand, as the site's own code draws them from each place's file (site/scripts/demand-regions-figures.mjs).",
    newest_days: C.NEWEST_DAYS, first: [C.placeKey(C.FIRST_A), C.placeKey(C.FIRST_B)],
    index: { file: !!index, built: index?.built ?? "", figures: {} }, places: {}, views: [],
  };
  const attr = (html, name) => new RegExp(`${name}="([^"]*)"`).exec(html)?.[1] ?? "";
  /** One view drawn and kept: `keeps` the parts of a key after cd|<mark>| that are kept (null: all), `drops` those left out. */
  const view = (kind, q, keeps, drops, withPoints) => {
    const html = renderToStaticMarkup(createElement(V.Country, { q, index, fileOf }));
    const a = attr(html, "data-cd-a"), b = attr(html, "data-cd-b");
    const clashes = [];
    const all = { ...checked(html, clashes), ...hovers(html, { a, b }) };
    if (withPoints) {
      const file = fileOf(C.placeOf(a, index));
      if (file && !V.heldWhyOf(file)) for (const what of ["peak", "average"]) for (const [t, v] of C.dailyPoints(file.daily, what, "all")) {
        if (v !== null) all[`cd|a|pt|${new Date(t).toISOString().slice(0, 10)}|${what === "peak" ? "peak" : "avg"}`] = num(v);
      }
    }
    const part = (k) => k.split("|").slice(2).join("|");
    const figures = Object.fromEntries(Object.entries(all).filter(([k]) => (!keeps || keeps.some((p) => part(k).startsWith(p))) && !drops.some((p) => part(k).startsWith(p))));
    const states = Object.fromEntries([...html.matchAll(/data-cd-place="(a|b)" data-cd-code="[^"]*" data-cd-state="([^"]*)"/g)].map((m) => [m[1], m[2]]));
    out.views.push({ kind, a, b, days: attr(html, "data-cd-days"), figure: W.FIGURES.find((f) => f.slug === q.figure)?.key ?? W.FIGURES[0].key, year: q.year ?? "", states, keeps, drops, clashes, figures });
    return html;
  };

  let first = true;
  for (const p of places) {
    const key = C.placeKey(p), file = fileOf(p);
    if (!file) { out.places[key] = { file: false }; continue; }
    const held = !!V.heldWhyOf(file);
    out.places[key] = { file: true, held, level: p.level, built: file.built ?? "", days: file.daily?.days?.length ?? 0 };
    const html = view("place", { a: key, b: "none" }, null, [], true);
    if (first && index) { out.index.figures = footCounts(html); first = false; }
    if (held) { console.log(`${key}: held`); continue; }
    for (const y of C.dailyYears(file.daily)) view("days", { a: key, b: "none", days: y }, ["day|"], [], false);
    if (file.weather && C.trainOf(file.weather).length) {
      for (const f of W.FIGURES.slice(1)) view("figure", { a: key, b: "none", figure: f.slug }, ["w|", "h|", "tip|w|"], [], false);
      for (const y of Object.keys(file.weather.years ?? {}).sort()) view("year", { a: key, b: "none", year: y }, ["tip|w|"], [], false);
    }
    console.log(`${key}: drawn`);
  }
  if (!only) {
    // two places side by side: the view as it opens, and each region beside the grid its file names
    const has = (k) => out.places[k]?.file;
    if (has(out.first[0]) || has(out.first[1])) view("pair", {}, null, ["pt|"], false);
    for (const p of places) {
      const file = p.level === "region" ? fileOf(p) : null;
      const grid = file?.alike?.grid ? `ba-${String(file.alike.grid).toLowerCase()}` : null;
      if (grid && has(grid)) view("pair", { a: C.placeKey(p), b: grid }, null, ["pt|"], false);
    }
  }
  fs.writeFileSync(args[0], JSON.stringify(out) + "\n");
  const n = out.views.reduce((s, v) => s + Object.keys(v.figures).length, 0) + Object.keys(out.index.figures).length;
  console.log(`wrote ${args[0]}: ${out.views.length} views of ${Object.values(out.places).filter((x) => x.file).length} places, ${n} figures`);
}
