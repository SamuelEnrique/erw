// Session 10411 (chain 720, part E): one more hub's ERW forecast of the day-ahead price as a CSV (lib/predictlines.ts
// hubCsv; site/data/predict/price_hubs.json): the day forecast now and every past hour the file holds, with the
// provenance first. A day with no forecast has no row and the header says why. Under /forecast and without an
// extension, so the release gate covers it as it covers the page. The hub is one the file lists: nothing else of the
// address is read. It reads the page's own file and asks nothing of Supabase.
import { hubCsv } from "@/lib/predictlines";
import { predictPriceHubs } from "@/lib/predictfiles";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const u = new URL(req.url);
  const file = predictPriceHubs();
  const hub = file && file.example !== true ? file.hubs.find((h) => h.hub === u.searchParams.get("hub")) : undefined;
  if (!file || !hub) return new Response("No day-ahead price forecast is on the site for this hub.\n", { status: 404, headers: { "Content-Type": "text/plain; charset=utf-8", "X-Robots-Tag": "noindex" } });
  return new Response(hubCsv(hub, file, new URL(`/forecast/hub-price?hub=${encodeURIComponent(hub.hub)}`, req.url).toString()), {
    headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="erw_forecast_day_ahead_price_${hub.grid}.csv"`, "X-Robots-Tag": "noindex" },
  });
}
