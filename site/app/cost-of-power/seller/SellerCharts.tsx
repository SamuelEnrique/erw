"use client";
// Session 145: the charts of "What a generator earns" (/cost-of-power/seller). Every value drawn arrives from the
// server (page.tsx; lib/capture.ts, lib/merchant.ts, lib/seller2.ts); each chart answers the mouse with the figures of
// the bar or point under it. Session 317 (the owner's ruling of 13 October 2026): drawn through the shared SVG set
// (components/svgchart.tsx, CategoryChart) with the rows they took on the canvas; a month of debt payments and the
// coverage lines at 1 and 1.25 are reference lines named on the chart; the range slider is gone, the table stands in.
import { CategoryChart, type CatSeries } from "@/components/svgchart";

const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const whole = (v: number) => Math.round(v).toLocaleString("en-US");
const sign = (v: number) => `${v < 0 ? "-" : "+"}${two(Math.abs(v))}`;
const short = (v: number) => (Math.abs(v) >= 1e9 ? `${two(v / 1e9)} billion` : Math.abs(v) >= 1e6 ? `${two(v / 1e6)} million` : whole(v));

export type Fig = { price: number; flat: number; premium: number; pct: number | null; hours: number } | null;
export type PremiumRow = { label: string; partial: boolean; months: number; solar: Fig; wind: Fig };

/** (a) the premium or discount to the flat average, by year and over the last twelve months, solar and wind. */
export function PremiumYears({ rows, hub, market, label }: { rows: PremiumRow[]; hub: string; market: string; label: string }) {
  const faint = rows.map((r) => r.partial);
  const line = (name: string, f: Fig) => (f
    ? `${name}: ${two(f.price)} USD/MWh received, ${sign(f.premium)}${f.pct === null ? "" : ` (${sign(f.pct)} percent)`} against a flat ${two(f.flat)}, ${whole(f.hours)} hours`
    : `${name}: not held`);
  const series: CatSeries[] = [
    { name: "Solar", color: "accent", values: rows.map((r) => (r.solar ? Math.round(r.solar.premium * 100) / 100 : null)), kind: "bar", faint, digits: 2 },
    { name: "Wind", color: "ink", values: rows.map((r) => (r.wind ? Math.round(r.wind.premium * 100) / 100 : null)), kind: "bar", faint, digits: 2 },
  ];
  return <div data-chart="premium"><CategoryChart id="premium" x={rows.map((r) => r.label)} series={series} unit="USD/MWh" label={label} height={300}
    notes={rows.map((r) => `${r.partial ? `${r.months} of 12 months counted; ` : ""}${hub}, ${market}. ${line("Solar", r.solar)}. ${line("Wind", r.wind)}. The grid's whole fleet by hour, not one site`)} /></div>;
}

export type YearRow = { y: string; complete: boolean; months: number; v: number };
/** Revenue (the peaker's margin) by calendar year, USD per kW of nameplate; a year short of twelve held months is hatched. */
export function RevenueYears({ rows, money, label }: { rows: YearRow[]; money: string; label: string }) {
  return <div data-chart="years"><CategoryChart id="years" x={rows.map((r) => r.y)} unit="USD/kW" label={label} height={280}
    series={[{ name: money, color: "accent", values: rows.map((r) => Math.round(r.v * 100) / 100), kind: "bar", faint: rows.map((r) => !r.complete), digits: 2 }]}
    notes={rows.map((r) => (r.complete ? null : `${r.months} of 12 months held, not a full year`))} /></div>;
}

export type MonthRow = { m: string; revenue: number; held: boolean; share: number };
/** Revenue per month for the reader's size, with one month of debt payments as a dashed line. */
export function MonthlyRevenue({ rows, dsMonth, label }: { rows: MonthRow[]; dsMonth: number; label: string }) {
  // a month not held whole is hatched; below a month of debt payments the bar is the accent, above it ink (as before)
  const below = rows.map((r) => (r.held && dsMonth > 0 && r.revenue < dsMonth ? Math.round(r.revenue) : null));
  const above = rows.map((r) => (r.held && !(dsMonth > 0 && r.revenue < dsMonth) ? Math.round(r.revenue) : null));
  const part = rows.map((r) => (r.held ? null : Math.round(r.revenue)));
  const series: CatSeries[] = [
    { name: dsMonth > 0 ? "Revenue above a month of debt payments" : "Revenue", color: "ink", values: above, kind: "bar", stack: "rev" },
    ...(dsMonth > 0 ? [{ name: "Revenue below a month of debt payments", color: "accent", values: below, kind: "bar" as const, stack: "rev" }] : []),
    ...(part.some((v) => v !== null) ? [{ name: "Part of the month held", color: "rule", values: part, kind: "bar" as const, stack: "rev" }] : []),
  ];
  return <div data-chart="months"><CategoryChart id="months" x={rows.map((r) => r.m)} series={series} unit="USD" label={label} height={300}
    refLines={dsMonth > 0 ? [{ value: dsMonth, name: `a month of debt payments, ${short(Math.round(dsMonth))} USD`, dashed: true }] : undefined}
    notes={rows.map((r) => (!r.held ? `${Math.round(r.share * 100)} percent of the month held: shown, not counted` : dsMonth > 0 ? `${r.revenue < dsMonth ? "Below" : "Above"} a month of debt payments, ${short(Math.round(dsMonth))} USD` : null))} /></div>;
}

/** Trailing-twelve-month debt coverage, with lines at 1.0 and 1.25 times. */
export function CoverageLine({ rows, label }: { rows: { m: string; dscr: number }[]; label: string }) {
  return <div data-chart="coverage"><CategoryChart id="coverage" x={rows.map((r) => r.m)} unit="times" label={label} height={240}
    series={[{ name: "Coverage", color: "ink", values: rows.map((r) => Math.round(r.dscr * 100) / 100), kind: "line", width: 2, digits: 2 }]}
    refLines={[{ value: 1, name: "1x" }, { value: 1.25, name: "1.25x", dashed: true }]}
    nameOf={(i) => `The twelve months to ${rows[i].m}`} /></div>;
}
