"use client";
// A single stacked bar of shares (session 22): the day's generation mix on /grid and /mix. Hover gives
// each part in its unit and as a share; the legend toggles parts; a PNG download. Negative parts
// (storage charging) are not drawn and are said so by the caller.
import { baseStyle, num, token, useEChart } from "./echarts";

export type Part = { name: string; value: number; color: string };

export function ShareBar({ parts, unit, ariaLabel, file = "erw-mix" }: { parts: Part[]; unit: string; ariaLabel: string; file?: string }) {
  const pos = parts.filter((p) => p.value > 0);
  const total = pos.reduce((a, p) => a + p.value, 0);
  const box = useEChart(
    (chart) => {
      const st = baseStyle();
      chart.setOption(
        {
          animation: false,
          textStyle: st.textStyle,
          grid: { left: 0, right: 0, top: 30, bottom: 0 },
          legend: { top: 0, left: 0, right: 40, type: "scroll", textStyle: { color: token("ink"), fontSize: 11 }, itemWidth: 12, itemHeight: 8 },
          toolbox: st.toolbox(file),
          tooltip: {
            ...st.tooltip,
            trigger: "item",
            formatter: (p: { seriesName: string; value: number; color: string }) =>
              `<span style="color:${p.color}">&#9632;</span> ${p.seriesName}: ${num(p.value)} ${unit} (${((100 * p.value) / total).toFixed(1)}%)`,
          },
          xAxis: { type: "value", show: false, max: "dataMax" },
          yAxis: { type: "category", show: false, data: ["mix"] },
          series: pos.map((p) => ({ name: p.name, type: "bar", stack: "mix", data: [p.value], color: token(p.color), barWidth: 22, itemStyle: { borderColor: token("panel"), borderWidth: 1 } })),
        },
        true,
      );
    },
    [parts, unit],
  );
  return <div ref={box} role="img" aria-label={ariaLabel} className="w-full" style={{ height: 60 }} />;
}
