"use client";
// Time-series line chart on uPlot (about 50 KB, canvas). Colors come from the design
// tokens (app/tokens.css) through CSS variables, so the chart follows the one token file.
import { useEffect, useRef } from "react";
import uPlot from "uplot";
import "uplot/dist/uPlot.min.css";

export type Line = { label: string; points: { t: number; v: number }[]; color: "accent" | "muted" | "ink"; step?: boolean };

function token(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(`--color-${name}`).trim() || "#2E2D29";
}

// x: how the cursor legend writes a time: to the minute (UTC), or as a month or year for period tables
export function LineChart({ lines, unit, height = 280, ariaLabel, x = "minute" }: { lines: Line[]; unit: string; height?: number; ariaLabel: string; x?: "minute" | "month" | "year" }) {
  const box = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = box.current;
    if (!el) return;
    // one shared time axis: the union of every line's timestamps (seconds), nulls where a line has no value
    const ts = Array.from(new Set(lines.flatMap((l) => l.points.map((p) => p.t)))).sort((a, b) => a - b);
    const index = new Map(ts.map((t, i) => [t, i]));
    const cols = lines.map((l) => {
      const c: (number | null)[] = new Array(ts.length).fill(null);
      for (const p of l.points) c[index.get(p.t)!] = p.v;
      return c;
    });
    const rule = token("rule"), muted = token("muted");
    const axis = { stroke: muted, grid: { stroke: rule, width: 1 }, ticks: { stroke: rule, width: 1 }, font: "11px system-ui, sans-serif" };
    const opts: uPlot.Options = {
      width: el.clientWidth,
      height,
      scales: { x: { time: true } },
      tzDate: (t) => uPlot.tzDate(new Date(t * 1000), "Etc/UTC"), // axis labels in UTC, as stored
      axes: [{ ...axis }, { ...axis, label: unit, labelFont: "11px system-ui, sans-serif", size: 56 }],
      series: [
        {
          label: x === "minute" ? "UTC" : x === "month" ? "Month" : "Year",
          value: (_u, v) => (v == null ? "" : new Date(v * 1000).toISOString().slice(0, x === "minute" ? 16 : x === "month" ? 7 : 4).replace("T", " ")),
        },
        ...lines.map((l) => ({
          label: l.label,
          stroke: token(l.color),
          width: l.color === "accent" ? 1.5 : 1.25,
          // a stepped (hourly) line holds its price until the next hour; any other line breaks at a gap
          spanGaps: !!l.step,
          paths: l.step ? uPlot.paths.stepped!({ align: 1 }) : undefined,
          value: (_u: uPlot, v: number | null) => (v == null ? "" : v.toFixed(2)),
        })),
      ],
      legend: { live: true },
      cursor: { points: { size: 5 } },
    };
    const plot = new uPlot(opts, [ts, ...cols] as uPlot.AlignedData, el);
    const ro = new ResizeObserver(() => plot.setSize({ width: el.clientWidth, height }));
    ro.observe(el);
    return () => {
      ro.disconnect();
      plot.destroy();
    };
  }, [lines, unit, height, x]);

  return <div ref={box} role="img" aria-label={ariaLabel} className="w-full text-ink" />;
}
