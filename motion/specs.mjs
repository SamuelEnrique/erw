// Energy Research Warehouse (ERW), session 274: the specs of the motion videos, from the rows that draw each chart.
//
//   node specs.mjs                       the chart of the week (newest docs/analysis/<week>/chart_of_the_week.json) and
//                                        the four strongest findings (site/data/findings/), and two extra proofs
//   node specs.mjs <file.json> ...       those files only
//
// Writes specs/<id>.json. Every number in a spec is a number of the source file: nothing is typed, rounded beyond the
// chart's own decimals, or filled. The motion type is chosen by the chart's kind:
//
//   line, lines, line_with_fleet, flag_line   draw-on    the chart drawn over its x axis
//   scatter                                    count-up   a scatter's message is its fitted effect: the effect table's
//                                                         full specification (its last row), with the finding's sentence
//   stacked_bar_pct                            roll call  each category in turn, with the first series' share
//   bars_free, grouped_bar                     reorder    the bars move from the first series' ranking to the second's
//
// "The four strongest findings": the committed findings with a tested effect (an effect table), ranked by the p-value
// of the table's first specification, smallest first, one card a finding (a five-grid version, "<id>_grids", and a
// variant, "<id>__<params>", count with their finding).
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..");
const OUT = path.join(HERE, "specs");
const FPS = 30;
const read = (p) => JSON.parse(fs.readFileSync(p, "utf-8"));

function drawOn(base, c) {
  const x = c.x.map(String);
  // a bar series on an axis of its own (a third scale) is left out of the motion version and named in leftOut
  const leftOut = c.series.filter((s) => s.type === "bar" && s.axis && s.axis !== "left" && s.axis !== "right").map((s) => s.name);
  const series = c.series.filter((s) => !leftOut.includes(s.name)).map((s) => ({
    name: s.name,
    values: (s.values ?? s.data).map((v) => (v === null || v === undefined || Number.isNaN(v) ? null : Number(v))),
    axis: !s.axis || s.axis === "left" ? "left" : "other",
    unit: s.unit ?? "",
    bar: s.type === "bar",
  }));
  let band = null;
  if (c.mark_area) {
    const from = x.indexOf(c.mark_area.from);
    const to = x.indexOf(c.mark_area.to);
    if (from >= 0 && to >= from) band = { from, to, label: `${c.mark_area.from} to ${c.mark_area.to}` };
  }
  return { ...base, type: "draw-on", x, xLabel: c.x_label ?? "", yLabel: c.y_left_label ?? c.y_label ?? "", yRightLabel: c.y_right_label ?? "", series, band, leftOut,
    decimals: c.decimals ?? (Math.max(...series[0].values.filter((v) => v !== null).map(Math.abs)) >= 100 ? 0 : 1), frames: 15 * FPS };
}

function countUp(base, d) {
  const et = d.effect_table;
  const row = et.rows[et.rows.length - 1];
  const col = String(et.columns[1]);                       // "Per GWh charged (MWh curtailed)"
  const m = col.match(/^Per (.+?) \((.+)\)$/);
  const unit = m ? `${m[2]} per ${m[1]}` : col;
  const words = String(et.in_words);
  const sentence = words.charAt(0).toUpperCase() + words.slice(1).split(":")[0] + ".";
  return { ...base, type: "count-up", value: row.coef_per_gw, decimals: Math.abs(row.coef_per_gw) >= 100 ? 0 : 3, unit: `${unit} (${row.measure})`, sentence, frames: 11 * FPS };
}

function rollCall(base, c) {
  const s = c.series[0];
  const rows = c.x.map((label, i) => ({ label: String(label), value: Number(s.values[i]) }));
  const frames = Math.max(10 * FPS, Math.min(20 * FPS, 40 + rows.length * 45 + 70));
  return { ...base, type: "roll-call", measure: `${s.name}, ${c.y_left_label ?? "percent"}`, rows, unit: c.kind === "stacked_bar_pct" ? "%" : "",
    decimals: 1, max: c.kind === "stacked_bar_pct" ? 100 : Math.max(...rows.map((r) => r.value)), frames };
}

