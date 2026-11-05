# Session 907 report: seven days of the data jobs

23 October 2026, from 07:25 UTC, on lab-desktop (the data machine), a session of `queue/done/049-day-23-october-data-margins-schedules-emissions.md`, in session 893's form. Model spend USD 0.

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
  | 23 October (to 07:25 UTC) | 196 | 0 |

- **No failed step since 22 October's one.** That was the package test's stale expectation for CARB's auction prices, which session 893 fixed with a test that keeps the package test in step with coverage. The fix reached main when chain 048 landed (`f9367c4d`), before today's daily run, which has not yet run.
- **17 to 20 October:** the causes sessions 682 and 893 named (Redivis's export cap and the old account's full storage, the data machine's live set and commit steps), none since 20 October.
- **GitHub's record** (`actions/runs?status=failure` since 17 October, 1 request): 6 failed runs, all of `code branch` (19 to 21 October); no data workflow failed as a run.
- Nothing to fix.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.github.com | 1 of 30 | the failed runs since 17 October |
| Supabase (`erw_health`, read only) | 7 | seven days of rows |

## Decisions made without you

- Read two hours after session 893 by the queue file's order. Its result is the same, with today's first rows added.

## For Samuel's ruling

- None new.

## Files

- New: this report. On the data machine only: `runs/c049/s907/`.
