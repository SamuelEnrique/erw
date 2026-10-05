# ERCOT hub prices by day

One derived table, `ercot_hub_prices_daily`, built by `warehouse/derived/ercot_hub_prices_daily.py` (session 114).
No request is made: the builder reads price tables the warehouse already holds. It exists so that Ask ERCOT
(`/ask/ercot`, in review) can answer a question about a past price. The interval history,
`ercot_all_hub_prices_history`, is 3,063,570 rows and is not in the site's database; this table is its summary by
day, small enough to be there whole.

## What a row is

For each of ERCOT's six trading hubs (`HB_HUBAVG`, `HB_BUSAVG`, `HB_NORTH`, `HB_SOUTH`, `HB_WEST`, `HB_HOUSTON`),
each market and each complete local operating day (America/Chicago) since 1 January 2015, up to seven rows. The
variable is `<market>_<statistic>`: `da` is the day-ahead market (hourly settlement point prices), `rt` the real-time
market (15-minute settlement point prices).

| Statistic | What it is | Unit |
|---|---|---|
| `mean` | the mean of the day's intervals | USD/MWh |
| `peak_mean` | the mean of the day's peak intervals | USD/MWh |
| `offpeak_mean` | the mean of the day's other intervals | USD/MWh |
| `min` | the day's lowest interval price, as published | USD/MWh |
| `max` | the day's highest interval price, as published | USD/MWh |
| `hours_below_zero` | hours priced below 0 USD/MWh | count |
| `hours_above_200` | hours priced above 200 USD/MWh | count |

`ts_utc` is the local day, written as its date at `00:00:00Z`, as the other daily tables write it. `market` is
`ercot_dam` or `ercot_rtm` and `node` is the hub.

**Peak** is the price board's definition (`docs/methods/price_board.md`): hours ending 7 to 22 local, Monday to
Friday, with the six NERC holidays off-peak. A Saturday, a Sunday or a holiday has no peak hour, so it has no
`peak_mean` row: absence, never a zero. Its `offpeak_mean` then equals its `mean`.

**Hours** in the real-time market are counted by interval: a 15-minute interval priced below zero counts 0.25 of an
hour. A real-time day with one such interval has `rt_hours_below_zero` 0.25. The comparison is strict: a price of
exactly 0 is not below zero, and a price of exactly 200 is not above 200.

**Means** are rounded to four decimals, half up. The lowest and highest prices are the publisher's own values.

## Why one statistic a row

The request behind the table described one row a hub, market and day, with the seven statistics side by side: 51,534
rows. The table holds the same 51,534 hub-days as 345,228 rows, one statistic each, because the site's database
keeps only the standard columns of a series table (`warehouse/supabase/load.py`): a statistic in a column of its own
would have been dropped on the way to the page the table is for (`docs/datastandard.md`, Decision 39).

## Complete days only

A day is written only when it holds every interval of its local day: 24 hours day-ahead and 96 intervals real-time,
23 and 92 on the day the clocks go forward, 25 and 100 on the day they go back. A day with a missing interval is left
out, never filled, and the run log names it. On the first build (5 October 2026) no day of the inputs was left out:
4,295 day-ahead days and 4,294 real-time days for each hub, with no gap from 1 January 2015.

## Inputs, and what happens where one is missing

| Table | What it gives |
|---|---|
| `ercot_all_hub_prices_history` | ERCOT's yearly files, both markets, from 2015 |
| `iso_dam_hub_prices`, `iso_rtm_hub_prices` | the daily run's tables: ERCOT's rows of the newest weeks |

An interval held by the history and by a daily table is read once, from the daily table; the header says how many
there were and how many differed.

The GitHub runner never holds the yearly history, and the daily tables keep the newest weeks only. There the builder
rebuilds the days its inputs reach and keeps, as they were, the rows an earlier run wrote for the days its inputs hold
no interval of (the table is restored from the Redivis draft before the run: `warehouse/redivis/config.yaml`). The
header says how many rows were carried. A row whose value did not change keeps its `retrieved_at`, so the loader
rewrites only the new days.

## Reading it

- The average price of a month or a year: the mean of `da_mean` or `rt_mean` over its days. This is the mean of the
  daily means. It differs from the mean of every interval only through the two days a year that hold 23 or 25 hours.
- The highest price of a period: the maximum of `rt_max` or `da_max`. The lowest: the minimum of `rt_min` or `da_min`.
- Hours below zero, or above 200 USD/MWh, in a period: the sum of that variable.
- It cannot give a count of intervals, a percentile or a median of interval prices, or the price of one hour. Those
  need the interval tables.

## Checks

`tests/test_session114.py` recomputes days of the table from the interval tables with plain Python, without the
builder's code, and requires the same numbers; it checks the peak rule on a holiday, a weekend and the two clock-change
days, and the carried rows on a machine without the history.

## Where it is

Public (derived from public ERCOT reports). In coverage, the archive and the Redivis draft like any table. In the
site's database it is loaded whole and held under `review_hold` in `warehouse/supabase/live_set.yaml`, with its source
under `sources_hold`, while Ask ERCOT is in review: it is in no count a visitor sees. The daily run rebuilds it after
the price tables (`warehouse/run_daily.sh`).
