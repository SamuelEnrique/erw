// Session 10401 (chain 720, part C): a Python reader of the ERW forecast's ledger (/forecast/ledger), with the address
// of the rows on the site that serves it (lib/csvreader.ts). Under /forecast, so the release gate covers it.
import { csvReader } from "@/lib/csvreader";
import { LEDGER_READER } from "../reader";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const s = new URL(req.url).searchParams.get("s") === "price" ? "price" : "demand";
  const url = new URL(`/forecast/ledger?s=${s}`, req.url).toString();
  return new Response(csvReader("py", url, LEDGER_READER), {
    headers: { "Content-Type": "text/plain; charset=utf-8", "Content-Disposition": `attachment; filename="erw_forecast_ledger_${s}.py"`, "X-Robots-Tag": "noindex" },
  });
}
