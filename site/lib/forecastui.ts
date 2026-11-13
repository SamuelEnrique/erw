// Session 4211 (chain 239): the forecast page's fields and its address, for the server (the first draw) and the client
// (the panel). A scenario is held as numbers (ScenarioState's Values): technology and state as their place in TECHS and
// STATES, a switch as 0 or 1, and NaN for a field the reader has not set, which then follows its default for the
// technology and state in view (so a new state brings its own capital cost, capacity factor and tax rates). The address
// carries only what the reader set: scenario A under plain names, B under the same names after "b", and view=b.
import { STATES, TECHS } from "./impact";
import { capexDefault, cfDefault, defaults, ilrDefault, type Inputs, type Params, type TechKey } from "./forecast";

export type Values = Record<string, number>;
export type Both = { a: Values; b: Values; view: "a" | "b" };
export type Group = "project" | "spending" | "taxes" | "output" | "value";
export const GROUPS: { key: Group; title: string; open: boolean }[] = [
  { key: "project", title: "Project", open: true },
  { key: "spending", title: "Spending in the state", open: false },
  { key: "taxes", title: "Taxes", open: false },
  { key: "output", title: "Output and fuel", open: false },
  { key: "value", title: "Present value", open: true },
];
export type FieldDef = {
  key: keyof Inputs; label: string; unit: string; min: number; max: number; whole: boolean; group: Group;
  /** a list instead of a number */
  options?: (P: Params) => { value: number; label: string }[];
  /** whether the field means anything for this technology and state (otherwise it is not drawn) */
  applies?: (tech: TechKey, state: string, P: Params) => boolean;
  /** the source of its default, said in the field's hover tip */
  source: (tech: TechKey, state: string, P: Params) => string;
  /** a field whose default is "not given" may be emptied back to it */
  nullable?: boolean;
};

export const STATE_LIST = STATES.filter(([k]) => k !== "us");
const techIx = (k: string) => TECHS.findIndex((t) => t.key === k);
const stateIx = (k: string) => STATE_LIST.findIndex(([s]) => s === k);
export const techOfIx = (i: number): TechKey => (TECHS[i] ?? TECHS[0]).key;
export const stateOfIx = (i: number): string => (STATE_LIST[i] ?? STATE_LIST[0])[0];
const n = (v: number, d = 0) => v.toLocaleString("en-US", { maximumFractionDigits: d });

/** session 4218: the words of each exemption read from a statute (site/data/forecast/sales_exemptions.json quotes them) */
const EXEMPT_WORDS: Record<string, string> = {
  "mn:land_based_wind": "Minnesota Statutes 297A.68, subd. 12, exempts wind energy conversion systems used as an electric power source and the materials to build them: 100 percent.",
  "ia:land_based_wind": "Iowa Code 423.3(54) exempts wind energy conversion property and the materials to build it: 100 percent.",
  "tx:land_based_wind": "Texas: the Comptroller applies the manufacturing exemption (Tax Code 151.318) to equipment that generates electricity, such as wind turbines and solar modules, but not to every item of a facility (its letter rulings); the exempt share is not held, so the default is 0 and this sales tax is an upper bound before that exemption.",
  "tx:utility_pv": "Texas: the Comptroller applies the manufacturing exemption (Tax Code 151.318) to equipment that generates electricity, such as wind turbines and solar modules, but not to every item of a facility (its letter rulings); the exempt share is not held, so the default is 0 and this sales tax is an upper bound before that exemption.",
  "tx:natural_gas": "Texas: the Comptroller applies the manufacturing exemption (Tax Code 151.318) to equipment that generates electricity, such as wind turbines and solar modules, but not to every item of a facility (its letter rulings); the exempt share is not held, so the default is 0 and this sales tax is an upper bound before that exemption.",
  "ne:land_based_wind": "Nebraska's exemption for community-based energy development projects (Revised Statutes 77-2704.57) was repealed by Laws 2026, LB901, operative 1 July 2026 (the Legislature's page, read 13 November 2026): none (0).",
  "ne:utility_pv": "Nebraska's exemption for community-based energy development projects (Revised Statutes 77-2704.57) was repealed by Laws 2026, LB901, operative 1 July 2026 (the Legislature's page, read 13 November 2026): none (0).",
  "nd:utility_pv": "North Dakota Century Code 57-39.2-04.2 exempts the production equipment and every other purchase for building a power plant, which includes any non-coal, non-wind generating facility of 100 kW or more selling its power: 100 percent.",
  "nd:natural_gas": "North Dakota Century Code 57-39.2-04.2 exempts the production equipment and every other purchase for building a power plant, which includes any non-coal, non-wind generating facility of 100 kW or more selling its power: 100 percent.",
  "nd:geothermal": "North Dakota Century Code 57-39.2-04.2 exempts the production equipment and every other purchase for building a power plant, which includes any non-coal, non-wind generating facility of 100 kW or more selling its power: 100 percent.",
  "nd:land_based_wind": "North Dakota Century Code 57-39.2-04.2 counts a wind facility only if it was completed before 1 January 2017: a new wind plant has no exemption (0).",
  "ia:utility_pv": "Iowa Code 423.3(90) exempts solar energy equipment, equipment primarily used to collect and convert solar radiation or carry it to a point of use: the modules and inverters, 67.2 percent of the tax on JEDI's materials and equipment. Racking and wiring are not named.",
};

