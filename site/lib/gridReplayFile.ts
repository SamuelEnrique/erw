// Energy Research Warehouse (ERW) site, session 1170 (chain 078): the replay's committed daily file of a year, read on the
// server for the Grid tool's replayed-day figures (lib/gridReplay.ts). The browser fetches the same file from /network/;
// the server reads it from site/public/network/ (next.config.ts traces those files into /grid's function). A file that
// cannot be read is said, never filled: the panel then says the day's figures could not be read.
import fs from "node:fs";
import path from "node:path";
import type { ReplayYear } from "@/lib/gridReplay";

export type ReplayRead = { ok: true; y: ReplayYear } | { ok: false; why: string };

const cache = new Map<string, ReplayRead>();

/** The replay's file of the day's year, parsed once a process. */
export function readReplayYear(day: string): ReplayRead {
  const year = day.slice(0, 4);
  const have = cache.get(year);
  if (have) return have;
  let out: ReplayRead;
  try {
    const y = JSON.parse(fs.readFileSync(path.join(process.cwd(), "public", "network", `daily_${year}.json`), "utf8")) as ReplayYear;
    out = Array.isArray(y.days) && Array.isArray(y.links) ? { ok: true, y } : { ok: false, why: `the replay's file of ${year} holds no days` };
  } catch (e) {
    out = { ok: false, why: `the replay's file of ${year} could not be read on the server (${(e as NodeJS.ErrnoException).code ?? "not valid JSON"})` };
  }
  if (out.ok) cache.set(year, out);
  return out;
}
