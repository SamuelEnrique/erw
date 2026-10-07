// Energy Research Warehouse (ERW) site, session 138: "What a datacenter pays" (/cost-of-power, in review).
//
// The arithmetic of the page, over the site's own files of hourly hub and zone prices (data/datacenter, written by
// warehouse/derived/datacenter_page.py; docs/methods/datacenter_cost.md). Pure functions, no imports: Node runs this
// file as it is (site/scripts/test-datacenter.mjs, tests/test_session138.py), and the contract panel runs it in the
// browser. Hours are counted in the grid's standard time, so every day has 24. An hour not held is null and is never
// filled: it is left out of every sum, and a month is counted only when at least NEAR of its hours are held.

export type Series = { s: number; v: (number | null)[] };
export type YearFile = {
  grid: string; year: number; hours: number; built: string; regions: Record<string, { rt?: Series; da?: Series }>;
  peak_mw?: number; peak_hour?: number; tight?: number[]; demand_mean_mw?: number;
  clean?: Series;  // session 140: the carbon-free share of the grid's generation by hour, percent (clean_energy_hourly)
};
export type Side = { hours: number; first: string; last: string; basis: string; tables: string[] };
/** `kind`, `ref` and `name` (session 140): a load zone is where a load settles; `ref` is the trading hub shown beside it. */
export type Region = { id: string; entity: string; rt?: Side; da?: Side; kind?: "zone" | "hub"; ref?: string; name?: string };
export type DemandYear = { hours_held: number; hours_due: number; peak_mw?: number; peak_hour?: number; tight_hours?: number; mean_mw?: number; whole?: boolean };
export type ZoneYear = { mean_mw: number; peak_mw: number; hours_held: number; hours_due: number };
export type GridIndex = {
  name: string; std_hours_behind_utc: number; std_name: string; main: string; years: number[]; regions: Region[];
  demand_source: string | null; demand: Record<string, DemandYear>; zones?: Record<string, Record<string, ZoneYear>>; zone_source?: string | null;
};
export type Index = {
  built: string; method: string; first: string; tight: number; tables: string[];
  grids: Record<string, GridIndex>; blank: Record<string, { name: string; words: string; regions: string[] }>;
};

export const NEAR = 0.95;
export const ORDER = ["ercot", "caiso", "nyiso", "isone", "spp", "miso", "pjm"] as const;
export const RUNS = {
  flat: "Flat: the same in every hour",
  hours: "Flexible: off in the most expensive hours of each year",
  share: "Flexible: off in a share of hours",
  shift: "Shifting: part of each day's energy moved to its cheapest hours",
} as const;
export type Run = keyof typeof RUNS;
export const BUYS = { rt: "Real time", da: "Day-ahead" } as const;
export type Buy = keyof typeof BUYS;
export type View = "load" | "grids";
export type Inputs = { view: View; grid: string; region: string; mw: number; run: Run; n: number; pct: number; shift: number; buy: Buy; gpu: number; pue: number };

/** The two stated defaults a reader can change, each with its source (shown on hover). */
export const ASSUMED = {
  gpu: { value: 1.3, unit: "kW per GPU", source: "NVIDIA DGX H100 system: 8 H100 GPUs and a maximum system power of 10.2 kW, so about 1.3 kW per GPU with its share of the server (NVIDIA DGX H100 datasheet). A GPU alone is rated up to 700 W." },
  pue: { value: 1.56, unit: "facility power over IT power", source: "Uptime Institute, Global Data Center Survey 2024: the industry's average power usage effectiveness, 1.56. Large operators report lower: Google reports 1.09 for its fleet over twelve months." },
} as const;
export const DEFAULTS = { mw: 100, n: 100, pct: 5, shift: 20, gpu: ASSUMED.gpu.value, pue: ASSUMED.pue.value };
export const LIMITS = { mw: [0.1, 10000], n: [0, 8784], pct: [0, 100], shift: [0, 50], gpu: [0.05, 20], pue: [1, 3] } as const;

const clamp = (v: number, [lo, hi]: readonly [number, number]) => Math.min(hi, Math.max(lo, v));
const numOf = (s: string | undefined, d: number, lim: readonly [number, number]) => {
  const v = s === undefined || s === "" ? NaN : Number(s);
  return Number.isFinite(v) ? clamp(v, lim) : d;
};

