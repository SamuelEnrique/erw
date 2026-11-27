// Energy Research Warehouse (ERW) site, session 10412 (chain 720, part E): the waiting problem set "A producer beside
// the price of oil" (lib/problemsets/a-producer-beside-the-price-of-oil.ts), every figure pinned to the equities page
// files (site/data/equities/series/<ticker>.json, what a company filed with the SEC, and energy_prices.json).
//
//   node --import ./scripts/problem-sets-register.mjs scripts/test-problem-set-producer.mjs     (from site/)
//
// It holds: the set is a waiting set (in WAITING_SETS, not in SETS, not in the guide, not on the index, in no edition);
// it builds with lib/problems.ts as its page does; a worked example and six questions in the guide's order; every
// number part carries a pf| key or a calc| of two pf| keys and every key, recomputed from the file by lib/pagefile.ts,
// gives the figure shown; every figure is the one its question names, found here again by the period's end, its length
// and the column (this script's search, not the module's), the later filing where a period was filed twice; the
// producer is the one the set's rule names, found here from the list of companies; no share price, index or segment
// line is read (each is held); no dash; no typed number in a line or an answer; no word that takes a side; the page
// drawn to HTML with the site's own components shows every figure by its key and its text, names the page files,
// carries the set's three decisions and links /equities. Exit 0 when all hold. No network. Reads only.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { renderToStaticMarkup } from "react-dom/server";

const here = path.dirname(fileURLToPath(import.meta.url));
const site = path.join(here, "..");
const SLUG = "a-producer-beside-the-price-of-oil";
const { problemSet, SETS, WAITING_SETS, WAITING_GUIDE, WAITING_DECISIONS } = await import("../lib/problems.ts");
const { GUIDE, instructorNote, sourceOfKey, keyWords } = await import("../lib/problemkit.ts");
const { parsePf, pfValue } = await import("../lib/pagefile.ts");
const { shown } = await import("../lib/format.ts");
const mod = await import("../lib/problemsets/a-producer-beside-the-price-of-oil.ts");
const Live = (await import("../app/learn/problems/[slug]/page.tsx")).default;
const livePage = await import("../app/learn/problems/[slug]/page.tsx");
const Index = (await import("../app/learn/problems/page.tsx")).default;
const editionPage = await import("../app/learn/problems/[slug]/[edition]/page.tsx");
const teacherPage = await import("../app/learn/problems/[slug]/[edition]/teacher/page.tsx");
const CITES = JSON.parse(fs.readFileSync(path.join(site, "data", "table_citations.json"), "utf-8"));
const cite = (t) => CITES[t];
const DASH = String.fromCharCode(0x2014), EN = String.fromCharCode(0x2013);
const read = (...p) => fs.readFileSync(path.join(site, ...p), "utf-8");
const json = (...p) => JSON.parse(read(...p));
const fails = [];
let checks = 0;
const check = (ok, what) => { checks += 1; if (!ok) fails.push(what); };
const attr = (s) => s.replaceAll("&", "&amp;").replaceAll('"', "&quot;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
const near = (a, b) => a !== undefined && b !== undefined && Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(a));

