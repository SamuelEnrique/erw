// Energy Research Warehouse (ERW) site, session 1160 (chain 077, "the reads"): smaller reads for the Grid tool that
// give a page the rows it drew before, and no others it drew nothing from.
//
// latestHour: the Now view's mix (components/grid/NowView.tsx) is the newest hour of eia930_all_generation that holds
// the grid's net generation, and that hour's fuels. Until this session it was found in a read of the grid's last 34
// days, every variable (about 8,000 rows and 8 requests for one grid, 13,000 rows and 14 requests for the Lower 48),
// of which one hour was drawn. Now: the newest row of the total in the same window (one row, the primary key read
// backwards), then the grid's rows from that hour on. The rows drawn are the same rows: the newest total in the window
// is the only total in the second read, so its hour and its fuels are the ones the 34-day read gave (session 1160's
// node test, scripts/test-grid-reads.mjs, holds the two equal on real rows). An empty window gives no rows, as before.
import "server-only";
import { series, type SeriesRow } from "@/lib/data";
import { HOURLY, rest } from "@/lib/supabase";

/** The newest row of `variable` for `entity` at or after `since`, and every row of the entity from its hour on, in the
 *  key's order: what series(table, { entity, since }) returns for that hour and after. No row: none in the window. */
export async function latestHour(table: string, entity: string, variable: string, since: string): Promise<SeriesRow[]> {
  const top = await rest<SeriesRow>("series", {
    select: "entity,variable,ts_utc,value,unit,freq",
    table_name: `eq.${table}`,
    entity: `eq.${entity}`,
    variable: `eq.${variable}`,
    ts_utc: `gte.${since}`,
    order: "ts_utc.desc",
  }, HOURLY, 1);
  if (!top.length) return [];
  return series(table, { entity, since: top[0].ts_utc });
}
