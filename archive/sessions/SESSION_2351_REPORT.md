# Session 2351 report: Sweden's production an hour by type (Svenska kraftnät's Mimer), a second source of the session's own choosing

24 October 2026, from 06:44 UTC, on lab-desktop (the data machine), a session of `queue/done/105-day-8-november-data-mexico-india-peru-korea.md`, there numbered 2301. The code machine had used 2301 on main, so this chain's sessions 2300 to 2306 are 2350 to 2356 (session 2350's report). Model spend USD 0.

Pulls: 12 requests of 20:
- mimer.svk.se's robots address (HTTP 404), its home page and its production statistics page;
- six downloads, one a production type, all of Sweden, 1 January 2020 to 18 March 2025;
- www.svk.se's robots file, home page and its "Om webbplatsen" page.

The trial and the write ran offline.

## Read these first

- **Why Svenska kraftnät.**
  - **Not held:** the ERW held no Swedish grid source (api.scb.se's v1 is closed), and no chain running or planned has taken Sweden.
  - **Avoided:** BPA was the other candidate, but it is held.
  - **Avoided countries:** those of chains 102 to 109 and chain 106's own choices (Latvia, Iceland, Slovenia).
- **Mimer's production statistics end on 18 March 2025.** The page says the days from 2025-03-18 on are reported to eSett and published on eSett Open Data. The table is therefore closed history, and eSett (which covers Sweden, Finland, Norway and Denmark) is the way to its later days.
- **One series table, `svk_sweden_production_hourly`:** 274,176 figures, internal.
  - **Span:** six production types, hourly, all of Sweden, 1 January 2020 (Swedish time) to 18 March 2025.
  - **Unit:** MWh, Mimer's settled kWh divided by 1,000.
  - **Variables:** `generation_nuclear`, `generation_other_thermal`, `generation_unspecified_measured`, `generation_solar`, `generation_hydro` and `generation_wind`.
  - **Extra column:** `x_published` keeps Mimer's publication time as printed.
- **The time base, found from the data.**
  - No page states it, but every day has 24 hours, the clock-change days included, so the hours are a fixed offset.
  - June's mean solar output is symmetric about the 12:00 label. Sweden's solar noon is about 11:50 Swedish normal time; in UTC labels it would fall at 13:00.
  - So the hours are Swedish normal time (UTC+1 all year) labelled by their start, and `ts_utc` is the label minus one hour. The header and the docstring say how this was found.
- **The checks:**
  - every file's rows sum to its "Summa" line;
  - 24 hours every day;
  - no hour twice;
  - no blank figure.
- **The cross-check against Eurostat's net production for Sweden** (`eurostat_electricity_monthly`, `runs/c105/s2351/cross_eurostat.py`):
  - **Nuclear, hydro and wind** agree within 0.5 percent every year from 2020 to 2024, and exactly in 2021 and 2022.
  - **Solar** is about 58 percent of Eurostat's, and other thermal about 50 percent: Mimer counts production settled at the grid, without production behind the meter or used on industrial sites.
  - **All types together** come to 95 to 97 percent.
- **License: internal.** Neither Mimer nor svk.se's about page states terms; the next licenses round reads them.
- **Registered:** the sector rule (`power`), the live-set hold, the license tables (licenses check: 491 tables, 0 problems). The test is `tests/test_session2351.py` (3 tests).

## Errors

- **The test's first fixture put the Summa line 1 kWh off**, which the check allows for rounding; it is now 10 kWh off.
- **The write's metadata patch did not apply** (the main checkout lags main). The table's own rows were put in by `runs/c102/add_own_rows.py` and checked: one row in each of the five files.

## Decisions made without you

- **Sweden from Svenska kraftnät's Mimer,** with its history to March 2025. eSett's later days are left for a later session.
- **The time base read from the data** (24-hour days and the solar curve), no page stating it.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/svk_sweden.py`, `tests/test_session2351.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c105/s2351/`, `runs/license_reads/s2351/`, `runs/s2351_*`.
