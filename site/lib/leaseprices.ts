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
