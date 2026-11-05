# Session 989 report: seven days of the data jobs

23 October 2026, from 14:17 UTC, on lab-desktop (the data machine), a session of `queue/done/055-afternoon-23-october-data-outlook-hybrids-loans-dams.md`, in session 962's form, run while the daily run held the data lock (sessions 987 and 988 follow when it is free). Model spend USD 0.

## Read these first

- **Failed steps by day** (`erw_health`, read only):

  | Day | Steps | Failed |
  |---|---|---|
  | 17 October | 668 | 13 |
  | 18 October | 684 | 15 |
  | 19 October | 763 | 3 |
  | 20 October | 777 | 5 |
  | 21 October | 632 | 0 |
  | 22 October | 731 | 1 |
  | 23 October (to 14:17 UTC) | 395 | 0 |

- **No failed step since 22 October's one** (`daily prices`, `package tests`, session 893's fix, on main since chain 048), as sessions 934, 948 and 962 found.
- **GitHub's record:** the same 7 failed runs since 17 October, all of `code branch`; no data workflow failed as a run. Today's runs to 14:17 UTC: 157; of the 100 the first page lists, 39 `latest prices`, 38 `chain watch`, 11 `code branch` and 10 `hourly network` succeeded, 1 `code branch` failed (chain 051's, above). **Today's daily run started at 14:00 UTC and is in progress;** it took the data lock at 14:10 (until 19:30 at most), which is why session 985's write waits.
- Nothing to fix.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.github.com | 2 of 30 | the failed runs since 17 October; today's runs (this machine's token, reads only) |
| Supabase (`erw_health`, read only) | 7 | seven days of rows |

## Decisions made without you

- **Run out of order,** while the lock is held: this session writes nothing to the warehouse.

## For Samuel's ruling

- None new.

## Files

- New: this report. On the data machine only: `runs/c055/s989/`.
