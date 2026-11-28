// Session 11404 (chain 770): the four plant types' figures under a given tree's lib/forecast.ts and parameter files,
// every state the sales tax file holds, the defaults and four variations, every stat and every year's taxes.
// Run from site/: node --import ./scripts/tsx-register.mjs ../runs/c770/s11404/plants.mjs <root> <out.json>
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const root = path.resolve(process.argv[2]);
const out = process.argv[3];
const F = await import(pathToFileURL(path.join(root, "site", "lib", "forecast.ts")).href);
const dir = path.join(root, "site", "data", "forecast");
const data = (n) => { const p = path.join(dir, n); return fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, "utf8")) : undefined; };
const P = {
  jediCosts: data("jedi_costs.json"), eiaCapex: data("eia_capex.json"), deflator: data("deflator.json"), capacity: data("capacity_factors.json"),
  sales: data("sales_tax.json"), income: data("income_tax.json"), property: data("property_rules.json"), taxable: data("jedi_taxable.json"), gas: data("gas.json"),
  exemptions: data("sales_exemptions.json"),
};
for (const k of ["coal", "biopower", "csp_trough"]) { const d = data(`${k}.json`); if (d) P[k] = d; }

// the live table on this machine (21 October 2026, before coal): the same rows for both trees
const csv = fs.readFileSync("C:/Users/lossa/Documents/erw/warehouse/output/nlr_jedi_multipliers.csv", "utf8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
const head = csv[0].split(",");
const iE = head.indexOf("entity"), iV = head.indexOf("variable"), iT = head.indexOf("ts_utc"), iX = head.indexOf("value");
const TECHS = ["land_based_wind", "utility_pv", "natural_gas", "geothermal"];
const rows = [];
for (const l of csv.slice(1)) {
  const c = l.split(",");
  const tech = c[iE].split(":")[1];
  if (TECHS.includes(tech)) rows.push({ entity: c[iE], variable: c[iV], ts_utc: c[iT], value: Number(c[iX]) });
}
const packed = F.pack(rows);
const STATES = Object.keys(P.sales.states).sort();
const FIG = ["c:jobs:onsite", "c:jobs:supply_chain", "c:jobs:induced", "c:jobs:total", "c:earnings:total", "c:output:total",
  "o:jobs:total", "o:earnings:total", "o:output:total", "sum:jobs", "sum:earnings", "sum:property", "sum:sales", "sum:income",
  "pv:earnings", "pv:property", "pv:sales", "pv:income", "pv:taxes", "y1:property", "y1:income"];
const VARIANTS = {
  default: {},
  own_rate: { own: 1.5, ownyears: 25, levy: 30 },
  big_late: { mw: 800, start: 2032, life: 35 },
  rate3: { rate: 3 },
  small: { mw: 5 },
};
const res = {};
let n = 0;
for (const tech of TECHS) for (const st of STATES) for (const [vn, set] of Object.entries(VARIANTS)) {
  const d = F.defaults(P, tech, st);
  const x = { ...d };
  for (const [k, v] of Object.entries(set)) if (k in d) x[k] = v;
  const r = F.run(x, F.unpack(packed, tech, st), P, null);
  const figs = Object.fromEntries(FIG.map((f) => [f, F.stat(r, f)]));
  const years = r.ok ? r.years.map((y) => [y.year, y.property, y.sales, y.income]) : [];
  res[`${tech}:${st}:${vn}`] = { ok: r.ok, key: F.inputsKey(x), figs, years };
  n++;
}
fs.writeFileSync(out, JSON.stringify(res));
console.log(`${n} runs, ${STATES.length} states, ${rows.length} rows`);
