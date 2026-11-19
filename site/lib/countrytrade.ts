// Energy Research Warehouse (ERW) site, session 8430 (chain 503, part D): the trade, matrix and mix files of the whole
// country, as the data machine's contract gives them (docs/state/page_files_regions.md, sections 4, 5 and 7), for
// /supply. This file holds their types, their readers and the sums the page draws: a year's sum of the months a file
// holds, the gap between two sides' reports of one flow as a percent of their mean size, a year's share of generation
// by source. The names, the reader of the folder and the formats are session 8410's (lib/countryfiles.ts). The page
// shows what the files hold, described: each pair's own flow and each region's own months. Nothing is filled, scaled
// or estimated; no region is summed against another, and no ledger of regions that gave and took is formed.
import { REGION_CODES, REGION_NAME, SOURCES, readRegionFile, type Arr } from "./countryfiles";

/** The thirteen regions and the two neighbours outside the lower 48, in the contract's order. */
export const NEIGHBOUR_CODES: string[] = [...REGION_CODES, "CAN", "MEX"];
/** The first month EIA's Form EIA-930 holds. */
export const FIRST_MONTH = "2018-07";

export type FileHead = { built?: string; tables?: string[]; method?: string; license?: string; fixture?: string };
export type TradeNeighbour = { net_imports_mwh?: Arr; their_report_mwh?: Arr; gap_mwh?: Arr; hours_own?: Arr; hours_their?: Arr; hours_both?: Arr };
/** `site/data/regions/trade/<region>.json` (the contract's section 5). */
export type TradeFile = FileHead & { code: string; name?: string; months: string[]; net_imports_mwh?: Arr; neighbors?: Record<string, TradeNeighbour> };
export type PairRow = { a: string; b: string; year: number | string; a_report_mwh?: number | null; b_report_mwh?: number | null; mean_mwh?: number | null; gap_mwh?: number | null; direction?: string | null };
export type Partners = { by_gross?: string[]; by_net?: string[]; net_import_share_of_demand_pct?: number | null };
/** `site/data/regions/trade_matrix.json` (the contract's section 7). */
export type MatrixFile = FileHead & { years?: (number | string)[]; regions?: string[]; region_pairs?: PairRow[]; ba_pairs?: PairRow[]; partners?: Record<string, Record<string, Partners>> };
export type MixMonth = { net_generation_mwh?: number | null; days_held?: number; days_in_month?: number; side?: string; avg?: Record<string, Arr> } & Record<string, unknown>;
/** `site/data/regions/mix/<region>.json` (the contract's section 4). */
export type MixFile = FileHead & { grid: string; name?: string; tz?: string; first?: string; upto?: string; sources?: string[]; months?: Record<string, MixMonth>; years?: Record<string, unknown>; hourly?: unknown };
/** `site/data/regions/index.json` (the contract's section 2), read here only for the names of the balancing authorities. */
export type IndexFile = FileHead & { regions?: { code: string; name?: string; bas?: string[]; grids?: string[] }[]; bas?: { code: string; name?: string; region?: string; grid?: string | null }[] };

export const tradeFile = (code: string) => readRegionFile<TradeFile>(`trade/${code.toLowerCase()}.json`);
export const mixFile = (code: string) => readRegionFile<MixFile>(`mix/${code.toLowerCase()}.json`);
export const matrixFile = () => readRegionFile<MatrixFile>("trade_matrix.json");
export const indexFile = () => readRegionFile<IndexFile>("index.json");
/** What the section reads: the four readers above, or a test's own. */
export type Readers = { trade: (code: string) => TradeFile | null; mix: (code: string) => MixFile | null; matrix: () => MatrixFile | null; index: () => IndexFile | null };
export const READERS: Readers = { trade: tradeFile, mix: mixFile, matrix: matrixFile, index: indexFile };

