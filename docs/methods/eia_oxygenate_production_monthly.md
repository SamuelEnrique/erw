# Oxygenate plant production (fuel ethanol, MTBE and other oxygenates), the U.S. and the PADDs, a month

Energy Research Warehouse (ERW), method note written in session 678 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_oxygenate_production_monthly`

Connector: `warehouse/connectors/eia_oxygenate_production.py` (session 631, made from session 618's `eia_refinery_production.py`).

## Publisher and report

U.S. Energy Information Administration (EIA), Petroleum Supply Monthly, oxygenate plant production, read through EIA's API v2, route `petroleum/pnp/oxy` (source id `eia:petroleum/pnp/oxy`). The report page the header names is `https://www.eia.gov/dnav/pet/pet_pnp_oxy_dc_nus_mbbl_m.htm`. The connector asks:

`https://api.eia.gov/v2/petroleum/pnp/oxy/data/?frequency=monthly&data[]=value&facets[process][]=YOP&facets[process][]=YNP&start=1981-01`

in pages of 5,000 rows sorted by period and series, 3 seconds apart, with EIA's key read from `EIA_API_KEY` (redacted in every address the table keeps). A page answered with HTTP 429 or 5xx is asked once more after 60 seconds. Ceiling: 7 requests a run.

## Vintage and revision rule

The header gives months 1981-01 to 2026-07: 6,446 records of EIA's, 6,006 rows (the rest were blanks). The run of 22 October 2026 (`20261022T050700Z`) asked 0 requests: every page came from `warehouse/raw/eia_oxygenate_production/`. The previous file held 0 rows.

The table is written with `ip.write_snapshot`: each run replaces the whole table, so a value EIA revises takes its new value and a series EIA drops leaves the table. A page an earlier run saved in `warehouse/raw` answers the same address again unless `--fresh` is given, so only a `--fresh` run brings EIA's newer months and revisions. `--offline` asks nothing and fails on a page not saved. Each row's `retrieved_at` is the time of the run. `--from YYYY-MM` sets the first month; the default, 1981-01, is the first month the table holds, and there is no separate early window.

## Shape

Series (`docs/datastandard.md` v0), one row a series and month.

- `entity`: `eia_oxygenate_production:<series>`, EIA's series id, one a product, process, area and unit (for example `eia_oxygenate_production:M_EPOOXE_YOP_NUS_1`). The table holds 30 entities.
- `variable` and `unit`:
  - `oxygenate_plant_production` (EIA's process YOP), `kbbl` (EIA's thousand barrels in the month), 2,712 rows;
  - `oxygenate_plant_production_per_day`, `kbbl/d`, 2,700 rows;
  - `biofuels_plant_net_production` (EIA's process YNP), `kbbl`, 297 rows;
  - `biofuels_plant_net_production_per_day`, `kbbl/d`, 297 rows.
  EIA's units `mbbl` and `mbbl/d` are kept at a factor of 1.
- `ts_utc`: the month's first day at 00:00:00Z; `freq` `P1M`; `geo` `US` on every row; `market` blank.
- `node`: EIA's series name, the product and area (for example "U.S. Oxygenate Plant Production of Fuel Ethanol (Thousand Barrels)").
- `source`, `source_url` (key redacted), `retrieved_at`, `vintage` (blank).

Areas: the U.S. (NUS) and the PADDs (R10 to R50). The PADDs are parts of the U.S.: a sum takes one level. The U.S. series, as EIA names them: oxygenate plant production of fuel ethanol (1981-01 to 2026-07), of MTBE (2005-01 to 2025-12), of oxygenates excluding fuel ethanol (2010-01 to 2026-07), and biofuels plant net production of other oxygenates (2010-01 to 2025-12).

## License

ERW verdict: public (`docs/licenses.md`, "Every table"). The header's line: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Petroleum Supply Monthly")."

## Cross-check

None in the connector. It checks itself: a process other than YOP and YNP, a unit or an area not in its map stops the run, as does an (entity, variable, ts_utc) given twice, and the run fails unless the rows read equal the total EIA counts.

## What it does not hold

- No blank: a record EIA gives without a value has no row, and nothing is filled.
- No state, district or plant figures: only the U.S. and the five PADDs.
- Series EIA has ended stop where EIA stops them (MTBE and the biofuels plant series at 2025-12 in this run).
