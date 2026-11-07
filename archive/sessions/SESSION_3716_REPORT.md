# Session 3716 report: the green streak against the health summaries

Energy Research Warehouse (ERW). Chain 208, session 17 of 20, portable laptop, 6 November 2026, about 23:12 to 23:14 UTC (during session 3706's gate). Branch `wip/3701-sellable`, commit `d7c608cde`.

- **Read:** `site/data/health_days.json` (written 6 November 01:41 UTC, `green_days` 0, counted to 5 November) against the fourteen summaries `queue/summary/2026-10-23-health.md` to `2026-11-05-health.md`.
  - Every day's failure count is the summary's: 1, 2, 1, 4, 6, 9, 10, 10, 2, 3, 3, 3, 3 and 7.
  - Every day is red, and the streak is 0, as `/internal/health` says.
  - The listed failures equal the count on every day.
- **`tests/test_session3716.py`** recomputes each of the last fourteen days from the summary files alone (its failures, its colour) and holds the record and `green_streak` to them. The days are whatever the repository holds, so a new day never turns it red by itself. 4 tests, OK.
- **`docs/machines.md`** gains "The green streak, as counted (session 3716)": the rows that count (scheduled steps and `dm_` steps), a red day, stale at source not a failure, short days not ending the streak while `SHORT_ENDS_STREAK` is off, and a missing day ending the count. The existing bullet named only part of this. The 24 test files that read `docs/machines.md`: 437 tests; 1 error, a Windows temporary folder's cleanup in `test_session185`, not the text.

## Decisions made without you

- The streak is recomputed from the summaries, not from `erw_health`: the summaries are the repository's record, and the test runs in a clean checkout.

## For Samuel's ruling

- None new. (The open one is session 479's: whether a short day ends the streak.)
