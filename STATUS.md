# ERW status

Generated 2026-10-29 15:39 UTC by `warehouse/metadata/build_status.py`, which the daily run regenerates after coverage; the daily workflow commits it. Every number below is read from `warehouse/metadata/coverage.csv`, `warehouse/metadata/run_status.csv` or Supabase.

## Tables

| | Tables | Rows |
|---|---|---|
| All | 629 | 98,841,052 |
| Public | 515 | 74,524,036 |
| Internal (never shown publicly) | 114 | 24,317,016 |

Newest table refresh: 2026-10-29 15:15:59 UTC. Validator: 628 of 629 tables pass. Per-table detail: [`docs/coverage.md`](docs/coverage.md).

## Health gate

**Closed.** The latest daily run on GitHub (2026-10-29) has 5 failed tables outside the known-gap list below: `datacenter_projects`, `digest`, `energy_deals`, `news_stories`, `policy_actions`. While the gate is closed, no session adds a new source or a new tool (`PRIORITIES.md`); fixing the failures, or a human adding one to the list, opens it. `python warehouse/metadata/build_status.py --gate` exits 1 while it is closed.

### Known gaps

Failures a human has accepted for now (`warehouse/metadata/known_gaps.csv`, edited by hand). A table here does not close the gate.

| Table | Why | Since | Decided |
|---|---|---|---|
| `ercot_large_load_queue` | ERCOT publishes no request-level large-load list (Protocol 3.2.7 requires only an aggregate monthly report); the connector watches the page and fails loudly until one appears | 2026-09-27 | session 17 design; listed as a known gap in session 28 |
| `carb_auction_allowance_prices` | CARB's auction summary PDF answers GitHub runners with HTTP 202 and no body on every run since 2026-09-27; it downloads from a residential connection. Refreshed locally: docs/runbook.md, "CARB auction prices". On the runner price_board_carbon carries its CARB rows forward from the draft (session 30), and build_coverage.py takes CARB's license from the previous coverage (session 33, after the 2026-09-29 run failed there), so this gap no longer stops the run | 2026-09-27 | session 29 ruling (prompt, Part A 1); reason brought up to date in session 34 |
| `nyiso_interconnection_queue` | NYISO's queue workbook answers GitHub runners with HTTP 202 and no body on every run since 2026-09-27; it downloads from a residential connection. Refreshed locally: docs/runbook.md, "NYISO interconnection queue" | 2026-09-27 | session 29 ruling (prompt, Part A 1) |
| `carb_lcfs_credit_prices` | CARB's LCFS credit price workbook answers GitHub runners with HTTP 202 and no body, as CARB's auction summary does (the same host, the same answer); it downloads from a residential connection and is refreshed by warehouse/refresh_board.sh on the data machine. On the runner the board's builder keeps the held rows for it (page_keep.py) | 2026-10-06 | decided: Samuel, 8 October 2026 (the chain prompt of that day, session 166 D) |
| `nyiso_load_queue` | NYISO's load interconnection requests are the sheet "Load Projects" of the same workbook as nyiso_interconnection_queue, and the same host answers GitHub runners HTTP 202 with no body (first run on the runner Monday 12 October 2026: "the answer is not the workbook (HTTP 202, first bytes b'')"). It downloads from a residential connection. On the runner the pull is recorded as skipped, not failed (session 206) | 2026-10-12 | decided: Samuel, 12 October 2026 (the chain prompt of that day, session 206, step 5) |
| `policy_monitor_refresh:orpuc` | Oregon's docket host (apps.puc.state.or.us) did not answer GitHub's runner on 11 and 12 October 2026 (a read timeout, then a connection error) while the other regulators answered. Not a table: the regulator key orpuc of warehouse/connectors/policy_monitor_refresh.py, whose rows go into large_load_rules and large_load_rules_internal. On the runner its failure is recorded as skipped, not failed (session 206); the data machine's daily run asks Oregon once a day (warehouse/run_data_machine.sh) | 2026-10-11 | decided: Samuel, 12 October 2026 (the chain prompt of that day, session 206, steps 5 and 6) |
| `eia930_all_storage:gap_days` | Each balancing authority's first day of BAT (battery) values: EIA's series begins part-way through it (ERCO and ISNE 2024-11-06, MISO 2025-01-15, SWPP 2026-02-04), and EIA's API answered the same on session 309's re-ask (run 20261019T111546Z). The day can never be complete at the source | 2026-10-19 | decided: Samuel, 19 October 2026 (the chain prompt of that day, daytime; the morning note's item 16, session 309's finding) |
| `eia930_all_storage:gap_days` | US48's BAT series from EIA is not complete for these days (July 2024 to January 2026): session 309 asked again from 2024-07-15 (run 20261019T111546Z) and EIA's API added 72 rows but filled none of the 109 open days | 2026-10-19 | decided: Samuel, 19 October 2026 (the chain prompt of that day, daytime; the morning note's item 16, session 309's finding) |
| `eia930_all_emissions:gap_days` | EIA's per-BA workbook for SWPP holds no CO2 value for these hours (for example 12 to 21 March 2021): session 309 read the workbooks of 17 October 2026 (Last-Modified) and rewrote the table from them; a day with no value at the source cannot fill | 2026-10-19 | decided: Samuel, 19 October 2026 (the chain prompt of that day, daytime; the morning note's item 16, session 309's finding) |

