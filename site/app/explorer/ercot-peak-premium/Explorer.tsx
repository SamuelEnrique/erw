"use client";
// The ERCOT peak-premium explorer: year and hub selectors over the derived tables
// ercot_peak_premium_annual and ercot_peak_premium_monthly (docs/methods/ercot_peak_premium.md).
import { useMemo, useState } from "react";
import { LineChart, type Line } from "@/components/LineChart";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";

/** One row of a derived table: entity, variable, period (YYYY-MM), value. */
export type Row = { e: string; v: string; t: string; x: number };

const BLOCKS = [
  { key: "overnight", label: "Overnight", hours: "21:00 to 12:00" },
  { key: "midday", label: "Midday", hours: "12:00 to 16:00" },
  { key: "peak", label: "Peak", hours: "16:00 to 21:00" },
  { key: "all", label: "All intervals", hours: "24 hours" },
];
const STATS = ["min", "q1", "median", "q3", "max"] as const;
const HEADLINE = [
  { v: "all_median", label: "Median, all intervals", unit: "USD/MWh" },
  { v: "all_p999", label: "99.9th percentile", unit: "USD/MWh" },
  { v: "worst_interval_multiple", label: "Worst-interval multiple (P99.9 / median)", unit: "ratio" },
  { v: "peak_iqr", label: "Peak-block IQR", unit: "USD/MWh" },
  { v: "all_iqr", label: "All-interval IQR", unit: "USD/MWh" },
  { v: "peak_minus_midday_median", label: "Peak minus midday median", unit: "USD/MWh" },
  { v: "midday_min", label: "Midday minimum", unit: "USD/MWh" },
  { v: "n_scarcity", label: "Intervals at or above 1,000 USD/MWh", unit: "count" },
  { v: "n_negative", label: "Intervals at or below 0", unit: "count" },
  { v: "n_intervals", label: "Intervals in the period", unit: "count" },
];

