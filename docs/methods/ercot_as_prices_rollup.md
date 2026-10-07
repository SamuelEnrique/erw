# ERCOT reserve prices by day and by month

Two derived tables, `ercot_as_prices_daily` and `ercot_as_prices_monthly`, built by
`warehouse/derived/ercot_as_prices_rollup.py` (session 148). No request is made: the builder reads one table the
warehouse already holds, `ercot_as_prices`, ERCOT's day-ahead market clearing price for capacity of each reserve
(ancillary service) product, hour by hour since 2018 (`docs/methods/capacity_and_ancillary.md`).

They exist so that Ask ERCOT (`/ask/ercot`, in review) does not read a year of hourly rows to answer one question
about a year of reserve prices. In session 143 that read took 13.3 seconds. A month is now one row.

The hourly table is not changed, moved or replaced. The battery page (`/cost-of-power/battery`, live) reads it as
before.

## What a row is

For each reserve product and each local operating day, five rows in the daily table; for each product and each local
month, five rows in the monthly table. One statistic a row (`docs/datastandard.md`, Decisions 39 and 44).

| Variable | What it is | Unit |
|---|---|---|
| `mcpc_dam_mean` | the mean of the hours held | USD/MW-hour |
| `mcpc_dam_min` | the lowest hourly price held, as published | USD/MW-hour |
| `mcpc_dam_max` | the highest hourly price held, as published | USD/MW-hour |
| `mcpc_dam_hours` | the count of hours held | count |
| `mcpc_dam_hours_in_day` (daily table) | the hours the local day has: 24, or 23 and 25 on the two clock-change days | count |
| `mcpc_dam_hours_in_month` (monthly table) | the hours the local month has | count |

The products are the hourly table's entities: `ercot:REGUP` (Regulation Up), `ercot:REGDN` (Regulation Down),
`ercot:RRS` (Responsive Reserve) and `ercot:NSPIN` (Non-Spin) from 1 January 2018, and `ercot:ECRS` (ERCOT Contingency
Reserve Service) from 10 June 2023, when ERCOT began buying it. `market` is `ercot_dam`, `node` the product, `geo`
`US-TX`, as in the hourly table. USD/MW-hour is US dollars per MW of capacity held for one hour; it is not USD/MWh.

Means are rounded to four decimals, half up. The lowest and highest prices are the publisher's own values. The monthly
mean is the mean of the month's hours, not the mean of its daily means: the two differ in a month with a clock change.

## The clock

The day and the month are ERCOT's local operating day and month, America/Chicago. This is the clock the hourly table
itself writes its days by: ERCOT publishes each price for an hour ending in Central time, and the hourly table writes
a product's local day only when every hour of it is there. `ts_utc` is the local day written as its date at
`00:00:00Z`, as the other daily tables write it; a month is its first local day at `00:00:00Z`. Query these tables
with plain dates and no time zone.

A day has 24 hours, 23 on the day the clocks go forward and 25 on the day they go back. `mcpc_dam_hours_in_day` and
`mcpc_dam_hours_in_month` are counted on that clock, so March has one hour fewer and November one hour more than the
calendar's days times 24.

## Never filled, and what to do with a short day or month

A day or a month with fewer hours than it has is still written, from the hours held. Nothing is filled, scaled,
spread or interpolated. It carries its count: `mcpc_dam_hours` is less than `mcpc_dam_hours_in_day` or
`mcpc_dam_hours_in_month`. A product has no row at all for a day or a month it holds no hour of: absence, never a
zero.

What a reader does with a short one:

- Compare `mcpc_dam_hours` with `mcpc_dam_hours_in_day` or `mcpc_dam_hours_in_month` before using a mean, a lowest or
  a highest price. When they differ, the three statistics are of the hours held only.
- Say that it is partial, and how many hours it rests on.
- Do not set it beside whole days or months without saying so. A month to date is not a month.
- Do not scale it up to a whole period, and do not treat the missing hours as zero.

On the first build (7 October 2026, from an hourly table that ends on operating day 5 October 2026) no day was short:
14,014 product-days, every one whole. Six of the 465 product-months were short, for two reasons that will recur:

| Product and month | Hours held | Hours in the month | Why |
|---|---|---|---|
| `ercot:ECRS`, June 2023 | 504 | 720 | the product began on 10 June 2023 |
| all five products, October 2026 | 120 | 744 | the month in progress: five days held |

The newest month is short on every build until the month ends. The run log names each short day and each short month,
and each table's header counts them.

