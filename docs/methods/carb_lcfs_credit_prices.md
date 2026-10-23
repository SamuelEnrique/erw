# California's Low Carbon Fuel Standard credit price and volume, a week (CARB's Weekly LCFS Credit Transfer Activity Report)

Energy Research Warehouse (ERW), method note written in session 2046 (chain 059) for a table first written on 6 October 2026 (session 132).

Tables: `carb_lcfs_credit_prices`

## Publisher and address

California Air Resources Board (CARB), Weekly LCFS Credit Transfer Activity Report (`https://ww2.arb.ca.gov/resources/documents/weekly-lcfs-credit-transfer-activity-reports`), sheet "Weekly Average Credit Price" of the workbook CARB publishes with it. The workbook's address changes each week, so the connector reads the page and follows its one `.xlsx` link with "weekly" in it; the file on the data machine was read from `https://ww2.arb.ca.gov/sites/default/files/2026-09/Weekly%20LCFS%20Credit%20Activity%20%28upto%2020%20Sep%2C%202026%29.xlsx`. Source id `carb:lcfs_weekly_credit_price`. Connector: `warehouse/connectors/carb_lcfs.py` (session 132).

CARB's host answers GitHub's runners HTTP 202 with no body (`known_gaps.csv`), so the table is refreshed on the data machine (`warehouse/refresh_board.sh`, `warehouse/run_data_machine.sh`); on the runner the step is recorded as skipped, not failed.

## Vintage and revision

7 January 2019 to 14 September 2026 (the week ending 20 September, the workbook's last) in the file on the data machine, written by run `20261012T234454Z` (12 October 2026). Header: "Rows read: 402 weeks. Cells CARB leaves empty, not written: 82."

Each run reads the page again, deletes the file and writes every week from 7 January 2019 again, so CARB's revisions are taken. The workbook itself is taken from the run's saved raw files when an earlier run saved the same address, so a week's workbook is downloaded once: every row's `retrieved_at` is 6 October 2026 08:16:36Z, when this address was first downloaded and saved, though the run was on 12 October. A table whose newest week is more than 28 days old is not written.

## Shape and variables

Series, 1,124 rows, one entity, `carb:lcfs_credit` (`node` "LCFS credit"); `freq` P1W; `geo` US-CA; `market` and `vintage` empty. A week is Monday to Sunday and `ts_utc` is the date CARB writes in "Week Of" at 00:00:00Z: a Monday in 401 of the 402 weeks, and Tuesday 7 September 2021 (the day after Labor Day) once, kept as CARB writes it.

| Variable | Unit | Rows | Weeks |
|---|---|---|---|
| `credit_price_weekly_avg` | USD/tCO2 | 402 | 7 January 2019 to 14 September 2026 |
| `credit_price_type1_weekly_avg` | USD/tCO2 | 361 | 21 October 2019 to 14 September 2026 |
| `credit_volume` | tCO2 | 361 | 21 October 2019 to 14 September 2026 |

The prices are CARB's volume-weighted average of the week's non-zero transfers, all of them and the Type 1 transfers (executed within 10 days of the agreement), US dollars per credit, one credit being one metric ton of CO2 equivalent. The week of 14 September 2026: 83.77 (all), 84.38 (Type 1), 764,973 credits. The all-transfer price ran from 211.02 at its highest to 46.54 at its lowest.

## Reading the source

- A page linking to no weekly workbook, or to more than one, stops the run.
- A sheet without "Week Of" and the three columns stops it; so does a week listed twice or two weeks less than 6 or more than 8 days apart.
- A cell CARB leaves empty is not written and is counted (82 here: the Type 1 price and the volume in the 41 weeks before 21 October 2019). Any other value that is not a number stops the run.
- A row whose "Week Of" is not a date is dropped. The transaction log in the workbook is not read. The docstring names session 132's ceiling of 1,500,000 rows in all; the code counts none of its own.

## License

`license_verdicts.csv` records CARB, read 10: "may be public", for public and for commercial use, on the State of California's conditions of use: "In general, information presented on this website, unless otherwise indicated, is considered in the public domain. It may be distributed or copied as permitted by law." Its note: CARB's own page was not read. `license_tables.csv` lists the table under CARB. Credit: California Air Resources Board.

## Cross-checks (session 2046)

- The counts above were computed from the rows, read past the header lines. They agree with the header: 402 weeks, and 82 empty cells, 41 in each of the two shorter variables, so 402 + 361 + 361 = 1,124. No (entity, variable, ts_utc) is given twice.
- The 402 weeks are 7 days apart but for the Tuesday week (8 days after the one before, 6 before the one after): no week is missing.
- The Type 1 price differs from the all-transfer price by at most 47.13 in any week; the two cover different sets of transfers, so no equality is expected.

## What it does not hold

- Each transfer: the workbook's transaction log is not read.
- Credit generation, deficits, the bank of credits, and CARB's other LCFS reports.
- Weeks before 2019.
