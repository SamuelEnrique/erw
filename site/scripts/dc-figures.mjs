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
  // session 10805: the states of part E
  { id: "mn_state_rate_35y", state: "mn", set: { invest: 1000, perm: 50, start: 2026, build: 2, life: 40 } },
  { id: "md_20y", state: "md", set: { invest: 300, perm: 5, start: 2026, build: 2, life: 20 } },
  { id: "md_10y", state: "md", set: { invest: 200, perm: 5, start: 2026, build: 2, life: 20 } },
  { id: "fl_100mw", state: "fl", set: { mw: 100, invest: 150, perm: 10, matshare: 40 } },
  { id: "fl_99mw", state: "fl", set: { mw: 99, invest: 1500, perm: 10 } },
  { id: "sc_2031", state: "sc", set: { invest: 100, perm: 25, start: 2031, build: 2, life: 20 } },
  { id: "nv_discretionary", state: "nv", set: { invest: 5000, perm: 500 } },
  { id: "mo_15y_building", state: "mo", set: { invest: 400, perm: 10, matshare: 50, start: 2026, build: 3, life: 20 } },
  { id: "id_threshold", state: "id", set: { invest: 250, perm: 30 } },
  { id: "nd_no_threshold", state: "nd", set: { mw: 20, invest: 50, perm: 3 } },
  // session 10806
  { id: "az_tenth_year", state: "az", set: { invest: 100, perm: 5, start: 2026, build: 2, life: 20 } },
  { id: "nc_75m", state: "nc", set: { invest: 75, perm: 5 } },
  { id: "wi_building", state: "wi", set: { invest: 200, perm: 5, matshare: 40, start: 2026, build: 2, life: 10 } },
  { id: "ut_words", state: "ut", set: { invest: 2000, perm: 100 } },
  { id: "mt_class17", state: "mt", set: { invest: 100, perm: 5, brate: 60, erate: 60 } },
  { id: "mt_below", state: "mt", set: { invest: 40, perm: 5, brate: 1, erate: 1 } },
  { id: "ks_250m_building", state: "ks", set: { invest: 600, perm: 25, matshare: 35 } },
  { id: "ga_rule", state: "ga", set: { invest: 2000, perm: 100 } },
  // session 10809: Georgia's ratios, the equipment schedule, Mississippi's words
  { id: "ga_chain", state: "ga", set: { invest: 1000, perm: 100, cons: 500 } },
  { id: "va_loudoun_schedule", state: "va", set: { invest: 500, perm: 50, refresh: 4, life: 12, brate: 0.805, erate: 4.15, eqv1: 60, eqstep: 15, eqfloor: 10 } },
  { id: "ms_words", state: "ms", set: { invest: 2000, perm: 100 } },
  { id: "pa_25y_state_rate", state: "pa", set: { invest: 200, perm: 45, start: 2026, build: 2, life: 30 } },
  { id: "mn_chain", state: "mn", set: { invest: 1000, perm: 100, cons: 500 } },
  { id: "ky_450m", state: "ky", set: { invest: 600, perm: 30 } },
  { id: "in_words", state: "in", set: { invest: 2000, perm: 100 } },
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
