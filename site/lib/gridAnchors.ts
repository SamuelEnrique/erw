// Energy Research Warehouse (ERW) site, session 1183 (chain 091): every panel chains 077, 078 and 091 added to the Grid
// tool (/grid) has an anchor, so a reader's view can be shared as an address: the tab, the grid and the panel's own
// state in the query (lib/gridtool.ts gridHref: grid, view, net, t, node, shape, mixp, mix, grids, year, q), the panel
// after the #. One list, read by the components that draw the panels, by scripts/test-grid-addresses.mjs (each address
// opens its tab and grid, its state read back), by scripts/test-grid-files.mjs (each drawn panel carries its anchor, and
// no id is twice on a page) and by scripts/check-routes.mjs (a landing asks each address and finds the anchor on it).
// The method note docs/methods/grid_network.md names each one ("Every panel in the address").
//
// An anchor is the same on every grid where the panel is the same: the grid is in the query, not in the anchor. Where a
// page draws the same panel for several grids (the energy mix panel with grids=pjm,miso; the stress view's three tables
// a grid), the first takes the anchor and each next one the anchor and its grid (anchorOf), as the Mix view's own older
// sections do (today, today-<ba>; hourly, hourly-<ba>). Three panels kept the anchor their section had before this
// session (scarcity, caiso-alerts, ercot-notices): links already point to them.
import type { GridView } from "@/lib/gridtool";

export const GRID_ANCHOR = {
  network: "network-figures",
  replay: "replayed-day",
  balance: "balance",
  gravity: "gravity-figures",
  exchangeGrids: "exchange-grids",
  exchangeTies: "exchange-ties",
  exchangeMonths: "exchange-months",
  clean24: "last-24-hours",
  mix: "mix-panel",
  scarcity: "scarcity",
  caisoAlerts: "caiso-alerts",
  ercotNotices: "ercot-notices",
  ask: "stored-answers",
  stressRamp: "stress-ramp",
  stressTight: "stress-tight",
  stressCalm: "stress-calm",
  stressGrids: "stress-grids",
} as const;
export type GridAnchorKey = keyof typeof GRID_ANCHOR;

/** The anchor of a panel drawn for a grid among several on one page: the first (i = 0) the anchor, the next ones the
 *  anchor and the grid ("mix-panel-miso"). */
export function anchorOf(key: GridAnchorKey, i: number, grid: string): string {
  return i ? `${GRID_ANCHOR[key]}-${grid}` : GRID_ANCHOR[key];
}

/** Each panel, the block on the page that carries the anchor (its data-grid-panel name, or the attribute that names a
 *  block inside one), and an address that opens it with its state: the tab and the grid it opens on (`tab`, `grid`),
 *  and the words of the panel's own state the address carries (`state`). */
export type PanelAnchor = { key: GridAnchorKey; panel: string; block: string; what: string; address: string; tab: GridView; grid: string; state: string[] };

