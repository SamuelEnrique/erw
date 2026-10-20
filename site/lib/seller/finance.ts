// Session 186: the finance of "What a generator earns" (/cost-of-power/seller), scenarios A and B, as session 179 built
// it for the battery (lib/battery/finance.ts). Pure arithmetic, no React and no imports: Node runs this file as it is
// (scripts/test-seller-finance.mjs, which also holds its arithmetic equal to the battery page's), and
// tests/test_session186.py holds a Python mirror of every function to 1e-6. Every formula is stated in
// docs/methods/generator_earns_algorithm.md, section 11. Everything here is per kW of nameplate; the page scales by the
// reader's size.
//
// Eight assumptions, all arithmetic after the model: capital cost, debt share, interest rate, term, fixed O&M,
// degradation, project life, hurdle rate. None is inside the model, so the revenue of the last twelve months, the
// capture price and the worst month are the page's own in both scenarios.
//
// Session 212 (the owner's chain prompt of 12 October 2026, as session 208 did for the battery): the contract is two
// more scenario assumptions, its share and its price, both 0 by default, so the default is fully merchant and every
// figure at a share of 0 is what it was. For solar and wind the contract is a share of the energy at a price per MWh;
// for a battery and a gas peaker, whose energy depends on the price, it is a toll on a share of the capacity, USD per
// kW-month (the battery page's form). The page says which (Contract.kind). The standalone contract panel is gone.
//
// Session 264 (the owner's list of 14 October 2026 for this tool): the PPA term is the eleventh assumption, "PPA term,
// years" (`ppa`, letter `y`, 1 to 40, whole). Until now every contract ran for the debt's years; now it runs for its
// own term, cut to the project life. Its default is the asset's life (Lazard's economic life, the debt's own default
// term), so at the defaults every figure is what it was. An older link that changed a scenario's debt term and holds a
// contract now runs that contract for the life, not the shorter term (a shared address must open what the browser
// showed, so the PPA term is never inferred from the debt's). A set of assumptions without the key (an older caller)
// runs the contract for the debt's years.
//
// Session 353 (the chain of 20 October 2026, night): two more assumptions in Financing, the tax credits, 0 by default so
// every default figure is what it was. The investment tax credit (`itc`, letter `i`) is a percent of the capital cost,
// received in the first year; the production tax credit (`ptc`, letter `x`) is USD per MWh of the plant's energy (the
// last twelve months' energy, falling with the degradation) in each of the first ten years. Both reach the cash flows to
// equity, so NPV, IRR and the breakeven PPA price; neither is counted in debt coverage (a credit is a tax figure, not
// cash from the plant). The page offers each credit only for an asset it names (SellerScenarios.tsx). And the contract
// has a shape (Contract.shape): "generated", the default and the only shape until now, pays the contract price on the
// contracted share of the energy as it is made; "block" is a fixed volume, the same MWh a year spread flat over every
// hour and settled against the hub's average of every hour, so the plant keeps all of its market revenue and pays the
// hub's flat price on the block. An older set of assumptions without the two keys reads as no credit.

export type Key = "capex" | "share" | "rate" | "term" | "fom" | "deg" | "life" | "hurdle" | "cshare" | "cprice" | "ppa" | "itc" | "ptc";
export type Assumptions = Record<Key, number>;
/** The thirteen, in the order the page lists them (session 212: the contract's share and price; session 264: the PPA
 * term; session 353: the two tax credits last). */
