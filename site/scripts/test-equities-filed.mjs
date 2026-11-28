// Energy Research Warehouse (ERW) site, session 10408 (chain 720, part E): /equities on the SEC's company figures.
// Since 27 November 2026 the equities files hold the companies and what each filed (the owner's ruling of 26 November),
// with every share price still held, "license needed". What a reader then meets is pinned here, drawn by the site's own
// code, without a build:
//   node --import ./scripts/events-page-register.mjs scripts/test-equities-filed.mjs
// The fixture is the one scripts/test-equities.mjs writes (its --keep), with one company's filed periods rewritten in
// the shapes the real files carry: two lengths of period to one period end (a 10-Q's 3 months and its year to date), a
// figure filed for the longer one only, an amended annual report beside the first one, a row that holds the period
// end's figures alone. Made-up values, each file marked as a test's fixture, which the site's own folder never reads.
// Held here: one figure over the periods filed is the figures as filed (nothing worked out from two filings; a period
// filed twice shows the later filing's figure); the newest period is one column for each length of period filed; a
// company whose share price is held keeps its blank, its filed figures and the energy price as a chart of its own;
// the choices are in the address and held to what the page offers. No network. Exit 0 when every check holds.
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const { EquitiesView } = await import("../app/equities/view.tsx");
const E = await import("../lib/equities.ts");

const fails = [];
let n = 0;
const check = (ok, what) => { n++; if (!ok) fails.push(what); };
const draw = (dir, query = {}) => { process.env.ERW_EQUITIES_DIR = dir; return renderToStaticMarkup(h(EquitiesView, { query })); };
const text = (html) => html.replace(/<title>[^<]*<\/title>/g, " ").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&amp;/g, "&").replace(/\s+/g, " ");
const dash = String.fromCharCode(0x2014);
const quiet = (html, where) => {
  const t = text(html);
  check(!/\bundefined\b|\bNaN\b|\bnull\b|\[object Object\]/.test(t), `${where}: "undefined", "NaN" or "null" on the page`);
  check(!html.includes(dash), `${where}: an em dash`);
  check(!/outperform|underperform|signal|\bbuy\b|\bsell\b|so what|overweight|undervalued/i.test(t), `${where}: a word of advice or a view`);
};

const KEEP = process.argv.includes("--keep") ? process.argv[process.argv.indexOf("--keep") + 1] : null;
if (KEEP) fs.mkdirSync(KEEP, { recursive: true });
const FIX = KEEP ?? fs.mkdtempSync(path.join(os.tmpdir(), "erw-c720-eqfiled-"));
execFileSync(process.execPath, ["--import", "./scripts/events-page-register.mjs", "scripts/test-equities.mjs", "--keep", FIX], { cwd: SITE, stdio: "pipe" });
const load = (name) => JSON.parse(fs.readFileSync(path.join(FIX, name), "utf8"));
const save = (name, v) => fs.writeFileSync(path.join(FIX, name), JSON.stringify(v));

