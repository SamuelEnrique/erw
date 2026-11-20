# Codebook plan, 20 November 2026 (chain 630, part A)

Drawn by `runs/c630/plan.py` from `warehouse/metadata/coverage.csv`, each table's header row on the data machine, `docs/methods/`, the site's source, `warehouse/supabase/live_set.yaml` and `warehouse/metadata/redivis_uploads.csv`. The table by table record is [`codebook-plan-2026-11-20.csv`](codebook-plan-2026-11-20.csv). No table was written.

## The counts

- Tables in coverage: 698; with a file on the data machine: 698.
- Order of part B: 1 public, read by the site: 196; 2 public: 386; 3 internal: 116.
- Shapes by the data standard (`/data/standard`): entities 74; events 56; series 568. A table of shape other holds columns of its own; its first columns are not the standard's.
- Named by at least one method note: 681; by none: 17.
- Named in the site's source: 216; loaded by the live set: 114; in the Redivis manifest: 230.
- Distinct column names: 2122; names held by five tables or more: 132 (the candidates for `_shared.yaml`).

## Column names held by five tables or more

`source` 698, `source_url` 668, `retrieved_at` 647, `vintage` 614, `geo` 613, `entity` 570, `ts_utc` 569, `freq` 568, `unit` 568, `value` 568, `variable` 568, `market` 535, `node` 535, `status` 127, `entity_type` 76, `capacity_mw` 74, `entity_id` 74, `lat` 74, `lon` 74, `name` 74, `operator` 74, `status_date` 74, `mw` 59, `event_date` 56, `event_id` 56, `event_type` 56, `currency` 54, `parties` 54, `entity_ids` 53, `price` 53, `x_state` 47, `ba` 44, `state` 34, `x_region` 32, `county` 28, `x_flag` 27, `x_geo_code` 26, `x_conf_status` 23, `x_county` 22, `x_table` 22, `x_label` 19, `x_file` 17, `x_utility_number` 15, `x_technology` 12, `sector` 11, `x_sheet` 11, `x_status` 11, `model_id` 10, `queue_id` 10, `transmission_owner` 10, `x_ba_code` 10, `x_basis` 10, `x_dollar_year` 10, `x_page` 10, `x_product` 10, `x_code` 9, `x_diba` 9, `x_diba_region` 9, `x_level` 9, `x_sector` 9, `x_utility_id` 9, `iso_status` 8, `kind` 8, `poi` 8, `queue_date` 8, `technology` 8, `x_date_kind` 8, `x_eia_status` 8, `x_group` 8, `x_ownership` 8, `x_period` 8, `x_plant_code` 8, `x_quarter` 8, `x_siec` 8, `x_type` 8, `x_vector` 8, `x_year` 8, `zone` 8, `actual_in_service_date` 7, `balancing_authority` 7, `document_title` 7, `fuel_technology` 7, `grid` 7, `proposed_in_service_date` 7, `withdrawn_date` 7, `x_area` 7, `x_class` 7, `x_nrg_bal` 7, `x_partner` 7, `x_retirement_year` 7, `confidence` 6, `page` 6, `plant_id` 6, `region` 6, `significance` 6, `utility` 6, `x_docket` 6, `x_document` 6, `x_fuel` 6, `x_grid` 6, `x_kind` 6, `x_notes` 6, `x_parent` 6, `x_reason` 6, `x_retirement_month` 6, `x_revised` 6, `x_sector_name` 6, `x_title` 6, `x_unit` 6, `city` 5, `eia_status` 5, `generator_id` 5, `net_summer_mw` 5, `row_kind` 5, `sentence` 5, `technology_group` 5, `utility_id` 5, `x_at` 5, `x_fips` 5, `x_fiscal_year` 5, `x_generator_id` 5, `x_lat` 5, `x_latitude` 5, `x_lon` 5, `x_longitude` 5, `x_nerc_region` 5, `x_note` 5, `x_plant_name` 5, `x_scenario` 5, `x_to_ba` 5, `x_utility` 5, `x_zone` 5

## Families, in the order of part B

A family is the tables of one name prefix held by three tables or more; the ERW's own derived tables of a smaller prefix are `erw_derived`, the other sources of a smaller prefix `other_sources`. A family takes the place of its first table in the order.

### ba (3 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `ba_boundaries` | public | derived | entities | 27 | ba_boundaries, grid_network, regions_pages | /grid, /grid/authority/[code], /grid/boundaries and 1 more | no | no |
| 2 | `ba_supply_monthly` | public | derived | series | 15 | ba_supply_monthly, eia930_caiso_break, eia930_daily_total_interchange and 4 more | /, /_retired/network-original, /about and 4 more | yes | energy_research_warehouse |
| 3 | `ba_trade_partners` | public | derived | series | 12 | authority_facts, interchange_pairs, supply_and_trade | /learn/problems, /supply | no | no |

### battery (4 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 4 | `battery_stack_monthly` | public | derived | series | 16 | ask, battery_awards, battery_early_years and 7 more | /, /about, /api/ask and 8 more | yes | energy_research_warehouse |
| 5 | `battery_stack_review_monthly` | public | derived | series | 16 | battery_stack, nyiso_as_prices, reserve_quantities_nyiso_spp and 1 more | /, /cost-of-power/battery, /cost-of-power/battery/months.csv and 2 more | no | energy_research_warehouse |
| 6 | `battery_stack_stress_daily` | public | derived | series | 17 | battery_earns_algorithm, battery_stack, battery_stress_days and 2 more | /, /about, /cost-of-power/battery and 5 more | yes | energy_research_warehouse |
| 200 | `battery_sourced_ranges` | public | source | series | 19 | battery_sourced_ranges | none | yes | energy_research_warehouse |

### caiso (15 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 7 | `caiso_as_prices` | public | source | series | 13 | battery_earns_algorithm, battery_stack, caiso_as_prices and 2 more | /board, /cost-of-power/battery | no | energy_research_warehouse |
| 8 | `caiso_battery_storage` | public | source | series | 13 | automated_analysis, automated_analysis_findings, caiso_battery_storage and 9 more | /_retired/curtailment-v2, /_retired/network-original, /curtailment and 4 more | yes | energy_research_warehouse |
| 9 | `caiso_curtailment_daily` | public | source | series | 13 | ask_ercot, automated_analysis, automated_analysis_findings and 9 more | /, /_retired/curtailment-original, /about and 4 more | yes | energy_research_warehouse |
| 10 | `caiso_curtailment_intervals` | public | source | series | 13 | automated_analysis_findings, caiso_curtailment_daily, caiso_curtailment_intervals and 3 more | /_retired/curtailment-v2, /board, /cost-of-power and 10 more | no | energy_research_warehouse |
| 11 | `caiso_curtailment_profile` | public | derived | series | 13 | ask_ercot, caiso_curtailment_intervals, curtailment and 1 more | /, /_retired/curtailment-v2, /about and 4 more | yes | energy_research_warehouse |
| 12 | `caiso_dam_alert_day_hub_prices` | public | source | series | 13 | caiso_alerts, caiso_dam_alert_day_hub_prices, flex_alert_scorecard | /grid/caiso/alerts | no | energy_research_warehouse |
| 13 | `caiso_fuel_supply` | public | source | series | 13 | automated_analysis_findings, caiso_fuel_supply, caiso_fuel_supply_history and 8 more | /shoulder | no | energy_research_warehouse |
| 14 | `caiso_grid_emergencies` | public | source | events | 21 | ai_power_regions, battery_stack, battery_stress_days and 9 more | /cost-of-power, /cost-of-power/tables.csv, /events/caiso-heat-2022 and 3 more | yes | energy_research_warehouse |
| 15 | `caiso_reliability_daily` | public | derived | series | 13 | california_reliability, flex_alert_scorecard, impossible_hours | /events/caiso-heat-2022, /grid, /grid/caiso/alerts | yes | energy_research_warehouse |
| 204 | `caiso_area_load_hourly` | public | source | series | 13 | caiso_area_load_hourly, caiso_dam_cleared_energy, caiso_fuel_supply and 4 more | none | no | energy_research_warehouse |
| 205 | `caiso_dam_cleared_energy` | public | source | series | 13 | caiso_dam_cleared_energy, supply_and_trade | none | no | energy_research_warehouse |
| 206 | `caiso_fuel_supply_history` | public | source | series | 13 | automated_analysis_findings, caiso_fuel_supply, caiso_fuel_supply_history and 3 more | none | no | energy_research_warehouse |
| 207 | `caiso_interconnection_queue` | public | source | entities | 26 | caiso_interconnection_queue, datacenter_facilities, energy_projects and 3 more | none | yes | energy_research_warehouse |
| 208 | `caiso_outlook_demand` | public | source | series | 13 | caiso_outlook_demand | none | no | energy_research_warehouse |
| 209 | `caiso_wind_solar_forecast` | public | source | series | 13 | caiso_wind_solar_forecast, generation_mix_hourly, renewable_forecast_error | none | no | energy_research_warehouse |

### carbon (3 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 16 | `carbon_intensity_daily` | public | derived | series | 14 | ai_power_regions, emissions, events and 4 more | /, /_retired/network-original, /about and 12 more | yes | energy_research_warehouse |
| 17 | `carbon_intensity_hourly` | public | derived | series | 14 | automated_analysis_findings, clean_energy, datacenter_pays_algorithm and 9 more | /, /_retired/network-original, /about and 6 more | yes | energy_research_warehouse |
| 18 | `carbon_intensity_monthly` | public | derived | series | 14 | datacenter_cost, datacenter_pays_algorithm, emissions and 3 more | /, /about, /cost-of-power and 5 more | yes | energy_research_warehouse |

### census (6 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 19 | `census_county_population` | public | source | series | 15 | county_population_and_regions, region_weather, states_page | /queues/places, /states | no | no |
| 210 | `census_bps_state_annual` | public | source | series | 15 | census_bps_state_annual | none | no | no |
| 211 | `census_c30_construction_monthly` | public | source | series | 15 | census_c30_construction_monthly | none | no | no |
| 212 | `census_cbp_hosting_annual` | public | source | series | 16 | census_cbp_hosting_annual | none | no | no |
| 213 | `census_metro_population` | public | source | series | 15 | automated_analysis_scanner, census_metro_population, demand_weather and 3 more | none | no | energy_research_warehouse |
| 214 | `census_qss_utilities_hosting_quarterly` | public | source | series | 14 | census_qss_utilities_hosting_quarterly | none | no | no |

### company (3 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 20 | `company_aliases` | public | model_extracted | entities | 25 | companies | /, /about, /companies and 3 more | no | no |
| 21 | `company_directory` | public | model_extracted | entities | 62 | companies | /, /about, /companies and 10 more | no | no |
| 22 | `company_links` | public | model_extracted | entities | 29 | companies | /, /about, /companies and 10 more | no | no |

### cost (3 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 23 | `cost_of_power_carbon` | public | derived | series | 14 | ask_ercot, cost_of_power, datacenter_cost and 2 more | /, /about, /cost-of-power and 2 more | yes | energy_research_warehouse |
| 24 | `cost_of_power_hourly_profile` | public | derived | series | 14 | ask_ercot, cost_of_power, datacenter_cost and 1 more | /, /about, /cost-of-power and 8 more | yes | energy_research_warehouse |
| 25 | `cost_of_power_monthly` | public | derived | series | 14 | ai_power_regions, ask, bill and 6 more | /, /_retired/board-original, /_retired/curtailment-original and 36 more | yes | energy_research_warehouse |

### datacenter (6 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 26 | `datacenter_facilities` | public | model_extracted | entities | 46 | automated_analysis, companies, datacenter_facilities and 8 more | /, /_retired/board-original, /_retired/board-v3 and 64 more | yes | energy_research_warehouse |
| 27 | `datacenter_operator_sites` | public | source | entities | 27 | census_cbp_hosting_annual, datacenter_facilities, datacenter_operator_sites and 1 more | /api/download, /board, /board/rows and 16 more | no | energy_research_warehouse |
| 28 | `datacenter_projects` | public | model_extracted | entities | 46 | companies, datacenter_facilities, datacenter_operator_sites and 5 more | /, /about, /api/download and 32 more | yes | energy_research_warehouse |
| 218 | `datacenter_queue_positions` | public | derived | entities | 27 | datacenter_facilities, datacenter_pays_algorithm | none | no | energy_research_warehouse |
| 583 | `datacenter_projects_evidence` | internal | model_extracted | events | 14 | datacenter_projects, datacenter_projects_evidence | /datacenters | no | energy_research_warehouse_internal |
| 584 | `datacenter_tracker_rollups` | internal | model_extracted | series | 13 | datacenter_projects, datacenter_tracker, datacenter_tracker_rollups | /board, /cost-of-power, /cost-of-power/battery and 9 more | no | energy_research_warehouse_internal |

