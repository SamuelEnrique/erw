// A time-series line chart (session 22: a wrapper over TimeChart, on ECharts, which replaced uPlot).
// Points are in seconds, as the pages build them.
import { TimeChart } from "./TimeChart";

export type Line = { label: string; points: { t: number; v: number }[]; color: "accent" | "muted" | "ink"; step?: boolean };

export function LineChart({ lines, unit, height = 280, ariaLabel, x = "minute" }: { lines: Line[]; unit: string; height?: number; ariaLabel: string; x?: "minute" | "month" | "year" }) {
  return (
    <TimeChart
      unit={unit}
      height={height}
      ariaLabel={ariaLabel}
      x={x}
      series={lines.map((l) => ({ name: l.label, color: l.color, step: l.step, dashed: l.color === "muted", points: l.points.map((p) => [p.t * 1000, p.v]) }))}
    />
  );
}
