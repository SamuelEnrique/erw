# Session 2444 report: seven days of the data jobs, nothing new to fix

24 October 2026, from 12:03 UTC, on lab-desktop (the data machine), chain 117, unattended. Precheck passed (`runs/c117/pre2444.out`). Model spend USD 0. Pulls: GitHub's API 2 of 30; Supabase's `erw_health` 7 reads.

## Read these first

- **Failed steps by day** (`erw_health`, read only, `runs/c117/s2444/byday.py`):

  | Day | Steps | Failed |
  |---|---|---|
  | 18 October | 684 | 15 |
  | 19 October | 763 | 3 |
  | 20 October | 777 | 5 |
  | 21 October | 632 | 0 |
  | 22 October | 731 | 1 |
  | 23 October | 740 | 1 |
  | 24 October (to 12:03 UTC) | 347 | 0 |

- **No failed step is new** since session 2395's look (10:10 UTC, 292 steps on 24 October). The newest is still 23 October's package test, traced by sessions 2039, 2095 and 2145.
- **GitHub's record** (`runs/c117/s2444/gh.py`, this machine's token, reads only):
  - 12 failed runs since 18 October, all `code branch`, the same twelve as sessions 2332, 2381 and 2395 found.
  - 23 runs since 10:10 UTC on 24 October:
    - chain watch 9, latest prices 8 and hourly network 2, all successes;
    - code branch: 2 successes (chain 110's and chain 113's landings), 1 cancelled, 1 running (chain 114's landing, run 40092336414, started 12:03 UTC).
    - The cancelled run (40085717917, chain 110's branch at `257f12c6`, 10:23 UTC) was replaced 12 seconds later by the run of that branch's next push (40085732054), which passed. It was a superseded run, not a failure.
- **Nothing to fix in the repository.** The live site still answers HTTP 402 (Vercel); no data job reads it.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.github.com | 2 of 30 | the failed runs since 18 October; the runs since 24 October 10:10 UTC |
| Supabase (`erw_health`, read only) | 7 | seven days of rows |

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report. On the data machine only: `runs/c117/s2444/`.
