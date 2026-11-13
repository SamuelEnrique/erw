// Energy Research Warehouse (ERW) site, session 4202 (chain 239): the forecast model of tool 17, /impact. For one
// generating project and each calendar year from its first construction year to its last operating year: JEDI's jobs,
// earnings and output (nlr_jedi_multipliers), property tax by the state's statute where one is held, sales and use tax
// on construction spending, state income tax on the earnings, severance on a gas plant's in-state fuel, and each
// stream's present value. docs/methods/forecast.md (internal) gives every formula and default with its source; the
// section numbers below are that note's.
//
// This file is pure and imports nothing: the page passes the parameter files of site/data/forecast/ and the JEDI rows
// it read, and scripts/check-values.mjs passes its own read of both, so a figure's check key recomputes here exactly.
// Severance is a callback (the page wires lib/severance.ts's compute), so this file needs no path of its own.

export type TechKey = "land_based_wind" | "utility_pv" | "natural_gas" | "geothermal";
export type Effect = "onsite" | "supply_chain" | "induced" | "total";
export type Measure = "jobs" | "earnings" | "output";
export type Phase = "construction" | "operations";
export const TECH_KEYS: TechKey[] = ["land_based_wind", "utility_pv", "natural_gas", "geothermal"];
export const EFFECTS: Effect[] = ["onsite", "supply_chain", "induced", "total"];
export const MEASURES: Measure[] = ["jobs", "earnings", "output"];
export const BASE_YEAR = 2025;
/** the first full calendar year after the chain wrote this (13 November 2026); section 2 */
export const DEFAULT_START = 2027;

/** One row of nlr_jedi_multipliers as the live set gives it */
export type Row = { entity: string; variable: string; ts_utc: string; value: number | string };

/** The parameter files of site/data/forecast/, as the page and check-values load them */
export type Params = {
  jediCosts: { technologies: Record<TechKey, { dollar_year: number; states: Record<string, { cost_usd_per_mw: number }> }> };
  eiaCapex: { technologies: Record<TechKey, { base_usd_per_kw: number; case_mw: number; dollar_year: number; construction_months: number; operating_life_years: number; states: Record<string, { usd_per_kw: number; cities: { city: string; usd_per_kw: number }[] }> }> };
  deflator: { base_year: number; index: Record<string, number> };
  capacity: Record<"land_based_wind" | "utility_pv" | "utility_pv_ilr", { states: Record<string, { median: number; plants: number }>; us: { median: number; plants: number } }>;
  sales: { states: Record<string, { state_rate: number; avg_local_rate: number }> };
  income: { states: Record<string, IncomeState> };
  property: { states: Record<string, { name: string; rules: PropertyRule[]; in_lieu?: { quote: string } }> };
  taxable: { technologies: Record<TechKey, { taxable_share: number | null }> };
  gas: { heat_rate_btu_per_kwh: number; capacity_factor: number; price_usd_per_mmbtu: number | null; btu_per_cf: number };
  /** session 4218: sales tax exemptions read from statutes (sales_exemptions.json); absent in older callers */
  exemptions?: { states: Record<string, Partial<Record<TechKey, { exempt_pct: number }>>> };
};
export type IncomeState = {
  name: string; none?: boolean; brackets: { over_usd: number; rate: number }[];
  standard_deduction_single: number | null; personal_exemption_single: number | null; personal_credit_single: number | null;
};
export type PropertyRule = {
  id: string; technologies: TechKey[]; kind: "capacity" | "production" | "valuation";
  usd_per_mw_year?: number; usd_per_mwh?: number; min_mw?: number;
  tiers?: { min_mw_exclusive?: number; min_mw_ac_exclusive?: number; max_mw?: number; usd_per_mwh: number }[];
  schedule_pct?: number[]; then_pct?: number; requires?: string;
};

