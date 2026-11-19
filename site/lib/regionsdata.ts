// Energy Research Warehouse (ERW) site, session 8601 (chain 504, 19 November 2026): what the Grid tool reads on the
// server from the whole country's page files (data/regions/, written by the data machine; the contract is
// docs/state/page_files_regions.md). Those files arrive one by one, so every reader here answers "not held" for a file
// that is not on the server yet, and nothing is drawn in its place.
import "server-only";
import fs from "node:fs";
import path from "node:path";

/** A file of data/regions by its path under that folder, or null when the server does not hold it. The path is one
 * this file writes itself (never a visitor's words), so the server's file trace holds that one folder. */
function regionsFile(rel: string): Buffer | null {
  const file = path.join(process.cwd(), "data", "regions", rel);
  try { return fs.readFileSync(file); } catch { return null; }
}

/** The balancing authorities' boundaries (section 1 of the contract: a GeoJSON FeatureCollection), as the file stands,
 * or null when it is not held. */
export function boundariesBody(): Buffer | null {
  return regionsFile("ba_boundaries.json");
}
