// Session 10402 (chain 720, part D): a company's, an index's or a segment's daily rows as a CSV (lib/equities.ts
// seriesCsv), with the provenance first: the file's own columns, a held column empty and named in the header with its
// reason; a series that is not shown has its header and no row. Under /equities and without an extension, so the
// release gate covers it as it covers the page. It reads the page's own files and asks nothing of Supabase.
import { seriesCsv } from "@/lib/equities";
import { attach, notHere, seriesOf } from "../reader";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const s = seriesOf(req);
  if (!s) return notHere("No series of this id is on the site.");
  return new Response(seriesCsv(s, new URL(req.url).toString()), { headers: attach(`erw_equities_${s.id}.csv`, "text/csv") });
}
