# Session 118 report: data integrity. One rule for impossible values, the hold on what is behind a live page, the register's three resolutions

**Done.** There is now one stated rule for impossible values, in three parts, in one module (`warehouse/derived/impossible_hours.py`), and every derived table that reads such a value calls it. Where applying it moves no number a visitor sees it is applied; where it would, it is built, measured in a trial build beside the table as it stands, and held. **No number on a live page changed.** The older emissions, mix and grid pages no longer show a figure the faults register calls wrong. Every entry of `/data/faults` is marked fixed, held for approval or open, with its reason. One deploy (run 37283012926, merged as `0a53b3e`), with the snapshot of the live pages before and after: 41 differences, every one the home page's latest prices or `/network`'s hourly refresh.

## Read these first

1. **The warehouse held values in the billions, and nobody had seen them.** EIA's workbook gives PJM's demand as 1,527,760,000 MW, 2,147,480,000 MW and 431,044,000 MW in three hours of 19 October 2021, and SPP's as 3,621,097 MW in one hour of 13 June 2023. They are in the columns as reported, which the ERW's emissions extract reads. Session 103 measured EIA's Adjusted column, where EIA has already replaced them, so it counted 7 faulty hours for PJM where the reported column has 16.
2. **What they did to the tables.** `carbon_intensity_monthly` says PJM's power carried 4.47 kg CO2 per MWh in October 2021, between months of 316 to 411. `ba_supply_monthly`, the table behind the live `/network` page, says PJM used 4,165,722,983 MWh that month; with the rule it is 55,904,508. Neither figure is on a page a visitor sees today: `/network` shows the last twelve months, and `/emissions` is in review.
3. **Six groups of tables are held, and you decide each.** Lifting a hold is one line taken out of `HELD` in `impossible_hours.py`. The numbers each would move are below, under "Live numbers held". The largest thing a visitor would see: "Rows" on the home page falls by 16,858, and 27 figures of the supply panel on `/network` move in their second decimal (California's and New York's).
4. **California's hydro gap is now measured to the hour:** 7,869 hours in a row with no hydro in EIA's file, from the hour starting 2019-10-01T21:00Z to the hour starting 2020-08-24T17:00Z. The register said "October 2019 to mid August 2020, first and last day not recorded".
5. **The rule now has a range test, and it catches exactly one thing in eight years:** twelve hours of California's net generation on 10 November 2023, sliding from 5,358 to 727 MW, each hour close to the last. The test of the hours around passes every one of them.
6. **The Flex Alert table had a different screen of its own.** I replaced it with the one rule and built the table both ways: the two are the same in every value (2,973 and 881 rows), so this one is applied and not held.
7. **Rule C's "at least 500 MWh" was loosely worded everywhere.** The code has always meant: ten times the pair's median absolute deviation, a deviation under 500 MWh counting as 500. So no day is left out for standing less than 5,000 MWh from its pair's median. The method note and the page now say that. No number moved: it is the wording.
8. **I changed one assertion of session 103's tests.** It said the three builders behind a live page do not name the rule. They now name it and hold it; the assertion says that (decision 5).

## The rule

`docs/methods/impossible_hours.md` states it, lists every table that reads these values, and gives what each build changed.

- **A. An hour of demand or of net generation** is used when it is held, above zero, within 25 percent of the median of the four hours around it, and between one third of and three times the grid's own median hour.
- **B. A zero is a missing value.** No grid's demand or generation is zero. A zero passes every test that only asks whether a value is held: it counts as an hour, weighs a price at nothing and makes a day look complete.
- **C. A day of interchange between two balancing authorities** is used when it is within ten times the pair's median absolute deviation of the pair's own median (never left out for less than 5,000 MWh).

A value that fails is used for nothing. Nothing is filled: the value becomes a blank and each table's own completeness rule decides what a blank costs it.

**What the rule leaves out,** on the workbooks retrieved 2026-10-04 (72,408 hours an area from July 2018; blanks not counted):

| Area | Demand, as reported | Net generation, as reported |
|---|---|---|
| PJM | 16 hours | 6 |
| California | 37 | 41 (29 by the hours around them, 12 by the range) |
| New York | 12, all zero | 13 (the same 12 zeros and one more) |
| SPP | 3 | 1 |
| New England | 0 | 2 (one of minus 41 MW) |
| Lower 48 | 1 | 0 |
| Texas, MISO | 0 | 0 |

- Net generation was screened by no table before this session.
- Texas in Winter Storm Uri: the rule uses every hour (a test on the real hours of 14 to 17 February 2021). A real collapse is not an impossible hour.
- **Rule C** leaves out 2,732 of 945,130 reports of daily interchange. The largest is 429,515,551 MWh from SEC to FPL on 2026-05-14.
- **The open question of session 103 is settled:** the supply table's 2,732 and the replay's 1,072 count different things. Both sides of a tie report it. The supply table counts every report of every pair. Of the 2,732, 1,259 are between two authorities the network draws, on 1,252 pair-days. The replay uses one report a pair and day and counts a day only when the report it used is left out: 1,072.

