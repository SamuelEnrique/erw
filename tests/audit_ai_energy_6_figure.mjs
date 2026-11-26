// Session 10221, audit of /ai-energy, finding 6: the page's own figure() (site/lib/aienergy.ts, no import, so Node runs it
// as it is) on every row of the page's file and on values a later row could hold. Prints one JSON line.
//   node tests/audit_ai_energy_6_figure.mjs
import fs from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const A = await import(pathToFileURL(path.join(root, "site", "lib", "aienergy.ts")).href);
const f = JSON.parse(fs.readFileSync(path.join(root, "site", "data", "ai_energy.json"), "utf-8"));
const rows = Object.fromEntries(f.rows.map((r) => [r.event_id, A.figure(r.x_value)]));
const probes = Object.fromEntries([1e-6, 9e-7, 3.4e-7].map((v) => [String(v), A.figure(v)]));
console.log(JSON.stringify({ rows, probes }));
