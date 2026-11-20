// Energy Research Warehouse (ERW) site, session 8901 (chain 507, part C): the figures of the four problem sets of the
// whole country as the site's own code builds them (lib/problems.ts), for the replication to compare with its own
// (replication/problem_sets/replicate_country.py --compare <file>).
//
//   node --import ./scripts/tsx-register.mjs scripts/problem-sets-country-figures.mjs <out.json>      (from site/)
//
// Writes { <slug>: { <question id>: { answer: [values of the answer's figures], all: [values of every figure of the
// answer, the line and the steps] } } }, the worked example included. Reads the committed page files only.
import fs from "node:fs";

const SLUGS = ["who-trades-with-whom", "storm-across-the-country", "under-the-ground-and-in-the-wind", "where-energy-goes", "your-own-balancing-authority"];  // session 8905: the fifth
const out = process.argv[2];
if (!out) { console.error("usage: problem-sets-country-figures.mjs <out.json>"); process.exitCode = 2; }
else {
  const { problemSet } = await import("../lib/problems.ts");
  const figs = (parts) => parts.filter((p) => typeof p !== "string").map((p) => p.v);
  const res = {};
  for (const slug of SLUGS) {
    const set = await problemSet(slug);
    res[slug] = {};
    for (const q of [set.example, ...set.questions].filter(Boolean)) res[slug][q.id] = { answer: figs(q.answer), all: figs([...q.answer, ...q.line, ...q.steps.flat()]) };
  }
  fs.writeFileSync(out, JSON.stringify(res, null, 1) + "\n");
  console.log(`${SLUGS.length} sets, ${Object.values(res).reduce((a, s) => a + Object.keys(s).length, 0)} questions and examples -> ${out}`);
}
