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
  { id: "ut_rule", state: "ut", set: { invest: 2000, perm: 100 } },
  // session 10813: Arkansas (state rate, construction covered), Oklahoma (no threshold, state rate), Illinois (words)
  { id: "ar_rule", state: "ar", set: { invest: 2000, perm: 20, matshare: 40 } },
  { id: "ok_rule", state: "ok", set: { invest: 500, perm: 20 } },
  { id: "il_words", state: "il", set: { invest: 2000, perm: 100 } },
  { id: "il_elec", state: "il", set: { invest: 2000, perm: 100, mwh: 5000000 } },
  // session 10815: Connecticut (20 years, 30 with USD 400 million)
  { id: "ct_30", state: "ct", set: { invest: 500, perm: 10, life: 30 } },
  { id: "ma_words", state: "ma", set: { invest: 2000, perm: 200 } },
  { id: "oh_words", state: "oh", set: { invest: 2000, perm: 100 } },
  { id: "oh_elec_elected", state: "oh", set: { invest: 2000, perm: 100, mwh: 5000000 } },
  { id: "oh_elec_tiers", state: "oh", set: { invest: 100, perm: 10, mwh: 40000 } },
  { id: "ne_words", state: "ne", set: { invest: 2000, perm: 100 } },
  { id: "al_words", state: "al", set: { invest: 2000, perm: 100 } },
  { id: "wy_rule", state: "wy", set: { invest: 800, perm: 30 } },
  // session 10818: Georgia's 40 percent and New Mexico's one third, the reader's rates typed
  { id: "ga_property", state: "ga", set: { invest: 2000, perm: 100, brate: 2.5, erate: 2.5 } },
  { id: "nm_property", state: "nm", set: { invest: 1500, perm: 60, brate: 3, erate: 3, eqv1: 60, eqstep: 15, eqfloor: 10 } },
  { id: "oh_property", state: "oh", set: { invest: 1000, perm: 50, brate: 6, erate: 6, mwh: 800000 } },
  { id: "ia_property", state: "ia", set: { invest: 1000, perm: 50, brate: 2, erate: 2 } },
  { id: "mn_property", state: "mn", set: { invest: 1000, perm: 50, brate: 1.8, erate: 1.8, life: 35 } },
  { id: "nd_property", state: "nd", set: { invest: 1500, perm: 40, brate: 1.2, erate: 1.2 } },
  { id: "ks_property", state: "ks", set: { invest: 800, perm: 30, brate: 13, erate: 13 } },
  { id: "sc_property", state: "sc", set: { invest: 2000, perm: 200, brate: 32, erate: 32 } },
  { id: "wy_property", state: "wy", set: { invest: 1000, perm: 50, brate: 7, erate: 7 } },
  { id: "az_property", state: "az", set: { invest: 3600, perm: 180, brate: 9, erate: 9 } },
  { id: "mo_property", state: "mo", set: { invest: 1400, perm: 30, brate: 7.5, erate: 7.5 } },
  { id: "nv_property", state: "nv", set: { invest: 600, perm: 50, brate: 3.2, erate: 3.2, abate: 75, abateyears: 10 } },
  { id: "al_property", state: "al", set: { invest: 800, perm: 100, brate: 4, erate: 4 } },
  { id: "ms_property", state: "ms", set: { invest: 10000, perm: 500, brate: 12, erate: 12, abate: 100, abateyears: 10 } },
  { id: "ar_property", state: "ar", set: { invest: 6000, perm: 500, brate: 4.7, erate: 4.7, matshare: 40 } },
  { id: "il_property", state: "il", set: { invest: 500, perm: 30, brate: 7, erate: 0, mwh: 1500000 } },
  { id: "tn_property", state: "tn", set: { invest: 2000, perm: 100, brate: 3.2, erate: 3.2 } },
  { id: "wi_property", state: "wi", set: { invest: 3300, perm: 100, brate: 1.9, erate: 1.9, matshare: 40 } },
  { id: "mi_2050", state: "mi", set: { invest: 500, perm: 40, life: 30, matshare: 30 } },
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
