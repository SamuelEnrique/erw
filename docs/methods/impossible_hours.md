# The rule for impossible values

EIA-930 holds values that did not happen: PJM's demand at 2,147,480,000 MW, New York's at zero, California's net
generation sliding to 727 MW, a day on which SPP sends MISO more than SPP uses. This note states the one rule the ERW
uses to leave them out, every derived table that reads such a value, where the rule is applied and where it is built
and held, and what it changed. Code: `warehouse/derived/impossible_hours.py`. The faults themselves, with their dates,
are in the table `known_data_faults` and on the page `/data/faults`.

Session 103 wrote the rule for an hour of demand. Session 118 made it the one rule for every impossible value: it now
covers net generation, has a range test for runs of faulty hours, states the zero rule on its own, and holds the rule
for a day of interchange, which three builders had each carried a copy of.

## The rule

**A. An hour of demand or of net generation** is used when it is

1. held (not blank),
2. above zero,
3. within 25 percent of the median of the four hours around it: the two before and the two after, those of them that
   are held and above zero, and
4. within the grid's own range: between one third of and three times the median of the grid's hours that pass the
   first three tests, over the history read.

**B. A zero is a missing value.** A grid's demand or net generation is never zero, so an hour at or below zero is a
blank and not a quantity. This is test 2 of A, stated on its own because a zero passes every test that only asks
whether a value is held: it counts as an hour, weighs a price at nothing, and makes a day look complete.

**C. A day of interchange between two balancing authorities** is used when it is within ten times the pair's median
absolute deviation of the pair's own median, over the history read. A deviation under 500 MWh counts as 500, so no day
is left out for standing less than 5,000 MWh from its pair's median.

A value that fails is used for nothing. **Nothing is filled, smoothed or replaced:** the value becomes a blank, and each
table's own completeness rule decides what a blank costs it (in the shoulder hours a day short of an hour is not a
complete day; in the carbon tables a day short of an hour is not written and neither is its month; in the supply table
a day is held only when every hour of it is).

**Why a quarter.** The steepest real ramps of these grids move demand about a tenth in an hour. No real hour stands a
quarter away from the four around it. Net generation follows demand less trade, and passes the same test: in Winter
Storm Uri, when Texas shed load, the rule uses every hour (a test on the real hours of 14 to 17 February 2021).

**Why one third and three times.** Measured on every grid's hours from July 2018 to 3 October 2026. Demand: the
lowest hour that passes the first three tests is 0.465 of its grid's median (New England) and the highest 2.086
(California). Net generation runs wider where a grid imports much of its power: 0.497 to 2.184 outside California, and
California's highest hour is 2.455. The range sits outside all of these. Over the whole history it leaves out twelve
hours and no others: California's net generation of 10 November 2023, sliding from 5,358 to 727 MW, each hour close to
the last, which is what the hours around cannot catch.

**Not for a single source.** Solar, wind and battery output move further than a quarter in an hour by nature, and are
zero for real. The energy mix tables test an hour of generation by fuel another way: its sources must add up to its
total, and a main source may not be blank (`warehouse/derived/mix_profile.py`).

## What the rule does not catch

- **A faulty hour inside a sum.** The Lower 48's demand is EIA's sum over every balancing authority. PJM's 224,345 MW
  of 2020-07-13T22:00Z is inside the Lower 48's 776,575 MW of the same hour, which stands 12 percent above the hours
  around it and passes. So the Lower 48 is given an average and no peak.
- **A run of faulty hours at a believable level.** Three or more in a row make their own median, and the range only
  catches a run that leaves the band.
- **Good hours between two faulty ones** are left out with them: their neighbours' median is pulled by the faults.
  In California's spring of 2019 this costs a few good hours, and on 19 October 2021 it costs PJM the hour before and
  the hour after its three hours in the billions.
- **An hour of interchange.** Rule C is a rule for days. The live `/network` page draws hourly interchange unscreened.

## Two columns, two counts

EIA's workbook holds each quantity three times: as reported (`Demand`, `Net generation`), as EIA imputed it, and
`Adjusted`, where EIA has put its own imputation in place of a value it judged wrong.

- The energy mix, demand growth and shoulder tables read the **Adjusted** columns.
- The emissions connector's extract, which the carbon, cost of power, supply, regions, reliability, event and Flex Alert
  tables read, holds the columns **as reported**.

The reported columns hold more impossible hours. Session 103 measured the Adjusted column and found 7 for PJM; the
reported column has 16, three of them in the billions. Whether the extract should read the Adjusted columns is a
ruling to make: it would inherit EIA's fill.

