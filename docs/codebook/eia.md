# Codebook: eia

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 112 public tables (5 entities, 1 events, 106 series; tiers: 2 derived, 110 source); 112 documented in full.

- [`eia_aeo_electricity`](#eia_aeo_electricity): One series of EIA's Annual Energy Outlook 2026 electricity Tables 8 and 9 (capacity, generation or a price), in one case (scenario), for one projected year.
- [`eia_aeo_emm_regions`](#eia_aeo_emm_regions): One series of EIA's Annual Energy Outlook 2026 Table 54 (electric power projections) for one Electricity Market Module region or the U.S., case cb2026, for one projected year.
- [`eia_aeo_industrial`](#eia_aeo_industrial): One series of EIA's Annual Energy Outlook 2026 industrial sub-sector tables (an industry's energy use of one fuel), in one case (scenario), for one projected year, in trillion Btu.
- [`eia_annual_crosscheck_ba`](#eia_annual_crosscheck_ba): One balancing authority's (or the Lower 48's) year of EIA-930's hourly net generation summed, set against EIA-923's annual figure, with the gap and the hours counted.
- [`eia_annual_generation_ba`](#eia_annual_generation_ba): One balancing authority's year of net generation, storage net generation or plant count, summed from Form EIA-923's plant rows by their Balancing Authority Code.
- [`eia_basin_production_monthly`](#eia_basin_production_monthly): One producing region's monthly crude oil production or marketed natural gas production, as EIA's Short-Term Energy Outlook gives its history.
- [`eia_biofuel_plants`](#eia_biofuel_plants): One fuel ethanol, biodiesel or renewable diesel plant's production capacity as of 1 January of one year (Form EIA-819); a plant appears once a year.
- [`eia_capacity_factors_annual`](#eia_capacity_factors_annual): One energy source and technology's yearly capacity factor or time adjusted capacity for U.S. utility-scale generators, from EIA's Electric Power Annual Tables 4.8.A and 4.8.B.
- [`eia_capacity_factors_monthly`](#eia_capacity_factors_monthly): One energy source and technology's monthly capacity factor or time adjusted capacity for U.S. utility-scale generators, from EIA's Electric Power Annual Tables 4.8.A and 4.8.B.
- [`eia_cbecs_commercial_buildings`](#eia_cbecs_commercial_buildings): One category of commercial buildings (by a building characteristic, or all buildings) and one figure from EIA's 2018 Commercial Buildings Energy Consumption Survey tables C1, C2 and E1.
- [`eia_co2_state_annual`](#eia_co2_state_annual): One state's (or the nation's) energy-related carbon dioxide emissions of one sector and one fuel for one year.
- [`eia_coal_delivered_price_annual`](#eia_coal_delivered_price_annual): One state's, census division's or the nation's yearly average delivered price of coal to one consuming sector.
- [`eia_coal_distribution_quarterly`](#eia_coal_distribution_quarterly): One quarter's domestic coal shipments of 2024 along one flow (origin, destination state, consuming sector, transport mode), from EIA's Annual Coal Distribution Report.
- [`eia_coal_mine_production_annual`](#eia_coal_mine_production_annual): One coal mine's (by MSHA id, coal rank and mine type) yearly production or average employees, from EIA's Annual Coal Report.
- [`eia_coal_price_rank_annual`](#eia_coal_price_rank_annual): One state's, region's or the nation's yearly average sales price of coal of one rank, from EIA's Annual Coal Report.
- [`eia_coal_prices_annual`](#eia_coal_prices_annual): One producing state's, region's or the nation's yearly average sales price of coal in one market type, from EIA's Annual Coal Report.
- [`eia_coal_production_annual`](#eia_coal_production_annual): One producing state's, region's or the nation's yearly coal production, number of mines or average employees, by coal rank and mine type, from EIA's Annual Coal Report.
- [`eia_coal_receipts_annual`](#eia_coal_receipts_annual): One year's coal received at one power plant from one mine, by supplier, coal rank, contract type and transport mode, with its price and quality (Form EIA-923).
- [`eia_coal_trade_price_annual`](#eia_coal_trade_price_annual): One year's average price of U.S. coal exports or imports of one rank with one country through one customs district, from EIA's Quarterly Coal Report.
- [`eia_county_region`](#eia_county_region): One county of the lower 48 states and the District of Columbia, with the balancing authority (grid operator area) and EIA region it is assigned to by the ERW's rule from EIA-861.
- [`eia_crude_first_purchase_prices`](#eia_crude_first_purchase_prices): One crude stream's or state's monthly average first purchase price (the price paid at the lease, as crude is first bought) as EIA reports it.
- [`eia_crude_imports_by_country`](#eia_crude_imports_by_country): One month's U.S. crude oil imports from one country of origin (or in all), as EIA reports them.
- [`eia_crude_imports_detail_monthly`](#eia_crude_imports_detail_monthly): One month's crude oil imports from one country of origin to one destination (refinery, state, PADD or the U.S.) of one grade, from EIA's company level imports (Form EIA-814).
- [`eia_crude_production_state_monthly`](#eia_crude_production_state_monthly): One month's crude oil field production of one state, region or federal offshore area, in the month or per day.
- [`eia_crude_quality_monthly`](#eia_crude_quality_monthly): One month's average API gravity or sulfur content of the crude oil run at refineries in the U.S., one PADD or one refining district.
- [`eia_crude_reserves_annual`](#eia_crude_reserves_annual): One state's, area's or the nation's crude oil proved reserves at a year's end, or one of the changes that take one year's reserves to the next.
- [`eia_crude_stream_prices`](#eia_crude_stream_prices): One crude stream's or area's monthly average price, as one of four EIA measures (first purchase price, landed cost or F.O.B. cost of imports, refiners' acquisition cost).
- [`eia_crude_tank_farm_stocks_monthly`](#eia_crude_tank_farm_stocks_monthly): One month's end crude oil stocks at tank farms and pipelines in the U.S. or one PADD, or ending stocks at Cushing, Oklahoma.
- [`eia_drilling_monthly`](#eia_drilling_monthly): One month's count of rotary rigs (crude oil, natural gas or both; U.S., onshore or offshore) or active well service rigs in operation.
- [`eia_energy_efficiency_state_annual`](#eia_energy_efficiency_state_annual): One state's (or the nation's) yearly savings or costs of utilities' energy efficiency programs in one sector, for one of EIA's time periods (reporting year or expected life cycle).
- [`eia_fuel_spot_prices`](#eia_fuel_spot_prices): One trading day's spot price of Henry Hub natural gas, WTI Cushing crude or Brent crude, as EIA reports it.
- [`eia_gas_balance_annual`](#eia_gas_balance_annual): One state's (or the nation's or the federal Gulf's) yearly natural gas supply or disposition figure for one process, from EIA's Natural Gas Annual.
- [`eia_gas_consumers_state_annual`](#eia_gas_consumers_state_annual): One state's (or the nation's) yearly number of natural gas consumers of one kind (residential, commercial, industrial; in all, buying from a utility, or with gas transported for them).
- [`eia_gas_consumption_state_monthly`](#eia_gas_consumption_state_monthly): One state's (or the nation's) monthly natural gas consumption by one sector, or in total, from EIA's Natural Gas Monthly.
- [`eia_gas_for_others_annual`](#eia_gas_for_others_annual): One state's (or the nation's) yearly natural gas delivered for the account of others (customer choice and transportation gas) to one sector, as a volume or as a share of the sector's deliveries.
- [`eia_gas_heat_content_monthly`](#eia_gas_heat_content_monthly): One month's average heat content of natural gas delivered to consumers in one state, DC or the U.S.
- [`eia_gas_interstate_annual`](#eia_gas_interstate_annual): One year's natural gas movement between a pair of areas (states, the federal Gulf, Canada, Mexico, other countries) for one process, from EIA's Natural Gas Annual.
- [`eia_gas_other_uses_state_annual`](#eia_gas_other_uses_state_annual): One state's (or the nation's) yearly natural gas used as vehicle fuel, lease and plant fuel or pipeline fuel, or delivered to consumers, from EIA's Natural Gas Annual.
- [`eia_gas_pipeline_projects`](#eia_gas_pipeline_projects): One natural gas pipeline project on EIA's tracker (current or historical sheet), as of the tracker of August 2026.
- [`eia_gas_plant_processing_annual`](#eia_gas_plant_processing_annual): One year's natural gas plant processing figure (gas processed, extraction loss or liquids extracted) for the U.S., a state or one of EIA's processing areas.
- [`eia_gas_prices_state_monthly`](#eia_gas_prices_state_monthly): One state's (or the nation's) monthly average natural gas price in one category (citygate, residential, commercial, industrial, electric power), as EIA's Natural Gas Monthly gives it.
- [`eia_gas_production_state_monthly`](#eia_gas_production_state_monthly): One state's, offshore area's or the nation's monthly natural gas production figure (gross withdrawals, marketed or dry production, vented and flared, shale gas), from EIA's Natural Gas Monthly.
- [`eia_gas_reserves_annual`](#eia_gas_reserves_annual): One state's, area's or the nation's dry natural gas proved reserves at a year's end, or one of the changes that take one year's reserves to the next.
- [`eia_gas_storage_capacity_monthly`](#eia_gas_storage_capacity_monthly): One month's underground natural gas storage capacity (total or working gas) or number of storage fields, for a state, region, the lower 48 or the U.S.
- [`eia_gas_storage_state_monthly`](#eia_gas_storage_state_monthly): One state's, region's or the nation's monthly natural gas in underground storage (a month-end stock) or injections and withdrawals (a flow over the month).
- [`eia_gas_storage_type_monthly`](#eia_gas_storage_type_monthly): One month's U.S. underground natural gas storage figure for all fields, salt caverns or non-salt fields.
- [`eia_gas_storage_weekly`](#eia_gas_storage_weekly): One region's (or the Lower 48's) working gas in underground storage at the end of one report week, from EIA's Weekly Natural Gas Storage Report.
- [`eia_gas_trade_country_monthly`](#eia_gas_trade_country_monthly): One month's U.S. natural gas exports or imports with one country by one mode (pipeline, LNG by vessel, truck, compressed, re-exports), as a volume or a price.
- [`eia_gas_trade_monthly`](#eia_gas_trade_monthly): One month's natural gas imports or exports through one route (pipeline with Canada or Mexico, LNG in all, or one point of exit), in million cubic feet.
- [`eia_gas_wells_annual`](#eia_gas_wells_annual): One state's (or the nation's or the federal Gulf's) yearly number of producing natural gas and gas condensate wells, from EIA's Natural Gas Annual.
- [`eia_heat_rates_annual`](#eia_heat_rates_annual): One fuel's (coal, petroleum, natural gas, nuclear) average operating heat rate for one year, from EIA's Electric Power Annual Table 8.1.
- [`eia_heating_fuel_prices_weekly`](#eia_heating_fuel_prices_weekly): One week's residential or wholesale price of heating oil or propane in one state, PADD or the nation, in the heating season.
- [`eia_hgl_pipelines`](#eia_hgl_pipelines): One pipeline segment of EIA's Hydrocarbon Gas Liquids (HGL) Pipelines map layer (updated January 2020).
- [`eia_ieo_projections`](#eia_ieo_projections): One series of EIA's International Energy Outlook 2023, reference case (a world region's energy consumption, CO2 emissions, or electricity generation or capacity by fuel), for one year.
- [`eia_international_electricity_annual`](#eia_international_electricity_annual): One year's electricity figure (generation by product, consumption, trade, losses or capacity) for the U.S., Canada or Mexico, from EIA's International Energy Statistics.
- [`eia_lng_exports_monthly`](#eia_lng_exports_monthly): One LNG export terminal's monthly export volume or export price, as EIA reports it.
- [`eia_lng_liquefaction_projects`](#eia_lng_liquefaction_projects): One train (liquefaction unit) of a U.S. LNG export project in operation, commissioning or construction, or one large approved project, from EIA's U.S. Liquefaction Capacity workbook (2026 Q3).
- [`eia_lng_storage_annual`](#eia_lng_storage_annual): One year's LNG additions to or withdrawals from storage (peak-shaving tanks, not export terminals) in the U.S. or one state.
- [`eia_mecs_manufacturing`](#eia_mecs_manufacturing): One industry's (by NAICS code, or all manufacturing) figure in the nation or one census region, from EIA's 2022 Manufacturing Energy Consumption Survey (fuel consumption by source, or an electricity component).
- [`eia_meters_state_annual`](#eia_meters_state_annual): One state's (or the nation's) yearly count of electricity meters of one technology in one sector.
- [`eia_net_imports_monthly`](#eia_net_imports_monthly): One month's U.S. net imports (imports less exports) of crude oil, petroleum products or both with one partner country, group or the world.
- [`eia_net_metering_state_annual`](#eia_net_metering_state_annual): One state's (or the nation's) yearly net-metered capacity or customers (customers who generate their own power and are credited for what they send to the grid) of one technology in one sector.
- [`eia_ngl_production_monthly`](#eia_ngl_production_monthly): One month's natural gas plant field production of one natural gas liquid in the U.S., a PADD or a refining district, in the month or per day.
- [`eia_nuclear_outages_daily`](#eia_nuclear_outages_daily): One day's U.S. nuclear fleet capacity, capacity on outage, or share on outage, EIA's estimate from the NRC's daily power reactor status reports.
- [`eia_nuclear_outages_facility_daily`](#eia_nuclear_outages_facility_daily): One nuclear plant's day of capacity, capacity on outage, or share on outage, EIA's estimate from the NRC's daily power reactor status reports.
- [`eia_nuclear_outages_generator_daily`](#eia_nuclear_outages_generator_daily): One nuclear reactor's day of capacity, capacity on outage, or share on outage, EIA's estimate from the NRC's daily power reactor status reports.
- [`eia_oxygenate_production_monthly`](#eia_oxygenate_production_monthly): One month's oxygenate plant production (fuel ethanol, MTBE and other oxygenates) or biofuels plant net production in the U.S. or a PADD, in the month or per day.
- [`eia_padd_crude_pipeline_flows`](#eia_padd_crude_pipeline_flows): One month's crude oil received by pipeline in one PADD from another PADD, as EIA reports it.
- [`eia_padd_rail_barge_movements_monthly`](#eia_padd_rail_barge_movements_monthly): One month's movement of crude oil or a petroleum product into one PADD from another, by rail or by tanker and barge.
- [`eia_petroleum_exports_by_destination`](#eia_petroleum_exports_by_destination): One month's U.S. exports of crude oil or one petroleum product to one destination country, in the month or per day.
- [`eia_petroleum_snd_monthly`](#eia_petroleum_snd_monthly): One month's supply or disposition figure (production, inputs, trade, stocks, product supplied) of crude oil or one petroleum product in the U.S. or a PADD, from EIA's Petroleum Supply Monthly.
- [`eia_petroleum_stocks_monthly`](#eia_petroleum_stocks_monthly): One month's end stocks of one petroleum product (gasoline, distillate and its grades, propane, residual fuel) in the U.S., a PADD or a PADD 1 sub-district.
- [`eia_petroleum_stocks_state_monthly`](#eia_petroleum_stocks_state_monthly): One month's end stocks of one petroleum product at refineries, bulk terminals and natural gas plants in one state, PADD or the U.S.
- [`eia_petroleum_stocks_weekly`](#eia_petroleum_stocks_weekly): One week's U.S. ending stocks of crude oil (with or without the Strategic Petroleum Reserve) or one petroleum product, from EIA's Weekly Petroleum Status Report.
- [`eia_petroleum_supply_weekly`](#eia_petroleum_supply_weekly): One week's value of one U.S. petroleum supply series (a stock, crude production, refinery utilization, crude input or a trade flow), from EIA's Weekly Petroleum Status Report.
- [`eia_petroleum_trade_weekly`](#eia_petroleum_trade_weekly): One week's U.S. imports, exports or net imports of crude oil, petroleum products or both, from EIA's Weekly Petroleum Status Report.
- [`eia_power_co2_state_annual`](#eia_power_co2_state_annual): One state's (or the nation's) yearly carbon dioxide emissions from power plants of one fuel, or their emission rate, from EIA's State Electricity Profiles.
- [`eia_power_costs_annual`](#eia_power_costs_annual): One year's figure from EIA's Electric Power Annual chapter 8 (tables 8.1 to 8.4) for the U.S. (a heat rate, a line of investor-owned utilities' revenue and expenses, or a plant type's operating expense).
- [`eia_power_fuel_stocks_monthly`](#eia_power_fuel_stocks_monthly): One location's month-end stocks of coal, petroleum liquids or petroleum coke at power plants, in the electric power sector or all sectors (Form EIA-923).
- [`eia_power_plant_fuel_costs`](#eia_power_plant_fuel_costs): One location's monthly average cost of coal or natural gas delivered to the electric power sector, in one unit (per MMBtu, per short ton, per Mcf), from Form EIA-923.
- [`eia_primary_energy_monthly`](#eia_primary_energy_monthly): One month's U.S. primary energy production, trade, stock change or consumption, in all or of one source, from EIA's Monthly Energy Review (Tables 1.1 to 1.3).
- [`eia_product_spot_prices`](#eia_product_spot_prices): One trading day's spot price of one refined product at one trading hub (gasoline, RBOB, ultra-low sulfur diesel, CARB diesel, jet fuel, heating oil, propane), as EIA reports it.
- [`eia_product_supplied_monthly`](#eia_product_supplied_monthly): One month's product supplied (EIA's measure of consumption) of one petroleum product in the U.S. or a PADD, in the month or per day.
- [`eia_recs_households`](#eia_recs_households): One category of homes (by a household or housing characteristic, or all homes) and one figure from EIA's 2020 Residential Energy Consumption Survey tables CE4.1 and CE4.11.
- [`eia_refinery_capacity_annual`](#eia_refinery_capacity_annual): One refinery capacity figure as of 1 January of a year (operable distillation or downstream charge capacity of one process, or the number of refineries), for a state, PADD or the U.S.
- [`eia_refinery_inputs_monthly`](#eia_refinery_inputs_monthly): One month's refinery and blender net input of one product in the U.S., a PADD or a refining district, in the month or per day.
- [`eia_refinery_production_monthly`](#eia_refinery_production_monthly): One month's refinery and blender net production of one product in the U.S., a PADD or a refining district, in the month or per day.
- [`eia_refinery_utilization_monthly`](#eia_refinery_utilization_monthly): One month's refinery gross input, capacity (operable, operating, idle) or utilization in the U.S., a PADD or a refining district.
- [`eia_refinery_weekly`](#eia_refinery_weekly): One week's refinery input of one product, operable capacity or utilization in the U.S. or a PADD, from EIA's Weekly Petroleum Status Report.
- [`eia_regional_retail_fuel_prices`](#eia_regional_retail_fuel_prices): One week's retail price of regular gasoline or No. 2 diesel in one region, state or city, from EIA's Gasoline and Diesel Fuel Update.
- [`eia_retail_electricity_prices`](#eia_retail_electricity_prices): One state's (or census division's, or the nation's) monthly average retail price of electricity in one sector.
- [`eia_retail_fuel_prices`](#eia_retail_fuel_prices): One week's U.S. retail price of gasoline (regular or all grades) or No. 2 diesel, from EIA's Gasoline and Diesel Fuel Update.
- [`eia_retail_sales_monthly`](#eia_retail_sales_monthly): One state's (or census division's, or the nation's) monthly retail sales of electricity, or number of customers, in one sector (Form EIA-861M).
- [`eia_sector_energy_consumption_monthly`](#eia_sector_energy_consumption_monthly): One month's U.S. energy consumption of one source by the industrial or commercial sector, from EIA's Monthly Energy Review (Tables 2.3 and 2.4).
- [`eia_seds_industrial_annual`](#eia_seds_industrial_annual): One state's (or the nation's) yearly figure for the industrial sector from EIA's State Energy Data System (consumption of one energy source, expenditures, or the average price).
- [`eia_seds_residential_annual`](#eia_seds_residential_annual): One state's (or the nation's) yearly figure for the residential sector from EIA's State Energy Data System (expenditures by source, total consumption, average price) or the state's population.
- [`eia_seds_state_energy`](#eia_seds_state_energy): One state's (or the nation's) yearly figure of one SEDS series (consumption by source or sector, an electricity or gas price, or expenditures).
- [`eia_shale_gas_reserves_annual`](#eia_shale_gas_reserves_annual): One year's shale gas proved reserves, reserves-based production, or a change in reserves, for the U.S., a state or a reporting district (2007 to 2021).
- [`eia_state_capacity_annual`](#eia_state_capacity_annual): One state's (or the nation's) net summer generating capacity of one producer type and one energy source at one year, from EIA's State Electricity Profiles.
- [`eia_state_generation_monthly`](#eia_state_generation_monthly): One state's (or census region's, or the nation's) monthly net electricity generation from one energy source, all sectors (Form EIA-923).
- [`eia_state_source_disposition_annual`](#eia_state_source_disposition_annual): One state's (or the nation's) yearly electricity supply or disposition figure, one of EIA's columns in its State Electricity Profiles.
- [`eia_state_to_state_capacity`](#eia_state_to_state_capacity): One natural gas pipeline's capacity at one state (or national) border crossing for one year, from EIA's U.S. State-to-State Capacity workbook (2026-01 issue).
- [`eia_steo_forecasts`](#eia_steo_forecasts): One series' value for one month (or year) as one release of EIA's Short-Term Energy Outlook gives it, forecast or history; each release kept.
- [`eia_uranium_facilities`](#eia_uranium_facilities): One U.S. uranium mill or heap leach facility (Table 3) or in-situ recovery plant (Table 4) of EIA's Domestic Uranium Production Report, with its owner, place, capacity and operating status by period.
- [`eia_uranium_marketing_annual`](#eia_uranium_marketing_annual): One year's figure of EIA's Uranium Marketing Annual Report summary tables for the U.S. (uranium bought by reactor owners and operators and its price, feed, enrichment, loadings, foreign trade or inventories).
- [`eia_uranium_production_quarterly`](#eia_uranium_production_quarterly): One U.S. facility's (or EIA's total) uranium concentrate production in one quarter, or the number of facilities of one kind producing at the end of a year or the latest quarter.
- [`eia_wood_pellets_monthly`](#eia_wood_pellets_monthly): One month's figure from EIA's Monthly Densified Biomass Fuel Report (wood pellets) for a region, the U.S. or a feedstock type (a price, a feedstock cost, facilities or employees).
- [`eia_world_coal_annual`](#eia_world_coal_annual): One country's or region's yearly coal figure (production, consumption, trade or reserves) for one coal product, from EIA's International Energy Statistics bulk file.
- [`eia_world_electricity_annual`](#eia_world_electricity_annual): One country's or region's yearly electricity figure (generation by product, consumption, trade, losses or capacity), from EIA's International Energy Statistics bulk file.
- [`eia_world_energy_co2_annual`](#eia_world_energy_co2_annual): One country's or region's yearly total primary energy production or consumption (in all or by source) or energy-related CO2 emissions, from EIA's International Energy Statistics bulk file.
- [`eia_world_oil_gas_annual`](#eia_world_oil_gas_annual): One country's or region's yearly petroleum or natural gas figure (production, consumption, trade, bunkers or stocks) for one product, from EIA's International Energy Statistics bulk file.
- [`eia_world_oil_monthly`](#eia_world_oil_monthly): One country's or region's monthly petroleum production, consumption or stocks for one product, from EIA's International Energy Statistics bulk file.

### `eia_aeo_electricity`

One series of EIA's Annual Energy Outlook 2026 electricity Tables 8 and 9 (capacity, generation or a price), in one case (scenario), for one projected year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 34034.

- **Time:** ts_utc is 1 January of the projected year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot); the release is in the entity id, vintage is not filled.
- **Source:** eia:aeo U.S. Energy Information Administration, Annual Energy Outlook 2026 (API v2, route aeo/2026) (https://www.eia.gov/outlooks/aeo/)
- **Method note:** [`docs/methods/eia_aeo_electricity.md`](../methods/eia_aeo_electricity.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Annual Energy Outlook (API v2, Tables 8 and 9). Via the Energy Research Warehouse (ERW), table `eia_aeo_electricity`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_aeo_2026:<seriesId>:<case> | none | text | for example eia_aeo_2026:cap_NA_elep_NA_cuc_NA_usa_gw:altelec, eia_aeo_2026:cap_NA_elep_NA_cuc_NA_usa_gw:alttrnp, eia_aeo_2026:cap_NA_elep_NA_cuc_NA_usa_gw:cb2026; 1309 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-01-01T00:00:00Z to 2050-01-01T00:00:00Z; 26 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -43447357.0 to 6775515137.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD/kWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 34034 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's name of the series | none | text | for example Electricity : Direct Use, Electricity : Electric Power Sector : Combined Heat and Power : Coal, Electricity : Electric Power Sector : Combined Heat and Power : Natural Gas; 111 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:aeo | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=8&facets%5Bscenario%5D%5B%5D=altelec&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=8&facets%5Bscenario%5D%5B%5D=alttrnp&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=8&facets%5Bscenario%5D%5B%5D=cb2026&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=8&facets%5Bscenario%5D%5B%5D=electrnp&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=8&facets%5Bscenario%5D%5B%5D=highZTC&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=8&facets%5Bscenario%5D%5B%5D=higheldmd&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=8&facets%5Bscenario%5D%5B%5D=highogs&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=8&facets%5Bscenario%5D%5B%5D=hm2026&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=8&facets%5Bscenario%5D%5B%5D=lm2026&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=8&facets%5Bscenario%5D%5B%5D=lowZTC&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=8&facets%5Bscenario%5D%5B%5D=lowogs&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=9&facets%5Bscenario%5D%5B%5D=altelec&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=9&facets%5Bscenario%5D%5B%5D=alttrnp&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=9&facets%5Bscenario%5D%5B%5D=cb2026&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=9&facets%5Bscenario%5D%5B%5D=electrnp&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=9&facets%5Bscenario%5D%5B%5D=highZTC&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=9&facets%5Bscenario%5D%5B%5D=higheldmd&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=9&facets%5Bscenario%5D%5B%5D=highogs&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=9&facets%5Bscenario%5D%5B%5D=hm2026&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=9&facets%5Bscenario%5D%5B%5D=lm2026&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=9&facets%5Bscenario%5D%5B%5D=lowZTC&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=9&facets%5Bscenario%5D%5B%5D=lowogs&length=5000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T18:31:12Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: the release is in the entity id | none | empty | no cell holds a value | 34034 |
| `x_table` | The AEO table the series is read from (8 or 9) (the source's name: tableId) | none | integer | 8, 9 | 0 |
| `x_scenario` | EIA's code of the AEO case (scenario) the projection belongs to (the source's name: scenario) | none | text | altelec, alttrnp, cb2026, electrnp, highZTC, higheldmd, highogs, hm2026, lm2026, lowZTC, lowogs | 0 |
| `x_scenario_name` | EIA's name of the case (the source's name: scenarioDescription) | none | text | Alternative Electricity, Alternative Electricity and Transportation, Alternative Transportation, Counterfactual Baseline case, High Economic Growth, High Electricity Demand, High Oil and Gas Supply, High Zero-Carbon Technology Cost, Low Economic Growth, Low Oil and Gas Supply, Low Zero-Carbon Technology Cost | 0 |
| `x_history` | EIA's flag saying whether the year is history or projection (every row here is PROJECTION) (the source's name: history) | none | text | PROJECTION | 0 |
| `x_region` | EIA's region identifier of the series (0-0, the United States, on every row) (the source's name: regionId) | none | text | 0-0 | 0 |
| `x_dollar_year` | The dollars a price is in: 2025 for the AEO's real 2025 dollars, or nominal | none | text | 2025, nominal | 29458: Not a price (a capacity or a generation row) |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `value` | The AEO series the entity names: capacity in MW (EIA's GW times 1,000), generation in MWh (EIA's billion kWh) or a price in USD per kWh (cents times 0.01); the unit column says which | MW; MWh; USD/kWh | 34034 | 2025-01-01T00:00:00Z | 2050-01-01T00:00:00Z |

### `eia_aeo_emm_regions`

One series of EIA's Annual Energy Outlook 2026 Table 54 (electric power projections) for one Electricity Market Module region or the U.S., case cb2026, for one projected year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 75712.

- **Time:** ts_utc is 1 January of the projected year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot); vintage is not filled.
- **Source:** eia:aeo_regions U.S. Energy Information Administration, Annual Energy Outlook 2026, Table 54 (API v2, route aeo/2026, tableId 62) (https://www.eia.gov/outlooks/aeo/)
- **Method note:** [`docs/methods/eia_aeo_emm_regions.md`](../methods/eia_aeo_emm_regions.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Annual Energy Outlook (API v2, Table 54 by EMM region). Via the Energy Research Warehouse (ERW), table `eia_aeo_emm_regions`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_aeo_2026_emm:<regionId>:<seriesId>; regionId 5-1 to 5-25 an EMM region, 5-0 the United States | none | text | for example eia_aeo_2026_emm:5-0:cap_NA_elep_NA_NA_NA_NA_gw, eia_aeo_2026_emm:5-0:cap_NA_elep_NA_cl_NA_NA_gw, eia_aeo_2026_emm:5-0:cap_NA_elep_NA_cmc_NA_NA_gw; 2912 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-01-01T00:00:00Z to 2050-01-01T00:00:00Z; 26 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -22434444.0 to 6272780762.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, TBtu, USD/MMBtu, USD/kWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US for 5-0; empty for a region (it spans states) | none | text | US | 72800 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 75712 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <region>: <series name> | none | text | for example Florida Reliability Coordinating Council: Electricity : Electric Power Sector : Capacity : Coal, Florida Reliability Coordinating Council: Electricity : Electric Power Sector : Capacity : Combined Cycle, Florida Reliability Coordinating Council: Electricity : Electric Power Sector : Capacity : Combustion Turbine/Diesel; 2600 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:aeo_regions | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=62&facets%5Bscenario%5D%5B%5D=cb2026 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T08:17:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 75712 |
| `x_scenario` | EIA's code of the AEO case (cb2026 on every row) (the source's name: scenario) | none | text | cb2026 | 0 |
| `x_scenario_name` | EIA's name of the case (Counterfactual Baseline case) (the source's name: scenarioDescription) | none | text | Counterfactual Baseline case | 0 |
| `x_history` | EIA's flag saying whether the year is history or projection (every row here is PROJECTION) (the source's name: history) | none | text | PROJECTION | 0 |
| `x_region` | EIA's Electricity Market Module region identifier (5-1 to 5-25, or 5-0 for the United States) (the source's name: regionId) | none | text | for example 5-0, 5-1, 5-10; 26 distinct | 0 |
| `x_region_name` | EIA's name of the region (the source's name: regionName) | none | text | for example Florida Reliability Coordinating Council, Midcontinent / Central, Midcontinent / East; 26 distinct | 0 |
| `x_dollar_year` | The dollars a price is in: 2025 for the AEO's real 2025 dollars, or nominal | none | text | 2025, nominal | 59488: Not a price (a quantity row) |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `value` | The Table 54 series the entity names: capacity in MW, generation in MWh, energy in TBtu (quads times 1,000), or a price in USD per kWh or USD per MMBtu; the unit column says which. A total and its parts overlap | MW; MWh; TBtu; USD/MMBtu; USD/kWh | 75712 | 2025-01-01T00:00:00Z | 2050-01-01T00:00:00Z |

### `eia_aeo_industrial`

One series of EIA's Annual Energy Outlook 2026 industrial sub-sector tables (an industry's energy use of one fuel), in one case (scenario), for one projected year, in trillion Btu.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 75504.

- **Time:** ts_utc is 1 January of the projected year at 00:00:00Z (freq P1Y); a year, not an instant.
- **Revisions:** Rewritten whole by each run (write_snapshot) from the newest AEO release the API lists; vintage is not filled.
- **Source:** eia:aeo_industrial U.S. Energy Information Administration, Annual Energy Outlook 2026 (API v2, route aeo/2026) (https://www.eia.gov/outlooks/aeo/)
- **Method note:** [`docs/methods/industry_page.md`](../methods/industry_page.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Annual Energy Outlook (API v2): the industrial sub-sector tables, energy use by fuel. Via the Energy Research Warehouse (ERW), table `eia_aeo_industrial`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_aeo_2026:<seriesId>.<h>:<case>, h six hex digits of the sha1 of the series' name, since EIA gives one seriesId to two series | none | text | for example eia_aeo_2026:cnsm_NA_idal_aap_dfo_NA_NA_trlbtu.a0df3d:altelec, eia_aeo_2026:cnsm_NA_idal_aap_dfo_NA_NA_trlbtu.a0df3d:alttrnp, eia_aeo_2026:cnsm_NA_idal_aap_dfo_NA_NA_trlbtu.a0df3d:cb2026; 2904 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-01-01T00:00:00Z to 2050-01-01T00:00:00Z; 26 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -35.413647 to 12210.396484; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | TBtu | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 75504 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's name of the series (industry, measure and fuel) | none | text | for example Aluminum Industry : Energy Use : Distillate Fuel Oil, Aluminum Industry : Energy Use : Natural Gas, Aluminum Industry : Energy Use : Other Petroleum; 264 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:aeo_industrial | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=139&sort%5B0%5D%5Bcolumn%5D=seriesId&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=scenario&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=period&sort%5B2%5D%5Bdirection%5D=asc&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=140&sort%5B0%5D%5Bcolumn%5D=seriesId&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=scenario&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=period&sort%5B2%5D%5Bdirection%5D=asc&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=35&sort%5B0%5D%5Bcolumn%5D=seriesId&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=scenario&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=period&sort%5B2%5D%5Bdirection%5D=asc&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=36&sort%5B0%5D%5Bcolumn%5D=seriesId&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=scenario&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=period&sort%5B2%5D%5Bdirection%5D=asc&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=37&sort%5B0%5D%5Bcolumn%5D=seriesId&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=scenario&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=period&sort%5B2%5D%5Bdirection%5D=asc&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=38&sort%5B0%5D%5Bcolumn%5D=seriesId&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=scenario&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=period&sort%5B2%5D%5Bdirection%5D=asc&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=39&sort%5B0%5D%5Bcolumn%5D=seriesId&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=scenario&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=period&sort%5B2%5D%5Bdirection%5D=asc&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=40&sort%5B0%5D%5Bcolumn%5D=seriesId&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=scenario&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=period&sort%5B2%5D%5Bdirection%5D=asc&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=41&sort%5B0%5D%5Bcolumn%5D=seriesId&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=scenario&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=period&sort%5B2%5D%5Bdirection%5D=asc&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=42&sort%5B0%5D%5Bcolumn%5D=seriesId&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=scenario&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=period&sort%5B2%5D%5Bdirection%5D=asc&length=5000, https://api.eia.gov/v2/aeo/2026/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BtableId%5D%5B%5D=43&sort%5B0%5D%5Bcolumn%5D=seriesId&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=scenario&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=period&sort%5B2%5D%5Bdirection%5D=asc&length=5000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T11:48:15Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 75504 |
| `x_series_id` | EIA's series identifier in the AEO (one id can name two series) (the source's name: seriesId) | none | text | for example cnsm_NA_idal_aap_dfo_NA_NA_trlbtu, cnsm_NA_idal_aap_ng_NA_NA_trlbtu, cnsm_NA_idal_aap_onp_NA_NA_trlbtu; 259 distinct | 0 |
| `x_table_id` | The EIA API's identifier of the AEO table the series is read from (the source's name: tableId) | none | integer | 139, 140, 35, 36, 37, 38, 39, 40, 41, 42, 43 | 0 |
| `x_table` | The AEO's own table number (24 to 34), one table per industry | none | integer | 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34 | 0 |
| `x_industry` | The industry of the table (refining, food, paper, bulk chemicals, glass, cement and lime, iron and steel, aluminum, metal-based durables, other manufacturing, nonmanufacturing) | none | text | aluminum, bulk_chemicals, cement_and_lime, food, glass, iron_and_steel, metal_based_durables, nonmanufacturing, other_manufacturing, paper, refining | 0 |
| `x_scenario` | EIA's code of the AEO case (scenario) the projection belongs to (the source's name: scenario) | none | text | altelec, alttrnp, cb2026, electrnp, highZTC, higheldmd, highogs, hm2026, lm2026, lowZTC, lowogs | 0 |
| `x_scenario_name` | EIA's name of the case (the source's name: scenarioDescription) | none | text | Alternative Electricity, Alternative Electricity and Transportation, Alternative Transportation, Counterfactual Baseline case, High Economic Growth, High Electricity Demand, High Oil and Gas Supply, High Zero-Carbon Technology Cost, Low Economic Growth, Low Oil and Gas Supply, Low Zero-Carbon Technology Cost | 0 |
| `x_history` | EIA's flag saying whether the year is history or projection (every row here is PROJECTION) (the source's name: history) | none | text | PROJECTION | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` | Projected energy use by the industry of the fuel the series names, in trillion Btu | TBtu | 75504 | 2025-01-01T00:00:00Z | 2050-01-01T00:00:00Z |

### `eia_annual_crosscheck_ba`

One balancing authority's (or the Lower 48's) year of EIA-930's hourly net generation summed, set against EIA-923's annual figure, with the gap and the hours counted.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 144.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y); EIA-930's hours are summed by their UTC start.
- **Revisions:** Rewritten whole by each run of the builder (the file is deleted, then written); vintage is not filled.
- **Source:** erw:eia_annual_crosscheck_ba ERW cross-check of EIA's hourly and annual generation by balancing authority (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/eia_annual_crosscheck.md)
- **Method note:** [`docs/methods/eia_annual_crosscheck.md`](../methods/eia_annual_crosscheck.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Cross-check of EIA-930's hourly sums against EIA-923's annual net generation by balancing authority (session 323). Via the Energy Research Warehouse (ERW), table `eia_annual_crosscheck_ba`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930:<BA>, eia930:US48 for the Lower 48 | none | text | eia930:CISO, eia930:ERCO, eia930:ISNE, eia930:MISO, eia930:NYIS, eia930:PJM, eia930:SWPP, eia930:US48 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -214127374.999 to 4494650070.999; 104 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 144 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 144 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:eia_annual_crosscheck_ba | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/eia_annual_crosscheck.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-19T23:00:42Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 144 |
| `x_reason` | The likely reason for the gap, by the ERW's rule (within 2 percent, missing hours, or the likely cause by the gap's sign); hypotheses, not EIA's statements | none | text | likely: EIA-930 higher because the BA meters generation from plants EIA-923 codes to another balancing authority (dynamic schedules, pseudo-ties), or EIA-930's own reporting, likely: EIA-930 higher because the BA meters generation from plants EIA-923 codes to another balancing authority (dynamic schedules, pseudo-ties), or EIA-930's own reporting (EIA-930 also lacks 1 of the year's 8784 hours), likely: EIA-930 lower because it counts what the balancing authority meters, while EIA-923 counts each plant's own net generation, industrial self-generation consumed on site among it; or plants coded to the BA are scheduled into a neighbour, likely: EIA-930 lower because it counts what the balancing authority meters, while EIA-923 counts each plant's own net generation, industrial self-generation consumed on site among it; or plants coded to the BA are scheduled into a neighbour (EIA-930 also lacks 2 of the year's 8760 hours), likely: EIA-930 lower because it counts what the balancing authority meters, while EIA-923 counts each plant's own net generation, industrial self-generation consumed on site among it; or plants coded to the BA are scheduled into a neighbour (EIA-930 also lacks 23 of the year's 8760 hours), likely: EIA-930 lower because it counts what the balancing authority meters, while EIA-923 counts each plant's own net generation, industrial self-generation consumed on site among it; or plants coded to the BA are scheduled into a neighbour (EIA-930 also lacks 24 of the year's 8784 hours), likely: EIA-930 lower because it counts what the balancing authority meters, while EIA-923 counts each plant's own net generation, industrial self-generation consumed on site among it; or plants coded to the BA are scheduled into a neighbour (EIA-930 also lacks 48 of the year's 8760 hours), likely: EIA-930 lower because it counts what the balancing authority meters, while EIA-923 counts each plant's own net generation, industrial self-generation consumed on site among it; or plants coded to the BA are scheduled into a neighbour (EIA-930 also lacks 48 of the year's 8784 hours), within 2 percent: the two counts agree to the size of what each leaves out (EIA-930 also lacks 25 of the year's 8760 hours), within 2 percent: the two counts agree to the size of what each leaves out (EIA-930 also lacks 47 of the year's 8784 hours) | 0 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `eia923_net_generation_mwh` | EIA-923's annual net generation of the plants coded to the authority, storage included, MWh | MWh | 24 | 2023-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `eia930_hours` | The hours EIA-930 reported in the year | count | 24 | 2023-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `eia930_net_generation_mwh` | The year's sum of EIA-930's hourly net generation for the authority, MWh | MWh | 24 | 2023-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `expected_hours` | The hours in the year | count | 24 | 2023-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `gap_mwh` | EIA-930's sum less EIA-923's, MWh | MWh | 24 | 2023-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `gap_pct` | The gap as a percent of EIA-923's figure | pct | 24 | 2023-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `eia_annual_generation_ba`

One balancing authority's year of net generation, storage net generation or plant count, summed from Form EIA-923's plant rows by their Balancing Authority Code.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 515.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (the file is deleted and rebuilt from the annual files); vintage is the year's file's Last-Modified time.
- **Source:** eia:eia923_annual U.S. Energy Information Administration, Form EIA-923 Power Plant Operations Report, annual files (https://www.eia.gov/electricity/data/eia923/)
- **Method note:** [`docs/methods/eia_annual_generation_ba.md`](../methods/eia_annual_generation_ba.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Form EIA-923 Power Plant Operations Report, annual files (net generation by plant, summed by balancing authority). Via the Energy Research Warehouse (ERW), table `eia_annual_generation_ba`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia923:<balancing authority code>; eia923:none for plants with no code, eia923:state_fuel_increment for EIA's state-fuel level increment rows | none | text | for example eia923:AECI, eia923:AVA, eia923:AVRN; 68 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1108134.0 to 879123805.594; 424 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 515 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 515 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:eia923_annual | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/electricity/data/eia923/archive/xls/f923_2023.zip, https://www.eia.gov/electricity/data/eia923/archive/xls/f923_2024.zip, https://www.eia.gov/electricity/data/eia923/xls/f923_2025.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-19T21:08:49Z, 2026-10-19T21:08:50Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The Last-Modified time of the year's EIA-923 zip file | none | utc time | 2025-08-19T13:42:05Z, 2026-01-12T20:59:57Z, 2026-09-11T13:28:33Z | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `net_generation_mwh` | Net generation of the plants coded to the authority in the year (sheet Page 1 Generation and Fuel Data), MWh | MWh | 201 | 2023-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `plants` | The plants with a row coded to the authority | count | 201 | 2023-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `storage_net_generation_mwh` | Net generation of the storage plants coded to the authority (sheet Page 1 Energy Storage, negative), MWh | MWh | 113 | 2023-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `eia_basin_production_monthly`

One producing region's monthly crude oil production or marketed natural gas production, as EIA's Short-Term Energy Outlook gives its history.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1680.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (the file is deleted and the whole series from 2015 written again), so the Outlook's revisions are taken; months later than three before the run, EIA's estimates and forecast, are not written. vintage is not filled.
- **Source:** eia:steo:basin_production EIA, Short-Term Energy Outlook: crude oil and natural gas production by region (https://www.eia.gov/outlooks/steo/)
- **Method note:** [`docs/methods/eia_basin_production_monthly.md`](../methods/eia_basin_production_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Short-Term Energy Outlook: crude oil and natural gas production by region. Via the Energy Research Warehouse (ERW), table `eia_basin_production_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:<Short-Term Energy Outlook series id> | none | text | eia:COPRAP, eia:COPRBK, eia:COPREF, eia:COPRHA, eia:COPRPM, eia:COPRR48, eia:NGMPAP, eia:NGMPBK, eia:NGMPEF, eia:NGMPHA, eia:NGMPPM, eia:NGMPR48 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 140 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.153108 to 6853.875428; 1680 distinct | 0 |
| `unit` | The unit of the row's value | none | text | bcf/d, kbbl/d | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, the regions included | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1680 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's name of the series (the producing region) | none | text | Crude Oil Production: Appalachia, Crude Oil Production: Bakken, Crude Oil Production: Eagle Ford, Crude Oil Production: Haynesville, Crude Oil Production: Permian, Crude Oil Production: Rest of Lower 48 States, Natural Gas Appalachia Marketed Production, Natural Gas Bakken Marketed Production, Natural Gas Eagle Ford Marketed Production, Natural Gas Haynesville Marketed Production, Natural Gas Permian Marketed Production, Natural Gas Rest of U.S. Marketed Production | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:steo:basin_production | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/steo/data/?frequency=monthly&data%5B0%5D=value&facets%5BseriesId%5D%5B%5D=NGMPR48&facets%5BseriesId%5D%5B%5D=NGMPEF&facets%5BseriesId%5D%5B%5D=NGMPHA&facets%5BseriesId%5D%5B%5D=COPRAP&facets%5BseriesId%5D%5B%5D=COPRPM&facets%5BseriesId%5D%5B%5D=NGMPAP&facets%5BseriesId%5D%5B%5D=NGMPBK&facets%5BseriesId%5D%5B%5D=COPRBK&facets%5BseriesId%5D%5B%5D=COPREF&facets%5BseriesId%5D%5B%5D=COPRHA&facets%5BseriesId%5D%5B%5D=NGMPPM&facets%5BseriesId%5D%5B%5D=COPRR48&start=2015-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=seriesId&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T11:48:02Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1680 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `crude_production` | Crude oil production of the region, thousand barrels a day (the Outlook's million barrels a day times 1,000); the R48 series is the rest of the Lower 48, not a total | kbbl/d | 840 | 2015-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `gas_marketed_production` | Marketed natural gas production of the region, billion cubic feet a day as published; the R48 series is the rest of the U.S., not a total | bcf/d | 840 | 2015-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `eia_biofuel_plants`

One fuel ethanol, biodiesel or renewable diesel plant's production capacity as of 1 January of one year (Form EIA-819); a plant appears once a year.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 511.

- **Time:** No time column. status_date is the 1 January the capacity is as of; x_year names that year.
- **Revisions:** Rewritten whole by each run (write_snapshot); vintage is each workbook's last-modified time.
- **Source:** eia:biofuels_capacity EIA, U.S. Biofuels Plant Production Capacity (https://www.eia.gov/biofuels/capacity/)
- **Method note:** [`docs/methods/eia_biofuel_plants.md`](../methods/eia_biofuel_plants.md)
- **Cite as:** U.S. Energy Information Administration (EIA). U.S. Biofuels Plant Production Capacity; U.S. Fuel Ethanol, Biodiesel, and Renewable Diesel Fuel and Other Biofuels Plant Production Capacity. Via the Energy Research Warehouse (ERW), table `eia_biofuel_plants`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: eia_biofuel:<year>:<fuel>:<state>:<n>, n the plant's place among its year, fuel and state in EIA's workbook | none | text | for example eia_biofuel:2025:biodiesel:al:1, eia_biofuel:2025:biodiesel:ar:1, eia_biofuel:2025:biodiesel:ca:1; 511 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: plant on every row | none | text | plant | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The facility (2026); the city for 2025, whose sheets name no facility | none | text | for example ABERDEEN II, ADAMS, ADKINS ENERGY; 469 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> of the plant | none | text | for example US-AL, US-AR, US-CA; 39 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 511 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 511 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: Not filled: the capacities are in gallons and barrels, in x_ columns | MW | empty | no cell holds a value | 511 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: active on every row | none | text | active | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The 1 January the capacity is as of | none | date | 2025-01-01, 2026-01-01 | 0 |
| `operator` | The operator or owner, as the publisher writes it. Here: The entity or respondent as EIA writes it | none | text | for example ABSOLUTE ENERGY LLC, ACE ETHANOL LLC, ADKINS ENERGY LLC; 462 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:biofuels_capacity | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/biofuels/biodiesel/capacity/biodieselcapacity.xlsx, https://www.eia.gov/biofuels/capacity/biofuelscapacity.xlsx, https://www.eia.gov/biofuels/renewable/capacity/renewablescapacity.xlsx, https://www.eia.gov/petroleum/ethanolcapacity/ethanolcapacity.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:54:11Z, 2026-10-23T18:54:13Z, 2026-10-23T18:54:14Z, 2026-10-23T18:54:53Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time from EIA's server | none | utc time | 2025-09-19T19:11:44Z, 2025-09-19T20:23:45Z, 2025-09-22T16:47:13Z, 2026-09-09T21:16:23Z | 0 |
| `x_year` | The year whose 1 January the capacity is as of | none | integer | 2025, 2026 | 0 |
| `x_fuel` | The fuel: ethanol, biodiesel, or renewable diesel and other biofuels | none | text | biodiesel, ethanol, renewable_diesel_and_other | 0 |
| `x_facility_type` | EIA's facility type (2026); for 2025 the workbook's fuel in the combined report's words (the source's name: Facility type) | none | text | Biodiesel, Ethanol, Renewable Diesel Fuel and Other Biofuels | 0 |
| `x_padd` | The Petroleum Administration for Defense District (PADD, EIA's fuel-supply region) of the plant (the source's name: PADD) | none | text | PADD 1, PADD 2, PADD 3, PADD 4, PADD 5 | 0 |
| `x_city` | The plant's city as the 2025 workbooks print it (the source's name: City) | none | text | for example Aberdeen, Adams, Adrian; 231 distinct | 253: A 2026 row (the 2026 workbook names the facility, not the city) |
| `x_capacity_mmgal_per_year` | What the plant can make in a year, million gallons, as published ((s) is less than 0.5) (the source's name: Capacity (MMgal/yr)) | million gallons per year | text | for example (s), 0, 1; 142 distinct | 0 |
| `x_capacity_kbbl_per_day` | What the plant can make in a day, thousand barrels, as published ((s) is less than 0.5) (the source's name: Capacity (Mb/d)) | kbbl/d | text | for example (s), 0, 1; 29 distinct | 0 |
| `x_coprocessing` | yes where EIA's footnote marks a refinery co-processing renewable feedstock with petroleum | none | text | yes | 507: EIA marks no co-processing |

### `eia_capacity_factors_annual`

One energy source and technology's yearly capacity factor or time adjusted capacity for U.S. utility-scale generators, from EIA's Electric Power Annual Tables 4.8.A and 4.8.B.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 374.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot); vintage is the workbook's last-modified time.
- **Source:** eia:electric_power_annual U.S. Energy Information Administration, Electric Power Annual (https://www.eia.gov/electricity/annual/)
- **Method note:** [`docs/methods/eia_capacity_factors.md`](../methods/eia_capacity_factors.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Electric Power Annual (Tables 4.8.A, 4.8.B and 8.1). Via the Energy Research Warehouse (ERW), table `eia_capacity_factors_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_epa_cf:<energy source>:<technology>, all where EIA gives no technology | none | text | eia_epa_cf:coal:all, eia_epa_cf:geothermal:all, eia_epa_cf:hydroelectric:all, eia_epa_cf:natural_gas:combined_cycle, eia_epa_cf:natural_gas:gas_turbine, eia_epa_cf:natural_gas:internal_combustion, eia_epa_cf:natural_gas:steam_turbine, eia_epa_cf:nuclear:all, eia_epa_cf:other_biomass:all, eia_epa_cf:other_fossil_gas:all, eia_epa_cf:petroleum:gas_turbine, eia_epa_cf:petroleum:internal_combustion, eia_epa_cf:petroleum:steam_turbine, eia_epa_cf:solar:photovoltaic, eia_epa_cf:solar:thermal, eia_epa_cf:wind:all, eia_epa_cf:wood:all | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.01 to 292281.3; 334 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 374 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's row name (source, technology) | none | text | Coal, Geothermal, Hydroelectric, Natural Gas, Combined Cycle, Natural Gas, Gas Turbine, Natural Gas, Internal Combustion, Natural Gas, Steam Turbine, Nuclear, Other Biomass, Other Fossil Gas, Petroleum, Gas Turbine, Petroleum, Internal Combustion, Petroleum, Steam Turbine, Solar, Photovoltaic, Solar, Thermal, Wind, Wood | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:electric_power_annual | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/electricity/annual/xls/epa_04_08_a.xlsx, https://www.eia.gov/electricity/annual/xls/epa_04_08_b.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T14:07:24Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time from EIA's server | none | utc time | 2026-10-19T22:48:17Z, 2026-10-19T22:48:21Z | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity_factor` | Capacity factor: the energy generated over what the capacity could make running all year, a ratio | ratio | 187 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `time_adjusted_capacity` | Summer capacity in operation the whole month, a year's the months' time weighted average, MW | MW | 187 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `eia_capacity_factors_monthly`

One energy source and technology's monthly capacity factor or time adjusted capacity for U.S. utility-scale generators, from EIA's Electric Power Annual Tables 4.8.A and 4.8.B.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1224.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot); vintage is the workbook's last-modified time.
- **Source:** eia:electric_power_annual U.S. Energy Information Administration, Electric Power Annual (https://www.eia.gov/electricity/annual/)
- **Method note:** [`docs/methods/eia_capacity_factors.md`](../methods/eia_capacity_factors.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Electric Power Annual (Tables 4.8.A, 4.8.B and 8.1). Via the Energy Research Warehouse (ERW), table `eia_capacity_factors_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_epa_cf:<energy source>:<technology>, all where EIA gives no technology | none | text | eia_epa_cf:coal:all, eia_epa_cf:geothermal:all, eia_epa_cf:hydroelectric:all, eia_epa_cf:natural_gas:combined_cycle, eia_epa_cf:natural_gas:gas_turbine, eia_epa_cf:natural_gas:internal_combustion, eia_epa_cf:natural_gas:steam_turbine, eia_epa_cf:nuclear:all, eia_epa_cf:other_biomass:all, eia_epa_cf:other_fossil_gas:all, eia_epa_cf:petroleum:gas_turbine, eia_epa_cf:petroleum:internal_combustion, eia_epa_cf:petroleum:steam_turbine, eia_epa_cf:solar:photovoltaic, eia_epa_cf:solar:thermal, eia_epa_cf:wind:all, eia_epa_cf:wood:all | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-01-01T00:00:00Z to 2025-12-01T00:00:00Z; 36 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.009 to 293802.5; 744 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1224 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's row name (source, technology) | none | text | Coal, Geothermal, Hydroelectric, Natural Gas, Combined Cycle, Natural Gas, Gas Turbine, Natural Gas, Internal Combustion, Natural Gas, Steam Turbine, Nuclear, Other Biomass, Other Fossil Gas, Petroleum, Gas Turbine, Petroleum, Internal Combustion, Petroleum, Steam Turbine, Solar, Photovoltaic, Solar, Thermal, Wind, Wood | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:electric_power_annual | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/electricity/annual/xls/epa_04_08_a.xlsx, https://www.eia.gov/electricity/annual/xls/epa_04_08_b.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T14:07:24Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time from EIA's server | none | utc time | 2026-10-19T22:48:17Z, 2026-10-19T22:48:21Z | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity_factor` | Capacity factor in the month: the energy generated over what the capacity could make, a ratio | ratio | 612 | 2023-01-01T00:00:00Z | 2025-12-01T00:00:00Z |
| `time_adjusted_capacity` | Summer capacity in operation the whole month, MW | MW | 612 | 2023-01-01T00:00:00Z | 2025-12-01T00:00:00Z |

### `eia_cbecs_commercial_buildings`

One category of commercial buildings (by a building characteristic, or all buildings) and one figure from EIA's 2018 Commercial Buildings Energy Consumption Survey tables C1, C2 and E1.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 5944.

- **Time:** ts_utc is 1 January of the survey year (2018) at 00:00:00Z (freq P1Y).
- **Revisions:** Written whole each run (write_snapshot) from the saved workbooks; EIA's revision is taken only when the saved copy is gone. vintage is each workbook's last-modified time.
- **Source:** eia:cbecs_2018 U.S. Energy Information Administration, 2018 Commercial Buildings Energy Consumption Survey (CBECS) (https://www.eia.gov/consumption/commercial/data/2018/)
- **Method note:** [`docs/methods/eia_buildings_surveys.md`](../methods/eia_buildings_surveys.md)
- **Cite as:** U.S. Energy Information Administration (EIA). 2018 Commercial Buildings Energy Consumption Survey (CBECS): consumption and expenditures, Tables C1, C2, E1. Via the Energy Research Warehouse (ERW), table `eia_cbecs_commercial_buildings`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: cbecs:<heading>_<category>, slugged; cbecs:all for all buildings | none | text | for example cbecs:all, cbecs:building_floorspace_square_feet_100_001_to_200_000, cbecs:building_floorspace_square_feet_10_001_to_25_000; 270 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 141238000000.0; 2552 distinct | 0 |
| `unit` | The unit of the row's value | none | text | TBtu, USD, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row (census regions are categories) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5944 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The category as EIA prints it | none | text | for example 0, 1, 1 elevator; 231 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:cbecs_2018 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/consumption/commercial/data/2018/ce/xls/c1.xlsx, https://www.eia.gov/consumption/commercial/data/2018/ce/xls/c2.xlsx, https://www.eia.gov/consumption/commercial/data/2018/ce/xls/e1.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:37:24Z, 2026-10-23T18:37:26Z, 2026-10-23T18:37:27Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time from EIA's server | none | utc time | 2022-12-15T11:32:48Z, 2022-12-16T16:51:21Z, 2023-07-28T13:37:19Z | 0 |
| `x_heading` | The heading the category sits under (for example Principal building activity), a footnote letter set aside | none | text | for example Building floorspace (square feet), Census region and division, Climate zone; 42 distinct | 23: The all-buildings row, which sits under no heading |
| `x_level` | The category's indent: 0 a category, 1 a part of the category above it (add level-0 rows only) | none | integer | 0, 1 | 0 |
| `x_parent` | The category a level-1 row is a part of | none | text | Any elevators, Any refrigeration, Any type of renovation, Desktop computers, Government owned, Health care, Mercantile, Midwest, Nongovernment owned, Northeast, South, West | 5019: A level-0 row (a part of no other category) |
| `x_table` | The CBECS table the figure is read from (C1, C2 or E1) | none | text | C1, C2, E1 | 0 |

Variables (23):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `buildings` | Number of buildings (C1, thousand buildings times 1,000) | count | 270 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `consumption_district_heat` | District heat consumed, trillion Btu (C1) | TBtu | 212 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `consumption_electricity_primary` | Electricity consumed, counted as the primary energy used to make it, trillion Btu (C1) | TBtu | 269 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `consumption_electricity_site` | Electricity consumed, at the site, trillion Btu (C1) | TBtu | 269 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `consumption_fuel_oil` | Fuel oil consumed, trillion Btu (C1) | TBtu | 233 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `consumption_natural_gas` | Natural gas consumed, trillion Btu (C1) | TBtu | 263 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `consumption_sum_major_fuels` | Consumption of the major fuels together, trillion Btu (C1) | TBtu | 269 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `enduse_computing` | Major fuels' consumption for computing, trillion Btu (E1) | TBtu | 258 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `enduse_cooking` | Major fuels' consumption for cooking, trillion Btu (E1) | TBtu | 262 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `enduse_cooling` | Major fuels' consumption for cooling, trillion Btu (E1) | TBtu | 266 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `enduse_lighting` | Major fuels' consumption for lighting, trillion Btu (E1) | TBtu | 267 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `enduse_office_equipment` | Major fuels' consumption for office equipment, trillion Btu (E1) | TBtu | 261 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `enduse_other` | Major fuels' consumption for other end uses, trillion Btu (E1) | TBtu | 266 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `enduse_refrigeration` | Major fuels' consumption for refrigeration, trillion Btu (E1) | TBtu | 264 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `enduse_space_heating` | Major fuels' consumption for space heating, trillion Btu (E1) | TBtu | 267 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `enduse_total` | Major fuels' consumption for all end uses, trillion Btu (E1) | TBtu | 269 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `enduse_ventilation` | Major fuels' consumption for ventilation, trillion Btu (E1) | TBtu | 267 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `enduse_water_heating` | Major fuels' consumption for water heating, trillion Btu (E1) | TBtu | 260 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `expenditure_district_heat` | Expenditure on district heat, USD (C2) | USD | 213 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `expenditure_electricity` | Expenditure on electricity, USD (C2) | USD | 269 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `expenditure_fuel_oil` | Expenditure on fuel oil, USD (C2) | USD | 237 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `expenditure_natural_gas` | Expenditure on natural gas, USD (C2) | USD | 264 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `expenditure_sum_major_fuels` | Expenditure on the major fuels together, USD (C2, million dollars times 1,000,000) | USD | 269 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |

### `eia_co2_state_annual`

One state's (or the nation's) energy-related carbon dioxide emissions of one sector and one fuel for one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 66144.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:co2-emissions/co2-emissions-aggregates U.S. Energy Information Administration, State Energy-Related Carbon Dioxide Emissions (API v2, route co2-emissions/co2-emissions-aggregates) (https://www.eia.gov/environment/emissions/state/)
- **Method note:** [`docs/methods/eia_co2_state_annual.md`](../methods/eia_co2_state_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). State Energy-Related Carbon Dioxide Emissions (API v2). Via the Energy Research Warehouse (ERW), table `eia_co2_state_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_co2:<state>:<sectorId>:<fuelId>; sectors CC, EC, IC, RC, TC and TT (all); fuels CO, NG, PE and TO (all) | none | text | for example eia_co2:AK:CC:CO, eia_co2:AK:CC:NG, eia_co2:AK:CC:PE; 1248 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1970-01-01T00:00:00Z to 2022-01-01T00:00:00Z; 53 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 5990393938.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | tCO2 | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 66144 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's names (state, sector, fuel) | none | text | for example Alabama, Commercial carbon dioxide emissions, All Fuels, Alabama, Commercial carbon dioxide emissions, Coal, Alabama, Commercial carbon dioxide emissions, Natural Gas; 1248 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:co2-emissions/co2-emissions-aggregates | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/co2-emissions/co2-emissions-aggregates/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&start=1970 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T21:47:54Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 66144 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `co2` | Energy-related carbon dioxide emissions of the sector and fuel, tonnes of CO2 (EIA's million metric tons times 1,000,000); a sum takes one level and leaves TT and TO out | tCO2 | 66144 | 1970-01-01T00:00:00Z | 2022-01-01T00:00:00Z |

### `eia_coal_delivered_price_annual`

One state's, census division's or the nation's yearly average delivered price of coal to one consuming sector.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3213.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:coal/consumption-and-quality U.S. Energy Information Administration, Quarterly Coal Report, consumption and quality (API v2, route coal/consumption-and-quality) (https://www.eia.gov/coal/production/quarterly/)
- **Method note:** [`docs/methods/eia_coal_prices.md`](../methods/eia_coal_prices.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Quarterly Coal Report, consumption and quality, delivered price (API v2). Via the Energy Research Warehouse (ERW), table `eia_coal_delivered_price_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_coal_delivered:<location>:<sector> | none | text | for example eia_coal_delivered:90:1, eia_coal_delivered:AK:1, eia_coal_delivered:AK:8; 228 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2000-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 26 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 227.42; 2228 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/short_ton | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> for a state; US for a census division or the U.S. | none | text | for example US, US-AK, US-AL; 50 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3213 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's names (location, sector) | none | text | for example Alabama, Electric Power, Alabama, Electric Utility, Alabama, Independent Power Producers; 228 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:coal/consumption-and-quality | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/coal/consumption-and-quality/data/?api_key=REDACTED&frequency=annual&data%5B%5D=price&start=2000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T22:17:07Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3213 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `price` | Average delivered price of coal to the sector, USD per short ton | USD/short_ton | 3213 | 2000-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `eia_coal_distribution_quarterly`

One quarter's domestic coal shipments of 2024 along one flow (origin, destination state, consuming sector, transport mode), from EIA's Annual Coal Distribution Report.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1207.

- **Time:** ts_utc is the first day of the quarter at 00:00:00Z (freq P3M).
- **Revisions:** Rewritten whole by each run (write_snapshot); vintage is the workbook's last-modified time.
- **Source:** eia:coal_distribution U.S. Energy Information Administration, Annual Coal Distribution Report (domestic distribution by origin and by destination state) (https://www.eia.gov/coal/distribution/annual/)
- **Method note:** [`docs/methods/eia_coal_distribution_quarterly.md`](../methods/eia_coal_distribution_quarterly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Annual Coal Distribution Report (domestic distribution by origin and destination state). Via the Energy Research Warehouse (ERW), table `eia_coal_distribution_quarterly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_coal_flow:<origin>:<destination>:<consumer type>:<mode> | none | text | for example eia_coal_flow:alabama:alabama:coke_plant:truck, eia_coal_flow:alabama:alabama:electric_power_sector:railroad, eia_coal_flow:alabama:alabama:industrial_plants_excluding_coke:railroad; 351 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2024-01-01T00:00:00Z, 2024-04-01T00:00:00Z, 2024-07-01T00:00:00Z, 2024-10-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.0 to 70447035.0; 1185 distinct | 0 |
| `unit` | The unit of the row's value | none | text | short_ton | 0 |
| `freq` | How long the interval of the row is | none | text | P3M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<destination state>, US for EIA's U.S. rows | none | text | for example US, US-AK, US-AL; 42 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1207 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <origin> to <destination>, consumer type, mode, in EIA's words | none | text | for example Alabama to Alabama, Coke Plant, Truck, Alabama to Alabama, Electric Power Sector, Railroad, Alabama to Alabama, Industrial Plants Excluding Coke, Railroad; 351 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:coal_distribution | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/coal/distribution/annual/xls/o_24state.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T12:47:50Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time from EIA's server | none | utc time | 2025-10-30T13:23:20Z | 0 |
| `x_origin` | The coal-origin state or region as EIA writes it (U.S. (All States) is EIA's total level) (the source's name: Origin State) | none | text | Alabama, Alaska, Colorado, Illinois, Indiana, Kentucky (East), Kentucky (West), Louisiana, Maryland, Mississippi, Missouri, Montana, New Mexico, North Dakota, Ohio, Pennsylvania (Anthracite), Pennsylvania (Bituminous), Texas, U.S. (All States), Utah, Virginia, West Virginia (Northern), West Virginia (Southern), Wyoming | 0 |
| `x_destination` | The destination state as EIA writes it | none | text | for example Alabama, Alaska, Arizona; 42 distinct | 0 |
| `x_consumer_type` | The consuming sector as EIA writes it (electric power, industrial plants excluding coke, coke plant, commercial and institutional) (the source's name: Consumer Type) | none | text | Coke Plant, Commercial/Institutional, Electric Power Sector, Industrial Plants Excluding Coke | 0 |
| `x_mode` | The transport mode as EIA writes it (railroad, river, truck and the others) (the source's name: Transportation Mode) | none | text | Railroad, River, Tidewater Piers, Tramway and Conveyor, Truck | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `shipments` | Coal shipped along the flow in the quarter, short tons | short_ton | 1207 | 2024-01-01T00:00:00Z | 2024-10-01T00:00:00Z |

### `eia_coal_mine_production_annual`

One coal mine's (by MSHA id, coal rank and mine type) yearly production or average employees, from EIA's Annual Coal Report.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 72852.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:coal/mine-production U.S. Energy Information Administration, Annual Coal Report, mine-level production (Form EIA-7A and MSHA Form 7000-2; API v2, route coal/mine-production) (https://www.eia.gov/coal/data.php)
- **Method note:** [`docs/methods/eia_coal_mine_production_annual.md`](../methods/eia_coal_mine_production_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Annual Coal Report, mine-level production (API v2). Via the Energy Research Warehouse (ERW), table `eia_coal_mine_production_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_coal_mine:<mineMSHAId>:<coalRankId>:<mineTypeId> | none | text | for example eia_coal_mine:100163:BIT:SUR, eia_coal_mine:100163:BIT:UND, eia_coal_mine:100329:PRP:SUR; more than 5000 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z, 2002-01-01T00:00:00Z, 2003-01-01T00:00:00Z, 2004-01-01T00:00:00Z, 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 117965515.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count, short_ton | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>; EIA's regions KYE, KYW, PAA, PAB, WVN and WVS put in their state | none | text | for example US-AK, US-AL, US-AR; 26 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 72852 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The mine's name | none | text | for example # 1, # 1 Loading Dock, # 1 Plant; more than 5000 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:coal/mine-production | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/coal/mine-production/data/?api_key=REDACTED&frequency=annual&data%5B%5D=production&data%5B%5D=average-employees&data%5B%5D=latitude&data%5B%5D=longitude&data%5B%5D=operating-company&data%5B%5D=refuse-flag&start=2001 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T00:35:18Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 72852 |
| `x_msha_id` | The mine's identifier at the Mine Safety and Health Administration (MSHA) (the source's name: mineMSHAId) | none | integer | 100163 to 5001977; 4665 distinct | 0 |
| `x_state` | EIA's state code of the mine, its regions (KYE, KYW, PAA, PAB, WVN, WVS) kept | none | text | for example AK, AL, AR; 29 distinct | 0 |
| `x_county` | The mine's county as EIA writes it (the source's name: mineCountyName) | none | text | for example Adair, Adams, Allegany; 229 distinct | 0 |
| `x_supply_region` | EIA's coal supply region of the mine (Powder River Basin, Appalachia Central and the others) (the source's name: supplyRegionDescription) | none | text | Appalachia Central, Appalachia Northern, Appalachia Southern, Illinois Basin, Other Interior, Other Western, Powder River Basin, Uinta Basin | 0 |
| `x_rank` | The coal rank (anthracite, bituminous, subbituminous, lignite) or Preparation Plant, as EIA writes it (the source's name: coalRankDescription) | none | text | Anthracite, Bituminous, Lignite, Preparation Plant, Subbituminous | 0 |
| `x_mine_type` | The mine type (surface, underground, refuse) (the source's name: mineTypeDescription) | none | text | Refuse, Surface, Underground | 0 |
| `x_status` | The mine's status as EIA writes it (Active, Temporarily closed, Permanently abandoned and the others) (the source's name: mineStatusDescription) | none | text | Active, Active, men not working, not producing, Active, men working, not producing, Mine closed by MSHA, New, under construction, Permanently abandoned, Temporarily closed | 0 |
| `x_operator` | The operating company, cut at 30 characters by EIA (the source's name: operating-company) | none | text | for example 101 Coal Inc., 101 Coal, Inc., 17 West Mining Inc; 4926 distinct | 0 |
| `x_latitude` | The mine's latitude as EIA gives it (the source's name: latitude) | degree | number | 28.683056 to 63.856944; 3402 distinct | 12817: EIA gives no latitude |
| `x_longitude` | The mine's longitude as EIA gives it (the source's name: longitude) | degree | number | -148.966111 to -5.4625; 3540 distinct | 12817: EIA gives no longitude |
| `x_refuse` | Yes for a refuse recovery operation (coal recovered from waste piles) (the source's name: refuse-flag) | none | text | Yes | 71778: EIA gives no refuse flag |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `employees` | The mine's average employees in the year, as EIA gives them | count | 35367 | 2001-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `production` | Coal produced by the mine in the year, short tons (a 0 EIA gives is kept) | short_ton | 37485 | 2001-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_coal_price_rank_annual`

One state's, region's or the nation's yearly average sales price of coal of one rank, from EIA's Annual Coal Report.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2843.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:coal/price-by-rank U.S. Energy Information Administration, Annual Coal Report, average sales price by rank (API v2, route coal/price-by-rank) (https://www.eia.gov/coal/annual/)
- **Method note:** [`docs/methods/eia_coal_prices.md`](../methods/eia_coal_prices.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Annual Coal Report, average sales price by rank (API v2). Via the Energy Research Warehouse (ERW), table `eia_coal_price_rank_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_coal_price_rank:<stateRegionId>:<coalRankId> | none | text | for example eia_coal_price_rank:AL:BIT, eia_coal_price_rank:AL:TOT, eia_coal_price_rank:APC:BIT; 128 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z, 2002-01-01T00:00:00Z, 2003-01-01T00:00:00Z, 2004-01-01T00:00:00Z, 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 5.68 to 269.0; 1521 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/short_ton | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> for a state; US for a region or the U.S. | none | text | US, US-AL, US-CO, US-IL, US-IN, US-KY, US-MD, US-MT, US-ND, US-NM, US-OH, US-OK, US-PA, US-TN, US-TX, US-UT, US-VA, US-WA, US-WV, US-WY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2843 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's area and rank names | none | text | for example Alabama, All, Alabama, Bituminous, Appalachia Central, All; 128 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:coal/price-by-rank | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/coal/price-by-rank/data/?api_key=REDACTED&frequency=annual&data%5B%5D=price&start=2001 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T23:48:37Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2843 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `price` | Average sales price of the coal, USD per short ton | USD/short_ton | 2843 | 2001-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_coal_prices_annual`

One producing state's, region's or the nation's yearly average sales price of coal in one market type, from EIA's Annual Coal Report.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2781.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:coal/market-sales-price U.S. Energy Information Administration, Annual Coal Report, average sales price (API v2, route coal/market-sales-price) (https://www.eia.gov/coal/annual/)
- **Method note:** [`docs/methods/eia_coal_prices.md`](../methods/eia_coal_prices.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Annual Coal Report, average sales price (API v2). Via the Energy Research Warehouse (ERW), table `eia_coal_prices_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_coal_price:<stateRegionId>:<marketTypeId> | none | text | for example eia_coal_price:AK:TOT, eia_coal_price:AL:OM, eia_coal_price:AL:TOT; 145 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z, 2002-01-01T00:00:00Z, 2003-01-01T00:00:00Z, 2004-01-01T00:00:00Z, 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 5.62 to 333.58; 2134 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/short_ton | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> for a state; US for a region or the U.S. | none | text | for example US, US-AK, US-AL; 26 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2781 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's area and market names | none | text | for example Alabama Open Market, Alabama Total, Alaska Total; 145 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:coal/market-sales-price | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/coal/market-sales-price/data/?api_key=REDACTED&frequency=annual&data%5B%5D=price&start=2001 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T20:21:08Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2781 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `price` | Average sales price of the coal, USD per short ton | USD/short_ton | 2781 | 2001-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_coal_production_annual`

One producing state's, region's or the nation's yearly coal production, number of mines or average employees, by coal rank and mine type, from EIA's Annual Coal Report.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 22630.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:coal/aggregate-production U.S. Energy Information Administration, Annual Coal Report, state aggregates (Form EIA-7A and MSHA Form 7000-2; API v2, route coal/aggregate-production) (https://www.eia.gov/coal/annual/)
- **Method note:** [`docs/methods/eia_coal_production_annual.md`](../methods/eia_coal_production_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Annual Coal Report, state aggregate production (API v2). Via the Energy Research Warehouse (ERW), table `eia_coal_production_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_coal_production:<stateRegionId>:<coalRankId>:<mineTypeId> | none | text | for example eia_coal_production:AK:SUB:ALL, eia_coal_production:AK:SUB:SUR, eia_coal_production:AK:TOT:ALL; 422 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z, 2002-01-01T00:00:00Z, 2003-01-01T00:00:00Z, 2004-01-01T00:00:00Z, 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 1171808669.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count, short_ton | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> for a state; US for a region or the U.S. | none | text | for example US, US-AK, US-AL; 27 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 22630 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's area, rank and mine type names | none | text | for example Alabama All All, Alabama All Surface, Alabama All Underground; 422 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:coal/aggregate-production | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/coal/aggregate-production/data/?api_key=REDACTED&frequency=annual&data%5B%5D=production&data%5B%5D=number-of-mines&data%5B%5D=average-employees&start=2001 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-22T10:51:47Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 22630 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `employees` | Average employees, as EIA gives them | count | 3808 | 2001-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `mines` | Number of mines | count | 9399 | 2001-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `production` | Coal produced, short tons | short_ton | 9423 | 2001-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_coal_receipts_annual`

One year's coal received at one power plant from one mine, by supplier, coal rank, contract type and transport mode, with its price and quality (Form EIA-923).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 270547.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:coal/shipments/receipts U.S. Energy Information Administration, coal receipts at power plants (Form EIA-923; API v2, route coal/shipments/receipts) (https://www.eia.gov/coal/data/browser/)
- **Method note:** [`docs/methods/eia_coal_receipts_annual.md`](../methods/eia_coal_receipts_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Coal receipts at power plants (Form EIA-923, API v2). Via the Energy Research Warehouse (ERW), table `eia_coal_receipts_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_coal_receipt:<mineMSHAId>:<plantId>:<supplier>:<coalRankId>:<contractType>:<transportationMode>; rank TOT is EIA's sum of the ranks beside it | none | text | for example eia_coal_receipt:100114:10675:ALPHA_COAL:BIT:Contract_Purchase:Tidewater_Piers, eia_coal_receipt:100114:10675:ALPHA_COAL:TOT:Contract_Purchase:Tidewater_Piers, eia_coal_receipt:100114:4143:TWENTY_MILE:BIT:Spot_Market_Purchase:Rail; more than 5000 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.07 to 10141666.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | Btu/lb, USD/short_ton, pct, short_ton | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<plant state> | none | text | for example US-AK, US-AL, US-AR; 47 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 270547 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <mine> to <plant> | none | text | for example # 1 (SIDNEY) to Indian River Generating Station, #1 (ALLIANCE  COAL) to Cross, #1 (ALLIANCE  COAL) to Harllee Branch; more than 5000 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:coal/shipments/receipts | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/coal/shipments/receipts/data/?api_key=REDACTED&frequency=annual&data%5B%5D=quantity&data%5B%5D=price&data%5B%5D=heat-content&data%5B%5D=sulfur-content&data%5B%5D=ash-content&start=2008 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T03:39:59Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 270547 |
| `x_msha_id` | The mine's identifier at the Mine Safety and Health Administration (MSHA) | none | integer | 100114 to 5000030; 1129 distinct | 0 |
| `x_mine_state` | The mine's state, EIA's code (the source's name: mineStateId) | none | text | for example AK, AL, AR; 28 distinct | 0 |
| `x_mine_county` | The mine's county as EIA writes it (the source's name: mineCountyName) | none | text | for example Allegany, Anderson, Atascosa; 114 distinct | 99965: EIA gives no county |
| `x_mine_basin` | The mine's coal basin as EIA writes it (Powder River Basin, Illinois Basin and the others) (the source's name: mineBasinDescription) | none | text | Appalachia Central, Appalachia Northern, Appalachia Southern, Illinois Basin, Other Interior, Other Western, Powder River Basin, Uinta Basin | 0 |
| `x_mine_type` | The mine type (surface or underground) (the source's name: mineTypeDescription) | none | text | Surface, Underground | 0 |
| `x_plant_id` | EIA's plant code of the receiving power plant, as in eia860_plants_annual | none | integer | 3 to 56848; 471 distinct | 0 |
| `x_plant_state` | The receiving plant's state | none | text | for example AK, AL, AR; 47 distinct | 0 |
| `x_supplier` | The coal supplier as EIA writes it | none | text | for example 101 COAL,INC., 1081 MINE, 1202215; 1205 distinct | 0 |
| `x_rank` | The coal rank as EIA writes it (All is EIA's sum of the ranks; leave it out of a sum over ranks) (the source's name: coalRankDescription) | none | text | All, Anthracite, Bituminous, Lignite, Subbituminous, Waste Coal | 0 |
| `x_contract_type` | The purchase type (contract, new contract, spot-market purchase) | none | text | Contract Purchase, New Contract, Spot-Market Purchase | 750: EIA gives no contract type |
| `x_transport_mode` | The mode the coal was carried in (rail, river, truck and the others) | none | text | Great Lakes, Pipeline, Rail, River, Tidewater Piers, Tramway/Conveyor, Truck, Water | 8: EIA gives no transport mode |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `ash_content` | Ash content of the coal, percent by weight | pct | 56858 | 2008-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `heat_content` | Heat content of the coal, Btu per pound | Btu/lb | 56858 | 2008-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `price` | Price of the coal received, USD per short ton | USD/short_ton | 43115 | 2008-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `quantity` | Coal received, short tons | short_ton | 56858 | 2008-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `sulfur_content` | Sulfur content of the coal, percent by weight | pct | 56858 | 2008-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `eia_coal_trade_price_annual`

One year's average price of U.S. coal exports or imports of one rank with one country through one customs district, from EIA's Quarterly Coal Report.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 24623.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:coal/exports-imports-quantity-price U.S. Energy Information Administration, Quarterly Coal Report, exports and imports (API v2, route coal/exports-imports-quantity-price) (https://www.eia.gov/coal/production/quarterly/)
- **Method note:** [`docs/methods/eia_coal_prices.md`](../methods/eia_coal_prices.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Quarterly Coal Report, exports and imports (API v2). Via the Energy Research Warehouse (ERW), table `eia_coal_trade_price_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_coal_trade:<exportImportType>:<coalRankId>:<countryId>:<customsDistrictId> | none | text | for example eia_coal_trade:Exports:COK:AE:BA_MD, eia_coal_trade:Exports:COK:AE:HG_TX, eia_coal_trade:Exports:COK:AE:LA_CA; 3460 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2000-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 26 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 7.92 to 9546.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/short_ton | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 24623 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's names (exports or imports, country, rank, customs district) | none | text | for example Exports, Afghanistan, All, Seattle, WA, Exports, Afghanistan, All, Total, Exports, Afghanistan, Steam Coal, Seattle, WA; 3460 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:coal/exports-imports-quantity-price | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/coal/exports-imports-quantity-price/data/?api_key=REDACTED&frequency=annual&data%5B%5D=price&start=2000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T23:48:44Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 24623 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `price` | Average price of the coal exported or imported, USD per short ton | USD/short_ton | 24623 | 2000-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `eia_county_region`

One county of the lower 48 states and the District of Columbia, with the balancing authority (grid operator area) and EIA region it is assigned to by the ERW's rule from EIA-861.

Shape: entities. Keys: `entity_id`. License: public; tier: derived. Rows read on 2026-11-20: 3117.

- **Time:** No time column. vintage names the EIA-861 data year (2025); the table is a snapshot as built on its retrieved_at.
- **Revisions:** Rewritten whole by each run of the builder (write_snapshot); vintage holds the EIA-861 data year used.
- **Source:** erw:eia_county_region the ERW's county to balancing authority rule (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/county_population_and_regions.md)
- **Method note:** [`docs/methods/county_population_and_regions.md`](../methods/county_population_and_regions.md)
- **Cite as:** Energy Research Warehouse (from EIA-861, EIA-930 and Census Bureau data). County to balancing authority and EIA region. Via the Energy Research Warehouse (ERW), table `eia_county_region`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: census:county:<five-digit FIPS code> | none | text | for example census:county:01001, census:county:01003, census:county:01005; 3117 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: county on every row | none | text | county | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The Census Bureau's county name (the newest it prints) | none | text | for example Abbeville County, Acadia Parish, Accomack County; 1852 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> of the county | none | text | for example US-AL, US-AR, US-AZ; 49 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 3117 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 3117 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 3117 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3117 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 3117 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 3117 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:eia_county_region | 0 |
| `source_url` | The address of the exact document the row was read from. Here: The ERW method note of the rule, since the table is derived | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/county_population_and_regions.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-18T01:27:47Z, 2026-11-18T01:27:48Z, 2026-11-18T01:27:49Z, 2026-11-18T01:27:50Z, 2026-11-18T01:27:51Z, 2026-11-18T01:27:52Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Text naming the EIA-861 data year (EIA-861 2025), not a UTC time | none | text | EIA-861 2025 | 0 |
| `x_state` | The county's state, two-letter postal code | none | text | for example AL, AR, AZ; 49 distinct | 0 |
| `x_fips` | The county's five-digit FIPS code (state and county), the Census Bureau's | none | integer | 1001 to 56045; 3117 distinct | 0 |
| `x_ba_primary` | The county's primary balancing authority, EIA-930 code: the one whose serving utilities have the most retail customers in the state | none | text | for example AECI, AVA, AZPS; 37 distinct | 24: No balancing authority: EIA-861 lists no utility for the county, or its utilities name none (x_basis says which) |
| `x_region` | The primary balancing authority's EIA-930 region (CAL, TEX, MIDW and the others), from the newest EIA-930 BALANCE file (the source's name: Region) | none | text | CAL, CAR, CENT, FLA, MIDA, MIDW, NE, NW, NY, SE, SW, TEN, TEX | 64: No primary balancing authority, or the newest EIA-930 BALANCE file gives it no region |
| `x_shared` | Y when EIA-861 lists utilities of more than one balancing authority in the county, else N | none | text | N, Y | 0 |
| `x_bas` | Every balancing authority listed in the county, each with its serving utilities' retail customers in the state and how many utilities, separated by semicolons, primary first | none | text | for example AECI (104,240 customers, 3 utilities), AECI (111,764 customers, 4 utilities), AECI (124,585 customers, 4 utilities); 2115 distinct | 24: No balancing authority (see x_basis) |
| `x_regions` | The EIA-930 regions of every listed balancing authority, separated by semicolons | none | text | for example CAL, CAL;NW, CAL;NW;SW; 37 distinct | 53: No balancing authority, or none of the listed ones has a region in the BALANCE file |
| `x_ba_by_count` | The balancing authority with the most serving utilities in the county (the other rule, kept for a reader who prefers it) | none | text | for example AECI, AVA, AZPS; 40 distinct | 24: No balancing authority (see x_basis) |
| `x_utilities` | EIA-861 utility numbers of every utility EIA lists as serving the county, separated by semicolons | none | text | for example 10000;10005;15336;16854;1726, 10000;10005;16854;22500;2551, 10000;10005;16854;2270; 2624 distinct | 12: EIA-861 lists no utility for the county |
| `x_basis` | How the county's balancing authority was decided (one, shared with the primary by customers, or why there is none) | none | text | its utilities name no balancing authority in EIA-861's sales file, no utility listed by EIA-861 for this county, one balancing authority, shared: primary by the serving utilities' customers in the state | 0 |

### `eia_crude_first_purchase_prices`

One crude stream's or state's monthly average first purchase price (the price paid at the lease, as crude is first bought) as EIA reports it.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2632.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Each run asks for the full history and merges it on (entity, variable, ts_utc), keeping EIA's newest value; a row EIA stops giving is kept from an earlier run. vintage is not filled.
- **Source:** eia:petroleum/pri/dfp2 Domestic Crude Oil First Purchase Prices (by stream; by area) (https://www.eia.gov/dnav/pet/pet_pri_dfp2_k_m.htm)
- **Source:** eia:petroleum/pri/dfp1 Domestic Crude Oil First Purchase Prices (by stream; by area) (https://www.eia.gov/dnav/pet/pet_pri_dfp2_k_m.htm)
- **Method note:** [`docs/methods/eia_crude_first_purchase_prices.md`](../methods/eia_crude_first_purchase_prices.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Domestic Crude Oil First Purchase Prices (by stream; by area). Via the Energy Research Warehouse (ERW), table `eia_crude_first_purchase_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:<EIA series id> (F003075793 Mars Blend; F002038__3 North Dakota; F003048__3 Texas; F003022__3 Louisiana; F003035__3 New Mexico) | none | text | eia:F002038__3, eia:F003022__3, eia:F003035__3, eia:F003048__3, eia:F003075793 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1977-07-01T00:00:00Z to 2026-08-01T00:00:00Z; 590 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 7.95 to 133.74; 2188 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/bbl | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, the state series included | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2632 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: EIA's series names are in the header's Series line | none | empty | no cell holds a value | 2632 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/pri/dfp1, eia:petroleum/pri/dfp2 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/pri/dfp1/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000&facets%5Bseries%5D%5B%5D=F002038__3&facets%5Bseries%5D%5B%5D=F003048__3&facets%5Bseries%5D%5B%5D=F003022__3&facets%5Bseries%5D%5B%5D=F003035__3, https://api.eia.gov/v2/petroleum/pri/dfp2/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000&facets%5Bseries%5D%5B%5D=F003075793 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T14:04:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2632 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `first_purchase_price` | Crude oil first purchase price, the month's average, US dollars a barrel | USD/bbl | 2632 | 1977-07-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `eia_crude_imports_by_country`

One month's U.S. crude oil imports from one country of origin (or in all), as EIA reports them.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 22657.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Each run asks for the full history and merges it on (entity, variable, ts_utc), keeping EIA's newest value; a row EIA stops giving is kept. The copy held was rebuilt from the ERW archive by restore_tables.py. vintage is not filled.
- **Source:** eia:petroleum/move/impcus U.S. Imports by Country of Origin (crude oil) (https://www.eia.gov/dnav/pet/pet_move_impcus_a2_nus_ep00_im0_mbbl_m.htm)
- **Method note:** [`docs/methods/eia_crude_imports_by_country.md`](../methods/eia_crude_imports_by_country.md)
- **Cite as:** U.S. Energy Information Administration (EIA). U.S. Imports by Country of Origin (crude oil). Via the Energy Research Warehouse (ERW), table `eia_crude_imports_by_country`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:<EIA series id> | none | text | for example eia:ESM_EPC0_IM0_NUS-NSS_MBBLD, eia:MCRIMGB2, eia:MCRIMIT2; 82 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1920-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 1280 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 10765.0; 3340 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl/d | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 22657 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: EIA's series names are in the header's Series line | none | empty | no cell holds a value | 22657 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/move/impcus | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/move/impcus/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000&facets%5Bproduct%5D%5B%5D=EPC0&facets%5Bprocess%5D%5B%5D=IM0, https://api.eia.gov/v2/petroleum/move/impcus/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=10000&length=5000&facets%5Bproduct%5D%5B%5D=EPC0&facets%5Bprocess%5D%5B%5D=IM0, https://api.eia.gov/v2/petroleum/move/impcus/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=15000&length=5000&facets%5Bproduct%5D%5B%5D=EPC0&facets%5Bprocess%5D%5B%5D=IM0, https://api.eia.gov/v2/petroleum/move/impcus/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=20000&length=5000&facets%5Bproduct%5D%5B%5D=EPC0&facets%5Bprocess%5D%5B%5D=IM0, https://api.eia.gov/v2/petroleum/move/impcus/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=25000&length=5000&facets%5Bproduct%5D%5B%5D=EPC0&facets%5Bprocess%5D%5B%5D=IM0, https://api.eia.gov/v2/petroleum/move/impcus/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=30000&length=5000&facets%5Bproduct%5D%5B%5D=EPC0&facets%5Bprocess%5D%5B%5D=IM0, https://api.eia.gov/v2/petroleum/move/impcus/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=35000&length=5000&facets%5Bproduct%5D%5B%5D=EPC0&facets%5Bprocess%5D%5B%5D=IM0, https://api.eia.gov/v2/petroleum/move/impcus/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=5000&length=5000&facets%5Bproduct%5D%5B%5D=EPC0&facets%5Bprocess%5D%5B%5D=IM0 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-29T00:59:35Z, 2026-09-29T00:59:37Z, 2026-09-29T00:59:39Z, 2026-09-29T00:59:41Z, 2026-09-29T00:59:43Z, 2026-09-29T00:59:45Z, 2026-09-29T00:59:47Z, 2026-09-29T00:59:48Z, 2026-09-30T19:21:27Z, 2026-11-05T23:10:41Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 22657 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `imports` | U.S. crude oil imports from the country the series names, thousand barrels a day | kbbl/d | 22657 | 1920-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `eia_crude_imports_detail_monthly`

One month's crude oil imports from one country of origin to one destination (refinery, state, PADD or the U.S.) of one grade, from EIA's company level imports (Form EIA-814).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 183393.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:crude-oil-imports U.S. Energy Information Administration, Company Level Imports, crude oil imports by country to destination (API v2, route crude-oil-imports, Form EIA-814) (https://www.eia.gov/petroleum/imports/companylevel/)
- **Method note:** [`docs/methods/eia_crude_imports_detail_monthly.md`](../methods/eia_crude_imports_detail_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Company Level Imports, crude oil imports by country to destination (API v2, Form EIA-814). Via the Energy Research Warehouse (ERW), table `eia_crude_imports_detail_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_crude_imports:<originId>:<destinationId>:<gradeId>; destinations nest, so a sum takes one destination type | none | text | for example eia_crude_imports:CTY_AE:PP_3:HSO, eia_crude_imports:CTY_AE:PP_3:LSO, eia_crude_imports:CTY_AE:PP_3:MED; more than 5000 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2009-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 211 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.0 to 101161.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 183393 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The origin, destination (with its type) and grade in EIA's names | none | text | for example Albania to CPI OPERATIONS LLC / PAULSBORO / NJ (Refinery), Heavy Sour, Albania to New Jersey (Port State), Heavy Sour, Albania to New Jersey (Refinery State), Heavy Sour; more than 5000 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:crude-oil-imports | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/crude-oil-imports/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=quantity&facets%5BoriginType%5D%5B%5D=CTY&start=2009-01&end=2010-12, https://api.eia.gov/v2/crude-oil-imports/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=quantity&facets%5BoriginType%5D%5B%5D=CTY&start=2011-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-22T06:54:47Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 183393 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `imports` | Crude oil imported in the month along the origin, destination and grade, thousand barrels | kbbl | 183393 | 2009-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_crude_production_state_monthly`

One month's crude oil field production of one state, region or federal offshore area, in the month or per day.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 25644.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/crd/crpdn U.S. Energy Information Administration, Petroleum Supply Monthly, crude oil field production (API v2, route petroleum/crd/crpdn) (https://www.eia.gov/petroleum/supply/monthly/)
- **Method note:** [`docs/methods/eia_crude_production_state_monthly.md`](../methods/eia_crude_production_state_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Petroleum Supply Monthly, crude oil field production (API v2). Via the Energy Research Warehouse (ERW), table `eia_crude_production_state_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_crude_production:<area>:<series stem>; regions R10 to R50 are sums of states and offshore areas | none | text | for example eia_crude_production:NUS:MCRFPUS, eia_crude_production:R10:MCRFPP1, eia_crude_production:R20:MCRFPP2; 43 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 307 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 433840.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl, kbbl/d | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> for a state; US for the U.S., the regions and the offshore areas | none | text | for example US, US-AK, US-AL; 33 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 25644 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name | none | text | for example Alabama Field Production of Crude Oil (Thousand Barrels per Day), Alabama Field Production of Crude Oil (Thousand Barrels), Alaska Field Production of Crude Oil (Thousand Barrels per Day); 84 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/crd/crpdn | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=FPF&start=2001-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T21:14:11Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 25644 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `field_production` | Crude oil field production in the month, thousand barrels | kbbl | 12822 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `field_production_per_day` | Crude oil field production, thousand barrels a day | kbbl/d | 12822 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_crude_quality_monthly`

One month's average API gravity or sulfur content of the crude oil run at refineries in the U.S., one PADD or one refining district.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 15968.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/pnp/crq U.S. Energy Information Administration, Petroleum Supply Monthly, crude oil input qualities (API v2, route petroleum/pnp/crq) (https://api.eia.gov/v2/petroleum/pnp/crq/)
- **Method note:** [`docs/methods/eia_crude_quality_monthly.md`](../methods/eia_crude_quality_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Petroleum Supply Monthly, crude oil input qualities (API v2). Via the Energy Research Warehouse (ERW), table `eia_crude_quality_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_crude_quality:<EIA series id> | none | text | for example eia_crude_quality:MCRAP2A2, eia_crude_quality:MCRAP2B2, eia_crude_quality:MCRAP2C2; 32 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1985-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 499 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.1 to 42.44; 1714 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degAPI, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 15968 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series description (the area) | none | text | for example Appalachian No. 1 Refinery District API Gravity (Weighted Average) of Crude Oil Input to Refineries (Degrees), Appalachian No. 1 Refinery District Sulfur Content (Weighted Average) of Crude Oil Input to Refineries (Percent), East Coast (PADD 1) API Gravity (Weighted Average) of Crude Oil Input to Refineries (Degrees); 32 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/pnp/crq | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/pnp/crq/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=YCG&facets%5Bprocess%5D%5B%5D=YCS&start=1985-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T03:39:07Z, 2026-10-24T03:39:11Z, 2026-10-24T03:39:15Z, 2026-10-24T03:39:18Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 15968 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `api_gravity` | Weighted average API gravity of crude input (a measure of how light the crude is, higher is lighter), degrees API; not additive across areas | degAPI | 7984 | 1985-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `sulfur_content` | Weighted average sulfur content of crude input, percent by weight; not additive across areas | pct | 7984 | 1985-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_crude_reserves_annual`

One state's, area's or the nation's crude oil proved reserves at a year's end, or one of the changes that take one year's reserves to the next.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 13931.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y); reserves are as of the year's end.
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/crd/pres U.S. Energy Information Administration, U.S. Crude Oil and Natural Gas Proved Reserves (API v2, route petroleum/crd/pres) (https://www.eia.gov/naturalgas/crudeoilreserves/)
- **Method note:** [`docs/methods/eia_crude_reserves_annual.md`](../methods/eia_crude_reserves_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). U.S. Crude Oil and Natural Gas Proved Reserves, crude oil (API v2). Via the Energy Research Warehouse (ERW), table `eia_crude_reserves_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_crude_reserves:<process>:<area>; parts of states and the Lower 48 repeat states and the U.S. | none | text | for example eia_crude_reserves:R01:NUS, eia_crude_reserves:R01:R1901F, eia_crude_reserves:R01:R44F; 416 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1977-01-01T00:00:00Z to 2021-01-01T00:00:00Z; 45 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1073000.0 to 44191000.0; 1719 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> for a state, US otherwise | none | text | US, US-AK, US-AL, US-AR, US-CA, US-CO, US-FL, US-IL, US-IN, US-KS, US-KY, US-LA, US-MI, US-MS, US-MT, US-ND, US-NE, US-NM, US-OH, US-OK, US-PA, US-TX, US-UT, US-WV, US-WY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 13931 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name | none | text | for example Alabama Crude Oil Estimated Production from Reserves (Million Barrels), Alabama Crude Oil Proved Reserves (Million Barrels), Alabama Crude Oil Reserves Acquisitions (Million Barrels); 416 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/crd/pres | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/crd/pres/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=R01&facets%5Bprocess%5D%5B%5D=R02&facets%5Bprocess%5D%5B%5D=R03&facets%5Bprocess%5D%5B%5D=R04&facets%5Bprocess%5D%5B%5D=R05&facets%5Bprocess%5D%5B%5D=R06&facets%5Bprocess%5D%5B%5D=R07A&facets%5Bprocess%5D%5B%5D=R10&start=1977 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T22:16:51Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 13931 |

Variables (8):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `acquisitions` | Proved reserves acquired (R06), thousand barrels | kbbl | 1131 | 2000-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `adjustments` | Adjustments to proved reserves (R02), thousand barrels | kbbl | 2274 | 1977-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `extensions_and_discoveries` | Extensions and discoveries of proved reserves (R07A), thousand barrels | kbbl | 299 | 2016-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `production` | Estimated production from reserves in the year (R10), thousand barrels | kbbl | 2274 | 1977-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `proved_reserves` | Crude oil proved reserves at the year's end (R01), thousand barrels (EIA's million barrels times 1,000) | kbbl | 2274 | 1977-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `revision_decreases` | Revision decreases of proved reserves (R04), thousand barrels | kbbl | 2274 | 1977-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `revision_increases` | Revision increases of proved reserves (R03), thousand barrels | kbbl | 2274 | 1977-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `sales` | Proved reserves sold (R05), thousand barrels | kbbl | 1131 | 2000-01-01T00:00:00Z | 2021-01-01T00:00:00Z |

### `eia_crude_stream_prices`

One crude stream's or area's monthly average price, as one of four EIA measures (first purchase price, landed cost or F.O.B. cost of imports, refiners' acquisition cost).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3013.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M); the header's words on a survey Monday do not concern this table.
- **Revisions:** Rewritten whole by each run (the file is deleted and the history from January 2019 written again), so EIA's revisions are taken; the copy held was rebuilt from the ERW archive by restore_tables.py. vintage is not filled.
- **Source:** eia:petroleum/pri/dfp2:streams EIA, Domestic Crude Oil First Purchase Prices for Selected Crude Streams (https://www.eia.gov/dnav/pet/pet_pri_dfp2_k_m.htm)
- **Source:** eia:petroleum/pri/land2 EIA, Landed Costs of Imported Crude for Selected Crude Streams (https://www.eia.gov/dnav/pet/pet_pri_land2_k_m.htm)
- **Source:** eia:petroleum/pri/imc2 EIA, F.O.B. Costs of Imported Crude Oil for Selected Crude Streams (https://www.eia.gov/dnav/pet/pet_pri_imc2_k_m.htm)
- **Source:** eia:petroleum/pri/rac2 EIA, Refiner Acquisition Cost of Crude Oil (https://www.eia.gov/dnav/pet/pet_pri_rac2_dcu_nus_m.htm)
- **Method note:** [`docs/methods/eia_crude_stream_prices.md`](../methods/eia_crude_stream_prices.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Domestic Crude Oil First Purchase Prices for Selected Crude Streams; F.O.B. Costs of Imported Crude Oil for Selected Crude Streams; Landed Costs of Imported Crude for Selected Crude Streams; Refiner Acquisition Cost of Crude Oil. Via the Energy Research Warehouse (ERW), table `eia_crude_stream_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:<EIA series id> | none | text | for example eia:F003048623, eia:F003048633, eia:F003075773; 41 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-09-01T00:00:00Z; 93 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 9.34 to 121.23; 2380 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/bbl | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: The state for a domestic stream, US for the three U.S. refiner series; empty for an import stream and for a PADD | none | text | US, US-AK, US-CA, US-LA, US-TX, US-WY | 1999 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3013 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The stream or area, from EIA's description | none | text | for example Alaska North Slope, Algerian Saharan Blend, California Kern River; 38 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/pri/dfp2:streams, eia:petroleum/pri/imc2, eia:petroleum/pri/land2, eia:petroleum/pri/rac2 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/pri/dfp2/data/?frequency=monthly&data%5B0%5D=value&start=2019-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000, https://api.eia.gov/v2/petroleum/pri/imc2/data/?frequency=monthly&data%5B0%5D=value&start=2019-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000, https://api.eia.gov/v2/petroleum/pri/land2/data/?frequency=monthly&data%5B0%5D=value&start=2019-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000, https://api.eia.gov/v2/petroleum/pri/rac2/data/?frequency=monthly&data%5B0%5D=value&start=2019-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T08:18:30Z, 2026-11-05T23:50:13Z, 2026-11-05T23:50:14Z, 2026-11-05T23:50:15Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3013 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `first_purchase_price` | Domestic crude stream's first purchase price, the month's average, USD a barrel | USD/bbl | 735 | 2019-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `fob_cost` | F.O.B. cost of an imported crude stream (its cost at the loading port, before transport), the month's average, USD a barrel | USD/bbl | 147 | 2019-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `landed_cost` | Landed cost of an imported crude stream (its cost delivered to the U.S.), the month's average, USD a barrel | USD/bbl | 472 | 2019-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `refiner_acquisition_cost` | Refiners' acquisition cost of crude (composite, domestic or imported), for the U.S. or a PADD, USD a barrel | USD/bbl | 1659 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `eia_crude_tank_farm_stocks_monthly`

One month's end crude oil stocks at tank farms and pipelines in the U.S. or one PADD, or ending stocks at Cushing, Oklahoma.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3553.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M); a month-end stock.
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/stoc/cu U.S. Energy Information Administration, Petroleum Supply Monthly, crude oil stocks at tank farms and pipelines (API v2, route petroleum/stoc/cu) (https://api.eia.gov/v2/petroleum/stoc/cu/)
- **Method note:** [`docs/methods/eia_crude_tank_farm_stocks_monthly.md`](../methods/eia_crude_tank_farm_stocks_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Petroleum Supply Monthly, crude oil stocks at tank farms and pipelines (API v2). Via the Energy Research Warehouse (ERW), table `eia_crude_tank_farm_stocks_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_crude_tank_farm_stocks:<EIA series id> | none | text | eia_crude_tank_farm_stocks:MCRSFP11, eia_crude_tank_farm_stocks:MCRSFP21, eia_crude_tank_farm_stocks:MCRSFP31, eia_crude_tank_farm_stocks:MCRSFP41, eia_crude_tank_farm_stocks:MCRSFP51, eia_crude_tank_farm_stocks:MCRSFUS1, eia_crude_tank_farm_stocks:MCRST_YCUOK_1 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1981-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 547 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 533.0 to 432034.0; 3426 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-OK for Cushing, US otherwise (the PADDs included) | none | text | US, US-OK | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3553 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series description | none | text | Cushing, OK Ending Stocks of Crude Oil (Thousand Barrels), East Coast (PADD 1) Crude Oil Stocks at Tank Farms and Pipelines (Thousand Barrels), Gulf Coast (PADD 3) Crude Oil Stocks at Tank Farms and Pipelines (Thousand Barrels), Midwest (PADD 2) Crude Oil Stocks at Tank Farms and Pipelines (Thousand Barrels), Rocky Mountain (PADD 4) Crude Oil Stocks at Tank Farms and Pipelines (Thousand Barrels), U.S. Crude Oil Stocks at Tank Farms and Pipelines (Thousand Barrels), West Coast (PADD 5) Crude Oil Stocks at Tank Farms and Pipelines (Thousand Barrels) | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/stoc/cu | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/stoc/cu/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=STT&facets%5Bprocess%5D%5B%5D=SAE&start=1981-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T05:21:28Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3553 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `ending_stocks` | Cushing, Oklahoma ending stocks of crude oil at the month's end, thousand barrels | kbbl | 271 | 2004-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `tank_farm_pipeline_stocks` | Crude oil stocks at tank farms and pipelines at the month's end, thousand barrels | kbbl | 3282 | 1981-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_drilling_monthly`

One month's count of rotary rigs (crude oil, natural gas or both; U.S., onshore or offshore) or active well service rigs in operation.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3431.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/crd/drill U.S. Energy Information Administration, crude oil and natural gas drilling activity (API v2, route petroleum/crd/drill) (https://www.eia.gov/dnav/pet/pet_crd_drill_s1_m.htm)
- **Method note:** [`docs/methods/eia_drilling_monthly.md`](../methods/eia_drilling_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Crude oil and natural gas drilling activity (API v2). Via the Energy Research Warehouse (ERW), table `eia_drilling_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_drilling:<EIA series id> | none | text | eia_drilling:E_ERTRR0_XR0_NUS_C, eia_drilling:E_ERTRR0_XR0_RUSOF_C, eia_drilling:E_ERTRR0_XR0_RUSON_C, eia_drilling:E_ERTRRG_XR0_NUS_C, eia_drilling:E_ERTRRO_XR0_NUS_C, eia_drilling:E_ERTS0_XRS_NUS_C | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1973-01-01T00:00:00Z to 2026-02-01T00:00:00Z; 638 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 6.0 to 5367.0; 1838 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3431 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name | none | text | U.S. Crude Oil Rotary Rigs in Operation (Count), U.S. Crude Oil and Natural Gas Active Well Service Rigs in operation (Count), U.S. Crude Oil and Natural Gas Rotary Rigs in Operation (Count), U.S. Natural Gas Rotary Rigs in Operation (Count), U.S. Offshore Crude Oil and Natural Gas Rotary Rigs in Operation (Count), U.S. Onshore Crude Oil and Natural Gas Rotary Rigs in Operation (Count) | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/crd/drill | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/crd/drill/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=XR0&facets%5Bprocess%5D%5B%5D=XRS&start=1973-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-22T00:37:00Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3431 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `rotary_rigs` | Rotary rigs in operation (the rigs that drill wells), count | count | 2840 | 1973-01-01T00:00:00Z | 2026-02-01T00:00:00Z |
| `service_rigs` | Active well service rigs in operation, count | count | 591 | 1973-01-01T00:00:00Z | 2022-03-01T00:00:00Z |

### `eia_energy_efficiency_state_annual`

One state's (or the nation's) yearly savings or costs of utilities' energy efficiency programs in one sector, for one of EIA's time periods (reporting year or expected life cycle).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 19740.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:electricity/state-electricity-profiles/energy-efficiency U.S. Energy Information Administration, State Electricity Profiles, energy efficiency (API v2, route electricity/state-electricity-profiles/energy-efficiency) (https://www.eia.gov/electricity/state/)
- **Method note:** [`docs/methods/eia_energy_efficiency_state_annual.md`](../methods/eia_energy_efficiency_state_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). State Electricity Profiles, energy efficiency (API v2). Via the Energy Research Warehouse (ERW), table `eia_energy_efficiency_state_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_efficiency:<state>:<time period slug>:<sector>; time period reporting_year or expected_life_cycle_of_programs; sectors RES, COM, IND, TRN, TOT | none | text | for example eia_efficiency:AK:expected_life_cycle_of_programs:COM, eia_efficiency:AK:expected_life_cycle_of_programs:IND, eia_efficiency:AK:expected_life_cycle_of_programs:RES; 520 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 17254851000.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 19740 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's names of state, time period and sector | none | text | for example Alabama, Expected Life Cycle of Programs, all sectors, Alabama, Expected Life Cycle of Programs, commercial, Alabama, Expected Life Cycle of Programs, industrial; 520 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:electricity/state-electricity-profiles/energy-efficiency | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/electricity/state-electricity-profiles/energy-efficiency/data/?api_key=REDACTED&frequency=annual&data%5B%5D=energy-savings&data%5B%5D=potential-peak-savings&data%5B%5D=customer-incentive&data%5B%5D=all-other-costs&start=2013 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T23:25:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 19740 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `all_other_costs` | All other costs of the programs, USD (EIA's thousand dollars times 1,000) | USD | 4935 | 2013-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `customer_incentive` | Cost of the incentives paid to customers, USD (EIA's thousand dollars times 1,000) | USD | 4935 | 2013-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `energy_savings` | Energy saved by the programs, MWh | MWh | 4935 | 2013-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `potential_peak_savings` | Potential reduction of peak demand by the programs, MW | MW | 4935 | 2013-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_fuel_spot_prices`

One trading day's spot price of Henry Hub natural gas, WTI Cushing crude or Brent crude, as EIA reports it.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 27814.

- **Time:** ts_utc is the trading date at 00:00:00Z (freq P1D), a date, not an instant; trading days only.
- **Revisions:** Each run asks for the whole daily history and merges it on (entity, variable, ts_utc); a revised value replaces the old, a row EIA stops giving stays. The copy held was rebuilt from the ERW archive by restore_tables.py. vintage is not filled.
- **Source:** eia:natural-gas/pri/fut Natural Gas Spot and Futures Prices (NYMEX), daily (https://www.eia.gov/dnav/ng/ng_pri_fut_s1_d.htm)
- **Source:** eia:petroleum/pri/spt Spot Prices for Crude Oil and Petroleum Products, daily (https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm)
- **Method note:** [`docs/methods/eia_fuel_spot_prices.md`](../methods/eia_fuel_spot_prices.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural Gas Spot and Futures Prices (NYMEX), daily; Spot Prices for Crude Oil and Petroleum Products, daily. Via the Energy Research Warehouse (ERW), table `eia_fuel_spot_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:henry_hub (RNGWHHD), eia:wti_cushing (RWTC) or eia:brent (RBRTE) | none | text | eia:brent, eia:henry_hub, eia:wti_cushing | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1986-01-02T00:00:00Z to 2026-11-11T00:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -36.98 to 145.31; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MMBtu, USD/bbl | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-LA for Henry Hub, US-OK for WTI Cushing, empty for Brent (not a U.S. place) | none | text | US-LA, US-OK | 10019 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 27814 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 27814 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/pri/fut, eia:petroleum/pri/spt | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/pri/fut/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&facets%5Bseries%5D%5B%5D=RNGWHHD&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&offset=0&length=5000, https://api.eia.gov/v2/natural-gas/pri/fut/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&facets%5Bseries%5D%5B%5D=RNGWHHD&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&offset=5000&length=5000, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&facets%5Bseries%5D%5B%5D=RBRTE&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&offset=0&length=5000, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&facets%5Bseries%5D%5B%5D=RBRTE&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&offset=10000&length=5000, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&facets%5Bseries%5D%5B%5D=RBRTE&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&offset=5000&length=5000, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&facets%5Bseries%5D%5B%5D=RWTC&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&offset=0&length=5000, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&facets%5Bseries%5D%5B%5D=RWTC&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&offset=10000&length=5000, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&facets%5Bseries%5D%5B%5D=RWTC&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&offset=5000&length=5000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-29T00:58:50Z to 2026-11-12T21:47:21Z; 29 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 27814 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `spot_price` | The day's spot price: USD per MMBtu for Henry Hub, USD a barrel for WTI and Brent (the unit column says which); negative values are real | USD/MMBtu; USD/bbl | 27814 | 1986-01-02T00:00:00Z | 2026-11-11T00:00:00Z |

### `eia_gas_balance_annual`

One state's (or the nation's or the federal Gulf's) yearly natural gas supply or disposition figure for one process, from EIA's Natural Gas Annual.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 11274.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:natural-gas/sum/snd U.S. Energy Information Administration, Natural Gas Annual, supply and disposition (API v2, route natural-gas/sum/snd) (https://www.eia.gov/naturalgas/annual/)
- **Method note:** [`docs/methods/eia_gas_balance_annual.md`](../methods/eia_gas_balance_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural Gas Annual, supply and disposition (API v2). Via the Energy Research Warehouse (ERW), table `eia_gas_balance_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_gas_balance:<process>:<area>, EIA's process code and area (S<state>, NUS, R3FM, with EIA's -Z00 and -Z0S forms) | none | text | for example eia_gas_balance:EEI:NUS-Z00, eia_gas_balance:EEI:R3FM-Z00, eia_gas_balance:EEI:SAK-Z00; 460 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1997-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 29 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -2019157.0 to 74778078.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> for a state area, US otherwise | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 11274 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name | none | text | for example Alabama  Natural Gas International Receipts (Million Cubic Feet), Alabama Dry Natural Gas Production (Million Cubic Feet), Alabama Natural  Gas Underground Storage Withdrawals (MMcf); 460 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/sum/snd | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/sum/snd/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=VC0&facets%5Bprocess%5D%5B%5D=FPD&facets%5Bprocess%5D%5B%5D=OVI&facets%5Bprocess%5D%5B%5D=IMI&facets%5Bprocess%5D%5B%5D=EEI&facets%5Bprocess%5D%5B%5D=MIR&facets%5Bprocess%5D%5B%5D=MID&facets%5Bprocess%5D%5B%5D=SAI&facets%5Bprocess%5D%5B%5D=SAW&facets%5Bprocess%5D%5B%5D=VG4&start=1997 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T23:21:38Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 11274 |

Variables (10):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `balancing_item` | EIA's balancing item, the difference supply and disposition leave (VG4), million cubic feet | MMcf | 1480 | 1997-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `dry_production` | Dry natural gas production (FPD), million cubic feet | MMcf | 982 | 1997-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `exports_intransit` | International deliveries, exports including gas in transit (EEI), million cubic feet | MMcf | 676 | 1997-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `imports_intransit` | International receipts, imports including gas in transit (IMI), million cubic feet | MMcf | 799 | 1997-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `interstate_deliveries` | Gas delivered to other states (MID), million cubic feet | MMcf | 1438 | 1997-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `interstate_receipts` | Gas received from other states (MIR), million cubic feet | MMcf | 1426 | 1997-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `storage_injections` | Injections into underground storage (SAI), million cubic feet | MMcf | 903 | 1997-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `storage_withdrawals` | Withdrawals from underground storage (SAW), million cubic feet | MMcf | 904 | 1997-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `supplemental_fuels` | Supplemental gaseous fuels supplied (OVI), million cubic feet | MMcf | 1183 | 1997-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_consumption` | Total natural gas consumption (VC0), million cubic feet | MMcf | 1483 | 1997-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `eia_gas_consumers_state_annual`

One state's (or the nation's) yearly number of natural gas consumers of one kind (residential, commercial, industrial; in all, buying from a utility, or with gas transported for them).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 12864.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:natural-gas/cons/num U.S. Energy Information Administration, Natural Gas Annual, number of consumers (API v2, route natural-gas/cons/num) (https://www.eia.gov/dnav/ng/ng_cons_num_dcu_nus_a.htm)
- **Method note:** [`docs/methods/eia_gas_consumers_state_annual.md`](../methods/eia_gas_consumers_state_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural Gas Annual, number of consumers (API v2). Via the Energy Research Warehouse (ERW), table `eia_gas_consumers_state_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_gas_consumers:<EIA area: NUS or S<state>> | none | text | for example eia_gas_consumers:NUS, eia_gas_consumers:SAK, eia_gas_consumers:SAL; 52 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1986-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 39 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 73719064.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 12864 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series description | none | text | for example Alabama Natural Gas Number of Commercial Consumers (Count), Alabama Natural Gas Number of Commercial Consumers - Sales (Count), Alabama Natural Gas Number of Commercial Consumers - Transported (Count); 444 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/cons/num | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/cons/num/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T02:20:47Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 12864 |

Variables (9):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `commercial_consumers` | Number of commercial natural gas consumers | count | 1987 | 1986-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `commercial_consumers_sales` | Commercial consumers buying gas from a utility | count | 1248 | 1998-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `commercial_consumers_transported` | Commercial consumers with gas transported for them | count | 1198 | 1998-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `industrial_consumers` | Number of industrial natural gas consumers | count | 1934 | 1986-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `industrial_consumers_sales` | Industrial consumers buying gas from a utility | count | 1224 | 1998-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `industrial_consumers_transported` | Industrial consumers with gas transported for them | count | 1199 | 1998-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `residential_consumers` | Number of residential natural gas consumers | count | 1987 | 1986-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `residential_consumers_sales` | Residential consumers buying gas from a utility | count | 1299 | 1997-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `residential_consumers_transported` | Residential consumers with gas transported for them | count | 788 | 1997-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_gas_consumption_state_monthly`

One state's (or the nation's) monthly natural gas consumption by one sector, or in total, from EIA's Natural Gas Monthly.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 63420.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:natural-gas/cons/sum U.S. Energy Information Administration, Natural Gas Monthly, consumption by state (API v2, route natural-gas/cons/sum) (https://www.eia.gov/naturalgas/monthly/)
- **Method note:** [`docs/methods/eia_gas_consumption_state_monthly.md`](../methods/eia_gas_consumption_state_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural Gas Monthly, consumption by state (API v2). Via the Energy Research Warehouse (ERW), table `eia_gas_consumption_state_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_gas_consumption:<process>:<area> | none | text | for example eia_gas_consumption:VC0:NUS, eia_gas_consumption:VCS:NUS, eia_gas_consumption:VCS:SAK; 208 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 307 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 3921586.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 63420 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name | none | text | for example Alabama Natural Gas Deliveries to Electric Power Consumers (MMcf), Alabama Natural Gas Industrial Consumption (MMcf), Alabama Natural Gas Residential Consumption (MMcf); 208 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/cons/sum | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/cons/sum/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=VRS&facets%5Bprocess%5D%5B%5D=VCS&facets%5Bprocess%5D%5B%5D=VIN&facets%5Bprocess%5D%5B%5D=VEU&facets%5Bprocess%5D%5B%5D=VC0&start=2001-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T20:22:19Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 63420 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption_commercial` | Natural gas delivered to commercial consumers (VCS), million cubic feet | MMcf | 15943 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `consumption_electric_power` | Natural gas delivered to electric power consumers (VEU), million cubic feet | MMcf | 15395 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `consumption_industrial` | Natural gas delivered to industrial consumers (VIN), million cubic feet | MMcf | 15827 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `consumption_residential` | Natural gas delivered to residential consumers (VRS), million cubic feet | MMcf | 15948 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `consumption_total` | Total natural gas consumption (VC0), million cubic feet; holds the others and more, so leave it out of a sum | MMcf | 307 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_gas_for_others_annual`

One state's (or the nation's) yearly natural gas delivered for the account of others (customer choice and transportation gas) to one sector, as a volume or as a share of the sector's deliveries.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 9245.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:natural-gas/cons/acct U.S. Energy Information Administration, Natural Gas Annual, natural gas delivered for the account of others (API v2, route natural-gas/cons/acct) (https://api.eia.gov/v2/natural-gas/cons/acct/)
- **Method note:** [`docs/methods/eia_gas_for_others_annual.md`](../methods/eia_gas_for_others_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural Gas Annual, natural gas delivered for the account of others (API v2). Via the Energy Research Warehouse (ERW), table `eia_gas_for_others_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_gas_for_others:<EIA series id> | none | text | for example eia_gas_for_others:NA1502_NUS_2, eia_gas_for_others:NA1502_SAL_2, eia_gas_for_others:NA1502_SAZ_2; 269 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1982-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 43 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 7415212.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation | none | text | for example US, US-AK, US-AL; 51 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 9245 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series description | none | text | for example Alabama Natural Gas % of Total Commercial Delivered for the Account of Others (%), Alabama Natural Gas % of Total Industrial Delivered for the Account of Others (%), Alabama Natural Gas % of Total Residential Consumers Delivered for the Account of Others (%); 269 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/cons/acct | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/cons/acct/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=VRT&facets%5Bprocess%5D%5B%5D=VF8&facets%5Bprocess%5D%5B%5D=VFT&facets%5Bprocess%5D%5B%5D=VF9&facets%5Bprocess%5D%5B%5D=VF6&facets%5Bprocess%5D%5B%5D=VFI&start=1982 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T09:01:59Z, 2026-10-24T09:02:05Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 9245 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `commercial_for_others` | Commercial gas delivered for the account of others, million cubic feet | MMcf | 1888 | 1987-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `commercial_share` | Share of commercial deliveries made for the account of others, a ratio (EIA's percent over 100) | ratio | 1753 | 1989-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `industrial_for_others` | Industrial gas delivered for the account of others, million cubic feet | MMcf | 2124 | 1982-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `industrial_share` | Share of industrial deliveries made for the account of others, a ratio (EIA's percent over 100) | ratio | 1767 | 1989-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `residential_for_others` | Residential gas delivered for the account of others, million cubic feet | MMcf | 1237 | 1988-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `residential_share` | Share of residential deliveries made for the account of others, a ratio (EIA's percent over 100; whole percents) | ratio | 476 | 2007-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_gas_heat_content_monthly`

One month's average heat content of natural gas delivered to consumers in one state, DC or the U.S.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 8476.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:natural-gas/cons/heat U.S. Energy Information Administration, Natural Gas Monthly, heat content of natural gas delivered to consumers (API v2, route natural-gas/cons/heat) (https://api.eia.gov/v2/natural-gas/cons/heat/)
- **Method note:** [`docs/methods/eia_gas_heat_content_monthly.md`](../methods/eia_gas_heat_content_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural Gas Monthly, heat content of natural gas delivered to consumers (API v2). Via the Energy Research Warehouse (ERW), table `eia_gas_heat_content_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_gas_heat_content:<EIA series id> | none | text | for example eia_gas_heat_content:NGA_EPG0_VGTH_NUS_BTUCF, eia_gas_heat_content:NGA_EPG0_VGTH_SAK_BTUCF, eia_gas_heat_content:NGA_EPG0_VGTH_SAL_BTUCF; 52 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2013-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 163 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 901.0 to 1140.0; 186 distinct | 0 |
| `unit` | The unit of the row's value | none | text | Btu/ft3 | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 8476 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series description (the area) | none | text | for example Alabama Heat Content of Natural Gas Deliveries to Consumers (BTU per Cubic Foot), Alaska Heat Content of Natural Gas Deliveries to Consumers (BTU per Cubic Foot), Arizona Heat Content of Natural Gas Deliveries to Consumers (BTU per Cubic Foot); 52 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/cons/heat | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/cons/heat/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=VGTH&start=2012-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T03:44:48Z, 2026-10-24T03:44:52Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 8476 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `heat_content` | Average heat content of the gas delivered to consumers, Btu per cubic foot; never summed across states | Btu/ft3 | 8476 | 2013-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_gas_interstate_annual`

One year's natural gas movement between a pair of areas (states, the federal Gulf, Canada, Mexico, other countries) for one process, from EIA's Natural Gas Annual.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 29470.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:natural-gas/move/ist U.S. Energy Information Administration, Natural Gas Annual, interstate movements (API v2, route natural-gas/move/ist) (https://www.eia.gov/naturalgas/annual/)
- **Method note:** [`docs/methods/eia_gas_interstate_annual.md`](../methods/eia_gas_interstate_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural Gas Annual, interstate movements (API v2). Via the Energy Research Warehouse (ERW), table `eia_gas_interstate_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_gas_interstate:<process>:<from-to pair>; Z00 is the first area's total, Z0R and Z0S its parts | none | text | for example eia_gas_interstate:EEI:NUS-Z00, eia_gas_interstate:EEI:R3FM-Z00, eia_gas_interstate:EEI:SAK-NCA; 1903 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1997-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 28 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -6498093.0 to 78835235.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> of the pair's first area, US otherwise | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 29470 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name, naming both areas | none | text | for example Alabama  Natural Gas International Receipts (Million Cubic Feet), Alabama  Natural Gas Net International Receipts (Million Cubic Feet), Alabama Natural Gas International & Interstate Deliveries (MMcf); 1888 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/move/ist | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/move/ist/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=MIN&facets%5Bprocess%5D%5B%5D=MID&facets%5Bprocess%5D%5B%5D=MIR&facets%5Bprocess%5D%5B%5D=IMB&facets%5Bprocess%5D%5B%5D=EEI&facets%5Bprocess%5D%5B%5D=IMI&facets%5Bprocess%5D%5B%5D=MIE&facets%5Bprocess%5D%5B%5D=MIT&facets%5Bprocess%5D%5B%5D=MIF&start=1997 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T22:16:43Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 29470 |

Variables (9):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `deliveries` | Interstate deliveries (MID), million cubic feet | MMcf | 6286 | 1997-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `deliveries_exports` | Deliveries including exports (MIF), million cubic feet | MMcf | 1416 | 1997-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `exports_intransit` | International deliveries including gas in transit (EEI), million cubic feet | MMcf | 1691 | 1997-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `imports_intransit` | International receipts including gas in transit (IMI), million cubic feet | MMcf | 1531 | 1997-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_across_borders` | Net movement across borders (IMB), million cubic feet | MMcf | 2152 | 1997-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_receipts` | Net interstate receipts (MIN), million cubic feet | MMcf | 7220 | 1997-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_receipts_imports` | Net receipts including imports (MIE), million cubic feet | MMcf | 1457 | 1997-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `receipts` | Interstate receipts (MIR), million cubic feet | MMcf | 6287 | 1997-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `receipts_imports` | Receipts including imports (MIT), million cubic feet | MMcf | 1430 | 1997-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_gas_other_uses_state_annual`

One state's (or the nation's) yearly natural gas used as vehicle fuel, lease and plant fuel or pipeline fuel, or delivered to consumers, from EIA's Natural Gas Annual.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3838.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:natural-gas/cons/sum:annual U.S. Energy Information Administration, Natural Gas Annual, consumption by end use and state (API v2, route natural-gas/cons/sum) (https://www.eia.gov/naturalgas/annual/)
- **Method note:** [`docs/methods/eia_gas_other_uses_state_annual.md`](../methods/eia_gas_other_uses_state_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural Gas Annual, consumption by end use and state: vehicle, lease and plant, pipeline fuel, deliveries (API v2). Via the Energy Research Warehouse (ERW), table `eia_gas_other_uses_state_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_gas_other_uses:<process>:<area> | none | text | for example eia_gas_other_uses:VDV:NUS, eia_gas_other_uses:VDV:SAK, eia_gas_other_uses:VDV:SAL; 157 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z, 2002-01-01T00:00:00Z, 2003-01-01T00:00:00Z, 2004-01-01T00:00:00Z, 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 30181736.0; 3051 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3838 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name | none | text | for example Alabama Natural Gas Pipeline and Distribution Use (MMcf), Alabama Natural Gas Vehicle Fuel Consumption (MMcf), Alaska Natural Gas Pipeline and Distribution Use (MMcf); 157 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/cons/sum:annual | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/cons/sum/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=VDV&facets%5Bprocess%5D%5B%5D=VGL&facets%5Bprocess%5D%5B%5D=VGP&facets%5Bprocess%5D%5B%5D=VGT&start=2001 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T01:00:33Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3838 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption_lease_and_plant_fuel` | Natural gas used as lease and plant fuel (VGL), million cubic feet; the nation's only | MMcf | 25 | 2001-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `consumption_pipeline_fuel` | Natural gas used as pipeline and distribution fuel (VGP), million cubic feet | MMcf | 1245 | 2001-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `consumption_vehicle_fuel` | Natural gas used as vehicle fuel (VDV), million cubic feet | MMcf | 1277 | 2001-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `delivered_to_consumers` | Volume delivered to consumers (VGT), million cubic feet; holds residential, commercial, industrial, electric power and vehicle fuel, so leave it out of a sum | MMcf | 1291 | 2001-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `eia_gas_pipeline_projects`

One natural gas pipeline project on EIA's tracker (current or historical sheet), as of the tracker of August 2026.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 1334.

- **Time:** event_date is EIA's completed date where it gives one, else 1 January of the year in service, else the date EIA last updated the record (x_date_basis says which).
- **Revisions:** Rewritten whole by each run from the newest tracker; there is no vintage column. Ids EIA gives twice with two rows are left out.
- **Source:** eia:naturalgas:pipeline_projects U.S. Energy Information Administration, natural gas pipeline projects (https://www.eia.gov/naturalgas/data.php)
- **Method note:** [`docs/methods/eia_gas_pipeline_projects.md`](../methods/eia_gas_pipeline_projects.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural gas pipeline projects. Via the Energy Research Warehouse (ERW), table `eia_gas_pipeline_projects`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: eia_gas_pipeline:<project name slug>:<year in service slug> | none | text | for example eia_gas_pipeline:134th_street_lateral_project:2021, eia_gas_pipeline:2010_system_enhancement_project:2010, eia_gas_pipeline:2011_system_expansion:2012; 1334 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which). Here: Completed date, else the year in service's 1 January, else EIA's last update (x_date_basis) | none | date | 1903-11-05 to 2031-01-01; 781 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: pipeline_project on every row | none | text | pipeline_project | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: The pipeline operator | none | text | for example 8 Star Alaska LLC, ANR Pipeline, ANR Pipeline Co. (TC Energy); 403 distinct | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons. Here: Not filled | none | empty | no cell holds a value | 1334 |
| `mw` | The capacity involved, in megawatts. Here: Not filled | MW | empty | no cell holds a value | 1334 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise. Here: Not filled | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 1334 |
| `currency` | The currency of the price, as an ISO 4217 code (USD). Here: Not filled | none | empty | no cell holds a value | 1334 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: EIA's status in lower case (completed, construction, approved, cancelled and the others) | none | text | announced, applied, approved, cancelled, cancelled/on hold, completed, construction, denied, on hold, part completed, pre-applied, proposed | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:naturalgas:pipeline_projects | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjectsAug2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T06:35:49Z | 0 |
| `x_project_name` | The project's name as EIA writes it (the source's name: Project Name) | none | text | for example (SEML) Southeast Mainline System Reversal, 134th Street Lateral Project, 2010 System Enhancement Project; 1325 distinct | 0 |
| `x_project_type` | The project type (Expansion, Lateral, New Pipeline, Reversal, Upgrade, Conversion, Abandonment) (the source's name: Project Type) | none | text | Abandonment, Conversion, Expansion, Lateral, New Pipeline, Reversal, Upgrade | 1: EIA gives no type |
| `x_completed_date` | The date the project was completed, as EIA gives it (the source's name: Completed Date) | none | date | 1903-11-05 to 2026-05-26; 734 distinct | 207: EIA gives no completed date |
| `x_year_in_service` | The year the project entered or is to enter service, as EIA writes it (the source's name: Year In Service Date) | none | text | for example 1996, 1997, 1998; 38 distinct | 29: EIA gives no year in service |
| `x_states` | EIA's list of the states (and provinces) the project is in (the source's name: State(s)) | none | text | for example AB,MT, AK, AL; 294 distinct | 0 |
| `x_beg_state` | The state where the project begins (the source's name: Beg_State) | none | text | for example AB, AK, AL; 58 distinct | 0 |
| `x_end_state` | The state where the project ends (the source's name: End_State) | none | text | for example AK, AL, AR; 58 distinct | 0 |
| `x_regions` | EIA's list of the regions the project is in (the source's name: Region(s)) | none | text | for example Canada, Canada, Midwest, Canada, Mountain; 49 distinct | 2: EIA gives no region |
| `x_beg_region` | The region where the project begins (the source's name: Beg_Region) | none | text | Canada, Gulf of America, Gulf of Mexico, Mexico, Midwest, Mountain, Northeast, Pacific, South Central, Southeast | 1: EIA gives no region |
| `x_end_region` | The region where the project ends (the source's name: End_Region) | none | text | Canada, Gulf of America, Gulf of Mexico, Mexico, Midwest, Mountain, Northeast, Pacific, South Central, Southeast | 2: EIA gives no region |
| `x_thru_region` | The regions the project passes through (the source's name: Thru_Region) | none | text | Midwest, Mountain, Mountain, Pacific, Northeast, Pacific, South Central, Southeast | 1294: EIA names no region passed through |
| `x_cost_million_usd` | The project's cost as EIA writes it, a range kept as a range (the source's name: Cost (millions)) | million USD | text | for example 0, 0.03, 0.05; 693 distinct | 215: EIA gives no cost |
| `x_miles` | The project's length (the source's name: Miles) | miles | text | for example -500, -956.4, 0; 496 distinct | 315: EIA gives no length |
| `x_capacity_mmcfd` | The capacity the project adds (the source's name: Additional Capacity) | MMcf/d | text | for example -150, -25, -255; 480 distinct | 62: EIA gives no added capacity |
| `x_diameter_inches` | The pipeline's diameter (several where EIA lists several) (the source's name: Pipeline Diameter) | inches | text | for example 10, 10,12, 10,16; 110 distinct | 374: EIA gives no diameter |
| `x_pipeline_type` | The pipeline type (Interstate, Intrastate, Foreign, Cross-border) (the source's name: Pipeline Type) | none | text | Cross-border, Foreign, Interstate, Intrastate | 3: EIA gives no type |
| `x_authority` | The authority that regulates the project (FERC, a state commission and the others) (the source's name: Authority) | none | text | for example AK DNR, AL PSC, CPUC; 26 distinct | 49: EIA names no authority |
| `x_docket` | The authority's docket number for the project (the source's name: Docket) | none | text | for example 6630-CG-138, CP 24-1, CP 26-18; 953 distinct | 105: EIA gives no docket |
| `x_crosses_state_border` | Yes or No: whether the project crosses a state border (the source's name: Crosses State Border) | none | text | No, Yes | 784: EIA does not say |
| `x_notes` | EIA's notes on the project (the source's name: Notes or Project Notes) | none | text | for example 1.9 miles of 42-inch Chilton Loop in Coosa and Chilton Counties, AL plus new 11,110 HP Solar Taurus 70 compressor unit and modifications at existing Compressor Station 105 in Coosa County. Adds 150,000 Dth/d of firm transport from existing MS/AL supply points to the Gaston delivery meter station supporting Alabama Power's coal-to-gas conversion of Gaston Unit 5. Commissioned 4/1/2025., 10.2-mile 36-inch Line 31 loop parallel to existing Lines 14/18 plus a 1.6-mile 16-inch Line 14-P Lateral to Entergy Mississippi's planned Traceview Advanced Power Station, with a new Ridgeland Compressor Station (3 × 1,500 HP gas-driven units) and meter/regulator station  -  all in Madison County, MS. Adds 125,000 Dth/d of firm capacity. Application filed 1/23/2026 (CP26-75); total cost $131M. Construction planned 8/2027; target in-service 9/2028., 11/27/2024: VG Plaquemines rec'd FERC approval to place PH 1 facilities in service. Deliver feedgas to Plaquemines LNG via new interstate pipeline; interconnections with TGP (Southwest Lateral TGP) and TETCO.; 419 distinct | 907: EIA gives no note |
| `x_demand_served` | The demand the project serves, as EIA gives it (Electric, LDC, Data Center and the others) (the source's name: Demand Served) | none | text | for example Data Center, Electric, Electric, Industrial, LDC; 48 distinct | 1128: EIA does not say |
| `x_website` | The website or document EIA cites for the project, as EIA gives it (the source's name: Website) | none | text | for example 1Q 2025 Financial Results, 4Q22 Financial Results PR, Commencement of service announcement; 156 distinct | 1067: EIA cites none |
| `x_last_updated` | When EIA last updated the record (the source's name: Last Updated Date) | none | date | 2009-06-26 to 2026-11-14; 304 distinct | 0 |
| `x_sheet` | The tracker's sheet the project is on: current or historical | none | text | current, historical | 0 |
| `x_date_basis` | Which date event_date is: completed, year_in_service or last_updated | none | text | completed, last_updated, year_in_service | 0 |

### `eia_gas_plant_processing_annual`

One year's natural gas plant processing figure (gas processed, extraction loss or liquids extracted) for the U.S., a state or one of EIA's processing areas.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 5829.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:natural-gas/prod/pp U.S. Energy Information Administration, Natural Gas Annual, natural gas plant processing (API v2, route natural-gas/prod/pp) (https://api.eia.gov/v2/natural-gas/prod/pp/)
- **Method note:** [`docs/methods/eia_gas_plant_processing_annual.md`](../methods/eia_gas_plant_processing_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural Gas Annual, natural gas plant processing (API v2). Via the Energy Research Warehouse (ERW), table `eia_gas_plant_processing_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_gas_plant_processing:<EIA series id> | none | text | for example eia_gas_plant_processing:N9060US2, eia_gas_plant_processing:NA1150_SAK_2, eia_gas_plant_processing:NA1150_SAL_2; 276 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1967-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 59 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 27088079.0; 4563 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf, kbbl | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US (the U.S., the federal offshore) or US-<state> (a state, its onshore or offshore part, or a pair's producing area) | none | text | for example US, US-AK, US-AL; 27 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5829 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's description | none | text | for example Alabama Natural Gas Plant Liquids Production (Million Cubic Feet), Alabama Natural Gas Processed (Million Cubic Feet), Alabama Natural Gas Total Liquids Extracted (Thousand Barrels); 275 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/prod/pp | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/prod/pp/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=YGP&facets%5Bprocess%5D%5B%5D=VG9&facets%5Bprocess%5D%5B%5D=YGT&start=1967 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T05:25:04Z, 2026-10-24T05:25:08Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5829 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `extraction_loss` | Volume lost from the gas as liquids are extracted (VG9), million cubic feet | MMcf | 2030 | 1967-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `gas_processed` | Natural gas processed at plants (YGP), million cubic feet | MMcf | 2075 | 1967-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `liquids_extracted` | Natural gas plant liquids extracted (YGT), thousand barrels | kbbl | 1724 | 1983-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_gas_prices_state_monthly`

One state's (or the nation's) monthly average natural gas price in one category (citygate, residential, commercial, industrial, electric power), as EIA's Natural Gas Monthly gives it.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 72550.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot), so a month EIA revises is replaced and a row EIA no longer gives leaves. vintage is not filled.
- **Source:** eia:natural-gas/pri/sum U.S. Energy Information Administration, Natural Gas Monthly, prices by state (API v2, route natural-gas/pri/sum) (https://www.eia.gov/naturalgas/monthly/)
- **Method note:** [`docs/methods/eia_gas_prices_state_monthly.md`](../methods/eia_gas_prices_state_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural Gas Monthly, prices by state (API v2). Via the Energy Research Warehouse (ERW), table `eia_gas_prices_state_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_gas_price:<process>:<area>, EIA's process code and area code (S<state> or NUS) | none | text | for example eia_gas_price:PCS:NUS, eia_gas_price:PCS:SAK, eia_gas_price:PCS:SAL; 257 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 307 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -3.26 to 152.45; 3378 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/Mcf | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 72550 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name | none | text | for example Alabama Natural Gas Industrial Price (Dollars per Thousand Cubic Feet), Alabama Natural Gas Price Sold to Electric Power Consumers (Dollars per Thousand Cubic Feet), Alabama Price of Natural Gas Delivered to Residential Consumers (Dollars per Thousand Cubic Feet); 257 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/pri/sum | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/pri/sum/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=PG1&facets%5Bprocess%5D%5B%5D=PRS&facets%5Bprocess%5D%5B%5D=PCS&facets%5Bprocess%5D%5B%5D=PIN&facets%5Bprocess%5D%5B%5D=PEU&start=2001-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T20:17:23Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 72550 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `price_citygate` | Citygate price (EIA process PG1: gas delivered to the local distribution company), USD per thousand cubic feet | USD/Mcf | 15632 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `price_commercial` | Price paid by commercial consumers (PCS), USD per thousand cubic feet | USD/Mcf | 15922 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `price_electric_power` | Price paid by electric power consumers (PEU), USD per thousand cubic feet | USD/Mcf | 9492 | 2002-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `price_industrial` | Price paid by industrial consumers (PIN), USD per thousand cubic feet | USD/Mcf | 15579 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `price_residential` | Price paid by residential consumers (PRS), USD per thousand cubic feet | USD/Mcf | 15925 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_gas_production_state_monthly`

One state's, offshore area's or the nation's monthly natural gas production figure (gross withdrawals, marketed or dry production, vented and flared, shale gas), from EIA's Natural Gas Monthly.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 47805.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:natural-gas/prod/sum U.S. Energy Information Administration, Natural Gas Monthly, production by state (API v2, route natural-gas/prod/sum) (https://www.eia.gov/naturalgas/monthly/)
- **Method note:** [`docs/methods/eia_gas_production_state_monthly.md`](../methods/eia_gas_production_state_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural Gas Monthly, production by state (API v2). Via the Energy Research Warehouse (ERW), table `eia_gas_production_state_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_gas_production:<area>:<series stem> | none | text | for example eia_gas_production:NUS:N9010US, eia_gas_production:NUS:N9040US, eia_gas_production:NUS:N9050US; 184 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 307 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -14.0 to 4247306.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 35 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 47805 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name | none | text | for example Alabama Dry Natural Gas Production (Million Cubic Feet), Alabama Natural Gas Gross Withdrawals (MMcf), Alabama Natural Gas Gross Withdrawals from Shale Gas (Million Cubic Feet); 184 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/prod/sum | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/prod/sum/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=FGW&facets%5Bprocess%5D%5B%5D=VGM&facets%5Bprocess%5D%5B%5D=FPD&facets%5Bprocess%5D%5B%5D=VGV&facets%5Bprocess%5D%5B%5D=FGS&start=2001-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T21:14:19Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 47805 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dry_production` | Dry natural gas production (FPD), million cubic feet in the month | MMcf | 8227 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `gross_withdrawals` | Gross withdrawals of natural gas (FGW), million cubic feet in the month | MMcf | 10773 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `marketed_production` | Marketed natural gas production (VGM), million cubic feet in the month | MMcf | 10773 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `shale_withdrawals` | Gross withdrawals from shale gas wells (FGS), within gross withdrawals, million cubic feet in the month | MMcf | 7620 | 2007-01-01T00:00:00Z | 2024-12-01T00:00:00Z |
| `vented_flared` | Natural gas vented and flared (VGV), million cubic feet in the month | MMcf | 10412 | 2001-01-01T00:00:00Z | 2024-12-01T00:00:00Z |

### `eia_gas_reserves_annual`

One state's, area's or the nation's dry natural gas proved reserves at a year's end, or one of the changes that take one year's reserves to the next.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 19232.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y); reserves are as of the year's end.
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:natural-gas/enr/dry U.S. Energy Information Administration, U.S. Crude Oil and Natural Gas Proved Reserves (API v2, route natural-gas/enr/dry) (https://www.eia.gov/naturalgas/crudeoilreserves/)
- **Method note:** [`docs/methods/eia_gas_reserves_annual.md`](../methods/eia_gas_reserves_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). U.S. Crude Oil and Natural Gas Proved Reserves, dry natural gas (API v2). Via the Energy Research Warehouse (ERW), table `eia_gas_reserves_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_gas_reserves:<process>:<area>; parts of states and the Lower 48 repeat states and the U.S. | none | text | for example eia_gas_reserves:R11:NUS, eia_gas_reserves:R11:R1901F, eia_gas_reserves:R11:R44F; 561 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1977-01-01T00:00:00Z to 2021-01-01T00:00:00Z; 45 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -10055.0 to 589236.0; 4519 distinct | 0 |
| `unit` | The unit of the row's value | none | text | bcf | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> for a state, US otherwise | none | text | US, US-AK, US-AL, US-AR, US-CA, US-CO, US-FL, US-KS, US-KY, US-LA, US-MI, US-MS, US-MT, US-ND, US-NM, US-NY, US-OH, US-OK, US-PA, US-TX, US-UT, US-VA, US-WV, US-WY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 19232 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name (for R11 EIA writes Expected Future Production) | none | text | for example Alabama Dry Natural Gas Expected Future Production (Billion Cubic Feet), Alabama Dry Natural Gas New Reservoir Discoveries in Old Fields (Billion Cubic Feet), Alabama Dry Natural Gas Reserves Acquisitions (Billion Cubic Feet); 561 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/enr/dry | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/enr/dry/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=R11&facets%5Bprocess%5D%5B%5D=R12&facets%5Bprocess%5D%5B%5D=R13&facets%5Bprocess%5D%5B%5D=R14&facets%5Bprocess%5D%5B%5D=R15&facets%5Bprocess%5D%5B%5D=R16&facets%5Bprocess%5D%5B%5D=R17&facets%5Bprocess%5D%5B%5D=R17A&facets%5Bprocess%5D%5B%5D=R18&facets%5Bprocess%5D%5B%5D=R19&facets%5Bprocess%5D%5B%5D=R20&start=1977 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T22:16:59Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 19232 |

Variables (11):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `acquisitions` | Proved reserves acquired (R16), billion cubic feet | bcf | 1117 | 2000-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `adjustments` | Adjustments to proved reserves (R12), billion cubic feet | bcf | 2200 | 1977-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `extensions` | Extensions of proved reserves (R17, 1977 to 2015), billion cubic feet | bcf | 1899 | 1977-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `extensions_and_discoveries` | Extensions and discoveries of proved reserves (R17A, 2016 to 2021), billion cubic feet | bcf | 301 | 2016-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `new_field_discoveries` | New field discoveries (R18, 1977 to 2015), billion cubic feet | bcf | 1899 | 1977-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `new_reservoir_discoveries` | New reservoir discoveries in old fields (R19, 1977 to 2015), billion cubic feet | bcf | 1899 | 1977-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `production` | Estimated production from reserves in the year (R20), billion cubic feet | bcf | 2200 | 1977-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `proved_reserves` | Dry natural gas proved reserves at the year's end (R11), billion cubic feet | bcf | 2200 | 1977-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `revision_decreases` | Revision decreases of proved reserves (R14), billion cubic feet | bcf | 2200 | 1977-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `revision_increases` | Revision increases of proved reserves (R13), billion cubic feet | bcf | 2200 | 1977-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `sales` | Proved reserves sold (R15), billion cubic feet | bcf | 1117 | 2000-01-01T00:00:00Z | 2021-01-01T00:00:00Z |

### `eia_gas_storage_capacity_monthly`

One month's underground natural gas storage capacity (total or working gas) or number of storage fields, for a state, region, the lower 48 or the U.S.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 23980.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:natural-gas/stor/cap U.S. Energy Information Administration, Natural Gas Monthly, underground storage capacity (API v2, route natural-gas/stor/cap) (https://www.eia.gov/dnav/ng/ng_stor_cap_dcu_nus_m.htm)
- **Method note:** [`docs/methods/eia_gas_storage_capacity_monthly.md`](../methods/eia_gas_storage_capacity_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural Gas Monthly, underground storage capacity (API v2). Via the Energy Research Warehouse (ERW), table `eia_gas_storage_capacity_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_gas_storage_capacity:<EIA series id> | none | text | for example eia_gas_storage_capacity:N5290832, eia_gas_storage_capacity:N5290842, eia_gas_storage_capacity:N5290852; 123 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1989-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 451 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.0 to 9371003.0; 2960 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 32 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 23980 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name | none | text | for example AGA Eastern Consuming Region Natural Gas Count of Underground Storage Capacity (Count), AGA Eastern Consuming Region Natural Gas Total Underground Storage Capacity (MMcf), AGA Eastern Consuming Region Natural Gas Working Underground Storage Capacity (MMcf); 123 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/stor/cap | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/stor/cap/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=SAC&facets%5Bprocess%5D%5B%5D=SACW0&facets%5Bprocess%5D%5B%5D=SAD&start=1989-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-22T03:59:30Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 23980 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `storage_fields` | Number of underground storage fields (SAD) | count | 6228 | 2013-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `total_capacity` | Total underground storage capacity (SAC), million cubic feet | MMcf | 11150 | 1989-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `working_capacity` | Working gas storage capacity, the gas that can be withdrawn (SACW0), million cubic feet | MMcf | 6602 | 2012-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_gas_storage_state_monthly`

One state's, region's or the nation's monthly natural gas in underground storage (a month-end stock) or injections and withdrawals (a flow over the month).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 55015.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M); a stock is at the month's end, a flow over the month.
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:natural-gas/stor/sum U.S. Energy Information Administration, Natural Gas Monthly, underground storage by state (API v2, route natural-gas/stor/sum) (https://www.eia.gov/naturalgas/monthly/)
- **Method note:** [`docs/methods/eia_gas_storage_state_monthly.md`](../methods/eia_gas_storage_state_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural Gas Monthly, underground storage by state (API v2). Via the Energy Research Warehouse (ERW), table `eia_gas_storage_state_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_gas_storage:<process>:<area> | none | text | for example eia_gas_storage:SAB:NUS, eia_gas_storage:SAB:R48, eia_gas_storage:SAB:R83; 205 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 307 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 8432410.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 32 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 55015 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name | none | text | for example AGA Eastern Consuming Region Natural  Gas Underground Storage Withdrawals (MMcf), AGA Eastern Consuming Region Natural Gas Injections into Underground Storage (MMcf), AGA Eastern Consuming Region Natural Gas Underground Storage Volume (MMcf); 205 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/stor/sum | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/stor/sum/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=SAO&facets%5Bprocess%5D%5B%5D=SAB&facets%5Bprocess%5D%5B%5D=SAT&facets%5Bprocess%5D%5B%5D=SAI&facets%5Bprocess%5D%5B%5D=SAW&start=2001-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T21:13:51Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 55015 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `base_gas` | Base gas (gas left in place to keep pressure) at the month's end (SAB), million cubic feet | MMcf | 11186 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `injections` | Gas injected into storage in the month (SAI), million cubic feet | MMcf | 10750 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `total_gas` | Total gas in storage, working and base (SAT), million cubic feet | MMcf | 11186 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `withdrawals` | Gas withdrawn from storage in the month (SAW), million cubic feet | MMcf | 10744 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `working_gas` | Working gas in storage at the month's end (SAO), million cubic feet | MMcf | 11149 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_gas_storage_type_monthly`

One month's U.S. underground natural gas storage figure for all fields, salt caverns or non-salt fields.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 8367.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M); base and working gas are month-end stocks, the rest flows over the month.
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:natural-gas/stor/type U.S. Energy Information Administration, Natural Gas Monthly, underground natural gas storage by storage type (API v2, route natural-gas/stor/type) (https://api.eia.gov/v2/natural-gas/stor/type/)
- **Method note:** [`docs/methods/eia_gas_storage_type_monthly.md`](../methods/eia_gas_storage_type_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural Gas Monthly, underground natural gas storage by storage type (API v2). Via the Energy Research Warehouse (ERW), table `eia_gas_storage_type_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_gas_storage_type:<EIA series id> | none | text | eia_gas_storage_type:N5010US2, eia_gas_storage_type:N5020US2, eia_gas_storage_type:N5030US2, eia_gas_storage_type:N5050US2, eia_gas_storage_type:N5060US2, eia_gas_storage_type:N5070US2, eia_gas_storage_type:N5400US2, eia_gas_storage_type:N5410US2, eia_gas_storage_type:N5420US2, eia_gas_storage_type:N5440US2, eia_gas_storage_type:N5450US2, eia_gas_storage_type:N5460US2, eia_gas_storage_type:N5500US2, eia_gas_storage_type:N5510US2, eia_gas_storage_type:N5520US2, eia_gas_storage_type:N5540US2, eia_gas_storage_type:N5550US2, eia_gas_storage_type:N5560US2 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1973-12-01T00:00:00Z to 2026-07-01T00:00:00Z; 614 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -497260.0 to 8432410.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 8367 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series description | none | text | U.S. Natural  Gas Underground Storage Withdrawals (MMcf), U.S. Natural Gas Non-Salt Underground Storage  - Base Gas  (MMcf), U.S. Natural Gas Non-Salt Underground Storage - Total  (MMcf), U.S. Natural Gas Non-Salt Underground Storage - Working Gas  (MMcf), U.S. Natural Gas Non-Salt Underground Storage Activity-Net  (MMcf), U.S. Natural Gas Non-Salt Underground Storage Activity-Withdraw  (MMcf), U.S. Natural Gas Non-Salt Underground Storage Injections (MMcf), U.S. Natural Gas Salt - Underground Storage - Base Gas  (MMcf), U.S. Natural Gas Salt Underground Storage - Total  (MMcf), U.S. Natural Gas Salt Underground Storage - Working Gas  (MMcf), U.S. Natural Gas Salt Underground Storage Activity-Injects  (MMcf), U.S. Natural Gas Salt Underground Storage Activity-Net  (MMcf), U.S. Natural Gas Salt Underground Storage Activity-Withdraw  (MMcf), U.S. Natural Gas Underground Storage Net Withdrawals (MMcf), U.S. Natural Gas Underground Storage Volume (MMcf), U.S. Total Natural Gas Injections into Underground Storage (MMcf), U.S. Total Natural Gas in Underground Storage (Base Gas) (MMcf), U.S. Total Natural Gas in Underground Storage (Working Gas) (MMcf) | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/stor/type | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/stor/type/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=SAB&facets%5Bprocess%5D%5B%5D=SAO&facets%5Bprocess%5D%5B%5D=SAT&facets%5Bprocess%5D%5B%5D=SAI&facets%5Bprocess%5D%5B%5D=SAW&facets%5Bprocess%5D%5B%5D=SAN&facets%5Bprocess%5D%5B%5D=SSB&facets%5Bprocess%5D%5B%5D=SSO&facets%5Bprocess%5D%5B%5D=SST&facets%5Bprocess%5D%5B%5D=SSI&facets%5Bprocess%5D%5B%5D=SSW&facets%5Bprocess%5D%5B%5D=SSN&facets%5Bprocess%5D%5B%5D=SNB&facets%5Bprocess%5D%5B%5D=SNO&facets%5Bprocess%5D%5B%5D=SNT&facets%5Bprocess%5D%5B%5D=SNI&facets%5Bprocess%5D%5B%5D=SNW&facets%5Bprocess%5D%5B%5D=SNN&start=1973-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T05:17:23Z, 2026-10-24T05:17:27Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 8367 |

Variables (18):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `all_base_gas` | Base gas in all storage fields at the month's end, million cubic feet | MMcf | 614 | 1973-12-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `all_injections` | Injections into all storage fields in the month, million cubic feet | MMcf | 611 | 1975-09-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `all_net_withdrawals` | Net withdrawals from all storage fields in the month, million cubic feet | MMcf | 611 | 1975-09-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `all_total` | Total gas in all storage fields, million cubic feet | MMcf | 614 | 1973-12-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `all_withdrawals` | Withdrawals from all storage fields in the month, million cubic feet | MMcf | 611 | 1975-09-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `all_working_gas` | Working gas in all storage fields at the month's end, million cubic feet | MMcf | 614 | 1973-12-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `non_salt_base_gas` | Base gas in non-salt fields at the month's end, million cubic feet | MMcf | 391 | 1994-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `non_salt_injections` | Injections into non-salt fields in the month, million cubic feet | MMcf | 391 | 1994-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `non_salt_net_withdrawals` | Net withdrawals from non-salt fields in the month, million cubic feet | MMcf | 391 | 1994-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `non_salt_total` | Total gas in non-salt fields, million cubic feet | MMcf | 391 | 1994-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `non_salt_withdrawals` | Withdrawals from non-salt fields in the month, million cubic feet | MMcf | 391 | 1994-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `non_salt_working_gas` | Working gas in non-salt fields at the month's end, million cubic feet | MMcf | 391 | 1994-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `salt_base_gas` | Base gas in salt caverns at the month's end, million cubic feet | MMcf | 391 | 1994-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `salt_injections` | Injections into salt caverns in the month, million cubic feet | MMcf | 391 | 1994-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `salt_net_withdrawals` | Net withdrawals from salt caverns in the month, million cubic feet | MMcf | 391 | 1994-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `salt_total` | Total gas in salt caverns, million cubic feet | MMcf | 391 | 1994-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `salt_withdrawals` | Withdrawals from salt caverns in the month, million cubic feet | MMcf | 391 | 1994-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `salt_working_gas` | Working gas in salt caverns at the month's end, million cubic feet | MMcf | 391 | 1994-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_gas_storage_weekly`

One region's (or the Lower 48's) working gas in underground storage at the end of one report week, from EIA's Weekly Natural Gas Storage Report.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 7040.

- **Time:** ts_utc is the Friday the report week ends, at 00:00:00Z (freq P1W).
- **Revisions:** Rewritten whole by each run (the file is deleted and the history from 2010 written again), so EIA's revisions are taken. vintage is not filled.
- **Source:** eia:natural-gas/stor/wkly EIA, Weekly Natural Gas Storage Report (https://ir.eia.gov/ngs/ngs.html)
- **Method note:** [`docs/methods/eia_gas_storage_weekly.md`](../methods/eia_gas_storage_weekly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Weekly Natural Gas Storage Report. Via the Energy Research Warehouse (ERW), table `eia_gas_storage_weekly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:<EIA series id> | none | text | eia:NW2_EPG0_SNO_R33_BCF, eia:NW2_EPG0_SSO_R33_BCF, eia:NW2_EPG0_SWO_R31_BCF, eia:NW2_EPG0_SWO_R32_BCF, eia:NW2_EPG0_SWO_R33_BCF, eia:NW2_EPG0_SWO_R34_BCF, eia:NW2_EPG0_SWO_R35_BCF, eia:NW2_EPG0_SWO_R48_BCF | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z to 2026-11-06T00:00:00Z; 880 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 54.0 to 4047.0; 1925 distinct | 0 |
| `unit` | The unit of the row's value | none | text | bcf | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, the regions included | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 7040 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's name of the series (the region) | none | text | Weekly East Region Natural Gas Working Underground Storage, Weekly Lower 48 States Natural Gas Working Underground Storage, Weekly Midwest Region Natural Gas Working Underground Storage, Weekly Mountain Region Natural Gas Working Underground Storage, Weekly Nonsalt Region Natural Gas Working Underground Storage, Weekly Pacific Region Natural Gas Working Underground Storage, Weekly Salt Region Natural Gas Working Underground Storage, Weekly South Central Region Natural Gas Working Underground Storage | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/stor/wkly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/stor/wkly/data/?frequency=weekly&data%5B0%5D=value&start=2010-01-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000, https://api.eia.gov/v2/natural-gas/stor/wkly/data/?frequency=weekly&data%5B0%5D=value&start=2010-01-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=5000&length=5000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T11:47:33Z, 2026-11-16T11:47:34Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 7040 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `working_gas` | Working gas in underground storage (gas available to withdraw), billion cubic feet, as EIA publishes it | bcf | 7040 | 2010-01-01T00:00:00Z | 2026-11-06T00:00:00Z |

### `eia_gas_trade_country_monthly`

One month's U.S. natural gas exports or imports with one country by one mode (pipeline, LNG by vessel, truck, compressed, re-exports), as a volume or a price.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 30337.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:natural-gas/move/expc U.S. Energy Information Administration, Natural Gas Monthly, exports by country (API v2, route natural-gas/move/expc) (https://www.eia.gov/naturalgas/monthly/)
- **Source:** eia:natural-gas/move/impc U.S. Energy Information Administration, Natural Gas Monthly, imports by country (API v2, route natural-gas/move/impc) (https://www.eia.gov/naturalgas/monthly/)
- **Method note:** [`docs/methods/eia_gas_trade_country_monthly.md`](../methods/eia_gas_trade_country_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural Gas Monthly, exports by country (API v2); Natural Gas Monthly, imports by country (API v2). Via the Energy Research Warehouse (ERW), table `eia_gas_trade_country_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_gas_trade:<EIA series id>; countries are parts of the U.S. total of the same mode | none | text | for example eia_gas_trade:N9100US2, eia_gas_trade:N9100US3, eia_gas_trade:N9102CN2; 207 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1973-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 643 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 890326.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf, USD/Mcf | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 30337 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name (the mode and the country) | none | text | for example Compressed U.S. Natural Gas Exports (Million Cubic Feet), Compressed U.S. Natural Gas Imports (Million Cubic Feet), Compressed U.S. Natural Gas Imports from Canada (Million Cubic Feet); 207 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/move/expc, eia:natural-gas/move/impc | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/move/expc/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&start=1973-01, https://api.eia.gov/v2/natural-gas/move/impc/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&start=1973-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-22T03:54:26Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 30337 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `price` | Price of the gas exported or imported, USD per thousand cubic feet | USD/Mcf | 9458 | 1989-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `volume` | Natural gas exported or imported in the month, million cubic feet | MMcf | 20879 | 1973-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_gas_trade_monthly`

One month's natural gas imports or exports through one route (pipeline with Canada or Mexico, LNG in all, or one point of exit), in million cubic feet.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1999.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (the file is deleted and the history from January 2015 written again), so EIA's revisions are taken. vintage is not filled.
- **Source:** eia:natural-gas/move/poe2:supply EIA, U.S. Natural Gas Exports and Re-Exports by Point of Exit (https://www.eia.gov/dnav/ng/ng_move_poe2_a_EPG0_ENP_Mmcf_m.htm)
- **Source:** eia:natural-gas/move/poe1:supply EIA, U.S. Natural Gas Imports by Point of Entry (https://www.eia.gov/dnav/ng/ng_move_poe1_a_EPG0_IRP_Mmcf_m.htm)
- **Method note:** [`docs/methods/eia_gas_trade_monthly.md`](../methods/eia_gas_trade_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). U.S. Natural Gas Exports and Re-Exports by Point of Exit; U.S. Natural Gas Imports by Point of Entry. Via the Energy Research Warehouse (ERW), table `eia_gas_trade_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:<EIA series id> | none | text | for example eia:N9102CN2, eia:N9102MX2, eia:N9103US2; 36 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 140 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 573089.0; 1485 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1999 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's name of the series without its unit | none | text | for example Altamira, Tamaulipas Liquefied Natural Gas Exports to All Countries, Calais, ME Liquefied Natural Gas Exports, Calexico, CA Liquefied Natural Gas Exports to All Countries; 36 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/move/poe1:supply, eia:natural-gas/move/poe2:supply | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/move/poe1/data/?frequency=monthly&data%5B0%5D=value&facets%5Bseries%5D%5B%5D=N9102CN2&facets%5Bseries%5D%5B%5D=N9102MX2&facets%5Bseries%5D%5B%5D=N9103US2&start=2015-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000, https://api.eia.gov/v2/natural-gas/move/poe2/data/?frequency=monthly&data%5B0%5D=value&start=2015-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000, https://api.eia.gov/v2/natural-gas/move/poe2/data/?frequency=monthly&data%5B0%5D=value&start=2015-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=10000&length=5000, https://api.eia.gov/v2/natural-gas/move/poe2/data/?frequency=monthly&data%5B0%5D=value&start=2015-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=15000&length=5000, https://api.eia.gov/v2/natural-gas/move/poe2/data/?frequency=monthly&data%5B0%5D=value&start=2015-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=20000&length=5000, https://api.eia.gov/v2/natural-gas/move/poe2/data/?frequency=monthly&data%5B0%5D=value&start=2015-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=25000&length=5000, https://api.eia.gov/v2/natural-gas/move/poe2/data/?frequency=monthly&data%5B0%5D=value&start=2015-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=30000&length=5000, https://api.eia.gov/v2/natural-gas/move/poe2/data/?frequency=monthly&data%5B0%5D=value&start=2015-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=35000&length=5000, https://api.eia.gov/v2/natural-gas/move/poe2/data/?frequency=monthly&data%5B0%5D=value&start=2015-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=5000&length=5000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T11:47:50Z, 2026-11-16T11:47:51Z, 2026-11-16T11:47:52Z, 2026-11-16T11:47:53Z, 2026-11-16T11:47:55Z, 2026-11-16T11:47:56Z, 2026-11-16T11:47:57Z, 2026-11-16T11:47:58Z, 2026-11-16T11:47:59Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1999 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `export_volume` | Natural gas exported in the month (by pipeline to Canada or Mexico, LNG in all, or through one point of exit), million cubic feet | MMcf | 1579 | 2015-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `import_volume` | Natural gas imported in the month (by pipeline from Canada or Mexico, or as LNG), million cubic feet | MMcf | 420 | 2015-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `eia_gas_wells_annual`

One state's (or the nation's or the federal Gulf's) yearly number of producing natural gas and gas condensate wells, from EIA's Natural Gas Annual.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1062.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:natural-gas/prod/wells U.S. Energy Information Administration, Natural Gas Annual, number of producing gas wells (API v2, route natural-gas/prod/wells) (https://www.eia.gov/naturalgas/annual/)
- **Method note:** [`docs/methods/eia_gas_wells_annual.md`](../methods/eia_gas_wells_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural Gas Annual, number of producing gas wells (API v2). Via the Energy Research Warehouse (ERW), table `eia_gas_wells_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_gas_wells:XDG:<area>, EIA's process and area (S<state>, NUS, R3FM the federal Gulf) | none | text | for example eia_gas_wells:XDG:NUS, eia_gas_wells:XDG:R3FM, eia_gas_wells:XDG:SAK; 36 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1989-01-01T00:00:00Z to 2020-01-01T00:00:00Z; 32 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 586213.0; 860 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> for a state, US otherwise | none | text | for example US, US-AK, US-AL; 35 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1062 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name | none | text | for example Alabama Natural Gas Number of Gas and Gas Condensate Wells (Count), Alaska Natural Gas Number of Gas and Gas Condensate Wells (Count), Arizona Natural Gas Number of Gas and Gas Condensate Wells (Count); 36 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/prod/wells | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/prod/wells/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=XDG&start=1989 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-22T00:37:07Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1062 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `gas_wells` | Number of producing gas and gas condensate wells (XDG) | count | 1062 | 1989-01-01T00:00:00Z | 2020-01-01T00:00:00Z |

### `eia_heat_rates_annual`

One fuel's (coal, petroleum, natural gas, nuclear) average operating heat rate for one year, from EIA's Electric Power Annual Table 8.1.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 44.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot); vintage is the workbook's last-modified time as EIA's server gives it.
- **Source:** eia:electric_power_annual U.S. Energy Information Administration, Electric Power Annual (https://www.eia.gov/electricity/annual/)
- **Method note:** [`docs/methods/eia_capacity_factors.md`](../methods/eia_capacity_factors.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Electric Power Annual (Tables 4.8.A, 4.8.B and 8.1). Via the Energy Research Warehouse (ERW), table `eia_heat_rates_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_epa_heat_rate:<coal\|petroleum\|natural_gas\|nuclear> | none | text | eia_epa_heat_rate:coal, eia_epa_heat_rate:natural_gas, eia_epa_heat_rate:nuclear, eia_epa_heat_rate:petroleum | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 7.689 to 11.465; 41 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMBtu/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 44 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's row name (fuel, average operating heat rate) | none | text | Coal, average operating heat rate, Natural Gas, average operating heat rate, Nuclear, average operating heat rate, Petroleum, average operating heat rate | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:electric_power_annual | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/electricity/annual/xls/epa_08_01.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T14:07:24Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time from EIA's server | none | utc time | 2026-10-19T22:54:36Z | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `heat_rate` | Average operating heat rate (fuel burned per unit of electricity), MMBtu per MWh (EIA's Btu per kWh over 1,000); utility and independent producer plants, combined heat and power excluded; nuclear the units' tested rate | MMBtu/MWh | 44 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `eia_heating_fuel_prices_weekly`

One week's residential or wholesale price of heating oil or propane in one state, PADD or the nation, in the heating season.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 48534.

- **Time:** ts_utc is EIA's week date at 00:00:00Z (freq P1W); weeks outside the heating season have no rows.
- **Revisions:** Rewritten whole by each run (write_snapshot); a saved page is reused unless asked fresh. vintage is not filled.
- **Source:** eia:petroleum/pri/wfr U.S. Energy Information Administration, Heating Oil and Propane Update (API v2, route petroleum/pri/wfr) (https://www.eia.gov/petroleum/heatingoilpropane/)
- **Method note:** [`docs/methods/eia_heating_fuel_prices_weekly.md`](../methods/eia_heating_fuel_prices_weekly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Heating Oil and Propane Update, weekly prices (API v2). Via the Energy Research Warehouse (ERW), table `eia_heating_fuel_prices_weekly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_heating_price:<EIA series id> (one product, process and area) | none | text | for example eia_heating_price:W_EPD2F_PRS_NUS_DPG, eia_heating_price:W_EPD2F_PRS_R10_DPG, eia_heating_price:W_EPD2F_PRS_R1X_DPG; 140 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2012-01-02T00:00:00Z to 2026-10-19T00:00:00Z; 383 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.256 to 6.431; 4855 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/gal | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> for a state, US for the U.S. and for a PADD | none | text | for example US, US-AL, US-AR; 40 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 48534 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name (heating oil or propane) | none | text | for example Alabama Propane Residential Price (Dollars per Gallon), Alabama Propane Wholesale/Resale Price (Dollars per Gallon), Arkansas Propane Residential Price (Dollars per Gallon); 140 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/pri/wfr | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/pri/wfr/data/?api_key=REDACTED&frequency=weekly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=PRS&facets%5Bprocess%5D%5B%5D=PWR&start=2012-01-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-22T00:51:42Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 48534 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `residential_price` | Residential price (EIA process PRS) of heating oil or propane, USD a gallon | USD/gal | 27174 | 2012-01-02T00:00:00Z | 2026-10-19T00:00:00Z |
| `wholesale_price` | Wholesale price (EIA process PWR) of heating oil or propane, USD a gallon | USD/gal | 21360 | 2013-10-07T00:00:00Z | 2026-10-19T00:00:00Z |

### `eia_hgl_pipelines`

One pipeline segment of EIA's Hydrocarbon Gas Liquids (HGL) Pipelines map layer (updated January 2020).

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 133.

- **Time:** No time column. vintage is EIA's update month of the layer (2020-01); the table is a snapshot as read on its retrieved_at.
- **Revisions:** Rewritten whole by each run (write_snapshot).
- **Source:** eia:hgl_pipelines U.S. Energy Information Administration, HGL Pipelines (updated January 2020), as served by Penn State's PASDA:  in batches (sha256 9e3a5b3a06958a436d3ef6c34e192f11ba8824502006e9ba0b41728ca2a7256b, saved at warehouse/raw/hifld_lines/20261120T024611Z/hgl.geojson) (https://mapservices.pasda.psu.edu/server/rest/services/pasda/HIFLD_FEMA/MapServer/47/query)
- **Method note:** [`docs/methods/map_layers.md`](../methods/map_layers.md)
- **Cite as:** U.S. Energy Information Administration, served by Penn State PASDA. HGL Pipelines (updated January 2020), PASDA map service HIFLD_FEMA layer 47. Via the Energy Research Warehouse (ERW), table `eia_hgl_pipelines`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: eia:hgl_pipeline:<OBJECTID> | none | text | for example eia:hgl_pipeline:1, eia:hgl_pipeline:10, eia:hgl_pipeline:100; 133 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: pipeline on every row | none | text | pipeline | 0 |
| `name` | The thing's name, as the publisher writes it. Here: EIA's Pipename | none | text | for example AEGS - East Leg, AEGS - North Leg, AEGS - West Leg; 70 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 133 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: The line's midpoint | degree | number | 26.63288 to 53.11971; 132 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: The line's midpoint | degree | number | -114.48627 to -77.4049; 132 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: Not filled: EIA gives no capacity | MW | empty | no cell holds a value | 133 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 133 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 133 |
| `operator` | The operator or owner, as the publisher writes it. Here: EIA's Opername | none | text | BUCKEYE PARTNERS, DCP MIDSTREAM, ENBRIDGE, ENERGY TRANSFER, ENLINK MIDSTREAM, ENTERPRISE PRODUCTS, EPIC, FLINT HILLS RESOURCES, KINDER MORGAN, MARATHON, MARKWEST LIBERTY, MIDAMERICAN  MIDSTREAM, MPLX, NGL LOGISTICS, NUSTAR ENERGY, ONEOK, PHILLIPS 66 PIPELINE, SUNOCO LOGISTICS, TARGA RESOURCES, VANTAGE PIPELINE, VERESEN, WILLIAMS | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:hgl_pipelines | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://mapservices.pasda.psu.edu/server/rest/services/pasda/HIFLD_FEMA/MapServer/47 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-20T02:49:04Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: EIA's update month of the layer (2020-01), not a UTC time | none | text | 2020-01 | 0 |
| `x_objectid` | The layer's object identifier of the segment (the source's name: OBJECTID) | none | integer | 1 to 133; 133 distinct | 0 |
| `x_length_km` | The line's length on a sphere of radius 6,371.0088 km, summed over its parts | km | number | 2.74 to 2594.2; 132 distinct | 0 |
| `x_raw_sha256` | The SHA-256 of the raw GeoJSON file the row was read from | none | text | 9e3a5b3a06958a436d3ef6c34e192f11ba8824502006e9ba0b41728ca2a7256b | 0 |

### `eia_ieo_projections`

One series of EIA's International Energy Outlook 2023, reference case (a world region's energy consumption, CO2 emissions, or electricity generation or capacity by fuel), for one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 17856.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot); the release is in the entity id, vintage is not filled.
- **Source:** eia:ieo/2023 U.S. Energy Information Administration, International Energy Outlook 2023 (World Energy Projection System) (https://www.eia.gov/ieo/)
- **Method note:** [`docs/methods/eia_ieo_projections.md`](../methods/eia_ieo_projections.md)
- **Cite as:** U.S. Energy Information Administration (EIA). International Energy Outlook 2023 (tables 1, 2, 10, 20, 21, reference case). Via the Energy Research Warehouse (ERW), table `eia_ieo_projections`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_ieo2023:<tableId>:<regionId>:<seriesId> | none | text | for example eia_ieo2023:10:0-0:emi_co2_fossil_afm_mtonne, eia_ieo2023:10:0-0:emi_co2_fossil_afr_mtonne, eia_ieo2023:10:0-0:emi_co2_fossil_ame_mtonne; 576 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2020-01-01T00:00:00Z to 2050-01-01T00:00:00Z; 31 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 42297838000.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, TBtu, tCO2 | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: world regions have no ISO 3166-2 code | none | empty | no cell holds a value | 17856 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 17856 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name, <what> : <region> : <fuel> | none | text | for example Carbon dioxide emissions : Africa and Middle East, Carbon dioxide emissions : Africa and Middle East : Africa, Carbon dioxide emissions : Africa and Middle East : Middle East; 574 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:ieo/2023 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/ieo/2023/data/?api_key=REDACTED&frequency=annual&data%5B0%5D=value&facets%5Bscenario%5D%5B%5D=Reference&facets%5BtableId%5D%5B%5D=1&facets%5BtableId%5D%5B%5D=2&facets%5BtableId%5D%5B%5D=10&facets%5BtableId%5D%5B%5D=20&facets%5BtableId%5D%5B%5D=21&sort%5B0%5D%5Bcolumn%5D=tableId&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=regionId&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=seriesId&sort%5B2%5D%5Bdirection%5D=asc&sort%5B3%5D%5Bcolumn%5D=period&sort%5B3%5D%5Bdirection%5D=asc&offset=0&length=5000, https://api.eia.gov/v2/ieo/2023/data/?api_key=REDACTED&frequency=annual&data%5B0%5D=value&facets%5Bscenario%5D%5B%5D=Reference&facets%5BtableId%5D%5B%5D=1&facets%5BtableId%5D%5B%5D=2&facets%5BtableId%5D%5B%5D=10&facets%5BtableId%5D%5B%5D=20&facets%5BtableId%5D%5B%5D=21&sort%5B0%5D%5Bcolumn%5D=tableId&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=regionId&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=seriesId&sort%5B2%5D%5Bdirection%5D=asc&sort%5B3%5D%5Bcolumn%5D=period&sort%5B3%5D%5Bdirection%5D=asc&offset=10000&length=5000, https://api.eia.gov/v2/ieo/2023/data/?api_key=REDACTED&frequency=annual&data%5B0%5D=value&facets%5Bscenario%5D%5B%5D=Reference&facets%5BtableId%5D%5B%5D=1&facets%5BtableId%5D%5B%5D=2&facets%5BtableId%5D%5B%5D=10&facets%5BtableId%5D%5B%5D=20&facets%5BtableId%5D%5B%5D=21&sort%5B0%5D%5Bcolumn%5D=tableId&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=regionId&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=seriesId&sort%5B2%5D%5Bdirection%5D=asc&sort%5B3%5D%5Bcolumn%5D=period&sort%5B3%5D%5Bdirection%5D=asc&offset=15000&length=5000, https://api.eia.gov/v2/ieo/2023/data/?api_key=REDACTED&frequency=annual&data%5B0%5D=value&facets%5Bscenario%5D%5B%5D=Reference&facets%5BtableId%5D%5B%5D=1&facets%5BtableId%5D%5B%5D=2&facets%5BtableId%5D%5B%5D=10&facets%5BtableId%5D%5B%5D=20&facets%5BtableId%5D%5B%5D=21&sort%5B0%5D%5Bcolumn%5D=tableId&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=regionId&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=seriesId&sort%5B2%5D%5Bdirection%5D=asc&sort%5B3%5D%5Bcolumn%5D=period&sort%5B3%5D%5Bdirection%5D=asc&offset=5000&length=5000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T13:45:18Z, 2026-10-23T13:45:21Z, 2026-10-23T13:45:24Z, 2026-10-23T13:45:26Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: the release is in the entity id | none | empty | no cell holds a value | 17856 |
| `x_history` | EIA's flag: HISTORIC for a year EIA marks as history, PROJECTION for its model result (the source's name: history) | none | text | HISTORIC, PROJECTION | 0 |
| `x_scenario` | EIA's case of the outlook (Reference on every row) (the source's name: scenario) | none | text | Reference | 0 |
| `x_table` | EIA's name of the IEO table the series is read from (the source's name: tableName) | none | text | Installed generating capacity by region and fuel, Net electricity generation by region and fuel, World carbon dioxide emissions by region, World total primary energy consumption by region, World total primary energy consumption by region and fuel | 0 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity` | Installed generating capacity, MW (EIA's gigawatts times 1,000) | MW | 8463 | 2020-01-01T00:00:00Z | 2050-01-01T00:00:00Z |
| `consumption` | Primary energy consumption, trillion Btu (EIA's quadrillion Btu times 1,000) | TBtu | 1581 | 2020-01-01T00:00:00Z | 2050-01-01T00:00:00Z |
| `emissions` | Energy-related carbon dioxide emissions, tonnes of CO2 (EIA's million metric tons times 1,000,000) | tCO2 | 651 | 2020-01-01T00:00:00Z | 2050-01-01T00:00:00Z |
| `generation` | Net electricity generation, MWh (EIA's billion kWh times 1,000,000) | MWh | 7161 | 2020-01-01T00:00:00Z | 2050-01-01T00:00:00Z |

### `eia_international_electricity_annual`

One year's electricity figure (generation by product, consumption, trade, losses or capacity) for the U.S., Canada or Mexico, from EIA's International Energy Statistics.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 4131.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:international U.S. Energy Information Administration, International Energy Statistics (API v2, route international) (https://www.eia.gov/international/data/world)
- **Method note:** [`docs/methods/eia_international_electricity_annual.md`](../methods/eia_international_electricity_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). International Energy Statistics (API v2). Via the Energy Research Warehouse (ERW), table `eia_international_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_intl:<EIA country code CAN, MEX, USA>:<EIA product id> | none | text | for example eia_intl:CAN:116, eia_intl:CAN:117, eia_intl:CAN:2; 51 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1980-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 45 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -63800200.0 to 4392552346.23; 3273 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: The country's two-letter ISO code (CA, MX, US) | none | text | CA, MX, US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 4131 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <country>, <product> in EIA's names | none | text | for example Canada, Biomass and waste, Canada, Coal, Canada, Electricity; 51 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:international | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/international/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&start=1980&facets%5BcountryRegionId%5D%5B%5D=CAN&facets%5BcountryRegionId%5D%5B%5D=MEX&facets%5BcountryRegionId%5D%5B%5D=USA&facets%5BactivityId%5D%5B%5D=12&facets%5BactivityId%5D%5B%5D=7&facets%5BactivityId%5D%5B%5D=2&facets%5BactivityId%5D%5B%5D=3&facets%5BactivityId%5D%5B%5D=4&facets%5BactivityId%5D%5B%5D=23&facets%5BactivityId%5D%5B%5D=9&facets%5Bunit%5D%5B%5D=BKWH&facets%5Bunit%5D%5B%5D=MK | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T04:55:57Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 4131 |
| `x_data_flag` | EIA's flag on the value where it gives one (for example a value that rounds to zero) (the source's name: dataFlagDescription) | none | text | A value exists, but rounds to zero; non-rounded values appear when downloaded, Values derived using SMR estimation methodology. Appears as a superscript., Values flagged perliminary by source. Appears as a superscript. | 3816: EIA gives no flag |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity` | Generating capacity, MW (EIA's million kW times 1,000) | MW | 1355 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `consumption` | Electricity consumption, MWh | MWh | 135 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `distribution_losses` | Electricity transmission and distribution losses, MWh | MWh | 135 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `exports` | Electricity exports, MWh | MWh | 135 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `generation` | Net electricity generation from the product, MWh (EIA's billion kWh times 1,000,000) | MWh | 2101 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `imports` | Electricity imports, MWh | MWh | 135 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_imports` | Electricity net imports, MWh | MWh | 135 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_lng_exports_monthly`

One LNG export terminal's monthly export volume or export price, as EIA reports it.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1100.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Each run asks for the full history and merges it on (entity, variable, ts_utc), keeping EIA's newest value; a row EIA stops giving is kept. The copy held was rebuilt from the ERW archive by restore_tables.py. vintage is not filled.
- **Source:** eia:natural-gas/move/poe2 U.S. Natural Gas Exports and Re-Exports by Point of Exit (LNG) (https://www.eia.gov/dnav/ng/ng_move_poe2_a_EPG0_ENG_Mmcf_m.htm)
- **Method note:** [`docs/methods/eia_lng_exports_monthly.md`](../methods/eia_lng_exports_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). U.S. Natural Gas Exports and Re-Exports by Point of Exit (LNG). Via the Energy Research Warehouse (ERW), table `eia_lng_exports_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:<EIA series id>: NGM_EPG0_ENG_Y<terminal>-Z00_MMCF for a volume, NGM_EPG0_PNG_Y<terminal>-Z00_DMCF for a price | none | text | eia:NGM_EPG0_ENG_YCAM-Z00_MMCF, eia:NGM_EPG0_ENG_YCCPL-Z00_MMCF, eia:NGM_EPG0_ENG_YCPT-Z00_MMCF, eia:NGM_EPG0_ENG_YCRP-Z00_MMCF, eia:NGM_EPG0_ENG_YELBA-Z00_MMCF, eia:NGM_EPG0_ENG_YFPT-Z00_MMCF, eia:NGM_EPG0_ENG_YGPT-Z00_MMCF, eia:NGM_EPG0_ENG_YPLAQ-Z00_MMCF, eia:NGM_EPG0_ENG_YSPL-Z00_MMCF, eia:NGM_EPG0_PNG_YCAM-Z00_DMCF, eia:NGM_EPG0_PNG_YCCPL-Z00_DMCF, eia:NGM_EPG0_PNG_YCPT-Z00_DMCF, eia:NGM_EPG0_PNG_YCRP-Z00_DMCF, eia:NGM_EPG0_PNG_YELBA-Z00_DMCF, eia:NGM_EPG0_PNG_YFPT-Z00_DMCF, eia:NGM_EPG0_PNG_YPLAQ-Z00_DMCF, eia:NGM_EPG0_PNG_YSPL-Z00_DMCF | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2013-11-01T00:00:00Z to 2026-08-01T00:00:00Z; 133 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 2.49 to 141519.0; 995 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf, USD/Mcf | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1100 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: EIA's series names are in the header's Series line | none | empty | no cell holds a value | 1100 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/move/poe2 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/move/poe2/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000&facets%5Bseries%5D%5B%5D=NGM_EPG0_ENG_YSPL-Z00_MMCF&facets%5Bseries%5D%5B%5D=NGM_EPG0_ENG_YCRP-Z00_MMCF&facets%5Bseries%5D%5B%5D=NGM_EPG0_ENG_YCAM-Z00_MMCF&facets%5Bseries%5D%5B%5D=NGM_EPG0_ENG_YFPT-Z00_MMCF&facets%5Bseries%5D%5B%5D=NGM_EPG0_ENG_YCCPL-Z00_MMCF&facets%5Bseries%5D%5B%5D=NGM_EPG0_ENG_YPLAQ-Z00_MMCF&facets%5Bseries%5D%5B%5D=NGM_EPG0_ENG_YCPT-Z00_MMCF&facets%5Bseries%5D%5B%5D=NGM_EPG0_ENG_YELBA-Z00_MMCF&facets%5Bseries%5D%5B%5D=NGM_EPG0_ENG_YGPT-Z00_MMCF&facets%5Bseries%5D%5B%5D=NGM_EPG0_PNG_YSPL-Z00_DMCF&facets%5Bseries%5D%5B%5D=NGM_EPG0_PNG_YCRP-Z00_DMCF&facets%5Bseries%5D%5B%5D=NGM_EPG0_PNG_YCAM-Z00_DMCF&facets%5Bseries%5D%5B%5D=NGM_EPG0_PNG_YFPT-Z00_DMCF&facets%5Bseries%5D%5B%5D=NGM_EPG0_PNG_YCCPL-Z00_DMCF&facets%5Bseries%5D%5B%5D=NGM_EPG0_PNG_YPLAQ-Z00_DMCF&facets%5Bseries%5D%5B%5D=NGM_EPG0_PNG_YCPT-Z00_DMCF&facets%5Bseries%5D%5B%5D=NGM_EPG0_PNG_YELBA-Z00_DMCF&facets%5Bseries%5D%5B%5D=NGM_EPG0_PNG_YGPT-Z00_DMCF | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-29T00:59:51Z, 2026-09-30T19:21:32Z, 2026-10-30T14:44:36Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1100 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `export_price` | Price of the terminal's LNG exports, USD per thousand cubic feet | USD/Mcf | 455 | 2013-11-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `export_volume` | LNG exported from the terminal in the month, million cubic feet | MMcf | 645 | 2013-11-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `eia_lng_liquefaction_projects`

One train (liquefaction unit) of a U.S. LNG export project in operation, commissioning or construction, or one large approved project, from EIA's U.S. Liquefaction Capacity workbook (2026 Q3).

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 48.

- **Time:** No time column. status_date is the in-service day where EIA gives one; vintage is the workbook's last-modified time.
- **Revisions:** Rewritten whole by each run (write_snapshot) from the newest quarterly workbook.
- **Source:** eia:us_liquefaction_capacity U.S. Energy Information Administration, U.S. Liquefaction Capacity (quarterly), listed on (https://www.eia.gov/naturalgas/data.php)
- **Method note:** [`docs/methods/eia_lng_liquefaction_projects.md`](../methods/eia_lng_liquefaction_projects.md)
- **Cite as:** U.S. Energy Information Administration (EIA). U.S. Liquefaction Capacity: LNG export projects, trains and approvals (quarterly). Via the Energy Research Warehouse (ERW), table `eia_lng_liquefaction_projects`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: eia_lng:<project>:<train>, or eia_lng:<project> for an approved project | none | text | for example eia_lng:alaska_lng, eia_lng:calcasieu_pass:trains_10_18c, eia_lng:calcasieu_pass:trains_1_9c; 48 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: project on every row | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The project's name as EIA prints it, footnote letters included | none | text | for example Alaska LNG, Calcasieu Pass, Trains 1-9C, Calcasieu Pass, Trains 10-18C; 48 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> of the project's location, US for an offshore project | none | text | US, US-AK, US-GA, US-LA, US-MD, US-MS, US-TX | 0 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: Not filled | degree | empty | no cell holds a value | 48 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: Not filled | degree | empty | no cell holds a value | 48 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: Not filled: the capacities are in bcf/d and Mtpa, in x_ columns | MW | empty | no cell holds a value | 48 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: operating, under_construction or planned (approved); empty for EIA's Commissioning | none | text | operating, planned, under_construction | 4 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The in-service day where EIA gives one | none | date | 2016-02-01, 2016-08-01, 2017-01-01, 2017-08-01, 2018-03-01, 2018-11-01, 2018-12-01, 2019-05-01, 2019-07-01, 2019-09-01, 2019-12-01, 2020-03-01, 2020-05-01, 2020-08-01, 2020-12-01, 2021-12-01, 2022-03-01, 2022-09-01, 2024-12-01, 2025-02-01, 2025-09-01, 2026-04-01 | 24 |
| `operator` | The operator or owner, as the publisher writes it. Here: The operator as EIA writes it | none | text | Alaska Gasline Development Corporation (AGDC), Berkshire Hathaway BHE GT&S, Cameron LNG, LLC, Cheniere Energy, Corpus Christi Liquefaction Stage III, LLC, Corpus Christi Liquefaction, LLC, Energy Transfer, LP, Fairwood Group, Freeport LNG, Freeport LNG Development, L.P., Glenfarne Energy Transition, LLC, Gulf LNG Liquefaction Company, LLC, Kimmeridge Energy Management, Kinder Morgan, NextDecade Corporation, Qatar Petroleum, ExxonMobil, Sempra Energy, Sempra LNG, Venture Global LNG, Venture Global LNG, Inc., Woodside Energy | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:us_liquefaction_capacity | 0 |
| `x_sheet` | The workbook sheet the row is from (existing_under_construction or approved) | none | text | approved, existing_under_construction | 0 |
| `x_train` | EIA's train label (for example Train 1) (the source's name: Train) | none | text | for example Train 1, Train 1B, Train 1D; 31 distinct | 9: An approved project's row (no train) |
| `x_status` | The project's status in EIA's words (the source's name: Project status) | none | text | Commercial operation, Commissioning, Completed FEED on a new design of one larger-size train, rather than 2 trains as was initially proposed. Awarded EPC contract to Bechtel. FID TBA, Completed FEED, awarded EPC contract to Bechtel Energy, issued limited notice to proceed to commence construction, FID TBA, Completed FEED, awarded EPC contract to Kiewit Energy. FID TBA, Completed FEED, awarded EPC contract to Samsung Heavy Industries and Black & Veatch. Project was granted DOE authorization for a 5-year extension to 2029 to commence operations., Completed FEED, reviewed EPC tenders, signed a preliminary EPC contract with a consortium led by Technip Energies and KBR, FID TBAD, Completed FEED, reviewed EPC tenders, signed a preliminary EPC contract with a consortium led by Technip Energies and KBR. FID TBAD, Completed FEED, selected engineering, procurement, and construction (EPC) contractor. FID targeted for 2026., Proposed, Under Construction, Under construction, Under constructionH, Undergoing FEED | 0 |
| `x_in_service` | When the train entered or enters service: a day, a year or a half year as EIA writes it (the source's name: In-service) | none | text | for example 1H2027, 1H2029, 2016-02-01; 31 distinct | 9: An approved project's row, or EIA gives none |
| `x_commercial_operation_date` | The day the train began commercial operation | none | date | 2016-05-01, 2016-10-01, 2017-03-01, 2017-10-01, 2018-04-01, 2019-03-01, 2019-07-01, 2019-08-01, 2019-09-01, 2019-11-01, 2020-01-01, 2020-03-02, 2020-04-01, 2020-08-01, 2020-08-02, 2021-03-01, 2022-02-01, 2022-05-01, 2023-10-01 | 28: Not in commercial operation (only the operating rows have one) |
| `x_trains` | An approved project's number of trains (the source's name: Number of trains) | count | integer | 1, 2, 3 | 40: A train's row (not an approved project), or EIA gives none |
| `x_baseload_bcfd` | Baseload capacity: a train's nameplate, or for an approved project the baseload per train (the source's name: Baseload) | bcf/d | number | 0.16, 0.28, 0.39, 0.53, 0.59, 0.6, 0.61, 0.66, 0.68, 0.69, 0.71, 0.72, 0.73, 0.74, 0.85, 0.96, 1.09, 1.32, 1.58, 2.04, 2.18 | 1: EIA prints a note in place of the figure |
| `x_baseload_mtpa` | Baseload capacity in million tonnes a year (the source's name: Mtpa) | million tonnes per year | number | 1.25, 10.0, 12.0, 14.4, 16.56, 2.0, 2.98, 4.0, 4.4, 4.5, 4.52, 5.0, 5.1, 5.2, 5.25, 5.4, 5.43, 5.5, 5.52, 5.6, 6.67, 6.75, 8.4, 9.9 | 1: EIA prints a note in place of the figure |
| `x_peak_bcfd` | Peak capacity: a train's nameplate, or for an approved project its proposed design capacity in all (the source's name: Peak) | bcf/d | number | 0.22, 0.56, 0.58, 0.61, 0.66, 0.74, 0.76, 0.79, 0.8, 0.88, 0.96, 1.05, 1.1, 1.21, 1.43, 1.45, 1.78, 1.89, 1.96, 2.14, 2.17, 2.18, 2.55, 2.86 | 1: EIA prints a note in place of the figure |
| `x_peak_mtpa` | Peak capacity in million tonnes a year (the source's name: Mtpa) | million tonnes per year | number | 1.45 to 20.22; 26 distinct | 1: EIA prints a note in place of the figure |
| `x_doe_fta_bcfd` | Export quantity the Department of Energy authorized to free trade agreement countries (the source's name: DOE-authorized) | bcf/d | number | 0.25 to 3.71; 28 distinct | 0 |
| `x_doe_fta_mtpa` | DOE-authorized export quantity to free trade agreement countries, million tonnes a year (the source's name: Mtpa) | million tonnes per year | number | 2.0 to 25.28; 26 distinct | 0 |
| `x_doe_nonfta_bcfd` | DOE-authorized export quantity to countries without a free trade agreement (the source's name: DOE-authorized) | bcf/d | number | 0.21 to 2.86; 28 distinct | 0 |
| `x_doe_nonfta_mtpa` | DOE-authorized export quantity to non-free trade agreement countries, million tonnes a year (the source's name: Mtpa) | million tonnes per year | number | 1.45 to 20.22; 28 distinct | 0 |
| `x_ferc_bcfd` | Quantity the Federal Energy Regulatory Commission (FERC) authorized (the source's name: FERC-authorized) | bcf/d | number | 0.22, 0.56, 0.58, 0.61, 0.66, 0.74, 0.76, 0.79, 0.8, 0.88, 0.96, 1.1, 1.2, 1.21, 1.5, 1.55, 1.78, 1.89, 1.96, 2.14, 2.17, 2.18, 2.55, 2.86 | 1: EIA writes n/a |
| `x_ferc_mtpa` | FERC-authorized quantity, million tonnes a year (the source's name: Mtpa) | million tonnes per year | number | 1.45 to 20.22; 26 distinct | 1: EIA writes n/a |
| `x_doe_fta_docket` | The DOE docket of the free trade agreement export application, as EIA writes it (the source's name: FTA application docket) | none | text | for example 10-160-LNG/12-06-LNG, 10-85-LNG/14-92-LNG/19-125-LNG, 11-115-LNG; 26 distinct | 0 |
| `x_doe_nonfta_docket` | The DOE docket of the non-free trade agreement export application, as EIA writes it (the source's name: non-FTA application docket) | none | text | for example 10-111-LNG/15-63-LNG/19-125-LNG, 10-161-LNG/11-161-LNG/16-108-LNG/21-98-LNG, 11-128-LNG; 26 distinct | 0 |
| `x_ferc_docket` | The FERC docket, as EIA writes it (the source's name: FERC docket) | none | text | CP14-120/PF12-8, CP14-517-000/CP19-20-000/CP20-459, CP15-521-000, CP15-550, CP15-560-000/CP22-41, CP16-116, CP16-454/CP16-455, CP17-117-000/CP17-180-000, CP17-178-000, CP17-20-000, CP17-470-000, CP17-66-000 and CP17-67-000, CP18-512/CP18-514/CP26-36-000, CP19-502-000, CP20-55-000, CP22-21-000/CP22-21-001, CP23-129-000/CP26-36-000, FERC CP15-490; MARAD, PF10-24/CP11-72/CP19-515, PF11-2/CP12-509/CP15-518-000/CP21-470-000, PF12-13/ CP13-25, PF12-16/ CP13-113, PF12-3/ CP12-507/CP19-514, PF13-3/CP14-103, PF13-8/CP13-552/CP13-553/CP19-515 | 0 |
| `x_project_type` | Greenfield, Brownfield or Floating, as EIA writes it (the source's name: Project type) | none | text | Brownfield, Floating, Greenfield | 0 |
| `x_marks` | EIA's footnote marks beside a figure, as column:mark joined by semicolons (the notes are in EIA's file) | none | text | baseload_bcfd:Note A; baseload_mtpa:Note A; peak_bcfd:Note A; peak_mtpa:Note A; doe_nonfta_bcfd:B; ferc_bcfd:n/a; ferc_mtpa:n/a; trains:n/a, baseload_mtpa:^; doe_fta_mtpa:^; doe_nonfta_mtpa:^, baseload_mtpa:^; peak_mtpa:^; doe_fta_mtpa:^; doe_nonfta_mtpa:^, baseload_mtpa:^; peak_mtpa:^; doe_nonfta_mtpa:^; ferc_mtpa:^, doe_fta_mtpa:^; doe_nonfta_mtpa:^, peak_bcfd:B; doe_fta_mtpa:^; doe_nonfta_mtpa:^; ferc_bcfd:B, peak_bcfd:D; doe_fta_mtpa:^; doe_nonfta_mtpa:^; ferc_bcfd:D, peak_mtpa:^; doe_fta_mtpa:^, peak_mtpa:^; doe_fta_mtpa:^; doe_nonfta_bcfd:+; doe_nonfta_mtpa:^+, peak_mtpa:^; doe_fta_mtpa:^; doe_nonfta_bcfd:B; doe_nonfta_mtpa:^, peak_mtpa:^; doe_fta_mtpa:^; doe_nonfta_mtpa:^; ferc_mtpa:^, peak_mtpa:^; doe_nonfta_mtpa:^; ferc_mtpa:^ | 13: No figure of the row carries a mark |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/naturalgas/importsexports/liquefactioncapacity/U.S.liquefactioncapacity_2026_Q3.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:59:44Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time from EIA's server | none | utc time | 2026-10-01T20:44:22Z | 0 |

### `eia_lng_storage_annual`

One year's LNG additions to or withdrawals from storage (peak-shaving tanks, not export terminals) in the U.S. or one state.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3074.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:natural-gas/stor/lng U.S. Energy Information Administration, Natural Gas Annual, LNG additions to and withdrawals from storage (API v2, route natural-gas/stor/lng) (https://api.eia.gov/v2/natural-gas/stor/lng/)
- **Method note:** [`docs/methods/eia_lng_storage_annual.md`](../methods/eia_lng_storage_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Natural Gas Annual, LNG additions to and withdrawals from storage (API v2). Via the Energy Research Warehouse (ERW), table `eia_lng_storage_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_lng_storage:<EIA series id> | none | text | for example eia_lng_storage:NA1330_NUS_2, eia_lng_storage:NA1330_SAK_2, eia_lng_storage:NA1330_SAL_2; 81 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1969-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 46 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 127627.0; 1722 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation | none | text | for example US, US-AK, US-AL; 42 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3074 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's description | none | text | for example Alabama Natural Gas LNG Storage Additions (MMcf), Alabama Natural Gas LNG Storage Withdrawals (MMcf), Alaska  Natural Gas LNG Storage Withdrawals (MMcf); 81 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/stor/lng | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/stor/lng/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=SLI&facets%5Bprocess%5D%5B%5D=SLW&start=1969 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T05:32:01Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3074 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `additions` | LNG added to storage (SLI), million cubic feet | MMcf | 1502 | 1969-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `withdrawals` | LNG withdrawn from storage (SLW), million cubic feet | MMcf | 1572 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_mecs_manufacturing`

One industry's (by NAICS code, or all manufacturing) figure in the nation or one census region, from EIA's 2022 Manufacturing Energy Consumption Survey (fuel consumption by source, or an electricity component).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 5363.

- **Time:** ts_utc is 1 January of the survey year (2022) at 00:00:00Z (freq P1Y).
- **Revisions:** Written whole each run (write_snapshot) from the saved workbooks; EIA's revision is taken only when the saved copy is gone. vintage is each workbook's last-modified time.
- **Source:** eia:mecs U.S. Energy Information Administration, 2022 Manufacturing Energy Consumption Survey (Form EIA-846) (https://www.eia.gov/consumption/manufacturing/data/2022/)
- **Method note:** [`docs/methods/eia_mecs_manufacturing.md`](../methods/eia_mecs_manufacturing.md)
- **Cite as:** U.S. Energy Information Administration (EIA). 2022 Manufacturing Energy Consumption Survey (MECS), Tables 3.2, 11.1 and 11.3. Via the Energy Research Warehouse (ERW), table `eia_mecs_manufacturing`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: mecs:<region>_<naics>, region us, northeast, midwest, south or west; naics the code or total | none | text | for example mecs:midwest_311, mecs:midwest_3112, mecs:midwest_311221; 405 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2022-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1.0 to 932709000.0; 1251 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, TBtu | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US for the nation; empty for a census region (no single ISO code) | none | text | US | 4217 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5363 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The industry as the table names it | none | text | for example Aerospace Product and Parts, Aircraft, All Other Basic Organic Chemical Manufacturing; 82 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:mecs | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/consumption/manufacturing/data/2022/xls/Table11_1.xlsx, https://www.eia.gov/consumption/manufacturing/data/2022/xls/Table11_3.xlsx, https://www.eia.gov/consumption/manufacturing/data/2022/xls/Table3_2.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:28:00Z, 2026-10-23T18:28:02Z, 2026-10-23T18:28:03Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time from EIA's server | none | utc time | 2025-07-28T15:37:19Z, 2025-07-28T15:43:31Z, 2026-02-27T15:15:37Z | 0 |
| `x_naics` | The industry's NAICS code (North American Industry Classification System), or total for all manufacturing | none | text | for example 311, 3112, 311221; 81 distinct | 0 |
| `x_region` | The region as the table names it (Total United States or a census region) | none | text | Midwest Census Region, Northeast Census Region, South Census Region, Total United States, West Census Region | 0 |
| `x_table` | The MECS table the figure is read from (Table 3.2, 11.1 or 11.3) | none | text | Table 11.1, Table 11.3, Table 3.2 | 0 |
| `x_mark` | The letter EIA prints beside the figure: h where EIA marks it revised data | none | text | h | 5353: EIA prints no mark beside the figure |

Variables (18):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `elec_net_demand` | Net demand for electricity (purchases plus transfers in plus onsite generation less sales and transfers offsite), MWh (Table 11.1) | MWh | 394 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `elec_onsite_generation` | Electricity generated onsite, MWh (Table 11.1) | MWh | 315 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `elec_purchases` | Electricity purchased, MWh (Table 11.1, million kWh times 1,000) | MWh | 397 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `elec_sales_transfers_offsite` | Electricity sold or transferred offsite, MWh (Table 11.1) | MWh | 331 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `elec_transfers_in` | Electricity transferred in, MWh (Table 11.1) | MWh | 366 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `fuel_coal` | Coal consumed as fuel, trillion Btu (Table 3.2) | TBtu | 382 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `fuel_coke_and_breeze` | Coke and breeze consumed as fuel, trillion Btu (Table 3.2) | TBtu | 391 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `fuel_distillate_fuel_oil` | Distillate fuel oil consumed as fuel, trillion Btu (Table 3.2) | TBtu | 124 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `fuel_hgl` | Hydrocarbon gas liquids consumed as fuel, trillion Btu (Table 3.2) | TBtu | 78 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `fuel_hydrogen` | Hydrogen consumed as fuel, trillion Btu (Table 3.2; national only, inside other in a region) | TBtu | 50 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `fuel_natural_gas` | Natural gas consumed as fuel, trillion Btu (Table 3.2) | TBtu | 367 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `fuel_net_electricity` | Net electricity consumed as fuel, trillion Btu (Table 3.2) | TBtu | 348 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `fuel_other` | Other fuels consumed, trillion Btu (Table 3.2) | TBtu | 203 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `fuel_residual_fuel_oil` | Residual fuel oil consumed as fuel, trillion Btu (Table 3.2) | TBtu | 340 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `fuel_total` | Total fuel consumption of the industry, trillion Btu (Table 3.2) | TBtu | 372 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `gen_cogeneration` | Onsite generation by cogeneration, MWh (Table 11.3) | MWh | 324 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `gen_other` | Other onsite generation, MWh (Table 11.3) | MWh | 294 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `gen_renewable` | Onsite generation from renewables other than wood and other biomass, MWh (Table 11.3) | MWh | 287 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |

### `eia_meters_state_annual`

One state's (or the nation's) yearly count of electricity meters of one technology in one sector.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 8578.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:electricity/state-electricity-profiles/meters U.S. Energy Information Administration, State Electricity Profiles, advanced metering (API v2, route electricity/state-electricity-profiles/meters) (https://www.eia.gov/electricity/state/)
- **Method note:** [`docs/methods/eia_meters_state_annual.md`](../methods/eia_meters_state_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). State Electricity Profiles, advanced metering (API v2). Via the Energy Research Warehouse (ERW), table `eia_meters_state_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_meters:<state>:<technology slug>:<sector>; technologies all_meters, advanced_meter_infrastructure, automatic_meter_reading, standard_meters; sectors RES, COM, IND, TRN, TOT | none | text | for example eia_meters:AK:advanced_meter_infrastructure:COM, eia_meters:AK:advanced_meter_infrastructure:IND, eia_meters:AK:advanced_meter_infrastructure:RES; 1040 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 168085999.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 8578 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's names of state, technology and sector | none | text | for example Alabama, Advanced Meter Infrastructure, all sectors, Alabama, Advanced Meter Infrastructure, commercial, Alabama, Advanced Meter Infrastructure, industrial; 1040 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:electricity/state-electricity-profiles/meters | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/electricity/state-electricity-profiles/meters/data/?api_key=REDACTED&frequency=annual&data%5B%5D=meters&start=2013 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T23:48:23Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 8578 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `meters` | Number of electricity meters of the technology in the sector; a sum takes one level | count | 8578 | 2013-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_net_imports_monthly`

One month's U.S. net imports (imports less exports) of crude oil, petroleum products or both with one partner country, group or the world.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 65501.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/move/neti U.S. Energy Information Administration, Petroleum Supply Monthly, U.S. net imports by country (API v2, route petroleum/move/neti) (https://www.eia.gov/dnav/pet/pet_move_neti_a_ep00_imn_mbblpd_m.htm)
- **Method note:** [`docs/methods/eia_net_imports_monthly.md`](../methods/eia_net_imports_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Petroleum Supply Monthly, U.S. net imports by country (API v2). Via the Energy Research Warehouse (ERW), table `eia_net_imports_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_net_imports:<EIA series id> | none | text | for example eia_net_imports:ESM_EP00_IMN_NUS-NSS_MBBLD, eia_net_imports:ESM_EPC0_IMN_NUS-NSS_MBBLD, eia_net_imports:ESM_EPP0_IMN_NUS-NSS_MBBLD; 530 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 199 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -6844.0 to 10159.0; 3640 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl/d | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row (the importer) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 65501 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series description | none | text | for example U.S. Net Imports from Afghanistan of Crude Oil and Petroleum Products (Thousand Barrels per Day), U.S. Net Imports from Afghanistan of Total Petroleum Products (Thousand Barrels per Day), U.S. Net Imports from Albania of Crude Oil (Thousand Barrels per Day); 530 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/move/neti | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/move/neti/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bproduct%5D%5B%5D=EP00&facets%5Bproduct%5D%5B%5D=EPC0&facets%5Bproduct%5D%5B%5D=EPP0&start=2010-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T10:42:54Z, 2026-10-24T10:42:58Z, 2026-10-24T10:43:02Z, 2026-10-24T10:43:06Z, 2026-10-24T10:43:11Z, 2026-10-24T10:43:15Z, 2026-10-24T10:43:20Z, 2026-10-24T10:43:24Z, 2026-10-24T10:43:28Z, 2026-10-24T10:43:33Z, 2026-10-24T10:43:37Z, 2026-10-24T10:43:41Z, 2026-10-24T10:43:46Z, 2026-10-24T10:43:50Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 65501 |
| `x_partner` | The trading partner: its ISO 3166 three-letter code as EIA gives it, or EIA's area code for the world (NUS-Z00), a group (OPEC, non-OPEC, Persian Gulf) or a country EIA gives no three-letter code (the source's name: duoarea) | none | text | for example ABW, AFG, AGO; 208 distinct | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `net_imports_crude` | Net imports of crude oil from the partner, thousand barrels a day (negative a net export) | kbbl/d | 8061 | 2010-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_imports_crude_and_products` | Net imports of crude oil and petroleum products from the partner, thousand barrels a day (negative a net export) | kbbl/d | 28828 | 2010-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_imports_products` | Net imports of petroleum products from the partner, thousand barrels a day (negative a net export) | kbbl/d | 28612 | 2010-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_net_metering_state_annual`

One state's (or the nation's) yearly net-metered capacity or customers (customers who generate their own power and are credited for what they send to the grid) of one technology in one sector.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 16226.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:electricity/state-electricity-profiles/net-metering U.S. Energy Information Administration, State Electricity Profiles, net metering (API v2, route electricity/state-electricity-profiles/net-metering) (https://www.eia.gov/electricity/state/)
- **Method note:** [`docs/methods/eia_net_metering_state_annual.md`](../methods/eia_net_metering_state_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). State Electricity Profiles, net metering (API v2). Via the Energy Research Warehouse (ERW), table `eia_net_metering_state_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_net_metering:<state>:<technology slug>:<sector>; technologies all_technologies, and for 2013 to 2019 photovoltaic, wind, other_technologies; sectors RES, COM, IND, TRN, TOT | none | text | for example eia_net_metering:AK:all_technologies:COM, eia_net_metering:AK:all_technologies:IND, eia_net_metering:AK:all_technologies:RES; 1031 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 5418553.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 16226 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's names of state, technology and sector | none | text | for example Alabama, All Technologies, all sectors, Alabama, All Technologies, commercial, Alabama, All Technologies, industrial; 1031 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:electricity/state-electricity-profiles/net-metering | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/electricity/state-electricity-profiles/net-metering/data/?api_key=REDACTED&frequency=annual&data%5B%5D=capacity&data%5B%5D=customers&start=2013 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T21:48:23Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 16226 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity` | Net-metered generating capacity, MW | MW | 8118 | 2013-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `customers` | Number of net-metered customers | count | 8108 | 2013-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_ngl_production_monthly`

One month's natural gas plant field production of one natural gas liquid in the U.S., a PADD or a refining district, in the month or per day.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 110896.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/pnp/gp U.S. Energy Information Administration, Petroleum Supply Monthly, natural gas plant field production (API v2, route petroleum/pnp/gp) (https://www.eia.gov/dnav/pet/pet_pnp_gp_dc_nus_mbbl_m.htm)
- **Method note:** [`docs/methods/eia_ngl_production_monthly.md`](../methods/eia_ngl_production_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Petroleum Supply Monthly, natural gas plant field production (API v2). Via the Energy Research Warehouse (ERW), table `eia_ngl_production_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_ngl_production:<EIA series id> | none | text | for example eia_ngl_production:MLPFP2A1, eia_ngl_production:MLPFP2A2, eia_ngl_production:MLPFP2B1; 284 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1973-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 643 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -3528.0 to 247591.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl, kbbl/d | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, the PADDs and districts included | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 110896 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name (the product and area) | none | text | for example East Coast (PADD 1) Field Production  of Condensate and Scrubber Oil  (Thousand Barrels per Day), East Coast (PADD 1) Field Production  of Condensate and Scrubber Oil  (Thousand Barrels), East Coast (PADD 1) Field Production of Ethane (Thousand Barrels per Day); 283 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/pnp/gp | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/pnp/gp/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=FPF&start=1973-01&end=2014-12, https://api.eia.gov/v2/petroleum/pnp/gp/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=FPF&start=2015-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-22T06:55:02Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 110896 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `field_production` | Natural gas plant field production of the liquid in the month, thousand barrels | kbbl | 55400 | 1981-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `field_production_per_day` | Natural gas plant field production of the liquid, thousand barrels a day | kbbl/d | 55496 | 1973-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_nuclear_outages_daily`

One day's U.S. nuclear fleet capacity, capacity on outage, or share on outage, EIA's estimate from the NRC's daily power reactor status reports.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 21702.

- **Time:** ts_utc is the day at 00:00:00Z (freq P1D), a date.
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:nuclear-outages/us-nuclear-outages U.S. Energy Information Administration, Status of U.S. Nuclear Outages (API v2) (https://www.eia.gov/nuclear/outages/)
- **Method note:** [`docs/methods/eia_nuclear_outages.md`](../methods/eia_nuclear_outages.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Status of U.S. Nuclear Outages (API v2, daily). Via the Energy Research Warehouse (ERW), table `eia_nuclear_outages_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_nuclear_outages:US | none | text | eia_nuclear_outages:US | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2007-01-01T00:00:00Z to 2026-10-21T00:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0007 to 104182.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 21702 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: U.S. nuclear fleet | none | text | U.S. nuclear fleet | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:nuclear-outages/us-nuclear-outages | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/nuclear-outages/us-nuclear-outages/data/?api_key=REDACTED&frequency=daily&data%5B%5D=capacity&data%5B%5D=outage&data%5B%5D=percentOutage&start=2007-01-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T19:39:31Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 21702 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity` | Nuclear generating capacity, MW | MW | 7234 | 2007-01-01T00:00:00Z | 2026-10-21T00:00:00Z |
| `outage` | Capacity on outage that day, MW | MW | 7234 | 2007-01-01T00:00:00Z | 2026-10-21T00:00:00Z |
| `outage_share` | Share of capacity on outage, a ratio (EIA's percent divided by 100) | ratio | 7234 | 2007-01-01T00:00:00Z | 2026-10-21T00:00:00Z |

### `eia_nuclear_outages_facility_daily`

One nuclear plant's day of capacity, capacity on outage, or share on outage, EIA's estimate from the NRC's daily power reactor status reports.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1312872.

- **Time:** ts_utc is the day at 00:00:00Z (freq P1D), a date.
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:nuclear-outages/facility-nuclear-outages U.S. Energy Information Administration, Status of U.S. Nuclear Outages (API v2) (https://www.eia.gov/nuclear/outages/)
- **Method note:** [`docs/methods/eia_nuclear_outages.md`](../methods/eia_nuclear_outages.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Status of U.S. Nuclear Outages, by plant (API v2, daily). Via the Energy Research Warehouse (ERW), table `eia_nuclear_outages_facility_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_nuclear_outages:<facility>, EIA's plant id | none | text | for example eia_nuclear_outages:1060, eia_nuclear_outages:1590, eia_nuclear_outages:1715; 66 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2007-01-01T00:00:00Z to 2026-10-21T00:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 4530.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1312872 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The plant's name | none | text | for example Arkansas Nuclear One, Beaver Valley, Braidwood Generation Station; 66 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:nuclear-outages/facility-nuclear-outages | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/nuclear-outages/facility-nuclear-outages/data/?api_key=REDACTED&frequency=daily&data%5B%5D=capacity&data%5B%5D=outage&data%5B%5D=percentOutage&start=2007-01-01&end=2014-12-31, https://api.eia.gov/v2/nuclear-outages/facility-nuclear-outages/data/?api_key=REDACTED&frequency=daily&data%5B%5D=capacity&data%5B%5D=outage&data%5B%5D=percentOutage&start=2015-01-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T20:54:58Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1312872 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity` | The plant's nuclear generating capacity, MW | MW | 437624 | 2007-01-01T00:00:00Z | 2026-10-21T00:00:00Z |
| `outage` | The plant's capacity on outage that day, MW | MW | 437624 | 2007-01-01T00:00:00Z | 2026-10-21T00:00:00Z |
| `outage_share` | Share of the plant's capacity on outage, a ratio (EIA's percent divided by 100) | ratio | 437624 | 2007-01-01T00:00:00Z | 2026-10-21T00:00:00Z |

### `eia_nuclear_outages_generator_daily`

One nuclear reactor's day of capacity, capacity on outage, or share on outage, EIA's estimate from the NRC's daily power reactor status reports.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2149671.

- **Time:** ts_utc is the day at 00:00:00Z (freq P1D), a date.
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:nuclear-outages/generator-nuclear-outages U.S. Energy Information Administration, Status of U.S. Nuclear Outages (API v2) (https://www.eia.gov/nuclear/outages/)
- **Method note:** [`docs/methods/eia_nuclear_outages.md`](../methods/eia_nuclear_outages.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Status of U.S. Nuclear Outages, by reactor (API v2, daily). Via the Energy Research Warehouse (ERW), table `eia_nuclear_outages_generator_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_nuclear_outages_gen:<facility>:<generator>, EIA's plant and reactor ids | none | text | for example eia_nuclear_outages_gen:1060:1, eia_nuclear_outages_gen:1590:1, eia_nuclear_outages_gen:1715:1; 107 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2007-01-01T00:00:00Z to 2026-11-19T00:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 1463.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2149671 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The plant's name and the reactor | none | text | for example Arkansas Nuclear One, reactor 1, Arkansas Nuclear One, reactor 2, Beaver Valley, reactor 1; 107 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:nuclear-outages/generator-nuclear-outages | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/nuclear-outages/generator-nuclear-outages/data/?api_key=REDACTED&frequency=daily&data%5B%5D=capacity&data%5B%5D=outage&data%5B%5D=percentOutage&start=2007-01-01&end=2014-12-31, https://api.eia.gov/v2/nuclear-outages/generator-nuclear-outages/data/?api_key=REDACTED&frequency=daily&data%5B%5D=capacity&data%5B%5D=outage&data%5B%5D=percentOutage&start=2015-01-01, https://api.eia.gov/v2/nuclear-outages/generator-nuclear-outages/data/?api_key=REDACTED&frequency=daily&data%5B%5D=capacity&data%5B%5D=outage&data%5B%5D=percentOutage&start=2026-10-22, https://api.eia.gov/v2/nuclear-outages/generator-nuclear-outages/data/?api_key=REDACTED&frequency=daily&data%5B%5D=capacity&data%5B%5D=outage&data%5B%5D=percentOutage&start=2026-11-13, https://api.eia.gov/v2/nuclear-outages/generator-nuclear-outages/data/?api_key=REDACTED&frequency=daily&data%5B%5D=capacity&data%5B%5D=outage&data%5B%5D=percentOutage&start=2026-11-14, https://api.eia.gov/v2/nuclear-outages/generator-nuclear-outages/data/?api_key=REDACTED&frequency=daily&data%5B%5D=capacity&data%5B%5D=outage&data%5B%5D=percentOutage&start=2026-11-17, https://api.eia.gov/v2/nuclear-outages/generator-nuclear-outages/data/?api_key=REDACTED&frequency=daily&data%5B%5D=capacity&data%5B%5D=outage&data%5B%5D=percentOutage&start=2026-11-18, https://api.eia.gov/v2/nuclear-outages/generator-nuclear-outages/data/?api_key=REDACTED&frequency=daily&data%5B%5D=capacity&data%5B%5D=outage&data%5B%5D=percentOutage&start=2026-11-19 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T22:33:55Z, 2026-11-12T16:41:37Z, 2026-11-13T18:16:36Z, 2026-11-16T18:52:20Z, 2026-11-17T17:43:12Z, 2026-11-18T17:50:44Z, 2026-11-19T17:51:46Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2149671 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity` | The reactor's generating capacity, MW | MW | 716557 | 2007-01-01T00:00:00Z | 2026-11-19T00:00:00Z |
| `outage` | The reactor's capacity on outage that day, MW | MW | 716557 | 2007-01-01T00:00:00Z | 2026-11-19T00:00:00Z |
| `outage_share` | Share of the reactor's capacity on outage, a ratio (EIA's percent divided by 100) | ratio | 716557 | 2007-01-01T00:00:00Z | 2026-11-19T00:00:00Z |

### `eia_oxygenate_production_monthly`

One month's oxygenate plant production (fuel ethanol, MTBE and other oxygenates) or biofuels plant net production in the U.S. or a PADD, in the month or per day.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 6006.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/pnp/oxy U.S. Energy Information Administration, Petroleum Supply Monthly, oxygenate plant production (API v2, route petroleum/pnp/oxy) (https://www.eia.gov/dnav/pet/pet_pnp_oxy_dc_nus_mbbl_m.htm)
- **Method note:** [`docs/methods/eia_oxygenate_production_monthly.md`](../methods/eia_oxygenate_production_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Petroleum Supply Monthly, oxygenate plant production (API v2). Via the Energy Research Warehouse (ERW), table `eia_oxygenate_production_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_oxygenate_production:<EIA series id> | none | text | for example eia_oxygenate_production:M_EPOOXE_YOP_NUS_1, eia_oxygenate_production:M_EPOOXE_YOP_NUS_2, eia_oxygenate_production:M_EPOOXE_YOP_R10_1; 30 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1981-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 547 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 34934.0; 1940 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl, kbbl/d | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, the PADDs included | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 6006 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name (the product and area) | none | text | for example East Coast (PADD 1) Oxygenate Plant Production of Fuel Ethanol (Thousand Barrels per Day), East Coast (PADD 1) Oxygenate Plant Production of Fuel Ethanol (Thousand Barrels), East Coast (PADD 1) Oxygenate Plant Production of MTBE (Thousand Barrels per Day); 30 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/pnp/oxy | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/pnp/oxy/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=YOP&facets%5Bprocess%5D%5B%5D=YNP&start=1981-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-22T05:07:00Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 6006 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `biofuels_plant_net_production` | Biofuels plant net production (YNP) in the month, thousand barrels | kbbl | 297 | 2010-01-01T00:00:00Z | 2025-12-01T00:00:00Z |
| `biofuels_plant_net_production_per_day` | Biofuels plant net production (YNP), thousand barrels a day | kbbl/d | 297 | 2010-01-01T00:00:00Z | 2025-12-01T00:00:00Z |
| `oxygenate_plant_production` | Oxygenate plant production (YOP) in the month, thousand barrels | kbbl | 2712 | 1981-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `oxygenate_plant_production_per_day` | Oxygenate plant production (YOP), thousand barrels a day | kbbl/d | 2700 | 1981-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_padd_crude_pipeline_flows`

One month's crude oil received by pipeline in one PADD from another PADD, as EIA reports it.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 4566.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Each run asks for the full history and merges it on (entity, variable, ts_utc), keeping EIA's newest value; a row EIA stops giving is kept. The copy held was rebuilt from the ERW archive by restore_tables.py. vintage is not filled.
- **Source:** eia:petroleum/move/pipe Movements by Pipeline between PAD Districts (crude oil) (https://www.eia.gov/dnav/pet/pet_move_pipe_dc_r10-r20_mbbl_m.htm)
- **Method note:** [`docs/methods/eia_padd_crude_pipeline_flows.md`](../methods/eia_padd_crude_pipeline_flows.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Movements by Pipeline between PAD Districts (crude oil). Via the Energy Research Warehouse (ERW), table `eia_padd_crude_pipeline_flows`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:<EIA series id> | none | text | eia:MCRMPP1P21, eia:MCRMPP2P11, eia:MCRMPP2P31, eia:MCRMPP2P41, eia:MCRMPP3P11, eia:MCRMPP3P21, eia:MCRMPP3P41, eia:MCRMPP3P51, eia:MCRMPP4P21, eia:MCRMP_R10-R30_1, eia:MCRMP_R40-R30_1 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1986-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 488 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 71416.0; 2493 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 4566 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: EIA's series names are in the header's Series line | none | empty | no cell holds a value | 4566 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/move/pipe | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/move/pipe/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000&facets%5Bproduct%5D%5B%5D=EPC0 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-29T00:59:52Z, 2026-09-30T19:21:35Z, 2026-11-05T23:10:46Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 4566 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `pipeline_receipts` | Crude oil received by pipeline in the receiving PADD from the PADD the series names, thousand barrels in the month | kbbl | 4566 | 1986-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `eia_padd_rail_barge_movements_monthly`

One month's movement of crude oil or a petroleum product into one PADD from another, by rail or by tanker and barge.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 120742.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/move/rail U.S. Energy Information Administration, Petroleum Supply Monthly, receipts by rail between PADDs (API v2, route petroleum/move/rail) (https://www.eia.gov/petroleum/supply/monthly/)
- **Source:** eia:petroleum/move/tb U.S. Energy Information Administration, Petroleum Supply Monthly, movements by tanker and barge between PADDs (API v2, route petroleum/move/tb) (https://www.eia.gov/petroleum/supply/monthly/)
- **Method note:** [`docs/methods/eia_padd_rail_barge_movements_monthly.md`](../methods/eia_padd_rail_barge_movements_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Petroleum Supply Monthly, movements by tanker and barge between PADDs (API v2); Petroleum Supply Monthly, receipts by rail between PADDs (API v2). Via the Energy Research Warehouse (ERW), table `eia_padd_rail_barge_movements_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_padd_movements:<EIA series id>; EIA's area pair is <receiving>-<origin> | none | text | for example eia_padd_movements:ESM_EPC0_RAIL_R10-R20_MBBL, eia_padd_movements:ESM_EPC0_RAIL_R10-R30_MBBL, eia_padd_movements:ESM_EPC0_RAIL_R10-R40_MBBL; 689 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1986-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 487 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 36053.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 120742 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name (receiving area, area of origin, product) | none | text | for example Central Atlantic (PADD 1B) Movements by Tanker and Barge from  Gulf Coast (PADD III) of Motor Gasoline Blending Components, RBOB (Thousand Barrels), Central Atlantic (PADD 1B) Movements by Tanker and Barge from  Gulf Coast (PADD III) of Motor Gasoline, Finished, Conventional, Ed55 and Lower (Thousand Barrels), Central Atlantic (PADD 1B) Receipts by Tanker and Barge from Gulf Coast (PADD 3) of Asphalt and Road Oil (Thousand Barrels); 689 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/move/rail, eia:petroleum/move/tb | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/move/rail/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&start=2010-01, https://api.eia.gov/v2/petroleum/move/tb/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&start=1986-01&end=2009-12, https://api.eia.gov/v2/petroleum/move/tb/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&start=2010-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-22T03:50:28Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 120742 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `rail_receipts` | Receipts by rail in the receiving area from the area of origin, thousand barrels in the month | kbbl | 20406 | 2010-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `tanker_barge_receipts` | Movements by tanker and barge into the receiving area from the area of origin, thousand barrels in the month | kbbl | 100336 | 1986-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_petroleum_exports_by_destination`

One month's U.S. exports of crude oil or one petroleum product to one destination country, in the month or per day.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 112478.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/move/expc U.S. Energy Information Administration, Petroleum Supply Monthly, exports by destination (API v2, route petroleum/move/expc) (https://www.eia.gov/dnav/pet/pet_move_expc_a_EP00_EEX_mbblpd_m.htm)
- **Method note:** [`docs/methods/eia_petroleum_exports_by_destination.md`](../methods/eia_petroleum_exports_by_destination.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Petroleum Supply Monthly, exports by destination (API v2). Via the Energy Research Warehouse (ERW), table `eia_petroleum_exports_by_destination`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_petroleum_exports:<EIA destination code>:<product>; products are part of EPP0's total, so a sum leaves EPP0 out | none | text | for example eia_petroleum_exports:NUS-NAA:EPC0, eia_petroleum_exports:NUS-NAA:EPD0, eia_petroleum_exports:NUS-NAA:EPJK; 1145 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 139 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 243478.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl, kbbl/d | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row (the exporter) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 112478 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The destination and product as EIA names them | none | text | for example ABW, Crude Oil, ABW, Distillate Fuel Oil, ABW, Ethane; 1098 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/move/expc | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/move/expc/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&start=2015-01&facets%5Bproduct%5D%5B%5D=EPC0&facets%5Bproduct%5D%5B%5D=EPP0, https://api.eia.gov/v2/petroleum/move/expc/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&start=2015-01&facets%5Bproduct%5D%5B%5D=EPD0&facets%5Bproduct%5D%5B%5D=EPM0F&facets%5Bproduct%5D%5B%5D=EPJK&facets%5Bproduct%5D%5B%5D=EPLLPA&facets%5Bproduct%5D%5B%5D=EPPR&facets%5Bproduct%5D%5B%5D=EPLLEA&facets%5Bproduct%5D%5B%5D=EPPC | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T02:15:57Z, 2026-10-23T02:16:02Z, 2026-10-23T02:16:06Z, 2026-10-23T02:16:11Z, 2026-10-23T02:16:16Z, 2026-10-23T02:16:20Z, 2026-10-23T02:16:25Z, 2026-10-23T02:16:30Z, 2026-10-23T02:16:34Z, 2026-10-23T02:16:39Z, 2026-10-23T04:41:53Z, 2026-10-23T04:41:58Z, 2026-10-23T04:42:03Z, 2026-10-23T04:42:08Z, 2026-10-23T04:42:13Z, 2026-10-23T04:42:17Z, 2026-10-23T04:42:22Z, 2026-10-23T04:42:27Z, 2026-10-23T04:42:32Z, 2026-10-23T04:42:37Z, 2026-10-23T04:42:41Z, 2026-10-23T04:42:46Z, 2026-10-23T04:42:51Z, 2026-10-23T04:42:56Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 112478 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `exports` | Exports of the product to the destination in the month, thousand barrels | kbbl | 56239 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `exports_per_day` | Exports of the product to the destination, thousand barrels a day | kbbl/d | 56239 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_petroleum_snd_monthly`

One month's supply or disposition figure (production, inputs, trade, stocks, product supplied) of crude oil or one petroleum product in the U.S. or a PADD, from EIA's Petroleum Supply Monthly.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 523835.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M); a stock is at the month's end.
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/sum/snd U.S. Energy Information Administration, Petroleum Supply Monthly, supply and disposition (API v2, route petroleum/sum/snd) (https://www.eia.gov/petroleum/supply/monthly/)
- **Method note:** [`docs/methods/eia_petroleum_snd_monthly.md`](../methods/eia_petroleum_snd_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Petroleum Supply Monthly, supply and disposition (API v2). Via the Energy Research Warehouse (ERW), table `eia_petroleum_snd_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_petroleum_snd:<EIA series id>; EP00 the total holds the other products | none | text | for example eia_petroleum_snd:MAPEXP11, eia_petroleum_snd:MAPEXP12, eia_petroleum_snd:MAPEXP21; 4459 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 139 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -104876.0 to 2113726.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl, kbbl/d | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, the PADDs included | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 523835 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name | none | text | for example East Coast (PADD 1) Asphalt and Road Oil Stock Change (Thousand Barrels per Day), East Coast (PADD 1) Asphalt and Road Oil Stock Change (Thousand Barrels), East Coast (PADD 1) Aviation Gasoline Stock Change (Thousand Barrels per Day); 4455 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/sum/snd | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/sum/snd/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bproduct%5D%5B%5D=EP00&facets%5Bproduct%5D%5B%5D=EPC0&facets%5Bproduct%5D%5B%5D=EPM0F&facets%5Bproduct%5D%5B%5D=EPD0&facets%5Bproduct%5D%5B%5D=EPJK&facets%5Bproduct%5D%5B%5D=EPLLPA&facets%5Bproduct%5D%5B%5D=EPPR&facets%5Bproduct%5D%5B%5D=EPOOXE&start=2015-01, https://api.eia.gov/v2/petroleum/sum/snd/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bproduct%5D%5B%5D=EPL0&facets%5Bproduct%5D%5B%5D=EPOL&facets%5Bproduct%5D%5B%5D=EPLLNG&facets%5Bproduct%5D%5B%5D=EPP2&facets%5Bproduct%5D%5B%5D=EPOO&facets%5Bproduct%5D%5B%5D=EPOOR&facets%5Bproduct%5D%5B%5D=EPOBG&facets%5Bproduct%5D%5B%5D=EPOBGC0&facets%5Bproduct%5D%5B%5D=EPM0C&facets%5Bproduct%5D%5B%5D=EPDXL0&start=2015-01, https://api.eia.gov/v2/petroleum/sum/snd/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bproduct%5D%5B%5D=EPOORXFE&facets%5Bproduct%5D%5B%5D=EPOBGR0&facets%5Bproduct%5D%5B%5D=EPPCM&facets%5Bproduct%5D%5B%5D=EPD00H&facets%5Bproduct%5D%5B%5D=EPDM10&facets%5Bproduct%5D%5B%5D=EPPM&facets%5Bproduct%5D%5B%5D=EPPP0&facets%5Bproduct%5D%5B%5D=EPLOLE&facets%5Bproduct%5D%5B%5D=EPPW&facets%5Bproduct%5D%5B%5D=EPLLPY&facets%5Bproduct%5D%5B%5D=EPOOXXFE&facets%5Bproduct%5D%5B%5D=EPPPO&facets%5Bproduct%5D%5B%5D=EPLLBYN&facets%5Bproduct%5D%5B%5D=EPLLCS&facets%5Bproduct%5D%5B%5D=EPOORO&facets%5Bproduct%5D%5B%5D=EPM0R&facets%5Bproduct%5D%5B%5D=EPPRY&start=2015-01, https://api.eia.gov/v2/petroleum/sum/snd/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bproduct%5D%5B%5D=EPPK&facets%5Bproduct%5D%5B%5D=EPPV&facets%5Bproduct%5D%5B%5D=EPPA&facets%5Bproduct%5D%5B%5D=EPPC&facets%5Bproduct%5D%5B%5D=EPPL&facets%5Bproduct%5D%5B%5D=EPL2&facets%5Bproduct%5D%5B%5D=EPLLEA&facets%5Bproduct%5D%5B%5D=EPLLBAN&facets%5Bproduct%5D%5B%5D=EPLLBAI&facets%5Bproduct%5D%5B%5D=EPPU&facets%5Bproduct%5D%5B%5D=EPOORDB&facets%5Bproduct%5D%5B%5D=EPOORDO&start=2015-01, https://api.eia.gov/v2/petroleum/sum/snd/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bproduct%5D%5B%5D=EPPNS&facets%5Bproduct%5D%5B%5D=EPPPN&facets%5Bproduct%5D%5B%5D=EPPRH&facets%5Bproduct%5D%5B%5D=EPPRX&facets%5Bproduct%5D%5B%5D=EPLLBYI&facets%5Bproduct%5D%5B%5D=EPLLEY&facets%5Bproduct%5D%5B%5D=EPOBV&facets%5Bproduct%5D%5B%5D=EPOOOXH&facets%5Bproduct%5D%5B%5D=EPOOOH&facets%5Bproduct%5D%5B%5D=EPPCC&facets%5Bproduct%5D%5B%5D=EPPS&start=2015-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-22T02:33:32Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 523835 |

Variables (23):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `ending_stocks` | Ending stocks (SAE) at the month's end, thousand barrels | kbbl | 40018 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `exports` | Exports (EEX) in the month, thousand barrels | kbbl | 27415 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `exports_per_day` | Exports (EEX), thousand barrels a day | kbbl/d | 27416 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `field_production` | Field production (FPF) in the month, thousand barrels | kbbl | 7670 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `field_production_per_day` | Field production (FPF), thousand barrels a day | kbbl/d | 7670 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `imports` | Imports (IM0) in the month, thousand barrels | kbbl | 27007 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `imports_per_day` | Imports (IM0), thousand barrels a day | kbbl/d | 27007 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_receipts` | Net receipts from other PADDs (VNR) in the month, thousand barrels | kbbl | 24049 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_receipts_per_day` | Net receipts from other PADDs (VNR), thousand barrels a day | kbbl/d | 24049 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `product_supplied` | Product supplied, EIA's measure of consumption (VPP), in the month, thousand barrels | kbbl | 41005 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `product_supplied_per_day` | Product supplied (VPP), thousand barrels a day | kbbl/d | 41283 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `refinery_net_input` | Refinery net input (YIR) in the month, thousand barrels | kbbl | 16364 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `refinery_net_input_per_day` | Refinery net input (YIR), thousand barrels a day | kbbl/d | 16372 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `refinery_net_production` | Refinery net production (YPR) in the month, thousand barrels | kbbl | 29297 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `refinery_net_production_per_day` | Refinery net production (YPR), thousand barrels a day | kbbl/d | 29297 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `renewable_plant_production` | Renewable plant net production (YNP) in the month, thousand barrels | kbbl | 11738 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `renewable_plant_production_per_day` | Renewable plant net production (YNP), thousand barrels a day | kbbl/d | 11738 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `stock_change` | Stock change (SCG) in the month, thousand barrels | kbbl | 40054 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `stock_change_per_day` | Stock change (SCG), thousand barrels a day | kbbl/d | 40054 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `supply_adjustment` | EIA's supply adjustment (VUA) in the month, thousand barrels | kbbl | 14310 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `supply_adjustment_per_day` | EIA's supply adjustment (VUA), thousand barrels a day | kbbl/d | 14310 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `transfers_to_crude_supply` | Transfers to crude oil supply (TVP) in the month, thousand barrels | kbbl | 2856 | 2022-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `transfers_to_crude_supply_per_day` | Transfers to crude oil supply (TVP), thousand barrels a day | kbbl/d | 2856 | 2022-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_petroleum_stocks_monthly`

One month's end stocks of one petroleum product (gasoline, distillate and its grades, propane, residual fuel) in the U.S., a PADD or a PADD 1 sub-district.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 18247.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M); a month-end stock.
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/stoc/ts U.S. Energy Information Administration, Petroleum Supply Monthly, product stocks (API v2, route petroleum/stoc/ts) (https://www.eia.gov/petroleum/supply/monthly/)
- **Method note:** [`docs/methods/eia_petroleum_stocks_monthly.md`](../methods/eia_petroleum_stocks_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Petroleum Supply Monthly, product stocks (API v2). Via the Energy Research Warehouse (ERW), table `eia_petroleum_stocks_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_petroleum_stocks:<EIA series id> | none | text | for example eia_petroleum_stocks:ESM_EPD00H_SAE_R1X_MBBL, eia_petroleum_stocks:ESM_EPD00H_SAE_R1Y_MBBL, eia_petroleum_stocks:ESM_EPD00H_SAE_R1Z_MBBL; 63 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 307 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 265711.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, the PADDs included | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 18247 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name | none | text | for example Central Atlantic (PADD 1B) Ending Stocks of Distillate Fuel Oil (Thousand Barrels), Central Atlantic (PADD 1B) Ending Stocks of Distillate Fuel Oil, 0 to 15 ppm Sulfur (Thousand Barrels), Central Atlantic (PADD 1B) Ending Stocks of Distillate Fuel Oil, Greater Than 500 ppm Sulfur (Thousand Barrels); 63 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/stoc/ts | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/stoc/ts/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=SAE&start=2001-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T23:17:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 18247 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `ending_stocks` | Ending stocks of the product at the month's end, thousand barrels | kbbl | 18247 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_petroleum_stocks_state_monthly`

One month's end stocks of one petroleum product at refineries, bulk terminals and natural gas plants in one state, PADD or the U.S.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 73997.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M); a month-end stock.
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/stoc/st U.S. Energy Information Administration, petroleum stocks at refineries, bulk terminals and natural gas plants by state (API v2, route petroleum/stoc/st) (https://www.eia.gov/petroleum/supply/monthly/)
- **Method note:** [`docs/methods/eia_petroleum_stocks_state_monthly.md`](../methods/eia_petroleum_stocks_state_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Petroleum stocks at refineries, bulk terminals and natural gas plants by state (API v2, petroleum/stoc/st). Via the Energy Research Warehouse (ERW), table `eia_petroleum_stocks_state_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_petroleum_stocks_state:<EIA series id> | none | text | for example eia_petroleum_stocks_state:E_EPOBGC0_STR_NUS_MBBL, eia_petroleum_stocks_state:E_EPOBGC0_STR_R10_MBBL, eia_petroleum_stocks_state:E_EPOBGC0_STR_R20_MBBL; 593 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 139 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 201559.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for a PADD or the nation | none | text | for example US, US-AK, US-AL; 51 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 73997 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name | none | text | for example Alabama Conventional Gasoline Blending Components Stocks at Refineries, Bulk Terminals, and Natural Gas Plants (Thousand Barrels), Alabama Conventional Motor Gasoline Stocks at Refineries, Bulk Terminals, and Natural Gas Plants (Thousand Barrels), Alabama Distillate Fuel Oil Stocks at Refineries, Bulk Terminals, and Natural Gas Plants (Thousand Barrels); 593 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/stoc/st | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/stoc/st/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=STR&start=2015-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T07:48:20Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 73997 |
| `x_area` | EIA's area code (NUS, a PADD such as R10, or a state) (the source's name: duoarea) | none | text | for example NUS, R10, R20; 56 distinct | 0 |
| `x_product` | EIA's product code (for example EPD0 distillate fuel oil, EPLLPA propane) (the source's name: product) | none | text | EPD0, EPD00H, EPDM10, EPDXL0, EPLLPA, EPM0C, EPM0F, EPM0R, EPOBG, EPOBGC0, EPOBGR0, EPPK, EPPR | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `stocks_refineries_terminals_gas_plants` | Stocks of the product at refineries, bulk terminals and natural gas plants at the month's end, thousand barrels | kbbl | 73997 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_petroleum_stocks_weekly`

One week's U.S. ending stocks of crude oil (with or without the Strategic Petroleum Reserve) or one petroleum product, from EIA's Weekly Petroleum Status Report.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 16855.

- **Time:** ts_utc is the week-ending date EIA reports at 00:00:00Z (freq P1W).
- **Revisions:** Each run asks for the full history and merges it on (entity, variable, ts_utc), keeping EIA's newest value; a row EIA stops giving is kept. The copy held was rebuilt from the ERW archive by restore_tables.py. vintage is not filled.
- **Source:** eia:petroleum/stoc/wstk Weekly Petroleum Status Report: stocks (https://www.eia.gov/petroleum/supply/weekly/)
- **Method note:** [`docs/methods/eia_petroleum_stocks_weekly.md`](../methods/eia_petroleum_stocks_weekly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Weekly Petroleum Status Report: stocks. Via the Energy Research Warehouse (ERW), table `eia_petroleum_stocks_weekly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:<EIA series id> | none | text | eia:WCESTUS1, eia:WCRSTUS1, eia:WCSSTUS1, eia:WDISTUS1, eia:WGTSTUS1, eia:WKJSTUS1, eia:WPRSTUS1, eia:WTTSTUS1 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1982-08-20T00:00:00Z to 2026-11-06T00:00:00Z; 2302 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 18167.0 to 2117643.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 16855 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: EIA's series names are in the header's Series line | none | empty | no cell holds a value | 16855 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/stoc/wstk | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key=REDACTED&frequency=weekly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000&facets%5Bseries%5D%5B%5D=WCESTUS1&facets%5Bseries%5D%5B%5D=WCSSTUS1&facets%5Bseries%5D%5B%5D=WCRSTUS1&facets%5Bseries%5D%5B%5D=WGTSTUS1&facets%5Bseries%5D%5B%5D=WDISTUS1&facets%5Bseries%5D%5B%5D=WKJSTUS1&facets%5Bseries%5D%5B%5D=WPRSTUS1&facets%5Bseries%5D%5B%5D=WTTSTUS1, https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key=REDACTED&frequency=weekly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=10000&length=5000&facets%5Bseries%5D%5B%5D=WCESTUS1&facets%5Bseries%5D%5B%5D=WCSSTUS1&facets%5Bseries%5D%5B%5D=WCRSTUS1&facets%5Bseries%5D%5B%5D=WGTSTUS1&facets%5Bseries%5D%5B%5D=WDISTUS1&facets%5Bseries%5D%5B%5D=WKJSTUS1&facets%5Bseries%5D%5B%5D=WPRSTUS1&facets%5Bseries%5D%5B%5D=WTTSTUS1, https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key=REDACTED&frequency=weekly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=15000&length=5000&facets%5Bseries%5D%5B%5D=WCESTUS1&facets%5Bseries%5D%5B%5D=WCSSTUS1&facets%5Bseries%5D%5B%5D=WCRSTUS1&facets%5Bseries%5D%5B%5D=WGTSTUS1&facets%5Bseries%5D%5B%5D=WDISTUS1&facets%5Bseries%5D%5B%5D=WKJSTUS1&facets%5Bseries%5D%5B%5D=WPRSTUS1&facets%5Bseries%5D%5B%5D=WTTSTUS1, https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key=REDACTED&frequency=weekly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=5000&length=5000&facets%5Bseries%5D%5B%5D=WCESTUS1&facets%5Bseries%5D%5B%5D=WCSSTUS1&facets%5Bseries%5D%5B%5D=WCRSTUS1&facets%5Bseries%5D%5B%5D=WGTSTUS1&facets%5Bseries%5D%5B%5D=WDISTUS1&facets%5Bseries%5D%5B%5D=WKJSTUS1&facets%5Bseries%5D%5B%5D=WPRSTUS1&facets%5Bseries%5D%5B%5D=WTTSTUS1 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-29T00:59:54Z, 2026-09-29T00:59:56Z, 2026-09-29T00:59:58Z, 2026-09-29T01:00:00Z, 2026-09-30T19:21:53Z, 2026-10-08T14:28:34Z, 2026-10-19T15:01:28Z, 2026-10-22T14:37:47Z, 2026-10-29T14:37:36Z, 2026-11-05T23:10:52Z, 2026-11-12T21:47:57Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 16855 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `stocks` | U.S. ending stocks of the product the series names, thousand barrels | kbbl | 16855 | 1982-08-20T00:00:00Z | 2026-11-06T00:00:00Z |

### `eia_petroleum_supply_weekly`

One week's value of one U.S. petroleum supply series (a stock, crude production, refinery utilization, crude input or a trade flow), from EIA's Weekly Petroleum Status Report.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 26268.

- **Time:** ts_utc is the Friday the report week ends, at 00:00:00Z (freq P1W).
- **Revisions:** Rewritten whole by each run (the file is deleted and the history from 2010 written again), so EIA's revisions are taken and a week EIA stops giving leaves. vintage is not filled.
- **Source:** eia:petroleum/stoc/wstk:supply EIA, Weekly Petroleum Status Report: stocks (https://www.eia.gov/petroleum/supply/weekly/)
- **Source:** eia:petroleum/sum/sndw EIA, Weekly Petroleum Status Report: supply and disposition (https://www.eia.gov/petroleum/supply/weekly/)
- **Source:** eia:petroleum/move/wkly:supply EIA, Weekly Petroleum Status Report: imports and exports (https://www.eia.gov/petroleum/supply/weekly/)
- **Method note:** [`docs/methods/eia_petroleum_supply_weekly.md`](../methods/eia_petroleum_supply_weekly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Weekly Petroleum Status Report: imports and exports; Weekly Petroleum Status Report: stocks; Weekly Petroleum Status Report: supply and disposition. Via the Energy Research Warehouse (ERW), table `eia_petroleum_supply_weekly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:<EIA series id> | none | text | for example eia:WCESTUS1, eia:WCREXUS2, eia:WCRFPUS2; 30 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z to 2026-11-06T00:00:00Z; 880 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -7471.0 to 726617.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl, kbbl/d, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, the PADD series included | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 26268 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's description of the series with its unit removed | none | text | for example Alaska Field Production of Crude Oil, Cushing, OK Ending Stocks excluding SPR of Crude Oil, East Coast (PADD 1) Percent Utilization of Refinery Operable Capacity; 30 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/move/wkly:supply, eia:petroleum/stoc/wstk:supply, eia:petroleum/sum/sndw | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/move/wkly/data/?frequency=weekly&data%5B0%5D=value&facets%5Bseries%5D%5B%5D=WCRIMUS2&facets%5Bseries%5D%5B%5D=WCREXUS2&facets%5Bseries%5D%5B%5D=WCRNTUS2&facets%5Bseries%5D%5B%5D=WRPIMUS2&facets%5Bseries%5D%5B%5D=WRPEXUS2&facets%5Bseries%5D%5B%5D=WRPNTUS2&facets%5Bseries%5D%5B%5D=WTTNTUS2&facets%5Bseries%5D%5B%5D=WDIIMUS2&facets%5Bseries%5D%5B%5D=WDIEXUS2&facets%5Bseries%5D%5B%5D=W_EPM0F_IM0_NUS-Z00_MBBLD&start=2010-01-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000, https://api.eia.gov/v2/petroleum/move/wkly/data/?frequency=weekly&data%5B0%5D=value&facets%5Bseries%5D%5B%5D=WCRIMUS2&facets%5Bseries%5D%5B%5D=WCREXUS2&facets%5Bseries%5D%5B%5D=WCRNTUS2&facets%5Bseries%5D%5B%5D=WRPIMUS2&facets%5Bseries%5D%5B%5D=WRPEXUS2&facets%5Bseries%5D%5B%5D=WRPNTUS2&facets%5Bseries%5D%5B%5D=WTTNTUS2&facets%5Bseries%5D%5B%5D=WDIIMUS2&facets%5Bseries%5D%5B%5D=WDIEXUS2&facets%5Bseries%5D%5B%5D=W_EPM0F_IM0_NUS-Z00_MBBLD&start=2010-01-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=5000&length=5000, https://api.eia.gov/v2/petroleum/stoc/wstk/data/?frequency=weekly&data%5B0%5D=value&facets%5Bseries%5D%5B%5D=WCESTUS1&facets%5Bseries%5D%5B%5D=W_EPC0_SAX_YCUOK_MBBL&facets%5Bseries%5D%5B%5D=WCSSTUS1&facets%5Bseries%5D%5B%5D=WGTSTUS1&facets%5Bseries%5D%5B%5D=WDISTUS1&start=2010-01-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000, https://api.eia.gov/v2/petroleum/sum/sndw/data/?frequency=weekly&data%5B0%5D=value&facets%5Bseries%5D%5B%5D=WCRFPUS2&facets%5Bseries%5D%5B%5D=W_EPC0_FPF_R48_MBBLD&facets%5Bseries%5D%5B%5D=W_EPC0_FPF_SAK_MBBLD&facets%5Bseries%5D%5B%5D=WPULEUS3&facets%5Bseries%5D%5B%5D=W_NA_YUP_R10_PER&facets%5Bseries%5D%5B%5D=W_NA_YUP_R20_PER&facets%5Bseries%5D%5B%5D=W_NA_YUP_R30_PER&facets%5Bseries%5D%5B%5D=W_NA_YUP_R40_PER&facets%5Bseries%5D%5B%5D=W_NA_YUP_R50_PER&facets%5Bseries%5D%5B%5D=WCRRIUS2&facets%5Bseries%5D%5B%5D=WCRRIP12&facets%5Bseries%5D%5B%5D=WCRRIP22&facets%5Bseries%5D%5B%5D=WCRRIP32&facets%5Bseries%5D%5B%5D=WCRRIP42&facets%5Bseries%5D%5B%5D=WCRRIP52&start=2010-01-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000, https://api.eia.gov/v2/petroleum/sum/sndw/data/?frequency=weekly&data%5B0%5D=value&facets%5Bseries%5D%5B%5D=WCRFPUS2&facets%5Bseries%5D%5B%5D=W_EPC0_FPF_R48_MBBLD&facets%5Bseries%5D%5B%5D=W_EPC0_FPF_SAK_MBBLD&facets%5Bseries%5D%5B%5D=WPULEUS3&facets%5Bseries%5D%5B%5D=W_NA_YUP_R10_PER&facets%5Bseries%5D%5B%5D=W_NA_YUP_R20_PER&facets%5Bseries%5D%5B%5D=W_NA_YUP_R30_PER&facets%5Bseries%5D%5B%5D=W_NA_YUP_R40_PER&facets%5Bseries%5D%5B%5D=W_NA_YUP_R50_PER&facets%5Bseries%5D%5B%5D=WCRRIUS2&facets%5Bseries%5D%5B%5D=WCRRIP12&facets%5Bseries%5D%5B%5D=WCRRIP22&facets%5Bseries%5D%5B%5D=WCRRIP32&facets%5Bseries%5D%5B%5D=WCRRIP42&facets%5Bseries%5D%5B%5D=WCRRIP52&start=2010-01-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=10000&length=5000, https://api.eia.gov/v2/petroleum/sum/sndw/data/?frequency=weekly&data%5B0%5D=value&facets%5Bseries%5D%5B%5D=WCRFPUS2&facets%5Bseries%5D%5B%5D=W_EPC0_FPF_R48_MBBLD&facets%5Bseries%5D%5B%5D=W_EPC0_FPF_SAK_MBBLD&facets%5Bseries%5D%5B%5D=WPULEUS3&facets%5Bseries%5D%5B%5D=W_NA_YUP_R10_PER&facets%5Bseries%5D%5B%5D=W_NA_YUP_R20_PER&facets%5Bseries%5D%5B%5D=W_NA_YUP_R30_PER&facets%5Bseries%5D%5B%5D=W_NA_YUP_R40_PER&facets%5Bseries%5D%5B%5D=W_NA_YUP_R50_PER&facets%5Bseries%5D%5B%5D=WCRRIUS2&facets%5Bseries%5D%5B%5D=WCRRIP12&facets%5Bseries%5D%5B%5D=WCRRIP22&facets%5Bseries%5D%5B%5D=WCRRIP32&facets%5Bseries%5D%5B%5D=WCRRIP42&facets%5Bseries%5D%5B%5D=WCRRIP52&start=2010-01-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=5000&length=5000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T11:47:37Z, 2026-11-16T11:47:39Z, 2026-11-16T11:47:40Z, 2026-11-16T11:47:42Z, 2026-11-16T11:47:43Z, 2026-11-16T11:47:46Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 26268 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `crude_input` | Refiner net input of crude oil (U.S. or a PADD), thousand barrels a day | kbbl/d | 5280 | 2010-01-01T00:00:00Z | 2026-11-06T00:00:00Z |
| `flow` | Imports, exports or net imports of crude, petroleum products or distillate, thousand barrels a day (negative net imports are net exports) | kbbl/d | 8778 | 2010-01-01T00:00:00Z | 2026-11-06T00:00:00Z |
| `production` | Field production of crude oil (U.S., Lower 48 or Alaska), thousand barrels a day | kbbl/d | 2640 | 2010-01-01T00:00:00Z | 2026-11-06T00:00:00Z |
| `stocks` | Ending stocks of crude (excluding or in the Strategic Petroleum Reserve, or at Cushing), total gasoline or distillate fuel oil, thousand barrels | kbbl | 4400 | 2010-01-01T00:00:00Z | 2026-11-06T00:00:00Z |
| `utilization` | Percent utilization of refinery operable capacity (U.S. or a PADD) | pct | 5170 | 2010-01-01T00:00:00Z | 2026-11-06T00:00:00Z |

### `eia_petroleum_trade_weekly`

One week's U.S. imports, exports or net imports of crude oil, petroleum products or both, from EIA's Weekly Petroleum Status Report.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 12614.

- **Time:** ts_utc is the week-ending date EIA reports at 00:00:00Z (freq P1W).
- **Revisions:** Each run asks for the full history and merges it on (entity, variable, ts_utc), keeping EIA's newest value; a row EIA stops giving is kept. The copy held was rebuilt from the ERW archive by restore_tables.py. vintage is not filled.
- **Source:** eia:petroleum/move/wkly Weekly Petroleum Status Report: imports and exports (https://www.eia.gov/petroleum/supply/weekly/)
- **Method note:** [`docs/methods/eia_petroleum_trade_weekly.md`](../methods/eia_petroleum_trade_weekly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Weekly Petroleum Status Report: imports and exports. Via the Energy Research Warehouse (ERW), table `eia_petroleum_trade_weekly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:<EIA series id> | none | text | eia:WCREXUS2, eia:WCRIMUS2, eia:WCRNTUS2, eia:WRPEXUS2, eia:WRPIMUS2, eia:WTTEXUS2, eia:WTTIMUS2 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-05T00:00:00Z to 2026-11-06T00:00:00Z; 1923 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -688.0 to 15217.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl/d | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 12614 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: EIA's series names are in the header's Series line | none | empty | no cell holds a value | 12614 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/move/wkly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/move/wkly/data/?api_key=REDACTED&frequency=weekly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000&facets%5Bseries%5D%5B%5D=WCREXUS2&facets%5Bseries%5D%5B%5D=WRPEXUS2&facets%5Bseries%5D%5B%5D=WTTEXUS2&facets%5Bseries%5D%5B%5D=WCRIMUS2&facets%5Bseries%5D%5B%5D=WRPIMUS2&facets%5Bseries%5D%5B%5D=WTTIMUS2&facets%5Bseries%5D%5B%5D=WCRNTUS2, https://api.eia.gov/v2/petroleum/move/wkly/data/?api_key=REDACTED&frequency=weekly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=10000&length=5000&facets%5Bseries%5D%5B%5D=WCREXUS2&facets%5Bseries%5D%5B%5D=WRPEXUS2&facets%5Bseries%5D%5B%5D=WTTEXUS2&facets%5Bseries%5D%5B%5D=WCRIMUS2&facets%5Bseries%5D%5B%5D=WRPIMUS2&facets%5Bseries%5D%5B%5D=WTTIMUS2&facets%5Bseries%5D%5B%5D=WCRNTUS2, https://api.eia.gov/v2/petroleum/move/wkly/data/?api_key=REDACTED&frequency=weekly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=5000&length=5000&facets%5Bseries%5D%5B%5D=WCREXUS2&facets%5Bseries%5D%5B%5D=WRPEXUS2&facets%5Bseries%5D%5B%5D=WTTEXUS2&facets%5Bseries%5D%5B%5D=WCRIMUS2&facets%5Bseries%5D%5B%5D=WRPIMUS2&facets%5Bseries%5D%5B%5D=WTTIMUS2&facets%5Bseries%5D%5B%5D=WCRNTUS2 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-29T01:00:06Z, 2026-09-29T01:00:11Z, 2026-09-29T01:00:16Z, 2026-09-30T19:22:28Z, 2026-10-08T14:28:40Z, 2026-10-19T15:02:03Z, 2026-10-22T14:38:10Z, 2026-10-29T14:37:41Z, 2026-11-05T23:10:57Z, 2026-11-12T21:48:02Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 12614 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `flow` | U.S. imports, exports or net imports of what the series names, thousand barrels a day | kbbl/d | 12614 | 1990-01-05T00:00:00Z | 2026-11-06T00:00:00Z |

### `eia_power_co2_state_annual`

One state's (or the nation's) yearly carbon dioxide emissions from power plants of one fuel, or their emission rate, from EIA's State Electricity Profiles.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 10640.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:electricity/state-electricity-profiles/emissions-by-state-by-fuel U.S. Energy Information Administration, State Electricity Profiles, emissions by state and fuel (API v2, route electricity/state-electricity-profiles/emissions-by-state-by-fuel) (https://www.eia.gov/electricity/state/)
- **Method note:** [`docs/methods/eia_power_co2_state_annual.md`](../methods/eia_power_co2_state_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). State Electricity Profiles, power plant emissions by state and fuel (API v2). Via the Energy Research Warehouse (ERW), table `eia_power_co2_state_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_power_co2:<state>:<fuel>; fuels COL, NG, PET, OTH and ALL (a sum leaves ALL out) | none | text | for example eia_power_co2:AK:ALL, eia_power_co2:AK:COL, eia_power_co2:AK:NG; 256 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 35 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 2547032000.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kgCO2/MWh, tCO2 | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 10640 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <state>, <fuel> in EIA's names | none | text | for example Alabama, Coal, Alabama, Natural Gas, Alabama, Other; 256 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:electricity/state-electricity-profiles/emissions-by-state-by-fuel | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/electricity/state-electricity-profiles/emissions-by-state-by-fuel/data/?api_key=REDACTED&frequency=annual&data%5B%5D=co2-thousand-metric-tons&data%5B%5D=co2-rate-lbs-mwh&start=1990 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T23:48:30Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 10640 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `co2` | Carbon dioxide emitted by power plants burning the fuel, tonnes of CO2 (EIA's thousand metric tons times 1,000) | tCO2 | 8820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `co2_rate` | Carbon dioxide emitted per unit of electricity, kg of CO2 per MWh (EIA's pounds per MWh times 0.453592) | kgCO2/MWh | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_power_costs_annual`

One year's figure from EIA's Electric Power Annual chapter 8 (tables 8.1 to 8.4) for the U.S. (a heat rate, a line of investor-owned utilities' revenue and expenses, or a plant type's operating expense).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 550.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:electric_power_annual:chapter8 U.S. Energy Information Administration, Electric Power Annual, tables 8.1 to 8.4 (https://www.eia.gov/electricity/annual/)
- **Method note:** [`docs/methods/eia_power_costs_annual.md`](../methods/eia_power_costs_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Electric Power Annual, chapter 8 (heat rates, revenue and expenses). Via the Energy Research Warehouse (ERW), table `eia_power_costs_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_epa:heat_rate:<source>, eia_epa:tested_heat_rate:<prime mover>:<source>, eia_epa:iou_finance:<line path>, or eia_epa:iou_plant_expense:<plant type> | none | text | for example eia_epa:heat_rate:coal, eia_epa:heat_rate:natural_gas, eia_epa:heat_rate:nuclear; 39 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.77 to 412440000000.0; 525 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMBtu/MWh, USD, USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 550 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's row name | none | text | for example Administrative and General, Coal, average operating heat rate, Combined Cycle, Natural Gas, average tested heat rate; 48 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:electric_power_annual:chapter8 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/electricity/annual/xls/epa_08_01.xlsx, https://www.eia.gov/electricity/annual/xls/epa_08_02.xlsx, https://www.eia.gov/electricity/annual/xls/epa_08_03.xlsx, https://www.eia.gov/electricity/annual/xls/epa_08_04.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T06:55:42Z, 2026-10-23T06:55:43Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 550 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `amount` | A line of investor-owned utilities' revenue and expenses, USD (table 8.3, EIA's million dollars times 1,000,000); the lines are a hierarchy | USD | 231 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `fuel_expense` | A plant type's fuel expense, USD per MWh (table 8.4) | USD/MWh | 33 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `heat_rate` | Average operating heat rate of the source's plants (fuel burned per unit of electricity), MMBtu per MWh (table 8.1) | MMBtu/MWh | 44 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `maintenance_expense` | A plant type's maintenance expense, USD per MWh (table 8.4) | USD/MWh | 44 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `operation_expense` | A plant type's operation expense, USD per MWh (table 8.4, EIA's mills per kWh, the same number) | USD/MWh | 44 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `tested_heat_rate` | Average tested heat rate by prime mover and energy source, MMBtu per MWh (table 8.2) | MMBtu/MWh | 110 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_expense` | A plant type's total operating expense, USD per MWh (table 8.4) | USD/MWh | 44 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `eia_power_fuel_stocks_monthly`

One location's month-end stocks of coal, petroleum liquids or petroleum coke at power plants, in the electric power sector or all sectors (Form EIA-923).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 48702.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M); a month-end stock.
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:electricity/electric-power-operational-data:stocks U.S. Energy Information Administration, Form EIA-923, electric power operational data (API v2) (https://www.eia.gov/electricity/data/browser/)
- **Method note:** [`docs/methods/eia_power_fuel_stocks_monthly.md`](../methods/eia_power_fuel_stocks_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Electric power operational data: fuel stocks (Form EIA-923, API v2). Via the Energy Research Warehouse (ERW), table `eia_power_fuel_stocks_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_power_stocks:<location>:<sector 98 electric power or 99 all sectors>:<fuel COL, PEL or PC> | none | text | for example eia_power_stocks:AK:98:COL, eia_power_stocks:AK:98:PEL, eia_power_stocks:AK:99:COL; 320 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2008-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 223 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 206828446.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl, short_ton | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation; empty for a census region | none | text | for example US, US-AK, US-AL; 53 distinct | 9221 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 48702 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's names (location, sector, fuel) | none | text | for example Alabama, All Sectors, coal, excluding waste coal, Alabama, All Sectors, petroleum coke, Alabama, All Sectors, petroleum liquids; 320 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:electricity/electric-power-operational-data:stocks | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=stocks&start=2008-01&facets%5Bfueltypeid%5D%5B%5D=COL&facets%5Bfueltypeid%5D%5B%5D=PEL&facets%5Bfueltypeid%5D%5B%5D=PC&facets%5Bsectorid%5D%5B%5D=98&facets%5Bsectorid%5D%5B%5D=99 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T10:05:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 48702 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `stocks` | Fuel stocks at power plants at the month's end: short tons for coal (excluding waste coal) and petroleum coke (EIA's thousand short tons times 1,000), thousand barrels for petroleum liquids; the unit column says which | kbbl; short_ton | 48702 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_power_plant_fuel_costs`

One location's monthly average cost of coal or natural gas delivered to the electric power sector, in one unit (per MMBtu, per short ton, per Mcf), from Form EIA-923.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 13160.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M); the header's words on a survey Monday do not concern this table.
- **Revisions:** Rewritten whole by each run (the file is deleted and the history from January 2019 written again), so EIA's revisions are taken; the copy held was rebuilt from the ERW archive by restore_tables.py. vintage is not filled.
- **Source:** eia:electricity/electric-power-operational-data:cost EIA, Electric power operational data: receipts and cost of fossil fuels (Form EIA-923) (https://www.eia.gov/electricity/data/browser/)
- **Method note:** [`docs/methods/eia_power_plant_fuel_costs.md`](../methods/eia_power_plant_fuel_costs.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Electric power operational data: receipts and cost of fossil fuels (Form EIA-923). Via the Energy Research Warehouse (ERW), table `eia_power_plant_fuel_costs`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:plant_fuel_cost:<location>:<COW\|NG>, COW all coal products, NG natural gas | none | text | for example eia:plant_fuel_cost:AK:COW, eia:plant_fuel_cost:AK:NG, eia:plant_fuel_cost:AL:COW; 98 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 92 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -3.26 to 168.23; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MMBtu, USD/Mcf, USD/short_ton | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US, or US-<state>; empty for an EIA census division | none | text | for example US, US-AK, US-AL; 48 distinct | 2714 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 13160 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's name of the location | none | text | for example Alabama, Alaska, Arizona; 58 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:electricity/electric-power-operational-data:cost | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?frequency=monthly&data%5B0%5D=cost-per-btu&data%5B1%5D=cost&facets%5Bsectorid%5D%5B%5D=98&facets%5Bfueltypeid%5D%5B%5D=COW&facets%5Bfueltypeid%5D%5B%5D=NG&start=2019-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=location&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=fueltypeid&sort%5B2%5D%5Bdirection%5D=asc&offset=0&length=5000, https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?frequency=monthly&data%5B0%5D=cost-per-btu&data%5B1%5D=cost&facets%5Bsectorid%5D%5B%5D=98&facets%5Bfueltypeid%5D%5B%5D=COW&facets%5Bfueltypeid%5D%5B%5D=NG&start=2019-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=location&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=fueltypeid&sort%5B2%5D%5Bdirection%5D=asc&offset=10000&length=5000, https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?frequency=monthly&data%5B0%5D=cost-per-btu&data%5B1%5D=cost&facets%5Bsectorid%5D%5B%5D=98&facets%5Bfueltypeid%5D%5B%5D=COW&facets%5Bfueltypeid%5D%5B%5D=NG&start=2019-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=location&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=fueltypeid&sort%5B2%5D%5Bdirection%5D=asc&offset=5000&length=5000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T08:18:31Z, 2026-10-06T08:18:32Z, 2026-10-06T08:18:33Z, 2026-10-22T15:08:02Z, 2026-10-22T15:08:08Z, 2026-10-23T15:05:50Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 13160 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `cost_per_mcf` | Average cost of natural gas delivered to power plants, USD per thousand cubic feet | USD/Mcf | 3604 | 2019-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `cost_per_mmbtu` | Average cost of the fuel delivered to power plants, USD per million Btu (coal and gas) | USD/MMBtu | 6580 | 2019-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `cost_per_short_ton` | Average cost of coal delivered to power plants, USD per short ton | USD/short_ton | 2976 | 2019-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `eia_primary_energy_monthly`

One month's U.S. primary energy production, trade, stock change or consumption, in all or of one source, from EIA's Monthly Energy Review (Tables 1.1 to 1.3).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 15180.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Each run asks for the full history and merges it on (entity, variable, ts_utc), keeping EIA's newest value; a row EIA stops giving is kept. The copy held was rebuilt from the ERW archive by restore_tables.py. vintage is not filled.
- **Source:** eia:total-energy Monthly Energy Review, tables 1.1 to 1.3 (primary energy: eia_primary_energy_monthly) and 2.3 and 2.4 (commercial and industrial energy consumption: eia_sector_energy_consumption_monthly) (https://www.eia.gov/totalenergy/data/monthly/)
- **Method note:** [`docs/methods/eia_primary_energy_monthly.md`](../methods/eia_primary_energy_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Monthly Energy Review, tables 1.1 to 1.3 (primary energy: eia_primary_energy_monthly) and 2.3 and 2.4 (commercial and industrial energy consumption: eia_sector_energy_consumption_monthly). Via the Energy Research Warehouse (ERW), table `eia_primary_energy_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:<Monthly Energy Review series id (MSN)> | none | text | eia:BMPRBUS, eia:BMTCBUS, eia:CLPRBUS, eia:CLTCBUS, eia:FFPRBUS, eia:FFTCBUS, eia:GETCBUS, eia:HVTCBUS, eia:NGPRBUS, eia:NLPRBUS, eia:NNTCBUS, eia:NUETBUS, eia:PAPRBUS, eia:PMTCBUS, eia:REPRBUS, eia:RETCBUS, eia:SOTCBUS, eia:TEAJBUS, eia:TEEXBUS, eia:TEIMBUS, eia:TENIBUS, eia:TEPRBUS, eia:TETCBUS, eia:WYTCBUS | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1973-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 643 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1586.161 to 9521.649; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | TBtu | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 15180 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: EIA's series names are in the header's Series line | none | empty | no cell holds a value | 15180 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:total-energy | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/total-energy/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=msn&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000&facets%5Bmsn%5D%5B%5D=FFPRBUS&facets%5Bmsn%5D%5B%5D=REPRBUS&facets%5Bmsn%5D%5B%5D=TEPRBUS&facets%5Bmsn%5D%5B%5D=CLPRBUS&facets%5Bmsn%5D%5B%5D=NGPRBUS&facets%5Bmsn%5D%5B%5D=PAPRBUS&facets%5Bmsn%5D%5B%5D=NLPRBUS&facets%5Bmsn%5D%5B%5D=BMPRBUS&facets%5Bmsn%5D%5B%5D=TEIMBUS&facets%5Bmsn%5D%5B%5D=TEEXBUS&facets%5Bmsn%5D%5B%5D=TENIBUS&facets%5Bmsn%5D%5B%5D=TEAJBUS&facets%5Bmsn%5D%5B%5D=FFTCBUS&facets%5Bmsn%5D%5B%5D=RETCBUS&facets%5Bmsn%5D%5B%5D=TETCBUS&facets%5Bmsn%5D%5B%5D=CLTCBUS&facets%5Bmsn%5D%5B%5D=NNTCBUS&facets%5Bmsn%5D%5B%5D=PMTCBUS&facets%5Bmsn%5D%5B%5D=BMTCBUS&facets%5Bmsn%5D%5B%5D=NUETBUS&facets%5Bmsn%5D%5B%5D=HVTCBUS&facets%5Bmsn%5D%5B%5D=GETCBUS&facets%5Bmsn%5D%5B%5D=SOTCBUS&facets%5Bmsn%5D%5B%5D=WYTCBUS, https://api.eia.gov/v2/total-energy/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=msn&sort%5B1%5D%5Bdirection%5D=asc&offset=10000&length=5000&facets%5Bmsn%5D%5B%5D=FFPRBUS&facets%5Bmsn%5D%5B%5D=REPRBUS&facets%5Bmsn%5D%5B%5D=TEPRBUS&facets%5Bmsn%5D%5B%5D=CLPRBUS&facets%5Bmsn%5D%5B%5D=NGPRBUS&facets%5Bmsn%5D%5B%5D=PAPRBUS&facets%5Bmsn%5D%5B%5D=NLPRBUS&facets%5Bmsn%5D%5B%5D=BMPRBUS&facets%5Bmsn%5D%5B%5D=TEIMBUS&facets%5Bmsn%5D%5B%5D=TEEXBUS&facets%5Bmsn%5D%5B%5D=TENIBUS&facets%5Bmsn%5D%5B%5D=TEAJBUS&facets%5Bmsn%5D%5B%5D=FFTCBUS&facets%5Bmsn%5D%5B%5D=RETCBUS&facets%5Bmsn%5D%5B%5D=TETCBUS&facets%5Bmsn%5D%5B%5D=CLTCBUS&facets%5Bmsn%5D%5B%5D=NNTCBUS&facets%5Bmsn%5D%5B%5D=PMTCBUS&facets%5Bmsn%5D%5B%5D=BMTCBUS&facets%5Bmsn%5D%5B%5D=NUETBUS&facets%5Bmsn%5D%5B%5D=HVTCBUS&facets%5Bmsn%5D%5B%5D=GETCBUS&facets%5Bmsn%5D%5B%5D=SOTCBUS&facets%5Bmsn%5D%5B%5D=WYTCBUS, https://api.eia.gov/v2/total-energy/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=msn&sort%5B1%5D%5Bdirection%5D=asc&offset=15000&length=5000&facets%5Bmsn%5D%5B%5D=FFPRBUS&facets%5Bmsn%5D%5B%5D=REPRBUS&facets%5Bmsn%5D%5B%5D=TEPRBUS&facets%5Bmsn%5D%5B%5D=CLPRBUS&facets%5Bmsn%5D%5B%5D=NGPRBUS&facets%5Bmsn%5D%5B%5D=PAPRBUS&facets%5Bmsn%5D%5B%5D=NLPRBUS&facets%5Bmsn%5D%5B%5D=BMPRBUS&facets%5Bmsn%5D%5B%5D=TEIMBUS&facets%5Bmsn%5D%5B%5D=TEEXBUS&facets%5Bmsn%5D%5B%5D=TENIBUS&facets%5Bmsn%5D%5B%5D=TEAJBUS&facets%5Bmsn%5D%5B%5D=FFTCBUS&facets%5Bmsn%5D%5B%5D=RETCBUS&facets%5Bmsn%5D%5B%5D=TETCBUS&facets%5Bmsn%5D%5B%5D=CLTCBUS&facets%5Bmsn%5D%5B%5D=NNTCBUS&facets%5Bmsn%5D%5B%5D=PMTCBUS&facets%5Bmsn%5D%5B%5D=BMTCBUS&facets%5Bmsn%5D%5B%5D=NUETBUS&facets%5Bmsn%5D%5B%5D=HVTCBUS&facets%5Bmsn%5D%5B%5D=GETCBUS&facets%5Bmsn%5D%5B%5D=SOTCBUS&facets%5Bmsn%5D%5B%5D=WYTCBUS, https://api.eia.gov/v2/total-energy/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=msn&sort%5B1%5D%5Bdirection%5D=asc&offset=5000&length=5000&facets%5Bmsn%5D%5B%5D=FFPRBUS&facets%5Bmsn%5D%5B%5D=REPRBUS&facets%5Bmsn%5D%5B%5D=TEPRBUS&facets%5Bmsn%5D%5B%5D=CLPRBUS&facets%5Bmsn%5D%5B%5D=NGPRBUS&facets%5Bmsn%5D%5B%5D=PAPRBUS&facets%5Bmsn%5D%5B%5D=NLPRBUS&facets%5Bmsn%5D%5B%5D=BMPRBUS&facets%5Bmsn%5D%5B%5D=TEIMBUS&facets%5Bmsn%5D%5B%5D=TEEXBUS&facets%5Bmsn%5D%5B%5D=TENIBUS&facets%5Bmsn%5D%5B%5D=TEAJBUS&facets%5Bmsn%5D%5B%5D=FFTCBUS&facets%5Bmsn%5D%5B%5D=RETCBUS&facets%5Bmsn%5D%5B%5D=TETCBUS&facets%5Bmsn%5D%5B%5D=CLTCBUS&facets%5Bmsn%5D%5B%5D=NNTCBUS&facets%5Bmsn%5D%5B%5D=PMTCBUS&facets%5Bmsn%5D%5B%5D=BMTCBUS&facets%5Bmsn%5D%5B%5D=NUETBUS&facets%5Bmsn%5D%5B%5D=HVTCBUS&facets%5Bmsn%5D%5B%5D=GETCBUS&facets%5Bmsn%5D%5B%5D=SOTCBUS&facets%5Bmsn%5D%5B%5D=WYTCBUS | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T12:28:53Z, 2026-10-23T12:28:54Z, 2026-10-23T12:28:55Z, 2026-10-30T14:45:15Z, 2026-10-30T14:45:23Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 15180 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` | Primary energy consumption of the source, trillion Btu | TBtu | 4501 | 1973-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `consumption_production` | Nuclear, hydro, geothermal, solar or wind energy, which EIA gives as one series for both production and consumption, trillion Btu | TBtu | 2963 | 1973-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `exports` | Primary energy exports (TEEXBUS), trillion Btu | TBtu | 643 | 1973-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `imports` | Primary energy imports (TEIMBUS), trillion Btu | TBtu | 643 | 1973-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_imports` | Primary energy net imports (TENIBUS), trillion Btu | TBtu | 643 | 1973-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `production` | Primary energy production of the source, trillion Btu | TBtu | 5144 | 1973-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `stock_change_and_other` | Primary energy stock change and other (TEAJBUS), trillion Btu | TBtu | 643 | 1973-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_product_spot_prices`

One trading day's spot price of one refined product at one trading hub (gasoline, RBOB, ultra-low sulfur diesel, CARB diesel, jet fuel, heating oil, propane), as EIA reports it.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 72232.

- **Time:** ts_utc is EIA's trading date at 00:00:00Z (freq P1D), a date; trading days only.
- **Revisions:** Each run asks for the full history and merges it on (entity, variable, ts_utc), keeping EIA's newest value; a row EIA stops giving is kept. The copy held was rebuilt from the ERW archive by restore_tables.py. vintage is not filled.
- **Source:** eia:petroleum/pri/spt Spot Prices for Crude Oil and Petroleum Products (https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm)
- **Method note:** [`docs/methods/eia_product_spot_prices.md`](../methods/eia_product_spot_prices.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Spot Prices for Crude Oil and Petroleum Products, daily. Via the Energy Research Warehouse (ERW), table `eia_product_spot_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:<EIA series id> | none | text | eia:EER_EPD2DC_PF4_Y05LA_DPG, eia:EER_EPD2DXL0_PF4_RGC_DPG, eia:EER_EPD2DXL0_PF4_Y35NY_DPG, eia:EER_EPD2F_PF4_Y35NY_DPG, eia:EER_EPJK_PF4_RGC_DPG, eia:EER_EPLLPA_PF4_Y44MB_DPG, eia:EER_EPMRR_PF4_Y05LA_DPG, eia:EER_EPMRU_PF4_RGC_DPG, eia:EER_EPMRU_PF4_Y35NY_DPG | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1986-06-02T00:00:00Z to 2026-11-11T00:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.203 to 5.526; 4354 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/gal | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 72232 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: EIA's series names are in the header's Series line | none | empty | no cell holds a value | 72232 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/pri/spt | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRR_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DC_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPJK_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2F_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPLLPA_PF4_Y44MB_DPG, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=10000&length=5000&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRR_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DC_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPJK_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2F_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPLLPA_PF4_Y44MB_DPG, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=15000&length=5000&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRR_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DC_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPJK_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2F_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPLLPA_PF4_Y44MB_DPG, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=20000&length=5000&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRR_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DC_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPJK_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2F_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPLLPA_PF4_Y44MB_DPG, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=25000&length=5000&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRR_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DC_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPJK_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2F_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPLLPA_PF4_Y44MB_DPG, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=30000&length=5000&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRR_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DC_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPJK_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2F_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPLLPA_PF4_Y44MB_DPG, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=35000&length=5000&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRR_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DC_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPJK_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2F_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPLLPA_PF4_Y44MB_DPG, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=40000&length=5000&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRR_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DC_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPJK_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2F_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPLLPA_PF4_Y44MB_DPG, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=45000&length=5000&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRR_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DC_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPJK_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2F_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPLLPA_PF4_Y44MB_DPG, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=5000&length=5000&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRR_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DC_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPJK_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2F_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPLLPA_PF4_Y44MB_DPG, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=50000&length=5000&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRR_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DC_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPJK_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2F_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPLLPA_PF4_Y44MB_DPG, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=55000&length=5000&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRR_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DC_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPJK_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2F_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPLLPA_PF4_Y44MB_DPG, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=60000&length=5000&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRR_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DC_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPJK_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2F_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPLLPA_PF4_Y44MB_DPG, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=65000&length=5000&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRR_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DC_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPJK_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2F_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPLLPA_PF4_Y44MB_DPG, https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=70000&length=5000&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRU_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPMRR_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DXL0_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2DC_PF4_Y05LA_DPG&facets%5Bseries%5D%5B%5D=EER_EPJK_PF4_RGC_DPG&facets%5Bseries%5D%5B%5D=EER_EPD2F_PF4_Y35NY_DPG&facets%5Bseries%5D%5B%5D=EER_EPLLPA_PF4_Y44MB_DPG | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-29T01:00:21Z, 2026-09-29T01:00:25Z, 2026-09-29T01:00:29Z, 2026-09-29T01:00:33Z, 2026-09-29T01:00:35Z, 2026-09-29T01:00:38Z, 2026-09-29T01:00:41Z, 2026-09-29T01:00:46Z, 2026-09-29T01:00:49Z, 2026-09-29T01:00:51Z, 2026-09-29T01:00:53Z, 2026-09-29T01:00:55Z, 2026-09-29T01:00:58Z, 2026-09-29T01:01:00Z, 2026-09-29T01:01:02Z, 2026-09-30T19:23:40Z, 2026-10-08T14:29:10Z, 2026-10-19T15:06:10Z, 2026-10-22T14:39:32Z, 2026-10-29T14:38:34Z, 2026-11-05T23:11:50Z, 2026-11-12T21:48:57Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 72232 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `spot_price` | The product's spot price that day at the hub the series names, USD a gallon | USD/gal | 72232 | 1986-06-02T00:00:00Z | 2026-11-11T00:00:00Z |

### `eia_product_supplied_monthly`

One month's product supplied (EIA's measure of consumption) of one petroleum product in the U.S. or a PADD, in the month or per day.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 71938.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/cons/psup U.S. Energy Information Administration, Petroleum Supply Monthly, product supplied (API v2, route petroleum/cons/psup) (https://www.eia.gov/petroleum/supply/monthly/)
- **Method note:** [`docs/methods/eia_product_supplied_monthly.md`](../methods/eia_product_supplied_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Petroleum Supply Monthly, product supplied (API v2). Via the Energy Research Warehouse (ERW), table `eia_product_supplied_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_product_supplied:<EIA series id> | none | text | for example eia_product_supplied:MAPUPP11, eia_product_supplied:MAPUPP12, eia_product_supplied:MAPUPP21; 702 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2017-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 115 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -5185.0 to 662039.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl, kbbl/d | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, the PADDs included | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 71938 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name | none | text | for example East Coast (PADD 1) Product Supplied  of Condensate and Scrubber Oil  (Thousand Barrels per Day), East Coast (PADD 1) Product Supplied  of Condensate and Scrubber Oil  (Thousand Barrels), East Coast (PADD 1) Product Supplied of Asphalt and Road Oil (Thousand Barrels per Day); 702 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/cons/psup | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/cons/psup/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=VPP&start=2017-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T23:04:16Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 71938 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `product_supplied` | Product supplied of the product in the month, thousand barrels | kbbl | 35969 | 2017-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `product_supplied_per_day` | Product supplied of the product, thousand barrels a day | kbbl/d | 35969 | 2017-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_recs_households`

One category of homes (by a household or housing characteristic, or all homes) and one figure from EIA's 2020 Residential Energy Consumption Survey tables CE4.1 and CE4.11.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2802.

- **Time:** ts_utc is 1 January of the survey year (2020) at 00:00:00Z (freq P1Y).
- **Revisions:** Written whole each run (write_snapshot) from the saved workbooks; EIA's revision is taken only when the saved copy is gone. vintage is each workbook's last-modified time.
- **Source:** eia:recs_2020 U.S. Energy Information Administration, 2020 Residential Energy Consumption Survey (RECS) (https://www.eia.gov/consumption/residential/data/2020/)
- **Method note:** [`docs/methods/eia_buildings_surveys.md`](../methods/eia_buildings_surveys.md)
- **Cite as:** U.S. Energy Information Administration (EIA). 2020 Residential Energy Consumption Survey (RECS): consumption and expenditures, Tables CE4.1, CE4.11. Via the Energy Research Warehouse (ERW), table `eia_recs_households`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: recs:<heading>_<category>, slugged; recs:all for all homes | none | text | for example recs:2020_annual_household_income_100_000_to_149_999, recs:2020_annual_household_income_10_000_to_19_999, recs:2020_annual_household_income_150_000_or_more; 77 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2020-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.0 to 232760000000.0; 1260 distinct | 0 |
| `unit` | The unit of the row's value | none | text | TBtu, USD, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row (census regions are categories) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2802 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The category as EIA prints it | none | text | for example $10,000 to $19,999, $100,000 to $149,999, $150,000 or more; 73 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:recs_2020 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/consumption/residential/data/2020/c&e/xls/ce4.1.xlsx, https://www.eia.gov/consumption/residential/data/2020/c&e/xls/ce4.11.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:37:29Z, 2026-10-23T18:37:30Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time from EIA's server | none | utc time | 2024-03-18T20:38:32Z, 2024-03-26T12:42:35Z | 0 |
| `x_heading` | The heading the category sits under (for example Housing unit type), as EIA prints it | none | text | 2020 annual household income, Census region and division, Census urban/rural classificatione, Climate regionf, Housing unit type, Main heating fuel, Number of household members, Ownership of housing unit, Payment method for energy bills, Total square footageh, Year of construction | 39: The all-homes row, which sits under no heading |
| `x_level` | The category's indent: 0 a category, 1 a part of the category above it, 2 a part of that (add level-0 rows only) | none | integer | 0, 1, 2 | 0 |
| `x_parent` | The category a level-1 or level-2 row is a part of | none | text | Midwest, Mountain, Northeast, Owned, Rentedg, South, Urban, West | 2136: A level-0 row (a part of no other category) |
| `x_table` | The RECS table the figure is read from (CE4.1 consumption, CE4.11 expenditures) | none | text | CE4.1, CE4.11 | 0 |

Variables (39):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption_electricity_air_conditioning` | Electricity consumption for air conditioning, trillion Btu (CE4.1) | TBtu | 76 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_electricity_other` | Electricity consumption for other end uses, trillion Btu (CE4.1) | TBtu | 77 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_electricity_refrigerators` | Electricity consumption by refrigerators, trillion Btu (CE4.1) | TBtu | 76 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_electricity_space_heating` | Electricity consumption for space heating, trillion Btu (CE4.1) | TBtu | 75 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_electricity_total` | Electricity consumption, all end uses, trillion Btu (CE4.1) | TBtu | 77 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_electricity_water_heating` | Electricity consumption for water heating, trillion Btu (CE4.1) | TBtu | 76 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_fuel_oil_kerosene_other` | Fuel oil and kerosene consumption for other end uses, trillion Btu (CE4.1) | TBtu | 44 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_fuel_oil_kerosene_space_heating` | Fuel oil and kerosene consumption for space heating, trillion Btu (CE4.1) | TBtu | 65 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_fuel_oil_kerosene_total` | Fuel oil and kerosene consumption, all end uses, trillion Btu (CE4.1) | TBtu | 66 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_fuel_oil_kerosene_water_heating` | Fuel oil and kerosene consumption for water heating, trillion Btu (CE4.1) | TBtu | 56 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_natural_gas_other` | Natural gas consumption for other end uses, trillion Btu (CE4.1) | TBtu | 76 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_natural_gas_space_heating` | Natural gas consumption for space heating, trillion Btu (CE4.1) | TBtu | 73 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_natural_gas_total` | Natural gas consumption, all end uses, trillion Btu (CE4.1) | TBtu | 77 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_natural_gas_water_heating` | Natural gas consumption for water heating, trillion Btu (CE4.1) | TBtu | 76 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_propane_other` | Propane consumption for other end uses, trillion Btu (CE4.1) | TBtu | 71 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_propane_space_heating` | Propane consumption for space heating, trillion Btu (CE4.1) | TBtu | 74 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_propane_total` | Propane consumption, all end uses, trillion Btu (CE4.1) | TBtu | 75 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_propane_water_heating` | Propane consumption for water heating, trillion Btu (CE4.1) | TBtu | 74 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `consumption_total` | Site energy consumption of all fuels, trillion Btu (CE4.1) | TBtu | 77 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_electricity_air_conditioning` | Expenditure on electricity for air conditioning, USD (CE4.11) | USD | 77 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_electricity_other` | Expenditure on electricity for other end uses, USD (CE4.11) | USD | 77 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_electricity_refrigerators` | Expenditure on electricity for refrigerators, USD (CE4.11) | USD | 77 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_electricity_space_heating` | Expenditure on electricity for space heating, USD (CE4.11) | USD | 76 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_electricity_total` | Expenditure on electricity, all end uses, USD (CE4.11) | USD | 77 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_electricity_water_heating` | Expenditure on electricity for water heating, USD (CE4.11) | USD | 76 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_fuel_oil_kerosene_other` | Expenditure on fuel oil and kerosene for other end uses, USD (CE4.11) | USD | 44 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_fuel_oil_kerosene_space_heating` | Expenditure on fuel oil and kerosene for space heating, USD (CE4.11) | USD | 65 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_fuel_oil_kerosene_total` | Expenditure on fuel oil and kerosene, all end uses, USD (CE4.11) | USD | 65 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_fuel_oil_kerosene_water_heating` | Expenditure on fuel oil and kerosene for water heating, USD (CE4.11) | USD | 56 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_natural_gas_other` | Expenditure on natural gas for other end uses, USD (CE4.11) | USD | 76 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_natural_gas_space_heating` | Expenditure on natural gas for space heating, USD (CE4.11) | USD | 74 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_natural_gas_total` | Expenditure on natural gas, all end uses, USD (CE4.11) | USD | 77 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_natural_gas_water_heating` | Expenditure on natural gas for water heating, USD (CE4.11) | USD | 76 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_propane_other` | Expenditure on propane for other end uses, USD (CE4.11) | USD | 73 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_propane_space_heating` | Expenditure on propane for space heating, USD (CE4.11) | USD | 73 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_propane_total` | Expenditure on propane, all end uses, USD (CE4.11) | USD | 75 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_propane_water_heating` | Expenditure on propane for water heating, USD (CE4.11) | USD | 73 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `expenditure_total` | Expenditure on all fuels, USD (CE4.11, billion dollars times 1,000,000,000) | USD | 77 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `housing_units` | Number of housing units (CE4.1, million housing units times 1,000,000) | count | 77 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |

### `eia_refinery_capacity_annual`

One refinery capacity figure as of 1 January of a year (operable distillation or downstream charge capacity of one process, or the number of refineries), for a state, PADD or the U.S.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 62804.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y); capacity as of that day.
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/pnp/cap1 U.S. Energy Information Administration, Refinery Capacity Report (API v2, route petroleum/pnp/cap1) (https://www.eia.gov/petroleum/refinerycapacity/)
- **Method note:** [`docs/methods/eia_refinery_capacity_annual.md`](../methods/eia_refinery_capacity_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Refinery Capacity Report, Form EIA-820 (API v2). Via the Energy Research Warehouse (ERW), table `eia_refinery_capacity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_refinery_capacity:<EIA series id> | none | text | for example eia_refinery_capacity:8_NA_8CCF_NGQ_4, eia_refinery_capacity:8_NA_8CCF_NGQ_5, eia_refinery_capacity:8_NA_8CCF_NPZ_4; 2009 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1982-01-01T00:00:00Z to 2026-01-01T00:00:00Z; 45 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 20092.219; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count, kbbl/d | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 44 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 62804 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name (the process, area and unit) | none | text | for example Alabama Number of Idle Refineries as of January 1 (Count), Alabama Number of Operable Refineries as of January 1 (Count), Alabama Number of Operating Refineries as of January 1 (Count); 2009 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/pnp/cap1 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/pnp/cap1/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&start=1982&end=1994, https://api.eia.gov/v2/petroleum/pnp/cap1/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&start=1995 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-22T02:42:37Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 62804 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity_per_calendar_day` | Capacity in barrels per calendar day (allowing for downtime), thousand barrels a day | kbbl/d | 11006 | 1982-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `capacity_per_stream_day` | Capacity in barrels per stream day (a day running without downtime), thousand barrels a day | kbbl/d | 45699 | 1982-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `refineries` | Number of refineries (operable, operating or idle, as the series names) | count | 6099 | 1982-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

### `eia_refinery_inputs_monthly`

One month's refinery and blender net input of one product in the U.S., a PADD or a refining district, in the month or per day.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 216010.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/pnp/inpt U.S. Energy Information Administration, Petroleum Supply Monthly, refinery and blender net input (API v2, route petroleum/pnp/inpt) (https://www.eia.gov/dnav/pet/pet_pnp_inpt_dc_nus_mbbl_m.htm)
- **Method note:** [`docs/methods/eia_refinery_inputs_monthly.md`](../methods/eia_refinery_inputs_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Petroleum Supply Monthly, refinery and blender net input (API v2). Via the Energy Research Warehouse (ERW), table `eia_refinery_inputs_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_refinery_inputs:<EIA series id> | none | text | for example eia_refinery_inputs:MBARI2A1, eia_refinery_inputs:MBARI2A2, eia_refinery_inputs:MBARI2B1; 1056 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2005-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 259 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -90065.0 to 633743.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl, kbbl/d | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, the PADDs and districts included | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 216010 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name (the product and area) | none | text | for example East Coast (PADD 1) Refinery and Blender Net Input of Aviation Gasoline Blending Components (Thousand Barrels per Day), East Coast (PADD 1) Refinery and Blender Net Input of Aviation Gasoline Blending Components (Thousand Barrels), East Coast (PADD 1) Refinery and Blender Net Input of Biodiesel (Thousand Barrels per Day); 1056 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/pnp/inpt | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/pnp/inpt/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=YIR&start=2005-01&end=2014-12, https://api.eia.gov/v2/petroleum/pnp/inpt/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=YIR&start=2015-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-22T06:14:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 216010 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `net_input` | Refinery and blender net input of the product in the month, thousand barrels | kbbl | 107999 | 2005-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_input_per_day` | Refinery and blender net input of the product, thousand barrels a day | kbbl/d | 108011 | 2005-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_refinery_production_monthly`

One month's refinery and blender net production of one product in the U.S., a PADD or a refining district, in the month or per day.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 326819.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/pnp/refp U.S. Energy Information Administration, Petroleum Supply Monthly, refinery and blender net production (API v2, route petroleum/pnp/refp) (https://www.eia.gov/dnav/pet/pet_pnp_refp_dc_nus_mbbl_m.htm)
- **Method note:** [`docs/methods/eia_refinery_production_monthly.md`](../methods/eia_refinery_production_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Petroleum Supply Monthly, refinery and blender net production (API v2). Via the Energy Research Warehouse (ERW), table `eia_refinery_production_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_refinery_production:<EIA series id> | none | text | for example eia_refinery_production:MAPRP2A1, eia_refinery_production:MAPRP2A2, eia_refinery_production:MAPRP2B1; 1488 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2005-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 259 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -37521.0 to 670493.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl, kbbl/d | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, the PADDs and districts included | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 326819 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name (the product and area) | none | text | for example East Coast (PADD 1) Refinery and Blender Net Production of Asphalt and Road Oil (Thousand Barrels per Day), East Coast (PADD 1) Refinery and Blender Net Production of Asphalt and Road Oil (Thousand Barrels), East Coast (PADD 1) Refinery and Blender Net Production of Aviation Gasoline (Thousand Barrels per Day); 1488 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/pnp/refp | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/pnp/refp/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=YPR&start=2005-01&end=2014-12, https://api.eia.gov/v2/petroleum/pnp/refp/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=YPR&start=2015-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-22T06:49:09Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 326819 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `net_production` | Refinery and blender net production of the product in the month, thousand barrels | kbbl | 163451 | 2005-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_production_per_day` | Refinery and blender net production of the product, thousand barrels a day | kbbl/d | 163368 | 2005-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_refinery_utilization_monthly`

One month's refinery gross input, capacity (operable, operating, idle) or utilization in the U.S., a PADD or a refining district.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 36672.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/pnp/unc U.S. Energy Information Administration, Petroleum Supply Monthly, refinery utilization and capacity (API v2, route petroleum/pnp/unc) (https://api.eia.gov/v2/petroleum/pnp/unc/)
- **Method note:** [`docs/methods/eia_refinery_utilization_monthly.md`](../methods/eia_refinery_utilization_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Petroleum Supply Monthly, refinery utilization and capacity (API v2). Via the Energy Research Warehouse (ERW), table `eia_refinery_utilization_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_refinery_utilization:<EIA series id> | none | text | for example eia_refinery_utilization:MGIRI2A2, eia_refinery_utilization:MGIRI2B2, eia_refinery_utilization:MGIRI2C2; 80 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1985-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 499 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 18976.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl/d, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, the PADDs and districts included | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 36672 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series description | none | text | for example Appalachian No. 1 Refinery District Gross Inputs to Refineries (Thousand Barrels Per Day), Appalachian No. 1 Refining District Idle Crude Oil Distillation Capacity  (Thousand Barrels per Day), Appalachian No. 1 Refining District Operable Crude Oil Distillation Capacity  (Thousand Barrels per Calendar Day); 80 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/pnp/unc | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/pnp/unc/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=YIY&facets%5Bprocess%5D%5B%5D=YRL&facets%5Bprocess%5D%5B%5D=YRO&facets%5Bprocess%5D%5B%5D=YRI&facets%5Bprocess%5D%5B%5D=YUP&start=1985-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T07:33:40Z, 2026-10-24T07:33:44Z, 2026-10-24T07:33:48Z, 2026-10-24T07:33:52Z, 2026-10-24T07:33:56Z, 2026-10-24T07:34:00Z, 2026-10-24T07:34:04Z, 2026-10-24T07:34:07Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 36672 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `gross_input` | Gross input to refineries, thousand barrels a day | kbbl/d | 7984 | 1985-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `idle_capacity` | Idle crude distillation capacity, thousand barrels a day (no row where operable equals operating capacity: nil, not unknown) | kbbl/d | 4736 | 1985-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `operable_capacity` | Operable crude distillation capacity, thousand barrels a day | kbbl/d | 7984 | 1985-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `operating_capacity` | Operating crude distillation capacity, thousand barrels a day | kbbl/d | 7984 | 1985-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `utilization` | Utilization of operable capacity, a ratio (EIA's percent divided by 100; above 1 where gross input exceeds operable capacity) | ratio | 7984 | 1985-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_refinery_weekly`

One week's refinery input of one product, operable capacity or utilization in the U.S. or a PADD, from EIA's Weekly Petroleum Status Report.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 50753.

- **Time:** ts_utc is EIA's week-ending date at 00:00:00Z (freq P1W), as in eia_petroleum_supply_weekly.
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:petroleum/pnp/wiup U.S. Energy Information Administration, Weekly Petroleum Status Report, refinery inputs and utilization (API v2, route petroleum/pnp/wiup) (https://www.eia.gov/petroleum/supply/weekly/)
- **Method note:** [`docs/methods/eia_refinery_weekly.md`](../methods/eia_refinery_weekly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Weekly Petroleum Status Report, refinery inputs and utilization (API v2). Via the Energy Research Warehouse (ERW), table `eia_refinery_weekly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_refinery:<EIA series id> | none | text | for example eia_refinery:WBCRI_NUS_2, eia_refinery:WBCRI_R10_2, eia_refinery:WBCRI_R20_2; 59 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z to 2026-10-16T00:00:00Z; 877 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -2844.0 to 18976.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl/d, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, the PADDs included | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 50753 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series name | none | text | for example East Coast (PADD 1) Gross Inputs into Refineries (Thousand Barrels per Day), East Coast (PADD 1) Operable Crude Oil Distillation Capacity  (Thousand Barrels per Calendar Day), East Coast (PADD 1) Percent Utilization of Refinery Operable Capacity; 59 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/pnp/wiup | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/pnp/wiup/data/?api_key=REDACTED&frequency=weekly&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=YIR&facets%5Bprocess%5D%5B%5D=YIY&facets%5Bprocess%5D%5B%5D=YRL&facets%5Bprocess%5D%5B%5D=YUP&start=2010-01-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T21:48:04Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 50753 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `net_input` | Refinery and blender net input of the product (YIR), thousand barrels a day | kbbl/d | 30802 | 2010-01-01T00:00:00Z | 2026-10-16T00:00:00Z |
| `operable_capacity` | Operable refinery capacity (YRL), thousand barrels a day | kbbl/d | 5152 | 2010-01-01T00:00:00Z | 2026-10-16T00:00:00Z |
| `refinery_net_input` | Refinery net input of the product (YIY), thousand barrels a day | kbbl/d | 10524 | 2010-01-01T00:00:00Z | 2026-10-16T00:00:00Z |
| `utilization` | Utilization of operable capacity (YUP), a ratio (EIA's percent divided by 100) | ratio | 4275 | 2010-06-04T00:00:00Z | 2026-10-16T00:00:00Z |

### `eia_regional_retail_fuel_prices`

One week's retail price of regular gasoline or No. 2 diesel in one region, state or city, from EIA's Gasoline and Diesel Fuel Update.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 16399.

- **Time:** ts_utc is EIA's survey Monday at 00:00:00Z (freq P1W).
- **Revisions:** Rewritten whole by each run (the file is deleted and the history from 2019 written again), so EIA's revisions are taken; the copy held was rebuilt from the ERW archive by restore_tables.py. vintage is not filled.
- **Source:** eia:petroleum/pri/gnd:regional EIA, Gasoline and Diesel Fuel Update (weekly retail prices) (https://www.eia.gov/petroleum/gasdiesel/)
- **Method note:** [`docs/methods/eia_regional_retail_fuel_prices.md`](../methods/eia_regional_retail_fuel_prices.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Gasoline and Diesel Fuel Update (weekly retail prices). Via the Energy Research Warehouse (ERW), table `eia_regional_retail_fuel_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:<EIA series id> | none | text | for example eia:EMD_EPD2D_PTE_NUS_DPG, eia:EMD_EPD2D_PTE_R10_DPG, eia:EMD_EPD2D_PTE_R1X_DPG; 40 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-07T00:00:00Z to 2026-11-09T00:00:00Z; 410 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.397 to 8.246; 3995 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/gal | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US for the nation, US-<state> for a state; empty for a PADD, a sub-PADD, PADD 5 except California, and a city | none | text | US, US-CA, US-CO, US-FL, US-MA, US-MN, US-NY, US-OH, US-TX, US-WA | 11479 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 16399 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's area name (region, state or city) | none | text | for example BOSTON, CALIFORNIA, CHICAGO; 29 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/pri/gnd:regional | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/pri/gnd/data/?frequency=weekly&data%5B0%5D=value&facets%5Bproduct%5D%5B%5D=EPMR&facets%5Bproduct%5D%5B%5D=EPD2D&start=2019-01-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000, https://api.eia.gov/v2/petroleum/pri/gnd/data/?frequency=weekly&data%5B0%5D=value&facets%5Bproduct%5D%5B%5D=EPMR&facets%5Bproduct%5D%5B%5D=EPD2D&start=2019-01-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=10000&length=5000, https://api.eia.gov/v2/petroleum/pri/gnd/data/?frequency=weekly&data%5B0%5D=value&facets%5Bproduct%5D%5B%5D=EPMR&facets%5Bproduct%5D%5B%5D=EPD2D&start=2019-01-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=15000&length=5000, https://api.eia.gov/v2/petroleum/pri/gnd/data/?frequency=weekly&data%5B0%5D=value&facets%5Bproduct%5D%5B%5D=EPMR&facets%5Bproduct%5D%5B%5D=EPD2D&start=2019-01-01&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=5000&length=5000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T08:18:26Z, 2026-10-06T08:18:27Z, 2026-10-06T08:18:28Z, 2026-10-07T14:44:53Z, 2026-10-14T15:39:21Z, 2026-10-22T15:06:39Z, 2026-10-27T14:59:29Z, 2026-11-05T23:50:12Z, 2026-11-12T22:15:15Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 16399 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `retail_price` | Weekly retail price of regular gasoline or No. 2 diesel in the area, USD a gallon | USD/gal | 16399 | 2019-01-07T00:00:00Z | 2026-11-09T00:00:00Z |

### `eia_retail_electricity_prices`

One state's (or census division's, or the nation's) monthly average retail price of electricity in one sector.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 114574.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Each run asks for the full history and merges it on (entity, variable, ts_utc), keeping EIA's newest value; a row EIA stops giving is kept. The copy held was rebuilt from the ERW archive by restore_tables.py. vintage is not filled.
- **Source:** eia:electricity/retail-sales Electric Power Monthly: average retail price of electricity (retail-sales) (https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a)
- **Method note:** [`docs/methods/eia_retail_electricity_prices.md`](../methods/eia_retail_electricity_prices.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Electric Power Monthly: retail sales of electricity and number of customers by state and sector (Form EIA-861M). Via the Energy Research Warehouse (ERW), table `eia_retail_electricity_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:retail_price:<stateid>:<sectorid> | none | text | for example eia:retail_price:AK:ALL, eia:retail_price:AK:COM, eia:retail_price:AK:IND; 372 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 308 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 1166.7; 3211 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation; empty for an EIA census division | none | text | for example US, US-AK, US-AL; 52 distinct | 18480 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 114574 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: EIA's names (state, sector) are in the header's Series line | none | empty | no cell holds a value | 114574 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:electricity/retail-sales | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=0&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=10000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=100000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=105000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=110000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=15000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=20000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=25000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=30000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=35000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=40000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=45000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=5000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=50000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=55000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=60000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=65000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=70000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=75000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=80000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=85000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=90000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=price&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=95000&length=5000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-29T01:01:16Z to 2026-10-23T14:40:15Z; 26 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 114574 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `retail_price` | Average retail price of electricity in the sector, USD per MWh (EIA's cents per kWh times 10) | USD/MWh | 114574 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `eia_retail_fuel_prices`

One week's U.S. retail price of gasoline (regular or all grades) or No. 2 diesel, from EIA's Gasoline and Diesel Fuel Update.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 5343.

- **Time:** ts_utc is the week date EIA reports at 00:00:00Z (freq P1W).
- **Revisions:** Each run asks for the full history and merges it on (entity, variable, ts_utc), keeping EIA's newest value; a row EIA stops giving is kept. The copy held was rebuilt from the ERW archive by restore_tables.py. vintage is not filled.
- **Source:** eia:petroleum/pri/gnd Gasoline and Diesel Fuel Update (retail prices) (https://www.eia.gov/dnav/pet/pet_pri_gnd_dcus_nus_w.htm)
- **Method note:** [`docs/methods/eia_retail_fuel_prices.md`](../methods/eia_retail_fuel_prices.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Gasoline and Diesel Fuel Update (retail prices). Via the Energy Research Warehouse (ERW), table `eia_retail_fuel_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:<EIA series id> (EMM_EPMR_PTE_NUS_DPG regular gasoline, EMM_EPM0_PTE_NUS_DPG all grades, EMD_EPD2D_PTE_NUS_DPG No. 2 diesel) | none | text | eia:EMD_EPD2D_PTE_NUS_DPG, eia:EMM_EPM0_PTE_NUS_DPG, eia:EMM_EPMR_PTE_NUS_DPG | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-08-20T00:00:00Z to 2026-11-09T00:00:00Z; 1885 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.907 to 6.529; 2569 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/gal | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5343 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: EIA's series names are in the header's Series line | none | empty | no cell holds a value | 5343 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:petroleum/pri/gnd | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/petroleum/pri/gnd/data/?api_key=REDACTED&frequency=weekly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000&facets%5Bseries%5D%5B%5D=EMM_EPMR_PTE_NUS_DPG&facets%5Bseries%5D%5B%5D=EMM_EPM0_PTE_NUS_DPG&facets%5Bseries%5D%5B%5D=EMD_EPD2D_PTE_NUS_DPG, https://api.eia.gov/v2/petroleum/pri/gnd/data/?api_key=REDACTED&frequency=weekly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=series&sort%5B1%5D%5Bdirection%5D=asc&offset=5000&length=5000&facets%5Bseries%5D%5B%5D=EMM_EPMR_PTE_NUS_DPG&facets%5Bseries%5D%5B%5D=EMM_EPM0_PTE_NUS_DPG&facets%5Bseries%5D%5B%5D=EMD_EPD2D_PTE_NUS_DPG | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-29T01:02:32Z, 2026-09-29T01:02:34Z, 2026-09-30T19:24:53Z, 2026-10-06T14:24:32Z, 2026-10-15T15:10:10Z, 2026-10-22T14:42:39Z, 2026-10-27T14:42:33Z, 2026-11-05T23:12:43Z, 2026-11-12T21:49:53Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5343 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `retail_price` | U.S. weekly retail price of the fuel the series names, USD a gallon | USD/gal | 5343 | 1990-08-20T00:00:00Z | 2026-11-09T00:00:00Z |

### `eia_retail_sales_monthly`

One state's (or census division's, or the nation's) monthly retail sales of electricity, or number of customers, in one sector (Form EIA-861M).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 228947.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Each run asks for the full history and merges it on (entity, variable, ts_utc), keeping EIA's newest value; a row EIA stops giving is kept. The copy held was rebuilt from the ERW archive by restore_tables.py. vintage is not filled.
- **Source:** eia:electricity/retail-sales Electric Power Monthly: retail sales of electricity and number of customers by state and sector (Form EIA-861M) (https://www.eia.gov/electricity/data/eia861m/)
- **Method note:** [`docs/methods/eia_retail_sales_monthly.md`](../methods/eia_retail_sales_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Electric Power Monthly: retail sales of electricity and number of customers by state and sector (Form EIA-861M). Via the Energy Research Warehouse (ERW), table `eia_retail_sales_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:retail_sales:<stateid>:<sectorid> or eia:customers:<stateid>:<sectorid>; sectors RES, COM, IND, TRA, OTH (EIA's older series), ALL | none | text | for example eia:customers:AK:ALL, eia:customers:AK:COM, eia:customers:AK:IND; 744 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 308 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 415228509.23; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation; empty for an EIA census division | none | text | for example US, US-AK, US-AL; 52 distinct | 36904 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 228947 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: EIA's names (state, sector) are in the header's Series line | none | empty | no cell holds a value | 228947 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:electricity/retail-sales | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=customers&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=0&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=customers&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=10000&length=5000, https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=customers&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=stateid&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=sectorid&sort%5B2%5D%5Bdirection%5D=asc&offset=100000&length=5000; 46 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-29T01:02:35Z to 2026-10-23T14:42:03Z; 52 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 228947 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `customers` | Number of retail electricity customers in the sector, EIA's count as published (0 before January 2008) | count | 114393 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `retail_sales` | Electricity sold to retail customers in the sector in the month, MWh (EIA's million kWh times 1,000) | MWh | 114554 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `eia_sector_energy_consumption_monthly`

One month's U.S. energy consumption of one source by the industrial or commercial sector, from EIA's Monthly Energy Review (Tables 2.3 and 2.4).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 9002.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Each run asks for the full history and merges it on (entity, variable, ts_utc), keeping EIA's newest value; a row EIA stops giving is kept. The copy held was rebuilt from the ERW archive by restore_tables.py. vintage is not filled.
- **Source:** eia:total-energy Monthly Energy Review, tables 1.1 to 1.3 (primary energy: eia_primary_energy_monthly) and 2.3 and 2.4 (commercial and industrial energy consumption: eia_sector_energy_consumption_monthly) (https://www.eia.gov/totalenergy/data/monthly/)
- **Method note:** [`docs/methods/eia_sector_energy_consumption_monthly.md`](../methods/eia_sector_energy_consumption_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Monthly Energy Review, tables 1.1 to 1.3 (primary energy: eia_primary_energy_monthly) and 2.3 and 2.4 (commercial and industrial energy consumption: eia_sector_energy_consumption_monthly). Via the Energy Research Warehouse (ERW), table `eia_sector_energy_consumption_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:<Monthly Energy Review series id (MSN)>, for example CLICBUS coal consumed by the industrial sector | none | text | eia:CLICBUS, eia:ESCCBUS, eia:ESICBUS, eia:LOICBUS, eia:NNCCBUS, eia:NNICBUS, eia:PACCBUS, eia:PAICBUS, eia:RECCBUS, eia:REICBUS, eia:TECCBUS, eia:TEICBUS, eia:TNCCBUS, eia:TNICBUS | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1973-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 643 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.515 to 3019.085; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | TBtu | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 9002 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: EIA's series names are in the header's Series line | none | empty | no cell holds a value | 9002 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:total-energy | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/total-energy/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=msn&sort%5B1%5D%5Bdirection%5D=asc&offset=0&length=5000&facets%5Bmsn%5D%5B%5D=TEICBUS&facets%5Bmsn%5D%5B%5D=TNICBUS&facets%5Bmsn%5D%5B%5D=ESICBUS&facets%5Bmsn%5D%5B%5D=LOICBUS&facets%5Bmsn%5D%5B%5D=NNICBUS&facets%5Bmsn%5D%5B%5D=PAICBUS&facets%5Bmsn%5D%5B%5D=CLICBUS&facets%5Bmsn%5D%5B%5D=REICBUS&facets%5Bmsn%5D%5B%5D=TECCBUS&facets%5Bmsn%5D%5B%5D=TNCCBUS&facets%5Bmsn%5D%5B%5D=ESCCBUS&facets%5Bmsn%5D%5B%5D=NNCCBUS&facets%5Bmsn%5D%5B%5D=PACCBUS&facets%5Bmsn%5D%5B%5D=RECCBUS, https://api.eia.gov/v2/total-energy/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=value&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=msn&sort%5B1%5D%5Bdirection%5D=asc&offset=5000&length=5000&facets%5Bmsn%5D%5B%5D=TEICBUS&facets%5Bmsn%5D%5B%5D=TNICBUS&facets%5Bmsn%5D%5B%5D=ESICBUS&facets%5Bmsn%5D%5B%5D=LOICBUS&facets%5Bmsn%5D%5B%5D=NNICBUS&facets%5Bmsn%5D%5B%5D=PAICBUS&facets%5Bmsn%5D%5B%5D=CLICBUS&facets%5Bmsn%5D%5B%5D=REICBUS&facets%5Bmsn%5D%5B%5D=TECCBUS&facets%5Bmsn%5D%5B%5D=TNCCBUS&facets%5Bmsn%5D%5B%5D=ESCCBUS&facets%5Bmsn%5D%5B%5D=NNCCBUS&facets%5Bmsn%5D%5B%5D=PACCBUS&facets%5Bmsn%5D%5B%5D=RECCBUS | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-27T08:12:18Z, 2026-09-27T08:12:25Z, 2026-09-30T19:27:13Z, 2026-10-30T14:48:47Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 9002 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `energy_consumption` | Energy consumed by the sector from the source the series names, trillion Btu as EIA publishes it | TBtu | 9002 | 1973-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `eia_seds_industrial_annual`

One state's (or the nation's) yearly figure for the industrial sector from EIA's State Energy Data System (consumption of one energy source, expenditures, or the average price).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 30940.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot); a saved page is reused unless asked fresh. vintage is not filled.
- **Source:** eia:seds_industrial U.S. Energy Information Administration, State Energy Data System (API v2, route seds) (https://www.eia.gov/state/seds/)
- **Method note:** [`docs/methods/industry_page.md`](../methods/industry_page.md)
- **Cite as:** U.S. Energy Information Administration (EIA). State Energy Data System (API v2): the industrial sector's consumption, expenditures and price by source and state. Via the Energy Research Warehouse (ERW), table `eia_seds_industrial_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_seds_ind:<seriesId>:<state> | none | text | for example eia_seds_ind:CLICB:AK, eia_seds_ind:CLICB:AL, eia_seds_ind:CLICB:AR; 884 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 35 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 285478100000.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | TBtu, USD, USD/MMBtu | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 30940 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's name of the series | none | text | All petroleum products consumed by the industrial sector, All petroleum products total expenditures in the industrial sector, Coal consumed by the industrial sector, Coal expenditures in the industrial sector, Distillate fuel oil consumed by the industrial sector, Electricity expenditures in the industrial sector, End-use energy consumption in the industrial sector, Hydrocarbon gas liquids consumed by the industrial sector, Natural gas expenditures in the industrial sector (including supplemental gaseous fuels), Petroleum coke consumed in the industrial sector, Renewable energy sources consumed by the industrial sector, Residual fuel oil consumed by the industrial sector, The industrial sector's share of electrical system energy losses, Total energy average price in the industrial sector, Total energy consumption in the industrial sector, Total energy expenditures in the industrial sector, Wood and waste consumed in the industrial sector | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:seds_industrial | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/seds/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BseriesId%5D%5B%5D=TEICB&facets%5BseriesId%5D%5B%5D=TNICB&facets%5BseriesId%5D%5B%5D=CLICB&facets%5BseriesId%5D%5B%5D=PAICB&facets%5BseriesId%5D%5B%5D=HLICB&facets%5BseriesId%5D%5B%5D=DFICB&facets%5BseriesId%5D%5B%5D=RFICB&facets%5BseriesId%5D%5B%5D=PCICB&facets%5BseriesId%5D%5B%5D=REICB&facets%5BseriesId%5D%5B%5D=WWICB&facets%5BseriesId%5D%5B%5D=LOICB&facets%5BseriesId%5D%5B%5D=TEICV&facets%5BseriesId%5D%5B%5D=CLICV&facets%5BseriesId%5D%5B%5D=PAICV&facets%5BseriesId%5D%5B%5D=NGICV&facets%5BseriesId%5D%5B%5D=ESICV&facets%5BseriesId%5D%5B%5D=TEICD&start=1990&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=seriesId&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=stateId&sort%5B2%5D%5Bdirection%5D=asc&length=5000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T11:34:39Z, 2026-11-19T11:34:43Z, 2026-11-19T11:34:47Z, 2026-11-19T11:34:52Z, 2026-11-19T11:34:56Z, 2026-11-19T11:35:01Z, 2026-11-19T11:35:05Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 30940 |
| `x_series` | EIA's SEDS series identifier (for example CLICB coal consumed by the industrial sector) (the source's name: seriesId) | none | text | CLICB, CLICV, DFICB, ESICV, HLICB, LOICB, NGICV, PAICB, PAICV, PCICB, REICB, RFICB, TEICB, TEICD, TEICV, TNICB, WWICB | 0 |
| `x_source` | The energy source of the series in the ERW's words (coal, petroleum, natural gas, electricity, total and the others) | none | text | coal, distillate_fuel_oil, electrical_system_losses, electricity, end_use_total, hgl, natural_gas, petroleum, petroleum_coke, renewables, residual_fuel_oil, total, wood_and_waste | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` | The industrial sector's consumption of the energy source, trillion Btu (EIA's billion Btu times 0.001) | TBtu | 20020 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `expenditures` | The industrial sector's expenditures on the energy source, nominal USD (EIA's million dollars times 1,000,000) | USD | 9100 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `price` | The industrial sector's total energy average price, USD per million Btu (TEICD) | USD/MMBtu | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_seds_residential_annual`

One state's (or the nation's) yearly figure for the residential sector from EIA's State Energy Data System (expenditures by source, total consumption, average price) or the state's population.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 20020.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:seds_residential U.S. Energy Information Administration, State Energy Data System (API v2, route seds) (https://www.eia.gov/state/seds/)
- **Method note:** [`docs/methods/eia_seds_residential_annual.md`](../methods/eia_seds_residential_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). State Energy Data System (API v2): the residential sector's expenditures, consumption and price, and population. Via the Energy Research Warehouse (ERW), table `eia_seds_residential_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_seds_res:<seriesId>:<state> | none | text | for example eia_seds_res:DFRCV:AK, eia_seds_res:DFRCV:AL, eia_seds_res:DFRCV:AR; 572 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 35 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 333267900000.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | TBtu, USD, USD/MMBtu, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 20020 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's name of the series | none | text | All petroleum products total expenditures in the residential sector, Distillate fuel oil expenditures in the residential sector, Electricity expenditures in the residential sector, Hydrocarbon gas liquids expenditures in the residential sector, Kerosene expenditures in the residential sector, Natural gas expenditures in the residential sector (including supplemental gaseous fuels), Resident population including Armed Forces, Total energy average price in the residential sector, Total energy consumption in the residential sector, Total energy expenditures in the residential sector, Wood expenditures in the residential sector | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:seds_residential | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/seds/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BseriesId%5D%5B%5D=TERCV&facets%5BseriesId%5D%5B%5D=ESRCV&facets%5BseriesId%5D%5B%5D=NGRCV&facets%5BseriesId%5D%5B%5D=PARCV&facets%5BseriesId%5D%5B%5D=DFRCV&facets%5BseriesId%5D%5B%5D=HLRCV&facets%5BseriesId%5D%5B%5D=KSRCV&facets%5BseriesId%5D%5B%5D=WDRCV&facets%5BseriesId%5D%5B%5D=TERCB&facets%5BseriesId%5D%5B%5D=TERCD&facets%5BseriesId%5D%5B%5D=TPOPP&start=1990&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=seriesId&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=stateId&sort%5B2%5D%5Bdirection%5D=asc&length=5000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T21:38:44Z, 2026-10-23T21:38:48Z, 2026-10-23T21:38:53Z, 2026-10-23T21:38:57Z, 2026-10-23T21:39:01Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 20020 |
| `x_series` | EIA's SEDS series identifier (for example ESRCV electricity expenditures in the residential sector) (the source's name: seriesId) | none | text | DFRCV, ESRCV, HLRCV, KSRCV, NGRCV, PARCV, TERCB, TERCD, TERCV, TPOPP, WDRCV | 0 |
| `x_source` | The energy source of the series in the ERW's words (electricity, natural_gas, petroleum, wood, total and the others) | none | text | distillate_fuel_oil, electricity, hgl, kerosene, natural_gas, petroleum, total, wood | 1820: The population rows (TPOPP), which have no energy source |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` | Residential total energy consumption (TERCB), trillion Btu (EIA's billion Btu times 0.001) | TBtu | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `expenditures` | Residential expenditures on the energy source, nominal USD (EIA's million dollars times 1,000,000) | USD | 14560 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `population` | The state's resident population (TPOPP), a count (EIA's thousands times 1,000) | count | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `price` | Residential total energy average price (TERCD), USD per million Btu | USD/MMBtu | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_seds_state_energy`

One state's (or the nation's) yearly figure of one SEDS series (consumption by source or sector, an electricity or gas price, or expenditures).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 49140.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot), so EIA's revisions replace the earlier figures. vintage is not filled.
- **Source:** eia:seds U.S. Energy Information Administration, State Energy Data System (API v2, route seds) (https://www.eia.gov/state/seds/)
- **Method note:** [`docs/methods/eia_seds_state_energy.md`](../methods/eia_seds_state_energy.md)
- **Cite as:** U.S. Energy Information Administration (EIA). State Energy Data System (API v2). Via the Energy Research Warehouse (ERW), table `eia_seds_state_energy`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_seds:<seriesId>:<state>; the series id says what the row measures | none | text | for example eia_seds:CLTCB:AK, eia_seds:CLTCB:AL, eia_seds:CLTCB:AR; 1404 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 35 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1.309 to 1719511200000.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | TBtu, USD, USD/MMBtu | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 49140 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's name of the series | none | text | for example All petroleum products total consumption, Coal total consumption, Electricity average price, all sectors; 27 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:seds | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/seds/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BseriesId%5D%5B%5D=TETCB&facets%5BseriesId%5D%5B%5D=ESTCB&facets%5BseriesId%5D%5B%5D=NGTCB&facets%5BseriesId%5D%5B%5D=CLTCB&facets%5BseriesId%5D%5B%5D=PATCB&facets%5BseriesId%5D%5B%5D=RETCB&facets%5BseriesId%5D%5B%5D=NUETB&facets%5BseriesId%5D%5B%5D=ESRCD&facets%5BseriesId%5D%5B%5D=ESCCD&facets%5BseriesId%5D%5B%5D=ESICD&facets%5BseriesId%5D%5B%5D=ESTCD&facets%5BseriesId%5D%5B%5D=ESTCV&facets%5BseriesId%5D%5B%5D=TETCV&facets%5BseriesId%5D%5B%5D=ESRCB&facets%5BseriesId%5D%5B%5D=ESCCB&facets%5BseriesId%5D%5B%5D=ESICB&facets%5BseriesId%5D%5B%5D=ESACB&facets%5BseriesId%5D%5B%5D=NGRCB&facets%5BseriesId%5D%5B%5D=NGCCB&facets%5BseriesId%5D%5B%5D=NGICB&facets%5BseriesId%5D%5B%5D=NGEIB&facets%5BseriesId%5D%5B%5D=NGACB&facets%5BseriesId%5D%5B%5D=NGRCD&facets%5BseriesId%5D%5B%5D=NGCCD&facets%5BseriesId%5D%5B%5D=NGICD&facets%5BseriesId%5D%5B%5D=NGEID&facets%5BseriesId%5D%5B%5D=NGTCD&start=1990&length=5000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T21:54:13Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 49140 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `value` | The SEDS series the entity names (consumption in trillion Btu, a price in USD per million Btu, or expenditures in USD); the unit column says which | TBtu; USD; USD/MMBtu | 49140 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_shale_gas_reserves_annual`

One year's shale gas proved reserves, reserves-based production, or a change in reserves, for the U.S., a state or a reporting district (2007 to 2021).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 4455.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y); reserves are as of 31 December.
- **Revisions:** Rewritten whole by each run (write_snapshot); EIA's route ends in 2021. vintage is not filled.
- **Source:** eia:natural-gas/enr/shalegas U.S. Energy Information Administration, U.S. Crude Oil and Natural Gas Proved Reserves, shale gas (API v2, route natural-gas/enr/shalegas) (https://api.eia.gov/v2/natural-gas/enr/shalegas/)
- **Method note:** [`docs/methods/eia_shale_gas_reserves_annual.md`](../methods/eia_shale_gas_reserves_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). U.S. Crude Oil and Natural Gas Proved Reserves, shale gas (API v2). Via the Energy Research Warehouse (ERW), table `eia_shale_gas_reserves_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_shale_gas_reserves:<EIA series id> | none | text | for example eia_shale_gas_reserves:RES_EPG0_R5301_NUS_BCF, eia_shale_gas_reserves:RES_EPG0_R5301_R48_BCF, eia_shale_gas_reserves:RES_EPG0_R5301_RCAC_BCF; 469 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -6298.0 to 393779.0; 1594 distinct | 0 |
| `unit` | The unit of the row's value | none | text | bcf | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation | none | text | US, US-AK, US-AL, US-AR, US-CA, US-CO, US-KS, US-KY, US-LA, US-MI, US-MS, US-MT, US-ND, US-NM, US-OH, US-OK, US-PA, US-TX, US-VA, US-WV, US-WY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 4455 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's description | none | text | for example Alabama (with State Offshore) Shale Production (Billion Cubic Feet), Alabama (with State Offshore) Shale Proved Reserves (Billion Cubic Feet), Alabama (with State Offshore) Shale Proved Reserves Acquisitions (Billion Cubic Feet); 469 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:natural-gas/enr/shalegas | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/natural-gas/enr/shalegas/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5Bprocess%5D%5B%5D=R5301&facets%5Bprocess%5D%5B%5D=R5302&facets%5Bprocess%5D%5B%5D=R5303&facets%5Bprocess%5D%5B%5D=R5304&facets%5Bprocess%5D%5B%5D=R5305&facets%5Bprocess%5D%5B%5D=R5306&facets%5Bprocess%5D%5B%5D=R5307&facets%5Bprocess%5D%5B%5D=R5307A&facets%5Bprocess%5D%5B%5D=R5308&facets%5Bprocess%5D%5B%5D=R5309&facets%5Bprocess%5D%5B%5D=R53R02&start=2007 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T03:51:02Z, 2026-10-24T03:51:06Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 4455 |

Variables (11):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `acquisitions` | Shale gas proved reserves acquired, billion cubic feet | bcf | 478 | 2009-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `adjustments` | Adjustments to shale gas proved reserves, billion cubic feet | bcf | 478 | 2009-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `extensions` | Extensions of shale gas proved reserves, billion cubic feet | bcf | 251 | 2009-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `extensions_and_discoveries` | Extensions and discoveries of shale gas proved reserves, billion cubic feet | bcf | 226 | 2016-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `new_field_discoveries` | New field discoveries of shale gas, billion cubic feet | bcf | 251 | 2009-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `new_reservoir_discoveries_in_old_fields` | New reservoir discoveries of shale gas in old fields (R5309), billion cubic feet | bcf | 251 | 2009-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `proved_reserves` | Shale gas proved reserves at the year's end, billion cubic feet | bcf | 543 | 2007-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `reserves_based_production` | Shale gas production counted against reserves (R5302), billion cubic feet | bcf | 543 | 2007-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `revision_decreases` | Revision decreases of shale gas proved reserves, billion cubic feet | bcf | 478 | 2009-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `revision_increases` | Revision increases of shale gas proved reserves, billion cubic feet | bcf | 478 | 2009-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `sales` | Shale gas proved reserves sold, billion cubic feet | bcf | 478 | 2009-01-01T00:00:00Z | 2021-01-01T00:00:00Z |

### `eia_state_capacity_annual`

One state's (or the nation's) net summer generating capacity of one producer type and one energy source at one year, from EIA's State Electricity Profiles.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 56719.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:electricity/state-electricity-profiles/capability U.S. Energy Information Administration, State Electricity Profiles, net summer capacity (API v2, route electricity/state-electricity-profiles/capability) (https://www.eia.gov/electricity/state/)
- **Method note:** [`docs/methods/eia_state_capacity_annual.md`](../methods/eia_state_capacity_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). State Electricity Profiles, net summer capacity (API v2). Via the Energy Research Warehouse (ERW), table `eia_state_capacity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_state_capacity:<state>:<producertypeid>:<energysourceid>; producer types EU, IPP, TOT (both); sources ALL, a fuel or a part of one | none | text | for example eia_state_capacity:AK:EU:ALL, eia_state_capacity:AK:EU:BAT, eia_state_capacity:AK:EU:COL; 2671 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 35 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 1230416.3; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 56719 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's descriptions (state, sector, source) | none | text | for example Alabama, All sectors, All, Alabama, All sectors, Battery, Alabama, All sectors, Coal; 2671 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:electricity/state-electricity-profiles/capability | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/electricity/state-electricity-profiles/capability/data/?api_key=REDACTED&frequency=annual&data%5B%5D=capability&start=1990 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T21:14:01Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 56719 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `net_summer_capacity` | Net summer capacity (the most a plant can deliver in summer, less its own use), MW; a sum takes one level and leaves ALL and TOT out | MW | 56719 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_state_generation_monthly`

One state's (or census region's, or the nation's) monthly net electricity generation from one energy source, all sectors (Form EIA-923).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 201076.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Each run asks for the full history and merges it on (entity, variable, ts_utc), keeping EIA's newest value; a row EIA stops giving is kept. The copy held was rebuilt from the ERW archive by restore_tables.py. vintage is not filled.
- **Source:** eia:electricity/electric-power-operational-data Electric Power Operational Data: net generation by state, sector and energy source (Form EIA-923, Electric Power Monthly) (https://www.eia.gov/electricity/data/browser/)
- **Method note:** [`docs/methods/eia_state_generation_monthly.md`](../methods/eia_state_generation_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Electric Power Operational Data: net generation by state, sector and energy source (Form EIA-923, Electric Power Monthly). Via the Energy Research Warehouse (ERW), table `eia_state_generation_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:generation:<location>:<fueltypeid>; ALL is the sum of the sources except DPV (estimated small-scale solar) | none | text | for example eia:generation:AK:ALL, eia:generation:AK:BIO, eia:generation:AK:COW; 759 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 308 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -997855.0 to 451966701.13; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation; empty for an EIA census region | none | text | for example US, US-AK, US-AL; 53 distinct | 40208 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 201076 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: EIA's names (location, source) are in the header's Series line | none | empty | no cell holds a value | 201076 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:electricity/electric-power-operational-data | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=generation&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=location&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=fueltypeid&sort%5B2%5D%5Bdirection%5D=asc&offset=0&length=5000&facets%5Bsectorid%5D%5B%5D=99&facets%5Bfueltypeid%5D%5B%5D=ALL&facets%5Bfueltypeid%5D%5B%5D=COW&facets%5Bfueltypeid%5D%5B%5D=PET&facets%5Bfueltypeid%5D%5B%5D=NG&facets%5Bfueltypeid%5D%5B%5D=OOG&facets%5Bfueltypeid%5D%5B%5D=NUC&facets%5Bfueltypeid%5D%5B%5D=HYC&facets%5Bfueltypeid%5D%5B%5D=HPS&facets%5Bfueltypeid%5D%5B%5D=WND&facets%5Bfueltypeid%5D%5B%5D=SUN&facets%5Bfueltypeid%5D%5B%5D=GEO&facets%5Bfueltypeid%5D%5B%5D=BIO&facets%5Bfueltypeid%5D%5B%5D=OTH&facets%5Bfueltypeid%5D%5B%5D=DPV, https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=generation&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=location&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=fueltypeid&sort%5B2%5D%5Bdirection%5D=asc&offset=10000&length=5000&facets%5Bsectorid%5D%5B%5D=99&facets%5Bfueltypeid%5D%5B%5D=ALL&facets%5Bfueltypeid%5D%5B%5D=COW&facets%5Bfueltypeid%5D%5B%5D=PET&facets%5Bfueltypeid%5D%5B%5D=NG&facets%5Bfueltypeid%5D%5B%5D=OOG&facets%5Bfueltypeid%5D%5B%5D=NUC&facets%5Bfueltypeid%5D%5B%5D=HYC&facets%5Bfueltypeid%5D%5B%5D=HPS&facets%5Bfueltypeid%5D%5B%5D=WND&facets%5Bfueltypeid%5D%5B%5D=SUN&facets%5Bfueltypeid%5D%5B%5D=GEO&facets%5Bfueltypeid%5D%5B%5D=BIO&facets%5Bfueltypeid%5D%5B%5D=OTH&facets%5Bfueltypeid%5D%5B%5D=DPV, https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?api_key=REDACTED&frequency=monthly&data%5B0%5D=generation&sort%5B0%5D%5Bcolumn%5D=period&sort%5B0%5D%5Bdirection%5D=asc&sort%5B1%5D%5Bcolumn%5D=location&sort%5B1%5D%5Bdirection%5D=asc&sort%5B2%5D%5Bcolumn%5D=fueltypeid&sort%5B2%5D%5Bdirection%5D=asc&offset=100000&length=5000&facets%5Bsectorid%5D%5B%5D=99&facets%5Bfueltypeid%5D%5B%5D=ALL&facets%5Bfueltypeid%5D%5B%5D=COW&facets%5Bfueltypeid%5D%5B%5D=PET&facets%5Bfueltypeid%5D%5B%5D=NG&facets%5Bfueltypeid%5D%5B%5D=OOG&facets%5Bfueltypeid%5D%5B%5D=NUC&facets%5Bfueltypeid%5D%5B%5D=HYC&facets%5Bfueltypeid%5D%5B%5D=HPS&facets%5Bfueltypeid%5D%5B%5D=WND&facets%5Bfueltypeid%5D%5B%5D=SUN&facets%5Bfueltypeid%5D%5B%5D=GEO&facets%5Bfueltypeid%5D%5B%5D=BIO&facets%5Bfueltypeid%5D%5B%5D=OTH&facets%5Bfueltypeid%5D%5B%5D=DPV; 41 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-29T01:05:09Z to 2026-10-23T14:44:57Z; 46 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 201076 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `net_generation` | Net electricity generation from the source, all sectors, MWh (EIA's thousand MWh times 1,000) | MWh | 201076 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `eia_state_source_disposition_annual`

One state's (or the nation's) yearly electricity supply or disposition figure, one of EIA's columns in its State Electricity Profiles.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 37738.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:electricity/state-electricity-profiles/source-disposition U.S. Energy Information Administration, State Electricity Profiles, supply and disposition (API v2, route electricity/state-electricity-profiles/source-disposition) (https://www.eia.gov/electricity/state/)
- **Method note:** [`docs/methods/eia_state_source_disposition_annual.md`](../methods/eia_state_source_disposition_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). State Electricity Profiles, supply and disposition (API v2). Via the Energy Research Warehouse (ERW), table `eia_state_source_disposition_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_state_disposition:<state> | none | text | for example eia_state_disposition:AK, eia_state_disposition:AL, eia_state_disposition:AR; 52 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 35 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -89521954.0 to 4341888785.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US for the nation | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 37738 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The state's name | none | text | for example Alabama, Alaska, Arizona; 52 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:electricity/state-electricity-profiles/source-disposition | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/electricity/state-electricity-profiles/source-disposition/data/?api_key=REDACTED&frequency=annual&data%5B%5D=electric-utilities&data%5B%5D=independent-power-producers&data%5B%5D=combined-heat-and-pwr-elect&data%5B%5D=elect-pwr-sector-gen-subtotal&data%5B%5D=combined-heat-and-pwr-comm&data%5B%5D=combined-heat-and-pwr-indust&data%5B%5D=indust-and-comm-gen-subtotal&data%5B%5D=total-net-generation&data%5B%5D=total-international-imports&data%5B%5D=total-supply&data%5B%5D=full-service-providers&data%5B%5D=energy-only-providers&data%5B%5D=facility-direct&data%5B%5D=total-elect-indust&data%5B%5D=direct-use&data%5B%5D=total-international-exports&data%5B%5D=estimated-losses&data%5B%5D=net-interstate-trade&data%5B%5D=unaccounted&data%5B%5D=total-disposition&data%5B%5D=net-trade-index&start=1990 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T21:48:14Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 37738 |

Variables (21):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `combined_heat_and_pwr_comm` | Supply: net generation by commercial combined heat and power plants, MWh | MWh | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `combined_heat_and_pwr_elect` | Supply: net generation by electric power sector combined heat and power plants, MWh | MWh | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `combined_heat_and_pwr_indust` | Supply: net generation by industrial combined heat and power plants, MWh | MWh | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `direct_use` | Disposition: direct use (electricity used where it is generated), MWh | MWh | 1817 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `elect_pwr_sector_gen_subtotal` | Supply: electric power sector generation, EIA's subtotal, MWh | MWh | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `electric_utilities` | Supply: net generation by electric utilities, MWh | MWh | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `energy_only_providers` | Disposition: retail sales by energy-only providers, MWh | MWh | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `estimated_losses` | Disposition: estimated losses, MWh | MWh | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `facility_direct` | Disposition: facility direct retail purchases, MWh | MWh | 1507 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `full_service_providers` | Disposition: retail sales by full-service providers, MWh | MWh | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `independent_power_producers` | Supply: net generation by independent power producers, MWh | MWh | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `indust_and_comm_gen_subtotal` | Supply: industrial and commercial generation, EIA's subtotal, MWh | MWh | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_interstate_trade` | Disposition: net interstate trade, MWh | MWh | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_trade_index` | EIA's net trade index, a ratio | ratio | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_disposition` | Total disposition, EIA's total, MWh | MWh | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_elect_indust` | Disposition: total electric industry retail sales, EIA's subtotal, MWh | MWh | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_international_exports` | Disposition: total international exports, MWh | MWh | 1736 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_international_imports` | Supply: total international imports, MWh | MWh | 1738 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_net_generation` | Supply: total net generation, EIA's total, MWh | MWh | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_supply` | Total supply, EIA's total, MWh | MWh | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `unaccounted` | Disposition: unaccounted for, MWh | MWh | 1820 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_state_to_state_capacity`

One natural gas pipeline's capacity at one state (or national) border crossing for one year, from EIA's U.S. State-to-State Capacity workbook (2026-01 issue).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 19311.

- **Time:** ts_utc is the first day of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot); vintage is the workbook's last-modified time. A row EIA lists twice is kept twice.
- **Source:** eia:state_to_state_capacity EIA, Natural Gas Data, Pipelines (https://www.eia.gov/naturalgas/data.php)
- **Method note:** [`docs/methods/eia_state_to_state_capacity.md`](../methods/eia_state_to_state_capacity.md)
- **Cite as:** EIA. U.S. State-to-State Capacity (natural gas pipelines). Via the Energy Research Warehouse (ERW), table `eia_state_to_state_capacity`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_s2s:<pipeline>:<state from>:<county from>:<state to>:<county to>:<n>, n the crossing's place among the year's rows with the same five | none | text | for example eia_s2s:algonquin_gas_trans_co:connecticut:fairfield:new_york:putnam:1, eia_s2s:algonquin_gas_trans_co:connecticut:windham:rhode_island:providence:1, eia_s2s:algonquin_gas_trans_co:massachusetts:worcester:rhode_island:providence:1; 686 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 33 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 5.118; 870 distinct | 0 |
| `unit` | The unit of the row's value | none | text | bcf/d | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state to>; empty for Canada and Mexico | none | text | for example US-AL, US-AR, US-AZ; 49 distinct | 1346 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 19311 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The pipeline | none | text | for example ANR Pipeline Co, Algonquin Gas Trans Co, Alliance Pipeline Co; 173 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:state_to_state_capacity | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/naturalgas/pipelines/EIA-StatetoStateCapacity_Jan2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T21:21:11Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time from EIA's server | none | utc time | 2026-02-03T21:15:45Z | 0 |
| `x_region_from` | The region the gas leaves, as EIA prints it (Midwest, Gulf of America, Canada and the others) | none | text | Canada, Gulf of America, Mexico, Midwest, Mountain, Northeast, Pacific, South Central, Southeast | 0 |
| `x_region_to` | The region the gas enters, as EIA prints it (Intra-regional where both sides are one region) | none | text | Canada, Intra-regional, Mexico, Midwest, Mountain, Northeast, Pacific, South Central, Southeast | 0 |
| `x_state_from` | The state (or province, country, offshore area) the gas leaves, as EIA prints it | none | text | for example Alabama, Alberta, Arizona; 56 distinct | 0 |
| `x_county_from` | The county the gas leaves, as EIA prints it | none | text | for example Alberta, Alcorn, Alimos Canyon; 348 distinct | 33: EIA prints no county (North Baja Pipeline from California) |
| `x_state_to` | The state (or province, country) the gas enters, as EIA prints it | none | text | for example Alabama, Arizona, Arkansas; 57 distinct | 0 |
| `x_county_to` | The county the gas enters, as EIA prints it | none | text | for example Adams, Aiken, Alcorn; 352 distinct | 0 |
| `x_capacity_mmcfd` | The crossing's capacity as EIA publishes it | MMcf/d | number | 0.0 to 5118.0; 870 distinct | 0 |
| `x_notes` | EIA's note on the row | none | text | for example !First year separating McKean/Cattaraugus from Potter/Allegany, (Closed 1999), 10 MMcf/d from Leidy North Project (Docket CP20-480); 370 distinct | 18432: EIA gives no note |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity` | The pipeline's capacity at the crossing, billion cubic feet a day (EIA's MMcf a day over 1,000) | bcf/d | 19311 | 1990-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `eia_steo_forecasts`

One series' value for one month (or year) as one release of EIA's Short-Term Energy Outlook gives it, forecast or history; each release kept.

Shape: series. Keys: `entity`, `variable`, `ts_utc`, `vintage`. License: public; tier: source. Rows read on 2026-11-20: 10195.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M), or 1 January of the year for the annual series (freq P1Y).
- **Revisions:** Every release kept, the key (entity, variable, ts_utc, vintage) with vintage the release's date; a rerun of the same release replaces its own rows, a new release adds rows beside the old.
- **Source:** eia:steo U.S. Energy Information Administration, Short-Term Energy Outlook (API v2, route steo) (https://www.eia.gov/outlooks/steo/)
- **Method note:** [`docs/methods/eia_steo_forecasts.md`](../methods/eia_steo_forecasts.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Short-Term Energy Outlook (API v2). Via the Energy Research Warehouse (ERW), table `eia_steo_forecasts`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_steo:<seriesId> | none | text | for example eia_steo:CLEPSHR_US, eia_steo:ESCMU_ENC, eia_steo:ESCMU_ESC; 54 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2009-01-01T00:00:00Z to 2027-12-01T00:00:00Z; 107 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.007665807 to 136.08435833; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MMBtu, USD/kWh, index, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1M, P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, the census division series included | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 10195 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's series description | none | text | for example Coal share of U.S. electricity generation, Conventional hydropower share of U.S. electricity generation, GDP Implicit Price Deflator; 54 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:steo | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/steo/data/?api_key=REDACTED&frequency=annual&data%5B%5D=value&facets%5BseriesId%5D%5B%5D=GDPDIUS&start=2009&length=5000, https://api.eia.gov/v2/steo/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=value&facets%5BseriesId%5D%5B%5D=CLEPSHR_US&facets%5BseriesId%5D%5B%5D=ESCMU_ENC&facets%5BseriesId%5D%5B%5D=ESCMU_ESC&facets%5BseriesId%5D%5B%5D=ESCMU_HAK&facets%5BseriesId%5D%5B%5D=ESCMU_MAC&facets%5BseriesId%5D%5B%5D=ESCMU_MTN&facets%5BseriesId%5D%5B%5D=ESCMU_NEC&facets%5BseriesId%5D%5B%5D=ESCMU_PAC&facets%5BseriesId%5D%5B%5D=ESCMU_SAC&facets%5BseriesId%5D%5B%5D=ESCMU_US&facets%5BseriesId%5D%5B%5D=ESCMU_WNC&facets%5BseriesId%5D%5B%5D=ESCMU_WSC&facets%5BseriesId%5D%5B%5D=ESICU_ENC&facets%5BseriesId%5D%5B%5D=ESICU_ESC&facets%5BseriesId%5D%5B%5D=ESICU_HAK&facets%5BseriesId%5D%5B%5D=ESICU_MAC&facets%5BseriesId%5D%5B%5D=ESICU_MTN&facets%5BseriesId%5D%5B%5D=ESICU_NEC&facets%5BseriesId%5D%5B%5D=ESICU_PAC&facets%5BseriesId%5D%5B%5D=ESICU_SAC&facets%5BseriesId%5D%5B%5D=ESICU_US&facets%5BseriesId%5D%5B%5D=ESICU_WNC&facets%5BseriesId%5D%5B%5D=ESICU_WSC&facets%5BseriesId%5D%5B%5D=ESRCU_ENC&facets%5BseriesId%5D%5B%5D=ESRCU_ESC&facets%5BseriesId%5D%5B%5D=ESRCU_HAK&facets%5BseriesId%5D%5B%5D=ESRCU_MAC&facets%5BseriesId%5D%5B%5D=ESRCU_MTN&facets%5BseriesId%5D%5B%5D=ESRCU_NEC&facets%5BseriesId%5D%5B%5D=ESRCU_PAC&facets%5BseriesId%5D%5B%5D=ESRCU_SAC&facets%5BseriesId%5D%5B%5D=ESRCU_US&facets%5BseriesId%5D%5B%5D=ESRCU_WNC&facets%5BseriesId%5D%5B%5D=ESRCU_WSC&facets%5BseriesId%5D%5B%5D=ESTCU_ENC&facets%5BseriesId%5D%5B%5D=ESTCU_ESC&facets%5BseriesId%5D%5B%5D=ESTCU_HAK&facets%5BseriesId%5D%5B%5D=ESTCU_MAC&facets%5BseriesId%5D%5B%5D=ESTCU_MTN&facets%5BseriesId%5D%5B%5D=ESTCU_NEC&facets%5BseriesId%5D%5B%5D=ESTCU_PAC&facets%5BseriesId%5D%5B%5D=ESTCU_SAC&facets%5BseriesId%5D%5B%5D=ESTCU_US&facets%5BseriesId%5D%5B%5D=ESTCU_WNC&facets%5BseriesId%5D%5B%5D=ESTCU_WSC&facets%5BseriesId%5D%5B%5D=HVEPSHR_US&facets%5BseriesId%5D%5B%5D=NGEPSHR_US&facets%5BseriesId%5D%5B%5D=NGHHUUS&facets%5BseriesId%5D%5B%5D=NUEPSHR_US&facets%5BseriesId%5D%5B%5D=RTEPSHR_US&facets%5BseriesId%5D%5B%5D=SOEPSHR_US&facets%5BseriesId%5D%5B%5D=WNEPSHR_US&facets%5BseriesId%5D%5B%5D=XXEPSHR_US&start=2020-01&length=5000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T18:32:44Z, 2026-11-14T10:59:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The release's date at 00:00:00Z, part of the key | none | utc time | 2026-10-06T00:00:00Z, 2026-11-10T00:00:00Z | 0 |
| `x_kind` | forecast for a period from the release's own month (or year) on, history for EIA's figure for an earlier period | none | text | forecast, history | 0 |
| `x_units_published` | EIA's unit as published, before the ERW's conversion (cents per kWh, percentage and the others) (the source's name: unit) | none | text | Index, 2017 = 100, cents per kilowatt hour, cents per kilowatthour, dollars per million Btu, percentage | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `value` | The Outlook series the entity names: retail electricity price (USD per kWh, nominal), Henry Hub spot price (USD per MMBtu), a generation share (ratio) or the GDP implicit price deflator (index, 2017 = 100); the unit column says which | USD/MMBtu; USD/kWh; index; ratio | 10195 | 2009-01-01T00:00:00Z | 2027-12-01T00:00:00Z |

### `eia_uranium_facilities`

One U.S. uranium mill or heap leach facility (Table 3) or in-situ recovery plant (Table 4) of EIA's Domestic Uranium Production Report, with its owner, place, capacity and operating status by period.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 24.

- **Time:** No time column. Each x_status_ column holds EIA's status for one period; vintage is the workbook's last-modified time.
- **Revisions:** Rewritten whole by each run (write_snapshot).
- **Source:** eia:uranium_production_quarterly U.S. Energy Information Administration, Domestic Uranium Production Report (Quarterly), Forms EIA-851Q and EIA-851A,  (Release Date: August 2026) (https://www.eia.gov/uranium/production/quarterly/)
- **Method note:** [`docs/methods/eia_uranium_production.md`](../methods/eia_uranium_production.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Domestic Uranium Production Report (Quarterly). Via the Energy Research Warehouse (ERW), table `eia_uranium_facilities`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: eia_uranium_facility:<name> | none | text | eia_uranium_facility:alta_mesa_project, eia_uranium_facility:burke_hollow, eia_uranium_facility:crow_butte_operation, eia_uranium_facility:dewey_burdock_project, eia_uranium_facility:goliad_isr_uranium_project, eia_uranium_facility:hobson_isr_plant, eia_uranium_facility:jab_and_antelope, eia_uranium_facility:kingsville_dome_project, eia_uranium_facility:la_palangana, eia_uranium_facility:lost_creek_project, eia_uranium_facility:moore_ranch, eia_uranium_facility:nichols_ranch_isr_project, eia_uranium_facility:pathfinder_shirley_basin, eia_uranium_facility:reno_creek, eia_uranium_facility:rosita_project, eia_uranium_facility:ross_cpp, eia_uranium_facility:sheep_mountain, eia_uranium_facility:shootaring_canyon_uranium_mill, eia_uranium_facility:smith_ranch_highland_operation, eia_uranium_facility:sweetwater_uranium_inc, eia_uranium_facility:sweetwater_uranium_inc_isr, eia_uranium_facility:vasquez_project, eia_uranium_facility:white_mesa_mill, eia_uranium_facility:willow_creek_project_ludeman_christensen_ranch_and_irigaray | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: plant on every row | none | text | plant | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The facility's name as EIA writes it | none | text | Alta Mesa Project, Burke Hollow, Crow Butte Operation, Dewey Burdock Project, Goliad Isr Uranium Project, Hobson Isr Plant, Jab And Antelope, Kingsville Dome Project, La Palangana, Lost Creek Project, Moore Ranch, Nichols Ranch Isr Project, Pathfinder Shirley Basin, Reno Creek, Rosita Project, Ross Cpp, Sheep Mountain, Shootaring Canyon Uranium Mill, Smith Ranch-Highland Operation, Sweetwater Uranium Inc., Sweetwater Uranium Inc. Isr, Vasquez Project, White Mesa Mill, Willow Creek Project (Ludeman, Christensen Ranch And Irigaray) | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> of the facility | none | text | US-NE, US-SD, US-TX, US-UT, US-WY | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 24 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 24 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: Not filled: the capacity is in ore or pounds, in x_capacity | MW | empty | no cell holds a value | 24 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: EIA's status of each period is in the x_status_ columns | none | empty | no cell holds a value | 24 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 24 |
| `operator` | The operator or owner, as the publisher writes it. Here: The owner, as EIA writes it | none | text | Anfield Energy Inc., Cameco, Encore Alta Mesa, Llc, Encore Energy Corporation, Energy Fuels Resources (Usa) Inc., Lost Creek Isr Llc, Pathfinder Mines Company, Power Resources, Inc. Dba Cameco Resources, Strata Energy, Inc., Uranerz Energy Corporation Db For Energy Fuels, Uranium Energy Corp., Uranium Energy Corporation | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:uranium_production_quarterly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/uranium/production/quarterly/xls/qupd_tbl3.xlsx, https://www.eia.gov/uranium/production/quarterly/xls/qupd_tbl4.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T12:52:16Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time from EIA's server | none | utc time | 2026-08-19T13:52:39Z, 2026-08-19T13:54:03Z | 0 |
| `x_kind` | mill (a mill or heap leach facility) or isr (an in-situ recovery plant) | none | text | isr, mill | 0 |
| `x_location` | The facility's county and state as EIA writes them | none | text | Bee, Texas, Brooks, Texas, Campbell and Johnson, Wyoming, Campbell, Wyoming, Carbon, Wyoming, Converse, Wyoming, Crook, Wyoming, Dawes, Nebraska, Duval, Texas, Fall River and Custer, South Dakota, Fremont, Wyoming, Garfield, Utah, Goliad, Texas, Johnson and Campbell, Wyoming, Karnes, Texas, Kleberg, Texas, San Juan, Utah, Sweetwater, Wyoming | 0 |
| `x_capacity` | The facility's capacity as EIA gives it, in x_capacity_unit | short tons of ore per day or pounds U3O8 per year | integer | 0, 1000000, 1300000, 1400000, 1500000, 2000, 2000000, 3000, 3000000, 4000000, 4100000, 5500000, 725, 750, 800000 | 0 |
| `x_capacity_unit` | The unit of x_capacity: short tons of ore a day for a mill, pounds of U3O8 a year for a plant | none | text | pounds U3O8 per year, short tons of ore per day | 0 |
| `x_status_2025` | EIA's operating status of the facility in 2025 (operating, standby, developing and the others) | none | text | developing, operating, partially permitted and licensed, permitted and licensed, reclamation, restoration, standby, undeveloped | 0 |
| `x_status_first_quarter_2026` | EIA's operating status of the facility in the first quarter of 2026 | none | text | developing, inactive, operating, partially permitted and licensed, permitted and licensed, reclamation, restoration, standby, under construction, undeveloped | 0 |
| `x_status_second_quarter_2026` | EIA's operating status of the facility in the second quarter of 2026 | none | text | developing, inactive, operating, partially permitted and licensed, permitted and licensed, reclamation, restoration, standby, undeveloped | 0 |
| `x_status_third_quarter_2026` | EIA's operating status of the facility in the third quarter of 2026 | none | empty | no cell holds a value | 24: EIA writes - or nothing (the quarter not yet reported in this release: no cell holds a value) |
| `x_status_fourth_quarter_2026` | EIA's operating status of the facility in the fourth quarter of 2026 | none | empty | no cell holds a value | 24: EIA writes - or nothing (the quarter not yet reported in this release: no cell holds a value) |

### `eia_uranium_marketing_annual`

One year's figure of EIA's Uranium Marketing Annual Report summary tables for the U.S. (uranium bought by reactor owners and operators and its price, feed, enrichment, loadings, foreign trade or inventories).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 763.

- **Time:** ts_utc is 1 January of the delivery year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:uranium_marketing_annual U.S. Energy Information Administration, Uranium Marketing Annual Report (Form EIA-858), tables S1a to S3b (https://www.eia.gov/uranium/marketing/)
- **Method note:** [`docs/methods/eia_uranium_marketing_annual.md`](../methods/eia_uranium_marketing_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Uranium Marketing Annual Report (Form EIA-858), summary tables. Via the Energy Research Warehouse (ERW), table `eia_uranium_marketing_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_uranium:us | none | text | eia_uranium:us | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2003-01-01T00:00:00Z, 2004-01-01T00:00:00Z, 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 170000000.0; 707 distinct | 0 |
| `unit` | The unit of the row's value | none | text | SWU, USD/SWU, USD/lb, lb | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 763 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's heading | none | text | for example Average price (US$ per SWU), Feed deliveries by owners and operators of U.S. civilian nuclear power reactors, Foreign purchases by U.S. suppliers; 31 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:uranium_marketing_annual | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/uranium/marketing/xls/umartableS1afigureS1.xlsx, https://www.eia.gov/uranium/marketing/xls/umartableS1bfigureS2.xlsx, https://www.eia.gov/uranium/marketing/xls/umartableS2figuresS3n4.xlsx, https://www.eia.gov/uranium/marketing/xls/umartableS3afigureS5.xlsx, https://www.eia.gov/uranium/marketing/xls/umartableS3bfigureS6.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T06:59:52Z, 2026-10-23T06:59:53Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 763 |

Variables (37):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `broker_purchases_from_foreign` | U.S. broker and trader purchases from foreign suppliers, pounds U3O8 equivalent (S3a) | lb | 21 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `enrichment_foreign_origin` | Enrichment services purchased, of foreign origin, separative work units (S2) | SWU | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `enrichment_price` | Average price of enrichment services, USD per separative work unit (S2) | USD/SWU | 20 | 2006-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `enrichment_total` | Enrichment services purchased, in all, separative work units (S2) | SWU | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `enrichment_us_origin` | Enrichment services purchased, of U.S. origin, separative work units (S2; EIA's million SWU times 1,000,000) | SWU | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `feed_deliveries` | Feed deliveries by the owners and operators (uranium delivered for enrichment), pounds U3O8 equivalent (S2) | lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `foreign_purchases_owners` | Foreign purchases by owners and operators, pounds U3O8 equivalent (S3a) | lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `foreign_purchases_total` | Foreign purchases in all, pounds U3O8 equivalent (S3a) | lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `foreign_purchases_us_suppliers` | Foreign purchases by U.S. suppliers, pounds U3O8 equivalent (S3a) | lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `foreign_sales` | Foreign sales, pounds U3O8 equivalent (S3a) | lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `inventories_owners` | Uranium inventories owned by owners and operators, pounds U3O8 equivalent (S3a) | lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `inventories_total` | Total commercial uranium inventories, pounds U3O8 equivalent (S3a) | lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `inventories_us_suppliers` | Uranium inventories owned by U.S. suppliers, pounds U3O8 equivalent (S3a) | lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `price_broker_purchases_from_foreign` | Weighted-average price of U.S. broker and trader purchases from foreign suppliers, USD per pound (S3b) | USD/lb | 21 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `price_foreign_purchases_owners` | Weighted-average price of foreign purchases by owners and operators, USD per pound (S3b) | USD/lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `price_foreign_purchases_total` | Weighted-average price of foreign purchases in all, USD per pound (S3b) | USD/lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `price_foreign_purchases_us_suppliers` | Weighted-average price of foreign purchases by U.S. suppliers, USD per pound (S3b) | USD/lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `price_foreign_sales` | Weighted-average price of foreign sales, USD per pound (S3b) | USD/lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `price_purchased_foreign_origin` | Weighted-average price of uranium of foreign origin, USD per pound (S1b) | USD/lb | 20 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `price_purchased_from_foreign_suppliers` | Weighted-average price of uranium bought from foreign suppliers, USD per pound (S1b) | USD/lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `price_purchased_from_other_owners_suppliers` | Weighted-average price of uranium bought from other owners and operators and suppliers, USD per pound (S1b) | USD/lb | 7 | 2003-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `price_purchased_from_us_brokers_traders` | Weighted-average price of uranium bought from U.S. brokers and traders, USD per pound (S1b) | USD/lb | 18 | 2003-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `price_purchased_from_us_producers` | Weighted-average price of uranium bought from U.S. producers, USD per pound (S1b) | USD/lb | 8 | 2003-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `price_purchased_long_term` | Weighted-average price of uranium bought under long-term contracts, USD per pound (S1b) | USD/lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `price_purchased_spot` | Weighted-average price of uranium bought under spot contracts, USD per pound (S1b) | USD/lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `price_purchased_total` | Weighted-average price of uranium bought, in all, USD per pound U3O8 equivalent (S1b) | USD/lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `price_purchased_us_origin` | Weighted-average price of uranium of U.S. origin, USD per pound (S1b) | USD/lb | 20 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `purchased_foreign_origin` | Uranium bought by the owners and operators, of foreign origin, pounds U3O8 equivalent (S1a) | lb | 20 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `purchased_from_foreign_suppliers` | Uranium the owners and operators bought from foreign suppliers, pounds U3O8 equivalent (S1a) | lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `purchased_from_other_owners_suppliers` | Uranium the owners and operators bought from other owners and operators and suppliers, pounds U3O8 equivalent (S1a) | lb | 9 | 2003-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `purchased_from_us_brokers_traders` | Uranium the owners and operators bought from U.S. brokers and traders, pounds U3O8 equivalent (S1a) | lb | 19 | 2003-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `purchased_from_us_producers` | Uranium the owners and operators bought from U.S. producers, pounds U3O8 equivalent (S1a) | lb | 8 | 2003-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `purchased_long_term` | Uranium bought by the owners and operators under long-term contracts, pounds U3O8 equivalent (S1a) | lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `purchased_spot` | Uranium bought by the owners and operators under spot contracts, pounds U3O8 equivalent (S1a) | lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `purchased_total` | Uranium bought by owners and operators of U.S. civilian nuclear power reactors, in all, pounds U3O8 equivalent (S1a) | lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `purchased_us_origin` | Uranium bought by the owners and operators, of U.S. origin, pounds U3O8 equivalent (S1a) | lb | 20 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `uranium_loaded` | Uranium in fuel assemblies loaded into U.S. civilian nuclear power reactors, pounds U3O8 equivalent (S2) | lb | 23 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `eia_uranium_production_quarterly`

One U.S. facility's (or EIA's total) uranium concentrate production in one quarter, or the number of facilities of one kind producing at the end of a year or the latest quarter.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 171.

- **Time:** ts_utc is the quarter's first day (freq P3M) or the year's 1 January (freq P1Y, a count at the year's end), at 00:00:00Z.
- **Revisions:** Rewritten whole by each run (write_snapshot); vintage is the workbook's last-modified time.
- **Source:** eia:uranium_production_quarterly U.S. Energy Information Administration, Domestic Uranium Production Report (Quarterly), Forms EIA-851Q and EIA-851A,  (Release Date: August 2026) (https://www.eia.gov/uranium/production/quarterly/)
- **Method note:** [`docs/methods/eia_uranium_production.md`](../methods/eia_uranium_production.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Domestic Uranium Production Report (Quarterly). Via the Energy Research Warehouse (ERW), table `eia_uranium_production_quarterly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_u3o8:<facility> (eia_u3o8:total EIA's total) for production; eia_uranium_facilities:<kind> for counts | none | text | eia_u3o8:alta_mesa_project, eia_u3o8:crowe_butte_operation, eia_u3o8:lost_creek_project, eia_u3o8:nichols_ranch_isr_project, eia_u3o8:ross_cpp, eia_u3o8:smith_ranch_highland_operation, eia_u3o8:total, eia_u3o8:white_mesa_mill, eia_u3o8:willow_creek_project_ludeman_christensen_ranch_and_irigaray, eia_uranium_facilities:byproduct_plants, eia_uranium_facilities:isr_plants, eia_uranium_facilities:mills_conventional, eia_uranium_facilities:mills_other, eia_uranium_facilities:total | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2000-01-01T00:00:00Z to 2026-04-01T00:00:00Z; 31 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 1087504.0; 43 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count, lb | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y, P3M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> for a facility in one state, US for the totals | none | text | US, US-NE, US-TX, US-UT, US-WY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 171 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The facility, or the kind of facility and the period, as EIA writes it | none | text | for example Alta Mesa Project, Byproduct recovery plants, end of 2000, Byproduct recovery plants, end of 2001; 144 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:uranium_production_quarterly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/uranium/production/quarterly/xls/qupd_tbl1.xlsx, https://www.eia.gov/uranium/production/quarterly/xls/qupd_tbl2.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T12:52:16Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time from EIA's server | none | utc time | 2026-08-13T18:57:16Z, 2026-08-13T19:09:04Z | 0 |
| `x_facility` | The facility's name as EIA writes it (Table 1) | none | text | Alta Mesa Project, Crowe Butte Operation, Lost Creek Project, Nichols Ranch ISR Project, Ross CPP, Smith Ranch-Highland Operation, Total production, White Mesa Mill, Willow Creek Project (Ludeman, Christensen Ranch And Irigaray) | 135: A facility-count row (Table 2) |
| `x_location` | The facility's county and state as EIA writes them | none | text | Brooks, Texas, Campbell and Johnson, Wyoming, Converse, Wyoming, Crook, Wyoming, Dawes, Nebraska, Johnson and Campbell, Wyoming, San Juan, Utah, Sweetwater, Wyoming | 140: A facility-count row, or EIA's total row |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `facilities_producing` | Number of facilities of the kind producing uranium concentrate at the end of the period | count | 135 | 2000-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `production` | Uranium concentrate produced in the quarter, pounds of U3O8 | lb | 36 | 2025-04-01T00:00:00Z | 2026-04-01T00:00:00Z |

### `eia_wood_pellets_monthly`

One month's figure from EIA's Monthly Densified Biomass Fuel Report (wood pellets) for a region, the U.S. or a feedstock type (a price, a feedstock cost, facilities or employees).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2090.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot). vintage is not filled.
- **Source:** eia:densified-biomass U.S. Energy Information Administration, Monthly Densified Biomass Fuel Report (API v2, routes densified-biomass/sales-and-price-by-region, export-sales-and-price, capacity-by-region) (https://www.eia.gov/biofuels/biomass/)
- **Method note:** [`docs/methods/eia_wood_pellets_monthly.md`](../methods/eia_wood_pellets_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Monthly Densified Biomass Fuel Report (API v2). Via the Energy Research Warehouse (ERW), table `eia_wood_pellets_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_wood_pellets:<sales\|export\|capacity\|feedstocks>:<region or fuel type> | none | text | eia_wood_pellets:capacity:EAST, eia_wood_pellets:capacity:SOUTH, eia_wood_pellets:capacity:US-TOTAL, eia_wood_pellets:capacity:WEST, eia_wood_pellets:export:US, eia_wood_pellets:feedstocks:OR, eia_wood_pellets:feedstocks:RP, eia_wood_pellets:feedstocks:SR, eia_wood_pellets:feedstocks:WPMR, eia_wood_pellets:sales:EAST, eia_wood_pellets:sales:SOUTH, eia_wood_pellets:sales:US-TOTAL, eia_wood_pellets:sales:WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2016-01-01T00:00:00Z to 2026-05-01T00:00:00Z; 125 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 2610.0; 1370 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/short_ton, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, the regions included | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2090 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EIA's region or fuel type name | none | text | EAST, Other Residuals, Roundwood/Pulpwood, SOUTH, Sawmill Residuals, US, US-TOTAL, WEST, Wood Product Manufacturing Residuals | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:densified-biomass | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.eia.gov/v2/densified-biomass/capacity-by-region/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=number-of-facilities&data%5B%5D=number-of-fte-employees&start=2016-01, https://api.eia.gov/v2/densified-biomass/export-sales-and-price/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=average-price&start=2016-01, https://api.eia.gov/v2/densified-biomass/feedstocks-and-cost/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=cost&start=2016-01, https://api.eia.gov/v2/densified-biomass/sales-and-price-by-region/data/?api_key=REDACTED&frequency=monthly&data%5B%5D=average-price&start=2016-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T23:57:46Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2090 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `domestic_price` | Average price of domestic sales of densified biomass in the region, USD per short ton | USD/short_ton | 500 | 2016-01-01T00:00:00Z | 2026-05-01T00:00:00Z |
| `export_price` | Average price of densified biomass exports, USD per short ton | USD/short_ton | 113 | 2016-01-01T00:00:00Z | 2026-05-01T00:00:00Z |
| `facilities` | Number of densified biomass facilities in the region | count | 500 | 2016-01-01T00:00:00Z | 2026-05-01T00:00:00Z |
| `feedstock_cost` | Cost of the feedstock type, USD per short ton | USD/short_ton | 477 | 2016-01-01T00:00:00Z | 2026-05-01T00:00:00Z |
| `fte_employees` | Full-time equivalent employees of the region's facilities | count | 500 | 2016-01-01T00:00:00Z | 2026-05-01T00:00:00Z |

### `eia_world_coal_annual`

One country's or region's yearly coal figure (production, consumption, trade or reserves) for one coal product, from EIA's International Energy Statistics bulk file.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 317307.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot); vintage is the bulk file's last-modified time.
- **Source:** eia:international_bulk U.S. Energy Information Administration, International Energy Statistics (bulk download) (https://www.eia.gov/international/data/world)
- **Method note:** [`docs/methods/eia_world_coal_energy.md`](../methods/eia_world_coal_energy.md)
- **Cite as:** U.S. Energy Information Administration (EIA). International Energy Statistics (bulk download). Via the Energy Research Warehouse (ERW), table `eia_world_coal_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_intl:<EIA country or region code>:<EIA product id>; coal (7) holds its kinds | none | text | for example eia_intl:ABW:11, eia_intl:ABW:119, eia_intl:ABW:12; 1854 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1980-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 45 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 1285176615140.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | short_ton | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no ISO code is guessed from EIA's area codes | none | empty | no cell holds a value | 317307 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 317307 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <area>, <product> in EIA's names | none | text | for example Afghanistan, Anthracite, Afghanistan, Bituminous, Afghanistan, Coal; 1798 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:international_bulk | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/opendata/bulk/INTL.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T07:54:07Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The bulk file's last-modified time from EIA's server | none | utc time | 2026-10-19T19:55:35Z | 0 |
| `x_area` | The kind of area: country, former (a country that no longer exists), part (EIA's offshore and trade-zone parts) or region (the world, continents, groups); a sum over countries takes country and former only | none | text | country, former, part, region | 0 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` | Coal consumption, short tons | short_ton | 78319 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `exports` | Coal exports, short tons | short_ton | 78319 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `imports` | Coal imports, short tons | short_ton | 78319 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `production` | Coal production, short tons (EIA's thousand short tons times 1,000) | short_ton | 78319 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `reserves` | Coal reserves, short tons (EIA's million short tons times 1,000,000; product 7 only) | short_ton | 4031 | 2008-01-01T00:00:00Z | 2023-01-01T00:00:00Z |

### `eia_world_electricity_annual`

One country's or region's yearly electricity figure (generation by product, consumption, trade, losses or capacity), from EIA's International Energy Statistics bulk file.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 332254.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot); vintage is the bulk file's last-modified time.
- **Source:** eia:international_bulk U.S. Energy Information Administration, International Energy Statistics (bulk download) (https://www.eia.gov/international/data/world)
- **Method note:** [`docs/methods/eia_world_electricity_annual.md`](../methods/eia_world_electricity_annual.md)
- **Cite as:** U.S. Energy Information Administration (EIA). International Energy Statistics (bulk download). Via the Energy Research Warehouse (ERW), table `eia_world_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_intl:<EIA country or region code>:<EIA product id>; a product's parts overlap | none | text | for example eia_intl:ABW:116, eia_intl:ABW:117, eia_intl:ABW:2; 4421 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1980-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 45 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -89850955.0 to 30664339571.261; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no ISO code is guessed from EIA's area codes | none | empty | no cell holds a value | 332254 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 332254 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <area>, <product> in EIA's names | none | text | for example Afghanistan, Biomass and waste, Afghanistan, Coal, Afghanistan, Electricity; 4285 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:international_bulk | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/opendata/bulk/INTL.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T07:54:07Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The bulk file's last-modified time from EIA's server | none | utc time | 2026-10-19T19:55:35Z | 0 |
| `x_area` | The kind of area: country, former (a country that no longer exists), part (EIA's offshore and trade-zone parts) or region (the world, continents, groups); a sum over countries takes country and former only | none | text | country, former, part, region | 0 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity` | Generating capacity, MW (EIA's million kW times 1,000) | MW | 109749 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `consumption` | Electricity consumption, MWh | MWh | 10973 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `distribution_losses` | Electricity transmission and distribution losses, MWh | MWh | 10968 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `exports` | Electricity exports, MWh | MWh | 10869 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `generation` | Net electricity generation from the product, MWh (EIA's billion kWh times 1,000,000) | MWh | 167774 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `imports` | Electricity imports, MWh | MWh | 10958 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_imports` | Electricity net imports, MWh | MWh | 10963 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_world_energy_co2_annual`

One country's or region's yearly total primary energy production or consumption (in all or by source) or energy-related CO2 emissions, from EIA's International Energy Statistics bulk file.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 246988.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot); vintage is the bulk file's last-modified time.
- **Source:** eia:international_bulk U.S. Energy Information Administration, International Energy Statistics (bulk download) (https://www.eia.gov/international/data/world)
- **Method note:** [`docs/methods/eia_world_coal_energy.md`](../methods/eia_world_coal_energy.md)
- **Cite as:** U.S. Energy Information Administration (EIA). International Energy Statistics (bulk download). Via the Energy Research Warehouse (ERW), table `eia_world_energy_co2_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_intl:<EIA country or region code>:<EIA product id>; a total holds its parts | none | text | for example eia_intl:ABW:1, eia_intl:ABW:3002, eia_intl:ABW:4002; 3701 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1949-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 77 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -68286.95066878719 to 37928008921.28; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | TBtu, tCO2 | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no ISO code is guessed from EIA's area codes | none | empty | no cell holds a value | 246988 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 246988 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <area>, <product> in EIA's names | none | text | for example Afghanistan, CO2 emissions, all fuels, Afghanistan, CO2 emissions, coal and coke, Afghanistan, CO2 emissions, coal and coke (by product); 3589 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:international_bulk | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/opendata/bulk/INTL.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T07:54:07Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The bulk file's last-modified time from EIA's server | none | utc time | 2026-10-19T19:55:35Z | 0 |
| `x_area` | The kind of area: country, former (a country that no longer exists), part (EIA's offshore and trade-zone parts) or region (the world, continents, groups); a sum over countries takes country and former only | none | text | country, former, part, region | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` | Primary energy consumption of the product, trillion Btu (EIA's quadrillion Btu times 1,000) | TBtu | 89405 | 1980-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `emissions` | Energy-related carbon dioxide emissions of the fuel, tonnes of CO2 (EIA's million metric tonnes times 1,000,000) | tCO2 | 79179 | 1949-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `production` | Primary energy production of the product, trillion Btu (EIA's quadrillion Btu times 1,000) | TBtu | 78404 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eia_world_oil_gas_annual`

One country's or region's yearly petroleum or natural gas figure (production, consumption, trade, bunkers or stocks) for one product, from EIA's International Energy Statistics bulk file.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 448267.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** Rewritten whole by each run (write_snapshot); vintage is the bulk file's last-modified time.
- **Source:** eia:international_bulk U.S. Energy Information Administration, International Energy Statistics (bulk download) (https://www.eia.gov/international/data/world)
- **Method note:** [`docs/methods/eia_world_oil_gas.md`](../methods/eia_world_oil_gas.md)
- **Cite as:** U.S. Energy Information Administration (EIA). International Energy Statistics (bulk download). Via the Energy Research Warehouse (ERW), table `eia_world_oil_gas_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_intl:<EIA country or region code>:<EIA product id>; a product's parts overlap | none | text | for example eia_intl:ABW:13, eia_intl:ABW:26, eia_intl:ABW:3; more than 5000 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1973-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 53 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -145.83096779310273 to 4597943.7403; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | bcf, kbbl, kbbl/d | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no ISO code is guessed from EIA's area codes | none | empty | no cell holds a value | 448267 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 448267 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <area>, <product> in EIA's names | none | text | for example Afghanistan, Biodiesel, Afghanistan, Biofuels, Afghanistan, Crude oil including lease condensate; more than 5000 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:international_bulk | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/opendata/bulk/INTL.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T07:54:07Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The bulk file's last-modified time from EIA's server | none | utc time | 2026-10-19T19:55:35Z | 0 |
| `x_area` | The kind of area: country, former (a country that no longer exists), part (EIA's offshore and trade-zone parts) or region (the world, continents, groups); a sum over countries takes country and former only | none | text | country, former, part, region | 0 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `bunker_consumption` | Bunker consumption of the product, as EIA gives it, thousand barrels a day | kbbl/d | 19237 | 1980-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `consumption` | Consumption of the product: thousand barrels a day for liquids, billion cubic feet a year for gas | bcf; kbbl/d | 156524 | 1973-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `exports` | Exports of the product: thousand barrels a day for liquids, billion cubic feet a year for gas | bcf; kbbl/d | 37887 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `imports` | Imports of the product: thousand barrels a day for liquids, billion cubic feet a year for gas | bcf; kbbl/d | 37451 | 1980-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `production` | Production of the product: thousand barrels a day for liquids, billion cubic feet a year for gas (the unit column says which) | bcf; kbbl/d | 195912 | 1973-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stocks` | Stocks of petroleum and other liquids, thousand barrels (EIA's million barrels times 1,000) | kbbl | 1256 | 1973-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `eia_world_oil_monthly`

One country's or region's monthly petroleum production, consumption or stocks for one product, from EIA's International Energy Statistics bulk file.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 541215.

- **Time:** ts_utc is the first day of the month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run (write_snapshot); vintage is the bulk file's last-modified time.
- **Source:** eia:international_bulk U.S. Energy Information Administration, International Energy Statistics (bulk download) (https://www.eia.gov/international/data/world)
- **Method note:** [`docs/methods/eia_world_oil_gas.md`](../methods/eia_world_oil_gas.md)
- **Cite as:** U.S. Energy Information Administration (EIA). International Energy Statistics (bulk download). Via the Energy Research Warehouse (ERW), table `eia_world_oil_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia_intl:<EIA country or region code>:<EIA product id>; a product's parts overlap | none | text | for example eia_intl:ABW:53, eia_intl:ABW:55, eia_intl:ABW:56; 1555 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1973-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 643 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -31.1 to 4766526.995; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kbbl, kbbl/d | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no ISO code is guessed from EIA's area codes | none | empty | no cell holds a value | 541215 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 541215 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <area>, <product> in EIA's names | none | text | for example Afghanistan, Crude oil including lease condensate, Afghanistan, Crude oil, NGPL, and other liquids, Afghanistan, NGPL; 1507 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:international_bulk | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/opendata/bulk/INTL.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T07:54:07Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The bulk file's last-modified time from EIA's server | none | utc time | 2026-10-19T19:55:35Z | 0 |
| `x_area` | The kind of area: country, former (a country that no longer exists), part (EIA's offshore and trade-zone parts) or region (the world, continents, groups); a sum over countries takes country and former only | none | text | country, former, part, region | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` | Consumption of the product, thousand barrels a day | kbbl/d | 6706 | 1980-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `production` | Production of the product, thousand barrels a day | kbbl/d | 527849 | 1973-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `stocks` | Stocks of petroleum and other liquids, thousand barrels (EIA's million barrels times 1,000) | kbbl | 6660 | 1980-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

