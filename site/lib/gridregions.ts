// Energy Research Warehouse (ERW) site, session 8602 (chain 504, 19 November 2026): the whole country in the Grid tool.
// EIA's thirteen regions of the lower 48 beside the seven grids and the Lower 48 of the picker, read from the whole
// country's page files (data/regions/, written by the data machine; the contract docs/state/page_files_regions.md).
// The parts with no drawing and no file reading in them, so the page and a test in Node read this file as it is.
// No imports.
//
// The address: /grid?region=<code>&view=<view>. `region` is a word of its own, so every address the tool had
// (/grid?grid=ercot&view=mix and the rest, lib/gridtool.ts) reads exactly as it did: gridPick is not touched. A region
// is in view only when the address names one the index holds.

/** EIA's codes of the thirteen regions, in the contract's order, with EIA's names. */
export const REGIONS = [
  ["CAL", "California"], ["CAR", "Carolinas"], ["CENT", "Central"], ["FLA", "Florida"], ["MIDA", "Mid-Atlantic"], ["MIDW", "Midwest"], ["NE", "New England"],
  ["NW", "Northwest"], ["NY", "New York"], ["SE", "Southeast"], ["SW", "Southwest"], ["TEN", "Tennessee"], ["TEX", "Texas"],
] as const;
export type RegionCode = (typeof REGIONS)[number][0];
export const REGION_KEY = "region";
/** The six regions no page of the site drew before the whole country's files: none of the seven grids is among their balancing authorities. */
export const NEW_REGIONS: readonly RegionCode[] = ["SE", "FLA", "CAR", "TEN", "NW", "SW"];
/** Where a region and one of the seven grids cover nearly the same ground (the contract, section 3, `alike`): the region's code and the grid's balancing authority code and name. */
export const ALIKE: Partial<Record<RegionCode, { ba: string; grid: string }>> = { TEX: { ba: "ERCO", grid: "ERCOT" }, NY: { ba: "NYIS", grid: "NYISO" }, NE: { ba: "ISNE", grid: "ISO-NE" }, MIDA: { ba: "PJM", grid: "PJM" } };

/** A region by the word an address uses for it: EIA's code, in any case. */
export function regionBy(word: string | string[] | undefined | null): RegionCode | null {
  const w = (Array.isArray(word) ? word[0] : word ?? "").trim().toUpperCase();
  return (REGIONS.find(([code]) => code === w)?.[0] ?? null) as RegionCode | null;
}
export const regionName = (code: string) => REGIONS.find(([c]) => c === code)?.[1] ?? code;

export type RegionView = "network" | "mix" | "clean" | "gravity";
/** The address of a region and a view; the Mix tab, which the tool opens on, is not written. `more` adds a view's own state. */
export function regionHref(code: string, view: RegionView = "mix", more: Record<string, string | undefined> = {}): string {
  const q = new URLSearchParams();
  q.set(REGION_KEY, code.toLowerCase());
  if (view !== "mix") q.set("view", view);
  for (const [k, v] of Object.entries(more)) if (v !== undefined && v !== "") q.set(k, v);
  return `/grid?${q.toString()}`;
}

// ------------------------------------------------------------------ the index (section 2 of the contract)
export type IndexRegion = { code: string; name: string; tz: string; bas: string[]; grids: string[]; first_hour?: string; last_hour?: string };
export type IndexBa = { code: string; name: string; region: string; tz?: string; grid?: string | null; region_grids?: string[]; generation_only?: boolean; active?: boolean; retired?: string | null; first_hour?: string; last_hour?: string; files?: string[] };
export type RegionIndex = { built: string; tables: string[]; method: string; license: string; regions: IndexRegion[]; bas: IndexBa[] };

