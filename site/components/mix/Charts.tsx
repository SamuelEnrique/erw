"use client";
// Energy Research Warehouse (ERW) site, session 133: the charts of the one energy mix page (/mix).
//
// Four charts on the site's one chart library (components/echarts.ts), each drawn from plain arrays the page computes on
// the server. Every one answers the mouse with the value, the hour or date, and the series. A value that is not held
// is a gap, never a filled point.
//   HourStack  generation by source as stacked areas over a category axis (the 24 local hours), with lines over it
//              (demand) and, when a factor is chosen, lines on a second axis (price, temperature, carbon, imports)
//   Lines      lines over a category axis: years, grids or fuels laid over each other, a second axis when asked
//   Bars       grouped bars over a category axis
//   Heat       a grid of cells (months by hours)
import { baseStyle, token, useEChart } from "@/components/echarts";

export type Series = { name: string; color: string; values: (number | null)[]; axis?: 0 | 1; dash?: "solid" | "dashed" | "dotted"; width?: number; unit?: string };
const col = (c: string) => (c.startsWith("var(") || c.startsWith("--") ? token(c) : c);
const num = (v: number, digits = 1) => v.toLocaleString("en-US", { maximumFractionDigits: Math.abs(v) >= 100 ? 0 : digits });

type Tip = { seriesName: string; value: number | null | undefined; marker: string; name: string; seriesIndex: number };
/** The tooltip of a category chart: the x label (the hour, the year), then each series with its value and unit. */
function tip(units: (string | undefined)[], what: string) {
  return (ps: Tip[]) => `${what ? `${what}, ` : ""}${ps[0].name}<br/>` + ps.filter((p) => p.value !== null && p.value !== undefined && !Number.isNaN(p.value))
    .map((p) => `${p.marker}${p.seriesName}: <b>${num(Number(p.value))}</b> ${units[p.seriesIndex] ?? ""}`).join("<br/>");
}
const legend = (st: ReturnType<typeof baseStyle>) => ({ type: "scroll", top: 0, left: 0, right: 30, textStyle: { fontSize: 11, color: st.textStyle.color }, itemWidth: 14, itemHeight: 8 });

export function HourStack({ x, layers, lines, unit, unit2, label, height = 300, name }: { x: string[]; layers: Series[]; lines: Series[]; unit: string; unit2?: string; label: string; height?: number; name: string }) {
  const box = useEChart((chart) => {
    const st = baseStyle();
    const two = lines.some((l) => l.axis === 1);
    const all = [...layers, ...lines];
    chart.setOption({
      textStyle: st.textStyle, animation: false, legend: legend(st), toolbox: st.toolbox(name),
      tooltip: { ...st.tooltip, trigger: "axis", formatter: tip(all.map((s) => s.unit ?? (s.axis === 1 ? unit2 : unit)), label) },
      grid: { left: 58, right: two ? 58 : 14, top: 48, bottom: 26 },
      xAxis: { type: "category", data: x, boundaryGap: false, ...st.axis, splitLine: { show: false } },
      yAxis: [{ type: "value", name: unit, ...st.axis }, { type: "value", name: unit2 ?? "", show: two, scale: true, ...st.axis, splitLine: { show: false } }],
      series: [
        ...layers.map((l) => ({ name: l.name, type: "line", stack: "mix", showSymbol: false, lineStyle: { width: 0 }, areaStyle: { color: col(l.color), opacity: 0.9 }, itemStyle: { color: col(l.color) }, data: l.values, emphasis: { focus: "series" } })),
        ...lines.map((l) => ({ name: l.name, type: "line", showSymbol: false, connectNulls: false, yAxisIndex: l.axis ?? 0, lineStyle: { width: l.width ?? 1.8, color: col(l.color), type: l.dash ?? "solid" }, itemStyle: { color: col(l.color) }, data: l.values, z: 5 })),
      ],
    }, true);
  }, [x, layers, lines, unit, unit2, label, name]);
  return <div ref={box} role="img" aria-label={label} style={{ height }} className="w-full" data-chart="stack" />;
}

