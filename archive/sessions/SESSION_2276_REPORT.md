# Session 2276 report: seven days of the data jobs

24 October 2026, from 04:50 UTC, on lab-desktop (the data machine), chain 103, unattended, in session 962's form, while session 2275's upload ran. This session writes nothing to the warehouse. Model spend USD 0.

## Read these first

- **Failed steps by day** (`erw_health`, read only, `runs/c103/s2276/byday.py`):

  | Day | Steps | Failed |
  |---|---|---|
  | 18 October | 684 | 15 |
  | 19 October | 763 | 3 |
  | 20 October | 777 | 5 |
  | 21 October | 632 | 0 |
  | 22 October | 731 | 1 |
  | 23 October | 740 | 1 |
  | 24 October (to about 04:50 UTC) | 140 | 0 |

- **No failed step is new** since session 2234. The newest is still 23 October's daily run package test (`test_coverage_has_one_row_per_table_and_the_documented_columns`). Sessions 2039 and 2095 traced it to a coverage row a data chain had rebuilt with main's validator.
- **GitHub's record** (`runs/c103/s2276/gh.py`):
  - 11 failed runs since 18 October, all `code branch`, the same 11 session 2234 listed. None is new: chain 101's landing (`task/2238-2251-data`) passed at its first attempt.
  - No data workflow failed as a run.
  - Runs since 24 October 03:00 UTC (21): chain watch 8, latest prices 8, hourly network 2 and `code branch` 3, all successes.
- **The live site** still answers Vercel's HTTP 402 on every page (chain 101's session 2251 found it on both snapshots). The data jobs above run; only the site's deploys are affected. It stays in the chain's note for Samuel.
- **Nothing to fix in the repository.**

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.github.com | 2 of 30 | the failed runs since 18 October and the runs since 24 October 03:00 UTC |
| Supabase (`erw_health`, read only) | 7 | seven days of rows |

## Decisions made without you

- None.

## For Samuel's ruling

- The site's Vercel deployment answering 402 (in the note, as in chains 099 and 101).

## Files

- New: this report. On the data machine only: `runs/c103/s2276/`.
