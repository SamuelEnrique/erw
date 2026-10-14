// Session 194: the decisions of "What a datacenter pays" (/cost-of-power), scenarios A and B, as session 179 built
// them for the battery (lib/battery/finance.ts) and session 186 for the generator (lib/seller/finance.ts). Pure
// arithmetic, no React and no imports: Node runs this file as it is (scripts/test-datacenter-finance.mjs), and
// tests/test_session194.py holds a Python mirror of every function to 1e-6. Every formula is stated in
// docs/methods/datacenter_pays_algorithm.md, section 4.14. Everything here is per MW of the load's size; the page
// scales by the reader's megawatts.
//
// A buyer has a cost where a seller has a revenue, so the frame is turned over: the present value of the cost in place
// of the net present value, the fixed price with the same present value in place of the breakeven toll, and, between
// the two scenarios, the upfront cost at which they come to the same and the rate the dearer one's extra cost returns.
//
// Eight assumptions. One is inside the model: how the load runs, flat or flexible. The page computes both ways on the
// server from its own price files and hands them over (`Way`); nothing here models an hour. The other seven are
// arithmetic after the model: power per GPU, the overhead ratio, delivery and other charges, the yearly change of
// prices, the upfront cost, the years counted and the hurdle rate.
//
// Session 213 (the owner's chain prompt of 12 October 2026, the battery page's layout): the contract is two more
// scenario assumptions, its share of the energy and its price per MWh, both 0 by default, so the default is fully
// merchant and every figure at a share of 0 is what it was. The contracted share of the energy is bought at the
// contract price in every year counted and pays nothing to the market; the rest pays the market, changing by the
// yearly rate. The standalone contract panel of session 138 is gone (LoadContract.tsx stays on disk, undrawn).

export type Key = "run" | "gpu" | "pue" | "adder" | "growth" | "upfront" | "life" | "hurdle" | "cshare" | "cprice";
export type Assumptions = Record<Key, number>;
/** The ten, in the order the page lists them (session 213: the contract's share and price last). */
export const KEYS: Key[] = ["run", "gpu", "pue", "adder", "growth", "upfront", "life", "hurdle", "cshare", "cprice"];
/** The eight of session 194. */
export const FINANCE_KEYS: Key[] = ["run", "gpu", "pue", "adder", "growth", "upfront", "life", "hurdle"];
/** The two ways a load runs: the values of the assumption `run`. */
export const FLAT = 0, FLEX = 1;

/** One way of running over the page's last twelve months, per MW of size, as lib/datacenter.ts computes it: the price
 * per MWh consumed, the cost in USD, the energy in MWh, the hours held, what a flat MW paid over the same hours, the
 * hours off; and the bad month of the 36 (its price per MWh, its cost per MW, how many months were ranked). */
export type Way = { per: number; cost: number; energy: number; held: number; flatCost: number; down: number; bad: { m: string; per: number; cost: number } | null; of: number };
/** Both ways, indexed by `run`. A way that is not held (no twelve months, or no day-ahead price to decide from) is null. */
export type Ways = [Way | null, Way | null];

