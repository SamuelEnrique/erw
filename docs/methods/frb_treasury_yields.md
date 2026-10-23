# US Treasury yields at 2, 10 and 30 years, constant maturity, daily (Federal Reserve Board, release H.15)

Energy Research Warehouse (ERW), method note written in session 2032 (chain 058) for a table first written on 13 October 2026 (session 207).

Tables: `frb_treasury_yields`

## Publisher and address

Board of Governors of the Federal Reserve System, release H.15 Selected Interest Rates (`https://www.federalreserve.gov/releases/h15/`, `RELEASE`), read from the Board's Data Download Program: the preformatted package "Treasury Constant Maturities" (`PACKAGE` `bf17364827e38702b42a58cf8eaa3f78`), CSV, labels included, one column a series, from 1 January 2019 (`URL`: `https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&series=bf17364827e38702b42a58cf8eaa3f78&lastobs=&from=01/01/2019&to=12/31/2099&filetype=csv&label=include&layout=seriescolumn`). One request a run, fetched fresh, then a 1 second pause, with a browser-like user agent (`HEADERS`: the Board's server answered an empty body without one, 13 October 2026). Source id `frb:h15_treasury_yields`. Connector: `warehouse/connectors/frb_treasury.py` (session 207), run by `warehouse/refresh_board.sh` (step `frb_treasury`, under `warehouse/pull_budget.py`).

The table replaces `fred_treasury_yields`, the same three series through FRED, retired by session 207 on the owner's ruling of 12 October 2026 (header). The docstring records the Board's notice, read 13 October 2026, that its "Build Your Package" option retires the week of 9 November 2026; the preformatted package read here is not named in that notice.

## Vintage and revision

The file on the data machine was rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261023T152740Z-github`, as its first header line says; that run's own header follows: retrieved `20261023T150655Z` (23 October 2026), "Rows read: 2,037 business days of 11 maturities; the three written: RIFLGFCY02_N.B, RIFLGFCY10_N.B, RIFLGFCY30_N.B. Business days the Board lists with no value (ND, market holidays) among the three, not written: 255. Nothing is filled."

`retrieved_at`: 5,832 rows carry 2026-10-13T00:31:25Z and 24 rows seven later times, the latest 2026-10-23T15:06:55Z. The archive keeps the rows each run found new or changed (`ARCHITECTURE.md`), so a restored row carries the `retrieved_at` it has in the archive, not the time of the latest run.

Each run reads the whole history from 2019, deletes the file and writes it again (`main`, `os.remove`), so the Board's revisions are taken. A table whose newest day is more than `STALE_DAYS` (10) days old is not written.

## Shape and variables

Series, 5,856 rows: 3 series of 1,952 days each, 2 January 2019 to 21 October 2026, the three on the same days, none on a Saturday or Sunday. `variable` `yield`; `unit` pct (percent a year, the market yield at constant maturity, quoted on an investment basis); `ts_utc` the business day at 00:00:00Z; `freq` P1D; `geo` US; `node` the Board's unique identifier; `market` and `vintage` empty.

| Entity | Maturity | `node` |
|---|---|---|
| `frb:tcm_2y` | 2-year | H15/H15/RIFLGFCY02_N.B |
| `frb:tcm_10y` | 10-year | H15/H15/RIFLGFCY10_N.B |
| `frb:tcm_30y` | 30-year | H15/H15/RIFLGFCY30_N.B |

## Reading the source

- An empty body stops the table (`build`).
- The CSV must have a row beginning "Time Period"; the data are read from it on (`parse`). `node` is taken from the row beginning "Unique Identifier: ".
- The three columns of `SERIES` must be present, or the table stops. The package's other maturities are read and not written; the header's "11 maturities" is fixed text, not a count the code makes.
- A cell "ND" or empty is not written and is counted (255 here, among the three); any other cell that is not a number stops the table.
- Days before `START` (2019-01-01) are not written.
- The request is tried up to 4 times (`iso_prices.with_retries`, `RETRIES`), with a wait of 5 seconds times the attempt number after each failure; HTTP 404 is a `SourceGap`, not retried; any other answer but HTTP 200 is a failure; timeout 180 seconds (`fetch_raw`).
- No row ceiling is set in the code.
- Any failure, the age refusal included, is recorded as a failure: `main` does not call `iso_prices.gap_skip`.
- The connector does not call `iso_prices.paused()`; the Board is not in `warehouse/metadata/paused_sources.csv`.

## License

Public. `sources.csv` has `public` for `frb:h15_treasury_yields`; the header: "License: public. A work of the Board of Governors of the Federal Reserve System, a U.S. government agency. Cite: Board of Governors of the Federal Reserve System (US), H.15 Selected Interest Rates." `license_verdicts.csv`, FRB, read 41 (the Board's disclaimer page, `https://www.federalreserve.gov/disclaimer.htm`, read 13 October 2026): "Unless otherwise indicated, information on Board's website is in the public domain and may be copied and distributed without permission. Please cite to the Board as the source of the information." Verdict: may be public, and may be public for commercial use.

## Cross-checks (session 2032)

- The counts above were computed from the rows, read past the header lines; no (entity, variable, ts_utc) appears twice.
- There are 2,037 weekdays from 1 January 2019 to 21 October 2026, the header's 2,037 business days read. 85 of them have no row in any of the three series, and 85 times 3 is the header's 255 ND cells.
- The 2-year yield stood above the 10-year on 544 days, the first 27 August 2019 and the last 5 September 2024.
- Range: 2-year 0.09 (5 February 2021) to 5.19 (17 October 2023); 10-year 0.52 (4 August 2020) to 5.31 (5 October 2026); 30-year 0.99 (9 March 2020) to 5.67 (7 October 2026). 21 October 2026: 4.81, 5.13 and 5.42.
- The docstring records session 207's check that every value of the FRED copy equalled the Board's (`archive/sessions/SESSION_207_REPORT.md`); it was not repeated here, and the FRED copy is retired.

## What it does not hold

- The package's other maturities, and the Board's other H.15 series.
- Days before 2 January 2019, and the business days the Board lists as ND.
- Intraday figures: one value a business day.
