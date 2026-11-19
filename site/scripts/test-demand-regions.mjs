// Energy Research Warehouse (ERW) site, session 8420 (chain 503, part C): "The whole country", the fourth view of
// /demand, held without a build. The view is drawn to HTML with the site's own code from fixtures in the form of the
// data machine's contract (scripts/regions-fixture-demand.mjs: values made by a rule, not data), and the whole page is
// drawn with no file (as the site stands until the data machine's files land) and with the fixtures in a folder of
// their own (ERW_REGIONS_DIR). Where the real files are on the site, their form is read too. No table, no server, no
// network, no click.
//   node --import ./scripts/battery-awards-page-register.mjs scripts/test-demand-regions.mjs
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { ADDRESSES, drawDemand, figuresOf, withoutAdded, wordsOf } from "./demand-pages.mjs";
import { ALIKE, BAS, CODES, NAMES, WHY, avgOf, demandFixture, indexFixture, numberOf, writeFixtureFolder } from "./regions-fixture-demand.mjs";

const C = await import("../lib/countrydemand.ts");
const F = await import("../lib/countryfiles.ts");
const G = await import("../lib/demandgrowth.ts");
const W = await import("../lib/demandweather.ts");
const P = await import("../lib/demandpage.ts");
const T = await import("../lib/tabs.ts");
const V = await import("../components/demand/Country.tsx");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const near = (a, b) => Math.abs(a - b) < 1e-9;
const here = (p) => new URL(p, import.meta.url);
const dash = [String.fromCharCode(0x2014), String.fromCharCode(0x2013)];
const figs = (html) => Object.fromEntries([...html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)].map((m) => [m[1], m[2]]));
const count = (html, s) => html.split(s).length - 1;
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&");

// ---- the fixture as files in memory: every region, and the fixture's balancing authorities that file demand
const index = indexFixture();
const files = {};
for (const code of CODES) files[code.toLowerCase()] = demandFixture(code);
for (const code of Object.keys(BAS)) if (!BAS[code].generation_only) files[`ba-${code.toLowerCase()}`] = demandFixture(code, { level: "ba" });
const fileOf = (p) => files[C.placeKey(p)] ?? null;
const draw = (q = {}, props = {}) => renderToStaticMarkup(createElement(V.Country, { q, index, fileOf, ...props }));

// ---- the library: the place an address names
const reg = (code) => ({ level: "region", code }), ba = (code) => ({ level: "ba", code });
ok(JSON.stringify(C.placeOf("ten", index)) === JSON.stringify(reg("TEN")) && JSON.stringify(C.placeOf("TEX", null)) === JSON.stringify(reg("TEX")), "a region from the address, by its code");
ok(JSON.stringify(C.placeOf("ba-tva", index)) === JSON.stringify(ba("TVA")) && JSON.stringify(C.placeOf("tva", index)) === JSON.stringify(ba("TVA")) && JSON.stringify(C.placeOf("tva", null)) === JSON.stringify(ba("TVA")), "a balancing authority from the address, as ba-tva or by its bare code");
ok(C.placeOf("mars", index) === null && C.placeOf("ba-ten", index) === null && C.placeOf(undefined, index) === null && C.placeOf("", null) === null, "with the index held, a code EIA does not list is no place");
ok(C.placeOf("../etc", null) === null && C.placeOf("a/b", null) === null && C.placeOf("ten.json", null) === null && C.placeOf("a b", null) === null && C.placeOf("x".repeat(9), null) === null, "a value that is not letters and digits is no place (it would be a file name)");
ok(C.placeFilePath(reg("TEN")) === "demand/ten.json" && C.placeFilePath(ba("TVA")) === "demand/ba/tva.json" && C.placeKey(reg("TEN")) === "ten" && C.placeKey(ba("TVA")) === "ba-tva", "the files of the contract: demand/<region>.json and demand/ba/<code>.json");
ok(C.countryHref({ a: reg("TEN"), b: ba("TVA") }) === "/demand?view=country&a=ten&b=ba-tva" && C.countryHref({ a: reg("SE"), b: "none", days: "2025", figure: "summer", year: "2024" }, "weather") === "/demand?view=country&a=se&b=none&days=2025&figure=summer&year=2024#weather" && C.countryHref({ a: reg("SE"), days: "all" }) === "/demand?view=country&a=se",
  "the view's address carries its choices: the two places, the days drawn, the figure and the year");
ok(C.FIRST_A.code === "TEN" && C.FIRST_B.code === "CAR" && /This page's own choice \(session 8420\); no publisher's default stands behind it/.test(C.FIRST_WHY), "the places drawn first are Tennessee and the Carolinas, and the hover says whose choice that is");
ok(C.regionRows(null).length === 13 && C.regionRows(null).map((r) => r.code).join() === CODES.join() && C.regionRows(null).every((r) => r.name === NAMES[r.code]) && C.regionRows(index)[11].tz === "America/Chicago", "the thirteen regions in EIA's order, from the contract's names without an index and from the index with one");
ok(F.NEW_REGIONS.map((c) => F.REGION_NAME[c]).join(", ") === "Southeast, Florida, Carolinas, Tennessee, Northwest, Southwest" && CODES.filter((c) => C.isNewRegion(c)).length === 6, "the six regions new to the site, by name");
ok(C.placeName(reg("TEN"), null) === "Tennessee" && C.placeName(ba("TVA"), index) === "Tennessee Valley Authority" && C.placeName(ba("TVA"), null) === "TVA" && C.placeName(ba("TVA"), null, files["ba-tva"]) === "Tennessee Valley Authority", "a place's name: the file's, else the index's, else EIA's name of a region, else its code");