## What it leaves out, measured on 2026-10-04

Held hours the rule does not use, from the extracts of the workbooks retrieved 2026-10-04 (hours from 2018-07-01;
72,408 an area). Blank hours are not counted here: they were always missing.

| Area | Demand, as reported | Net generation, as reported | Which |
|---|---|---|---|
| PJM | 16 | 6 | demand: 417,669 MW at 2019-12-11T19:00Z; 155,276 at 2019-12-12T21:00Z; 215,682 at 2020-04-10T03:00Z; 224,345 at 2020-07-13T22:00Z; 262,651 at 2020-07-24T15:00Z; 245,799 at 2020-07-27T21:00Z; 192,229 at 2020-07-28T16:00Z; 176,085 at 2020-07-29T20:00Z; 138,575 at 2020-08-13T12:00Z; 250,825 at 2020-09-03T20:00Z; five hours from 2021-10-19T01:00Z (1,527,760,000, 2,147,480,000 and 431,044,000 MW, and the good hour on each side); 56,260 at 2024-11-21T16:00Z. Net generation: 257,186 at 2020-09-03T20:00Z and the same five hours of 19 October 2021 |
| California (CAISO) | 37 | 41 | demand: 28 from 2019-02-13 to 2019-05-10; 7 from 2019-12-19 to 2019-12-22 (three of 14, 91 and 96 MW); 2020-10-08T18:00Z; 2025-07-31T20:00Z. Net generation: 29 apart from the hours around them (629 MW at 2018-07-20T18:00Z; 1,932 at 2019-08-25T20:00Z; 2019-10-03 to 2019-10-08; 2019-12-19 and 20; one each in March, May and October 2020; 2023-11-10; 2025-04-01; 2026-08-19 and 20), and 12 more on 2023-11-10 outside the range (a slide from 5,358 to 727 MW) |
| New York (NYISO) | 12 | 13 | zero in both columns at 2019-04-18T03:00Z; 2024-01-17T23:00Z; 2024-10-09T20:00Z and T21:00Z; 2025-01-15T22:00Z and T23:00Z; six from 2026-02-09T23:00Z to 2026-02-10T04:00Z. Net generation also 20,562 MW at 2025-01-15T20:00Z |
| SPP | 3 | 1 | 3,621,097 MW of demand and 3,617,992 of net generation at 2023-06-13T01:00Z; demand 24,991 at 2024-07-19T04:00Z and 1,505 at 2025-06-21T09:00Z |
| New England (ISO-NE) | 0 | 2 | minus 41 MW at 2021-03-01T04:00Z; 2,776 MW at 2021-03-02T04:00Z |
| Lower 48 | 1 | 0 | 525,129 MW at 2020-04-10T03:00Z |
| Texas (ERCOT), MISO | 0 | 0 | |

The list is `runs/session118/left_out.csv` on the data machine (not in git). On the Adjusted demand the counts are
those of session 103: PJM 7, California 38, New York 12, SPP 2, Lower 48 1, and the range test adds none.

**Rule C**, on `eia930_daily_interchange` (to 2026-09-30): 2,732 of 945,130 reports are left out. The largest is
429,515,551 MWh from SEC to FPL on 2026-05-14; SPP to MISO on 2026-07-21 is 2,159,056 MWh. The supply table states
2,732 and the network's replay 1,072, and session 103 recorded that nobody knew why they differ. Measured in session
118: they count different things. Both sides of a tie report it, so the table holds two reports of most pair-days. The
supply table counts every report of every pair. Of the 2,732, 1,259 are between two balancing authorities the network
draws, on 1,252 pair-days. The replay uses one report a pair and day (the first side's, the other side's when the
first is missing) and counts a day only when the report it used is left out: 1,072.

## California's hydro gap

EIA's file holds no hydro for California in every one of the 7,869 hours from the hour starting 2019-10-01T21:00Z to
the hour starting 2020-08-24T17:00Z (both included); the hour before holds 1,278 MW and the hour after 1,898 MW. EIA's
total leaves it out too. It is not an impossible value by the rule (the hours are believable, only short), so it has
its own constant, `impossible_hours.CISO_NO_HYDRO`, measured on the workbook retrieved 2026-10-04:

- the energy mix tables do not write those months (session 94: a main source may not be blank);
- the carbon builder leaves the hours out of both intensities, in the held build;
- the pages that read the carbon tables leave the months out and say so (below).

## Every table that reads these values

