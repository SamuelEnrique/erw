// Session 8013 (chain 505, part C): one balancing authority's own facts, or one region's sum, for the panel that opens
// on a click of the map or the network in the Grid tool (components/grid/AuthorityFacts.tsx). The file is the data
// machine's (data/regions/authority/, docs/state/page_files_regions.md section 10). Under /grid and without an
// extension, so the release gate covers it as it covers the page. Made when the site is built, one address a file.
import { authorityBody, authorityStems } from "@/lib/regionsdata";

export const dynamic = "force-static";
export const dynamicParams = false;

export function generateStaticParams() {
  // with no file on the server one name that answers "not held", so the build has a page to make
  const stems = authorityStems();
  return (stems.length ? stems : ["none"]).map((code) => ({ code }));
}

export async function GET(_req: Request, { params }: { params: Promise<{ code: string }> }) {
  const { code } = await params;
  const body = authorityBody(code);
  const headers = { "Content-Type": "application/json; charset=utf-8", "X-Robots-Tag": "noindex" };
  if (!body) return new Response(JSON.stringify({ held: false, file: `data/regions/authority/${code}.json` }), { headers });
  return new Response(new Uint8Array(body), { headers });
}