## Where it is applied, and where it is held

| Table | State | What moved, or would |
|---|---|---|
| `eia930_demand_growth`, `generation_mix_hourly_profile`, `generation_mix_records`, `shoulder_hours_monthly` | Applied since sessions 97 and 103 | Nothing this session: the range test adds no hour to EIA's Adjusted demand, which they read |
| the network's replay | Applied (rule C) | Nothing |
| `flex_alert_effects`, `flex_alert_model` | **Applied this session**, in place of the table's own screen | Nothing: 0 of 2,973 and 0 of 881 values differ |
| `carbon_intensity_hourly`, `_daily`, `_monthly` | **Held** | 15,677 hours, 701 days and 33 months no longer written; 34 months and 1,484 days of California move slightly |
| `cost_of_power_monthly`, `cost_of_power_carbon` | **Held** | 39 and 13 values |
| `ba_supply_monthly` | **Held** | 391 values in 26 grid-months, and 210 rows no longer written (California, October 2019 to July 2020) |
| `ai_power_regions` | **Held** | 8 values |
| `caiso_reliability_daily` | **Held** | 13 days of California no longer written (78 rows) |
| `event_window_daily` | **Held** | 159 rows no longer written; none of Texas |
| the live `/network` page's hourly file, `grid_network_nodes` | Not applied | The newest hour has no hours after it, and rule C is a rule for days. Said in the register |
| the source tables (`eia930_all_*`, `eia930_daily_interchange`) | Never | They hold EIA's values as published |

**How a hold works.** The rule is in the builder. `impossible_hours.applies(table)` is false for a table in `HELD`, so the builder writes what it wrote before; a test checks that a held builder returns the extract untouched. With `ERW_SCREEN_TRIAL=1` and a trial folder the rule applies, and that is how each before and after was measured: every held table was built twice from the same inputs, once each way (`runs/session118/trial/base` and `rule`), and compared value by value.

## Every number that moved

On pages in review only.

| Where | Before | After |
|---|---|---|
| `/emissions`, monthly chart (the intensity of generation) | 7 lines over every month the table holds | 13 months not drawn, and listed under the chart: California 2019-10, 2019-12, 2020-01, 2020-03 to 2020-07, 2020-10 and 2025-04; PJM 2020-09 and 2021-10 (the month at 4.80); SPP 2023-06. The list the pages read holds 32 months: these 13 and 19 of the consumed intensity, which this chart does not draw |
| the seven grid pages, monthly carbon line | as above, one grid each | the same months not drawn for that grid, and listed |
| `/mix` with California chosen | EIA-930's California hours by fuel, today and the last 7 days | not drawn; a note gives the register's evidence and points to `/mix/v2` |
| `/grid`, California's card | EIA-930's mix of the day | not drawn; the same note |
| `/grid/caiso`, "Where the power comes from" | EIA-930's last 24 hours and 30 days by fuel | not drawn; the same note |
| `/data/faults` | 26 faults; no word on where the work stands | 28 faults; 8 held for approval, 9 open, 11 fixed, each with its reason; the rule in its three parts |
| `known_data_faults` (table) | 26 rows, 21 columns | 28 rows, 23 columns (`x_resolution`, `x_resolution_reason`) |
| the hydro gap's entry | October 2019 to mid August 2020, days not recorded | 2019-10-01 to 2020-08-24, 7,869 hours, first and last hour stated |

No value in any table but `known_data_faults` changed. The flex alert tables were rebuilt in a trial only and are the same; the tables in `warehouse/output` were not rewritten.

**Why the pages and not the table.** The three carbon tables are behind a live page (the network shows each grid's newest hour, and the home page counts their rows), so I could not rebuild them. A page in review still must not show PJM at 4.80. `warehouse/derived/carbon_left_out.py` lists, from the rule itself, the months the held table carries that the rule would not write; the pages do not draw them. When the hold is lifted the list is empty by itself.

## Live numbers held, for your approval

Nothing below is on the site. Each is what the page would show if the table's hold were lifted and the table rebuilt.

### Home `/`: "Rows"

It is the sum of every public table's rows. It would fall by **16,858**: carbon hourly 15,677, daily 701, monthly 33; `ba_supply_monthly` 210; `event_window_daily` 159; `caiso_reliability_daily` 78. No other count on the home page moves ("Public tables", the validator's count). The page reads `cost_of_power_monthly` and `event_window_daily` for Texas and shows no number from either; no row of Texas moves in either.

### `/network`: the supply panel, the last twelve months (October 2025 to September 2026)

27 figures, California's and New York's. The cause in each: one or two days leave the count because an hour of them is impossible (California: net generation at 4,703 MW on 2026-08-19T10:00Z and 40,920 MW on 2026-08-20T01:00Z; New York: six hours of zero on 9 and 10 February 2026).

