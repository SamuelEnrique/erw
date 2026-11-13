// Energy Research Warehouse (ERW) site: GET /api/subscribe/confirm?e=<address>&t=<token> (session 23), the link in
// the confirmation email. The database checks the signed token (subscribe_confirm, migration 007) and marks the
// address confirmed; only then does the sender include it. Redirects to /subscribe with the outcome.
import { NextResponse } from "next/server";
import { limited } from "@/lib/guard";
import { rpc } from "@/lib/supabase";

export const runtime = "nodejs";

export async function GET(req: Request) {
  const u = new URL(req.url);
  const back = (state: string) => NextResponse.redirect(new URL(`/subscribe?state=${state}`, req.url), 303);
  const email = u.searchParams.get("e") ?? "", token = u.searchParams.get("t") ?? "";
  // session 177: an address is at most 254 characters and has the form the table's own check asks for
  if (!email || email.length > 254 || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || !/^[0-9a-f]{64}$/.test(token)) return back("badlink");
  // session 5102 (docs/reviews/security-faults-2026-11-13.md, row 16): a well-formed link makes the database check a
  // token; 60 an hour from one address, then the page's own "try again in an hour"
  if (!(await limited(req, "confirm", 60, 3600)).ok) return back("busy");
  try {
    return back((await rpc<boolean>("subscribe_confirm", { p_email: email, p_token: token })) ? "confirmed" : "badlink");
  } catch (e) {
    console.error(`[erw] confirm: ${(e as Error).message}`);
    return back("error");
  }
}