### eia (114 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 29 | `eia_aeo_industrial` | public | source | series | 20 | industry_page | /industry | no | no |
| 30 | `eia_basin_production_monthly` | public | source | series | 13 | eia_basin_production_monthly, eia_petroleum_supply_weekly, supply_and_trade | /, /about, /data and 1 more | no | energy_research_warehouse |
| 31 | `eia_county_region` | public | derived | entities | 24 | county_population_and_regions, queue_places, region_weather and 1 more | /queues/places, /states | no | no |
| 32 | `eia_crude_first_purchase_prices` | public | source | series | 13 | eia_crude_first_purchase_prices, eia_crude_stream_prices, price_board | /board | yes | energy_research_warehouse |
| 33 | `eia_crude_stream_prices` | public | source | series | 13 | eia_crude_first_purchase_prices, eia_crude_stream_prices, eia_fuel_spot_prices and 2 more | /board | no | energy_research_warehouse |
| 34 | `eia_fuel_spot_prices` | public | source | series | 13 | automated_analysis_findings, cost_of_power, eia_all_futures_prices and 11 more | /, /_retired/board-original, /_retired/board-v3 and 18 more | yes | energy_research_warehouse |
| 35 | `eia_gas_prices_state_monthly` | public | source | series | 13 | eia_gas_prices_state_monthly, price_board | /board | no | no |
| 36 | `eia_gas_storage_weekly` | public | source | series | 13 | eia_gas_storage_type_monthly, eia_gas_storage_weekly, eia_petroleum_supply_weekly and 3 more | /, /about, /board and 2 more | no | energy_research_warehouse |
| 37 | `eia_gas_trade_monthly` | public | source | series | 13 | eia_gas_trade_monthly, eia_petroleum_supply_weekly, gas_balance_weekly and 2 more | /, /about, /board and 2 more | no | energy_research_warehouse |
| 38 | `eia_heat_rates_annual` | public | source | series | 13 | eia_capacity_factors, price_board | /board | no | no |
| 39 | `eia_heating_fuel_prices_weekly` | public | source | series | 13 | eia_heating_fuel_prices_weekly, price_board | /board | no | no |
| 40 | `eia_hgl_pipelines` | public | source | entities | 17 | map_layers | 1 site files | no | no |
| 41 | `eia_lng_exports_monthly` | public | source | series | 13 | desnz_uk_gas_quarterly, doe_lng_export_applications, eia_gas_trade_monthly and 4 more | /board | no | energy_research_warehouse |
| 42 | `eia_mecs_manufacturing` | public | source | series | 17 | eia_mecs_manufacturing, industry_page | /industry | no | no |
| 43 | `eia_petroleum_supply_weekly` | public | source | series | 13 | eia_crude_tank_farm_stocks_monthly, eia_petroleum_supply_weekly, eia_refinery_weekly and 1 more | /, /about, /data and 1 more | no | energy_research_warehouse |
| 44 | `eia_power_plant_fuel_costs` | public | source | series | 13 | eia_power_fuel_stocks_monthly, eia_power_plant_fuel_costs, eia_regional_retail_fuel_prices and 2 more | /board, /cost-of-power, /cost-of-power/battery and 9 more | no | energy_research_warehouse |
| 45 | `eia_product_spot_prices` | public | source | series | 13 | eia_all_futures_prices, eia_fuel_spot_prices, eia_product_spot_prices and 2 more | /, /_retired/board-v4, /about and 3 more | no | energy_research_warehouse |
| 46 | `eia_regional_retail_fuel_prices` | public | source | series | 13 | eia_product_spot_prices, eia_regional_retail_fuel_prices, ev_game and 1 more | /, /about, /board and 3 more | no | energy_research_warehouse |
| 47 | `eia_retail_electricity_prices` | public | source | series | 13 | bill, cost_of_power, datacenter_cost and 7 more | /, /about, /board and 5 more | no | energy_research_warehouse |
| 48 | `eia_retail_fuel_prices` | public | source | series | 13 | eia_product_spot_prices, eia_regional_retail_fuel_prices, eia_retail_fuel_prices and 2 more | /board | no | energy_research_warehouse |
| 49 | `eia_retail_sales_monthly` | public | source | series | 13 | automated_analysis_findings, automated_analysis_scanner, consumption and 8 more | /, /about, /consumption and 6 more | yes | energy_research_warehouse |
| 50 | `eia_sector_energy_consumption_monthly` | public | source | series | 13 | consumption, demand_growth, eia_mecs_manufacturing and 3 more | /, /about, /consumption and 4 more | yes | energy_research_warehouse |
| 51 | `eia_seds_industrial_annual` | public | source | series | 15 | industry_page, states_page | /industry | no | no |
| 52 | `eia_seds_state_energy` | public | source | series | 13 | eia_gas_heat_content_monthly, eia_primary_energy_monthly, eia_seds_residential_annual and 3 more | /industry | no | no |
| 53 | `eia_state_capacity_annual` | public | source | series | 13 | eia_state_capacity_annual, irena_capacity_annual | /cost-of-power, /demand | no | no |
| 54 | `eia_steo_forecasts` | public | source | series | 15 | eia_steo_forecasts, forecast | /impact | no | no |
| 241 | `eia_aeo_electricity` | public | source | series | 19 | eia_aeo_electricity, eia_aeo_emm_regions | none | no | no |
| 242 | `eia_aeo_emm_regions` | public | source | series | 19 | eia_aeo_emm_regions | none | no | no |
| 243 | `eia_annual_crosscheck_ba` | public | derived | series | 14 | eia_annual_crosscheck, eia_annual_generation_ba, grid_network | none | yes | energy_research_warehouse |
| 244 | `eia_annual_generation_ba` | public | source | series | 13 | eia_annual_crosscheck, eia_annual_generation_ba, grid_network | none | yes | energy_research_warehouse |
| 245 | `eia_biofuel_plants` | public | source | entities | 22 | eia_biofuel_plants, epa_rfs_rins | none | no | no |
| 246 | `eia_capacity_factors_annual` | public | source | series | 13 | eia_capacity_factors | none | no | no |
| 247 | `eia_capacity_factors_monthly` | public | source | series | 13 | eia_capacity_factors | none | no | no |
| 248 | `eia_cbecs_commercial_buildings` | public | source | series | 17 | eia_buildings_surveys | none | no | no |
| 249 | `eia_co2_state_annual` | public | source | series | 13 | eia_co2_state_annual, eia_world_coal_energy, epa_ghg_inventory_annual | none | no | no |
| 250 | `eia_coal_delivered_price_annual` | public | source | series | 13 | eia_coal_prices, eia_coal_receipts_annual, price_board | none | no | no |
| 251 | `eia_coal_distribution_quarterly` | public | source | series | 17 | eia_coal_distribution_quarterly | none | no | no |
| 252 | `eia_coal_mine_production_annual` | public | source | series | 24 | eia_coal_mine_production_annual, eia_coal_receipts_annual, msha_coal_mines and 1 more | none | no | no |
| 253 | `eia_coal_price_rank_annual` | public | source | series | 13 | eia_coal_prices, price_board | none | no | no |
| 254 | `eia_coal_prices_annual` | public | source | series | 13 | eia_coal_prices, price_board | none | no | no |
| 255 | `eia_coal_production_annual` | public | source | series | 13 | eia_coal_mine_production_annual, eia_coal_production_annual, eia_world_coal_energy | none | no | no |
| 256 | `eia_coal_receipts_annual` | public | source | series | 24 | eia923_receipts, eia_coal_distribution_quarterly, eia_coal_receipts_annual | none | no | no |
| 257 | `eia_coal_trade_price_annual` | public | source | series | 13 | eia_coal_prices, price_board | none | no | no |
| 258 | `eia_crude_imports_by_country` | public | source | series | 13 | eia_crude_imports_by_country, eia_crude_imports_detail_monthly, eia_petroleum_exports_by_destination and 1 more | none | no | energy_research_warehouse |
| 259 | `eia_crude_imports_detail_monthly` | public | source | series | 13 | cer_pipeline_throughput, eia_crude_imports_by_country, eia_crude_imports_detail_monthly and 2 more | none | no | no |
| 260 | `eia_crude_production_state_monthly` | public | source | series | 13 | eia_basin_production_monthly, eia_crude_production_state_monthly, eia_world_oil_gas and 2 more | none | no | no |
| 261 | `eia_crude_quality_monthly` | public | source | series | 13 | eia_crude_quality_monthly | none | no | no |
| 262 | `eia_crude_reserves_annual` | public | source | series | 13 | eia_crude_reserves_annual | none | no | no |
| 263 | `eia_crude_tank_farm_stocks_monthly` | public | source | series | 13 | eia_crude_tank_farm_stocks_monthly | none | no | no |
| 264 | `eia_drilling_monthly` | public | source | series | 13 | eia_drilling_monthly | none | no | no |
| 265 | `eia_energy_efficiency_state_annual` | public | source | series | 13 | eia861_efficiency, eia_energy_efficiency_state_annual | none | no | no |
| 266 | `eia_gas_balance_annual` | public | source | series | 13 | eia_gas_balance_annual, eia_gas_other_uses_state_annual, eia_gas_plant_processing_annual and 1 more | none | no | no |
| 267 | `eia_gas_consumers_state_annual` | public | source | series | 13 | eia_gas_consumers_state_annual | none | no | no |
| 268 | `eia_gas_consumption_state_monthly` | public | source | series | 13 | eia_gas_consumers_state_annual, eia_gas_consumption_state_monthly, eia_gas_for_others_annual and 4 more | none | no | no |
| 269 | `eia_gas_for_others_annual` | public | source | series | 13 | eia_gas_for_others_annual | none | no | no |
| 270 | `eia_gas_heat_content_monthly` | public | source | series | 13 | eia_gas_heat_content_monthly | none | no | no |
| 271 | `eia_gas_interstate_annual` | public | source | series | 13 | eia_gas_interstate_annual, eia_gas_pipeline_projects | none | no | no |
| 272 | `eia_gas_other_uses_state_annual` | public | source | series | 13 | eia_gas_other_uses_state_annual | none | no | no |
| 273 | `eia_gas_pipeline_projects` | public | source | events | 37 | eia_gas_pipeline_projects, eia_state_to_state_capacity, map_layers and 1 more | none | no | no |
| 274 | `eia_gas_plant_processing_annual` | public | source | series | 13 | eia_gas_plant_processing_annual | none | no | no |
| 275 | `eia_gas_production_state_monthly` | public | source | series | 13 | eia_basin_production_monthly, eia_gas_production_state_monthly, gas_balance_weekly and 1 more | none | no | no |
| 276 | `eia_gas_reserves_annual` | public | source | series | 13 | eia_gas_reserves_annual | none | no | no |
| 277 | `eia_gas_storage_capacity_monthly` | public | source | series | 13 | eia_gas_storage_capacity_monthly, eia_gas_storage_state_monthly, eia_gas_storage_type_monthly and 2 more | none | no | no |
| 278 | `eia_gas_storage_state_monthly` | public | source | series | 13 | eia_gas_balance_annual, eia_gas_storage_capacity_monthly, eia_gas_storage_state_monthly and 2 more | none | no | no |
| 279 | `eia_gas_storage_type_monthly` | public | source | series | 13 | eia_gas_storage_type_monthly | none | no | no |
| 280 | `eia_gas_trade_country_monthly` | public | source | series | 13 | cer_gas_trade, eia_gas_prices_state_monthly, eia_gas_trade_country_monthly and 4 more | none | no | no |
| 281 | `eia_gas_wells_annual` | public | source | series | 13 | eia_gas_wells_annual | none | no | no |
| 282 | `eia_ieo_projections` | public | source | series | 16 | eia_ieo_projections | none | no | no |
| 283 | `eia_international_electricity_annual` | public | source | series | 14 | cer_electricity_trade, eia_international_electricity_annual, eia_world_electricity_annual and 2 more | none | no | no |
| 284 | `eia_lng_liquefaction_projects` | public | source | entities | 35 | eia_lng_liquefaction_projects, map_layers, policy_monitor | none | no | no |
| 285 | `eia_lng_storage_annual` | public | source | series | 13 | eia_gas_storage_type_monthly, eia_lng_storage_annual | none | no | no |
| 286 | `eia_meters_state_annual` | public | source | series | 13 | eia861_meters_netmetering, eia_meters_state_annual | none | no | no |
| 287 | `eia_net_imports_monthly` | public | source | series | 14 | eia_net_imports_monthly | none | no | no |
| 288 | `eia_net_metering_state_annual` | public | source | series | 13 | eia861_meters_netmetering, eia_net_metering_state_annual, lbnl_tracking_the_sun | none | no | no |
| 289 | `eia_ngl_production_monthly` | public | source | series | 13 | eia_ngl_production_monthly, eia_petroleum_snd_monthly | none | no | no |
| 290 | `eia_nuclear_outages_daily` | public | source | series | 13 | eia_nuclear_outages | none | no | no |
| 291 | `eia_nuclear_outages_facility_daily` | public | source | series | 13 | eia_nuclear_outages | none | no | no |
| 292 | `eia_nuclear_outages_generator_daily` | public | source | series | 13 | eia_nuclear_outages, nuclear_fleet_status | none | no | no |
| 293 | `eia_oxygenate_production_monthly` | public | source | series | 13 | eia_biofuel_plants, eia_oxygenate_production_monthly, epa_rfs_rins | none | no | no |
| 294 | `eia_padd_crude_pipeline_flows` | public | source | series | 13 | eia_padd_crude_pipeline_flows, eia_padd_rail_barge_movements_monthly | none | no | energy_research_warehouse |
| 295 | `eia_padd_rail_barge_movements_monthly` | public | source | series | 13 | eia_padd_crude_pipeline_flows, eia_padd_rail_barge_movements_monthly | none | no | no |
| 296 | `eia_petroleum_exports_by_destination` | public | source | series | 13 | eia_crude_imports_by_country, eia_petroleum_exports_by_destination | none | no | no |
| 297 | `eia_petroleum_snd_monthly` | public | source | series | 13 | eia_net_imports_monthly, eia_ngl_production_monthly, eia_petroleum_exports_by_destination and 4 more | none | no | no |
| 298 | `eia_petroleum_stocks_monthly` | public | source | series | 13 | eia_petroleum_stocks_monthly, eia_petroleum_stocks_state_monthly, eia_petroleum_stocks_weekly | none | no | no |
| 299 | `eia_petroleum_stocks_state_monthly` | public | source | series | 15 | eia_petroleum_stocks_state_monthly | none | no | no |
| 300 | `eia_petroleum_stocks_weekly` | public | source | series | 13 | eia_petroleum_stocks_weekly, eia_petroleum_supply_weekly | none | no | energy_research_warehouse |
| 301 | `eia_petroleum_trade_weekly` | public | source | series | 13 | eia_crude_imports_by_country, eia_petroleum_supply_weekly, eia_petroleum_trade_weekly | none | no | energy_research_warehouse |
| 302 | `eia_power_co2_state_annual` | public | source | series | 13 | eia_power_co2_state_annual, epa_ghg_inventory_annual, owid_ember_electricity_annual and 1 more | none | no | no |
| 303 | `eia_power_costs_annual` | public | source | series | 13 | eia_power_costs_annual, price_board | none | no | no |
| 304 | `eia_power_fuel_stocks_monthly` | public | source | series | 13 | eia_power_fuel_stocks_monthly, eia_state_generation_monthly | none | no | no |
| 305 | `eia_primary_energy_monthly` | public | source | series | 13 | eia_ieo_projections, eia_primary_energy_monthly, eia_sector_energy_consumption_monthly | none | no | energy_research_warehouse |
| 306 | `eia_product_supplied_monthly` | public | source | series | 13 | eia_product_supplied_monthly, fhwa_motor_fuel_monthly | none | no | no |
| 307 | `eia_recs_households` | public | source | series | 17 | eia_buildings_surveys | none | no | no |
| 308 | `eia_refinery_capacity_annual` | public | source | series | 13 | eia_refinery_capacity_annual, eia_refinery_utilization_monthly, map_layers | none | no | no |
| 309 | `eia_refinery_inputs_monthly` | public | source | series | 13 | eia_crude_quality_monthly, eia_petroleum_snd_monthly, eia_refinery_capacity_annual and 3 more | none | no | no |
| 310 | `eia_refinery_production_monthly` | public | source | series | 13 | eia_petroleum_snd_monthly, eia_refinery_inputs_monthly, eia_refinery_production_monthly and 1 more | none | no | no |
| 311 | `eia_refinery_utilization_monthly` | public | source | series | 13 | eia_refinery_utilization_monthly | none | no | no |
| 312 | `eia_refinery_weekly` | public | source | series | 13 | eia_petroleum_supply_weekly, eia_refinery_capacity_annual, eia_refinery_inputs_monthly and 2 more | none | no | no |
| 313 | `eia_seds_residential_annual` | public | source | series | 15 | doe_lead_energy_burden, eia_seds_residential_annual, states_page | none | no | no |
| 314 | `eia_shale_gas_reserves_annual` | public | source | series | 13 | eia_shale_gas_reserves_annual | none | no | no |
| 315 | `eia_state_generation_monthly` | public | source | series | 13 | aedg_alaska_generation_monthly, cec_total_system_generation_annual, eia923_monthly and 7 more | none | no | energy_research_warehouse |
| 316 | `eia_state_source_disposition_annual` | public | source | series | 13 | dbedt_hawaii_electricity_annual, eia_state_source_disposition_annual, states_page | none | no | no |
| 317 | `eia_state_to_state_capacity` | public | source | series | 21 | eia_state_to_state_capacity | none | no | no |
| 318 | `eia_uranium_facilities` | public | source | entities | 23 | eia_uranium_production | none | no | no |
| 319 | `eia_uranium_marketing_annual` | public | source | series | 13 | eia_uranium_marketing_annual | none | no | no |
| 320 | `eia_uranium_production_quarterly` | public | source | series | 15 | eia_uranium_production | none | no | no |
| 321 | `eia_wood_pellets_monthly` | public | source | series | 13 | eia_wood_pellets_monthly | none | no | no |
| 322 | `eia_world_coal_annual` | public | source | series | 14 | eia_world_coal_energy | none | no | no |
| 323 | `eia_world_electricity_annual` | public | source | series | 14 | abs_suriname_electricity_annual, arse_burkina_electricity_annual, arsel_cameroon_electricity_annual and 27 more | none | no | no |
| 324 | `eia_world_energy_co2_annual` | public | source | series | 14 | eia_ieo_projections, eia_world_coal_energy | none | no | no |
| 325 | `eia_world_oil_gas_annual` | public | source | series | 14 | bcrp_peru_hydrocarbons_monthly, eia_world_oil_gas | none | no | no |
| 326 | `eia_world_oil_monthly` | public | source | series | 14 | eia_world_oil_gas | none | no | no |
| 585 | `eia_all_futures_prices` | internal | source | series | 13 | eia_all_futures_prices, eia_fuel_spot_prices, eia_product_spot_prices and 2 more | none | no | energy_research_warehouse_internal |
| 586 | `eia_ice_electricity_daily` | internal | source | series | 15 | eia_ice_electricity_daily, price_board | none | no | no |

