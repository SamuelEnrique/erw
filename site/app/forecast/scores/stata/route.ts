// Session 10401 (chain 720, part C): a Stata reader of the ERW forecast's report card (/forecast/scores), with the
// address of the rows on the site that serves it (lib/csvreader.ts). Under /forecast, so the release gate covers it.
import { csvReader } from "@/lib/csvreader";
import { SCORES_READER } from "../reader";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const url = new URL("/forecast/scores", req.url).toString();
  return new Response(csvReader("do", url, SCORES_READER), {
    headers: { "Content-Type": "text/plain; charset=utf-8", "Content-Disposition": "attachment; filename=\"erw_forecast_scores.do\"", "X-Robots-Tag": "noindex" },
  });
}
