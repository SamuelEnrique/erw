// Energy Research Warehouse (ERW) site, session 10402 (chain 720, part D): energy equities, the group on the price board
// and /equities, drawn and computed with the site's own code, without a build.
//   node --import ./scripts/events-page-register.mjs scripts/test-equities.mjs [--keep <folder>]
// Three states: no equities file (a folder that does not exist); the contract's own example files at their real path
// (site/data/equities/, every value null: nothing of them is shown as real, their rows' names included); and files of
// the contract's shape written here with made-up values, each marked as a test's fixture, which the site's own folder
// never reads (lib/equitiesfiles.ts). `--keep` writes the fixture to a folder and leaves it, for a local build served
// with ERW_EQUITIES_DIR (to see the layout before the real files exist; never deployed). No network. Exit 0 when every
// check holds, 1 otherwise.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const { EquitiesView } = await import("../app/equities/view.tsx");
const E = await import("../lib/equities.ts");
const F = await import("../lib/equitiesfiles.ts");
const B = await import("../lib/board.ts");
const { csvReader } = await import("../lib/csvreader.ts");
const R = await import("../app/equities/reader.ts");
const board = JSON.parse(fs.readFileSync(path.join(SITE, "data", "board.json"), "utf8"));

const fails = [];
let n = 0;
const check = (ok, what) => { n++; if (!ok) fails.push(what); };
const folder = (dir) => { if (dir === null) delete process.env.ERW_EQUITIES_DIR; else process.env.ERW_EQUITIES_DIR = dir; };
const draw = (dir, query = {}) => { folder(dir); return renderToStaticMarkup(h(EquitiesView, { query })); };
const text = (html) => html.replace(/<title>[^<]*<\/title>/g, " ").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&amp;/g, "&").replace(/\s+/g, " ");
const dash = String.fromCharCode(0x2014);
const count = (html, re) => (html.match(re) ?? []).length;
const quiet = (html, where) => {
  const t = text(html);
  check(!/\bundefined\b|\bNaN\b|\bnull\b/.test(t), `${where}: "undefined", "NaN" or "null" on the page`);
  check(!html.includes(dash), `${where}: an em dash`);
  check(!/outperform|underperform|signal|\bbuy\b|\bsell\b|so what|overweight|undervalued/i.test(t), `${where}: a word of advice or a view`);
};

// ---- 1. No equities file ---------------------------------------------------------------------------------------------
{
  const none = path.join(os.tmpdir(), "erw-c720-no-such-equities");
  const html = draw(none);
  check(html.includes('data-eq-state="no-files"') && text(html).includes("Energy equities: not built yet"), "no files: the page is its title and one blank");
  check(!html.includes("data-check="), "no files: a checked figure is drawn");
  quiet(html, "no files");
  folder(none);
  check(B.holdRows(E.withEquities(board, F.equitiesBoard()), []).groups.length === board.groups.length, "no files: the board has its own groups and no other");
  check(E.withEquities(board, null) === board, "no equities file: the board's file is handed back as it is");
}

