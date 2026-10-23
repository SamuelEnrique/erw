# EIA-930 hourly demand by sub-region (sub-balancing-authority)

Energy Research Warehouse (ERW), method note written in session 675 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `eia930_subba_demand_hourly`, `eia930_subba_demand_hourly_2021`, `eia930_subba_demand_hourly_2022`, `eia930_subba_demand_hourly_2023`, `eia930_subba_demand_hourly_2024`, `eia930_subba_demand_hourly_2025`

Connector: `warehouse/connectors/eia930_subba.py` (session 602 for the rolling table, session 612 for the yearly tables).

## Publisher and report

U.S. Energy Information Administration (EIA), Hourly Electric Grid Monitor, demand by subregion (Form EIA-930), read through EIA's API v2, route `electricity/rto/region-sub-ba-data`. Source code in the tables: `eia:electricity/rto/region-sub-ba-data`. The report's page is `https://www.eia.gov/electricity/gridmonitor/`. The connector asks

`https://api.eia.gov/v2/electricity/rto/region-sub-ba-data/data/?frequency=hourly&data[]=value&start=<first hour>&end=<last hour>`

in pages of 5,000 records, sorted by period and sub-region, 3 seconds apart. A 429 or a 5xx is asked once more after 60 seconds. The key is read from `EIA_API_KEY` and is redacted in every `source_url`.

## Vintage and revision rule

- `eia930_subba_demand_hourly`: the last 90 whole UTC days before the run's day (`--days`, default 90; `--through` sets the run's day). The table on the data machine holds hours 2026-07-24T00:00:00Z to 2026-10-21T06:00:00Z, retrieved 2026-10-22 00:46 UTC.
- `eia930_subba_demand_hourly_<year>`: with `--year <y>`, the year's hours (EIA's hour-ending periods `<y>-01-01T01` to `<y+1>-01-01T00`), read in twelve monthly windows, each paged on its own. 2021 (session 684, chain 044), 2022, 2023, 2024 and 2025 are held, each covering `<y>-01-01T00:00:00Z` to `<y>-12-31T23:00:00Z`.
- Every table is written with `ip.write_snapshot`: a run replaces the whole table. Nothing from an earlier run is kept in the file, so a figure EIA revises is replaced at the next run of that window.
- Ceiling: 59 requests a run for the rolling table, 89 for a year. A run that reaches the ceiling writes nothing; the pages it saved in `warehouse/raw/eia930_subba/` answer the next run. A saved page is reused unless `--fresh`; `--offline` asks nothing.

## Shape and columns

Series shape. Columns: `entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage`.

- `entity`: `eia930_subba:<parent>:<subba>`, EIA's parent balancing authority code and sub-region code, for example `eia930_subba:MISO:0001`.
- `variable`: `demand_mw` only, unit `MW`. EIA gives megawatthours in the hour; an hour's megawatthours are the hour's mean megawatts, so the factor is 1. The variable is defined as in `eia930_all_demand`.
- `ts_utc`: the hour's start. EIA's period is the hour's end, so `ts_utc` is the period less one hour, as `warehouse/connectors/eia930.py` does.
- `freq` `PT1H`; `geo` `US`; `market` empty; `node` the sub-region's name and its parent's name, for example "Zone 1 (Midcontinent Independent System Operator, Inc.)"; `vintage` empty.

Sub-regions in the rolling table: 89, under ten parents (BHBA 3, CISO 4, ERCO 8, ISNE 8, MISO 6, NYIS 11, PJM 20, PNM 9, SWPP 17, SWPW 3). The yearly tables hold 82 (2021, 2022 and 2023) and 83 (2024 and 2025).

## License

ERW verdict: public. Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Hourly Electric Grid Monitor")."

## Cross-check

None in the connector. It checks only its own reading: the rows read must equal EIA's `total` for each window, a unit outside its map (megawatthours) stops the run, a record without a parent or sub-region stops it, and an (entity, variable, ts_utc) given twice stops it.

## What it does not hold

- A blank value has no row and nothing is filled. An hour EIA does not give for a sub-region is missing, counted in the run log and the header:
  - rolling table: all 89 sub-regions have fewer than 2,160 hours, 6,063 hours missing;
  - 2022: 38 of 82 sub-regions short of 8,760 hours, 5,489 hours missing;
  - 2023: 24 of 82 short, 988 hours missing;
  - 2024: 64 of 83 short of 8,784 hours, 2,356 hours missing;
  - 2025: 75 of 83 short of 8,760 hours, 3,463 hours missing.
- The rolling table's window asked ran to the end of 21 October 2026; its latest hour is 2026-10-21T06:00:00Z.
- No year before 2022 and no generation, interchange or forecast: demand only.
- No sum to the parent balancing authority. EIA-930 demand by balancing authority is in `eia930_all_demand`; the connector does not compare the sub-regions with it.
