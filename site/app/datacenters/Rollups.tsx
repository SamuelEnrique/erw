// Session 2243 (chain 156): the datacenter tracker's rollups by grid and by operator, from datacenter_facilities as the
// live set serves it (lib/dcrollups.ts, the function scripts/check-values.mjs recomputes each key with). A sum is of the
// MW stated by the rows the page's sums count (a named US state, not cancelled); the rows of a group that state no MW
// are counted beside the sum, never added as zero; a group with none stated has no sum.
import { Num } from "@/components/Num";
import { ToolSection } from "@/components/tool/ToolPage";
import type { EntityRow } from "@/lib/data";
import { rollupKey, rollups, type FacRow } from "@/lib/dcrollups";

const whole = (v: number) => Math.round(v).toLocaleString("en-US");
const cell = "px-3 py-1.5 align-top tabular-nums";

function Table({ rows, dim, label }: { rows: FacRow[]; dim: "grid" | "operator"; label: string }) {
  const rs = rollups(rows, dim).filter((r) => r.counted > 0);
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-left text-sm" data-dc-rollup={dim}>
        <caption className="sr-only">The facilities by {label.toLowerCase()}</caption>
        <thead>
          <tr className="bg-accent text-white">
            {[label, "Facilities", "MW stated", "Stating MW", "Stating none"].map((h) => <th key={h} scope="col" className="px-3 py-1.5 font-normal">{h}</th>)}
          </tr>
        </thead>
        <tbody>
          {rs.map((r) => (
            <tr key={r.value || "-"} className="border-b border-rule" data-dc-rollup-row={r.value || "-"}>
              <th scope="row" className="px-3 py-1.5 font-normal">{r.value || (dim === "grid" ? "no grid stated or read" : "operator not stated")}</th>
              <td className={cell}><Num check={rollupKey("facilities", dim, r.value)} raw={r.counted}>{whole(r.counted)}</Num></td>
              <td className={cell}>{r.mw === null ? <span className="text-muted">none stated</span> : <Num check={rollupKey("mw", dim, r.value)} raw={r.mw}>{whole(r.mw)}</Num>}</td>
              <td className={cell}><Num check={rollupKey("with_mw", dim, r.value)} raw={r.withMw}>{whole(r.withMw)}</Num></td>
              <td className={cell}><Num check={rollupKey("without", dim, r.value)} raw={r.without}>{whole(r.without)}</Num></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Rollups({ rows }: { rows: EntityRow[] }) {
  return (
    <ToolSection title="By grid and by operator" id="rollups"
      note={<>The facilities in a named US state and not cancelled, as the page&apos;s other sums count them. A sum is of the MW the sources state, of any basis (IT load, total, a tenant&apos;s share, a phase); the facilities that state none are counted beside it. The grid is the one a story names, else the facility&apos;s queue&apos;s ISO, else the grid that serves most of its state.</>}>
      <div className="grid gap-6 lg:grid-cols-2">
        <Table rows={rows as unknown as FacRow[]} dim="grid" label="Grid" />
        <Table rows={rows as unknown as FacRow[]} dim="operator" label="Operator" />
      </div>
    </ToolSection>
  );
}
