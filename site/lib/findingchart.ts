// Energy Research Warehouse (ERW) site, session 170: a finding card's chart, from the spec the finding wrote
// (warehouse/analysis/findings/<name>.py, card["chart"]) to an ECharts option. Pure: no fs, no fetch, so the card page,
// the render page and the tests share it. Every chart answers the mouse: the tooltip names every series at the point.

export type ChartSeries = {
  name: string; type: "line" | "bar"; unit: string; axis?: string; values: (number | null)[];
  sensitivity?: Record<string, (number | null)[]>; hours?: (number | null)[]; gw?: (number | null)[];
};
export type ChartSpec = {
  kind: "line_with_fleet" | "grouped_bar" | "stacked_bar_pct"; x: string[]; x_label: string; series: ChartSeries[];
  y_left_label?: string; y_right_label?: string; placeholders?: { grid: string; words: string; text: string }[];
  reference?: { name: string; value: number }; requested_gw?: number[]; projects?: number[];
};

const INK = "#1a1a1a", MUTED = "#6b6b6b", RULE = "#e5e5e5";
const PALETTE = ["#1f5f8b", "#c4541c", "#2e7d4f", "#8a6d3b", "#6a4c93", "#9a9a9a"];
const fmt = (v: number | null | undefined, nd = 1) => (v === null || v === undefined || Number.isNaN(v) ? "not held" : v.toLocaleString("en-US", { maximumFractionDigits: nd, minimumFractionDigits: nd }));

const base = (xLabel: string, x: string[]) => ({
  animation: false,
  textStyle: { fontFamily: "Inter, system-ui, sans-serif", color: INK },
  grid: { left: 56, right: 64, top: 36, bottom: 56, containLabel: false },
  xAxis: { type: "category" as const, data: x, name: xLabel, nameLocation: "middle" as const, nameGap: 34,
    axisLabel: { color: MUTED, fontSize: 11 }, axisLine: { lineStyle: { color: RULE } }, nameTextStyle: { color: MUTED, fontSize: 11 } },
  legend: { top: 0, textStyle: { color: MUTED, fontSize: 11 } },
});

export function optionFor(c: ChartSpec): Record<string, unknown> {
  if (c.kind === "line_with_fleet") {
    const [mult, hours, fleet] = c.series;
    return {
      ...base(c.x_label, c.x),
      tooltip: { trigger: "axis", confine: true, formatter: (ps: { axisValue: string; seriesName: string; value: number | null }[]) =>
        [ps[0]?.axisValue, ...ps.map((p) => `${p.seriesName}: ${fmt(p.value, p.seriesName.includes("MW") ? 0 : p.seriesName.includes("Hours") ? 2 : 1)}`)].join("<br/>") },
      yAxis: [
        { type: "value", name: c.y_left_label ?? "", position: "left", axisLabel: { color: MUTED, fontSize: 11 }, splitLine: { lineStyle: { color: RULE } }, nameTextStyle: { color: MUTED, fontSize: 11 } },
        { type: "value", name: c.y_right_label ?? "", position: "right", axisLabel: { color: MUTED, fontSize: 11 }, splitLine: { show: false }, nameTextStyle: { color: MUTED, fontSize: 11 } },
      ],
      series: [
        { name: mult.name, type: "line", yAxisIndex: 0, data: mult.values, showSymbol: false, lineStyle: { width: 1.5, color: PALETTE[0] }, itemStyle: { color: PALETTE[0] } },
        { name: hours.name, type: "bar", yAxisIndex: 0, data: hours.values, itemStyle: { color: PALETTE[1], opacity: 0.7 } },
        { name: fleet.name, type: "line", yAxisIndex: 1, data: fleet.values, showSymbol: false, areaStyle: { color: PALETTE[2], opacity: 0.12 }, lineStyle: { width: 1.5, color: PALETTE[2] }, itemStyle: { color: PALETTE[2] } },
      ],
    };
  }
  if (c.kind === "grouped_bar") {
    return {
      ...base(c.x_label, c.x),
      tooltip: { trigger: "axis", confine: true, formatter: (ps: { axisValue: string; seriesName: string; seriesIndex: number; dataIndex: number; value: number | null }[]) => {
        const lines = [ps[0]?.axisValue];
        for (const p of ps) {
          const s = c.series[p.seriesIndex];
          const sens = s.sensitivity ? Object.entries(s.sensitivity).map(([k, v]) => `${k}: ${fmt(v[p.dataIndex])}%`).join(", ") : "";
          const h = s.hours?.[p.dataIndex];
          lines.push(`${p.seriesName}: ${fmt(p.value)}%${h ? ` of ${h.toLocaleString("en-US")} hours` : ""}${sens ? ` (${sens})` : ""}`);
        }
        return lines.join("<br/>");
      } },
      yAxis: { type: "value", name: c.y_left_label ?? "", max: 100, axisLabel: { color: MUTED, fontSize: 11 }, splitLine: { lineStyle: { color: RULE } }, nameTextStyle: { color: MUTED, fontSize: 11 } },
      series: c.series.map((s, i) => ({ name: s.name, type: "bar", data: s.values, itemStyle: { color: PALETTE[i % PALETTE.length] } })),
    };
  }
  // stacked_bar_pct: one bar per technology, the statuses stacked to 100, a reference line for the CDC ratio
  return {
    ...base(c.x_label, c.x),
    grid: { left: 56, right: 24, top: 36, bottom: 72 },
    tooltip: { trigger: "axis", confine: true, formatter: (ps: { axisValue: string; seriesName: string; seriesIndex: number; dataIndex: number; value: number | null }[]) => {
      const i = ps[0]?.dataIndex ?? 0;
      const head = `${ps[0]?.axisValue}: ${fmt(c.requested_gw?.[i] ?? null, 0)} GW requested, ${(c.projects?.[i] ?? 0).toLocaleString("en-US")} requests`;
      return [head, ...ps.map((p) => `${p.seriesName}: ${fmt(p.value)}% (${fmt(c.series[p.seriesIndex].gw?.[p.dataIndex] ?? null, 0)} GW)`)].join("<br/>");
    } },
    yAxis: { type: "value", name: c.y_left_label ?? "", max: 100, axisLabel: { color: MUTED, fontSize: 11 }, splitLine: { lineStyle: { color: RULE } }, nameTextStyle: { color: MUTED, fontSize: 11 } },
    series: [
      ...c.series.map((s, i) => ({ name: s.name, type: "bar", stack: "pct", data: s.values, itemStyle: { color: PALETTE[i % PALETTE.length] } })),
      ...(c.reference ? [{ name: c.reference.name, type: "line", data: [], markLine: { silent: true, symbol: "none", data: [{ yAxis: c.reference.value, name: c.reference.name }],
        lineStyle: { color: INK, type: "dashed" }, label: { formatter: `${c.reference.name}: ${fmt(c.reference.value, 0)}%`, position: "insideEndTop", color: INK, fontSize: 11 } } }] : []),
    ],
  };
}
