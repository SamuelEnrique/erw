# Every reporting facility's greenhouse gases by year, a series (EPA's Greenhouse Gas Reporting Program data summary)

Energy Research Warehouse (ERW), method note written in session 2079 (chain 067) for a table first written on 23 October 2026 (session 2072).

Tables: `epa_ghgrp_facility_emissions`

## Publisher and address

U.S. Environmental Protection Agency (EPA), Greenhouse Gas Reporting Program (GHGRP), data summary spreadsheets: the workbook `ghgp_data_by_year_2023.xlsx` inside `https://www.epa.gov/system/files/other-files/2024-10/2023_data_summary_spreadsheets.zip`, the newest zip the program's data sets page (`https://www.epa.gov/ghgreporting/data-sets`) links. Source id `epa:ghgrp_facilities`. Connector: `warehouse/connectors/ghgrp_facilities.py` (session 2072).

## Vintage and revision

Reporting years 2015 to 2023 (`--first-year` 2015; the workbook holds 2011 on). The zip was last modified 2024-10-15T14:42:16Z (`vintage`, every row) and retrieved 2026-10-21T17:42:37Z by `ghgrp_power.py`, which shares the raw store `warehouse/raw/ghgrp/`; session 2072 reused it and asked only the page again, to confirm the zip is still the newest. Written by run `20261023T203605Z` (session 2079 wrote it again, its rows unchanged, for the header's corrected words: the pipeline and distribution entities and "facility-states") (23 October 2026).

The page is asked fresh each run and the newest year it links is taken; a zip already saved is reused. The table is merged, not replaced: a run's rows replace earlier rows with the same (entity, variable, ts_utc), and earlier rows not in the run are kept, so a facility EPA drops stays.

## Shape and variables

Series, 70,338 rows, one a facility, segment and year; unit `tCO2e` (metric tons of CO2 equivalent, AR4 global warming potentials, Decision 61), freq P1Y, `ts_utc` the year's 1 January, node the facility's name. 10,048 entities of 9,864 facility ids; 29 ids appear in more than one segment.

| Segment (`x_segment`) | Variable | Rows | Entities | Facility ids | 2023, Mt CO2e |
|---|---|---|---|---|---|
| Direct Point Emitters | emissions_direct | 59,533 | 8,205 | 8,205 | 2,382.8 |
| Onshore Oil & Gas Prod. | emissions_onshore_production | 4,429 | 830 | 830 | 91.4 |
| Gathering & Boosting | emissions_gathering_boosting | 2,786 | 476 | 476 | 89.5 |
| LDC - Direct Emissions | emissions_ldc | 1,499 | 189 | 189 | 11.4 |
| SF6 from Elec. Equip. | emissions_sf6_equipment | 806 | 137 | 137 | 1.9 |
| Transmission Pipelines | emissions_transmission_pipelines | 1,285 | 240 | 56 | 1.5 |

- By year, all six segments: 2015 3,058.1 Mt; 2016 2,983.1; 2017 2,926.0; 2018 2,989.6; 2019 2,861.5; 2020 2,605.2; 2021 2,719.5; 2022 2,696.9; 2023 2,578.6. Gathering and boosting and transmission pipelines have no row for 2015 (their rows begin in 2016).
- Direct emitters in 2023 by `x_sectors`: Power Plants 1,403.9 Mt; Chemicals 113.1; Petroleum and Natural Gas Systems 109.4; Minerals 106.8; Other 94.9; Waste 92.2. The largest value is James H Miller Jr (`ghgrp:1007227`, Alabama), 21,775,439.586 tCO2e in 2022.
- 396 values are 0 and 2 are below zero, as published: Muscatine's SF6 in 2018 (-1,023.72) and Golden Grain Energy's direct emissions in 2015 (-1,196.25).
- Entity: `ghgrp:<facility id>`; transmission pipelines and distribution companies, listed by EPA a row a state where the emissions occur, are `ghgrp:<facility id>:<state>` with `x_emission_state` (2,783 rows; the 56 pipelines make 240 facility-states, TransCanada / ANR Pipeline 17). One row names no such state and keeps `ghgrp:<facility id>`: `ghgrp:1008674`, Interstate Power & Light - MN Gas Distribution, 2015, value 0, geo `US-IA` (the reported state).
- `geo` is filled in every row: 54 codes, the 50 states, DC, `US-GU`, `US-PR` and `US-VI`; no row names more than one state. Where `x_emission_state` is filled, `geo` is that state in every row.
- `x_frs_id` (blank in 6,526 rows), `x_naics` (blank in 18), `x_subparts` (filled in all), `x_sectors` (direct emitters only), `x_basin` (onshore production and gathering only), `x_county` (blank in 6,800).

## Reading the source

- Six sheets of the workbook are taken; "Suppliers" (gases supplied, not emitted), "CO2 Injection" and "Geologic Sequestration of CO2" (quantities injected and stored), the industry type key and the FAQs are not.
- A column whose heading begins with four digits must read `<year> Total reported (direct) emissions`; a sheet missing, a sheet without its "Facility Id" header, a value that is not a number, a state name not in the connector's map, or a facility given twice in a year and segment stops the run.
- A blank cell has no row; nothing is filled. Values as EPA publishes them, whitespace collapsed.
- Ceiling: two requests (the page, the zip when not saved). www.epa.gov's robots file disallows only Drupal's own paths and search pages (read 228).

## License

`license_verdicts.csv` records EPA, read 55 (its disclaimers page): "may be public", for public and for commercial use: "Unless otherwise specified, geospatial data produced by the EPA is by default in the public domain and is not subject to domestic copyright protection under 17 U.S.C."; the same page lets EPA's documents be freely distributed and used for non-commercial, scientific and educational purposes. `license_tables.csv` maps the table to EPA (the source registry), and `docs/licenses.md` gives it "may be public", flagged public, agreeing; `sources.csv` names the source's license as public. The header asks for the citation "U.S. EPA, Greenhouse Gas Reporting Program, data summary 2023".

## Cross-checks (session 2079)

- The counts above were computed from the rows, read past the header lines; the six segments' rows and entities match the header's, and sum to its 70,338. No (entity, variable, ts_utc) is given twice; the rows are in (entity, variable, ts_utc) order.
- Session 2072's check against `epa_ghgrp_power_co2` (non-biogenic CO2, 2015 to 2023, the same facility ids), recomputed: 10,071 facility-years of 1,284 power plants; CO2e over CO2 median 1.0010, 5th percentile 1.0010, 95th 1.0081, none below 1; summed, 1,930.6 against 1,919.5 million tons in 2015 and 1,445.4 against 1,439.1 in 2023. All as the report gives them.

## What it does not hold

- Suppliers' quantities, CO2 injected or sequestered, and emissions by gas or by subpart: a facility's total in CO2 equivalent only.
- Years before 2015, and 2024 on (the newest summary the page links is 2023's).
- Facilities below the program's reporting threshold, and any cell EPA left blank.
