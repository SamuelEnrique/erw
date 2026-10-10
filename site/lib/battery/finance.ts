// Session 179: the finance of "What a battery earns" (/cost-of-power/battery), scenarios A and B. Pure arithmetic, no
// React and no imports: Node runs this file as it is (scripts/test-battery-finance.mjs), and tests/test_session179.py
// holds a Python mirror of every function to 1e-6. Every formula is stated in docs/methods/battery_earns_algorithm.md,
// section 11.1. Everything here is per kW of rated power; the page scales by the reader's size.
//
// Ten assumptions. Eight are arithmetic after the model: capital cost, debt share, interest rate, term, fixed O&M,
// degradation, project life, hurdle rate. Two are inside the model's daily optimization and cannot be recomputed here:
// round-trip efficiency and cycles a day. For those the page offers only the steps the model itself was run at
// (data/battery_scenario_steps.json, warehouse/derived/battery_scenario_steps.py) and interpolates nothing.

export type Key = "capex" | "share" | "rate" | "term" | "fom" | "rte" | "cycles" | "deg" | "life" | "hurdle";
export type Assumptions = Record<Key, number>;
/** The ten, in the order the page lists them. */
export const KEYS: Key[] = ["capex", "share", "rate", "term", "fom", "rte", "cycles", "deg", "life", "hurdle"];

export type Spec = {
  key: Key; letter: string; label: string; unit: string; min: number; max: number; whole: boolean;
  /** the step of the sensitivity chart, in the assumption's own unit, and how the chart states it */
  swing: number; swingWords: string;
  /** how the differing value reads in a column header, and in the last row ("B: <words(b)> against <plain(a)>") */
  short: (v: number) => string; words: (v: number) => string; plain: (v: number) => string;
  /** the source of the default, as the page prints it */
  source: string;
};
const n = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
export const LAZARD = "Lazard, Levelized Cost of Energy+, June 2025";
export const SPECS: Record<Key, Spec> = {
  capex: { key: "capex", letter: "c", label: "Capital cost", unit: "USD per kW", min: 0, max: 10000, whole: false, swing: 100, swingWords: "USD 100 per kW",
    short: (v) => `capex ${n(v)} USD/kW`, words: (v) => `capex USD ${n(v)} per kW`, plain: n, source: `${LAZARD} (LCOS v10.0)` },
  share: { key: "share", letter: "s", label: "Debt share", unit: "percent of capital cost", min: 0, max: 100, whole: false, swing: 10, swingWords: "10 points",
    short: (v) => `debt share ${n(v)}%`, words: (v) => `debt share ${n(v)} percent`, plain: n, source: `${LAZARD}: 60% debt at an 8% interest rate` },
  rate: { key: "rate", letter: "r", label: "Interest rate", unit: "percent a year", min: 0, max: 30, whole: false, swing: 1, swingWords: "1 point",
    short: (v) => `interest ${n(v)}%`, words: (v) => `interest rate ${n(v)} percent`, plain: n, source: `${LAZARD}: 60% debt at an 8% interest rate` },
  term: { key: "term", letter: "t", label: "Term of the debt", unit: "years", min: 1, max: 40, whole: true, swing: 5, swingWords: "5 years",
    short: (v) => `term ${n(v)} years`, words: (v) => `term ${n(v)} years`, plain: n, source: `${LAZARD}: economic life sets the debt amortization schedule, 20 years for storage` },
  fom: { key: "fom", letter: "f", label: "Fixed O&M", unit: "USD per kW a year", min: 0, max: 500, whole: false, swing: 5, swingWords: "USD 5 per kW a year",
    short: (v) => `fixed O&M ${n(v)} USD/kW-yr`, words: (v) => `fixed O&M USD ${n(v)} per kW a year`, plain: n, source: `${LAZARD} (LCOS v10.0)` },
  rte: { key: "rte", letter: "e", label: "Round-trip efficiency", unit: "percent", min: 0, max: 100, whole: false, swing: 3, swingWords: "one step, 3 points",
    short: (v) => `efficiency ${n(v)}%`, words: (v) => `round-trip efficiency ${n(v)} percent`, plain: n, source: `${LAZARD} (LCOS v10.0): 86 to 92 percent for utility-scale storage; the model runs at the low end` },
  cycles: { key: "cycles", letter: "y", label: "Cycles a day, at most", unit: "full cycles", min: 0, max: 10, whole: false, swing: 0.5, swingWords: "one step, 0.5 cycles",
    short: (v) => `${n(v)} ${v === 1 ? "cycle" : "cycles"} a day`, words: (v) => `cycles a day ${n(v)}`, plain: n, source: "The model's rule: at most one full cycle a day. The other steps are the reader's, not a source's" },
  deg: { key: "deg", letter: "d", label: "Degradation", unit: "percent a year", min: 0, max: 20, whole: false, swing: 1, swingWords: "1 point",
    short: (v) => `degradation ${n(v)}% a year`, words: (v) => `degradation ${n(v)} percent a year`, plain: n, source: "The model has no capacity fade. No cited rate is held, so the default is none" },
  life: { key: "life", letter: "l", label: "Project life", unit: "years", min: 1, max: 40, whole: true, swing: 5, swingWords: "5 years",
    short: (v) => `life ${n(v)} years`, words: (v) => `project life ${n(v)} years`, plain: n, source: `${LAZARD}: 20 years for storage` },
  hurdle: { key: "hurdle", letter: "h", label: "Hurdle rate", unit: "percent a year", min: 0, max: 40, whole: false, swing: 1, swingWords: "1 point",
    short: (v) => `hurdle ${n(v)}%`, words: (v) => `hurdle rate ${n(v)} percent`, plain: n, source: "No cited rate is held. The default is set equal to the interest rate" },
};
/** The model's own values of the two assumptions inside it, and the steps offered when no table of steps is held. */
export const MODEL = { rte: 86, cycles: 1 };
export type Steps = { rte: number[]; cycles: number[] };
export const ONLY_DEFAULT: Steps = { rte: [MODEL.rte], cycles: [MODEL.cycles] };

