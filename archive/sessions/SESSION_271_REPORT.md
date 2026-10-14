# Session 271 report: seven green days and the schedules

14 October 2026, 08:04 to 09:50 UTC, unattended, on lab-desktop (the data machine), the first session of the overnight chain of 14 October (sessions 271 to 278). Branch `task/271-green-days`. Model spend USD 0: no model call. Pulls, each within its connector's ceiling: NOAA (35 requests, 8,994 rows), ERCOT (the 60-day SCED list, then 9 zips, 0.50 GB; the large-load meeting pages in the block's proof run), CAISO (OASIS: nothing new to ask), EIA (the eight EIA-930 workbooks in the block's proof run). Nothing from NYISO, ISO-NE, MISO, SPP, PJM or a paused publisher. Writes under the data lock: ten tables and their stores, the block's proof run.

## Read these first

- **The CARB rule is in: 13 October is green, the first green day on record.** A step that fails only because a publisher has not published within the connector's limit ("29 days old (limit 28)") is now a skip, "stale at source", never retried, a yellow row (`stale` in `site/data/health_days.json`), never a failed step or a red day. 13 October's only failure was exactly that (`dm_carb_lcfs`, CARB's newest week is 14 September). The record reads green for 1 day, counted to 13 October.
- **The yellow row is in the data, not yet on the page.** `/internal/health` is `site/app/internal/health/page.tsx`, which this chain may not edit. The record carries `stale` per day; the page shows a stale step as a skip until its code reads the field (one file, for the code machine).
- **A trap I met and undid: a full coverage build on this machine read `nyiso_load_queue` from a stale copy.** This machine's file is from 10 October; the runner's newer copy declares its license in its header, which the builder takes first. My full build (exit 0) therefore flipped the table to internal, the license files followed, and a gate test (`test_redivis_gates`) caught the header saying public. I put the committed row back and rebuilt the license files: 40 "license needed", as before tonight (price_board_stats out, session 254's `scarcity_hours_by_grid` in). Ruling 1 asks whether this machine should sync that table.
- **NOAA: 6,000,000 rows a year, and a refresh now costs about 9,000 rows, not about 600,000.** A refresh asked the whole stretch since July 2025 every time; it now asks from a week before the newest hour held and stitches the answers. 2026's count: 2,786,639 of 6,000,000 (it began at the old count, 2,777,645). NOAA's service still ends on 4 October 2026, so the tables end there: as current as NOAA allows.
- **Eight new steps on this machine's daily run, two daily and six weekly, and a weekly live-set load.** Below, with the proof run.

## The rulings, one by one

| Ruling | What was done | Result |
|---|---|---|
| The CARB rule | `warehouse/health.py` (`stale_reason`, `is_stale`, the record's `stale` list, the summary's own section), `iso_prices.stale_skip` (and `gap_skip` on any machine), `run_status.streaks` (a lag is not a failed run) | 13 October green; 7 to 12 October stay red on real failures (the runner's CARB HTTP 202, the board builder, the ledger load, the package test) |
| NOAA's ceiling | `CEILING = 6_000_000` a UTC year, counted as rows NOAA sends (`warehouse/raw/noaa_grid_weather/ceiling.json`); the incremental refresh | 35 requests, 8,994 rows; stores exit 0 for the four tables |
| `price_board_stats` | `retired_tables.csv`; the file moved to `warehouse/output/retired/`; `refresh_board_v4.sh` marked retired | coverage 199 tables without it; the license table 39 "license needed" (40 before) |
| ERCOT's storage disclosure | pulled to the newest listed day (6 to 14 August 2026, 9 zips, 10.92 of 12 GB); table and the two derived tables rebuilt | `ercot_sced_esr_hourly` 1,531,959 rows (1,458,735 before), 195 days |
| Node price history | the standing daily pull (session 204) is the only node history ERCOT publishes openly (its archive needs a signed-in account); `ercot_storage_node_basis` rebuilt on what is held | 2,064 rows (2,050 before), the same measuring week |
| The Flex Alert scorecard | `caiso_alert_prices.py` (0 days to pull: the six new notices are 2026 Restricted Maintenance Operations, outside the model's window that ends October 2025, and not alert types), then the scorecard | 2,973 and 881 rows, 0 values changed |
| `clean_energy_hourly` | weekly: EIA-930's workbooks (`--dry-run`), then `mix_clean.py` | see the proof run |
| Weekly live-set load | `dm_live_set_weekly`: every table this machine writes that a live-set rule names | see the proof run |
| ERCOT's 15-minute hub history | `hub_history.py append-ercot`, daily | 34,704 rows appended (27,648 real-time to 13 October 04:45 UTC, 7,056 day-ahead to 14 October 04:00); 3,098,274 rows; 42 s |
| The large-load watch | kept (the Monday watch and the runner's monthly step) | |
| The connector as a guard | `dm_ercot_large_load`, daily | see the proof run |
| The 135 MW footnote | `large_load_snapshot.py` writes a `note` on a report whose approved figure fell from the one before (computed, no reason claimed); `Report.note` in `site/lib/largeload.ts`; the method note | one note, on the report of 19 June 2026 |

## The schedule (`warehouse/run_data_machine_tables.sh`)

| Step | Tables | When |
|---|---|---|
| `dm_ercot_large_load` | `ercot_large_load_status` | daily |
| `dm_ercot_hub_append` | `ercot_all_hub_prices_history` | daily |
| `dm_ercot_sced_pull`, `dm_ercot_sced_write` | `ercot_sced_esr_hourly` | weekly |
| `dm_ercot_storage_rt` | `ercot_storage_rt_monthly`, `ercot_storage_node_basis` | weekly |
| `dm_eia930_workbooks` | none (the workbooks) | weekly |
| `dm_clean_energy` | `clean_energy_hourly`, `clean_energy_summary` | weekly |
| `dm_noaa_weather` | the four NOAA tables | weekly |
| `dm_live_set_weekly` | every table this machine writes that a rule names | weekly |

- "Weekly" is the first run of each ISO week (`runs/dm_weekly_<YYYY-Www>.done`) or `WEEKLY=1`. A step may now name several tables, each stored when it moved, or none.

## The proof run

`WEEKLY=1 lock.py run -- bash warehouse/run_data_machine_tables.sh`, 09:02 to 09:41 UTC, exit 0; no step failed (`runs/session271/block_run.out`).

| Step | Result |
|---|---|
| the ten steps of sessions 247 and 254 | ok; the monthly ones skipped (October's ran) |
| `dm_ercot_large_load` | ok: 38 rows, 0 new (ERCOT has posted no status update since 19 June 2026); stored (the file's retrieval time moved) |
| `dm_ercot_hub_append` | ok: 0 rows (the morning's append had them); no change, no stores |
| `dm_ercot_sced_pull`, `_write` | ok: 195 of 195 days held, 0 requests; the table written and stored |
| `dm_ercot_storage_rt` | ok; both tables stored |
| `dm_eia930_workbooks` | ok: the eight workbooks |
| `dm_clean_energy` | ok: `clean_energy_hourly` 472,877 rows to 13 October 2026 06:00 UTC (4 October before); `clean_energy_summary` 27,447; both stored |
| `dm_noaa_weather` | ok: 35 requests, 8,994 rows; 2,795,633 of 6,000,000 for 2026; the four tables stored |
| `dm_live_set` | ok: the six tables match |
| `dm_live_set_weekly` | ok: written `clean_energy_summary` 27,447, `ercot_large_load_status` 38, `ercot_storage_node_basis` 2,064, `ercot_storage_rt_monthly` 329, `merchant_revenue_monthly` 8,335; six others unchanged; database 1,671.1 MB of 7,500 |

- **No page is live** (`site/lib/release.ts`, since session 166), so the loads cannot change what a visitor sees; the landing's snapshots say so for the 25 pages.
- `merchant_revenue_monthly` was written because the live copy differed from this machine's file: the generator's builders are switched off (`GENERATOR=0`, session 204), so this machine's file is the last one built here. A ruling (2).
- The block's status file lost its first lines during the run: the whole suite ran at the same time and one of its tests wrote the same file. The run's own log has every line.

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py --what "session 271"` | 0 | six of six; on duty |
| `health.py days --from 2026-10-07 --to 2026-10-13` | 0 | green for 1 day, counted to 13 October |
| `noaa_grid_weather.py --offline --out-dir` (trial), then `--refresh` under the lock | 0, 0 | the trial equals the held tables |
| `ercot_sced_esr.py --list`, `--pull --from 2026-08-06` | 0, 0 | 9 of 9 days |
| `caiso_alert_prices.py`, `flex_alert_scorecard.py` under the lock | 0, 0 | 0 days to pull; 0 values changed |
| `ercot_sced_esr.py --write`, `ercot_storage_realtime.py` under the lock | 0 | |
| `hub_history.py append-ercot` under the lock | 0 | 34,704 rows |
| `table_stores.py` for the ten tables | 0 | 40 steps, each exit 0 |
| `build_coverage.py` | 0 | 199 tables; then `nyiso_load_queue`'s row put back (Read these first) |
| `licenses.py tables`, `write`, `status`, `check` | 0, 0, 0, 0 | 199 tables, 40 "license needed", 0 problems |
| the block's proof run | 0 | above |
| `python -m unittest tests.test_session271` | 0 | 17 tests |
| the 20 modules that touch what changed | 1, then 0 | four pins moved by tonight's tables (above), then 432 tests OK |
| `python -m unittest discover -s tests` | 1 | 4,016 tests, 534 s, 7 failures: the three this machine always has (51, 125, 165), and four this session caused and then corrected (120, 207 twice, `test_redivis_gates`); the four modules then 91 tests OK |

## Decisions made without you

1. **The CARB rule reads the words of a connector's own age check** ("<n> days old (limit <m>)") or "stale at source"; a step with any other error line still fails. CARB's HTTP 202 on GitHub's runner is a refusal, not a lag: it stays what session 206 made it (a known gap, a skip on the runner).
2. **Rows recorded "failed" before the rule are read by it too,** so 13 October turned green without rewriting erw_health. 7 to 12 October had other failures and stay red.
3. **The yellow row is data only** (`stale` in the record of days): the page is in `site/app/`, off limits tonight.
4. **NOAA's "6,000,000 rows a year" is counted as the rows NOAA sends in a UTC year,** with 2026 starting at every row counted before (2,777,645). A file this machine already holds is not counted again.
5. **NOAA's refresh asks only from a week before the newest hour held,** so a weekly refresh stays near 9,000 rows. NOAA's revisions of older months are no longer asked for; the first whole answer stays the base.
6. **The SCED pull, its table and the two derived tables are weekly, not daily:** ERCOT keeps 933 days on its list, so nothing is lost, and the table's 1.5 million rows go to the archive and the draft once a week instead of every day. At the 12 GB ceiling (about 19 more days of zips) the step is a skip that says so; run by a person it still exits 3.
7. **"Node price history" is read as the standing daily pull.** ERCOT's history of node prices beyond its 7-day list is behind a signed-in account, which the ERW does not hold.
8. **The Flex Alert scorecard's window was not moved** to 2026: the new notices are not alerts, and a 2026 season would need NOAA's 2026 summer for its three stations (a pull of `noaa_isd.py`) and would change the model's published numbers.
9. **ERCOT's hub history appends only after each member's newest interval;** a workbook's row is never replaced from the live window, and a later workbook replaces the appended rows. On 1 January 2027 the step stops loudly until the 2027 members have their rows in `table_migrations.csv`.
10. **The footnote is computed,** and says nothing of why: ERCOT's deck states no reason. The pages show it once their code reads `note`.
11. **`price_board_stats` stays under `catalogue_hold`** (session 127's test pins it there) and its Redivis draft copy is left for a person, as session 207 left FRED's.
12. **Session 120's and 207's tests were moved to tonight's tables:** 194 matched days (186 before), four retired tables (three); the count of 40 "license needed" stands, with one table out and one in.

## For Samuel's ruling

1. `nyiso_load_queue` on this machine is older than the runner's (10 October against Monday's), and `scripts/sync.py` does not bring it: should the sync take it, so that a full coverage build here agrees with the runner's? Until then a full build on this machine is wrong for that one row.
2. The yellow row on `/internal/health`: the code machine reads `stale` from the record (one file)? And `merchant_revenue_monthly`: this machine's file went into the live set by the weekly load though its builders are switched off here; leave it out of the weekly list?
3. The Redivis draft copy of `price_board_stats`, and its archive history: remove, as FRED's wait to be?
4. NOAA's revisions: ask the whole stretch again once a year (about 650,000 rows of the 6,000,000)?
5. The 2027 members of ERCOT's hub history: add their rows to `table_migrations.csv` before 1 January?
6. ERCOT's storage disclosure reaches its 12 GB ceiling in about 19 days of zips: raise it, or let the table end there?

## Files

- Changed: `warehouse/health.py`, `warehouse/connectors/iso_prices.py`, `warehouse/metadata/run_status.py`, `warehouse/connectors/noaa_grid_weather.py`, `warehouse/connectors/hub_history.py`, `warehouse/connectors/ercot_sced_esr.py`, `warehouse/derived/large_load_snapshot.py`, `warehouse/run_data_machine_tables.sh`, `warehouse/refresh_board_v4.sh`, `warehouse/metadata/retired_tables.csv`, `site/lib/largeload.ts`, `site/data/large_load_status.json`, `site/data/health_days.json`, `docs/machines.md`, `docs/methods/ercot_large_load_status.md`, `docs/methods/ercot_storage_realtime.md`, tests 120, 126, 207 and 247, and the metadata the stores and the license scripts wrote.
- New: `tests/test_session271.py`, this report.
- On this machine, not in git: the ten tables, `warehouse/output/retired/price_board_stats.csv`, `warehouse/raw/noaa_grid_weather/ceiling.json`, `runs/session271/`.

## The landing

- In session 272's report.
