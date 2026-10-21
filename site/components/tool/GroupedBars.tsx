// Session 235: a bar chart in the brand's manner (docs/brand.md, section 6; the battery page's year chart is the
// reference), for any tool page: one group a year (or a span), one bar a series, the series named on the chart in
// their own colors (no legend box), an incomplete year hatched, a figure written above each bar or each group. Plain
// SVG drawn on the server: no chart library and no script. Every color is a token of app/tokens.css read through its
// CSS variable, so a change of brand is that one file; the type and the grid lines take the brand's rules for
// `svg[role="img"]`. On a phone the brand keeps the chart at a readable width and lets it scroll inside its frame.

/** A series' color, by the token's role: the highlighted series is the accent, the one beside it ink. */
export type Tone = "accent" | "ink" | "muted";
const COLOR: Record<Tone, string> = { accent: "var(--color-accent)", ink: "var(--color-ink)", muted: "var(--color-muted)" };

export type BarSeries = { name: string; tone: Tone };
export type BarGroup = {
  /** the label under the group ("2024", "Last 12 months"), and a second line under it ("9 months") */
  label: string; sub?: string;
  /** an incomplete year: its bars are hatched */
  partial?: boolean;
  /** one value a series, null where it is not held */
  values: (number | null)[];
  /** written above the group in place of each bar's own figure ("87%") */
  over?: string;
  /** the hover's words */
  title?: string;
};

const nice = (hi: number) => [0.5, 1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 5000].find((s) => hi / s <= 5) ?? 10000;

export function GroupedBars({ id, groups, series, unit, label, partialWords = "Incomplete year", fmt = (v) => Math.round(v).toLocaleString("en-US") }: {
  /** a name for the chart's own patterns, unique on the page */
  id: string; groups: BarGroup[]; series: BarSeries[]; unit: string; label: string; partialWords?: string;
  /** how a bar's figure is written above it */
  fmt?: (v: number) => string;
}) {
  const W = 760, H = 300, L = 54, R = 10, top = 30, bot = 44;
  const all = groups.flatMap((g) => g.values).filter((v): v is number => v !== null);
  const hi = (Math.max(0, ...all) * 1.12) || 1, lo = Math.min(0, ...all) * 1.12;
  const step = nice(hi - lo);
  const ticks: number[] = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi; t += step) ticks.push(Math.round(t * 100) / 100 || 0);  // session 404: || 0, so a tick at minus zero reads "0", not "-0"
  const y = (v: number) => top + ((hi - v) / (hi - lo)) * (H - top - bot);
  const gw = (W - L - R) / Math.max(1, groups.length);
  const n = series.length;
  const bw = Math.min(46, (gw * 0.72) / n);
  const anyPartial = groups.some((g) => g.partial);
  // the series' names on the first line after the unit, each in its own color; the hatch's meaning last. They start
  // from the left, so that on a phone, where the chart scrolls sideways inside its frame, they are in view at once
  const names: { text: string; tone: Tone; hatch?: boolean }[] = [...series.map((s) => ({ text: s.name, tone: s.tone })), ...(anyPartial ? [{ text: partialWords, tone: "muted" as Tone, hatch: true }] : [])];
  let at = L - 46 + unit.length * 6.6 + 28;
  const placed = names.map((t) => { const x = at; at += t.text.length * 6.6 + (t.hatch ? 38 : 24); return { ...t, x }; });
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={label} data-bars={id}>
      <defs>
        {series.map((s, k) => (
          <pattern key={k} id={`${id}-hatch-${k}`} width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <rect width="5" height="5" style={{ fill: "var(--color-surface)" }} /><rect width="2.2" height="5" style={{ fill: COLOR[s.tone] }} />
          </pattern>
        ))}
      </defs>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} style={{ stroke: t === 0 ? "var(--color-ink)" : "var(--color-rule)" }} strokeWidth={t === 0 ? 1 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" style={{ fill: "var(--color-muted)" }}>{t.toLocaleString("en-US")}</text>
        </g>
      ))}
      <text x={L - 46} y={14} style={{ fill: "var(--color-muted)" }}>{unit}</text>
      <g data-direct-labels="1">
        {placed.map((t) => (
          <g key={t.text}>
            {t.hatch ? <rect x={t.x} y={5} width="10" height="10" fill={`url(#${id}-hatch-0)`} style={{ stroke: COLOR[series[0].tone] }} strokeWidth="0.75" /> : null}
            <text x={t.x + (t.hatch ? 15 : 0)} y={14} style={{ fill: COLOR[t.tone] }}>{t.text}</text>
          </g>
        ))}
      </g>
      {groups.map((g, i) => {
        const x0 = L + i * gw + (gw - bw * n) / 2;
        const tops = g.values.map((v) => (v === null ? y(0) : y(Math.max(0, v))));
        return (
          <g key={g.label} data-group={g.label}>
            {g.values.map((v, k) => {
              if (v === null) return null;
              const a = y(Math.max(0, v)), b = y(Math.min(0, v));
              return <rect key={k} x={x0 + k * bw} width={bw} y={a} height={Math.max(0.5, b - a)} fill={g.partial ? `url(#${id}-hatch-${k})` : undefined}
                stroke={g.partial ? undefined : "none"} style={g.partial ? { stroke: COLOR[series[k].tone] } : { fill: COLOR[series[k].tone] }} strokeWidth={g.partial ? 0.75 : 0} />;
            })}
            {g.over !== undefined
              ? <text x={x0 + (bw * n) / 2} y={Math.min(...tops) - 6} textAnchor="middle" style={{ fill: "var(--color-ink)" }}>{g.over}</text>
              : g.values.map((v, k) => (v === null ? null : <text key={k} x={x0 + k * bw + bw / 2} y={tops[k] - 6} textAnchor="middle" style={{ fill: "var(--color-ink)" }}>{fmt(v)}</text>))}
            <text x={x0 + (bw * n) / 2} y={H - bot + 16} textAnchor="middle" style={{ fill: "var(--color-ink)" }}>{g.label}</text>
            {g.sub ? <text x={x0 + (bw * n) / 2} y={H - bot + 31} textAnchor="middle" style={{ fill: "var(--color-muted)" }}>{g.sub}</text> : null}
            {g.title ? <title>{g.title}</title> : null}
          </g>
        );
      })}
    </svg>
  );
}
