"use client";
// Every time series on the site (session 22): lines or stacked areas on ECharts, with hover values in
// their unit, zoom and pan (drag, wheel), a range slider, legend toggles and a download-as-PNG control.
// `mini` is the home page's sparkline: hover and zoom only, no axes, legend, slider or toolbox.
import { baseStyle, num, token, useEChart } from "./echarts";

export type TimeSeries = {
  name: string;
  color: string; // a token name ("accent") or a CSS variable ("var(--color-fuel-gas)")
  points: [number, number | null][]; // [time in ms, value]
  step?: boolean;
  dashed?: boolean;
};

type Props = {
  series: TimeSeries[];
  unit: string;
  ariaLabel: string;
  height?: number;
  stack?: boolean; // stacked areas (a mix); negative values are shown as they are, not stacked away
  x?: "minute" | "day" | "month" | "year";
  mini?: boolean;
  file?: string; // the PNG's file name
};

const FMT: Record<string, (t: number) => string> = {
  minute: (t) => new Date(t).toISOString().slice(0, 16).replace("T", " ") + " UTC",
  day: (t) => new Date(t).toISOString().slice(0, 10),
  month: (t) => new Date(t).toISOString().slice(0, 7),
  year: (t) => new Date(t).toISOString().slice(0, 4),
};

export function TimeChart({ series, unit, ariaLabel, height = 260, stack = false, x = "minute", mini = false, file = "erw-chart" }: Props) {
  const box = useEChart(
    (chart) => {
      const st = baseStyle();
      const fmt = FMT[x];
      chart.setOption(
        {
          animation: false,
          textStyle: st.textStyle,
          grid: mini ? { left: 2, right: 2, top: 4, bottom: 4 } : { left: 58, right: 14, top: series.length > 1 ? 52 : 26, bottom: 58 },
          legend: mini || series.length < 2 ? undefined : { top: 0, left: 0, right: 40, type: "scroll", textStyle: { color: token("ink"), fontSize: 11 }, itemWidth: 14, itemHeight: 8 },
          toolbox: mini ? undefined : st.toolbox(file),
          tooltip: {
            ...st.tooltip,
            trigger: "axis",
            axisPointer: { type: "line", lineStyle: { color: token("muted") } },
            formatter: (ps: { axisValue: number; seriesName: string; value: [number, number | null]; color: string }[]) => {
              const rows = ps.filter((p) => p.value[1] !== null && p.value[1] !== undefined);
              if (!rows.length) return "";
              return `${fmt(ps[0].axisValue)}<br/>` + rows.map((p) => `<span style="color:${p.color}">&#9632;</span> ${p.seriesName}: ${num(p.value[1] as number)} ${unit}`).join("<br/>");
            },
          },
          xAxis: {
            type: "time",
            show: !mini,
            ...st.axis,
            splitLine: { show: false },
            axisLabel: { ...st.axis.axisLabel, hideOverlap: true },
          },
          yAxis: {
            type: "value",
            show: !mini,
            scale: !stack,
            name: mini ? undefined : unit,
            nameLocation: "end",
            ...st.axis,
            axisLabel: { ...st.axis.axisLabel, formatter: (v: number) => (Math.abs(v) >= 1e6 ? `${v / 1e6}M` : Math.abs(v) >= 1e4 ? `${v / 1e3}k` : String(v)) },
          },
          dataZoom: mini
            ? [{ type: "inside", filterMode: "none" }]
            : [
                { type: "inside", filterMode: "none" },
                { type: "slider", height: 18, bottom: 6, filterMode: "none", borderColor: token("rule"), textStyle: { color: token("muted"), fontSize: 10 }, labelFormatter: (v: number) => fmt(v) },
              ],
          series: series.map((s) => {
            const color = token(s.color);
            return {
              name: s.name,
              type: "line",
              data: s.points,
              showSymbol: false,
              connectNulls: false,
              step: s.step ? "end" : false,
              sampling: "lttb",
              color,
              lineStyle: { width: stack ? 0.6 : 1.5, type: s.dashed ? "dashed" : "solid", color },
              ...(stack ? { stack: "total", areaStyle: { color, opacity: 0.85 }, emphasis: { focus: "series" } } : {}),
            };
          }),
        },
        true,
      );
    },
    [series, unit, stack, x, mini],
  );
  return <div ref={box} role="img" aria-label={ariaLabel} className="w-full" style={{ height }} />;
}
