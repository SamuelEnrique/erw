// Energy Research Warehouse (ERW) site, session 128: the ceilings of the question-answering tools.
//
// Before a question is sent to a model, the route asks admit(). It answers yes, or a plain message and the reason:
//
//   month, day   the tool's spend this month, or today, has reached its ceiling (site_api_calls, counted by the
//                database; ceilings from limits.json or the environment). The tool answers again when the month or the
//                day turns over (UTC).
//   visitor      this visitor has asked the day's number of questions.
//   closed       the tool cannot count (no ceilings, no secret for the visitor's hash, the database did not answer, a
//                call in the ledger has no price): it answers no one. It fails closed, never open.
//
// In none of these cases is a model called. The check is one call of the database's site_ask_admit (migration 023),
// which counts the visitor's question as it admits it.
//
// THE VISITOR. No address is stored anywhere. The server makes a keyed hash of the visitor's address, the UTC day and
// a secret it alone holds (ASK_VISITOR_SALT), and the database keeps that hash with a count, for today only. The hash
// cannot be turned back into an address without the secret, and it is another value tomorrow, so a visitor is not
// followed from one day to the next. A visitor is an address: people behind one address share a count.
//
// WHAT A CEILING IS NOT. It is checked before a question, not during one. Questions already being answered when the
// ceiling is reached finish, so a day can end above its ceiling by the cost of the questions in flight. One question
// is bounded by the loop's own limits (lib/chat/spec.json: its tool calls and its tokens).
//
// Pure functions and an injected database call, so the tests run them without a server.
import { createHmac } from "node:crypto";
import file from "./limits.json";

export type Limits = { daily_usd: number; monthly_usd: number; per_visitor_per_day: number };
export type Reason = "month" | "day" | "visitor" | "closed";
export type Admitted = { ok: true } | { ok: false; reason: Reason; why: string; status: number; message: string };
export type AdmitCall = (args: { p_visitor: string; p_per_visitor: number; p_day_usd: number; p_month_usd: number }) => Promise<{ ok?: boolean; reason?: string | null }>;

const num = (v: unknown): number | null => {
  if (typeof v === "number") return Number.isFinite(v) && v >= 0 ? v : null;
  if (typeof v === "string" && /^\d+(\.\d+)?$/.test(v.trim())) return Number(v.trim());
  return null;
};

/** The ceilings: the environment's value where it is set, else the file's. null when any of the three is missing or is
 * not a number: the tool is then closed. A ceiling of 0 is a number: it admits nothing. */
export function readLimits(env: Record<string, string | undefined> = process.env, conf: Record<string, unknown> = file): Limits | null {
  const pick = (name: string, key: string) => (env[name] !== undefined && env[name] !== "" ? num(env[name]) : num(conf[key]));
  const daily = pick("ASK_DAILY_USD", "daily_usd"), monthly = pick("ASK_MONTHLY_USD", "monthly_usd"), per = pick("ASK_PER_VISITOR_PER_DAY", "per_visitor_per_day");
  if (daily === null || monthly === null || per === null || !Number.isInteger(per)) return null;
  return { daily_usd: daily, monthly_usd: monthly, per_visitor_per_day: per };
}

/** The secret of the visitor's hash, or null when it is not set or is too short to be one. */
export function readSalt(env: Record<string, string | undefined> = process.env): string | null {
  const s = (env.ASK_VISITOR_SALT ?? "").trim();
  return s.length >= 24 ? s : null;
}

/** The UTC day of an instant, "2026-10-06". */
export const utcDay = (now: number) => new Date(now).toISOString().slice(0, 10);

/** The visitor's key for one day: 32 hexadecimal characters of HMAC-SHA256(secret, day and address). */
export function visitorKey(ip: string, day: string, salt: string): string {
  return createHmac("sha256", salt).update(`${day}\n${ip}`).digest("hex").slice(0, 32);
}

export function message(reason: Reason, limits: Limits | null): string {
  if (reason === "day") return "This tool has reached its spending limit for today, so it is not answering questions until tomorrow (UTC). Your question was not sent to the model.";
  if (reason === "month") return "This tool has reached its spending limit for the month, so it is not answering questions until next month. Your question was not sent to the model.";
  if (reason === "visitor") return `You have reached today's limit of ${limits?.per_visitor_per_day ?? 0} questions. It starts again at midnight UTC. Your question was not sent to the model.`;
  return "This tool is not answering questions right now. Your question was not sent to the model.";
}

const refuse = (reason: Reason, why: string, limits: Limits | null): Admitted => ({ ok: false, reason, why, status: reason === "visitor" ? 429 : 503, message: message(reason, limits) });

/** May this question go to a model? One database call; any failure, and any answer that is not a plain yes, is a no. */
export async function admit(ip: string, now: number, limits: Limits | null, salt: string | null, call: AdmitCall): Promise<Admitted> {
  if (!limits) return refuse("closed", "no ceilings in the configuration", limits);
  if (!salt) return refuse("closed", "ASK_VISITOR_SALT is not set, or is shorter than 24 characters", limits);
  if (!ip || ip === "unknown") return refuse("closed", "the visitor's address is not known, so its questions cannot be counted", limits);
  let r: { ok?: boolean; reason?: string | null };
  try {
    r = await call({ p_visitor: visitorKey(ip, utcDay(now), salt), p_per_visitor: limits.per_visitor_per_day, p_day_usd: limits.daily_usd, p_month_usd: limits.monthly_usd });
  } catch (e) {
    return refuse("closed", `the database did not answer: ${(e as Error).message}`.slice(0, 200), limits);
  }
  if (r && r.ok === true) return { ok: true };
  const reason = r?.reason;
  if (reason === "day" || reason === "month" || reason === "visitor") return refuse(reason, `site_ask_admit: ${reason}`, limits);
  return refuse("closed", `site_ask_admit: ${reason ?? "no answer"}`, limits);
}

/** A question's identifier in the ledger: 32 hexadecimal characters drawn at random, made from nothing about the visitor. */
export function questionId(): string {
  return crypto.randomUUID().replace(/-/g, "");
}
