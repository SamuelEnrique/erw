// Session 2245 (chain 156): the datacenter tracker's timeline, from first reported to energized, for the facilities whose
// sources state both (lib/dcrollups.ts timeline). The wait is the difference of the two years; the median of a grid or of
// a year of first report needs three facilities with both. Every figure carries its key, dctime|<stat>|<dim>|<value>,
// which scripts/check-values.mjs recomputes with the same function.
import { Num } from "@/components/Num";
import { ToolSection, ToolTable } from "@/components/tool/ToolPage";
import type { EntityRow } from "@/lib/data";
import { timeKey, timeline, timelineCells, type FacRow } from "@/lib/dcrollups";

export function Timeline({ rows }: { rows: EntityRow[] }) {
  const t = timeline(rows as unknown as FacRow[]);
  return (
    <ToolSection title="From first reported to energized" id="timeline"
      note={<>Only the facilities whose sources state both: the date of the first story and the year the facility is to be energized or come online. The wait is the difference of the two years, in whole years (the energized date is a year); a facility with one date is not on it, and no wait is estimated from one. A median needs three facilities with both.</>}>
      {t.length === 0 ? (
        <p className="text-sm text-muted" role="status" data-timeline-none="1">No facility held states both a first report and the year it is to be energized.</p>
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          {(["grid", "year"] as const).map((dim) => (
            <ToolTable key={dim} caption={`The wait by ${dim === "grid" ? "grid" : "year of first report"}`} minWidth={360}
              head={[dim === "grid" ? "Grid" : "Year first reported", "Facilities with both dates", "Median wait, years"]}
              rows={timelineCells(t, dim).map((c) => ({
                key: c.value || "-",
                cells: [
                  c.value || (dim === "grid" ? "no grid stated or read" : "not stated"),
                  <Num key="n" check={timeKey("count", dim, c.value)} raw={c.count}>{String(c.count)}</Num>,
                  c.median === null ? <span key="m" className="text-muted">fewer than three</span> : <Num key="m" check={timeKey("median", dim, c.value)} raw={c.median}>{String(c.median)}</Num>,
                ],
              }))} />
          ))}
        </div>
      )}
    </ToolSection>
  );
}
