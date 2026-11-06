# Session 1542 report: periodicals fault 58, the chart line's dead /data anchors

Energy Research Warehouse (ERW), session 1542, chain 172, samueloldlaptop, 6 November 2026, 13:46 to 13:50 UTC. Model: Claude Opus 5.5 (the file names Fable 5.1). Model spend USD 0. No warehouse data written; no preview sent; nothing posted. Branch `wip/1542-periodicals`, cut from `origin/main`.

## What it did, with commits (`a752d3fc5`, `c9ca668b8`)

- **The fault** (row 58, from session 1504's link check, logged by session 1530). The Digest of 6 November reads: "Table `onrr_revenue_monthly`, series `...`: [the table and its download](/data#onrr_revenue_monthly)." `/data` does not list that table, so the reader lands at the top of `/data`. The same happened on 22 October (`eia861m_utility_sales_monthly`) and 23 October (`eia_padd_rail_barge_movements_monthly`).
- **Why**: `/data` shows the live catalogue's public rows (`site/lib/data.ts`, `catalogue`), and the loader keeps out of that catalogue every table under `live_set.yaml`'s `catalogue_hold` (and marks `review_hold` tables "review"). All three tables are under `catalogue_hold`. The live catalogue, read with the public key, holds 135 rows, and none of the three.
- **The fix**: `warehouse/analysis/findings/daily_chart.py` has `on_data_page`, which checks for a coverage table with a public license and on neither hold list, and `table_words`. The line links to `/data#<table>` only for a listed table. For any other it writes: "Table `onrr_revenue_monthly`, series `...`: not yet among the tables /data lists." A live set that cannot be read gives no link.
- **The other anchors**: every `/data#<table>` in the stored Digests and Roundups was checked against the same lists (`runs/s1542/anchors.py`). Four anchors fail, all chart lines (the three issues, and `latest.md`). The fun fact's and the Roundup's links are all to listed tables.
- **Tests**: `tests/test_session1542.py` has 6 tests. On fixtures, it covers a listed, a held, a review, an internal and an unknown table, and an unreadable live set. On the repository's own files, it covers the three held tables, `eia_fuel_spot_prices` as a listed one, and the line with no dead anchor. `tests/test_periodicals.py` and every test that reads `daily_chart.py` pass: 413 tests. No stored issue is rewritten.
- **The faults file**: row 58 says "fixed", with the commit.

## Decisions made without you

- The words for a table `/data` does not list are a plain statement ("not yet among the tables /data lists"), not a link elsewhere. The table is in the record, but its Redivis version is not released, so there is no address to give.

## For Samuel's ruling

- None.
