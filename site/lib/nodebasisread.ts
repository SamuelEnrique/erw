// Energy Research Warehouse (ERW) site, session 355: the read of ERCOT's storage nodes against the hub for the battery
// page (node_basis_summary, the data machine's session 358), server only, kept out of the page as the price years'
// read is (lib/priceyearsread.ts): the page's own reads stay read.ts's. Every row of the storage class for the months
// asked; the page keeps a month only when all six figures are held.
import { HOURLY, attempt, rest } from "@/lib/supabase";

export const STORAGE_VARS = ["spread_4h_p10", "spread_4h_p50", "spread_4h_p90", "hub_spread_4h", "share_wider_pct", "days"] as const;
export type StorageVar = (typeof STORAGE_VARS)[number];

export function storageRows() {
  return attempt(() => rest<{ variable: string; ts_utc: string; value: number }>("series", { select: "variable,ts_utc,value", table_name: "eq.node_basis_summary", entity: "eq.ercot:HB_HUBAVG",
    variable: `in.(${STORAGE_VARS.map((v) => `dam_storage_${v}`).join(",")})`, order: "ts_utc" }, HOURLY));
}
