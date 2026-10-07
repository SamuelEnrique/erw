// Session 146: the plants overlay of "Where the resources are": EIA-860M's operating and planned units with their
// coordinates, from the project map's own copy of the two tables. Under /resources, so the release gate covers it.
import { plants } from "@/lib/resourcesdata";

export const dynamic = "force-static";

export function GET() {
  return Response.json(plants(), { headers: { "X-Robots-Tag": "noindex" } });
}
