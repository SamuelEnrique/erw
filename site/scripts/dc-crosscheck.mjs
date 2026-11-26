// Chain 740 (lab-desktop window 3), session 10804: the datacenter of /impact (lib/dcimpact.ts) beside what a state's own
// report or release said of the same project or the same kind of project. Each case runs the document's own figures
// through the model at its defaults otherwise, and prints the model's figure beside the published one. A difference is
// reported, never tuned away. docs/methods/forecast.md, the datacenter cross-check.
// Run: node site/scripts/dc-crosscheck.mjs   (writes docs/reviews/impact-datacenter-crosscheck-2026-11-26.json)
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const D = await import("../lib/dcimpact.ts");
const data = (n) => JSON.parse(fs.readFileSync(path.join(here, "..", "data", "forecast", n), "utf8"));
const P = { announced: data("datacenter_announced.json"), rules: data("datacenter_rules.json"), wages: data("datacenter_wages.json"),
  sales: data("sales_tax.json"), income: data("income_tax.json"), deflator: data("deflator.json") };
const idx = P.deflator.index;
const to25 = (y) => idx["2025"] / idx[String(y)];
const out = [];

// 1. JLARC (Virginia, 2024), page 21: "If a typical modern 250,000-square-foot data center costs $250 million to $325 million
// to build and equip, the exemption would provide an initial benefit of about $9 million to $15.5 million in savings
// (depending on the locality)." Dollars of 2024 (the report's year).
for (const usd of [250, 325]) {
  const x = D.dcDefaults(P, "va", { invest: usd * to25(2024), perm: 50, start: 2026, build: 2, life: 5, refresh: 0 });
  const r = D.dcRun(x, P);
  const initial = r.years.filter((y) => y.phase === "construction").reduce((a, y) => a + (y.forgone ?? 0), 0) / to25(2024);
  out.push({ case: "jlarc_typical_250k_sqft", investment_musd_2024: usd, model_forgone_musd_2024: +(initial / 1e6).toFixed(2),
    published: "about $9 million to $15.5 million (depending on the locality)", rate_pct: x.sales,
    at_lowest_and_highest_rate_musd: [5.3, 7.0].map((r2) => +((usd * 1e6 * x.eq / 100 * r2 / 100) / 1e6).toFixed(2)) });
}

// 2. Alabama's governor (14 June 2018, request 126): Facebook in Huntsville, $750 million, 100 jobs at "an average annual
// salary of $80,000"; "Total new revenue over thirty years from the Data Center is estimated to be $297.3 million that will
// be divided between the state, county and city." The model over 30 operating years, dollars of 2018 back from 2025.
{
  const k = to25(2018);
  const x = D.dcDefaults(P, "al", { invest: 750 * k, perm: 100, opwage: Math.round(80000 * k), start: 2026, build: 2, life: 30 });
  const r = D.dcRun(x, P);
  const opYears = r.years.filter((y) => y.phase === "operations");
  const sales = opYears.reduce((a, y) => a + (y.sales ?? 0), 0) + r.years.filter((y) => y.phase === "construction").reduce((a, y) => a + (y.sales ?? 0), 0);
  const income = r.sums.income;
  out.push({ case: "al_facebook_huntsville_2018", published_30y_revenue_musd_2018: 297.3,
    model_sales_tax_paid_musd_2018: +(sales / k / 1e6).toFixed(1), model_income_tax_musd_2018: +(income / k / 1e6).toFixed(1),
    model_property_tax: "not held (no Alabama rate is held; the reader types the county's and city's)",
    model_total_held_musd_2018: +((sales + income) / k / 1e6).toFixed(1), exemption_held: r.exemption.held });
}

// 3. Louisiana Economic Development (13 July 2026, request 33): "approximately 1,000 operational jobs"; "LED estimates the
// project will result in an additional 1,900 indirect new jobs". The model holds no Louisiana multiplier; Virginia's
// (JLARC) ratio of indirect plus induced to direct operating jobs, for comparison only.
{
  const m = P.rules.multipliers.va.operations;
  out.push({ case: "la_meta_richland_2026_indirect", published_indirect_per_operational_job: 1900 / 1000,
    virginia_indirect_plus_induced_per_direct_job: +((m.indirect.jobs + m.induced.jobs) / m.direct.jobs).toFixed(3),
    model_for_louisiana: "not computed (no public multiplier held for Louisiana)" });
}

fs.writeFileSync(path.join(here, "..", "..", "docs", "reviews", "impact-datacenter-crosscheck-2026-11-26.json"), JSON.stringify({ computed: "2026-11-26", by: "site/scripts/dc-crosscheck.mjs", cases: out }, null, 1) + "\n");
console.log(JSON.stringify(out, null, 1));
