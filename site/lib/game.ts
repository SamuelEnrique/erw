// Session 38: the home battery game's server side, shared by /api/play/finish and /api/play/score. Every score is
// recomputed here from the posted actions and the level's real prices (lib/levels.ts), so no client can post a score
// its actions did not earn. The rate limit is per server instance's memory, as /api/ask's: a floor, not a guarantee.
import { NextResponse } from "next/server";
import { optimum, simulate, validActions, type Action } from "@/lib/battery";
import { levelFor, type Level } from "@/lib/levels";
import { rest } from "@/lib/supabase";

const LIMIT = 30;
const WINDOW_MS = 3_600_000;
const seen = new Map<string, number[]>();

export function clientIp(req: Request): string {
  const fwd = req.headers.get("x-forwarded-for");
  if (fwd) return fwd.split(",")[0].trim();
  return req.headers.get("x-real-ip") ?? "unknown";
}

/** false when this IP has made LIMIT game requests in the last hour (the IP lives only in this memory). */
export function allow(ip: string, now = Date.now()): boolean {
  const recent = (seen.get(ip) ?? []).filter((t) => now - t < WINDOW_MS);
  if (recent.length >= LIMIT) {
    seen.set(ip, recent);
    return false;
  }
  recent.push(now);
  seen.set(ip, recent);
  return true;
}

export const fail = (error: string, status = 400) => NextResponse.json({ error }, { status });

export type Scored = { level: Level; actions: Action[]; score: number; optimal: number; cash: number; bonus: number };

/** A posted play, checked and scored: the level must be a famous day or a recent complete day, and the actions one per
 * interval of it. */
export async function scorePlay(body: { level?: unknown; actions?: unknown }): Promise<Scored | string> {
  if (typeof body.level !== "string") return "level is required (the operating day, YYYY-MM-DD)";
  const level = await levelFor(body.level);
  if (!level) return `no level for ${body.level}`;
  if (!validActions(body.actions, level.price.length)) return `actions: ${level.price.length} values, each 1, 0 or -1`;
  const r = simulate(level.price, body.actions);
  const o = optimum(level.price);
  const c = (v: number) => Math.round(v * 10_000) / 10_000;
  return { level, actions: body.actions, score: c(r.score), optimal: c(o.score), cash: c(r.cash), bonus: c(r.bonus) };
}

export type ScoreRow = { nickname: string | null; score: number; optimal_score: number; ts: string };

/** The leaderboard of one level: the best ten scores, the ERW's own checks left out. */
export async function leaderboard(date: string, revalidate = 60): Promise<ScoreRow[]> {
  const rows = await rest<ScoreRow>("game_scores", {
    select: "nickname,score,optimal_score,ts", level_date: `eq.${date}`, check: "is.false", order: "score.desc,ts.asc",
  }, revalidate, 10);
  return rows.map((r) => ({ ...r, score: Number(r.score), optimal_score: Number(r.optimal_score) }));
}
