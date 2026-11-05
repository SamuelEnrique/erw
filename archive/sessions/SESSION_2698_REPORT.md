# Session 2698 report: Great Britain's gas consumption and meters by country and region, 2005 to 2024, weather corrected (DESNZ's Subnational gas consumption statistics), public, the session's third own choice

25 October 2026, about 13:13 to 13:22 UTC, on lab-desktop (the data machine), chain 135, unattended, run before sessions 2695 to 2697 so that its write came before GitHub's daily run takes the data lock at about 14:10. Precheck passed (`runs/c135/pre2698.out`). Model spend USD 0. Pulls: 4 requests of 20 (3 by the probe, 1 fetch of the workbook under a run name of its own, read offline by the trial and the write).

## Why this source

- **The companion of session 2693's table:** DESNZ publishes the subnational gas statistics beside the electricity ones, from the same host, under the same licence, with the same countries and regions. The ERW held Great Britain's gas only nationally (`desnz_uk_gas_quarterly`, Energy Trends 4.1).

## Read these first

- **The write's metadata patch conflicted again,** in all four files this time (`docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`): the new rows sort beside sessions 2692's and 2693's. The write reported `fail=1` and released the lock with the main checkout clean; the files were resolved as a union in the worktree, with no marker left, 589 tables and no row twice, and committed on their own. The finish then ran clean (`fail=0`). The test passed before its commit.
- **The host:** www.gov.uk's robots file closes only print and search paths and names no Claude agent (read 1422); the assets host has no robots file (read 1393).
- **The terms:** the Open Government Licence v3.0 (DESNZ's verdict, read 315). The table is **public**.

## The table

- **`desnz_gb_regional_gas_consumption_annual`** (series, 1,966 rows, 130 entities, 2005 to 2024, `gas`), from the workbook "Subnational gas consumption statistics 2005-2024" (published 18 December 2025, its 2005 to 2013 tables revised on 5 May 2026; read 1424).
  - Entity `desnz_subgas:<area>:<item>`, areas as in session 2693's table: the names with "(inc unallocated)" from 2015, `unallocated` to 2014, England's nine regions, and `inner_london` and `outer_london` from 2014.
  - Items `consumption_domestic`, `_non_domestic` and `_total` (MWh, the workbook's GWh times 1,000); the same for `meters_` (count, the consuming meters only); and from 2015 `meters_non_consuming`, outside the meters' total.
- **What the figures are:**
  - Weather corrected.
  - The years are DESNZ's gas years, not calendar years. Up to 2015 a year runs October to September. From 2018 it runs mid-May to mid-May (2024 is mid-May 2024 to mid-May 2025). 2016 and 2017 fall between.
  - The table keeps DESNZ's year label, and both headers give the periods.
  - A domestic meter is one using under 73,200 kWh a year, so small businesses are counted as domestic.
- **The workbook differs from the electricity one,** each difference read:
  - a Notes column;
  - a column of non-consuming meters from 2015;
  - 2014's sheet gives Inner and Outer London and no London.
- **Checks, all passing:**
  - an area's domestic and non-domestic parts add to its total;
  - England's nine regions add to England (in 2014, Inner plus Outer London stand for London);
  - Inner and Outer London add to London where all three are given.

  A note on a country's or region's row stops the run. DESNZ's one note, a large consumer left out, is given to local authorities only.
- **Figures:**
  - Great Britain's consumption was 667.6 TWh in 2005 and 501.3 in 2014.
  - With the unallocated, it was 488.4 in 2015 and 438.0 in 2024.
  - Consuming meters: 24.9 million in 2024, beside 0.38 million non-consuming.
- **Its record:** written by run `20261025T131751Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T131756Z-local`, 1,966 rows), held from the live set, and in the release package (public; 301 public tables in the package's README).

## Cross-checks

Against the ERW's `desnz_uk_gas_quarterly` (Energy Trends 4.1, the UK, calendar years, not weather corrected), four quarters summed:

| | 2015 | 2024 |
|---|---|---|
| Final consumption there (TWh) | 495.3 | 428.2 |
| Great Britain's total here (TWh) | 488.4 | 438.0 |
| Gap | 1.4 per cent | 2.3 per cent |

The bases differ: Great Britain against the UK, gas years against calendar years, weather corrected against not. The domestic figures do not compare (280.6 TWh here in 2024 against 252.3 there), because DESNZ's subnational "domestic" is a consumption band that takes in small businesses.

## Requests (4 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.gov.uk's robots file (its own request) | 200 |
| 2 | the collection of sub-national gas consumption data | 200 |
| 3 | the page of regional and local authority gas consumption statistics | 200 |
| 4 | the workbook (the fetch, 1,650,955 bytes) | 200 |

Reads recorded: 1422 to 1424.

## Decisions made without you

- **DESNZ's subnational gas as the third own choice; public** under the verdict on record.
- **The weather-corrected workbook (2005 to 2024), not the uncorrected one (2015 to 2024):** it is DESNZ's main series and the longer one. The uncorrected workbook can be a second table.
- **The gas year kept as DESNZ labels it,** at the label year's first day, with the periods in the header, rather than moved to the period's start, which changes in 2016, 2017 and 2018.
- **Non-consuming meters as their own item,** outside the meters' total, as DESNZ gives them.
- **Session 2698 before 2695 to 2697,** so that its write did not wait on the daily run's lock.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/desnz_subnational_gas_consumption.py`, `tests/test_session2698.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (reads 1422 to 1424) and `docs/licenses.md`.
- On the data machine only: `runs/c135/s2698/`, `runs/license_reads/s2698/`, `warehouse/raw/desnz_regional/s2698probe1/`, `warehouse/output/desnz_gb_regional_gas_consumption_annual.csv`.
