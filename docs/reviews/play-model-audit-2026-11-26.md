# The games under `/play`: their arithmetic audited as a hostile expert would

Session 10227, chain 710 part D, 26 November 2026, the old laptop. Read as a battery trader and an EV fleet manager who play to find the score wrong, and as a teacher checking what the games teach. The pages: `/play/battery` (the home battery game, its three modes) and `/play/ev` ("Should your family get an EV?"). Only what is on main: the battery game's branch `wip/7535-play-battery` was never landed and is not read.

- Nothing changed on main but this file and its evidence folder (`docs/reviews/play-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no live service asked, no play written: the game's write routes were read, never called.
- Each finding with a fix has its own branch, `wip/audit-play-<n>`. Words-only fixes (1, 2, 4, 5, 6) are for landing, also merged together as `wip/audit-play-words`; 3 and 7 would move figures and wait for the owner; 8 needs a person to confirm a date.

## In short

- **The arithmetic is right.** An independent restatement (no site code) of the battery game's scorer and of its perfect battery agrees with the site's own `simulate`, `tally` and `optimum` on 693 of 693 figures (8 levels, Easy, Normal and Hard, 6 plays each: the best, a naive clock rule, a bad one, selling first, idling, and the site's own best plan), to 2e-12 USD, and on the server's four-place scores. The EV game: 312 of 312 figures for the 52 places of its price file, and all 208 keyed figures, to 3e-12.
- **"The perfect battery" is the true optimum of the game.** A second dynamic programme written here gives the same score on all 16 day-and-mode cases; a battery free to run at any power (a mixed-integer programme) earns at most 2.7 percent more (Uri on Hard), 0.1 percent on the default day.
- **What is stored was wrong in one clause (finding 1).** "Nothing that joins it to a leaderboard row": a posted play leaves two rows with the same level, score to four places, preset and a time seconds apart. Words, for landing.
- **The starting charge is free and the end charge worthless (findings 2 and 3).** Ending the day as full as it began would cut the perfect score 15 percent on the default day, 24 on Uri's, 31 on the calm spring day. The page now says the rule (words); changing it is the owner's.
- **A home battery is paid the wholesale price both ways (finding 4).** At the average price Texas homes pay, and ending as full as it began, the perfect battery earns USD 0.18 on the default day (against 2.09) and nothing on 4 of the 7 famous days. The method note said so; the page did not. Words, for landing.
- **Smaller words.** The end table's hovers (finding 5: Hard's prices are not all real; the perfect battery is held to three moves; wear is per kWh taken out, USD 0.116 per kWh sold); Normal's "no forecast" while the fleet call names the day's dearest hour 15 minutes ahead (finding 6); "ERCOT's offer cap since 2023" where the warehouse's own prices show it in 2022 (finding 8, to confirm).
- **The EV game's verdict rests on one week of gasoline (finding 7).** The 52 weeks' mean in place of the newest week moves the US net present value from USD 3,887 to 2,946 and turns it below zero in Massachusetts, New Hampshire, New York and Rhode Island. Said on the page; for the owner.
- **Held grids reach neither game; the EV game prices charging at the retail residential price, as it should.** The battery game reads ERCOT and CAISO rows only (public); Hard's score on an ordinary day is 98.5 to 100 percent the game's own emergency, which the page labels a game rule.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/play/battery/page.tsx` | The page: the game, "The day and the battery" (today's level's lowest and highest price, what is real and what assumed), the rules (version 5), the fleet call against ERCOT's ADER pilot, the fictional and real fleet, "What is stored", the sources |
| `site/app/play/battery/Game.tsx` | The game in the browser: the mode picker, the day at a glance, the play, the notices, the end table and its hovers, the hour lost the most, the replay with its reasons, the share card, the leaderboard |
| `site/lib/battery.ts` | The rules and their arithmetic, no imports: settings and their sources, difficulties, `rulesOf`, `emergencyOf`, `step`, `simulate`, `tally`, `noBattery`, `optimum` (the dynamic programme), `shownPrices`, `worstHour`, `explain`, presets, `glance`, `priceHover`, `fullCycle` |
| `site/lib/levels.ts` | The levels: today's level (the newest complete ERCOT day of HB_HUBAVG real time in the live set's last 30 days) and the seven famous days of `site/data/battery_levels.json`; `levelFor`, the server's check of a posted play's day |
| `site/lib/game.ts`, `site/app/api/play/finish`, `score`, `top` | The server: every score rescored from the actions (`scoreOn`), the rate limits, the leaderboard reads, and the two writes: `game_plays` (the research record) and `game_scores` (the public board) |
| `warehouse/supabase/migrations/013_game.sql`, `014`, `018`, `019`, `033` | The two tables, their columns and row-level security |
| `warehouse/derived/battery_levels.py`, `battery_solar.py` | The famous days chosen by stated rules from `ercot_all_hub_prices_history` and `iso_hub_prices_history`; the roof's shape (EIA-930 over EIA-860M) |
| `site/app/play/ev/page.tsx`, `EvGame.tsx`, `Decisions.tsx` | The EV page: the family's inputs with each default's source on hover, payback and net present value, a year of fuel, the cost chart, "every number", the eleven decisions |
| `site/lib/ev.ts` | The EV arithmetic: defaults and their sources, `chargePrice`, `verdict`, `cumulative`, `keyed` |
| `site/data/ev_prices.json` | Each state's newest residential price (EIA Electric Power Monthly 5.6.A, `eia_retail_electricity_prices`) and newest weekly regular gasoline (`eia_regional_retail_fuel_prices`), built 2026-11-17 |
| Notes | `docs/methods/battery_game.md`, `docs/methods/ev_game.md`, `docs/battery_game_demo.md` |