**Applied** means the table as it stands is built with the rule. **Held** means the rule is in the table's builder and
is applied only in a trial build (`impossible_hours.HELD`, `ERW_SCREEN_TRIAL=1`): the table is behind a page open to
visitors, or its row count is in the home page's "Rows", so applying the rule moves a number a visitor sees. A person
approves it by taking the table's line out of `HELD`; its next build then applies the rule.

| Table | Reads | Rule | State |
|---|---|---|---|
| `eia930_demand_growth` | Adjusted demand | A, B | Applied (session 97) |
| `generation_mix_hourly_profile`, `generation_mix_records` | Adjusted demand; generation by fuel | A, B on demand; its own sum test on generation | Applied (session 103) |
| `shoulder_hours_monthly` | Adjusted demand | A, B | Applied (session 103) |
| the network's replay (`site/public/network/daily_*.json`) | daily interchange; daily demand | C; a band of its own on daily demand | Applied (sessions 93, 109) |
| `carbon_intensity_hourly`, `_daily`, `_monthly` | demand and net generation as reported | A, B; the hydro gap; California's late hours | **Held** |
| `cost_of_power_monthly`, `cost_of_power_carbon` | demand as weights; net generation | A, B | **Held** |
| `ba_supply_monthly` | demand and net generation by day; daily interchange | A, B (held); C applied since session 62 | **Held** |
| `ai_power_regions` | demand and net generation by year; daily interchange; the two tables above | A, B (held); C applied | **Held** |
| `caiso_reliability_daily` | California's demand | A, B | **Held** |
| `event_window_daily` | demand and net generation by day | A, B | **Held** |
| `flex_alert_effects`, `flex_alert_model` | California's demand | A, B, in place of a screen of its own (below 30 percent of the median hour, or 20 percent from both neighbours) | Applied (session 118): built both ways from the same inputs, the two tables are the same in every value, so nothing was held |
| `grid_network_nodes`, the live `/network` page's hourly file | the newest hour of demand, hourly interchange | none: one hour has no hours after it, and rule C is for days | Not applied; said on `/data/faults` |
| `eia930_all_demand`, `eia930_all_generation`, `eia930_all_emissions`, `eia930_daily_interchange` | the source tables | none | They hold EIA's values as published and always will |

## What the held builds would change

Each held table was built twice in a trial folder from the same inputs, once as it is built today and once with the
rule (`runs/session118/trial/base` and `rule`), and compared value by value. Session 118's report lists every figure
on a live page that would move.

