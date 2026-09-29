// Session 30 (price board v2): a sparkline as plain inline SVG, no chart library. The values are drawn as given, in
// order; the last point is marked. A zero line is drawn when the values cross zero. The title carries the first and
// last point, so a reader can hover for them.
export function InlineSpark({
  values,
  width = 120,
  height = 28,
  label,
  color = "var(--color-accent)",
}: {
  values: { t: string; v: number }[];
  width?: number;
  height?: number;
  label: string;
  color?: string;
}) {
  if (values.length < 2) return <span className="text-[11px] text-muted">fewer than 2 days</span>;
  const vs = values.map((p) => p.v);
  const lo = Math.min(...vs);
  const hi = Math.max(...vs);
  const pad = 2;
  const x = (i: number) => pad + (i * (width - 2 * pad)) / (values.length - 1);
  const y = (v: number) => (hi === lo ? height / 2 : pad + ((hi - v) * (height - 2 * pad)) / (hi - lo));
  const pts = values.map((p, i) => `${x(i).toFixed(1)},${y(p.v).toFixed(1)}`).join(" ");
  const first = values[0];
  const last = values[values.length - 1];
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={label} className="block max-w-full">
      <title>{`${label}: ${first.t.slice(0, 10)} ${first.v.toFixed(2)} to ${last.t.slice(0, 10)} ${last.v.toFixed(2)}`}</title>
      {lo < 0 && hi > 0 ? <line x1={pad} x2={width - pad} y1={y(0)} y2={y(0)} stroke="var(--color-rule)" strokeWidth={1} /> : null}
      <polyline points={pts} fill="none" stroke={color} strokeWidth={1.4} strokeLinejoin="round" strokeLinecap="round" />
      <circle cx={x(values.length - 1)} cy={y(last.v)} r={2} fill={color} />
    </svg>
  );
}

// A bar strip in inline SVG (the ERCOT history on /board): one bar per value, labels under every other bar.
export function InlineBars({
  values,
  width = 360,
  height = 90,
  label,
  color = "var(--color-accent)",
}: {
  values: { k: string; v: number }[];
  width?: number;
  height?: number;
  label: string;
  color?: string;
}) {
  if (!values.length) return null;
  const hi = Math.max(...values.map((p) => p.v), 0);
  const lo = Math.min(...values.map((p) => p.v), 0);
  const top = 4;
  const axis = 14;
  const h = height - top - axis;
  const bw = width / values.length;
  const y = (v: number) => top + ((hi - v) * h) / (hi - lo || 1);
  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`} role="img" aria-label={label} className="block max-w-full">
      <title>{label}</title>
      {values.map((p, i) => (
        <g key={p.k}>
          <rect x={i * bw + 1} width={Math.max(1, bw - 2)} y={Math.min(y(p.v), y(0))} height={Math.max(0.5, Math.abs(y(p.v) - y(0)))} fill={color}>
            <title>{`${p.k}: ${p.v.toFixed(2)}`}</title>
          </rect>
          {i % 2 === 0 || values.length <= 8 ? (
            <text x={i * bw + bw / 2} y={height - 3} textAnchor="middle" fontSize={9} fill="var(--color-muted)">
              {p.k.slice(2, 4) === "" ? p.k : `'${p.k.slice(2, 4)}`}
            </text>
          ) : null}
        </g>
      ))}
      <line x1={0} x2={width} y1={y(0)} y2={y(0)} stroke="var(--color-rule)" strokeWidth={1} />
    </svg>
  );
}
