// Energy Research Warehouse (ERW) site, session 10405 (chain 720, part E): the fields the equities contract gained on
// 26 November 2026 in answer to data requests 571 and 572 (a company's last close, changes and market value in the
// list; the board's averages, 30-day low and high and one-year range on each `ok` row of the board file), read by the
// site's own code, without a build.
//   node --import ./scripts/events-page-register.mjs scripts/test-equities-cells.mjs
// The fixture is the one scripts/test-equities.mjs writes (its --keep), with those fields added to two companies and
// to one board row: made-up values, each file marked as a test's fixture, which the site's own folder never reads.
// Held here: a list and a board file with none of the fields are drawn as they were (the companies' table has its seven
// columns; the board's group is lean); with them, the table gains the close, the five changes and the market value,
// each with its key into the list by the company's place in the file, a rise with its sign, and a company whose price
// is held says so in those cells; the board's group takes the board's full columns and a row carries only the cells
// the file holds. No network. Exit 0 when every check holds, 1 otherwise.
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
const board = JSON.parse(fs.readFileSync(path.join(SITE, "data", "board.json"), "utf8"));

const fails = [];
let n = 0;
const check = (ok, what) => { n++; if (!ok) fails.push(what); };
const draw = (dir, query = {}) => { process.env.ERW_EQUITIES_DIR = dir; return renderToStaticMarkup(h(EquitiesView, { query })); };
const text = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&amp;/g, "&").replace(/\s+/g, " ");
const dash = String.fromCharCode(0x2014);
const fig = (html, keyPath, raw, shown) => new RegExp(`data-check="pf\\|equities/index\\.json\\|${keyPath.replace(/[/]/g, "\\/")}" data-raw="${String(raw).replace(".", "\\.").replace("-", "\\-")}"[^>]*>${shown.replace(/[.+]/g, "\\$&")}<`).test(html);

// `--keep <folder>` writes the fixture there and leaves it, for a local build served with ERW_EQUITIES_DIR (to see the
// columns before any real company exists; such a build is looked at on this machine and never deployed)
const KEEP = process.argv.includes("--keep") ? process.argv[process.argv.indexOf("--keep") + 1] : null;
if (KEEP) fs.mkdirSync(KEEP, { recursive: true });
const FIX = KEEP ?? fs.mkdtempSync(path.join(os.tmpdir(), "erw-c720-eqcells-"));
execFileSync(process.execPath, ["--import", "./scripts/events-page-register.mjs", "scripts/test-equities.mjs", "--keep", FIX], { cwd: SITE, stdio: "pipe" });
const load = (name) => JSON.parse(fs.readFileSync(path.join(FIX, name), "utf8"));
const save = (name, v) => fs.writeFileSync(path.join(FIX, name), JSON.stringify(v));

// ---- 1. As the files stand: none of the fields ------------------------------------------------------------------------
const list = load("index.json"), eq = load("board.json");
check(list.companies.length >= 3 && eq.rows.some((r) => r.status === "ok"), "the base fixture is not the one this test builds on");
{
  const html = draw(FIX, {});
  check(!html.includes("data-eq-priced") && !html.includes("|companies/"), "a list with no close, change or market value draws the columns, or a figure of them");
  check(E.companiesPriced(list.companies) === false, "companiesPriced: a list with none of the fields");
  const merged = E.withEquities(board, eq);
  const g = merged.groups.find((x) => x.id === "equities");
  check(g && g.lean === true, "a board file whose rows carry no other cell: the group is not lean");
  check(merged.rows.filter((r) => r.group === "equities").every((r) => !("avg7" in r) && !("range" in r)), "a row carries a cell the file does not hold");
  check(eq.rows.every((r) => !E.hasWideCells(r)), "hasWideCells: a row with none of the cells");
}