/** The page's inputs from its address. A grid or region it does not hold is the first one held; a number it cannot read is the default. */
export function inputsOf(q: Record<string, string | undefined>, index: Index): Inputs {
  const grids = ORDER.filter((g) => index.grids[g]);
  const grid = grids.includes(q.grid as (typeof ORDER)[number]) ? (q.grid as string) : grids[0] ?? "ercot";
  const g = index.grids[grid];
  const region = g?.regions.find((r) => r.id === q.region)?.id ?? g?.regions.find((r) => r.id === g.main)?.id ?? g?.regions[0]?.id ?? "";
  const run = (Object.keys(RUNS) as Run[]).includes(q.run as Run) ? (q.run as Run) : "flat";
  const buy: Buy = q.buy === "da" ? "da" : "rt";
  return {
    view: q.view === "grids" ? "grids" : "load", grid, region, run, buy,
    mw: numOf(q.mw, DEFAULTS.mw, LIMITS.mw), n: Math.round(numOf(q.n, DEFAULTS.n, LIMITS.n)), pct: numOf(q.pct, DEFAULTS.pct, LIMITS.pct),
    shift: numOf(q.shift, DEFAULTS.shift, LIMITS.shift), gpu: numOf(q.gpu, DEFAULTS.gpu, LIMITS.gpu), pue: numOf(q.pue, DEFAULTS.pue, LIMITS.pue),
  };
}
export function hrefOf(x: Inputs, change: Partial<Inputs> = {}): string {
  const y = { ...x, ...change };
  const q = new URLSearchParams();
  if (y.view === "grids") return "/cost-of-power?view=grids";
  q.set("grid", y.grid);
  if (y.region) q.set("region", y.region);
  q.set("mw", String(y.mw)); q.set("run", y.run);
  if (y.run === "hours") q.set("n", String(y.n));
  if (y.run === "share") q.set("pct", String(y.pct));
  if (y.run === "shift") q.set("shift", String(y.shift));
  q.set("buy", y.buy);
  if (y.gpu !== DEFAULTS.gpu) q.set("gpu", String(y.gpu));
  if (y.pue !== DEFAULTS.pue) q.set("pue", String(y.pue));
  return `/cost-of-power?${q.toString()}`;
}

// ---------------------------------------------------------------------------------------------------------------------
// hours
// ---------------------------------------------------------------------------------------------------------------------

