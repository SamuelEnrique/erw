# Uranium, lithium, cobalt, nickel and copper prices, a month (the IMF's Primary Commodity Price System)

Energy Research Warehouse (ERW), method note written in session 2046 (chain 059) for a table first written on 6 October 2026 (session 132).

Tables: `imf_commodity_prices`

## Publisher and address

International Monetary Fund (IMF), Primary Commodity Price System (PCPS) (`https://www.imf.org/en/Research/commodity-prices`), read from the IMF's SDMX 3.0 data service in one request a run: `https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.RES/PCPS/+/G001.PURAN+PLITH+PCOBA+PNICK+PCOPP.USD.M?c[TIME_PERIOD]=ge:2019-01` (area G001 "World", US dollars, monthly), asked for as JSON. Source id `imf:pcps`. Connector: `warehouse/connectors/imf_pcps.py` (session 132). The same five series were held earlier as `fred_imf_commodity_prices`, read through FRED, retired on 13 October 2026 (`retired_tables.csv`).

## Vintage and revision

January 2019 to September 2026 in the file on the data machine. The file was rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261020T063359Z-github`, carrying the header of run `20261020T062100Z` (20 October 2026). Header: "Rows read: 465. Months the IMF lists with no value, not written: 0."

Each run reads every month from January 2019, deletes the file and writes the table again, so the IMF's revisions are taken. A table whose newest month is more than 150 days old is not written. Since the file was rebuilt from the archive, the rows' `retrieved_at` is when the archive first held each row: 458 rows say 6 October 2026 and 7 rows (August and September 2026) 7 October.

## Shape and variables

Series, 465 rows: 5 series of 93 months each. `entity` `imf:PCPS:<indicator>`; `variable` `price`, the IMF's average of the month (not a daily price); `ts_utc` the month's first day at 00:00:00Z; `freq` P1M; `node` the commodity; `geo`, `market` and `vintage` empty.

| Entity | `node` | Unit | September 2026 | Highest (month) |
|---|---|---|---|---|
| imf:PCPS:PURAN | Uranium | USD/lb | 72.47 | 81.32 (February 2024) |
| imf:PCPS:PLITH | Lithium | USD/t | 144,778.55 | 490,008.18 (April 2022) |
| imf:PCPS:PCOBA | Cobalt | USD/t | 42,212.62 | 81,790.38 (April 2022) |
| imf:PCPS:PNICK | Nickel | USD/t | 16,323.82 | 33,924.18 (March 2022) |
| imf:PCPS:PCOPP | Copper | USD/t | 14,473.06 | 14,473.06 (September 2026) |

The unit of each series is the connector's own map ("as the IMF's commodity tables state it"), not read from the IMF's answer. `docs/methods/usgs_mcs_critical_minerals.md` finds the lithium series on another basis, six to ten times USGS's battery-grade carbonate price, and does not compare the two.

## Reading the source

- An indicator not asked for, or a period that is not a month, stops the run; so does an answer without all five indicators.
- A month the IMF lists with no value (null, empty or "NaN") is not written and is counted (none here). Any other value that is not a number stops the run.
- One request a run, tried up to four times. The docstring names session 132's ceiling of 1,500,000 rows in all; the code counts none of its own.

## License

`license_verdicts.csv` records the IMF, read 13: "may be public" for public use, "needs written permission" for commercial use (contact copyright@imf.org). The sentence quoted there includes "Users may download, extract, copy, create derivative works, publish, distribute, and use Data obtained from IMF Sites subject to these conditions: Distributed or reproduced Data must appear accurately with attribution to the IMF as the source" and "The IMF prohibits bulk download of information by automated technology without explicit permission"; its note says the IMF's "Data" lists Primary Commodity Prices by name. `license_tables.csv` lists the table under the IMF. The table's header still says the terms page answered HTTP 403 and was read through a search result's quotation; `license_reads.csv` record 13 is a read of that page on 12 October 2026 with HTTP 200. Cite: International Monetary Fund, Primary Commodity Price System.

## Cross-checks (session 2046)

- The counts above were computed from the rows, read past the header lines: 5 series times 93 months is the 465 rows the header says were read, none empty; no (entity, variable, ts_utc) is given twice.
- The 93 months run without a gap from January 2019 to September 2026 in every series.

## What it does not hold

- Daily or spot prices: monthly averages only.
- The PCPS's other commodities and its indices, and months before 2019.
- A confirmed basis for lithium (above).
