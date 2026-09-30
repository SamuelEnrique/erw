# ERW status

Generated 2026-09-30 00:40 UTC by `warehouse/metadata/build_status.py`, which the daily run regenerates after coverage; the daily workflow commits it. Every number below is read from `warehouse/metadata/coverage.csv`, `warehouse/metadata/run_status.csv` or Supabase.

## Tables

| | Tables | Rows |
|---|---|---|
| All | 77 | 6,042,164 |
| Public | 65 | 5,902,746 |
| Internal (never shown publicly) | 12 | 139,418 |

Newest table refresh: 2026-09-29 18:42:09 UTC. Validator: 77 of 77 tables pass. Per-table detail: [`docs/coverage.md`](docs/coverage.md).

## Health gate

**Closed.** The latest daily run on GitHub (2026-09-29) has 2 failed tables outside the known-gap list below: `coverage`, `eia930_swpp_demand`. While the gate is closed, no session adds a new source or a new tool (`PRIORITIES.md`); fixing the failures, or a human adding one to the list, opens it. `python warehouse/metadata/build_status.py --gate` exits 1 while it is closed.

### Known gaps

Failures a human has accepted for now (`warehouse/metadata/known_gaps.csv`, edited by hand). A table here does not close the gate.

| Table | Why | Since | Decided |
|---|---|---|---|
| `ercot_large_load_queue` | ERCOT publishes no request-level large-load list (Protocol 3.2.7 requires only an aggregate monthly report); the connector watches the page and fails loudly until one appears | 2026-09-27 | session 17 design; listed as a known gap in session 28 |
| `carb_auction_allowance_prices` | CARB's auction summary PDF answers GitHub runners with HTTP 202 and no body on every run since 2026-09-27; it downloads from a residential connection. Refreshed locally: docs/runbook.md, "CARB auction prices". On the runner price_board_carbon carries its CARB rows forward from the draft (session 30), and build_coverage.py takes CARB's license from the previous coverage (session 33, after the 2026-09-29 run failed there), so this gap no longer stops the run | 2026-09-27 | session 29 ruling (prompt, Part A 1); reason brought up to date in session 34 |
| `nyiso_interconnection_queue` | NYISO's queue workbook answers GitHub runners with HTTP 202 and no body on every run since 2026-09-27; it downloads from a residential connection. Refreshed locally: docs/runbook.md, "NYISO interconnection queue" | 2026-09-27 | session 29 ruling (prompt, Part A 1) |

## Last runs

| Workflow | Last run (UTC) | Outcome |
|---|---|---|
| daily prices, on GitHub | 2026-09-29 18:59 | 34 ok, 3 failed, 2 skipped (table results of that day) |
| daily run, local | 2026-09-30 00:30 | 3 ok, 9 gap (table results of that day) |
| latest prices, every 15 minutes | 2026-09-29 22:36 | 39 hubs and zones in `latest_prices` (newest retrieval) |

A table that failed is not written that day; nothing partial is. The reasons are in `warehouse/metadata/run_status.csv`.

## Tables whose last run failed

