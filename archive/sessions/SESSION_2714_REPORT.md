# Session 2714 report: the UK's major power producers' power stations, May 2026 (DESNZ's DUKES 5.11), public, a source of the session's own choosing

25 October 2026, about 17:08 to 17:13 UTC, with the write at 18:21 UTC after this machine's daily task released the data lock, on lab-desktop (the data machine), chain 136, unattended. Precheck passed (`runs/c136/pre2714.out`). Model spend USD 0. Pulls: 3 requests of 20 (2 by the probe, 1 fetch of the workbook, read offline by the trial and the write).

## Why this source

- **This chain's four planned provinces gave one internal table** (Nova Scotia); Manitoba and Saskatchewan need written permission, and Newfoundland and Labrador publishes no data file.
- **The ERW held no UK power station,** only the UK's capacity as totals (DESNZ's regions and Energy Trends). DUKES 5.11 lists each of the major power producers' stations, from the host and licence of chain 135's DESNZ tables. It was not held, retired or taken by a chain.

## Read these first

- **The host:** www.gov.uk's robots file closes only print and search paths and names no Claude agent (read 1446). The chapter 5 page lists tables 5.1 to 5.16 (read 1447). The terms are the Open Government Licence v3.0 (DESNZ's verdict, read 315), so the table is **public**.
- **A new table, `desnz_uk_power_stations`** (entities, 1,364 rows, `power`), one row a station operational at the end of May 2026, from the sheet "5.11 Full list":
  - `entity_id` `dukes:<DESNZ site code>`, `entity_type` plant, `name` the site, `operator` the company.
  - `geo` from the country. `capacity_mw` as stated. `status` operating, `status_date` 2026-05-31, read from the title.
  - The sheet's other 14 columns are kept as text: technology, type, CHP, fuels, grid connection, region, postcode, OS reference, X and Y, year commissioned, site code.
  - **`lat` and `lon`** are converted here from the sheet's X and Y, which are British National Grid (EPSG:27700) for every station, Northern Ireland's included. That was checked on known sites: Belfast's SSE Arena 54.604, -5.915; Ballylumford 54.845, -5.787; Drax 53.736, -0.991; Dinorwig 53.119, -4.102. pyproj is imported only for the conversion; the test skips it where pyproj is missing (the check run's `requirements.txt` lacks it).
- **Figures:**
  - 85,099.5 MW in all: England 837 stations and 54,973 MW, Scotland 336 and 18,137, Wales 137 and 9,171, Northern Ireland 54 and 2,818.
  - By fuel: natural gas 33,676 MW, wind 29,837, solar 6,454, nuclear 5,883, biomass 3,316, pumped hydro 2,900.
- **Checks, all passing:**
  - every site code unique; every capacity positive;
  - the list's capacity by fuel equal to table 5.11.A's major power producer rows, wind split onshore (12,952.6 MW) and offshore (16,884.9) by the sheet's type, and in all equal to its total, within 0.01 MW.
- **Not listed:** other generators, 28,758.6 MW in table 5.11.A (DESNZ's note 1). The earlier editions' sheets (DUKES 2004 to 2025) use other layouts and were not read.
- **Its record:** written by run `20261025T182127Z` under the data lock and validated (exit 0, the entities shape). It is in coverage, archived (`20261025T182131Z-local`), held from the live set, and in the release package (public). The patch applied cleanly.

## Cross-check

Against `desnz_uk_renewables_quarterly` (Energy Trends 6.1, all generators, the end of 2025): offshore wind 16,649.7 MW there against the major power producers' 16,884.9 MW here at the end of May 2026. The list is five months later, and offshore wind is almost all major power producers'.

## Requests (3 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.gov.uk's robots file (its own request) | 200 |
| 2 | the chapter 5 page | 200 |
| 3 | DUKES_5.11.xlsx (the fetch) | 200 |

Reads recorded: 1446 and 1447.

## Decisions made without you

- **DUKES 5.11 as the own choice; public** under the verdict on record.
- **Coordinates converted to WGS84** for the standard's `lat` and `lon`, with the sheet's X and Y kept beside them.
- **The current list only,** not the earlier editions' sheets.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/desnz_dukes_power_stations.py`, `tests/test_session2714.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (reads 1446 and 1447) and `docs/licenses.md`.
- On the data machine only: `runs/c136/s2714/`, `runs/license_reads/s2714/`, `warehouse/raw/desnz_dukes/s2714probe1/`, `warehouse/output/desnz_uk_power_stations.csv`.