/** The defaults for a duration: its Lazard capital cost and fixed O&M (lib/batterystack.ts, COSTS), and the rest. */
export function defaultsOf(costs: { capex: number; fom: number }): Assumptions {
  return { capex: costs.capex, share: 60, rate: 8, term: 20, fom: costs.fom, rte: MODEL.rte, cycles: MODEL.cycles, deg: 0, life: 20, hurdle: 8 };
}

/** One value brought inside its bounds, or to the default when it cannot be read; the two stepped assumptions take the
 * default unless the value is one of the steps held. */
export function bound(key: Key, v: number, d: Assumptions, steps: Steps): number {
  if (!Number.isFinite(v)) return d[key];
  if (key === "rte" || key === "cycles") return steps[key].includes(v) ? v : d[key];
  const s = SPECS[key];
  const x = Math.min(s.max, Math.max(s.min, v));
  return s.whole ? Math.round(x) : x;
}

export type View = "a" | "b";
export type Scenarios = { a: Assumptions; b: Assumptions; view: View };
/** Both scenarios from the address: <a or b><letter>, each defaulted and bounded; `v=b` puts B in view. */
export function parseScenarios(q: Record<string, string | undefined>, d: Assumptions, steps: Steps): Scenarios {
  const one = (p: View): Assumptions => {
    const out = { ...d };
    for (const k of KEYS) {
      const raw = q[p + SPECS[k].letter];
      if (raw !== undefined && raw !== "") out[k] = bound(k, Number(raw), d, steps);
    }
    return out;
  };
  return { a: one("a"), b: one("b"), view: q.v === "b" ? "b" : "a" };
}
/** The address parameters of both scenarios: only what differs from the defaults, so no parameter means the defaults. */
export function scenarioQuery(s: Scenarios, d: Assumptions): [string, string][] {
  const out: [string, string][] = [];
  for (const p of ["a", "b"] as View[]) for (const k of KEYS) if (s[p][k] !== d[k]) out.push([p + SPECS[k].letter, String(s[p][k])]);
  if (s.view === "b") out.push(["v", "b"]);
  return out;
}
/** Whether a parameter name is one of the scenarios' (so that the page's other links can carry or drop it). */
export const isScenarioParam = (name: string) => name === "v" || /^[ab][csrtfeydlh]$/.test(name);
/** The scenarios' parameters of a query string, to append to another link of the page. A change of duration drops the
 * capital cost and the fixed O&M (their defaults scale with the duration), as the page drops its own typed costs. */
