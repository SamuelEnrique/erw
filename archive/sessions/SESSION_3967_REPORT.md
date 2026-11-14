# Session 3967 report: the daily run of 14 November, two faults fixed

Energy Research Warehouse (ERW). Chain 278, data machine (lab-desktop), 14 November 2026, 14:54 to 16:17 UTC. Opus 5.5. Model spend USD 0. No request to a publisher. `erw_health` read over `SUPABASE_DB_URL` (`runs/c278/daily_now.py`).

## The daily run of 14 November (run 43602537759, dispatched 14:00 UTC)

- **39 steps in `erw_health`:** 34 ok, 2 failed, 2 skipped, 1 retried.
- **`daily run` failed at 15:57 UTC**, at the coverage step: "news_scores_shadow: sources ['IEA (en dash) International Energy Agency'] are not in sources.csv; cannot set its license". No daily commit today; the board, package tests and the guard's verdict on the daily commit were not reached.
- **`portwatch` failed at 14:54:** the Strait of Hormuz's third page answered HTTP 429 ("API calls quota exceeded (6012 request units ...)") on four tries inside 30 seconds.
- **Expected, not faults:** `ercot_as_prices` skipped (ruling 2 of 6 November); `carb_lcfs` skipped (CARB's newest week 2026-09-14, 61 days old); `frb_treasury` passed on its retry (the Board's empty body, as on 12 November).
- **The health summary of 13 November reached main** (`7c594771a`, after the run's failure): the guard let a bot push through. Its line: "**Stale on main:** daily prices, 1.7 days (its last commit on main, 'Daily prices ...', 2026-11-12 23:27 UTC; allowed 1 day); health summary, 2.0 days".

## Fault 1: the shadow table's dashed outlet name (fixed)

- **Cause:** session 3940 folded the IEA outlet's en dash in `news_stories` and `news_index` and joined the registry's two IEA rows. `news_scores_shadow` copies each story's outlet into its `source`, and the shadow scorer expired on 6 October (`warehouse/config/shadow.yaml`), so nothing rewrote its 15 rows naming the IEA with the dash. The runner restores that table from the Redivis draft each day.
- **Fix:** `warehouse/news/ingest.py` `fold_shadow_sources`, called every day before coverage and before the registry update, writes again only the shadow rows whose outlet name changes (scores untouched, its header's Retrieved line kept, a line saying what was done). Not in `shadow.py`: the daily model cap can skip that step.
- **Test** `tests/test_session3967_shadow.py` (5): the dashed names folded and nothing else moved; the header; a second run writes nothing; no table, no write; `main` calls it before the registry. With test 3940: 16 passed.

## Fault 2: PortWatch's retries inside ArcGIS Online's quota minute (fixed)

- **Fix:** `warehouse/connectors/portwatch.py` passes `wait=20` to the shared `with_retries`: waits of 20, 40 and 60 seconds, so the fourth try comes two minutes after the first. A fourth 429 still fails loudly.
- **Test** `tests/test_session3967.py` (3); with the PortWatch tests of sessions 173, 3015, 321 and 324: 38 passed.

## What waits

- **Both fixes ride in gate b** (`wip/c278-land-b`, started 16:04 UTC).
- **A second daily run today:** dispatched once gate b lands and the data machine's own run (17:00 UTC) has let go of the data lock, which both share; otherwise tomorrow's 14:00 run is the first with the fixes.
- **The data machine's run of 14 November** (17:00 UTC): waiting.

## Decisions made without you

- **The fold sits in the news ingest,** which runs every day, not in the expired shadow scorer.
- **The re-run waits for the data machine's run** rather than taking the lock from it.

## For Samuel's ruling

- None.
