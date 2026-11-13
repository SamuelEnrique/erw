# Price board v2: method

Tables: `price_board_latest`, `price_board_peak_offpeak`, `price_board_spreads` (session 2340; as held on 24 October 2026, 3,237, 3,894 and 2,488 rows)

> **MISO is paused (4 October 2026).** MISO's terms forbid automated access to its site, so every pull of MISO's own servers is paused pending a review; MISO's hub prices stop at the last day pulled. What is held stays as it is. [`miso_pause.md`](miso_pause.md)

## The board as it stands, part by part (chain 165, sessions 1600 to 1617, 6 November 2026)

This part says what `/board` draws today, group by group and column by column: the table, the computation, the window, the step, the limits, the assumptions with their sources, the tracers, and what the board cannot show and why, publisher by publisher. The sections after it are the board's history, session by session, and stay as they were written. The code: `warehouse/derived/board_page.py` (the builder; the daily run's `board` step and the data machine's `dm_board_page`, through `warehouse/derived/page_keep.py board`), `site/lib/board.ts` (every rule of the page, pure), `site/components/board/BoardView.tsx` and `Workbench.tsx` (the page), `site/app/board/page.tsx` (the page's hold of the day, `holdRows`, on the server), `site/app/board/rows/` (the CSV and its readers). The audit of 6 November 2026: `docs/reviews/board-audit-2026-11-06.md`.

### The columns of every row

