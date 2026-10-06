"use client";
// Energy Research Warehouse (ERW) site, session 135: the charts of Thesis Builder (/thesis). Both answer the mouse
// with the series, the category and the value with its unit, and neither offers a download: a run is never exported.
//
//   TrendChart    a trend's own table as bars or a line (lib/thesis/view.ts, chartOf: a cell that is not a number is
//                 left out, never drawn as zero)
//   FunnelChart   the deal funnel's stages, one bar each, in the order the report gives them
import { baseStyle, token, useEChart } from "@/components/echarts";
import { num, type ChartData } from "@/lib/thesis/view";

// the report's words reach a tooltip as HTML: they are written as text
const esc = (s: string) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c] as string);
// the site's categorical colors in their fixed order (app/tokens.css); a chart of one series is drawn in the accent
const ORDER = ["fuel-gas", "fuel-coal", "fuel-nuclear", "fuel-wind", "fuel-solar", "fuel-hydro", "fuel-storage", "fuel-other"];

export function TrendChart({ data, height = 280 }: { data: ChartData; height?: number }) {
  const box = useEChart((chart) => {
    const st = baseStyle();
    const many = data.series.length > 1;
    const color = (i: number) => (many ? token(ORDER[i % ORDER.length]) : token("accent"));
    const unit = data.unit ? ` ${esc(data.unit)}` : "";
    chart.setOption({
      textStyle: st.textStyle, animation: false,
      legend: many ? { type: "scroll", top: 0, left: 0, textStyle: { fontSize: 11 }, itemWidth: 14, itemHeight: 8 } : undefined,
      tooltip: { ...st.tooltip, trigger: "axis", axisPointer: { type: data.kind === "bar" ? "shadow" : "line" }, formatter: (ps: { dataIndex: number; seriesIndex: number }[]) => {
        const i = ps[0].dataIndex;
        const lines = ps.map((p) => { const s = data.series[p.seriesIndex]; const v = s.data[i]; return v === null || v === undefined ? "" : `<br/>${esc(s.name)}: <b>${num(v)}</b>${unit}`; }).join("");
        return `${esc(data.categories[i])}${lines}`;
      } },
      grid: { left: 8, right: 14, top: many ? 30 : 12, bottom: 6, containLabel: true },
      xAxis: { type: "category", data: data.categories, boundaryGap: data.kind === "bar", ...st.axis, axisLabel: { ...st.axis.axisLabel, hideOverlap: true, width: 96, overflow: "truncate" }, splitLine: { show: false } },
      yAxis: { type: "value", scale: data.kind === "line", ...st.axis },      // the unit is in the caption above and in every hover
      series: data.series.map((s, i) => (data.kind === "bar"
        ? { name: s.name, type: "bar", data: s.data, barMaxWidth: 28, barGap: "8%", itemStyle: { color: color(i), borderRadius: [3, 3, 0, 0] } }
        : { name: s.name, type: "line", data: s.data, connectNulls: false, symbolSize: 7, lineStyle: { width: 2, color: color(i) }, itemStyle: { color: color(i) } })),
    }, true);
  }, [data]);
  return <div ref={box} role="img" aria-label={`${data.title}${data.unit ? `, ${data.unit}` : ""}: ${data.series.map((s) => s.name).join(", ")} by ${data.categories.length} categories; the table below holds the same values`} style={{ height }} className="w-full" data-chart="trend" />;
}

export function FunnelChart({ stages }: { stages: { id: string; label: string; n: number }[] }) {
  const box = useEChart((chart) => {
    const st = baseStyle();
    chart.setOption({
      textStyle: st.textStyle, animation: false,
      tooltip: { ...st.tooltip, trigger: "axis", axisPointer: { type: "shadow" }, formatter: (ps: { dataIndex: number }[]) => {
        const s = stages[ps[0].dataIndex];
        return `Deal funnel<br/>${esc(s.label)}: <b>${num(s.n)}</b> ${s.n === 1 ? "company" : "companies"}`;
      } },
      grid: { left: 8, right: 44, top: 6, bottom: 6, containLabel: true },
      xAxis: { type: "value", minInterval: 1, ...st.axis },
      yAxis: { type: "category", inverse: true, data: stages.map((s) => s.label), ...st.axis, axisLabel: { ...st.axis.axisLabel, width: 190, overflow: "break" }, splitLine: { show: false } },
      series: [{ name: "Deal funnel", type: "bar", data: stages.map((s) => s.n), barMaxWidth: 22, itemStyle: { color: token("accent"), borderRadius: [0, 3, 3, 0] },
        label: { show: true, position: "right", color: token("ink"), fontSize: 11, formatter: (p: { value: number }) => num(p.value) } }],
    }, true);
  }, [stages]);
  return <div ref={box} role="img" aria-label={`Deal funnel: ${stages.map((s) => `${s.label} ${s.n}`).join(", ")}`} style={{ height: Math.max(140, 40 + stages.length * 34) }} className="w-full" data-chart="funnel" />;
}
