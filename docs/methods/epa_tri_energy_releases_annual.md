# The energy industries' toxic releases by facility, chemical and year, 2015 to 2023 (EPA's Toxics Release Inventory)

Energy Research Warehouse (ERW), method note written in session 2129 (chain 079) for a table first written on 23 October 2026 (session 2121, `archive/sessions/SESSION_2121_REPORT.md`).

Tables: `epa_tri_energy_releases_annual`

## Publisher and address

U.S. Environmental Protection Agency (EPA), Toxics Release Inventory (TRI) Program, the TRI Basic Data Files (`https://www.epa.gov/toxics-release-inventory-tri-program/tri-basic-data-files-calendar-years-1987-present`): one CSV a reporting year, one row a form, 122 columns (counted in every saved file), at `https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/<year>_US/csv`. Source id `epa:tri_basic`. The nine files are saved under `warehouse/raw/epa_tri_energy/` (2015 to 2022: 61,239,948 to 64,742,430 bytes; 2023: 61,601,087).

Connector: `warehouse/connectors/epa_tri_energy.py` (session 2121): `[--first-year 2015] [--last-year 2023] [--offline] [--out-dir DIR]`, one request a year, each file read in chunks of 20,000 rows. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. `coverage.csv` gives the sectors power, oil, gas and coal.

## Vintage and revision

Last written by run `20261023T231642Z`, offline from the saved files: "This run wrote 384483 rows: 0 new, 384483 replacing earlier rows with the same (entity, variable, ts_utc)". The files were retrieved from 2026-10-23T22:33:49Z (2023) to 22:41:56Z (2022); `vintage` is empty (the service gave no last-modified time). A later run replaces each form's rows by its key and keeps rows it does not restate.

## Shape and variables