### eia860 (9 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 55 | `eia860_generator_owners` | public | source | entities | 26 | companies, eia860_schedules | /companies, /companies/[id], /companies/[id]/rows and 5 more | no | no |
| 56 | `eia860_plants_annual` | public | source | entities | 51 | companies, eia860_environment, eia860_plants_annual and 6 more | /companies, /companies/[id], /companies/[id]/rows and 6 more | no | no |
| 327 | `eia860_boilers` | public | source | entities | 94 | eia860_environment, eia860_schedules | none | no | no |
| 328 | `eia860_cooling_systems` | public | source | entities | 56 | eia860_environment, eia860_schedules | none | no | no |
| 329 | `eia860_emission_controls` | public | source | entities | 32 | eia860_environment, eia860_schedules | none | no | no |
| 330 | `eia860_multifuel_generators` | public | source | entities | 55 | eia860_environment, eia860_schedules | none | no | no |
| 331 | `eia860_solar_generators` | public | source | entities | 55 | eia860_schedules, uspvdb_solar_facilities | none | no | no |
| 332 | `eia860_storage_generators` | public | source | entities | 65 | eia860_schedules | none | no | no |
| 333 | `eia860_wind_generators` | public | source | entities | 37 | eia860_schedules, lbnl_projects | none | no | no |

### eia860m (4 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 57 | `eia860m_operating_generators` | public | source | entities | 36 | automated_analysis_findings, companies, contracts and 27 more | /, /_retired/seller-original, /about and 13 more | no | energy_research_warehouse |
| 58 | `eia860m_planned_generators` | public | source | entities | 34 | companies, eia860m_operating_generators, eia860m_planned_generators and 12 more | /, /about, /companies and 14 more | no | energy_research_warehouse |
| 59 | `eia860m_retired_generators` | public | source | entities | 36 | eia860m_operating_generators, eia860m_planned_generators, eia860m_retired_generators and 9 more | /_retired/map-v2, /api/download, /data and 1 more | yes | energy_research_warehouse |
| 334 | `eia860m_retired_generators_all` | public | source | entities | 35 | automated_analysis_findings, eia860m_operating_generators, eia860m_planned_generators and 4 more | none | no | energy_research_warehouse |

### eia861 (13 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 60 | `eia861_delivery_only` | public | source | series | 20 | county_population_and_regions, eia861_delivery_only, ercot_node_wires_utilities and 1 more | /cost-of-power, /demand | no | no |
| 61 | `eia861_utility_data` | public | source | entities | 47 | companies, eia861_short_form, eia861_utility_data and 1 more | /companies, /companies/[id], /companies/[id]/rows and 5 more | no | no |
| 62 | `eia861_utility_sales` | public | source | series | 20 | census_bps_state_annual, census_cbp_hosting_annual, county_population_and_regions and 10 more | /cost-of-power, /demand | no | no |
| 335 | `eia861_advanced_meters` | public | source | series | 16 | eia861_meters_netmetering | none | no | no |
| 336 | `eia861_demand_response` | public | source | series | 16 | eia861_programs | none | no | no |
| 337 | `eia861_distributed_generation` | public | source | series | 17 | eia861_distribution, lbnl_tracking_the_sun | none | no | no |
| 338 | `eia861_distribution_systems` | public | source | series | 15 | eia861_distribution | none | no | no |
| 339 | `eia861_dynamic_pricing` | public | source | series | 36 | eia861_distribution, eia861_programs | none | no | no |
| 340 | `eia861_energy_efficiency` | public | source | series | 17 | eia861_efficiency | none | no | no |
| 341 | `eia861_net_metering` | public | source | series | 16 | eia861_distribution, eia861_meters_netmetering | none | no | no |
| 342 | `eia861_operational_data` | public | source | series | 18 | eia861_operations | none | no | no |
| 343 | `eia861_short_form` | public | source | series | 21 | eia861_operations, eia861_short_form | none | no | no |
| 344 | `eia861_utility_reliability` | public | source | series | 22 | doe_oe417_events, eia861_utility_reliability, policy_monitor | none | no | no |

### eia930 (37 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 63 | `eia930_all_demand` | public | source | series | 14 | ai_power_regions, caiso_alerts, california_reliability and 20 more | /, /_retired/network-original, /about and 11 more | yes | energy_research_warehouse |
| 64 | `eia930_all_emissions` | public | source | series | 14 | authority_facts, eia930_all_emissions, eia930_all_history and 6 more | /events, /events/uri-2021, /grid | yes | energy_research_warehouse |
| 65 | `eia930_all_generation` | public | source | series | 14 | eia930_all_demand, eia930_all_emissions, eia930_all_generation and 10 more | /, /_retired/mix-original, /about and 9 more | yes | energy_research_warehouse |
| 66 | `eia930_all_interchange` | public | source | series | 15 | eia930_all_demand, eia930_all_interchange, eia930_daily_interchange and 6 more | /, /_retired/network-original, /about and 9 more | no | energy_research_warehouse |
| 67 | `eia930_all_storage` | public | source | series | 14 | automated_analysis_findings, eia930_all_generation, eia930_all_storage and 3 more | /, /_retired/network-original, /about and 6 more | yes | energy_research_warehouse |
| 68 | `eia930_ba_demand_hourly` | public | source | series | 13 | eia930_region_hourly, forecast_error, interchange_pairs and 1 more | 1 site files | no | no |
| 69 | `eia930_daily_demand` | public | source | series | 15 | automated_analysis_findings, bpa_ba_hourly, eia930_all_demand and 8 more | /grid, /network | no | energy_research_warehouse |
| 70 | `eia930_daily_interchange` | public | source | series | 16 | ai_power_regions, automated_analysis_findings, ba_supply_monthly and 8 more | /_retired/network-original, /grid, /network and 1 more | no | energy_research_warehouse |
| 71 | `eia930_daily_total_interchange` | public | source | series | 15 | automated_analysis_findings, ba_supply_monthly, eia930_all_interchange and 5 more | /_retired/network-original | no | energy_research_warehouse |
| 72 | `eia930_demand_growth` | public | derived | series | 14 | ask_ercot, datacenter_cost, datacenter_pays_algorithm and 8 more | /, /_retired/demand-original, /about and 8 more | yes | energy_research_warehouse |
| 73 | `eia930_demand_weather` | public | derived | series | 18 | automated_analysis_findings, demand_growth, demand_weather and 2 more | /, /_retired/demand-weather, /about and 3 more | no | energy_research_warehouse |
| 74 | `eia930_event_hourly_interchange` | public | source | series | 16 | eia930_all_interchange, eia930_daily_interchange, eia930_daily_total_interchange and 3 more | /_retired/network-original, /grid, /network | no | energy_research_warehouse |
| 75 | `eia930_forecast_error_hourly` | public | derived | series | 11 | forecast_error | 1 site files | no | no |
| 76 | `eia930_generation_latest` | public | source | series | 13 | eia930_all_storage, generation_mix, generation_mix_hourly | /, /_retired/mix-original, /about and 3 more | yes | energy_research_warehouse |
| 77 | `eia930_region_fuel_hourly` | public | derived | series | 10 | authority_facts, eia930_region_fuel_hourly, regions_pages | /grid | no | no |
| 78 | `eia930_region_hourly` | public | derived | series | 13 | eia930_region_fuel_hourly, eia930_region_hourly, forecast_error and 2 more | 1 site files | no | no |
| 79 | `eia930_region_pair_hourly` | public | derived | series | 15 | eia930_region_hourly, interchange_pairs, regions_pages | /grid | no | no |
| 348 | `eia930_all_history` | public | source | series | 14 | eia930_all_demand, eia930_all_generation, eia930_all_history and 2 more | none | no | energy_research_warehouse |
| 349 | `eia930_ba_interchange_hourly_2018` | public | source | series | 12 | interchange_pairs | none | no | no |
| 350 | `eia930_ba_interchange_hourly_2019` | public | source | series | 12 | none | none | no | no |
| 351 | `eia930_ba_interchange_hourly_2020` | public | source | series | 12 | none | none | no | no |
| 352 | `eia930_ba_interchange_hourly_2021` | public | source | series | 12 | none | none | no | no |
| 353 | `eia930_ba_interchange_hourly_2022` | public | source | series | 12 | none | none | no | no |
| 354 | `eia930_ba_interchange_hourly_2023` | public | source | series | 12 | none | none | no | no |
| 355 | `eia930_ba_interchange_hourly_2024` | public | source | series | 12 | none | none | no | no |
| 356 | `eia930_ba_interchange_hourly_2025` | public | source | series | 12 | none | none | no | no |
| 357 | `eia930_ba_interchange_hourly_2026` | public | source | series | 12 | none | none | no | no |
| 358 | `eia930_ba_supply_hourly` | public | source | series | 13 | eia930_region_fuel_hourly, eia930_region_hourly, interchange_pairs and 1 more | none | no | no |
| 359 | `eia930_forecast_error_daily` | public | derived | series | 15 | forecast_error | none | no | no |
| 360 | `eia930_subba_demand_hourly` | public | source | series | 13 | eia930_all_demand, eia930_daily_demand, eia930_subba_demand and 1 more | none | no | no |
| 361 | `eia930_subba_demand_hourly_2019` | public | source | series | 13 | eia930_subba_demand | none | no | no |
| 362 | `eia930_subba_demand_hourly_2020` | public | source | series | 13 | eia930_subba_demand | none | no | no |
| 363 | `eia930_subba_demand_hourly_2021` | public | source | series | 13 | eia930_subba_demand | none | no | no |
| 364 | `eia930_subba_demand_hourly_2022` | public | source | series | 13 | eia930_subba_demand | none | no | no |
| 365 | `eia930_subba_demand_hourly_2023` | public | source | series | 13 | eia930_subba_demand | none | no | no |
| 366 | `eia930_subba_demand_hourly_2024` | public | source | series | 13 | eia930_subba_demand, packages | none | no | no |
| 367 | `eia930_subba_demand_hourly_2025` | public | source | series | 13 | eia930_subba_demand | none | no | no |

### energy (9 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 80 | `energy_companies` | public | model_extracted | entities | 26 | companies, energy_deals, thesis_builder | /, /_retired/board-original, /_retired/board-v3 and 29 more | yes | energy_research_warehouse |
| 81 | `energy_deals` | public | model_extracted | events | 49 | automated_analysis, companies, deal_counterparties and 4 more | /, /_retired/board-original, /_retired/board-v3 and 63 more | yes | energy_research_warehouse |
| 82 | `energy_projects` | public | derived | entities | 29 | ask, eia860m_operating_generators, eia860m_planned_generators and 6 more | /, /_retired/board-original, /_retired/board-v3 and 47 more | yes | energy_research_warehouse |
| 368 | `energy_charts_belgium_hourly` | public | source | series | 14 | energy_charts_belgium_hourly, energy_charts_central_europe | none | no | no |
| 369 | `energy_charts_central_europe` | public | source | series | 15 | bfe_ch_electricity_wednesdays, bfe_switzerland_electricity_monthly, energy_charts_central_europe | none | no | no |
| 370 | `energy_charts_italy_power` | public | source | series | 13 | energy_charts_italy_power, energy_charts_portugal_power | none | no | no |
| 371 | `energy_charts_portugal_power` | public | source | series | 13 | energy_charts_portugal_power | none | no | no |
| 372 | `energy_charts_southeast_europe_daily` | public | source | series | 15 | energy_charts_southeast_europe_daily | none | no | no |
| 587 | `energy_deals_evidence` | internal | model_extracted | events | 17 | deal_tracker, energy_deals | /deals | no | energy_research_warehouse_internal |