This differs from `ercot_hub_prices_daily`, which leaves a day with a missing interval out. There a missing interval
would have gone unseen inside a mean; here the count is a row beside the mean, so the short period can be shown for
what it is.

## Input, and what happens where it is missing or thinner

| Table | What it gives |
|---|---|
| `ercot_as_prices` | every hour of every product since 2018, rewritten whole by its connector on every run |

The builder refuses to write anything when the hourly table is absent, holds a variable other than `mcpc_dam`, a
frequency other than `PT1H`, a unit other than USD/MW-hour, an empty price, an hour that does not start on the hour, a
duplicate key, or more hours in a period than the period has. Both tables are built whole in memory before either is
written.

A day or a month the hourly table on a machine holds no hour of keeps the rows an earlier run wrote for it, as they
were, and the header says how many rows were carried. A row whose value did not change keeps its `retrieved_at`, so the
loader rewrites only what is new (the tables are restored from the Redivis draft before the daily run for that reason:
`warehouse/redivis/config.yaml`). A month the hourly table holds only part of is rebuilt from that part: on a machine
whose hourly table is days behind another's, the newest month's count goes back until the next run on the fuller
table. The count says so.

`--in-dir <dir>` reads the hourly table from another folder and writes nothing there. `--out-dir <dir>` is a trial: it
writes the two tables and its log there and records nothing (no registry row, no run status).

## Reading it

- A product's price month by month, or one month's average: `ercot_as_prices_monthly`, `mcpc_dam_mean`. Each row is
  that month's own mean of its hours.
- A product's price day by day, or over a stretch of days: `ercot_as_prices_daily`, `mcpc_dam_mean`.
- The average of a year or of several months: the mean of `mcpc_dam_mean` over the days of `ercot_as_prices_daily`.
  This is the mean of the daily means. It differs from the mean of every hour only through the two days a year that
  hold 23 or 25 hours. The mean of the monthly means weighs a short month as much as a long one and is further off.
- The highest price of a period: the maximum of `mcpc_dam_max`. The lowest: the minimum of `mcpc_dam_min`. The daily
  table says which day; neither says which hour.
- Whether a period is whole: `mcpc_dam_hours` against `mcpc_dam_hours_in_day` or `mcpc_dam_hours_in_month`.
- They cannot give the price of one hour, the hours of a day, a count of hours above a price, a median or a
  percentile of hourly prices. Those need `ercot_as_prices`.

## Checked by hand

Three days and two months were added up from the hourly rows with plain Python and the `csv` module, without the
builder's code or pandas, and set beside the trial tables (`runs/session148/hand_check.py`, 7 October 2026). All 25
figures agree.

| Product, day or month | Mean | Lowest | Highest | Hours held | Hours it has |
|---|---|---|---|---|---|
| `ercot:REGUP`, 15 July 2024 (an ordinary day) | 2.1733 | 0.0 | 9.49 | 24 | 24 |
| `ercot:RRS`, 9 March 2025 (clocks forward) | 3.3757 | 0.3 | 22.07 | 23 | 23 |
| `ercot:NSPIN`, 2 November 2025 (clocks back) | 1.3224 | 0.06 | 7.2 | 25 | 25 |
| `ercot:ECRS`, June 2025 | 2.6617 | 0.04 | 42.77 | 720 | 720 |
| `ercot:ECRS`, June 2023 (its first month, short) | 88.8969 | 0.07 | 2493.48 | 504 | 720 |

`tests/test_session148.py` repeats the comparison on a machine that holds the hourly table, and tests the arithmetic,
the two clock-change days, a day with missing hours and the carried rows on hours made in the test.

## Size

First build: `ercot_as_prices_daily` 70,070 rows (14,014 product-days, 1 January 2018 to 5 October 2026),
`ercot_as_prices_monthly` 2,325 rows (465 product-months, January 2018 to October 2026). The daily table grows by 25
rows a day.

## Where it is

Public (derived from public ERCOT reports, `ercot:NP4-181-ER` and `ercot:NP4-188-CD`). In coverage, the archive and
the Redivis draft like any table. In the site's database both are loaded whole and held under `review_hold` in
`warehouse/supabase/live_set.yaml`, with their source `erw:ercot_as_prices_rollup` under `sources_hold`, while Ask
ERCOT is in review: they are in no count a visitor sees. No migration is needed: a series table goes into the one
`series` table of the site's database under its `table_name`. The daily run rebuilds both right after the hourly table
(`warehouse/run_daily.sh`).
