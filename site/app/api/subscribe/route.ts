// Energy Research Warehouse (ERW) site: POST /api/subscribe, the /subscribe form (session 19).
// Adds one address to the Supabase table subscribers with the anon key (insert-only, migration
// 005: the key cannot read the table back). Stores the address and the time, nothing else.
// Answers with a redirect to /subscribe, which says what happened.
import { NextResponse } from "next/server";
import { insertRow } from "@/lib/supabase";

export const runtime = "nodejs";

// the same test as the table's check constraint (warehouse/supabase/migrations/005_subscribers.sql)
const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

export async function POST(req: Request) {
  const back = (state: string) => NextResponse.redirect(new URL(`/subscribe?state=${state}`, req.url), 303);
  let form: FormData;
  try {
    form = await req.formData();
  } catch {
    return back("invalid");
  }
  // a field people do not see; a form that fills it is a bot, and nothing is stored
  if (String(form.get("website") ?? "") !== "") return back("done");
  const email = String(form.get("email") ?? "").trim();
  if (email.length < 3 || email.length > 254 || !EMAIL.test(email)) return back("invalid");
  try {
    await insertRow("subscribers", { email, source: "site" });
  } catch (e) {
    console.error(`[erw] subscribe: ${(e as Error).message}`);
    return back("error");
  }
  return back("done");
}