### ercot (39 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 83 | `ercot_4cp_intervals` | public | source | series | 18 | datacenter_cost, datacenter_pays_algorithm, ercot_4cp and 3 more | /board, /cost-of-power, /demand | yes | energy_research_warehouse |
| 84 | `ercot_all_hub_prices_history` | public | source | series | 14 | ai_power_regions, automated_analysis_findings, battery_awards and 20 more | /, /_retired/board-original, /about and 13 more | no | energy_research_warehouse |
| 85 | `ercot_as_prices` | public | source | series | 13 | battery_earns_algorithm, battery_stack, capacity_and_ancillary and 6 more | /api/ask, /api/download, /board and 1 more | yes | energy_research_warehouse |
| 86 | `ercot_as_prices_daily` | public | derived | series | 13 | ask_ercot, capacity_and_ancillary, ercot_as_prices_rollup and 1 more | 2 site files | yes | energy_research_warehouse |
| 87 | `ercot_as_prices_monthly` | public | derived | series | 13 | ask_ercot, capacity_and_ancillary, ercot_as_prices_rollup and 1 more | 2 site files | yes | energy_research_warehouse |
| 88 | `ercot_cdr_reserve_margins` | public | source | series | 15 | demand_growth, eia411, ercot_cdr_reserve_margins and 4 more | /, /_retired/board-original, /_retired/curtailment-original and 32 more | no | no |
| 89 | `ercot_hub_prices_daily` | public | derived | series | 13 | ercot_as_prices_rollup, ercot_hub_prices_daily, grid_network and 4 more | /_retired/board-v4, /api/ask | yes | energy_research_warehouse |
| 90 | `ercot_interconnection_queue` | public | source | entities | 26 | companies, datacenter_facilities, datacenter_tracker and 6 more | /companies, /companies/[id], /companies/[id]/rows and 7 more | yes | energy_research_warehouse |
| 91 | `ercot_large_load_status` | public | source | series | 15 | ask_ercot, datacenter_cost, datacenter_facilities and 5 more | /, /_retired/board-v3, /_retired/board-v4 and 51 more | yes | energy_research_warehouse |
| 92 | `ercot_node_places` | public | source | entities | 21 | ercot_node_places, ercot_node_planned_generation, ercot_node_transmission and 2 more | /cost-of-power, /demand | no | no |
| 93 | `ercot_peak_premium_annual` | public | derived | series | 13 | ercot_peak_premium, explorers, packages and 1 more | /, /_retired/board-original, /about and 7 more | yes | energy_research_warehouse |
| 94 | `ercot_peak_premium_monthly` | public | derived | series | 13 | ercot_peak_premium, explorers | /, /about, /data and 6 more | yes | energy_research_warehouse |
| 95 | `ercot_rtm_price_adders` | public | source | series | 13 | automated_analysis_findings, datacenter_pays_algorithm, ercot_rt_price_adders and 3 more | /board, /cost-of-power, /cost-of-power/tables.csv | yes | energy_research_warehouse |
| 96 | `ercot_storage_dam_awards_monthly` | public | derived | series | 13 | battery_awards, battery_earns_algorithm, ercot_dam_esr_awards and 3 more | /cost-of-power/battery/awards | yes | energy_research_warehouse |
| 97 | `ercot_storage_dam_offers_monthly` | public | derived | series | 13 | battery_awards, ercot_storage_dam_offers | /cost-of-power/battery/awards | yes | energy_research_warehouse |
| 98 | `ercot_storage_node_basis` | public | derived | series | 13 | battery_awards, ercot_dam_esr_awards, ercot_rtm_node_prices and 1 more | /cost-of-power/battery/awards | yes | energy_research_warehouse |
| 99 | `ercot_storage_rt_monthly` | public | derived | series | 13 | battery_awards, ercot_sced_esr_hourly, ercot_storage_realtime | /cost-of-power/battery/awards | yes | energy_research_warehouse |
| 100 | `ercot_transmission_projects` | public | source | events | 34 | ercot_node_transmission, ercot_transmission_projects, siting | /demand | no | no |
| 101 | `ercot_wind_solar_hsl_daily` | public | source | series | 13 | ask_ercot, curtailment, ercot_wind_solar_hsl_daily and 2 more | /, /_retired/curtailment-original, /about and 3 more | yes | energy_research_warehouse |
| 102 | `ercot_wind_solar_hsl_hourly` | public | source | series | 13 | curtailment, ercot_wind_solar_forecast, ercot_wind_solar_hsl_daily and 2 more | /, /about, /data and 1 more | no | energy_research_warehouse |
| 103 | `ercot_zone_load_hourly` | public | source | series | 13 | ask_ercot, automated_analysis_findings, datacenter_cost and 7 more | 1 site files | no | energy_research_warehouse |
| 104 | `ercot_zone_prices_history` | public | source | series | 14 | automated_analysis_findings, cost_of_power, datacenter_cost and 6 more | /board, /demand, /prices and 2 more | no | energy_research_warehouse |
| 381 | `ercot_as_quantities` | public | source | series | 13 | battery_awards, battery_stack, ercot_as_prices and 1 more | none | no | energy_research_warehouse |
| 382 | `ercot_cdr_units` | public | source | entities | 42 | ercot_cdr_units, ercot_node_places | none | no | no |
| 383 | `ercot_dam_cleared_energy` | public | source | series | 13 | caiso_dam_cleared_energy, ercot_dam_cleared_energy, ercot_zone_load_hourly and 1 more | none | no | energy_research_warehouse |
| 384 | `ercot_dam_esr_awards` | public | source | series | 31 | battery_awards, battery_earns_algorithm, ercot_cdr_units and 5 more | none | no | energy_research_warehouse |
| 385 | `ercot_grid_notices` | public | source | events | 17 | battery_stress_days, caiso_grid_emergencies, ercot_grid_notices and 1 more | none | yes | energy_research_warehouse |
| 386 | `ercot_node_planned_generation` | public | source | entities | 36 | eia860m_planned_generators, ercot_node_planned_generation | none | no | no |
| 387 | `ercot_node_transmission` | public | source | entities | 26 | ercot_node_transmission | none | no | no |
| 388 | `ercot_node_wires_utilities` | public | source | entities | 23 | ercot_node_wires_utilities | none | no | no |
| 389 | `ercot_peak_premium_node_monthly` | public | derived | series | 13 | ercot_peak_premium | none | yes | energy_research_warehouse |
| 390 | `ercot_rtm_node_prices` | public | source | series | 14 | ercot_dam_esr_awards, ercot_peak_premium, ercot_rtm_node_prices and 4 more | none | no | energy_research_warehouse |
| 391 | `ercot_sced_esr_hourly` | public | source | series | 34 | battery_awards, energy_charts_central_europe, ercot_sced_esr_hourly and 1 more | none | no | energy_research_warehouse |
| 392 | `ercot_storage_dam_offers_daily` | public | derived | series | 13 | ercot_dam_esr_awards, ercot_storage_dam_offers | none | no | energy_research_warehouse |
| 393 | `ercot_storage_rt_offers_monthly` | public | source | series | 13 | ercot_storage_realtime | none | yes | energy_research_warehouse |
| 394 | `ercot_wind_solar_forecast` | public | source | series | 13 | ercot_wind_solar_forecast, ercot_wind_solar_hsl_daily, ercot_wind_solar_hsl_hourly and 3 more | none | no | energy_research_warehouse |
| 395 | `ercot_wind_solar_hsl_monthly` | public | derived | series | 13 | ercot_wind_solar_hsl_hourly, ercot_wind_solar_output_hourly | none | no | energy_research_warehouse |
| 396 | `ercot_wind_solar_output_hourly` | public | source | series | 13 | curtailment, ercot_wind_solar_hsl_hourly, ercot_wind_solar_output_hourly | none | no | energy_research_warehouse |
| 588 | `ercot_node_prices_hourly` | internal | derived | series | 14 | node_basis, price_board | none | no | energy_research_warehouse_internal |

### erw_derived (33 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 105 | `ai_power_regions` | public | derived | series | 15 | ai_power_regions, automated_analysis_scanner, cost_of_power and 4 more | /reports/draft/ai-gigawatts | yes | energy_research_warehouse |
| 106 | `attention_index_weekly` | public | model_extracted | series | 10 | attention | /attention | yes | energy_research_warehouse |
| 107 | `attention_story_links` | public | model_extracted | events | 30 | attention | /attention | yes | energy_research_warehouse |
| 108 | `clean_energy_hourly` | public | derived | series | 16 | clean_energy, datacenter_cost, datacenter_pays_algorithm | /_retired/mix-clean, /cost-of-power, /cost-of-power/tables.csv and 1 more | no | energy_research_warehouse |
| 109 | `clean_energy_summary` | public | derived | series | 13 | clean_energy, datacenter_cost, datacenter_pays_algorithm | /, /_retired/mix-clean, /about and 5 more | yes | energy_research_warehouse |
| 110 | `event_study_estimates` | public | derived | series | 21 | ai_power_regions, california_reliability, event_study and 1 more | /events, /events/caiso-heat-2020, /events/caiso-heat-2022 and 8 more | no | energy_research_warehouse |
| 111 | `event_window_daily` | public | derived | series | 15 | automated_analysis_findings, california_reliability, cost_of_power and 8 more | /, /_retired/board-original, /_retired/board-v3 and 50 more | yes | energy_research_warehouse |
| 112 | `flex_alert_effects` | public | derived | series | 13 | caiso_alerts, flex_alert_scorecard, impossible_hours and 1 more | /grid/caiso/alerts | yes | energy_research_warehouse |
| 113 | `flex_alert_model` | public | derived | series | 13 | caiso_alerts, flex_alert_scorecard, impossible_hours and 1 more | /grid/caiso/alerts | yes | energy_research_warehouse |
| 114 | `forecast_tool_parameters` | public | derived | series | 17 | forecast | 1 site files | yes | energy_research_warehouse |
| 115 | `friction_index_weekly` | public | model_extracted | series | 10 | attention | /attention | yes | energy_research_warehouse |
| 116 | `generation_mix_hourly_profile` | public | derived | series | 13 | automated_analysis_findings, caiso_fuel_supply_history, eia930_region_fuel_hourly and 3 more | /, /_retired/mix-v2, /about and 3 more | yes | energy_research_warehouse |
| 117 | `generation_mix_records` | public | derived | series | 15 | caiso_fuel_supply_history, generation_mix_hourly, impossible_hours | /_retired/mix-v2, /grid | yes | energy_research_warehouse |
| 118 | `hub_price_comparison` | public | derived | series | 13 | datacenter_cost, hub_price_comparison, prices_map | /board, /cost-of-power, /cost-of-power/battery and 10 more | yes | energy_research_warehouse |
| 119 | `known_data_faults` | public | derived | events | 23 | automated_analysis_scanner, eia_state_generation_monthly, ercot_large_load_status and 3 more | /data/faults, /grid | yes | energy_research_warehouse |
| 120 | `merchant_revenue_monthly` | public | derived | series | 14 | ask, automated_analysis_findings, battery_stack and 5 more | /, /_retired/board-original, /_retired/curtailment-original and 38 more | yes | energy_research_warehouse |
| 121 | `nlr_jedi_multipliers` | public | derived | series | 31 | economic_impact, forecast | /, /about, /data and 2 more | yes | energy_research_warehouse |
| 122 | `node_basis_daily` | public | derived | series | 16 | automated_analysis, battery_earns_algorithm, ercot_cdr_units and 5 more | /cost-of-power, /demand, /research | no | no |
| 123 | `node_basis_summary` | public | derived | series | 16 | ask, battery_earns_algorithm, datacenter_cost and 6 more | /board, /cost-of-power, /cost-of-power/battery and 1 more | yes | energy_research_warehouse |
| 124 | `region_weather_hourly` | public | derived | series | 8 | forecast_error, region_weather, regions_pages | 1 site files | no | no |
| 125 | `scarcity_hours_by_grid` | public | derived | series | 14 | datacenter_cost, ercot_rtm_price_adders, iso_dam_hub_prices and 1 more | /cost-of-power, /cost-of-power/tables.csv | yes | energy_research_warehouse |
| 126 | `shoulder_hours_monthly` | public | derived | series | 13 | demand_growth, eia930_caiso_break, impossible_hours and 2 more | /, /about, /data and 3 more | yes | energy_research_warehouse |
| 127 | `state_generation_mix_monthly` | public | derived | series | 13 | generation_mix, generation_mix_hourly, noaa_uscrn_solar_monthly and 2 more | /, /_retired/mix-original, /about and 3 more | yes | energy_research_warehouse |
| 128 | `state_large_load_laws` | public | model_extracted | events | 27 | large_load_research, policy_monitor, siting and 1 more | /cost-of-power, /policy | no | energy_research_warehouse |
| 397 | `deal_counterparties` | public | model_extracted | entities | 27 | deal_counterparties, deal_tracker, energy_deals | none | no | energy_research_warehouse |
| 398 | `gas_balance_weekly` | public | derived | series | 14 | gas_balance_weekly | none | no | no |
| 399 | `generator_pipeline_by_grid` | public | derived | series | 19 | ask, generator_pipeline_by_grid | none | no | no |
| 400 | `nuclear_fleet_status` | public | derived | series | 18 | ask, nuclear_fleet_status | none | no | energy_research_warehouse |
| 401 | `resource_layer_features` | public | derived | entities | 24 | resource_layers_table | none | no | no |
| 402 | `subregion_demand_growth` | public | derived | series | 16 | demand_growth, subregion_demand_growth | none | no | no |
| 589 | `api_cost_ledger` | internal | derived | events | 19 | api_cost_ledger, attention, datacenter_projects_evidence and 2 more | /internal/costs | yes | energy_research_warehouse_internal |
| 590 | `texas_delivery_charges` | internal | model_extracted | events | 30 | ask_ercot, datacenter_cost, datacenter_pays_algorithm and 4 more | /cost-of-power | no | energy_research_warehouse_internal |
| 591 | `texas_transmission_matrix` | internal | model_extracted | events | 40 | ask_ercot, datacenter_cost, siting | /cost-of-power, /cost-of-power/months.csv, /cost-of-power/tables.csv and 2 more | no | energy_research_warehouse_internal |

### ferc714 (23 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 129 | `ferc714_forecast_growth` | public | derived | series | 14 | demand_growth, ferc714_forecast_growth, siting | /demand | no | no |
| 430 | `ferc714_planning_area_forecasts` | public | source | series | 14 | ferc714_forecast_growth | none | no | no |
| 600 | `ferc714_area_demand_2006` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 601 | `ferc714_area_demand_2007` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 602 | `ferc714_area_demand_2008` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 603 | `ferc714_area_demand_2009` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 604 | `ferc714_area_demand_2010` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 605 | `ferc714_area_demand_2011` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 606 | `ferc714_area_demand_2012` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 607 | `ferc714_area_demand_2013` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 608 | `ferc714_area_demand_2014` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 609 | `ferc714_area_demand_2015` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 610 | `ferc714_area_demand_2016` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 611 | `ferc714_area_demand_2017` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 612 | `ferc714_area_demand_2018` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 613 | `ferc714_area_demand_2019` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 614 | `ferc714_area_demand_2020` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 615 | `ferc714_area_demand_2021` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 616 | `ferc714_area_demand_2022` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 617 | `ferc714_area_demand_2023` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 618 | `ferc714_area_demand_2024` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 619 | `ferc714_area_demand_2025` | internal | source | series | 13 | ferc714_area_demand | none | no | no |
| 620 | `ferc714_respondents` | internal | source | entities | 18 | ferc714_area_demand, ferc714_forecast_growth | none | no | no |

### grid (5 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 130 | `grid_network_links` | public | derived | series | 15 | eia930_all_interchange, grid_network, grid_network_links and 1 more | /, /about, /data and 1 more | no | energy_research_warehouse |
| 131 | `grid_network_nodes` | public | derived | series | 16 | eia930_all_interchange, grid_network, grid_network_links and 1 more | /, /about, /data and 1 more | no | energy_research_warehouse |
| 132 | `grid_peak_vs_capacity` | public | derived | series | 17 | ask, datacenter_facilities, datacenter_tracker and 6 more | /, /_retired/board-original, /_retired/curtailment-original and 32 more | yes | no |
| 133 | `grid_stress_yearly` | public | derived | series | 14 | ask_ercot, automated_analysis_findings, datacenter_cost and 2 more | /, /_retired/mix-stress, /about and 5 more | yes | energy_research_warehouse |
| 431 | `grid_stress_days` | public | derived | series | 18 | ercot_grid_notices, stress_days | none | yes | energy_research_warehouse |

