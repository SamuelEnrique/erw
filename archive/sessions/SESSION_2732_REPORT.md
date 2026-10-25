# Session 2732 report: seven days of the data jobs (no new failure; the package test's fix awaits the next daily run)

25 October 2026, about 19:59 to 20:15 UTC, on lab-desktop (the data machine), chain 137, unattended. Precheck passed (`runs/c137/pre2732.out`). Model spend USD 0. Pulls: GitHub's API 2 of 30; Supabase's `erw_health` 7 reads.

## Read these first

- **Every failed step since 23 October was opened** (`runs/c137/s2732/steps.out`), as session 2718's lesson asks:
  - 23 and 25 October, the daily run's "package tests": the coverage test that session 2718 fixed. The fix landed with chain 136 at 19:11 UTC (`b9c8ec2d`), after today's daily run, so the first run with it is 26 October's, from about 14:00 UTC.
  - **24 October, the same step: "1 error in 0.49s".** That is a collection error, not a test's failure, so the whole step stopped at once. Its log needs the repository's admin rights (this machine's token cannot read it), so its cause is not known. 26 October's run will show whether it was the same coverage fault.
  - 24 October, this machine's `dm_test_board` (tests 132 and 240): its group was put back as committed. It has passed since; today's local daily run lists it ok.
- **The package tests do not run fairly on this machine:** `pytest package/tests` from the main checkout failed throughout on row counts, as this machine's tables differ from the coverage GitHub's runner builds. It was stopped by my 900-second limit at 95 per cent (`runs/c137/s2732/pkg.out`). The daily run on GitHub is the test of record.
- **Failed steps by day** (`erw_health`): 19 October 3, 20 October 5, 21 October 0, 22 October 1, 23 October 1, 24 October 2, 25 October (to 20:00 UTC) 1 of 601.
- **GitHub's record** (`runs/c137/s2732/gh.py`, this machine's token, reads only):
  - The same 12 failed runs since 19 October, all `code branch` on task branches.
  - 26 runs since 17:19 UTC, each a success: chain watch 11, latest prices 11, hourly network 3, and chain 136's landing (code branch 1).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.github.com | 2 of 30 | the failed runs since 19 October; the runs since 25 October 17:19 UTC |
| Supabase (`erw_health`, read only) | 7 | seven days of rows, with every failed step's reason |

## Decisions made without you

- **No new fix:** the package test's fault was fixed in session 2718, and the 24 October collection error cannot be read without the repository's admin rights.

## For Samuel's ruling

- **The 24 October "package tests" log** (run on GitHub, about 14:10 UTC): readable only with admin rights. 26 October's daily run will say whether session 2718's fix ended the step's failures.

## Files

- New: this report. On the data machine only: `runs/c137/s2732/`.
