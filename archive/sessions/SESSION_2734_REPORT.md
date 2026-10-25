# Session 2734 report: the UK's de-rated plant capacity a year, 1996 to 2025 (DESNZ's DUKES 5.7), public, a third source of the session's own choosing

25 October 2026, about 19:40 to 19:45 UTC, run before sessions 2731 to 2733, on lab-desktop (the data machine), chain 137, unattended. Precheck passed (`runs/c137/pre2734.out`). Model spend USD 0. Pulls: 2 requests of 20 (1 by the probe, 1 fetch of the workbook, read offline by the trial and the write).

## Why this source

- **The ERW held the UK's capacity only as one year's station list** (DUKES 5.11) and as renewables by region. DUKES 5.7 gives thirty years by kind of company and fuel, from the chapter of sessions 2728 and 2729.

## Read these first

- **DESNZ's own sheet disagrees with itself in 2015 and 2016,** and the table keeps it as published:
  - All companies' total capacity and fossil fuels total are each 99 MW above their parts (79,539.65 MW against 79,440.65 in 2015).
  - All companies' total is also 99 MW above the major power producers' and the other generators' totals together.
  - Every fuel row adds exactly.

  The connector names these four differences (year, row, 99 MW within 0.05) and stops on any other. Its test proves that the same 99 MW in an unnamed year, or another amount in a named one, still stops the run.
- **The host:** www.gov.uk's robots file closes only print and search paths and names no Claude agent (read 1466). The terms are the Open Government Licence v3.0 (read 315), so the table is **public**.
- **A new table, `desnz_uk_derated_capacity_annual`** (series, 1,680 rows, 50 entities, `power`), 1996 to 2025:
  - Entity `desnz_cap:<mpp|other|all>:<item>`, for the major power producers, the other generators and all companies.
  - Items: each fuel or thermal technology, the totals, and all companies' renewables, low carbon and fossil totals.
  - Variables `derated_capacity` (table 5.7.A) and `thermal_capacity` (5.7.B), MW.
- **These are de-rated figures,** not installed capacity: wind, solar and small hydro are multiplied by 0.43, 0.17 and 0.365 (DESNZ's note 4), and grid export capacity is used where known (note 1).
  - The other generators' figures before 2006 are declared net capacity (note 6). Their falls in 2007, 2010 and 2012 are capacity moved to the major power producers (note 7).
- **Figures:**
  - All companies' de-rated capacity was 73,270 MW in 1996, 90,393 in 2010 and 74,510 in 2025.
  - Coal went from 26,623 MW in 1996 to 0 in 2025, and gas from 14,411 to 36,508 MW.
  - De-rated renewables rose from 1,955 to 27,730 MW.
- **Checks, all passing** (but the named differences), within 0.5 MW:
  - each group's parts add to its total;
  - the major power producers and the other generators add to all companies, item by item;
  - the renewables, low carbon and fossil totals equal their parts, and fossil, low carbon and pumped hydro make the total.
- **Its record:** written by run `20261025T194323Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T194328Z-local`), held from the live set, and in the release package (public).
- **The write's patch conflicted** in `docs/coverage.md`, `coverage.csv` and `archive_manifest.csv`, beside session 2729's rows. It was resolved as a union in the worktree, with no marker and no row twice, and committed before the finish.

## Cross-check

Against chain 136's DUKES tables, the major power producers in 2025:
- pumped hydro 2,744 MW here and in `desnz_uk_storage_annual`'s power capacity;
- nuclear 5,883 MW here and in `desnz_uk_power_stations` (May 2026);
- gas 33,616.9 MW here against the station list's 33,676 MW, export capacity against installed capacity (note 1).

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.gov.uk's robots file (its own request) | 200 |
| 2 | DUKES_5.7.xlsx (the fetch) | 200 |

Read recorded: 1466.

## Decisions made without you

- **DUKES 5.7 as the third own choice; public.**
- **DESNZ's 99 MW kept as published and named,** rather than the totals recomputed: the ERW keeps the source's figures.
- **Run before sessions 2731 to 2733,** so that its table is described and uploaded with the chain's others.

## For Samuel's ruling

- None new. (DESNZ may be told of its 2015 and 2016 totals; no letter is sent.)

## Files

- New: `warehouse/connectors/desnz_dukes_capacity.py`, `tests/test_session2734.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (read 1466) and `docs/licenses.md`.
- On the data machine only: `runs/c137/s2734/`, `runs/license_reads/s2734/`, `warehouse/raw/desnz_dukes/s2734probe1/`, `warehouse/output/desnz_uk_derated_capacity_annual.csv`.
