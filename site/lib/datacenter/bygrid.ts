// Energy Research Warehouse (ERW) site, session 467 and 468 (chain 019): the datacenter tracker by grid. Pure, with no
// imports: the page (app/datacenters/GridsView.tsx), scripts/check-values.mjs and tests/test_session468.py read this file
// as it is. The sites are the interconnection-queue positions that name a datacenter or a large load (lib/data.ts,
// queueSites), the facilities of datacenter_facilities that rest on a public source; the queue totals are each grid's
// own queue, the positions still active.

/** The words of warehouse/derived/datacenter_facilities.py's QUEUE_PATTERN, as PostgreSQL reads a regular expression
 *  (tests/test_session467.py holds the two equal). A queue position whose name or fuel field matches is one the
 *  datacenter tracker counts as naming a datacenter or a large load. */
export const QUEUE_SITE_PATTERN = "data ?cent(?:er|re)s?|datacenter|large load|co-?located load|digital campus|hyperscale|crypto|bitcoin";
/** Session 2302 (chain 087): the fields of a queue row the pattern is matched against, as the live set names them (the
 *  PostgREST column or JSON path), in the order they are read. The operator is the third: session 2102 found two ERCOT
 *  positions (Bullock Gas, Liberty Thermal Energy Center; 1,400 MW of combined-cycle each, Hill County, Texas) whose only
 *  data-center word is their owner's name (Bullock Data Center, LLC; Liberty Data Center I, LLC). The derived table
 *  datacenter_queue_positions still reads the name and fuel fields alone (the data machine's change); the site's read
 *  layer reads the operator too, so the tracker's power side shows them. The same list serves scripts/check-values.mjs. */
export const QUEUE_SITE_FIELDS = ["name", "extra->>fuel_technology", "operator"] as const;
export type QueueSiteField = (typeof QUEUE_SITE_FIELDS)[number];
const SITE_RE = new RegExp(QUEUE_SITE_PATTERN, "i");
/** The first field of a row (in QUEUE_SITE_FIELDS' order) that names a datacenter or a large load, or null: the pure
 *  rule behind lib/data.ts queueSites, so a fixture can test it (scripts/test-queue-sites.mjs). A point of
 *  interconnection is never read: "load" in a substation's name is not a large load. */
export function queueSiteMatch(row: { name?: string | null; operator?: string | null; extra?: { fuel_technology?: string | null } | null }): QueueSiteField | null {
  if (SITE_RE.test(row.name ?? "")) return "name";
  if (SITE_RE.test(row.extra?.fuel_technology ?? "")) return "extra->>fuel_technology";
  if (SITE_RE.test(row.operator ?? "")) return "operator";
  return null;
}
/** The words of a match, for a row's hover ("named a data center by its operator's name"). */
export const matchWords = (field: QueueSiteField | null): string =>
  field === "name" ? "named in the position's own name" : field === "extra->>fuel_technology" ? "named in the position's fuel or type field" : field === "operator" ? "named by its operator's name" : "not matched";
/** The six queues the builder reads (warehouse/derived/energy_projects.py, QUEUE_ISOS), in its order. */
export const QUEUE_GRIDS = ["ercot", "caiso", "nyiso", "miso", "spp", "isone"] as const;
/** The zone of a site or a position whose queue names none: one group a grid, compared with the grid's whole queue. */
export const NO_ZONE = "-";

/** What the grouping needs of a queue row: its table (the grid), its zone as the queue states it, its MW and status. */
export type QueueRow = { table_name: string; capacity_mw: number | string | null; status?: string | null; zone?: string | null };
export const gridOfTable = (t: string) => t.replace(/_interconnection_queue$/, "");
export const zoneOfRow = (r: QueueRow) => (r.zone ?? "").trim() || NO_ZONE;
const mwOf = (r: QueueRow) => (r.capacity_mw === null || r.capacity_mw === "" || r.capacity_mw === undefined ? null : Number(r.capacity_mw));

export type Group = {
  grid: string; zone: string;
  sites: number;            // the public-source sites in the group
  sitesWithMw: number;      // of them, those whose position states its MW
  mwAsked: number;          // the MW those positions ask to connect (generation or storage, not the site's load)
  activePositions: number;  // the queue's positions still active: in the zone, or, for NO_ZONE, in the whole grid
  activeMw: number;         // and their MW, where stated
};

/** One group a grid and zone that holds a site, in the queue grids' order then by zone. `active` is each grid's active
 *  positions (status "active"); a zone's totals count the active positions the queue places in that zone, and the
 *  NO_ZONE group's the grid's whole queue. */
export function groups(sites: QueueRow[], active: QueueRow[]): Group[] {
  const by = new Map<string, Group>();
  for (const s of sites) {
    const grid = gridOfTable(s.table_name), zone = zoneOfRow(s), k = `${grid}|${zone}`;
    const g = by.get(k) ?? { grid, zone, sites: 0, sitesWithMw: 0, mwAsked: 0, activePositions: 0, activeMw: 0 };
    g.sites++;
    const mw = mwOf(s);
    if (mw !== null && Number.isFinite(mw)) { g.sitesWithMw++; g.mwAsked += mw; }
    by.set(k, g);
  }
  for (const g of by.values()) {
    for (const a of active) {
      if (gridOfTable(a.table_name) !== g.grid) continue;
      if (g.zone !== NO_ZONE && zoneOfRow(a) !== g.zone) continue;
      g.activePositions++;
      const mw = mwOf(a);
      if (mw !== null && Number.isFinite(mw)) g.activeMw += mw;
    }
  }
  const order = (grid: string) => { const i = (QUEUE_GRIDS as readonly string[]).indexOf(grid); return i < 0 ? 99 : i; };
  return [...by.values()].sort((a, b) => order(a.grid) - order(b.grid) || a.grid.localeCompare(b.grid) || a.zone.localeCompare(b.zone));
}

/** A figure of a group by its key's last part (dcq|<grid>|<zone>|<stat>), for scripts/check-values.mjs. */
export function groupStat(gs: Group[], grid: string, zone: string, stat: string): number | undefined {
  const g = gs.find((x) => x.grid === grid && x.zone === zone);
  if (!g) return undefined;
  return ({ sites: g.sites, sites_with_mw: g.sitesWithMw, mw_asked: g.mwAsked, active_positions: g.activePositions, active_mw: g.activeMw } as Record<string, number>)[stat];
}