/** The reader's project: one scenario. Percent fields are percents (7 is 7 percent); null is "not given". */
export type Inputs = {
  tech: TechKey; state: string;
  /** MW: nameplate, or AC for PV */
  mw: number;
  /** capital cost, USD per kW (AC for PV), 2025 dollars */
  capex: number;
  start: number; build: number; life: number;
  /** local content, percent of JEDI's default shares */
  local: number;
  /** operating spending, percent of JEDI's default (JEDI's O&M costs are of 2010 to 2017; section 9) */
  om: number;
  /** real discount rate, percent */
  rate: number;
  /** capacity factor, ratio (wind and PV: the production taxes; gas: the fuel) */
  cf: number;
  /** PV: DC over AC */
  ilr: number;
  /** sales tax rate, percent (state plus average local) */
  sales: number;
  /** taxable share of construction spending, percent; null where none is held (geothermal) */
  taxable: number | null;
  /** exemption from sales tax on that share, percent */
  exempt: number;
  /** Iowa wind: the county's special valuation (427B.26) applies */
  iaval: boolean;
  /** local levy, USD per 1,000 of taxable value (Iowa's valuation) */
  levy: number | null;
  /** the reader's own property tax: effective rate, percent of capital cost, falling straight to 0 over `ownyears` */
  own: number | null; ownyears: number | null;
  /** gas plant: heat rate (Btu/kWh), in-state share of the fuel (percent), price (USD/MMBtu, 2025) */
  heat: number; instate: number; gasprice: number | null;
};

export type Streams = { jobs: number; earnings: number; output: number; property: number | null; sales: number | null; income: number; severance: number | null };
export type Year = {
  year: number; phase: Phase;
  jobs: Record<Effect, number>; earnings: Record<Effect, number>; output: Record<Effect, number>;
  property: number | null; sales: number | null; income: number; severance: number | null;
  /** session 4220: the year's MWh (operations, where a capacity factor is held) and the taxable value a valuation or the
   *  reader's own rate taxes (null where the tax is not on a value) */
  mwh: number | null; value: number | null;
};
export type Result = {
  ok: boolean; why?: string;
  years: Year[];
  sums: Streams;
  pv: Streams & { taxes: number };
  construction: { jobs: Record<Effect, number>; earnings: Record<Effect, number>; output: Record<Effect, number> };
  operations: { jobs: Record<Effect, number>; earnings: Record<Effect, number>; output: Record<Effect, number> };
  property: { held: boolean; rule: string | null; note: string };
  severance: { held: boolean; note: string };
  sales: { held: boolean; note: string };
};
export type Severance = (state: string, volumeMcf: number, priceUsdPerMcf: number) => number | null;

// ---- small helpers -------------------------------------------------------------------------------------------------
const ZERO = (): Record<Effect, number> => ({ onsite: 0, supply_chain: 0, induced: 0, total: 0 });
export const num = (v: number | string | null | undefined) => (v === null || v === undefined || v === "" ? NaN : Number(v));
/** index(2025) / index(y): a figure of year y in 2025 dollars (section 2) */
export function to2025(P: Params, y: number): number {
  const a = P.deflator.index[String(BASE_YEAR)], b = P.deflator.index[String(y)];
  if (!(a > 0) || !(b > 0)) throw new Error(`no deflator for ${y}`);
  return a / b;
}
export function jediPerMw(rows: Row[], tech: TechKey, state: string, phase: Phase, effect: Effect, measure: Measure): number | null {
  const r = rows.find((x) => x.entity === `nlr_jedi:${tech}:${state}:${phase}:${effect}` && x.variable === measure);
  const v = r ? num(r.value) : NaN;
  return Number.isFinite(v) ? v : null;
}

