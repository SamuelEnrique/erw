// Session 10401 (chain 720, part C): the ERW forecast's report card as a CSV (lib/predict.ts scoresCsv): every row of the
// score file as the file holds it, every place, method, series and cut, with the provenance first. Under /forecast and
// without an extension, so the release gate covers it as it covers the page. It asks nothing of Supabase.
import { scoresCsv } from "@/lib/predict";
import { predictScores } from "@/lib/predictfiles";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const scores = predictScores();
  if (!scores) return new Response("The forecast's score file is not on the site yet.\n", { status: 404, headers: { "Content-Type": "text/plain; charset=utf-8", "X-Robots-Tag": "noindex" } });
  return new Response(scoresCsv(scores, new URL(req.url).toString()), {
    headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": "attachment; filename=\"erw_forecast_scores.csv\"", "X-Robots-Tag": "noindex" },
  });
}
