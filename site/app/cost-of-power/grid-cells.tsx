import type { ReactNode } from "react";
import { ToolTable } from "@/components/tool/ToolPage";
import { whole } from "@/lib/datacenter";
import { INDEX, type MatrixRow } from "@/lib/datacenterdata";
import { NYLOAD, type NyZone } from "./model";

// Session 213: the three cells "What a datacenter pays" drew in its grid questions until this session, kept on disk and
// drawn by nothing (CLAUDE.md rule 3; the battery page's Contract.tsx is the pattern): New York's load in line by zone,
// the Commission's transmission charge matrix row by row, and demand by region. What they showed is the page's
// download, tables.csv (tables.csv/route.ts), written from the same files.

function Missing({ why, words = "not held yet" }: { why: string; words?: string }) {
  return <span className="cursor-help border-b border-dotted border-muted italic text-muted" title={why} data-missing="1">{words}</span>;
}
const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
export const matrixTip = (r: MatrixRow) => `${r.document}, filed ${r.filed}, page ${r.page ?? "not printed"} of the attachment${r.scan_page ? ` (page ${r.scan_page} of the filed scan)` : ""}. Column "${r.header}". Read from the line: "${r.sentence}".${r.digits_spaced ? " The text of the file prints this figure with its digits spaced." : ""} ${r.docket_status}.`;
const matrixName = (r: MatrixRow) => `${r.year}${r.matrix ? `, matrix ${r.matrix}` : ""}`;

/** New York's load in line by zone: megawatts and requests as NYISO's sheet "Load Projects" lists them, the reader's
 * zone first; each zone's requests by status, and the source, on hover. Sums within NYISO's one list, by its statuses. */
export function NyLoadCell({ own }: { own: string }): ReactNode {
  const mine = NYLOAD.zones.find((z) => z.zone_name === own);
  const src = `${NYLOAD.source.name}, sheet "Load Projects" (${NYLOAD.source.url}), as NYISO last changed it on ${NYLOAD.source.workbook_last_modified}. ${NYLOAD.rule.in_line}`;
  const tip = (z: NyZone) => `${z.zone} ${z.zone_name}: ${z.by_status.map((b) => `${b.status}: ${b.requests} requests, ${b.mw.toLocaleString("en-US")} MW`).join("; ") || "no request in line"}. ${src}`;
  return (
    <span className="block" data-nyload="1">
      {mine ? <span className="mb-1 block"><span className="cursor-help border-b border-dotted border-muted" title={tip(mine)} data-nyload-own="1">{mine.mw.toLocaleString("en-US")} MW in {whole(mine.requests)} requests in {mine.zone_name}</span>; <span className="cursor-help border-b border-dotted border-muted" title={src} data-nyload-total="1">{NYLOAD.total.mw.toLocaleString("en-US")} MW in {whole(NYLOAD.total.requests)} requests in New York</span></span> : null}
      {NYLOAD.zones.map((z) => (
        <span key={z.zone} className={`mr-3 inline-block cursor-help whitespace-nowrap text-xs ${z.zone_name === own ? "font-semibold" : ""}`} data-nyload-zone={z.zone_name} title={tip(z)}>{z.zone_name} {z.mw.toLocaleString("en-US")} MW</span>
      ))}
    </span>
  );
}

/** The matrix, row by row: all of ERCOT and the four utilities as transmission providers, each figure as printed. */
export function MatrixTable({ rows }: { rows: MatrixRow[] }): ReactNode {
  const keys = [...new Set(rows.map((r) => `${r.year}|${r.matrix}|${r.scope}`))];
  const pick = (k: string, q: string[]) => rows.find((r) => `${r.year}|${r.matrix}|${r.scope}` === k && q.includes(r.quantity));
  const cell = (r: MatrixRow | undefined, digits: number) => r ? <a href={r.scan_url || r.url} title={matrixTip(r)} className="cursor-help no-underline hover:underline">{r.value.toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits })}</a> : <Missing why="The matrix prints no such figure in this row." words="not printed" />;
  return (
    <ToolTable caption="The Commission's transmission charge matrix" words minWidth={680} head={["", "Transmission cost of service, USD a year", "Rate, USD per kW a year", "Four-peak demand, kW", ""]}
      rows={keys.map((k) => { const [, , scope] = k.split("|"); const any = rows.find((r) => `${r.year}|${r.matrix}|${r.scope}` === k)!;
        return { key: k, cells: [`${scope}, ${matrixName(any)}`, cell(pick(k, ["total_transmission_cost_of_service", "transmission_cost_of_service"]), 0), cell(pick(k, ["postage_stamp_rate", "access_fee"]), 6),
          cell(pick(k, ["total_average_4cp", "average_4cp"]), 0), <span key="s" className="text-xs text-muted">{any.status === "approved" ? "approved" : "filed, not approved"}</span>] }; })} />
  );
}

/** Demand by region: each zone's average demand in the newest whole year against the first whole year held. */
export function ZoneCell({ zones, own }: { zones: NonNullable<(typeof INDEX.grids)[string]["zones"]>; own: string }): ReactNode {
  const rows = Object.entries(zones).map(([z, ys]) => {
    const wholeYears = Object.keys(ys).filter((y) => ys[y].hours_held >= 0.95 * ys[y].hours_due && ys[y].hours_due >= 8760).sort();
    const a = wholeYears[0], b = wholeYears.at(-1);
    return { z, a, b, from: a ? ys[a].mean_mw : null, to: b ? ys[b].mean_mw : null, peak: b ? ys[b].peak_mw : null };
  }).filter((r) => r.a && r.b && r.a !== r.b);
  if (!rows.length) return <Missing why="No region holds two whole years of hourly demand." />;
  return (
    <span className="block" data-zones="1">
      {rows.map((r) => (
        <span key={r.z} className={`mr-3 inline-block cursor-help whitespace-nowrap ${r.z === own ? "font-semibold" : ""}`} data-zone={r.z} title={`${r.z}: average demand ${whole(r.from!)} MW in ${r.a}, ${whole(r.to!)} MW in ${r.b}; highest hour of ${r.b}: ${whole(r.peak!)} MW`}>
          {r.z} {r.to! >= r.from! ? "+" : ""}{two((100 * (r.to! - r.from!)) / r.from!)}%
        </span>
      ))}
      <span className="block text-xs text-muted">average demand, {rows[0].a} to {rows[0].b}</span>
    </span>
  );
}
