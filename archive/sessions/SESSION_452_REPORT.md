# Session 452 report: ercot_peak_premium, refreshed

21 October 2026, from 08:40 UTC, unattended, on lab-desktop (the data machine), the first session of the chain of 21 October, day (`queue/done/018-day-21-october-data.md`). Model spend USD 0. Pulls: none.

## Read these first

- **Refreshed and loaded.** `ercot_peak_premium_monthly` went from September to **October 2026** (23,688 to 23,856 rows; October is the month so far, as the builder writes it). `ercot_peak_premium_annual` keeps its 2,016 rows, with 2026's year rebuilt. The archive took 114 and 280 rows new or changed. The live set took both whole (2,016 and 23,856 written; the database 2,322.3 to 2,326.1 MB), through the gate (0.49 s before, 0.46 s after).
- **Why it had not run since 29 September: a fault in its input check, now fixed** (`warehouse/derived/ercot_peak_premium.py`, `tests/test_session452.py`, 3 tests). The builder refused "62208 rows repeat a (hub, interval) across the input tables". The daily step `dm_ercot_hub_append_stores` now writes the live days into the year's history too, so every interval of the rolling `ercot_rtm_hub_prices` (31,104 rows) is also in `ercot_rtm_hub_prices_2026`: 62,208 is twice 31,104. The same interval at the same price is now read once (the history's row, read first, and the count is logged). The same interval at two prices is still refused. On the runner the step fails earlier, since the history is never restored there.
- **The consolidated tables are as they were.** The run needs the members of `ercot_all_hub_prices_history` (24 members) and `iso_rtm_hub_prices` (4). `consolidate.py split` wrote them, then the builder ran, then `consolidate.py build` found both families "unchanged since the split; not rewritten". The data rows' SHA-256 equals the copies set aside first (`runs/s452_before/`), and no member is left in `warehouse/output`.
- **Memory first**: 8.53 GB free of 15.70 GB at 08:40 UTC; the two families are 717 MB and 16 MB as CSVs.
- `consolidate.py check` read `iso_rtm_hub_prices` as MISMATCH before anything was done. Its four members add up to the table's 57,312 rows; what it compares with is the older copies of the members kept in `warehouse/output/members/`. Not this session's to change; noted.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | |
| `consolidate.py check --family ...` (before) | 1 | `iso_rtm_hub_prices` against `members/`'s older copies (above) |
| `warehouse/lock.py acquire` | 0 | 08:40 UTC; released 08:44 UTC |
| `consolidate.py split --family ercot_all_hub_prices_history --family iso_rtm_hub_prices` | 0 | 28 members |
| `ercot_peak_premium.py` (as it was) | 1 | the 62,208 repeated rows |
| `tests.test_session452` | 0 | 3 tests |
| `ercot_peak_premium.py` (fixed; the main checkout's copy restored after the run) | 0 | |
| `consolidate.py build --family ...` | 0 | both unchanged, not rewritten; data rows' hashes equal |
| `erw_validate.py` (both) | 0 | |
| `archive.py write`, `build_coverage.py --only` | 0, 0 | |
| `db_probe.py`, `load.py --only`, `db_probe.py` | 0, 0, 0 | |

Rule 8: `s452-load-before` and `s452-load-after`, 0 differences on 25 pages, expected (every page in review).

## Decisions made without you

1. A repeated interval at the same price read once, keeping the refusal for two prices.
2. The fixed builder run from the main checkout by copying the file in and restoring it after, so that the main checkout stays on main's code.

## For Samuel's ruling

- A step for `ercot_peak_premium` in `warehouse/run_data_machine.sh`, with the split and build around it, since no scheduled run can build it now.

## Files

- Changed: `warehouse/derived/ercot_peak_premium.py`, `warehouse/metadata/coverage.csv`, `docs/coverage.md`. New: `tests/test_session452.py`, this report.
