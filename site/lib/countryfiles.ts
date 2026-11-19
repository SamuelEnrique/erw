// Energy Research Warehouse (ERW) site, session 8410 (chain 503): the page files of the whole country, as the data
// machine's contract gives them (docs/state/page_files_regions.md, chain 501): thirteen regions of the lower 48 as
// EIA's Form EIA-930 names them, and every balancing authority, since July 2018. This file holds the names, the
// reader, and what the events pages compute from an event's file. The pages show what the files hold, described:
// sums and means over the hours a file holds, and nothing estimated (no share of a shock covered by imports, no
// ledger of regions that gave and took).
import fs from "node:fs";
import path from "node:path";

/** EIA's thirteen regions of the lower 48, in the contract's order. */
export const REGION_CODES = ["CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NW", "NY", "SE", "SW", "TEN", "TEX"] as const;
export type RegionCode = (typeof REGION_CODES)[number];

/** EIA's names of the regions (EIA-930's reference table). */
export const REGION_NAME: Record<string, string> = {
  CAL: "California", CAR: "Carolinas", CENT: "Central", FLA: "Florida", MIDA: "Mid-Atlantic", MIDW: "Midwest", NE: "New England",
  NW: "Northwest", NY: "New York", SE: "Southeast", SW: "Southwest", TEN: "Tennessee", TEX: "Texas", CAN: "Canada", MEX: "Mexico",
};

/** The six regions no page of the site drew before chain 503: none of the seven grids of the older pages is in them. */
export const NEW_REGIONS: string[] = ["SE", "FLA", "CAR", "TEN", "NW", "SW"];

/** Which of the seven grids of the older pages sits in a region (EIA places each balancing authority in one region).
 *  The index file's `regions[].grids` says the same and is read first where it is held. */
export const REGION_GRIDS: Record<string, string[]> = {
  CAL: ["CISO"], CAR: [], CENT: ["SWPP"], FLA: [], MIDA: ["PJM"], MIDW: ["MISO"], NE: ["ISNE"], NW: [], NY: ["NYIS"], SE: [], SW: [], TEN: [], TEX: ["ERCO"],
};
export const GRID_NAME: Record<string, string> = { ERCO: "ERCOT", CISO: "CAISO", PJM: "PJM", MISO: "MISO", SWPP: "SPP", NYIS: "NYISO", ISNE: "ISO-NE" };

/** The eight sources of generation, in the contract's order, with the words and the colour token of each. */
export const SOURCES: { key: string; label: string; color: string }[] = [
  { key: "natural_gas", label: "Natural gas", color: "var(--color-fuel-gas)" },
  { key: "coal", label: "Coal", color: "var(--color-fuel-coal)" },
  { key: "nuclear", label: "Nuclear", color: "var(--color-fuel-nuclear)" },
  { key: "wind", label: "Wind", color: "var(--color-fuel-wind)" },
  { key: "solar", label: "Solar", color: "var(--color-fuel-solar)" },
  { key: "hydro", label: "Hydro", color: "var(--color-fuel-hydro)" },
  { key: "storage", label: "Storage", color: "var(--color-fuel-storage)" },
  { key: "other", label: "Other", color: "var(--color-fuel-other)" },
];

export type Arr = (number | null)[];
export type Hours = { start: string; step_hours: number; n: number };
export type RegionHours = { demand_mw?: Arr; net_generation_mw?: Arr; net_imports_mw?: Arr; gen?: Record<string, Arr> };
export type RegionEvent = RegionHours & { baseline?: RegionHours };
export type PairEvent = { flow_mw?: Arr; baseline_mw?: Arr };
/** `site/data/regions/events/<event>.json` (the contract's section 6). */
export type EventRegionsFile = {
  built?: string; tables?: string[]; method?: string; license?: string; fixture?: string;
  event: string; title?: string; start: string; end: string;
  baseline?: string | { how?: string; text?: string; rule?: string; baseline_offsets_days?: number[] };
  baseline_offsets_days?: number[];
  hours: Hours;
  regions: Record<string, RegionEvent>;
  pairs?: Record<string, PairEvent>;
};

/** The folder of the page files. ERW_REGIONS_DIR stands in for it in a test, and only there. */
export function regionsDir(): string {
  return process.env.ERW_REGIONS_DIR ?? path.join(process.cwd(), "data", "regions");
}

/** One page file of the whole country, or null while the data machine has not written it (or it cannot be read as
 *  JSON). A file that says it is a test's fixture is never read from the site's own folder. */
