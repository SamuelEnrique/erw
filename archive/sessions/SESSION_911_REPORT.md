# Session 911 report: the hydropower fleet (Oak Ridge National Laboratory's Existing Hydropower Assets)

23 October 2026, from 08:06 UTC, on lab-desktop (the data machine), a session of `queue/done/051-day-23-october-data-world-gas-hydro.md`. Model spend USD 0. Pulls: 8 requests of 15, each 11 seconds after the last (HydroSource's robots file asks a crawl delay of 10 s). HydroSource's robots file, asked alone first; its sitemap index and its datasets sitemap; the EHA Plant Database 2026 page; the Data Use Policy; the robots path of the workbook's S3 host (HTTP 403, no file); the plants file as CSV and as a workbook.

## Read these first

- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `ornl_eha_hydropower_plants`, 2,257 plants (2,216 conventional hydro, 26 pumped storage, 15 both), 102,778 MW, from ORNL's Existing Hydropower Assets (EHA) Plant Database, 2026 (HydroSource, published July 2026, DOI 10.21951/EHA_FY2026/3374497). Each plant's place (state, county, FIPS code, NAD83 point, waterway, hydrologic unit), owner and owner type, dam owner, the FERC docket and its authorization's issue and expiry dates, the permitting agency, mode of operation (run-of-river, peaking, canal or conduit and the rest), units, hydro and pumped storage capacity, average annual generation since 2002, capacity factor and first year of operation, NERC region, balancing authority, EIA sector and transmission owner. An entities table, beside EIA's plant tables.
- **The cross-check against EIA's plants by EIA plant id:**
  - 1,649 EHA plants carry an EIA plant id (1,624 ids; 39 plants share an id with another, kept as ORNL gives them); 608 carry none: small plants (median 0.3 MW, 290 MW in all), 389 of them under FERC exemptions.
  - Of the 1,465 plants with hydro or pumped storage generators in `eia860m_operating_generators`, 1,456 are in EHA by id; the 9 missing hold 30 MW in all.
  - Capacity, plant by plant: EHA's hydro capacity equals EIA-860M's conventional hydro nameplate within 1 MW at 1,429 of 1,432 ids (80,129 and 80,134 MW in all); pumped storage at 39 of 39 (22,224 MW both).
  - EHA's own totals, 80,547 MW hydro and 22,231 MW pumped storage, are above EIA-860M's 80,163 and 22,224; the plants without an EIA id hold 290 MW of the difference.
- **The data use policy:** "Data hosted on HydroSource is openly shared, without restriction, in accordance with Department of Energy's Public Access Plan", with a citation of the authors, title, publisher and DOI, which the header carries. The verdict is for session 914 (the licenses' fifth round) to record.

## Decisions made without you

- **The workbook, not the CSV:** the same 2,257 rows, but in clean UTF-8 text (the CSV is Windows-1252) and with ORNL's field descriptions, which name each column's unit and meaning.
- **The workbook taken by its link on the landing page.** The page also shows a form (a required name and other fields) beside the download links; the links themselves are public addresses on ORNL's S3 bucket, and the policy says the data are shared without restriction. No form was filled.
- **`capacity_mw` is hydro and pumped storage capacity summed;** each is also in its own column. `status` and `operator` are left empty: the database lists plants in operation and names owners, not operators.
- **The table flagged `public`** by the policy above.

## For Samuel's ruling

- None new.

## Errors

- The first cross-check read the tables with pandas' `comment="#"`, which cuts a row at a '#' inside a value (3 EHA rows, 163 of EIA-860M's), and its counts were a few plants short. Found by session 917; the figures above are from the check run again reading past the header lines only (`runs/c051/readt.py`).

## Files

- New: `warehouse/connectors/ornl_eha.py`, `tests/test_session911.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c051/s911/`, `runs/license_reads/s911/`, `runs/s911*`, `warehouse/raw/ornl_eha/`.
