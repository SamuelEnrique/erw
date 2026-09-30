# SESSION 38: The home battery game, MVP

## Read first
CLAUDE.md, archive/sessions/SESSION_37_REPORT.md, iso_rtm_hub_prices (ERCOT HB_HUBAVG,
15-minute), ercot_all_hub_prices_history, storage_daily_cycle, the site's layout and
palette, the Supabase migrations folder.

## Budget and rules
- Expected Anthropic API spend: USD 0. Hard cap: USD 0. No model calls.
- No pulls. No new heavy dependencies: one canvas, plain React, no game engine.
- Supabase: one new small table for scores; nothing else.
- The daily job may land: pull and merge before pushing, never force push.
- Real prices only. The battery, the home and the brand are fictional and labeled so.

## The game
Route /play/battery (nav: a new "Play" entry). One screen, works with mouse and touch.
1. The level: the latest complete ERCOT operating day of HB_HUBAVG real-time prices,
   96 fifteen-minute intervals, scrolling left to right over about 90 seconds. Everyone
   gets the same level that day. A picker also offers five famous days from the
   history table: 2021-02-15, 2023-08-10, a calm spring day, a solar-heavy day, and a
   negative-price day (choose them from the table and state the choice in the report).
2. The player owns one Texas home battery, labeled as an assumption: 13.5 kWh usable,
   5 kW, 90 percent round trip, starts half full. Hold to charge (buy at the interval's
   price), release to discharge (sell), idle otherwise. State of charge bar, cash ticker.
3. One VPP call per level: at the day's highest-price hour, a banner calls the fleet;
   if the player's battery discharges during that hour the fleet map lights up and a
   bonus equal to the energy delivered at that hour's price is paid. Label the bonus
   rule as a game rule, not a real program's terms.
4. Score: dollars earned, and "your fleet": the same result times 10,000 homes. At the
   end, the perfect-foresight score for that day computed by dynamic programming over
   the 96 intervals with the same battery (so the player sees how close they came),
   and a one-paragraph plain-language debrief: when prices peaked, what a battery
   would have done, and a link to /storage and /grid/ercot.
5. Leaderboard: optional nickname (letters and digits, 3 to 16, a small block list),
   no email, no account. Supabase table `game_scores` (level date, nickname, score,
   optimal score, ts) written through a server route with a per-IP rate limit. A short
   notice: scores are public, nothing else is stored.
6. Stanford palette, readable at 380 px, 60 fps on a laptop, no sound.

## Research hooks, stored but not shown
Each finished play also writes its 96 actions and final score to `game_plays` with a
random session id, no IP, no nickname join. State that in the notice. This is the
data for a later dispatch-decision paper.

## Verify and ship
The DP optimum verified against a brute-force check on a 12-interval toy day in a
test; a test that the level uses real rows; check-routes covers /play/battery;
tests/, deploy, live check, and one scripted play through the server route.

## Do not
No pulls, no model calls, no accounts, no emails, no third-party trackers, no force
push.

## Report: archive/sessions/SESSION_38_REPORT.md
What the game does, the five famous days chosen and why, the optimal score for today's
level, the tables added, the privacy notice text, decisions made without a human, open
questions, wall time, spend USD 0 confirmed. Commit after every working step. Push.

## Chain
When the report is written and pushed, read SESSION_39_PROMPT.md and execute it. If it
is absent, stop.