### interchange (3 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 134 | `interchange_pair_monthly` | public | derived | series | 18 | interchange_pairs | 1 site files | no | no |
| 432 | `interchange_event_pairs` | public | derived | series | 22 | interchange_pairs | none | no | no |
| 433 | `interchange_pair_daily` | public | derived | series | 18 | interchange_pairs | none | no | no |

### interconnection (5 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 135 | `interconnection_agreements_by_grid` | public | derived | series | 13 | interconnection_agreements, siting | /demand | no | no |
| 136 | `interconnection_durations` | public | derived | entities | 26 | automated_analysis, interconnection_durations, large_load_waits and 1 more | /cost-of-power, /demand, /research | yes | no |
| 137 | `interconnection_queue_summary` | public | derived | series | 13 | ask_ercot, datacenter_cost, datacenter_pays_algorithm and 5 more | /_retired/map-v2, /board, /cost-of-power and 11 more | yes | energy_research_warehouse |
| 434 | `interconnection_agreements_signed` | public | derived | entities | 26 | interconnection_agreements | none | no | no |
| 435 | `interconnection_durations_summary` | public | derived | series | 13 | ask, interconnection_durations | none | yes | no |

### iso (12 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 138 | `iso_curtailment_monthly` | public | derived | series | 13 | ask_ercot, automated_analysis_findings, caiso_curtailment_daily and 3 more | /, /_retired/curtailment-original, /about and 3 more | yes | energy_research_warehouse |
| 139 | `iso_dam_hub_prices` | public | source | series | 13 | battery_earns_algorithm, battery_stack, cost_of_power and 15 more | /, /_retired/board-original, /_retired/board-v3 and 39 more | yes | energy_research_warehouse |
| 140 | `iso_hub_prices_history` | public | source | series | 13 | ai_power_regions, automated_analysis_findings, battery_earns_algorithm and 22 more | /_retired/board-v4, /board, /board/rows and 11 more | no | energy_research_warehouse |
| 141 | `iso_queue_snapshot_summary` | public | derived | series | 16 | iso_queue_snapshot_summary, siting | /demand | no | no |
| 142 | `iso_queue_statistics` | public | derived | series | 17 | energy_projects, explorers, interconnection_durations and 3 more | /about, /api/analysis, /api/download and 34 more | yes | energy_research_warehouse |
| 143 | `iso_reserve_margin_reports` | public | source | series | 19 | demand_growth, reserve_margin_reports, siting | /demand | yes | energy_research_warehouse |
| 144 | `iso_rt_top_intervals` | public | derived | series | 13 | iso_trader_daily, price_board, trader_view | /_retired/markets | yes | energy_research_warehouse |
| 145 | `iso_rtm_hub_prices` | public | source | series | 13 | automated_analysis_findings, battery_earns_algorithm, battery_game and 17 more | /, /_retired/board-original, /about and 11 more | yes | energy_research_warehouse |
| 146 | `iso_trader_daily` | public | derived | series | 13 | iso_trader_daily, price_board | /, /_retired/board-original, /_retired/board-v3 and 26 more | yes | energy_research_warehouse |
| 147 | `iso_zone_prices_history` | public | source | series | 13 | automated_analysis_findings, cost_of_power, datacenter_cost and 9 more | /board | no | energy_research_warehouse |
| 436 | `iso_hub_prices_history_2018` | public | source | series | 13 | hub_prices_history_2018 | none | no | no |
| 621 | `iso_all_capacity_prices` | internal | source | series | 17 | battery_stack, capacity_and_ancillary, datacenter_pays_algorithm and 6 more | /cost-of-power, /demand | no | energy_research_warehouse_internal |

### isone (9 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 148 | `isone_dam_zone_prices` | public | source | series | 13 | datacenter_cost, datacenter_pays_algorithm, hub_price_comparison and 11 more | /_retired/board-original, /curtailment, /prices/compare | yes | energy_research_warehouse |
| 149 | `isone_interconnection_queue` | public | source | entities | 26 | ask, energy_projects, interconnection_explorer and 2 more | /api/ask | yes | energy_research_warehouse |
| 150 | `isone_rtm_zone_prices_hourly` | public | source | series | 13 | datacenter_cost, datacenter_pays_algorithm, hub_price_comparison and 7 more | /_retired/board-original, /prices/compare | yes | energy_research_warehouse |
| 437 | `isone_rtm_zone_prices` | public | source | series | 13 | datacenter_cost, datacenter_pays_algorithm, hub_price_comparison and 5 more | none | yes | energy_research_warehouse |
| 622 | `isone_as_prices` | internal | source | series | 13 | battery_stack, capacity_and_ancillary, isone_as_prices and 2 more | none | no | energy_research_warehouse_internal |
| 623 | `isone_dam_cleared_energy` | internal | source | series | 13 | caiso_dam_cleared_energy, isone_dam_cleared_energy, supply_and_trade | none | no | energy_research_warehouse_internal |
| 624 | `isone_ddg_undelivered_monthly` | internal | source | series | 13 | ask_ercot, curtailment, isone_ddg_undelivered_monthly | 1 site files | no | energy_research_warehouse_internal |
| 625 | `isone_zone_load_hourly` | internal | source | series | 13 | ask_ercot, datacenter_cost, isone_dam_cleared_energy and 1 more | 1 site files | no | energy_research_warehouse_internal |
| 626 | `isone_zone_prices_history` | internal | source | series | 13 | ask_ercot, automated_analysis_findings, datacenter_cost and 4 more | 1 site files | no | energy_research_warehouse_internal |

### large (9 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 151 | `large_load_connection_rules` | public | source | events | 26 | large_load_connection_rules, large_load_research, large_load_tariffs and 1 more | /demand | no | energy_research_warehouse |
| 152 | `large_load_public` | public | model_extracted | events | 33 | authority_facts, datacenter_cost, datacenter_pays_algorithm and 1 more | /cost-of-power, /learn/problems | yes | energy_research_warehouse |
| 153 | `large_load_rules` | public | model_extracted | events | 35 | datacenter_cost, datacenter_pays_algorithm, large_load_connection_rules and 4 more | /cost-of-power, /demand, /policy | no | energy_research_warehouse |
| 438 | `large_load_rule_reads` | public | model_extracted | events | 22 | policy_monitor | none | no | energy_research_warehouse |
| 627 | `large_load_document_verdicts` | internal | derived | events | 22 | large_load_public | none | no | energy_research_warehouse_internal |
| 628 | `large_load_rules_internal` | internal | model_extracted | events | 35 | datacenter_cost, policy_monitor, vascc_pause | none | no | energy_research_warehouse_internal |
| 629 | `large_load_statements` | internal | model_extracted | events | 44 | datacenter_cost, datacenter_pays_algorithm, large_load_connection_rules and 3 more | none | no | energy_research_warehouse_internal |
| 630 | `large_load_wait_summary` | internal | derived | series | 16 | large_load_waits | none | no | no |
| 631 | `large_load_waits` | internal | derived | events | 50 | datacenter_cost, datacenter_pays_algorithm, large_load_public and 4 more | /cost-of-power, /demand | no | energy_research_warehouse_internal |

### lbnl (9 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 154 | `lbnl_interconnection_queue` | public | source | entities | 40 | ask, automated_analysis_findings, caiso_interconnection_queue and 13 more | /cost-of-power, /demand, /queues and 2 more | yes | energy_research_warehouse |
| 155 | `lbnl_solar_projects` | public | source | entities | 56 | forecast, lbnl_hybrid_plants, lbnl_ppa_prices and 1 more | /impact | no | no |
| 156 | `lbnl_wind_capacity_factors` | public | source | series | 15 | eia_capacity_factors, forecast, lbnl_projects | /impact | no | no |
| 439 | `lbnl_hybrid_ppa_prices` | public | source | events | 34 | lbnl_hybrid_plants, lbnl_ppa_prices, lbnl_projects and 1 more | none | no | no |
| 440 | `lbnl_ppa_prices` | public | source | events | 18 | lbnl_ppa_prices, lbnl_projects, price_board | none | no | no |
| 441 | `lbnl_tracking_the_sun` | public | source | series | 14 | lbnl_tracking_the_sun | none | no | no |
| 442 | `lbnl_wind_costs` | public | source | series | 16 | lbnl_projects | none | no | no |
| 443 | `lbnl_wind_turbine_orders` | public | source | events | 14 | lbnl_projects | none | no | no |
| 632 | `lbnl_hybrid_plants` | internal | source | entities | 40 | lbnl_hybrid_plants | none | no | no |

### news (3 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 157 | `news_index` | public | model_extracted | events | 11 | attention, datacenter_facilities, miso_pause and 1 more | /, /_retired/ask-original, /_retired/board-original and 68 more | yes | energy_research_warehouse |
| 633 | `news_scores_shadow` | internal | model_extracted | events | 20 | news_scores_shadow | none | no | energy_research_warehouse_internal |
| 634 | `news_stories` | internal | model_extracted | events | 29 | attention, companies, datacenter_projects and 7 more | /deals, /deals/comparables, /deals/v2 and 2 more | no | energy_research_warehouse_internal |

### noaa (21 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 158 | `noaa_grid_weather_hourly` | public | source | series | 15 | demand_weather, noaa_grid_weather_daily, noaa_grid_weather_hourly and 4 more | /_retired/demand-weather, /demand | no | energy_research_warehouse |
| 159 | `noaa_grid_weather_stations` | public | source | series | 23 | automated_analysis_scanner, census_metro_population, demand_weather and 5 more | /_retired/demand-weather, /demand | no | energy_research_warehouse |
| 160 | `noaa_isd_hourly` | public | source | series | 15 | automated_analysis_scanner, caiso_alerts, california_reliability and 5 more | /events, /events/caiso-heat-2022, /grid/caiso/alerts | no | energy_research_warehouse |
| 444 | `noaa_climdiv_state_monthly` | public | source | series | 14 | noaa_climdiv_state_monthly, noaa_cpc_oni_monthly | none | no | no |
| 445 | `noaa_cpc_degree_days_daily` | public | source | series | 14 | noaa_climdiv_state_monthly, noaa_cpc_degree_days_daily, noaa_cpc_oni_monthly | none | no | no |
| 446 | `noaa_cpc_oni_monthly` | public | source | series | 14 | noaa_cpc_oni_monthly | none | no | no |
| 447 | `noaa_grid_weather_daily` | public | source | series | 15 | demand_weather, noaa_cpc_degree_days_daily, noaa_grid_weather_daily and 4 more | none | no | energy_research_warehouse |
| 448 | `noaa_ncei_billion_disasters` | public | source | events | 18 | events, noaa_ncei_billion_disasters | none | no | no |
| 449 | `noaa_ncei_storm_events` | public | source | events | 42 | noaa_ncei_billion_disasters, noaa_ncei_storm_events | none | no | no |
| 450 | `noaa_region_station_hourly_2018` | public | source | series | 7 | none | none | no | no |
| 451 | `noaa_region_station_hourly_2019` | public | source | series | 7 | none | none | no | no |
| 452 | `noaa_region_station_hourly_2020` | public | source | series | 7 | none | none | no | no |
| 453 | `noaa_region_station_hourly_2021` | public | source | series | 7 | none | none | no | no |
| 454 | `noaa_region_station_hourly_2022` | public | source | series | 7 | none | none | no | no |
| 455 | `noaa_region_station_hourly_2023` | public | source | series | 7 | none | none | no | no |
| 456 | `noaa_region_station_hourly_2024` | public | source | series | 7 | none | none | no | no |
| 457 | `noaa_region_station_hourly_2025` | public | source | series | 7 | none | none | no | no |
| 458 | `noaa_region_station_hourly_2026` | public | source | series | 7 | none | none | no | no |
| 459 | `noaa_region_stations` | public | derived | series | 20 | region_weather | none | no | no |
| 460 | `noaa_station_weather_hourly` | public | source | series | 14 | demand_weather, noaa_grid_weather_daily, noaa_grid_weather_hourly and 4 more | none | no | energy_research_warehouse |
| 461 | `noaa_uscrn_solar_monthly` | public | source | series | 18 | noaa_uscrn_solar_monthly | none | no | no |

### nrc (7 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 161 | `nrc_power_reactors` | public | source | entities | 39 | companies, ieso_generation_fuel_hourly, nrc_license_actions and 4 more | /companies, /companies/[id], /companies/[id]/rows and 5 more | no | no |
| 462 | `nrc_advanced_reactor_preapplicants` | public | source | entities | 18 | nrc_new_reactors, policy_monitor | none | no | no |
| 463 | `nrc_event_notifications` | public | source | events | 35 | gfz_kp_index_3h, nrc_event_notifications, nrc_rop_findings | none | no | no |
| 464 | `nrc_license_actions` | public | source | events | 22 | nrc_license_actions, policy_monitor | none | no | no |
| 465 | `nrc_new_reactor_applications` | public | source | events | 27 | nrc_new_reactors, policy_monitor | none | no | no |
| 466 | `nrc_reactor_status` | public | source | series | 13 | generation_mix_hourly, nrc_event_notifications, nrc_power_reactors and 1 more | none | no | energy_research_warehouse |
| 467 | `nrc_rop_findings` | public | source | events | 29 | nrc_rop_findings | none | no | no |

### nyiso (7 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 162 | `nyiso_as_prices` | public | source | series | 13 | battery_stack, capacity_and_ancillary, nyiso_as_prices and 2 more | /board, /board/rows, /board/rows/python and 2 more | no | energy_research_warehouse |
| 163 | `nyiso_dam_zone_prices` | public | source | series | 13 | ask, battery_stack, datacenter_cost and 13 more | /_retired/board-original, /cost-of-power/battery, /curtailment and 2 more | yes | energy_research_warehouse |
| 164 | `nyiso_interconnection_queue` | public | source | entities | 26 | ask, caiso_interconnection_queue, companies and 8 more | /companies, /companies/[id], /companies/[id]/rows and 5 more | yes | energy_research_warehouse |
| 165 | `nyiso_load_queue` | public | source | entities | 44 | ask_ercot, datacenter_cost, iso_queue_snapshot_summary and 2 more | /cost-of-power, /demand | no | energy_research_warehouse |
| 166 | `nyiso_rtm_zone_prices` | public | source | series | 13 | battery_stack, datacenter_cost, datacenter_pays_algorithm and 8 more | /_retired/board-original, /cost-of-power/battery, /prices/compare | yes | energy_research_warehouse |
| 468 | `nyiso_dam_cleared_energy` | public | source | series | 13 | caiso_dam_cleared_energy, nyiso_dam_cleared_energy, supply_and_trade | none | no | energy_research_warehouse |
| 469 | `nyiso_zone_load_hourly` | public | source | series | 13 | datacenter_cost, datacenter_pays_algorithm, eia930_all_demand and 2 more | none | no | energy_research_warehouse |

