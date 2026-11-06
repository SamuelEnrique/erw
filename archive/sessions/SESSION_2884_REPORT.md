# Session 2884 report: seven days of the data jobs, read again

6 November 2026, about 01:13 to 02:00 UTC, on lab-desktop (the data machine), chain 147, unattended. Model spend USD 0. Pulls: GitHub's API about 20 of 30; Supabase's `erw_health` read only.

## Read these first

- **The daily run committed to main again.** "Daily prices 2026-11-06" (`e2794ff06`, 01:32 UTC) came from run 42120465428, which session 2863 dispatched with `days=7`:
  - merge tests ok;
  - the pull, the validation and coverage ok, about 3 hours;
  - the commit;
  - the package tests, which failed one test (below; the job stays green by design, and the failure is a row of `erw_health`);
  - yesterday's health summary.
  - Its first scheduled run, at 14:00 UTC on 6 November, is session 2886's (chain 148) to read.
- **The newest summary's first line** (`queue/summary/2026-11-05-health.md`): "**Stale on main:** hourly network, 0.2 days (its last ok step in erw_health, 2026-11-05 22:05 UTC; allowed 3 hours)." The hourly network skips while the daily run holds the data lock, and the run held it from about 22:30 to 01:45 UTC. The daily run itself is no longer named. A job allowed hours is now said in hours (`wip/c147-data`).
- **Failed steps by day** (`runs/s2884_seven.out`):

  | Day | Rows | Failed | A job failed for the whole day |
  |---|---|---|---|
  | 30 October | 700 | 10 | none |
  | 31 October | 675 | 2 | daily prices (merge tests) |
  | 1 November | 665 | 3 | daily prices (merge tests) |
  | 2 November | 683 | 3 | daily prices (merge tests) |
  | 3 November | 671 | 3 | daily prices (merge tests) |
  | 4 November | 658 | 3 | daily prices (merge tests) |
  | 5 November | 687 | 7 | none |
  | 6 November (to about 01:45) | 51 | 0 | none |

- **Every failed step was opened:**
  - **30 October:** the account's spending limit, so every model step failed (session 2864). Then the three-run failure streak rows.
  - **31 October to 5 November:** "merge tests", twice a day (session 2863's fix). The data machine's own `dm_test_findings` failed once a day too.
  - **The run of 22:19 UTC:**
    - `eia930`: CISO's demand forecast was 25 hours short of 168, from the clock change of 1 November. EIA's own gap; the connector writes nothing incomplete.
    - `portwatch`: PortWatch answered "Invalid URL" for chokepoint 6. The publisher's side; this is the first day of it.
    - `ercot_as_prices`: ERCOT answered HTTP 503 at `/misapp` four times, so `ercot_as_prices_rollup` had no input.
    - `package tests`: `test_derived_tables_flag_license_and_inputs` on `ercot_wind_solar_hsl_monthly`.
- **Two faults of this repository's code, fixed with their tests** (on `wip/c147-data`, landed with this chain):
  - `dm_test_findings`: `tests/test_session174.py` required each card's `computed_at` to begin "2026-10-". The data machine recomputes the cards daily, so from 1 November the test failed every day, and the run put every recomputed card back. The test now holds the time to between 1 October 2026 and now.
  - The package test: `ercot_wind_solar_history.py` registered its derived monthly table under the publisher "Energy Research Warehouse (ERW)", where the package requires "Energy Research Warehouse (ERW), derived". The code and the registry's row are corrected, and the test passes on this machine.

## Decisions made without you

- **EIA's, PortWatch's and ERCOT's failures left as the publishers' own.** PortWatch's is watched for a second day.

## Files

- On `wip/c147-data`: `tests/test_session174.py`, `warehouse/connectors/ercot_wind_solar_history.py`, `warehouse/metadata/sources.csv`, `warehouse/health.py`, `tests/test_session2864.py`, this report.
- On the data machine only: `runs/c147/seven_days.py`, `runs/s2884_seven.out`, `runs/s2884_pkg.out`.
