// Session 3306 (chain 200): the companies /companies lists for a query, as a CSV with its provenance first
// (lib/companydb.ts indexCsv). Under /companies, so the release gate covers it as it covers the page. It asks nothing of
// Supabase.
import { filterRows, indexCsv, indexRows, queryOf } from "@/lib/companydb";
import { companyIndex } from "@/lib/companydata";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const ix = companyIndex();
  const u = new URL(req.url);
  const q = queryOf(Object.fromEntries(u.searchParams.entries()), ix);
  const rows = filterRows(indexRows(ix), q);
  return new Response(indexCsv(rows, ix, q, u.toString()), {
    headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": "attachment; filename=\"erw_companies.csv\"", "X-Robots-Tag": "noindex" },
  });
}
