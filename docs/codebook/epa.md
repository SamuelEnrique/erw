# Codebook: epa

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 8 public tables (2 entities, 6 series; tiers: 8 source); 8 documented in full.

- [`epa_ghg_inventory_annual`](#epa_ghg_inventory_annual): One line of EPA's national greenhouse gas Inventory (1990 to 2022 edition) for one economic sector, or the nation, in one year, from Chapter 2 Table 2-10, 2-11 or 2-12.
- [`epa_ghgrp_facility_emissions`](#epa_ghgrp_facility_emissions): One reporting facility's (or, for transmission pipelines and gas distribution companies, one facility-state's) total reported greenhouse gas emissions in one segment of EPA's GHGRP data summary in one year, 2015 to 2023.
- [`epa_ghgrp_power_co2`](#epa_ghgrp_power_co2): One power plant's (a GHGRP facility reporting under subpart D, electricity generation) reported CO2 of one kind in one reporting year, 2010 to 2023.
- [`epa_lmop_landfill_projects`](#epa_lmop_landfill_projects): One landfill and one landfill gas energy project at it (or the landfill alone, with a project id of its own) in EPA's LMOP database as of September 2024.
- [`epa_needs_units`](#epa_needs_units): One generating unit (a generator, or a boiler carrying the unit's capacity) of EPA's NEEDS inventory for the 2025 reference case of its power sector model (IPM), from one of four sheets.
- [`epa_rfs_fuel_annual`](#epa_rfs_fuel_annual): One renewable fuel category's (under one D code) RINs generated or batch volume in one RIN year of EPA's Renewable Fuel Standard data, 2010 to 2026.
- [`epa_rfs_rins_monthly`](#epa_rfs_rins_monthly): One D code's RINs generated or renewable fuel batch volume in one production month of EPA's Renewable Fuel Standard data, July 2010 to September 2026.
- [`epa_tri_energy_releases_annual`](#epa_tri_energy_releases_annual): One Toxics Release Inventory form (one facility's report of one chemical, a document control number) of the five energy industries in one reporting year, 2015 to 2023, with one of its three release totals.

### `epa_ghg_inventory_annual`

One line of EPA's national greenhouse gas Inventory (1990 to 2022 edition) for one economic sector, or the nation, in one year, from Chapter 2 Table 2-10, 2-11 or 2-12.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 5016.

- **Time:** ts_utc is 1 January of the year (UTC), naming the calendar year; freq P1Y.
- **Revisions:** Rewritten whole by each run (a snapshot of one edition); vintage is the zip's Last-Modified time. No job runs the connector.
- **Source:** epa:ghg_inventory_1990_2022 EPA, Inventory of U.S. Greenhouse Gas Emissions and Sinks: 1990-2022 (https://www.epa.gov/ghgemissions/inventory-us-greenhouse-gas-emissions-and-sinks-1990-2022)
- **Method note:** [`docs/methods/epa_ghg_inventory_annual.md`](../methods/epa_ghg_inventory_annual.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). Inventory of U.S. Greenhouse Gas Emissions and Sinks: 1990-2022. Via the Energy Research Warehouse (ERW), table `epa_ghg_inventory_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: epa_ghgi:<sector> for the seven sectors of Table 2-10 (electric_power_industry, industry, transportation and the others), or epa_ghgi:us for the three national lines | none | text | epa_ghgi:agriculture, epa_ghgi:commercial, epa_ghgi:electric_power_industry, epa_ghgi:industry, epa_ghgi:residential, epa_ghgi:transportation, epa_ghgi:u_s_territories, epa_ghgi:us | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2022-01-01T00:00:00Z; 33 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | -1011200000 to 7529900000; 1855 distinct | 0 |
| `unit` | The unit of the row's value | none | text | tCO2e | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always US | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5016 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5016 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:ghg_inventory_1990_2022 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epa.gov/system/files/other-files/2024-04/trends-in-greenhouse-gas-emissions-and-removals.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T23:21:15Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The zip's Last-Modified time (2024-08-26) | none | utc time | 2024-08-26T14:52:48Z | 0 |
| `x_table` | The Inventory's Chapter 2 table the row comes from: 2-10 (by economic sector), 2-11 (electric power by gas) or 2-12 (sectors with electricity distributed) | none | text | 2-10, 2-11, 2-12 | 0 |
| `x_sector` | The economic sector as EPA's table names it | none | text | Agriculture, Commercial, Electric Power Industry, Industry, Residential, Transportation, U.S. Territories | 99: Empty on the three national lines (epa_ghgi:us) |
| `x_group` | The gas (Table 2-11) or the basis, Direct Emissions or Electricity-Related (Table 2-12), the line sits under | none | text | CF4, CH4, CO2, Direct Emissions, Electricity-Related, N2O, SF6 | 2805: Empty in Table 2-10 and on the total lines of Tables 2-11 and 2-12 |
| `x_line` | The line's name as EPA prints it (a footnote letter sometimes kept, as Stationary Sourcesa) | none | text | for example Abandoned Oil and Gas Wells, Abandoned Underground Coal Mines, Adipic Acid Production; 75 distinct | 0 |

Variables (85):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `direct:abandoned_oil_and_gas_wells` | The sector's direct emissions from abandoned oil and gas wells (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:abandoned_underground_coal_mines` | The sector's direct emissions from abandoned underground coal mines (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:adipic_acid_production` | The sector's direct emissions from adipic acid production (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:aluminum_production` | The sector's direct emissions from aluminum production (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:ammonia_production` | The sector's direct emissions from ammonia production (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:anaerobic_digestion_at_biogas_facilities` | The sector's direct emissions from anaerobic digestion at biogas facilities (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:caprolactam_glyoxal_and_glyoxylic_acid_production` | The sector's direct emissions from caprolactam, glyoxal and glyoxylic acid production (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:carbide_production_and_consumption` | The sector's direct emissions from carbide production and consumption (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:carbon_dioxide_consumption` | The sector's direct emissions from carbon dioxide consumption (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:cement_production` | The sector's direct emissions from cement production (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:co2_from_fossil_fuel_combustion` | The sector's CO2 from fossil fuel combustion (Table 2-10) | tCO2e | 231 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:coal_mining` | The sector's direct emissions from coal mining (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:composting` | The sector's direct emissions from composting (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:electrical_equipment` | The sector's direct emissions from electrical equipment (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:electronics_industry` | The sector's direct emissions from the electronics industry (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:enteric_fermentation` | The sector's direct emissions from enteric fermentation (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:ferroalloy_production` | The sector's direct emissions from ferroalloy production (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:field_burning_of_agricultural_residues` | The sector's direct emissions from field burning of agricultural residues (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:fluorochemical_production` | The sector's direct emissions from fluorochemical production (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:glass_production` | The sector's direct emissions from glass production (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:incineration_of_waste` | The sector's direct emissions from incineration of waste (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:iron_and_steel_production` | The sector's direct emissions from iron and steel production (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:landfills_industrial` | The sector's direct emissions from industrial landfills (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:landfills_municipal` | The sector's direct emissions from municipal landfills (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:lead_production` | The sector's direct emissions from lead production (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:lime_production` | The sector's direct emissions from lime production (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:liming` | The sector's direct emissions from liming (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:magnesium_production_and_processing` | The sector's direct emissions from magnesium production and processing (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:manure_management` | The sector's direct emissions from manure management (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:mobile_combustion` | The sector's direct emissions from mobile combustion (Table 2-10) | tCO2e | 99 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:n2o_from_agricultural_soil_management` | The sector's N2O from agricultural soil management (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:n2o_from_product_uses` | The sector's N2O from product uses (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:natural_gas_systems` | The sector's direct emissions from natural gas systems (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:nitric_acid_production` | The sector's direct emissions from nitric acid production (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:non_energy_use_of_fuels` | The sector's direct emissions from non-energy use of fuels (Table 2-10) | tCO2e | 99 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:other_process_uses_of_carbonates` | The sector's direct emissions from other process uses of carbonates (Table 2-10) | tCO2e | 66 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:petrochemical_production` | The sector's direct emissions from petrochemical production (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:petroleum_systems` | The sector's direct emissions from petroleum systems (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:phosphoric_acid_production` | The sector's direct emissions from phosphoric acid production (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:rice_cultivation` | The sector's direct emissions from rice cultivation (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:sf6_and_pfcs_from_other_product_use` | The sector's SF6 and PFCs from other product use (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:soda_ash_production` | The sector's direct emissions from soda ash production (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:stationary_combustion` | The sector's direct emissions from stationary combustion (Table 2-10) | tCO2e | 198 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:substitution_of_ozone_depleting_substances` | The sector's direct emissions from substitution of ozone depleting substances (Table 2-10) | tCO2e | 132 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:titanium_dioxide_production` | The sector's direct emissions from titanium dioxide production (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:total` | The sector's total direct emissions (Table 2-10) | tCO2e | 231 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:urea_consumption_for_non_agricultural_purposes` | The sector's direct emissions from urea consumption for non-agricultural purposes (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:urea_fertilization` | The sector's direct emissions from urea fertilization (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:wastewater_treatment` | The sector's direct emissions from wastewater treatment (Table 2-10) | tCO2e | 66 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `direct:zinc_production` | The sector's direct emissions from zinc production (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:direct` | The end-use sector's direct emissions (Table 2-12) | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:direct:ch4` | The end-use sector's direct CH4 (Table 2-12) | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:direct:co2` | The end-use sector's direct CO2 (Table 2-12) | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:direct:hfcs` | The end-use sector's direct HFCs (Table 2-12) | tCO2e | 66 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:direct:hfcs_pfcs_sf6_and_nf3` | The end-use sector's direct HFCs, PFCs, SF6 and NF3 (Table 2-12) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:direct:n2o` | The end-use sector's direct N2O (Table 2-12) | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:direct:sf6` | The end-use sector's direct line labelled SF6 (Table 2-12); on Residential it equals the substitution of ozone depleting substances, as EPA labels it | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:electricity_related` | The end-use sector's share of the electric power industry's emissions (Table 2-12) | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:electricity_related:ch4` | The end-use sector's electricity-related CH4 (Table 2-12) | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:electricity_related:co2` | The end-use sector's electricity-related CO2 (Table 2-12) | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:electricity_related:n2o` | The end-use sector's electricity-related N2O (Table 2-12) | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:electricity_related:sf6` | The end-use sector's electricity-related SF6 (Table 2-12) | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `distributed:total` | The end-use sector's total emissions with electricity-related emissions distributed to it (Table 2-12) | tCO2e | 165 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `lulucf_sector_net_total` | The net total of land use, land-use change and forestry (LULUCF), negative as a net sink (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `net_emissions_sources_and_sinks` | The nation's net emissions, sources less sinks (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:cf4` | The electric power industry's CF4 (Table 2-11) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:cf4:electrical_equipment` | The electric power industry's CF4 from electrical equipment (Table 2-11) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:ch4` | The electric power industry's CH4 (methane) (Table 2-11) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:ch4:incineration_of_waste` | The electric power industry's CH4 from incineration of waste (Table 2-11) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:ch4:stationary_sourcesa` | The electric power industry's CH4 from stationary sources, only stationary combustion for electricity generation (EPA's footnote a; the letter kept in the name) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:co2` | The electric power industry's CO2 (Table 2-11) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:co2:coal` | The electric power industry's CO2 from coal (Table 2-11) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:co2:fossil_fuel_combustion` | The electric power industry's CO2 from fossil fuel combustion, a subtotal of the coal, natural gas, petroleum and geothermal lines (Table 2-11) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:co2:geothermal` | The electric power industry's CO2 from geothermal (Table 2-11) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:co2:incineration_of_waste` | The electric power industry's CO2 from incineration of waste (Table 2-11) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:co2:natural_gas` | The electric power industry's CO2 from natural gas (Table 2-11) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:co2:other_process_uses_of_carbonates` | The electric power industry's CO2 from other process uses of carbonates (Table 2-11) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:co2:petroleum` | The electric power industry's CO2 from petroleum (Table 2-11) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:n2o` | The electric power industry's N2O (nitrous oxide) (Table 2-11) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:n2o:incineration_of_waste` | The electric power industry's N2O from incineration of waste (Table 2-11) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:n2o:stationary_sourcesa` | The electric power industry's N2O from stationary sources, only stationary combustion for electricity generation (EPA's footnote a; the letter kept in the name) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:sf6` | The electric power industry's SF6 (Table 2-11) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:sf6:electrical_equipment` | The electric power industry's SF6 from electrical equipment (Table 2-11) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `power:total` | The electric power industry's emissions, all gases (Table 2-11; equals its direct:total) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `total_gross_emissions_sources` | The nation's gross emissions from all sources (Table 2-10) | tCO2e | 33 | 1990-01-01T00:00:00Z | 2022-01-01T00:00:00Z |

Waiting for a second look: The global warming potentials behind tCO2e: the header says the Inventory's tables do not name them, and nothing says they match the GHGRP tables' AR4 weights. Read again on 20 November 2026 in the notes and source lines of the 15 CSV tables of the saved Trends zip under warehouse/raw/epa_ghg_inventory (Table 2-14 says only gross total GWP-weighted values): not found..

### `epa_ghgrp_facility_emissions`

One reporting facility's (or, for transmission pipelines and gas distribution companies, one facility-state's) total reported greenhouse gas emissions in one segment of EPA's GHGRP data summary in one year, 2015 to 2023.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 70338.

- **Time:** ts_utc is the reporting year's 1 January (UTC), naming the year; freq P1Y.
- **Revisions:** Merged by (entity, variable, ts_utc), keeping a run's rows; earlier rows a run does not restate are kept, so a facility EPA drops stays. vintage is the zip's Last-Modified time.
- **Source:** epa:ghgrp_facilities U.S. Environmental Protection Agency, Greenhouse Gas Reporting Program, data summary spreadsheets, ghgp_data_by_year_2023.xlsx (https://www.epa.gov/ghgreporting/data-sets)
- **Method note:** [`docs/methods/epa_ghgrp_facility_emissions.md`](../methods/epa_ghgrp_facility_emissions.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). Greenhouse Gas Reporting Program, data summary spreadsheets (ghgp_data_by_year_2023.xlsx). Via the Energy Research Warehouse (ERW), table `epa_ghgrp_facility_emissions`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ghgrp:<facility id>, or ghgrp:<facility id>:<state> for transmission pipelines and local distribution companies, a row a state where the emissions occur | none | text | for example ghgrp:1000001, ghgrp:1000002, ghgrp:1000003; more than 5000 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1196.25 to 21775439.586; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | tCO2e | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>: the state where the emissions occur where the sheet gives it, else the facility's state | none | text | for example US-AK, US-AL, US-AR; 54 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 70338 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The facility's name, not a pricing node | none | text | for example (430) Civitas Resources - Permian Basin, (540) Civitas Resources - Denver Basin, (540) Civitas Resources - GB - Denver Basin; more than 5000 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:ghgrp_facilities | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epa.gov/system/files/other-files/2024-10/2023_data_summary_spreadsheets.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T17:42:37Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The summary zip's Last-Modified time (2024-10-15) | none | utc time | 2024-10-15T14:42:16Z | 0 |
| `x_segment` | The sheet (segment) of EPA's data summary the row comes from: Direct Point Emitters, Onshore Oil & Gas Prod., Gathering & Boosting, Transmission Pipelines, LDC - Direct Emissions (local gas distribution companies), SF6 from Elec. Equip. | none | text | Direct Point Emitters, Gathering & Boosting, LDC - Direct Emissions, Onshore Oil & Gas Prod., SF6 from Elec. Equip., Transmission Pipelines | 0 |
| `x_frs_id` | The facility's id in EPA's Facility Registry Service (FRS), which joins it to other EPA tables (the source's name: FRS Id) | none | integer | 110000307864 to 110071704324; more than 5000 distinct | 6526: EPA gives no FRS id |
| `x_naics` | The facility's primary NAICS (industry classification) code (the source's name: Primary NAICS Code) | none | integer | 111419 to 928110; 279 distinct | 18: EPA gives no code |
| `x_subparts` | The facility's latest reported industry type, as the GHGRP subpart letters it reports under (the source's name: Latest Reported Industry Type (subparts)) | none | text | for example AA,C, AA,C,II, AA,C,II,TT; 165 distinct | 0 |
| `x_sectors` | The facility's latest reported industry type by sector (Power Plants, Chemicals and the others) (the source's name: Latest Reported Industry Type (sectors)) | none | text | for example Chemicals, Chemicals,Coal-based Liquid Fuel Supply,Suppliers of CO2, Chemicals,Industrial Gas Suppliers; 71 distinct | 10805: The segment's sheet gives no sectors (every segment but direct emitters) |
| `x_basin` | The oil and gas basin, code and name as EPA writes it (the source's name: Basin) | none | text | for example 140 - Florida Platform, 160 - Appalachian Basin, 160A - Appalachian Basin (Eastern Overthrust Area); 44 distinct | 63123: Not an onshore production or gathering and boosting row |
| `x_county` | The facility's county as EPA writes it (the source's name: County (or Reported County)) | none | text | for example ACADIA, ACADIA PARISH, ACCOMACK COUNTY; 2106 distinct | 6800: EPA gives no county |
| `x_emission_state` | The state where the emissions occur, two-letter code (pipelines and distribution companies, listed a row a state) (the source's name: State where Emissions Occur) | none | text | for example AL, AR, AZ; 49 distinct | 67555: Not a transmission pipeline or distribution company row, or EPA names no such state (one row) |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `emissions_direct` | Total reported direct emissions of a direct point emitter, in CO2 equivalent (AR4 weights) | tCO2e | 59533 | 2015-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `emissions_gathering_boosting` | Total reported emissions of a gathering and boosting facility, in CO2 equivalent | tCO2e | 2786 | 2016-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `emissions_ldc` | Total reported direct emissions of a local gas distribution company in one state, in CO2 equivalent | tCO2e | 1499 | 2015-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `emissions_onshore_production` | Total reported emissions of an onshore oil and gas production facility, in CO2 equivalent | tCO2e | 4429 | 2015-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `emissions_sf6_equipment` | Total reported SF6 emissions from electrical transmission equipment, in CO2 equivalent | tCO2e | 806 | 2015-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `emissions_transmission_pipelines` | Total reported emissions of a natural gas transmission pipeline in one state, in CO2 equivalent | tCO2e | 1285 | 2016-01-01T00:00:00Z | 2023-01-01T00:00:00Z |

### `epa_ghgrp_power_co2`

One power plant's (a GHGRP facility reporting under subpart D, electricity generation) reported CO2 of one kind in one reporting year, 2010 to 2023.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 17035.

- **Time:** ts_utc is the reporting year's 1 January (UTC), naming the year; freq P1Y.
- **Revisions:** Rewritten whole by each run from the newest summary zip, so EPA's revisions replace earlier figures; vintage is not filled.
- **Source:** epa:ghgrp U.S. Environmental Protection Agency, Greenhouse Gas Reporting Program, data summary spreadsheets (2023) (https://www.epa.gov/ghgreporting/data-sets)
- **Method note:** [`docs/methods/epa_ghgrp_power_co2.md`](../methods/epa_ghgrp_power_co2.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). Greenhouse Gas Reporting Program, data summary spreadsheets. Via the Energy Research Warehouse (ERW), table `epa_ghgrp_power_co2`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ghgrp:<GHGRP facility id> | none | text | for example ghgrp:1000001, ghgrp:1000049, ghgrp:1000050; 1443 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 22800874.9; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | tCO2 | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> of the facility | none | text | for example US-AL, US-AR, US-AZ; 49 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 17035 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The facility's name, not a pricing node | none | text | for example 23rd and 3rd, 48th Street Peaking Station, A B Brown Generating Station; 1509 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:ghgrp | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epa.gov/system/files/other-files/2024-10/2023_data_summary_spreadsheets.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T17:42:37Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 17035 |
| `x_frs_id` | The facility's id in EPA's Facility Registry Service (FRS) (the source's name: FRS Id) | none | integer | 110000308444 to 110071542884; 1790 distinct | 72: EPA gives no FRS id |
| `x_oris` | The plant's ORIS codes from EPA's GHGRP-to-ORIS power plant crosswalk, joined with ';' | none | text | for example 10, 1001, 10030; 1418 distinct | 49: The facility has no ORIS code in EPA's crosswalk (21 facilities) |
| `x_subparts` | The facility's industry type that year, as the GHGRP subpart letters it reported under (D is electricity generation) (the source's name: Industry Type (subparts)) | none | text | for example C,D, C,D,DD, C,D,DD,MM-REF,P,Y; 35 distinct | 0 |
| `x_naics` | The facility's primary NAICS (industry classification) code (the source's name: Primary NAICS Code) | none | integer | 211112 to 926130; 33 distinct | 0 |
| `x_reporting_year` | The reporting year of the workbook the row was read from | none | integer | 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023 | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `co2_biogenic` | The facility's reported biogenic CO2 emissions | tCO2 | 500 | 2010-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `co2_non_biogenic` | The facility's reported CO2 emissions, non-biogenic (from fossil and other non-biological carbon) | tCO2 | 16535 | 2010-01-01T00:00:00Z | 2023-01-01T00:00:00Z |

### `epa_lmop_landfill_projects`

One landfill and one landfill gas energy project at it (or the landfill alone, with a project id of its own) in EPA's LMOP database as of September 2024.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 3399.

- **Time:** No time column; status_date is blank; project_start_date and project_shutdown_date keep EPA's dates. vintage is the file's last-modified time.
- **Revisions:** A snapshot, rewritten whole by each run; no schedule runs it.
- **Source:** epa:lmop U.S. Environmental Protection Agency, Landfill Methane Outreach Program (LMOP) Database, composite data file (https://www.epa.gov/lmop/lmop-landfill-and-project-database)
- **Method note:** [`docs/methods/epa_lmop_landfill_projects.md`](../methods/epa_lmop_landfill_projects.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). Landfill Methane Outreach Program (LMOP) Database, composite data file. Via the Energy Research Warehouse (ERW), table `epa_lmop_landfill_projects`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: lmop:<Landfill ID>:<Project ID> | none | text | for example lmop:1000:1072-0, lmop:1001:1073-0, lmop:1002:1074-0; 3399 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always project, landfills without a project included | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The landfill's name, then ': ' and the project's name where it has one | none | text | for example 130 Environmental Park (130EP) Landfill, 27th Avenue Landfill, 31st Street Landfill: Project #1; 3361 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> of the landfill (Guam, Puerto Rico and the Virgin Islands among them) | none | text | for example US-AK, US-AL, US-AR; 53 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: EPA's latitude of the landfill; blank on 321 rows | degree | number | 13.429707 to 64.80476; 2302 distinct | 321 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: EPA's longitude of the landfill; blank on 321 rows | degree | number | -166.50657 to 144.750611; 2307 distinct | 321 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: EPA's Rated MW Capacity of the project, repeated on each landfill row of a project fed by several landfills: never sum over rows | MW | number | 0.0 to 50.0; 197 distinct | 2615 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: operating (Operational), under_construction (Construction), planned (Planned), retired (Shutdown); blank for Candidate, Future Potential, Low Potential and Unknown | none | text | operating, planned, retired, under_construction | 1885 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: Not filled: blank in every row | none | empty | no cell holds a value | 3399 |
| `operator` | The operator or owner, as the publisher writes it. Here: The project's owner(s), EPA's Project Owner(s) | none | text | for example AC Landfill Energy, LLC (ACLE (JV of DCO Energy & South Jersey Industries)), APTIM, ARC Technologies Corporation; 186 distinct | 2671 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:lmop | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epa.gov/system/files/documents/2024-09/lmopcompositedata.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T23:11:19Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's last-modified time (2024-09-20) | none | utc time | 2024-09-20T16:32:56Z | 0 |
| `ghgrp_id` | The landfill's 7-digit facility id in EPA's Greenhouse Gas Reporting Program (the source's name: GHGRP ID) | none | integer | 1000010 to 1014715; 1331 distinct | 1348: EPA's cell is blank (the landfill has no GHGRP id) |
| `landfill_id` | EPA's unique number of the landfill (the source's name: Landfill ID) | none | integer | 1 to 21409; 2641 distinct | 0 |
| `landfill_name` | The landfill's name (the source's name: Landfill Name) | none | text | for example 130 Environmental Park (130EP) Landfill, 27th Avenue Landfill, 31st Street Landfill; 2594 distinct | 0 |
| `landfill_alias` | Another name of the landfill (the source's name: Landfill Alias) | none | text | for example "Mount Trashmore", (Sheala) SLF, 10800 County Road 21 NW; 885 distinct | 2064: EPA's cell is blank |
| `state` | The state the landfill is in, two-letter code (the source's name: State) | none | text | for example AK, AL, AR; 53 distinct | 0 |
| `physical_address` | The landfill's physical address (the source's name: Physical Address) | none | text | for example #1 Industry Hills Parkway, .5 miles north of FM 2641, 1 Bob Foeller Drive; 2162 distinct | 462: EPA's cell is blank |
| `city` | The city the landfill is in or near (the source's name: City) | none | text | for example Abbeville, Aberdeen, Abernathy; 1912 distinct | 173: EPA's cell is blank |
| `county` | The county the landfill is in (the source's name: County) | none | text | for example Abbeville, Acadia, Accomack; 1083 distinct | 5: EPA's cell is blank |
| `zip_code` | The landfill's ZIP code (the source's name: Zip Code) | none | text | for example 00605, 00610, 00612; 2124 distinct | 366: EPA's cell is blank |
| `military_landfill` | Yes when a federal or state military branch owns the landfill (the source's name: Military Landfill?) | none | text | No, Yes | 0 |
| `on_tribal_land` | Yes when the landfill is on tribal land (the source's name: On Tribal Land?) | none | text | No, Yes | 0 |
| `anaerobic_digester` | Yes when an anaerobic digester is co-located with the landfill (perhaps under another owner) (the source's name: Anaerobic Digester?) | none | text | No, Yes | 0 |
| `composting` | Yes when composting operations exist within 1 mile of the landfill (the source's name: Composting?) | none | text | No, Yes | 0 |
| `solar_project` | Yes when a solar project is at the landfill site (the source's name: Solar Project?) | none | text | No, Yes | 0 |
| `wind_project` | Yes when a wind project is at the landfill site (the source's name: Wind Project?) | none | text | No, Yes | 0 |
| `ownership_type` | Whether the landfill is publicly owned, privately owned or co-owned (Public, Private, Public/Private, Unknown) (the source's name: Ownership Type) | none | text | Private, Public, Public/Private, Unknown | 0 |
| `landfill_owner_organization_s` | The organization(s) that own the landfill (the source's name: Landfill Owner Organization(s)) | none | text | for example 3M Company, 600 Land, Inc., A. Capuano Brothers, Inc.; 1585 distinct | 149: EPA's cell is blank |
| `landfill_operator_organization` | The organization that operates the landfill (the source's name: Landfill Operator Organization) | none | text | for example 3M Company, A & M Quarries, Inc., A-9 Trucking Enterprise; 1152 distinct | 666: EPA's cell is blank |
| `year_landfill_opened` | The year the landfill opened or began accepting waste (the source's name: Year Landfill Opened) | none | integer | 1900 to 2025; 101 distinct | 376: EPA's cell is blank |
| `landfill_closure_year` | The year the landfill stopped (or is expected to stop) accepting waste, or closed or is expected to close; one value is 2945 as EPA gives it (the source's name: Landfill Closure Year) | none | integer | 1960 to 2945; 216 distinct | 280: EPA's cell is blank |
| `current_landfill_status` | Whether the landfill is Open or Closed (or Unknown) (the source's name: Current Landfill Status) | none | text | Closed, Open, Unknown | 0 |
| `design_landfill_area_acres` | The landfill's design waste mass area (the source's name: Design Landfill Area (acres)) | acre | number | 1.0 to 1388.0; 436 distinct | 1688: EPA's cell is blank |
| `current_landfill_area_acres` | The landfill's current waste mass area (the source's name: Current Landfill Area (acres)) | acre | number | 1.0 to 1620.0; 765 distinct | 1301: EPA's cell is blank |
| `design_landfill_depth_feet` | The landfill's design waste mass depth (maximum or average) (the source's name: Design Landfill Depth (feet)) | foot | number | 2.0 to 540.0; 104 distinct | 2511: EPA's cell is blank |
| `current_landfill_depth_feet` | The landfill's current waste mass depth (maximum or average) (the source's name: Current Landfill Depth (feet)) | foot | number | 10.0 to 500.0; 129 distinct | 2601: EPA's cell is blank |
| `landfill_design_capacity_tons` | The landfill's waste design capacity, in short tons (the source's name: Landfill Design Capacity (tons)) | short ton | integer | 12560 to 994920296; 1316 distinct | 1410: EPA's cell is blank |
| `waste_in_place_tons` | The waste in place at the landfill, in short tons (the source's name: Waste in Place (tons)) | short ton | number | 187.0 to 142250454.0; 1978 distinct | 469: EPA's cell is blank |
| `waste_in_place_year` | The year the waste in place figure refers to (the source's name: Waste in Place Year) | none | integer | 1965 to 2022; 46 distinct | 1233: EPA's cell is blank |
| `annual_waste_acceptance_rate_tons_per_year` | The waste the landfill accepts a year, in short tons (the source's name: Annual Waste Acceptance Rate (tons per year)) | short ton/year | number | 0.0 to 3953108.0; 2049 distinct | 439: EPA's cell is blank |
| `annual_waste_acceptance_year` | The year the waste acceptance rate refers to (the source's name: Annual Waste Acceptance Year) | none | integer | 1965 to 2022; 45 distinct | 1001: EPA's cell is blank |
| `does_lf_recirculate_leachate` | Whether the landfill recirculated leachate (liquid drained from the waste) in the past year: Yes, No or Unknown (the source's name: Does LF Recirculate Leachate?) | none | text | No, Unknown, Yes | 0 |
| `leachate_recirc_frequency_past_10_yrs` | How often the landfill recirculated leachate over the past 10 years (the source's name: Leachate Recirc Frequency (Past 10 Yrs)) | none | text | At least once per year, Not used, Occasionally but not every year, Several times per year | 1: EPA's cell is blank (one row) |
| `permitted_as_rd_d_lf` | Whether the landfill is permitted under the Research, Development and Demonstration (RD&D) Permits Rule for municipal solid waste landfills (the source's name: Permitted as RD&D LF?) | none | text | No, Yes | 0 |
| `lfg_generated_mmscfd` | Estimated landfill gas generated, in million standard cubic feet a day (the source's name: LFG Generated (mmscfd)) | MMscfd | number | 0.036 to 31.405; 919 distinct | 1649: EPA's cell is blank |
| `lfg_collection_system_in_place` | Whether an active gas collection and control system is in place (No also for passive venting or flaring, or perimeter wells only; Shutdown, Unknown) (the source's name: LFG Collection System In Place?) | none | text | No, Shutdown, Unknown, Yes | 0 |
| `lfg_collected_mmscfd` | Landfill gas collected, in million standard cubic feet a day (the source's name: LFG Collected (mmscfd)) | MMscfd | number | 0.0 to 24.951; 943 distinct | 1502: EPA's cell is blank |
| `lfg_collected_year` | The year the landfill gas collected figure refers to (the source's name: LFG Collected Year) | none | integer | 1998, 2003, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024 | 1627: EPA's cell is blank |
| `percent_methane` | The percent of the landfill gas that is methane (the source's name: Percent Methane) | pct | number | 20.0 to 70.0; 308 distinct | 1494: EPA's cell is blank |
| `flares_in_place` | Whether one or more flares are in place at the landfill (Yes, No, Shutdown, Unknown) (the source's name: Flares in Place?) | none | text | No, Shutdown, Unknown, Yes | 0 |
| `number_of_flares` | The number of flares in place (the source's name: Number of Flares) | count | integer | 1, 12, 2, 26, 3, 4, 5, 6, 7, 9 | 2149: EPA's cell is blank |
| `lfg_flared_mmscfd` | Landfill gas flared (in back-up flares when a project operates), in million standard cubic feet a day (the source's name: LFG Flared (mmscfd)) | MMscfd | number | 0.0 to 15.136; 754 distinct | 1742: EPA's cell is blank |
| `lfg_flared_year` | The year the landfill gas flared figure refers to (the source's name: LFG Flared Year) | none | integer | 2008, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024 | 1822: EPA's cell is blank |
| `number_of_wells` | The number of active landfill gas extraction wells (the source's name: Number of Wells) | count | integer | 1 to 2000; 301 distinct | 1593: EPA's cell is blank |
| `gccs_capacity_cfm` | The capacity of the gas collection and control system, in cubic feet a minute (the source's name: GCCS Capacity (cfm)) | cfm | integer | 80 to 45000; 315 distinct | 1652: EPA's cell is blank |
| `passive_venting_flaring` | Yes when the landfill passively vents or flares landfill gas (the source's name: Passive Venting/Flaring?) | none | text | No, Unknown, Yes | 0 |
| `projected_direct_reductions_mmtco2e_yr_mw` | Projected direct methane reductions a year if an electricity project is developed, in million metric tons CO2 equivalent (global warming potential 28) (the source's name: Projected Direct Reductions (MMTCO2e/yr) - MW) | MMTCO2e/year | number | 0.002 to 1.3786; 387 distinct | 2955: EPA's cell is blank |
| `projected_avoided_reductions_mmtco2e_yr_mw` | Projected avoided carbon dioxide reductions a year if an electricity project is developed, in million metric tons CO2 equivalent (the source's name: Projected Avoided Reductions (MMTCO2e/yr) - MW) | MMTCO2e/year | number | 0.0002 to 0.1315; 174 distinct | 2955: EPA's cell is blank |
| `project_id` | EPA's project id: the parent project number, a hyphen and the expansion number (the source's name: Project ID) | none | text | for example 0-0, 100-0, 100-1; 3365 distinct | 0 |
| `lmop_status` | EPA's current project status: Operational, Construction, Planned, Shutdown, Candidate, Future Potential, Low Potential or Unknown (the source's name: Current Project Status) | none | text | Candidate, Construction, Future Potential, Low Potential, Operational, Planned, Shutdown, Unknown | 0 |
| `project_name` | The project's name, where it has one (the source's name: Project Name) | none | text | for example Combination Project, Combination Project #1, Combination Project #1 (MBC Cogen); 107 distinct | 1865: No project name (mostly landfills without a project) |
| `project_start_date` | The date the project or expansion became operational (future dates for planned projects) (the source's name: Project Start Date) | none | date | 1974-04-01 to 2027-12-31; 709 distinct | 1889: EPA's cell is blank |
| `project_shutdown_date` | The date the project or expansion shut down (the source's name: Project Shutdown Date) | none | date | 1975-02-01 to 2024-01-01; 272 distinct | 2683: Not shut down, or no date given (5 Shutdown rows) |
| `project_type_category` | The category of landfill gas energy project: Electricity, Direct (use), Renewable Natural Gas or Unknown (the source's name: Project Type Category) | none | text | Direct, Electricity, Renewable Natural Gas, Unknown | 0 |
| `lfg_energy_project_type` | The project's specific technology (Reciprocating Engine, Boiler, Gas Turbine and the others) (the source's name: LFG Energy Project Type) | none | text | Boiler, Cogeneration, Combined Cycle, Condensate Evaporation, Direct Thermal, Electricity, Fuel Cell, Gas Turbine, Greenhouse, Hydrogen, Industrial, Leachate Evaporation, Linear Generator, Medium Btu, Microturbine, Organic Rankine Cycle, Other, Reciprocating Engine, Steam Turbine, Stirling Cycle Engine, Unknown, Vehicle Fuel | 0 |
| `rng_delivery_method` | How the renewable natural gas is delivered: Pipeline Injection, Local Use or Unknown (the source's name: RNG Delivery Method) | none | text | Local Use, Pipeline Injection, Unknown | 3132: Not a renewable natural gas project, or not given |
| `lfg_use_details` | Details of how the project uses the landfill gas (free text) (the source's name: LFG Use Details) | none | text | for example (1) 1,600 kW Caterpillar 3520 reciprocating engine, (1) 1-MW GE-Jenbacher engine, (1) 1-MW GE-Jenbacher engine & (1) 1.4-MW GE-Jenbacher engine; electricity will power college and Energy Innovation Center (EIC); 1078 distinct | 2110: EPA's cell is blank |
| `actual_mw_generation` | Actual or estimated electric generation of an electricity project (the source's name: Actual MW Generation) | MW | number | 0.0 to 23.4; 398 distinct | 2451: Not an electricity project, or not given |
| `lfg_flow_to_project_mmscfd` | Landfill gas flowing (or to flow, once operational) to the project, in million standard cubic feet a day (the source's name: LFG Flow to Project (mmscfd)) | MMscfd | number | 0.0 to 19.42; 588 distinct | 2282: EPA's cell is blank |
| `potential_end_users` | Potential end users of the gas, for projects under construction or planned (the source's name: Potential End Users) | none | text | for example 5 LNG industrial clients, AL power plant (~3 mi.), Atmos Energy; 68 distinct | 3321: EPA's cell is blank |
| `end_user_s` | The end user organization(s) of the gas or power (the source's name: End User(s)) | none | text | for example AES Indiana, ANR Pipeline Company; Kwik Trip, Abengoa Bioenergy Corporation; 544 distinct | 2116: EPA's cell is blank |
| `project_developer_s` | The project developer organization(s) (the source's name: Project Developer(s)) | none | text | for example AES Indiana; Granger Energy, APTIM, APTIM; DTE Vantage; 429 distinct | 2026: EPA's cell is blank |
| `product_supplier_s` | The product supplier organization(s), such as engine makers (the source's name: Product Supplier(s)) | none | text | for example 2G Energy, Inc., 2G Energy, Inc.; Caterpillar, Inc., 2G Energy, Inc.; MWM of America; 130 distinct | 2509: EPA's cell is blank |
| `self_developed` | Yes when no third-party developer built the project (the landfill owner or end user did) (the source's name: Self-Developed) | none | text | No, Unknown, Yes | 0 |
| `current_year_emission_reductions_mmtco2e_yr_direct` | The project's direct methane reductions in the current year, in million metric tons CO2 equivalent (global warming potential 28) (the source's name: Current Year Emission Reductions (MMTCO2e/yr) - Direct) | MMTCO2e/year | number | 0.0 to 1.3001; 461 distinct | 0 |
| `current_year_emission_reductions_mmtco2e_yr_avoided` | The project's avoided carbon dioxide reductions in the current year, in million metric tons CO2 equivalent (the source's name: Current Year Emission Reductions (MMTCO2e/yr) - Avoided) | MMTCO2e/year | number | 0.0 to 0.11294; 454 distinct | 0 |

### `epa_needs_units`

One generating unit (a generator, or a boiler carrying the unit's capacity) of EPA's NEEDS inventory for the 2025 reference case of its power sector model (IPM), from one of four sheets.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 38030.

- **Time:** No time column; status_date is empty. vintage is the workbook's Last-Modified time (2025-12-15).
- **Revisions:** A snapshot of one NEEDS version, rewritten whole by each run; a later reference case is a new address set in the code.
- **Source:** epa:needs_2025_reference_case U.S. Environmental Protection Agency, National Electric Energy Data System (NEEDS) for the 2025 Reference Case (https://www.epa.gov/power-sector-modeling/national-electric-energy-data-system-needs)
- **Method note:** [`docs/methods/epa_needs_units.md`](../methods/epa_needs_units.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). National Electric Energy Data System (NEEDS) for the 2025 Reference Case. Via the Energy Research Warehouse (ERW), table `epa_needs_units`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: epa_needs:<EPA's UniqueID_Final> (ORIS plant code, unit kind and unit id) | none | text | for example epa_needs:0_I_1, epa_needs:10002_G_GEN1, epa_needs:10003_B_BLR1; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: generator (EPA's G, and its one I, an import) or equipment (B, a boiler) | none | text | equipment, generator | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The plant name and the unit id | none | text | for example (3K) 59 Hetcheltown Rd P3101, 0 Hammond St CSG 0HAMP, 0 Hammond St CSG OHAMB; more than 5000 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> from EPA's state name | none | text | for example US-AK, US-AL, US-AR; 52 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: Not filled | degree | empty | no cell holds a value | 38030 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: Not filled | degree | empty | no cell holds a value | 38030 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: EPA's Capacity (MW); for units with boilers the capacity sits on the boiler row; blank on 7 dropped units | MW | number | 0.0 to 2561.2; 2293 distinct | 7 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: active for a unit of the NEEDS_Active sheet, else blank (x_needs_sheet says which) | none | text | active | 15342 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: Not filled | none | empty | no cell holds a value | 38030 |
| `operator` | The operator or owner, as the publisher writes it. Here: Not filled; the owner is x_owner | none | empty | no cell holds a value | 38030 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:needs_2025_reference_case | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epa.gov/system/files/documents/2025-12/needs-for-2025-reference-case.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T01:59:08Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's Last-Modified time | none | utc time | 2025-12-15T18:55:14Z | 0 |
| `x_needs_sheet` | EPA's sheet the unit is on: active, retired_by_2028, hardwired_capacity (hard-wired into the model) or dropped_capacity (dropped from the model) | none | text | active, dropped_capacity, hardwired_capacity, retired_by_2028 | 0 |
| `x_unique_id` | EPA's unique unit id: ORIS plant code, unit kind and unit id (the source's name: UniqueID_Final) | none | text | for example 0_I_1, 10002_G_GEN1, 10003_B_BLR1; more than 5000 distinct | 0 |
| `x_oris` | The plant's ORIS plant code (the source's name: ORIS Plant Code) | none | integer | 0 to 68893; more than 5000 distinct | 0 |
| `x_unit_kind` | The unit kind: G a generator, B a boiler, I an import (C a committed unit, none here) (the source's name: Boiler/Generator/Committed Unit) | none | text | B, G, I | 0 |
| `x_unit_id` | The unit's id within the plant (the source's name: Unit ID) | none | text | for example 00001, 00003, 0000A; more than 5000 distinct | 3: EPA's cell is blank |
| `x_camd_unit_id` | The unit's id in EPA's CAMD database (the source's name: CAMD Database UnitID) | none | integer | 1 to 91323; 3476 distinct | 33977: EPA's cell is blank |
| `x_plant_type` | EPA's plant type of the unit (Combustion Turbine, Solar PV, Hydro and 19 others) (the source's name: PlantType) | none | text | Biomass, Coal Steam, Combined Cycle, Combustion Turbine, Energy Storage, Fossil Waste, Fuel Cell, Geothermal, Hydro, IGCC, IMPORT, Landfill Gas, Municipal Solid Waste, Non-Fossil Waste, Nuclear, O/G Steam, Offshore Wind, Onshore Wind, Pumped Storage, Solar PV, Solar Thermal, Tires | 0 |
| `x_ct_ic` | EPA's Combustion Turbine/IC Engine column (only 'IC Engine', an internal combustion engine, is written) (the source's name: Combustion Turbine/IC Engine) | none | text | IC Engine | 33715: EPA's cell is blank |
| `x_ipm_region` | The IPM model region of the unit (the source's name: Region Name) | none | text | for example ERC_FRNT, ERC_GWAY, ERC_PHDL; 67 distinct | 10581: Blank in 10,581 dropped units |
| `x_county` | The unit's county as EPA writes it (the source's name: County) | none | text | for example ANOKA, Abbeville, Acadia; 1617 distinct | 114: EPA's cell is blank |
| `x_fips5` | The county's five-digit FIPS code (the source's name: FIPS5) | none | integer | 1001 to 56041; 2253 distinct | 10581: Blank in the same 10,581 dropped units |
| `x_heat_rate_btu_kwh` | The unit's heat rate (fuel heat per kWh generated); EPA writes 0 for 14,852 units (the source's name: Heat Rate (Btu/kWh)) | Btu/kWh | integer | 0 to 40000; 2440 distinct | 11300: EPA leaves it blank (11,300 units) |
| `x_online_year` | The year the unit came on line (the source's name: On Line Year) | none | integer | 1891 to 2031; 137 distinct | 1407: EPA's cell is blank |
| `x_retirement_year` | The unit's retirement year (two dropped units carry 0, as EPA gives it) (the source's name: Retirement Year) | none | integer | 0 to 2103; 67 distinct | 30767: No retirement: EPA's 9999 written blank, or blank |
| `x_firing` | The boiler's firing type as EPA writes it (wall, tangential, cyclone, FBC and the others) (the source's name: Firing) | none | text | Cell, FBC, cell, cyclone, other, stoker/SPR, tangential, vertical, wall | 37250: EPA's cell is blank |
| `x_bottom` | EPA's Bottom column of the boiler: dry or wet (the source's name: Bottom) | none | text | dry, wet | 37383: EPA's cell is blank |
| `x_cogen` | Whether the unit is a cogeneration unit: Y or N (the source's name: Cogen?) | none | text | N, Y | 10499: EPA's cell is blank |
| `x_fuels` | The fuels EPA's model gives the unit (the source's name: Modeled Fuels) | none | text | for example Biomass, Bituminous, Bituminous, Natural Gas; 32 distinct | 11300: EPA's cell is blank |
| `x_scrubber` | The unit's SO2 scrubber: Wet Scrubber, Dry Scrubber or Reagent Injection (the source's name: Wet/DryScrubber) | none | text | Dry Scrubber, Reagent Injection, Wet Scrubber | 37556: EPA's cell is blank (no scrubber given) |
| `x_nox_comb_control` | The unit's NOx combustion controls, EPA's codes joined with '+' (for example LNB low NOx burner technology, OFA overfire air, AA advanced overfire air, LA low excess air, NH3 ammonia injection, H2O water injection), each defined in the workbook's key (the source's name: NOx Comb Control) | none | text | for example AA, AA + FR, AA + LNB; 105 distinct | 34426: EPA's cell is blank |
| `x_nox_post_comb_control` | The unit's NOx post-combustion control: SCR selective catalytic reduction, SNCR selective non-catalytic reduction, ReACT regenerative activated coke technology (the source's name: NOx Post-Comb Control) | none | text | ReACT, SCR, SNCR | 35670: EPA's cell is blank |
| `x_pm_control` | The unit's particulate matter controls, EPA's codes joined with '+': B baghouse, C cyclone, ESPC electrostatic precipitator cold side, ESPH electrostatic precipitator hot side, WESP electrostatic precipitator wet side, WS wet scrubber (the source's name: PM Control) | none | text | B, B + C, B + WS, C, ESPC, ESPC + B, ESPC + B + WS, ESPC + C, ESPC + WESP, ESPC + WS, ESPH, ESPH + B, ESPH + B + C, ESPH + B + WS, ESPH + C, ESPH + WESP, WESP + B, WS | 37323: EPA's cell is blank |
| `x_mercury_controls` | The unit's mercury control: ACI activated carbon injection (the source's name: Mercury_Controls) | none | text | ACI | 37680: EPA's cell is blank |
| `x_so2_permit_rate` | The unit's SO2 permit rate (the source's name: SO2 Permit Rate (lbs/mmBtu)) | lb/MMBtu | number | 0.00064 to 10.0; 265 distinct | 33595: EPA's cell is blank |
| `x_nox_rate_mode1` | The unit's mode 1 NOx rate (the source's name: Mode 1 NOx Rate (lbs/mmBtu)) | lb/MMBtu | number | 0.0 to 4.79601; 3530 distinct | 11300: EPA's cell is blank |
| `x_ccs` | Y when EPA marks the unit with carbon capture and storage (CCS) (the source's name: CCS) | none | text | Y | 38028: EPA's cell is blank |
| `x_c2g` | EPA's coal to gas mark of the unit (C2G, C2G (RFO), C2G/Retire) (the source's name: C2G) | none | text | C2G, C2G (RFO), C2G/Retire | 38001: EPA's cell is blank |
| `x_bart` | Yes when EPA marks the unit a BART affected unit (the source's name: BART Affected Unit) | none | text | Yes | 37950: EPA's cell is blank |
| `x_owner` | The unit's owner as EPA writes it (the source's name: Owner Name) | none | text | for example 0HAM WHAM8 Solar, LLC, 1000 Mile Solar, LLC, 126 Grove Solar LLC; more than 5000 distinct | 1: EPA's cell is blank (one unit) |
| `x_owner_percent` | The owner's share of the unit (the source's name: Owner Percent) | pct | number | 20.0 to 100.0; 152 distinct | 1: EPA's cell is blank (one unit) |
| `x_holding_company` | The owner's holding company as EPA writes it (the source's name: Holding Company) | none | text | for example 0HAM WHAM8 Solar, LLC, 1000 Mile Solar, LLC, 126 Grove Solar LLC; more than 5000 distinct | 1: EPA's cell is blank (one unit) |
| `x_holding_company_percent` | The holding company's share of the unit (the source's name: Holding Company Percent) | pct | number | 20.0 to 100.0; 152 distinct | 1: EPA's cell is blank (one unit) |
| `x_regulatory_status` | Whether the unit is Regulated or Non-regulated (the source's name: Regulatory Status) | none | text | Non-regulated, Regulated | 228: EPA's cell is blank |
| `x_drop_reason` | EPA's reason for dropping the unit from NEEDS (the source's name: Reasons for Dropping the Unit from NEEDS) | none | text | Dropped - Lack of model plants, Dropped - Planned unit whose status does not meet NEEDS criteria, Dropped - Plant is identified as onsite because it is a net buyer of electricity in 2021, Dropped - Project has been canceled or postponed, Dropped - Retired/Planned Retirement by 06/2028, Dropped - Units whose status are "OS" or "RE" for the past 3 consecutive years, Dropped - in Alaska or in Hawaii or Puerto Rico | 26537: Not on the dropped_capacity sheet |

Waiting for a second look: x_firing, x_bottom, x_scrubber: EPA's words (wall, tangential, cyclone, FBC, stoker/SPR, cell, dry, wet, Reagent Injection and the others) are kept; the workbook's Key to Emission Control sheet does not cover these columns. Read again on 20 November 2026 in the saved NEEDS workbook under warehouse/raw/epa_needs (sheet Key to Emission Control and the NEEDS_Active headings): not found.; x_bart: the connector names it BART only; the term is not expanded in the repository. Read again on 20 November 2026 in the saved NEEDS workbook (sheet Key to Emission Control and the NEEDS_Active headings, BART Affected Unit): not found.; x_ct_ic: only 'IC Engine' appears; what an empty cell means beside it is not said. Read again on 20 November 2026 in the saved NEEDS workbook (sheet Key to Emission Control and the NEEDS_Active headings): not found..

### `epa_rfs_fuel_annual`

One renewable fuel category's (under one D code) RINs generated or batch volume in one RIN year of EPA's Renewable Fuel Standard data, 2010 to 2026.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 568.

- **Time:** ts_utc is the RIN year's first day (UTC); freq P1Y. The latest year is partial, to the month the file names.
- **Revisions:** Rewritten whole by each run from the newest monthly file, which carries the whole history; EPA's corrections replace earlier figures. vintage is the file's Last-Modified time.
- **Source:** epa:rfs_emts U.S. Environmental Protection Agency, Public Data for the Renewable Fuel Standard (EMTS) (https://www.epa.gov/fuels-registration-reporting-and-compliance-help/public-data-renewable-fuel-standard)
- **Method note:** [`docs/methods/epa_rfs_rins.md`](../methods/epa_rfs_rins.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). Public Data for the Renewable Fuel Standard: RIN generation and renewable fuel volume production (EMTS). Via the Energy Research Warehouse (ERW), table `epa_rfs_fuel_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: epa_rfs:d<code>:<EPA's fuel category code> | none | text | for example epa_rfs:d3:171, epa_rfs:d3:190, epa_rfs:d3:195; 32 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z, 2026-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 270 to 14967243350; 459 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count, gal | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always US | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 568 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The fuel category as EPA names it, not a pricing node (the same as x_fuel_category) | none | text | Biodiesel (EV 1.5), Biogas (77,000 Btu LHV/1 gallon), Butanol (EV 1.3), Cellulosic Diesel (EV application required), Cellulosic Ethanol (EV 1.0), Cellulosic Heating Oil (EV application required), Cellulosic Renewable Gasoline Blendstock (EV application required), LPG (EV 1.1), Non-cellulosic Ethanol (EV 1.0), Non-ester Renewable Diesel (EV 1.5), Non-ester Renewable Diesel (EV 1.6), Non-ester Renewable Diesel (EV 1.7), Renewable Compressed Natural Gas, Renewable Compressed Natural Gas - CNG, Renewable Gasoline (EV 1.5), Renewable Heating Oil (EV 1.6), Renewable Jet Fuel (EV 1.0), Renewable Jet Fuel (EV 1.6), Renewable Jet Fuel (EV 1.7), Renewable Liquefied Natural Gas, Renewable Naphtha (EV 1.4), Renewable Naphtha (EV 1.5), Renewable Natural Gas - RNG | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:rfs_emts | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epa.gov/system/files/other-files/2026-10/fuelproduction_sep2026.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:42:32Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's Last-Modified time | none | utc time | 2026-10-14T21:34:41Z | 0 |
| `x_fuel_category` | The renewable fuel category as EPA names it (Biodiesel (EV 1.5), Cellulosic Ethanol (EV 1.0) and the others) (the source's name: Fuel Category) | none | text | Biodiesel (EV 1.5), Biogas (77,000 Btu LHV/1 gallon), Butanol (EV 1.3), Cellulosic Diesel (EV application required), Cellulosic Ethanol (EV 1.0), Cellulosic Heating Oil (EV application required), Cellulosic Renewable Gasoline Blendstock (EV application required), LPG (EV 1.1), Non-cellulosic Ethanol (EV 1.0), Non-ester Renewable Diesel (EV 1.5), Non-ester Renewable Diesel (EV 1.6), Non-ester Renewable Diesel (EV 1.7), Renewable Compressed Natural Gas, Renewable Compressed Natural Gas - CNG, Renewable Gasoline (EV 1.5), Renewable Heating Oil (EV 1.6), Renewable Jet Fuel (EV 1.0), Renewable Jet Fuel (EV 1.6), Renewable Jet Fuel (EV 1.7), Renewable Liquefied Natural Gas, Renewable Naphtha (EV 1.4), Renewable Naphtha (EV 1.5), Renewable Natural Gas - RNG | 0 |
| `x_d_code_name` | The name of the fuel's D code (Cellulosic Biofuel D3, Biomass-Based Diesel D4, Advanced Biofuel D5, Renewable Fuel D6, Cellulosic Diesel D7) (the source's name: Fuel) | none | text | Advanced Biofuel, Biomass-Based Diesel, Cellulosic Biofuel, Cellulosic Diesel, Renewable Fuel | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `batch_volume` | The renewable fuel's volume produced, in gallons (EPA's Batch Volume) | gal | 284 | 2010-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `rins_generated` | RINs generated, a count (EPA's RIN Quantity) | count | 284 | 2010-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

### `epa_rfs_rins_monthly`

One D code's RINs generated or renewable fuel batch volume in one production month of EPA's Renewable Fuel Standard data, July 2010 to September 2026.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1632.

- **Time:** ts_utc is the month's first day (UTC), from EPA's RIN_YEAR and Production Month; freq P1M.
- **Revisions:** Rewritten whole by each run from the newest monthly file, which carries the whole history; EPA's corrections replace earlier figures. vintage is the file's Last-Modified time.
- **Source:** epa:rfs_emts U.S. Environmental Protection Agency, Public Data for the Renewable Fuel Standard (EMTS) (https://www.epa.gov/fuels-registration-reporting-and-compliance-help/public-data-renewable-fuel-standard)
- **Method note:** [`docs/methods/epa_rfs_rins.md`](../methods/epa_rfs_rins.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). Public Data for the Renewable Fuel Standard: RIN generation and renewable fuel volume production (EMTS). Via the Energy Research Warehouse (ERW), table `epa_rfs_rins_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: epa_rfs:d<code> (d3 to d7) | none | text | epa_rfs:d3, epa_rfs:d4, epa_rfs:d5, epa_rfs:d6, epa_rfs:d7 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-07-01T00:00:00Z to 2026-09-01T00:00:00Z; 195 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 472 to 1365563204; 1391 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count, gal | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always US | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1632 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The D code's name as EPA's fuel type file gives it, not a pricing node | none | text | Advanced Biofuel, Biomass-Based Diesel, Cellulosic Biofuel, Cellulosic Diesel, Renewable Fuel | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:rfs_emts | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.epa.gov/system/files/other-files/2026-10/rindata_sep2026.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:42:34Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's Last-Modified time | none | utc time | 2026-10-14T21:35:00Z | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `batch_volume` | The renewable fuel's volume produced in the month, in gallons (EPA's BATCH_VOLUME) | gal | 816 | 2010-07-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `rins_generated` | RINs generated in the month, a count (EPA's RIN_QUANTITY) | count | 816 | 2010-07-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `epa_tri_energy_releases_annual`

One Toxics Release Inventory form (one facility's report of one chemical, a document control number) of the five energy industries in one reporting year, 2015 to 2023, with one of its three release totals.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 384483.

- **Time:** ts_utc is the reporting year's 1 January (UTC), naming the calendar year; freq P1Y.
- **Revisions:** Merged by (entity, variable, ts_utc): a run replaces each form's rows and keeps rows it does not restate. vintage is not filled (the service gave no last-modified time).
- **Source:** epa:tri_basic U.S. Environmental Protection Agency, Toxics Release Inventory (TRI) Program, TRI Basic Data Files (https://www.epa.gov/toxics-release-inventory-tri-program/tri-basic-data-files-calendar-years-1987-present)
- **Method note:** [`docs/methods/epa_tri_energy_releases_annual.md`](../methods/epa_tri_energy_releases_annual.md)
- **Cite as:** U.S. Environmental Protection Agency (EPA). Toxics Release Inventory (TRI) basic data files, US, by reporting year. Via the Energy Research Warehouse (ERW), table `epa_tri_energy_releases_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: tri:<TRIFD>:<TRI chemical id>:<document control number>, one form | none | text | for example tri:00612PRPCMPR681:0000091203:1315213976006, tri:00612PRPCMPR681:0000091203:1316215151085, tri:00612PRPCMPR681:0000091203:1317216110027; more than 5000 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 73621326.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | g, lb | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> of the facility, territories included | none | text | for example US-AK, US-AL, US-AR; 55 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 384483 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The facility's name, not a pricing node | none | text | for example 50 BUTTES, ACA SHAD HMA PLANT, ACA SOUTEL HMA PLANT; 2624 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | epa:tri_basic | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2015_US/csv, https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2016_US/csv, https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2017_US/csv, https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2018_US/csv, https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2019_US/csv, https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2020_US/csv, https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2021_US/csv, https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2022_US/csv, https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/2023_US/csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T22:33:49Z, 2026-10-23T22:37:06Z, 2026-10-23T22:37:43Z, 2026-10-23T22:38:25Z, 2026-10-23T22:39:07Z, 2026-10-23T22:39:47Z, 2026-10-23T22:40:30Z, 2026-10-23T22:41:11Z, 2026-10-23T22:41:56Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 384483 |
| `x_trifd` | The facility's TRI facility id (TRIFD) (the source's name: 2. TRIFD) | none | text | for example 00612PRPCMPR681, 00619CRBBNLUCHE, 00624CLCTRRD337; 2856 distinct | 0 |
| `x_frs_id` | The facility's id in EPA's Facility Registry Service, shared with epa_ghgrp_facility_emissions' x_frs_id (the source's name: 3. FRS ID) | none | integer | 110000307800 to 110071821104; 2846 distinct | 72: EPA gives no FRS id (72 rows) |
| `x_chemical_id` | EPA's TRI chemical or compound id (the source's name: 39. TRI CHEMICAL/COMPOUND ID) | none | text | for example 0000050000, 0000056235, 0000060355; 193 distinct | 0 |
| `x_chemical` | The chemical's name (the source's name: 37. CHEMICAL) | none | text | for example 1,1,1,2-Tetrachloroethane, 1,1,1-Trichloroethane, 1,1,2,2-Tetrachloroethane; 208 distinct | 0 |
| `x_cas` | The chemical's CAS registry number as EPA gives it (the source's name: 40. CAS#) | none | text | for example 100-02-7, 100-41-4, 100-42-5; 193 distinct | 0 |
| `x_sector` | EPA's TRI industry sector: Electric Utilities, Petroleum, Petroleum Bulk Terminals, Natural Gas Processing or Coal Mining (the source's name: 23. INDUSTRY SECTOR) | none | text | Coal Mining, Electric Utilities, Natural Gas Processing, Petroleum, Petroleum Bulk Terminals | 0 |
| `x_sector_code` | EPA's TRI industry sector code (2211, 324, 4247, 211, 2121) (the source's name: 22. INDUSTRY SECTOR CODE) | none | integer | 211, 2121, 2211, 324, 4247 | 0 |
| `x_naics` | The form's primary NAICS (industry classification) code (the source's name: 30. PRIMARY NAICS) | none | integer | 211111, 211112, 211130, 212111, 212112, 212114, 212115, 221111, 221112, 221113, 221117, 221118, 221121, 221122, 324110, 324121, 324122, 324191, 324199, 424710 | 0 |
| `x_county` | The facility's county as EPA writes it (the source's name: 7. COUNTY) | none | text | for example ACADIA PARISH, ACCOMACK, ADA; 832 distinct | 0 |
| `x_latitude` | The facility's latitude, decimal degrees as EPA gives it (the source's name: 12. LATITUDE) | degree | number | 13.38531 to 70.19975; 2812 distinct | 0 |
| `x_longitude` | The facility's longitude, decimal degrees as EPA gives it (west negative) (the source's name: 13. LONGITUDE) | degree | number | -166.535932 to 145.764563; 2811 distinct | 0 |
| `x_parent` | The facility's parent company, EPA's standardized name (the source's name: 17. STANDARD PARENT CO NAME) | none | text | for example A TEICHERT & SON INC, ABH ENTERPRISES INC, ADAMS RESOURCES & ENERGY INC; 583 distinct | 282: EPA gives no parent company (282 rows) |
| `x_carcinogen` | Whether the chemical is a carcinogen: YES or NO (the source's name: 46. CARCINOGEN) | none | text | NO, YES | 0 |
| `x_pbt` | EPA's PBT flag of the chemical: YES or NO (the source's name: 47. PBT) | none | text | NO, YES | 0 |
| `x_pfas` | Whether the chemical is a PFAS: YES or NO (the source's name: 48. PFAS) | none | text | NO, YES | 0 |
| `x_form_type` | The form type: R, or A (EPA's short form, which reports no quantities, so its totals are 0) (the source's name: 49. FORM TYPE) | none | text | A, R | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `off_site_release_total` | The form's off-site releases: transferred off site for disposal or release (EPA's OFF-SITE RELEASE TOTAL) | g; lb | 128161 | 2015-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `on_site_release_total` | The form's on-site releases: to air, water, underground injection and land (EPA's ON-SITE RELEASE TOTAL) | g; lb | 128161 | 2015-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `total_releases` | The form's total releases: on-site and off-site disposal or other releases (EPA's TOTAL RELEASES), in lb, or g for dioxins | g; lb | 128161 | 2015-01-01T00:00:00Z | 2023-01-01T00:00:00Z |

Waiting for a second look: x_pbt: the connector says only whether the chemical is 'a PBT'; the term is not expanded in the repository. Read again on 20 November 2026 in the headings and values of the saved TRI basic data CSV under warehouse/raw/epa_tri_energy (column 47. PBT, YES or NO; column 43. CLASSIFICATION, TRI, PBT or Dioxin): not found..

