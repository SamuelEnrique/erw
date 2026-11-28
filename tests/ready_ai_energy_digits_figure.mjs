// Session 11407 (chain 770, part C), the ruling readied for finding 6 of docs/reviews/ai-energy-model-audit-2026-11-26.md:
// the page's own figure() (site/lib/aienergy.ts, no import, so Node runs it as it is) on every row of the page's file,
// as the page calls it (the value and the row's printed words), and on values a later row could hold. One JSON line.
//   node tests/ready_ai_energy_digits_figure.mjs [path to aienergy.ts]
import fs from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const lib = process.argv[2] ? path.resolve(process.argv[2]) : path.join(root, "site", "lib", "aienergy.ts");
const A = await import(pathToFileURL(lib).href);
const f = JSON.parse(fs.readFileSync(path.join(root, "site", "data", "ai_energy.json"), "utf-8"));
const rows = Object.fromEntries(f.rows.map((r) => [r.event_id, A.figure(r.x_value, r.x_printed)]));
const probes = Object.fromEntries([1e-6, 9e-7, 3.4e-7].map((v) => [String(v), A.figure(v)]));
const printedProbe = A.figure(9e-7, "about 9×10−7 kWh a token");
console.log(JSON.stringify({ rows, probes, printedProbe }));
