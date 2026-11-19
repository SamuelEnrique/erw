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

/** Session 8612 (the second read of the map, row 36): a link of the Network tab followed while the Map or the Gravity
 *  shape is shown keeps that shape. The shape is in the address the reader is at (`shape=map`), written by the network
 *  as it is toggled; the links of a region's list are drawn on the server and do not know it. Given a link and the
 *  address's query, the link with the shape added; the link as it is when the address names no shape, names one this
 *  tool does not have, or the link already names one. */
export function keepShape(href: string, search: string): string {
  const shape = new URLSearchParams(search).get("shape");
  if (shape !== "map" && shape !== "gravity") return href;
  const [path, query = ""] = href.split("?");
  const q = new URLSearchParams(query);
  if (q.has("shape")) return href;
  q.set("shape", shape);
  return `${path}?${q.toString()}`;
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
export function regionOfBa(index: RegionIndex): Record<string, { code: string; name: string; tz?: string }> {
  const names = new Map(index.regions.map((r) => [r.code, r.name]));
  // session 8604: with the authority's own time zone, as the index gives it, so the panel can say its local time
  return Object.fromEntries(index.bas.filter((b) => names.has(b.region)).map((b) => [b.code, { code: b.region, name: names.get(b.region) as string, ...(b.tz ? { tz: b.tz } : {}) }]));
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
  months: Record<string, MixPeriod>; years: Record<string, MixPeriod>; tables?: string[]; method?: string; license?: string; hourly?: MixHourly;
  /** Session 8610 (the contract's line of 19 November, data request 551): the sources no authority of the region has printed in any held hour since July 2018. Each is null all through the file (its averages, its energy, its share, its hourly array), never zero. */
  sources_not_printed?: string[] };

/** Session 8610: the sources a region's file names as never printed, as a list of the page's own keys; empty for a file that names none. */
export function notPrinted(file: Pick<RegionMix, "sources_not_printed"> | null | undefined): string[] {
  const v = file?.sources_not_printed;
  return Array.isArray(v) ? v.filter((k): k is string => typeof k === "string" && (MIX_SOURCES as readonly string[]).includes(k)) : [];
}
/** Session 8610: a region's file as the net load is computed from it. Net load is demand less wind and solar. Where the
 *  file names wind or solar as never printed (no authority of the region has reported it since July 2018), there is none
 *  of it to take from demand, so net load is demand less the one that is reported; an hour of a source that is reported
 *  and not held still leaves the hour's net load blank. The file itself is not changed: this is a copy whose never
 *  printed wind or solar averages read zero, for the net load alone. `absent` names what was left out, for the page to say. */
export function netLoadFile(file: RegionMix): { file: RegionMix; absent: string[] } {
  const absent = notPrinted(file).filter((k) => k === "wind" || k === "solar");
  if (!absent.length) return { file, absent };
  const zero = (p: MixPeriod): MixPeriod => {
    const avg = { ...p.avg };
    for (const k of absent) if (avg[k] === null || avg[k] === undefined) avg[k] = Array.from({ length: 24 }, () => 0);
    return { ...p, avg };
  };
  return { file: { ...file, months: Object.fromEntries(Object.entries(file.months).map(([k, p]) => [k, zero(p)])), years: Object.fromEntries(Object.entries(file.years).map(([k, p]) => [k, zero(p)])) }, absent };
}
/** Session 8610: why a source's figure is blank, said on hover. A source the file names as never printed says so; any
 *  other blank says only that the figure is not held for that hour or period. */
export function whyBlank(label: string, region: string, never: boolean, what = "this hour"): string {
  return never
    ? `No balancing authority of ${region} has reported ${label.toLowerCase()} to EIA in any hour held since July 2018, so the region's file holds none. It is blank, not zero.`
    : `${label} is not held for ${region} in ${what}.`;
}

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
export function lastHours(file: RegionMix, days: number): { from: number; x: string[]; /** session 8605: each hour's start, in milliseconds, for a chart on a time axis */ t: number[]; get: (key: string) => (number | null)[] } | null {
  const h = file.hourly;
  if (!h || !h.hours || !h.hours.n) return null;
  const from = Math.max(0, h.hours.n - days * 24);
  const stamps = Array.from({ length: h.hours.n - from }, (_, k) => hourAt(h.hours, from + k));
  return { from, x: stamps.map((s) => s.slice(0, 13).replace("T", " ")), t: stamps.map((s) => Date.parse(s)), get: (key) => series(h, key).slice(from, h.hours.n).map((v) => (v === undefined ? null : v)) };
}

/** Session 8605: one hour of a stack of sources, drawn as the mix library's own rule says for the average day
 * (lib/mix2.ts `stack`): what is above zero is stacked up from zero, what is below zero (batteries charging, a pumped
 * storage plant pumping, a solar plant's own use at night) down from zero, so such an hour is not hidden inside the
 * stack and no source is drawn across zero. For each source, in the order given: the band it takes, or null when its
 * value is zero or not held. `top` and `bottom` are the stack's two ends. */
export function hourStack(values: (number | null | undefined)[]): { bands: ([number, number] | null)[]; top: number; bottom: number } {
  let top = 0, bottom = 0;
  const bands = values.map((v) => {
    if (v === null || v === undefined || v === 0 || !Number.isFinite(v)) return null;
    if (v > 0) { const band: [number, number] = [top, top + v]; top += v; return band; }
    const band: [number, number] = [bottom + v, bottom]; bottom += v; return band;
  });
  return { bands, top, bottom };
}

/** Session 8605 (the reader's read on the real files: California's chips went from October 2026 to January 2026 with
 * no word): the months from a mix file's first held month to its newest that the file does not hold, oldest first,
 * and how many months that span is. The data machine writes a month when at least 90 percent of its days hold every
 * hour of every source (docs/methods/regions_pages.md); the others are absent from the file, not zero. */
export function monthsNotHeld(file: Pick<RegionMix, "months"> & { built?: string }): { span: number; missing: string[]; /** the whole months after the newest held and before the month the file was built in (the Northwest's file of 19 November 2026 held none of 2026) */ after: string[] } {
  const held = Object.keys(file.months).filter((k) => /^\d{4}-(0[1-9]|1[0-2])$/.test(k)).sort();
  if (!held.length) return { span: 0, missing: [], after: [] };
  const has = new Set(held), missing: string[] = [], after: string[] = [];
  let [y, m] = held[0].split("-").map(Number), span = 0;
  const last = held[held.length - 1];
  const built = typeof file.built === "string" && /^\d{4}-(0[1-9]|1[0-2])/.test(file.built) ? file.built.slice(0, 7) : last;
  for (;;) {
    const k = `${y}-${String(m).padStart(2, "0")}`;
    if (k > last && k >= built) break;
    if (k > last) after.push(k);
    else { span += 1; if (!has.has(k)) missing.push(k); }
    m += 1;
    if (m > 12) { m = 1; y += 1; }
  }
  return { span, missing, after };
}

/** Session 8605: the seven grids that file no battery series in Form EIA-930, by their balancing authority's code, as
 * the Storage page has said since session 34 ("CAISO reports no battery series in EIA-930. NYISO and PJM report none"). */
export const NO_BATTERY_SERIES: Record<string, string> = { CISO: "CAISO", NYIS: "NYISO", PJM: "PJM" };
/** What the Storage row of a region says on hover when one of its balancing authorities files no battery series, or
 * null. A fact of the filing and no reading of the figure. */
export function storageNote(region: { name: string; bas: string[] }): string | null {
  const none = region.bas.filter((b) => NO_BATTERY_SERIES[b]);
  if (!none.length) return null;
  const who = none.map((b) => NO_BATTERY_SERIES[b]).join(" and ");
  const others = region.bas.length - none.length;
  return `${who} files no battery series in Form EIA-930. ${others ? `This row holds what ${region.name}'s other ${others === 1 ? "balancing authority reports" : `${others} balancing authorities report`}` : `It is ${region.name}'s one balancing authority, so this row is the figure the region's file holds`}, not ${who}'s batteries.${none.includes("CISO") ? " CAISO's own battery data is on the Storage page." : ""}`;
}

/** The months a file holds, newest first. */
export const monthsOf = (file: RegionMix) => Object.keys(file.months).sort().reverse();

// ------------------------------------------------------------------ a region's trade (section 5 of the contract)
export type TradeNeighbor = { net_imports_mwh: (number | null)[]; their_report_mwh: (number | null)[]; gap_mwh: (number | null)[]; hours_own: (number | null)[]; hours_their: (number | null)[]; hours_both: (number | null)[] };
export type RegionTrade = { built: string; tables: string[]; method: string; license: string; code: string; name: string; months: string[]; /** the hours of each Eastern month */ hours_in_month?: number[]; net_imports_mwh: (number | null)[]; neighbors: Record<string, TradeNeighbor> };

/** Session 8605 (the reader's read: November 2026 stood beside whole months with 336 of its 721 hours): for a month of
 * a trade file, the most hours any neighbour's row holds of the region's own report, and the hours of the month, when
 * the first is short of the second; null for a whole month, or when the file does not say the month's hours. */
export function partMonth(file: RegionTrade, month: string): { hours: number; of: number } | null {
  const i = file.months.indexOf(month), of = file.hours_in_month?.[i];
  if (i < 0 || typeof of !== "number" || !(of > 0)) return null;
  const hours = Math.max(0, ...Object.values(file.neighbors).map((n) => n.hours_own?.[i] ?? 0));
  return hours < of ? { hours, of } : null;
}

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
