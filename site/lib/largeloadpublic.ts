// Energy Research Warehouse (ERW) site: the large-load statements on a public document (session 272).
//
// The table large_load_public (warehouse/derived/large_load_public.py; docs/methods/large_load_public.md): one row a
// figure a public document states about large loads (megawatts, or a wait as written), with the entity, the ERW's class
// of the stage, the date, the document's title, page and link. Public by the owner's ruling of 14 October 2026: facts
// with a link and no quoted text. Do not sum across rows or entities: the entities count differently, a document often
// states a total and its parts, and an operator's figures hold its utilities'.
//
// The one read the datacenter page needs (the code machine wires the page). It reads the live set with the anon key
// through lib/supabase.ts, as every page's read does.
import "server-only";
import { HOURLY, rest } from "./supabase";

export const TABLE = "large_load_public";

/** A row as the page uses it. Numbers arrive as numbers or null; the columns kept in `extra` arrive as strings. */
export type LargeLoadStatement = {
  event_id: string;
  event_date: string;
  parties: string;            // the entity, as the statements table names it
  mw: number | null;          // megawatts (row_kind "mw")
  status: string;             // the stage, as the ERW classes it
  source_url: string;         // the document
  entity_group: string;
  entity_type: string;
  row_kind: "mw" | "wait" | string;
  mw_low: string;
  mw_high: string;
  duration_as_stated: string; // a wait (row_kind "wait"): the figure as written, a number and its unit with its bound
  wait_basis: string;         // measured, expected or a general statement
  wait_counted: string;       // whether the duration is a load's wait at all
  load_scope: string;
  stage_class: string;        // one of the ERW's five classes, or not classed: never the document's words
  document_title: string;
  document_type: string;
  page: string;
  event_date_basis: string;
  public_basis: string;       // SEC filing; public regulatory filing; publisher's terms read in session 205
  regulator: string;
  state: string;              // the regulator's state for a regulatory filing, else the states the entity serves
  grid: string;               // ercot, caiso, pjm, miso, spp, nyiso, isone, "more than one" or "none of the seven"
  source_flag: string;
  statement_id: string;
};

const TOP = ["event_id", "event_date", "parties", "mw", "status", "source_url"];
const EXTRA = ["entity_group", "entity_type", "row_kind", "mw_low", "mw_high", "duration_as_stated", "wait_basis", "wait_counted", "load_scope",
  "stage_class", "document_title", "document_type", "page", "event_date_basis", "public_basis", "regulator", "state", "grid", "source_flag", "statement_id"];

/** The statements, newest first; with `grid`, that grid's only (its own word in the table: "ercot", "pjm", ...). */
export async function largeLoadStatements(grid?: string): Promise<LargeLoadStatement[]> {
  const query: Record<string, string> = {
    select: [...TOP, ...EXTRA.map((k) => `${k}:extra->>${k}`)].join(","),
    table_name: `eq.${TABLE}`,
    order: "event_date.desc,event_id",
  };
  if (grid) query["extra->>grid"] = `eq.${grid}`;
  return rest<LargeLoadStatement>("events", query, HOURLY, 2_000);
}
