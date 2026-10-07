"use client";
// Session 145: the four charts of "What a generator earns" (/cost-of-power/seller). Every value drawn arrives from the
// server (page.tsx; lib/capture.ts, lib/merchant.ts, lib/seller2.ts); each chart answers the mouse with the figures of
// the bar or point under it. The site's one chart library (components/echarts.ts).
import { baseStyle, token, useEChart } from "@/components/echarts";

const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const whole = (v: number) => Math.round(v).toLocaleString("en-US");
const sign = (v: number) => `${v < 0 ? "-" : "+"}${two(Math.abs(v))}`;
const short = (v: number) => (Math.abs(v) >= 1e9 ? `${two(v / 1e9)} billion` : Math.abs(v) >= 1e6 ? `${two(v / 1e6)} million` : whole(v));

export type Fig = { price: number; flat: number; premium: number; pct: number | null; hours: number } | null;
export type PremiumRow = { label: string; partial: boolean; months: number; solar: Fig; wind: Fig };

/** (a) the premium or discount to the flat average, by year and over the last twelve months, solar and wind. */
export function PremiumYears({ rows, hub, market, label }: { rows: PremiumRow[]; hub: string; market: string; label: string }) {
  const box = useEChart((chart) => {
    const s = baseStyle();
    const bar = (key: "solar" | "wind", color: string) => rows.map((r) => ({ value: r[key] ? Math.round(r[key]!.premium * 100) / 100 : null, itemStyle: { color, opacity: r.partial ? 0.4 : 1 } }));
    const line = (name: string, f: Fig) => (f
      ? `${name}: ${two(f.price)} USD/MWh received, ${sign(f.premium)}${f.pct === null ? "" : ` (${sign(f.pct)} percent)`} against a flat ${two(f.flat)}, ${whole(f.hours)} hours`
      : `${name}: not held`);
    chart.setOption({
      textStyle: s.textStyle,
      grid: { left: 56, right: 16, top: 16, bottom: 30 },
      tooltip: { ...s.tooltip, trigger: "axis", axisPointer: { type: "shadow" },
        formatter: (ps: { dataIndex: number }[]) => {
          const r = rows[ps[0].dataIndex];
          return [`<strong>${r.label}</strong>${r.partial ? ` (${r.months} of 12 months counted)` : ""}, ${hub}, ${market}`, line("Solar", r.solar), line("Wind", r.wind),
            "The grid's whole fleet by hour, not one site"].join("<br/>");
        } },
      xAxis: { type: "category", data: rows.map((r) => r.label), ...s.axis },
      yAxis: { type: "value", name: "USD/MWh", nameLocation: "middle", nameGap: 40, ...s.axis },
      series: [
        { name: "Solar", type: "bar", data: bar("solar", token("accent")), barMaxWidth: 30 },
        { name: "Wind", type: "bar", data: bar("wind", token("ink")), barMaxWidth: 30 },
      ],
    }, true);
  }, [rows, hub, market]);
  return <div ref={box} role="img" aria-label={label} data-chart="premium" style={{ height: 300 }} className="w-full" />;
}

export type YearRow = { y: string; complete: boolean; months: number; v: number };
/** Revenue (the peaker's margin) by calendar year, USD per kW of nameplate; a year short of twelve held months is pale. */
export function RevenueYears({ rows, money, label }: { rows: YearRow[]; money: string; label: string }) {
  const box = useEChart((chart) => {
    const s = baseStyle();
    chart.setOption({
      textStyle: s.textStyle,
      grid: { left: 56, right: 16, top: 16, bottom: 30 },
      tooltip: { ...s.tooltip, trigger: "axis", axisPointer: { type: "shadow" },
        formatter: (ps: { dataIndex: number }[]) => {
          const r = rows[ps[0].dataIndex];
          return `<strong>${r.y}</strong>${r.complete ? "" : ` (${r.months} of 12 months held, not a full year)`}<br/>${money}: ${two(r.v)} USD per kW`;
        } },
      xAxis: { type: "category", data: rows.map((r) => r.y), ...s.axis },
      yAxis: { type: "value", name: "USD/kW", nameLocation: "middle", nameGap: 40, ...s.axis },
      series: [{ name: money, type: "bar", barMaxWidth: 40, data: rows.map((r) => ({ value: Math.round(r.v * 100) / 100, itemStyle: { color: token("accent"), opacity: r.complete ? 1 : 0.4 } })) }],
    }, true);
  }, [rows, money]);
  return <div ref={box} role="img" aria-label={label} data-chart="years" style={{ height: 280 }} className="w-full" />;
}

