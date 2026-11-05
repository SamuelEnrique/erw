// Energy Research Warehouse (ERW) site, session 587: the held figures that show (/internal/holds). The file is written
// by scripts/build-content.mjs before every build (scripts/holds-content.mjs), from docs/licenses_holds.csv, the list
// scripts/check-holds.mjs --csv writes, and warehouse/metadata/license_status.csv. Server only: no page for visitors
// imports this, and it holds no figure of a held table, only addresses, tables, grids, verdicts and counts.
import "server-only";
import holds from "@/content/holds.json";

/** One line of docs/licenses_holds.csv, each cell as the check wrote it. */
export type HoldRow = { page: string; figures: string; kinds: string; tables: string; grids: string; day: string };
/** A table's record in warehouse/metadata/license_status.csv. */
export type HoldTable = { status: string; verdict: string; from: string; publishers: string };
export type Holds = {
  built_at: string;
  source: string;
  status_source: string;
  columns: string[];
  unread: string | null;
  status_unread: string | null;
  rows: HoldRow[];
  tables: Record<string, HoldTable | null>;
};

export const HOLDS = holds as unknown as Holds;

/** The tables a row names, as scripts/check-holds.mjs joins them ("; "). */
export const tablesOf = (cell: string): string[] => cell.split(";").map((x) => x.trim()).filter(Boolean);

/** A cell that is an address on this site ("/grid?grid=isone"), so the page may link it; anything else is shown as text. */
export const isSitePath = (page: string): boolean => /^\/(?!\/)[^\s"<>\\]*$/.test(page);

export const REPO = "https://github.com/SamuelEnrique/erw";