export const KEYS: Key[] = ["capex", "share", "rate", "term", "fom", "deg", "life", "hurdle", "cshare", "cprice", "ppa", "itc", "ptc"];
/** The eight of session 186: the ones every asset's arithmetic reads the same way. */
export const FINANCE_KEYS: Key[] = ["capex", "share", "rate", "term", "fom", "deg", "life", "hurdle"];
/** Session 353: the contract's three, and the two tax credits. */
export const CONTRACT_KEYS: Key[] = ["cshare", "cprice", "ppa"];
export const CREDIT_KEYS: Key[] = ["itc", "ptc"];
/** The years the production tax credit is paid: ten, its term under sections 45 and 45Y of the Internal Revenue Code. */
export const PTC_YEARS = 10;
/** What the contract is for the asset: a share of the energy at a price per MWh (solar, wind), or a toll on a share of
 * the capacity, USD per kW-month (a battery, a gas peaker). `energyKw` is the last twelve months' energy, MWh per kW
 * of nameplate, which an energy contract is priced on. */
export type Contract = {
  kind: "energy" | "toll"; energyKw: number;
  /** session 353: an energy contract's shape ("generated" when absent), and the hub's average price of every hour over
   * the same months, USD per MWh, which a block is settled against (null when not held: the block is then not offered) */
  shape?: "generated" | "block"; flat?: number | null;
};
export const NO_CONTRACT: Contract = { kind: "toll", energyKw: 0 };

export type Spec = {
  key: Key; letter: string; label: string; unit: string; min: number; max: number; whole: boolean;
  /** the step of the sensitivity chart, in the assumption's own unit, and how the chart states it */
  swing: number; swingWords: string;
  /** how the differing value reads in a column header, and in the last row ("B: <words(b)> against <plain(a)>") */
  short: (v: number) => string; words: (v: number) => string; plain: (v: number) => string;
  /** the source of the default, as the page prints it (the page adds the asset's own range to the two costs) */
  source: string;
};
const n = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
export const LAZARD = "Lazard, Levelized Cost of Energy+, June 2025";
/** Session 208, the owner's ruling of 12 October 2026: the hurdle rate's default is Lazard's cost of equity, 12
 * percent, as Lazard's June 2025 report states its financing: "60% debt at an 8% interest rate and 40% equity at a 12%
 * cost" (read 11 October 2026; docs/methods/battery_earns_algorithm.md, "Cross-checks"). The NPV is to equity, after
 * the debt payments, so equity's cost discounts it. From session 196 to 207 it was the weighted cost, 0.6 x 8 + 0.4 x
 * 12 = 9.6; before that 8, equal to the interest rate, with no source. The datacenter page keeps 9.6 (the same ruling). */
export const HURDLE = 12;
/** Session 196, the same ruling, for the battery among this page's assets: Lazard's storage cases (LCOS v10.0) give a
 * battery degradation of 2.6% a year (lib/battery/finance.ts, DEG). Solar, wind and a gas peaker keep a default of
 * none: the ruling names the battery, and the page says no cited rate is held for them. */
export const BATTERY_DEG = 2.6;
export const BATTERY_DEG_SOURCE = `${LAZARD} (LCOS v10.0): battery degradation of 2.6 percent a year in its utility-scale cases of 2 and 4 hours. The model itself has no loss of output with age: here the rate is a yearly cut to revenue`;
/** Session 298 (the owner's ruling 7a of 18 October 2026): solar's degradation default is the ATB's 0.7 percent a
 * year; wind and the gas peaker still hold none. The NPV of the default solar case moves with it (the page's source
 * line and the methods note say by how much). */
