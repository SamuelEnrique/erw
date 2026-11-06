# Session 3161 report: four old derived tables' publishers

6 November 2026, about 14:21 to 14:26 UTC, on lab-desktop (the data machine, its first window), chain 181, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **The fault** (chain 177's session 3109): on this machine's full warehouse, `package/tests/test_erw.py` fails two tests. `test_derived_tables_flag_license_and_inputs` fails on all four tables below; `test_cite_names_the_iso_the_table_and_the_commit` fails on two of them. Their builders registered the publisher "Energy Research Warehouse (ERW)" without ", derived".
- **The fix, as session 2884's** (commit `cc41ef566` on `wip/c181-data`):
  - each builder's `update_sources` publisher: `warehouse/derived/demand_weather.py`, `eia_annual_crosscheck.py`, `queue_statistics.py` and `stress_days.py`;
  - the four `sources.csv` rows;
  - `site/data/table_citations.json`, rebuilt by `package/tools/build_tables.py`. Four citations now begin "Energy Research Warehouse (ERW), derived."; the download route writes that in its header.
  - No table was rebuilt: the rows' `source` ids do not change.
- **Test `tests/test_session3161.py`** (3 tests):
  - every `erw:` source of a table that `coverage.csv` calls derived names that publisher. Only these four did not; `storage_daily_cycle`'s "..., derived from California ISO" already does.
  - the four builders and rows say so;
  - the site's citations follow.
- **Checked:**
  - The tests of sessions 3161, 126, 152, 323, 1001, 1008 and 1009: 80 passed, 3 skipped.
  - `build_tables.py --check` passes; `release_v1.py --check` shows 0 differences.
  - With the branch's package and records over the four tables' files, all 67 derived tables cite with the phrase. The two package tests that failed now pass. A third failed only because `ercot_rtm_hub_prices` was not in the worktree.
- **The gate:** passed on `3600395a8` (wip/c181-data with origin/main merged at 14:26 UTC), run from the main checkout. Freeze none; db probe passed; the build lock waited 521 s for the second window's build. The suite ran 7,897 tests, OK (358 skipped); npm ci, the build and serve passed. check-values: 7,815 of 7,815 values match; its 2 failures are main's known floors (`/deals`, `/learn/problems/know-your-grid`; `cv_diff.py`: 0 new). The three checks the gate skips after that were run by hand on the kept build under the build lock (`runs/c153/handcheck.sh`, 15:12 to 15:17 UTC): check-routes (225 pages in review asked as a visitor, 0 failed), check-cross-checks (92 passed), check-csp (97 pages, 0 violations). A first try from the branch's worktree stopped at db_probe, which needs the main checkout's `.env`.

## Decisions made without you

- **The site's citations rebuilt with the fix.** They are the package's own words for these four tables. They are not a page's figure, and every page is in review.
- **The live registry is not loaded by hand**: the daily run's loader carries the four rows.

## For Samuel's ruling

- None.
