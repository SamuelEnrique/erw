// Energy Research Warehouse (ERW) site, session 133: the one energy mix page (/mix), its address and its small helpers.
//
// One tool, one page, one address: /mix holds what /mix, /mix/v2, /mix/clean and /mix/stress showed, as views of one
// page, and the views session 133 added (availability by source, forecast against actual, the long history). The
// whole state of the page is in its address, so any view can be shared. Pure functions; the page and its tests
// (scripts/test-mix.mjs) share them.
import { GRIDS, type GridSlug } from "@/lib/mix2";

export const VIEWS = [
  ["now", "Now and by state"], ["day", "The average day"], ["duck", "Year after year"], ["records", "Records"], ["clean", "How clean, and when"],
  ["stress", "How hard the system works"], ["supply", "Availability by source"], ["forecast", "Wind and solar forecasts"], ["history", "Since 2001"],
] as const;
export type View = (typeof VIEWS)[number][0];
export const FACTORS = [["none", "None"], ["price", "Price"], ["demand", "Demand"], ["temperature", "Temperature"], ["carbon", "Carbon intensity"], ["imports", "Net imports"]] as const;
export type Factor = (typeof FACTORS)[number][0];
export const SEASON_NAMES = [["all", "Whole year"], ["winter", "Winter"], ["spring", "Spring"], ["summer", "Summer"], ["autumn", "Autumn"]] as const;
export const MAX_GRIDS = 4;
export const GRID_COLORS = ["var(--color-accent)", "var(--color-fuel-gas)", "var(--color-fuel-nuclear)", "var(--color-fuel-wind)"];
export const DASHES = ["solid", "dashed", "dotted", "solid"] as const;
export const HOURS = Array.from({ length: 24 }, (_, h) => `${String(h).padStart(2, "0")}:00`);

export type Choice = {
  view: View; grids: GridSlug[]; period: string | null; cal: string | null; year: string | null; season: string; norm: "mw" | "peak"; factor: Factor;
  src: "wind" | "solar"; states: string[]; ba: string | null; state: string | null;
  /** Session 168: the grids "Select grids" shows on the views that open with every grid ("Now and by state",
   *  "Wind and solar forecasts"): every grid unless the address names some. On the other views it is `grids`. */
  shown: GridSlug[];
};
/** Session 168: "Select grids" stands on every view. What each view does with the choice:
 *    compare  draws the grids chosen side by side, four at most (the seven views that always had the control);
 *    filter   opens with every grid and draws only the grids chosen once some are (the opening view and the forecasts);
 *    none     cannot use it: the control is greyed and its hover says why (the history since 2001 is by state). */
export const ALL_GRIDS: GridSlug[] = GRIDS.map((g) => g.slug);
export const gridUse = (view: View): "compare" | "filter" | "none" => (view === "now" || view === "forecast" ? "filter" : view === "history" ? "none" : "compare");
export const NO_GRID_CHOICE = "This view is by state: EIA's record since 2001 is not kept by grid.";
/** The filter views' click: with every grid shown, a click shows that grid alone; a click on the only grid shown
 *  shows every grid again; otherwise the grid is added or taken off. Always in the page's own order of grids. */
export function filtered(shown: GridSlug[], g: GridSlug): GridSlug[] {
  if (shown.length === ALL_GRIDS.length) return [g];
  if (shown.includes(g)) return shown.length === 1 ? ALL_GRIDS : shown.filter((x) => x !== g);
  return ALL_GRIDS.filter((x) => x === g || shown.includes(x));
}
type Query = Record<string, string | string[] | undefined>;
const one = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v);
const isGrid = (g: string): g is GridSlug => GRIDS.some((x) => x.slug === g);

/** What an address asks for. Unknown values fall back to the view's own default; the old pages' own parameters
 *  (grid, vs) are read too, so an address of a retired page still opens the same grids. */
