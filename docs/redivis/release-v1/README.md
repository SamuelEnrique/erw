# Energy Research Warehouse (ERW), version 1

The live, citable record of the US energy system: prices, flows, projects, deals and policy across power, natural gas, oil, nuclear, renewables, storage and transmission, with the global prices and events that move US markets. Every source is reshaped into three standard table shapes so that tables can be joined and compared: `series` (one row per observation: entity, variable, ts_utc, value), `entities` (one row per physical or corporate thing) and `events` (one row per deal, filing or announcement). Timestamps are UTC; power is MW and prices are USD per MWh unless a `unit` column says otherwise. The data standard: https://github.com/SamuelEnrique/erw/blob/main/docs/datastandard.md

**Version 1 holds 135 tables** (10 entities, 10 events, 115 series) and three metadata tables (`erw_coverage`, `erw_sources`, `erw_headers`). Every table's description is its provenance header: the source report, its address, when it was retrieved, the method, and its license line.

## What is not in it

42 tables of the warehouse's public draft are not in version 1: a table whose publisher's terms ask for permission or a license that has not been recorded is held from 2026-10-21 (the ERW's license record, https://github.com/SamuelEnrique/erw/blob/main/docs/licenses.md), and retired tables and the old members of consolidated tables are not tables of the warehouse. Tables licensed for internal use are never in this dataset. 65 public tables (`boem_ogor_lease_production_monthly`, `boem_renewable_leases`, `egrid_power_plants`, `eia861_utility_sales`, `eia861m_utility_sales_monthly`, `eia923_plant_fuel_annual`, `eia930_subba_demand_hourly`, `eia930_subba_demand_hourly_2021`, `eia930_subba_demand_hourly_2022`, `eia930_subba_demand_hourly_2023`, `eia930_subba_demand_hourly_2024`, `eia930_subba_demand_hourly_2025`, `eia_aeo_electricity`, `eia_co2_state_annual`, `eia_coal_delivered_price_annual`, `eia_coal_price_rank_annual`, `eia_coal_prices_annual`, `eia_coal_production_annual`, `eia_coal_trade_price_annual`, `eia_crude_imports_detail_monthly`, `eia_crude_production_state_monthly`, `eia_crude_reserves_annual`, `eia_drilling_monthly`, `eia_energy_efficiency_state_annual`, `eia_gas_balance_annual`, `eia_gas_consumption_state_monthly`, `eia_gas_interstate_annual`, `eia_gas_prices_state_monthly`, `eia_gas_production_state_monthly`, `eia_gas_reserves_annual`, `eia_gas_storage_capacity_monthly`, `eia_gas_storage_state_monthly`, `eia_gas_trade_country_monthly`, `eia_gas_wells_annual`, `eia_heating_fuel_prices_weekly`, `eia_meters_state_annual`, `eia_net_metering_state_annual`, `eia_ngl_production_monthly`, `eia_nuclear_outages_daily`, `eia_nuclear_outages_facility_daily`, `eia_nuclear_outages_generator_daily`, `eia_oxygenate_production_monthly`, `eia_padd_rail_barge_movements_monthly`, `eia_petroleum_snd_monthly`, `eia_petroleum_stocks_monthly`, `eia_power_co2_state_annual`, `eia_product_supplied_monthly`, `eia_refinery_capacity_annual`, `eia_refinery_inputs_monthly`, `eia_refinery_production_monthly`, `eia_refinery_weekly`, `eia_seds_state_energy`, `eia_state_capacity_annual`, `eia_state_source_disposition_annual`, `eia_steo_forecasts`, `eia_wood_pellets_monthly`, `epa_ghgrp_power_co2`, `ercot_all_hub_prices_history`, `grid_peak_vs_capacity`, `interconnection_durations`, `interconnection_durations_summary`, `nlr_atb_electricity_costs`, `node_basis_daily`, `uswtdb_wind_turbines`, `utility_service_territories`) are in version 1 by license but not yet in the dataset: the account's storage is full, and the table is added once it is settled.

## How to cite

Cite the organization that published the data, then the ERW table and this version. For example:

> U.S. Energy Information Administration (EIA). Spot prices. Via the Energy Research Warehouse (ERW), table `eia_fuel_spot_prices`, Redivis dataset `energy_research_warehouse`, version v1.

Each table's own citation is in `docs/redivis/release-v1/tables.csv` in the repository.

## How it is made

One connector per source pulls, reshapes and validates; the validator is the gate a table passes before upload. Uploads write a draft only; a version is released by a person after reading what the draft changes. Code, methods and the session reports: https://github.com/SamuelEnrique/erw

## Credit

The Energy Research Warehouse is adapted, with permission, from the infrastructure and documents of the Item Response Warehouse (github.com/ben-domingue/irw).
