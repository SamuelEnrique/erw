# Session 72 report: what session 71 left, the storage build-out, sync against the cloud, check-values that cannot hang

Energy Research Warehouse (ERW), session 72, first of the overnight chain (72 to 75), on the portable laptop, 2026-10-03 from 07:17 to about 09:55 UTC, unattended. **Model spend: USD 0.00** (the cap was USD 0). No pull, no model call, no force push. Branch `wip/072-finish` on GitHub.

**Tonight's overriding rule (Samuel's): nothing goes live.** Nothing was pushed to main or to a `task/` branch, nothing merged, nothing deployed. No Supabase table that a live page reads was loaded or overwritten. The steps that would have merged or changed the live site are below, as commands.

## To finish

Run these in order, in the main folder (`C:\Users\samen\Documents\erw`), only after the reviewer has seen tonight's site. Each `push` to a `task/` branch runs `.github/workflows/code-branch.yml`, which merges into main and deploys when the checks pass.

```bash
# 1. Session 72 (and with it session 69's storage build-out and session 71's report): bring the branch up to date, then merge
git checkout wip/072-finish
git fetch origin
git merge origin/main                      # the daily run's commits since 07:17 UTC; never a rebase, never a force
git push origin wip/072-finish:task/072-finish

# 2. The storage build-out in Supabase's live set. Not done tonight: load.py --only also writes the table's row into
#    Supabase's catalogue, and the live home page counts the catalogue's public tables and rows (89 tables tonight), so
#    loading would have changed a live number. Do it after step 1 has merged (the page is in review either way).
python warehouse/lock.py acquire --task "storage_buildout_monthly into the live set" --minutes 20; echo "exit=$?"
python warehouse/supabase/load.py --only '^storage_buildout_monthly$'; echo "exit=$?"
python warehouse/lock.py release

# 3. Battery game version 4 (session 70's "To finish", steps 4 and 6; steps 1 to 3 and 5 are done, below)
cd C:/Users/samen/Documents/erw-game
git fetch origin
git merge origin/main                      # after step 1 has merged; the branch already holds main as of 07:17 UTC
git push origin wip/066-battery-game-v4:task/066-battery-game-v4
cd site
node scripts/check-routes.mjs https://erw-flame.vercel.app
node scripts/check-lights.mjs https://erw-flame.vercel.app
node scripts/play-battery.mjs https://erw-flame.vercel.app   # posts v4 test plays (marked as ERW checks); needs the unlock link to work while /play/battery is in review

# 4. Session 69's own step 13, once step 1 has merged
git push origin --delete wip/069-storage-buildout
```

## In plain words

- **Session 71's report** is on this branch (`6559008`, cherry-picked from the local `task/071-report`). It reaches main with step 1.
- **The game's migration is applied, and only it.** `warehouse/supabase/apply.py --only 019_game_v4.sql` now exists and is tested. Migration 019 is applied (exit 0); 014 is not edited. Both preset checks now accept v4 presets, and the 44 scores and 56 plays held are unchanged. The game is **not merged** (your ruling).
- **The game's rooftop solar shapes are built:** a shape on 7 of 7 levels, committed and pushed to `wip/066-battery-game-v4` (`fcdffe6`); the game's 42 tests pass. Two things to look at:
  - Two ERCOT days peak above nameplate: 1.0429 of nameplate on 2023-08-10, 1.0318 on 2026-08-29. EIA-930 solar output over EIA-860M operating MW.
  - The two California levels (2026-04-27, 2026-07-24) fall after 2025-12-16, when EIA's CAISO series changed (session 73). Their solar series did not visibly break, but they rest on that series.
- **The footer's "Data and methods"** is greyed with no label while `/data` is in review (your ruling), and the browser test checks it.
- **The unlock link still answers 404** on production (07:26 UTC).
- **The storage build-out page is finished up to its merge.** It is built in `warehouse/output` (21,229 rows), valid, in coverage, the archive and the Redivis draft (`erw_headers` 1,741 to 1,753 lines). It is in the menu and `review` in the release gate. It is checked against its fixture (7,313 checks pass). It is not in Supabase (step 2) and not merged (step 1).
- **Sync now compares with the cloud.** `scripts/sync.py` compares each local table with Redivis's own copy, by row count and newest timestamp, not with `coverage.csv`. It restored this laptop's 11 tables that were behind. It never overwrites one that is ahead, and says so.
  - `eia930_all_interchange`: 127,560 rows to 2026-09-28 23:00 UTC before, **135,456 rows to 2026-09-29 23:00 after**.
  - `news_scores_shadow`: 2,375 rows to 2026-09-28 before, **3,595 rows to 2026-10-01 after**.
