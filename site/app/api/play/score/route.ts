// Energy Research Warehouse (ERW) site: POST /api/play/score, the home battery game's leaderboard (session 38).
// Body: {"level": "YYYY-MM-DD", "actions": [...], "nickname": "optional"}. The score is recomputed from the actions on
// the level's real prices (lib/game.ts), never taken from the client. Writes one row to game_scores: the level, the
// nickname (letters and digits, 3 to 16, or none), the score, the perfect-foresight score and the time. No email, no
// account, no IP. Answers with the level's best ten. Header x-erw-check: 1 marks the ERW's own scripted checks.
import { NextResponse } from "next/server";
import { validNickname } from "@/lib/battery";
import { allow, clientIp, fail, leaderboard, scorePlay, type PlayBody } from "@/lib/game";
import { insertRow } from "@/lib/supabase";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  if (!allow(clientIp(req))) return fail("limit reached: 30 game requests per hour; try again later", 429);
  let body: PlayBody & { nickname?: unknown };  // session 66: with the add-ons (Hard only), which the preset carries
  try {
    body = await req.json();
  } catch {
    return fail("send JSON: {\"level\": \"YYYY-MM-DD\", \"actions\": [...], \"nickname\": \"...\"}");
  }
  let nickname: string | null = null;
  if (body.nickname !== undefined && body.nickname !== null && body.nickname !== "") {
    if (typeof body.nickname !== "string" || !validNickname(body.nickname)) {
      return fail("nickname: 3 to 16 letters and digits, and not one the block list stops");
    }
    nickname = body.nickname;
  }
  const s = await scorePlay(body);
  if (typeof s === "string") return fail(s);
  try {
    await insertRow("game_scores", {
      level_date: s.level.date, nickname, score: s.score, optimal_score: s.optimal, check: req.headers.get("x-erw-check") === "1",
      preset: s.preset, difficulty: s.difficulty,  // session 50: ranked only against plays under the same rules
    });
  } catch (e) {
    console.error(`[erw] play/score: ${(e as Error).message}`);
    return fail("the score could not be stored; try again", 502);
  }
  let top: Awaited<ReturnType<typeof leaderboard>> = [];
  try {
    top = await leaderboard(s.level.date, 0, s.preset);
  } catch (e) {
    console.error(`[erw] play/score leaderboard: ${(e as Error).message}`);
  }
  return NextResponse.json({ score: s.score, optimal: s.optimal, level: s.level.date, preset: s.preset, top });
}
