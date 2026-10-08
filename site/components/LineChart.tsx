// A time-series line chart (session 22: a wrapper over TimeChart, on ECharts, which replaced uPlot).
// Points are in seconds, as the pages build them. Session 161: with x "hour_of_day" a point's t is the local hour of
// the day, 0 to 23, and is passed as it is.
import { TimeChart } from "./TimeChart";

export type Line = { label: string; points: { t: number; v: number }[]; color: string; step?: boolean; y2?: boolean };

export function LineChart({ lines, unit, height = 280, ariaLabel, x = "minute", unit2 }: { lines: Line[]; unit: string; height?: number; ariaLabel: string; x?: "minute" | "month" | "year" | "hour_of_day"; unit2?: string }) {
  return (
    <TimeChart
      unit={unit}
      height={height}
      ariaLabel={ariaLabel}
      x={x}
      unit2={unit2}
      series={lines.map((l) => ({ name: l.label, color: l.color, step: l.step, dashed: l.color === "muted", y2: l.y2, points: l.points.map((p) => [x === "hour_of_day" ? p.t : p.t * 1000, p.v]) }))}
    />
  );
}
