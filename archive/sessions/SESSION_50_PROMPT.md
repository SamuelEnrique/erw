# SESSION 50: Battery game v2 (for a battery industry reviewer)

## Read first
CLAUDE.md, archive/sessions/SESSION_38_REPORT.md and SESSION_46_REPORT.md, site/lib/
battery.ts, lib/game.ts, the /play/battery page and components, battery_levels.py,
storage_daily_cycle, storage_capacity, iso_rtm_hub_prices, the Supabase game tables.

## Budget and rules
- Expected Anthropic API spend: USD 0. Hard cap: USD 0. No model calls. No data pulls.
- Supabase is near 394 MB: first, dispatch the weekly-vacuum workflow once (approved)
  and record the size. No new Supabase table; the game tables may get columns.
- Real prices only. Battery specs, the brand and the VPP program are fictional or
  user-set and labeled as such; where a rule mirrors a real program, cite the real
  program's public document and say the game simplifies it.
- Pull and merge if the daily job lands, never force push, commit after every step.

## The work
1. Battery settings panel (defaults labeled as assumptions, all editable within
   stated ranges): usable kWh, continuous kW, round-trip efficiency, a backup reserve
   (percent the battery may not go below, default 20), and a degradation cost per kWh
   cycled (default from a stated, cited public source on battery cost and cycle life,
   or user-set if none is found). The DP optimum, the server rescoring and the
   leaderboard respect the settings; the leaderboard groups scores by settings preset.
2. The VPP event, realistic: read ERCOT's public material on its aggregated
   distributed energy resource (ADER) program and model the game's fleet call on it
   (notice time, event length, what the battery is paid for), citing it and stating
   every simplification. Keep the bonus rule transparent on the page.
3. Difficulty: Easy (prices visible a few hours ahead, a forecast band), Normal (as
   now), Hard (no forecast, reserve enforced, degradation on).
4. A 30-second first-run tutorial (skippable, remembered in browser storage with
   try/catch), and a house-and-battery animation: charge flowing in from the grid,
   discharge flowing out, the reserve line on the battery.
5. The replay: after a game, the perfect battery's day plays back beside the player's,
   with a one-line reason at each switch read from the prices ("charged: cheapest four
   hours of the morning", "held: reserve").
6. Mobile polish at 380 px, and frame time measured in a visible browser window.
7. docs/methods/battery_game.md: every assumption, its source or "assumption", and what
   the game leaves out (tariffs, retail rates, grid fees, real program terms).
8. docs/reviews/henry-questions.md: ten questions for a former Tesla battery engineer,
   each tied to a specific setting or rule in the game, so his answers become design
   decisions.

## Verify and ship
DP optimum against brute force with reserve and degradation; server rescoring under
each preset; check-routes; tests/; deploy; live check and one scripted play per
difficulty.

## Report: archive/sessions/SESSION_50_REPORT.md
What changed and why, every assumption with its source, the ADER reading and the
simplifications, the questions file, Supabase before and after the vacuum, wall time,
spend USD 0 confirmed, open questions. Push.