// Session 67: the battery revenue stack ("What a battery earns", /cost-of-power/battery). Every number on the page is
// computed here from the rows of battery_stack_monthly and battery_stack_stress_daily (warehouse/derived/battery_stack.py),
// by the page, by its contract panel in the browser and by scripts/check-values.mjs alike (key
// bs|<inputs>|<stat>). No imports: Node runs this file as it is. docs/methods/battery_stack.md.
//
// The tables are per MW of rated power; the page scales by the reader's size. Energy and ancillary services are split
// hour by hour by one linear program a day, so the streams add up with nothing counted twice. No capacity payment is in
// it: ERCOT has none, California's is not held, and the other markets' capacity prices are internal and never read here.

export type Row = { variable: string; ts_utc: string; value: number };
export type Strategy = "foresight" | "dayahead";
export type Duration = 2 | 4 | 8;
export type Inputs = { grid: string; dur: Duration; strat: Strategy; mw: number; fom: number; ds: number };
export type Month = {
  m: string; held: boolean; daysHeld: number; daysOut: number; daysOutAncillary: number; daysOutEnergy: number; daysInMonth: number;
  energy: number | null; ancillary: number | null; total: number | null; products: Record<string, number>;
};

export const TABLE = "battery_stack_monthly";
// Session 86: the grids in review (NYISO, SPP) are in a table of their own, held out of the live set; the page reads
// them from data/battery_stack_review.json, and only in the internal view.
export const REVIEW_TABLE = "battery_stack_review_monthly";
export const STRESS_TABLE = "battery_stack_stress_daily";
export const RTE = 0.86;   // round trip, as warehouse/derived/battery_stack.py and the seller tab
export const NEAR = 0.9;  // a month counts when at least this share of its days is held (the seller tab's rule)
export const DURATIONS: Duration[] = [2, 4, 8];
export const STRATEGIES: Record<Strategy, string> = { foresight: "Perfect foresight", dayahead: "Day-ahead schedule" };

/** The grids the tool is built for. Two are ready; the others are listed with the reason they are not.
 * Session 86: `review` marks a grid that is built and waits for approval (its energy and reserve prices are both
 * public): greyed for a visitor exactly as before, open in the internal view. A grid whose reserve prices are internal
 * is not built; it says "held, not shown: license needed". `at` is where energy is priced, when it is not a hub. */
export const GRIDS: { id: string; name: string; ready: boolean; review?: boolean; why?: string; hub?: string; at?: string; entity?: string; from?: string }[] = [
  { id: "ercot", name: "ERCOT", ready: true, hub: "HB_HUBAVG", entity: "ercot:HB_HUBAVG", from: "2018" },
  { id: "caiso", name: "CAISO", ready: true, hub: "SP15", entity: "caiso:TH_SP15_GEN-APND", from: "September 2024" },
  { id: "pjm", name: "PJM", ready: false, why: "license needed" },
  { id: "nyiso", name: "NYISO", ready: false, review: true, why: "coming", hub: "N.Y.C.", at: "N.Y.C. zone (New York City)", entity: "nyiso:N.Y.C.", from: "September 2024" },
  { id: "isone", name: "ISO-NE", ready: false, why: "held, not shown: license needed" },
  { id: "miso", name: "MISO", ready: false, why: "held, not shown: license needed" },
  { id: "spp", name: "SPP", ready: false, review: true, why: "coming", hub: "SPPNORTH_HUB", entity: "spp:SPPNORTH_HUB", from: "September 2024" },
];
export const READY = GRIDS.filter((g) => g.ready);
export const IN_REVIEW = GRIDS.filter((g) => g.review);
/** Whether a grid can be opened: a ready one by anyone, one in review only in the internal view. */
export const opens = (id: string | undefined, internal: boolean) => READY.some((g) => g.id === id) || (internal && IN_REVIEW.some((g) => g.id === id));
export const gridOf = (id: string) => GRIDS.find((g) => g.id === id)!;

