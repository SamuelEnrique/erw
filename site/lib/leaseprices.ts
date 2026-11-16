// Session 49: the lease tool's default prices, shared by /severance/lease and /severance/lease/real (moved here from
// the lease page, unchanged): the monthly means of the warehouse's EIA daily spot prices since 2023.
import { series } from "@/lib/data";
import type { PricePoint } from "@/lib/lease";

const T = "eia_fuel_spot_prices";
const SINCE = "2023-01-01T00:00:00Z";

/** The mean of each calendar month of an EIA daily spot series since 2023; the latest month is labeled as partial. */
export async function monthMeans(entity: string, name: string, unit: string, per: string): Promise<Record<string, PricePoint>> {
  const rows = await series(T, { entity, variable: "spot_price", since: SINCE });
  const by = new Map<string, number[]>();
  for (const r of rows) {
    const m = r.ts_utc.slice(0, 7);
    if (!by.has(m)) by.set(m, []);
    by.get(m)!.push(r.value);
  }
  const months = [...by.keys()].sort();
  const last = months[months.length - 1];
  const out: Record<string, PricePoint> = {};
  for (const m of months) {
    const xs = by.get(m)!;
    const value = Math.round((xs.reduce((a, b) => a + b, 0) / xs.length) * 100) / 100;
    out[m] = {
      value, n: xs.length,
      label: `${name}, the mean of ${xs.length} daily EIA spot prices in ${m}${m === last ? " (the latest month held, possibly partial)" : ""}, $${value.toFixed(2)} ${unit}${per}`,
    };
  }
  return out;
}

/** Session 7502 (chain 304): the first instant the calculator's default price asks the table from: the first day (UTC)
 * of the month three months before the month of `now`. A month boundary, so every month read is read whole. */
export function latestMonthSince(now: number = Date.now()): string {
  const d = new Date(now);
  return new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() - 3, 1)).toISOString().slice(0, 10) + "T00:00:00Z";
}

/** The calculator's default price (moved here from app/severance/page.tsx in session 7502, so a script can run it): the
 * mean of the latest complete calendar month of an EIA daily spot series. A month is complete once a later month's
 * first day is held. Until session 7502 the rows were asked for from 75 days before now: when the table ran more than
 * about two weeks behind, the "complete" month began mid-month and its mean left out the month's first days
 * (docs/reviews/severance-faults-2026-11-16.md, row 1). Now the read begins on a month's first day. Null when no
 * complete month is held in the three months before this one: the page then says "not held: enter a price". */
export async function latestMonthMean(entity: string, now: number = Date.now()): Promise<{ value: number; month: string; n: number } | null> {
  const rows = await series(T, { entity, variable: "spot_price", since: latestMonthSince(now) });
  if (!rows.length) return null;
  const last = rows.map((r) => r.ts_utc.slice(0, 7)).sort().pop()!;
  const months = [...new Set(rows.map((r) => r.ts_utc.slice(0, 7)))].sort().filter((m) => m < last);
  const m = months.pop();
  if (!m) return null;
  const xs = rows.filter((r) => r.ts_utc.startsWith(m)).map((r) => r.value);
  return { value: Math.round((xs.reduce((a, b) => a + b, 0) / xs.length) * 100) / 100, month: m, n: xs.length };
}
