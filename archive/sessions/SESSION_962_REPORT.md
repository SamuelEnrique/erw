# Session 962 report: seven days of the data jobs

23 October 2026, from 13:11 UTC, on lab-desktop (the data machine), a session of `queue/done/054-day-23-october-data-federal-royalties-wind-costs-minerals.md`, in session 934's form. Model spend USD 0.

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
  | 23 October (to 13:11 UTC) | 361 | 0 |

- **No failed step since 22 October's one** (`daily prices`, `package tests`, session 893's fix, on main since chain 048), as sessions 920, 934 and 948 found; 40 more of today's steps since session 948, all passed.
- **GitHub's record:** the same 7 failed runs since 17 October, all of `code branch`, the newest chain 051's first check run (39928894186). No data workflow failed as a run; chain 053's check run (39949265023) passed. Today's runs to 13:11 UTC: 145; of the 100 the first page lists, 38 `latest prices`, 38 `chain watch`, 11 `hourly network` and 12 `code branch` succeeded, 1 `code branch` failed (above). The daily run has not yet run today.
- Nothing to fix.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.github.com | 2 of 30 | the failed runs since 17 October; today's runs (this machine's token, reads only) |
| Supabase (`erw_health`, read only) | 7 | seven days of rows |

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report. On the data machine only: `runs/c054/s962/`.
