// Session 10221: the page's own figure() (site/lib/aienergy.ts) on each row's value and on values a later row could
// hold, beside the number as the publication printed it. Run from site/:
//   node --import ../runs/c10221/register.mjs ../runs/c10221/figure_probe.mjs <out json>
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const [out] = process.argv.slice(2);
const A = await import(pathToFileURL(path.join(process.cwd(), "lib", "aienergy.ts")).href);
const f = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "ai_energy.json"), "utf-8"));
const rows = f.rows.map((r) => ({ id: r.event_id, value: r.x_value, shown: A.figure(r.x_value), printed: r.x_printed }));
const probes = [0.10, 1.0e-4, 1e-6, 9e-7, 3.4e-7, 1e21, 2.5e21].map((v) => ({ value: v, shown: A.figure(v) }));
fs.writeFileSync(out, JSON.stringify({ rows, probes }, null, 1));
console.log(JSON.stringify(probes));
