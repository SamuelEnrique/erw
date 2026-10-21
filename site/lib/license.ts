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

// Session 215 (the owner's ruling of 12 October 2026 on session 207's question 4): every page that reads one of these
// tables shows the catalogue's words, "license needed", in the place a number would have been, from the day in the
// file. The hold reaches a page through lib/supabase.ts (a read of a held table throws LicenseNeeded, which attempt and
// required turn into a reason that components/NoData.tsx draws as the words) and through components/Num.tsx (a number
// whose check key names a held table is drawn as the words). The words and the title are the catalogue's (app/data/page.tsx).

/** The words beside the status on the catalogue, in the hover: the publishers whose sentence decides the table. */
export const LICENSE_TITLE_SUFFIX = "the publisher's own page asks for permission; none is recorded yet";
export function licenseTitle(table: string): string {
  const who = licensePublishers(table);
  return `${who.length ? who.join("; ") : table}: ${LICENSE_TITLE_SUFFIX}`;
}

/** A reason attempt() or required() gives for a held read. NoData reads the prefix and draws the words. */
export const LICENSE_REASON = `${LICENSE_NEEDED}: `;
export const licenseReason = (table: string) => `${LICENSE_REASON}${licenseTitle(table)}`;
export const isLicenseReason = (reason: string) => reason.startsWith(LICENSE_REASON);

/** The grid operators among the publishers, by the prefix their entities carry ("isone:.H.INTERNAL_HUB", "iso:isone").
 *  A consolidated table (iso_dam_hub_prices holds CAISO, ERCOT, MISO and SPP) is flagged whole in the status file for
 *  the grids that ask for permission; the price board (session 207) holds those grids' rows and keeps the others', in
 *  PJM's manner, and the pages do the same: a table every deciding publisher of which is a grid operator is held row by
 *  row, for the rows of those grids; a table decided by anyone else (a news outlet, an operator's site) is held whole. */
const GRID_PREFIX: Record<string, string> = { "ISO-NE": "isone", MISO: "miso", NYISO: "nyiso", PJM: "pjm", SPP: "spp", CAISO: "caiso", ERCOT: "ercot" };
const GRID_NAME: Record<string, string> = Object.fromEntries(Object.entries(GRID_PREFIX).map(([k, v]) => [v, k]));

/** True when every publisher deciding the table is a grid operator: the hold is by grid, not whole. */
export function licenseByGrid(table: string): boolean {
  const who = licensePublishers(table);
  return who.length > 0 && who.every((p) => p in GRID_PREFIX);
}

/** The grid prefixes ("isone", "miso", "nyiso") whose prices are held on the day: a grid that decides any held table. */
export function licenseHeldGrids(now: Date = new Date()): string[] {
  const out = new Set<string>();
  for (const t of licenseNeededTables(now)) for (const p of licensePublishers(t)) if (p in GRID_PREFIX) out.add(GRID_PREFIX[p]);
  return [...out].sort();
}

/** The grid an entity belongs to, by its prefix: "isone:.H.INTERNAL_HUB" and "iso:isone" are ISO-NE's; "" when none. */
export function gridOfEntity(entity: string | undefined | null): string {
  if (!entity) return "";
  const m = /^([a-z0-9_-]+):(.*)$/i.exec(entity);
  if (!m) return "";
  const head = m[1].toLowerCase();
  if (head in GRID_NAME) return head;
  if (head === "iso" && m[2].toLowerCase() in GRID_NAME) return m[2].toLowerCase();
  return "";
}

/** Session 382: the grid a check key names as an input, in the entity form ("iso:ercot"), or undefined. The generator
 *  page's model keys (mr|iso=ercot&asset=solar&...|<stat>, ms|iso=ercot&...&hub=HB_WEST&market=rt|<span>|<stat>) carry
 *  their grid as `iso=` (session 264: "every check key names its grid"), not as an entity, so until this session the
 *  hold of 21 October read them as naming no grid and held ERCOT's, CAISO's and SPP's figures with ISO-NE's and NYISO's. */
export function gridEntityOfKey(parts: string[]): string | undefined {
  for (const x of parts) {
    const m = /(?:^|&)(?:iso|grid)=([a-z0-9_-]+)(?=&|$)/i.exec(x);
    if (m && m[1].toLowerCase() in GRID_NAME) return `iso:${m[1].toLowerCase()}`;
  }
  return undefined;
}

/** The hold on one row of a table: a held table decided by grids holds the rows of the grids that decide it (and a row
 *  of no grid, such as a national total, is kept); any other held table holds every row. `entity` undefined asks about
 *  the table whole. */
export function licenseHeldRow(table: string, entity?: string | null, now: Date = new Date()): boolean {
  if (!licenseNeeded(table, now)) return false;
  if (!licenseByGrid(table)) return true;
  if (entity === undefined || entity === null) return true;
  const g = gridOfEntity(entity);
  return !!g && licensePublishers(table).some((p) => GRID_PREFIX[p] === g);
}

/** Whether a grid's own rows are held on the day, wherever they are read (latest_prices holds every grid's newest
 *  interval and is not a coverage table): true for a grid that decides any held table. */
export function licenseHeldGrid(grid: string, now: Date = new Date()): boolean {
  const g = (GRID_PREFIX[grid] ?? grid).toLowerCase();
  return licenseHeldGrids(now).includes(g);
}

/** The title for a held grid's row where no one table is named (the latest prices). */
export function licenseGridTitle(grid: string): string {
  const g = (GRID_PREFIX[grid] ?? grid).toLowerCase();
  return `${GRID_NAME[g] ?? grid}: ${LICENSE_TITLE_SUFFIX}`;
}

/** Session 502: the license words of one table on the day, for a page's license line (components/tool/TableLicenses.tsx):
 *  "public" when the table is not held (every table a page reads is public in coverage.csv: tests/test_session502.py),
 *  "held: license needed" when it is held whole, "held for <the grids>: license needed" when it is held by grid. */
export function licenseWords(table: string, now: Date = new Date()): string {
  if (!licenseNeeded(table, now)) return "public";
  if (licenseByGrid(table)) return `held for ${licensePublishers(table).join(", ")}: ${LICENSE_NEEDED}`;
  return `held: ${LICENSE_NEEDED}`;
}
