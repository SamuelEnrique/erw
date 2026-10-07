// Session 146: the queue overlay of "Where the resources are": the interconnection queue's rows of energy_projects in
// the live set, counted by county. Under /resources, so the release gate covers it. A read that fails is answered with
// its reason, and the page shows a placeholder.
import { queue } from "@/lib/resourcesdata";
import { attempt } from "@/lib/supabase";

export const dynamic = "force-static";
export const revalidate = 3600;

export async function GET() {
  const res = await attempt(queue);
  return Response.json(res.ok ? res.data : { ok: false, reason: res.reason }, { headers: { "X-Robots-Tag": "noindex" } });
}
