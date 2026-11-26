// Session 10402 (chain 720, part D): a Python reader of a series' daily rows (/equities/rows), with the address of the
// rows on the site that serves it (lib/csvreader.ts). Under /equities, so the release gate covers it.
import { csvReader } from "@/lib/csvreader";
import { attach, notHere, rowsSpec, seriesOf } from "../../reader";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const s = seriesOf(req);
  if (!s) return notHere("No series of this id is on the site.");
  const url = new URL(`/equities/rows${new URL(req.url).search}`, req.url).toString();
  return new Response(csvReader("py", url, rowsSpec(s)), { headers: attach(`erw_equities_${s.id}.py`) });
}
