// Energy Research Warehouse (ERW) site: POST /api/subscribe, the /subscribe form (session 19).
// Adds one address to the Supabase table subscribers with the anon key (insert-only, migration
// 005: the key cannot read the table back). Stores the address, the emails and topics chosen, and the time.
// Session 23: double opt-in. The row is stored unconfirmed and the address gets a confirmation email with a
// signed link (lib/emailtoken.ts); nothing is sent to it until it follows the link (/api/subscribe/confirm).
// Answers with a redirect to /subscribe, which says what happened.
import { NextResponse } from "next/server";
import { emailToken } from "@/lib/emailtoken";
import { insertRow } from "@/lib/supabase";
import { TOPICS, TOPIC_IDS } from "@/lib/topics";

export const runtime = "nodejs";

// the same test as the table's check constraint (warehouse/supabase/migrations/005_subscribers.sql)
const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

async function sendConfirmation(email: string, origin: string, daily: boolean, weekly: boolean, topics: string[]): Promise<boolean> {
  const key = process.env.RESEND_API_KEY, token = emailToken(email, "confirm");
  if (!key || !token) {
    console.error(`[erw] subscribe: confirmation not sent (${!key ? "RESEND_API_KEY" : "EMAIL_TOKEN_SECRET"} not set)`);
    return false;
  }
  const site = (process.env.SITE_URL || origin).replace(/\/$/, "");
  const link = `${site}/api/subscribe/confirm?e=${encodeURIComponent(email)}&t=${token}`;
  const what = [daily ? "ERW's weekday Energy Digest" : "", weekly ? "ERW's Sunday Roundup" : ""].filter(Boolean).join(" and ");
  const labels = TOPICS.filter((t) => topics.includes(t.id)).map((t) => t.label).join(", ");
  const text = `Confirm your ERW email subscription\n\nSomeone, probably you, asked to receive ${what} from the Energy Research Warehouse (ERW) at this address, with the top stories filtered to: ${labels}.\n\nConfirm: ${link}\n\nIf you did not ask for this, ignore this email: nothing will be sent until the link is followed.\n`;
  const html = `<!doctype html><html><body style="margin:0;padding:16px;background:#F7F3EA;color:#2E2D29;font-family:Georgia,serif"><div style="max-width:560px;margin:0 auto"><h1 style="font-size:20px">Confirm your ERW email subscription</h1><p style="font-family:system-ui,sans-serif;font-size:14px">Someone, probably you, asked to receive ${what} from the Energy Research Warehouse (ERW) at this address, with the top stories filtered to: ${labels}.</p><p style="font-family:system-ui,sans-serif;font-size:14px"><a href="${link}">Confirm the subscription</a></p><p style="font-family:system-ui,sans-serif;font-size:12px;color:#6B665E">If you did not ask for this, ignore this email: nothing will be sent until the link is followed.</p></div></body></html>`;
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from: process.env.DIGEST_FROM || "ERW Energy Digest <onboarding@resend.dev>", to: [email], subject: "Confirm your ERW email subscription", text, html }),
    cache: "no-store",
  });
  if (!res.ok) {
    console.error(`[erw] subscribe: Resend HTTP ${res.status} ${(await res.text()).slice(0, 200)}`);
    return false;
  }
  return true;
}

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
  // session 21, ruling 7: separate opt-ins for the daily digest and the Roundup (column weekly), either or both (migration 006)
  const daily = form.get("daily") === "on", weekly = form.get("weekly") === "on";
  if (!daily && !weekly) return back("none");
  // session 23: the topics the email's top stories are filtered to (migration 007); at least one
  const topics = form.getAll("topic").map(String).filter((t) => TOPIC_IDS.includes(t));
  if (topics.length === 0) return back("notopic");
  try {
    await insertRow("subscribers", { email, source: "site", daily, weekly, topics });
  } catch (e) {
    console.error(`[erw] subscribe: ${(e as Error).message}`);
    return back("error");
  }
  const sent = await sendConfirmation(email, new URL(req.url).origin, daily, weekly, topics);
  return back(sent ? "check" : "unsent");
}
