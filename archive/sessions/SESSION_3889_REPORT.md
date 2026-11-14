# Session 3889 report: the daily run of 13 November, its three faults fixed at their causes, and the board

Energy Research Warehouse (ERW). Chain 227, data machine (lab-desktop), 13 November 2026 14:00 to 17:45 UTC (session 3888's carried step, the daily run, read with session 3889's, the board). Opus 5.5. Model spend USD 0. Requests: GitHub's API 22 (under 30), among them the two runs' artifacts and one job log; Supabase's `erw_health` read over `SUPABASE_DB_URL`.

## The daily run of 13 November (run 43438591932)

- Dispatched at 14:00:03 UTC by pg_cron; the workflow ended at about 17:20 with success. `merge tests` ok (they had failed every run from 7 to 12 November), `nyiso` ok, `daily run` ok at 16:45.
- Skipped, each with its reason: `eia_series` and `ercot_storage_dam` (the publisher did not answer within the 15-minute budget), `ercot_as_prices` (ruling 2: no request to ERCOT's disallowed paths), `carb_lcfs` (CARB's newest week is 60 days old).
- **Three faults**, each of this repository's code, each fixed below with its test:
  1. `board_tests` failed at 15:20 (the board put back as committed, as on 12 November);
  2. **the daily commit was refused** by the push guard at 16:57, and the health summary's commit at 17:15, both for `test_session3703.TheNetwork.test_every_network_figure_agrees_with_the_pages_code`;
  3. `package tests` failed at 17:04: `test_fetch_types_and_provenance[datacenter_tracker_rollups]`.
- The day's metadata, docs and digests did not reach main (the commit was refused). The next run recomputes them.

## 1. The board (3889's step)

- **Read, not guessed:** the run's artifact (`daily-prices-log`: `runs/daily_board_tests.out`, `runs/daily_board.out`) for 12 and 13 November. Both days fail the same way: `22.2287 != 22.4387` in test 1118 (the newest spark spread against the hub less 7 x the gas), and test 1139's spread rows.
- **The cause:** `page_keep.py` takes or keeps each board row alone. On the runner ERCOT's histories are shorter, so it kept `ercot-hb-hubavg-da`, `-spark` and `-heat` as they were (78 points against 2,867), but took Henry Hub's row from the new build. A spark spread takes the day's gas price, else the newest trading day's up to 4 days back, so a new Henry Hub day changes spread values already held: the kept spread was no longer its inputs (0.21 = 7 x 0.03 USD per MMBtu).
- **The fix** (`warehouse/derived/page_keep.py`, `BOARD_TOGETHER`): Henry Hub's row and every spark spread and implied heat rate are one set. When one of them with a value is kept as it was, all are kept, except a row the new build blanks on purpose (a pause is still taken). The rows that combine same-day values only (hub spreads, peak less off-peak, day-ahead less real time, the cracks) agree with their inputs on every day both hold, and are left to the old rule. On the runner the gas row and the spreads now wait for the data machine's run, which holds every history and takes them whole; until now the whole runner board was put back every day.
- Test 3889 (`TheSetIsOneBuild`, 7 tests); tests of `page_keep` and the board (204 passed, 23 skipped; 284, 478, 884: 14 passed). The price board's method says so. **Landed at `989e2c927`.**

## 2. The daily commit refused: the Grid tool's replication

- **Read** from the refresh job's log (GitHub's API serves it with the repository's token): the page's own code drew six figures the replication did not, `series|eia930_all_demand|eia930:<BA>|demand_mw|2026-11-11T23:00:00Z` for ERCO, CISO, PJM, MISO, NYIS and ISNE.
- **The cause:** `replication/grid/replicate.py`'s `network()` never drew the demand figure the page's `demandAt` (`site/lib/gridKeys.ts`) draws when the snapshot holds a grid's demand at the hour shown. The committed snapshot's demand hours are older than its hour shown, so the test passed until the daily run's snapshot of 13 November held demand at that hour.
- **The fix:** `network()` draws each grid's demand in the hour shown as `demandAt` does, keyed `netsnap|` when the hourly refresh read it, else as its row of `eia930_all_demand`. Test 3889 (`TheNetworksDemand`) gives the committed snapshot demand at its hour shown both ways and runs the page's own code (node) against the replication: it fails without the fix and passes with it. Test 3703 passes.
- The hourly network job skipped while the daily run ran (15:05 to 17:05); its next snapshot could have met the same refusal.

## 3. The package tests: the rollups' provenance

- **The cause:** `datacenter_tracker_rollups`' header says "derived from datacenter_projects" inside its Shape line but has no `Derived from:` line, which `build_coverage.py` reads for coverage's `derived` column. So coverage read it as derived "no", its header names no run log, and the package's provenance test refused it. The test was reached for the first time on 13 November: until chain 221's fix, the package tests stopped earlier on this table's cite test.
- **The fix:** the builder writes `Derived from: datacenter_projects`, as every other derived builder does. Coverage then recomputes the table's license from its input: both internal, so the build passes. Test 3889 (`TheRollupsAreDerived`) runs the builder into a temporary folder and reads its header with coverage's own parser. Tests 2236 and 2247: 15 passed.
- Fixes 2 and 3 go through a second gate (`task/c227-data2`).

## The health summary's "Stale on main" line

- The newest summary on main is of 11 November (its line: "daily prices, 6.6 days ... hourly network, 4.8 hours"). The summaries of 12 and 13 November were refused with the daily commits; the next run writes them once fix 2 is on main.

## Decisions made without you

- **A kept spread keeps Henry Hub and every other spread,** not the day-ahead rows. Keeping the day-ahead rows too would freeze every hub's prices on the runner for the gas row's sake.
- **Fixes 2 and 3 landed in a second gate.** The first gate had started before the run ended and its branch could not take commits while it ran.

## For Samuel's ruling

- **check-values on a published Digest after EIA revises a figure:** the Digest of 12 November printed US48 demand at 2026-11-11 23:00 UTC as 488,034 MW; EIA's revision, loaded at 16:01, reads 488,341. check-values compares a past issue with today's table, so every revision fails it (the gate of `wip/w2-land-e` at 16:43 met the same line). Default: counted as main's known failure, as `/digest/2026-10-21|digest_fuel` is.
- **`/policy`'s floor:** since the three policy tables were held for a license (window 3's session 4102), the page draws 0 checked numbers with 1 held, against its floor of 10. Default: counted as main's known failure. Window 3 or the landing desk owns the floor.
