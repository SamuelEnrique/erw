# Session 325 report: the known gaps and the gap days

19 October 2026, from 21:24 UTC (the rule) and 23:08 UTC (the re-asks), unattended, on lab-desktop (the data machine), the fifth session of the chain of 19 October, daytime. Model spend USD 0.

## Read these first

- **The open gap days: 833 (session 309) to 234.** 597 closed as known gaps, by the owner's default for item 16. 2 filled: CAISO's 2 November 2025, day-ahead and real-time, by session 322's fix of the 25-hour request. The other 234 are still incomplete at the source, or a held publisher's.
- **How a gap day is closed:** a row of `warehouse/metadata/known_gaps.csv` keyed `<table>:gap_days`, with two new columns, `part` (the BA or market) and `days` (a list, a range or `all`), each with session 309's reason. `build_status.py` counts a day so named as "closed as a known gap" when the table still lacks it. The key is not the table's name, so `iso_prices.gap_skip` never reads it as a pass for the table's own failures on the runner. Three rows:
  - `eia930_all_storage`, ERCO and ISNE 2024-11-06, MISO 2025-01-15, SWPP 2026-02-04: each BA's first BAT day, which EIA reports only in part (4 closed);
  - `eia930_all_storage`, US48 2024-07-01 to 2026-01-31: EIA's series is not complete there (109 closed);
  - `eia930_all_emissions`, SWPP, every day: EIA's workbook holds no CO2 for SWPP's hours (484 closed).
- **Re-asked, newest first; none filled.** EIA's API for the demand days of September and October 2026 (ERCO 4, NYIS 2, SWPP 2; 27 requests) and ERCO's BAT days of 5 and 6 December 2025 (2 requests). EIA's per-BA workbooks re-posted on 19 October 2026 (Last-Modified 16:12 GMT, saved by this machine's daily run, so no request), built in a scratch folder and tested day by day against the 162 open emissions days. Every one is still incomplete. Each re-ask is a row of `run_status.csv` (run `20261019T232000Z`, 172 rows).
- **A table of several grids can now be re-checked:** `iso_hub_prices_history`'s gap rows name their market (`caiso_dam 2025-11-02`), and `day_complete` judges that market's rows on its grid's day. Before, such a day was "not verifiable here" (session 58).

## Open gap days by table, after the session

| Table | Open | Why |
|---|---:|---|
| `eia930_all_emissions` | 168 | CISO, PJM, MISO, NYIS, ERCO, ISNE, US48 days EIA's workbooks of 19 October still lack (162 single days; 6 ranges recorded by a history build) |
| `iso_hub_prices_history` | 43 | ISO-NE, NYISO and SPP days: held publishers, not asked |
| `eia930_erco_demand`, `_nyis_`, `_swpp_` | 4, 2, 2 | EIA's API still lacks hours |
| `isone_rtm_zone_prices`, `_hourly`; `spp_rtm_hub_prices` | 7, 2; 3 | held, not asked |
| `eia930_all_storage` | 2 | ERCO 5 and 6 December 2025: EIA's API still lacks hours |
| `eia930_all_interchange` | 1 | names no single day |

## Pulls against their ceilings

- EIA's API: 29 requests of 1,500 (27 for `eia930.py --days 50`, 2 for `eia930_storage.py --since 2025-12-01 --ba erco`). Nothing was asked of ISO-NE, NYISO, SPP, MISO or PJM.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 325"` | 0 | |
| `consolidate.py split`, `eia930.py --days 50`, `consolidate.py build` under the lock | 0, 0, 0 | 0 rows new for the gap days |
| `eia930_storage.py --since 2025-12-01 --ba erco` under the lock | 0 | the two days still short |
| `eia930_emissions.py --from-raw --dry-run`, then into `runs/s325_em` | 0, 0 | 4,345,896 rows, 19 incomplete BA-day groups (17 in session 309); 0 of 162 open days filled |
| `build_status.py` | 0 | 234 open, 147 filled, 597 closed as known |
| `tests.test_session325`, 149 | 0 | |

## Decisions made without you

1. **The closures are rows of `known_gaps.csv`, under a key of their own**, so they cannot mask a table's failure on the runner.
2. **No table was stored or loaded:** nothing filled, so this machine's copies of the EIA-930 tables (behind the runner's) were not archived over the runner's.
3. **The first scratch build was wrong and was redone:** `--out-dir` also moves the raw folder, and the completeness cache is keyed by table, so a second test read the first table's counts. Both corrected before the result above.

## For Samuel's ruling

- ERCO's 5 and 6 December 2025 storage days, and the eight EIA-930 demand days: close them as known gaps too, or keep asking.

## Files

- New: `tests/test_session325.py`, this report.
- Changed: `warehouse/metadata/known_gaps.csv` (columns `part`, `days`; three rows), `warehouse/metadata/build_status.py` (`known_gap_days`, `known_day`, a market's day in a table of several grids), `warehouse/metadata/run_status.csv` (172 rows), `STATUS.md`.
