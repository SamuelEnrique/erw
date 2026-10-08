// Session 146: the datacenter overlay of "Where the resources are": the facilities of datacenter_facilities in the
// live set that the table places. Under /resources, so the release gate covers it. A read that fails is answered with
// its reason, and the page shows a placeholder.
import { datacenters } from "@/lib/resourcesdata";
import { attempt } from "@/lib/supabase";

export const dynamic = "force-static";
export const revalidate = 3600;

export async function GET() {
  const res = await attempt(datacenters);
  return Response.json(res.ok ? res.data : { ok: false, reason: res.reason }, { headers: { "X-Robots-Tag": "noindex" } });
}
