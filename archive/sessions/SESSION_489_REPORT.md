# Session 489 report: the tables of sessions 484 to 496 and 507, written under the data lock

21 October 2026, from 18:29 UTC, on lab-desktop (the data machine), the sixth session of `queue/done/022-evening-21-october-sources.md`, run once the daily run released the data lock. Model spend USD 0.

## Read these first

- **Ten connectors' tables written into `warehouse/output`**, all under the data lock (taken 18:29:44, released 18:36), by `runs/s489_write.sh`. Every connector reused its raw files where it held them.

  | Table | Rows | What |
  |---|---|---|
  | `ferc714_area_demand_2023` to `_2025` | 779,627; 781,703; 770,886 | 89 respondents a year (session 484) |
  | `eia861_utility_sales` | 2015 to 2025, 34,207 to 55,427 a year | 1,521 to 3,179 utilities (sessions 485 and 495) |
  | `egrid_power_plants` | 12,612 plants | eGRID2023, 1,303,569 MW (session 486) |
  | `nlr_atb_electricity_costs` | 95,000 | ATB 2025 v1.0.0, 547 entities, 20 technologies (session 487) |
  | `eia_aeo_electricity` | 34,034 | AEO2026, 11 cases (session 490) |
  | `eia_steo_forecasts` | 5,088 | the STEO of 6 October 2026, 53 series (session 491) |
  | `epa_ghgrp_power_co2` | 17,035 | 1,443 facilities, 2010 to 2023 (session 492) |
  | `boem_renewable_leases` | 52 | leases and grants (session 493) |
  | `uswtdb_wind_turbines` | 77,839 | 159,587 MW (session 496) |
  | `eia_seds_state_energy` | 23,660 | 676 series by state, 1990 to 2024 (session 507) |

- **The gates**: the validator exited 0. `archive.py write` exited 0: 12 tables archived, 3,030,651 rows. `build_coverage.py --only` failed first (exit 1): `eia_seds_state_energy` had no sector rule. Session 507's rule was only on the `wip/` branch. The coverage was run again with the branch's `build_coverage.py`, copied in for that one run and then restored: it exited 0.
- **The metadata moved to the branch**: `coverage.csv`, `docs/coverage.md`, `archive_manifest.csv` and `sources.csv` were copied as a patch of added lines only. `licenses.py tables --headers` (the data machine's `warehouse/output`), `write` and `check` were run in the worktree: 224 tables, 0 problems. The main checkout was put back to main's files.
- **No table of this chain is in the live set.** Nothing was loaded and nothing was uploaded to Redivis.

## The landing (from 18:58 UTC), and what it needed

The whole suite, run after merging origin/main, failed 19 tests. Ten failures came from main and nine from this chain.

- **Main's ten: the daily recompute of the Research cards.**
  - Session 361's `dm_findings_recompute` committed its first run with the data machine's page files (`c8aa37ff`, 21 October, 18:28 UTC). The tests then failed on that commit, and passed on the commit before it.
  - It moved numbers that the tests of sessions 173, 174, 182, 274 and 381 hold to the cards as built, for example `peak_hour_moved`'s percentages, now over 365 days and no longer 364. Every `task/` branch would have failed its checks.
  - **Put back**: `site/data/findings` and `site/public/findings` are back as they were before that commit. `warehouse/metadata/findings_recompute.csv` keeps the run's record.
  - **The daily run now tests the cards** (`warehouse/run_data_machine.sh`): after the recompute, the step `dm_test_findings` runs those five tests. A failure puts the cards back as committed, the same way a page file whose own test fails is put back. Which gives way, the tests or the recompute, is yours to rule.
  - **Session 167's map totals**: `map.json` of the same commit sums one kind to 762,785 MW on the page and 762,786 MW in the test. A sum in another order rounds the other way. The test now holds the counts exactly and the MW within 1.
- **This chain's nine: the new public tables.** In coverage, the nine public tables entered `/data`'s catalogue and the Redivis v1 package, and none has a Redivis upload (sessions 410 and 275).
  - They are held from both: `catalogue_hold` in `live_set.yaml`, and `STORAGE_HELD` in `release_v1.py`, in the same way as `node_basis_daily`.
  - The package's `tables.csv` and `variables.csv` gained their rows (9 and 153), and its README names the 11 held tables.
  - Only those rows were added. A full rewrite from this machine's file headers would have changed other tables' descriptions.
- **Session numbers**: the code machine's chain 023 holds sessions 497 to 506, so this chain's 497, 498 and 499 were renumbered 507, 508 and 509 (their reports, the SEDS test and its comments). The output header `eia_seds_state_energy.csv` on the data machine still says session 497 until its next write.
- Tests: `tests/test_session489.py` (5). The whole suite then passed: 5,204 tests, 0 failures.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 33 | AEO 24 (of 60), STEO 4, SEDS 5 (of 20) |
| energy.usgs.gov | 8 of 30 | USWTDB's pages |
| others | 0 | raw files reused (PUDL, EIA-861, eGRID, ATB, GHGRP, BOEM) |

## Decisions made without you

1. Coverage was run with the branch's sector rules, not main's, rather than landing the rule first and writing a second time.
2. The Research cards were put back, and tested after each recompute, rather than changing five sessions' tests to today's numbers. No page's default figure moves.
3. The nine new public tables were held from `/data` and Redivis v1 rather than listed without a Redivis copy.

## For Samuel's ruling

- The daily recompute (session 361) or the cards' pinned tests (sessions 173, 174, 182, 274 and 381): which gives way. Until you rule, the recompute runs every day and its cards are put back whenever those tests fail.

## Files

- Changed: `docs/coverage.md`, `docs/licenses.md`, `warehouse/metadata/{coverage,archive_manifest,sources,license_tables}.csv`, `warehouse/run_data_machine.sh`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/redivis/release-v1/`, `tests/test_session167.py`, `site/data/findings/`, `site/public/findings/` (put back). New: this report, `tests/test_session489.py`. `runs/s489_write.sh` stays on the data machine (`runs/` is not in git).
