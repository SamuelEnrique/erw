# The utilities' and the hosting industry's revenue a quarter, from 2003 (the Census Bureau's Quarterly Services Survey, 2024 benchmark)

Energy Research Warehouse (ERW), method note written in session 2261 (chain 102) for a table first written on 24 October 2026 (session 2264).

Tables: `census_qss_utilities_hosting_quarterly`

## Publisher and address

The U.S. Census Bureau's Quarterly Services Survey (QSS) estimates the revenue and expenses of employer firms in the service industries each quarter. Each year it publishes a benchmark dataset of the whole history, revised to its annual surveys, in its economic time series format.

`https://www2.census.gov/services/qss/2024/qss-mf-24.csv` (the fourth quarter of 2003 to the fourth quarter of 2024), linked from `https://www.census.gov/services/qss/benchmark.html`. The dataset's read-me (`readme.txt` beside it) describes its eight sections.

www.census.gov has no robots file (HTTP 404, read 460). www2.census.gov's robots file sets rules for named crawlers only, none for other readers (session 2264).

## Vintage and revision

The 2024 benchmark was published in March 2025: its "DATA UPDATED ON" section reads Thursday, 13 March 2025. The next benchmark revises the history and reaches the fourth quarter of 2025. The quarters after the benchmark's last are in the current release's workbook (`qss-all-current.xlsx`, six quarters), which this table does not take. The connector asks the 2024 file again on each run unless `--offline`. A later benchmark has a new address, so the connector's `URL` must be moved to it.

## Shape and variables

Series, 784 rows, 5 entities, 5 variables, from the fourth quarter of 2003 (518) and the first quarter of 2010 (22, 2211, 2212, 2213) to the fourth quarter of 2024. Unit USD (QSS's millions times 1,000,000), freq P3M, `ts_utc` the quarter's first day, geo US.

- `census_qss:22` (utilities), `census_qss:2211` (electric power generation, transmission and distribution), `census_qss:2212` (natural gas distribution), `census_qss:2213` (water, sewage and other systems): `total_revenue` and `total_revenue_sa` (seasonally adjusted), 60 quarters each.
- `census_qss:518` (data processing, hosting and related services): `total_revenue` and `total_revenue_sa` (85 quarters each), `revenue_from_businesses` (45), `revenue_from_governments` (60) and `revenue_from_households` (29).
- `x_cv`: the coefficient of variation QSS gives for the figure, in percent, where it gives one.
- `node`: the category as the Census Bureau names it.

## Checks the connector makes

- The dataset must hold its CATEGORIES, DATA TYPES, ERROR TYPES, TIME PERIODS and DATA sections.
- The five categories must be found by their codes (22T, 2211T, 22121T, 2213T, 518T).
- Every period must read as Qn-YYYY.
- A key given twice stops the run.
- Only data types in millions of dollars are taken; percent changes are not.
- A figure QSS marks S (below publication standards) or N, or leaves out, has no row and is counted: 121 marked S.

## The cross-check

From `runs/c102/s2264/cross.out`: each year's not adjusted quarters sum to within 0.5 percent of four times the mean of its adjusted quarters for 22, 2211, 2213 and 518, and within 2.3 percent for 2212. In whole years, data processing and hosting's revenue rose from 130.8 billion USD (2015) to 374.9 billion (2024); electric power's from 462.8 to 579.3 billion; the utilities' from 575.2 to 746.1 billion.

## License

Public: the Census Bureau's verdict (read 17), a work of the U.S. government.

## Found while writing this note

- The utilities' series start in 2010 in this benchmark, though 518's start in 2003.
- `revenue_from_households` for 518 has 29 quarters, the rest marked S.

## What it does not hold

- The quarters after the fourth quarter of 2024 (in the current release, not taken).
- Expenses, which QSS gives for other industries, not for these five in the benchmark.
- Any industry but the five, or any geography but the nation.