const leap = (y: number) => (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;
export const hoursIn = (y: number) => (leap(y) ? 8784 : 8760);
const DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
/** The first hour of each month of a year, and the year's end: thirteen indexes. */
export function monthStarts(y: number): number[] {
  const out = [0];
  for (let m = 0; m < 12; m++) out.push(out[m] + 24 * (DAYS[m] + (m === 1 && leap(y) ? 1 : 0)));
  return out;
}
/** A year's prices at one region and market, one entry an hour of the year, null where not held. */
export function expand(f: YearFile, region: string, buy: Buy): (number | null)[] {
  const out: (number | null)[] = Array(f.hours).fill(null);
  const s = f.regions[region]?.[buy];
  if (s) for (let i = 0; i < s.v.length; i++) out[s.s + i] = s.v[i];
  return out;
}

/** The mean of the prices held: what a flat load pays per MWh. */
export function flatMean(p: (number | null)[]): { mean: number | null; hours: number } {
  let sum = 0, n = 0;
  for (const v of p) if (v !== null) { sum += v; n++; }
  return { mean: n ? sum / n : null, hours: n };
}

/** The load in each hour of a year as a multiple of its size: 1 in an ordinary hour, 0 in an hour it is turned down,
 * between 0 and 2 where a day's energy is shifted; 0 where the price is not held (the hour is left out).
 *   hours  off in the n most expensive hours held of the year (n is for a whole year: a year held in part takes the
 *          same share of its hours, rounded);
 *   share  off in the most expensive pct percent of the hours held;
 *   shift  each whole day, shift percent of the day's energy leaves its most expensive hours and is added to its
 *          cheapest (24 x shift / 100 hours of each, the last one in part), so the day's energy is unchanged. A day
 *          with an hour missing is not shifted.
 * The hours are chosen knowing the year's prices: the most a load could have saved, not a forecast. */
export function weights(p: (number | null)[], x: Pick<Inputs, "run" | "n" | "pct" | "shift">): number[] {
  const w = p.map((v) => (v === null ? 0 : 1));
  if (x.run === "flat") return w;
  if (x.run === "hours" || x.run === "share") {
    const held: number[] = [];
    for (let i = 0; i < p.length; i++) if (p[i] !== null) held.push(i);
    const k = Math.min(held.length, Math.round(x.run === "hours" ? (x.n * held.length) / p.length : (x.pct / 100) * held.length));
    held.sort((a, b) => (p[b] as number) - (p[a] as number) || a - b);
    for (let j = 0; j < k; j++) w[held[j]] = 0;
    return w;
  }
  const h = (24 * Math.min(50, Math.max(0, x.shift))) / 100, whole = Math.floor(h), part = h - whole;
  for (let d = 0; d + 24 <= p.length; d += 24) {
    const idx: number[] = [];
    for (let i = d; i < d + 24; i++) if (p[i] !== null) idx.push(i);
    if (idx.length < 24) continue;
    idx.sort((a, b) => (p[b] as number) - (p[a] as number) || a - b);  // dearest first
    for (let j = 0; j < whole; j++) { w[idx[j]] -= 1; w[idx[23 - j]] += 1; }
    if (part > 0) { w[idx[whole]] -= part; w[idx[23 - whole]] += part; }
  }
  return w;
}

// ---------------------------------------------------------------------------------------------------------------------
// months, years, spans. Every figure is per MW of load; the page multiplies by the reader's size.
// ---------------------------------------------------------------------------------------------------------------------

export type Month = {
  m: string; due: number; held: number; complete: boolean;
  flat: number;     // the sum of the prices held: what a flat MW paid, USD
  cost: number;     // what a MW of this load paid, USD
  energy: number;   // what it consumed, MWh
  down: number;     // hours it was turned down
  tight: number;    // the grid's tight hours in the month (0 when not held)
  tightDown: number;  // those of them in which this load was turned down
};
/** A year's months for a load. `tight` is the year's tight hours (indexes), when held. */
export function monthsOfYear(y: number, p: (number | null)[], w: number[], tight?: number[]): Month[] {
  const st = monthStarts(y), isTight = new Set(tight ?? []);
  const out: Month[] = [];
  for (let m = 0; m < 12; m++) {
    const r: Month = { m: `${y}-${String(m + 1).padStart(2, "0")}`, due: st[m + 1] - st[m], held: 0, complete: false, flat: 0, cost: 0, energy: 0, down: 0, tight: 0, tightDown: 0 };
    for (let i = st[m]; i < st[m + 1]; i++) {
      const v = p[i];
      if (isTight.has(i)) { r.tight++; if (v !== null && w[i] === 0) r.tightDown++; }
      if (v === null) continue;
      r.held++; r.flat += v; r.cost += v * w[i]; r.energy += w[i];
      if (w[i] === 0) r.down++;
    }
    r.complete = r.held >= NEAR * r.due;
    if (r.held) out.push(r);
  }
  return out;
}
/** Every month held of a region and market for a load, oldest first. */
export function monthsOf(files: YearFile[], region: string, buy: Buy, x: Pick<Inputs, "run" | "n" | "pct" | "shift">): Month[] {
  return [...files].sort((a, b) => a.year - b.year).flatMap((f) => {
    const p = expand(f, region, buy);
    return monthsOfYear(f.year, p, weights(p, x), f.tight);
  });
}

export type Span = { months: number; held: number; due: number; flat: number | null; per: number | null; cost: number; flatCost: number; energy: number; down: number; tight: number; tightDown: number };
/** The sums of some months: the flat price (USD/MWh), the load's price per MWh consumed, and the totals per MW. */
export function span(ms: Month[]): Span {
  const t = { months: ms.length, held: 0, due: 0, cost: 0, flatCost: 0, energy: 0, down: 0, tight: 0, tightDown: 0 };
  for (const r of ms) { t.held += r.held; t.due += r.due; t.cost += r.cost; t.flatCost += r.flat; t.energy += r.energy; t.down += r.down; t.tight += r.tight; t.tightDown += r.tightDown; }
  return { ...t, flat: t.held ? t.flatCost / t.held : null, per: t.energy ? t.cost / t.energy : null };
}
const prev = (m: string, k: number) => {
  const d = new Date(Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)) - 1 - k, 1));
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
};
/** The last twelve consecutive complete months, oldest first; null when no twelve are held. */
export function lastTwelve(ms: Month[]): Month[] | null {
  const by = new Map(ms.map((r) => [r.m, r]));
  for (const r of [...ms].reverse()) {
    if (!r.complete) continue;
    const twelve = Array.from({ length: 12 }, (_, k) => by.get(prev(r.m, k)));
    if (twelve.every((t) => t && t.complete)) return (twelve as Month[]).reverse();
  }
  return null;
}
/** The complete months of the 36 that end with the last twelve months (or with the newest complete month). */
export function last36(ms: Month[]): { from: string; to: string; months: Month[] } | null {
  const done = ms.filter((r) => r.complete);
  if (!done.length) return null;
  const to = (lastTwelve(ms)?.[11] ?? done[done.length - 1]).m, from = prev(to, 35);
  return { from, to, months: done.filter((r) => r.m >= from && r.m <= to) };
}
const perOf = (r: Month) => (r.energy ? r.cost / r.energy : 0);
/** A bad month for a buyer: of the months given, the one at the top tenth by cost per MWh (nearest rank): one month
 * in ten cost that or more. The mirror of the battery page's 10th-percentile month of revenue. */
