# Codebook: epa

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 8 public tables (2 entities, 6 series; tiers: 8 source); 0 documented in full.

- [`epa_ghg_inventory_annual`](#epa_ghg_inventory_annual): EPA, Inventory of U.S. Greenhouse Gas Emissions and Sinks: 1990-2022 (April 2024), Chapter 2 Tables 2-10, 2-11 and 2-12: emissions by economic sector and source, the electric power industry's by gas and fuel, each sector's by gas with electricity distributed (session 2136)
- [`epa_ghgrp_facility_emissions`](#epa_ghgrp_facility_emissions): U.S. EPA, Greenhouse Gas Reporting Program, data summary 2023: every reporting facility's total reported emissions by year, 2015 to 2023, in the six emitting segments of the summary (session 2072)
- [`epa_ghgrp_power_co2`](#epa_ghgrp_power_co2): EPA Greenhouse Gas Reporting Program, power plants' (subpart D) reported CO2, 2010 to 2023 (session 492)
- [`epa_lmop_landfill_projects`](#epa_lmop_landfill_projects): U.S. EPA, Landfill Methane Outreach Program (LMOP) Database, composite data file: every landfill the program tracks and its landfill gas energy projects (session 2127)
- [`epa_needs_units`](#epa_needs_units): EPA, National Electric Energy Data System (NEEDS) for the 2025 reference case, 38,030 units (active 22,688, retired_by_2028 1,094, hardwired_capacity 2,755, dropped_capacity 11,493; MW active 1,155,380, dropped_capacity 582,669, hardwired_capacity 117,400, retired_by_2028 65,351) (session 2183)
- [`epa_rfs_fuel_annual`](#epa_rfs_fuel_annual): U.S. EPA, Renewable Fuel Standard, RIN generation and renewable fuel volume production by fuel type, a RIN year by D code and fuel category, 2010 to 2026 (session 2030)
- [`epa_rfs_rins_monthly`](#epa_rfs_rins_monthly): U.S. EPA, Renewable Fuel Standard, RIN generation and renewable fuel volume production by month, by D code, 2010-07 to 2026-09 (session 2030)
- [`epa_tri_energy_releases_annual`](#epa_tri_energy_releases_annual): U.S. EPA, Toxics Release Inventory, basic data files, reporting years 2015 to 2023: the energy industries' releases by facility, chemical and year (session 2121)

### `epa_ghg_inventory_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 5016.

- **Source:** epa:ghg_inventory_1990_2022 EPA, Inventory of U.S. Greenhouse Gas Emissions and Sinks: 1990-2022 (https://www.epa.gov/ghgemissions/inventory-us-greenhouse-gas-emissions-and-sinks-1990-2022)
- **Method note:** [`docs/methods/epa_ghg_inventory_annual.md`](../methods/epa_ghg_inventory_annual.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). Inventory of U.S. Greenhouse Gas Emissions and Sinks: 1990-2022. Via the Energy Research Warehouse (ERW), table `epa_ghg_inventory_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | epa_ghgi:agriculture, epa_ghgi:commercial, epa_ghgi:electric_power_industry, epa_ghgi:industry, epa_ghgi:residential, epa_ghgi:transportation, epa_ghgi:u_s_territories, epa_ghgi:us | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2022-01-01T00:00:00Z; 33 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | -1011200000 to 7529900000; 1855 distinct | 0 |
| `unit` | The unit of the row's value | none | text | tCO2e | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 5016 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 5016 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:ghg_inventory_1990_2022 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epa.gov/system/files/other-files/2024-04/trends-in-greenhouse-gas-emissions-and-removals.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T23:21:15Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2024-08-26T14:52:48Z | 0 |
| `x_table` | not yet written |  | text | 2-10, 2-11, 2-12 | 0 |
| `x_sector` | not yet written |  | text | Agriculture, Commercial, Electric Power Industry, Industry, Residential, Transportation, U.S. Territories | 99 |
| `x_group` | not yet written |  | text | CF4, CH4, CO2, Direct Emissions, Electricity-Related, N2O, SF6 | 2805 |
| `x_line` | not yet written |  | text | for example Abandoned Oil and Gas Wells, Abandoned Underground Coal Mines, Adipic Acid Production; 75 distinct | 0 |

Variables (85):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `direct:abandoned_oil_and_gas_wells` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:abandoned_underground_coal_mines` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:adipic_acid_production` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:aluminum_production` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:ammonia_production` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:anaerobic_digestion_at_biogas_facilities` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:caprolactam_glyoxal_and_glyoxylic_acid_production` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:carbide_production_and_consumption` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:carbon_dioxide_consumption` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:cement_production` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:co2_from_fossil_fuel_combustion` |  | tCO2e | 231 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:coal_mining` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:composting` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:electrical_equipment` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:electronics_industry` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:enteric_fermentation` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:ferroalloy_production` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:field_burning_of_agricultural_residues` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:fluorochemical_production` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:glass_production` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:incineration_of_waste` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:iron_and_steel_production` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:landfills_industrial` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:landfills_municipal` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:lead_production` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:lime_production` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:liming` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:magnesium_production_and_processing` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:manure_management` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:mobile_combustion` |  | tCO2e | 99 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:n2o_from_agricultural_soil_management` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:n2o_from_product_uses` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:natural_gas_systems` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:nitric_acid_production` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:non_energy_use_of_fuels` |  | tCO2e | 99 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:other_process_uses_of_carbonates` |  | tCO2e | 66 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:petrochemical_production` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:petroleum_systems` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:phosphoric_acid_production` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:rice_cultivation` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:sf6_and_pfcs_from_other_product_use` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:soda_ash_production` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:stationary_combustion` |  | tCO2e | 198 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:substitution_of_ozone_depleting_substances` |  | tCO2e | 132 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:titanium_dioxide_production` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:total` |  | tCO2e | 231 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:urea_consumption_for_non_agricultural_purposes` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:urea_fertilization` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:wastewater_treatment` |  | tCO2e | 66 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:zinc_production` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:direct` |  | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:direct:ch4` |  | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:direct:co2` |  | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:direct:hfcs` |  | tCO2e | 66 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:direct:hfcs_pfcs_sf6_and_nf3` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:direct:n2o` |  | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:direct:sf6` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:electricity_related` |  | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:electricity_related:ch4` |  | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:electricity_related:co2` |  | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:electricity_related:n2o` |  | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:electricity_related:sf6` |  | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:total` |  | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `lulucf_sector_net_total` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `net_emissions_sources_and_sinks` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:cf4` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:cf4:electrical_equipment` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:ch4` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:ch4:incineration_of_waste` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:ch4:stationary_sourcesa` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:co2` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:co2:coal` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:co2:fossil_fuel_combustion` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:co2:geothermal` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:co2:incineration_of_waste` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:co2:natural_gas` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:co2:other_process_uses_of_carbonates` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:co2:petroleum` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:n2o` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:n2o:incineration_of_waste` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:n2o:stationary_sourcesa` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:sf6` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:sf6:electrical_equipment` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:total` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `total_gross_emissions_sources` |  | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |

### `epa_ghgrp_facility_emissions`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 70338.

- **Source:** epa:ghgrp_facilities U.S. Environmental Protection Agency, Greenhouse Gas Reporting Program, data summary spreadsheets, ghgp_data_by_year_2023.xlsx (https://www.epa.gov/ghgreporting/data-sets)
- **Method note:** [`docs/methods/epa_ghgrp_facility_emissions.md`](../methods/epa_ghgrp_facility_emissions.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). Greenhouse Gas Reporting Program, data summary spreadsheets (ghgp_data_by_year_2023.xlsx). Via the Energy Research Warehouse (ERW), table `epa_ghgrp_facility_emissions`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example ghgrp:1000001, ghgrp:1000002, ghgrp:1000003; more than 5000 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1196.25 to 21775439.586; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | tCO2e | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 54 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 70338 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example (430) Civitas Resources - Permian Basin, (540) Civitas Resources - Denver Basin, (540) Civitas Resources - GB - Denver Basin; more than 5000 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:ghgrp_facilities | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epa.gov/system/files/other-files/2024-10/2023_data_summary_spreadsheets.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T17:42:37Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2024-10-15T14:42:16Z | 0 |
| `x_segment` | not yet written |  | text | Direct Point Emitters, Gathering & Boosting, LDC - Direct Emissions, Onshore Oil & Gas Prod., SF6 from Elec. Equip., Transmission Pipelines | 0 |
| `x_frs_id` | not yet written |  | integer | 110000307864 to 110071704324; more than 5000 distinct | 6526 |
| `x_naics` | not yet written |  | integer | 111419 to 928110; 279 distinct | 18 |
| `x_subparts` | not yet written |  | text | for example AA,C, AA,C,II, AA,C,II,TT; 165 distinct | 0 |
| `x_sectors` | not yet written |  | text | for example Chemicals, Chemicals,Coal-based Liquid Fuel Supply,Suppliers of CO2, Chemicals,Industrial Gas Suppliers; 71 distinct | 10805 |
| `x_basin` | not yet written |  | text | for example 140 - Florida Platform, 160 - Appalachian Basin, 160A - Appalachian Basin (Eastern Overthrust Area); 44 distinct | 63123 |
| `x_county` | not yet written |  | text | for example ACADIA, ACADIA PARISH, ACCOMACK COUNTY; 2106 distinct | 6800 |
| `x_emission_state` | not yet written |  | text | for example AL, AR, AZ; 49 distinct | 67555 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `emissions_direct` |  | tCO2e | 59533 | 2015-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `emissions_gathering_boosting` |  | tCO2e | 2786 | 2016-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `emissions_ldc` |  | tCO2e | 1499 | 2015-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `emissions_onshore_production` |  | tCO2e | 4429 | 2015-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `emissions_sf6_equipment` |  | tCO2e | 806 | 2015-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `emissions_transmission_pipelines` |  | tCO2e | 1285 | 2016-01-01T00:00:00Z | 2023-01-01T00:00:00Z |

### `epa_ghgrp_power_co2`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 17035.

- **Source:** epa:ghgrp U.S. Environmental Protection Agency, Greenhouse Gas Reporting Program, data summary spreadsheets (2023) (https://www.epa.gov/ghgreporting/data-sets)
- **Method note:** [`docs/methods/epa_ghgrp_power_co2.md`](../methods/epa_ghgrp_power_co2.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). Greenhouse Gas Reporting Program, data summary spreadsheets. Via the Energy Research Warehouse (ERW), table `epa_ghgrp_power_co2`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example ghgrp:1000001, ghgrp:1000049, ghgrp:1000050; 1443 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 22800874.9; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | tCO2 | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AL, US-AR, US-AZ; 49 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 17035 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example 23rd and 3rd, 48th Street Peaking Station, A B Brown Generating Station; 1509 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:ghgrp | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epa.gov/system/files/other-files/2024-10/2023_data_summary_spreadsheets.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T17:42:37Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 17035 |
| `x_frs_id` | not yet written |  | integer | 110000308444 to 110071542884; 1790 distinct | 72 |
| `x_oris` | not yet written |  | text | for example 10, 1001, 10030; 1418 distinct | 49 |
| `x_subparts` | not yet written |  | text | for example C,D, C,D,DD, C,D,DD,MM-REF,P,Y; 35 distinct | 0 |
| `x_naics` | not yet written |  | integer | 211112 to 926130; 33 distinct | 0 |
| `x_reporting_year` | not yet written |  | integer | 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023 | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `co2_biogenic` |  | tCO2 | 500 | 2010-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `co2_non_biogenic` |  | tCO2 | 16535 | 2010-01-01T00:00:00Z | 2023-01-01T00:00:00Z |

### `epa_lmop_landfill_projects`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 3399.

- **Source:** epa:lmop U.S. Environmental Protection Agency, Landfill Methane Outreach Program (LMOP) Database, composite data file (https://www.epa.gov/lmop/lmop-landfill-and-project-database)
- **Method note:** [`docs/methods/epa_lmop_landfill_projects.md`](../methods/epa_lmop_landfill_projects.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). Landfill Methane Outreach Program (LMOP) Database, composite data file. Via the Energy Research Warehouse (ERW), table `epa_lmop_landfill_projects`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example lmop:1000:1072-0, lmop:1001:1073-0, lmop:1002:1074-0; 3399 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 130 Environmental Park (130EP) Landfill, 27th Avenue Landfill, 31st Street Landfill: Project #1; 3361 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 53 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 13.429707 to 64.80476; 2302 distinct | 321 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -166.50657 to 144.750611; 2307 distinct | 321 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | 0.0 to 50.0; 197 distinct | 2615 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | operating, planned, retired, under_construction | 1885 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 3399 |
| `operator` | The operator or owner, as the publisher writes it | none | text | for example AC Landfill Energy, LLC (ACLE (JV of DCO Energy & South Jersey Industries)), APTIM, ARC Technologies Corporation; 186 distinct | 2671 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:lmop | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epa.gov/system/files/documents/2024-09/lmopcompositedata.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T23:11:19Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2024-09-20T16:32:56Z | 0 |
| `ghgrp_id` | not yet written |  | integer | 1000010 to 1014715; 1331 distinct | 1348 |
| `landfill_id` | not yet written |  | integer | 1 to 21409; 2641 distinct | 0 |
| `landfill_name` | not yet written |  | text | for example 130 Environmental Park (130EP) Landfill, 27th Avenue Landfill, 31st Street Landfill; 2594 distinct | 0 |
| `landfill_alias` | not yet written |  | text | for example "Mount Trashmore", (Sheala) SLF, 10800 County Road 21 NW; 885 distinct | 2064 |
| `state` | not yet written |  | text | for example AK, AL, AR; 53 distinct | 0 |
| `physical_address` | not yet written |  | text | for example #1 Industry Hills Parkway, .5 miles north of FM 2641, 1 Bob Foeller Drive; 2162 distinct | 462 |
| `city` | not yet written |  | text | for example Abbeville, Aberdeen, Abernathy; 1912 distinct | 173 |
| `county` | not yet written |  | text | for example Abbeville, Acadia, Accomack; 1083 distinct | 5 |
| `zip_code` | not yet written |  | text | for example 00605, 00610, 00612; 2124 distinct | 366 |
| `military_landfill` | not yet written |  | text | No, Yes | 0 |
| `on_tribal_land` | not yet written |  | text | No, Yes | 0 |
| `anaerobic_digester` | not yet written |  | text | No, Yes | 0 |
| `composting` | not yet written |  | text | No, Yes | 0 |
| `solar_project` | not yet written |  | text | No, Yes | 0 |
| `wind_project` | not yet written |  | text | No, Yes | 0 |
| `ownership_type` | not yet written |  | text | Private, Public, Public/Private, Unknown | 0 |
| `landfill_owner_organization_s` | not yet written |  | text | for example 3M Company, 600 Land, Inc., A. Capuano Brothers, Inc.; 1585 distinct | 149 |
| `landfill_operator_organization` | not yet written |  | text | for example 3M Company, A & M Quarries, Inc., A-9 Trucking Enterprise; 1152 distinct | 666 |
| `year_landfill_opened` | not yet written |  | integer | 1900 to 2025; 101 distinct | 376 |
| `landfill_closure_year` | not yet written |  | integer | 1960 to 2945; 216 distinct | 280 |
| `current_landfill_status` | not yet written |  | text | Closed, Open, Unknown | 0 |
| `design_landfill_area_acres` | not yet written |  | number | 1.0 to 1388.0; 436 distinct | 1688 |
| `current_landfill_area_acres` | not yet written |  | number | 1.0 to 1620.0; 765 distinct | 1301 |
| `design_landfill_depth_feet` | not yet written |  | number | 2.0 to 540.0; 104 distinct | 2511 |
| `current_landfill_depth_feet` | not yet written |  | number | 10.0 to 500.0; 129 distinct | 2601 |
| `landfill_design_capacity_tons` | not yet written |  | integer | 12560 to 994920296; 1316 distinct | 1410 |
| `waste_in_place_tons` | not yet written |  | number | 187.0 to 142250454.0; 1978 distinct | 469 |
| `waste_in_place_year` | not yet written |  | integer | 1965 to 2022; 46 distinct | 1233 |
| `annual_waste_acceptance_rate_tons_per_year` | not yet written |  | number | 0.0 to 3953108.0; 2049 distinct | 439 |
| `annual_waste_acceptance_year` | not yet written |  | integer | 1965 to 2022; 45 distinct | 1001 |
| `does_lf_recirculate_leachate` | not yet written |  | text | No, Unknown, Yes | 0 |
| `leachate_recirc_frequency_past_10_yrs` | not yet written |  | text | At least once per year, Not used, Occasionally but not every year, Several times per year | 1 |
| `permitted_as_rd_d_lf` | not yet written |  | text | No, Yes | 0 |
| `lfg_generated_mmscfd` | not yet written |  | number | 0.036 to 31.405; 919 distinct | 1649 |
| `lfg_collection_system_in_place` | not yet written |  | text | No, Shutdown, Unknown, Yes | 0 |
| `lfg_collected_mmscfd` | not yet written |  | number | 0.0 to 24.951; 943 distinct | 1502 |
| `lfg_collected_year` | not yet written |  | integer | 1998, 2003, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024 | 1627 |
| `percent_methane` | not yet written |  | number | 20.0 to 70.0; 308 distinct | 1494 |
| `flares_in_place` | not yet written |  | text | No, Shutdown, Unknown, Yes | 0 |
| `number_of_flares` | not yet written |  | integer | 1, 12, 2, 26, 3, 4, 5, 6, 7, 9 | 2149 |
| `lfg_flared_mmscfd` | not yet written |  | number | 0.0 to 15.136; 754 distinct | 1742 |
| `lfg_flared_year` | not yet written |  | integer | 2008, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024 | 1822 |
| `number_of_wells` | not yet written |  | integer | 1 to 2000; 301 distinct | 1593 |
| `gccs_capacity_cfm` | not yet written |  | integer | 80 to 45000; 315 distinct | 1652 |
| `passive_venting_flaring` | not yet written |  | text | No, Unknown, Yes | 0 |
| `projected_direct_reductions_mmtco2e_yr_mw` | not yet written |  | number | 0.002 to 1.3786; 387 distinct | 2955 |
| `projected_avoided_reductions_mmtco2e_yr_mw` | not yet written |  | number | 0.0002 to 0.1315; 174 distinct | 2955 |
| `project_id` | not yet written |  | text | for example 0-0, 100-0, 100-1; 3365 distinct | 0 |
| `lmop_status` | not yet written |  | text | Candidate, Construction, Future Potential, Low Potential, Operational, Planned, Shutdown, Unknown | 0 |
| `project_name` | not yet written |  | text | for example Combination Project, Combination Project #1, Combination Project #1 (MBC Cogen); 107 distinct | 1865 |
| `project_start_date` | not yet written |  | date | 1974-04-01 to 2027-12-31; 709 distinct | 1889 |
| `project_shutdown_date` | not yet written |  | date | 1975-02-01 to 2024-01-01; 272 distinct | 2683 |
| `project_type_category` | not yet written |  | text | Direct, Electricity, Renewable Natural Gas, Unknown | 0 |
| `lfg_energy_project_type` | not yet written |  | text | Boiler, Cogeneration, Combined Cycle, Condensate Evaporation, Direct Thermal, Electricity, Fuel Cell, Gas Turbine, Greenhouse, Hydrogen, Industrial, Leachate Evaporation, Linear Generator, Medium Btu, Microturbine, Organic Rankine Cycle, Other, Reciprocating Engine, Steam Turbine, Stirling Cycle Engine, Unknown, Vehicle Fuel | 0 |
| `rng_delivery_method` | not yet written |  | text | Local Use, Pipeline Injection, Unknown | 3132 |
| `lfg_use_details` | not yet written |  | text | for example (1) 1,600 kW Caterpillar 3520 reciprocating engine, (1) 1-MW GE-Jenbacher engine, (1) 1-MW GE-Jenbacher engine & (1) 1.4-MW GE-Jenbacher engine; electricity will power college and Energy Innovation Center (EIC); 1078 distinct | 2110 |
| `actual_mw_generation` | not yet written |  | number | 0.0 to 23.4; 398 distinct | 2451 |
| `lfg_flow_to_project_mmscfd` | not yet written |  | number | 0.0 to 19.42; 588 distinct | 2282 |
| `potential_end_users` | not yet written |  | text | for example 5 LNG industrial clients, AL power plant (~3 mi.), Atmos Energy; 68 distinct | 3321 |
| `end_user_s` | not yet written |  | text | for example AES Indiana, ANR Pipeline Company; Kwik Trip, Abengoa Bioenergy Corporation; 544 distinct | 2116 |
| `project_developer_s` | not yet written |  | text | for example AES Indiana; Granger Energy, APTIM, APTIM; DTE Vantage; 429 distinct | 2026 |
| `product_supplier_s` | not yet written |  | text | for example 2G Energy, Inc., 2G Energy, Inc.; Caterpillar, Inc., 2G Energy, Inc.; MWM of America; 130 distinct | 2509 |
| `self_developed` | not yet written |  | text | No, Unknown, Yes | 0 |
| `current_year_emission_reductions_mmtco2e_yr_direct` | not yet written |  | number | 0.0 to 1.3001; 461 distinct | 0 |
| `current_year_emission_reductions_mmtco2e_yr_avoided` | not yet written |  | number | 0.0 to 0.11294; 454 distinct | 0 |

### `epa_needs_units`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 38030.

- **Source:** epa:needs_2025_reference_case U.S. Environmental Protection Agency, National Electric Energy Data System (NEEDS) for the 2025 Reference Case (https://www.epa.gov/power-sector-modeling/national-electric-energy-data-system-needs)
- **Method note:** [`docs/methods/epa_needs_units.md`](../methods/epa_needs_units.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). National Electric Energy Data System (NEEDS) for the 2025 Reference Case. Via the Energy Research Warehouse (ERW), table `epa_needs_units`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example epa_needs:0_I_1, epa_needs:10002_G_GEN1, epa_needs:10003_B_BLR1; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | equipment, generator | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example (3K) 59 Hetcheltown Rd P3101, 0 Hammond St CSG 0HAMP, 0 Hammond St CSG OHAMB; more than 5000 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 52 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 38030 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 38030 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | 0.0 to 2561.2; 2293 distinct | 7 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | active | 15342 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 38030 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 38030 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:needs_2025_reference_case | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epa.gov/system/files/documents/2025-12/needs-for-2025-reference-case.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T01:59:08Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2025-12-15T18:55:14Z | 0 |
| `x_needs_sheet` | not yet written |  | text | active, dropped_capacity, hardwired_capacity, retired_by_2028 | 0 |
| `x_unique_id` | not yet written |  | text | for example 0_I_1, 10002_G_GEN1, 10003_B_BLR1; more than 5000 distinct | 0 |
| `x_oris` | not yet written |  | integer | 0 to 68893; more than 5000 distinct | 0 |
| `x_unit_kind` | not yet written |  | text | B, G, I | 0 |
| `x_unit_id` | not yet written |  | text | for example 00001, 00003, 0000A; more than 5000 distinct | 3 |
| `x_camd_unit_id` | not yet written |  | integer | 1 to 91323; 3476 distinct | 33977 |
| `x_plant_type` | not yet written |  | text | Biomass, Coal Steam, Combined Cycle, Combustion Turbine, Energy Storage, Fossil Waste, Fuel Cell, Geothermal, Hydro, IGCC, IMPORT, Landfill Gas, Municipal Solid Waste, Non-Fossil Waste, Nuclear, O/G Steam, Offshore Wind, Onshore Wind, Pumped Storage, Solar PV, Solar Thermal, Tires | 0 |
| `x_ct_ic` | not yet written |  | text | IC Engine | 33715 |
| `x_ipm_region` | not yet written |  | text | for example ERC_FRNT, ERC_GWAY, ERC_PHDL; 67 distinct | 10581 |
| `x_county` | not yet written |  | text | for example ANOKA, Abbeville, Acadia; 1617 distinct | 114 |
| `x_fips5` | not yet written |  | integer | 1001 to 56041; 2253 distinct | 10581 |
| `x_heat_rate_btu_kwh` | not yet written |  | integer | 0 to 40000; 2440 distinct | 11300 |
| `x_online_year` | not yet written |  | integer | 1891 to 2031; 137 distinct | 1407 |
| `x_retirement_year` | not yet written |  | integer | 0 to 2103; 67 distinct | 30767 |
| `x_firing` | not yet written |  | text | Cell, FBC, cell, cyclone, other, stoker/SPR, tangential, vertical, wall | 37250 |
| `x_bottom` | not yet written |  | text | dry, wet | 37383 |
| `x_cogen` | not yet written |  | text | N, Y | 10499 |
| `x_fuels` | not yet written |  | text | for example Biomass, Bituminous, Bituminous, Natural Gas; 32 distinct | 11300 |
| `x_scrubber` | not yet written |  | text | Dry Scrubber, Reagent Injection, Wet Scrubber | 37556 |
| `x_nox_comb_control` | not yet written |  | text | for example AA, AA + FR, AA + LNB; 105 distinct | 34426 |
| `x_nox_post_comb_control` | not yet written |  | text | ReACT, SCR, SNCR | 35670 |
| `x_pm_control` | not yet written |  | text | B, B + C, B + WS, C, ESPC, ESPC + B, ESPC + B + WS, ESPC + C, ESPC + WESP, ESPC + WS, ESPH, ESPH + B, ESPH + B + C, ESPH + B + WS, ESPH + C, ESPH + WESP, WESP + B, WS | 37323 |
| `x_mercury_controls` | not yet written |  | text | ACI | 37680 |
| `x_so2_permit_rate` | not yet written |  | number | 0.00064 to 10.0; 265 distinct | 33595 |
| `x_nox_rate_mode1` | not yet written |  | number | 0.0 to 4.79601; 3530 distinct | 11300 |
| `x_ccs` | not yet written |  | text | Y | 38028 |
| `x_c2g` | not yet written |  | text | C2G, C2G (RFO), C2G/Retire | 38001 |
| `x_bart` | not yet written |  | text | Yes | 37950 |
| `x_owner` | not yet written |  | text | for example 0HAM WHAM8 Solar, LLC, 1000 Mile Solar, LLC, 126 Grove Solar LLC; more than 5000 distinct | 1 |
| `x_owner_percent` | not yet written |  | number | 20.0 to 100.0; 152 distinct | 1 |
| `x_holding_company` | not yet written |  | text | for example 0HAM WHAM8 Solar, LLC, 1000 Mile Solar, LLC, 126 Grove Solar LLC; more than 5000 distinct | 1 |
| `x_holding_company_percent` | not yet written |  | number | 20.0 to 100.0; 152 distinct | 1 |
| `x_regulatory_status` | not yet written |  | text | Non-regulated, Regulated | 228 |
| `x_drop_reason` | not yet written |  | text | Dropped - Lack of model plants, Dropped - Planned unit whose status does not meet NEEDS criteria, Dropped - Plant is identified as onsite because it is a net buyer of electricity in 2021, Dropped - Project has been canceled or postponed, Dropped - Retired/Planned Retirement by 06/2028, Dropped - Units whose status are "OS" or "RE" for the past 3 consecutive years, Dropped - in Alaska or in Hawaii or Puerto Rico | 26537 |

### `epa_rfs_fuel_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 568.

- **Source:** epa:rfs_emts U.S. Environmental Protection Agency, Public Data for the Renewable Fuel Standard (EMTS) (https://www.epa.gov/fuels-registration-reporting-and-compliance-help/public-data-renewable-fuel-standard)
- **Method note:** [`docs/methods/epa_rfs_rins.md`](../methods/epa_rfs_rins.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). Public Data for the Renewable Fuel Standard: RIN generation and renewable fuel volume production (EMTS). Via the Energy Research Warehouse (ERW), table `epa_rfs_fuel_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example epa_rfs:d3:171, epa_rfs:d3:190, epa_rfs:d3:195; 32 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z, 2026-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 270 to 14967243350; 459 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count, gal | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 568 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | Biodiesel (EV 1.5), Biogas (77,000 Btu LHV/1 gallon), Butanol (EV 1.3), Cellulosic Diesel (EV application required), Cellulosic Ethanol (EV 1.0), Cellulosic Heating Oil (EV application required), Cellulosic Renewable Gasoline Blendstock (EV application required), LPG (EV 1.1), Non-cellulosic Ethanol (EV 1.0), Non-ester Renewable Diesel (EV 1.5), Non-ester Renewable Diesel (EV 1.6), Non-ester Renewable Diesel (EV 1.7), Renewable Compressed Natural Gas, Renewable Compressed Natural Gas - CNG, Renewable Gasoline (EV 1.5), Renewable Heating Oil (EV 1.6), Renewable Jet Fuel (EV 1.0), Renewable Jet Fuel (EV 1.6), Renewable Jet Fuel (EV 1.7), Renewable Liquefied Natural Gas, Renewable Naphtha (EV 1.4), Renewable Naphtha (EV 1.5), Renewable Natural Gas - RNG | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:rfs_emts | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epa.gov/system/files/other-files/2026-10/fuelproduction_sep2026.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:42:32Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-14T21:34:41Z | 0 |
| `x_fuel_category` | not yet written |  | text | Biodiesel (EV 1.5), Biogas (77,000 Btu LHV/1 gallon), Butanol (EV 1.3), Cellulosic Diesel (EV application required), Cellulosic Ethanol (EV 1.0), Cellulosic Heating Oil (EV application required), Cellulosic Renewable Gasoline Blendstock (EV application required), LPG (EV 1.1), Non-cellulosic Ethanol (EV 1.0), Non-ester Renewable Diesel (EV 1.5), Non-ester Renewable Diesel (EV 1.6), Non-ester Renewable Diesel (EV 1.7), Renewable Compressed Natural Gas, Renewable Compressed Natural Gas - CNG, Renewable Gasoline (EV 1.5), Renewable Heating Oil (EV 1.6), Renewable Jet Fuel (EV 1.0), Renewable Jet Fuel (EV 1.6), Renewable Jet Fuel (EV 1.7), Renewable Liquefied Natural Gas, Renewable Naphtha (EV 1.4), Renewable Naphtha (EV 1.5), Renewable Natural Gas - RNG | 0 |
| `x_d_code_name` | not yet written |  | text | Advanced Biofuel, Biomass-Based Diesel, Cellulosic Biofuel, Cellulosic Diesel, Renewable Fuel | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `batch_volume` |  | gal | 284 | 2010-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `rins_generated` |  | count | 284 | 2010-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

### `epa_rfs_rins_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1632.

- **Source:** epa:rfs_emts U.S. Environmental Protection Agency, Public Data for the Renewable Fuel Standard (EMTS) (https://www.epa.gov/fuels-registration-reporting-and-compliance-help/public-data-renewable-fuel-standard)
- **Method note:** [`docs/methods/epa_rfs_rins.md`](../methods/epa_rfs_rins.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). Public Data for the Renewable Fuel Standard: RIN generation and renewable fuel volume production (EMTS). Via the Energy Research Warehouse (ERW), table `epa_rfs_rins_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | epa_rfs:d3, epa_rfs:d4, epa_rfs:d5, epa_rfs:d6, epa_rfs:d7 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-07-01T00:00:00Z to 2026-09-01T00:00:00Z; 195 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 472 to 1365563204; 1391 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count, gal | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1632 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | Advanced Biofuel, Biomass-Based Diesel, Cellulosic Biofuel, Cellulosic Diesel, Renewable Fuel | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:rfs_emts | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epa.gov/system/files/other-files/2026-10/rindata_sep2026.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:42:34Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-14T21:35:00Z | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `batch_volume` |  | gal | 816 | 2010-07-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `rins_generated` |  | count | 816 | 2010-07-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `epa_tri_energy_releases_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 384483.

- **Source:** epa:tri_basic U.S. Environmental Protection Agency, Toxics Release Inventory (TRI) Program, TRI Basic Data Files (https://www.epa.gov/toxics-release-inventory-tri-program/tri-basic-data-files-calendar-years-1987-present)
- **Method note:** [`docs/methods/epa_tri_energy_releases_annual.md`](../methods/epa_tri_energy_releases_annual.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). Toxics Release Inventory (TRI) basic data files, US, by reporting year. Via the Energy Research Warehouse (ERW), table `epa_tri_energy_releases_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example tri:00612PRPCMPR681:0000091203:1315213976006, tri:00612PRPCMPR681:0000091203:1316215151085, tri:00612PRPCMPR681:0000091203:1317216110027; more than 5000 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 73621326.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | g, lb | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 55 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 384483 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example 50 BUTTES, ACA SHAD HMA PLANT, ACA SOUTEL HMA PLANT; 2624 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:tri_basic | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2015_US/csv, https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2016_US/csv, https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2017_US/csv, https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2018_US/csv, https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2019_US/csv, https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2020_US/csv, https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2021_US/csv, https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2022_US/csv, https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2023_US/csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T22:33:49Z, 2026-10-23T22:37:06Z, 2026-10-23T22:37:43Z, 2026-10-23T22:38:25Z, 2026-10-23T22:39:07Z, 2026-10-23T22:39:47Z, 2026-10-23T22:40:30Z, 2026-10-23T22:41:11Z, 2026-10-23T22:41:56Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 384483 |
| `x_trifd` | not yet written |  | text | for example 00612PRPCMPR681, 00619CRBBNLUCHE, 00624CLCTRRD337; 2856 distinct | 0 |
| `x_frs_id` | not yet written |  | integer | 110000307800 to 110071821104; 2846 distinct | 72 |
| `x_chemical_id` | not yet written |  | text | for example 0000050000, 0000056235, 0000060355; 193 distinct | 0 |
| `x_chemical` | not yet written |  | text | for example 1,1,1,2-Tetrachloroethane, 1,1,1-Trichloroethane, 1,1,2,2-Tetrachloroethane; 208 distinct | 0 |
| `x_cas` | not yet written |  | text | for example 100-02-7, 100-41-4, 100-42-5; 193 distinct | 0 |
| `x_sector` | not yet written |  | text | Coal Mining, Electric Utilities, Natural Gas Processing, Petroleum, Petroleum Bulk Terminals | 0 |
| `x_sector_code` | not yet written |  | integer | 211, 2121, 2211, 324, 4247 | 0 |
| `x_naics` | not yet written |  | integer | 211111, 211112, 211130, 212111, 212112, 212114, 212115, 221111, 221112, 221113, 221117, 221118, 221121, 221122, 324110, 324121, 324122, 324191, 324199, 424710 | 0 |
| `x_county` | not yet written |  | text | for example ACADIA PARISH, ACCOMACK, ADA; 832 distinct | 0 |
| `x_latitude` | not yet written |  | number | 13.38531 to 70.19975; 2812 distinct | 0 |
| `x_longitude` | not yet written |  | number | -166.535932 to 145.764563; 2811 distinct | 0 |
| `x_parent` | not yet written |  | text | for example A TEICHERT & SON INC, ABH ENTERPRISES INC, ADAMS RESOURCES & ENERGY INC; 583 distinct | 282 |
| `x_carcinogen` | not yet written |  | text | NO, YES | 0 |
| `x_pbt` | not yet written |  | text | NO, YES | 0 |
| `x_pfas` | not yet written |  | text | NO, YES | 0 |
| `x_form_type` | not yet written |  | text | A, R | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `off_site_release_total` |  | g; lb | 128161 | 2015-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `on_site_release_total` |  | g; lb | 128161 | 2015-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `total_releases` |  | g; lb | 128161 | 2015-01-01T00:00:00Z | 2023-01-01T00:00:00Z |

