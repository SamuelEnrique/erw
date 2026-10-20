# Session 336 report: the three red steps and the code machine's requests

20 October 2026, from 04:04 UTC (the prompt is dated the night of 19 October), unattended, on lab-desktop (the data machine). Model spend USD 0. Pulls: EIA's API 7 of 10 (`publisher_figure.py`); ERCOT and CAISO 0 of 40; NYISO, ISO-NE, SPP and PJM held, MISO paused: none asked.

## Read these first

- **20 October does not count green by the new gate, and cannot: its three failed rows were recorded before this session began, and the gate counts any failed row of the day** (`health.day_record`, read at 07:31 UTC: 251 counted rows, 3 failed, none missing). They are the scheduled run's (39344868297, started 19 October 23:58 UTC on `cb4d456f`): `eia930` at 00:26 (five demand tables, "incomplete data": the midnight window, item 2), `generation_mix` at 00:50 ("input table absent: eia_state_generation_monthly", after `eia_series` hit its 15-minute budget; session 327's guard, which skips the step then, landed at 02:19 UTC, after that run had started) and `package tests` at 02:17 (`nyiso_zone_load_hourly`, item 1). **The manual run proves each step now passes:** https://github.com/SamuelEnrique/erw/actions/runs/39373861108 (workflow_dispatch on `ad0a1e76`, queues 0, monthly 0, once 0), 05:14:53 to 07:30:54 UTC, **success**: 24 rows of `erw_health`, 22 ok and 2 skipped (`eia_series`, EIA's budget again; `carb_lcfs`, the known gap), none failed. `eia930` wrote with no failed row at a start after 05:00 UTC (the run's own commit `e37f529f` lists it ok, "failed: none"), `generation_mix` skipped by session 327's rule, and `package tests` ok at 07:30. 21 October is the first day that can count green (`runs/s336_day_20.out`, `runs/s336_day_20_steps.out`).
- **The package test of `nyiso_zone_load_hourly` failed on the runner's header, not its rows.** The runner rebuilds the held NYISO table from the archive every run (`warehouse/restore_tables.py`, session 305), which writes "Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), ..." above the table's own header. The test's `own_first_line` set aside only `restore.py`'s line (session 202), so the table's first own line was that note: "assert (False)". Read from the archive's run log in the bucket: each rebuild also stacked one more such line on the last (12, 13, 14 and 15 header lines, 15 to 20 October). It passed on this machine, whose copy came from the Redivis draft. **Fixed both:** the test sets aside any rebuild line, and `restore_tables.py` and `restore.py` drop the run's own rebuild lines before adding theirs (the data SHA-256 the archive compares is of the rows only, so nothing else moves).
- **eia930's window.** A demand table's window now ends at the last midnight EIA has published demand to: the clock's midnight when EIA holds the hour that ends there, else the one before (one day back at most; a longer lag fails as before). The query asks one day more at its start. **The dry run proves it at a simulated 00:05 start, asking EIA nothing** (`--dry-run --now --raw --raw-through`, a replay of an earlier run's raw answers): at 2026-10-19T00:05Z, with EIA's answers of the 10:51 run cut at period 2026-10-18T23 as they stood at midnight, all eight demand tables are written (window to 18 October, 144 rows each). The old rule over the same rows fails exactly the runner's five (CISO, ISNE, MISO, PJM, US48: "71 of 72 hours"); with the hour published the window stays at the clock's midnight. 20 October's raw answers are on the runner, not here, so the replay is of 19 October's, one day earlier.
- **`publisher_figure.py` had a fault of its own:** for a retail sales draft it asked EIA for the column `retail_sales` (the ERW's variable); EIA's column is `sales` (`eia_series.py:192`), and EIA answered HTTP 400. Fixed; then **all four open EIA record drafts carry EIA's figure, each the same as ours** (the scan of 19 October had raised four, not two). The step now runs after the data machine's daily scan (`dm_publisher_figure`), and EIA not answering (5xx, a timeout) is a skip, not a red day.

## What to review

1. `package/tests/test_erw.py` (`own_first_line`), `warehouse/restore_tables.py` (`replay_sliced`), `warehouse/archive/restore.py` (`rebuild`).
2. `warehouse/connectors/eia930.py`: `demand_window_end`, `raw_rows`, the dry run in `main`.
3. `warehouse/analysis/findings/publisher_figure.py` (`MEASURE_COLUMNS`, the skip) and its step in `warehouse/run_data_machine.sh`.
4. `tests/test_session336.py` (15 tests).

## The code machine's requests (`docs/state/review_2026-10-19_code_pm.md`)

| Request | Done |
|---|---|
| The first daily `dm_grid_tables` run (session 314) | Run here at 04:15 UTC as the schedule runs it (`warehouse/health.py run --step dm_grid_tables`, an `ok` row of `erw_health`): 7 grids, 93 public live tables, 425 reads of the live set, 56 s; `ercot_grid_notices` (session 322) joins ERCOT's tables. `docs/grids/grid_tables.json` committed. The scheduled run (`run_data_machine.sh` sources `run_data_machine_tables.sh:213`) runs it next at 17:00 UTC |
| `publisher_figure.py` after the scan (session 316) | Run (above): 4 of 4 drafts with EIA's figure, 7 requests (4, of which two answered 504 and one 400, then 3 after the fix). In the daily run after `dm_scanner` |
| ERCOT's day-ahead table to the last day (session 319) | Already there: the live set's `iso_dam_hub_prices` holds ERCOT's day-ahead to 2026-10-21T04:00Z (the operating day of 20 October), loaded 01:20 UTC by the manual run; CAISO's to 06:00Z. The market of 21 October posts about 18:30 UTC. No ERCOT or CAISO request (0 of 40) |
| NYISO's and ISO-NE's day-ahead | **Held** (the prompt: not asked). MISO's is paused (since 4 October); its newest hour in the live set is 2026-10-04T04:00Z |

## Pulls against their ceilings

| Pull | Ceiling | Used |
|---|---|---|
| EIA's API, `publisher_figure.py` | 10 | 7 |
| ERCOT's and CAISO's day-ahead connectors | 40 | 0 |
| NYISO, ISO-NE, SPP, PJM (held), MISO (paused) | 0 | 0 |

Every other read was of this machine's files, the live set (Supabase) and the archive's bucket.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | on duty until 2026-10-20 20:04 UTC |
| the package test `test_large_table_by_partition[nyiso_zone_load_hourly]` here | 0 | passes on this machine's copy (the Redivis draft's header); the runner's header read from the archive's run log |
| `tests.test_session336` | 0 | 15 tests |
| `tests.test_session336`, 305, 316, 181, 202 | 0 | |
| eia930 dry runs, a and b (`runs/s336_eia930_dry_a.out`, `_b.out`); the old rule (`runs/s336_eia930_old_rule.out`) | 0, 0, 0 | above |
| the whole suite, `GITHUB_ACTIONS=true` | 1 | 6 failures: the five standing (51, 94, 125, 165, 267) and `test_session156` case 18 (Texas's curtailment share, from the daily data of 20 October, session 327's item 8; `site/data/curtailment/ercot.json` is main's own) |
| `scripts/freeze.py status` | 0 | no freeze |

## The landing

- Freeze 0. Before snapshot `s336-before` at 04:33:09 UTC. Merged origin/main (session 319's landing) into `task/336-red-steps`; pushed 04:33:18 (`7cea126d`). Checks: run 39370197596 **success** (04:33:22 to 04:44:44). The branch was merged to main by the checks' own landing at 04:44:39 (`1f038b92`, "Merge task/336-red-steps: checks passed"), deployment 7191776445 success 04:46:12; session 320's landing followed at 04:47:51 (`ad0a1e76`), deployment 7191815445 success 04:49:16.
- After snapshot `s336-after` at 05:14:33; compare: **0 differences on 25 pages** (expected: every page is in review; the after snapshot carries session 320's landing too).
- My watch of the checks queried the API with a token this shell holds that GitHub refuses ("Bad credentials"), read nothing for 40 minutes and timed out; the public API showed the success. The dispatch used git's own credential.
- This report went out in a second push, with its own snapshots (below).

## Decisions made without you

1. **Both halves of the header fault fixed**, the test and the stacking: the test alone would have passed while each held table's header grew a line a day.
2. **The window moves one day back at most**, so EIA lagging longer still fails a table loudly; only the demand tables move (the generation tables are checked by day already, and a day EIA has not finished is a gap row as before).
3. **The dry run replays raw answers rather than asking EIA**: the prompt's EIA allowance was `publisher_figure.py`'s, and only a replay can show EIA's state at a past minute. `--raw-through` stands for what EIA had published at the simulated start.
4. **`dm_grid_tables` was run by hand once now** rather than waiting for 17:00, so the request's first run is on record; its row counts toward 20 October as the schedule's would.
5. **`publisher_figure.py` runs in the daily run** (session 316 left its place to you; it is one line after `dm_scanner`, reversible), asking EIA only for a draft without its month's figure; EIA not answering is a skip.
6. **All four record drafts were read**, not two: the review list held four open EIA record drafts.

## For Samuel's ruling

- Whether `dm_publisher_figure` stays in the daily run (decision 5).
- The four EIA record drafts at `/internal/findings` now carry EIA's figure and can be approved or dropped.

## Files

- New: `tests/test_session336.py`, this report.
- Changed: `package/tests/test_erw.py`, `warehouse/restore_tables.py`, `warehouse/archive/restore.py`, `warehouse/connectors/eia930.py`, `warehouse/analysis/findings/publisher_figure.py`, `warehouse/run_data_machine.sh`, `docs/grids/grid_tables.json`.
- Outside git: the four drafts' `card.publisher` in `scanner_drafts` (the script's own write); `runs/s336_*`.
