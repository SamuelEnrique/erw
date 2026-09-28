"use client";
// Five-number summaries as horizontal boxes on one scale (session 22): the ERCOT peak-premium
// explorer's time-of-day blocks. Hover gives the five numbers; zoom along the price axis; PNG download.
import { baseStyle, num, token, useEChart } from "./echarts";

export type BoxRow = { name: string; stats: [number, number, number, number, number] }; // min, q1, median, q3, max

export function BoxChart({ rows, unit, ariaLabel, file = "erw-boxes" }: { rows: BoxRow[]; unit: string; ariaLabel: string; file?: string }) {
  const box = useEChart(
    (chart) => {
      const st = baseStyle();
      const q1 = Math.min(...rows.map((r) => r.stats[1])), q3 = Math.max(...rows.map((r) => r.stats[3]));
      const pad = Math.max(10, (q3 - q1) * 1.5);
      chart.setOption(
        {
          animation: false,
          textStyle: st.textStyle,
          grid: { left: 96, right: 16, top: 26, bottom: 52 },
          toolbox: st.toolbox(file),
          tooltip: {
            ...st.tooltip,
            trigger: "item",
            formatter: (p: { name: string; value: number[] }) => {
              const v = p.value.slice(-5);
              return `${p.name}<br/>min ${num(v[0])}, Q1 ${num(v[1])}, median ${num(v[2])}, Q3 ${num(v[3])}, max ${num(v[4])} ${unit}`;
            },
          },
          yAxis: { type: "category", data: rows.map((r) => r.name), ...st.axis, splitLine: { show: false } },
          xAxis: { type: "value", name: unit, nameLocation: "end", ...st.axis, min: Math.floor(q1 - pad), max: Math.ceil(q3 + pad) },
          dataZoom: [
            { type: "inside", xAxisIndex: 0, filterMode: "none" },
            { type: "slider", xAxisIndex: 0, height: 16, bottom: 6, filterMode: "none", borderColor: token("rule") },
          ],
          series: [{
            type: "boxplot",
            data: rows.map((r) => r.stats),
            itemStyle: { color: token("panel"), borderColor: token("ink") },
            emphasis: { itemStyle: { borderColor: token("accent") } },
            markPoint: undefined,
          }, {
            type: "scatter",
            name: "median",
            data: rows.map((r, i) => [r.stats[2], i]),
            symbol: "rect",
            symbolSize: [3, 18],
            color: token("accent"),
            tooltip: { formatter: (p: { value: number[] }) => `median ${num(p.value[0])} ${unit}` },
          }],
        },
        true,
      );
    },
    [rows, unit],
  );
  return <div ref={box} role="img" aria-label={ariaLabel} className="w-full" style={{ height: 40 + rows.length * 44 + 40 }} />;
}