export function carry(search: string, sameDuration: boolean): string {
  const out: string[] = [];
  for (const [k, v] of new URLSearchParams(search)) {
    if (!isScenarioParam(k)) continue;
    if (!sameDuration && /^[ab][cf]$/.test(k)) continue;
    out.push(`${k}=${encodeURIComponent(v)}`);
  }
  return out.length ? `&${out.join("&")}` : "";
}
/** The assumptions that differ between A and B, in the page's order. */
export const differing = (a: Assumptions, b: Assumptions): Key[] => KEYS.filter((k) => a[k] !== b[k]);
/** The last row, in words: "B: capex USD 1,100 per kW against 1,300; hurdle rate 8 percent against 10." */
export function differenceWords(a: Assumptions, b: Assumptions): string {
  const ks = differing(a, b);
  if (!ks.length) return "A and B hold the same assumptions.";
  return `B: ${ks.map((k) => `${SPECS[k].words(b[k])} against ${SPECS[k].plain(a[k])}`).join("; ")}.`;
}

// ---------------------------------------------------------------------------------------------------------------------
// The arithmetic. Rates and shares are in percent, as the reader types them. USD per kW of rated power.

/** The level annual payment per dollar borrowed at `rate` (a fraction) over `years`; at a rate of zero, 1 / years. */
export const crf = (rate: number, years: number) => (rate === 0 ? 1 / years : rate / (1 - (1 + rate) ** -years));
/** The years the debt is repaid over: its term, cut to the project life when the term is longer. */
export const debtYears = (a: Assumptions) => Math.min(a.term, a.life);
/** Annual debt payments, USD per kW: the capital cost times the debt share, level over the debt's years. */
export const debtService = (a: Assumptions) => a.capex * (a.share / 100) * crf(a.rate / 100, debtYears(a));
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
export const TARGET = 1.25;
/** The breakeven toll, USD per kW-month: the price of a toll on the whole battery at which twelve months of it, less
 * fixed O&M, over the debt payments, is `target`. Solving (12 x toll - fom) / debt = target. Null with no debt. */
export function breakevenToll(a: Assumptions, target = TARGET): number | null {
  const ds = debtService(a);
  return ds > 0 ? (target * ds + a.fom) / 12 : null;
}
/** The merchant tail: the years of the project life after the debt's years (the toll is taken to run as long as the
 * debt), and the present value at the hurdle rate, at year 0, of those years' revenue less fixed O&M. */
export function merchantTail(a: Assumptions, revKw: number): { years: number; from: number; to: number; pv: number } {
  const dy = debtYears(a);
  let pv = 0;
  for (let t = dy + 1; t <= a.life; t++) pv += (revenueInYear(a, revKw, t) - a.fom) / (1 + a.hurdle / 100) ** t;
  return { years: Math.max(0, a.life - dy), from: dy + 1, to: a.life, pv };
}

export type Result = { debt: number; coverage: number | null; npv: number; irr: number | null; toll: number | null; tail: ReturnType<typeof merchantTail> };
/** Everything a scenario's column shows that depends on its finance, from the last twelve months' revenue per kW. */
export function resultOf(a: Assumptions, revKw: number): Result {
  const fl = flows(a, revKw);
  return { debt: debtService(a), coverage: coverage(a, revKw), npv: npv(a.hurdle, fl), irr: irr(fl), toll: breakevenToll(a), tail: merchantTail(a, revKw) };
}

export type Side = { value: number; npv: number };
export type Bar = { key: Key; label: string; step: string; base: number; down: Side | null; up: Side | null; size: number };
/** The sensitivity of the net present value: each assumption moved by its stated step down and up, the others held.
 * `revOf` gives the last twelve months' revenue per kW at an efficiency and a cycle limit, or null when that step is
 * not held. A side is null when the moved value leaves the assumption's bounds or its step is not held. Sorted by the
 * larger of the two moves, largest first; ties keep the page's order. */
