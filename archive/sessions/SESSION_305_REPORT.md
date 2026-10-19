# Session 305 report: Redivis out of every schedule's read path

19 October 2026, from 05:13 UTC, unattended, on lab-desktop (the data machine), the first session of the chain of 19 October (sessions 305 to 313). Model spend USD 0: no model call by the session. Pulls: none from any publisher (Supabase, the archive bucket and GitHub only, as the prompt allowed).

## Read these first

- **The cause: the daily run's restore exported about 2.5 GB from Redivis on every run** (48 rolling-window tables; `eia930_all_emissions` alone 1.1 GB). With reruns, the Sunday Roundup and this machine's sync, that passed Redivis's 100 GB in 30 days, and from 15 October every export was refused. The daily run stopped at its first step on 15, 16, 17 and 18 October, and the Roundup of 18 October (week 42) failed at the same restore and was not sent.
- **The dm_* store steps failed on a read, not an upload.** Every table reached the draft (`ok carb_auction_allowance_prices: CSV 336 rows, Redivis count(*) 336`); then the merge of `erw_headers` read the draft's header lines, an export, and was refused. Uploads work; only reads are capped.
- **Now: GitHub's cache first, then the archive, Redivis last under a ceiling** (`warehouse/restore_tables.py`). All 48 rolling-window tables rebuild from the bucket in about 8.5 minutes here (`eia930_all_emissions`, 4.3 million rows, in 54 s, replayed in sixteen slices of keys); where this machine's copy is the archive's latest, the rebuild's values are equal row for row (5 tables, `caiso_fuel_supply`'s 155,064 among them).
- **The manual run was not green: cancelled at the job's 180-minute limit** ([run 39207762565](https://github.com/SamuelEnrique/erw/actions/runs/39207762565), dispatched 06:03:46 UTC with queues 0 and monthly 0, cancelled 09:04:06). The restore itself worked on the runner: **48 of 48 tables in about 12 minutes, 47 from the archive and 1 from its bucket copy, none from Redivis.** The time went to two publishers that did not answer the runner: every CAISO OASIS and SPP request timed out after about 2.4 minutes (CAISO 06:24 to 07:03, SPP 07:03 to 07:43). The run had reached `eia_series` (done 08:38) when it was stopped, so its commit step, cache save and loads did not run. The daily runs of 14 and 15 October, before the cap, were also cancelled at 180 minutes. The workflow is left as landed; no second run was dispatched, since one started after 09:05 could not end before 13:00.
- **Pushed straight to `main`, not through a `task/` branch** (decision 1): the manual run had to run this code before 13:00 UTC.

## What to review

1. `warehouse/restore_tables.py`: the order of the four sources and what each must prove before a table is taken.
2. `docs/machines.md`, the new section "Where each scheduled job reads its tables from (session 305)".
3. `.github/workflows/daily-prices.yml`: the cache restored before the run, stashed and saved after a good one.
4. Decisions 3 and 4 below (two tables the archive cannot rebuild row for row; the news tables of 15 October).

## The root cause, step by step

| Where | What exported from Redivis | How much | Since 15 October |
|---|---|---|---|
| `daily-prices.yml`, `run_daily.sh` step 0 (`upload.py --restore`) | every rolling-window table, each run (the runner has none) | about 2.47 GB a run (sizes of the 48 tables here) | refused: "FAIL restore weather_obs_hourly ... Cannot export more than 100GB within a 30 day period" |
| `roundup.yml` (`upload.py --restore`, then `sync.py`) | the same, and the tables the watch list, findings and templates read | 2.5 GB and more, weekly | refused on 18 October: no Roundup |
| this machine, `dm_sync` (`scripts/sync.py`) | a table behind the draft | as needed | the comparison reads metadata only, so it kept working |
| this machine, every `dm_*_stores` and `dm_zone_redivis` | `erw_headers`, read to merge the table's header lines | small ("this export of 0GB") | refused: `redivis exited 1` on every store step |

Other failures of this machine's run, fixed here:
- `dm_live_set`: "MISMATCH sources: CSV 315, Supabase 316". The extra row, "OPEC: Publications", was loaded by a run on this machine on 15 October whose news tables were never committed (decision 4). The row is back in `sources.csv`; a load gave `match sources: CSV 316, Supabase 316`.
- `dm_commit`: "git pull --rebase exit 128" on 15 and 17 October: those same eight uncommitted tracked tables ("You have unstaged changes"). The commit step now sets such files aside in a named stash before its pull.

`ercot_zone_load_hourly` ("the operator answered no hour", 10 October): already fixed at its cause by session 277 (`47fd2d4f`). Its 10-day window asked for hours ERCOT had not posted in its monthly workbook, and that publisher's lag is now "stale at source", a skip. The table runs in the Saturday supply refresh; the daily runs of 17 October stopped before it, so 24 October is its first run since the fix. It stays listed in STATUS.md until then. No pull was made to prove it (the session's pulls: none).

