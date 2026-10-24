// Energy Research Warehouse (ERW) site, session 1167 (chain 078): the Grid tool's held grids, where a block draws rows
// that do not pass through lib/supabase.ts's hold. The standing rule (lib/license.ts, the owner's ruling of 12 October
// 2026, chain 077's rules: "no held grid's rows are drawn"): a table held by grid shows "license needed" in place of a
// held grid's figures. Reads of the live set are held there already; three places of the tool drew held rows all the
// same, and each now asks here:
//   - the committed files and the replay's files, which no read of the live set filters: the network's hub prices by
//     day and in the stories (public/network/*.json, warehouse/derived/network_daily.py and network_stories.py, from
//     iso_hub_prices_history among others) and the energy mix's hub price by hour (data/mixplus, mix_views.py, from
//     iso_hub_prices_history for every grid but ERCOT);
//   - the queue's positions of energy_projects, read by entity_id (lib/grid.ts), which the live set's filter by
//     `entity` let through: ISO-NE's rows reached the page.
// Pure: the day is an argument, as in lib/license.ts, so a node test runs it on fixed days.
import { LICENSE_NEEDED, licenseHeldRow, licenseTitle } from "@/lib/license";

/** The table the replay's and the mix files' hub prices are of, for the grids other than ERCOT. */
export const HUB_PRICE_TABLE = "iso_hub_prices_history";
/** The table the Grid tool's queue block reads. */
export const QUEUE_TABLE = "energy_projects";

/** The network's balancing authority codes of the seven ISO grids, and each one's grid. */
export const BA_GRID: Record<string, string> = { CISO: "caiso", ERCO: "ercot", ISNE: "isone", MISO: "miso", NYIS: "nyiso", PJM: "pjm", SWPP: "spp" };

export type Held = { words: string; why: string };
const held = (table: string): Held => ({ words: LICENSE_NEEDED, why: licenseTitle(table) });

/** A grid's hub price held for a license on the day, by the grid's slug ("isone"), or null. */
export function heldGridPrice(slug: string, now: Date = new Date()): Held | null {
  return licenseHeldRow(HUB_PRICE_TABLE, `iso:${slug}`, now) ? held(HUB_PRICE_TABLE) : null;
}

/** A balancing authority's hub price held for a license on the day, by its network code ("ISNE"), or null. A code of
 *  no ISO grid is never held here (it has no hub price in the files). */
export function heldHubPrice(ba: string, now: Date = new Date()): Held | null {
  const g = BA_GRID[ba];
  return g ? heldGridPrice(g, now) : null;
}

/** Session 1403 (chain 100): the table the Clean tab's live week reads (components/grid/CleanWeekPanel.tsx). */
export const CARBON_HOURLY_TABLE = "carbon_intensity_hourly";

/** A grid's hourly carbon intensity held for a license on the day, by the grid's slug ("isone"), or null. The table is
 *  public in every status file today (site/data/license_status.json), so no grid is held; a grid that becomes held reads
 *  "license needed" and its rows are not read. A slug of no ISO grid (the Lower 48) is held as the table whole is. */
export function heldCarbon(slug: string, now: Date = new Date()): Held | null {
  const ba = Object.keys(BA_GRID).find((k) => BA_GRID[k] === slug);
  return licenseHeldRow(CARBON_HOURLY_TABLE, ba ? `eia930:${ba}` : undefined, now) ? held(CARBON_HOURLY_TABLE) : null;
}

/** The queue's positions of energy_projects a page may draw: a held grid's are left out ("isone_queue:137" is ISO-NE's). */
export function shownQueue<T extends { entity_id: string }>(rows: T[], now: Date = new Date()): T[] {
  return rows.filter((r) => !licenseHeldRow(QUEUE_TABLE, r.entity_id, now));
}

/** A grid's queue block held for a license on the day, by its queue table ("isone_interconnection_queue"), or null. */
export function heldQueue(queueTable: string | null | undefined, now: Date = new Date()): Held | null {
  if (!queueTable) return null;
  const prefix = queueTable.replace(/_interconnection_queue$/, "_queue");
  return licenseHeldRow(QUEUE_TABLE, `${prefix}:x`, now) ? held(QUEUE_TABLE) : null;
}
