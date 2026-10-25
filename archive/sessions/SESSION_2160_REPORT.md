# Session 2160 report: data processing and hosting by state (County Business Patterns, a source of the session's choosing)

24 October 2026, from 00:23 UTC, on lab-desktop (the data machine), a session of `queue/done/092-day-30-october-data-bpa-snowpack-access-outlook-permits.md`. Model spend USD 0. Pulls: www2.census.gov, 15 requests of 20: its robots file in a call of its own, the 2022 and 2023 dataset listings, and the state files 2012 to 2023 (2022's first as a probe). Also Supabase for the locks.

## Read these first

- **Why this source:** AI's demand for power is the ERW's sharpest lens. The industry that runs data centers is counted by state in County Business Patterns, as NAICS 518210 (data processing, hosting and related services; from 2022, computing infrastructure providers, data processing, web hosting, and related services). The ERW held no CBP table, and no chain had planned one. NREL's ATB and EIA's proved reserves, the session's first two thoughts, are already held.
- **One series table, `census_cbp_hosting_annual`:** 1,836 rows, the 50 states and DC in every year from 2012 to 2023. Each has establishments, employment (the pay period including 12 March) and annual payroll (USD, the Bureau's thousands times 1,000), for all legal forms. The Bureau's noise flags are kept (G low, H moderate, J high, N not available), with the NAICS edition each year's file uses. Each file is a 12 MB zip of 93 MB of text, read a line at a time; only NAICS 518210's lines are kept.
- **The cross-check** (`runs/c092/s2160/cross.py`):
  - In 2023, hosting employment by state ranks the states much as the ERW's data center operator sites do (`datacenter_operator_sites`, Spearman 0.56). California, Texas and Virginia lead both.
  - **But it is not a measure of load.** Virginia's commercial electricity sales (`eia861_utility_sales`) rose from 48.5 TWh in 2015 to 77.7 in 2023, mostly data centers, while its hosting establishments stayed near 600 (Pearson 0.36). Data centers employ few people for their power, so this table measures the industry's workforce, not its electricity.
  - The nation's 518210 employment grew from 433,438 (2012) to 629,527 (2023).
- **Registered:** the sector rule (`power;datacenters`), both holds, the release package's rows, the license tables (the Census Bureau, read 17; licenses check 0 problems, release check 0 differences); no row twice. The test: `tests/test_session2160.py` (3 tests).

## Errors

- **The write's metadata patch met main's newer files** (main now holds chain 079's tables). Each side only held its own table's row, so it was resolved by union and the table finished again.

## Decisions made without you

- **CBP's NAICS 518210 as this session's source,** said above, with its limit stated: a count of the industry, not of its power.
- **2012 to 2023,** within the ceiling.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/census_cbp_hosting.py`, `tests/test_session2160.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c092/s2160/`.
