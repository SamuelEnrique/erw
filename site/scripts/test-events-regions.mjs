// Energy Research Warehouse (ERW) site, session 8410 (chain 503, part B): "The whole country" on the event pages and the
// index's line of regions, held without a build. The section is drawn to HTML with the site's own code from a fixture
// in the form of the data machine's contract (scripts/regions-fixture.mjs: values made by a rule, not data), and the
// whole pages are drawn with no file (as the site stands until the data machine's files land) and with the fixture in
// a folder of its own (ERW_REGIONS_DIR). No table, no server, no network, no click.
//   node --import ./scripts/events-page-register.mjs scripts/test-events-regions.mjs
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { withoutAdded } from "./events-added.mjs";
import { csvRows, drawPage, pageText, PAGES } from "./events-pages.mjs";
import { CODES, eventFixture } from "./regions-fixture.mjs";

const C = await import("../lib/countryfiles.ts");
const W = await import("../app/events/WholeCountry.tsx");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const near = (a, b) => Math.abs(a - b) < 1e-9;
const here = (p) => new URL(p, import.meta.url);
const dash = [String.fromCharCode(0x2014), String.fromCharCode(0x2013)];
const figs = (html) => Object.fromEntries([...html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)].map((m) => [m[1], m[2]]));
const draw = (props) => renderToStaticMarkup(createElement(W.WholeCountry, { event: "elliott_2022", path: "/events/elliott-2022", first: "TEN", second: "CAR", firstWhy: "Tennessee and the Carolinas are drawn first.", q: {}, ...props }));

// ---- the library on the fixture: every expected value recomputed here from the fixture's rule
const file = eventFixture();
const N = file.hours.n;
ok(C.REGION_CODES.join() === CODES.join() && C.REGION_CODES.length === 13, "the thirteen regions, in the contract's order");
ok(C.NEW_REGIONS.map((c) => C.REGION_NAME[c]).join(", ") === "Southeast, Florida, Carolinas, Tennessee, Northwest, Southwest", "the six regions new to the site, by name");
ok(C.NEW_REGIONS.every((c) => C.REGION_GRIDS[c].length === 0) && C.REGION_CODES.filter((c) => !C.NEW_REGIONS.includes(c)).every((c) => C.REGION_GRIDS[c].length === 1), "a region is new exactly when none of the seven grids is in it");
const rows = C.summarize(file);
const by = Object.fromEntries(rows.map((r) => [r.code, r]));
ok(rows.length === 13 && rows.map((r) => r.code).join() === CODES.join(), "summarize gives the thirteen in order, the one the file lacks included");
ok(by.NW.held === false && by.NW.demand === null && by.NW.peak === null && by.NW.hoursHeld === 0, "a region the file does not hold has no figure");
// California, region 1: event 1000 + h, baseline 1000
const sumH = (N * (N - 1)) / 2;
ok(by.CAL.demand.hours === N && near(by.CAL.demand.mwh, 1000 * N + sumH) && near(by.CAL.demand.base_mwh, 1000 * N) && near(by.CAL.demand.diff_mwh, sumH) && near(by.CAL.demand.pct, (sumH / (1000 * N)) * 100),
  "demand against the baseline: sums over the hours both hold, the difference and the percent");
