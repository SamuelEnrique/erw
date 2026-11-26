// Session 10401 (chain 720, part C): a Stata reader of a place's hours of the ERW forecast (/forecast/rows), with the
// address of the rows on the site that serves it (lib/csvreader.ts). Under /forecast, so the release gate covers it.
import { csvReader } from "@/lib/csvreader";
import { ROWS_READER } from "../reader";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const u = new URL(req.url);
  const url = new URL(`/forecast/rows${u.search}`, req.url).toString();
  return new Response(csvReader("do", url, ROWS_READER), {
    headers: { "Content-Type": "text/plain; charset=utf-8", "Content-Disposition": "attachment; filename=\"erw_forecast_rows.do\"", "X-Robots-Tag": "noindex" },
  });
}
