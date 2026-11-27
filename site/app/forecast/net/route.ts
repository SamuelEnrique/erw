// Session 10410 (chain 720, part E): a place's ERW forecast of net demand, wind and solar as a CSV (lib/predictlines.ts
// netCsv): net demand for the day forecast now, and wind and solar for that day and every past hour the wind and solar
// file holds, with the provenance first. A line that is not shown has no row and the header says why. Under /forecast
// and without an extension, so the release gate covers it as it covers the page. It reads the page's own files and asks
// nothing of Supabase.
import { isShown } from "@/lib/predict";
import { netCsv } from "@/lib/predictlines";
import { predictIndex, predictPlace, predictWindSolar } from "@/lib/predictfiles";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const u = new URL(req.url);
  const index = predictIndex();
  const place = index?.places.find((p) => p.place === u.searchParams.get("place"));
  const file = predictPlace(place);
  const demand = file?.series?.demand;
  if (!place || !file || file.example === true || !isShown(file, demand) || !demand?.net_demand) return new Response("No net demand, wind or solar forecast is on the site for this place.\n", { status: 404, headers: { "Content-Type": "text/plain; charset=utf-8", "X-Robots-Tag": "noindex" } });
  const ws = predictWindSolar();
  return new Response(netCsv(place, demand, ws && ws.example !== true ? ws : null, u.toString()), {
    headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="erw_forecast_net_demand_${place.place}.csv"`, "X-Robots-Tag": "noindex" },
  });
}