const num = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
/** A region's or a neighbour's name ("Tennessee", "Canada"); the code itself when it is neither. */
export const placeName = (code: string) => REGION_NAME[code] ?? code;
const place = (code: string) => { const i = NEIGHBOUR_CODES.indexOf(code); return i < 0 ? NEIGHBOUR_CODES.length : i; };
/** Codes in the contract's order (the thirteen, Canada, Mexico), any other code after them by its letters. */
export const inOrder = (codes: string[]) => [...codes].sort((x, y) => place(x) - place(y) || x.localeCompare(y));

/** The positions of a year's months in a file's list of months ("2025" in ["2024-12", "2025-01", ...]). */
export function monthsOfYear(months: string[] | undefined, year: string): number[] {
  const out: number[] = [];
  (months ?? []).forEach((m, i) => { if (m.slice(0, 4) === year) out.push(i); });
  return out;
}
/** The calendar years a list of months touches, oldest first. */
export const yearsOf = (months: string[] | undefined) => [...new Set((months ?? []).map((m) => m.slice(0, 4)))].sort();

export type Sum = { mwh: number; held: number; of: number };
/** The sum of an array over the positions given, over the ones it holds: `held` of `of`. Null when it holds none. A
 *  month that is not held is left out and counted, never filled. */
export function sumOver(arr: Arr | undefined, at: number[]): Sum | null {
  let mwh = 0, held = 0;
  for (const i of at) { const v = arr?.[i]; if (num(v)) { mwh += v; held++; } }
  return held ? { mwh, held, of: at.length } : null;
}

/** The share of the mean size of two reports of one flow that the gap between them must reach to be called large on
 *  the page, in percent. The session's own default (8430): no publisher's threshold stands behind it. */
export const LARGE_GAP_PCT = 10;
/** The gap between two reports of one flow as a percent of their mean size (the mean of their absolute values). Null
 *  when one of the three is not held or both reports are zero. */
export function gapPct(gap: number | null | undefined, one: number | null | undefined, other: number | null | undefined): number | null {
  if (!num(gap) || !num(one) || !num(other)) return null;
  const size = (Math.abs(one) + Math.abs(other)) / 2;
  return size > 0 ? (Math.abs(gap) / size) * 100 : null;
}
export const isLarge = (pct: number | null, threshold = LARGE_GAP_PCT) => pct !== null && pct >= threshold;

export type NeighbourYear = {
  code: string; name: string;
  /** the region's own report, the neighbour's report and the gap, each summed over the months of the year it holds */
  own: Sum | null; their: Sum | null; gap: Sum | null;
  /** the gap as a percent of the two reports' mean size, over the months of the year that hold all three */
  pct: number | null; large: boolean; compared: number;
  hoursOwn: Sum | null; hoursTheir: Sum | null; hoursBoth: Sum | null;
};
/** One region's year with each of its neighbours, in the contract's order. */
export function neighboursOfYear(file: TradeFile, year: string, threshold = LARGE_GAP_PCT): NeighbourYear[] {
  const at = monthsOfYear(file.months, year);
  return inOrder(Object.keys(file.neighbors ?? {})).map((code) => {
    const n = file.neighbors![code];
    const all = at.filter((i) => num(n.net_imports_mwh?.[i]) && num(n.their_report_mwh?.[i]) && num(n.gap_mwh?.[i]));
    const o = sumOver(n.net_imports_mwh, all), t = sumOver(n.their_report_mwh, all), g = sumOver(n.gap_mwh, all);
    const pct = o && t && g ? gapPct(g.mwh, o.mwh, t.mwh) : null;
    return {
      code, name: placeName(code), own: sumOver(n.net_imports_mwh, at), their: sumOver(n.their_report_mwh, at), gap: sumOver(n.gap_mwh, at),
      pct, large: isLarge(pct, threshold), compared: all.length,
      hoursOwn: sumOver(n.hours_own, at), hoursTheir: sumOver(n.hours_their, at), hoursBoth: sumOver(n.hours_both, at),
    };
  });
}
/** One region's net imports from all its neighbours over a year, from the file's own total (a month the file leaves
 *  null, because a neighbour was short of half its hours, is left out and counted). */
