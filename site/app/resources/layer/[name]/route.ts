// Session 146: one file of a resource layer of "Where the resources are", by the name the manifest gives it with its
// extension dropped. Under /resources and without an extension, so the release gate covers it: a visitor is answered
// with the in-review page, as for the page itself. Made when the site is built, for every file the manifest names.
import { layerBody, layerStems } from "@/lib/resourcesdata";

export const dynamic = "force-static";

export function generateStaticParams() {
  return layerStems().map((name) => ({ name }));
}

export async function GET(_req: Request, { params }: { params: Promise<{ name: string }> }) {
  const { name } = await params;
  const body = layerBody(name);
  if (!body) return Response.json({ error: "not a file of a resource layer the site holds" }, { status: 404 });
  return new Response(new Uint8Array(body), { headers: { "Content-Type": "application/json; charset=utf-8", "X-Robots-Tag": "noindex" } });
}