## Last runs

| Workflow | Last run (UTC) | Outcome |
|---|---|---|
| daily prices, on GitHub | 2026-10-29 15:39 | 164 ok, 6 failed, 20 gap, 8 skipped (table results of that day) |
| daily run, local | 2026-10-19 23:20 | 941 gap (table results of that day) |
| latest prices, every 15 minutes | 2026-10-29 15:31 | 39 hubs and zones in `latest_prices` (newest retrieval) |

A table that failed is not written that day; nothing partial is. The reasons are in `warehouse/metadata/run_status.csv`.

## Tables whose last run failed

| Table | Run | Reason |
|---|---|---|
| `coverage` | 20260929T185935Z | price_board_carbon: input tables ['carb_auction_allowance_prices'] are not in warehouse/output; fixed in 670ba69 (session 33); recorded in session 34 from the j |
| `datacenter_projects` | 20261029T145217Z | RuntimeError: all 1 calls failed |
| `digest` | 20261029T153913Z | anthropic.BadRequestError: Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'You have reached your specified API usage  |
| `energy_deals` | 20261029T145212Z | RuntimeError: all 1 calls failed |
| `news_stories` | 20261029T145105Z | model claude-haiku-4-5; calls 0 (16 failed); stories scored 0 of 400; tokens input 0, output 0, cache write 0, cache read 0; cost USD 0.0000; duplicate links re |
| `policy_actions` | 20261029T145208Z | 0 newly scored, 1959 of 1980 scored; 388 at significance 5 or more; cost USD 0.0000 |

## Open gaps

Days a per-day connector could not write complete, re-checked against the table with the connector's own completeness rule. Recorded gap days: 1124; filled since: 249; closed as known gaps: 599 (`eia930_all_emissions` 486, `eia930_all_storage` 113; the rows of warehouse/metadata/known_gaps.csv keyed <table>:gap_days); open: 276.

