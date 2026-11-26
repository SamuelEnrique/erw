// Chain 740 (lab-desktop window 3), session 10805: the datacenter run's downloadable files, written as the page writes them
// (lib/dcfiles.ts) for two scenarios, so a test can run the Python script and read its verdicts. Writes the files to the
// folder given (default: the system's temporary folder) and prints their paths.
// Run: node site/scripts/dc-files-check.mjs [folder]
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const D = await import("../lib/dcimpact.ts");
const F = await import("../lib/dcfiles.ts");
const data = (n) => JSON.parse(fs.readFileSync(path.join(here, "..", "data", "forecast", n), "utf8"));
const P = { announced: data("datacenter_announced.json"), rules: data("datacenter_rules.json"), wages: data("datacenter_wages.json"),
  sales: data("sales_tax.json"), income: data("income_tax.json"), deflator: data("deflator.json") };
const one = (state, set) => { const x = D.dcDefaults(P, state, set); return { dc: true, x, r: D.dcRun(x, P) }; };
const sc = { a: one("va", { mw: 1000, invest: 3000, perm: 50, mwh: 5000000, brate: 1, erate: 4 }), b: one("mn", { invest: 1000, perm: 50, life: 40, matshare: 30 }) };
const dir = process.argv[2] ?? fs.mkdtempSync(path.join(os.tmpdir(), "erw-dc-"));
fs.mkdirSync(dir, { recursive: true });
const files = { "run.csv": F.dcCsv(sc), "run.py": F.dcPython(P, sc), "run.do": F.dcStata(P, sc) };
for (const [n, t] of Object.entries(files)) fs.writeFileSync(path.join(dir, n), t);
console.log(path.join(dir, "run.py"));
