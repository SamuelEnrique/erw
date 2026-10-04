// Energy Research Warehouse (ERW) site, session 93: the network page's reads, moved here from app/network/page.tsx
// unchanged, so that /network and /network/v3 (version 3, in review) read the same things the same way: the live week's
// demand, batteries and hub prices aligned to the snapshot's hours, and one ISO grid's rows of ba_supply_monthly.
import "server-only";
import { TABLE as SUPPLY_TABLE, type SupplyRow } from "@/lib/basupply";
import { MARKETS, series } from "@/lib/data";
import { HOURLY, attempt, rest } from "@/lib/supabase";
import type { LiveExtras, Snapshot } from "./Network";

export const ISO_BA: Record<string, string> = { CAISO: "CISO", ERCOT: "ERCO", "ISO-NE": "ISNE", MISO: "MISO", NYISO: "NYIS", PJM: "PJM", SPP: "SWPP" };
const SUPPLY_VARS = ["days_in_month", "days_held", "days_left_out", "thin_month", "share_days", "demand_mwh", "net_import_mwh", "net_import_share_pct",
  "net_import_pairs_mwh", "net_import_total_interchange_mwh", "net_import_balance_mwh", "net_import_pairs_share_pct", "net_import_total_interchange_share_pct",
  "net_import_balance_share_pct"];

/** Hourly means over the hours whose every interval is present, keyed by the hour's start (UTC, ISO). */
function hourly(rows: { ts_utc: string; value: number }[], perHour: number): Map<string, number> {
  const by = new Map<string, { s: number; n: number }>();
  for (const r of rows) {
    const h = new Date(Math.floor(new Date(r.ts_utc).getTime() / 3_600_000) * 3_600_000).toISOString().replace(".000Z", "Z");
    const a = by.get(h) ?? { s: 0, n: 0 };
    a.s += Number(r.value); a.n += 1; by.set(h, a);
  }
  return new Map([...by].filter(([, a]) => a.n === perHour).map(([h, a]) => [h, a.s / a.n]));
}

export async function liveExtras(snap: Snapshot): Promise<LiveExtras> {
  const since = snap.hours[0];
  const align = (m: Map<string, number>) => snap.hours.map((h) => (m.has(h) ? Math.round(m.get(h)! * 10) / 10 : null));
  const out: LiveExtras = { batteries: {}, batterySource: {}, prices: {}, priceKind: {}, demand: {} };
  const dem = await attempt(() => series("eia930_all_demand", { variable: "demand_mw", since }));
  if (dem.ok) {
    for (const ba of Object.values(ISO_BA)) {
      const rows = dem.data.filter((r) => r.entity === `eia930:${ba}`);
      if (rows.length) out.demand[ba] = align(hourly(rows, 1));
    }
  }
  const bat = await attempt(() => series("eia930_all_storage", { variable: "net_generation_battery_mw", since }));
  if (bat.ok) {
    for (const ba of ["ERCO", "ISNE", "MISO", "SWPP"]) {
      const rows = bat.data.filter((r) => r.entity === `eia930:${ba}`);
      if (rows.length) { out.batteries[ba] = align(hourly(rows, 1)); out.batterySource[ba] = "EIA-930"; }
    }
  }
  const ca = await attempt(() => series("caiso_battery_storage", { variable: "batteries_mw", since }));
  if (ca.ok && ca.data.length) { out.batteries.CISO = align(hourly(ca.data, 12)); out.batterySource.CISO = "CAISO's own data: CAISO reports no battery series to EIA-930"; }
  await Promise.all(MARKETS.map(async (m) => {
    const src = m.rt ?? m.da;
    const ba = ISO_BA[m.iso];
    if (!ba || !src) return;
    const r = await attempt(() => series(src.table, { entity: m.main, variable: src.variable, since }));
    if (!r.ok || !r.data.length) return;
    const per = src.freq === "PT15M" ? 4 : src.freq === "PT5M" ? 12 : 1;
    out.prices[ba] = align(hourly(r.data, per));
    out.priceKind[ba] = `${m.rt ? "real time" : "day-ahead: no real-time table in the live set"}, ${m.main.split(":")[1]}`;
  }));
  return out;
}

/** One ISO grid's rows of ba_supply_monthly (its own and its ties'): one small read each, so no read passes the anon
 * role's statement time limit. The shares need demand, which the warehouse holds for the seven ISO grids only. */
export async function supplyRows(ba: string): Promise<SupplyRow[]> {
  // a range on the key (eia930:CISO up to, not including, eia930:CISP) uses the table's index; a LIKE does not
  const hi = `eia930:${ba.slice(0, -1)}${String.fromCharCode(ba.charCodeAt(ba.length - 1) + 1)}`;
  return rest<SupplyRow>("series", { select: "entity,variable,ts_utc,value", table_name: `eq.${SUPPLY_TABLE}`, and: `(entity.gte.eia930:${ba},entity.lt.${hi})`,
    variable: `in.(${SUPPLY_VARS.join(",")})`, order: "entity,variable,ts_utc" }, HOURLY);
}
