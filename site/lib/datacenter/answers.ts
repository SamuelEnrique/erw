// Session 228: the three answers "What a datacenter pays" (/cost-of-power) adds beside "What will it pay?": will the
// power be there, how clean, how soon. Pure arithmetic, no React, no imports but the page's own hour arithmetic: Node
// runs this file as it is (scripts/check-values.mjs recomputes every number here from its own read of the same tables;
// scripts/test-datacenter-answers.mjs holds hand cases). Every figure is per MW of the load's size unless its name says
// USD for the size; the page scales by the reader's megawatts. The formulas are in
// docs/methods/datacenter_pays_algorithm.md, sections 4.15 to 4.17.

// The year's hours as lib/datacenter.ts counts them (repeated here so that Node runs this file without a bundler, as
// it runs finance.ts): no import.
const leap = (y: number) => (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;
export const hoursIn = (y: number) => (leap(y) ? 8784 : 8760);
const DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
/** The first hour of each month of a year, and the year's end: thirteen indexes (lib/datacenter.ts, monthStarts). */
export function monthStarts(y: number): number[] {
  const out = [0];
  for (let m = 0; m < 12; m++) out.push(out[m] + 24 * (DAYS[m] + (m === 1 && leap(y) ? 1 : 0)));
  return out;
}

/** The scarcity level: an hour whose price is at or above it is counted short. USD 1,000 per MWh is the cap on an
 * incremental energy offer in every FERC market (Order 831, 2016; CAISO's soft cap, NYISO's, ISO-NE's and SPP's); in
 * ERCOT, outside FERC, a price above it comes from its scarcity pricing (the operating reserve demand curve adders) on
 * top of offers. One level for every grid, so the count means the same thing everywhere. */
export const SCARCITY_USD = 1000;
/** The grids' balancing authorities in EIA-930, as the carbon tables name them. */
export const BA: Record<string, string> = { ercot: "ERCO", caiso: "CISO", nyiso: "NYIS", isone: "ISNE", spp: "SWPP", miso: "MISO", pjm: "PJM" };
export type Way = "flat" | "flex" | "shift";
export const WAYS: Way[] = ["flat", "flex", "shift"];

/** A year's hourly prices and a way's hourly weights, as lib/datacenter.ts holds them (Ruled.prices, Ruled.weights). */
export type Hourly = { prices: Map<number, (number | null)[]>; weights: Map<number, number[]> };
/** A month of one way: its label and its energy per MW (lib/datacenter.ts Month.energy, the sum of the weights). */
export type MonthEnergy = { m: string; energy: number; held: number };

/** The hour's start, in milliseconds since the epoch, of hour `i` of year `y` counted in the grid's standard time
 * (`behind` hours behind UTC all year, as the page's files count them). */
export const hourUtcMs = (y: number, i: number, behind: number) => Date.UTC(y, 0, 1) + (i + behind) * 3600_000;
/** The month label of hour `i` of year `y`. */
export function monthOfHour(y: number, i: number): string {
  const st = monthStarts(y);
  let m = 0;
  while (m < 11 && i >= st[m + 1]) m++;
  return `${y}-${String(m + 1).padStart(2, "0")}`;
}

// ---------------------------------------------------------------------------------------------------------------------
// 1. Will the power be there: the hours at or above the scarcity level in the last twelve months
// ---------------------------------------------------------------------------------------------------------------------

export type ScarceMonth = { m: string; hours: number; usd: number };
export type Scarcity = {
  level: number; months: string[];
  /** the hours counted short, what a flat MW paid in them, and the hours by month and by clock hour (standard time) */
  hours: number; flatUsd: number; byMonth: ScarceMonth[]; byHour: number[];
  /** the ways: the hours each way was off in (weight 0), what a MW of it paid in the scarce hours, and what it avoided against a flat MW */
  ways: Record<Way, { off: number; paidUsd: number; avoidedUsd: number }>;
  /** the clock hours the scarce hours fell in, standard time, first and last (null with none) */
  from: number | null; to: number | null;
};
/** The hours of the last twelve months (`months`, the page's) whose price is at or above the level, for a flat MW and
 * for each way's weights. */
export function scarcity(prices: Map<number, (number | null)[]>, ways: Record<Way, Map<number, number[]>>, months: string[], level = SCARCITY_USD): Scarcity {
  const inL12 = new Set(months);
  const byMonth = new Map<string, ScarceMonth>(), byHour = Array(24).fill(0);
  let hours = 0, flatUsd = 0;
  const w = { flat: { off: 0, paidUsd: 0, avoidedUsd: 0 }, flex: { off: 0, paidUsd: 0, avoidedUsd: 0 }, shift: { off: 0, paidUsd: 0, avoidedUsd: 0 } };
  const clock: number[] = [];
  for (const [y, p] of prices) {
    const st = monthStarts(y);
    for (let m = 0; m < 12; m++) {
      const label = `${y}-${String(m + 1).padStart(2, "0")}`;
      if (!inL12.has(label)) continue;
      for (let i = st[m]; i < st[m + 1]; i++) {
        const v = p[i];
        if (v === null || v === undefined || v < level) continue;
        hours++; flatUsd += v; byHour[i % 24]++; clock.push(i % 24);
        const r = byMonth.get(label) ?? { m: label, hours: 0, usd: 0 };
        r.hours++; r.usd += v; byMonth.set(label, r);
        for (const k of WAYS) {
          const wt = ways[k].get(y)?.[i] ?? 1;
          w[k].paidUsd += v * wt;
          if (wt === 0) w[k].off++;
        }
      }
    }
  }
  for (const k of WAYS) w[k].avoidedUsd = flatUsd - w[k].paidUsd;
  const sortedMonths = [...byMonth.values()].sort((a, b) => a.m.localeCompare(b.m));
  return { level, months, hours, flatUsd, byMonth: sortedMonths, byHour, ways: w, from: clock.length ? Math.min(...clock) : null, to: clock.length ? Math.max(...clock) : null };
}

// ---------------------------------------------------------------------------------------------------------------------
// 2. How clean: the load's carbon, from the grid's intensity of consumed electricity (carbon_intensity_hourly and
//    carbon_intensity_monthly, variable intensity_demand, kg CO2 per MWh)
// ---------------------------------------------------------------------------------------------------------------------

export type IntensityRow = { ts_utc: string; value: number };
export type Carbon = {
  /** the last twelve months at the grid's monthly average, for each way: kg per MWh consumed over the months of the
   * twelve whose intensity is held (`months` of `of`), and tonnes a year per MW at that rate on the year's energy */
  l12: Record<Way, { kgPerMwh: number | null; tonnesPerMw: number | null; energy: number; months: number; of: number }>;
  /** the hours held hour by hour: the window, the hours counted (price and intensity both held), each way's own-hours intensity, the grid's mean over the same hours */
  window: { from: string | null; to: string | null; hours: number; ways: Record<Way, number | null>; grid: number | null };
  /** the grid's intensity by calendar year: the mean of its months held */
  years: { y: number; kg: number; months: number }[];
  /** the grid's intensity by month, as the table holds it */
  monthly: { m: string; kg: number }[];
};
const monthKey = (ts: string) => ts.slice(0, 7);
/** The load's carbon over the last twelve months at the grid's monthly average: each month's energy per MW (a way's)
 * times the month's intensity, over the months of the twelve whose intensity is held; the tonnes a year apply that
 * rate to the year's whole energy. Null when no month of the twelve has an intensity. */
export function l12Carbon(monthly: IntensityRow[], months: Record<Way, MonthEnergy[]>, l12: string[]): Carbon["l12"] {
  const by = new Map(monthly.map((r) => [monthKey(r.ts_utc), r.value]));
  const out = {} as Carbon["l12"];
  for (const k of WAYS) {
    let kg = 0, energy = 0, all = 0, n = 0;
    for (const m of l12) {
      const row = months[k].find((r) => r.m === m), v = by.get(m);
      if (!row) continue;
      all += row.energy;
      if (v === undefined) continue;
      kg += row.energy * v; energy += row.energy; n++;
    }
    const rate = energy > 0 ? kg / energy : null;
    out[k] = { kgPerMwh: rate, tonnesPerMw: rate === null ? null : (rate * all) / 1000, energy: all, months: n, of: l12.length };
  }
  return out;
}
/** Each way's intensity over its own hours in the window the hourly table holds: the sum of weight x intensity over
 * the sum of weights, over the hours in which the price (so the weight) and the intensity are both held; and the
 * grid's plain mean over the same hours. */
export function windowCarbon(hourly: IntensityRow[], h: Record<Way, Hourly>, behind: number): Carbon["window"] {
  const kg = new Map(hourly.map((r) => [Date.parse(r.ts_utc), r.value]));
  const sums = { flat: [0, 0], flex: [0, 0], shift: [0, 0] } as Record<Way, [number, number]>;
  let gridSum = 0, hours = 0, from: number | null = null, to: number | null = null;
  for (const [y, p] of h.flat.prices) {
    for (let i = 0; i < p.length; i++) {
      if (p[i] === null) continue;
      const ms = hourUtcMs(y, i, behind), v = kg.get(ms);
      if (v === undefined) continue;
      hours++; gridSum += v;
      from = from === null ? ms : Math.min(from, ms); to = to === null ? ms : Math.max(to, ms);
      for (const k of WAYS) { const wt = h[k].weights.get(y)?.[i] ?? 0; sums[k][0] += wt * v; sums[k][1] += wt; }
    }
  }
  const iso = (ms: number | null) => (ms === null ? null : new Date(ms).toISOString().replace(/\.\d{3}Z$/, "Z"));
  const ways = { flat: null, flex: null, shift: null } as Record<Way, number | null>;
  for (const k of WAYS) ways[k] = sums[k][1] > 0 ? sums[k][0] / sums[k][1] : null;
  return { from: iso(from), to: iso(to), hours, ways, grid: hours ? gridSum / hours : null };
}
/** The grid's intensity by calendar year: the mean of the months held. */
export function yearlyCarbon(monthly: IntensityRow[]): Carbon["years"] {
  const by = new Map<number, { sum: number; n: number }>();
  for (const r of monthly) { const y = Number(r.ts_utc.slice(0, 4)); const a = by.get(y) ?? { sum: 0, n: 0 }; a.sum += r.value; a.n++; by.set(y, a); }
  return [...by.entries()].sort((a, b) => a[0] - b[0]).map(([y, a]) => ({ y, kg: a.sum / a.n, months: a.n }));
}

// ---------------------------------------------------------------------------------------------------------------------
// 3. How soon: the operator's own figures of large load (ercot_large_load_status)
// ---------------------------------------------------------------------------------------------------------------------

export type StatusRow = { variable: string; ts_utc: string; value: number };
export type Report = { day: string; approved: number | null; running: number | null; simultaneous: number | null; submissions: number | null; submissionsMw: number | null };
export type LargeLoad = { reports: Report[]; latest: Report | null; yearAgo: Report | null; approvedChange: number | null };
/** The reports by day, the latest with an approved figure, the report the change is measured from (the newest one a
 * year or more before it; the earliest held when the reports span less than a year), and the change. */
export function largeLoad(rows: StatusRow[]): LargeLoad {
  const by = new Map<string, Report>();
  for (const r of rows) {
    const day = r.ts_utc.slice(0, 10);
    const p = by.get(day) ?? { day, approved: null, running: null, simultaneous: null, submissions: null, submissionsMw: null };
    if (r.variable === "approved_to_energize_mw") p.approved = r.value;
    else if (r.variable === "observed_nonsimultaneous_peak_mw") p.running = r.value;
    else if (r.variable === "observed_simultaneous_peak_mw") p.simultaneous = r.value;
    else if (r.variable === "new_submissions_count") p.submissions = r.value;
    else if (r.variable === "new_submissions_mw") p.submissionsMw = r.value;
    by.set(day, p);
  }
  const reports = [...by.values()].sort((a, b) => a.day.localeCompare(b.day));
  const withApproved = reports.filter((r) => r.approved !== null);
  const latest = withApproved.at(-1) ?? null;
  const yearAgo = latest ? [...withApproved].reverse().find((r) => Date.parse(r.day) <= Date.parse(latest.day) - 365 * 86400_000) ?? (withApproved[0] !== latest ? withApproved[0] : null) : null;
  return { reports, latest, yearAgo, approvedChange: latest && yearAgo ? latest.approved! - yearAgo.approved! : null };
}

// ---------------------------------------------------------------------------------------------------------------------
// The answers of one address, and each number by its name (the check key's last part)
// ---------------------------------------------------------------------------------------------------------------------

export type Notices = { held: boolean; last: string | null; count: number; byType: Record<string, number> } | null;
export type Answers = { scarcity: Scarcity; carbon: Carbon; largeLoad: LargeLoad | null; notices: Notices; mw: number; held: Record<Way, boolean> };

/** One number of the answers by its name, for the reader's size: the page writes it, check-values recomputes it. */
export function statOf(a: Answers, stat: string): number | null | undefined {
  const p = stat.split(":");
  // USD and tonnes for the reader's size are whole units (the page writes them so, and check-values holds the text to the raw)
  const sized = (v: number | null) => (v === null ? null : Math.round(v * a.mw));
  if (p[0] === "scarce") {
    const s = a.scarcity;
    if (p[1] === "hours") return s.hours;
    if (p[1] === "flat_usd") return sized(s.flatUsd);
    if (p[1] === "off") return a.held[p[2] as Way] ? s.ways[p[2] as Way]?.off : null;
    if (p[1] === "avoided_usd") return a.held[p[2] as Way] ? sized(s.ways[p[2] as Way]?.avoidedUsd ?? null) : null;
    if (p[1] === "paid_usd") return a.held[p[2] as Way] ? sized(s.ways[p[2] as Way]?.paidUsd ?? null) : null;
    if (p[1] === "month") { const r = s.byMonth.find((x) => x.m === p[2]); return p[3] === "usd" ? sized(r?.usd ?? 0) : (r?.hours ?? 0); }
    if (p[1] === "clock") return s.byHour[Number(p[2])];
    return undefined;
  }
  if (p[0] === "co2") {
    const c = a.carbon;
    if (p[1] === "l12") return p[2] === "tonnes" ? sized(c.l12[p[3] as Way]?.tonnesPerMw ?? null) : c.l12[p[3] as Way]?.kgPerMwh;
    if (p[1] === "window") return p[2] === "grid" ? c.window.grid : p[2] === "hours" ? c.window.hours : c.window.ways[p[2] as Way];
    if (p[1] === "year") return c.years.find((r) => r.y === Number(p[2]))?.kg;
    if (p[1] === "month") return c.monthly.find((r) => r.m === p[2])?.kg;
    return undefined;
  }
  if (p[0] === "ll") {
    const l = a.largeLoad;
    if (!l) return undefined;
    if (p[1] === "approved_change") return l.approvedChange === null ? null : Math.abs(l.approvedChange);
    if (p[1] === "report") { const r = l.reports.find((x) => x.day === p[2]); return r ? (r[p[3] as keyof Report] as number | null) : undefined; }
    if (p[1] === "latest") return l.latest ? (l.latest[p[2] as keyof Report] as number | null) : undefined;
    return undefined;
  }
  if (p[0] === "notices") return a.notices ? (p[1] === "count" ? a.notices.count : a.notices.byType[p[1]] ?? 0) : undefined;
  return undefined;
}

// ---------------------------------------------------------------------------------------------------------------------
// The reads: the answers of one address from the live set (session 228). Shared by the page (app/cost-of-power/model.ts,
// through lib/supabase.ts), by scripts/check-values.mjs (through its own reader) and by the page's tables.csv: the
// caller hands over `rows`, a function that reads one Supabase table with PostgREST parameters, so that each reads the
// live set its own way and the arithmetic is one. The ways of running are the page's own (lib/datacenter.ts,
// monthsRuled): a flat load; the load's own flexible way when "Your load" is flexible, else the form's default of a
// load off in the 100 most expensive hours of each year; and a load that shifts its energy within each day, the form's
// default share when "Your load" does not shift.
// ---------------------------------------------------------------------------------------------------------------------
// No import of lib/datacenter.ts here, so that Node runs this file as it is (scripts/check-values.mjs,
// scripts/try-datacenter-answers.mjs): the caller computes the three ways' months, weights and prices with
// lib/datacenter.ts's monthsRuled (the page in app/cost-of-power/model.ts; the scripts in scripts/datacenter-ways.mjs,
// ruledWays) from the specs waysOf gives, and hands them over.
export type Reader = (table: "series" | "events", params: Record<string, string>) => Promise<Record<string, unknown>[]>;
export type Flex = { run: "flat" | "hours" | "share" | "shift"; n: number; pct: number; shift: number };
export const FLAT_LOAD: Flex = { run: "flat", n: 0, pct: 0, shift: 0 };
/** The three ways a load runs for the answers, from "Your load": flat; the load's own flexible way, else the form's
 * default (`n` hours a year off); the load's own shift, else the form's default share. */
export function waysOf(x: Flex, defaults: { n: number; shift: number }): Record<Way, Flex> {
  return {
    flat: FLAT_LOAD,
    flex: x.run === "hours" || x.run === "share" ? x : { run: "hours", n: defaults.n, pct: 0, shift: 0 },
    shift: x.run === "shift" ? x : { run: "shift", n: 0, pct: 0, shift: defaults.shift },
  };
}
/** The way "Your load" is, among the three. */
export const ownWay = (x: Flex): Way => (x.run === "flat" ? "flat" : x.run === "shift" ? "shift" : "flex");

/** One way's months, weights and prices as lib/datacenter.ts's monthsRuled gives them. */
export type Ruled = { months: MonthEnergy[]; weights: Map<number, number[]>; prices: Map<number, (number | null)[]> };
export type Ruleds = Record<Way, Ruled>;
export type AnswerArgs = { grid: string; mw: number; l12: string[]; behind: number; ruled: Ruleds; rows: Reader };

const num = (v: unknown) => Number(v);
/** The answers of one address, read from the live set and computed from the page's own files. */
export async function readAnswers(args: AnswerArgs): Promise<Answers> {
  const { grid, mw, l12, behind, rows, ruled } = args;
  const held = { flat: ruled.flat.months.length > 0, flex: ruled.flex.months.length > 0, shift: ruled.shift.months.length > 0 } as Record<Way, boolean>;
  const entity = `eia930:${BA[grid] ?? grid.toUpperCase()}`;
  const [monthlyRaw, hourlyRaw, statusRaw, noticesRaw] = await Promise.all([
    rows("series", { select: "ts_utc,value", table_name: "eq.carbon_intensity_monthly", entity: `eq.${entity}`, variable: "eq.intensity_demand", order: "ts_utc" }),
    rows("series", { select: "ts_utc,value", table_name: "eq.carbon_intensity_hourly", entity: `eq.${entity}`, variable: "eq.intensity_demand", order: "ts_utc" }),
    grid === "ercot" ? rows("series", { select: "variable,ts_utc,value", table_name: "eq.ercot_large_load_status", entity: "eq.ercot:large_load", order: "ts_utc" }) : Promise.resolve([]),
    grid === "caiso" ? rows("events", { select: "event_date,event_type", table_name: "eq.caiso_grid_emergencies", order: "event_date.desc" }) : Promise.resolve([]),
  ]);
  const monthly: IntensityRow[] = monthlyRaw.map((r) => ({ ts_utc: String(r.ts_utc), value: num(r.value) }));
  const hourly: IntensityRow[] = hourlyRaw.map((r) => ({ ts_utc: String(r.ts_utc), value: num(r.value) }));
  const waysWeights = { flat: ruled.flat.weights, flex: ruled.flex.weights, shift: ruled.shift.weights } as Record<Way, Map<number, number[]>>;
  const sc = scarcity(ruled.flat.prices, waysWeights, l12);
  for (const k of WAYS) if (!held[k]) sc.ways[k] = { off: 0, paidUsd: sc.flatUsd, avoidedUsd: 0 };
  const months = {} as Record<Way, MonthEnergy[]>;
  for (const k of WAYS) months[k] = ruled[k].months.map((m) => ({ m: m.m, energy: m.energy, held: m.held }));
  const hourlyWays = {} as Record<Way, Hourly>;
  for (const k of WAYS) hourlyWays[k] = { prices: ruled.flat.prices, weights: ruled[k].weights };
  const carbon = { l12: l12Carbon(monthly, months, l12), window: windowCarbon(hourly, hourlyWays, behind), years: yearlyCarbon(monthly), monthly: monthly.map((r) => ({ m: r.ts_utc.slice(0, 7), kg: r.value })) };
  for (const k of WAYS) if (!held[k]) { carbon.l12[k] = { kgPerMwh: null, tonnesPerMw: null, energy: 0, months: 0, of: l12.length }; carbon.window.ways[k] = null; }
  const status: StatusRow[] = statusRaw.map((r) => ({ variable: String(r.variable), ts_utc: String(r.ts_utc), value: num(r.value) }));
  let notices: Notices = null;
  if (grid === "caiso") {
    const first = `${l12[0]}-01`, last = l12.at(-1)!;
    const inWindow = noticesRaw.filter((r) => { const d = String(r.event_date).slice(0, 10); return d >= first && d.slice(0, 7) <= last; });
    const byType: Record<string, number> = {};
    for (const r of inWindow) byType[String(r.event_type)] = (byType[String(r.event_type)] ?? 0) + 1;
    notices = { held: noticesRaw.length > 0, last: noticesRaw.length ? String(noticesRaw[0].event_date).slice(0, 10) : null, count: inWindow.length, byType };
  }
  return { scarcity: sc, carbon, largeLoad: grid === "ercot" && status.length ? largeLoad(status) : null, notices, mw, held };
}
