# U.S. Wind Turbine Database: every utility-scale land-based and offshore wind turbine

Energy Research Warehouse (ERW), method note written in session 675 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `uswtdb_wind_turbines`

Connector: `warehouse/connectors/uswtdb.py` (session 496).

## Publisher and report

U.S. Geological Survey, Lawrence Berkeley National Laboratory and American Clean Power Association, U.S. Wind Turbine Database (USWTDB), API v1. Source code `usgs:uswtdb`; the database's page is `https://energywind.usgs.gov/uswtdb/`. The connector reads USGS's public API, which needs no key:

`https://energy.usgs.gov/api/uswtdb/v1/turbines?limit=10000&offset=<k>`

in pages of 10,000 turbines, 3 seconds apart, until a page comes back short.

## Vintage and revision rule

- One snapshot of the whole database as the API gives it on the run's day: retrieved 2026-10-21 18:33 UTC, 8 requests of 30.
- `vintage` is empty: the API gives no release date.
- Written with `ip.write_snapshot`: a run replaces the whole table, so a turbine the database drops leaves the table.
- Ceiling: 30 requests a run. Every page is asked fresh.

## Shape and columns

Entities shape. Standard columns: `entity_id, entity_type, name, geo, lat, lon, capacity_mw, status, status_date, operator, source, source_url, retrieved_at, vintage`.

- `entity_id`: `uswtdb:<case_id>`, the database's id of the turbine, for example `uswtdb:3000001`.
- `entity_type` `generator`; `name` the project's name (`p_name`) and "turbine <case_id>"; `geo` `US-<state>`; `lat`, `lon` from `ylat`, `xlong`.
- `capacity_mw`: the turbine's rated capacity (`t_cap`, kW) divided by 1,000.
- `status`, `status_date` and `operator` empty: the database lists installed turbines, gives no status and names no owner.

The database's own fields follow, renamed with their units: `case_id`, `eia_plant_id` (`eia_id`), `project_name` (`p_name`), `project_year` (`p_year`), `project_turbines` (`p_tnum`), `project_capacity_mw` (`p_cap`), `state`, `county`, `fips_county`, `manufacturer` (`t_manu`), `model` (`t_model`), `turbine_capacity_kw` (`t_cap`), `hub_height_m` (`t_hh`), `rotor_diameter_m` (`t_rd`), `rotor_swept_area_m2` (`t_rsa`), `total_height_m` (`t_ttlh`), `confidence_attributes` (`t_conf_atr`), `confidence_location` (`t_conf_loc`), `image_date` (`t_img_date`, rewritten from M/D/YYYY to YYYY-MM-DD), `image_source` (`t_img_src`), `retrofit`, `retrofit_year`, `offshore` (`t_offshore`, 1 for offshore), `faa_ors`, `faa_asn`, `usgs_project_id` (`usgs_pr_id`).

From the header: 77,839 turbines; capacity 159,587 MW; 129 offshore; 72,788 with an EIA plant id.

## License

ERW verdict: unsettled. The table is flagged public, but licenses.md records the publisher's terms as not settled (needs written permission by default) and the publisher, USGS with LBNL and ACP, as not read. Header: "License: public (USGS data are in the U.S. public domain; cite "U.S. Wind Turbine Database, USGS, LBNL and ACP")." The connector quotes USGS: "USGS-authored or produced data and information are considered to be in the U.S. Public Domain" (record 87 of license_reads.csv).

## Cross-check

None in the connector. It stops when a field it maps is missing from the API's records, when a `case_id` is given twice, or when an image date is not M/D/YYYY.

## What it does not hold

- A blank stays blank; nothing is filled. Some turbines have no rated capacity (`capacity_mw` blank), no maker or model, or no EIA plant id (5,051 of 77,839 lack one, by the header's counts).
- No status, commissioning date or retirement: the database lists installed turbines, and `project_year` is the project's year, not the turbine's.
- No owner or operator.
- No generation or capacity factor.