// ---- 2. The contract's example files, at their real path -------------------------------------------------------------
// (Once the data machine's real files replace the examples this part has nothing to read: the real files are then
// checked on a build by scripts/check-values.mjs through each figure's key, and this part says so and passes.)
folder(null);
const onSite = F.equitiesBoard();
if (!onSite || onSite.example !== true) {
  console.log("the contract's example files are no longer at site/data/equities (the data machine's files have replaced them): part 2 has nothing to read");
} else {
  const example = onSite;
  const html = draw(null);
  check(html.includes('data-eq-state="example"') && text(html).includes("Energy equities: not built yet"), "examples: the page is its title and one blank");
  check(!html.includes("data-check=") && !html.includes("data-svg-chart") && !/XOM|Example index|Integrated oil/.test(text(html)), "examples: nothing of an example file is on the page, its names included");
  check(html.includes("the contract&#x27;s examples"), "examples: the blank's hover says why");
  quiet(html, "examples");
  const merged = E.withEquities(board, example);
  check(merged.groups.length === board.groups.length + 1 && merged.groups.at(-1).id === "equities" && merged.groups.at(-1).lean === true, "examples: the group is the board's last, with the lean columns");
  check(JSON.stringify(merged.groups.slice(0, -1)) === JSON.stringify(board.groups) && JSON.stringify(merged.rows.slice(0, board.rows.length)) === JSON.stringify(board.rows) && merged.sources === board.sources, "examples: every group, row and source of the board is as it was, in its order");
  const rows = merged.rows.slice(board.rows.length);
  check(rows.length === 1 && rows[0].status === "not_held" && rows[0].label === "Segments and indices" && !rows[0].last && /contract's examples/.test(rows[0].note), "examples: one blank row that says the files are examples");
  check(!JSON.stringify(rows).includes("Example index"), "examples: an example row's name is not shown as a row of the board");
}

// ---- 3. Files of the contract's shape, with a test's made-up values --------------------------------------------------
const KEEP = process.argv.includes("--keep") ? process.argv[process.argv.indexOf("--keep") + 1] : null;
if (KEEP) fs.mkdirSync(KEEP, { recursive: true });
const FIX = KEEP ?? fs.mkdtempSync(path.join(os.tmpdir(), "erw-c720-equities-"));
fs.mkdirSync(path.join(FIX, "series"), { recursive: true });
const FIXTURE = "scripts/test-equities.mjs: made-up values, a test's fixture";
const head = { fixture: FIXTURE, built: "2026-11-26T12:00:00Z", example: false, method: "docs/methods/equities.md", contract: "docs/state/page_files_equities.md" };
// 300 trading days (weekdays) ending 25 November 2026
const days = [];
for (let t = Date.parse("2026-11-25T00:00:00Z"); days.length < 300; t -= 86_400_000) { const d = new Date(t).getUTCDay(); if (d !== 0 && d !== 6) days.unshift(new Date(t).toISOString().slice(0, 10)); }
const LAST = days.at(-1);
const round = (v, d = 2) => Number(v.toFixed(d));
const walk = (start, step, wave) => days.map((_, i) => round(start + step * i + wave * Math.sin(i / 9)));
const move = (v, i, k) => { const j = i - k; return j < 0 ? null : { t: days[j], v: v[j], ch: round(v.at(-1) - v[j]), pct: round(((v.at(-1) - v[j]) / v[j]) * 100) }; };
const movesOf = (v) => ({ d: move(v, v.length - 1, 1), w: move(v, v.length - 1, 5), m: move(v, v.length - 1, 21), ytd: (() => { const j = days.findLastIndex((x) => x < "2026-01-01"); return j < 0 ? null : { t: days[j], v: v[j], ch: round(v.at(-1) - v[j]), pct: round(((v.at(-1) - v[j]) / v[j]) * 100) }; })(), y: move(v, v.length - 1, 252) });
const QCOLS = ["period_start", "period_end", "months", "fy", "fp", "form", "filed", "revenue", "net_income", "capex", "debt", "shares_outstanding", "accession", "url"];
const quarter = (cik, k, rev, inc, capex, debt, shares, url) => [["2026-07-01", "2026-09-30", 3, 2026, "Q3", "10-Q", "2026-10-30"], ["2026-04-01", "2026-06-30", 3, 2026, "Q2", "10-Q", "2026-07-31"], ["2025-01-01", "2025-12-31", 12, 2025, "FY", "10-K", "2026-02-20"]][k]
  .concat([rev, inc, capex, debt, shares, `000${cik}-26-00000${k + 1}`, url ?? `https://www.sec.gov/Archives/edgar/data/${cik}/000${cik}2600000${k + 1}/form.htm`]);
const CONCEPTS = { revenue: "us-gaap:Revenues", net_income: "us-gaap:NetIncomeLoss", capex: "us-gaap:PaymentsToAcquirePropertyPlantAndEquipment", debt: "us-gaap:LongTermDebt", shares_outstanding: "dei:EntityCommonStockSharesOutstanding" };
const CUNITS = { close: "USD/share", adj_close: "USD/share", volume: "shares", market_value: "USD", revenue: "USD", net_income: "USD", capex: "USD", debt: "USD", shares_outstanding: "shares" };
function company(id, name, cik, exchange, segments, price, quarters, shown = true) {
  const base = { ...head, license: shown ? "public" : "internal", id, kind: "company", name, cik, ticker: id, exchange, segments, units: CUNITS, daily_columns: ["day", "close", "adj_close", "volume", "market_value"], quarterly_columns: QCOLS, quarterly: quarters, concepts: CONCEPTS };
  if (!shown) return { ...base, status: "license needed", why: "license needed: no source found whose terms allow the ERW to show daily prices (docs/reviews/equities-sources-2026-11-26.md)", source: "not shown", held: Object.fromEntries(["close", "adj_close", "volume", "market_value"].map((c) => [c, "license needed"])), daily: days.slice(-2).map((d) => [d, null, null, null, null]), last: null, moves: { d: null, w: null, m: null, ytd: null, y: null } };
  return { ...base, status: "shown", why: null, source: "A made-up exchange's daily closing prices (a test's fixture), https://example.test/prices", held: { adj_close: "the source prints no adjusted close" },
    daily: days.map((d, i) => [d, price[i], null, 1_000_000 + 1000 * i, round(price[i] * 4_000_000_000, 0)]), last: { t: LAST, v: price.at(-1) }, moves: movesOf(price) };
}
const xom = walk(100, 0.05, 3), nee = walk(70, 0.02, 2);
const eq = walk(100, 0.04, 2.5), vw = walk(100, 0.05, 3), idx = walk(600, 0.3, 12);
const files = {
  "series/XOM.json": company("XOM", "Exxon Mobil Corp", "0000034088", "NYSE", ["integrated_oil_gas"], xom, [quarter("0000034088", 0, 83_331_000_000, 7_548_000_000, 6_100_000_000, 36_600_000_000, 4_262_000_000), quarter("0000034088", 1, 81_500_000_000, 7_082_000_000, 6_300_000_000, 37_200_000_000, 4_290_000_000), quarter("0000034088", 2, 339_247_000_000, 33_680_000_000, 25_600_000_000, 36_755_000_000, 4_340_000_000, "https://example.test/not-the-sec")]),
  "series/DUK.json": company("DUK", "Duke Energy Corp", "0001326160", "NYSE", ["regulated_utilities"], null, [quarter("0001326160", 0, 8_154_000_000, 1_421_000_000, null, 85_200_000_000, 777_000_000), quarter("0001326160", 2, 30_357_000_000, 4_524_000_000, 12_280_000_000, 83_100_000_000, 772_000_000)], false),
  "series/NEE.json": company("NEE", "NextEra Energy Inc", "0000753308", "NYSE", ["regulated_utilities", "solar"], nee, [[null, null, null, null, null, null, null, null, null, null, null, null, null, null]]),
  "series/segment-integrated_oil_gas.json": { ...head, license: "public", id: "segment-integrated_oil_gas", kind: "segment", name: "Integrated oil and gas", cik: null, ticker: null, exchange: null, segments: ["integrated_oil_gas"], status: "shown", why: null,
    source: "Built by the ERW from its companies' closing prices (a test's fixture)", units: { equal_weight: "index, first day = 100", value_weight: "index, first day = 100", n: "companies", n_value: "companies" }, held: {},
    daily_columns: ["day", "equal_weight", "value_weight", "n", "n_value"], daily: days.map((d, i) => [d, eq[i], vw[i], 6, 5]), last: { t: LAST, v: eq.at(-1) }, last_value_weight: { t: LAST, v: vw.at(-1) }, moves: movesOf(eq), moves_value_weight: movesOf(vw) },
  "series/index-energy_select.json": { ...head, license: "public", id: "index-energy_select", kind: "index", name: "A made-up energy index", cik: null, ticker: null, exchange: null, segments: null, status: "shown", why: null,
    source: "A made-up index publisher (a test's fixture), https://example.test/index", units: { level: "points" }, held: {}, daily_columns: ["day", "level"], daily: days.map((d, i) => [d, idx[i]]), last: { t: LAST, v: idx.at(-1) }, moves: movesOf(idx) },
};
const SEGS = [{ id: "integrated_oil_gas", label: "Integrated oil and gas", rule: "A company whose filings report both oil and gas production and refining.", n_companies: 6 },
  { id: "regulated_utilities", label: "Regulated electric and gas utilities", rule: "A company whose SIC code is 4911, 4931 or 4924 and whose rates a state commission sets.", n_companies: 2 },
  { id: "solar", label: "Solar", rule: "A company whose main reported business is solar equipment or solar generation.", n_companies: 1 }];
const list = { ...head, license: "public", tables: ["equity_universe", "equity_prices_daily", "equity_fundamentals_quarterly", "equity_index_daily"], last_day: LAST, segments: SEGS,
  companies: [
    { id: "XOM", cik: "0000034088", name: "Exxon Mobil Corp", ticker: "XOM", exchange: "NYSE", sic: "2911", sic_label: "Petroleum refining", segments: ["integrated_oil_gas"], segments_note: null, directory_id: null, price_status: "shown", price_why: null, fundamentals_status: "shown", fundamentals_why: null, first: days[0], last: LAST, file: "series/XOM.json" },
    { id: "DUK", cik: "0001326160", name: "Duke Energy Corp", ticker: "DUK", exchange: "NYSE", sic: "4931", sic_label: "Electric and other services combined", segments: ["regulated_utilities"], segments_note: null, directory_id: null, price_status: "license needed", price_why: "license needed: no source found whose terms allow the ERW to show daily prices (docs/reviews/equities-sources-2026-11-26.md)", fundamentals_status: "shown", fundamentals_why: null, first: null, last: null, file: "series/DUK.json" },
    { id: "NEE", cik: "0000753308", name: "NextEra Energy Inc", ticker: "NEE", exchange: "NYSE", sic: "4911", sic_label: "Electric services", segments: ["regulated_utilities", "solar"], segments_note: "In two segments: its utility is rate-regulated and its other arm builds solar.", directory_id: null, price_status: "shown", price_why: null, fundamentals_status: "not filed", fundamentals_why: "no XBRL facts of these concepts are in its filings as read", first: days[0], last: LAST, file: "series/NEE.json" }],
  indices: [{ id: "energy_select", name: "A made-up energy index", publisher: "A made-up publisher", kind: "index", proxy_for: null, status: "shown", why: null, first: days[0], last: LAST, file: "series/index-energy_select.json" },
    { id: "held_index", name: "A held index", publisher: "Another publisher", kind: "proxy", proxy_for: "an index whose levels are licensed", status: "license needed", why: "license needed: the publisher's terms forbid republication", first: null, last: null, file: "series/index-held_index.json" }],
  segment_series: [{ id: "segment-integrated_oil_gas", segment: "integrated_oil_gas", file: "series/segment-integrated_oil_gas.json" }] };
const wti = walk(60, 0.03, 4);
const months = [...new Set(days.map((d) => `${d.slice(0, 7)}-01`))];
const prices = { ...head, series: [
  { id: "wti", label: "WTI crude oil, Cushing, spot", unit: "USD/bbl", freq: "D", table: "eia_fuel_spot_prices", entity: "eia:RWTC", variable: "price", source: "EIA, spot prices (a test's fixture)", license: "public", status: "shown", why: null, first: days[0], last: LAST, last_value: { t: LAST, v: wti.at(-1) }, moves: movesOf(wti) },
  { id: "henry_hub_month", label: "Henry Hub natural gas, monthly", unit: "USD/MMBtu", freq: "M", table: "eia_gas_prices_state_monthly", entity: "eia:RNGWHHD", variable: "price", source: "EIA (a test's fixture)", license: "public", status: "shown", why: null, first: months[0], last: months.at(-1), last_value: { t: months.at(-1), v: 3.1 }, moves: { d: null, w: null, m: null, ytd: null, y: null } },
  { id: "pjm_west", label: "PJM Western Hub, day-ahead", unit: "USD/MWh", freq: "D", table: "iso_hub_prices_history", entity: "pjm:WESTERN_HUB", variable: "da_price", source: "PJM", license: "internal", status: "license needed", why: "license needed: PJM publishes its prices under a license the ERW does not hold (docs/licenses.md)", first: null, last: null, last_value: null, moves: { d: null, w: null, m: null, ytd: null, y: null } }],
  daily: { wti: days.map((d, i) => [d, wti[i]]), henry_hub_month: months.map((d, i) => [d, round(2.5 + 0.05 * i)]) } };
const sparkOf = (v) => ({ t0: days.at(-90), d: days.slice(-90).map((d) => Math.round((Date.parse(d) - Date.parse(days.at(-90))) / 86_400_000)), v: v.slice(-90) });
const boardFile = { ...head, group: { id: "equities", title: "Energy equities", filters: [{ key: "kind", label: "Show", options: [["all", "Segments and indices"], ["segment", "Segments"], ["index", "Indices"]], default: "all" }] },
  sources: ["Built by the ERW from its companies' closing prices (a test's fixture)", "A made-up index publisher (a test's fixture)"],
  rows: [
    { id: "equities-segment-integrated_oil_gas-equal", group: "equities", label: "Integrated oil and gas (equal weight)", unit: "index, first day = 100", freq: "D", tags: { kind: "segment", weighting: "equal" }, source: 0, status: "ok", basis: "the mean of the companies' daily returns, chained", last: { t: LAST, v: eq.at(-1) }, moves: movesOf(eq), spark: sparkOf(eq), file: "series/segment-integrated_oil_gas.json" },
    { id: "equities-segment-integrated_oil_gas-value", group: "equities", label: "Integrated oil and gas (weighted by market value)", unit: "index, first day = 100", freq: "D", tags: { kind: "segment", weighting: "value" }, source: 0, status: "ok", basis: "the same, weighted by the day before's market value", last: { t: LAST, v: vw.at(-1) }, moves: movesOf(vw), spark: sparkOf(vw), file: "series/segment-integrated_oil_gas.json" },
    { id: "equities-index-energy_select", group: "equities", label: "A made-up energy index", unit: "points", freq: "D", tags: { kind: "index", weighting: null }, source: 1, status: "ok", last: { t: LAST, v: idx.at(-1) }, moves: movesOf(idx), spark: sparkOf(idx), file: "series/index-energy_select.json" },
    { id: "equities-index-held_index", group: "equities", label: "A held index", unit: "points", tags: { kind: "index", weighting: null }, status: "licensed", note: "license needed: the publisher's terms forbid republication", file: "series/index-held_index.json" }] };
const write = (rel, v) => fs.writeFileSync(path.join(FIX, ...rel.split("/")), JSON.stringify(v));
write("index.json", list); write("energy_prices.json", prices); write("board.json", boardFile);
for (const [rel, v] of Object.entries(files)) write(rel, v);

try {
  // 3a. the board's group
  folder(FIX);
  const merged = B.holdRows(E.withEquities(board, F.equitiesBoard()), []);
  const mine = merged.rows.slice(board.rows.length);
  check(merged.groups.at(-1).id === "equities" && merged.groups.at(-1).lean === true && JSON.stringify(merged.groups.slice(0, -1)) === JSON.stringify(board.groups), "the board: the equities group after the board's own, which are as they were");
  check(JSON.stringify(merged.rows.slice(0, board.rows.length)) === JSON.stringify(B.holdRows(board, []).rows), "the board: every row it had is as it was, in its order");
  check(mine.length === 4 && mine.every((r) => r.group === "equities" && r.at === "" && r.code === ""), "the board: one row a segment's weighting and one an index");
  check(mine[0].status === "ok" && mine[0].last.v === eq.at(-1) && mine[0].moves.d.ch === boardFile.rows[0].moves.d.ch && mine[0].spark.v.length === 90 && mine[0].freq === "D", "the board: a row's latest value, moves and trend are the file's");
  check(merged.sources[mine[0].source] === boardFile.sources[0] && merged.sources[mine[2].source] === boardFile.sources[1] && merged.sources.length === board.sources.length + 2, "the board: a row's source is the file's, placed after the board's own");
  check(mine[0].open === "/equities?a=segment-integrated_oil_gas" && mine[2].open === "/equities?a=index-energy_select", "the board: a row opens its series on /equities");
  check(mine[3].status === "licensed" && !mine[3].last && !mine[3].moves && !mine[3].spark && !mine[3].open && /forbid republication/.test(mine[3].note), "the board: a held row has its name, its words and its reason, and no figure");
  check(mine[2].tags.kind === "index" && !("weighting" in mine[2].tags), "the board: a tag the file holds as null is left out");
  const g = merged.groups.at(-1);
  check(B.rowsOf(merged, g, {}).length === 4 && B.rowsOf(merged, g, { kind: "segment" }).length === 2 && B.rowsOf(merged, g, { kind: "index" }).length === 2, "the board: the group's filter shows segments, indices or both");
  check(B.leadRow(merged, g).id === "equities-segment-integrated_oil_gas-equal", "the board: the group's first row with a value leads its fold");
  check(B.benchOf(new URLSearchParams({ s: mine[0].id }), merged).s === null && B.benchOf(new URLSearchParams({ s: board.rows.find((r) => r.status === "ok").id, o: mine[0].id }), merged).o === null, "the board: an equities row is never the workbench's row or the series laid over it");
  const csv = B.rowsCsv(merged).split("\n");
  const line = csv.find((l) => l.startsWith("equities-segment-integrated_oil_gas-equal,"));
  check(!!line && line.includes(String(eq.at(-1))) && line.includes("Built by the ERW") && csv.some((l) => l.startsWith("equities-index-held_index,") && l.includes("licensed source needed")), "the board's rows as a CSV hold the group's rows, a held one with its words and no figure");
  const before = B.boardFileChecks(B.holdRows(board, [])), after = B.boardFileChecks(merged);
  check(after.every((c, i) => c.ok || !before[i].ok), `the board's own checks of its file pass with the group as without it (${after.filter((c) => !c.ok).map((c) => c.what.slice(0, 60)).join("; ")})`);
  check(E.withEquities(merged, boardFile) === merged, "a board file that already holds the group is left alone");
  check(E.boardRow({ id: "x", group: "equities", label: "X", unit: "points", status: "ok" }, 0).status === "not_held" && E.boardRow({ id: "x", group: "equities", label: "X", unit: "points", status: "something new" }, 0).status === "not_held", "a row marked ok with no value, or with a status the board does not know, is a blank row");

  // 3b. /equities as it opens: the first segment's two lines
  const html = draw(FIX);
  const t = text(html);
  check(html.includes('data-eq-state="files"') && html.includes('data-eq-window="1y"') && html.includes('data-eq-line="a" data-eq-shown="1"'), "as it opens: the first segment, the last year");
  check(t.includes("Every company counts the same") && t.includes("Larger companies count more"), "a segment's two weightings are named plainly");
  check(new RegExp(`data-n="eq\\|a\\|last">${E.levelWords(eq.at(-1)).replace(".", "\\.")}<`).test(html) && new RegExp(`data-n="eq\\|a\\|lastv">${E.levelWords(vw.at(-1)).replace(".", "\\.")}<`).test(html), "the last value of each weighting is the file's");
  check(html.includes(`data-check="pf|equities/series/segment-integrated_oil_gas.json|last/v" data-raw="${eq.at(-1)}"`) && html.includes("pf|equities/series/segment-integrated_oil_gas.json|moves_value_weight/y/pct"), "the figures carry their keys into the series' file");
  check(t.includes("6 companies, 5 of them with a public share count, on the last day"), "a segment says how many companies are in each line");
  check(count(html, /data-eq-line=/g) === 1 && t.includes("Integrated oil and gas: the last year"), "one chart, named with its window");
  check(/title="[^"]*Segment Integrated oil and gas \(6 companies\): A company whose filings report both[^"]*"/.test(html), "the segment's rule is on its name's hover");
  check(html.includes('data-eq-count="3|3"') && t.indexOf("Exxon Mobil Corp") < t.indexOf("Duke Energy Corp") && t.indexOf("Duke Energy Corp") < t.indexOf("NextEra Energy Inc"), "every company, in the list's own order");
  check(/data-not-held="1">license needed</.test(html.slice(html.indexOf('id="companies"'))) && /title="License needed: no source found[^"]*"/.test(html), "a company whose price is held says license needed in the table, with why on hover");
  check(/data-not-held="1">not filed</.test(html) && html.includes("no XBRL facts of these concepts"), "a company with no filed figures says not filed, with why on hover");
  check(!html.includes('id="filed"'), "no filed figures section while no company is chosen");
  check(["The line", "Every company", "Segments and indices", "Downloads"].every((x) => t.includes(x)) && count(html, /<h1/g) === 1, "one title and the sections");
  check(html.includes('href="/equities/rows?id=segment-integrated_oil_gas"') && html.includes('href="/equities/list"') && html.includes('href="/board#equities"'), "downloads: the series' days, the list, and the way back to the board");
  check(html.includes('href="/data/methods/equities"'), "the method note is linked");
  quiet(html, "as it opens");

  // 3c. two companies side by side, an energy price laid over, three months
  const two = draw(FIX, { a: "XOM", b: "DUK", p: "wti", win: "3m" });
  const tt = text(two);
  check(two.includes('data-eq-line="a" data-eq-shown="1"') && two.includes('data-eq-line="b" data-eq-shown="0"') && two.includes("xl:grid-cols-2"), "A and B side by side: one price shown, one held");
  check(tt.includes("Share price, DUK, Duke Energy Corp: license needed") && /data-eq-blank="line\|b"/.test(two), "a held share price is a blank that says license needed");
  check(/aria-label="XOM, Exxon Mobil Corp, close, USD\/share, with WTI crude oil, Cushing, spot \(USD\/bbl\) laid over it on its own axis/.test(two), "the energy price is laid over the line on its own axis, both named with their units");
  check(two.includes('id="filed"') && two.includes('data-eq-filed="2"'), "the filed figures of both companies, the held one's included");
  check(/data-n="eq\|a\|filed\|revenue"><span data-check="pf\|equities\/series\/XOM\.json\|quarterly\/0\/7" data-raw="83331000000"[^>]*>83,331</.test(two), "XOM's newest revenue, in USD million, with its key into the file");
  check(/data-n="eq\|b\|filed\|revenue"><span data-check="pf\|equities\/series\/DUK\.json\|quarterly\/0\/7" data-raw="8154000000"[^>]*>8,154</.test(two), "DUK's filed revenue is drawn although its price is held");
  check(/data-n="eq\|b\|filed\|capex"><span[^>]*data-not-held="1">not filed</.test(two), "a line not filed for the period says so");
  check(/title="83,331,000,000 USD, us-gaap:Revenues\. Filed on 10-Q, 2026-10-30, accession 0000000034088-26-000001: https:\/\/www\.sec\.gov\/Archives/.test(two), "a filed figure's hover: the exact figure, its concept, its form, its day and its filing's address");
  check(two.includes('href="https://www.sec.gov/Archives/edgar/data/0000034088/00000000340882600000' + "1" + '/form.htm"') && !two.includes('href="https://example.test/not-the-sec"'), "a period opens its filing on the SEC's site, and no other address is made a link");
  check(two.includes('data-eq-periods="a"') && tt.includes("XOM, Exxon Mobil Corp: every period filed (3), USD million") && tt.includes("12 months to 2025-12-31"), "every period a company filed, behind a fold, each with its months");
  check(tt.includes("4,262.0"), "shares in millions with one decimal");
  check(two.includes('href="/equities/filed?id=XOM"') && two.includes('href="/equities/filed/stata?id=DUK"'), "downloads: the filed figures of each company");
  quiet(two, "A and B");

  // 3d. choices: a monthly price, a held price, the table's filter and order, an address the page does not know
  const month = draw(FIX, { a: "index-energy_select", p: "henry_hub_month", win: "6m" });
  check(/aria-label="A made-up energy index, level, points, with Henry Hub natural gas, monthly \(USD\/MMBtu\) laid over it/.test(month), "a monthly price laid over an index");
  const idxAll = E.pointsOf(files["series/index-energy_select.json"], "level");
  const inWin = E.windowLike(E.pricePoints(prices, "henry_hub_month"), "6m", idxAll);
  check(inWin.length >= 5 && inWin.length <= 7 && inWin.every((p) => new Date(p.t).getUTCDate() === 1), "a monthly price keeps its own dates: one point a month of the window, none spread over days");
  const heldP = draw(FIX, { a: "XOM", p: "pjm_west" });
  check(/data-hint="1">PJM Western Hub, day-ahead: license needed</.test(heldP) && /title="License needed: PJM publishes its prices under a license/.test(heldP) && !/aria-label="[^"]*PJM Western Hub[^"]*laid over/.test(heldP), "a held energy price is not drawn: the chart says license needed, with why on hover");
  const seg = draw(FIX, { seg: "regulated_utilities" });
  check(seg.includes('data-eq-count="2|3"') && !text(seg.slice(seg.indexOf('id="companies"'), seg.indexOf('id="segments"'))).includes("Exxon"), "the table filtered by segment");
  check(draw(FIX, { q: "exx" }).includes('data-eq-count="1|3"') && draw(FIX, { shown: "1" }).includes('data-eq-count="2|3"') && draw(FIX, { q: "electric services" }).includes('data-eq-count="1|3"'), "the table filtered by words and by what is shown");
  const sorted = text(draw(FIX, { sort: "ticker", dir: "desc" }));
  const part = sorted.slice(sorted.indexOf("Every company"), sorted.indexOf("Segments and indices"));
  check(part.indexOf("Exxon Mobil") < part.indexOf("NextEra") && part.indexOf("NextEra") < part.indexOf("Duke Energy") && part.includes("Ticker (Z to A)"), "the table sorted by ticker, Z to A, and the head says so");
  check(draw(FIX, { a: "NEE" }).includes('href="/equities?a=NEE&amp;sort=ticker#companies"'), "a sort link keeps the choice of A");
  const odd = draw(FIX, { a: "zz", b: "zz", p: "zz", win: "zz", seg: "zz", sort: "zz" });
  check(odd.includes('data-eq-window="1y"') && odd.includes('data-eq-count="3|3"') && count(odd, /data-eq-line=/g) === 1, "an address the page does not know opens the defaults");
  const nee2 = draw(FIX, { a: "NEE" });
  check(/Regulated electric and gas utilities, Solar/.test(text(nee2)) && nee2.includes("In two segments: its utility is rate-regulated"), "a company in two segments names both, with the list's note on hover");
  check(/data-eq-filed="1"/.test(nee2) && /Newest period filed[\s\S]*data-not-held="1">not filed</.test(nee2), "a company with no filed figures: the section says not filed");

  // 3e. the pure parts and the downloads
  folder(FIX);
  const q = E.queryOf({}, list, prices);
  check(q.a === "segment-integrated_oil_gas" && E.hrefOf(q, {}, q.a) === "/equities" && E.hrefOf(q, { a: "XOM", p: "wti", win: "3m" }, q.a) === "/equities?a=XOM&p=wti&win=3m", "the defaults and an address that carries a choice");
  check(E.picksOf(list).map((p) => p.id).join() === "segment-integrated_oil_gas,index-energy_select,index-held_index,XOM,DUK,NEE", "what can be chosen: the segments' lines, the indices, the companies, in the list's order");
  check(E.seriesIdOf("series/XOM.json") === "XOM" && E.seriesIdOf("../x.json") === null && E.seriesIdOf("series/a/b.json") === null && F.readEquities("../../package.json") === null && F.readEquities("series/../index.json") === null, "only a file of the folder is ever named");
  check(E.secUrl("https://www.sec.gov/x") === "https://www.sec.gov/x" && E.secUrl("https://www.sec.gov.example.test/x") === null && E.secUrl("javascript:alert(1)") === null, "only the SEC's own address is a link");
  const sx = files["series/XOM.json"];
  const scsv = E.seriesCsv(sx, "https://example.test/equities/rows?id=XOM").split("\n");
  check(scsv.filter((l) => l && !l.startsWith("#")).length === 301 && scsv.some((l) => l === "# Held: adj_close is empty in every row: the source prints no adjusted close") && scsv.find((l) => !l.startsWith("#")) === "day,close,adj_close,volume,market_value", "a series' days as a CSV: its header, a held column named with its reason, a line a day");
  const hcsv = E.seriesCsv(files["series/DUK.json"], "u").split("\n");
  check(hcsv.filter((l) => l && !l.startsWith("#")).length === 1 && hcsv.some((l) => l.startsWith("# No row: the series is not shown. License needed")), "a held series' CSV has its header and no row");
  const fcsv = E.filedCsv(sx, "u").split("\n").filter((l) => l && !l.startsWith("#"));
  check(fcsv.length === 4 && fcsv[0] === QCOLS.join(",") && fcsv[1].startsWith("2026-07-01,2026-09-30,3,2026,Q3,10-Q,2026-10-30,83331000000,"), "the filed figures as a CSV, the file's own columns");
  check(E.filedCsv(files["series/NEE.json"], "u").split("\n").filter((l) => l && !l.startsWith("#")).length === 1, "a row of nulls is not a filing");
  const lcsv = E.listCsv(list, "u").split("\n");
  check(lcsv.filter((l) => l && !l.startsWith("#")).length === 4 && lcsv.some((l) => l.startsWith("# Segment solar: Solar: A company whose main reported business")) && lcsv.some((l) => l.startsWith("NEE,NextEra Energy Inc,0000753308,NYSE,4911,Electric services,regulated_utilities solar,shown,,not filed,")), "the list as a CSV: every company, the segments' rules in its header");
  for (const [name, spec, cols] of [["rows", R.rowsSpec(sx), sx.daily_columns], ["filed", R.filedSpec(sx), QCOLS], ["list", R.LIST_SPEC, E.LIST_HEAD]]) {
    check([...spec.text, ...spec.figures, ...spec.show, ...(spec.count ? [spec.count] : [])].every((c) => cols.includes(c)), `the ${name} readers name only columns the CSV has`);
    const stata = csvReader("do", "https://example.test/x", spec);
    check(!stata.includes("///") && spec.figures.every((c) => stata.includes(`destring ${c}, replace force`)) && !/\n\n\n/.test(stata) && !stata.includes(dash), `the ${name} Stata reader keeps the owner's rules`);
    check(csvReader("py", "https://example.test/x", spec).includes("pd.read_csv"), `the ${name} Python reader loads the rows`);
  }
  check(E.blankWords("license needed") === "license needed" && E.blankWords("source needed") === "source needed" && E.blankWords("x", true) === "not built yet" && E.isShown({ example: true, status: "shown" }) === false, "the blank's words; an example file shows nothing");
} finally {
  folder(null);
  if (!KEEP) fs.rmSync(FIX, { recursive: true, force: true });
}

if (fails.length) { console.log(`FAIL ${fails.length} of ${n}:\n  ${fails.join("\n  ")}`); process.exitCode = 1; }
else console.log(`ok: ${n} checks of energy equities (the board's group and /equities: no files, the contract's examples, a fixture of the contract's shape)`);
