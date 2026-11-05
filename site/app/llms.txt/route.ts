// Energy Research Warehouse (ERW) site, session 1011 (chain 070): /llms.txt, the briefing for AI readers, the same text
// as package/llms.txt (copied at build by scripts/build-content.mjs into content/llms.json; tests/test_session1011.py).
// A path with a file's ending passes the release gate's curtain (proxy.ts), so this route keeps the review itself: while
// every page is in review, it answers the internal view only, until the owner opens the site or rules on this file.
import llms from "@/content/llms.json";
import { COOKIE, cookieOpens } from "@/lib/release";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const cookie = (req.headers.get("cookie") ?? "").split(/;\s*/).find((c) => c.startsWith(`${COOKIE}=`))?.slice(COOKIE.length + 1);
  if (!(await cookieOpens(cookie, process.env.INTERNAL_COSTS_TOKEN))) {
    return new Response("in review\n", { status: 404, headers: { "Content-Type": "text/plain; charset=utf-8", "X-Robots-Tag": "noindex" } });
  }
  return new Response((llms as { text: string }).text, { headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "private, no-store" } });
}
