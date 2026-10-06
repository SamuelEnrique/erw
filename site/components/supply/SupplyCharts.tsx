"use client";
// Energy Research Warehouse (ERW) site, session 134: the charts of Supply and trade (/supply).
//
//   Band    a series through its year against the five years before: their lowest to highest as a band, their mean
//           dashed, last year thin, this year bold. The mouse reads each of them with its date and unit.
//   Trend   a row's last 52 points as a small line that answers the mouse with the value, the date and the series.
import { useMemo, useState } from "react";
import { baseStyle, token, useEChart } from "@/components/echarts";
import { dateWords, fmt, shortDate, type Row } from "@/lib/supply";

export function Band({ row, height = 300 }: { row: Row; height?: number }) {
  const s = row.season!;
  const box = useEChart((chart) => {
    const st = baseStyle();
    const x = s.t.map((t) => shortDate(t, row.freq));
    const year = s.t[0].slice(0, 4);
    const n = (v: number | null | undefined) => (v === null || v === undefined ? null : v);
    chart.setOption({
      textStyle: st.textStyle, animation: false, toolbox: st.toolbox(`erw-supply-${row.id}`),
      legend: { type: "scroll", top: 0, left: 0, right: 30, textStyle: { fontSize: 11 }, itemWidth: 14, itemHeight: 8, data: [year, String(Number(year) - 1), "Five-year average", "Five-year range"] },
      tooltip: { ...st.tooltip, trigger: "axis", formatter: (ps: { dataIndex: number }[]) => {
        const i = ps[0].dataIndex;
        const line = (name: string, v: number | null) => (v === null ? "" : `<br/>${name}: <b>${fmt(v, row.unit)}</b> ${row.unit}`);
        return `${row.label}, ${row.at}<br/>${dateWords(s.t[i], row.freq)}${line(year, s.cur[i])}${line(String(Number(year) - 1), s.last[i])}${line("Five-year average", s.avg[i])}`
          + (s.lo[i] !== null ? `<br/>Five-year range: ${fmt(s.lo[i]!, row.unit)} to ${fmt(s.hi[i]!, row.unit)} ${row.unit}` : "");
      } },
      grid: { left: 62, right: 14, top: 48, bottom: 26 },
      xAxis: { type: "category", data: x, boundaryGap: false, ...st.axis, splitLine: { show: false } },
      yAxis: { type: "value", scale: true, name: row.unit, ...st.axis },
      series: [
        { name: "low", type: "line", stack: "band", showSymbol: false, lineStyle: { opacity: 0 }, data: s.lo.map(n), tooltip: { show: false } },
        { name: "Five-year range", type: "line", stack: "band", showSymbol: false, lineStyle: { opacity: 0 }, areaStyle: { color: token("rule"), opacity: 0.6 }, itemStyle: { color: token("rule") }, data: s.hi.map((h, i) => (h === null || s.lo[i] === null ? null : h - s.lo[i]!)) },
        { name: "Five-year average", type: "line", showSymbol: false, lineStyle: { width: 1.2, type: "dashed", color: token("muted") }, itemStyle: { color: token("muted") }, data: s.avg.map(n) },
        { name: String(Number(year) - 1), type: "line", showSymbol: false, lineStyle: { width: 1.2, color: token("fuel-gas") }, itemStyle: { color: token("fuel-gas") }, data: s.last.map(n) },
        { name: year, type: "line", showSymbol: row.freq === "M", symbolSize: 5, lineStyle: { width: 2.4, color: token("accent") }, itemStyle: { color: token("accent") }, data: s.cur.map(n), z: 5 },
      ],
    }, true);
  }, [row]);
  return <div ref={box} role="img" aria-label={`${row.label}, ${row.at}: this year against the five years before`} style={{ height }} className="w-full" data-chart="band" data-band={row.id} />;
}

export function Trend({ row }: { row: Row }) {
  const pts = useMemo(() => (row.spark ? row.spark.t.map((t, i) => ({ t, v: row.spark!.v[i] })) : []), [row]);
  const [at, setAt] = useState<number | null>(null);
  if (pts.length < 2) return <span className="text-[11px] text-muted" title="A trend line needs two points held.">not held yet</span>;
  const W = 104, H = 24, pad = 3;
  const vs = pts.map((p) => p.v), lo = Math.min(...vs), hi = Math.max(...vs);
  const x = (i: number) => pad + (i * (W - 2 * pad)) / (pts.length - 1);
  const y = (v: number) => (hi === lo ? H / 2 : pad + ((hi - v) * (H - 2 * pad)) / (hi - lo));
  const p = at === null ? null : pts[at];
  return (
    <span className="relative inline-block align-middle" data-trend={row.id}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} role="img" className="block"
        aria-label={`${row.label}, ${row.at}: last ${pts.length} values, ${fmt(pts[0].v, row.unit)} on ${dateWords(pts[0].t, row.freq)} to ${fmt(pts[pts.length - 1].v, row.unit)} on ${dateWords(pts[pts.length - 1].t, row.freq)}`}
        onMouseMove={(e) => { const b = e.currentTarget.getBoundingClientRect(); setAt(Math.max(0, Math.min(pts.length - 1, Math.round(((e.clientX - b.left - pad) / (b.width - 2 * pad)) * (pts.length - 1))))); }}
        onMouseLeave={() => setAt(null)}>
        {lo < 0 && hi > 0 ? <line x1={pad} x2={W - pad} y1={y(0)} y2={y(0)} stroke="var(--color-rule)" strokeWidth={1} /> : null}
        <polyline points={pts.map((q, i) => `${x(i).toFixed(1)},${y(q.v).toFixed(1)}`).join(" ")} fill="none" stroke="var(--color-accent)" strokeWidth={1.3} strokeLinejoin="round" />
        <circle cx={x(at ?? pts.length - 1)} cy={y((p ?? pts[pts.length - 1]).v)} r={2.2} fill="var(--color-accent)" />
        {at !== null ? <line x1={x(at)} x2={x(at)} y1={0} y2={H} stroke="var(--color-muted)" strokeWidth={0.6} /> : null}
      </svg>
      {p ? (
        <span role="tooltip" className="pointer-events-none absolute bottom-full right-0 z-20 mb-1 whitespace-nowrap border border-rule bg-white px-2 py-1 text-left text-[11px] leading-tight text-ink shadow-sm">
          <span className="block text-muted">{row.label}, {row.at}</span>
          <span className="block"><strong>{fmt(p.v, row.unit)}</strong> {row.unit} on {dateWords(p.t, row.freq)}</span>
        </span>
      ) : null}
    </span>
  );
}
