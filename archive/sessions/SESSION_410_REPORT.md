# Session 410 report: the /data catalogue and coverage agree

21 October 2026, about 04:00 to 05:30 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-410` on `wip/410-s` (from `wip/381-382-land` at `61c4c309`). Chain `queue/done/015-day-20-october-code-pm.md`, session 410. Model spend USD 0; no pull from any publisher; no warehouse data written.

## Read these first

- **Where /data's list comes from.** `site/app/data/page.tsx` reads the live catalogue (`lib/data.ts`, `catalogue()`), which `warehouse/supabase/load.py` writes from `warehouse/metadata/coverage.csv` (live_set.yaml, `catalogue`) less the tables under `catalogue_hold`, each with `in_live_set` yes, no or review; the site keeps the rows whose license is public and whose `in_live_set` is not review. The page already showed each table's license (or "license needed" from 21 October, by `lib/license.ts`), first and last row, row count, source report, tier and download (Download CSV, "Held: license needed" for a held table, or the Redivis link with "version 1 is pending release"). The one field missing was the refresh.
- **Built**: a "Refreshed (UTC)" column on /data, the day of coverage.csv's `last_run` (the time in the hover; "not recorded" where coverage has none); two registry lines in `warehouse/metadata/sources.csv`; `tests/test_session410.py`, which reads the page's source of tables statically, as load.py and lib/data.ts read coverage.csv, and fails when the page, coverage.csv, sources.csv, the license holds or the Redivis drafts disagree (12 tests).
- **By coverage.csv as it stands, /data lists 99 of the 179 public tables**: 30 of them held for a license ("license needed", not downloadable), 42 with Download CSV, 27 with the Redivis link. The other 80 public tables are held off the page by the two hold lists of `warehouse/supabase/live_set.yaml` (48 under `catalogue_hold`, session 85; 32 loaded for pages in review under `review_hold`, session 102). Both are a person's lists, so nothing was changed there: under "For Samuel's ruling".
- **No Redivis version is released** (v1 waits for the owner's click, `docs/redivis/release-v1.md`). Every listed table has a draft in the public dataset `energy_research_warehouse` (`warehouse/metadata/redivis_uploads.csv`); the page's existing place for it (the Redivis link and its title, and the note under the table) already says version 1 is pending release. No address per table was added.

## What to review

- The commit `e18cfa90` on `wip/410-s`: `site/app/data/page.tsx`, `warehouse/metadata/sources.csv`, `tests/test_session410.py`.
- The shots are **not made**: three builds failed on Supabase statement timeouts (see "To finish"). `docs/brand/review-410/shot-410.mjs` makes them (`01-data-top`, `02-data-coverage` at 1280 and 390, `03-data-refreshed` at 390) with `data-410.json`, the rows the page drew.
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
| `npm run build`, third and last try (05:00) | 1 | the same (seven timeouts, the home page); TypeScript passed each time. No server was started; the shots wait under "To finish" |
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

## To finish

On a build that passes (the database answering), from the worktree or the merged copy, under the build mutex:

```
cd site && npm run build > ../runs/chain_oct21/s410/build4.out 2>&1; echo "exit=$?"
npx next start -p 3410            # in the background
node ../docs/brand/review-410/shot-410.mjs http://localhost:3410 > ../runs/chain_oct21/s410/shots.out 2>&1; echo "exit=$?"
```

Then look at each PNG in `docs/brand/review-410/`, check that `data-410.json` lists the tables `tests/test_session410.py`'s `page_tables()` names (99 by coverage.csv tonight, unless the live catalogue was loaded from another coverage), that the 30 held tables read "license needed" and "Held: license needed", and that the Refreshed column shows a day for every table but `datacenter_queue_positions` and `lbnl_interconnection_queue`; commit the shots and the JSON, and stop the process on port 3410.

## Files

- `site/app/data/page.tsx` (the Refreshed column and its note); `warehouse/metadata/sources.csv` (two rows); `tests/test_session410.py` (new).
- `docs/brand/review-410/shot-410.mjs` (the shots and `data-410.json` wait).
- This report.

## Finished on the combined branch (21 October)

On `wip/015-finish` (the worktree `C:\Users\lossa\Documents\erw-finish`, cut from `wip/015-land`: sessions 401 to 410, 413 and 414 merged on main), 21 October 2026, 09:17 to 09:42 UTC under the build mutex: `duty.py beat` exit 0, `npm ci` exit 0, **one build, `npm run build` exit 0** (no statement timeout in its log), `npx next start -p 3415`. Every output is under `runs/chain_oct21/finish/` (outside git). Common to every section below: the **full `check-values.mjs`** (no restriction) exit 1: **6,359 of 6,359 values match Supabase**; 10 pages below their floors, exactly session 408's list with its counts (`/deals` 0 of 10, `/map` 0 of 1, `/events` 2 of 9, `/events/uri-2021` 9 of 10, `/events/covid-2020` 7 of 10, `/events/caiso-heat-2020`, `/events/caiso-heat-2022` and `/events/east-heat-2025` 0 of 10, `/learn/bill` 5 of 10, `/research/card/gas_sets_price` 4 of 6), every one license-held, expected; no other failure. **`check-routes.mjs`** exit 0 (1 live page and 223 in review asked as a visitor, 0 failed). The **whole suite** (`ERW_LOCK_EXEMPT=1 python -m unittest discover -s tests`, 09:43 to 09:49 UTC, the server stopped) exit 1: 4,911 tests, 1 failure, `test_session156` (the ask fixtures, the chain's known failure tonight), 254 skipped; the ten sessions' own modules (402 to 410, 414) exit 0, 107 tests. The server was stopped and the mutex released at 09:42 UTC.

- **The shots:** `node docs/brand/review-410/shot-410.mjs http://localhost:3415` exit 0: 99 rows at both widths, the aside "99 public tables", "live set unreadable: false"; the five PNGs and `data-410.json` committed (commit `1b770a65`).
- **The comparison:** `data-410.json` lists exactly the 99 tables of `test_session410.page_tables()` (none missing, none extra); 30 rows read "license needed" with "Held: license needed" in the Download column; every Refreshed cell holds a day but `datacenter_queue_positions` and `lbnl_interconnection_queue`, as the report expected.
- **Looked at each PNG:** `01-data-top` at 1280 and 390 is right (the heading, the coverage table's first rows; at 390 the table scrolls inside its frame). `02-data-coverage` at both widths and `03-data-refreshed_390` show a beige empty band over the upper part of the image and, in `03`, a header row that reads "Table ... Tier" over the date column, not in step with the scrolled body. Whether that is the page (a sticky header inside the overflow box) or the capture (the script clips at y 0 with `captureBeyondViewport: false` after scrolling) was not settled; listed, not fixed.
- `tests.test_session410`: exit 0 within the ten sessions' modules.
