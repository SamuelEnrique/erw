"use client";
// Session 3062 (chain 166): the monitor's charts, of every record of data/policy/monitor.json (not the filtered set,
// so each sum has one value scripts/check_policy.py can trace): records by month and body; records by sector and
// band of significance; the MW and USD the records state as their own, summed by month where stated. Drawn by the
// site's CategoryChart (SVG, a hover card, a Chart | Table toggle); every count and sum is lib/policymonitor.ts's,
// which adds the file's fields and computes nothing else.
import { CategoryChart, type CatSeries } from "@/components/svgchart";
import { byBodyMonth, figureSums, sigBySector, sumKey, type MonitorRow } from "@/lib/policymonitor";

const COLORS = ["series-1", "series-2", "series-3", "series-4", "series-5", "series-6", "series-7", "series-8"];
const tip = "cursor-help border-b border-dotted border-muted";
const money = (v: number) => (v >= 1e9 ? `USD ${(v / 1e9).toLocaleString("en-US", { maximumFractionDigits: 2 })} billion` : `USD ${(v / 1e6).toLocaleString("en-US", { maximumFractionDigits: 2 })} million`);

export function MonitorCharts({ rows }: { rows: MonitorRow[] }) {
  const bm = byBodyMonth(rows);
  const ss = sigBySector(rows);
  const sums = figureSums(rows);
  return (
    <div className="mt-6 grid gap-6" data-monitor-charts="1">
      <div data-chart="policy-body-month">
        <CategoryChart id="policy-body-month" x={bm.months} unit="records" height={280}
          label="Records by the month of their newest document, by body (every record of the monitor's file)"
          series={bm.series.map((s, i): CatSeries => ({ name: s.name, color: COLORS[i % COLORS.length], values: s.values, kind: "bar", stack: "body", digits: 0 }))} />
      </div>
      <div data-chart="policy-sig-sector">
        <CategoryChart id="policy-sig-sector" x={ss.sectors.map((s) => s.replace(/_/g, " "))} unit="records" height={280}
          label="Records by the scorer's sector, by band of significance (the news rubric, a model's score)"
          series={ss.series.map((s, i): CatSeries => ({ name: s.name, color: COLORS[i], values: s.values, kind: "bar", stack: "sig", digits: 0 }))} />
      </div>
      <div data-chart="policy-figures">
        <h3 className="mb-1 text-sm">The figures stated, summed <span className={`text-xs text-muted ${tip}`} title="Each record's own figure, read from a title or a document's opening paragraph only, in MW or USD; a record that states none adds nothing. A sum is not an estimate of all actions: it is what the documents state.">by month, where stated</span></h3>
        <table className="text-xs">
          <caption className="sr-only">The MW and USD the records state as their own, summed by month, with how many records state one</caption>
          <thead><tr className="border-b border-rule text-left text-muted"><th className="pr-4">Month</th><th className="pr-4">Unit</th><th className="pr-4 text-right">Sum</th><th className="text-right">Records</th></tr></thead>
          <tbody>
            {sums.map((s) => (
              <tr key={`${s.unit}${s.month}`} className="border-b border-rule/60">
                <td className="pr-4 tabular-nums">{s.month}</td><td className="pr-4">{s.unit}</td>
                <td className="pr-4 text-right tabular-nums"><span className={tip} title={`The figures of ${s.records.join(", ")}`} data-check={sumKey(s)}>{s.unit === "USD" ? money(s.value) : `${s.value.toLocaleString("en-US")} MW`}</span></td>
                <td className="text-right tabular-nums">{s.records.length}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