export function sensitivity(a: Assumptions, revOf: (rte: number, cycles: number) => number | null, steps: Steps): Bar[] {
  const at = (x: Assumptions): number | null => {
    const rev = revOf(x.rte, x.cycles);
    return rev === null ? null : npv(x.hurdle, flows(x, rev));
  };
  const base = at(a);
  if (base === null) return [];
  const bars = KEYS.map((k): Bar => {
    const s = SPECS[k];
    const side = (dir: -1 | 1): Side | null => {
      let v: number;
      if (k === "rte" || k === "cycles") {
        const i = steps[k].indexOf(a[k]) + dir;
        if (steps[k].indexOf(a[k]) < 0 || i < 0 || i >= steps[k].length) return null;
        v = steps[k][i];
      } else {
        v = Math.round((a[k] + dir * s.swing) * 1e6) / 1e6;
        if (v < s.min || v > s.max) return null;
      }
      const y = at({ ...a, [k]: v });
      return y === null ? null : { value: v, npv: y };
    };
    const down = side(-1), up = side(1);
    return { key: k, label: s.label, step: s.swingWords, base, down, up, size: Math.max(down ? Math.abs(down.npv - base) : 0, up ? Math.abs(up.npv - base) : 0) };
  });
  return bars.map((b, i) => ({ b, i })).sort((x, y) => y.b.size - x.b.size || x.i - y.i).map((x) => x.b);
}

// ---------------------------------------------------------------------------------------------------------------------
// The steps of efficiency and of the cycle limit: the model's own runs (data/battery_scenario_steps.json).

export type StepCase = { first: string; last: string; months: string[]; days: number[]; table: number[]; cells: Record<string, number[]> };
export type StepFile = { built: string; rte_steps: number[]; cycle_steps: number[]; tolerance_usd_per_mw: number; cases: Record<string, StepCase> };
export type LiveMonth = { m: string; held: boolean; total: number | null; daysHeld: number };
export const cellKey = (rte: number, cycles: number) => `${rte}|${cycles}`;
export type StepState = { ok: true } | { ok: false; why: "none" | "months" | "revised"; fileLast: string | null; liveLast: string | null };
/** Whether the file of steps still describes the live table over the months the page needs (the held months of its
 * 36-month window): every one is in the file, with the same count of solved days and, in the default cell, the same
 * total to within the tolerance. When not, the page offers the default step alone and says why: it never shows a step
 * computed from months the live table has since moved past or revised. */
export function stepState(c: StepCase | null | undefined, live: LiveMonth[], need: string[], tol = 0.005): StepState {
  const liveLast = need.length ? need[need.length - 1] : null;
  if (!c) return { ok: false, why: "none", fileLast: null, liveLast };
  const at = new Map(c.months.map((m, i) => [m, i]));
  const by = new Map(live.map((r) => [r.m, r]));
  for (const m of need) if (!at.has(m)) return { ok: false, why: "months", fileLast: c.last, liveLast };
  const base = c.cells[cellKey(MODEL.rte, MODEL.cycles)];
  for (const m of need) {
    const i = at.get(m)!, r = by.get(m);
    if (!r || r.total === null || !base || r.daysHeld !== c.days[i] || Math.abs(r.total - base[i]) > tol) return { ok: false, why: "revised", fileLast: c.last, liveLast };
  }
  return { ok: true };
}
/** The steps the controls offer: the file's when it still describes the live table, else the default alone. */
export const stepsOffered = (f: Pick<StepFile, "rte_steps" | "cycle_steps">, s: StepState): Steps => (s.ok ? { rte: f.rte_steps, cycles: f.cycle_steps } : ONLY_DEFAULT);
/** A cell's monthly totals, USD per MW, by month; null when the cell is not held. */
export function cellTotals(c: StepCase | null | undefined, rte: number, cycles: number): Map<string, number> | null {
  const v = c?.cells[cellKey(rte, cycles)];
  return c && v ? new Map(c.months.map((m, i) => [m, v[i]])) : null;
}
