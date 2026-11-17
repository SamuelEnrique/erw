// Energy Research Warehouse (ERW) site, ruling alternative 2 of /grid (session 7725, 17 November 2026; branch
// wip/alt-grid-2, not a default on main): the Mix tab's demand "right now" is the hourly snapshot's (data/grid_network.json
// or its hourly refresh, the node's demand_mw at demand_ts), as the Network tab reads it, where that hour is newer than
// the daily table's newest hour (eia930_all_demand); otherwise the table's. On main it is always the table's. No imports
// beyond types: Node runs this file as it is.

export type DemandRow = { entity: string; variable: string; ts_utc: string; value: number; unit?: string; freq?: string };
export type SnapNode = { id: string; demand_mw: number | null; demand_ts: string | null };

export function pickDemand(table: DemandRow | undefined, node: SnapNode | undefined, entity: string): { d: DemandRow | undefined; fromSnap: boolean } {
  const fromSnap = !!(node && node.demand_mw !== null && node.demand_ts && (!table || Date.parse(node.demand_ts) > Date.parse(table.ts_utc)));
  return fromSnap ? { d: { entity, variable: "demand_mw", ts_utc: node!.demand_ts!, value: node!.demand_mw!, unit: "MW", freq: "PT1H" }, fromSnap } : { d: table, fromSnap };
}
