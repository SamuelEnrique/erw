// Energy Research Warehouse (ERW) site, chain 740 (lab-desktop window 3), session 10802: the datacenter in /impact.
// For one datacenter and each calendar year from its first construction year to its last operating year: on-site jobs
// and earnings (the reader's or an announced project's figures; wages from Census County Business Patterns), supply
// chain and induced effects where a public multiplier is held (Virginia, JLARC's IMPLAN tables), property tax on the
// building and the equipment by the state's rule and the reader's rates, sales and use tax on the equipment (bought again
// every refresh cycle) and on the building's taxable share, with the tax a state's datacenter exemption forgoes as its own
// line, state income tax on the earnings, a tax on the electricity bought where a statute sets one, and each stream's
// present value. docs/methods/forecast.md, the datacenter sections (internal), gives every formula and default.
//
// Pure and imports nothing, as lib/forecast.ts: the page passes the parameter files, check-values its own read of them.
// incomeTax is lib/forecast.ts's own, written again here so this file stands alone (a test holds them equal).

export type DcEffect = "onsite" | "supply_chain" | "induced" | "total";
export const DC_EFFECTS: DcEffect[] = ["onsite", "supply_chain", "induced", "total"];
export const DC_BASE_YEAR = 2025;
export const DC_DEFAULT_START = 2027;

type Stat = { n: number; low?: number; median?: number; high?: number; low_row?: string; high_row?: string };
type Part = { jobs: number; earnings_musd: number; quote: string };
export type DcIncome = {
  name: string; none?: boolean; brackets: { over_usd: number; rate: number }[];
  standard_deduction_single: number | null; personal_exemption_single: number | null; personal_credit_single: number | null;
};
export type DcRule = {
  name: string;
  sales_exemption?: { cite: string; covers: ("equipment" | "construction")[]; min_investment_usd: number; min_jobs: number;
    last_year?: number; term_years?: number; invest_before_year?: number; tip: string;
    /** session 10805: the statute exempts the state's rate only (Minnesota's refund at the 297A.62 rate) */
    rate_part?: "state";
    /** a least MW (Florida: a critical IT load of 100 MW) */
    min_mw?: number;
    /** the facility must be certified (here: its first construction year) before this year (South Carolina 2032, Minnesota 2042) */
    start_before_year?: number;
    /** a longer term for a larger investment (Maryland: 20 years with USD 250 million) */
    term_years_big?: { min_investment_usd: number; years: number };
    /** a discretionary abatement by application, held as words only (Nevada): never applied */
    discretionary?: boolean };
  /** session 10806: a least investment for the rule to apply (Montana's class seventeen, USD 50 million); below it no rule is held */
  property?: { building_ratio: number; equipment_ratio: number; cite: string; tip: string; min_investment_usd?: number };
  electricity?: { cite: string; kind: "monthly_blocks"; blocks: { upto_kwh: number | null; usd_per_kwh: number }[]; tip: string };
};
/** The parameter files the datacenter reads (site/data/forecast/): the page and check-values load them */
export type DcParams = {
  announced: { defaults: Record<"mw_stated" | "investment_per_mw" | "permanent_jobs_per_mw" | "permanent_jobs_per_billion" | "construction_jobs_per_billion", Stat>; computed?: string };
  rules: {
    split: { land_pct: number; building_pct: number; equipment_pct: number; other_pct: number; words: string };
    refresh: { years: number; words: string }; build: { months: number; words: string }; life: { years: number; words: string };
    multipliers: Record<string, { words: string; construction: Record<"direct" | "indirect" | "induced", Part>; operations: Record<"direct" | "indirect" | "induced", Part> }>;
    states: Record<string, DcRule>;
  };
  wages: { year: number; states: Record<string, { operations?: { per_job_usd: number }; construction?: { per_job_usd: number } }> };
  sales: { states: Record<string, { state_rate: number; avg_local_rate: number }> };
  income: { states: Record<string, DcIncome> };
  deflator: { index: Record<string, number> };
};