// ---- defaults (section 2) ------------------------------------------------------------------------------------------
export function capexDefault(P: Params, tech: TechKey, state: string): { usdPerKw: number; from: "state" | "base"; cities: string[] } {
  const e = P.eiaCapex.technologies[tech];
  const s = e.states[state];
  const v2023 = s ? s.usd_per_kw : e.base_usd_per_kw;
  return { usdPerKw: v2023 * to2025(P, e.dollar_year), from: s ? "state" : "base", cities: s ? s.cities.map((c) => c.city) : [] };
}
export function cfDefault(P: Params, tech: TechKey, state: string): { value: number; from: "state" | "us" | "jedi" } {
  if (tech === "natural_gas") return { value: P.gas.capacity_factor, from: "jedi" };
  if (tech === "geothermal") return { value: NaN, from: "us" };  // no production tax applies to it: not used
  const c = P.capacity[tech];
  return c.states[state] ? { value: c.states[state].median, from: "state" } : { value: c.us.median, from: "us" };
}
export function ilrDefault(P: Params, state: string): { value: number; from: "state" | "us" } {
  const c = P.capacity.utility_pv_ilr;
  return c.states[state] ? { value: c.states[state].median, from: "state" } : { value: c.us.median, from: "us" };
}
export function defaults(P: Params, tech: TechKey, state: string): Inputs {
  const e = P.eiaCapex.technologies[tech];
  const st = P.sales.states[state];
  const share = P.taxable.technologies[tech]?.taxable_share;
  return {
    tech, state, mw: e.case_mw, capex: round(capexDefault(P, tech, state).usdPerKw, 2),
    start: DEFAULT_START, build: Math.ceil(e.construction_months / 12), life: e.operating_life_years,
    local: 100, om: 100, rate: 7, cf: round(cfDefault(P, tech, state).value, 4), ilr: tech === "utility_pv" ? round(ilrDefault(P, state).value, 4) : 1,
    sales: st ? round((st.state_rate + st.avg_local_rate) * 100, 4) : 0, taxable: share === null || share === undefined ? null : round(share * 100, 4),
    exempt: P.exemptions?.states[state]?.[tech]?.exempt_pct ?? 0, iaval: false, levy: null, own: null, ownyears: null,
    heat: P.gas.heat_rate_btu_per_kwh, instate: 0, gasprice: P.gas.price_usd_per_mmbtu === null ? null : round(P.gas.price_usd_per_mmbtu, 4),
  };
}
export const round = (v: number, d: number) => Math.round(v * 10 ** d) / 10 ** d;

// ---- income tax (section 6) ----------------------------------------------------------------------------------------
/** One single filer's state income tax on wages w (2025 dollars), by the state's 2026 brackets */
export function incomeTax(s: IncomeState | undefined, w: number): number {
  if (!s || s.none || !(w > 0)) return 0;
  const taxable = Math.max(0, w - (s.standard_deduction_single ?? 0) - (s.personal_exemption_single ?? 0));
  let tax = 0;
  const b = s.brackets;
  for (let i = 0; i < b.length; i++) {
    const lo = b[i].over_usd, hi = i + 1 < b.length ? b[i + 1].over_usd : Infinity;
    if (taxable > lo) tax += (Math.min(taxable, hi) - lo) * b[i].rate;
  }
  return Math.max(0, tax - (s.personal_credit_single ?? 0));
}