/** fault 7: a statute's capacity or production tax is held for this technology and state (Iowa's valuation is optional, so
 *  the reader's own rate stays offered there) */
export const statuteHeld = (t: TechKey, s: string, P: Params) =>
  (P.property.states[s]?.rules ?? []).some((r) => r.technologies.includes(t) && r.kind !== "valuation" && r.kind !== "exempt_years" && r.kind !== "capacity_option" && r.kind !== "own_exempt" && !r.adds_to_property);

export const FIELDS: FieldDef[] = [
  { key: "tech", label: "Technology", unit: "", min: 0, max: TECHS.length - 1, whole: true, group: "project",
    options: () => TECHS.map((t, i) => ({ value: i, label: t.label })),
    source: () => "Each is NLR's own JEDI model of that kind of plant, read for every state (nlr_jedi_multipliers). NLR publishes no JEDI model for battery storage." },
  { key: "state", label: "State", unit: "", min: 0, max: STATE_LIST.length - 1, whole: true, group: "project",
    options: () => STATE_LIST.map(([, name], i) => ({ value: i, label: name })),
    source: () => "JEDI's multipliers, the tax rules and the default costs are each the state's own." },
  { key: "mw", label: "Size", unit: "MW", min: 1, max: 10000, whole: false, group: "project",
    source: (t, _s, P) => `EIA's case size for this technology, ${n(P.eiaCapex.technologies[t].case_mw)} MW (capital cost study for AEO2025, case ${(P.eiaCapex.technologies[t] as unknown as { case: number }).case}).${t === "utility_pv" ? " MW of AC." : ""}` },
  { key: "capex", label: "Capital cost", unit: "USD/kW, 2025", min: 100, max: 20000, whole: false, group: "project",
    source: (t, s, P) => {
      const d = capexDefault(P, t, s);
      return d.from === "state"
        ? `EIA's overnight cost in this state (${d.cities.join(", ")}${d.cities.length > 1 ? ": their mean" : ""}), 2023 dollars converted to 2025 by the GDP price index. Capital cost study for AEO2025, Appendix A. Excludes sales tax and financing.`
        : "EIA gives no figure for this technology in this state: its base case, 2023 dollars converted to 2025 by the GDP price index. Capital cost study for AEO2025.";
    } },
  { key: "start", label: "First construction year", unit: "", min: 2026, max: 2060, whole: true, group: "project",
    source: () => "The first full calendar year from today. Every dollar is a 2025 dollar whatever the year." },
  { key: "build", label: "Construction", unit: "years", min: 1, max: 10, whole: true, group: "project",
    source: (t, _s, P) => `EIA's plant construction time for this technology, ${P.eiaCapex.technologies[t].construction_months} months, in whole years.` },
  { key: "life", label: "Operation", unit: "years", min: 1, max: 60, whole: true, group: "project",
    source: (t, _s, P) => `EIA's operating life for this technology, ${P.eiaCapex.technologies[t].operating_life_years} years (capital cost study for AEO2025).` },
  { key: "local", label: "Local content", unit: "% of JEDI's", min: 0, max: 200, whole: true, group: "spending",
    source: () => "JEDI's default share of each line of spending bought in the state. 100 is JEDI's own; a project's spending plan moves it." },
  { key: "om", label: "Operating spending", unit: "% of JEDI's", min: 0, max: 300, whole: true, group: "spending",
    source: () => "JEDI's default operating and maintenance spending (costs of 2010 to 2017). 100 is JEDI's own." },
  { key: "sales", label: "Sales tax rate", unit: "%", min: 0, max: 15, whole: false, group: "taxes",
    source: () => "The state's rate plus its population-weighted average local rate, midyear 2026. Tax Foundation (CC BY-NC 4.0)." },
  { key: "taxable", label: "Taxable share of spending", unit: "%", min: 0, max: 100, whole: false, group: "taxes", nullable: true,
    source: (t) => t === "geothermal" ? "JEDI's geothermal model holds no sales tax line: no share is held." : "JEDI's own base for sales tax, its materials and equipment purchases, as a share of its cost before tax." },
  { key: "exempt", label: "Sales tax exemption", unit: "% of the tax", min: 0, max: 100, whole: false, group: "taxes",
    source: (t, s, P) => (EXEMPT_WORDS[`${s}:${t}`] ?? (P.exemptions?.states[s]?.[t] ? "The state's statute exempts these purchases." : "No exemption of this state for this technology has been read: 0, so the sales tax is before exemptions.")) },
  { key: "iaval", label: "Local option by ordinance or agreement", unit: "", min: 0, max: 1, whole: true, group: "taxes",
    options: () => [{ value: 0, label: "No" }, { value: 1, label: "Yes" }],
    applies: (t, s) => (s === "ia" && t === "land_based_wind") || (s === "or" && t === "utility_pv"),
    source: (_t, s) => (s === "or"
      ? "Oregon (2015 c.571, notes to ORS 307.175): a county and a solar project outside any city may agree to exempt it and take a fee in lieu, USD 5,500 to 7,000 per MW of nameplate a year, for up to 20 years; agreements end with projects exempt by 2 January 2028."
      : "Iowa Code 427B.26 applies where the county or city has adopted it by ordinance: 0 percent of net acquisition cost the first year, 5 points more each year, 30 percent from the seventh.") },
  { key: "optrate", label: "Fee in lieu", unit: "USD per MW a year", min: 0, max: 20000, whole: false, group: "taxes", nullable: true,
    applies: (t, s) => s === "or" && t === "utility_pv",
    source: () => "Within the statute's USD 5,500 to 7,000 (a rate outside it is held to it). Default 7,000, the statute's maximum and its one fixed rate until the 2021 amendment set the range." },
  { key: "levy", label: "Local levy", unit: "USD per 1,000", min: 0, max: 200, whole: false, group: "taxes", nullable: true,
    applies: (t, s) => s === "ia" && t === "land_based_wind",
    source: () => "No statewide figure is held: the county's consolidated levy, in dollars per 1,000 of taxable value." },
  { key: "own", label: "Property tax, effective rate", unit: "% of cost", min: 0, max: 10, whole: false, group: "taxes", nullable: true, applies: (t, s, P) => !statuteHeld(t, s, P),
    // fault 16: where a statute is held but leaves years or the choice open (Iowa's valuation, Kansas's exemption, Oregon's
    // agreement), the rate covers those years, not "no statute"
    source: (t, s, P) => ((P.property.states[s]?.rules ?? []).some((r) => r.technologies.includes(t) && r.kind === "own_exempt") && s === "az"
      ? "Arizona values renewable energy equipment at 20 percent of its depreciated cost through 2040 (Revised Statutes 42-14155): a rate typed here is the reader's own, applied to 20 percent of the capital cost until 2040 and to all of it after, as the value falls. The statute's 90 percent cap on depreciation and its deduction of federal tax credits from the cost are not modeled."
      : (P.property.states[s]?.rules ?? []).some((r) => r.technologies.includes(t) && r.kind === "own_exempt")
      ? "Florida exempts 80 percent of a renewable energy device's assessed value through 2037 (Statutes 196.182): a rate typed here is the reader's own, applied to the remaining 20 percent of the capital cost until 2037 and to all of it after, as the value falls. Land and other real property are not exempt; the tool applies the 80 percent to the whole capital cost."
      : (P.property.states[s]?.rules ?? []).some((r) => r.technologies.includes(t) && r.adds_to_property)
      ? "The state's excise on production is held; the property tax on the plant is not: a rate typed here is the reader's own, added to the excise, applied to the capital cost as it falls."
      : (P.property.states[s]?.rules ?? []).some((r) => r.technologies.includes(t))
      ? "The state's statute leaves some years or cases open (without the local option, or after an exemption or an agreement ends): a rate typed here is the reader's own for those years, applied to the capital cost as it falls."
      : "No statute is held for this state and technology: a rate typed here is the reader's own, applied to the capital cost as it falls.") },
  { key: "ownyears", label: "Taxable value falls to 0 over", unit: "years", min: 1, max: 60, whole: true, group: "taxes", nullable: true, applies: (t, s, P) => !statuteHeld(t, s, P),
    source: () => "The reader's own: the years over which the taxable value falls in a straight line." },
  { key: "cf", label: "Capacity factor", unit: "ratio", min: 0.01, max: 1, whole: false, group: "output",
    applies: (t) => t !== "geothermal",
    source: (t, s, P) => {
      if (t === "natural_gas") return "JEDI's default for its gas plant, 0.65. It sets the fuel the plant burns.";
      const d = cfDefault(P, t, s);
      const c = P.capacity[t as "land_based_wind" | "utility_pv"];
      return d.from === "state"
        ? `The median of ${c.states[s].plants} plants in this state (${t === "land_based_wind" ? "2025, built 2019 to 2024; LBNL and EIA-860" : "2024 AC, built 2019 to 2023; LBNL"}). It sets the production taxes.`
        : `The national median of ${c.us.plants} plants (fewer than 3 in this state). It sets the production taxes.`;
    } },
  { key: "ilr", label: "Loading ratio", unit: "DC over AC", min: 1, max: 2, whole: false, group: "output",
    applies: (t) => t === "utility_pv",
    source: (_t, s, P) => { const d = ilrDefault(P, s); return d.from === "state" ? "The median plant in this state, built 2019 to 2023 (LBNL). JEDI counts PV in MW of DC." : "The national median plant, built 2019 to 2023 (LBNL). JEDI counts PV in MW of DC."; } },
  { key: "heat", label: "Heat rate", unit: "Btu/kWh", min: 5000, max: 15000, whole: true, group: "output",
    applies: (t) => t === "natural_gas",
    source: () => "EIA's combined cycle (2x2x1) heat rate, higher heating value. Capital cost study for AEO2025, case 5." },
  { key: "instate", label: "Fuel produced in the state", unit: "%", min: 0, max: 100, whole: false, group: "output",
    applies: (t) => t === "natural_gas",
    source: () => "JEDI's gas model saves 0. Severance is the wells' tax: it applies only to the share produced in the state, where the state's rule is held (Texas, Louisiana, New Mexico)." },
  { key: "gasprice", label: "Gas price", unit: "USD/MMBtu, 2025", min: 0.5, max: 30, whole: false, group: "output", nullable: true,
    applies: (t) => t === "natural_gas",
    source: () => "The mean Henry Hub spot price of 2025's twelve months, EIA's Short-Term Energy Outlook." },
  { key: "rate", label: "Discount rate, real", unit: "%", min: 0, max: 20, whole: false, group: "value",
    source: () => "OMB Circular A-94's base case for benefit-cost analysis, 7 percent real. Its Appendix C gives 2.0 percent for 30-year Treasury borrowing (2026), the rate for cost-effectiveness analysis." },
];
export const FIELD = Object.fromEntries(FIELDS.map((f) => [f.key, f])) as Record<string, FieldDef>;

