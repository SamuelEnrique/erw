// A stacked area chart as server-rendered SVG (session 18: /mix). Layers stack in the order
// given; only positive values stack (a negative value, such as storage charging, is drawn as
// zero and the caller says so under the chart). Colors are design tokens (app/tokens.css).
export type Layer = { key: string; label: string; color: string; values: (number | null)[] };

export function StackedArea({
  x,
  layers,
  unit,
  ariaLabel,
  height = 240,
  tick,
  ticks,
}: {
  x: number[]; // one time (ms) per column
  layers: Layer[];
  unit: string;
  ariaLabel: string;
  height?: number;
  tick: (t: number) => string; // axis label of a tick
  ticks: number[]; // the times to label
}) {
  const W = 720, H = height, L = 56, R = 8, T = 8, B = 22;
  const n = x.length;
  if (n < 2) return null;
  const tops: number[][] = [];
  const acc = new Array(n).fill(0);
  for (const l of layers) {
    const row = acc.map((a, i) => a + Math.max(0, l.values[i] ?? 0));
    tops.push(row);
    row.forEach((v, i) => (acc[i] = v));
  }
  const ymax = Math.max(...acc) || 1;
  const step = Math.pow(10, Math.floor(Math.log10(ymax)));
  const nice = [1, 2, 2.5, 5, 10].map((m) => m * step).find((s) => ymax / s <= 5) ?? step * 10;
  const top = Math.ceil(ymax / nice) * nice;
  const x0 = x[0], x1 = x[n - 1];
  const px = (t: number) => L + ((t - x0) / (x1 - x0)) * (W - L - R);
  const py = (v: number) => T + (1 - v / top) * (H - T - B);
  const fmtY = (v: number) => (v >= 1e6 ? `${v / 1e6}M` : v >= 1e3 ? `${v / 1e3}k` : String(v));
  const paths = layers.map((l, k) => {
    const upper = tops[k].map((v, i) => `${px(x[i]).toFixed(1)},${py(v).toFixed(1)}`);
    const lower = (k === 0 ? new Array(n).fill(0) : tops[k - 1]).map((v, i) => `${px(x[i]).toFixed(1)},${py(v).toFixed(1)}`).reverse();
    return { l, d: `M${upper.join("L")}L${lower.join("L")}Z` };
  });
  const grid = Array.from({ length: Math.round(top / nice) + 1 }, (_, i) => i * nice);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="block h-auto w-full" role="img" aria-label={ariaLabel}>
      {grid.map((v) => (
        <g key={v}>
          <line x1={L} x2={W - R} y1={py(v)} y2={py(v)} stroke="var(--color-rule)" strokeWidth={1} />
          <text x={L - 4} y={py(v) + 3} textAnchor="end" fontSize={10} fill="var(--color-muted)">
            {fmtY(v)}
          </text>
        </g>
      ))}
      <text x={4} y={T + 8} fontSize={10} fill="var(--color-muted)">
        {unit}
      </text>
      {paths.map(({ l, d }) => (
        <path key={l.key} d={d} fill={l.color} stroke="var(--color-panel)" strokeWidth={0.4}>
          <title>{l.label}</title>
        </path>
      ))}
      {ticks.map((t) => (
        <g key={t}>
          <line x1={px(t)} x2={px(t)} y1={H - B} y2={H - B + 4} stroke="var(--color-muted)" />
          <text x={px(t)} y={H - 6} textAnchor="middle" fontSize={10} fill="var(--color-muted)">
            {tick(t)}
          </text>
        </g>
      ))}
    </svg>
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