// ---- property tax (section 4) --------------------------------------------------------------------------------------
export function propertyRules(P: Params, x: Inputs): PropertyRule[] {
  const st = P.property.states[x.state];
  return st ? st.rules.filter((r) => r.technologies.includes(x.tech)) : [];
}
function tierRate(r: PropertyRule, mw: number): number {
  if (r.usd_per_mwh !== undefined) return r.usd_per_mwh;
  for (const t of r.tiers ?? []) {
    const lo = t.min_mw_exclusive ?? t.min_mw_ac_exclusive ?? 0;
    if (mw > lo && (t.max_mw === undefined || mw <= t.max_mw)) return t.usd_per_mwh;
  }
  return 0;
}
/** The property tax of operating year i (0 is the first), or null when no rule or input gives one */
export function propertyTax(P: Params, x: Inputs, i: number): { tax: number | null; rule: string | null; value?: number | null } {
  const rules = propertyRules(P, x);
  const mwh = x.mw * 8760 * x.cf;
  const spend = x.capex * x.mw * 1000;
  if (rules.length) {
    let tax = 0, value: number | null = null, used: string[] = [];
    for (const r of rules) {
      if (r.min_mw !== undefined && x.mw < r.min_mw) continue;
      if (r.kind === "capacity") { tax += x.mw * (r.usd_per_mw_year ?? 0); used.push(r.id); }
      else if (r.kind === "production") {
        // a scenario with no capacity factor (geothermal) has no production tax: the Python and Stata files do the same
        const rate = tierRate(r, x.mw);
        if (rate > 0 && Number.isFinite(mwh)) { tax += mwh * rate; used.push(r.id); }
      }
      else if (r.kind === "valuation") {
        if (!x.iaval) continue;
        if (x.levy === null) return { tax: null, rule: r.id };
        const pct = i < (r.schedule_pct ?? []).length ? r.schedule_pct![i] : (r.then_pct ?? 0);
        value = spend * (pct / 100);
        tax += value * (x.levy / 1000); used.push(r.id);
      }
    }
    if (used.length) return { tax, rule: used.join("+"), value };
  }
  if (x.own !== null && x.ownyears !== null && x.ownyears > 0) {
    const share = Math.max(0, 1 - i / x.ownyears);
    return { tax: spend * share * (x.own / 100), rule: "own", value: spend * share };
  }
  return { tax: null, rule: null };
}