ok(by.CAL.peak.mw === 1000 + N - 1 && by.CAL.peak.at === C.hourAt(file.hours, N - 1) && by.CAL.peak.base_mw === 1000, "the highest hour, when it was, and the baseline at that same hour");
ok(C.hourAt(file.hours, 0) === "2022-12-19T05:00:00Z" && C.hourAt(file.hours, 24) === "2022-12-20T05:00:00Z" && C.utcHour("2022-12-20T05:00:00Z") === "2022-12-20 05:00 UTC", "an hour of the file by its position, in UTC");
// the Southwest, region 11: its first six hours are null
ok(by.SW.demand.hours === N - 6 && by.SW.hoursHeld === N - 6 && near(by.SW.demand.base_mwh, 11000 * (N - 6)), "a null hour is left out of both sums, never filled");
// Tennessee, region 12, and the Carolinas, region 2
ok(near(by.TEN.demand.pct, 20) && near(by.CAR.demand.pct, -10) && near(by.TEN.imports.mean_mw, 500) && near(by.TEN.imports.base_mean_mw, -100) && near(by.CAR.imports.mean_mw, -300), "Tennessee +20 percent and importing, the Carolinas -10 percent and exporting");
ok(near(by.TEN.sources.natural_gas.diff_mwh, 10 * N) && near(by.TEN.sources.storage.diff_mwh, -70 * N) && by.FLA.sources.coal === null && near(by.TEN.generation.diff_mwh, 100 * 12 * N), "generation by source less the baseline; a source the file lacks has no figure");
const hit = C.reached(rows);
ok(C.REACHED_PCT === 5 && hit.map((r) => r.code).join() === "CAR,TEN", "reached: demand over the window 5 percent or more from the baseline, above or below");
const ps = C.pairs(file);
const pair = Object.fromEntries(ps.map((p) => [p.key, p]));
ok(ps.map((p) => p.key).join() === "CAR-TEN,SE-TEN,FLA-SE", "the pairs, largest energy over the window first");
ok(pair["CAR-TEN"].sent === "CAR" && pair["CAR-TEN"].took === "TEN" && near(pair["CAR-TEN"].mwh, 200 * N) && pair["CAR-TEN"].base.sent === "TEN" && pair["CAR-TEN"].base.took === "CAR" && near(pair["CAR-TEN"].base.mean_mw, -50),
  "a pair above zero: the first region sent and the second took; its baseline ran the other way");
ok(pair["SE-TEN"].sent === "TEN" && pair["SE-TEN"].took === "SE" && pair["FLA-SE"].sent === null && pair["FLA-SE"].took === null && pair["FLA-SE"].base.sent === "FLA", "a pair below zero: the second sent; a pair at zero names neither");
ok(C.regionOf("ten") === "TEN" && C.regionOf("TEX") === "TEX" && C.regionOf("pjm") === null && C.regionOf(undefined) === null, "a region from the address, or none");
const long = eventFixture({ n: 30 * 24, first: "2020-03-01T05:00:00Z" });
ok(!C.drawnByDay(file.hours) && C.points(file.regions.CAL.demand_mw, file.hours).length === N && C.drawnByDay(long.hours) && C.points(long.regions.CAL.demand_mw, long.hours).length === 31,
  "a window of 21 days or less is drawn by hour, a longer one by UTC day");
ok(C.points(file.regions.SW.demand_mw, file.hours).length === N - 6 && C.points(undefined, file.hours).length === 0, "a null hour has no point");
ok(C.baselineOf(file).words === "same weekdays 364 and 728 days earlier" && C.baselineOf(file).offsets.join() === "364,728" && C.baselineOf({ ...file, baseline: { how: "x", baseline_offsets_days: [7] }, baseline_offsets_days: undefined }).offsets.join() === "7", "the baseline's own words and offsets, in either form");

// ---- the section drawn from the fixture
const html = draw({ file });
const text = pageText(html);
const f = figs(html);
ok(html.startsWith('<section data-whole-country="elliott_2022" id="whole-country"') && html.endsWith('<span data-whole-country-end="1"></span>'), "the section stands between its two marks");
ok(/<h2[^>]*>The whole country<\/h2>/.test(html) && html.includes('data-wc-state="drawn"'), "its title is The whole country");
ok(CODES.every((c) => html.includes(`data-wc-row="${c}"`)) && CODES.every((c) => text.includes(C.REGION_NAME[c])), "each of the thirteen regions has its row, by name");
ok((html.match(/data-wc-new="1"/g) ?? []).length === 6 && ["SE", "FLA", "CAR", "TEN", "NW", "SW"].every((c) => new RegExp(`data-wc-row="${c}" data-wc-new="1"`).test(html)), "the six regions new to the site carry their mark");
ok(text.includes("Southeast, Florida, Carolinas, Tennessee, Northwest, Southwest: none of the seven grids"), "the six are named in the lead's hover");
// the data machine's builder (warehouse/derived/regions_pages.py, event_doc) writes the offsets of a baseline by calendar
// year as words, and the window's own words
const byYear = pageText(draw({ file: { ...file, baseline: "the same calendar days of 2019 and 2020", baseline_offsets_days: ["2 calendar year(s)", "1 calendar year(s)"], window: "from the first day's midnight, Eastern time, to the midnight after the last day, Pacific time" } }));
ok(byYear.includes("The file's own words: the same calendar days of 2019 and 2020. Offsets: 2 calendar year(s), 1 calendar year(s).") && byYear.includes("The window's hours, in the file's words: from the first day's midnight, Eastern time")
  && text.includes("Offsets in days: 364, 728.") && !text.includes("The window's hours, in the file's words"), "the baseline's hover gives the file's own words, its offsets in days or in words, and the window's words where the file has them");