## The default game and the plays re-done, to the digit

The page opens on Easy (Normal and Easy score alike; Easy only shows the day ahead) at today's level, read from the live set, which this machine does not read. The newest complete ERCOT day in the main copy's `iso_rtm_hub_prices` (2026-11-12, Central) stands in for it; the seven famous days are the page's own file.

- `extract.py` streamed the prices from the main copy's tables (read only): the history's 4,255 complete days, the famous days' real-time and day-ahead prices, the newest days at each ERCOT hub.
- `restate.py`, from the method note's words and none of the site's code: the scorer, a dynamic programme over the three actions, and a mixed-integer programme of a battery free to run at any power (scipy, HiGHS) with its linear relaxation.
- `site_side.mjs` ran the same plays through the site's own `site/lib/battery.ts`; `compare_battery.py` set them side by side: **693 of 693 figures agree** (score, server score, kWh bought and sold, their average prices, the end charge, the end and its reason), largest difference 1.8e-12 (`compare_battery.out`).

| Level, Normal (USD, one battery) | Perfect | Any power | Naive (charge 02:00 to 05:00, sell 17:00 to 20:00) | Bad (the reverse) | Sell first | Idle |
|---|---|---|---|---|---|---|
| Default, 2026-11-12 | 2.0882 | 2.0902 | 1.5567 | -1.1906 | 0.3797 | 0 |
| Uri, 2021-02-15 | 240.2274 | 240.7426 | -8.8908 (out of money) | -7.0726 (out of money) | 56.4103 | 0 |
| Heat, 2023-08-10 | 60.9710 | 61.1691 | 17.2432 | -5.6259 (out of money) | 0.1750 | 0 |
| Calm, 2026-04-26 | 0.4406 | 0.4419 | 0.0933 | -0.1444 | 0.1666 | 0 |
| Solar, 2026-08-29 | 0.9328 | 0.9352 | 0.3573 | -0.4503 | 0.1583 | 0 |
| Negative, 2025-01-05 | 0.7949 | 0.7984 | 0.5256 | -0.4341 | -0.2018 | 0 |
| CAISO noon, 2026-04-27 | 0.8267 | 0.8306 | -0.0046 | 0.0148 | 0.0667 | 0 |
| CAISO ramp, 2026-07-24 | 12.9806 | 13.0160 | 7.2597 | -5.6552 (out of money) | 0.6638 | 0 |

