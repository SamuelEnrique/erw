# Session 2693 report: Great Britain's electricity consumption and meters by country and region, 2005 to 2024 (DESNZ's Subnational electricity consumption statistics), public, the session's second own choice

25 October 2026, about 13:03 to 13:12 UTC, on lab-desktop (the data machine), chain 135, unattended. Precheck passed (`runs/c135/pre2693.out`). Model spend USD 0. Pulls: 4 requests of 20 (3 by the probe, 1 fetch of the workbook under a run name of its own, read offline by the trials and the write).

## Read these first

- **A commit was made before its test's result was read.** Commit `5c3a6a6e` (the connector, its test and the reads) carried `tests/test_session2693.py` with two failing cases: their bad sheets missed the totals by exactly 1 GWh, which the checks' tolerance of 1 GWh lets pass. Commit `d1c79601` set them past it (12 against 10, 95 against 90); the test passes since. Nothing was written from the failing commit.
- **The write's metadata patch conflicted.** The new rows sort beside session 2692's in `docs/coverage.md`, `warehouse/metadata/coverage.csv` and `warehouse/metadata/archive_manifest.csv` (`sources.csv` applied cleanly). The write reported `fail=1` and released the lock with the main checkout put back; the three files were resolved as a union (`runs/c124/resolve_union.py`) in commit `80eb2d0e`, with no marker left, each table once (588 tables) and no row twice. The finish then ran clean (`fail=0`).
- **The host:** www.gov.uk's robots file closes only print and search paths (read 1419); the assets host has no robots file (read 1393).
- **The terms:** the Open Government Licence v3.0 (DESNZ's verdict, read 315). The table is **public**.

## The table

- **`desnz_gb_regional_consumption_annual`** (series, 2,608 rows, 190 entities, 2005 to 2024, `power`), from the workbook "Subnational electricity consumption statistics 2005-2024" (last updated 18 December 2025, read 1421).
  - Entity `desnz_sub:<area>:<item>`. The areas are kept as each sheet names them: `great_britain` (to 2014), `great_britain_inc_unallocated` (from 2015), `scotland` and `scotland_inc_unallocated` likewise, `england`, `wales`, `england_and_wales_inc_unallocated`, `unallocated`, England's nine regions, and London as `inner_london` and `outer_london` where a sheet splits it.
  - Items `consumption_*` (MWh, the workbook's GWh times 1,000) and `meters_*` (count, its thousands times 1,000): domestic, its standard and Economy 7 parts where given, non-domestic and all meters. The mean and median a meter are not taken (they are ratios of the rows kept).
- **Checks, all passing:** a sheet's parts add to its totals within 1 GWh or 0.01 thousand meters; standard and Economy 7 add to the domestic; England's nine regions add to England. A heading or area not in the map stops the run.
- **Figures:** Great Britain's consumption was 320.3 TWh in 2005 and 292.2 in 2014; with the unallocated, 287.5 in 2015 and 249.2 in 2024.
- **Its record:** written by run `20261025T130818Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T130823Z-local`, 2,608 rows), held from the live set, and in the release package (public: 300 public tables in the package's README).

## Cross-checks

Against the ERW's `desnz_uk_nations_electricity_annual` (session 2678, the nations' sales): England's consumption here is 243.1 TWh in 2015 against 240.5 there, and 212.0 in 2024 against 209.0. The two count differently (meter readings here, suppliers' sales there), and the gap is 1.1 per cent in 2015 and 1.4 in 2024.

## Requests (4 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.gov.uk's robots file | 200 |
| 2 | the collection of sub-national electricity consumption data | 200 |
| 3 | the page of regional and local authority statistics | 200 |
| 4 | the workbook (the fetch, 2,103,254 bytes) | 200 |

Reads recorded: 1419 to 1421.

## Decisions made without you

- **DESNZ's subnational consumption as the second own choice; public** under the verdict on record.
- **The table named `desnz_gb_regional_consumption_annual`:** the first name (48 characters) was past the 40 allowed.
- **The areas kept as named, not joined across 2014 and 2015:** from 2015 DESNZ adds the consumption it cannot place to Great Britain's and Scotland's totals; a series joined across the change would show a step that is not in the use.
- **Local authorities not taken:** the table holds the countries and regions only; the authorities' rows can be added from the same workbook.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/desnz_subnational_consumption.py`, `tests/test_session2693.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (reads 1419 to 1421) and `docs/licenses.md`.
- On the data machine only: `runs/c135/s2693/`, `runs/license_reads/s2693/`, `warehouse/raw/desnz_regional/s2693probe1/`, `warehouse/output/desnz_gb_regional_consumption_annual.csv`.
