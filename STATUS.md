# ERW status

Generated 2026-09-27 00:12 UTC by `warehouse/metadata/build_status.py`, which the daily run regenerates after coverage; the daily workflow commits it. Every number below is read from `warehouse/metadata/coverage.csv`, `warehouse/metadata/run_status.csv` or Supabase.

## Tables

| | Tables | Rows |
|---|---|---|
| All | 81 | 3,751,828 |
| Public | 75 | 3,629,472 |
| Internal (never shown publicly) | 6 | 122,356 |

Newest table refresh: 2026-09-26 23:32:06 UTC. Validator: 81 of 81 tables pass. Per-table detail: [`docs/coverage.md`](docs/coverage.md).

## Last runs

| Workflow | Last run (UTC) | Outcome |
|---|---|---|
| daily prices, on GitHub | none recorded | |
| daily run, local | 2026-09-26 23:32 | 101 ok, 1 failed, 17 gap (table results of that day) |
| latest prices, every 15 minutes | 2026-09-26 23:59 | 39 hubs and zones in `latest_prices` (newest retrieval) |

A table that failed is not written that day; nothing partial is. The reasons are in `warehouse/metadata/run_status.csv`.

## Tables whose last run failed

| Table | Run | Reason |
|---|---|---|
| `spp_rtm_hub_prices` | 20260925T234948Z | SourceGap: SPP has no daily RTBM file for 2026-09-22 and its interval file for 2026-09-22 14:05:00-05:00 is missing: SPP RTBM interval 2026-09-22 14:05:00-05:00 |

## Open gaps

Days a per-day connector could not write complete, re-checked against the table with the connector's own completeness rule. Recorded gap days: 11; filled since: 0; open: 11.

| Table | Day | State | First recorded reason |
|---|---|---|---|
| `eia930_erco_demand` | 2026-09-04 | still incomplete in the table | demand_forecast_mw: 5 of 24 hours (19 missing, 0 published as null; first missing ['2026-09-04T05:00:00Z', '2026-09-04T06:00:00Z', '2026-09- |
| `eia930_erco_demand` | 2026-09-05 | still incomplete in the table | demand_forecast_mw: 19 of 24 hours (5 missing, 0 published as null; first missing ['2026-09-05T00:00:00Z', '2026-09-05T01:00:00Z', '2026-09- |
| `eia930_nyis_demand` | 2026-09-04 | still incomplete in the table | demand_forecast_mw: 4 of 24 hours (20 missing, 0 published as null; first missing ['2026-09-04T04:00:00Z', '2026-09-04T05:00:00Z', '2026-09- |
| `eia930_nyis_demand` | 2026-09-05 | still incomplete in the table | demand_forecast_mw: 20 of 24 hours (4 missing, 0 published as null; first missing ['2026-09-05T00:00:00Z', '2026-09-05T01:00:00Z', '2026-09- |
| `isone_rtm_zone_prices` | 2026-09-02 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-03T03:45:00Z']), extra 0; .Z.CONNECTICUT: 95 rows, expecte |
| `isone_rtm_zone_prices` | 2026-09-11 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-12T03:45:00Z']), extra 0; .Z.CONNECTICUT: 95 rows, expecte |
| `isone_rtm_zone_prices` | 2026-09-12 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-12T04:15:00Z']), extra 0; .Z.CONNECTICUT: 95 rows, expecte |
| `isone_rtm_zone_prices` | 2026-09-13 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 94 rows, expected 96, missing 2 (first ['2026-09-13T04:00:00Z', '2026-09-13T04:15:00Z']), extra 0; .Z.CONNE |
| `isone_rtm_zone_prices` | 2026-09-15 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 88 rows, expected 96, missing 8 (first ['2026-09-15T18:00:00Z', '2026-09-15T18:15:00Z', '2026-09-15T18:30:0 |
| `isone_rtm_zone_prices` | 2026-09-25 | still incomplete in the table | day incomplete: .H.INTERNAL_HUB: 95 rows, expected 96, missing 1 (first ['2026-09-25T17:15:00Z']), extra 0; .Z.CONNECTICUT: 95 rows, expecte |
| `isone_rtm_zone_prices_hourly` | 2026-09-25 | still incomplete in the table | RTM_HOURLY 2026-09-25 failed after 4 attempts: EmptyDataError('No columns to parse from file') |