// ---- 2. The companies' close, changes and market value ------------------------------------------------------------------
const mv = (t, v, ch, pct) => ({ t, v, ch, pct });
const a = list.companies[0], b = list.companies[1], c = list.companies[2];
a.last_close = { t: "2026-11-25", v: 118.42 };
a.moves = { d: mv("2026-11-24", 117.3, 1.12, 0.95), w: mv("2026-11-18", 120, -1.58, -1.32), m: mv("2026-10-26", 110.5, 7.92, 7.17), ytd: mv("2025-12-31", 100, 18.42, 18.42), y: null };
a.market_value = { t: "2026-11-25", v: 498765432100 };
// a company whose close is held but whose share count is not: a close and no market value
b.last_close = { t: "2026-11-25", v: 64 };
b.moves = { d: mv("2026-11-24", 64, 0, 0), w: null, m: null, ytd: null, y: mv("2025-11-25", 80, -16, -20) };
b.market_value = null;
// a third company carries none of them
c.last_close = null; c.moves = null; c.market_value = null;
save("index.json", list);
{
  check(E.companiesPriced(list.companies) === true, "companiesPriced: a list where a company has a close");
  const html = draw(FIX, {});
  const table = html.slice(html.indexOf('id="companies"'));
  check(html.includes('data-eq-priced="1"') && text(table).includes("Last close, USD") && text(table).includes("Market value, USD"), "the companies' table has no column of the close and the market value");
  const ia = 0, ib = 1;
  check(fig(html, `companies/${ia}/last_close/v`, 118.42, "118.42"), "a company's last close, keyed by its place in the file");
  check(fig(html, `companies/${ia}/moves/d/pct`, 0.95, "+0.95%") && fig(html, `companies/${ia}/moves/w/pct`, -1.32, "-1.32%") && fig(html, `companies/${ia}/moves/ytd/pct`, 18.42, "+18.42%"), "a company's changes: a rise with its sign, a fall with its own");
  check(fig(html, `companies/${ia}/market_value/v`, 498765432100, "498,765,432,100"), "a company's market value, whole, keyed");
  check(!html.includes(`companies/${ia}/moves/y/`), "a change the list does not hold is drawn as a figure");
  check(fig(html, `companies/${ib}/last_close/v`, 64, "64.00") && fig(html, `companies/${ib}/moves/d/pct`, 0, "0.00%") && fig(html, `companies/${ib}/moves/y/pct`, -20, "-20.00%"), "a second company's close and changes");
  check(!html.includes(`companies/${ib}/market_value/`) && !html.includes("companies/2/"), "a market value the list does not hold, or a company with none of the fields, is drawn as a figure");
  // the keys follow the file's order when the table is sorted another way
  const sorted = draw(FIX, { sort: "name", dir: "desc" });
  check(fig(sorted, `companies/${ia}/last_close/v`, 118.42, "118.42") && fig(sorted, `companies/${ib}/last_close/v`, 64, "64.00"), "sorted the other way, a figure's key no longer names the company's place in the file");
  const t = text(html);
  check(!/\bundefined\b|\bNaN\b|\bnull\b/.test(t) && !html.includes(dash), '"undefined", "NaN", "null" or an em dash on the page');
  check(!/outperform|underperform|signal|\bbuy\b|\bsell\b|overweight|undervalued/i.test(t), "a word of advice or a view");
  check(E.wholeWords(498765432100) === "498,765,432,100" && E.wholeWords(1234.5) === "1,234.50", "wholeWords");
}

// ---- 3. The board's other cells on an ok row ---------------------------------------------------------------------------
{
  const row = eq.rows.find((r) => r.status === "ok");
  row.avg7 = { v: 101.2, n: 5 };
  row.avg30 = { v: 99.8, n: 21 };
  row.avg365 = { v: 95.4, n: 251, ch: 6.1 };
  row.lo30 = 96.5; row.hi30 = 103.9;
  row.range = { lo: 82.1, hi: 104.6, n: 251, pos: 0.86 };
  const other = eq.rows.find((r) => r.status === "ok" && r !== row);
  check(E.hasWideCells(row) && !E.hasWideCells(other) && !E.hasWideCells({ ...row, status: "not_held" }), "hasWideCells: a row with the cells, one without, one that is not ok");
  const merged = E.withEquities(board, eq);
  const g = merged.groups.find((x) => x.id === "equities");
  check(g && g.lean === false, "with a row that carries the board's other cells, the group stays lean");
  const got = merged.rows.find((r) => r.id === row.id), plain = merged.rows.find((r) => r.id === other.id);
  check(got.avg7.v === 101.2 && got.avg30.n === 21 && got.avg365.ch === 6.1 && got.lo30 === 96.5 && got.hi30 === 103.9 && got.range.pos === 0.86, "the row's cells are the file's");
  check(!("avg7" in plain) && !("range" in plain) && plain.last && plain.moves, "a row without the cells keeps its value and its moves, and gains no cell");
  check(merged.groups.length === board.groups.length + 1 && merged.rows.slice(0, board.rows.length).every((r, i) => r === board.rows[i]), "the board's own groups and rows are no longer as they were");
  check(E.withEquities(board, { ...eq, example: true }).groups.find((x) => x.id === "equities").lean === true, "an example file's group is not lean");
  if (KEEP) save("board.json", eq);
}

if (!KEEP) fs.rmSync(FIX, { recursive: true, force: true });
if (fails.length) { console.log(`FAIL ${fails.length} of ${n}:\n  ${fails.join("\n  ")}`); process.exitCode = 1; }
else console.log(`ok: ${n} checks of the equities list's and board rows' new fields (a fixture of the contract's shape)`);
