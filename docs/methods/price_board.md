# Price board v2: method

Built in session 30 (Part A) for the site's `/board` (platform tool 2, the real-time price board). Four derived tables, tier `derived`, computed by `warehouse/derived/price_board.py` from the ERW's own tables. The site reads them as they are and computes nothing: every number on `/board` is a value of one of these tables, or of a source table the page names.

## Common rules

- **Operating days are local.** ERCOT and SPP: America/Chicago. CAISO: America/Los_Angeles. NYISO and ISO-NE: America/New_York. MISO: EST, a fixed UTC-5, as MISO publishes.
- **Only complete days count.** A day's mean is taken only when every interval of it is in the table: 24 hours (23 or 25 on the daylight saving days), or 96 fifteen-minute intervals (92 or 100). A day with one interval missing is left out, never filled or interpolated. So a table with a gap day shows fewer days, and the counts (`days_7d`, `days_30d`, `peak_intervals`) say how many.
- **Inputs.**
  - Day-ahead: `iso_dam_hub_prices` (CAISO, ERCOT, MISO, SPP, by `market`), `nyiso_dam_zone_prices`, `isone_dam_zone_prices`.
  - Real-time: `iso_rtm_hub_prices` (by `market`; SPP's real-time series starts 2026-09-24), `nyiso_rtm_zone_prices` (15-minute means of the 5-minute prices), `isone_rtm_zone_prices_hourly` (ISO-NE's final hourly real-time LMPs).
  - ERCOT's history: `ercot_all_hub_prices_history`, streamed once and cut to HB_HUBAVG.
  - Henry Hub, Brent and WTI: `eia_fuel_spot_prices`.
  - Carbon: `carb_auction_allowance_prices`, `rggi_auction_allowance_prices`.
- **Keys.** A hub is the same entity in both markets, so the variable carries the market: `da_` for day-ahead, `rt_` for real-time.
- **Rounding.** Values are stored to 4 decimals, half up; the page shows 2.
- **Main hubs** (as in `site/data/markets.json`): ERCOT HB_HUBAVG, CAISO TH_SP15_GEN-APND, NYISO N.Y.C., MISO INDIANA.HUB, SPP SPPNORTH_HUB, ISO-NE .H.INTERNAL_HUB.

## price_board_latest

One set of rows per hub or zone and market (39 hubs and zones, 12 markets). `ts_utc` of a daily value is the local operating day at 00:00:00Z.

| Variable | Formula |
|---|---|
| `{da,rt}_daily_mean` | Mean of the day's intervals, for each complete day of the last 30 up to the latest complete day (the sparkline) |
| `{da,rt}_latest_day_mean` | The daily mean of the latest complete day. For day-ahead this can be tomorrow, which the ISO has already cleared |
| `{da,rt}_previous_day_mean` | The daily mean of the day before it, only if that day is complete (no gap is bridged) |
| `{da,rt}_day_change` | latest minus previous, USD/MWh |
| `{da,rt}_day_change_pct` | 100 x (latest minus previous) / abs(previous) |
| `{da,rt}_avg_7d`, `_avg_30d` | Mean of the daily means of the complete days among the last 7 or 30 days ending on the latest day |
| `{da,rt}_days_7d`, `_days_30d` | How many complete days those means are over |
| `{da,rt}_min_30d`, `_max_30d` | Lowest and highest daily mean of those 30 days |
| `{da,rt}_latest_interval` | The newest interval in the table, as published (its own `freq`) |
| `{da,rt}_intervals_30d` | Intervals the table holds in the 30 days before its newest; 0 would mean no series |
| `da_minus_rt` | Day-ahead daily mean minus real-time daily mean, on the latest day both are complete (on the day-ahead row) |

## price_board_peak_offpeak

The main hub of each ISO, both markets.

**Peak** is hours ending 7 to 22 local (hour beginning 06:00 to 21:59) on peak days; every other hour is off-peak.

- **Peak days,** ERCOT, MISO, SPP, NYISO and ISO-NE: Monday to Friday, the Eastern and Texas "5x16" convention.
- **Peak days,** CAISO: Monday to Saturday, the Western (WECC) "6x16" convention.
- **Holidays.** NERC holidays are off-peak all day: New Year's Day, Memorial Day, Independence Day, Labor Day, Thanksgiving and Christmas. One that falls on a Sunday moves to the Monday.

**Rows per complete day** of the last 90 each table reaches (`P1D`):

- `peak_mean`, `offpeak_mean` and `all_mean`;
- `peak_intervals` and `offpeak_intervals`.

A weekend or holiday has no peak row.

**Rows per ERCOT operating year** since 2015, HB_HUBAVG, from the history plus the rolling tables (`P1Y`): `all_mean`, `peak_mean`, `offpeak_mean`, `peak_minus_offpeak` and `days`. The current year is year to date.

These are means. `ercot_peak_premium_annual` gives medians and the peak-minus-midday premium; the page shows both.

## price_board_spreads

Daily, last 365 days.

- **`henry_hub`**, `eia:henry_hub`, USD/MMBtu: EIA's Henry Hub spot price, as `eia_fuel_spot_prices` holds it (trading dates).
- **`da_daily_mean`**, main hub: the day-ahead daily mean.
- **`spark_spread_7`**, USD/MWh: `da_daily_mean - 7.0 x Henry Hub`. **The one labelled assumption of the board: a heat rate of 7.0 MMBtu/MWh,** roughly a combined-cycle gas plant. It is not any plant's heat rate, and ignores basis between Henry Hub and the ISO's own gas hubs.
- **`implied_heat_rate`**, MMBtu/MWh: `da_daily_mean / Henry Hub`.
- **The gas price used:** Henry Hub of the operating day, or of the latest trading day up to 4 days before it (weekends and holidays). This is the trader view's rule (`docs/methods/trader_view.md`). The date used is `x_gas_date`. A day with no Henry Hub price within 4 days has no spread row: EIA publishes with a lag of several days, so the newest days have none yet.
- **`brent_minus_wti`**, `erw:brent_minus_wti`, USD/bbl: Brent spot minus WTI Cushing spot, on the dates both are published.

**Reach.** For ERCOT the day-ahead history covers the whole year. The other ISOs' day-ahead tables hold about 35 days (rolling windows since 2026-08-26), so their spreads start there. No history was backfilled.

## price_board_carbon

**License `internal`,** as its inputs: CARB's and RGGI's terms are unconfirmed (session 7). Per auction series:

- `latest_price` (CARB `settlement_price`, USD/tCO2; RGGI `clearing_price`, USD/short_ton), with `allowances_offered` and `allowances_sold` of the same auction;
- `previous_price` of the auction before, and `price_change`.

`ts_utc` is the auction date as the table gives it: CARB publishes only the month, so the first of the month.

- **Discontinued series are left out.** A series whose last auction is over a year before the program's newest is dropped: RGGI's future-vintage auctions ended in 2011. A stale price is never shown as current.
- **No secondary-market carbon prices.** The ERW holds none.
- **The public page shows none of this table's values** while it is internal. It says why, and shows only that the block exists.
