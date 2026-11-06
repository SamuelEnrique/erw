// Session 3306 (chain 200): a Stata reader of the companies /companies lists for a query (/companies/rows; lib/companydb.ts
// reader), with the address of that CSV, the query kept. Under /companies, so the release gate covers it.
import { reader } from "@/lib/companydb";
import { companyIndex } from "@/lib/companydata";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const u = new URL(req.url);
  const url = new URL(`/companies/rows${u.search}`, req.url).toString();
  const figures = companyIndex().columns.filter((c) => c.startsWith("n_") || c.endsWith("_mw"));
  return new Response(reader("do", url, "the companies of the company database that /companies lists for a query", figures), {
    headers: { "Content-Type": "text/plain; charset=utf-8", "Content-Disposition": "attachment; filename=\"erw_companies.do\"", "X-Robots-Tag": "noindex" },
  });
}
