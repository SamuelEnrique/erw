// Session 10236: the site's own gate on the niche (lib/thesis/niche.ts: gate, judge with no model, forcedOf) on the
// inputs of gate_inputs.json, written to gate_site.json for thesis.py to set beside its restatement. No model is asked:
// judge is given no ask function. Run from site/: node --import ../runs/c10236/register.mjs ../runs/c10236/gate_site.mjs
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const site = process.cwd();
const N = await import(pathToFileURL(path.join(site, "lib", "thesis", "niche.ts")).href);
const inputs = JSON.parse(fs.readFileSync(path.join(site, "..", "runs", "c10236", "gate_inputs.json"), "utf-8"));
const curated = [...N.TABLE.flatMap((t) => t.suggestions), ...N.DEFAULT_SUGGESTIONS, ...N.NICHE_EXAMPLES];
const out = [];
for (const s of [...inputs, ...curated]) {
  const g = N.gate(s);
  const d = await N.judge(s, null);
  out.push({ input: s, verdict: g.verdict, why: g.why, topic: g.topic, ok: d.ok, by: d.by, suggestions: d.suggestions.length });
}
fs.writeFileSync(path.join(site, "..", "runs", "c10236", "gate_site.json"), JSON.stringify(out, null, 1));
console.log(`gate_site.json: ${out.length} inputs (${inputs.length} typed, ${curated.length} curated)`);
