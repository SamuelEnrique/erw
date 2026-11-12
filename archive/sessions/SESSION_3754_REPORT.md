# Session 3754 report: the health summaries, the stale line, the streak

Energy Research Warehouse (ERW). Chain 211, session 5 of 24, data machine (lab-desktop), 12 November 2026. Opus 5.5. Model spend USD 0.

- **The health summaries of 6 to 10 November** are the ones the daily run wrote on their days, each refused at the guard and kept on `wip/red-health-*`. They were re-landed as written with session 3753's push (see its report), not regenerated.
- **"Stale on main" covers two more jobs** (`81d44fb33` on `wip/c211-code`, landed with the chain's branch):
  - latest prices: its last ok row of `erw_health`, allowed 1 hour (it commits nothing to main, so it is read from the health table);
  - the health summary itself: its commit on main ("Health summary <day>"), allowed 1 day.
  - The hourly network was already read, within 3 hours.
  - A limit of one hour reads "allowed 1 hour".
  - `tests/test_session3754.py` (3 tests); session 2864's fixtures given the two new inputs (13 tests, OK).
- **`/internal/health`'s streak:** `green_days` is 0 in every summary from 6 to 10 November (`site/data/health_days.json`, `counted_to` 2026-11-10). The reason: each of those days has failed steps, mostly the daily run's "merge tests" and the guard's refusals of the health summary commit, plus the data machine's `dm_test_replication` on 7 to 10 November. The streak can start again from the first day with no failed step, which needs the daily run green (session 3753) and `dm_test_replication` fixed (carried to chain 212's session 3779).

## Decisions made without you

- The past summaries were re-landed as written rather than rebuilt. A rebuild today would read "Stale on main" against today's clock and misstate what each day saw. The new stale rules apply from the next summary on.
- The two new stale rules read the latest prices from `erw_health` (it commits nothing) and the summary from main's log, which matches how the existing rules read the hourly network and the daily run.

## For Samuel's ruling

- None new.
