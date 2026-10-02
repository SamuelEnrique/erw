// Energy Research Warehouse (ERW) site: GET /api/play/top?level=YYYY-MM-DD&preset=<preset>, the home battery game's
// leaderboard for one level and one preset (session 55; session 50's open question 2). The pick screen calls it when
// the player changes the difficulty, the battery's settings or the day, so the board shown is the one the play would
// join. Read only: the best ten of game_scores for the level and preset, the ERW's own checks left out (lib/game.ts
// leaderboard). Refuses a level that is not a famous day or a recent complete day, and a preset that lib/battery.ts's
// presetOf does not write (parsePreset), with HTTP 400.
import { NextResponse } from "next/server";
import { parsePreset, presetLabel } from "@/lib/battery";
import { allowRead, clientIp, fail, leaderboard } from "@/lib/game";
import { levelFor } from "@/lib/levels";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  if (!allowRead(clientIp(req))) return fail("limit reached: 240 leaderboard reads per hour; try again later", 429);
  const q = new URL(req.url).searchParams;
  const preset = q.get("preset") ?? "";
  if (!parsePreset(preset)) return fail("preset: not one the game writes (for example normal:13.5-5-90-v3, or hard:13.5-5-90-r20-d0.11-v3)");
  const date = q.get("level") ?? "";
  let level;
  try {
    level = await levelFor(date);
  } catch (e) {
    console.error(`[erw] play/top: ${(e as Error).message}`);
    return fail("the levels could not be read; try again", 502);
  }
  if (!level) return fail(`level: no level for ${date || "(none)"}; a famous day or one of the last ten complete days, YYYY-MM-DD`);
  try {
    const top = await leaderboard(level.date, 60, preset);
    return NextResponse.json({ level: level.date, preset, label: presetLabel(preset), top }, { headers: { "Cache-Control": "public, max-age=30" } });
  } catch (e) {
    console.error(`[erw] play/top: ${(e as Error).message}`);
    return fail("the leaderboard could not be read; try again", 502);
  }
}