export const totalOfYear = (file: TradeFile, year: string) => sumOver(file.net_imports_mwh, monthsOfYear(file.months, year));

export type MonthCell = { own: number | null; their: number | null; gap: number | null; pct: number | null; large: boolean; hoursOwn: number | null; hoursTheir: number | null; hoursBoth: number | null };
/** One month of one neighbour, as the file holds it. */
export function monthCell(n: TradeNeighbour | undefined, i: number, threshold = LARGE_GAP_PCT): MonthCell {
  const v = (a: Arr | undefined) => { const x = a?.[i]; return num(x) ? x : null; };
  const own = v(n?.net_imports_mwh), their = v(n?.their_report_mwh), gap = v(n?.gap_mwh);
  const pct = gapPct(gap, own, their);
  return { own, their, gap, pct, large: isLarge(pct, threshold), hoursOwn: v(n?.hours_own), hoursTheir: v(n?.hours_their), hoursBoth: v(n?.hours_both) };
}

/** The points of a chart from a monthly array: one a held month, t the month's first second (UTC), v in GWh. */
export function monthPoints(arr: Arr | undefined, months: string[] | undefined): { t: number; v: number }[] {
  const out: { t: number; v: number }[] = [];
  (months ?? []).forEach((m, i) => { const v = arr?.[i]; if (num(v)) out.push({ t: Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)) - 1, 1) / 1000, v: v / 1000 }); });
  return out;
}

export type PairView = {
  key: string; a: string; b: string;
  /** the region the net flow ran from and the one it ran to, by the file's `direction` (by the sign of its mean when
   *  the file names none); both null when neither says */
  from: string | null; to: string | null;
  /** each side's report of the flow from `from` to `to` (the file's value, its sign turned when the flow ran from b to
   *  a), the mean, and the sender's report less the taker's; a report below zero says that side counted the flow the
   *  other way */
  fromReport: number | null; toReport: number | null; mean: number | null; gap: number | null;
  pct: number | null; large: boolean;
};
/** The pairs of one year, each turned to its own direction, in the contract's order of the first code and then the
 *  second (no pair is ranked against another). */
export function pairsOfYear(rows: PairRow[] | undefined, year: string, threshold = LARGE_GAP_PCT): PairView[] {
  const out: PairView[] = [];
  for (const r of rows ?? []) {
    if (String(r.year) !== year || !r.a || !r.b) continue;
    const dir = r.direction === "a_to_b" || r.direction === "b_to_a" ? r.direction : num(r.mean_mwh) && r.mean_mwh !== 0 ? (r.mean_mwh > 0 ? "a_to_b" : "b_to_a") : null;
    const turn = dir === "b_to_a" ? -1 : 1;
    const v = (x: number | null | undefined) => (num(x) ? x * turn || 0 : null);
    const pct = gapPct(r.gap_mwh, r.a_report_mwh, r.b_report_mwh);
    out.push({
      key: `${r.a}-${r.b}`, a: r.a, b: r.b, from: dir ? (dir === "a_to_b" ? r.a : r.b) : null, to: dir ? (dir === "a_to_b" ? r.b : r.a) : null,
      fromReport: v(dir === "b_to_a" ? r.b_report_mwh : r.a_report_mwh), toReport: v(dir === "b_to_a" ? r.a_report_mwh : r.b_report_mwh),
      mean: v(r.mean_mwh), gap: num(r.gap_mwh) ? r.gap_mwh : null, pct, large: isLarge(pct, threshold),
    });
  }
  return out.sort((x, y) => place(x.a) - place(y.a) || x.a.localeCompare(y.a) || place(x.b) - place(y.b) || x.b.localeCompare(y.b));
}

