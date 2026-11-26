// Session 10401 (chain 720, part C): the ERW forecast's ledger, as the forecast build wrote it (site/data/predict/
// ledger_demand.csv, ledger_price.csv: every forecast as made on its day, appended and never rewritten; the contract's
// change of 26 November 2026). The file is served as it is, its own "#" lines of provenance first. Under /forecast and
// without an extension, so the release gate covers it as it covers the page. It asks nothing of Supabase.
import { predictLedger } from "@/lib/predictfiles";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const s = new URL(req.url).searchParams.get("s") === "price" ? "price" : "demand";
  const text = predictLedger(s);
  if (text === null) return new Response("The forecast's ledger is not on the site yet.\n", { status: 404, headers: { "Content-Type": "text/plain; charset=utf-8", "X-Robots-Tag": "noindex" } });
  return new Response(text, { headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="erw_forecast_ledger_${s}.csv"`, "X-Robots-Tag": "noindex" } });
}
