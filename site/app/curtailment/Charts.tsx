"use client";
// Energy Research Warehouse (ERW) site, session 144: the charts of the one curtailment page (/curtailment), on the
// site's one chart library (components/echarts.ts). Two charts, each drawn from plain arrays the page computes on the
// server, and each answers the mouse:
//   XY    bars, lines and areas over a category axis (days, months, hours of the day, hours), stacked where asked, a
//         second axis for a share; the tooltip names the category, then each series with its value and unit, then the
//         page's own line for that category where it has one (the days held, the reason a share is missing)
//   Heat  a grid of cells, months by hours of the day; the tooltip is the page's own text for the cell, and a cell
//         with no hour held is drawn grey and says so
// A value that is not held is a gap, never a filled point.
import { baseStyle, token, useEChart } from "@/components/echarts";

export type S = {
  name: string; color: string; values: (number | null)[]; kind?: "bar" | "line" | "area"; stack?: string; axis?: 0 | 1; unit?: string; dash?: boolean;
  /** decimals in the tooltip (default: none from 100 up, else two) */
  digits?: number;
};
const col = (c: string) => (c.startsWith("var(") || c.startsWith("--") ? token(c) : c);
const fmt = (v: number, digits?: number) => v.toLocaleString("en-US", digits === undefined ? { maximumFractionDigits: Math.abs(v) >= 100 ? 0 : 2 } : { minimumFractionDigits: digits, maximumFractionDigits: digits });
type Tip = { seriesName: string; value: number | null | undefined | { value: number | null }; marker: string; name: string; seriesIndex: number; dataIndex: number };
const valueOf = (p: Tip): number | null => { const v = typeof p.value === "object" && p.value !== null ? p.value.value : p.value; return v === null || v === undefined || Number.isNaN(v) ? null : Number(v); };

export function XY({ id, x, series, unit, unit2, label, height = 280, notes, dim, zoom, every, zero = true }: {
  /** the chart's name in the page (data-chart) and of its PNG */
  id: string; x: string[]; series: S[]; unit: string; unit2?: string; label: string; height?: number;
  /** one more tooltip line per category */
  notes?: (string | null)[];
  /** categories drawn faint (the months outside the period chosen) */
  dim?: boolean[];
  /** a range slider under a long axis */
  zoom?: boolean; every?: number; zero?: boolean;
}) {
  const box = useEChart((chart) => {
    const st = baseStyle();
    const two = series.some((s) => s.axis === 1);
    chart.setOption({
      textStyle: st.textStyle, animation: false, toolbox: st.toolbox(id),
      tooltip: { ...st.tooltip, trigger: "axis", axisPointer: { type: series.some((s) => (s.kind ?? "bar") === "bar") ? "shadow" : "line" },
        formatter: (ps: Tip[]) => {
          const i = ps[0].dataIndex;
          const lines = ps.map((p) => ({ p, v: valueOf(p) })).filter((r) => r.v !== null)
            .map(({ p, v }) => `${p.marker}${p.seriesName}: <b>${fmt(v as number, series[p.seriesIndex].digits)}</b> ${series[p.seriesIndex].unit ?? (series[p.seriesIndex].axis === 1 ? unit2 ?? "" : unit)}`);
          return [`<strong>${x[i]}</strong>`, ...(lines.length ? lines : ["not held"]), ...(notes?.[i] ? [`<span style="opacity:.75">${notes[i]}</span>`] : [])].join("<br/>");
        } },
      grid: { left: 64, right: two ? 54 : 16, top: 30, bottom: zoom ? 58 : 28 },
      xAxis: { type: "category", data: x, ...st.axis, axisLabel: { ...st.axis.axisLabel, interval: every ?? "auto" }, splitLine: { show: false } },
      yAxis: [{ type: "value", name: unit, scale: !zero, ...st.axis }, { type: "value", name: unit2 ?? "", show: two, ...st.axis, splitLine: { show: false } }],
      ...(zoom ? { dataZoom: [{ type: "slider", height: 18, bottom: 6, borderColor: token("rule"), textStyle: { color: token("muted"), fontSize: 10 } }, { type: "inside" }] } : {}),
      series: series.map((s) => {
        const kind = s.kind ?? "bar", c = col(s.color);
        const data = s.values.map((v, i) => (dim?.[i] ? { value: v, itemStyle: { opacity: 0.4 } } : v));
        if (kind === "bar") return { name: s.name, type: "bar", stack: s.stack, yAxisIndex: s.axis ?? 0, itemStyle: { color: c }, barMaxWidth: 34, data, emphasis: { focus: "none" } };
        return { name: s.name, type: "line", stack: s.stack, yAxisIndex: s.axis ?? 0, showSymbol: x.length <= 40, symbolSize: 4, connectNulls: false, itemStyle: { color: c },
          lineStyle: { width: kind === "area" ? 1 : 2, color: c, type: s.dash ? "dashed" : "solid" }, ...(kind === "area" ? { areaStyle: { color: c, opacity: 0.4 } } : {}), data, z: 5 };
      }),
    }, true);
  }, [id, x, series, unit, unit2, label, notes, dim, zoom, every, zero]);
  return <div ref={box} role="img" aria-label={label} data-chart={id} style={{ height }} className="w-full" />;
}

export function Heat({ id, hours, months, values, tips, most, label, height = 330 }: {
  id: string; hours: string[]; months: string[];
  /** [month][hour]: the count, or null where no hour of the cell is held */
  values: (number | null)[][];
  /** [month][hour]: the cell's own text */
  tips: string[][]; most: number; label: string; height?: number;
}) {
  const box = useEChart((chart) => {
    const st = baseStyle();
    const held: [number, number, number][] = [], blank: [number, number, number][] = [];
    values.forEach((row, m) => row.forEach((v, h) => (v === null ? blank : held).push([h, m, v ?? 0])));
    chart.setOption({
      textStyle: st.textStyle, animation: false, toolbox: st.toolbox(id),
      tooltip: { ...st.tooltip, trigger: "item", formatter: (p: { value: [number, number, number] }) => tips[p.value[1]]?.[p.value[0]] ?? "" },
      grid: { left: 70, right: 16, top: 30, bottom: 62 },
      xAxis: { type: "category", data: hours, ...st.axis, splitArea: { show: false }, splitLine: { show: false } },
      yAxis: { type: "category", data: months, inverse: true, ...st.axis, splitLine: { show: false } },
      visualMap: { type: "continuous", seriesIndex: 0, min: 0, max: Math.max(1, most), calculable: false, orient: "horizontal", left: "center", bottom: 4, itemHeight: 160, itemWidth: 10,
        text: [`${Math.max(1, most)} hours`, "0"], textStyle: { color: token("muted"), fontSize: 11 }, inRange: { color: [token("surface"), token("duration-1"), token("duration-3"), token("duration-4")] } },
      series: [
        { name: "held", type: "heatmap", data: held, itemStyle: { borderColor: token("rule"), borderWidth: 0.5 }, emphasis: { itemStyle: { borderColor: token("ink"), borderWidth: 1 } } },
        { name: "not held", type: "heatmap", data: blank, itemStyle: { color: token("rule"), opacity: 0.45, borderColor: token("surface"), borderWidth: 0.5 } },
      ],
    }, true);
  }, [id, hours, months, values, tips, most, label]);
  return <div ref={box} role="img" aria-label={label} data-chart={id} style={{ height }} className="w-full" />;
}
