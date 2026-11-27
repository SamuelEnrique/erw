// Session 10410 (chain 720, part E): a Stata reader of a hub's real-time price forecast (/forecast/realtime-price),
// with the address of the rows on the site that serves it (lib/csvreader.ts). Under /forecast, so the release gate
// covers it. The hub is one the file lists, and the address written into the reader is built again from it: nothing of
// the request's own words is passed on into the script.
import { csvReader } from "@/lib/csvreader";
import { predictRtPrice } from "@/lib/predictfiles";
import { RT_READER } from "../reader";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const hub = predictRtPrice()?.hubs.find((h) => h.hub === new URL(req.url).searchParams.get("hub"));
  if (!hub) return new Response("No real-time price forecast is on the site for this hub.\n", { status: 404, headers: { "Content-Type": "text/plain; charset=utf-8", "X-Robots-Tag": "noindex" } });
  const url = new URL(`/forecast/realtime-price?hub=${encodeURIComponent(hub.hub)}`, req.url).toString();
  return new Response(csvReader("do", url, RT_READER), {
    headers: { "Content-Type": "text/plain; charset=utf-8", "Content-Disposition": `attachment; filename="erw_forecast_real_time_price_${hub.grid}.do"`, "X-Robots-Tag": "noindex" },
  });
}