export const SOLAR_DEG = 0.7;
export const SOLAR_DEG_SOURCE = "NREL, Annual Technology Baseline 2025, utility-scale PV: a degradation rate of 0.7 percent a year. The model itself has no loss of output with age: here the rate is a yearly cut to revenue";
export const SPECS: Record<Key, Spec> = {
  capex: { key: "capex", letter: "c", label: "Capital cost", unit: "USD per kW", min: 0, max: 10000, whole: false, swing: 100, swingWords: "USD 100 per kW",
    short: (v) => `capex ${n(v)} USD/kW`, words: (v) => `capex USD ${n(v)} per kW`, plain: n, source: `${LAZARD}, the midpoint of its range` },
  share: { key: "share", letter: "s", label: "Debt share", unit: "percent of capital cost", min: 0, max: 100, whole: false, swing: 10, swingWords: "10 points",
    short: (v) => `debt share ${n(v)}%`, words: (v) => `debt share ${n(v)} percent`, plain: n, source: `${LAZARD}: 60% debt at an 8% interest rate` },
  rate: { key: "rate", letter: "r", label: "Interest rate", unit: "percent a year", min: 0, max: 30, whole: false, swing: 1, swingWords: "1 point",
    short: (v) => `interest ${n(v)}%`, words: (v) => `interest rate ${n(v)} percent`, plain: n, source: `${LAZARD}: 60% debt at an 8% interest rate` },
  term: { key: "term", letter: "t", label: "Term of the debt", unit: "years", min: 1, max: 40, whole: true, swing: 5, swingWords: "5 years",
    short: (v) => `term ${n(v)} years`, words: (v) => `term ${n(v)} years`, plain: n, source: `${LAZARD}: economic life sets the debt amortization schedule, so the term is this asset's life` },
  fom: { key: "fom", letter: "f", label: "Fixed O&M", unit: "USD per kW a year", min: 0, max: 500, whole: false, swing: 5, swingWords: "USD 5 per kW a year",
    short: (v) => `fixed O&M ${n(v)} USD/kW-yr`, words: (v) => `fixed O&M USD ${n(v)} per kW a year`, plain: n, source: `${LAZARD}, the midpoint of its range` },
  deg: { key: "deg", letter: "d", label: "Degradation", unit: "percent a year", min: 0, max: 20, whole: false, swing: 1, swingWords: "1 point",
    short: (v) => `degradation ${n(v)}% a year`, words: (v) => `degradation ${n(v)} percent a year`, plain: n, source: "The model has no loss of output with age. No cited rate is held, so the default is none" },
  life: { key: "life", letter: "l", label: "Project life", unit: "years", min: 1, max: 40, whole: true, swing: 5, swingWords: "5 years",
    short: (v) => `life ${n(v)} years`, words: (v) => `project life ${n(v)} years`, plain: n, source: `${LAZARD}: the life of this asset` },
  hurdle: { key: "hurdle", letter: "h", label: "Hurdle rate", unit: "percent a year", min: 0, max: 40, whole: false, swing: 1, swingWords: "1 point",
    short: (v) => `hurdle ${n(v)}%`, words: (v) => `hurdle rate ${n(v)} percent`, plain: n, source: `${LAZARD}: "60% debt at an 8% interest rate and 40% equity at a 12% cost". The default is that cost of equity, ${HURDLE} percent: the NPV is to equity, after the debt payments` },
  // session 212: the contract. The unit's words depend on the asset (the page sets them from Contract.kind)
  cshare: { key: "cshare", letter: "n", label: "Contract share", unit: "percent", min: 0, max: 100, whole: false, swing: 10, swingWords: "10 points",
    short: (v) => `contract ${n(v)}%`, words: (v) => `contract share ${n(v)} percent`, plain: n, source: "No contract: the default is fully merchant. A contracted share is paid the contract price every month of the debt's years and earns nothing from the market" },
  cprice: { key: "cprice", letter: "p", label: "Contract price", unit: "USD", min: 0, max: 1000, whole: false, swing: 1, swingWords: "USD 1",
    short: (v) => `contract USD ${n(v)}`, words: (v) => `contract price USD ${n(v)}`, plain: n, source: "No contract: the default is fully merchant. The price is the reader's own term; no published price is held" },
  // session 264: the contract's length, the eleventh
  ppa: { key: "ppa", letter: "y", label: "PPA term", unit: "years", min: 1, max: 40, whole: true, swing: 5, swingWords: "5 years",
    short: (v) => `PPA ${n(v)} ${v === 1 ? "year" : "years"}`, words: (v) => `PPA term ${n(v)} ${v === 1 ? "year" : "years"}`, plain: n, source: `The years the contract pays its price, cut to the project life; after them the whole plant is in the market. No published PPA term is held, so the default is this asset's life (${LAZARD}), the debt's own default term: at the default the contract runs as it did before this field` },
  // session 353: the tax credits, none by default
  itc: { key: "itc", letter: "i", label: "Investment tax credit", unit: "percent of capital cost", min: 0, max: 70, whole: false, swing: 10, swingWords: "10 points",
    short: (v) => `ITC ${n(v)}%`, words: (v) => `investment tax credit ${n(v)} percent`, plain: n, source: "No credit: the default is none. The credit is that percent of the capital cost, received in the first year. The page holds no figure for whether this project qualifies, or at what rate" },
  ptc: { key: "ptc", letter: "x", label: "Production tax credit", unit: "USD per MWh", min: 0, max: 100, whole: false, swing: 5, swingWords: "USD 5 per MWh",
    short: (v) => `PTC ${n(v)} USD/MWh`, words: (v) => `production tax credit USD ${n(v)} per MWh`, plain: n, source: `No credit: the default is none. The credit is paid on each MWh of the first ${PTC_YEARS} years, the credit's term under sections 45 and 45Y of the Internal Revenue Code, on the last twelve months' energy falling with the degradation. The page holds no figure for whether this project qualifies, or at what rate` },
};
/** The contract's unit and the chart's words for an asset (session 212). */
export function contractUnits(kind: Contract["kind"]): { shareUnit: string; priceUnit: string; priceStep: string } {
  return kind === "energy"
    ? { shareUnit: "percent of the energy", priceUnit: "USD per MWh", priceStep: "USD 1 per MWh" }
    : { shareUnit: "percent of the capacity", priceUnit: "USD per kW-month", priceStep: "USD 1 per kW-month" };
}

