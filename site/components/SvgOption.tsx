"use client";
// Energy Research Warehouse (ERW) site, session 318 (the owner's ruling of 13 October 2026): a chart option the
// analysis engine wrote (warehouse/analysis/style.py's weekly templates and charts of the week, lib/findingchart.ts's
// card charts, lib/chartforms.ts's forms, MultiChart's small multiples), drawn through the shared SVG set instead of
// the canvas: lib/svgoption.ts reads the option into props, and this draws a category chart, a time chart, a scatter
// or a column of panels. Every number is the option's own; an option the reader cannot read is said so in words, with
// no chart drawn wrong. `small`: the picker's examples (no toggle, no card, a short height).
import { useMemo } from "react";
import { TimeChart } from "@/components/TimeChart";
import { CategoryChart, ScatterChart } from "@/components/svgchart";
import { readOption, type CategoryRead } from "@/lib/svgoption";

function Category({ r, id, label, height, small }: { r: CategoryRead; id: string; label: string; height: number; small: boolean }) {
  return <CategoryChart id={id} x={r.x} series={r.series} unit={r.unit} unit2={r.unit2} label={label} height={height} refLines={r.refLines} shade={r.shade ?? undefined} marks={r.marks} zero={r.zero} small={small} />;
}

export function SvgOption({ option, label, height = 340, id = "option", small = false, ...rest }: { option: unknown; label: string; height?: number; id?: string; small?: boolean } & Record<string, unknown>) {
  const r = useMemo(() => readOption(option), [option]);
  const attrs = Object.fromEntries(Object.entries(rest).filter(([k]) => k.startsWith("data-")));
  if (r.kind === "unread") return <p className="text-xs text-muted" data-option-unread="1" {...attrs}>This chart could not be drawn: {r.why}. The analysis file holds its values.</p>;
  if (r.kind === "panels") {
    return (
      <div data-option-kind="panels" {...attrs}>
        {r.panels.map((p, i) => (
          <div key={i} className="mb-2" data-panel={i}>
            {r.titles[i] ? <p className="text-xs font-semibold text-ink">{r.titles[i]}</p> : null}
            <Category r={p} id={`${id}-${i}`} label={`${label}: ${r.titles[i] ?? `panel ${i + 1}`}`} height={Math.max(120, Math.round(height / r.panels.length))} small={small} />
          </div>
        ))}
      </div>
    );
  }
  if (r.kind === "time") return <div data-option-kind="time" {...attrs}><TimeChart series={r.series} unit={r.unit} unit2={r.unit2} ariaLabel={label} height={height} x={r.x} mini={small} /></div>;
  if (r.kind === "scatter") return <div data-option-kind="scatter" {...attrs}><ScatterChart id={id} points={r.points} xUnit={r.xUnit} yUnit={r.yUnit} label={label} height={height} fit={r.fit ?? undefined} labels={r.points.length <= 12} small={small} /></div>;
  return <div data-option-kind="category" {...attrs}><Category r={r} id={id} label={label} height={height} small={small} /></div>;
}
