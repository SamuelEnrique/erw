// Energy Research Warehouse (ERW) site, session 467 and 468 (chain 019): the datacenter tracker by grid. Pure, with no
// imports: the page (app/datacenters/GridsView.tsx), scripts/check-values.mjs and tests/test_session468.py read this file
// as it is. The sites are the interconnection-queue positions that name a datacenter or a large load (lib/data.ts,
// queueSites), the facilities of datacenter_facilities that rest on a public source; the queue totals are each grid's
// own queue, the positions still active.

/** The words of warehouse/derived/datacenter_facilities.py's QUEUE_PATTERN, as PostgreSQL reads a regular expression
 *  (tests/test_session467.py holds the two equal). A queue position whose name or fuel field matches is one the
 *  datacenter tracker counts as naming a datacenter or a large load. */
export const QUEUE_SITE_PATTERN = "data ?cent(?:er|re)s?|datacenter|large load|co-?located load|digital campus|hyperscale|crypto|bitcoin";
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