/** The defaults for an asset: its Lazard capital cost, fixed O&M and life (lib/merchant.ts, DEFAULTS), Lazard's
 * financing (60 percent debt at 8 percent, repaid over the life), and the two that no source in the repository gives. */
export function defaultsOf(costs: { capex: number; fom: number; life: number; deg?: number }): Assumptions {
  return { capex: costs.capex, share: 60, rate: 8, term: costs.life, fom: costs.fom, deg: costs.deg ?? 0, life: costs.life, hurdle: HURDLE, cshare: 0, cprice: 0, ppa: costs.life, itc: 0, ptc: 0 };
}

/** One value brought inside its bounds, or to the default when it cannot be read. */
export function bound(key: Key, v: number, d: Assumptions): number {
  if (!Number.isFinite(v)) return d[key];
  const s = SPECS[key];
  const x = Math.min(s.max, Math.max(s.min, v));
  return s.whole ? Math.round(x) : x;
}

export type View = "a" | "b";
export type Scenarios = { a: Assumptions; b: Assumptions; view: View };
/** Both scenarios from the address: <a or b><letter>, each defaulted and bounded; `v=b` puts B in view.
 * Session 195: scenario A sets the page's headline, and the two fields "Your plant" held until then are gone. Their
 * names still open the same headline in an older link, as old names of scenario A's own: `fom` is A's fixed O&M, and
 * `ds`, the annual debt payments in USD for `mw` megawatts, is the capital cost at which A's debt share, interest rate
 * and term give that payment. A's own parameter wins over an old name (`af` over `fom`, `ac` over `ds`). */
