// Energy Research Warehouse (ERW) site, session 154: the one file "Rules in motion" reads (/cost-of-power, the section
// "How soon"): data/datacenter/rules.json, written whole by the warehouse's builder. It is read from the folder when a
// request asks (next.config.ts already lists data/datacenter for the page's server trace), so a build made before the
// file exists still serves the page: the block then reads "not held yet". Nothing is read from the database.
import "server-only";
import fs from "node:fs";
import path from "node:path";
import { fileOf, type RulesFile } from "@/lib/rules";

let kept: { stamp: string; file: RulesFile | null; error: string | null } | null = null;
/** The rules file, or null with the reason it could not be read. Read again only when the file on disk has changed. */
export function rulesFile(): { file: RulesFile | null; error: string | null } {
  const at = path.join(process.cwd(), "data", "datacenter", "rules.json");
  let stamp: string;
  try { const s = fs.statSync(at); stamp = `${s.mtimeMs}:${s.size}`; } catch { return { file: null, error: "not there" }; }
  if (kept && kept.stamp === stamp) return { file: kept.file, error: kept.error };
  let file: RulesFile | null = null, error: string | null = null;
  try {
    file = fileOf(JSON.parse(fs.readFileSync(at, "utf8")));
    if (!file) error = "not a rules file";
  } catch (e) { error = (e as Error).message; }
  kept = { stamp, file, error };
  return { file, error };
}