| Table | Rows before | Rows after | What changes |
|---|---|---|---|
| `carbon_intensity_hourly` | 1,120,725 | 1,105,048 | 15,677 hours no longer written: California's hydro gap (7,789 hours of the consumed intensity, 7,784 of the generation intensity) and the impossible hours of each denominator |
| `carbon_intensity_daily` | 46,682 | 45,981 | 701 days gone (California 681, PJM 14, SPP 4, New England 1, the Lower 48 1); 1,484 of California's days from November 2023 to December 2025 move as its late hours are read where they belong |
| `carbon_intensity_monthly` | 1,275 | 1,242 | 33 months gone: California 22, PJM 7, SPP 3, the Lower 48 1. PJM's October 2021 was 4.4718 (consumed) and 4.7971 (generation) kg CO2/MWh between months of 316 to 411. 34 of California's months move by at most 0.15, as its late hours are read where they belong |
| `cost_of_power_monthly` | 2,304 | 2,304 | 39 values in five grid-months: New York's October 2024, January 2025 and February 2026 (hours at zero demand leave the hour counts and the simple means; the load-weighted prices do not move, a zero weighs nothing), SPP's June 2025 (load-weighted real-time 33.4085 to 33.4103 USD/MWh) and California's July 2025 (33.2546 to 33.2600 at SP15). No value of Texas moves |
| `cost_of_power_carbon` | 712 | 712 | 9 values change (SPP's June 2025, California's July 2025), 2 gone (California's April 2025 intensity of generation, both hubs), 2 new (New York's February 2026: with the zero hours left out the month's CO2 is held in every hour that is used) |
| `ba_supply_monthly` | 158,503 | 158,503 | 433 values in 28 grid-months. PJM's demand of October 2021 was 4,165,722,983 MWh and is 55,904,508; SPP's of June 2023 was 28,293,676 and is 23,996,172. In the twelve months the live page shows: California's August 2026 and New York's February 2026 |
| `ai_power_regions` | 187 | 187 | 8 values: California's carbon intensity (142.8 to 142.2 kg CO2/MWh), its days and demand; New York's flat-load prices (day-ahead 72.64 to 72.52 USD/MWh) |
| `caiso_reliability_daily` | 20,498 | 20,420 | 13 days of California no longer written (78 rows), in February, April, May and December 2019, October 2020 and July 2025: each held an impossible hour of demand. No value changes |
| `event_window_daily` | 28,438 | 28,383 | 55 rows gone, none changed: days of California (2019 and 2020), New York, PJM and the Lower 48 (April 2019 and 2020) that held an impossible hour, and the comparisons with a baseline that rested on them. No row of Texas moves, so the stress days of the live seller page do not |

Not held, because nothing moved: `flex_alert_effects` (2,973 rows) and `flex_alert_model` (881 rows). The table's own
screen marked 27 of California's hours and the one rule marks 37; the hours that differ lie before the weather the
model needs, and the two builds are the same in every value.

## The pages, while the carbon tables are held

`/emissions` and the grid pages read `carbon_intensity_monthly`. Until the held build is approved the table still
carries 32 months the rule would not write (33 less one that is lost only to the empty hour the late-hours correction
leaves). `warehouse/derived/carbon_left_out.py` lists them from the rule itself and writes `site/data/carbon_left_out.json`;
the pages do not draw those months and say which they are. When the hold is lifted the table no longer holds them and
the list is empty by itself. Run the script again after a new pull of the workbooks.

## Where it was applied in session 103, with before and after

Each table was rebuilt in a trial folder with the rule and compared, value by value, with the table as it stood
(`runs/session103/before_after.py`).

| Table | Before | After | What changed |
|---|---|---|---|
| `eia930_demand_growth` | 24,108 rows | 24,108 rows | **Nothing: 0 values differ.** The table has used this rule since session 97; its code now calls the shared rule |
| `generation_mix_hourly_profile` | 162,911 rows | 162,911 rows | **39 values**, all an average demand of one local hour in one month. PJM 7 (largest: April 2020, hour 23, 75,077.4 to 70,229.0 MW), California 24 (February, April and May 2019, January 2026), New York 6 (February 2026, six hours, up by about 650 to 760 MW each), SPP 2 (July 2024; June 2025, hour 04, 28,596.4 to 29,530.6 MW). No generation figure and no share changed |
| `generation_mix_records` | 306 rows | 306 rows | Nothing: 0 values differ |
| `shoulder_hours_monthly` | 27,328 rows | 27,201 rows | **445 values of California's EIA-based rows changed**: the months April, May and December 2019 and July 2025 (105 to 107 each), and the year figures of 2019 (15) and 2025 (6). Largest: the average demand of April 2019, hour 15, 22,007.8 to 22,694.4 MW; the year 2019's mean shoulder energy above the mean, 35,895.7 to 36,328.7 MWh. **California's February 2019 is no longer written** (123 rows gone): with its impossible hours blank, fewer than 90 percent of its days are complete, which is the table's own rule for a month. Texas: nothing (its file holds no impossible hour). Not from the rule: 13 new rows and 13 changed values of California's own-data rows of 2026, from a day's newer input, and 17 rows of 2026-08-03 gone, a day that left 2026's ten worst (see below) |

Session 118's range test adds no hour to these three: on the Adjusted demand it leaves out nothing the first three
tests kept, so the tables do not move.

**A fault of the shoulder table's own, found by that rebuild and fixed.** The table was merged into its earlier file,
so a row a run no longer made stayed: a day that left a year's ten worst kept its rank, and California's 2026 held
eleven ranked days after one newer day of input. A grid rebuilt by a run is now written whole
(`warehouse/derived/shoulder_hours.py`); a grid whose workbook is not on the machine keeps its earlier rows as before.

## Tests

`tests/test_session103.py`: the rule on hours made for the test (a spike, a zero, a blank, a real ramp kept, a good
hour between two faulty ones left out); the rule is the one `demand_growth.py` had, value for value.

`tests/test_session118.py`, on real rows of the extracts kept in `tests/fixtures/session118/`: PJM's hours of 19
October 2021 and 13 July 2020; New York's six zeros of February 2026; SPP's 3,621,097 and 1,505 MW; Texas in Winter
Storm Uri, where every hour is used; California's slide of 10 November 2023, which only the range catches; the hours
around an hour taken by the clock; a held builder writing what it wrote and a trial build applying the rule; rule C
equal to the three builders' own copies; the hydro gap's first and last hour; the months the pages leave out; and the
register's resolutions.
