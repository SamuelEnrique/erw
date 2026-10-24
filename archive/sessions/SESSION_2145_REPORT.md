# Session 2145 report: seven days of the data jobs

24 October 2026, from 00:31 UTC, on lab-desktop (the data machine), chain 090, unattended. Done in session 962's form while the helper drafted session 2143's notes. This session writes nothing to the warehouse. Model spend USD 0.

## Read these first

- **Failed steps by day** (`erw_health`, read only, `runs/c090/s2145/byday.py`, from session 2095's):

  | Day | Steps | Failed |
  |---|---|---|
  | 18 October | 684 | 15 |
  | 19 October | 763 | 3 |
  | 20 October | 777 | 5 |
  | 21 October | 632 | 0 |
  | 22 October | 731 | 1 |
  | 23 October | 740 | 1 |
  | 24 October (to 00:31 UTC) | 20 | 0 |

- **No failed step is new since session 2095's look.** The newest is the same one: 23 October's daily run failed its package test (`test_coverage_has_one_row_per_table_and_the_documented_columns`). Sessions 2039 and 2095 traced it to a coverage row a data chain had rebuilt with main's validator, gone from main since.
- **GitHub's record:**
  - 10 failed runs since 18 October, all `code branch`, the same ten session 2095 listed (the newest chain 067's landing, `task/2070-2083-data`, 20:49 and 21:14 UTC on 23 October).
  - No data workflow failed as a run.
  - 146 runs since 23 October 12:00 UTC; of the 100 listed, the data workflows all succeeded: chain watch 36, latest prices 34, hourly network 10, daily prices 1.
  - The `code branch` runs (13 succeeded, 3 cancelled, 3 failed) are other chains' landings in that window, theirs to read.
- **Nothing to fix in the repository.**

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.github.com | 2 of 30 | the failed runs since 18 October; the runs since 23 October 12:00 UTC (this machine's token, reads only) |
| Supabase (`erw_health`, read only) | 7 | seven days of rows |

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report. On the data machine only: `runs/c090/s2145/`.
