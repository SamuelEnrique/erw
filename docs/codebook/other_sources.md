# Codebook: other_sources

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 104 public tables (9 entities, 7 events, 88 series; tiers: 4 derived, 100 source); 104 documented in full.

- [`abs_suriname_electricity_annual`](#abs_suriname_electricity_annual): One year's value of one Suriname electricity measure (EBS's demand by category, net generation, net consumption or capacity, or a Staatsolie plant's generation), from the statistics office's Environment Statistics Publication.
- [`aedg_alaska_generation_monthly`](#aedg_alaska_generation_monthly): One Alaska service area's electricity generation from one fuel in one month, from the Alaska Energy Data Gateway.
- [`aeso_alberta_load_hourly`](#aeso_alberta_load_hourly): Alberta's internal load in one hour, from the Alberta Electric System Operator's Historical Pool Price report.
- [`ai_energy_published`](#ai_energy_published): One energy figure for AI (per query, per token, of a training run or of a fleet) as a model maker, a cloud operator or a peer-reviewed paper printed it.
- [`aneel_siga_plants`](#aneel_siga_plants): One Brazilian central generation plant in ANEEL's SIGA register (operating, under construction or not yet begun).
- [`asli_liechtenstein_electricity_annual`](#asli_liechtenstein_electricity_annual): One year's value of Liechtenstein's electricity production, imports, exports or consumption, from the statistics office's Energie table 5.
- [`asub_aland_electricity_annual`](#asub_aland_electricity_annual): One year's electricity supply to Aland from one origin (imports from Sweden or Finland; oil, wind, bioenergy or solar production), or the total, from ASUB's table MI009.
- [`asub_aland_electricity_sales_annual`](#asub_aland_electricity_sales_annual): One year's electricity sales of one Aland distributor region to one sector (or its total), or Aland's exports, from ASUB's table MI010.
- [`bcrp_peru_electricity_monthly`](#bcrp_peru_electricity_monthly): One Peruvian department's (or Peru's total) electricity production in one month, from the central bank's BCRPData (data from MINEM).
- [`bcrp_peru_hydrocarbons_monthly`](#bcrp_peru_hydrocarbons_monthly): Peru's production of crude oil, natural gas liquids or natural gas in one month, from the central bank's BCRPData (data from INEI and MINEM).
- [`bfe_ch_electricity_wednesdays`](#bfe_ch_electricity_wednesdays): One Wednesday's value of one Swiss electricity balance item (generation by type, storage pumps, imports, exports, national consumption), from the Swiss Federal Office of Energy's weekly balance.
- [`bfe_switzerland_electricity_monthly`](#bfe_switzerland_electricity_monthly): One month's value of one item of Switzerland's electricity balance, from the Swiss Federal Office of Energy's monthly values.
- [`blm_ca_renewable_rows`](#blm_ca_renewable_rows): One renewable energy right-of-way on public lands in California (verified or preliminary), from the Bureau of Land Management's California renewable energy projects layers.
- [`blm_oil_gas_statistics_annual`](#blm_oil_gas_statistics_annual): One state's value of one federal onshore oil and gas measure (leases, acreage, drilling permits, wells) for one federal fiscal year, from BLM's Oil and Gas Statistics.
- [`bpa_ba_hourly`](#bpa_ba_hourly): One hour's value of the BPA balancing authority's load, generation by type or net interchange, the hour's mean of BPA's five-minute values.
- [`bsee_offshore_incidents`](#bsee_offshore_incidents): One incident on the US outer continental shelf reported to the Bureau of Safety and Environmental Enforcement, from its calendar-year workbooks.
- [`caiso_tie_flows_5min`](#caiso_tie_flows_5min): The net Western Energy Imbalance Market transfer between one pair of balancing areas in one five-minute interval of CAISO's real-time dispatch.
- [`carb_auction_allowance_prices`](#carb_auction_allowance_prices): One cap-and-trade auction's (California, joint with Quebec) value of one result for its current-vintage or advance-vintage allowances.
- [`carb_lcfs_credit_prices`](#carb_lcfs_credit_prices): One week's value of one Low Carbon Fuel Standard credit measure, as the California Air Resources Board publishes it.
- [`cbs_curacao_electricity_annual`](#cbs_curacao_electricity_annual): Curacao's electricity production by Aqualectra in one year, from the Central Bureau of Statistics Curacao.
- [`cbs_netherlands_electricity_monthly`](#cbs_netherlands_electricity_monthly): One month's value of one measure of the Netherlands' electricity balance (production by source, own use, imports and exports by country, losses, net consumption), from Statistics Netherlands table 84575NED.
- [`cec_total_system_generation_annual`](#cec_total_system_generation_annual): One year's California in-state generation, or imports from the Northwest or Southwest, from one fuel, or the total system power by fuel, from the California Energy Commission.
- [`censtatd_hk_electricity`](#censtatd_hk_electricity): One month's value of Hong Kong's electricity consumption by type of user (or exports to the Mainland), or one quarter's value of its generation, imports, exports, own use and losses, from the Census and Statistics Department.
- [`cftc_cot_positions`](#cftc_cot_positions): One NYMEX futures contract's value of one Commitments of Traders measure for one report week.
- [`constraints_binding_hourly`](#constraints_binding_hourly): One transmission constraint that bound in one hour of an operator's day-ahead market (SPP or CAISO), with the shadow price the operator published.
- [`constraints_binding_monthly`](#constraints_binding_monthly): One constraint (with its contingency) in one month, from constraints_binding_hourly; derived.
- [`cso_ireland_electricity_monthly`](#cso_ireland_electricity_monthly): Ireland's gross or net electricity output in one month, from the Central Statistics Office's table MSM01.
- [`czso_cz_regional_electricity_annual`](#czso_cz_regional_electricity_annual): One Czech region's (or Czechia's) installed capacity or gross production by type of plant, or net consumption by activity, in 2024, from the Czech Statistical Office's Comparison of Regions.
- [`destatis_de_electricity_monthly`](#destatis_de_electricity_monthly): One month's electricity or heat generation of Germany's general supply plants from one energy source (or in total), from Destatis' monthly report.
- [`dfe_ni_electricity_monthly`](#dfe_ni_electricity_monthly): One month's value of Northern Ireland's renewable or non-renewable generation (by type or fuel) or its electricity trade, from the Department for the Economy's report figures 6 to 9.
- [`dosm_malaysia_electricity_monthly`](#dosm_malaysia_electricity_monthly): One month's value of Malaysia's electricity supply or consumption by sector, from the Department of Statistics Malaysia.
- [`dst_dk_electricity_supply_annual`](#dst_dk_electricity_supply_annual): One year's value of Denmark's electricity supply, production or imports, or its wind, hydro or solar power supply, from Statistics Denmark's Energy Account table ENE1HT.
- [`edf_sei_islands_electricity_annual`](#edf_sei_islands_electricity_annual): One French island grid's net electricity production from one source, its net imports or its total supply, in one year, from EDF SEI.
- [`egrid_power_plants`](#egrid_power_plants): One US power plant of eGRID2023 (data year 2023): its capacity, generation, emissions and emission rates, as EPA publishes them.
- [`egrid_subregions_annual`](#egrid_subregions_annual): One eGRID2023 subregion's value of one measure (capacity, net generation, CO2 emissions and rates, resource mix) for data year 2023.
- [`eia411_capacity_margins_annual`](#eia411_capacity_margins_annual): One NERC assessment area's value of one supply and demand measure (peak load, net internal demand, capacity resources, capacity margin) for one summer or winter season, actual or projected.
- [`eia861m_utility_sales_monthly`](#eia861m_utility_sales_monthly): One sampled utility's retail sales, revenue or customers in one state and sector in one month, from Form EIA-861M.
- [`elexon_gb_demand_daily`](#elexon_gb_demand_daily): Great Britain's Initial National Demand Outturn summed over one settlement day, from Elexon's BMRS.
- [`emi_nz_generation_demand_monthly`](#emi_nz_generation_demand_monthly): New Zealand's, the North Island's or the South Island's grid generation or demand in one month, from the Electricity Authority's EMI reports.
- [`energinet_dk_production_hourly`](#energinet_dk_production_hourly): One Danish price area's (DK1 or DK2) value of one production, consumption or exchange measure in one hour, from Energinet's settlement data.
- [`epe_brazil_consumption_monthly`](#epe_brazil_consumption_monthly): One Brazilian state's electricity consumption or consumers in one market class (captive or free) and sector in one month, from EPE's Statistical Yearbook raw data.
- [`epra_kenya_electricity_annual`](#epra_kenya_electricity_annual): One fiscal year's value of one Kenyan generation capacity (by grid kind and technology) or electricity consumption (by customer category) measure, from EPRA's Energy and Petroleum Statistics Reports.
- [`fbos_fiji_electricity_annual`](#fbos_fiji_electricity_annual): Energy Fiji Limited's units produced or sold (in total or to one consumer class) in one year, from the Fiji Bureau of Statistics.
- [`fema_disaster_declarations`](#fema_disaster_declarations): One FEMA disaster declaration for one designated area (a county, a tribal area or a statewide area), declared on or after 2015-01-01, from OpenFEMA.
- [`fhwa_motor_fuel_monthly`](#fhwa_motor_fuel_monthly): The gallons of gasoline or of special fuels one state reports taxed in one month, from FHWA's Monthly Motor Fuel source data.
- [`frb_treasury_yields`](#frb_treasury_yields): One US Treasury maturity's market yield at constant maturity for one business day.
- [`frb_utility_output_monthly`](#frb_utility_output_monthly): One month's seasonally adjusted industrial production index or capacity utilization of one G.17 series (electric and gas utilities and their parts, with total industry and energy for comparison), from the Federal Reserve's G.17 release.
- [`generation_outages_hourly`](#generation_outages_hourly): Megawatts of generation out of service in one hour, for one SPP area by fuel or for CAISO by planned and forced, as each operator publishes it.
- [`gfz_kp_index_3h`](#gfz_kp_index_3h): The planetary geomagnetic index Kp for one three-hour interval, from GFZ's file since 1932.
- [`grid_all_alerts`](#grid_all_alerts): One grid alert, watch, emergency or disturbance report, from CAISO's emergencies, ERCOT's notices or DOE's OE-417 reports; derived.
- [`hagstofa_iceland_power_annual`](#hagstofa_iceland_power_annual): Iceland's installed capacity or generation in public power plants in one year, from Statistics Iceland's table IDN02101.
- [`hagstova_faroe_electricity_annual`](#hagstova_faroe_electricity_annual): SEV's electricity production from one source, or its sales to one consumer group, in one year, from Statistics Faroe Islands tables UO03020 and UO03030.
- [`hifld_transmission_lines`](#hifld_transmission_lines): One electric transmission line of 230 kV and above in HIFLD's Electric Power Transmission Lines layer.
- [`ieso_generation_fuel_hourly`](#ieso_generation_fuel_hourly): Ontario's generation from one fuel (or the IESO's control actions line) in one hour, from the IESO's Generator Output by Fuel Type Hourly Report.
- [`ieso_ontario_demand_hourly`](#ieso_ontario_demand_hourly): Ontario's demand or market demand in one hour, from the IESO's Hourly Demand Report.
- [`ilr_luxembourg_electricity`](#ilr_luxembourg_electricity): One month's or year's value of one Luxembourg electricity measure (withdrawals by customer class, generation, capacity, injection, trade, customers, self-consumption), from the regulator ILR's statistics workbook.
- [`imf_commodity_prices`](#imf_commodity_prices): One commodity's average price for one month, from the IMF's Primary Commodity Price System.
- [`impact_tax_rules`](#impact_tax_rules): One tax rule the economic impact tool holds (a state's severance tax, fee or option on oil and gas, or a property tax rule for a generating project), or a record that no rule is held, each with its citation.
- [`ine_es_dwellings_electricity_2021`](#ine_es_dwellings_electricity_2021): One Spanish area's (nation, autonomous community, province or municipality) count of dwellings in one electricity use band, or its median annual consumption, from INE's 2021 census.
- [`irs_soi_energy_credits_annual`](#irs_soi_energy_credits_annual): One state's (or the US's, or SOI's other areas') returns claiming, or amount of, one residential energy credit in one tax year, from IRS Statistics of Income Historic Table 2.
- [`miso_interconnection_queue`](#miso_interconnection_queue): One position in MISO's generator interconnection queue, as held on 30 September 2026 (MISO pulls paused since 4 October 2026).
- [`msha_coal_mines`](#msha_coal_mines): One US coal mine in MSHA's Mines data set, with its current status, operator, place and type.
- [`msha_coal_production_quarterly`](#msha_coal_production_quarterly): One coal mine's production, employee hours or average employees in one calendar quarter, its subunits summed, from MSHA's Quarterly Mine Employment and Production.
- [`ncsi_oman_electricity_annual`](#ncsi_oman_electricity_annual): One year's value of Oman's electricity production, distribution or connections by governorate, or production by source, from NCSI's Energy Statistics 2026 tables 11 and 12.
- [`nhc_hurdat2_track_points`](#nhc_hurdat2_track_points): One best-track fix (six-hourly, or a landfall or peak between) of one tropical or subtropical cyclone in the Atlantic or the Northeast and North Central Pacific from 2000, from NOAA's HURDAT2.
- [`nlr_atb_electricity_costs`](#nlr_atb_electricity_costs): One technology case's value of one cost or performance measure (capital cost, O&M, fuel, capacity factor, LCOE) for one projection year, from the 2025 Electricity Annual Technology Baseline of the National Laboratory of the Rockies (formerly NREL).
- [`ntd_transit_energy_annual`](#ntd_transit_energy_annual): One transit agency's fuel or energy used by one mode and type of service in one report year, from the National Transit Database.
- [`nve_norway_reservoirs_weekly`](#nve_norway_reservoirs_weekly): One Norwegian area's (the country, a price area or a water region) hydropower reservoir filling, stored energy or capacity in one week, from NVE's reservoir statistics.
- [`ons_brazil_balance_hourly`](#ons_brazil_balance_hourly): One Brazilian subsystem's (or the national interconnected system's) generation by source, load or net interchange in one hour, from ONS's energy balance.
- [`owid_ember_electricity_annual`](#owid_ember_electricity_annual): One country's or region's electricity demand or power sector greenhouse gas emissions in one year, the Ember columns of Our World in Data's energy dataset.
- [`predict_demand_forecasts`](#predict_demand_forecasts): One place's ERW forecast of demand for one UTC hour of a target day, as the forecast was made on its day (a model's output, not a published figure).
- [`predict_price_forecasts`](#predict_price_forecasts): One place's ERW forecast of its grid hub's day-ahead price for one UTC hour of a target day, as the forecast was made on its day (a model's output, not a published figure).
- [`price_congestion_hourly`](#price_congestion_hourly): One part of the day-ahead price at one hub or load zone for one hour, as SPP or CAISO splits it.
- [`price_congestion_monthly`](#price_congestion_monthly): One hub or load zone in one month, the means of its day-ahead price parts; derived from price_congestion_hourly.
- [`ree_spain_balance_monthly`](#ree_spain_balance_monthly): One month's value of one series of Spain's electrical energy balance (generation by technology, storage, exchanges, demand at busbars), from Red Electrica's REData.
- [`rrc_lease_production_monthly`](#rrc_lease_production_monthly): One Texas Railroad Commission lease's reported production of oil, casinghead gas, gas or condensate in Martin County in one month.
- [`rte_eco2mix_france_halfhourly`](#rte_eco2mix_france_halfhourly): France's consumption, production from one source or net physical exchanges in one half hour, from RTE's eco2mix national files.
- [`scb_sweden_electricity_monthly`](#scb_sweden_electricity_monthly): One month's electricity supply in Sweden from one type of production (or imports, or the sum), from Statistics Sweden's table TAB1011 (the Swedish Energy Agency's statistics).
- [`scripps_co2_mlo_monthly`](#scripps_co2_mlo_monthly): Atmospheric CO2 at Mauna Loa Observatory in one month, from the Scripps CO2 Program's in situ record.
- [`singstat_singapore_electricity`](#singstat_singapore_electricity): Singapore's monthly electricity generation (table M890831), or one row of its annual generation and consumption by sector (table M890841), from SingStat's Table Builder.
- [`smard_germany_monthly`](#smard_germany_monthly): Germany's actual generation from one source, or its grid load, in one month, from the Bundesnetzagentur's SMARD.
- [`sne_panama_electricity_annual`](#sne_panama_electricity_annual): One year's value of one Panama electricity measure (gross generation by plant type or system, net production, maximum demand, load factor), from the Secretaria Nacional de Energia's historical series.
- [`sne_panama_generation_monthly`](#sne_panama_generation_monthly): Panama's total gross generation in one month, from the Secretaria Nacional de Energia's Cuadro GE-10.
- [`sors_serbia_electricity_annual`](#sors_serbia_electricity_annual): One item of Serbia's balance of electricity in 2024 (production, trade, transformation, own use, losses, final consumption by sector), from the statistics office's Energy Balances table 1.
- [`ssb_norway_electricity_monthly`](#ssb_norway_electricity_monthly): One month's value of one line of Norway's electricity balance (generation by source, trade, consumption by industry and households, losses), from Statistics Norway's table 14091.
- [`stat_kz_kazakhstan_electricity_annual`](#stat_kz_kazakhstan_electricity_annual): One year's value of one item of the electricity column of Kazakhstan's fuel and energy balance (output by plant class, trade, own use, losses, consumption by sector), from the Bureau of National Statistics.
- [`stat_tj_tajikistan_electricity_annual`](#stat_tj_tajikistan_electricity_annual): One year's value of Tajikistan's electricity output by plant type, trade, losses or consumption by sector, from the Agency on Statistics' analytical table 11.
- [`statat_austria_electricity_annual`](#statat_austria_electricity_annual): One year's value of one item of Austria's electricity balance (trade, transformation input and output by plant type, owner and fuel, final energy use by sector, energy sector use by branch), from Statistics Austria's energy balances.
- [`statat_austria_electricity_monthly`](#statat_austria_electricity_monthly): One month's value of Austria's net electricity production by source or of its monthly balance, from Statistics Austria's monthly electricity statistics.
- [`statbank_moldova_electricity_monthly`](#statbank_moldova_electricity_monthly): One month's value of one electricity indicator of Moldova's stocks, inputs and consumption, from the National Bureau of Statistics' StatBank table ENE010100.
- [`statbel_be_electricity_production_annual`](#statbel_be_electricity_production_annual): Belgium's gross electricity production from one energy product (or in total) in one year, from Statbel's beSTAT.
- [`statee_estonia_electricity_monthly`](#statee_estonia_electricity_monthly): One month's value of Estonia's electricity production (total, hydro, wind, solar), imports or exports, from Statistics Estonia's table KE21.
- [`statfi_finland_electricity_monthly`](#statfi_finland_electricity_monthly): One month's value of one line of Finland's electricity supply and consumption (generation by source, net imports by country, total consumption), from Statistics Finland's table 12su.
- [`statsbots_botswana_electricity_monthly`](#statsbots_botswana_electricity_monthly): One month's Botswana local generation, imports or distribution, or one quarter's generation or imports by source, from Statistics Botswana's Electricity Stats Brief.
- [`statsmu_mauritius_electricity_annual`](#statsmu_mauritius_electricity_annual): One year's value of one Mauritius electricity measure (generation by source, renewable share, sales, capacity, peak demand), from Statistics Mauritius' Energy and Water Statistics.
- [`usace_nid_dams`](#usace_nid_dams): One dam (or a dam's associated structure) in the U.S. Army Corps of Engineers' National Inventory of Dams.
- [`usdm_drought_state_weekly`](#usdm_drought_state_weekly): One contiguous state's percent of area in one U.S. Drought Monitor category (cumulative) in one weekly map.
- [`uspvdb_solar_facilities`](#uspvdb_solar_facilities): One large-scale solar photovoltaic facility in the USGS U.S. Large-Scale Solar Photovoltaic Database.
- [`uswtdb_wind_turbines`](#uswtdb_wind_turbines): One utility-scale land-based or offshore wind turbine in the USGS U.S. Wind Turbine Database.
- [`wapa_energy_sales_annual`](#wapa_energy_sales_annual): One WAPA project's (or WAPA's total) energy sold or power rate in one federal fiscal year, from WAPA's Rates and Sales Data.
- [`weather_forecast_hourly`](#weather_forecast_hourly): One airport's forecast temperature or wind speed for one hour, from the National Weather Service's hourly forecast.
- [`weather_forecast_issued_hourly`](#weather_forecast_issued_hourly): One NWS hourly forecast value (temperature or wind) for one airport and one forecast hour, as one issue gave it; the variable names the lead in days (the hour's UTC date less the issue's).
- [`weather_obs_hourly`](#weather_obs_hourly): One airport's mean observed temperature or wind speed in one hour, from the National Weather Service API.
- [`wfigs_wildfires`](#wfigs_wildfires): One wildfire of 1,000 acres or more discovered from 2015, from NIFC's WFIGS Incident Locations.

### `abs_suriname_electricity_annual`

One year's value of one Suriname electricity measure (EBS's demand by category, net generation, net consumption or capacity, or a Staatsolie plant's generation), from the statistics office's Environment Statistics Publication.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 56.

- **Time:** ts_utc is the year's first day at 00:00:00Z; freq P1Y.
- **Revisions:** Rewritten whole as one snapshot by each run from the saved publication; vintage is the publication's last-modified time.
- **Source:** abs_sr:milieustatistieken_2024_tables_7_1_7_4_7_8_7_9 Algemeen Bureau voor de Statistiek in Suriname (ABS), Milieustatistieken Publicatie / Environment Statistics Publication, December 2024, tables 7.1, 7.4, 7.8 and 7.9 (sources: N.V. EnergieBedrijven Suriname; Staatsolie)
- **Method note:** [`docs/methods/abs_suriname_electricity_annual.md`](../methods/abs_suriname_electricity_annual.md)
- **Cite as:** Algemeen Bureau voor de Statistiek in Suriname (ABS). Milieustatistieken Publicatie / Environment Statistics Publication, December 2024, tables 7.1, 7.4, 7.8 and 7.9. Via the Energy Research Warehouse (ERW), table `abs_suriname_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: abs_sr:ebs, abs_sr:ebs:<demand category> or abs_sr:staatsolie:<plant> | none | text | abs_sr:ebs, abs_sr:ebs:commercial, abs_sr:ebs:industrial, abs_sr:ebs:other, abs_sr:ebs:residential, abs_sr:ebs:total, abs_sr:staatsolie:afobaka_hydro, abs_sr:staatsolie:saramacca_backup, abs_sr:staatsolie:tout_lui_faut_thermal | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 167.7 to 1470000.0; 53 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: SR on every row | none | text | SR | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 56 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: ABS's label of the row (English part), not a pricing node | none | text | Afobaka Hydro Operations for the purpose of EPAR (EBS), Available Capacity, Commercial, Energy production (back-up production in Saramacca), Industrial, Installed Capacity, Net Consumption, Other, Residential, Total, Total Electricity Net Generation, Tout Lui Faut Thermal Power Plant for the purpose of EBS | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | abs_sr:milieustatistieken_2024_tables_7_1_7_4_7_8_7_9 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://statistics-suriname.org/wp-content/uploads/2024/12/Elfde-Milieustatistieken-pub-dec-2024.pdf | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T00:27:21Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The publication's last-modified time (UTC) | none | utc time | 2024-12-31T08:40:24Z | 0 |
| `x_table` | The publication's table the row is read from (7.1 capacity, 7.4 demand, 7.8 net generation and consumption, 7.9 Staatsolie's generation) | none | number | 7.1, 7.4, 7.8, 7.9 | 0 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `available_capacity` | EBS's available capacity, table 7.1 | MW | 3 | 2019-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `demand` | EBS's electricity demand in the year by customer category (residential, commercial, industrial, other, total), table 7.4 | MWh | 25 | 2019-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `generation` | A Staatsolie plant's electricity generation in the year, table 7.9 | MWh | 15 | 2019-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `installed_capacity` | EBS's installed capacity, table 7.1 | MW | 3 | 2019-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `net_consumption` | EBS's net consumption in the year, table 7.8 | MWh | 5 | 2019-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `net_generation` | EBS's total electricity net generation in the year, table 7.8 | MWh | 5 | 2019-01-01T00:00:00Z | 2023-01-01T00:00:00Z |

### `aedg_alaska_generation_monthly`

One Alaska service area's electricity generation from one fuel in one month, from the Alaska Energy Data Gateway.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 51061.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; 2001 to 2021.
- **Revisions:** Rewritten whole as one snapshot by each run from the Gateway's one JSON answer; vintage is not filled.
- **Source:** aedg_ak:public_monthly_generation_v3 Alaska Center for Energy and Power (ACEP) at the University of Alaska Fairbanks (UAF). Monthly Electrical Generation By Community. Version v3.0. Alaska Energy Data Gateway, 2026
- **Method note:** [`docs/methods/aedg_alaska_generation_monthly.md`](../methods/aedg_alaska_generation_monthly.md)
- **Cite as:** Alaska Energy Data Gateway (ACEP, University of Alaska Fairbanks). Monthly Electrical Generation By Community, v3.0. Via the Energy Research Warehouse (ERW), table `aedg_alaska_generation_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: aedg:ak:<service area id>:<fuel>, the Gateway's service_area_geom_id and its fuel type as a slug | none | text | for example aedg:ak:100_1:distillate_oil, aedg:ak:100_1:hydro, aedg:ak:103_1:distillate_oil; 271 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z to 2021-12-01T00:00:00Z; 252 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -418.0 to 280929.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-AK on every row | none | text | US-AK | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 51061 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The service area's first community in alphabetical order and how many others share its grid, not a pricing node | none | text | for example Adak, Akhiok, Akiachak; 175 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | aedg_ak:public_monthly_generation_v3 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://akenergygateway.alaska.edu/explore/data/public_monthly_generation/datasets/public_monthly_generation | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T10:36:35Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 51061 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `generation` | The service area's electricity generation from the fuel in the month, as published (negatives kept: net generation, storage's own use) | MWh | 51061 | 2001-01-01T00:00:00Z | 2021-12-01T00:00:00Z |

### `aeso_alberta_load_hourly`

Alberta's internal load in one hour, from the Alberta Electric System Operator's Historical Pool Price report.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 15853.

- **Time:** ts_utc is the hour's start in UTC (AESO's hour ending in Alberta local time, read through America/Edmonton); freq PT1H.
- **Revisions:** Merged by (entity, variable, ts_utc): each run's hours replace the same hours and older ones are kept; vintage is not filled (the report states no publication time).
- **Source:** aeso:historical_pool_price Alberta Electric System Operator, Historical Pool Price report (Energy Trading System) (http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalPoolPriceReportServlet)
- **Method note:** [`docs/methods/aeso_alberta_load_hourly.md`](../methods/aeso_alberta_load_hourly.md)
- **Cite as:** Alberta Electric System Operator (AESO), Canada. Historical Pool Price report, Alberta internal load. Via the Energy Research Warehouse (ERW), table `aeso_alberta_load_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: aeso:alberta on every row | none | text | aeso:alberta | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-01-01T07:00:00Z to 2026-10-23T19:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 8295.0 to 12785.0; 3436 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: CA-AB on every row | none | text | CA-AB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 15853 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Alberta on every row, not a pricing node | none | text | Alberta | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | aeso:historical_pool_price | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalPoolPriceReportServlet?beginDate=01012025&endDate=12312025&contentType=csv, http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalPoolPriceReportServlet?beginDate=12312025&endDate=10242026&contentType=csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T20:08:46Z, 2026-10-23T20:09:04Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: the report states no publication time | none | empty | no cell holds a value | 15853 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `ail_demand` | Alberta internal load (AIL), the hour's demand | MW | 15853 | 2025-01-01T07:00:00Z | 2026-10-23T19:00:00Z |

### `ai_energy_published`

One energy figure for AI (per query, per token, of a training run or of a fleet) as a model maker, a cloud operator or a peer-reviewed paper printed it.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 23.

- **Time:** event_date is the publication's date; x_retrieved_at is when its copy was saved.
- **Revisions:** Rewritten whole as one snapshot by each build from the session-read rows file; nothing converted, summed or averaged.
- **Source:** erw:ai_energy_published the publications named per row (source_url), saved at warehouse/raw/ai_energy_published/ with their sha256: https://arxiv.org/abs/1906.02243; https://arxiv.org/abs/2104.10350; https://arxiv.org/abs/2204.05149; https://arxiv.org/abs/2211.02001; https://arxiv.org/abs/2311.16863; https://arxiv.org/abs/2508.15734; https://blog.samaltman.com/the-gentle-singularity; https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/msc/documents/presentations/CSR/2026-Microsoft-Environmental-Data-Fact-Sheet-PDF.pdf (https://sustainability.atmeta.com/asset/2025-environmental-data-index)
- **Method note:** [`docs/methods/ai_energy_published.md`](../methods/ai_energy_published.md)
- **Cite as:** Energy Research Warehouse (ERW), from published figures. Energy per AI query, as published (docs/methods/ai_energy_published.md). Via the Energy Research Warehouse (ERW), table `ai_energy_published`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: ai_energy:<publication>_<n> | none | text | ai_energy:bloom_2022_1, ai_energy:bloom_2022_2, ai_energy:bloom_2022_3, ai_energy:google_2025_1, ai_energy:google_2025_2, ai_energy:google_2025_3, ai_energy:luccioni_2024_1, ai_energy:luccioni_2024_2, ai_energy:luccioni_2024_3, ai_energy:meta_2025_1, ai_energy:microsoft_2026_1, ai_energy:openai_2025_1, ai_energy:patterson_2021_1, ai_energy:patterson_2021_2, ai_energy:patterson_2021_3, ai_energy:patterson_2021_4, ai_energy:patterson_2021_5, ai_energy:patterson_2021_6, ai_energy:patterson_2022_1, ai_energy:patterson_2022_2, ai_energy:patterson_2022_3, ai_energy:strubell_2019_1, ai_energy:strubell_2019_2 | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which). Here: The publication's date | none | date | 2019-06-05, 2021-04-21, 2022-04-11, 2022-11-03, 2024-06-03, 2025-06-10, 2025-08-21, 2025-09-12, 2026-07-09 | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: publication on every row | none | text | publication | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: The publisher (the company, or the authors' institution) | none | text | Google, Google and the University of California at Berkeley, Hugging Face (BigScience) with Graphcore and LISN, Hugging Face and Carnegie Mellon University, Meta, Microsoft, OpenAI (Sam Altman's blog), University of Massachusetts Amherst | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 23 |
| `mw` | The capacity involved, in megawatts. Here: Not filled: no cell holds a value | MW | empty | no cell holds a value | 23 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise. Here: Not filled: no cell holds a value | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 23 |
| `currency` | The currency of the price, as an ISO 4217 code (USD). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 23 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: published on every row | none | text | published | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ai_energy_published | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://arxiv.org/abs/1906.02243, https://arxiv.org/abs/2104.10350, https://arxiv.org/abs/2204.05149, https://arxiv.org/abs/2211.02001, https://arxiv.org/abs/2311.16863, https://arxiv.org/abs/2508.15734, https://blog.samaltman.com/the-gentle-singularity, https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/msc/documents/presentations/CSR/2026-Microsoft-Environmental-Data-Fact-Sheet-PDF.pdf, https://sustainability.atmeta.com/asset/2025-environmental-data-index | 0 |
| `x_publisher_kind` | Who printed the figure: model maker, cloud operator, data center operator (or several), or peer-reviewed paper (the source's name: publisher_kind) | none | text | model maker, model maker and cloud operator, model maker and data center operator, peer-reviewed paper | 0 |
| `x_peer_reviewed` | yes, with the venue, only where the page read names it; otherwise no, with the kind of publication (preprint, company report, blog post) (the source's name: peer_reviewed) | none | text | no (a blog post by the company's chief executive), no (a company report), no (preprint as read; the arXiv page names no journal), no (preprint by the model maker), no (preprint), yes (ACL 2019), yes (ACM FAccT '24) | 0 |
| `x_title` | The publication's title (the source's name: title) | none | text | 2025 Environmental Data Index (2025 Sustainability Report), 2026 Environmental Sustainability Report Data Fact Sheet, Carbon Emissions and Large Neural Network Training, Energy and Policy Considerations for Deep Learning in NLP, Estimating the Carbon Footprint of BLOOM, a 176B Parameter Language Model, Measuring the environmental impact of delivering AI at Google Scale, Power Hungry Processing: Watts Driving the Cost of AI Deployment?, The Carbon Footprint of Machine Learning Training Will Plateau, Then Shrink, The Gentle Singularity | 0 |
| `x_authors` | The publication's authors (the source's name: authors) | none | text | Alexandra Sasha Luccioni, Sylvain Viguier, Anne-Laure Ligozat, Alexandra Sasha Luccioni, Yacine Jernite, Emma Strubell, Cooper Elsworth, Keguo Huang, David Patterson, Ian Schneider, Robert Sedivy, Savannah Goodman, Ben Townsend, Parthasarathy Ranganathan, Jeff Dean, Amin Vahdat, Ben Gomes, James Manyika, David Patterson, Joseph Gonzalez, Quoc Le, Chen Liang, Lluis-Miquel Munguia, Daniel Rothchild, David So, Maud Texier, Jeff Dean, David Patterson, Joseph Gonzalez, Urs Hölzle, Quoc Le, Chen Liang, Lluis-Miquel Munguia, Daniel Rothchild, David So, Maud Texier, Jeff Dean, Emma Strubell, Ananya Ganesh, Andrew McCallum, Meta Platforms, Microsoft, Sam Altman | 0 |
| `x_page` | The page of the publication the figure is printed on (the source's name: page) | none | text | 1, 12, 2, 4, 5, 5 to 6, 6, 7, 8, the post (one page) | 0 |
| `x_printed` | The publication's own words holding the figure, cut from its saved copy (the source's name: printed) | none | text | % of Google 2019 total energy consumption (12.2 TWh, (0.047 vs. 2.9 kWh), 10.8 TWh for Microsoft, BERT V100x64 12,041.51 79 1507, Data centers total 6,966,000 9,117,122 11,167,416 14,975,435 18,061,781, Electricity 10,770,714 13,621,517 18,153,454 23,567,502 29,829,540 37,026,353, NAS P100x8 1515.43 274,120 656,347, The NAS producing Evolved Transformer used 7.5 MWh, The largest size has 11B parameters, and training used 86 MWh, Total energy used 433,196 kWh, Training GShard-600B used 24 MWh, Training Meena used [...] 232 MWh, We estimated it used 179 MWh, image generation, whose mean consumption is 2.9 kWh, its energy consumption is 1287 MWh, the annual energy consumption in 2020 was 15.4 TWh for Google, the average query uses about 0.34 watt-hours, the calculated energy consumption is only 0.10 Wh per prompt, the instance used for the BLOOM model API consumed 914 kWh of electricity, the primary energy draw originates from the active AI Accelerator power (0.14 Wh, 58% of total), to 1.0×10−4 kWh for the biggest one, we find the median Gemini Apps text prompt consumes 0.24 Wh of energy, which represents an electrical consumption of 1,163,032 kWh | 0 |
| `x_value` | The number in the printed words, in x_unit | the row's x_unit | number | 0.0001, 0.047, 0.1, 0.14, 0.24, 0.34, 10.8, 1163032.0, 12.2, 1287.0, 15.4, 1507.0, 179.0, 18061781.0, 2.9, 232.0, 24.0, 37026353.0, 433196.0, 656347.0, 7.5, 86.0, 914.0 | 0 |
| `x_unit` | The unit of x_value, the publication's own (Wh, kWh, MWh, TWh) (the source's name: unit) | none | text | MWh, TWh, Wh, kWh | 0 |
| `x_measures` | What the figure measures, in words (energy per prompt, per query, per 1,000 inferences, of a training run, of a fleet in a year) (the source's name: measures) | none | text | energy of a deployment, energy of a fleet in a year, energy of a fleet in a year (electricity consumed within the organization), energy of a fleet in a year (electricity consumed), energy of a training run, energy of a training run (kWh times PUE), energy of all the experiments of a project, energy per 1,000 inferences (the mean of the image generation task), energy per 1,000 inferences (the mean of the text generation task), energy per inference, energy per prompt, energy per prompt (one part of it), energy per query | 0 |
| `x_subject` | What the figure is of (a model, a fleet, a company) (the source's name: subject) | none | text | BERT base on 64 V100 GPUs, BLOOM (176 billion parameters), BLOOMz-7B, GPT-3 (175 billion parameters; OpenAI's model), GShard-600B (600 billion parameters), Google's annual energy consumption, Google's total energy consumption, Meena (2.6 billion parameters), Meta's data centers, Microsoft (its datacenters and offices together, as the fact sheet counts them), Microsoft's annual energy consumption, Switch Transformer (1500 billion parameters), T5 (11 billion parameters), image generation (the models of the study), neural architecture search for the Evolved Transformer (So et al.) on 8 P100 GPUs, text generation (the models of the study), the BLOOM model's API instance, the BigScience workshop's experiments (3.46 million GPU hours, BLOOM's training among them), the average ChatGPT query, the median Gemini Apps text prompt, the neural architecture search that produced Evolved Transformer | 0 |
| `x_period` | The period the figure covers, as the publication states it, or not stated (the source's name: period) | none | text | 2019, 2020, 2024 (the index reports the fiscal year 2024; the table runs 2020 to 2024), May 2025, May 2025 (page 7), fiscal year 2025 (ended 30 June 2025; the table runs FY20 to FY25), not stated, the BigScience project, the paper's deployment study, the study's experiments, the training, 118 days | 0 |
| `x_basis` | The boundary the publication states for the figure, or not stated (the source's name: basis) | none | text | Google's own report as the paper cites it ([Goo20]), the denominator of its Table 4, a narrower boundary, as the paper describes it: a methodology aligned with a more narrow, existing approach (its Figure 1), as the paper measures it for Google's own models, as the paper states it, not stated, the active AI accelerators only, the fact sheet's Table 5, Energy consumption within the organization (MWh); the date is that of Microsoft's post accompanying the report, as its address on blogs.microsoft.com gives it (2026/07/09); the fact sheet prints no date of its own, the hyperscaler's sustainability report, as the paper cites it, the index's table Electricity Consumption by Facility, in MWh; the date is the report's launch as Meta's news page dates it (12 September 2025), the mean over the study's models for the task, on its hardware, the paper's Table 1, the paper's comprehensive boundary: active AI accelerators, host CPU and DRAM, idle machines provisioned, data center overhead (PUE), the paper's estimate, the paper's estimate ("Its estimated carbon emissions due to training are 552 tCO2e and its energy consumption is 1287 MWh"), the paper's estimate (its Table 3, column kWh·PUE), the paper's measurement, the study's measurement | 0 |
| `x_saved_as` | The path of the publication's saved copy in the warehouse's raw files | none | text | warehouse/raw/ai_energy_published/20261119T1230Z/altman_2025.html, warehouse/raw/ai_energy_published/20261119T1230Z/bloom_2022.pdf, warehouse/raw/ai_energy_published/20261119T1230Z/google_2025.pdf, warehouse/raw/ai_energy_published/20261119T1230Z/luccioni_2024.pdf, warehouse/raw/ai_energy_published/20261119T1230Z/meta_2025_data_index.pdf, warehouse/raw/ai_energy_published/20261119T1230Z/microsoft_2026_fact_sheet.pdf, warehouse/raw/ai_energy_published/20261119T1230Z/patterson_2021.pdf, warehouse/raw/ai_energy_published/20261119T1230Z/patterson_2022.pdf, warehouse/raw/ai_energy_published/20261119T1230Z/strubell_2019.pdf | 0 |
| `x_sha256` | The SHA-256 of the saved copy | none | text | 0af70b6db33650b01829bd3a59c1f3659f45e301300ec711f264e48735e5e8b7, 0fd180837df00b3427c3eae484a492224b8f18c381e82a2aed98b04553a197f6, 348b58c832076258e1792a710fab3f0ac60f02001857532a7136771b52b30339, 89b7f0b905caffc9d43f2dcbdd08c517bcfc02ab963417f7e9facf8b35b876b3, 997025051680fd262e80da571ddb74d2af4e8f023baea9b6d4bd7539d163ab33, 99baa6948df14609dcbbc078cbef024bebb2fd62e842c027cb8859e5f5814701, a23ccf280f496629a81a6117faa8ded7ade5f292e3dc5ce36203b2a979679f63, cd8c3732e179f9a71a8dd42efabf7ffe7ee2bfc6c4ce4d63cfe799609b58dd12, d7527cd23308869105b404b486117603bb3f5ee10e30499367f8698110afb66d | 0 |
| `x_retrieved_at` | When the publication's copy was saved, UTC | none | utc time | 2026-11-19T12:24:38Z, 2026-11-19T12:24:40Z, 2026-11-19T12:24:58Z, 2026-11-19T12:25:20Z, 2026-11-19T12:25:37Z, 2026-11-19T12:25:54Z, 2026-11-19T12:26:27Z, 2026-11-19T13:19:34Z, 2026-11-19T13:53:18Z | 0 |

### `aneel_siga_plants`

One Brazilian central generation plant in ANEEL's SIGA register (operating, under construction or not yet begun).

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 25042.

- **Time:** No time column; status_date is the first unit's entry into operation; the register as ANEEL generated it on x_dataset_date.
- **Revisions:** Rewritten whole as one snapshot by each run from ANEEL's one CSV; vintage is the file's Last-Modified.
- **Source:** aneel:siga Agencia Nacional de Energia Eletrica (ANEEL), SIGA - Sistema de Informacoes de Geracao da ANEEL (open data portal) (https://dadosabertos.aneel.gov.br/dataset/siga-sistema-de-informacoes-de-geracao-da-aneel)
- **Method note:** [`docs/methods/aneel_siga_plants.md`](../methods/aneel_siga_plants.md)
- **Cite as:** Agencia Nacional de Energia Eletrica (ANEEL). SIGA - Sistema de Informacoes de Geracao da ANEEL (generation plants, open data portal, monthly CSV). Via the Energy Research Warehouse (ERW), table `aneel_siga_plants`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: aneel_siga:<CodCEG>, ANEEL's unique plant code (type, source, state, number, check digit, version) | none | text | for example aneel_siga:CGH.PH.AL.000476-6.1, aneel_siga:CGH.PH.AL.028544-7.1, aneel_siga:CGH.PH.AL.028545-5.1; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: plant on every row | none | text | plant | 0 |
| `name` | The thing's name, as the publisher writes it. Here: ANEEL's plant name (NomEmpreendimento) | none | text | for example 10028, 10032, 10033; more than 5000 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: BR-<the plant's main state> | none | text | for example BR-AC, BR-AL, BR-AM; 27 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: ANEEL's approximate centroid; empty where ANEEL gives 0 and 0 | degree | number | -33.72280556 to 4.715; more than 5000 distinct | 465 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: ANEEL's approximate centroid; empty where ANEEL gives 0 and 0 | degree | number | -72.81111111 to -32.41720121; more than 5000 distinct | 465 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: The granted or registered capacity (MdaPotenciaOutorgadaKw / 1,000) | MW | number | 1e-05 to 11233.1; 2175 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: operating, under_construction or planned (not yet begun), from ANEEL's phase | none | text | operating, planned, under_construction | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The first generating unit's entry into operation (DatEntradaOperacao); empty where ANEEL gives its placeholder 1900-01-03 | none | date | 1900-12-25 to 2026-09-02; 3891 distinct | 2398 |
| `operator` | The operator or owner, as the publisher writes it. Here: Not filled | none | empty | no cell holds a value | 25042 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | aneel:siga | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://dadosabertos.aneel.gov.br/dataset/6d90b77c-c5f5-4d81-bdec-7bc619494bb9/resource/11ec447d-698d-4ab8-977f-b424d5deee6a/download/siga-empreendimentos-geracao.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T06:57:16Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The CSV's Last-Modified (UTC) | none | utc time | 2026-10-01T05:01:27Z | 0 |
| `x_ceg` | ANEEL's unique code of the plant (GGG.FF.UF.999999-D.VV: type, source, main state, number, check digit, version) (the source's name: CodCEG) | none | text | for example CGH.PH.AL.000476-6.1, CGH.PH.AL.028544-7.1, CGH.PH.AL.028545-5.1; more than 5000 distinct | 0 |
| `x_generation_type` | ANEEL's generation type: UHE hydro plant, PCH small hydro, CGH mini hydro, EOL wind, UFV solar photovoltaic, UTE thermal, UTN nuclear (the source's name: SigTipoGeracao) | none | text | CGH, EOL, PCH, UFV, UHE, UTE, UTN | 0 |
| `x_phase` | ANEEL's phase in Portuguese: Operacao (operating), Construcao (under construction), Construcao nao iniciada (not yet begun) (the source's name: DscFaseUsina) | none | text | Construção, Construção não iniciada, Operação | 0 |
| `x_fuel_origin` | ANEEL's fuel origin in Portuguese (biomass, wind, fossil, hydro, nuclear, solar) (the source's name: DscOrigemCombustivel) | none | text | Biomassa, Eólica, Fóssil, Hídrica, Nuclear, Solar | 0 |
| `x_fuel_source` | ANEEL's fuel source in Portuguese (hydraulic potential, wind, solar radiation, natural gas, petroleum, agro-industrial residues and others) (the source's name: DscFonteCombustivel) | none | text | Agroindustriais, Biocombustíveis líquidos, Carvão mineral, Cinética do vento, Floresta, Gás natural, Outros Fósseis, Petróleo, Potencial hidráulico, Radiação solar, Resíduos animais, Resíduos sólidos urbanos, Urânio | 0 |
| `x_fuel_name` | ANEEL's fuel name in Portuguese (sugarcane bagasse, biogas and others) (the source's name: NomFonteCombustivel) | none | text | for example Bagaço de Cana de Açúcar, Biogás - Floresta, Biogás - RA; 31 distinct | 0 |
| `x_grant_type` | ANEEL's grant type: Registro (registration), Autorizacao (authorization), Concessao (concession); joined by ; for the three plants listed under two (the source's name: DscTipoOutorga) | none | text | Autorização, Autorização;Concessão, Concessão, Registro | 0 |
| `x_capacity_operating_mw` | The capacity in operation (for a plant no longer operating, the last power considered in operation) (the source's name: MdaPotenciaFiscalizadaKw) | MW | number | 0.0 to 11233.1; 1840 distinct | 0 |
| `x_physical_guarantee_mw` | The plant's physical guarantee approved by the Ministry of Mines and Energy (the source's name: MdaGarantiaFisicaKw) | MW | number | 0.0 to 7750.8; 1052 distinct | 0 |
| `x_qualified_generation` | ANEEL's qualified generation indicator as published: Sim (yes) or Nao (no) (the source's name: IdcGeracaoQualificada) | none | text | Não, Sim | 15957: ANEEL leaves the field blank |
| `x_grant_start` | The start of the grant's validity (the source's name: DatInicioVigencia) | none | date | 1970-07-17 to 2032-09-25; 1481 distinct | 19683: ANEEL gives no grant dates (most registered plants) |
| `x_grant_end` | The end of the grant's validity (the source's name: DatFimVigencia) | none | date | 1998-09-15 to 2063-01-14; 1677 distinct | 19693: ANEEL gives no grant dates (most registered plants) |
| `x_ownership` | The owners and their shares, as ANEEL's text (the source's name: DscPropriRegimePariticipacao) | none | text | for example 0.0100% para COTRIJUC - COOPERATIVA AGROPECUARIA JULIO DE CASTILHOS - 91.023.168/0001-78 (REG), 10% para ENERGETICA UVAIA LTDA - 10.980.551/0001-12 (REG), 10% para TEXTILFIO MALHAS LTDA - 00.214.242/0001-88 (REG), 10% para CRISTALCOPO S/A - 05.316.470/0001-82 (REG), 10% para CATARINENSE DISTRIBUIDORA DE PROD CONGELADOS LTDA - 79.508.156/0001-38 (REG), 10% para BRISA COMERCIO DE ALIMENTOS LTDA - 16.939.428/0001-34 (REG), 10% para ESDEL COMERCIO DE PRODUTOS ALIMENTARES LTDA - 79.456.703/0001-89 (REG), 10% para FIBRAOESTE INDUSTRIA E COMERCIO LTDA - 85.140.663/0001-64 (REG), 10% para SOCIEDADE HOSPITALAR SAO MIGUEL DO OESTE LTDA - 86.247.574/0001-84 (REG), 10% para MAXI COLOR EMPREENDIMENTOS E PARTICIPACOES LTDA - 47.615.091/0001-33 (REG), 10% para HIGH TECH EQUIPAMENTOS INDUSTRIAIS LTDA - 80.706.229/0001-85 (REG), 100% para '' BG NORTE PETROLEO LTDA '' - 04.890.965/0001-58 (REG); more than 5000 distinct | 0 |
| `x_sub_basin` | The river sub-basin, ANEEL's number and name (the source's name: DscSubBacia) | none | text | for example 15 - Madeira, 16 - Amazonas, entre os rios Madeira e Trombetas, 17 - Tapajos; 60 distinct | 23589: ANEEL leaves the field blank (most non-hydro plants) |
| `x_municipalities` | The municipalities the plant lies in, with their states (the source's name: DscMuninicpios) | none | text | for example Abadia dos Dourados - MG, Abaiara - CE, Abdon Batista - SC; 2182 distinct | 0 |
| `x_dataset_date` | ANEEL's generation date of the dataset (the source's name: DatGeracaoConjuntoDados) | none | date | 2026-10-01 | 0 |

Waiting for a second look: x_qualified_generation (ANEEL's IdcGeracaoQualificada, Sim or Nao): what makes generation qualified is not written in the connector, the method note or the header. Read again on 20 November 2026 in the connector, the method note and the saved SIGA CSV under warehouse/raw/aneel_siga (data rows only, no dictionary): not found..

### `asli_liechtenstein_electricity_annual`

One year's value of Liechtenstein's electricity production, imports, exports or consumption, from the statistics office's Energie table 5.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 164.

- **Time:** ts_utc is the year's first day at 00:00:00Z; freq P1Y; from 1985.
- **Revisions:** Rewritten whole as one snapshot by each run from the saved workbook; vintage is not filled.
- **Source:** asli_li:energie_2025_tabelle5 Amt fuer Statistik Liechtenstein, Energie 2025, Tabelle 5: Stromproduktion und -verbrauch seit 1985 (CC BY 4.0)
- **Method note:** [`docs/methods/asli_liechtenstein_electricity_annual.md`](../methods/asli_liechtenstein_electricity_annual.md)
- **Cite as:** Amt fuer Statistik Liechtenstein. Energie 2025, Tabelle 5: Stromproduktion und -verbrauch seit 1985. Via the Energy Research Warehouse (ERW), table `asli_liechtenstein_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: asli:li:<item>: production, imports, exports, consumption | none | text | asli:li:consumption, asli:li:exports, asli:li:imports, asli:li:production | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1985-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 41 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 417594.639; 137 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: LI on every row | none | text | LI | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 164 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The table's column in German, not a pricing node | none | text | Export, Import, Produktion im Inland, Verbrauch im Inland | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | asli_li:energie_2025_tabelle5 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.statistikportal.li/statistikportal/publications/551-energie/2025/01/1/551.2025.01.1_02_energie-2025-tabellen.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T06:49:03Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 164 |
| `x_pv_method` | How photovoltaic production is counted: old (to 2021) or new (from 2022); the Office changed its method in 2023 | none | text | new, old | 0 |
| `x_old_method_value` | On 2022's rows only, the figure by the old photovoltaic method | MWh | number | 0.0, 100496.177, 308825.0, 409321.177 | 160: Empty on every year but 2022 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` | Electricity consumed in Liechtenstein in the year | MWh | 41 | 1985-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `exports` | Electricity exported in the year | MWh | 41 | 1985-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `generation` | Electricity produced in Liechtenstein in the year | MWh | 41 | 1985-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `imports` | Electricity imported in the year | MWh | 41 | 1985-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `asub_aland_electricity_annual`

One year's electricity supply to Aland from one origin (imports from Sweden or Finland; oil, wind, bioenergy or solar production), or the total, from ASUB's table MI009.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 190.

- **Time:** ts_utc is the year's first day at 00:00:00Z; freq P1Y; 1994 to 2025.
- **Revisions:** Rewritten whole as one snapshot by each run from one JSON-stat query; vintage is not filled.
- **Source:** asub_ax:MI009 Statistics and Research Aland (ASUB), Anskaffning och produktion av el
- **Method note:** [`docs/methods/asub_aland_electricity_annual.md`](../methods/asub_aland_electricity_annual.md)
- **Cite as:** Statistics and Research Aland (ASUB). Table MI009: Anskaffning och produktion av el (electricity supply and production by origin). Via the Energy Research Warehouse (ERW), table `asub_aland_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: asub:ax:<origin> | none | text | asub:ax:bioenergy, asub:ax:import_finland, asub:ax:import_sweden, asub:ax:oil, asub:ax:solar, asub:ax:total, asub:ax:wind | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1994-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 32 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 351500.0; 158 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: AX on every row | none | text | AX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 190 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The origin as ASUB names it in Swedish, not a pricing node | none | text | Bioenergi, Import Finland, Import Sverige, Olja, Solkraft, Totalt, Vindkraft | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | asub_ax:MI009 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://pxweb.asub.ax/PXWeb/api/v1/sv/Statistik/MI/MI009.px | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T08:54:42Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 190 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `generation` | Electricity produced on Aland from the origin in the year (physical production) | MWh | 94 | 1994-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `imports` | Electricity imported from Sweden or Finland in the year | MWh | 64 | 1994-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `supply` | Aland's total electricity supply in the year | MWh | 32 | 1994-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `asub_aland_electricity_sales_annual`

One year's electricity sales of one Aland distributor region to one sector (or its total), or Aland's exports, from ASUB's table MI010.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 603.

- **Time:** ts_utc is the year's first day at 00:00:00Z; freq P1Y; 1980, 1985, 1990 and each year from 1994.
- **Revisions:** Rewritten whole as one snapshot by each run from one JSON-stat query; vintage is not filled.
- **Source:** asub_ax:MI010 Statistics and Research Aland (ASUB), Elforsaljningen efter ar, region, sald effekt och bransch
- **Method note:** [`docs/methods/asub_aland_electricity_sales_annual.md`](../methods/asub_aland_electricity_sales_annual.md)
- **Cite as:** Statistics and Research Aland (ASUB). Table MI010: Elforsaljningen (electricity sales by year, region, sector). Via the Energy Research Warehouse (ERW), table `asub_aland_electricity_sales_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: asub:ax:<region>:<sector>; sectors total, households, agriculture, industry, services, public_sector | none | text | asub:ax:aland:agriculture, asub:ax:aland:households, asub:ax:aland:industry, asub:ax:aland:public_sector, asub:ax:aland:services, asub:ax:aland:total, asub:ax:alands_elandelslag:agriculture, asub:ax:alands_elandelslag:households, asub:ax:alands_elandelslag:industry, asub:ax:alands_elandelslag:public_sector, asub:ax:alands_elandelslag:services, asub:ax:alands_elandelslag:total, asub:ax:export:total, asub:ax:mariehamns_energi:households, asub:ax:mariehamns_energi:industry, asub:ax:mariehamns_energi:public_sector, asub:ax:mariehamns_energi:services, asub:ax:mariehamns_energi:total | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1980-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 35 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 297000.0; 159 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: AX on every row | none | text | AX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 603 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The region and sector as ASUB names them in Swedish, not a pricing node | none | text | Export: Totalt, Landskommunerna (Ålands elandelslag): Hushåll, Landskommunerna (Ålands elandelslag): Industri, Landskommunerna (Ålands elandelslag): Jordbruk, Landskommunerna (Ålands elandelslag): Offentlig sektor, Landskommunerna (Ålands elandelslag): Service, Landskommunerna (Ålands elandelslag): Totalt, Mariehamn (Mariehamns Energi Ab): Hushåll, Mariehamn (Mariehamns Energi Ab): Industri, Mariehamn (Mariehamns Energi Ab): Offentlig sektor, Mariehamn (Mariehamns Energi Ab): Service, Mariehamn (Mariehamns Energi Ab): Totalt, Åland, totalt: Hushåll, Åland, totalt: Industri, Åland, totalt: Jordbruk, Åland, totalt: Offentlig sektor, Åland, totalt: Service, Åland, totalt: Totalt | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | asub_ax:MI010 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://pxweb.asub.ax/PXWeb/api/v1/sv/Statistik/MI/MI010.px | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T10:46:02Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 603 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `exports` | Aland's electricity exports in the year (the region export) | MWh | 8 | 2018-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `sales` | Electricity sold to the sector in the region in the year | MWh | 595 | 1980-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `bcrp_peru_electricity_monthly`

One Peruvian department's (or Peru's total) electricity production in one month, from the central bank's BCRPData (data from MINEM).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 6450.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; from 2005-01.
- **Revisions:** Rewritten whole as one snapshot by each run from the BCRPData answer; vintage is not filled.
- **Source:** bcrp_pe:bcrpdata_produccion_electricidad_departamento Banco Central de Reserva del Peru (BCRP), BCRPData, monthly series: Produccion de electricidad por departamento (RD13043DM to RD13067DM), source: Ministerio de Energia y Minas (MINEM)
- **Method note:** [`docs/methods/bcrp_peru_electricity_monthly.md`](../methods/bcrp_peru_electricity_monthly.md)
- **Cite as:** Banco Central de Reserva del Peru (BCRP). BCRPData monthly series: Produccion de electricidad por departamento (RD13043DM to RD13067DM; source MINEM). Via the Energy Research Warehouse (ERW), table `bcrp_peru_electricity_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: bcrp_pe:<department> or bcrp_pe:total | none | text | bcrp_pe:amazonas, bcrp_pe:ancash, bcrp_pe:apurimac, bcrp_pe:arequipa, bcrp_pe:ayacucho, bcrp_pe:cajamarca, bcrp_pe:cusco, bcrp_pe:huancavelica, bcrp_pe:huanuco, bcrp_pe:ica, bcrp_pe:junin, bcrp_pe:la_libertad, bcrp_pe:lambayeque, bcrp_pe:lima, bcrp_pe:loreto, bcrp_pe:madre_de_dios, bcrp_pe:moquegua, bcrp_pe:pasco, bcrp_pe:piura, bcrp_pe:puno, bcrp_pe:san_martin, bcrp_pe:tacna, bcrp_pe:total, bcrp_pe:tumbes, bcrp_pe:ucayali | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2005-01-01T00:00:00Z to 2026-06-01T00:00:00Z; 258 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 89.79 to 5789604.968; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: PE on every row, whatever the department | none | text | PE | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 6450 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: BCRP's name of the department, not a pricing node | none | text | Amazonas, Ancash, Apurímac, Arequipa, Ayacucho, Cajamarca, Cusco, Huancavelica, Huánuco, Ica, Junín, La Libertad, Lambayeque, Lima, Loreto, Madre de Dios, Moquegua, Pasco, Piura, Puno, San Martín, Tacna, Total, Tumbes, Ucayali | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | bcrp_pe:bcrpdata_produccion_electricidad_departamento | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/produccion-de-electricidad-por-departamento | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T00:53:45Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 6450 |
| `x_series_code` | BCRP's code of the series (RD13043DM to RD13067DM) | none | text | RD13043DM, RD13044DM, RD13045DM, RD13046DM, RD13047DM, RD13048DM, RD13049DM, RD13050DM, RD13051DM, RD13052DM, RD13053DM, RD13054DM, RD13055DM, RD13056DM, RD13057DM, RD13058DM, RD13059DM, RD13060DM, RD13061DM, RD13062DM, RD13063DM, RD13064DM, RD13065DM, RD13066DM, RD13067DM | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `production` | Electricity produced in the department in the month (BCRP's GWh times 1,000) | MWh | 6450 | 2005-01-01T00:00:00Z | 2026-06-01T00:00:00Z |

### `bcrp_peru_hydrocarbons_monthly`

Peru's production of crude oil, natural gas liquids or natural gas in one month, from the central bank's BCRPData (data from INEI and MINEM).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 960.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; from 2000-01.
- **Revisions:** Rewritten whole as one snapshot by each run from the BCRPData answer; vintage is not filled.
- **Source:** bcrp_pe:bcrpdata_produccion_hidrocarburos Banco Central de Reserva del Peru (BCRP), BCRPData, monthly series: Produccion minera e hidrocarburos (miles de unidades recuperables), Hidrocarburos (PN01882AM, PN01883AM, PN01884AM), sources: INEI and Ministerio de Energia y Minas (MINEM)
- **Method note:** [`docs/methods/bcrp_peru_hydrocarbons_monthly.md`](../methods/bcrp_peru_hydrocarbons_monthly.md)
- **Cite as:** Banco Central de Reserva del Peru (BCRP). BCRPData monthly series: Produccion minera e hidrocarburos, Hidrocarburos (PN01882AM, PN01883AM, PN01884AM; sources INEI and MINEM). Via the Energy Research Warehouse (ERW), table `bcrp_peru_hydrocarbons_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: bcrp_pe:crude_oil, bcrp_pe:natural_gas_liquids or bcrp_pe:natural_gas | none | text | bcrp_pe:crude_oil, bcrp_pe:natural_gas, bcrp_pe:natural_gas_liquids | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2000-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 320 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 80.233 to 50811.3255; 960 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf, kbbl | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: PE on every row | none | text | PE | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 960 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: BCRP's series name in Spanish, with its unit, not a pricing node | none | text | Hidrocarburos - Gas Natural (millones de pies cúbicos), Hidrocarburos - Líquidos de gas natural (miles de barriles), Hidrocarburos - Petróleo (miles de barriles) | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | bcrp_pe:bcrpdata_produccion_hidrocarburos | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/produccion-minera-e-hidrocarburos-miles-de-unidades-recuperables | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T00:59:38Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 960 |
| `x_series_code` | BCRP's code of the series (PN01882AM, PN01883AM, PN01884AM) | none | text | PN01882AM, PN01883AM, PN01884AM | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `production` | Production in the month: crude oil and natural gas liquids in thousand barrels, natural gas in million cubic feet | MMcf; kbbl | 960 | 2000-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `bfe_ch_electricity_wednesdays`

One Wednesday's value of one Swiss electricity balance item (generation by type, storage pumps, imports, exports, national consumption), from the Swiss Federal Office of Energy's weekly balance.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 11154.

- **Time:** ts_utc is the Wednesday's date at 00:00:00Z, a Swiss local day as the file gives it; freq P1D; the energy of that one day.
- **Revisions:** Merged by (entity, variable, ts_utc): each run's days replace the same days and older ones are kept; vintage is the file's Last-Modified.
- **Source:** bfe:ogd51 Swiss Federal Office of Energy (SFOE), ENSTAT: Wochenstatistik Elektrizitaetsbilanz (https://opendata.swiss/de/dataset/enstat-wochenstatistik-elektrizitatsbilanz-erzeugung-und-abgabe-elektrischer-energie-in-der-sch)
- **Method note:** [`docs/methods/bfe_ch_electricity_wednesdays.md`](../methods/bfe_ch_electricity_wednesdays.md)
- **Cite as:** Swiss Federal Office of Energy (SFOE). ENSTAT: Wochenstatistik Elektrizitaetsbilanz (weekly electricity balance, Wednesdays). Via the Energy Research Warehouse (ERW), table `bfe_ch_electricity_wednesdays`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: bfe_weekly:ch on every row | none | text | bfe_weekly:ch | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2003-01-01T00:00:00Z to 2026-06-24T00:00:00Z; 1222 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 5.0 to 330746.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: CH on every row | none | text | CH | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 11154 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: SFOE weekly balance (Wednesdays) and the file's column, not a pricing node | none | text | SFOE weekly balance (Wednesdays), Ausfuhr_GWh, SFOE weekly balance (Wednesdays), Einfuhr_GWh, SFOE weekly balance (Wednesdays), Erzeugung_andere_GWh, SFOE weekly balance (Wednesdays), Erzeugung_kernkraftwerk_GWh, SFOE weekly balance (Wednesdays), Erzeugung_laufwerk_GWh, SFOE weekly balance (Wednesdays), Erzeugung_netto_GWh, SFOE weekly balance (Wednesdays), Erzeugung_photovoltaik_GWh, SFOE weekly balance (Wednesdays), Erzeugung_speicherwerk_GWh, SFOE weekly balance (Wednesdays), Erzeugung_thermisch_GWh, SFOE weekly balance (Wednesdays), Erzeugung_windkraftwerk_GWh, SFOE weekly balance (Wednesdays), Landesverbrauch_GWh, SFOE weekly balance (Wednesdays), Verbrauch_speicherpumpen_GWh | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | bfe:ogd51 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.bfe-ogd.ch/ogd51/ogd51_wochenstatistik_elektrizitaetsbilanz.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T04:52:40Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's Last-Modified (UTC) | none | utc time | 2026-09-18T09:25:46Z | 0 |
| `x_column` | The file's column the value is read from (German, in GWh) | none | text | Ausfuhr_GWh, Einfuhr_GWh, Erzeugung_andere_GWh, Erzeugung_kernkraftwerk_GWh, Erzeugung_laufwerk_GWh, Erzeugung_netto_GWh, Erzeugung_photovoltaik_GWh, Erzeugung_speicherwerk_GWh, Erzeugung_thermisch_GWh, Erzeugung_windkraftwerk_GWh, Landesverbrauch_GWh, Verbrauch_speicherpumpen_GWh | 0 |
| `x_definition` | For the file's Erzeugung_netto only: less_pumps (generation less the storage pumps, through 2024) or before_pumps (generation before them, from 2025) | none | text | before_pumps, less_pumps | 9932: Empty on every column but Erzeugung_netto |

Variables (13):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `exports` | Exports on the day | MWh | 1222 | 2003-01-01T00:00:00Z | 2026-06-24T00:00:00Z |
| `generation_less_storage_pumps` | Generation less the storage pumps on the day (the file's Erzeugung_netto through 2024) | MWh | 1144 | 2003-01-01T00:00:00Z | 2024-12-25T00:00:00Z |
| `imports` | Imports on the day | MWh | 1222 | 2003-01-01T00:00:00Z | 2026-06-24T00:00:00Z |
| `national_consumption` | National consumption on the day | MWh | 1222 | 2003-01-01T00:00:00Z | 2026-06-24T00:00:00Z |
| `net_generation` | Generation before the storage pumps on the day (the file's Erzeugung_netto from 2025) | MWh | 78 | 2025-01-01T00:00:00Z | 2026-06-24T00:00:00Z |
| `nuclear` | Nuclear generation on the day | MWh | 1222 | 2003-01-01T00:00:00Z | 2026-06-24T00:00:00Z |
| `other` | Other generation on the day (before 2025 it includes thermal, wind and solar) | MWh | 1144 | 2003-01-01T00:00:00Z | 2024-12-25T00:00:00Z |
| `run_of_river` | Run-of-river hydro generation on the day | MWh | 1222 | 2003-01-01T00:00:00Z | 2026-06-24T00:00:00Z |
| `solar` | Photovoltaic generation on the day (a column of its own from 2025) | MWh | 78 | 2025-01-01T00:00:00Z | 2026-06-24T00:00:00Z |
| `storage_hydro` | Storage hydro generation on the day | MWh | 1222 | 2003-01-01T00:00:00Z | 2026-06-24T00:00:00Z |
| `storage_pumps` | Electricity used by the storage pumps on the day | MWh | 1222 | 2003-01-01T00:00:00Z | 2026-06-24T00:00:00Z |
| `thermal` | Thermal generation on the day (a column of its own from 2025) | MWh | 78 | 2025-01-01T00:00:00Z | 2026-06-24T00:00:00Z |
| `wind` | Wind generation on the day (a column of its own from 2025) | MWh | 78 | 2025-01-01T00:00:00Z | 2026-06-24T00:00:00Z |

### `bfe_switzerland_electricity_monthly`

One month's value of one item of Switzerland's electricity balance, from the Swiss Federal Office of Energy's monthly values.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 4000.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; from 2000-01.
- **Revisions:** Rewritten whole as one snapshot by each run from the saved file; vintage is the file's Last-Modified; provisional months carry x_final 0.
- **Source:** bfe:ogd35 Swiss Federal Office of Energy, ENSTAT: Elektrizitaetsbilanz der Schweiz - Monatswerte-CSV (https://opendata.swiss/en/dataset/enstat-elektrizitatsbilanz-der-schweiz-monatswerte-csv)
- **Method note:** [`docs/methods/bfe_switzerland_electricity_monthly.md`](../methods/bfe_switzerland_electricity_monthly.md)
- **Cite as:** Swiss Federal Office of Energy (SFOE). ENSTAT: Electricity balance of Switzerland, monthly values (CSV). Via the Energy Research Warehouse (ERW), table `bfe_switzerland_electricity_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: bfe:ch on every row | none | text | bfe:ch | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2000-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 320 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 7000.0 to 9323000.0; 2619 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: CH on every row | none | text | CH | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 4000 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: SFOE's column name in German, not a pricing node | none | text | Ausfuhr_GWh, Einfuhr_GWh, Endverbrauch_GWh, Erzeugung_Kernkraftwerk_GWh, Erzeugung_Laufwerk_GWh, Erzeugung_Photovoltaik_GWh, Erzeugung_Speicherwerk_GWh, Erzeugung_Thermische_GWh, Erzeugung_Windkraft_GWh, Erzeugung_andere_GWh, Erzeugung_netto_GWh, Landeserzeugung_GWh, Landesverbrauch_GWh, Verbrauch_Speicherpumpen_GWh, Verluste_GWh | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | bfe:ogd35 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.bfe-ogd.ch/ogd35/ogd35_schweizerische_elektrizitaetsbilanz_monatswerte.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T07:53:13Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's Last-Modified (UTC) | none | utc time | 2026-10-07T07:18:58Z | 0 |
| `x_final` | SFOE's Definitiv: 1 for a final month, 0 for a provisional one (the source's name: Definitiv) | none | integer | 0, 1 | 0 |

Variables (15):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `exports` | Exports (Ausfuhr) | MWh | 320 | 2000-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `final_consumption` | Final consumption (Endverbrauch) | MWh | 320 | 2000-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `imports` | Imports (Einfuhr) | MWh | 320 | 2000-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `losses` | Losses (Verluste) | MWh | 320 | 2000-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `national_consumption` | National consumption (Landesverbrauch) | MWh | 320 | 2000-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `national_generation` | National generation (Landeserzeugung) | MWh | 320 | 2000-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_generation` | Net generation (Erzeugung_netto) | MWh | 320 | 2000-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nuclear_generation` | Nuclear generation (Erzeugung_Kernkraftwerk) | MWh | 320 | 2000-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `other_generation` | Other generation (Erzeugung_andere) | MWh | 240 | 2000-01-01T00:00:00Z | 2019-12-01T00:00:00Z |
| `pumped_storage_consumption` | Electricity used by the storage pumps (Verbrauch_Speicherpumpen) | MWh | 320 | 2000-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `run_of_river_generation` | Run-of-river hydro generation (Erzeugung_Laufwerk) | MWh | 320 | 2000-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `solar_generation` | Photovoltaic generation (Erzeugung_Photovoltaik) | MWh | 80 | 2020-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `storage_hydro_generation` | Storage hydro generation (Erzeugung_Speicherwerk) | MWh | 320 | 2000-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `thermal_generation` | Thermal generation (Erzeugung_Thermische) | MWh | 80 | 2020-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `wind_generation` | Wind generation (Erzeugung_Windkraft) | MWh | 80 | 2020-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `blm_ca_renewable_rows`

One renewable energy right-of-way on public lands in California (verified or preliminary), from the Bureau of Land Management's California renewable energy projects layers.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 57.

- **Time:** No time column; status_date is the effective date; the table is a snapshot as read on its retrieved_at.
- **Revisions:** Rewritten whole as one snapshot by each run from BLM's two layers; vintage is not filled.
- **Source:** blm:ca_renewable_energy_projects U.S. Department of the Interior, Bureau of Land Management, California State Office, BLM CA Renewable Energy Projects (https://gis.blm.gov/caarcgis/rest/services/RenewableEnergy/BLM_CA_Renewable_Energy_Projects/FeatureServer)
- **Method note:** [`docs/methods/blm_ca_renewable_rows.md`](../methods/blm_ca_renewable_rows.md)
- **Cite as:** U.S. Department of the Interior, Bureau of Land Management (BLM). BLM CA Renewable Energy Projects (verified and preliminary renewable energy rights-of-way). Via the Energy Research Warehouse (ERW), table `blm_ca_renewable_rows`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: blm_row:<BLM serial number, spaces removed> | none | text | for example blm_row:CACA009501, blm_row:CACA009755, blm_row:CACA011688A; 57 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: project on every row | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it. Here: BLM's project name (the holder or applicant as BLM writes it) | none | text | for example Aero Power, LLC - Campo, Alta East X, LLC, Alta Windpower Dev. LLC - Alta 1; 55 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-CA on every row | none | text | US-CA | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 57 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 57 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: Not filled: BLM gives no capacity | MW | empty | no cell holds a value | 57 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: BLM's disposition is in x_disposition | none | empty | no cell holds a value | 57 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The right-of-way's effective date | none | date | 1982-12-08 to 2014-03-21; 32 distinct | 25 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 57 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | blm:ca_renewable_energy_projects | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://gis.blm.gov/caarcgis/rest/services/RenewableEnergy/BLM_CA_Renewable_Energy_Projects/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=false&f=json, https://gis.blm.gov/caarcgis/rest/services/RenewableEnergy/BLM_CA_Renewable_Energy_Projects/FeatureServer/1/query?where=1%3D1&outFields=*&returnGeometry=false&f=json | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T12:41:42Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 57 |
| `x_layer` | BLM's layer: verified (layer 0) or preliminary (layer 1) renewable energy rights-of-way | none | text | preliminary, verified | 0 |
| `x_serial_number` | BLM's serial number of the case | none | text | for example CACA 009501, CACA 009755, CACA 011688A; 57 distinct | 0 |
| `x_disposition` | BLM's disposition: Authorized, Pending or Closed (the source's name: Disposition) | none | text | Authorized, Closed, Pending | 0 |
| `x_case_type` | BLM's case type (ROW-SOLAR DEV FAC solar development, ROW-WIND DEV FAC wind development, ROW-WIND PROJ TEST wind testing) (the source's name: CaseType) | none | text | ROW-SOLAR DEV FAC, ROW-WIND DEV FAC, ROW-WIND PROJ TEST | 0 |
| `x_case_type_code` | BLM's code of the case type (the source's name: CaseTypeCode) | none | integer | 283002, 283003, 283103 | 0 |
| `x_commodity` | BLM's commodity (solar or wind energy facilities), as written (the source's name: Commodity) | none | text | SOLAR ENERGY FACILITIES, Solar Energy Facilities, Wind Energy Facilities | 0 |
| `x_project_type` | BLM's project type (CSP, PV, testing, turbines) (the source's name: ProjectType) | none | text | CSP, PV, testing, turbines | 3: BLM leaves the field blank |
| `x_application_date` | The application date (the source's name: ApplicationDate) | none | date | 1981-03-19 to 2016-05-23; 50 distinct | 2: BLM leaves the field blank |
| `x_effective_date` | The effective date (the source's name: EffectiveDate) | none | date | 1982-12-08 to 2014-03-21; 32 distinct | 25: BLM leaves the field blank |
| `x_expiration_date` | The expiration date (the source's name: ExpirationDate) | none | date | 2013-01-25, 2013-03-30, 2013-09-06, 2014-03-30, 2014-06-01, 2014-09-30, 2015-06-25, 2015-12-31, 2017-10-25, 2022-12-27, 2027-02-25, 2027-04-01, 2028-01-31, 2028-12-31, 2037-12-14, 2038-12-08, 2038-12-31, 2039-12-31, 2040-12-31, 2041-12-31, 2042-12-31, 2043-12-31 | 32: BLM leaves the field blank |
| `x_expiration_year` | The expiration year (the source's name: ExpirationYear) | none | integer | 2013, 2014, 2015, 2017, 2022, 2027, 2028, 2037, 2038, 2039, 2040, 2041, 2042, 2043 | 32: BLM leaves the field blank |
| `x_project_acres` | The project's acres (the source's name: ProjectAcres) | acre | integer | 20 to 30810; 36 distinct | 20: BLM leaves the field blank |
| `x_blm_acres` | The acres on BLM land (the source's name: BLMAcres) | acre | integer | 13 to 37219; 53 distinct | 3: BLM leaves the field blank |
| `x_data_source` | BLM's data source field as written (Application, LR2000, a map, a shapefile) (the source's name: DataSource) | none | text | A. Shaffer legals, App. Map, Application, Application Map, ApplicationM&B, LR2000, MTP Drawing, MTP map, legals, POD, Shapefile-company | 0 |
| `x_remarks` | BLM's remarks (the source's name: Remarks) | none | text | for example 5/28/10Deleted Sec26&27l;4/28/11enXcoverbal2 incl. samelands; Amended 8/11, 6.5 sections of LWCF land within project; within 29Palms Base expansionzone, Amended 1/15/2008; Amended via POD 2/2011; 42 distinct | 13: BLM leaves the field blank |
| `x_in_time` | not documented by the source (the source's name: InTime) | none | text | 1st | 0 |

Waiting for a second look: x_in_time (BLM's InTime, 1st on every row): what it marks is not written in the connector, the method note or the header. Read again on 20 November 2026 in the connector (it copies the field as served) and the method note: still not documented by the source. Read again on 20 November 2026 in the saved layer JSON under warehouse/raw/blm_renewable (its fields list gives InTime only its own name as alias, a string of length 5): not found..

### `blm_oil_gas_statistics_annual`

One state's value of one federal onshore oil and gas measure (leases, acreage, drilling permits, wells) for one federal fiscal year, from BLM's Oil and Gas Statistics.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 12500.

- **Time:** ts_utc is 1 October before the fiscal year at 00:00:00Z (FY 2025 begins 1 October 2024); freq P1Y.
- **Revisions:** Rewritten whole as one snapshot by each run from BLM's workbook; vintage is the workbook's Last-Modified.
- **Source:** blm:oil_gas_statistics U.S. Department of the Interior, Bureau of Land Management, Oil and Gas Statistics (https://www.blm.gov/programs/energy-and-minerals/oil-and-gas/oil-and-gas-statistics)
- **Method note:** [`docs/methods/blm_oil_gas_statistics_annual.md`](../methods/blm_oil_gas_statistics_annual.md)
- **Cite as:** U.S. Department of the Interior, Bureau of Land Management (BLM). Oil and Gas Statistics: All Federal Oil and Gas Statistics by Year by State (Tables 1 to 10). Via the Energy Research Warehouse (ERW), table `blm_oil_gas_statistics_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: blm_oil_gas:<state postal code, lower case> | none | text | for example blm_oil_gas:ak, blm_oil_gas:al, blm_oil_gas:ar; 50 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2000-10-01T00:00:00Z, 2001-10-01T00:00:00Z, 2002-10-01T00:00:00Z, 2003-10-01T00:00:00Z, 2004-10-01T00:00:00Z, 2005-10-01T00:00:00Z, 2006-10-01T00:00:00Z, 2007-10-01T00:00:00Z, 2008-10-01T00:00:00Z, 2009-10-01T00:00:00Z, 2010-10-01T00:00:00Z, 2011-10-01T00:00:00Z, 2012-10-01T00:00:00Z, 2013-10-01T00:00:00Z, 2014-10-01T00:00:00Z, 2015-10-01T00:00:00Z, 2016-10-01T00:00:00Z, 2017-10-01T00:00:00Z, 2018-10-01T00:00:00Z, 2019-10-01T00:00:00Z, 2020-10-01T00:00:00Z, 2021-10-01T00:00:00Z, 2022-10-01T00:00:00Z, 2023-10-01T00:00:00Z, 2024-10-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 15359523.0; 2821 distinct | 0 |
| `unit` | The unit of the row's value | none | text | acre, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> | none | text | for example US-AK, US-AL, US-AR; 50 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 12500 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The state as BLM names it, not a pricing node | none | text | for example Alabama, Alaska, Arizona; 50 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | blm:oil_gas_statistics | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.blm.gov/sites/default/files/docs/2026-04/All%20Fed%20O_G%20Statistics%20by%20Year%20by%20State_Web%20Stats_Tabs%20w%20Table%20Numbers_FY25.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T21:20:34Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's Last-Modified (UTC) | none | utc time | 2026-04-08T14:16:52Z | 0 |
| `x_fiscal_year` | The federal fiscal year (October to September) | none | integer | 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 | 0 |
| `x_table` | BLM's table the value is read from (Table 1 to Table 10) | none | text | Table 1, Table 10, Table 2, Table 3, Table 4, Table 5, Table 6, Table 7, Table 8, Table 9 | 0 |
| `x_as_of` | The date the workbook says its figures stand at | none | date | 2025-10-01 | 0 |

Variables (10):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `acres_newly_leased` | Acres newly leased during the fiscal year | acre | 1250 | 2000-10-01T00:00:00Z | 2024-10-01T00:00:00Z |
| `acres_under_lease` | Acres under federal lease on the fiscal year's last day | acre | 1250 | 2000-10-01T00:00:00Z | 2024-10-01T00:00:00Z |
| `apds_approved` | Applications for permit to drill approved during the fiscal year | count | 1250 | 2000-10-01T00:00:00Z | 2024-10-01T00:00:00Z |
| `leases_in_effect` | Federal oil and gas leases in effect on the fiscal year's last day | count | 1250 | 2000-10-01T00:00:00Z | 2024-10-01T00:00:00Z |
| `new_leases_issued` | New leases issued during the fiscal year | count | 1250 | 2000-10-01T00:00:00Z | 2024-10-01T00:00:00Z |
| `producible_service_completions` | Producible and service well completions on the fiscal year's last day | count | 1250 | 2000-10-01T00:00:00Z | 2024-10-01T00:00:00Z |
| `producible_service_well_bores` | Producible and service well bores on the fiscal year's last day | count | 1250 | 2000-10-01T00:00:00Z | 2024-10-01T00:00:00Z |
| `producing_acres` | Producing acres on the fiscal year's last day | acre | 1250 | 2000-10-01T00:00:00Z | 2024-10-01T00:00:00Z |
| `producing_leases` | Producing leases on the fiscal year's last day | count | 1250 | 2000-10-01T00:00:00Z | 2024-10-01T00:00:00Z |
| `wells_spud` | Wells spud (drilling started) during the fiscal year | count | 1250 | 2000-10-01T00:00:00Z | 2024-10-01T00:00:00Z |

### `bpa_ba_hourly`

One hour's value of the BPA balancing authority's load, generation by type or net interchange, the hour's mean of BPA's five-minute values.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 400261.

- **Time:** ts_utc is the hour's start (UTC); freq PT1H; files before 2022 in Pacific local time, put into UTC.
- **Revisions:** Rewritten whole as one snapshot by each run from BPA's yearly workbooks; vintage is each workbook's Last-Modified.
- **Source:** bpa:ba_load_generation Bonneville Power Administration, Transmission Services, VER and Balancing Authority Monitoring (https://transmission.bpa.gov/Business/Operations/Wind/default.aspx)
- **Method note:** [`docs/methods/bpa_ba_hourly.md`](../methods/bpa_ba_hourly.md)
- **Cite as:** Bonneville Power Administration (BPA). VER and Balancing Authority Monitoring: Total Load, Wind, Solar, Hydro, Thermal and Net Interchange (five-minute, yearly workbooks). Via the Energy Research Warehouse (ERW), table `bpa_ba_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: bpa:bpat on every row | none | text | bpa:bpat | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2020-01-01T08:00:00Z to 2026-10-23T06:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -2117.75 to 14914.5; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: the area spans states | none | empty | no cell holds a value | 400261 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 400261 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: BPA balancing authority on every row, not a pricing node | none | text | BPA balancing authority | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | bpa:ba_load_generation | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://transmission.bpa.gov/Business/Operations/Wind/OPITabularReports/WindGenTotalLoadYTD_2020.xls, https://transmission.bpa.gov/Business/Operations/Wind/OPITabularReports/WindGenTotalLoadYTD_2021.xls, https://transmission.bpa.gov/Business/Operations/Wind/OPITabularReports/WindGenTotalLoadYTD_2022.xlsx, https://transmission.bpa.gov/Business/Operations/Wind/OPITabularReports/WindGenTotalLoadYTD_2023.xlsx, https://transmission.bpa.gov/Business/Operations/Wind/OPITabularReports/WindGenTotalLoadYTD_2024.xlsx, https://transmission.bpa.gov/Business/Operations/Wind/OPITabularReports/WindGenTotalLoadYTD_2025.xlsx, https://transmission.bpa.gov/Business/Operations/Wind/OPITabularReports/WindGenTotalLoadYTD_2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T23:26:21Z, 2026-10-23T23:26:48Z, 2026-10-23T23:27:11Z, 2026-10-23T23:27:17Z, 2026-10-23T23:27:20Z, 2026-10-23T23:27:23Z, 2026-10-23T23:27:26Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The year's workbook's Last-Modified (UTC) | none | utc time | 2021-11-01T08:40:13Z, 2022-01-28T09:40:03Z, 2024-05-12T08:40:19Z, 2024-05-14T08:40:18Z, 2025-10-30T08:40:21Z, 2026-01-01T09:40:20Z, 2026-10-23T08:40:16Z | 0 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48). Here: bpat on every row | none | text | bpat | 0 |
| `x_intervals` | How many five-minute values the hour holds (12 in a full hour) | count | integer | 10, 11, 12, 4, 5, 7 | 0 |
| `x_format` | The file's format: new (BPA's UTC column, 2022 on) or old (Pacific local time, 2021 and before) | none | text | new, old | 0 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `hydro_generation` | Hydro generation | MW | 59686 | 2020-01-01T08:00:00Z | 2026-10-23T06:00:00Z |
| `load` | The balancing authority's load | MW | 59687 | 2020-01-01T08:00:00Z | 2026-10-23T06:00:00Z |
| `net_interchange` | Net interchange, positive an export | MW | 59687 | 2020-01-01T08:00:00Z | 2026-10-23T06:00:00Z |
| `nuclear_generation` | Nuclear generation | MW | 59687 | 2020-01-01T08:00:00Z | 2026-10-23T06:00:00Z |
| `solar_generation` | Solar generation (2022 on) | MW | 42142 | 2022-01-01T08:00:00Z | 2026-10-23T06:00:00Z |
| `thermal_generation` | Thermal generation (BPA's fossil and biomass) | MW | 59686 | 2020-01-01T08:00:00Z | 2026-10-23T06:00:00Z |
| `wind_generation` | Wind generation | MW | 59686 | 2020-01-01T08:00:00Z | 2026-10-23T06:00:00Z |

### `bsee_offshore_incidents`

One incident on the US outer continental shelf reported to the Bureau of Safety and Environmental Enforcement, from its calendar-year workbooks.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 4818.

- **Time:** event_date is the incident's date; x_time its time as BSEE writes it.
- **Revisions:** Rewritten whole as one snapshot by each run from BSEE's workbooks; the table has no vintage column.
- **Source:** bsee:offshore_incidents Bureau of Safety and Environmental Enforcement, Offshore Incident Statistics (https://www.bsee.gov/stats-facts/offshore-incident-statistics)
- **Method note:** [`docs/methods/bsee_offshore_incidents.md`](../methods/bsee_offshore_incidents.md)
- **Cite as:** U.S. Department of the Interior, Bureau of Safety and Environmental Enforcement (BSEE). Offshore Incident Statistics: incidents for public use, by calendar year. Via the Energy Research Warehouse (ERW), table `bsee_offshore_incidents`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: bsee_incident:<serial> | none | text | for example bsee_incident:-25871, bsee_incident:-25874, bsee_incident:-25878; 4818 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2018-01-02 to 2024-12-31; 1921 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: offshore_incident on every row | none | text | offshore_incident | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: The operator | none | text | for example ANKOR Energy LLC, Anadarko Petroleum Corporation, Apache Corporation; 95 distinct | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons. Here: lease:<number> | none | text | for example lease:00016, lease:00019, lease:00020; 683 distinct | 606 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 4818 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 4818 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 4818 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 4818 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | bsee:offshore_incidents | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.bsee.gov/sites/bsee.gov/files/2023-03/cy-2021-excel-spreadsheet.xlsx, https://www.bsee.gov/sites/bsee.gov/files/2024-02/cy-2022-excel-spreadsheet.xlsx, https://www.bsee.gov/sites/bsee.gov/files/2024-10/cy-2023-excel-spreadsheet.xlsx, https://www.bsee.gov/sites/bsee.gov/files/2026-04/cy-2024-excel-spreadsheet.xlsx, https://www.bsee.gov/sites/bsee.gov/files/cy-2020-offshore-incident-statistics-excel-spreadsheet.xlsx, https://www.bsee.gov/sites/bsee.gov/files/cy2018-public-release-01-17-2020.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T00:54:22Z, 2026-10-24T00:59:41Z, 2026-10-24T01:00:04Z, 2026-10-24T01:00:05Z, 2026-10-24T01:00:07Z, 2026-10-24T01:00:09Z | 0 |
| `x_year` | The workbook's calendar year (the year of event_date) | none | integer | 2018, 2020, 2021, 2022, 2023, 2024 | 0 |
| `x_time` | The incident's time as BSEE writes it, a 24-hour hhmm number without leading zeros (the source's name: Time) | none | integer | 0 to 2359; 718 distinct | 0 |
| `x_region` | BSEE's OCS region as written (Gulf of Mexico, Gulf of America from 2024, Pacific, Alaska) (the source's name: OCS Region) | none | text | Alaska, Gulf of America, Gulf of Mexico, Pacific | 0 |
| `x_district` | BSEE's district name (the source's name: District Name) | none | text | Anchorage District, California, California District, Houma District, Lafayette District, Lake Charles District, Lake Jackson District, New Orleans District, Santa Maria District | 1: BSEE leaves the cell blank (one row) |
| `x_area` | The offshore area's name (the source's name: Area Name) | none | text | for example Alaminos Canyon, Atwater Valley, BAY MARCHAND AREA; 66 distinct | 59: BSEE leaves the cell blank (2022 and 2023) |
| `x_block` | The offshore block (the source's name: Block) | none | text | for example 10, 100, 1000; 495 distinct | 1: BSEE leaves the cell blank |
| `x_water_depth_ft` | The water depth, as BSEE gives it (the source's name: Water Depth (feet)) | ft | integer | 5 to 60817; 726 distinct | 104: BSEE leaves the cell blank |
| `x_structure` | The structure's name (the source's name: Structure Name) | none | text | for example "A" Sump, #5, #8; 290 distinct | 1404: BSEE leaves the cell blank |
| `x_structure_type` | The structure's type as written (fixed platform, caisson, FPSO, tension leg platform and others) (the source's name: Structure Type) | none | text | CAIS, CT, Caisson, Compliant Tower, FIXED, FPSO, Fixed Leg Platform, Floating Production, Storage, And Offloading, MOPU, MTLP, Mini Tension Leg Platform, Mobile Production Unit, SEMI, SPAR, Semi Submersible (Column Stabilized Unit) Floating Production System, Spar Platform - Floating Production System, TLP, Tension Leg Platform, WP | 1404: BSEE leaves the cell blank |
| `x_rig` | The rig's name (the source's name: Rig Name) | none | text | for example * BARGE RIG TO BE DETERMINED, * BARGE TO BE DETERMINED, * COIL TUBING UNIT; 104 distinct | 3267: BSEE leaves the cell blank |
| `x_fatalities` | Fatalities, every fatality column summed (operator and contractor) | count | integer | 0, 1 | 0 |
| `x_injuries` | Injuries, every injury column summed (operator and contractor, each injury class) | count | integer | 0, 1, 2 | 0 |
| `x_fire` | Y when the incident involved a fire, else N (the source's name: Fire) | none | text | N, Y | 0 |
| `x_explosion` | Y when the incident involved an explosion, else N (the source's name: Explosion) | none | text | N, Y | 0 |
| `x_loss_of_well_control` | Y when the incident involved a loss of well control (any of BSEE's four kinds), else N | none | text | N, Y | 0 |
| `x_collision` | Y when the incident involved a collision (major or minor), else N | none | text | N, Y | 0 |
| `x_lifting` | Y when the incident involved a crane or other lifting device, else N | none | text | N, Y | 0 |
| `x_gas_release` | Y when the incident involved a reportable H2S release or a shut-down gas release, else N | none | text | N, Y | 0 |
| `x_summary` | BSEE's summary of the incident in its own words, spaces run together (the source's name: Incident Summary) | none | text | for example "06.27.2024: [REDACTED_NAME], As per 30 CFR 250.190, Talos Third Coast LLC respectfully submits the final investigation report as a follow up to the initial submittal of a crane / material handling incident at the MP-138G (G16500) facility on 06.14.2024 at 12:45 hours. After reviewing the report and corrective actions, if further clarification is necessary, Talos Operations and HSE can schedule a call into the New Orleans District office at the district's convenience. Total Cost: $200.00 USD, repair light fixture wiring and replace safety cage. 06.14.2024 As required by 30 CFR 250.188(a)(8), Talos Third Coast LLC submits the initial notification of a crane / material handling incident that occurred on MP-138G (G16500) at 12:45hours on 06/14/2024. Incident Description: While operating the crane on a blind lift from boat to production deck, crane operator bumped light fixture with tool box load breaking the coupling and casing light to fall. No personnel were injured in the incident. Talos Third Coast LLC. will provide a written follow up report upon completion of the incident investigation as required by 30 CFR 250.190. ", "This is initial and final report." Event During backloading operations, the handrail of a gangway contacted a suspended 550-gallon tote tank of engine oil. Event Description - Sequence / Timeline On February 8, 2023, backloading operations were underway utilizing Drill side crane of the EI 314 A Facility. . At approximately 08:00HRS; the marine vessel (M/V) Wildcat transitioned from EI 314 A Production side, under crane, to the Drill side crane. . During the transition the rigger attached the hook of the Drill side crane to a full 550-gallon tote tank of engine oil. . The crane operator then hoisted the tote tank and positioned it over the water awaiting the M/V to move into position to receive it. . While the load was held in position the M/V began to reverse toward the platform and under the load. . Once in position to receive the load the M/V was exposed to side sea conditions which swayed the vessel up during side-to-side (transverse axis) movements. . At that time, the bottom of the tote tank encountered one of the handrails of a gangway. . As the boat leveled to its original elevation, the crane operator lifted the load slightly then swung the tote tank to the left, away from the gangway and then lowered the tote tank to the deck of the M/V. . Once backloading operations were complete the crane operator reported the event to the Person-in-Charge (PIC) on the platform and then the Field Foreman and AOL's incident reporting requirements were initiated which included reporting the incident to the Field Foreman, Production Forman, and HSE Coordinator for investigation. Event Consequences 1. Gangway handrail was bent downward, and a weld was broken on the base of a socket which connects the handrail to the walking plank. There were no environmental impacts, or injuries to personnel because of this event. Reference Final Report Attachment., "This is initial and final report."_x000D_ _x000D_ Event: _x000D_ A production operator noticed a cotton cloth/rag smoldering inside of a wheelbarrow that included filtration media material and used paint that was curing for non-hazardous disposal._x000D_ _x000D_ Event Description - Sequence / Timeline:_x000D_ 15:25HRS 05/14/2022 EI 314 C a facility stop-work was initiated when a production operator identified a smoldering cotton cloth/rag inside of a wheelbarrow designated as a collection pan for paint operations waste. The operator immediately reacted with water to saturate the rag and other items from any further stage of reaction._x000D_ _x000D_ 15:30HRS A safety stand-down meeting was conducted, and production and paint operations personnel were in attendance to review the finding and establish a plan forward._x000D_ _x000D_ 17:00HRS Ultimate-work-authority (UWA) approved resumption of painting operations._x000D_ _x000D_ 08:00HRS 05/15/2022 A Microsoft Teams meeting was organized by Facilities Maintenance Management and representatives of current AOL painting operations in various contractor roles were in attendance. During the meeting the event was reviewed, and discussions of prevention were communicated to all affected and unaffected painting crews so that everyone was aware of the expectation for reviewing and referencing safety data sheets, various risk affiliated with chemicals that contain reactive properties, and onsite management planning and control._x000D_ _x000D_ Event Consequences:_x000D_ All facility operations were halted for investigation and a safety stand-down meeting was conducted to review the smoldering cloth/rag finding and identify a safe path forward._x000D_ _x000D_ Emergency muster actions did not occur and there was no injury, property damage or environmental impact because of this event._x000D_; 4788 distinct | 11: BSEE leaves the cell blank (11 rows of 2021) |

### `caiso_tie_flows_5min`

The net Western Energy Imbalance Market transfer between one pair of balancing areas in one five-minute interval of CAISO's real-time dispatch.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. A pair has rows on a day only if it had a transfer that was not zero that day.. License: public; tier: source. Rows read on 2026-11-20: 569820.

- **Time:** ts_utc is the five minutes' start in UTC.
- **Revisions:** A rolling 35 days; days already held are not asked again, and days older than the window are dropped at each run. vintage is not filled.
- **Source:** caiso:ENE_EIM_TRANSFER_TIE California Independent System Operator (CAISO), OASIS EIM Transfer by Tie, real-time dispatch (RTD), five minutes (https://oasis.caiso.com/mrioasis/logon.do)
- **Method note:** [`docs/methods/caiso_tie_flows.md`](../methods/caiso_tie_flows.md)
- **Cite as:** CAISO. Via the Energy Research Warehouse (ERW), table `caiso_tie_flows_5min`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example caiso:AVA-AVRN, caiso:AVA-BPAT, caiso:AVA-IPCO; 68 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-10-16T07:00:00Z to 2026-11-19T07:55:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -2001.95 to 1795.51; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT5M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA,US-NV,US-AZ,US-OR,US-WA,US-ID,US-UT,US-WY,US-MT,US-NM | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_rtd | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 569820 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:ENE_EIM_TRANSFER_TIE | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=ENE_EIM_TRANSFER_TIE&version=4&baa_grp_id=ALL&market_run_id=RTD&startdatetime=20261016T07:00-0000&enddatetime=20261017T07:00-0000, https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=ENE_EIM_TRANSFER_TIE&version=4&baa_grp_id=ALL&market_run_id=RTD&startdatetime=20261017T07:00-0000&enddatetime=20261018T07:00-0000, https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=ENE_EIM_TRANSFER_TIE&version=4&baa_grp_id=ALL&market_run_id=RTD&startdatetime=20261019T07:00-0000&enddatetime=20261020T07:00-0000; 32 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-20T11:15:10Z to 2026-11-20T11:22:41Z; 32 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 569820 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `transfer_mw_net` | The pair's tie transfers from the first area to the second less those back, MW (positive, the first sends to the second); scheduled transfers, not metered flows | MW | 569820 | 2026-10-16T07:00:00Z | 2026-11-19T07:55:00Z |

### `carb_auction_allowance_prices`

One cap-and-trade auction's (California, joint with Quebec) value of one result for its current-vintage or advance-vintage allowances.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 336.

- **Time:** ts_utc is the first day of the auction month at 00:00:00Z (the summary gives no day); freq P3M.
- **Revisions:** Merged by (entity, variable, ts_utc); each run reads the whole summary and replaces every row; vintage is not filled.
- **Source:** carb:auction-results-summary California Air Resources Board, Summary of Joint Auction Settlement Prices and Results (PDF, Last updated August 2026; linked from https://ww2.arb.ca.gov/our-work/programs/cap-and-trade-program/auction-information) (https://ww2.arb.ca.gov/sites/default/files/2020-08/results_summary.pdf)
- **Method note:** [`docs/methods/carb_auction_allowance_prices.md`](../methods/carb_auction_allowance_prices.md)
- **Cite as:** California Air Resources Board (CARB). Summary of California and Joint Auction Settlement Prices and Results. Via the Energy Research Warehouse (ERW), table `carb_auction_allowance_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: carb:current_auction (the current-vintage allowances sold at the auction) or carb:advance_auction (the advance-vintage allowances) | none | text | carb:advance_auction, carb:current_auction | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2012-11-01T00:00:00Z to 2026-08-01T00:00:00Z; 56 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 10.0 to 98215920.0; 189 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/tCO2, count | 0 |
| `freq` | How long the interval of the row is | none | text | P3M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 336 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The auction as CARB numbers it (Auction #1 to #8, Joint Auction #1 to #48), not a pricing node | none | text | for example Auction #1, Auction #2, Auction #3; 56 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | carb:auction-results-summary | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ww2.arb.ca.gov/sites/default/files/2020-08/results_summary.pdf | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T17:37:37Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 336 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `allowances_offered` | Allowances offered at the auction (one allowance is one metric ton of CO2 equivalent) | count | 112 | 2012-11-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `allowances_sold` | Allowances sold at the auction | count | 112 | 2012-11-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `settlement_price` | The auction's settlement price, USD per metric ton of CO2 equivalent | USD/tCO2 | 112 | 2012-11-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `carb_lcfs_credit_prices`

One week's value of one Low Carbon Fuel Standard credit measure, as the California Air Resources Board publishes it.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1145.

- **Time:** ts_utc is the Monday of the week (Monday to Sunday) at 00:00:00Z; freq P1W.
- **Revisions:** Rewritten whole by each run (the whole history from 2019 is read each run, so revisions are picked up); vintage is not filled.
- **Source:** carb:lcfs_weekly_credit_price California Air Resources Board, Weekly LCFS Credit Transfer Activity Report, weekly average credit price (https://ww2.arb.ca.gov/resources/documents/weekly-lcfs-credit-transfer-activity-reports)
- **Method note:** [`docs/methods/carb_lcfs_credit_prices.md`](../methods/carb_lcfs_credit_prices.md)
- **Cite as:** California Air Resources Board (CARB). Weekly LCFS Credit Transfer Activity Report, weekly average credit price. Via the Energy Research Warehouse (ERW), table `carb_lcfs_credit_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: carb:lcfs_credit on every row | none | text | carb:lcfs_credit | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-07T00:00:00Z to 2026-11-02T00:00:00Z; 409 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 41.29 to 6039846.0; 1105 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/tCO2, tCO2 | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1145 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: LCFS credit on every row, not a pricing node | none | text | LCFS credit | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | carb:lcfs_weekly_credit_price | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ww2.arb.ca.gov/sites/default/files/2026-11/Weekly%20LCFS%20Credit%20Activity%20%28upto%208%20Nov%2C%202026%29.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-15T17:49:36Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1145 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `credit_price_type1_weekly_avg` | Volume-weighted average price of the week's non-zero Type 1 credit transfers (executed within 10 days of the agreement), USD per credit (one metric ton of CO2 equivalent) | USD/tCO2 | 368 | 2019-10-21T00:00:00Z | 2026-11-02T00:00:00Z |
| `credit_price_weekly_avg` | Volume-weighted average price of all the week's non-zero credit transfers, USD per credit (one metric ton of CO2 equivalent) | USD/tCO2 | 409 | 2019-01-07T00:00:00Z | 2026-11-02T00:00:00Z |
| `credit_volume` | Credits transferred in the week | tCO2 | 368 | 2019-10-21T00:00:00Z | 2026-11-02T00:00:00Z |

### `cbs_curacao_electricity_annual`

Curacao's electricity production by Aqualectra in one year, from the Central Bureau of Statistics Curacao.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3.

- **Time:** ts_utc is the year's first day at 00:00:00Z; freq P1Y.
- **Revisions:** Rewritten whole as one snapshot by each run from the saved page; vintage is not filled.
- **Source:** cbs_cw:manufacturing_electricity_production Central Bureau of Statistics Curacao (CBS Curacao), Manufacturing: electricity production (source: Curacao Water and Power Company, Aqualectra)
- **Method note:** [`docs/methods/cbs_curacao_electricity_annual.md`](../methods/cbs_curacao_electricity_annual.md)
- **Cite as:** Central Bureau of Statistics Curacao (CBS). Manufacturing: electricity production (source Aqualectra). Via the Energy Research Warehouse (ERW), table `cbs_curacao_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: cbs_cw:aqualectra on every row | none | text | cbs_cw:aqualectra | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 866900.0, 916300.0, 982800.0 | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: CW on every row | none | text | CW | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: CBS's label, not a pricing node | none | text | Electricity Production (mln kWh) | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | cbs_cw:manufacturing_electricity_production | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.cbs.cw/manufacturing-0 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T03:36:57Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `production` | Electricity produced by Aqualectra in the year (CBS's million kWh times 1,000) | MWh | 3 | 2022-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `cbs_netherlands_electricity_monthly`

One month's value of one measure of the Netherlands' electricity balance (production by source, own use, imports and exports by country, losses, net consumption), from Statistics Netherlands table 84575NED.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 8880.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; from 1976-01.
- **Revisions:** Rewritten whole as one snapshot by each run from CBS's table; vintage is the file's Last-Modified; x_status gives the period's status.
- **Source:** cbs:84575NED Statistics Netherlands (CBS), table 84575NED (https://dataportal.cbs.nl/detail/CBS/84575NED)
- **Method note:** [`docs/methods/cbs_netherlands_electricity_monthly.md`](../methods/cbs_netherlands_electricity_monthly.md)
- **Cite as:** Statistics Netherlands (CBS). Table 84575NED: Elektriciteitsbalans; aanbod en verbruik. Via the Energy Research Warehouse (ERW), table `cbs_netherlands_electricity_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: cbs:nl on every row | none | text | cbs:nl | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1976-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 607 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 14256000.0; 3579 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: NL on every row | none | text | NL | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 8880 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: CBS's Dutch title of the measure, not a pricing node | none | text | Aardgas, België, Biomassa, Brandstoffen, totaal, Bruto productie, Denemarken, Distributieverliezen, Duitsland, Eigen verbruik bij elektr.productie, Invoer, totaal, Kernenergie, Kolen, Netto productie, totaal, Netto verbruik (berekend), Noorwegen, Olieproducten, Overige brandstoffen (niet-hernieuwbaar), Overige bronnen, Uitvoer, totaal, Verenigd Koninkrijk, Waterkracht, Windenergie op land, Windenergie op zee, Windenergie, totaal, Zonnestroom | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | cbs:84575NED | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://datasets.cbs.nl/csv/CBS/nl/84575NED | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T02:51:52Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's Last-Modified (UTC) | none | utc time | 2026-09-29T18:03:10Z | 0 |
| `x_measure` | CBS's code of the measure (the source's name: Measure) | none | text | for example D004599, E006479, E006560; 30 distinct | 0 |
| `x_status` | The period's status in CBS's period codes: Definitief (final), NaderVoorlopig (revised provisional), Voorlopig (provisional) | none | text | Definitief, NaderVoorlopig, Voorlopig | 0 |

Variables (30):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `distribution_losses` | Distribution losses | MWh | 607 | 1976-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `export` | Exports, total | MWh | 607 | 1976-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `export_belgium` | Exports to Belgium | MWh | 376 | 1982-08-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `export_denmark` | Exports to Denmark | MWh | 91 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `export_germany` | Exports to Germany | MWh | 376 | 1982-08-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `export_norway` | Exports to Norway | MWh | 219 | 2008-05-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `export_united_kingdom` | Exports to the United Kingdom | MWh | 183 | 2011-05-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `gross_production` | Gross electricity production | MWh | 607 | 1976-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `import` | Imports, total | MWh | 607 | 1976-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `import_belgium` | Imports from Belgium | MWh | 340 | 1976-02-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `import_denmark` | Imports from Denmark | MWh | 91 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `import_germany` | Imports from Germany | MWh | 340 | 1976-02-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `import_norway` | Imports from Norway | MWh | 219 | 2008-05-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `import_united_kingdom` | Imports from the United Kingdom | MWh | 183 | 2011-05-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_biomass` | Net production from biomass | MWh | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_coal` | Net production from coal | MWh | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_consumption` | Net electricity consumption | MWh | 607 | 1976-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_fuels` | Net production from fuels, total | MWh | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_hydro` | Net production from hydro power | MWh | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_natural_gas` | Net production from natural gas | MWh | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_nuclear` | Net production from nuclear energy | MWh | 134 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_oil_products` | Net production from oil products | MWh | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_other_fuels` | Net production from other fuels | MWh | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_other_sources` | Net production from other sources | MWh | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_production` | Net electricity production, total | MWh | 607 | 1976-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_solar` | Net production from solar | MWh | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_wind` | Net production from wind, total | MWh | 295 | 2002-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_wind_offshore` | Net production from offshore wind | MWh | 238 | 2006-10-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_wind_onshore` | Net production from onshore wind | MWh | 295 | 2002-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `own_use` | Own use at electricity production | MWh | 607 | 1976-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `cec_total_system_generation_annual`

One year's California in-state generation, or imports from the Northwest or Southwest, from one fuel, or the total system power by fuel, from the California Energy Commission.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 795.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z; freq P1Y; 2009 to 2025.
- **Revisions:** Rewritten whole as one snapshot by each run from the Commission's workbook; vintage is the workbook's Last-Modified.
- **Source:** cec:total_system_electric_generation California Energy Commission, Energy Almanac, Total System Electric Generation (https://www.energy.ca.gov/media/7311)
- **Method note:** [`docs/methods/cec_total_system_generation_annual.md`](../methods/cec_total_system_generation_annual.md)
- **Cite as:** California Energy Commission (CEC). Total System Electric Generation (Energy Almanac), the workbook of all years with totals. Via the Energy Research Warehouse (ERW), table `cec_total_system_generation_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: cec_tsp:<california, northwest, southwest or total>:<fuel> | none | text | for example cec_tsp:california:biomass, cec_tsp:california:coal, cec_tsp:california:geothermal; 47 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 132157000.0; 655 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-CA on every row, imports included | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 795 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The region and fuel as the workbook names them, not a pricing node | none | text | for example California: Biomass, California: Coal, California: Geothermal; 47 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | cec:total_system_electric_generation | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.energy.ca.gov/sites/default/files/2026-10/Total_System_Electric_Generation_2009-2025_with_totals_ada.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T21:44:27Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's Last-Modified (UTC) | none | utc time | 2026-10-07T22:24:36Z | 0 |
| `x_region` | The region of the block: california (in-state), northwest or southwest (imports), total (total system power) | none | text | california, northwest, southwest, total | 0 |
| `x_fuel` | The fuel as a slug; in the total block oil is combined with other (oil_other) and unspecified imports are unspecified | none | text | biomass, coal, geothermal, large_hydro, natural_gas, nuclear, oil, oil_other, other, small_hydro, solar, unspecified, unspecified_imports, wind | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `imports` | The Commission's estimate of the energy delivered to California from the region, by the generator's fuel (unspecified: source not traced) | MWh | 404 | 2009-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `in_state_generation` | California's in-state generation from the fuel in the year | MWh | 204 | 2009-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_system_power` | California's total system power from the fuel: in-state generation plus imports | MWh | 187 | 2009-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `censtatd_hk_electricity`

One month's value of Hong Kong's electricity consumption by type of user (or exports to the Mainland), or one quarter's value of its generation, imports, exports, own use and losses, from the Census and Statistics Department.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3699.

- **Time:** ts_utc is the period's first day at 00:00:00Z; freq P1M (table 915-91201) or P3M (table 915-91203).
- **Revisions:** Merged by (entity, variable, ts_utc): each run's periods replace the same periods and older ones are kept; vintage is not filled.
- **Source:** censtatd:hong_kong_energy_statistics Census and Statistics Department, Hong Kong Energy Statistics, tables 915-91201 and 915-91203 (figures from CLP Power and HK Electric), listed on DATA.GOV.HK (https://data.gov.hk/en-data/dataset/hk-censtatd-tablechart-915-91201)
- **Method note:** [`docs/methods/censtatd_hk_electricity.md`](../methods/censtatd_hk_electricity.md)
- **Cite as:** Census and Statistics Department, Hong Kong (C&SD). Hong Kong Energy Statistics, tables 915-91201 (monthly consumption of electricity by type of user) and 915-91203 (electricity production, imports, exports and consumption). Via the Energy Research Warehouse (ERW), table `censtatd_hk_electricity`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: censtatd:915-91201 (monthly consumption table) or censtatd:915-91203 (quarterly supply table), the C&SD table, not a place | none | text | censtatd:915-91201, censtatd:915-91203 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1979-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 572 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 14362222.222222222; 2630 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is. Here: P1M for table 915-91201, P3M for table 915-91203 | none | text | P1M, P3M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: HK on every row | none | text | HK | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3699 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Hong Kong on every row, not a pricing node | none | text | Hong Kong | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | censtatd:hong_kong_energy_statistics | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.censtatd.gov.hk/api/get.php?id=915-91201&lang=en&full_series=1, https://www.censtatd.gov.hk/api/get.php?id=915-91203&lang=en&full_series=1 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T06:44:04Z, 2026-10-24T06:44:05Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3699 |

Variables (10):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption_commercial` | Electricity consumption by commercial users | MWh | 572 | 1979-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `consumption_domestic` | Electricity consumption by domestic users | MWh | 572 | 1979-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `consumption_industrial` | Electricity consumption by industrial users | MWh | 572 | 1979-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `consumption_street_lighting` | Electricity consumption by street lighting | MWh | 572 | 1979-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `consumption_total` | Electricity consumption, all users (C&SD's terajoules converted) | MWh | 572 | 1979-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `exports_mainland` | Electricity exported to the Chinese Mainland | MWh | 623 | 1979-04-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `imports_mainland` | Electricity imported from the Chinese Mainland | MWh | 54 | 2013-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `industry_own_use_and_losses` | The power companies' own use and losses | MWh | 54 | 2013-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `local_consumption` | Local consumption (excluding the power companies' own use, losses and exports to the Mainland) | MWh | 54 | 2013-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `local_generation` | Local electricity generation | MWh | 54 | 2013-01-01T00:00:00Z | 2026-04-01T00:00:00Z |

### `cftc_cot_positions`

One NYMEX futures contract's value of one Commitments of Traders measure for one report week.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 9888.

- **Time:** ts_utc is the report's as-of date (a Tuesday, or the Monday the CFTC gives in a holiday week) at 00:00:00Z; the CFTC publishes it the Friday after; freq P1W.
- **Revisions:** Rewritten whole by each run (the old file removed first); vintage is not filled.
- **Source:** cftc:disaggregated_cot_futures Commodity Futures Trading Commission, Commitments of Traders, Disaggregated report, futures only (https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm)
- **Method note:** [`docs/methods/cftc_cot_positions.md`](../methods/cftc_cot_positions.md)
- **Cite as:** Commodity Futures Trading Commission (CFTC). Commitments of Traders, Disaggregated report, futures only. Via the Energy Research Warehouse (ERW), table `cftc_cot_positions`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: cftc:<CFTC contract market code>: 067651 WTI crude oil, 06765T Brent Last Day, 023651 Henry Hub natural gas, 111659 RBOB gasoline | none | text | cftc:023651, cftc:067651, cftc:06765T, cftc:111659 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-06T00:00:00Z to 2026-11-03T00:00:00Z; 618 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -331548.0 to 2706454.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: nymex on every row | none | text | nymex | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The CFTC's market name as printed (its wording changes over the years) | none | text | BRENT CRUDE OIL LAST DAY - NEW YORK MERCANTILE EXCHANGE, BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE, CRUDE OIL, LIGHT SWEET - NEW YORK MERCANTILE EXCHANGE, GASOLINE BLENDSTOCK (RBOB)  - NEW YORK MERCANTILE EXCHANGE, GASOLINE BLENDSTOCK (RBOB) - NEW YORK MERCANTILE EXCHANGE, GASOLINE RBOB - NEW YORK MERCANTILE EXCHANGE, NAT GAS NYME - NEW YORK MERCANTILE EXCHANGE, NATURAL GAS - NEW YORK MERCANTILE EXCHANGE, WTI-PHYSICAL - NEW YORK MERCANTILE EXCHANGE | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | cftc:disaggregated_cot_futures | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://publicreporting.cftc.gov/resource/72hh-3qpy.json?cftc_contract_market_code=023651&%24where=report_date_as_yyyy_mm_dd+%3E%3D+%272015-01-01T00%3A00%3A00%27&%24order=report_date_as_yyyy_mm_dd+ASC&%24limit=5000, https://publicreporting.cftc.gov/resource/72hh-3qpy.json?cftc_contract_market_code=067651&%24where=report_date_as_yyyy_mm_dd+%3E%3D+%272015-01-01T00%3A00%3A00%27&%24order=report_date_as_yyyy_mm_dd+ASC&%24limit=5000, https://publicreporting.cftc.gov/resource/72hh-3qpy.json?cftc_contract_market_code=06765T&%24where=report_date_as_yyyy_mm_dd+%3E%3D+%272015-01-01T00%3A00%3A00%27&%24order=report_date_as_yyyy_mm_dd+ASC&%24limit=5000, https://publicreporting.cftc.gov/resource/72hh-3qpy.json?cftc_contract_market_code=111659&%24where=report_date_as_yyyy_mm_dd+%3E%3D+%272015-01-01T00%3A00%3A00%27&%24order=report_date_as_yyyy_mm_dd+ASC&%24limit=5000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T11:48:10Z, 2026-11-16T11:48:20Z, 2026-11-16T11:48:25Z, 2026-11-16T11:48:30Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 9888 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `managed_money_long` | Managed money long positions, futures only (the CFTC's m_money_positions_long_all), contracts | count | 2472 | 2015-01-06T00:00:00Z | 2026-11-03T00:00:00Z |
| `managed_money_net` | Managed money long less short, computed by the ERW, contracts | count | 2472 | 2015-01-06T00:00:00Z | 2026-11-03T00:00:00Z |
| `managed_money_short` | Managed money short positions, futures only (the CFTC's m_money_positions_short_all), contracts | count | 2472 | 2015-01-06T00:00:00Z | 2026-11-03T00:00:00Z |
| `open_interest` | Open interest, futures only (the CFTC's open_interest_all), contracts | count | 2472 | 2015-01-06T00:00:00Z | 2026-11-03T00:00:00Z |

### `constraints_binding_hourly`

One transmission constraint that bound in one hour of an operator's day-ahead market (SPP or CAISO), with the shadow price the operator published.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. A constraint has a row only in an hour it bound; an absent hour is an hour it did not bind (or a missing file, named in the header).. License: public; tier: source. Rows read on 2026-11-20: 1808231.

- **Time:** ts_utc is the hour's start in UTC.
- **Revisions:** Merged by (entity, variable, ts_utc); a day read again from the operator replaces the rows held for it, and rows not read again are kept. vintage is not filled.
- **Source:** spp:DA-BC Day-Ahead Binding Constraints (https://portal.spp.org/pages/da-binding-constraints)
- **Method note:** [`docs/methods/grid_congestion.md`](../methods/grid_congestion.md)
- **Cite as:** CAISO; SPP. Via the Energy Research Warehouse (ERW), table `constraints_binding_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example caiso:18023_PAHRUMP _230_18904_BOB SS  _230_BR_1 _1\|Base Case, caiso:18023_PAHRUMP _230_18910_INOVATIN_230_BR_1 _1\|Base Case, caiso:18076_LTHRPWLS_138_18999_VEAJAF  _138_BR_1 _1\|Base Case; more than 5000 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2014-03-01T06:00:00Z to 2026-11-21T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -9446.50604 to 8529.24217; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-CA,US-NV | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_dam, spp_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 1808231 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:PRC_NOMOGRAM, spp:DA-BC | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_NOMOGRAM&version=1&market_run_id=DAM&startdatetime=20150101T08:00-0000&enddatetime=20150201T08:00-0000, https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_NOMOGRAM&version=1&market_run_id=DAM&startdatetime=20150201T08:00-0000&enddatetime=20150301T08:00-0000, https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_NOMOGRAM&version=1&market_run_id=DAM&startdatetime=20150301T08:00-0000&enddatetime=20150401T07:00-0000; 843 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-20T10:41:34Z to 2026-11-20T12:07:29Z; 843 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1808231 |
| `x_constraint` | The constraint's name alone, as the operator prints it (SPP Constraint Name, CAISO NOMOGRAM_ID_XML) | none | text | for example 021BA_LN@TULSA_NO<CON1097>, 1001_LN@COULTER<28374>, 10028A_LN@NESCTY<11922>; more than 5000 distinct | 0 |
| `x_contingency` | The contingency under which the constraint bound, as the operator prints it (SPP Contingency Name, CAISO CONSTRAINT_CAUSE); empty in SPP's files before 2022, which print none | none | text | for example 100, 1003, 10042; 2316 distinct | 622588: the operator's file prints no contingency for the row |
| `x_monitored` | The monitored facility, as SPP prints it (Monitored Facility) | none | text | for example LN  - BEVRC7, LN  - TEXAS_CO, LN 103_ROKE - MOORE; 2746 distinct | 490111: CAISO prints no such column |
| `x_contingent_facility` | The contingent facility, as SPP prints it (Contingent Facility) | none | text | for example ADD NEW EAST, AECI : 5HOLMAN MARSHFLD : 161 69 :, AECI : BLACKBRY JASPER7 : 345 : 1; 4639 distinct | 490111: CAISO prints no such column |
| `x_constraint_type` | SPP's constraint type code as printed (FG flowgate, MA, MCE, RTCA, WRC) | none | text | FG, MA, MCE, RTCA, WRC | 490111: CAISO prints no such column |
| `x_nerc_id` | The NERC flowgate identifier SPP prints (NERCID) | none | integer | 1015 to 99995; 3287 distinct | 1072052: CAISO prints no such column, or SPP printed none for the row |
| `x_state` | SPP's state of the constraint in the hour (BINDING, BREACHED, MONITORED), not a US state | none | text | BINDING, BREACHED, MONITORED | 490111: CAISO prints no such column |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `shadow_price_dam` | The constraint's shadow price in the day-ahead market, USD/MWh, sign as printed (SPP negative, CAISO positive) | USD/MWh | 1808231 | 2014-03-01T06:00:00Z | 2026-11-21T07:00:00Z |

### `constraints_binding_monthly`

One constraint (with its contingency) in one month, from constraints_binding_hourly; derived.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 223556.

- **Time:** ts_utc is the month's first day at 00:00 UTC.
- **Revisions:** Rebuilt from constraints_binding_hourly at each run and merged by (entity, variable, ts_utc), so a month recomputed replaces the one held. vintage is not filled.
- **Source:** erw:constraints_binding_monthly ERW derived table (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_congestion.md)
- **Method note:** [`docs/methods/grid_congestion.md`](../methods/grid_congestion.md)
- **Cite as:** CAISO; SPP. Via the Energy Research Warehouse (ERW), table `constraints_binding_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example caiso:18023_PAHRUMP _230_18904_BOB SS  _230_BR_1 _1\|Base Case, caiso:18023_PAHRUMP _230_18910_INOVATIN_230_BR_1 _1\|Base Case, caiso:18076_LTHRPWLS_138_18999_VEAJAF  _138_BR_1 _1\|Base Case; more than 5000 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-11-01T00:00:00Z; 143 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -2507.47256 to 9446.50604; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-CA,US-NV | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_dam, spp_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 223556 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:constraints_binding_monthly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_congestion.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-20T12:13:22Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 223556 |
| `x_constraint` | The constraint's name alone, as the operator prints it | none | text | for example 021BA_LN@TULSA_NO<CON1097>, 1001_LN@COULTER<28374>, 10028A_LN@NESCTY<11922>; more than 5000 distinct | 0 |
| `x_contingency` | The contingency under which it bound, as the operator prints it; empty where the operator printed none | none | text | for example 100, 1003, 10042; 2316 distinct | 68928: the operator's file prints no contingency |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `hours_bound` | Hours the constraint bound in the month's day-ahead market, count | count | 55889 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `shadow_price_abs_max` | Highest size (absolute value) of the shadow price in the month, USD/MWh | USD/MWh | 55889 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `shadow_price_abs_mean` | Mean size (absolute value) of the shadow price over the hours it bound, USD/MWh | USD/MWh | 55889 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `shadow_price_mean` | Mean shadow price over the hours it bound, sign as printed, USD/MWh | USD/MWh | 55889 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |

### `cso_ireland_electricity_monthly`

Ireland's gross or net electricity output in one month, from the Central Statistics Office's table MSM01.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 644.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; from 1975-01.
- **Revisions:** Rewritten whole as one snapshot by each run from CSO's JSON-stat answer; vintage is the answer's updated time.
- **Source:** cso:MSM01 Central Statistics Office, Ireland, PxStat, table MSM01 (https://data.cso.ie/table/MSM01)
- **Method note:** [`docs/methods/cso_ireland_electricity_monthly.md`](../methods/cso_ireland_electricity_monthly.md)
- **Cite as:** Central Statistics Office, Ireland (CSO). PxStat table MSM01: Electricity Output (monthly). Via the Energy Research Warehouse (ERW), table `cso_ireland_electricity_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: cso:ie on every row | none | text | cso:ie | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1975-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 620 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 503000.0 to 3004000.0; 543 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: IE on every row | none | text | IE | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 644 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The statistic as CSO names it, not a pricing node | none | text | Gross Electricity Output, Net Electricity Output | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | cso:MSM01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/MSM01/JSON-stat/2.0/en | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T06:48:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The JSON-stat answer's updated time (UTC) | none | utc time | 2026-10-09T11:00:00Z | 0 |
| `x_code` | CSO's code of the statistic: MSM01C1 gross output, MSM01C2 net output | none | text | MSM01C1, MSM01C2 | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `gross_electricity_output` | Gross electricity output in the month (to 2008-12, discontinued by CSO) | MWh | 408 | 1975-01-01T00:00:00Z | 2008-12-01T00:00:00Z |
| `net_electricity_output` | Net electricity output in the month | MWh | 236 | 2007-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `czso_cz_regional_electricity_annual`

One Czech region's (or Czechia's) installed capacity or gross production by type of plant, or net consumption by activity, in 2024, from the Czech Statistical Office's Comparison of Regions.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 360.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z; freq P1Y; capacity at 31 December.
- **Revisions:** Merged by (entity, variable, ts_utc): each run's rows replace the same keys and older ones are kept; vintage is the zip's Last-Modified.
- **Source:** czso:comparison_of_regions_14_energy Czech Statistical Office (CZSO), Comparison of Regions in the Czech Republic 2025, 14. Energy (source: Energy Regulatory Office) (https://csu.gov.cz/produkty/comparison-of-regions-in-the-czech-republic-2025)
- **Method note:** [`docs/methods/czso_cz_regional_electricity_annual.md`](../methods/czso_cz_regional_electricity_annual.md)
- **Cite as:** Czech Statistical Office (CZSO). Comparison of Regions in the Czech Republic 2025, 14. Energy (tables 14.101 and 14.103). Via the Energy Research Warehouse (ERW), table `czso_cz_regional_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: czso_regions:<ISO 3166-2 region code, or CZ>:<item> | none | text | for example czso_regions:CZ-10:agriculture_forestry, czso_regions:CZ-10:combined_cycle, czso_regions:CZ-10:construction; 225 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 73881775.218; 312 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: CZ on every row, whatever the region (the region is in entity and x_region) | none | text | CZ | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 360 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: CZSO <area code>, <the table's English label>, in ASCII, not a pricing node | none | text | for example CZSO CZ, Agriculture and forestry, CZSO CZ, Combined power plants, CZSO CZ, Construction; 255 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | czso:comparison_of_regions_14_energy | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://csu.gov.cz/docs/107508/4491dd21-67d2-55cf-a3e6-926ec9c4b345/33020525.zip?version=1.1 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T05:01:44Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The zip's Last-Modified (UTC) | none | utc time | 2026-02-12T12:46:51Z | 0 |
| `x_region` | The region's name in Czech, as the tables give it | none | text | Hl. m. Praha, Jihomoravský, Jihočeský, Karlovarský, Královéhradecký, Liberecký, Moravskoslezský, Olomoucký, Pardubický, Plzeňský, Středočeský, Vysočina, Zlínský, Ústecký, Česko Czechia | 0 |
| `x_table` | The CZSO table the row is read from: 14.101 (capacity and gross production by type of plant) or 14.103 (net consumption by activity) | none | number | 14.101, 14.103 | 0 |
| `x_label` | The table's own label of the row, in Czech (the type of plant, the activity or the total) | none | text | Instalovaný výkon elektráren-ských soustrojí k 31. 12. (MW), Spotřeba elektřiny netto (GWh), Výroba elektřiny brutto (GWh), domácnosti, doprava, energetika, fotovoltaické elektrárny, jaderné elektrárny, obchod, služby, školství a zdravotnictví, parní elektrárny, paroplynové elektrárny, plynové a spalovací elektrárny, průmysl, stavebnictví, vodní elektrárny včetně přečerpávacích, větrné elektrárny, zemědělství a lesnictví | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `gross_production` | Gross electricity production of the type of plant in the region in the year | MWh | 120 | 2024-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `installed_capacity` | Installed capacity of the type of plant in the region at 31 December | MW | 120 | 2024-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_consumption` | Net electricity consumption of the activity in the region in the year | MWh | 120 | 2024-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `destatis_de_electricity_monthly`

One month's electricity or heat generation of Germany's general supply plants from one energy source (or in total), from Destatis' monthly report.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 123.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; provisional figures.
- **Revisions:** Merged by (entity, variable, ts_utc): each run's month replaces the same keys and older months are kept; vintage is the page's Last-Modified.
- **Source:** destatis:monatsbericht_elektrizitaet_waerme Statistisches Bundesamt (Destatis), Elektrizitaets- und Waermeerzeugung nach Energietraegern (Monatsbericht) (https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Energie/Erzeugung/Tabellen/elekrizitaet-waermeerzeugung-energietraeger-monatsbericht.html)
- **Method note:** [`docs/methods/destatis_de_electricity_monthly.md`](../methods/destatis_de_electricity_monthly.md)
- **Cite as:** Statistisches Bundesamt (Destatis). Elektrizitaets- und Waermeerzeugung nach Energietraegern (Monatsbericht). Via the Energy Research Warehouse (ERW), table `destatis_de_electricity_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: destatis:de (Insgesamt, the total) or destatis:de:<energy source slug> | none | text | for example destatis:de, destatis:de:abfall_hausmuell_siedlungsabfaelle, destatis:de:andere_mineraloelprodukte; 27 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-07-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 11973315.0; 62 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: DE on every row | none | text | DE | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 123 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Destatis general supply, <label>, <measure>, not a pricing node | none | text | for example Destatis general supply, Abfall (Hausmüll, Siedlungsabfälle), gross electricity generation, Destatis general supply, Abfall (Hausmüll, Siedlungsabfälle), net electricity generation, Destatis general supply, Abfall (Hausmüll, Siedlungsabfälle), net electricity generation in CHP; 123 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | destatis:monatsbericht_elektrizitaet_waerme | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Energie/Erzeugung/Tabellen/elekrizitaet-waermeerzeugung-energietraeger-monatsbericht.html | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T04:45:04Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The page's Last-Modified (UTC) | none | utc time | 2026-10-26T04:45:04Z | 0 |
| `x_label` | The page's label of the energy source, in German, as printed | none | text | for example Abfall (Hausmüll, Siedlungsabfälle), Andere Mineralölprodukte, Biogas; 27 distinct | 0 |
| `x_cell` | The page's cell as printed ('-' is zero) | none | text | for example -, - -, 1 029 403; 63 distinct | 0 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `gross_generation` | Gross electricity generation of general supply plants in the month | MWh | 24 | 2026-07-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_generation` | Net electricity generation of general supply plants in the month | MWh | 24 | 2026-07-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_generation_chp` | Net electricity generation in combined heat and power in the month | MWh | 24 | 2026-07-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_heat_generation` | Net heat generation in the month | MWh | 26 | 2026-07-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_heat_generation_chp` | Net heat generation in combined heat and power in the month | MWh | 25 | 2026-07-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `dfe_ni_electricity_monthly`

One month's value of Northern Ireland's renewable or non-renewable generation (by type or fuel) or its electricity trade, from the Department for the Economy's report figures 6 to 9.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1326.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; from 2018-01.
- **Revisions:** Rewritten whole as one snapshot by each run from the report's CSV figures; vintage is the files' Last-Modified.
- **Source:** dfe_ni:electricity_consumption_renewable_generation_2026 Department for the Economy (Northern Ireland), Electricity Consumption and Renewable Generation in Northern Ireland, April 2025 to March 2026 (4 June 2026), figures 6 to 9
- **Method note:** [`docs/methods/dfe_ni_electricity_monthly.md`](../methods/dfe_ni_electricity_monthly.md)
- **Cite as:** Department for the Economy (Northern Ireland). Electricity Consumption and Renewable Generation in Northern Ireland, April 2025 to March 2026, figures 6 to 9. Via the Energy Research Warehouse (ERW), table `dfe_ni_electricity_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: dfe_ni:gb-nir:<item>: a type or fuel, or total | none | text | dfe_ni:gb-nir:bioenergy, dfe_ni:gb-nir:coal, dfe_ni:gb-nir:distillate_other, dfe_ni:gb-nir:gas, dfe_ni:gb-nir:hydro_tidal, dfe_ni:gb-nir:landfill_gas, dfe_ni:gb-nir:solar, dfe_ni:gb-nir:total, dfe_ni:gb-nir:wind | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-01-01T00:00:00Z to 2026-06-01T00:00:00Z; 102 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -136000.0 to 576000.0; 440 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: GB-NIR on every row | none | text | GB-NIR | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1326 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: DfE's column header, not a pricing node | none | text | Bioenergy(GWh), Coal (GWh), Distillate and Other (GWh), Export (Gwh), Gas (GWh), Hydro/Tidal (GWh), Import (GWh), Landfill gas (GWh), Net imports (Gwh), Non-renewable generation (GWh), Renewable generation (GWh), Solar PV(GWh), Wind (GWh) | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | dfe_ni:electricity_consumption_renewable_generation_2026 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://datavis.nisra.gov.uk/Economy/electricity-consumption-and-renewable-generation-report.html | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T21:58:24Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The CSV files' Last-Modified (UTC) | none | utc time | 2026-09-03T08:30:10Z | 0 |
| `x_figure` | The report figure's link text the row is read from (Figure 6 to Figure 9) | none | text | Figure 6.CSV (5kB), Figure 7.CSV (4kB), Figure 8.CSV (4kB), Figure 9.CSV (5kB) | 0 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `exports` | Electricity exported in the month, written positive | MWh | 102 | 2018-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `imports` | Electricity imported in the month | MWh | 102 | 2018-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `net_imports` | Net imports in the month | MWh | 102 | 2018-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `non_renewable_generation` | Non-renewable generation in the month, total or by fuel (gas, coal, distillate and other) | MWh | 408 | 2018-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `renewable_generation` | Renewable generation in the month, total or by type (wind, solar, bioenergy, landfill gas, hydro and tidal) | MWh | 612 | 2018-01-01T00:00:00Z | 2026-06-01T00:00:00Z |

### `dosm_malaysia_electricity_monthly`

One month's value of Malaysia's electricity supply or consumption by sector, from the Department of Statistics Malaysia.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1224.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; the latest six months provisional.
- **Revisions:** Merged by (entity, variable, ts_utc): each run's months replace the same months and older ones are kept; vintage is each file's Last-Modified.
- **Source:** dosm:electricity_supply_consumption Department of Statistics Malaysia, Monthly Electricity Supply and Monthly Electricity Consumption (compiled from TNB, SESB, Sarawak Energy and the Energy Commission) (https://data.gov.my/data-catalogue/electricity_supply)
- **Method note:** [`docs/methods/dosm_malaysia_electricity_monthly.md`](../methods/dosm_malaysia_electricity_monthly.md)
- **Cite as:** Department of Statistics Malaysia (DOSM). Monthly Electricity Supply and Monthly Electricity Consumption, by sector (data.gov.my catalogue). Via the Energy Research Warehouse (ERW), table `dosm_malaysia_electricity_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: dosm:MY on every row | none | text | dosm:MY | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-01-01T00:00:00Z to 2026-06-01T00:00:00Z; 102 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 17563330.992741447; 970 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: MY on every row | none | text | MY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1224 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Malaysia on every row, not a pricing node | none | text | Malaysia | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | dosm:electricity_supply_consumption | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://storage.data.gov.my/energy/electricity_consumption.csv, https://storage.data.gov.my/energy/electricity_supply.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T06:31:10Z, 2026-10-24T06:31:11Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's Last-Modified (UTC): the supply file or the consumption file | none | utc time | 2026-10-07T16:10:05Z, 2026-10-07T16:10:06Z | 0 |

Variables (12):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption_exports` | Electricity consumption, exports | MWh | 102 | 2018-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `consumption_local` | Electricity consumption, local | MWh | 102 | 2018-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `consumption_local_commercial` | Electricity consumption, local commercial (includes industry and mining) | MWh | 102 | 2018-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `consumption_local_domestic` | Electricity consumption, local domestic (includes public lighting) | MWh | 102 | 2018-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `consumption_losses` | Electricity consumption, losses | MWh | 102 | 2018-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `consumption_total` | Electricity consumption, total | MWh | 102 | 2018-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `supply_distribution` | DOSM's distribution sector of supply (equal to the total every month: never add it to the other sectors) | MWh | 102 | 2018-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `supply_imports` | Electricity supply, imports | MWh | 102 | 2018-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `supply_local` | Electricity supply, local | MWh | 102 | 2018-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `supply_local_private` | Electricity supply, local private | MWh | 102 | 2018-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `supply_local_public` | Electricity supply, local public | MWh | 102 | 2018-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `supply_total` | Electricity supply, total | MWh | 102 | 2018-01-01T00:00:00Z | 2026-06-01T00:00:00Z |

### `dst_dk_electricity_supply_annual`

One year's value of Denmark's electricity supply, production or imports, or its wind, hydro or solar power supply, from Statistics Denmark's Energy Account table ENE1HT.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 360.

- **Time:** ts_utc is the year's first day at 00:00:00Z; freq P1Y; 1966 to 2025.
- **Revisions:** Rewritten whole as one snapshot by each run from the StatBank answer; vintage is not filled.
- **Source:** dst:statbank_ene1ht Statistics Denmark, StatBank table ENE1HT, Energy Account in specific units (detailed table), supply
- **Method note:** [`docs/methods/dst_dk_electricity_supply_annual.md`](../methods/dst_dk_electricity_supply_annual.md)
- **Cite as:** Statistics Denmark (Danmarks Statistik). StatBank ENE1HT, Energy Account in specific units (detailed table), supply. Via the Energy Research Warehouse (ERW), table `dst_dk_electricity_supply_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: dst_ene:dk on every row | none | text | dst_ene:dk | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1966-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 60 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 59287000.0; 263 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: DK on every row | none | text | DK | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 360 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The StatBank codes and texts of the supply item and energy kind, not a pricing node | none | text | EIMPORT Imports; EMEL Electricity (GWh), EPRODI Total production; EMEL Electricity (GWh), ETIL Total supply; EMEL Electricity (GWh), ETILVE Supply of renewable energy; EMSOLK Solar power (GWh), ETILVE Supply of renewable energy; EMVAND Hydro power (GWh), ETILVE Supply of renewable energy; EMVIND Wind power (GWh) | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | dst:statbank_ene1ht | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.statbank.dk/v1/data/ENE1HT/CSV?lang=en&delimiter=Semicolon&valuePresentation=CodeAndValue&TILGANG=ETIL,EIMPORT,ETILVE,EPRODI&ENERGI1=EMEL,EMVIND,EMVAND,EMSOLK&Tid=* | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T22:15:24Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 360 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `electricity_imports` | Imports of electricity (EIMPORT, EMEL) | MWh | 60 | 1966-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `electricity_production` | Total production of electricity (EPRODI, EMEL) | MWh | 60 | 1966-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `electricity_total_supply` | Total supply of electricity (ETIL, EMEL) | MWh | 60 | 1966-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `hydro_power_supply` | Supply of renewable energy from hydro power (ETILVE, EMVAND) | MWh | 60 | 1966-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `solar_power_supply` | Supply of renewable energy from solar power (ETILVE, EMSOLK) | MWh | 60 | 1966-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `wind_power_supply` | Supply of renewable energy from wind power (ETILVE, EMVIND) | MWh | 60 | 1966-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `edf_sei_islands_electricity_annual`

One French island grid's net electricity production from one source, its net imports or its total supply, in one year, from EDF SEI.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 326.

- **Time:** ts_utc is the year's first day at 00:00:00Z; freq P1Y; 2018 to 2024.
- **Revisions:** Rewritten whole as one snapshot by each run from EDF's open data answer; vintage is not filled.
- **Source:** edf_sei:production-annuelle-delectricite-par-filiere EDF SA, Production annuelle d'electricite par filiere d'EDF SA en Corse & Outremer
- **Method note:** [`docs/methods/edf_sei_islands_electricity_annual.md`](../methods/edf_sei_islands_electricity_annual.md)
- **Cite as:** EDF SA (EDF Systemes Energetiques Insulaires). Production annuelle d'electricite par filiere d'EDF SA en Corse & Outremer (annual net electricity production by source, the island grids). Via the Energy Research Warehouse (ERW), table `edf_sei_islands_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: edf_sei:<territory>:<source> | none | text | for example edf_sei:corsica:bioenergy, edf_sei:corsica:diesel, edf_sei:corsica:hydro; 51 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 3089572.0; 316 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: The territory's code (FR-20R Corsica, GF, GP, MQ, RE, BL, MF, PM; FR for the Iles du Ponant) | none | text | BL, FR, FR-20R, GF, GP, MF, MQ, PM, RE | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 326 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The territory as EDF names it, not a pricing node | none | text | Corse, Guadeloupe, Guyane, Iles du Ponant, Martinique, Réunion, St Barthélemy, St Martin, St Pierre et Miquelon | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | edf_sei:production-annuelle-delectricite-par-filiere | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://opendata.edf.fr/data-fair/api/v1/datasets/production-annuelle-delectricite-par-filiere/lines?size=1000 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T09:17:20Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 326 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `generation` | Net energy injected into the territory's grid from the source in the year | MWh | 261 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_imports` | Net imports over Corsica's links in the year | MWh | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `supply` | The territory's total in the year | MWh | 58 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `egrid_power_plants`

One US power plant of eGRID2023 (data year 2023): its capacity, generation, emissions and emission rates, as EPA publishes them.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 12612.

- **Time:** No time column; data_year 2023 and vintage eGRID2023 name the edition; the table is a snapshot as read on its retrieved_at.
- **Revisions:** Rewritten whole as one snapshot: a later run replaces the whole table when EPA publishes a new eGRID.
- **Source:** epa:egrid U.S. Environmental Protection Agency, Emissions & Generation Resource Integrated Database (eGRID2023), plant sheet PLNT23 (https://www.epa.gov/egrid/download-data)
- **Method note:** [`docs/methods/egrid_power_plants.md`](../methods/egrid_power_plants.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). Emissions & Generation Resource Integrated Database (eGRID). Via the Energy Research Warehouse (ERW), table `egrid_power_plants`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: egrid:<ORISPL>, the DOE/EIA plant code | none | text | for example egrid:1, egrid:10, egrid:100; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | plant | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example (3K) 59 Hetcheltown Rd, 0 Hammond St CSG, 1 Commercial; more than 5000 distinct | 1 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 52 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 17.947115 to 71.292; more than 5000 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -171.712439 to -65.27956; more than 5000 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: eGRID's plant nameplate capacity (NAMEPCAP) | MW | number | 0.3 to 6809.0; 2193 distinct | 1 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: eGRID gives no status | none | empty | no cell holds a value | 12612 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: Not filled: eGRID gives no status | none | empty | no cell holds a value | 12612 |
| `operator` | The operator or owner, as the publisher writes it. Here: The utility's name (eGRID's UTLSRVNM) | none | text | for example 0HAM WHAM8 Solar, LLC, 1001 Ebenezer Church Solar, LLC, 1008 Matthews Solar, LLC; more than 5000 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:egrid | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epa.gov/system/files/documents/2025-06/egrid2023_data_rev2.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T16:59:48Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: eGRID2023, the edition's name (not a date) | none | text | eGRID2023 | 0 |
| `data_year` | eGRID's data year (the source's name: YEAR) | none | integer | 2023 | 0 |
| `plant_id` | The DOE/EIA ORIS plant or facility code (the source's name: ORISPL) | none | integer | 1 to 70454; more than 5000 distinct | 0 |
| `state` | The plant's state, postal code (the source's name: PSTATABB) | none | text | for example AK, AL, AR; 52 distinct | 0 |
| `county` | The plant's county name (the source's name: CNTYNAME) | none | text | for example Abbeville, Acadia, Accomack; 1456 distinct | 26: eGRID leaves the cell blank |
| `fips_state` | The plant's FIPS state code, zero-padded to 2 digits (the source's name: FIPSST) | none | integer | 1 to 72; 52 distinct | 0 |
| `fips_county` | The plant's FIPS county code, zero-padded to 3 digits (the source's name: FIPSCNTY) | none | integer | 1 to 810; 243 distinct | 142: eGRID leaves the cell blank |
| `transmission_owner` | The name of the plant's transmission or distribution system owner (the source's name: OPRNAME) | none | text | for example 4 Rivers Electric Cooperative, Inc., 4-County Electric Power Assn, A & N Electric Coop; 1067 distinct | 62: eGRID leaves the cell blank |
| `utility_id` | The utility's ID (the source's name: UTLSRVID) | none | integer | 7 to 66470; more than 5000 distinct | 0 |
| `sector` | eGRID's plant-level sector (Electric Utility, IPP, Industrial or Commercial, CHP or not) (the source's name: SECTOR) | none | text | Commercial CHP, Commercial Non-CHP, Electric Utility, IPP CHP, IPP Non-CHP, Industrial CHP, Industrial Non-CHP | 0 |
| `balancing_authority` | The balancing authority's code (the source's name: BACODE) | none | text | for example AECI, AVA, AVRN; 69 distinct | 1: eGRID leaves the cell blank |
| `balancing_authority_name` | The balancing authority's name (the source's name: BANAME) | none | text | for example Alcoa Power Generating, Inc. - Yadkin Division, Arizona Public Service Company, Arlington Valley, LLC - AVBA; 70 distinct | 0 |
| `nerc_region` | The NERC region's acronym (the source's name: NERC) | none | text | AK, HI, MRO, NPCC, PR, RFC, SERC, TRE, WECC | 0 |
| `egrid_subregion` | The eGRID subregion's acronym (the source's name: SUBRGN) | none | text | for example AKGD, AKMS, AZNM; 27 distinct | 0 |
| `iso_rto` | The ISO or RTO territory the plant is associated with (the source's name: ISORTO) | none | text | CAISO, ERCOT, ISONE, MISO, NYISO, PJM, SPP | 4399: eGRID leaves the cell blank (no ISO or RTO named) |
| `units` | The plant's number of units (the source's name: NUMUNT) | count | integer | 1 to 73; 35 distinct | 1: eGRID leaves the cell blank |
| `generators` | The plant's number of generators (the source's name: NUMGEN) | count | integer | 1 to 73; 35 distinct | 1: eGRID leaves the cell blank |
| `primary_fuel` | The plant's primary fuel, eGRID's code (the source's name: PLPRMFL) | none | text | for example AB, BFG, BIT; 36 distinct | 0 |
| `primary_fuel_category` | The plant's primary fuel category (COAL, GAS, OIL, NUCLEAR, HYDRO, WIND, SOLAR, BIOMASS, GEOTHERMAL, OFSL, OTHF) (the source's name: PLFUELCT) | none | text | BIOMASS, COAL, GAS, GEOTHERMAL, HYDRO, NUCLEAR, OFSL, OIL, OTHF, SOLAR, WIND | 0 |
| `coal_flag` | Yes when the plant burned or generated any amount of coal (the source's name: COALFLAG) | none | text | Yes | 12509: eGRID leaves the cell blank (only Yes is printed) |
| `chp_flag` | Yes when eGRID applies its combined heat and power (CHP) plant adjustment (the source's name: CHPFLAG) | none | text | Yes | 11682: eGRID leaves the cell blank (only Yes is printed) |
| `capacity_factor` | The plant's capacity factor (the source's name: CAPFAC) | ratio | number | 0.0 to 1.37976; more than 5000 distinct | 373: eGRID leaves the cell blank |
| `heat_input_mmbtu` | The plant's annual heat input from combustion (the source's name: PLHTIAN) | MMBtu | number | 0.0 to 172665705.425; 3232 distinct | 8964: eGRID leaves the cell blank |
| `net_generation_mwh` | The plant's annual net generation (the source's name: PLNGENAN) | MWh | number | -1034280.0 to 31522590.0; more than 5000 distinct | 373: eGRID leaves the cell blank |
| `nox_tons` | The plant's annual NOx emissions (the source's name: PLNOXAN) | short ton | number | 0.0 to 12604.704; 2848 distinct | 9209: eGRID leaves the cell blank |
| `so2_tons` | The plant's annual SO2 emissions (the source's name: PLSO2AN) | short ton | number | 0.0 to 39245.681; 2142 distinct | 9208: eGRID leaves the cell blank |
| `co2_tons` | The plant's annual CO2 emissions (the source's name: PLCO2AN) | short ton | number | 0.0 to 18109178.3; 2851 distinct | 9208: eGRID leaves the cell blank |
| `ch4_lbs` | The plant's annual CH4 (methane) emissions (the source's name: PLCH4AN) | lb | number | 0.0 to 4148743.931; 2957 distinct | 9067: eGRID leaves the cell blank |
| `n2o_lbs` | The plant's annual N2O (nitrous oxide) emissions (the source's name: PLN2OAN) | lb | number | 0.0 to 603513.812; 2913 distinct | 9067: eGRID leaves the cell blank |
| `co2e_tons` | The plant's annual CO2 equivalent emissions (the source's name: PLCO2EQA) | short ton | number | 0.0 to 18240458.877; 3056 distinct | 8991: eGRID leaves the cell blank |
| `hg_lbs` | The plant's annual mercury (Hg) emissions (the source's name: PLHGAN) | lb | empty | no cell holds a value | 12612: eGRID leaves every cell blank in this edition (no cell holds a value) |
| `nox_rate_lb_mwh` | The plant's annual NOx emission rate per MWh of total output (the source's name: PLNOXRTA) | lb/MWh | number | 0.0 to 8500.0; 2301 distinct | 9339: eGRID leaves the cell blank |
| `so2_rate_lb_mwh` | The plant's annual SO2 emission rate per MWh of total output (the source's name: PLSO2RTA) | lb/MWh | number | 0.0 to 752.0; 1182 distinct | 9338: eGRID leaves the cell blank |
| `co2_rate_lb_mwh` | The plant's annual CO2 emission rate per MWh of total output (the source's name: PLCO2RTA) | lb/MWh | number | 0.0 to 423504.0; 2770 distinct | 9338: eGRID leaves the cell blank |
| `co2e_rate_lb_mwh` | The plant's annual CO2 equivalent emission rate per MWh of total output (the source's name: PLC2ERTA) | lb/MWh | number | 0.0 to 424893.132; 2941 distinct | 9305: eGRID leaves the cell blank |
| `heat_rate_btu_kwh` | The plant's nominal heat rate (fuel heat per kWh generated) (the source's name: PLHTRT) | Btu/kWh | number | -3332000.0 to 2593000.0; 3244 distinct | 9314: eGRID leaves the cell blank |
| `gen_coal_mwh` | The plant's annual net generation from coal (the source's name: PLGENACL) | MWh | number | -7625.153 to 15767071.0; 268 distinct | 372: eGRID leaves the cell blank |
| `gen_oil_mwh` | The plant's annual net generation from oil (the source's name: PLGENAOL) | MWh | number | -4977.0 to 2550227.0; 1194 distinct | 372: eGRID leaves the cell blank |
| `gen_gas_mwh` | The plant's annual net generation from gas (the source's name: PLGENAGS) | MWh | number | -27603.0 to 19937352.0; 2218 distinct | 372: eGRID leaves the cell blank |
| `gen_nuclear_mwh` | The plant's annual net generation from nuclear (the source's name: PLGENANC) | MWh | integer | 0 to 31522590; 55 distinct | 372: eGRID leaves the cell blank |
| `gen_hydro_mwh` | The plant's annual net generation from hydro (the source's name: PLGENAHY) | MWh | number | -1034280.0 to 15749890.0; 1366 distinct | 372: eGRID leaves the cell blank |
| `gen_biomass_mwh` | The plant's annual net generation from biomass (the source's name: PLGENABM) | MWh | number | -7400.806 to 506058.1; 615 distinct | 372: eGRID leaves the cell blank |
| `gen_wind_mwh` | The plant's annual net generation from wind (the source's name: PLGENAWI) | MWh | number | -10328.0 to 3887512.0; 1297 distinct | 372: eGRID leaves the cell blank |
| `gen_solar_mwh` | The plant's annual net generation from solar (the source's name: PLGENASO) | MWh | number | -3151.0 to 1036774.0; 4514 distinct | 372: eGRID leaves the cell blank |
| `gen_geothermal_mwh` | The plant's annual net generation from geothermal (the source's name: PLGENAGT) | MWh | integer | 0 to 4499612; 64 distinct | 372: eGRID leaves the cell blank |
| `gen_other_fossil_mwh` | The plant's annual net generation from other fossil fuels (the source's name: PLGENAOF) | MWh | number | -9045.315 to 1376971.9; 151 distinct | 372: eGRID leaves the cell blank |
| `gen_other_purchased_mwh` | The plant's annual net generation from other, unknown or purchased fuel (the source's name: PLGENAOP) | MWh | number | -107414.0 to 481609.0; 344 distinct | 372: eGRID leaves the cell blank |

### `egrid_subregions_annual`

One eGRID2023 subregion's value of one measure (capacity, net generation, CO2 emissions and rates, resource mix) for data year 2023.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 540.

- **Time:** ts_utc is 2023-01-01T00:00:00Z on every row; freq P1Y.
- **Revisions:** Rewritten whole as one snapshot by each run from EPA's eGRID workbook; vintage is the workbook's Last-Modified.
- **Source:** epa:egrid_subregions U.S. Environmental Protection Agency, Emissions & Generation Resource Integrated Database (eGRID2023), subregion sheet SRL23 (https://www.epa.gov/egrid/download-data)
- **Method note:** [`docs/methods/egrid_subregions_annual.md`](../methods/egrid_subregions_annual.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). eGRID2023 (subregion sheet). Via the Energy Research Warehouse (ERW), table `egrid_subregions_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: egrid:<eGRID subregion acronym> | none | text | for example egrid:AKGD, egrid:AKMS, egrid:AZNM; 27 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 524352082.167; 353 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, kgCO2/MWh, ratio, tCO2 | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: a subregion crosses states | none | empty | no cell holds a value | 540 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 540 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The subregion's name, not a pricing node | none | text | for example ASCC Alaska Grid, ASCC Miscellaneous, ERCOT All; 27 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:egrid_subregions | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epa.gov/system/files/documents/2025-06/egrid2023_data_rev2.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T16:59:48Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's Last-Modified (UTC) | none | utc time | 2025-06-16T15:33:55Z | 0 |

Variables (20):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `co2_emissions` | Annual CO2 emissions, metric tons (eGRID's short tons times 0.90718474) | tCO2 | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `co2_rate` | CO2 output emission rate, kg per MWh (eGRID's lb/MWh times 0.45359237) | kgCO2/MWh | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `co2_rate_nonbaseload` | CO2 non-baseload output emission rate, kg per MWh | kgCO2/MWh | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `co2e_emissions` | Annual CO2 equivalent emissions, metric tons (eGRID's short tons times 0.90718474) | tCO2 | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `co2e_rate` | CO2 equivalent output emission rate, kg per MWh | kgCO2/MWh | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `nameplate_capacity` | The subregion's nameplate capacity | MW | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `net_generation` | The subregion's annual net generation | MWh | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `share_biomass` | Share of net generation from biomass (resource mix) | ratio | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `share_coal` | Share of net generation from coal (resource mix) | ratio | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `share_gas` | Share of net generation from gas (resource mix) | ratio | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `share_geothermal` | Share of net generation from geothermal (resource mix) | ratio | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `share_hydro` | Share of net generation from hydro (resource mix) | ratio | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `share_nonrenewables` | Share of net generation from non-renewables (resource mix) | ratio | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `share_nuclear` | Share of net generation from nuclear (resource mix) | ratio | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `share_oil` | Share of net generation from oil (resource mix) | ratio | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `share_other_fossil` | Share of net generation from other fossil fuels (resource mix) | ratio | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `share_other_unknown` | Share of net generation from other, unknown or purchased fuel (resource mix) | ratio | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `share_renewables` | Share of net generation from renewables (resource mix) | ratio | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `share_solar` | Share of net generation from solar (resource mix) | ratio | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `share_wind` | Share of net generation from wind (resource mix) | ratio | 27 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |

### `eia411_capacity_margins_annual`

One NERC assessment area's value of one supply and demand measure (peak load, net internal demand, capacity resources, capacity margin) for one summer or winter season, actual or projected.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2924.

- **Time:** ts_utc is the peak period's first day: summer 1 June; winter 1 October of the season's first year (EIA's winter runs October to May); freq P1Y.
- **Revisions:** Rewritten whole as one snapshot of the program's last release (November 2016: actual to 2016, projected to 2027); vintage is not filled.
- **Source:** eia:eia411 U.S. Energy Information Administration, Form EIA-411, Coordinated Bulk Power Supply and Demand Program Report (https://www.eia.gov/electricity/data/eia411/)
- **Method note:** [`docs/methods/eia411.md`](../methods/eia411.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Form EIA-411, Coordinated Bulk Power Supply and Demand Program Report. Via the Energy Research Warehouse (ERW), table `eia411_capacity_margins_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia411:<assessment area as EIA names it> | none | text | eia411:balance_of_eastern_region, eia411:contiguous_u_s, eia411:ecar, eia411:frcc, eia411:maac, eia411:main, eia411:mapp, eia411:miso, eia411:mro, eia411:npcc, eia411:pjm, eia411:rfc, eia411:serc, eia411:spp, eia411:tre, eia411:wecc | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-06-01T00:00:00Z to 2027-10-01T00:00:00Z; 76 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.670876063958871 to 1051249.1665787257; 2639 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, whatever the area | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2924 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The assessment area as EIA names it, with its interconnection, not a pricing node | none | text | Balance of Eastern Region (Eastern Interconnection), Contiguous U.S. (All Grids), Contiguous U.S. (All Interconnections), ECAR (Eastern Interconnection), FRCC (Eastern Interconnection), MAAC (Eastern Interconnection), MAIN (Eastern Interconnection), MAPP (Eastern Interconnection), MISO (Eastern Interconnection), MRO (Eastern Interconnection), NPCC (Eastern Interconnection), PJM (Eastern Interconnection), RFC (Eastern Interconnection), SERC (Eastern Interconnection), SPP (Eastern Interconnection), TRE (ERCOT), WECC (Western Interconnection) | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:eia411 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/electricity/data/eia411/xls/peak_load_2016.xls, https://www.eia.gov/electricity/data/eia411/xls/summer_capacity_2016.xls, https://www.eia.gov/electricity/data/eia411/xls/winter_capacity_2016.xls | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T06:13:11Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2924 |
| `x_projected` | actual, or projected (EIA's E years) | none | text | actual, projected | 0 |

Variables (8):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `summer_capacity_margin` | Summer capacity margin, percent of capacity resources (EIA's rough calculation before 2015, NERC's from 2015) | pct | 415 | 1990-06-01T00:00:00Z | 2027-06-01T00:00:00Z |
| `summer_capacity_resources` | Summer capacity resources | MW | 415 | 1990-06-01T00:00:00Z | 2027-06-01T00:00:00Z |
| `summer_net_internal_demand` | Summer net internal demand | MW | 415 | 1990-06-01T00:00:00Z | 2027-06-01T00:00:00Z |
| `summer_peak_load` | Summer peak load | MW | 415 | 1990-06-01T00:00:00Z | 2027-06-01T00:00:00Z |
| `winter_capacity_margin` | Winter capacity margin, percent of capacity resources (EIA's rough calculation before 2015, NERC's from 2015) | pct | 283 | 2001-10-01T00:00:00Z | 2027-10-01T00:00:00Z |
| `winter_capacity_resources` | Winter capacity resources | MW | 283 | 2001-10-01T00:00:00Z | 2027-10-01T00:00:00Z |
| `winter_net_internal_demand` | Winter net internal demand | MW | 283 | 2001-10-01T00:00:00Z | 2027-10-01T00:00:00Z |
| `winter_peak_load` | Winter peak load | MW | 415 | 1990-10-01T00:00:00Z | 2027-10-01T00:00:00Z |

Waiting for a second look: 110 capacity margins (frcc, miso, pjm, spp and tre, 2017 to 2027, both seasons) are resources less demand over demand, a reserve margin, kept as EIA gives them; the variable's label states the general rule only. Read again on 20 November 2026 in docs/methods/eia411.md and the saved EIA-411 workbooks' list under warehouse/raw/eia411: not found..

### `eia861m_utility_sales_monthly`

One sampled utility's retail sales, revenue or customers in one state and sector in one month, from Form EIA-861M.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1051488.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; from 2017-01.
- **Revisions:** Rewritten whole as one snapshot by each run from EIA's yearly files; vintage is not filled; x_data_status marks preliminary years.
- **Source:** eia:eia861m U.S. Energy Information Administration, Form EIA-861M, sales to ultimate customers (https://www.eia.gov/electricity/data/eia861m/)
- **Method note:** [`docs/methods/eia861m_utility_sales_monthly.md`](../methods/eia861m_utility_sales_monthly.md)
- **Cite as:** U.S. Energy Information Administration (EIA). Form EIA-861M, monthly sales to ultimate customers. Via the Energy Research Warehouse (ERW), table `eia861m_utility_sales_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia861m:<EIA utility number>:<state> | none | text | for example eia861m:10000:KS, eia861m:10000:MO, eia861m:10005:KS; 763 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2017-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 115 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 1926363000.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, USD, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> | none | text | for example US-AK, US-AL, US-AR; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1051488 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The utility's name, not a pricing node | none | text | for example 4-County Electric Power Assn, A & N Electric Coop, AES Indiana; 402 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:eia861m | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/electricity/data/eia861m/archive/xls/retail_sales_2017.xlsx, https://www.eia.gov/electricity/data/eia861m/archive/xls/retail_sales_2018.xlsx, https://www.eia.gov/electricity/data/eia861m/archive/xls/retail_sales_2019.xlsx, https://www.eia.gov/electricity/data/eia861m/archive/xls/retail_sales_2020.xlsx, https://www.eia.gov/electricity/data/eia861m/archive/xls/sales_ult_cust_2021.xlsx, https://www.eia.gov/electricity/data/eia861m/archive/xls/sales_ult_cust_2022.xlsx, https://www.eia.gov/electricity/data/eia861m/archive/xls/sales_ult_cust_2023.xlsx, https://www.eia.gov/electricity/data/eia861m/archive/xls/sales_ult_cust_2024.xlsx, https://www.eia.gov/electricity/data/eia861m/archive/xls/sales_ult_cust_2025.xlsx, https://www.eia.gov/electricity/data/eia861m/xls/sales_ult_cust_2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T19:29:43Z, 2026-10-21T19:29:44Z, 2026-10-21T20:26:09Z, 2026-10-21T20:26:10Z, 2026-10-21T20:26:12Z, 2026-10-21T20:26:13Z, 2026-10-21T20:26:15Z, 2026-10-21T20:26:16Z, 2026-10-21T20:26:18Z, 2026-10-21T20:26:19Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1051488 |
| `x_utility_number` | EIA's utility number | none | integer | 84 to 67121; 369 distinct | 0 |
| `x_state` | The state, two-letter code | none | text | for example AK, AL, AR; 52 distinct | 0 |
| `x_ownership` | EIA's ownership type of the utility (Investor Owned, Cooperative, Municipal, Federal, State, Political Subdivision, Retail Power Marketer, Behind the Meter) | none | text | Behind the Meter, Cooperative, Federal, Investor Owned, Municipal, Political Subdivision, Retail Power Marketer, State | 2580: EIA leaves the ownership blank |
| `x_data_status` | EIA's data status: Final or Preliminary | none | text | Final, Preliminary | 0 |

Variables (15):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `commercial_customers` | Commercial customers | count | 70152 | 2017-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `commercial_revenue` | Revenue from commercial customers (EIA's thousand dollars times 1,000) | USD | 70147 | 2017-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `commercial_sales` | Retail sales to commercial customers | MWh | 70148 | 2017-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `industrial_customers` | Industrial customers | count | 70121 | 2017-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `industrial_revenue` | Revenue from industrial customers (EIA's thousand dollars times 1,000) | USD | 70109 | 2017-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `industrial_sales` | Retail sales to industrial customers | MWh | 70109 | 2017-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `residential_customers` | Residential customers | count | 69916 | 2017-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `residential_revenue` | Revenue from residential customers (EIA's thousand dollars times 1,000) | USD | 69905 | 2017-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `residential_sales` | Retail sales to residential customers | MWh | 69908 | 2017-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `total_customers` | Customers, all sectors | count | 70181 | 2017-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `total_revenue` | Revenue, all sectors (EIA's thousand dollars times 1,000) | USD | 70181 | 2017-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `total_sales` | Retail sales, all sectors | MWh | 70180 | 2017-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `transportation_customers` | Transportation customers | count | 70143 | 2017-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `transportation_revenue` | Revenue from transportation customers (EIA's thousand dollars times 1,000) | USD | 70145 | 2017-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `transportation_sales` | Retail sales to transportation customers | MWh | 70143 | 2017-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `elexon_gb_demand_daily`

Great Britain's Initial National Demand Outturn summed over one settlement day, from Elexon's BMRS.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1932.

- **Time:** ts_utc is the settlement day at 00:00:00Z (Decision 11), the day being Great Britain's own (Europe/London); freq P1D.
- **Revisions:** Merged by (entity, variable, ts_utc): each run's days replace the same days and older ones are kept; vintage is not filled (x_publish_time holds Elexon's publication time).
- **Source:** elexon:indod Elexon Limited, Balancing Mechanism Reporting Service (BMRS), Insights API, demand/outturn/daily (INDOD) (https://bmrs.elexon.co.uk/)
- **Method note:** [`docs/methods/elexon_gb_demand_daily.md`](../methods/elexon_gb_demand_daily.md)
- **Cite as:** Elexon Limited (BMRS). Balancing Mechanism Reporting Service, Initial National Demand Outturn per day (INDOD). Via the Energy Research Warehouse (ERW), table `elexon_gb_demand_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: elexon:GB on every row | none | text | elexon:GB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2021-04-27T00:00:00Z to 2026-10-23T00:00:00Z; 1932 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 395760.0 to 909318.0; 1928 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: GB on every row | none | text | GB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1932 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Great Britain on every row, not a pricing node | none | text | Great Britain | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | elexon:indod | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://data.elexon.co.uk/bmrs/api/v1/demand/outturn/daily?settlementDateFrom=2020-01-01&settlementDateTo=2021-12-31&format=csv, https://data.elexon.co.uk/bmrs/api/v1/demand/outturn/daily?settlementDateFrom=2022-01-01&settlementDateTo=2023-12-31&format=csv, https://data.elexon.co.uk/bmrs/api/v1/demand/outturn/daily?settlementDateFrom=2024-01-01&settlementDateTo=2025-12-31&format=csv, https://data.elexon.co.uk/bmrs/api/v1/demand/outturn/daily?settlementDateFrom=2026-01-01&settlementDateTo=2026-10-23&format=csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T00:17:29Z, 2026-10-24T00:17:30Z, 2026-10-24T00:17:31Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1932 |
| `x_settlement_date` | The settlement day as Elexon gives it | none | date | 2021-04-27 to 2026-10-23; 1932 distinct | 0 |
| `x_publish_time` | Elexon's publication time of the day's figure, UTC (the source's name: PublishTime) | none | utc time | 2021-04-27T23:15:00Z to 2026-10-23T23:15:00Z; 1932 distinct | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `indo_daily` | Initial national demand outturn (INDO) summed over the day's half hours, excluding station transformer, pumping and interconnector export demand | MWh | 1932 | 2021-04-27T00:00:00Z | 2026-10-23T00:00:00Z |

### `emi_nz_generation_demand_monthly`

New Zealand's, the North Island's or the South Island's grid generation or demand in one month, from the Electricity Authority's EMI reports.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 846.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; from 2015-01.
- **Revisions:** Rewritten whole as one snapshot by each run from EMI's two reports; vintage is not filled.
- **Source:** emi:generation_demand_trends Electricity Authority (New Zealand), Electricity Market Information, reports Generation trends (W_GG_C) and Demand trends (W_GD_C) (https://www.emi.ea.govt.nz/Wholesale/Reports)
- **Method note:** [`docs/methods/emi_nz_generation_demand_monthly.md`](../methods/emi_nz_generation_demand_monthly.md)
- **Cite as:** Electricity Authority (New Zealand). EMI reports: Generation trends (W_GG_C) and Demand trends (W_GD_C), monthly. Via the Energy Research Warehouse (ERW), table `emi_nz_generation_demand_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: emi:nz (New Zealand), emi:ni (North Island) or emi:si (South Island) | none | text | emi:ni, emi:nz, emi:si | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-09-01T00:00:00Z; 141 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1087959.0 to 4136646.0; 846 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: NZ on every row, island rows included | none | text | NZ | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 846 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: EMI's region name, not a pricing node | none | text | New Zealand, North Island, South Island | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | emi:generation_demand_trends | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.emi.ea.govt.nz/Wholesale/Download/DataReport/CSV/W_GD_C?DateFrom=20150101&DateTo=20260930&RegionType=ISLAND&TimeScale=MONTH&_si=v\|3, https://www.emi.ea.govt.nz/Wholesale/Download/DataReport/CSV/W_GD_C?DateFrom=20150101&DateTo=20260930&RegionType=NZ&TimeScale=MONTH&_si=v\|3, https://www.emi.ea.govt.nz/Wholesale/Download/DataReport/CSV/W_GG_C?DateFrom=20150101&DateTo=20260930&RegionType=ISLAND&TimeScale=MONTH&Show=Gwh&_si=v\|3, https://www.emi.ea.govt.nz/Wholesale/Download/DataReport/CSV/W_GG_C?DateFrom=20150101&DateTo=20260930&RegionType=NZ&TimeScale=MONTH&Show=Gwh&_si=v\|3 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T03:54:31Z, 2026-10-24T03:55:34Z, 2026-10-24T03:55:38Z, 2026-10-24T03:55:42Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 846 |
| `x_region_id` | EMI's region id: NZ, NI or SI | none | text | NI, NZ, SI | 0 |
| `x_report` | EMI's report code: W_GG_C generation trends, W_GD_C demand trends | none | text | W_GD_C, W_GG_C | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `demand` | Grid demand in the month (report W_GD_C; EMI's GWh times 1,000) | MWh | 423 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `generation` | Grid generation in the month (report W_GG_C; EMI's GWh times 1,000) | MWh | 423 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `energinet_dk_production_hourly`

One Danish price area's (DK1 or DK2) value of one production, consumption or exchange measure in one hour, from Energinet's settlement data.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 607311.

- **Time:** ts_utc is the hour's start in UTC (Energinet's HourUTC); freq PT1H; x_hour_dk is the same hour in Danish time.
- **Revisions:** Merged by (entity, variable, ts_utc): each run's hours replace the same hours (settlement data revised for up to two years) and older ones are kept; vintage is the answer's Last-Modified.
- **Source:** energinet:production_consumption_settlement Energinet, Energi Data Service, Production and Consumption - Settlement (https://www.energidataservice.dk/tso-electricity/ProductionConsumptionSettlement)
- **Method note:** [`docs/methods/energinet_dk_production_hourly.md`](../methods/energinet_dk_production_hourly.md)
- **Cite as:** Energinet (Energi Data Service). Energi Data Service, Production and Consumption - Settlement (ProductionConsumptionSettlement). Via the Energy Research Warehouse (ERW), table `energinet_dk_production_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: energinet:DK1 or energinet:DK2, the price area | none | text | energinet:DK1, energinet:DK2 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2024-12-31T23:00:00Z to 2026-10-13T23:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -3472.49 to 4870.058475; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: DK on every row | none | text | DK | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 607311 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The price area (DK1 or DK2), not a pricing node | none | text | DK1, DK2 | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | energinet:production_consumption_settlement | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.energidataservice.dk/dataset/ProductionConsumptionSettlement?start=2025-01-01T00:00&end=2026-10-15T00:00&limit=0&sort=HourUTC%20ASC | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T01:51:11Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The API answer's Last-Modified (UTC) | none | utc time | 2026-10-24T01:51:12Z | 0 |
| `x_hour_dk` | The hour in Danish local time (Energinet's HourDK) (the source's name: HourDK) | none | text | for example 2025-01-01T00:00:00, 2025-01-01T01:00:00, 2025-01-01T02:00:00; more than 5000 distinct | 0 |

Variables (21):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `central_power` | Energinet's CentralPowerMWh: production by central power plants | MWh | 31250 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `commercial_power` | Energinet's CommercialPowerMWh: commercial power production | MWh | 31250 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `commercial_power_self_con` | Energinet's LocalPowerSelfConMWh: self-consumption of local power, very uncertain by Energinet's word; ends 1 September 2026 | MWh | 29186 | 2024-12-31T23:00:00Z | 2026-08-31T23:00:00Z |
| `exchange_gb` | Exchange with Great Britain (negative an export) | MWh | 15625 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `exchange_ge` | Exchange with Germany (negative an export) | MWh | 31250 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `exchange_great_belt` | Exchange over the Great Belt link between DK1 and DK2 (negative an export) | MWh | 31250 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `exchange_nl` | Exchange with the Netherlands (negative an export) | MWh | 15625 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `exchange_no` | Exchange with Norway (negative an export) | MWh | 15625 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `exchange_se` | Exchange with Sweden (negative an export) | MWh | 31250 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `gross_consumption` | Gross consumption: Energinet's sum of production and exchange | MWh | 31250 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `hydro_power` | Hydro power production | MWh | 31250 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `local_power` | Energinet's LocalPowerMWh: production by local power plants | MWh | 31250 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `offshore_wind_ge100mw` | Offshore wind production, turbines of 100 MW or more | MWh | 31250 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `offshore_wind_lt100mw` | Offshore wind production, turbines under 100 MW | MWh | 31250 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `onshore_wind_ge50kw` | Onshore wind production, turbines of 50 kW or more | MWh | 31250 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `onshore_wind_lt50kw` | Onshore wind production, turbines under 50 kW | MWh | 31250 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `solar_power_ge10lt40kw` | Solar power production, installations of 10 to 40 kW | MWh | 31250 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `solar_power_ge40kw` | Solar power production, installations of 40 kW or more | MWh | 31250 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `solar_power_lt10kw` | Solar power production, installations under 10 kW | MWh | 31250 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `solar_power_self_con` | Self-consumption of solar power | MWh | 31250 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |
| `unknown_prod` | Production of unknown type | MWh | 31250 | 2024-12-31T23:00:00Z | 2026-10-13T23:00:00Z |

### `epe_brazil_consumption_monthly`

One Brazilian state's electricity consumption or consumers in one market class (captive or free) and sector in one month, from EPE's Statistical Yearbook raw data.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 105032.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; 2011-01 to 2025-12.
- **Revisions:** Rewritten whole as one snapshot by each run from EPE's workbook; vintage is the workbook's Last-Modified.
- **Source:** epe:anuario_dados_brutos EPE, Dados do Anuario Estatistico de Energia Eletrica, Dados Brutos (https://www.epe.gov.br/pt/publicacoes-dados-abertos/dados-abertos/dados-do-anuario-estatistico-de-energia-eletrica)
- **Method note:** [`docs/methods/epe_brazil_consumption_monthly.md`](../methods/epe_brazil_consumption_monthly.md)
- **Cite as:** Empresa de Pesquisa Energetica (EPE). Statistical Yearbook of Electricity, raw data (Dados Brutos). Via the Energy Research Warehouse (ERW), table `epe_brazil_consumption_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: epe:br:<state>:<captive or free>:<sector> | none | text | for example epe:br:ac:captive:comercial, epe:br:ac:captive:consumo_proprio, epe:br:ac:captive:iluminacao_publica; 354 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2011-01-01T00:00:00Z to 2025-12-01T00:00:00Z; 180 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -4093.602 to 19782929.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: BR-<state> | none | text | for example BR-AC, BR-AL, BR-AM; 27 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 105032 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The state, class and sector as EPE names them in Portuguese, not a pricing node | none | text | for example AC: Cativo: Comercial, AC: Cativo: Consumo Próprio, AC: Cativo: Iluminação Pública; 354 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epe:anuario_dados_brutos | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/dados-abertos/Documents/Dados%20brutos.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T11:53:13Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's Last-Modified (UTC) | none | utc time | 2026-06-03T16:54:55Z | 0 |
| `x_rows` | The number of EPE's rows summed into the value (over system, the sector's lower levels, voltage and band) | count | integer | 1 to 57; 56 distinct | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumers` | Consumers in the month | count | 52537 | 2011-01-01T00:00:00Z | 2025-12-01T00:00:00Z |
| `consumption` | Electricity consumption in the month | MWh | 52495 | 2011-01-01T00:00:00Z | 2025-12-01T00:00:00Z |

### `epra_kenya_electricity_annual`

One fiscal year's value of one Kenyan generation capacity (by grid kind and technology) or electricity consumption (by customer category) measure, from EPRA's Energy and Petroleum Statistics Reports.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 129.

- **Time:** ts_utc is the fiscal year's 1 July at 00:00:00Z; freq P1Y; capacity as at 30 June.
- **Revisions:** Merged by (entity, variable, ts_utc): each run's rows replace the same keys and older ones are kept; vintage is the report's Last-Modified.
- **Source:** epra:energy_petroleum_statistics_report Energy and Petroleum Regulatory Authority (EPRA), Energy and Petroleum Statistics Reports for the fiscal years 2023/24, 2024/25 and 2025/26, tables 2.1 and 2.2 (https://www.epra.go.ke/index.php/statistics-0)
- **Method note:** [`docs/methods/epra_kenya_electricity_annual.md`](../methods/epra_kenya_electricity_annual.md)
- **Cite as:** Energy and Petroleum Regulatory Authority, Kenya (EPRA). Energy and Petroleum Statistics Report (fiscal years 2023/24 to 2025/26), table 2.1 (installed, effective and captive capacity) and table 2.2 (consumption by customer category). Via the Energy Research Warehouse (ERW), table `epra_kenya_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: epra:KE on every row | none | text | epra:KE | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-07-01T00:00:00Z, 2024-07-01T00:00:00Z, 2025-07-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.1 to 12444710.0; 84 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: KE on every row | none | text | KE | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 129 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Kenya on every row, not a pricing node | none | text | Kenya | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epra:energy_petroleum_statistics_report | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epra.go.ke/sites/default/files/2024-10/EPRA%20Energy%20and%20Petroleum%20Statistics%20Report%20FY%202023-2024_2.pdf, https://www.epra.go.ke/sites/default/files/2025-09/Statistics-Report-June-2025-Web.pdf, https://www.epra.go.ke/sites/default/files/2026-09/Energy%20%26%20Petroleum%20Statistics%20Report%202026.pdf | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T07:11:19Z, 2026-10-24T07:12:01Z, 2026-10-24T07:12:08Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The report PDF's Last-Modified (UTC) | none | utc time | 2024-10-17T13:42:23Z, 2025-09-29T18:41:35Z, 2026-09-28T10:44:25Z | 0 |

Variables (43):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity_captive_bioenergy` | Captive capacity, bioenergy | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_captive_geothermal` | Captive capacity, geothermal | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_captive_hydro` | Captive capacity, hydro | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_captive_solar` | Captive capacity, solar | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_captive_thermal` | Captive capacity, thermal | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_captive_total` | Captive capacity, total | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_captive_waste_heat_recovery` | Captive capacity, waste heat recovery | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_interconnected_effective_bioenergy` | Effective capacity on the interconnected grid, bioenergy | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_interconnected_effective_geothermal` | Effective capacity on the interconnected grid, geothermal | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_interconnected_effective_hydro` | Effective capacity on the interconnected grid, hydro | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_interconnected_effective_imports` | Effective capacity on the interconnected grid, imports | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_interconnected_effective_solar` | Effective capacity on the interconnected grid, solar | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_interconnected_effective_thermal` | Effective capacity on the interconnected grid, thermal | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_interconnected_effective_total` | Effective capacity on the interconnected grid, total | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_interconnected_effective_wind` | Effective capacity on the interconnected grid, wind | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_interconnected_installed_bioenergy` | Installed capacity on the interconnected grid, bioenergy, as at 30 June | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_interconnected_installed_geothermal` | Installed capacity on the interconnected grid, geothermal | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_interconnected_installed_hydro` | Installed capacity on the interconnected grid, hydro | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_interconnected_installed_imports` | Installed capacity on the interconnected grid, imports | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_interconnected_installed_solar` | Installed capacity on the interconnected grid, solar | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_interconnected_installed_thermal` | Installed capacity on the interconnected grid, thermal | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_interconnected_installed_total` | Installed capacity on the interconnected grid, total | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_interconnected_installed_wind` | Installed capacity on the interconnected grid, wind | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_offgrid_hydro` | Off-grid capacity, hydro | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_offgrid_solar` | Off-grid capacity, solar | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_offgrid_thermal` | Off-grid capacity, thermal | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_offgrid_total` | Off-grid capacity, total | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_offgrid_wind` | Off-grid capacity, wind | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_total_installed_bioenergy` | Total installed capacity, bioenergy | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_total_installed_geothermal` | Total installed capacity, geothermal | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_total_installed_hydro` | Total installed capacity, hydro | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_total_installed_imports` | Total installed capacity, imports | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_total_installed_solar` | Total installed capacity, solar | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_total_installed_thermal` | Total installed capacity, thermal | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_total_installed_total` | Total installed capacity, all technologies | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_total_installed_waste_heat_recovery` | Total installed capacity, waste heat recovery | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `capacity_total_installed_wind` | Total installed capacity, wind | MW | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `consumption_domestic` | Electricity consumption by domestic customers in the fiscal year | MWh | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `consumption_e_mobility` | Electricity consumption by e-mobility in the fiscal year | MWh | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `consumption_industrial` | Electricity consumption by industrial customers in the fiscal year | MWh | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `consumption_small_commercial` | Electricity consumption by small commercial customers in the fiscal year | MWh | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `consumption_street_lighting` | Electricity consumption by street lighting in the fiscal year | MWh | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `consumption_total` | Electricity consumption, all categories, in the fiscal year | MWh | 3 | 2023-07-01T00:00:00Z | 2025-07-01T00:00:00Z |

### `fbos_fiji_electricity_annual`

Energy Fiji Limited's units produced or sold (in total or to one consumer class) in one year, from the Fiji Bureau of Statistics.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 83.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z; freq P1Y; 2011 to 2024.
- **Revisions:** Rewritten whole as one snapshot by each run from the two saved PDFs; vintage is not filled.
- **Source:** fbos:electricity Fiji Bureau of Statistics, Key Statistics table 3.7[A] and Economic Surveys: Electricity 2024, Appendix III (source: Energy Fiji Ltd)
- **Method note:** [`docs/methods/fbos_fiji_electricity_annual.md`](../methods/fbos_fiji_electricity_annual.md)
- **Cite as:** Fiji Bureau of Statistics (FBoS). Key Statistics table 3.7[A] and Electricity 2024 Appendix III (Energy Fiji Ltd's production and sales). Via the Energy Research Warehouse (ERW), table `fbos_fiji_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: fbos:fj:efl (units produced and sold) or fbos:fj:<consumer class> (units sold) | none | text | fbos:fj:commercial, fbos:fj:domestic, fbos:fj:efl, fbos:fj:industrial, fbos:fj:others | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 11800.0 to 1218906.0; 81 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: FJ on every row | none | text | FJ | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 83 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: FBoS's row label, not a pricing node | none | text | Commercial Sales, Units Sold (GWh), Domestic Sales, Units Sold (GWh), Industrial Sales, Units Sold (GWh), Others Sales, Units Sold (GWh), Units Produced (kwh), Units Sold (kwh) | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | fbos:electricity | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.statsfiji.gov.fj/download/138/table-3/827/3-7a_electricity.pdf, https://www.statsfiji.gov.fj/download/271/electricity/5954/2024-electricity.pdf | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T15:00:20Z, 2026-10-24T15:00:42Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 83 |
| `x_label` | FBoS's row label as printed (the same as node) | none | text | Commercial Sales, Units Sold (GWh), Domestic Sales, Units Sold (GWh), Industrial Sales, Units Sold (GWh), Others Sales, Units Sold (GWh), Units Produced (kwh), Units Sold (kwh) | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `generation` | Units produced by Energy Fiji Limited in the year | MWh | 14 | 2011-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `sales` | Units sold in the year, in total or to the consumer class (industrial, commercial, domestic, others) | MWh | 69 | 2011-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `fema_disaster_declarations`

One FEMA disaster declaration for one designated area (a county, a tribal area or a statewide area), declared on or after 2015-01-01, from OpenFEMA.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 26199.

- **Time:** event_date is the declaration date; x_incident_begin and x_incident_end are the incident's UTC days.
- **Revisions:** Rewritten whole as one snapshot by each run from OpenFEMA's CSV; vintage is the file's Last-Modified (empty here: none was given).
- **Source:** fema:openfema_disaster_declarations_v2 Federal Emergency Management Agency (FEMA), OpenFEMA Dataset: Disaster Declarations Summaries - v2 (https://www.fema.gov/openfema-data-page/disaster-declarations-summaries-v2)
- **Method note:** [`docs/methods/fema_disaster_declarations.md`](../methods/fema_disaster_declarations.md)
- **Cite as:** Federal Emergency Management Agency (FEMA). OpenFEMA Dataset: Disaster Declarations Summaries - v2. Via the Energy Research Warehouse (ERW), table `fema_disaster_declarations`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: fema:<declaration>:<state and county FIPS>:<place code> | none | text | for example fema:DR-4205-MS:28091:99091, fema:DR-4206-CA:06000:72468, fema:DR-4207-VT:50001:99001; more than 5000 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2015-01-07 to 2026-10-17; 1004 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: major_disaster, emergency or fire_management | none | text | emergency, fire_management, major_disaster | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: FEMA on every row | none | text | FEMA | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons. Here: US-<state>, and fips:<state><county> where FEMA names a county | none | text | for example US-AK, US-AK;fips:02013, US-AK;fips:02016; 3277 distinct | 0 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 26199 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 26199 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 26199 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: open, or closed where FEMA gives a closeout date | none | text | closed, open | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | fema:openfema_disaster_declarations_v2 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries.csv | 0 |
| `x_incident_type` | FEMA's incident type (Hurricane, Severe Storm, Flood, Fire, Biological and others) (the source's name: incidentType) | none | text | Biological, Chemical, Coastal Storm, Dam/Levee Break, Earthquake, Fire, Flood, Hurricane, Mud/Landslide, Other, Severe Ice Storm, Severe Storm, Snowstorm, Straight-Line Winds, Tornado, Toxic Substances, Tropical Depression, Tropical Storm, Typhoon, Volcanic Eruption, Winter Storm | 0 |
| `x_title` | The declaration's title as FEMA writes it (the source's name: declarationTitle) | none | text | for example 0419 FIRE, 1170 ROAD FIRE, 141ST FIRE; 797 distinct | 0 |
| `x_state` | The state or territory, two-letter code (the source's name: state) | none | text | for example AK, AL, AR; 56 distinct | 0 |
| `x_designated_area` | The designated area as FEMA writes it (a county, parish, tribal area or statewide) (the source's name: designatedArea) | none | text | for example Abbeville (County), Absentee Shawnee-Citizens Band of Potawatomi (TJSA), Acadia (Parish); 2902 distinct | 0 |
| `x_incident_begin` | The incident's first day, UTC (the source's name: incidentBeginDate) | none | date | 2014-04-25 to 2026-10-16; 914 distinct | 0 |
| `x_incident_end` | The incident's last day, UTC (the source's name: incidentEndDate) | none | date | 2014-12-06 to 2026-10-15; 898 distinct | 280: FEMA gives no end date |
| `x_programs` | The assistance programs declared, joined by ; (IH individuals and households, IA individual assistance, PA public assistance, HM hazard mitigation) | none | text | HM, IH, IH;HM, IH;PA, IH;PA;HM, PA, PA;HM | 0 |
| `x_disaster_number` | FEMA's disaster number (the source's name: disasterNumber) | none | integer | 3372 to 5679; 1634 distinct | 0 |
| `x_region` | The FEMA region, 1 to 10 (the source's name: region) | none | integer | 1, 10, 2, 3, 4, 5, 6, 7, 8, 9 | 0 |
| `x_tribal` | 1 for a tribal request, else 0 (the source's name: tribalRequest) | none | integer | 0, 1 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T19:55:36Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 26199 |

### `fhwa_motor_fuel_monthly`

The gallons of gasoline or of special fuels one state reports taxed in one month, from FHWA's Monthly Motor Fuel source data.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 7998.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; from 2020-01.
- **Revisions:** Rewritten whole as one snapshot by each run from the two files fetched fresh, so FHWA's revisions are taken; vintage is each file's Last-Modified.
- **Source:** fhwa:monthly_motor_fuel FHWA, Monthly Motor Fuel Report source data, DOT DataHub (https://data.transportation.gov/stories/s/nrec-wf7k)
- **Method note:** [`docs/methods/fhwa_motor_fuel_monthly.md`](../methods/fhwa_motor_fuel_monthly.md)
- **Cite as:** U.S. Department of Transportation, Federal Highway Administration (FHWA). Monthly Motor Fuel: Gasoline Volumes Distributed; Special Fuel Volumes Distributed (DOT DataHub). Via the Energy Research Warehouse (ERW), table `fhwa_motor_fuel_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: fhwa_mf:<state postal code> | none | text | for example fhwa_mf:AK, fhwa_mf:AL, fhwa_mf:AR; 52 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2020-01-01T00:00:00Z to 2026-05-01T00:00:00Z; 77 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 663897 to 1325852618; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | gal | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> (50 states, DC, Puerto Rico) | none | text | for example US-AK, US-AL, US-AR; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 7998 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The place as FHWA names it, not a pricing node | none | text | for example Alabama, Alaska, Arizona; 52 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | fhwa:monthly_motor_fuel | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://data.transportation.gov/api/views/5n49-mh85/rows.csv?accessType=DOWNLOAD, https://data.transportation.gov/api/views/5qxh-t94v/rows.csv?accessType=DOWNLOAD | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T19:42:07Z, 2026-10-23T19:42:12Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's Last-Modified (UTC): the gasoline file or the special fuels file | none | utc time | 2026-09-29T21:01:49Z, 2026-09-29T21:04:18Z | 0 |
| `x_data_type` | The dataset's DATA TYPE: Actual, Estimate or Gas Holiday (Georgia's months its gasoline tax was suspended: the volumes still taxed) (the source's name: DATA TYPE) | none | text | Actual, Estimate, Gas Holiday | 0 |
| `x_date_modified` | The dataset's DATE MODIFIED as published (the source's name: DATE MODIFIED) | none | text | 04/15/2026 12:00:00 AM, 08/14/2026 12:00:00 AM, 09/18/2024 12:00:00 AM, 09/28/2026 12:00:00 AM, 12/14/2023 12:00:00 AM | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `gasoline_volume` | Gallons of gasoline the state reports taxed in the month | gal | 3999 | 2020-01-01T00:00:00Z | 2026-05-01T00:00:00Z |
| `special_fuel_volume` | Gallons of special fuels the state reports taxed in the month | gal | 3999 | 2020-01-01T00:00:00Z | 2026-05-01T00:00:00Z |

### `frb_treasury_yields`

One US Treasury maturity's market yield at constant maturity for one business day.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 5901.

- **Time:** ts_utc is the business day at 00:00:00Z; freq P1D.
- **Revisions:** Rewritten whole by each run (the whole history from 2019 is read each run, so revisions are picked up); vintage is not filled.
- **Source:** frb:h15_treasury_yields Board of Governors of the Federal Reserve System, H.15 Selected Interest Rates: market yield on U.S. Treasury securities at constant maturity, the Data Download Program's package Treasury Constant Maturities (daily) (https://www.federalreserve.gov/releases/h15/)
- **Method note:** [`docs/methods/frb_treasury_yields.md`](../methods/frb_treasury_yields.md)
- **Cite as:** Board of Governors of the Federal Reserve System. H.15 Selected Interest Rates: market yield on U.S. Treasury securities at constant maturity, the Data Download Program's package Treasury Constant Maturities (daily). Via the Energy Research Warehouse (ERW), table `frb_treasury_yields`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: frb:tcm_<maturity>, 2, 10 or 30 years | none | text | frb:tcm_10y, frb:tcm_2y, frb:tcm_30y | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-02T00:00:00Z to 2026-11-12T00:00:00Z; 1967 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.09 to 5.67; 535 distinct | 0 |
| `unit` | The unit of the row's value | none | text | pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5901 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The Federal Reserve Board's series identifier (H15/H15/RIFLGFCY<years>_N.B), not a pricing node | none | text | H15/H15/RIFLGFCY02_N.B, H15/H15/RIFLGFCY10_N.B, H15/H15/RIFLGFCY30_N.B | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | frb:h15_treasury_yields | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&series=bf17364827e38702b42a58cf8eaa3f78&lastobs=&from=01/01/2019&to=12/31/2099&filetype=csv&label=include&layout=seriescolumn | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-13T00:31:25Z, 2026-10-14T15:40:16Z, 2026-10-15T15:51:26Z, 2026-10-19T16:31:24Z, 2026-10-19T20:56:30Z, 2026-10-21T15:17:42Z, 2026-10-22T15:09:12Z, 2026-10-23T15:06:55Z, 2026-10-24T15:14:30Z, 2026-10-27T15:00:44Z, 2026-10-28T15:08:28Z, 2026-10-29T14:56:24Z, 2026-10-30T15:07:43Z, 2026-11-05T23:51:25Z, 2026-11-12T22:16:42Z, 2026-11-15T15:33:48Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5901 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `yield` | Market yield on US Treasury securities at constant maturity, quoted on an investment basis, percent a year | pct | 5901 | 2019-01-02T00:00:00Z | 2026-11-12T00:00:00Z |

### `frb_utility_output_monthly`

One month's seasonally adjusted industrial production index or capacity utilization of one G.17 series (electric and gas utilities and their parts, with total industry and energy for comparison), from the Federal Reserve's G.17 release.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 15365.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M.
- **Revisions:** Rewritten whole as one snapshot by each run: each release revises earlier months, and the table is the release read; vintage is not filled.
- **Source:** frb:g17 Board of Governors of the Federal Reserve System, G.17 Industrial Production and Capacity Utilization (https://www.federalreserve.gov/releases/g17/)
- **Method note:** [`docs/methods/frb_utility_output_monthly.md`](../methods/frb_utility_output_monthly.md)
- **Cite as:** Board of Governors of the Federal Reserve System. G.17 Industrial Production and Capacity Utilization. Via the Energy Research Warehouse (ERW), table `frb_utility_output_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: frb_g17:<G.17 series code> | none | text | frb_g17:B50001, frb_g17:B50089, frb_g17:G2211, frb_g17:G22111, frb_g17:G221111A4T8, frb_g17:G22112, frb_g17:G2211A2, frb_g17:G2212, frb_g17:N221111, frb_g17:N221112, frb_g17:N221113, frb_g17:N221114T8, frb_g17:N22112C, frb_g17:N22112M, frb_g17:N22112R, frb_g17:N2212C, frb_g17:N2212M, frb_g17:N2212R, frb_g17:N2212T | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1919-01-01T00:00:00Z to 2026-09-01T00:00:00Z; 1293 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 3.3284 to 271.2812; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | index, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 15365 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The series' title with its NAICS code, not a pricing node | none | text | Commercial and other electricity sales NAICS=22112pt., Commercial and other gas sales NAICS=2212pt., Electric and gas utilities NAICS=2211,2, Electric power generation NAICS=22111, Electric power generation, transmission, and distribution NAICS=2211, Electric power transmission, control, and distribution NAICS=22112, Energy, total, Fossil Fuel electric power generation NAICS=221112, Gas transmission NAICS=2212pt., Hydroelectric power generation NAICS=221111, Hydroelectric, renewables, and other NAICS=221111,4-8, Industrial electricity sales NAICS=22112pt., Industrial gas sales NAICS=2212pt., Natural gas distribution NAICS=2212, Nuclear electric power generation NAICS=221113, Renewables and other electric power generation NAICS=221114-8, Residential electricity sales NAICS=22112pt., Residential gas sales NAICS=2212pt., Total index | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | frb:g17 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.federalreserve.gov/releases/g17/ipdisk/ip_sa.txt, https://www.federalreserve.gov/releases/g17/ipdisk/utl_sa.txt | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T05:15:17Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 15365 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `production` | Industrial production index, seasonally adjusted, 2017 = 100 (never summed) | index | 12497 | 1919-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `utilization` | Capacity utilization, seasonally adjusted, percent of capacity | pct | 2868 | 1967-01-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `generation_outages_hourly`

Megawatts of generation out of service in one hour, for one SPP area by fuel or for CAISO by planned and forced, as each operator publishes it.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1173900.

- **Time:** ts_utc is the hour's start in UTC.
- **Revisions:** Merged by (entity, variable, ts_utc). SPP's hour is from the newest file of its operating day (or the day before for hours 0 to 2, Central); CAISO's from the prior trade date report. A day read again replaces the one held. vintage is not filled.
- **Source:** spp:CAP-GEN-OUTAGE Southwest Power Pool (SPP), Capacity of Generation on Outage, https://portal.spp.org/pages/capacity-of-generation-on-outage; caiso:CURTAILED-NONOP-GEN California Independent System Operator (CAISO), Curtailed and Non-Operational Generator Prior Trade Date Report (https://www.caiso.com/documents/curtailed-non-operational-generator-prior-trade-date-report-20261118.xlsx)
- **Method note:** [`docs/methods/grid_outages.md`](../methods/grid_outages.md)
- **Cite as:** CAISO; SPP. Via the Energy Research Warehouse (ERW), table `generation_outages_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:ISO, spp:SPP, spp:SWPW, spp:Total | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2016-10-07T05:00:00Z to 2026-11-21T05:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 47612.26; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-CA,US-NV | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1173900 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 1173900 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:CURTAILED-NONOP-GEN, spp:CAP-GEN-OUTAGE | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://portal.spp.org/file-browser-api/download/capacity-of-generation-on-outage?path=/2016/2016.zip, https://portal.spp.org/file-browser-api/download/capacity-of-generation-on-outage?path=/2017/2017.zip, https://portal.spp.org/file-browser-api/download/capacity-of-generation-on-outage?path=/2018/2018.zip; 2678 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-20T10:55:02Z to 2026-11-20T13:04:16Z; 2678 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1173900 |

Variables (13):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `outage_mw_coal` | SPP, coal megawatts out of service, MW | MW | 93123 | 2017-07-22T05:00:00Z | 2026-11-21T05:00:00Z |
| `outage_mw_forced` | CAISO, megawatts curtailed by forced outages, weighted by the part of the hour each covers, MW | MW | 47545 | 2021-06-17T07:00:00Z | 2026-11-19T07:00:00Z |
| `outage_mw_gas` | SPP, natural gas megawatts out of service, MW | MW | 93123 | 2017-07-22T05:00:00Z | 2026-11-21T05:00:00Z |
| `outage_mw_hydro` | SPP, hydro megawatts out of service, MW | MW | 93123 | 2017-07-22T05:00:00Z | 2026-11-21T05:00:00Z |
| `outage_mw_nuclear` | SPP, nuclear megawatts out of service, MW | MW | 93123 | 2017-07-22T05:00:00Z | 2026-11-21T05:00:00Z |
| `outage_mw_oil` | SPP, diesel fuel oil megawatts out of service, MW | MW | 93123 | 2017-07-22T05:00:00Z | 2026-11-21T05:00:00Z |
| `outage_mw_other` | SPP, other fuels' megawatts out of service, MW | MW | 93123 | 2017-07-22T05:00:00Z | 2026-11-21T05:00:00Z |
| `outage_mw_planned` | CAISO, megawatts curtailed by planned outages, weighted by the part of the hour each covers, MW | MW | 47545 | 2021-06-17T07:00:00Z | 2026-11-19T07:00:00Z |
| `outage_mw_solar` | SPP, solar megawatts out of service, MW | MW | 93123 | 2017-07-22T05:00:00Z | 2026-11-21T05:00:00Z |
| `outage_mw_total` | Megawatts out of service, all fuels (SPP Outaged MW; CAISO planned plus forced), MW | MW | 147580 | 2016-10-07T05:00:00Z | 2026-11-21T05:00:00Z |
| `outage_mw_waste_disposal` | SPP, waste disposal megawatts out of service, MW | MW | 93123 | 2017-07-22T05:00:00Z | 2026-11-21T05:00:00Z |
| `outage_mw_waste_heat` | SPP, waste heat megawatts out of service, MW | MW | 93123 | 2017-07-22T05:00:00Z | 2026-11-21T05:00:00Z |
| `outage_mw_wind` | SPP, wind megawatts out of service, MW | MW | 93123 | 2017-07-22T05:00:00Z | 2026-11-21T05:00:00Z |

### `gfz_kp_index_3h`

The planetary geomagnetic index Kp for one three-hour interval, from GFZ's file since 1932.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 277032.

- **Time:** ts_utc is the three-hour interval's start (00, 03, ..., 21 UTC); freq PT3H.
- **Revisions:** Rewritten whole as one snapshot by each run from GFZ's file; vintage is the file's Last-Modified; x_status marks preliminary intervals.
- **Source:** gfz:kp_ap_since_1932 GFZ Potsdam, Kp_ap_since_1932.txt, https://kp.gfz-potsdam.de/fileadmin/files_for_gfz_cms/Kp_ap_since_1932.txt (listed on (https://kp.gfz-potsdam.de/en/data)
- **Method note:** [`docs/methods/gfz_kp_index_3h.md`](../methods/gfz_kp_index_3h.md)
- **Cite as:** GFZ Helmholtz Centre for Geosciences (Potsdam). Geomagnetic Kp index (Kp and ap since 1932). Via the Energy Research Warehouse (ERW), table `gfz_kp_index_3h`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: gfz:kp on every row | none | text | gfz:kp | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1932-01-01T00:00:00Z to 2026-10-22T21:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 9.0; 28 distinct | 0 |
| `unit` | The unit of the row's value | none | text | index | 0 |
| `freq` | How long the interval of the row is | none | text | PT3H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: a planetary index | none | empty | no cell holds a value | 277032 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 277032 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: planetary on every row, not a pricing node | none | text | planetary | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | gfz:kp_ap_since_1932 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://kp.gfz-potsdam.de/fileadmin/files_for_gfz_cms/Kp_ap_since_1932.txt | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T23:17:02Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's Last-Modified (UTC) | none | utc time | 2026-10-22T23:52:43Z | 0 |
| `x_ap` | The interval's ap, GFZ's equivalent amplitude (unitless; times 2 nT, the disturbance at 50 degrees geomagnetic latitude) | index | integer | 0 to 400; 28 distinct | 0 |
| `x_status` | definitive or preliminary, GFZ's status of the interval | none | text | definitive, preliminary | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `kp` | The planetary geomagnetic index Kp in thirds (5- is 4.667, 5o 5.000, 5+ 5.333) | index | 277032 | 1932-01-01T00:00:00Z | 2026-10-22T21:00:00Z |

### `grid_all_alerts`

One grid alert, watch, emergency or disturbance report, from CAISO's emergencies, ERCOT's notices or DOE's OE-417 reports; derived.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 5397.

- **Time:** event_date is the date the source gives the event; x_start and x_end are the source's own start and end where printed.
- **Revisions:** Rebuilt whole from its three input tables at each run; an event's row follows its input table's row.
- **Source:** erw:grid_all_alerts ERW derived table (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_alerts.md)
- **Method note:** [`docs/methods/grid_alerts.md`](../methods/grid_alerts.md)
- **Cite as:** CAISO; ERCOT; U.S. Department of Energy (DOE). Via the Energy Research Warehouse (ERW), table `grid_all_alerts`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | none | text | for example caiso_awe:1998-05-30:alert:c7046d023c, caiso_awe:1998-07-26:alert:efb4878194, caiso_awe:1998-07-27:alert:4c4cdaae48; more than 5000 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 1998-05-30 to 2026-10-15; 2541 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others) | none | text | for example actual_physical_attack, actual_physical_attack_vandalism, actual_physical_event; 88 distinct | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | text | California ISO, ERCOT | 3313 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 5397 |
| `mw` | The capacity involved, in megawatts | MW | number | 0.0 to 160000.0; 357 distinct | 3525 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 5397 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 5397 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | active, cancelled, declared, ended, issued, restored | 694 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:grid_emergencies_history, doe:oe417, ercot:news_releases, ercot:operations_messages | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://doe417.pnnl.gov/summaries/2016_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2017_Annual_Summary.xls, https://doe417.pnnl.gov/summaries/2018_Annual_Summary.xls; 116 distinct | 0 |
| `x_input_table` | The ERW table the row comes from (caiso_grid_emergencies, ercot_grid_notices, doe_oe417_events) | none | text | caiso_grid_emergencies, doe_oe417_events, ercot_grid_notices | 0 |
| `x_grid` | The grid (caiso, ercot) or, for an OE-417 report, the NERC region as the report prints it | none | text | for example FRCC, MPCC, MRO; 34 distinct | 1058 |
| `x_kind` | The kind of alert in the source's own words (CAISO's label, ERCOT's headline label, OE-417's event type as published) | none | text | for example - Cyber event (information technology), - Failure at high voltage substation or switchyard, - Failure at high voltage substation or switchyard - Other; 313 distinct | 0 |
| `x_start` | The event's start as the source prints it | none | text | for example 2011-02-02, 2011-02-03, 2011-02-03 1201; 3532 distinct | 1347: the source prints no start |
| `x_end` | The event's end as the source prints it | none | text | for example - Unknown - Unknown, 2011-02-03 1200, 2011-02-04 1200; 2777 distinct | 1888: the source prints no end (ERCOT's notices print none) |
| `x_area` | The area the source names (CAISO's and ERCOT's region, OE-417's area affected) | none | text | for example Ada County, Idaho, AitkinCounty, Minnesota, Alabama; 1375 distinct | 0 |

### `hagstofa_iceland_power_annual`

Iceland's installed capacity or generation in public power plants in one year, from Statistics Iceland's table IDN02101.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 88.

- **Time:** ts_utc is the year's first day at 00:00:00Z; freq P1Y; 1976 to 2019; capacity at the year's end.
- **Revisions:** Rewritten whole as one snapshot by each run from one JSON-stat query; vintage is the answer's updated time.
- **Source:** hagstofa:IDN02101 Statistics Iceland (Hagstofa Islands), from the National Energy Authority (https://px.hagstofa.is/pxen/pxweb/en/Umhverfi/Umhverfi__4_orkumal__2_framleidslaognotkun/)
- **Method note:** [`docs/methods/hagstofa_iceland_power_annual.md`](../methods/hagstofa_iceland_power_annual.md)
- **Cite as:** Statistics Iceland (Hagstofa Islands). Table IDN02101: installed capacity and generation in public power plants. Via the Energy Research Warehouse (ERW), table `hagstofa_iceland_power_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: hagstofa:is on every row | none | text | hagstofa:is | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1976-01-01T00:00:00Z to 2019-01-01T00:00:00Z; 44 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 502.7 to 19828868.0; 87 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: IS on every row | none | text | IS | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 88 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The measure as Statistics Iceland names it, not a pricing node | none | text | Annual generation of energy, GWh, Installed capacity at end of period, MW | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | hagstofa:IDN02101 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://px.hagstofa.is/pxen/api/v1/en/Umhverfi/4_orkumal/2_framleidslaognotkun/IDN02101.px | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T10:14:30Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The JSON-stat answer's updated time (UTC) | none | utc time | 2015-12-10T10:41:00Z | 0 |
| `x_table` | Statistics Iceland's table code (IDN02101) | none | text | IDN02101 | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity` | Installed capacity of public power plants at the year's end | MW | 44 | 1976-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `generation` | Annual generation of public power plants (the table's GWh times 1,000) | MWh | 44 | 1976-01-01T00:00:00Z | 2019-01-01T00:00:00Z |

### `hagstova_faroe_electricity_annual`

SEV's electricity production from one source, or its sales to one consumer group, in one year, from Statistics Faroe Islands tables UO03020 and UO03030.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 421.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z; freq P1Y; 1990 to 2025.
- **Revisions:** Rewritten whole as one snapshot by each run from one JSON-stat query a table; vintage is not filled.
- **Source:** hagstova:UO03 Statistics Faroe Islands (Hagstova Foroya) (https://statbank.hagstova.fo/pxweb/en/H2/H2__UO__UO03/)
- **Method note:** [`docs/methods/hagstova_faroe_electricity_annual.md`](../methods/hagstova_faroe_electricity_annual.md)
- **Cite as:** Statistics Faroe Islands (Hagstova Foroya). Tables UO03020 (SEV's electricity production by source) and UO03030 (SEV's electricity sales by consumer group). Via the Energy Research Warehouse (ERW), table `hagstova_faroe_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: hagstova:fo:<source or consumer group> | none | text | hagstova:fo:biogas, hagstova:fo:finance_business_services, hagstova:fo:fisheries_aquaculture, hagstova:fo:households, hagstova:fo:hydro, hagstova:fo:production_construction, hagstova:fo:public_private_services, hagstova:fo:shops_hotels, hagstova:fo:solar, hagstova:fo:street_lights, hagstova:fo:thermal, hagstova:fo:tidal, hagstova:fo:total, hagstova:fo:total_sales, hagstova:fo:transport_communication, hagstova:fo:wind | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 36 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 506249.0; 419 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: FO on every row | none | text | FO | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 421 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The category as Statistics Faroe Islands names it, not a pricing node | none | text | Agric., fish. ind., aquac., ressource comp., Biogas, Finance, insurance a.o. industrial serv., Houses, apts, summer and boat houses, Hydro, Production and construction, Publ. and priv. serv., church., meet. h., etc., Shops, restaurants and hotels, etc., Solar PV, Street lights, Thermal, Tidal energy, Total, Total sale of electricity, Transport, mail, and communication, Wind | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | hagstova:UO03 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://statbank.hagstova.fo/api/v1/en/H2/UO/UO03/ork_elgerd.px, https://statbank.hagstova.fo/api/v1/en/H2/UO/UO03/ork_elsola.px | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T15:23:19Z, 2026-10-24T15:23:23Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 421 |
| `x_table` | The table's code: UO03020 (production by source) or UO03030 (sales by consumer group) | none | text | UO03020, UO03030 | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `generation` | SEV's electricity production from the source in the year (table UO03020) | MWh | 160 | 1990-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `sales` | SEV's electricity sales to the consumer group in the year (table UO03030) | MWh | 261 | 1997-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `hifld_transmission_lines`

One electric transmission line of 230 kV and above in HIFLD's Electric Power Transmission Lines layer.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 10692.

- **Time:** No time column; vintage is HIFLD's SOURCEDATE of the line (a date); the table is a snapshot as read on its retrieved_at.
- **Revisions:** One row a line, rewritten whole as one snapshot by each build; vintage holds HIFLD's source date.
- **Source:** hifld:transmission_lines Homeland Infrastructure Foundation-Level Data (HIFLD), Electric Power Transmission Lines (ORNL, NGA HSIP), as served by Penn State's PASDA: https://mapservices.pasda.psu.edu/server/rest/services/pasda/HIFLD_FEMA/MapServer/178/query where VOLTAGE>=230, in batches (sha256 ba039a3a2b7259dc6b474d2ffcf408f3bd3f628dfd7cab5ef5e7cf513094de10, saved at warehouse/raw/hifld_lines/20261120T024611Z/transmission.geojson) (https://mapservices.pasda.psu.edu/server/rest/services/pasda/HIFLD_FEMA/MapServer/178/query)
- **Method note:** [`docs/methods/map_layers.md`](../methods/map_layers.md)
- **Cite as:** Homeland Infrastructure Foundation-Level Data (HIFLD), served by Penn State PASDA. Electric Power Transmission Lines, HIFLD open data layer, PASDA map service HIFLD_FEMA layer 178. Via the Energy Research Warehouse (ERW), table `hifld_transmission_lines`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: hifld:transmission_line:<HIFLD ID> | none | text | for example hifld:transmission_line:100019, hifld:transmission_line:100024, hifld:transmission_line:100029; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: transmission_line on every row | none | text | transmission_line | 0 |
| `name` | The thing's name, as the publisher writes it. Here: <SUB_1> to <SUB_2> where HIFLD names both ends, else empty | none | text | for example 11TH AVENUE to STADIUM, 137TH AVENUE to NEWTON, 137TH AVENUE to UNKNOWN177419; more than 5000 distinct | 2355 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: a line crosses states | none | empty | no cell holds a value | 10692 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: The line's midpoint | degree | number | 17.94672 to 61.43109; more than 5000 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: The line's midpoint | degree | number | -150.54138 to -65.85667; more than 5000 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: Not filled: HIFLD gives no capacity | MW | empty | no cell holds a value | 10692 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: operating for HIFLD's IN SERVICE, under_construction for UNDER CONSTRUCTION, else empty (HIFLD's word in x_status) | none | text | operating, under_construction | 2382 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 10692 |
| `operator` | The operator or owner, as the publisher writes it. Here: HIFLD's OWNER as printed; empty where HIFLD prints NOT AVAILABLE | none | text | for example AEP, AEP TEXAS CENTRAL, AEP TEXAS CENTRAL CO.; 294 distinct | 1846 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | hifld:transmission_lines | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://mapservices.pasda.psu.edu/server/rest/services/pasda/HIFLD_FEMA/MapServer/178 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-20T02:48:53Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: HIFLD's SOURCEDATE, a date (YYYY-MM-DD) | none | date | 1996-01-01 to 2024-09-26; 752 distinct | 0 |
| `x_hifld_id` | HIFLD's ID of the line (the source's name: ID) | none | integer | 100019 to 400541; more than 5000 distinct | 0 |
| `x_voltage_kv` | The line's voltage as HIFLD prints it (the source's name: VOLTAGE) | kV | integer | 1000, 230, 232, 236, 238, 240, 245, 250, 273, 275, 287, 345, 348, 400, 450, 500, 765 | 0 |
| `x_volt_class` | HIFLD's voltage class: a kV range (220-287, 345, 500, 735 AND ABOVE) or DC (the source's name: VOLT_CLASS) | none | text | 220-287, 345, 500, 735 AND ABOVE, DC | 0 |
| `x_type` | HIFLD's line type: AC or DC, overhead or underground, as printed (the source's name: TYPE) | none | text | AC; OVERHEAD, AC; UNDERGROUND, DC; OVERHEAD, OVERHEAD | 2: HIFLD prints NOT AVAILABLE or nothing |
| `x_inferred` | HIFLD's INFERRED: whether the line's VOLTAGE and/or VOLT_CLASS were inferred (Y) or not (N); an inferred voltage was populated from an indirect source, by identifying substation bus connectivity from imagery, analysing the substation and transmission structures by algorithm, and/or applying expert or regional knowledge of transmission infrastructure (the dataset's ISO 19139 metadata, Oak Ridge National Laboratory, publication date 2024-09-30) (the source's name: INFERRED) | none | text | N, Y | 0 |
| `x_status` | HIFLD's status word as printed (IN SERVICE, INACTIVE, UNDER CONSTRUCTION) (the source's name: STATUS) | none | text | IN SERVICE, INACTIVE, UNDER CONSTRUCTION | 2367: HIFLD prints NOT AVAILABLE or nothing |
| `x_sub_1` | The substation HIFLD names at one end of the line (the source's name: SUB_1) | none | text | for example 11TH AVENUE, 137TH AVENUE, 230-KV WEST; 4622 distinct | 415: HIFLD prints NOT AVAILABLE or nothing |
| `x_sub_2` | The substation HIFLD names at the other end of the line (the source's name: SUB_2) | none | text | for example 11TH AVENUE, 3 MILE KNOLL, 40TH STREET; 3955 distinct | 2355: HIFLD prints NOT AVAILABLE or nothing |
| `x_length_km` | The drawn line's length on a sphere of radius 6,371.0088 km | km | number | 0.01 to 1359.74; more than 5000 distinct | 0 |
| `x_source` | HIFLD's SOURCE: the source HIFLD names for the line, as printed (the source's name: SOURCE) | none | text | for example Arizona Corporation Commission http://preview.tinyurl.com/nkregtd, California Energy Commission, California Energy Commission http://www.energy.ca.gov/maps/; 358 distinct | 0 |
| `x_source_date` | HIFLD's source date of the line (the source's name: SOURCEDATE) | none | date | 1996-01-01 to 2024-09-26; 752 distinct | 0 |
| `x_val_date` | HIFLD's validation date of the line (the source's name: VAL_DATE) | none | date | 2014-06-06 to 2024-08-02; 635 distinct | 0 |
| `x_raw_sha256` | The SHA-256 of the raw GeoJSON file the row was read from | none | text | ba039a3a2b7259dc6b474d2ffcf408f3bd3f628dfd7cab5ef5e7cf513094de10 | 0 |

### `ieso_generation_fuel_hourly`

Ontario's generation from one fuel (or the IESO's control actions line) in one hour, from the IESO's Generator Output by Fuel Type Hourly Report.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 371781.

- **Time:** ts_utc is the hour's start in UTC (the IESO's hour ending in Eastern Standard Time, all year); freq PT1H.
- **Revisions:** Rewritten whole as one snapshot by each run from the IESO's yearly files; vintage is each file's CreatedAt in UTC.
- **Source:** ieso:gen_output_by_fuel_hourly IESO, Generator Output by Fuel Type Hourly Report (https://reports-public.ieso.ca/public/GenOutputbyFuelHourly/)
- **Method note:** [`docs/methods/ieso_generation_fuel_hourly.md`](../methods/ieso_generation_fuel_hourly.md)
- **Cite as:** Independent Electricity System Operator (IESO), Ontario. Generator Output by Fuel Type Hourly Report. Via the Energy Research Warehouse (ERW), table `ieso_generation_fuel_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ieso:ontario on every row | none | text | ieso:ontario | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2020-01-01T05:00:00Z to 2026-10-23T04:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 12208.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: CA-ON on every row | none | text | CA-ON | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 371781 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The fuel as the IESO names it, not a pricing node | none | text | BIOFUEL, CONTROL ACTIONS, GAS, HYDRO, NUCLEAR, OTHER, SOLAR, WIND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ieso:gen_output_by_fuel_hourly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://reports-public.ieso.ca/public/GenOutputbyFuelHourly/PUB_GenOutputbyFuelHourly_2020.xml, https://reports-public.ieso.ca/public/GenOutputbyFuelHourly/PUB_GenOutputbyFuelHourly_2021.xml, https://reports-public.ieso.ca/public/GenOutputbyFuelHourly/PUB_GenOutputbyFuelHourly_2022.xml, https://reports-public.ieso.ca/public/GenOutputbyFuelHourly/PUB_GenOutputbyFuelHourly_2023.xml, https://reports-public.ieso.ca/public/GenOutputbyFuelHourly/PUB_GenOutputbyFuelHourly_2024.xml, https://reports-public.ieso.ca/public/GenOutputbyFuelHourly/PUB_GenOutputbyFuelHourly_2025.xml, https://reports-public.ieso.ca/public/GenOutputbyFuelHourly/PUB_GenOutputbyFuelHourly_2026.xml | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T01:57:52Z, 2026-10-24T01:58:04Z, 2026-10-24T01:58:15Z, 2026-10-24T01:58:25Z, 2026-10-24T01:58:36Z, 2026-10-24T01:58:47Z, 2026-10-24T01:58:57Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The year's file's CreatedAt (UTC) | none | utc time | 2021-01-01T11:50:49Z, 2022-01-01T11:50:44Z, 2023-01-01T11:50:41Z, 2024-01-01T11:50:48Z, 2025-01-01T11:50:47Z, 2026-01-01T11:50:43Z, 2026-10-23T11:50:49Z | 0 |
| `x_quality` | The report's OutputQuality for the value, as published (codes not defined in the repository) (the source's name: OutputQuality) | none | integer | -1, -12, -2, -3, -30, -4, -5, -6, -7, -8, 0 | 0 |

Variables (8):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `control_actions` | The IESO's CONTROL ACTIONS line in the hour | MWh | 15 | 2026-07-15T14:00:00Z | 2026-07-16T04:00:00Z |
| `generation_biofuel` | Biofuel generation in the hour | MWh | 59688 | 2020-01-01T05:00:00Z | 2026-10-23T04:00:00Z |
| `generation_gas` | Gas generation in the hour | MWh | 59688 | 2020-01-01T05:00:00Z | 2026-10-23T04:00:00Z |
| `generation_hydro` | Hydro generation in the hour | MWh | 59688 | 2020-01-01T05:00:00Z | 2026-10-23T04:00:00Z |
| `generation_nuclear` | Nuclear generation in the hour (the report's Output) | MWh | 59688 | 2020-01-01T05:00:00Z | 2026-10-23T04:00:00Z |
| `generation_other` | Other generation in the hour | MWh | 13638 | 2025-04-02T18:00:00Z | 2026-10-23T04:00:00Z |
| `generation_solar` | Solar generation in the hour | MWh | 59688 | 2020-01-01T05:00:00Z | 2026-10-23T04:00:00Z |
| `generation_wind` | Wind generation in the hour | MWh | 59688 | 2020-01-01T05:00:00Z | 2026-10-23T04:00:00Z |

Waiting for a second look: x_quality (the report's OutputQuality): the codes 0 and -1 to -30 are not defined in the repository (the IESO's schema was not read). Read again on 20 November 2026 in the connector, the method note and the saved XML reports under warehouse/raw/ieso_genfuel (they point to the IESO's schema and stylesheet by address only, neither saved): not found..

### `ieso_ontario_demand_hourly`

Ontario's demand or market demand in one hour, from the IESO's Hourly Demand Report.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 31680.

- **Time:** ts_utc is the hour's start in UTC (the IESO's hour ending in Eastern Standard Time all year); freq PT1H.
- **Revisions:** Merged by (entity, variable, ts_utc): each run's hours replace the same hours and older ones are kept; vintage is the file's creation time.
- **Source:** ieso:demand Independent Electricity System Operator, Hourly Demand Report (https://reports-public.ieso.ca/public/Demand/)
- **Method note:** [`docs/methods/ieso_ontario_demand_hourly.md`](../methods/ieso_ontario_demand_hourly.md)
- **Cite as:** Independent Electricity System Operator (IESO), Ontario. Hourly Demand Report (PUB_Demand). Via the Energy Research Warehouse (ERW), table `ieso_ontario_demand_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ieso:ontario on every row | none | text | ieso:ontario | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-01-01T05:00:00Z to 2026-10-23T05:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 11536.0 to 27678.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: CA-ON on every row | none | text | CA-ON | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 31680 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Ontario on every row, not a pricing node | none | text | Ontario | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ieso:demand | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://reports-public.ieso.ca/public/Demand/PUB_Demand_2025.csv, https://reports-public.ieso.ca/public/Demand/PUB_Demand_2026.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T20:04:42Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The year's file's creation time (UTC) | none | utc time | 2026-01-31T12:30:13Z, 2026-10-23T12:30:09Z | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `market_demand` | Market demand: Ontario demand plus exports | MW | 15840 | 2025-01-01T05:00:00Z | 2026-10-23T05:00:00Z |
| `ontario_demand` | Ontario demand: the demand of Ontario's consumers | MW | 15840 | 2025-01-01T05:00:00Z | 2026-10-23T05:00:00Z |

### `ilr_luxembourg_electricity`

One month's or year's value of one Luxembourg electricity measure (withdrawals by customer class, generation, capacity, injection, trade, customers, self-consumption), from the regulator ILR's statistics workbook.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 668.

- **Time:** ts_utc is the month's or the year's first day at 00:00:00Z (customers at 31 December of the year); freq P1M or P1Y.
- **Revisions:** Rewritten whole as one snapshot by each run from ILR's workbook; vintage is the workbook's last-modified time; the current year's months carry x_status provisional.
- **Source:** ilr:donnees-statistiques-electricite ILR, Donnees statistiques du secteur d'electricite (Tableau de bord), data.public.lu (https://data.public.lu/fr/datasets/donnees-statistiques-du-secteur-delectricite-ilr/)
- **Method note:** [`docs/methods/ilr_luxembourg_electricity.md`](../methods/ilr_luxembourg_electricity.md)
- **Cite as:** Institut Luxembourgeois de Regulation (ILR). Donnees statistiques du secteur d'electricite (data.public.lu). Via the Energy Research Warehouse (ERW), table `ilr_luxembourg_electricity`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ilr:lu:<customer class, energy source or neighbour country> | none | text | ilr:lu:allemagne, ilr:lu:belgique, ilr:lu:biogaz, ilr:lu:biomasse, ilr:lu:clients_industriels_2gwh_an, ilr:lu:clients_professionnels_2gwh_an, ilr:lu:clients_residentiels, ilr:lu:cogeneration_a_gaz_naturel, ilr:lu:eolienne, ilr:lu:eolienne_nombre_de_pylones, ilr:lu:france, ilr:lu:hydroelectrique, ilr:lu:photovoltaique, ilr:lu:total, ilr:lu:usine_d_incineration | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2017-01-01T00:00:00Z to 2026-06-01T00:00:00Z; 114 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 4302310.735; 615 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, count | 0 |
| `freq` | How long the interval of the row is. Here: P1M for monthly withdrawals, P1Y for the annual blocks | none | text | P1M, P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: LU on every row | none | text | LU | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 668 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: ILR's label of the class, source or neighbour, in French, not a pricing node | none | text | Allemagne, Belgique, Biogaz, Biomasse, Clients industriels (>2GWh/an), Clients professionnels (≤2GWh/an), Clients résidentiels, Cogénération à gaz naturel, Eolienne, Eolienne (nombre de pylônes), France, Hydroélectrique, Photovoltaïque, Total, Usine d'incinération | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ilr:donnees-statistiques-electricite | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://download.data.public.lu/resources/donnees-statistiques-du-secteur-delectricite-ilr/20260901-135330/donnees-statistiques-du-secteur-delectricite.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T09:35:06Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time (UTC) | none | utc time | 2026-09-01T13:53:32Z | 0 |
| `x_block` | The sheet's number and the block's title, in French | none | text | 1. Electricité prélevée en kWh, 1. Nombre de clients au 31/12, 2. Nombre de raccordement d'installations de production par type, 2. Production nationale en kWh, 2. Puissance installée par source d'énergie en kW, 2. Volume injecté en kWh, 3. Nombre d'autoconsommateurs ou partageurs d'énergie, 3. Puissance installée des autoconsommateurs et groupes de partages en kW, 3. Volume autoconsommée ou partagé en KWh, 3. Volume injecté des autoconsommateurs et partageurs en KWh, 7. Données annuelles: Import - Export en kWh | 0 |
| `x_status` | provisional for the current year's months | none | text | provisional | 650: Not provisional |

Variables (12):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity` | Installed capacity of the energy source (kW / 1,000) | MW | 32 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `connections` | Production installations connected, by type | count | 28 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `customers` | Customers of the class at 31 December | count | 36 | 2017-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `export` | Electricity exported to the neighbour country in the year | MWh | 27 | 2017-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `generation` | National production from the energy source | MWh | 32 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `import` | Electricity imported from the neighbour country in the year | MWh | 27 | 2017-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `injection` | Volume injected into the grid from the energy source | MWh | 32 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `self_consumer_injection` | Electricity self-consumers injected into the grid | MWh | 26 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `self_consumers` | Self-consumers | count | 30 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `self_consumption` | Electricity self-consumed | MWh | 26 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `self_consumption_capacity` | Capacity of self-consumers' installations | MW | 30 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `withdrawal` | Electricity withdrawn from the grid by the customer class (kWh / 1,000) | MWh | 342 | 2017-01-01T00:00:00Z | 2026-06-01T00:00:00Z |

### `imf_commodity_prices`

One commodity's average price for one month, from the IMF's Primary Commodity Price System.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 752.

- **Time:** ts_utc is the first day of the month at 00:00:00Z; freq P1M; monthly averages, not daily prices.
- **Revisions:** Rewritten whole by each run (the whole history from 2019 is read each run, so revisions are picked up); vintage is not filled.
- **Source:** imf:pcps International Monetary Fund, Primary Commodity Price System (PCPS), monthly prices (https://www.imf.org/en/Research/commodity-prices)
- **Method note:** [`docs/methods/imf_commodity_prices.md`](../methods/imf_commodity_prices.md)
- **Cite as:** International Monetary Fund (IMF). Primary Commodity Price System (PCPS), monthly prices. Via the Energy Research Warehouse (ERW), table `imf_commodity_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: imf:PCPS:<IMF commodity code> | none | text | imf:PCPS:PCOALAU, imf:PCPS:PCOBA, imf:PCPS:PCOPP, imf:PCPS:PLITH, imf:PCPS:PNGASEU, imf:PCPS:PNGASJP, imf:PCPS:PNICK, imf:PCPS:PURAN | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-10-01T00:00:00Z; 94 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.46261232 to 490008.1789809524; 752 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MMBtu, USD/lb, USD/t | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 752 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 752 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The commodity in words, not a pricing node | none | text | Coal, Australia, Cobalt, Copper, LNG, Asia, Lithium, Natural gas, EU, Nickel, Uranium | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | imf:pcps | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.RES/PCPS/+/G001.PURAN+PLITH+PCOBA+PNICK+PCOPP+PCOALAU+PNGASEU+PNGASJP.USD.M?c[TIME_PERIOD]=ge:2019-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-14T10:45:40Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 752 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `price` | The IMF's average price of the commodity in the month, in US dollars per the row's unit (a metric ton; uranium a pound; gas and LNG an MMBtu) | USD/MMBtu; USD/lb; USD/t | 752 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |

Waiting for a second look: The header's title names uranium, lithium, cobalt, nickel and copper, but the table also holds coal (Australia), natural gas (EU) and LNG (Asia), as its access line asks for. Read again on 20 November 2026 in the saved request names under warehouse/raw/imf_pcps (from 14 November 2026 they ask PCOALAU, PNGASEU and PNGASJP beside the five metals): the title is still not updated, not found..

### `impact_tax_rules`

One tax rule the economic impact tool holds (a state's severance tax, fee or option on oil and gas, or a property tax rule for a generating project), or a record that no rule is held, each with its citation.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 130.

- **Time:** event_date is the effective date the citation gives where it gives one date, else the day the rule or statute was read or the repository searched (x_date_kind says which).
- **Revisions:** Rewritten whole as one snapshot by each run from the two record files; no page is read again.
- **Method note:** [`docs/methods/impact_tax_rules.md`](../methods/impact_tax_rules.md)
- **Cite as:** Energy Research Warehouse (ERW); Louisiana Department of Revenue; Louisiana State Legislature; New Mexico Taxation and Revenue Department; Texas Comptroller of Public Accounts; US state legislatures and tax agencies, as the forecast tool's property rules cite them. Crude Oil Production Tax; La. R.S. 47:633, Severance tax; rates; administration; Natural Gas Production Tax; New Mexico Oil and Gas Production tax rates for 04/01/2026 through 08/31/2026 by county and appropriate suffix (spreadsheet, revised); Oil & Gas Production Taxes; Revenue Information Bulletin No. 26-013 (June 2, 2026): Natural Gas Severance Tax Rate Effective July 1, 2026, through June 30, 2027; Revenue Information Bulletin No. 26-014 (August 3, 2026): Prices Applicable to Oil and Gas for Horizontal Wells, July 1, 2026 to June 30, 2027; Tax Credit for Qualifying Low-Producing Gas Wells; Tax Credit for Qualifying Low-Producing Oil Leases; The ERW's record that it holds no property-tax rule (session 346); The forecast tool's property tax rules (site/data/forecast/property_rules.json). Via the Energy Research Warehouse (ERW), table `impact_tax_rules`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: erw_tax:<state>:<rule> | none | text | for example erw_tax:ak:ak_note, erw_tax:al:al_note, erw_tax:ar:ar_note; 130 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 1951-09-01, 1953-08-27, 1969-10-01, 2026-09-30, 2026-10-20, 2026-11-13, 2026-11-14 | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: severance_tax, severance_fee, severance_option or property_tax_rule | none | text | property_tax_rule, severance_fee, severance_option, severance_tax | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: The citation's publisher, or the state on the forecast's property rules; empty on the no-rule rows | none | text | for example Alabama, Alaska, Arizona; 55 distinct | 7 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 130 |
| `mw` | The capacity involved, in megawatts. Here: Not filled: no cell holds a value | MW | empty | no cell holds a value | 130 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise. Here: Not filled: no cell holds a value | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 130 |
| `currency` | The currency of the price, as an ISO 4217 code (USD). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 130 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: held, or no_rule_held where the ERW holds no statute | none | text | held, no_rule_held | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:impact_tax_rules, forecast:property_rules, la_ldr:la_rib_26_013, la_ldr:la_rib_26_014, la_legislature:la_rs_47_633, nm_trd:nm_trd_rates_2026, nm_trd:nm_trd_taxes, tx_cpa:tx_cpa_gas, tx_cpa:tx_cpa_lp_gas, tx_cpa:tx_cpa_lp_oil, tx_cpa:tx_cpa_oil | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://apps.legislature.ky.gov/LAW/STATUTES/statute.aspx?id=53523, https://comptroller.texas.gov/taxes/crude-oil/, https://comptroller.texas.gov/taxes/crude-oil/low-producing-leases.php; 72 distinct | 0 |
| `x_state` | The state, two-letter code | none | text | for example AK, AL, AR; 51 distinct | 0 |
| `x_tax` | The tax: severance or property | none | text | property, severance | 0 |
| `x_product` | What the rule taxes: oil, gas or condensate (severance), a generating project (no-rule rows), or the technologies a property rule applies to, joined by ; | none | text | condensate, gas, generating_project, geothermal, land_based_wind, land_based_wind;natural_gas, land_based_wind;natural_gas;geothermal, land_based_wind;utility_pv, land_based_wind;utility_pv;geothermal, land_based_wind;utility_pv;natural_gas;geothermal, natural_gas, natural_gas;geothermal, oil, utility_pv, utility_pv;geothermal, utility_pv;land_based_wind, utility_pv;land_based_wind;geothermal, utility_pv;natural_gas;geothermal | 0 |
| `x_rule` | The rule's id in its record file (the source's name: id) | none | text | for example ak_note, al_note, ar_note; 130 distinct | 0 |
| `x_rule_name` | The rule's name (severance), or the title of the statute or page it cites (property) | none | text | for example Alabama Department of Revenue, Property Tax Assessment, Alaska Legislative Research Services, Report 21.028, Local Government in Alaska (11 December 2020), Arizona Revised Statutes 42-14155, Valuation of renewable energy and storage equipment; definitions; 105 distinct | 0 |
| `x_kind` | The kind of rule as its record names it (severance: base, fee, variant and option kinds such as credit_tier and per_unit; property: capacity, exempt_pct, own_exempt, note and others; no_rule_held) (the source's name: kind) | none | text | base, capacity, capacity_option, credit_tier, exempt_pct, exempt_years, fee, hcg_ratio, no_rule_held, note, own_exempt, per_unit, production, rate, rate_param, valuation, variant | 0 |
| `x_basis` | What the rate applies to: pct_value (a fraction of value), per_unit, or the basis a property rule names (the source's name: basis) | none | text | net acquisition cost, pct_value, per_unit | 113: The record gives no basis |
| `x_rate` | The rate: a fraction of value (0.046 for Texas oil), or with x_basis per_unit an amount a unit; variant or district where the rate is given elsewhere (the source's name: rate) | ratio, or USD per x_unit where x_basis is per_unit | text | 0, 0.0019, 0.0024, 0.013, 0.01565, 0.018925, 0.023, 0.03, 0.03125, 0.0315, 0.0375, 0.03785, 0.04, 0.046, 0.0625, 0.065, 0.075, 0.125, 0.1514, district, variant | 99: The rule has no single rate (a property rule, a note, a no-rule row) |
| `x_per_unit` | A fee per unit (Texas oil 0.00625 a bbl, gas 0.000667 a Mcf) (the source's name: per_unit) | USD per x_unit | number | 0.000667, 0.00625 | 128: The rule has no per-unit amount |
| `x_unit` | The unit of the per-unit amount or rate (bbl, Mcf) | none | text | Mcf, bbl | 127: The rule has no per-unit amount |
| `x_effective_text` | The citation's own words on when the rule is effective (the source's name: effective) | none | text | 1951-09-01, 1953-08-27, 1969-10-01, 2025-07-01 for the 6.5 percent rate (wells completed on or after that date), 2025-09-01 to 2026-08-31 (TRD table), 2026-04-01 to 2026-08-31 (TRD table), 2026-07-01 to 2027-06-30, report periods September 2015 and later | 116: The record gives no effective date |
| `x_date_kind` | Which date event_date is: the effective date the citation gives, the day the rule or statute was read, or the day the ERW recorded that it holds no rule | none | text | the day the ERW recorded that it holds no rule (2026-10-20), the day the rule was read (2026-09-30), the day the rule was read (2026-09-30); the citation's own words are in x_effective_text, the day the statute or agency page was read, the effective date the citation gives | 0 |
| `x_who` | Who or what the rule applies to, in words (the source's name: who) | none | text | A gas well whose production for the prior three months averages no more than 90 Mcf per day (flared gas excluded); Form AP-217. Casinghead gas and condensate are not eligible, A horizontally drilled well or horizontal recompletion producing on or after July 1, 2015, A well designated a gas well, incapable of producing an average of 250,000 cubic feet per day during the entire month, A well designated an orphan well for longer than 60 months, certified, A well designated an orphan well for longer than 60 months, certified by the Department of Conservation and Energy, A well drilled to a true vertical depth of more than 15,000 feet, production commencing after July 31, 1994, A well inactive for two years or more, or with 30 days or less of production in the past two years, certified by the Department of Conservation and Energy (applications July 1, 2018 to June 30, 2028), producing from the same interval, An EOR project whose carbon dioxide is captured from an anthropogenic source in Texas, would otherwise be released, is measurable at capture, and is sequestered in Texas, An oil lease whose production over a 90-day period averages less than 15 barrels per well per day, or less than 5 percent recoverable oil per barrel of produced water; Form AP-216, An oil well certified as incapable of more than 10 barrels per producing day for the entire month, An oil well certified by the Department of Revenue as incapable of more than 25 barrels per producing day for the entire month, producing at least 50 percent salt water per day; every well on a multiple-well lease must be certified, As for oil: inactive two years or more, certified, same interval, Gas condensate from a well drilled to a true vertical depth of more than 15,000 feet, production commencing after July 31, 1994, Gas from a gas well certified by the Railroad Commission; the rate depends on how the well's drilling and completion costs compare with the median cost of high-cost gas wells of the previous state fiscal year, Gas from a qualifying well consumed within 1,000 feet of the well that would otherwise have been lawfully vented or flared, Gas from a restimulation well certified by the Railroad Commission, Gas from a well certified as a two-year inactive well, Gas from a well designated an oil well with wellhead (or casinghead) pressure of 50 psig or less for the entire month; gas lift wells are presumed to qualify, Gas from an oil well, lawfully vented or flared, certified by the Railroad Commission, Oil from a well certified by the Railroad Commission as a two-year inactive well, Oil from an enhanced recovery project certified by the Texas Railroad Commission; a valid project number must be reported, Oil from an orphan well under R.S. 30:88.2(A) enhanced under a Department of Conservation and Energy permit (re-entry, workover, plugback), certified | 106: The record says nothing of it |
| `x_what` | What the rule gives, in words (the rate, or a property rule's explanation) (the source's name: what (severance); tip (property)) | none | text | for example 0.0 percent of market value, 1.3 cents per Mcf, 1.565 percent of value (3.125 percent if production commences on or after October 1, 2028); 99 distinct | 25: The record says nothing of it |
| `x_how_long` | How long the rule lasts, in words (the source's name: how_long) | none | text | 10 years beginning the first day of the month after the Railroad Commission certifies a positive production response (or, for an expansion, incremental production), 24 months from commercial production or until payout of the well cost, whichever comes first, 24 months from commercial production or until payout, whichever comes first, 24 months or until payout for wells completed before July 1, 2025; 18 months or until payout for wells completed on or after July 1, 2025, 24 months or until payout of the well cost, whichever comes first, As certified; the operator keeps the first three months' amount, Each month the pressure test is met, Each month the test is met, Each report month, while the lease qualifies and by the certified price, Each report month, while the well qualifies and by the certified price, Five years, Ten years, The first 120 consecutive calendar months from first production, or until the cumulative reduction equals 50 percent of the drilling and completion costs, whichever occurs first (wells spudded or completed after August 31, 1996), Until the 30th anniversary of the date the Comptroller first approves the application; the reduction is prorated to the anthropogenic share of the carbon dioxide used, Until the earlier of the last day of the 36th consecutive month after the well first produces following the restimulation treatment, or the date the exempted taxes (chapters 201 and 202) reach the lesser of the restimulation costs or $750,000, Until the well averages more than 10 barrels per day for an entire calendar month, While certified (by the 25th day of the second month after production) | 108: The record says nothing of it |
| `x_quote` | The cited page's own words stating the rule (the source's name: quote) | none | text | for example (1) for a large scale wind energy conversion system, .12 cents per kilowatt-hour of electricity produced by the system; (2) for a medium scale wind energy conversion system, .036 cents per kilowatt-hour of electricity produced by the system; and (3) for a small scale wind energy conversion system of two megawatts or less, but greater than .25 megawatts capacity, .012 cents per kilowatt-hour of electricity produced by the system., (1)(a) The owner of a renewable energy generation facility annually shall pay a nameplate capacity tax equal to the total nameplate capacity of the commissioned renewable energy generation facility multiplied by a tax rate of three thousand five hundred eighteen dollars per megawatt., (2) Except as provided in subsections (3), (4), and (5), the amount of the solar energy facilities tax, in each year after the facility is placed in service, is equal to $7,000.00 per megawatt of nameplate capacity, alternating current as reported on the annual form prescribed under section 8(1). (3) The amount of the specific tax as prescribed in subsection (2) must be reduced to $2,000.00 per megawatt of nameplate capacity, alternating current [...], for a qualified facility located on 1 or more of the following: (a) Property owned by this state [...] (b) Property located in an opportunity zone [...] (c) Property that was used or is currently used for commercial or industrial purposes and that is a facility, historic resource, functionally obsolete, or blighted [...] (d) Improved real property used for another purpose if the qualified facility is attached to the improvement.; 91 distinct | 31: No quote recorded for the row |
| `x_quote2` | A second quote from the cited page (the source's name: quote2) | none | text | for example "Nameplate capacity," the number of kilowatts a renewable facility can produce, as assigned to the power units in the renewable facility by the manufacturer and determined by the secretary; [...] "Wind farm," all real or personal property used or constructed for the purpose of producing electricity for commercial purposes utilizing the wind as an energy source and with a nameplate capacity of at least five thousand kilowatts., "large scale wind energy conversion system" means a wind energy conversion system of more than 12 megawatts, as measured by the nameplate capacity of the system, (a) Electrical Equipment 11% Includes the manufacture of electric household appliances, electronic equipment, batteries, ignition systems, and machinery used in the generation and utilization of electrical energy. [PT-300:] Schedule E: Leased Utility Real or personal property used by Water, Heat, Light, Solar, Power, Telephone, Cable Television, and Sewer Companies. [...] The SCDOR applies depreciation for all taxable properties in accordance with SC Code Section 12-37-930.; 31 distinct | 96: No second quote recorded |
| `x_code_section` | The statute section cited (property rules: the cited statute's or page's title) | none | text | for example Alabama Department of Revenue, Property Tax Assessment, Alaska Legislative Research Services, Report 21.028, Local Government in Alaska (11 December 2020), Arizona Revised Statutes 42-14155, Valuation of renewable energy and storage equipment; definitions; 75 distinct | 36: No statute recorded for the row |
| `x_code_quote` | The statute's own words | none | text | (f) "Qualified solar energy facility" or "qualified facility" means a facility, whether owned or leased, that when constructed and placed in service is located in a solar energy district and that uses or will use solar energy as the sole source for the generation of at least 2 megawatts of nameplate capacity, alternating current [...], Each month, the comptroller shall certify the average taxable price of gas, adjusted to 2005 dollars, during the previous three months, Each month, the comptroller shall certify the average taxable price of oil, adjusted to 2005 dollars, during the previous three months, Enclosed is a copy of the 2026 Trend and Percent Good Tables for Tax Year 2027, along with a detailed list of North American Industry Classification System (NAICS) codes. [...] 2211 Electric Power Generation, Transmission and Distribution 46 9 [...] PERCENT GOOD TABLE [...] pp09 [...] 30 YEARS: 2026 98.00, 2025 97.00, 2024 95.00 [...] 1995 20.00, 1994 20.00, F. Solar Energy Device 10-Year Age/Life Original Cost x Index Factor x %GD Schedule [...] Solar/Ind 10YR [...] 2025 92, 2024 84, 2023 76, 2022 67, 2021 58, 2020 49, 2019 39, 2018 30, 2017 24, 2016 21, 2015 20, Gas produced from a qualifying well that is consumed within 1,000 feet of the qualifying well and would otherwise have been lawfully vented or flared is not subject to the tax imposed by this chapter., Hydrocarbons produced from a well qualify for a five-year severance tax exemption if the commission designates the well as a two-year inactive well., TABLE 4: MACHINERY AND EQUIPMENT PERCENT GOOD FACTORS. Individual Properties - Average Service Life - 5.5% Rate of Return [...] 17: 96 91 87 82 77 72 68 63 58 53 48 43 38 34 30 26 23 19 16 14 12 10 9 7 5 3 1 [...] No minimum percent good factor is intended in this table., The amount of tax reduction shall be computed by subtracting from the tax rate imposed by Section 201.052 the product of that tax rate times the ratio of drilling and completion costs incurred for the well to twice the median drilling and completion costs for high-cost wells spudded or completed during the previous state fiscal year, except that the effective rate of tax may not be reduced below zero., The tax imposed by this chapter does not apply to gas: (1) injected into the earth in this state, unless sold for that purpose; (2) produced from oil wells with oil and lawfully vented or flared, The tax imposed by this chapter is at the rate of 4.6 percent of the market value of oil produced in this state or 4.6 cents for each barrel of 42 standard gallons of oil produced in this state, whichever rate results in the greater amount of tax., The tax imposed by this chapter is at the rate of 7.5 percent of the market value of gas produced and saved in this state by the producer., The tax imposed by this section is at the same rate as the rate of the tax imposed on oil by Section 202.052 of this code., the recovered oil tax rate applies to oil on which a tax is imposed by this chapter for the 10 years beginning the first day of the month following the date the commission certifies that, in the case of an enhanced recovery project including a co-production project, a positive production response has occurred, until the 30th anniversary of the date that the comptroller first approves an application for a tax rate reduction under this section, the producer of oil recovered through an enhanced oil recovery project that qualifies under Section 202.054 for the recovered oil tax rate provided by Section 202.052 (b) is entitled to an additional 50 percent reduction in that tax rate, until the earlier of: (1) the last day of the 36th consecutive month following the month in which the well first produces hydrocarbons after a restimulation treatment is completed; or (2) the date on which the cumulative amount of taxes exempted under Chapter 201 and this chapter and any credit under Subsection (l) equals the lesser of: (A) the restimulation costs described by Subsection (j); or (B) $750,000. | 113: No statute words recorded for the row |
| `x_code_url` | The statute's address (property rules: the further addresses cited) | none | text | https://boe.ca.gov/proptaxes/pdf/lta17020.pdf https://boe.ca.gov/meetings/pdf/2025/ah58126.pdf, https://comptroller.texas.gov/taxes/property-tax/docs/96-1569.pdf https://hcad.org/assets/uploads/pdf/resources/2026/2026-PP-Calc-Guide.pdf, https://dam.assets.ohio.gov/image/upload/v1739290822/tax.ohio.gov/forms/public_utility_property/2025/pupp-instructions.pdf, https://docs.legis.wisconsin.gov/document/statutes/70.112, https://dor.georgia.gov/document/document/lgsd-2024-001-amended-and-adopted-regulationspdf/download, https://dor.wa.gov/sites/default/files/2025-12/2026ValuationGuidelines.docx, https://legislature.mi.gov/Laws/MCL?objectName=mcl-211-1157 https://legislature.mi.gov/Laws/MCL?objectName=mcl-211-1152, https://revenue.ky.gov/Forms/61A200(P)(1-25).pdf, https://revenuefiles.mt.gov/property/personal-property/2026-Personal-Property-Depreciation-Schedules-and-Trend-Tables-v2.pdf, https://sdlegislature.gov/api/Statutes/10-35-16.html, https://statutes.capitol.texas.gov/Docs/TX/htm/TX.201.htm, https://statutes.capitol.texas.gov/Docs/TX/htm/TX.202.htm, https://tax.wv.gov/Documents/LegislativeRules/LegislativeRule.Title-110.Series-1M.pdf https://cabellassessor.com/Forms/TrendandPercentGoodTablesforTaxYear2027.pdf, https://www.flsenate.gov/Laws/Statutes/2025/193.624, https://www.scstatehouse.gov/code/t12c037, https://www.tax.newmexico.gov/businesses/wp-content/uploads/sites/4/2021/02/210-240-Electric.pdf, https://www.tn.gov/content/dam/tn/attorneygeneral/documents/ops/2013/op13-028.pdf | 98: No statute address recorded for the row |
| `x_detail` | Other fields of the rule's record, as JSON (tiers, bounds, district rates, exempt shares and others) | none | text | for example {"abates": "tax", "exempt_share": 0.55, "min_mw": 10, "requires": "option", "years": 20}, {"above_mw": 5, "below_mw": 150, "exempt_steps": [{"share": 0.8, "until": 5}, {"share": 0.7, "until": 10}, {"share": 0.6}]}, {"adds_to_property": true, "exempt_years": 3, "usd_per_mwh": 1.0}; 71 distinct | 43: The record holds no other field |
| `x_applies_to` | Which of the economic impact tool's technologies the rule applies to (severance rows: oil and gas production, which none of them produces) | none | text | every technology of the economic impact tool, geothermal, land_based_wind, land_based_wind;natural_gas, land_based_wind;natural_gas;geothermal, land_based_wind;utility_pv, land_based_wind;utility_pv;geothermal, land_based_wind;utility_pv;natural_gas;geothermal, natural_gas, natural_gas;geothermal, oil and gas production; none of the economic impact tool's technologies produces oil or gas, utility_pv, utility_pv;geothermal, utility_pv;land_based_wind, utility_pv;land_based_wind;geothermal, utility_pv;natural_gas;geothermal | 0 |
| `x_note` | Where the row was read from: the record file and its version, the day read, and what the forecast does not model | none | text | for example As site/data/forecast/property_rules.json holds it (version 2026-11-13); read 2026-11-13, As site/data/forecast/property_rules.json holds it (version 2026-11-13); read 2026-11-13, request 102; not modeled by the forecast: Payments by the state from its public utility account to the plant's municipality and county, USD 2,000 per MW shared (two thirds to a city or village and one third to its county, or one third to a town and two thirds to its county) plus USD 1,500 per MW to each: USD 5,000 per MW in all, in place of the property tax the plant does not pay. Not modeled: the caps on the shared part at USD 300 a resident of the municipality and USD 100 a resident of the county (79.04(6)(d)); the extra USD 900 per MW each for a plant on the site of an existing plant or a brownfield (7)(a); whether a given owner is taxed under s. 76.28 (79.04(6)(a)'s list of owners). A gas plant receives the shared USD 2,000 per MW and, as a baseload plant of 50 MW or more, USD 600 each (7)(b); "baseload" is not read, so no gas rule is held., As site/data/forecast/property_rules.json holds it (version 2026-11-13); read 2026-11-13, request 105; not modeled by the forecast: The abatement needs the Director's approval (jobs on the construction, a capital investment of USD 3 or 10 million, wages of 110 and 175 percent of the state's average, NRS 701A.365) and the county may deny it within 30 days: off by default. No rate is in the statute: the abatement acts on the reader's own rate. The 20 fiscal years run from the approval, taken as the first construction year. The partial abatement of local sales and use taxes above 0.6 percent for 3 years (701A.370(1)(b)) is not modeled. Eligibility needs a generating capacity of at least 10 MW (701A.360, read by the re-check of session 4291): held as the rule's minimum size.; 55 distinct | 0 |

### `ine_es_dwellings_electricity_2021`

One Spanish area's (nation, autonomous community, province or municipality) count of dwellings in one electricity use band, or its median annual consumption, from INE's 2021 census.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 58626.

- **Time:** ts_utc is 2021-01-01T00:00:00Z, the 2021 census; freq P1Y.
- **Revisions:** Rewritten whole as one snapshot by each run from INE's CSV; vintage is the file's Last-Modified.
- **Source:** ine_es:jaxi_tpx_59531 Instituto Nacional de Estadistica (INE), Censo de Poblacion y Viviendas 2021, Viviendas segun su intensidad de uso (viviendas por intensidad de uso a partir del consumo electrico), data updated 22 November 2024
- **Method note:** [`docs/methods/ine_es_dwellings_electricity_2021.md`](../methods/ine_es_dwellings_electricity_2021.md)
- **Cite as:** Instituto Nacional de Estadistica (INE), Spain. Censo de Poblacion y Viviendas 2021: Viviendas segun su intensidad de uso. Via the Energy Research Warehouse (ERW), table `ine_es_dwellings_electricity_2021`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ine_viv:es, ine_viv:ccaa_<code>, ine_viv:prov_<code> or ine_viv:mun_<code>, INE's codes | none | text | for example ine_viv:ccaa_01, ine_viv:ccaa_02, ine_viv:ccaa_03; 3257 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2021-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 26623708.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ES on every row, whatever the area | none | text | ES | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 58626 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: INE's area code and name with the measure in Spanish, not a pricing node | none | text | for example 01 Andalucía: Mediana consumo anual, 01 Andalucía: Viviendas con bajo consumo, 01 Andalucía: Viviendas con consumo entre 1.001 y 2.000 kwh; more than 5000 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ine_es:jaxi_tpx_59531 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ine.es/jaxi/files/tpx/es/csv_bdsc/59531.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T23:46:30Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The CSV's Last-Modified (UTC) | none | utc time | 2026-03-02T13:17:24Z | 0 |
| `x_level` | The area's level: nation, ccaa (autonomous community or city), province or municipality | none | text | ccaa, municipality, nation, province | 0 |

Variables (18):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dwellings_1001_2000_kwh` | Dwellings consuming 1,001 to 2,000 kWh a year | count | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `dwellings_2001_3000_kwh` | Dwellings consuming 2,001 to 3,000 kWh a year | count | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `dwellings_3001_4000_kwh` | Dwellings consuming 3,001 to 4,000 kWh a year | count | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `dwellings_4001_5000_kwh` | Dwellings consuming 4,001 to 5,000 kWh a year | count | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `dwellings_5001_6000_kwh` | Dwellings consuming 5,001 to 6,000 kWh a year | count | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `dwellings_6001_7000_kwh` | Dwellings consuming 6,001 to 7,000 kWh a year | count | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `dwellings_7001_8000_kwh` | Dwellings consuming 7,001 to 8,000 kWh a year | count | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `dwellings_751_1000_kwh` | Dwellings consuming 751 to 1,000 kWh a year | count | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `dwellings_8001_9000_kwh` | Dwellings consuming 8,001 to 9,000 kWh a year | count | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `dwellings_9001_10000_kwh` | Dwellings consuming 9,001 to 10,000 kWh a year | count | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `dwellings_empty` | Dwellings classed empty by their electricity consumption | count | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `dwellings_low_consumption` | Dwellings of low electricity consumption | count | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `dwellings_occasional_251_500_kwh` | Dwellings of occasional use, 251 to 500 kWh a year | count | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `dwellings_occasional_501_750_kwh` | Dwellings of occasional use, 501 to 750 kWh a year | count | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `dwellings_occasional_use` | Dwellings of occasional use, both bands | count | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `dwellings_over_10000_kwh` | Dwellings consuming over 10,000 kWh a year | count | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `dwellings_total` | Dwellings, total | count | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `median_annual_consumption` | Median annual electricity consumption per dwelling (INE's kWh / 1,000) | MWh | 3257 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |

### `irs_soi_energy_credits_annual`

One state's (or the US's, or SOI's other areas') returns claiming, or amount of, one residential energy credit in one tax year, from IRS Statistics of Income Historic Table 2.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1074.

- **Time:** ts_utc is the tax year's first day at 00:00:00Z; freq P1Y; tax years 2015 to 2023.
- **Revisions:** Rewritten whole as one snapshot by each run from SOI's yearly files; vintage is each file's Last-Modified.
- **Source:** irs:soi_historic_table_2 Internal Revenue Service, SOI Tax Stats, Historic Table 2 (https://www.irs.gov/statistics/soi-tax-stats-historic-table-2)
- **Method note:** [`docs/methods/irs_soi_energy_credits_annual.md`](../methods/irs_soi_energy_credits_annual.md)
- **Cite as:** Internal Revenue Service (IRS), Statistics of Income. SOI Tax Stats: Historic Table 2, individual income and tax data by state. Via the Energy Research Warehouse (ERW), table `irs_soi_energy_credits_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: irs_soi:<SOI's state code>; US is SOI's national row, OA its other areas | none | text | for example irs_soi:AK, irs_soi:AL, irs_soi:AR; 54 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 110 to 7983695000; 1047 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, US for the national row, empty for OA (other areas) | none | text | for example US, US-AK, US-AL; 53 distinct | 20 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1074 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: SOI's state code, not a pricing node | none | text | for example AK, AL, AR; 54 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | irs:soi_historic_table_2 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.irs.gov/pub/irs-soi/15in54cmcsv.csv, https://www.irs.gov/pub/irs-soi/16in54cmcsv.csv, https://www.irs.gov/pub/irs-soi/17in54cmcsv.csv, https://www.irs.gov/pub/irs-soi/18in55cmagi.csv, https://www.irs.gov/pub/irs-soi/19in55cmcsv.csv, https://www.irs.gov/pub/irs-soi/20in55cmcsv.csv, https://www.irs.gov/pub/irs-soi/21in55cmcsv.csv, https://www.irs.gov/pub/irs-soi/22in55cmcsv.csv, https://www.irs.gov/pub/irs-soi/23in55cmcsv.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T21:13:17Z, 2026-10-23T21:13:19Z, 2026-10-23T21:13:21Z, 2026-10-23T21:13:23Z, 2026-10-23T21:14:17Z, 2026-10-23T21:14:19Z, 2026-10-23T21:14:21Z, 2026-10-23T21:14:22Z, 2026-10-23T21:14:24Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The year's file's Last-Modified (UTC; one file gives 1970-01-01, an epoch time) | none | utc time | 1970-01-01T00:00:00Z, 2019-10-31T02:11:53Z, 2020-09-01T02:12:26Z, 2021-12-08T13:39:13Z, 2022-12-16T23:25:24Z, 2024-02-27T03:11:29Z, 2025-01-16T03:11:43Z, 2025-11-07T08:57:12Z, 2026-08-21T14:12:00Z | 0 |
| `x_soi_column` | SOI's column the value is read from (N07260, A07260, N07262, A07262, N07265, A07265: N a count of returns, A an amount) | none | text | A07260, A07262, A07265, N07260, N07262, N07265 | 0 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `energy_efficient_home_improvement_credit_amount` | Amount of the energy efficient home improvement credit (A07265, 2023) | USD | 54 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `energy_efficient_home_improvement_credit_returns` | Returns claiming the energy efficient home improvement credit (N07265, 2023) | count | 54 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `residential_clean_energy_credit_amount` | Amount of the residential clean energy credit (A07262, 2023) | USD | 54 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `residential_clean_energy_credit_returns` | Returns claiming the residential clean energy credit (N07262, 2023) | count | 54 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `residential_energy_credit_amount` | Amount of the residential energy credit (A07260, 2015 to 2022; SOI's thousands of dollars times 1,000) | USD | 429 | 2015-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `residential_energy_credit_returns` | Returns claiming the residential energy credit (N07260, 2015 to 2022) | count | 429 | 2015-01-01T00:00:00Z | 2022-01-01T00:00:00Z |

### `miso_interconnection_queue`

One position in MISO's generator interconnection queue, as held on 30 September 2026 (MISO pulls paused since 4 October 2026).

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 3881.

- **Time:** No time column; queue_date, proposed_in_service_date and withdrawn_date are the ISO's dates (YYYY-MM-DD); vintage is the snapshot's time.
- **Revisions:** A snapshot: a run replaces the whole table; MISO pulls are paused, so the table holds the queue as of 30 September 2026, rebuilt from the archive.
- **Source:** miso:interconnection_queue MISO Generator Interconnection Queue (giqueue API) (https://www.misoenergy.org/api/giqueue/getprojects)
- **Method note:** [`docs/methods/miso_interconnection_queue.md`](../methods/miso_interconnection_queue.md)
- **Cite as:** Midcontinent Independent System Operator (MISO). Generator Interconnection Queue (giqueue API) [PAUSED 2026-10-04: MISO's terms forbid automated access; pulls paused pending a review of MISO's terms by a person (docs/methods/miso_pause.md)]. Via the Energy Research Warehouse (ERW), table `miso_interconnection_queue`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: miso_queue:<project number> | none | text | for example miso_queue:J1000, miso_queue:J1001, miso_queue:J1002; 3881 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: project on every row | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it. Here: Empty on every row | none | empty | no cell holds a value | 3881 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> where MISO gives a state, else empty | none | text | US-AK, US-AR, US-IA, US-IL, US-IN, US-KY, US-LA, US-MI, US-MN, US-MO, US-MS, US-MT, US-ND, US-SD, US-TX, US-WI | 211 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 3881 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 3881 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: The larger of MISO's summer and winter net MW, as gridstatus reads it | MW | number | 0.0 to 2220.0; 535 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: active (Active, Pending Revision Approval, Pending Transfer), completed (Done, LEGACY: Done) or withdrawn, from iso_status | none | text | active, completed, withdrawn | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The withdrawn date of a withdrawn row; no completed row has one | none | date | 2017-02-17 to 2026-09-18; 429 distinct | 1755 |
| `operator` | The operator or owner, as the publisher writes it. Here: Empty on every row | none | empty | no cell holds a value | 3881 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | miso:interconnection_queue | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.misoenergy.org/api/giqueue/getprojects | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-30T23:33:22Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: 2026-09-30T00:00:00Z, a timestamp, where other queues carry a day | none | utc time | 2026-09-30T00:00:00Z | 0 |
| `queue_id` | MISO's project number of the request (the source's name: Queue ID) | none | text | for example J1000, J1001, J1002; 3880 distinct | 0 |
| `county` | The county of the project as MISO writes it (the source's name: County) | none | text | for example Acadia, Acadia Parish, Adair; 776 distinct | 175: MISO gives no county |
| `state` | The state of the project, two-letter code (the source's name: State) | none | text | AK, AR, IA, IL, IN, KY, LA, MI, MN, MO, MS, MT, ND, SD, TX, WI | 211: MISO gives no state |
| `poi` | The point of interconnection: the substation or line where the project would connect (the source's name: Interconnection Location) | none | text | for example "18CAMPBELLW”, “18CAMPBELLB, 08GIBSON (PSI) - 7ALBION   345.0kV, 10CULY13 253500 (F.B. Culley ) - 10AEP_T  353586 (tap between Culley (10CULY13 253500) - Grandview (; 2916 distinct | 157: MISO gives none |
| `zone` | The zone of the project (the source's name: Zone) | none | empty | no cell holds a value | 3881: Empty in every row: MISO's queue does not give it |
| `transmission_owner` | The transmission owner the project connects to, as MISO names it (the source's name: Transmission Owner) | none | text | for example AMEREN ILLINOIS, AMEREN MISSOURI, AMEREN TRANSMISSION COMPANY OF ILLINOIS; 94 distinct | 130: MISO gives none |
| `fuel_technology` | The project's generation type in MISO's words (Solar, Battery Storage, Wind, Hybrid, Gas and others) (the source's name: Generation Type) | none | text | Battery Storage, Biomass, Coal, Combined Cycle, Compressed Air Storage, Diesel, Gas, High Voltage DC, Hybrid, Hydro, Nuclear, Solar, Waste Heat Recovery, Wind | 325: MISO gives none |
| `iso_status` | MISO's own status of the request (Active, Pending Revision Approval, Pending Transfer, Done, LEGACY: Done, Withdrawn) (the source's name: Status) | none | text | Active, Done, LEGACY: Done, Pending Revision Approval, Pending Transfer, Withdrawn | 0 |
| `queue_date` | The date the request entered the queue (the source's name: Queue Date) | none | date | 2015-04-15 to 2026-09-09; 619 distinct | 6: MISO gives no queue date (6 rows) |
| `proposed_in_service_date` | The date the project proposes to begin operating (the source's name: Proposed Completion Date) | none | date | 1990-12-03 to 2030-06-01; 337 distinct | 3259: MISO gives no proposed date |
| `actual_in_service_date` | The date the project began operating (the source's name: Actual Completion Date (gridstatus)) | none | empty | no cell holds a value | 3881: Empty in every row: MISO gives no such date |
| `withdrawn_date` | The date the request was withdrawn (the source's name: Withdrawn Date) | none | date | 2017-02-17 to 2026-09-22; 431 distinct | 1750: Not withdrawn, or withdrawn with no date given |

### `msha_coal_mines`

One US coal mine in MSHA's Mines data set, with its current status, operator, place and type.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 35736.

- **Time:** No time column; status_date is the current status date; the table is a snapshot as read on its retrieved_at.
- **Revisions:** Rewritten whole as one snapshot by each run from MSHA's Mines.zip; vintage is the file's Last-Modified.
- **Source:** msha:open_government_data Mine Safety and Health Administration (MSHA), U.S. Department of Labor, Open Government Data (https://arlweb.msha.gov/OpenGovernmentData/OGIMSHA.asp)
- **Method note:** [`docs/methods/msha_coal_mines.md`](../methods/msha_coal_mines.md)
- **Cite as:** U.S. Department of Labor, Mine Safety and Health Administration (MSHA). Open Government Data: Mines; Quarterly Mine Employment and Production. Via the Energy Research Warehouse (ERW), table `msha_coal_mines`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: msha_mine:<MINE_ID>, seven digits (EIA's coal tables drop the leading zero) | none | text | for example msha_mine:0100114, msha_mine:0100153, msha_mine:0100163; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: plant on every row (a mine) | none | text | plant | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The current mine name | none | text | for example # 1, # 1 Refuse, # 2; more than 5000 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> | none | text | for example US-AK, US-AL, US-AR; 33 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: As MSHA gives it; empty where zero or out of range | degree | number | 0.000278 to 89.6297; more than 5000 distinct | 11789 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: As MSHA gives it; empty where zero or out of range | degree | number | -148.966111 to -0.000278; more than 5000 distinct | 11789 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: Not filled: a mine has no MW | MW | empty | no cell holds a value | 35736 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: active (Active, New Mine), suspended (Temporarily Idled, NonProducing) or retired (Abandoned, Abandoned and Sealed), from MSHA's current status | none | text | active, retired, suspended | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The current status date | none | date | 1925-01-01 to 2026-10-22; more than 5000 distinct | 0 |
| `operator` | The operator or owner, as the publisher writes it. Here: The current operator | none | text | for example 10-Creek Mining Company, 10-Tucky Farms & Stables Inc, 101 Coal Inc.; more than 5000 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | msha:open_government_data | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://arlweb.msha.gov/OpenGovernmentData/DataSets/Mines.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T19:29:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's Last-Modified (UTC) | none | utc time | 2026-10-23T11:58:31Z | 0 |
| `x_mine_status` | MSHA's current mine status in its words (Active, New Mine, Temporarily Idled, NonProducing, Abandoned, Abandoned and Sealed) (the source's name: CURRENT_MINE_STATUS) | none | text | Abandoned, Abandoned and Sealed, Active, New Mine, NonProducing, Temporarily Idled | 0 |
| `x_mine_type` | MSHA's current mine type: Surface, Underground or Facility (the source's name: CURRENT_MINE_TYPE) | none | text | Facility, Surface, Underground | 108: MSHA leaves it empty |
| `x_controller` | The current controller's name, as published (the source's name: CURRENT_CONTROLLER_NAME) | none | text | for example (Donald) Todd  Kiscaden; Scott  Kiscaden, (Harold) Lynn  Keene; Larry  Stinson, (Landon) Keller  Smith; Karl  Singer; more than 5000 distinct | 339: MSHA leaves it empty |
| `x_county_fips` | The county's FIPS code, as published (the source's name: FIPS_CNTY_CD) | none | integer | 1 to 999; 131 distinct | 0 |
| `x_county` | The county's name, as published (the source's name: FIPS_CNTY_NM) | none | text | for example Accomack, Adams, Albany; 373 distinct | 0 |
| `x_district` | MSHA's district code, as published (the source's name: DISTRICT) | none | text | C03, C04, C05, C07, C08, C09, C10, M2, M3, M5, M6, M7 | 0 |
| `x_primary_sic` | The primary SIC (industry) of the mine: Coal (Anthracite), Coal (Bituminous) or Coal (Lignite) (the source's name: PRIMARY_SIC) | none | text | Coal (Anthracite), Coal (Bituminous), Coal (Lignite) | 114: MSHA leaves it empty |
| `x_employees` | The number of employees, as published (the source's name: NO_EMPLOYEES) | count | integer | 0 to 1207; 162 distinct | 12189: MSHA leaves it empty |
| `x_nearest_town` | The nearest town, as published (the source's name: NEAREST_TOWN) | none | text | for example (Near Bishop Tazewell), --Sutton, .Bickmore; 4245 distinct | 11367: MSHA leaves it empty |

### `msha_coal_production_quarterly`

One coal mine's production, employee hours or average employees in one calendar quarter, its subunits summed, from MSHA's Quarterly Mine Employment and Production.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 294323.

- **Time:** ts_utc is the calendar quarter's first day at 00:00:00Z; freq P3M; from 2010.
- **Revisions:** Rewritten whole as one snapshot by each run from MSHA's file (the newest quarters grow as operators report); vintage is the file's Last-Modified.
- **Source:** msha:open_government_data Mine Safety and Health Administration (MSHA), U.S. Department of Labor, Open Government Data (https://arlweb.msha.gov/OpenGovernmentData/OGIMSHA.asp)
- **Method note:** [`docs/methods/msha_coal_mines.md`](../methods/msha_coal_mines.md)
- **Cite as:** U.S. Department of Labor, Mine Safety and Health Administration (MSHA). Open Government Data: Mines; Quarterly Mine Employment and Production. Via the Energy Research Warehouse (ERW), table `msha_coal_production_quarterly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: msha_mine:<MINE_ID> | none | text | for example msha_mine:0100328, msha_mine:0100329, msha_mine:0100347; 3378 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z to 2026-04-01T00:00:00Z; 66 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 0 to 31354008; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count, short_ton | 0 |
| `freq` | How long the interval of the row is | none | text | P3M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> | none | text | for example US-AK, US-AL, US-AR; 27 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 294323 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The mine's name (the last a quarter's rows give), not a pricing node | none | text | for example # 1 Refuse, # 2, # 4; 3130 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | msha:open_government_data | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://arlweb.msha.gov/OpenGovernmentData/DataSets/MinesProdQuarterly.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T19:29:38Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's Last-Modified (UTC) | none | utc time | 2026-10-23T11:58:32Z | 0 |
| `x_subunits` | The mine's subunits reported in the quarter and summed | count | integer | 1, 2, 3, 4 | 0 |
| `x_production_blank` | The subunits whose production MSHA leaves empty in the quarter (the others are summed) | count | integer | 0, 1, 2, 3 | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `average_employees` | The subunits' average employees in the quarter, summed | count | 98108 | 2010-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `coal_production` | Coal produced in the quarter (MSHA's tons, short tons) | short_ton | 98107 | 2010-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `employee_hours` | The hours the operator reports its employees worked in the quarter | count | 98108 | 2010-01-01T00:00:00Z | 2026-04-01T00:00:00Z |

### `ncsi_oman_electricity_annual`

One year's value of Oman's electricity production, distribution or connections by governorate, or production by source, from NCSI's Energy Statistics 2026 tables 11 and 12.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 126.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z; freq P1Y; 2023 to 2025.
- **Revisions:** Rewritten whole as one snapshot by each run from the saved bulletin; vintage is the PDF's Last-Modified.
- **Source:** ncsi:energy_statistics National Centre for Statistics and Information (NCSI), Sultanate of Oman, Energy Statistics 2026 (Fifth Edition, data 2025), tables 11 and 12 (source: Public Services Regulatory Authority)
- **Method note:** [`docs/methods/ncsi_oman_electricity_annual.md`](../methods/ncsi_oman_electricity_annual.md)
- **Cite as:** National Centre for Statistics and Information, Oman (NCSI). Energy Statistics 2026 (Fifth Edition, data 2025), tables 11 and 12 (electricity). Via the Energy Research Warehouse (ERW), table `ncsi_oman_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ncsi:om:<governorate, others or total; or source> | none | text | ncsi:om:ad_dakhiliyah, ncsi:om:al_batinah_north, ncsi:om:al_batinah_south, ncsi:om:al_buraimi, ncsi:om:al_dhahirah, ncsi:om:al_wusta, ncsi:om:ash_sharqiyah_north, ncsi:om:ash_sharqiyah_south, ncsi:om:dhofar, ncsi:om:diesel, ncsi:om:gas, ncsi:om:musandam, ncsi:om:muscat, ncsi:om:other, ncsi:om:others, ncsi:om:solar, ncsi:om:total, ncsi:om:wind | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 50973500.0; 122 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: OM on every row, whatever the governorate | none | text | OM | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 126 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: NCSI's row and column, not a pricing node | none | text | for example Ad Dakhliyah, Connections (000), Ad Dakhliyah, Distribution (GWh), Ad Dakhliyah, Production (GWh); 42 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ncsi:energy_statistics | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.ncsi.gov.om/uploads/pdfs/energy_statistics_bulletin_2026_1783504139.pdf | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T17:36:17Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The PDF's Last-Modified (UTC) | none | utc time | 2026-07-08T09:48:59Z | 0 |
| `x_label` | NCSI's row and column as printed, with the bulletin's unit (the same as node) | none | text | for example Ad Dakhliyah, Connections (000), Ad Dakhliyah, Distribution (GWh), Ad Dakhliyah, Production (GWh); 42 distinct | 0 |
| `x_table` | The bulletin's table: 11 (by governorate) or 12 (by source) | none | integer | 11, 12 | 0 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `connections` | Electricity connections in the governorate (table 11, from thousands) | count | 36 | 2023-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `distribution` | Electricity distributed in the governorate in the year (table 11, from GWh) | MWh | 36 | 2023-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `production` | Electricity production in the governorate in the year (table 11, from GWh) | MWh | 36 | 2023-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `production_by_source` | Electricity production from the source in the year (table 12, from TWh to one decimal) | MWh | 18 | 2023-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `nhc_hurdat2_track_points`

One best-track fix (six-hourly, or a landfall or peak between) of one tropical or subtropical cyclone in the Atlantic or the Northeast and North Central Pacific from 2000, from NOAA's HURDAT2.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 27812.

- **Time:** event_date is the fix's UTC day; x_time_utc its UTC time (HHMM).
- **Revisions:** Rewritten whole as one snapshot by each run from the two HURDAT2 files; vintage is each file's Last-Modified.
- **Source:** nhc:hurdat2 NOAA National Hurricane Center, HURDAT2 (the best track data) (https://www.nhc.noaa.gov/data/#hurdat)
- **Method note:** [`docs/methods/nhc_hurdat2_track_points.md`](../methods/nhc_hurdat2_track_points.md)
- **Cite as:** NOAA National Weather Service, National Hurricane Center. HURDAT2: best track data, Atlantic and Northeast and North Central Pacific. Via the Energy Research Warehouse (ERW), table `nhc_hurdat2_track_points`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: nhc:<storm id>:<YYYYMMDDHHMM> | none | text | for example nhc:AL012000:200006071800, nhc:AL012000:200006080000, nhc:AL012000:200006080600; more than 5000 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2000-05-22 to 2025-11-01; 3686 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: The system's status at the fix (tropical storm, hurricane and others) | none | text | disturbance, extratropical, hurricane, low, subtropical_depression, subtropical_storm, tropical_depression, tropical_storm, wave | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: NHC on every row | none | text | NHC | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 27812 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 27812 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 27812 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 27812 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 27812 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nhc:hurdat2 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2025-092326.txt, https://www.nhc.noaa.gov/data/hurdat/hurdat2-nepac-1949-2025-092926.txt | 0 |
| `x_storm_id` | The storm's ATCF id (basin, number, season) | none | text | for example AL012000, AL012001, AL012002; 973 distinct | 0 |
| `x_storm_name` | The storm's name as the file writes it (UNNAMED for some) | none | text | for example ADOLPH, ADRIAN, AGATHA; 341 distinct | 0 |
| `x_basin` | The basin: atlantic or pacific | none | text | atlantic, pacific | 0 |
| `x_time_utc` | The fix's UTC time, HHMM (0000, 0600, 1200, 1800, or another hour for a record the file marks) | none | integer | 0 to 2330; 126 distinct | 0 |
| `x_record` | The file's record identifier: C closest approach to a coast, not followed by a landfall; G genesis; I an intensity peak in both pressure and wind; L a landfall (the center crossing a coastline); P a minimum in central pressure; R more detail on the intensity while it changes rapidly; S a change of status; T more detail on the track; W the maximum sustained wind speed | none | text | C, G, I, L, P, R, S, T, W | 27230: The fix carries no record identifier |
| `x_landfall` | 1 where x_record is L (a landfall), else 0 | none | integer | 0, 1 | 0 |
| `x_lat` | The fix's latitude, decimal degrees, north positive | degree | number | 0.4 to 70.7; 585 distinct | 0 |
| `x_lon` | The fix's longitude, decimal degrees, east positive | degree | number | -180.0 to 179.9; 1923 distinct | 0 |
| `x_max_wind_kt` | The maximum sustained wind | kt | integer | 10 to 185; 34 distinct | 0 |
| `x_min_pressure_mb` | The minimum central pressure | mb | integer | 872 to 1024; 129 distinct | 41: The file writes -999 (no pressure given) |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T20:09:44Z, 2026-10-23T20:09:46Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The basin file's Last-Modified (UTC) | none | utc time | 2026-09-30T18:37:36Z, 2026-09-30T18:37:37Z | 0 |

### `nlr_atb_electricity_costs`

One technology case's value of one cost or performance measure (capital cost, O&M, fuel, capacity factor, LCOE) for one projection year, from the 2025 Electricity Annual Technology Baseline of the National Laboratory of the Rockies (formerly NREL).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 95000.

- **Time:** ts_utc is the projection year's 1 January at 00:00:00Z; freq P1Y; 2023 to 2060.
- **Revisions:** Rewritten whole as one snapshot by each run from the ATB's parquet file; vintage is the file's Last-Modified.
- **Source:** nlr:atb_electricity National Laboratory of the Rockies (NLR, formerly NREL), 2025 Electricity Annual Technology Baseline (ATB) v1.0.0 (https://atb.nrel.gov/electricity/)
- **Method note:** [`docs/methods/nlr_atb_electricity_costs.md`](../methods/nlr_atb_electricity_costs.md)
- **Cite as:** National Laboratory of the Rockies (NLR, formerly NREL). Electricity Annual Technology Baseline (ATB), flat file. Via the Energy Research Warehouse (ERW), table `nlr_atb_electricity_costs`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: nlr_atb_2025:<technology>:<detail>:<scenario>, lower case | none | text | for example nlr_atb_2025:biopower:dedicated:biopower:utility:advanced, nlr_atb_2025:biopower:dedicated:biopower:utility:conservative, nlr_atb_2025:biopower:dedicated:biopower:utility:moderate; 547 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-01-01T00:00:00Z to 2060-01-01T00:00:00Z; 38 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.1169815322192364 to 24600.93062840958; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, USD/kW, USD/kW-year, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 95000 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The ATB's display name, not a pricing node | none | text | for example Biopower - Dedicated, CSP - Class 2, CSP - Class 3; 183 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nlr:atb_electricity | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/parquet/2025/v1.0.0/ATBe.parquet | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T17:03:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The parquet file's Last-Modified (UTC) | none | utc time | 2026-09-01T22:22:25Z | 0 |
| `x_technology` | The ATB's technology (UtilityPV, LandbasedWind, NaturalGas_FE, Utility-Scale Battery Storage and others) (the source's name: technology) | none | text | Biopower, CSP, Coal_FE, Coal_Retrofits, CommPV, Commercial Battery Storage, DistributedWind, Geothermal, Hydropower, LandbasedWind, NaturalGas_FE, NaturalGas_Retrofits, Nuclear, OffShoreWind, Pumped Storage Hydropower, ResPV, Residential Battery Storage, Utility-Scale Battery Storage, Utility-Scale PV-Plus-Battery, UtilityPV | 0 |
| `x_techdetail` | The ATB's technology detail (a class, a duration, a configuration) (the source's name: techdetail) | none | text | for example 10Hr Battery Storage, 1Hr Battery Storage, 2Hr Battery Storage; 124 distinct | 456: The ATB gives no detail |
| `x_techdetail2` | The ATB's second technology detail (a carbon capture share, a technology name) (the source's name: techdetail2) | none | text | for example 90%-CCS, 95%-CCS, 99%-CCS; 59 distinct | 0 |
| `x_resourcedetail` | The ATB's resource detail (a resource class) (the source's name: resourcedetail) | none | text | for example Class1, Class10, Class11; 39 distinct | 4104: The ATB gives no resource detail |
| `x_scale` | The ATB's scale: Utility, Commercial or Residential (the source's name: scale) | none | text | Commercial, Residential, Utility | 0 |
| `x_scenario` | The ATB's scenario: Advanced, Moderate or Conservative (the source's name: scenario) | none | text | Advanced, Conservative, Moderate | 0 |
| `x_display_name` | The ATB's display name of the technology case (the source's name: display_name) | none | text | for example Biopower - Dedicated, CSP - Class 2, CSP - Class 3; 183 distinct | 0 |
| `x_default` | The ATB's default field, as published (1 or 0) (the source's name: default) | none | integer | 0, 1 | 0 |
| `x_maturity` | The ATB's maturity field, as published (Y or N) (the source's name: maturity) | none | text | N, Y | 0 |
| `x_case` | The ATB's cost case: R&D (no tax credits), the default view | none | text | R&D | 0 |
| `x_crp_years` | The cost recovery period, years (30, the default view) | year | integer | 30 | 0 |
| `x_dollar_year` | The dollar year of the costs (2023) | none | integer | 2023 | 0 |
| `x_atb_version` | The ATB edition and version (2025 v1.0.0) | none | text | 2025 v1.0.0 | 0 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity_factor` | Capacity factor | ratio | 14496 | 2023-01-01T00:00:00Z | 2060-01-01T00:00:00Z |
| `capex` | Capital expenditure, USD per kW (2023 dollars) | USD/kW | 19844 | 2023-01-01T00:00:00Z | 2060-01-01T00:00:00Z |
| `fixed_om` | Fixed operation and maintenance cost, USD per kW-year | USD/kW-year | 20528 | 2023-01-01T00:00:00Z | 2060-01-01T00:00:00Z |
| `fuel` | Fuel cost, USD per MWh | USD/MWh | 393 | 2023-01-01T00:00:00Z | 2060-01-01T00:00:00Z |
| `lcoe` | Levelized cost of energy, USD per MWh (R&D case, 30-year cost recovery period) | USD/MWh | 14496 | 2023-01-01T00:00:00Z | 2060-01-01T00:00:00Z |
| `occ` | Overnight capital cost, USD per kW | USD/kW | 19844 | 2023-01-01T00:00:00Z | 2060-01-01T00:00:00Z |
| `variable_om` | Variable operation and maintenance cost, USD per MWh | USD/MWh | 5399 | 2023-01-01T00:00:00Z | 2060-01-01T00:00:00Z |

Waiting for a second look: x_default (the ATB's default field, 1 or 0) and x_maturity (the ATB's maturity field, Y or N): what each marks is not written in the connector, the method note or the header. Read again on 20 November 2026 in the saved ATB 2025 workbook under warehouse/raw/nlr_atb (sheets Preface and Contents and Financial Definitions): not found..

### `ntd_transit_energy_annual`

One transit agency's fuel or energy used by one mode and type of service in one report year, from the National Transit Database.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 10161.

- **Time:** ts_utc is the report year's first day at 00:00:00Z; freq P1Y; 2022 to 2025.
- **Revisions:** Rewritten whole as one snapshot by each run from the FTA's CSV; vintage is the file's Last-Modified.
- **Source:** fta:ntd_fuel_energy Federal Transit Administration, 2022 - 2025 NTD Annual Data - Fuel and Energy (DOT DataHub 8ehq-7his) (https://data.transportation.gov/d/8ehq-7his)
- **Method note:** [`docs/methods/ntd_transit_energy_annual.md`](../methods/ntd_transit_energy_annual.md)
- **Cite as:** U.S. Department of Transportation, Federal Transit Administration (FTA). 2022 - 2025 NTD Annual Data - Fuel and Energy. Via the Energy Research Warehouse (ERW), table `ntd_transit_energy_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ntd_mode:<NTD ID>:<mode>:<type of service> | none | text | for example ntd_mode:00001:DR:PT, ntd_mode:00001:DR:TX, ntd_mode:00001:FB:DO; 1425 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 28389998.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, gal, t | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state of the agency's headquarters> | none | text | for example US-AK, US-AL, US-AR; 51 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 10161 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The agency, mode and type of service as the FTA names them, not a pricing node | none | text | for example Academy Lines, Inc., dba: Academy: Commuter Bus (DO), Academy Lines, Inc.: Commuter Bus (DO), Access Services: Demand Response (PT); 1751 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | fta:ntd_fuel_energy | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://data.transportation.gov/api/views/8ehq-7his/rows.csv?accessType=DOWNLOAD | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T01:54:08Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's Last-Modified (UTC) | none | utc time | 2026-10-14T15:08:39Z | 0 |
| `x_ntd_id` | The agency's NTD ID (the source's name: NTD ID) | none | integer | 1 to 99425; 553 distinct | 0 |
| `x_agency` | The agency's name in the report year (it can differ between years) (the source's name: Agency) | none | text | for example Academy Lines, Inc., Academy Lines, Inc., dba: Academy, Access Services; 696 distinct | 0 |
| `x_city` | The agency's city (the source's name: City) | none | text | for example Akron, Albany, Albuquerque; 425 distinct | 16: The FTA gives no city (four agencies) |
| `x_mode` | The FTA's mode code (MB, DR, CB, VP and others; the mode's name is in node) (the source's name: Mode) | none | text | AR, CB, CC, CR, DR, FB, HR, IP, LR, MB, MG, PB, RB, SR, TB, TR, VP, YR | 0 |
| `x_tos` | The type of service: DO directly operated, PT purchased transportation, and the FTA's other codes (the source's name: TOS) | none | text | DO, PT, TN, TX | 0 |
| `x_uza` | The urbanized area (the source's name: UZA Name) | none | text | for example Akron, OH, Albany, GA, Albany--Schenectady, NY; 302 distinct | 0 |
| `x_mode_voms` | Vehicles operated in maximum service in the mode (the source's name: Mode VOMS) | count | integer | 0 to 5489; 466 distinct | 7: The FTA leaves it blank |
| `x_reporter_type` | The agency's reporter type: Full Reporter or Reduced Reporter (the source's name: Reporter Type) | none | text | Full Reporter, Reduced Reporter | 0 |
| `x_questionable` | yes where the FTA marks the figure Questionable | none | empty | no cell holds a value | 10161: Not marked Questionable (no row is marked in this run) |

Variables (9):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `biodiesel` | Biodiesel used in the year | gal | 571 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `cng_gal_equivalent` | Compressed natural gas used, gallon equivalents as the FTA reports them | gal | 832 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `diesel` | Diesel used in the year | gal | 2236 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `electric_battery` | Electric battery energy used (the FTA's kWh / 1,000) | MWh | 3000 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `electric_propulsion` | Electric propulsion energy used (the FTA's kWh / 1,000) | MWh | 359 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `gasoline` | Gasoline used in the year | gal | 2862 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `hydrogen` | Hydrogen used (the FTA's kg / 1,000) | t | 43 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `lpg_gal_equivalent` | Liquefied petroleum gas used, gallon equivalents as the FTA reports them | gal | 222 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `other_fuel` | Other fuel used in the year | gal | 36 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

Waiting for a second look: x_tos: the type-of-service codes TN and TX are not defined in the connector or the method note (DO and PT are). Read again on 20 November 2026 in the headings of the saved NTD CSV under warehouse/raw/ntd_transit_energy (TOS as a heading only): not found..

### `nve_norway_reservoirs_weekly`

One Norwegian area's (the country, a price area or a water region) hydropower reservoir filling, stored energy or capacity in one week, from NVE's reservoir statistics.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 44793.

- **Time:** ts_utc is the date NVE gives the week (its last day) at 00:00:00Z: a stock at that date; freq P1W.
- **Revisions:** Rewritten whole as one snapshot by each run from NVE's one answer; vintage is not filled.
- **Source:** nve:magasinstatistikk NVE, reservoir statistics (magasinstatistikk) (https://api.nve.no/doc/magasinstatistikk/)
- **Method note:** [`docs/methods/nve_norway_reservoirs_weekly.md`](../methods/nve_norway_reservoirs_weekly.md)
- **Cite as:** Norwegian Water Resources and Energy Directorate (NVE). Reservoir statistics (magasinstatistikk): filling share, stored energy and capacity a week. Via the Energy Research Warehouse (ERW), table `nve_norway_reservoirs_weekly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: nve:no:<area>: no (the country), no1 to no5 (price areas), region_1 to region_3 (water regions) | none | text | nve:no:no, nve:no:no1, nve:no:no2, nve:no:no3, nve:no:no4, nve:no:no5, nve:no:region_1, nve:no:region_2, nve:no:region_3 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1995-01-08T00:00:00Z to 2026-10-18T00:00:00Z; 1659 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 5.165346 to 87437580.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: NO on every row, whatever the area | none | text | NO | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 44793 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: NVE's area type and number with the ISO week, not a pricing node | none | text | for example EL 1, 1995-W01, EL 1, 1995-W02, EL 1, 1995-W03; more than 5000 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nve:magasinstatistikk | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligData | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T17:57:48Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 44793 |
| `x_iso_week` | The ISO week (YYYY-Www) | none | text | for example 1995-W01, 1995-W02, 1995-W03; 1659 distinct | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity` | Reservoir capacity in energy (from TWh) | MWh | 14931 | 1995-01-08T00:00:00Z | 2026-10-18T00:00:00Z |
| `filling_share` | Reservoir filling, percent of capacity, at the week's date | pct | 14931 | 1995-01-08T00:00:00Z | 2026-10-18T00:00:00Z |
| `stored_energy` | Energy stored in the reservoirs at the week's date (from TWh) | MWh | 14931 | 1995-01-08T00:00:00Z | 2026-10-18T00:00:00Z |

### `ons_brazil_balance_hourly`

One Brazilian subsystem's (or the national interconnected system's) generation by source, load or net interchange in one hour, from ONS's energy balance.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1790640.

- **Time:** ts_utc is the hour's start in UTC, from Brasilia time (UTC-3) as ONS prints it; freq PT1H.
- **Revisions:** Merged by (entity, variable, ts_utc): each run's hours replace the same hours (ONS revises its data) and older ones are kept; vintage is each yearly file's Last-Modified.
- **Source:** ons:balanco_energia_subsistema ONS, open data, Balanco de Energia nos Subsistemas (hourly) (https://dados.ons.org.br/dataset/balanco-energia-subsistema)
- **Method note:** [`docs/methods/ons_brazil_balance_hourly.md`](../methods/ons_brazil_balance_hourly.md)
- **Cite as:** Operador Nacional do Sistema Eletrico (ONS). Dados Abertos ONS, Balanco de Energia nos Subsistemas (hourly). Via the Energy Research Warehouse (ERW), table `ons_brazil_balance_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ons:<subsystem>: N, NE, S, SE, or SIN (the national interconnected system) | none | text | ons:N, ons:NE, ons:S, ons:SE, ons:SIN | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2020-01-01T03:00:00Z to 2026-10-23T02:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -16172.03099999 to 106148.66; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: BR on every row | none | text | BR | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1790640 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: ONS's subsystem name in Portuguese, not a pricing node | none | text | NORDESTE, NORTE, SISTEMA INTERLIGADO NACIONAL, SUDESTE/CENTRO-OESTE, SUL | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ons:balanco_energia_subsistema | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/balanco_energia_subsistema_ho/BALANCO_ENERGIA_SUBSISTEMA_2020.csv, https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/balanco_energia_subsistema_ho/BALANCO_ENERGIA_SUBSISTEMA_2021.csv, https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/balanco_energia_subsistema_ho/BALANCO_ENERGIA_SUBSISTEMA_2022.csv, https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/balanco_energia_subsistema_ho/BALANCO_ENERGIA_SUBSISTEMA_2023.csv, https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/balanco_energia_subsistema_ho/BALANCO_ENERGIA_SUBSISTEMA_2024.csv, https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/balanco_energia_subsistema_ho/BALANCO_ENERGIA_SUBSISTEMA_2025.csv, https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/balanco_energia_subsistema_ho/BALANCO_ENERGIA_SUBSISTEMA_2026.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T03:25:26Z, 2026-10-24T03:25:27Z, 2026-10-24T03:25:28Z, 2026-10-24T03:25:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The yearly file's Last-Modified (UTC) | none | utc time | 2024-10-20T14:55:51Z, 2024-10-20T14:56:38Z, 2024-10-20T14:57:21Z, 2025-07-28T13:30:26Z, 2025-07-28T13:31:29Z, 2026-01-31T22:01:09Z, 2026-10-23T22:00:22Z | 0 |
| `x_brasilia_hour` | ONS's stamp of the hour as printed, Brasilia time (the source's name: din_instante) | none | text | for example 2020-01-01 00:00:00, 2020-01-01 01:00:00, 2020-01-01 02:00:00; more than 5000 distinct | 0 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `hydro` | Hydro generation, the hour's mean (ONS's MWmed) | MW | 298440 | 2020-01-01T03:00:00Z | 2026-10-23T02:00:00Z |
| `load` | Load, the hour's mean | MW | 298440 | 2020-01-01T03:00:00Z | 2026-10-23T02:00:00Z |
| `net_interchange` | ONS's net interchange, positive an export (it can differ from generation minus load) | MW | 298440 | 2020-01-01T03:00:00Z | 2026-10-23T02:00:00Z |
| `solar` | Solar generation, the hour's mean | MW | 298440 | 2020-01-01T03:00:00Z | 2026-10-23T02:00:00Z |
| `thermal` | Thermal generation, the hour's mean | MW | 298440 | 2020-01-01T03:00:00Z | 2026-10-23T02:00:00Z |
| `wind` | Wind generation, the hour's mean | MW | 298440 | 2020-01-01T03:00:00Z | 2026-10-23T02:00:00Z |

### `owid_ember_electricity_annual`

One country's or region's electricity demand or power sector greenhouse gas emissions in one year, the Ember columns of Our World in Data's energy dataset.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 12406.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z; freq P1Y.
- **Revisions:** Merged by (entity, variable, ts_utc): each run's years replace the same keys and older ones are kept; vintage is the file's Last-Modified.
- **Source:** owid:energy Our World in Data, energy dataset (based on Ember's Yearly Electricity Data and Yearly Electricity Data Europe, 2026) (https://ourworldindata.org/energy)
- **Method note:** [`docs/methods/owid_ember_electricity_annual.md`](../methods/owid_ember_electricity_annual.md)
- **Cite as:** Ember; Our World in Data. Energy dataset (owid_energy), Ember's electricity demand and emissions columns; Yearly Electricity Data and Yearly Electricity Data Europe (through Our World in Data). Via the Energy Research Warehouse (ERW), table `owid_ember_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: owid_energy:<ISO alpha-3>, or owid_energy:<region or income group in snake case> | none | text | for example owid_energy:ABW, owid_energy:AFG, owid_energy:AGO; 239 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 36 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 31772350000.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, tCO2e | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 12406 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 12406 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The country's or region's name, not a pricing node | none | text | for example ASEAN (Ember), Afghanistan, Africa; 239 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | owid:energy | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://catalog.ourworldindata.org/energy/owid_energy/owid_energy.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T23:07:14Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's Last-Modified (UTC) | none | utc time | 2026-09-30T14:42:02Z | 0 |
| `x_iso_code` | The country's ISO alpha-3 code | none | text | for example ABW, AFG, AGO; 214 distinct | 1302: Empty on regions and income groups |
| `x_owid_column` | Our World in Data's column the value is read from (electricity_demand_twh, electricity_emissions_mtco2eq) | none | text | electricity_demand_twh, electricity_emissions_mtco2eq | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `electricity_demand` | Electricity demand in the year (Ember via Our World in Data; TWh times 1,000,000) | MWh | 6378 | 1990-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `electricity_emissions` | The power sector's greenhouse gas emissions in the year, CO2 equivalent (million tonnes times 1,000,000) | tCO2e | 6028 | 2000-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `predict_demand_forecasts`

One place's ERW forecast of demand for one UTC hour of a target day, as the forecast was made on its day (a model's output, not a published figure).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-27: 696.

- **Time:** ts_utc is the forecast hour's start (UTC); vintage is the hour the forecast was made; x_target_day is the place's local day.
- **Revisions:** Every making kept, one row per vintage: the key is (entity, variable, ts_utc, vintage). The table is the whole ledger (site/data/predict/ledger_demand.csv), rewritten from it each run; a forecast once made is never replaced.
- **Source:** erw:predict the ERW's own forecast, from eia930_ba_demand_hourly (U.S. Energy Information Administration, Form EIA-930, public) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/predict.md)
- **Method note:** [`docs/methods/predict.md`](../methods/predict.md)
- **Cite as:** ERW. Via the Energy Research Warehouse (ERW), table `predict_demand_forecasts`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example eia930:BPAT, eia930:CAL, eia930:CAR; 29 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-11-27T05:00:00Z to 2026-11-28T07:00:00Z; 27 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 3671.2 to 94014.9; 552 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 696 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 696 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:predict | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/predict.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-26T23:35:24Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-11-26T11:00:00Z | 0 |
| `x_place` | The forecast's place on the page (region-<code> an EIA-930 region, ba-<code> a balancing authority) | none | text | for example ba-bpat, ba-ciso, ba-cple; 29 distinct | 0 |
| `x_method` | The method that made the forecast (warehouse/predict/predict_demand.py; chosen by the backtest's rule) | none | text | regression | 0 |
| `x_horizon_days` | Days from the last hour of demand the forecast read to the target day | days | integer | 3, 4 | 0 |
| `x_inputs_through_utc` | The last hour of the place's demand the forecast read (UTC) | none (an ISO 8601 UTC time) | utc time | 2026-11-24T05:00:00Z, 2026-11-24T07:00:00Z, 2026-11-25T04:00:00Z, 2026-11-25T05:00:00Z, 2026-11-25T06:00:00Z, 2026-11-25T07:00:00Z | 0 |
| `x_target_day` | The place's local day the forecast is for | none (a date) | date | 2026-11-27 | 0 |
| `x_local_hour` | The hour of the place's local day, 0 to 23 | hour | integer | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23 | 0 |
| `x_lo` | The low end of the forecast's range (the method's interval, docs/methods/predict.md) | MW | number | 3201.6 to 87206.0; 551 distinct | 0 |
| `x_hi` | The high end of the forecast's range | MW | number | 4162.8 to 108127.6; 551 distinct | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `demand_forecast_mw` | The ERW's forecast of the place's hourly demand, MW | MW | 696 | 2026-11-27T05:00:00Z | 2026-11-28T07:00:00Z |

### `predict_price_forecasts`

One place's ERW forecast of its grid hub's day-ahead price for one UTC hour of a target day, as the forecast was made on its day (a model's output, not a published figure).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-27: 144.

- **Time:** ts_utc is the forecast hour's start (UTC); vintage is the hour the forecast was made; x_target_day is the place's local day.
- **Revisions:** Every making kept, one row per vintage: the key is (entity, variable, ts_utc, vintage). The table is the whole ledger (site/data/predict/ledger_price.csv), rewritten from it each run; a forecast once made is never replaced.
- **Source:** erw:predict the ERW's own forecast, from the hubs' day-ahead prices (ERCOT, SPP, CAISO, public), eia930_ba_demand_hourly and eia_fuel_spot_prices (public) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/predict_price.md)
- **Method note:** [`docs/methods/predict_price.md`](../methods/predict_price.md)
- **Cite as:** ERW. Via the Energy Research Warehouse (ERW), table `predict_price_forecasts`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | eia930:CAL, eia930:CENT, eia930:CISO, eia930:ERCO, eia930:SWPP, eia930:TEX | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-11-27T06:00:00Z to 2026-11-28T07:00:00Z; 26 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 14.69 to 70.21; 108 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso, ercot, spp | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | HB_NORTH, SPPNORTH_HUB, TH_SP15_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:predict | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/predict_price.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-26T23:35:24Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-11-26T11:00:00Z | 0 |
| `x_place` | The forecast's place on the page (region-<code> an EIA-930 region, ba-<code> a balancing authority); market and node name its grid's hub | none | text | ba-ciso, ba-erco, ba-swpp, region-cal, region-cent, region-tex | 0 |
| `x_method` | The method that made the forecast (warehouse/predict/predict_price.py; chosen by the backtest's rule) | none | text | regression, yesterday | 0 |
| `x_horizon_days` | Days from the last hour of prices the forecast read to the target day | days | integer | 2 | 0 |
| `x_inputs_through_utc` | The last hour of the hub's day-ahead price the forecast read (UTC) | none (an ISO 8601 UTC time) | utc time | 2026-11-26T05:00:00Z, 2026-11-26T07:00:00Z | 0 |
| `x_target_day` | The place's local day the forecast is for | none (a date) | date | 2026-11-27 | 0 |
| `x_local_hour` | The hour of the place's local day, 0 to 23 | hour | integer | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23 | 0 |
| `x_lo` | The low end of the forecast's range (docs/methods/predict_price.md) | USD/MWh | number | -2.01 to 48.12; 108 distinct | 0 |
| `x_hi` | The high end of the forecast's range | USD/MWh | number | 27.57 to 99.47; 115 distinct | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `lmp_dam_forecast` | The ERW's forecast of the hub's hourly day-ahead price, USD/MWh | USD/MWh | 144 | 2026-11-27T06:00:00Z | 2026-11-28T07:00:00Z |

### `price_congestion_hourly`

One part of the day-ahead price at one hub or load zone for one hour, as SPP or CAISO splits it.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1279835.

- **Time:** ts_utc is the hour's start in UTC.
- **Revisions:** Merged by (entity, variable, ts_utc); a day is written only when every hour of the operating day is there once, and a day read again replaces the one held. vintage is not filled.
- **Source:** spp:DA-LMP-SL Day-Ahead LMP by Settlement Location (https://portal.spp.org/pages/da-lmp-by-location)
- **Method note:** [`docs/methods/grid_congestion.md`](../methods/grid_congestion.md)
- **Cite as:** CAISO; SPP. Via the Energy Research Warehouse (ERW), table `price_congestion_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:DLAP_PGAE-APND, caiso:DLAP_SCE-APND, caiso:DLAP_SDGE-APND, caiso:DLAP_VEA-APND, caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, caiso:TH_ZP26_GEN-APND, spp:SPPNORTH_HUB, spp:SPPSOUTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-01-01T06:00:00Z to 2026-11-21T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -201.8997 to 1288.8055; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-CA,US-NV | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_dam, spp_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | DLAP_PGAE-APND, DLAP_SCE-APND, DLAP_SDGE-APND, DLAP_VEA-APND, SPPNORTH_HUB, SPPSOUTH_HUB, TH_NP15_GEN-APND, TH_SP15_GEN-APND, TH_ZP26_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:PRC_LMP, spp:DA-LMP-SL | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_LMP&version=12&market_run_id=DAM&node=TH_NP15_GEN-APND,TH_SP15_GEN-APND,TH_ZP26_GEN-APND,DLAP_PGAE-APND,DLAP_SCE-APND,DLAP_SDGE-APND,DLAP_VEA-APND&startdatetime=20230801T07:00-0000&enddatetime=20230901T07:00-0000, https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_LMP&version=12&market_run_id=DAM&node=TH_NP15_GEN-APND,TH_SP15_GEN-APND,TH_ZP26_GEN-APND,DLAP_PGAE-APND,DLAP_SCE-APND,DLAP_SDGE-APND,DLAP_VEA-APND&startdatetime=20230901T07:00-0000&enddatetime=20231001T07:00-0000, https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_LMP&version=12&market_run_id=DAM&node=TH_NP15_GEN-APND,TH_SP15_GEN-APND,TH_ZP26_GEN-APND,DLAP_PGAE-APND,DLAP_SCE-APND,DLAP_SDGE-APND,DLAP_VEA-APND&startdatetime=20231001T07:00-0000&enddatetime=20231101T07:00-0000; 731 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-20T10:42:12Z to 2026-11-20T12:47:00Z; 731 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1279835 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `congestion_dam` | The congestion part of the day-ahead price (SPP MCC, CAISO MCC), USD/MWh | USD/MWh | 269599 | 2023-01-01T06:00:00Z | 2026-11-21T07:00:00Z |
| `energy_dam` | The energy part of the day-ahead price (SPP MEC, CAISO MCE), USD/MWh | USD/MWh | 269599 | 2023-01-01T06:00:00Z | 2026-11-21T07:00:00Z |
| `ghg_dam` | The greenhouse gas part of CAISO's day-ahead price (MGHG), USD/MWh | USD/MWh | 201439 | 2023-08-10T07:00:00Z | 2026-11-21T07:00:00Z |
| `lmp_dam` | The day-ahead locational marginal price (SPP LMP, CAISO LMP), USD/MWh | USD/MWh | 269599 | 2023-01-01T06:00:00Z | 2026-11-21T07:00:00Z |
| `loss_dam` | The loss part of the day-ahead price (SPP MLC, CAISO MCL), USD/MWh | USD/MWh | 269599 | 2023-01-01T06:00:00Z | 2026-11-21T07:00:00Z |

### `price_congestion_monthly`

One hub or load zone in one month, the means of its day-ahead price parts; derived from price_congestion_hourly.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 2236.

- **Time:** ts_utc is the month's first day at 00:00 UTC.
- **Revisions:** Rebuilt from price_congestion_hourly at each run and merged by (entity, variable, ts_utc), so a month recomputed replaces the one held. vintage is not filled.
- **Source:** erw:price_congestion_monthly ERW derived table (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_congestion.md)
- **Method note:** [`docs/methods/grid_congestion.md`](../methods/grid_congestion.md)
- **Cite as:** CAISO; SPP. Via the Energy Research Warehouse (ERW), table `price_congestion_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:DLAP_PGAE-APND, caiso:DLAP_SCE-APND, caiso:DLAP_SDGE-APND, caiso:DLAP_VEA-APND, caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, caiso:TH_ZP26_GEN-APND, spp:SPPNORTH_HUB, spp:SPPSOUTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-08-01T00:00:00Z to 2026-11-01T00:00:00Z; 40 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -177.8992 to 744.0; 1389 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-CA,US-NV | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_dam, spp_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | DLAP_PGAE-APND, DLAP_SCE-APND, DLAP_SDGE-APND, DLAP_VEA-APND, SPPNORTH_HUB, SPPSOUTH_HUB, TH_NP15_GEN-APND, TH_SP15_GEN-APND, TH_ZP26_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:price_congestion_monthly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_congestion.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-20T12:13:22Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 2236 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `congestion_mean` | Mean congestion part, USD/MWh | USD/MWh | 326 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `congestion_share_pct` | The mean congestion part as a share of the mean LMP, pct | pct | 326 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `energy_mean` | Mean energy part, USD/MWh | USD/MWh | 326 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `ghg_mean` | Mean greenhouse gas part (CAISO), USD/MWh | USD/MWh | 280 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `hours_held` | Hours of the month held, count | count | 326 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `lmp_mean` | Mean day-ahead LMP over the hours held, USD/MWh | USD/MWh | 326 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `loss_mean` | Mean loss part, USD/MWh | USD/MWh | 326 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |

### `ree_spain_balance_monthly`

One month's value of one series of Spain's electrical energy balance (generation by technology, storage, exchanges, demand at busbars), from Red Electrica's REData.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1890.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; from 2020-01.
- **Revisions:** Merged by (entity, variable, ts_utc): each run's months replace the same months and older ones are kept; vintage is not filled.
- **Source:** ree:redata_balance_electrico Red Electrica (REE), REData API, balance-electrico (https://www.ree.es/en/datos/balance)
- **Method note:** [`docs/methods/ree_spain_balance_monthly.md`](../methods/ree_spain_balance_monthly.md)
- **Cite as:** Red Electrica (REE). REData API, electrical energy balance (balance-electrico), a month. Via the Energy Research Warehouse (ERW), table `ree_spain_balance_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ree:ES on every row | none | text | ree:ES | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2020-01-01T00:00:00Z to 2026-09-01T00:00:00Z; 81 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -2876662.709 to 25259616.550000016; 1873 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ES on every row | none | text | ES | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1890 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Spain on every row, not a pricing node | none | text | Spain | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ree:redata_balance_electrico | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://apidatos.ree.es/en/datos/balance/balance-electrico?start_date=2020-01-01T00:00&end_date=2020-12-31T23:59&time_trunc=month, https://apidatos.ree.es/en/datos/balance/balance-electrico?start_date=2021-01-01T00:00&end_date=2021-12-31T23:59&time_trunc=month, https://apidatos.ree.es/en/datos/balance/balance-electrico?start_date=2022-01-01T00:00&end_date=2022-12-31T23:59&time_trunc=month, https://apidatos.ree.es/en/datos/balance/balance-electrico?start_date=2023-01-01T00:00&end_date=2023-12-31T23:59&time_trunc=month, https://apidatos.ree.es/en/datos/balance/balance-electrico?start_date=2024-01-01T00:00&end_date=2024-12-31T23:59&time_trunc=month, https://apidatos.ree.es/en/datos/balance/balance-electrico?start_date=2025-01-01T00:00&end_date=2025-12-31T23:59&time_trunc=month, https://apidatos.ree.es/en/datos/balance/balance-electrico?start_date=2026-01-01T00:00&end_date=2026-12-31T23:59&time_trunc=month | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T03:18:21Z, 2026-10-24T03:18:54Z, 2026-10-24T03:19:23Z, 2026-10-24T03:19:46Z, 2026-10-24T03:20:09Z, 2026-10-24T03:20:34Z, 2026-10-24T03:21:03Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1890 |
| `x_group` | REE's group of the series: Renewable, Non-renewable, Almacenamiento (storage) or Demand (the source's name: type) | none | text | Almacenamiento, Demand, Non-renewable, Renewable | 0 |
| `x_series_id` | REE's id of the series (the source's name: id) | none | integer | 10288, 10289, 10290, 10291, 10292, 10293, 10294, 10295, 10297, 10298, 10299, 10344, 10483, 1445, 1446, 1450, 1451, 1454, 1455, 1458, 1459, 1472, 1474, 2180, 2181 | 0 |

Variables (25):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `battery_charging` | Battery charging (negative, as REE gives it) | MWh | 45 | 2023-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_delivery` | Battery delivery | MWh | 45 | 2023-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `coal` | Coal generation | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `cogeneration` | Cogeneration | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `combined_cycle` | Combined cycle generation | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `cross_border_exchange_balance` | Cross-border exchange balance (a net export negative) | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `demand_at_busbars` | Demand at busbars | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `diesel_engines` | Diesel engine generation | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `fuel_gas` | Fuel and gas generation | MWh | 18 | 2020-03-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `gas_turbine` | Gas turbine generation | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `hydro` | Hydro generation | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `hydroeolian` | Hydro-wind generation | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `non_renewable_generation` | Non-renewable generation, REE's subtotal | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `non_renewable_waste` | Non-renewable waste generation | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nuclear` | Nuclear generation | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `other_renewables` | Other renewable generation | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pumping_consumption` | Pumping consumption (negative, as REE gives it) | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pumping_turbine` | Pumped storage turbine generation | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `renewable_generation` | Renewable generation, REE's subtotal | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `renewable_waste` | Renewable waste generation | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `solar_photovoltaic` | Solar photovoltaic generation | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `steam_turbine` | Steam turbine generation | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `storage_balance` | Storage balance, REE's subtotal | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `thermal_solar` | Solar thermal generation | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `wind` | Wind generation | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `rrc_lease_production_monthly`

One Texas Railroad Commission lease's reported production of oil, casinghead gas, gas or condensate in Martin County in one month.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 212252.

- **Time:** ts_utc is the production month's first day at 00:00:00Z; freq P1M.
- **Revisions:** Replaced whole by each run: a snapshot of the dump's latest 24 months, as the dump revises; vintage is the dump's oil extract date.
- **Source:** rrc:pdq_dump RRC Production Data Query dump (PDQ_DSV.zip) (https://mft.rrc.texas.gov/link/1f5ddb8d-329a-4459-b7f8-177b4f5ee60d)
- **Method note:** [`docs/methods/rrc_lease_production_monthly.md`](../methods/rrc_lease_production_monthly.md)
- **Cite as:** Railroad Commission of Texas (RRC). Production Data Query dump (PDQ_DSV.zip). Via the Energy Research Warehouse (ERW), table `rrc_lease_production_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: rrc:<oil or gas code>-<district no>-<lease no>, the RRC's lease id (a gas lease is one gas well) | none | text | for example rrc:G-10-149593, rrc:G-10-295113, rrc:G-10-299615; 4828 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2024-08-01T00:00:00Z, 2024-09-01T00:00:00Z, 2024-10-01T00:00:00Z, 2024-11-01T00:00:00Z, 2024-12-01T00:00:00Z, 2025-01-01T00:00:00Z, 2025-02-01T00:00:00Z, 2025-03-01T00:00:00Z, 2025-04-01T00:00:00Z, 2025-05-01T00:00:00Z, 2025-06-01T00:00:00Z, 2025-07-01T00:00:00Z, 2025-08-01T00:00:00Z, 2025-09-01T00:00:00Z, 2025-10-01T00:00:00Z, 2025-11-01T00:00:00Z, 2025-12-01T00:00:00Z, 2026-01-01T00:00:00Z, 2026-02-01T00:00:00Z, 2026-03-01T00:00:00Z, 2026-04-01T00:00:00Z, 2026-05-01T00:00:00Z, 2026-06-01T00:00:00Z, 2026-07-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 0 to 872591; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | Mcf, bbl | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 212252 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 212252 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | rrc:pdq_dump | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://mft.rrc.texas.gov/link/1f5ddb8d-329a-4459-b7f8-177b4f5ee60d | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-01T04:38:43Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The dump's oil extract date (2026-09-18) | none | utc time | 2026-09-18T00:00:00Z | 0 |
| `x_county` | The county (MARTIN) (the source's name: COUNTY_NAME) | none | text | MARTIN | 0 |
| `x_district` | The RRC district's name (08, 7C, 8A); the entity carries the district number (the source's name: DISTRICT_NAME (from DISTRICT_NO)) | none | text | 08, 7C, 8A | 0 |
| `x_oil_gas_code` | O for an oil lease, G for a gas lease (the source's name: OIL_GAS_CODE) | none | text | G, O | 0 |
| `x_lease_no` | The lease's number (the source's name: LEASE_NO) | none | integer | 388 to 299975; 4822 distinct | 0 |
| `x_lease_name` | The lease's name (the source's name: LEASE_NAME) | none | text | for example A LLOYD 48, ABRAXAS "20", ABRAXAS "27"; 4715 distinct | 0 |
| `x_operator_no` | The number of the operator that reported the month (the source's name: OPERATOR_NO) | none | integer | 27200 to 950523; 71 distinct | 0 |
| `x_operator_name` | The name of the operator that reported the month (the source's name: OPERATOR_NAME) | none | text | for example ALAMAR VENTURES, INC., APACHE CORPORATION, ARYA RESOURCES, LLC; 71 distinct | 0 |
| `x_field_no` | The field's number (the source's name: FIELD_NO) | none | integer | 448200 to 90557500; 51 distinct | 0 |
| `x_field_name` | The field's name (the source's name: FIELD_NAME) | none | text | for example ACKERLY (DEAN SAND), BETTY SUE (DEVONIAN), BLOCK 7 (DEVONIAN); 50 distinct | 0 |
| `x_gas_well_no` | The gas well number, gas leases only (the source's name: GAS_WELL_NO) | none | text | 124, 1A, 1H, 2, 2H, 3H, 4H, 5, 6H | 211870: Empty on oil leases |
| `x_wells` | The wells the RRC lists on the lease in OG_WELL_COMPLETION (any status, any county; 0 where it lists none) | count | integer | 1 to 919; 46 distinct | 0 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `casinghead_gas_mcf` | Casinghead gas produced by an oil lease in the county in the month, as reported by the operator | Mcf | 105935 | 2024-08-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `condensate_bbl` | Condensate produced by a gas lease in the county in the month, as reported by the operator | bbl | 191 | 2024-08-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `gas_mcf` | Gas produced by a gas lease in the county in the month, as reported by the operator | Mcf | 191 | 2024-08-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `oil_bbl` | Oil produced by an oil lease in the county in the month, as reported by the operator | bbl | 105935 | 2024-08-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `rte_eco2mix_france_halfhourly`

France's consumption, production from one source or net physical exchanges in one half hour, from RTE's eco2mix national files.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1448927.

- **Time:** ts_utc is the half hour's start in UTC, from RTE's date and hour in French local time; freq PT30M.
- **Revisions:** Merged by (entity, variable, ts_utc): each run's half hours replace the same keys and older ones are kept; vintage is each file's Last-Modified; x_nature says definitive or consolidated.
- **Source:** rte:eco2mix_national RTE (Reseau de Transport d'Electricite), eco2mix, national definitive and consolidated files (https://www.rte-france.com/eco2mix/telecharger-les-indicateurs)
- **Method note:** [`docs/methods/rte_eco2mix_france_halfhourly.md`](../methods/rte_eco2mix_france_halfhourly.md)
- **Cite as:** RTE (Reseau de Transport d'Electricite). eco2mix, national definitive and consolidated files (France, every half hour). Via the Energy Research Warehouse (ERW), table `rte_eco2mix_france_halfhourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: rte_eco2mix:FR on every row | none | text | rte_eco2mix:FR | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-12-31T23:00:00Z to 2026-08-31T21:30:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -21063.0 to 90236.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT30M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: FR on every row | none | text | FR | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1448927 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: France on every row, not a pricing node | none | text | France | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | rte:eco2mix_national | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://eco2mix.rte-france.com/download/eco2mix/eCO2mix_RTE_Annuel-Definitif_2020.zip, https://eco2mix.rte-france.com/download/eco2mix/eCO2mix_RTE_Annuel-Definitif_2021.zip, https://eco2mix.rte-france.com/download/eco2mix/eCO2mix_RTE_Annuel-Definitif_2022.zip, https://eco2mix.rte-france.com/download/eco2mix/eCO2mix_RTE_Annuel-Definitif_2023.zip, https://eco2mix.rte-france.com/download/eco2mix/eCO2mix_RTE_Annuel-Definitif_2024.zip, https://eco2mix.rte-france.com/download/eco2mix/eCO2mix_RTE_Annuel-Definitif_2025.zip, https://eco2mix.rte-france.com/download/eco2mix/eCO2mix_RTE_En-cours-Consolide.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T03:06:36Z, 2026-10-24T03:06:38Z, 2026-10-24T03:06:39Z, 2026-10-24T03:06:41Z, 2026-10-24T03:06:43Z, 2026-10-24T03:06:45Z, 2026-10-24T03:06:47Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's Last-Modified (UTC) | none | utc time | 2023-02-09T13:08:49Z, 2024-05-16T15:29:17Z, 2025-06-25T11:26:58Z, 2025-06-25T13:41:41Z, 2026-03-19T04:07:52Z, 2026-10-06T10:02:08Z, 2026-10-06T10:02:20Z | 0 |
| `x_nature` | RTE's nature of the data: Donnees definitives (definitive) or Donnees consolidees (consolidated) | none | text | Données consolidées, Données définitives | 0 |
| `x_local_date` | RTE's date in French local time | none | date | 2020-01-01 to 2026-08-31; 2435 distinct | 0 |
| `x_local_hour` | RTE's hour in French local time (HH:MM) | none | text | for example 00:00, 00:30, 01:00; 48 distinct | 0 |

Variables (13):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `bioenergy` | Production from bioenergy | MW | 116853 | 2019-12-31T23:00:00Z | 2026-08-31T21:30:00Z |
| `coal` | Production from coal | MW | 116853 | 2019-12-31T23:00:00Z | 2026-08-31T21:30:00Z |
| `consumption` | Consumption | MW | 116853 | 2019-12-31T23:00:00Z | 2026-08-31T21:30:00Z |
| `gas` | Production from gas | MW | 116853 | 2019-12-31T23:00:00Z | 2026-08-31T21:30:00Z |
| `hydro` | Production from hydro | MW | 116853 | 2019-12-31T23:00:00Z | 2026-08-31T21:30:00Z |
| `nuclear` | Production from nuclear | MW | 116853 | 2019-12-31T23:00:00Z | 2026-08-31T21:30:00Z |
| `oil` | Production from oil | MW | 116853 | 2019-12-31T23:00:00Z | 2026-08-31T21:30:00Z |
| `physical_exchanges` | Net physical exchanges | MW | 116853 | 2019-12-31T23:00:00Z | 2026-08-31T21:30:00Z |
| `pumping` | Pumping (negative) | MW | 116853 | 2019-12-31T23:00:00Z | 2026-08-31T21:30:00Z |
| `solar` | Production from solar | MW | 116853 | 2019-12-31T23:00:00Z | 2026-08-31T21:30:00Z |
| `wind` | Production from wind | MW | 116853 | 2019-12-31T23:00:00Z | 2026-08-31T21:30:00Z |
| `wind_offshore` | Production from offshore wind (from 2022) | MW | 81772 | 2021-12-31T23:30:00Z | 2026-08-31T21:30:00Z |
| `wind_onshore` | Production from onshore wind (from 2022) | MW | 81772 | 2021-12-31T23:30:00Z | 2026-08-31T21:30:00Z |

### `scb_sweden_electricity_monthly`

One month's electricity supply in Sweden from one type of production (or imports, or the sum), from Statistics Sweden's table TAB1011 (the Swedish Energy Agency's statistics).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 6059.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; from 1974-01.
- **Revisions:** Rewritten whole as one snapshot by each run from SCB's JSON-stat answer; vintage is SCB's updated time.
- **Source:** scb:TAB1011 Swedish Energy Agency, via Statistics Sweden, table TAB1011 (https://www.statistikdatabasen.scb.se/pxweb/en/ssd/START__EN__EN0108/)
- **Method note:** [`docs/methods/scb_sweden_electricity_monthly.md`](../methods/scb_sweden_electricity_monthly.md)
- **Cite as:** Statistics Sweden (SCB). Table TAB1011: Electricity supply in Sweden by type of production, monthly. Via the Energy Research Warehouse (ERW), table `scb_sweden_electricity_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: scb:se on every row | none | text | scb:se | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1974-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 632 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 18923000.0; 3074 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: SE on every row | none | text | SE | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 6059 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: SCB's label as written, not a pricing node | none | text | - of which back pressure, industrial, - of which back-pressure, district heating work, - of which condensation, - of which gas turbine etc., conventional thermal power, net, hydro power (including pump power), net, import, nuclear power (condensation), net, solar power (on-grid), sum of supply, wind | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | scb:TAB1011 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://statistikdatabasen.scb.se/api/v2/tables/TAB1011 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T03:00:52Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: SCB's updated time of the table (UTC) | none | utc time | 2026-10-09T06:00:00Z | 0 |
| `x_code` | SCB's code of the type of production (Tot, Vatten, Vind, Karn and others) (the source's name: Prodslag) | none | text | Gast, Imp, Karn, Kondens, Mottri, Mottrk, Solkraft, SumVarmeKraft, Tot, Vatten, Vind | 0 |

Variables (11):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `conventional_thermal_power` | Conventional thermal power, net (SumVarmeKraft) | MWh | 632 | 1974-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `hydro_power` | Hydro power including pump power, net (Vatten) | MWh | 632 | 1974-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `import` | Imports, including transit through Sweden from abroad (Imp) | MWh | 630 | 1974-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nuclear_power` | Nuclear power (condensation), net (Karn) | MWh | 629 | 1974-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `of_which_back_pressure_district_heating_work` | Of which back pressure, district heating (Mottrk) | MWh | 608 | 1976-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `of_which_back_pressure_industrial` | Of which back pressure, industrial (Mottri) | MWh | 608 | 1976-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `of_which_condensation` | Of which condensation (Kondens) | MWh | 630 | 1974-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `of_which_gas_turbine_etc` | Of which gas turbine and others (Gast) | MWh | 610 | 1974-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `solar_power` | Solar power (Solkraft) | MWh | 92 | 2019-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `sum_of_supply` | Sum of supply (Tot) | MWh | 632 | 1974-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `wind` | Wind power (Vind) | MWh | 356 | 1997-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `scripps_co2_mlo_monthly`

Atmospheric CO2 at Mauna Loa Observatory in one month, from the Scripps CO2 Program's in situ record.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1636.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; from 1958-03.
- **Revisions:** Rewritten whole as one snapshot by each run from the Scripps file; vintage is the file's Last-Modified.
- **Source:** scripps:co2_mlo_monthly Scripps CO2 Program, monthly_in_situ_co2_mlo.csv, https://keelinglabsites.ucsd.edu/websitedataco2/monthly_in_situ_co2_mlo.csv (linked from (https://scrippsco2.ucsd.edu/data/primary-mauna-loa-co2-record/)
- **Method note:** [`docs/methods/scripps_co2_mlo_monthly.md`](../methods/scripps_co2_mlo_monthly.md)
- **Cite as:** Scripps CO2 Program (Scripps Institution of Oceanography, UC San Diego). Primary Mauna Loa CO2 Record: monthly in situ CO2. Via the Energy Research Warehouse (ERW), table `scripps_co2_mlo_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: scripps:mlo on every row | none | text | scripps:mlo | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1958-03-01T00:00:00Z to 2026-09-01T00:00:00Z; 818 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 313.21 to 432.0; 1516 distinct | 0 |
| `unit` | The unit of the row's value | none | text | ppm | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1636 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1636 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Mauna Loa Observatory on every row, not a pricing node | none | text | Mauna Loa Observatory | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | scripps:co2_mlo_monthly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://keelinglabsites.ucsd.edu/websitedataco2/monthly_in_situ_co2_mlo.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T23:40:15Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's Last-Modified (UTC) | none | utc time | 2026-10-21T21:16:30Z | 0 |
| `x_station` | The station measured: MLO (Mauna Loa), or MKO (Maunakea's summit) for the months after Mauna Loa's 2022 eruption | none | text | MKO, MLO | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `co2` | Monthly mean CO2 concentration, adjusted to the 15th of the month, ppm of dry air | ppm | 818 | 1958-03-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `co2_seasonally_adjusted` | Monthly mean CO2 concentration, seasonally adjusted, ppm of dry air | ppm | 818 | 1958-03-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `singstat_singapore_electricity`

Singapore's monthly electricity generation (table M890831), or one row of its annual generation and consumption by sector (table M890841), from SingStat's Table Builder.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1009.

- **Time:** ts_utc is the month's or the year's first day at 00:00:00Z; freq P1M (M890831) or P1Y (M890841).
- **Revisions:** Rewritten whole as one snapshot by each run from SingStat's two tables; vintage is each table's dataLastUpdated.
- **Source:** singstat:M890831_M890841 Singapore Department of Statistics, SingStat Table Builder (https://tablebuilder.singstat.gov.sg/table/TS/M890831)
- **Method note:** [`docs/methods/singstat_singapore_electricity.md`](../methods/singstat_singapore_electricity.md)
- **Cite as:** Singapore Department of Statistics (SingStat). Table Builder M890831 and M890841: electricity generation, monthly; generation and consumption, annual. Via the Energy Research Warehouse (ERW), table `singstat_singapore_electricity`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: singstat:sg on every row | none | text | singstat:sg | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1975-01-01T00:00:00Z to 2026-06-01T00:00:00Z; 618 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 25900.0 to 60410400.0; 999 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is. Here: P1M for table M890831, P1Y for table M890841 | none | text | P1M, P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: SG on every row | none | text | SG | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1009 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The row as SingStat writes it, not a pricing node | none | text | Accommodation And Food Services, Commerce And Service-Related, Construction, Electricity Consumption, Electricity Generation, Financial And Insurance Activities, Households, Industrial-Related, Information And Communications, Manufacturing, Other Commerce And Service-Related, Other Industrial-Related, Others, Professional, Scientific & Technical, Administration & Support Activities, Real Estate Activities, Transport-Related, Utilities, Wholesale And Retail Trade | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | singstat:M890831_M890841 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://tablebuilder.singstat.gov.sg/api/table/tabledata/M890831, https://tablebuilder.singstat.gov.sg/api/table/tabledata/M890841 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T06:06:34Z, 2026-10-24T06:06:37Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The table's dataLastUpdated, as a date at 00:00Z | none | utc time | 2026-06-23T00:00:00Z, 2026-10-14T00:00:00Z | 0 |
| `x_table` | SingStat's table: M890831 (generation, monthly) or M890841 (generation and consumption, annual) | none | text | M890831, M890841 | 0 |
| `x_series` | SingStat's series number of the row (1, 2, 2.1, 2.1.1 and so on: its place in the table's hierarchy) (the source's name: seriesNo) | none | text | 1, 2, 2.1, 2.1.1, 2.1.2, 2.1.3, 2.1.4, 2.2, 2.2.1, 2.2.2, 2.2.3, 2.2.4, 2.2.5, 2.2.6, 2.2.7, 2.3, 2.4, 2.5 | 0 |

Variables (19):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `m890831_electricity_generation` | Electricity generation in the month (table M890831) | MWh | 618 | 1975-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `m890841_accommodation_and_food_services` | Annual electricity consumption, accommodation and food services | MWh | 20 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `m890841_commerce_and_service_related` | Annual electricity consumption, commerce and service-related | MWh | 20 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `m890841_construction` | Annual electricity consumption, construction | MWh | 20 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `m890841_electricity_consumption` | Electricity consumption in the year, total (table M890841) | MWh | 20 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `m890841_electricity_generation` | Electricity generation in the year (table M890841) | MWh | 51 | 1975-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `m890841_financial_and_insurance_activities` | Annual electricity consumption, financial and insurance activities | MWh | 20 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `m890841_households` | Annual electricity consumption, households | MWh | 20 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `m890841_industrial_related` | Annual electricity consumption, industrial-related | MWh | 20 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `m890841_information_and_communications` | Annual electricity consumption, information and communications | MWh | 20 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `m890841_manufacturing` | Annual electricity consumption, manufacturing | MWh | 20 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `m890841_other_commerce_and_service_related` | Annual electricity consumption, other commerce and service-related | MWh | 20 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `m890841_other_industrial_related` | Annual electricity consumption, other industrial-related | MWh | 20 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `m890841_others` | Annual electricity consumption, others | MWh | 20 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `m890841_professional_scientific_technical_administration_support_activities` | Annual electricity consumption, professional, scientific, technical, administration and support activities | MWh | 20 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `m890841_real_estate_activities` | Annual electricity consumption, real estate activities | MWh | 20 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `m890841_transport_related` | Annual electricity consumption, transport-related | MWh | 20 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `m890841_utilities` | Annual electricity consumption, utilities | MWh | 20 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `m890841_wholesale_and_retail_trade` | Annual electricity consumption, wholesale and retail trade | MWh | 20 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `smard_germany_monthly`

Germany's actual generation from one source, or its grid load, in one month, from the Bundesnetzagentur's SMARD.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1800.

- **Time:** ts_utc is the month's first day (SMARD's Start date, a month in German time); freq P1M; from 2015-01.
- **Revisions:** Rewritten whole as one snapshot by each run from SMARD's one download; vintage is not filled.
- **Source:** smard:market_data_month Bundesnetzagentur, SMARD market data (https://www.smard.de/en/downloadcenter/download-market-data)
- **Method note:** [`docs/methods/smard_germany_monthly.md`](../methods/smard_germany_monthly.md)
- **Cite as:** Bundesnetzagentur (SMARD). SMARD market data: actual generation and grid load. Via the Energy Research Warehouse (ERW), table `smard_germany_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: smard:de on every row | none | text | smard:de | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-09-01T00:00:00Z; 141 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 47418616.09; 1793 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: DE on every row | none | text | DE | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1800 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The column as SMARD writes it, not a pricing node | none | text | Biomass, Fossil gas, Hard coal, Hydro pumped storage, Hydropower, Lignite, Nuclear, Other conventional, Other renewable, Photovoltaics, Wind offshore, Wind onshore, grid load | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | smard:market_data_month | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.smard.de/nip-download-manager/nip/download/market-data | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T02:45:34Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1800 |
| `x_file` | The file of SMARD's download the value is read from (actual generation or actual consumption) | none | text | Actual_consumption_201501010000_202610240445_Month_2.csv, Actual_generation_201501010000_202610240445_Month_1.csv | 0 |

Variables (13):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `generation_biomass` | Actual generation from biomass | MWh | 141 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `generation_fossil_gas` | Actual generation from fossil gas | MWh | 141 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `generation_hard_coal` | Actual generation from hard coal | MWh | 141 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `generation_hydro_pumped_storage` | Actual generation from pumped storage hydro | MWh | 141 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `generation_hydropower` | Actual generation from hydropower | MWh | 141 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `generation_lignite` | Actual generation from lignite | MWh | 141 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `generation_nuclear` | Actual generation from nuclear | MWh | 108 | 2015-01-01T00:00:00Z | 2023-12-01T00:00:00Z |
| `generation_other_conventional` | Actual generation from other conventional sources | MWh | 141 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `generation_other_renewable` | Actual generation from other renewables | MWh | 141 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `generation_photovoltaics` | Actual generation from photovoltaics | MWh | 141 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `generation_wind_offshore` | Actual generation from offshore wind | MWh | 141 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `generation_wind_onshore` | Actual generation from onshore wind | MWh | 141 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `grid_load` | Grid load | MWh | 141 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `sne_panama_electricity_annual`

One year's value of one Panama electricity measure (gross generation by plant type or system, net production, maximum demand, load factor), from the Secretaria Nacional de Energia's historical series.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 569.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z; freq P1Y; 1970 to 2021.
- **Revisions:** Merged by (entity, variable, ts_utc): each run's years replace the same keys and older ones are kept; vintage is the workbook's Last-Modified.
- **Source:** sne:estadisticas_electricidad Secretaria Nacional de Energia, Panama, Generacion Historica Electrica (Serie 1970-2021), sheets C-GE-8 GenBruXTCen&PSis,80-21 and C-GE-14 ProdNet,DemMax,FactCar, listed at (https://www.energia.gob.pa/datos-y-estadisticas/)
- **Method note:** [`docs/methods/sne_panama.md`](../methods/sne_panama.md)
- **Cite as:** Secretaria Nacional de Energia, Panama. Generacion Historica Electrica (Serie 1970-2021), cuadros GE-8 (gross generation by plant type), GE-10 (monthly gross generation) and GE-14 (net production, maximum demand, load factor). Via the Energy Research Warehouse (ERW), table `sne_panama_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: sne:PA on every row | none | text | sne:PA | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1970-01-01T00:00:00Z to 2021-01-01T00:00:00Z; 52 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 13886520.0; 549 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: PA on every row | none | text | PA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 569 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Panama on every row, not a pricing node | none | text | Panama | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | sne:estadisticas_electricidad | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | http://www.energia.gob.pa/wp-content/uploads/2024/04/2-CEE-1970-2021-GE-Generaci%C3%B3n-El%C3%A9ctrica.xls | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T10:11:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's Last-Modified (UTC) | none | utc time | 2024-04-01T15:57:18Z | 0 |

Variables (17):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `generation_gross_biogas` | Gross generation, biogas | MWh | 6 | 2016-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `generation_gross_canal_authority` | Gross generation of the Panama Canal Authority's plants (from 2000) | MWh | 22 | 2000-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `generation_gross_gas_turbine_light_diesel` | Gross generation, gas turbines on light diesel | MWh | 42 | 1980-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `generation_gross_gas_turbine_marine_diesel` | Gross generation, gas turbines on marine diesel | MWh | 34 | 1988-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `generation_gross_hydro` | Gross generation, hydro plants | MWh | 42 | 1980-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `generation_gross_interconnected` | Gross generation of the national interconnected system | MWh | 42 | 1980-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `generation_gross_internal_combustion` | Gross generation, internal combustion (bunker or diesel) | MWh | 42 | 1980-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `generation_gross_isolated_systems` | Gross generation of the isolated systems (both a type and a part of the system) | MWh | 42 | 1980-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `generation_gross_light_diesel_other` | Gross generation, the sheet's Sub-Total (Diesel Liviano) | MWh | 42 | 1980-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `generation_gross_natural_gas` | Gross generation, natural gas (excluding the isolated systems' natural gas) | MWh | 4 | 2018-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `generation_gross_solar` | Gross generation, solar | MWh | 8 | 2014-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `generation_gross_steam_bunker` | Gross generation, steam plants (Vapor (Bunker); mostly coal from 2011, wholly coal from 2015) | MWh | 42 | 1980-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `generation_gross_total` | Gross generation, total (Cuadro GE-8; the Canal Authority's plants from 2000) | MWh | 42 | 1980-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `generation_gross_wind` | Gross generation, wind | MWh | 9 | 2013-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `load_factor` | Load factor (Cuadro GE-14) | pct | 49 | 1973-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `net_production` | Net production: net generation plus purchases from other companies (Cuadro GE-14) | MWh | 52 | 1970-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `peak_demand` | Maximum demand (Cuadro GE-14; neither sheet says whose) | MW | 49 | 1973-01-01T00:00:00Z | 2021-01-01T00:00:00Z |

### `sne_panama_generation_monthly`

Panama's total gross generation in one month, from the Secretaria Nacional de Energia's Cuadro GE-10.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 504.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; 1980-01 to 2021-12.
- **Revisions:** Merged by (entity, variable, ts_utc): each run's months replace the same keys and older ones are kept; vintage is the workbook's Last-Modified.
- **Source:** sne:estadisticas_electricidad Secretaria Nacional de Energia, Panama, Generacion Historica Electrica (Serie 1970-2021), sheet C-GE-10 GenBruTotMen,80-21, listed at (https://www.energia.gob.pa/datos-y-estadisticas/)
- **Method note:** [`docs/methods/sne_panama.md`](../methods/sne_panama.md)
- **Cite as:** Secretaria Nacional de Energia, Panama. Generacion Historica Electrica (Serie 1970-2021), cuadros GE-8 (gross generation by plant type), GE-10 (monthly gross generation) and GE-14 (net production, maximum demand, load factor). Via the Energy Research Warehouse (ERW), table `sne_panama_generation_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: sne:PA on every row | none | text | sne:PA | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1980-01-01T00:00:00Z to 2021-12-01T00:00:00Z; 504 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 135300.0 to 1280676.718807; 486 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: PA on every row | none | text | PA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 504 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Panama on every row, not a pricing node | none | text | Panama | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | sne:estadisticas_electricidad | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | http://www.energia.gob.pa/wp-content/uploads/2024/04/2-CEE-1970-2021-GE-Generaci%C3%B3n-El%C3%A9ctrica.xls | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T10:11:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's Last-Modified (UTC) | none | utc time | 2024-04-01T15:57:18Z | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `generation_gross_total` | Total gross generation in the month (the Canal Authority's plants included from 2000, so the series breaks there) | MWh | 504 | 1980-01-01T00:00:00Z | 2021-12-01T00:00:00Z |

### `sors_serbia_electricity_annual`

One item of Serbia's balance of electricity in 2024 (production, trade, transformation, own use, losses, final consumption by sector), from the statistics office's Energy Balances table 1.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 36.

- **Time:** ts_utc is 2024-01-01T00:00:00Z; freq P1Y.
- **Revisions:** Rewritten whole as one snapshot by each run from the saved publication; vintage is the PDF's Last-Modified.
- **Source:** sors:energy_balances_2024 Statistical Office of the Republic of Serbia (SORS), Energy Balances, 2024 (final data), table 1, Balance of Electricity in 2024
- **Method note:** [`docs/methods/sors_serbia_electricity_annual.md`](../methods/sors_serbia_electricity_annual.md)
- **Cite as:** Statistical Office of the Republic of Serbia (SORS). Energy Balances, 2024 (final data), table 1: Balance of Electricity in 2024. Via the Energy Research Warehouse (ERW), table `sors_serbia_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: sors:rs:<item>: total, a plant type, an energy-sector branch, a final sector or a renewable source | none | text | sors:rs:agriculture, sors:rs:autoproducers, sors:rs:chp, sors:rs:coal_mines, sors:rs:coal_processing, sors:rs:construction, sors:rs:district_heating, sors:rs:households, sors:rs:hydro, sors:rs:industry, sors:rs:oil_gas_extraction, sors:rs:other, sors:rs:other_consumers, sors:rs:pumped_storage, sors:rs:refineries, sors:rs:solar, sors:rs:thermal, sors:rs:total, sors:rs:transport, sors:rs:wind | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 18460.0 to 37488627.0; 31 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: RS on every row | none | text | RS | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 36 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: SORS's label in Serbian, not a pricing node | none | text | for example Ветроелектране, Грађевинарство, Губици; 31 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | sors:energy_balances_2024 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://publikacije.stat.gov.rs/G2026/pdf/G20265730.pdf | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T19:20:48Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The PDF's Last-Modified (UTC) | none | utc time | 2026-02-26T07:42:33Z | 0 |
| `x_label` | The row's label in Serbian, as SORS prints it (the same as node) | none | text | for example Ветроелектране, Грађевинарство, Губици; 31 distinct | 0 |

Variables (10):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `available_final` | Energy available for final consumption | MWh | 1 | 2024-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `exports` | Exports | MWh | 1 | 2024-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `final_consumption` | Final consumption, by sector | MWh | 7 | 2024-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `gross_available` | Gross available energy | MWh | 1 | 2024-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `gross_production` | Gross electricity production, total or by plant type | MWh | 7 | 2024-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `imports` | Imports | MWh | 1 | 2024-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `losses` | Losses | MWh | 1 | 2024-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `own_use` | Own use of the energy sector, by branch | MWh | 12 | 2024-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `primary_production` | Primary production of electricity (hydro, wind, solar) | MWh | 3 | 2024-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `transformation_input` | Electricity used in transformation (pumped storage, production of other energy) | MWh | 2 | 2024-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `ssb_norway_electricity_monthly`

One month's value of one line of Norway's electricity balance (generation by source, trade, consumption by industry and households, losses), from Statistics Norway's table 14091.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 5550.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; from 1993-01.
- **Revisions:** Rewritten whole as one snapshot by each run from SSB's JSON-stat answer; vintage is SSB's updated time.
- **Source:** ssb:14091 Statistics Norway, table 14091 (https://www.ssb.no/en/statbank/table/14091)
- **Method note:** [`docs/methods/ssb_norway_electricity_monthly.md`](../methods/ssb_norway_electricity_monthly.md)
- **Cite as:** Statistics Norway (SSB). Table 14091: Electricity balance (MWh). Via the Energy Research Warehouse (ERW), table `ssb_norway_electricity_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ssb:norway on every row | none | text | ssb:norway | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1993-01-01T00:00:00Z to 2026-09-01T00:00:00Z; 405 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 92.0 to 17782573.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: NO on every row | none | text | NO | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5550 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The line's name as SSB writes it, not a pricing node | none | text | for example Consumption in cottages and holiday houses, Consumption in dwellings, Consumption in electricity supply, WSW, construction; 26 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ssb:14091 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://data.ssb.no/api/v0/en/table/14091 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T02:25:07Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: SSB's updated time of the table (UTC) | none | utc time | 2026-10-19T06:00:00Z | 0 |
| `x_code` | SSB's code for the line (1, 1.1, ..., 7.42: its place in the balance) | none | number | 1.0 to 7.42; 26 distinct | 0 |

Variables (26):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption_in_cottages_and_holiday_houses` | Consumption in cottages and holiday houses | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `consumption_in_dwellings` | Consumption in dwellings | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `consumption_in_electricity_supply_wsw_construction` | Consumption in electricity supply, water, sewerage and waste, and construction, as SSB names the line | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `consumption_in_extraction_of_crude_petroleum_and_natural_gas` | Consumption in extraction of crude petroleum and natural gas | MWh | 201 | 2010-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `consumption_in_households` | Consumption in households | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `consumption_in_manufacturing_excluding_power_intensive_manufacturing` | Consumption in manufacturing excluding power-intensive manufacturing | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `consumption_in_mining_industries` | Consumption in mining industries | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `consumption_in_power_intensive_manufacturing` | Consumption in power-intensive manufacturing | MWh | 405 | 1993-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `consumption_in_primary_industries` | Consumption in primary industries | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `consumption_in_production_of_aluminium_and_other_metals` | Consumption in production of aluminium and other metals | MWh | 201 | 2010-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `consumption_in_production_of_industrial_chemicals` | Consumption in production of industrial chemicals | MWh | 201 | 2010-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `consumption_in_production_of_iron_steel_and_ferro_alloys` | Consumption in production of iron, steel and ferro-alloys | MWh | 201 | 2010-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `consumption_in_production_of_pulp_paper_and_cardboard` | Consumption in production of pulp, paper and cardboard | MWh | 201 | 2010-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `consumption_in_secondary_industries` | Consumption in secondary industries | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `consumption_in_tertiary_industries` | Consumption in tertiary industries | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `export` | Exports | MWh | 405 | 1993-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `grid_loss_and_statistical_difference` | Grid loss and statistical difference | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `gross_electricity_consumption` | Gross electricity consumption | MWh | 405 | 1993-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `hydro_power_generation` | Hydro power generation | MWh | 405 | 1993-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `import` | Imports | MWh | 405 | 1993-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `net_electricity_consumption` | Net electricity consumption | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pump_storage_consumption` | Pump storage consumption | MWh | 405 | 1993-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `solar_power_generation` | Solar power generation | MWh | 81 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `thermal_power_generation` | Thermal power generation | MWh | 405 | 1993-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `total_electricity_generation` | Total electricity generation | MWh | 405 | 1993-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `wind_power_generation` | Wind power generation | MWh | 333 | 1999-01-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `stat_kz_kazakhstan_electricity_annual`

One year's value of one item of the electricity column of Kazakhstan's fuel and energy balance (output by plant class, trade, own use, losses, consumption by sector), from the Bureau of National Statistics.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 84.

- **Time:** ts_utc is the year's first day at 00:00:00Z; freq P1Y; 2022 to 2025.
- **Revisions:** Rewritten whole as one snapshot by each run from the yearly workbooks; vintage is each workbook's Last-Modified.
- **Source:** stat_kz:fuel_energy_balance_physical Bureau of National Statistics of the Agency for Strategic Planning and Reforms of the Republic of Kazakhstan, Fuel and energy balance of the Republic of Kazakhstan, in physical terms
- **Method note:** [`docs/methods/stat_kz_kazakhstan_electricity_annual.md`](../methods/stat_kz_kazakhstan_electricity_annual.md)
- **Cite as:** Bureau of National Statistics of Kazakhstan. Fuel and energy balance of the Republic of Kazakhstan, in physical terms (2022 to 2025), the electricity column. Via the Energy Research Warehouse (ERW), table `stat_kz_kazakhstan_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statkz:kz:<item>: a plant class, a balance item or a sector | none | text | statkz:kz:agriculture, statkz:kz:biogas, statkz:kz:chpp_main, statkz:kz:chpp_secondary, statkz:kz:consumption, statkz:kz:exports, statkz:kz:households, statkz:kz:hydro, statkz:kz:imports, statkz:kz:industry, statkz:kz:losses, statkz:kz:other, statkz:kz:output, statkz:kz:own_use, statkz:kz:services, statkz:kz:solar, statkz:kz:statistical_difference, statkz:kz:tpp_main, statkz:kz:tpp_secondary, statkz:kz:transport, statkz:kz:wind | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1208814.998 to 123782240.2; 82 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: KZ on every row | none | text | KZ | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 84 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The row's label in the balance, not a pricing node | none | text | for example 3. Final energy consumption, Agriculture/forestry, Combined Heat and Power Plants (CHPP) (main activity); 35 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | stat_kz:fuel_energy_balance_physical | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://stat.gov.kz/api/iblock/element/205511/file/en/, https://stat.gov.kz/api/iblock/element/411633/file/en/, https://stat.gov.kz/api/iblock/element/411634/file/en/, https://stat.gov.kz/api/iblock/element/75937/file/en/ | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T10:27:38Z, 2026-10-25T10:28:52Z, 2026-10-25T10:28:57Z, 2026-10-25T10:29:01Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The year's workbook's Last-Modified (UTC) | none | utc time | 2023-08-01T11:06:34Z, 2024-08-01T13:42:57Z, 2025-08-01T04:35:25Z, 2026-08-03T06:42:05Z | 0 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` | Final consumption, total or by sector | MWh | 28 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `exports` | Exports (written positive) | MWh | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `generation` | Electricity output, total or by plant class | MWh | 36 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `imports` | Imports | MWh | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `losses` | Losses | MWh | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `own_use` | Own use | MWh | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `statistical_difference` | Statistical difference | MWh | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `stat_tj_tajikistan_electricity_annual`

One year's value of Tajikistan's electricity output by plant type, trade, losses or consumption by sector, from the Agency on Statistics' analytical table 11.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 475.

- **Time:** ts_utc is the year's first day at 00:00:00Z; freq P1Y; 1991 to 2025.
- **Revisions:** Rewritten whole as one snapshot by each run from the saved workbook; vintage is the workbook's Last-Modified.
- **Source:** stat_tj:analytical_table_11 Agency on Statistics under the President of the Republic of Tajikistan, analytical table: Electricity output, trade and consumption, 1991-2025 (www.stat.tj)
- **Method note:** [`docs/methods/stat_tj_tajikistan_electricity_annual.md`](../methods/stat_tj_tajikistan_electricity_annual.md)
- **Cite as:** Agency on Statistics under the President of the Republic of Tajikistan. Analytical table: Electricity output, trade and consumption, 1991-2025. Via the Energy Research Warehouse (ERW), table `stat_tj_tajikistan_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: tajstat:tj:<item> | none | text | tajstat:tj:agriculture, tajstat:tj:construction, tajstat:tj:consumption, tajstat:tj:discrepancy, tajstat:tj:exports, tajstat:tj:households, tajstat:tj:hydro, tajstat:tj:imports, tajstat:tj:industry, tajstat:tj:losses, tajstat:tj:other_sectors, tajstat:tj:output, tajstat:tj:thermal, tajstat:tj:transport | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1991-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 35 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1000000.0 to 24000000.0; 149 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: TJ on every row | none | text | TJ | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 475 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The row's label, not a pricing node | none | text | Agriculture, Construction, Discrepancy, Exports, Households, Hydropower, Imports, Industry, Losses, Other sectors, Output, Thermal power, Total internal consumption (by sector), Transport | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | stat_tj:analytical_table_11 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.stat.tj/wp-content/uploads/2026/09/table_11-1.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T10:07:12Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's Last-Modified (UTC) | none | utc time | 2026-09-26T05:32:16Z | 0 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` | Consumption, total or by sector | MWh | 245 | 1991-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `distribution_losses` | Distribution losses | MWh | 35 | 1991-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `exports` | Exports | MWh | 35 | 1991-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `generation` | Electricity output, total or by plant type (hydropower, thermal power) | MWh | 104 | 1991-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `imports` | Imports | MWh | 35 | 1991-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `statistical_difference` | Discrepancy, as the table names it | MWh | 21 | 1991-01-01T00:00:00Z | 2014-01-01T00:00:00Z |

### `statat_austria_electricity_annual`

One year's value of one item of Austria's electricity balance (trade, transformation input and output by plant type, owner and fuel, final energy use by sector, energy sector use by branch), from Statistics Austria's energy balances.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 6675.

- **Time:** ts_utc is the year's first day at 00:00:00Z; freq P1Y; 1970 to 2024.
- **Revisions:** Rewritten whole as one snapshot by each run from the saved spreadsheet; vintage is the file's Last-Modified.
- **Source:** statat:energy_balances_1970_2024 STATISTIK AUSTRIA, Energy balances Austria 1970-2024, sheet Electricity
- **Method note:** [`docs/methods/statat_austria_electricity_annual.md`](../methods/statat_austria_electricity_annual.md)
- **Cite as:** Statistics Austria (Statistik Austria). Energy balances Austria 1970-2024, sheet Electricity. Via the Energy Research Warehouse (ERW), table `statat_austria_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statat_ele:at (a total), statat_ele:<plant>[:<owner>[:<fuel>[:<sub-fuel>]]], statat_ele:sector:<sector> or statat_ele:branch:<branch> | none | text | for example statat_ele:at, statat_ele:branch:blast_furnaces, statat_ele:branch:coke_ovens; 117 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1970-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 55 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -6779832.094 to 78753844.014; 4246 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: AT on every row | none | text | AT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 6675 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The sheet's labels joined, not a pricing node | none | text | for example Energy sector use, Energy sector use / Blast furnaces, Energy sector use / Coke ovens; 124 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statat:energy_balances_1970_2024 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.statistik.at/fileadmin/pages/99/energy_balances_austria_1970-2024_data.ods | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T23:33:09Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The spreadsheet's Last-Modified (UTC) | none | utc time | 2025-11-07T08:00:30Z | 0 |

Variables (8):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `energy_sector_use` | The energy sector's use, by branch | MWh | 185 | 1970-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `exports` | Exports of electricity | MWh | 55 | 1970-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `final_energy_use` | Final energy use, by sector | MWh | 1265 | 1970-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `gross_inland_consumption` | Gross inland consumption of electricity (its net imports) | MWh | 55 | 1970-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `imports` | Imports of electricity | MWh | 55 | 1970-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `transformation_input` | Electricity used as transformation input | MWh | 165 | 1970-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `transformation_output` | Transformation output: electricity generated, by plant type, owner and fuel | MWh | 4840 | 1970-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `transport_losses` | Transport losses | MWh | 55 | 1970-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `statat_austria_electricity_monthly`

One month's value of Austria's net electricity production by source or of its monthly balance, from Statistics Austria's monthly electricity statistics.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 793.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; from 2023-01.
- **Revisions:** Rewritten whole as one snapshot by each run from the yearly files; vintage is each file's Last-Modified.
- **Source:** statat:monthly_electricity_statistics STATISTIK AUSTRIA, Monthly electricity statistics (MEle2023 to MEle2026)
- **Method note:** [`docs/methods/statat_austria_electricity_monthly.md`](../methods/statat_austria_electricity_monthly.md)
- **Cite as:** Statistics Austria (Statistik Austria). Monthly electricity statistics (MEle2023 to MEle2026). Via the Energy Research Warehouse (ERW), table `statat_austria_electricity_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statat_mele:at or statat_mele:at:<source> | none | text | statat_mele:at, statat_mele:at:coal, statat_mele:at:combustible_renewables, statat_mele:at:conventional_thermal, statat_mele:at:hydro, statat_mele:at:mixed_hydro, statat_mele:at:natural_gas, statat_mele:at:oil, statat_mele:at:other_combustible_fuels_non_renewable, statat_mele:at:pure_hydro, statat_mele:at:solar, statat_mele:at:wind | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 43 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 30300.0 to 7240000.0; 785 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: AT on every row | none | text | AT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 793 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The year and the row, not a pricing node | none | text | for example 2023 Conventional thermal, 2023 Hydro, 2023 Total consumption (calculated); 74 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statat:monthly_electricity_statistics | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.statistik.at/fileadmin/pages/99/MEle2023.ods, https://www.statistik.at/fileadmin/pages/99/MEle2024.ods, https://www.statistik.at/fileadmin/pages/99/MEle2025.ods, https://www.statistik.at/fileadmin/pages/99/MEle2026.ods | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T03:04:45Z, 2026-10-26T03:04:51Z, 2026-10-26T03:04:56Z, 2026-10-26T03:05:01Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The year's file's Last-Modified (UTC) | none | utc time | 2024-10-31T08:01:55Z, 2025-04-02T07:00:09Z, 2026-04-28T09:40:09Z, 2026-09-23T07:09:28Z | 0 |

Variables (8):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` | Consumption | MWh | 43 | 2023-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `exports` | Exports | MWh | 43 | 2023-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `exports_to_eu` | Exports to the EU | MWh | 43 | 2023-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `imports` | Imports | MWh | 43 | 2023-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `imports_from_eu` | Imports from the EU | MWh | 43 | 2023-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `losses` | Losses | MWh | 43 | 2023-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_production` | Net electricity production, total or by source | MWh | 492 | 2023-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `pumped_storage_use` | Electricity used by pumped storage | MWh | 43 | 2023-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `statbank_moldova_electricity_monthly`

One month's value of one electricity indicator of Moldova's stocks, inputs and consumption, from the National Bureau of Statistics' StatBank table ENE010100.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 980.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; from 2015-01.
- **Revisions:** Rewritten whole as one snapshot by each run from one JSON-stat query; vintage is not filled.
- **Source:** statbank_md:ENE010100 National Bureau of Statistics of the Republic of Moldova, StatBank, Energy resources, monthly series (https://statbank.statistica.md/PxWeb/pxweb/en/40%20Statistica%20economica/40%20Statistica%20economica__15%20ENE__serii%20lunare/ENE010100.px/)
- **Method note:** [`docs/methods/statbank_moldova_electricity_monthly.md`](../methods/statbank_moldova_electricity_monthly.md)
- **Cite as:** National Bureau of Statistics of the Republic of Moldova (StatBank). StatBank table ENE010100: Stocks, inputs and electricity consumption, monthly. Via the Energy Research Warehouse (ERW), table `statbank_moldova_electricity_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statbank_md:md on every row | none | text | statbank_md:md | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 140 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 583245.2; 743 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: MD on every row | none | text | MD | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 980 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The indicator as StatBank writes it, not a pricing node | none | text | Acquired from other sources, Export, Gross inland consumption, Import, Production, Stock change, of which: consumed in the residential sector | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statbank_md:ENE010100 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://statbank.statistica.md/PxWeb/api/v1/en/40%20Statistica%20economica/15%20ENE/serii%20lunare/ENE010100.px | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T08:30:00Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 980 |
| `x_code` | StatBank's code of the indicator (1 to 7) | none | integer | 1, 2, 3, 4, 5, 6, 7 | 0 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `acquired_from_other_sources` | Acquired from other sources | MWh | 140 | 2015-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `exports` | Exports | MWh | 140 | 2015-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `gross_inland_consumption` | Gross inland consumption | MWh | 140 | 2015-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `imports` | Imports | MWh | 140 | 2015-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `production` | Production (not called gross or net by the bureau) | MWh | 140 | 2015-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `residential_consumption` | Of which consumed in the residential sector | MWh | 140 | 2015-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `stock_change` | Stock change | MWh | 140 | 2015-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `statbel_be_electricity_production_annual`

Belgium's gross electricity production from one energy product (or in total) in one year, from Statbel's beSTAT.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 200.

- **Time:** ts_utc is the year's first day at 00:00:00Z; freq P1Y; 2018 to 2025.
- **Revisions:** Rewritten whole as one snapshot by each run from beSTAT's CSV; vintage is not filled.
- **Source:** statbel:bestat_gross_electricity_production Statbel (Directorate-General Statistics, Statistics Belgium), beSTAT, Evolution Gross electricity production 2025
- **Method note:** [`docs/methods/statbel_be_electricity_production_annual.md`](../methods/statbel_be_electricity_production_annual.md)
- **Cite as:** Statistics Belgium (Statbel). beSTAT: Evolution Gross electricity production 2025, by energy product. Via the Energy Research Warehouse (ERW), table `statbel_be_electricity_production_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statbel_gep:be:total or statbel_gep:be:<product group>:<product> | none | text | statbel_gep:be:manufactered_gases:blast_furnace_gas, statbel_gep:be:manufactered_gases:coke_oven_gas, statbel_gep:be:manufactered_gases:other_recovered_gases, statbel_gep:be:natural_gas:natural_gas, statbel_gep:be:non_renewable_waste:non_renewable_industrial_waste, statbel_gep:be:non_renewable_waste:non_renewable_municipal_waste, statbel_gep:be:nuclear_energy:nuclear_energy, statbel_gep:be:oil_and_petroleum_products:gasoil_diesel, statbel_gep:be:oil_and_petroleum_products:heavy_fuel_oil, statbel_gep:be:oil_and_petroleum_products:lpg, statbel_gep:be:oil_and_petroleum_products:other_kerosene, statbel_gep:be:oil_and_petroleum_products:refinery_gas, statbel_gep:be:other_sources:other_sources, statbel_gep:be:other_sources:pumped_hydro, statbel_gep:be:other_sources:recovered_heat, statbel_gep:be:renewables_and_biofuels:biodiesel, statbel_gep:be:renewables_and_biofuels:biogas, statbel_gep:be:renewables_and_biofuels:natural_hydro, statbel_gep:be:renewables_and_biofuels:other_liquid_biofuels, statbel_gep:be:renewables_and_biofuels:renewable_municipal_waste, statbel_gep:be:renewables_and_biofuels:solar_photovoltaic, statbel_gep:be:renewables_and_biofuels:solid_biofuels, statbel_gep:be:renewables_and_biofuels:wind, statbel_gep:be:solid_fossil_fuels:other_bituminous_coal, statbel_gep:be:total | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 300.0 to 100481800.0; 188 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: BE on every row | none | text | BE | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 200 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The product levels as Statbel writes them, not a pricing node | none | text | All products, Manufactered gases: Blast furnace gas, Manufactered gases: Coke oven gas, Manufactered gases: Other recovered gases, Natural gas: Natural gas, Non-renewable waste: Non-renewable industrial waste, Non-renewable waste: Non-renewable municipal waste, Nuclear energy: Nuclear energy, Oil and petroleum products: Gasoil/diesel, Oil and petroleum products: Heavy fuel oil, Oil and petroleum products: LPG, Oil and petroleum products: Other kerosene, Oil and petroleum products: Refinery gas, Other sources: Other sources, Other sources: Pumped hydro, Other sources: Recovered heat, Renewables and biofuels: Biodiesel, Renewables and biofuels: Biogas, Renewables and biofuels: Natural hydro, Renewables and biofuels: Other liquid biofuels, Renewables and biofuels: Renewable municipal waste, Renewables and biofuels: Solar photovoltaic, Renewables and biofuels: Solid biofuels, Renewables and biofuels: Wind, Solid fossil fuels: Other bituminous coal | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statbel:bestat_gross_electricity_production | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://bestat.statbel.fgov.be/bestat/api/views/cd9605c7-3f71-4527-9404-40bfb81c8523/result/CSV | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T00:03:53Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 200 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `gross_electricity_production` | Gross electricity production from the energy product in the year (Statbel's GWh times 1,000) | MWh | 200 | 2018-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `statee_estonia_electricity_monthly`

One month's value of Estonia's electricity production (total, hydro, wind, solar), imports or exports, from Statistics Estonia's table KE21.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1344.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; from 2005-01.
- **Revisions:** Rewritten whole as one snapshot by each run from one JSON-stat query; vintage is not filled.
- **Source:** statee:KE21 Statistics Estonia, table KE21 (https://andmed.stat.ee/en/stat/majandus__energeetika__energia-tarbimine-ja-tootmine__luhiajastatistika/KE21)
- **Method note:** [`docs/methods/statee_estonia_electricity_monthly.md`](../methods/statee_estonia_electricity_monthly.md)
- **Cite as:** Statistics Estonia. Table KE21: Electricity production, imports, exports and sale (monthly). Via the Energy Research Warehouse (ERW), table `statee_estonia_electricity_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statee:ee on every row | none | text | statee:ee | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2005-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 260 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 200.0 to 1375000.0; 818 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: EE on every row | none | text | EE | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1344 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The indicator as Statistics Estonia writes it, not a pricing node | none | text | Electricity production from hydro energy, GWh, Electricity production from solar energy, GWh, Electricity production from wind energy, GWh, Exports of electricity, GWh, Imports of electricity, GWh, Total electricity production, GWh | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statee:KE21 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://andmed.stat.ee/api/v1/en/stat/majandus/energeetika/energia-tarbimine-ja-tootmine/luhiajastatistika/KE21.PX | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T05:03:06Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1344 |
| `x_code` | Statistics Estonia's code of the indicator (PROD_E, PROD_E_HYDR, PROD_E_WIND, PROD_E_SOLAR, IMPORTS, EXPORTS) | none | text | EXPORTS, IMPORTS, PROD_E, PROD_E_HYDR, PROD_E_SOLAR, PROD_E_WIND | 0 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `electricity_production_from_hydro_energy` | Electricity production from hydro energy | MWh | 260 | 2005-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `electricity_production_from_solar_energy` | Electricity production from solar energy | MWh | 44 | 2023-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `electricity_production_from_wind_energy` | Electricity production from wind energy | MWh | 260 | 2005-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `exports_of_electricity` | Exports of electricity | MWh | 260 | 2005-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `imports_of_electricity` | Imports of electricity | MWh | 260 | 2005-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `total_electricity_production` | Total electricity production | MWh | 260 | 2005-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `statfi_finland_electricity_monthly`

One month's value of one line of Finland's electricity supply and consumption (generation by source, net imports by country, total consumption), from Statistics Finland's table 12su.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 6350.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M; from 1992-01.
- **Revisions:** Rewritten whole as one snapshot by each run from one JSON-stat query; vintage is the answer's updated time.
- **Source:** statfi:12su Statistics Finland, StatFin, table 12su (https://pxdata.stat.fi/PxWeb/pxweb/en/StatFin/StatFin__ehk/statfin_ehk_pxt_12su.px/)
- **Method note:** [`docs/methods/statfi_finland_electricity_monthly.md`](../methods/statfi_finland_electricity_monthly.md)
- **Cite as:** Statistics Finland. StatFin table 12su: Supplies and total consumption of electricity, monthly. Via the Energy Research Warehouse (ERW), table `statfi_finland_electricity_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statfi:fi on every row | none | text | statfi:fi | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1992-01-01T00:00:00Z to 2026-06-01T00:00:00Z; 414 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -942000.0 to 9629000.0; 2908 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: FI on every row | none | text | FI | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 6350 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The line as Statistics Finland writes it, code included, not a pricing node | none | text | 1 TOTAL ELECTRICITY GENERATION, 1.1 Hydro power, 1.2 Wind power, 1.3 Solar power, 1.4 Nuclear power, 1.5 Combined heat and power (CHP), 1.5.1 CHP, district heating, 1.5.2 CHP, industri, 1.5.3 Micro-CHP, 1.6 Conventional condensing power, 2 NET IMPORTS OF ELECTRICITY, 2.1 Norway, 2.2 Sweden, 2.3 Russia, 2.4 Estonia, SSS TOTAL ELECTRICITY CONSUMPTION | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statfi:12su | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://pxdata.stat.fi/PxWeb/api/v1/en/StatFin/ehk/12su.px | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T04:09:36Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The JSON-stat answer's updated time (UTC) | none | utc time | 2026-09-23T05:00:00Z | 0 |
| `x_code` | Statistics Finland's code of the line (1, 1.1, ..., 2.4: its place in the table) | none | text | 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.5.1, 1.5.2, 1.5.3, 1.6, 2, 2.1, 2.2, 2.3, 2.4, SSS | 0 |

Variables (16):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `chp_district_heating` | CHP, district heating | MWh | 414 | 1992-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `chp_industri` | CHP, industry | MWh | 414 | 1992-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `combined_heat_and_power_chp` | Combined heat and power (CHP) | MWh | 414 | 1992-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `conventional_condensing_power` | Conventional condensing power | MWh | 414 | 1992-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `estonia` | Net imports from Estonia | MWh | 236 | 2006-11-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `hydro_power` | Hydro power | MWh | 414 | 1992-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `micro_chp` | Micro-CHP | MWh | 318 | 2000-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `net_imports_of_electricity` | Net imports of electricity | MWh | 414 | 1992-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `norway` | Net imports from Norway | MWh | 414 | 1992-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `nuclear_power` | Nuclear power | MWh | 414 | 1992-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `russia` | Net imports from Russia | MWh | 414 | 1992-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `solar_power` | Solar power | MWh | 414 | 1992-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `sweden` | Net imports from Sweden | MWh | 414 | 1992-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `total_electricity_consumption` | Total electricity consumption | MWh | 414 | 1992-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `total_electricity_generation` | Total electricity generation | MWh | 414 | 1992-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `wind_power` | Wind power | MWh | 414 | 1992-01-01T00:00:00Z | 2026-06-01T00:00:00Z |

### `statsbots_botswana_electricity_monthly`

One month's Botswana local generation, imports or distribution, or one quarter's generation or imports by source, from Statistics Botswana's Electricity Stats Brief.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 383.

- **Time:** ts_utc is the month's 1st (freq P1M) or the quarter's first day (freq P3M) at 00:00:00Z.
- **Revisions:** Merged by (entity, variable, ts_utc): each run's periods replace the same keys and older ones are kept; vintage is the brief's Last-Modified.
- **Source:** statsbots:electricity_stats_brief Statistics Botswana, Electricity Generation and Distribution Stats Brief (tables 2, 3, 7, 10 and 11), linked from (https://www.statsbots.org.bw/)
- **Method note:** [`docs/methods/statsbots_botswana_electricity_monthly.md`](../methods/statsbots_botswana_electricity_monthly.md)
- **Cite as:** Statistics Botswana. Electricity Generation and Distribution Stats Brief (tables 2, 3, 7, 10 and 11). Via the Energy Research Warehouse (ERW), table `statsbots_botswana_electricity_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statsbots_bw:BW on every row | none | text | statsbots_bw:BW | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2016-01-01T00:00:00Z to 2026-06-01T00:00:00Z; 126 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 3136.5 to 894024.9; 383 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is. Here: P1M for generation, imports and distribution; P3M for the brief's one quarter by source | none | text | P1M, P3M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: BW on every row | none | text | BW | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 383 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Botswana on every row, not a pricing node | none | text | Botswana | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statsbots:electricity_stats_brief | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.statsbots.org.bw/sites/default/files/Electricity%20Generation%20and%20Distribution%20Stats%20Brief%2C%20Second%20Quarter%202026.pdf | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T10:49:35Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The brief PDF's Last-Modified (UTC) | none | utc time | 2026-09-29T07:03:14Z | 0 |

Variables (9):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `distribution` | Electricity distributed in the month | MWh | 125 | 2016-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `generation` | Electricity generated locally in the month | MWh | 126 | 2016-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `generation_coal` | Generation from coal in the quarter | MWh | 1 | 2026-04-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `generation_diesel` | Generation from diesel in the quarter | MWh | 1 | 2026-04-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `generation_solar` | Generation from solar in the quarter | MWh | 1 | 2026-04-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `imports` | Electricity imported in the month | MWh | 126 | 2016-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `imports_cross_border` | Cross-border imports in the quarter | MWh | 1 | 2026-04-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `imports_eskom` | Imports from Eskom in the quarter | MWh | 1 | 2026-04-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `imports_sapp_markets` | Imports from the SAPP markets in the quarter | MWh | 1 | 2026-04-01T00:00:00Z | 2026-04-01T00:00:00Z |

### `statsmu_mauritius_electricity_annual`

One year's value of one Mauritius electricity measure (generation by source, renewable share, sales, capacity, peak demand), from Statistics Mauritius' Energy and Water Statistics.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 79.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z; freq P1Y; 2017 to 2025 (Tables 7 and 8: 2022 to 2025).
- **Revisions:** Merged by (entity, variable, ts_utc): each run's years replace the same keys and older ones are kept; vintage is the edition's workbook's Last-Modified.
- **Source:** statsmu:energy_water_statistics Statistics Mauritius, Economic and Social Indicators, Energy and Water Statistics 2025 (Issue 1929) and 2023 (Issue 1791), Tables 1, 7 and 8 (https://statsmauritius.govmu.org/Pages/Statistics/ESI/Energy_Water/Energy_Water_Yr25.aspx)
- **Method note:** [`docs/methods/statsmu_mauritius_electricity_annual.md`](../methods/statsmu_mauritius_electricity_annual.md)
- **Cite as:** Statistics Mauritius. Economic and Social Indicators, Energy and Water Statistics (2023 and 2025 editions), Tables 1, 7 and 8. Via the Energy Research Warehouse (ERW), table `statsmu_mauritius_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statsmu:MU (the Republic of Mauritius) on every row | none | text | statsmu:MU | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 7.6 to 3551556.36; 79 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: MU on every row | none | text | MU | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 79 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Mauritius on every row, not a pricing node | none | text | Mauritius | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statsmu:energy_water_statistics | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://statsmauritius.govmu.org/Documents/Statistics/ESI/2024/EI1791/Energy_Water_Yr23_070624.xlsx, https://statsmauritius.govmu.org/Documents/Statistics/ESI/2026/EI1929/ESI_Energy_Yr25_050626.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T10:33:20Z, 2026-10-24T10:33:57Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The edition's workbook's Last-Modified (UTC) | none | utc time | 2024-06-07T07:40:46Z, 2026-06-05T04:58:07Z | 0 |

Variables (16):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity_effective` | Effective capacity (Table 7; not defined by the source) | MW | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_installed` | Installed capacity, including plants not exporting to the CEB (Table 7) | MW | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `electricity_sold` | The CEB's electricity sales (Table 1) | MWh | 9 | 2017-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `generation_bagasse` | Generation from bagasse (and fuelwood in the 2025 edition) (Table 8) | MWh | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `generation_coal` | Generation from coal (Table 8) | MWh | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `generation_fuel_oil_diesel` | Generation from fuel oil and diesel (Table 8) | MWh | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `generation_gas_turbine_kerosene` | Generation from gas turbines on kerosene (Table 8) | MWh | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `generation_hydro` | Generation from hydro (Table 8) | MWh | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `generation_landfill_gas` | Generation from landfill gas (Table 8) | MWh | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `generation_photovoltaic` | Generation from photovoltaics (Table 8) | MWh | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `generation_renewable` | Generation from renewables (Table 8) | MWh | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `generation_total` | Electricity generation, every producer's, own use included (Table 1) | MWh | 9 | 2017-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `generation_wind` | Generation from wind (Table 8) | MWh | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `peak_demand_mauritius` | Peak demand, island of Mauritius (Table 7) | MW | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `peak_demand_rodrigues` | Peak demand, Rodrigues (Table 7) | MW | 4 | 2022-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `renewable_share` | Share of generation from renewables (Table 1) | pct | 9 | 2017-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `usace_nid_dams`

One dam (or a dam's associated structure) in the U.S. Army Corps of Engineers' National Inventory of Dams.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 92788.

- **Time:** No time column; vintage is the inventory's data-last-updated date; year_completed is the dam's completion year.
- **Revisions:** Rewritten whole as one snapshot by each run from the inventory's national CSV; vintage is the date the inventory says its data were last updated.
- **Source:** usace:nid U.S. Army Corps of Engineers, National Inventory of Dams (https://nid.sec.usace.army.mil/)
- **Method note:** [`docs/methods/usace_nid_dams.md`](../methods/usace_nid_dams.md)
- **Cite as:** U.S. Army Corps of Engineers (USACE). National Inventory of Dams (national download). Via the Energy Research Warehouse (ERW), table `usace_nid_dams`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: usace_nid:<Federal ID> (unique; the NID ID repeats for associated structures and is in nid_id) | none | text | for example usace_nid:AK00001, usace_nid:AK00002, usace_nid:AK00003; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: dam on every row | none | text | dam | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The dam's name | none | text | for example "E" Pond Treatment, #1 Tailings Pond, #154; more than 5000 distinct | 4335 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state or territory> | none | text | for example US-AK, US-AL, US-AR; 52 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: As the inventory gives it; empty where only one coordinate of the two is given (that one is in coordinate_given) | degree | number | 0.0 to 71.266667; more than 5000 distinct | 162 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: As the inventory gives it; empty where only one coordinate of the two is given (that one is in coordinate_given) | degree | number | -176.6873 to 144.7061; more than 5000 distinct | 162 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: Not filled: the inventory gives no MW | MW | empty | no cell holds a value | 92788 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 92788 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 92788 |
| `operator` | The operator or owner, as the publisher writes it. Here: The owners' names | none | text | for example & FRY;OLSEN;RUMFORD, & FRY;OLSON;RUMFORDS, (7) RANCH C/O GABRIELLE MANIGAULT; more than 5000 distinct | 6829 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | usace:nid | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://nid.sec.usace.army.mil/api/nation/csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T13:59:04Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The inventory's data-last-updated date (YYYY-MM-DD) | none | date | 2026-10-22 | 0 |
| `nid_id` | The NID ID (shared by a dam's associated structures) (the source's name: NID ID) | none | text | for example AK00001, AK00002, AK00003; more than 5000 distinct | 3: The inventory leaves it blank |
| `owner_types` | The owner types, joined by ; (Federal, State, Local Government, Private, Public Utility, Tribal Government, Not Listed) (the source's name: Owner Types) | none | text | for example Federal, Federal;Local Government, Federal;Private; 27 distinct | 12: The inventory leaves it blank |
| `primary_owner_type` | The primary owner type (the source's name: Primary Owner Type) | none | text | Federal, Local Government, Not Listed, Private, Public Utility, State, Tribal Government | 12: The inventory leaves it blank |
| `primary_purpose` | The dam's primary purpose (Recreation, Flood Risk Reduction, Hydroelectric, Irrigation, Water Supply and others) (the source's name: Primary Purpose) | none | text | Debris Control, Fire Protection, Stock, Or Small Fish Pond, Fish and Wildlife Pond, Flood Risk Reduction, Grade Stabilization, Hydroelectric, Irrigation, Navigation, Other, Recreation, Tailings, Water Supply | 5873: The inventory leaves it blank |
| `purposes` | All the dam's purposes, joined by ; (the source's name: Purposes) | none | text | for example Debris Control, Debris Control;Debris Control;Other;Other, Debris Control;Fire Protection, Stock, Or Small Fish Pond; 571 distinct | 5869: The inventory leaves it blank |
| `associated_structure` | Yes when the row is an associated structure of a dam, else No (the source's name: Is Associated Structure?) | none | text | No, Yes | 0 |
| `county` | The county (the source's name: County) | none | text | for example Abbeville, Acadia, Accomack; 1792 distinct | 155: The inventory leaves it blank |
| `river` | The river or stream name, as published (the source's name: River or Stream Name) | none | text | for example "Y" Branch, #Name?, (Dry Water Course); more than 5000 distinct | 9047: The inventory leaves it blank |
| `primary_dam_type` | The primary dam type (Earth, Concrete, Gravity, Rockfill, Arch and others) (the source's name: Primary Dam Type) | none | text | Arch, Buttress, Concrete, Earth, Gravity, Masonry, Multi-Arch, Other, Rockfill, Roller-Compacted Concrete, Stone, Timber Crib | 7881: The inventory leaves it blank |
| `nid_height_ft` | The dam's NID height (the source's name: NID Height (Ft)) | ft | integer | 0 to 789; 382 distinct | 0 |
| `dam_length_ft` | The dam's length (the source's name: Dam Length (Ft)) | ft | number | 0.0 to 470610.0; 4271 distinct | 14087: The inventory leaves it blank |
| `year_completed` | The year the dam was completed (the source's name: Year Completed) | none | integer | 0 to 2026; 267 distinct | 19052: The inventory leaves it blank |
| `nid_storage_acre_ft` | The NID storage (the source's name: NID Storage (Acre-Ft)) | acre-ft | number | 0.0 to 277540000.0; more than 5000 distinct | 0 |
| `normal_storage_acre_ft` | The normal storage (the source's name: Normal Storage (Acre-Ft)) | acre-ft | number | -48.0 to 277540000.0; more than 5000 distinct | 6718: The inventory leaves it blank |
| `surface_area_acres` | The reservoir's surface area (the source's name: Surface Area (Acres)) | acre | number | 0.0 to 20255000.0; 4683 distinct | 20390: The inventory leaves it blank |
| `drainage_area_sq_mi` | The drainage area (the source's name: Drainage Area (Sq Miles)) | sq mi | number | 0.0 to 8300000.0; 4902 distinct | 30860: The inventory leaves it blank |
| `max_discharge_cfs` | The maximum discharge (the source's name: Max Discharge (Cubic Ft/Second)) | cubic ft/second | number | 0.0 to 3707516.0; more than 5000 distinct | 46769: The inventory leaves it blank |
| `locks_n` | The number of locks (the source's name: Number of Locks) | count | integer | 0, 1, 2, 3, 4, 5 | 57464: The inventory leaves it blank |
| `source_agency` | The agency that supplied the record (a state or a federal agency) (the source's name: Source Agency) | none | text | for example Alabama, Alaska, Arizona; 69 distinct | 3: The inventory leaves it blank |
| `record_updated` | The date the record's data were last updated, as published (MM/DD/YYYY) (the source's name: Data Last Updated) | none | text | for example 01/07/2026, 01/08/2025, 01/08/2026; 261 distinct | 0 |
| `coordinate_given` | Where the inventory gives only one coordinate of the two, the one given (lat and lon are then left empty) | none | text | lat ; lon -79.87083333, lat ; lon -81.98228 | 92786: Both coordinates or neither given |

### `usdm_drought_state_weekly`

One contiguous state's percent of area in one U.S. Drought Monitor category (cumulative) in one weekly map.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 177696.

- **Time:** ts_utc is the map date (a Tuesday) at 00:00:00Z; freq P1W; x_valid_start and x_valid_end give the week the map is valid for.
- **Revisions:** Rewritten whole as one snapshot by each run from the Monitor's data services; vintage is not filled.
- **Source:** usdm:state_statistics the U.S. Drought Monitor's data services (National Drought Mitigation Center, USDA, NOAA) (https://droughtmonitor.unl.edu/DmData/DataDownload/WebServiceInfo.aspx)
- **Method note:** [`docs/methods/usdm_drought_state_weekly.md`](../methods/usdm_drought_state_weekly.md)
- **Cite as:** U.S. Drought Monitor (National Drought Mitigation Center, USDA, NOAA). U.S. Drought Monitor, state statistics: percent of area by drought category, weekly. Via the Energy Research Warehouse (ERW), table `usdm_drought_state_weekly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: usdm:<state postal code> | none | text | for example usdm:AL, usdm:AR, usdm:AZ; 48 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2014-12-30T00:00:00Z to 2026-10-20T00:00:00Z; 617 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 100.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> | none | text | for example US-AL, US-AR, US-AZ; 48 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 177696 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The state's postal code, not a pricing node | none | text | for example AL, AR, AZ; 48 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | usdm:state_statistics | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://usdmdataservices.unl.edu/api/StateStatistics/GetDroughtSeverityStatisticsByAreaPercent?aoi=01%2C04%2C05%2C06%2C08%2C09%2C10%2C12%2C13%2C16%2C17%2C18%2C19%2C20%2C21%2C22%2C23%2C24%2C25%2C26%2C27%2C28%2C29%2C30%2C31%2C32%2C33%2C34%2C35%2C36%2C37%2C38%2C39%2C40%2C41%2C42%2C44%2C45%2C46%2C47%2C48%2C49%2C50%2C51%2C53%2C54%2C55%2C56&startdate=1/1/2015&enddate=12/31/2018&statisticsType=1, https://usdmdataservices.unl.edu/api/StateStatistics/GetDroughtSeverityStatisticsByAreaPercent?aoi=01%2C04%2C05%2C06%2C08%2C09%2C10%2C12%2C13%2C16%2C17%2C18%2C19%2C20%2C21%2C22%2C23%2C24%2C25%2C26%2C27%2C28%2C29%2C30%2C31%2C32%2C33%2C34%2C35%2C36%2C37%2C38%2C39%2C40%2C41%2C42%2C44%2C45%2C46%2C47%2C48%2C49%2C50%2C51%2C53%2C54%2C55%2C56&startdate=1/1/2019&enddate=12/31/2022&statisticsType=1, https://usdmdataservices.unl.edu/api/StateStatistics/GetDroughtSeverityStatisticsByAreaPercent?aoi=01%2C04%2C05%2C06%2C08%2C09%2C10%2C12%2C13%2C16%2C17%2C18%2C19%2C20%2C21%2C22%2C23%2C24%2C25%2C26%2C27%2C28%2C29%2C30%2C31%2C32%2C33%2C34%2C35%2C36%2C37%2C38%2C39%2C40%2C41%2C42%2C44%2C45%2C46%2C47%2C48%2C49%2C50%2C51%2C53%2C54%2C55%2C56&startdate=1/1/2023&enddate=10/23/2026&statisticsType=1 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T20:06:26Z, 2026-10-23T20:06:43Z, 2026-10-23T20:06:50Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 177696 |
| `x_valid_start` | The first day the map is valid for (the source's name: ValidStart) | none | date | 2014-12-30 to 2026-10-20; 617 distinct | 0 |
| `x_valid_end` | The last day the map is valid for (the source's name: ValidEnd) | none | date | 2015-01-05 to 2026-10-26; 617 distinct | 0 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `d0` | Percent of the state's area abnormally dry or worse | pct | 29616 | 2014-12-30T00:00:00Z | 2026-10-20T00:00:00Z |
| `d1` | Percent of the state's area in moderate drought or worse | pct | 29616 | 2014-12-30T00:00:00Z | 2026-10-20T00:00:00Z |
| `d2` | Percent of the state's area in severe drought or worse | pct | 29616 | 2014-12-30T00:00:00Z | 2026-10-20T00:00:00Z |
| `d3` | Percent of the state's area in extreme drought or worse | pct | 29616 | 2014-12-30T00:00:00Z | 2026-10-20T00:00:00Z |
| `d4` | Percent of the state's area in exceptional drought | pct | 29616 | 2014-12-30T00:00:00Z | 2026-10-20T00:00:00Z |
| `none` | Percent of the state's area in none of the categories | pct | 29616 | 2014-12-30T00:00:00Z | 2026-10-20T00:00:00Z |

### `uspvdb_solar_facilities`

One large-scale solar photovoltaic facility in the USGS U.S. Large-Scale Solar Photovoltaic Database.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 6611.

- **Time:** No time column; project_year is the year of operation; image_date the date of the image it was drawn from.
- **Revisions:** Rewritten whole as one snapshot by each run from the database's API; vintage is not filled.
- **Source:** usgs:uspvdb U.S. Geological Survey and Lawrence Berkeley National Laboratory, U.S. Large-Scale Solar Photovoltaic Database (API v1) (https://energy.usgs.gov/uspvdb/)
- **Method note:** [`docs/methods/uspvdb_solar_facilities.md`](../methods/uspvdb_solar_facilities.md)
- **Cite as:** U.S. Geological Survey (USGS), with LBNL. U.S. Large-Scale Solar Photovoltaic Database (API v1). Via the Energy Research Warehouse (ERW), table `uspvdb_solar_facilities`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: uspvdb:<case_id> | none | text | for example uspvdb:400004, uspvdb:400005, uspvdb:400008; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: plant on every row | none | text | plant | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The facility's name (p_name) | none | text | for example (3K) 59 Hetcheltown Rd, 0 Hammond St (CSG), 1 Commercial; more than 5000 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> | none | text | for example US-AK, US-AL, US-AR; 50 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: The outline's centroid (ylat) | degree | number | 19.6558 to 66.8385; more than 5000 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: The outline's centroid (xlong) | degree | number | -162.5531 to -67.4623; more than 5000 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: The facility's AC capacity (p_cap_ac) | MW | number | 0.2 to 690.0; 475 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: the database lists facilities in operation | none | empty | no cell holds a value | 6611 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 6611 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 6611 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | usgs:uspvdb | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://energy.usgs.gov/api/uspvdb/v1/projects | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T05:19:06Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 6611 |
| `case_id` | The database's id of the facility (the source's name: case_id) | none | integer | 400004 to 407577; more than 5000 distinct | 0 |
| `eia_plant_id` | EIA's plant id (the source's name: eia_id) | none | integer | 645 to 69098; more than 5000 distinct | 0 |
| `project_name` | The facility's name (the source's name: p_name) | none | text | for example (3K) 59 Hetcheltown Rd, 0 Hammond St (CSG), 1 Commercial; more than 5000 distinct | 0 |
| `project_year` | The year of operation (the newest year not complete) (the source's name: p_year) | none | integer | 1985, 1990, 2002, 2003, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 | 0 |
| `state` | The state, postal code (the source's name: p_state) | none | text | for example AK, AL, AR; 50 distinct | 0 |
| `county` | The county (the source's name: p_county) | none | text | for example Accomack, Ada, Adair; 880 distinct | 0 |
| `power_region` | The power region (PJM, MISO, ISNE, CISO, ERCO and others) (the source's name: p_pwr_reg) | none | text | for example AECI, AK, AVA; 53 distinct | 17: USGS leaves it blank |
| `capacity_ac_mw` | The facility's AC capacity (the source's name: p_cap_ac) | MW | number | 0.2 to 690.0; 475 distinct | 0 |
| `capacity_dc_mw` | The facility's DC capacity (the source's name: p_cap_dc) | MW | number | 1.0 to 788.2; 857 distinct | 0 |
| `area_m2` | The outline's area (the source's name: p_area) | m2 | integer | 869 to 18802490; more than 5000 distinct | 0 |
| `technology_primary` | The primary technology (PV on every row) (the source's name: p_tech_pri) | none | text | PV | 0 |
| `technology_secondary` | The secondary technology (c-si crystalline silicon, thin-film, cpv concentrating PV, other) (the source's name: p_tech_sec) | none | text | c-si, c-si,cpv, c-si,cpv,thin-film, c-si,thin-film, cpv, other, thin-film | 236: USGS leaves it blank |
| `axis` | The tracking: single-axis, fixed-tilt, dual-axis, or more than one (the source's name: p_axis) | none | text | dual-axis, dual-axis,fixed-tilt,single-axis, fixed-tilt, fixed-tilt,single-axis, single-axis | 284: USGS leaves it blank |
| `azimuth_deg` | The panels' azimuth (the source's name: p_azimuth) | degree | integer | 0 to 360; 185 distinct | 222: USGS leaves it blank |
| `tilt_deg` | The panels' tilt (the source's name: p_tilt) | degree | integer | 0 to 90; 54 distinct | 1323: USGS leaves it blank |
| `battery` | batteries where the facility has them (the source's name: p_battery) | none | text | batteries | 6236: The facility has no battery listed |
| `agrivoltaic` | non-agrivoltaic, or es, grazing, crop and their combinations, as USGS gives them (the source's name: p_agrivolt) | none | text | crop, crop,es, crop,grazing, crop,grazing,es, es, es,grazing, grazing, non-agrivoltaic | 0 |
| `site_type` | USGS's general category of the facility's site (p_type): greenfield (land that may have been wildland, urbanized, cultivated or reclaimed); RCRA (a Resource Conservation and Recovery Act site, a facility that treats, stores or disposes of hazardous wastes and needs cleanup under RCRA's corrective action program); superfund; AML (abandoned hardrock mines and mineral processing sites listed in the Superfund Enterprise Management System); landfill (designated a landfill in EPA's RE-Powering Matrix); landfill named (the facility's name holds the word landfill, EPA does not list it as one); PCSC (a brownfield site that EPA's RE-Powering Matrix gives no specific designation; USGS does not expand the letters) (the source's name: p_type) | none | text | AML, PCSC, RCRA, greenfield, landfill, landfill named, superfund | 0 |
| `system_type` | The system type: ground, rooftop, canopy, floating, or more than one (the source's name: p_sys_type) | none | text | canopy, canopy,ground, canopy,ground,rooftop, canopy,rooftop, floating, ground, ground,rooftop, rooftop | 0 |
| `image_date` | The image's date, YYYY-MM-DD (the source's name: p_img_date) | none | date | 2009-04-17 to 2026-02-08; 1573 distinct | 1: USGS's date is no calendar date (one row: 20240231) |
| `digitizing_confidence` | The digitizing confidence (1 to 4) (the source's name: p_dig_conf) | none | integer | 1, 2, 3, 4 | 0 |
| `zscore` | USGS's z-score of the facility's DC capacity over its area (p_cap_dc / p_area): how many standard deviations the record lies from the mean of all records; a high or low value may mean an error in the capacity or the area (the source's name: p_zscore) | none | number | -1.04 to 58.18; 339 distinct | 0 |
| `multi_polygon` | single or multi: whether the facility's outline is one polygon or several, as USGS gives it (the source's name: multi_poly) | none | text | multi, single | 0 |
| `comments` | USGS's comments (community solar) (the source's name: p_comm) | none | text | community solar | 5510: USGS gives no comment |
| `image_date_usgs` | The image date as USGS gives it (YYYYMMDD) (the source's name: p_img_date) | none | integer | 20090417 to 20260208; 1574 distinct | 0 |

### `uswtdb_wind_turbines`

One utility-scale land-based or offshore wind turbine in the USGS U.S. Wind Turbine Database.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 77839.

- **Time:** No time column; project_year is the project's year, not the turbine's; image_date the date of the image it was located on.
- **Revisions:** Rewritten whole as one snapshot by each run from the database's API; vintage is not filled.
- **Source:** usgs:uswtdb U.S. Geological Survey, Lawrence Berkeley National Laboratory and American Clean Power Association, U.S. Wind Turbine Database (API v1) (https://energywind.usgs.gov/uswtdb/)
- **Method note:** [`docs/methods/uswtdb_wind_turbines.md`](../methods/uswtdb_wind_turbines.md)
- **Cite as:** U.S. Geological Survey (USGS), with LBNL and ACP. U.S. Wind Turbine Database (API v1). Via the Energy Research Warehouse (ERW), table `uswtdb_wind_turbines`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: uswtdb:<case_id> | none | text | for example uswtdb:3000001, uswtdb:3000003, uswtdb:3000008; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: generator on every row (a turbine) | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The project's name (p_name) and turbine <case_id> | none | text | for example 25 Mile Creek turbine 3118873, 25 Mile Creek turbine 3119095, 25 Mile Creek turbine 3119490; more than 5000 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> | none | text | for example US-AK, US-AR, US-AZ; 48 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: The turbine's position (ylat) | degree | number | 13.38938 to 70.20971; more than 5000 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: The turbine's position (xlong) | degree | number | -171.71307 to 144.72266; more than 5000 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: The turbine's rated capacity | MW | number | 0.05 to 14.0; 109 distinct | 5056 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: the database lists installed turbines | none | empty | no cell holds a value | 77839 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 77839 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 77839 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | usgs:uswtdb | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://energy.usgs.gov/api/uswtdb/v1/turbines | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T18:33:12Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 77839 |
| `case_id` | The database's id of the turbine (the source's name: case_id) | none | integer | 3000001 to 3154451; more than 5000 distinct | 0 |
| `eia_plant_id` | EIA's plant id (the source's name: eia_id) | none | integer | 90 to 69327; 1348 distinct | 5051: No EIA plant id given |
| `project_name` | The project's name (the source's name: p_name) | none | text | for example 25 Mile Creek, 251 Wind, 30 MW Iowa DG Portfolio; 1805 distinct | 0 |
| `project_year` | The project's year (not the turbine's) (the source's name: p_year) | none | integer | 1982 to 2026; 42 distinct | 842: USGS leaves it blank |
| `project_turbines` | The number of turbines in the project (the source's name: p_tnum) | count | integer | 1 to 664; 190 distinct | 0 |
| `project_capacity_mw` | The project's capacity (the source's name: p_cap) | MW | number | 0.05 to 1055.6; 845 distinct | 3857: USGS leaves it blank |
| `state` | The turbine's state, postal code (the source's name: t_state) | none | text | for example AK, AR, AZ; 48 distinct | 0 |
| `county` | The turbine's county (the source's name: t_county) | none | text | for example Adair County, Adams County, Addison County; 587 distinct | 0 |
| `fips_county` | The county's five-digit FIPS code (the source's name: t_fips) | none | text | for example 02013, 02016, 02020; 722 distinct | 0 |
| `manufacturer` | The turbine's manufacturer (the source's name: t_manu) | none | text | for example AAER, AOC, AWE; 62 distinct | 4866: USGS gives no maker |
| `model` | The turbine's model (the source's name: t_model) | none | text | for example 1.5-70.5, 1.5-77, 1.5_74; 329 distinct | 4909: USGS gives no model |
| `turbine_capacity_kw` | The turbine's rated capacity (the source's name: t_cap) | kW | integer | 50 to 14000; 109 distinct | 5056: USGS gives no rated capacity |
| `hub_height_m` | The turbine's hub height (the source's name: t_hh) | m | number | 19.0 to 140.0; 104 distinct | 5450: USGS leaves it blank |
| `rotor_diameter_m` | The rotor diameter (the source's name: t_rd) | m | number | 13.4 to 222.0; 108 distinct | 5140: USGS leaves it blank |
| `rotor_swept_area_m2` | The rotor's swept area (the source's name: t_rsa) | m2 | number | 141.03 to 38707.56; 108 distinct | 5140: USGS leaves it blank |
| `total_height_m` | The turbine's total height (the source's name: t_ttlh) | m | number | 30.5 to 247.5; 226 distinct | 5500: USGS leaves it blank |
| `confidence_attributes` | USGS's confidence in the turbine's attributes: 1 none (no attribute data beyond total height and year), 2 partial (incomplete information or substantial conflict between sources), 3 full (complete information, consistent across several sources) (the source's name: t_conf_atr) | none | integer | 1, 2, 3 | 0 |
| `confidence_location` | USGS's confidence in the turbine's location: 1 no turbine shown in the image (or clouds, or imagery older than the turbine), 2 partial (a developed pad with a concrete base or turbine parts on the ground), 3 full (an installed turbine shown) (the source's name: t_conf_loc) | none | integer | 1, 2, 3 | 0 |
| `image_date` | The date of the image the turbine was located on (rewritten from M/D/YYYY to YYYY-MM-DD) (the source's name: t_img_date) | none | date | 2010-01-01 to 2026-08-21; 1597 distinct | 6467: USGS leaves it blank |
| `image_source` | The image's source (Vantor, Planet, NAIP, Bing Maps Aerial, Google Earth) (the source's name: t_img_src) | none | text | Bing Maps Aerial, Google Earth, NAIP, Planet, Vantor | 0 |
| `retrofit` | 1 where the turbine was retrofitted, else 0 (the source's name: t_retrofit) | none | integer | 0, 1 | 0 |
| `retrofit_year` | The year of the retrofit (the source's name: t_retro_yr) | none | integer | 2015, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 | 69130: Not retrofitted |
| `offshore` | 1 for an offshore turbine, else 0 (the source's name: t_offshore) | none | integer | 0, 1 | 0 |
| `faa_ors` | The turbine's identifier in the Federal Aviation Administration's digital obstacle files (for cross-reference) (the source's name: faa_ors) | none | text | for example 02-000669, 02-020007, 02-020012; more than 5000 distinct | 3349: USGS leaves it blank |
| `faa_asn` | The turbine's identifier in the FAA's obstruction evaluation and airport airspace analysis dataset (for cross-reference) (the source's name: faa_asn) | none | text | for example 1987-AGL-900-OE, 1997-ACE-1545-OE, 1997-ACE-1546-OE; more than 5000 distinct | 3556: USGS leaves it blank |
| `usgs_project_id` | USGS's project id, as published (the source's name: usgs_pr_id) | none | integer | 1 to 49135; more than 5000 distinct | 41912: USGS leaves it blank |

### `wapa_energy_sales_annual`

One WAPA project's (or WAPA's total) energy sold or power rate in one federal fiscal year, from WAPA's Rates and Sales Data.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 307.

- **Time:** ts_utc is the fiscal year's first day (1 October of the year before) at 00:00:00Z; freq P1Y; FY 2008 to FY 2025.
- **Revisions:** Rewritten whole as one snapshot by each run from WAPA's workbook; vintage is the workbook's Last-Modified.
- **Source:** wapa:rates_and_sales_data Western Area Power Administration, Rates and Sales Data FY 2008-2025 (workbook, March 2026)
- **Method note:** [`docs/methods/wapa_energy_sales_annual.md`](../methods/wapa_energy_sales_annual.md)
- **Cite as:** Western Area Power Administration (WAPA). Rates and Sales Data FY 2008-2025: energy sold and power rate by project. Via the Energy Research Warehouse (ERW), table `wapa_energy_sales_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: wapa_proj:<project> or wapa_proj:wapa_total | none | text | wapa_proj:boulder_canyon_project, wapa_proj:central_arizona_project, wapa_proj:central_valley_project, wapa_proj:falcon_amistad_project, wapa_proj:loveland_area_projects, wapa_proj:olmsted, wapa_proj:parker_davis_project, wapa_proj:pick_sloan_missouri_basin_program_eastern_division, wapa_proj:provo_river_project, wapa_proj:salt_lake_city_area_integrated_projects, wapa_proj:wapa_total, wapa_proj:washoe_project | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2007-10-01T00:00:00Z, 2008-10-01T00:00:00Z, 2009-10-01T00:00:00Z, 2010-10-01T00:00:00Z, 2011-10-01T00:00:00Z, 2012-10-01T00:00:00Z, 2013-10-01T00:00:00Z, 2014-10-01T00:00:00Z, 2015-10-01T00:00:00Z, 2016-10-01T00:00:00Z, 2017-10-01T00:00:00Z, 2018-10-01T00:00:00Z, 2019-10-01T00:00:00Z, 2020-10-01T00:00:00Z, 2021-10-01T00:00:00Z, 2022-10-01T00:00:00Z, 2023-10-01T00:00:00Z, 2024-10-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 42428128.0; 271 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 307 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The row's label (the project), not a pricing node | none | text | Boulder Canyon Project, Central Arizona Project, Central Valley Project, Falcon-Amistad Project, Loveland Area Projects, Olmsted, Parker-Davis Project, Pick-Sloan Missouri Basin Program - Eastern Division, Provo River Project, Salt Lake City Area/Integrated Projects, WAPA Total, Washoe Project | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | wapa:rates_and_sales_data | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.wapa.gov/wp-content/uploads/2026/03/3-Rates-and-Sales-Data-FY-2008-2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T21:59:36Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's Last-Modified (UTC) | none | utc time | 2026-03-20T21:16:04Z | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `energy_sold` | Energy sold in the fiscal year | MWh | 199 | 2007-10-01T00:00:00Z | 2024-10-01T00:00:00Z |
| `power_rate` | Power rate (WAPA's cents/kWh times 10); see the header for the surcharges a rate excludes | USD/MWh | 108 | 2007-10-01T00:00:00Z | 2024-10-01T00:00:00Z |

### `weather_forecast_hourly`

One airport's forecast temperature or wind speed for one hour, from the National Weather Service's hourly forecast.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 18538.

- **Time:** ts_utc is the forecast hour's start (UTC); freq PT1H; about 7 days ahead.
- **Revisions:** Merged by (entity, variable, ts_utc): a newer run replaces the value for the same hour (the latest forecast); vintage is the forecast's updateTime.
- **Source:** nws:forecast_hourly National Weather Service API, https://api.weather.gov/points/<lat,lon> then its forecastHourly (units=si) (https://api.weather.gov/points/<lat,lon>)
- **Method note:** [`docs/methods/weather_forecast_hourly.md`](../methods/weather_forecast_hourly.md)
- **Cite as:** National Weather Service (NWS, NOAA). Hourly gridpoint forecast (api.weather.gov). Via the Energy Research Warehouse (ERW), table `weather_forecast_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: nws:<station>, one airport per ISO load center | none | text | nws:KBOS, nws:KDFW, nws:KIND, nws:KLAX, nws:KLGA, nws:KOKC, nws:KPHL | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-28T09:00:00Z to 2026-11-23T01:00:00Z; 1327 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 102.2; 69 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF, mph | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<the airport's state> | none | text | US-CA, US-IN, US-MA, US-NY, US-OK, US-PA, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 18538 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The ISO whose load center the airport stands for, not a pricing node | none | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nws:forecast_hourly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.weather.gov/gridpoints/BOX/73,101/forecast/hourly?units=si, https://api.weather.gov/gridpoints/FWD/81,109/forecast/hourly?units=si, https://api.weather.gov/gridpoints/IND/54,67/forecast/hourly?units=si, https://api.weather.gov/gridpoints/LOX/149,41/forecast/hourly?units=si, https://api.weather.gov/gridpoints/OKX/37,46/forecast/hourly?units=si, https://api.weather.gov/gridpoints/OUN/94,90/forecast/hourly?units=si, https://api.weather.gov/gridpoints/PHI/48,75/forecast/hourly?units=si | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-28T10:03:28Z to 2026-11-16T14:38:14Z; 249 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The forecast's updateTime (UTC) | none | utc time | 2026-09-28T06:26:20Z to 2026-11-16T14:15:32Z; 249 distinct | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `temperature_f` | Forecast temperature for the hour | degF | 9269 | 2026-09-28T09:00:00Z | 2026-11-23T01:00:00Z |
| `wind_speed_mph` | Forecast wind speed for the hour | mph | 9269 | 2026-09-28T09:00:00Z | 2026-11-23T01:00:00Z |

### `weather_forecast_issued_hourly`

One NWS hourly forecast value (temperature or wind) for one airport and one forecast hour, as one issue gave it; the variable names the lead in days (the hour's UTC date less the issue's).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-26: 2184.

- **Time:** ts_utc is the forecast hour's start (UTC, freq PT1H); vintage is the issue's updateTime.
- **Revisions:** Appended run to run and never replaced across leads: a later issue writes another variable (another lead); of two issues read on one UTC day for the same lead, the later is kept.
- **Source:** nws:forecast_hourly National Weather Service API, https://api.weather.gov/points/<lat,lon> then its forecastHourly (units=si) (https://api.weather.gov/points/<lat,lon>)
- **Cite as:** National Weather Service (NWS, NOAA). Hourly gridpoint forecast (api.weather.gov). Via the Energy Research Warehouse (ERW), table `weather_forecast_issued_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | nws:KBOS, nws:KDFW, nws:KIND, nws:KLAX, nws:KLGA, nws:KOKC, nws:KPHL | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-11-26T12:00:00Z to 2026-12-02T23:00:00Z; 156 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 82.4; 72 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF, mph | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA, US-IN, US-MA, US-NY, US-OK, US-PA, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 2184 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nws:forecast_hourly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.weather.gov/gridpoints/BOX/73,101/forecast/hourly?units=si, https://api.weather.gov/gridpoints/FWD/81,109/forecast/hourly?units=si, https://api.weather.gov/gridpoints/IND/54,67/forecast/hourly?units=si, https://api.weather.gov/gridpoints/LOX/149,41/forecast/hourly?units=si, https://api.weather.gov/gridpoints/OKX/37,46/forecast/hourly?units=si, https://api.weather.gov/gridpoints/OUN/94,90/forecast/hourly?units=si, https://api.weather.gov/gridpoints/PHI/48,75/forecast/hourly?units=si | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-26T12:04:36Z, 2026-11-26T12:04:37Z, 2026-11-26T12:04:39Z, 2026-11-26T12:04:41Z, 2026-11-26T12:04:43Z, 2026-11-26T12:04:45Z, 2026-11-26T12:04:47Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-11-26T06:26:58Z, 2026-11-26T09:07:45Z, 2026-11-26T09:14:54Z, 2026-11-26T09:37:47Z, 2026-11-26T11:11:43Z, 2026-11-26T11:21:09Z, 2026-11-26T11:45:22Z | 0 |

Variables (14):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `temperature_f_lead0d` |  | degF | 84 | 2026-11-26T12:00:00Z | 2026-11-26T23:00:00Z |
| `temperature_f_lead1d` |  | degF | 168 | 2026-11-27T00:00:00Z | 2026-11-27T23:00:00Z |
| `temperature_f_lead2d` |  | degF | 168 | 2026-11-28T00:00:00Z | 2026-11-28T23:00:00Z |
| `temperature_f_lead3d` |  | degF | 168 | 2026-11-29T00:00:00Z | 2026-11-29T23:00:00Z |
| `temperature_f_lead4d` |  | degF | 168 | 2026-11-30T00:00:00Z | 2026-11-30T23:00:00Z |
| `temperature_f_lead5d` |  | degF | 168 | 2026-12-01T00:00:00Z | 2026-12-01T23:00:00Z |
| `temperature_f_lead6d` |  | degF | 168 | 2026-12-02T00:00:00Z | 2026-12-02T23:00:00Z |
| `wind_speed_mph_lead0d` |  | mph | 84 | 2026-11-26T12:00:00Z | 2026-11-26T23:00:00Z |
| `wind_speed_mph_lead1d` |  | mph | 168 | 2026-11-27T00:00:00Z | 2026-11-27T23:00:00Z |
| `wind_speed_mph_lead2d` |  | mph | 168 | 2026-11-28T00:00:00Z | 2026-11-28T23:00:00Z |
| `wind_speed_mph_lead3d` |  | mph | 168 | 2026-11-29T00:00:00Z | 2026-11-29T23:00:00Z |
| `wind_speed_mph_lead4d` |  | mph | 168 | 2026-11-30T00:00:00Z | 2026-11-30T23:00:00Z |
| `wind_speed_mph_lead5d` |  | mph | 168 | 2026-12-01T00:00:00Z | 2026-12-01T23:00:00Z |
| `wind_speed_mph_lead6d` |  | mph | 168 | 2026-12-02T00:00:00Z | 2026-12-02T23:00:00Z |

### `weather_obs_hourly`

One airport's mean observed temperature or wind speed in one hour, from the National Weather Service API.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 18587.

- **Time:** ts_utc is the UTC hour's start; freq PT1H; an hour with no observation is absent.
- **Revisions:** Merged by (entity, variable, ts_utc): each run asks the last 30 days, replaces the hours it reads again and keeps the older ones; vintage is not filled.
- **Source:** nws:observations National Weather Service API (https://api.weather.gov/stations/<station>/observations)
- **Method note:** [`docs/methods/weather_obs_hourly.md`](../methods/weather_obs_hourly.md)
- **Cite as:** National Weather Service (NWS, NOAA). Station observations (api.weather.gov). Via the Energy Research Warehouse (ERW), table `weather_obs_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: nws:<station>, one airport per ISO load center | none | text | nws:KBOS, nws:KDFW, nws:KIND, nws:KLAX, nws:KLGA, nws:KOKC, nws:KPHL | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-21T09:00:00Z to 2026-11-16T13:00:00Z; 1338 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 100.4; 859 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF, mph | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA, US-IN, US-MA, US-NY, US-OK, US-PA, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 18587 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The ISO whose load center the airport stands for, not a pricing node | none | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nws:observations | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://api.weather.gov/stations/KBOS/observations?cursor=eyJzIjoiMjAyNi0wOS0yM1QwODo1NTowMCswMDowMCJ9, https://api.weather.gov/stations/KBOS/observations?cursor=eyJzIjoiMjAyNi0wOS0yMVQxNjoxNTowMCswMDowMCJ9, https://api.weather.gov/stations/KBOS/observations?cursor=eyJzIjoiMjAyNi0wOS0yMlQwNzozMDowMCswMDowMCJ9; 465 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-28T10:03:28Z to 2026-11-16T14:38:13Z; 362 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 18587 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `temperature_f` | Mean of the station's temperature observations in the hour | degF | 9322 | 2026-09-21T09:00:00Z | 2026-11-16T13:00:00Z |
| `wind_speed_mph` | Mean of the station's wind speed observations in the hour | mph | 9265 | 2026-09-21T09:00:00Z | 2026-11-16T13:00:00Z |

### `wfigs_wildfires`

One wildfire of 1,000 acres or more discovered from 2015, from NIFC's WFIGS Incident Locations.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 6222.

- **Time:** event_date is the discovery's UTC day; x_discovered_utc, x_contained_utc and x_out_utc are UTC times.
- **Revisions:** Rewritten whole as one snapshot by each run from the WFIGS feature service; vintage is the answer's Last-Modified.
- **Source:** nifc:wfigs_incident_locations NIFC, WFIGS Incident Locations (https://data-nifc.opendata.arcgis.com/)
- **Method note:** [`docs/methods/wfigs_wildfires.md`](../methods/wfigs_wildfires.md)
- **Cite as:** National Interagency Fire Center (NIFC). Wildland Fire Interagency Geospatial Services (WFIGS): Incident Locations. Via the Energy Research Warehouse (ERW), table `wfigs_wildfires`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: wfigs:<IRWIN id, lower case, braces dropped> | none | text | for example wfigs:000df40c-307f-4973-9171-bb269168b9f3, wfigs:0022a54b-5d87-4818-9bd2-78848568d249, wfigs:00295066-e99f-4f61-8fdc-dc06a97f7b52; more than 5000 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2015-01-18 to 2026-10-21; 2135 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: wildfire on every row | none | text | wildfire | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | empty | no cell holds a value | 6222 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 6222 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 6222 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 6222 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 6222 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: out or contained where those times are given, else empty | none | text | contained, out | 1239 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nifc:wfigs_incident_locations | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Incident_Locations/FeatureServer/0 | 0 |
| `x_name` | The incident's name, as published (the source's name: IncidentName) | none | text | for example  Black Mountain,  Bridger Foothills,  CASTLE; more than 5000 distinct | 0 |
| `x_state` | The state of the point of origin (US-<state>) (the source's name: POOState) | none | text | for example US-AK, US-AL, US-AR; 42 distinct | 0 |
| `x_county` | The county of the point of origin (the source's name: POOCounty) | none | text | for example Ada, Adair, Adams; 730 distinct | 0 |
| `x_latitude` | The initial latitude of the point of origin, as published (the source's name: InitialLatitude) | degree | number | 0.0 to 81.2877; 4996 distinct | 1136: WFIGS gives none |
| `x_longitude` | The initial longitude of the point of origin, as published (the source's name: InitialLongitude) | degree | number | -231.667 to 102.53; 4739 distinct | 1136: WFIGS gives none |
| `x_final_acres` | The fire's final acres, as published (the source's name: FinalAcres) | acre | number | 1000.0 to 318156.0; 446 distinct | 5729: WFIGS gives no final acres |
| `x_incident_size_acres` | The incident size, as published (the source's name: IncidentSize) | acre | number | 918.0 to 1054150.0; 4492 distinct | 24: WFIGS gives no incident size |
| `x_cause_general` | The general fire cause (Lightning, Equipment, Arson and others) (the source's name: FireCauseGeneral) | none | text | Arson, Camping, Cause and Origin Not Identified, Coal Seam, Debris and open burning, Debris/Open Burning, Equipment, Equipment and vehicle use, Firearms/Weapons, Incendiary, Investigated but Undetermined, Lightning, Misc/Other, Natural, Other Human Cause, Other Natural Cause, Other causes, Power generation/transmission/distribution, Railroad, Railroad operations and maintenance, Recreation and ceremony, Smoking, Undetermined, Undetermined (remarks required), Utilities | 5071: WFIGS gives no general cause |
| `x_cause` | The fire cause: Human, Natural, Undetermined or Unknown (the source's name: FireCause) | none | text | Human, Natural, Undetermined, Unknown | 147: WFIGS gives no cause |
| `x_discovered_utc` | The discovery time, UTC (the source's name: FireDiscoveryDateTime) | none | utc time | 2015-01-18T19:03:00Z to 2026-10-21T19:40:00Z; more than 5000 distinct | 0 |
| `x_contained_utc` | The containment time, UTC (the source's name: ContainmentDateTime) | none | utc time | 2015-01-19T18:00:00Z to 2026-10-22T19:58:00Z; 4133 distinct | 1640: WFIGS gives no containment time |
| `x_out_utc` | The fire-out time, UTC (the source's name: FireOutDateTime) | none | utc time | 2015-01-23T02:00:00Z to 2026-10-23T22:17:00Z; 3808 distinct | 1709: WFIGS gives no fire-out time |
| `x_unique_fire_id` | The unique fire identifier, as published (the source's name: UniqueFireIdentifier) | none | text | for example 2015-AKDAS-512313, 2015-AKDAS-512321, 2015-AKDAS-512396; more than 5000 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T23:10:00Z, 2026-10-23T23:10:03Z, 2026-10-23T23:10:05Z, 2026-10-23T23:10:08Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The answer's Last-Modified (UTC) | none | utc time | 2026-10-23T23:06:52Z | 0 |

