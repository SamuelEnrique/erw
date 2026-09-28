# ERW status

Generated 2026-09-28 09:47 UTC by `warehouse/metadata/build_status.py`, which the daily run regenerates after coverage; the daily workflow commits it. Every number below is read from `warehouse/metadata/coverage.csv`, `warehouse/metadata/run_status.csv` or Supabase.

## Tables

| | Tables | Rows |
|---|---|---|
| All | 107 | 4,793,743 |
| Public | 99 | 4,659,653 |
| Internal (never shown publicly) | 8 | 134,090 |

Newest table refresh: 2026-09-28 08:35:35 UTC. Validator: 107 of 107 tables pass. Per-table detail: [`docs/coverage.md`](docs/coverage.md).

## Last runs

| Workflow | Last run (UTC) | Outcome |
|---|---|---|
| daily prices, on GitHub | 2026-09-27 18:27 | 290 ok, 32 failed, 25 gap, 8 skipped (table results of that day) |
| daily run, local | 2026-09-27 04:42 | 137 ok, 10 failed, 10 gap (table results of that day) |
| latest prices, every 15 minutes | 2026-09-28 06:51 | 39 hubs and zones in `latest_prices` (newest retrieval) |

A table that failed is not written that day; nothing partial is. The reasons are in `warehouse/metadata/run_status.csv`.

## Tables whose last run failed

| Table | Run | Reason |
|---|---|---|
| `caiso_trader_daily` | 20260927T180906Z | ValueError: You are trying to merge on object and float64 columns for key 'value'. If you wish to proceed you should use pd.concat |
| `carb_auction_allowance_prices` | 20260927T181629Z | RuntimeError: CARB auction summary PDF failed after 4 attempts: RuntimeError('CARB auction summary PDF HTTP 202') |
| `ercot_large_load_queue` | 20260927T094319Z | iso_prices.SourceGap: ERCOT publishes no request-level large-load list: https://www.ercot.com/services/rq/large-load-integration links 3 spreadsheets, none a st |
| `ercot_trader_daily` | 20260927T180906Z | ValueError: You are trying to merge on object and float64 columns for key 'value'. If you wish to proceed you should use pd.concat |
| `iso_rt_top_intervals` | 20260927T180906Z | iso_prices.SourceGap: no ISO has 7 complete real-time days |
| `isone_trader_daily` | 20260927T180906Z | ValueError: You are trying to merge on object and float64 columns for key 'value'. If you wish to proceed you should use pd.concat |
| `miso_trader_daily` | 20260927T180906Z | ValueError: You are trying to merge on object and float64 columns for key 'value'. If you wish to proceed you should use pd.concat |
| `nyiso_interconnection_queue` | 20260927T094201Z | RuntimeError: nyiso queue failed after 4 attempts: RuntimeError('GET https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx failed: <Res |
| `nyiso_trader_daily` | 20260927T180906Z | ValueError: You are trying to merge on object and float64 columns for key 'value'. If you wish to proceed you should use pd.concat |
| `spp_trader_daily` | 20260927T180906Z | ValueError: You are trying to merge on object and float64 columns for key 'value'. If you wish to proceed you should use pd.concat |

## Open gaps

Days a per-day connector could not write complete, re-checked against the table with the connector's own completeness rule. Recorded gap days: 21; filled since: 9; open: 12.

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
| `isone_rtm_zone_prices_hourly` | 2026-09-26 | still incomplete in the table | RTM_HOURLY 2026-09-26 failed after 4 attempts: EmptyDataError('No columns to parse from file') |
