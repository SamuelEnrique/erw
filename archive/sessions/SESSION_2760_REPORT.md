# Session 2760 report: seven days of the data jobs, nothing new

25 October 2026, about 22:53 UTC, on lab-desktop (the data machine), chain 139, unattended. Precheck passed (`runs/c139/pre2760.out`). Model spend USD 0. Pulls: GitHub's API 2 of 30; Supabase's `erw_health` 7 reads.

## Read these first

- **No step has failed since session 2746 read the record at 21:23 UTC.** Every failed step of the seven days was opened (`runs/c139/s2760/steps.out`, each reason's first line). The one of 25 October is the daily run's package test (`test_coverage_has_one_row_per_table_and_the_documented_columns`), from before session 2718's fix landed.
- **26 October's daily run has not run yet** (it starts about 14:00 UTC). File 139 expected this session to read it, but the chain reached this session on the evening of 25 October. The fix's first test therefore falls to the next chain's data-jobs session (2774 of file 140).
- **Failed steps by day** (`erw_health`): 19 October 3, 20 October 5, 21 October 0, 22 October 1, 23 October 1, 24 October 2, 25 October (to 22:53 UTC) 1 of 679. The reasons, as recorded:
  - 19 October: the Roundup's weather restore over Redivis's 100 GB export limit; the live set's load of two tables; the license check's four unknown tables in the public dataset.
  - 20 October: EIA-930's incomplete demand data; generation mix's absent input; a package test's partition; the data machine's ERCOT hub store and its live-set load.
  - 22 to 25 October: package tests (a license flag, the coverage columns, an import error), and the data machine's test board.
  - All are of earlier days and were reported by the sessions that read them (2718, 2732, 2746); none recurs after 25 October's daily run.
- **GitHub's record** (`runs/c139/s2760/gh.py`, this machine's token, reads only):
  - The same 12 failed runs since 19 October, all `code branch` on task branches; none new.
  - 16 runs since 21:23 UTC, each a success: chain watch 7, latest prices 7, hourly network 1, and code branch 1.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.github.com | 2 of 30 | the failed runs since 19 October; the runs since 25 October 21:23 UTC |
| Supabase (`erw_health`, read only) | 7 | seven days of rows, every failed step's reason |

## Decisions made without you

- **The 26 October run left to file 140's session 2774,** as it has not run.

## For Samuel's ruling

- None new.

## Files

- New: this report. On the data machine only: `runs/c139/s2760/`.
