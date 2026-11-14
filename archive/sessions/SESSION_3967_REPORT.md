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
- **The data machine's run of 14 November** (17:00 UTC): read below (added at 18:45 UTC).

## The data machine's run of 14 November (17:00 to 18:34 UTC)

- **Every step ok or expected** (`runs/data_machine_status.txt`) but three: `dm_carb_lcfs` skipped (CARB 61 days old), `dm_live_set` skipped ("the database gate is closed (8.95 s, 1000 rows of iso_dam_hub_prices): nothing loaded"), `dm_test_battery_dispatch` failed (test 178, waiting on its ruling, put back as committed). `dm_test_replication` passed: gate b's replication files hold.
- **`dm_commit` refused** at 18:34 by the push guard: "2 failing tests: test_session5074.Datacenter.test_the_hourly_window_as_the_do_file_counts_it, test_session5502.TheExpectedValues.test_each_quoted_figure_is_the_page_s". The commit `a7a17d360` (253 files) went to `wip/red-dm-2026-11-14`; main untouched.
- **Why:** the datacenter refresh moved its figures. The carbon file holds 10,160 hourly rows, but prices and intensity are both held in only 10,094 of them (the page's window was 10,151): the carbon tables run past the prices' last hour, since no daily commit has landed since 12 November. Test 5074 holds the two counts equal; test 5502 holds the signature pack's quoted figures (written 14 November) to `replication/datacenter/page_figures.json`, so any daily move refuses the commit.
- **Fault 3, fixed:** the replication group (`warehouse/run_data_machine.sh`, session 3206's rule: a refresh that moves a recorded figure is put back whole) did not run tests 5074 and 5502, which landed today, so the guard refused the whole commit, every other group's files with it. They join the group (5074's Datacenter and Analysis classes, 5502); test 3206 follows (3 passed; the three joined: 12 tests OK). Gate c started 18:41 UTC.
- **The daily re-run** dispatched at 18:36 UTC (`once=1`, HTTP 204) once the data machine let go of the lock.

## Decisions made without you

- **The fold sits in the news ingest,** which runs every day, not in the expired shadow scorer.
- **The re-run waited for the data machine's run** rather than taking the lock from it.
- **The new tests joined the data machine's group** rather than being changed: their checks stand, and a refresh they refuse is put back instead of blocking the other groups.

## For Samuel's ruling

- **The signature pack's datacenter figures and the daily refresh.** Test 5502 holds the pack's quoted datacenter figures (written 14 November) to files the data machine refreshes daily (the datacenter is the one daily tool, test 5074's `DAILY`). From now on the datacenter group will be put back every day its figures move, so the datacenter's files stay as of 14 November on main until the pack follows them or test 5502 reads the datacenter's figures as of their day. Default: put back daily (the pack's figures stand); window P1 or you to choose.