function fmt(x: number, unit: string): string {
  if (unit === "count") return Math.round(x).toLocaleString("en-US");
  return x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function fullYear(y: number): number {
  return (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0 ? 35_136 : 35_040;
}

/** One block's five-number summary as a horizontal box on a shared, clipped scale. */
function Box({ s, lo, hi }: { s: Record<string, number>; lo: number; hi: number }) {
  const W = 520, H = 30, pad = 6;
  const x = (v: number) => pad + ((Math.min(Math.max(v, lo), hi) - lo) / (hi - lo)) * (W - 2 * pad);
  const clipL = s.min < lo, clipR = s.max > hi;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="block h-8 w-full" preserveAspectRatio="none" aria-hidden>
      <line x1={x(s.min)} x2={x(s.q1)} y1={H / 2} y2={H / 2} stroke="var(--color-muted)" />
      <line x1={x(s.q3)} x2={x(s.max)} y1={H / 2} y2={H / 2} stroke="var(--color-muted)" />
      {!clipL ? <line x1={x(s.min)} x2={x(s.min)} y1={9} y2={H - 9} stroke="var(--color-muted)" /> : <path d={`M${pad} ${H / 2} l6 -5 v10 z`} fill="var(--color-muted)" />}
      {!clipR ? <line x1={x(s.max)} x2={x(s.max)} y1={9} y2={H - 9} stroke="var(--color-muted)" /> : <path d={`M${W - pad} ${H / 2} l-6 -5 v10 z`} fill="var(--color-muted)" />}
      <rect x={x(s.q1)} y={5} width={Math.max(1, x(s.q3) - x(s.q1))} height={H - 10} fill="var(--color-panel)" stroke="var(--color-ink)" />
      <line x1={x(s.median)} x2={x(s.median)} y1={5} y2={H - 5} stroke="var(--color-accent)" strokeWidth={2.5} />
    </svg>
  );
}

export function Explorer({
  annual,
  monthly,
  monthlyError,
  citeAnnual,
  citeMonthly,
}: {
  annual: Row[];
  monthly: Row[];
  monthlyError: string | null;
  citeAnnual: React.ReactNode;
  citeMonthly: React.ReactNode;
}) {
  const hubs = useMemo(() => Array.from(new Set(annual.map((r) => r.e))).sort(), [annual]);
  const years = useMemo(() => Array.from(new Set(annual.map((r) => Number(r.t.slice(0, 4))))).sort((a, b) => b - a), [annual]);
  const get = (hub: string, v: string, year: number) => annual.find((r) => r.e === hub && r.v === v && r.t === `${year}-01`)?.x;
  // default: HB_HUBAVG (the thesis hub) and the newest complete year
  const defHub = hubs.includes("ercot:HB_HUBAVG") ? "ercot:HB_HUBAVG" : hubs[0];
  const defYear = years.find((y) => get(defHub, "n_intervals", y) === fullYear(y)) ?? years[0];
  const [hub, setHub] = useState(defHub);
  const [year, setYear] = useState(defYear);

  const n = get(hub, "n_intervals", year);
  const partial = n !== undefined && n !== fullYear(year);
  const boxes = BLOCKS.map((b) => {
    const s: Record<string, number> = {};
    for (const k of STATS) {
      const val = get(hub, `${b.key}_${k}`, year);
      if (val !== undefined) s[k] = val;
    }
    return { b, s, complete: STATS.every((k) => k in s) };
  });
  const have = boxes.filter((x) => x.complete);
  // scale: the quartiles of every block, widened by one IQR each side; whiskers beyond are clipped and labeled
  const q1s = have.map((x) => x.s.q1), q3s = have.map((x) => x.s.q3);
  const iqr = Math.max(...q3s) - Math.min(...q1s);
  const scaleLo = Math.max(Math.min(...have.map((x) => x.s.min)), Math.min(...q1s) - iqr);
  const scaleHi = Math.min(Math.max(...have.map((x) => x.s.max)), Math.max(...q3s) + iqr);

  const byYear = (v: string) =>
    annual
      .filter((r) => r.e === hub && r.v === v)
      .map((r) => ({ t: Date.UTC(Number(r.t.slice(0, 4)), 0, 1) / 1000, v: r.x }))
      .sort((a, b) => a.t - b.t);
  const yearLines: Line[] = [
    { label: "Peak-block IQR", points: byYear("peak_iqr"), color: "accent" },
    { label: "Median, all intervals", points: byYear("all_median"), color: "muted" },
  ];
  const byMonth = (v: string) =>
    monthly
      .filter((r) => r.e === hub && r.v === v)
      .map((r) => ({ t: Date.UTC(Number(r.t.slice(0, 4)), Number(r.t.slice(5, 7)) - 1, 1) / 1000, v: r.x }))
      .sort((a, b) => a.t - b.t);
  const monthLines: Line[] = [
    { label: "Peak median", points: byMonth("peak_median"), color: "accent" },
    { label: "Midday median", points: byMonth("midday_median"), color: "muted" },
    { label: "Overnight median", points: byMonth("overnight_median"), color: "ink" },
  ];
  const hubName = hub.split(":")[1];

  return (
    <>
      <div className="mb-6 flex flex-wrap gap-4 text-sm">
        <label className="flex items-center gap-2">
          Hub
          <select value={hub} onChange={(e) => setHub(e.target.value)} className="border border-rule bg-panel px-2 py-1 font-mono">
            {hubs.map((h) => (
              <option key={h} value={h}>
                {h.split(":")[1]}
              </option>
            ))}
          </select>
        </label>
        <label className="flex items-center gap-2">
          Year
          <select value={year} onChange={(e) => setYear(Number(e.target.value))} className="border border-rule bg-panel px-2 py-1">
            {years.map((y) => (
              <option key={y} value={y}>
                {y}
                {get(hub, "n_intervals", y) !== fullYear(y) ? " (partial)" : ""}
              </option>
            ))}
          </select>
        </label>
      </div>

      <section className="mb-10">
        <h2 className="mb-1 border-b border-rule pb-1 text-xl">
          {hubName}, {year}
          {partial ? <span className="ml-2 text-sm text-muted">partial year</span> : null}
        </h2>
        {partial && n !== undefined ? (
          <p className="mb-2 text-xs text-muted">
            {fmt(n, "count")} of {fmt(fullYear(year), "count")} intervals: the year is not over, and the figures cover only the intervals so far.
          </p>
        ) : null}
        <div className="grid grid-cols-2 gap-px border border-rule bg-rule md:grid-cols-5">
          {HEADLINE.map((h) => {
            const val = get(hub, h.v, year);
            return (
              <div key={h.v} className="bg-panel p-2">
                <div className="text-xs text-muted">{h.label}</div>
                {val !== undefined ? (
                  <div className="text-lg tabular-nums">
                    <Num check={`series|ercot_peak_premium_annual|${hub}|${h.v}|${year}-01-01T00:00:00Z`} raw={val}>
                      {fmt(val, h.unit)}
                    </Num>{" "}
                    {h.unit !== "count" ? <span className="text-xs text-muted">{h.unit}</span> : null}
                  </div>
                ) : (
                  <div className="text-xs text-muted">no data: no {h.v} row for this hub and year</div>
                )}
              </div>
            );
          })}
        </div>

        <h3 className="mt-6 mb-2 text-lg">Distribution by time of day, USD/MWh</h3>
        {have.length === 0 ? (
          <NoData reason="no block summaries for this hub and year" />
        ) : (
          <div className="border border-rule bg-panel p-3">
            {boxes.map(({ b, s, complete }) => (
              <div key={b.key} className="grid grid-cols-1 items-center gap-x-3 border-b border-rule/60 py-2 last:border-0 md:grid-cols-[9rem_1fr_22rem]">
                <div className="text-sm">
                  {b.label} <span className="text-xs text-muted">{b.hours}</span>
                </div>
                {complete ? <Box s={s} lo={scaleLo} hi={scaleHi} /> : <NoData reason={`missing ${b.key} statistics`} />}
                <div className="grid grid-cols-5 gap-1 text-right text-xs tabular-nums">
                  {STATS.map((k) => (
                    <div key={k}>
                      <div className="text-muted">{k === "q1" ? "Q1" : k === "q3" ? "Q3" : k}</div>
                      {k in s ? (
                        <Num check={`series|ercot_peak_premium_annual|${hub}|${b.key}_${k}|${year}-01-01T00:00:00Z`} raw={s[k]}>
                          {fmt(s[k], "USD/MWh")}
                        </Num>
                      ) : null}
                    </div>
                  ))}
                </div>
              </div>
            ))}
            <p className="mt-2 text-xs text-muted">
              Box: Q1 to Q3, accent line the median. Whiskers run to the min and max; a triangle marks a whisker cut at the edge of the scale (
              {fmt(scaleLo, "USD/MWh")} to {fmt(scaleHi, "USD/MWh")}), and the exact values are in the columns on the right.
            </p>
          </div>
        )}
        {citeAnnual}
      </section>

      <section className="mb-10">
        <h2 className="mb-2 border-b border-rule pb-1 text-xl">{hubName} by year</h2>
        <LineChart lines={yearLines} unit="USD/MWh" height={260} ariaLabel={`${hubName} peak-block IQR and median by year`} x="year" />
        <p className="mt-1 text-xs text-muted">Each point is one ERCOT operating year; the last year is partial.</p>
        {citeAnnual}
      </section>

      <section className="mb-10">
        <h2 className="mb-2 border-b border-rule pb-1 text-xl">{hubName} by month: median price by block</h2>
        {monthlyError ? (
          <NoData what="ercot_peak_premium_monthly" reason={monthlyError} />
        ) : (
          <LineChart lines={monthLines} unit="USD/MWh" height={280} ariaLabel={`${hubName} monthly median price by block`} x="month" />
        )}
        {citeMonthly}
      </section>
    </>
  );
}
