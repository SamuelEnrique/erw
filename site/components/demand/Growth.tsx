import { Hint } from "@/components/demand/Hint";
import { cells, hourName, monthName, signed, whole, wholeYears, type Area, type Period } from "@/lib/demandgrowth";

// Session 8420 (chain 503, part C): the three charts of the as-metered view of /demand, as they stood in the page file
// (app/demand/page.tsx, sessions 97 and 152), moved here unchanged so that the view of the whole country
// (components/demand/Country.tsx) draws a region or a balancing authority with the same charts and not with second
// versions of them. A page file may export only what Next.js allows, so they could not be shared from there. The one
// change: the base year and the last whole year, which the charts read from the page's file, are given as `file` (the
// page gives its own file, the new view a region's `growth` object). What the page draws did not move
// (scripts/test-demand-pin.mjs). Each mark carries data-tip, shown by components/demand/Hover.tsx.
export const UP = "var(--color-accent)", DOWN = "var(--color-down)";

/** Average demand by year as bars, the peak as a mark above each. */
export function YearsChart({ area }: { area: Area }) {
  const W = 760, H = 300, L = 70, R = 12, top = 18, bot = 30;
  const ys = wholeYears(area);
  const hasPeak = ys.some((y) => y.row.peak_demand_mw !== undefined);
  const hi = Math.max(...ys.map((y) => y.row.peak_demand_mw ?? y.row.avg_demand_mw)) * 1.08;
  const step = [1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000].find((s) => hi / s <= 6) ?? 200000;
  const bw = (W - L - R) / ys.length;
  const y = (v: number) => top + ((hi - v) / hi) * (H - top - bot);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-chart="years" aria-label={`${area.name}: average demand by year${hasPeak ? " and the year's peak hour" : ""}, MW`}>
      {Array.from({ length: Math.floor(hi / step) + 1 }, (_, i) => i * step).map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{t.toLocaleString("en-US")}</text>
        </g>
      ))}
      {ys.map((d, i) => {
        const tip = `${area.name}, ${d.year}: average ${whole(d.row.avg_demand_mw)} MW${d.row.peak_demand_mw !== undefined ? `, highest hour ${whole(d.row.peak_demand_mw)} MW` : ""}`;
        return (
          <g key={d.year} data-year={d.year} data-tip={tip}>
            <rect x={L + i * bw} y={top} width={bw} height={H - top - bot} fill="transparent" />
            <rect x={L + i * bw + bw * 0.18} y={y(d.row.avg_demand_mw)} width={bw * 0.64} height={y(0) - y(d.row.avg_demand_mw)} fill="var(--color-accent)" aria-label={tip} />
            {d.row.peak_demand_mw !== undefined ? <line x1={L + i * bw + bw * 0.1} x2={L + (i + 1) * bw - bw * 0.1} y1={y(d.row.peak_demand_mw)} y2={y(d.row.peak_demand_mw)} stroke="var(--color-ink)" strokeWidth="2.5" /> : null}
            <text x={L + (i + 0.5) * bw} y={H - 10} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{d.year}</text>
          </g>
        );
      })}
      <text x={L} y={11} fontSize="11" fill="var(--color-muted)">MW</text>
    </svg>
  );
}

/** Where growth concentrates: a cell per month and hour of the day, shaded by the percent change since the base year. */
export function Heat({ area, file }: { area: Area; file: Period }) {
  const cs = cells(file, area);
  if (!cs.length) return <p className="border border-rule bg-paper px-3 py-2 text-sm"><Hint words="not held" why={`The table has no month-and-hour cell for ${area.name} in both ${file.base} and ${file.last_year}.`} /></p>;
  const W = 760, L = 84, R = 8, top = 22, ch = 20;
  const cw = (W - L - R) / 24;
  const H = top + 12 * ch + 6;
  const max = Math.max(...cs.map((c) => Math.abs(c.pct)));
  const at = new Map(cs.map((c) => [`${c.month}|${c.hour}`, c]));
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-chart="heat" data-cells={cs.length} aria-label={`${area.name}: change in average demand from ${file.base} to ${file.last_year}, by month and local hour of the day, percent`}>
      {[0, 3, 6, 9, 12, 15, 18, 21].map((h) => <text key={h} x={L + (h + 0.5) * cw} y={14} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{hourName(h)}</text>)}
      {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
        <g key={m}>
          <text x={L - 8} y={top + (m - 1) * ch + 14} textAnchor="end" fontSize="11" fill="var(--color-ink)">{monthName(m)}</text>
          {Array.from({ length: 24 }, (_, h) => {
            const c = at.get(`${m}|${h}`);
            return c
              ? <rect key={h} x={L + h * cw} y={top + (m - 1) * ch} width={cw - 1} height={ch - 1} fill={c.pct >= 0 ? UP : DOWN} fillOpacity={0.08 + 0.92 * (Math.abs(c.pct) / max)} data-cell={`${m}|${h}`} data-tip={`${monthName(m)}, ${hourName(h)}: ${signed(c.pct)} percent, ${c.mw > 0 ? "+" : ""}${whole(c.mw)} MW`} />
              : <rect key={h} x={L + h * cw} y={top + (m - 1) * ch} width={cw - 1} height={ch - 1} fill="transparent" stroke="var(--color-rule)" data-tip={`${monthName(m)}, ${hourName(h)}: not held`} />;
          })}
        </g>
      ))}
    </svg>
  );
}

/** The change since the base year by month or by hour: a bar each, percent. */
export function ChangeBars({ items, what, file }: { items: { label: string; pct: number | undefined }[]; what: string; file: Period }) {
  const W = 760, H = 200, L = 46, R = 8, top = 14, bot = 28;
  const vals = items.map((i) => i.pct ?? 0);
  const hi = Math.max(0, ...vals) * 1.1 || 1, lo = Math.min(0, ...vals) * 1.1;
  const bw = (W - L - R) / items.length;
  const y = (v: number) => top + ((hi - v) / (hi - lo)) * (H - top - bot);
  const step = [1, 2, 5, 10, 20].find((s) => (hi - lo) / s <= 6) ?? 20;
  const ticks: number[] = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi; t += step) ticks.push(t);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" data-chart={what} aria-label={`Change in average demand from ${file.base} to ${file.last_year}, ${what}, percent`}>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{t}</text>
        </g>
      ))}
      {items.map((it, i) => (
        <g key={it.label} data-tip={it.pct !== undefined ? `${it.label}: ${signed(it.pct)} percent from ${file.base} to ${file.last_year}` : `${it.label}: not held`}>
          <rect x={L + i * bw} y={top} width={bw} height={H - top - bot} fill="transparent" />
          {it.pct !== undefined ? <rect x={L + i * bw + bw * 0.15} y={Math.min(y(0), y(it.pct))} width={bw * 0.7} height={Math.max(1, Math.abs(y(it.pct) - y(0)))} fill={it.pct >= 0 ? UP : DOWN} /> : null}
          {items.length <= 12 || i % 3 === 0 ? <text x={L + (i + 0.5) * bw} y={H - 10} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{items.length <= 12 ? it.label.slice(0, 3) : it.label}</text> : null}
        </g>
      ))}
      <text x={L} y={10} fontSize="11" fill="var(--color-muted)">percent</text>
    </svg>
  );
}
