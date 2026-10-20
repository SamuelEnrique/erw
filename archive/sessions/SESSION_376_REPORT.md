# Session 376 report: dm_node_rt, the node basis's real-time days kept each day

20 October 2026, unattended, on lab-desktop (the data machine), the fourth session of the chain of 20 October, day: the code written and tested while the daily run held the data lock, the first real run at 20:21 UTC under this chain's lock. Model spend USD 0. **Pulls: ERCOT 0 of the ceiling of 40 requests**: the step reads the 15-minute files `dm_ercot_node_prices` already saved, and asks ERCOT nothing.

## Read these first

- **Real-time days held in `node_basis_daily`: before, 28 September to 18 October 2026, 20 days; after, 28 September to 19 October, 22 days.** The two gained: 19 October (the newest whole day saved) and **8 October**, which every earlier build had left out: ERCOT posted that day's 11:45 interval twice (`..._20261008_1145_csv.zip` under two posting times), so the hour read five prices and the day was refused as not whole. `realtime()` now reads one file an interval, the later posting (commit `3b509aba`).
- **The step:** `soft_step dm_node_rt "$PYTHON" warehouse/derived/node_basis.py --daily` in `warehouse/run_data_machine.sh`, after the node prices' own pull and stores (`dm_node_stores`) and before `dm_carb_auction`. `--daily` compares the Central days whose every 15-minute interval is saved (`rt_days_saved`, from the files' names: a stamp is the end of its interval) with the days the table holds (`rt_days_held`, the hub's `rtm_mean` rows) and rebuilds only when a day is gained; otherwise it prints "node_basis_daily SKIPPED: ..." and exits 75. ERCOT's list keeps seven days, so a day the step misses for a week can still be built, from this machine's saved files only.
- **Then the stores of what moved**: `node_basis_daily` with `table_stores.py --no-redivis` (validator, coverage row, archive; no Redivis draft: the storage is full, and no session uploads it), `node_basis_summary` and `ercot_node_prices_hourly` through `table_stores` as before. No live-set load in the step: the live set loads `node_basis_daily` from GitHub's run or a session's load (session 374 loaded today's, 957,969 rows).
- **`health.py` knows the step** through its generic `step` wrapper, as every `soft_step`: exit 0 ok, exit 75 skipped with the step's last line as the reason, anything else failed. The step's four names (`dm_node_rt`, `dm_node_rt_stores_daily`, `dm_node_rt_stores_summary`, `dm_node_rt_stores_hourly`) are in `docs/machines.md`'s table of the daily's steps.

## The first run, 20:21 UTC

The worktree's code against the main checkout's files (`runs/s376_daily.py`, which points the modules' paths at the main checkout; the step runs it from main once this lands), under the lock:

| Table | Rows | Range |
|---|---|---|
| `node_basis_daily` | 957,969 (949,995 before) | 888 points; day-ahead 1 October 2025 to 20 October 2026, real time 28 September to 19 October 2026 |
| `node_basis_summary` | 1,260 | to October 2026 |
| `ercot_node_prices_hourly` (internal) | 499,080 | 16 July to 20 October 2026: the ceiling of 500,000 rows keeps the newest days |

About 2.5 minutes; 0 days not read. Then by hand, as the step's stores would: the validator on the three (exit 0), `build_coverage.py --only` the three (exit 0), `archive.py write` the three (exit 0; run `20261020T202433Z-local`: 7,974 rows new or changed in `node_basis_daily`, 153 in `node_basis_summary`, 16,992 in the hourly table with 16,272 keys deleted from its window). **No Redivis step for any of the three in this run**: main's `upload.py` (before session 377's change lands) fails a refusal for storage rather than skipping it.

## Checks

| What | Exit | Notes |
|---|---|---|
| `tests.test_session376` (9 tests), with `204`, `206` | 0 | |
| the trial run into `runs/s376_trial/` (before the lock) | 0 | 21 days: 8 October missing, which found the twice-posted interval |
| the trial again after the fix | 0 | 22 days, saved and built equal |
| `runs/s376_daily.py` (the real run, under the lock) | 0 | above |
| `erw_validate.py`, `build_coverage.py --only`, `archive.py write` | 0, 0, 0 | |

## Decisions made without you

1. **Rebuild whole from the saved files, not an append**: `node_basis.py` builds the tables from the files each time (about 3 minutes); an append would be a second code path to check.
2. **The later posting of an interval ERCOT posted twice is the one read**: ERCOT's correction, as the later file.
3. **No Redivis step in today's run**, for any of the three: the storage is full.

## For Samuel's ruling

- None new: `node_basis_daily` waits for the Redivis storage (session 363's question).

## Files

- New: `tests/test_session376.py`, this report.
- Changed: `warehouse/derived/node_basis.py`, `warehouse/run_data_machine.sh`, `warehouse/table_stores.py` (`--no-redivis`), `docs/machines.md` (commits `68fac139`, `3b509aba` and the reports commit).
