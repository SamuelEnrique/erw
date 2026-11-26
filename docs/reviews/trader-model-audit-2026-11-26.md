# The trader view: the model audited as a hostile expert would

Session 10209, 26 November 2026, chain 710 (part D), the old laptop. Read as a power trader at a utility desk who reads day-ahead against real time, on-peak against off-peak, heat rates and volatility every morning and wants to find them wrong. In the form of `docs/reviews/board-model-audit-2026-11-26.md` and `docs/reviews/datacenter-model-audit-2026-11-26.md`.

- Nothing changed on main but this file and its folder of evidence (`docs/reviews/trader-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no request to any service.
- Each finding's test is on its own branch, `wip/audit-trader-<n>`. Branches that change only words are for landing (the rows at the foot); a branch whose fix would move a figure carries the test only and is not for landing.
- **Where the trader view is now.** Platform tool 24's page, `/markets`, was retired in session 132: it redirects to `/board` (`site/next.config.ts`), and its table is the board's group "The week, by hub" with "The week's highest real-time intervals" under it (`WeekTable` in `site/components/board/BoardView.tsx`), and a hub's week in the workbench. So this audit reads the builder of the trader tables (`warehouse/derived/trader_view.py`), the week's builder (`build_week` in `warehouse/derived/board_page.py`) and the week table's words.
- **Not repeated:** the board audit of tonight (its findings 1 to 5: the kept rows and ERCOT's two "latest" prices, the held grids' week lines in `board.json`, CAISO's two on-peak blocks and the on-peak week of 9 calendar days, the strip's stale mark, the battery spread), the trader's read of 16 November (`docs/reviews/board-read-2026-11-16.md`: row 8, the spread's sign; row 9, the stale volatility) and the cross-checks of session 2228 in `docs/methods/iso_trader_daily.md` (the day-ahead mean and the heat rate).

## In short

- **The arithmetic is right.** An independent restatement written from the two method notes, not from the code, makes every public row of `iso_trader_daily` again from the warehouse's price tables and Henry Hub: 4,543 figures of ERCOT, CAISO and SPP (nine variables, 26 August to 21 October 2026), every one to the fourth decimal but nine heat rates of 15 October, which the table took on the gas of 14 October because EIA published 15 October's a day after the run (finding 2). MISO's 2,408 figures agree too (counts only). The board's week table of 21 October, built from that table, agrees in all 227 public figures; the board of 25 November agrees to the cent on the three hubs whose hourly files reach the week's end. The top ten real-time intervals: 10 of 10 for ERCOT and CAISO.
- **SPP's real-time prices are held and the trader view does not read them (finding 1, Medium).** The notes said "the ERW has no SPP real-time table"; the table has been held for months, and the board draws SPP's real-time rows a few lines above a week table whose SPP real-time cells said "Needs a real-time price on each of the week's 7 days". The rule would give SPP North a real time less day-ahead week of -3.73 USD/MWh. Words fixed; computing it is Samuel's ruling.
- **The heat rate divides power by gas traded a day later, and at the newest days by gas up to 4 days older (finding 2, Medium).** EIA dates Henry Hub by the trading day (gas for the next day's flow); the day-ahead power traded the day before. On the board of 25 November the heat-rate week ends on 21 November on Henry Hub of 17 November. Taking the trading day before moves ERCOT's daily heat rate by 0.31 MMBtu/MWh on average (65 of 363 days by more than 0.5, at most 4.86). Words fixed; the gas day is Samuel's ruling.
- **The off-peak week weighs days, not hours (finding 3, Medium; a figure).** A weekend day's 24 off-peak hours count as much as a weekday's 8. SP15's week on the board of 25 November: 42.72 as drawn, 39.36 hour-weighted (-7.9 percent); SPP North 19.08 against 16.61 (-13.0 percent). For Samuel's ruling.
- **Two heads said nothing of what they measure (finding 4, Low).** "30-day volatility" is a standard deviation of daily changes in USD/MWh, not annualized, not a percent, and two missing days hold ERCOT's at 6 November until 9 December; "Hours RT over DA + 50" counts hours by the hour's mean, where any 15-minute interval would count 1.6 to 6.3 times as many. Words fixed.
- **Smaller, the notes only.** The on-peak block is hours ending 7 to 22 in every grid, where the Eastern block (NYISO, ISO-NE, PJM) is hours ending 8 to 23 (finding 5, held grids, no page shows it); the notes described `/markets`, a week rule and a top-ten week the code does not have (finding 6).
- **Five branches fix words and move no figure (1, 2, 4, 5, 6); one shows a figure for ruling (3); findings 1 and 2 also carry a ruling line.** The five merge together and with the board audit's branches 3, 4 and 5 onto origin/main with no conflict, and every test passes.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `warehouse/derived/trader_view.py` | The builder (session 19): for each grid in `ISOS` (ERCOT, CAISO, NYISO, MISO, SPP, ISO-NE) and each hub and complete local day, the nine daily metrics; the 30-day volatility; `iso_rt_top_intervals`, the ten highest real-time intervals of each grid's latest 7 complete days; `keep_retrieved` |
| `warehouse/consolidate.py` | Folds the six `<iso>_trader_daily` members into `iso_trader_daily` (session 29), told apart by `market` |
| `warehouse/connectors/iso_prices.py`, `warehouse/connectors/eia_fuels.py` | The inputs: `iso_dam_hub_prices` and `iso_rtm_hub_prices` (ERCOT, CAISO, MISO, SPP; `spp_rtm` among them), `nyiso_*` and `isone_*` zone tables; Henry Hub in `eia_fuel_spot_prices`, dated by EIA's trading day |
| `warehouse/derived/board_page.py`, `build_week` | The week table and spikes the board shows, from `iso_trader_daily` and `iso_rt_top_intervals`: each measure's latest 7 days in the grid, the mean (all 7 needed, one for on-peak), the change on the 7 before, the largest spread, the hours, the newest volatility, the newest day-ahead mean |
| `site/components/board/BoardView.tsx`, `WeekTable` | The trader view's face on `/board`: "The week, by hub" (11 public rows; NYISO and ISO-NE as one "license needed" line each, MISO paused, PJM licensed) and "The week's highest real-time intervals" |
| `site/components/board/Workbench.tsx` | A hub's week (the same figures) when its row is opened |
| `site/lib/board.ts` | `holdRows` (drops a held grid's week lines and spikes on the server), `weekStale` (the volatility's stale mark) |
| `site/data/board.json` | `week` and `spikes` as the builder wrote them (built 25 November 2026, 15:23 UTC) |
| `site/public/board/h/<hub>.json`, `site/public/board/s/eia-henry-hub-spot.json` | A hub's day-ahead and real-time hours (to the cent) and on-peak flags; Henry Hub's series. The restatement of the board of 25 November reads these |
| `site/next.config.ts`, `site/app/_retired/markets/page.tsx` | `/markets` redirects to `/board`; the old page is kept in a folder Next.js does not route |
| `docs/methods/trader_view.md`, `docs/methods/iso_trader_daily.md`, `docs/methods/price_board.md` ("The week, by hub") | The notes: the metrics, the inputs, the page; the consolidated table and its cross-checks; the board's use of it |
| `warehouse/supabase/live_set.yaml` | `iso_trader_daily`, 45 days, in the live set (with its held grids' rows: `license_status.csv`, "license needed" from 21 October 2026, cited, not a finding here) |
| `warehouse/analysis/templates/implied_heat_rate.py` | Reads `iso_trader_daily` for Automated Analysis (tool 26, audited in part C); not read here |

## How every number here was computed

- **The independent restatement of the table:** `restate_trader.py` (standard library), written from `trader_view.md` and `iso_trader_daily.md`: each hub's local days from the price tables (`zoneinfo`, 23, 24 or 25 hours), on-peak with NERC's holidays written a second way, a real-time hour as the mean of four 15-minute intervals, the spread as real time less day-ahead, Henry Hub of the day or up to 4 days before, the volatility as a `Decimal` standard deviation of 30 changes over 31 calendar days. It reads `iso_dam_hub_prices`, `iso_rtm_hub_prices` and `eia_fuel_spot_prices` of the main checkout (26 August to 12 November 2026, read only) and compares with `iso_trader_daily` of the main checkout (run of 21 October 2026, 14:36 UTC). A held grid's value is never printed: MISO is compared by counts only; NYISO's and ISO-NE's inputs are not read.
- **The week table:** `restate_week.py`, written from the notes' rule for the week. Part A: the board of 21 October (`git show 47b1fbc7e:site/data/board.json`, built 15:19 UTC in the same run as the table) against the table on disk. Part B: the board of 25 November against the page's own hourly files and Henry Hub series.
- **One rule at a time:** `measures_trader.py`, on the same tables and page files, public grids only.
- **The drawings:** `draw_week.mjs` draws `BoardView` with the site's own code (`node --import ./scripts/tsx-register.mjs`, after `holdRows`) and writes the week section's hovers and words; each words branch drawn and read (`draw_b1.txt`, `draw_b2.txt`, `draw_b4.txt`, and `draw_trial.txt` for all branches merged).
- Copies of every script and its printout: `docs/reviews/trader-model-audit-2026-11-26/` (written to run from `runs/c10209/` of a worktree).

## The arithmetic re-done

| Figures | Compared | Agree | The gaps |
|---|---|---|---|
| `da_mean_usd`, `da_onpeak_mean_usd`, `da_offpeak_mean_usd` | 625, 438, 625 | all, exactly to the fourth decimal | |
| `rt_mean_usd`, `da_rt_spread_mean_usd`, `da_rt_spread_max_usd`, `hours_rt_over_da_50` | 495 each | all, exactly | |
| `da_volatility_30d_usd` | 283 | all, exactly | |
| `implied_heat_rate` | 592 | 583 | 9: every hub on 15 October 2026. The table took Henry Hub of 14 October (3.22) because EIA's 15 October (3.30) was retrieved on 22 October, after the run; today's file gives it. The rule, written again, gives the table's figure on the gas the table had |
| MISO, all nine variables (counts only) | 2,408 | all, exactly | |
| Restated inside the table's span and absent from it | | | the 21 October real-time day and 19 to 21 October heat rates (not yet published at the run); SPP's real-time metrics on 21 days: the rule makes them from `spp_rtm`, the code does not (finding 1) |
| Clock-change day, 1 November 2026 | 11 public hubs | all hold 25 hours and are written | |
| The board's week table of 21 October, from the table: the newest day-ahead and its date; five week means, their changes and ends; the largest spread; the hours; the volatility and its date | 227 on 11 public rows | 227, to the fourth decimal | |
| The board's week table of 25 November, from the page's hourly files: SP15, NP15, SPP North | 57 | 51 | SP15's largest spread 19.85 against 19.84 from hours rounded to the cent; SPP North's five real-time figures, which the page does not hold (finding 1) |
| `iso_rt_top_intervals`, the snapshot of 21 October | ERCOT 10, CAISO 10 | 20 | |

- **Not restated, and why.** ERCOT's six hubs, CAISO ZP26 and SPP South on the board of 25 November: their hourly files end on 20 November and the week ends on 25 November (the board audit's finding 1 and its data request; not filed twice). The spikes of 25 November: 15-minute prices are not in the page's files, and the tables here end on 12 November.
- **The rules the restatement wrote again and found as the code does them:** a local operating day in each grid's time zone (MISO in EST), complete at 23, 24 or 25 hours; hour-beginning timestamps, on-peak the hours starting 06:00 to 21:00 local (hours ending 7 to 22), Monday to Friday, NERC's six holidays with a Sunday's on the Monday; real time less day-ahead hour by hour, its mean, its largest and the hours above 50; the heat rate on Henry Hub of the day or up to 4 days before, a price above zero; the volatility over 31 consecutive days; the week means as the mean of 7 daily values.

## One rule changed at a time

Each line changes one choice and keeps every other. Public hubs; the tables of 26 August to 12 November 2026 unless a line names the board of 25 November.

| Choice the trader view makes | The other choice | Worth | Said on the page? |
|---|---|---|---|
| SPP: no real-time metrics | read `spp_rtm_hub_prices`, as for every other grid | SPP North's week (13 to 22 November, 7 days with both markets whole) -3.73, change -2.63, largest 31.29, 0 hours; SPP South (10 to 18 November) -3.66, +3.04, 99.19, 1 hour | no: "not held yet" (finding 1) |
| Henry Hub dated on the operating day | the trading day before, when the day-ahead power traded | daily heat rate, mean absolute change 0.24 to 0.40 MMBtu/MWh on seven main hubs (78 days; 51 on another gas price), at most 2.25; ERCOT hub average over 363 days to 20 November: 0.31, 65 days above 0.5, at most 4.86 | no (finding 2) |
| Henry Hub up to 4 days back at the newest days | none until EIA publishes the day | the board of 25 November: 18 to 21 November divide by 17 November's gas (1 to 4 days old); on 21 October, 15 October's heat rates by 14 October's | no (finding 2) |
| The off-peak week: the mean of 7 daily means | every off-peak hour once (88 hours a week) | the board of 25 November: SP15 42.72 to 39.36, NP15 57.22 to 58.74, SPP North 19.08 to 16.61; over 72 weeks the mean absolute gap 1.48 (ERCOT hub average) to 3.95 (SPP South), at most 9.35 (ERCOT West) | the board audit's words branch 3 says "the mean of the off-peak means"; not the weighting (finding 3) |
| The heat-rate week: the mean of 7 daily ratios | the week's mean price over the mean gas | mean +0.000 to +0.036, at most +0.258 MMBtu/MWh | no; small |
| Volatility: USD standard deviation of daily changes | annualized log returns | SP15 8.59 USD/MWh is 22.2 percent of the 31 days' mean price, 481 percent a year by log returns; SPP North 1,911 percent; SPP South none (a day at or below zero) | no unit on the page (finding 4); the note says why |
| Volatility: 31 calendar days, all needed | the newest 31 days held | ERCOT hub average 13.17 of 6 November (stale) to 12.06 to 20 November; the stale figure stands until 9 December | no (finding 4) |
| Volatility: day-over-day changes | 7-day changes (the same weekday) | SP15 8.59 to 7.22; NP15 6.93 to 10.26; SPP North 15.40 to 21.05 | no; a choice, not a fault |
| Hours over day-ahead + 50: the hour's mean | any 15-minute interval of the hour | ERCOT hub average 31 to 56 hours; HB_NORTH 42 to 68; HB_WEST 40 to 80; SP15 15 to 28; NP15 3 to 19 | no (finding 4) |
| On-peak hours ending 7 to 22 in every grid | the Eastern block, hours ending 8 to 23, for NYISO and ISO-NE | not sized: held grids | no (finding 5) |

## Each claim against the code

| Claim, or question | Where | What the code does | Verdict |
|---|---|---|---|
| "RT minus DA": its sign | the week's head | real time less day-ahead, hour by hour, then the day's mean; the group above takes the other order, said on hover | **Right as stated** (the read of 16 November, row 8) |
| Its averaging | the head's hover | the mean of 7 daily means of 23, 24 or 25 hourly differences; each day counts once | **Right as stated** |
| Hour-ending against hour-beginning | the notes | timestamps are each interval's start; on-peak is the hours starting 06:00 to 21:00, hours ending 7 to 22, as said | **Right**; restated |
| Time zones and daylight saving days | the notes | each grid's local day (Central, Pacific, Eastern prevailing; MISO in EST); 1 November 2026 holds 25 hours in all 11 public hubs and is written | **Right** |
| On-peak by grid, NERC holidays | the notes; the week's on-peak head (board branch 3) | Monday to Friday, hours ending 7 to 22, NERC's six holidays with a Sunday's on the Monday, in every grid | **Right for ERCOT and SPP**; CAISO's Saturday is the board audit's finding 3; the Eastern grids' block is finding 5 |
| Implied heat rate's gas hub | the note | Henry Hub in every grid, "indicative"; no regional hub | **Right as stated** (the board audit, "Gas at Henry Hub") |
| Implied heat rate's gas day | the note ("that of the operating day"); nothing on the page | Henry Hub of the date EIA gives (the trading day, gas for the next day's flow), or up to 4 days back | **Finding 2** |
| Volatility's definition and annualization | the note ("does not annualize"); the head said nothing | sample standard deviation of 30 daily changes in USD/MWh over 31 calendar days, all needed | **Right in the note; finding 4 on the page** |
| Negative prices in averages and logs | the note | every price enters the means as published; no logarithm is taken; a negative day's heat rate is negative and enters the heat-rate week (SPP South's lowest day in the table, -12.70 USD/MWh, `iso_trader_daily.md`) | **Right**; the negative heat rate is not said, and is small |
| "Hours RT over DA + 50" | the head | hours whose mean of four 15-minute prices ran more than 50 over day-ahead (strictly more) | **Finding 4** (the hour, not the interval, unsaid) |
| SPP's real time | the notes; the SPP cells' hover | not read: `ISOS` gives SPP `None` though `spp_rtm_hub_prices` is held | **Finding 1** |
| Held grids (ISO-NE, NYISO; MISO paused; PJM licensed) | the week table | `holdRows` drops their week lines and spikes on the server; drawn after it, no held figure is in the week section (`draw_trial.txt`) | **Right on the page**; `board.json` holds them (the board audit's finding 2); the table in the live set holds them under "license needed" (`license_status.csv`, cited) |
| Staleness | the volatility cell | `weekStale` marks a volatility past 3 days; the five week means carry their end on hover only | **Right as stated**; ERCOT's volatility is stale until 9 December (finding 4) |
| The window covered | the cells' hovers | each measure's latest 7 days in the grid: on 25 November day-ahead to 25 November, real time to 24 November, the heat rate to 21 November | **Right as stated** (`price_board.md`: "the end is on hover") |
| "The week's highest real-time intervals" | the list's head | the ten highest intervals of all a grid's hubs over its latest 7 complete days, which can run over 8 calendar days | **Finding 6** (the note); the list carries no dates in its head |
| "A week mean needs all 7 days" | the note; the empty cell's hover | all 7, but the on-peak mean is taken over one or more (`need = 1`) | **Finding 6** (the note); no public figure of 21 October differs |
| "The page that reads them: `/markets`" | the note; `platform-tools.md` | `/markets` redirects to `/board` since session 132 | **Finding 6** |

## What a trader's own number would hold that this does not

| Item | Why | Size, where measurable |
|---|---|---|
| SPP's real-time spread | held, not read | finding 1 |
| The heat rate on the gas traded with the power, and on the regional hub (Waha, Houston Ship Channel, SoCal Citygate, Panhandle) | the gas day is a choice; regional hubs are licensed indices | finding 2; regional not sized (no table) |
| The off-peak "wrap" weighted by hours, and on-peak blocks by the exchange's definition in each region | conventions | finding 3; the Eastern block not sized |
| Real-time spikes at the settlement interval (15 minutes in ERCOT, 5 in CAISO and SPP) | the trader view keeps hours | finding 4: 1.6 to 6.3 times as many hours |
| An annualized volatility of the forward curve, and implied volatility | forward curves and options are licensed (CME Group, ICE) | not sized |
| PJM West, MISO Indiana Hub, NYISO Zone J, ISO-NE Mass Hub | license needed, paused or licensed | `docs/licenses.md` |
| Node-level day-ahead less real time (virtual bidding) | hubs only | not sized |

## Findings, largest effect first

| # | Severity | Finding | Effect | Fix | Branch |
|---|---|---|---|---|---|
| 1 | Medium | SPP's real-time prices are held and not read; the notes say no table exists; the week's SPP cells give the wrong reason | SPP North's real time less day-ahead week -3.73 not shown, nor SPP South's -3.66 | words; computing it: ruling | `wip/audit-trader-1` |
| 2 | Medium | The heat rate takes Henry Hub dated on the operating day (gas traded a day after the power), and up to 4 days older at the newest days; unsaid | 0.31 MMBtu/MWh a day on average (ERCOT hub average, 363 days), at most 4.86; the week of 25 November ends on gas of 17 November | words; the gas day: ruling | `wip/audit-trader-2` |
| 3 | Medium | The off-peak week weighs each day once, not each hour | SP15 42.72 against 39.36 (-7.9 percent); SPP North 19.08 against 16.61 (-13.0 percent) | figure: ruling | `wip/audit-trader-3` |
| 4 | Low | "30-day volatility" and "Hours RT over DA + 50" said nothing of what they measure | the volatility is USD/MWh, not annualized (SP15 8.59 is 481 percent a year by log returns); the hours by the interval 1.6 to 6.3 times as many | words | `wip/audit-trader-4` |
| 5 | Low | On-peak is hours ending 7 to 22 in every grid; the Eastern block is hours ending 8 to 23 | held grids' rows of the table; no page shows them; not sized | words (the note) | `wip/audit-trader-5` |
| 6 | Low | The notes describe `/markets`, a week rule and a top-ten week the code does not have, and "SPP real time (no table)" | no figure | words (the notes) | `wip/audit-trader-6` |

- Ranked by severity, then by size. Three Medium, three Low.
- The five words branches (1, 2, 4, 5, 6) were merged together, with the board audit's words branches 3, 4 and 5, onto origin/main of 26 November in a trial: no conflict; the six trader tests, the three board tests and `tests/test_session89_miso_pause.py` pass (31 passed); `site/scripts/test-board-read.mjs` 31 of 31; drawn, the week section carries every new hover and line and no em dash. Each branch alone was run with every test file that reads the changed component, module or note (189 or 190 passed with 52 subtests on branches 1, 2 and 4; 16 on branches 5 and 6), and `test-board-read`, `test-board-1116` and `test-board-1193` pass on branches 1, 2 and 4.

## 1. SPP's real-time prices are held and not read (Medium; words, and a ruling)

- **Where.** `warehouse/derived/trader_view.py`, `ISOS["spp"] = ("spp_dam_hub_prices", None, "America/Chicago")`. `warehouse/connectors/iso_prices.py` writes `spp_rtm_hub_prices` (SPP's RTBM 5-minute prices as 15-minute means), the rows of `iso_rtm_hub_prices` whose `market` is `spp_rtm`; the board draws SPP North's and SPP South's real-time rows and hourly files from it. `trader_view.md` (inputs table), `iso_trader_daily.md` (inputs table and "What it does not hold"), the code's docstring and `platform-tools.md` said there is no SPP real-time table.
- **Why it is wrong.** A trader sees SPP's real-time price in the group "Power, by hub" and an empty "RT minus DA, week" for the same hub a few lines down, whose hover gave a reason that is not so.
- **How much.** From the page's own hourly file, the trader view's rule gives SPP North's week (the latest 7 days with both markets whole, 13 to 22 November, over 10 calendar days: SPP's real time has gap days) -3.73 USD/MWh, change -2.63, largest hourly 31.29, no hour over 50; SPP South (10 to 18 November) -3.66, +3.04, 99.19, 1 hour. On the tables of 13 November the rule makes SPP's real-time metrics on 21 days of the table's span.
- **The test.** `tests/test_audit_trader_1.py` on `wip/audit-trader-1`: the code reads no SPP real-time table while the connector writes one, and the week would hold -3.73 (passes on main); the notes' words and the drawn cells (fails on main).
- **The fix on the branch, words only.** The two notes and the docstring say the table is held and not read; the week's three SPP real-time cells read "not computed" with the hover "SPP's real-time prices are held (the real-time rows of the groups above), but the week's real-time measures are not computed for SPP: the trader view does not read them." Drawn and read: pass. No figure moves.
- **For Samuel's ruling.** Default "left as it is". The other choice: `ISOS["spp"]` reads `spp_rtm_hub_prices`; the week's SPP rows gain five figures each (SPP North -3.73, SPP South -3.66 on the file of 25 November).

## 2. The heat rate's gas day (Medium; words, and a ruling)

- **Where.** `trader_view.py`, `hh_for` (Henry Hub of the day, or up to 4 days before); `eia_fuels.py` and `eia_fuel_spot_prices.md` ("`ts_utc` EIA's trading date"); `trader_view.md` ("The Henry Hub price is that of the operating day"); nothing on the page.
- **Why it is wrong.** EIA's daily Henry Hub is dated by the day it traded, for gas flowing the next day; the day-ahead power for an operating day traded the day before. So on a weekday the heat rate sets the power against gas traded a day later (the gas the trader could not yet see). And the 4 days meant for weekends also bridge EIA's publication lag: on the board of 25 November the heat-rate week ends on Saturday 21 November, whose gas is Tuesday 17 November's; 18 to 21 November all divide by it. On 21 October the table's heat rates of 15 October used 14 October's gas, because 15 October's arrived the next day; the next run changed them, so a heat rate shown can move days later.
- **How much.** The trading day before the operating day in place of the operating day: on seven main hubs over 78 days the daily heat rate moves by 0.24 to 0.40 MMBtu/MWh on average, at most 2.25 (51 days on another gas price); ERCOT hub average over 363 days to 20 November, from the page's own files: 0.31 on average, 65 days by more than 0.5, at most 4.86. The mean change is near zero (+0.01): the week's figure moves less than a day's.
- **The test.** `tests/test_audit_trader_2.py` on `wip/audit-trader-2`: the measured move from the page's files, and the week of 25 November on gas of 17 November (passes on main); the note's and the drawn line's words (fails on main).
- **The fix on the branch, words only.** The note's row says which gas and why; a line under the week table says it: "Heat rate, week: each day's day-ahead mean over the Henry Hub spot price EIA dates on that day, or on the newest trading day up to 4 days before. EIA dates it by the trading day, gas traded that day for the next day's flow, while the day-ahead power traded the day before; and the newest days, before EIA publishes their gas, take a price up to 4 days older. Not any plant's heat rate, and not a regional gas hub's." Drawn and read: pass. No figure moves.
- **For Samuel's ruling.** Default "left as it is". The other choice: the gas of the trading day before the operating day, with the 4-day reach kept for weekends and holidays only (every daily heat rate moves, 0.31 MMBtu/MWh on average for ERCOT's hub average; the newest days without their gas blank).

## 3. The off-peak week weighs days, not hours (Medium; a figure)

- **Where.** `board_page.py`, `build_week`, `wmean`: the mean of the 7 daily `da_offpeak_mean_usd`. A weekday holds 8 off-peak hours, a weekend day or holiday 24.
- **Why it matters.** A trader's off-peak week (the 7x8 and 2x16 wrap) is the mean of its 88 off-peak hours; the page gives a Saturday's 24 hours three times a weekday night's weight per hour. Board branch 3's hover says "the mean of the off-peak means", which is right; the weighting is not said, and it is the choice that is in question.
- **How much.** On the board of 25 November (19 to 25 November): SP15 42.72 as drawn, 39.36 hour-weighted (-3.36, -7.9 percent); NP15 57.22 and 58.74 (+1.51); SPP North 19.08 and 16.61 (-2.48, -13.0 percent). Over the 72 weeks of the tables: mean absolute gap 1.48 (ERCOT hub average) to 3.95 USD/MWh (SPP South), at most 9.35 (ERCOT West). The day-ahead week's mean (7 daily means of 24 hours) and the on-peak week (16 hours each weekday) are not touched by this.
- **The test.** `tests/test_audit_trader_3.py` on `wip/audit-trader-3`: the page's figures and the hour-weighted ones from the hourly files. Passes on main; not for landing.
- **For Samuel's ruling.** Default "left as it is". The other choice: the week's off-peak as the mean of its off-peak hours (needs the daily off-peak hour count in `iso_trader_daily`, or the week built from the hours); SP15 42.72 to 39.36 on the file of 25 November.

## 4. Two heads of the week said nothing of what they measure (Low; words)

- **Where.** `BoardView.tsx`, `WeekTable`: "Hours RT over DA + 50" and "30-day volatility" had no hover; the volatility cell's hover gives only "as of" a date.
- **Why it matters.** A trader reads "volatility" as an annualized percent of log returns; here it is USD/MWh of daily changes, not annualized (the note says so; the page did not). SP15's 8.59 is 22.2 percent of the 31 days' mean price, and 481 percent a year by log returns. It needs 31 calendar days: ERCOT's day-ahead days of 7 and 8 November are missing, so ERCOT's figure of 6 November (13.17) stands, marked stale, until 9 December; the newest 31 days held would give 12.06. And the hours count an hour by the mean of its four 15-minute prices: over 26 August to 12 November any interval of the hour ran 50 over day-ahead in 56 hours at ERCOT's hub average against 31 by the mean, 80 against 40 at HB_WEST, 19 against 3 at NP15.
- **The test.** `tests/test_audit_trader_4.py` on `wip/audit-trader-4`: ERCOT's volatility of 6 November, the missing days and the 12.06 (passes on main); the heads' words drawn (fails on main).
- **The fix on the branch, words only.** The hours head: "The week's hours in which the hour's real-time price ran more than 50 USD/MWh above its day-ahead price. A 15-minute market's hour is the mean of its four 15-minute prices, so a 15-minute spike the hour's mean hides is not counted." The volatility head: "The sample standard deviation of the 30 day-over-day changes in the day-ahead daily mean, over the 31 days to the date shown, in USD/MWh: not annualized and not a percent (prices can be zero or negative, so no log returns are taken). It needs all 31 days, so one missing day leaves the last one standing, marked stale, for the 31 days after." Drawn and read: pass. No figure moves. A volatility over the newest 31 days held would move ERCOT's figure (13.17 to 12.06); not proposed, listed above.

## 5. The on-peak block is the Central and Western one in every grid (Low; words, the note)

- **Where.** `trader_view.py`: `6 <= h <= 21` on the local hour start for every grid; `trader_view.md` called it "the standard 5x16 block".
- **Why it matters.** Hours ending 7 to 22 is ERCOT's, SPP's and the Western block. The Eastern block that NYISO, ISO-NE and PJM name, and the Eastern contracts settle on, is hours ending 8 to 23 Eastern prevailing time. NYISO's and ISO-NE's rows take the earlier hour; MISO's take it in EST. Those grids are held or paused, so no page shows their on-peak figures, but the rows are in the table and the live set. The Eastern block's hours are this auditor's reading of the operators' and exchanges' definitions, not checked against a file held here (no request was made).
- **The test.** `tests/test_audit_trader_5.py` on `wip/audit-trader-5`: one block for every grid in the code (passes on main); the note's words (fails on main).
- **The fix on the branch, words only.** A note line names the block as the Central and Western one and the Eastern block beside it. Not sized: no held grid's price is read. Moving NYISO's and ISO-NE's block would move held figures no page shows: a data request below, not a ruling tonight.

## 6. The notes describe the trader view as it was (Low; words, the notes)

- **Where and what.** `trader_view.md`: "The page that reads them: the site's `/markets`" and "On the page (`/markets`)", retired in session 132; "A week mean needs all 7 days of the metric; otherwise the cell says 'no data'", where `build_week` takes the on-peak mean of one or more (`need = 1`) and the cell says "not held yet"; "the latest 7 local days" for the top ten, which can run over 8 calendar days (13 to 20 October for ERCOT and CAISO on the snapshot of 21 October), and the code counts a day whole on the interval times any hub holds, not each hub's (no day differs on the tables of 13 November). `platform-tools.md`: `/markets` and "SPP real time (no table)".
- **The test.** `tests/test_audit_trader_6.py` on `wip/audit-trader-6`: the redirect, `need = 1` and `sorted(full)[-7:]` (passes on main); the notes' words (fails on main).
- **The fix on the branch, words only.** The notes say each as it is. No figure moves; on the board of 21 October every public hub held all 7 on-peak days (the restatement used the rule of 7 and agreed on all 11).

## What was checked and found right

- **Every public row of `iso_trader_daily`** (4,543 figures, nine variables) and MISO's (2,408, counts only), restated from the price tables, exactly to the fourth decimal but the nine heat rates of 15 October explained above.
- **The week table** of 21 October (227 public figures) from the table, and of 25 November (51 figures on three hubs, to the cent) from the page's own files.
- **The calendar:** the local operating day in each grid, 25 hours on 1 November 2026 in every public hub, NERC's holidays (Labor Day, 7 September 2026, off-peak), hour-beginning timestamps.
- **The real-time hour** as the mean of four 15-minute intervals, all four needed; the spread's sign and its mean, largest and hours.
- **The top ten intervals** of 21 October for ERCOT and CAISO, 20 of 20.
- **No held figure in the week section** drawn after `holdRows`.

## Not covered, or left open

- **ERCOT's six hubs, CAISO ZP26 and SPP South on the board of 25 November**: their hourly files end on 20 November; the board audit's data request covers them.
- **The spikes of 25 November**: 15-minute prices are not in the page's files.
- **The workbench's own drawing of a hub's week** (`Workbench.tsx`): it shows the same figures from `board.json`; its words are the board audit's branch 3.
- **Automated Analysis's heat-rate template**, which reads `iso_trader_daily`: tool 26, part C.
- **The page's hourly files were read whole** (up to 881 KB, about four years of hours for ERCOT's hub average); every measurement here uses at most 365 days of them.

## Landing, rulings and data (returned to the chain's main session)

- **For landing (words only):** `wip/audit-trader-1` (`3b06ebfcd`), `wip/audit-trader-2` (`417426069`), `wip/audit-trader-4` (`1c083e5eb`), `wip/audit-trader-5` (`38b3d58d2`), `wip/audit-trader-6` (`09eedb97c`). They merge together and with the board audit's branches 3, 4 and 5 cleanly. Branches 1, 2 and 4 touch `site/components/board/BoardView.tsx` (not `site/app/board/`): land after window E's board group if both are waiting.
- **Not for landing:** `wip/audit-trader-3` (`355a6d71f`, a figure).
- **For Samuel's ruling, default "left as it is":** finding 1, read SPP's real-time table (SPP North's week -3.73, SPP South's -3.66 added); finding 2, Henry Hub of the trading day before the operating day (ERCOT hub average's daily heat rate moves 0.31 MMBtu/MWh on average, at most 4.86); finding 3, the off-peak week by hours (SP15 42.72 to 39.36, -7.9 percent; SPP North 19.08 to 16.61).
- **Data requests:** the one-hour shift of the on-peak block for NYISO and ISO-NE (hours ending 8 to 23 against 7 to 22), sized on the data machine as counts and percents only, for Samuel to see before any ruling (finding 5).