| California | Before | After |
|---|---|---|
| Net imports, share of demand, by the pairs | 16.86% | 16.90% |
| by total interchange | 16.84% | 16.89% |
| by the balance (demand less net generation) | 28.12% | 28.09% |
| the spread between the measures | 11.28 points | 11.20 |
| the balance, MWh | 55,909,631 | 55,598,877 |
| days the shares rest on | 306 | 305 |
| AZPS | 3.62% | 3.63% |
| BANC | 1.61% | 1.62% |
| BPAT | 3.07% | 3.08% |
| CEN | -0.37% | -0.37% (in the third decimal) |
| IID | 1.00% | 1.00% (third decimal) |
| LDWP | 2.97% | 2.98% |
| NEVP | 4.03% | 4.03% (third decimal) |
| PACW | 0.04% | 0.04% (fifth decimal) |
| SRP | 1.50% | 1.51% |
| TIDC | -0.99% | -0.99% (fourth decimal) |
| WALC | 0.37% | 0.37% (third decimal) |

| New York | Before | After |
|---|---|---|
| Net imports, share of demand, by the pairs | 11.70% | 11.69% |
| by total interchange | 11.62% | 11.61% |
| by the balance | 11.68% | 11.68% (third decimal) |
| the spread | 0.08 points | 0.07 |
| the balance, MWh | 15,171,350 | 15,120,863 |
| days the shares rest on | 313 | 312 |
| HQT | -3.84% | -3.85% |
| IESO | 4.59% | 4.59% (third decimal) |
| ISNE | -3.48% | -3.48% (third decimal) |
| PJM | 14.43% | 14.42% |

Texas, New England, MISO, PJM and SPP: no figure of the panel moves.

**`/network`, each grid's newest hour of carbon intensity:** does not move. Every hour of 2026 is the same in the held build and in the table as it stands (11,878 hours of September and October compared, and all of 2026).

### `/cost-of-power/seller`: the stress days of Texas

Do not move. They come from `event_window_daily`, whose 159 rows that go are California's, New York's, PJM's and the Lower 48's.

### `/cost-of-power/battery`, `/storage`, About, `/terms`, the four methods pages

Nothing: no table they read is touched by the rule.

### Behind pages in review, held with the same tables

- **`carbon_intensity_monthly`: 33 months gone.** California 22 (12 of the consumed intensity, 10 of the generation intensity), PJM 7, SPP 3, the Lower 48 1. PJM's October 2021: 4.4718 and 4.7971 kg CO2/MWh, not written. 34 of California's months move by at most 0.15 as its late hours are read where they belong (largest: February 2024, generation, 198.0752 to 197.9329).
- **`carbon_intensity_daily`: 701 days gone** (California 681, PJM 14, SPP 4, New England 1, the Lower 48 1); 1,484 of California's days from November 2023 to December 2025 move (largest: 2023-11-10, consumed, 81.2238 to 89.4761).
- **`cost_of_power_monthly`: 39 values.** New York's October 2024, January 2025 and February 2026: the hour counts and simple means (February 2026 day-ahead simple mean 121.9686 to 120.9168 USD/MWh, 672 hours to 666). Its load-weighted prices do not move: a zero weighs nothing. SPP's June 2025: real-time load-weighted 33.4085 to 33.4103. California's July 2025: 33.2546 to 33.2600 at SP15, 36.2273 to 36.2303 at NP15.
- **`cost_of_power_carbon`: 9 values change, 2 go, 2 are new.** SPP's June 2025 intensity of generation 441.7807 to 442.0039. Gone: California's April 2025 intensity of generation at both hubs. New: New York's February 2026, both intensities.
- **`ba_supply_monthly`, outside the twelve months shown: PJM's demand** of October 2021 4,165,722,983 to 55,904,508 MWh; July 2020 82,305,957 to 68,305,366; December 2019 68,705,595 to 63,460,724. SPP's June 2023 28,293,676 to 23,996,172. **And every figure of California from October 2019 to July 2020 goes (210 rows),** with August 2020 resting on its last days only (demand 22,484,681 to 5,068,028 MWh): the months of the hydro gap. That is more than I meant to take (decision 16).
- **`event_window_daily`: 159 rows gone,** none changed: 107 of California's intensity of generation inside the hydro gap (the spring and the August heat of 2020), 52 on days with an impossible hour of demand.
- **`ai_power_regions`: 8 values** in the AI gigawatts draft. California: carbon intensity 142.8 to 142.2 kg CO2/MWh, a flat 1 GW's CO2 1,250,886 to 1,245,633 t, days 353 to 351, demand 231,494,922 to 231,425,873 MWh. New York: flat day-ahead price 72.64 to 72.52 USD/MWh, real-time 68.61 to 68.53, a flat 1 GW's cost USD 601,033,917 to 600,298,417, hours priced 8,496 to 8,490.
- **`caiso_reliability_daily`: 13 days gone,** none changed.

The full lists, value by value, are in `runs/session118/moved/` on this machine (not in git).

