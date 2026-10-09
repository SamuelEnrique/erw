// Energy Research Warehouse (ERW) site, session 162: the co-optimized hybrid and the reader's own profile on "What a
// generator earns" (/cost-of-power/seller). One implementation: the page (server), the box "Your plant's profile"
// (browser) and scripts/test-hybrid.mjs all call these functions; warehouse/derived/seller_hybrid.py solves the same
// program with scipy and tests/test_session162.py holds the two to one figure. No imports: Node runs this file as it
// is. docs/methods/cost_of_power.md, "Session 162".
//
// The pair: a plant and a battery behind one interconnection, each day on its own, the day's day-ahead prices known
// when the schedule is made (an upper bound for a schedule made the day before). Per hour, with the plant's output g
// (MWh, never below zero), the price p, the battery's power P, its energy E and the limit L:
//
//   maximize   sum p x (g + discharge - charge)
//   charge     0 to min(P, L + g): what the plant does not supply is bought, the purchase inside the limit
//   discharge  0 to min(P, L - g): the pair's export inside the limit; none in an hour whose price is below zero
//   energy     state of charge = sum(eta x charge - discharge / eta), eta = sqrt(0.86), between 0 and E, each day
//              from empty; at most one full cycle a day (sum discharge / eta <= E): the battery page's rules
//
// The plant sells every hour at its price, so the pair's revenue is the plant's plus what the battery adds, and an
// idle battery is always allowed: the pair never earns less than the plant alone.

export const RTE = 0.86;  // round trip, as the battery page states it (lib/batterystack.ts, RTE; a test holds them equal)
const EPS = 1e-9;

export type DaySolution = { value: number; charge: number[]; discharge: number[]; soc: number[]; iterations: number };

/** A linear program, maximize c.x subject to A x <= b (b >= 0) and 0 <= x <= ub, by the simplex method with bounded
 *  variables (a variable not in the basis sits at zero or at its upper bound). Largest reduced cost first; after a
 *  run of steps without progress, the lowest index first (Bland's rule), which cannot cycle. */
export function simplex(c: number[], A: number[][], b: number[], ub: number[]): { x: number[]; iterations: number } {
  const n = c.length, m = A.length, w = n + m;
  const T: Float64Array[] = A.map((row, i) => { const r = new Float64Array(w); for (let j = 0; j < n; j++) r[j] = row[j]; r[n + i] = 1; return r; });
  const rhs = Float64Array.from(b);
  const r = new Float64Array(w);
  for (let j = 0; j < n; j++) r[j] = c[j];
  const basis = Array.from({ length: m }, (_, i) => n + i);
  const inBasis = new Uint8Array(w); for (let i = 0; i < m; i++) inBasis[n + i] = 1;
  const flipped = new Uint8Array(w);
  const bound = (j: number) => (j < n ? ub[j] : Infinity);
  let iterations = 0;
  for (;;) {
    if (++iterations > 50000) throw new Error("the linear program did not end");
    const bland = iterations > 2000;
    let j = -1, best = 1e-9;
    for (let k = 0; k < w; k++) {
      if (inBasis[k] || bound(k) <= 0) continue;
      if (r[k] > best) { j = k; if (bland) break; best = r[k]; }
    }
    if (j < 0) break;
    let step = bound(j), leave = -1, upper = false;
    for (let i = 0; i < m; i++) {
      const a = T[i][j];
      if (a > EPS) {
        const t = Math.max(0, rhs[i]) / a;
        if (t < step - 1e-12 || (t <= step + 1e-12 && leave >= 0 && basis[i] < basis[leave])) { step = t; leave = i; upper = false; }
      } else if (a < -EPS && bound(basis[i]) !== Infinity) {
        const t = Math.max(0, bound(basis[i]) - rhs[i]) / -a;
        if (t < step - 1e-12 || (t <= step + 1e-12 && leave >= 0 && basis[i] < basis[leave])) { step = t; leave = i; upper = true; }
      }
    }
    if (step === Infinity) throw new Error("the linear program has no bound");
    if (leave < 0) {
      // the entering variable reaches its own upper bound: it now counts down from there
      const u = bound(j);
      for (let i = 0; i < m; i++) { rhs[i] -= u * T[i][j]; T[i][j] = -T[i][j]; }
      r[j] = -r[j];
      flipped[j] ^= 1;
      continue;
    }
    if (upper) {
      // the leaving variable goes to its upper bound: write its row for the distance below that bound
      const k = basis[leave], row = T[leave];
      for (let q = 0; q < w; q++) if (q !== k) row[q] = -row[q];
      rhs[leave] = bound(k) - rhs[leave];
      flipped[k] ^= 1;
    }
    const row = T[leave], pv = row[j];
    for (let q = 0; q < w; q++) row[q] /= pv;
    rhs[leave] /= pv;
    for (let i = 0; i < m; i++) {
      if (i === leave) continue;
      const f = T[i][j];
      if (f === 0) continue;
      const ri = T[i];
      for (let q = 0; q < w; q++) ri[q] -= f * row[q];
      rhs[i] -= f * rhs[leave];
    }
    const f = r[j];
    for (let q = 0; q < w; q++) r[q] -= f * row[q];
    inBasis[basis[leave]] = 0; inBasis[j] = 1; basis[leave] = j;
  }
  const v = new Float64Array(w);
  for (let i = 0; i < m; i++) v[basis[i]] = rhs[i];
  const x: number[] = [];
  for (let j = 0; j < n; j++) x.push(Math.min(ub[j], Math.max(0, flipped[j] ? ub[j] - v[j] : v[j])));
  return { x, iterations };
}

