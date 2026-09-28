// Energy Research Warehouse (ERW) site: GET /api/subscribe/confirm?e=<address>&t=<token> (session 23), the link in
// the confirmation email. The database checks the signed token (subscribe_confirm, migration 007) and marks the
// address confirmed; only then does the sender include it. Redirects to /subscribe with the outcome.
import { NextResponse } from "next/server";
import { rpc } from "@/lib/supabase";

export const runtime = "nodejs";

export async function GET(req: Request) {
  const u = new URL(req.url);
  const back = (state: string) => NextResponse.redirect(new URL(`/subscribe?state=${state}`, req.url), 303);
  const email = u.searchParams.get("e") ?? "", token = u.searchParams.get("t") ?? "";
  if (!email || !/^[0-9a-f]{64}$/.test(token)) return back("badlink");
  try {
    return back((await rpc<boolean>("subscribe_confirm", { p_email: email, p_token: token })) ? "confirmed" : "badlink");
  } catch (e) {
    console.error(`[erw] confirm: ${(e as Error).message}`);
    return back("error");
  }
}
