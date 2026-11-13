// Session 4209 (chain 239): the forecast model against published impact studies (docs/methods/forecast.md, section 9).
// Each study's own project (technology, state, MW, cost and its dollar year) runs through lib/forecast.ts at the tool's
// defaults otherwise; the study's published statewide figures stand beside the model's. The studies' local content is
// their own (the developer's spending plan), the model's is JEDI's default: that is the first reason for a difference.
//
//   node site/scripts/forecast-crosscheck.mjs <nlr_jedi_multipliers.csv> [--json out.json]
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const F = await import("../lib/forecast.ts");
const data = (n) => JSON.parse(fs.readFileSync(path.join(here, "..", "data", "forecast", n), "utf8"));
const P = {
  jediCosts: data("jedi_costs.json"), eiaCapex: data("eia_capex.json"), deflator: data("deflator.json"), capacity: data("capacity_factors.json"),
  sales: data("sales_tax.json"), income: data("income_tax.json"), property: data("property_rules.json"), taxable: data("jedi_taxable.json"), gas: data("gas.json"),
};

function readRows(file) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const head = lines[0].split(",");
  const at = (k) => head.indexOf(k);
  return lines.slice(1).map((l) => l.split(",")).filter((c) => ["jobs", "earnings", "output"].includes(c[at("variable")]))
    .map((c) => ({ entity: c[at("entity")], variable: c[at("variable")], ts_utc: c[at("ts_utc")], value: Number(c[at("value")]) }));
}

// Each study: what it says, where, and the inputs it states. Figures are the study's statewide totals.
export const STUDIES = [
  {
    id: "jayhawk_ks", title: "Jayhawk Wind Energy Project (Bourbon and Crawford Counties, Kansas): economic development report, November 2019",
    url: "https://fortscott.biz/wp-content/uploads/2019/12/Jayhawk-Wind-Economic-Development-Report-Final-November-20191.pdf", request: 50,
    method: "JEDI Wind with 2017 IMPLAN state multipliers and the project's own spending and local shares; 25-year life",
    tech: "land_based_wind", state: "ks", mw: 195, cost_usd: 250e6, cost_year: 2019, cost_words: "an investment of almost $250 million", life: 25,
    published: { "construction:total:jobs": 634, "construction:onsite:jobs": 190, "construction:supply_chain:jobs": 321, "construction:induced:jobs": 123,
      "construction:total:earnings": 36.7e6, "construction:total:output": 98.2e6, "operations:total:jobs": 43, "operations:onsite:jobs": 9,
      "operations:total:earnings": 2.2e6, "operations:total:output": 7.5e6 },
    published_words: "634 (190 direct) local jobs during construction for the State of Kansas; 43 (9 direct) long-term jobs for the State of Kansas; over $36.7 million in local earnings during construction for the State of Kansas; over $2.2 million in local long-term earnings; over $98.2 million in local output during construction; over $7.5 million in local long-term output",
    dollars_of: 2019,
  },
  {
    id: "glendive_mt", title: "Glendive Wind (Prairie County, Montana), NextEra Energy Resources: economic impact summary of a 2024 study by Strategic Economic Research",
    url: "https://www.nexteraenergyresources.com/content/dam/neer/us/en/microsites/PDF/glendive-prairie-econ-impact.pdf", request: 49,
    method: "IMPLAN multipliers with NREL's JEDI model, statewide",
    tech: "land_based_wind", state: "mt", mw: 800, cost_usd: 1e9, cost_year: 2024, cost_words: "$1 billion investment in Prairie County; up to 800 megawatts", life: 30,
    published: { "construction:total:jobs": 400 },
    published_words: "Approx. 400 construction jobs in the state of Montana",
    dollars_of: 2024,
  },
  {
    id: "ohio_pv_low", title: "Measuring the Economic Impacts of Utility-Scale Solar in Ohio, Ohio University (Voinovich School), 31 July 2020: the low scenario",
    url: "https://static1.squarespace.com/static/56a8596376d99c0164fc16bd/t/5f50094e9c0ff3029d54bc6c/1599080786155/Measuring+the+Economic+Impacts+of+Utility-Scale+Solar+in+Ohio+---+FINAL%2C+7.31.2020.pdf", request: 54,
    method: "JEDI PV updated with 2018 IMPLAN multipliers and NREL's Q1 2018 one-axis tracker utility cost benchmark; 80 percent Ohio labor and 30 percent Ohio materials; DC capacity; 2018 dollars; 40-year life",
    tech: "utility_pv", state: "oh", mw_dc: 2500, cost_usd: 3592192939, cost_year: 2018, cost_words: "Project Construction or Installation Cost, Low (2.5 GW): $3,592,192,939", life: 40,
    published: { "construction:total:jobs": 18039, "construction:onsite:jobs": 8536, "operations:total:jobs": 207, "construction:total:output": 3.2e9, "property:year": 22.5e6 },
    published_words: "a total of 18,039 one-time construction phase jobs, and 207 annual operations and maintenance (O&M) phase jobs; 8,536 direct construction jobs; roughly $3.2B construction phase economic impacts; up to $22.5M in annual tax revenues",
    dollars_of: 2018,
  },
];

