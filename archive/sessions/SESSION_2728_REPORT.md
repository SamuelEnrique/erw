# Session 2728 report: the UK's maximum load, plant load factors and thermal efficiency, 1996 to 2025 (DESNZ's DUKES 5.10), public, a source of the session's own choosing

25 October 2026, about 19:27 to 19:33 UTC, on lab-desktop (the data machine), chain 137, unattended. Precheck passed (`runs/c137/pre2728.out`). Model spend USD 0. Pulls: 2 requests of 20 (1 by the probe, 1 fetch of the workbook, read offline by the trial and the write).

## Why this source

- **This chain's four planned territories gave no table** (Prince Edward Island, Yukon, the Northwest Territories, Nunavut).
- **The ERW held no UK peak load or load factor.** DUKES 5.10 gives them for the major power producers, the companion of chain 136's DUKES tables 5.11, 5.13 and 5.16, from the same chapter, host and licence.

## Read these first

- **The host:** www.gov.uk's robots file closes only print and search paths and names no Claude agent (read 1464). The chapter page was read in session 2714 (read 1447). The terms are the Open Government Licence v3.0 (read 315), so the table is **public**.
- **A new table, `desnz_uk_plant_loads_annual`** (series, 425 rows, 11 entities, `power`), 1996 to 2025:
  - **The maximum load** (`max_load`, MW) of the UK, Great Britain and Northern Ireland, and of England and Wales and Scotland where given (six years).
  - **Maximum demand as a share of the major power producers' capacity** and **the system load factor** (pct, on `uk`).
  - **Load factors** (pct) of CCGT, nuclear, pumped storage, conventional thermal, coal and all plant.
  - **Thermal efficiency** (pct, gross calorific value) of CCGT, coal and nuclear.
- **DESNZ's notes, kept in the header and connector:**
  - Note 3: a year's maximum load is that of the twelve months ending March of the next year, so a winter's peak falls in the year it starts.
  - Notes 6, 8 and 11: the bases of the conventional thermal and all-plant load factors, and the regional demands before 2008.
- **Figures:**
  - The UK's maximum load was 56,815 MW in 1996, 60,893 in 2010, 48,945 in 2020, 47,361 in 2024 and 51,538 in 2025.
  - CCGT's load factor fell from 71.2 per cent in 1996 to 29.7 in 2025; its thermal efficiency rose from 45.3 to 48.0 per cent.
  - Coal's figures are zero in 2025, its first year after the last station closed.
- **Checks, all passing:**
  - England and Wales and Scotland add to Great Britain, and Great Britain and Northern Ireland to the total, within 1 MW;
  - every percentage lies in [0, 100];
  - every row label is matched exactly; a new one stops the run.
- **Its record:** written by run `20261025T193019Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T193023Z-local`), held from the live set, and in the release package (public). The patch applied cleanly.

## Cross-check

No other ERW table holds the UK's peak. A plausibility check against `elexon_gb_demand_daily` (Elexon's daily national demand, MWh), year by year from April to March: each year's GB peak sits 8,150 to 12,550 MW above the highest day's mean.

| DESNZ's year | GB maximum load (MW) | Elexon's highest day | That day's mean (MW) |
|---|---|---|---|
| 2022 | 47,117 | 15 December 2022 | 37,488 |
| 2023 | 46,854 | 17 January 2024 | 36,917 |
| 2024 | 46,045 | 10 January 2025 | 37,888 |
| 2025 | 50,101 | 6 January 2026 | 37,550 |

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.gov.uk's robots file (its own request) | 200 |
| 2 | DUKES_5.10.xlsx (the fetch) | 200 |

Read recorded: 1464.

## Decisions made without you

- **DUKES 5.10 as the own choice; public.**
- **Entities by area and plant type, variables by measure,** so that one plant type's load factor and efficiency sit on one entity.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/desnz_dukes_plant_loads.py`, `tests/test_session2728.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (read 1464) and `docs/licenses.md`.
- On the data machine only: `runs/c137/s2728/`, `runs/license_reads/s2728/`, `warehouse/raw/desnz_dukes/s2728probe1/`, `warehouse/output/desnz_uk_plant_loads_annual.csv`.
