# Petroleum product stocks at the month's end: gasoline, distillate, propane and residual fuel, a month

Energy Research Warehouse (ERW), method note written in session 678 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_petroleum_stocks_monthly`

Connector: `warehouse/connectors/eia_petroleum_stocks.py` (session 559).

## Publisher and report

U.S. Energy Information Administration (EIA), Petroleum Supply Monthly, product stocks, read through EIA's API v2, route `petroleum/stoc/ts` (source id `eia:petroleum/stoc/ts`). Report page: `https://www.eia.gov/petroleum/supply/monthly/`. The connector asks:

`https://api.eia.gov/v2/petroleum/stoc/ts/data/?frequency=monthly&data[]=value&facets[process][]=SAE&start=2001-01`

in pages of 5,000 rows sorted by period and series, 3 seconds apart, with EIA's key read from `EIA_API_KEY` (redacted in every address the table keeps). A page answered with HTTP 429 or 5xx is asked once more after 60 seconds. Ceiling: 19 requests a run.

The docstring records what the route held on 21 October 2026: total gasoline, distillate fuel oil and its three sulfur grades, propane and propylene, and residual fuel oil; no crude oil, and no breakdown by type of storage, despite the route's name.

## Vintage and revision rule

The header gives months 2001-01 to 2026-07: 18,742 records of EIA's, 18,247 rows (the rest were blanks). The run of 21 October 2026 (`20261021T231729Z`) asked 0 requests: every page came from `warehouse/raw/eia_petroleum_stocks/`. The previous file held 0 rows.

The table is written with `ip.write_snapshot`: each run replaces the whole table, so a value EIA revises takes its new value and a series EIA drops leaves the table. A page an earlier run saved in `warehouse/raw` answers the same address again unless `--fresh` is given, so only a `--fresh` run brings EIA's newer months and revisions. `--offline` asks nothing and fails on a page not saved. Each row's `retrieved_at` is the time of the run. `--from YYYY-MM` sets the first month (default 2001-01); there is no separate early window.

## Shape

Series (`docs/datastandard.md` v0), one row a series and month.

- `entity`: `eia_petroleum_stocks:<series>`, EIA's series id, one a product and area (for example `eia_petroleum_stocks:MD1ST_NUS_1`). The table holds 63 entities.
- `variable`: `ending_stocks` (EIA's process SAE), `unit` `kbbl`: thousand barrels held at the month's end. Every row has this variable and unit. The connector would write `ending_stocks_per_day` in `kbbl/d` for a series in thousand barrels a day; the table holds none.
- `ts_utc`: the month's first day at 00:00:00Z, though the stock is the one at the month's end; `freq` `P1M`; `geo` `US` on every row; `market` blank.
- `node`: EIA's series name (for example "U.S. Ending Stocks of Distillate Fuel Oil, Greater than 15 to 500 ppm Sulfur (Thousand Barrels)").
- `source`, `source_url` (key redacted), `retrieved_at`, `vintage` (blank).

Areas: the U.S. (NUS), the PADDs (R10 to R50) and PADD 1's sub-districts (R1X New England, R1Y Central Atlantic, R1Z Lower Atlantic). Totals and parts (the U.S. and the PADDs, PADD 1 and its sub-districts, distillate and its grades) are EIA's: a sum takes one level.

The U.S. series, as EIA names them: total gasoline, distillate fuel oil, its grades greater than 500 ppm and greater than 15 to 500 ppm sulfur, and residual fuel oil, each 2001-01 to 2026-07; distillate of 0 to 15 ppm sulfur from 2004-01; propane and propylene 2001-01 to 2021-12.

## License

ERW verdict: public (`docs/licenses.md`, "Every table"). The header's line: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Petroleum Supply Monthly")."

## Cross-check

None in the connector. It checks itself: a process other than SAE, a unit or an area not in its map stops the run, as does an (entity, variable, ts_utc) given twice, and the run fails unless the rows read equal the total EIA counts.

## What it does not hold

- No crude oil stocks and no stocks by type of storage: the route does not give them (docstring, 21 October 2026).
- No propane and propylene after 2021-12 in this route.
- No blank: a record EIA gives without a value has no row, and nothing is filled.
- No month before 2001-01.
