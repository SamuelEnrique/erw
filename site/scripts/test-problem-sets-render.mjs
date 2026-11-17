// Energy Research Warehouse (ERW) site, session 7534 (chain 304): the problem sets' decisions block drawn to HTML with the
// site's own code, and held to the method note's list.
//   node --import ./scripts/problem-sets-register.mjs scripts/test-problem-sets-render.mjs
// Checks: every set has its block, each choice with its default, source and session in a hover tip; the index draws
// them all; every key is in docs/methods/problem_sets.md's section "The decisions", and no key there is missing here;
// no em dash in the words. Exit 0 when all hold, 1 otherwise. No network.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const here = path.dirname(fileURLToPath(import.meta.url));
const { PROBLEM_DECISIONS, ProblemDecisions } = await import("../app/learn/problems/Decisions.tsx");
const { SETS } = await import("../lib/problems.ts");
const fails = [];
const check = (ok, what) => { if (!ok) fails.push(what); };

for (const s of SETS) {
  const html = renderToStaticMarkup(h(ProblemDecisions, { slug: s.slug }));
  const want = PROBLEM_DECISIONS.filter((d) => d.sets.includes(s.slug));
  check(html.includes(`data-decisions="${s.slug}"`), `${s.slug}: no block`);
  check(want.length >= 2, `${s.slug}: fewer than two choices`);
  check(html.includes(`data-decision-count="${want.length}"`), `${s.slug}: the count`);
  for (const d of want) {
    for (const mark of ["data-decision", "data-decision-default", "data-decision-source", "data-decision-session"]) check(html.includes(`${mark}="${d.key}"`), `${s.slug} ${d.key}: ${mark}`);
  }
  for (const d of PROBLEM_DECISIONS.filter((x) => !x.sets.includes(s.slug))) check(!html.includes(`data-decision="${d.key}"`), `${s.slug}: ${d.key} drawn on a set it is not of`);
}
const all = renderToStaticMarkup(h(ProblemDecisions, {}));
check(all.includes(`data-decision-count="${PROBLEM_DECISIONS.length}"`), "the index: the count");
check(new Set(PROBLEM_DECISIONS.map((d) => d.key)).size === PROBLEM_DECISIONS.length, "a key twice");
check(PROBLEM_DECISIONS.every((d) => d.sets.every((x) => SETS.some((s) => s.slug === x))), "a set that does not exist");
const dash = String.fromCharCode(0x2014);
check(!all.includes(dash), "an em dash in the words");

const note = fs.readFileSync(path.join(here, "..", "..", "docs", "methods", "problem_sets.md"), "utf-8");
const sec = note.slice(note.indexOf("## The decisions"));
check(note.includes("## The decisions"), "the note has no section 'The decisions'");
const noted = [...sec.split(/\n## /)[0].matchAll(/^\| `([a-z0-9-]+)` \|/gm)].map((m) => m[1]);
check(JSON.stringify([...noted].sort()) === JSON.stringify(PROBLEM_DECISIONS.map((d) => d.key).sort()), `the note's keys ${noted.join(",")} are not the block's`);

if (fails.length) { console.log(`FAIL ${fails.length}:\n  ${fails.join("\n  ")}`); process.exitCode = 1; }
else console.log(`ok: ${SETS.length} sets, ${PROBLEM_DECISIONS.length} choices, the note's list equal`);