| Column | What it is | Window and step | Limits |
|---|---|---|---|
| Latest, its date | the newest value held and its date; a day-ahead price may be tomorrow's | the row's own step | "stale" beside the date past 3 days (a power market's daily row), 10 (another daily row), 17 (weekly), 132 (monthly), 135 (quarterly): `closeAge` |
| Day, Week, Month, Year | the latest less the value held at least 1, 7, 30 (28 for a monthly row) and 365 days before, no more than 6 days older than that; the base's date on hover | daily rows have a day; weekly rows no day; monthly rows no day or week; quarterly rows a year only | "not held yet" when no base is held; blank ("stale") on a stale row (`shownMove`) |
| YTD | the latest less the last value held of the year before, no older than 6 days (daily), a week and 6 days (weekly), December (monthly), the fourth quarter (quarterly) before 31 December | every step | as the other moves |
| Percent beside a move | 100 x the move over the base | | only for a price that cannot be negative: not power, ancillary services, spreads, rates or a row with a formula |
| 7-day and 30-day avg | the mean of the values held in the 7 and 30 days ending on the latest; the count on hover | daily rows only | |
| 12-month avg | the mean of the values held in the 365 days ending on the latest, and the latest less it | every step, when 180 daily, 26 weekly, 9 monthly or 4 quarterly values of the year are held | "not held yet" below that; "stale" on a stale row |
| 30-day low to high | the lowest and highest of the last 30 days | daily rows only | |
| Trend | the series' own points, the mouse reading each date and value | the last 90 days (daily, at most 90 points), a year (weekly), three years (monthly, quarterly) | no point is filled |
| One-year range | the lowest and highest of the 365 days ending on the latest, and where the latest sits | as the 12-month avg | |
| Futures 1 to 4 | "licensed source needed" (CME Group) | gas, crude and products | EIA's NYMEX series end on 5 April 2024 |
| Day's high / low | the latest complete local day's highest and lowest hour, each with the hour it began in local time; under them the last 7 and 30 days' peak hour and the hours above 100, 250 and 1,000 USD/MWh | power group only | hours, not intervals; a single interval's spike is in the week's spikes |
| The name's hover | the code, the formula, the interval (`basis`) and the source | | |

### The groups

| Group | Rows (default view first) | Tables | Computation | Step |
|---|---|---|---|---|
| Power, by hub and zone | the main hub of ERCOT, CAISO and SPP in both markets; every hub, ERCOT's eight load zones, the node basis by class (monthly, linking `/cost-of-power`) and ERCOT's reliability deployment adder behind Show; NYISO and ISO-NE "license needed", MISO "paused", PJM "licensed source needed" | `ercot_zone_prices_history`, `iso_zone_prices_history`, `ercot_all_hub_prices_history`, `iso_hub_prices_history`, the rolling hub and zone tables; `node_basis_summary`; `ercot_rtm_price_adders` | a daily mean of a complete local operating day's hours (24; 23 or 25 on the daylight saving days), each hour the day-ahead price or the mean of every one of its real-time intervals; an adder that ended is no row | daily (node basis monthly) |
| Power, on-peak and off-peak | the main hubs | the same | the on-peak hours (ending 7 to 22 local, Monday to Friday; CAISO Monday to Saturday; NERC holidays off-peak) and the others, and their difference | daily |
| Spark and dark spreads | the main hubs' spark spread, implied heat rate and dark spread; every public hub's spark spread behind Show | the hub rows, `eia_fuel_spot_prices`, `eia_power_plant_fuel_costs` | day-ahead mean - 7.0 x Henry Hub (the day's, else the newest trading day's up to 4 days before); the month's day-ahead mean - 10.5 x US coal delivered | daily; dark monthly |
| Hub spreads | ERCOT North less Houston, West less North, South less Houston; CAISO NP15 less SP15; SPP North less South; ERCOT hub average less SPP North; CAISO SP15 less ERCOT hub average; day-ahead by default | the hub rows | the first hub's daily mean less the second's on the same date (across grids each on its own local day) | daily |
| Day-ahead minus real time | every hub and zone with both markets | the hub rows | the two daily means of the same day | daily |
| Battery spread | every hub and zone | the hub rows | the day's highest hour less its lowest | daily |
| Ancillary services | ERCOT by default; CAISO and SPP; NYISO and ISO-NE held, MISO paused, PJM licensed | `ercot_as_prices`, `caiso_as_prices`, `spp_as_prices` | a daily mean of a complete local day's hourly day-ahead prices | daily |
| Natural gas | Henry Hub; NYMEX contracts, seven regional hubs, TTF and JKM as placeholders | `eia_fuel_spot_prices` | EIA's spot close | daily |
| Natural gas in storage and LNG exports | working gas, Lower 48 and the regions; LNG export price and volume by terminal; US LNG exports and the pipeline trade; daily feedgas a placeholder | `eia_gas_storage_weekly`, `eia_lng_exports_monthly`, `eia_gas_trade_monthly` | as EIA reports | weekly; monthly |
| Natural gas by sector and state | citygate, homes, commercial, industrial, electric power | `eia_gas_prices_state_monthly` | as EIA reports | monthly |
| Crude oil | WTI, Brent, Brent less WTI by default; first purchase (with North Dakota), landed, F.O.B. and refiner acquisition behind Show | `eia_fuel_spot_prices`, `eia_crude_stream_prices`, `eia_crude_first_purchase_prices` | EIA's closes and monthly prices | daily; monthly |
| Refined products, spot | EIA's nine daily product spots | `eia_product_spot_prices` | EIA's closes | daily |
| Oil spreads | the two 3-2-1 cracks; six cracks by product; Brent less WTI | the product and crude rows | (2 x gasoline + diesel) x 42 / 3 - crude; a product x 42 - crude | daily |
| Gas spreads, monthly | Europe less the United States, Japan LNG less the United States, Japan LNG less Europe; the regional basis and the LNG netback as placeholders | `wb_commodity_prices_monthly` | the World Bank's monthly averages, the same month | monthly |
| World energy benchmarks | crude (4), coal (2), gas US and Europe, LNG Japan | `wb_commodity_prices_monthly` | as published | monthly |
| Retail gasoline and diesel | regions by default (US regular and all grades first); states, cities | `eia_regional_retail_fuel_prices`, `eia_retail_fuel_prices` | as EIA's weekly survey reports | weekly |
| Heating oil and propane | residential, United States by default | `eia_heating_fuel_prices_weekly` | as EIA reports, October to March | weekly |
| Retail electricity by state | all sectors, states by default | `eia_retail_electricity_prices` | as EIA-861M reports | monthly |
| Coal and gas delivered to power plants | coal, every area by default; coal spot by basin as placeholders | `eia_power_plant_fuel_costs` | as EIA-923 reports; a cost of exactly 0 is no delivery and no row | monthly |
| Uranium and battery metals | uranium, lithium, cobalt, nickel, copper; daily uranium and lithium as placeholders | `imf_commodity_prices` | the IMF's monthly averages | monthly |
| US Treasury yields | 2, 10, 30 years | `frb_treasury_yields` | the Board's H.15 | daily |
| Carbon and credits | California's LCFS credit (all and Type 1), California's current and advance auctions; RGGI, EUA, RECs and RINs as placeholders | `carb_lcfs_credit_prices`, `carb_auction_allowance_prices` | as CARB publishes | weekly; quarterly |
| Delivery charges and transmission peaks | ERCOT's coincident peak load; the Texas delivery charges as a placeholder | `ercot_4cp_intervals` | ERCOT's load in each summer month's 4CP interval, dated the month | monthly, four months a year |
| Capacity and equities | a placeholder an auction (PJM, NYISO, ISO-NE, MISO); energy equities | none | | |

Beside the groups: the top twelve tiles (`TOP_TWELVE`), the week's table by hub and the week's spikes (`iso_trader_daily`, `iso_rt_top_intervals`), the workbench (any row, by the hour for a power hub; overlays, spreads and ratios, prior years, the distribution with a threshold the reader sets).

### The assumptions, each with its source

- **The spark spread's heat rate, 7.0 MMBtu/MWh**: the board's assumption, about a combined-cycle gas plant, no plant's own; beside it, where `eia_heat_rates_annual` is on the machine that builds, EIA's average operating heat rate of the US natural gas fleet (combined-cycle and peaking plants together), EIA's Electric Power Annual, Table 8.1, its value and year (`heat_ref`).
- **The dark spread's heat rate, 10.5 MMBtu/MWh**: about the US coal fleet's average; beside it EIA's coal fleet average from the same table.
- **The gas of every spark spread is Henry Hub**, in Louisiana: no regional gas price is held. The spread is labeled indicative.
- **The 3-2-1 yields**: two barrels of gasoline and one of diesel from three of crude, before any cost.
- **The thresholds of the hours above**: 100, 250 and 1,000 USD/MWh, the board's own round numbers (the workbench's threshold is the reader's).

### The tracers

Every number on the page carries a key (`data-n`, the row's id and the figure's name). `site/scripts/check-board.mjs` checks the file first (`boardFileChecks`: a key per cell, the numbers and sources, a floor a group, the placeholders' words with no digit, the new figures' consistency; `--file` alone, with no server) and then every marked number of the served page against the file; `check-board-v4.mjs` the same for the earlier marks. The daily run refuses a board its tests refuse (`tests.test_session132`, `240`, `1118`, `1139`), and `page_keep.py` takes a row only where it is no older and no shorter than the one held. Since session 3889 (13 November 2026) it takes or keeps Henry Hub's row and every spark spread and implied heat rate as one set (`BOARD_TOGETHER`): a spread takes the newest gas day up to 4 days back, so a kept spread beside a newer gas row was no longer its inputs, and on 12 and 13 November the board's tests refused the runner's board for it. The rows' CSV (`/board/rows`) carries every figure with its source, and its Python and Stata readers (`/board/rows/python`, `/board/rows/stata`) read it as it is. The tests: `tests/test_board_1601.py` to `test_board_1616.py`, each on real rows of the tables (`tests/fixtures/board_16NN/`) or, where a rule needs dates placed around a year's end, on series made in memory and said so.

### What the board cannot show, and why, publisher by publisher

| Publisher | What | Why | What would supply it |
|---|---|---|---|
| MISO | every hub, both markets; spreads; reserves; capacity | paused since 4 October 2026: MISO's terms forbid automated access (`miso_pause.md`) | a person's review of the terms |
| PJM | every hub; spreads; reserves; capacity | PJM publishes under a license and an account the ERW does not hold | PJM Data Miner, under PJM's data license |
| NYISO, ISO-NE | every hub and zone and every row built from them; reserves; capacity | their terms ask for written permission (`license_status.csv`, from 21 October 2026) | a permission recorded there |
| CME Group | NYMEX futures, contracts 1 to 4 | EIA's copy ends on 5 April 2024 | CME Group, under license |
| S&P Global Commodity Insights (Platts), Natural Gas Intelligence | regional gas hubs and their basis; JKM by the day | licensed indices | either, under license |
| ICE Endex, LSEG | TTF by the day; EUA | licensed | either, under license |
| S&P Global | coal spot by basin | EIA shows the week's prices by permission and may not release the history | S&P Global |
| UxC, TradeTech; Fastmarkets, Benchmark Mineral Intelligence | uranium and lithium by the day | licensed | any of them, under license |
| OPIS, Argus Media | RIN prices | the ERW holds EPA's RINs generated, not their prices | either, under license |
| S&P Global Commodity Insights, ICE | renewable energy credits | licensed | either, under license |
| RGGI, Inc. | the auctions' clearing prices | held internal while RGGI's terms are reviewed | RGGI, Inc., under its terms |
| Data vendors (for example S&P Global Commodity Insights, Wood Mackenzie) | LNG feedgas by the day | compiled from pipeline nominations | such a vendor, under license |
| Shipping assessments (for example Spark Commodities, the Baltic Exchange) | the LNG netback's freight | not held | either, under license |
| The Texas utilities, at the PUCT | delivery charges | the ERW's copy is a model's reading of news reports, internal | each utility's tariff as the PUCT posts it |
| An exchange data vendor | energy equities | licensed | for example Nasdaq Data Link or LSEG |

Not on the board by its rule: annual tables, contracts by signing date (PPAs), tariffs as events, positions (CFTC) and forecasts (EIA's STEO), each named in the audit.

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

- `peak_mean`, `offpeak_mean` and `all_mean`, and `peak_minus_offpeak` (the day's two means, subtracted) on a peak day;
- `peak_intervals` and `offpeak_intervals`.

A weekend or holiday has no peak row.

**Rows per ERCOT operating year** since 2015, HB_HUBAVG, from the history plus the rolling tables (`P1Y`): `{da,rt}_year_all_mean`, `_year_peak_mean`, `_year_offpeak_mean`, `_year_peak_minus_offpeak` and `_year_days`. The current year is year to date. (`year_` keeps them apart from a daily row dated 1 January.)

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

---

# Session 132: the one price board and its markets workbench

From session 132 the price board is one page at one address, `/board`. It holds what the first board (the sections above), version 3 (session 104), the version 4 work (session 127, `price_board_v4.md`) and the markets page (`trader_view.md`) showed, and the series session 132 added. `/markets`, `/board/v3` and `/board/v4` redirect to `/board`; their page files are kept, unrouted, under `site/app/_retired/`. ERCOT's history since 2015 is no longer a section of the board: the page links to `/explorer/ercot-peak-premium`.

The page face carries no method, by the owner's rule: a number that is missing is a short placeholder with its reason on hover, and everything about method, gaps and sources is in this note.

## Where the page's numbers come from

The page reads the site's own files, written by `warehouse/derived/board_page.py` from tables already in `warehouse/output` (the builder makes no request):

| File | What |
|---|---|
| `site/data/board.json` | every row: latest value and date, moves, means, last 30 points, one-year range; the week's table and spikes |
| `site/public/board/s/<id>.json` | one file a row: its whole history held, read by the workbench when the row is opened |
| `site/public/board/h/<id>.json` | one file a power hub or ancillary service: hourly prices, read by the workbench |

Built on 6 October 2026: 794 rows (740 with values, 54 placeholders), 740 series files (about 6 MB) and 74 hourly files (about 12 MB). The tables behind the first board (`price_board_latest` and the three beside it) are still built by the daily run and are no longer read by a page.

## The figures of a row

Every row is one series: daily, weekly or monthly. A weekly or monthly series is shown as such and labeled so.

| Column | Definition |
|---|---|
| Latest, its date | the newest date held, and its value |
| Day | the latest value less the value held before it, when that is no more than 7 days older (a fuel has no weekend). Daily series only |
| Week, month, year | the latest value less the newest value held at least 7, 30 and 365 days earlier, when that value is no more than 6 days older than that. A weekly series has no daily move; a monthly series has no daily or weekly move, and its month is the month before |
| 7-day and 30-day average | the mean of the values held in the 7 and 30 days ending on the latest date (the count is on hover). Daily series only |
| 30-day low to high | the lowest and highest value of the last 30 days. Daily series only |
| Last 30 | the last 30 values held (days, weeks or months), drawn as given; the mouse reads each point |
| One-year range | the lowest and highest value of the 365 days ending on the latest date, and where the latest sits between them. Drawn when at least 180 daily, 26 weekly or 9 monthly values of the year are held |
| Percent beside a move | only for a price that cannot be negative: not for power, ancillary services, spreads or yields |

A move whose earlier value is not held is not made: the cell reads "not held yet". Nothing is filled, smoothed or estimated anywhere on the page.

## Power

- **Sources:** `ercot_all_hub_prices_history` (ERCOT's six hubs, from 2019 on this page), `iso_hub_prices_history` (the main hub of CAISO, NYISO, SPP and ISO-NE, and CAISO's NP15, from 1 September 2024), and the rolling tables of every hub and zone (`iso_dam_hub_prices`, `iso_rtm_hub_prices`, `nyiso_dam_zone_prices`, `nyiso_rtm_zone_prices`, `isone_dam_zone_prices`, `isone_rtm_zone_prices`, `isone_rtm_zone_prices_hourly`, from 26 August 2026; SPP's South hub in real time from 24 September 2026). Where two tables hold the same hour, the later-listed one is used.
- **How far back each row goes:** ERCOT's hubs to January 2019; the five main hubs outside ERCOT and NP15 to September 2024; every other zone to late August 2026. A zone with six weeks of history has no move over a year and no one-year range: those cells read "not held yet".
- **An hourly real-time price** is the mean of the hour's intervals (four 15-minute means) when all of them are held. An hour short of an interval is not an hour.
- **A daily price** is the mean of a complete local operating day: 24 hours, 23 or 25 on the daylight saving days. A day short of an hour is not a day. Real time is published a day or two behind day-ahead, and day-ahead may already hold tomorrow.
- **On-peak** is hours ending 7 to 22 local, Monday to Friday (CAISO: Monday to Saturday); NERC holidays are off-peak.
- **Names:** hubs and zones are written in words; the operator's code is on hover.
- **MISO:** every MISO row is listed with "paused while terms are reviewed" and no value. MISO's terms forbid automated access to its site, so its pulls are paused since 4 October 2026 (`miso_pause.md`). The builder drops MISO's rows unread, and no MISO file is written.
- **PJM:** every PJM row is listed with "licensed source needed". PJM publishes its prices under a license and an account the ERW does not hold.

## Ancillary services

Day-ahead prices by the hour for the four grids held: ERCOT (`ercot_as_prices`, from 2019 here), CAISO (`caiso_as_prices`), NYISO (`nyiso_as_prices`) and SPP (`spp_as_prices`), each from September 2024. A row is the daily mean of a complete local day, USD per MW per hour. ISO-NE's are held internal and MISO's are paused: both are listed without values.

## Fuels and the other series

| Group | Source table | Publisher and step | From |
|---|---|---|---|
| Henry Hub, WTI, Brent | `eia_fuel_spot_prices` | EIA, daily spot | 1986 (Henry Hub 1997) |
| Refined products, spot | `eia_product_spot_prices` | EIA, daily spot, the nine series EIA publishes by the day | 1986 |
| Crude by stream | `eia_crude_stream_prices` | EIA, monthly: first purchase price of nine domestic streams, landed and F.O.B. cost of the imported streams EIA names, refiners' acquisition cost by region | 2019 |
| Retail gasoline and diesel | `eia_regional_retail_fuel_prices` | EIA, weekly: the US, the PADDs, and the states and cities EIA lists | 2019 |
| Retail electricity | `eia_retail_electricity_prices` | EIA, Form EIA-861M, monthly, by state and sector | 2019 on this page |
| Coal and gas delivered to power plants | `eia_power_plant_fuel_costs` | EIA, Form EIA-923, monthly, by state | 2019 |
| Uranium, lithium, cobalt, nickel, copper | `imf_commodity_prices` | IMF, Primary Commodity Price System, monthly averages | 2019 |
| Treasury yields, 2, 10 and 30 years | `frb_treasury_yields` | Federal Reserve Board, release H.15, the Board's own Data Download Program, daily (session 207; `fred_treasury_yields`, the same series through FRED, is retired) | 2019 |
| California low-carbon fuel credit | `carb_lcfs_credit_prices` | California Air Resources Board, weekly average of credit transfers | 2019 |

- **Fuel dates:** EIA publishes spot prices by trading day about a week behind, so gas and oil carry their own dates, older than the power prices.
- **WTI, Brent and the gap** are three rows. The gap is Brent less WTI on trading days both are held. Checked on 6 October 2026 against EIA's API (`petroleum/pri/spt`, series RBRTE and RWTC): 113.96 and 96.16 USD a barrel on 29 September 2026, a gap of 17.80, equal to the board's.
- **EIA publishes two crude grades by the day** and no others. The other grades are monthly averages, labeled monthly.
- **A crude stream with no value** (California Kern River and Midway-Sunset in recent months, several imported streams) is a month EIA lists without a number: no row is written.
- **Plant fuel costs:** EIA writes a cost of exactly 0 for a state and month with no deliveries (California's coal in every month): 1,060 such rows are not written. A negative cost is kept as EIA reports it: gas delivered to plants in New Mexico and Arizona was negative in several months of 2024 to 2026 (as low as -3.26 USD/Mcf), which fits negative Permian gas prices but is worth a second look.
- **California's credit price:** CARB lists one week by its Tuesday (7 September 2021, the day after Labor Day); the date is kept as CARB writes it.
- **Treasury yields** have no sector in the coverage vocabulary; the table is filed under `equities` (financial markets) as the nearest.

## Spreads, with their stated heat rates and yields

Each formula is on hover on the page.

| Spread | Formula |
|---|---|
| Spark spread, indicative | day-ahead daily mean at the grid's main hub - 7.0 MMBtu/MWh x Henry Hub. The gas price is the operating day's, else the newest trading day's up to 4 days before. 7.0 MMBtu/MWh is an assumed heat rate, about a combined-cycle plant. Henry Hub is in Louisiana, not the gas a plant in the grid burns: the spread is indicative |
| Implied heat rate | day-ahead daily mean / Henry Hub, the same gas rule |
| Dark spread, indicative, monthly | the month's mean of the hub's day-ahead daily means (every day of the month held) - 10.5 MMBtu/MWh x EIA's US average cost of coal delivered to power plants that month. 10.5 MMBtu/MWh is an assumed heat rate, about the US coal fleet's average; the coal cost is a national average, not the grid's |
| 3-2-1 crack spread | (2 x gasoline + 1 x diesel) x 42 / 3 - crude, USD a barrel: Gulf Coast conventional gasoline and ultra-low sulfur diesel against WTI, and New York Harbor products against Brent. Yields: two barrels of gasoline and one of diesel from three of crude, before any cost |
| Brent minus WTI | Brent spot - WTI spot at Cushing |
| Day-ahead minus real time | day-ahead daily mean - real-time daily mean, same day and hub |
| Battery spread | the day's highest hourly price - its lowest, on complete operating days, by hub and market; the 30-day average is the row's 30-day average |
| On-peak less off-peak | the day's on-peak mean - its off-peak mean |

EIA publishes spot gas about a week behind, so the newest spark spread is a few days older than the newest power price. EIA publishes plant fuel costs about three months behind, so the dark spread is as old.

## The week, by hub

The markets page's table, unchanged in content (`trader_view.md`): from `iso_trader_daily`, the week's means with their change on the week before, the largest real-time premium, the hours real time ran more than 50 USD/MWh above day-ahead, and 30-day volatility; from `iso_rt_top_intervals`, the week's highest real-time intervals. A week is the latest 7 operating days the operator has for each measure, so the real-time measures and the heat rate end earlier than day-ahead (the end is on hover). MISO's rows of both tables are not read.

## The markets workbench

Opens beside the tables when a row is clicked, and at full width with Expand. Its state is in the address, so a view can be shared.

- **Window:** a week to the whole history held, or two dates.
- **Step:** hourly for a power hub or an ancillary service, else the row's own step. Hourly times are shown in the grid's local time.
- **Overlay:** any second series on the board. When the two have different steps, both are shown by the month: the finer one as the mean of the values it holds in each calendar month, and its name says "(monthly mean)".
- **Spread or ratio:** the first less the second, or the first over the second, on the times both hold. It is drawn as its own line with its average (dashed) and its range (shaded). Two hubs give a basis, power over gas a heat rate, a product over crude a crack.
- **Prior years:** the series (or the spread, when one is drawn) by day, week or month of the year, one line a year for the last six years, and the lowest and highest of the five years before the newest as a band. For a daily series the band is by the week: the lowest and highest value those five years hold in the seven days a date falls in (a fuel has no weekend, so a band by the single day would narrow wherever a year's date fell on one). 29 February shares 28 February's place. A line joins the dates its year holds; the mouse reads only values that are held.
- **Distribution:** a histogram of the window's values; values above a chosen threshold and below zero; on-peak and off-peak means (hourly step); the median; 30-day volatility, the standard deviation of the last 30 changes between consecutive values of the series at its own step; and the ten highest values with their times.
- **A power hub opens** on its last seven days by the hour, day-ahead against real time, with the spread between them, each market's on-peak and off-peak mean, the ten highest hours, the week's table for that hub and the week's highest 15-minute real-time intervals.
- **CSV:** the rows shown.

## Not held, and the source that would supply each

| Row | Why | Source that would supply it |
|---|---|---|
| NYMEX futures, contracts 1 to 4 (WTI, RBOB gasoline, heating oil, Henry Hub), and the futures curve beside each spot row | EIA stopped publishing them on 5 April 2024; the history from 2019 is held internal (`eia_all_futures_prices`, session 127) and not shown | CME Group |
| Regional gas hubs (Waha, SoCal Citygate, Algonquin, Chicago) | licensed | S&P Global Commodity Insights (Platts) or Natural Gas Intelligence |
| TTF, daily | licensed | ICE Endex or LSEG |
| JKM, daily | licensed | S&P Global Commodity Insights (Platts) |
| PJM hubs | licensed | PJM Data Miner, under PJM's data license |
| Coal spot by basin | EIA shows the week's prices with S&P Global's permission and cannot release the history | S&P Global |
| Capacity prices | auction results are held internal while each operator's terms are reviewed | each operator, under its data license |
| Uranium and lithium, daily | licensed | UxC or TradeTech; Fastmarkets or Benchmark Mineral Intelligence |
| Renewable energy credits | licensed | S&P Global Commodity Insights or ICE |
| European carbon (EUA) | licensed | ICE Endex |
| Energy equities | licensed | an exchange data vendor |
| California and RGGI allowance auctions | held internal while the publishers' terms are reviewed (session 7) | already held; a ruling on the terms |

## Terms of the sources session 132 added, quoted

**EIA** (retail fuel, crude streams, plant fuel costs), "Copyrights and Reuse", as quoted in `price_board_v4.md`:

> U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.

The three pulls are EIA's own surveys (the weekly retail survey, Forms EIA-14, EIA-182 and EIA-856 for crude, Form EIA-923 for plant fuel). License: public.

**EIA on coal spot prices by basin** (eia.gov/coal/markets, read 6 October 2026):

> Data source: With permission, S&P Global

> Because the historical spot price data are proprietary, they cannot be released by EIA; see S&P Global.

These terms forbid republishing, so no coal spot price is pulled or shown: the rows are greyed.

**EIA on NYMEX futures** (the API's own route name, read 6 October 2026): "NYMEX Futures Prices (Futures prices after April 5, 2024, are not available)". The newest day of contract 1 for crude oil and natural gas is 2024-04-05.

**Federal Reserve Board** (Treasury yields): release H.15 is a work of a U.S. government agency, public domain. Since session 207 (the owner's ruling of 12 October 2026) the three series are read from the Board's own Data Download Program (`frb_treasury.py`, the package "Treasury Constant Maturities"), not through FRED, whose terms forbid storing FRED content without the Bank's written consent (`docs/licenses.md`). Cite: Board of Governors of the Federal Reserve System (US), H.15 Selected Interest Rates. License: public. The check of 13 October 2026: every value of the FRED copy equals the Board's for the same day and maturity (1,944 days of each). The FRED copy (`fred_treasury_yields`) and the FRED spot prices (`fred_daily_spot_prices`, EIA's series, held from EIA's API as `eia_fuel_spot_prices`) are retired: `warehouse/metadata/retired_tables.csv`.

**International Monetary Fund** (commodity prices), "Copyright and Usage" (imf.org/en/about/copyright-and-terms). The page answered this machine HTTP 403 on 6 October 2026, so its words were read through a web search's quotation of the page, not on the page:

> You may download, extract, copy, create derivative works, publish, distribute, and use Data obtained from IMF Sites

subject to conditions that include citing the source, saying so when the data are materially transformed, and not altering the data in a way that affects their nature or accuracy. The search result also notes that a revision of October 2024 removed the word "sell" from an earlier wording. License: public with attribution, by this reading. **A person should read the page before the table is opened to visitors.** The same five commodities' cousins on FRED (`fred_imf_commodity_prices`, session 7) were held internal, as FRED's own notice on them required, and are retired since session 207 (`warehouse/metadata/retired_tables.csv`: FRED is no longer stored).

**California Air Resources Board** (LCFS credit price), California's Conditions of Use (www.ca.gov/use, read 6 October 2026):

> In general, information presented on this website, unless otherwise indicated, is considered in the public domain. It may be distributed or copied as permitted by law.

The workbook carries no other notice. License: public. The same words would cover CARB's allowance auction results, which session 7 held internal: a ruling for a person, not made here.

## The refresh

`warehouse/refresh_board.sh`: the four connectors, the validator and the builder, each under `warehouse/health.py`. Written, not scheduled: no workflow and no line of `run_daily.sh` calls it. The page shows the day it was built until it is.

Before it is scheduled, one thing should be ruled: the workbench's files are about 18 MB in the repository and every one is rewritten each day. Git stores the daily change compactly, but the files could instead go to the public storage bucket the network map already uses (`erw-public`), with the page reading them from there.

Since then (6 October 2026) the runner's daily run calls it, and the builder's rows go through `warehouse/derived/page_keep.py`, which takes a row only where it is no older and no shorter than the held one. Session 284 (14 October 2026) found the consequence for ERCOT: the runner holds only ERCOT's rolling window, so its ERCOT rows are always shorter than the held ones and were never taken. They stood at 7 and 8 October. The data machine's daily run (`warehouse/run_data_machine.sh`, step `dm_board_page`, then the group `dm_test_board`) now runs `page_keep.py board` too, on the machine that holds ERCOT's history, so ERCOT's rows move once a day, after the runner's run.

## Where the workbench opens (session 168, 9 October 2026)

Before any row is clicked, the workbench's place holds a quiet empty panel: the same box the workbench takes (docked on
the right from the extra-wide width, 42 percent of the board and at least 460 px; above the tables below that width),
the faint outline of a chart drawn in SVG (two axes and three light grid lines, no picture file) and one line, "Click
any row to open the markets workbench here." A click on a row puts the workbench in that box, as before. Measured in a
browser on 9 October 2026: at 1440 px the box and the tables do not move on a click; on narrower screens the box keeps
its place and width, and its height becomes the workbench's own (614 to 1,669 px by row, against the panel's 736 px),
while the row clicked stays where it was on the screen.

## As the page stands (session 328, 20 October 2026)

What sessions 318, 319 and 328 changed, so that this note says what the page draws today:

- **The workbench's three charts are drawn in SVG** (session 318, the owner's ruling of 13 October 2026 on charts),
  through the site's shared chart set, with labels on the lines and a Chart | Table switch. The price chart draws the
  spread or ratio as its own line with its average as a named line; its range is no longer a shaded area: the low and
  the high are the stat row's (the table under the chart). The prior years are lines with the five years before the
  newest as a band; the distribution is bars. No value moved.
- **The day and week moves are written in the ink** (session 319, `docs/brand.md`'s rule on up and down): the sign and
  the arrow carry the direction, so color is never the only cue.
- **The distribution's threshold** shows its default beside the box, in grey: USD 100 per MWh for a power price
  (`USD/MWh` rows), else halfway from the window's mean to its high, as `benchOf` in `site/lib/board.ts` sets it. Reset
  puts it back (session 328). The default is the board's own rule, not a published figure.
- **Downloads** (session 328): under the board, each public table the board is built from, as the live set's CSV
  (`/api/download`), with a Python and a Stata reader of that CSV. A table not in the live set is named with its place
  on Redivis. The workbench's own CSV (the rows shown) is unchanged.

## Every public price table, drawn or not (session 1117, 23 October 2026)

The owner's ruling of 5 October 2026: "pretty much all energy prices". Every price table of `warehouse/metadata/coverage.csv` on 23 October 2026, and where it stands on the board. Three public tables were held and not drawn; they are drawn from this session, by `warehouse/derived/board_page.py` (`build_world`, `build_gas_prices`, `build_heating`), on the next run of the builder on a machine that holds them (the data machine's daily `dm_board_page`; a machine without the table builds no row and `page_keep.py` keeps what is held).

| Table | License | On the board |
|---|---|---|
| `ercot_all_hub_prices_history`, `iso_hub_prices_history`, the rolling hub and zone tables | public; ISO-NE's, NYISO's and MISO's rows held | Power, on-peak and off-peak, spreads, battery spread, the week (held grids "license needed", session 1116) |
| `ercot_as_prices`, `caiso_as_prices`, `spp_as_prices`, `nyiso_as_prices` | public; NYISO's held | Ancillary services |
| `eia_fuel_spot_prices`, `eia_product_spot_prices` | public | Natural gas, crude oil, refined products, oil spreads |
| `eia_crude_stream_prices` (first purchase, landed, F.O.B., refiner acquisition) | public | Crude oil, monthly |
| `eia_regional_retail_fuel_prices` | public | Retail gasoline and diesel, weekly |
| `eia_retail_electricity_prices` | public | Retail electricity by state, monthly |
| `eia_power_plant_fuel_costs` | public | Coal and gas delivered to power plants, monthly |
| `imf_commodity_prices` | public | Uranium and battery metals, monthly |
| `frb_treasury_yields` | public | US Treasury yields |
| `carb_lcfs_credit_prices` | public | Carbon and credits |
| **`wb_commodity_prices_monthly`** | public (CC BY 4.0) | **World energy benchmarks, monthly (new):** crude oil (average, Brent, Dubai, WTI), coal (Australian, South African), natural gas (United States, Europe), LNG (Japan). The metals of the same table are not drawn: the board's metals are the IMF's |
| **`eia_gas_prices_state_monthly`** | public | **Natural gas by sector and state, monthly (new):** citygate, homes, commercial, industrial and electric power, the United States and each state, USD per Mcf |
| **`eia_heating_fuel_prices_weekly`** | public | **Heating oil and propane, weekly (new):** residential and wholesale, the United States, the PADDs and the states; EIA publishes weeks only in the heating season (October to March), so a row is marked stale from spring |
| `carb_auction_allowance_prices` | public | **Carbon and credits (from session 1135):** the current and the advance auction's settlement prices, a quarterly row each: a move over a year only, the one-year range once four auctions are held, stale past 135 days (a quarter, a month and the 10 days), drawn in the workbench on the months' axis |
| `eia_crude_first_purchase_prices` | public | Not drawn: the crude group draws `eia_crude_stream_prices`' first purchase prices; whether this table's two series are the same is not checked here |
| `eia_retail_fuel_prices` | public | Not drawn: the retail fuel group draws `eia_regional_retail_fuel_prices`, whose regions include the United States; the two are not checked against each other here |
| `ercot_as_prices_daily`, `ercot_as_prices_monthly`, `ercot_hub_prices_daily`, `ercot_rtm_price_adders`, `ercot_zone_prices_history`, `ercot_rtm_node_prices` | public | Not drawn: daily and monthly roll-ups of rows already drawn, a component of the real-time price, and nodes (the node basis is on the economics pages) |
| `eia_coal_prices_annual`, `eia_coal_delivered_price_annual`, `eia_coal_trade_price_annual`, `eia_coal_price_rank_annual`, `eia_power_costs_annual` | public | Not drawn: annual series; the board draws daily, weekly and monthly rows |
| `lbnl_ppa_prices`, `lbnl_hybrid_ppa_prices` | public | Not drawn: contract prices by signing date (events), not a market price |
| `iso_all_capacity_prices`, `pjm_rpm_capacity_prices`, `isone_as_prices`, `miso_as_prices`, `rggi_auction_allowance_prices`, `eia_all_futures_prices`, `ercot_node_prices_hourly` | internal | Listed as held ("licensed source needed" or "not held yet") where the board names them |

## The held rows and the stale closes (session 1116, 23 October 2026)

- **The hold of 21 October on the whole board.** The builder holds ISO-NE's and NYISO's hub rows ("licensed source needed"), but until this session their peak and off-peak rows, spark and dark spreads, day-ahead less real time, battery spreads, NYISO's ancillary prices, their week rows and their spikes were still drawn: 94 rows of figures, read from tables held for those grids (`price_board_peak_offpeak`, `price_board_spreads`, `nyiso_as_prices`, `iso_hub_prices_history`; `site/data/license_status.json`). The page now makes every row of a grid held on the day "license needed" in place, its name and label kept and every figure dropped, with the hold's words on hover, and leaves the grid's week rows and spikes out, with one line "ISO-NE hubs: license needed" in the week's table as MISO's and PJM's have (`holdRows` in `site/lib/board.ts`). It is applied on the server (`site/app/board/page.tsx`), so no held figure is in what the browser receives. MISO's rows stay "paused while terms are reviewed" (the pause is the stronger reason) and PJM's "licensed source needed". The grids held are read from the status file on the day the page is built: a permission recorded there lifts the hold with no change here.
- **Not changed here:** the series files the workbench opens (`site/public/board/s/<id>.json`) are written by the builder for every row, the held grids' included; no row of a held grid can open the workbench, but the files stand at their addresses. Holding them is the builder's (`warehouse/derived/board_page.py`, the data machine's).
- **Every close's age** is in the hover of its date: whole UTC days from the value's date to the day the board's file was built ("3 days before the board was built on 23 Oct 2026"), counted as the Digest counts its fuel closes (session 804). A day-ahead price for a coming day says it is after the build.
- **Stale**: a row is marked "stale" beside its date past 10 days for a daily series (session 304, the owner's ruling of 18 October 2026: EIA posts spot prices weekly and late), 17 for a weekly one (a week more), and 132 for a monthly one, dated the first day of its month (four months and the same 10 days: EIA's monthly series come about two months after their month). One function, `closeAge` in `site/lib/board.ts`, for every row and every tile. **By the publisher's calendar** (session 1134): a power market posts every day, weekends and holidays included, so a daily row of the power groups (power, on-peak and off-peak, spreads, day-ahead less real time, battery spread, ancillary services) is stale past 3 days; on the file of 23 October the power rows were 0 to 4 days old (the 4 were ISO-NE's and NYISO's, held), so only SPP's ancillary prices are marked among them. ERCOT's day-ahead row holds every day of its last 30 through 22 October: the gap of 15 October that roadmap v4 named is filled. On the file of 23 October: SPP's ancillary prices (newest 3 October), CARB's weekly credit prices (14 September) and the monthly series a publisher stopped (plant fuel by state, crude streams, some since 2020) are marked; none of the twelve at the top is.

## A held grid said once a group (session 1193, 23 October 2026)

Within a group, the rows of a grid held for a license on the day are one line under the public rows: the grid, its count of rows, "license needed" with the hold's words on hover and, for a screen reader, in the line itself, and a toggle ("Show the rows' names") that shows the rows, blank as before. The rows stay in the page, hidden until asked, so every row is in the page either way; nothing about the hold or its words changes. `heldLines` in `site/lib/board.ts` splits a group's rows; `site/scripts/check-board.mjs` checks each line on a build. On the file of 23 October: 10 lines in the groups' default views (NYISO's and ISO-NE's in five power groups), for 20 rows.

## The rows' CSV and the held rows (session 1311, 23 October 2026)

The rows' CSV (`/board/rows`, session 1137) counts the held rows by grid in its header ("Held rows by grid: ISO-NE 54, NYISO 81" on the file of 23 October) and carries the hold's words in a last column, `hold`, on each held line; every other line leaves it empty.

## The figures on the page and their keys

Each number `/grid` shows carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs` checks against the live set and `site/scripts/check-methods.mjs` against this note (session 409). The keys the sections above do not name:

- `price_board_latest`, `da_latest_day_mean`, `rt_latest_day_mean`: a grid's block "What it costs" (`components/grid/YourGrid.tsx`): the day-ahead and the real-time daily mean at the grid's hub, each on its own latest day, USD per MWh.
- `price_board_peak_offpeak`, `da_peak_mean`, `da_offpeak_mean`: the same block: the day-ahead peak mean on its latest day, and the off-peak mean of the same day.
- `price_board_latest`, `da_avg_30d`: the same block: the average written beside the 30-day line of the day-ahead daily mean.

## The power rows made complete (session 1601, chain 165, 6 November 2026)

- **ERCOT's load zones** are rows of "Power, by hub and zone" (Show: every hub and zone), after the hubs: Austin Energy, CPS Energy, Houston, LCRA, North, Rayburn, South and West, day-ahead from `ercot_zone_prices_history` (ERCOT's settlement point prices at the load zones); Houston, North, South and West in real time too. A zone whose real-time price the warehouse does not hold has its real-time row "not held yet". Each zone has its battery spread and, where both markets are held, its day-ahead less real time, as a hub has; on-peak and off-peak stay the main hub's. The builder reads the table first of its price tables, so no later table's hour is replaced by it.
- **The zone history** (`iso_zone_prices_history`) is read too, first with it: CAISO ZP26 and SPP South reach back before the rolling tables began on 26 August 2026, so their moves over a year and their one-year range can be drawn once the table is on the machine that builds.
- **Every power row states its interval** (`basis`, in the hover of the row's name, "Interval: ..."): a daily mean of the complete local operating day's hours (24; 23 or 25 on the daylight saving days), each hour the hour's day-ahead price, or the mean of the hour's four 15-minute real-time prices (ERCOT), of four 15-minute means of the 5-minute prices (CAISO's `lmp_rtm_15m_mean`), of twelve 5-minute prices, or the hourly real-time price as published, read from the interval of the newest table that holds the hub. The battery spread, the on-peak and off-peak means and day-ahead less real time say theirs; an ancillary row says it is a daily mean of hourly day-ahead prices.
- **ERCOT's node basis**, summarized: five monthly rows, "ERCOT nodes against the hub average", one a class of point (every point, gas, solar, wind and storage plants' points), each the month's median across the class's points of each point's mean daily day-ahead basis to the hub average (the point's price less HB_HUBAVG's), from `node_basis_summary` (`docs/methods/node_basis.md`). Each row links to the node view (`/cost-of-power`), which draws the month's 10th to 90th percentiles; the nodes themselves are not rows.
- **ERCOT's real-time price adders** (`ercot_rtm_price_adders`, report NP6-792-ER): a daily row, the mean of the complete local day's hours, each the hour's mean of the adder over its SCED intervals. An adder whose newest hour is more than 90 days older than the table's newest has ended and is drawn as no row: RTORPA (the ORDC on-line reserve adder), RTOFFPA and RTORDPA end on 4 December 2025 and RTRDPA, the reliability deployment adder, begins on 5 December 2025 (`docs/methods/ercot_rtm_price_adders.md`). So one row today, RTRDPA.
- **Capacity**: one placeholder an auction in place of the one row for four: PJM's Base Residual Auction (licensed; the row keeps the id `capacity`, so `page_keep.py` keeps no twin), NYISO's ICAP spot auction and ISO-NE's Forward Capacity Auction (licensed; the page makes them "license needed" with the two grids' hold), MISO's Planning Resource Auction (paused). Each names the publisher and why it is held: `iso_all_capacity_prices` and `pjm_rpm_capacity_prices` are internal.
- Tests: `tests/test_board_1601.py`, on real rows cut from the tables (`tests/fixtures/board_1601/`).

## Natural gas in storage and LNG exports (session 1602, chain 165, 6 November 2026)

A group of its own, after "Natural gas": volumes beside the prices.

| Rows | Table | Step | Unit | What a row is |
|---|---|---|---|---|
| Working gas in storage: Lower 48, East, Midwest, Mountain, Pacific, South Central, and South Central's salt and nonsalt | `eia_gas_storage_weekly` (EIA, Weekly Natural Gas Storage Report) | weekly | Bcf | the working gas at the end of the week EIA reports, dated the week's last day. The week's move is the week's net injection or withdrawal; the year's move is against the same week a year before (within the board's six days' slack) |
| LNG export price, a terminal: Sabine Pass, Corpus Christi, Cameron, Freeport, Calcasieu Pass, Plaquemines, Cove Point, Elba Island | `eia_lng_exports_monthly` (EIA, exports by point of exit) | monthly | USD/Mcf | the month's average price of the LNG exported there, as EIA reports it |
| LNG exports, a terminal (the same and Golden Pass) | the same | monthly | MMcf | the month's volume exported there |
| LNG exports, United States; pipeline exports to Mexico and to Canada; pipeline imports from Canada | `eia_gas_trade_monthly` | monthly | MMcf | the month's volume |
| LNG feedgas, daily | none | | Bcf/d | "licensed source needed": daily feedgas is compiled from pipeline nominations by data vendors (for example S&P Global Commodity Insights or Wood Mackenzie) |

The group opens on the storage rows (Show: gas in storage); the five-year average of storage is not held, so no row compares the week with it; the year's move and the one-year range stand beside it. A terminal's price is EIA's average for the month, not a spot price; EIA publishes it about two months after the month, so a row is a monthly series with the board's monthly stale rule.

Natural gas: the placeholders of the regional hubs are seven from this session, Houston Ship Channel, Transco Zone 6 New York and Eastern Gas South (formerly Dominion South) added to Waha, SoCal Citygate, Algonquin Citygate and Chicago Citygate: none is held (S&P Global Commodity Insights or Natural Gas Intelligence would supply them). TTF and JKM stay placeholders by the day; their notes name the World Bank's monthly Europe gas and Japan LNG rows of the world group.

Tests: `tests/test_board_1602.py`, on real rows (`tests/fixtures/board_1602/`).

## Oil and products: the series held and not drawn (session 1603, chain 165, 6 November 2026)

- **North Dakota crude oil, first purchase price, monthly** (`eia_crude_first_purchase_prices`, series F002038__3, EIA's first purchase price by area; the table's method note calls it a proxy for Bakken crude): a row of the crude group (Show: first purchase, monthly). The table's other series, Mars Blend (F003075793), is not drawn again: it is the crude stream row `eia_crude_stream_prices` already draws (every one of the 91 months both hold is equal, checked on 6 November 2026).
- **Gasoline, all grades, United States, weekly** (`eia_retail_fuel_prices`, EMM_EPM0_PTE_NUS_DPG): a row of the retail group, beside the US regular row. The table's US regular and diesel rows are the regional table's (406 of 406 weeks equal), so they are not drawn twice.
- **Coal by basin** stays five placeholders (S&P Global; EIA may not release the history); each now names the World Bank's monthly Australian and South African coal rows of the world group.
- **The PADD series and the spot products**: unchanged. The retail and heating groups draw every PADD EIA publishes; the spot products are EIA's nine daily series (New York Harbor, the Gulf Coast and Los Angeles), the inputs of the two 3-2-1 cracks among them.

Tests: `tests/test_board_1603.py` (`tests/fixtures/board_1603/`).

## Carbon, the held rows' words, and the costs (session 1604, chain 165, 6 November 2026)

- **A held series says "licensed source needed" and names its publisher** (the chain's rule): RGGI's quarterly auction (RGGI, Inc.; `rggi_auction_allowance_prices` is internal while RGGI's terms are reviewed) and ISO-NE's reserves and regulation (ISO-NE; `isone_as_prices` internal) were "not held yet" with no publisher until this session. Both keep their ids. ISO-NE's row is then "license needed" on the page with the grid's hold, as every ISO-NE row is.
- **RINs**: a placeholder, "Renewable fuel credits (RINs), D4 and D6", daily: no RIN price is held (the ERW holds EPA's RINs generated by month, `epa_rfs_rins_monthly`, not their prices); OPIS or Argus Media would supply daily prices, under license.
- **A cost group**, "Delivery charges and transmission peaks", before "Capacity and equities":
  - **ERCOT coincident peak load** (`ercot_4cp_intervals`, ERCOT's Four Coincident Peak Calculations, NP9-83-M): ERCOT's load in the 15-minute interval it names as each summer month's coincident peak, June to September, MW. One value a summer month, dated the month's first day, so the row is a monthly series holding four months a year: its month's move is the month before in the same summer, its year's move the same month a year before, and it never holds the nine months of a year a one-year range needs. A transmission customer's share of the four sets its transmission charge for the next year. 2021 is not held (on neither of ERCOT's lists); ERCOT publishes a summer's calculation by December, so the row is stale by the board's monthly rule from January to November.
  - **Texas delivery charges, by utility**: a placeholder. The charges the ERW holds (`texas_delivery_charges`) were read by a model from five news outlets' reports and are internal; each transmission and distribution utility's tariff, as the Public Utility Commission of Texas posts it, would supply them openly.
- **Uranium** is unchanged: the IMF's monthly price is drawn, the daily spot a placeholder (UxC, TradeTech). **Retail electricity** by state and sector is drawn as it was.

Tests: `tests/test_board_1604.py` (`tests/fixtures/board_1604/`).

## The power spreads (session 1606, chain 165, 6 November 2026)

- **Hub spreads, within and across grids** (a group after the spark spreads): the first hub's daily mean less the second's, day-ahead and real time, from the two hubs' rows of "Power, by hub and zone".

  | Pair | Scope |
  |---|---|
  | ERCOT North hub less Houston hub; West hub less North hub; South hub less Houston hub | within ERCOT |
  | CAISO NP15 less SP15 | within CAISO |
  | SPP North hub less South hub | within SPP |
  | ERCOT hub average less SPP North hub | across grids |
  | CAISO SP15 less ERCOT hub average | across grids |

  Within a grid both means are of the same local operating day. Across two grids they are of the same date, each on its own grid's local operating day (America/Chicago for ERCOT and SPP, America/Los_Angeles for CAISO), so a cross-grid spread compares days that begin two hours apart. A pair with a grid held for a license on the day is not built; a market with either hub not held is "not held yet". A positive spread: the first hub priced above the second.
- **The spark spread at every public hub**: ERCOT's, CAISO's and SPP's hubs other than the main one each have a spark spread row, behind the group's new Show filter (main hubs by default, as the other power groups); the load zones have none. The implied heat rate and the dark spread stay the main hub's. The gas is Henry Hub for every hub (no regional gas price is held: the gas group's placeholders).
- **The stated heat rate's source**, in every spark and dark row's hover: 7.0 MMBtu/MWh (spark) and 10.5 (dark) are the board's assumptions, about a combined-cycle gas plant and about the US coal fleet's average, no plant's own; beside each, when `eia_heat_rates_annual` is on the machine that builds, EIA's newest average operating heat rate of the US natural gas fleet (combined-cycle and peaking plants together) or of the coal fleet, from EIA's Electric Power Annual, Table 8.1, its value and year, also written as the row's `heat_ref` and the file's `heat_ref` so a check can key it.
- **Not built: the ERCOT 4CP exposure** (gap 28 of the audit). It needs the hub's 15-minute real-time price in each coincident-peak interval, which the board's hourly store does not keep; offered for the next chain.
- `hubspread` is a power group for the stale rule (`POWER_GROUPS`, past 3 days).

Tests: `tests/test_board_1606.py` (`tests/fixtures/board_1606/`).

## The gas and oil spreads (session 1607, chain 165, 6 November 2026)

- **Cracks by product** (oil spreads, daily): a product's price a gallon times 42 less the crude's a barrel, on the trading days EIA publishes both, before any cost: gasoline, diesel and jet fuel at the Gulf Coast against WTI; gasoline, diesel and No. 2 heating oil at New York Harbor against Brent. Each row's newest inputs are in the hover of its value. They stand beside the two 3-2-1 cracks.
- **Gas spreads, monthly** (a group after the oil spreads): from the World Bank's monthly averages (`wb_commodity_prices_monthly`, the Pink Sheet), Europe less the United States (the TTF-to-Henry Hub spread by the month), Japan LNG less the United States (the JKM-to-Henry Hub spread by the month) and Japan LNG less Europe, USD per MMBtu, the same month. The daily TTF and JKM are licensed (the gas group's placeholders), so these are months, not days, and are labeled so.
- **Placeholders**: the regional basis to Henry Hub (no regional hub's daily price is held; S&P Global Commodity Insights or Natural Gas Intelligence would supply them) and the LNG netback to the US Gulf (the destination price, the shipping and the regasification on the same days; no freight is held; a shipping assessment, for example Spark Commodities or the Baltic Exchange, would supply it).
- Brent less WTI is unchanged (the crude group, also under oil spreads).

Tests: `tests/test_board_1607.py` (`tests/fixtures/board_1607/`).

## The moves: the year to date, and none on a stale row (session 1608, chain 165, 6 November 2026)

- **Five moves a row**: day, week, month and year as before (the method's table above), and **YTD**, the latest value less the last value held of the year before, when that value is no older than a step's slack before 31 December: 6 days for a daily series (a fuel has no holiday close), a week and 6 days for a weekly one, December for a monthly one, the fourth quarter for a quarterly one. A year before that ends earlier has no YTD move ("not held yet"). The move's own date is on its hover ("against 11.00 on 30 Dec 2025"), so the window's two ends are stated. The builder writes it as `moves.ytd`; the page draws it as a fifth column from the same list as the four (`MOVES` in `site/lib/board.ts`).
- **A stale row's moves are blank**, each cell reading "stale" with the row's age on hover (`shownMove`): a move measured from a series past the board's stale threshold (`closeAge`) is not shown as current. The latest value and its date stay, with the "stale" mark beside the date, as before. `site/scripts/check-board.mjs` and `check-board-v4.mjs` expect no number in those cells.
- The rows' CSV (`/board/rows`) keeps its four moves until session 1614's downloads.
- `tests/test_session132.py` and `tests/test_session1139.py` take a file built before the YTD move as it is (four moves), so a landing before the first rebuild passes.

Tests: `tests/test_board_1608.py`.

## The trend line (session 1609, chain 165, 6 November 2026)

The column "Last 30" is named "Trend" from this session, and its line is no longer the last 30 values: it is the last **90 days** of a daily row (at most 90 points; a fuel's trading days only, so about 63), a **year** of a weekly row (about 53 weeks), and **three years** of a monthly or a quarterly row (36 months, 12 quarters), each ending on the row's latest value (`SPARK_DAYS` and `SPARK_POINTS` in the builder). The points are the series' own, none filled; the mouse reads each point's date and value as before, and the line is drawn by the page's own SVG (no image). The top block's twelve tiles draw the same line. The column header's hover says the spans. Up to 90 points a row make `board.json` larger: session 1618 measures it.

Tests: `tests/test_board_1609.py`.

## The day's extremes (session 1611, chain 165, 6 November 2026)

- **"Day's high / low"**, a column of the power group only (the group's `extremes` flag): each hub's and zone's latest complete local operating day, its highest and its lowest hour, each with the hour it began in the grid's local time (`ext` of the row: the day, the time zone, the two hours' values in UTC and local time, and the count of hours). The hour is the row's own: the day-ahead price, or the mean of the hour's real-time intervals as the row's interval says. The board's hourly store keeps hours, not intervals, so a single interval's spike is in the week's spikes table (`iso_rt_top_intervals`, under "The week, by hub"), not in this column. The hover names the day and the hours. On a stale row the cell reads "stale". A held grid's rows lose `ext` with their other figures (`holdRows`).
- **The price duration above a threshold the reader sets** is the workbench's: a row opened there shows "Hours above" a threshold the reader types in place (a power row by the hour), with its default (USD 100 per MWh for a power price) and a reset beside it (session 328). Nothing is added for it on the wall.

Tests: `tests/test_board_1611.py`.

## The week and the month in one row (session 1612, chain 165, 6 November 2026)

Under each power row's day high and low, two lines: the last **7** and **30** days, each of the complete local operating days among the 7 or 30 ending on the row's latest day: its **peak hour** (value, day and local time, on hover) and the **hours above 100, 250 and 1,000 USD/MWh** (`h>100/250/1000`), from the row's own hours (`ext.w`, `ext.m`: the days counted, the first, the hours, the peak, the counts). A window short of days says how many it holds on hover; the mean of the week and of the month are the row's 7-day and 30-day averages, already columns. Hours, not intervals (session 1611's note): a count of 15-minute intervals above a price is not held on the board.

Tests: `tests/test_board_1612.py`.

## The comparison: a year before and the twelve-month mean (session 1613, chain 165, 6 November 2026)

- **Against the same date a year before**: the Year move, as since session 132 (the newest value held at least 365 days before and no more than 6 days older than that; its date on hover).
- **Against the trailing twelve-month mean**: a column "12-month avg", the mean of the values held in the 365 days ending on the row's latest (`avg365`: the mean, the count, and the latest less it, drawn beside the mean). Written only when as many values are held as the one-year range needs (180 daily, 26 weekly, 9 monthly, 4 quarterly), so a zone with six weeks of history reads "not held yet". On a stale row it reads "stale". A held grid's rows lose it (`holdRows`).

Tests: `tests/test_board_1613.py`.

## The downloads of the board as shown (session 1614, chain 165, 6 November 2026)

- **The rows' CSV** (`/board/rows`, session 1137) carries the board as the page shows it: beside its earlier columns, `ytd_move`, `avg_12m` and `vs_12m` (the twelve-month mean and the latest less it), `day_high`, `day_high_local`, `day_low`, `day_low_local` (the power rows' day extremes and the hours they began, local time), `basis` (the row's interval) and `status_words` (the page's words for a row with no figure: "licensed source needed", "license needed", "paused while terms are reviewed", "not held yet"). `hold` stays the last column. A held row carries no figure in any of the columns from `latest` to `source`, and no digit after `latest`.
- **Readers**: `/board/rows/python` and `/board/rows/stata`, each a script that reads the CSV at the address of the site that served it, prints the `#` header and skips it, loads the rows as they are, and counts the rows by their status words (`rowsReader` in `site/lib/board.ts`). The Stata reader is in the owner's form: no line continuation, one empty line between the commands outside a loop and none inside one, every figure column destrung with force. The footer of `/board` links both beside the CSV.
- The rows are only the board's own: every public row with its figures and source, every held row with its words. The tables behind them keep their own downloads (CSV, Python, Stata, R) under the board.

Tests: `tests/test_board_1614.py`.

## The checks (session 1616, chain 165, 6 November 2026)

`site/scripts/check-board.mjs` begins with the file's own checks (`boardFileChecks` in `site/lib/board.ts`, on the file as the page draws it, after the day's hold), and with `--file` runs them alone, with no served page:

- a key per cell: every row has its own id (each number's key is the row's id and the figure's name);
- every row with a value has its date, numbers that are numbers and a source;
- a floor a group (`GROUP_FLOORS`): about two thirds of the rows with values after the hold on the file of 5 November 2026, and of what this chain's builder adds to its new groups; a group the file does not hold yet is named, not judged;
- every row with no value shows its words ("licensed source needed", "license needed", "paused while terms are reviewed", "not held yet"), with no digit and no figure;
- the figures this chain added hold together: a day's high above its low, a week's and a month's peak at least the day's high, the hours above 100, 250 and 1,000 in order; a twelve-month mean's difference the latest less the mean; a year-to-date move measured from the year before;
- every row of the groups this chain added (hub spreads, gas storage and LNG, gas spreads, costs) says its interval or its formula.

On the served page the script then checks every marked number against the file as before, now with the YTD move, the twelve-month mean and its difference, and the day's high and low with the week's and month's peaks and counts; a stale row's cells are expected blank.

Tests: `tests/test_board_1616.py` (the site's file, a file the builder writes from this chain's fixtures, and a file broken on purpose).

## The file's size and the build's time (session 1618, chain 165, 6 November 2026)

- **Measured**: the site's `board.json` of 5 November 2026 is 992,915 bytes (176,261 compressed), 1,200 rows. Its 1,106 rows with values, their figures made again from their own series files by this chain's `stats()` (the YTD move, the twelve-month mean, the trend over 90 days, a year or three years) and each row given an interval of about 250 characters: 1,483,180 bytes (242,795 compressed). With the rows this chain adds (about 98 with values and 12 placeholders, at the 1,047 bytes a row with values measures) and the day extremes of about 34 power rows (564 bytes each): about 1.54 MB, 265 KB compressed, **about 55 percent more**. The series files (1,106, 4.8 MB) and the hourly files (74, 12.4 MB) grow by the new rows' own files only (the trend's longer span is in `board.json`, not in them).
- **Decided: not paged, not summarized.** The file does not double; the page sends it in its payload compressed, about 90 KB more than today. The budget for a file not paged is 2.5 MB as written and 400 KB compressed (`tests/test_board_1618.py`, run on the site's file); a build past it is a decision to page the monthly state rows (about 700 of the 1,200) behind their groups' filters, which this note will say when it is made.
- **The build's time**: the builder took 65 to 112 seconds on the old laptop on 6, 9 and 12 October 2026 (its logs), most of it the ERCOT history's 805,000 hours. This chain's builder reads two more large tables, `ercot_zone_prices_history` (about 560 MB here) and `iso_zone_prices_history` (about 360 MB), so the step's reading roughly doubles: about 3 to 4 minutes on the old laptop, less on the data machine, which holds the tables and builds the board (`dm_board_page`). The runner holds neither table and skips them (`here()`), as it skips the ERCOT history. Not measured whole here: a full build on this machine would take the memory the first window's build needs.
- **Not done**: dropping a held grid's rows before they are made into hours would save memory, but `build_power` lists a held grid's zones from the hours read and the spark rows of a held grid's main hub would turn from "license needed" to "not held yet"; tried and left out.

## The keys other readers take from the board (session 1621, chain 165, 6 November 2026)

- **The Digest** (`warehouse/news/brief.py`, `day_move`) takes the board's day move from `board_page.stats` on a two-point series; this chain's `stats` gives the same move and percent (`tests/test_board_1621.py`).
- **Ask's board panel** (`site/lib/chat/panel.ts`) reads each row's latest value and date, its moves `d`, `w`, `m` and `y`, its one-year range and its trend; every one is written under the same name. The trend is now up to 90 points (session 1609), which the panel draws as it is given.
- **Offered, not wired** (Ask's code and the periodicals belong to other chains): a row's `moves.ytd` (the year to date), `avg365` (`v`, `n`, `ch`: the twelve-month mean, its count, the latest less it), `ext` (a power row's day high and low and the week's and month's peaks and hours above 100, 250 and 1,000) and `basis` (its interval in words). The Roundup's "week in five numbers" could take a hub's `ext.w.peak` as the week's highest hour, and its hours above 100, from the board's file rather than computing them again.

## The 4CP exposure (session 1626, chain 167, 6 November 2026)

**ERCOT hub average, real time, at the month's 4CP interval** (the cost group, beside the coincident peak load): the hub average's 15-minute real-time settlement point price in the interval ERCOT names as each summer month's coincident peak, June to September, dated the month as the load row is. It is what energy cost in the interval that also sets a load's transmission charge for the next year. Read from `ercot_all_hub_prices_history` and `iso_rtm_hub_prices`, each filtered to `ercot_rtm` and `HB_HUBAVG` as it is streamed (the history is never in memory whole a second time), the later table's price for an interval winning (`cp4_price`). On the old laptop's tables all 28 intervals ERCOT published for 2018 to 2025 (2021 not held) are priced, from USD 19.40 per MWh (1 July 2024) to USD 2,847.82 (10 August 2023), figures of the fixture `tests/fixtures/board_1626/`. A month whose interval is not priced is no point. Tests: `tests/test_board_1626.py`.

## The rows' CSV: the week and the month (session 1631, chain 167)

The rows' CSV carries a power row's week and month as its cells show them: `week_peak`, `week_hours_over_100`, `week_hours_over_250`, `week_hours_over_1000` and the same four of the month, between `latest` and `source` (a held row's are empty as its other figures are; the Stata reader destrings them). Tests: `tests/test_board_1631.py`.

## A row with no figure prints its words and no digit (session 1632, chain 167)

A held grid's row (`holdRows`) loses its interval's words (`basis`) and the fleet heat rate beside a spark spread (`heat_ref`) with its figures, and a row the builder holds no value for ("not held yet") is written without them: an interval's words carry digits ("24; 23 or 25", "4 15-minute"), and a row with no figure shows its status words and no digit, in its hover and in its line of the rows' CSV. `boardFileChecks` counts a kept `basis` on such a row as a fault. Tests: `tests/test_board_1632.py`.
