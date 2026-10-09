// Session 167: what the project map's unit card reads, from the page's own file (data/map.json): the entity ids,
// operators, counties, the source's technology text, dates and the fields one kind alone carries. The page itself
// leaves them out (they would more than double what a phone loads) and asks for them once, at the first click on a
// unit. Under /map and without an extension, so the release gate covers it: a visitor is answered with the in-review
// page, as for the page itself. Made when the site is built; it asks nothing of Supabase.
import mapJson from "@/data/map.json";
import { CARD_KEYS, type MapFile } from "@/lib/projectmap";

export const dynamic = "force-static";

export function GET() {
  const f = mapJson as unknown as MapFile;
  const body = Object.fromEntries(["built", ...CARD_KEYS].map((k) => [k, f[k as keyof MapFile]]));
  return Response.json(body, { headers: { "X-Robots-Tag": "noindex" } });
}
