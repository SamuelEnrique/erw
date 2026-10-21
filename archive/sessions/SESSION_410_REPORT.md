# Session 410 report: the /data catalogue and coverage agree

21 October 2026, about 04:00 to 05:30 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-410` on `wip/410-s` (from `wip/381-382-land` at `61c4c309`). Chain `queue/done/015-day-20-october-code-pm.md`, session 410. Model spend USD 0; no pull from any publisher; no warehouse data written.

## Read these first

- **Where /data's list comes from.** `site/app/data/page.tsx` reads the live catalogue (`lib/data.ts`, `catalogue()`), which `warehouse/supabase/load.py` writes from `warehouse/metadata/coverage.csv` (live_set.yaml, `catalogue`) less the tables under `catalogue_hold`, each with `in_live_set` yes, no or review; the site keeps the rows whose license is public and whose `in_live_set` is not review. The page already showed each table's license (or "license needed" from 21 October, by `lib/license.ts`), first and last row, row count, source report, tier and download (Download CSV, "Held: license needed" for a held table, or the Redivis link with "version 1 is pending release"). The one field missing was the refresh.
- **Built**: a "Refreshed (UTC)" column on /data, the day of coverage.csv's `last_run` (the time in the hover; "not recorded" where coverage has none); two registry lines in `warehouse/metadata/sources.csv`; `tests/test_session410.py`, which reads the page's source of tables statically, as load.py and lib/data.ts read coverage.csv, and fails when the page, coverage.csv, sources.csv, the license holds or the Redivis drafts disagree (12 tests).
- **By coverage.csv as it stands, /data lists 99 of the 179 public tables**: 30 of them held for a license ("license needed", not downloadable), 42 with Download CSV, 27 with the Redivis link. The other 80 public tables are held off the page by the two hold lists of `warehouse/supabase/live_set.yaml` (48 under `catalogue_hold`, session 85; 32 loaded for pages in review under `review_hold`, session 102). Both are a person's lists, so nothing was changed there: under "For Samuel's ruling".
- **No Redivis version is released** (v1 waits for the owner's click, `docs/redivis/release-v1.md`). Every listed table has a draft in the public dataset `energy_research_warehouse` (`warehouse/metadata/redivis_uploads.csv`); the page's existing place for it (the Redivis link and its title, and the note under the table) already says version 1 is pending release. No address per table was added.

## What to review

- The commit `e18cfa90` on `wip/410-s`: `site/app/data/page.tsx`, `warehouse/metadata/sources.csv`, `tests/test_session410.py`.
- The shots: `docs/brand/review-410/` (`01-data-top`, `02-data-coverage` at 1280 and 390, `03-data-refreshed` at 390), made by `docs/brand/review-410/shot-410.mjs`, with `data-410.json`, the rows the page drew.
- After the landing, in the internal view: `/data#coverage`.

## What disagreed, and what was done

