// Energy Research Warehouse (ERW) site, session 1412 (chain 107): the geometry of one small chart of the Flex Alert
// scorecard (/grid/caiso/alerts, "Each alert day through the evening"), and what its hover says at an hour.
//
// The drawing is session 60's DayChart (app/grid/caiso/alerts/page.tsx), moved here word for word so the client chart
// (app/grid/caiso/alerts/DayChart.tsx) can draw it and answer a hover: the same viewBox (260 by 120), the same scale
// (the lowest to the highest of demand and the band, 8 percent of the span added each side, or 500 MW when flat), the
// same points, rounded to one decimal as before. Nothing here is a figure of its own: every value is a row of
// flex_alert_effects (freq PT1H) the page hands, grouped by Pacific hour as it was.
//
// A point is [Pacific hour, actual_mw, predicted_mw, predicted_mw_lo, predicted_mw_hi, alert_hour], null where the row is
// not held (the compact form the page sends the browser; `record` turns it back into the hour's values by name).

export type HourPoint = [number, number | null, number | null, number | null, number | null, number | null];
const NAMES = ["actual_mw", "predicted_mw", "predicted_mw_lo", "predicted_mw_hi", "alert_hour"] as const;

export const W = 260, Hh = 120, L = 34, B = 16;

/** The hour's values by name, as session 60's DayChart held them (a value not held is absent, not null). */
export function record(p: HourPoint): Record<string, number> {
  const o: Record<string, number> = {};
  NAMES.forEach((n, i) => { const v = p[i + 1]; if (v !== null && v !== undefined) o[n] = v; });
  return o;
}

/** The hours of a day to points, from the hour's values by name (the page's grouping). */
export function pointsOf(by: Map<number, Record<string, number>>): HourPoint[] {
  return [...by.keys()].sort((a, b) => a - b).map((h) => [h, ...NAMES.map((n) => by.get(h)![n] ?? null)] as HourPoint);
}

/** Session 60's DayChart, every line of its arithmetic as it was; null when no hour is held. */
export function dayGeometry(points: HourPoint[]) {
  const by = new Map<number, Record<string, number>>(points.map((p) => [p[0], record(p)]));
  const hs = [...by.keys()].sort((a, b) => a - b);
  if (!hs.length) return null;
  const vals = hs.flatMap((h) => ["actual_mw", "predicted_mw_lo", "predicted_mw_hi"].map((k) => by.get(h)![k]).filter((v) => v !== undefined));
  const lo = Math.min(...vals), hi = Math.max(...vals), pad = (hi - lo) * 0.08 || 500;
  const x = (h: number) => L + ((h - hs[0]) / Math.max(1, hs.at(-1)! - hs[0])) * (W - L - 6);
  const y = (v: number) => 4 + (1 - (v - (lo - pad)) / (hi - lo + 2 * pad)) * (Hh - B - 4);
  const path = (k: string) => hs.filter((h) => by.get(h)![k] !== undefined).map((h, i) => `${i ? "L" : "M"}${x(h).toFixed(1)},${y(by.get(h)![k]).toFixed(1)}`).join("");
  const band = hs.map((h) => `${x(h).toFixed(1)},${y(by.get(h)!.predicted_mw_hi).toFixed(1)}`).join(" ") + " " +
    [...hs].reverse().map((h) => `${x(h).toFixed(1)},${y(by.get(h)!.predicted_mw_lo).toFixed(1)}`).join(" ");
  const alertHs = hs.filter((h) => by.get(h)!.alert_hour === 1);
  const step = (W - L - 6) / Math.max(1, hs.at(-1)! - hs[0]);
  return {
    hs, by, x, y, step, lo, hi, band, alertHs,
    actual: path("actual_mw"), predicted: path("predicted_mw"),
    ticks: hs.filter((h) => h % 3 === 0),
  };
}

/** The hour nearest a point of the drawing (in its viewBox units), of the hours held. */
export function nearestHour(hs: number[], x: (h: number) => number, vx: number): number {
  let best = hs[0];
  for (const h of hs) if (Math.abs(x(h) - vx) < Math.abs(x(best) - vx)) best = h;
  return best;
}

/** What the hover says at an hour: the Pacific hour as the axis writes it, demand served, the model's estimate, its
 *  band, the estimate less demand (the page's sign: a positive number is a cut) and whether it is an alert hour. Each
 *  value is the hour's own row, unrounded here (the card writes it). */
export function hourCard(v: Record<string, number>, h: number) {
  const actual = v.actual_mw, predicted = v.predicted_mw;
  return {
    hour: `${h}:00`,
    actual, predicted, lo: v.predicted_mw_lo, hi: v.predicted_mw_hi,
    diff: actual !== undefined && predicted !== undefined ? predicted - actual : undefined,
    alert: v.alert_hour === 1,
  };
}