/** The ancillary products of each market, in the order the page lists them. */
export const PRODUCTS: Record<string, { key: string; label: string }[]> = {
  ercot: [
    { key: "regup", label: "Regulation Up" }, { key: "regdn", label: "Regulation Down" }, { key: "rrs", label: "Responsive Reserve" },
    { key: "ecrs", label: "ECRS (from June 2023)" }, { key: "nspin", label: "Non-Spin" },
  ],
  caiso: [
    { key: "regup", label: "Regulation Up" }, { key: "regdn", label: "Regulation Down" }, { key: "spin", label: "Spinning Reserve" },
    { key: "nonspin", label: "Non-Spinning Reserve" },
  ],
  // session 86, in review
  nyiso: [{ key: "reg", label: "Regulation Capacity (up and down)" }, { key: "spin", label: "10-Minute Spinning Reserve" }],
  spp: [
    { key: "regup", label: "Regulation Up" }, { key: "regdn", label: "Regulation Down" }, { key: "spin", label: "Spinning Reserve" },
    { key: "supp", label: "Supplemental Reserve" },
  ],
};
/** What the capacity row says, in words: no number from a capacity table is ever shown. */
export const CAPACITY_WORDS: Record<string, string> = {
  ercot: "None: an energy-only market",
  caiso: "Not held: California's resource adequacy prices are contract statistics, not yet in the warehouse",
  nyiso: "Not shown: New York's capacity prices are held and their license is under review",
  spp: "None: SPP has no capacity market",
};

/** Lazard, "Levelized Cost of Energy+", June 2025, LCOS v10.0, utility-scale standalone storage, the midpoint of its low
 * and high: 100 MW / 200 MWh (capital 610 USD/kW, fixed O&M 11.2 USD/kW-yr) and 100 MW / 400 MWh (1,110 and 22), the
 * seller tab's defaults. Lazard prints no 8-hour case: its line is the straight line through the 2- and 4-hour figures
 * (capital 110 USD/kW plus 250 USD/kWh; fixed O&M 0.4 USD/kW-yr plus 5.4 USD/kWh-yr), an extrapolation and said so. */
export const COSTS: Record<Duration, { capex: number; fom: number; note: string }> = {
  2: { capex: 610, fom: 11.2, note: "Lazard's 100 MW / 200 MWh case, midpoint of 340 to 880 USD/kW and of 3.0 to 8.2 USD/kWh-yr" },
  4: { capex: 1110, fom: 22, note: "Lazard's 100 MW / 400 MWh case, midpoint of 620 to 1,600 USD/kW and of 3.0 to 8.0 USD/kWh-yr" },
  8: { capex: 2110, fom: 43.6, note: "no Lazard case: the straight line through its 2-hour and 4-hour midpoints, an extrapolation" },
};
export const DEBT = { share: 0.6, rate: 0.08, life: 20 };  // Lazard: 60 percent debt at 8 percent, over a 20-year life
export const crf = (rate: number, n: number) => rate / (1 - (1 + rate) ** -n);
/** The default annual debt payment per MW: the capital cost, 60 percent debt at 8 percent, level over 20 years. */
export const debtPerMw = (d: Duration) => COSTS[d].capex * 1000 * DEBT.share * crf(DEBT.rate, DEBT.life);

/** The inputs from a query (strings), each defaulted and bounded. */
export function inputsOf(q: Record<string, string | undefined>, internal = false): Inputs {
  const num = (v: string | undefined, d: number, lo: number, hi: number) => {
    const x = v === undefined || v === "" ? NaN : Number(v);
    return Number.isFinite(x) ? Math.min(hi, Math.max(lo, x)) : d;
  };
  const grid = opens(q.grid, internal) ? q.grid! : "ercot";  // session 86: a grid in review opens only in the internal view
  const dur = (DURATIONS.includes(Number(q.dur) as Duration) ? Number(q.dur) : 4) as Duration;
  const strat = (q.strat === "dayahead" ? "dayahead" : "foresight") as Strategy;
  const mw = num(q.mw, 100, 1, 5000);
  return { grid, dur, strat, mw, fom: num(q.fom, COSTS[dur].fom, 0, 500), ds: Math.round(num(q.ds, debtPerMw(dur) * mw, 0, 1e11)) };
}
/** The inputs as a stable string: the check keys' and the links' form. */
export const inputsKey = (x: Inputs) => `grid=${x.grid}&dur=${x.dur}&strat=${x.strat}&mw=${x.mw}&fom=${x.fom}&ds=${x.ds}`;
export function parseKey(k: string, internal = false): Inputs {
  return inputsOf(Object.fromEntries(k.split("&").map((p) => p.split("=") as [string, string])), internal);
}
/** The query of a link: only what differs from the defaults of the chosen duration, so a duration link carries no stale
 * cost default. */
