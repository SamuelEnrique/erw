// Energy Research Warehouse (ERW) site, session 10404 (chain 720, part E): the waiting problem set "A forecast's report
// card" (lib/problemsets/a-forecasts-report-card.ts), every figure pinned to site/data/predict/scores.json.
//
//   node --import ./scripts/problem-sets-register.mjs scripts/test-problem-set-forecast.mjs     (from site/)
//
// It holds: the set is a waiting set (in WAITING_SETS, not in SETS, not in the guide, not on the index, in no edition,
// with no data.csv); it builds with lib/problems.ts as its page does; a worked example and six questions in the guide's
// order; every number part carries a pf| key or a calc| of two pf| keys and every key, recomputed from the file by
// lib/pagefile.ts, gives the figure shown; every figure read from the file is the one the question names, found here
// again by the row's own place, method, cut and key (this script's search, not the module's); the hours of the day with
// the largest and the smallest error are the file's; no dash; no typed number in a line or an answer; the page drawn to
// HTML with the site's own components shows every figure by its key and its text, names the page file, carries the
// set's three decisions and links /forecast. Exit 0 when all hold. No network. Reads only.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { renderToStaticMarkup } from "react-dom/server";

const here = path.dirname(fileURLToPath(import.meta.url));
const site = path.join(here, "..");
const SLUG = "a-forecasts-report-card";
const { problemSet, SETS, WAITING_SETS, WAITING_GUIDE, WAITING_DECISIONS } = await import("../lib/problems.ts");
const { GUIDE, instructorNote, sourceOfKey, keyWords } = await import("../lib/problemkit.ts");
const { parsePf, pfValue } = await import("../lib/pagefile.ts");
const { shown } = await import("../lib/format.ts");
const mod = await import("../lib/problemsets/a-forecasts-report-card.ts");
const Live = (await import("../app/learn/problems/[slug]/page.tsx")).default;
const livePage = await import("../app/learn/problems/[slug]/page.tsx");
const Index = (await import("../app/learn/problems/page.tsx")).default;
const editionPage = await import("../app/learn/problems/[slug]/[edition]/page.tsx");
const teacherPage = await import("../app/learn/problems/[slug]/[edition]/teacher/page.tsx");
const CITES = JSON.parse(fs.readFileSync(path.join(site, "data", "table_citations.json"), "utf-8"));
const cite = (t) => CITES[t];
const DASH = String.fromCharCode(0x2014), EN = String.fromCharCode(0x2013);
const read = (...p) => fs.readFileSync(path.join(site, ...p), "utf-8");
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
check(/for \(const meta of SETS\)/.test(read("scripts", "build-problem-edition.mjs")), "the edition builder no longer freezes SETS alone");
check(read("app", "learn", "problems", "[slug]", "data.csv", "route.ts").includes("const meta = SETS.find((s) => s.slug === slug);"), "the data.csv route no longer reads SETS alone");
for (const f of fs.readdirSync(path.join(site, "data", "problem_editions"))) check(!read("data", "problem_editions", f).includes(SLUG), `the dated edition file ${f} names the waiting set`);
check(!read("lib", "release.ts").includes(SLUG), "lib/release.ts names the set: it opens nothing");
check(WAITING_DECISIONS.length === 3 && WAITING_DECISIONS.every((d) => d.sets.length === 1 && d.sets[0] === SLUG && d.text && d.def && d.source && d.session), "the set's three decisions, each whole");

