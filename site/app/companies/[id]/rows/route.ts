// Session 3306 (chain 200): a company's public rows of the company database (company_links), as a CSV with its
// provenance first (lib/companydb.ts linksCsv). Under /companies and without an extension, so the release gate covers it
// as it covers the page. A held table's rows are not in it; their counts are in its header. It asks nothing of Supabase.
import { linksCsv, linksOf } from "@/lib/companydb";
import { company, companyIndex } from "@/lib/companydata";

export const dynamic = "force-dynamic";

export async function GET(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const c = company(id);
  if (!c) return new Response("No listed company has this id.\n", { status: 404, headers: { "Content-Type": "text/plain; charset=utf-8" } });
  const ix = companyIndex();
  return new Response(linksCsv(c, linksOf(c, ix), ix, new URL(req.url).toString()), {
    headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="erw_company_${c.id}.csv"`, "X-Robots-Tag": "noindex" },
  });
}
