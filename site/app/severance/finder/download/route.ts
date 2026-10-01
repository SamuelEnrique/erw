// Session 57: the refund finder's flags as CSV, internal: 404 without the internal token, as the page
// (/severance/finder). Every lease and rule the finder flagged, with its months, test, base tax, tax with the rule, the
// potential saving and what the flag cannot see (warehouse/derived/severance_screen.py).
import fs from "node:fs";
import zlib from "node:zlib";
import { FLAGS, outDir, tokenOk } from "@/lib/finder";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  if (!tokenOk(new URL(req.url).searchParams.get("token"))) return new Response("Not found", { status: 404 });
  const f = `${outDir()}/${FLAGS}`;
  if (!fs.existsSync(f)) return new Response("The finder's flags are not on this server", { status: 404 });
  return new Response(zlib.gunzipSync(fs.readFileSync(f)), {
    headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": "attachment; filename=\"severance_refund_finder_internal.csv\"", "Cache-Control": "private, no-store", "X-Robots-Tag": "noindex" },
  });
}