- **Hard** (the default battery, reserve 25 percent, wear USD 0.11 per kWh, the emergency): perfect 29.8218 on the default day, 154.6718 Uri, 48.3635 heat, 29.4861 calm; every play agrees. The demo note's figures (60.97, 48.36, 0.44, the roof's 88.34) come out the same.
- **The default day's perfect plan** bought 28.81 kWh at an average of 22.08 USD/MWh and sold 32.34 kWh at 67.85; the 3.52 kWh more sold than bought is the free starting charge less the losses (finding 2).
- **The EV game.** `ev_restate.py` (no site code) and `ev_site.mjs` (the site's `lib/ev.ts`): **312 of 312 figures** for the 52 places agree to 2.7e-12, and so do the four keyed figures of each place. The United States at the defaults: gasoline USD 2,219.44 a year, electricity 844.44, saved 1,375.00, payback 3.6 years, net present value USD 3,887. The file's 52 electricity cells equal the warehouse's newest month (August 2026) to the cent; its gasoline cells are of the week of 9 November, newer than this machine's copy (2 November), so they were not checked here (data request b).

## One rule changed at a time

`measures.py` (`measures.out`, `summary.out`, `ev_flips.out`), each with restate.py's own functions.

| Rule | The game | Changed to | Measured worth |
|---|---|---|---|
| The perfect battery's moves | three: full charge, full sell, hold | any power from zero to full | default +0.0020 (0.1 percent); Uri Hard +4.19 (2.7); others 0.0 to 0.5 percent |
| The end of the day | the charge left counts for nothing; it starts half full for free | must end at least half full | default 2.0882 to 1.7809 (-15 percent); Uri -24; calm -31; solar -21; negative -15; CAISO noon -6; heat -0.4 |
| The start | half full | empty | default 2.0882 to 1.7085 (-18 percent); calm -41 |
| The price paid to charge | the real-time wholesale price | Texas's (California's) average residential price that month, sold at wholesale | default 2.09 to 1.22 (any power); with the end held half full 0.18; calm, solar, negative and CAISO noon 0.00 |
| The fleet call's bonus | the hour's mean price again on each kWh sold in it | none | default 2.0882 to 1.5578 (-25 percent); heat -27; CAISO ramp -35 |
| Wear on Normal | none | USD 0.11 per kWh taken out (Hard's) | default 2.0882 to 0.4810; calm and solar 0.0000: no cycle pays |
| Hard's emergency | the dearest hour spiked toward 5,000, then a two-hour outage | Hard without it (reserve and wear kept) | default 29.8218 to 0.4491 (98.5 percent of the score is the emergency); calm and solar 29.49 and 29.61 to 0.0000; Uri 154.67 to 186.75 |
| Price resolution | 15-minute real time | the hour's mean | default -3.8 percent; heat -14 |
| Foresight | every real-time price known | the plan made on the day-ahead prices, scored at real time | default 1.6193 (78 percent of perfect); heat 16.77 (28 percent); calm 0.0987 (22); solar 0.8595 (92); Uri -8.89, out of money |
| Place | the hub average | Houston's hub (2026-11-12) | perfect 1.2475 against 2.0882; the hub-average plan played at Houston 1.0357 |
| EV gasoline | the newest week (USD 3.995, 9 November) | the 52 weeks to 2 November (3.7328) | US payback 3.6 to 4.1 years, NPV 3,887 to 2,946; NPV below zero in 6 places instead of 2 (MA, NH, NY, RI turn); mean change -972 |
| EV electricity | the newest month (August 2026) | the 12 months to August | US 181.6 to 180.58 USD/MWh, NPV +31; CA 297.5 to 325.77, NPV 6,030 to 5,181; HI payback 14.2 to 10.4; ME turns above zero |
| EV payback | not discounted | discounted at the game's 5 percent | US 3.64 to 4.12 years; TX 4.33 to 5.01; HI 14.2 to 25.3 |

## Each claim against the code

- **The prices and their day.** ERCOT's real-time settlement point price at HB_HUBAVG, every 15-minute interval of a Central operating day (92, 96 or 100); CAISO's SP15 real-time price as the 15-minute mean of its 5-minute prices, said. Today's level is the newest complete day of the last 30 and names its day; "Today's level" may be days old, its date beside it. Right.
- **Real time against day-ahead.** The game is real time throughout and says so. The perfect battery knows every real-time price; a trader knows the day-ahead prices the day before, and a plan made on them earns 22 to 92 percent of perfect on the days held (the table above). The page's words ("a battery that knew every price") are right; the gap is what an expert would add.
- **Round-trip losses and the state of charge.** The square root of the round trip each way, full power or idle, charge clipped at full, discharge clipped at the reserve (Hard), as said. The end table's "loses 10 percent of the energy on the round trip" is right; "$0.11 of wear on each kWh it sells" is not: wear is charged per kWh taken out, USD 0.116 per kWh sold (**finding 5**).
- **"The best possible".** The end table's hover says the perfect battery is "the most any play of this day could earn": true of plays, which have the same three moves (two dynamic programmes agree on all 16 cases, and the site's test checks 3^12 plays of toy days). A battery free to run at part power would earn up to 2.7 percent more; the hover's "the same battery" does not say it is held to the three moves (**finding 5**).
- **On Hard, "the day's real prices".** The end table's "You" hover says the play is scored "on the day's real prices"; on Hard the dearest hour is traded at the game's prices, which the note under the table says but the hover does not (**finding 5**).
- **Normal's "no forecast".** The fleet call's notice says, 15 minutes ahead, that the next hour is the day's dearest; the ADER section says nobody knows that in advance in the pilot, but the modes line still says "no forecast" (**finding 6**). Knowing it is worth at least the bonus (25 percent of the default day's perfect score).
- **The starting charge.** "Half full at the start (assumptions)": the page did not say the starting charge is free and the end charge worthless (**findings 2 and 3**).
- **Wholesale against retail.** The intro says "wholesale power prices"; the method note says "the battery buys and sells at the wholesale real-time price, which no household does"; the page did not (**finding 4**). The ADER section's "every kWh sold earns the real-time price" is the pilot's settlement for an aggregator, not what a home pays.
- **The EV's charging price.** The average residential price of the state's newest month, every utility and hour, fixed charges spread over the kWh, said in the decisions; retail, not wholesale, as it should be. The average overstates an EV's marginal kWh where a bill carries a fixed charge, and understates it on a tiered rate's top tier; neither is held (below).
- **Units.** USD/MWh shown as cents a kWh (divided by 10), kWh per mile from fueleconomy.gov's wall-to-wheels figure (charging losses in it, as said), USD a gallon. Right.
- **The emergency's numbers.** USD 105.00 for a two-hour outage (1.5 kW x 2 h x 35,000 / 1,000), the reserve 3.38 kWh against the outage's 3.16, the fleet 50 MW and 135 MWh, the degradation cost 721 x 25 / 158,000 = 0.114: all right. "ERCOT's offer cap since 2023" (**finding 8**).
- **The levels' rules.** The negative-price day (2025-01-05, mean -10.66 USD/MWh) is the lowest of the history's 4,255 complete days to 2026-08-25, and none of the 74 later days held is lower (the lowest, 2026-10-11, 13.85). The calm day is the narrowest range of the 92 days of March to May 2026 (17.68). Right.
- **Held grids.** `iso_rtm_hub_prices` and `iso_hub_prices_history` are held "by grid" for ISO-NE, MISO and NYISO; the game reads `ercot:HB_HUBAVG` and frozen CAISO SP15 rows only. The EV game's two EIA tables are public. Nothing held reaches either game.
- **What is stored.** The battery page: see **finding 1**. The EV page carries `noUsage`: the page view is counted and nothing after it, and nothing the family types is sent; it promises nothing in words that the code breaks.

