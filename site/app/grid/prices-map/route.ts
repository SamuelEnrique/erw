// Session 8013 (chain 505, part E3): what power costs across the map (data/regions/prices_map.json, the data machine's;
// docs/state/page_files_regions.md section 13), read only when the reader turns the map's color to price. Under /grid
// and without an extension, so the release gate covers it as it covers the page. Made when the site is built; until the
// file is on the server this address answers that it is not held, and the switch says so.
import fs from "node:fs";
import path from "node:path";

export const dynamic = "force-static";

export function GET() {
  const headers = { "Content-Type": "application/json; charset=utf-8", "X-Robots-Tag": "noindex" };
  let body: Buffer | null = null;
  try { body = fs.readFileSync(path.join(process.cwd(), "data", "regions", "prices_map.json")); } catch { body = null; }
  if (!body) return new Response(JSON.stringify({ held: false, file: "data/regions/prices_map.json" }), { headers });
  return new Response(new Uint8Array(body), { headers });
}