export function hrefOf(x: Inputs, change: Partial<Inputs> = {}): string {
  const y = { ...x, ...change };
  const q: string[] = [`grid=${y.grid}`, `dur=${y.dur}`, `strat=${y.strat}`];
  if (y.mw !== 100) q.push(`mw=${y.mw}`);
  // a cost the reader typed is kept across a strategy or grid change, and dropped when the duration changes (its
  // default scales with the duration)
  if (y.dur === x.dur) {
    if (y.fom !== COSTS[y.dur].fom) q.push(`fom=${y.fom}`);
    if (y.ds !== Math.round(debtPerMw(y.dur) * x.mw)) q.push(`ds=${y.ds}`);
  }
  return `/cost-of-power/battery?${q.join("&")}`;
}

/** The months of one strategy and duration from the table's rows of one hub, per MW. */
export function monthsOf(rows: Row[], strat: Strategy, dur: Duration): Month[] {
  const pre = `${strat}_${dur}h_`;
  const by = new Map<string, Record<string, number>>();
  for (const r of rows) {
    if (!r.variable.startsWith(pre)) continue;
    const m = r.ts_utc.slice(0, 7);
    if (!by.has(m)) by.set(m, {});
    by.get(m)![r.variable.slice(pre.length)] = Number(r.value);
  }
  const out: Month[] = [];
  for (const [m, v] of [...by.entries()].sort((a, b) => a[0].localeCompare(b[0]))) {
    const daysHeld = v.days_held ?? 0, daysInMonth = v.days_in_month ?? 0;
    const products: Record<string, number> = {};
    for (const [k, x] of Object.entries(v)) {
      const hit = /^revenue_(.+)_usd_per_mw$/.exec(k);
      if (hit && !["energy", "ancillary", "total"].includes(hit[1])) products[hit[1]] = x;
    }
    const has = v.revenue_total_usd_per_mw !== undefined;
    out.push({
      m, daysHeld, daysOut: v.days_left_out ?? 0, daysOutAncillary: v.days_left_out_ancillary ?? 0, daysOutEnergy: v.days_left_out_energy ?? 0, daysInMonth,
      held: has && daysInMonth > 0 && daysHeld / daysInMonth >= NEAR - 1e-9,
      energy: has ? v.revenue_energy_usd_per_mw : null, ancillary: has ? v.revenue_ancillary_usd_per_mw : null,
      total: has ? v.revenue_total_usd_per_mw : null, products,
    });
  }
  return out;
}

export type Stream = "energy" | "ancillary" | "total" | string;
const pick = (r: Month, s: Stream): number | null =>
  s === "energy" ? r.energy : s === "ancillary" ? r.ancillary : s === "total" ? r.total : r.total === null ? null : (r.products[s] ?? 0);

/** An average year of one stream, per MW: the mean of each calendar month's held months, summed over the twelve
 * calendar months, so a window that is not a whole number of years does not count one season more than another.
 * Null unless every calendar month has a held month. */
export function averageYear(ms: Month[], s: Stream): number | null {
  let sum = 0;
  for (let k = 1; k <= 12; k++) {
    const xs = ms.filter((r) => r.held && Number(r.m.slice(5, 7)) === k).map((r) => pick(r, s)).filter((v): v is number => v !== null);
    if (!xs.length) return null;
    sum += xs.reduce((a, v) => a + v, 0) / xs.length;
  }
  return sum;
}

const prevMonth = (m: string, k: number) => new Date(Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)) - 1 - k, 1)).toISOString().slice(0, 7);