export function badMonth(ms: Month[]): Month | null {
  const sorted = ms.filter((r) => r.complete && r.energy > 0).sort((a, b) => perOf(b) - perOf(a) || a.m.localeCompare(b.m));
  return sorted.length ? sorted[Math.max(0, Math.ceil(0.1 * sorted.length) - 1)] : null;
}
export type Year = Span & { y: string; complete: boolean };
/** By calendar year: the sums of its complete months; a year is complete when all twelve are. */
export function years(ms: Month[]): Year[] {
  const ys = [...new Set(ms.map((r) => r.m.slice(0, 4)))].sort();
  return ys.map((y) => {
    const done = ms.filter((r) => r.m.startsWith(y) && r.complete);
    return { y, complete: done.length === 12, ...span(done) };
  }).filter((r) => r.months > 0);
}

// ---------------------------------------------------------------------------------------------------------------------
// the reader's size, the GPUs and the contract
// ---------------------------------------------------------------------------------------------------------------------

/** USD per GPU-hour from power alone: the GPU's power with its share of the facility's overhead, at a price per MWh. */
export const gpuHour = (perMwh: number, gpuKw: number, pue: number) => (perMwh * gpuKw * pue) / 1000;
/** The GPUs a facility of this size powers. */
export const gpus = (mw: number, gpuKw: number, pue: number) => (mw * 1000) / (gpuKw * pue);

export type Contract = { share: number; price: number };  // percent of the energy, USD per MWh
/** The contract panel's results, computed in the browser, over a span of the load (the last twelve months). The
 * contracted share of the energy is bought at the contract price and pays nothing to the market; the rest pays what
 * the market cost. The same arithmetic as the battery page's contract (lib/batterystack.ts, contractResult): a share
 * at the typed price, the rest at the market's figure for the same twelve months. */
export function contractResult(s: Pick<Span, "cost" | "energy">, mw: number, c: Contract) {
  const share = Math.min(100, Math.max(0, c.share)) / 100;
  const contracted = share * s.energy * mw * c.price;
  const market = (1 - share) * s.cost * mw;
  const without = s.cost * mw, mwh = s.energy * mw;
  return { contracted, market, total: contracted + market, per: mwh ? (contracted + market) / mwh : null, without, perWithout: mwh ? without / mwh : null, mwh };
}

// ---------------------------------------------------------------------------------------------------------------------
// words
// ---------------------------------------------------------------------------------------------------------------------

