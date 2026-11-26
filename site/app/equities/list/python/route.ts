// Session 10402 (chain 720, part D): a Python reader of the list of companies (/equities/list), with the address of the
// rows on the site that serves it (lib/csvreader.ts). Under /equities, so the release gate covers it.
import { csvReader } from "@/lib/csvreader";
import { LIST_SPEC, attach } from "../../reader";

export const dynamic = "force-dynamic";

export function GET(req: Request) {
  return new Response(csvReader("py", new URL("/equities/list", req.url).toString(), LIST_SPEC), { headers: attach("erw_equities_companies.py") });
}