### other_sources (154 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 167 | `ai_energy_published` | public | source | events | 26 | ai_energy_published | /ai-energy | no | no |
| 168 | `carb_auction_allowance_prices` | public | source | series | 13 | carb_auction_allowance_prices, generator_earns_algorithm, price_board and 2 more | /board | no | energy_research_warehouse |
| 169 | `carb_lcfs_credit_prices` | public | source | series | 13 | carb_lcfs_credit_prices, price_board | /board | no | energy_research_warehouse |
| 170 | `cftc_cot_positions` | public | source | series | 13 | automated_analysis_scanner, cftc_cot_positions, supply_and_trade | /, /about, /data and 2 more | no | energy_research_warehouse |
| 171 | `egrid_power_plants` | public | source | entities | 60 | egrid_power_plants, egrid_subregions_annual, eia923_plant_fuel_annual and 2 more | /cost-of-power, /demand | no | no |
| 172 | `eia411_capacity_margins_annual` | public | source | series | 14 | eia411, siting | /demand | no | no |
| 173 | `frb_treasury_yields` | public | source | series | 13 | frb_treasury_yields, frb_utility_output_monthly, price_board | /board | no | energy_research_warehouse |
| 174 | `hifld_transmission_lines` | public | source | entities | 27 | map_layers | 1 site files | no | no |
| 175 | `imf_commodity_prices` | public | source | series | 13 | imf_commodity_prices, price_board, usgs_mcs_critical_minerals and 1 more | /_retired/board-v4, /board | no | energy_research_warehouse |
| 176 | `impact_tax_rules` | public | source | events | 34 | economic_impact, forecast, impact_tax_rules | /, /about, /data and 2 more | yes | energy_research_warehouse |
| 177 | `rrc_lease_production_monthly` | public | source | series | 24 | rrc_lease_production_monthly, severance | /severance/lease/real | no | energy_research_warehouse |
| 178 | `weather_obs_hourly` | public | source | series | 13 | events, noaa_isd_hourly, weather_forecast_hourly and 1 more | /grid | yes | energy_research_warehouse |
| 478 | `abs_suriname_electricity_annual` | public | source | series | 14 | abs_suriname_electricity_annual | none | no | no |
| 479 | `aedg_alaska_generation_monthly` | public | source | series | 13 | aedg_alaska_generation_monthly | none | no | no |
| 480 | `aeso_alberta_load_hourly` | public | source | series | 13 | aeso_alberta_load_hourly | none | no | no |
| 481 | `aneel_siga_plants` | public | source | entities | 30 | aneel_siga_plants | none | no | no |
| 482 | `asli_liechtenstein_electricity_annual` | public | source | series | 15 | asli_liechtenstein_electricity_annual | none | no | no |
| 483 | `asub_aland_electricity_annual` | public | source | series | 13 | asub_aland_electricity_annual, asub_aland_electricity_sales_annual | none | no | no |
| 484 | `asub_aland_electricity_sales_annual` | public | source | series | 13 | asub_aland_electricity_sales_annual | none | no | no |
| 485 | `bcrp_peru_electricity_monthly` | public | source | series | 14 | bcrp_peru_electricity_monthly | none | no | no |
| 486 | `bcrp_peru_hydrocarbons_monthly` | public | source | series | 14 | bcrp_peru_hydrocarbons_monthly | none | no | no |
| 487 | `bfe_ch_electricity_wednesdays` | public | source | series | 15 | bfe_ch_electricity_wednesdays | none | no | no |
| 488 | `bfe_switzerland_electricity_monthly` | public | source | series | 14 | bfe_switzerland_electricity_monthly | none | no | no |
| 489 | `blm_ca_renewable_rows` | public | source | entities | 30 | blm_ca_renewable_rows | none | no | no |
| 490 | `blm_oil_gas_statistics_annual` | public | source | series | 16 | blm_oil_gas_statistics_annual, policy_monitor | none | no | no |
| 491 | `bpa_ba_hourly` | public | source | series | 16 | bpa_ba_hourly | none | no | no |
| 492 | `bsee_offshore_incidents` | public | source | events | 31 | bsee_offshore_incidents | none | no | no |
| 493 | `cbs_curacao_electricity_annual` | public | source | series | 13 | cbs_curacao_electricity_annual | none | no | no |
| 494 | `cbs_netherlands_electricity_monthly` | public | source | series | 15 | cbs_netherlands_electricity_monthly | none | no | no |
| 495 | `cec_total_system_generation_annual` | public | source | series | 15 | cec_total_system_generation_annual | none | no | no |
| 496 | `censtatd_hk_electricity` | public | source | series | 13 | censtatd_hk_electricity | none | no | no |
| 497 | `cso_ireland_electricity_monthly` | public | source | series | 14 | cso_ireland_electricity_monthly | none | no | no |
| 498 | `czso_cz_regional_electricity_annual` | public | source | series | 16 | czso_cz_regional_electricity_annual | none | no | no |
| 499 | `destatis_de_electricity_monthly` | public | source | series | 15 | destatis_de_electricity_monthly | none | no | no |
| 500 | `dfe_ni_electricity_monthly` | public | source | series | 14 | dfe_ni_electricity_monthly | none | no | no |
| 501 | `dosm_malaysia_electricity_monthly` | public | source | series | 13 | dosm_malaysia_electricity_monthly | none | no | no |
| 502 | `dst_dk_electricity_supply_annual` | public | source | series | 13 | dst_dk_electricity_supply_annual | none | no | no |
| 503 | `edf_sei_islands_electricity_annual` | public | source | series | 13 | edf_sei_islands_electricity_annual | none | no | no |
| 504 | `egrid_subregions_annual` | public | source | series | 13 | egrid_subregions_annual | none | no | no |
| 505 | `eia861m_utility_sales_monthly` | public | source | series | 17 | eia861_utility_sales, eia861m_utility_sales_monthly, eia_retail_sales_monthly and 1 more | none | no | no |
| 506 | `elexon_gb_demand_daily` | public | source | series | 15 | desnz_uk_electricity_quarterly, desnz_uk_plant_loads_annual, elexon_gb_demand_daily | none | no | no |
| 507 | `emi_nz_generation_demand_monthly` | public | source | series | 15 | emi_nz_generation_demand_monthly | none | no | no |
| 508 | `energinet_dk_production_hourly` | public | source | series | 14 | energinet_dk_production_hourly, ens_denmark_electricity_monthly | none | no | no |
| 509 | `epe_brazil_consumption_monthly` | public | source | series | 14 | epe_brazil_consumption_monthly | none | no | no |
| 510 | `epra_kenya_electricity_annual` | public | source | series | 13 | epra_kenya_electricity_annual | none | no | no |
| 511 | `fbos_fiji_electricity_annual` | public | source | series | 14 | fbos_fiji_electricity_annual | none | no | no |
| 512 | `fema_disaster_declarations` | public | source | events | 23 | fema_disaster_declarations | none | no | no |
| 513 | `fhwa_motor_fuel_monthly` | public | source | series | 15 | fhwa_motor_fuel_monthly | none | no | no |
| 514 | `frb_utility_output_monthly` | public | source | series | 13 | frb_utility_output_monthly | none | no | no |
| 515 | `gfz_kp_index_3h` | public | source | series | 15 | gfz_kp_index_3h | none | no | no |
| 516 | `hagstofa_iceland_power_annual` | public | source | series | 14 | hagstofa_iceland_power_annual | none | no | no |
| 517 | `hagstova_faroe_electricity_annual` | public | source | series | 14 | hagstova_faroe_electricity_annual | none | no | no |
| 518 | `ieso_generation_fuel_hourly` | public | source | series | 14 | ieso_generation_fuel_hourly | none | no | no |
| 519 | `ieso_ontario_demand_hourly` | public | source | series | 13 | ieso_generation_fuel_hourly, ieso_ontario_demand_hourly, statcan_electricity_generation_monthly | none | no | no |
| 520 | `ilr_luxembourg_electricity` | public | source | series | 15 | ilr_luxembourg_electricity | none | no | no |
| 521 | `ine_es_dwellings_electricity_2021` | public | source | series | 14 | ine_es_dwellings_electricity_2021 | none | no | no |
| 522 | `irs_soi_energy_credits_annual` | public | source | series | 14 | irs_soi_energy_credits_annual | none | no | no |
| 523 | `miso_interconnection_queue` | public | source | entities | 26 | interconnection_explorer, isone_interconnection_queue, miso_interconnection_queue and 2 more | none | yes | energy_research_warehouse |
| 524 | `msha_coal_mines` | public | source | entities | 23 | msha_coal_mines | none | no | no |
| 525 | `msha_coal_production_quarterly` | public | source | series | 15 | msha_coal_mines | none | no | no |
| 526 | `ncsi_oman_electricity_annual` | public | source | series | 15 | ncsi_oman_electricity_annual | none | no | no |
| 527 | `nhc_hurdat2_track_points` | public | source | events | 23 | nhc_hurdat2_track_points | none | no | no |
| 528 | `nlr_atb_electricity_costs` | public | source | series | 26 | battery_sourced_ranges, lbnl_projects, nlr_atb_electricity_costs | none | no | no |
| 529 | `ntd_transit_energy_annual` | public | source | series | 22 | ntd_transit_energy_annual | none | no | no |
| 530 | `nve_norway_reservoirs_weekly` | public | source | series | 14 | nve_norway_reservoirs_weekly | none | no | no |
| 531 | `ons_brazil_balance_hourly` | public | source | series | 14 | ons_brazil_balance_hourly | none | no | no |
| 532 | `owid_ember_electricity_annual` | public | source | series | 15 | amm_guatemala_generation_monthly, bfe_switzerland_electricity_monthly, cbs_netherlands_electricity_monthly and 51 more | none | no | no |
| 533 | `ree_spain_balance_monthly` | public | source | series | 15 | ree_spain_balance_monthly | none | no | no |
| 534 | `rte_eco2mix_france_halfhourly` | public | source | series | 16 | rte_eco2mix_france_halfhourly | none | no | no |
| 535 | `scb_sweden_electricity_monthly` | public | source | series | 14 | scb_sweden_electricity_monthly, svk_sweden_production_hourly | none | no | no |
| 536 | `scripps_co2_mlo_monthly` | public | source | series | 14 | scripps_co2_mlo_monthly | none | no | no |
| 537 | `singstat_singapore_electricity` | public | source | series | 15 | singstat_singapore_electricity | none | no | no |
| 538 | `smard_germany_monthly` | public | source | series | 14 | destatis_de_electricity_monthly, energy_charts_central_europe, smard_germany_monthly | none | no | no |
| 539 | `sne_panama_electricity_annual` | public | source | series | 13 | sne_panama | none | no | no |
| 540 | `sne_panama_generation_monthly` | public | source | series | 13 | sne_panama | none | no | no |
| 541 | `sors_serbia_electricity_annual` | public | source | series | 14 | sors_serbia_electricity_annual | none | no | no |
| 542 | `ssb_norway_electricity_monthly` | public | source | series | 14 | eurostat_electricity_consumption_annual, ssb_norway_electricity_monthly, statnett_norway_daily | none | no | no |
| 543 | `stat_kz_kazakhstan_electricity_annual` | public | source | series | 13 | stat_kz_kazakhstan_electricity_annual | none | no | no |
| 544 | `stat_tj_tajikistan_electricity_annual` | public | source | series | 13 | stat_tj_tajikistan_electricity_annual | none | no | no |
| 545 | `statat_austria_electricity_annual` | public | source | series | 13 | statat_austria_electricity_annual | none | no | no |
| 546 | `statat_austria_electricity_monthly` | public | source | series | 13 | statat_austria_electricity_monthly | none | no | no |
| 547 | `statbank_moldova_electricity_monthly` | public | source | series | 14 | makstat_macedonia_electricity_monthly, statbank_moldova_electricity_monthly | none | no | no |
| 548 | `statbel_be_electricity_production_annual` | public | source | series | 13 | statbel_be_electricity_production_annual | none | no | no |
| 549 | `statee_estonia_electricity_monthly` | public | source | series | 14 | statee_estonia_electricity_monthly | none | no | no |
| 550 | `statfi_finland_electricity_monthly` | public | source | series | 14 | statfi_finland_electricity_monthly | none | no | no |
| 551 | `statsbots_botswana_electricity_monthly` | public | source | series | 13 | statsbots_botswana_electricity_monthly | none | no | no |
| 552 | `statsmu_mauritius_electricity_annual` | public | source | series | 13 | statsmu_mauritius_electricity_annual | none | no | no |
| 553 | `usace_nid_dams` | public | source | entities | 35 | usace_nid_dams | none | no | no |
| 554 | `usdm_drought_state_weekly` | public | source | series | 15 | usdm_drought_state_weekly | none | no | no |
| 555 | `uspvdb_solar_facilities` | public | source | entities | 39 | blm_ca_renewable_rows, lbnl_projects, uspvdb_solar_facilities | none | no | no |
| 556 | `uswtdb_wind_turbines` | public | source | entities | 40 | blm_ca_renewable_rows, uspvdb_solar_facilities, uswtdb_wind_turbines and 1 more | none | no | no |
| 557 | `wapa_energy_sales_annual` | public | source | series | 13 | wapa_energy_sales_annual | none | no | no |
| 558 | `weather_forecast_hourly` | public | source | series | 13 | weather_forecast_hourly, weather_obs_hourly | none | yes | energy_research_warehouse |
| 559 | `wfigs_wildfires` | public | source | events | 26 | wfigs_wildfires | none | no | no |
| 636 | `amm_guatemala_generation_monthly` | internal | source | series | 13 | amm_guatemala_generation_monthly | none | no | no |
| 637 | `arse_burkina_electricity_annual` | internal | source | series | 14 | arse_burkina_electricity_annual | none | no | no |
| 638 | `arsel_cameroon_electricity_annual` | internal | source | series | 14 | arsel_cameroon_electricity_annual | none | no | no |
| 639 | `ask_kosovo_electricity_monthly` | internal | source | series | 14 | ask_kosovo_electricity_monthly | none | no | no |
| 640 | `bchydro_ba_load_hourly` | internal | source | series | 13 | bchydro_ba_load_hourly | none | no | no |
| 641 | `cea_india_psp_annual` | internal | source | series | 16 | cea_india_psp_annual | none | no | no |
| 642 | `ceb_srilanka_electricity_annual` | internal | source | series | 13 | ceb_srilanka_electricity_annual | none | no | no |
| 643 | `cence_costarica_generation_monthly` | internal | source | series | 15 | cence_costarica_generation_monthly | none | no | no |
| 644 | `cisos_cook_electricity_quarterly` | internal | source | series | 14 | cisos_cook_electricity_quarterly | none | no | no |
| 645 | `cosit_iraq_electricity_annual` | internal | source | series | 13 | cosit_iraq_electricity_annual | none | no | no |
| 646 | `csp_latvia_electricity_monthly` | internal | source | series | 14 | csp_latvia_electricity_monthly | none | no | no |
| 647 | `dbedt_hawaii_electricity_annual` | internal | source | series | 14 | dbedt_hawaii_electricity_annual | none | no | no |
| 648 | `derk_bih_electricity_annual` | internal | source | series | 14 | derk_bih_electricity_annual | none | no | no |
| 649 | `econtrol_austria_electricity_monthly` | internal | source | series | 17 | econtrol_austria_electricity_monthly, statat_austria_electricity_annual, statat_austria_electricity_monthly | none | no | no |
| 650 | `eec_eswatini_electricity_annual` | internal | source | series | 14 | eec_eswatini_electricity_annual | none | no | no |
| 651 | `eehc_egypt_electricity_annual` | internal | source | series | 15 | eehc_egypt_electricity_annual | none | no | no |
| 652 | `eles_slovenia_hourly` | internal | source | series | 15 | eles_slovenia_hourly | none | no | no |
| 653 | `enercal_nc_electricity_annual` | internal | source | series | 14 | enercal_nc_electricity_annual | none | no | no |
| 654 | `energycom_ghana_electricity_annual` | internal | source | series | 13 | energycom_ghana_electricity_annual | none | no | no |
| 655 | `ens_denmark_electricity_monthly` | internal | source | series | 14 | ens_denmark_electricity_monthly | none | no | no |
| 656 | `erb_zambia_electricity_annual` | internal | source | series | 15 | erb_zambia_electricity_annual | none | no | no |
| 657 | `erc_mongolia_electricity_annual` | internal | source | series | 13 | erc_mongolia_electricity_annual | none | no | no |
| 658 | `eru_czech_electricity` | internal | source | series | 14 | eru_czech_electricity | none | no | no |
| 659 | `esco_georgia_electricity_monthly` | internal | source | series | 13 | esco_georgia_electricity_monthly | none | no | no |
| 660 | `eso_cayman_electricity_annual` | internal | source | series | 13 | eso_cayman_electricity_annual | none | no | no |
| 661 | `ewa_bahrain_electricity_annual` | internal | source | series | 15 | ewa_bahrain_electricity_annual | none | no | no |
| 662 | `gastat_saudi_electricity_annual` | internal | source | series | 14 | gastat_saudi_electricity_annual | none | no | no |
| 663 | `grenada_cso_electricity_annual` | internal | source | series | 14 | grenada_cso_electricity_annual | none | no | no |
| 664 | `hops_croatia_annual` | internal | source | series | 16 | hops_croatia_annual | none | no | no |
| 665 | `inseed_togo_electricity_annual` | internal | source | series | 14 | inseed_togo_electricity_annual | none | no | no |
| 666 | `instat_madagascar_electricity_monthly` | internal | source | series | 14 | instat_madagascar_electricity_monthly | none | no | no |
| 667 | `irena_capacity_annual` | internal | source | series | 14 | aneel_siga_plants, desnz_uk_renewables_quarterly, epra_kenya_electricity_annual and 2 more | none | no | no |
| 668 | `je_jersey_electricity_annual` | internal | source | series | 15 | je_jersey_electricity_annual | none | no | no |
| 669 | `kpx_korea_demand_monthly` | internal | source | series | 14 | kpx_korea | none | no | no |
| 670 | `kpx_korea_generation_annual` | internal | source | series | 15 | kpx_korea | none | no | no |
| 671 | `makstat_macedonia_electricity_monthly` | internal | source | series | 14 | makstat_macedonia_electricity_monthly, statbank_moldova_electricity_monthly | none | no | no |
| 672 | `miso_as_prices` | internal | source | series | 13 | battery_stack, capacity_and_ancillary, miso_as_prices and 2 more | none | no | energy_research_warehouse_internal |
| 673 | `nawec_gambia_electricity_monthly` | internal | source | series | 13 | nawec_gambia_electricity_monthly | none | no | no |
| 674 | `nbs_maldives_electricity` | internal | source | series | 14 | nbs_maldives_electricity | none | no | no |
| 675 | `nrcs_snotel_swe_daily` | internal | source | series | 18 | nrcs_snotel_swe_daily | none | no | no |
| 676 | `nsi_bulgaria_electricity_monthly` | internal | source | series | 14 | nsi_bulgaria_electricity_monthly | none | no | no |
| 677 | `nso_malawi_electricity_sales_annual` | internal | source | series | 14 | nso_malawi_electricity_sales_annual | none | no | no |
| 678 | `nspower_ns_load_hourly` | internal | source | series | 13 | nspower_ns_load_hourly | none | no | no |
| 679 | `ope_pf_electricity_annual` | internal | source | series | 13 | ope_pf_electricity_annual | none | no | no |
| 680 | `pjm_rpm_capacity_prices` | internal | source | series | 13 | capacity_and_ancillary, cost_of_power, pjm_rpm_capacity_prices and 1 more | /demand | no | energy_research_warehouse_internal |
| 681 | `portwatch_chokepoint_transits` | internal | source | series | 13 | automated_analysis, automated_analysis_findings, portwatch_chokepoint_transits | none | no | energy_research_warehouse_internal |
| 682 | `pse_poland_balance_15min` | internal | source | series | 15 | pse_poland_balance_15min | none | no | no |
| 683 | `ren_portugal_balance_annual` | internal | source | series | 13 | energy_charts_portugal_power, ren_portugal_balance_annual | none | no | no |
| 684 | `rggi_auction_allowance_prices` | internal | source | series | 13 | carb_auction_allowance_prices, price_board, price_board_carbon and 1 more | none | no | energy_research_warehouse_internal |
| 685 | `sbs_samoa_electricity_annual` | internal | source | series | 14 | sbs_samoa_electricity_annual | none | no | no |
| 686 | `siea_solomon_electricity_annual` | internal | source | series | 13 | siea_solomon_electricity_annual | none | no | no |
| 687 | `slu_cso_electricity_annual` | internal | source | series | 14 | slu_cso_electricity_annual | none | no | no |
| 688 | `statai_anguilla_electricity_monthly` | internal | source | series | 13 | statai_anguilla_electricity_monthly | none | no | no |
| 689 | `statgl_greenland_electricity_annual` | internal | source | series | 14 | statgl_greenland_electricity_annual | none | no | no |
| 690 | `statnett_norway_daily` | internal | source | series | 13 | statnett_norway_daily | none | no | no |
| 691 | `svk_sweden_production_hourly` | internal | source | series | 14 | svk_sweden_production_hourly | none | no | no |
| 692 | `treasury_1603_awards` | internal | source | events | 15 | treasury_1603_awards, usaspending_doe_obligations | none | no | no |
| 693 | `usaspending_doe_obligations` | internal | source | series | 16 | usaspending_doe_obligations | none | no | no |
| 694 | `vmme_paraguay_electricity_annual` | internal | source | series | 13 | vmme_paraguay_electricity_annual | none | no | no |
| 695 | `zimstat_zimbabwe_generation_monthly` | internal | source | series | 14 | zimstat_zimbabwe_generation_monthly | none | no | no |