/** The last twelve months: the newest held month whose eleven months before it are all held. Null if there is none. */
export function lastTwelve(ms: Month[]): Month[] | null {
  const by = new Map(ms.map((r) => [r.m, r]));
  for (const r of [...ms].reverse()) {
    if (!r.held) continue;
    const twelve = Array.from({ length: 12 }, (_, k) => by.get(prevMonth(r.m, k)));
    if (twelve.every((t) => t && t.held)) return (twelve as Month[]).reverse();
  }
  return null;
}
export const sumOf = (ms: Month[], s: Stream) => ms.reduce((a, r) => a + (pick(r, s) ?? 0), 0);

/** The 10th-percentile month of the held months by total revenue (nearest rank): one month in ten earned that or less. */
export function badMonth(ms: Month[]): Month | null {
  const sorted = ms.filter((r) => r.held).sort((a, b) => a.total! - b.total! || a.m.localeCompare(b.m));
  return sorted.length ? sorted[Math.max(0, Math.ceil(0.1 * sorted.length) - 1)] : null;
}

/** The one month that carries the window: the held month with the highest total, when it alone is more than a quarter
 * of everything the held months earned (ERCOT's February 2021, Winter Storm Uri; session 71's rule). The income table
 * then gives the average of every year held without it, beside the average with it, so a reader is not misled by one
 * storm. Nothing is removed from the data: the month stays in every other figure and on the chart. Null when no month
 * weighs that much. */
export function outlier(ms: Month[]): { m: string; share: number; averageWithout: number | null } | null {
  const held = ms.filter((r) => r.held);
  const sum = held.reduce((a, r) => a + r.total!, 0);
  if (held.length < 12 || sum <= 0) return null;
  const top = held.reduce((a, r) => (r.total! > a.total! ? r : a));
  const share = top.total! / sum;
  if (share <= 0.25) return null;
  return { m: top.m, share: share * 100, averageWithout: averageYear(ms.filter((r) => r.m !== top.m), "total") };
}
/** The average of every year held without the outlier month, one stream, per MW (null when there is no outlier). */
export function averageWithout(ms: Month[], s: Stream): number | null {
  const o = outlier(ms);
  return o ? averageYear(ms.filter((r) => r.m !== o.m), s) : null;
}

/** Session 71: the last 36 months, the window of the page's bad month: the 36 calendar months ending with the last
 * twelve months' last month (else the newest held month), and the held months in it. A market held for less than 36
 * months gives fewer; the page says how many. */
export function last36(ms: Month[]): { from: string; to: string; months: Month[] } | null {
  const held = ms.filter((r) => r.held);
  if (!held.length) return null;
  const to = (lastTwelve(ms)?.[11] ?? held.at(-1)!).m;
  const from = prevMonth(to, 35);
  return { from, to, months: held.filter((r) => r.m >= from && r.m <= to) };
}

/** Session 71: the last three full calendar years: the newest calendar year with all twelve months held, and the two
 * before it, each also complete. Null when three such years are not held (CAISO, held from September 2024). */
export function lastThreeYears(ms: Month[]): string[] | null {
  const full = years(ms).filter((y) => y.complete).map((y) => y.y);
  const newest = full.at(-1);
  if (!newest) return null;
  const want = [0, 1, 2].map((k) => String(Number(newest) - k)).reverse();
  return want.every((y) => full.includes(y)) ? want : null;
}
/** The average of the last three full calendar years, one stream, per MW: their months' sum over three. */
export function threeYearAverage(ms: Month[], s: Stream): number | null {
  const ys = lastThreeYears(ms);
  if (!ys) return null;
  return ms.filter((r) => r.held && ys.includes(r.m.slice(0, 4))).reduce((a, r) => a + (pick(r, s) ?? 0), 0) / 3;
}

export type Year = { y: string; months: number; complete: boolean; energy: number; ancillary: number };
/** Revenue by calendar year per MW, the held months only; a year is complete when all twelve of its months are held. */
export function years(ms: Month[]): Year[] {
  const out = new Map<string, Year>();
  for (const r of ms) {
    if (!r.held) continue;
    const y = r.m.slice(0, 4);
    if (!out.has(y)) out.set(y, { y, months: 0, complete: false, energy: 0, ancillary: 0 });
    const t = out.get(y)!;
    t.months++; t.energy += r.energy!; t.ancillary += r.ancillary!;
  }
  return [...out.values()].map((t) => ({ ...t, complete: t.months === 12 })).sort((a, b) => a.y.localeCompare(b.y));
}

