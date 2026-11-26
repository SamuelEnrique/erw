// Energy Research Warehouse (ERW) site, session 10405 (chain 720, part E): the day's peak and the days after tomorrow on
// /forecast (the contract's changes of session 10601: a place file's series.demand.peak, and ahead.json), drawn to
// HTML with the site's own code, without a build.
//   node --import ./scripts/events-page-register.mjs scripts/test-forecast-peak.mjs
// The fixture is the one scripts/test-forecast.mjs writes (its --keep), with a peak added to Texas's demand and a file
// of the days ahead: made-up values, each file marked as a test's fixture, which the site's own folder never reads.
// Held here: a page with neither is the page as it was; the peak's table draws every method the same, the operator
// where it is the closer one included, and a method the file does not score as a blank; the days after tomorrow are
// the horizons after the place's own day (the day the place's file already draws is not drawn twice), a horizon the
// file does not show is a row that says so with the file's reason, and the highest and lowest hour are the file's;
// every figure carries its key into its file; price draws neither; the download and its readers. No network. Exit 0
// when every check holds, 1 otherwise.
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const { ForecastView } = await import("../app/forecast/view.tsx");
const P = await import("../lib/predict.ts");
const { csvReader } = await import("../lib/csvreader.ts");
const { AHEAD_READER } = await import("../app/forecast/ahead/reader.ts");

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
  check(!/outperform|signal|should buy|should sell|so what|\bbetter\b|\bbeats?\b|\bwins?\b/i.test(t.replace(/shown only where it beats it/g, "")), `${where}: a word of advice or a view`);
};
const fig = (html, file, keyPath, raw, shown) => html.includes(`data-check="pf|predict/${file}|${keyPath}" data-raw="${raw}"`) && (shown === undefined || new RegExp(`data-check="pf\\|predict/${file.replace(".", "\\.")}\\|${keyPath.replace(/[/]/g, "\\/")}" data-raw="${String(raw).replace(".", "\\.")}"[^>]*>(<span[^>]*>)?${shown.replace(".", "\\.")}<`).test(html));
const between = (html, from, to) => { const i = html.indexOf(from); if (i < 0) return ""; const j = html.indexOf(to, i + from.length); return html.slice(i, j < 0 ? undefined : j); };

// ---- The fixture: the forecast test's own, then a peak and the days ahead ---------------------------------------------
const FIX = fs.mkdtempSync(path.join(os.tmpdir(), "erw-c720-peak-"));
execFileSync(process.execPath, ["--import", "./scripts/events-page-register.mjs", "scripts/test-forecast.mjs", "--keep", FIX], { cwd: SITE, stdio: "pipe" });
const FIXTURE = "scripts/test-forecast-peak.mjs: made-up values, a test's fixture";
const load = (name) => JSON.parse(fs.readFileSync(path.join(FIX, name), "utf8"));
const save = (name, v) => fs.writeFileSync(path.join(FIX, name), JSON.stringify(v));

// 1. the page as it was: no peak in a place file, no file of the days ahead
{
  const html = draw(FIX, { a: "region-tex" });
  check(html.includes('data-fc-state="files"') && html.includes('data-fc-shown="1"'), "the base fixture is not drawn");
  check(!html.includes("data-fc-peak") && !html.includes("data-fc-ahead") && !html.includes('data-fc-download="ahead"'), "with no peak and no file of the days ahead, the page draws one of them");
}

