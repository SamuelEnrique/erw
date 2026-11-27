// Energy Research Warehouse (ERW) site, session 10409 (chain 720, part E): what the forecast's page files gained on
// 27 November 2026, on /forecast (the contract's dated lines of that day: in a place file's series.demand,
// operator_filing, with_weather_forecast and net_demand; in every shown series, band_coverage; the files
// wind_solar.json and rt_price.json), drawn to HTML with the site's own code, without a build.
//   node --import ./scripts/events-page-register.mjs scripts/test-forecast-lines.mjs [--keep <folder>]
// The fixture is the one scripts/test-forecast.mjs writes (its --keep), with those fields added to Texas and a file of
// wind and solar: made-up values, each file marked as a test's fixture, which the site's own folder never reads.
// Held here: a page with none of them is the page as it was; net demand, wind and solar are drawn for the day forecast
// now and scored, every method the same weight, the operator's where it is the closer one included; a past day of wind
// and solar beside what happened; the operator's filing says, where months are flagged, that the filed forecast is not
// the operator's own in those months, and sets the months that pass beside every month; the line with the weather
// forecast is a separate line, never called the ERW forecast, in no chart, and says too few days to judge below the
// file's own minimum; the band's record by line, by hour and by month; every figure carries its key into its file;
// price draws its own band and none of demand's views, and the real-time price at its hub beside the hub's day-ahead
// price (the comparator, never an ERW method), a day with no forecast being a blank with the file's reason. No network.
// Exit 0 when every check holds, 1 otherwise.
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const { ForecastView } = await import("../app/forecast/view.tsx");
const L = await import("../lib/predictlines.ts");

const fails = [];
let n = 0;
const check = (ok, what) => { n++; if (!ok) fails.push(what); };
const draw = (dir, query = {}) => { process.env.ERW_PREDICT_DIR = dir; return renderToStaticMarkup(h(ForecastView, { query })); };
const text = (html) => html.replace(/<title>[^<]*<\/title>/g, " ").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&amp;/g, "&").replace(/\s+/g, " ");
const dash = String.fromCharCode(0x2014);
const count = (html, re) => (html.match(re) ?? []).length;
const quiet = (html, where) => {
  const t = text(html);
  check(!/\bundefined\b|\bNaN\b|\bnull\b|\[object Object\]/.test(t), `${where}: "undefined", "NaN" or "null" on the page`);
  check(!html.includes(dash), `${where}: an em dash`);
  check(!/outperform|signal|should buy|should sell|so what|\bbetter\b|\bbeats?\b|\bwins?\b/i.test(t.replace(/shown only where it beats it/g, "")), `${where}: a word of advice or a view`);
};
const esc = (s) => String(s).replace(/[.*+?^${}()|[\]\\/]/g, "\\$&");
/** A figure of the page: its key into its file, its raw value and, when given, the words it is written in. */
const fig = (html, file, keyPath, raw, shown) => new RegExp(`data-check="pf\\|predict/${esc(file)}\\|${esc(keyPath)}" data-raw="${esc(raw)}"[^>]*>(<span[^>]*>)?${shown === undefined ? "" : `${esc(shown)}<`}`).test(html);

const KEEP = process.argv.includes("--keep") ? process.argv[process.argv.indexOf("--keep") + 1] : null;
if (KEEP) fs.mkdirSync(KEEP, { recursive: true });
const FIX = KEEP ?? fs.mkdtempSync(path.join(os.tmpdir(), "erw-c720-lines-"));
execFileSync(process.execPath, ["--import", "./scripts/events-page-register.mjs", "scripts/test-forecast.mjs", "--keep", FIX], { cwd: SITE, stdio: "pipe" });
const FIXTURE = "scripts/test-forecast-lines.mjs: made-up values, a test's fixture";
const load = (name) => JSON.parse(fs.readFileSync(path.join(FIX, name), "utf8"));
const save = (name, v) => fs.writeFileSync(path.join(FIX, name), JSON.stringify(v));

// ---- 1. As the files stood before 27 November: none of the views ------------------------------------------------------
const before = draw(FIX, {});
{
  check(before.includes('data-fc-state="files"') && before.includes('data-fc-tomorrow="a" data-fc-shown="1"'), "the base fixture is not the one this test builds on");
  check(before.includes('data-fc-net="a" data-fc-net-hours="none"') && before.includes('data-fc-filing="a" data-fc-filing-months="none"') && before.includes('data-fc-wwf="a" data-fc-wwf-days="none"') && before.includes('data-fc-band="a" data-fc-band-rows="0"'), "a place whose file holds none of the new fields: each view's place is empty");
  check(!/net demand|filed forecast|weather forecast|Inside the band/i.test(text(before)), "a page with none of the new fields says nothing of them");
  check(!before.includes("wind_solar.json") && !before.includes("data-fc-blank=\"net|"), "no figure and no blank of a view the files do not hold");
}

// ---- The fixture --------------------------------------------------------------------------------------------------------
const tex = load("region-tex.json");
const dem = tex.series.demand;
const TS = dem.tomorrow.map((r) => r[0]);
const demandAt = (hr) => dem.tomorrow[hr][2];
const windAt = (hr) => 6000.5 - 100 * hr;                                   // highest at 00:00: 6,000.5
const solarAt = (hr) => (hr >= 8 && hr <= 16 ? 2000 + 500 * (4 - Math.abs(12 - hr)) : 0);   // highest at 12:00: 4,000
const netAt = (hr) => demandAt(hr) - windAt(hr) - solarAt(hr);
const span2 = { first_day: "2024-11-26", last_day: "2026-11-25" }, spanAll = { first_day: "2019-07-01", last_day: "2026-11-25" }, spanOp = { first_day: "2026-09-30", last_day: "2026-11-25" };
const mw = (span, hours, mae, pct) => ({ ...span, hours, mae_mw: mae, nmae_pct: pct });
const band = (inside, below, above, hours) => ({ nominal_pct: 80.0, hours, inside_pct: inside, below_pct: below, above_pct: above, by_local_hour_inside_pct: Array.from({ length: 24 }, (_, hr) => Number((inside - 2 + hr / 6).toFixed(1))),
  by_month_columns: ["month", "hours", "inside_pct"], by_month: [["2026-09", 720, 90.7], ["2026-10", 744, 82.4], ["2026-11", 601, 68.5]] });
dem.tomorrow_from = "the ledger: the forecast first made for this day, kept as made (a later run the same day does not replace it); the method chosen now is regression_recent";
dem.operator_filing = { what: "the operator's day-ahead forecast as filed on Form EIA-930, set against the demand it forecasts", tolerance_pct: 5.0,
  months_columns: ["month", "hours", "operator_pct_of_demand", "flagged"], months: [["2026-08", 744, 100.4, false], ["2026-09", 720, 93.8, true], ["2026-10", 744, 99.25, false]],
  months_flagged: 1, months_held: 3, shift_mape_last_2_years: { "-1": 3.61, 0: 2.09, 1: 1.75 }, best_shift_hours: 1,
  // on the months that pass the ERW forecast is the closer of the two, on every month the operator's is: both are drawn the same
  sound_last_2_years: { ...span2, hours: 16800, mae: { erw: 880.4, operator: 990.6, yesterday: 2300.5, week_ago: 3200.5 }, mape: { erw: 1.76, operator: 1.98, yesterday: 4.6, week_ago: 6.4 } } };
dem.with_weather_forecast = { what: "the regression with the weather, fitted on the airport's observed temperature and applied with the National Weather Service's hourly forecast for the airport", airport: "KDFW", min_days: 30, days: 17, status: "too_few_days",
  all: { first_day: "2026-10-16", last_day: "2026-11-19", hours: 409, mae: { with_weather_forecast: 1933.03, with_airport_weather_known: 1947.68, erw: 2713.99, operator: 605.33, regression: 2941.88, regression_recent: null },
    mape: { with_weather_forecast: 3.809, with_airport_weather_known: 3.838, erw: 5.327, operator: 1.181, regression: 5.783, regression_recent: null } },
  tomorrow_columns: ["ts_utc", "local_hour", "with_weather_forecast"], tomorrow: TS.map((ts, hr) => [ts, hr, demandAt(hr) + 250.5]), tomorrow_issue_utc: "2026-11-26T11:21:09Z" };
dem.net_demand = { what: "net demand: the demand less the output of wind and solar", status: "shown", wind_solar_place: "region-tex",
  last_2_years: mw(span2, 17172, { erw: 5539.7, yesterday: 6824.8 }, { erw: 15.77, yesterday: 19.43 }), backtest: mw(spanAll, 64568, { erw: 5138.2, yesterday: 6434.4 }, { erw: 14.94, yesterday: 18.71 }),
  with_operator: mw(spanOp, 1368, { erw: 5979.6, yesterday: 7205.5, operator: 1914.0 }, { erw: 17.06, yesterday: 20.56, operator: 5.46 }),
  tomorrow_columns: ["ts_utc", "local_hour", "erw"], tomorrow: TS.map((ts, hr) => [ts, hr, netAt(hr)]) };
