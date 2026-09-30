# Session 38 report: the home battery game, MVP

Energy Research Warehouse (ERW), session 38, run 2026-09-30 from 09:42 to about 10:40 UTC. **Wall time about 58 minutes;** about 30 of them were a deploy that did not start (below).

**API spend: USD 0.00, confirmed.** No model call. The cost ledger's last row is 05:12 UTC.

- **No pull, no accounts, no emails, no trackers.** The daily job did not land during the session. No force push.
- **Deployed and checked live:**
  - routes 45 of 45;
  - values 1,596 of 1,596;
  - one scripted play through the server routes, which passed.

## What the game does

`/play/battery`, in a new "Play" entry of the nav. One screen, mouse, touch and keys, no sound.

1. **The level:** one real ERCOT operating day of HB_HUBAVG real-time prices, every 15-minute interval (96), scrolling left to right over 90 seconds.
   - **Today's level** is the latest complete operating day in the live set (`iso_rtm_hub_prices`), the same for everyone that day. It is 2026-09-27 as of this run.
   - A **picker** offers five famous days (below).
   - **Future prices are hidden,** as in a real-time market.
   - A server-rendered line states today's range, checked live: 20.41 to 100.29 USD/MWh (rows at 2026-09-27 13:30 and 22:15 UTC).
2. **The battery,** labelled on the page as an assumption and as fictional ("Mockingbird Home Battery" is made up): 13.5 kWh usable, 5 kW, 90 percent round trip (the square root of 0.9 each way), half full at the start.
   - **Hold "charge"** (button, C or the down arrow) to buy at the interval's price. **Hold "discharge"** (button, S or the up arrow) to sell. **Let go** to idle.
   - Each interval's action is the control held for most of its time.
   - A state-of-charge bar and a cash ticker.
3. **The fleet call (a game rule, labelled so):**
   - A banner calls the fleet in the day's highest-price clock hour (the four intervals with the highest mean).
   - If the battery discharges in that hour, the fleet map lights up.
   - The bonus is the energy delivered in that hour times the hour's mean price, never below zero.
4. **The score** is dollars earned, cash plus the bonus, and "your fleet", the same times 10,000 homes. At the end:
   - **The perfect-foresight score:** dynamic programming over the day's intervals with the same battery, rules and bonus. It runs in 11 to 27 ms on a 96-interval day.
   - **The share of it the player made.**
   - **A plain-language debrief** built from the day's rows: when the price peaked and bottomed, when the dearest hour began, and when the optimal battery charged and discharged. It links `/storage` and `/grid/ercot`.
5. **The leaderboard:**
   - an optional nickname (letters and digits, 3 to 16, a small block list); no email, no account;
   - the level's best ten, with each score's share of perfect;
   - **The server recomputes every score** from the posted actions and the level's real prices (`lib/game.ts`), so no client can post a score its moves did not earn;
   - a per-IP rate limit of 30 game requests per hour, per server instance, kept in memory as `/api/ask`'s is.
6. **Palette and layout:** Stanford's palette through the site's tokens: charging in Palo Alto green, selling in cardinal. At 380 px the page has no horizontal overflow and every control fits (checked in a browser, in a 380 px frame).

## The five famous days, and why

**Where they live.** They are frozen in `site/data/battery_levels.json` by `warehouse/derived/battery_levels.py`, because the history table is not in the live set. Every price is a warehouse row, and `tests/test_session38.py` compares each against its table.

| Day | Chosen how | Range, USD/MWh | Perfect foresight |
|---|---|---|---|
| 2021-02-15, Winter Storm Uri | named by the prompt: the first day of rotating outages | 1,403.49 to 9,004.59 | $240.36 |
| 2023-08-10, a summer scarcity day | named by the prompt | 24.90 to 3,842.89 | $60.97 |
| 2026-04-26, a calm spring day | the narrowest range of any complete operating day, March to May 2026 (17.68; 92 days compared) | 16.48 to 34.16 | $0.44 |
| 2026-08-29, a solar-heavy day | the highest solar share of ERCO's net generation, 19.46 percent, of the 32 complete days `eia930_all_generation` holds (2026-08-26 to 09-26) | 14.48 to 58.45 | $0.93 |
| 2025-01-05, a negative-price day | the lowest mean real-time price of any of 4,255 complete days since 2015: -10.6556 | -31.88 to 20.63 | $0.79 |

- **The solar-heavy day's prices** come from `iso_rtm_hub_prices`, because the history ends 2026-08-25. The warehouse holds EIA's fuel mix only for the last month; ERCOT's own solar table holds 9 days.
- **The negative-price day** is a Sunday of January 2025. Its mean is negative although it is not a spring or solar day.

## The optimal score for today's level

**Today's level, 2026-09-27: perfect foresight $1.4994** for one battery, $14,994 for the fleet of 10,000. The scripted play's plain rule (charge the first four hours, sell the last four) scored $0.6161 on it.

## Tables added

**Migration 013 (`warehouse/supabase/migrations/013_game.sql`), applied:**

