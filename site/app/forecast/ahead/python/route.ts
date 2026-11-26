// Session 10405 (chain 720, part E): a Python reader of the ERW forecast's days ahead (/forecast/ahead), with the
// address of the rows on the site that serves it (lib/csvreader.ts). Under /forecast, so the release gate covers it.
import { csvReader } from "@/lib/csvreader";
import { AHEAD_READER } from "../reader";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const url = new URL("/forecast/ahead", req.url).toString();
  return new Response(csvReader("py", url, AHEAD_READER), {
    headers: { "Content-Type": "text/plain; charset=utf-8", "Content-Disposition": "attachment; filename=\"erw_forecast_days_ahead.py\"", "X-Robots-Tag": "noindex" },
  });
}