export function usdShort(v: number): string {
  const t = (x: number) => x.toLocaleString("en-US", { maximumFractionDigits: 2 });
  if (Math.abs(v) >= 1e9) return `${t(v / 1e9)} billion`;
  if (Math.abs(v) >= 1e6) return `${t(v / 1e6)} million`;
  return Math.round(v).toLocaleString("en-US");
}
export const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
export const whole = (v: number) => Math.round(v).toLocaleString("en-US");
export const monthName = (m: string) => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });
export const shortMonth = (m: string) => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "short", year: "numeric", timeZone: "UTC" });
/** The load in words, for the summary sentence. */
export function loadWords(x: Inputs): string {
  const size = `${x.mw.toLocaleString("en-US")} MW`;
  if (x.run === "hours") return `A ${size} load that turns off in the ${x.n.toLocaleString("en-US")} most expensive hours of each year`;
  if (x.run === "share") return `A ${size} load that turns off in the most expensive ${x.pct} percent of hours`;
  if (x.run === "shift") return `A ${size} load that moves ${x.shift} percent of each day's energy to the day's cheapest hours`;
  return `A flat ${size} load`;
}
/** When a set of hours of a year fall: the months and the hours of the day they span, in the grid's standard time. */
export function whenOf(y: number, hours: number[]): { months: number[]; from: number; to: number } | null {
  if (!hours.length) return null;
  const st = monthStarts(y), months = new Set<number>(), byHour = new Set<number>();
  for (const i of hours) { months.add(st.findIndex((s, k) => k < 12 && i >= s && i < st[k + 1]) + 1); byHour.add(i % 24); }
  const hs = [...byHour].sort((a, b) => a - b);
  return { months: [...months].sort((a, b) => a - b), from: hs[0], to: hs[hs.length - 1] };
}
const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
export const monthsWords = (ms: number[]) => ms.map((m) => MON[m - 1]).join(", ");
export const hh = (h: number) => `${String(h % 24).padStart(2, "0")}:00`;

// ---------------------------------------------------------------------------------------------------------------------
// Session 140: the flexible load judged on a forecast, not on hindsight; and the load's own hours against clean
// generation. weights() above chooses a load's hours knowing the whole year's prices ("if perfectly foreseen").
// ruleWeights() below is a rule an operator could follow: every decision for an hour rests on prices published before
// that hour begins, and never on the price the hour settles at.
//
//   hours, share   the load is off in an hour when the hour's DAY-AHEAD price (published the day before) is at or
//                  above a threshold fixed before the day begins: the k-th dearest hourly day-ahead price of the PRIOR
//                  days (the 30 days that end where the day begins), with k the share of hours to shed times the hours
//                  held of those days (at least 1). A day whose prior days are not held (under NEAR of their hours) is
//                  not decided: the load runs. The load has a budget: the hours a year the reader named (or the
//                  share of the year's hours). Once a calendar year's budget is used the load runs for the rest of
//                  that year; on a day with more hours at or above the threshold than are left, the dearest day-ahead
//                  hours are taken first. So the load is never off in more hours than the reader asked for, and the
//                  figure "if perfectly foreseen" (the same number of hours, chosen knowing the year) is never worse.
//   shift          each whole day, the energy moves out of the day's dearest DAY-AHEAD hours into its cheapest
//                  day-ahead hours (the N dearest and N cheapest day-ahead hours of each day, N = 24 x shift / 100).
//                  A day with a day-ahead hour missing is not shifted.
// What the load pays is the price of the market it buys in (real time or day-ahead) in the hours it runs.
// ---------------------------------------------------------------------------------------------------------------------

export const PRIOR_DAYS = 30;
export type Rule = "forecast" | "hindsight";
export type Flex = Pick<Inputs, "run" | "n" | "pct" | "shift">;
/** The share of hours a load that turns off means to shed. */
export const shedShare = (x: Flex) => (x.run === "hours" ? Math.min(1, x.n / 8760) : x.run === "share" ? Math.min(1, x.pct / 100) : 0);
/** The rank the threshold stands at: the k-th dearest of `held` prior hours. 0: never off. */
export function shedRank(x: Flex, held: number): number {
  const q = shedShare(x);
  if (q <= 0 || held <= 0) return 0;
  return Math.min(held, Math.max(1, Math.round(q * held)));
}

/** The threshold of each day of consecutive years of day-ahead prices, for a load that turns off: the k-th dearest
 * hourly day-ahead price of the PRIOR_DAYS days before the day; null for a day that is not decided (its prior days
 * are not held, or the load sheds nothing). A day's threshold reads no price of that day or of any later day. */
