// Energy Research Warehouse (ERW) site, session 8901 (chain 507, part C): the four problem sets of the whole country,
// each figure pinned to its committed page file.
//
//   node --import ./scripts/problem-sets-register.mjs scripts/test-problem-sets-country.mjs     (from site/)
//
// For each set: it builds with lib/problems.ts as the live page does; a worked example and six to eight questions; every
// number part carries a pf| key or a calc| of two pf| keys, and every key, recomputed from the file by lib/pagefile.ts,
// gives the figure shown; the guide's order names every question once; no em dash in any word; no typed number in a
// line or an answer of the module's source; the set's page is drawn to HTML with the site's own components and every
// figure is found in it by its key and its text, with its page files named, its decisions block, and no link to a dated
// edition (none holds these sets); the edition pages list no address of a set no edition holds; the index names the page
// files; the hover words and the CSV rows of a pf| figure name its file and its tables. Exit 0 when all hold. No network.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const here = path.dirname(fileURLToPath(import.meta.url));
const site = path.join(here, "..");
const { problemSet, SETS } = await import("../lib/problems.ts");
const { GUIDE, csvOf, figureRows, keyWords, sourceOfKey, tablesOfKey } = await import("../lib/problemkit.ts");
const { parsePf, pfValue } = await import("../lib/pagefile.ts");
const { shown } = await import("../lib/format.ts");
const Live = (await import("../app/learn/problems/[slug]/page.tsx")).default;
const Index = (await import("../app/learn/problems/page.tsx")).default;
const editionPage = await import("../app/learn/problems/[slug]/[edition]/page.tsx");
const teacherPage = await import("../app/learn/problems/[slug]/[edition]/teacher/page.tsx");
const MODULES = {
  "who-trades-with-whom": "who-trades-with-whom", "storm-across-the-country": "storm-across-the-country",
  "under-the-ground-and-in-the-wind": "under-the-ground-and-in-the-wind", "where-energy-goes": "where-energy-goes",
};
const CITES = JSON.parse(fs.readFileSync(path.join(site, "data", "table_citations.json"), "utf-8"));
const cite = (t) => CITES[t];
const DASH = String.fromCharCode(0x2014), EN = String.fromCharCode(0x2013);
const fails = [];
const check = (ok, what) => { if (!ok) fails.push(what); };
const attr = (s) => s.replaceAll("&", "&amp;").replaceAll('"', "&quot;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");

/** A key's value recomputed from the files alone: a pf| key read, a calc| of two such keys combined. */
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

/** Each bracketed array after `<field>: ` in a text (as scripts/test-problemkit.mjs reads lib/problems.ts). */
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

let questions = 0, keys = 0, drawnFound = 0;
const slugs = Object.keys(MODULES);
check(JSON.stringify(SETS.slice(-4).map((s) => s.slug)) === JSON.stringify(slugs), "the four sets come after the five, in order");
check(JSON.stringify(SETS.slice(0, 5).map((s) => s.slug)) === JSON.stringify(["know-your-grid", "prices-and-your-bill", "when-the-grid-broke", "storage-and-taxes", "networks-and-money"]), "the five keep their place");
const editionParams = [...editionPage.generateStaticParams(), ...teacherPage.generateStaticParams()];

