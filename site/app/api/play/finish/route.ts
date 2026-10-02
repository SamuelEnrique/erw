// Energy Research Warehouse (ERW) site: POST /api/play/finish, the end of a home battery game (session 38).
// Body: {"level": "YYYY-MM-DD", "actions": [1, 0, -1, ...], "settings": {...}, "difficulty": "normal"} (session 50:
// settings and difficulty are optional and default to the v1 game; session 66: "addons": ["solar"], optional, Hard only). The server scores the actions on the level's real prices
// (lib/game.ts) and writes the play to game_plays for later research: a random session id, the level, the actions and
// the score. No IP, no nickname, nothing that joins it to a leaderboard row. Answers with the score and the
// perfect-foresight score. Header x-erw-check: 1 marks the ERW's own scripted checks.
import { NextResponse } from "next/server";
import { allow, clientIp, fail, scorePlay, type PlayBody } from "@/lib/game";
import { insertRow } from "@/lib/supabase";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  if (!allow(clientIp(req))) return fail("limit reached: 30 game requests per hour; try again later", 429);
  let body: PlayBody;  // session 66: with the add-ons (Hard only), which the preset carries
  try {
    body = await req.json();
  } catch {
    return fail("send JSON: {\"level\": \"YYYY-MM-DD\", \"actions\": [...]}");
  }
  const s = await scorePlay(body);
  if (typeof s === "string") return fail(s);
  try {
    await insertRow("game_plays", {
      session_id: crypto.randomUUID(), level_date: s.level.date, actions: s.actions, score: s.score,
      check: req.headers.get("x-erw-check") === "1",
      preset: s.preset, difficulty: s.difficulty, settings: s.settings,  // session 50
    });
  } catch (e) {
    console.error(`[erw] play/finish: ${(e as Error).message}`);
    return NextResponse.json({ score: s.score, optimal: s.optimal, cash: s.cash, wear: s.wear, bonus: s.bonus, solar: s.solar, penalty: s.penalty, preset: s.preset, stored: false });
  }
  return NextResponse.json({ score: s.score, optimal: s.optimal, cash: s.cash, wear: s.wear, bonus: s.bonus, solar: s.solar, penalty: s.penalty, preset: s.preset, stored: true });
}
