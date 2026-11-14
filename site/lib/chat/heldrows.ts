// Energy Research Warehouse (ERW) site, session 5260 (chain 238): the hold by grid for a table of things, in the
// chat's tools. warehouse/chat/license_hold.py and warehouse/chat/tools.py hold the same rules.
//
// The platform set's pj08 (docs/reviews/ask-eval-2026-11-13.md, "The second class"): asked how many MW are active in
// ISO New England's interconnection queue, the chat read isone_interconnection_queue, a table the license file holds,
// and answered with the figure. The cause: a table held by grid is read, and the held grids' rows are left out row by
// row, by each row's `entity` (lib/supabase.ts restPaged). A table of things has no `entity`: its rows are named by
// `entity_id` ("isone_queue:1630"). So none of its rows was ever left out. Two rules, for the tools:
//
//   ownGrid    a table held by grid whose name begins with the prefix of a grid that decides it is that grid's own
//              table (isone_interconnection_queue, nyiso_dam_zone_prices): every row of it is held, so the tools refuse
//              it by name, in a table held whole's words, for a query, a description and a compare alike
//   keepRows   a table of things or of events that several grids share (energy_projects) is read without the rows whose
//              id is a held grid's, and without MISO's own (the pause); a read that matched only such rows is refused
//              with the hold's words, not answered "no rows match"
//
// A series table is not touched here: lib/supabase.ts leaves a held grid's rows out of it by their entity, as before.
import { LICENSE_NEEDED, gridPrefix, licenseByGrid, licenseHeldRow, licenseNeeded, licensePublishers, licenseTitle } from "@/lib/license";

/** MISO's own, by an id's or a table's head ("miso:INDIANA.HUB", "miso_queue:J1234"): as lib/chat/tools.ts misoOwn. */
export const misoOwnId = (v: unknown): boolean => typeof v === "string" && /^miso[:_]/i.test(v);

/** The held grid whose own table this is ("isone" for isone_interconnection_queue), or "" for a table several grids
 *  share, a table held whole, a table held by row, a table not held. */
export function ownGrid(table: string): string {
  if (!licenseNeeded(table) || !licenseByGrid(table)) return "";
  for (const p of licensePublishers(table)) {
    const g = gridPrefix(p);
    if (g && table.toLowerCase().startsWith(`${g}_`)) return g;
  }
  return "";
}

/** The id a row is its grid's by: a series row's entity, a thing's entity_id (read as `id`, or by its own name). */
export function rowId(r: Record<string, unknown>): string {
  for (const k of ["entity", "id", "entity_id"]) if (typeof r[k] === "string" && r[k]) return r[k] as string;
  return "";
}

/** The rows of a table of things or of events without the held grids' own and without MISO's own, and how many of each
 *  were left out. A series table's rows come back as they are. */
export function keepRows<T extends Record<string, unknown>>(table: string, shape: string, rows: T[]): { kept: T[]; held: number; paused: number } {
  if (shape === "series") return { kept: rows, held: 0, paused: 0 };
  const byGrid = licenseNeeded(table) && licenseByGrid(table);
  let held = 0, paused = 0;
  const kept = rows.filter((r) => {
    const id = rowId(r);
    if (misoOwnId(id)) { paused += 1; return false; }
    if (byGrid && licenseHeldRow(table, id)) { held += 1; return false; }
    return true;
  });
  return { kept, held, paused };
}

/** The refusal of a held grid's own table, by name: the words of a table held whole (lib/chat/tools.ts tableInfo). */
export function ownTableWords(table: string): string {
  return `table ${table} is ${LICENSE_NEEDED}: ${licenseTitle(table)}. State no figure of it: answer with not_in_warehouse true and say that it is "${LICENSE_NEEDED}"`;
}

/** The refusal of a read of a shared table that matched only a held grid's rows. */
export function heldRowsWords(table: string): string {
  return `the rows of ${table} that match are a held grid's own and are ${LICENSE_NEEDED}: ${licenseTitle(table)}. State no figure of them: answer with not_in_warehouse true and say that they are "${LICENSE_NEEDED}"`;
}
