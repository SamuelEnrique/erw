"use client";
// Session 347: the third question's chart on /impact: the reader's project's construction job-years in each state JEDI
// gives a figure for, on site, in the supply chain and induced, stacked, the states from the most to the least. The
// shared SeriesChart (components/tool/SeriesChart.tsx) draws it, with its Chart | Table toggle; the page hands it the
// values (JEDI's per-MW lines times the reader's project, lib/impact.ts). The hover names the state and its three parts.
import { SeriesChart } from "@/components/tool/SeriesChart";
import { Tip } from "@/components/tool/ToolPage";

const one = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

export function StateChart({ id, unit, categories, keys, onsite, supply, induced, highlight }: {
  id: string; unit: string; categories: string[]; keys: string[]; onsite: number[]; supply: number[]; induced: number[]; highlight: string;
}) {
  return (
    <SeriesChart
      id={id}
      title="The same project in other states"
      unit={unit}
      kind="stacked"
      scale="linear"
      fmt={(v) => Math.round(v).toLocaleString("en-US")}
      categories={keys.map((k, i) => ({ label: categories[i], sub: k === highlight ? "yours" : undefined }))}
      series={[
        { name: "On site", color: "var(--color-accent)", values: onsite },
        { name: "Supply chain", color: "var(--color-ink)", values: supply },
        { name: "Induced", color: "var(--color-muted)", values: induced },
      ]}
      says={(i) => `${categories[i]}: ${one(onsite[i] + supply[i] + induced[i])} ${unit} (on site ${one(onsite[i])}, supply chain ${one(supply[i])}, induced ${one(induced[i])})`}
      // fault 19 (session 4253): the chart's words as a tip, not a line under it (explanations only as hover tips, the owner's
      // tool rules)
      tip={<Tip id={`${id}-tip`} label="the same project in other states">The ten states with the most construction job-years, the scenario&apos;s own and the five with the fewest: JEDI&apos;s per-MW construction jobs in each state, scaled by the scenario&apos;s spending and local content. The chart&apos;s table holds them.</Tip>}
    />
  );
}