export function parseScenarios(q: Record<string, string | undefined>, d: Assumptions, mw = 0): Scenarios {
  const given = (name: string) => q[name] !== undefined && q[name] !== "";
  const one = (p: View): Assumptions => {
    const out = { ...d };
    for (const k of KEYS) {
      const raw = q[p + SPECS[k].letter];
      if (raw !== undefined && raw !== "") out[k] = bound(k, Number(raw), d);
    }
    return out;
  };
  const a = one("a");
  if (!given("af") && given("fom")) a.fom = bound("fom", Number(q.fom), d);
  if (!given("ac") && given("ds") && mw > 0) {
    const ds = Math.round(Number(q.ds)), per = 1000 * (a.share / 100) * crf(a.rate / 100, debtYears(a)) * mw;
    if (Number.isFinite(ds) && ds >= 0 && per > 0 && debtUsd(a, mw) !== ds) a.capex = bound("capex", ds / per, d);
  }
  return { a, b: one("b"), view: q.v === "b" ? "b" : "a" };
}
/** The two names "Your plant" held until session 195: read once as scenario A's, then dropped from the address. */
export const isOldParam = (name: string) => name === "fom" || name === "ds";
/** The address parameters of both scenarios: only what differs from the defaults, so no parameter means the defaults. */
export function scenarioQuery(s: Scenarios, d: Assumptions): [string, string][] {
  const out: [string, string][] = [];
  for (const p of ["a", "b"] as View[]) for (const k of KEYS) if (s[p][k] !== d[k]) out.push([p + SPECS[k].letter, String(s[p][k])]);
  if (s.view === "b") out.push(["v", "b"]);
  return out;
}
/** Whether a parameter name is one of the scenarios' (so that the page's other links can carry or drop it). */
export const isScenarioParam = (name: string) => name === "v" || /^[ab][csrtfdlhnpyix]$/.test(name);
/** The scenarios' parameters of a query string, to append to another address of the page. A change of asset (or of a
 * battery's duration) drops the capital cost, the fixed O&M, the term, the life and (session 264) the PPA term, whose
 * defaults are the asset's. */
export function carry(search: string, sameAsset: boolean): string {
  const out: string[] = [];
  for (const [k, v] of new URLSearchParams(search)) {
    if (!isScenarioParam(k)) continue;
    if (!sameAsset && /^[ab][cftly]$/.test(k)) continue;
    out.push(`${k}=${encodeURIComponent(v)}`);
  }
  return out.length ? `&${out.join("&")}` : "";
}
/** The assumptions that differ between A and B, in the page's order. */
export const differing = (a: Assumptions, b: Assumptions): Key[] => KEYS.filter((k) => a[k] !== b[k]);
/** The last row, in words: "B: capex USD 1,200 per kW against 1,375; hurdle rate 10 percent against 8." */
export function differenceWords(a: Assumptions, b: Assumptions): string {
  const ks = differing(a, b);
  if (!ks.length) return "A and B hold the same assumptions.";
  return `B: ${ks.map((k) => `${SPECS[k].words(b[k])} against ${SPECS[k].plain(a[k])}`).join("; ")}.`;
}

// ---------------------------------------------------------------------------------------------------------------------
// The arithmetic. Rates and shares are in percent, as the reader types them. USD per kW of nameplate.

/** The level annual payment per dollar borrowed at `rate` (a fraction) over `years`; at a rate of zero, 1 / years. */
export const crf = (rate: number, years: number) => (rate === 0 ? 1 / years : rate / (1 - (1 + rate) ** -years));
/** The years the debt is repaid over: its term, cut to the project life when the term is longer. */
export const debtYears = (a: Assumptions) => Math.min(a.term, a.life);
/** Session 264: the years the contract pays its price: the PPA term, cut to the project life; the debt's years for a
 * set of assumptions that holds no PPA term (an older caller). */
export const contractYears = (a: Assumptions) => Math.min(a.ppa ?? debtYears(a), a.life);
/** Annual debt payments, USD per kW: the capital cost times the debt share, level over the debt's years. */
export const debtService = (a: Assumptions) => a.capex * (a.share / 100) * crf(a.rate / 100, debtYears(a));
/** Annual debt payments in whole USD for `mw` megawatts: what the page's coverage divides by, and what its check keys
 * carry. The order of the multiplication is the page's own (lib/merchant.ts, debtPerMw, times the megawatts), so the
 * defaults give the figure the page showed before session 195 to the last dollar. */
