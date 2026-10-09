# Price board v2: method

> **MISO is paused (4 October 2026).** MISO's terms forbid automated access to its site, so every pull of MISO's own servers is paused pending a review; MISO's hub prices stop at the last day pulled. What is held stays as it is. [`miso_pause.md`](miso_pause.md)

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
| Treasury yields, 2, 10 and 30 years | `fred_treasury_yields` | Federal Reserve Board, release H.15, through FRED, daily | 2019 |
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

**Federal Reserve Board, through FRED** (Treasury yields): release H.15 is a work of a U.S. government agency. FRED marks these series "Public Domain: Citation Requested". Cite: Board of Governors of the Federal Reserve System (US), retrieved from FRED, Federal Reserve Bank of St. Louis. License: public. FRED's series page did not answer this machine on 6 October 2026 (the connection was reset), so the notice is quoted as the site's other FRED connector records it (`fred_series.py`, session 7), not from a fresh reading.

**International Monetary Fund** (commodity prices), "Copyright and Usage" (imf.org/en/about/copyright-and-terms). The page answered this machine HTTP 403 on 6 October 2026, so its words were read through a web search's quotation of the page, not on the page:

> You may download, extract, copy, create derivative works, publish, distribute, and use Data obtained from IMF Sites

subject to conditions that include citing the source, saying so when the data are materially transformed, and not altering the data in a way that affects their nature or accuracy. The search result also notes that a revision of October 2024 removed the word "sell" from an earlier wording. License: public with attribution, by this reading. **A person should read the page before the table is opened to visitors.** The same five commodities' cousins on FRED (`fred_imf_commodity_prices`, session 7) stay internal, as FRED's own notice on them requires.

**California Air Resources Board** (LCFS credit price), California's Conditions of Use (www.ca.gov/use, read 6 October 2026):

> In general, information presented on this website, unless otherwise indicated, is considered in the public domain. It may be distributed or copied as permitted by law.

The workbook carries no other notice. License: public. The same words would cover CARB's allowance auction results, which session 7 held internal: a ruling for a person, not made here.

## The refresh

`warehouse/refresh_board.sh`: the four connectors, the validator and the builder, each under `warehouse/health.py`. Written, not scheduled: no workflow and no line of `run_daily.sh` calls it. The page shows the day it was built until it is.

Before it is scheduled, one thing should be ruled: the workbench's files are about 18 MB in the repository and every one is rewritten each day. Git stores the daily change compactly, but the files could instead go to the public storage bucket the network map already uses (`erw-public`), with the page reading them from there.

## Where the workbench opens (session 168, 9 October 2026)

Before any row is clicked, the workbench's place holds a quiet empty panel: the same box the workbench takes (docked on
the right from the extra-wide width, 42 percent of the board and at least 460 px; above the tables below that width),
the faint outline of a chart drawn in SVG (two axes and three light grid lines, no picture file) and one line, "Click
any row to open the markets workbench here." A click on a row puts the workbench in that box, as before. Measured in a
browser on 9 October 2026: at 1440 px the box and the tables do not move on a click; on narrower screens the box keeps
its place and width, and its height becomes the workbench's own (614 to 1,669 px by row, against the panel's 736 px),
while the row clicked stays where it was on the screen.
