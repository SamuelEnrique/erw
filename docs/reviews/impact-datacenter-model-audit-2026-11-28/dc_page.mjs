// Session 11404 (chain 770): /impact's datacenter figures by the page's own code (lib/forecastdata.ts's dcParams and
// dcProjectList, lib/dcui.ts's dcResolve, lib/dcimpact.ts's dcRun, dcStat and dcDisplay), for the audit's cases.
// Writes cases.json (each case's id, state and what it sets) and page.json (every figure, by year, and its printed text).
// Run from site/: node --import ./scripts/tsx-register.mjs ../runs/c770/s11404/dc_page.mjs
import fs from "node:fs";

const FD = await import("../../../site/lib/forecastdata.ts");
const D = await import("../../../site/lib/dcimpact.ts");
const U = await import("../../../site/lib/dcui.ts");
const I = await import("../../../site/lib/forecastui.ts");
const P2 = FD.dcParams();
const list = FD.dcProjectList();
const STATES = I.STATE_LIST.map(([k]) => k);
const out = "../runs/c770/s11404/";

// the cases: every state at its defaults; the three projects of seed 11404 as the picker sets them; settings that reach
// every line (rates, an abatement, a schedule, the building's share, the electricity)
const cases = [];
for (const st of STATES) cases.push({ id: `default_${st}`, state: st, v: {} });
const pickOf = (id) => {
  const i = list.findIndex((p) => p.id === id);
  const p = list[i];
  const v = { dcproj: i };
  if (p.mw !== null) v.dmw = p.mw;
  if (p.invest !== null) v.invest = p.invest;
  if (p.perm !== null) v.perm = p.perm;
  if (p.cons !== null) v.cons = p.cons;
  return { p, v };
};
for (const [id, extra] of [
  ["ms_aws_madison_2024", {}], ["va_google_2025", {}], ["az_beale_pima_2025", {}],
  // each with the property lines and the building's share typed, the county's own figures (runs/c770/s11404, the audit's section 3)
  ["ms_aws_madison_2024", { brate: 10.5, erate: 10.5, matshare: 40, pabate: 50, abateyears: 10 }],
  ["va_google_2025", { brate: 0.875, erate: 4.15, eqv1: 60, eqstep: 15, eqfloor: 10, matshare: 40, mwh: 2628000 }],
  ["az_beale_pima_2025", { brate: 12, erate: 12, matshare: 40 }],
]) {
  const { p, v } = pickOf(id);
  const tag = Object.keys(extra).length ? `${id}_typed` : id;
  cases.push({ id: tag, state: p.state, v: { ...v, ...extra }, project: id });
}
const more = [
  ["oh_mwh", "oh", { mwh: 5000000 }], ["il_mwh", "il", { mwh: 5000000 }], ["va_mwh_small", "va", { mwh: 30 }],
  ["la_typed", "la", { brate: 10, erate: 10, pabate: 100, abateyears: 10 }], ["ga_late", "ga", { dstart: 2030 }],
  ["mn_state_rate", "mn", { invest: 1000, perm: 50 }], ["md_big", "md", { invest: 300, perm: 5 }], ["md_small", "md", { invest: 200, perm: 5 }],
  ["fl_99", "fl", { dmw: 99 }], ["sc_2032", "sc", { dstart: 2032 }], ["wa_rural", "wa", { dstart: 2034 }], ["mt_small", "mt", { invest: 40, brate: 1, erate: 1 }],
  ["va_noex", "va", { dcex: 0 }], ["va_once", "va", { refresh: 0 }], ["va_bld40", "va", { brate: 1, erate: 1, bldyears: 40 }],
];
for (const [id, st, v] of more) cases.push({ id, state: st, v });

const page = {};
const restCases = [];
for (const c of cases) {
  const vals = {};
  for (const f of U.DC_FIELDS) vals[f.name] = Number.isFinite(c.v[f.name]) ? c.v[f.name] : NaN;
  const x = U.dcResolve(P2, vals, c.state);
  const r = D.dcRun(x, P2);
  // what the restatement is told: only what the reader or the pick sets, by the model's names
  const set = {};
  for (const f of U.DC_FIELDS) if (Number.isFinite(c.v[f.name]) && !["dmw", "invest", "perm", "cons"].includes(f.name) || (Number.isFinite(c.v[f.name]) && !c.project)) set[f.input] = f.input === "dcex" ? c.v[f.name] === 1 : c.v[f.name];
  restCases.push({ id: c.id, state: c.state, set, ...(c.project ? { project: c.project } : {}) });
  const figs = {};
  const names = ["c:jobs:onsite", "c:jobs:total", "c:earnings:total", "o:jobs:onsite", "o:jobs:total", "o:earnings:total", "y1:property", "sum:property",
    "sum:sales", "sum:income", "pv:taxes", "pv:earnings", "sum:salesbefore", "sum:forgone", "y1:propb", "y1:prope", "y1:elec", "pv:sales", "pv:income",
    "pv:property", "pv:elec", "pv:forgone", "sum:jobs", "sum:earnings"];
  for (const n of names) { const v = D.dcStat(r, n); figs[n] = { v, text: v === null ? null : D.dcDisplay(n, v) }; }
  page[c.id] = { x, ok: r.ok, why: r.why ?? null, exemption: r.exemption, chain: r.chain.held, figs,
    years: r.years.map((y) => ({ year: y.year, jobs: y.jobs.total, earnings: y.earnings.total, equipment: y.equipment, property: y.property, propb: y.propb, prope: y.prope,
      salesbefore: y.salesbefore, forgone: y.forgone, sales: y.sales, income: y.income, elec: y.elec })) };
}
// the other-states chart for the default Texas and Virginia scenarios, as DcOtherStates computes it
const other = {};
for (const st0 of ["tx", "va"]) {
  other[st0] = STATES.map((st) => {
    const res = D.dcRun(U.dcResolve(P2, { dcproj: NaN }, st), P2);
    return { st, ok: res.ok, taxes: (res.pv.sales ?? 0) + res.pv.income + (res.pv.elec ?? 0), forgone: res.pv.forgone ?? 0 };
  });
}
page._other = other;
page._defaults = P2.announced.defaults;
fs.writeFileSync(out + "cases.json", JSON.stringify(restCases, null, 1));
fs.writeFileSync(out + "page.json", JSON.stringify(page));
console.log(`${cases.length} cases`);