export const debtUsd = (a: Assumptions, mw: number) => Math.round(a.capex * 1000 * (a.share / 100) * crf(a.rate / 100, debtYears(a)) * mw);
/** Market revenue in year t (1 is the first), USD per kW: the last twelve months' revenue, falling by the degradation
 * rate each year after the first. */
export const revenueInYear = (a: Assumptions, revKw: number, t: number) => revKw * (1 - a.deg / 100) ** (t - 1);
/** Session 212: the contract's income a year, USD per kW of nameplate: for an energy contract the contracted share of
 * the last twelve months' energy at the contract price; for a toll the contracted share of the capacity at the price,
 * twelve months. 0 with no contract (an older set of assumptions, without the two keys, is read as none). */
export const contractYear = (a: Assumptions, c: Contract = NO_CONTRACT) =>
  ((a.cshare ?? 0) / 100) * (a.cprice ?? 0) * (c.kind === "energy" ? c.energyKw : 12);
/** The uncontracted share of the plant, a fraction: 1 with no contract. */
export const merchantShare = (a: Assumptions) => 1 - (a.cshare ?? 0) / 100;
/** Session 353: what the market pays a plant under contract in a year of the contract, USD per kW, on that year's market
 * revenue `rev`: the uncontracted share of it (the shape "generated", as every contract until now); for a block, all of
 * it less the hub's flat price on the block's volume (the contracted share of the energy). */
export const contractedMarket = (a: Assumptions, rev: number, c: Contract = NO_CONTRACT) =>
  c.shape === "block" && c.kind === "energy" && c.flat !== null && c.flat !== undefined ? rev - ((a.cshare ?? 0) / 100) * c.energyKw * c.flat : merchantShare(a) * rev;
/** Income in year t, USD per kW: for the contract's years (session 264: the PPA term; the debt's years until then) the
 * contract plus what the market pays the plant beside it (the uncontracted share of the market revenue; session 353:
 * for a block, contractedMarket); after them the whole plant in the market. At a contract share of 0 this is the market
 * revenue in every year. */
export const incomeInYear = (a: Assumptions, revKw: number, t: number, c: Contract = NO_CONTRACT) =>
  t <= contractYears(a) ? contractYear(a, c) + contractedMarket(a, revenueInYear(a, revKw, t), c) : revenueInYear(a, revKw, t);
/** Session 353: the tax credits in year t, USD per kW: the investment tax credit, a percent of the capital cost, in year
 * 1; the production tax credit on the year's energy (the last twelve months' energy, falling by the degradation rate)
 * in the first PTC_YEARS years. 0 with neither (an older set of assumptions, without the keys, is read as none). */
export const creditInYear = (a: Assumptions, t: number, c: Contract = NO_CONTRACT) =>
  (t === 1 ? ((a.itc ?? 0) / 100) * a.capex : 0) + (t <= PTC_YEARS && (a.ptc ?? 0) > 0 ? (a.ptc ?? 0) * c.energyKw * (1 - a.deg / 100) ** (t - 1) : 0);
/** The cash flows to equity, USD per kW, years 0 to the project life: the equity paid in at year 0, then each year's
 * income less fixed O&M less the debt payment while the debt lasts (session 353: plus the year's tax credits, when the
 * scenario holds one; with none the flows are what they were, to the last digit). */
export function flows(a: Assumptions, revKw: number, c: Contract = NO_CONTRACT): number[] {
  const ds = debtService(a), dy = debtYears(a);
  const credits = (a.itc ?? 0) > 0 || (a.ptc ?? 0) > 0;
  const out = [-a.capex * (1 - a.share / 100)];
  for (let t = 1; t <= a.life; t++) out.push(incomeInYear(a, revKw, t, c) - a.fom - (t <= dy ? ds : 0) + (credits ? creditInYear(a, t, c) : 0));
  return out;
}
/** Net present value of yearly cash flows at `ratePct` percent: the sum of flow t over (1 + rate)^t. */
export function npv(ratePct: number, fl: number[]): number {
  const r = ratePct / 100;
  let s = 0;
  for (let t = 0; t < fl.length; t++) s += fl[t] / (1 + r) ** t;
  return s;
}
export const IRR_LOW = -99, IRR_HIGH = 1000;   // the bracket, percent a year
/** The internal rate of return, percent a year, by bisection between -99 and 1,000 percent. Null when the net present
 * value has the same sign at both ends of the bracket (no rate in it sets the value to zero: for example when no year's
 * cash flow is positive). Where the flows change sign more than once there can be several such rates; this returns the
 * one the bisection reaches. */
