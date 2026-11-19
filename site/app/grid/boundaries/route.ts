// Session 8601 (chain 504): the balancing authorities' boundaries for the Grid tool's map, read only when the map is
// chosen. Under /grid and without an extension, so the release gate covers it as it covers the page (lib/release.ts: an
// address under a page takes that page's status). Made when the site is built. The file is the data machine's
// (data/regions/ba_boundaries.json, docs/state/page_files_regions.md section 1); until it is on the server this
// address answers that it is not held, and the map draws the file it has drawn since session 193, with its label.
import { boundariesBody } from "@/lib/regionsdata";

export const dynamic = "force-static";

export function GET() {
  const body = boundariesBody();
  const headers = { "Content-Type": "application/json; charset=utf-8", "X-Robots-Tag": "noindex" };
  // always an answer the map can read: the file as it stands, or one object that says it is not held
  if (!body) return new Response(JSON.stringify({ held: false, file: "data/regions/ba_boundaries.json" }), { headers });
  return new Response(new Uint8Array(body), { headers });
}