ok(f["wc|TEN|demand_pct"] === "+20.0" && f["wc|CAR|demand_pct"] === "-10.0" && f["wc|TEN|demand_gwh"] === C.gwh(14400 * N) && f["wc|TEN|peak_mw"] === "14,400" && f["wc|TEN|peak_base_mw"] === "12,000", "Tennessee's row: demand, percent, highest hour and the baseline at that hour");
ok(f["wc|TEN|imports_mw"] === "+500" && f["wc|TEN|imports_base_mw"] === "-100" && f["wc|CAR|imports_mw"] === "-300" && f["wc|SW|hours"] === String(N - 6), "net imports with their sign, and the hours held");
ok(f["wc|TEN|gen|natural_gas"] === C.signedGwh(10 * N) && f["wc|TEN|gen|storage"] === C.signedGwh(-70 * N) && f["wc|TEN|gen|net"] === C.signedGwh(1200 * N) && !("wc|FLA|gen|coal" in f), "generation by source less the baseline, in GWh");
ok(!Object.keys(f).some((k) => k.startsWith("wc|NW|") && k !== "wc|NW|hours") && (html.match(/data-not-held="1"/g) ?? []).length >= 8 && text.includes("The file holds no hour of demand for Northwest"), "the region the file lacks reads not held, with why on hover");
ok(f["wc|pair|CAR-TEN|mean_mw"] === "200" && f["wc|pair|CAR-TEN|gwh"] === C.gwh(200 * N) && f["wc|pair|SE-TEN|mean_mw"] === "150" && f["wc|pair|CAR-TEN|base_mean_mw"] === "50", "each pair's mean and energy, in the direction shown");
const pairLine = (k) => (new RegExp(`<tr[^>]*>(?:(?!</tr>)[\\s\\S])*data-wc-pair="${k}"[\\s\\S]*?</tr>`).exec(html) ?? [""])[0].replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");
ok(/Carolinas Tennessee 200 .* Tennessee to Carolinas 50/.test(pairLine("CAR-TEN")) && /Tennessee Southeast 150/.test(pairLine("SE-TEN")) && /Florida and Southeast: no net flow/.test(pairLine("FLA-SE")), "pair by pair: which region sent and which took, and the baseline's direction");
ok(!/donor|taker|share of the (shock|shortfall)|covered by imports/i.test(text), "no ledger of regions that gave and took, no share covered by imports");
ok(html.includes('data-wc-a="TEN"') && html.includes('data-wc-b="CAR"') && html.includes('data-wc-charts="a" data-wc-region="TEN"') && html.includes('data-wc-charts="b" data-wc-region="CAR"'), "the regions drawn first are the page's own two");
ok(html.includes('action="/events/elliott-2022#whole-country"') && html.includes('name="region"') && html.includes('name="b"') && (html.match(/<option /g) ?? []).length === 27, "the choice: two lists of the thirteen (the second with None) in a form that needs no script");
const one = draw({ file, q: { region: "tex", b: "none" } });
ok(one.includes('data-wc-a="TEX"') && one.includes('data-wc-b=""') && !one.includes('data-wc-charts="b"') && one.includes('data-wc-region="TEX"'), "a region from the address redraws the charts for it; None draws one");
const same = draw({ file, q: { region: "car", b: "car" } });
ok(same.includes('data-wc-a="CAR"') && same.includes('data-wc-b=""'), "the same region twice draws it once");
const bad = draw({ file, q: { region: "pjm" } });
ok(bad.includes('data-wc-a="TEN"'), "a region that is none of the thirteen falls back to the page's first");
const nw = draw({ file, q: { region: "nw", b: "none" } });
ok(/data-wc-charts="a" data-wc-region="NW"[\s\S]*?data-not-held="1"/.test(nw), "a chosen region the file lacks reads not held, no chart");
ok(CODES.every((c) => html.includes(`href="/events/elliott-2022?region=${c.toLowerCase()}#whole-country"`)), "each region's name chooses it");
const heads = [...html.matchAll(/data-wc-head="([^"]+)"/g)].map((m) => m[1]);
ok(heads.length === 8 + 9 + 7 &&[...html.matchAll(/<span title="([^"]*)" data-wc-head=/g)].every((m) => m[1].length > 30), "every column head carries its hover");
ok(/data-wc-source="1"[\s\S]*EIA Form EIA-930 \(public domain\)[\s\S]*eia930_region_hourly[\s\S]*file built 2026-11-19/.test(html) && html.includes('href="/data/methods/events"'), "the source line names EIA's form, the tables, the build day and the method");
ok(!dash.some((c) => html.includes(c)) && !/\b(should|recommend|we advise)\b/i.test(text) && !/NaN|undefined|Infinity/.test(text.replace(/\[title:[^\]]*\]/g, "")) && !/NaN|undefined|Infinity/.test(html.replace(/echarts|data-chart[^>]*>/g, "")),
  "no dash, no advice, no NaN or undefined in the section");
