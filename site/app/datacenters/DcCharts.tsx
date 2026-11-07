// Session 2246 (chain 156): the datacenter tracker's three charts (lib/dcrollups.ts). The brand's five series colors in
// order (docs/brand.md, "Chart series"), touching fills parted by a 1 px white line, a legend for the stacked chart,
// every mark a hover with its values (an SVG title) and its key (data-check), and a table of every figure under each
// chart. scripts/check_datacenters.py recomputes every figure with its own code.
import { Num } from "@/components/Num";
import { ChartFrame, ToolSection } from "@/components/tool/ToolPage";
import type { EntityRow } from "@/lib/data";
import { chartGrids, operatorMw, plannedByQuarter, powerShares, type FacRow } from "@/lib/dcrollups";

const W = 760;
const COLORS = ["var(--chart-ink)", "var(--color-accent)", "var(--chart-blue)", "var(--chart-grey)", "var(--chart-light)"];
const M = "var(--color-muted)", T = "var(--color-ink)";
const whole = (v: number) => Math.round(v).toLocaleString("en-US");
const POWER: Record<string, string> = {
  behind_the_meter_gas: "Gas on the site", behind_the_meter: "On the site, fuel not stated", nuclear: "Nuclear",
  renewables_storage: "Renewables or storage", gas: "Gas", grid: "Grid or a utility", other: "Other", none: "Not stated",
};

function Bars({ items, unit, label, chart }: { items: { name: string; v: number; key: string; tip: string }[]; unit: string; label: string; chart: string }) {
  const L = 230, R = 80, rowH = 24, top = 4, H = top + items.length * rowH + 4;
  const hi = Math.max(1, ...items.map((i) => i.v));
  const x = (v: number) => L + (v / hi) * (W - L - R);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={label} data-chart={chart}>
      {items.map((it, i) => {
        const y = top + i * rowH;
        return (
          <g key={it.name}>
            <text x={L - 8} y={y + rowH / 2 + 4} textAnchor="end" fontSize="12" fill={T}>{it.name.length > 32 ? `${it.name.slice(0, 31)}.` : it.name}</text>
            <rect x={L} y={y + 4} width={Math.max(0.5, x(it.v) - L)} height={rowH - 8} fill="var(--chart-ink)" data-check={it.key} data-value={it.v}><title>{it.tip}</title></rect>
            <text x={x(it.v) + 6} y={y + rowH / 2 + 4} fontSize="12" fill={T}>{whole(it.v)}{unit}</text>
          </g>
        );
      })}
    </svg>
  );
}

