// Energy Research Warehouse (ERW) site, session 183: "What a generator earns" priced at the hub or zone chosen.
//
// Until this session the page priced its revenue, its months and its debt coverage at the grid's main hub whatever
// hub was chosen, while the capture price and the contract followed the hub. The files of data/seller/hubs
// (warehouse/derived/merchant_hubs.py) hold the seller's own model solved again with each hub's own hourly price. This
// file turns one hub's file into the record lib/merchant.ts reads for a grid, so every figure of the page (the months,
// the bad months, debt coverage, the spans, the peaker at the reader's heat rate, ERCOT's stress days) is computed by
// the same functions at the hub chosen. The main hub keeps the page's own snapshot: nothing here is used for it.
// docs/methods/generator_earns_algorithm.md, "Another hub or zone".
import type { SnapIso, SnapMonth, Snapshot } from "@/lib/merchant";

export type HubMarket = "rt" | "da";
export type HubEntry = { file: string; market: HubMarket; basis: string; tables: string[]; first: string; last: string; months: number; bytes: number };
/** The builder at the main hub against the page's snapshot, per asset: months compared and the largest difference. */
export type HubCheck = Record<string, { months: number; max_abs_usd_per_mw: number; max_share: number; at: string }>;
export type HubIndex = {
  built: string; method: string; near: number; since: string; snapshot_built: string; capture_built: string; henry_hub: string; eia860m: string[];
  grids: Record<string, { name: string; tz: string; main: string; workbook: string; file: string; check: HubCheck | null; hubs: Record<string, HubEntry> }>;
};
/** A grid's hourly index: its first hour, Henry Hub by hour, and each local month's [first index, last index + 1, hours in the month]. */
export type GridFile = { iso: string; tz: string; start: string; hours: number; months: Record<string, [number, number, number]>; hh: (number | null)[] };
export type HubFile = { id: string; entity: string; market: HubMarket; months: Record<string, Omit<SnapMonth, "him" | "i0" | "i1">>; price: (number | null)[]; stress?: SnapIso["stress"] };

/** The grid's record with one hub's months, prices and stress days in place of the main hub's. The fleet's hours above
 *  nameplate and below zero are the grid's, whatever the hub. A month the grid's index does not hold is left out. */
export function hubIso(base: SnapIso, grid: GridFile, hub: HubFile): SnapIso {
  const months: Record<string, SnapMonth> = {};
  for (const [m, r] of Object.entries(hub.months)) {
    const ix = grid.months[m];
    if (!ix) continue;
    months[m] = { ...r, him: ix[2], i0: ix[0], i1: ix[1] } as SnapMonth;
  }
  return { iso: base.iso, hub: hub.id, ba: base.ba, tz: base.tz, start: grid.start, months, price: hub.price, hh: grid.hh, stress: hub.stress, over_nameplate: base.over_nameplate, negative: base.negative };
}

/** The snapshot with one grid's record replaced: what lib/merchant.ts and lib/seller2.ts then read. */
export const withHub = (snap: Snapshot, iso: string, s: SnapIso): Snapshot => ({ ...snap, isos: { ...snap.isos, [iso]: s } });

export const marketWords = (m: HubMarket) => (m === "rt" ? "real-time" : "day-ahead");
/** The check keys of a page priced at another hub carry the hub and its market, so no check reads them as the main hub's. */
export const hubKey = (key: string, hub: string, market: HubMarket) => `${key}&hub=${hub}&market=${market}`;
