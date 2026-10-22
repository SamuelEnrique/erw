# Method notes for the tables of 21 October: the plan (session 674)

Energy Research Warehouse (ERW), session 674 (chain 043, run on 22 October 2026 UTC). The chain asked for a method note for every table whose `last_run` in `coverage.csv` is 21 October 2026 and that has none. 162 tables were last run that day (most are daily tables re-run); the ones that need a note are the tables **first written** on 21 or 22 October and named by no note under `docs/methods/` (by the note's file name or by the table's name in backticks in a note): **78 tables from 55 connectors**, grouped into **49 notes** (one a source where one source gives several tables: the five EIA-930 sub-region tables, the twenty-one FERC Form 714 tables, the three nuclear outage tables, the four EIA coal price tables). The count was made by `git log` of `coverage.csv` for each table's first line; the list is below.

Tables first written before 21 October that still have no note (14, among them `battery_sourced_ranges`, `rrc_lease_production_monthly` and seven EIA petroleum and gas tables of September) are outside this chain's list and are named in the note of session 683.

Each note holds: the publisher and report, the address, the vintage and revision rule, every column or variable with its unit, the shape, the license verdict, the cross-check the connector runs, and what the table does not hold. A grouped note carries a line `Tables:` naming its tables, and `docs/coverage.md` gains a last column, `Method`, linking each table's note (`build_coverage.py`, session 674).

## Session 674

| Note | Tables | Connector |
|---|---|---|
| `docs/methods/eia861_utility_sales.md` | `eia861_utility_sales` | `eia861_sales.py` |
| `docs/methods/eia861m_utility_sales_monthly.md` | `eia861m_utility_sales_monthly` | `eia861m_sales.py` |
| `docs/methods/eia923_plant_fuel_annual.md` | `eia923_plant_fuel_annual` | `eia923_plant_fuel.py` |
| `docs/methods/egrid_power_plants.md` | `egrid_power_plants` | `egrid.py` |
| `docs/methods/eia_state_capacity_annual.md` | `eia_state_capacity_annual` | `eia_state_capacity.py` |
| `docs/methods/eia_state_source_disposition_annual.md` | `eia_state_source_disposition_annual` | `eia_state_disposition.py` |
| `docs/methods/eia_energy_efficiency_state_annual.md` | `eia_energy_efficiency_state_annual` | `eia_energy_efficiency.py` |
| `docs/methods/eia_meters_state_annual.md` | `eia_meters_state_annual` | `eia_meters.py` |
| `docs/methods/eia_net_metering_state_annual.md` | `eia_net_metering_state_annual` | `eia_net_metering.py` |
| `docs/methods/eia_power_co2_state_annual.md` | `eia_power_co2_state_annual` | `eia_power_co2_state.py` |

## Session 675

| Note | Tables | Connector |
|---|---|---|
| `docs/methods/eia930_subba_demand.md` | `eia930_subba_demand_hourly`, `eia930_subba_demand_hourly_2022`, `eia930_subba_demand_hourly_2023`, `eia930_subba_demand_hourly_2024`, `eia930_subba_demand_hourly_2025` | `eia930_subba.py` |
| `docs/methods/ferc714_area_demand.md` | `ferc714_area_demand_2006`, `ferc714_area_demand_2007`, `ferc714_area_demand_2008`, `ferc714_area_demand_2009`, `ferc714_area_demand_2010`, `ferc714_area_demand_2011`, `ferc714_area_demand_2012`, `ferc714_area_demand_2013`, `ferc714_area_demand_2014`, `ferc714_area_demand_2015`, `ferc714_area_demand_2016`, `ferc714_area_demand_2017`, `ferc714_area_demand_2018`, `ferc714_area_demand_2019`, `ferc714_area_demand_2020`, `ferc714_area_demand_2021`, `ferc714_area_demand_2022`, `ferc714_area_demand_2023`, `ferc714_area_demand_2024`, `ferc714_area_demand_2025`, `ferc714_respondents` | `ferc714_demand.py`, `ferc714_respondents.py` |
| `docs/methods/eia_nuclear_outages.md` | `eia_nuclear_outages_daily`, `eia_nuclear_outages_facility_daily`, `eia_nuclear_outages_generator_daily` | `eia_nuclear_outages.py`, `eia_nuclear_outages_facility.py`, `eia_nuclear_outages_generator.py` |
| `docs/methods/nlr_atb_electricity_costs.md` | `nlr_atb_electricity_costs` | `nlr_atb_costs.py` |
| `docs/methods/uswtdb_wind_turbines.md` | `uswtdb_wind_turbines` | `uswtdb.py` |
| `docs/methods/epa_ghgrp_power_co2.md` | `epa_ghgrp_power_co2` | `ghgrp_power.py` |
| `docs/methods/eia_co2_state_annual.md` | `eia_co2_state_annual` | `eia_co2_state.py` |
| `docs/methods/eia_seds_state_energy.md` | `eia_seds_state_energy` | `eia_seds.py` |
| `docs/methods/eia_aeo_electricity.md` | `eia_aeo_electricity` | `eia_aeo.py` |
| `docs/methods/eia_steo_forecasts.md` | `eia_steo_forecasts` | `eia_steo.py` |

