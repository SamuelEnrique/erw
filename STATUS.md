# ERW status

Generated 2026-09-29 03:14 UTC by `warehouse/metadata/build_status.py`, which the daily run regenerates after coverage; the daily workflow commits it. Every number below is read from `warehouse/metadata/coverage.csv`, `warehouse/metadata/run_status.csv` or Supabase.

## Tables

| | Tables | Rows |
|---|---|---|
| All | 113 | 4,812,358 |
| Public | 104 | 4,675,663 |
| Internal (never shown publicly) | 9 | 136,695 |

Newest table refresh: 2026-09-29 03:01:41 UTC. Validator: 113 of 113 tables pass. Per-table detail: [`docs/coverage.md`](docs/coverage.md).

## Health gate

**Closed.** The latest daily run on GitHub (2026-09-28) has 2 failed tables outside the known-gap list below: `carb_auction_allowance_prices`, `nyiso_interconnection_queue`. While the gate is closed, no session adds a new source or a new tool (`PRIORITIES.md`); fixing the failures, or a human adding one to the list, opens it. `python warehouse/metadata/build_status.py --gate` exits 1 while it is closed.

### Known gaps

Failures a human has accepted for now (`warehouse/metadata/known_gaps.csv`, edited by hand). A table here does not close the gate.

| Table | Why | Since | Decided |
|---|---|---|---|
| `ercot_large_load_queue` | ERCOT publishes no request-level large-load list (Protocol 3.2.7 requires only an aggregate monthly report); the connector watches the page and fails loudly until one appears | 2026-09-27 | session 17 design; listed as a known gap in session 28 |

## Last runs

| Workflow | Last run (UTC) | Outcome |
|---|---|---|
| daily prices, on GitHub | 2026-09-28 23:52 | 280 ok, 7 failed, 2 gap, 10 skipped (table results of that day) |
| daily run, local | 2026-09-29 01:14 | 120 ok, 2 failed, 9 gap (table results of that day) |
| latest prices, every 15 minutes | 2026-09-29 00:45 | 39 hubs and zones in `latest_prices` (newest retrieval) |

A table that failed is not written that day; nothing partial is. The reasons are in `warehouse/metadata/run_status.csv`.

## Tables whose last run failed

| Table | Run | Reason |
|---|---|---|
| `eia930_swpp_demand` | 20260929T005739Z | RuntimeError: incomplete data, no file written for eia930_swpp_demand: demand_forecast_mw: 53 of 72 hours (19 missing, 0 published as null; first missing ['2026 |
| `eia_sector_energy_consumption_monthly` | 20260929T005932Z | RuntimeError: eia_sector_energy_consumption_monthly: newest date 2026-05-01 is 151 days old (limit 150); not writing a stale table |
| `ercot_large_load_queue` | 20260928T234003Z | iso_prices.SourceGap: ERCOT publishes no request-level large-load list: https://www.ercot.com/services/rq/large-load-integration links 3 spreadsheets, none a st |
| `nyiso_interconnection_queue` | 20260928T233903Z | RuntimeError: nyiso queue failed after 4 attempts: RuntimeError('GET https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx failed: <Res |

## Open gaps

Days a per-day connector could not write complete, re-checked against the table with the connector's own completeness rule. Recorded gap days: 29; filled since: 11; open: 18.

| Table | Day | State | First recorded reason |
|---|---|---|---|
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
