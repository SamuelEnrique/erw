// Energy Research Warehouse (ERW) site, session 207: the license status of the tables flagged public whose publisher's
// own page asks for permission or a license (docs/licenses.md). The owner's ruling of 12 October 2026: from the day in
// the file (2026-10-20) such a table shows "license needed", as PJM's prices do, unless a permission is recorded.
// Nothing changes before that day. The file is written by `python scripts/licenses.py status` with
// warehouse/metadata/license_status.csv, the record the builders read.
import status from "@/data/license_status.json";

type Row = { status: string; from: string; publishers: string[] };
const TABLES = status.tables as Record<string, Row>;

export const LICENSE_FROM: string = status.from;
export const LICENSE_NEEDED = "license needed";

/** The UTC day, YYYY-MM-DD. */
export function utcDay(now: Date = new Date()): string {
  return now.toISOString().slice(0, 10);
}

/** True when the table's status is "license needed" and the day is on or after its `from` day. */
export function licenseNeeded(table: string, now: Date = new Date()): boolean {
  const r = TABLES[table];
  return !!r && r.status === LICENSE_NEEDED && utcDay(now) >= r.from;
}

/** The publishers whose sentence decides the table, for the words beside the status. */
export function licensePublishers(table: string): string[] {
  return TABLES[table]?.publishers ?? [];
}

/** The tables that are "license needed" on the day. */
export function licenseNeededTables(now: Date = new Date()): string[] {
  return Object.keys(TABLES).filter((t) => licenseNeeded(t, now)).sort();
}