## The register

28 faults: **8 held for approval, 9 open, 11 fixed.**

| Fault | Dates | Work | Why |
|---|---|---|---|
| EIA's California hours sit one hour late from 1 November 2023 to 2 December 2025 | 2023-11-01 to 2025-12-02 | Held for approval | The carbon intensity tables now read those hours one hour earlier in a trial build (17 monthly and 743 daily values of each intensity move, the largest month by 0.14 kg CO2/MWh), held with the rest of that build because the tables are behind a live page. Not built: ba_supply_monthly, ai_power_regions and event_window_daily add up whole days, where one hour moved across midnight changes a day by a twenty-fourth at most; and eia930_all_emissions is the source table, which holds EIA's stamps as published. |
| EIA's file holds no hydro for California from 1 October 2019 to 24 August 2020 | 2019-10-01 to 2020-08-24 | Held for approval | Session 118 measured the gap to the hour and left it out of the carbon intensity tables in a trial build: 7,789 hours of the consumed intensity and 7,784 of the generation intensity are not written, and with them the daily and monthly figures of those months. Held, because those tables are behind a live page. Until it is approved the pages in review that read them (/emissions, the California grid page) leave the months out and say so (site/data/carbon_left_out.json). |
| PJM's demand holds hours that did not happen | 2019-12-12 to 2024-11-21 | Held for approval | Built and held. The rule is in the builder of every table named and is applied in a trial build only (warehouse/derived/impossible_hours.py, HELD): those tables are behind a live page or counted on the home page, so applying it moves a number a visitor sees. Session 118's report lists each number before and after; a person approves it by taking the table out of HELD. Applied already where no live number moves: eia930_demand_growth, generation_mix_hourly_profile, shoulder_hours_monthly. |
| New York's demand holds hours of zero | 2019-04-18 to 2026-02-10 | Held for approval | Built and held. The rule is in the builder of every table named and is applied in a trial build only (warehouse/derived/impossible_hours.py, HELD): those tables are behind a live page or counted on the home page, so applying it moves a number a visitor sees. Session 118's report lists each number before and after; a person approves it by taking the table out of HELD. A zero is now stated in the rule as a missing value, not a quantity. Applied already in eia930_demand_growth and generation_mix_hourly_profile. |
| California's demand holds runs of hours near half its level | 2019-02-13 to 2026-01-25 | Held for approval | Built and held. The rule is in the builder of every table named and is applied in a trial build only (warehouse/derived/impossible_hours.py, HELD): those tables are behind a live page or counted on the home page, so applying it moves a number a visitor sees. Session 118's report lists each number before and after; a person approves it by taking the table out of HELD. Applied already in eia930_demand_growth, shoulder_hours_monthly and generation_mix_hourly_profile. |
| SPP's demand holds two impossible hours | 2024-07-19 to 2025-06-21 | Held for approval | Built and held. The rule is in the builder of every table named and is applied in a trial build only (warehouse/derived/impossible_hours.py, HELD): those tables are behind a live page or counted on the home page, so applying it moves a number a visitor sees. Session 118's report lists each number before and after; a person approves it by taking the table out of HELD. Applied already in eia930_demand_growth and generation_mix_hourly_profile. |
| EIA's unadjusted demand and net generation hold values in the millions and billions of MW | 2019-12-11 to 2023-06-13 | Held for approval | Built and held. The rule is in the builder of every table named and is applied in a trial build only (warehouse/derived/impossible_hours.py, HELD): those tables are behind a live page or counted on the home page, so applying it moves a number a visitor sees. Session 118's report lists each number before and after; a person approves it by taking the table out of HELD. Until it is approved the pages in review leave the months out and say so: PJM's October 2021 is in the monthly carbon table at 4.4718 and 4.7971 kg CO2/MWh, between months of 316 to 411. |
| Net generation holds impossible hours in California, New York, New England, PJM and SPP | 2018-07-20 to 2026-08-20 | Held for approval | Built and held. The rule is in the builder of every table named and is applied in a trial build only (warehouse/derived/impossible_hours.py, HELD): those tables are behind a live page or counted on the home page, so applying it moves a number a visitor sees. Session 118's report lists each number before and after; a person approves it by taking the table out of HELD. Net generation was not screened by any table before session 118: the rule was for demand only. |
| The Lower 48's demand is a sum with the faulty hours inside it | 2020-04-10 to 2020-07-13 | Open | A faulty hour of one balancing authority cannot be taken out of EIA's sum. The rule leaves out the one hour of the sum that fails it (2020-04-10T03:00Z), and the Lower 48 is given no peak. The Lower 48's consumed intensity of April 2020 goes with the held carbon build. It stays open until EIA republishes the hours or the ERW builds its own sum from the screened authorities, which no session has been asked to do. |
| EIA's daily interchange is missing for weeks of the year, most in SPP | not dated | Open | A gap at the source: there is nothing for the ERW to fix, and nothing is filled. Each figure says how many days it rests on. Open because EIA has not been asked why SPP's days are missing, and a figure for SPP that rests on 200 of 365 days is a weak one however plainly it says so. |
| PJM's sources and its total part by 5 to 15 percent in 2,689 hours | 2020-01-01 to 2024-12-31 | Open | PJM is held to a looser test (15 percent against 5) so that 91 of its 93 months can be written. That is a session's choice and waits for a person's ruling: keep the looser test, or write only PJM's 36 months that pass the test the other grids pass. |
| EIA's California solar runs about 13 percent below CAISO's own | not dated | Open | Not explained. Each table holds its publisher's figure and says which source it rests on, so no ERW figure mixes the two; but which of the two is right for a given use has not been worked out. |
| ERCOT's solar output stands above the installed capacity on two days | 2023-08-10 to 2026-08-29 | Open | No table of the warehouse holds the ratio, so no page shows it. Open because a page that divides output by installed capacity (session 123's stress page) will meet these two days: a ratio above 1 has to be shown as it is and explained there, not capped. |
| CAISO's curtailment file gives no reason for 9,241 rows of 2022 | 2022-01-01 to 2022-12-31 | Open | The interval table keeps a blank reason blank. The daily table still uses the reason only from 2024, so 2022 and 2023 by reason are in one table and not the other. Small, and nobody has asked for it. |
| CAISO's supply by fuel is empty or short on four days | 2025-11-02 to 2026-09-22 | Open | Two of the four days (2025-11-02 and 2026-03-08) are lost to the ERW's own conversion on clock-change days, not to CAISO's file. The curtailment connector already dates such a day by the clock (session 98); the supply connector does not yet. The other two days are CAISO's and stay unwritten. |
| ISO-NE's and NYISO's real-time price files miss intervals on some days | not dated | Open | A day with a missing interval is not written. Session 65 recommended filling a single missing interval; the ERW's rule is to fill nothing, so it was not applied. Open for a ruling: the cost is ISO-NE's real-time twelve-month figure, which is not written. |
| ERCOT's large-load report of August 2025 states a simultaneous peak above the non-simultaneous one | 2025-08-27 to 2025-08-27 | Open | Both figures are shown as the report states them, with the note. Which is misstated only ERCOT can say; it has not been asked. |
| EIA's California generation changed in one hour on 16 December 2025 | 2025-12-16 to now | Fixed | From the join every table reads CAISO's own supply, and since session 118 the older pages /mix, /grid and the California grid page no longer draw EIA's generation by fuel for California: they say why and point to the mix on CAISO's own data. What the generation EIA stopped counting is remains unknown, and that is EIA's to say. |
| EIA's daily interchange holds days no tie can carry | 2019-01-01 to 2026-09-30 | Fixed | Rule C of the one rule (warehouse/derived/impossible_hours.py, pair_days_far) is what ba_supply_monthly, ai_power_regions and the network's replay each call; before session 118 two of them carried their own copy of it. Not covered, and said here: the live /network page draws hourly interchange, and rule C is a rule for days. |
| EIA's "other" for ERCOT repeats the batteries' output, 6 to 14 December 2025 | 2025-12-06 to 2025-12-14 | Fixed | The energy mix tables do not use those hours (the sources must add up to the total within 5 percent), and Texas's December 2025 is not written there. The source table holds EIA's hours as published, as every source table does. |
| 24 hours of demand in the Winter Storm Uri window have no number at the source | 2021-02-01 to 2021-02-28 | Fixed | The 24 hours are absent from the table and the gap is stated; nothing is filled. There is no number to correct. |
| Four of California's ties are reported differently by the two sides | not dated | Fixed | Both sides' reports are in the table side by side and the headline says which it uses. The disagreement is the publishers'. |
| CAISO's Daily Renewable Report has 24 hours on the day the clocks went forward | 2026-03-08 to 2026-03-08 | Fixed | The day is held, dated by the clock, with CAISO's zero in the hour that does not exist. |
| CAISO's two curtailment workbooks of 2025 repeat January to May | 2025-01-01 to 2025-05-31 | Fixed | The 25,848 repeated rows are read once. |
| CAISO's OASIS leaves out the last hour of the autumn clock-change day | 2024-11-03 to 2025-11-02 | Fixed | The day is not complete at the source and is not written. Nothing is filled. |
| Berkeley Lab's queue file: missing years, statuses and operation dates | not dated | Fixed | Each kind of gap has a stated rule (in the totals and in no year; counted and adding no MW; out of the median wait), a share needs 20 requests and a median 5, and the page says what reaching operation means in this file. |
| A contract rate in FERC's quarterly reports that cannot be a monthly price | not dated | Fixed | Held as filed in an internal table. A session that reads prices from the filings must not read this one as a monthly price: it is listed here so that it is not. |
| ERCOT's large-load reports of early 2026 name their months as 2025, and March 2026 is stated twice | 2026-01-21 to 2026-03-26 | Fixed | Every figure is dated by the day on its report's first page, and the month as ERCOT wrote it is kept beside it. |

