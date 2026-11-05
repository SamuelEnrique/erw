# Petroleum products supplied (EIA's measure of consumption), every product, the U.S. and the five PADDs, a month

Energy Research Warehouse (ERW), method note written in session 678 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_product_supplied_monthly`

Connector: `warehouse/connectors/eia_product_supplied.py` (session 556).

## Publisher and report

U.S. Energy Information Administration (EIA), Petroleum Supply Monthly, product supplied, read through EIA's API v2, route `petroleum/cons/psup` (source id `eia:petroleum/cons/psup`). Product supplied is EIA's measure of consumption. Report page: `https://www.eia.gov/petroleum/supply/monthly/`. The connector asks:

`https://api.eia.gov/v2/petroleum/cons/psup/data/?frequency=monthly&data[]=value&facets[process][]=VPP&start=2017-01`

in pages of 5,000 rows sorted by period and series, 3 seconds apart, with EIA's key read from `EIA_API_KEY` (redacted in every address the table keeps). A page answered with HTTP 429 or 5xx is asked once more after 60 seconds. Ceiling: 19 requests a run.

## Vintage and revision rule

The header gives months 2017-01 to 2026-07: 77,658 records of EIA's, 71,938 rows (the rest were blanks). The run of 21 October 2026 (`20261021T230416Z`) asked 0 requests: every page came from `warehouse/raw/eia_product_supplied/`. The previous file held 0 rows.

The table is written with `ip.write_snapshot`: each run replaces the whole table, so a value EIA revises takes its new value and a series EIA drops leaves the table. A page an earlier run saved in `warehouse/raw` answers the same address again unless `--fresh` is given, so only a `--fresh` run brings EIA's newer months and revisions. `--offline` asks nothing and fails on a page not saved. Each row's `retrieved_at` is the time of the run. `--from YYYY-MM` sets the first month (default 2017-01); there is no separate early window. The docstring says every product, from 2017, fits within a run's ceiling.

## Shape

Series (`docs/datastandard.md` v0), one row a series and month.

- `entity`: `eia_product_supplied:<series>`, EIA's series id, one a product and area in one unit (for example `eia_product_supplied:MAPUPP11`). The table holds 702 entities.
- `variable` and `unit`: `product_supplied` in `kbbl` (EIA's thousand barrels in the month, 35,969 rows) and `product_supplied_per_day` in `kbbl/d` (35,969 rows). EIA's `mbbl` and `mbbl/d` are kept at a factor of 1.
- `ts_utc`: the month's first day at 00:00:00Z; `freq` `P1M`; `geo` `US` on every row; `market` blank.
- `node`: EIA's series name (for example "East Coast (PADD 1) Product Supplied of Asphalt and Road Oil (Thousand Barrels)").
- `source`, `source_url` (key redacted), `retrieved_at`, `vintage` (blank).

Products: every product EIA gives on the route, about 60 by the docstring, with its totals and their parts: a sum takes one level. Areas: the U.S. (NUS) and the PADDs (R10 to R50).

## License

ERW verdict: public (`docs/licenses.md`, "Every table"). The header's line: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Petroleum Supply Monthly")."

## Cross-check

None in the connector. It checks itself: a process other than VPP, a unit or an area not in its map stops the run, as does an (entity, variable, ts_utc) given twice, and the run fails unless the rows read equal the total EIA counts. `eia_petroleum_snd_monthly` also carries a `product_supplied` variable for the U.S. and the PADDs, from 2015; the connector does not compare the two.

## What it does not hold

- No month before 2017-01.
- No blank: a record EIA gives without a value has no row, and nothing is filled.
- No state or sector figures: only the U.S. and the five PADDs.
