# Crude oil and petroleum product ending stocks, a week

Energy Research Warehouse (ERW), method note written in session 696 (chain 045) for a table first written on 25 September 2026.

Tables: `eia_petroleum_stocks_weekly`

## Publisher and address

U.S. Energy Information Administration (EIA), Weekly Petroleum Status Report: stocks, through EIA's API v2, route
`petroleum/stoc/wstk`. Document list: `https://api.eia.gov/v2/petroleum/stoc/wstk/`. The data address, as the rows keep
it (decoded here; the key is written `REDACTED`):
`https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key=REDACTED&frequency=weekly&data[0]=value&sort[0][column]=period&sort[0][direction]=asc&sort[1][column]=series&sort[1][direction]=asc&offset=0&length=5000`
followed by one `facets[series][]=` for each of the 8 series below, with `offset` 0, 5000, 10000 and 15000 for the four
pages. Connector: `warehouse/connectors/eia_series.py` (session 7). Page: `https://www.eia.gov/petroleum/supply/weekly/`.

## Vintage and revision

Weekly, the week-ending date EIA reports. coverage.csv: 1982-08-20 to 2026-10-16, 16,831 rows, 8 series. Each run asks
for the full history EIA offers. The write merges into the file already there (`ip.write_csv`): a row with the same
(entity, variable, ts_utc) takes EIA's new value, and a row EIA no longer gives is kept. The header's own line says each
run "replaces all of it"; that holds only while EIA keeps every week. A table is not written if its newest week is more
than 21 days old.

The connector states no request ceiling. It asks in pages of 5,000 records 0.5 seconds apart and tries a failed request
up to 4 times; the file read here holds four page addresses. Each response is saved under
`warehouse/raw/eia_series/<run>/`; the connector does not reuse a saved page.

The file on this machine was rebuilt from the ERW archive by `warehouse/restore_tables.py`, as of run
`20261022T152428Z-github`; the run's own header follows (retrieved `20261022T143537Z`). The rows' `retrieved_at` runs
from 29 September to 22 October 2026: 16,799 rows carry 29 September.

## Shape and variables

Series. `entity` `eia:<EIA series id>`, EIA's id unchanged. `ts_utc` the week-ending date at 00:00:00Z (a Friday on every
row), `freq` `P1W`, `geo` `US` on every row, `market`, `node` and `vintage` blank. One variable, `stocks`, in `kbbl`
(thousand barrels, EIA's `MBBL`).

| EIA's series | EIA's name | Rows | Weeks |
|---|---|---|---|
| `WCESTUS1` | U.S. Ending Stocks excluding SPR of Crude Oil | 2,299 | 1982-08-20 to 2026-10-16 |
| `WCSSTUS1` | U.S. Ending Stocks of Crude Oil in SPR | 2,299 | 1982-08-20 to 2026-10-16 |
| `WCRSTUS1` | U.S. Ending Stocks of Crude Oil | 2,299 | 1982-08-20 to 2026-10-16 |
| `WGTSTUS1` | U.S. Ending Stocks of Total Gasoline | 1,920 | 1990-01-05 to 2026-10-16 |
| `WDISTUS1` | U.S. Ending Stocks of Distillate Fuel Oil | 2,299 | 1982-08-20 to 2026-10-16 |
| `WKJSTUS1` | U.S. Ending Stocks of Kerosene-Type Jet Fuel | 2,299 | 1982-08-20 to 2026-10-16 |
| `WPRSTUS1` | U.S. Propane and Propylene Ending Stocks Excluding Propylene at Terminal | 1,496 | 1993-03-05 to 2026-10-16 |
| `WTTSTUS1` | U.S. Ending Stocks of Crude Oil and Petroleum Products | 1,920 | 1990-01-05 to 2026-10-16 |

No `x_*` fields. Totals and parts are EIA's own: commercial crude (`WCESTUS1`) plus the Strategic Petroleum Reserve
(`WCSSTUS1`) equals total crude (`WCRSTUS1`) in all 2,299 weeks (computed for this note). `WTTSTUS1` is more than the
series here added up: 1,498,245 kbbl in the week ending 16 October 2026, against 1,153,248 for total crude, gasoline,
distillate, jet fuel and propane.

As of 23 October 2026: 16,831 rows, 8 series (counted from the CSV, header lines skipped). Week ending 16 October 2026:
commercial crude 412,517 kbbl, SPR 282,683, total crude and products 1,498,245.

## License

Public: a work of the U.S. government. ERW verdict `public` (`docs/licenses.md`, "Every table": EIA, may be public,
flag and verdict agree). The header: "License: public domain (EIA)". Cite "U.S. Energy Information Administration,
Weekly Petroleum Status Report".

## Cross-check

None in the connector. It checks itself: a unit outside its map, a (series, period) given twice, a non-numeric value, a
series EIA returns nothing for, or a row count other than the total EIA reports stops the table.

Session 559 (`archive/sessions/SESSION_559_REPORT.md`) compared `eia_petroleum_stocks_monthly`'s U.S. stocks at each
month's end with this table's week ending within 3 days of it, 307 months. Distillate (`MDISTUS1` against `WDISTUS1`):
median 1.013, middle half 1.002 to 1.028. Gasoline (`MGTSTUS1` against `WGTSTUS1`): median 1.009, middle half 1.003 to
1.017. The monthly survey runs about 1 percent above the weekly estimate.

## What it does not hold

- U.S. totals only: no PADD and no type of storage. Of the products, only the five above; the rest are inside
  `WTTSTUS1` and not shown apart.
- Six weeks absent from the five series that start in 1982 (counted from the CSV): 1982-09-03, 1982-09-10, 1982-09-17,
  1983-04-22, 1983-05-06 and 1983-05-27. The header counts 0 weeks listed without a value, so EIA's answer has no such
  week.
- Propane and propylene from 1993 to 2002 have rows only from October to late March or April each year (a gap each
  spring and summer, 259 weeks in all, counted from the CSV); every week from October 2002.
- No week before 1982-08-20; gasoline and the grand total begin 1990-01-05.
