// Session 10401 (chain 720, part C): a place's hours of the ERW forecast as a CSV (lib/predict.ts rowsCsv): tomorrow's
// forecast and every past hour held, both series, with the provenance first. A series that is not shown (license
// needed, paused, too short, not built) has no line and the header says why. Under /forecast and without an extension,
// so the release gate covers it as it covers the page. It reads the page's own files and asks nothing of Supabase.
import { rowsCsv } from "@/lib/predict";
import { predictIndex, predictPlace } from "@/lib/predictfiles";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const u = new URL(req.url);
  const index = predictIndex();
  const place = index?.places.find((p) => p.place === u.searchParams.get("place"));
  const file = predictPlace(place);
  if (!place || !file) return new Response("No forecast file is on the site for this place.\n", { status: 404, headers: { "Content-Type": "text/plain; charset=utf-8", "X-Robots-Tag": "noindex" } });
  return new Response(rowsCsv(file, u.toString()), {
    headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="erw_forecast_${place.place}.csv"`, "X-Robots-Tag": "noindex" },
  });
}