dem.band_coverage = band(80.3, 9.4, 10.3, 17400);
tex.series.price.band_coverage = band(77.9, 11.3, 10.9, 17446);
const HIST = dem.history.slice(0, 48).map((r) => [r[0], r[1], r[2]]);   // two past days: ts, local day, local hour
const fuel = (at, opAt, method, pct) => ({ status: "shown", method, method_mae_last_2_years: { yesterday: 6550.6, profile7: 5689.0, regression: 5382.3 }, target_series: "EIA-930's net generation for the region (a test's fixture)",
  operator: opAt ? "ERCOT's short-term wind and solar forecasts (a test's fixture)" : null, operator_held: opAt ? null : "not held: the warehouse holds no forecast of this region's wind or solar by its operator",
  made_utc: "2026-11-26T18:00:00Z", inputs_through_utc: "2026-11-26T05:00:00Z", target_day: "2026-11-27", horizon_days: 2, band: "the 10th and 90th percentile of the chosen method's own past errors at the same local hour over 365 days",
  band_coverage_pct: pct, band_coverage: band(pct, 10.9, Number((89.1 - pct).toFixed(1)), 16923),
  tomorrow_columns: ["ts_utc", "local_hour", "erw", "lo", "hi", "operator"], tomorrow: TS.map((ts, hr) => [ts, hr, at(hr), at(hr) - 400, at(hr) + 400, opAt ? opAt(hr) : null]), tomorrow_held: null,
  summary: { last_2_years: mw(span2, 17186, { erw: 5382.3, yesterday: 6550.6, profile7: 5689.0, regression: 5382.3 }, { erw: 40.46, yesterday: 49.24, profile7: 42.76, regression: 40.46 }),
    backtest: mw(spanAll, 64587, { erw: 4890.6, yesterday: 6015.3, profile7: 5165.4, regression: 4890.6 }, { erw: 41.26, yesterday: 50.75, profile7: 43.58, regression: 41.26 }),
    with_operator: opAt ? mw(spanOp, 1368, { erw: 5833.0, yesterday: 6398.2, profile7: 6248.8, regression: 5833.0, operator: 1457.7 }, { erw: 52.99, yesterday: 58.13, profile7: 56.77, regression: 52.99, operator: 13.24 }) : null, with_operator_available: null },
  history_columns: ["ts_utc", "local_day", "local_hour", "erw", "lo", "hi", "operator", "actual", "yesterday"], history: HIST.map(([ts, day, hr]) => [ts, day, hr, at(hr), at(hr) - 400, at(hr) + 400, opAt ? opAt(hr) : null, at(hr) + 150, at(hr) - 90]) });
const ws = { fixture: FIXTURE, contract: "docs/state/page_files_predict.md", built: "2026-11-27T03:28:48Z", tier: "derived", label: "ERW forecast", method_note: "docs/methods/predict_wind_solar.md",
  made_rule: "made at 20:00 UTC the day before the target local day, from output through two days before it; no weather enters", units: "MW",
  methods: [{ id: "erw", words: "the method the rule chose for the place and fuel" }, { id: "operator", words: "the operator's own forecast, where the warehouse holds it" }, { id: "yesterday", words: "the same local hour of the latest whole day read" }, { id: "profile7", words: "the mean of the same local hour over the seven latest whole days read" }],
  // Texas is the second place, so a figure's key must name its position in the file
  places: [{ place: "region-cal", name: "California", time: "America/Los_Angeles", fuels: {} }, { place: "region-tex", name: "Texas", time: "America/Chicago", fuels: { wind: fuel(windAt, (hr) => windAt(hr) + 120, "regression", 79.8), solar: fuel(solarAt, null, "profile7", 75.7) } }],
  rows_columns: ["place", "fuel", "method", "cut", "key", "hours", "mae_mw", "nmae_pct", "held"], rows: [["region-tex", "wind", "erw", "all", "", 64587, 4890.6, 41.26, null]] };
save("region-tex.json", tex);
save("wind_solar.json", ws);
const TEX = "region-tex.json", WS = "wind_solar.json";

// ---- 2. The library ------------------------------------------------------------------------------------------------------
{
  const months = L.filingMonths(dem.operator_filing);
  check(months.length === 3 && months[1].flagged === true && months[1].pct === 93.8 && months[1].i === 1 && months[0].flagged === false, "filingMonths: the months by the file's column names, each with its place");
  check(L.filingShift(dem.operator_filing) === 1 && L.filingShift({ best_shift_hours: 0 }) === null && L.filingShift(null) === null, "filingShift: a shift of nought is none");
  check(L.tooFewDays(dem.with_weather_forecast) === true && L.tooFewDays({ status: "scored", days: 40, min_days: 30 }) === false && L.tooFewDays({ days: 12, min_days: 30 }) === true && L.tooFewDays(null) === false, "tooFewDays: the file's status, or fewer days than its own minimum");
  check(L.windSolarOf(ws, "region-tex")?.pi === 1 && L.windSolarOf(ws, "ba-none") === null && L.windSolarOf({ ...ws, example: true }, "region-tex") === null && L.windSolarOf(null, "region-tex") === null, "windSolarOf: a place by its id with its position; an example file shows nothing");
  const hours = L.lineHours(ws.places[1].fuels.wind.tomorrow_columns, ws.places[1].fuels.wind.tomorrow, "operator");
  check(hours.length === 24 && hours[0].erw === 6000.5 && hours[0].other === 6120.5 && hours[3].lo === windAt(3) - 400 && hours[23].i === 23, "lineHours: a line's hours by the file's column names, the line beside it included");
  const past = L.lineHours(ws.places[1].fuels.wind.history_columns, ws.places[1].fuels.wind.history, "operator");
  check(L.lineDays(past).join(" ") === "2026-11-25 2026-11-24" && L.lineDefaultDay(past) === "2026-11-25" && L.lineDefaultDay([]) === null, "lineDays and lineDefaultDay: the days a line holds, the newest with a forecast and what happened");
  check(L.bandMonths(dem.band_coverage).map((m) => `${m.month}=${m.inside}`).join(" ") === "2026-09=90.7 2026-10=82.4 2026-11=68.5", "bandMonths: the months in the file's own order");
  check(L.mwMetricOf("mape") === "nmae_pct" && L.mwMetricOf("mae") === "mae_mw", "the page's two scores, said for the megawatt lines");
  const cuts = L.lineScores(ws.rows_columns, ws.rows, { place: "region-tex", fuel: "wind" }, ["mae_mw", "nmae_pct"]);
  check(cuts.get("all")?.cells.get("|erw")?.values.mae_mw === 4890.6 && cuts.get("all")?.cells.get("|erw")?.i === 0 && L.lineScores(ws.rows_columns, ws.rows, { place: "region-tex", grid: "x" }, ["mae_mw"]).size === 0, "lineScores: a file's rows by cut, key and method; a column the file does not name matches nothing");
}

