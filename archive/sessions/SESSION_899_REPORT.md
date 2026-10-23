# Session 899 report: the natural gas pipeline projects (EIA)

23 October 2026, from 06:35 UTC, on lab-desktop (the data machine), a session of `queue/done/049-day-23-october-data-margins-schedules-emissions.md`. Model spend USD 0. Pulls: EIA, 4 requests of 6 (the address `/naturalgas/pipelines/`, which answers 403, a folder with no page; the natural gas data page; then, through the raw store, the page and the workbook).

## Read these first

- **One events table written, validated, archived, in coverage (sector gas, public), in the release package, both holds:** `eia_gas_pipeline_projects`, 1,334 projects from EIA's tracker of August 2026 (137 current, 1,197 historical from 1996). For each: operator, type (new pipeline, expansion, lateral, conversion), status, states and regions, cost in millions of dollars as EIA writes it (a range kept), miles, added capacity (MMcf/d), diameter, authority and docket, notes, demand served.
- **The event date by what EIA gives:**
  - completed date (1,127 projects);
  - else the year in service's 1 January (139);
  - else the date EIA last updated the record (68, projects with neither).
  - `x_date_basis` says which. No project is left out for want of a date.
- **No key, left out:** three projects EIA gives twice with different rows under one name and year (Columbia to Eastover Pipeline 2016, East Side Expansion Project 2015, TETCO Capacity Expansion Project 2016), named in the header.
- **The cross-check the queue file named does not apply:** `eia_gas_interstate_annual` holds flows between states, not capacity. Checked instead within the tracker:
  - The current sheet's projects: 34 applied, 31 under construction, 30 approved, 13 announced, 10 on hold, 10 pre-applied, 4 completed, 3 part completed, 2 proposed.
  - Two project names appear in both sheets.
  - The historical capacity completed each year: 25,165 MMcf/d in 2018, 4,231 in 2022, 18,696 in 2024.
  - The current projects' capacity by year in service: 28,814 MMcf/d in 2027, 25,579 in 2028.

## Decisions made without you

- The tracker as an events table (one row a project), `event_type` `pipeline_project`.
- The newest workbook the page links (`Aug2026`), chosen by the month and year in its name.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_gas_pipeline_projects.py`, `tests/test_session899.py` (4 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. Session 898's report (one wording).
- On the data machine only: `runs/c049/`, `runs/license_reads/s899/`, `runs/s899*`.

## Corrected by session 905

The method notes' checks (session 905) found these against the code and the tables:

- The completed and last-updated dates carried a time (`1996-06-01 00:00:00`): the cells come as dates the reader did not catch. Session 905 writes them as YYYY-MM-DD and wrote the table again.
- An id's last part was EIA's year text as given (`none` for 29, `na` for 39, one `2020-2027 (phased)`); it is now a slug (`2020_2027_phased`).
- One historical project (SONAT South Sys Expansion II Phase 1A*) gives a completed date of 1903-11-05 against a year in service of 2003; kept as EIA gives it, so the table runs from 1903, not 1996.
- The project types also include Reversal (42), Upgrade (24) and Abandonment (2).