export function DcCharts({ rows }: { rows: EntityRow[] }) {
  const rs = rows as unknown as FacRow[];
  const qs = plannedByQuarter(rs), grids = [...chartGrids(rs), "other"], ops = operatorMw(rs), power = powerShares(rs);
  const L = 56, R = 12, top = 10, H = 240, B = 24;
  const hiQ = Math.max(1, ...qs.map((q) => q.parts.reduce((a, p) => a + p.mw, 0)));
  const y = (v: number) => top + (1 - v / hiQ) * (H - top - B);
  const bw = (W - L - R) / Math.max(1, qs.length);
  return (
    <ToolSection title="The tracker in charts" id="charts"
      note={<>The facilities the page&apos;s sums count (a named US state, not cancelled). A sum is of the MW the sources state, of any basis; the facilities that state none are counted in each hover and table. Hover a mark for its values.</>}>
      <ChartFrame title="Planned and building MW, by the quarter first reported and by grid" note={<>Planned (announced, applied or permitted) and under construction; the grid a story names, else its queue&apos;s ISO, else its state&apos;s; the four grids with the most MW, the rest as other.</>}>
        {qs.length ? (
          <>
            <ul className="mb-2 flex flex-wrap gap-x-4 gap-y-1 text-xs" aria-label="Legend">
              {grids.map((g, i) => <li key={g} className="flex items-center gap-1"><span aria-hidden="true" className="inline-block h-3 w-3" style={{ background: COLORS[i] }} />{g === "other" ? "Other grids or none" : g}</li>)}
            </ul>
            <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Planned and building MW by quarter first reported, stacked by grid" data-chart="planned">
              {qs.map((q, i) => {
                let base = 0;
                const x = L + i * bw + bw * 0.15, w = bw * 0.7;
                return (
                  <g key={q.quarter}>
                    {q.parts.filter((p) => p.mw > 0).map((p) => {
                      const y0 = y(base), y1 = y(base + p.mw);
                      base += p.mw;
                      return <rect key={p.grid} x={x} y={y1} width={w} height={Math.max(0.5, y0 - y1)} fill={COLORS[grids.indexOf(p.grid)]} stroke="#FFFFFF" strokeWidth="1"
                        data-check={`dcchart|planned|${q.quarter}|${p.grid}`} data-value={p.mw}><title>{`${q.quarter}, ${p.grid === "other" ? "other grids or none" : p.grid}: ${whole(p.mw)} MW stated`}</title></rect>;
                    })}
                    <text x={x + w / 2} y={H - 8} textAnchor="middle" fontSize="11" fill={M}>{q.quarter}</text>
                  </g>
                );
              })}
            </svg>
            <details className="mt-2 text-sm">
              <summary className="cursor-pointer text-xs text-muted">The figures as a table</summary>
              <table className="mt-1 w-full border-collapse text-left text-sm">
                <thead><tr className="border-b border-rule text-xs text-muted">{["Quarter", ...grids, "Stating no MW"].map((h) => <th key={h} scope="col" className="py-1 pr-3 font-normal">{h}</th>)}</tr></thead>
                <tbody>{qs.map((q) => (
                  <tr key={q.quarter} className="border-b border-rule/60">
                    <td className="py-1 pr-3">{q.quarter}</td>
                    {q.parts.map((p) => <td key={p.grid} className="py-1 pr-3 tabular-nums"><Num check={`dcchart|planned|${q.quarter}|${p.grid}`} raw={p.mw}>{whole(p.mw)}</Num></td>)}
                    <td className="py-1 pr-3 tabular-nums"><Num check={`dcchart|planned|${q.quarter}|without`} raw={q.without}>{whole(q.without)}</Num></td>
                  </tr>
                ))}</tbody>
              </table>
            </details>
          </>
        ) : <p className="text-sm text-muted" role="status">No counted facility is planned or building with a first report held.</p>}
      </ChartFrame>
      <ChartFrame title="The operators with the most MW stated" note={<>The operator, else the developer; the MW its counted facilities state.</>}>
        {ops.length ? (
          <>
            <Bars chart="operator" unit=" MW" label="The operators with the most MW stated"
              items={ops.map((o) => ({ name: o.operator, v: o.mw, key: `dcchart|operator|${o.operator}|mw`, tip: `${o.operator}: ${whole(o.mw)} MW stated by ${o.withMw} of its ${o.facilities} counted facilities` }))} />
            <details className="mt-2 text-sm">
              <summary className="cursor-pointer text-xs text-muted">The figures as a table</summary>
              <table className="mt-1 w-full border-collapse text-left text-sm"><tbody>{ops.map((o) => (
                <tr key={o.operator} className="border-b border-rule/60"><td className="py-1 pr-3">{o.operator}</td><td className="py-1 pr-3 tabular-nums"><Num check={`dcchart|operator|${o.operator}|mw`} raw={o.mw}>{whole(o.mw)}</Num> MW</td><td className="py-1 pr-3 text-muted">{o.withMw} of {o.facilities} state MW</td></tr>
              ))}</tbody></table>
            </details>
          </>
        ) : <p className="text-sm text-muted" role="status">No counted facility states MW.</p>}
      </ChartFrame>
      <ChartFrame title="The kind of power the sources state" note={<>The share of the counted facilities by the kind of power their sources state; most state none.</>}>
        <Bars chart="power" unit="%" label="The share of the counted facilities by the kind of power stated"
          items={power.map((p) => ({ name: POWER[p.kind] ?? p.kind, v: p.pct, key: `dcchart|power|${p.kind}|pct`, tip: `${POWER[p.kind] ?? p.kind}: ${p.facilities} facilities, ${p.pct}% of those counted` }))} />
        <details className="mt-2 text-sm">
          <summary className="cursor-pointer text-xs text-muted">The figures as a table</summary>
          <table className="mt-1 w-full border-collapse text-left text-sm"><tbody>{power.map((p) => (
            <tr key={p.kind} className="border-b border-rule/60"><td className="py-1 pr-3">{POWER[p.kind] ?? p.kind}</td><td className="py-1 pr-3 tabular-nums"><Num check={`dcchart|power|${p.kind}|facilities`} raw={p.facilities}>{whole(p.facilities)}</Num></td><td className="py-1 pr-3 tabular-nums"><Num check={`dcchart|power|${p.kind}|pct`} raw={p.pct}>{String(p.pct)}</Num>%</td></tr>
          ))}</tbody></table>
        </details>
      </ChartFrame>
    </ToolSection>
  );
}
