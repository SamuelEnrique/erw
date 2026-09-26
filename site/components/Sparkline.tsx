import type { Point } from "@/lib/data";

// A server-rendered sparkline: no library, no client code. The last point is marked.
export function Sparkline({ points, width = 160, height = 36, label }: { points: Point[]; width?: number; height?: number; label: string }) {
  if (points.length < 2) return null;
  const xs = points.map((p) => new Date(p.ts_utc).getTime());
  const ys = points.map((p) => p.value);
  const x0 = Math.min(...xs), x1 = Math.max(...xs);
  const y0 = Math.min(...ys), y1 = Math.max(...ys);
  const pad = 3;
  const sx = (x: number) => pad + ((x - x0) / (x1 - x0 || 1)) * (width - 2 * pad);
  const sy = (y: number) => height - pad - ((y - y0) / (y1 - y0 || 1)) * (height - 2 * pad);
  const d = points.map((p, i) => `${i ? "L" : "M"}${sx(xs[i]).toFixed(1)},${sy(p.value).toFixed(1)}`).join("");
  const last = points.length - 1;
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={label} className="block">
      {y0 < 0 && y1 > 0 ? <line x1={pad} x2={width - pad} y1={sy(0)} y2={sy(0)} stroke="var(--color-rule)" strokeWidth={1} /> : null}
      <path d={d} fill="none" stroke="var(--color-accent)" strokeWidth={1.25} />
      <circle cx={sx(xs[last])} cy={sy(ys[last])} r={2} fill="var(--color-accent)" />
    </svg>
  );
}