// ---- 3. Tomorrow: wind, solar and net demand ----------------------------------------------------------------------------
const page = draw(FIX, {});
const t = text(page);
quiet(page, "demand");
{
  check(page.includes('data-fc-net="a" data-fc-net-hours="24"') && t.includes("Texas: wind, solar and net demand"), "the block of net demand, 24 hours");
  check(fig(page, TEX, "series/demand/net_demand/tomorrow/0/2", netAt(0), "34,000") && /data-n="fc\|a\|net\|low"/.test(page) && t.includes("Lowest net demand"), "the lowest hour of net demand is the file's, written whole, with its key");
  check(fig(page, TEX, "series/demand/net_demand/tomorrow/17/2", netAt(17)) && /data-n="fc\|a\|net\|high"/.test(page), "the highest hour of net demand is the file's");
  check(fig(page, WS, "places/1/fuels/wind/tomorrow/0/2", 6000.5, "6,001") && fig(page, WS, "places/1/fuels/solar/tomorrow/12/2", 4000, "4,000") && t.includes("Highest wind hour") && t.includes("Highest solar hour"), "the highest hour of wind and of solar, each with its key into the wind and solar file by the place's position there");
  check(/aria-label="ERW forecast of demand, of wind and solar output and of net demand for Texas, Friday 27 Nov 2026/.test(page), "the chart's name says what it draws");
  // the chart's title carries the words ERW forecast; its lines' names are short, so a phone's plot keeps its width
  check(t.includes("ERW forecast of demand, wind, solar and net demand: Friday 27 Nov 2026"), "the chart's title carries the words ERW forecast");
  const net = page.slice(page.indexOf('data-fc-net="a"'), page.indexOf("data-fc-net-table="));
  for (const name of ["Demand", "Net demand", "Wind", "Solar"]) check(new RegExp(`>${name}<`).test(net), `the chart's line "${name}"`);
  check(!/ERW forecast: (demand|net demand|wind|solar)/.test(page), "no line's name repeats the title's words at the plot's edge");
  check(page.indexOf("data-fc-net-table=\"a\"") > page.indexOf('data-fc-net="a"') && page.includes('data-fc-net-block="1"'), "the tables stand under the charts, at the page's width");
  // the scores: every method the file scores, the operator's lower error drawn as any other
  check(page.includes('data-fc-line-scores="a"') && fig(page, TEX, "series/demand/net_demand/last_2_years/nmae_pct/erw", 15.77, "15.77") && fig(page, TEX, "series/demand/net_demand/with_operator/nmae_pct/operator", 5.46, "5.46"), "net demand's scores, the operator's where it is scored");
  check(fig(page, WS, "places/1/fuels/wind/summary/with_operator/nmae_pct/operator", 13.24, "13.24") && fig(page, WS, "places/1/fuels/wind/summary/last_2_years/nmae_pct/profile7", 42.76, "42.76") && fig(page, WS, "places/1/fuels/wind/summary/backtest/hours", 64587, "64,587"), "wind's scores and hours, from the wind and solar file");
  check(!page.includes("places/1/fuels/solar/summary/with_operator") && /not scored/.test(t), "a line the operator's forecast is not held for has no row of it, and its cell says not scored");
  const mae = draw(FIX, { m: "mae" });
  check(fig(mae, TEX, "series/demand/net_demand/last_2_years/mae_mw/erw", 5539.7, "5,540") && fig(mae, WS, "places/1/fuels/solar/summary/backtest/mae_mw/yesterday", 6015.3, "6,015"), "the score in MW when the page's score is the error in MW, written whole");
  check(page.includes('data-fc-net-fold="a"') && fig(page, WS, "places/1/fuels/wind/tomorrow/5/5", windAt(5) + 120) && t.includes("Wind, operator") && fig(page, TEX, "series/demand/net_demand/tomorrow/5/2", netAt(5)), "hour by hour: demand, wind with the operator's forecast, solar, net demand");
}

// ---- 4. How it has done: wind and solar on a past day --------------------------------------------------------------------
{
  check(page.includes('data-fc-wsday="a" data-fc-wsday-of="2026-11-25"') && /aria-label="ERW forecast of wind and solar output for Texas on Wednesday 25 Nov 2026, beside what happened/.test(page), "wind and solar on the newest past day held, beside what happened");
  check(page.includes("Wind, actual") && page.includes("Solar, actual") && page.includes("What happened is drawn dashed"), "what happened is a line of its own for each, and the hover says which");
  const d24 = draw(FIX, { day: "2026-11-24" });
  check(d24.includes('data-fc-wsday-of="2026-11-24"'), "the day asked for, where the wind and solar file holds it");
  const odd = draw(FIX, { day: "2026-01-01" });
  check(odd.includes('data-fc-wsday-of="2026-11-25"') && odd.includes("2026-01-01 is not among them"), "a day the file does not hold: the newest day held, and the hover says so");
  quiet(odd, "a day not held");
}

// ---- 5. The operator's filing ---------------------------------------------------------------------------------------------
{
  check(page.includes('data-fc-filing="a" data-fc-filing-months="3" data-fc-filing-flagged="1"'), "the block of the filing check");
  check(/In <span data-check="pf\|predict\/region-tex\.json\|series\/demand\/operator_filing\/months_flagged" data-raw="1"[^>]*>1<\/span> of 3 months the forecast filed on Form EIA-930 is more than 5 percent from the demand it forecasts over the whole month\. In those months the filed forecast is not the operator&#x27;s own forecast\./.test(page), "where months are flagged the page says the filed forecast is not the operator's own in those months");
  check(fig(page, TEX, "series/demand/operator_filing/sound_last_2_years/mape/erw", 1.76, "1.76") && fig(page, TEX, "series/demand/operator_filing/sound_last_2_years/mape/operator", 1.98, "1.98") && fig(page, TEX, "series/demand/operator_filing/sound_last_2_years/hours", 16800, "16,800"), "the months that pass: every method's score, the ERW's lower one drawn as any other");
  check(/Every month<\/th>[\s\S]{0,400}data-check="pf\|predict\/scores\.json\|rows\/\d+\/\d+"/.test(page), "beside them, the last two years on every month, from the score file");
  check(page.includes('data-fc-filing-fold="a"') && t.includes("The filing month by month: 3 months, 1 flagged") && fig(page, TEX, "series/demand/operator_filing/months/1/2", 93.8, "93.80") && count(page, /data-fc-filing-month="flagged"/g) === 1 && count(page, /data-fc-filing-month="passes"/g) === 2, "every month behind a fold, the flagged one marked");
  check(t.includes("its hours fit best moved by 1") && page.includes("3.61%, 2.09%, 1.75%"), "a filing whose hours fit best moved: said beside the heading, the three errors on hover");
  // every month flagged: no hour passes, and the row says so in place of a nought and four blanks
  const all = load(TEX);
  all.series.demand.operator_filing = { ...dem.operator_filing, months: dem.operator_filing.months.map((m) => [m[0], m[1], 76.2, true]), months_flagged: 3,
    sound_last_2_years: { first_day: null, last_day: null, hours: 0, mae: { erw: null, operator: null, yesterday: null, week_ago: null }, mape: { erw: null, operator: null, yesterday: null, week_ago: null } } };
  save(TEX, all);
  const flaggedAll = draw(FIX, {});
  check(/data-fc-filing-none-pass="a"[^>]*>no month of the last two years passes the check</.test(flaggedAll) && flaggedAll.includes('data-fc-filing-flagged="3"') && !flaggedAll.includes("operator_filing/sound_last_2_years/hours"), "every month flagged: the row of the months that pass says none does");
  quiet(flaggedAll, "every month flagged");
  // no month flagged: the sentence and the two rows are not drawn, the fold is
  const none = load(TEX);
  none.series.demand.operator_filing = { ...dem.operator_filing, months: dem.operator_filing.months.map((m) => [m[0], m[1], 100.2, false]), months_flagged: 0, best_shift_hours: 0 };
  save(TEX, none);
  const clean = draw(FIX, {});
  check(clean.includes('data-fc-filing-flagged="0"') && !clean.includes("data-fc-filing-says") && text(clean).includes("3 months, none flagged") && !text(clean).includes("fit best moved"), "no month flagged: no sentence, the months in their fold");
  save(TEX, tex);
}

// ---- 6. The separate line with the weather forecast -----------------------------------------------------------------------
{
  check(page.includes('data-fc-wwf="a" data-fc-wwf-days="17" data-fc-wwf-few="1"') && t.includes("with the weather forecast (a separate line, not the ERW forecast), KDFW: 17 of the 30 days needed, too few days to judge"), "the line's heading: separate, not the ERW forecast, too few days to judge");
  check(fig(page, TEX, "series/demand/with_weather_forecast/all/mape/with_weather_forecast", 3.809, "3.81") && fig(page, TEX, "series/demand/with_weather_forecast/all/mape/operator", 1.181, "1.18") && fig(page, TEX, "series/demand/with_weather_forecast/all/hours", 409, "409"), "its scores beside the methods on the same hours");
  check(t.includes("With the airport's weather known") && !/regression_recent|with_weather_forecast|with_airport_weather_known|nmae_pct|mae_mw/.test(t), "the same line on the airport's observed weather is named plainly; a file's own id is never printed on the page's face");
  check(page.includes('data-fc-wwf-fold="a"') && fig(page, TEX, "series/demand/with_weather_forecast/tomorrow/17/2", demandAt(17) + 250.5), "its hours for the day forecast now, behind a fold");
  // never in a chart, never called the ERW forecast's line
  const charts = [...page.matchAll(/<svg[^>]*>/g)].map((m) => /aria-label="([^"]*)"/.exec(m[0])?.[1]).filter((a) => a && /ERW forecast/.test(a));
  check(charts.length >= 5 && charts.every((a) => !/weather forecast/i.test(a)) && !page.includes("ERW forecast: with the weather"), "the separate line is in no chart of the ERW forecast");
  const scored = load(TEX);
  scored.series.demand.with_weather_forecast = { ...dem.with_weather_forecast, days: 41, status: "scored" };
  save(TEX, scored);
  const s2 = draw(FIX, {});
  check(s2.includes('data-fc-wwf-few="0"') && text(s2).includes("41 of the 30 days needed,") && !text(s2).includes("too few days to judge"), "with the days the file asks for, the heading no longer says too few");
  save(TEX, tex);
}

// ---- 7. The band ----------------------------------------------------------------------------------------------------------
{
  check(page.includes('data-fc-band="a" data-fc-band-rows="3"') && t.includes("the band, and how often what happened fell inside it (a band made to hold 80 percent of hours)"), "the band's record: demand, wind and solar");
  check(fig(page, TEX, "series/demand/band_coverage/inside_pct", 80.3, "80.30") && fig(page, TEX, "series/demand/band_coverage/below_pct", 9.4, "9.40") && fig(page, TEX, "series/demand/band_coverage/above_pct", 10.3, "10.30") && fig(page, TEX, "series/demand/band_coverage/hours", 17400, "17,400"), "the shares inside, below and above, and the hours");
  check(fig(page, WS, "places/1/fuels/wind/band_coverage/inside_pct", 79.8, "79.80") && fig(page, WS, "places/1/fuels/solar/band_coverage/inside_pct", 75.7, "75.70"), "the wind and solar bands, from their file");
  check(/aria-label="Texas: the share of past hours on which what happened fell inside the band of the ERW forecast, by the hour of the place's clock, in percent"/.test(page.replace(/&#x27;/g, "'")), "the share inside by the hour of the day, as a chart");
  check(page.includes('data-fc-band-fold="a|0"') && fig(page, TEX, "series/demand/band_coverage/by_month/2/2", 68.5, "68.50") && fig(page, TEX, "series/demand/band_coverage/by_month/2/1", 601, "601"), "month by month behind a fold, a month below the band's own share drawn as any other");
  const price = draw(FIX, { s: "price" });
  quiet(price, "price");
  check(price.includes('data-fc-band="a" data-fc-band-rows="1"') && fig(price, TEX, "series/price/band_coverage/inside_pct", 77.9, "77.90") && !price.includes("fuels/wind"), "price: its own band, and no line of wind or solar");
  check(!price.includes('data-fc-net="a" data-fc-net-hours="24"') && !price.includes("data-fc-filing=") && !price.includes("data-fc-wwf="), "price draws none of demand's views");
}

// ---- 8. What a file does not hold -----------------------------------------------------------------------------------------
{
  // no forecast of net demand for the day: a blank with the file's reason, and the scores still
  const empty = load(TEX);
  empty.series.demand.net_demand = { ...dem.net_demand, tomorrow: [] };
  save(TEX, empty);
  const wsHeld = JSON.parse(JSON.stringify(ws));
  for (const f of Object.values(wsHeld.places[1].fuels)) { f.tomorrow = []; f.tomorrow_held = "no forecast yet: the output of two days before is not held when the forecast is made"; }
  save(WS, wsHeld);
  const html = draw(FIX, {});
  check(html.includes('data-fc-net="a" data-fc-net-hours="0"') && /data-fc-blank="net\|a"[^>]*>ERW forecast of net demand, Texas, Friday 27 Nov 2026: no forecast yet</.test(html) && html.includes("no forecast yet: the output of two days before is not held"), "no net demand for the day: a blank whose face is the reason's first words and whose hover is the file's reason");
  // session 10411: net demand's own reason (the contract's `tomorrow_held` of session 10603) comes before the fuels'
  const own = load(TEX);
  own.series.demand.net_demand = { ...dem.net_demand, tomorrow: [], tomorrow_held: "the wind forecast is not held: no forecast: the method chosen reads every hour of the days 18 to 20 November" };
  save(TEX, own);
  const ownHtml = draw(FIX, {});
  check(/title="the wind forecast is not held: no forecast: the method chosen reads every hour of the days 18 to 20 November"[^>]*data-fc-blank="net\|a"[^>]*>ERW forecast of net demand, Texas, Friday 27 Nov 2026: not held</.test(ownHtml) && !ownHtml.includes("no forecast yet: the output of two days before"), "net demand's own reason for the day is the hover, before the wind and solar forecast's");
  // and a fuel whose day is not forecast carries `tomorrow: null`, not rows of nulls: the same blank
  for (const f of Object.values(wsHeld.places[1].fuels)) f.tomorrow = null;
  save(WS, wsHeld);
  check(draw(FIX, {}).includes('data-fc-net="a" data-fc-net-hours="0"'), "a fuel with no rows at all for the day (tomorrow: null) is a day not forecast");
  save(TEX, empty);
  for (const f of Object.values(wsHeld.places[1].fuels)) f.tomorrow = [];
  save(WS, wsHeld);
  check(html.includes('data-fc-line-scores="a"') && fig(html, TEX, "series/demand/net_demand/last_2_years/nmae_pct/erw", 15.77), "and its scores are drawn still");
  quiet(html, "no net demand for the day");
  // no wind and solar file: net demand alone
  fs.rmSync(path.join(FIX, WS));
  save(TEX, tex);
  const alone = draw(FIX, {});
  check(alone.includes('data-fc-net="a" data-fc-net-hours="24"') && !alone.includes("wind_solar.json|") && alone.includes('data-fc-wsday="a" data-fc-wsday-of="none"') && alone.includes('data-fc-band-rows="1"'), "no wind and solar file: net demand is drawn alone, and no figure of the file");
  check(text(alone).includes("Highest wind hour") && /The wind and solar file \(site\/data\/predict\/wind_solar\.json\) holds no wind line for this place/.test(alone), "the wind and solar figures are blanks that say why");
  quiet(alone, "no wind and solar file");
  // an example wind and solar file shows nothing
  save(WS, { ...ws, example: true });
  check(!draw(FIX, {}).includes("wind_solar.json|"), "an example wind and solar file: nothing of it is shown");
  save(WS, ws);
}

// ---- 8b. The place a wind and solar entry is shown for (session 10411; the contract's `shown_for`) ------------------------
{
  check(L.windSolarFor(ws, "region-tex")?.pi === 1 && L.windSolarFor(ws, "ba-erco") === null && L.windSolarFor(ws, "ba-erco", "region-tex")?.pi === 1, "a file with no shown_for: the entry of the place's own id, or the one its net demand names");
  const listed = JSON.parse(JSON.stringify(ws));
  listed.places[0].shown_for = ["region-cal"];
  listed.places[1].shown_for = ["region-tex", "ba-erco"];
  check(L.windSolarFor(listed, "ba-erco")?.pi === 1 && L.windSolarFor(listed, "region-tex")?.pi === 1 && L.windSolarFor(listed, "region-mida") === null && L.windSolarFor(listed, "region-mida", "region-tex") === null, "a file with shown_for: the entry that names the place, and no other");
  check(L.windSolarFor({ ...listed, example: true }, "ba-erco") === null && L.windSolarFor(null, "ba-erco") === null, "an example file, or none: no entry");
  // a place with no net demand of its own (the fixture's ERCOT authority) is shown the entry that names it
  save(WS, listed);
  const erco = draw(FIX, { a: "ba-erco" });
  const words = text(erco);
  quiet(erco, "a place shown another's entry");
  check(erco.includes('data-fc-net="a" data-fc-net-hours="24" data-fc-net-of="region-tex"') && /ERCO\): wind and solar/.test(words) && !/ERCO\): wind, solar and net demand/.test(words), "a place with no net demand of its own: wind and solar, drawn from the entry that names it");
  check(!words.includes("Lowest net demand") && words.includes("Highest wind hour") && fig(erco, WS, "places/1/fuels/wind/tomorrow/0/2", 6000.5, "6,001") && !erco.includes("net_demand/"), "its figures are the wind's and the solar's; nothing of a net demand it does not hold");
  check(/aria-label="ERW forecast of demand and of wind and solar output for Electric Reliability Council of Texas, Inc\. \(ERCO\)/.test(erco) && erco.includes("the file&#x27;s entry region-tex, Texas, which it names for this place"), "the chart says what it draws, and the hover which entry of the file it is");
  check(erco.includes('data-fc-line-scores="a"') && fig(erco, WS, "places/1/fuels/wind/summary/last_2_years/nmae_pct/erw", 40.46, "40.46") && erco.includes('data-fc-wsday="a" data-fc-wsday-of="2026-11-25"') && erco.includes('data-fc-band-rows="2"') && fig(erco, WS, "places/1/fuels/solar/band_coverage/inside_pct", 75.7, "75.70"), "and its scores, its past day and the wind and solar bands (the fixture's authority has no band record of its own demand)");
  check(erco.includes('data-fc-download="net"') && erco.includes('href="/forecast/net?place=ba-erco"'), "the download is offered for it");
  const got = (await import("../app/forecast/net/route.ts")).GET(new Request("https://example.test/forecast/net?place=ba-erco"));
  const body = await got.text();
  check(got.status === 200 && /^# net_demand: no line\. The place's file holds no net demand$/m.test(body) && body.split("\n").filter((l) => l.startsWith("ba-erco,wind,tomorrow,")).length === 24, "its CSV: the wind and solar rows, and the header says it holds no net demand");
  check(draw(FIX, { a: "region-mida" }).includes('data-fc-net="a" data-fc-net-hours="none"'), "a place no entry names and with no net demand draws nothing of it");
  save(WS, ws);
}

// ---- 9. Two places, and the hover of a forecast kept as first made --------------------------------------------------------
{
  const two = draw(FIX, { b: "region-mida" });
  check(two.includes('data-fc-net="a" data-fc-net-hours="24"') && two.includes('data-fc-net="b" data-fc-net-hours="none"') && two.includes('data-fc-band="b" data-fc-band-rows="0"'), "two places: each view once a place, a place with none of it empty");
  quiet(two, "two places");
  check(page.includes("Kept as first made: the ledger: the forecast first made for this day, kept as made") && page.includes("the method chosen now is regression with the recent days."), "a forecast the ledger already held: the place's hover says it is kept as first made, the method in the page's words");
  check(!before.includes("Kept as first made"), "a forecast made fresh says nothing of the ledger");
}

// ---- 10. The real-time price (rt_price.json) -------------------------------------------------------------------------------
{
  const RT = "rt_price.json";
  const noFile = draw(FIX, { s: "price" });
  check(!noFile.includes('id="realtime"') && !noFile.includes("data-fc-rt="), "no real-time file: the page has no section of it");
  const price = tex.series.price;
  const PTS = price.tomorrow.map((r) => r[0]);
  const PH = price.history.slice(0, 48).map((r) => [r[0], r[1], r[2]]);
  const rtAt = (hr) => 22.5 + 2 * hr;                 // lowest at 00:00: 22.50; highest at 23:00: 68.50
  const daAt = (hr) => rtAt(hr) + 1.25;
  const sum = (hours, mae, mape) => ({ hours, mae: { erw: mae[0], day_ahead: mae[1], yesterday: mae[2], regression: mae[3] }, mape: { erw: mape[0], day_ahead: mape[1], yesterday: mape[2], regression: mape[3] } });
  const hubOf = (tomorrow, held) => ({ hub: "ercot:HB_NORTH", grid: "ercot", time: "America/Chicago", status: "shown", method: "regression", method_mae_last_2_years: { yesterday: 19.72, regression: 12.33 },
    made_utc: "2026-11-26T22:00:00Z", inputs_through_utc: "2026-11-26T05:00:00Z", target_day: "2026-11-27", horizon_days: 2, band: "the 10th and 90th percentile of the chosen method's own past errors at the same local hour over 365 days",
    band_coverage_pct: 77.5, band_coverage: band(77.5, 9.9, 12.6, 17422), tomorrow_columns: ["ts_utc", "local_hour", "erw", "lo", "hi", "day_ahead"], tomorrow, tomorrow_held: held,
    // over the last two years the day-ahead price is the closer of the two, over the backtest too: drawn as any other
    summary: { last_2_years: { ...span2, ...sum(17422, [12.33, 11.83, 19.72, 12.33], [33.883, 30.845, 60.868, 33.883]) }, backtest: { ...spanAll, ...sum(64818, [37.94, 23.67, 40.94, 37.94], [63.819, 40.667, 94.845, 63.819]) } },
    history_columns: ["ts_utc", "local_day", "local_hour", "erw", "lo", "hi", "day_ahead", "actual", "yesterday"], history: PH.map(([ts, day, hr]) => [ts, day, hr, rtAt(hr), rtAt(hr) - 8, rtAt(hr) + 8, daAt(hr), rtAt(hr) + 3, rtAt(hr) - 2]) });
  const row = (m, cut, key, hours, mae, mape) => ["hub-ercot", "rt_price", m, cut, key, hours, mae, mape, null];
  const rtFile = (hub) => ({ fixture: FIXTURE, contract: "docs/state/page_files_predict.md", built: "2026-11-27T03:29:56Z", tier: "derived", label: "ERW forecast", method_note: "docs/methods/predict_price.md, section 7",
    made_rule: "made at 22:00 UTC the day before the target local day, after the day-ahead markets publish", units: "USD/MWh",
    methods: [{ id: "erw", words: "the ERW method the rule chose for the hub" }, { id: "day_ahead", words: "the hub's day-ahead price for the hour: the market's own forecast of the real-time price; the comparator, never an ERW method" }, { id: "yesterday", words: "the real-time price of the same local hour two days before" }, { id: "regression", words: "least squares by local hour on the day-ahead price" }],
    // the hub is the second of the file, so a figure's key must name its position there
    hubs: [{ hub: "spp:SPPNORTH_HUB", grid: "spp", time: "America/Chicago", status: "shown", method: "regression", tomorrow_columns: [], tomorrow: [], tomorrow_held: "no forecast yet", summary: {}, history_columns: [], history: [] }, hub],
    rows_columns: ["place", "series", "method", "cut", "key", "hours", "mae", "mape", "held"],
    rows: [["hub-spp", "rt_price", "erw", "all", "", 100, 1.5, 2.5, null], row("erw", "spike", "", 649, 1969.9, 92.504), row("day_ahead", "spike", "", 649, 988.97, 77.717),
      row("erw", "month", "2026-11", 505, 9.5, 31.2), row("day_ahead", "month", "2026-11", 505, 8.25, 27.4), row("erw", "month", "2026-10", 744, 7.1, 22.5), row("day_ahead", "month", "2026-10", 744, 7.6, 24.1),
      row("erw", "hour", "17", 730, 21.4, 40.1), row("day_ahead", "hour", "17", 730, 18.2, 35.6), row("erw", "hour", "3", 730, 5.2, null)] });
  const rt = rtFile(hubOf(PTS.map((ts, hr) => [ts, hr, rtAt(hr), rtAt(hr) - 8, rtAt(hr) + 8, daAt(hr)]), null));
  save(RT, rt);
  check(L.rtHubOf(rt, "ercot:HB_NORTH")?.hi === 1 && L.rtHubOf(rt, "pjm:WEST") === null && L.rtHubOf({ ...rt, example: true }, "ercot:HB_NORTH") === null && L.rtHubOf(rt, null) === null, "rtHubOf: a hub by its id with its position; an example file shows nothing");
  const html = draw(FIX, { s: "price" });
  const words = text(html);
  quiet(html, "the real-time price");
  check(html.includes('id="realtime"') && html.includes('data-fc-rt="a" data-fc-rt-hub="ercot:HB_NORTH" data-fc-rt-hours="24"') && words.includes("Texas: the real-time price at ercot:HB_NORTH"), "price: a section of the real-time price at the hub the place's day-ahead forecast is of");
  check(fig(html, RT, "hubs/1/tomorrow/23/2", 68.5, "68.50") && fig(html, RT, "hubs/1/tomorrow/23/5", 69.75, "69.75") && fig(html, RT, "hubs/1/tomorrow/0/2", 22.5, "22.50") && words.includes("Day-ahead price, same hour"), "its highest hour, the day-ahead price for the same hour and its lowest hour, each with its key by the hub's position");
  check(/aria-label="ERW forecast of the real-time price at ercot:HB_NORTH for Friday 27 Nov 2026, with the hub&#x27;s day-ahead price/.test(html) && html.includes("never an ERW method"), "the chart says what it draws; the day-ahead price is named the comparator, never an ERW method");
  check(html.includes('data-fc-rt-day="a" data-fc-rt-day-of="2026-11-25"') && /aria-label="ERW forecast of the real-time price at ercot:HB_NORTH on Wednesday 25 Nov 2026, beside the hub&#x27;s day-ahead price and what happened/.test(html), "a past day beside the day-ahead price and what happened");
  check(draw(FIX, { s: "price", day: "2026-11-24" }).includes('data-fc-rt-day-of="2026-11-24"') && draw(FIX, { s: "price", day: "2026-01-01" }).includes('data-fc-rt-day-of="2026-11-25"'), "the day asked for where the file holds it, else the newest day held");
  check(fig(html, RT, "hubs/1/summary/last_2_years/mae/erw", 12.33, "12.33") && fig(html, RT, "hubs/1/summary/last_2_years/mae/day_ahead", 11.83, "11.83") && fig(html, RT, "hubs/1/summary/backtest/hours", 64818, "64,818"), "the report card: the day-ahead price's lower error drawn as any other");
  check(fig(html, RT, "rows/1/6", 1969.9, "1,969.90") && fig(html, RT, "rows/2/6", 988.97, "988.97") && words.includes("Price spikes"), "the price spikes, from the file's rows, each with its row's key");
  check(html.includes('data-fc-rt-cut="a|month"') && fig(html, RT, "rows/5/6", 7.1, "7.10") && fig(html, RT, "rows/4/6", 8.25, "8.25") && /Oct 2026[\s\S]*Nov 2026/.test(html.slice(html.indexOf('data-fc-rt-cut="a|month"'))), "by month, the calendar's order, a month the ERW forecast lost drawn as one it won");
  check(html.includes('data-fc-rt-cut="a|hour"') && /03:00[\s\S]*17:00/.test(html.slice(html.indexOf('data-fc-rt-cut="a|hour"'))) && fig(html, RT, "rows/7/6", 21.4, "21.40"), "by hour of day, the clock's order");
  const pct = draw(FIX, { s: "price", m: "mape" });
  check(fig(pct, RT, "hubs/1/summary/last_2_years/mape/day_ahead", 30.845, "30.85") && /a percent error is not defined where the price is near zero/.test(pct), "the percent error when the page's score is that; a row with none says why");
  check(html.includes('data-fc-band="a" data-fc-band-rows="2"') && fig(html, RT, "hubs/1/band_coverage/inside_pct", 77.5, "77.50") && words.includes("ERW forecast of the real-time price"), "the band's record has a row of the real-time price");
  // no forecast for the day: a blank with the file's reason; the past day and the report card are drawn still
  save(RT, rtFile(hubOf([], "no forecast yet: the day-ahead price for the target day is not held when the forecast is made")));
  const held = draw(FIX, { s: "price" });
  check(held.includes('data-fc-rt-hours="0"') && /data-fc-blank="rt\|a"[^>]*>ERW forecast of the real-time price, ercot:HB_NORTH, Friday 27 Nov 2026: no forecast yet</.test(held) && held.includes("the day-ahead price for the target day is not held when the forecast is made"), "no forecast for the day: a blank that says so, with the file's reason");
  check(held.includes('data-fc-rt-day-of="2026-11-25"') && fig(held, RT, "hubs/1/summary/last_2_years/mae/erw", 12.33), "and the past day and the report card are drawn still");
  quiet(held, "no real-time forecast for the day");
  save(RT, rt);
  // demand draws none of it; a place whose price is held has no real-time section
  const dem2 = draw(FIX, {});
  check(!dem2.includes('id="realtime"') && !dem2.includes("rt_price.json|"), "demand draws nothing of the real-time price");
  const mida = draw(FIX, { a: "region-mida", s: "price" });
  check(!mida.includes('id="realtime"') && !mida.includes("rt_price.json|") && mida.includes("license needed"), "a place whose price is held: no real-time section, and no figure of it");
  const pair = draw(FIX, { a: "region-mida", b: "region-tex", s: "price" });
  check(pair.includes('data-fc-rt="a" data-fc-rt-hub="none"') && pair.includes('data-fc-rt="b" data-fc-rt-hub="ercot:HB_NORTH"'), "two places, one with a hub: the section draws the one");
  quiet(pair, "two places, price");
  save(RT, { ...rt, example: true });
  check(!draw(FIX, { s: "price" }).includes("rt_price.json|"), "an example real-time file: nothing of it is shown");
  save(RT, rt);
}

// ---- 11. Downloads of the new lines (session 10410) ------------------------------------------------------------------------
{
  const { csvReader } = await import("../lib/csvreader.ts");
  const { NET_READER } = await import("../app/forecast/net/reader.ts");
  const { RT_READER } = await import("../app/forecast/realtime-price/reader.ts");
  const data = (csv) => csv.split("\n").filter((l) => l && !l.startsWith("#"));
  const texNow = load(TEX), wsNow = load(WS), rtNow = load("rt_price.json");
  const ncsv = L.netCsv({ place: "region-tex", name: "Texas" }, texNow.series.demand, wsNow, "https://example.test/forecast/net?place=region-tex");
  const nrows = data(ncsv);
  check(nrows[0] === L.NET_HEAD.join(",") && nrows.length === 1 + 24 + 2 * (24 + 48), "the net demand CSV: its head, 24 hours of net demand, and for wind and for solar the day forecast now and two past days");
  check(nrows.includes(`region-tex,net_demand,tomorrow,${TS[0]},2026-11-27,0,${netAt(0)},,,,,`) && nrows.includes(`region-tex,wind,tomorrow,${TS[5]},2026-11-27,5,${windAt(5)},${windAt(5) - 400},${windAt(5) + 400},${windAt(5) + 120},,`), "a row of net demand has no band; a row of wind has its band and the operator's forecast");
  check(nrows.some((l) => l.startsWith("region-tex,solar,history,") && l.endsWith(`,${solarAt(12)},${solarAt(12) - 400},${solarAt(12) + 400},,${solarAt(12) + 150},${solarAt(12) - 90}`)), "a past hour of solar: the forecast, its band, no operator's forecast, what happened and the same hour of the day read");
  check(/^# ERW forecast: a model's output \(tier derived\), never a published or official figure/m.test(ncsv) && /^# From: https:\/\/example\.test\/forecast\/net\?place=region-tex$/m.test(ncsv) && /^# wind: .*method regression/m.test(ncsv), "the provenance first: what it is, each line's method, the address");
  const none = L.netCsv({ place: "region-tex", name: "Texas" }, texNow.series.demand, null, "u");
  check(data(none).length === 1 + 24 && /^# wind: no line\. The wind and solar file holds no such line for this place$/m.test(none), "no wind and solar file: net demand's rows, and the header says why the others have none");
  const rcsv = L.rtCsv(rtNow.hubs[1], rtNow, "https://example.test/forecast/realtime-price?hub=ercot%3AHB_NORTH");
  const rrows = data(rcsv);
  check(rrows[0] === L.RT_HEAD.join(",") && rrows.length === 1 + 24 + 48 && rrows.includes(`ercot:HB_NORTH,tomorrow,${texNow.series.price.tomorrow[23][0]},2026-11-27,23,68.5,60.5,76.5,69.75,,`), "the real-time price CSV: the day forecast now and two past days, beside the day-ahead price");
  check(/day_ahead_price is the hub's day-ahead price, the market's own forecast of the real-time price: the comparator, never an ERW method/.test(rcsv), "the header names the day-ahead price as the comparator");
  const heldHub = { ...rtNow.hubs[1], tomorrow: [], tomorrow_held: "no forecast yet: the day-ahead price for the target day is not held when the forecast is made" };
  const hcsv = L.rtCsv(heldHub, rtNow, "u");
  check(data(hcsv).length === 1 + 48 && /^# tomorrow: no row\. no forecast yet: the day-ahead price for the target day is not held/m.test(hcsv), "a day with no forecast: no row of it, and the header says why");
  for (const [name, spec, cols] of [["net", NET_READER, L.NET_HEAD], ["real-time", RT_READER, L.RT_HEAD]]) {
    check([...spec.text, ...spec.figures].every((c) => cols.includes(c)) && spec.show.every((c) => cols.includes(c)) && cols.includes(spec.count), `${name}: the reader names only columns the CSV has`);
    check([...spec.text, ...spec.figures].length === cols.length, `${name}: every column is read as text or as a figure`);
    const py = csvReader("py", "https://example.test/x", spec), doFile = csvReader("do", "https://example.test/x", spec);
    check(py.includes('URL = "https://example.test/x"') && doFile.includes("https://example.test/x") && !py.includes(dash) && !doFile.includes(dash), `${name}: the Python and the Stata reader carry the address`);
  }
  // the routes themselves, asked as a reader's browser asks them
  process.env.ERW_PREDICT_DIR = FIX;
  const route = async (file, address) => { const res = (await import(file)).GET(new Request(address)); return { status: res.status, type: res.headers.get("Content-Type") ?? "", robots: res.headers.get("X-Robots-Tag"), name: res.headers.get("Content-Disposition") ?? "", text: await res.text() }; };
  const n1 = await route("../app/forecast/net/route.ts", "https://example.test/forecast/net?place=region-tex");
  check(n1.status === 200 && n1.type.startsWith("text/csv") && n1.robots === "noindex" && n1.name.includes("erw_forecast_net_demand_region-tex.csv") && data(n1.text).length === nrows.length, "/forecast/net: a place's CSV, named, not indexed");
  check((await route("../app/forecast/net/route.ts", "https://example.test/forecast/net?place=region-zz")).status === 404 && (await route("../app/forecast/net/route.ts", "https://example.test/forecast/net?place=region-mida")).status === 404 && (await route("../app/forecast/net/route.ts", "https://example.test/forecast/net")).status === 404, "/forecast/net: a place the index does not list, one with no net demand, or none: 404");
  const n2 = await route("../app/forecast/net/python/route.ts", "https://example.test/forecast/net/python?place=region-tex&x=%3Cscript%3E");
  check(n2.status === 200 && n2.text.includes('URL = "https://example.test/forecast/net?place=region-tex"') && !n2.text.includes("script") && n2.name.includes("region-tex.py"), "the Python reader's address is built again from the listed place: nothing else of the request is passed on");
  const n3 = await route("../app/forecast/net/stata/route.ts", "https://example.test/forecast/net/stata?place=region-tex");
  check(n3.status === 200 && n3.text.includes("https://example.test/forecast/net?place=region-tex") && n3.name.includes("region-tex.do") && (await route("../app/forecast/net/stata/route.ts", "https://example.test/forecast/net/stata?place=nowhere")).status === 404, "the Stata reader, and 404 for a place not listed");
  const r1 = await route("../app/forecast/realtime-price/route.ts", "https://example.test/forecast/realtime-price?hub=ercot%3AHB_NORTH");
  check(r1.status === 200 && r1.type.startsWith("text/csv") && r1.robots === "noindex" && r1.name.includes("erw_forecast_real_time_price_ercot.csv") && data(r1.text).length === rrows.length && /^# From: https:\/\/example\.test\/forecast\/realtime-price\?hub=ercot%3AHB_NORTH$/m.test(r1.text), "/forecast/realtime-price: a hub's CSV, its address written from the listed hub");
  check((await route("../app/forecast/realtime-price/route.ts", "https://example.test/forecast/realtime-price?hub=pjm%3AWEST")).status === 404 && (await route("../app/forecast/realtime-price/route.ts", "https://example.test/forecast/realtime-price")).status === 404, "/forecast/realtime-price: a hub the file does not list, or none: 404");
  const r2 = await route("../app/forecast/realtime-price/python/route.ts", "https://example.test/forecast/realtime-price/python?hub=ercot%3AHB_NORTH&y=1");
  const r3 = await route("../app/forecast/realtime-price/stata/route.ts", "https://example.test/forecast/realtime-price/stata?hub=ercot%3AHB_NORTH");
  check(r2.status === 200 && r2.text.includes('URL = "https://example.test/forecast/realtime-price?hub=ercot%3AHB_NORTH"') && !r2.text.includes("y=1") && r3.status === 200 && r3.text.includes("hub=ercot%3AHB_NORTH") && r3.name.includes("ercot.do"), "its two readers carry the hub's address and nothing else of the request");
  // the page offers them where the place holds the lines
  const d = draw(FIX, {});
  check(d.includes('data-fc-download="net"') && d.includes('href="/forecast/net?place=region-tex"') && d.includes('href="/forecast/net/python?place=region-tex"') && d.includes('href="/forecast/net/stata?place=region-tex"'), "demand: the download of net demand, wind and solar, with its readers");
  const p = draw(FIX, { s: "price" });
  check(p.includes('data-fc-download="realtime"') && p.includes('href="/forecast/realtime-price?hub=ercot%3AHB_NORTH"') && p.includes('href="/forecast/realtime-price/stata?hub=ercot%3AHB_NORTH"') && !p.includes('data-fc-download="net"'), "price: the download of the real-time price at the place's hub, with its readers");
  check(!draw(FIX, { a: "region-mida" }).includes('data-fc-download="net"') && !draw(FIX, { a: "region-mida", s: "price" }).includes('data-fc-download="realtime"'), "a place that holds neither is offered neither");
  check(count(draw(FIX, { a: "region-tex", b: "ba-erco", s: "price" }), /data-fc-download="realtime"/g) <= 1, "two places of one hub: its download is offered once");

  // ---- 12. Wind and solar by month and by hour of day, behind folds ----------------------------------------------------
  check(!d.includes("data-fc-ws-cut="), "a wind and solar file with no row by month or hour: no fold of them");
  const wsCuts = JSON.parse(JSON.stringify(wsNow));
  const wrow = (fuel, m, cut, key, hours, mae, pct) => ["region-tex", fuel, m, cut, key, hours, mae, pct, null];
  // rows 1 to 7 of the file: in October the same hour of the day read was the closer of the two, on purpose
  wsCuts.rows = [...wsCuts.rows, wrow("wind", "erw", "month", "2026-11", 601, 5210.4, 48.2), wrow("wind", "yesterday", "month", "2026-11", 601, 6105.5, 56.5), wrow("wind", "erw", "month", "2026-10", 744, 4800.6, 39.9), wrow("wind", "yesterday", "month", "2026-10", 744, 4700.2, 39.1),
    wrow("solar", "erw", "hour", "12", 730, 2100.5, 18.4), wrow("solar", "profile7", "hour", "12", 730, 2050.5, 17.9), wrow("solar", "erw", "hour", "3", 730, 0.4, null)];
  save(WS, wsCuts);
  const cut = draw(FIX, {});
  quiet(cut, "wind and solar by month and hour");
  check(cut.includes('data-fc-ws-cuts="a"') && cut.includes('data-fc-ws-cut="a|wind|month"') && cut.includes('data-fc-ws-cut="a|solar|hour"') && !cut.includes('data-fc-ws-cut="a|wind|hour"') && !cut.includes('data-fc-ws-cut="a|solar|month"'), "a fold for each fuel and cut the file holds rows of, and none for one it does not");
  check(fig(cut, WS, "rows/3/7", 39.9, "39.90") && fig(cut, WS, "rows/4/7", 39.1, "39.10") && fig(cut, WS, "rows/1/7", 48.2, "48.20") && /Oct 2026[\s\S]*Nov 2026/.test(cut.slice(cut.indexOf('data-fc-ws-cut="a|wind|month"'), cut.indexOf('data-fc-ws-cut="a|solar|hour"'))), "wind by month: the calendar's order, a month the plain rule was closer drawn as any other, each figure with its row's key");
  check(text(cut).includes("Texas: ERW forecast of wind, month by month, % of the mean (2 months)") && text(cut).includes("Texas: ERW forecast of solar, by hour of day, % of the mean (2 hours)"), "each fold says the place, the fuel, the cut, the score and the count");
  const solar = cut.slice(cut.indexOf('data-fc-ws-cut="a|solar|hour"'));
  check(/03:00[\s\S]*12:00/.test(solar) && fig(cut, WS, "rows/6/7", 17.9, "17.90") && /the error over the mean output is not defined where the mean is nought/.test(solar) && !/Operator/.test(solar.slice(0, solar.indexOf("</details>"))), "solar by hour: the clock's order; a row with no percent says why; a method with no row in the cut has no column");
  const cutMae = draw(FIX, { m: "mae" });
  check(fig(cutMae, WS, "rows/1/6", 5210.4, "5,210") && fig(cutMae, WS, "rows/7/6", 0.4, "0") && text(cutMae).includes("Texas: ERW forecast of wind, month by month, MW (2 months)"), "the error in MW when the page's score is that, written whole");
  check(!draw(FIX, { s: "price" }).includes("data-fc-ws-cut="), "price draws none of them");
  save(WS, wsNow);
}

// ---- 13. More hubs, the backtest by year, the files' own words for their cuts (session 10411) -------------------------------
{
  const P = await import("../lib/predict.ts");
  const RT = "rt_price.json", HUBS = "price_hubs.json";
  const rtNow = load(RT);                       // its hubs: one of SPP, then Texas's own, ercot:HB_NORTH
  const price = tex.series.price;
  const noHubs = draw(FIX, { s: "price" });
  check(!noHubs.includes('id="hubs"') && !noHubs.includes("data-fc-hubs="), "no other hub of the grid in either file: no section of more hubs");
  // one more hub of Texas's grid in the real-time file, with the backtest by year
  const hou = JSON.parse(JSON.stringify(rtNow.hubs[1]));
  hou.hub = "ercot:HB_HOUSTON"; hou.grid = "ercot-houston";
  const yr = (year, mae, mape) => ({ year, first_day: `${year}-01-01`, last_day: `${year}-12-31`, hours: 8760, mae: { erw: mae[0], day_ahead: mae[1], yesterday: mae[2], regression: mae[0] }, mape: { erw: mape[0], day_ahead: mape[1], yesterday: mape[2], regression: mape[0] } });
  hou.long_backtest = { what: "the same walk-forward backtest from 1 January 2016, as far back as the hub's prices allow", first_target: "2016-01-01", method: "regression", band_coverage_pct: 77.6,
    all: { first_day: "2016-01-01", last_day: "2026-11-25", hours: 95461, mae: { erw: 29.85, day_ahead: 19.94, yesterday: 32.51, regression: 29.85 }, mape: { erw: 51.4, day_ahead: 35.0, yesterday: 76.1, regression: 51.4 } },
    // in 2017 the ERW forecast was the closer of the two, in 2016 the day-ahead price: both drawn the same
    by_year: [yr(2016, [8.33, 7.88, 10.71], [24.4, 20.3, 30.8]), yr(2017, [10.92, 11.02, 15.29], [26.1, 27.5, 33.3])] };
  const rt2 = { ...rtNow, cuts: { top10: "the ten days of the backtest with the highest real-time price hour", spike: "the hours whose real-time price is above the hub's own 99th percentile over the backtest", month: "key YYYY-MM" }, hubs: [...rtNow.hubs, hou],
    rows: [...rtNow.rows, ["hub-ercot-houston", "rt_price", "erw", "top10", "", 240, 3958.65, 700.1, null], ["hub-ercot-houston", "rt_price", "day_ahead", "top10", "", 240, 1390.2, 900.5, null]] };
  // the day-ahead hubs file: the same hub, a place file's series.price block with its place, grid and time first
  const sum = (hours, mae, mape) => ({ first_day: "2020-03-05", last_day: "2026-11-26", hours, mae: { erw: mae[0], yesterday: mae[1], week_ago: mae[2], operator: null }, mape: { erw: mape[0], yesterday: mape[1], week_ago: mape[2], operator: null } });
  const block = { place: "hub-ercot-houston", grid: "ercot-houston", demand_place: "ba-erco", time: "America/Chicago", ...price, hub: "ercot:HB_HOUSTON", method: "yesterday",
    tomorrow: price.tomorrow.map((r) => [r[0], r[1], r[2] + 3, r[3] + 3, r[4] + 3, null]), summary: { last_30_days: sum(601, [11.11, 11.11, 13.55], [35.3, 35.3, 40.8]), backtest: sum(58809, [23.51, 23.51, 54.8], [31.8, 31.8, 125.6]) } };
  const hrow = (m, cut, key, hours, mae, mape) => ["hub-ercot-houston", "price", m, cut, key, hours, mae, mape, null];
  const hubsFile = { fixture: FIXTURE, contract: "docs/state/page_files_predict.md", built: "2026-11-27T08:40:00Z", tier: "derived", label: "ERW forecast", what: "the ERW forecast of the day-ahead price at more hubs of the three public grids",
    method_note: "docs/methods/predict_price.md", made_rule: "made at 18:00 UTC the day before the target day", methods: [{ id: "erw", what: "the ERW method the rule chose for the hub" }, { id: "yesterday", what: "the hub's day-ahead price at the same local hour of the day before" }],
    hubs: [block], rows_columns: ["place", "series", "method", "cut", "key", "hours", "mae", "mape", "held"],
    rows: [hrow("erw", "top10", "", 240, 1469.87, 300.5), hrow("week_ago", "top10", "", 240, 4114.53, 900.2), hrow("erw", "event", "uri-2021", 432, 1080.92, 250.1), hrow("erw", "month", "2026-11", 601, 11.11, 35.3), hrow("erw", "month", "2026-10", 744, 9.5, 30.1), hrow("week_ago", "month", "2026-10", 744, 8.9, 28.4)],
    cuts: { top10: "the ten days with the highest price hour" } };
  save(RT, rt2);
  save(HUBS, hubsFile);

  // the library
  check(L.gridOfHub("ercot:HB_HOUSTON") === "ercot" && L.gridOfHub(null) === "" && L.moreHubs("ercot:HB_NORTH", hubsFile, rt2).join(" ") === "ercot:HB_HOUSTON", "moreHubs: the other hubs of the grid of a place's own hub, each once, the own hub and another grid's left out");
  check(L.moreHubs("ercot:HB_NORTH", null, null).length === 0 && L.moreHubs(null, hubsFile, rt2).length === 0 && L.moreHubs("ercot:HB_NORTH", { ...hubsFile, example: true }, null).length === 0, "no file, no own hub or an example file: no hub");
  check(L.priceHubOf(hubsFile, "ercot:HB_HOUSTON")?.hi === 0 && L.priceHubOf(hubsFile, "ercot:HB_NORTH") === null && L.rtHubOf(rt2, "ercot:HB_HOUSTON")?.hi === 2, "a hub's entry in each file, with its position");
  // the address
  const idx = load("index.json");
  const q = P.queryOf({ s: "price", hub: "ercot:HB_HOUSTON" }, idx);
  check(q.hub === "ercot:HB_HOUSTON" && P.hrefOf(q) === "/forecast?s=price&hub=ercot%3AHB_HOUSTON" && P.hrefOf(q, { hub: null }) === "/forecast?s=price", "a hub is in the address with price");
  check(P.queryOf({ hub: "ercot:HB_HOUSTON" }, idx).hub === null && P.queryOf({ s: "price", hub: "<script>" }, idx).hub === null && P.queryOf({ s: "price", hub: ["a:b", "c:d"] }, idx).hub === null && P.hrefOf({ ...q, s: "demand" }) === "/forecast", "with demand, in no hub's form, or given twice: no hub");

  // the list, with no hub drawn
  const list = draw(FIX, { s: "price" });
  const lw = text(list);
  quiet(list, "more hubs, the list");
  check(list.includes('id="hubs"') && list.includes('data-fc-hubs="1" data-fc-hub-drawn="none"') && lw.includes("Texas: the other hubs of ERCOT, USD/MWh") && !list.includes("data-fc-dah="), "price: a section of the other hubs of the place's grid, one row a hub, none drawn until chosen");
  check(fig(list, HUBS, "hubs/0/tomorrow/18/2", 68, "68.00") && fig(list, HUBS, "hubs/0/tomorrow/0/2", 23, "23.00") && lw.includes("at 18:00"), "a hub's row: the highest and the lowest hour of its day-ahead forecast, each with its key into the hubs file");
  check(fig(list, HUBS, "hubs/0/summary/backtest/mae/erw", 23.51, "23.51") && fig(list, RT, "hubs/2/summary/last_2_years/mae/erw", 12.33, "12.33") && fig(list, RT, "hubs/2/summary/last_2_years/mae/day_ahead", 11.83, "11.83"), "and each market's error: the day-ahead forecast's over its backtest, the real-time forecast's and the day-ahead price's over two years");
  check(list.includes('href="/forecast?s=price&amp;hub=ercot%3AHB_HOUSTON#hubs"'), "the hub's name draws it");
  check(list.includes('data-fc-rt="a" data-fc-rt-hub="ercot:HB_NORTH"') && !list.includes('data-fc-rt="hub"'), "the place's own hub keeps its real-time block; no other hub's is drawn");

  // one hub drawn whole
  const html = draw(FIX, { s: "price", hub: "ercot:HB_HOUSTON" });
  const w = text(html);
  quiet(html, "a hub drawn");
  // session 10414 (read in the accessibility tree of a build): a price block's title was a fourth-level heading right
  // under the section's second-level one, in "Real-time price" and in "More hubs". No level is skipped now
  for (const [name, page] of [["price, a hub drawn", html], ["price", list], ["demand", draw(FIX, {})]]) {
    const levels = [...page.matchAll(/<h([1-6])[\s>]/g)].map((m) => Number(m[1]));
    check(levels.length > 3 && levels.every((l, i) => i === 0 || l <= levels[i - 1] + 1), `${name}: a heading level is skipped (${levels.join("")})`);
  }
  check(html.includes('data-fc-hub-drawn="ercot:HB_HOUSTON"') && html.includes('data-fc-dah="hub" data-fc-dah-hub="ercot:HB_HOUSTON" data-fc-dah-hours="24"') && w.includes("ercot:HB_HOUSTON: the day-ahead price"), "the hub chosen: its day-ahead price drawn whole");
  check(fig(html, HUBS, "hubs/0/tomorrow/18/2", 68, "68.00") && /data-n="fc\|hub\|dah\|top"/.test(html) && /aria-label="ERW forecast of the day-ahead price at ercot:HB_HOUSTON for Friday 27 Nov 2026, by the hour/.test(html), "its day forecast now, with keys into the hubs file, and a chart that says what it draws");
  const dah = html.slice(html.indexOf('data-fc-dah="hub"'), html.indexOf('data-fc-rt="hub"'));
  check(dah.length > 1000 && !text(dah).includes("Day-ahead price, same hour") && !dah.includes("with the hub&#x27;s day-ahead price") && text(html.slice(html.indexOf('data-fc-rt="hub"'))).includes("Day-ahead price, same hour"), "the day-ahead block has no line of another market beside it; the real-time block has the day-ahead price");
  check(fig(html, HUBS, "hubs/0/summary/last_30_days/mae/week_ago", 13.55, "13.55") && fig(html, HUBS, "hubs/0/summary/backtest/hours", 58809, "58,809") && html.includes('data-fc-dah-summary="hub"'), "its report card: the last 30 days and the backtest, every method the same");
  check(fig(html, HUBS, "rows/0/6", 1469.87, "1,469.87") && fig(html, HUBS, "rows/1/6", 4114.53, "4,114.53") && w.includes("The ten days with the highest price hour") && html.includes("The file&#x27;s words on this cut: the ten days with the highest price hour."), "a cut is named for a price, and the file's own words of it are its hover");
  check(html.includes('href="/events/uri-2021"') && fig(html, HUBS, "rows/2/6", 1080.92, "1,080.92"), "an event's row opens the event's page");
  check(html.includes('data-fc-dah-cut="hub|month"') && /Oct 2026[\s\S]*Nov 2026/.test(html.slice(html.indexOf('data-fc-dah-cut="hub|month"'))) && fig(html, HUBS, "rows/5/6", 8.9, "8.90"), "by month, the calendar's order, a month a plain rule was closer drawn as any other");
  check(html.includes('data-fc-rt="hub" data-fc-rt-hub="ercot:HB_HOUSTON"') && w.includes("ercot:HB_HOUSTON: the real-time price") && html.includes('data-fc-rt="a" data-fc-rt-hub="ercot:HB_NORTH"'), "then its real-time price; the place's own hub keeps its block");
  check(html.includes('data-fc-rt-years="hub"') && fig(html, RT, "hubs/2/long_backtest/all/hours", 95461, "95,461") && fig(html, RT, "hubs/2/long_backtest/by_year/0/mae/day_ahead", 7.88, "7.88") && fig(html, RT, "hubs/2/long_backtest/by_year/1/mae/erw", 10.92, "10.92") && fig(html, RT, "hubs/2/long_backtest/band_coverage_pct", 77.6, "77.60"), "the backtest from 2016: the whole span, each year, and the share inside the band, each with its key");
  const years = html.slice(html.indexOf('data-fc-rt-years="hub"'));
  check(/>2016<[\s\S]*>2017</.test(years) && w.includes("The real-time price year by year, the backtest from 2016-01-01") && html.includes("The file&#x27;s words: the same walk-forward backtest from 1 January 2016"), "the years in order, under words that say what the table is, the file's own on hover");
  check(!html.includes('data-fc-rt-years="a"'), "a hub whose entry holds no backtest by year draws no table of it");
  check(fig(html, RT, "rows/" + (rtNow.rows.length) + "/6", 3958.65, "3,958.65") && html.includes("The file&#x27;s words on this cut: the ten days of the backtest with the highest real-time price hour."), "the real-time cuts carry the real-time file's own words");
  check(html.includes('data-fc-hub-download="ercot:HB_HOUSTON"') && html.includes('href="/forecast/realtime-price?hub=ercot%3AHB_HOUSTON"') && html.includes(">Close ercot:HB_HOUSTON<") && html.includes('href="/forecast?s=price#hubs"'), "the hub's download, and a way to close it");
  check(/<input type="hidden" name="hub" value="ercot:HB_HOUSTON"/.test(html), "the hub stays drawn through another choice of the form");
  // seen at 390 px in a build: the links under a hub drawn were 18 px tall, under the 24 a finger needs
  const under = html.slice(html.indexOf('data-fc-hub="ercot:HB_HOUSTON"'));
  check(count(under, /<a [^>]*download=""[^>]*class="inline-block py-1"|<a [^>]*class="inline-block py-1"[^>]*download=""/g) === 6 && /class="[^"]*inline-block py-1[^"]*"[^>]*>Close ercot:HB_HOUSTON</.test(under), "the links under a hub drawn are tall enough for a finger");
  // the hub's day-ahead forecast as a download, the route asked as a browser asks it
  check(html.includes('data-fc-hub-download-dah="ercot:HB_HOUSTON"') && html.includes('href="/forecast/hub-price?hub=ercot%3AHB_HOUSTON"') && html.includes('href="/forecast/hub-price/stata?hub=ercot%3AHB_HOUSTON"'), "the hub's day-ahead forecast is offered as a CSV with its readers");
  {
    process.env.ERW_PREDICT_DIR = FIX;
    const ask = async (file, address) => { const res = (await import(file)).GET(new Request(address)); return { status: res.status, type: res.headers.get("Content-Type") ?? "", name: res.headers.get("Content-Disposition") ?? "", robots: res.headers.get("X-Robots-Tag"), text: await res.text() }; };
    const h1 = await ask("../app/forecast/hub-price/route.ts", "https://example.test/forecast/hub-price?hub=ercot%3AHB_HOUSTON");
    const rowsOf = h1.text.split("\n").filter((l) => l && !l.startsWith("#"));
    check(h1.status === 200 && h1.type.startsWith("text/csv") && h1.robots === "noindex" && h1.name.includes("erw_forecast_day_ahead_price_ercot-houston.csv") && rowsOf[0] === L.HUB_HEAD.join(",") && rowsOf.length === 1 + 24 + price.history.length, "/forecast/hub-price: the hub's CSV, the day forecast now and every past hour held");
    check(rowsOf.includes(`ercot:HB_HOUSTON,tomorrow,${price.tomorrow[18][0]},2026-11-27,18,${price.made_utc},live,68,62,74,,,`) && /^# From: https:\/\/example\.test\/forecast\/hub-price\?hub=ercot%3AHB_HOUSTON$/m.test(h1.text) && /No operator publishes a forecast of its day-ahead price/.test(h1.text), "a row of the day forecast now with its band; the provenance first");
    check((await ask("../app/forecast/hub-price/route.ts", "https://example.test/forecast/hub-price?hub=ercot%3AHB_NORTH")).status === 404 && (await ask("../app/forecast/hub-price/route.ts", "https://example.test/forecast/hub-price")).status === 404, "a hub the hubs file does not list, or none: 404");
    const h2 = await ask("../app/forecast/hub-price/python/route.ts", "https://example.test/forecast/hub-price/python?hub=ercot%3AHB_HOUSTON&z=9");
    const h3 = await ask("../app/forecast/hub-price/stata/route.ts", "https://example.test/forecast/hub-price/stata?hub=ercot%3AHB_HOUSTON");
    check(h2.status === 200 && h2.text.includes('URL = "https://example.test/forecast/hub-price?hub=ercot%3AHB_HOUSTON"') && !h2.text.includes("z=9") && h3.status === 200 && h3.name.includes("ercot-houston.do"), "its two readers carry the hub's address and nothing else of the request");
    const { HUB_READER } = await import("../app/forecast/hub-price/reader.ts");
    check([...HUB_READER.text, ...HUB_READER.figures].every((c) => L.HUB_HEAD.includes(c)) && [...HUB_READER.text, ...HUB_READER.figures].length === L.HUB_HEAD.length && HUB_READER.show.every((c) => L.HUB_HEAD.includes(c)), "the reader names every column of the CSV and no other");
  }
  const pct = draw(FIX, { s: "price", hub: "ercot:HB_HOUSTON", m: "mape" });
  check(fig(pct, HUBS, "hubs/0/summary/backtest/mape/week_ago", 125.6, "125.60") && fig(pct, RT, "hubs/2/long_backtest/by_year/1/mape/day_ahead", 27.5, "27.50") && pct.includes("hub=ercot%3AHB_HOUSTON"), "the percent error when the page's score is that");
  // a hub the files do not list for the place, and a hub with demand
  for (const hub of ["spp:SPPNORTH_HUB", "ercot:HB_NORTH", "ercot:HB_NOWHERE"]) check(draw(FIX, { s: "price", hub }).includes('data-fc-hub-drawn="none"'), `the hub ${hub} is not one of the other hubs of the place's grid: none is drawn`);
  check(!draw(FIX, { hub: "ercot:HB_HOUSTON" }).includes('id="hubs"'), "demand draws no hub");
  check(!draw(FIX, { a: "region-mida", s: "price", hub: "ercot:HB_HOUSTON" }).includes('id="hubs"'), "a place whose price is held has no hub to offer");
  // two places of one grid share the list
  const pair = draw(FIX, { a: "region-tex", b: "ba-erco", s: "price" });
  check((pair.match(/data-fc-hubs-of=/g) ?? []).length <= 1 || !pair.includes('data-fc-hubs-of="b"'), "two places of one grid: the grid's hubs are listed once");
  // the place's own price rows: a price's ten days are named by the price, with the score file's cuts_price on hover
  const scores = load("scores.json");
  scores.rows.push(["region-tex", "price", "erw", "top10", "", 240, 55.5, 60.2, null], ["region-tex", "price", "yesterday", "top10", "", 240, 61.5, 70.2, null]);
  scores.cuts_price = { top10: "the ten days with the highest price hour (the price rows' own cut)" };
  save("scores.json", scores);
  const own = draw(FIX, { s: "price" });
  const card = own.slice(own.indexOf('data-fc-cut="other"'), own.indexOf('id="realtime"'));
  check(text(card).includes("The ten days with the highest price hour") && !text(card).includes("The ten highest-demand days") && card.includes("the ten days with the highest price hour (the price rows&#x27; own cut)") && !card.includes("ten highest-demand days of the backtest"), "the place's own price rows: the ten days are the price's, and the hover is the score file's words for its price rows");
  const demandCard = draw(FIX, {});
  check(text(demandCard).includes("The ten highest-demand days") && demandCard.includes("ten highest-demand days of the backtest"), "demand keeps its own words");
  delete scores.cuts_price;
  save("scores.json", scores);
  const older = draw(FIX, { s: "price" });
  check(!older.slice(older.indexOf('data-fc-cut="other"'), older.indexOf('id="realtime"')).includes("ten highest-demand days of the backtest"), "a score file with no words for its price rows: the demand's words are not quoted for a price");
  // an example hubs file shows nothing
  save(HUBS, { ...hubsFile, example: true });
  save(RT, rtNow);
  check(!draw(FIX, { s: "price", hub: "ercot:HB_HOUSTON" }).includes('id="hubs"'), "an example hubs file, and no other hub in the real-time file: no section");
  fs.rmSync(path.join(FIX, HUBS));
}

if (!KEEP) fs.rmSync(FIX, { recursive: true, force: true });
if (fails.length) { for (const f of fails) console.log(`FAIL ${f}`); console.log(`${fails.length} of ${n} checks failed`); process.exit(1); }
console.log(`ok: ${n} checks of the forecast's lines of 27 November (net demand, wind and solar, the operator's filing, the weather forecast line, the band, the real-time price)`);
