// Session 10221, audit of /ai-energy, finding 7: the page's own measures() (site/lib/aienergy.ts) on the page's file, and
// the rows each choice of "What is measured" shows (the page filters on x_measures equal to the choice). Prints one JSON line.
//   node tests/audit_ai_energy_7_measures.mjs
import fs from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const A = await import(pathToFileURL(path.join(root, "site", "lib", "aienergy.ts")).href);
const f = JSON.parse(fs.readFileSync(path.join(root, "site", "data", "ai_energy.json"), "utf-8"));
const choices = A.measures(f.rows);
const shows = Object.fromEntries(choices.map((m) => [m, f.rows.filter((r) => r.x_measures === m).map((r) => r.event_id)]));
console.log(JSON.stringify({ choices, shows }));
