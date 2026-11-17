// Energy Research Warehouse (ERW) site, session 7543 (chain 304, part C): /demand read as a utility planner reads it,
// for five cases (docs/reviews/demand-read-2026-11-16.md). The page's own function draws each view to HTML from the
// site's committed copies (data/demand_growth.json, data/demand_weather.json, data/data_faults.json); the consumption
// view's two live-set reads are answered by a stand-in for fetch with made-up rows (two states, 25 months; no real
// row of any table is in this file). Each site row of the read is held here as fixed, by its number, and the page is
// held to /grid's Records and to the explorer on the figures and words they share. No server, no network, no click.
//   node --import ./scripts/battery-awards-page-register.mjs scripts/test-demand-read.mjs
import fs from "node:fs";
import { prerenderToNodeStream } from "react-dom/static";

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const file = (...p) => fs.readFileSync(new URL(["..", ...p].join("/"), import.meta.url), "utf-8");
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (html) => ent(html.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").replace(/ ([,.;:)])/g, "$1").replace(/\( /g, "(").replace(/ 's\b/g, "'s");
const titleOf = (html, attr) => ent((html.match(new RegExp(`title="([^"]*)"[^>]*${attr}`)) ?? html.match(new RegExp(`${attr}[^>]*title="([^"]*)"`)) ?? ["", ""])[1]);

// ---- the consumption view's reads: made-up rows, two states, the window of the live set (25 months to 2026-08)
const MONTHS = Array.from({ length: 25 }, (_, i) => new Date(Date.UTC(2024, 7 + i, 1)).toISOString().replace(/\.\d{3}Z$/, "Z"));
const fake = [];
for (const st of ["US", "TX", "NM"]) for (const sec of ["ALL", "RES", "COM", "IND", "TRA"]) MONTHS.forEach((ts, i) => {
  if (st === "NM" && sec === "RES" && ["2026-03", "2026-04", "2026-05", "2026-06"].includes(ts.slice(0, 7))) return;  // a gap, as the read found one
  fake.push({ entity: `eia:retail_sales:${st}:${sec}`, variable: "retail_sales", ts_utc: ts, value: 1_000_000.37 + 1000 * i, unit: "MWh", freq: "P1M" });
});
process.env.SUPABASE_URL = "http://localhost:9/";
process.env.SUPABASE_ANON_KEY = "stand-in";
globalThis.fetch = async (url) => {
  const q = new URL(String(url)).searchParams;
  const name = (q.get("table_name") ?? "").replace(/^eq\./, "");
  const limit = Number(q.get("limit") ?? 1000), offset = Number(q.get("offset") ?? 0);
  const rows = name === "eia_retail_sales_monthly" ? fake : name === "eia_sector_energy_consumption_monthly" ? [] : null;
  if (rows === null) return new Response("stand-in: not held", { status: 404 });
  return new Response(JSON.stringify(rows.slice(offset, offset + limit)), { status: 200, headers: { "content-type": "application/json" } });
};
const log = console.error;
console.error = () => {};
const { default: Demand } = await import("../app/demand/page.tsx");
const draw = async (query) => {
  const { prelude } = await prerenderToNodeStream(await Demand({ searchParams: Promise.resolve(query) }));
  let html = "";
  for await (const c of prelude) html += c;
  return html;
};
const views = {};
for (const [k, q] of Object.entries({ ercot: { area: "ercot" }, caiso: { area: "caiso" }, pjm: { area: "pjm" }, weather: { view: "weather" }, consumption: { view: "consumption" } })) views[k] = await draw(q);
console.error = log;

const D = JSON.parse(file("data", "demand_growth.json"));
const W = JSON.parse(file("data", "demand_weather.json"));
const F = JSON.parse(file("data", "data_faults.json"));
const g = await import("../lib/demandweather.ts");
const P = await import("../lib/demandpage.ts");
const { DEMAND_GROWTH_DECISIONS } = await import("../app/explore/demand-growth/Decisions.tsx");

ok(Object.values(views).every((h) => h.length > 5000 && !/\bundefined\b|NaN/.test(words(h))), "every view draws, with no undefined and no NaN");
ok(words(views.ercot).includes("From 2019 to 2025, ERCOT's average demand went from 43,798 MW to 55,717 MW, a change of +27.22 percent"), "case 1: ERCOT's summary, as it was");

// ---- row 1: the heat map's hover names the colour a fall is drawn in
const tokens = file("app", "tokens.css");
const down = (tokens.match(/--color-down:\s*(#[0-9A-Fa-f]{6})/) ?? ["", ""])[1];
const heatWhy = titleOf(views.ercot, "data-hint=\"1\">How to read the cells");
ok(down === "#2E2D29" && heatWhy.includes("Red is growth, dark grey a fall") && !heatWhy.includes("green"), `row 1: a fall is drawn in ${down}, and the hover says dark grey, not green`);

// ---- row 2: the weather view's "Metered, MW" set beside the as-metered view
let cellsOk = 0, cellsAll = 0;
for (const ba of g.ORDER) for (const y of g.years(W)) {
  const f = g.figureOf(W, ba, y, "energy");
  if (!f) continue;
  cellsAll++;
  const t = ent((views.weather.match(new RegExp(`title="([^"]*)" data-metered-why="${ba}\\|${y}"`)) ?? ["", ""])[1]);
  if (t && t === g.meteredWhy(W.grids[ba].name, y, "energy", f, D.areas[ba].years[y])) cellsOk++;
}
ok(cellsAll === 35 && cellsOk === cellsAll, `row 2: every energy cell of the weather table carries its hover (${cellsOk} of ${cellsAll})`);
const e25 = ent((views.weather.match(/title="([^"]*)" data-metered-why="ERCO\|2025"/) ?? ["", ""])[1]);
ok(e25 === "ERCOT, 2025: 55,666 MW, the mean of the 8,622 of 8,760 hours whose weather all five stations hold, the hours the fit is read on. The as-metered view's average of 2025 is 55,717 MW, over the 8,736 hours it uses (every hour that passes the screen, weather or not): 51 MW apart.",
  "row 2: ERCOT 2025, the two figures and why they differ");
ok(/data-metered-head="1"/.test(views.weather), "row 2: the column head says what the figure is read on");
let peaksSame = 0, peaksAll = 0;
for (const ba of g.ORDER) for (const y of g.years(W)) {
  const s = g.figureOf(W, ba, y, "summer_peak"), m = D.areas[ba].years[y];
  const at = D.areas[ba].at[y]?.peak_demand_mw ?? D.areas[ba].at[y]?.ytd_peak_demand_mw;
  if (!s || !at || !["06", "07", "08", "09"].includes(at.slice(5, 7))) continue;
  peaksAll++;
  if (Math.round(s.actual) === Math.round(m.peak_demand_mw ?? m.ytd_peak_demand_mw) && s.at === at) peaksSame++;
}
ok(peaksAll >= 30 && peaksSame === peaksAll, `row 2: where the year's peak fell in June to September, the two views give the same hour and MW (${peaksSame} of ${peaksAll})`);

// ---- rows 3 and 4: the summary sentence, for every figure and year
const sentence = (h) => words((h.match(/data-summary="1">([\s\S]*?)<\/p>/) ?? ["", ""])[1]);
ok(sentence(views.weather) === "In 2025, against the average of 2019 to 2021, the year's energy grew by more than the temperature explains in 5 of the 7 grids that hold the figure: ERCOT (+24.2 percent, give or take 4.0), SPP (+12.5 percent, give or take 1.5), PJM (+6.6 percent, give or take 2.5), CAISO (+4.6 percent, give or take 3.2) and MISO (+3.5 percent, give or take 2.6); in the other 2 the part the temperature does not explain is smaller than the fit's own error.",
  "rows 3 and 4: the default view's sentence is as it was");
const summer26 = sentence(await (async () => { console.error = () => {}; const h = await draw({ view: "weather", figure: "summer", year: "2026" }); console.error = log; return h; })());
ok(summer26.includes("grew by more than the temperature explains in 0 of the 7 grids that hold the figure, and by less than it explains in 1: NYISO (-7.8 percent, give or take 3.9)"), "row 3: a finding below zero is growth by less than the temperature explains (NYISO, summer 2026)");
ok(summer26.includes("in 5 the peak hour was hotter than any hour of 2019 to 2021, beyond the weather the fit saw, so the figure is not called a finding: ERCOT (+16.0 percent, give or take 6.2)") && summer26.includes("in 1 the part the temperature does not explain is smaller than the fit's own error"),
  "row 4: a peak beyond the fit's weather is not counted as inside the fit's error (ERCOT, summer 2026: +16.0, give or take 6.2)");
let combos = 0, right = 0;
for (const fig of g.FIGURES) for (const y of g.years(W)) {
  const { found, not } = g.split(W, y, fig.key);
  const p = g.summaryParts(found, not);
  combos++;
  if (p.up.every((x) => x.g.unexplained_pct >= 0) && p.down.every((x) => x.g.unexplained_pct < 0) && p.within.every((x) => !x.g.outside && Math.abs(x.g.unexplained_pct) <= x.g.uncertainty_pct)
    && p.up.length + p.down.length === found.length && p.within.length + p.beyond.length === not.length) right++;
}
ok(combos === 20 && right === combos, `rows 3 and 4: in all ${combos} figures and years the four parts are what the sentence calls them`);

// ---- row 5: an hour is named by its start, as the explorer says
const local = DEMAND_GROWTH_DECISIONS.find((d) => d.key === "local-time");
ok(titleOf(views.ercot, 'data-hour-why="when"') === P.HOUR_WHY && heatWhy.endsWith(P.HOUR_WHY) && local.def.includes("An hour is named by its start.") && P.HOUR_WHY.includes("An hour is named by its start: 17:00 is the hour from 17:00 to 18:00"),
  "row 5: the peak's hour column and the heat map say an hour is named by its start, as the explorer's line does");

// ---- row 6: demand against retail sales, the explorer's own words, on the first and the third views
const against = DEMAND_GROWTH_DECISIONS.find((d) => d.key === "against-sales");
const againstWhy = `${against.text} ${against.def} Source: ${against.source}`;
const tipIn = (h) => ent((h.match(/data-against-sales="1">[\s\S]*?title="([^"]*)"/) ?? ["", ""])[1]);
ok(tipIn(views.ercot) === againstWhy && tipIn(views.consumption) === againstWhy && againstWhy.includes("California -2.96, CAISO +4.45"), "row 6: the as-metered and consumption views carry the explorer's line on retail sales, word for word");
ok(views.ercot.includes('href="/demand?view=consumption"') && /data-against-sales="1">[\s\S]*?href="\/demand"/.test(views.consumption), "row 6: each links the other view");

// ---- row 7: California's 2019 base, from the register's entry
const fault = F.rows.find((r) => r.id === P.CA_BASE_FAULT);
const caWhy = ent((views.caiso.match(/data-ca-base="1">[\s\S]*?title="([^"]*)"/) ?? ["", ""])[1]);
ok(fault && caWhy === P.caBaseWhy(fault, F.status_words) && caWhy.includes("March 2019's mean is 19,536.4 MW in the table") && views.caiso.includes(`href="/data/faults#${P.CA_BASE_FAULT}"`), "row 7: the CAISO view says its base year is low in its early months, with the register's figures and a link to the entry");
ok(!views.ercot.includes("data-ca-base") && !views.pjm.includes("data-ca-base"), "row 7: only California's view carries it");

// ---- two pages, one figure (no row: they agree): /grid's Records give each year's peak hour as this page does
let same = 0, all = 0;
for (const [ba, slug] of Object.entries({ ERCO: "ercot", CISO: "caiso", PJM: "pjm", MISO: "miso", SWPP: "spp", NYIS: "nyiso", ISNE: "isone" })) {
  const plus = JSON.parse(file("data", "mixplus", `${slug}.json`));
  for (const y of Object.keys(plus.records).filter((x) => x !== "all")) {
    const r = plus.records[y].find((x) => x.key === "demand_hour_max");
    if (!r) continue;
    all++;
    const row = D.areas[ba].years[y] ?? {}, at = D.areas[ba].at[y] ?? {};
    if (Math.round(row.peak_demand_mw ?? row.ytd_peak_demand_mw) === Math.round(r.value) && (at.peak_demand_mw ?? at.ytd_peak_demand_mw) === r.at) same++;
  }
}
ok(all === 56 && same === all, `two pages: /grid's "Peak hour of demand" and this page's peak agree in ${same} of ${all} grid-years, MW and hour`);

// ---- rows 8 to 10: the consumption view
const cons = views.consumption;
ok(words(cons).includes("MWh") && !/\d,\d{3}\.\d{2}( MWh| \|)/.test(words(cons).replace(/TBtu[\s\S]*$/, "")) && /data-check="series_esum\|eia_retail_sales_monthly/.test(cons) === /data-check/.test(cons),
  "row 8: sales are whole MWh (no hundredths of a MWh on the face)");
ok(!/text-muted[^>]*>[^<]*Sums of 12 months/.test(cons) && /title="[^"]*Sums of 12 months, so seasons cancel out[^"]*"/.test(cons) && /title="[^"]*Transportation is electric rail and transit[^"]*"/.test(cons), "row 9: the two grey paragraphs are hovers now, their words whole");
const nm = ent((cons.match(/title="([^"]*)" data-no-data="NM\|RES"/) ?? ["", ""])[1]);
ok(nm === "eia:retail_sales:NM:RES: no row for 2026-03, 2026-04, 2026-05, 2026-06 in eia_retail_sales_monthly as the site holds it, so no 12-month total is given.", "row 10: a 'no data' cell names the months it lacks");

// ---- row 11: an empty answer for the energy review's table is said, not thrown (the stand-in answers it with no rows)
ok(/Industrial and commercial energy, all fuels \(US\)[\s\S]*the table returned no rows/.test(words(cons)) && words(cons).includes("Sector shares and growth, by state"), "row 11: the energy review's empty read is said in its section, and the rest of the view draws");

// ---- nothing held: every table this read quotes is public (lib/license.ts)
const L = await import("../lib/license.ts");
ok(["eia930_demand_growth", "eia930_demand_weather", "generation_mix_records", "known_data_faults", "eia_retail_sales_monthly", "eia_sector_energy_consumption_monthly", "subregion_demand_growth"]
  .every((t) => !L.licenseNeeded(t) && ["eia930:ISNE", "eia930:NYIS", "eia930:MISO", "iso:isone"].every((e) => !L.licenseHeldRow(t, e))), "no table this read quotes is held, whole or by grid");
const review = fs.readFileSync(new URL("../../docs/reviews/demand-read-2026-11-16.md", import.meta.url), "utf-8");
ok(!review.includes(String.fromCharCode(0x2014)), "the review has no em dash");

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
