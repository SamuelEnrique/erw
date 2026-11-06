# Redivis version 1 on the Stanford dataset: read and planned

Energy Research Warehouse (ERW), session 660 (chain 043, run on 22 October 2026 UTC), for Samuel. **Nothing was uploaded, created, changed or released on Redivis in this session.** 13 requests to Redivis's API, all reads (ceiling 30).

## Which dataset the token reaches

- **The token in `.env` (`REDIVIS_API_TOKEN`) belongs to the user `samuelca`** (Redivis's `/users/me`), the account `config.yaml` names through `REDIVIS_OWNER`.
- **It reaches the Stanford dataset, with edit access.** The owner's reference `erw:b9wm` is the Datapages organization's dataset `datapages.erw:b9wm` (Redivis's own answer: owner `datapages`, kind organization, full name Datapages; address `https://stanford.redivis.com/datasets/b9wm-3hb080mtm`; DOI `10.57761/4f55-6d55`; `accessLevel: edit`; public access `data`). Datapages is the organization the session 59 starter was made for (Ben Domingue's).
- **It already has a released version, v1.0, with one table and no draft.** The table is `eia930_iso_hourly_demand_2019_2025` (429,525 rows, 31.5 MB, 8 variables): the starter dataset of session 59 (`exports/redivis-starter/`). So the ERW's first full release there will be Redivis's second version of `datapages.erw` (Redivis numbers it when it is released), and the draft opened by the first upload starts from v1.0's table. Session 661 leaves that table as it is: it is released, and removing it is the owner's or Ben's choice (under "For Samuel" below).
- **The old dataset** `samuelca.energy_research_warehouse:05yh` (the user account's) is reached too: its draft holds 184 tables, 8.24 GB by Redivis's sizes, never released. Its free 10 GB is full (sessions 363, 385).
- **The organization's storage limit is not reported by the API.** `GET /organizations/datapages` is not an API endpoint (404, "Invalid API endpoint"), and no dataset answer carries a quota. The limit is learned only from a refusal: the uploader reads Redivis's "exceed its free storage allotment" as a skip (session 377), so a batch that reaches it stops and names what is left.

## The reconcile, read only

`upload.py --reconcile` was not run as written: it opens each dataset's draft with `create_next_version(if_not_exists=True)`, and the Stanford dataset has no draft, so it would have created one (a write); against the old dataset it asks one `count(*)` a table (223 tables, beyond the ceiling of 30). The read-only equivalent: the Stanford dataset holds 0 of the 186 ERW tables below, and its one table is not an ERW table. The old draft's list was read whole (2 requests) and is the "In the old draft" column below. Session 661 runs `--reconcile` against the Stanford draft once it exists.

## How the uploader reaches the Stanford dataset (session 661 makes it)

Decided here, reversible: **a second target in `config.yaml`, not a change of the default.** `upload.py --target stanford` uploads to `datapages.erw` (owner kind organization), with its own manifest (`warehouse/metadata/redivis_uploads_stanford.csv`), and refuses any table whose ERW verdict in `docs/licenses.md` ("Every table") is not `public`, whatever `coverage.csv`'s flag says; internal tables are never routed there. The daily run keeps its default target (the old account's draft) until the owner rules, because three things read the default and each changes with it: the daily's `--changed` upload (it would start uploading to the Stanford draft every day), `--check-license` after it (the starter table is not an ERW table and would fail it), and the restore of rolling-window tables (`restore_tables.py` asks the old draft last, and several rolling tables are unsettled and would not be on the Stanford one).

## The tables to upload: 186, 13.25 GB of CSV

Every table whose ERW verdict is `public` (session 378's one word a table). Redivis stored the 128 of them the old draft holds at 0.935 of their CSV size, so the draft will need about **12.4 GB**, plus the three metadata tables (a few MB). That is more than the 10 GB a free account holds; whether Datapages holds more is the open question above. 58 of the 186 have never been on Redivis (most are the tables written from 21 October, held for storage in `release_v1.py`).

### Session 661: the 93 smallest (0.19 GB)

| Table | ERW verdict | Rows | CSV MB | In the old draft | Old draft MB |
|---|---|---|---|---|---|
| `battery_sourced_ranges` | public | 90 | 0.1 | yes | 0.1 |
| `battery_stack_monthly` | public | 11,556 | 3.1 | yes | 3.0 |
| `battery_stack_stress_daily` | public | 1,890 | 0.6 | yes | 0.5 |
| `boem_renewable_leases` | public | 52 | 0.0 | no |  |
| `caiso_curtailment_daily` | public | 25,104 | 5.2 | yes | 4.6 |
| `caiso_curtailment_profile` | public | 6,124 | 1.3 | yes | 1.2 |
| `caiso_dam_alert_day_hub_prices` | public | 3,024 | 1.1 | yes | 1.0 |
| `caiso_dam_cleared_energy` | public | 9,727 | 3.4 | yes | 3.2 |
| `caiso_grid_emergencies` | public | 1,906 | 0.6 | yes | 0.6 |
| `caiso_interconnection_queue` | public | 2,278 | 0.7 | yes | 0.6 |
| `caiso_reliability_daily` | public | 20,624 | 4.2 | yes | 3.7 |
| `carb_auction_allowance_prices` | public | 336 | 0.1 | yes | 0.1 |
| `carb_lcfs_credit_prices` | public | 1,124 | 0.3 | yes | 0.3 |
| `carbon_intensity_monthly` | public | 1,275 | 0.3 | yes | 0.3 |
| `census_metro_population` | public | 1,650 | 0.4 | yes | 0.4 |
| `cftc_cot_positions` | public | 9,824 | 3.9 | yes | 3.7 |
| `egrid_power_plants` | public | 12,612 | 5.5 | no |  |
| `eia860m_planned_generators` | public | 2,316 | 1.0 | yes | 1.0 |
| `eia860m_retired_generators` | public | 249 | 0.1 | yes | 0.1 |
| `eia860m_retired_generators_all` | public | 7,334 | 3.0 | yes | 3.2 |
| `eia930_demand_growth` | public | 24,108 | 4.6 | yes | 4.1 |
| `eia930_demand_weather` | public | 1,057 | 0.2 | yes | 0.2 |
| `eia930_generation_latest` | public | 3,166 | 2.3 | yes | 2.3 |
| `eia_annual_crosscheck_ba` | public | 144 | 0.1 | yes | 0.1 |
| `eia_annual_generation_ba` | public | 515 | 0.1 | yes | 0.1 |
| `eia_basin_production_monthly` | public | 1,668 | 1.3 | yes | 1.3 |
| `eia_coal_delivered_price_annual` | public | 3,213 | 0.9 | no |  |
| `eia_coal_price_rank_annual` | public | 2,843 | 0.8 | no |  |
| `eia_coal_prices_annual` | public | 2,781 | 0.7 | no |  |
| `eia_crude_first_purchase_prices` | public | 860 | 0.4 | yes | 0.3 |
| `eia_crude_reserves_annual` | public | 13,931 | 7.7 | no |  |
| `eia_crude_stream_prices` | public | 2,982 | 1.2 | yes | 1.2 |
| `eia_drilling_monthly` | public | 3,431 | 1.3 | no |  |
| `eia_gas_balance_annual` | public | 11,274 | 6.8 | no |  |
| `eia_gas_storage_weekly` | public | 7,000 | 3.0 | yes | 2.9 |
| `eia_gas_trade_monthly` | public | 1,979 | 0.9 | yes | 0.9 |
| `eia_gas_wells_annual` | public | 1,062 | 0.4 | no |  |
| `eia_lng_exports_monthly` | public | 1,083 | 1.4 | yes | 1.4 |
| `eia_meters_state_annual` | public | 8,578 | 3.0 | no |  |
| `eia_net_metering_state_annual` | public | 16,226 | 6.1 | no |  |
| `eia_nuclear_outages_daily` | public | 21,702 | 7.2 | no |  |
| `eia_oxygenate_production_monthly` | public | 6,006 | 2.5 | no |  |
| `eia_padd_crude_pipeline_flows` | public | 4,558 | 1.8 | yes | 1.7 |
| `eia_petroleum_stocks_monthly` | public | 18,247 | 6.6 | no |  |
| `eia_petroleum_trade_weekly` | public | 12,586 | 7.5 | yes | 7.2 |
| `eia_power_co2_state_annual` | public | 10,640 | 4.1 | no |  |
| `eia_regional_retail_fuel_prices` | public | 16,239 | 7.4 | yes | 7.0 |
| `eia_retail_fuel_prices` | public | 5,331 | 2.7 | yes | 2.6 |
| `eia_sector_energy_consumption_monthly` | public | 8,988 | 6.9 | yes | 6.7 |
| `eia_wood_pellets_monthly` | public | 2,090 | 0.6 | no |  |
| `energy_companies` | public | 475 | 0.6 | yes | 0.6 |
| `epa_ghgrp_power_co2` | public | 17,035 | 4.3 | no |  |
| `ercot_4cp_intervals` | public | 28 | 0.0 | yes | 0.0 |
| `ercot_as_prices_monthly` | public | 2,325 | 0.5 | yes | 0.5 |
| `ercot_as_quantities` | public | 4,800 | 1.1 | yes | 0.9 |
| `ercot_dam_cleared_energy` | public | 432 | 0.1 | yes | 0.1 |
| `ercot_grid_notices` | public | 178 | 0.1 | yes | 0.1 |
| `ercot_interconnection_queue` | public | 1,758 | 0.6 | yes | 0.6 |
| `ercot_large_load_status` | public | 38 | 0.0 | yes | 0.0 |
| `ercot_peak_premium_annual` | public | 2,016 | 0.4 | yes | 0.4 |
| `ercot_peak_premium_monthly` | public | 23,856 | 5.2 | yes | 4.8 |
| `ercot_storage_dam_awards_monthly` | public | 252 | 0.1 | yes | 0.1 |
| `ercot_storage_dam_offers_daily` | public | 20,124 | 4.8 | yes | 4.2 |
| `ercot_storage_dam_offers_monthly` | public | 819 | 0.2 | yes | 0.2 |
| `ercot_storage_node_basis` | public | 2,064 | 0.5 | yes | 0.4 |
| `ercot_storage_rt_monthly` | public | 329 | 0.1 | yes | 0.1 |
| `ercot_wind_solar_forecast` | public | 2,538 | 0.5 | yes | 0.4 |
| `ercot_wind_solar_hsl_daily` | public | 186 | 0.0 | yes | 0.0 |
| `ercot_wind_solar_hsl_hourly` | public | 8,400 | 1.8 | yes | 1.6 |
| `flex_alert_effects` | public | 2,973 | 0.6 | yes | 0.5 |
| `flex_alert_model` | public | 881 | 0.2 | yes | 0.2 |
| `frb_treasury_yields` | public | 5,850 | 1.8 | yes | 1.7 |
| `generation_mix_records` | public | 306 | 0.1 | yes | 0.1 |
| `grid_network_links` | public | 18,816 | 3.5 | yes | 3.1 |
| `grid_network_nodes` | public | 84 | 0.0 | yes | 0.0 |
| `grid_stress_yearly` | public | 2,394 | 0.5 | yes | 0.4 |
| `imf_commodity_prices` | public | 465 | 0.1 | yes | 0.1 |
| `interconnection_queue_summary` | public | 17,246 | 3.8 | yes | 3.5 |
| `iso_curtailment_monthly` | public | 3,232 | 0.6 | yes | 0.6 |
| `known_data_faults` | public | 28 | 0.0 | yes | 0.0 |
| `nlr_jedi_multipliers` | public | 5,562 | 4.2 | yes | 4.1 |
| `noaa_grid_weather_stations` | public | 245 | 0.1 | yes | 0.1 |
| `node_basis_summary` | public | 1,260 | 0.3 | yes | 0.3 |
| `price_years_by_window` | public | 2,754 | 0.9 | yes | 0.8 |
| `shoulder_hours_monthly` | public | 27,197 | 5.3 | yes | 4.6 |
| `spp_dam_cleared_energy` | public | 14,352 | 4.5 | yes | 4.2 |
| `spp_interconnection_queue` | public | 3,078 | 0.9 | yes | 0.8 |
| `storage_buildout_monthly` | public | 21,229 | 4.2 | yes | 3.8 |
| `storage_capacity` | public | 1,627 | 0.6 | yes | 0.7 |
| `storage_daily_cycle` | public | 14,451 | 3.2 | yes | 2.9 |
| `storage_owners_monthly` | public | 9,540 | 2.3 | yes | 2.2 |
| `weather_forecast_hourly` | public | 9,942 | 2.0 | yes | 1.7 |
| `weather_obs_hourly` | public | 10,086 | 2.2 | yes | 2.0 |

### Session 662: the next 81 (5.89 GB)

| Table | ERW verdict | Rows | CSV MB | In the old draft | Old draft MB |
|---|---|---|---|---|---|
| `ba_supply_monthly` | public | 158,503 | 30.6 | yes | 27.1 |
| `boem_ogor_lease_production_monthly` | public | 1,131,562 | 244.6 | no |  |
| `caiso_area_load_hourly` | public | 266,340 | 95.8 | yes | 91.3 |
| `caiso_as_prices` | public | 229,056 | 60.2 | yes | 56.8 |
| `caiso_battery_storage` | public | 363,744 | 66.5 | yes | 58.9 |
| `caiso_curtailment_intervals` | public | 485,666 | 109.2 | yes | 92.1 |
| `caiso_fuel_supply` | public | 156,624 | 28.6 | yes | 25.1 |
| `caiso_fuel_supply_history` | public | 782,808 | 149.2 | yes | 131.9 |
| `caiso_wind_solar_forecast` | public | 344,041 | 101.9 | yes | 95.0 |
| `carbon_intensity_daily` | public | 46,948 | 11.1 | yes | 10.0 |
| `carbon_intensity_hourly` | public | 1,127,177 | 268.1 | yes | 242.4 |
| `eia860m_operating_generators` | public | 28,605 | 11.3 | yes | 12.1 |
| `eia861_utility_sales` | public | 433,115 | 109.4 | no |  |
| `eia861m_utility_sales_monthly` | public | 1,145,088 | 282.6 | no |  |
| `eia930_all_demand` | public | 21,024 | 17.0 | yes | 16.5 |
| `eia930_all_generation` | public | 111,240 | 83.4 | yes | 81.3 |
| `eia930_all_history` | public | 60,084 | 16.5 | yes | 14.6 |
| `eia930_all_interchange` | public | 278,664 | 137.8 | yes | 132.5 |
| `eia930_all_storage` | public | 72,984 | 39.2 | yes | 37.9 |
| `eia930_daily_demand` | public | 191,651 | 90.5 | yes | 86.2 |
| `eia930_daily_total_interchange` | public | 212,310 | 105.1 | yes | 100.4 |
| `eia930_event_hourly_interchange` | public | 266,833 | 133.0 | yes | 128.3 |
| `eia930_subba_demand_hourly` | public | 186,177 | 63.7 | no |  |
| `eia930_subba_demand_hourly_2022` | public | 712,831 | 242.3 | no |  |
| `eia930_subba_demand_hourly_2023` | public | 717,332 | 243.8 | no |  |
| `eia930_subba_demand_hourly_2024` | public | 726,716 | 247.0 | no |  |
| `eia930_subba_demand_hourly_2025` | public | 723,617 | 246.0 | no |  |
| `eia_aeo_electricity` | public | 34,034 | 14.0 | no |  |
| `eia_co2_state_annual` | public | 66,144 | 21.5 | no |  |
| `eia_coal_trade_price_annual` | public | 24,623 | 8.0 | no |  |
| `eia_crude_imports_by_country` | public | 22,633 | 9.6 | yes | 9.2 |
| `eia_crude_imports_detail_monthly` | public | 154,779 | 61.7 | no |  |
| `eia_crude_production_state_monthly` | public | 25,644 | 9.1 | no |  |
| `eia_energy_efficiency_state_annual` | public | 19,740 | 9.7 | no |  |
| `eia_fuel_spot_prices` | public | 27,754 | 9.1 | yes | 8.5 |
| `eia_gas_consumption_state_monthly` | public | 63,420 | 30.3 | no |  |
| `eia_gas_interstate_annual` | public | 29,470 | 17.1 | no |  |
| `eia_gas_prices_state_monthly` | public | 72,550 | 34.9 | no |  |
| `eia_gas_production_state_monthly` | public | 47,805 | 22.0 | no |  |
| `eia_gas_reserves_annual` | public | 19,232 | 12.6 | no |  |
| `eia_gas_storage_capacity_monthly` | public | 23,980 | 10.0 | no |  |
| `eia_gas_storage_state_monthly` | public | 55,015 | 25.0 | no |  |
| `eia_gas_trade_country_monthly` | public | 30,337 | 9.5 | no |  |
| `eia_heating_fuel_prices_weekly` | public | 48,534 | 18.7 | no |  |
| `eia_ngl_production_monthly` | public | 31,956 | 42.3 | no |  |
| `eia_padd_rail_barge_movements_monthly` | public | 120,742 | 45.5 | no |  |
| `eia_petroleum_stocks_weekly` | public | 16,823 | 10.6 | yes | 10.2 |
| `eia_petroleum_supply_weekly` | public | 26,118 | 22.1 | yes | 21.6 |
| `eia_power_plant_fuel_costs` | public | 12,898 | 8.2 | yes | 7.9 |
| `eia_product_spot_prices` | public | 72,052 | 58.8 | yes | 57.3 |
| `eia_product_supplied_monthly` | public | 71,938 | 26.7 | no |  |
| `eia_refinery_capacity_annual` | public | 62,804 | 23.7 | no |  |
| `eia_refinery_inputs_monthly` | public | 216,010 | 85.5 | no |  |
| `eia_refinery_production_monthly` | public | 175,413 | 133.0 | no |  |
| `eia_refinery_weekly` | public | 50,753 | 23.6 | no |  |
| `eia_retail_electricity_prices` | public | 114,202 | 51.9 | yes | 49.7 |
| `eia_retail_sales_monthly` | public | 228,203 | 103.4 | yes | 98.3 |
| `eia_seds_state_energy` | public | 49,140 | 57.2 | no |  |
| `eia_state_capacity_annual` | public | 56,719 | 20.2 | no |  |
| `eia_state_generation_monthly` | public | 200,030 | 198.4 | yes | 193.6 |
| `eia_state_source_disposition_annual` | public | 37,738 | 37.9 | no |  |
| `eia_steo_forecasts` | public | 5,088 | 11.7 | no |  |
| `ercot_as_prices` | public | 338,252 | 74.8 | yes | 65.7 |
| `ercot_as_prices_daily` | public | 70,470 | 15.7 | yes | 14.7 |
| `ercot_hub_prices_daily` | public | 346,560 | 78.8 | yes | 73.2 |
| `ercot_rtm_node_prices` | public | 704,496 | 149.7 | yes | 139.2 |
| `ercot_rtm_price_adders` | public | 601,810 | 134.4 | yes | 118.5 |
| `ercot_wind_solar_output_hourly` | public | 52,608 | 10.7 | yes | 9.0 |
| `ercot_zone_load_hourly` | public | 926,838 | 190.2 | yes | 157.6 |
| `generation_mix_hourly_profile` | public | 165,760 | 33.5 | yes | 30.1 |
| `lbnl_interconnection_queue` | public | 38,201 | 16.0 | yes | 15.8 |
| `nlr_atb_electricity_costs` | public | 95,000 | 42.8 | no |  |
| `noaa_grid_weather_daily` | public | 118,630 | 26.1 | yes | 24.4 |
| `noaa_isd_hourly` | public | 412,435 | 139.7 | yes | 129.5 |
| `node_basis_daily` | public | 960,627 | 221.3 | no |  |
| `nrc_reactor_status` | public | 234,815 | 53.1 | yes | 49.0 |
| `rrc_lease_production_monthly` | public | 212,252 | 62.0 | yes | 58.2 |
| `spp_as_prices` | public | 159,432 | 46.8 | yes | 44.0 |
| `spp_as_quantities` | public | 159,768 | 46.8 | yes | 44.3 |
| `spp_curtailment_daily` | public | 38,408 | 7.9 | yes | 7.0 |
| `state_generation_mix_monthly` | public | 107,560 | 21.6 | yes | 19.1 |

### Session 663: the 12 largest, last (7.17 GB)

| Table | ERW verdict | Rows | CSV MB | In the old draft | Old draft MB |
|---|---|---|---|---|---|
| `eia923_plant_fuel_annual` | public | 872,492 | 314.6 | no |  |
| `eia930_all_emissions` | public | 4,347,360 | 1,099.6 | yes | 964.1 |
| `eia930_daily_interchange` | public | 951,832 | 502.9 | yes | 483.4 |
| `eia_nuclear_outages_facility_daily` | public | 1,312,872 | 453.6 | no |  |
| `eia_nuclear_outages_generator_daily` | public | 2,141,406 | 783.2 | no |  |
| `eia_petroleum_snd_monthly` | public | 523,835 | 376.3 | no |  |
| `ercot_all_hub_prices_history` | public | 3,103,458 | 716.7 | no |  |
| `ercot_dam_esr_awards` | public | 1,953,717 | 540.7 | yes | 571.0 |
| `ercot_sced_esr_hourly` | public | 1,580,775 | 553.5 | yes | 590.0 |
| `ercot_zone_prices_history` | public | 2,481,384 | 570.2 | yes | 508.4 |
| `noaa_grid_weather_hourly` | public | 1,907,625 | 411.7 | yes | 388.6 |
| `noaa_station_weather_hourly` | public | 4,747,179 | 848.1 | yes | 765.8 |

The metadata tables (`erw_coverage`, `erw_sources`, `erw_headers`) go with session 663's batch, after every table, so `erw_headers` holds the headers of the tables the draft holds.

## The tables excluded: 104

- **54 internal**: licensed for internal use; never in the public dataset.
- **50 unsettled**: a publisher not read, a "license needed" ruling waiting for its permission, or a flag and a verdict that disagree. Many are in the old draft today (their `coverage.csv` flag is public); none goes to the Stanford dataset until its verdict is `public`.
- **FRED**: no table in `coverage.csv` comes from FRED any longer. Its three tables were retired on 13 October 2026 (`retired_tables.csv`: `fred_daily_spot_prices`, `fred_treasury_yields`, `fred_imf_commodity_prices`), so FRED's series are excluded by construction; two of them are still in the old draft.

| Table | ERW verdict | Flag in coverage.csv | Rows | In the old draft |
|---|---|---|---|---|
| `api_cost_ledger` | internal | internal | 3,740 | no |
| `datacenter_projects_evidence` | internal | internal | 162 | no |
| `eia_all_futures_prices` | internal | internal | 21,240 | no |
| `energy_deals_evidence` | internal | internal | 548 | no |
| `ercot_node_prices_hourly` | internal | internal | 499,296 | no |
| `ferc714_area_demand_2006` | internal | internal | 1,532,108 | no |
| `ferc714_area_demand_2007` | internal | internal | 1,375,404 | no |
| `ferc714_area_demand_2008` | internal | internal | 1,326,412 | no |
| `ferc714_area_demand_2009` | internal | internal | 1,100,955 | no |
| `ferc714_area_demand_2010` | internal | internal | 1,098,623 | no |
| `ferc714_area_demand_2011` | internal | internal | 1,059,978 | no |
| `ferc714_area_demand_2012` | internal | internal | 1,062,839 | no |
| `ferc714_area_demand_2013` | internal | internal | 1,054,827 | no |
| `ferc714_area_demand_2014` | internal | internal | 884,855 | no |
| `ferc714_area_demand_2015` | internal | internal | 867,248 | no |
| `ferc714_area_demand_2016` | internal | internal | 869,616 | no |
| `ferc714_area_demand_2017` | internal | internal | 858,484 | no |
| `ferc714_area_demand_2018` | internal | internal | 849,724 | no |
| `ferc714_area_demand_2019` | internal | internal | 832,185 | no |
| `ferc714_area_demand_2020` | internal | internal | 834,384 | no |
| `ferc714_area_demand_2021` | internal | internal | 796,348 | no |
| `ferc714_area_demand_2022` | internal | internal | 784,264 | no |
| `ferc714_area_demand_2023` | internal | internal | 779,627 | no |
| `ferc714_area_demand_2024` | internal | internal | 781,703 | no |
| `ferc714_area_demand_2025` | internal | internal | 770,886 | no |
| `ferc714_respondents` | internal | internal | 219 | no |
| `ferc_eqr_buyer_doubtful` | internal | internal | 1,281 | no |
| `ferc_eqr_buyer_names` | internal | internal | 17,955 | no |
| `ferc_eqr_contract_terms` | internal | internal | 186,873 | no |
| `ferc_eqr_contracts` | internal | internal | 186,873 | no |
| `ferc_eqr_contracts_history` | internal | internal | 571,115 | no |
| `ferc_eqr_party_mw` | internal | internal | 812 | no |
| `ferc_eqr_party_totals` | internal | internal | 12,290 | no |
| `ferc_eqr_quarter_changes` | internal | internal | 68 | no |
| `iso_all_capacity_prices` | internal | internal | 814 | no |
| `isone_as_prices` | internal | internal | 55,964 | no |
| `isone_dam_cleared_energy` | internal | internal | 960 | no |
| `isone_ddg_undelivered_monthly` | internal | internal | 840 | no |
| `isone_zone_load_hourly` | internal | internal | 131,319 | no |
| `isone_zone_prices_history` | internal | internal | 1,075,024 | no |
| `large_load_document_verdicts` | internal | internal | 427 | no |
| `large_load_rules_internal` | internal | internal | 74 | no |
| `large_load_statements` | internal | internal | 798 | no |
| `large_load_waits` | internal | internal | 2,622 | no |
| `miso_as_prices` | internal | internal | 54,936 | no |
| `news_scores_shadow` | internal | internal | 4,748 | no |
| `news_stories` | internal | internal | 21,656 | no |
| `pjm_rpm_capacity_prices` | internal | internal | 234 | no |
| `policy_reads_evidence` | internal | internal | 3,395 | no |
| `portwatch_chokepoint_transits` | internal | internal | 119,616 | no |
| `price_board_carbon` | internal | internal | 15 | no |
| `rggi_auction_allowance_prices` | internal | internal | 304 | no |
| `texas_delivery_charges` | internal | internal | 73 | no |
| `texas_transmission_matrix` | internal | internal | 855 | no |
| `ai_power_regions` | unsettled | public | 187 | yes |
| `battery_stack_review_monthly` | unsettled | public | 3,744 | yes |
| `clean_energy_hourly` | unsettled | public | 473,781 | yes |
| `clean_energy_summary` | unsettled | public | 27,531 | yes |
| `cost_of_power_carbon` | unsettled | public | 712 | yes |
| `cost_of_power_hourly_profile` | unsettled | public | 4,368 | yes |
| `cost_of_power_monthly` | unsettled | public | 2,304 | yes |
| `datacenter_facilities` | unsettled | public | 422 | yes |
| `datacenter_operator_sites` | unsettled | public | 275 | yes |
| `datacenter_projects` | unsettled | public | 145 | yes |
| `datacenter_queue_positions` | unsettled | public | 3 | yes |
| `energy_deals` | unsettled | public | 497 | yes |
| `energy_projects` | unsettled | public | 39,786 | yes |
| `event_study_estimates` | unsettled | public | 3,040 | yes |
| `event_window_daily` | unsettled | public | 29,953 | yes |
| `grid_stress_days` | unsettled | public | 282 | yes |
| `hub_price_comparison` | unsettled | public | 575 | yes |
| `impact_tax_rules` | unsettled | public | 49 | yes |
| `iso_dam_hub_prices` | unsettled | public | 22,488 | yes |
| `iso_hub_prices_history` | unsettled | public | 596,232 | yes |
| `iso_queue_statistics` | unsettled | public | 1,511 | yes |
| `iso_rt_top_intervals` | unsettled | public | 50 | yes |
| `iso_rtm_hub_prices` | unsettled | public | 58,656 | yes |
| `iso_trader_daily` | unsettled | public | 15,951 | yes |
| `iso_zone_prices_history` | unsettled | public | 1,665,645 | yes |
| `isone_dam_zone_prices` | unsettled | public | 12,312 | yes |
| `isone_interconnection_queue` | unsettled | public | 1,751 | yes |
| `isone_rtm_zone_prices` | unsettled | public | 38,880 | yes |
| `isone_rtm_zone_prices_hourly` | unsettled | public | 11,016 | yes |
| `large_load_public` | unsettled | public | 341 | yes |
| `large_load_rule_reads` | unsettled | public | 87 | yes |
| `large_load_rules` | unsettled | public | 43 | yes |
| `merchant_revenue_monthly` | unsettled | public | 8,853 | yes |
| `miso_interconnection_queue` | unsettled | public | 3,881 | yes |
| `news_index` | unsettled | public | 16,247 | yes |
| `nyiso_as_prices` | unsettled | public | 293,376 | yes |
| `nyiso_dam_cleared_energy` | unsettled | public | 9,744 | yes |
| `nyiso_dam_zone_prices` | unsettled | public | 15,312 | yes |
| `nyiso_interconnection_queue` | unsettled | public | 1,814 | yes |
| `nyiso_load_queue` | unsettled | public | 74 | yes |
| `nyiso_rtm_zone_prices` | unsettled | public | 58,080 | yes |
| `nyiso_zone_load_hourly` | unsettled | public | 749,595 | yes |
| `policy_action_tags` | unsettled | public | 38 | yes |
| `policy_actions` | unsettled | public | 1,937 | yes |
| `policy_reads` | unsettled | public | 389 | yes |
| `price_board_latest` | unsettled | public | 3,233 | yes |
| `price_board_peak_offpeak` | unsettled | public | 3,783 | yes |
| `price_board_spreads` | unsettled | public | 2,406 | yes |
| `scarcity_hours_by_grid` | unsettled | public | 178,886 | yes |
| `uswtdb_wind_turbines` | unsettled | public | 77,839 | no |

## For Samuel

- **The daily run's target.** Whether the daily's upload, its license check and the restore move to the Stanford dataset (the three reads above), and when. Until then the old account's draft keeps receiving the daily's uploads (most refused for storage), and the Stanford draft is filled by these sessions only.
- **The starter table** `eia930_iso_hourly_demand_2019_2025` in `datapages.erw` v1.0: kept in the next version, or removed from the draft before the click.
- **Datapages' storage limit**, if Redivis's organization settings show it: the draft needs about 12.4 GB.
