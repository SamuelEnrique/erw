"use client";
// Session 138: the chart of "What a datacenter pays" (/cost-of-power). Every value drawn arrives from the server
// (page.tsx, lib/datacenter.ts); the chart answers the mouse: each bar shows its year, its figures and the months held.
// Session 236: the page is on the brand (components/Brand.tsx). Session 317 (the owner's ruling of 13 October 2026):
// drawn through the shared SVG set (components/svgchart.tsx, CategoryChart) with the rows it took on the canvas: the
// flat load and this load as bars (a year short of twelve months hatched), the perfectly foreseen cost as a mark.
import { CategoryChart, type CatSeries } from "@/components/svgchart";

export type YearBar = { y: string; flat: number | null; per: number | null; complete: boolean; months: number; down: number; foreseen?: number | null };
const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const r2 = (v: number | null | undefined) => (v === null || v === undefined ? null : Math.round(v * 100) / 100);

export function YearCost({ rows, flex, off, label }: { rows: YearBar[]; flex: boolean; off: boolean; label: string }) {
  const faint = rows.map((r) => !r.complete);
  const series: CatSeries[] = [{ name: "Flat load", color: flex ? "muted" : "accent", values: rows.map((r) => r2(r.flat)), kind: "bar", faint, digits: 2 }];
  if (flex) {
    series.push({ name: "This load", color: "accent", values: rows.map((r) => r2(r.per)), kind: "bar", faint, digits: 2 });
    // session 140: the same load with its hours chosen knowing the year's prices, a mark beside the bars
    series.push({ name: "If perfectly foreseen", color: "ink", values: rows.map((r) => r2(r.foreseen)), kind: "line", mark: true, digits: 2 });
  }
  const notes = rows.map((r) => {
    const bits: string[] = [];
    if (!r.complete) bits.push(`${r.months} of 12 months held`);
    if (flex && r.per !== null && r.flat !== null) bits.push(`saved ${two(r.flat - r.per)} USD/MWh${off && r.down ? `, off in ${r.down.toLocaleString("en-US")} hours` : ""}`);
    if (flex && r.foreseen != null && r.flat !== null) bits.push(`foreseen: saved ${two(r.flat - r.foreseen)}`);
    return bits.length ? bits.join("; ") : null;
  });
  return <div data-year-cost="1"><CategoryChart id="year-cost" x={rows.map((r) => r.y)} series={series} unit="USD/MWh" label={label} height={300} notes={notes} /></div>;
}