/** The address name of a field: tech, state, mw, cost (USD/kW; old /impact links' capex was a percent and is dropped), ... */
const NAME: Partial<Record<keyof Inputs, string>> = { capex: "cost" };
export const param = (k: string, view: "a" | "b") => `${view === "b" ? "b" : ""}${NAME[k as keyof Inputs] ?? k}`;
const PARAMS = new Set(FIELDS.flatMap((f) => [param(f.key, "a"), param(f.key, "b")]).concat(["view", "capex", "abate", "proj", "bproj"]));
export const dropParam = (name: string) => PARAMS.has(name);

/** A scenario's values from the address (NaN for every field not given; technology and state always given). */
export function parse(q: Record<string, string | undefined>): Both {
  const one = (view: "a" | "b", base?: Values): Values => {
    const v: Values = {};
    for (const f of FIELDS) {
      const raw = q[param(f.key, view)];
      let x = raw === undefined || raw === "" ? NaN : f.key === "tech" ? techIx(raw) : f.key === "state" ? stateIx(raw) : Number(raw);
      if (!Number.isFinite(x) || x < 0 && (f.key === "tech" || f.key === "state")) x = NaN;
      if (Number.isFinite(x)) x = clampTo(f, x);
      v[f.key] = x;
    }
    if (!Number.isFinite(v.tech)) v.tech = base ? base.tech : techIx("land_based_wind");
    if (!Number.isFinite(v.state)) v.state = base ? base.state : stateIx("tx");
    return v;
  };
  const a = one("a");
  return { a, b: one("b", a), view: q.view === "b" ? "b" : "a" };
}
export function clampTo(f: FieldDef, x: number): number {
  const y = Math.min(f.max, Math.max(f.min, x));
  return f.whole ? Math.round(y) : y;
}
/** The address parameters of a state: only what the reader set */
export function query(s: Both): [string, string][] {
  const out: [string, string][] = [];
  for (const view of ["a", "b"] as const) {
    const v = s[view];
    for (const f of FIELDS) {
      const x = v[f.key];
      if (!Number.isFinite(x)) continue;
      if (f.key === "tech") { if (view === "a" ? x !== techIx("land_based_wind") : x !== s.a.tech) out.push([param("tech", view), techOfIx(x)]); continue; }
      if (f.key === "state") { if (view === "a" ? x !== stateIx("tx") : x !== s.a.state) out.push([param("state", view), stateOfIx(x)]); continue; }
      out.push([param(f.key, view), String(x)]);
    }
  }
  if (s.view === "b") out.push(["view", "b"]);
  return out;
}
/** The model's inputs: each field the reader set, else its default for the technology and state */
export function resolve(P: Params, v: Values): Inputs {
  const tech = techOfIx(v.tech), state = stateOfIx(v.state);
  const d = defaults(P, tech, state);
  const x = { ...d } as Record<string, unknown>;
  for (const f of FIELDS) {
    if (f.key === "tech" || f.key === "state") continue;
    const val = v[f.key];
    if (Number.isFinite(val)) x[f.key] = f.key === "iaval" ? val === 1 : val;
  }
  return x as Inputs;
}

/** Session 4216: the planned project of each scenario, held as its place in the page's list (Values.proj, NaN for none)
 *  and written in the address by its id (proj, bproj), so a link names the project, not a place in a list. */
export function withProjects(s: Both, q: Record<string, string | undefined>, ids: string[]): Both {
  const at = (v: string | undefined) => (v ? ids.indexOf(v) : -1);
  const a = at(q.proj), b = at(q.bproj);
  return { ...s, a: { ...s.a, proj: a >= 0 ? a : NaN }, b: { ...s.b, proj: b >= 0 ? b : NaN } };
}
export function queryWithProjects(s: Both, ids: string[]): [string, string][] {
  const out = query(s);
  for (const view of ["a", "b"] as const) {
    const i = s[view].proj;
    if (Number.isFinite(i) && ids[i]) out.push([view === "b" ? "bproj" : "proj", ids[i]]);
  }
  return out;
}
