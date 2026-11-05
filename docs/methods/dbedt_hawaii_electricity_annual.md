# Hawaii's electricity by island, and Hawaiian Electric on Oahu (DBEDT's State of Hawaii Data Book 2025, section 17)

Energy Research Warehouse (ERW), method note written in session 2583 (chain 127) for a table first written on 25 October 2026 (session 2580).

Tables: `dbedt_hawaii_electricity_annual`

## Publisher and address

The Hawaii State Department of Business, Economic Development and Tourism (DBEDT), The State of Hawaii Data Book 2025, section 17 (one workbook), tables 17.07, 17.10 and 17.13: `https://files.hawaii.gov/dbedt/economic/databook/db2025/DB2025_section17.xlsx`. One GET, no key. Source id `dbedt_hi:data_book_2025_section_17`. Connector: `warehouse/connectors/dbedt_hawaii_electricity.py` (session 2580). files.hawaii.gov has no robots file (read 1123); dbedt.hawaii.gov's asks a crawl delay of 10 seconds (read 1124), kept.

## Vintage and revision

Written by run `20261025T024218Z` (the write under the lock, offline), which read the workbook saved at 2026-10-25T02:39:06Z. `vintage` is its last-modified time, 2026-09-30T00:47:35Z. Each year's Data Book has its own address.

## Shape and variables

Series, 268 rows, 88 entities; `ts_utc` the year's first day; `freq` P1Y; `geo` US-HI; `node` DBEDT's label; `x_table` the table.

| Table | `entity` | `variable` | Years | Unit | Figures |
|---|---|---|---|---|---|
| 17.07 (EIA-923 with DBEDT's calculations) | `dbedt:hi:<island>:<source>`: island state_total, hawaii, maui, lanai, molokai, oahu, kauai, not_specified; source total, petroleum, coal, wind, biomass, geothermal, hydro, other_gases, solar, others | `generation` | 2024 (80 rows) | MWh (million kWh times 1,000) | the state 9,160.9 GWh, Oahu 6,513.7; petroleum 7,054.0, solar 704.9 |
| 17.10 (the utilities' monthly financial reports) | `dbedt:hi:<island>`: state_total, oahu, hawaii, kauai, lanai, maui, molokai | `residential_customers`, `residential_sales`, `other_customers`, `other_sales` | 2025 (28 rows) | count; MWh (million kWh times 1,000) | the state's sales 2,561 GWh residential, 6,355 GWh other use |
| 17.13 (Hawaiian Electric's records) | `dbedt:hi:heco_oahu` | `customers`, `residential_customers`, `net_input` (net generation plus purchases), `sales`, `generating_capability` | 1994 to 2025 (160 rows) | count; MWh (1,000 kWh as given); MW (1,000 kW) | sales 6,797 GWh in 1994, 6,258 GWh in 2025; capability 1,516 MW in 2025 |

The totals hold their parts. 17.07's "others" (energy storage among them) holds negative figures, kept as given.

## Reading the source

- The run stops at once, asking nothing, while `dbedt_hi` or files.hawaii.gov is paused.
- One request a run; `--offline` reads the saved workbook.
- **17.07:** its unit line must read "[Million kWh. Components may not sum to total due to rounding]"; its header must list the ten sources in order and its rows the eight islands; each island's sources add to its total, and the islands to the state, within 0.5 million kWh (DBEDT's own note: components may not sum because of rounding).
- **17.10:** its two blocks (residential, other use) each with the seven islands in order; the islands add to the state within 1 customer and 3 million kWh. Rates, revenues and average use are not taken.
- **17.13:** its columns found by their headers; the years run without a gap. Average use and the residential rate are not taken.
- The run stops, and no file is written, for: a sheet, title, unit line, header or island not as expected, a figure that is not a number, a negative figure outside 17.07's others, a sum missed, a year missing.

Nothing is filled.

## License

Internal. DBEDT's pages read "Copyright (c) 2026, State of Hawaii. All rights reserved." (read 1127); the State's Terms of Use page on portal.ehawaii.gov is drawn by script, its terms not in the bytes received (read 1129). Verdict: needs written permission (ZIMSTAT's precedent). Held from the live set and from Redivis. Table 17.07 rests on EIA's Form EIA-923, which the ERW holds under EIA's own terms.

## Cross-check

EIA's Hawaii for 2024 (`eia_state_source_disposition_annual`, read past its header lines): total net generation 9,160,979 MWh, DBEDT's 9,160.9 GWh.