export function irr(fl: number[]): number | null {
  let lo = IRR_LOW, hi = IRR_HIGH;
  let flo = npv(lo, fl);
  const fhi = npv(hi, fl);
  if (!Number.isFinite(flo) || !Number.isFinite(fhi)) return null;
  if (flo === 0) return lo;
  if (fhi === 0) return hi;
  if (flo > 0 === fhi > 0) return null;
  for (let i = 0; i < 200 && hi - lo > 1e-10; i++) {
    const mid = (lo + hi) / 2, fm = npv(mid, fl);
    if (fm === 0) return mid;
    if (fm > 0 === flo > 0) { lo = mid; flo = fm; } else hi = mid;
  }
  return (lo + hi) / 2;
}
/** Debt coverage on a year's revenue: the contract plus the uncontracted share of the revenue, less fixed O&M, over
 * the debt payments (session 212; at a contract share of 0, revenue less fixed O&M over the debt payments, as
 * before). Null with no debt. */
export function coverage(a: Assumptions, revKw: number, c: Contract = NO_CONTRACT): number | null {
  const ds = debtService(a);
  return ds > 0 ? (contractYear(a, c) + contractedMarket(a, revKw, c) - a.fom) / ds : null;
}
/** Debt coverage in one month: the month's revenue per kW less a twelfth of the fixed O&M, over a twelfth of the debt
 * payments (the page's own monthly coverage, lib/merchant.ts). Null with no debt. */
export function monthCoverage(a: Assumptions, monthKw: number): number | null {
  const ds = debtService(a);
  return ds > 0 ? (monthKw - a.fom / 12) / (ds / 12) : null;
}
export const TARGET = 1.25;
/** The contract price for the whole of the energy, USD per MWh, at which coverage is `target`: solving
 * (price x energy - fom) / debt = target, with `energyKw` the last twelve months' energy in MWh per kW. Solar and
 * wind, whose output does not depend on the price. Null with no debt or no energy. */
export function contractPrice(a: Assumptions, energyKw: number, target = TARGET): number | null {
  const ds = debtService(a);
  return ds > 0 && energyKw > 0 ? (target * ds + a.fom) / energyKw : null;
}
/** The toll on the whole asset, USD per kW-month, at which coverage is `target`: solving
 * (12 x toll - fom) / debt = target (the battery page's breakeven toll). A battery and a gas peaker, whose energy
 * depends on the price. Null with no debt. */
export function breakevenToll(a: Assumptions, target = TARGET): number | null {
  const ds = debtService(a);
  return ds > 0 ? (target * ds + a.fom) / 12 : null;
}

/** Session 235 (the owner's task of 12 October 2026: "the results show the breakeven PPA price"): the contract price at
 * which the net present value to equity is zero, the scenario's other assumptions held. For solar and wind it is a
 * price for power, USD per MWh (a PPA); for a battery and a gas peaker a toll, USD per kW-month. The contract is on
 * `share` percent of the plant: the scenario's own contract share when it holds one, else the whole plant (100). It
 * runs for the debt's years (session 264: for the PPA term), as every contract of this page does, and the uncontracted share earns the market's
 * revenue. NPV is a straight line in the price, so the price is exact: -NPV at a price of 0, over the present value of
 * one dollar of price on the contracted share through the debt's years. It does not read the scenario's own contract
 * price. Null when nothing is contracted or the contract has no energy to price; a value at or below 0 says NPV is
 * already at or above zero with the contracted share paid nothing. */
