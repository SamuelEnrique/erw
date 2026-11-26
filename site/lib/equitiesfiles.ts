// Energy Research Warehouse (ERW) site, session 10402 (chain 720, part D): the reader of the energy equities page files
// (site/data/equities/, written by the data machine's warehouse/derived/equity_pages.py; contract
// docs/state/page_files_equities.md): the list, the board's rows, the energy prices, and one file a company, an index
// or a segment under series/. A file is read when it is asked for, in the manner of lib/predictfiles.ts: a file not on
// the site is null and the page draws its blanks. A file that says it is a test's fixture is read only from a test's
// own folder (ERW_EQUITIES_DIR), never from the site's.
import fs from "node:fs";
import path from "node:path";
import type { EqBoardFile, EqList, EqPrices, EqSeries } from "@/lib/equities";

/** The text of a file of the site's own folder, or null. The path is written out from the site's root so that the build
 *  sees which folder is read and carries that folder with the route, and no more. */
function siteText(parts: string[]): string | null {
  const at = path.join(process.cwd(), "data", "equities", ...parts);
  return fs.existsSync(at) ? fs.readFileSync(at, "utf8") : null;
}
/** The text of a file of a test's folder (ERW_EQUITIES_DIR), or null. The build is told not to follow these reads. */
function testText(dir: string, parts: string[]): string | null {
  const at = path.join(/*turbopackIgnore: true*/ dir, ...parts);
  return fs.existsSync(/*turbopackIgnore: true*/ at) ? fs.readFileSync(/*turbopackIgnore: true*/ at, "utf8") : null;
}

/** One page file by its path under the folder ("index.json", "series/XOM.json"), or null. Only a plain file name, or
 *  one under series/, is read. */
export function readEquities<T>(rel: string): T | null {
  if (!/^(series\/)?[A-Za-z0-9][A-Za-z0-9._-]*\.json$/.test(rel) || rel.includes("..")) return null;
  try {
    const parts = rel.split("/");
    const text = process.env.ERW_EQUITIES_DIR ? testText(process.env.ERW_EQUITIES_DIR, parts) : siteText(parts);
    if (text === null) return null;
    const v = JSON.parse(text) as T & { fixture?: string };
    if (v && typeof v === "object" && "fixture" in v && v.fixture && !process.env.ERW_EQUITIES_DIR) return null;
    return v;
  } catch {
    return null;
  }
}

export const equitiesList = () => readEquities<EqList>("index.json");
export const equitiesBoard = () => readEquities<EqBoardFile>("board.json");
export const equitiesPrices = () => readEquities<EqPrices>("energy_prices.json");
/** A series' file by the path the list gives it ("series/XOM.json"). */
export const equitiesSeries = (file: string | null | undefined) => (file ? readEquities<EqSeries>(file) : null);
