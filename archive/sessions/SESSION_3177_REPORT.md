# Session 3177 report: the markets' operating tables: the grids' stress (chain 166)

6 November 2026, about 14:12 to 14:20 UTC, on lab-desktop, second window, chain 166, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **7 drafts added to the review list** (module `deep.markets_operations`, state draft), from `warehouse/analysis/findings/deep/stress.py` on the ERW's `grid_stress_yearly` (2019 to 2025):
  - **Solar in the tightest hours:**
    - ERCOT: 5.0 percent of its solar capacity in 2025, against 71.1 percent in 2019. Its tightest hours have moved to when solar is down.
    - PJM: 34.4, against 19.3.
  - **Wind in ERCOT's tightest hours:** 20.6 percent of its wind capacity in 2025, against 17.7.
  - **Wind and solar's capacity factor in ERCOT:** 29.7 percent in 2025, against 32.6.
  - **Calm hours** (wind and solar far below usual):
    - CAISO: 2,776 in 2025, against 2,180 in 2019.
    - PJM: 1,976, against 1,492.
    - ERCOT: 592, against 396.
- **Checked:** all 7 reproduce from their own scripts, and all 178 do-files hold.

## What it did

- **`deep/stress.py`:** five candidates. `tests/test_session3177.py` (1 test, passed). Gas in the tightest hours fails the tests in every grid.

## Decisions made without you

- **The single-hour extremes of the table** (the year's lowest net load, its largest ramp) are not candidates: session 252's lesson, no measure is one interval of a year.
- **Not hunted:** node basis (from October 2025) and the scarcity hours (from November 2023) are too short for the tests.
- **The ERCOT solar sentence names what moved** (the tightest hours' timing) only as the table's own definition; it does not state a cause.

## For Samuel's ruling

- None new.
