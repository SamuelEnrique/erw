// Energy Research Warehouse (ERW) site, session 207: the license status of the tables flagged public whose publisher's
// own page asks for permission or a license (docs/licenses.md). The owner's ruling of 12 October 2026: from the day in
// the file (2026-10-20) such a table shows "license needed", as PJM's prices do, unless a permission is recorded.
// Nothing changes before that day. The file is written by `python scripts/licenses.py status` with
// warehouse/metadata/license_status.csv, the record the builders read.
import status from "@/data/license_status.json";

// Session 499: `hold` is "row" for a table held row by row by each row's own license (session 441's method,
// docs/reviews/sources-by-row-2026-10-21.md); absent, or "table", the table is held whole as before. The data machine
// writes it (warehouse/metadata/license_status.csv's `hold` column, copied by scripts/licenses.py status).
export type LicenseStatusRow = { status: string; from: string; publishers: string[]; hold?: string };
const TABLES = status.tables as Record<string, LicenseStatusRow>;

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

/** True when every publisher deciding the table is a grid operator: the hold is by grid, not whole. A table held by
 *  row (session 499) is never also held by grid. */
export function licenseByGrid(table: string): boolean {
  if (licenseByRow(table)) return false;
  const who = licensePublishers(table);
  return who.length > 0 && who.every((p) => p in GRID_PREFIX);
}

// Session 499: the hold by row. Session 441's method gives the four tables whose rows rest on many publishers
// (datacenter_facilities, datacenter_projects, datacenter_operator_sites, energy_deals) two columns, `publishers` and a
// row's license, one of the three values below, computed by the data machine from the row's own publishers. The method
// named the column `license`; the live set's events and entities already carry a `license` column, the table's tier
// (public or internal, migration 001, read by row-level security), so the row's own is `row_license`, a column of the
// table's CSV that the loader keeps in `extra` like the table's other own columns. A table the status file marks
// `hold: "row"` is read for its public rows only (lib/supabase.ts adds the filter) and its held rows are counted, never
// shown. A table without the mark is held whole, as before: nothing changes until the data machine writes the column
// and the mark.
export const ROW_LICENSE_COLUMN = "row_license";
/** The PostgREST name of the row's license in a live-set row: a key of `extra`. */
export const ROW_LICENSE_FILTER = `extra->>${ROW_LICENSE_COLUMN}`;
export const ROW_LICENSE_PUBLIC = "public";
export const ROW_LICENSES = [ROW_LICENSE_PUBLIC, LICENSE_NEEDED, "unsettled"] as const;

/** Whether a status row marks its table as held by row. */
export function holdIsByRow(r: LicenseStatusRow | undefined): boolean {
  return !!r && r.hold === "row";
}

/** True when the status file marks the table as held row by row by each row's own license. */
export function licenseByRow(table: string): boolean {
  return holdIsByRow(TABLES[table]);
}

/** Whether one row is held by its own license field: every value but "public" holds it, a missing one included. */
export function rowLicenseHeld(row: Record<string, unknown> | null | undefined): boolean {
  const extra = (row?.extra ?? {}) as Record<string, unknown>;
  const v = extra[ROW_LICENSE_COLUMN] ?? row?.[ROW_LICENSE_COLUMN];
  return String(v ?? "").trim().toLowerCase() !== ROW_LICENSE_PUBLIC;
}

/** The rows a page may show of a table held by row, and how many are held. Pure: the page's split, tested on fixtures. */
export function splitByRowLicense<T extends Record<string, unknown>>(rows: T[]): { shown: T[]; held: number } {
  const shown = rows.filter((r) => !rowLicenseHeld(r));
  return { shown, held: rows.length - shown.length };
}

/** The grid prefixes ("isone", "miso", "nyiso") whose prices are held on the day: a grid that decides any held table. */
export function licenseHeldGrids(now: Date = new Date()): string[] {
  const out = new Set<string>();
  for (const t of licenseNeededTables(now)) for (const p of licensePublishers(t)) if (p in GRID_PREFIX) out.add(GRID_PREFIX[p]);
  return [...out].sort();
}

/** The grid an entity belongs to, by its prefix: "isone:.H.INTERNAL_HUB" and "iso:isone" are ISO-NE's; "" when none.
 *  Session 499: an interconnection-queue position's id names its grid as "<grid>_queue:<id>" ("nyiso_queue:1630"), and
 *  a load queue's as "<grid>_load_queue:<id>"; both are that grid's (session 467 found them read as no grid). */
export function gridOfEntity(entity: string | undefined | null): string {
  if (!entity) return "";
  const m = /^([a-z0-9_-]+):(.*)$/i.exec(entity);
  if (!m) return "";
  const head = m[1].toLowerCase();
  if (head in GRID_NAME) return head;
  const q = /^([a-z]+)_(?:load_)?queue$/.exec(head);
  if (q && q[1] in GRID_NAME) return q[1];
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
  // session 499: a table held by row is read for its public rows only (lib/supabase.ts), so a figure of what a page
  // was given is of public rows; held rows never reach the page. Asked about the table whole, it is held.
  if (licenseByRow(table)) return entity === undefined;
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
