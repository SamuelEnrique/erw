# The screening rule for impossible hours

EIA-930's hourly demand holds hours that did not happen. This note states the one rule the ERW uses to leave them out,
where it is applied, and what it changed. Code: `warehouse/derived/impossible_hours.py`. The faults themselves, with
their dates, are in the table `known_data_faults` and on the page `/data/faults`.

## The rule

An hour of demand is used when it is

1. held (not blank),
2. above zero, and
3. within 25 percent of the median of the four hours around it: the two before and the two after, those of them that
   are held and above zero.

An hour that fails is used for nothing. **Nothing is filled, smoothed or replaced:** the hour becomes a blank, and each
table's own completeness rule decides what a blank costs it (in the shoulder hours a day short of an hour is not a
complete day; in the energy mix the hour drops out of the average demand of its hour of the day).

**Why a quarter.** The steepest real ramps of these grids move demand about a tenth in an hour. No real hour stands a
quarter away from the four around it.

**For demand only.** Solar, wind and battery output move further than a quarter in an hour by nature. Interchange has a
rule of its own: a pair-day is left out when it is further than 10 median absolute deviations, and at least 500 MWh,
from the pair's own median (`warehouse/derived/ba_supply.py`).

## What the rule does not catch

- **A faulty hour inside a sum.** The Lower 48's demand is EIA's sum over every balancing authority. PJM's 224,345 MW
  of 2020-07-13T22:00Z is inside the Lower 48's 776,575 MW of the same hour, which stands 12 percent above the hours
  around it and passes. So the Lower 48 is given an average and no peak.
- **A run of faulty hours at a believable level.** Three or more in a row make their own median.
- **Good hours between two faulty ones** are left out with them: their neighbours' median is pulled by the faults.
  In California's spring of 2019 this costs a few good hours.

## What it leaves out, measured on 2026-10-04

From the newest EIA-930 workbook of each area held on the data machine, every hour from 2018 (76,757 to 76,759 hours
an area). The list is `runs/session103/impossible_hours.csv` on the data machine (not in git).

| Area | Blank | At or below zero | Apart from the hours around it | Which |
|---|---|---|---|---|
| PJM | 27 | 0 | 7 | 2019-12-12T21:00Z (155,276 MW); 2020-04-10T03:00Z (215,682); 2020-07-13T22:00Z (224,345); 2020-07-28T16:00Z (192,229); 2020-07-29T20:00Z (176,085); 2020-08-13T12:00Z (138,575); 2024-11-21T16:00Z (56,260) |
| CAISO | 48 | 0 | 38 | 28 from 2019-02-13 to 2019-05-10; 7 from 2019-12-19 to 2019-12-22 (three of 14, 91 and 96 MW); 2020-10-08T18:00Z; 2025-07-31T19:00Z; 2026-01-25T20:00Z |
| NYISO | 24 | 12 | 0 | 2019-04-18T03:00Z; 2024-01-17T23:00Z; 2024-10-09T20:00Z and T21:00Z; 2025-01-15T22:00Z and T23:00Z; six from 2026-02-09T23:00Z to 2026-02-10T04:00Z |
| SPP | 48 | 0 | 2 | 2024-07-19T04:00Z (24,991 MW); 2025-06-21T09:00Z (1,505 MW) |
| Lower 48 | 24 | 0 | 1 | 2020-04-10T03:00Z (525,129 MW) |
| ERCOT | 96 | 0 | 0 | |
| MISO, ISO-NE | 24, 24 | 0 | 0 | |

New York's zeros are in 2019, 2024, 2025 and 2026. None is in 2020.

## Where it is applied, with before and after

Each table was rebuilt in a trial folder with the rule and compared, value by value, with the table as it stood
(`runs/session103/before_after.py`).

| Table | Before | After | What changed |
|---|---|---|---|
| `eia930_demand_growth` | 24,108 rows | 24,108 rows | **Nothing: 0 values differ.** The table has used this rule since session 97; its code now calls the shared rule |
| `generation_mix_hourly_profile` | 162,911 rows | 162,911 rows | **39 values**, all an average demand of one local hour in one month. PJM 7 (largest: April 2020, hour 23, 75,077.4 to 70,229.0 MW), California 24 (February, April and May 2019, January 2026), New York 6 (February 2026, six hours, up by about 650 to 760 MW each), SPP 2 (July 2024; June 2025, hour 04, 28,596.4 to 29,530.6 MW). No generation figure and no share changed |
| `generation_mix_records` | 306 rows | 306 rows | Nothing: 0 values differ |
| `shoulder_hours_monthly` | 27,328 rows | 27,201 rows | **445 values of California's EIA-based rows changed**: the months April, May and December 2019 and July 2025 (105 to 107 each), and the year figures of 2019 (15) and 2025 (6). Largest: the average demand of April 2019, hour 15, 22,007.8 to 22,694.4 MW; the year 2019's mean shoulder energy above the mean, 35,895.7 to 36,328.7 MWh. **California's February 2019 is no longer written** (123 rows gone): with its impossible hours blank, fewer than 90 percent of its days are complete, which is the table's own rule for a month. Texas: nothing (its file holds no impossible hour). Not from the rule: 13 new rows and 13 changed values of California's own-data rows of 2026, from a day's newer input, and 17 rows of 2026-08-03 gone, a day that left 2026's ten worst (see below) |

**A fault of the shoulder table's own, found by this rebuild and fixed.** The table was merged into its earlier file,
so a row a run no longer made stayed: a day that left a year's ten worst kept its rank, and California's 2026 held
eleven ranked days after one newer day of input. A grid rebuilt by a run is now written whole
(`warehouse/derived/shoulder_hours.py`); a grid whose workbook is not on the machine keeps its earlier rows as before.

## Where it is not applied, and why

The rule is not yet applied in three tables that a live page reads, because applying it would change a table behind a
live page and this session was not told it may:

| Table | Reads demand for | The impossible hours inside its period |
|---|---|---|
| `cost_of_power_monthly`, `cost_of_power_carbon` | the weights of the load-weighted price, by hour | The table holds every grid but Texas from September 2024. Inside that: SPP's 1,505 MW of 2025-06-21T09:00Z; California's 11,819 MW of 2025-07-31T19:00Z and 17,438 MW of 2026-01-25T20:00Z; New York's zeros of October 2024, January 2025 and February 2026, which weigh those hours at nothing. Texas's file holds no impossible hour |
| `ba_supply_monthly` | daily demand, the days whose every hour is held | each such hour's day is counted with the faulty value; New York's zero hours count as held |
| `ai_power_regions` | demand by year | as above |

Applying it is one line in each builder (`impossible_hours.screen` on the demand column). The source tables
(`eia930_all_emissions`, `eia930_all_demand`) hold EIA's hours as published and always will.

## Tests

`tests/test_session103.py`: the rule on hours made for the test (a spike, a zero, a blank, a real ramp kept, a good
hour between two faulty ones left out); the rule is the one `demand_growth.py` had, value for value; the three builders
call it.