ok(!/min-w-\[|w-\[\d{3,}px\]/.test(html) && (html.match(/class="overflow-x-auto"/g) ?? []).length === 3, "the three tables scroll inside their own frames (no sideways scroll of the page at 390 px)");
const longHtml = draw({ file: long, event: "covid_2020", path: "/events/covid-2020", first: "CAL", second: undefined });
ok(longHtml.includes("Drawn by day") && html.includes("Drawn by hour"), "a long window says it is drawn by day");

// ---- held, and not built
const heldFile = eventFixture({ license: "internal" });
const heldHtml = draw({ file: heldFile });
ok(Object.keys(figs(heldHtml)).length === 0 && (heldHtml.match(/data-license-held="1"/g) ?? []).length >= 13 * 17 && !heldHtml.includes("data-wc-region=") && heldHtml.includes("license needed"), "a file that is not public: every cell blank with license needed on hover, no figure, no chart");
ok(CODES.every((c) => heldHtml.includes(`data-wc-row="${c}"`)), "a held file still draws its rows: a held value is not left off");
ok(W.heldWhy(file) === null && /license needed/.test(W.heldWhy(heldFile)) && /license needed: /.test(W.heldWhy(eventFixture({ tables: ["event_window_daily"] })) ?? ""), "held when the license line is not public or a table it names is license needed in the status file");
W.REGIONS_HELD.push("NE");
const neHeld = draw({ file });
W.REGIONS_HELD.pop();
ok(!Object.keys(figs(neHeld)).some((k) => k.startsWith("wc|NE|")) && "wc|TEN|demand_pct" in figs(neHeld) && (neHeld.match(/data-license-held="1"/g) ?? []).length === 17, "a region put on hold is drawn blank, cell by cell, and the others stand");
const none = draw({ file: null });
ok(none.includes('data-wc-state="not-built"') && none.includes("not built yet") && Object.keys(figs(none)).length === 0 && /Southeast[\s\S]*Tennessee/.test(none) && none.includes("site/data/regions/events/elliott_2022.json"),
  "with no file the section says not built yet, names the regions on hover and draws no figure");
ok(withoutAdded(html) === "" && withoutAdded(none) === "", "the pin's cut removes the whole section");

// ---- the reader: a fixture is never read from the site's own folder
ok(process.env.ERW_REGIONS_DIR === undefined, "ERW_REGIONS_DIR is not set as the test starts");
ok(!fs.existsSync(here("../data/regions/events/elliott_2022.json")) || !("fixture" in JSON.parse(fs.readFileSync(here("../data/regions/events/elliott_2022.json"), "utf-8"))), "no fixture stands in the site's own folder");
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "erw-regions-"));
fs.mkdirSync(path.join(tmp, "events"), { recursive: true });
fs.writeFileSync(path.join(tmp, "events", "elliott_2022.json"), JSON.stringify(file));
fs.writeFileSync(path.join(tmp, "events", "uri_2021.json"), "{ not json");
const cwd = process.cwd();
try {
  process.chdir(tmp);  // a folder whose data/regions holds a fixture, read as the site reads its own
  fs.mkdirSync(path.join(tmp, "data", "regions", "events"), { recursive: true });
  fs.writeFileSync(path.join(tmp, "data", "regions", "events", "elliott_2022.json"), JSON.stringify(file));
  ok(C.eventRegionsFile("elliott_2022") === null, "a fixture in the site's own folder is refused");
} finally { process.chdir(cwd); }

