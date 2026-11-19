// Energy Research Warehouse (ERW) site, session 8430 (chain 503, part D): "The whole country" on /supply, held without
// a build. The section is drawn to HTML with the site's own code from fixtures in the form of the data machine's
// contract (scripts/regions-fixture-trade.mjs: values made by a rule, not data), and the whole page is drawn with no
// file (as the site stands until the data machine's files land) and with the fixtures in a folder of its own
// (ERW_REGIONS_DIR). The page's own input files are the copy kept with the pin. No table, no server, no network, no click.
//   node --import ./scripts/supply-pin-register.mjs scripts/test-supply-regions.mjs
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { pageText } from "./battery-awards-page.mjs";
import { BA_PAIRS, CODES, NEIGHBOURS, PARTNERS, REGION_PAIRS, SOURCE_KEYS, energyOf, fixtureMonths, fixtureReaders, indexFixture, matrixFixture, mixFixture, ownOf, pairOf, tradeFixture } from "./regions-fixture-trade.mjs";
import { figureCount, fixClock, standInCatalogue, supplyAdded, withoutSupplyAdded } from "./supply-added.mjs";

const F = await import("../lib/countryfiles.ts");
const T = await import("../lib/countrytrade.ts");
const S = await import("../components/supply/Country.tsx");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const near = (a, b) => Math.abs(a - b) < 1e-6;
const here = (p) => new URL(p, import.meta.url);
const dash = [String.fromCharCode(0x2014), String.fromCharCode(0x2013)];
const figs = (html) => Object.fromEntries([...html.matchAll(/<span data-cn="([^"]+)">([^<]*)<\/span>/g)].map((m) => [m[1], m[2]]));
// the page as a reader sees it with no hover: tags and their attributes gone (scripts/check-supply.mjs reads it so)
const seen = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
const draw = (props = {}) => renderToStaticMarkup(createElement(S.Country, { q: {}, read: fixtureReaders(), ...props }));
const sum = (xs) => xs.reduce((s, v) => s + v, 0);
const rowOf = (html, mark) => (new RegExp(`<tr[^>]*>(?:(?!</tr>)[\\s\\S])*${mark}[\\s\\S]*?</tr>`).exec(html) ?? [""])[0];

// ---- the library on the fixtures: every expected value recomputed here from the fixture's rule
const months = fixtureMonths();
const Y25 = months.map((m, i) => (m.startsWith("2025") ? i : -1)).filter((i) => i >= 0);
ok(months.length === 100 && months[0] === T.FIRST_MONTH && months[99] === "2026-10" && Y25.length === 12 && Y25[0] === 78, "the fixture's months run from July 2018 to October 2026");
ok(T.NEIGHBOUR_CODES.join() === [...CODES, "CAN", "MEX"].join() && T.placeName("CAN") === "Canada" && T.placeName("MEX") === "Mexico" && T.placeName("TVA") === "TVA", "the thirteen regions, then Canada and Mexico, by name");
ok(T.inOrder(["MEX", "TVA", "SE", "CAL", "CAN"]).join() === "CAL,SE,CAN,MEX,TVA", "codes in the contract's order, any other code after them");
const ten = tradeFixture("TEN"), car = tradeFixture("CAR");
ok(T.monthsOfYear(ten.months, "2025").join() === Y25.join() && T.monthsOfYear(ten.months, "2018").length === 6 && T.monthsOfYear(ten.months, "2026").length === 10 && T.yearsOf(ten.months).join() === "2018,2019,2020,2021,2022,2023,2024,2025,2026", "a year's months in a file, and the years a file touches");
const own = (code, nb, at) => sum(at.map((m) => ownOf(code, nb, m)));
const nb25 = Object.fromEntries(T.neighboursOfYear(ten, "2025").map((x) => [x.code, x]));
ok(Object.keys(nb25).join() === "CAR,CENT,MIDA,MIDW,SE" && nb25.CAR.name === "Carolinas", "Tennessee's neighbours in the contract's order");
ok(near(nb25.CAR.own.mwh, own("TEN", "CAR", Y25)) && near(nb25.CAR.own.mwh, -109980) && nb25.CAR.own.held === 12 && nb25.CAR.own.of === 12 && near(nb25.CAR.their.mwh, -109980 - 600) && near(nb25.CAR.gap.mwh, 600), "a year with a neighbour: the own report, the neighbour's and the gap, each the sum of the year's months");
ok(near(nb25.CAR.pct, (600 / ((109980 + 110580) / 2)) * 100) && nb25.CAR.large === false && nb25.CAR.compared === 12, "the gap as a percent of the mean size of the two reports; under 10 percent is not large");
ok(near(nb25.SE.own.mwh, -13980) && near(nb25.SE.their.mwh, -11184) && near(nb25.SE.gap.mwh, -2796) && near(nb25.SE.pct, (2796 / 12582) * 100) && nb25.SE.large === true, "Tennessee and the Southeast: the two reports stand 22.2 percent apart, which is large");
ok(T.LARGE_GAP_PCT === 10 && T.isLarge(10) && !T.isLarge(9.99) && !T.isLarge(null) && T.isLarge(6, 5) && T.gapPct(5, 0, 0) === null && T.gapPct(null, 1, 1) === null && near(T.gapPct(-10, 100, -100), 10), "large is 10 percent or more; no percent without both reports and the gap, or when both reports are zero");
ok(near(nb25.CAR.hoursOwn.mwh, 6 * 744 + 6 * 720) && near(nb25.CAR.hoursBoth.mwh, 12 * 720), "the hours each side held, summed");
const total25 = T.totalOfYear(ten, "2025");
ok(near(total25.mwh, sum(NEIGHBOURS.TEN.map((x) => own("TEN", x, Y25)))) && near(total25.mwh, -357900) && total25.held === 12, "the year from all neighbours is the sum of the file's own monthly totals");
const car18 = Object.fromEntries(T.neighboursOfYear(car, "2018").map((x) => [x.code, x]));
ok(car18.SE.own.held === 3 && car18.SE.own.of === 6 && near(car18.SE.own.mwh, own("CAR", "SE", [3, 4, 5])) && T.totalOfYear(car, "2018").held === 3 && near(T.totalOfYear(car, "2018").mwh, sum(NEIGHBOURS.CAR.map((x) => own("CAR", x, [3, 4, 5])))),
  "a month that is not held is left out of the sum and counted, never filled");
const ten26 = Object.fromEntries(T.neighboursOfYear(ten, "2026").map((x) => [x.code, x]));
ok(ten26.MIDW.own.held === 10 && ten26.MIDW.their.held === 9 && ten26.MIDW.gap.held === 9 && ten26.MIDW.compared === 9 && near(ten26.MIDW.pct, (450 / ((Math.abs(own("TEN", "MIDW", [91, 92, 93, 94, 95, 96, 97, 98, 99])) * 2 + 450) / 2)) * 100),
  "the percent runs over the months that hold both reports and the gap");
ok(T.neighboursOfYear(ten, "2017").every((x) => x.own === null && x.pct === null) && T.totalOfYear(ten, "2017") === null, "a year the file does not hold has no figure");
const c90 = T.monthCell(ten.neighbors.MIDW, 90), c78 = T.monthCell(ten.neighbors.SE, 78);
ok(c90.own === ownOf("TEN", "MIDW", 90) && c90.their === null && c90.gap === null && c90.pct === null && !c90.large && c78.large && near(c78.own, -1220) && near(c78.their, -976) && c78.hoursOwn === 744 && c78.hoursBoth === 720, "one month of one neighbour, as the file holds it");
const pts = T.monthPoints(car.neighbors.SE.net_imports_mwh, car.months);
ok(pts.length === 97 && pts[0].t === Date.UTC(2018, 9, 1) / 1000 && near(pts[0].v, ownOf("CAR", "SE", 3) / 1000) && T.monthPoints(undefined, car.months).length === 0, "the chart's points: one a held month, in GWh; a month not held has no point");

const matrix = matrixFixture();
const pairs = T.pairsOfYear(matrix.region_pairs, "2025");
const pair = Object.fromEntries(pairs.map((p) => [p.key, p]));
ok(pairs.map((p) => p.key).join() === "CAL-NW,CAL-MEX,CAR-SE,CAR-TEN,CENT-TEX,FLA-SE,MIDA-NY,NW-SW,SE-TEN,CAN-NW", "the pairs of a year in the contract's order of codes, none ranked against another");
const k = (key) => REGION_PAIRS.findIndex((p) => p.join("-") === key) + 1;
const raw = (key, y = 2025) => pairOf(key.split("-"), k(key), y);
ok(pair["CAR-SE"].from === "CAR" && pair["CAR-SE"].to === "SE" && near(pair["CAR-SE"].fromReport, 1_002_000) && near(pair["CAR-SE"].toReport, 981_960) && near(pair["CAR-SE"].mean, 991_980) && near(pair["CAR-SE"].gap, 20_040) && near(pair["CAR-SE"].pct, (20_040 / 991_980) * 100) && !pair["CAR-SE"].large,
  "a pair whose flow ran from the first to the second: each side's report, their mean and the gap as the file gives them");
ok(pair["CAR-TEN"].from === "TEN" && pair["CAR-TEN"].to === "CAR" && near(pair["CAR-TEN"].fromReport, -raw("CAR-TEN").b_report_mwh) && near(pair["CAR-TEN"].fromReport, 1_961_960) && near(pair["CAR-TEN"].toReport, 2_002_000) && near(pair["CAR-TEN"].mean, 1_981_980) && near(pair["CAR-TEN"].gap, raw("CAR-TEN").gap_mwh)
  && near(pair["CAR-TEN"].gap, pair["CAR-TEN"].fromReport - pair["CAR-TEN"].toReport), "a pair whose flow ran from the second to the first is turned to its own direction; the gap is still the sender's report less the receiver's");
ok(pair["SE-TEN"].large && near(pair["SE-TEN"].pct, (1_501_000 / 2_251_500) * 100), "a pair whose two reports stand 66.7 percent apart is large");
ok(pair["FLA-SE"].from === null && pair["FLA-SE"].mean === 0 && pair["FLA-SE"].pct === null && pair["NW-SW"].from === null && pair["NW-SW"].mean === null && pair["NW-SW"].toReport === null && pair["NW-SW"].gap === null && near(pair["NW-SW"].fromReport, raw("NW-SW").a_report_mwh),
  "a pair at zero names no direction; a pair one side of which is not held has no mean, no gap and no direction");
ok(T.pairsOfYear(matrix.region_pairs, "2019").length === 0 && T.pairsOfYear(undefined, "2025").length === 0 && T.pairsOfYear([{ a: "CAR", b: "SE", year: 2025, a_report_mwh: -4, b_report_mwh: -6, mean_mwh: -5, gap_mwh: 2 }], "2025")[0].from === "SE", "a year the file does not hold has no pair; with no direction named, the sign of the mean says it");
const partners = T.partnersOfYear(matrix, "2025");
ok(partners.map((p) => p.ba).join() === "BPAT,DUK,TVA" && partners[2].byGross.join() === PARTNERS.TVA.by_gross.join() && partners[2].byNet.join() === PARTNERS.TVA.by_net.join() && near(partners[2].sharePct, 9.5) && T.partnersOfYear(matrix, "2019").length === 0 && T.partnersOfYear(null, "2025").length === 0, "each authority's partners in a year, as the file lists them");

const tenMix = mixFixture("TEN"), carMix = mixFixture("CAR"), flaMix = mixFixture("FLA");
const mm = T.mixMonths(tenMix, "2025");
const net = (code, m, keys = SOURCE_KEYS) => sum(keys.map((s) => energyOf(code, SOURCE_KEYS.indexOf(s) + 1, m)));
ok(mm.length === 12 && mm[0].month === "2025-01" && near(mm[0].net, net("TEN", 78)) && near(mm[0].net, 352_260) && near(mm[0].mwh.natural_gas, 12_780) && near(mm[0].share.natural_gas, Math.round((12_780 / 352_260) * 10000) / 100) && mm[0].mwh.storage === -1200 && mm[1].daysHeld === 26 && mm[1].daysInMonth === 28,
  "a year's months of a mix file: each source's share as the file writes it, its energy, the net generation and the days");
const my = T.mixYear(mm);
ok(near(my.share.natural_gas, (sum(Y25.map((m) => energyOf("TEN", 1, m))) / sum(Y25.map((m) => net("TEN", m)))) * 100) && near(my.share.natural_gas, (154_020 / 4_231_740) * 100) && my.months.natural_gas === 12 && near(my.net.mwh, 4_231_740) && near(sum(SOURCE_KEYS.map((s) => my.share[s])), 100),
  "a year's share by source: the year's energy over the year's net generation, and the shares add up to 100");
ok(T.mixMonths(carMix, "2025").length === 11 && T.mixYear(T.mixMonths(carMix, "2025")).months.coal === 11 && T.mixMonths(flaMix, "2025")[0].share.coal === null && T.mixYear(T.mixMonths(flaMix, "2025")).share.coal === null && T.mixMonths(mixFixture("SW"), "2018").length === 0,
  "a month or a source the file lacks has no figure and is not in the year");
ok(T.sharePoints(tenMix, "wind").length === 100 && T.sharePoints(mixFixture("SW"), "wind").length === 94 && T.sharePoints(flaMix, "coal").length === 0 && T.sharePoints(tenMix, "wind")[0].t === Date.UTC(2018, 6, 1) / 1000, "the mix chart's points: one a month the file holds");
ok(T.defaultYear(["2023", "2024", "2025", "2026"], "2026-11-19T12:00:00Z") === "2025" && T.defaultYear(["2026"], "2026-11-19T12:00:00Z") === "2026" && T.defaultYear(["2022", "2023"], "2026-11-19T12:00:00Z") === "2023" && T.defaultYear(["2024", "2025"]) === "2025" && T.defaultYear([]) === null,
  "the year drawn first: the last calendar year that had ended when the files were built, when they hold it");
ok(T.yearOf("2024", ["2024", "2025"]) === "2024" && T.yearOf("1999", ["2024"]) === null && T.yearOf(undefined, ["2024"]) === null && T.monthWords("2025-08") === "Aug 2025" && T.pct1(22.22) === "22.2", "a year from the address when the files hold it; a month in words");

// ---- the section drawn from the fixtures: Tennessee and the Carolinas, 2025
const html = draw({ q: { region: "ten", b: "car" } });
const text = pageText(html);
const f = figs(html);
ok(html.startsWith('<section data-whole-country="supply" id="whole-country"') && html.endsWith('<span data-whole-country-end="1"></span>') && withoutSupplyAdded(html) === "" && supplyAdded(`<p>x</p>${html}<p>y</p>`) === html, "the section stands between its two marks, and the pin's cut removes it whole");
ok(/<h2[^>]*>The whole country<\/h2>/.test(html) && html.includes('data-wc-state="drawn"') && html.includes('data-wc-a="TEN"') && html.includes('data-wc-b="CAR"') && html.includes('data-wc-year="2025"'), "its title is The whole country; the year drawn first is 2025");
ok(["wc-trade", "wc-pairs", "wc-mix"].every((id) => html.includes(`id="${id}"`)) && /Net imports by month and by neighbour/.test(text) && /Who trades with whom, 2025/.test(text) && /Generation mix by month/.test(text), "its three views: net imports, who trades with whom, the generation mix");
ok(html.includes('data-wc-trade="a" data-wc-region="TEN"') && html.includes('data-wc-trade="b" data-wc-region="CAR"') && html.includes('data-wc-mix="a" data-wc-region="TEN"') && html.includes('data-wc-mix="b" data-wc-region="CAR"') && (html.match(/lg:grid-cols-2/g) ?? []).length === 2, "two regions side by side, A and B, in the trade view and in the mix view");
ok(f["trade|TEN|2025|CAR|own"] === "-110.0" && f["trade|TEN|2025|CAR|their"] === "-110.6" && f["trade|TEN|2025|CAR|gap"] === "+0.6" && f["trade|TEN|2025|CAR|gap_pct"] === "0.5" && f["trade|TEN|2025|CAR|months"] === "12", "Tennessee with the Carolinas in 2025: its own report, the neighbour's report beside it, the gap and its percent");
ok(f["trade|TEN|2025|SE|own"] === F.signedGwh(-13980) && f["trade|TEN|2025|SE|their"] === F.signedGwh(-11184) && f["trade|TEN|2025|SE|gap"] === "-2.8" && f["trade|TEN|2025|SE|gap_pct"] === "22.2" && f["trade|TEN|2025|all"] === "-357.9" && f["trade|TEN|2025|all|months"] === "12", "Tennessee with the Southeast, and with all its neighbours");
const seRow = rowOf(html, 'data-cn="trade\\|TEN\\|2025\\|SE\\|gap_pct"');
ok(/data-gap-large="1"/.test(seRow) && /title="Tennessee reported -14\.0 GWh of net imports from Southeast in 2025; Southeast reported the same flow as -11\.2 GWh\. Over the hours both reported, the gap is -2\.8 GWh, 22\.2 percent of the mean size of the two reports over the 12 months that hold both\. That is large by this page&#x27;s rule: 10 percent or more\. Default: 10 percent, this page&#x27;s own choice \(session 8430\); no publisher&#x27;s threshold stands behind it\. Source: EIA Form EIA-930/.test(seRow),
  "a large gap is marked and said plainly on hover, with the rule, its default and its source");
ok(!/data-gap-large/.test(rowOf(html, 'data-cn="trade\\|TEN\\|2025\\|CAR\\|gap_pct"')) && /A gap of 10 percent or more of the mean size of the two reports is marked as large\. Default: 10 percent, this page&#x27;s own choice \(session 8430\)/.test(rowOf(html, 'data-cn="trade\\|TEN\\|2025\\|CAR\\|gap_pct"')), "a gap that is not large carries no mark; its hover still gives the rule");
ok(f["trade|TEN|2025-01|SE"] === F.signedGwh(-1220) && f["trade|TEN|2025-01|all"] === F.signedGwh(sum(NEIGHBOURS.TEN.map((x) => ownOf("TEN", x, 78)))) && (html.match(/data-wc-month="2025-\d\d"/g) ?? []).length === 12 + 12 + 12 + 11, "the year month by month: all neighbours and each neighbour, by the own report");
const janSe = (/<span[^>]*data-gap-large="1"[^>]*><span data-cn="trade\|TEN\|2025-01\|SE">/.exec(html) ?? [""])[0];
ok(/Southeast reported the same flow as -1\.0 GWh \(720 hours\)\. Over the 720 hours both reported, the gap is -0\.2 GWh, 22\.2 percent/.test(janSe) && /Tennessee reported -1\.2 GWh of net imports from Southeast in Jan 2025 \(744 hours\)/.test(janSe), "a month's hover gives the neighbour's report, the gap and the hours each side held");
ok((html.match(/data-gap-large="1"/g) ?? []).length === 1 + 12 + 1, "the marks of a large gap: Tennessee and the Southeast's year, its twelve months, and the pair of the two in the matrix");
ok(NEIGHBOURS.TEN.every((x) => html.includes(`data-wc-nb="${x}"`)) && html.includes('data-wc-nb="all"') && /data-wc-nb="SE"[^>]*data-wc-new="1"/.test(html) && /data-wc-nb="CAR"[^>]*data-wc-new="1"/.test(html) && !/data-wc-nb="MIDA"[^>]*data-wc-new/.test(html), "each neighbour has its row, by name; a region new to the site carries its mark");
const charts = [...html.matchAll(/<svg[^>]*role="img" aria-label="([^"]*)"/g)].map((m) => m[1]);
ok(charts.length === 4 && /^Tennessee: net imports by month from Jul 2018, all neighbours and each neighbour, GWh/.test(charts[0]) && /^Carolinas: net imports by month/.test(charts[1]) && /^Tennessee: each source&#x27;s share of net generation by month, Jul 2018 to Oct 2026, percent/.test(charts[2]) && (html.match(/data-chart-table="1"/g) ?? []).length === 4,
  "four charts that answer the mouse, each with its table: net imports and the mix for A and for B");

ok(f["pair|CAR-SE|2025|from_report"] === "1,002.0" && f["pair|CAR-SE|2025|to_report"] === "982.0" && f["pair|CAR-SE|2025|mean"] === "992.0" && f["pair|CAR-SE|2025|gap"] === "+20.0" && f["pair|CAR-SE|2025|gap_pct"] === "2.0", "a pair of regions: each side's report, their mean, the gap and its percent");
const line = (key) => rowOf(html, `data-wc-pair="${key}"`).replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");
ok(/Carolinas Southeast 1,002\.0 982\.0 992\.0 \+20\.0 2\.0/.test(line("CAR-SE")) && /Tennessee Carolinas 1,962\.0 2,002\.0 1,982\.0 -40\.0 2\.0/.test(line("CAR-TEN")) && /Mexico California 5,882\.0 6,002\.0/.test(line("CAL-MEX")) && /Canada Northwest 7,002\.0/.test(line("CAN-NW")),
  "pair by pair: which sent and which received, Canada and Mexico among them");
ok(/Florida and Southeast no net flow 0\.0 0\.0 0\.0 0\.0 not held yet/.test(line("FLA-SE")) && /Northwest and Southwest not held yet -10,002\.0 not held yet not held yet not held yet not held yet/.test(line("NW-SW")), "a pair at zero reads no net flow; what the file does not hold reads not held yet");
ok(/data-gap-large="1"/.test(rowOf(html, 'data-wc-pair="SE-TEN"')) && /Southeast reported 3,002\.0 GWh sent to Tennessee in 2025; Tennessee reported the same flow as 1,501\.0 GWh\. The gap is \+1,501\.0 GWh, 66\.7 percent of the mean size of the two reports\. That is large by this page&#x27;s rule/.test(rowOf(html, 'data-wc-pair="SE-TEN"')),
  "a pair with a large gap says so plainly on hover");
ok((html.match(/data-wc-kind="pair"/g) ?? []).length === REGION_PAIRS.length && (html.match(/data-wc-kind="bapair"/g) ?? []).length === BA_PAIRS.length && f["bapairs|2025|n"] === "4" && f["partners|2025|n"] === "3" && (html.match(/<details /g) ?? []).length === 2, "every pair of regions of the year, and in two folds the pairs of balancing authorities and each authority's partners");
ok(f["bapair|DUK-TVA|2025|from_report"] === F.gwh(11_002_000) && /title="Duke Energy Carolinas, balancing authority DUK, in EIA&#x27;s region Carolinas\."/.test(html) && /DUK TVA 11,002\.0 10,782\.0 10,892\.0 \+220\.0 2\.0/.test(line("DUK-TVA")) && /TVA SOCO 11,762\.0 12,002\.0 11,882\.0 -240\.0 2\.0/.test(line("SOCO-TVA")),"a pair of balancing authorities, turned to its own direction, each code with its name on hover");
const tva = rowOf(html, 'data-wc-partners="TVA"').replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");
ok(/TVA SOCO, MISO, PJM, DUK MISO, SOCO, PJM, DUK/.test(tva) && /title="Southern Company Services; Midcontinent Independent System Operator; PJM Interconnection; Duke Energy Carolinas"/.test(html), "an authority's partners by gross and by net exchange, in the file's order, their names on hover");
ok(!Object.keys(f).some((x) => x.endsWith("|share")) && !/percent of demand/.test(seen(html)) && /that share is not drawn in this section until the owner rules/.test(html), "the share of demand the file holds is not drawn; the hover says so");
S.SHOWN.importShare = true;
const withShare = draw({ q: { region: "ten", b: "car" } });
S.SHOWN.importShare = false;
ok(figs(withShare)["partners|TVA|2025|share"] === "9.5" && figs(withShare)["partners|BPAT|2025|share"] === "-10.0" && /Net imports, percent of demand/.test(seen(withShare)), "the switch draws it, for the owner's ruling");
ok(CODES.filter((c) => REGION_PAIRS.flat().includes(c)).every((c) => html.includes(`href="/supply?region=${c.toLowerCase()}&amp;b=`)) && html.includes('href="/supply?region=se&amp;b=car&amp;year=2025#whole-country"') && !/href="\/supply\?region=(can|mex)/.test(html), "a region's name in a pair chooses it as Region A and keeps Region B and the year");
ok((rowOf(html, 'data-wc-pair="CAR-TEN"').match(/bg-paper font-semibold/g) ?? []).length === 1 && !/bg-paper font-semibold/.test(rowOf(html, 'data-wc-pair="CAL-NW"')) && /bg-paper font-semibold/.test(rowOf(html, 'data-wc-pair="DUK-TVA"')) && !/bg-paper font-semibold/.test(rowOf(html, 'data-wc-pair="BPAT-CISO"')), "the rows of the two chosen regions, and of their balancing authorities, are lit");

ok(f["mix|TEN|2025-01|natural_gas"] === "3.6" && f["mix|TEN|2025-01|net"] === F.gwh(352_260) && f["mix|TEN|2025|natural_gas"] === "3.6" && f["mix|TEN|2025|net"] === F.gwh(4_231_740) && f["mix|TEN|2025-01|storage"] === "-0.3" && /26 of 28/.test(rowOf(html.slice(html.indexOf('data-wc-mix="a"'), html.indexOf('data-wc-mix="b"')), 'data-wc-month="2025-02"')) && /31 of 31/.test(rowOf(html.slice(html.indexOf('data-wc-mix="a"')), 'data-wc-month="2025-01"')),"the mix: each source's share by month, the net generation, the days held, and the year's row");
ok(/Natural gas in Tennessee, Jan 2025: 12\.8 GWh of 352\.3 GWh of net generation\./.test(html) && /2025, 11 months/.test(seen(html)) && /2025, 12 months/.test(seen(html)) && !("mix|CAR|2025-06|coal" in f) && "mix|CAR|2025-07|coal" in f, "a share's hover gives the energy; the Carolinas' year says it holds 11 months");
const heads = [...html.matchAll(/<span title="([^"]*)" data-wc-head="([^"]+)"/g)];
ok(heads.length === 5 + (1 + 5) + 5 + (1 + 3) + 7 + 7 + 2 + 10 + 10 && heads.every((m) => m[1].length > 30), "every column head carries its hover");
ok(/data-wc-source="1"[\s\S]*EIA Form EIA-930 \(public domain\)[\s\S]*eia930_region_pair_hourly[\s\S]*interchange_pair_monthly[\s\S]*files built 2026-11-19/.test(html) && html.includes('href="/data/methods/regions_trade"'), "the source line names EIA's form, the tables, the build day and the method");
ok((html.match(/<option /g) ?? []).length === 13 + 14 + 9 && html.includes('action="/supply#whole-country"') && ["region", "b", "year"].every((x) => html.includes(`name="${x}"`)) && /Region A is California and Region B is Carolinas: the first two of EIA&#x27;s thirteen regions in EIA&#x27;s own order of codes\. The year is 2025: the last calendar year that had ended when the files were built/.test(html),
  "the choice: Region A, Region B (with None) and the year, in a form that needs no script; the defaults and their source on hover");
ok(text.includes("Southeast, Florida, Carolinas, Tennessee, Northwest, Southwest: none of the seven grids") && F.NEW_REGIONS.every((c) => new RegExp(`<option value="${c.toLowerCase()}"[^>]*>${F.REGION_NAME[c]}</option>`).test(html)), "the six regions new to the site are named, and each can be chosen");

// ---- the address
const first = draw();
ok(first.includes('data-wc-a="CAL"') && first.includes('data-wc-b="CAR"') && first.includes('data-wc-year="2025"') && S.FIRST_A === "CAL" && S.FIRST_B === "CAR", "with nothing chosen: California and the Carolinas, 2025");
const one = draw({ q: { region: "tex", b: "none", year: "2023" } });
ok(one.includes('data-wc-a="TEX"') && one.includes('data-wc-b=""') && !one.includes('data-wc-trade="b"') && !one.includes('data-wc-mix="b"') && !/lg:grid-cols-2/.test(one) && one.includes('data-wc-year="2023"') && figs(one)["pair|CAR-SE|2023|from_report"] === "1,000.0" && /Mexico/.test(rowOf(one, 'data-wc-nb="MEX"')), "a region, None and a year from the address: one region, that year, Mexico among Texas's neighbours");
ok(draw({ q: { region: "car", b: "car" } }).includes('data-wc-b=""') && draw({ q: { region: "pjm", b: "xx", year: "1999" } }).includes('data-wc-a="CAL"') && draw({ q: { region: "pjm", b: "xx", year: "1999" } }).includes('data-wc-year="2025"'), "the same region twice draws it once; what is none of the thirteen, or a year not held, falls back");
const y18 = draw({ q: { region: "car", b: "sw", year: "2018" } });
ok(figs(y18)["trade|CAR|2018|SE|months"] === "3" && /3<\/span> of 6/.test(rowOf(y18, 'data-cn="trade\\|CAR\\|2018\\|all\\|months"')) && /data-not-held="1"/.test(rowOf(y18, 'data-wc-month="2018-07"')) && /The file leaves Jul 2018 out of Carolinas&#x27; total/.test(y18) && /The file holds no month of 2018 for Southwest: its months run from Jan 2019 to Oct 2026/.test(y18) && /The file holds no pair of regions for 2018/.test(y18),
  "a year held in part: the months held are counted, the rest read not held yet with why on hover");
const kept = draw({ q: { region: "ten" }, keep: { g: "burn,cleared", s: "eia-wcestus1" } });
ok(kept.includes('<input type="hidden" name="g" value="burn,cleared"/>') && kept.includes('<input type="hidden" name="s" value="eia-wcestus1"/>') && kept.includes('href="/supply?g=burn%2Ccleared&amp;s=eia-wcestus1&amp;region=se&amp;b=car&amp;year=2025#whole-country"') && !html.includes('type="hidden"'), "the page's own choices (its groups and its open chart) are carried by the form and the links");

// ---- held, and not built
const heldHtml = draw({ q: { region: "ten", b: "car" }, read: fixtureReaders({ license: "internal" }) });
ok(Object.keys(figs(heldHtml)).filter((x) => !/\|n$/.test(x)).length === 0 && !/<svg[^>]*role="img"/.test(heldHtml) && (heldHtml.match(/data-license-held="1"/g) ?? []).length > 400 && (heldHtml.match(/data-wc-chart-held=/g) ?? []).length === 4 && heldHtml.includes("license needed") && /license needed: the file&#x27;s license line reads &quot;internal&quot;/.test(heldHtml),
  "files that are not public: every cell blank with license needed on hover, no figure, no chart");
ok(NEIGHBOURS.TEN.every((x) => heldHtml.includes(`data-wc-nb="${x}"`)) && (heldHtml.match(/data-wc-kind="pair"/g) ?? []).length === REGION_PAIRS.length, "held files still draw their rows: a held value is not left off");
ok(S.heldWhy(tradeFixture("TEN")) === null && S.heldWhy(null) === null && /license needed/.test(S.heldWhy(tradeFixture("TEN", { license: "internal" }))) && /license needed: /.test(S.heldWhy(tradeFixture("TEN", { tables: ["event_window_daily"] })) ?? ""), "held when the license line is not public or a table it names is license needed in the status file");
S.REGIONS_HELD.push("SE");
const seHeld = draw({ q: { region: "ten", b: "se" } });
S.REGIONS_HELD.pop();
const fs2 = figs(seHeld);
ok(!Object.keys(fs2).some((x) => /^trade\|TEN\|[^|]+\|SE/.test(x) || /^trade\|SE\|/.test(x) || /^mix\|SE\|/.test(x) || /^pair\|(CAR-SE|SE-TEN|FLA-SE)\|/.test(x)) && fs2["trade|TEN|2025|CAR|own"] === "-110.0" && fs2["pair|CAR-TEN|2025|mean"] === "1,982.0" && fs2["bapair|DUK-TVA|2025|mean"] !== undefined && !("bapair|SOCO-TVA|2025|mean" in fs2),
  "a region put on hold is drawn blank wherever it stands (its own views, a neighbour's row, its pairs, its authorities), and the others stand");
const none = draw({ read: { trade: () => null, mix: () => null, matrix: () => null, index: () => null } });
ok(none.includes('data-wc-state="not-built"') && none.includes("not built yet") && Object.keys(figs(none)).length === 0 && /Southeast[\s\S]*Tennessee/.test(none) && none.includes("site/data/regions/trade/") && !none.includes("<form") && withoutSupplyAdded(none) === "",
  "with no file the section says not built yet, names the regions on hover and draws no figure");
const part = draw({ q: { region: "fla", b: "ten" }, read: fixtureReaders({ without: ["trade/fla", "mix/ten", "matrix", "index"] }) });
ok(part.includes('data-wc-not-built="trade/fla.json"') && part.includes('data-wc-not-built="mix/ten.json"') && part.includes('data-wc-not-built="trade_matrix.json"') && "trade|TEN|2025|all" in figs(part) && "mix|FLA|2025|net" in figs(part) && !Object.keys(figs(part)).some((x) => /^(trade\|FLA|mix\|TEN|pair|bapair)/.test(x)) && (part.match(/not built yet/g) ?? []).length === 3,
  "a file that is missing says not built yet in its own view; the views whose files are there are drawn");
const noIndex = draw({ q: { region: "ten", b: "car" }, read: fixtureReaders({ without: ["index"] }) });
ok(/Balancing authority TVA, by its EIA-930 code\. Its name stands here once the index/.test(noIndex) && figs(noIndex)["bapair|DUK-TVA|2025|mean"] !== undefined && !/bg-paper font-semibold/.test(rowOf(noIndex, 'data-wc-pair="DUK-TVA"')), "without the index file the authorities stand by their codes, and their figures still stand");
const otherOnly = draw({ q: { region: "fla", b: "none" }, read: fixtureReaders({ without: ["trade/fla", "mix/fla", "matrix"] }) });
ok(otherOnly.includes('data-wc-state="drawn"') && (otherOnly.match(/not built yet/g) ?? []).length === 3, "a chosen region with no file, while other regions have theirs: each view says not built yet");
const noMonths = draw({ q: { region: "ten", b: "none" }, read: { ...fixtureReaders(), trade: () => ({ code: "TEN", neighbors: {} }) } });
ok(noMonths.includes('data-wc-not-built="trade/ten.json"') && !Object.keys(figs(noMonths)).some((x) => x.startsWith("trade|")) && "mix|TEN|2025|net" in figs(noMonths), "a trade file with no list of months is not in the contract's form: its view says not built yet");

// ---- the rules of the page, on everything drawn above
for (const [name, h] of [["two regions", html], ["one region", one], ["a year held in part", y18], ["held", heldHtml], ["a region on hold", seHeld], ["in part", part], ["not built", none]]) {
  const t = seen(h);
  ok(!dash.some((c) => h.includes(c)) && !/\b(should|recommend|we advise)\b/i.test(pageText(h)) && !/NaN|\bundefined\b|Infinity/.test(t) && !/NaN|undefined|Infinity/.test(h.replace(/<svg[\s\S]*?<\/svg>/g, "")),
    `${name}: no dash, no advice, no NaN or undefined`);
  ok(!/\b(methodology|limitations?|disputed)\b|\bnot held\b(?! yet)|against expectations|consensus/i.test(t), `${name}: the page's own check of its face holds (a value that is not held reads "not held yet", no method prose)`);
  ok(!/donor|taker|giver|ledger|share of the (shock|shortfall)|covered by imports|rank/i.test(pageText(h)), `${name}: no ledger of regions that gave and took, no ranking, no share covered by imports`);
}
ok(!/min-w-\[|w-\[\d{3,}px\]/.test(html) && (html.match(/class="overflow-x-auto" tabindex="0"/g) ?? []).length === 2 + 2 + 1 + 1 + 1 + 2, "the nine tables scroll inside their own frames (no sideways scroll of the page at 390 px)");
ok(!/ data-n="[^"]*\|/.test(html) && figureCount(html) === 4 && !/ data-row="/.test(html) && !/ data-group="/.test(html) && !/ data-(surprise|release|band|chip|open)=/.test(html),
  "the section writes none of the page's own marks (a keyed data-n, data-row, data-group), so the page's checks read what they read; its four charts carry the chart's own count of points");

// ---- the reader: a fixture is never read from the site's own folder
ok(process.env.ERW_REGIONS_DIR === undefined, "ERW_REGIONS_DIR is not set as the test starts");
const inSite = (rel) => { const u = here(`../data/regions/${rel}`); return fs.existsSync(u) && "fixture" in JSON.parse(fs.readFileSync(u, "utf-8")); };
ok(!inSite("trade_matrix.json") && !inSite("trade/ten.json") && !inSite("mix/ten.json"), "no fixture stands in the site's own folder");
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "erw-regions-supply-"));
const put = (dir, rel, v) => { const at = path.join(dir, ...rel.split("/")); fs.mkdirSync(path.dirname(at), { recursive: true }); fs.writeFileSync(at, typeof v === "string" ? v : JSON.stringify(v)); };
for (const c of CODES) { put(tmp, `trade/${c.toLowerCase()}.json`, tradeFixture(c)); put(tmp, `mix/${c.toLowerCase()}.json`, mixFixture(c)); }
put(tmp, "trade_matrix.json", matrixFixture());
put(tmp, "index.json", indexFixture());
put(tmp, "mix/nw.json", "{ not json");
const cwd = process.cwd();
try {
  process.chdir(tmp);  // a folder whose data/regions holds a fixture, read as the site reads its own
  put(tmp, "data/regions/trade/ten.json", tradeFixture("TEN"));
  put(tmp, "data/regions/trade_matrix.json", matrixFixture());
  ok(T.tradeFile("TEN") === null && T.matrixFile() === null, "a fixture in the site's own folder is refused");
} finally { process.chdir(cwd); }

// ---- the whole page: with no file (the site until the files land), then with the fixtures in a folder of their own
const undoClock = fixClock("2026-11-19T12:00:00Z");
const undoRead = standInCatalogue(true);
const log = console.error;
console.error = () => {};
try {
  const { drawSupply } = await import("./supply-read-page.mjs");
  const hasFiles = fs.existsSync(here("../data/regions/trade_matrix.json")) || fs.existsSync(here("../data/regions/trade"));
  const page = await drawSupply("");
  const at = page.indexOf('<section data-whole-country="supply"'), lastGroup = page.lastIndexOf('data-group="'), dec = page.indexOf('data-decisions='), down = page.indexOf("data-downloads=");
  ok(at > 0 && (page.match(/data-whole-country="/g) ?? []).length === 1 && (page.match(/data-whole-country-end="1"/g) ?? []).length === 1 && lastGroup < at && at < dec && dec < down, "the page: the section is on it once, under the last of its tables and above the decisions block and the downloads");
  if (!hasFiles) ok(/data-wc-state="not-built"/.test(supplyAdded(page)) && Object.keys(figs(page)).length === 0, "the page with no file on the site: not built yet and no figure");
  const base = withoutSupplyAdded(page);
  const burn = withoutSupplyAdded(await drawSupply("g=burn"));
  const chosen = await drawSupply("region=ten&b=car&year=2024");
  ok(withoutSupplyAdded(chosen) === base && withoutSupplyAdded(await drawSupply("g=burn&region=se&b=none&year=2019")) === burn, "a choice of region and year in the address moves nothing outside the section");
  process.env.ERW_REGIONS_DIR = tmp;
  const drawn = await drawSupply("region=ten&b=car");
  const df = figs(drawn);
  ok(withoutSupplyAdded(drawn) === base && figureCount(withoutSupplyAdded(drawn)) === figureCount(base), "the page with the files: outside the section it is, byte for byte, the page with none");
  ok(/data-wc-state="drawn"/.test(drawn) && df["trade|TEN|2025|SE|gap_pct"] === "22.2" && df["pair|SE-TEN|2025|gap_pct"] === "66.7" && df["mix|CAR|2025|net"] !== undefined && drawn.includes('data-wc-a="TEN"') && drawn.includes('data-wc-b="CAR"'), "the page reads the files of the folder and the choice of its address");
  const withG = await drawSupply("g=burn&s=eia-wcestus1&region=nw&b=sw&year=2024");
  ok(withG.includes('data-wc-a="NW"') && withG.includes('data-wc-not-built="mix/nw.json"') && "trade|NW|2024|all" in figs(withG) && supplyAdded(withG).includes('<input type="hidden" name="g" value="burn"/>') && (withG.match(/data-group="/g) ?? []).length === 1,
    "a file that cannot be read as JSON is treated as not built; the page's own choice of groups stands beside the section's");
} finally { delete process.env.ERW_REGIONS_DIR; console.error = log; undoRead(); undoClock(); fs.rmSync(tmp, { recursive: true, force: true }); }

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
