# US Treasury yields at 2, 10 and 30 years, a business day (the Federal Reserve Board's H.15)

Energy Research Warehouse (ERW), method note written in session 2046 (chain 059) for a table first written on 13 October 2026 (session 207).

Tables: `frb_treasury_yields`

## Publisher and address

Board of Governors of the Federal Reserve System, H.15 Selected Interest Rates (`https://www.federalreserve.gov/releases/h15/`), read from the Board's Data Download Program, the preformatted package "Treasury Constant Maturities" (package `bf17364827e38702b42a58cf8eaa3f78`), one request a run: `https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&series=bf17364827e38702b42a58cf8eaa3f78&lastobs=&from=01/01/2019&to=12/31/2099&filetype=csv&label=include&layout=seriescolumn`. The request carries a browser-like agent: the Board's server answered an empty body without one (13 October 2026). Source id `frb:h15_treasury_yields`. Connector: `warehouse/connectors/frb_treasury.py` (session 207).

Until session 207 the same three series were held as `fred_treasury_yields`, read through FRED, whose terms forbid storing its content; that table is retired (`retired_tables.csv`). The connector's docstring records the Board's notice (read 13 October 2026) that its "Build Your Package" option is to be retired the week of 9 November 2026; the preformatted package read here is not named in it.

## Vintage and revision

2 January 2019 to 21 October 2026 in the file on the data machine. The file was rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261023T152740Z-github`, carrying the header of run `20261023T150655Z` (23 October 2026). Header: "Rows read: 2,037 business days of 11 maturities ... Business days the Board lists with no value (ND, market holidays) among the three, not written: 255."

Each run reads the whole package from 2019, deletes the file and writes the table again, so the Board's revisions are taken. A table whose newest day is more than 10 days old is not written. Since the file was rebuilt from the archive, the rows' `retrieved_at` is when the archive first held each row: 5,832 rows (2 January 2019 to 8 October 2026) say 13 October 2026, and the other 24 rows, the days from 9 to 21 October, the run that first wrote each, 14 to 23 October.

## Shape and variables

Series, 5,856 rows: 3 series of 1,952 business days each. `variable` `yield`, the market yield on U.S. Treasury securities at constant maturity, investment basis; `unit` pct (percent a year); `ts_utc` the business day at 00:00:00Z; `freq` P1D; `geo` US; `node` the Board's series identifier; `market` and `vintage` empty.

| Entity | Maturity | `node` |
|---|---|---|
| frb:tcm_2y | 2 years | H15/H15/RIFLGFCY02_N.B |
| frb:tcm_10y | 10 years | H15/H15/RIFLGFCY10_N.B |
| frb:tcm_30y | 30 years | H15/H15/RIFLGFCY30_N.B |

On 21 October 2026: 4.81 (2 years), 5.13 (10 years), 5.42 (30 years). Lowest in the file: 0.09, 0.52 and 0.99; highest: 5.19, 5.31 and 5.67. The package's other eight maturities are read and not written.

## Reading the source

- An empty answer, a CSV with no "Time Period" row, or a package without one of the three series' columns stops the run.
- A day the Board marks "ND" or leaves empty is not written and is counted; any other value that is not a number stops the run.
- Days before 1 January 2019 are dropped. One request a run, tried up to four times, with a one-second pause after the answer. The code counts no row ceiling.

## License

`license_verdicts.csv` records the Board (FRB), read 41 (the Board's disclaimer page, 13 October 2026, session 207): "may be public", for public and for commercial use. The sentence: "Unless otherwise indicated, information on Board's website is in the public domain and may be copied and distributed without permission. Please cite to the Board as the source of the information." `license_tables.csv` lists the table under FRB. Cite: Board of Governors of the Federal Reserve System (US), H.15 Selected Interest Rates.

## Cross-checks (session 2046)

- The counts above were computed from the rows, read past the header lines. The header's figures agree: 2,037 days times 3 series is 6,111, less 255 ND is the 5,856 written (85 days without a value for each series).
- The three series hold the same 1,952 days, none on a Saturday or Sunday, and no gap between days is longer than 4 days. No (entity, variable, ts_utc) is given twice.
- The 2-year stood above the 10-year on 544 days, the first 27 August 2019 and the last 5 September 2024.

## What it does not hold

- The package's other eight maturities, and the H.15's other rates.
- Days before 2019, and weekly, monthly or annual averages.
- Market holidays: no value is filled for them.
