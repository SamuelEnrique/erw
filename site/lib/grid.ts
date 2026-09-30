// Energy Research Warehouse (ERW) site: the grid pages' data (session 35, /grid/<slug>). One reader per block, each
// for one grid of docs/grids/grids.json; every number a page shows is a row of a live-set table, or a sum of rows
// that site/scripts/check-values.mjs recomputes with the same key.
import "server-only";
import { HOURLY, rest } from "@/lib/supabase";
import { DOCS, type GridConfig } from "@/lib/markdown";
import { daysAgo, series, storageUnits, type SeriesRow, type StorageUnit } from "@/lib/data";

export const GRIDS: GridConfig[] = DOCS.grid_config;
export const gridOf = (slug: string) => GRIDS.find((g) => g.slug === slug) ?? null;

// EIA-930 fuel variables, in the fixed color order of the token file (as /grid)
export const FUELS: { key: string; label: string; vars: string[] }[] = [
  { key: "gas", label: "Natural gas", vars: ["natural_gas"] },
  { key: "coal", label: "Coal", vars: ["coal"] },
  { key: "nuclear", label: "Nuclear", vars: ["nuclear"] },
  { key: "wind", label: "Wind", vars: ["wind", "wind_with_battery"] },
  { key: "solar", label: "Solar", vars: ["solar", "solar_with_battery"] },
  { key: "hydro", label: "Hydro", vars: ["hydro"] },
  { key: "storage", label: "Storage", vars: ["battery", "pumped_storage", "other_storage", "unknown_storage"] },
  { key: "other", label: "Other", vars: [] },
];
export const fuelOf = (variable: string) => {
  const f = variable.replace(/^net_generation_/, "").replace(/_mw$/, "");
  return FUELS.find((g) => g.vars.includes(f))?.key ?? "other";
};
export const fuelName = (variable: string) =>
  variable.replace(/^net_generation_/, "").replace(/_mw$/, "").split("_").join(" ");

export type QueueRow = { entity_id: string; capacity_mw: number | null; status: string | null; tech: string | null };
export type NewsRow = { event_id: string; event_date: string; source: string; source_url: string; extra: Record<string, string> };

/** The grid's queue positions in energy_projects (the live set leaves out withdrawn ones). */
async function queue(table: string): Promise<QueueRow[]> {
  return rest<QueueRow>("entities", {
    select: "entity_id,capacity_mw,status,tech:extra->>technology_group",
    table_name: "eq.energy_projects",
    // the queue rows' ids share a prefix (ercot_queue:...), which the primary key serves; a filter on extra timed out
    entity_id: `like.${table.replace(/_interconnection_queue$/, "_queue")}:*`,
    order: "entity_id",
  }, HOURLY);
}

/** Scored news of the last `days` days (news_index), newest first. */
async function news(since: string): Promise<NewsRow[]> {
  return rest<NewsRow>("events", {
    select: "event_id,event_date,source,source_url,extra",
    table_name: "eq.news_index",
    event_date: `gte.${since}`,
    order: "event_date.desc,event_id",
  }, HOURLY);
}

export type Facility = { entity_id: string; capacity_mw: number | null; state: string | null; utility: string | null; member_ids: string | null };

/** Datacenter facilities of datacenter_facilities, with their state, utility, member ids and MW. */
async function datacenterStates(): Promise<Facility[]> {
  return rest("entities", {
    select: "entity_id,capacity_mw,state:extra->>state,utility:extra->>utility,member_ids:extra->>member_ids",
    table_name: "eq.datacenter_facilities",
    order: "entity_id",
  }, HOURLY);
}

/** Session 36A (docs/methods/datacenter_facilities.md, "Grid pages"): the grid a facility belongs to, or null when no
 * rule gives one: a facility from an ISO's queue (member id <iso>_queue:...) is that ISO's; else one whose utility a
 * grid lists is that grid's. The pages then fall back to the state lists for a null. check-values.mjs does the same. */
export function facilityGrid(f: { utility: string | null; member_ids: string | null }): string | null {
  const ids = (f.member_ids ?? "").split(";");
  for (const g of GRIDS) {
    const pre = g.queue_table ? g.queue_table.replace(/_interconnection_queue$/, "_queue:") : null;
    if (pre && ids.some((x) => x.startsWith(pre))) return g.slug;
  }
  const u = (f.utility ?? "").trim();
  return u ? GRIDS.find((g) => g.utilities.includes(u))?.slug ?? null : null;
}

export function facilityInGrid(g: GridConfig, f: Facility): boolean {
  const by = facilityGrid(f);
  return by ? by === g.slug : !!f.state && f.state in g.states;
}

/** A story is this grid's when its headline names the grid (a word of names) or its region is one of its states.
 * check-values.mjs matches the same way. */
export function newsMatch(g: GridConfig, r: { extra: Record<string, string> }): boolean {
  const h = r.extra?.headline ?? "";
  const region = (r.extra?.region ?? "").trim();
  return g.names.some((n) => new RegExp(`\\b${n.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`).test(h))
    || Object.values(g.states).includes(region);
}

export type GridData = {
  demand: SeriesRow[]; gen: SeriesRow[]; cycle: SeriesRow[]; units: StorageUnit[];
  ci: SeriesRow[]; monthly: SeriesRow[]; prices: SeriesRow[]; peak: SeriesRow[];
  queue: QueueRow[]; dcs: Facility[];
  news: NewsRow[]; newsSince: string;
  errors: Record<string, string>;
};

export async function load(g: GridConfig): Promise<GridData> {
  const errors: Record<string, string> = {};
  const safe = async <T,>(what: string, f: () => Promise<T>, empty: T): Promise<T> => {
    try {
      return await f();
    } catch (e) {
      errors[what] = (e as Error).message;
      return empty;
    }
  };
  const newsSince = daysAgo(14);
  const [demand, gen, cycle, units, ci, monthly, prices, peak, q, dcs, n] = await Promise.all([
    safe("demand", () => series("eia930_all_demand", { entity: g.entity, variable: "demand_mw", since: daysAgo(9) }), []),
    safe("gen", () => series("eia930_all_generation", { entity: g.entity, since: daysAgo(34) }), []), // covers the 30-day window whole
    safe("cycle", () => (g.storage_entity ? series("storage_daily_cycle", { entity: g.storage_entity, since: daysAgo(45) }) : Promise.resolve([])), []),
    safe("units", storageUnits, []),
    safe("ci", () => series("carbon_intensity_hourly", { entity: g.entity, since: daysAgo(4) }), []),
    safe("monthly", () => series("carbon_intensity_monthly", { entity: g.entity, variable: "intensity_generation" }), []),
    safe("prices", () => (g.hub && g.prices_public ? series("price_board_latest", { entity: g.hub.entity }) : Promise.resolve([])), []),
    safe("peak", () => (g.hub && g.prices_public ? series("price_board_peak_offpeak", { entity: g.hub.entity, since: daysAgo(20) }) : Promise.resolve([])), []),
    safe("queue", () => (g.queue_table ? queue(g.queue_table) : Promise.resolve([])), []),
    safe("dcs", datacenterStates, []),
    safe("news", () => news(newsSince), []),
  ]);
  return {
    demand, gen, cycle, units: units.filter((u) => u.iso === g.iso), ci, monthly, prices, peak, queue: q,
    dcs: dcs.filter((d) => facilityInGrid(g, d)), news: n.filter((r) => newsMatch(g, r)), newsSince, errors,
  };
}