export const PANEL_ANCHORS: PanelAnchor[] = [
  { key: "network", panel: "grid_network_<grid>", block: "data-grid-panel", what: "the grid's ties (or the seven grids) in the hour the network shows", address: "/grid?grid=ercot&view=network&net=day&t=2021-02-15&node=BPAT", tab: "network", grid: "ercot", state: ["net", "t", "node"] },
  { key: "replay", panel: "grid_replay_<BA>", block: "data-grid-replay-day", what: "the balancing authority in the address on the day picked in the replay", address: "/grid?grid=ercot&view=network&net=day&t=2021-02-15&node=ERCO", tab: "network", grid: "ercot", state: ["net", "t", "node"] },
  { key: "balance", panel: "grid_network_<grid> (its balance)", block: "data-grid-balance", what: "whether the grid's balance closes, the hour shown and the week", address: "/grid?grid=ercot&view=network", tab: "network", grid: "ercot", state: [] },
  { key: "gravity", panel: "grid_gravity_<grid>", block: "data-grid-panel", what: "the seven grids in the gravity shape, the hour shown (and the replayed day's demand)", address: "/grid?grid=ercot&view=gravity&shape=gravity&net=day&t=2021-02-15", tab: "gravity", grid: "ercot", state: ["shape", "net", "t"] },
  { key: "exchangeGrids", panel: "grid_exchange_us48", block: "data-grid-view", what: "the seven grids' net export in the snapshot's hour", address: "/grid?grid=us48&view=gravity&shape=gravity", tab: "gravity", grid: "us48", state: ["shape"] },
  { key: "exchangeTies", panel: "grid_exchange_<grid> (ties)", block: "data-grid-view", what: "the grid's ties in the hour, and each tie over the snapshot's week", address: "/grid?grid=ercot&view=gravity&shape=gravity", tab: "gravity", grid: "ercot", state: ["shape"] },
  { key: "exchangeMonths", panel: "grid_exchange_<grid> (twelve months)", block: "data-grid-view", what: "the grid's neighbours over the last twelve months", address: "/grid?grid=ercot&view=gravity&shape=gravity", tab: "gravity", grid: "ercot", state: ["shape"] },
  { key: "clean24", panel: "grid_clean24_<grid>", block: "data-grid-panel", what: "the latest, lowest and highest intensity of generation per ISO in the last 24 hours", address: "/grid?grid=ercot&view=clean", tab: "clean", grid: "ercot", state: [] },
  { key: "mix", panel: "grid_mix_<grid>", block: "data-grid-panel", what: "the energy mix panel, hourly or by month", address: "/grid?grid=ercot&mixp=month", tab: "mix", grid: "ercot", state: ["mixp"] },
  { key: "scarcity", panel: "grid_scarcity_<grid>", block: "data-grid-panel", what: "the scarcity hours of the grid in view, the latest 30 days held", address: "/grid?grid=ercot", tab: "mix", grid: "ercot", state: [] },
  { key: "caisoAlerts", panel: "grid_caisoalert_caiso", block: "data-grid-panel", what: "CAISO's alerts: today, the last alert day, the notices that are not alerts", address: "/grid?grid=caiso", tab: "mix", grid: "caiso", state: [] },
  { key: "ercotNotices", panel: "grid_ercotnotice_ercot", block: "data-grid-panel", what: "ERCOT's notices: today, the last day of each kind, the notices that are not calls", address: "/grid?grid=ercot", tab: "mix", grid: "ercot", state: [] },
  { key: "ask", panel: "grid_ask_<grid>", block: "data-grid-panel", what: "the stored answers under the Ask box, the question in the box kept", address: "/grid?grid=ercot&ask=1&q=What+was+the+peak%3F", tab: "mix", grid: "ercot", state: ["ask", "q"] },
  { key: "stressRamp", panel: "grid_stress_<grid> (ramp)", block: "data-mix", what: "the evening ramp and the lowest net load, by year", address: "/grid?grid=ercot&mix=stress&year=2024", tab: "mix", grid: "ercot", state: ["mix", "year"] },
  { key: "stressTight", panel: "grid_stress_<grid> (tight)", block: "data-mix", what: "what each fuel gave in the tightest hours of the year", address: "/grid?grid=ercot&mix=stress&year=2024", tab: "mix", grid: "ercot", state: ["mix", "year"] },
  { key: "stressCalm", panel: "grid_stress_<grid> (calm)", block: "data-mix", what: "dark, calm stretches, by year", address: "/grid?grid=ercot&mix=stress&year=2024", tab: "mix", grid: "ercot", state: ["mix", "year"] },
  { key: "stressGrids", panel: "grid_stress_all", block: "data-mix", what: "the seven grids in the year", address: "/grid?grid=ercot&mix=stress&year=2024", tab: "mix", grid: "ercot", state: ["mix", "year"] },
];

/** The address of a panel with its anchor: what a reader shares. */
export const panelAddress = (a: PanelAnchor) => `${a.address}#${GRID_ANCHOR[a.key]}`;