export function choiceOf(q: Query): Choice {
  const view = VIEWS.some(([k]) => k === one(q.view)) ? (one(q.view) as View) : "now";
  const listed = (one(q.grids) ?? "").split(",").filter(isGrid);
  const old = [one(q.grid), one(q.vs)].filter((g): g is string => !!g).filter(isGrid);
  const named = [...new Set([...listed, ...old])];
  // session 168: on a view that opens with every grid, an address naming all seven names none
  const every = gridUse(view) === "filter" && named.length === ALL_GRIDS.length;
  const grids = every ? [] : named.slice(0, MAX_GRIDS);
  const shown = !named.length || every ? ALL_GRIDS : gridUse(view) === "filter" ? ALL_GRIDS.filter((g) => named.includes(g)) : grids;
  const period = one(q.period);
  const factor = FACTORS.some(([k]) => k === one(q.factor)) ? (one(q.factor) as Factor) : "none";
  const states = [...new Set((one(q.states) ?? "").split(",").filter((s) => /^[A-Z]{2}$/.test(s)))].slice(0, MAX_GRIDS);
  return {
    view, grids: grids.length ? grids : ["ercot"], period: period && /^\d{4}(-\d{2})?$/.test(period) ? period : null,
    cal: /^(0[1-9]|1[0-2])$/.test(one(q.cal) ?? "") ? one(q.cal)! : null, year: /^\d{4}$/.test(one(q.year) ?? "") ? one(q.year)! : null,
    season: SEASON_NAMES.some(([k]) => k === one(q.season)) ? one(q.season)! : "all", norm: one(q.norm) === "peak" ? "peak" : "mw", factor,
    src: one(q.src) === "solar" ? "solar" : "wind", states: states.length ? states : ["US"], ba: one(q.ba) ?? null, state: one(q.state) ?? null, shown,
  };
}
/** The address of a choice: only what is not the default is written. */
export function hrefOf(c: Choice, patch: Partial<Choice> = {}): string {
  const n = { ...c, ...patch };
  const q = new URLSearchParams();
  if (n.view !== "now") q.set("view", n.view);
  // session 168: the grids chosen are carried to every view that uses them. Nothing chosen (every grid on the two
  // views that open with every grid, ERCOT alone on the others) writes nothing, so the opening addresses are as they were
  const every = n.shown.length === ALL_GRIDS.length;
  if (n.view === "now") { if (n.ba && every) q.set("ba", n.ba); if (n.state) q.set("state", n.state); }
  else if (n.view === "history") { if (n.states.join(",") !== "US") q.set("states", n.states.join(",")); }
  if (gridUse(n.view) === "filter") { if (!every) q.set("grids", n.shown.join(",")); }
  else if (gridUse(n.view) === "compare" && (n.grids.join(",") !== "ercot" || !every)) q.set("grids", n.grids.join(","));
  if (n.view === "day" && n.period) q.set("period", n.period);
  if (n.view === "duck" && n.cal) q.set("cal", n.cal);
  if (["duck", "records", "clean", "stress", "supply"].includes(n.view) && n.year) q.set("year", n.year);
  if (n.view === "supply" && n.season !== "all") q.set("season", n.season);
  if (["day", "duck", "history"].includes(n.view) && n.norm === "peak") q.set("norm", "peak");
  if (["day", "duck"].includes(n.view) && n.factor !== "none") q.set("factor", n.factor);
  if (n.view === "forecast" && n.src !== "wind") q.set("src", n.src);
  const s = q.toString();
  return s ? `/mix?${s}` : "/mix";
}
/** A grid added to or taken from the selection (at most four; the last one stays). */
export function toggled<T>(list: T[], item: T, max = MAX_GRIDS): T[] {
  if (list.includes(item)) return list.length > 1 ? list.filter((x) => x !== item) : list;
  return list.length < max ? [...list, item] : list;
}
/** Values as a share of a peak, percent; a null stays null. */
export const ofPeak = (v: (number | null)[], peak: number | null) => v.map((x) => (x === null || !peak ? null : Math.round((1000 * x) / peak) / 10));
export const peakOf = (v: (number | null)[] | undefined) => { const s = (v ?? []).filter((x): x is number => x !== null); return s.length ? Math.max(...s) : null; };
export const n0 = (v: number) => Math.round(v).toLocaleString("en-US");
export const n1 = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
export const n2 = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
/** A line's shade for one of n years: from the rule grey of the first to the accent of the last. */
export const yearShade = (i: number, n: number) => (n <= 1 ? "#8C1515" : ["#C9C2B4", "#B5AC9C", "#A19785", "#8E836F", "#7A6E5A", "#665945", "#52442F", "#8C1515"][Math.min(7, Math.round((7 * i) / (n - 1)))]);
export const FUEL_COLOR: Record<string, string> = {
  natural_gas: "var(--color-fuel-gas)", coal: "var(--color-fuel-coal)", nuclear: "var(--color-fuel-nuclear)", wind: "var(--color-fuel-wind)", solar: "var(--color-fuel-solar)",
  hydro: "var(--color-fuel-hydro)", hydro_storage: "var(--color-fuel-hydro)", storage: "var(--color-fuel-storage)", other: "var(--color-fuel-other)",
  other_renewables: "var(--color-fuel-storage)", oil_and_other: "var(--color-fuel-other)", not_itemized: "var(--color-muted)",
};
export const FUEL_WORDS: Record<string, string> = {
  natural_gas: "Natural gas", coal: "Coal", nuclear: "Nuclear", wind: "Wind", solar: "Solar", hydro: "Hydro", storage: "Storage", hydro_storage: "Hydro and storage", other: "Other",
  other_renewables: "Geothermal and biomass", oil_and_other: "Oil and other", not_itemized: "Not itemized by EIA",
};
