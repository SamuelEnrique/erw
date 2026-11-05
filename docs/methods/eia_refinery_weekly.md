# Weekly refinery inputs, operable capacity and utilization, the U.S. and the five PADDs

Energy Research Warehouse (ERW), method note written in session 678 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_refinery_weekly`

Connector: `warehouse/connectors/eia_refinery_weekly.py` (session 543).

## Publisher and report

U.S. Energy Information Administration (EIA), Weekly Petroleum Status Report, refinery inputs and utilization, read through EIA's API v2, route `petroleum/pnp/wiup` (source id `eia:petroleum/pnp/wiup`). Report page: `https://www.eia.gov/petroleum/supply/weekly/`. The connector asks:

`https://api.eia.gov/v2/petroleum/pnp/wiup/data/?frequency=weekly&data[]=value&facets[process][]=YIR&facets[process][]=YIY&facets[process][]=YRL&facets[process][]=YUP&start=2010-01-01`

in pages of 5,000 rows sorted by period and series, 3 seconds apart, with EIA's key read from `EIA_API_KEY` (redacted in every address the table keeps). A page answered with HTTP 429 or 5xx is asked once more after 60 seconds. Ceiling: 19 requests a run in the code (`CEILING`) and in the header ("0 requests of 19"); the docstring still says 20.

## Vintage and revision rule

The header gives weeks 2010-01-01 to 2026-10-16: 51,259 records of EIA's, 50,753 with a value. The run of 21 October 2026 (`20261021T214804Z`) asked 0 requests: every page came from `warehouse/raw/eia_refinery_weekly/`. The previous file held 0 rows.

The table is written with `ip.write_snapshot`: each run replaces the whole table, so a value EIA revises takes its new value and a series EIA drops leaves the table. A page an earlier run saved in `warehouse/raw` answers the same address again unless `--fresh` is given, so only a `--fresh` run brings EIA's newer weeks and revisions. `--offline` asks nothing and fails on a page not saved. Each row's `retrieved_at` is the time of the run. `--from YYYY-MM-DD` sets the first week (default 2010-01-01); there is no separate early window.

## Shape

Series (`docs/datastandard.md` v0), one row a series and week.

- `entity`: `eia_refinery:<series>`, EIA's series id, one a process, product and area (for example `eia_refinery:WCRRIP12`). The prefix is `eia_refinery`, not the table's name. The table holds 59 entities.
- `variable` and `unit`, by EIA's process:
  - `net_input` (YIR, refinery and blender net input, by product), `kbbl/d`, 30,802 rows;
  - `refinery_net_input` (YIY, by product), `kbbl/d`, 10,524 rows;
  - `operable_capacity` (YRL), `kbbl/d`, 5,152 rows;
  - `utilization` (YUP), `ratio`: EIA's percent divided by 100, 4,275 rows.
  EIA's `mbbl/d` is kept at a factor of 1.
- `ts_utc`: EIA's week-ending date at 00:00:00Z, as in `eia_petroleum_supply_weekly`; `freq` `P1W`; `geo` `US` on every row; `market` blank.
- `node`: EIA's series name (for example "East Coast (PADD 1) Refiner Net Input of Crude Oil (Thousand Barrels per Day)").
- `source`, `source_url` (key redacted), `retrieved_at`, `vintage` (blank).

Areas: the U.S. (NUS) and the PADDs (R10 to R50). The U.S. series include gross inputs into refineries, refiner net input of crude oil, and refiner and blender net input of gasoline blending components, of fuel ethanol, of RBOB and of conventional CBOB, GTAB and other blending components; the last five begin in the week ending 2010-06-04.

## License

ERW verdict: public (`docs/licenses.md`, "Every table"). The header's line: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Weekly Petroleum Status Report")."

## Cross-check

None in the connector. It checks itself: a process, unit or area not in its map stops the run, as does an (entity, variable, ts_utc) given twice, and the run fails unless the rows read equal the total EIA counts.

## What it does not hold

- No week before 2010-01-01.
- No blank: a record EIA gives without a value has no row, and nothing is filled.
- No refining districts or states: only the U.S. and the five PADDs.
- No refinery output: the weekly route read here is inputs and utilization. The monthly inputs and production are `eia_refinery_inputs_monthly` and `eia_refinery_production_monthly`.
