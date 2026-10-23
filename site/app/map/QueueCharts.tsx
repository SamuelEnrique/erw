"use client";
// Session 349: the Queues tab's three charts, through the shared SeriesChart (its Chart | Table toggle): positions
// entered against those that reached operation, the share withdrawn and the median wait, each by entry year. The tab
// hands the values, which are iso_queue_statistics' own rows (QueuesView.tsx); nothing is computed here.
import { SeriesChart } from "@/components/tool/SeriesChart";

const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

// Session 2300 (chain 087): each chart stands in a frame that carries data-source ("<table>|<queue table>|<rule>", the
// rule naming the variables drawn), and each chart's note names the table, the ISO's queue table and the variable, so
// a reader finds the source without the table below. The values are iso_queue_statistics' rows, one a year entered.
const TABLE = "iso_queue_statistics";
const sourceOf = (iso: string, variables: string) => `${TABLE}|${iso}_interconnection_queue|${variables}, one row a year entered`;
const from = (label: string, iso: string) => `Read from ${TABLE}, which the ERW derives from ${label}'s own queue (${iso}_interconnection_queue)`;

export function QueueCharts({ label, iso, years, entered, operating, rate, wait }: {
  label: string; iso: string; years: string[]; entered: (number | null)[]; operating: (number | null)[]; rate: (number | null)[]; wait: (number | null)[];
}) {
  const cats = years.map((y) => ({ label: y }));
  return (
    <div data-queue-charts={label}>
      <div data-source={sourceOf(iso, "positions_entered and positions_operating")}>
        <SeriesChart id="queue-entered" title="Entered and reached operation" unit="positions" kind="line" scale="linear" categories={cats}
          series={[{ name: "Entered", color: "var(--color-ink)", values: entered }, { name: "Operating", color: "var(--color-accent)", values: operating }]}
          says={(i) => `${years[i]}: ${entered[i] ?? "not held"} entered, ${operating[i] ?? "not held"} operating (${TABLE}, ${iso}:queue_${years[i]})`}
          note={`${label}: positions by the year they entered the queue, and how many of them reached operation. ${from(label, iso)}: positions_entered and positions_operating by entry year; the same figures are in the table below, each with its check key.`} />
      </div>
      {rate.some((v) => v !== null) ? (
        <div data-source={sourceOf(iso, "withdrawal_rate")}>
          <SeriesChart id="queue-withdrawn" title="Withdrawn, share of entered" unit="share" kind="line" scale="linear" categories={cats} fmt={two}
            series={[{ name: "Withdrawn", color: "var(--color-accent)", values: rate }]}
            says={(i) => `${years[i]}: ${rate[i] === null ? "not held" : two(rate[i]!)} of the positions entered were withdrawn (${TABLE}, ${iso}:queue_${years[i]}, withdrawal_rate)`}
            note={`${from(label, iso)}: withdrawal_rate by entry year, the positions withdrawn over the positions entered (a recent year's share is not final). The same figures are in the table below.`} />
        </div>
      ) : null}
      {wait.some((v) => v !== null) ? (
        <div data-source={sourceOf(iso, "wait_years_median")}>
          <SeriesChart id="queue-wait" title="Median wait, entry to operation" unit="years" kind="line" scale="linear" categories={cats} fmt={two}
            series={[{ name: "Median wait", color: "var(--color-accent)", values: wait }]}
            says={(i) => `${years[i]}: ${wait[i] === null ? "no wait held" : `${two(wait[i]!)} years`} (${TABLE}, ${iso}:queue_${years[i]}, wait_years_median)`}
            note={`${from(label, iso)}: wait_years_median by entry year, over the year's positions that reached operation (the column "Waits counted" below says how many). The same figures are in the table below.`} />
        </div>
      ) : null}
    </div>
  );
}
