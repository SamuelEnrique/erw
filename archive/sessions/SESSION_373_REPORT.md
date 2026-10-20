# Session 373 report: this machine restored from the archive

20 October 2026, unattended, on lab-desktop (the data machine), the first session of the chain of 20 October, day. The precheck passed at the start of the day; the tables were restored into a staging folder earlier in the day, while the daily run held the data lock, and put in place under the lock from 20:01 UTC, after that lock lapsed at 20:00:05 UTC (below). Model spend USD 0. Pulls: none from a publisher; the ERW archive's bucket read (the run log, and each table's runs).

## Read these first

- **All 71 tables of `docs/state/archive_proof_2026-10-20.csv` (24 behind, 47 that differ only by the archive's revisions) are the archive's latest run now**, each validated (`erw_validate.py`, exit 0) and its coverage row rebuilt with `--only` (exit 0; 21 rows of `coverage.csv` changed). This machine's copies are kept in `runs/s373_before/`, not deleted.
- **`scripts/sync.py --check` before and after:** at 17:13 UTC (the daily run's own `dm_sync`): 156 current, 49 behind, 1 ahead, 2 diverged, 1 not on Redivis. At 20:19 UTC: **201 current**, 1 behind (`api_cost_ledger`: the same 3,710 rows, Redivis's newest entry 38 minutes later), 2 ahead (`eia930_all_storage`, `eia930_generation_latest`), 2 diverged (`grid_network_links`, `price_board_latest`), 3 not on Redivis (`ercot_all_hub_prices_history`, `node_basis_daily`, `nyiso_load_queue`).
- **The row counts did not move** (the table below): the daily run's `dm_sync` at 17:13 UTC had already brought the 24 behind tables level with Redivis before the swap. **What moved is the values: 26 of the 71 now hold the archive's revisions** (the other 45 were already byte for byte the archive's data).
- **The daily run of 20 October did not finish.** Its scheduled task ended at 18:06 UTC with 0xC000013A (STATUS_CONTROL_C_EXIT), in `dm_battery_scenario_steps`, and never released the lock, which lapsed by itself at 20:00:05 UTC; it was not broken. That step had failed at 18:02 UTC on a stale `battery_stack_monthly` ("caiso foresight 2h: the default cell is not battery_stack_monthly: 2023-11 ..."), one of the tables this session restored. **Its page files were left uncommitted in the main checkout** and are still there (with its metadata, in the named stash below and the working tree): this chain committed none of them.
- Session 374 found 8 more tables older here than the archive's latest run and restored them the same way (its report); with the third machine's two tables, 81 tables in all.

## Rows before and after

| Table | Rows before | Rows after | Archive run | Data |
|---|---|---|---|---|
| `caiso_as_prices` | 228,672 | 228,672 | `20261020T063359Z-github` | same |
| `caiso_curtailment_daily` | 25,096 | 25,096 | `20261020T063359Z-github` | same |
| `caiso_fuel_supply` | 156,000 | 156,000 | `20261020T063359Z-github` | same |
| `eia930_all_interchange` | 262,512 | 262,512 | `20261020T063359Z-github` | same |
| `eia930_daily_interchange` | 951,150 | 951,150 | `20261020T063359Z-github` | same |
| `eia_fuel_spot_prices` | 27,754 | 27,754 | `20261020T063359Z-github` | same |
| `eia_petroleum_stocks_weekly` | 16,823 | 16,823 | `20261020T063359Z-github` | same |
| `eia_petroleum_trade_weekly` | 12,586 | 12,586 | `20261020T063359Z-github` | same |
| `eia_product_spot_prices` | 72,052 | 72,052 | `20261020T063359Z-github` | same |
| `ercot_as_prices_daily` | 70,445 | 70,445 | `20261020T011604Z-github` | same |
| `ercot_dam_esr_awards` | 1,945,677 | 1,945,677 | `20261020T063359Z-github` | same |
| `ercot_hub_prices_daily` | 346,476 | 346,476 | `20261020T063359Z-github` | same |
| `ercot_storage_dam_offers_daily` | 20,046 | 20,046 | `20261020T063359Z-github` | same |
| `ercot_wind_solar_hsl_daily` | 180 | 180 | `20261020T063359Z-github` | same |
| `frb_treasury_yields` | 5,847 | 5,847 | `20261020T063359Z-github` | same |
| `iso_dam_hub_prices` | 22,224 | 22,224 | `20261020T063359Z-github` | same |
| `iso_rtm_hub_prices` | 57,312 | 57,312 | `20261020T063359Z-github` | same |
| `isone_dam_zone_prices` | 12,096 | 12,096 | `20261020T063359Z-github` | same |
| `isone_rtm_zone_prices` | 38,880 | 38,880 | `20261020T063359Z-github` | same |
| `large_load_rules_internal` | 74 | 74 | `20261020T011604Z-github` | same |
| `nyiso_dam_zone_prices` | 14,784 | 14,784 | `20261020T063359Z-github` | same |
| `nyiso_rtm_zone_prices` | 57,024 | 57,024 | `20261020T063359Z-github` | same |
| `policy_reads_evidence` | 3,362 | 3,362 | `20261020T011604Z-github` | same |
| `spp_curtailment_daily` | 38,392 | 38,392 | `20261020T063359Z-github` | same |
| `battery_stack_monthly` | 11,556 | 11,556 | `20261020T063359Z-github` | revised by the archive |
| `caiso_battery_storage` | 362,016 | 362,016 | `20261020T063359Z-github` | same |
| `caiso_interconnection_queue` | 2,278 | 2,278 | `20261019T211146Z-github` | revised by the archive |
| `carbon_intensity_daily` | 46,932 | 46,932 | `20261020T063359Z-github` | same |
| `carbon_intensity_hourly` | 1,126,793 | 1,126,793 | `20261020T063359Z-github` | same |
| `carbon_intensity_monthly` | 1,275 | 1,275 | `20261020T063359Z-github` | revised by the archive |
| `datacenter_operator_sites` | 275 | 275 | `20261019T211146Z-github` | revised by the archive |
| `datacenter_queue_positions` | 11 | 11 | `20261019T211146Z-github` | revised by the archive |
| `eia930_all_demand` | 20,640 | 20,640 | `20261020T063359Z-github` | same |
| `eia930_all_emissions` | 4,345,896 | 4,345,896 | `20261020T063359Z-github` | same |
| `eia930_all_generation` | 107,208 | 107,208 | `20261020T063359Z-github` | same |
| `eia930_daily_demand` | 191,583 | 191,583 | `20261020T063359Z-github` | same |
| `eia930_demand_growth` | 24,108 | 24,108 | `20261005T021655Z-local` | revised by the archive |
| `energy_deals_evidence` | 543 | 543 | `20261020T011604Z-github` | revised by the archive |
| `energy_projects` | 39,786 | 39,786 | `20261019T211146Z-github` | same |
| `ercot_as_prices` | 338,132 | 338,132 | `20261020T063359Z-github` | same |
| `ercot_as_prices_monthly` | 2,325 | 2,325 | `20261020T011604Z-github` | revised by the archive |
| `ercot_interconnection_queue` | 1,805 | 1,805 | `20261019T211146Z-github` | revised by the archive |
| `ercot_storage_dam_awards_monthly` | 252 | 252 | `20261020T063359Z-github` | revised by the archive |
| `ercot_storage_dam_offers_monthly` | 819 | 819 | `20261020T063359Z-github` | revised by the archive |
| `ercot_wind_solar_hsl_hourly` | 7,920 | 7,920 | `20261020T063359Z-github` | same |
| `ercot_wind_solar_output_hourly` | 52,608 | 52,608 | `20261020T063359Z-github` | revised by the archive |
| `ferc_eqr_contracts_history` | 574,165 | 574,165 | `20261009T221405Z-local` | revised by the archive |
| `imf_commodity_prices` | 465 | 465 | `20261020T063359Z-github` | revised by the archive |
| `iso_all_capacity_prices` | 814 | 814 | `20261004T023527Z-local` | revised by the archive |
| `iso_curtailment_monthly` | 3,232 | 3,232 | `20261020T063359Z-github` | revised by the archive |
| `iso_hub_prices_history` | 595,512 | 595,512 | `20261020T063359Z-github` | same |
| `iso_trader_daily` | 15,693 | 15,693 | `20261020T063359Z-github` | same |
| `isone_dam_cleared_energy` | 960 | 960 | `20261020T011604Z-github` | revised by the archive |
| `isone_ddg_undelivered_monthly` | 840 | 840 | `20261007T221509Z-local` | revised by the archive |
| `isone_interconnection_queue` | 1,751 | 1,751 | `20261019T211146Z-github` | revised by the archive |
| `isone_rtm_zone_prices_hourly` | 11,016 | 11,016 | `20261020T063359Z-github` | same |
| `lbnl_interconnection_queue` | 38,201 | 38,201 | `20261004T023527Z-local` | revised by the archive |
| `miso_interconnection_queue` | 3,881 | 3,881 | `20261004T023527Z-local` | revised by the archive |
| `news_index` | 15,847 | 15,847 | `20261020T063359Z-github` | revised by the archive |
| `news_stories` | 21,087 | 21,087 | `20261020T063359Z-github` | revised by the archive |
| `nyiso_interconnection_queue` | 1,814 | 1,814 | `20261004T023527Z-local` | revised by the archive |
| `nyiso_load_queue` | 74 | 74 | `20261007T100923Z-local` | revised by the archive |
| `policy_actions` | 1,926 | 1,926 | `20261020T063359Z-github` | same |
| `policy_reads` | 385 | 385 | `20261020T011604Z-github` | same |
| `portwatch_chokepoint_transits` | 119,322 | 119,322 | `20261020T063359Z-github` | revised by the archive |
| `price_board_peak_offpeak` | 3,717 | 3,717 | `20261020T063359Z-github` | same |
| `price_board_spreads` | 2,408 | 2,408 | `20261020T063359Z-github` | same |
| `spp_interconnection_queue` | 3,080 | 3,080 | `20261019T211146Z-github` | same |
| `storage_daily_cycle` | 14,389 | 14,389 | `20261020T063359Z-github` | same |
| `weather_forecast_hourly` | 9,480 | 9,480 | `20261020T063359Z-github` | same |
| `weather_obs_hourly` | 9,624 | 9,624 | `20261020T063359Z-github` | same |

| Table (session 374) | Rows before | Rows after | Archive run | Data |
|---|---|---|---|---|
| `nlr_jedi_multipliers` | none | 5,562 | `20261020T084621Z-local` | new here |
| `impact_tax_rules` | none | 49 | `20261020T083547Z-local` | new here |
| `eia860m_retired_generators` | 249 | 249 | `20261020T063359Z-github` | revised by the archive |
| `eia930_generation_latest` | 2,410 | 1,906 | `20261020T063359Z-github` | revised by the archive |
| `eia_retail_sales_monthly` | 228,203 | 228,203 | `20261019T211146Z-github` | revised by the archive |
| `eia_sector_energy_consumption_monthly` | 8,988 | 8,988 | `20261019T211146Z-github` | revised by the archive |
| `price_board_carbon` | 15 | 15 | `20261020T063359Z-github` | revised by the archive |
| `price_board_latest` | 3,276 | 3,237 | `20261020T063359Z-github` | revised by the archive |
| `storage_buildout_monthly` | 21,229 | 21,229 | `20261020T063359Z-github` | revised by the archive |
| `storage_capacity` | 1,627 | 1,627 | `20261020T063359Z-github` | revised by the archive |

"Revised by the archive": the data (the rows below the header, `warehouse/archive/archive.py`'s `data_sha256`) differs from this machine's copy before. The staged copy of 68 of the 71 was restored a second time just before the swap: its SHA-256 did not equal the run log's (the archive had a newer run of 20 October 06:33 UTC, or a rebuilt table's bytes differ from the run's own file), and the swap restores again rather than put in place a copy it cannot match.

## Checks

| What | Exit | Notes |
|---|---|---|
| `runs/s373_swap.py runs/s373_restore runs/s373_tables.txt` (under the lock) | 0 | 71 of 71 in place, 20:01 to 20:11 UTC |
| `warehouse/validate/erw_validate.py` on the 71 | 0 | |
| `warehouse/metadata/build_coverage.py --only '^(the 71)$'` | 0 | the first run rebuilt 1 row, not 71: the list of names had Windows line endings, so 70 names in the expression ended in a carriage return; run again with them stripped: 71 rebuilt, 138 carried over |
| `scripts/sync.py --check` | 0 | the counts above |

## Decisions made without you

1. **The restore waited for the lock** rather than writing beside the daily run: the staged copies were made while it held the lock (they are not data writes: `runs/`), and the swap ran only once the lock had lapsed by itself.
2. **The staged copy is checked against the run log at the swap**, and restored again when it does not match, so a run archived after the staging is the one put in place.
3. **This machine's old copies are kept** in `runs/s373_before/` (rule 3), for a person to delete.

## For Samuel's ruling

- The daily run's page files of 20 October, uncommitted in the main checkout: tomorrow's run rebuilds and commits them; nothing is lost by leaving them.

## Files

- New on this machine (not in git): `runs/s373_restore/` (emptied by the swap), `runs/s373_before/` (79 old copies: the 71, and session 374's 8), `runs/s373_rows.csv`, `runs/s373_swap.py`, `runs/s373_drive.py`, the outputs `runs/s373_*.out`.
- Changed: `warehouse/metadata/coverage.csv`, `docs/coverage.md` (commit `ea853c8b`, with sessions 374 and 376's rows); this report.
