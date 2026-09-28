// Energy Research Warehouse (ERW) site: the signed token of a confirmation or unsubscribe link (session 23).
// HMAC-SHA256 of lower(email) + ":" + purpose with EMAIL_TOKEN_SECRET, in hex: the same token the database checks
// (warehouse/supabase/migrations/007_subscriber_confirm.sql) and the sender writes (warehouse/news/email_digest.py).
// Server-only: the secret never reaches the browser.
import "server-only";
import { createHmac } from "node:crypto";

export function emailToken(email: string, purpose: "confirm" | "unsubscribe"): string | null {
  const secret = process.env.EMAIL_TOKEN_SECRET;
  if (!secret) return null;
  return createHmac("sha256", secret).update(`${email.trim().toLowerCase()}:${purpose}`).digest("hex");
}
