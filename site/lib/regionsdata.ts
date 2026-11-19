// Energy Research Warehouse (ERW) site, session 8601 (chain 504, 19 November 2026): what the Grid tool reads on the
// server from the whole country's page files (data/regions/, written by the data machine; the contract is
// docs/state/page_files_regions.md). Those files arrive one by one, so every reader here answers "not held" for a file
// that is not on the server yet, and nothing is drawn in its place.
import "server-only";
import fs from "node:fs";
import path from "node:path";
import { readAlike, readIndex, readMix, readTrade, regionBy, type Alike, type RegionIndex, type RegionMix, type RegionTrade } from "@/lib/gridregions";

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

// Session 8602: the thirteen regions in the Grid tool. Each reader gives the file as the page uses it, or null when
// the server does not hold it or it is not that file whole (lib/gridregions.ts decides). A region's files are named by
// EIA's code in lower case (the contract's common rules); the code is checked against the thirteen before a path is made.
const read = new Map<string, { at: number; value: unknown }>();   // a file is parsed once for each time it was written
function json(rel: string): unknown {
  const file = path.join(process.cwd(), "data", "regions", rel);
  let at: number;
  try { at = fs.statSync(file).mtimeMs; } catch { return null; }
  const had = read.get(rel);
  if (had && had.at === at) return had.value;
  let value: unknown = null;
  try { value = JSON.parse(fs.readFileSync(file, "utf8")); } catch { value = null; }
  read.set(rel, { at, value });
  return value;
}
const fileOf = (code: string) => (regionBy(code) ? `${regionBy(code)!.toLowerCase()}.json` : null);

/** Section 2 of the contract: the thirteen regions and the balancing authorities EIA places in each. */
export function regionsIndex(): RegionIndex | null {
  return readIndex(json("index.json"));
}
/** Section 4: a region's generation by source, by month, by year and for its newest 35 days by hour. */
export function regionMix(code: string): RegionMix | null {
  const f = fileOf(code);
  return f ? readMix(json(path.join("mix", f))) : null;
}
/** Section 5: a region's trade with each neighbour, by month, from both sides' reports. */
export function regionTrade(code: string): RegionTrade | null {
  const f = fileOf(code);
  return f ? readTrade(json(path.join("trade", f))) : null;
}
/** Section 3, the `alike` object alone: a region beside the grid that covers nearly its ground, and why they differ. */
export function regionAlike(code: string): Alike | null {
  const f = fileOf(code);
  return f ? readAlike(json(path.join("demand", f))) : null;
}