export function readRegionFile<T>(rel: string): T | null {
  const at = path.join(regionsDir(), ...rel.split("/"));
  try {
    if (!fs.existsSync(at)) return null;
    const v = JSON.parse(fs.readFileSync(at, "utf8")) as T & { fixture?: string };
    if (v && typeof v === "object" && "fixture" in v && v.fixture && !process.env.ERW_REGIONS_DIR) return null;
    return v;
  } catch {
    return null;
  }
}
export const eventRegionsFile = (event: string) => readRegionFile<EventRegionsFile>(`events/${event}.json`);

/** How the file says its baseline is formed, in its own words, and the offsets in days. */
export function baselineOf(file: EventRegionsFile): { words: string; offsets: number[] } {
  const b = file.baseline;
  const words = typeof b === "string" ? b : b ? b.how ?? b.text ?? b.rule ?? "" : "";
  const offsets = file.baseline_offsets_days ?? (typeof b === "object" && b ? b.baseline_offsets_days ?? [] : []);
  return { words, offsets };
}

const num = (v: number | null | undefined): v is number => typeof v === "number" && Number.isFinite(v);
/** The start of hour `i` of the file, UTC, as the file writes its hours ("2022-12-23T05:00:00Z"). */
export function hourAt(hours: Hours, i: number): string {
  return new Date(Date.parse(hours.start) + i * (hours.step_hours || 1) * 3_600_000).toISOString().replace(".000Z", "Z");
}

export type Against = { hours: number; mwh: number; base_mwh: number; diff_mwh: number; pct: number | null; mean_mw: number; base_mean_mw: number };
/** A series over the window against its baseline, over the hours both hold: the energy of each (MW over an hour is
 *  MWh), the difference, the percent (null when the baseline's sum is zero) and the two means. Null when no hour is
 *  held by both. */
export function against(event: Arr | undefined, base: Arr | undefined, step = 1): Against | null {
  if (!event || !base) return null;
  let hours = 0, a = 0, b = 0;
  for (let i = 0; i < Math.min(event.length, base.length); i++) {
    const x = event[i], y = base[i];
    if (num(x) && num(y)) { hours++; a += x; b += y; }
  }
  if (!hours) return null;
  return { hours, mwh: a * step, base_mwh: b * step, diff_mwh: (a - b) * step, pct: b !== 0 ? ((a - b) / Math.abs(b)) * 100 : null, mean_mw: a / hours, base_mean_mw: b / hours };
}

export type Peak = { mw: number; at: string; base_mw: number | null };
/** The highest held hour of a series, when it was (UTC), and the baseline at that same hour (null when not held). */
export function peakOf(event: Arr | undefined, base: Arr | undefined, hours: Hours): Peak | null {
  if (!event) return null;
  let best = -1;
  for (let i = 0; i < event.length; i++) { const v = event[i]; if (num(v) && (best < 0 || v > (event[best] as number))) best = i; }
  if (best < 0) return null;
  const b = base?.[best];
  return { mw: event[best] as number, at: hourAt(hours, best), base_mw: num(b) ? b : null };
}

export type RegionSummary = {
  code: string; name: string; isNew: boolean; grids: string[]; held: boolean;
  demand: Against | null; peak: Peak | null; imports: Against | null; generation: Against | null; sources: Record<string, Against | null>;
  hoursHeld: number;
};
/** Every region of the file's window, in EIA's order: what demand, generation by source and net imports did against the
 *  baseline. A region the file does not hold is returned with `held` false and nothing else. */
export function summarize(file: EventRegionsFile): RegionSummary[] {
  const step = file.hours.step_hours || 1;
  return REGION_CODES.map((code) => {
    const r = file.regions?.[code];
    const base = r?.baseline;
    const sources = Object.fromEntries(SOURCES.map((s) => [s.key, against(r?.gen?.[s.key], base?.gen?.[s.key], step)]));
    const demand = against(r?.demand_mw, base?.demand_mw, step);
    return {
      code, name: REGION_NAME[code], isNew: NEW_REGIONS.includes(code), grids: REGION_GRIDS[code] ?? [], held: !!r,
      demand, peak: peakOf(r?.demand_mw, base?.demand_mw, file.hours), imports: against(r?.net_imports_mw, base?.net_imports_mw, step),
      generation: against(r?.net_generation_mw, base?.net_generation_mw, step), sources,
      hoursHeld: (r?.demand_mw ?? []).filter(num).length,
    };
  });
}