Series, 384,483 rows: 128,161 forms, each with three variables, `total_releases`, `on_site_release_total` and `off_site_release_total` (EPA's columns "107. TOTAL RELEASES", "65. ON-SITE RELEASE TOTAL", "88. OFF-SITE RELEASE TOTAL"). `entity` `tri:<TRIFD>:<TRI chemical id>:<document control number>`, one form; `ts_utc` the reporting year's 1 January; `freq` P1Y; `unit` lb (375,498 rows) or g (8,985 rows, every one "Dioxin and dioxin-like compounds", Decision 66), as printed; `geo` US-<state>, 55 values including DC, GU, MP, PR and VI; `node` the facility's name; `market` and `vintage` empty. The `x_` columns: TRIFD, FRS id (blank on 72 rows), chemical id, name and CAS number, EPA's sector and code, primary NAICS, county, latitude, longitude, parent company (blank on 282 rows), carcinogen, PBT and PFAS flags, form type.

| EPA sector (code) | Forms | Facilities |
|---|---|---|
| Petroleum (324) | 50,078 | 1,014 |
| Petroleum Bulk Terminals (4247) | 37,195 | 837 |
| Electric Utilities (2211) | 36,480 | 637 |
| Natural Gas Processing (211) | 3,594 | 342 |
| Coal Mining (2121) | 814 | 54 |

Rows a year: 44,700 (2015), 43,386, 43,755, 43,770, 41,946, 40,086, 39,618, 44,433, 42,789 (2023). Facilities a year: 1,784 (2015) to 2,083 (2022) and 2,039 (2023). Natural gas processing forms a year: 35, 33, 27, 14, 8, 13, 4 (2015 to 2021), then 1,714 (2022) and 1,746 (2023).

## Placing values in time

A form reports a calendar year; `ts_utc` is that year's 1 January, UTC. A form whose year is not its file's stops the run.

## What is and is not filled

- Kept: forms whose "INDUSTRY SECTOR CODE" is 2211, 324, 211, 2121 or 4247. Other industries are not read.
- A site can file several forms of one chemical in a year (one an establishment, or a refinery and its terminal under two NAICS codes); each is its own entity, and nothing is summed. `x_trifd` and `x_chemical_id` group them.
- Values as published, zeros kept; a blank cell has no row; nothing is filled. The 10,849 Form A forms (EPA's short form, which reports no quantities) carry 0 in all three totals: 32,547 zero values.

## License

Header: "License: public (a work of the U.S. government). Cite: U.S. EPA, Toxics Release Inventory, basic data files, reporting years 2015 to 2023." `license_verdicts.csv` records EPA, read 55: "may be public", for public and for commercial use. `docs/licenses.md`: "may be public", flag public, ERW verdict public.

## Checks (session 2129)

The figures in this note were computed from the rows of `warehouse/output/epa_tri_energy_releases_annual.csv`, streamed past its 10 header lines (scripts in `runs/c079/s2129/`).

- 384,483 rows, `ts_utc` from 2015-01-01T00:00:00Z to 2023-01-01T00:00:00Z, as the header states. No (entity, variable, ts_utc) twice; no negative value. Every form has all three variables.
- Session 2121's cross-check (`runs/c079/s2121/cross.py`), run again: its output is identical to the saved `cross.out`.
  - EPA's arithmetic: total releases equal on-site plus off-site on all 128,161 forms (0 exceptions).
  - Electric utilities, total releases in pounds: 432.6 million lb (558 facilities) in 2015, 360.3, 339.2, 337.8, 281.8 (2019), 228.6, 253.7, 243.6, 194.6 million lb (388 facilities) in 2023; mercury and its compounds 102,399 lb (2015), 54,512 (2019), 38,313 (2023).
  - The FRS id join to `epa_ghgrp_facility_emissions`: 370 of 558 electric utilities (66.3 percent) in 2015 to 239 of 387 (61.8 percent) in 2023 are GHGRP facilities that year.
- All five sectors, total releases in pounds: 533.9 million lb (2015), 453.7, 432.2, 435.0, 377.9, 313.7, 343.0, 468.1 (2022), 484.1 (2023).
- Sites with more than one form of a chemical in a year: 183 (2015), 159, 176, 166, 125, 126, 124, 120, 102 (2023); of them, those whose forms carry two or more NAICS codes: 100, 94, 122, 121, 79, 79, 80, 78, 78.

## Where the description and the data disagree

1. **Natural gas processing before 2022.** The docstring: "the few forms of earlier years are those of plants under another code". Of the 134 forms in sector 211 from 2015 to 2021, 65 carry NAICS 211130 (natural gas processing itself), 68 carry 211112 and 1 carries 211111.
2. **"Report from 2022".** Header line 3: "natural gas processing plants report from 2022, when EPA added them". The table holds 134 forms of that sector from 2015 to 2021 (4 to 35 a year); the docstring mentions them, the header does not.

## The session report against the table

The figures of `SESSION_2121_REPORT.md` checked against the table, the code and the rerun cross-check hold (384,483 rows, 128,161 forms, the five sectors' forms and facilities, natural gas processing's 4 to 35 forms then 1,714 and 1,746, the unit g, EPA's arithmetic on every form, the electric utilities' pounds and mercury, 61 to 66 percent in the GHGRP, the 2023 file of 61.6 MB, 12 requests), except:

- "132 to 201 such pairs a year" (sites with several forms of one chemical): no count of the table gives that range. Sites with more than one form of a chemical in a year number 102 to 183; those whose forms carry two NAICS codes, 78 to 122; the forms in such groups, 322 to 484.
- "the 2015 to 2022 files (62 to 65 MB each)": the saved files run from 61,239,948 bytes (2021) to 64,742,430 (2015); 2020's is 61,547,118.
- "the table's header, written with 65, is written again in session 2129": the file's header already names Decision 66 (run `20261023T231642Z`).

Acted on in session 2129: the docstring and the header now say natural gas processing plants were added to the inventory from 2022 and that the 134 earlier forms are of plants that reported before (65 under 211130); the table was written again offline, its rows unchanged; session 2121's report is corrected on the forms counted and the files' sizes.

## What it does not hold

- Any industry but the five sectors, the form's 70 detailed quantities (air, water, land, transfers), and reporting years before 2015 or after 2023.
- Any sum across a site's forms, chemicals or units.
