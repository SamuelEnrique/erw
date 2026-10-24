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
import { DataError, HOURLY, markFailedRead, rest } from "@/lib/supabase";
import { fetchHourly } from "@/lib/network";  // session 1180

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

// Session 1180 (chain 091, "the storage units and the snapshot, read once"):
//
// gridStorageUnits: the Mix and Clean tabs of an ISO grid drew the battery units of its footprint (components/grid/
// YourGrid.tsx Batteries: sums of MW by status and of MWh) out of lib/data.ts storageUnits, the whole of
// storage_capacity (1,627 units, two requests, seven columns), kept by lib/grid.ts load for the units whose ISO is the
// grid's. Now the read asks PostgREST for the grid's units only (extra->>iso=eq.<ISO>, the filter the chat's tools use
// on the same table) and for the three columns drawn: capacity_mw, status and the MWh. The rows come in the order of the
// whole read (entity_id), so each sum adds the same numbers in the same order. storageUnits is unchanged for the pages
// that draw the whole fleet (/storage, the home page, the battery game).
//
// freshSnapshot: the Gravity tab drew the network's hourly snapshot (lib/network.ts fetchHourly) twice a render, once
// with a one-hour revalidation for the network component and its panel grid_gravity_<grid> (components/grid/
// NetworkView.tsx) and once fresh for the Exchange blocks under it (components/grid/ExchangeView.tsx, session 237: a
// number shown must be the object's own, which check-values reads fresh). The fresh read is kept, the reason for it
// holds; it does not need a second, older read beside it. Now the render reads it fresh once (React's `cache`), and
// both draw that one object; the Network tab keeps its hourly read, the Now tab its own fresh one.

/** Session 1180: what the grid's own blocks draw of a battery unit of storage_capacity. */
export type GridUnit = { capacity_mw: number | null; status: string | null; mwh: string | null };

/** Session 1180: the query of a grid's battery units: its ISO's units only, the columns drawn, the whole read's order. */
export function gridUnitsQuery(iso: string): Record<string, string> {
  return { select: "capacity_mw,status,mwh:extra->>energy_capacity_mwh", table_name: "eq.storage_capacity", "extra->>iso": `eq.${iso}`, order: "entity_id" };
}

/** Session 1180: the battery units of storage_capacity whose ISO is `iso` (EIA-860M's balancing authority, mapped). */
export async function gridStorageUnits(iso: string): Promise<GridUnit[]> {
  return rest<GridUnit>("entities", gridUnitsQuery(iso), HOURLY, 20_000);
}

/** Session 1180: the network's hourly snapshot, read fresh (lib/network.ts fetchHourly(0)), once a render. */
export const freshSnapshot = cache((): Promise<unknown> => fetchHourly(0));

// ------------------------------------------------------------------ session 1181 (chain 091): a whole table answering no row
/** A read of a whole table that always holds rows (CAISO's and ERCOT's notices: every row of each, no window), whose empty
 *  answer is a failed read, not "no notice": it throws a DataError with the reason, after asking the page for a short
 *  revalidation as a failed read does (lib/supabase.ts markFailedRead, session 537), so every reader of the render says it
 *  could not be read and none draws "0 days" or "no alert today" from nothing. A read of a window (the scorecard's, the
 *  heat event page's) can hold no row and does not come here. */
export async function wholeTable<T>(table: string, holds: string, read: () => Promise<T[]>): Promise<T[]> {
  const rows = await read();
  if (rows.length) return rows;
  const e = new DataError(`Supabase events: ${table} answered no row for the whole table, which holds ${holds}: read as a failed read`);
  await markFailedRead(e);
  throw e;
}

/** The same rule over a read already made through attempt() (lib/supabase.ts): an answer of no row becomes a failed read
 *  with its reason, and the page is asked for a short revalidation; a read that failed, a read with rows and a read not
 *  made (null) are handed back as they came. For CAISO's notices (lib/reliability.ts gridNotices(), one request a render,
 *  read as session 1160 left it, so its other readers, the scorecard and the heat event page, are as they were). */
export async function wholeRead<T>(table: string, holds: string, read: Promise<{ ok: true; data: T[] } | { ok: false; reason: string } | null>): Promise<{ ok: true; data: T[] } | { ok: false; reason: string } | null> {
  const r = await read;
  if (!r || !r.ok || r.data.length) return r;
  const e = new DataError(`Supabase events: ${table} answered no row for the whole table, which holds ${holds}: read as a failed read`);
  await markFailedRead(e);
  return { ok: false, reason: e.message };
}

/** Session 1411: wholeRead's rule for a series of a table that holds a row every day (caiso_reliability_daily's peak demand,
 *  every Pacific day since 2018): an answer of no row is a failed read, said with the series endpoint, and the page is
 *  asked for a short revalidation; a read that failed and a read with rows are handed back as they came. */
export async function wholeSeriesRead<T>(table: string, holds: string, read: Promise<{ ok: true; data: T[] } | { ok: false; reason: string }>): Promise<{ ok: true; data: T[] } | { ok: false; reason: string }> {
  const r = await read;
  if (!r.ok || r.data.length) return r;
  const e = new DataError(`Supabase series: ${table} answered no row, and it holds ${holds}: read as a failed read`);
  await markFailedRead(e);
  return { ok: false, reason: e.message };
}

/** What caiso_grid_emergencies always holds, for the reason of an empty answer. */
export const CAISO_HOLDS = "every notice since 1998";
