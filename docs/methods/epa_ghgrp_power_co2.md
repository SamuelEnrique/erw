# EPA Greenhouse Gas Reporting Program: power plants' reported CO2 by year

Energy Research Warehouse (ERW), method note written in session 675 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `epa_ghgrp_power_co2`

Connector: `warehouse/connectors/ghgrp_power.py` (session 492).

## Publisher and report

U.S. Environmental Protection Agency (EPA), Greenhouse Gas Reporting Program (GHGRP), data summary spreadsheets (2023). Source code `epa:ghgrp`. The connector reads:

- the data-sets page, `https://www.epa.gov/ghgreporting/data-sets`, to find the newest summary zip and the ORIS crosswalk it links;
- the zip, `https://www.epa.gov/system/files/other-files/2024-10/2023_data_summary_spreadsheets.zip` (one workbook a reporting year, `ghgp_data_<year>.xlsx`, sheet "Direct Emitters" or "Direct Point Emitters");
- EPA's GHGRP-to-ORIS crosswalk, `https://www.epa.gov/system/files/documents/2022-04/ghgrp_oris_power_plant_crosswalk_12_13_21.xlsx` (sheet "ORIS Crosswalk").

## Which facilities

In each year's workbook, the facilities whose "Industry Type (subparts)" includes subpart D (electricity generation) that year. A facility reporting under D and other subparts is taken, with its row's figures as the workbook gives them.

## Vintage and revision rule

- Reporting years 2010 to 2023, every workbook in the newest zip the page links. Retrieved 2026-10-21. `vintage` is empty.
- Written with `ip.write_snapshot`: a run replaces the whole table, so EPA's revisions in a newer summary replace the earlier figures.
- Ceiling: three requests (the page, asked fresh each run; the zip; the crosswalk; files already in `warehouse/raw/ghgrp/` are reused).

## Shape and columns

Series shape, with five extra columns: `entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_frs_id, x_oris, x_subparts, x_naics, x_reporting_year`.

- `entity`: `ghgrp:<GHGRP facility id>`, for example `ghgrp:1000112`; `node` the facility's name; `geo` `US-<state>`.
- `ts_utc`: the reporting year's 1 January; `freq` `P1Y`; `market` empty.
- Variables, both in `tCO2` (metric tons of CO2, as the facility reported them):
  - `co2_non_biogenic`, from "CO2 emissions (non-biogenic)" (16,535 rows);
  - `co2_biogenic`, from "Biogenic CO2 emissions (metric tons)" (500 rows).
- `x_frs_id` the facility's FRS id; `x_oris` the plant's ORIS codes from EPA's crosswalk, joined with ";"; `x_subparts` the workbook's subparts; `x_naics` the primary NAICS code; `x_reporting_year` the workbook's year.

From the header: 17,035 rows; 1,443 facilities, 1,422 with an ORIS code.

## License

ERW verdict: public. Header: "License: public (a work of the U.S. government; cite "U.S. EPA, Greenhouse Gas Reporting Program, data summary 2023")." The connector cites EPA's terms as record 55 of license_reads.csv.

## Cross-check

None in the connector. It stops when a sheet lacks one of the columns it reads, or when a facility is given twice in a year.

## What it does not hold

- No methane, nitrous oxide or totals: EPA gives them in metric tons of CO2 equivalent (AR4 GWPs), CO2e is not in the standard's unit vocabulary, and CO2 itself is not CO2e.
- A blank cell has no row; nothing is filled.
- No facility that does not report under subpart D.
- No unit-level or monthly figures; one value a facility, variable and year.
- Facilities without an ORIS code in EPA's crosswalk (21 of 1,443) have `x_oris` blank.