| Found | Tables | Done |
|---|---|---|
| In coverage.csv, public, on /data; no source in sources.csv names it | `datacenter_queue_positions` (its source report: `ercot:interconnection_queue;nyiso:interconnection_queue`) | **Fixed**: those two registry rows now name it. `scripts/licenses.py`'s derivation was run with the old and the new registry over the tables on the main copy: no table's publishers or reason change (the table is by hand there) |
| In coverage.csv, public; no source names it, but a source names a table `table_migrations.csv` records as migrated into it (session 29's consolidation) | `eia930_all_demand`, `eia930_all_generation`, `ercot_all_hub_prices_history`, `iso_dam_hub_prices`, `iso_rtm_hub_prices`, `iso_trader_daily` | Accepted by the test through the migration file; the registry was **not** edited: naming these tables would move `scripts/licenses.py` from "the grids its coverage row lists" and "EIA-930 (its name)" to the registry for them, which is the license record's path, not a missing line |
| In coverage.csv, internal (not on /data); no source names it | `news_scores_shadow` | Listed only; by hand in `scripts/licenses.py` |
| Named in sources.csv, not in coverage.csv | 54 old names of session 29's consolidation (in `table_migrations.csv`); `fred_daily_spot_prices`, `fred_imf_commodity_prices`, `fred_treasury_yields`, `price_board_stats` (in `retired_tables.csv`) | Accepted: the registry only grows (`merge_sources.py`, decision 13) |
| Named in sources.csv, accounted for nowhere | `curtailment_monthly` (`erw:curtailment_monthly`, seen 2026-09-27 only: session 18's name for what reached coverage as `iso_curtailment_monthly`) | Listed in the test with its reason; the registry never removes a name |
| Public in coverage.csv, named by an internal source | `news_index`, `energy_deals`, `datacenter_projects` (by design: links and the model's fields, no outlet text) and `nyiso_load_queue` (header "License: public, with a caution"; registry row `nyiso:load_queue` internal) | Named in the test; on the machine with the tables the test reads each header's "License: public". `nyiso_load_queue` is under `catalogue_hold` and also held for a license, so no visitor sees it; which of the two records governs is under "For Samuel's ruling" |
| Coverage gives no `last_run` | `datacenter_queue_positions`, `lbnl_interconnection_queue` | The page says "not recorded"; coverage.csv was not rebuilt (no count or time written by hand) |
| Coverage gives no `interval` | `ai_power_regions`, `noaa_isd_hourly` | Freq is blank, as before |
| `catalogue_hold` names a table not in coverage.csv | `price_board_stats` (retired 2026-10-13) | Left: a hold line with no effect |
| `site/data/license_status.json` against `license_status.csv` | every table | Agree (status, from day, publishers); the test keeps them so |

No row count or timestamp on /data is written by hand: every one is the catalogue's, which is coverage.csv's.

## Checks

Every gate redirected to a file under `runs/chain_oct21/s410/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `tests.test_session410` | 0 | 12 tests OK |
| `tests.test_session410` with sources.csv as before the fix | 1 | 2 failures (the table no source names; the two lines), as it should |
| `tests.test_session207`, `test_session215`, `test_session410` | 0 | 39 tests OK |
| `tests.test_merge_sources`, `test_session140_loadqueue` | 0 | 24 tests OK |
| `scripts/licenses.py` `build_tables`, registry before and after | | 212 tables, no difference |
| `duty.py beat` before each build | 0 | |
| `npm ci` in the worktree's `site/` | 0 | |
| `npm run build`, first try (04:17) | 1 | compiled and type-checked (TypeScript passed); the home page's required reads met Supabase statement timeouts (57014); the mutex was let go |
| `npm run build`, second try (04:42) | 1 | the same: seven statement timeouts, the home page's prerender failed |
| The whole suite (`ERW_LOCK_EXEMPT=1 ... -m unittest discover -s tests`) | 1 | 4,794 tests, 2 failures, 255 skipped: `test_session156` (the ask fixtures, expected tonight) and `test_session121.TheSite` ("alias-loader: nothing at @/content/docs.json": the suite started before the first build wrote `site/content/docs.json`) |
| `tests.test_session121` again, after the build wrote the file | 0 | 34 tests OK |

## Decisions made without you

1. **"Refresh" is the table's last run** (coverage.csv `last_run`), shown as its day with the full time in the hover: the registries hold no per-table schedule, and the cron lines of `.github/workflows/` are by job, not by table.
2. **The holds were not touched.** "Every public table listed" would need the 80 tables under `catalogue_hold` and `review_hold` in the live catalogue; both lists are a person's, by their own comments, so the page lists what the loader lets a visitor see, and the test reads the page's list the same way.
3. **The consolidated tables were not added to the registry**, as the table above says; the test accepts them through `table_migrations.csv`.
4. **No Redivis address per table**: none is released, and the page's one place for it already says version 1 is pending.
5. **The test reads `warehouse/supabase/load.py`'s own rules** (`live_rule`, `live_flag`, the `catalogue_hold` list) by loading the module under its own name (`erw_supabase_load_s410`), so a change to the loader's rules changes what the test expects.

## For Samuel's ruling

- **/data and the hold lists**: 80 public tables are not on /data (48 under `catalogue_hold`, 32 under `review_hold`). (a) List them on /data, from coverage.csv, marked held or in review, with no download; (b) keep the page to what the live catalogue holds; (c) take tables off `catalogue_hold` one by one.
- **`nyiso_load_queue`**: its header says "License: public, with a caution" and coverage.csv says public; the registry row `nyiso:load_queue` says internal; `license_status.csv` holds it ("license needed"). Which record governs, and should the registry row be made public or the header internal?
- **The consolidated tables in the registry**: name `iso_dam_hub_prices`, `iso_rtm_hub_prices`, `iso_trader_daily`, `eia930_all_demand`, `eia930_all_generation` and `ercot_all_hub_prices_history` in their sources' rows (it moves `scripts/licenses.py`'s reason for them to the registry), or keep the migration file as the link.

## Files

- `site/app/data/page.tsx` (the Refreshed column and its note); `warehouse/metadata/sources.csv` (two rows); `tests/test_session410.py` (new).
- `docs/brand/review-410/` (the shots, `shot-410.mjs`, `data-410.json`).
- This report.
