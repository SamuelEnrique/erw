# Session 913 report: the Annual Energy Outlook by Electricity Market Module region

23 October 2026, from 08:13 UTC, on lab-desktop (the data machine), a session of `queue/done/051-day-23-october-data-world-gas-hydro.md`. Model spend USD 0. Pulls: EIA's API v2, 20 requests of 20 (three facet lists of AEO2026: its tables, cases and regions; one page to count the table's records; then the connector's 16 pages).

## Read these first

- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `eia_aeo_emm_regions`, 75,712 rows, 2,912 series, 2025 to 2050, from AEO2026's Table 54 (Electric Power Projections by Electricity Market Module Region, the API's tableId 62) for the 25 EMM regions and the U.S. Each region's capacity by technology (coal, combined cycle, combustion turbine, nuclear, fossil steam, pumped storage, diurnal storage, fuel cells, hydrogen turbines, renewables), cumulative planned and unplanned additions and retirements by technology, end-use capacity and generation, generation by fuel, sales by sector, net energy for load with imports and exports, fuel use, fuel prices and end-use and service-category prices. PROJECTIONS, EIA's, and the header says so.
- **One case, the Counterfactual Baseline (`cb2026`):** AEO2026 names no Reference case, and Table 54 in every one of its 11 cases would be about 176 pages of the API, nine times the session's ceiling. `eia_aeo_electricity` keeps the national tables in every case.
- **The cross-checks:**
  - **The 25 regions summed against Table 54's own U.S. row:** every capacity series in every year within 0.1 percent (969 of 969 series-years). Generation and sales sum to a little less than the U.S. row (total generation 4,503 against 4,518 TWh in 2025, sales 4,050 against 4,069): the U.S. row holds more than the 25 regions, which the table does not name. Prices are averages and were not summed.
  - **Table 54's U.S. row against the national tables (`eia_aeo_electricity`, the same case), by series:** the 28 cumulative additions and retirements series agree in 403 of 403 non-zero series-years. The one series name the two share for generation does not: Table 54's "Electric Power Sector : Total Generation" is 4,249 TWh in 2025, Table 8's series of the same name 4,518, which is Table 54's total generation with the end-use sectors. Named, not mended.
- **Not taken:** the emissions (2,704 rows in million short tons and 676 in short tons; short tons are not in the standard's units).

## Decisions made without you

- **The baseline case only,** as above; another case is one run of `--case`, about 16 requests.
- **`geo` empty for a region,** which spans states; `US` for the U.S. row. The region's id and name are in `x_region` and `x_region_name`.
- **quadrillion Btu given as TBtu** (times 1,000), a unit already in the vocabulary.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_aeo_regions.py`, `tests/test_session913.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c051/s913/`, `runs/s913*`, `warehouse/raw/eia_aeo_regions/`.
