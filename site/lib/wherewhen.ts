// Energy Research Warehouse (ERW) site, session 8014 (chain 581, part C): the curtailment tool's "Where and when" view
// (/curtailment/where-when) reads one file, data/curtailment/where_when.json, written by the data machine
// (warehouse/derived/where_when.py; contract docs/state/page_files_curtailment.md; method docs/methods/where_when.md).
// This module holds the file's shape and the little arithmetic the view names: a cell's share of hours below zero, the
// sum of a place's years, a year's figure. Nothing is filled: a cell with no hour held has no share.

export type Grid12 = (number | null)[][];
export type CurtailmentPlace = { id: string; name: string; grid: string; kind: "curtailment"; table: string; vintage: string; unit: string; time: string; source: string;
  years: string[]; by_hour: boolean; by_hour_reason?: string; fuels?: string[]; variables?: string[];
  matrix?: Record<string, Record<string, (number[] | null)[]>>; monthly?: Record<string, Record<string, number | null>>; months?: string[];
  by_year: Record<string, Record<string, number | boolean | null>>; days_held?: Record<string, { days_held: number; days_in_year: number }> };
export type PricePlace = { id: string; name: string; grid: string; grid_name: string; kind: string; unit: string; time: string; tables: Record<string, string[]>; freq: Record<string, string>;
  years: string[]; matrix: Record<string, { basis: string; negative: number[][]; held: number[][] }>;
  by_year: Record<string, { basis: string; hours_in_year: number; hours_held: number; negative: number; whole: boolean; share_negative_pct: number | null }> };
export type Ranked = { id: string; name: string; grid: string; kind: string; year: string; share_negative_pct: number | null; negative: number; hours_held: number };
export type WhereWhen = { built: string; method: string; contract: string; license: string; tables: string[]; internal_tables: string[]; near: number; hour_rule: string; whole_year_rule: string;
  curtailment: CurtailmentPlace[]; curtailment_not_held: Record<string, string>; prices: PricePlace[];
  price_blank: Record<string, { name: string; words: string; regions: string[] }>; ranked_negative: Ranked[] };

export const ALL = "all";
export const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** A price place's matrix for a year, or every year summed ("all"): negative and held counts, 12 by 24. */
export function priceCells(p: PricePlace, year: string): { negative: number[][]; held: number[][]; basis: string } | null {
  const ys = year === ALL ? p.years : p.years.filter((y) => y === year);
  if (!ys.length) return null;
  const neg = Array.from({ length: 12 }, () => new Array<number>(24).fill(0));
  const held = Array.from({ length: 12 }, () => new Array<number>(24).fill(0));
  const bases = new Set<string>();
  for (const y of ys) {
    const m = p.matrix[y];
    if (!m) continue;
    bases.add(m.basis);
    for (let i = 0; i < 12; i++) for (let h = 0; h < 24; h++) { neg[i][h] += m.negative[i][h]; held[i][h] += m.held[i][h]; }
  }
  return { negative: neg, held, basis: [...bases].sort().join(" and ") };
}

/** A cell's share of hours below zero, percent; null when no hour of it is held. */
export const shareOf = (neg: number, held: number): number | null => (held > 0 ? (100 * neg) / held : null);

/** CAISO's curtailment matrix for a year (or every year summed) and a fuel ("both" sums solar and wind), MWh, 12 by 24;
 * a month not held in a year is null in that year, and a summed cell is null only when no year holds it. */
export function curtailCells(c: CurtailmentPlace, year: string, fuel: string): Grid12 | null {
  if (!c.by_hour || !c.matrix) return null;
  const ys = year === ALL ? c.years : c.years.filter((y) => y === year);
  if (!ys.length) return null;
  const fuels = fuel === "both" ? (c.fuels ?? []) : [fuel];
  const out: Grid12 = Array.from({ length: 12 }, () => new Array<number | null>(24).fill(null));
  for (const y of ys) for (const f of fuels) {
    const g = c.matrix[y]?.[f];
    if (!g) continue;
    g.forEach((row, i) => { if (row) row.forEach((v, h) => { if (v !== null && v !== undefined) out[i][h] = (out[i][h] ?? 0) + v; }); });
  }
  return out;
}

/** The newest whole year of a place, or the newest year held. */
export function newestYear(years: string[], byYear: Record<string, { whole?: boolean | number | null } | Record<string, unknown>>): string | null {
  const whole = years.filter((y) => (byYear[y] as { whole?: boolean })?.whole);
  return whole.length ? whole[whole.length - 1] : years.length ? years[years.length - 1] : null;
}

/** The largest figure of a 12 by 24 grid, for the color scale; 0 when none. */
export function maxOf(g: (number | null)[][]): number {
  let m = 0;
  for (const r of g) for (const v of r) if (v !== null && v > m) m = v;
  return m;
}