## Session 676

| Note | Tables | Connector |
|---|---|---|
| `docs/methods/eia_gas_balance_annual.md` | `eia_gas_balance_annual` | `eia_gas_balance.py` |
| `docs/methods/eia_gas_consumption_state_monthly.md` | `eia_gas_consumption_state_monthly` | `eia_gas_consumption_state.py` |
| `docs/methods/eia_gas_interstate_annual.md` | `eia_gas_interstate_annual` | `eia_gas_interstate.py` |
| `docs/methods/eia_gas_prices_state_monthly.md` | `eia_gas_prices_state_monthly` | `eia_gas_prices_state.py` |
| `docs/methods/eia_gas_production_state_monthly.md` | `eia_gas_production_state_monthly` | `eia_gas_production_state.py` |
| `docs/methods/eia_gas_reserves_annual.md` | `eia_gas_reserves_annual` | `eia_gas_reserves.py` |
| `docs/methods/eia_gas_storage_capacity_monthly.md` | `eia_gas_storage_capacity_monthly` | `eia_gas_storage_capacity.py` |
| `docs/methods/eia_gas_storage_state_monthly.md` | `eia_gas_storage_state_monthly` | `eia_gas_storage_state.py` |
| `docs/methods/eia_gas_trade_country_monthly.md` | `eia_gas_trade_country_monthly` | `eia_gas_trade.py` |
| `docs/methods/eia_gas_wells_annual.md` | `eia_gas_wells_annual` | `eia_gas_wells.py` |

## Session 677

| Note | Tables | Connector |
|---|---|---|
| `docs/methods/eia_crude_imports_detail_monthly.md` | `eia_crude_imports_detail_monthly` | `eia_crude_imports_detail.py` |
| `docs/methods/eia_crude_production_state_monthly.md` | `eia_crude_production_state_monthly` | `eia_crude_production_state.py` |
| `docs/methods/eia_crude_reserves_annual.md` | `eia_crude_reserves_annual` | `eia_crude_reserves.py` |
| `docs/methods/eia_drilling_monthly.md` | `eia_drilling_monthly` | `eia_drilling.py` |
| `docs/methods/eia_coal_prices.md` | `eia_coal_prices_annual`, `eia_coal_delivered_price_annual`, `eia_coal_price_rank_annual`, `eia_coal_trade_price_annual` | `eia_coal_prices.py`, `eia_coal_delivered_price.py`, `eia_coal_price_rank.py`, `eia_coal_trade_price.py` |
| `docs/methods/boem_renewable_leases.md` | `boem_renewable_leases` | `boem_leases.py` |
| `docs/methods/boem_ogor_lease_production_monthly.md` | `boem_ogor_lease_production_monthly` | `boem_ogor.py` |
| `docs/methods/eia_heating_fuel_prices_weekly.md` | `eia_heating_fuel_prices_weekly` | `eia_heating_fuel_prices.py` |
| `docs/methods/eia_wood_pellets_monthly.md` | `eia_wood_pellets_monthly` | `eia_wood_pellets.py` |

## Session 678

| Note | Tables | Connector |
|---|---|---|
| `docs/methods/eia_ngl_production_monthly.md` | `eia_ngl_production_monthly` | `eia_ngl_production.py` |
| `docs/methods/eia_oxygenate_production_monthly.md` | `eia_oxygenate_production_monthly` | `eia_oxygenate_production.py` |
| `docs/methods/eia_padd_rail_barge_movements_monthly.md` | `eia_padd_rail_barge_movements_monthly` | `eia_padd_movements.py` |
| `docs/methods/eia_petroleum_snd_monthly.md` | `eia_petroleum_snd_monthly` | `eia_petroleum_snd.py` |
| `docs/methods/eia_petroleum_stocks_monthly.md` | `eia_petroleum_stocks_monthly` | `eia_petroleum_stocks.py` |
| `docs/methods/eia_product_supplied_monthly.md` | `eia_product_supplied_monthly` | `eia_product_supplied.py` |
| `docs/methods/eia_refinery_capacity_annual.md` | `eia_refinery_capacity_annual` | `eia_refinery_capacity.py` |
| `docs/methods/eia_refinery_inputs_monthly.md` | `eia_refinery_inputs_monthly` | `eia_refinery_inputs.py` |
| `docs/methods/eia_refinery_production_monthly.md` | `eia_refinery_production_monthly` | `eia_refinery_production.py` |
| `docs/methods/eia_refinery_weekly.md` | `eia_refinery_weekly` | `eia_refinery_weekly.py` |