### policy (4 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 179 | `policy_action_tags` | public | model_extracted | events | 21 | datacenter_cost, policy_action_tags, policy_monitor | /policy | no | energy_research_warehouse |
| 180 | `policy_actions` | public | model_extracted | events | 50 | companies, datacenter_cost, policy_action_tags and 2 more | /, /_retired/board-original, /_retired/board-v3 and 38 more | yes | energy_research_warehouse |
| 181 | `policy_reads` | public | model_extracted | events | 33 | api_cost_ledger, datacenter_cost, policy_monitor and 1 more | /, /_retired/board-original, /_retired/board-v3 and 28 more | yes | energy_research_warehouse |
| 696 | `policy_reads_evidence` | internal | model_extracted | events | 15 | policy_monitor | /policy | no | energy_research_warehouse_internal |

### price (5 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 182 | `price_board_latest` | public | derived | series | 13 | ask, packages, price_board | /_retired/board-original, /_retired/board-v3, /_retired/board-v4 and 2 more | yes | energy_research_warehouse |
| 183 | `price_board_peak_offpeak` | public | derived | series | 13 | packages, price_board | /_retired/board-original, /board, /board/rows and 3 more | yes | energy_research_warehouse |
| 184 | `price_board_spreads` | public | derived | series | 14 | ask, price_board, price_board_v4 | /_retired/board-original, /api/ask, /board and 3 more | yes | energy_research_warehouse |
| 185 | `price_years_by_window` | public | derived | series | 23 | battery_earns_algorithm, datacenter_cost, datacenter_pays_algorithm and 3 more | /board, /cost-of-power, /cost-of-power/battery and 9 more | yes | energy_research_warehouse |
| 697 | `price_board_carbon` | internal | derived | series | 13 | price_board, price_board_carbon, rggi_auction_allowance_prices | /_retired/board-original | yes | energy_research_warehouse_internal |

### spp (5 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 186 | `spp_as_prices` | public | source | series | 13 | battery_stack, capacity_and_ancillary, price_board and 3 more | /board, /cost-of-power/battery | no | energy_research_warehouse |
| 187 | `spp_curtailment_daily` | public | source | series | 13 | ask_ercot, curtailment, ercot_wind_solar_hsl_daily and 2 more | /, /_retired/curtailment-original, /about and 4 more | yes | energy_research_warehouse |
| 560 | `spp_as_quantities` | public | source | series | 13 | reserve_quantities_nyiso_spp, spp_as_prices, spp_as_quantities and 1 more | none | no | energy_research_warehouse |
| 561 | `spp_dam_cleared_energy` | public | source | series | 13 | caiso_dam_cleared_energy, spp_as_quantities, spp_dam_cleared_energy and 1 more | none | no | energy_research_warehouse |
| 562 | `spp_interconnection_queue` | public | source | entities | 26 | datacenter_facilities, interconnection_explorer, isone_interconnection_queue and 1 more | none | yes | energy_research_warehouse |

### storage (4 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 188 | `storage_buildout_monthly` | public | derived | series | 13 | automated_analysis_findings, battery_awards, battery_early_years and 8 more | /, /about, /api/ask and 6 more | yes | energy_research_warehouse |
| 189 | `storage_capacity` | public | derived | entities | 28 | battery_game, eia860m_operating_generators, eia860m_planned_generators and 5 more | /, /_retired/board-original, /_retired/board-v3 and 30 more | yes | energy_research_warehouse |
| 190 | `storage_daily_cycle` | public | derived | series | 14 | battery_awards, eia930_all_storage, events and 3 more | /, /about, /data and 8 more | yes | energy_research_warehouse |
| 191 | `storage_owners_monthly` | public | derived | series | 16 | storage, storage_owners | /, /about, /data and 3 more | yes | energy_research_warehouse |

### utility (5 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 192 | `utility_large_load_rule_changes` | public | model_extracted | events | 25 | large_load_research, policy_monitor, siting | /cost-of-power, /policy | no | energy_research_warehouse |
| 193 | `utility_large_load_rules` | public | model_extracted | events | 46 | large_load_research, siting | /cost-of-power, /policy | no | energy_research_warehouse |
| 194 | `utility_large_load_tariffs` | public | source | series | 34 | large_load_research, large_load_tariffs, siting | /demand | no | energy_research_warehouse |
| 195 | `utility_service_territories` | public | source | entities | 20 | companies, county_population_and_regions, datacenter_projects and 6 more | /companies, /companies/[id], /companies/[id]/rows and 7 more | yes | no |
| 581 | `utility_large_load_queue_totals` | public | model_extracted | events | 22 | large_load_research, large_load_waits | none | no | energy_research_warehouse |

### wb (3 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 196 | `wb_commodity_prices_monthly` | public | source | series | 13 | price_board, usgs_mcs_critical_minerals, wb_commodity_prices_monthly | /board | no | no |
| 582 | `wb_electricity_access_annual` | public | source | series | 16 | wb_electricity_access_annual, wb_iea_electricity_annual | none | no | no |
| 698 | `wb_iea_electricity_annual` | internal | source | series | 16 | wb_electricity_access_annual, wb_iea_electricity_annual | none | no | no |

### afdc (3 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 197 | `afdc_ev_charging_state_annual` | public | source | series | 14 | afdc_ev_charging_state_annual, afdc_station_counts_annual, eurostat_ev_recharging_annual | none | no | no |
| 198 | `afdc_station_counts_annual` | public | source | series | 14 | afdc_station_counts_annual | none | no | no |
| 199 | `afdc_vehicle_registrations_annual` | public | source | series | 13 | afdc_ev_charging_state_annual, afdc_station_counts_annual, afdc_vehicle_registrations_annual | none | no | no |

### boem (3 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 201 | `boem_offshore_platforms` | public | source | entities | 36 | boem_offshore_platforms | none | no | no |
| 202 | `boem_ogor_lease_production_monthly` | public | source | series | 13 | boem_offshore_platforms, boem_ogor_lease_production_monthly, boem_renewable_leases and 3 more | none | no | no |
| 203 | `boem_renewable_leases` | public | source | entities | 20 | boem_renewable_leases, policy_monitor | none | no | no |

### cer (3 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 215 | `cer_electricity_trade` | public | source | series | 13 | cer_electricity_trade, eia_international_electricity_annual, statcan_electricity_generation_monthly | none | no | no |
| 216 | `cer_gas_trade` | public | source | series | 13 | cer_gas_trade | none | no | no |
| 217 | `cer_pipeline_throughput` | public | source | series | 19 | cer_pipeline_throughput | none | no | no |

