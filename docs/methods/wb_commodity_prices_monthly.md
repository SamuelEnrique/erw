# The World Bank's commodity prices (the Pink Sheet)

Energy Research Warehouse (ERW), method note written in session 932 (chain 052) for a table first written on 23 October 2026.

Tables: `wb_commodity_prices_monthly`

## Publisher and address

World Bank, World Bank Commodity Price Data (The Pink Sheet), the CMO Historical Data Monthly workbook, sheet "Monthly Prices", linked from `https://www.worldbank.org/en/research/commodity-markets` (when written, `https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx`). Connector: `warehouse/connectors/wb_pink_sheet.py` (session 926).

## Vintage and revision

January 1960 to September 2026 when written (the workbook "Updated on October 02, 2026", retrieved 2026-10-23T09:58:30Z). The World Bank updates it at the start of each month. A snapshot: each run asks for the page again (the workbook's address changes with each edition) and reuses a saved workbook at the same address (ceiling: two requests).

## Shape and variables

Series. `entity` `wb_pink:<series name as a slug>`; `variable` `price`; nominal U.S. dollars; `ts_utc` the month's first day; `freq` `P1M`; `geo` empty (world markets); `node` the series' name.

| Series | Unit | From |
|---|---|---|
| Crude oil: average, Brent, Dubai | USD/bbl | 1960 |
| Crude oil, WTI | USD/bbl | 1982 |
| Coal, Australian; Coal, South African | USD/t | 1970; 1984 |
| Natural gas, US; Natural gas, Europe | USD/MMBtu | 1960 |
| Liquefied natural gas, Japan | USD/MMBtu | 1977 |
| Aluminum, copper, lead, tin, nickel, zinc | USD/t | 1960 |

When written: 11,139 rows, 15 series.

## Reading the workbook

- The page must link one monthly workbook; the heading row is the one whose second cell begins "Crude oil"; the units are the next row's, and a unit not in the map ($/bbl, $/mt, $/mmbtu) stops the run, as does a column missing or a month not of the form 1960M01.
- The sheet's "…" (not available) has no row; nothing is filled.
- The workbook's "**" after a name (a note in its Description sheet) is removed from the node and named in the header (South African coal).
- Not taken: the natural gas index (2010=100), the agricultural and fertilizer prices, iron ore ($/dmtu), the precious metals ($/troy oz).

## License

CC BY 4.0, "unless indicated otherwise in the data or indicator metadata" (the World Bank's Summary Terms of Use, read 141 of `license_reads.csv`; verdict "may be public", session 928).

## Cross-checks (sessions 926 and 932)

- Copper and nickel against `imf_commodity_prices`: within 1 percent in all 93 months both hold.
- WTI, Brent and Henry Hub against EIA's daily spot prices (`eia_fuel_spot_prices`) averaged by month: within 3 percent in 487 of 489, 464 of 472 and 350 of 357 months; medians within 0.12 percent.
- Session 932, against the table: each series' first month as above.

## What it does not hold

- The annual workbook, the indices and real-dollar prices (the World Bank gives monthly series in nominal dollars only).