/** One day of the battery beside a plant. p: the day's hourly prices; g: the plant's output by hour (MWh, zero for a
 *  battery alone); power and energy: the battery's MW and MWh; limit: the interconnection, MW (Infinity for a battery
 *  alone, limited by its own power). The value is what the battery adds to the plant's revenue. */
export function solveDay(p: number[], g: number[], power: number, energy: number, limit: number, rte = RTE): DaySolution {
  const T = p.length;
  const zero = () => new Array<number>(T).fill(0);
  if (!(power > 0) || !(energy > 0)) return { value: 0, charge: zero(), discharge: zero(), soc: zero(), iterations: 0 };
  const eta = Math.sqrt(rte);
  const c: number[] = [], ub: number[] = [];
  for (let t = 0; t < T; t++) { c.push(-p[t]); ub.push(Math.min(power, limit + g[t])); }
  for (let t = 0; t < T; t++) { c.push(p[t]); ub.push(p[t] < 0 ? 0 : Math.min(power, Math.max(0, limit - g[t]))); }
  const A: number[][] = [], b: number[] = [];
  for (let t = 0; t < T; t++) {
    const s = new Array<number>(2 * T).fill(0);
    for (let k = 0; k <= t; k++) { s[k] = eta; s[T + k] = -1 / eta; }
    A.push(s); b.push(energy);                 // full
    A.push(s.map((v) => -v)); b.push(0);       // empty
  }
  const cyc = new Array<number>(2 * T).fill(0);
  for (let t = 0; t < T; t++) cyc[T + t] = 1 / eta;
  A.push(cyc); b.push(energy);                 // at most one full cycle a day
  const sol = simplex(c, A, b, ub);
  const charge = sol.x.slice(0, T), discharge = sol.x.slice(T);
  // at a price of zero or more, charging and discharging together never pays; where a tie left both, net them
  for (let t = 0; t < T; t++) {
    if (p[t] < 0) continue;
    const both = Math.min(charge[t], discharge[t] / (eta * eta));
    if (both > 0) { charge[t] -= both; discharge[t] -= both * eta * eta; }
  }
  const soc: number[] = [];
  let s = 0, value = 0;
  for (let t = 0; t < T; t++) { s += eta * charge[t] - discharge[t] / eta; soc.push(s); value += p[t] * (discharge[t] - charge[t]); }
  return { value, charge, discharge, soc, iterations: sol.iterations };
}

/** What breaks in a day's schedule, in words: an empty list when every limit holds in every hour. */
export function checkDay(sol: DaySolution, p: number[], g: number[], power: number, energy: number, limit: number, rte = RTE, tol = 1e-6): string[] {
  const eta = Math.sqrt(rte), bad: string[] = [];
  let out = 0;
  for (let t = 0; t < p.length; t++) {
    const c = sol.charge[t], d = sol.discharge[t];
    if (c < -tol || c > power + tol) bad.push(`hour ${t}: charge ${c} outside 0 to ${power}`);
    if (d < -tol || d > power + tol) bad.push(`hour ${t}: discharge ${d} outside 0 to ${power}`);
    if (Math.min(c, d) > tol) bad.push(`hour ${t}: charging and discharging together`);
    if (sol.soc[t] < -tol || sol.soc[t] > energy + tol) bad.push(`hour ${t}: state of charge ${sol.soc[t]} outside 0 to ${energy}`);
    if (g[t] + d - c > limit + tol) bad.push(`hour ${t}: export ${g[t] + d - c} above the limit ${limit}`);
    if (c - d - g[t] > limit + tol) bad.push(`hour ${t}: purchase ${c - d - g[t]} above the limit ${limit}`);
    if (p[t] < 0 && d > tol) bad.push(`hour ${t}: discharge at a price below zero`);
    out += d / eta;
  }
  if (out > energy + tol) bad.push(`more than one full cycle: ${out} MWh taken out`);
  return bad;
}