// Session 1184 (chain 091): each panel's method, the section of its note that defines it (the chain 077 or 078
// section, or the older section the panel follows), as /data/methods/<note>#<heading id>. The id is the one the site's
// renderer writes for the heading (lib/markdown.ts headingSlugs): scripts/test-grid-methods.mjs renders each committed
// note with lib/markdown.ts render and holds each fragment to an id of it, under the heading named there; check-links.mjs
// finds the same ids on the served method page. One constant a panel, each linked in its component as
// href={METHOD_<PANEL>}: scripts/check-methods.mjs reads a constant that holds a note's address as a link to that note,
// and scripts/page_tables.py reads only the constants a component imports, so a note named like a table (ercot_grid_notices)
// is not taken for a read of the network's panels. GRID_METHOD gathers them by panel, for the tests. A heading renamed in
// a note moves its id: the test says which link broke.
export const METHOD_NETWORK = "/data/methods/grid_network#the-grid-tools-panels-every-figure-keyed-chain-077-23-october-2026";
export const METHOD_REPLAY = "/data/methods/grid_network_v3#the-outside-grids-demand-in-the-replay-chain-078-24-october-2026";
export const METHOD_BALANCE = "/data/methods/grid_network#the-balance-said-where-the-figures-are-chain-078-24-october-2026";
export const METHOD_GRAVITY = "/data/methods/grid_network#the-grid-tools-panels-every-figure-keyed-chain-077-23-october-2026";
export const METHOD_EXCHANGE_GRIDS = "/data/methods/grid_network#the-exchange-blocks-under-the-gravity-shape-session-1167";
export const METHOD_EXCHANGE_TIES = "/data/methods/grid_network#the-exchange-blocks-under-the-gravity-shape-session-1167";
export const METHOD_EXCHANGE_MONTHS = "/data/methods/grid_network#who-supplies-a-grid-session-68";
export const METHOD_CLEAN24 = "/data/methods/grid_network#the-grid-tools-panels-every-figure-keyed-chain-077-23-october-2026";
export const METHOD_MIX = "/data/methods/generation_mix_hourly#the-mix-tabs-energy-mix-keyed-hourly-and-by-month-chain-077-23-october-2026";
export const METHOD_SCARCITY = "/data/methods/scarcity_hours_by_grid#on-the-grid-tool-session-1154-23-october-2026";
export const METHOD_CAISO_ALERTS = "/data/methods/california_reliability#on-the-grid-tool-the-alert-state-session-1155-23-october-2026";
export const METHOD_ERCOT_NOTICES = "/data/methods/ercot_grid_notices#6-on-the-grid-tool-the-notice-state-session-1174-24-october-2026";
export const METHOD_ASK = "/data/methods/grid_network#the-grid-tools-panels-every-figure-keyed-chain-077-23-october-2026";
export const METHOD_STRESS_RAMP = "/data/methods/grid_stress#the-views-figures-keyed-from-the-committed-files-chain-078-24-october-2026";
export const METHOD_STRESS_TIGHT = "/data/methods/grid_stress#the-large-tables-keyed-whole-session-1168";
export const METHOD_STRESS_CALM = "/data/methods/grid_stress#the-large-tables-keyed-whole-session-1168";
export const METHOD_STRESS_GRIDS = "/data/methods/grid_stress#the-views-figures-keyed-from-the-committed-files-chain-078-24-october-2026";
// Session 1185 (chain 091): the Lower 48's view by month of the energy mix panel (grid_mix_us48, mixp=month) is the sum
// of the states (lib/lower48.ts), whose rule is its own section of generation_mix.md: a second link of the mix panel,
// drawn under that view only, beside METHOD_MIX. Not in GRID_METHOD, which is one method a panel.
export const METHOD_MIX_US48 = "/data/methods/generation_mix#the-lower-48-by-month-the-sum-of-the-states-chain-091-24-october-2026";
// Session 1402 (chain 100): the hub's real-time price beside the hourly mix (grid_hubprice_<grid>, under the energy mix
// panel's 7-day chart on the Mix tab, components/grid/HubPricePanel.tsx): its anchor and its method, beside the mix
// panel's. Not in GRID_ANCHOR or GRID_METHOD, whose 17 panels sessions 1183 and 1184 pin; a second grid on one page takes
// the anchor and its grid, as anchorOf writes it (hubPriceAnchor).
export const HUB_PRICE_ANCHOR = "hub-price";
export const hubPriceAnchor = (i: number, grid: string): string => (i ? `${HUB_PRICE_ANCHOR}-${grid}` : HUB_PRICE_ANCHOR);
export const METHOD_HUB_PRICE = "/data/methods/generation_mix_hourly#the-hubs-price-beside-the-hourly-mix-chain-100-24-october-2026";
// Session 1403 (chain 100): the cleanest hours, live (grid_cleanweek_<grid>, beside the Clean tab's committed "the
// cleanest hours of the average day", components/grid/CleanWeekPanel.tsx): its anchor and its method, outside
// GRID_ANCHOR and GRID_METHOD as session 1402's are; a second grid on one page takes the anchor and its grid.
export const CLEAN_WEEK_ANCHOR = "clean-week";
export const cleanWeekAnchor = (i: number, grid: string): string => (i ? `${CLEAN_WEEK_ANCHOR}-${grid}` : CLEAN_WEEK_ANCHOR);
export const METHOD_CLEAN_WEEK = "/data/methods/generation_mix_hourly#the-cleanest-hours-live-chain-100-24-october-2026";
// Session 1406 (chain 100): the Lower 48 on the Network tab, the seven grids' demand and the Lower 48's in the hour, and
// the seven's exchange with the grids around them (inside grid_network_us48, components/grid/Lower48Demand.tsx): its
// anchor and its method, outside GRID_ANCHOR and GRID_METHOD as sessions 1402's and 1403's are; the panel keeps its own
// (#network-figures, METHOD_NETWORK).
export const LOWER48_DEMAND_ANCHOR = "lower48-demand";
export const METHOD_NETWORK_US48 = "/data/methods/grid_network#the-lower-48-on-the-network-tab-chain-100-24-october-2026";
export const GRID_METHOD: Record<GridAnchorKey, string> = {
  network: METHOD_NETWORK,
  replay: METHOD_REPLAY,
  balance: METHOD_BALANCE,
  gravity: METHOD_GRAVITY,
  exchangeGrids: METHOD_EXCHANGE_GRIDS,
  exchangeTies: METHOD_EXCHANGE_TIES,
  exchangeMonths: METHOD_EXCHANGE_MONTHS,
  clean24: METHOD_CLEAN24,
  mix: METHOD_MIX,
  scarcity: METHOD_SCARCITY,
  caisoAlerts: METHOD_CAISO_ALERTS,
  ercotNotices: METHOD_ERCOT_NOTICES,
  ask: METHOD_ASK,
  stressRamp: METHOD_STRESS_RAMP,
  stressTight: METHOD_STRESS_TIGHT,
  stressCalm: METHOD_STRESS_CALM,
  stressGrids: METHOD_STRESS_GRIDS,
};