// ---- the run ---------------------------------------------------------------------------------------------------------
export function run(x: Inputs, rows: Row[], P: Params, sev?: Severance | null): Result {
  const empty: Result = {
    ok: false, years: [], sums: { jobs: 0, earnings: 0, output: 0, property: null, sales: null, income: 0, severance: null },
    pv: { jobs: 0, earnings: 0, output: 0, property: null, sales: null, income: 0, severance: null, taxes: 0 },
    construction: { jobs: ZERO(), earnings: ZERO(), output: ZERO() }, operations: { jobs: ZERO(), earnings: ZERO(), output: ZERO() },
    property: { held: false, rule: null, note: "" }, severance: { held: false, note: "" }, sales: { held: false, note: "" },
  };
  const jc = P.jediCosts.technologies[x.tech];
  const cost = jc?.states[x.state]?.cost_usd_per_mw;
  if (!cost) return { ...empty, why: "JEDI gives no figure for this technology in this state" };
  const ok = (v: number, lo: number) => Number.isFinite(v) && v >= lo;
  if (!ok(x.mw, 0.001) || !ok(x.capex, 0) || !ok(x.build, 1) || !ok(x.life, 1) || !ok(x.local, 0) || !ok(x.om, 0) || !ok(x.rate, 0)) return { ...empty, why: "an input is out of range" };
  const yJ = jc.dollar_year;
  const toNow = to2025(P, yJ);
  const S = x.capex * x.mw * 1000;                 // the reader's spending, 2025 dollars
  const sJedi = S / toNow;                          // the same in JEDI's dollars
  const L = x.local / 100;
  const basisMw = x.tech === "utility_pv" ? x.mw * x.ilr : x.mw;
  const c = { jobs: ZERO(), earnings: ZERO(), output: ZERO() }, o = { jobs: ZERO(), earnings: ZERO(), output: ZERO() };
  for (const e of EFFECTS) for (const m of MEASURES) {
    const pc = jediPerMw(rows, x.tech, x.state, "construction", e, m), po = jediPerMw(rows, x.tech, x.state, "operations", e, m);
    if (pc === null || po === null) return { ...empty, why: `JEDI's ${e} ${m} is not held for this state` };
    const k = m === "jobs" ? 1 : toNow;
    c[m][e] = (pc / cost) * sJedi * L * k;         // section 3: proportional to spending
    o[m][e] = po * basisMw * L * (x.om / 100) * k; // operating spending does not scale with capital cost; the reader may scale it
  }
  // sales tax (section 5)
  const salesHeld = x.taxable !== null;
  const salesTotal = salesHeld ? S * (x.taxable! / 100) * (x.sales / 100) * (1 - x.exempt / 100) : null;
  // severance (section 7)
  let sevYear: number | null = null, sevNote = "";
  if (x.tech === "natural_gas") {
    if (x.instate > 0 && sev && x.gasprice !== null) {
      const mmbtu = x.mw * 8760 * x.cf * x.heat / 1000;
      const mcf = mmbtu / (P.gas.btu_per_cf / 1000);
      sevYear = sev(x.state, mcf * (x.instate / 100), x.gasprice * (P.gas.btu_per_cf / 1000));
      sevNote = sevYear === null ? "no severance rule held for this state" : "";
    } else sevNote = x.instate > 0 ? "no severance rule held for this state" : "no in-state fuel given";
  } else sevNote = "a wind, solar or geothermal plant burns no gas";
  const st = P.income.states[x.state];
  const years: Year[] = [];
  let propRule: string | null = null, propHeld = false;
  for (let i = 0; i < x.build; i++) {
    const f = 1 / x.build;
    const jobs = scale(c.jobs, f), earnings = scale(c.earnings, f), output = scale(c.output, f);
    years.push({ year: x.start + i, phase: "construction", jobs, earnings, output, property: null,
      sales: salesTotal === null ? null : salesTotal * f, income: jobs.total > 0 ? jobs.total * incomeTax(st, earnings.total / jobs.total) : 0, severance: null,
      mwh: null, value: null });
  }
  for (let i = 0; i < x.life; i++) {
    const p = propertyTax(P, x, i);
    if (p.tax !== null) { propHeld = true; propRule = p.rule; }
    years.push({ year: x.start + x.build + i, phase: "operations", jobs: { ...o.jobs }, earnings: { ...o.earnings }, output: { ...o.output },
      property: p.tax, sales: null, income: o.jobs.total > 0 ? o.jobs.total * incomeTax(st, o.earnings.total / o.jobs.total) : 0,
      severance: x.tech === "natural_gas" ? sevYear : null,
      mwh: Number.isFinite(x.cf) ? x.mw * 8760 * x.cf : null, value: p.value ?? null });
  }
  const disc = (t: number) => 1 / (1 + x.rate / 100) ** (t - x.start);
  const sum = (f: (y: Year) => number | null, pv: boolean) => {
    let s = 0, any = false;
    for (const y of years) { const v = f(y); if (v !== null) { any = true; s += v * (pv ? disc(y.year) : 1); } }
    return any ? s : null;
  };
  const sums: Streams = {
    jobs: sum((y) => y.jobs.total, false)!, earnings: sum((y) => y.earnings.total, false)!, output: sum((y) => y.output.total, false)!,
    property: propHeld ? sum((y) => y.property, false) : null, sales: sum((y) => y.sales, false), income: sum((y) => y.income, false)!,
    severance: sevYear === null ? null : sum((y) => y.severance, false),
  };
  const pvS = {
    jobs: sums.jobs, earnings: sum((y) => y.earnings.total, true)!, output: sum((y) => y.output.total, true)!,
    property: propHeld ? sum((y) => y.property, true) : null, sales: sum((y) => y.sales, true), income: sum((y) => y.income, true)!,
    severance: sevYear === null ? null : sum((y) => y.severance, true),
  };
  const taxes = (pvS.property ?? 0) + (pvS.sales ?? 0) + pvS.income + (pvS.severance ?? 0);
  const rules = propertyRules(P, x);
  const propNote = propHeld ? (propRule === "own" ? "the reader's own rate" : "the state's statute")
    : rules.some((r) => r.kind === "valuation") ? (x.iaval ? "the local levy is not given" : "the county's special valuation is off and no other rule is held")
    : "no rule held for this state and technology";
  return {
    ok: true, years, sums, pv: { ...pvS, taxes }, construction: c, operations: o,
    property: { held: propHeld, rule: propRule, note: propNote },
    severance: { held: sevYear !== null, note: sevNote },
    sales: { held: salesHeld, note: salesHeld ? (x.exempt > 0 ? "after the exemption" : "before exemptions") : "no taxable share held for this technology" },
  };
}
function scale(r: Record<Effect, number>, f: number): Record<Effect, number> {
  return { onsite: r.onsite * f, supply_chain: r.supply_chain * f, induced: r.induced * f, total: r.total * f };
}