export function Lines({ x, series, unit, unit2, label, height = 300, name, zero, every }: { x: string[]; series: Series[]; unit: string; unit2?: string; label: string; height?: number; name: string; zero?: boolean; every?: number }) {
  const box = useEChart((chart) => {
    const st = baseStyle();
    const two = series.some((l) => l.axis === 1);
    chart.setOption({
      textStyle: st.textStyle, animation: false, legend: legend(st), toolbox: st.toolbox(name),
      tooltip: { ...st.tooltip, trigger: "axis", formatter: tip(series.map((s) => s.unit ?? (s.axis === 1 ? unit2 : unit)), label) },
      grid: { left: 58, right: two ? 58 : 14, top: 48, bottom: 26 },
      xAxis: { type: "category", data: x, boundaryGap: false, ...st.axis, axisLabel: { ...st.axis.axisLabel, interval: every ?? "auto" }, splitLine: { show: false } },
      yAxis: [{ type: "value", name: unit, scale: !zero, ...st.axis }, { type: "value", name: unit2 ?? "", show: two, scale: true, ...st.axis, splitLine: { show: false } }],
      series: series.map((l) => ({ name: l.name, type: "line", showSymbol: x.length <= 30 && l.values.filter((v) => v !== null).length <= 30, symbolSize: 4, connectNulls: false, yAxisIndex: l.axis ?? 0,
        lineStyle: { width: l.width ?? 1.6, color: col(l.color), type: l.dash ?? "solid" }, itemStyle: { color: col(l.color) }, data: l.values })),
    }, true);
  }, [x, series, unit, unit2, label, name, zero, every]);
  return <div ref={box} role="img" aria-label={label} style={{ height }} className="w-full" data-chart="lines" />;
}

export function Bars({ x, series, unit, label, height = 260, name }: { x: string[]; series: Series[]; unit: string; label: string; height?: number; name: string }) {
  const box = useEChart((chart) => {
    const st = baseStyle();
    chart.setOption({
      textStyle: st.textStyle, animation: false, legend: legend(st), toolbox: st.toolbox(name),
      tooltip: { ...st.tooltip, trigger: "axis", axisPointer: { type: "shadow" }, formatter: tip(series.map((s) => s.unit ?? unit), label) },
      grid: { left: 58, right: 14, top: 48, bottom: 26 },
      xAxis: { type: "category", data: x, ...st.axis, splitLine: { show: false } },
      yAxis: { type: "value", name: unit, ...st.axis },
      series: series.map((l) => ({ name: l.name, type: "bar", itemStyle: { color: col(l.color) }, data: l.values, barMaxWidth: 26 })),
    }, true);
  }, [x, series, unit, label, name]);
  return <div ref={box} role="img" aria-label={label} style={{ height }} className="w-full" data-chart="bars" />;
}

/** rows by columns; cells[r][c] is the value or null. The mouse reads the row, the column and the value. */
export function Heat({ rows, cols, cells, unit, label, height, name, marks }: { rows: string[]; cols: string[]; cells: (number | null)[][]; unit: string; label: string; height?: number; name: string; marks?: [number, number][] }) {
  const box = useEChart((chart) => {
    const st = baseStyle();
    const data: [number, number, number][] = [];
    let lo = Infinity, hi = -Infinity;
    cells.forEach((r, i) => r.forEach((v, j) => { if (v !== null && v !== undefined) { data.push([j, i, v]); lo = Math.min(lo, v); hi = Math.max(hi, v); } }));
    chart.setOption({
      textStyle: st.textStyle, animation: false, toolbox: st.toolbox(name),
      tooltip: { ...st.tooltip, trigger: "item", formatter: (p: { value: [number, number, number] }) => `${label}<br/>${rows[p.value[1]]}, ${cols[p.value[0]]}: <b>${num(p.value[2])}</b> ${unit}` },
      grid: { left: 86, right: 14, top: 26, bottom: 46 },
      xAxis: { type: "category", data: cols, ...st.axis, splitArea: { show: false }, splitLine: { show: false } },
      yAxis: { type: "category", data: rows, inverse: true, ...st.axis, splitLine: { show: false } },
      visualMap: { min: Number.isFinite(lo) ? lo : 0, max: Number.isFinite(hi) ? hi : 1, calculable: false, orient: "horizontal", left: "center", bottom: 0, itemHeight: 120, itemWidth: 10,
        textStyle: { fontSize: 10, color: token("muted") }, inRange: { color: ["#FBF8F2", token("accent")] }, formatter: (v: number) => num(v, 0) },
      series: [{ type: "heatmap", data, itemStyle: { borderColor: "#fff", borderWidth: 1 },
        markPoint: marks && marks.length ? { symbol: "rect", symbolSize: 6, silent: true, itemStyle: { color: token("ink") }, data: marks.map(([r, c]) => ({ coord: [c, r] })) } : undefined }],
    }, true);
  }, [rows, cols, cells, unit, label, name, marks]);
  return <div ref={box} role="img" aria-label={label} style={{ height: height ?? Math.max(180, 70 + rows.length * 18) }} className="w-full" data-chart="heat" />;
}