| Table | Day | State | First recorded reason |
|---|---|---|---|
| `eia930_all_emissions` | 2018-07-10 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2018-08-01 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2018-08-25 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2018-09-19 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2018-10-17 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2018-11-04 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2018-11-05 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2018-11-08 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2018-11-09 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2018-11-10 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2018-11-12 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2018-12-03 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2018-12-23 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-02-02 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-02-06 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-03-11 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-04-03 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-04-17 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-04-18 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-06-01 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-06-12 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-06-28 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-07-04 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-07-05 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-07-12 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-08-13 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-08-25 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-08-29 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-09-01 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-09-24 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-11-03 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-11-04 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-11-13 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-11-14 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-12-01 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-12-04 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-12-12 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-12-13 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2019-12-14 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2020-02-14 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2020-03-08 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2020-03-09 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2020-03-30 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2020-06-18 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2020-08-02 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2020-08-03 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2020-08-04 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2020-08-10 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2020-10-31 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2020-11-02 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2021-03-01 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2021-07-28 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2021-08-18 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2021-08-27 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2021-08-29 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2021-08-30 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2021-08-31 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2021-10-22 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2021-11-08 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2021-12-08 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2021-12-09 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2021-12-28 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2022-01-05 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2022-03-13 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2022-03-14 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2022-05-17 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2022-06-06 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2022-06-09 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2022-06-13 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2022-10-01 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2022-10-02 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2022-11-05 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2022-11-06 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2022-11-07 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2023-03-12 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2023-03-13 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2023-04-13 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2023-10-04 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2023-10-12 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2023-10-31 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2023-11-04 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2023-11-05 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2023-11-06 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2023-11-07 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2023-11-14 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2023-11-28 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-01-17 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-01-18 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-03-10 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-03-11 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-03-28 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-05-17 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-05-18 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-06-30 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-07-01 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-07-02 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-10-09 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-10-10 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-10-19 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-10-31 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-11-01 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-11-02 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-11-03 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-11-03 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-11-04 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2024-11-19 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-01-15 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-01-16 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-01-17 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-03-07 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-03-08 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-03-09 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-07-01 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-07-02 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-07-24 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-07-25 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-10-31 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-11-01 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-11-01 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-11-02 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-11-02 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-11-03 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-12-03 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-12-04 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2025-12-06 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-01-24 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-01-25 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-01-30 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-02-01 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-02-09 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-02-09 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-02-10 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-02-10 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-02-18 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-03-06 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-03-07 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-03-08 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-03-08 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-03-09 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-03-27 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-04-23 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-05-04 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-05-05 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-06-10 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-06-25 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-07-01 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-08-25 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-09-27 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-09-27 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-09-28 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-09-28 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-09-29 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-10-03 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-10-04 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-10-05 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-10-06 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-10-07 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-10-07 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-10-08 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-10-09 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-10-10 | still incomplete in the table | 0 of 24 hours with co2_emissions_coal; not written for this day |
| `eia930_all_emissions` | 2026-10-10 | still incomplete in the table | session 325 re-check (EIA's per-BA workbooks of 19 October 2026, Last-Modified 16:12 GMT, saved by this machine's daily run at 17:24 UTC; no |
| `eia930_all_emissions` | 2026-10-11 | still incomplete in the table | 0 of 24 hours with co2_emissions_coal; not written for this day |
| `eia930_all_emissions` | 2026-10-12 | still incomplete in the table | 21 of 24 hours with co2_emissions_oil; not written for this day |
| `eia930_all_emissions` | 2026-10-12 | still incomplete in the table | 7 of 24 hours with co2_emissions_coal; not written for this day |
| `eia930_all_emissions` | 2026-10-15 | still incomplete in the table | 12 of 24 hours with co2_emissions_oil; not written for this day |
| `eia930_all_emissions` | 2026-10-15 | still incomplete in the table | 20 of 24 hours with co2_emissions_oil; not written for this day |
| `eia930_all_emissions` | 2026-10-16 | still incomplete in the table | 13 of 24 hours with co2_emissions_oil; not written for this day |
| `eia930_all_emissions` | 2026-10-16 | still incomplete in the table | 22 of 24 hours with both CO2 values; not written for this day |
| `eia930_all_emissions` | 2026-10-19 | still incomplete in the table | 4 of 24 hours with co2_emissions_oil; not written for this day |
| `eia930_all_emissions` | 2026-10-20 | still incomplete in the table | 20 of 24 hours with co2_emissions_oil; not written for this day |
| `eia930_all_emissions` | 2026-10-21 | still incomplete in the table | 1 of 24 hours with co2_emissions_coal; not written for this day |
| `eia930_all_emissions` | 2026-10-22 | still incomplete in the table | 0 of 24 hours with co2_emissions_coal; not written for this day |
| `eia930_all_emissions` | 2026-10-23 | still incomplete in the table | 0 of 24 hours with co2_emissions_coal; not written for this day |
| `eia930_all_emissions` | 2026-10-24 | still incomplete in the table | 4 of 24 hours with co2_emissions_oil; not written for this day |
| `eia930_all_emissions` | 2026-10-27 | still incomplete in the table | 4 of 24 hours with both CO2 values; not written for this day |
| `eia930_all_emissions` | 2026-10-27 | still incomplete in the table | 4 of 24 hours with both CO2 values; not written for this day |
| `eia930_all_emissions` | 2026-10-27 | still incomplete in the table | 4 of 24 hours with both CO2 values; not written for this day |
| `eia930_all_emissions` | 2026-10-27 | still incomplete in the table | 4 of 24 hours with both CO2 values; not written for this day |
| `eia930_all_emissions` | 2026-10-27 | still incomplete in the table | 4 of 24 hours with both CO2 values; not written for this day |
| `eia930_all_emissions` | 2026-10-27 | still incomplete in the table | 4 of 24 hours with both CO2 values; not written for this day |
| `eia930_all_emissions` | 2026-10-27 | still incomplete in the table | 4 of 24 hours with both CO2 values; not written for this day |
| `eia930_all_emissions` | 2026-10-28 | still incomplete in the table | 0 of 24 hours with both CO2 values; not written for this day |
| `eia930_all_emissions` | 2026-10-28 | still incomplete in the table | 0 of 24 hours with both CO2 values; not written for this day |
| `eia930_all_emissions` | 2026-10-28 | still incomplete in the table | 0 of 24 hours with both CO2 values; not written for this day |
| `eia930_all_emissions` | 2026-10-28 | still incomplete in the table | 0 of 24 hours with both CO2 values; not written for this day |
| `eia930_all_emissions` | 2026-10-28 | still incomplete in the table | 0 of 24 hours with both CO2 values; not written for this day |
| `eia930_all_emissions` | 2026-10-28 | still incomplete in the table | 0 of 24 hours with both CO2 values; not written for this day |
| `eia930_all_emissions` | 2026-10-28 | still incomplete in the table | 0 of 24 hours with both CO2 values; not written for this day |
| `eia930_all_emissions` | ciso 2018-07-20..2026-08-19 | a range recorded by a history build (run_status.csv) | 275 UTC days without 24 hours with co2_emissions_coal, not written (first 2018-07-20, 2019-05-28, 2019-08-25; last 2026-08-19) |
| `eia930_all_emissions` | ciso 2018-07-20..2026-08-20 | a range recorded by a history build (run_status.csv) | 10 UTC days without 24 hours with co2_emissions_natural_gas, not written (first 2018-07-20, 2019-08-25, 2019-12-19; last 2026-08-20) |
| `eia930_all_emissions` | ciso 2018-07-20..2026-09-27 | a range recorded by a history build (run_status.csv) | 189 UTC days without 24 hours with co2_emissions_oil, not written (first 2018-07-20, 2019-03-15, 2019-03-16; last 2026-09-27) |
| `eia930_all_emissions` | ciso 2026-10-21..2026-10-24 | a range recorded by a history build (run_status.csv) | 4 UTC days without 24 hours with co2_emissions_coal, not written (first 2026-10-21, 2026-10-22, 2026-10-23; last 2026-10-24) |
| `eia930_all_emissions` | ciso 2026-10-21..2026-10-25 | a range recorded by a history build (run_status.csv) | 5 UTC days without 24 hours with co2_emissions_coal, not written (first 2026-10-21, 2026-10-22, 2026-10-23; last 2026-10-25) |
| `eia930_all_emissions` | ciso 2026-10-21..2026-10-26 | a range recorded by a history build (run_status.csv) | 6 UTC days without 24 hours with co2_emissions_coal, not written (first 2026-10-21, 2026-10-22, 2026-10-23; last 2026-10-26) |
| `eia930_all_emissions` | isne 2024-07-19..2026-09-27 | a range recorded by a history build (run_status.csv) | 366 UTC days without 24 hours with co2_emissions_coal, not written (first 2024-07-19, 2024-07-20, 2024-07-21; last 2026-09-27) |
| `eia930_all_emissions` | isne 2024-09-06..2026-09-27 | a range recorded by a history build (run_status.csv) | 318 UTC days without 24 hours with co2_emissions_oil, not written (first 2024-09-06, 2024-09-07, 2024-09-08; last 2026-09-27) |
| `eia930_all_emissions` | isne 2026-10-10..2026-10-15 | a range recorded by a history build (run_status.csv) | 6 UTC days without 24 hours with co2_emissions_oil, not written (first 2026-10-10, 2026-10-11, 2026-10-12; last 2026-10-15) |
| `eia930_all_emissions` | isne 2026-10-11..2026-10-15 | a range recorded by a history build (run_status.csv) | 5 UTC days without 24 hours with co2_emissions_oil, not written (first 2026-10-11, 2026-10-12, 2026-10-13; last 2026-10-15) |
| `eia930_all_emissions` | isne 2026-10-12..2026-10-19 | a range recorded by a history build (run_status.csv) | 5 UTC days without 24 hours with co2_emissions_oil, not written (first 2026-10-12, 2026-10-13, 2026-10-14; last 2026-10-19) |
| `eia930_all_emissions` | isne 2026-10-13..2026-10-20 | a range recorded by a history build (run_status.csv) | 5 UTC days without 24 hours with co2_emissions_oil, not written (first 2026-10-13, 2026-10-14, 2026-10-15; last 2026-10-20) |
| `eia930_all_emissions` | isne 2026-10-14..2026-10-20 | a range recorded by a history build (run_status.csv) | 4 UTC days without 24 hours with co2_emissions_oil, not written (first 2026-10-14, 2026-10-15, 2026-10-19; last 2026-10-20) |
| `eia930_all_emissions` | isne 2026-10-19..2026-10-25 | a range recorded by a history build (run_status.csv) | 4 UTC days without 24 hours with co2_emissions_oil, not written (first 2026-10-19, 2026-10-20, 2026-10-24; last 2026-10-25) |
| `eia930_all_emissions` | isne 2026-10-19..2026-10-26 | a range recorded by a history build (run_status.csv) | 5 UTC days without 24 hours with co2_emissions_oil, not written (first 2026-10-19, 2026-10-20, 2026-10-24; last 2026-10-26) |
| `eia930_all_emissions` | miso 2018-07-02..2026-09-27 | a range recorded by a history build (run_status.csv) | 2982 UTC days without 24 hours with co2_emissions_oil, not written (first 2018-07-02, 2018-07-03, 2018-07-04; last 2026-09-27) |
| `eia930_all_interchange` | pairs | names no single day (run_status.csv): listed, not re-checked | 353 pair-days with fewer than 24 hours not written: AECI-MISO 2026-10-28 (5 h); AECI-SIKE 2026-10-28 (5 h); AECI-SPA 2026-10-28 (5 h); AECI- |
| `eia930_all_storage` | 2025-12-05 | still incomplete in the table | session 325 re-check (EIA's API, electricity/rto/fuel-type-data BAT, ERCO asked again from 2025-12-01): still incomplete |
| `eia930_all_storage` | 2025-12-06 | still incomplete in the table | session 325 re-check (EIA's API, electricity/rto/fuel-type-data BAT, ERCO asked again from 2025-12-01): still incomplete |
| `eia930_erco_demand` | 2026-09-04 | still incomplete in the table | session 325 re-check (EIA's API, electricity/rto/region-data, asked again for the last 50 days): still incomplete |
| `eia930_erco_demand` | 2026-09-05 | still incomplete in the table | session 325 re-check (EIA's API, electricity/rto/region-data, asked again for the last 50 days): still incomplete |
| `eia930_erco_demand` | 2026-10-05 | still incomplete in the table | session 325 re-check (EIA's API, electricity/rto/region-data, asked again for the last 50 days): still incomplete |
| `eia930_erco_demand` | 2026-10-06 | still incomplete in the table | session 325 re-check (EIA's API, electricity/rto/region-data, asked again for the last 50 days): still incomplete |
| `eia930_nyis_demand` | 2026-09-04 | still incomplete in the table | session 325 re-check (EIA's API, electricity/rto/region-data, asked again for the last 50 days): still incomplete |
| `eia930_nyis_demand` | 2026-09-05 | still incomplete in the table | session 325 re-check (EIA's API, electricity/rto/region-data, asked again for the last 50 days): still incomplete |
| `eia930_swpp_demand` | 2026-09-28 | still incomplete in the table | session 325 re-check (EIA's API, electricity/rto/region-data, asked again for the last 50 days): still incomplete |
| `eia930_swpp_demand` | 2026-09-29 | still incomplete in the table | session 325 re-check (EIA's API, electricity/rto/region-data, asked again for the last 50 days): still incomplete |
| `iso_hub_prices_history` | 2025-09-03 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2025-09-03T04:45:00Z']), extra 0 |
| `iso_hub_prices_history` | 2025-09-10 | still incomplete in the table | day incomplete: 1 intervals longer than 5 minutes (a missing time stamp), first at N.Y.C. 2025-09-10T15:41:00Z |
| `iso_hub_prices_history` | 2025-09-15 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 94 rows, expected 96, missing 2 (first ['2025-09-15T06:30:00Z', '2025-09-15T07:15:00Z']), extra 0 |
| `iso_hub_prices_history` | 2025-09-16 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 89 rows, expected 96, missing 7 (first ['2025-09-16T18:15:00Z', '2025-09-16T18:30:00Z', '2025-09-16T18:45:0 |
| `iso_hub_prices_history` | 2025-09-25 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 94 rows, expected 96, missing 2 (first ['2025-09-25T15:00:00Z', '2025-09-25T15:15:00Z']), extra 0 |
| `iso_hub_prices_history` | 2025-10-22 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2025-10-22T13:30:00Z']), extra 0 |
| `iso_hub_prices_history` | 2025-10-23 | still incomplete in the table | day incomplete: 1 intervals longer than 5 minutes (a missing time stamp), first at N.Y.C. 2025-10-23T15:35:05Z |
| `iso_hub_prices_history` | 2025-10-26 | still incomplete in the table | day incomplete: 1 intervals longer than 5 minutes (a missing time stamp), first at N.Y.C. 2025-10-26T09:40:01Z |
| `iso_hub_prices_history` | 2025-11-01 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2025-11-02T02:45:00Z']), extra 0 |
| `iso_hub_prices_history` | 2025-11-12 | still incomplete in the table | day incomplete: 1 intervals longer than 5 minutes (a missing time stamp), first at N.Y.C. 2025-11-12T15:25:00Z |
| `iso_hub_prices_history` | 2025-11-19 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 89 rows, expected 96, missing 7 (first ['2025-11-19T20:45:00Z', '2025-11-19T21:00:00Z', '2025-11-19T21:15:0 |
| `iso_hub_prices_history` | 2025-11-23 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2025-11-23T11:00:00Z']), extra 0 |
| `iso_hub_prices_history` | 2025-12-01 | still incomplete in the table | day incomplete: 1 intervals longer than 5 minutes (a missing time stamp), first at N.Y.C. 2025-12-01T16:05:03Z |
| `iso_hub_prices_history` | 2025-12-06 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 90 rows, expected 96, missing 6 (first ['2025-12-06T19:30:00Z', '2025-12-06T19:45:00Z', '2025-12-06T20:00:0 |
| `iso_hub_prices_history` | 2025-12-09 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 93 rows, expected 96, missing 3 (first ['2025-12-09T21:15:00Z', '2025-12-09T21:30:00Z', '2025-12-09T21:45:0 |
| `iso_hub_prices_history` | 2025-12-10 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2025-12-10T20:45:00Z']), extra 0 |
| `iso_hub_prices_history` | 2025-12-30 | still incomplete in the table | day incomplete: 1 intervals longer than 5 minutes (a missing time stamp), first at N.Y.C. 2025-12-30T12:25:02Z |
| `iso_hub_prices_history` | 2026-02-03 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 91 rows, expected 96, missing 5 (first ['2026-02-03T19:45:00Z', '2026-02-03T20:00:00Z', '2026-02-03T20:15:0 |
| `iso_hub_prices_history` | 2026-02-07 | still incomplete in the table | day incomplete: 1 intervals longer than 5 minutes (a missing time stamp), first at N.Y.C. 2026-02-07T14:40:02Z |
| `iso_hub_prices_history` | 2026-03-27 | still incomplete in the table | day incomplete: 1 intervals longer than 5 minutes (a missing time stamp), first at N.Y.C. 2026-03-27T13:50:05Z |
| `iso_hub_prices_history` | 2026-04-10 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-04-10T04:15:00Z']), extra 0 |
| `iso_hub_prices_history` | 2026-04-21 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-04-21T05:00:00Z']), extra 0 |
| `iso_hub_prices_history` | 2026-04-28 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 79 rows, expected 96, missing 17 (first ['2026-04-28T21:00:00Z', '2026-04-28T21:15:00Z', '2026-04-28T21:30: |
| `iso_hub_prices_history` | 2026-05-21 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 89 rows, expected 96, missing 7 (first ['2026-05-21T18:15:00Z', '2026-05-21T18:30:00Z', '2026-05-21T18:45:0 |
| `iso_hub_prices_history` | 2026-05-27 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 80 rows, expected 96, missing 16 (first ['2026-05-28T00:00:00Z', '2026-05-28T00:15:00Z', '2026-05-28T00:30: |
| `iso_hub_prices_history` | 2026-06-04 | still incomplete in the table | DAM 2026-06-04 failed after 4 attempts: KeyError('Interval End') |
| `iso_hub_prices_history` | 2026-06-06 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 92 rows, expected 96, missing 4 (first ['2026-06-06T10:15:00Z', '2026-06-06T13:15:00Z', '2026-06-06T17:15:0 |
| `iso_hub_prices_history` | 2026-06-12 | still incomplete in the table | day incomplete: 1 intervals longer than 5 minutes (a missing time stamp), first at N.Y.C. 2026-06-12T11:05:02Z |
| `iso_hub_prices_history` | 2026-06-30 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 91 rows, expected 96, missing 5 (first ['2026-06-30T13:30:00Z', '2026-06-30T18:30:00Z', '2026-06-30T18:45:0 |
| `iso_hub_prices_history` | 2026-07-01 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-07-01T04:30:00Z']), extra 0 |
| `iso_hub_prices_history` | 2026-07-03 | still incomplete in the table | day incomplete: 1 intervals longer than 5 minutes (a missing time stamp), first at N.Y.C. 2026-07-03T22:25:05Z |
| `iso_hub_prices_history` | 2026-07-20 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-07-20T11:00:00Z']), extra 0 |
| `iso_hub_prices_history` | 2026-07-22 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 89 rows, expected 96, missing 7 (first ['2026-07-22T19:30:00Z', '2026-07-22T19:45:00Z', '2026-07-22T20:00:0 |
| `iso_hub_prices_history` | 2026-07-24 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-07-24T12:45:00Z']), extra 0 |
| `iso_hub_prices_history` | 2026-07-27 | still incomplete in the table | day incomplete: 1 intervals longer than 5 minutes (a missing time stamp), first at N.Y.C. 2026-07-28T00:15:00Z |
| `iso_hub_prices_history` | 2026-07-30 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 93 rows, expected 96, missing 3 (first ['2026-07-30T20:15:00Z', '2026-07-30T20:30:00Z', '2026-07-30T22:00:0 |
| `iso_hub_prices_history` | 2026-08-25 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-08-25T19:45:00Z']), extra 0 |
| `iso_hub_prices_history` | 2026-09-02 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-03T03:45:00Z']), extra 0 |
| `iso_hub_prices_history` | 2026-09-11 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-12T03:45:00Z']), extra 0 |
| `iso_hub_prices_history` | 2026-09-12 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-12T04:15:00Z']), extra 0 |
| `iso_hub_prices_history` | 2026-09-13 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 94 rows, expected 96, missing 2 (first ['2026-09-13T04:00:00Z', '2026-09-13T04:15:00Z']), extra 0 |
| `iso_hub_prices_history` | 2026-09-15 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 88 rows, expected 96, missing 8 (first ['2026-09-15T18:00:00Z', '2026-09-15T18:15:00Z', '2026-09-15T18:30:0 |
| `iso_hub_prices_history` | 2026-09-25 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-25T17:15:00Z']), extra 0 |
| `isone_rtm_zone_prices` | 2026-09-02 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-03T03:45:00Z']), extra 0; .Z.CONNECTICUT: 95 rows, expecte |
| `isone_rtm_zone_prices` | 2026-09-11 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-12T03:45:00Z']), extra 0; .Z.CONNECTICUT: 95 rows, expecte |
| `isone_rtm_zone_prices` | 2026-09-12 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-12T04:15:00Z']), extra 0; .Z.CONNECTICUT: 95 rows, expecte |
| `isone_rtm_zone_prices` | 2026-09-13 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 94 rows, expected 96, missing 2 (first ['2026-09-13T04:00:00Z', '2026-09-13T04:15:00Z']), extra 0; .Z.CONNE |
| `isone_rtm_zone_prices` | 2026-09-15 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 88 rows, expected 96, missing 8 (first ['2026-09-15T18:00:00Z', '2026-09-15T18:15:00Z', '2026-09-15T18:30:0 |
| `isone_rtm_zone_prices` | 2026-09-25 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-25T17:15:00Z']), extra 0; .Z.CONNECTICUT: 95 rows, expecte |
| `isone_rtm_zone_prices` | 2026-10-01 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 94 rows, expected 96, missing 2 (first ['2026-10-01T04:00:00Z', '2026-10-01T04:15:00Z']), extra 0; .Z.CONNE |
| `isone_rtm_zone_prices` | 2026-10-20 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 88 rows, expected 96, missing 8 (first ['2026-10-20T19:30:00Z', '2026-10-20T19:45:00Z', '2026-10-20T20:00:0 |
| `isone_rtm_zone_prices_hourly` | 2026-10-02 | still incomplete in the table | RTM_HOURLY 2026-10-02 failed after 4 attempts: EmptyDataError('No columns to parse from file') |
| `isone_rtm_zone_prices_hourly` | 2026-10-09 | still incomplete in the table | RTM_HOURLY 2026-10-09 failed after 4 attempts: EmptyDataError('No columns to parse from file') |
| `spp_rtm_hub_prices` | 2026-10-07 | still incomplete in the table | SPP has no daily RTBM file for 2026-10-07 and its interval file for 2026-10-07 23:10:00-05:00 is missing: SPP RTBM interval 2026-10-07 23:10 |
| `spp_rtm_hub_prices` | 2026-10-10 | still incomplete in the table | SPP has no daily RTBM file for 2026-10-10 and its interval file for 2026-10-10 15:15:00-05:00 is missing: SPP RTBM interval 2026-10-10 15:15 |
| `spp_rtm_hub_prices` | 2026-10-12 | still incomplete in the table | SPP has no daily RTBM file for 2026-10-12 and its interval file for 2026-10-12 17:20:00-05:00 is missing: SPP RTBM interval 2026-10-12 17:20 |
| `spp_rtm_hub_prices` | 2026-10-19 | still incomplete in the table | SPP has no daily RTBM file for 2026-10-19 and its interval file for 2026-10-19 12:15:00-05:00 is missing: SPP RTBM interval 2026-10-19 12:15 |
| `spp_rtm_hub_prices` | 2026-10-21 | still incomplete in the table | SPP has no daily RTBM file for 2026-10-21 and its interval file for 2026-10-21 15:25:00-05:00 is missing: SPP RTBM interval 2026-10-21 15:25 |
| `spp_rtm_hub_prices` | 2026-10-22 | still incomplete in the table | SPP has no daily RTBM file for 2026-10-22 and its interval file for 2026-10-22 18:05:00-05:00 is missing: SPP RTBM interval 2026-10-22 18:05 |
| `spp_rtm_hub_prices` | 2026-10-28 | still incomplete in the table | SPP has no daily RTBM file for 2026-10-28 and its interval file for 2026-10-28 13:50:00-05:00 is missing: publisher did not answer within th |