export type Day = { p: number[]; g: number[] };
export type Totals = {
  days: number; hours: number; energy: number; plant: number; pair: number; battery: number; added: number;
  charged: number; fromPlant: number; discharged: number; limit: number; capture: number | null; flat: number | null;
};

/** The plant's capacity as the interconnection limit: the capacity named, or the plant's highest hour when that is higher. */
export function limitOf(days: Day[], capacity: number): number {
  let top = capacity;
  for (const d of days) for (const v of d.g) if (v > top) top = v;
  return top;
}

/** A span of days: the plant alone, the battery alone (its own interconnection, no plant), the co-optimized pair, and
 *  the two alone added. `added` is never below `pair`: the pair is the same two assets under one more limit. */
export function totals(days: Day[], power: number, hours: number, capacity: number, rte = RTE): Totals {
  const limit = limitOf(days, capacity);
  const energyCap = power * hours;
  let n = 0, energy = 0, plant = 0, add = 0, alone = 0, charged = 0, fromPlant = 0, discharged = 0, sp = 0;
  for (const d of days) {
    const T = d.p.length;
    for (let t = 0; t < T; t++) { plant += d.p[t] * d.g[t]; energy += d.g[t]; sp += d.p[t]; }
    n += T;
    const s = solveDay(d.p, d.g, power, energyCap, limit, rte);
    add += s.value;
    for (let t = 0; t < T; t++) { charged += s.charge[t]; fromPlant += Math.min(s.charge[t], d.g[t]); discharged += s.discharge[t]; }
    alone += solveDay(d.p, new Array<number>(T).fill(0), power, energyCap, Infinity, rte).value;
  }
  return { days: days.length, hours: n, energy, plant, pair: plant + add, battery: alone, added: plant + alone, charged, fromPlant, discharged, limit,
    capture: energy > 0 ? plant / energy : null, flat: n ? sp / n : null };
}

// the page's own plants: data/seller/hybrid.json (warehouse/derived/seller_hybrid.py)

export type HybridFuel = { months: string[]; days: number; left_out: number; peak: number };
export type HybridCheck = { fuel: string; hours: number; battery_mw_per_plant_mw: number; plant: number; pair: number; battery: number; energy: number; charged: number; from_plant: number; discharged: number; limit: number };
export type HybridGrid = {
  name: string; tz: string; hub: string; market: string; basis: string; tables: string[]; workbook: string; capacity: string; t0: string;
  fuels: Record<string, HybridFuel>; check: HybridCheck[]; days: [string, number, number][]; price: (number | null)[]; solar: (number | null)[]; wind: (number | null)[];
};
export type YearFile = { year: number; hours: number; held: number; file: string };
export type HybridFile = { built: string; method: string; rte: number; near_days: number; near_year: number; grids: Record<string, HybridGrid>; years: Record<string, YearFile[]> };

/** The days of a fuel's twelve months that are held whole (every hour a price and the fuel's output), the output
 *  scaled to a plant of `mw`. A day with a missing hour is left out, never filled. */
export function daysOf(g: HybridGrid, fuel: "solar" | "wind", mw: number): Day[] {
  const f = g.fuels[fuel];
  if (!f) return [];
  const out: Day[] = [];
  const shape = g[fuel];
  for (const [date, i0, T] of g.days) {
    const m = date.slice(0, 7);
    if (m < f.months[0] || m > f.months[11]) continue;
    const p: number[] = [], q: number[] = [];
    let whole = true;
    for (let t = i0; t < i0 + T; t++) {
      const a = g.price[t], b = shape[t];
      if (a === null || a === undefined || b === null || b === undefined) { whole = false; break; }
      p.push(a); q.push(b * mw);
    }
    if (whole) out.push({ p, g: q });
  }
  return out;
}

// (c) the reader's own profile

