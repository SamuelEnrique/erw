// Session 10410 (chain 720, part E): a hub's ERW forecast of the real-time price as a CSV (lib/predictlines.ts rtCsv):
// the day forecast now and every past hour the file holds, beside the hub's day-ahead price, with the provenance first.
// A day with no forecast has no row and the header says why. Under /forecast and without an extension, so the release
// gate covers it as it covers the page. The hub is one the file lists: nothing else of the address is read. It reads
// the page's own file and asks nothing of Supabase.
import { rtCsv } from "@/lib/predictlines";
import { predictRtPrice } from "@/lib/predictfiles";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const u = new URL(req.url);
  const file = predictRtPrice();
  const hub = file && file.example !== true ? file.hubs.find((h) => h.hub === u.searchParams.get("hub")) : undefined;
  if (!file || !hub) return new Response("No real-time price forecast is on the site for this hub.\n", { status: 404, headers: { "Content-Type": "text/plain; charset=utf-8", "X-Robots-Tag": "noindex" } });
  return new Response(rtCsv(hub, file, new URL(`/forecast/realtime-price?hub=${encodeURIComponent(hub.hub)}`, req.url).toString()), {
    headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="erw_forecast_real_time_price_${hub.grid}.csv"`, "X-Robots-Tag": "noindex" },
  });
}
