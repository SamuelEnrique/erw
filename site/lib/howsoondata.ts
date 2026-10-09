// Energy Research Warehouse (ERW) site, session 163: the one file "How long a large load waits" reads (/cost-of-power,
// the section "How soon"): data/datacenter/how_soon.json, written whole by warehouse/derived/how_soon.py. It holds
// aggregates only. It is read from the folder when a request asks (next.config.ts already lists data/datacenter for the
// page's server trace), so a build made before the file exists still serves the page: the block then reads "not held
// yet". Nothing is read from the database, and no table of requests is read at all.
import "server-only";
import fs from "node:fs";
import path from "node:path";
import { fileOf, type HowSoonFile } from "@/lib/howsoon";

let kept: { stamp: string; file: HowSoonFile | null; error: string | null } | null = null;
/** The file of measured waits, or null with the reason it could not be read. Read again only when the file on disk has changed. */
export function howSoonFile(): { file: HowSoonFile | null; error: string | null } {
  const at = path.join(process.cwd(), "data", "datacenter", "how_soon.json");
  let stamp: string;
  try { const s = fs.statSync(at); stamp = `${s.mtimeMs}:${s.size}`; } catch { return { file: null, error: "not there" }; }
  if (kept && kept.stamp === stamp) return { file: kept.file, error: kept.error };
  let file: HowSoonFile | null = null, error: string | null = null;
  try {
    file = fileOf(JSON.parse(fs.readFileSync(at, "utf8")));
    if (!file) error = "not a file of measured waits";
  } catch (e) { error = (e as Error).message; }
  kept = { stamp, file, error };
  return { file, error };
}
