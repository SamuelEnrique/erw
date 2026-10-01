# SESSION 56: California levels in the battery game

## Read first
site/data/battery_levels.json and warehouse/derived/battery_levels.py,
iso_hub_prices_history (CAISO SP15 real-time), site/lib/battery.ts, lib/game.ts,
the /play/battery page, site/lib/problems.ts (set E, question 4).

## Budget and rules
USD 0, no model calls, no data pulls, no Supabase table. Target about 30 minutes.
Pull and merge if the daily job lands, never force push, commit after each item.

## Items
1. Problem set E, question 4: say the battery's coverage is "at best", because its
   revenue is a perfect-foresight upper bound, as the seller's tab notes say.
2. Two CAISO famous days in battery_levels.py, from iso_hub_prices_history (SP15
   real-time, complete days only, every interval present), with the selection rule
   stated in the file and on the page: the day with the lowest midday (10:00 to 15:00
   Pacific) mean price, and the day with the largest rise from the 12:00 to 15:00 mean
   to the 18:00 to 21:00 mean. Label each "CAISO SP15" and its rule. The picker groups
   levels by grid; the debrief names the grid and links /grid/caiso; the leaderboard,
   DP and server rescoring work per level as they do now.
3. A test that the two days' prices equal their table rows and each day is complete;
   check-routes; tests/; deploy; live check and one scripted play on each new level.

## Report: archive/sessions/SESSION_56_REPORT.md
The two days chosen, each with its rule's number, the optimal score on each, wall
time, spend USD 0 confirmed. Push. Stop.