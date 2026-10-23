# Crude oil and petroleum product imports and exports, a week

Energy Research Warehouse (ERW), method note written in session 696 (chain 045) for a table first written on 25 September 2026.

Tables: `eia_petroleum_trade_weekly`

## Publisher and address

U.S. Energy Information Administration (EIA), Weekly Petroleum Status Report: imports and exports, through EIA's API
v2, route `petroleum/move/wkly`. Document list: `https://api.eia.gov/v2/petroleum/move/wkly/`. The data address, as the
rows keep it (decoded here; the key is written `REDACTED`):
`https://api.eia.gov/v2/petroleum/move/wkly/data/?api_key=REDACTED&frequency=weekly&data[0]=value&sort[0][column]=period&sort[0][direction]=asc&sort[1][column]=series&sort[1][direction]=asc&offset=0&length=5000`
followed by one `facets[series][]=` for each of the 7 series below, with `offset` 0, 5000 and 10000 for the three pages.
Connector: `warehouse/connectors/eia_series.py` (session 7). Page: `https://www.eia.gov/petroleum/supply/weekly/`.

## Vintage and revision

Weekly, the week-ending date EIA reports. coverage.csv: 1990-01-05 to 2026-10-16, 12,593 rows, 7 series. Each run asks
for the full history EIA offers. The write merges into the file already there (`ip.write_csv`): a row with the same
(entity, variable, ts_utc) takes EIA's new value, and a row EIA no longer gives is kept. The header's own line says each
run "replaces all of it"; that holds only while EIA keeps every week. A table is not written if its newest week is more
than 21 days old.

The connector states no request ceiling. It asks in pages of 5,000 records 0.5 seconds apart and tries a failed request
up to 4 times; the file read here holds three page addresses. Each response is saved under
`warehouse/raw/eia_series/<run>/`; the connector does not reuse a saved page.

The file on this machine was rebuilt from the ERW archive by `warehouse/restore_tables.py`, as of run
`20261022T152428Z-github`; the run's own header follows (retrieved `20261022T143537Z`). The rows' `retrieved_at` runs
from 29 September to 22 October 2026: 12,565 rows carry 29 September.

## Shape and variables

Series. `entity` `eia:<EIA series id>`, EIA's id unchanged. `ts_utc` the week-ending date at 00:00:00Z (a Friday on every
row), `freq` `P1W`, `geo` `US` on every row, `market`, `node` and `vintage` blank. One variable, `flow`, in `kbbl/d`
(thousand barrels a day, EIA's `MBBL/D`).

| EIA's series | EIA's name | Rows | Weeks |
|---|---|---|---|
| `WCREXUS2` | U.S. Exports of Crude Oil | 1,863 | 1991-02-08 to 2026-10-16 |
| `WRPEXUS2` | U.S. Exports of Total Petroleum Products | 1,862 | 1991-02-08 to 2026-10-16 |
| `WTTEXUS2` | U.S. Exports of Crude Oil and Petroleum Products | 1,863 | 1991-02-08 to 2026-10-16 |
| `WCRIMUS2` | U.S. Imports of Crude Oil | 1,920 | 1990-01-05 to 2026-10-16 |
| `WRPIMUS2` | U.S. Imports of Total Petroleum Products | 1,920 | 1990-01-05 to 2026-10-16 |
| `WTTIMUS2` | U.S. Imports of Crude Oil and Petroleum Products | 1,863 | 1991-02-08 to 2026-10-16 |
| `WCRNTUS2` | U.S. Net Imports of Crude Oil | 1,302 | 2001-11-09 to 2026-10-16 |

No `x_*` fields. Exports and imports are positive. Net imports can be negative: one week is, 24 April 2026, at -688.

Totals and parts are EIA's own (computed for this note): net crude imports equal crude imports less crude exports in
1,301 of 1,302 weeks (2021-08-06 differs by 1 kbbl/d). Total imports equal crude plus products in 1,770 of 1,863 weeks;
the other 93, from 2019-08-09 to 2026-09-04, differ by 1 kbbl/d. Total exports equal crude plus products in 1,735 of
1,862 weeks; the other 127 all fall from 1991-02-08 to 1993-07-09 and differ by up to 242 kbbl/d.

As of 23 October 2026: 12,593 rows, 7 series (counted from the CSV, header lines skipped). Week ending 16 October 2026:
crude exports 3,442 kbbl/d, crude imports 5,758, net crude imports 2,316, product exports 7,407.

## License

Public: a work of the U.S. government. ERW verdict `public` (`docs/licenses.md`, "Every table": EIA, may be public,
flag and verdict agree). The header: "License: public domain (EIA)". Cite "U.S. Energy Information Administration,
Weekly Petroleum Status Report".

## Cross-check

None in the connector. It checks itself: a unit outside its map, a (series, period) given twice, a non-numeric value, a
series EIA returns nothing for, or a row count other than the total EIA reports stops the table.

## What it does not hold

- U.S. totals only: no PADD, no country of origin or destination (monthly crude imports by country are in
  `eia_crude_imports_by_country`), no product shown apart from the products total.
- No net imports of products or of the total, only of crude, and those only from 2001-11-09.
- No export week before 1991-02-08; total imports also begin then. Crude and product imports begin 1990-01-05.
- One week absent inside a span (counted from the CSV): product exports, 1993-07-23. The header counts 0 weeks listed
  without a value, so EIA's answer has no such week.