export const ppaShare = (a: Assumptions) => ((a.cshare ?? 0) > 0 ? a.cshare : 100);
export function breakevenPpa(a: Assumptions, revKw: number, c: Contract = NO_CONTRACT, share = ppaShare(a)): number | null {
  const unit = c.kind === "energy" ? c.energyKw : 12;
  if (!(share > 0) || !(unit > 0)) return null;
  const at0 = npv(a.hurdle, flows({ ...a, cshare: share, cprice: 0 }, revKw, c));
  const r = a.hurdle / 100, dy = contractYears(a);  // session 264: the PPA term's years
  let perDollar = 0;
  for (let t = 1; t <= dy; t++) perDollar += ((share / 100) * unit) / (1 + r) ** t;
  return perDollar > 0 ? -at0 / perDollar : null;
}
/** Session 235, "Make B a PPA": the scenario with the whole plant under contract at its breakeven PPA price, rounded up
 * to the cent (so NPV is zero or a few dollars above) and kept inside the price's bounds. Null where there is no
 * breakeven price. Nothing else of the scenario changes, and no default moves. */
export function asPpa(a: Assumptions, revKw: number, c: Contract = NO_CONTRACT): Assumptions | null {
  const p = breakevenPpa(a, revKw, c, 100);
  if (p === null || !Number.isFinite(p)) return null;
  const price = Math.min(SPECS.cprice.max, Math.max(SPECS.cprice.min, Math.ceil(p * 100 - 1e-9) / 100));
  return { ...a, cshare: 100, cprice: price };
}

export type Result = { debt: number; coverage: number | null; npv: number; irr: number | null };
/** Everything a scenario's column shows that depends on its finance and on revenue, from the last twelve months'
 * revenue per kW. */
export function resultOf(a: Assumptions, revKw: number, c: Contract = NO_CONTRACT): Result {
  const fl = flows(a, revKw, c);
  return { debt: debtService(a), coverage: coverage(a, revKw, c), npv: npv(a.hurdle, fl), irr: irr(fl) };
}

export type Side = { value: number; npv: number };
export type Bar = { key: Key; label: string; step: string; base: number; down: Side | null; up: Side | null; size: number };
/** The sensitivity of the net present value: each assumption moved by its stated step down and up, the others held. A
 * side is null when the moved value leaves the assumption's bounds. Sorted by the larger of the two moves, largest
 * first; ties keep the page's order. */
export function sensitivity(a: Assumptions, revKw: number, c: Contract = NO_CONTRACT): Bar[] {
  const at = (x: Assumptions) => npv(x.hurdle, flows(x, revKw, c));
  const base = at(a);
  // session 212 (as session 211 on the battery): the contract's two rows only when the scenario holds a contract;
  // session 353: a tax credit's row only when the scenario holds that credit
  const keys = [...FINANCE_KEYS, ...((a.cshare ?? 0) > 0 ? CONTRACT_KEYS : []), ...CREDIT_KEYS.filter((k) => (a[k] ?? 0) > 0)];
  const bars = keys.map((k): Bar => {
    const s = SPECS[k];
    const side = (dir: -1 | 1): Side | null => {
      const v = Math.round((a[k] + dir * s.swing) * 1e6) / 1e6;
      if (v < s.min || v > s.max) return null;
      return { value: v, npv: at({ ...a, [k]: v }) };
    };
    const down = side(-1), up = side(1);
    return { key: k, label: s.label, step: s.swingWords, base, down, up, size: Math.max(down ? Math.abs(down.npv - base) : 0, up ? Math.abs(up.npv - base) : 0) };
  });
  return bars.map((b, i) => ({ b, i })).sort((x, y) => y.b.size - x.b.size || x.i - y.i).map((x) => x.b);
}
