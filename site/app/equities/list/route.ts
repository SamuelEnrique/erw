// Session 10402 (chain 720, part D): the listed energy companies by segment as a CSV (lib/equities.ts listCsv): every
// company the list holds, whatever the page's filter, with the segments' rules in its provenance. Under /equities and
// without an extension, so the release gate covers it as it covers the page. It asks nothing of Supabase.
import { listCsv } from "@/lib/equities";
import { equitiesList } from "@/lib/equitiesfiles";
import { attach, notHere } from "../reader";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const list = equitiesList();
  if (!list) return notHere("The list of companies is not on the site yet.");
  return new Response(listCsv(list, new URL(req.url).toString()), { headers: attach("erw_equities_companies.csv", "text/csv") });
}
