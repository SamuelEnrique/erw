// Session 11404 (chain 770): one choice of /impact's datacenter changed at a time, by the page's own model (lib/dcimpact.ts
// on the parameter files as lib/forecastdata.ts reads them). Prints each measure's figures before and after.
// Run from site/: node --import ./scripts/tsx-register.mjs ../runs/c770/s11404/measures.mjs
import fs from "node:fs";

const FD = await import("../../../site/lib/forecastdata.ts");
const D = await import("../../../site/lib/dcimpact.ts");
const U = await import("../../../site/lib/dcui.ts");
const P2 = FD.dcParams();
const list = FD.dcProjectList();
const fig = (r) => ({ cjobs: r.construction.jobs.total, cearn: r.construction.earnings.total, ojobs: r.operations.jobs.total, oearn: r.operations.earnings.total,
  salesbefore: r.sums.salesbefore, forgone: r.sums.forgone, sales: r.sums.sales, income: r.sums.income, pvsales: r.pv.sales, pvincome: r.pv.income,
  pvprop: r.pv.property, pvtax: r.pv.taxes, pvearn: r.pv.earnings, prop: r.sums.property });
const run = (st, v, PP = P2) => {
  const vals = {};
  for (const f of U.DC_FIELDS) vals[f.name] = Number.isFinite(v[f.name]) ? v[f.name] : NaN;
  const x = U.dcResolve(PP, vals, st);
  return { x, r: D.dcRun(x, PP) };
};
const pick = (id) => { const p = list.find((q) => q.id === id); const v = {}; if (p.mw !== null) v.dmw = p.mw; if (p.invest !== null) v.invest = p.invest; if (p.perm !== null) v.perm = p.perm; if (p.cons !== null) v.cons = p.cons; return { p, v }; };
const out = [];
const show = (name, st, a, b, PPb = P2, PPa = P2) => {
  const A = run(st, a, PPa), B = run(st, b, PPb);
  const fa = fig(A.r), fb = fig(B.r);
  const pct = (k) => (fa[k] ? `${(((fb[k] ?? 0) / fa[k] - 1) * 100).toFixed(2)}%` : "n/a");
  out.push({ name, st, before: fa, after: fb });
  console.log(`\n## ${name} (${st})`);
  for (const k of Object.keys(fa)) if (fa[k] !== fb[k]) console.log(`  ${k}: ${fa[k] === null ? "null" : fa[k].toFixed(2)} -> ${fb[k] === null ? "null" : fb[k].toFixed(2)} (${pct(k)})`);
};
const clone = () => JSON.parse(JSON.stringify(P2));

// 1. construction workers a billion: 833.3 (with Meta's seven posts, decision 27) against 400.0 (before them)
{ const Q = clone(); Q.announced.defaults.construction_jobs_per_billion.median = 400; show("construction workers 400 a billion, not 833.3", "va", {}, {}, Q); show("construction workers 400 a billion, not 833.3", "tx", {}, {}, Q); }
// 2. permanent jobs by the investment (66.67 a billion), not by the MW (decision 2)
show("permanent jobs by investment (66.67 a USD billion)", "va", {}, { perm: 12 * P2.announced.defaults.permanent_jobs_per_billion.median });
// 3. equipment bought once, or every 7 years, not every 5 (decision 7)
show("equipment bought once (refresh 0)", "va", {}, { refresh: 0 });
show("equipment bought every 7 years", "va", {}, { refresh: 7 });
show("equipment bought once (refresh 0)", "tx", {}, { refresh: 0 });
// 4. Loudoun's schedule for the equipment, at Loudoun's 2026 rates (decision 8)
show("Loudoun's equipment schedule 60/15/10, Loudoun's rates typed", "va", { brate: 0.875, erate: 4.15 }, { brate: 0.875, erate: 4.15, eqv1: 60, eqstep: 15, eqfloor: 10 });
// 5. JLARC's interview wage, USD 100,000, for a Virginia datacenter job (decision 6)
show("JLARC's USD 100,000 wage, not CBP's 152,609", "va", {}, { opwage: 100000 });
// 6. the exemption off
show("exemption not applied", "va", {}, { dcex: 0 });
// 7. the building's taxable share 40 percent (not given by default)
show("building's taxable share 40 percent", "va", {}, { matshare: 40 });
show("building's taxable share 40 percent", "ms", {}, { matshare: 40 });
// 8. 30 operating years, and the A-94 Appendix C rate of 2 percent
show("30 operating years", "va", {}, { dlife: 30 });
show("discount rate 2 percent real", "va", {}, { drate: 2 });
// 9. the median investment a MW against the mean (decision 1)
{ const rows = P2.announced.defaults.investment_per_mw; console.log("\ninvestment a MW: median", rows.median, "n", rows.n); }
// 10. supply chain and induced where none is held: the Mississippi project with Virginia's, Georgia's and Minnesota's ratios
{ const { v } = pick("ms_aws_madison_2024");
  for (const s of ["va", "ga", "mn"]) { const Q = clone(); Q.rules.multipliers.ms = P2.rules.multipliers[s]; show(`AWS Madison with ${s}'s supply chain and induced ratios`, "ms", v, v, Q); } }
