# Session 455 report: the loader, values not stamps (a branch, not landed)

21 October 2026, from 09:06 UTC, unattended, on lab-desktop (the data machine), the fourth session of the chain of 21 October, day (`queue/done/018-day-21-october-data.md`). Model spend USD 0. Pulls: none. **On [`wip/455-loader`](https://github.com/SamuelEnrique/erw/tree/wip/455-loader) (`29b1bffc`), not landed, for Samuel's ruling.**

## Read these first

Three changes to `warehouse/supabase/load.py`, each with its tests in `tests/test_session455.py` (10 tests; with the loader's earlier tests of sessions 60, 166 and 206, 63 pass):

- **(b) A row is written when its values move, not when only its stamp does.** `canon()` takes `stamps=False`, which leaves `retrieved_at` (`STAMPS`) out of the compared body. `value_diff()` is the comparison `sync_table()` already made, now without the stamps. A rebuilt table whose rows have the same values writes nothing, and a row whose value moved is written with its new stamp. A key gone from the file, and a license change, are still caught. One consequence for the ruling: an unchanged row in Supabase keeps the `retrieved_at` of the run that last changed it, not of the latest run that read it.
- **(a) An older copy equal in value is no rollback.** When `older_than_live()` finds the file's stamps older (session 60's guard), the loader now runs `value_diff()`. If no row differs and none is gone, the table loads as unchanged: nothing is written, and the live rows keep their stamps. Otherwise it is refused as before, the message now giving the count of rows that differ. This is session 384's draft (its report, part c), built on the comparison the loader already makes, so the table is read once.
- **(c) `series` vacuumed only after a large write.** `main()` counts the rows written and deleted by shape table. `vacuum()` runs only `ANALYZE` on a shape table the load changed by 1% of its rows or less (`VACUUM_SHARE`). `headers`, `catalogue` and `sources` are vacuumed as before, and so is everything when no counts are given (`--vacuum-full` unchanged).

## What (b) would have written

| Load | Written | Under (b) | Source of the count |
|---|---|---|---|
| session 438, `caiso_curtailment_profile` and `eia930_demand_growth` | 30,232 | **8** | the trial builds against the held copies (session 438): 4 and 4 values moved |
| session 432, `iso_queue_statistics` | 474 | 474 | every written row had a moved value (the comparison of 432) |
| session 452, `ercot_peak_premium_*` | 25,872 | 394 at most | the archive's count of rows new or changed (114 and 280), which compares without `retrieved_at` |
| session 374, `node_basis_daily` | 957,969 | not known | every live row now carries 20:35:34 UTC, so whether the rows were new to Supabase or rewritten is no longer readable; under (b) a rewrite of equal values would have written none |

Under (c), the loads of sessions 432 (474 rows), 438 (30,232) and 452 (25,872) are each under 1% of `series` (3.6 million rows), so `series` would have been analysed only. Session 374's 957,969 rows (27%) would still have been vacuumed. Measured from the sessions' own counts and the archive's, with no load.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | (session 454's, the same hour) |
| `tests.test_session455`, `test_session60`, `test_session166`, `test_session206` | 0 | 63 tests, 3 skipped |

## For Samuel's ruling

- Merge `wip/455-loader`: (b) changes what `retrieved_at` means for a live row (the last run that changed it), (a) follows from (b), (c) changes the daily load's vacuum.

## Files

- On `wip/455-loader`: `warehouse/supabase/load.py`, `tests/test_session455.py`.
- On this chain's branch: this report.
