// Energy Research Warehouse (ERW) site, session 105: the project map, version 2 (/map/v2, in review).
//
// Every operating and planned generating unit of EIA's monthly inventory (Form EIA-860M), batteries among them, from
// the site's copy of the two tables (data/map_v2.json, written by warehouse/derived/project_map.py). Pure functions
// over that file: which units a choice of grid, technology, status and size selects, their totals, and the queue's
// active capacity for the same grid (data/queues.json, Berkeley Lab's file as session 95 summarized it).

export type MapFile = {
  tables: string[]; vintage: string; retrieved: string; source_url: string; built: string;
  grids: { slug: string; name: string }[]; techs: { slug: string; name: string }[]; statuses: { slug: string; name: string }[];
  states: string[]; names: string[]; counts: Record<string, number>;
  n: number[]; s: number[]; g: number[]; t: number[]; st: number[]; mw: number[]; y: number[]; la: (number | null)[]; lo: (number | null)[];
};
/** What the browser gets: the file's columns with each unit's place on the map's plane (null when the projection has
 *  no place for it: Puerto Rico), in place of its latitude and longitude. */
export type MapData = Omit<MapFile, "la" | "lo"> & { x: (number | null)[]; y2: (number | null)[]; statesGeo: unknown; width: number; height: number };

export type Choice = { grid: number; tech: number; status: number; min: number; max: number };   // -1: every grid, technology or status
export const EVERY: Choice = { grid: -1, tech: -1, status: -1, min: 0, max: Infinity };

/** A size typed by the reader: a number at or above zero, or nothing (the bound is then open). */
export function sizeOf(text: string, open: number): number {
  const t = text.trim().replace(/,/g, "");
  if (!/^\d+(\.\d+)?$/.test(t)) return open;
  return Number(t);
}

/** The positions of the units a choice selects, in the file's order (largest first). */
export function select(f: Pick<MapFile, "g" | "t" | "st" | "mw">, c: Choice): number[] {
  const out: number[] = [];
  for (let i = 0; i < f.mw.length; i++) {
    if (c.grid >= 0 && f.g[i] !== c.grid) continue;
    if (c.tech >= 0 && f.t[i] !== c.tech) continue;
    if (c.status >= 0 && f.st[i] !== c.status) continue;
    if (f.mw[i] < c.min || f.mw[i] > c.max) continue;
    out.push(i);
  }
  return out;
}

export type Totals = { units: number; mw: number; byStatus: { units: number; mw: number }[] };
export function totals(f: Pick<MapFile, "st" | "mw" | "statuses">, picked: number[]): Totals {
  const byStatus = f.statuses.map(() => ({ units: 0, mw: 0 }));
  let mw = 0;
  for (const i of picked) { mw += f.mw[i]; byStatus[f.st[i]].units += 1; byStatus[f.st[i]].mw += f.mw[i]; }
  return { units: picked.length, mw, byStatus };
}

// The queue beside the inventory. Berkeley Lab's file has its own regions and its own technologies; nothing is added
// across the two sources. A grid of the map is one region of the queue; "outside the seven ISOs" is its two regions
// outside them, shown apart; every grid is its row for all regions.
export const QUEUE_REGIONS: Record<string, { slug: string; name: string }[]> = {
  all: [{ slug: "us", name: "All regions" }],
  ercot: [{ slug: "ercot", name: "ERCOT" }], caiso: [{ slug: "caiso", name: "CAISO" }], pjm: [{ slug: "pjm", name: "PJM" }], miso: [{ slug: "miso", name: "MISO" }],
  spp: [{ slug: "spp", name: "SPP" }], nyiso: [{ slug: "nyiso", name: "NYISO" }], isone: [{ slug: "isone", name: "ISO-NE" }],
  outside: [{ slug: "west", name: "West, outside the ISOs" }, { slug: "southeast", name: "Southeast, outside the ISOs" }],
};
export const QUEUE_TECHS: { slug: string; name: string }[] = [
  { slug: "all", name: "All technologies" }, { slug: "solar", name: "Solar" }, { slug: "solar_battery", name: "Solar with storage" },
  { slug: "battery", name: "Storage (batteries alone)" }, { slug: "wind", name: "Wind" }, { slug: "offshore_wind", name: "Offshore wind" },
  { slug: "gas", name: "Natural gas" }, { slug: "other", name: "Everything else" },
];
/** The queue's technologies that answer to one of the map's (the rows the page marks when a technology is chosen). */
export const QUEUE_FOR_TECH: Record<string, string[]> = {
  solar: ["solar", "solar_battery"], wind: ["wind", "offshore_wind"], battery: ["battery", "solar_battery"], natural_gas: ["gas"],
  storage: ["other"], nuclear: ["other"], coal: ["other"], hydro: ["other"], petroleum: ["other"], biomass: ["other"], geothermal: ["other"], other: ["other"], unknown: [],
};
export type QueueViews = Record<string, { whole: { total_active_requests: number; total_active_mw: number } }>;
export type QueueRow = { region: string; tech: string; slug: string; requests: number | null; mw: number | null; marked: boolean };
/** The queue's active requests and MW for a grid of the map, one row a region and technology; null where the file
 *  holds no request of that kind in that region. */
export function queueRows(views: QueueViews, grid: string, tech: string): QueueRow[] {
  const marked = new Set(tech === "all" ? [] : QUEUE_FOR_TECH[tech] ?? []);
  return (QUEUE_REGIONS[grid] ?? []).flatMap((r) => QUEUE_TECHS.map((t) => {
    const w = views[`${r.slug}|${t.slug}`]?.whole;
    return { region: r.name, tech: t.name, slug: t.slug, requests: w ? w.total_active_requests : null, mw: w ? w.total_active_mw : null, marked: marked.has(t.slug) };
  }));
}

export const whole = (v: number) => Math.round(v).toLocaleString("en-US");
export const one = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
/** The fuel color of a technology of the map: the site's eight, the rest share "other" (a ninth hue is never made). */
export const COLOR: Record<string, string> = {
  solar: "--color-fuel-solar", wind: "--color-fuel-wind", battery: "--color-fuel-storage", storage: "--color-fuel-other", natural_gas: "--color-fuel-gas",
  nuclear: "--color-fuel-nuclear", coal: "--color-fuel-coal", hydro: "--color-fuel-hydro", petroleum: "--color-fuel-other", biomass: "--color-fuel-other",
  geothermal: "--color-fuel-other", other: "--color-fuel-other", unknown: "--color-fuel-other",
};