// 11. Beale's own wage (USD 64,000) and its own split (two thirds equipment, one third construction)
{ const { v } = pick("az_beale_pima_2025");
  show("Beale: the document's wage USD 64,000", "az", v, { ...v, opwage: 64000 });
  show("Beale: the document's split, equipment 66.67, building 33.33, land 0", "az", { ...v, brate: 12, erate: 12 }, { ...v, brate: 12, erate: 12, eq: 66.6667, bld: 33.3333, land: 0 }); }
// 12. Arizona's standard deduction at the federal 2026 amount (USD 16,100) against the file's 8,350 (a data request)
{ const { v } = pick("az_beale_pima_2025"); const Q = clone(); Q.income.states.az = { ...Q.income.states.az, standard_deduction_single: 16100 };
  show("Beale: Arizona's standard deduction 16,100, not 8,350", "az", v, v, Q); }
// 13. the superseded documents of two campuses left out of the medians (Richland 2024, Amazon NW Louisiana February 2026)
{ const A = JSON.parse(fs.readFileSync("data/forecast/datacenter_announced.json", "utf8"));
  const drop = new Set(["la_meta_richland_2024", "la_amazon_caddo_bossier_2026"]);
  const idx = JSON.parse(fs.readFileSync("data/forecast/deflator.json", "utf8")).index;
  const to25 = (v, y) => (idx[String(y)] ? v * idx["2025"] / idx[String(y)] : v);
  const med = (a) => { const s = [...a].sort((p, q) => p - q); const n = s.length; return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2; };
  const keys = { mw: [], inv: [], pmw: [], pbn: [], cbn: [] };
  for (const r of A.rows) {
    if (r.to_date || drop.has(r.id)) continue;
    const m = r.mw?.value; const gen = r.investment_includes_generation || r.investment_partial;
    const i = r.investment && !gen ? to25(r.investment.value, r.investment.year ?? 2025) : null;
    const p = r.permanent_jobs && !String(r.permanent_jobs.measure).includes("kind not stated") ? r.permanent_jobs.value : null;
    const c = r.construction_jobs?.value ?? null;
    if (m) keys.mw.push(m); if (m && i) keys.inv.push(i / 1e6 / m); if (m && p !== null) keys.pmw.push(p / m);
    if (i && p !== null) keys.pbn.push(p / (i / 1e9)); if (i && c !== null) keys.cbn.push(c / (i / 1e9));
  }
  const Q = clone(); const d = Q.announced.defaults;
  d.mw_stated.median = med(keys.mw); d.investment_per_mw.median = med(keys.inv); d.permanent_jobs_per_mw.median = med(keys.pmw);
  d.permanent_jobs_per_billion.median = med(keys.pbn); d.construction_jobs_per_billion.median = med(keys.cbn);
  console.log("\nmedians without the two superseded rows:", Object.fromEntries(Object.entries(keys).map(([k, v]) => [k, [v.length, med(v)]])));
  show("medians without the two superseded documents", "va", {}, {}, Q); }
// 14. Texas: the share of the default's taxes that is sales tax a qualifying datacenter would not pay under Tax Code 151.359 (unread)
{ const { r } = run("tx", {}); console.log(`\nTexas default: pv taxes ${r.pv.taxes.toFixed(2)}, of which sales ${r.pv.sales.toFixed(2)} (${(100 * r.pv.sales / r.pv.taxes).toFixed(1)} percent); sum sales ${r.sums.sales.toFixed(2)}`);
  const t = run("tn", {}).r; console.log(`Tennessee default: pv taxes ${t.pv.taxes.toFixed(2)}, of which sales ${t.pv.sales.toFixed(2)} (${(100 * t.pv.sales / t.pv.taxes).toFixed(1)} percent)`); }
fs.writeFileSync("../runs/c770/s11404/measures.json", JSON.stringify(out, null, 1));
