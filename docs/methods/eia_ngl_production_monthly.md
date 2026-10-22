# Natural gas liquids produced at natural gas processing plants, by product and area, a month

Energy Research Warehouse (ERW), method note written in session 678 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_ngl_production_monthly`

Connector: `warehouse/connectors/eia_ngl_production.py` (session 629, made from session 618's `eia_refinery_production.py`).

## Publisher and report

U.S. Energy Information Administration (EIA), Petroleum Supply Monthly, natural gas plant field production, read through EIA's API v2, route `petroleum/pnp/gp` (source id `eia:petroleum/pnp/gp`). The report page the header names is `https://www.eia.gov/dnav/pet/pet_pnp_gp_dc_nus_mbbl_m.htm`. The connector asks:

`https://api.eia.gov/v2/petroleum/pnp/gp/data/?frequency=monthly&data[]=value&facets[process][]=FPF&start=<first month>`

in pages of 5,000 rows sorted by period and series, 3 seconds apart, with EIA's key read from `EIA_API_KEY` (the key is redacted in every address the table keeps). A page answered with HTTP 429 or 5xx is asked once more after 60 seconds.

## Vintage and revision rule

The header gives months 1973-01 to 2026-07: 114,306 records of EIA's, 110,896 rows (the rest were blanks). The run of 22 October 2026 (`20261022T065502Z`) asked 0 requests: every page came from `warehouse/raw/eia_ngl_production/`. The previous file held 31,956 rows.

The table is written with `ip.write_snapshot`: each run replaces the whole table, so a value EIA revises takes its new value and a series EIA drops leaves the table. A page an earlier run saved in `warehouse/raw` answers the same address again unless `--fresh` is given, so only a `--fresh` run brings EIA's newer months and revisions. `--offline` asks nothing and fails on a page not saved. Each row's `retrieved_at` is the time of the run, also when its page came from the raw files.

`--from YYYY-MM` sets the first month; the connector's default is 2015-01. The header records a run from 1973-01 in two windows (`start=1973-01`, to 2014-12, then from 2015-01) and a ceiling of 18 requests. The connector in this worktree has neither the early window nor that ceiling (its ceiling is 17 requests a run), so the table on the data machine was written by a later version of the script than the one here.

## Shape

Series (`docs/datastandard.md` v0), one row a series and month.

- `entity`: `eia_ngl_production:<series>`, EIA's series id, one a product, area and unit (for example `eia_ngl_production:M_EPL2_FPF_NUS_MBBLD`). The table holds 284 entities.
- `variable` and `unit`: `field_production` in `kbbl` (EIA's thousand barrels in the month, 55,400 rows) and `field_production_per_day` in `kbbl/d` (55,496 rows). EIA's units `mbbl` and `mbbl/d` are kept at a factor of 1.
- `ts_utc`: the month's first day at 00:00:00Z; `freq` `P1M`; `geo` `US` on every row; `market` blank.
- `node`: EIA's series name, which names the product and the area (for example "U.S. Field Production of Natural Gas Liquids (Thousand Barrels per Day)").
- `source`, `source_url` (the API address, key redacted), `retrieved_at`, `vintage` (blank).

Products, as EIA's U.S. series names give them: natural gas liquids, ethane, propane, normal butane, isobutane, natural gasoline, and, ending in 2021-12, gas plant production of liquefied petroleum gases and of pentanes plus; condensate and scrubber oil from 2023-08. Areas: the U.S. (NUS), the PADDs (R10 to R50) and the refining districts within them (R2A, R2B, R2C, R3A to R3E, RAP and REC). The PADDs are parts of the U.S. and the districts parts of their PADDs: a sum takes one level. The U.S. daily series of natural gas liquids begins in 1973-01; most other U.S. series begin in 1981-01.

## License

ERW verdict: public (`docs/licenses.md`, "Every table"). The header's line: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Petroleum Supply Monthly")."

## Cross-check

None in the connector. It checks itself: a process other than FPF, a unit or an area not in its map stops the run, as does an (entity, variable, ts_utc) given twice, and the run fails unless the rows read equal the total EIA counts. The docstring notes that the U.S. and PADD series of the same products are also in `eia_petroleum_snd_monthly` (`field_production`); the districts are this route's own.

## What it does not hold

- No blank: a record EIA gives without a value has no row, and nothing is filled.
- No state or plant figures, only the U.S., the PADDs and the refining districts.
- Only EIA's process FPF (field production) is asked; any other process of the route would stop the run.
- Series EIA has ended stop where EIA stops them (the liquefied petroleum gases and pentanes plus series at 2021-12).
