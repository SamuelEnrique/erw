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

export type Key = "capex" | "share" | "rate" | "term" | "fom" | "deg" | "life" | "hurdle";
export type Assumptions = Record<Key, number>;
/** The eight, in the order the page lists them. */
export const KEYS: Key[] = ["capex", "share", "rate", "term", "fom", "deg", "life", "hurdle"];

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
    short: (v) => `hurdle ${n(v)}%`, words: (v) => `hurdle rate ${n(v)} percent`, plain: n, source: "No cited rate is held. The default is set equal to the interest rate" },
};

/** The defaults for an asset: its Lazard capital cost, fixed O&M and life (lib/merchant.ts, DEFAULTS), Lazard's
 * financing (60 percent debt at 8 percent, repaid over the life), and the two that no source in the repository gives. */
export function defaultsOf(costs: { capex: number; fom: number; life: number }): Assumptions {
  return { capex: costs.capex, share: 60, rate: 8, term: costs.life, fom: costs.fom, deg: 0, life: costs.life, hurdle: 8 };
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
export const isScenarioParam = (name: string) => name === "v" || /^[ab][csrtfdlh]$/.test(name);
/** The scenarios' parameters of a query string, to append to another address of the page. A change of asset (or of a
 * battery's duration) drops the capital cost, the fixed O&M, the term and the life, whose defaults are the asset's. */
export function carry(search: string, sameAsset: boolean): string {
  const out: string[] = [];
  for (const [k, v] of new URLSearchParams(search)) {
    if (!isScenarioParam(k)) continue;
    if (!sameAsset && /^[ab][cftl]$/.test(k)) continue;
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
/** Annual debt payments, USD per kW: the capital cost times the debt share, level over the debt's years. */
export const debtService = (a: Assumptions) => a.capex * (a.share / 100) * crf(a.rate / 100, debtYears(a));
/** Annual debt payments in whole USD for `mw` megawatts: what the page's coverage divides by, and what its check keys
 * carry. The order of the multiplication is the page's own (lib/merchant.ts, debtPerMw, times the megawatts), so the
 * defaults give the figure the page showed before session 195 to the last dollar. */
export const debtUsd = (a: Assumptions, mw: number) => Math.round(a.capex * 1000 * (a.share / 100) * crf(a.rate / 100, debtYears(a)) * mw);
/** Revenue in year t (1 is the first), USD per kW: the last twelve months' revenue, falling by the degradation rate
 * each year after the first. */
export const revenueInYear = (a: Assumptions, revKw: number, t: number) => revKw * (1 - a.deg / 100) ** (t - 1);
/** The cash flows to equity, USD per kW, years 0 to the project life: the equity paid in at year 0, then each year's
 * revenue less fixed O&M less the debt payment while the debt lasts. */
export function flows(a: Assumptions, revKw: number): number[] {
  const ds = debtService(a), dy = debtYears(a);
  const out = [-a.capex * (1 - a.share / 100)];
  for (let t = 1; t <= a.life; t++) out.push(revenueInYear(a, revKw, t) - a.fom - (t <= dy ? ds : 0));
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
/** Debt coverage on a year's revenue: revenue less fixed O&M, over the debt payments. Null with no debt. */
export function coverage(a: Assumptions, revKw: number): number | null {
  const ds = debtService(a);
  return ds > 0 ? (revKw - a.fom) / ds : null;
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

export type Result = { debt: number; coverage: number | null; npv: number; irr: number | null };
/** Everything a scenario's column shows that depends on its finance and on revenue, from the last twelve months'
 * revenue per kW. */
export function resultOf(a: Assumptions, revKw: number): Result {
  const fl = flows(a, revKw);
  return { debt: debtService(a), coverage: coverage(a, revKw), npv: npv(a.hurdle, fl), irr: irr(fl) };
}

export type Side = { value: number; npv: number };
export type Bar = { key: Key; label: string; step: string; base: number; down: Side | null; up: Side | null; size: number };
/** The sensitivity of the net present value: each assumption moved by its stated step down and up, the others held. A
 * side is null when the moved value leaves the assumption's bounds. Sorted by the larger of the two moves, largest
 * first; ties keep the page's order. */
export function sensitivity(a: Assumptions, revKw: number): Bar[] {
  const at = (x: Assumptions) => npv(x.hurdle, flows(x, revKw));
  const base = at(a);
  const bars = KEYS.map((k): Bar => {
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
