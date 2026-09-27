# ERW status

Generated 2026-09-27 03:23 UTC by `warehouse/metadata/build_status.py`, which the daily run regenerates after coverage; the daily workflow commits it. Every number below is read from `warehouse/metadata/coverage.csv`, `warehouse/metadata/run_status.csv` or Supabase.

## Tables

| | Tables | Rows |
|---|---|---|
| All | 86 | 3,802,684 |
| Public | 78 | 3,680,082 |
| Internal (never shown publicly) | 8 | 122,602 |

Newest table refresh: 2026-09-27 03:19:47 UTC. Validator: 86 of 86 tables pass. Per-table detail: [`docs/coverage.md`](docs/coverage.md).

## Last runs

| Workflow | Last run (UTC) | Outcome |
|---|---|---|
| daily prices, on GitHub | 2026-09-27 03:22 | 82 ok, 21 failed, 10 gap, 3 skipped (table results of that day) |
| daily run, local | 2026-09-27 02:23 | 121 ok, 8 failed, 8 gap (table results of that day) |
| latest prices, every 15 minutes | 2026-09-27 00:54 | 39 hubs and zones in `latest_prices` (newest retrieval) |

A table that failed is not written that day; nothing partial is. The reasons are in `warehouse/metadata/run_status.csv`.

## Tables whose last run failed

| Table | Run | Reason |
|---|---|---|
| `carb_auction_allowance_prices` | 20260927T031351Z | RuntimeError: CARB auction summary PDF failed after 4 attempts: RuntimeError('CARB auction summary PDF HTTP 202') |
| `news_stories` | 20260927T031740Z | RuntimeError("feed Hydrogen Insight failed after 3 attempts: RuntimeError('HTTP 503')") |
| `nyiso_interconnection_queue` | 20260927T031605Z | RuntimeError: nyiso queue failed after 4 attempts: RuntimeError('GET https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx failed: <Res |
| `spp_rtm_hub_prices` | 20260927T030605Z | SourceGap: SPP has no daily RTBM file for 2026-09-23 and its interval file for 2026-09-23 16:20:00-05:00 is missing: SPP RTBM interval 2026-09-23 16:20:00-05:00 |

## Open gaps

Days a per-day connector could not write complete, re-checked against the table with the connector's own completeness rule. Recorded gap days: 19; filled since: 0; open: 19.

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