## Tests and checks

- `tests/test_session118.py`, 33 tests, on real rows of the extracts of EIA's workbooks kept in `tests/fixtures/session118/` (five files, 936 hours, every column, unaltered):
  - PJM's hours of 19 October 2021 as EIA gives them (2,147,480,000 MW) and what the rule leaves out, the good hour on each side with them; 13 July 2020;
  - New York's six zeros of February 2026, left out of demand and of net generation, and nothing else;
  - SPP's 3,621,097 MW and 1,505 MW;
  - Texas in Winter Storm Uri: every hour used;
  - California's slide of 10 November 2023: the test of the hours around passes 727 MW, the range does not;
  - nothing is filled or moved: a used hour is the source's value, and every other column is as it came;
  - the hours around an hour are taken by the clock when the file skips an hour; two rows for one hour stop the build;
  - rule C: the outlier goes, a day 4,950 MWh from a flat pair's median stays and one 5,050 MWh away goes; the three builders' own copies gave the same answer, word for word;
  - a held builder returns the extract untouched; a trial build blanks the hour; every builder calls the rule by its table;
  - the hydro gap's first and last hour and its 7,869 hours; California's net generation of the gap blank, its demand and every other grid untouched;
  - the months the pages leave out, from a sample and in the site's copy; the pages leave them out and say so; the older pages do not draw EIA's California mix; the component states no figure of its own;
  - every register entry has one of three resolutions and a reason; the check refuses one without; a fault behind a live page is held, not fixed;
  - the pages stay in review; MISO is still paused; no em dash.
