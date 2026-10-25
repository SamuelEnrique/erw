# Session 2746 report: seven days of the data jobs, nothing new

25 October 2026, about 21:23 UTC, on lab-desktop (the data machine), chain 138, unattended. Precheck passed (`runs/c138/pre2746.out`). Model spend USD 0. Pulls: GitHub's API 2 of 30; Supabase's `erw_health` 7 reads.

## Read these first

- **No step has failed since session 2732 read the record at 19:59 UTC.** The one failed step of 25 October is the daily run's package test, from before session 2718's fix landed (`runs/c138/s2746/steps.out`, every reason opened).
- **The fix's first test is 26 October's daily run,** from about 14:00 UTC; session 2760 of the next chain will read it.
- **Failed steps by day** (`erw_health`): 19 October 3, 20 October 5, 21 October 0, 22 October 1, 23 October 1, 24 October 2, 25 October (to 21:23 UTC) 1 of 640.
- **GitHub's record** (`runs/c138/s2746/gh.py`, this machine's token, reads only):
  - The same 12 failed runs since 19 October, all `code branch` on task branches.
  - 16 runs since 19:59 UTC, each a success: chain watch 6, latest prices 6, hourly network 3, and chain 137's landing (code branch 1).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.github.com | 2 of 30 | the failed runs since 19 October; the runs since 25 October 19:59 UTC |
| Supabase (`erw_health`, read only) | 7 | seven days of rows, with 25 October's failed step's reason |

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report. On the data machine only: `runs/c138/s2746/`.
