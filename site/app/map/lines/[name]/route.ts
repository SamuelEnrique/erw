// Session 8014 (chain 581, part D): one line layer of the project map, read by the map only when its switch is turned
// on (lib/maplayers.ts). The files are the data machine's (site/data/map_layers/, warehouse/connectors/hifld_lines.py).
// Under /map and without an extension, so the release gate covers it as it covers the page. Made when the site is
// built, one address a layer; it asks nothing of Supabase and reads nothing a visitor names.
import transmission from "@/data/map_layers/transmission_230kv.json";
import hgl from "@/data/map_layers/hgl_pipelines.json";

export const dynamic = "force-static";
export const dynamicParams = false;

const FILES: Record<string, unknown> = { transmission, hgl };

export function generateStaticParams() {
  return Object.keys(FILES).map((name) => ({ name }));
}

export async function GET(_req: Request, { params }: { params: Promise<{ name: string }> }) {
  const { name } = await params;
  const body = FILES[name];
  if (!body) return Response.json({ held: false }, { status: 404, headers: { "X-Robots-Tag": "noindex" } });
  return Response.json(body, { headers: { "X-Robots-Tag": "noindex" } });
}
