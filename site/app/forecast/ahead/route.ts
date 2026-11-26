// Session 10405 (chain 720, part E): the ERW forecast of demand for the days after tomorrow as a CSV (lib/predict.ts
// aheadCsv): every hour of every horizon the file shows, every place, with the provenance first. Under /forecast and
// without an extension, so the release gate covers it as it covers the page. It asks nothing of Supabase and reads no
// word of the address.
import { aheadCsv } from "@/lib/predict";
import { predictAhead } from "@/lib/predictfiles";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const ahead = predictAhead();
  if (!ahead || ahead.example === true) return new Response("The file of the days ahead is not on the site yet.\n", { status: 404, headers: { "Content-Type": "text/plain; charset=utf-8", "X-Robots-Tag": "noindex" } });
  return new Response(aheadCsv(ahead, new URL("/forecast/ahead", req.url).toString()), {
    headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": "attachment; filename=\"erw_forecast_days_ahead.csv\"", "X-Robots-Tag": "noindex" },
  });
}