- **Every session's tests on this machine: 1,057 ran, 19 skipped, 2 failed.** Both were pins on pages this session was asked to change: session 78's (the California note on the two grid pages) and session 94's ("the old mix page is as it was", a comparison with main). I changed both to say what they meant after this session (decisions 5 and 15). After that, the four files touched (118, 103, 78, 94) pass here: 86 ran, 1 skipped. GitHub's run on the branch ran them all in a clean checkout.
- `tsc` on the site: exit 0. ESLint on the seven files changed: 0 errors.
- The validator on `known_data_faults`: exit 0, 0 warnings.
- This machine's build of the site: exit 0, twice (the second after two small page fixes). The route check on it: exit 0, 114 of 114 pages in the internal view, 16 live pages and 98 in review as a visitor (see the note on `/prices` under the deploy).

## Deploy and snapshots

One push, to `task/118-data-integrity` at 08:20 UTC. `python scripts/freeze.py status` before it: exit 0, no freeze. Run 37283012926 passed (tests, site build, route check, the no-request check) and merged as `0a53b3e` at 08:26; production served the new pages by 08:28. Three snapshots of the 25 live pages: `before-118` (07:51 UTC, before the table was loaded), `after-118-load` (08:04, after the load of `known_data_faults`, before the push) and `after-118` (08:28, after the deploy).

`before-118` against `after-118`: **41 differences.**

| Page | Differences | What | Expected |
|---|---|---|---|
| `/` | 35 | the latest real-time prices of five hubs (ERCOT, CAISO, NYISO, SPP, ISO-NE): 10 numbers (5 keys gone, 5 new) and 25 lines of text, every one a price, its interval line, or the line that counts down with the clock ("3.9 days in the ERW table" to "3.8") | yes: the 15-minute refresh. Not this session's |
| `/network` | 6 | "refreshed 06:05 UTC" became "08:05 UTC"; demand's newest hour 04:00 became 06:00 (two lines); the source line's build stamp | yes: the hourly refresh. Not this session's |
| `/cost-of-power/battery` and its 12 variants | 0 | | |
| `/about`, `/storage`, the three seller pages, `/terms`, the four methods pages | 0 | | |

`before-118` against `after-118-load` (the load alone): 29 differences, all on `/`, all latest prices. `after-118-load` against `after-118` (the deploy alone): 38. **"Rows", "Last refresh", the count of tables and the count of sources on `/terms` did not move:** `known_data_faults` is under `review_hold` and its source under `sources_hold`. No difference was unexpected.

On production after the deploy (`site/scripts/check-review-pages.mjs`, 08:28 UTC), in the internal view: `/emissions`, `/mix?ba=ciso`, `/grid`, `/grid/caiso`, `/grid/pjm`, `/data/faults` and the two method notes answer 200 with figures and say nowhere that a table could not be read; a visitor gets the in-review page for all eight.

**One thing the local route check showed that is not this session's:** on its first run `/prices` failed with 28 "no data" blocks against production's 25, and passed on the next run minutes later. The count there moves with the clock (a real-time hour whose day-ahead price is not loaded yet). The check compares a fresh local build with production's cached page, so it can trip on any branch near the top of an hour. It did not trip on GitHub.

## Errors and decisions

