"use client";
// Session 3062 (chain 166): the monitor's charts, of every record of data/policy/monitor.json (not the filtered set,
// so each sum has one value scripts/check_policy.py can trace): records by month and body; records by sector and
// band of significance; the MW and USD the records state as their own, summed by month where stated. Drawn by the
// site's CategoryChart (SVG, a hover card, a Chart | Table toggle); every count and sum is lib/policymonitor.ts's,
// which adds the file's fields and computes nothing else.
import { CategoryChart, type CatSeries } from "@/components/svgchart";
import { byBodyMonth, figureKey, figureMonths, figureText, monthLabels, sectorWords, sigBySector, type MonitorRow } from "@/lib/policymonitor";
// Session 1876 (policy faults rows 3, 26, 28): the sectors as words; the last month labelled with the day the file runs
// to when it is a part month; the figures by month as each unit's largest, with its record, document and key (no sum:
// a sum added a terminal's cost estimate to a penalty, and MW of relicensed hydro to new plants).

const COLORS = ["series-1", "series-2", "series-3", "series-4", "series-5", "series-6", "series-7", "series-8"];
const tip = "cursor-help border-b border-dotted border-muted";

export function MonitorCharts({ rows, last = "" }: { rows: MonitorRow[]; last?: string }) {
  const bm = byBodyMonth(rows);
  const ss = sigBySector(rows);
  const figs = figureMonths(rows);
  return (
    <div className="mt-6 grid gap-6" data-monitor-charts="1">
      <div data-chart="policy-body-month">
        <CategoryChart id="policy-body-month" x={monthLabels(bm.months, last)} unit="records" height={280}
          label="Records by the month of their newest document, by body (every record of the monitor's file)"
          series={bm.series.map((s, i): CatSeries => ({ name: s.name, color: COLORS[i % COLORS.length], values: s.values, kind: "bar", stack: "body", digits: 0 }))} />
      </div>
      <div data-chart="policy-sig-sector">
        <CategoryChart id="policy-sig-sector" x={ss.sectors.map(sectorWords)} unit="records" height={280}
          label="Records by the scorer's sector, by band of significance (the news rubric, a model's score)"
          series={ss.series.map((s, i): CatSeries => ({ name: s.name, color: COLORS[i], values: s.values, kind: "bar", stack: "sig", digits: 0 }))} />
      </div>
      <div data-chart="policy-figures">
        <h3 className="mb-1 text-sm">The figures stated, by month: <span className={`text-xs text-muted ${tip}`} title="Each record's own figure, read from a title or a document's opening paragraph only, in its unit, by the month of the record's newest document. Figures are not added: one month's USD holds a terminal's cost estimate and a penalty.">the largest of each unit</span></h3>
        <div className="overflow-x-auto">
        <table className="text-xs">
          <caption className="sr-only">For each month and unit, how many records state a figure in it, and the largest with its record</caption>
          <thead><tr className="border-b border-rule text-left text-muted"><th className="pr-4">Month</th><th className="pr-4">Unit</th><th className="pr-4 text-right">Records</th><th className="pr-4 text-right">Largest</th><th>Its record</th></tr></thead>
          <tbody>
            {figs.map((m) => (
              <tr key={`${m.month}|${m.unit}`} className="border-b border-rule/60 align-top" data-monitor-figmonth={`${m.month}|${m.unit}`}>
                <td className="whitespace-nowrap pr-4 tabular-nums">{m.month}</td><td className="pr-4">{m.unit}</td>
                <td className="pr-4 text-right tabular-nums">{m.n}</td>
                <td className="whitespace-nowrap pr-4 text-right tabular-nums"><span className={tip} title={`"${m.top.figure!.words}" (${m.top.figure!.event_id})`} data-check={figureKey(m.top)}>{figureText(m.top.figure!)}</span></td>
                <td><a href={m.top.sources?.[0]} title={m.top.id}>{m.top.body}: {m.top.title.length > 90 ? m.top.title.slice(0, 87) + "..." : m.top.title}</a></td>
              </tr>
            ))}
          </tbody>
        </table>
        </div>
      </div>
    </div>
  );
}