for (const slug of slugs) {
  const src = fs.readFileSync(path.join(site, "lib", "problemsets", `${MODULES[slug]}.ts`), "utf-8");
  const mod = await import(`../lib/problemsets/${MODULES[slug]}.ts`);
  check(mod.META.slug === slug && typeof mod.build === "function" && mod.GUIDE_ENTRY, `${slug}: META, GUIDE_ENTRY and build`);
  check(GUIDE[slug] === mod.GUIDE_ENTRY, `${slug}: registered in the guide`);
  const set = await problemSet(slug);
  check(!!set, `${slug}: problemSet builds it`);
  if (!set) continue;
  check(!!set.example, `${slug}: a worked example`);
  check(set.questions.length >= 6 && set.questions.length <= 8, `${slug}: ${set.questions.length} questions, not six to eight`);
  const ids = set.questions.map((q) => q.id);
  check(JSON.stringify([...ids].sort()) === JSON.stringify([...mod.GUIDE_ENTRY.order].sort()) && new Set(mod.GUIDE_ENTRY.order).size === ids.length, `${slug}: the order ${mod.GUIDE_ENTRY.order} against ${ids}`);
  check(JSON.stringify(ids) === JSON.stringify(mod.GUIDE_ENTRY.order), `${slug}: asked in the guide's order`);
  questions += ids.length;
  for (const q of [set.example, ...set.questions]) {
    check(typeof q.q === "string" && q.q.length > 20 && q.why.length > 20 && q.steps.length >= 1 && q.line.length >= 1, `${slug} ${q.id}: words, steps and a line`);
    const words = [q.q, q.why, ...[q.answer, q.line, ...q.steps].flat().filter((p) => typeof p === "string")].join(" ");
    check(!words.includes(DASH) && !words.includes(EN), `${slug} ${q.id}: a dash`);
    for (const part of [q.answer, q.line, ...q.steps].flat()) {
      if (typeof part === "string") continue;
      keys += 1;
      check(/^(pf|calc)\|/.test(part.k), `${slug} ${q.id}: a key that is not pf| or calc|: ${part.k}`);
      const v = recompute(part.k);
      check(v !== undefined && Math.abs(v - part.v) <= 1e-9 * Math.max(1, Math.abs(v)), `${slug} ${q.id}: ${part.k} gives ${v}, the page ${part.v}`);
      check(Number.isFinite(part.v), `${slug} ${q.id}: not a finite figure: ${part.k}`);
    }
  }
  // the module's source: no typed number in a line or an answer, no dash at all
  check(!src.includes(DASH) && !src.includes(EN), `${slug}: a dash in the module`);
  for (const arr of [...arraysAfter(src, "line"), ...arraysAfter(src, "answer")]) {
    const hit = outsideStrings(arr).match(/(?<![\w.$])\d+(\.\d+)?(?![\w])/);
    check(hit === null, `${slug}: a typed number in ${arr.slice(0, 100)}`);
  }
  // the hover and the CSV of a pf| figure name the file and its tables
  const any = set.questions[0].answer.find((p) => typeof p !== "string");
  const file = parsePf(any.k)?.file;
  const words = sourceOfKey(any.k, cite);
  check(!!words && words.includes(`site/data/${file}`), `${slug}: the hover names the page file (${words})`);
  for (const t of tablesOfKey(any.k)) check(words.includes(CITES[t] ?? t), `${slug}: the hover cites ${t}`);
  const rows = figureRows(set.example, set.questions, () => false);
  const csv = csvOf(slug, set.title, rows, "2026-11-19T00:00:00Z", cite);
  check(rows.length > 0 && csv.split("\n").length > rows.length + 3, `${slug}: the CSV`);
  check(rows.every((r) => keyWords(r.key) !== undefined), `${slug}: every key has its words`);
  // the set's page, drawn with the site's own components
  const html = renderToStaticMarkup(await Live({ params: Promise.resolve({ slug }) }));
  check(html.includes(`data-decisions="${slug}"`), `${slug}: the decisions block`);
  check(html.includes("data-page-files"), `${slug}: the page files named`);
  check(!html.includes("data-editions"), `${slug}: a link to an edition that does not hold it`);
  check(html.includes("data-example"), `${slug}: the worked example drawn`);
  check(html.includes("Worked solution") && html.includes("Why it matters"), `${slug}: the worked solutions and why it matters`);
  for (const q of [set.example, ...set.questions]) for (const part of [q.answer, q.line, ...q.steps].flat()) {
    if (typeof part === "string") continue;
    const found = html.includes(`data-check="${attr(part.k)}" data-raw="${String(part.v)}"`) && html.includes(`>${attr(shown(part.v))}</span>`);
    check(found, `${slug} ${q.id}: ${part.k} not drawn`);
    if (found) drawnFound += 1;
  }
  check(!html.includes(DASH), `${slug}: a dash on the page`);
  check(!editionParams.some((p) => p.slug === slug), `${slug}: an edition address for a set no edition holds`);
}
const index = renderToStaticMarkup(Index());
for (const slug of slugs) {
  check(index.includes(`href="/learn/problems/${slug}"`) || index.includes(`/learn/problems/${slug}`), `the index lists ${slug}`);
  check(index.includes(`data-set-files="${slug}"`) && index.includes(`data-no-edition="${slug}"`), `the index: ${slug}'s page files and its no-edition line`);
}
check(editionParams.length === 2 * 5, `the edition pages: ${editionParams.length} addresses, not the five sets' two each`);

if (fails.length) { console.log(`FAIL ${fails.length}:\n  ${fails.slice(0, 40).join("\n  ")}`); process.exitCode = 1; }
else console.log(`ok: ${slugs.length} sets, ${questions} questions and ${slugs.length} examples, ${keys} keyed figures recomputed from their files, ${drawnFound} found on the drawn pages`);