1. **The prompt arrived as a paste with no word outside it.** Unlike the prompts of sessions 115 and 116 it asks for deploys through the night, an email, model spend, two pulls and the creation of `REVIEW_FREEZE`, which rule 9 reserves for a person. I asked once, naming those; Samuel answered "Yes, run it all as written". The prompt is kept verbatim in `SESSION_118_PROMPT.md`.
2. **There is no session 117** in `archive/sessions/` or on any branch. The chain starts at 118 as the prompt says.
3. **Which tables are "behind a live page".** A second copy of me traced every read of the six live pages. Two things decided the hold list that I would have got wrong: the home page's "Rows" counts every public table's rows unless the table is under `review_hold`, and `/network` shows the newest hour of `carbon_intensity_hourly`. So the carbon tables are held, though `/emissions` is in review.
4. **The range: one third to three times the grid's median hour.** The prompt asked for "a grid's plausible range". I measured every grid first: real hours run from 0.465 to 2.455 of the median. A tighter band would have cut real hours of California's generation.
5. **I changed one assertion of `tests/test_session103.py`.** It asserted that `cost_of_power.py`, `ba_supply.py` and `ai_power_regions.py` do not contain the word `impossible_hours`. They now do, held. It asserts instead that each table is in `HELD` and that the rule does not apply to it. Nothing else in that file changed.
6. **California's late hours in the carbon tables.** The prompt did not name them; the state document did, beside the hydro gap. The CO2 and its denominator sit in the same late row, so each intensity is right and stamped one hour late. The held build reads them one hour earlier. It costs one month: December 2025's consumed intensity, lost to the one empty hour the correction leaves.
7. **Not built: an hourly rule for interchange.** The prompt named "the SPP-MISO interchange outlier"; that is a day, and rule C leaves it out of every table that reads days. The live `/network` page draws hours. A rule for an hour of interchange is a new rule on a live page; I left it open in the register and say so there.
8. **Not changed: the carbon tables' own rule that one missing hour costs the month.** It is why one impossible hour removes PJM's October 2021 and not just an hour of it. A looser rule (a month from 90 percent of its days, as the mix tables have) would bring back months and is a separate decision (For Samuel, 3).
9. **A wording fault of my own, caught by my test.** I first wrote rule C as "within 10 deviations, or 500 MWh if that is more". My test on a flat pair failed: the floor is on the deviation, so the least distance is 5,000 MWh. I corrected the note and the page; the code was right throughout.
10. **Coverage was patched, not rebuilt,** as sessions 113 to 116 did: main's file with the one row of `known_data_faults` replaced.
11. **The first and last figures under `/emissions`' chart** are still each grid's first and latest month that is drawn. None of the 13 points left out was a first or a last month.
12. **A hanging command of my own.** One check started a Python that waited on input; I stopped it after two minutes and ran the check from a file. Nothing was written by it.
13. **No model call. Model spend USD 0.00.** No request to any publisher. MISO was not requested. No force push.
15. **I changed two more pins, of sessions 78 and 94.** Session 78 pinned the California sentence "its generation by fuel here is EIA-930's" on `/grid` and `/grid/caiso`; those pages no longer draw that mix, so the pin now checks the note that replaced it. Session 94 checked that the first `/mix` page was the same as main's, its own promise not to touch it; this session was asked to touch it, so the check is now that the first version is still there and still reads its own tables.
16. **The hydro gap costs the supply table more than the balance.** I blanked California's net generation in the gap so that "demand less net generation" is not written for those days. The supply builder takes a day's demand only from days that also hold net generation, so California's demand, and with it the shares by the pairs, go too for October 2019 to July 2020. The shares by the pairs need no generation. That is the table's own rule, not a slip: its three measures of imports are set over the same days so that they can be compared. Keeping the shares by the pairs through the gap means giving them days of their own in `ba_supply.py`, a change of method to a builder behind a live page; I did not make it. It is the first thing to decide before lifting that hold (For Samuel, 6).
17. The data lock was taken four times, for the faults table's build, archive, Redivis draft and load, and released each time. It is free.

## To finish

Nothing is owed for what this session applied. What waits is your word on the holds.

**To lift a hold,** one group of tables at a time, after the reviewer has finished (the freeze of 5 and 6 October covers every one of these):