### desnz (17 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 219 | `desnz_gb_regional_consumption_annual` | public | source | series | 13 | desnz_gb_regional_consumption_annual, desnz_gb_regional_gas_consumption_annual | none | no | no |
| 220 | `desnz_gb_regional_gas_consumption_annual` | public | source | series | 13 | desnz_gb_regional_gas_consumption_annual | none | no | no |
| 221 | `desnz_regional_renewable_capacity_annual` | public | source | series | 13 | desnz_regional_renewable_capacity_annual | none | no | no |
| 222 | `desnz_regional_renewables_annual` | public | source | series | 13 | desnz_regional_renewable_capacity_annual, desnz_regional_renewables_annual | none | no | no |
| 223 | `desnz_uk_capacity_by_connection_annual` | public | source | series | 13 | desnz_uk_capacity_by_connection_annual | none | no | no |
| 224 | `desnz_uk_co2_intensity_annual` | public | source | series | 13 | desnz_uk_co2_intensity_annual | none | no | no |
| 225 | `desnz_uk_derated_capacity_annual` | public | source | series | 13 | desnz_uk_capacity_by_connection_annual, desnz_uk_derated_capacity_annual, desnz_uk_mpp_capacity_countries_annual | none | no | no |
| 226 | `desnz_uk_electricity_quarterly` | public | source | series | 16 | desnz_uk_electricity_quarterly, desnz_uk_gas_quarterly, desnz_uk_nations_electricity_annual and 2 more | none | no | no |
| 227 | `desnz_uk_fuel_used_generation_annual` | public | source | series | 13 | desnz_uk_fuel_used_generation_annual | none | no | no |
| 228 | `desnz_uk_gas_quarterly` | public | source | series | 14 | desnz_gb_regional_gas_consumption_annual, desnz_uk_fuel_used_generation_annual, desnz_uk_gas_quarterly | none | no | no |
| 229 | `desnz_uk_interconnector_flows_annual` | public | source | series | 13 | desnz_uk_interconnector_flows_annual | none | no | no |
| 230 | `desnz_uk_mpp_capacity_countries_annual` | public | source | series | 13 | desnz_uk_mpp_capacity_countries_annual | none | no | no |
| 231 | `desnz_uk_nations_electricity_annual` | public | source | series | 13 | desnz_gb_regional_consumption_annual, desnz_uk_nations_electricity_annual | none | no | no |
| 232 | `desnz_uk_plant_loads_annual` | public | source | series | 13 | desnz_uk_plant_loads_annual | none | no | no |
| 233 | `desnz_uk_power_stations` | public | source | entities | 28 | desnz_uk_derated_capacity_annual, desnz_uk_power_stations, desnz_uk_storage_annual | none | no | no |
| 234 | `desnz_uk_renewables_quarterly` | public | source | series | 15 | desnz_regional_renewable_capacity_annual, desnz_regional_renewables_annual, desnz_uk_capacity_by_connection_annual and 2 more | none | no | no |
| 235 | `desnz_uk_storage_annual` | public | source | series | 13 | desnz_uk_derated_capacity_annual, desnz_uk_storage_annual | none | no | no |

### doe (5 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 236 | `doe_grip_selections` | public | source | events | 21 | doe_grip_selections | none | no | no |
| 237 | `doe_lead_energy_burden` | public | source | series | 17 | doe_lead_energy_burden | none | no | no |
| 238 | `doe_lng_export_applications` | public | source | entities | 25 | doe_lng_export_applications, policy_monitor | none | no | no |
| 239 | `doe_oe417_events` | public | source | events | 27 | doe_oe417_events, events, gfz_kp_index_3h and 1 more | none | no | no |
| 240 | `doe_useer_employment` | public | source | series | 16 | doe_useer_employment | none | no | no |

### eia923 (3 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 345 | `eia923_fuel_receipts` | public | source | events | 44 | eia923_receipts, eia_power_plant_fuel_costs | none | no | no |
| 346 | `eia923_plant_fuel_annual` | public | source | series | 13 | egrid_power_plants, eia923_monthly, eia923_plant_fuel_annual and 3 more | none | no | no |
| 347 | `eia923_plant_fuel_monthly` | public | source | series | 21 | eia923_monthly, eia923_receipts, eia_state_generation_monthly and 3 more | none | no | no |

### epa (8 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 373 | `epa_ghg_inventory_annual` | public | source | series | 17 | epa_ghg_inventory_annual | none | no | no |
| 374 | `epa_ghgrp_facility_emissions` | public | source | series | 21 | epa_ghg_inventory_annual, epa_ghgrp_facility_emissions, epa_lmop_landfill_projects and 1 more | none | no | no |
| 375 | `epa_ghgrp_power_co2` | public | source | series | 18 | epa_ghgrp_facility_emissions, epa_ghgrp_power_co2 | none | no | no |
| 376 | `epa_lmop_landfill_projects` | public | source | entities | 79 | epa_lmop_landfill_projects | none | no | no |
| 377 | `epa_needs_units` | public | source | entities | 48 | epa_needs_units, policy_monitor | none | no | no |
| 378 | `epa_rfs_fuel_annual` | public | source | series | 15 | eia_biofuel_plants, epa_rfs_rins | none | no | no |
| 379 | `epa_rfs_rins_monthly` | public | source | series | 13 | eia_biofuel_plants, epa_rfs_rins, policy_monitor and 1 more | none | no | no |
| 380 | `epa_tri_energy_releases_annual` | public | source | series | 29 | epa_tri_energy_releases_annual | none | no | no |

### eurostat (27 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 403 | `eurostat_crude_imports_by_field_monthly` | public | source | series | 16 | eurostat_crude_imports_by_field_monthly | none | no | no |
| 404 | `eurostat_crude_imports_monthly` | public | source | series | 17 | eurostat_crude_imports_by_field_monthly, eurostat_crude_imports_monthly, eurostat_electricity_trade_annual and 1 more | none | no | no |
| 405 | `eurostat_data_centre_electricity_annual` | public | source | series | 16 | eurostat_data_centre_electricity_annual | none | no | no |
| 406 | `eurostat_electricity_capacity_annual` | public | source | series | 19 | czso_cz_regional_electricity_annual, eurostat_electricity_capacity_annual, eurostat_electricity_production_annual and 1 more | none | no | no |
| 407 | `eurostat_electricity_consumption_annual` | public | source | series | 17 | czso_cz_regional_electricity_annual, eurostat_data_centre_electricity_annual, eurostat_electricity_consumption_annual and 4 more | none | no | no |
| 408 | `eurostat_electricity_monthly` | public | source | series | 17 | cbs_netherlands_electricity_monthly, cso_ireland_electricity_monthly, csp_latvia_electricity_monthly and 21 more | none | no | no |
| 409 | `eurostat_electricity_production_annual` | public | source | series | 17 | czso_cz_regional_electricity_annual, dst_dk_electricity_supply_annual, eurostat_electricity_consumption_annual and 8 more | none | no | no |
| 410 | `eurostat_electricity_trade_annual` | public | source | series | 17 | desnz_uk_interconnector_flows_annual, eurostat_electricity_consumption_annual, eurostat_electricity_trade_annual and 1 more | none | no | no |
| 411 | `eurostat_electrification_rate_annual` | public | source | series | 17 | eurostat_electrification_rate_annual | none | no | no |
| 412 | `eurostat_ev_recharging_annual` | public | source | series | 18 | eurostat_ev_recharging_annual, eurostat_ev_recharging_power_annual | none | no | no |
| 413 | `eurostat_ev_recharging_power_annual` | public | source | series | 17 | eurostat_ev_recharging_power_annual | none | no | no |
| 414 | `eurostat_fossil_share_annual` | public | source | series | 16 | eurostat_fossil_share_annual | none | no | no |
| 415 | `eurostat_gas_balance_monthly` | public | source | series | 17 | eurostat_gas_balance_monthly, eurostat_import_dependency_annual, eurostat_oil_monthly and 1 more | none | no | no |
| 416 | `eurostat_gas_import_origin_annual` | public | source | series | 17 | eurostat_gas_import_origin_annual, eurostat_import_concentration_annual | none | no | no |
| 417 | `eurostat_gas_imports_monthly` | public | source | series | 18 | eurostat_gas_balance_monthly, eurostat_gas_imports_monthly | none | no | no |
| 418 | `eurostat_hard_coal_imports_annual` | public | source | series | 17 | eurostat_electricity_trade_annual, eurostat_hard_coal_imports_annual | none | no | no |
| 419 | `eurostat_household_electricity_annual` | public | source | series | 17 | eurostat_household_electricity_annual, eurostat_industry_electricity_annual | none | no | no |
| 420 | `eurostat_import_concentration_annual` | public | source | series | 17 | eurostat_gas_import_origin_annual, eurostat_import_concentration_annual, eurostat_supply_diversity_annual | none | no | no |
| 421 | `eurostat_import_dependency_annual` | public | source | series | 17 | eurostat_gas_import_origin_annual, eurostat_import_dependency_annual, eurostat_supply_diversity_annual | none | no | no |
| 422 | `eurostat_industry_electricity_annual` | public | source | series | 17 | eurostat_industry_electricity_annual | none | no | no |
| 423 | `eurostat_nonhousehold_bands_annual` | public | source | series | 17 | eurostat_nonhousehold_bands_annual | none | no | no |
| 424 | `eurostat_nuclear_fuel_cycle_annual` | public | source | series | 18 | eurostat_nuclear_fuel_cycle_annual | none | no | no |
| 425 | `eurostat_oil_monthly` | public | source | series | 18 | eurostat_crude_imports_by_field_monthly, eurostat_crude_imports_monthly, eurostat_oil_monthly and 1 more | none | no | no |
| 426 | `eurostat_renewable_capacity_annual` | public | source | series | 18 | eurostat_crude_imports_by_field_monthly, eurostat_crude_imports_monthly, eurostat_electricity_capacity_annual and 7 more | none | no | no |
| 427 | `eurostat_renewable_shares_annual` | public | source | series | 17 | eurostat_fossil_share_annual, eurostat_renewable_shares_annual, statec_lu_power_capacity_annual | none | no | no |
| 428 | `eurostat_solid_fuels_monthly` | public | source | series | 18 | eurostat_hard_coal_imports_annual, eurostat_oil_monthly, eurostat_solid_fuels_monthly | none | no | no |
| 429 | `eurostat_supply_diversity_annual` | public | source | series | 16 | eurostat_supply_diversity_annual | none | no | no |

### onrr (3 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 470 | `onrr_production_annual` | public | source | series | 20 | blm_oil_gas_statistics_annual, onrr | none | no | no |
| 471 | `onrr_production_monthly` | public | source | series | 16 | blm_oil_gas_statistics_annual, onrr | none | no | no |
| 472 | `onrr_revenue_monthly` | public | source | series | 23 | onrr | none | no | no |

### ornl (6 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 473 | `ornl_eha_hydropower_plants` | public | source | entities | 43 | ornl_hydropower, policy_monitor, usace_nid_dams and 1 more | none | no | no |
| 474 | `ornl_eha_hydropower_units` | public | source | entities | 32 | ornl_hydropower | none | no | no |
| 475 | `ornl_hydropower_pipeline` | public | source | entities | 28 | ornl_hydropower, policy_monitor | none | no | no |
| 476 | `ornl_hydropower_relicensing` | public | source | events | 36 | ornl_hydropower, policy_monitor | none | no | no |
| 477 | `ornl_npd_potential` | public | source | entities | 29 | ornl_hydropower, usace_nid_dams | none | no | no |
| 635 | `ornl_tedb_transportation_annual` | internal | source | series | 15 | ornl_tedb_transportation_annual | none | no | no |

### statcan (8 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 563 | `statcan_electricity_generation_monthly` | public | source | series | 18 | bchydro_ba_load_hourly, statcan_electricity_generation_monthly, statcan_electricity_trade_monthly and 3 more | none | no | no |
| 564 | `statcan_electricity_trade_monthly` | public | source | series | 16 | nspower_ns_load_hourly, statcan_electricity_trade_monthly, statcan_energy_balance_annual and 1 more | none | no | no |
| 565 | `statcan_energy_balance_annual` | public | source | series | 17 | statcan_energy_balance_annual | none | no | no |
| 566 | `statcan_generating_capacity_annual` | public | source | series | 18 | statcan_generating_capacity_annual | none | no | no |
| 567 | `statcan_generation_class_annual` | public | source | series | 17 | statcan_generation_class_annual, statcan_power_disposition_annual | none | no | no |
| 568 | `statcan_oil_gas_supply_monthly` | public | source | series | 20 | statcan_energy_balance_annual, statcan_oil_gas_supply_monthly, statcan_petroleum_products_monthly | none | no | no |
| 569 | `statcan_petroleum_products_monthly` | public | source | series | 18 | statcan_energy_balance_annual, statcan_petroleum_products_monthly | none | no | no |
| 570 | `statcan_power_disposition_annual` | public | source | series | 16 | statcan_generation_class_annual, statcan_power_disposition_annual | none | no | no |

### statec (4 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 571 | `statec_lu_electricity_generation_annual` | public | source | series | 13 | statec_lu_electricity_generation_annual, statec_lu_power_capacity_annual | none | no | no |
| 572 | `statec_lu_electricity_trade_annual` | public | source | series | 13 | statec_lu_electricity_generation_annual | none | no | no |
| 573 | `statec_lu_power_capacity_annual` | public | source | series | 13 | statec_lu_power_capacity_annual | none | no | no |
| 574 | `statec_lu_supplier_mix_annual` | public | source | series | 13 | statec_lu_power_capacity_annual | none | no | no |

### usbr (3 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 575 | `usbr_crsp_reservoirs_daily` | public | source | series | 13 | usbr_crsp_reservoirs_daily | none | no | no |
| 576 | `usbr_hydropower_monthly` | public | source | series | 14 | nrcs_snotel_swe_daily, usbr_hydropower_monthly, usbr_mead_powell_daily and 2 more | none | no | no |
| 577 | `usbr_mead_powell_daily` | public | source | series | 13 | usbr_crsp_reservoirs_daily, usbr_mead_powell_daily | none | no | no |

### usgs (3 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 578 | `usgs_comcat_earthquakes_south_central` | public | source | events | 29 | usgs_comcat_earthquakes_south_central | none | no | no |
| 579 | `usgs_mcs_critical_minerals` | public | source | series | 22 | imf_commodity_prices, resource_layers_table, usgs_mcs_critical_minerals | none | no | no |
| 580 | `usgs_streamflow_daily` | public | source | series | 16 | usbr_mead_powell_daily, usgs_streamflow_daily | none | no | no |

### ferc (8 tables)

| Order | Table | License | Tier | Shape | Columns | Method notes | Pages | Live | Redivis |
|---|---|---|---|---|---|---|---|---|---|
| 592 | `ferc_eqr_buyer_doubtful` | internal | source | events | 19 | contracts, eqr_buyers, eqr_terms | /contracts | no | energy_research_warehouse_internal |
| 593 | `ferc_eqr_buyer_names` | internal | source | entities | 22 | contracts, eqr_buyers, eqr_terms | /contracts | no | energy_research_warehouse_internal |
| 594 | `ferc_eqr_contract_terms` | internal | source | events | 29 | contracts, eqr_terms | none | no | energy_research_warehouse_internal |
| 595 | `ferc_eqr_contracts` | internal | source | events | 43 | contracts, eqr_buyers, eqr_terms and 1 more | /, /about, /contracts and 2 more | yes | energy_research_warehouse_internal |
| 596 | `ferc_eqr_contracts_history` | internal | source | events | 43 | contracts, eqr_terms, ferc_eqr_contracts | /contracts | no | energy_research_warehouse_internal |
| 597 | `ferc_eqr_party_mw` | internal | source | entities | 25 | contracts, eqr_terms | none | no | energy_research_warehouse_internal |
| 598 | `ferc_eqr_party_totals` | internal | source | entities | 24 | contracts, eqr_buyers, eqr_terms | /contracts | no | energy_research_warehouse_internal |
| 599 | `ferc_eqr_quarter_changes` | internal | derived | series | 13 | contracts, eqr_terms | none | no | energy_research_warehouse_internal |

