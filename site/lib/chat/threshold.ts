// Session 3297 (the trader set's tr15, "how many 15-minute intervals at ERCOT West above 100 USD/MWh"): the query tool's
// value threshold, as warehouse/chat/tools.py _threshold and its filter in query. Rows are kept when their value column is
// strictly above and/or strictly below the figures, before the aggregation, so count with a threshold is the number of
// intervals past it. The same argument name (threshold, {above, below}) and the same answer field (threshold: column,
// above, below, rows_in_window, rows_kept, note) in both loops. Kept apart from tools.ts, with no imports, so that
// `node --test site/scripts/test-ask-threshold.test.mjs` runs it without the site's build.

export type Threshold = { above?: number; below?: number };

export class ThresholdError extends Error {}

/** The note of a result when rows matched the filters and none is past the threshold (tools.py THRESHOLD_NONE). */
export const THRESHOLD_NONE = "rows match these filters, and none of them is past the threshold (threshold.rows_kept is 0)";

const SHAPE ='threshold is an object with above, below or both, for example {"above": 100}';

/** The threshold argument read as [above, below], each a number or null; null when no threshold was given. */
export function readThreshold(t: unknown): [number | null, number | null] | null {
  if (t === undefined || t === null) return null;
  if (typeof t !== "object" || Array.isArray(t)) throw new ThresholdError(SHAPE);
  const keys = Object.keys(t as object);
  if (!keys.length || keys.some((k) => k !== "above" && k !== "below")) throw new ThresholdError(SHAPE);
  const pick = (k: "above" | "below"): number | null => {
    const v = (t as Record<string, unknown>)[k];
    if (v === undefined || v === null) return null;
    if (typeof v !== "number" || Number.isNaN(v)) throw new ThresholdError(`threshold ${k} must be a number`);
    return v;
  };
  const above = pick("above"), below = pick("below");
  if (above === null && below === null) throw new ThresholdError(SHAPE);
  if (above !== null && below !== null && above >= below) throw new ThresholdError("threshold above must be less than below (rows strictly between the two)");
  return [above, below];
}

/** The rows past the threshold, and the answer's threshold field. A row with no value is never kept. */
export function applyThreshold<R extends { v: number | null }>(rows: R[], t: [number | null, number | null], column: string, round: (x: number) => number = (x) => x): { kept: R[]; field: Record<string, unknown> } {
  const [above, below] = t;
  const kept = rows.filter((r) => r.v !== null && Number.isFinite(r.v) && (above === null || r.v > above) && (below === null || r.v < below));
  const field: Record<string, unknown> = { column };
  if (above !== null) field.above = round(above);
  if (below !== null) field.below = round(below);
  field.rows_in_window = rows.length;
  field.rows_kept = kept.length;
  field.note = "rows_kept of rows_in_window have a value strictly past the threshold; the aggregation is over those rows";
  return { kept, field };
}