export type Parsed = { ok: true; values: number[] } | { ok: false; why: string };
const leap = (y: number) => (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;
export const hoursOfYear = (y: number) => (leap(y) ? 8784 : 8760);

/** The reader's text as one value an hour. Accepted: one number a line, or a CSV (comma, semicolon or tab) in which
 *  exactly one column is a number in every row; a first line that holds no number is a header and is skipped; empty
 *  lines after the last value are ignored. Refused, with the reason: an empty line or an empty value between values
 *  (a gap), a value that is not a plain number, a value below zero, and any count of values other than the year's
 *  (8,760, or 8,784 in a leap year). Nothing is filled, trimmed to length or repaired. */
export function parseProfile(text: string, year: number): Parsed {
  const need = hoursOfYear(year);
  const lines = text.replace(/^﻿/, "").split(/\r\n|\r|\n/);
  while (lines.length && lines[lines.length - 1].trim() === "") lines.pop();
  if (!lines.length) return { ok: false, why: "Nothing was pasted." };
  const plain = /^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$/;
  const split = (l: string) => l.split(/[,;\t]/).map((s) => s.trim());
  let rows = lines.map(split);
  if (!rows[0].some((s) => plain.test(s))) rows = rows.slice(1);  // a header
  const first = lines.length - rows.length + 1;  // the file's line number of the first data row
  if (!rows.length) return { ok: false, why: "The text holds a header and no value." };
  const width = rows[0].length;
  for (let i = 0; i < rows.length; i++) {
    if (rows[i].length === 1 && rows[i][0] === "") return { ok: false, why: `Line ${first + i} is empty: a gap. Nothing is filled, so the profile is not read.` };
    if (rows[i].length !== width) return { ok: false, why: `Line ${first + i} holds ${rows[i].length} columns and the first row holds ${width}.` };
  }
  const numeric: number[] = [];
  for (let k = 0; k < width; k++) if (rows.every((r) => plain.test(r[k]))) numeric.push(k);
  if (width > 1 && numeric.length > 1) return { ok: false, why: `${numeric.length} columns hold numbers in every row. Keep one: the plant's output.` };
  if (numeric.length === 0) {
    for (let i = 0; i < rows.length; i++) {
      const bad = rows[i].find((s) => !plain.test(s));
      if (width === 1 && bad !== undefined) return { ok: false, why: bad === "" ? `Line ${first + i} is empty: a gap. Nothing is filled, so the profile is not read.` : `Line ${first + i} is not a number: "${bad.slice(0, 20)}".` };
    }
    return { ok: false, why: "No column holds a number in every row: a value is missing or is not a number." };
  }
  const values = rows.map((r) => Number(r[numeric[0]]));
  const at = values.findIndex((v) => !Number.isFinite(v));
  if (at >= 0) return { ok: false, why: `Line ${first + at} is not a number.` };
  const neg = values.findIndex((v) => v < 0);
  if (neg >= 0) return { ok: false, why: `Line ${first + neg} is below zero (${values[neg]}). A plant's output is zero or more.` };
  if (values.length !== need) return { ok: false, why: `${values.length.toLocaleString("en-US")} values were read and ${year} has ${need.toLocaleString("en-US")} hours. The profile must hold every hour of the year, once.` };
  return { ok: true, values };
}

export type PriceYear = { grid: string; name: string; hub: string; market: string; year: number; utc_offset_hours: number; first_utc: string; hours: number; held: number; tables: string[]; built: string; price: (number | null)[] };
export type ProfileResult = {
  hours: number; priced: number; energy: number; energyPriced: number; revenue: number; capture: number | null; flat: number | null; ratio: number | null;
  peak: number; days: number; daysOut: number; hybrid: Totals | null;
};

/** The reader's year against the hub's hourly prices of that year, hour for hour. Revenue, the capture price and the
 *  flat average are over the hours that hold a price; an hour without one is in none of them. The hybrid takes the
 *  days (24 hours each, local standard time) whose every hour holds a price; the others are left out and counted. */
export function profileResult(values: number[], prices: (number | null)[], power: number, hours: number, rte = RTE): ProfileResult {
  let priced = 0, energy = 0, energyPriced = 0, revenue = 0, sp = 0, peak = 0;
  for (let i = 0; i < values.length; i++) {
    const p = prices[i], v = values[i];
    energy += v;
    if (v > peak) peak = v;
    if (p === null || p === undefined) continue;
    priced += 1; sp += p; energyPriced += v; revenue += p * v;
  }
  const days: Day[] = [];
  const n = Math.floor(values.length / 24);
  for (let d = 0; d < n; d++) {
    const p = prices.slice(d * 24, d * 24 + 24);
    if (p.some((v) => v === null || v === undefined)) continue;
    days.push({ p: p as number[], g: values.slice(d * 24, d * 24 + 24) });
  }
  const capture = energyPriced > 0 ? revenue / energyPriced : null, flat = priced ? sp / priced : null;
  return { hours: values.length, priced, energy, energyPriced, revenue, capture, flat, ratio: capture !== null && flat !== null && flat > 0 ? (100 * capture) / flat : null,
    peak, days: days.length, daysOut: n - days.length, hybrid: power > 0 && days.length ? totals(days, power, hours, peak, rte) : null };
}
