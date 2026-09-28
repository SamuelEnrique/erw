import type { Point } from "@/lib/data";
import { TimeChart } from "./TimeChart";

// The home page's sparkline (session 22: on ECharts, with hover values and zoom, like every chart).
export function Sparkline({ points, height = 40, label, unit = "USD/MWh" }: { points: Point[]; width?: number; height?: number; label: string; unit?: string }) {
  if (points.length < 2) return null;
  return (
    <TimeChart
      mini
      unit={unit}
      height={height}
      ariaLabel={label}
      series={[{ name: label, color: "accent", points: points.map((p) => [new Date(p.ts_utc).getTime(), p.value]) }]}
    />
  );
}