export type MonthRow = { m: string; revenue: number; held: boolean; share: number };
/** Revenue per month for the reader's size, with one month of debt payments as a dashed line. */
export function MonthlyRevenue({ rows, dsMonth, label }: { rows: MonthRow[]; dsMonth: number; label: string }) {
  const box = useEChart((chart) => {
    const s = baseStyle();
    const accent = token("accent"), ink = token("ink"), rule = token("rule");
    chart.setOption({
      textStyle: s.textStyle,
      grid: { left: 70, right: 16, top: 16, bottom: 56 },
      tooltip: { ...s.tooltip, trigger: "axis", axisPointer: { type: "shadow" },
        formatter: (ps: { dataIndex: number }[]) => {
          const r = rows[ps[0].dataIndex];
          const lines = [`<strong>${r.m}</strong>`, `Revenue: ${short(Math.round(r.revenue))} USD`];
          if (!r.held) lines.push(`${Math.round(r.share * 100)} percent of the month held: shown, not counted`);
          else if (dsMonth > 0) lines.push(`${r.revenue < dsMonth ? "Below" : "Above"} a month of debt payments, ${short(Math.round(dsMonth))} USD`);
          return lines.join("<br/>");
        } },
      xAxis: { type: "category", data: rows.map((r) => r.m), ...s.axis },
      yAxis: { type: "value", name: "USD", nameLocation: "middle", nameGap: 54, ...s.axis, axisLabel: { ...s.axis.axisLabel, formatter: (v: number) => short(v) } },
      dataZoom: [{ type: "slider", height: 16, bottom: 6 }],
      series: [{
        name: "Revenue", type: "bar", barCategoryGap: "10%",
        data: rows.map((r) => ({ value: Math.round(r.revenue), itemStyle: { color: !r.held ? rule : r.revenue < dsMonth ? accent : ink } })),
        markLine: dsMonth > 0 ? { silent: true, symbol: "none", lineStyle: { color: accent, type: "dashed" }, label: { show: false }, data: [{ yAxis: dsMonth }] } : undefined,
      }],
    }, true);
  }, [rows, dsMonth]);
  return <div ref={box} role="img" aria-label={label} data-chart="months" style={{ height: 300 }} className="w-full" />;
}

/** Trailing-twelve-month debt coverage, with lines at 1.0 and 1.25 times. */
export function CoverageLine({ rows, label }: { rows: { m: string; dscr: number }[]; label: string }) {
  const box = useEChart((chart) => {
    const s = baseStyle();
    const accent = token("accent");
    chart.setOption({
      textStyle: s.textStyle,
      grid: { left: 56, right: 44, top: 16, bottom: 30 },
      tooltip: { ...s.tooltip, trigger: "axis",
        formatter: (ps: { dataIndex: number }[]) => {
          const r = rows[ps[0].dataIndex];
          return `<strong>The twelve months to ${r.m}</strong><br/>Coverage: ${two(r.dscr)} times`;
        } },
      xAxis: { type: "category", data: rows.map((r) => r.m), ...s.axis },
      yAxis: { type: "value", name: "times", nameLocation: "middle", nameGap: 40, ...s.axis },
      series: [{
        name: "Coverage", type: "line", showSymbol: false, lineStyle: { color: token("ink"), width: 2 }, itemStyle: { color: token("ink") },
        data: rows.map((r) => Math.round(r.dscr * 100) / 100),
        markLine: { silent: true, symbol: "none", lineStyle: { color: accent }, label: { color: accent, formatter: "{c}x" }, data: [{ yAxis: 1 }, { yAxis: 1.25, lineStyle: { color: accent, type: "dashed" } }] },
      }],
    }, true);
  }, [rows]);
  return <div ref={box} role="img" aria-label={label} data-chart="coverage" style={{ height: 240 }} className="w-full" />;
}