function recompute(k) {
  const p = k.split("|");
  if (p[0] === "pf") return parsePf(k) ? pfValue(k) : undefined;
  if (p[0] === "calc" && p.length === 4) {
    const [a, b] = [p[2], p[3]].map((x) => x.replaceAll("~", "|"));
    if (!a.startsWith("pf|") || !b.startsWith("pf|")) return undefined;
    const x = pfValue(a), y = pfValue(b);
    if (x === undefined || y === undefined) return undefined;
    return p[1] === "ratio" ? x / y : p[1] === "diff" ? x - y : p[1] === "pct" ? (x / y) * 100 : undefined;
  }
  return undefined;
}
function arraysAfter(text, field) {
  const out = [];
  for (const m of text.matchAll(new RegExp(`\\b${field}: \\[`, "g"))) {
    let depth = 0, j = m.index + m[0].length - 1, quote = null;
    for (; j < text.length; j += 1) {
      const c = text[j];
      if (quote) { if (c === "\\") j += 1; else if (c === quote) quote = null; continue; }
      if (c === '"' || c === "`" || c === "'") { quote = c; continue; }
      if (c === "[") depth += 1;
      if (c === "]" && --depth === 0) break;
    }
    out.push(text.slice(m.index + m[0].length - 1, j + 1));
  }
  return out;
}
const outsideStrings = (s) => s.replace(/`(?:\\.|[^`\\])*`|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/g, "");
const mine = WAITING_DECISIONS.filter((d) => d.sets.includes(SLUG));

// ---------------------------------------------------------------- a waiting set, and nothing more
check(WAITING_SETS.some((s) => s.slug === SLUG), "the set is a waiting set");
check(!SETS.some((s) => s.slug === SLUG), "the set is in SETS: the index and the edition builder would take it");
check(!(SLUG in GUIDE) && WAITING_GUIDE[SLUG] === mod.GUIDE_ENTRY, "its guide is the waiting guide's, not GUIDE's");
check(!instructorNote().includes(SLUG), "the instructors' note names a waiting set");
const index = renderToStaticMarkup(Index());
check(!index.includes(SLUG) && !index.includes(mod.META.title), "the index lists a waiting set");
const editionParams = [...editionPage.generateStaticParams(), ...teacherPage.generateStaticParams()];
check(!editionParams.some((p) => p.slug === SLUG), "an edition address for a waiting set");
check(livePage.generateStaticParams().some((p) => p.slug === SLUG), "the set's page is not among the pages built");
for (const f of fs.readdirSync(path.join(site, "data", "problem_editions"))) check(!read("data", "problem_editions", f).includes(SLUG), `the dated edition file ${f} names the waiting set`);
check(!read("lib", "release.ts").includes(SLUG), "lib/release.ts names the set: it opens nothing");
check(mine.length === 3 && mine.every((d) => d.sets.length === 1 && d.text && d.def && d.source && d.session), "the set's three decisions, each whole");

// ---------------------------------------------------------------- the set, built as its page builds it
const set = await problemSet(SLUG);
check(!!set && !!set.example, "problemSet builds it, with a worked example");
const ids = set.questions.map((q) => q.id);
check(ids.length === 6 && JSON.stringify(ids) === JSON.stringify(mod.GUIDE_ENTRY.order), `six questions in the guide's order: ${ids}`);
let keys = 0;
const allWords = [];
for (const q of [set.example, ...set.questions]) {
  check(typeof q.q === "string" && q.q.length > 20 && q.why.length > 20 && q.steps.length >= 1 && q.line.length >= 1, `${q.id}: words, steps and a line`);
  const words = [q.q, q.why, ...[q.answer, q.line, ...q.steps].flat().filter((p) => typeof p === "string")].join(" ");
  allWords.push(words);
  check(!words.includes(DASH) && !words.includes(EN), `${q.id}: a dash`);
  check(!/\bundefined\b|\bnull\b|NaN/.test(words), `${q.id}: a word that is no word (${words.match(/\bundefined\b|\bnull\b|NaN/)})`);
  for (const part of [q.answer, q.line, ...q.steps].flat()) {
    if (typeof part === "string") continue;
    keys += 1;
    check(/^(pf|calc)\|/.test(part.k), `${q.id}: a key that is not pf| or calc|: ${part.k}`);
    check(Number.isFinite(part.v) && near(recompute(part.k), part.v), `${q.id}: ${part.k} gives ${recompute(part.k)}, the page ${part.v}`);
    check(keyWords(part.k) !== undefined, `${q.id}: ${part.k} has no words`);
    // every key leads into a company's filed periods or the public energy prices: no share price, index or segment line
    const files = part.k.startsWith("pf|") ? [part.k.split("|")[1]] : part.k.split("|").slice(2).map((x) => x.split("~")[1]);
    const paths = part.k.startsWith("pf|") ? [part.k.split("|")[2]] : part.k.split("|").slice(2).map((x) => x.split("~")[2]);
    check(files.every((f, i) => (/^equities\/series\/[A-Z.-]+\.json$/.test(f) && paths[i].startsWith("quarterly/")) || (f === "equities/energy_prices.json" && paths[i].startsWith("daily/"))), `${q.id}: ${part.k} reads something other than a filed period or an energy price`);
  }
}
const src = read("lib", "problemsets", `${SLUG}.ts`);
check(!src.includes(DASH) && !src.includes(EN), "a dash in the module");
for (const arr of [...arraysAfter(src, "line"), ...arraysAfter(src, "answer")]) check(outsideStrings(arr).match(/(?<![\w.$])\d+(\.\d+)?(?![\w])/) === null, `a typed number in ${arr.slice(0, 100)}`);
// "sells" is what a producer does with its fuel and is no advice; to buy or sell a share, a stock or the company is
const SIDES = /\b(better|worse|beats|beat|wins|outperform\w*|should|recommend\w*|cheap|expensive|undervalued|overvalued|invest\w*|(buy|sell|hold)s? (the |its |a )?(share|stock|compan)\w*)\b/i;
check(!SIDES.test(allWords.join(" ")), `a word that takes a side or gives advice (${allWords.join(" ").match(SIDES)?.[0]})`);
check(!/share price|stock price|market value|return/i.test(allWords.join(" ")), "a question reads a share price, which is held");

