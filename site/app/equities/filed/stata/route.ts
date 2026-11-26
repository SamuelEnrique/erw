// Session 10402 (chain 720, part D): a Stata reader of the figures a company filed (/equities/filed), with the address
// of the rows on the site that serves it (lib/csvreader.ts). Under /equities, so the release gate covers it.
import { csvReader } from "@/lib/csvreader";
import { attach, filedSpec, notHere, seriesOf } from "../../reader";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  const s = seriesOf(req);
  if (!s || s.kind !== "company") return notHere("No company of this id is on the site.");
  const url = new URL(`/equities/filed${new URL(req.url).search}`, req.url).toString();
  return new Response(csvReader("do", url, filedSpec(s)), { headers: attach(`erw_equities_${s.id}_filed.do`) });
}
