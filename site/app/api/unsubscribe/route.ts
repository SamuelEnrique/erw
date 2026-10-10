// Energy Research Warehouse (ERW) site: /api/unsubscribe?e=<address>&t=<token> (session 23), the link in every
// email. The database checks the signed token (subscribe_unsubscribe, migration 007), marks the address unsubscribed and
// adds it to the suppression list, which the sender also applies to fixed recipients.
//
// Session 58/59: a GET no longer unsubscribes. On 2026-09-29 00:32 UTC the digest's only fixed recipient was unsubscribed
// about forty minutes after the digest was sent, by its own link: the token exists only inside a sent email, and no test or
// script calls this route, so the likeliest cause is a mail scanner or link prefetcher following the link (a GET). Now:
//   GET   (a click, or a scanner)       redirects to /subscribe?confirm=1, which asks; nothing changes
//   POST  from that page's button       (form field confirm=yes) unsubscribes, then shows the result
//   POST  RFC 8058 one-click            (body List-Unsubscribe=One-Click, a mail client's button) unsubscribes
// Any other POST changes nothing.
import { NextResponse } from "next/server";
import { rpc } from "@/lib/supabase";

export const runtime = "nodejs";

async function run(email: string, token: string): Promise<string> {
  // session 177: an address is at most 254 characters and has the form the table's own check asks for
  if (!email || email.length > 254 || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || !/^[0-9a-f]{64}$/.test(token)) return "badlink";
  try {
    return (await rpc<boolean>("subscribe_unsubscribe", { p_email: email, p_token: token })) ? "unsubscribed" : "badlink";
  } catch (e) {
    console.error(`[erw] unsubscribe: ${(e as Error).message}`);
    return "error";
  }
}

export async function GET(req: Request) {
  const u = new URL(req.url);
  const q = new URLSearchParams({ confirm: "1", e: u.searchParams.get("e") ?? "", t: u.searchParams.get("t") ?? "" });
  return NextResponse.redirect(new URL(`/subscribe?${q}`, req.url), 303);
}

export async function POST(req: Request) {
  const u = new URL(req.url);
  const body = await req.text();
  if (body.length > 4000) return new NextResponse("nothing changed: the request is too large", { status: 413 });   // session 177
  const form = new URLSearchParams(body);
  const email = u.searchParams.get("e") ?? form.get("e") ?? "", token = u.searchParams.get("t") ?? form.get("t") ?? "";
  if (form.get("List-Unsubscribe") === "One-Click") {
    const state = await run(email, token);  // RFC 8058: the mail client's own unsubscribe button
    return new NextResponse(state, { status: state === "unsubscribed" ? 200 : 400 });
  }
  if (form.get("confirm") === "yes") {
    return NextResponse.redirect(new URL(`/subscribe?state=${await run(email, token)}`, req.url), 303);
  }
  return new NextResponse("nothing changed: confirm on the page the link opens", { status: 400 });
}