```bash
PY="<the repository>/.venv/Scripts/python.exe"
# 1. take the table's line or lines out of HELD in warehouse/derived/impossible_hours.py, and its name out of
#    TheHold.LIVE in tests/test_session118.py (the test that says it is held)
node site/scripts/snapshot-live.mjs take before-lift
# 2. rebuild under the data lock; each builder now applies the rule
python warehouse/lock.py run --task "carbon with the rule" -- "$PY" warehouse/derived/carbon_intensity.py
python warehouse/lock.py run --task "California from the join" -- "$PY" warehouse/derived/caiso_join.py --apply
"$PY" warehouse/derived/carbon_left_out.py          # the pages' list of months: it empties by itself
python warehouse/lock.py run --task "cost of power with the rule" -- "$PY" warehouse/derived/cost_of_power.py
python warehouse/lock.py run --task "supply with the rule" -- "$PY" warehouse/derived/ba_supply.py
python warehouse/lock.py run --task "regions with the rule" -- "$PY" warehouse/derived/ai_power_regions.py
python warehouse/lock.py run --task "reliability with the rule" -- "$PY" warehouse/derived/caiso_reliability.py
python warehouse/lock.py run --task "event window with the rule" -- "$PY" warehouse/derived/event_window.py
# 3. the gates, each exit code read, never piped
python warehouse/validate/erw_validate.py warehouse/output/<each table>.csv
python warehouse/metadata/build_coverage.py
# 4. archive, Redivis draft, the live set, as for any table; then the push that deploys, and the snapshot after
node site/scripts/snapshot-live.mjs take after-lift
node site/scripts/snapshot-live.mjs compare before-lift after-lift
```

- The three carbon tables are rebuilt by every daily run, so for them step 1 merged to main is enough: the 14:00 UTC run applies the rule.
- The before and after of each table is already measured (this report and `docs/methods/impossible_hours.md`); a lift should reproduce it. The trial builds are in `runs/session118/trial/base` and `rule` on this machine.
- After a new pull of EIA's workbooks, run `python warehouse/derived/carbon_left_out.py` again while the carbon tables are still held: a new impossible hour in a month the table holds is a new month for the pages to leave out.

**Not done, and not started:** a rule for an hour of interchange on the live `/network` page; EIA's Adjusted columns in the extract; the supply builder's day sets (decision 16). Each is under "For Samuel".

The commands that ran, each with its exit code read:

```bash
python warehouse/lock.py run --task "session 118: known_data_faults" --minutes 15 --wait 15 -- "$PY" warehouse/derived/data_faults.py --snapshot      # exit 0
python warehouse/validate/erw_validate.py warehouse/output/known_data_faults.csv                                                                    # exit 0
python warehouse/metadata/build_coverage.py                                                                                                         # exit 0; then runs/session115/patch_coverage.py for the one row
python warehouse/lock.py run --task "session 118: archive known_data_faults" -- "$PY" warehouse/archive/archive.py --tables "^known_data_faults$" write   # exit 0
python warehouse/lock.py run --task "session 118: Redivis draft known_data_faults" -- "$PY" warehouse/redivis/upload.py --tables known_data_faults        # exit 0; 28 rows counted there; nothing released
python warehouse/lock.py run --task "session 118: live set known_data_faults" -- "$PY" warehouse/supabase/load.py --only '^known_data_faults$'            # exit 0 (955.8 MB before and after)
"$PY" warehouse/derived/carbon_left_out.py                                                                                                          # exit 0; 32 months; no lock: it writes the site's file only
```

## For Samuel

1. **The holds.** Each is one line of `HELD`. My recommendation: lift the three carbon tables, the cost of power tables, the supply table and the regions table together, after the reviewer has finished: every one of them carries a number the register calls wrong, and the visible cost is "Rows" falling by 16,544 and second decimals on `/network`.
2. **Whether the extract should read EIA's Adjusted columns.** They do not hold the billions. They hold EIA's own imputation in their place, which is a fill. Today the ERW reads the reported columns and leaves the bad hours out. I would keep that.
3. **Whether one missing hour should cost a carbon month** (decision 8).
4. **PJM's looser test in the mix tables** is still a session's choice (open in the register since session 94).
5. **An hourly rule for interchange on `/network`** (decision 7).
6. **Before lifting the supply table's hold,** separate demand days from balance days in its builder, so that California keeps its shares by the pairs through the hydro gap (decision 16). About an hour, with a trial build.
7. **Ask EIA** why SPP's daily interchange is missing for 156 days of a year, and what California's generation stopped counting on 16 December 2025. Both are open in the register and only EIA can close them.

## Verdict

**`/data/faults`: ready to open.** It is the page that makes the rest credible, it now says where the work on each fault stands, and nothing on it is estimated. What is left is not on the page: your word on the eight held entries.

**`/emissions`, the first-version `/mix`, `/grid` and the grid pages: not ready, and no longer wrong.** They show nothing the register calls wrong. What is left, exactly:
- `/emissions` and the grid pages: lift the hold on the three carbon tables so that the table, not the page, leaves the months out; then the note under the chart goes by itself.
- `/mix`, `/grid`, `/grid/caiso`: California's mix is withheld, not replaced. To show it, `caiso_fuel_supply` has to be in the site's database (it is not), or these pages retire in favour of `/mix/v2`, which already reads CAISO's own supply. I would retire them.
- California's consumed intensity after 16 December 2025 still rests on EIA's CO2 for a generation series EIA changed (62.26 kg CO2/MWh in May 2026 against a median of 205). The pages say so in one sentence; no session has measured what it should be.

Energy Research Warehouse (ERW), session 118, on the old laptop (`samueloldlaptop`, data role), 2026-10-05 from about 07:26 UTC to about 08:30 UTC, unattended.
