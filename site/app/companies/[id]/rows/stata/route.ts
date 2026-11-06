// Session 3306 (chain 200): a Stata reader of a company's public rows (/companies/<id>/rows; lib/companydb.ts reader),
// with the address of the rows on the site that serves it. Under /companies, so the release gate covers it.
import { LINK_HEAD, reader } from "@/lib/companydb";
import { company } from "@/lib/companydata";

export const dynamic = "force-dynamic";

export async function GET(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const c = company(id);
  if (!c) return new Response("No listed company has this id.\n", { status: 404, headers: { "Content-Type": "text/plain; charset=utf-8" } });
  const url = new URL(`/companies/${c.id}/rows`, req.url).toString();
  return new Response(reader("do", url, `the public rows of ${c.name} in the company database`, LINK_HEAD.filter((h) => ["confidence", "mw", "usd"].includes(h))), {
    headers: { "Content-Type": "text/plain; charset=utf-8", "Content-Disposition": `attachment; filename="erw_company_${c.id}.do"`, "X-Robots-Tag": "noindex" },
  });
}
