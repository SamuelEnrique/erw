// Energy Research Warehouse (ERW) site, session 138: the files "What a datacenter pays" reads (/cost-of-power).
// The index is bundled; a grid's years of hourly prices are read from data/datacenter when a request first asks for
// that grid, and kept (next.config.ts lists the folder for the page's server trace). Nothing is read from the database.
import "server-only";
import fs from "node:fs";
import path from "node:path";
import indexJson from "@/data/datacenter/index.json";
import deliveryJson from "@/data/datacenter/texas_delivery.json";
import type { Index, YearFile } from "@/lib/datacenter";

export const INDEX = indexJson as unknown as Index;

export type DeliveryRow = {
  utility: string; rate_class: string; charge: string; value: number; value_as_written: string; unit: string; effective: string | null;
  document: string; url: string; page: string | null; sentence: string; column: string; terms: string;
  // session 140: what the charge is (the tariff's own words are in `why`), and whether it applies to every such load
  kind?: "transmission" | "distribution" | "other"; applies?: string; why?: string;
};
/** Session 140: a figure of the Commission's transmission charge matrix, as printed (texas_transmission_matrix). */
export type MatrixRow = {
  year: string; matrix: string; scope: string; quantity: string; value: number; value_as_written: string; unit: string; header: string; status: string;
  docket: string; item: string; filed: string; document: string; url: string; page: string | null; scan_url: string; scan_page: string | null; sentence: string;
  docket_status: string; digits_spaced: boolean;
};
/** `withheld`: a utility whose charges are held internally (its terms), with the words the page shows and why. */
export type DeliveryFile = { table: string | null; built: string | null; license: string | null; note: string | null; rows: DeliveryRow[]; withheld: { utility: string; words: string; why: string }[]; matrix?: MatrixRow[]; matrix_table?: string };
export const DELIVERY = deliveryJson as unknown as DeliveryFile;

const cache = new Map<string, YearFile[]>();
/** Every year held of a grid, oldest first. Throws when a file the index names cannot be read. */
export function yearFiles(grid: string): YearFile[] {
  const have = cache.get(grid);
  if (have) return have;
  const g = INDEX.grids[grid];
  if (!g) return [];
  const dir = path.join(process.cwd(), "data", "datacenter");
  const files = g.years.map((y) => JSON.parse(fs.readFileSync(path.join(dir, `${grid}_${y}.json`), "utf8")) as YearFile);
  cache.set(grid, files);
  return files;
}