- **`game_scores`,** the public leaderboard:
  - columns: level_date, nickname (null, or letters and digits 3 to 16, checked in SQL too), score, optimal_score, check, ts;
  - the anon key may insert and read it.
- **`game_plays`,** the research record:
  - columns: a random session id (made on the server), level_date, the actions (one per interval, 1, 0 or -1, 92 to 100 of them), score, check, ts;
  - the anon key may insert only: it cannot read, update or delete;
  - no IP, no nickname, and no column that joins it to `game_scores`.
- **`check`** marks the ERW's own scripted plays (header `x-erw-check: 1`), so they stay off the leaderboard and out of the research data. `game_scores` holds 5 check rows, from the local and live scripted plays. `game_plays` holds 6: those 5, and one from the browser check. That game finished at 09:55:50 UTC and posted without the header (id 4, one move, -0.0363). I set its flag by hand afterwards rather than delete it.
- **Size:** 48 KB and 32 KB. **Supabase stands at 341.7 MB** (341.5 before).

**The two tables and "nothing else".** The prompt allows "one new small table for scores; nothing else", but its research-hooks section requires `game_plays`, so both were made. No other table was added; the famous days are a site data file, not a Supabase table.

## The privacy notice (the text on the page)

> Scores are public. Posting one stores the level, your nickname if you give one, your score, the perfect-foresight score and the time; nothing else, and no email, account or IP address. Each finished game also stores its moves (one per fifteen minutes) and its score with a random id, for later research on how people run batteries: never shown, with no nickname or IP address, and nothing that joins it to a leaderboard row. No trackers, no sound.

## Verify and ship

- **The DP optimum equals brute force** over all 3^12 action sequences on four 12-interval toy days: a trough and a peak, negative prices, a flat day, and a spike in the fleet hour. The DP's own actions, replayed, reproduce its score (`site/scripts/test-battery.mjs`, run by `tests/test_session38.py` with Node 24, which runs `lib/battery.ts` as it is).
- **The levels use real rows:** a test compares every famous day's timestamps and prices with its table, and checks each day has every interval.
- **check-routes and check-values:**
  - check-routes covers `/play/battery`;
  - check-values covers today's price range on the page (two values);
  - `tests/`: 75 of 75.
- **One scripted play through the server route** (`site/scripts/play-battery.mjs`), local and live. The steps:
  - the optimum of 2023-08-10, which the server scored at 60.9710, equal to the optimum;
  - posted with nickname ERWcheck, and left off the leaderboard;
  - today's level with a plain rule;
  - three refusals: a nickname with a space, 2 actions instead of 96, and an unknown level.
- **Browser check:**
  - The game ran in Chrome, and a held key charged the battery (6.75 to 7.94 kWh).
  - **60 fps was not measured.** The automated window does not paint in the background, so `requestAnimationFrame` stalled whenever the tool was not taking a screenshot.
  - A frame's work is one canvas redraw of at most 100 steps. React re-renders once per interval (about once a second), not per frame.
  - The DP runs once, at the end.

**The deploy that did not start.** The push of 41d2b1c got no Vercel deployment and no status for 35 minutes. The live check against the old build failed on `/play/battery` (404). Earlier pushes deployed normally. The next push (c8b622a, a real fix: the price label no longer overlaps the line at 380 px) deployed in about a minute, and every live check then passed.

## Decisions made without a human

1. **"Hold to charge, release to discharge" is two hold controls,** with idle when neither is held. Release alone cannot mean both discharge and idle, and the prompt asks for all three.
2. **An interval's action is the control held for most of it,** so the player's moves are the DP's three actions and a perfect-foresight score is never beaten.
3. **Future prices are hidden;** the chart scales to the prices seen so far.
4. **Round trip as the square root of 0.9 each way.** The score is cash; the energy left in the battery at the end is not valued, for the player and the optimum alike.
5. **The fleet hour** is the clock hour with the highest mean price. The bonus is its mean price times the energy delivered, never below zero, so a negative-price hour cannot charge the player for answering.
6. **The famous days' selection rules** are the table above, stated on the page and in `battery_levels.py`.
7. **Two tables, and a `check` flag** for the ERW's own plays.
8. **The fictional brand** is "Mockingbird Home Battery".

## Open questions

1. **Vercel missed one push's deploy.** If it recurs, a deploy hook or a check in the workflow would catch it.
2. **The rate limit is per instance and in memory,** a floor as `/api/ask`'s is. A table-backed limit would store a hashed IP, which the notice promises not to.
3. **Replayed optimum actions are accepted.** A player who posts the DP's actions tops the leaderboard. The server cannot tell foresight from a replay. Mark scores at 100 percent of perfect?
4. **Famous days from the history only reach 2026-08-25,** and EIA's fuel mix only the last month. A longer solar history would allow a better "solar-heavy" pick.
5. **The research table** needs a stated purpose and a retention rule before any paper uses it.

## Skipped

- Sound, as instructed.
- A frame-rate measurement (above).
