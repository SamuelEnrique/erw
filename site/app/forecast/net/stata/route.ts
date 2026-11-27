// Session 10410 (chain 720, part E): a Stata reader of a place's net demand, wind and solar forecast (/forecast/net),
// with the address of the rows on the site that serves it (lib/csvreader.ts). Under /forecast, so the release gate
// covers it. The place is one the index lists, and the address written into the reader is built again from it: nothing
// of the request's own words is passed on into the script.
import { csvReader } from "@/lib/csvreader";
import { predictIndex } from "@/lib/predictfiles";
import { NET_READER } from "../reader";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const place = predictIndex()?.places.find((p) => p.place === new URL(req.url).searchParams.get("place"));
  if (!place) return new Response("No forecast file is on the site for this place.\n", { status: 404, headers: { "Content-Type": "text/plain; charset=utf-8", "X-Robots-Tag": "noindex" } });
  const url = new URL(`/forecast/net?place=${place.place}`, req.url).toString();
  return new Response(csvReader("do", url, NET_READER), {
    headers: { "Content-Type": "text/plain; charset=utf-8", "Content-Disposition": `attachment; filename="erw_forecast_net_demand_${place.place}.do"`, "X-Robots-Tag": "noindex" },
  });
}