export function crosscheck(rows) {
  return STUDIES.map((s) => {
    const base = F.defaults(P, s.tech, s.state);
    const ilr = s.tech === "utility_pv" ? base.ilr : 1;
    const mw = s.mw ?? s.mw_dc / ilr;  // the model's PV MW are AC: the study's DC MW over the state's loading ratio
    const capex = (s.cost_usd * F.to2025(P, s.cost_year)) / (mw * 1000);
    const x = { ...base, mw, capex, life: s.life };
    const r = F.run(x, rows, P);
    const back = 1 / F.to2025(P, s.dollars_of);  // the model's 2025 dollars in the study's dollars
    const model = {};
    for (const [k, v] of Object.entries(s.published)) {
      if (k === "property:year") { const y = r.years.find((t) => t.phase === "operations"); model[k] = y?.property ?? null; continue; }
      const [ph, e, m] = k.split(":");
      const val = r[ph][m][e];
      model[k] = m === "jobs" ? val : val * back;
    }
    const lines = Object.keys(s.published).map((k) => ({ figure: k, published: s.published[k], model: model[k],
      ratio: model[k] === null || !s.published[k] ? null : model[k] / s.published[k] }));
    return { id: s.id, title: s.title, url: s.url, request: s.request, method: s.method, inputs: { tech: s.tech, state: s.state, mw, capex_2025_usd_per_kw: capex, life: s.life, ilr },
      published_words: s.published_words, cost_words: s.cost_words, dollars_of: s.dollars_of, lines };
  });
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  const file = process.argv[2];
  if (!file || !fs.existsSync(file)) { console.error("usage: forecast-crosscheck.mjs <nlr_jedi_multipliers.csv> [--json out.json]"); process.exit(2); }
  const out = crosscheck(readRows(file));
  for (const s of out) {
    console.log(`\n${s.id}: ${s.inputs.tech} ${s.inputs.state} ${s.inputs.mw.toFixed(1)} MW, capex ${s.inputs.capex_2025_usd_per_kw.toFixed(0)} USD/kW (2025)`);
    for (const l of s.lines) console.log(`  ${l.figure.padEnd(32)} published ${String(l.published).padStart(12)}  model ${l.model === null ? "none" : l.model.toFixed(1).padStart(12)}  ratio ${l.ratio === null ? "-" : l.ratio.toFixed(3)}`);
  }
  const j = process.argv.indexOf("--json");
  if (j > 0) fs.writeFileSync(process.argv[j + 1], JSON.stringify({ written_by: "site/scripts/forecast-crosscheck.mjs", studies: out }, null, 1) + "\n");
}