/** Debt coverage over the last twelve months: the twelve months' revenue for the reader's size, less a year of fixed
 * O&M, over the annual debt payments. `market` is the twelve months' revenue per MW. */
export function coverage(marketPerMw: number, x: Pick<Inputs, "mw" | "fom" | "ds">): number | null {
  return x.ds > 0 ? (marketPerMw * x.mw - x.fom * 1000 * x.mw) / x.ds : null;
}

export type Contract = { share: number; price: number; end: string };  // percent, USD/kW-month, YYYY-MM
/** The contract panel's results, computed in the browser. The contracted share of the battery is paid the contract
 * price per kW-month and earns nothing from the market; the rest earns the market's revenue. */
export function contractResult(ms: Month[], x: Inputs, c: Contract) {
  const s = Math.min(100, Math.max(0, c.share)) / 100;
  const contracted = s * x.mw * 1000 * c.price * 12;
  const avg = averageYear(ms, "total");
  const l12 = lastTwelve(ms);
  const market12 = l12 ? sumOf(l12, "total") : null;
  // session 71: the market lines lead with the last twelve months; the average of every year held is shown beside them
  return {
    contracted,
    market12: market12 === null ? null : (1 - s) * market12 * x.mw,
    marketAverage: avg === null ? null : (1 - s) * avg * x.mw,
    coverageWith: market12 === null || x.ds <= 0 ? null : (contracted + (1 - s) * market12 * x.mw - x.fom * 1000 * x.mw) / x.ds,
    coverageWithout: market12 === null ? null : coverage(market12, x),
    after12: market12 === null ? null : market12 * x.mw,
    afterAverage: avg === null ? null : avg * x.mw,
    first: l12 ? l12[0].m : null,
    last: l12 ? l12[11].m : null,
  };
}

export type StressRow = { variable: string; ts_utc: string; value: number; event: string };
export const EVENTS: Record<string, string> = { uri_2021: "Winter Storm Uri, February 2021", elliott_2022: "Winter Storm Elliott, December 2022", ercot_heat_2023: "The summer 2023 heat" };
/** Each stress event's held days for one strategy and duration, per MW: the window's revenue by stream and its best day. */
export function stress(rows: StressRow[], strat: Strategy, dur: Duration) {
  const pre = `${strat}_${dur}h_revenue_`;
  const out: { event: string; days: number; first: string; last: string; energy: number; ancillary: number; total: number; best: { day: string; v: number } }[] = [];
  for (const event of Object.keys(EVENTS)) {
    const days = new Map<string, Record<string, number>>();
    for (const r of rows) {
      if (r.event !== event || !r.variable.startsWith(pre)) continue;
      const d = r.ts_utc.slice(0, 10);
      if (!days.has(d)) days.set(d, {});
      days.get(d)![r.variable.slice(pre.length).replace("_usd_per_mw", "")] = Number(r.value);
    }
    if (!days.size) continue;
    const list = [...days.entries()].sort((a, b) => a[0].localeCompare(b[0]));
    const sum = (k: string) => list.reduce((a, [, v]) => a + (v[k] ?? 0), 0);
    const best = list.reduce((a, [d, v]) => (v.total > a.v ? { day: d, v: v.total } : a), { day: list[0][0], v: list[0][1].total });
    out.push({ event, days: list.length, first: list[0][0], last: list.at(-1)![0], energy: sum("energy"), ancillary: sum("ancillary"), total: sum("total"), best });
  }
  return out;
}

/** One number for a check key's stat (bs|<inputs>|<stat>), for the reader's size: what the page shows and
 * check-values recomputes from its own read of the tables. */
