// Energy Research Warehouse (ERW) site: /api/unsubscribe?e=<address>&t=<token> (session 23), the link in every
// email. GET (a click) and POST (a mail client's one-click unsubscribe, RFC 8058, from the List-Unsubscribe
// header) both work. The database checks the signed token (subscribe_unsubscribe, migration 007), marks the
// address unsubscribed and adds it to the suppression list, which the sender also applies to fixed recipients.
import { NextResponse } from "next/server";
import { rpc } from "@/lib/supabase";

export const runtime = "nodejs";

async function run(req: Request): Promise<string> {
  const u = new URL(req.url);
  const email = u.searchParams.get("e") ?? "", token = u.searchParams.get("t") ?? "";
  if (!email || !/^[0-9a-f]{64}$/.test(token)) return "badlink";
  try {
    return (await rpc<boolean>("subscribe_unsubscribe", { p_email: email, p_token: token })) ? "unsubscribed" : "badlink";
  } catch (e) {
    console.error(`[erw] unsubscribe: ${(e as Error).message}`);
    return "error";
  }
}

export async function GET(req: Request) {
  return NextResponse.redirect(new URL(`/subscribe?state=${await run(req)}`, req.url), 303);
}

export async function POST(req: Request) {
  const state = await run(req);
  return new NextResponse(state, { status: state === "unsubscribed" ? 200 : 400 });
}
