# Session 2957 report: the method notes and the tracers

6 November 2026, about 08:29 to 08:40 UTC, on lab-desktop (the data machine), chain 157 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **Every figure the four new method notes name was computed again from its table and matched: 29 of 29.**
  - generator_pipeline_by_grid: the two months' totals and the five moves;
  - iso_queue_snapshot_summary: active MW by grid;
  - nuclear_fleet_status: reactors, capacity and available energy;
  - gas_balance_weekly: the newest week and July's shares.
- **A license fault found and repaired in `iso_queue_snapshot_summary`:**
  - Release v1 holds ISO-NE's, MISO's and NYISO's queue tables whole: "license needed from 2026-10-21 ... needs written permission". Session 2953's build summarized all six grids, so it would have published what those holds keep back.
  - The table was rebuilt on CAISO, ERCOT and SPP only: 570 rows, archive run `20261106T083538Z-local`. Its header and method note name the three held grids. Session 2953's active MW for ISO-NE, MISO and NYISO are no longer in the table.
  - The archive is append-only, so the first build's rows stay in the private `erw-archive` bucket, which publishes nothing.
  - On the way: an internal license was tried first and refused by the coverage build, which derives a table's license from its inputs' coverage licenses. That attempt was reverted.
- **The records for the four tables:**
  - `licenses.py tables`, `write`, `check`: 637 tables, 0 problems.
  - The package: all four public.
  - `release_v1.STORAGE_HELD`: all four, until they are on Redivis's public draft (session 2959); `release_v1.py --check` 0 differences.
  - `live_set.yaml` `catalogue_hold`: all four.
  - Test 505 holds the license document to the script's output on a machine without the tables, so the record was built without `--headers`. `ercot_wind_solar_hsl_monthly`'s line is kept as on main (session 2940).
  - Tests: the four tables' own, and 275, 410, 505, 1001, 1008, 1009 with the live-set and coverage tests: 700 passed before 505's fix, then 505 and the package tests 26 passed.
- **The keys the pages will read** (for session 2958's wiring): `allgrids|queue|<row>` (active queue MW, CAISO, ERCOT and SPP); `allgrids|queuemonths|<row>` (the newest request year's median with at least 5 dated); the price board's gas group from `gas_storage:lower48` (`five_year_position_pct`, `vs_five_year_avg_bcf`); the pipeline's `entered_mw` and `online_mw` by grid.

## Decisions made without you

- **The held grids left out of the queue summary** rather than the table made internal.

## For Samuel's ruling

- None new.
