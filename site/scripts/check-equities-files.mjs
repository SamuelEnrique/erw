// Energy Research Warehouse (ERW) site, session 10402 (chain 720, part D): /equities and the board's equities group
// drawn and computed by the site's own code on the equities page files, and every figure set beside the file it names.
// Without a build.
//   node --import ./scripts/events-page-register.mjs scripts/check-equities-files.mjs [folder of the files]
// The folder is site/data/equities unless one is given (a copy of the files from another branch, before they land).
// Drawn: the page as it opens, with each energy price chosen, with each thing the list can draw as A (and the next as
// B), over two windows. A figure on the page carries data-check="pf|equities/<file>|<path>" and data-raw: the value at
// that path of that file must be the raw value. The board's group: every row of the file is a row of the board, a row
// with a value carries the file's value, a row without one carries no figure.
// Exit 0 when every figure agrees and no page prints "undefined", "NaN" or "null"; 1 otherwise; 0 with a line when the
// files are the contract's examples or are not there (nothing to check).
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dir = path.resolve(process.argv[2] ?? path.join(SITE, "data", "equities"));
const read = (name) => JSON.parse(fs.readFileSync(path.join(dir, ...name.split("/")), "utf8"));
if (!fs.existsSync(path.join(dir, "index.json"))) { console.log(`no index.json in ${dir}: the equities files are not there, nothing to check`); process.exit(0); }
const list = read("index.json");
if (list.example === true) { console.log(`the files in ${dir} are the contract's examples (every value null): nothing to check`); process.exit(0); }
process.env.ERW_EQUITIES_DIR = dir;
const { EquitiesView } = await import("../app/equities/view.tsx");
const E = await import("../lib/equities.ts");
const B = await import("../lib/board.ts");
const cache = new Map();
const doc = (name) => { if (!cache.has(name)) cache.set(name, read(name)); return cache.get(name); };
const at = (name, p) => p.split("/").reduce((v, seg) => (v === undefined || v === null ? undefined : v[/^\d+$/.test(seg) && Array.isArray(v) ? Number(seg) : decodeURIComponent(seg)]), doc(name));
const text = (html) => html.replace(/<title>[^<]*<\/title>/g, " ").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&amp;/g, "&").replace(/\s+/g, " ");

