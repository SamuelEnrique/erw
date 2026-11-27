// Energy Research Warehouse (ERW) site, session 10401 (chain 720, part C): what a reader of /forecast sees, drawn to HTML
// with the site's own code, without a build.
//   node --import ./scripts/events-page-register.mjs scripts/test-forecast.mjs
// Three states are drawn: no files on the site (how main stands until the data machine's forecast build lands); the
// contract's own example files (docs/state/page_files_predict_examples, every value null); and files of the contract's
// shape written here into a temporary folder with made-up values, each marked as a test's fixture, which the site's
// own folder never reads (lib/predictfiles.ts). The page reads ERW_PREDICT_DIR for each. No network. Exit 0 when every
// check holds, 1 otherwise.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const EXAMPLES = path.resolve(SITE, "..", "docs", "state", "page_files_predict_examples");
const { ForecastView } = await import("../app/forecast/view.tsx");
const P = await import("../lib/predict.ts");
const { csvReader } = await import("../lib/csvreader.ts");
const { ROWS_READER } = await import("../app/forecast/rows/reader.ts");
const { SCORES_READER } = await import("../app/forecast/scores/reader.ts");

const fails = [];
let n = 0;
const check = (ok, what) => { n++; if (!ok) fails.push(what); };
const draw = (dir, query = {}) => { process.env.ERW_PREDICT_DIR = dir; return renderToStaticMarkup(h(ForecastView, { query })); };
const text = (html) => html.replace(/<title>[^<]*<\/title>/g, " ").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&amp;/g, "&").replace(/\s+/g, " ");
const dash = String.fromCharCode(0x2014);
const count = (html, re) => (html.match(re) ?? []).length;
const quiet = (html, where) => {
  const t = text(html);
  check(!/\bundefined\b|\bNaN\b|\bnull\b/.test(t), `${where}: "undefined", "NaN" or "null" on the page`);
  check(!html.includes(dash), `${where}: an em dash`);
  check(!/outperform|signal|should buy|should sell|so what/i.test(t), `${where}: a word of advice or a view`);
};

// ---- 1. No files on the site -----------------------------------------------------------------------------------------
{
  const html = draw(path.join(os.tmpdir(), "erw-c720-no-such-folder"));
  check(html.includes('data-fc-state="no-files"'), "no files: the page does not say so");
  check(text(html).includes("ERW forecast: not built yet"), "no files: the blank's words");
  check(!html.includes("data-check="), "no files: a checked figure is drawn");
  check(html.includes("<h1") && text(html).includes("ERW forecast"), "no files: the title");
  quiet(html, "no files");
}

