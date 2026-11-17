// Energy Research Warehouse (ERW) site, session 7531 (chain 304): a stand-in for next/font/google, which exists only
// inside a Next build, so components/Brand.tsx can be imported by a script that draws a whole /events page to HTML
// (scripts/events-pages.mjs). Each family is given an empty class; nothing else is replaced. The same stand-in as
// session 7514's for the battery awards page, kept under the tool's own name so neither branch depends on the other.
const FONT = "const f = () => ({ variable: '', className: '', style: { fontFamily: 'sans-serif' } }); export const IBM_Plex_Mono = f, IBM_Plex_Sans = f, Source_Serif_4 = f;";
export async function resolve(specifier, context, next) {
  if (specifier === "next/font/google") return { url: "erw-font-stand-in:google", shortCircuit: true };
  return next(specifier, context);
}
// With EVENTS_DRAW_UNHELD=1 in the environment, the license status file is served without its two event tables, so the
// pages draw every figure they compute, the ones the hold of 21 October 2026 draws as "license needed" included. That
// is for the replication only (it recomputes what the page computes, held or not); the page itself, its status file
// and its hold are not changed, and without the variable the pages are drawn exactly as a visitor's build draws them.
import fs from "node:fs";
import { fileURLToPath } from "node:url";
const UNHELD = process.env.EVENTS_DRAW_UNHELD === "1";
export async function load(url, context, next) {
  if (url === "erw-font-stand-in:google") return { format: "module", source: FONT, shortCircuit: true };
  if (UNHELD && url.startsWith("file:") && url.replace(/\\/g, "/").endsWith("/data/license_status.json")) {
    const s = JSON.parse(fs.readFileSync(fileURLToPath(url), "utf-8"));
    delete s.tables.event_window_daily;
    delete s.tables.event_study_estimates;
    return { format: "module", source: `export default ${JSON.stringify(s)};`, shortCircuit: true };
  }
  return next(url, context);
}