/** The index as the page uses it, or null for anything that is not the index whole (no list of regions, a region with no code, name or list of authorities). */
export function readIndex(v: unknown): RegionIndex | null {
  const f = v as Partial<RegionIndex> | null;
  if (!f || typeof f !== "object" || !Array.isArray(f.regions) || !Array.isArray(f.bas) || typeof f.built !== "string") return null;
  for (const r of f.regions) if (!r || typeof r.code !== "string" || typeof r.name !== "string" || !Array.isArray(r.bas)) return null;
  for (const b of f.bas) if (!b || typeof b.code !== "string" || typeof b.region !== "string") return null;
  return { built: f.built, tables: Array.isArray(f.tables) ? f.tables : [], method: typeof f.method === "string" ? f.method : "", license: typeof f.license === "string" ? f.license : "", regions: f.regions, bas: f.bas };
}

/** Each balancing authority's region, for the network's panel and the map's hover: { TVA: { code: "TEN", name: "Tennessee" } }. */
export function regionOfBa(index: RegionIndex): Record<string, { code: string; name: string }> {
  const names = new Map(index.regions.map((r) => [r.code, r.name]));
  return Object.fromEntries(index.bas.filter((b) => names.has(b.region)).map((b) => [b.code, { code: b.region, name: names.get(b.region) as string }]));
}

// ------------------------------------------------------------------ hourly arrays (the contract's common rules)
export type Hours = { start: string; step_hours: number; n: number };
/** The hour of a position: the start plus the position's hours, as the files write a time ("2025-08-01T19:00:00Z"). */
export function hourAt(hours: Hours, i: number): string {
  return new Date(Date.parse(hours.start) + i * hours.step_hours * 3_600_000).toISOString().replace(".000Z", "Z");
}

// ------------------------------------------------------------------ a region's mix (section 4 of the contract)
/** The eight sources, in the contract's order (the order of data/mix/*.json). */
export const MIX_SOURCES = ["natural_gas", "coal", "nuclear", "wind", "solar", "hydro", "storage", "other"] as const;
export type MixHourly = { hours: Hours } & Record<string, (number | null)[] | Hours>;
export type MixPeriod = { avg: Record<string, (number | null)[]>; side: string; days_held: number; days_in_month?: number } & Record<string, unknown>;
export type RegionMix = { grid: string; name: string; tz: string; built: string; join: string | null; first: string; upto: string; sources: string[];
  months: Record<string, MixPeriod>; years: Record<string, MixPeriod>; tables?: string[]; method?: string; license?: string; hourly?: MixHourly };

/** A region's mix file as the page uses it, or null for anything that is not that file (no months, or no list of sources). */
export function readMix(v: unknown): RegionMix | null {
  const f = v as Partial<RegionMix> | null;
  if (!f || typeof f !== "object" || typeof f.months !== "object" || !f.months || typeof f.years !== "object" || !Array.isArray(f.sources) || typeof f.name !== "string" || typeof f.tz !== "string") return null;
  return f as RegionMix;
}

const series = (h: MixHourly | undefined, key: string): (number | null)[] => { const v = h?.[key]; return Array.isArray(v) ? v : []; };

/** The newest hour of the hourly part that holds a net generation: its position, its time, and each figure at it (null where not held). */
export function latestHour(file: RegionMix): { i: number; ts: string; demand: number | null; net_generation: number | null; net_imports: number | null; sources: { key: string; mw: number | null; share_pct: number | null }[] } | null {
  const h = file.hourly;
  if (!h || !h.hours || typeof h.hours.n !== "number") return null;
  const gen = series(h, "net_generation");
  let i = Math.min(h.hours.n, gen.length) - 1;
  while (i >= 0 && (gen[i] === null || gen[i] === undefined)) i -= 1;
  if (i < 0) return null;
  const at = (key: string) => { const v = series(h, key)[i]; return v === null || v === undefined ? null : v; };
  const total = gen[i] as number;
  return { i, ts: hourAt(h.hours, i), demand: at("demand"), net_generation: total, net_imports: at("net_imports"),
    sources: MIX_SOURCES.map((key) => { const mw = at(key); return { key, mw, share_pct: mw === null || !total ? null : Math.round((mw / total) * 10000) / 100 }; }) };
}