| Table | Run | Reason |
|---|---|---|
| `carb_auction_allowance_prices` | 20260929T185935Z | RuntimeError: CARB auction summary PDF failed after 4 attempts: RuntimeError('CARB auction summary PDF HTTP 202'); recorded in session 34 from the job log of Gi |
| `coverage` | 20260929T185935Z | price_board_carbon: input tables ['carb_auction_allowance_prices'] are not in warehouse/output; fixed in 670ba69 (session 33); recorded in session 34 from the j |
| `eia930_swpp_demand` | 20260929T185935Z | RuntimeError: incomplete data, no file written for eia930_swpp_demand: demand_forecast_mw: 53 of 72 hours (19 missing, 0 published as null; first missing ['2026 |
| `eia_sector_energy_consumption_monthly` | 20260929T005932Z | RuntimeError: eia_sector_energy_consumption_monthly: newest date 2026-05-01 is 151 days old (limit 150); not writing a stale table |
| `ercot_large_load_queue` | 20260928T234003Z | iso_prices.SourceGap: ERCOT publishes no request-level large-load list: https://www.ercot.com/services/rq/large-load-integration links 3 spreadsheets, none a st |
| `nyiso_interconnection_queue` | 20260928T233903Z | RuntimeError: nyiso queue failed after 4 attempts: RuntimeError('GET https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx failed: <Res |

## Open gaps

Days a per-day connector could not write complete, re-checked against the table with the connector's own completeness rule. Recorded gap days: 789; filled since: 11; open: 778.

| Table | Day | State | First recorded reason |
|---|---|---|---|
| `eia930_all_emissions` | 2018-07-10 | still incomplete in the table | 4 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2018-08-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2018-08-25 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2018-09-19 | still incomplete in the table | 20 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2018-10-17 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2018-11-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2018-11-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2018-11-05 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2018-11-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2018-11-08 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2018-11-09 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2018-11-10 | still incomplete in the table | 6 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2018-11-12 | still incomplete in the table | 18 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2018-12-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2018-12-23 | still incomplete in the table | 22 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-02-02 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-02-06 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-03-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-03-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-03-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-03-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-03-09 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-03-10 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-03-11 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-03-15 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-03-16 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-03-17 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-03-22 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-03-23 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-03-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-03-29 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-03-30 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-03-31 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-04-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-04-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-04-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-04-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-04-13 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-04-14 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-04-17 | still incomplete in the table | 17 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-04-18 | still incomplete in the table | 20 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-04-19 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-04-20 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-04-21 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-04-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-04-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-04-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-05-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-05-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-05-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-05-10 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-05-11 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-05-12 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-05-17 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-05-18 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-05-19 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-05-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-05-25 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-05-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-05-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-05-31 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-06-01 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-06-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-06-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-06-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-06-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-06-09 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-06-12 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-06-21 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-06-22 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-06-23 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-06-28 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-07-04 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-07-05 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-07-12 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-07-12 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-07-13 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-07-14 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-07-19 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-07-20 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-07-21 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-07-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-07-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-07-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-08-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-08-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-08-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-08-10 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-08-11 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-08-13 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-08-16 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-08-17 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-08-18 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-08-23 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-08-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-08-25 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-08-25 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-08-29 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-08-30 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-08-31 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-09-01 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-09-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-09-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-09-13 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-09-14 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-09-15 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-09-20 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-09-21 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-09-22 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-09-24 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-09-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-09-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-09-29 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-10-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-10-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-10-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-10-11 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-10-12 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-10-13 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-10-18 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-10-19 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-10-20 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-10-25 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-10-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-10-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-04 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-09 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-10 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-13 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-14 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-15 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-16 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-17 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-22 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-23 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-29 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-11-30 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-01 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-12 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-13 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-13 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-14 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-14 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-15 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-20 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-21 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-22 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-23 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-25 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2019-12-29 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-02-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-02-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-02-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-02-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-02-09 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-02-14 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-02-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-02-29 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-03-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-03-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-03-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-03-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-03-08 | still incomplete in the table | 6 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-03-09 | still incomplete in the table | 20 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-03-13 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-03-14 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-03-15 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-03-20 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-03-21 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-03-22 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-03-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-03-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-03-29 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-03-30 | still incomplete in the table | 21 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-04-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-04-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-04-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-04-10 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-04-11 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-04-12 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-04-17 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-04-18 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-04-19 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-04-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-04-25 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-04-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-05-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-05-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-05-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-05-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-05-09 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-05-10 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-05-15 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-05-16 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-05-17 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-05-22 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-05-23 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-05-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-05-25 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-05-29 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-05-30 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-05-31 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-06-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-06-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-06-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-06-12 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-06-13 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-06-14 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-06-18 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-06-19 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-06-20 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-06-21 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-06-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-06-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-06-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-07-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-07-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-07-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-07-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-07-10 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-07-11 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-07-12 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-07-17 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-07-18 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-07-19 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-07-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-07-25 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-07-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-07-31 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-03 | still incomplete in the table | 4 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-04 | still incomplete in the table | 20 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-09 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-10 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-14 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-15 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-16 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-21 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-22 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-23 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-29 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-08-30 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-09-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-09-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-09-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-09-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-09-11 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-09-12 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-09-13 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-09-18 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-09-19 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-10-09 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-10-10 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-10-11 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-10-16 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-10-17 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-10-18 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-10-23 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-10-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-10-25 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-10-30 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-10-31 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-10-31 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-11-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-11-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-11-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-11-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-11-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-11-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-11-13 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-11-14 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-11-15 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-11-20 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-11-21 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-11-22 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-11-25 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-11-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-11-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-11-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-11-29 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-12-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-12-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-12-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-12-11 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-12-12 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-12-13 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-12-18 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-12-19 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-12-20 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-12-23 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-12-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-12-25 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-12-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2020-12-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-02-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-02-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-03-01 | still incomplete in the table | 23 of 24 hours with co2_emissions_natural_gas; not written for this day |
| `eia930_all_emissions` | 2021-03-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-03-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-03-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-03-12 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-03-13 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-03-14 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-03-19 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-03-20 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-03-21 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-03-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-03-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-03-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-04-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-04-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-04-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-07-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-08-18 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-08-27 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-08-29 | still incomplete in the table | 22 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-08-30 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-08-31 | still incomplete in the table | 22 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-09-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-09-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-10-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-10-09 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-10-10 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-10-22 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-11-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-11-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-11-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-11-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-11-25 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-11-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-12-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-12-09 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-12-22 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-12-23 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-12-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-12-28 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-12-30 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2021-12-31 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-01-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-01-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-01-05 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-01-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-01-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-01-09 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-01-14 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-01-15 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-01-16 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-01-17 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-01-21 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-01-22 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-01-23 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-02-11 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-02-12 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-02-13 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-03-13 | still incomplete in the table | 6 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-03-14 | still incomplete in the table | 20 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-03-18 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-03-19 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-03-20 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-05-17 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-06-06 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-06-09 | still incomplete in the table | 22 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-06-13 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-10-01 | still incomplete in the table | 20 of 24 hours with co2_emissions_coal; not written for this day |
| `eia930_all_emissions` | 2022-10-02 | still incomplete in the table | 23 of 24 hours with co2_emissions_coal; not written for this day |
| `eia930_all_emissions` | 2022-11-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-11-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-11-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-11-07 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2022-11-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-03-12 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-03-13 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-04-13 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-10-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-10-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-10-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-10-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-10-12 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-10-31 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-11-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-11-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-11-05 | still incomplete in the table | 4 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-11-06 | still incomplete in the table | 19 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-11-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-11-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-11-14 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-11-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-12-25 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2023-12-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-01-17 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-01-18 | still incomplete in the table | 19 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-02-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-02-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-02-09 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-02-10 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-02-11 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-02-16 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-02-17 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-02-18 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-03-10 | still incomplete in the table | 6 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-03-11 | still incomplete in the table | 20 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-03-22 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-03-23 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-03-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-03-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-05-17 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-05-18 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-05-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-05-25 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-05-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-05-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-06-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-06-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-06-30 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-07-01 | still incomplete in the table | 5 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-07-02 | still incomplete in the table | 19 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-07-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-07-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-07-10 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-07-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-07-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-07-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-10-09 | still incomplete in the table | 20 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-10-10 | still incomplete in the table | 20 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-10-19 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-10-31 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-11-01 | still incomplete in the table | 7 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-11-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-11-03 | still incomplete in the table | 17 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-11-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-11-03 | still incomplete in the table | 4 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-11-04 | still incomplete in the table | 19 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-11-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2024-11-19 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-01-15 | still incomplete in the table | 22 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-01-16 | still incomplete in the table | 17 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-01-17 | still incomplete in the table | 19 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-03-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-03-08 | still incomplete in the table | 8 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-03-09 | still incomplete in the table | 16 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-07-01 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-07-02 | still incomplete in the table | 22 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-07-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-07-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-07-24 | still incomplete in the table | 6 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-07-25 | still incomplete in the table | 19 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-09-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-09-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-09-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-10-31 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-11-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-11-01 | still incomplete in the table | 7 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-11-02 | still incomplete in the table | 17 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-11-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-11-02 | still incomplete in the table | 4 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-11-03 | still incomplete in the table | 19 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-11-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-11-14 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-11-15 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-11-16 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-11-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-11-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-11-29 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-11-30 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-04 | still incomplete in the table | 6 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-06 | still incomplete in the table | 18 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-09 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-10 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-11 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-12 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-13 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-14 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-15 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-16 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-17 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-18 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-19 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-20 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-21 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-22 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-23 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-25 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-29 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-30 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2025-12-31 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-09 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-10 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-11 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-12 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-13 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-14 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-15 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-16 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-17 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-18 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-19 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-20 | still incomplete in the table | 6 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-21 | still incomplete in the table | 18 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-22 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-23 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-24 | still incomplete in the table | 15 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-25 | still incomplete in the table | 22 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-25 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-29 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-30 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-30 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-01-31 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-01 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-09 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-09 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-09 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-10 | still incomplete in the table | 19 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-10 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-10 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-11 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-12 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-13 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-14 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-15 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-16 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-17 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-18 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-18 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-19 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-20 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-21 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-22 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-23 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-25 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-02-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-03-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-03-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-03-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-03-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-03-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-03-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-03-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-03-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-03-07 | still incomplete in the table | 8 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-03-08 | still incomplete in the table | 16 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-03-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-03-08 | still incomplete in the table | 6 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-03-09 | still incomplete in the table | 20 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-03-09 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-03-27 | still incomplete in the table | 21 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-04-23 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-05-04 | still incomplete in the table | 17 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-05-05 | still incomplete in the table | 20 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-05-20 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-05-21 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-05-22 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-05-23 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-05-24 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-05-25 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-05-26 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-05-27 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-05-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-05-29 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-05-30 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-05-31 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-06-01 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-06-02 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-06-03 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-06-04 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-06-05 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-06-06 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-06-07 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-06-08 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-06-09 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-06-10 | still incomplete in the table | 20 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-06-25 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-07-01 | still incomplete in the table | 23 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-08-25 | still incomplete in the table | 22 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-09-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-09-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-09-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-09-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-09-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-09-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-09-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | 2026-09-28 | still incomplete in the table | 24 of 24 hours with CO2 values; day not written |
| `eia930_all_emissions` | ciso 2018-07-20..2026-08-19 | a range recorded by a history build (run_status.csv) | 275 UTC days without 24 hours with co2_emissions_coal, not written (first 2018-07-20, 2019-05-28, 2019-08-25; last 2026-08-19) |
| `eia930_all_emissions` | ciso 2018-07-20..2026-08-20 | a range recorded by a history build (run_status.csv) | 10 UTC days without 24 hours with co2_emissions_natural_gas, not written (first 2018-07-20, 2019-08-25, 2019-12-19; last 2026-08-20) |
| `eia930_all_emissions` | ciso 2018-07-20..2026-09-27 | a range recorded by a history build (run_status.csv) | 189 UTC days without 24 hours with co2_emissions_oil, not written (first 2018-07-20, 2019-03-15, 2019-03-16; last 2026-09-27) |
| `eia930_all_emissions` | isne 2024-07-19..2026-09-27 | a range recorded by a history build (run_status.csv) | 366 UTC days without 24 hours with co2_emissions_coal, not written (first 2024-07-19, 2024-07-20, 2024-07-21; last 2026-09-27) |
| `eia930_all_emissions` | isne 2024-09-06..2026-09-27 | a range recorded by a history build (run_status.csv) | 318 UTC days without 24 hours with co2_emissions_oil, not written (first 2024-09-06, 2024-09-07, 2024-09-08; last 2026-09-27) |
| `eia930_all_emissions` | miso 2018-07-02..2026-09-27 | a range recorded by a history build (run_status.csv) | 2982 UTC days without 24 hours with co2_emissions_oil, not written (first 2018-07-02, 2018-07-03, 2018-07-04; last 2026-09-27) |
| `eia930_all_storage` | 2024-07-15 | still incomplete in the table | net_generation_battery_mw: 19 of 24 hours; day not written |
| `eia930_all_storage` | 2024-07-16 | still incomplete in the table | net_generation_battery_mw: 5 of 24 hours; day not written |
| `eia930_all_storage` | 2024-07-17 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-07-18 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-07-19 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-07-20 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-07-21 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-07-22 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-07-23 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-07-24 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-07-25 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-07-26 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-07-27 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-07-28 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-07-29 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-07-30 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-07-31 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-01 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-02 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-03 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-04 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-05 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-06 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-07 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-08 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-09 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-10 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-11 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-12 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-13 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-14 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-15 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-16 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-17 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-18 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-19 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-20 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-21 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-22 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-23 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-24 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-25 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-26 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-27 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-28 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-29 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-30 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-08-31 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-01 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-02 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-03 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-04 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-05 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-06 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-07 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-08 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-09 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-10 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-11 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-12 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-13 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-14 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-15 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-16 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-17 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-18 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-19 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-20 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-21 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-22 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-23 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-24 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-25 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-26 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-27 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-28 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-29 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-09-30 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-01 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-02 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-03 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-04 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-05 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-06 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-07 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-08 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-09 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-10 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-11 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-12 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-13 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-14 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-15 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-16 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-17 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-18 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-19 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-20 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-21 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-22 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-23 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-24 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-25 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-26 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-27 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-28 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-29 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-30 | still incomplete in the table | net_generation_battery_mw: 0 of 24 hours; day not written |
| `eia930_all_storage` | 2024-10-31 | still incomplete in the table | net_generation_battery_mw: 17 of 24 hours; day not written |
| `eia930_all_storage` | 2024-11-06 | still incomplete in the table | net_generation_battery_mw: 18 of 24 hours; day not written |
| `eia930_all_storage` | 2024-11-06 | still incomplete in the table | net_generation_battery_mw: 19 of 24 hours; day not written |
| `eia930_all_storage` | 2025-01-15 | still incomplete in the table | net_generation_battery_mw: 19 of 24 hours; day not written |
| `eia930_all_storage` | 2025-12-05 | still incomplete in the table | net_generation_battery_mw: 6 of 24 hours; day not written |
| `eia930_all_storage` | 2025-12-06 | still incomplete in the table | net_generation_battery_mw: 18 of 24 hours; day not written |
| `eia930_all_storage` | 2026-02-04 | still incomplete in the table | net_generation_battery_mw: 18 of 24 hours; day not written |
| `eia930_ciso_generation` | 2026-09-28 | still incomplete in the table | net_generation_mw: 6 of 24 hours (18 missing, 0 published as null; first missing ['2026-09-28T06:00:00Z', '2026-09-28T07:00:00Z', '2026-09-2 |
| `eia930_erco_demand` | 2026-09-04 | still incomplete in the table | demand_forecast_mw: 5 of 24 hours (19 missing, 0 published as null; first missing ['2026-09-04T05:00:00Z', '2026-09-04T06:00:00Z', '2026-09- |
| `eia930_erco_demand` | 2026-09-05 | still incomplete in the table | demand_forecast_mw: 19 of 24 hours (5 missing, 0 published as null; first missing ['2026-09-05T00:00:00Z', '2026-09-05T01:00:00Z', '2026-09- |
| `eia930_erco_generation` | 2026-09-28 | still incomplete in the table | net_generation_mw: 4 of 24 hours (20 missing, 0 published as null; first missing ['2026-09-28T04:00:00Z', '2026-09-28T05:00:00Z', '2026-09-2 |
| `eia930_isne_generation` | 2026-09-28 | still incomplete in the table | net_generation_mw: 3 of 24 hours (21 missing, 0 published as null; first missing ['2026-09-28T03:00:00Z', '2026-09-28T04:00:00Z', '2026-09-2 |
| `eia930_miso_generation` | 2026-09-28 | still incomplete in the table | net_generation_mw: 4 of 24 hours (20 missing, 0 published as null; first missing ['2026-09-28T04:00:00Z', '2026-09-28T05:00:00Z', '2026-09-2 |
| `eia930_nyis_demand` | 2026-09-04 | still incomplete in the table | demand_forecast_mw: 4 of 24 hours (20 missing, 0 published as null; first missing ['2026-09-04T04:00:00Z', '2026-09-04T05:00:00Z', '2026-09- |
| `eia930_nyis_demand` | 2026-09-05 | still incomplete in the table | demand_forecast_mw: 20 of 24 hours (4 missing, 0 published as null; first missing ['2026-09-05T00:00:00Z', '2026-09-05T01:00:00Z', '2026-09- |
| `eia930_nyis_generation` | 2026-09-28 | still incomplete in the table | net_generation_mw: 3 of 24 hours (21 missing, 0 published as null; first missing ['2026-09-28T03:00:00Z', '2026-09-28T04:00:00Z', '2026-09-2 |
| `eia930_pjm_generation` | 2026-09-28 | still incomplete in the table | net_generation_mw: 3 of 24 hours (21 missing, 0 published as null; first missing ['2026-09-28T03:00:00Z', '2026-09-28T04:00:00Z', '2026-09-2 |
| `eia930_swpp_generation` | 2026-09-28 | still incomplete in the table | net_generation_mw: 4 of 24 hours (20 missing, 0 published as null; first missing ['2026-09-28T04:00:00Z', '2026-09-28T05:00:00Z', '2026-09-2 |
| `eia930_us48_generation` | 2026-09-28 | still incomplete in the table | net_generation_mw: 3 of 24 hours (21 missing, 0 published as null; first missing ['2026-09-28T03:00:00Z', '2026-09-28T04:00:00Z', '2026-09-2 |
| `isone_rtm_zone_prices` | 2026-09-02 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-03T03:45:00Z']), extra 0; .Z.CONNECTICUT: 95 rows, expecte |
| `isone_rtm_zone_prices` | 2026-09-11 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-12T03:45:00Z']), extra 0; .Z.CONNECTICUT: 95 rows, expecte |
| `isone_rtm_zone_prices` | 2026-09-12 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-12T04:15:00Z']), extra 0; .Z.CONNECTICUT: 95 rows, expecte |
| `isone_rtm_zone_prices` | 2026-09-13 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 94 rows, expected 96, missing 2 (first ['2026-09-13T04:00:00Z', '2026-09-13T04:15:00Z']), extra 0; .Z.CONNE |
| `isone_rtm_zone_prices` | 2026-09-15 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 88 rows, expected 96, missing 8 (first ['2026-09-15T18:00:00Z', '2026-09-15T18:15:00Z', '2026-09-15T18:30:0 |
| `isone_rtm_zone_prices` | 2026-09-25 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-25T17:15:00Z']), extra 0; .Z.CONNECTICUT: 95 rows, expecte |