const pk = (mae, mape, exact, within) => ({ mae, mape, hour_exact_pct: exact, hour_within_1_pct: within });
const tex = load("region-tex.json");
check(tex.series.demand.status === "shown" && tex.series.demand.target_day === "2026-11-27", "the base fixture's Texas is not the one this test builds on");
tex.series.demand.peak = {
  what: "the day's highest hourly demand and its local hour; a method's peak is the highest of its own hourly forecasts for the day, and the hour of it",
  tomorrow: { local_hour: 17, ts_utc: "2026-11-27T23:00:00Z", erw: 57000, lo: 55500, hi: 58500 },
  // the operator is the closer one in both spans, on purpose: it is drawn as any other
  last_2_years: { days: 700, first_day: "2024-11-26", last_day: "2026-11-25", methods: { erw: pk(2100.4, 3.3, 41.5, 70.25), operator: pk(900.2, 1.4, 60, 88.1), yesterday: pk(2500, 4.1, 35.5, 66.6), week_ago: pk(3100.7, 5.2, 33.3, 61.2) } },
  // the backtest holds no score of the operator: a blank, not a nought
  backtest: { days: 2600, first_day: "2019-07-01", last_day: "2026-11-25", methods: { erw: pk(2200.6, 3.5, 42, 71.5), yesterday: pk(2600.1, 4.3, 36, 67), week_ago: pk(3200.9, 5.4, 34, 62) } },
};
save("region-tex.json", tex);
const off = 6;
const iso = (day, hour) => new Date(Date.parse(`${day}T00:00:00Z`) + (hour + off) * 3_600_000).toISOString().replace(".000Z", "Z");
// a day's forecast: it peaks at `top` (base + 1,000 an hour up to it, then down), band 1,500 either side
const dayRows = (day, base, top) => Array.from({ length: 24 }, (_, hr) => { const v = base + 1000 * (hr <= top ? hr : 2 * top - hr); return [iso(day, hr), hr, v, v - 1500, v + 1500]; });
const horizon = (hd, after, day, shown, base, top, sc) => ({ horizon_days: hd, days_after_tomorrow: after, target_day: day, shown, held: shown ? null : "not shown: over the last two years the same hour a week ago had the lower error at this horizon",
  last_2_years: { hours: 17000 + hd, mae: { regression: sc[0], week_ago: sc[1], yesterday: sc[2] }, mape: { regression: sc[3], week_ago: sc[4], yesterday: sc[5] }, operator_day_ahead_mae_same_hours: 640.5 },
  band_coverage_pct: 80.5, forecast_columns: ["ts_utc", "local_hour", "erw", "lo", "hi"], forecast: shown ? dayRows(day, base, top) : null });
const ahead = { fixture: FIXTURE, contract: "docs/state/page_files_predict.md", built: "2026-11-26T14:05:00Z", tier: "derived", label: "ERW forecast", method_notes: { demand: "docs/methods/predict.md" },
  made_utc: "2026-11-26T13:00:00Z", what: "The demand forecast two to seven days ahead. Each horizon is scored over the last two years against the same hour a week ago, and shown only where it beats it.",
  places: [{ place: "ba-erco", time: "America/Chicago", last_whole_day: "2026-11-24", horizons: [] },
    { place: "region-tex", time: "America/Chicago", last_whole_day: "2026-11-24", horizons: [
      horizon(3, 0, "2026-11-27", true, 40000, 17, [1400.4, 1800.6, 1700, 2.9, 3.9, 3.6]),   // the place's own day: its file draws it
      horizon(5, 2, "2026-11-29", false, 0, 0, [1900.2, 1800.6, 1750, 4.1, 3.9, 3.7]),          // not shown, and out of order in the file
      horizon(4, 1, "2026-11-28", true, 41000, 16, [1500.4, 1800.6, 1700, 3.1, 3.9, 3.6]),
      horizon(6, 3, "2026-11-30", true, 39000, 18, [1650.5, 1801.2, 1720, 3.4, 3.9, 3.6]),
    ] }] };
save("ahead.json", ahead);

// ---- 2. The pure functions --------------------------------------------------------------------------------------------
{
  const e = P.aheadOf(ahead, "region-tex");
  check(e && e.pi === 1, "aheadOf: the place's position in the file");
  check(P.aheadOf(ahead, "region-zz") === null && P.aheadOf(null, "region-tex") === null && P.aheadOf({ ...ahead, example: true }, "region-tex") === null, "aheadOf: a place not in the file, no file, an example");
  const days = P.aheadDays(e.place, "2026-11-27");
  check(JSON.stringify(days.map((d) => d.h.target_day)) === JSON.stringify(["2026-11-28", "2026-11-29", "2026-11-30"]), `aheadDays: the days after the place's own, in the calendar's order: ${days.map((d) => d.h.target_day)}`);
  check(JSON.stringify(days.map((d) => d.hi)) === JSON.stringify([2, 1, 3]), "aheadDays: each day keeps its position in the file (a figure's key names it)");
  check(days[0].top.v === 57000 && days[0].top.hour === 16 && days[0].low.v === 41000 && days[0].low.hour === 0, "aheadDays: the highest and the lowest hour of a day");
  check(days[1].hours.length === 0 && days[1].top === null, "aheadDays: a horizon the file does not show has no hour");
  check(P.aheadDays(e.place, null).length === 3, "aheadDays: with no day of the place's own, the file's days after tomorrow");
  check(P.aheadMethod({}) === "regression" && P.aheadMethod({ method: "regression_recent" }) === "regression_recent", "aheadMethod");
  check(P.methodWords("regression_recent") === "Regression with the recent days" && P.methodShort("regression_recent") === "Regression, recent", "the fourth method's words");
}

