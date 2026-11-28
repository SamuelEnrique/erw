# Method: trader view

Tables: `iso_rt_top_intervals`

> **MISO is paused (4 October 2026).** MISO's terms forbid automated access to its site, so every pull of MISO's own servers is paused pending a review; MISO's hub prices stop at the last day pulled, and so does its trader view. What is held stays as it is. [`miso_pause.md`](miso_pause.md)

Energy Research Warehouse (ERW), session 19. Tables: `ercot_trader_daily`, `caiso_trader_daily`, `nyiso_trader_daily`, `miso_trader_daily`, `spp_trader_daily`, `isone_trader_daily` (derived, series, public) and `iso_rt_top_intervals` (derived, series snapshot, public). Code: `warehouse/derived/trader_view.py`. The page that reads them: the site's `/markets` (platform tool 24) until session 132; since then `/markets` redirects to the price board, `/board`, whose "The week, by hub" is this table's face (`docs/methods/price_board.md`).

**PJM is absent.** The ERW has no PJM energy price table: PJM's Data Miner needs an API key, and its terms bar non-members from republishing. The trader view will add PJM when a licensed key exists.

## Inputs

| ISO | Day-ahead table | Real-time table | Real-time hour | Operating day |
|---|---|---|---|---|
| ERCOT | `ercot_dam_hub_prices` (6 hubs) | `ercot_rtm_hub_prices` (15-minute) | mean of the hour's four intervals | America/Chicago |
| CAISO | `caiso_dam_hub_prices` (3 trading hubs) | `caiso_rtm_hub_prices` (15-minute means of 5-minute prices) | mean of the hour's four intervals | America/Los_Angeles |
| NYISO | `nyiso_dam_zone_prices` (11 zones) | `nyiso_rtm_zone_prices` (15-minute means) | mean of the hour's four intervals | America/New_York |
| MISO | `miso_dam_hub_prices` (8 hubs) | `miso_rtm_hub_prices` (hourly) | as published | EST (MISO's market time, no daylight saving) |
| SPP | `spp_dam_hub_prices` (2 hubs) | not read: SPP's real-time prices are held (`spp_rtm_hub_prices`, 15-minute means of 5-minute prices, the rows of `iso_rtm_hub_prices` whose `market` is `spp_rtm`), but the code's `ISOS` map gives SPP no real-time table, so SPP has the day-ahead metrics only (session 10209, `docs/reviews/trader-model-audit-2026-11-26.md`, finding 1) | | America/Chicago |
| ISO-NE | `isone_dam_zone_prices` (hub and 8 zones) | `isone_rtm_zone_prices_hourly` (ISO-NE's hourly real-time LMP) | as published | America/New_York |

Henry Hub: `eia_fuel_spot_prices`, entity `eia:henry_hub` (EIA daily spot, USD/MMBtu, trading dates).

## Daily metrics (`<iso>_trader_daily`)

One row per hub (or zone), local operating day and metric. `ts_utc` is the operating day at 00:00:00Z (Decision 11). `entity` and `node` are the price tables' own. Arithmetic is exact decimal on the published prices, rounded to 4 decimals.

| Variable | Unit | Definition |
|---|---|---|
| `da_mean_usd` | USD/MWh | mean of the day's day-ahead hourly prices. The day must have every hour: 24, or 23 or 25 on a daylight saving change day. With an hour missing, nothing is written for the hub and day |
| `da_onpeak_mean_usd` | USD/MWh | mean over on-peak hours: the standard 5x16 block, hours starting 06:00 to 21:00 local (hours ending 7 to 22), on weekdays that are not NERC holidays, in every grid (CAISO's Saturdays included among the off-peak days, where the price board's on-peak group takes Monday to Saturday). Not written on weekends and holidays |
| `da_offpeak_mean_usd` | USD/MWh | mean over every other hour of the day (the whole day on weekends and holidays) |
| `rt_mean_usd` | USD/MWh | mean of the day's hourly real-time prices |
| `da_rt_spread_mean_usd` | USD/MWh | mean over the day's hours of (real-time minus day-ahead) |
| `da_rt_spread_max_usd` | USD/MWh | the largest hourly (real-time minus day-ahead) of the day |
| `hours_rt_over_da_50` | count | hours in which real-time exceeded day-ahead by more than 50 USD/MWh |
| `implied_heat_rate` | MMBtu/MWh | `da_mean_usd` / Henry Hub spot. The Henry Hub price is the one EIA dates on the operating day, or on the latest trading day up to 4 days before it (weekends and holidays have no trading). EIA dates the daily spot by its trading day: gas traded that day for the next day's flow, while the day-ahead power of the operating day traded the day before; so on a weekday the gas was traded a day after the power, and the newest days, before EIA publishes their gas, take a price up to 4 days older (session 10209, `docs/reviews/trader-model-audit-2026-11-26.md`, finding 2) |
| `da_volatility_30d_usd` | USD/MWh | sample standard deviation of the 30 day-over-day changes in `da_mean_usd` over the 31 days ending on the day. All 31 days are required |

**Notes.**
- **The four real-time metrics need every hour** of both markets on the day. A 15-minute table's hour needs all four intervals.
- **NERC holidays:** New Year's Day, Memorial Day, Independence Day, Labor Day, Thanksgiving and Christmas Day. A holiday on a Sunday moves to Monday.
- **The block is the Central and Western one in every grid (session 10209, `docs/reviews/trader-model-audit-2026-11-26.md`, finding 5).** Hours ending 7 to 22 local is the on-peak block of ERCOT, SPP and the Western contracts. The Eastern block, which NYISO, ISO-NE and PJM name and the Eastern contracts settle on, is hours ending 8 to 23 Eastern prevailing time (07:00 to 23:00), one hour later; the code takes hours ending 7 to 22 for NYISO and ISO-NE too, and for MISO in EST. Those grids are held or paused, so no page shows their on-peak figures, but their rows are in the table. Not sized: the audit reads no held grid's prices.
- **Why this volatility.** Power prices can be zero or negative, so log returns are undefined on some days. The ERW measures volatility on the change in the daily average price, in USD/MWh, and does not annualize it.
- **What a heat rate means here.** The implied heat rate is the day-ahead price over the gas price. It shows how many MMBtu of gas a MWh sells for. It is not any plant's heat rate, and it ignores the gas basis between Henry Hub and the ISO's own gas hubs, which the ERW does not hold.

## The top 10 real-time intervals (`iso_rt_top_intervals`)

- **What it is:** for each ISO with a real-time table, the 10 highest real-time prices, over all its hubs, in the latest 7 local days with every interval of every hub. Ties go to the earlier interval. The 7 need not run in a row: a day not held whole is passed over, so the week can cover more calendar days (on the snapshot of 21 October 2026, 13 to 20 October for ERCOT and CAISO, 11 to 19 October for ISO-NE). And the code counts a day whole when every interval time is held by some hub, not by each hub; on the tables of 13 November 2026 no day differs (session 10209, `docs/reviews/trader-model-audit-2026-11-26.md`, finding 6).
- **Rows:** `ts_utc` is the interval start and `freq` the real-time table's interval (PT15M or PT1H).
- **Snapshot:** the table is replaced every run. The header names each ISO's week.

## Keeping Supabase quiet

- **The problem:** the daily run recomputes every day the price tables hold (about 33).
- **The rule:** a row whose value is unchanged keeps the `retrieved_at` of the run that first wrote it. The Supabase loader compares every column, so it rewrites only new or revised days.
- **CI:** the CI runner restores the trader tables from the Redivis draft (`warehouse/redivis/config.yaml`). That keeps days older than the price tables' windows, and gives the rule its previous copy.

## On the page (`/markets` until session 132; now the price board's "The week, by hub" at `/board`)

- **Per ISO, a hub table:**
  - this week's mean (the latest 7 operating days in the table; the off-peak mean weighs each day by its off-peak hours, so each hour counts once, since the ruling on the trader view audit of 26 November, finding 3) of the day-ahead average, on-peak and off-peak averages, real-time minus day-ahead, and implied heat rate, each with the change on the 7 days before;
  - the week's largest hourly spread, and the week's count of hours with real-time more than 50 USD/MWh above day-ahead;
  - the latest 30-day volatility;
  - the latest day's day-ahead average, as the table holds it.
- **The ISO's top 10 real-time intervals of the week.**
- A week mean needs all 7 days of the metric; otherwise the cell says "not held yet". The on-peak mean is the exception: `warehouse/derived/board_page.py` (`build_week`, `need = 1`) takes the mean of those of the grid's latest 7 on-peak days that the hub holds, one being enough (session 10209, finding 6; on the board of 21 October 2026 every public hub held all 7, so no figure shown differed: the audit restated all 11 with the rule of 7).
