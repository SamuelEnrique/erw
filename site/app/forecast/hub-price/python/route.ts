// Session 10411 (chain 720, part E): a Python reader of one more hub's day-ahead price forecast (/forecast/hub-price),
// with the address of the rows on the site that serves it (lib/csvreader.ts). Under /forecast, so the release gate
// covers it. The hub is one the file lists, and the address written into the reader is built again from it: nothing of
// the request's own words is passed on into the script.
import { csvReader } from "@/lib/csvreader";
import { predictPriceHubs } from "@/lib/predictfiles";
import { HUB_READER } from "../reader";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const hub = predictPriceHubs()?.hubs.find((h) => h.hub === new URL(req.url).searchParams.get("hub"));
  if (!hub) return new Response("No day-ahead price forecast is on the site for this hub.\n", { status: 404, headers: { "Content-Type": "text/plain; charset=utf-8", "X-Robots-Tag": "noindex" } });
  const url = new URL(`/forecast/hub-price?hub=${encodeURIComponent(hub.hub)}`, req.url).toString();
  return new Response(csvReader("py", url, HUB_READER), {
    headers: { "Content-Type": "text/plain; charset=utf-8", "Content-Disposition": `attachment; filename="erw_forecast_day_ahead_price_${hub.grid}.py"`, "X-Robots-Tag": "noindex" },
  });
}