// ---- The fixture: DUK's filed periods in the real files' shapes; a segment no rule fills -------------------------------
const M = 1_000_000;
const sec = (k) => [`0001326160-26-00001${k}`, `https://www.sec.gov/Archives/edgar/data/1326160/00013261602600001${k}/index.htm`];
const ROWS = [
  //  period_start, period_end, months, fy, fp, form, filed, revenue, net_income, capex, debt, shares
  ["2026-01-01", "2026-09-30", 9, 2026, "Q3", "10-Q", "2026-11-05", 2400 * M, 380 * M, 990 * M, 7900 * M, 77.8 * M, ...sec(0)],
  ["2026-07-01", "2026-09-30", 3, 2026, "Q3", "10-Q", "2026-11-05", 850 * M, 140 * M, null, 7900 * M, 77.8 * M, ...sec(0)],
  ["2026-01-01", "2026-06-30", 6, 2026, "Q2", "10-Q", "2026-08-05", 1550 * M, 240 * M, 640 * M, 7850 * M, 77.7 * M, ...sec(1)],
  ["2026-04-01", "2026-06-30", 3, 2026, "Q2", "10-Q", "2026-08-05", 750 * M, 100 * M, null, 7850 * M, 77.7 * M, ...sec(1)],
  ["2026-01-01", "2026-03-31", 3, 2026, "Q1", "10-Q", "2026-05-05", 800 * M, 140 * M, 310 * M, 7800 * M, 77.6 * M, ...sec(2)],
  // the annual report amended: the later filing restates net income and holds nothing else
  ["2025-01-01", "2025-12-31", 12, 2025, "FY", "10-K/A", "2026-04-01", null, 455 * M, null, null, null, ...sec(3)],
  ["2025-01-01", "2025-12-31", 12, 2025, "FY", "10-K", "2026-02-26", 3200 * M, 490 * M, 1400 * M, 8700 * M, 77.5 * M, ...sec(4)],
  ["2025-07-01", "2025-09-30", 3, 2025, "Q3", "10-Q", "2025-11-07", 820 * M, 130 * M, null, 7600 * M, 77.4 * M, ...sec(5)],
  // a row that holds the period end's figures alone (the real files carry 148 of them)
  [null, "2024-12-31", null, 2024, "FY", "10-K", "2025-02-27", null, null, null, 8000 * M, 77.2 * M, ...sec(6)],
];
const duk = load("series/DUK.json");
check(duk.status === "license needed" && Array.isArray(duk.quarterly_columns) && duk.quarterly_columns[7] === "revenue" && duk.quarterly_columns[11] === "shares_outstanding", "the base fixture is not the one this test builds on");
duk.quarterly = ROWS;
save("series/DUK.json", duk);
const list = load("index.json");
list.segments.push({ id: "lng", label: "LNG", rule: null, rule_why: "no SEC industry code is LNG alone: the exporters file under 4924 with the local gas distributors", n_companies: 0 });
// every share price held, as the files of 27 November are: the list names no segment line and no index
const heldList = { ...list, segment_series: [], indices: [], held: { companies: null, indices: "license needed: no source found whose terms allow the ERW to keep daily share prices or index levels", prices: "license needed: no source found whose terms allow the ERW to keep daily share prices or index levels" },
  companies: list.companies.filter((c) => c.id !== "XOM").map((c) => (c.id === "NEE" ? { ...c, price_status: "license needed", price_why: "license needed: no source found", fundamentals_status: "source needed", fundamentals_why: "no us-gaap 10-Q or 10-K facts on EDGAR" } : c)) };
save("index.json", list);

// ---- 1. One figure over the periods filed (lib/equities.ts figureLine) ---------------------------------------------------
const fs1 = E.filingsOf(duk);
const ends = (line) => line.map((p) => p.f.period_end).join(" ");
const vals = (line) => line.map((p) => p.v / M).join(" ");
{
  check(fs1.length === 9 && fs1[8].period_start === null && fs1[8].months === null, "a row with a period end and no start is a filing");
  const rev3 = E.figureLine(fs1, "revenue", "3");
  check(ends(rev3) === "2025-09-30 2026-03-31 2026-06-30 2026-09-30" && vals(rev3) === "820 800 750 850", "revenue by 3 months: the four periods filed for exactly 3 months, oldest first");
  check(!rev3.some((p) => p.f.period_end === "2025-12-31"), "a fourth quarter not filed on its own has no point: nothing is worked out from the year and the nine months");
  const inc12 = E.figureLine(fs1, "net_income", "12");
  check(inc12.length === 1 && inc12[0].v === 455 * M && inc12[0].f.form === "10-K/A" && inc12[0].f.i === 5, "a period filed twice: the later filing's figure, with its own row's key");
  const rev12 = E.figureLine(fs1, "revenue", "12");
  check(rev12.length === 1 && rev12[0].v === 3200 * M && rev12[0].f.form === "10-K", "an amended filing that holds no revenue leaves the first filing's revenue");
  check(vals(E.figureLine(fs1, "capex", "3")) === "310" && vals(E.figureLine(fs1, "capex", "12")) === "1400", "capital spending: only the periods filed at that exact length (a 10-Q's is its year to date)");
  const debt3 = E.figureLine(fs1, "debt", "3");
  check(ends(debt3) === "2024-12-31 2025-09-30 2025-12-31 2026-03-31 2026-06-30 2026-09-30" && vals(debt3) === "8000 7600 8700 7800 7850 7900", "debt, a figure at a period's end: one point a period end, once");
  check(ends(E.figureLine(fs1, "debt", "12")) === "2024-12-31 2025-12-31" && vals(E.figureLine(fs1, "shares_outstanding", "12")) === "77.2 77.5", "debt and shares by 12 months: the period ends of the annual reports");
  check(E.figureLine([], "revenue", "3").length === 0, "no filing, no point");
}