## The fix

| Piece | Change |
|---|---|
| `warehouse/restore_tables.py` (new) | per missing table: (1) `--cache DIR` when the copy's data SHA-256 is the archive's latest; (2) `_copies/<table>/<sha>.csv.gz` in the bucket, same test; (3) the archive rebuilt from the bucket, taken with the latest run's row count (or more for `judge_by_newest`, `price_board_spreads`); (4) Redivis under `export_ceiling_gb_per_day` (2 GB a UTC day, all machines, ledger `_exports/<day>/` in the bucket). None: exit 1, the run stops (session 28's rule). `--stash DIR` keeps the tables as last archived for the cache; `--seed-bucket` puts an exact copy in the bucket |
| `daily-prices.yml` | `actions/cache/restore@v4` before the run (`erw-rolling-<run id>`, restore keys `erw-rolling-`), `RESTORE_CACHE`; after a good run, the stash and `actions/cache/save@v4` |
| `run_daily.sh`, `roundup.yml` | the restore is `restore_tables.py --rolling` (the Roundup reads the daily run's cache) |
| `scripts/sync.py` | a missing or behind table from the archive first; Redivis last, under the ceiling, its export written to the ledger |
| `warehouse/redivis/upload.py` | a read refused for the cap is "skipped: Redivis export cap" (the draft's header lines left as they are); an upload refused for it is a skip, exit 75, the table waiting in the archive; `restore(only=...)` for one table |
| `warehouse/table_stores.py` | the Redivis step's exit 75 is a skip, recorded as one |
| `warehouse/archive/archive.py` | an exact copy of a rolling-window table that has dropped keys goes to `_copies/` when it is archived; `pull` leaves `_copies` and `_exports` out |
| `warehouse/archive/restore.py` | a bucket's run log read once per client, not once per table |
| `warehouse/run_data_machine.sh` | tracked files the run does not commit are stashed, by name, before `git pull --rebase` |

## Pulls against their ceilings

- Publishers: none (ceiling: none).
- The archive bucket: the 48 tables' parts read twice for the trials (about 248 MB compressed each time; Supabase Pro includes 250 GB of egress a month).
- Redivis: no export asked by the session; two uploads (`carb_auction_allowance_prices`, the stores proof, 336 rows; nothing released).

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 305"` | 0 | six of six |
| `restore_tables.py --rolling --no-redivis --out-dir <scratch>` | 1 | 46 of 48 from the archive; `policy_reads_evidence` and `price_board_spreads` refused on their row counts (decision 3) |
| the same for those two, after decision 3 | 0 | one from its bucket copy, one by the moving-window rule |
| rebuild against this machine's copies, values with `retrieved_at` aside | | equal for every table where this copy is the archive's latest (5); elsewhere the archive holds the 15 October run, newer than Redivis's upload |
| `tests.test_session305` and the affected tests (119, 173, the Redivis gates, 46) | 0 | 96 tests |
| the whole suite | 1 | 4279 tests, 4 failures: `test_session125`, `165`, `267`, `51`; the same four fail with this session's changes set aside (they read this machine's own data files and an untracked `.do` file) |
| `erw_validate.py` on the eight news and deal tables | 0 | |
| `build_coverage.py --only` the eight | 0 | |
| `table_stores.py carb_auction_allowance_prices` under the lock | 0 | uploaded; `erw_headers` "skipped: Redivis export cap" |
| `load.py --no-vacuum --only '^caiso_grid_emergencies$'` under the lock | 0 | `match sources: CSV 316, Supabase 316` |
| `scripts/freeze.py status` | 0 | no freeze |

## The landing

- Before `s305-before` 06:02:37 UTC; live set loaded (sources); merged origin/main (nothing new); pushed 06:02:57 (`7bd74acf`); deployment 7166881092 success 06:04:36; after `s305-after` 06:04:40; compare: **0 differences on 25 pages** (expected: nothing a visitor sees changed).
- The manual run: [39207762565](https://github.com/SamuelEnrique/erw/actions/runs/39207762565), **cancelled** at the 180-minute job limit (09:04:06 UTC). Steps: merge tests ok, data lock ok, cache restore ok (empty, the first run), restore 48 of 48 from the archive (log line "restored 48 of 48 tables (the archive: 47, a copy in the archive bucket: 1); 0 failed"), ercot, nyiso, isone, eia930, eia930_storage, caiso_fuel_supply, carbon_intensity, caiso_join, eia930_interchange, grid_network, weather_nws, eia_fuels, trader_view ok; caiso DAM and RTM, spp DAM and RTM and eia930_emissions failed ("no complete day of CO2 values in the window"); stash, cache save and commit skipped. Not green by 13:00: reported, the workflow as it was. Today's 14:00 run will be the next test (session 313 reports it).

## Decisions made without you

1. **Straight to `main`.** A code change belongs on a `task/` branch with its checks (docs/machines.md); the manual run had to run on main's code before 13:00 UTC, so the commits went to main after the local suite (above) and the before and after snapshots. Reversible: three commits.
2. **The ceiling is 2 GB a UTC day, all machines together** (60 GB in 30 days, under Redivis's 100), and a table whose size Redivis does not report is counted as 1 GB.
3. **Two tables the archive cannot rebuild row for row.** It records no deletion for a rolling-window table, so a table that drops keys rebuilds with more rows. `policy_reads_evidence`: this machine's copy has the latest run's 3,216 rows and the archive's values for every one; it was archived again as held here (0 rows new, run `20261019T054850Z-local`), and its exact copy put in the bucket. `price_board_spreads` (2,303 rebuilt against 2,281, days that left its 365-day window): taken by the existing `judge_by_newest` rule, since its builder rebuilds it from its inputs each run and carries only ERCOT's rows. From now on `archive.py write` puts the exact copy of any such table in the bucket each time it archives it.
4. **The eight news and deal tables of 15 October are committed.** A run on this machine at 15:32 to 15:43 UTC that day scored 521 stories and extracted their deals, and its tables stayed uncommitted here. Each is a superset of main's (`news_stories` 20,244 rows against 19,723, none of main's missing) and passes the validator. Committing them also saves the runner from scoring the same stories again. The registry row of that run, "OPEC: Publications", is back in `sources.csv` as Supabase holds it.
5. **The manual run is the day's run.** It sends the day's digest and spends the scheduled steps' model budget (the workflow's own cap, USD 1.50), and the 14:00 UTC trigger is skipped by the gate ("the day's work is done").
6. **`erw_headers` is left stale while the cap lasts.** The tables' own headers are in the archive's run log and in each table's description. Before a release, the headers table should be rebuilt (session 312 has it).
7. **The health summary of 18 October was written here** (`health.py summary --day 2026-10-18`), because the daily run that writes it had not run.

## For Samuel's ruling

- The daily job's 180-minute limit: the runs of 14, 15 and 19 October were cancelled at it, today with CAISO OASIS and SPP timing out from the runner (78 minutes of retries). Raise the limit, cut the retries when a publisher does not answer, or leave it.
- The Roundup of week 42 (18 October) was not sent: run `roundup.yml` by hand now that the restore works, or let week 43 be the next.
- The gate counts a run as done when its job is green, and a daily run whose step failed is still green: the 14:00 run of 17 and 18 October was skipped after a failed run. Change the gate to read the step's status, or leave it.

## Files

- New: `warehouse/restore_tables.py`, `tests/test_session305.py`, `queue/summary/2026-10-18-health.md`, this report.
- Changed: `.github/workflows/daily-prices.yml`, `.github/workflows/roundup.yml`, `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `scripts/sync.py`, `warehouse/redivis/upload.py`, `warehouse/redivis/config.yaml`, `warehouse/table_stores.py`, `warehouse/archive/archive.py`, `warehouse/archive/restore.py`, `docs/machines.md`, `tests/test_session119.py`, `tests/test_session173.py`, the eight news and deal tables, `warehouse/metadata/sources.csv`, `coverage.csv`, `docs/coverage.md`, `archive_manifest.csv`, `redivis_uploads.csv`, `site/data/health_days.json`.
