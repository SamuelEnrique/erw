# Crude oil and petroleum products moved between PADDs by rail and by tanker and barge, a month

Energy Research Warehouse (ERW), method note written in session 678 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_padd_rail_barge_movements_monthly`

Connector: `warehouse/connectors/eia_padd_movements.py` (session 622; the early window of tanker and barge added in session 624).

## Publisher and report

U.S. Energy Information Administration (EIA), Petroleum Supply Monthly, read through EIA's API v2 on two routes, as the header names them:

- `eia:petroleum/move/rail`: receipts by rail between PADDs (route `petroleum/move/rail`, EIA's process RAIL);
- `eia:petroleum/move/tb`: movements by tanker and barge between PADDs (route `petroleum/move/tb`, EIA's process BMV).

Report page: `https://www.eia.gov/petroleum/supply/monthly/`. The connector asks, for each route:

`https://api.eia.gov/v2/<route>/data/?frequency=monthly&data[]=value&start=<first month>`

in pages of 5,000 rows sorted by period and series, 3 seconds apart, with EIA's key read from `EIA_API_KEY` (redacted in every address the table keeps). A page answered with HTTP 429 or 5xx is asked once more after 60 seconds. Ceiling: 20 requests a run.

## Vintage and revision rule

The header gives months 1986-01 to 2026-07: records of EIA's, rail 20,406 and tanker and barge 100,668; 120,742 rows (the rest were blanks). Rail begins in 2010-01. The run of 22 October 2026 (`20261022T035028Z`) asked 0 requests: every page came from `warehouse/raw/eia_padd_movements/`. The previous file held 56,182 rows.

The default first month is 2010-01. `--from 1986-01` reads tanker and barge from its first month: a first month before 2010-01 is asked as a window of its own, to 2009-12 (`end=2009-12`), and then from 2010-01, so the pages of session 622's window answer again from `warehouse/raw`. The header's access line records that split.

The table is written with `ip.write_snapshot`: each run replaces the whole table, so a value EIA revises takes its new value and a series EIA drops leaves the table. A saved page answers the same address again unless `--fresh` is given, so only a `--fresh` run brings EIA's newer months and revisions. `--offline` asks nothing and fails on a page not saved. Each row's `retrieved_at` is the time of the run.

## Shape

Series (`docs/datastandard.md` v0), one row a series and month.

- `entity`: `eia_padd_movements:<series>`, EIA's series id, one a product, mode and pair of areas (for example `eia_padd_movements:ESM_EPC0_RAIL_R10-R20_MBBL`). The table holds 689 entities.
- `variable` and `unit`: `rail_receipts` in `kbbl` (20,406 rows) and `tanker_barge_receipts` in `kbbl` (100,336 rows), EIA's thousand barrels in the month (`mbbl`, kept at a factor of 1). The only unit accepted is `mbbl`.
- `ts_utc`: the month's first day at 00:00:00Z; `freq` `P1M`; `geo` `US` on every row; `market` blank.
- `node`: EIA's series name, which names the receiving area, the area of origin and the product, for example "East Coast (PADD 1) Receipts by Rail from Midwest (PADD 2) of Crude Oil (Thousand Barrels)".
- `source`: the route's id, `eia:petroleum/move/rail` or `eia:petroleum/move/tb`; `source_url` (key redacted), `retrieved_at`, `vintage` (blank).

EIA's area pair is `<receiving>-<origin>` and is kept in the series id: R10-R20 is PADD 1 receiving from PADD 2. Areas are the PADDs R10 to R50 and PADD 1's subdistricts R1X (New England), R1Y (Central Atlantic) and R1Z (Lower Atlantic).

## License

ERW verdict: public (`docs/licenses.md`, "Every table"). The header's line: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Petroleum Supply Monthly")."

## Cross-check

None in the connector. It checks itself: a process that is not its route's, a unit or an area pair not in its map stops the run, as does an (entity, variable, ts_utc) given twice (on two pages, or a series in both routes), and the run fails unless each route's and window's rows read equal the total EIA counts.

## What it does not hold

- No pipeline movements: the pipeline movements of crude oil between PADDs are `eia_padd_crude_pipeline_flows` (`eia_series.py`).
- No rail before 2010-01, where EIA's rail route begins.
- No blank: a record EIA gives without a value has no row, and nothing is filled. A zero EIA gives is kept as 0.
- No area but the PADDs and PADD 1's three subdistricts: an area pair outside them stops the run rather than being left out.
