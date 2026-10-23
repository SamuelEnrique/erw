# ICE's day-ahead on-peak electricity indices at seven hubs, a delivery day (as EIA republishes them)

Energy Research Warehouse (ERW), method note written in session 2023 (chain 057) for a table first written on 23 October 2026 (session 2014).

Tables: `eia_ice_electricity_daily`

## Publisher and address

The Intercontinental Exchange (ICE), republished by the U.S. Energy Information Administration (EIA) on its Wholesale Electricity and Natural Gas Market Data page (`https://www.eia.gov/electricity/wholesale/`), the current year's workbook `https://www.eia.gov/electricity/wholesale/xls/ice_electric-<YEAR>.xlsx` (2026: one sheet, "2026"). Source id `eia:ice_wholesale_electricity`. Connector: `warehouse/connectors/eia_ice_electricity.py` (session 2014).

## Vintage and revision

The 2026 workbook, last modified 15 October 2026 13:35:32 UTC, retrieved 23 October 2026 18:15:30 UTC and written by run `20261023T181826Z` from the saved file (`--offline`). Deliveries from 29 December 2025 to 14 October 2026, trades from 26 December 2025 to 13 October 2026.

Without `--offline` the year's file is fetched again on every run (it is not taken from the saved files), and the table is written whole each time: a row ICE or EIA no longer gives leaves it. The default year is the current UTC year, so from 1 January 2027 a run asks for 2027's file only, and the table then holds that year alone.

## Shape and variables

Series, 7,056 rows: 1,008 hub-days times 7 variables, every hub-day holding all seven. `entity` `ice:<ICE's product name, slugged>`; `ts_utc` the delivery start date at 00:00:00Z; `freq` P1D; `market` the region as EIA's page names it; `node` the product as ICE writes it; `x_trade_date` the trade date (before the delivery start in all 1,008 hub-days); `x_delivery_end` the delivery end date.

| Entity | Region (`market`) | `geo` | Hub-days | First and last delivery |
|---|---|---|---|---|
| ice:mid_c_peak | Northwest | empty | 180 | 29 December 2025 to 14 October 2026 |
| ice:palo_verde_peak | Southwest | US-AZ | 180 | 29 December 2025 to 14 October 2026 |
| ice:sp15_ez_gen_da_lmp_peak | Southern California | US-CA | 178 | 29 December 2025 to 14 October 2026 |
| ice:np15_ez_gen_da_lmp_peak | Northern California | US-CA | 81 | 29 December 2025 to 13 October 2026 |
| ice:nepool_mh_da_lmp_peak | New England | US-MA | 166 | 30 December 2025 to 14 October 2026 |
| ice:pjm_wh_real_time_peak | PJM | empty | 183 | 29 December 2025 to 14 October 2026 |
| ice:indiana_hub_rt_peak | Midwest | US-IN | 40 | 2 January to 14 October 2026 |

| Variable | Unit |
|---|---|
| price_high, price_low, price_wavg | USD/MWh |
| price_change (the change in the weighted average from the product's previous trade, as the file gives it) | USD/MWh |
| volume | MWh |
| trades, counterparties | count |

A trade for more than one delivery day (a weekend or holiday package) is one row at its start date, its end in `x_delivery_end`; nothing is spread over the days. 144 hub-days are such packages: 42 each at Mid-C, Palo Verde and SP15, 18 at NP15, none in the East.

## Reading the workbook

- A sheet is read when one of its first ten rows holds "Price hub" and "Trade date" (names matched lowered, with everything but letters and digits removed). Such a sheet without a column for the hub, the trade date, the delivery start and end, the high, low and weighted average prices, the volume and the trades stops the run; the change and the counterparties are taken where the sheet has them. A workbook with no such sheet, or one giving no row, stops the run.
- A row whose hub is empty is passed over. A hub not in the connector's map (`HUBS`, which also holds ERCOT North and a second spelling each of Palo Verde and SP15) stops the run; so do a trade, start or end date that does not read, and a delivery end before its start.
- Cells are read with only an empty cell empty (`keep_default_na=False`): an empty cell has no row, and text where a figure belongs ("n/a" included) stops the run. Nothing is filled.
- An (entity, variable, ts_utc) given twice stops the run.
- Ceiling: one request a year asked, with a pause of one second after it. EIA's robots file disallows `/*archive/`, which holds every earlier year's final file and the history zip: they are not asked.

## License

Internal, held from publication. The table's header: "License: internal. EIA: "The market data provided here are republished, with permission, from data collected by the Intercontinental Exchange (ICE)"; the data are ICE's, not EIA's own work, and are held from publication pending a ruling." `license_tables.csv` maps the table by hand to "EIA; ICE, whose prices EIA republishes", and `license_verdicts.csv` gives "ICE, whose prices EIA republishes" (read 192, EIA's page) the verdict needs written permission; session 2019 added ICE's own Terms of Use (read 195), which license the site's content, its pricing and market data included, for personal, non-commercial use only. Whether to ask ICE is for a person to rule.

## Cross-checks (sessions 2014 and 2023)

- Session 2014, ICE's weighted average against the ISOs' own hub prices over the same days' peak hours (`iso_hub_prices_history`): SP15 against CAISO TH_SP15 day-ahead, 178 days, mean difference -0.12 USD/MWh, correlation 0.980; NP15 against TH_NP15, 81 days, +0.27, 0.964; Mass Hub against ISO-NE's internal hub day-ahead, 166 days, +0.91, 0.941; Indiana Hub real time against MISO's Indiana hub real time to 3 October, 37 days, +12.82, 0.590 (a real-time product traded a day ahead). PJM West was not checked: the ERW holds no PJM hub price.
- Session 2023: the counts above were computed from the rows, read past the header lines. The table's means of the weighted average at SP15 (25.57), NP15 (36.41) and Mass Hub (77.79) equal session 2014's ICE means on the same numbers of days.
- The low is at or below the weighted average, and the weighted average at or below the high, in all 1,008 hub-days (114 with one price, low equal to high). Trades are at least 1 and counterparties from 2 to 41 in every hub-day; volume at least 400 MWh.
- The 144 packages counted from the rows equal the header's 144 hub-days.
- `price_change` equals the weighted average less that of the product's previous row by trade date, within a cent, in 888 of the 1,001 hub-days that have a previous row; 61 of the other 113 are a package or follow one. The column is kept as the file gives it.
- The weighted average is below zero in 11 hub-days (SP15 10, Mid-C 1; lowest -2.80 USD/MWh at SP15 on 24 April 2026) and highest at PJM West on 27 January 2026, 1,014.40 USD/MWh.

## What it does not hold

- Years before 2026: their files are under paths EIA's robots file disallows.
- ERCOT North: the 2026 file has no row for it.
- ICE's natural gas hubs (session 2014: the page's gas files stop at 2017 and are under `/archive/`), off-peak products, and anything ICE does not give EIA.
- A price for each day of a package: the package is one row at its start.