export function ruleThresholds(da: (number | null)[][], x: Flex): (number | null)[][] {
  const starts: number[] = [];
  let total = 0;
  for (const d of da) { starts.push(total); total += d.length; }
  const all: (number | null)[] = new Array(total);
  for (let y = 0; y < da.length; y++) for (let i = 0; i < da[y].length; i++) all[starts[y] + i] = da[y][i];
  const span30 = 24 * PRIOR_DAYS;
  return da.map((year, y) => {
    const out: (number | null)[] = [];
    for (let d = 0; d + 24 <= year.length; d += 24) {
      const g = starts[y] + d;  // the day's first hour, counted from the first year's first hour
      const prior: number[] = [];
      for (let i = Math.max(0, g - span30); i < g; i++) { const v = all[i]; if (v !== null && v !== undefined) prior.push(v); }
      if (g < span30 || prior.length < NEAR * span30) { out.push(null); continue; }
      const k = shedRank(x, prior.length);
      if (k === 0) { out.push(null); continue; }
      prior.sort((a, b) => b - a);
      out.push(prior[k - 1]);
    }
    return out;
  });
}
/** The hours a load that turns off may be off in a year of `hours` hours: the hours a year the reader named, or the
 * named share of the year's hours. */
export const shedBudget = (x: Flex, hours: number) => Math.round(shedShare(x) * hours);

/** The forecast rule over consecutive years. `pay` and `da` are each year's hourly prices of the market bought in and
 * of the day-ahead market (the same arrays when the load buys day-ahead), one entry an hour, null where not held; the
 * years must be consecutive and oldest first (a year not held is passed as nulls). Returns each year's weights, and
 * for each year the days decided and not decided. The decision for hour h reads da[h], the day-ahead prices of the
 * hours before h's day and how many hours the load has already been off this year; of pay[] it reads only whether the
 * hour is held, never a price. `cap` false leaves out the year's budget of hours (the threshold alone: the load may
 * then be off in more hours than the reader named); the page uses the budget, and scripts/rule-gap.mjs reports both. */
export function ruleWeights(pay: (number | null)[][], da: (number | null)[][], x: Flex, cap = true): { w: number[][]; decided: number[]; undecided: number[] } {
  const w = pay.map((p) => p.map((v) => (v === null ? 0 : 1)));
  const decided = pay.map(() => 0), undecided = pay.map(() => 0);
  if (x.run === "flat") return { w, decided, undecided };
  if (x.run === "shift") {
    const h = (24 * Math.min(50, Math.max(0, x.shift))) / 100, whole = Math.floor(h), part = h - whole;
    for (let y = 0; y < da.length; y++) for (let d = 0; d + 24 <= da[y].length; d += 24) {
      const idx: number[] = [];
      let payHeld = 0;
      for (let i = d; i < d + 24; i++) { if (da[y][i] !== null) idx.push(i); if (pay[y][i] !== null) payHeld++; }
      if (idx.length < 24 || payHeld < 24) { undecided[y]++; continue; }
      decided[y]++;
      idx.sort((a, b) => (da[y][b] as number) - (da[y][a] as number) || a - b);  // dearest day-ahead hour first
      for (let j = 0; j < whole; j++) { w[y][idx[j]] -= 1; w[y][idx[23 - j]] += 1; }
      if (part > 0) { w[y][idx[whole]] -= part; w[y][idx[23 - whole]] += part; }
    }
    return { w, decided, undecided };
  }
  const thresholds = ruleThresholds(da, x);
  for (let y = 0; y < da.length; y++) {
    let left = cap ? shedBudget(x, pay[y].length) : Infinity;  // the year's hours still to be used
    for (let d = 0, n = 0; d + 24 <= da[y].length; d += 24, n++) {
      const threshold = thresholds[y][n];
      if (threshold === null) { undecided[y]++; continue; }
      decided[y]++;
      if (left <= 0) continue;
      const over: number[] = [];
      for (let i = d; i < d + 24; i++) { const v = da[y][i]; if (v !== null && v >= threshold && pay[y][i] !== null) over.push(i); }
      over.sort((a, b) => (da[y][b] as number) - (da[y][a] as number) || a - b);  // the dearest day-ahead hour first
      for (const i of over.slice(0, left)) w[y][i] = 0;
      left -= Math.min(left, over.length);
    }
  }
  return { w, decided, undecided };
}

/** The files of a grid as consecutive years, oldest first: a year between two held that has no file is an empty one. */
function consecutive(files: YearFile[]): YearFile[] {
  const sorted = [...files].sort((a, b) => a.year - b.year);
  if (!sorted.length) return [];
  const by = new Map(sorted.map((f) => [f.year, f]));
  const out: YearFile[] = [];
  for (let y = sorted[0].year; y <= sorted[sorted.length - 1].year; y++) out.push(by.get(y) ?? { grid: sorted[0].grid, year: y, hours: hoursIn(y), built: "", regions: {} });
  return out;
}
export type Ruled = { months: Month[]; weights: Map<number, number[]>; prices: Map<number, (number | null)[]>; decided: number; undecided: number; da: boolean };
/** Every month held of a region and market for a load under a rule, oldest first, with each year's weights and prices.
 * Under "forecast" a load that is not flat needs the region's day-ahead prices: `da` is false when none is held, and
 * then no month is returned. */
