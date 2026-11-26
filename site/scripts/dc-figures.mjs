// Chain 740 (lab-desktop window 3), session 10804: the datacenter figures of /impact for the replication's cases, drawn
// with the page's own model (lib/dcimpact.ts) from the parameter files, written to
// replication/impact/datacenter/page_figures.json, which replication/impact/datacenter/replicate.py recomputes.
// Run: node site/scripts/dc-figures.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const D = await import("../lib/dcimpact.ts");
const data = (n) => JSON.parse(fs.readFileSync(path.join(here, "..", "data", "forecast", n), "utf8"));
const P = { announced: data("datacenter_announced.json"), rules: data("datacenter_rules.json"), wages: data("datacenter_wages.json"),
  sales: data("sales_tax.json"), income: data("income_tax.json"), deflator: data("deflator.json") };
export const CASES = [
  { id: "default_va", state: "va", set: {} },
  { id: "default_tx", state: "tx", set: {} },
  { id: "la_meta_richland_2026", state: "la", set: { mw: 5000, invest: 50000, perm: 1000, cons: 7500, start: 2026, build: 5, life: 20, brate: 10, erate: 10 } },
  { id: "va_cleanarc_caroline_2025", state: "va", set: { mw: 1000, invest: 3000, perm: 50, start: 2026, build: 2, life: 20, mwh: 5000000 } },
  { id: "wv_penzance_berkeley_2026", state: "wv", set: { mw: 600, invest: 4000, perm: 125, cons: 1000, start: 2026, build: 2, life: 20 } },
  { id: "va_no_exemption_abated", state: "va", set: { mw: 300, invest: 2500, perm: 60, dcex: false, brate: 1.1, erate: 4.15, bldyears: 40, abate: 50, abateyears: 10, matshare: 40 } },
  { id: "ia_threshold", state: "ia", set: { mw: 50, invest: 199, perm: 20 } },
  { id: "la_late_build", state: "la", set: { invest: 5000, perm: 100, start: 2030, build: 2, life: 10 } },
];
const STREAMS = ["jobs", "earnings", "property", "propb", "prope", "salesbefore", "forgone", "sales", "income", "elec"];
const out = CASES.map((c) => {
  const x = D.dcDefaults(P, c.state, c.set);
  const r = D.dcRun(x, P);
  return { id: c.id, inputs: x, ok: r.ok, eligible: r.exemption.eligible, chain: r.chain.held,
    years: r.years.map((y) => ({ year: y.year, phase: y.phase, ...Object.fromEntries(STREAMS.map((s) => [s, D.dcStat(r, `year:${y.year}:${s}`)])) })),
    sums: Object.fromEntries(STREAMS.map((s) => [s, D.dcStat(r, `sum:${s}`)])), pv: Object.fromEntries([...STREAMS.filter((s) => s !== "jobs"), "taxes"].map((s) => [s, D.dcStat(r, `pv:${s}`)])) };
});
const dest = path.join(here, "..", "..", "replication", "impact", "datacenter", "page_figures.json");
fs.mkdirSync(path.dirname(dest), { recursive: true });
fs.writeFileSync(dest, JSON.stringify({ about: "The datacenter figures of /impact for the replication's cases, from lib/dcimpact.ts (site/scripts/dc-figures.mjs).", cases: out }, null, 1) + "\n");
console.log("wrote", path.relative(process.cwd(), dest), out.length, "cases");