- **check-values cannot hang and does not flake on the latest prices.**
  - It has a hard timeout on every request (60 s) and on the whole run (15 minutes).
  - A latest-price key now carries the interval the page shows. The same interval in Supabase must match exactly. A newer interval in Supabase is reported as "superseded" and passes only within 45 minutes. No key is dropped.
  - Tested both ways on a local build: 6,537 of 6,537 match. Run just after a refresh: 6,498 match and the 39 latest prices are superseded, 30 minutes behind; exit 0.
- **Found and fixed: this laptop cannot use pyarrow's dataset module.** A Windows Application Control policy blocks one of its DLLs (`_json`). Every Redivis read that came back through pyarrow failed, and one failure could have done damage. `upload.py`'s header merge took a failed read of `erw_headers` for "the draft has none". It would then have replaced every table's provenance header lines in the Redivis draft with the uploaded table's alone. It did not happen tonight: the first failed upload stopped before that step. It is fixed: only a table Redivis says is absent starts afresh, and a read error writes nothing. Sync and upload now read Redivis without pyarrow, and tests cover both.

## Part A: what session 71 left

| Item | State |
|---|---|
| Session 71's report | on this branch (`6559008`) |
| `apply.py --only` | added: a file name or a number (`--only 019`); applies that migration only, and not the settings the full run writes; a name that matches none or several applies nothing (exit 2). Tests: `tests/test_session72.py` |
| Migration 019 | carried from the game branch unchanged (`633c3bb`, so the game's merge finds the same file) and applied at about 07:40 UTC under the lock. Read back afterwards: both checks hold `(-v3\|(-[a-z]+)*-v4)?`; `game_scores` 44 rows, `game_plays` 56, as before |
| Session 70 step 1 (lock) | taken for 019 and step 3, released |
| Session 70 step 3 (solar shapes) | dry run, then the builder: 7 of 7 levels have a shape; `tests.test_session70 test_session66 test_session38 test_session56 test_session50`: 42 tests, OK (3 skipped: they look for price history in the game worktree's own `warehouse/output`); committed `fcdffe6`, pushed to `wip/066-battery-game-v4` |
| Session 70 step 4 (the merge) | **not run** (your ruling); "To finish", step 3 |
| Session 70 step 6 (live checks) | **not run**: the game is not deployed; "To finish", step 3 |
| Footer | greyed, no label, not a link (`bfdd43f`); browser test assertion added |
| Unlock link (Part E) | 404 at 07:26 UTC |

The shapes' peaks and troughs, from the dry run:

| Level | BA | Highest hour, share of nameplate | Lowest | Nameplate MW |
|---|---|---|---|---|
| 2021-02-15 (Uri) | ERCO | 0.5525 | 0.0000 | 5,120.6 |
| 2023-08-10 (heat) | ERCO | **1.0429** | 0.0000 | 12,325.7 |
| 2026-04-26 (calm) | ERCO | 0.7773 | 0.0000 | 31,734.3 |
| 2026-08-29 (solar) | ERCO | **1.0318** | 0.0000 | 32,759.8 |
| 2025-01-05 (negative) | ERCO | 0.3503 | 0.0000 | 22,837.9 |
| 2026-04-27 (caiso-solar-noon) | CISO | 0.4696 | -0.0025 | 24,968.1 |
| 2026-07-24 (caiso-duck) | CISO | 0.7486 | -0.0005 | 25,798.6 |

Output above nameplate is not impossible: plants built with more panels than inverter capacity, or plants operating before EIA-860M lists them. But it is flagged, not explained. The small negative California troughs are night-time station load as EIA reports it.

## Part B: the storage build-out page (session 69's "To finish")

| Step | Result |
|---|---|
| 1. The branch up to date with main | `wip/069-storage-buildout` merged with main (`ee9b2db`, no conflict), pushed; then merged into this branch (`411f3e8`) |
| 2. The swap | the page now uses session 67's shared pieces (`ToolPage`, `ToolHeader`, `InputPanel`, `HeadlineRow`/`HeadlineNumber`, `ToolSection`, `ChartFrame` with its legend, `Fold`, `SourceLine`, `Num`); the two server-drawn charts and two tables stay in `parts.tsx`; the five colors are tokens in `app/tokens.css` (`--color-duration-1` to `4`, `--color-not-reported`, `--color-surface`) |
| 3. The four edits | `build_coverage.py` (sector and grids), `live_set.yaml`, `run_daily.sh` (`run_other storage_buildout`), `llms.txt`; the chat spec re-exported (no model call) and the page added to `docs/tools.md`, which two tests required |
| 4. Lock and sync | the lock taken; sync was Part C |
| 5. The table | `storage_buildout_monthly`: **21,229 rows**, 140 months to 2026-08, 1,137 operating battery units, 8 retired, 8,313 solar, 482 planned; 252 units (15,567.5 MW) outside the seven ISOs |
| 6. Validator, coverage | every table in `warehouse/output` validated: **108 of 108 pass**. Run in four parallel parts because one pass over 4.8 GB passes the 15-minute cap; the reports were merged and coverage reused them. Coverage: 108 tables; the new one derived, public, power, 21,229 rows |
| 7. Archive | 21,229 rows |
| 8. Redivis draft | `storage_buildout_monthly` 21,229 rows (Redivis's count equals the file's); `erw_headers` 1,753 lines; `--check-license` ok (14 internal tables, 0 in the public dataset). Nothing released |
| 9. Supabase live set | **not loaded** ("To finish", step 2): it would add a row to the catalogue the live home page counts |
| 10. Site entries | the menu (Grid, after Storage), `"/storage/buildout": "review"`. Without its own line it would have taken `/storage`'s `live` status. Also the check-routes and check-values pages |
| 11. Tests | below |
| 12. The merge | **not run** ("To finish", step 1) |

## Part C: sync compares with the cloud

`scripts/sync.py` now reads, for every table `coverage.csv` lists, Redivis's own row count (the table's metadata) and newest timestamp (Redivis's statistics of its `ts_utc`, `event_date` or `date` variable). It compares them with the local file's rows and newest timestamp:

| Local against Redivis | What sync does |
|---|---|
| missing here | restores it |
| behind (an older newest timestamp, or the same and fewer rows) | restores it |
| ahead (newer, or the same and more rows) | **never overwrites it**: "AHEAD, not overwritten ... (upload it, or it is lost with this machine)" |
| diverged (newer by one measure, older by the other) | reports it; replaced only with `--refresh` |
| a table Redivis cannot be asked about | left out, reported, and the run exits 1: an unanswered question is never read as "absent" |

Restores go through Redivis's CSV export, re-typed from Redivis's variable types, and are written by the same `as_erw_text` as before. A restored file was checked against the old format: same timestamps, the validator passes.

**This laptop, before and after** (`sync.py --no-git`, exit 0): 92 tables current, **11 behind, all restored, 0 failed**, 0 ahead, 2 diverged, 2 not on Redivis. The 11 restored files pass the validator.

| Table | Before | After (Redivis's) |
|---|---|---|
| `eia930_all_interchange` | 127,560 rows to 2026-09-28 23:00 | 135,456 rows to 2026-09-29 23:00 |
| `news_scores_shadow` | 2,375 rows to 2026-09-28 23:26 | 3,595 rows to 2026-10-01 23:32 |
| `eia_crude_first_purchase_prices` | 858 to 2026-06 | 860 to 2026-07 |
| `eia_crude_imports_by_country` | 22,615 to 2026-06 | 22,633 to 2026-07 |
| `eia_lng_exports_monthly` | 1,066 to 2026-06 | 1,083 to 2026-07 |
| `eia_padd_crude_pipeline_flows` | 4,550 to 2026-06 | 4,558 to 2026-07 |
| `eia_petroleum_stocks_weekly` | 16,799 to 2026-09-18 | 16,807 to 2026-09-25 |
| `eia_petroleum_trade_weekly` | 12,565 to 2026-09-18 | 12,572 to 2026-09-25 |
| `eia_product_spot_prices` | 71,908 to 2026-09-22 | 71,953 to 2026-09-29 |
| `eia_retail_fuel_prices` | 5,322 to 2026-09-21 | 5,325 to 2026-09-28 |
| `portwatch_chokepoint_transits` | 118,440 to 2026-09-20 | 118,734 to 2026-09-27 |

Left as they are, and needing a look:

- **`grid_network_links` diverged:** 26,160 rows to 2026-09-28 here, 26,136 rows to 2026-09-29 on Redivis.
- **`policy_reads_evidence` diverged, and looks wrong on Redivis:** 1,778 rows here, **7 rows** on Redivis. A draft table of 7 rows for a table of 1,778 suggests an upload that replaced it with a small slice. I did not touch it.
- **Not on Redivis at all:** `caiso_grid_emergencies` and `caiso_reliability_daily` (session 58's tables). They are here and in coverage, so the cloud has no copy.

## Part D: check-values

- Every request has a hard timeout (`CHECK_VALUES_REQUEST_S`, default 60 s) and the whole run one too (`CHECK_VALUES_TIMEOUT_MIN`, default 15). Past it the run fails loudly with exit 1. Session 71's third run hung for 70 minutes.
- The latest-price key is now `latest_prices|<entity>|<variable>|<ts_utc>`, on `/`, `/prices` and `/prices/<entity>`. Supabase's `latest_prices` holds one row per entity, the newest interval, and the earlier interval is held nowhere else in Supabase (checked: the `series` table has no rows for those 5-minute intervals). So:
  - the same interval in Supabase: the values must be equal;
  - a newer interval in Supabase: "superseded", reported on its own line and in the summary, and it passes only if the page is at most 45 minutes behind;
  - the page newer than Supabase, or more than 45 minutes behind: fails.
- Tested on a local build:
  - 07:51: 6,471 of 6,471, exit 0, 5 minutes.
  - 08:41: 6,537 of 6,537, exit 0.
  - 09:01, just after a refresh while the pages were still cached: 6,498 match, 39 latest prices superseded (30 minutes behind), exit 0.
- The exact comparison for every latest price, whatever the timing, would need Supabase to keep the last hour or so of intervals (a small new table the 15-minute job writes). That is a design change for you; not built.

## Tests and checks (local, on this branch's final build)

| Check | Result |
|---|---|
| `python -m unittest discover -s tests` | 354 tests, OK (2 skipped), exit 0. Two failed on the first run, both from the build-out: the page was missing from `docs/tools.md`, and the chat spec was stale after the `llms.txt` edit. Both fixed, both pass |
| `tests/test_session72.py` | 10 tests: `apply.py --only` (4), sync (3), the CSV restore's types (1), the header merge never clobbering (2); OK |
| Package tests (`pytest package/tests`) | 444 collected: **410 passed, 32 skipped, 0 failed; 2 did not finish** inside the 15-minute cap (`test_tier_column_cite_and_info` and the one after it, in the slowest group, which read the full local tables). Run in parts because the whole suite took 24 minutes in session 71 |
| `npx tsc --noEmit` | exit 0 |
| `npm run build` | exit 0 |
| `check-routes`, both passes | exit 0: pass 1, 77 of 77; pass 2, 14 live and 63 in review asked as a visitor, 0 failed |
| `check-values` | 6,537 of 6,537, exit 0 (and the superseded run above) |
| `test-battery-stack.mjs` | 67 assertions pass, the footer's included |
| `test-buildout.mjs` | 915 checks pass |
| `check-buildout.mjs` against the fixture | 7,313 checks pass, 3,530 numbers equal the fixture's rows, 16 pages (it now reads the page with the internal cookie, since the page is in review) |
| Validator, coverage, `--check-license` | exit 0 each |

## Errors and decisions

- **Decision: Supabase not loaded for the new table.** Explained in "To finish", step 2. Your rule allowed a brand-new table, but the loader also writes its catalogue row, which a live page counts.
- **Decision: session 69's page swap kept `next/link` for the page's own choice links** (another grid or measure, the same page). The gated link would render them greyed in the server's HTML while the page is in review. Every other link on the page goes through the gated link.
- **Decision: 019 is carried onto this branch**, so `--only 019` has a file to apply and the game's later merge finds an identical file.
- **Error, mine: the validator over every table was stopped by my 15-minute cap** (exit 124). Rerun in four parallel parts; all pass.
- **Error, mine: a first check-values run against a server built before the build-out page existed** answered 404 for it. It was not a result; the page was then built and checked.
- **Error, mine: the package test parts first ran with the wrong paths** (exit 4, nothing ran); rerun correctly.
- **Found: pyarrow is blocked on this laptop** (Application Control policy, `pyarrow._json`). `upload.py`'s `restore`, `reconcile` and `remove_migrated`, and the `erw` package's Redivis backend, still use pyarrow paths. They will fail here, loudly, until the policy allows the DLL or they are rewritten as sync and the upload were. The GitHub runner is not affected.
- **The data lock** was held about 07:39 to 07:47 (019 and the solar shapes) and 08:00 to 08:38 (the build-out's data steps).

## For Samuel

1. **"To finish"** above: the merge, the build-out's live-set load, the game's merge and live checks.
2. **`policy_reads_evidence` on Redivis holds 7 rows**; this laptop holds 1,778. One of them is wrong; I suspect the draft.
3. **`caiso_grid_emergencies` and `caiso_reliability_daily` are not on Redivis at all.**
4. **This laptop blocks pyarrow's dataset module.** If that is a Windows setting you can change (Smart App Control or an Application Control policy), the remaining Redivis paths work again; otherwise they need the same rewrite.
5. **The unlock link still answers 404** on production.
6. **Two ERCOT game days have solar above nameplate** (1.04 and 1.03); worth a look before the game ships.
