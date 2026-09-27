# ERW status

Generated 2026-09-27 09:51 UTC by `warehouse/metadata/build_status.py`, which the daily run regenerates after coverage; the daily workflow commits it. Every number below is read from `warehouse/metadata/coverage.csv`, `warehouse/metadata/run_status.csv` or Supabase.

## Tables

| | Tables | Rows |
|---|---|---|
| All | 87 | 3,810,914 |
| Public | 79 | 3,684,967 |
| Internal (never shown publicly) | 8 | 125,947 |

Newest table refresh: 2026-09-27 09:46:50 UTC. Validator: 87 of 87 tables pass. Per-table detail: [`docs/coverage.md`](docs/coverage.md).

## Last runs

| Workflow | Last run (UTC) | Outcome |
|---|---|---|
| daily prices, on GitHub | 2026-09-27 09:51 | 184 ok, 24 failed, 22 gap, 5 skipped (table results of that day) |
| daily run, local | 2026-09-27 04:42 | 137 ok, 10 failed, 10 gap (table results of that day) |
| latest prices, every 15 minutes | 2026-09-27 06:01 | 39 hubs and zones in `latest_prices` (newest retrieval) |

A table that failed is not written that day; nothing partial is. The reasons are in `warehouse/metadata/run_status.csv`.

## Tables whose last run failed

| Table | Run | Reason |
|---|---|---|
| `carb_auction_allowance_prices` | 20260927T094001Z | RuntimeError: CARB auction summary PDF failed after 4 attempts: RuntimeError('CARB auction summary PDF HTTP 202') |
| `ercot_large_load_queue` | 20260927T094319Z | iso_prices.SourceGap: ERCOT publishes no request-level large-load list: https://www.ercot.com/services/rq/large-load-integration links 3 spreadsheets, none a st |
| `nyiso_interconnection_queue` | 20260927T094201Z | RuntimeError: nyiso queue failed after 4 attempts: RuntimeError('GET https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx failed: <Res |

## Open gaps

Days a per-day connector could not write complete, re-checked against the table with the connector's own completeness rule. Recorded gap days: 21; filled since: 0; open: 21.

| Table | Day | State | First recorded reason |
|---|---|---|---|
| `eia930_ciso_generation` | 2026-09-26 | still incomplete in the table | net_generation_mw: 6 of 24 hours (18 missing, 0 published as null; first missing ['2026-09-26T06:00:00Z', '2026-09-26T07:00:00Z', '2026-09-2 |
| `eia930_erco_demand` | 2026-09-04 | still incomplete in the table | demand_forecast_mw: 5 of 24 hours (19 missing, 0 published as null; first missing ['2026-09-04T05:00:00Z', '2026-09-04T06:00:00Z', '2026-09- |
| `eia930_erco_demand` | 2026-09-05 | still incomplete in the table | demand_forecast_mw: 19 of 24 hours (5 missing, 0 published as null; first missing ['2026-09-05T00:00:00Z', '2026-09-05T01:00:00Z', '2026-09- |
| `eia930_erco_generation` | 2026-09-26 | still incomplete in the table | net_generation_mw: 4 of 24 hours (20 missing, 0 published as null; first missing ['2026-09-26T04:00:00Z', '2026-09-26T05:00:00Z', '2026-09-2 |
| `eia930_isne_generation` | 2026-09-26 | still incomplete in the table | net_generation_mw: 3 of 24 hours (21 missing, 0 published as null; first missing ['2026-09-26T03:00:00Z', '2026-09-26T04:00:00Z', '2026-09-2 |
| `eia930_miso_generation` | 2026-09-26 | still incomplete in the table | net_generation_mw: 4 of 24 hours (20 missing, 0 published as null; first missing ['2026-09-26T04:00:00Z', '2026-09-26T05:00:00Z', '2026-09-2 |
| `eia930_nyis_demand` | 2026-09-04 | still incomplete in the table | demand_forecast_mw: 4 of 24 hours (20 missing, 0 published as null; first missing ['2026-09-04T04:00:00Z', '2026-09-04T05:00:00Z', '2026-09- |
| `eia930_nyis_demand` | 2026-09-05 | still incomplete in the table | demand_forecast_mw: 20 of 24 hours (4 missing, 0 published as null; first missing ['2026-09-05T00:00:00Z', '2026-09-05T01:00:00Z', '2026-09- |
| `eia930_nyis_generation` | 2026-09-26 | still incomplete in the table | net_generation_mw: 3 of 24 hours (21 missing, 0 published as null; first missing ['2026-09-26T03:00:00Z', '2026-09-26T04:00:00Z', '2026-09-2 |
| `eia930_pjm_generation` | 2026-09-26 | still incomplete in the table | net_generation_mw: 3 of 24 hours (21 missing, 0 published as null; first missing ['2026-09-26T03:00:00Z', '2026-09-26T04:00:00Z', '2026-09-2 |
| `eia930_swpp_generation` | 2026-09-26 | still incomplete in the table | net_generation_mw: 4 of 24 hours (20 missing, 0 published as null; first missing ['2026-09-26T04:00:00Z', '2026-09-26T05:00:00Z', '2026-09-2 |
| `eia930_us48_generation` | 2026-09-26 | still incomplete in the table | net_generation_mw: 3 of 24 hours (21 missing, 0 published as null; first missing ['2026-09-26T03:00:00Z', '2026-09-26T04:00:00Z', '2026-09-2 |
| `isone_rtm_zone_prices` | 2026-09-02 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-03T03:45:00Z']), extra 0; .Z.CONNECTICUT: 95 rows, expecte |
| `isone_rtm_zone_prices` | 2026-09-11 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-12T03:45:00Z']), extra 0; .Z.CONNECTICUT: 95 rows, expecte |
| `isone_rtm_zone_prices` | 2026-09-12 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-12T04:15:00Z']), extra 0; .Z.CONNECTICUT: 95 rows, expecte |
| `isone_rtm_zone_prices` | 2026-09-13 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 94 rows, expected 96, missing 2 (first ['2026-09-13T04:00:00Z', '2026-09-13T04:15:00Z']), extra 0; .Z.CONNE |
| `isone_rtm_zone_prices` | 2026-09-15 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 88 rows, expected 96, missing 8 (first ['2026-09-15T18:00:00Z', '2026-09-15T18:15:00Z', '2026-09-15T18:30:0 |
| `isone_rtm_zone_prices` | 2026-09-25 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-25T17:15:00Z']), extra 0; .Z.CONNECTICUT: 95 rows, expecte |
| `isone_rtm_zone_prices_hourly` | 2026-09-25 | still incomplete in the table | RTM_HOURLY 2026-09-25 failed after 4 attempts: EmptyDataError('No columns to parse from file') |
| `isone_rtm_zone_prices_hourly` | 2026-09-26 | still incomplete in the table | RTM_HOURLY 2026-09-26 failed after 4 attempts: EmptyDataError('No columns to parse from file') |
| `miso_rtm_hub_prices` | 2026-09-26 | still incomplete in the table | MISO has published neither the final nor the prelim real-time LMP file for 2026-09-26 (HTTP 404) |