export type PartnerRow = { ba: string; byGross: string[] | null; byNet: string[] | null; sharePct: number | null };
/** Each balancing authority's partners in one year, as the file lists them, by the authority's code. */
export function partnersOfYear(file: MatrixFile | null, year: string): PartnerRow[] {
  return Object.keys(file?.partners ?? {}).sort().flatMap((ba) => {
    const p = file!.partners![ba]?.[year];
    if (!p) return [];
    return [{ ba, byGross: Array.isArray(p.by_gross) ? p.by_gross : null, byNet: Array.isArray(p.by_net) ? p.by_net : null, sharePct: num(p.net_import_share_of_demand_pct) ? p.net_import_share_of_demand_pct : null }];
  });
}

export const SOURCE_KEYS: string[] = SOURCES.map((s) => s.key);
export type MixRow = { month: string; share: Record<string, number | null>; mwh: Record<string, number | null>; net: number | null; daysHeld: number | null; daysInMonth: number | null };
/** The months of one year that a mix file holds, oldest first: each source's share of net generation as the file
 *  writes it, its energy, the month's net generation and its days. */
export function mixMonths(file: MixFile, year: string): MixRow[] {
  return Object.keys(file.months ?? {}).filter((m) => m.slice(0, 4) === year).sort().map((month) => {
    const r = file.months![month];
    const of = (suffix: string) => Object.fromEntries(SOURCE_KEYS.map((s) => { const v = r[`${s}${suffix}`]; return [s, num(v) ? v : null]; }));
    return { month, share: of("_share_pct"), mwh: of("_mwh"), net: num(r.net_generation_mwh) ? r.net_generation_mwh : null, daysHeld: num(r.days_held) ? r.days_held : null, daysInMonth: num(r.days_in_month) ? r.days_in_month : null };
  });
}
export type MixYear = { share: Record<string, number | null>; months: Record<string, number>; net: Sum | null };
/** A year's share by source: the source's energy over the year's months that hold both it and the net generation, over
 *  the net generation of those same months, in percent. `months` says how many months stand behind each share. */
export function mixYear(rows: MixRow[]): MixYear {
  const share: Record<string, number | null> = {}, months: Record<string, number> = {};
  for (const s of SOURCE_KEYS) {
    let e = 0, g = 0, k = 0;
    for (const r of rows) { const x = r.mwh[s]; if (num(x) && num(r.net)) { e += x; g += r.net; k++; } }
    share[s] = k && g !== 0 ? (e / g) * 100 : null;
    months[s] = k;
  }
  const held = rows.filter((r) => num(r.net));
  return { share, months, net: held.length ? { mwh: held.reduce((s, r) => s + (r.net as number), 0), held: held.length, of: rows.length } : null };
}
/** The points of the mix chart: one source's share by month over every month the file holds, t the month's first second. */
export function sharePoints(file: MixFile, source: string): { t: number; v: number }[] {
  return Object.keys(file.months ?? {}).sort().flatMap((m) => {
    const v = file.months![m][`${source}_share_pct`];
    return num(v) ? [{ t: Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)) - 1, 1) / 1000, v }] : [];
  });
}

/** The year drawn when the address names none: the last calendar year that had ended when the file was built, if the
 *  files hold it (the newest year they can hold whole), else the newest year at or before it, else the newest held.
 *  The session's own default (8430). */
export function defaultYear(years: string[], built?: string): string | null {
  const sorted = [...new Set(years)].sort();
  if (!sorted.length) return null;
  const ended = built && /^\d{4}/.test(built) ? String(Number(built.slice(0, 4)) - 1) : null;
  const before = ended ? sorted.filter((y) => y <= ended) : [];
  return before.length ? before[before.length - 1] : sorted[sorted.length - 1];
}
/** A year from a query value, when the files hold it; else null. */
export const yearOf = (v: string | undefined, years: string[]) => (v && years.includes(v) ? v : null);

/** A percent to one decimal, and a month in words ("Aug 2025"). */
export const pct1 = (v: number) => v.toFixed(1);
const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
export const monthWords = (m: string) => `${MON[Number(m.slice(5, 7)) - 1] ?? m.slice(5, 7)} ${m.slice(0, 4)}`;
