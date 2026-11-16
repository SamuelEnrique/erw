// A time-series line chart (session 22: a wrapper over TimeChart, on ECharts, which replaced uPlot).
// Points are in seconds, as the pages build them. Session 161: with x "hour_of_day" a point's t is the local hour of
// the day, 0 to 23, and is passed as it is.
import { TimeChart } from "./TimeChart";

// Session 7542: `gap` (seconds), optional: where two points stand further apart than it, the line is broken there
// (a null point after the first), so hours a table does not hold are not drawn as a straight line across them.
export type Line = { label: string; points: { t: number; v: number }[]; color: string; step?: boolean; y2?: boolean; gap?: number };

/** The points with a break where two stand more than `gap` apart; as given when `gap` is not set. */
export function gapped(points: { t: number; v: number }[], gap?: number): { t: number; v: number | null }[] {
  if (!gap) return points;
  const out: { t: number; v: number | null }[] = [];
  points.forEach((p, i) => {
    if (i > 0 && p.t - points[i - 1].t > gap) out.push({ t: points[i - 1].t + gap, v: null });
    out.push(p);
  });
  return out;
}

export function LineChart({ lines, unit, height = 280, ariaLabel, x = "minute", unit2 }: { lines: Line[]; unit: string; height?: number; ariaLabel: string; x?: "minute" | "month" | "year" | "hour_of_day"; unit2?: string }) {
  return (
    <TimeChart
      unit={unit}
      height={height}
      ariaLabel={ariaLabel}
      x={x}
      unit2={unit2}
      series={lines.map((l) => ({ name: l.label, color: l.color, step: l.step, dashed: l.color === "muted", y2: l.y2, points: gapped(l.points, l.gap).map((p): [number, number | null] => [x === "hour_of_day" ? p.t : p.t * 1000, p.v]) }))}
    />
  );
}