// ---- 3. Demand, one place: the peak's table and the days after tomorrow -----------------------------------------------
{
  const html = draw(FIX, { a: "region-tex" });
  const peak = between(html, 'data-fc-peak="1"', "data-fc-cut=");
  check(peak.length > 0, "the peak's table is not drawn");
  check(count(peak, /<tr class="border-b/g) === 6, `the peak's table: ${count(peak, /<tr class="border-b/g)} rows, not six (two spans, three measures)`);
  check(text(peak).replace(/\s+([:,])/g, "$1").includes("The day's peak: the error of its size, %, and how often its hour was the day's, % of days"), "the peak's heading");
  check(fig(html, "region-tex.json", "series/demand/peak/last_2_years/days", 700, "700") && fig(html, "region-tex.json", "series/demand/peak/backtest/days", 2600, "2,600"), "the peak: the days scored, keyed");
  check(fig(html, "region-tex.json", "series/demand/peak/last_2_years/methods/erw/mape", 3.3, "3.30"), "the peak: the ERW forecast's error of its size, keyed and written");
  check(fig(html, "region-tex.json", "series/demand/peak/last_2_years/methods/operator/mape", 1.4, "1.40"), "the peak: the operator's, where it is the closer one, is drawn as any other");
  check(fig(html, "region-tex.json", "series/demand/peak/last_2_years/methods/erw/hour_exact_pct", 41.5, "41.50") && fig(html, "region-tex.json", "series/demand/peak/last_2_years/methods/week_ago/hour_within_1_pct", 61.2, "61.20"), "the peak: the hour's shares, keyed");
  check(!html.includes("series/demand/peak/backtest/methods/operator/") && count(peak, /data-not-held="1"/g) === 3, `the peak: a method the file does not score is three blanks (${count(peak, /data-not-held="1"/g)})`);
  check(peak.includes("The file&#x27;s words: the day&#x27;s highest hourly demand"), "the peak: the file's words on hover");
  // the days after tomorrow
  check(html.includes('data-fc-ahead="a" data-fc-ahead-days="3" data-fc-ahead-shown="2"'), "the days ahead: three days after the place's own, two shown");
  check(!html.includes("places/1/horizons/0/"), "the days ahead: the place's own day is drawn twice");
  const block = between(html, 'data-fc-ahead-block="1"', 'id="record"');
  check(text(block).includes("Texas: the days after Friday 27 Nov 2026") && text(block).includes("ERW forecast of demand: Saturday 28 Nov 2026 to Monday 30 Nov 2026"), "the days ahead: the heading and the chart's title");
  check(count(block, /data-svg-chart/g) >= 1 || block.includes("<svg"), "the days ahead: no chart");
  check(fig(html, "ahead.json", "places/1/horizons/2/forecast/16/2", 57000, "57,000") && text(block).includes("57,000 at 16:00"), "the days ahead: a day's highest hour, keyed, with its hour");
  check(fig(html, "ahead.json", "places/1/horizons/2/forecast/0/2", 41000, "41,000") && fig(html, "ahead.json", "places/1/horizons/3/forecast/18/2", 57000, "57,000"), "the days ahead: the lowest hour, and another day's highest");
  check(fig(html, "ahead.json", "places/1/horizons/2/last_2_years/mape/regression", 3.1, "3.10") && fig(html, "ahead.json", "places/1/horizons/2/last_2_years/mape/week_ago", 3.9, "3.90"), "the days ahead: the horizon's error and the week-ago hour's, keyed");
  check(fig(html, "ahead.json", "places/1/horizons/2/last_2_years/operator_day_ahead_mae_same_hours", 640.5, "641") && fig(html, "ahead.json", "places/1/horizons/2/band_coverage_pct", 80.5, "80.50"), "the days ahead: the operator's day-ahead error in MW and the band's share");
  check(html.includes('data-fc-ahead-blank="2026-11-29"') && block.includes("not shown: over the last two years the same hour a week ago had the lower error at this horizon") && !html.includes("places/1/horizons/1/"), "the days ahead: a horizon the file does not show is a row that says so, with the reason, and no figure");
  check(block.includes("shown only where it beats it"), "the days ahead: the file's own words on which days are shown, on hover");
  check(html.includes('data-fc-download="ahead"') && html.includes('href="/forecast/ahead"') && html.includes('href="/forecast/ahead/python"') && html.includes('href="/forecast/ahead/stata"'), "the days ahead: the download, with its two readers");
  check(html.indexOf('data-fc-ahead-block="1"') > html.indexOf('data-fc-tomorrow="a"') && html.indexOf('data-fc-ahead-block="1"') < html.indexOf('id="record"'), "the days ahead stand under Tomorrow, before the record");
  check(html.indexOf('data-fc-peak="1"') > html.indexOf('data-fc-summary="1"') && html.indexOf('data-fc-peak="1"') < html.indexOf('data-fc-cut="month"'), "the peak stands after the summary, before the months");
  quiet(html, "demand, one place");
}

// ---- 4. The error in megawatts; two places; price -----------------------------------------------------------------------
{
  const html = draw(FIX, { a: "region-tex", m: "mae" });
  check(fig(html, "region-tex.json", "series/demand/peak/last_2_years/methods/erw/mae", 2100.4, "2,100") && fig(html, "region-tex.json", "series/demand/peak/backtest/methods/week_ago/mae", 3200.9, "3,201"), "the peak in MW: whole megawatts, keyed");
  check(fig(html, "ahead.json", "places/1/horizons/2/last_2_years/mae/regression", 1500.4, "1,500") && fig(html, "ahead.json", "places/1/horizons/3/last_2_years/mae/week_ago", 1801.2, "1,801"), "the days ahead in MW: whole megawatts, keyed");
  quiet(html, "demand, MW");
  const two = draw(FIX, { a: "region-tex", b: "ba-erco" });
  check(two.includes('data-fc-ahead="a" data-fc-ahead-days="3"') && two.includes('data-fc-ahead="b" data-fc-ahead-days="0"'), "two places: one with days ahead, one whose entry holds none");
  check(count(two, /data-fc-ahead-table="/g) === 1, "two places: a table for the place that has days, none for the one that has not");
  check(between(two, 'data-fc-peak="1"', "data-fc-cut=").includes('data-fc-group="b"'), "two places: the peak's table has both places' columns");
  quiet(two, "demand, two places");
  const price = draw(FIX, { a: "region-tex", s: "price" });
  check(!price.includes("data-fc-peak") && !price.includes("data-fc-ahead") && !price.includes('data-fc-download="ahead"'), "price draws the peak or the days ahead of demand");
}

// ---- 5. A file of the days ahead that is an example, or missing, draws nothing -----------------------------------------
{
  save("ahead.json", { ...ahead, example: true });
  const html = draw(FIX, { a: "region-tex" });
  check(!html.includes("data-fc-ahead") && !html.includes('data-fc-download="ahead"') && html.includes('data-fc-peak="1"'), "an example file of the days ahead is drawn, or takes the peak with it");
  save("ahead.json", ahead);
}

// ---- 6. The download and its readers -----------------------------------------------------------------------------------
{
  const url = "https://example.invalid/forecast/ahead";
  const csv = P.aheadCsv(ahead, url);
  const lines = csv.trimEnd().split("\n");
  const body = lines.filter((x) => !x.startsWith("#"));
  check(body[0] === P.AHEAD_HEAD.join(",") && body.length === 1 + 3 * 24, `the CSV: its head and ${body.length - 1} rows, not the 72 of the three horizons shown`);
  check(body[1] === "region-tex,2026-11-27,3,2026-11-27T06:00:00Z,0,regression,40000,38500,41500", `the CSV's first row: ${body[1]}`);
  check(csv.includes("horizons left out: 1") && csv.includes(`# From: ${url}`) && csv.includes("never a published or official figure"), "the CSV's provenance: what is left out, where from, what it is");
  check(P.aheadCsv({ ...ahead, example: true }, url).trimEnd().split("\n").filter((x) => !x.startsWith("#")).length === 1, "the CSV of an example file holds a row");
  check(!csv.includes(dash), "the CSV: an em dash");
  for (const [kind, as] of [["py", "pd.read_csv"], ["do", "import delimited"]]) {
    const r = csvReader(kind, url, AHEAD_READER);
    check(r.includes(url) && r.includes(as) && !r.includes(dash), `the ${kind} reader: the address, the read, no em dash`);
    for (const c of [...AHEAD_READER.text, ...AHEAD_READER.figures, ...AHEAD_READER.show, AHEAD_READER.count]) check(P.AHEAD_HEAD.includes(c), `the reader names a column the CSV has not: ${c}`);
  }
  const scores = load("scores.json");
  const sc = scores.rows_columns.indexOf("series");
  const withPeak = { ...scores, rows: [...scores.rows, scores.rows[0].map((v, i) => (i === sc ? "demand_peak" : v))] };
  check(!P.scoresCsv(scores, url).includes("demand_peak") && P.scoresCsv(withPeak, url).includes("# series demand_peak:") && P.scoresCsv(withPeak, url).includes("holds the count of days"), "the report card's CSV says what a row of the peak counts, only when it has one");
}

fs.rmSync(FIX, { recursive: true, force: true });
if (fails.length) { console.log(`FAIL ${fails.length} of ${n}:\n  ${fails.join("\n  ")}`); process.exitCode = 1; }
else console.log(`ok: ${n} checks of /forecast's peak and days ahead (a fixture of the contract's shape)`);