// ---- check keys (section 11) -----------------------------------------------------------------------------------------
// A figure's key is forecast|<every input of its scenario, in KEY_ORDER, "-" for not given>|<figure>, so that
// scripts/check-values.mjs recomputes it from its own read of the JEDI rows and the parameter files, with nothing else.
export const KEY_ORDER: (keyof Inputs)[] = ["tech", "state", "mw", "capex", "start", "build", "life", "local", "om", "rate", "cf", "ilr", "sales", "taxable",
  "exempt", "iaval", "levy", "own", "ownyears", "heat", "instate", "gasprice"];
export function inputsKey(x: Inputs): string {
  return ["forecast", ...KEY_ORDER.map((k) => { const v = x[k]; return v === null ? "-" : typeof v === "boolean" ? (v ? "1" : "0") : String(v); })].join("|");
}
export function parseKey(key: string): { x: Inputs; figure: string } | null {
  const p = key.split("|");
  if (p[0] !== "forecast" || p.length !== KEY_ORDER.length + 2) return null;
  const x: Record<string, unknown> = {};
  KEY_ORDER.forEach((k, i) => {
    const v = p[i + 1];
    x[k] = k === "tech" || k === "state" ? v : k === "iaval" ? v === "1" : v === "-" ? null : Number(v);
  });
  return { x: x as Inputs, figure: p[p.length - 1] };
}
/** One figure of a run, by its name:
 *   c:<measure>:<effect>, o:<measure>:<effect>   construction (over the build) and each operating year (JEDI's lines)
 *   sum:<stream>, pv:<stream>, pv:taxes            over the whole life, and its present value
 *   y1:<stream>                                     the first operating year (property, severance, income)
 *   year:<yyyy>:<stream>                            one year of the table (jobs, earnings, output, property, sales, income, severance) */
export function stat(r: Result, figure: string): number | null {
  if (!r.ok) return null;
  const p = figure.split(":");
  if (p[0] === "c" || p[0] === "o") {
    const g = p[0] === "c" ? r.construction : r.operations;
    const v = g[p[1] as Measure]?.[p[2] as Effect];
    return v === undefined ? null : v;
  }
  if (p[0] === "sum" || p[0] === "pv") {
    const g = p[0] === "sum" ? r.sums : r.pv;
    const v = (g as Record<string, number | null>)[p[1]];
    return v === undefined ? null : v;
  }
  const pick = (y: Year | undefined, s: string): number | null => {
    if (!y) return null;
    if (s === "jobs" || s === "earnings" || s === "output") return y[s].total;
    if (s === "mwh" || s === "value") return y[s];
    const v = (y as unknown as Record<string, number | null>)[s];
    return v === undefined ? null : v;
  };
  if (p[0] === "y1") return pick(r.years.find((y) => y.phase === "operations"), p[1]);
  if (p[0] === "year") return pick(r.years.find((y) => y.year === Number(p[1])), p[2]);
  return null;
}

