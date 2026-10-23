# California Low Carbon Fuel Standard credit price and volume, weekly (California Air Resources Board)

Energy Research Warehouse (ERW), method note written in session 2032 (chain 058) for a table first written on 6 October 2026 (session 132).

Tables: `carb_lcfs_credit_prices`

## Publisher and address

California Air Resources Board (CARB), Weekly LCFS Credit Transfer Activity Report (`https://ww2.arb.ca.gov/resources/documents/weekly-lcfs-credit-transfer-activity-reports`, `PAGE`), sheet "Weekly Average Credit Price" (`SHEET`) of the workbook CARB publishes with it. The workbook's address changes each week, so the connector reads the page (fetched fresh, then a 1 second pause) and follows the one `.xlsx` link on it whose address contains "weekly" (`workbook_url`). Source id `carb:lcfs_weekly_credit_price`. Connector: `warehouse/connectors/carb_lcfs.py` (session 132), with the user agent `UA`.

On GitHub's runner the table is a known gap (`warehouse/metadata/known_gaps.csv`: the workbook answers the runner HTTP 202 with no body); it is refreshed on the data machine by `warehouse/refresh_board.sh` (step `carb_lcfs`) and `warehouse/run_data_machine.sh` (step `dm_carb_lcfs`).

## Vintage and revision

The file on the data machine was written by run `20261012T234454Z` (12 October 2026) from the workbook "Weekly LCFS Credit Activity (upto 20 Sep, 2026)" (the header's access line, `https://ww2.arb.ca.gov/sites/default/files/2026-09/Weekly%20LCFS%20Credit%20Activity%20%28upto%2020%20Sep%2C%202026%29.xlsx`). Header: "Rows read: 402 weeks. Cells CARB leaves empty, not written: 82. Nothing is filled."

Every row carries `retrieved_at` 2026-10-06T08:16:36Z, six days before the run. The workbook is fetched with `iso_prices.fetch_raw` without `fresh`, so a workbook address an earlier run saved is read again from `warehouse/raw/carb_lcfs/`, and its rows carry the first download's time (`raw_cached`). The page is always fetched fresh, so a new week's workbook, at a new address, is downloaded.

Each run deletes the file and writes it again (`main`, `os.remove`), so CARB's revisions are taken. A table whose newest week is more than `STALE_DAYS` (28) days old is not written; the refusal says "(limit 28)", which `iso_prices.gap_skip` (`stale_skip`) records as a skip, "stale at source", not a failure. On 23 October 2026 the file's newest week, 14 September 2026, is 39 days old.

## Shape and variables

Series, 1,124 rows: 3 series on one entity, `carb:lcfs_credit`, over 402 weeks from 7 January 2019 to 14 September 2026. `ts_utc` the week's Monday at 00:00:00Z, except the week CARB lists by its Tuesday, 7 September 2021 (3 rows; the code keeps the date as CARB writes it); weeks are 7 days apart except the 6 and 8 days around that one. `freq` P1W; `geo` US-CA; `node` "LCFS credit"; `market` and `vintage` empty.

| Variable | Unit | CARB's column | Rows | First week |
|---|---|---|---|---|
| `credit_price_weekly_avg` | USD/tCO2 | Weekly Average Credit Price ($) | 402 | 2019-01-07 |
| `credit_price_type1_weekly_avg` | USD/tCO2 | Type 1 Transfer Weekly Average Credit Price ($) | 361 | 2019-10-21 |
| `credit_volume` | tCO2 | Total Volume (MT) | 361 | 2019-10-21 |

The prices are CARB's volume-weighted averages of the week's non-zero transfers, all and Type 1, US dollars a credit; one credit is one metric ton of CO2 equivalent (header). The 82 empty cells are the Type 1 price and the volume of the 41 weeks from 7 January to 14 October 2019.

## Reading the source

- The page must link exactly one weekly workbook, or the table stops (`workbook_url`).
- The sheet must have the column "Week Of" and the three columns of `COLUMNS` (white space in the names is collapsed first), or the table stops (`parse`).
- A row whose "Week Of" is not a date is dropped and not counted.
- The weeks must be unique and 6 to 8 days apart, or the table stops ("does not list one row a week").
- Weeks before `START` (2019-01-07) are not written.
- A cell that is empty is not written and is counted (82 here); a cell that is not empty and not a number stops the table.
- Each document is tried up to 4 times (`iso_prices.with_retries`, `RETRIES`), with a wait of 5 seconds times the attempt number after each failure; HTTP 404 is a `SourceGap`, not retried; any other answer but HTTP 200 is a failure; timeout 180 seconds (`fetch_raw`).
- Ceiling: none is counted in the code. The docstring named session 132's 1,500,000 rows in all until session 2032 corrected it.
- The connector does not call `iso_prices.paused()`; CARB is not in `warehouse/metadata/paused_sources.csv`.

## License

Public. `sources.csv` has `public` for `carb:lcfs_weekly_credit_price`; the header: "License: public. California's Conditions of Use (https://www.ca.gov/use/): information on the State's websites is, unless otherwise indicated, in the public domain. Credit: California Air Resources Board." `license_verdicts.csv`, CARB, read 10 (`https://www.ca.gov/use/`, read 12 October 2026): "may be public", and may be public for commercial use; CARB's own page was not read.

## Cross-checks (session 2032)

- The counts above were computed from the rows, read past the header lines; 402 weeks times 3 measures less the header's 82 empty cells is the 1,124 rows, and no (entity, variable, ts_utc) appears twice.
- The Type 1 price and the volume are present in the same 361 weeks. No value is zero or below.
- The weekly average price was highest at 211.02 (week of 10 February 2020) and lowest at 46.54 (week of 24 June 2024). Week of 14 September 2026: 83.77 for all transfers, 84.38 for Type 1, 764,973 credits.
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- The workbook's transaction log and its other sheets: only `SHEET` is read.
- Weeks before 7 January 2019.
- The Type 1 price and the volume before 21 October 2019, where CARB's cells are empty.
- California's cap-and-trade allowances: `carb_auction_allowance_prices`.