export function stat(rows: Row[], stressRows: StressRow[], x: Inputs, what: string): number | null {
  const ms = monthsOf(rows, x.strat, x.dur);
  const [a, b, c] = what.split(":");
  const scaled = (v: number | null) => (v === null ? null : Math.round(v * x.mw));  // whole US dollars for the reader's size
  const l12 = lastTwelve(ms);
  switch (a) {
    case "avg": return scaled(averageYear(ms, b));
    case "avg_kw": return (() => { const v = averageYear(ms, b); return v === null ? null : v / 1000; })();
    case "share": { const t = averageYear(ms, "total"), v = averageYear(ms, b); return t === null || v === null || t === 0 ? null : Math.round((v / t) * 100); }
    case "l12": return l12 ? scaled(sumOf(l12, b)) : null;
    case "p10": return scaled(badMonth(ms)?.total ?? null);
    case "cover": return l12 ? coverage(sumOf(l12, "total"), x) : null;
    case "n": return ms.filter((r) => r.held).length;
    case "top_share": { const o = outlier(ms); return o ? Math.round(o.share) : null; }
    case "avg_without_top": return scaled(outlier(ms)?.averageWithout ?? null);
    // session 71: the last twelve months per kW and by share; the bad month of the last 36 months; the last three full
    // years; the average of every year held without the outlier month
    case "l12_kw": return l12 ? sumOf(l12, b) / 1000 : null;
    case "l12_share": { if (!l12) return null; const t = sumOf(l12, "total"); return t === 0 ? null : Math.round((sumOf(l12, b) / t) * 100); }
    case "p10_36": return scaled(badMonth(last36(ms)?.months ?? [])?.total ?? null);
    case "n36": { const w = last36(ms); return w ? w.months.length : null; }
    case "y3": return scaled(threeYearAverage(ms, b));
    case "y3_kw": { const v = threeYearAverage(ms, b); return v === null ? null : v / 1000; }
    case "avg_without": return scaled(averageWithout(ms, b));
    case "avg_without_kw": { const v = averageWithout(ms, b); return v === null ? null : v / 1000; }
    case "ds": return x.ds;
    case "year": { const y = years(ms).find((t) => t.y === b); return y ? (c === "energy" ? y.energy : c === "ancillary" ? y.ancillary : y.energy + y.ancillary) / 1000 : null; }
    case "month": { const r = ms.find((t) => t.m === b); return r ? scaled(pick(r, c)) : null; }
    case "days": { const r = ms.find((t) => t.m === b); return r ? (c === "out" ? r.daysOut : r.daysHeld) : null; }
    case "out": return ms.reduce((s, r) => s + r.daysOut, 0);
    case "stress": { const e = stress(stressRows, x.strat, x.dur).find((t) => t.event === b); return e ? scaled(c === "best" ? e.best.v : c === "energy" ? e.energy : c === "ancillary" ? e.ancillary : e.total) : null; }
    default: return null;
  }
}

/** US dollars, short, as scripts/check-values.mjs formats data-format usd. */
export function usdShort(v: number): string {
  const t = (x: number) => x.toLocaleString("en-US", { maximumFractionDigits: 2 });
  if (Math.abs(v) >= 1e9) return `${t(v / 1e9)} billion`;
  if (Math.abs(v) >= 1e6) return `${t(v / 1e6)} million`;
  return v.toLocaleString("en-US");
}
export const monthName = (m: string) => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });

/** Each product's required duration (the stored energy an upward reserve must have behind it), as
 * warehouse/derived/battery_stack.py applies it, with its source. "Assumed" marks a requirement that could not be
 * checked against the market operator's own document in session 67: one hour is used. */
