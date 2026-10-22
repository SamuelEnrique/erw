# EIA Annual Energy Outlook 2026: electricity supply, prices and generating capacity, every case

Energy Research Warehouse (ERW), method note written in session 675 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `eia_aeo_electricity`

Connector: `warehouse/connectors/eia_aeo.py` (session 490).

## Publisher and report

U.S. Energy Information Administration (EIA), Annual Energy Outlook 2026 (AEO2026), read through EIA's API v2, route `aeo/2026`. Source code `eia:aeo`; the report's page is `https://www.eia.gov/outlooks/aeo/`. Two tables of the outlook: Table 8, Electricity Supply, Disposition, Prices, and Emissions; Table 9, Electricity Generating Capacity. The connector asks:

- `https://api.eia.gov/v2/aeo/` for the route list, and takes the newest release (2026 on 21 October 2026);
- `https://api.eia.gov/v2/aeo/2026/facet/scenario/` for the cases;
- `https://api.eia.gov/v2/aeo/2026/data/?frequency=annual&data[]=value&facets[tableId][]=<8|9>&facets[scenario][]=<case>`, one request a table and case.

Requests are 3 seconds apart; a 429 or a 5xx is asked once more after 60 seconds. The key is read from `EIA_API_KEY` and redacted in every `source_url`.

## Vintage and revision rule

- Projection years 2025 to 2050; every row's `x_history` is `PROJECTION`. Retrieved 2026-10-21. `vintage` is empty; the release is in the entity id (`eia_aeo_2026:`).
- Written with `ip.write_snapshot`: a run replaces the whole table. When the API lists a newer release, the next run replaces AEO2026 with it.
- Ceiling: 40 requests a run (the run of 21 October 2026 used 24).

## Shape and columns

Series shape, with six extra columns: `entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_table, x_scenario, x_scenario_name, x_history, x_region, x_dollar_year`.

- `entity`: `eia_aeo_2026:<seriesId>:<case>`, the series' own id and the case's id, for example `eia_aeo_2026:cnsm_NA_elep_NA_tel_NA_usa_blnkwh:altelec`. 119 series.
- `variable`: `value` for every row; `node` the series' name, for example "Electricity : Total Electricity Use".
- `ts_utc`: the projection year's 1 January; `freq` `P1Y`; `geo` `US`; `x_region` `0-0` for every row.
- Units (rows in the table):
  - `MWh`, Table 8, 43 series, from billion kWh times 1,000,000 (12,298 rows);
  - `USD/kWh`, Table 8, 8 series, from cents per kWh times 0.01, each in the AEO's real 2025 dollars (`x_dollar_year` 2025, 2,288 rows) and in nominal dollars (`x_dollar_year` `nominal`, 2,288 rows);
  - `MW`, Table 9, 60 series, from GW times 1,000 (17,160 rows).
- Cases, each 3,094 rows (`x_scenario`, `x_scenario_name`): `altelec` Alternative Electricity; `alttrnp` Alternative Transportation; `cb2026` Counterfactual Baseline case; `electrnp` Alternative Electricity and Transportation; `highZTC` High Zero-Carbon Technology Cost; `higheldmd` High Electricity Demand; `highogs` High Oil and Gas Supply; `hm2026` High Economic Growth; `lm2026` Low Economic Growth; `lowZTC` Low Zero-Carbon Technology Cost; `lowogs` Low Oil and Gas Supply.

34,034 rows in all.

## License

ERW verdict: public. Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Annual Energy Outlook 2026")."

## Cross-check

None in the connector. A unit outside its map stops the run; a table and case with more rows than one page stops it; an (entity, variable, ts_utc) given twice stops it.

## What it does not hold

- These are EIA's projections, not observations; nothing is filled or interpolated.
- No Reference case: AEO2026 names none, and its cases are taken as EIA names them.
- Not taken: Table 8's emissions, 286 rows in short tons and 572 rows in million short tons. Short tons are not in the standard's unit vocabulary.
- Only Tables 8 and 9; no regional table and no other AEO table.
- No earlier AEO edition.