// ---------------------------------------------------------------- each figure is the one its question names (this script's own search of the files)
const A = mod.TICKER, B = mod.SECOND, Q3 = mod.Q3, Q2 = mod.Q2, QY = mod.Q3_BEFORE;
const seriesOf = (t) => json("data", "equities", "series", `${t}.json`);
const rowsOf = (doc) => doc.quarterly.map((r) => Object.fromEntries(doc.quarterly_columns.map((n, i) => [n, r[i]])));
/** The later filing's row of a period that holds a column; months null for a figure at a day. */
const pick = (rows, end, months, column) => rows.filter((r) => r.period_end === end && (months === null || r.months === months) && typeof r[column] === "number").sort((x, y) => String(y.filed ?? "").localeCompare(String(x.filed ?? "")))[0];
const rowsA = rowsOf(seriesOf(A)), rowsB = rowsOf(seriesOf(B));
const f = (rows, end, months, column) => { const r = pick(rows, end, months, column); check(!!r, `no row for ${column}, ${months} months to ${end}`); return r?.[column]; };
const prices = json("data", "equities", "energy_prices.json");
const p = (id, day) => { const hit = (prices.daily[id] ?? []).filter((r) => r[0] === day); check(hit.length === 1 && typeof hit[0][1] === "number", `${hit.length} rows of ${id} on ${day}`); return hit[0]?.[1]; };
const answerOf = (id) => [set.example, ...set.questions].find((q) => q.id === id).answer.filter((x) => typeof x !== "string").map((x) => x.v);
const same = (id, want) => { const got = answerOf(id); check(got.length === want.length && want.every((w, i) => near(w, got[i])), `${id}: the answer's figures ${got} against the files' ${want}`); };
const r3 = f(rowsA, Q3, 3, "revenue"), r2 = f(rowsA, Q2, 3, "revenue"), ry = f(rowsA, QY, 3, "revenue");
const w3 = p("wti", Q3), w2 = p("wti", Q2), wy = p("wti", QY);
same("px", [r3, r2, (r3 / r2) * 100]);
same("p1", [w3, w2, (w3 / w2) * 100, (r3 / r2) * 100]);
const n3 = f(rowsA, Q3, 3, "net_income");
same("p2", [n3, r3, (n3 / r3) * 100]);
const c9 = f(rowsA, Q3, 9, "capex"), r9 = f(rowsA, Q3, 9, "revenue");
same("p3", [c9, r9, (c9 / r9) * 100]);
const d3 = f(rowsA, Q3, null, "debt"), d0 = f(rowsA, QY, null, "debt");
same("p4", [d3, d0, d3 - d0]);
same("p5", [r3, ry, (r3 / ry) * 100, w3, wy, (w3 / wy) * 100]);
const b3 = f(rowsB, Q3, 3, "revenue"), b2 = f(rowsB, Q2, 3, "revenue"), g3 = p("henry_hub", Q3), g2 = p("henry_hub", Q2);
same("p6", [b3, b2, (b3 / b2) * 100, g3, g2, (g3 / g2) * 100, (r3 / r2) * 100, (w3 / w2) * 100]);
// what the set says of the files is so: the nine months' spending and revenue are one row; debt is one figure a period end
check(pick(rowsA, Q3, 9, "capex") === pick(rowsA, Q3, 9, "revenue"), "p3: the nine months' capital spending and revenue are not the same row");
for (const end of [Q3, QY]) check(new Set(rowsA.filter((r) => r.period_end === end && typeof r.debt === "number").map((r) => r.debt)).size === 1, `p4: the rows of the period to ${end} hold more than one figure of debt`);
const q4 = set.questions.find((q) => q.id === "p4");
check(q4.answer.some((x) => typeof x === "string" && x.includes(d3 > d0 ? "the debt rose" : d3 < d0 ? "the debt fell" : "the debt is the same")), "p4: the words say which way the debt moved, as the files have it");
// the producer is the one the rule names: of the segment's companies whose file holds every period the set reads, the largest revenue of the quarter
const list = json("data", "equities", "index.json");
const holds = (rows) => [[Q3, 3, "revenue"], [Q2, 3, "revenue"], [QY, 3, "revenue"], [Q3, 3, "net_income"], [Q3, 9, "capex"], [Q3, 9, "revenue"], [Q3, null, "debt"], [QY, null, "debt"]].every(([e, m, c]) => !!pick(rows, e, m, c));
const ranked = list.companies.filter((c) => c.fundamentals_status === "shown" && (c.segments ?? []).includes(mod.SEGMENT))
  .map((c) => ({ id: c.id, rows: rowsOf(json("data", "equities", ...c.file.split("/"))) })).filter((c) => holds(c.rows))
  .map((c) => ({ id: c.id, revenue: pick(c.rows, Q3, 3, "revenue").revenue })).sort((x, y) => y.revenue - x.revenue);