/** The reader's datacenter: one scenario. Percent fields are percents; null is "not given". */
export type DcInputs = {
  state: string;
  /** MW as the reader states them (IT capacity or the power required: the reader's own measure) */
  mw: number;
  /** total investment, USD million, 2025 dollars (land, building, equipment and other) */
  invest: number;
  start: number; build: number; life: number;
  /** the investment's split, percent: building and site, equipment, land (the rest is other spending) */
  bld: number; eq: number; land: number;
  /** operating years between equipment purchases (0: bought once) */
  refresh: number;
  /** permanent jobs on site; construction workers on site in each construction year */
  perm: number; cons: number;
  /** earnings per job, USD a year, 2025 dollars */
  opwage: number; conswage: number;
  /** sales tax rate, percent (state plus average local) */
  sales: number;
  /** the building's taxable purchases (materials), percent of its cost; null: not given (no public source read gives it) */
  matshare: number | null;
  /** apply the state's datacenter sales tax exemption where the project meets its thresholds (1) or not (0) */
  dcex: boolean;
  /** property tax: the reader's rates, percent of assessed value, on the building and on the equipment */
  brate: number | null; erate: number | null;
  /** the building's value falls in a straight line to 0 over this many years (null: held at its cost) */
  bldyears: number | null;
  /** an abatement of the property tax, percent, for this many operating years (null: every year) */
  abate: number; abateyears: number | null;
  /** session 10809: the equipment's taxable value in the years of its cycle, percent of its cost: the first year's, the points it
   *  falls each year, and its floor (100, 0, 0: held at cost, an upper bound; a county's schedule is typed, e.g. Loudoun's) */
  eqv1: number; eqstep: number; eqfloor: number;
  /** the electricity bought, MWh a year (null: not given) */
  mwh: number | null;
  /** real discount rate, percent */
  rate: number;
};

export type DcYear = {
  year: number; phase: "construction" | "operations";
  jobs: Record<DcEffect, number>; earnings: Record<DcEffect, number>;
  /** equipment and building purchases of the year (2025 dollars) */
  equipment: number; building: number;
  property: number | null; propb: number | null; prope: number | null;
  /** sales tax due before any exemption, forgone by the exemption, and paid */
  salesbefore: number | null; forgone: number | null; sales: number | null;
  income: number; elec: number | null;
  /** the taxable value of the year (building and equipment, assessed), where the reader's rates tax it */
  value: number | null; mwh: number | null;
};
export type DcStreams = { jobs: number; earnings: number; property: number | null; propb: number | null; prope: number | null;
  salesbefore: number | null; forgone: number | null; sales: number | null; income: number; elec: number | null };
export type DcResult = {
  ok: boolean; why?: string;
  years: DcYear[]; sums: DcStreams; pv: DcStreams & { taxes: number };
  construction: { jobs: Record<DcEffect, number>; earnings: Record<DcEffect, number> };
  operations: { jobs: Record<DcEffect, number>; earnings: Record<DcEffect, number> };
  chain: { held: boolean; note: string };
  exemption: { held: boolean; eligible: boolean; applied: boolean; note: string };
  property: { held: boolean; note: string };
  sales: { held: boolean; note: string };
  elec: { held: boolean; note: string };
};

const ZERO = (): Record<DcEffect, number> => ({ onsite: 0, supply_chain: 0, induced: 0, total: 0 });
const times = (r: Record<DcEffect, number>, f: number): Record<DcEffect, number> =>
  ({ onsite: r.onsite * f, supply_chain: r.supply_chain * f, induced: r.induced * f, total: r.total * f });
export const dcRound = (v: number, d: number) => Math.round(v * 10 ** d) / 10 ** d;
export function dcTo2025(P: DcParams, y: number): number {
  const a = P.deflator.index[String(DC_BASE_YEAR)], b = P.deflator.index[String(y)];
  if (!(a > 0) || !(b > 0)) throw new Error(`no deflator for ${y}`);
  return a / b;
}