export function monthsRuled(files: YearFile[], region: string, buy: Buy, x: Flex, rule: Rule): Ruled {
  const ys = consecutive(files);
  const pay = ys.map((f) => expand(f, region, buy));
  const weightsBy = new Map<number, number[]>(), prices = new Map<number, (number | null)[]>();
  let decided = 0, undecided = 0, w: number[][];
  const haveDa = ys.some((f) => f.regions[region]?.da);
  if (rule === "hindsight" || x.run === "flat") w = pay.map((p) => weights(p, x));
  else {
    if (!haveDa) return { months: [], weights: weightsBy, prices, decided: 0, undecided: 0, da: false };
    const r = ruleWeights(pay, buy === "da" ? pay : ys.map((f) => expand(f, region, "da")), x);
    w = r.w; decided = r.decided.reduce((a, v) => a + v, 0); undecided = r.undecided.reduce((a, v) => a + v, 0);
  }
  const months: Month[] = [];
  ys.forEach((f, i) => { weightsBy.set(f.year, w[i]); prices.set(f.year, pay[i]); months.push(...monthsOfYear(f.year, pay[i], w[i], f.tight)); });
  return { months, weights: weightsBy, prices, decided, undecided, da: haveDa };
}

export function ordinal(k: number): string {
  const t = k % 100, u = k % 10;
  return `${k}${t >= 11 && t <= 13 ? "th" : u === 1 ? "st" : u === 2 ? "nd" : u === 3 ? "rd" : "th"}`;
}
/** The rule in words, for a hover: what the load does and what it knows when it decides. */
export function ruleWords(x: Flex): string {
  if (x.run === "flat") return "";
  if (x.run === "shift") {
    const n = ((24 * Math.min(50, Math.max(0, x.shift))) / 100).toLocaleString("en-US", { maximumFractionDigits: 1 });
    return `Each day the load moves energy out of that day's ${n} dearest day-ahead hours into its ${n} cheapest day-ahead hours. Day-ahead prices are published the day before, so the load knows them when it decides. It pays the price of the market it buys in.`;
  }
  const k = shedRank(x, 24 * PRIOR_DAYS);
  const budget = x.run === "hours" ? `${x.n.toLocaleString("en-US")} hours` : `${x.pct} percent of its hours`;
  return `The load is off in an hour when that hour's day-ahead price, published the day before, is at or above the ${ordinal(k)} dearest hourly day-ahead price of the prior ${PRIOR_DAYS} days (${24 * PRIOR_DAYS} hours), until it has been off in ${budget} of the calendar year; on a day with more such hours than are left, the dearest day-ahead hours first. It decides before the hour and never sees the price the hour settles at. A day whose prior ${PRIOR_DAYS} days are not held is not decided: the load runs.`;
}

/** The carbon-free share of the grid's generation in the hours a load runs: the mean of the hours' shares weighted by
 * the load in each hour, over the hours where the price and the share are both held; and a flat load's over the same
 * hours. Shares are percent. Null when no such hour is held. */
export function cleanShare(clean: (number | null)[], p: (number | null)[], w: number[]): { load: number | null; flat: number | null; hours: number; energy: number } {
  let sw = 0, se = 0, sf = 0, n = 0;
  for (let i = 0; i < clean.length && i < p.length; i++) {
    const c = clean[i];
    if (c === null || c === undefined || p[i] === null) continue;
    n++; sf += c; sw += c * w[i]; se += w[i];
  }
  return { load: se > 0 ? sw / se : null, flat: n ? sf / n : null, hours: n, energy: se };
}
/** A year's hourly list from a stored series (the grid's carbon-free share), null where not held. */
export function expandSeries(s: Series | undefined, hours: number): (number | null)[] {
  const out: (number | null)[] = Array(hours).fill(null);
  if (s) for (let i = 0; i < s.v.length; i++) out[s.s + i] = s.v[i];
  return out;
}
