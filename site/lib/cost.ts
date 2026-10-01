// Session 37: the cost-of-power calculator's arithmetic (docs/methods/cost_of_power.md), shared by the page (the
// defaults, rendered on the server and checked) and the calculator (the reader's own inputs, in the browser).
// scripts/check-values.mjs recomputes the defaults on its own, without this file.

export type Cell = { month: string; hour: number; price: number; hours: number };
export type Hub = { entity: string; iso: string; flat: number | null; cheap80: number | null; months: string[]; hoursHeld: number };

export const DEFAULTS = { mw: 100, loadFactor: 0.9, days: 90, share: 0.8 };
export const PERIODS = { month: 30, year: 365 } as const;

type Row = { entity: string; variable: string; ts_utc: string; value: number };

/** The last 12 months with real-time hours, newest first, and the flat-load price over them: the simple means
 * weighted by the hours held (the mean price of every hour held). */
export function flatPrice(monthly: Row[], entity: string, only?: string[]): { price: number | null; months: string[]; hours: number } {
  const hours = new Map<string, number>(), mean = new Map<string, number>();
  for (const r of monthly) {
    if (r.entity !== entity) continue;
    const m = r.ts_utc.slice(0, 7);
    if (r.variable === "rt_hours") hours.set(m, r.value);
    if (r.variable === "rt_simple_mean") mean.set(m, r.value);
  }
  // session 49: `only`, the months to use (the page passes the latest complete month every ISO holds); else the latest 12
  const months = [...hours.keys()].filter((m) => mean.has(m) && (!only || only.includes(m))).sort().reverse().slice(0, 12);
  let num = 0, den = 0;
  for (const m of months) {
    num += (mean.get(m) as number) * (hours.get(m) as number);
    den += hours.get(m) as number;
  }
  return { price: den ? num / den : null, months, hours: den };
}

/** The (month, hour of day) cells of the hourly profile. */
export function cells(profile: Row[], entity: string): Cell[] {
  const price = new Map<string, number>(), n = new Map<string, number>();
  for (const r of profile) {
    if (r.entity !== entity) continue;
    const m = /^rt_(mean|days)_h(\d\d)$/.exec(r.variable);
    if (!m) continue;
    const k = `${r.ts_utc.slice(0, 7)}|${m[2]}`;
    (m[1] === "mean" ? price : n).set(k, r.value);
  }
  return [...price.keys()].filter((k) => n.has(k)).map((k) => {
    const [month, h] = k.split("|");
    return { month, hour: Number(h), price: price.get(k) as number, hours: n.get(k) as number };
  });
}

/** The mean price of the cheapest `share` of hours: cells ranked by price (then month, then hour), taken by their
 * hours until they hold `share` of all hours, the last one in part. */
export function cheapPrice(cs: Cell[], share = DEFAULTS.share): number | null {
  const total = cs.reduce((a, c) => a + c.hours, 0);
  if (!total) return null;
  const sorted = [...cs].sort((a, b) => a.price - b.price || a.month.localeCompare(b.month) || a.hour - b.hour);
  const target = share * total;
  let left = target, cost = 0;
  for (const c of sorted) {
    if (left <= 0) break;
    const take = Math.min(c.hours, left);
    cost += c.price * take;
    left -= take;
  }
  return cost / target;
}

/** MWh drawn: MW x load factor x 24 x days, times the share of hours run. */
export const energy = (mw: number, lf: number, days: number, share = 1) => mw * lf * 24 * days * share;
