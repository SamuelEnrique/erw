# Refinery capacity as of January 1: operable distillation and downstream charge capacity, and the number of refineries, a year

Energy Research Warehouse (ERW), method note written in session 678 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_refinery_capacity_annual`

Connector: `warehouse/connectors/eia_refinery_capacity.py` (session 614; the early window of 1982 to 1994 added in session 619).

## Publisher and report

U.S. Energy Information Administration (EIA), Refinery Capacity Report (Form EIA-820), read through EIA's API v2, route `petroleum/pnp/cap1` (source id `eia:petroleum/pnp/cap1`). Report page: `https://www.eia.gov/petroleum/refinerycapacity/`. The connector asks:

`https://api.eia.gov/v2/petroleum/pnp/cap1/data/?frequency=annual&data[]=value&start=<first year>`

with no facet (every process, area and unit of the route), in pages of 5,000 rows sorted by period and series, 3 seconds apart, with EIA's key read from `EIA_API_KEY` (redacted in every address the table keeps). A page answered with HTTP 429 or 5xx is asked once more after 60 seconds. Ceiling: 5 requests a run.

## Vintage and revision rule

The header gives years 1982 to 2026: 65,350 records of EIA's, 62,804 rows (the rest were blanks). The run of 22 October 2026 (`20261022T024237Z`) asked 0 requests: every page came from `warehouse/raw/eia_refinery_capacity/`. The previous file held 51,504 rows.

The default first year is 1995: the route holds 65,350 rows from 1982, beyond session 614's ceiling. `--from 1982` reads 1982 to 1994 as a window of its own (`end=1994`) and then 1995 on, so session 614's saved pages answer the later years again. The header's access line records that split (`start=1982 (to 1994, then from 1995)`).

The table is written with `ip.write_snapshot`: each run replaces the whole table, so a value EIA revises takes its new value and a series EIA drops leaves the table. A saved page answers the same address again unless `--fresh` is given, so only a `--fresh` run brings EIA's newer years and revisions. `--offline` asks nothing and fails on a page not saved. Each row's `retrieved_at` is the time of the run.

## Shape

Series (`docs/datastandard.md` v0), one row a series and year.

- `entity`: `eia_refinery_capacity:<series>`, EIA's series id, one a process, area and unit (for example `eia_refinery_capacity:8_NA_8CCF_NUS_5`). The table holds 2,009 entities.
- `variable` and `unit`, set by EIA's unit:
  - `capacity_per_calendar_day`, `kbbl/d`: EIA's barrels per calendar day (B/CD) divided by 1,000; 11,006 rows;
  - `capacity_per_stream_day`, `kbbl/d`: EIA's barrels per stream day (B/SD) divided by 1,000; 45,699 rows;
  - `refineries`, `count`: the number of refineries (operable, operating or idle, by EIA's process); 6,099 rows.
  A barrel per stream day is a day's capacity running without downtime; a barrel per calendar day allows for it.
- `ts_utc`: January 1 of EIA's year at 00:00:00Z (EIA's "as of January 1"); `freq` `P1Y`; `market` blank.
- `geo`: `US-<state>` for a state (EIA's area `S<state>`), `US-PR`, `US-GU` and `US-VI` for Puerto Rico, Guam and the Virgin Islands, and `US` for the U.S. and the PADDs. The table holds 44 values of `geo`.
- `node`: EIA's series name, the process, area and unit (for example "U.S. Refinery Catalytic Cracking, Fresh Feed Downstream Charge Capacity as of January 1 (Barrels per Stream Day)").
- `source`, `source_url` (key redacted), `retrieved_at`, `vintage` (blank).

The process (atmospheric distillation, vacuum distillation, cracking, reforming, hydrotreating, coking and others) is in the entity and the node, not in a column of its own. The PADDs (R10 to R50) and the states are parts of the U.S.: a sum takes one level. A PADD row has `geo` `US`, so the PADD is told apart only by its series id and name.

## License

ERW verdict: public (`docs/licenses.md`, "Every table"). The header's line: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Refinery Capacity Report")."

## Cross-check

None in the connector. It checks itself: a unit or an area not in its map stops the run, as does an (entity, variable, ts_utc) given twice, and the run fails unless each window's rows read equal the total EIA counts.

## What it does not hold

- No refinery by name: the route gives states, PADDs and the U.S., not single plants.
- No year before 1982.
- No blank: a record EIA gives without a value has no row, and nothing is filled. A zero EIA gives is kept as 0.
- Capacity, not throughput: what refineries ran is in `eia_refinery_inputs_monthly` and `eia_refinery_weekly`.
