// Session 11407 (chain 770, part C), the ruling readied for finding 7 of docs/reviews/ai-energy-model-audit-2026-11-26.md:
// the page's own measures() and the rows each choice of "What is measured" shows (ofMeasure when the module has it, as
// the page calls it; x_measures equal to the choice otherwise, as origin/main's page filters). Prints one JSON line.
//   node tests/ready_ai_energy_filter_groups_measures.mjs [path to aienergy.ts]
import fs from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const lib = process.argv[2] ? path.resolve(process.argv[2]) : path.join(root, "site", "lib", "aienergy.ts");
const A = await import(pathToFileURL(lib).href);
const f = JSON.parse(fs.readFileSync(path.join(root, "site", "data", "ai_energy.json"), "utf-8"));
const choices = A.measures(f.rows);
const pick = (m) => (A.ofMeasure ? A.ofMeasure(f.rows, m) : f.rows.filter((r) => r.x_measures === m));
const shows = Object.fromEntries(choices.map((m) => [m, pick(m).map((r) => r.event_id)]));
console.log(JSON.stringify({ choices, shows, distinct: [...new Set(f.rows.map((r) => r.x_measures))].length }));