// ---- the library: the daily series, every expected value recomputed here from the fixture's rule
const ten = files.ten, iT = numberOf("TEN"), N = ten.daily.days.length;
const sum = C.dailySummary(ten.daily);
ok(iT === 12 && N === 17 && sum.days === N && sum.held === N - 1 && sum.first === "2024-12-25" && sum.last === "2025-01-10", "the days drawn: how many, how many hold a whole day's demand, the first and the last");
ok(sum.topDay.day === "2025-01-10" && near(sum.topDay.mwh, 24 * (1000 * iT + 10 * (N - 1))) && sum.lowDay.day === "2024-12-25" && near(sum.lowDay.mwh, 24 * 1000 * iT), "the days of most and of least demand among the held days");
ok(sum.topHour.day === "2025-01-10" && sum.topHour.mw === 1000 * iT + 10 * (N - 1) + 500 && sum.topHour.at === "2025-01-10T22:00:00Z", "the highest hour of the days drawn, and when it was");
let heldSum = 0;
for (let d = 0; d < N; d++) if (d !== 3) heldSum += 24 * (1000 * iT + 10 * d);
ok(near(sum.mwh, heldSum), "the demand of the held days, summed; the day that is not whole is left out, never filled");
const y24 = C.dailySummary(ten.daily, "2024"), y25 = C.dailySummary(ten.daily, "2025");
ok(y24.days === 7 && y24.held === 6 && y24.last === "2024-12-31" && y24.topHour.mw === 1000 * iT + 60 + 500 && y25.days === 10 && y25.held === 10 && y25.first === "2025-01-01" && C.dailySummary(ten.daily, "2019") === null, "the days of one year only, when a year is chosen");
ok(C.dailyYears(ten.daily).join() === "2024,2025" && C.dailyYears(undefined).length === 0 && C.dailySummary(undefined) === null && C.dailySummary({ days: [] }) === null, "the years the series holds a day of; no series, no summary");
const peak = C.dailyPoints(ten.daily, "peak"), avg = C.dailyPoints(ten.daily, "average");
ok(peak.length === N && peak[0][0] === Date.parse("2024-12-25T00:00:00Z") && peak[0][1] === 1000 * iT + 500 && peak[3][1] === null && avg[3][1] === null && near(avg[5][1], 1000 * iT + 50) && C.dailyPoints(ten.daily, "peak", "2025").length === 10,
  "a chart's points: the day's highest hour, and its average (its MWh over the hours used); a day not held is a break, never a filled point");
const nd = C.newestDays(ten.daily, 3);
ok(nd.length === 3 && nd[0].day === "2025-01-10" && nd[2].day === "2025-01-08" && near(nd[0].mwh, 24 * (1000 * iT + 160)) && nd[0].hours === 24 && C.newestDays(ten.daily, 99).find((r) => r.day === "2024-12-28").mwh === null && C.NEWEST_DAYS === 7, "the newest days, newest first, as the file holds them");

// ---- the library: a file's growth is read by the page's own functions
const area = C.areaOf(ten), period = C.periodOf(ten.growth);
const ys = G.wholeYears(area), ytd = G.yearToDate(period, area);
ok(area.name === "Tennessee" && area.tz === "America/Chicago" && ys.length === 7 && ys[0].year === "2019" && ys[6].row.avg_demand_mw === avgOf(iT, 2025) && ytd.year === "2026" && ytd.row.ytd_avg_demand_mw === avgOf(iT, 2026) + 50 && ytd.base.ytd_avg_demand_mw === avgOf(iT, 2019) + 50,
  "the growth object is the page's area object: lib/demandgrowth.ts reads its whole years and its year so far");
const cs = G.cells(period, area), ex = G.extremes(cs);
ok(cs.length === 287 && ex.most.month === 12 && ex.most.hour === 23 && near(ex.most.pct, 8.3) && ex.most.mw === 35 && ex.least.month === 1 && ex.least.hour === 0 && near(ex.least.pct, -5) && G.byMonth(period, area)[11].pct === 6 && near(G.byHour(period, area)[23].pct, 2.3),
  "the month and hour cells, their extremes, and the change by month and by hour, by the page's own functions (an absent cell stays absent)");
ok(C.areaOf({ ...ten, growth: undefined }) === null, "a file with no growth object gives no area");
ok(C.trainOf(ten.weather).join() === "2019,2020,2021" && C.trainOf({ ...ten.weather, train: [2020, 2019] }).join() === "2019,2020" && C.trainOf({ ...ten.weather, train: undefined }).join() === "2019,2020,2021" && C.trainOf(undefined).length === 0
  && C.trainOf({ ...ten.weather, train: undefined, holdout: {} }).length === 0, "the fit's years: the file's own line, else the years its holdout is keyed by");