// ---- the whole pages: with no file (the site until the files land), then with the fixture in a folder of its own
const tables = { event_window_daily: csvRows(here("../../replication/events/window_rows.csv")), caiso_grid_emergencies: csvRows(here("../../replication/events/notice_rows.csv")) };
const rowsOf = (name) => tables[name] ?? null;
const hasFile = (ev) => fs.existsSync(here(`../data/regions/events/${ev}.json`));
for (const [slug, pfile] of PAGES) {
  const { html: page } = await drawPage(pfile, rowsOf);
  if (slug === "index") {
    ok((page.match(/data-regions-reached="/g) ?? []).length === 9 && (page.match(/data-regions-reached-end="1"/g) ?? []).length === 9, "index: each of the nine events has its line of regions");
    continue;
  }
  const ev = slug.replace(/-/g, "_");
  const at = page.indexOf(`<section data-whole-country="${ev}"`), dec = page.indexOf("data-decisions=");
  ok(at > 0 && (page.match(/data-whole-country="/g) ?? []).length === 1 && at < dec, `${slug}: the section is on the page once, above the decisions block`);
  if (!hasFile(ev)) ok(/data-wc-state="not-built"/.test(page), `${slug}: with no file on the site, not built yet and no figure`);
}
process.env.ERW_REGIONS_DIR = tmp;
try {
  const { html: ell } = await drawPage("../app/events/elliott-2022/page.tsx", rowsOf, { searchParams: Promise.resolve({}) });
  ok(ell.includes('data-wc-state="drawn"') && ell.includes('data-wc-a="TEN"') && ell.includes('data-wc-b="CAR"') && figs(ell)["wc|TEN|demand_pct"] === "+20.0", "Winter Storm Elliott's page with a file: drawn, Tennessee and the Carolinas first");
  ok(pageText(ell).includes("the balancing authorities that shed firm load were in the southeast, among them TVA and Duke"), "the hover says why those two are first, in the page's own words of FERC and NERC");
  const { html: ell2 } = await drawPage("../app/events/elliott-2022/page.tsx", rowsOf, { searchParams: Promise.resolve({ region: "se", b: "fla" }) });
  ok(ell2.includes('data-wc-a="SE"') && ell2.includes('data-wc-b="FLA"'), "the page reads the choice from its address");
  const { html: uri } = await drawPage("../app/events/uri-2021/page.tsx", rowsOf, { searchParams: Promise.resolve({}) });
  ok(uri.includes('data-wc-state="not-built"'), "a file that cannot be read as JSON is treated as not built");
  const { html: ix } = await drawPage("../app/events/page.tsx", rowsOf);
  const line = (/<span data-regions-reached="elliott_2022"[\s\S]*?<span data-regions-reached-end="1">/.exec(ix) ?? [""])[0];
  const lf = figs(line);
  ok(lf["reached|elliott_2022|n"] === "2" && lf["reached|elliott_2022|of"] === "12" && /Carolinas, Tennessee/.test(line) && /Default: 5 percent/.test(line) && /Source: EIA Form EIA-930/.test(line), "index: Elliott's row says 2 of 12 regions, names them, and gives the rule, its default and its source on hover");
  ok(/href="\/events\/elliott-2022#whole-country"/.test(line), "index: the row links to the section");
} finally { delete process.env.ERW_REGIONS_DIR; fs.rmSync(tmp, { recursive: true, force: true }); }

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
