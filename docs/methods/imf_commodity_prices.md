# Uranium, lithium, cobalt, nickel and copper prices, monthly averages (IMF, Primary Commodity Price System)

Energy Research Warehouse (ERW), method note written in session 2032 (chain 058) for a table first written on 6 October 2026 (session 132).

Tables: `imf_commodity_prices`

## Publisher and address

International Monetary Fund (IMF), Primary Commodity Price System (PCPS) (`https://www.imf.org/en/Research/commodity-prices`, `PAGE`), read from the IMF's SDMX 3.0 data service, dataflow `IMF.RES/PCPS`, area G001 ("World"), US dollars, monthly, from January 2019 (`API`: `https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.RES/PCPS/+/G001.PURAN+PLITH+PCOBA+PNICK+PCOPP.USD.M?c[TIME_PERIOD]=ge:2019-01`). One request a run, fetched fresh, asking for JSON. Source id `imf:pcps`. Connector: `warehouse/connectors/imf_pcps.py` (session 132), run by `warehouse/refresh_board.sh` (step `imf_pcps`, under `warehouse/pull_budget.py`). `fred_series.py` and `wb_pink_sheet.py` name this table but do not write it; `fred_series.py` writes `fred_imf_commodity_prices`, a different table.

## Vintage and revision

The file on the data machine was rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261020T063359Z-github`, as its first header line says; that run's own header follows: retrieved `20261020T062100Z` (20 October 2026), "Rows read: 465. Months the IMF lists with no value, not written: 0. Nothing is filled. These are monthly averages, not daily prices."

`retrieved_at`: 458 rows carry 2026-10-06T08:18:42Z and 7 rows 2026-10-07T14:45:08Z. The archive keeps the rows each run found new or changed (`ARCHITECTURE.md`), so a restored row carries the `retrieved_at` it has in the archive, not the time of the latest run.

Each run reads the whole history from 2019, deletes the file and writes it again (`main`, `os.remove`), so the IMF's revisions are taken. A table whose newest month is more than `STALE_DAYS` (150) days old is not written.

## Shape and variables

Series, 465 rows: 5 series of 93 months each, January 2019 to September 2026, no month missing. `entity` `imf:PCPS:<indicator>`; `variable` `price`, the IMF's average of the month; `ts_utc` the month's first day at 00:00:00Z; `freq` P1M; `node` the commodity; `geo`, `market` and `vintage` empty.

| Entity | `node` | Unit |
|---|---|---|
| `imf:PCPS:PURAN` | Uranium | USD/lb |
| `imf:PCPS:PLITH` | Lithium | USD/t |
| `imf:PCPS:PCOBA` | Cobalt | USD/t |
| `imf:PCPS:PNICK` | Nickel | USD/t |
| `imf:PCPS:PCOPP` | Copper | USD/t |

The units are the connector's `SERIES` map, "as the IMF's commodity tables state them" (header); the answer's own unit is not read.

## Reading the source

- A series for an indicator that was not asked for stops the table (`parse`).
- A period that is not a month (YYYY-Mnn) stops the table.
- A value that is null, empty or "NaN" is not written and is counted (none here); any other value that is not a number stops the table.
- The indicators answered must be the five asked for, or the table stops (`build`).
- The request is tried up to 4 times (`iso_prices.with_retries`, `RETRIES`), with a wait of 5 seconds times the attempt number after each failure; HTTP 404 is a `SourceGap`, not retried; any other answer but HTTP 200 is a failure; timeout 180 seconds (`fetch_raw`).
- Ceiling: none is counted in the code. The docstring named session 132's 1,500,000 rows in all until session 2032 corrected it.
- Any failure, the age refusal included, is recorded as a failure: `main` does not call `iso_prices.gap_skip`.
- The connector does not call `iso_prices.paused()`; the IMF is not in `warehouse/metadata/paused_sources.csv`.

## License

`sources.csv` has `public` for `imf:pcps`. The header written by the run of the file on the data machine (the connector's line was corrected by session 2032 to cite read 13, the page itself, and takes effect at the next run): "License: public with attribution, on the IMF's Copyright and Usage terms as read through a search result's quotation (the page itself answered HTTP 403): a person should confirm before the table is opened. Cite: International Monetary Fund, Primary Commodity Price System."

The page has since been read: `license_reads.csv` read 13 (`https://www.imf.org/en/about/copyright-and-terms`, read 12 October 2026, HTTP 200). `license_verdicts.csv`, IMF, read 13: "may be public", and "needs written permission" for commercial use (contact copyright@imf.org). The sentence read: "Users may download, extract, copy, create derivative works, publish, distribute, and use Data obtained from IMF Sites subject to these conditions: Distributed or reproduced Data must appear accurately with attribution to the IMF as the source [...] For any potential commercial reuse of IMF Data, email copyright@imf.org to request permission. [...] The IMF prohibits bulk download of information by automated technology without explicit permission". The verdict's note: "Data" lists Primary Commodity Prices by name. This connector makes one request a run.

## Cross-checks (session 2032)

- The counts above were computed from the rows, read past the header lines; 5 series of 93 months is the header's 465 rows, and no (entity, variable, ts_utc) appears twice.
- Copper and nickel against `wb_commodity_prices_monthly` (`wb_pink:copper`, `wb_pink:nickel`, USD/t): both tables hold all 93 months; the IMF's copper is within 0.483 percent of the World Bank's and its nickel within 0.85 percent, the largest gap of each in June 2022.
- Range: uranium 24.475 USD/lb (June 2019) to 81.318 (February 2024); lithium 67,930.886 USD/t (July 2020) to 490,008.179 (April 2022); cobalt 21,721.075 (February 2025) to 81,790.381 (April 2022); nickel 11,523.091 (January 2019) to 33,924.176 (March 2022); copper 5,057.972 (April 2020) to 14,473.056 (September 2026, the newest month).
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- The PCPS's other indicators and indexes; only the five of `SERIES` are asked for.
- Months before January 2019.
- Daily prices: these are monthly averages.
- Copper and nickel from the World Bank: `wb_commodity_prices_monthly`.