export type Spec = {
  key: Key; letter: string; label: string; unit: string; min: number; max: number; whole: boolean;
  /** the step of the sensitivity chart, in the assumption's own unit, and how the chart states it */
  swing: number; swingWords: string;
  /** how the differing value reads in a column header, and in the last row ("B: <words(b)> against <plain(a)>") */
  short: (v: number) => string; words: (v: number) => string; plain: (v: number) => string;
  /** the source of the default, as the page prints it (the page supplies the two cited ones and the way of running) */
  source: string;
};
const n = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
const way = (v: number) => (v === FLEX ? "flexible" : "flat");
export const LAZARD = "Lazard, Levelized Cost of Energy+, June 2025";
export const SPECS: Record<Key, Spec> = {
  run: { key: "run", letter: "w", label: "How the load runs", unit: "flat or flexible", min: FLAT, max: FLEX, whole: true, swing: 1, swingWords: "the other way",
    short: (v) => `runs ${way(v)}`, words: (v) => `runs ${way(v)}`, plain: way, source: "As described under \"Your load\"" },
  gpu: { key: "gpu", letter: "g", label: "Power per GPU", unit: "kW", min: 0.05, max: 20, whole: false, swing: 0.1, swingWords: "0.1 kW",
    short: (v) => `${n(v)} kW per GPU`, words: (v) => `${n(v)} kW per GPU`, plain: n, source: "" },
  pue: { key: "pue", letter: "p", label: "Facility overhead ratio (PUE)", unit: "facility power over IT power", min: 1, max: 3, whole: false, swing: 0.1, swingWords: "0.1",
    short: (v) => `overhead ratio ${n(v)}`, words: (v) => `overhead ratio ${n(v)}`, plain: n, source: "" },
  adder: { key: "adder", letter: "d", label: "Delivery and other charges", unit: "USD per MWh", min: 0, max: 500, whole: false, swing: 5, swingWords: "USD 5 per MWh",
    short: (v) => `other charges ${n(v)} USD/MWh`, words: (v) => `other charges USD ${n(v)} per MWh`, plain: n,
    source: "The page's figure is market energy alone. No delivery, transmission or other charge is added, so the default is none" },
  growth: { key: "growth", letter: "e", label: "Change of prices", unit: "percent a year", min: -20, max: 20, whole: false, swing: 1, swingWords: "1 point",
    short: (v) => `prices ${n(v)}% a year`, words: (v) => `prices changing ${n(v)} percent a year`, plain: n,
    source: "The last twelve months are repeated every year. No cited forecast is held, so the default is no change" },
  upfront: { key: "upfront", letter: "u", label: "Upfront cost", unit: "USD per kW of the load's size", min: 0, max: 20000, whole: false, swing: 100, swingWords: "USD 100 per kW",
    short: (v) => `upfront ${n(v)} USD/kW`, words: (v) => `upfront cost USD ${n(v)} per kW`, plain: n,
    source: "What this way of running, or this overhead ratio, costs to build. No cited cost is held, so the default is none" },
  life: { key: "life", letter: "l", label: "Years counted", unit: "years", min: 1, max: 40, whole: true, swing: 5, swingWords: "5 years",
    short: (v) => `${n(v)} years`, words: (v) => `${n(v)} years counted`, plain: n, source: "No cited term is held for a datacenter's power. The default is 20 years" },
  // session 265 (the owner's list of 14 October 2026): the field is labelled for what its default is, a generator's
  // weighted cost of capital as Lazard states it; the field stays editable, and the sentences still call it the hurdle rate
  hurdle: { key: "hurdle", letter: "h", label: "Cost of capital: a generator's WACC, Lazard", unit: "percent a year", min: 0, max: 40, whole: false, swing: 1, swingWords: "1 point",
    short: (v) => `hurdle ${n(v)}%`, words: (v) => `hurdle rate ${n(v)} percent`, plain: n,
    source: `${LAZARD}: "60% debt at an 8% interest rate and 40% equity at a 12% cost". The default is that weighted cost, 0.6 x 8 + 0.4 x 12 = 9.6 percent. It is the cost of capital of a power plant's builder, not a datacenter's own, for which no cited rate is held` },
  // session 213: the contract
  cshare: { key: "cshare", letter: "n", label: "Contract share", unit: "percent of the energy", min: 0, max: 100, whole: false, swing: 10, swingWords: "10 points",
    short: (v) => `contract ${n(v)}%`, words: (v) => `contract share ${n(v)} percent`, plain: n,
    source: "No contract: the default is fully merchant. A contracted share of the energy is bought at the contract price in every year counted and pays nothing to the market" },
  cprice: { key: "cprice", letter: "c", label: "Contract price", unit: "USD per MWh", min: 0, max: 1000, whole: false, swing: 1, swingWords: "USD 1 per MWh",
    short: (v) => `contract USD ${n(v)}/MWh`, words: (v) => `contract price USD ${n(v)} per MWh`, plain: n,
    source: "No contract: the default is fully merchant. The price is the reader's own term; no published price is held" },
};
/** Session 196, the owner's ruling of 11 October 2026: the hurdle rate's default is Lazard's weighted cost of capital,
 * "60% debt at an 8% interest rate and 40% equity at a 12% cost" (its June 2025 report, read 11 October 2026):
 * 0.6 x 8 + 0.4 x 12 = 9.6. Until then it was 8, set equal to the interest rate. */
export const LIFE = 20, HURDLE = 9.6;

/** The defaults: the way of running as "Your load" has it, the power per GPU and the overhead ratio as the page cites
 * them (session 195: "Your load" no longer holds those two; scenario A does, and sets the headline), and the five the
 * page does not otherwise hold. */
export function defaultsOf(load: { run: number; gpu: number; pue: number }): Assumptions {
  return { run: load.run === FLEX ? FLEX : FLAT, gpu: load.gpu, pue: load.pue, adder: 0, growth: 0, upfront: 0, life: LIFE, hurdle: HURDLE, cshare: 0, cprice: 0 };
}

