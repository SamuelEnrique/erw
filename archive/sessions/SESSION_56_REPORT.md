# Session 56 report: California levels in the battery game

Energy Research Warehouse (ERW), session 56, run 2026-10-01 from 20:08 to about 20:28 UTC. **Wall time about 20 minutes,** against a 30-minute target.

**API spend: USD 0.00, confirmed.**
- No model call.
- No data pull: the California days were chosen from `iso_hub_prices_history` already on this machine.
- No Supabase table. The scripted plays wrote rows marked as ERW checks (`x-erw-check: 1`) to the existing game tables, as every session since 38 has done.
- No force push. The daily job did not land, so there was nothing to merge.

| Item | Done | Commit |
|---|---|---|
| 1. Set E, question 4 says "at best" | yes | `02434a9` |
| 2. Two CAISO famous days | yes | `8c384f5` |
| 3. Tests, check-routes, deploy, live checks, scripted plays | yes | `5a390d7`, and this report |

## 1. Set E, question 4

The question now asks how many months the battery's cash flow "could at best cover". The live answer reads: "At best, in 26 of 99 months; it fell short in 73 months even with perfect foresight. A real battery, which cannot see the day's prices in advance, earns less and covers fewer."

A step of the worked solution says why, in the seller's tab's words: the battery knows each day's prices in advance, and a real one captures a fraction of this. This answers session 55's open question 3.

## 2. The two California days

**Source:** CAISO SP15 (`TH_SP15_GEN-APND`) real-time prices.
- The values are the 15-minute means of CAISO's 5-minute prices (`lmp_rtm_15m_mean`), from `iso_hub_prices_history`.
- Operating days are in Pacific time.
- Only complete days count: every interval present (96, or 92 or 100 on a clock change). 393 days qualify, 2025-09-01 to 2026-09-29.

| Level | The rule | The day | The rule's number |
|---|---|---|---|
| CAISO SP15: the cheapest midday | the lowest mean price from 10:00 to 15:00 Pacific (the intervals starting 10:00 to 14:45) | **2026-04-27** | a mean of **-22.13 USD/MWh** (-22.1251); the day ran from -36.00 to 23.03 USD/MWh |
| CAISO SP15: the steepest evening ramp | the largest rise from the 12:00 to 15:00 mean to the 18:00 to 21:00 mean | **2026-07-24** | from **53.37** to **462.27 USD/MWh**, a rise of **408.90 USD/MWh** (408.9038); the day peaked at 980.64 USD/MWh |

**The optimal score on each day,** the default battery (13.5 kWh, 5 kW, 90 percent round trip), perfect foresight:

| Day | Normal | Hard (20 percent reserve, USD 0.11 per kWh wear) |
|---|---|---|
| 2026-04-27, the cheapest midday | **USD 0.8267** | USD 0.2450 |
| 2026-07-24, the steepest evening ramp | **USD 12.9806** | USD 10.2451 |

A cheap midday alone pays a battery little: the day's whole spread was under USD 60. The evening ramp pays about 16 times more.

### Where the rules are stated

- **In the builder:** `warehouse/derived/battery_levels.py`, its docstring and the constants `MIDDAY, AFTERNOON, EVENING`.
- **In each level:** the level's `rule` field, and its `why` line with the rule's number.
- **On the page:** in the intro, and on each California card ("The rule: ...").
- **In the method page:** `docs/methods/battery_game.md`, the section "The California days".

### The game

- **The picker** groups the levels by grid: "ERCOT (Texas): Central time", then "CAISO SP15 (Southern California): Pacific time".
- **Clock times** are shown in each level's own time zone: the play header, the chart axis, the debrief, the replay and the strip below the chart.
- **The play header** names the grid.
- **The debrief** names the grid ("The grid: CAISO SP15 (Southern California)") and the hub, and links `/grid/caiso`. ERCOT days link `/grid/ercot` as before, and only ERCOT days link an `/events` page.
- **The share card** names the grid's prices.
- **Unchanged and confirmed by the scripted plays:** the leaderboard by preset, the DP optimum and the server's rescoring work per level.

### Two decisions

1. **The ERCOT days are frozen.** A plain run of the builder keeps the five ERCOT days exactly as session 38 wrote them; the only change is the new `grid` and `tz` fields, and a test checks that their prices are untouched. `--rebuild-ercot` chooses them again. Without this, rebuilding to add California would have re-chosen the ERCOT "solar-heavy" day from `eia930_all_generation`, which has grown since. That could move a level, and its leaderboard, to another date.
2. **No date may be shared.** The game keys a level by its date (`game_scores.level_date` is a `date` column), so a California day may not share its date with an ERCOT level. Changing the schema was out of scope (no Supabase change). Instead the builder stops, rather than choose another day, if a California day:
   - is an ERCOT famous day, or
   - falls in the last 14 days, where ERCOT's recent days are levels.

   Neither happened: the ERCOT calm day is 2026-04-26, one day before the cheapest midday.

## 3. Checks

- **Tests:** `tests/test_session56.py`, 5 tests:
  - each California day's prices equal its rows in `iso_hub_prices_history`;
  - each day holds every interval of its Pacific day, 15 minutes apart, and nothing more;
  - each rule, recomputed in pandas over the 393 complete days, picks its day, and each level's line states that rule's number (checked again from the level's own prices);
  - no date is shared with an ERCOT level, and the five ERCOT days are unchanged;
  - the picker, the rule, the debrief's link, and every clock call using the level's own time zone.
- **Session 38's test** now checks the five ERCOT days only. Its real-rows check is for ERCOT HB_HUBAVG; the California days have their own.
- **Results:** sessions 38, 55 and 56 together, 19 tests, OK. The DP test also times the optimum on the new days: 22 to 30 ms.
- **check-values:** 3,817 of 3,817 locally; **3,732 of 3,732 live**.
- **check-routes:** 63 of 63 locally and live.
- **One scripted play on each new level, live** (`play-battery.mjs`, marked as ERW checks):
  - the optimum's actions through `/api/play/finish` scored 0.8267 and 12.9806, equal to `lib/battery.ts`'s optimum;
  - `/api/play/score` stored each under `normal:13.5-5-90`, with the check row left off the leaderboard;
  - `/api/play/top` answered 200 for each day on Hard;
  - every earlier check of the script passed too.
- **Phone width:** `screenshots.mjs` now includes `/play/battery`. At 390 px the two groups and the California cards with their rules fit with no horizontal scroll. A level's date no longer wraps mid-date.
  - A first screenshot made with Chrome's `--screenshot` flag looked clipped, but `/tour` clipped the same way: that flag cannot render narrower than its minimum window. The DevTools script renders a true 390 px viewport.

## Open questions

1. **The fleet call on California days** is still the game rule modeled on ERCOT's ADER pilot, and the page says so. Should California days model a California program instead, such as the Demand Side Grid Support program or an Emergency Load Reduction Program event?
2. **More California levels** would make the date-keyed leaderboard tighter. A `grid` column on `game_scores` (with the key `level_date, grid, preset`) would remove the one-date-per-level limit. That is a schema change for a later session.
