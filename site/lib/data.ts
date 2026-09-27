// Energy Research Warehouse (ERW) site: the reads each page makes, over lib/supabase.ts.
import "server-only";
import { DataError, HOURLY, LATEST, rest } from "./supabase";
import markets from "@/data/markets.json";

export type CatalogueRow = {
  table_name: string;
  iso: string | null;
  market: string | null;
  n_nodes: number | null;
  interval: string | null;
  ts_min: string | null;
  ts_max: string | null;
  n_rows: number | null;
  source_report: string | null;
  last_run: string | null;
  validator_status: string | null;
  license: string;
  sector: string | null;
  derived: string | null;
  in_live_set: string;
};

export type LatestPrice = {
  entity: string;
  variable: string;
  ts_utc: string;
  value: number;
  unit: string;
  source: string;
  retrieved_at: string;
  license: string;
};

export type Point = { ts_utc: string; value: number };
export type SeriesRow = { entity: string; variable: string; ts_utc: string; value: number; unit: string };

export type Market = (typeof markets.isos)[number];
export const MARKETS: Market[] = markets.isos;

/** One row per ERW table, public tables only (row-level security hides the rest). */
export async function catalogue(): Promise<CatalogueRow[]> {
  const rows = await rest<CatalogueRow>("catalogue", { select: "*", order: "table_name" }, HOURLY);
  if (rows.length === 0) throw new DataError("the catalogue table returned no rows");
  return rows.filter((r) => r.license === "public");
}

/** The newest real-time interval per hub and zone, refreshed every 15 minutes. */
export async function latestPrices(): Promise<LatestPrice[]> {
  const rows = await rest<LatestPrice>("latest_prices", { select: "*", order: "entity" }, LATEST);
  if (rows.length === 0) throw new DataError("the latest_prices table returned no rows");
  return rows;
}

/** Rows of one series table for one entity (or every entity) since a time. */
export async function series(
  table: string,
  opts: { entity?: string; variable?: string; since?: string; entities?: string[] },
  revalidate = HOURLY,
): Promise<SeriesRow[]> {
  const q: Record<string, string> = {
    select: "entity,variable,ts_utc,value,unit",
    table_name: `eq.${table}`,
    order: "entity,variable,ts_utc", // the key: stable pages
  };
  if (opts.entity) q.entity = `eq.${opts.entity}`;
  if (opts.entities) q.entity = `in.(${opts.entities.map((e) => `"${e}"`).join(",")})`;
  if (opts.variable) q.variable = `eq.${opts.variable}`;
  if (opts.since) q.ts_utc = `gte.${opts.since}`;
  return rest<SeriesRow>("series", q, revalidate);
}

/** The newest row of one entity in one series table. */
export async function newest(table: string, entity: string, variable: string): Promise<SeriesRow | null> {
  const rows = await rest<SeriesRow>(
    "series",
    {
      select: "entity,variable,ts_utc,value,unit",
      table_name: `eq.${table}`,
      entity: `eq.${entity}`,
      variable: `eq.${variable}`,
      order: "ts_utc.desc",
    },
    HOURLY,
    1,
  );
  return rows[0] ?? null;
}

/** Rows of one series table for a list of variables (the peak-premium explorer). */
export async function seriesVariables(table: string, variables: string[]): Promise<SeriesRow[]> {
  return rest<SeriesRow>(
    "series",
    {
      select: "entity,variable,ts_utc,value,unit",
      table_name: `eq.${table}`,
      variable: `in.(${variables.join(",")})`,
      order: "entity,variable,ts_utc",
    },
    HOURLY,
  );
}

/** The provenance header lines of a live-set table (its CSV's '#' lines). */
export async function headers(table: string): Promise<string[]> {
  const rows = await rest<{ line: string }>(
    "headers",
    { select: "line", table_name: `eq.${table}`, order: "line_no" },
    HOURLY,
  );
  return rows.map((r) => r.line);
}

/** ISO timestamp for `days` days before now, for PostgREST filters. */
export function daysAgo(days: number, now = Date.now()): string {
  // floored to the hour, so every render within an hour asks for the same URL (and hits the cache)
  const t = Math.floor((now - days * 86_400_000) / 3_600_000) * 3_600_000;
  return new Date(t).toISOString().replace(/\.\d{3}Z$/, "Z");
}

/** The time this render runs. A cached page is re-rendered on its revalidate schedule, so "now" is the render time. */
export function renderTime(): number {
  return Date.now();
}

/** A deal of energy_deals (session 15): the events columns, with the table's own columns in extra. */
export type DealRow = {
  event_id: string;
  event_date: string;
  status: string | null;
  mw: number | null;
  price: number | null;
  currency: string | null;
  parties: string | null;
  source: string;
  source_url: string;
  extra: Record<string, string>;
};

/** Every deal in the live set (public rows only), newest first. */
export async function deals(): Promise<DealRow[]> {
  return rest<DealRow>(
    "events",
    {
      select: "event_id,event_date,status,mw,price,currency,parties,source,source_url,extra",
      table_name: "eq.energy_deals",
      order: "event_date.desc,event_id",
    },
    HOURLY,
  );
}

/** A point of the project map (session 16): the fields the map draws and filters on. */
export type ProjectPoint = {
  entity_id: string;
  lat: number | null;
  lon: number | null;
  capacity_mw: number | null;
  status: string | null;
  kind: string | null;
  tech: string | null;
  state: string | null;
  prec: string | null;
};

/** Every row of energy_projects in the live set (withdrawn queue positions are not loaded). */
export async function projectPoints(): Promise<ProjectPoint[]> {
  return rest<ProjectPoint>(
    "entities",
    {
      select:
        "entity_id,lat,lon,capacity_mw,status,kind:extra->>kind,tech:extra->>technology_group,state:extra->>state,prec:extra->>geo_precision",
      table_name: "eq.energy_projects",
      order: "entity_id",
    },
    HOURLY,
    100_000,
  );
}

/** One entities row of a live-set table, with its own columns in extra (the map's click card). */
export type EntityRow = {
  entity_id: string;
  entity_type: string;
  name: string | null;
  lat: number | null;
  lon: number | null;
  capacity_mw: number | null;
  status: string | null;
  status_date: string | null;
  operator: string | null;
  source: string;
  source_url: string | null;
  vintage: string | null;
  table_name: string;
  extra: Record<string, string>;
};

export async function entity(table: string, id: string): Promise<EntityRow | null> {
  const rows = await rest<EntityRow>(
    "entities",
    {
      select: "entity_id,entity_type,name,lat,lon,capacity_mw,status,status_date,operator,source,source_url,vintage,table_name,extra",
      table_name: `eq.${table}`,
      entity_id: `eq.${id}`,
    },
    HOURLY,
    1,
  );
  return rows[0] ?? null;
}
