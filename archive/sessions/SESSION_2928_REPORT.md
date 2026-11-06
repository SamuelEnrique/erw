# Session 2928 report: the data machine's own run

6 November 2026, about 06:10 to 06:13 UTC, on lab-desktop (the data machine), chain 153, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **`runs/data_machine_status.txt`** is the run of 5 November (written 18:10 UTC). Every step is ok or a stated skip but one:
  - `dm_test_findings failed: FAILED (failures=1)`;
  - `dm_carb_lcfs` skipped as stale at the source (CARB's newest week is 14 September, 52 days old, against a limit of 28);
  - the monthly and weekly steps skipped as already done for November and week 45.
- **The `dm_` rows of `erw_health`, 30 October to 6 November:**

  | Day | dm_ rows | Failed |
  |---|---|---|
  | 30 Oct | 52 | 0 |
  | 31 Oct | 51 | 0 |
  | 1 Nov | 52 | 1 (`dm_test_findings`) |
  | 2 Nov | 70 | 1 (`dm_test_findings`) |
  | 3 Nov | 59 | 1 (`dm_test_findings`) |
  | 4 Nov | 51 | 1 (`dm_test_findings`) |
  | 5 Nov | 51 | 1 (`dm_test_findings`) |
  | 6 Nov | 0 (its run is at 17:00 UTC) | |

- **`dm_test_findings` passes now.** Its own command, run from the main checkout (`PYTHONPATH=tests python -m unittest test_session173 test_session174 test_session182 test_session274 test_session381`), gave 73 tests OK (`runs/c153/dm_findings.out`). Chain 147's session 2884 fixed it. That fix reached main at 03:03 UTC on 6 November (`a41dd2e41`), after the run of 5 November, so the five failures predate it. No new fault.
- **Not read:** the run of 6 November at 18:00 UTC (chain 151's item 9). It comes after this chain's sessions, so it is carried to chain 155's session 2942.

## Decisions made without you

- None.

## For Samuel's ruling

- **CARB's LCFS credit prices** have not moved past 14 September at the source: whether the 28-day staleness limit should stay, or the table be marked as CARB's pause.