ok(WHY.startsWith("a clause") && !WHY.endsWith(".") && C.sentence(WHY) === `A${WHY.slice(1)}.` && C.sentence("Done already.") === "Done already." && C.sentence("  ") === "" && C.sentence(undefined) === "", "the file's words on why two figures differ, set as a sentence: a capital and a full stop, no word changed");
const wfile = { train: [2019, 2020, 2021], grids: { ten: ten.weather, car: files.car.weather } };
ok(W.years(wfile, ["ten", "car"]).join() === "2022,2023,2024,2025,2026" && W.lastWholeYear(wfile, ["ten"]) === "2025" && W.lastWholeYear(wfile, ["ten", "car"]) === "2025" && W.figureOf(wfile, "ten", "2025", "energy").growth_pct === iT + 4 && W.ORDER.length === 7,
  "the weather object is the page's grid object: lib/demandweather.ts reads its years, its last whole year and its figures");
const al = C.alikeRows(files.tex.alike);
ok(al.length === 7 && al[0].year === "2019" && al[0].region === 13000 && al[0].grid === 12900 && near(al[0].pct, 0.78) && C.alikeRows(undefined).length === 0, "a region beside its grid: both averages and the file's difference, year by year");

// ---- the view drawn from the fixture: Tennessee and the Carolinas first
const html = draw();
const text = wordsOf(html);
const f = figs(html);
ok(html.includes('data-view-body="country"') && html.includes('data-cd-a="ten"') && html.includes('data-cd-b="car"') && html.includes('data-cd-days="all"'), "with nothing chosen the view draws Tennessee as place A and the Carolinas as place B, every day held");
ok(html.includes('data-cd-place="a" data-cd-code="ten" data-cd-state="drawn"') && html.includes('data-cd-place="b" data-cd-code="car" data-cd-state="drawn"') && /Place A<\/div><h2[^>]*><span title="Tennessee, EIA&#x27;s region TEN of Form EIA-930\./.test(html), "two places side by side, each named, with what it is on hover");
ok(f["cd|a|sum|avg0"] === "12,000" && f["cd|a|sum|avg1"] === "12,600" && f["cd|a|sum|avg_growth"] === "+5.00" && f["cd|a|sum|peak0"] === "24,000" && f["cd|a|sum|peak1"] === "25,200" && f["cd|a|sum|peak_growth"] === "+5.00" && f["cd|a|sum|ytd_growth"] === "+5.81"
  && f["cd|b|sum|avg0"] === "2,000" && f["cd|b|sum|avg_growth"] === "+30.00", "each place's summary, in the form of the as-metered view's first sentence: average, peak and the year so far");
ok(count(html, 'data-cd-new="') === 2 && html.includes('data-cd-new="TEN"') && html.includes('data-cd-new="CAR"') && text.includes("Tennessee is one of the six regions no page of the site drew before 19 November 2026 (Southeast, Florida, Carolinas, Tennessee, Northwest, Southwest)"),
  "a place that is one of the six new regions says so, and names the six on hover");
ok(CODES.every((c) => html.includes(`data-cd-region="${c}"`)) && count(html, 'data-cd-region-new="1"') === 6 && ["SE", "FLA", "CAR", "TEN", "NW", "SW"].every((c) => new RegExp(`data-cd-region="${c}" data-cd-region-new="1"`).test(html)),
  "the table of regions has the thirteen by name, the six new ones marked");
ok(CODES.every((c) => html.includes(`href="/demand?view=country&amp;a=${c.toLowerCase()}&amp;b=`)) && Object.keys(BAS).filter((b) => !BAS[b].generation_only).every((b) => html.includes(`href="/demand?view=country&amp;a=ba-${b.toLowerCase()}&amp;b=`)),
  "every region and every balancing authority that files demand can be chosen by its name");
ok(Object.keys(BAS).every((b) => html.includes(`data-cd-ba="${b}"`)) && !html.includes("a=ba-sepa") && html.includes("Southeastern Power Administration files no demand with EIA"), "a generation-only authority is listed, with why it has no demand, and is not a link");
const nOpt = 13 + Object.keys(BAS).length;
ok(html.includes('data-cd-form="1"') && html.includes('action="/demand"') && html.includes('<input type="hidden" name="view" value="country"/>') && html.includes('name="a"') && html.includes('name="b"') && html.includes('name="days"')
  && count(html, "<option ") === nOpt + (nOpt + 1) + 3, "the choice: two lists of every region and balancing authority (the second with None) and the days drawn, in a form that needs no script");
ok(/<option value="ten" selected="">Tennessee \(region\)<\/option>/.test(html) && /<option value="car" selected="">Carolinas \(region\)<\/option>/.test(html) && /<option value="ba-tva">TVA: Tennessee Valley Authority<\/option>/.test(html), "the lists show the places drawn, regions by name and authorities by code and name");

// ---- demand by day
ok(count(html, 'data-cd-daily="') === 2 && html.includes(`data-cd-daily="a" data-cd-points="${N}"`) && count(html, "Highest hour</text>") + count(html, ">Highest hour<") >= 2 && /Tennessee: the highest hour and the average of each day, MW, every day held/.test(html), "demand by day: a chart for each place, the day's highest hour and its average");
ok(f["cd|a|day|held"] === "16" && f["cd|a|day|days"] === "17" && f["cd|a|day|top_gwh"] === F.gwh(24 * (12000 + 160)) && f["cd|a|day|low_gwh"] === "288.0" && f["cd|a|day|top_mw"] === "12,660" && text.includes("10 January 2025, 16:00") && text.includes("10 January 2025, 17:00"),
  "the days drawn, for each place: the counts, the days of most and least demand, the highest hour in the place's own time");
ok(f["cd|a|new|2025-01-10|gwh"] === "291.8" && f["cd|b|new|2025-01-10|mw"] === "2,660" && count(html, "cd|a|new|") === 14 && text.includes("Default: 7 days, this page's own choice (session 8420)"), "the newest seven days, both places on one line a day, with the default said on hover");
const one24 = draw({ days: "2024" }), f24 = figs(one24);
ok(one24.includes('data-cd-days="2024"') && one24.includes('data-cd-daily="a" data-cd-points="7"') && f24["cd|a|day|held"] === "6" && f24["cd|a|day|days"] === "7" && f24["cd|a|day|top_mw"] === "12,560" && /<option value="2024" selected="">2024<\/option>/.test(one24) && f24["cd|a|y|2025|avg"] === "12,600",
  "the days of one year, when a year is chosen: the chart and its table follow, the years do not move");
ok(draw({ days: "1999" }).includes('data-cd-days="all"'), "a year the files do not hold falls back to every day held");

// ---- year by year, and where the growth is: the page's own charts
ok(f["cd|a|y|2025|avg"] === "12,600" && f["cd|a|y|2025|avg_growth"] === "+5.00" && f["cd|a|y|2025|yoy"] === "+0.80" && f["cd|a|y|2025|peak"] === "25,200" && f["cd|a|y|2025|peak_growth"] === "+5.00" && f["cd|a|y|2025|hours"] === "8,760"
  && f["cd|a|y|ytd|avg"] === "12,750" && f["cd|a|y|ytd|avg_growth"] === "+5.81" && f["cd|b|y|2020|avg_growth"] === "+5.00" && !("cd|a|y|2019|avg_growth" in f) && count(html, ">the base year<") === 6,
  "year by year, one row a place and year: average, growth since 2019 and on the year before, peak, hours; the base year says so");
ok(text.includes("15 August 2025, 16:00") && text.includes("15 August 2025, 17:00") && text.includes("2026, to October") && text.includes("Each place's own clock time, daylight saving included (Tennessee: America/Chicago; Carolinas: America/New_York)"), "each peak's hour in the place's own time, and the hover names the two zones");
ok(f["cd|a|screen|jumps"] === "24" && f["cd|a|screen|blank"] === "12" && f["cd|b|screen|jumps"] === "4", "the hours left out, for each place");
ok(count(html, 'data-chart="years"') === 2 && count(html, 'data-chart="heat" data-cells="287"') === 2 && count(html, 'data-chart="by month"') === 2 && count(html, 'data-chart="by hour"') === 2 && count(html, 'data-chart="explained"') === 1,
  "the page's own charts, one for each place: the years, the months and hours, by month, by hour; and one chart of the weather for both");
ok(count(html, 'data-hover="1"') === 9 && count(html, "data-tip=") > 600 && html.includes('data-tip="Tennessee, 2025: average 12,600 MW, highest hour 25,200 MW"') && html.includes('data-tip="December, 23:00: +8.30 percent, +35 MW"') && html.includes('data-tip="February, 03:00: not held"'),
  "each of them sits in the page's hover frame and its marks carry their words; a cell the file lacks reads not held");
ok(f["cd|a|cell|most|pct"] === "+8.30" && f["cd|a|cell|most|mw"] === "35" && f["cd|a|cell|least|pct"] === "-5.00" && /Largest: December at 23:00/.test(text) && /Smallest: January at 00:00/.test(text), "the cell that grew most and the one that grew least");
const src = fs.readFileSync(here("../components/demand/Country.tsx"), "utf-8");
ok(!/<svg|<rect|<path/.test(src) && src.includes('from "@/components/demand/Growth"') && src.includes('import { Explained } from "@/components/demand/Weather"') && src.includes('import { TimeChart } from "@/components/TimeChart"'), "the view draws no chart of its own: every chart is one the site already had");

// ---- with the weather taken out
ok(f["cd|a|w|2025|g"] === "+16.0" && f["cd|a|w|2025|w"] === "+1.0" && f["cd|a|w|2025|u"] === "+15.0" && f["cd|a|w|2025|pm"] === "2.0" && f["cd|a|w|2025|mw"] === "12,600" && f["cd|b|w|2022|u"] === "+2.0" && /data-reading="no" title="smaller than its uncertainty">no</.test(html) && /data-reading="finding" title="a finding">yes</.test(html),
  "the weather view for both regions: growth, the part the weather explains, the part it does not, its give or take, and whether it is a finding");
ok(/The year&#x27;s energy, 2025: growth against the average of 2019 to 2021, percent/.test(html) && html.includes('data-grid="ten"') && html.includes('data-grid="car"') && /by place, percent/.test(html) && text.includes("2026, part"), "its chart is the weather view's own, a row a place, in the last whole year held; the newest year says it is a part");
ok(ent(html).includes("Tennessee, 2025: 12,600 MW, read on the 8,700 of 8,760 hours the fit holds (the hours whose weather is held, table region_weather_hourly). The table above gives 12,600 MW for 2025, over the 8,760 hours it uses"), "a metered figure's hover sets it beside the table of years");
ok(f["cd|a|h|2019"] === W.signed(0.15) && f["cd|a|h|hour"] === "4.2" && f["cd|a|h|day"] === "3.2" && text.includes("Each of 2019, 2020, 2021 is left out in turn"), "the check on years the fit had not seen, for each place");
const win = draw({ figure: "winter", year: "2022" }), fw = figs(win);
ok(/The winter peak, 2022: growth against/.test(win) && !("cd|a|w|2022|g" in fw) && fw["cd|a|w|2023|g"] === "+14.0" && ent(win).includes("The file of Tennessee holds no figure of the winter peak for 2022.") && win.includes('<input type="hidden" name="figure" value="winter"/>') && win.includes('<input type="hidden" name="year" value="2022"/>'),
  "a figure and a year from the address; a figure the file lacks reads not held with why; the form carries the choice");
ok(html.includes('href="/demand?view=country&amp;a=ten&amp;b=car&amp;figure=summer&amp;year=2025#weather"') && html.includes('href="/demand?view=country&amp;a=ten&amp;b=car&amp;figure=energy&amp;year=2023#weather"'), "each figure and each year is a link that keeps the two places");

// ---- a balancing authority beside a region
const tva = draw({ a: "ba-tva", b: "ten" }), ft = figs(tva);
ok(tva.includes('data-cd-a="ba-tva"') && tva.includes('data-cd-b="ten"') && ft["cd|a|sum|avg0"] === "21,000" && ft["cd|b|sum|avg0"] === "12,000" && ent(tva).includes("Tennessee Valley Authority (TVA), a balancing authority that files Form EIA-930. EIA places it in its region Tennessee."), "a balancing authority beside a region: both drawn, the authority named with its region");
ok(ent(tva).includes("The weather view is built for EIA's regions, not for a single balancing authority: the file of Tennessee Valley Authority holds none.") && tva.includes('data-tip="Tennessee Valley Authority, 2025: not held"') && ft["cd|b|w|2025|g"] === "+16.0" && !Object.keys(ft).some((k) => k.startsWith("cd|a|w|")),
  "the authority holds no weather view: its row reads not held with why, and the region's stands");
const late = draw({ a: "ba-grid", b: "none" }), fl = figs(late);
ok(late.includes('data-cd-b=""') && fl["cd|a|sum|avg0"] === String((avgOf(28, 2022)).toLocaleString("en-US")) && !("cd|a|sum|avg_growth" in fl) && !("cd|a|y|2025|avg_growth" in fl) && fl["cd|a|y|2025|yoy"] !== undefined && ent(late).includes("holds no such figure for 2025: a growth needs the same measure in 2019")
  && !late.includes("md:grid-cols-2") && !late.includes('data-cd-place="b"'), "an authority whose record begins after 2019 has no growth since 2019: not held with why, never computed; one place alone is one column");
const gen = draw({ a: "ba-sepa", b: "ten" });
ok(gen.includes('data-cd-place="a" data-cd-code="ba-sepa" data-cd-state="no-demand"') && ent(gen).includes("EIA lists Southeastern Power Administration (SEPA) as a generation-only balancing authority: it files no demand") && !Object.keys(figs(gen)).some((k) => k.startsWith("cd|a|")) && figs(gen)["cd|b|sum|avg0"] === "12,000",
  "a generation-only authority can be chosen: it reads not held with why, no figure, and the other place stands");
ok(draw({ a: "mars" }).includes('data-cd-a="ten"') && draw({ a: "car" }).includes('data-cd-b=""') && draw({ a: "se", b: "se" }).includes('data-cd-b=""') && draw({ a: "se", b: "mars" }).includes('data-cd-b=""') && draw({ a: "se", b: "fla" }).includes('data-cd-b="fla"'),
  "a place the address does not name right falls back to the first; the same place twice is drawn once");

// ---- a region beside the grid that covers nearly its ground
ok(!html.includes("data-cd-alike=") && !html.includes('id="alike"'), "Tennessee and the Carolinas sit beside none of the seven grids: no such section");
const tex = draw({ a: "tex", b: "ny" }), fx = figs(tex);
ok(tex.includes('data-cd-alike="a" data-cd-alike-grid="ERCO"') && tex.includes('data-cd-alike="b" data-cd-alike-grid="NYIS"') && />Texas and ERCOT</.test(tex) && />New York and NYISO</.test(tex), "Texas beside ERCOT, New York beside NYISO: the section names both");
ok(fx["cd|a|alike|2019|region"] === "13,000" && fx["cd|a|alike|2019|grid"] === "12,900" && fx["cd|a|alike|2019|pct"] === "+0.78" && fx["cd|a|alike|2025|region"] === "13,600" && fx["cd|a|alike|2025|grid"] === "13,500" && count(tex, 'data-cd-alike-why="a|') === 7,
  "both figures stand, year by year, with the file's difference");
const whyHtml = C.sentence(WHY).replace(/'/g, "&#x27;");
ok(count(tex, `title="${whyHtml}"`) === 2 * 7 + 2 && tex.includes(`title="The region&#x27;s average less the grid&#x27;s, as a percent of the grid&#x27;s, as the file gives it. ${whyHtml}"`) && count(tex, ">Why they differ<") === 2, "the hover of each difference says why, in the data machine's own sentence");
ok(fx["cd|a|alike|apart"] === "7" && wordsOf(tex).includes("The two differ in 7 of the 7 years held."), "how many of the years held the two differ in");
const same = (file) => ({ ...file, alike: { ...file.alike, years: Object.fromEntries(Object.entries(file.alike.years).map(([y, r]) => [y, { ...r, grid_avg_demand_mw: r.region_avg_demand_mw, difference_pct: 0 }])) } });
const equal = renderToStaticMarkup(createElement(V.Country, { q: { a: "tex", b: "none" }, index, fileOf: () => same(files.tex) })), fq = figs(equal);
ok(fq["cd|a|alike|2019|region"] === "13,000" && fq["cd|a|alike|2019|grid"] === "13,000" && fq["cd|a|alike|2019|pct"] === "0.00" && fq["cd|a|alike|years"] === "7" && !("cd|a|alike|apart" in fq) && wordsOf(equal).includes("The two are equal in each of the 7 years held.")
  && equal.includes(">Why they can differ<") && !equal.includes(">Why they differ<") && count(equal, `title="${whyHtml}"`) === 7 + 1,
  "where the two are equal in every year the view says so, both figures still stand, and the sentence is offered as why they can differ");
ok(tex.includes('href="/demand?area=ercot"') && tex.includes('href="/demand?view=country&amp;a=tex&amp;b=ba-erco"') && tex.includes('href="/demand?area=nyiso"'), "each links the grid's own view, and the region beside the grid as two places");
ok(Object.keys(ALIKE).join() === "TEX,NY,NE,MIDA" && Object.keys(ALIKE).every((c) => draw({ a: c.toLowerCase(), b: "none" }).includes(`data-cd-alike-grid="${ALIKE[c]}"`)), "the four pairs of the contract: Texas, New York, New England and the Mid-Atlantic");
const erco = draw({ a: "tex", b: "ba-erco" }), fe = figs(erco);
ok(fe["cd|a|sum|avg0"] === "13,000" && fe["cd|b|sum|avg0"] === "24,000" && ent(erco).includes("It is ERCOT, one of the seven grids of the other views."), "the region and the grid as two places: each from its own file");

// ---- the standard: hovers, sources, no advice, no sideways scroll
const heads = [...html.matchAll(/<span title="([^"]*)" data-cd-head="([^"]+)"/g)];
ok(heads.length >= 30 && heads.every((m) => m[1].length > 25) && count(html, "data-cd-head=") === heads.length, `every marked column head carries its hover (${heads.length})`);
ok(/data-cd-source="1"[\s\S]*EIA Form EIA-930, hourly demand by balancing authority and region \(public domain\)[\s\S]*eia930_region_hourly[\s\S]*the file of Tennessee built 2026-11-19[\s\S]*the index built 2026-11-19/.test(html) && html.includes('href="/data/methods/demand_growth"'), "the source line names EIA's form, the tables, the days the files were built, and the method");
ok(!dash.some((c) => html.includes(c)) && !/\b(should|recommend|we advise|must)\b/i.test(text) && !/NaN|undefined|Infinity/.test(text) && !/NaN|undefined|Infinity/.test(html.replace(/<svg[\s\S]*?<\/svg>/g, "")), "no dash, no advice, no NaN or undefined in the view");
ok(!/donor|taker|covered by imports/i.test(text), "no ledger of regions that gave and took, no share covered by imports");
ok(!/min-w-\[|w-\[\d{3,}px\]/.test(html) && count(html, 'class="overflow-x-auto"') === 7 && count(html, "<table") === 7, "every table scrolls inside its own frame (no sideways scroll of the page at 390 px)");
ok(count(html, "md:grid-cols-2") >= 4 && /Default: every day held, this page's own choice \(session 8420\)/.test(text) && /Defaults: the year's energy, in the last whole year held/.test(text), "A and B stand in two columns from the middle width up, one under the other on a phone; each default is said on hover");

// ---- held, and not built
const heldFiles = { ...files, ten: demandFixture("TEN", { license: "internal" }) };
const heldHtml = renderToStaticMarkup(createElement(V.Country, { q: {}, index, fileOf: (p) => heldFiles[C.placeKey(p)] ?? null }));
const fh = figs(heldHtml);
ok(heldHtml.includes('data-cd-place="a" data-cd-code="ten" data-cd-state="held"') && !Object.keys(fh).some((k) => k.startsWith("cd|a|")) && fh["cd|b|sum|avg0"] === "2,000" && count(heldHtml, 'data-license-held="1"') >= 1 + 9 + 14 + 8 * 7 && heldHtml.includes("license needed"),
  "a file that is not public: every cell of the place blank with license needed on hover, no figure, no chart; the other place stands");
ok(count(heldHtml, 'data-chart="years"') === 1 && count(heldHtml, ">Tennessee</th>") >= 9 && heldHtml.includes('data-cd-daily="a" data-cd-points="0"'), "a held place still has its rows: a held value is not left off");
ok(V.heldWhyOf(ten) === null && /license needed/.test(V.heldWhyOf(heldFiles.ten)) && /license needed: /.test(V.heldWhyOf(demandFixture("TEN", { tables: ["event_window_daily"] })) ?? ""), "held when the license line is not public or a table it names is license needed in the status file");
const none = renderToStaticMarkup(createElement(V.Country, { q: {}, index: null, fileOf: () => null }));
ok(none.includes('data-cd-place="a" data-cd-code="ten" data-cd-state="not-built"') && none.includes('data-cd-place="b" data-cd-code="car" data-cd-state="not-built"') && count(none, ">not built yet<") >= 3 && Object.keys(figs(none)).length === 0 && figuresOf(none) === 0
  && none.includes("site/data/regions/demand/ten.json") && none.includes("site/data/regions/index.json") && !none.includes('id="by-day"') && !none.includes("<svg"), "with no file the view says not built yet for each place and for the index, names the files on hover, and draws no figure and no chart");
ok(CODES.every((c) => none.includes(`data-cd-region="${c}"`)) && count(none, 'data-cd-region-new="1"') === 6 && count(none, "<option ") === 13 + 14 + 1 && none.includes('data-cd-index="not-built"'), "the thirteen regions are still named and can be chosen, the six new ones marked, before any file lands");
const half = renderToStaticMarkup(createElement(V.Country, { q: {}, index, fileOf: (p) => (p.code === "CAR" ? null : fileOf(p)) })), fhalf = figs(half);
ok(half.includes('data-cd-place="b" data-cd-code="car" data-cd-state="not-built"') && fhalf["cd|a|sum|avg0"] === "12,000" && !Object.keys(fhalf).some((k) => k.startsWith("cd|b|")) && count(half, 'data-chart="years"') === 1 && />Carolinas<\/th><td colSpan="\d+"[^>]*><span[^>]*title="The file of Carolinas \(site\/data\/regions\/demand\/car\.json\)/.test(half),
  "one place built and the other not: the first is drawn, the second reads not built yet in every table");
const bare = renderToStaticMarkup(createElement(V.Country, { q: { a: "ba-tva", b: "none" }, index: null, fileOf }));
ok(bare.includes('data-cd-a="ba-tva"') && figs(bare)["cd|a|sum|avg0"] === "21,000" && /<option value="ba-tva" selected="">TVA: Tennessee Valley Authority<\/option>/.test(bare), "without the index a balancing authority named in the address is still read and drawn");
const thin = { ...ten, growth: undefined, daily: undefined, weather: undefined };
const thinHtml = renderToStaticMarkup(createElement(V.Country, { q: { a: "ten", b: "none" }, index, fileOf: () => thin }));
ok(Object.keys(figs(thinHtml)).length === 0 && count(thinHtml, 'data-not-held="1"') >= 5 && !/NaN|undefined|Infinity/.test(wordsOf(thinHtml)) && !thinHtml.includes("<svg"), "a file with no daily series, no growth and no weather: not held with why, section by section, nothing drawn");

const lone = (file) => renderToStaticMarkup(createElement(V.Country, { q: { a: "ten", b: "none" }, index, fileOf: () => file }));
const noMonth = lone({ ...ten, growth: { ...ten.growth, ytd_through: undefined }, screened: undefined }), fm = figs(noMonth);
ok(fm["cd|a|y|2025|avg"] === "12,600" && fm["cd|a|sum|avg_growth"] === "+5.00" && !("cd|a|y|ytd|avg" in fm) && !("cd|a|sum|ytd_growth" in fm) && !noMonth.includes("data-cd-screened") && !/NaN|undefined|Infinity/.test(wordsOf(noMonth)),
  "a file that does not say which month the year so far runs to, or how many hours were left out: the whole years stand and nothing is made up");
const noBase = lone({ ...ten, growth: { ...ten.growth, base: undefined } }), fb = figs(noBase);
ok(!Object.keys(fb).some((k) => k.startsWith("cd|a|y|") || k.startsWith("cd|a|sum|") || k.startsWith("cd|a|cell|")) && fb["cd|a|day|top_mw"] === "12,660" && count(noBase, 'data-chart="years"') === 0 && !/NaN|undefined|Infinity/.test(wordsOf(noBase)),
  "a file whose growth names no base year: its years read not held, its days are still drawn");

// ---- the reader: a fixture is never read from the site's own folder; the whole page
ok(process.env.ERW_REGIONS_DIR === undefined, "ERW_REGIONS_DIR is not set as the test starts");
const onSite = (rel) => fs.existsSync(here(`../data/regions/${rel}`));
ok(!onSite("index.json") || !("fixture" in JSON.parse(fs.readFileSync(here("../data/regions/index.json"), "utf-8"))), "no fixture stands in the site's own folder");
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "erw-demand-regions-"));
writeFixtureFolder(tmp);
const cwd = process.cwd();
try {
  process.chdir(tmp);  // a folder whose data/regions holds the fixture, read as the site reads its own
  writeFixtureFolder(path.join(tmp, "data", "regions"));
  ok(C.regionsIndex() === null && C.demandPlaceFile(reg("TEN")) === null && C.demandPlaceFile(ba("TVA")) === null, "a fixture in the site's own folder is refused: the index and the files");
} finally { process.chdir(cwd); }

for (const [name, query] of ADDRESSES.filter(([k]) => ["plain", "weather", "consumption"].includes(k))) {
  const page = await drawDemand(query);
  ok(count(page, 'data-tab="country"') === 1 && /<a href="\/demand\?view=country" data-tab="country" data-view="country" class="[^"]*">The whole country<\/a>/.test(page) && count(withoutAdded(page), 'data-tab="country"') === 0 && page.length - withoutAdded(page).length < 220,
    `${name}: the row of tabs gains "The whole country", and the pin's cut removes that anchor and nothing else`);
}
ok(T.TABBED["/demand"].tabs.map((t) => t[0]).join() === "metered,weather,consumption,country" && T.tabHref("/demand", "country") === "/demand?view=country" && P.VIEWS.map((v) => v[0]).join() === "metered,weather,consumption,country"
  && P.viewOf({ view: "country" }) === "country" && P.viewOf({}) === "metered" && P.viewOf({ view: "mars" }) === "metered" && P.viewOf({ view: "weather" }) === "weather" && P.viewHref("country") === "/demand?view=country" && P.METHODS.country.href === "/data/methods/demand_growth",
  "the fourth view has its tab, its address and its method note; the three before it keep theirs");
if (!onSite("index.json") && !onSite("demand/ten.json")) {
  const page = await drawDemand({ view: "country" });
  ok(page.includes('data-demand="country"') && /data-tab="country" data-view="country"/.test(page) && /aria-current="page" data-tab="country"/.test(page) && page.includes('data-cd-state="not-built"') && figuresOf(page) === 0, "the whole page with no file on the site: the tab is current, not built yet, no figure");
}
process.env.ERW_REGIONS_DIR = tmp;
try {
  const page = await drawDemand({ view: "country" });
  ok(page.includes('data-demand="country"') && page.includes('data-cd-a="ten"') && page.includes('data-cd-b="car"') && figs(page)["cd|a|sum|avg_growth"] === "+5.00" && figuresOf(page) > 150, "the whole page with files: drawn, Tennessee and the Carolinas first");
  const page2 = await drawDemand({ view: "country", a: "se", b: "ba-soco", days: "2025", figure: "night", year: "2024" });
  ok(page2.includes('data-cd-a="se"') && page2.includes('data-cd-b="ba-soco"') && page2.includes('data-cd-days="2025"') && /The overnight minimum, 2024/.test(page2), "the page reads every choice from its address");
  fs.writeFileSync(path.join(tmp, "demand", "fla.json"), "{ not json");
  const page3 = await drawDemand({ view: "country", a: "fla", b: "none" });
  ok(page3.includes('data-cd-code="fla" data-cd-state="not-built"'), "a file that cannot be read as JSON is treated as not built");
} finally { delete process.env.ERW_REGIONS_DIR; fs.rmSync(tmp, { recursive: true, force: true }); }

// ---- the real files, where the data machine's have landed: their form, as the contract gives it (skipped until then)
if (onSite("index.json")) {
  const real = C.regionsIndex();
  ok(!!real && real.regions.length === 13 && real.regions.map((r) => r.code).join() === CODES.join() && real.bas.length > 40 && real.license === "public", "the real index: thirteen regions in EIA's order, the balancing authorities, public");
  let read = 0, shaped = 0;
  for (const r of real?.regions ?? []) {
    const file = C.demandPlaceFile(reg(r.code));
    if (!file) continue;
    read++;
    const d = file.daily;
    if (file.code === r.code && file.level === "region" && file.license === "public" && file.growth?.base && d && [d.demand_mwh, d.peak_mw, d.peak_at, d.hours].every((x) => Array.isArray(x) && x.length === d.days.length)) shaped++;
  }
  ok(read === shaped, `the real region files on the site have the contract's form (${shaped} of ${read} read)`);
  if (read) {
    const page = await drawDemand({ view: "country" });
    ok(page.includes('data-view-body="country"') && !/NaN|undefined|Infinity/.test(wordsOf(page)) && !dash.some((c) => page.includes(c)), "the view draws on the real files with no NaN, no undefined and no dash");
    const D = JSON.parse(fs.readFileSync(here("../data/demand_growth.json"), "utf-8"));
    for (const [code, grid] of Object.entries(ALIKE)) {
      const a = C.demandPlaceFile(reg(code))?.alike;
      if (!a) { console.log(`note ${code}: the real file gives no alike object`); continue; }
      const rows = C.alikeRows(a), off = rows.filter((x) => x.grid !== null && D.areas[grid]?.years[x.year]?.avg_demand_mw !== undefined && Math.abs(x.grid - D.areas[grid].years[x.year].avg_demand_mw) > 0.06);
      const sign = rows.filter((x) => x.region !== null && x.grid !== null && x.pct !== null && Math.abs(x.pct - ((x.region - x.grid) / x.grid) * 100) > 0.02);
      console.log(`note ${code} and ${grid}: ${rows.length} years; ${off.length} where the grid's average is not the as-metered view's; ${sign.length} where the difference is not the region's less the grid's over the grid's${a.why ? "" : "; no sentence on why"}`);
    }
  }
}

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