## What an expert's own number would hold that this does not

- **A retail bill, not a wholesale spread.** A home battery's value is the bill it saves (time-of-use rates, export credits, demand charges), not the wholesale spread: at the average Texas residential price the perfect battery earns nothing on most days once it must end as full as it began (above). Tariffs are not held.
- **Foresight a trader has.** The day-ahead plan played at real time earns 78 percent of perfect on the default day and 28 on the heat day; the game's "percent of perfect" measures a player against perfect real-time foresight.
- **A battery's own place.** Houston's hub gave a perfect 1.2475 against the hub average's 2.0882 on 2026-11-12; the ADER pilot settles at the load zone, which is not held here.
- **Hard as a market.** On an ordinary day 98.5 to 100 percent of Hard's perfect score is the game's spike, its bonus and the outage, all labelled game rules; a Hard leaderboard ranks skill at the game's emergency, not at the day's market.
- **The EV: the marginal kWh, public charging, resale, upkeep.** A fleet manager prices the marginal kWh (a time-of-use or EV rate), a share of public fast charging, depreciation and maintenance. None is held; the game says what it leaves out. The decisions name one EV rate (PG&E's E-TOU-C) without using it.
- **The EV: a year of prices, not a week.** Finding 7: the newest week of gasoline sits USD 0.26 above its 52-week mean.

## Findings

| # | Severity | Finding | Measured | Branch | Kind |
|---|---|---|---|---|---|
| 1 | Moderate | "What is stored" says a play's research record has "nothing that joins it to a leaderboard row", and a posted score stores "nothing else" than five fields | both rows carry the level, the score to four places, the preset and a time stamped by the same database seconds apart; the public row also stores the preset and difficulty; the usage counts and the hourly limit's daily code were not named | `wip/audit-play-1` (`b07de2fb7`) | words, for landing |
| 2 | Moderate | The page does not say the starting half charge is free and the end charge counts for nothing | the perfect plan sells 3.52 kWh more than it buys on the default day | `wip/audit-play-2` (`4f12d4559`) | words, for landing |
| 3 | Moderate | The rule itself: every score includes the starting charge sold | ending at least half full: default -15 percent, Uri -24, calm -31 | `wip/audit-play-3` (`a7863f750`) | figure, the owner's ruling |
| 4 | Moderate | The page never says no household buys or sells at wholesale | at the Texas average residential price, ending half full: default 2.09 to 0.18; 0.00 on calm, solar, negative and CAISO noon | `wip/audit-play-4` | words, for landing |
| 5 | Minor | The end table's hovers: "on the day's real prices" on Hard; the perfect battery "the same battery" though held to three moves; wear "on each kWh it sells" | any power +0.1 to +2.7 percent; wear USD 0.116 per kWh sold | `wip/audit-play-5` | words, for landing |
| 6 | Minor | Normal says "no forecast" while the fleet call names the day's dearest hour 15 minutes ahead | the bonus alone is 25 percent of the default day's perfect score | `wip/audit-play-6` | words, for landing |
| 7 | Moderate | The EV verdict uses the newest week of gasoline and the newest month of electricity, held flat for 8 years | 52-week gasoline: US NPV 3,887 to 2,946, four states below zero; 12-month electricity: CA NPV -849, ME above zero | `wip/audit-play-7` | figure, the owner's ruling |
| 8 | Minor | "ERCOT's offer cap since 2023" | the history's highest interval: 9,051.55 in 2021, 5,101.55 in 2022, 5,075.46 in 2023: the cap was 5,000 in 2022 already | none | to be confirmed by a person |

### 1. What is stored

- **Where.** `page.tsx`, "What is stored". `site/app/api/play/finish/route.ts` writes `game_plays` with `session_id, level_date, actions, score, check, preset, difficulty, settings`; `score/route.ts` writes `game_scores` with `level_date, nickname, score, optimal_score, check, preset, difficulty`; migration 013 stamps `ts` with `now()` on both. The game posts the finish when a play ends and the score when the player posts it, so the two rows of one play share the level, the score to four places, the preset and a time seconds apart. The page also never named the site's usage counts on it (the page view and "input changed", `docs/methods/usage_counts.md`) or the hourly limit's daily code (`site/lib/guard.ts`).
- **The fix on the branch.** Words only: the paragraph lists the preset among what each row stores, says the two rows "could be matched to each other; no column joins them", and names the usage counts and the limit's daily code; the method note says the same. Drawn and read: pass (`diff_b1.out`: only that paragraph changed, in all three modes). Test `tests/test_audit_play_1.py`; the 13 test files that read the page or the note pass (144 tests).

### 2 and 3. The starting charge

- **Where.** `rulesOf`: `start: s.kwh * 0.5`; `simulate` and `optimum` add nothing for the final charge. The perfect battery ends every famous day empty on Normal.
- **Finding 2, the fix on the branch.** Words only, in the money rule: "The battery starts half full at no cost, and whatever is left in it when the day ends counts for nothing, so selling the starting charge counts as earnings: on Normal, on the calm spring day, it is nearly a third of the perfect battery's score." The note gives the measured effect. Drawn and read: pass (`diff_b2.out`). Test `tests/test_audit_play_2.py` (an independent dynamic programme: 0.440601 free, 0.304087 ending half full); the 13 test files pass (143 tests).
- **Finding 3, for the owner.** Ending at least as full as it began would move every perfect score and share: Uri 240.2274 to 181.7193, heat 60.9710 to 60.7340, calm 0.4406 to 0.3041, solar 0.9328 to 0.7328, negative 0.7949 to 0.6723, CAISO noon 0.8267 to 0.7775, CAISO ramp 12.9806 to 12.3609. Test `tests/test_audit_play_3.py` (passes on main: it shows the rule). Default: left as it is.

## Rows for the desk

- **Landing (words, requested):** to be filled when every branch is pushed.
- **For the owner (not for landing):** `wip/audit-play-3` `a7863f750`; `wip/audit-play-7`.
- **Data requests:** (a) CAISO SP15 day-ahead prices (`iso_dam_hub_prices`, `caiso:TH_SP15_GEN-APND`, `lmp_dam`) for 2026-04-27 and 2026-07-24, Pacific days, which this machine's copy lacks: to measure the day-ahead plan on the two California levels. (b) The 52 gasoline cells of `site/data/ev_prices.json` (week of 9 November 2026) against the data machine's `eia_regional_retail_fuel_prices`, and the 52-week mean to that week for each: this machine's copy ends 2 November. (c) On the live set, with the service key, a count only (no row copied): the `game_scores` rows (`check` false) for which a `game_plays` row has the same `level_date`, `preset` and `score` and a `ts` within 120 seconds; it sizes finding 1.