let pages = 0, figures = 0;
const wrong = [], bad = [];
function page(query) {
  const html = renderToStaticMarkup(h(EquitiesView, { query }));
  pages++;
  const junk = text(html).match(/.{0,50}(\bundefined\b|\bNaN\b|\bnull\b|\[object Object\]|Infinity).{0,50}/);
  if (junk) bad.push(`${JSON.stringify(query)}: ${junk[0]}`);
  for (const m of html.matchAll(/data-check="pf\|equities\/([^|"]+)\|([^"]+)" data-raw="([^"]*)"/g)) {
    figures++;
    const v = at(m[1], m[2]);
    if (typeof v !== "number" || String(v) !== m[3]) wrong.push(`${JSON.stringify(query)}: ${m[1]} ${m[2]} page ${m[3]} file ${v}`);
  }
  return html;
}
const prices = fs.existsSync(path.join(dir, "energy_prices.json")) ? read("energy_prices.json") : null;
const picks = E.picksOf(list);
const opens = page({});
for (const win of ["1y", "all"]) {
  for (const p of prices?.series ?? []) page({ p: p.id, win });
  picks.forEach((x, i) => page({ a: x.id, ...(picks[i + 1] ? { b: picks[i + 1].id } : {}), ...(prices?.series[0] ? { p: prices.series[0].id } : {}), win }));
}
// session 10408 (the SEC's company figures, in the files since 27 November 2026): each company with the other filed
// figures and lengths of period chosen, beside the next company, so that the figure above each chart and the newest
// period's columns are set beside the file too; and the figure's line computed here again from the file's own rows
let lines = 0, points = 0;
const companies = picks.filter((x) => x.kind === "company");
const again = (rows, cols, col, per) => {
  // the rule in words (lib/equities.ts figureLine), written a second time: a sum is taken from the rows of exactly
  // that length; a figure at a period's end from every row ("3") or the annual reports' rows ("12"); one value a
  // period end, the later filing's
  const at = (n) => cols.indexOf(n), atEnd = col === "debt" || col === "shares_outstanding";
  const best = new Map();
  for (const r of rows) {
    const v = r[at(col)], end = r[at("period_end")];
    if (typeof v !== "number" || typeof end !== "string") continue;
    if (atEnd ? per === "12" && !String(r[at("form")] ?? "").startsWith("10-K") : r[at("months")] !== Number(per)) continue;
    const had = best.get(end);
    if (!had || String(r[at("filed")] ?? "") > had.filed) best.set(end, { filed: String(r[at("filed")] ?? ""), v });
  }
  return [...best.keys()].sort().map((end) => `${end}=${best.get(end).v}`).join(" ");
};
companies.forEach((x, i) => {
  const s = doc(x.file);
  const filings = E.filingsOf(s);
  for (const [fig, per] of [["net_income", "12"], ["capex", "12"], ["debt", "3"], ["shares_outstanding", "12"], ["revenue", "3"], ["revenue", "12"], ["net_income", "3"], ["capex", "3"], ["debt", "12"], ["shares_outstanding", "3"]]) {
    const line = E.figureLine(filings, fig, per);
    lines++; points += line.length;
    if (line.map((p) => `${p.f.period_end}=${p.v}`).join(" ") !== again(s.quarterly ?? [], s.quarterly_columns ?? [], fig, per)) wrong.push(`${x.id} ${fig} by ${per} months: the line differs from the file's rows read again`);
    if (i % 4 === 0 || fig === "net_income" || fig === "debt") {
      const html = page({ a: x.id, ...(companies[i + 1] ? { b: companies[i + 1].id } : {}), fig, per });
      const n = /data-eq-figure="a" data-eq-points="(\d+)"/.exec(html)?.[1];
      if (list.companies.find((c) => c.id === x.id)?.fundamentals_status === "shown" && Number(n) !== line.length) wrong.push(`${x.id} ${fig} by ${per} months: the page draws ${n} periods, the file holds ${line.length}`);
    }
  }
});
console.log(`the filed figures: ${companies.length} companies, ${lines} lines of one figure over the periods filed (${points} points), each computed twice from the file's rows`);
const state = /data-eq-state="([^"]+)"/.exec(opens)?.[1];
console.log(`the list: ${list.segments.length} segments, ${list.companies.length} companies, ${list.indices.length} indices, ${(list.segment_series ?? []).length} segment lines; ${picks.length} things to draw; ${prices ? `${prices.series.length} energy prices, ${prices.series.filter((s) => s.status === "shown").length} shown` : "no energy prices file"}`);
console.log(`the page as it opens: state ${state}; ${/data-eq-price="([^"]+)"/.exec(opens)?.[1] ? `the energy price ${/data-eq-price="([^"]+)"/.exec(opens)[1]} drawn alone` : `${(opens.match(/data-eq-line=/g) ?? []).length} line(s)`}; blanks: ${[...opens.matchAll(/data-eq-blank="[^"]*"[^>]*>([^<]*)</g)].map((m) => m[1].trim()).join(" | ") || "none"}`);
console.log(`pages drawn: ${pages}; figures with a key into a file: ${figures}; differing from the file: ${wrong.length}; "undefined", "NaN" or "null" on a page: ${bad.length}`);
// the board's group
if (fs.existsSync(path.join(dir, "board.json"))) {
  const eq = read("board.json");
  const board = JSON.parse(fs.readFileSync(path.join(SITE, "data", "board.json"), "utf8"));
  const merged = E.withEquities(board, eq);
  const mine = merged.rows.slice(board.rows.length);
  let rowsWrong = 0;
  eq.rows.forEach((r, i) => {
    const m = mine[i];
    const ok = m && m.id === r.id && (r.status === "ok" && r.last ? m.status === "ok" && m.last.v === r.last.v && m.last.t === r.last.t && JSON.stringify(m.moves) === JSON.stringify(r.moves) : m.status !== "ok" && !m.last && !m.moves && !m.spark);
    if (!ok) { rowsWrong++; wrong.push(`board row ${r.id}`); }
  });
  const same = JSON.stringify(merged.rows.slice(0, board.rows.length)) === JSON.stringify(board.rows) && JSON.stringify(merged.groups.slice(0, -1)) === JSON.stringify(board.groups);
  if (!same) wrong.push("the board's own rows or groups changed");
  const by = {};
  for (const m of mine) by[m.status] = (by[m.status] ?? 0) + 1;
  console.log(`the board's group: ${mine.length} rows after the board's own ${board.rows.length} (${JSON.stringify(by)}); differing from the file: ${rowsWrong}; the board's own rows and groups as they were: ${same}; the board's own checks of its file: ${B.boardFileChecks(B.holdRows(merged, [])).filter((c) => !c.ok).length} failing, ${B.boardFileChecks(B.holdRows(board, [])).filter((c) => !c.ok).length} without the group`);
}
for (const w of wrong.slice(0, 20)) console.log(`  DIFFERS ${w}`);
for (const w of bad.slice(0, 20)) console.log(`  BAD ${w}`);
process.exitCode = wrong.length || bad.length ? 1 : 0;
