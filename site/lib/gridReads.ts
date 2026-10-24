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
//
// Session 1179 (chain 091, "one read of a grid's generation a page"): the Mix tab read the grid's eia930_all_generation
// four times, each for its own window, every variable: 45 days (lib/grid.ts load, for the grid's own blocks), 34 days
// (latestHour above, the Now view's mix), 10 days (components/grid/Conditions.tsx loadConditions, "Yesterday" and the
// grid's row of "Generation mix, as a table") and 9 days (components/grid/MixView.tsx, the energy mix's hourly panel).
// Now the render reads it once, at the widest window: shareGeneration(entity, since) starts the read and keeps it for
// the render (React's `cache`, one Map a request, as lib/reliability.ts keeps CAISO's notices), and each reader takes
// its own days from it with the start it computed before (generationSince: the rows at or after its own daysAgo(n),
// in the read's order, which is what the same read from that start returns; latestHour: the newest total at or after
// its start, then the rows from that hour on, as its two requests gave). A reader whose entity was not shared, or
// whose start is before the shared one, reads as it did. The grid's own reads share 45 days (lib/grid.ts load, the
// grid tabs of the seven ISO grids); the Lower 48's Mix tab shares 10 days (app/grid/page.tsx), its widest whole read
// (its Now view's 34 days stay latestHour's two small requests). scripts/test-grid-generation.mjs holds the slices to
// the reads they replace on real rows.
import "server-only";
import { cache } from "react";
import { series, type SeriesRow } from "@/lib/data";
import { HOURLY, rest } from "@/lib/supabase";

/** Session 1179: the table read once a render. */
export const GENERATION = "eia930_all_generation";

type Shared = { since: string; rows: Promise<SeriesRow[]> };
/** The render's shared reads of GENERATION, by entity (React's `cache`: one Map a request). */
const sharedReads = cache((): Map<string, Shared> => new Map());
const covers = (w: Shared | undefined, since: string): w is Shared => !!w && Date.parse(w.since) <= Date.parse(since);

/** The rows at or after `since`, in their order: what the same read from `since` returns, out of a read that began at
 *  or before it. */
export function rowsSince(rows: SeriesRow[], since: string): SeriesRow[] {
  const t = Date.parse(since);
  return rows.filter((r) => Date.parse(r.ts_utc) >= t);
}

/** What latestHour's two requests return, out of rows that hold its window whole: the newest row of `variable` at or
 *  after `since`, then every row from its hour on, in their order. No such row: none. */
export function latestHourOf(rows: SeriesRow[], variable: string, since: string): SeriesRow[] {
  const t = Date.parse(since);
  let top = -Infinity;
  for (const r of rows) {
    const x = Date.parse(r.ts_utc);
    if (r.variable === variable && x >= t && x > top) top = x;
  }
  return top === -Infinity ? [] : rows.filter((r) => Date.parse(r.ts_utc) >= top);
}

/** Read `entity`'s generation from `since` once for this render, for every reader after (the first share of an entity
 *  holds; a later one reads nothing). Nothing is returned: a reader asks generationSince. */
export function shareGeneration(entity: string, since: string): void {
  const reads = sharedReads();
  if (reads.has(entity)) return;
  const rows = series(GENERATION, { entity, since });
  rows.catch(() => undefined);   // a failed read is the readers' to say (each awaits it); not one left unhandled here
  reads.set(entity, { since, rows });
}

/** series(GENERATION, { entity, since }): out of the render's shared read when it began at or before `since`, else
 *  read as before. A failed shared read fails each reader with its error. */
export async function generationSince(entity: string, since: string): Promise<SeriesRow[]> {
  const w = sharedReads().get(entity);
  return covers(w, since) ? rowsSince(await w.rows, since) : series(GENERATION, { entity, since });
}

/** The newest row of `variable` for `entity` at or after `since`, and every row of the entity from its hour on, in the
 *  key's order: what series(table, { entity, since }) returns for that hour and after. No row: none in the window. */
export async function latestHour(table: string, entity: string, variable: string, since: string): Promise<SeriesRow[]> {
  // session 1179: out of the render's shared read of the grid's generation when it holds the window whole
  const w = table === GENERATION ? sharedReads().get(entity) : undefined;
  if (covers(w, since)) return latestHourOf(await w.rows, variable, since);
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