/** One single filer's state income tax on wages w (lib/forecast.ts's incomeTax, written again) */
export function dcIncomeTax(s: DcIncome | undefined, w: number): number {
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

// ---- defaults ------------------------------------------------------------------------------------------------------
export function dcWage(P: DcParams, state: string, kind: "operations" | "construction"): number | null {
  const w = P.wages.states[state]?.[kind]?.per_job_usd;
  return w === undefined ? null : w * dcTo2025(P, P.wages.year);
}
/** The defaults of a state's datacenter. The size, investment and jobs follow what the reader set: an investment not
 *  given is the MW times the announced projects' median per MW, permanent jobs the MW times their median per MW, and
 *  construction workers the investment times their median per billion dollars. */
export function dcDefaults(P: DcParams, state: string, set: Partial<DcInputs> = {}): DcInputs {
  const D = P.announced.defaults, R = P.rules;
  const mw = set.mw ?? dcRound(D.mw_stated.median!, 3);
  const invest = set.invest ?? dcRound(mw * D.investment_per_mw.median!, 2);
  const st = P.sales.states[state];
  return {
    mw, invest, start: DC_DEFAULT_START, build: Math.ceil(R.build.months / 12), life: R.life.years,
    bld: R.split.building_pct, eq: R.split.equipment_pct, land: R.split.land_pct, refresh: R.refresh.years,
    perm: dcRound(mw * D.permanent_jobs_per_mw.median!, 1), cons: dcRound((invest / 1000) * D.construction_jobs_per_billion.median!, 1),
    opwage: dcRound(dcWage(P, state, "operations") ?? NaN, 0), conswage: dcRound(dcWage(P, state, "construction") ?? NaN, 0),
    sales: st ? dcRound((st.state_rate + st.avg_local_rate) * 100, 4) : 0, matshare: null, dcex: true,
    brate: null, erate: null, bldyears: null, abate: 0, abateyears: null, mwh: null, rate: 7, eqv1: 100, eqstep: 0, eqfloor: 0,
    ...set, state,
  };
}

// ---- pieces ----------------------------------------------------------------------------------------------------------
/** Virginia's ratios of indirect and induced to direct (JLARC Tables D-3 and D-5), or null where none is held */
export function dcChain(P: DcParams, state: string, phase: "construction" | "operations") {
  const m = P.rules.multipliers[state]?.[phase];
  if (!m) return null;
  return {
    jobs: { supply_chain: m.indirect.jobs / m.direct.jobs, induced: m.induced.jobs / m.direct.jobs },
    earnings: { supply_chain: m.indirect.earnings_musd / m.direct.earnings_musd, induced: m.induced.earnings_musd / m.direct.earnings_musd },
  };
}
/** Whether the project meets the state's exemption thresholds (the wage test is not checked) */
export function dcEligible(P: DcParams, x: DcInputs): { held: boolean; eligible: boolean; why: string } {
  const r = P.rules.states[x.state]?.sales_exemption;
  if (!r) return { held: false, eligible: false, why: "no datacenter sales tax exemption of this state has been read" };
  if (r.discretionary) return { held: true, eligible: false, why: "the state's relief is held as words only, not applied: its hover says why (an approval, or a threshold not read)" };
  const usd = x.invest * 1e6;
  const spent = r.invest_before_year === undefined ? usd
    : usd * Math.max(0, Math.min(x.build, r.invest_before_year - x.start)) / x.build;
  const okInv = spent >= r.min_investment_usd, okJobs = x.perm >= r.min_jobs;
  const okMw = r.min_mw === undefined || x.mw >= r.min_mw;
  const okStart = r.start_before_year === undefined || x.start < r.start_before_year;
  const why = okInv && okJobs && okMw && okStart ? "meets the statute's thresholds"
    : !okStart ? `the statute certifies only before ${r.start_before_year}`
    : !okMw ? `the MW are below the statute's ${r.min_mw}`
    : !okInv ? `the investment${r.invest_before_year !== undefined ? ` spent before ${r.invest_before_year}` : ""} is below the statute's USD ${(r.min_investment_usd / 1e6).toLocaleString("en-US")} million`
    : `the permanent jobs are below the statute's ${r.min_jobs}`;
  return { held: true, eligible: okInv && okJobs && okMw && okStart, why };
}
function exemptYear(P: DcParams, x: DcInputs, year: number): boolean {
  const r = P.rules.states[x.state]?.sales_exemption;
  if (!r) return false;
  if (r.last_year !== undefined && year > r.last_year) return false;
  const term = r.term_years_big && x.invest * 1e6 >= r.term_years_big.min_investment_usd ? r.term_years_big.years : r.term_years;
  if (term !== undefined && year >= x.start + term) return false;
  return true;
}
/** A year's tax on the electricity bought, by the state's statute; null where none is held or no MWh is given */
export function dcElecTax(P: DcParams, x: DcInputs): number | null {
  const e = P.rules.states[x.state]?.electricity;
  if (!e || x.mwh === null) return null;
  const month = (x.mwh * 1000) / 12;
  let tax = 0, lo = 0;
  for (const b of e.blocks) {
    const hi = b.upto_kwh ?? Infinity;
    if (month > lo) tax += (Math.min(month, hi) - lo) * b.usd_per_kwh;
    lo = hi;
  }
  return tax * 12;
}

// ---- the run ---------------------------------------------------------------------------------------------------------
export function dcRun(x: DcInputs, P: DcParams): DcResult {
  const nul: DcStreams = { jobs: 0, earnings: 0, property: null, propb: null, prope: null, salesbefore: null, forgone: null, sales: null, income: 0, elec: null };
  const empty: DcResult = {
    ok: false, years: [], sums: nul, pv: { ...nul, taxes: 0 }, construction: { jobs: ZERO(), earnings: ZERO() }, operations: { jobs: ZERO(), earnings: ZERO() },
    chain: { held: false, note: "" }, exemption: { held: false, eligible: false, applied: false, note: "" }, property: { held: false, note: "" },
    sales: { held: false, note: "" }, elec: { held: false, note: "" },
  };
  const ok = (v: number, lo: number) => Number.isFinite(v) && v >= lo;
  if (!ok(x.mw, 0.001) || !ok(x.invest, 0) || !ok(x.build, 1) || !ok(x.life, 1) || !ok(x.perm, 0) || !ok(x.cons, 0) || !ok(x.rate, 0)
    || !ok(x.bld, 0) || !ok(x.eq, 0) || !ok(x.land, 0) || x.bld + x.eq + x.land > 100 || !ok(x.refresh, 0)) return { ...empty, why: "an input is out of range" };
  if (!ok(x.opwage, 0) || !ok(x.conswage, 0)) return { ...empty, why: "no wage is held for this state: type one" };
  const usd = x.invest * 1e6;
  const bldCost = usd * x.bld / 100, eqCost = usd * x.eq / 100;
  const chC = dcChain(P, x.state, "construction"), chO = dcChain(P, x.state, "operations");
  const phase = (onsite: number, wage: number, ch: ReturnType<typeof dcChain>) => {
    const jobs = ZERO(), earnings = ZERO();
    jobs.onsite = onsite; earnings.onsite = onsite * wage;
    if (ch) {
      jobs.supply_chain = onsite * ch.jobs.supply_chain; jobs.induced = onsite * ch.jobs.induced;
      earnings.supply_chain = earnings.onsite * ch.earnings.supply_chain; earnings.induced = earnings.onsite * ch.earnings.induced;
    }
    jobs.total = jobs.onsite + jobs.supply_chain + jobs.induced; earnings.total = earnings.onsite + earnings.supply_chain + earnings.induced;
    return { jobs, earnings };
  };
  const c = phase(x.cons, x.conswage, chC), o = phase(x.perm, x.opwage, chO);
  const el = dcEligible(P, x);
  const rule = P.rules.states[x.state];
  const covers = rule?.sales_exemption?.covers ?? [];
  const prop = rule?.property && (rule.property.min_investment_usd === undefined || x.invest * 1e6 >= rule.property.min_investment_usd) ? rule.property : undefined;
  const st = P.income.states[x.state];
  const elec = dcElecTax(P, x);
  const years: DcYear[] = [];
  // the share of the rate an exemption reaches: the whole rate, or the state's rate only (never above the scenario's rate)
  const part = rule?.sales_exemption?.rate_part === "state" ? Math.min(1, (P.sales.states[x.state]?.state_rate ?? 0) * 100 / (x.sales || 1)) : 1;
  const tax = (equipment: number, building: number, year: number) => {
    const bTax = x.matshare === null ? 0 : building * (x.matshare / 100) * (x.sales / 100);
    const eTax = equipment * (x.sales / 100);
    const before = eTax + bTax;
    const applies = el.eligible && x.dcex && exemptYear(P, x, year);
    const forgone = applies ? ((covers.includes("equipment") ? eTax : 0) + (covers.includes("construction") ? bTax : 0)) * part : 0;
    return { before, forgone, paid: before - forgone };
  };
  for (let i = 0; i < x.build; i++) {
    const f = 1 / x.build, year = x.start + i;
    const equipment = eqCost * f, building = bldCost * f;
    const t = tax(equipment, building, year);
    const jobs = { ...c.jobs }, earnings = { ...c.earnings };
    years.push({ year, phase: "construction", jobs, earnings, equipment, building, property: null, propb: null, prope: null,
      salesbefore: t.before, forgone: t.forgone, sales: t.paid,
      income: jobs.total > 0 ? jobs.total * dcIncomeTax(st, earnings.total / jobs.total) : 0, elec: null, value: null, mwh: null });
  }
  for (let i = 0; i < x.life; i++) {
    const year = x.start + x.build + i;
    const equipment = x.refresh > 0 && i > 0 && i % x.refresh === 0 ? eqCost : 0;
    const t = tax(equipment, 0, year);
    const bval = bldCost * (x.bldyears !== null && x.bldyears > 0 ? Math.max(0, 1 - i / x.bldyears) : 1);
    const br = prop?.building_ratio ?? 1, er = prop?.equipment_ratio ?? 1;
    const ab = x.abate > 0 && (x.abateyears === null || i < x.abateyears) ? 1 - x.abate / 100 : 1;
    const propb = x.brate === null ? null : bval * br * (x.brate / 100) * ab;
    // the equipment's age in its cycle: bought in the build (age 0 in the first operating year) or again every refresh cycle
    const age = x.refresh > 0 ? i % x.refresh : i;
    const eqval = eqCost * Math.max(x.eqfloor, x.eqv1 - x.eqstep * age) / 100;
    const prope = x.erate === null ? null : eqval * er * (x.erate / 100) * ab;
    const value = x.brate === null && x.erate === null ? null : (x.brate === null ? 0 : bval * br) + (x.erate === null ? 0 : eqval * er);
    years.push({ year, phase: "operations", jobs: { ...o.jobs }, earnings: { ...o.earnings }, equipment, building: 0,
      property: propb !== null && prope !== null ? propb + prope : null, propb, prope,
      salesbefore: t.before, forgone: t.forgone, sales: t.paid,
      income: o.jobs.total > 0 ? o.jobs.total * dcIncomeTax(st, o.earnings.total / o.jobs.total) : 0,
      elec, value, mwh: x.mwh });
  }
  const disc = (t: number) => 1 / (1 + x.rate / 100) ** (t - x.start);
  const sum = (f: (y: DcYear) => number | null, pv: boolean) => {
    let s = 0, any = false;
    for (const y of years) { const v = f(y); if (v !== null) { any = true; s += v * (pv ? disc(y.year) : 1); } }
    return any ? s : null;
  };
  const streams = (pv: boolean): DcStreams => ({
    jobs: sum((y) => y.jobs.total, false)!, earnings: sum((y) => y.earnings.total, pv)!,
    property: years.some((y) => y.phase === "operations" && y.property === null) ? null : sum((y) => y.property, pv),
    propb: sum((y) => y.propb, pv), prope: sum((y) => y.prope, pv),
    salesbefore: sum((y) => y.salesbefore, pv), forgone: sum((y) => y.forgone, pv), sales: sum((y) => y.sales, pv),
    income: sum((y) => y.income, pv)!, elec: sum((y) => y.elec, pv),
  });
  const sums = streams(false), pvS = streams(true);
  const taxes = (pvS.property ?? 0) + (pvS.sales ?? 0) + pvS.income + (pvS.elec ?? 0);
  const propNote = x.brate === null && x.erate === null ? "no property tax rate is held statewide: the reader's rates are not given"
    : x.brate === null ? "the building's rate is not given" : x.erate === null ? "the equipment's rate is not given" : "";
  return {
    // construction over the build (job-years and their earnings), as lib/forecast.ts's construction lines are; each
    // construction year holds the workers on site the reader gives (an announced peak held in every year: an upper reading)
    ok: true, years, sums, pv: { ...pvS, taxes }, construction: { jobs: times(c.jobs, x.build), earnings: times(c.earnings, x.build) }, operations: o,
    chain: { held: chC !== null, note: chC ? "" : "no public multiplier for datacenters is held for this state: the figures are the on-site effect alone" },
    exemption: { held: el.held, eligible: el.eligible, applied: el.eligible && x.dcex, note: el.held ? (el.eligible ? (x.dcex ? "applied" : "not applied (the scenario's choice)") : el.why) : el.why },
    property: { held: x.brate !== null && x.erate !== null, note: propNote },
    sales: { held: true, note: x.matshare === null ? "on the equipment; the building's taxable share is not given" : "on the equipment and the building's taxable share" },
    elec: { held: elec !== null, note: elec !== null ? "" : !rule?.electricity ? "no statute on the electricity bought is read for this state" : "the electricity bought is not given" },
  };
}

/** How a datacenter figure is written (the page and check-values both read it): jobs as lib/forecast.ts writes them
 *  (one decimal under 100, whole from 100), MWh whole, every other figure in US dollars short */
export function dcDisplay(figure: string, v: number): string {
  const p = figure.split(":");
  if (p[1] === "jobs" || p[2] === "jobs") return v.toLocaleString("en-US", { maximumFractionDigits: v < 100 ? 1 : 0 });
  if (p[p.length - 1] === "mwh") return Math.round(v).toLocaleString("en-US");
  const a = Math.abs(v);
  if (a >= 1e9) return `USD ${(v / 1e9).toLocaleString("en-US", { maximumFractionDigits: 2 })} billion`;
  if (a >= 1e6) return `USD ${(v / 1e6).toLocaleString("en-US", { maximumFractionDigits: 1 })} million`;
  return `USD ${Math.round(v).toLocaleString("en-US")}`;
}

// ---- check keys ------------------------------------------------------------------------------------------------------
export const DC_KEY_ORDER: (keyof DcInputs)[] = ["state", "mw", "invest", "start", "build", "life", "bld", "eq", "land", "refresh", "perm", "cons",
  "opwage", "conswage", "sales", "matshare", "dcex", "brate", "erate", "bldyears", "abate", "abateyears", "mwh", "rate", "eqv1", "eqstep", "eqfloor"];
export function dcKey(x: DcInputs): string {
  return ["datacenter", ...DC_KEY_ORDER.map((k) => { const v = x[k]; return v === null ? "-" : typeof v === "boolean" ? (v ? "1" : "0") : String(v); })].join("|");
}
export function dcParseKey(key: string): { x: DcInputs; figure: string } | null {
  const p = key.split("|");
  if (p[0] !== "datacenter" || p.length !== DC_KEY_ORDER.length + 2) return null;
  const x: Record<string, unknown> = {};
  DC_KEY_ORDER.forEach((k, i) => {
    const v = p[i + 1];
    x[k] = k === "state" ? v : k === "dcex" ? v === "1" : v === "-" ? null : Number(v);
  });
  return { x: x as DcInputs, figure: p[p.length - 1] };
}
/** One figure of a run, by its name, as lib/forecast.ts's stat: c:<jobs|earnings>:<effect>, o:..., sum:<stream>,
 *  pv:<stream>, pv:taxes, y1:<stream>, year:<yyyy>:<stream>. Output is not computed for a datacenter: null. */
export function dcStat(r: DcResult, figure: string): number | null {
  if (!r.ok) return null;
  const p = figure.split(":");
  if (p[0] === "c" || p[0] === "o") {
    if (p[1] === "output") return null;
    if ((p[2] === "supply_chain" || p[2] === "induced") && !r.chain.held) return null;
    const g = p[0] === "c" ? r.construction : r.operations;
    const v = (g as Record<string, Record<string, number>>)[p[1]]?.[p[2]];
    return v === undefined ? null : v;
  }
  if (p[0] === "sum" || p[0] === "pv") {
    const g = p[0] === "sum" ? r.sums : r.pv;
    const v = (g as Record<string, number | null>)[p[1]];
    return v === undefined ? null : v;
  }
  const pick = (y: DcYear | undefined, s: string): number | null => {
    if (!y) return null;
    if (s === "jobs" || s === "earnings") return y[s].total;
    const v = (y as unknown as Record<string, number | null>)[s];
    return v === undefined ? null : v;
  };
  if (p[0] === "y1") return pick(r.years.find((y) => y.phase === "operations"), p[1]);
  if (p[0] === "year") return pick(r.years.find((y) => y.year === Number(p[1])), p[2]);
  return null;
}
