// Energy Research Warehouse (ERW) site, chain 780 (session 11600): the regions files of the All grids tab, read on the
// server when a request asks for the tab. They are read through the site's one reader of a page file (lib/pagefile.ts),
// by names the index gives at request time, so the data machine's files land with no change of code
// (next.config.ts names the folder for /cost-of-power's trace). A file that is missing, is not JSON or has not the
// contract's shape gives no section's worth of figures: the section then says the files are not built, and draws none.
//
// ERW_SITING_REGIONS_DIR names another data folder (one that holds siting/regions/): a test's fixture or a local look
// at files that have not landed. It is never set on the site.
import { DATA_DIR, readPageFile } from "@/lib/pagefile";
import { INDEX_FILE, TABLE_FILE, placeFile, type IndexFile, type PlaceFile, type TableFile } from "./lib";

const dataDir = (): string => process.env.ERW_SITING_REGIONS_DIR || DATA_DIR();

export type Loaded =
  | { state: "files"; index: IndexFile; table: TableFile }
  | { state: "example" | "none"; why: string };

const isIndex = (d: unknown): d is IndexFile => !!d && typeof d === "object" && Array.isArray((d as IndexFile).places) && Array.isArray((d as IndexFile).sections);
const isTable = (d: unknown): d is TableFile => !!d && typeof d === "object" && Array.isArray((d as TableFile).columns) && Array.isArray((d as TableFile).rows) && typeof (d as TableFile).sources === "object";

/** The index and the table, or why the section has nothing to draw. The contract's own example files (every value
 *  null, `example` true) are not drawn as a table of blanks: they are said to be examples. */
export function loadRegions(): Loaded {
  let index: unknown, table: unknown;
  try {
    index = readPageFile(INDEX_FILE, dataDir());
    table = readPageFile(TABLE_FILE, dataDir());
  } catch {
    return { state: "none", why: "not built yet: the regions files (site/data/siting/regions) are not on this build of the site" };
  }
  if (!isIndex(index) || !isTable(table)) return { state: "none", why: "not built yet: the regions files do not have the shape their contract gives (docs/state/page_files_siting_regions.md)" };
  if (index.example === true || table.example === true) {
    return { state: "example", why: "not built yet: the files on this build are the contract's own examples, written before the data machine's builder ran; every value in them is empty, and none is drawn" };
  }
  return { state: "files", index, table };
}

/** A place's own file, by the name the index gives it; null when it is not there or is not the place's. */
export function loadPlace(index: IndexFile, id: string): PlaceFile | null {
  const p = index.places.find((x) => x.id === id);
  const file = p ? placeFile(p.file) : null;
  if (!file) return null;
  try {
    const d = readPageFile(file, dataDir()) as PlaceFile;
    return d && typeof d === "object" && d.id === id && d.sections && typeof d.sections === "object" ? d : null;
  } catch {
    return null;
  }
}
/** The path of a place's file under site/data, for its figures' check keys. */
export const placePath = (index: IndexFile, id: string): string | null => {
  const p = index.places.find((x) => x.id === id);
  return p ? placeFile(p.file) : null;
};