// ---- 2. The contract's example files: nothing is shown as a forecast ------------------------------------------------
{
  check(fs.existsSync(path.join(EXAMPLES, "index.json")), "the contract's example files are not in docs/state/page_files_predict_examples");
  for (const s of ["demand", "price"]) {
    const html = draw(EXAMPLES, { s, b: "region-mida" });
    check(html.includes('data-fc-state="example"'), `examples, ${s}: the page does not know the files are examples`);
    check(!html.includes("data-check=") && !html.includes("data-n=\"fc|"), `examples, ${s}: a figure is drawn from an example file`);
    check(count(html, /data-fc-shown="0"/g) === 2 && !html.includes('data-fc-shown="1"'), `examples, ${s}: a place is drawn as shown`);
    check(count(html, /data-fc-blank="/g) >= 6, `examples, ${s}: fewer than six blanks (tomorrow, a past day and the record, for two places)`);
    check(text(html).includes("not built yet"), `examples, ${s}: the blank's words`);
    check(html.includes("no forecast has been written yet"), `examples, ${s}: the blank's hover does not say why`);
    check(!html.includes("data-svg-chart"), `examples, ${s}: a chart is drawn from an example file`);
    quiet(html, `examples, ${s}`);
  }
}

// ---- 3. Files of the contract's shape, with a test's made-up values --------------------------------------------------
// `--keep <folder>` writes the fixture there and leaves it, for a build served with ERW_PREDICT_DIR set to it (to see the
// page's layout before the real files exist; such a build is looked at on this machine and never deployed)
const KEEP = process.argv.includes("--keep") ? process.argv[process.argv.indexOf("--keep") + 1] : null;
if (KEEP) fs.mkdirSync(KEEP, { recursive: true });
const FIX = KEEP ?? fs.mkdtempSync(path.join(os.tmpdir(), "erw-c720-predict-"));
const FIXTURE = "scripts/test-forecast.mjs: made-up values, a test's fixture";
const head = { fixture: FIXTURE, contract: "docs/state/page_files_predict.md", built: "2026-11-26T14:05:00Z", tier: "derived", label: "ERW forecast" };
const NOTES = { demand: "docs/methods/predict.md", price: "docs/methods/predict_price.md" };
const TCOLS = ["ts_utc", "local_hour", "erw", "lo", "hi", "operator"];
const HCOLS = ["ts_utc", "local_day", "local_hour", "made_utc", "kind", "erw", "lo", "hi", "operator", "actual", "yesterday", "week_ago"];
const iso = (day, hour, offset) => new Date(Date.parse(`${day}T00:00:00Z`) + (hour + offset) * 3_600_000).toISOString().replace(".000Z", "Z");
const sum4 = (v) => ({ erw: v[0], operator: v[1], yesterday: v[2], week_ago: v[3] });
const part = (first, last, hours, mae, mape) => ({ first_day: first, last_day: last, hours, mae: sum4(mae), mape: sum4(mape) });
// demand: the ERW forecast peaks at 17:00 (40,000 + 1,000 an hour to 17, then down); the operator stands 300 above it
const demandAt = (hr) => 40000 + 1000 * (hr <= 17 ? hr : 34 - hr);
const priceAt = (hr) => 20 + 2.5 * (hr <= 18 ? hr : 36 - hr);
function series(kind, offset, status = "shown", held = null) {
  const demand = kind === "demand";
  const base = { status, held, method: status === "shown" ? (demand ? "regression" : "flexible") : null, fit_day: status === "shown" ? "2026-11-26" : null,
    target_day: status === "shown" ? "2026-11-27" : null, hub: demand || status !== "shown" ? null : "ercot:HB_NORTH", market: demand ? null : "day-ahead",
    unit: demand ? "MW" : "USD/MWh", method_note: NOTES[kind], made_utc: status === "shown" ? "2026-11-26T13:00:00Z" : null, inputs_through_utc: status === "shown" ? "2026-11-26T11:00:00Z" : null,
    band: status === "shown" ? "the 10th to the 90th percentile of the method's own errors at this hour of the day over the last 60 days" : null, band_coverage_pct: status === "shown" ? 81.4 : null,
    tomorrow_columns: TCOLS, operator_held: demand ? null : "not published: no operator publishes a forecast of its day-ahead price", history_columns: HCOLS,
    horizon_days: status === "shown" ? 2 : null, tomorrow_held: null };
  if (status !== "shown") {
    return { ...base, tomorrow: [[iso("2026-11-27", 0, offset), 0, null, null, null, null]], history: [[iso("2026-11-25", 0, offset), "2026-11-25", 0, null, "backtest", null, null, null, null, null, null, null]],
      summary: { last_30_days: part(null, null, null, [null, null, null, null], [null, null, null, null]), backtest: part(null, null, null, [null, null, null, null], [null, null, null, null]) } };
  }
  const at = demand ? demandAt : priceAt, w = demand ? 1500 : 6, op = demand ? 300 : null;
  const tomorrow = Array.from({ length: 24 }, (_, hr) => [iso("2026-11-27", hr, offset), hr, at(hr), at(hr) - w, at(hr) + w, op === null ? null : at(hr) + op]);
  // two past days. On 25 November the ERW forecast is the worst of the four on purpose (it misses by 500 MW or 5 USD each
  // hour, the operator by 100 MW, yesterday by 300, a week ago by 400): a day it lost must be drawn as any other.
  const day = (d, kind2, miss) => Array.from({ length: 24 }, (_, hr) => {
    const actual = at(hr) - (demand ? 1000 : 2);
    const f = (m) => (m === null ? null : actual + m);
    return [iso(d, hr, offset), d, hr, iso(d, 13 - 24, 0), kind2, f(miss[0]), f(miss[0]) - w, f(miss[0]) + w, demand ? f(miss[1]) : null, actual, f(miss[2]), f(miss[3])];
  });
  const history = [...day("2026-11-24", "backtest", demand ? [200, 400, -600, 900] : [1, null, -3, 4]), ...day("2026-11-25", "live", demand ? [500, -100, 300, -400] : [5, null, 3, -4])];
  return { ...base, tomorrow, history,
    summary: { last_30_days: part("2026-10-27", "2026-11-25", 720, demand ? [812, 640, 2210, 3105] : [6.42, null, 9.87, 12.3], demand ? [1.62, 1.28, 4.4, 6.21] : [18.3, null, 27.1, 33.9]),
      backtest: part("2025-11-26", "2026-11-25", 8760, demand ? [905, 950, 2400, 3300] : [7.05, null, 10.4, 13.6], demand ? [1.81, 1.9, 4.8, 6.6] : [20.1, null, 29.9, 36.2]) } };
}
const places = [
  { place: "region-mida", name: "Mid-Atlantic", kind: "region", eia930: "MIDA", time: "America/New_York", file: "region-mida.json", off: 5, price: ["license needed", "license needed: PJM's terms ask for a license the ERW does not hold (docs/licenses.md)"] },
  { place: "region-tex", name: "Texas", kind: "region", eia930: "TEX", time: "America/Chicago", file: "region-tex.json", off: 6, price: ["shown", null] },
  { place: "ba-erco", name: "Electric Reliability Council of Texas, Inc.", kind: "ba", eia930: "ERCO", time: "America/Chicago", file: "ba-erco.json", off: 6, price: ["too short", "fewer whole days of history than the method needs"] },
];
const ixSeries = (s) => ({ status: s.status, held: s.held, method: s.method, fit_day: s.fit_day, target_day: s.target_day, hub: s.hub, market: s.market });
const files = places.map((p) => ({ ...head, place: p.place, name: p.name, kind: p.kind, eia930: p.eia930, time: p.time, tables: ["eia930_ba_demand_hourly", "predict_demand_hourly"],
  series: { demand: series("demand", p.off), price: series("price", p.off, p.price[0], p.price[1]) } }));
const index = { ...head, method_notes: NOTES, made_rule: "Each day's forecast is made at 13:00 UTC from figures published before that hour.",
  band_rule: "The band runs from the 10th to the 90th percentile of the method's own past errors at the same hour of the day.",
  choice_rule: "A place's method is the one with the lowest backtest error among those built for it.",
  places: places.map((p, i) => ({ place: p.place, name: p.name, kind: p.kind, eia930: p.eia930, time: p.time, file: p.file, series: { demand: ixSeries(files[i].series.demand), price: ixSeries(files[i].series.price) } })) };
// the report card: in October 2026 and at 17:00 the ERW forecast is worse than the operator's, on purpose
const rows = [];
const add = (place, s, cut, key, hours, by) => { for (const [m, v] of Object.entries(by)) rows.push([place, s, m, cut, key, v === null ? null : hours, v === null ? null : v[0], v === null ? null : v[1], v === null ? (m === "operator" ? "not published" : "license needed") : null]); };
for (const p of ["region-tex", "region-mida", "ba-erco"]) {
  const k = p === "region-tex" ? 1 : p === "region-mida" ? 1.5 : 0.8;
  const d = (a, b, c, e, f) => ({ erw: [a * k, a * k / 500], operator: [b * k, b * k / 500], yesterday: [c * k, c * k / 500], week_ago: [e * k, e * k / 500], regression: [f * k, f * k / 500] });
  add(p, "demand", "all", "", 8760, d(905, 950, 2400, 3300, 905));
  add(p, "demand", "month", "2026-11", 600, d(700, 900, 2100, 3000, 700));
  add(p, "demand", "month", "2026-10", 744, d(1300, 800, 2500, 3400, 1300));
  add(p, "demand", "hour", "17", 365, d(1500, 1100, 2900, 3600, 1500));
  add(p, "demand", "hour", "3", 365, d(400, 600, 1200, 2000, 400));
  add(p, "demand", "top10", "", 240, d(2100, 1900, 5200, 6100, 2100));
  add(p, "demand", "event", "uri-2021", 120, d(6000, 7000, 9000, 15000, 6000));
  add(p, "demand", "last_2_years", "", 17420, d(880, 940, 2350, 3250, 880));
}
add("region-tex", "price", "all", "", 8700, { erw: [7.05, 20.1], operator: null, yesterday: [10.4, 29.9], week_ago: [13.6, 36.2], flexible: [7.05, 20.1] });
// as the real files are: one operator row a price place (over every hour, with its reason) and none in the other cuts
add("region-tex", "price", "month", "2026-11", 600, { erw: [9.5, 31.0], yesterday: [8.1, 25.5], week_ago: [11.2, 30.3], flexible: [9.5, 31.0] });
add("region-tex", "price", "spike", "", 87, { erw: [310.4, 61.2], yesterday: [402.9, 80.3], week_ago: [455.0, 88.8], flexible: [310.4, 61.2] });
rows.push(["region-mida", "price", "erw", "all", "", null, null, null, "license needed"]);
const scores = { ...head, method_notes: NOTES, span: { demand: { first_day: "2025-11-26", last_day: "2026-11-25" }, price: { first_day: "2025-11-26", last_day: "2026-11-25" } },
  methods: [{ id: "erw", what: "the method chosen for the place by the rule of the method note" }, { id: "operator", what: "the operator's own day-ahead forecast, as EIA-930 prints it" },
    { id: "yesterday", what: "the same hour of the day before" }, { id: "week_ago", what: "the same hour seven days before" }, { id: "regression", what: "the regression of the method note" }, { id: "flexible", what: "the flexible model of the method note" }],
  metrics: { mae: "mean absolute error, in the series' unit", mape: "mean absolute percent error, in percent" }, mape_rule: "A percent error is not written for an hour whose price is within 1 USD/MWh of zero.",
  cuts: { all: "every hour scored", month: "key YYYY-MM", hour: "key 0 to 23, the place's clock", top10: "the place's ten highest-demand days of the backtest", event: "key: the event id of /events", spike: "price only: the hours above the grid's 99th percentile" },
  rows_columns: ["place", "series", "method", "cut", "key", "hours", "mae", "mape", "held"], rows };
// the contract's additions of 26 November: a place whose target day holds no forecast says why (`tomorrow_held`); a
// place scored month by month since 2023 (42 months: a long table keeps to a frame of its own); the demand ledger
{
  const erco = files[2].series.demand;
  erco.tomorrow = erco.tomorrow.map((r) => [r[0], r[1], null, null, null, null]);
  erco.tomorrow_held = "no data: the place's demand for the last whole day is not in the warehouse yet";
  for (let i = 0; i < 40; i++) {
    const m = `${2023 + Math.floor(i / 12)}-${String((i % 12) + 1).padStart(2, "0")}`;
    if (m !== "2026-10" && m !== "2026-11") add("region-mida", "demand", "month", m, 700, { erw: [1000 + i, 2 + i / 100], operator: [900, 1.9], yesterday: [2500, 5], week_ago: [3300, 6.6], regression: [1000 + i, 2 + i / 100] });
  }
  fs.writeFileSync(path.join(FIX, "ledger_demand.csv"), ["# a test's fixture: the ledger's three lines of provenance", "# second line", "# third line",
    "series,place,target_day,ts_utc,local_hour,made_utc,inputs_through_utc,horizon_days,method,erw,lo,hi", "demand,region-tex,2026-11-27,2026-11-27T06:00:00Z,0,2026-11-26T13:00:00Z,2026-11-26T11:00:00Z,2,regression,40000,38500,41500", ""].join("\n"));
}
fs.writeFileSync(path.join(FIX, "index.json"), JSON.stringify(index));
fs.writeFileSync(path.join(FIX, "scores.json"), JSON.stringify(scores));
files.forEach((f, i) => fs.writeFileSync(path.join(FIX, places[i].file), JSON.stringify(f)));

try {
  // 3a. the page as it opens: Texas alone, demand
  const html = draw(FIX);
  const t = text(html);
  check(html.includes('data-fc-state="files"') && html.includes('data-fc-series="demand"') && html.includes('data-fc-metric="mape"'), "as it opens: Texas, demand, percent error");
  check(count(html, /data-fc-tomorrow="/g) === 1 && html.includes('data-fc-tomorrow="a" data-fc-shown="1" data-fc-hours="24"'), "as it opens: one place, 24 hours of tomorrow");
  check(/data-n="fc\|a\|demand\|top">57,000</.test(html), "the highest hour of the ERW forecast is 57,000 MW (17:00)");
  check(/data-n="fc\|a\|demand\|optop">57,300</.test(html), "the operator's forecast for that hour is 57,300 MW");
  check(/data-n="fc\|a\|demand\|low">40,000</.test(html), "the lowest hour of the ERW forecast is 40,000 MW (00:00)");
  check(t.includes("ERW forecast, 17:00") && t.includes("Operator's forecast, 17:00") && t.includes("ERW forecast, 00:00"), "each figure says whose it is and its hour");
  check(html.includes('data-check="pf|predict/region-tex.json|series/demand/tomorrow/17/2" data-raw="57000"'), "the highest hour carries its key into the place's file");
  check(html.includes('data-check="pf|predict/region-tex.json|series/demand/tomorrow/17/5" data-raw="57300"'), "the operator's figure carries its key into the place's file");
  // every chart of the model's line says "ERW forecast"
  const charts = [...html.matchAll(/data-svg-chart="category"[^>]*>[\s\S]*?aria-label="([^"]*)"/g)].map((m) => m[1]);
  check(charts.length === 2 && charts.every((c) => c.startsWith("ERW forecast of demand for Texas")), `two charts, each named "ERW forecast" (${charts.length})`);
  check(count(html, /data-series="ERW forecast"/g) === 2 && count(html, /data-band-name=""/g) === 2 && count(html, /Band of the ERW forecast/g) === 2, "the ERW forecast's line and its band on both charts, the band named in the chart's legend");
  check(count(html, /data-series="Operator&#x27;s forecast"/g) === 2, "the operator's own forecast on both charts");
  check(count(html, /data-series="What happened"/g) === 1, "what happened on the past day's chart only");
  check(t.includes("Friday 27 Nov 2026") && html.includes('data-fc-day-of="2026-11-25"'), "tomorrow is 27 November; the past day opens on the newest held, 25 November");
  // the hour the forecast was made and the method, on the place's hover
  check(/title="ERW forecast for Friday 27 Nov 2026: made 2026-11-26 07:00 CST \(2026-11-26 13:00 UTC\)[^"]*Method: Regression, last fit 2026-11-26\.[^"]*13:00 UTC[^"]*lowest backtest error/.test(html), "the place's hover: the hour made, the method, the rules");
  // the past day the ERW forecast lost: drawn as any other, the four errors side by side
  for (const [m, v] of [["erw", "500"], ["operator", "100"], ["yesterday", "300"], ["week_ago", "400"]]) check(new RegExp(`data-n="fc\\|a\\|demand\\|day\\|${m}" data-fc-day-hours="24"[^>]*>${v}<`).test(html), `25 November: ${m}'s mean absolute error is ${v} MW over 24 hours`);
  // the report card: the months and hours the ERW forecast lost are in the same table, in the file's months oldest first
  const month = html.slice(html.indexOf('data-fc-cut="month"'), html.indexOf('data-fc-cut="hour"'));
  check(month.indexOf("Oct 2026") > 0 && month.indexOf("Oct 2026") < month.indexOf("Nov 2026"), "by month: October before November");
  check(/>2\.60<[\s\S]*>1\.60<[\s\S]*>1\.40<[\s\S]*>1\.80</.test(month), "by month: October (the ERW 2.60%, the operator 1.60%) and November (1.40%, 1.80%), both drawn");
  const rowClass = [...month.matchAll(/<tr class="([^"]*)">/g)].map((m) => m[1].trim());
  check(rowClass.length === 3 && new Set(rowClass.slice(1)).size === 1, "by month: the month the ERW forecast lost and the month it won are the same kind of row");
  check(!/font-semibold|bg-paper|text-up|text-down/.test(month.replace(/<h4[^>]*>/g, "")), "by month: no cell is weighted or colored by who won");
  const hour = html.slice(html.indexOf('data-fc-cut="hour"'), html.indexOf('data-fc-cut="other"'));
  check(hour.indexOf("03:00") > 0 && hour.indexOf("03:00") < hour.indexOf("17:00"), "by hour of day: 03:00 before 17:00");
  check(html.includes('data-fc-cut="other"') && t.includes("The ten highest-demand days") && t.includes("Event: uri 2021") && t.includes("Every hour scored"), "the other cuts: every hour, the ten highest-demand days, the event");
  check(html.includes('data-check="pf|predict/scores.json|rows/0/7" data-raw="1.81"'), "a score carries its key into the score file");
  check(html.includes('data-check="pf|predict/region-tex.json|series/demand/summary/backtest/mape/erw" data-raw="1.81"'), "the backtest's figure carries its key into the place's file");
  check(month.includes(">Regression<") && !month.includes(">Flexible<"), "a method the score file scores for the series has its column; one it does not score for it has none");
  check(/title="Same hour yesterday: the same hour of the day before"[^>]*>Yesterday</.test(month), "a column's short name carries its full name and the file's words on hover");
  check(!html.includes("data-fc-group="), "one place: no row of place names over the columns");
  // every place at once, in the index's own order, the held one as any other row
  const all = html.slice(html.indexOf("data-fc-all="));
  check(html.includes('data-fc-all="3"') && all.indexOf("Mid-Atlantic") < all.indexOf(">Texas<") && all.indexOf(">Texas<") < all.indexOf("Electric Reliability Council of Texas, Inc. (ERCO)"), "every place: the index's own order, not sorted by score");
  // session 10413 (read at 390 px by a finger): a place's name in the table was 18 px tall; it has padding and a negative
  // margin of the same size now, so the row keeps its height and only the place a finger lands grows
  const names = [...all.slice(0, all.indexOf('id="downloads"') > 0 ? all.indexOf('id="downloads"') : all.length).matchAll(/<a [^>]*href="\/forecast[^"]*"[^>]*>/g)].map((m) => m[0]);
  check(names.length >= 3 && names.every((a) => a.includes('class="inline-block py-1 -my-1"')), `every place's name in the table has a finger's height (${names.length} names)`);
  // the downloads and the method notes
  check(html.includes('href="/forecast/rows?place=region-tex"') && html.includes('href="/forecast/rows/python?place=region-tex"') && html.includes('href="/forecast/rows/stata?place=region-tex"'), "downloads: the place's hours as CSV, Python and Stata");
  check(html.includes('href="/forecast/scores"') && html.includes('href="/forecast/scores/python"') && html.includes('href="/forecast/scores/stata"'), "downloads: the report card as CSV, Python and Stata");
  check(html.includes('href="/demand?view=country&amp;a=tex#forecast"'), "a link to the operator's long record on /demand");
  check(html.includes('href="/data/methods/predict"') && html.includes('href="/data/methods/predict_price"'), "the two method notes are linked");
  check(count(html, /<h1/g) === 1 && ["Tomorrow", "How it has done", "Every place", "Downloads"].every((x) => t.includes(x)), "one title and the four sections");
  check(!/impact/i.test(html), "nothing of the Economic impact tool is on the page");
  quiet(html, "as it opens");

  // 3b. two places side by side, the second's price held
  const two = draw(FIX, { a: "region-tex", b: "region-mida", s: "price" });
  const tt = text(two);
  check(count(two, /data-fc-tomorrow="/g) === 2 && two.includes("xl:grid-cols-2"), "A and B: two places side by side");
  check(two.includes('data-fc-tomorrow="a" data-fc-shown="1"') && two.includes('data-fc-tomorrow="b" data-fc-shown="0"'), "A and B: Texas's price shown, the Mid-Atlantic's held");
  check(tt.includes("ERW forecast of price, Mid-Atlantic: license needed"), "a held price is a blank that says license needed");
  check(/data-fc-blank="tomorrow\|b\|price"/.test(two) && /title="License needed: PJM&#x27;s terms[^"]*Nothing of this series is shown\."/.test(two), "the held price's hover gives the file's reason");
  // session 10407 (the browser read's row FC3): this line pinned the status said twice ("License needed: license needed: ..."), the fault itself
  check(!/License needed: license needed/i.test(two), "the held price's hover says its status twice");
  const b = two.slice(two.indexOf('data-fc-tomorrow="b"'), two.indexOf('id="record"'));
  check(!b.includes("data-check=") && !/\d{2}\.\d{2}/.test(text(b)), "no figure of the held price is on the page");
  check(/data-n="fc\|a\|price\|top">65\.00</.test(two) && tt.includes("ercot:HB_NORTH, day-ahead"), "Texas's price: the highest hour 65.00 USD/MWh, the hub named");
  check(two.includes('data-fc-metric="mae"'), "price opens on the error in USD/MWh");
  check(count(two, /data-series="Operator&#x27;s forecast"/g) === 0 && tt.includes("not published"), "no operator's price forecast is drawn; the page says not published");
  check(/title="Operator&#x27;s forecast[^"]*not published/.test(two), "the operator's blank says why on hover");
  check(tt.includes("Price spikes"), "price: the spike hours' row");
  const monthTwo = two.slice(two.indexOf('data-fc-cut="month"'), two.indexOf('data-fc-cut="other"'));
  check(/data-fc-group="a">Texas</.test(monthTwo) && /data-fc-group="b">Mid-Atlantic</.test(monthTwo), "A and B: the score table names each place over its columns");
  check(/>Flexible</.test(monthTwo) && /<td[^>]*><span[^>]*title="License needed[^"]*"[^>]*>license needed<\/span><\/td>/.test(monthTwo), "A and B: the held place is one column that says license needed, with why on hover");
  const both = draw(FIX, { a: "region-tex", b: "ba-erco" });
  const monthBoth = both.slice(both.indexOf('data-fc-cut="month"'), both.indexOf('data-fc-cut="hour"'));
  check(/>2\.60<[\s\S]*>2\.08<[\s\S]*>1\.40<[\s\S]*>1\.12</.test(monthBoth), "A and B, demand: one row a month, Texas's score then ERCOT's in the same row");
  check(count(monthBoth, /<tr /g) === 4, "A and B, demand: two header rows and one row a month");
  // the metric follows the series unless the reader chose the other one
  check(draw(FIX, { s: "price", m: "mape" }).includes('data-fc-metric="mape"') && draw(FIX, { s: "price", m: "mae" }).includes('data-fc-metric="mae"'), "price: percent error when asked for");
  check(/<select name="m"[^>]*>\s*<option value="" selected="">Error in USD\/MWh \(MAE\)<\/option><option value="mape">/.test(two), "the score's list opens on the series' own metric, sent as no choice");
  const allTwo = two.slice(two.indexOf("data-fc-all="));
  check(/data-fc-all-blank="region-mida">license needed</.test(allTwo) && /data-fc-all-blank="ba-erco">too short a history</.test(allTwo), "every place, price: the held places are rows with their words");
  quiet(two, "A and B");

  // 3c. choices: a past day, a day not held, a place that is not one, the metric
  const d24 = draw(FIX, { day: "2026-11-24", m: "mae" });
  check(d24.includes('data-fc-day-of="2026-11-24"') && /data-n="fc\|a\|demand\|day\|erw"[^>]*>200</.test(d24), "a past day picked: 24 November, the ERW forecast's error 200 MW");
  check(d24.includes('data-fc-metric="mae"') && d24.includes('data-check="pf|predict/scores.json|rows/0/6" data-raw="905"'), "the error in MW: the score's key is the file's mae column");
  const gone = draw(FIX, { day: "2020-01-01" });
  check(/data-fc-blank="day\|a\|demand"/.test(gone) && text(gone).includes("2020-01-01, Texas: not held") && gone.includes("The file holds 2026-11-24 to 2026-11-25"), "a day the file does not hold is a blank that says what is held");
  const odd = draw(FIX, { a: "zz", b: "region-tex", s: "zz", m: "zz", day: "zz" });
  check(odd.includes('data-fc-series="demand"') && count(odd, /data-fc-tomorrow="/g) === 1 && odd.includes('data-fc-tomorrow="a" data-fc-shown="1"'), "an address the page does not know opens the defaults");
  const erco = draw(FIX, { a: "ba-erco", s: "price" });
  check(text(erco).includes("ERW forecast of price, Electric Reliability Council of Texas, Inc. (ERCO): too short a history") && erco.includes("fewer whole days of history than the method needs"), "a history too short is a blank with the file's reason");

  // 3c2. the contract's additions of 26 November 2026, and what the first read at a phone's width found
  check(/title="ERW forecast for Friday 27 Nov 2026: made [^"]*, 2 days before the day forecast \(2 is the day-ahead forecast/.test(html), "the place's hover says how many days before the day the forecast was made");
  check(t.includes("The last two years") && /href="\/events\/uri-2021"[^>]*>Event: uri 2021</.test(html), "the two-year cut has its row; an event's row opens the event's page");
  check(html.includes('href="/forecast/ledger?s=demand"') && html.includes('href="/forecast/ledger/stata?s=demand"') && !two.includes("/forecast/ledger"), "the ledger is offered where its file is on the site (demand), and not where it is not (price)");
  check(!tt.includes("no operator publishes") && two.includes("not published: no operator publishes a forecast of its day-ahead price"), "a long reason is the cell's hover; the cell says its first words");
  check(count(two, /data-not-held="1">not published</g) >= 4, "the operator's price cells say not published");
  // a method the file scores for none of a table's rows is not a column of blanks there: the operator has a row (with
  // its reason) over every hour scored and none by month
  const pm = two.slice(two.indexOf('data-fc-cut="month"'), two.indexOf('data-fc-cut="other"'));
  const po = two.slice(two.indexOf('data-fc-cut="other"'), two.indexOf("data-fc-all="));
  check(!pm.includes(">Operator<") && pm.includes(">Yesterday<") && po.includes(">Operator<"), "price: the operator is no column by month, where the file has no row of it, and is one over every hour, where it has");
  const noTomorrow = draw(FIX, { a: "ba-erco" });
  check(noTomorrow.includes('data-fc-tomorrow="a" data-fc-shown="0"') && text(noTomorrow).includes("ERW forecast of demand, Electric Reliability Council of Texas, Inc. (ERCO), Friday 27 Nov 2026: no data") && noTomorrow.includes("the place&#x27;s demand for the last whole day is not in the warehouse yet"), "a target day with no forecast is a blank that says why");
  check(noTomorrow.includes('data-fc-day-of="2026-11-25"') && noTomorrow.includes('data-fc-cut="month"'), "a place with no forecast for tomorrow still has its past days and its record");
  const long = draw(FIX, { a: "region-mida" });
  check(/data-fc-tall="42"/.test(long) && text(long).includes("(42 months)") && !/data-fc-tall=/.test(html) && t.includes("(2 months)"), "a month table of 42 rows keeps to a frame of its own; one of 2 rows does not");
  check(count(long.slice(long.indexOf('data-fc-cut="month"'), long.indexOf('data-fc-cut="hour"')), /<tr /g) === 43, "the long table holds every month: none is folded away");
  check(P.shortHeld("not published: no operator publishes") === "not published" && P.shortHeld(null) === "not held" && P.shortHeld("a reason that runs on for a whole sentence with no colon") === "not held", "the short words of a reason");
  check(P.eventHref("uri-2021") === "/events/uri-2021" && P.eventHref("../x") === null && P.eventHref("a b") === null, "only an event's own address is made a link");

  // 3d. the pure parts
  const tex = files[1];
  const q = P.queryOf({}, index);
  check(q.a === "region-tex" && q.b === null && q.s === "demand" && P.metricOf(q) === "mape" && P.hrefOf(q) === "/forecast", "the defaults and their address");
  check(P.hrefOf(q, { b: "region-mida", s: "price" }) === "/forecast?b=region-mida&s=price", "an address carries a choice");
  check(P.queryOf({ a: "region-tex", b: "region-tex" }, index).b === null, "B is never A");
  check(P.queryOf({ s: "price", m: "mae" }, index).m === null && P.queryOf({ s: "price", m: "mape" }, index).m === "mape" && P.queryOf({ m: "mape" }, index).m === null && P.queryOf({ m: "mae" }, index).m === "mae", "a metric is kept in the address only where it is not the series' own");
  const sc = P.dayScore(P.historyOf(tex.series.price).filter((x) => x.day === "2026-11-25"));
  check(sc && sc.hours === 24 && sc.methods.join() === "erw,yesterday,week_ago" && sc.mae.erw === 5, "a day's score leaves out a method with no forecast (the operator's price) and counts the same hours for the rest");
  const short = P.historyOf(tex.series.demand).filter((x) => x.day === "2026-11-25").map((x, i) => (i < 4 ? { ...x, operator: null } : x));
  check(P.dayScore(short).hours === 20, "an hour one method lacks is left out for every method");
  const csv = P.rowsCsv(tex, "https://example.test/forecast/rows?place=region-tex");
  const body = csv.split("\n").filter((l) => l && !l.startsWith("#"));
  check(body[0] === P.ROWS_HEAD.join(",") && body.length === 1 + 2 * (24 + 48), "the rows' CSV: its header and 144 lines (two series, tomorrow and two past days)");
  check(csv.startsWith("# Energy Research Warehouse (ERW): the ERW forecast for Texas") && csv.includes("never a published or official figure") && csv.includes("# From: https://example.test"), "the rows' CSV opens with its provenance");
  check(body.includes("region-tex,demand,MW,tomorrow,2026-11-27T23:00:00Z,2026-11-27,17,2026-11-26T13:00:00Z,live,57000,55500,58500,57300,,,"), "the rows' CSV: the 17:00 line of tomorrow");
  const held = P.rowsCsv(files[0], "u");
  check(held.includes("# price: no line. License needed") && !held.split("\n").some((l) => l.startsWith("region-mida,price")), "a held series has no line in the CSV and the header says why");
  const scsv = P.scoresCsv(scores, "u").split("\n").filter((l) => l && !l.startsWith("#"));
  check(scsv.length === 1 + rows.length && scsv[1] === "region-tex,demand,erw,all,,8760,905,1.81,", "the report card's CSV: every row of the file");
  for (const [name, spec, col] of [["rows", ROWS_READER, P.ROWS_HEAD], ["scores", SCORES_READER, P.SCORES_HEAD]]) {
    check([...spec.text, ...spec.figures].every((c) => col.includes(c)) && spec.show.every((c) => col.includes(c)) && col.includes(spec.count), `the ${name} readers name only columns the CSV has`);
    const stata = csvReader("do", "https://example.test/x", spec);
    check(!stata.includes("///") && spec.figures.every((c) => stata.includes(`destring ${c}, replace force`)) && !/\n\n\n/.test(stata), `the ${name} Stata reader keeps the owner's rules`);
    const loop = stata.slice(stata.indexOf("while r(eof)"), stata.indexOf("file close"));
    check(!/\n\n/.test(loop.slice(0, loop.lastIndexOf("}"))), `the ${name} Stata reader has no empty line inside its loop`);
    check(csvReader("py", "https://example.test/x", spec).includes("pd.read_csv") && !stata.includes(dash), `the ${name} Python reader loads the rows`);
  }
  check(P.blankWords("license needed") === "license needed" && P.blankWords("anything", true) === "not built yet", "the blank's words");
  check(P.isShown({ example: true }, { status: "shown" }) === false && P.isShown({}, { status: "shown" }) === true, "an example file shows nothing, whatever its status says");
  // a day of 25 hours (the autumn clock change): the repeated hour is drawn twice and named
  const fall = { ...tex.series.demand, history: [["2026-11-01T06:00:00Z", "2026-11-01", 1, null, "backtest", 1, 0, 2, 1, 1, 1, 1], ["2026-11-01T07:00:00Z", "2026-11-01", 1, null, "backtest", 1, 0, 2, 1, 1, 1, 1]] };
  check(P.historyOf(fall).map((x) => x.label).join("|") === "01:00|01:00 (again)", "the repeated hour of the autumn clock change is named");
} finally {
  if (!KEEP) fs.rmSync(FIX, { recursive: true, force: true });
}

if (fails.length) { console.log(`FAIL ${fails.length} of ${n}:\n  ${fails.join("\n  ")}`); process.exitCode = 1; }
else console.log(`ok: ${n} checks of /forecast (no files, the contract's examples, a fixture of the contract's shape)`);