/** The share of the baseline by which a region's demand over the window must differ from it to be counted as reached,
 *  in percent, either way. The session's own default (8410): no publisher's threshold stands behind it. */
export const REACHED_PCT = 5;
/** The regions whose demand over the window stood REACHED_PCT percent or more from the baseline, above or below. */
export function reached(rows: RegionSummary[], threshold = REACHED_PCT): RegionSummary[] {
  return rows.filter((r) => r.demand && r.demand.pct !== null && Math.abs(r.demand.pct) >= threshold);
}

export type PairSummary = {
  key: string; a: string; b: string; hours: number; mean_mw: number; mwh: number;
  /** who sent and who took over the window, by the sign of the window's sum; both null when the sum is zero */
  sent: string | null; took: string | null;
  base: { hours: number; mean_mw: number; mwh: number; sent: string | null; took: string | null } | null;
};
/** Each pair of regions of the file, largest energy over the window first: power from the first code to the second is
 *  positive in the file, so the sign of the window's sum says which sent and which took. The baseline beside it. */
export function pairs(file: EventRegionsFile): PairSummary[] {
  const step = file.hours.step_hours || 1;
  const out: PairSummary[] = [];
  for (const [key, p] of Object.entries(file.pairs ?? {})) {
    const [a, b] = key.split("-");
    if (!a || !b) continue;
    const side = (arr: Arr | undefined) => {
      const xs = (arr ?? []).filter(num);
      if (!xs.length) return null;
      const sum = xs.reduce((s, v) => s + v, 0);
      return { hours: xs.length, mean_mw: sum / xs.length, mwh: sum * step, sent: sum > 0 ? a : sum < 0 ? b : null, took: sum > 0 ? b : sum < 0 ? a : null };
    };
    const ev = side(p.flow_mw);
    if (!ev) continue;
    out.push({ key, a, b, ...ev, base: side(p.baseline_mw) });
  }
  return out.sort((x, y) => Math.abs(y.mwh) - Math.abs(x.mwh) || x.key.localeCompare(y.key));
}

/** A region code from a query value ("ten", "TEN"), or null when it is none of the thirteen. */
export function regionOf(v: string | undefined): string | null {
  const c = (v ?? "").toUpperCase();
  return (REGION_CODES as readonly string[]).includes(c) ? c : null;
}

/** The points of a chart from an hourly array: by hour while the window is at most `byDayOver` days long, else the
 *  mean of each UTC day's held hours (a day with no held hour has no point). t in seconds. */
export function points(arr: Arr | undefined, hours: Hours, byDayOver = 21): { t: number; v: number }[] {
  if (!arr) return [];
  const t0 = Date.parse(hours.start) / 1000, step = (hours.step_hours || 1) * 3600;
  if (hours.n * (hours.step_hours || 1) <= byDayOver * 24) {
    const out: { t: number; v: number }[] = [];
    arr.forEach((v, i) => { if (num(v)) out.push({ t: t0 + i * step, v }); });
    return out;
  }
  const days = new Map<number, { s: number; n: number }>();
  arr.forEach((v, i) => {
    if (!num(v)) return;
    const d = Math.floor((t0 + i * step) / 86_400) * 86_400;
    const g = days.get(d) ?? { s: 0, n: 0 };
    g.s += v; g.n++;
    days.set(d, g);
  });
  return [...days.entries()].sort((x, y) => x[0] - y[0]).map(([t, g]) => ({ t, v: g.s / g.n }));
}
export const drawnByDay = (hours: Hours, byDayOver = 21) => hours.n * (hours.step_hours || 1) > byDayOver * 24;

/** Whole megawatts and megawatt-hours with thousands separators; gigawatt-hours with one decimal; a signed percent. */
export const whole = (v: number) => Math.round(v).toLocaleString("en-US");
export const gwh = (mwh: number) => (mwh / 1000).toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
export const signedGwh = (mwh: number) => `${mwh > 0 ? "+" : ""}${gwh(mwh)}`;
export const signedPct = (v: number) => `${v > 0 ? "+" : ""}${v.toFixed(1)}`;
export const signedWhole = (v: number) => `${Math.round(v) > 0 ? "+" : ""}${whole(v)}`;
/** "2022-12-23 23:00 UTC" from the file's hour. */
export const utcHour = (ts: string) => `${ts.slice(0, 10)} ${ts.slice(11, 16)} UTC`;
