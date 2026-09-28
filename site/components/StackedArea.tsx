// A stacked area chart (session 22: a wrapper over TimeChart, on ECharts, which replaced the server
// SVG). The chart has its own legend, which toggles layers; Legend below is kept for tables that
// show the same colors.
import { TimeChart } from "./TimeChart";

export type Layer = { key: string; label: string; color: string; values: (number | null)[] };

export function StackedArea({ x, layers, unit, ariaLabel, height = 260 }: {
  x: number[];
  layers: Layer[];
  unit: string;
  ariaLabel: string;
  height?: number;
  tick?: (t: number) => string; // no longer used: the time axis labels itself
  ticks?: number[];
}) {
  if (x.length < 2) return null;
  const gaps = x.slice(1).map((t, i) => t - x[i]).sort((a, b) => a - b);
  const gap = gaps[Math.floor(gaps.length / 2)];
  const fmt = gap >= 27 * 86_400_000 ? "month" : gap >= 86_400_000 ? "day" : "minute";
  return (
    <TimeChart
      stack
      unit={unit}
      height={height + 60}
      ariaLabel={ariaLabel}
      x={fmt}
      series={layers.map((l) => ({ name: l.label, color: l.color, points: x.map((t, i) => [t, l.values[i]] as [number, number | null]) }))}
    />
  );
}

export function Legend({ items }: { items: { key: string; label: string; color: string }[] }) {
  return (
    <div className="my-2 flex flex-wrap gap-3 text-xs" aria-label="Colors">
      {items.map((f) => (
        <span key={f.key} className="flex items-center gap-1">
          <span className="inline-block h-3 w-3 rounded-sm" style={{ background: f.color }} />
          {f.label}
        </span>
      ))}
    </div>
  );
}
