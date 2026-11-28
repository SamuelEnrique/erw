// Energy Research Warehouse (ERW) site: /api/subscribe/confirm?e=<address>&t=<token> (session 23), the link in the
// confirmation email. The database checks the signed token (subscribe_confirm, migration 007) and marks the address
// confirmed; only then does the sender include it. Redirects to /subscribe with the outcome.
//
// wip/ready-subscribe-confirm (the small pages audit of 26 November, finding 4, for Samuel's ruling): a GET no longer
// confirms, as session 59 did for the unsubscribe link, so a mail scanner or link prefetcher that follows the link cannot
// confirm an address that never asked. Now:
//   GET   (a click, or a scanner)       redirects to /subscribe?confirmsub=1, which asks; nothing changes
//   POST  from that page's button       (form field confirm=yes) confirms, then shows the result
// Any other POST changes nothing.
import { NextResponse } from "next/server";
import { limited, sameOrigin } from "@/lib/guard";
import { rpc } from "@/lib/supabase";

export const runtime = "nodejs";

export async function GET(req: Request) {
  const u = new URL(req.url);
  const q = new URLSearchParams({ confirmsub: "1", e: u.searchParams.get("e") ?? "", t: u.searchParams.get("t") ?? "" });
  return NextResponse.redirect(new URL(`/subscribe?${q}`, req.url), 303);
}

export async function POST(req: Request) {
  const back = (state: string) => NextResponse.redirect(new URL(`/subscribe?state=${state}`, req.url), 303);
  if (!sameOrigin(req)) return back("badlink");   // the button posts from this site's own page
  const body = await req.text();
  if (body.length > 4000) return new NextResponse("nothing changed: the request is too large", { status: 413 });   // session 177
  const form = new URLSearchParams(body);
  if (form.get("confirm") !== "yes") return new NextResponse("nothing changed: confirm on the page the link opens", { status: 400 });
  const email = form.get("e") ?? "", token = form.get("t") ?? "";
  // session 177: an address is at most 254 characters and has the form the table's own check asks for
  if (!email || email.length > 254 || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || !/^[0-9a-f]{64}$/.test(token)) return back("badlink");
  // session 5102 (docs/reviews/security-faults-2026-11-13.md, row 16): a well-formed request makes the database check a
  // token; 60 an hour from one address, then the page's own "try again in an hour"
  if (!(await limited(req, "confirm", 60, 3600)).ok) return back("busy");
  try {
    return back((await rpc<boolean>("subscribe_confirm", { p_email: email, p_token: token })) ? "confirmed" : "badlink");
  } catch (e) {
    console.error(`[erw] confirm: ${(e as Error).message}`);
    return back("error");
  }
}
