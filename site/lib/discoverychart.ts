// Energy Research Warehouse (ERW) site, session 181: the chart of a scanner draft and of the impact study, from the
// spec the engine wrote (kind "flag_line") to an ECharts option. One or two lines over days; the flagged point marked
// with a dot; the record or the threshold as dashed reference lines; the days compared as a shaded band. Pure: no fs,
// no fetch. Hover names every series at the day, with its unit.
import type { ChartSpec } from "./findingchart";

const INK = "#1a1a1a", MUTED = "#6b6b6b", RULE = "#e5e5e5", MARK = "#c4541c";
const PALETTE = ["#1f5f8b", "#8a6d3b", "#2e7d4f", "#6a4c93"];
const fmt = (v: number | null | undefined, nd: number) =>
  v === null || v === undefined || Number.isNaN(v) ? "not held" : v.toLocaleString("en-US", { maximumFractionDigits: nd, minimumFractionDigits: nd });

export function discoveryOption(c: ChartSpec): Record<string, unknown> {
  const nd = c.decimals ?? 2;
  const area = c.mark_area;
  // the band's ends as days the axis holds (a day without a value is not on a category axis)
  const from = area ? c.x.find((d) => d >= area.from) ?? c.x[c.x.length - 1] : undefined;
  const to = area ? [...c.x].reverse().find((d) => d <= area.to) ?? c.x[c.x.length - 1] : undefined;
  return {
    animation: false,
    textStyle: { fontFamily: "Inter, system-ui, sans-serif", color: INK },
    grid: { left: 64, right: 24, top: 36, bottom: 72 },
    legend: { top: 0, textStyle: { color: MUTED, fontSize: 11 } },
    xAxis: { type: "category", data: c.x, name: c.x_label, nameLocation: "middle", nameGap: 34,
      axisLabel: { color: MUTED, fontSize: 11 }, axisLine: { lineStyle: { color: RULE } }, nameTextStyle: { color: MUTED, fontSize: 11 } },
    yAxis: { type: "value", name: c.y_left_label ?? "", scale: true, axisLabel: { color: MUTED, fontSize: 11 }, splitLine: { lineStyle: { color: RULE } }, nameTextStyle: { color: MUTED, fontSize: 11 } },
    tooltip: { trigger: "axis", confine: true, formatter: (ps: { axisValue: string; seriesName: string; seriesIndex: number; value: number | null }[]) => {
      const lines = [ps[0]?.axisValue + (c.mark && ps[0]?.axisValue === c.mark.x ? ` (flagged: ${c.mark.label})` : "")];
      for (const p of ps) lines.push(`${p.seriesName}: ${fmt(p.value, nd)} ${c.series[p.seriesIndex]?.unit ?? ""}`);
      for (const r of c.ref_lines ?? []) lines.push(`${r.name}: ${fmt(r.value, nd)}`);
      if (c.band_words) lines.push(c.band_words);
      return lines.join("<br/>");
    } },
    series: c.series.map((s, i) => ({
      name: s.name, type: "line", data: s.values, showSymbol: c.x.length <= 60, symbolSize: 4, connectNulls: false,
      lineStyle: { width: 1.5, color: PALETTE[i % PALETTE.length] }, itemStyle: { color: PALETTE[i % PALETTE.length] },
      ...(i === 0 && c.mark ? { markPoint: { symbol: "circle", symbolSize: 11, silent: true, data: [{ coord: [c.mark.x, c.mark.value] }], itemStyle: { color: MARK }, label: { show: false } } } : {}),
      ...(i === 0 && c.ref_lines?.length ? { markLine: { silent: true, symbol: "none", data: c.ref_lines.map((r) => ({ yAxis: r.value, name: r.name })),
        lineStyle: { type: "dashed", color: MUTED }, label: { formatter: "{b}", position: "insideEndTop", color: MUTED, fontSize: 10 } } } : {}),
      ...(i === 0 && area && from && to ? { markArea: { silent: true, itemStyle: { color: MARK, opacity: 0.1 }, label: { color: MUTED, fontSize: 10 },
        data: [[{ xAxis: from, name: area.label }, { xAxis: to }]] } } : {}),
    })),
  };
}
