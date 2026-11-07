// Energy Research Warehouse (ERW) site, session 3650: GET /learn/problems/<set>/data.csv. Every figure of a problem
// set as the live page computes it (lib/problems.ts): the worked example's and each question's, once each, with its
// check key, its table, its value, its unit and its source (lib/problemkit.ts). A figure of a table that is not public
// (components/Num.tsx, heldBy) is left out, as the page leaves it out. Provenance in '#' lines at the top, as in the
// ERW's own CSVs. The address takes the problem sets' status (lib/release.ts): in review, it answers the internal view
// alone, as the page does.
import { cookies } from "next/headers";
import citations from "@/data/table_citations.json";
import { heldBy } from "@/components/Num";
import { csvOf, figureRows } from "@/lib/problemkit";
import { problemSet, SETS } from "@/lib/problems";
import { COOKIE, cookieOpens, statusOf } from "@/lib/release";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const text = (msg: string, status: number) => new Response(msg + "\n", { status, headers: { "Content-Type": "text/plain; charset=utf-8" } });
const cite = (t: string) => (citations as Record<string, string>)[t];

export async function GET(_req: Request, { params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const meta = SETS.find((s) => s.slug === slug);
  if (!meta) return text("no such problem set", 404);
  // the proxy (site/proxy.ts) never sees a path with an extension, so the page's status is applied here
  const internal = await cookieOpens((await cookies()).get(COOKIE)?.value, process.env.INTERNAL_COSTS_TOKEN);
  if (!internal && statusOf(`/learn/problems/${slug}`) === "review") return text("in review: this download opens with the page it belongs to", 404);
  let set;
  try {
    set = await problemSet(slug);
  } catch (e) {
    return text(`the set could not be computed: ${e instanceof Error ? e.message : String(e)}`, 503);
  }
  if (!set) return text("no such problem set", 404);
  const readAt = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  const body = csvOf(slug, meta.title, figureRows(set.example, set.questions, (k) => heldBy(k) !== null), readAt, cite);
  return new Response(body, {
    headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="erw-problems-${slug}.csv"`, "Cache-Control": "no-store" },
  });
}