check(ranked.length >= 2 && ranked[0].id === A && ranked[0].revenue > ranked[1].revenue, `the producer is not the rule's: ${ranked.slice(0, 3).map((c) => `${c.id} ${c.revenue}`).join(", ")}`);
const second = list.companies.find((c) => c.id === B);
check(!!second && (second.segments ?? []).includes(mod.SEGMENT) && second.fundamentals_status === "shown", "the second producer is not a company of the segment with filed figures");
const segment = (list.segments ?? []).find((s) => s.id === mod.SEGMENT);
check(!!segment && src.includes(`"${segment.label}"`), "the module names the segment by the list's own label");

// ---------------------------------------------------------------- the page, drawn with the site's own components
const html = renderToStaticMarkup(await Live({ params: Promise.resolve({ slug: SLUG }) }));
check(html.includes(`data-waiting-set="${SLUG}"`), "the page is marked as a waiting set's");
check(html.includes(`data-decisions="${SLUG}"`) && html.includes('data-decision-count="3"'), "the decisions block with the set's three");
for (const d of mine) check(html.includes(`data-decision="${d.key}"`), `the decision ${d.key} not drawn`);
for (const d of WAITING_DECISIONS.filter((x) => !x.sets.includes(SLUG))) check(!html.includes(`data-decision="${d.key}"`), `another waiting set's decision ${d.key} drawn`);
check(html.includes("data-page-files") && html.includes(`site/data/equities/series/${A}.json`) && html.includes("site/data/equities/energy_prices.json"), "the page files named");
check(!html.includes("data-editions"), "a link to an edition, which does not hold it");
check(html.includes("data-example") && html.includes("Worked solution") && html.includes("Why it matters"), "the worked example, the solutions and why it matters");
check((html.match(/data-can/g) ?? []).length === 1 && html.includes(attr(mod.GUIDE_ENTRY.can).replaceAll("'", "&#x27;")), "the line of what a student can do, once");
check(html.includes(`/equities?a=${A}`), "the page the set is of is linked");
let drawn = 0;
for (const q of [set.example, ...set.questions]) for (const part of [q.answer, q.line, ...q.steps].flat()) {
  if (typeof part === "string") continue;
  const found = html.includes(`data-check="${attr(part.k)}" data-raw="${String(part.v)}"`) && html.includes(`>${attr(shown(part.v))}</span>`);
  check(found, `${q.id}: ${part.k} not drawn`);
  if (found) drawn += 1;
}
check(!html.includes(DASH), "a dash on the page");
const any = set.questions[1].answer.find((x) => typeof x !== "string");
const hover = sourceOfKey(any.k, cite);
check(!!hover && hover.includes(`site/data/equities/series/${A}.json`), `the hover names the page file (${hover})`);
// the other waiting set and a listed set are untouched
const other = renderToStaticMarkup(await Live({ params: Promise.resolve({ slug: "a-forecasts-report-card" }) }));
check(other.includes('data-decision-count="3"') && !mine.some((d) => other.includes(`data-decision="${d.key}"`)), "the forecast's waiting set carries this set's choices");
const listed = renderToStaticMarkup(await Live({ params: Promise.resolve({ slug: "where-energy-goes" }) }));
check(!listed.includes("data-waiting-set") && !WAITING_DECISIONS.some((d) => listed.includes(`data-decision="${d.key}"`)), "a listed set's page carries a waiting set's mark or choices");

if (fails.length) { console.log(`FAIL ${fails.length} of ${checks}:\n  ${fails.slice(0, 40).join("\n  ")}`); process.exitCode = 1; }
else console.log(`ok: ${checks} checks; a waiting set, ${ids.length} questions and 1 example, ${keys} keyed figures recomputed from the files, ${drawn} found on the drawn page`);
