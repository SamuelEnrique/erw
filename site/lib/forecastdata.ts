// Session 4212 (chain 239): the forecast page's data on the server. The parameter files of site/data/forecast/ (each
// with its source; docs/methods/forecast.md), trimmed to the numbers the model reads before they go to the browser,
// and the JEDI rows packed as 24 numbers a technology and state (EFFECTS x MEASURES x the two phases, in PACK's order),
// so that every change of scenario A or B is computed in the browser with no request.
import jediCosts from "@/data/forecast/jedi_costs.json";
import eiaCapex from "@/data/forecast/eia_capex.json";
import deflator from "@/data/forecast/deflator.json";
import capacity from "@/data/forecast/capacity_factors.json";
import sales from "@/data/forecast/sales_tax.json";
import income from "@/data/forecast/income_tax.json";
import property from "@/data/forecast/property_rules.json";
import taxable from "@/data/forecast/jedi_taxable.json";
import gas from "@/data/forecast/gas.json";
import exemptions from "@/data/forecast/sales_exemptions.json";
import severanceRules from "@/data/severance_rules.json";
import { type Params } from "./forecast";
export { pack, unpack, PACK, groupPlanned, type Packed, type Planned } from "./forecast";

export function params(): Params {
  const ec = eiaCapex.technologies as unknown as Params["eiaCapex"]["technologies"];
  const slimEc = Object.fromEntries(Object.entries(ec).map(([t, v]) => [t, {
    base_usd_per_kw: v.base_usd_per_kw, case_mw: v.case_mw, dollar_year: v.dollar_year, construction_months: v.construction_months,
    operating_life_years: v.operating_life_years, case: (v as unknown as { case: number }).case,
    states: Object.fromEntries(Object.entries(v.states).map(([s, x]) => [s, { usd_per_kw: x.usd_per_kw, cities: x.cities.map((c) => ({ city: c.city, usd_per_kw: c.usd_per_kw })) }])),
  }]));
  const jc = jediCosts.technologies as unknown as Params["jediCosts"]["technologies"];
  const slimJc = Object.fromEntries(Object.entries(jc).map(([t, v]) => [t, { dollar_year: v.dollar_year,
    states: Object.fromEntries(Object.entries(v.states).map(([s, x]) => [s, { cost_usd_per_mw: x.cost_usd_per_mw }])) }]));
  const inc = income.states as unknown as Params["income"]["states"];
  const slimInc = Object.fromEntries(Object.entries(inc).map(([s, v]) => [s, { name: v.name, none: v.none, brackets: v.brackets.map((b) => ({ over_usd: b.over_usd, rate: b.rate })),
    standard_deduction_single: v.standard_deduction_single, personal_exemption_single: v.personal_exemption_single, personal_credit_single: v.personal_credit_single }]));
  const prop = property.states as unknown as Params["property"]["states"];
  const slimProp = Object.fromEntries(Object.entries(prop).map(([s, v]) => [s, { name: v.name, rules: v.rules.map((r) => ({
    id: r.id, technologies: r.technologies, kind: r.kind, usd_per_mw_year: r.usd_per_mw_year, usd_per_mwh: r.usd_per_mwh, min_mw: r.min_mw,
    tiers: r.tiers, schedule_pct: r.schedule_pct, then_pct: r.then_pct, requires: r.requires, default_levy: r.default_levy, levy_words: r.levy_words, tip: r.tip, own_tip: r.own_tip, option_tip: r.option_tip, rate_tip: r.rate_tip,
    assessment_ratio: r.assessment_ratio, depr_pct_per_year: r.depr_pct_per_year, floor_pct: r.floor_pct, usd_per_mw_value: r.usd_per_mw_value,
    years: r.years, usd_per_mw_min: r.usd_per_mw_min, usd_per_mw_max: r.usd_per_mw_max, default_usd_per_mw: r.default_usd_per_mw,
    exempt_years: r.exempt_years, adds_to_property: r.adds_to_property, exempt_share: r.exempt_share, until_year: r.until_year,
    above_mw: r.above_mw, below_mw: r.below_mw, exempt_steps: r.exempt_steps })) }]));  // fault 15: every field of PropertyRule kept (Kansas's years were dropped)
  return {
    jediCosts: { technologies: slimJc } as Params["jediCosts"],
    eiaCapex: { technologies: slimEc } as unknown as Params["eiaCapex"],
    deflator: { base_year: deflator.base_year, index: deflator.index as Record<string, number> },
    capacity: capacity as unknown as Params["capacity"],
    sales: { states: Object.fromEntries(Object.entries(sales.states).map(([s, v]) => [s, { state_rate: v.state_rate, avg_local_rate: v.avg_local_rate }])) },
    income: { states: slimInc } as Params["income"],
    property: { states: slimProp } as Params["property"],
    taxable: { technologies: Object.fromEntries(Object.entries(taxable.technologies).map(([t, v]) => [t, { taxable_share: v.taxable_share }])) } as Params["taxable"],
    gas: { heat_rate_btu_per_kwh: gas.heat_rate_btu_per_kwh, capacity_factor: gas.capacity_factor, price_usd_per_mmbtu: gas.price_usd_per_mmbtu, btu_per_cf: gas.btu_per_cf },
    exemptions: { states: Object.fromEntries(Object.entries(exemptions.states).map(([s, v]) => [s, Object.fromEntries(Object.entries(v).map(([t, e]) => [t, { exempt_pct: e.exempt_pct, tip: (e as { tip?: string }).tip }]))])) } as Params["exemptions"],
  };
}

/** The gas rules of the three states /severance holds (the only part of its rules the forecast reads) */
export function gasSeverance(): unknown {
  const r = severanceRules as unknown as { version: string; sources: Record<string, unknown>; states: Record<string, { name: string; products: Record<string, unknown>; value_deduction?: unknown }> };
  return { version: r.version, sources: {}, states: Object.fromEntries(Object.entries(r.states).map(([k, v]) => [k, { name: v.name, value_deduction: v.value_deduction, products: { gas: v.products.gas } }])) };
}
