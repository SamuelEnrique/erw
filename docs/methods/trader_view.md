# Method: trader view

Energy Research Warehouse (ERW), session 19. Tables: `ercot_trader_daily`, `caiso_trader_daily`, `nyiso_trader_daily`, `miso_trader_daily`, `spp_trader_daily`, `isone_trader_daily` (derived, series, public) and `iso_rt_top_intervals` (derived, series snapshot, public). Code: `warehouse/derived/trader_view.py`. The page that reads them: the site's `/markets` (platform tool 24).

**PJM is absent.** The ERW has no PJM energy price table: PJM's Data Miner needs an API key, and its terms bar non-members from republishing. The trader view will add PJM when a licensed key exists.

## Inputs

| ISO | Day-ahead table | Real-time table | Real-time hour | Operating day |
|---|---|---|---|---|
| ERCOT | `ercot_dam_hub_prices` (6 hubs) | `ercot_rtm_hub_prices` (15-minute) | mean of the hour's four intervals | America/Chicago |
| CAISO | `caiso_dam_hub_prices` (3 trading hubs) | `caiso_rtm_hub_prices` (15-minute means of 5-minute prices) | mean of the hour's four intervals | America/Los_Angeles |
| NYISO | `nyiso_dam_zone_prices` (11 zones) | `nyiso_rtm_zone_prices` (15-minute means) | mean of the hour's four intervals | America/New_York |
| MISO | `miso_dam_hub_prices` (8 hubs) | `miso_rtm_hub_prices` (hourly) | as published | EST (MISO's market time, no daylight saving) |
| SPP | `spp_dam_hub_prices` (2 hubs) | none: the ERW has no SPP real-time table | | America/Chicago |
| ISO-NE | `isone_dam_zone_prices` (hub and 8 zones) | `isone_rtm_zone_prices_hourly` (ISO-NE's hourly real-time LMP) | as published | America/New_York |

Henry Hub: `eia_fuel_spot_prices`, entity `eia:henry_hub` (EIA daily spot, USD/MMBtu, trading dates).

## Daily metrics (`<iso>_trader_daily`)

One row per hub (or zone), local operating day and metric. `ts_utc` is the operating day at 00:00:00Z (Decision 11). `entity` and `node` are the price tables' own. Arithmetic is exact decimal on the published prices, rounded to 4 decimals.

| Variable | Unit | Definition |
|---|---|---|
| `da_mean_usd` | USD/MWh | mean of the day's day-ahead hourly prices. The day must have every hour: 24, or 23 or 25 on a daylight saving change day. With an hour missing, nothing is written for the hub and day |
| `da_onpeak_mean_usd` | USD/MWh | mean over on-peak hours: the standard 5x16 block, hours starting 06:00 to 21:00 local (hours ending 7 to 22), on weekdays that are not NERC holidays. Not written on weekends and holidays |
| `da_offpeak_mean_usd` | USD/MWh | mean over every other hour of the day (the whole day on weekends and holidays) |
| `rt_mean_usd` | USD/MWh | mean of the day's hourly real-time prices |
| `da_rt_spread_mean_usd` | USD/MWh | mean over the day's hours of (real-time minus day-ahead) |
| `da_rt_spread_max_usd` | USD/MWh | the largest hourly (real-time minus day-ahead) of the day |
| `hours_rt_over_da_50` | count | hours in which real-time exceeded day-ahead by more than 50 USD/MWh |
| `implied_heat_rate` | MMBtu/MWh | `da_mean_usd` / Henry Hub spot. The Henry Hub price is that of the operating day, or of the latest trading day up to 4 days before it (weekends and holidays have no trading) |
| `da_volatility_30d_usd` | USD/MWh | sample standard deviation of the 30 day-over-day changes in `da_mean_usd` over the 31 days ending on the day. All 31 days are required |

**Notes.**
- **The four real-time metrics need every hour** of both markets on the day. A 15-minute table's hour needs all four intervals.
- **NERC holidays:** New Year's Day, Memorial Day, Independence Day, Labor Day, Thanksgiving and Christmas Day. A holiday on a Sunday moves to Monday.
- **Why this volatility.** Power prices can be zero or negative, so log returns are undefined on some days. The ERW measures volatility on the change in the daily average price, in USD/MWh, and does not annualize it.
- **What a heat rate means here.** The implied heat rate is the day-ahead price over the gas price. It shows how many MMBtu of gas a MWh sells for. It is not any plant's heat rate, and it ignores the gas basis between Henry Hub and the ISO's own gas hubs, which the ERW does not hold.

## The top 10 real-time intervals (`iso_rt_top_intervals`)

- **What it is:** for each ISO with a real-time table, the 10 highest real-time prices, over all its hubs, in the latest 7 local days with every interval of every hub. Ties go to the earlier interval.
- **Rows:** `ts_utc` is the interval start and `freq` the real-time table's interval (PT15M or PT1H).
- **Snapshot:** the table is replaced every run. The header names each ISO's week.

## Keeping Supabase quiet

- **The problem:** the daily run recomputes every day the price tables hold (about 33).
- **The rule:** a row whose value is unchanged keeps the `retrieved_at` of the run that first wrote it. The Supabase loader compares every column, so it rewrites only new or revised days.
- **CI:** the CI runner restores the trader tables from the Redivis draft (`warehouse/redivis/config.yaml`). That keeps days older than the price tables' windows, and gives the rule its previous copy.

## On the page (`/markets`)

- **Per ISO, a hub table:**
  - this week's mean (the latest 7 operating days in the table) of the day-ahead average, on-peak and off-peak averages, real-time minus day-ahead, and implied heat rate, each with the change on the 7 days before;
  - the week's largest hourly spread, and the week's count of hours with real-time more than 50 USD/MWh above day-ahead;
  - the latest 30-day volatility;
  - the latest day's day-ahead average, as the table holds it.
- **The ISO's top 10 real-time intervals of the week.**
- A week mean needs all 7 days of the metric; otherwise the cell says "no data".
