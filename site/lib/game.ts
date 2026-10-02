// Session 38: the home battery game's server side, shared by /api/play/finish and /api/play/score. Every score is
// recomputed here from the posted actions and the level's real prices (lib/levels.ts), so no client can post a score
// its actions did not earn. The rate limit is per server instance's memory, as /api/ask's: a floor, not a guarantee.
import { NextResponse } from "next/server";
import {
  ADDONS, DEFAULT_SETTINGS, optimum, presetOf, rulesOf, simulate, validActions, validAddons, validDifficulty, validSettings, validSolar,
  type Action, type AddonKey, type Difficulty, type Settings,
} from "@/lib/battery";
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

/** Session 55: the leaderboard's read route (GET /api/play/top) has its own, larger floor: the pick screen reloads the
 * board as the player changes the settings, which should not use up the 30 plays an hour. */
const READ_LIMIT = 240;
const seenRead = new Map<string, number[]>();
export function allowRead(ip: string, now = Date.now()): boolean {
  const recent = (seenRead.get(ip) ?? []).filter((t) => now - t < WINDOW_MS);
  if (recent.length >= READ_LIMIT) {
    seenRead.set(ip, recent);
    return false;
  }
  recent.push(now);
  seenRead.set(ip, recent);
  return true;
}

export const fail = (error: string, status = 400) => NextResponse.json({ error }, { status });

export type Scored = {
  level: Level; actions: Action[]; score: number; optimal: number; cash: number; wear: number; bonus: number;
  settings: Settings; difficulty: Difficulty; preset: string;
  addons: AddonKey[]; solar: number; penalty: number;  // session 66: the add-ons on, the roof's sales and the lights-out penalty, USD
};
export type PlayBody = { level?: unknown; actions?: unknown; settings?: unknown; difficulty?: unknown; addons?: unknown };

/** Session 66: a play scored on a level already found: lib/battery.ts's own simulate and optimum under the posted
 * settings, difficulty and add-ons (the page's scorer, so the two cannot differ), or a sentence saying what is wrong.
 * An add-on that needs something the level does not hold (rooftop solar: the day's solar shape) is refused: nothing
 * is filled. */
export function scoreOn(level: Level, body: PlayBody): Scored | string {
  if (!validActions(body.actions, level.price.length)) return `actions: ${level.price.length} values, each 1, 0 or -1`;
  const settings = body.settings === undefined ? DEFAULT_SETTINGS : body.settings;
  if (!validSettings(settings)) return "settings: kwh, kw, rte, reserve and deg, each a number within its range and on its step (lib/battery.ts SETTINGS)";
  const difficulty = body.difficulty === undefined ? "normal" : body.difficulty;
  if (!validDifficulty(difficulty)) return "difficulty: easy, normal or hard";
  const addons = body.addons === undefined ? [] : body.addons;
  if (!validAddons(addons, difficulty)) return `addons: a list of ${Object.keys(ADDONS).join(", ")}, each once, and only on Hard`;
  if (addons.includes("solar") && !validSolar(level.solar, level.price.length)) return `addons: rooftop solar is not available for ${level.date}: the warehouse holds no solar shape for that day`;
  const rules = rulesOf(settings, difficulty, addons);
  const sun = rules.solarKw > 0 ? level.solar : undefined;
  const r = simulate(level.price, body.actions, rules, sun);
  const o = optimum(level.price, rules, sun);
  const c = (v: number) => Math.round(v * 10_000) / 10_000;
  return {
    level, actions: body.actions, score: c(r.score), optimal: c(o.score), cash: c(r.cash), wear: c(r.wear), bonus: c(r.bonus),
    settings, difficulty, preset: presetOf(settings, difficulty, addons), addons, solar: c(r.solar), penalty: c(r.penalty),
  };
}

/** A posted play, checked and scored: the level must be a famous day or a recent complete day, and the actions one per
 * interval of it. Session 50: the battery's settings and the difficulty (both optional: a v1 play is Normal with the
 * default battery) must be within lib/battery.ts's ranges; the score and the optimum are recomputed under them. */
export async function scorePlay(body: PlayBody): Promise<Scored | string> {
  if (typeof body.level !== "string") return "level is required (the operating day, YYYY-MM-DD)";
  const level = await levelFor(body.level);
  if (!level) return `no level for ${body.level}`;
  return scoreOn(level, body);
}

export type ScoreRow = { nickname: string | null; score: number; optimal_score: number; ts: string; preset: string };

/** The leaderboard of one level and one preset (session 50: plays are ranked only against plays under the same rules):
 * the best ten scores, the ERW's own checks left out. */
export async function leaderboard(date: string, revalidate = 60, preset = presetOf(DEFAULT_SETTINGS, "normal")): Promise<ScoreRow[]> {
  const rows = await rest<ScoreRow>("game_scores", {
    select: "nickname,score,optimal_score,ts,preset", level_date: `eq.${date}`, preset: `eq.${preset}`, check: "is.false", order: "score.desc,ts.asc",
  }, revalidate, 10);
  return rows.map((r) => ({ ...r, score: Number(r.score), optimal_score: Number(r.optimal_score) }));
}

export type PresetCount = { preset: string; n: number; best: number };

/** Session 50: every preset played on a level, with its number of scores and its best, for the leaderboard's list. */
export async function presetsPlayed(date: string, revalidate = 60): Promise<PresetCount[]> {
  const rows = await rest<{ preset: string; score: number }>("game_scores", {
    select: "preset,score", level_date: `eq.${date}`, check: "is.false", order: "score.desc",
  }, revalidate, 1000);
  const by = new Map<string, PresetCount>();
  for (const r of rows) {
    const x = by.get(r.preset) ?? { preset: r.preset, n: 0, best: Number(r.score) };
    x.n++;
    by.set(r.preset, x);
  }
  return [...by.values()].sort((a, b) => b.n - a.n);
}