/** One value brought inside its bounds, or to the default when it cannot be read. */
export function bound(key: Key, v: number, d: Assumptions): number {
  if (!Number.isFinite(v)) return d[key];
  const s = SPECS[key];
  const x = Math.min(s.max, Math.max(s.min, v));
  return s.whole ? Math.round(x) : x;
}
/** Which ways are held: a scenario cannot be set to one that is not. */
export const held = (ways: Ways): [boolean, boolean] => [ways[FLAT] !== null, ways[FLEX] !== null];

export type View = "a" | "b";
export type Scenarios = { a: Assumptions; b: Assumptions; view: View };
/** The two names "Your load" held until session 195, and the assumption each is an old name of. Before that session
 * they were the default of both scenarios, so an older link's `gpu` or `pue` is read as A's and as B's, unless the
 * scenario's own parameter is there; they are then dropped from the address. */
export const OLD: Record<string, Key> = { gpu: "gpu", pue: "pue" };
export const isOldParam = (name: string) => name in OLD;
/** Both scenarios from the address: <a or b><letter>, each defaulted and bounded; `v=b` puts B in view. A way of
 * running that is not held (`open`) falls back to the default. */
export function parseScenarios(q: Record<string, string | undefined>, d: Assumptions, open: [boolean, boolean] = [true, true]): Scenarios {
  const one = (p: View): Assumptions => {
    const out = { ...d };
    for (const [name, k] of Object.entries(OLD)) {
      const raw = q[name];
      if (raw !== undefined && raw !== "") out[k] = bound(k, Number(raw), d);
    }
    for (const k of KEYS) {
      const raw = q[p + SPECS[k].letter];
      if (raw !== undefined && raw !== "") out[k] = bound(k, Number(raw), d);
    }
    if (!open[out.run]) out.run = d.run;
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
/** Whether a parameter name is one of the scenarios' (so that the page's other links can carry or drop it). None of
 * the page's own is two letters long or the one letter `v`: view, grid, region, mw, run, n, pct, shift, buy, gpu, pue. */
export const isScenarioParam = (name: string) => name === "v" || /^[ab][wgpdeulhnc]$/.test(name);
/** Session 236: scenario B's own site, `bsite=<grid>:<region>` (absent: B is at the site "Your load" names). It is read
 * by the server, which computes B's two ways of running from that site's prices (app/cost-of-power/model.ts), so it is
 * not one of the assumptions the browser rewrites (isScenarioParam is false for it) and it is carried like them. */
export const SITE_B = "bsite";
/** The scenarios' parameters of a query string, to append to another address of the page. */
export function carry(search: string): string {
  const out: string[] = [];
  for (const [k, v] of new URLSearchParams(search)) if (isScenarioParam(k) || k === SITE_B) out.push(`${k}=${encodeURIComponent(v)}`);
  return out.length ? `&${out.join("&")}` : "";
}
/** The assumptions that differ between A and B, in the page's order. */
export const differing = (a: Assumptions, b: Assumptions): Key[] => KEYS.filter((k) => a[k] !== b[k]);
/** The row "What differs", in words: "B: runs flexible against flat; hurdle rate 10 percent against 8." */
export function differenceWords(a: Assumptions, b: Assumptions): string {
  const ks = differing(a, b);
  if (!ks.length) return "A and B hold the same assumptions.";
  return `B: ${ks.map((k) => `${SPECS[k].words(b[k])} against ${SPECS[k].plain(a[k])}`).join("; ")}.`;
}

// ---------------------------------------------------------------------------------------------------------------------
// The arithmetic. Rates are in percent, as the reader types them. USD per MW of the load's size.

/** The way a scenario runs, or null when that way is not held. */
export const wayOf = (a: Assumptions, ways: Ways): Way | null => ways[a.run === FLEX ? FLEX : FLAT];
/** Session 213: the contracted share of the energy, a fraction (0 without the key: an older set of assumptions is read
 * as fully merchant), and the uncontracted rest. */
export const contractShare = (a: Assumptions) => (a.cshare ?? 0) / 100;
export const merchantShare = (a: Assumptions) => 1 - contractShare(a);
/** The contract's cost a year, USD per MW: the contracted share of the energy at the contract price. 0 with no contract. */
export const contractYear = (a: Assumptions, w: Way) => contractShare(a) * w.energy * (a.cprice ?? 0);
/** The market's cost a year, USD per MW, on the uncontracted rest of the energy: the whole of it with no contract. */
export const marketYear = (a: Assumptions, w: Way) => merchantShare(a) * w.cost;
/** USD per MWh consumed: the market energy of the last twelve months (the contracted share at its price, session 213),
 * and the other charges typed. */
export const price = (a: Assumptions, w: Way) => (marketYear(a, w) + contractYear(a, w)) / w.energy + a.adder;
/** A year's cost, USD per MW: the last twelve months' market energy (the contracted share at its price), and the other
 * charges on every MWh consumed. */
export const bill = (a: Assumptions, w: Way) => marketYear(a, w) + contractYear(a, w) + a.adder * w.energy;
/** USD per GPU-hour for power: the price, times the GPU's power with its share of the facility's overhead. */
export const gpuHour = (a: Assumptions, w: Way) => (price(a, w) * a.gpu * a.pue) / 1000;
/** The GPUs one MW powers. */
export const gpusPerMw = (a: Assumptions) => 1000 / (a.gpu * a.pue);
/** GPU-hours run in a year, per MW: the energy in MWh per MW is the hours at full load, times the GPUs a MW powers. */
export const gpuHoursYear = (a: Assumptions, w: Way) => w.energy * gpusPerMw(a);

export type Off = { hours: number; mwh: number; perMwh: number; perGpuHour: number };
/** The hours a load is off, and what they save: the cost a flat load paid in those hours over the energy not bought
 * (with the other charges, which are not paid either), USD per MWh, and the same per GPU-hour not run. A GPU-hour that
 * earns more than that costs more to turn off than the power it saves; one that earns less, less: the breakeven. Null
 * for a load that is never off (flat, or shifting within the day). */
export function offOf(a: Assumptions, w: Way): Off | null {
  const mwh = w.held - w.energy;
  if (w.down <= 0 || mwh <= 1e-9) return null;
  const perMwh = (w.flatCost - w.cost) / mwh + a.adder;
  return { hours: w.down, mwh, perMwh, perGpuHour: (perMwh * a.gpu * a.pue) / 1000 };
}

/** The cost of year t (1 is the first), USD per MW: the market's cost and the other charges changing by the rate each
 * year after the first (as before session 213); the contract's cost the same every year, its price being fixed. With
 * no contract this is the year's cost changing by the rate, to the bit. */
export const costInYear = (a: Assumptions, w: Way, t: number) => (marketYear(a, w) + a.adder * w.energy) * (1 + a.growth / 100) ** (t - 1) + contractYear(a, w);
/** The costs, USD per MW, years 0 to the years counted: the upfront cost at year 0 (USD per kW, so times 1,000), then
 * each year's cost. All positive: a cost, not a flow to equity. */
export function flows(a: Assumptions, w: Way): number[] {
  const out = [a.upfront * 1000];
  for (let t = 1; t <= a.life; t++) out.push(costInYear(a, w, t));
  return out;
}
/** The present value of yearly amounts at `ratePct` percent: the sum of amount t over (1 + rate)^t. */
export function npv(ratePct: number, fl: number[]): number {
  const r = ratePct / 100;
  let s = 0;
  for (let t = 0; t < fl.length; t++) s += fl[t] / (1 + r) ** t;
  return s;
}
/** The present value of 1 a year for `years` years at `ratePct` percent. */
export function annuity(ratePct: number, years: number): number {
  const r = ratePct / 100;
  let s = 0;
  for (let t = 1; t <= years; t++) s += 1 / (1 + r) ** t;
  return s;
}
/** The present value of the cost at the hurdle rate, USD per MW: the upfront cost and every year's cost. */
export const presentValue = (a: Assumptions, w: Way) => npv(a.hurdle, flows(a, w));
/** The fixed price for the whole of the energy, USD per MWh, held for every year counted, whose present value is the
 * market's: the breakeven of a contract against the market as the scenario sees it. Market energy only: the other
 * charges and the upfront cost are paid either way. With no change of prices it is the last twelve months' price. */
export function levelPrice(a: Assumptions, w: Way): number {
  const r = a.hurdle / 100, g = a.growth / 100;
  let s = 0;
  for (let t = 1; t <= a.life; t++) s += (1 + g) ** (t - 1) / (1 + r) ** t;
  return ((w.cost / w.energy) * s) / annuity(a.hurdle, a.life);
}
/** All-in power per GPU-hour over the years counted, USD: the present value of the cost over the present value of the
 * GPU-hours run, both at the hurdle rate. At the defaults it is the page's power per GPU-hour. */
export const levelGpuHour = (a: Assumptions, w: Way) => presentValue(a, w) / (gpuHoursYear(a, w) * annuity(a.hurdle, a.life));

export const IRR_LOW = -99, IRR_HIGH = 1000;   // the bracket, percent a year
/** The internal rate of return, percent a year, by bisection between -99 and 1,000 percent (lib/seller/finance.ts,
 * the same code). Null when the present value has the same sign at both ends of the bracket. */
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

export type Result = { price: number; bill: number; gpuHour: number; gpus: number; gpuHours: number; off: Off | null; pv: number; level: number; allIn: number };
/** Everything a scenario's column shows, per MW, from the way it runs. */
export function resultOf(a: Assumptions, w: Way): Result {
  return { price: price(a, w), bill: bill(a, w), gpuHour: gpuHour(a, w), gpus: gpusPerMw(a), gpuHours: gpuHoursYear(a, w), off: offOf(a, w), pv: presentValue(a, w), level: levelPrice(a, w), allIn: levelGpuHour(a, w) };
}

export type Against = {
  /** B less A: the first year's cost, the GPU-hours run in a year and the present value, per MW */
  bill: number; gpuHours: number; pv: number;
  /** the upfront cost of B, USD per kW, at which the two present values are equal (negative: none does) */
  evenUpfront: number;
  /** the scenario with the larger upfront cost, how much larger (USD per kW), and the rate at which that extra cost
   * equals the yearly costs it avoids; null when the two count different years or no rate in the bracket does */
  more: View | null; extra: number; rate: number | null; sameYears: boolean;
};
/** B set against A. */
export function against(a: Assumptions, wa: Way, b: Assumptions, wb: Way): Against {
  const pa = presentValue(a, wa), pb = presentValue(b, wb);
  const more: View | null = b.upfront > a.upfront ? "b" : a.upfront > b.upfront ? "a" : null;
  const sameYears = a.life === b.life;
  let rate: number | null = null;
  if (more && sameYears) {
    const hi = more === "b" ? b : a, wh = more === "b" ? wb : wa, lo = more === "b" ? a : b, wl = more === "b" ? wa : wb;
    const fl = [-(hi.upfront - lo.upfront) * 1000];
    for (let t = 1; t <= hi.life; t++) fl.push(costInYear(lo, wl, t) - costInYear(hi, wh, t));
    rate = irr(fl);
  }
  return { bill: bill(b, wb) - bill(a, wa), gpuHours: gpuHoursYear(b, wb) - gpuHoursYear(a, wa), pv: pb - pa, evenUpfront: (pa - (pb - b.upfront * 1000)) / 1000,
    more, extra: Math.abs(b.upfront - a.upfront), rate, sameYears };
}

export type Side = { value: number; v: number };
export type Bar = { key: Key; label: string; step: string; base: number; down: Side | null; up: Side | null; size: number };
/** The sensitivity of the all-in power per GPU-hour: each assumption moved by its stated step down and up, the others
 * held. The way of running has one step, the other way, when that way is held. A side is null when the moved value
 * leaves the assumption's bounds. Sorted by the larger of the two moves, largest first; ties keep the page's order.
 * Empty when the scenario's own way is not held. */
export function sensitivity(a: Assumptions, ways: Ways): Bar[] {
  const at = (x: Assumptions) => { const w = wayOf(x, ways); return w ? levelGpuHour(x, w) : null; };
  const base = at(a);
  if (base === null) return [];
  // session 213 (as session 211 on the battery): the contract's two rows only when the scenario holds a contract
  const keys = contractShare(a) > 0 ? KEYS : FINANCE_KEYS;
  const bars = keys.map((k): Bar => {
    const s = SPECS[k];
    const side = (dir: -1 | 1): Side | null => {
      const v = Math.round((a[k] + dir * s.swing) * 1e6) / 1e6;
      if (v < s.min || v > s.max) return null;
      const got = at({ ...a, [k]: v });
      return got === null ? null : { value: v, v: got };
    };
    const down = side(-1), up = side(1);
    // a move smaller than one part in a million million of the figure is the arithmetic's own noise: no move (at the
    // defaults the years counted and the hurdle rate do not move the figure at all)
    const size = Math.max(down ? Math.abs(down.v - base) : 0, up ? Math.abs(up.v - base) : 0);
    return { key: k, label: s.label, step: s.swingWords, base, down, up, size: size < 1e-12 * Math.abs(base) ? 0 : size };
  });
  return bars.map((b, i) => ({ b, i })).sort((x, y) => y.b.size - x.b.size || x.i - y.i).map((x) => x.b);
}
