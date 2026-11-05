// Energy Research Warehouse (ERW) site, session 405: the interconnection explorer's own parts
// (/explore/interconnection; the frame is components/explore/Explore.tsx, the shared helpers ./index.ts). It reads
// iso_queue_statistics (warehouse/derived/queue_statistics.py; docs/methods/energy_projects.md, "Queue statistics") as
// it stands and computes nothing: every figure it shows is one row of that table, or one count its header states, with
// the check key of that row or that count.
//
// This file holds no read and imports nothing, so a client component may import it and node can run it in the tests.

export const TABLE = "iso_queue_statistics";
export const METHOD = "/data/methods/energy_projects";

/** The six queues, in the order of the map's Queues tab (app/map/QueuesView.tsx): the grid's prefix and its name. */
export const QUEUES: [string, string][] = [["caiso", "CAISO"], ["ercot", "ERCOT"], ["nyiso", "NYISO"], ["miso", "MISO"], ["spp", "SPP"], ["isone", "ISO-NE"]];

/** What a queue does not hold, in the method note's words (the same lines as the map's Queues tab). */
export const NOT_HELD: Record<string, string> = {
  ercot: "ERCOT's report lists active and completed positions only, so no withdrawn count and no withdrawal rate are held.",
  miso: "MISO's queue holds no in-service date, so no wait is held.",
  isone: "ISO-NE's queue holds no in-service date, so no wait is held.",
  spp: "SPP's wait reads its Commercial Operation Date, which its queue fills for active and withdrawn positions too: for an operating position it may be the date requested, not achieved.",
};

/** The four statuses a position of an entry year is counted in (the method note: each ISO's own words as the queue
 *  connector maps them). The four make up the positions entered; a status a queue does not hold has no row. `short`
 *  names the series on the chart, where four long names overrun a phone's width. */
export const STATUSES = [
  { key: "operating", label: "Reached operation", short: "Operating", color: "var(--color-fuel-nuclear)" },
  { key: "withdrawn", label: "Withdrawn", short: "Withdrawn", color: "var(--color-muted)" },
  { key: "waiting", label: "Still waiting", short: "Waiting", color: "var(--color-accent)" },
  { key: "status_not_stated", label: "Status not stated", short: "No status", color: "var(--color-not-reported)" },
] as const;

export const MEASURES = [
  { key: "positions", label: "Positions", unit: "positions" },
  { key: "mw", label: "MW", unit: "MW" },
] as const;
export type Measure = (typeof MEASURES)[number]["key"];

export type Row = { entity: string; variable: string; ts_utc: string; value: number };

/** The entity of one queue's entry year, as the table writes it: "ercot:queue_2019". */
export const entityOf = (iso: string, year: number | string) => `${iso}:queue_${year}`;
/** The label timestamp of an entry year. */
export const yearTs = (year: number | string) => `${year}-01-01T00:00:00Z`;
/** The entry year an entity names, or null. */
export function yearOf(entity: string): number | null {
  const m = /:queue_(\d{4})$/.exec(entity);
  return m ? Number(m[1]) : null;
}

/** One row's value among a queue's rows, by entry year and variable. */
export function valueOf(rows: Row[], iso: string, year: number, variable: string): number | undefined {
  const e = entityOf(iso, year);
  const r = rows.find((x) => x.entity === e && x.variable === variable);
  return r === undefined ? undefined : Number(r.value);
}

/** The commit that fixed the build's read (session 367, 005b590d, 20 October 2026 19:45:54 UTC): a table whose header
 *  says it was built before this was built by the faulty read (the method note, "A fault in the first build"). */
export const FIXED_AT = "2026-10-20T19:45:54Z";

/** The time the table was built, from its header's "Retrieved: 20261020T093659Z (UTC) by ..." line, ISO form, or null. */
export function builtAt(header: string[]): string | null {
  const l = header.find((x) => x.startsWith("Retrieved:"));
  const m = l?.match(/(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z/);
  return m ? `${m[1]}-${m[2]}-${m[3]}T${m[4]}:${m[5]}:${m[6]}Z` : null;
}

/** Whether the table as it stands is the faulty build's: built before the fix, or of a time the header does not say. */
export function faultyBuild(header: string[]): boolean {
  const b = builtAt(header);
  return b === null || new Date(b).getTime() < new Date(FIXED_AT).getTime();
}

/** When one queue's input was retrieved, from the header's "Inputs read:" line ("ercot_interconnection_queue (1758
 *  rows; retrieved 20261019T203101Z; ..."), ISO form, or null. */
export function inputRetrieved(header: string[], iso: string): string | null {
  const l = header.find((x) => x.startsWith("Inputs read:"));
  const m = l?.match(new RegExp(`(?:^|[:;] )${iso}_interconnection_queue \\([^)]*?retrieved (\\d{4})(\\d{2})(\\d{2})T(\\d{2})(\\d{2})(\\d{2})Z`));
  return m ? `${m[1]}-${m[2]}-${m[3]}T${m[4]}:${m[5]}:${m[6]}Z` : null;
}

/** The header's line of the positions with no queue date (counted in no year). */
export const UNDATED = "Positions with no queue date";

/** A count the header states for one queue, on the line that begins with `prefix` ("...: ERCOT 456, CAISO 169"), or
 *  null. The queue is named as the header names it (ISO-NE, not isone). */
export function headerCount(header: string[], prefix: string, name: string): number | null {
  const l = header.find((x) => x.startsWith(prefix));
  if (!l) return null;
  const items = l.slice(l.indexOf(":") + 1).split(",").map((s) => s.trim());
  const it = items.find((s) => s.startsWith(`${name} `));
  const n = it ? Number(it.slice(name.length + 1).replace(/,/g, "")) : NaN;
  return Number.isFinite(n) ? n : null;
}

/** The check key of a count the header states: series_hdr|<table>|iso:<grid>|<line prefix>|<name>. It names the grid as
 *  an entity, so a held grid's count is held as its rows are (components/Num.tsx); scripts/check-values.mjs reads it. */
export const headerKey = (iso: string, prefix: string, name: string) => `series_hdr|${TABLE}|iso:${iso}|${prefix}|${name}`;

/** Whether an entry year is not over: the year the queue's input was retrieved in (its positions are still entering). */
export function partialYear(year: number, retrieved: string | null, now = new Date()): boolean {
  const y = retrieved ? new Date(retrieved).getUTCFullYear() : now.getUTCFullYear();
  return year >= y;
}
