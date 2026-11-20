// Energy Research Warehouse (ERW) site, session 9000 (chain 601, part C): the congestion view (/congestion) reads one
// file, data/conditions/congestion.json, written by the data machine (warehouse/derived/congestion_page.py; contract
// docs/state/page_files_conditions.md; method docs/methods/grid_congestion.md). This module holds the file's shape and
// the little arithmetic the view names: a constraint's hours summed over the years shown, a month's time stamp.
// Nothing is filled: a month a constraint did not bind has no entry.

export type ConstraintYear = { hours: number; abs_mean: number | null; abs_max: number | null; cost: number | null };
export type Constraint = {
  name: string; contingency: string | null; monitored: string | null; type: string | null; nerc_id: string | null;
  first: string; last: string; hours: number; abs_mean: number | null; abs_max: number | null; cost: number | null;
  by_year: Record<string, ConstraintYear>;
  /** [month YYYY-MM, hours bound, mean size of the shadow price, highest size, mean signed price] */
  monthly: [string, number, number | null, number | null, number | null][];
  /** twelve months by 24 hours of the day: hours bound, every year held summed */
  hod_month: number[][];
};
export type OperatorConstraints = {
  time: string; years: string[]; days_held: Record<string, number>; constraints_by_year: Record<string, number>;
  hours_by_year: Record<string, number>; first: string; last: string;
  top: Record<string, { by_hours: string[]; by_cost: string[] }>; constraints: Record<string, Constraint>;
};
export type PlaceYear = { hours: number; lmp_mean: number | null; congestion_mean: number | null; congestion_share_pct: number | null;
  hours_congestion_up: number; hours_congestion_down: number; congestion_max: number | null; congestion_min: number | null };
export type Place = {
  id: string; node: string; name: string; time: string; years: string[]; first: string; last: string; monthly_columns: string[];
  /** [month, hours, lmp_mean, energy_mean, congestion_mean, loss_mean, ghg_mean, congestion_share_pct] */
  monthly: [string, number, number | null, number | null, number | null, number | null, number | null, number | null][];
  by_year: Record<string, PlaceYear>; hod_month_congestion_mean: Record<string, (number | null)[][]>;
};
export type Operator = { id: string; name: string; status: string; why?: string };
export type Congestion = {
  built: string; method: string; contract: string; license: string; tables: string[]; unit: string; market: string;
  sign_rule: string; cost_rule: string; share_rule: string; operators: Operator[];
  sources: Record<string, { constraints: string; prices: string }>;
  constraints: Record<string, OperatorConstraints>; places: Record<string, Place[]>;
};

export const ALL = "all";
export const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** Seconds since 1970 at the first instant of a YYYY-MM month (the charts' month axis). */
export const monthT = (m: string) => Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)) - 1, 1) / 1000;

/** A constraint's figure for a year, or across every year held ("all"). */
export function yearOf(c: Constraint, year: string): ConstraintYear | null {
  if (year === ALL) return { hours: c.hours, abs_mean: c.abs_mean, abs_max: c.abs_max, cost: c.cost };
  return c.by_year[year] ?? null;
}

/** The largest figure of a grid, for shading (by size: a negative mean shades as deep as a positive one). */
export function maxAbs(cells: (number | null)[][]): number {
  let m = 0;
  for (const row of cells) for (const v of row) if (v !== null && Math.abs(v) > m) m = Math.abs(v);
  return m;
}