// ---- the rows packed for the browser (lib/forecastdata.ts sends them; the page unpacks a scenario's) -----------------
const PHASES: Phase[] = ["construction", "operations"];
/** the order of a packed technology and state: phase, then effect, then measure */
export const PACK = PHASES.flatMap((p) => EFFECTS.flatMap((e) => MEASURES.map((m) => [p, e, m] as const)));
export type Packed = Record<string, number[]>;  // "<tech>:<state>" -> 24 numbers
export function pack(rows: Row[]): Packed {
  const at = new Map(rows.map((r) => [`${r.entity}|${r.variable}`, Number(r.value)]));
  const out: Packed = {};
  const keys = new Set(rows.map((r) => r.entity.split(":").slice(1, 3).join(":")));
  for (const k of keys) {
    const v = PACK.map(([p, e, m]) => at.get(`nlr_jedi:${k}:${p}:${e}|${m}`) ?? NaN);
    if (v.every(Number.isFinite)) out[k] = v;
  }
  return out;
}
export function unpack(p: Packed, tech: TechKey, state: string): Row[] {
  const v = p[`${tech}:${state}`];
  if (!v) return [];
  return PACK.map(([ph, e, m], i) => ({ entity: `nlr_jedi:${tech}:${state}:${ph}:${e}`, variable: m, ts_utc: "", value: v[i] }));
}

/** Session 4216: the planned generators of the four technologies (energy_projects' EIA-860M planned rows, in the live
 *  set), grouped by plant and technology: the left box's list of planned projects. A plant's MW is its generators'
 *  nameplate added (AC for solar); its year the earliest planned operation date; its county EIA-860M's. */
export type Planned = { id: string; name: string; tech: string; state: string; county: string; mw: number; year: number | null };
const GROUP_TECH: Record<string, string> = { wind: "land_based_wind", solar: "utility_pv", natural_gas: "natural_gas", geothermal: "geothermal" };
export function groupPlanned(rows: { entity_id: string; name: string | null; capacity_mw: number | string | null; tech: string | null; state: string | null; county: string | null; date: string | null }[]): Planned[] {
  const by = new Map<string, Planned>();
  for (const r of rows) {
    const tech = GROUP_TECH[r.tech ?? ""];
    const plant = r.entity_id.split(":").slice(0, 2).join(":");
    if (!tech || !r.state) continue;
    const k = `${plant}|${tech}`;
    const year = r.date ? Number(r.date.slice(0, 4)) : null;
    const p = by.get(k) ?? { id: `${plant.replace("eia860:", "")}-${tech}`, name: r.name ?? plant, tech, state: r.state.toLowerCase(), county: r.county ?? "", mw: 0, year };
    p.mw += Number(r.capacity_mw ?? 0);
    if (year !== null && (p.year === null || year < p.year)) p.year = year;
    by.set(k, p);
  }
  return [...by.values()].filter((p) => p.mw > 0).sort((a, b) => a.state.localeCompare(b.state) || a.name.localeCompare(b.name));
}

// ---- how a figure is written (session 4219): the page writes each figure so, and check-values compares the text with
// displayOf(figure, raw), so the forms live here, beside the arithmetic, where both read them ----------------------------
export function usdText(v: number): string {
  const a = Math.abs(v);
  if (a >= 1e9) return `USD ${(v / 1e9).toLocaleString("en-US", { maximumFractionDigits: 2 })} billion`;
  if (a >= 1e6) return `USD ${(v / 1e6).toLocaleString("en-US", { maximumFractionDigits: 1 })} million`;
  return `USD ${Math.round(v).toLocaleString("en-US")}`;
}
export const jobsText = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: v < 100 ? 1 : 0 });
/** The text of a figure by its name (stat's names): jobs as jobs, every other figure in US dollars */
export function displayOf(figure: string, v: number): string {
  const p = figure.split(":");
  const isJobs = p[1] === "jobs" || p[2] === "jobs";
  if (p[2] === "mwh") return Math.round(v).toLocaleString("en-US");  // session 4220: MWh, whole
  return isJobs ? jobsText(v) : usdText(v);
}