/** The hourly part cut to its last `days` days, by position: the labels of the hours (UTC) and each series; null where there is no hourly part. */
export function lastHours(file: RegionMix, days: number): { from: number; x: string[]; get: (key: string) => (number | null)[] } | null {
  const h = file.hourly;
  if (!h || !h.hours || !h.hours.n) return null;
  const from = Math.max(0, h.hours.n - days * 24);
  const x = Array.from({ length: h.hours.n - from }, (_, k) => hourAt(h.hours, from + k).slice(0, 13).replace("T", " "));
  return { from, x, get: (key) => series(h, key).slice(from, h.hours.n).map((v) => (v === undefined ? null : v)) };
}

/** The months a file holds, newest first. */
export const monthsOf = (file: RegionMix) => Object.keys(file.months).sort().reverse();

// ------------------------------------------------------------------ a region's trade (section 5 of the contract)
export type TradeNeighbor = { net_imports_mwh: (number | null)[]; their_report_mwh: (number | null)[]; gap_mwh: (number | null)[]; hours_own: (number | null)[]; hours_their: (number | null)[]; hours_both: (number | null)[] };
export type RegionTrade = { built: string; tables: string[]; method: string; license: string; code: string; name: string; months: string[]; net_imports_mwh: (number | null)[]; neighbors: Record<string, TradeNeighbor> };

export function readTrade(v: unknown): RegionTrade | null {
  const f = v as Partial<RegionTrade> | null;
  if (!f || typeof f !== "object" || !Array.isArray(f.months) || !Array.isArray(f.net_imports_mwh) || typeof f.neighbors !== "object" || !f.neighbors) return null;
  return f as RegionTrade;
}

/** One month of a region's trade: the total (null when any neighbour is short of half its hours, as the file writes it) and each neighbour's row, the largest flow first, either way. */
export function tradeMonth(file: RegionTrade, month: string): { month: string; total: number | null; rows: { code: string; own: number | null; theirs: number | null; gap: number | null; hoursOwn: number | null; hoursTheir: number | null; hoursBoth: number | null }[] } | null {
  const i = file.months.indexOf(month);
  if (i < 0) return null;
  const at = (v: (number | null)[] | undefined) => (v && v[i] !== undefined ? v[i] : null);
  const rows = Object.entries(file.neighbors).map(([code, n]) => ({ code, own: at(n.net_imports_mwh), theirs: at(n.their_report_mwh), gap: at(n.gap_mwh), hoursOwn: at(n.hours_own), hoursTheir: at(n.hours_their), hoursBoth: at(n.hours_both) }))
    .sort((a, b) => Math.abs(b.own ?? 0) - Math.abs(a.own ?? 0) || a.code.localeCompare(b.code));
  return { month, total: at(file.net_imports_mwh), rows };
}

/** The newest month in which any neighbour's own report is held. */
export function newestTradeMonth(file: RegionTrade): string | null {
  for (let i = file.months.length - 1; i >= 0; i -= 1) if (Object.values(file.neighbors).some((n) => n.net_imports_mwh?.[i] !== null && n.net_imports_mwh?.[i] !== undefined)) return file.months[i];
  return null;
}

/** A neighbour's name: a region's, or Canada and Mexico, which the trade files name by CAN and MEX. */
export const neighborName = (code: string) => (code === "CAN" ? "Canada" : code === "MEX" ? "Mexico" : regionName(code));

// ------------------------------------------------------------------ a region beside the grid it nearly is (section 3 of the contract, `alike`)
export type Alike = { grid: string; years: Record<string, { region_avg_demand_mw: number; grid_avg_demand_mw: number; difference_pct: number }>; why: string };
/** The `alike` object of a region's demand file, or null when the file holds none. */
export function readAlike(v: unknown): Alike | null {
  const a = (v as { alike?: Partial<Alike> } | null)?.alike;
  if (!a || typeof a.grid !== "string" || typeof a.why !== "string" || !a.why.trim()) return null;
  return { grid: a.grid, years: (a.years ?? {}) as Alike["years"], why: a.why.trim() };
}
/** The one sentence of a hover: the first sentence of the file's own `why`. */
export function whySentence(a: Alike): string {
  const m = a.why.match(/^.*?[.!?](?=\s|$)/);
  return (m ? m[0] : a.why).trim();
}
