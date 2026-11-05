# Refinery and blender net production by product, the U.S., the PADDs and the refining districts, a month

Energy Research Warehouse (ERW), method note written in session 678 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_refinery_production_monthly`

Connector: `warehouse/connectors/eia_refinery_production.py` (session 618, made from session 615's `eia_refinery_inputs.py`; the early window of 2005 to 2014 added in session 635).

## Publisher and report

U.S. Energy Information Administration (EIA), Petroleum Supply Monthly, refinery and blender net production, read through EIA's API v2, route `petroleum/pnp/refp` (source id `eia:petroleum/pnp/refp`). The report page the header names is `https://www.eia.gov/dnav/pet/pet_pnp_refp_dc_nus_mbbl_m.htm`. The connector asks:

`https://api.eia.gov/v2/petroleum/pnp/refp/data/?frequency=monthly&data[]=value&facets[process][]=YPR&start=<first month>`

in pages of 5,000 rows sorted by period and series, 3 seconds apart, with EIA's key read from `EIA_API_KEY` (redacted in every address the table keeps). A page answered with HTTP 429 or 5xx is asked once more after 60 seconds. Ceiling: 37 requests a run.

## Vintage and revision rule

The header gives months 2005-01 to 2026-07: 334,405 records of EIA's, 326,819 rows (the rest were blanks). The run of 22 October 2026 (`20261022T064909Z`) asked 0 requests: every page came from `warehouse/raw/eia_refinery_production/`. The previous file held 175,413 rows.

The default first month is 2015-01. `--from 2005-01` reads 2005 to 2014 as a window of its own (`end=2014-12`) and then 2015-01 on, so the saved pages of the 2015 window answer again. The header's access line records that split (`start=2005-01 (to 2014-12, then from 2015-01)`). The connector's comment says a run from 2005 needs a session of its own.

The table is written with `ip.write_snapshot`: each run replaces the whole table, so a value EIA revises takes its new value and a series EIA drops leaves the table. A saved page answers the same address again unless `--fresh` is given, so only a `--fresh` run brings EIA's newer months and revisions. `--offline` asks nothing and fails on a page not saved. Each row's `retrieved_at` is the time of the run.

## Shape

Series (`docs/datastandard.md` v0), one row a series and month.

- `entity`: `eia_refinery_production:<series>`, EIA's series id, one a product, area and unit (for example `eia_refinery_production:MAPRP2A1`). The table holds 1,488 entities.
- `variable` and `unit`: `net_production` (EIA's process YPR) in `kbbl`, EIA's thousand barrels in the month (163,451 rows), and `net_production_per_day` in `kbbl/d` (163,368 rows). EIA's `mbbl` and `mbbl/d` are kept at a factor of 1.
- `ts_utc`: the month's first day at 00:00:00Z; `freq` `P1M`; `geo` `US` on every row; `market` blank.
- `node`: EIA's series name, the product and area (for example "Refining District Indiana-Illinois-Kentucky Refinery and Blender Net Production of Asphalt and Road Oil (Thousand Barrels)").
- `source`, `source_url` (key redacted), `retrieved_at`, `vintage` (blank).

Areas: the U.S. (NUS), the PADDs (R10 to R50) and the refining districts within them (R2A, R2B, R2C, R3A to R3E, RAP and REC). The PADDs are parts of the U.S. and the districts parts of their PADDs: a sum takes one level. Every row has `geo` `US`; the area is told apart by the series id and name.

## License

ERW verdict: public (`docs/licenses.md`, "Every table"). The header's line: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Petroleum Supply Monthly")."

## Cross-check

None in the connector. It checks itself: a process other than YPR, a unit or an area not in its map stops the run, as does an (entity, variable, ts_utc) given twice, and the run fails unless each window's rows read equal the total EIA counts. The docstring notes that the U.S. and PADD series of the same product are also in `eia_petroleum_snd_monthly` (`refinery_net_production`); the districts are this route's own.

## What it does not hold

- No month before 2005-01.
- No blank: a record EIA gives without a value has no row, and nothing is filled.
- No refinery by name and no state: only the U.S., the PADDs and the refining districts.
- Production only: refinery and blender inputs are `eia_refinery_inputs_monthly`.
