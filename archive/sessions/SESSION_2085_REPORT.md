# Session 2085 report: the world's renewable capacity (IRENA's statistics)

23 October 2026, from 21:05 UTC, on lab-desktop (the data machine), the second session of `queue/done/068-day-26-october-data-mexico-renewables-loans-credits-pipelines.md`, unattended. Model spend USD 0. Pulls: 8 requests of 15 (below).

## Read these first

- **One table written, validated, archived, in coverage (sector power), held internal and from the live set:** `irena_capacity_annual`, installed electricity capacity by country and technology, 2015 to 2025, from IRENASTAT's "Electricity statistics by Country/area, Technology, Data Type, Grid connection and Year" (its 2026 H2 table, updated 28 September 2026): 20,662 rows, 224 countries, 23 technologies (solar PV, onshore and offshore wind, renewable, mixed and pumped hydropower, the bioenergies, geothermal, marine, nuclear, coal, gas, oil and IRENA's renewable and non-renewable totals), in MW, grid connection All. 43,402 cells IRENA leaves empty have no row; a 0 it gives is kept.
- **www.irena.org refused the reader:** its publication page answered HTTP 403, an Azure WAF challenge, so the host is not asked again and IRENA's terms of use, which live there, were not read. The table is therefore internal ("not settled" in the license record) until a licenses round reads IRENA's terms from another address or a ruling settles it. IRENASTAT's own host, `pxweb.irena.org`, has no robots file and answered the API.
- **The cross-check against `eia_state_capacity_annual`** (EIA's net summer capacity, all sectors, summed over the states): nuclear the same to the MW every year (98,391 MW in 2024); wind 1.001 of EIA's, natural gas 1.004 to 1.005, coal 1.008 to 1.010 and hydropower 1.048 to 1.054 (IRENA counts mixed plants with it) in 2018, 2021, 2023 and 2024, the years the session's script compared; over every year from 2018 to 2024 gas is 1.003 to 1.006 and coal 1.008 to 1.012 (session 2094). Solar is 1.43 to 1.62 of EIA's: IRENA's photovoltaic includes the small-scale systems EIA's state table does not hold.
- **The query** is one POST of a JSON body (all countries and technologies, the capacity data type, All, the years asked) to the table's address, which also serves its metadata by GET; since the raw store finds a saved file by its address, the connector keeps the metadata and the answer together in `warehouse/raw/irena_capacity/capacity_query_2015_2025.json` and reads both from it offline. The first offline write failed on that (the raw store gave the answer for the metadata); fixed and written again, no new request.

## The pulls

1. `www.irena.org/robots.txt` (read 225): disallows `/DocumentDownloads/` and two other paths. 2. The Renewable Capacity Statistics 2026 page (read 226): HTTP 403, a challenge. 3. `pxweb.irena.org/robots.txt` (read 227): 404. 4 and 5. IRENASTAT's folder listings. 6. The table's metadata. 7 and 8. The connector's trial: the metadata again and the query (3.3 MB).

## Decisions made without you

- **Capacity only, grid connection All, from 2015:** generation is in the same table and a later run can take it with one more query.
- **Held internal** with no verdict, rather than public, since IRENA's terms could not be read.
- **No geo:** IRENA's codes are ISO alpha-3, and the data standard's geo is alpha-2; the code is the entity and the name is the node.

## For Samuel's ruling

- None new; IRENA's terms wait on a licenses round (session 2089) or a reading you can do in a browser.

## Files

- New: `warehouse/connectors/irena_capacity.py`, `tests/test_session2085.py` (4 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_reads.csv` (225 to 227), `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c068/s2085/`, `runs/license_reads/s2085/`, `runs/s2085*`, `warehouse/raw/irena_capacity/`.