function reorder(base, c) {
  let labels, before, after;
  if (c.kind === "grouped_bar") {   // x is a year: the series ranked in the first year, then in the last
    labels = c.series.map((s) => s.name);
    before = { name: String(c.x[0]), values: c.series.map((s) => Number(s.values[0])) };
    after = { name: String(c.x[c.x.length - 1]), values: c.series.map((s) => Number(s.values[s.values.length - 1])) };
  } else {
    labels = c.x.map(String);
    before = { name: c.series[0].name, values: c.series[0].values.map(Number) };
    after = { name: c.series[1].name, values: c.series[1].values.map(Number) };
  }
  return { ...base, type: "reorder", labels, before, after, unit: c.y_left_label ?? "", decimals: c.decimals ?? 0, frames: 14 * FPS };
}

const KIND = {
  line: drawOn, lines: drawOn, line_with_fleet: drawOn, flag_line: drawOn,
  scatter: "count", stacked_bar_pct: rollCall, bars_free: reorder, grouped_bar: reorder,
};

export function specOf(file) {
  const d = read(file);
  const week = d.week;   // a chart of the week's file has its week; a finding has an id
  const c = d.chart;
  const id = week ? `chart_of_the_week_${week}` : d.id;
  const base = {
    id, kicker: week ? `ERW, chart of the week, ${week}` : "ERW Research",
    title: c.title ?? d.title, subtitle: week ? c.subtitle : d.subtitle ?? "", source: week ? (c.source ?? d.source_line) : d.source_line,
    width: 1080, height: 1350,
  };
  const how = KIND[c.kind];
  if (!how) throw new Error(`${file}: chart kind ${c.kind} has no motion type`);
  if (how === "count") return countUp(base, d);
  return how(base, c);
}

export function strongest(dir = path.join(ROOT, "site", "data", "findings"), n = 4) {
  const seen = new Set();
  const ranked = fs.readdirSync(dir).filter((f) => f.endsWith(".json") && f !== "catalogue.json")
    .map((f) => ({ f: path.join(dir, f), d: read(path.join(dir, f)) }))
    .filter(({ d }) => d.effect_table?.rows?.length)
    .map(({ f, d }) => ({ f, id: d.id, family: d.id.split("__")[0].replace(/_grids$/, ""), p: Number(d.effect_table.rows[0].p) }))
    .sort((a, b) => a.p - b.p || a.id.localeCompare(b.id));
  const out = [];
  for (const r of ranked) {
    if (seen.has(r.family)) continue;
    seen.add(r.family);
    out.push(r);
    if (out.length === n) break;
  }
  return out;
}

function newestWeek() {
  const dir = path.join(ROOT, "docs", "analysis");
  const weeks = fs.readdirSync(dir).filter((w) => /^\d{4}-W\d{2}$/.test(w) && fs.existsSync(path.join(dir, w, "chart_of_the_week.json"))).sort();
  return path.join(dir, weeks[weeks.length - 1], "chart_of_the_week.json");
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  const files = args.length ? args.map((a) => path.resolve(a)) : [
    newestWeek(),
    ...strongest().map((r) => r.f),
    // the two extra proofs: the motion types the five above do not use
    path.join(ROOT, "site", "data", "findings", "who_rescues_whom.json"),
    path.join(ROOT, "site", "data", "findings", "queue_divorce.json"),
  ];
  fs.mkdirSync(OUT, { recursive: true });
  if (!args.length) for (const r of strongest()) console.log(`strongest: ${r.id} (p of the first specification ${r.p.toExponential(2)})`);
  for (const f of files) {
    const s = specOf(f);
    fs.writeFileSync(path.join(OUT, `${s.id}.json`), JSON.stringify(s, null, 1) + "\n");
    console.log(`${s.id}: ${s.type}, ${s.frames / FPS} s, from ${path.relative(ROOT, f)}`);
  }
}