// ---------------------------------------------------------------- the set, built as its page builds it
const set = await problemSet(SLUG);
check(!!set && !!set.example, "problemSet builds it, with a worked example");
const ids = set.questions.map((q) => q.id);
check(ids.length === 6 && JSON.stringify(ids) === JSON.stringify(mod.GUIDE_ENTRY.order), `six questions in the guide's order: ${ids}`);
let keys = 0;
for (const q of [set.example, ...set.questions]) {
  check(typeof q.q === "string" && q.q.length > 20 && q.why.length > 20 && q.steps.length >= 1 && q.line.length >= 1, `${q.id}: words, steps and a line`);
  const words = [q.q, q.why, ...[q.answer, q.line, ...q.steps].flat().filter((p) => typeof p === "string")].join(" ");
  check(!words.includes(DASH) && !words.includes(EN), `${q.id}: a dash`);
  check(!/\bundefined\b|\bnull\b|NaN/.test(words), `${q.id}: a word that is no word (${words.match(/\bundefined\b|\bnull\b|NaN/)})`);
  for (const part of [q.answer, q.line, ...q.steps].flat()) {
    if (typeof part === "string") continue;
    keys += 1;
    check(/^(pf|calc)\|/.test(part.k), `${q.id}: a key that is not pf| or calc|: ${part.k}`);
    check(Number.isFinite(part.v) && near(recompute(part.k), part.v), `${q.id}: ${part.k} gives ${recompute(part.k)}, the page ${part.v}`);
    check(keyWords(part.k) !== undefined, `${q.id}: ${part.k} has no words`);
  }
}
const src = read("lib", "problemsets", "a-forecasts-report-card.ts");
check(!src.includes(DASH) && !src.includes(EN), "a dash in the module");
for (const arr of [...arraysAfter(src, "line"), ...arraysAfter(src, "answer")]) check(outsideStrings(arr).match(/(?<![\w.$])\d+(\.\d+)?(?![\w])/) === null, `a typed number in ${arr.slice(0, 100)}`);
check(!/\b(better|worse|beats|beat|wins|outperform\w*|accurate|should|recommend\w*)\b/i.test([set.example, ...set.questions].map((q) => [q.q, q.why, ...[q.answer, q.line, ...q.steps].flat().filter((p) => typeof p === "string")].join(" ")).join(" ")), "a word that takes a side or gives advice");

// ---------------------------------------------------------------- each figure is the one its question names (this script's own search of the file)
const file = JSON.parse(read("data", "predict", "scores.json"));
const col = Object.fromEntries(file.rows_columns.map((n, i) => [n, i]));
const row = (place, method, cut, key = "") => {
  const hit = file.rows.filter((r) => r[col.place] === place && r[col.series] === "demand" && r[col.method] === method && r[col.cut] === cut && String(r[col.key] ?? "") === key);
  check(hit.length === 1, `${hit.length} rows of the file for ${place}, ${method}, ${cut}, ${key}`);
  return hit[0] ?? [];
};
const A = mod.PLACE, B = mod.SECOND;
const answerOf = (id) => [set.example, ...set.questions].find((q) => q.id === id).answer.filter((p) => typeof p !== "string").map((p) => p.v);
const same = (id, want) => { const got = answerOf(id); check(got.length === want.length && want.every((w, i) => near(w, got[i])), `${id}: the answer's figures ${got} against the file's ${want}`); };
const m = (place, method, cut, key) => row(place, method, cut, key)[col.mape], e = (place, method, cut) => row(place, method, cut)[col.mae], n = (place, method, cut) => row(place, method, cut)[col.hours];
same("fx", [m(A, "erw", "all"), m(A, "operator", "all"), m(A, "erw", "all") - m(A, "operator", "all")]);
same("f1", [e(A, "erw", "last_2_years"), e(A, "operator", "last_2_years"), e(A, "erw", "last_2_years") / e(A, "operator", "last_2_years")]);
same("f2", [m(A, "yesterday", "all"), m(A, "week_ago", "all"), m(A, "week_ago", "all") - m(A, "yesterday", "all")]);
const hoursOfDay = Array.from({ length: 24 }, (_, h) => m(A, "erw", "hour", String(h)));
check(hoursOfDay.every((v) => typeof v === "number" && Number.isFinite(v)), "the file holds the 24 hours of the day for the place");
const top = Math.max(...hoursOfDay), low = Math.min(...hoursOfDay);
same("f3", [top, low, top / low]);
const q3 = set.questions.find((q) => q.id === "f3");
const hh = (h) => `${String(h).padStart(2, "0")}:00`;
check(q3.answer.some((p) => typeof p === "string" && p.includes(`Largest at ${hh(hoursOfDay.indexOf(top))}`)) && q3.answer.some((p) => typeof p === "string" && p.includes(`smallest at ${hh(hoursOfDay.indexOf(low))}`)), "f3: the hours named are the file's largest and smallest, the first on a tie");
same("f4", [m(A, "erw", "top10"), m(A, "operator", "top10"), m(A, "erw", "top10") - m(A, "operator", "top10"), m(A, "erw", "all")]);
same("f5", [m(B, "erw", "all"), m(B, "operator", "all"), m(B, "erw", "all") - m(B, "operator", "all"), m(A, "erw", "all") - m(A, "operator", "all")]);
same("f6", [n(A, "erw", "all"), n(A, "erw", "last_2_years"), (n(A, "erw", "last_2_years") / n(A, "erw", "all")) * 100]);
// two methods of a row are scored on the same hours, as the set says
for (const [place, cut] of [[A, "all"], [A, "last_2_years"], [A, "top10"], [B, "all"]]) check(n(place, "erw", cut) === n(place, "operator", cut), `${place}, ${cut}: the two forecasts are scored on different hours`);
check(n(A, "yesterday", "all") === n(A, "week_ago", "all"), "the two rules are scored on different hours");
check(q3 && set.example.q.includes(`${file.span.demand.first_day} to ${file.span.demand.last_day}`), "the worked example names the file's own span of days");