export const REQUIREMENTS: Record<string, { product: string; rule: string; source: string; assumed: boolean }[]> = {
  ercot: [
    { product: "Regulation Up, Regulation Down, Responsive Reserve", rule: "30 minutes from 5 December 2025", source: "ERCOT NPRR 1282", assumed: false },
    { product: "Regulation Up, Regulation Down, Responsive Reserve", rule: "1 hour before 5 December 2025", source: "assumed", assumed: true },
    { product: "ECRS", rule: "2 hours from its start in June 2023; 1 hour from 5 December 2025", source: "ERCOT NPRR 1096 and NPRR 1282", assumed: false },
    { product: "Non-Spin", rule: "4 hours from 9 December 2022", source: "ERCOT NPRR 1096", assumed: false },
    { product: "Non-Spin", rule: "1 hour before 9 December 2022", source: "assumed", assumed: true },
  ],
  caiso: [
    { product: "Regulation Up, Regulation Down", rule: "1 hour in the day-ahead market", source: "CAISO tariff, section 8.4.1.1(g)", assumed: false },
    { product: "Spinning Reserve, Non-Spinning Reserve", rule: "30 minutes", source: "CAISO tariff, section 8.4.3", assumed: false },
  ],
  // session 86 assumed one hour for both. Session 100 read the operators' own documents (docs/methods/
  // reserve_quantities_nyiso_spp.md): SPP's protocols state 60 minutes for all four products; NYISO's tariff states one
  // hour for operating reserves from storage and no time for regulation, which stays an assumption (session 102).
  nyiso: [
    { product: "10-Minute Spinning Reserve", rule: "1 hour", source: "NYISO Market Administration and Control Area Services Tariff, section 4.4.2.1, effective 16 September 2026", assumed: false },
    { product: "Regulation Capacity", rule: "1 hour", source: "the tariff states no time (Rate Schedule 3, section 15.3.2.1(e), lets NYISO reduce a storage resource's regulation capacity for its energy level), so one hour is used", assumed: true },
  ],
  spp: [
    { product: "Regulation Up, Regulation Down, Spinning Reserve, Supplemental Reserve", rule: "60 minutes", source: "SPP Integrated Marketplace Protocols, Revision 119, section 4.2.2", assumed: false },
  ],
};
/** Session 102: how long a reserve must be backed on a grid in review, in words (session 100's verified rules). */
export const DURATION_WORDS: Record<string, string> = {
  nyiso: "How long a reserve must be backed is NYISO's own rule for spinning reserve, one hour (its tariff, section 4.4.2.1). For regulation the tariff states no time, so one hour is assumed; a shorter requirement would raise these numbers and a longer one lower them.",
  spp: "How long a reserve must be backed is SPP's own rule, 60 minutes for each of the four products (Integrated Marketplace Protocols, Revision 119, section 4.2.2).",
};
/** Session 86: what the model leaves out on a grid in review, in words. */
export const LEFT_OUT: Record<string, string> = {
  nyiso: "NYISO's 10-minute non-synchronous and 30-minute reserves are left out: in every hour held, 10-minute spinning reserve paid at least as much for the same megawatt. Regulation is one product in New York, up and down together, so an award takes the battery's power in both directions",
  spp: "SPP's ramp capability and uncertainty products are left out: what a battery must hold behind them was not read",
};

// Session 178: the model's day-ahead ancillary revenue beside what ERCOT's storage resources were really awarded, over
// the months both hold whole, in USD per kW of power and month. The page reads it from data/battery_awards_beside.json
// (warehouse/derived/battery_awards_compare.py --snapshot), never from the live set: one line, ERCOT only.
// docs/methods/battery_earns_algorithm.md, "Beside ERCOT's real awards", has the caveats.
export type AwardsCase = { first: string; last: string; months: number; model: number; fleet: number; ratio: number };
export type AwardsSnapshot = { built: string; cases: Record<string, AwardsCase> };
/** The comparison for one strategy and duration, or null when the snapshot holds none (or the grid is not ERCOT). */
export function awardsBeside(snap: AwardsSnapshot, grid: string, strat: Strategy, dur: Duration): AwardsCase | null {
  if (grid !== "ercot") return null;
  const c = snap?.cases?.[`${strat}_${dur}h`];
  const ok = c && [c.months, c.model, c.fleet, c.ratio].every((v) => typeof v === "number" && Number.isFinite(v)) && c.months > 0 && c.fleet > 0;
  return ok ? c : null;
}
/** One number of a check key bsa|<strategy>_<N>h|<model, fleet, ratio or months>, from the snapshot. */
export function awardsStat(snap: AwardsSnapshot, k: string, what: string): number | null {
  const hit = /^(foresight|dayahead)_(2|4|8)h$/.exec(k);
  const c = hit ? awardsBeside(snap, "ercot", hit[1] as Strategy, Number(hit[2]) as Duration) : null;
  return c && ["model", "fleet", "ratio", "months"].includes(what) ? (c as unknown as Record<string, number>)[what] : null;
}