// ---- 2. The newest period's columns (newestOf) ---------------------------------------------------------------------------
{
  const cols = E.newestOf(fs1);
  check(cols.length === 2 && cols[0].months === 3 && cols[1].months === 9 && cols.every((c) => c.head.period_end === "2026-09-30"), "the newest period end, one column for each length of period filed to it, shortest first");
  check(cols[0].cells.revenue.v === 850 * M && cols[0].cells.revenue.f.i === 1 && cols[1].cells.revenue.v === 2400 * M && cols[1].cells.revenue.f.i === 0, "each column's revenue is the figure filed for exactly that period");
  check(cols[0].cells.capex === null && cols[1].cells.capex.v === 990 * M, "a figure filed for the longer period only is empty in the shorter one");
  check(cols[0].cells.debt.v === 7900 * M && cols[1].cells.debt.v === 7900 * M && cols[0].cells.shares_outstanding.v === 77.8 * M, "debt and shares are the period end's, the same in both columns");
  check(E.newestOf([]).length === 0, "no filing, no column");
  const only = E.newestOf(fs1.slice(8));
  check(only.length === 1 && only[0].months === null && only[0].cells.debt.v === 8000 * M && only[0].cells.revenue === null, "a newest row that holds the period end's figures alone is one column");
}

// ---- 3. The page: a company whose share price is held ---------------------------------------------------------------------
{
  const html = draw(FIX, { a: "DUK" });
  const t = text(html);
  quiet(html, "DUK");
  check(html.includes('data-eq-line="a" data-eq-shown="0"') && /data-eq-blank="line\|a"[^>]*>Share price, DUK, Duke Energy Corp: license needed</.test(html), "the share price is a blank that says license needed");
  check(/title="License needed: no source found whose terms allow the ERW to show daily prices[^"]*"[^>]*data-eq-blank="line\|a"/.test(html), "the blank's hover is the file's own reason");
  check(html.includes('data-eq-figure="a" data-eq-points="4"'), "the chosen figure (revenue by 3 months) is drawn over the four periods filed");
  check(/data-n="eq\|a\|figure"><span data-check="pf\|equities\/series\/DUK\.json\|quarterly\/1\/7" data-raw="850000000"[^>]*>850</.test(html), "the newest period's figure above the chart, in USD million, with its key into the file");
  check(t.includes("Revenue, 3 months to 2026-09-30") && t.includes("Duke Energy Corp: revenue, 3 months to each period end"), "the figure and its period are named in words");
  check(/aria-label="DUK, Duke Energy Corp: revenue, 3 months to each period end, USD million, 4 periods from 2025-09-30 to 2026-09-30, as filed with the SEC"/.test(html), "the chart's name says what it draws, how many periods and from where");
  check(html.includes("A period not filed on its own has no point") && html.includes("a period filed twice shows the later filing"), "what is not drawn, and the amended filing's rule, are in the chart's hover");
  check(!html.includes("data-check=\"pf|equities/series/DUK.json|daily") && !html.includes("|last|v"), "no figure of a held price is drawn");
  // the energy price keeps a chart of its own while no line can carry it
  check(html.includes('data-eq-price="wti"') && t.includes("Energy price") && !t.includes("Energy price laid over") && !t.includes("press one to lay it over"), "with no line to lay it over, the first energy price is drawn as a line of its own");
  check(/<select[^>]*name="fig"/.test(html) && /<select[^>]*name="per"/.test(html) && t.includes("Filed figure") && t.includes("Its periods"), "the figure and its periods are choices of the page");
  // the words beside "Reset to the defaults" are of what the page opens on (here a segment's line, which is shown), not of what is chosen
  check(t.includes("Reset to the defaults : Integrated oil and gas alone, no price laid over, the last year") && !t.includes("the last year, revenue by 3 months"), "the defaults said are those of what the page opens on");
  // the newest period: two columns, each with its own key
  check(html.includes('data-eq-newest="a|3"') && html.includes('data-eq-newest="a|9"') && t.includes("DUK, 3 months to 2026-09-30") && t.includes("DUK, 9 months to 2026-09-30"), "the newest period: the 3 months and the 9 months side by side");
  check(/data-n="eq\|a\|filed\|revenue"><span data-check="pf\|equities\/series\/DUK\.json\|quarterly\/1\/7" data-raw="850000000"[^>]*>850</.test(html), "the 3 months' revenue");
  check(/data-n="eq\|a\|filed\|revenue\|9"><span data-check="pf\|equities\/series\/DUK\.json\|quarterly\/0\/7" data-raw="2400000000"[^>]*>2,400</.test(html), "the 9 months' revenue");
  check(/data-n="eq\|a\|filed\|capex"><span[^>]*data-not-held="1">not filed</.test(html) && /data-n="eq\|a\|filed\|capex\|9"><span data-check="pf\|equities\/series\/DUK\.json\|quarterly\/0\/9" data-raw="990000000"[^>]*>990</.test(html), "capital spending: not filed for the 3 months, filed for the 9");
  check(/data-n="eq\|a\|filed\|shares_outstanding"><span data-check="pf\|equities\/series\/DUK\.json\|quarterly\/[01]\/11" data-raw="77800000"[^>]*>77\.8</.test(html), "shares in millions, one decimal");
  check(t.includes("DUK, Duke Energy Corp: every period filed (9), USD million") && (html.match(/https:\/\/www\.sec\.gov\/Archives\/edgar\/data\/1326160\//g) ?? []).length >= 9, "every period filed stays behind its fold, each opening its filing");
}

// ---- 4. The other figures and lengths ------------------------------------------------------------------------------------
{
  const inc = draw(FIX, { a: "DUK", fig: "net_income", per: "12" });
  check(inc.includes('data-eq-figure="a" data-eq-points="1"') && /data-eq-blank="figure\|a"[^>]*>Net income, 12 months to each period end, DUK, Duke Energy Corp: one period filed</.test(inc), "one period filed is no line: the page says so");
  check(inc.includes("once, for 12 months to 2025-12-31"), "and its hover names the one period");
  quiet(inc, "one period");
  const cap = draw(FIX, { a: "DUK", fig: "capex", per: "12" });
  check(cap.includes('data-eq-points="1"'), "capital spending by 12 months: the one year filed");
  const debt = draw(FIX, { a: "DUK", fig: "debt" });
  check(debt.includes('data-eq-figure="a" data-eq-points="6"') && text(debt).includes("Long-term debt, at 2026-09-30") && text(debt).includes("long-term debt, at the end of each period filed"), "debt: a point at each period end, named as a figure at a day");
  check(/data-n="eq\|a\|figure"><span data-check="pf\|equities\/series\/DUK\.json\|quarterly\/[01]\/10" data-raw="7900000000"[^>]*>7,900</.test(debt), "the newest debt with its key");
  const sh = draw(FIX, { a: "DUK", fig: "shares_outstanding", per: "12" });
  check(sh.includes('data-eq-points="2"') && text(sh).includes("shares outstanding, at the end of each year reported") && /aria-label="[^"]*million shares/.test(sh), "shares by 12 months: the annual reports' period ends, in million shares");
  // a mistyped choice falls back to the page's own
  const odd = draw(FIX, { a: "DUK", fig: "profit", per: "7" });
  check(odd.includes('data-eq-figure="a" data-eq-points="4"') && text(odd).includes("revenue, 3 months to each period end"), "a figure or a length the page does not offer falls back to revenue by 3 months");
  quiet(odd, "a mistyped choice");
}

// ---- 5. Two companies, and a company with no filed figures ---------------------------------------------------------------
{
  const two = draw(FIX, { a: "XOM", b: "DUK" });
  check(two.includes('data-eq-figure="a"') && two.includes('data-eq-figure="b" data-eq-points="4"') && two.includes('data-eq-filed="2"'), "two companies: the chosen figure of each, side by side");
  check(two.includes('data-eq-line="a" data-eq-shown="1"') && !two.includes("data-eq-price="), "where one line is shown the energy price is laid over it, not drawn alone");
  check(two.includes('data-eq-newest="a|3"') && two.includes('data-eq-newest="b|3"') && two.includes('data-eq-newest="b|9"'), "the newest period of both, a column for each length each filed");
  quiet(two, "two companies");
  const nee = draw(FIX, { a: "NEE" });
  check(nee.includes('data-eq-figure="a" data-eq-points="0"') && /data-eq-blank="figure\|a"[^>]*>Revenue, NEE, NextEra Energy Inc: not filed</.test(nee) && nee.includes('data-eq-newest="a|held"'), "a company with no filed figures: a blank in the chart's place and in the table, with the file's reason");
  quiet(nee, "no filed figures");
}

// ---- 6. Every share price held, as the files of 27 November are -----------------------------------------------------------
{
  save("index.json", heldList);
  const html = draw(FIX, {});
  const t = text(html);
  quiet(html, "every price held");
  check(html.includes('data-eq-picks="2"') && html.includes('data-eq-slot="a"') && t.includes("DUK, Duke Energy Corp"), "the page opens on the first company of the list");
  check(html.includes('data-eq-line="a" data-eq-shown="0"') && html.includes('data-eq-figure="a" data-eq-points="4"') && html.includes('data-eq-price="wti"'), "as it opens: the price a blank, the filed figure drawn, the energy price a line of its own");
  check(/data-eq-no-rule="lng"[^>]*>0</.test(html) && html.includes("No company is placed in LNG: no SEC industry code is LNG alone") && !html.includes("seg=lng"), "a segment no rule fills: its nought with the reason on hover, and no empty table to open");
  check(draw(FIX, { filed: "1" }).includes('data-eq-count="1|2"') && draw(FIX, { shown: "1" }).includes('data-eq-count="0|2"'), "the table's filter: only the companies whose filed figures are shown");
  check(/<input type="checkbox" name="filed" checked="" value="1"/.test(draw(FIX, { filed: "1" })) && !/<input type="checkbox" name="filed" checked=""/.test(html), "the filter's box reads the address");
  check(t.includes("Reset to the defaults : Duke Energy Corp alone, the first energy price the files show, the last year, revenue by 3 months"), "the defaults said when the page opens on a company whose price is held");
  const src = html.slice(html.indexOf('id="companies"'));
  check(/data-not-held="1">license needed</.test(src) && /data-not-held="1">source needed</.test(src), "the table says which is held and why, in the catalogue's words");
  save("index.json", list);
}

// ---- 7. The address ------------------------------------------------------------------------------------------------------
{
  const prices = load("energy_prices.json");
  const q = E.queryOf({}, list, prices);
  check(q.fig === "revenue" && q.per === "3" && q.filed === false && E.hrefOf(q, {}, q.a) === "/equities", "the defaults are left out of the address");
  check(E.hrefOf(q, { a: "DUK", fig: "debt", per: "12", filed: true }, q.a) === "/equities?a=DUK&fig=debt&per=12&filed=1", "a figure, a length and the filter are in the address");
  const back = E.queryOf({ a: "DUK", fig: "debt", per: "12", filed: "1" }, list, prices);
  check(back.fig === "debt" && back.per === "12" && back.filed === true && back.a === "DUK", "and read back from it");
  check(E.queryOf({ fig: "constructor", per: "__proto__" }, list, prices).fig === "revenue" && E.queryOf({ fig: ["debt", "capex"] }, list, prices).fig === "revenue", "a name the page does not offer, or one given twice, is the default");
  const html = draw(FIX, { a: "DUK", fig: "debt", per: "12", seg: "regulated_utilities" });
  check(/<input type="hidden" name="fig" value="debt"/.test(html) && /<input type="hidden" name="per" value="12"/.test(html), "the table's filter keeps the figure and its length");
  check(html.includes("fig=debt&amp;per=12"), "and so do the page's links");
  check(E.FIGURES.join(" ") === "revenue net_income capex debt shares_outstanding" && E.PERIOD_KEYS.join(" ") === "3 12", "the figures and lengths offered");
}

// ---- 8. A finger's height (session 10413: read on production at 390 px by a finger) -----------------------------------------
{
  // a company's name in the table was 18 px tall and a filing's link under a figure 15 px: each has padding now, and a
  // negative margin of the same size, so the row and the line keep their height and only the place a finger lands grows
  const html = draw(FIX, { a: "DUK" });
  const table = html.slice(html.indexOf('id="companies"'));
  const names = [...table.matchAll(/<a [^>]*title="Draw [^"]*"[^>]*>/g)].map((m) => m[0]);
  check(names.length > 0 && names.every((a) => a.includes('class="inline-block py-1 -my-1"')), `every company's name in the table has a finger's height (${names.length} names)`);
  const filings = [...html.matchAll(/<a [^>]*title="The filing on the SEC&#x27;s site[^"]*"[^>]*>/g)].map((m) => m[0]);
  check(filings.length > 0 && filings.every((a) => a.includes('class="inline-block py-1.5 -my-1.5"')), `every filing's link has a finger's height (${filings.length} links)`);
}

// ---- 9. The newest period filed, in the table of every company (session 10414: the list's newest_filed) -------------------
{
  const before = load("index.json");
  // a list none of whose companies carries the field is the table as it was
  const old = draw(FIX, { a: "DUK" });
  const oldTable = old.slice(old.indexOf('id="companies"'));
  check(!before.companies.some((c) => "newest_filed" in c) && oldTable.includes(">Filed figures<") && !oldTable.includes('data-eq-sort="filed"') && !oldTable.includes("data-eq-newest-of="), "a list with no newest period: the column says only that the figures are shown");
  const at = (id) => before.companies.findIndex((c) => c.id === id);
  const NOTE = "the filed history under this SEC number starts with the period to 2026-06-30: a new registrant (docs/methods/equities.md)";
  const filedOf = {
    DUK: { period_end: "2026-09-30", form: "10-Q", filed: "2026-11-05", url: sec(0)[1], revenue: { months: 3, v: 850 * M }, net_income: { months: 3, v: 140 * M }, capex: { months: 9, v: 990 * M }, debt: 7900 * M, shares_outstanding: 77.8 * M },
    NEE: { period_end: "2025-12-31", form: "10-K", filed: "2026-02-13", url: "https://www.sec.gov/Archives/edgar/data/753308/000075330826000010/index.htm", revenue: { months: 12, v: 27412 * M }, net_income: { months: 12, v: 6835 * M }, capex: null, debt: 89556 * M, shares_outstanding: 2085 * M },
    XOM: { period_end: "2026-06-30", form: "10-Q", filed: "2026-08-01", url: "http://not-the-sec.example/x", revenue: null, net_income: { months: 3, v: 7000 * M }, capex: null, debt: null, shares_outstanding: null },
  };
  check(["DUK", "NEE", "XOM"].every((id) => at(id) >= 0), "the base fixture lists DUK, NEE and XOM");
  // one more company whose figures are shown and whose newest period the list does not give
  // (the base fixture's companies are the three above: a fourth is added after them, so no position of theirs moves)
  const spare = { ...before.companies[at("DUK")], id: "ZFX", ticker: "ZFX", name: "Zeta Fixture Corp", cik: "0000000001", file: "series/ZFX.json", fundamentals_status: "shown", fundamentals_why: null };
  const list2 = { ...before, companies: [...before.companies.map((c) => ({ ...c, ...(filedOf[c.id] ? { fundamentals_status: "shown", fundamentals_why: c.id === "XOM" ? NOTE : null } : {}), newest_filed: filedOf[c.id] ?? null })), { ...spare, newest_filed: null }] };
  save("index.json", list2);
  const none = list2.companies.find((c) => c.id === "ZFX");
  const html = draw(FIX, { a: "DUK" });
  const table = html.slice(html.indexOf('id="companies"'), html.indexOf('id="segments"'));
  quiet(html, "the newest period in the table");
  check(table.includes('data-eq-sort="filed"') && table.includes(">Newest period filed<") && text(table).includes("Newest period filed , with its revenue in USD million") && !table.includes("Revenue of that period") && !table.includes(">Filed figures<") && (table.slice(0, table.indexOf("</thead>")).match(/<th /g) ?? []).length === 7 && (oldTable.slice(0, oldTable.indexOf("</thead>")).match(/<th /g) ?? []).length === 7, "the table keeps its seven columns (seen in a build: an eighth made it wider than its frame): the newest period filed, a head that sorts, and its revenue");
  check(/href="\/equities\?[^"]*sort=filed&amp;dir=desc[^"]*#companies"[^>]*title="Sort by the newest period filed, newest first"/.test(table), "the head's first press sorts newest first");
  const rowOf = (id) => { const i = table.indexOf(`data-eq-newest-of="${id}"`); return i < 0 ? "" : table.slice(i, table.indexOf("</tr>", i)); };
  const dukRow = rowOf("DUK");
  check(dukRow.includes(`<a href="${sec(0)[1]}" class="inline-block py-1 -my-1" rel="noopener"`) && dukRow.includes(">2026-09-30, 10-Q</a>") && dukRow.includes("filed 2026-11-05"), "a company's newest period: its end and form, opening the filing, with a finger's height");
  check(dukRow.includes(`data-check="pf|equities/index.json|companies/${at("DUK")}/newest_filed/revenue/v" data-raw="850000000"`) && />850<\/span>/.test(dukRow) && text(dukRow).includes("Revenue 850 , 3 months") && dukRow.includes("850,000,000 USD"), "its revenue in USD million, keyed into the list, with the months it covers and the exact figure on hover");
  const neeRow = rowOf("NEE");
  check(/>27,412<\/span>/.test(neeRow) && text(neeRow).includes("Revenue 27,412 , 12 months") && neeRow.includes(">2025-12-31, 10-K</a>"), "a company whose newest filing is a year's: twelve months, said beside the figure");
  const xomRow = rowOf("XOM");
  check(xomRow.includes(">2026-06-30, 10-Q</span>") && !xomRow.includes("not-the-sec.example") && />revenue not filed</.test(xomRow) && xomRow.includes("gives no revenue under the concept the ERW reads"), "an address that is not the SEC's is no link; a newest filing with no revenue says so");
  check(xomRow.includes('data-eq-filed-note-mark="XOM"') && xomRow.includes("A note on what XOM filed: the filed history under this SEC number starts") && !dukRow.includes("data-eq-filed-note-mark"), "a note the list carries while the figures are shown is marked on the company's row, and only there");
  check(!!none && />none filed</.test(table) && table.includes(`${none.ticker}: the list holds no newest period for this company.`), "a company shown with no newest period says none filed");
  const heldRow = list2.companies.find((c) => c.fundamentals_status !== "shown");
  check(!heldRow || table.includes(`>${E.blankWords(heldRow.fundamentals_status)}<`), "a company whose filed figures are held is a blank with its reason");
  // the sort: newest first, then oldest first (a company with none first), then the list's own order
  const order = (desc) => E.companiesOf(list2, { seg: null, q: "", shown: false, sort: "filed", desc }).map((c) => c.id);
  const newestFirst = order(true), oldestFirst = order(false);
  check(newestFirst.slice(0, 3).join(" ") === "DUK XOM NEE" && newestFirst[newestFirst.length - 1] === "ZFX" && newestFirst.length === list2.companies.length, "newest first: the period ends in order, a company with none last");
  check(oldestFirst.slice(0, 3).join(" ") === "NEE XOM DUK" && oldestFirst[oldestFirst.length - 1] === "ZFX", "oldest first: the reverse, a company with none still last");
  const sorted = draw(FIX, { a: "DUK", sort: "filed", dir: "desc" });
  const st = sorted.slice(sorted.indexOf('id="companies"'), sorted.indexOf('id="segments"'));
  check(st.indexOf('data-eq-newest-of="DUK"') < st.indexOf('data-eq-newest-of="XOM"') && st.indexOf('data-eq-newest-of="XOM"') < st.indexOf('data-eq-newest-of="NEE"') && st.includes("Newest period filed (newest first)") && /title="Sorted newest first: press for oldest first"/.test(st), "the page in that order, and its head says which");
  const asc = draw(FIX, { a: "DUK", sort: "filed" });
  const at2 = asc.slice(asc.indexOf('id="companies"'), asc.indexOf('id="segments"'));
  const head = at2.slice(at2.indexOf('data-eq-sort="filed"') - 400, at2.indexOf('data-eq-sort="filed"') + 200);
  check(at2.includes("Newest period filed (oldest first)") && /title="Sorted oldest first: press for the list&#x27;s own order"/.test(at2) && !/sort=filed/.test(head.slice(head.lastIndexOf("<a "))), "oldest first, and the next press is the list's own order");
  check(E.queryOf({ sort: "filed", dir: "desc" }, list2).sort === "filed" && E.queryOf({ sort: "revenue" }, list2).sort === null, "the address takes the new sort and no other new word");
  // the note under a company's own figures, in the file's words
  const withNote = { ...list2, companies: list2.companies.map((c) => (c.id === "DUK" ? { ...c, fundamentals_why: NOTE } : c)) };
  save("index.json", withNote);
  const noted = draw(FIX, { a: "DUK" });
  check(noted.includes('data-eq-filed-note="DUK"') && text(noted).includes(`A note on what DUK filed: ${NOTE}.`) && !html.includes('data-eq-filed-note="DUK"'), "a company drawn whose filings carry a note: the note under its figures; none where the list has none");
  // the list's download: the newest period's columns after the columns it had
  const csv = E.listCsv(list2, "https://example.test/equities/list");
  const lines9 = csv.split("\n").filter((l) => l && !l.startsWith("#"));
  check(lines9[0] === E.LIST_HEAD.join(",") && E.LIST_HEAD.slice(0, 13).join(",") === "ticker,name,cik,exchange,sic,sic_label,segments,price_status,price_why,fundamentals_status,fundamentals_why,first_day,last_day" && E.LIST_HEAD.length === 25, "the list's CSV keeps its thirteen columns and gains twelve");
  const dukLine = lines9.find((l) => l.startsWith("DUK,"));
  check(!!dukLine && dukLine.endsWith(`,2026-09-30,10-Q,2026-11-05,${sec(0)[1]},850000000,3,140000000,3,990000000,9,7900000000,77800000`), "a company's line carries its newest period as filed, in USD and shares");
  const noneLine = lines9.find((l) => l.startsWith(`${none?.ticker},`));
  check(!!noneLine && noneLine.endsWith(",,,,,,,,,,,,"), "a company with no newest period: twelve empty cells");
  check(/^# newest_\*: the newest period the company filed with the SEC/m.test(csv), "the CSV's head says what the new columns are");
  const { LIST_SPEC } = await import("../app/equities/reader.ts");
  check([...LIST_SPEC.text, ...LIST_SPEC.figures].length === E.LIST_HEAD.length && E.LIST_HEAD.every((c) => LIST_SPEC.text.includes(c) || LIST_SPEC.figures.includes(c)) && LIST_SPEC.figures.join(",") === E.LIST_FILED_FIGURES.join(","), "the readers know every column: the sums, their months, debt and shares as figures");
  save("index.json", before);
}

if (!KEEP) fs.rmSync(FIX, { recursive: true, force: true });
if (fails.length) { for (const f of fails) console.log(`FAIL ${f}`); console.log(`${fails.length} of ${n} checks failed`); process.exit(1); }
console.log(`ok: ${n} checks of /equities on the filed figures (one figure over the periods filed, the newest period's columns, a held price beside public filings)`);