// ---------------------------------------------------------------- the page, drawn with the site's own components
const html = renderToStaticMarkup(await Live({ params: Promise.resolve({ slug: SLUG }) }));
check(html.includes(`data-waiting-set="${SLUG}"`), "the page is marked as a waiting set's");
check(html.includes(`data-decisions="${SLUG}"`) && html.includes('data-decision-count="3"'), "the decisions block with the set's three");
for (const d of WAITING_DECISIONS) check(html.includes(`data-decision="${d.key}"`), `the decision ${d.key} not drawn`);
check(html.includes("data-page-files") && html.includes("site/data/predict/scores.json"), "the page file named");
check(!html.includes("data-editions"), "a link to an edition, which does not hold it");
check(html.includes("data-example") && html.includes("Worked solution") && html.includes("Why it matters"), "the worked example, the solutions and why it matters");
check((html.match(/data-can/g) ?? []).length === 1 && html.includes(attr(mod.GUIDE_ENTRY.can).replaceAll("'", "&#x27;")), "the line of what a student can do, once");
check(html.includes('href="/forecast"') || html.includes("/forecast"), "the page the set is of is linked");
let drawn = 0;
for (const q of [set.example, ...set.questions]) for (const part of [q.answer, q.line, ...q.steps].flat()) {
  if (typeof part === "string") continue;
  const found = html.includes(`data-check="${attr(part.k)}" data-raw="${String(part.v)}"`) && html.includes(`>${attr(shown(part.v))}</span>`);
  check(found, `${q.id}: ${part.k} not drawn`);
  if (found) drawn += 1;
}
check(!html.includes(DASH), "a dash on the page");
const any = set.questions[0].answer.find((p) => typeof p !== "string");
const hover = sourceOfKey(any.k, cite);
check(!!hover && hover.includes("site/data/predict/scores.json"), `the hover names the page file (${hover})`);
// a set the index lists is untouched by the waiting one: its page still has its own decisions and no waiting mark
const other = renderToStaticMarkup(await Live({ params: Promise.resolve({ slug: "where-energy-goes" }) }));
check(!other.includes("data-waiting-set") && !WAITING_DECISIONS.some((d) => other.includes(`data-decision="${d.key}"`)), "a listed set's page carries the waiting set's mark or choices");

if (fails.length) { console.log(`FAIL ${fails.length} of ${checks}:\n  ${fails.slice(0, 40).join("\n  ")}`); process.exitCode = 1; }
else console.log(`ok: ${checks} checks; 1 waiting set, ${ids.length} questions and 1 example, ${keys} keyed figures recomputed from the file, ${drawn} found on the drawn page`);
