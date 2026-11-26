// Session 10402 (chain 720, part D): the figures a company filed, period by period, as a CSV (lib/equities.ts filedCsv),
// in the file's own columns with the provenance first; each row carries its filing's address on the SEC's site. Under
// /equities and without an extension, so the release gate covers it as it covers the page. It asks nothing of Supabase.
import { filedCsv } from "@/lib/equities";
import { attach, notHere, seriesOf } from "../reader";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const s = seriesOf(req);
  if (!s || s.kind !== "company") return notHere("No company of this id is on the site.");
  return new Response(filedCsv(s, new URL(req.url).toString()), { headers: attach(`erw_equities_${s.id}_filed.csv`, "text/csv") });
}
