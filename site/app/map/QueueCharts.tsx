"use client";
// Session 349: the Queues tab's three charts, through the shared SeriesChart (its Chart | Table toggle): positions
// entered against those that reached operation, the share withdrawn and the median wait, each by entry year. The tab
// hands the values, which are iso_queue_statistics' own rows (QueuesView.tsx); nothing is computed here.
import { SeriesChart } from "@/components/tool/SeriesChart";

const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export function QueueCharts({ label, years, entered, operating, rate, wait }: {
  label: string; years: string[]; entered: (number | null)[]; operating: (number | null)[]; rate: (number | null)[]; wait: (number | null)[];
}) {
  const cats = years.map((y) => ({ label: y }));
  return (
    <div data-queue-charts={label}>
      <SeriesChart id="queue-entered" title="Entered and reached operation" unit="positions" kind="line" scale="linear" categories={cats}
        series={[{ name: "Entered", color: "var(--color-ink)", values: entered }, { name: "Operating", color: "var(--color-accent)", values: operating }]}
        says={(i) => `${years[i]}: ${entered[i] ?? "not held"} entered, ${operating[i] ?? "not held"} operating`}
        note={`${label}: positions by the year they entered the queue, and how many of them reached operation.`} />
      {rate.some((v) => v !== null) ? (
        <SeriesChart id="queue-withdrawn" title="Withdrawn, share of entered" unit="share" kind="line" scale="linear" categories={cats} fmt={two}
          series={[{ name: "Withdrawn", color: "var(--color-accent)", values: rate }]}
          says={(i) => `${years[i]}: ${rate[i] === null ? "not held" : two(rate[i]!)} of the positions entered were withdrawn`} />
      ) : null}
      {wait.some((v) => v !== null) ? (
        <SeriesChart id="queue-wait" title="Median wait, entry to operation" unit="years" kind="line" scale="linear" categories={cats} fmt={two}
          series={[{ name: "Median wait", color: "var(--color-accent)", values: wait }]}
          says={(i) => `${years[i]}: ${wait[i] === null ? "no wait held" : `${two(wait[i]!)} years`}`} />
      ) : null}
    </div>
  );
}
