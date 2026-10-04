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
  // session 28: the provenance tier, source, derived or model_extracted (docs/datastandard.md)
  tier: string | null;
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
export type SeriesRow = { entity: string; variable: string; ts_utc: string; value: number; unit: string; freq?: string | null };

export type Market = (typeof markets.isos)[number];
export const MARKETS: Market[] = markets.isos;

/** One row per ERW table, public tables only (row-level security hides the rest). Session 102: a table loaded for a page
 *  in review (in_live_set "review": warehouse/supabase/live_set.yaml, review_hold) is left out, so no count a visitor
 *  sees moves when such a table is loaded. */
export async function catalogue(): Promise<CatalogueRow[]> {
  const rows = await rest<CatalogueRow>("catalogue", { select: "*", order: "table_name" }, HOURLY);
  if (rows.length === 0) throw new DataError("the catalogue table returned no rows");
  return rows.filter((r) => r.license === "public" && r.in_live_set !== "review");
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
  opts: { entity?: string; variable?: string; since?: string; entities?: string[]; market?: string; event?: string },
  revalidate = HOURLY,
): Promise<SeriesRow[]> {
  const q: Record<string, string> = {
    select: "entity,variable,ts_utc,value,unit,freq", // session 30: freq tells /board's daily rows from its annual ones
    table_name: `eq.${table}`,
    order: "entity,variable,ts_utc,event", // the key (session 36C: event is part of it, '' outside event_window_daily): stable pages
  };
  if (opts.entity) q.entity = `eq.${opts.entity}`;
  if (opts.entities) q.entity = `in.(${opts.entities.map((e) => `"${e}"`).join(",")})`;
  if (opts.variable) q.variable = `eq.${opts.variable}`;
  // session 29: one partition of a consolidated table (iso_trader_daily, iso_dam_hub_prices, ...)
  if (opts.market) q.market = `eq.${opts.market}`;
  // session 36C: one event of event_window_daily (uri_2021, covid_2020)
  if (opts.event) q.event = `eq.${opts.event}`;
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
  src?: string | null; // datacenters: news, operator or queue (session 22)
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

/** Map points of datacenter_facilities (session 16, tool 4; session 22: news, operator lists and queues in
 * one table): the fourth kind on the project map. kind is the entity type, datacenter; the source kind is src. */
export async function datacenterPoints(): Promise<ProjectPoint[]> {
  return rest<ProjectPoint>(
    "entities",
    {
      select: "entity_id,lat,lon,capacity_mw,status,kind:entity_type,src:extra->>kind,tech:extra->>technology_group,state:extra->>state,prec:extra->>geo_precision",
      table_name: "eq.datacenter_facilities",
      order: "entity_id",
    },
    HOURLY,
  );
}

/** Every facility of datacenter_facilities in the live set (session 22), with its own columns in extra. */
export async function datacenters(): Promise<EntityRow[]> {
  return rest<EntityRow>(
    "entities",
    {
      select: "entity_id,entity_type,name,lat,lon,capacity_mw,status,status_date,operator,source,source_url,vintage,table_name,extra",
      table_name: "eq.datacenter_facilities",
      order: "entity_id",
    },
    HOURLY,
  );
}

/** Session 24: a policy action (policy_actions) with its scores and, when it has one, its impact read (policy_reads). */
export type PolicyAction = {
  event_id: string;
  event_date: string;
  status: string | null;
  source_url: string;
  agency: string;
  action_type: string;
  title: string;
  docket: string;
  sector_tags: string;
  states: string;
  significance: string;
  sector: string;
  why: string;
  related_urls: string;
  news_story_urls: string;
};
export type PolicyRead = {
  action_event_id: string;
  what_changes: string;
  affected_sectors: string;
  affected_isos: string;
  affected_states: string;
  direction_supply: string;
  direction_demand: string;
  direction_prices: string;
  direction_buildout: string;
  timeline: string;
  plain_read: string;
  fields_kept: string;
  fields_dropped: string;
  model_id: string;
};

export async function policyActions(): Promise<PolicyAction[]> {
  const f = ["agency", "action_type", "title", "docket", "sector_tags", "states", "significance", "sector", "why", "related_urls", "news_story_urls"];
  return rest<PolicyAction>(
    "events",
    {
      select: ["event_id", "event_date", "status", "source_url", ...f.map((k) => `${k}:extra->>${k}`)].join(","),
      table_name: "eq.policy_actions",
      order: "event_date.desc,event_id",
    },
    HOURLY,
    10_000,
  );
}

export async function policyReads(): Promise<PolicyRead[]> {
  const f = ["action_event_id", "what_changes", "affected_sectors", "affected_isos", "affected_states", "direction_supply", "direction_demand",
    "direction_prices", "direction_buildout", "timeline", "plain_read", "fields_kept", "fields_dropped", "model_id"];
  return rest<PolicyRead>("events", { select: f.map((k) => `${k}:extra->>${k}`).join(","), table_name: "eq.policy_reads", order: "event_id" }, HOURLY, 10_000);
}

/** Session 26: a company of energy_companies (tool 10's seed, from Thesis Builder runs). */
export type Company = {
  entity_id: string;
  name: string;
  source_url: string | null;
  description: string;
  sector: string;
  niche_tags: string;
  stage: string;
  raised: string;
  location: string;
  founders: string;
  website: string;
  sources: string;
  confidence: string;
  confidence_note: string;
  first_seen: string;
};

export async function companies(): Promise<Company[]> {
  const f = ["description", "sector", "niche_tags", "stage", "raised", "location", "founders", "website", "sources", "confidence",
    "confidence_note", "first_seen"];
  return rest<Company>(
    "entities",
    { select: ["entity_id", "name", "source_url", ...f.map((k) => `${k}:extra->>${k}`)].join(","), table_name: "eq.energy_companies", order: "name" },
    HOURLY,
    10_000,
  );
}

/** Session 31: a battery unit of storage_capacity (EIA-860M), the fields /storage sums. */
export type StorageUnit = {
  entity_id: string;
  capacity_mw: number | null;
  status: string | null;
  state: string | null;
  iso: string | null;
  planned_year: string | null;
  mwh: string | null; // session 34: EIA's Nameplate Energy Capacity (MWh); none for planned units
};

export async function storageUnits(): Promise<StorageUnit[]> {
  return rest<StorageUnit>(
    "entities",
    { select: "entity_id,capacity_mw,status,state:extra->>state,iso:extra->>iso,planned_year:extra->>planned_year,mwh:extra->>energy_capacity_mwh", table_name: "eq.storage_capacity", order: "entity_id" },
    HOURLY,
    20_000,
  );
}
