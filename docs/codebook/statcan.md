# Codebook: statcan

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 8 public tables (8 series; tiers: 8 source); 0 documented in full.

- [`statcan_electricity_generation_monthly`](#statcan_electricity_generation_monthly): Statistics Canada, table 25-10-0015-01, electric power generation, monthly generation by province, class of producer and type of generation, 2008-01 to 2026-07 (session 2176)
- [`statcan_electricity_trade_monthly`](#statcan_electricity_trade_monthly): Statistics Canada, table 25-10-0016-01, electric power generation, monthly receipts, deliveries and availability by province, the trade with the United States and between provinces among them, 2008-01 to 2026-07 (session 2328)
- [`statcan_energy_balance_annual`](#statcan_energy_balance_annual): Statistics Canada, table 25-10-0029-01, supply and demand of primary and secondary energy, by province and fuel, a year, 1995 to 2024 (session 2383)
- [`statcan_generating_capacity_annual`](#statcan_generating_capacity_annual): Statistics Canada, table 25-10-0022-01, installed plants, annual generating capacity by type of electricity generation and class of producer, by province, 2006 to 2025 (session 2418)
- [`statcan_generation_class_annual`](#statcan_generation_class_annual): Statistics Canada, table 25-10-0020-01, Electric power, annual generation by class of producer, by province and type, 2005 to 2025 (session 2440)
- [`statcan_oil_gas_supply_monthly`](#statcan_oil_gas_supply_monthly): Statistics Canada, tables 25-10-0063-01 (supply and disposition of crude oil and equivalent, 2016-01 to 2026-07) and 25-10-0086-01 (natural gas supply and disposition, 2016-01 to 2026-08), monthly, by province (session 2179)
- [`statcan_petroleum_products_monthly`](#statcan_petroleum_products_monthly): Statistics Canada, table 25-10-0081-01, petroleum products by supply and disposition, monthly, by province, 2019-01 to 2026-07 (session 2378)
- [`statcan_power_disposition_annual`](#statcan_power_disposition_annual): Statistics Canada, table 25-10-0021-01, Electric power, electric utilities and industry, annual supply and disposition, by province, 2005 to 2025 (session 2441)

### `statcan_electricity_generation_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 58361.

- **Source:** statcan:25-10-0015-01 Statistics Canada, Table 25-10-0015-01, Electric power generation, monthly generation by type of electricity (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510001501)
- **Method note:** [`docs/methods/statcan_electricity_generation_monthly.md`](../methods/statcan_electricity_generation_monthly.md)
- **Cite as:** Statistics Canada. Table 25-10-0015-01, Electric power generation, monthly generation by type of electricity. Via the Energy Research Warehouse (ERW), table `statcan_electricity_generation_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example statcan_gen:ab:all:combustion_turbine, statcan_gen:ab:all:conventional_steam_turbine, statcan_gen:ab:all:hydraulic_turbine; 458 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2008-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 223 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -155428.0 to 66771096.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | CA, CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-NT, CA-NU, CA-ON, CA-PE, CA-QC, CA-SK, CA-YT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 58361 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Alberta: Electricity producers, electric utilities: Combustion turbine, Alberta: Electricity producers, electric utilities: Conventional steam turbine, Alberta: Electricity producers, electric utilities: Hydraulic turbine; 458 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statcan:25-10-0015-01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www150.statcan.gc.ca/n1/tbl/csv/25100015-eng.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T00:49:55Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-09-29T12:30:43Z | 0 |
| `x_class` | not yet written |  | text | all, industries, utilities | 0 |
| `x_type` | not yet written |  | text | combustion_turbine, conventional_steam_turbine, hydraulic_turbine, internal_combustion_turbine, nuclear_steam_turbine, other_types_of_electricity_generation, solar, tidal_power_turbine, total_all_types_of_electricity_generation, total_electricity_production_from_biomass, total_electricity_production_from_combustible_fuels, total_electricity_production_from_non_renewable_combustible_fuels, wind_power_turbine | 0 |
| `x_total` | not yet written |  | text | yes | 23310 |
| `x_vector` | not yet written |  | text | for example v105899358, v105899359, v1059484806; 458 distinct | 0 |
| `x_revised` | not yet written |  | text | r | 57663 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `generation` |  | MWh | 58361 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `statcan_electricity_trade_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 25215.

- **Source:** statcan:25-10-0016-01 Statistics Canada, Table 25-10-0016-01, Electric power generation, monthly receipts, deliveries and availability (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510001601)
- **Method note:** [`docs/methods/statcan_electricity_trade_monthly.md`](../methods/statcan_electricity_trade_monthly.md)
- **Cite as:** Statistics Canada. Table 25-10-0016-01, Electric power generation, monthly receipts, deliveries and availability. Via the Energy Research Warehouse (ERW), table `statcan_electricity_trade_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | statcan_trade:ab, statcan_trade:bc, statcan_trade:ca, statcan_trade:mb, statcan_trade:nb, statcan_trade:nl, statcan_trade:ns, statcan_trade:nt, statcan_trade:nu, statcan_trade:on, statcan_trade:pe, statcan_trade:qc, statcan_trade:sk, statcan_trade:yt | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2008-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 223 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -11739.0 to 66771096.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | CA, CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-NT, CA-NU, CA-ON, CA-PE, CA-QC, CA-SK, CA-YT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 25215 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Alberta: Deliveries to other provinces, Alberta: Deliveries to the United States, Alberta: Firm deliveries to other provinces; 170 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statcan:25-10-0016-01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www150.statcan.gc.ca/n1/tbl/csv/25100016-eng.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T07:22:19Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-08T12:30:35Z | 0 |
| `x_total` | not yet written |  | text | yes | 11998 |
| `x_vector` | not yet written |  | text | for example v1059484942, v1061444191, v44158996; 170 distinct | 0 |
| `x_revised` | not yet written |  | text | r | 24961 |

Variables (17):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `available_for_use` |  | MWh | 3122 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `deliveries_firm_other_provinces` |  | MWh | 641 | 2008-01-01T00:00:00Z | 2015-12-01T00:00:00Z |
| `deliveries_firm_total` |  | MWh | 936 | 2008-01-01T00:00:00Z | 2015-12-01T00:00:00Z |
| `deliveries_firm_us` |  | MWh | 728 | 2008-01-01T00:00:00Z | 2015-12-01T00:00:00Z |
| `deliveries_non_firm_other_provinces` |  | MWh | 690 | 2008-01-01T00:00:00Z | 2015-12-01T00:00:00Z |
| `deliveries_non_firm_total` |  | MWh | 875 | 2008-01-01T00:00:00Z | 2015-12-01T00:00:00Z |
| `deliveries_non_firm_us` |  | MWh | 786 | 2008-01-01T00:00:00Z | 2015-12-01T00:00:00Z |
| `deliveries_other_provinces` |  | MWh | 2159 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `deliveries_other_total` |  | MWh | 319 | 2008-01-01T00:00:00Z | 2013-12-01T00:00:00Z |
| `deliveries_other_us` |  | MWh | 319 | 2008-01-01T00:00:00Z | 2013-12-01T00:00:00Z |
| `deliveries_total` |  | MWh | 2390 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `deliveries_us` |  | MWh | 2077 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `generation` |  | MWh | 3122 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `receipts_other_provinces` |  | MWh | 2225 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `receipts_total` |  | MWh | 2453 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `receipts_us_other` |  | MWh | 283 | 2008-01-01T00:00:00Z | 2011-12-01T00:00:00Z |
| `receipts_us_purchased` |  | MWh | 2090 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `statcan_energy_balance_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 128420.

- **Source:** statcan:25-10-0029-01 Statistics Canada, Table 25-10-0029-01, Supply and demand of primary and secondary energy in terajoules, annual (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002901)
- **Method note:** [`docs/methods/statcan_energy_balance_annual.md`](../methods/statcan_energy_balance_annual.md)
- **Cite as:** Statistics Canada. Table 25-10-0029-01, Supply and demand of primary and secondary energy in terajoules, annual. Via the Energy Research Warehouse (ERW), table `statcan_energy_balance_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example statcan_eb:ab:aviation_gasoline, statcan_eb:ab:aviation_turbo_fuel, statcan_eb:ab:coke; 354 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1995-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 30 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -2000892777.778 to 6851210277.778; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | CA, CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-NT, CA-NU, CA-ON, CA-PE, CA-QC, CA-SK, CA-YT | 15966 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 128420 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Alberta: Aviation gasoline: All other manufacturing, Alberta: Aviation gasoline: Availability, Alberta: Aviation gasoline: Canadian airlines; more than 5000 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statcan:25-10-0029-01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www150.statcan.gc.ca/n1/tbl/csv/25100029-eng.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T09:09:49Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2025-11-13T13:30:17Z | 0 |
| `x_fuel` | not yet written |  | text | for example Aviation gasoline, Aviation turbo fuel, Canadian bituminous; 28 distinct | 0 |
| `x_line` | not yet written |  | text | for example Agriculture, fishing, hunting and trapping, All other manufacturing, Aluminum and non-ferrous metal manufacturing; 46 distinct | 0 |
| `x_vector` | not yet written |  | text | for example v1038098890, v1038098891, v1038098894; more than 5000 distinct | 0 |
| `x_terminated` | not yet written |  | text | t | 128229 |

Variables (46):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `agriculture_fishing_hunting_and_trapping` |  | MWh | 3947 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `all_other_manufacturing` |  | MWh | 2759 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `aluminum_and_non_ferrous_metal_manufacturing` |  | MWh | 697 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `availability` |  | MWh | 7398 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `canadian_airlines` |  | MWh | 1475 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `canadian_marine` |  | MWh | 1670 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `cement_manufacturing` |  | MWh | 777 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `chemicals_manufacturing` |  | MWh | 1620 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `commercial_and_other_institutional` |  | MWh | 5340 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `construction` |  | MWh | 3199 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `energy_use_final_demand` |  | MWh | 6556 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `exports` |  | MWh | 3509 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `foreign_airlines` |  | MWh | 794 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `foreign_marine` |  | MWh | 997 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `forestry_logging_and_support_activities` |  | MWh | 2132 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `imports` |  | MWh | 3888 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `inter_product_transfers` |  | MWh | 2904 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `inter_regional_transfers` |  | MWh | 4289 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `iron_and_steel_manufacturing` |  | MWh | 936 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_supply` |  | MWh | 8313 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `non_energy_use` |  | MWh | 1817 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `other_adjustments` |  | MWh | 3331 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `pipelines` |  | MWh | 1631 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `producer_consumption` |  | MWh | 3077 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `production` |  | MWh | 4178 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `public_administration` |  | MWh | 4795 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `pulp_and_paper_manufacturing` |  | MWh | 1661 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `railways` |  | MWh | 1417 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `refined_petroleum_products_manufacturing` |  | MWh | 447 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `residential` |  | MWh | 3356 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `retail_pump_sales` |  | MWh | 2126 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `road_transport_and_urban_transit` |  | MWh | 2946 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `statistical_difference` |  | MWh | 4680 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `stock_change_utilities_and_industry` |  | MWh | 32 | 2005-01-01T00:00:00Z | 2009-01-01T00:00:00Z |
| `stock_variation` |  | MWh | 3580 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_airlines` |  | MWh | 1755 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_industrial` |  | MWh | 5528 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_manufacturing` |  | MWh | 3372 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_marine` |  | MWh | 1887 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_mining_and_oil_and_gas_extraction` |  | MWh | 4113 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_transportation` |  | MWh | 4194 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `transformed_to_coke_and_manufactured_gases` |  | MWh | 178 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `transformed_to_electricity_by_industry` |  | MWh | 1001 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `transformed_to_electricity_by_utilities` |  | MWh | 1306 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `transformed_to_refined_petroleum_products` |  | MWh | 987 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `transformed_to_steam_generation` |  | MWh | 1825 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `statcan_generating_capacity_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 5952.

- **Source:** statcan:25-10-0022-01 Statistics Canada, Table 25-10-0022-01, Installed plants, annual generating capacity by type of electricity generation (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002201)
- **Method note:** [`docs/methods/statcan_generating_capacity_annual.md`](../methods/statcan_generating_capacity_annual.md)
- **Cite as:** Statistics Canada. Table 25-10-0022-01, Installed plants, annual generating capacity by type of electricity generation. Via the Energy Research Warehouse (ERW), table `statcan_generating_capacity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example statcan_cap:ab:all, statcan_cap:ab:industry, statcan_cap:ab:private; 55 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 155906.393; 3211 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | CA, CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-NT, CA-NU, CA-ON, CA-PE, CA-QC, CA-SK, CA-YT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 5952 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Alberta: Electricity producer, industries: Combustion turbine, Alberta: Electricity producer, industries: Conventional steam turbine, Alberta: Electricity producer, industries: Internal combustion turbine; 392 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statcan:25-10-0022-01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www150.statcan.gc.ca/n1/tbl/csv/25100022-eng.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T11:01:55Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-19T12:30:44Z | 0 |
| `x_class` | not yet written |  | text | Electricity producer, industries, Electricity producer, private electric utilities, Electricity producer, public electric utilities, Total all classes of electricity producer | 0 |
| `x_type` | not yet written |  | text | Combustion turbine, Conventional steam turbine, Geothermal, Hydraulic turbine, Internal combustion turbine, Nuclear steam turbine, Other non-combustibles, Solar power, Tidal power turbine, Total installed capacity, Total thermal, Wind power turbine | 0 |
| `x_vector` | not yet written |  | text | for example v105775408, v105775409, v105775410; 392 distinct | 0 |
| `x_symbol` | not yet written |  | text | r | 5772 |
| `x_terminated` | not yet written |  | empty | no cell holds a value | 5952 |

Variables (12):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity_combustion_turbine` |  | MW | 668 | 2006-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_conventional_steam_turbine` |  | MW | 707 | 2006-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_geothermal` |  | MW | 12 | 2023-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_hydraulic_turbine` |  | MW | 698 | 2006-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_internal_combustion_turbine` |  | MW | 707 | 2006-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_nuclear_steam_turbine` |  | MW | 160 | 2006-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_other_non_combustibles` |  | MW | 43 | 2018-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_solar_power` |  | MW | 319 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_tidal_power_turbine` |  | MW | 60 | 2006-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `capacity_total` |  | MW | 988 | 2006-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_total_thermal` |  | MW | 927 | 2006-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_wind_power_turbine` |  | MW | 663 | 2006-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `statcan_generation_class_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 5937.

- **Source:** statcan:25-10-0020-01 Statistics Canada, Table 25-10-0020-01, Electric power, annual generation by class of producer (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002001)
- **Method note:** [`docs/methods/statcan_generation_class_annual.md`](../methods/statcan_generation_class_annual.md)
- **Cite as:** Statistics Canada. Table 25-10-0020-01, Electric power, annual generation by class of producer. Via the Energy Research Warehouse (ERW), table `statcan_generation_class_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example statcan_gc:ab:all, statcan_gc:ab:industries, statcan_gc:ab:utilities; 42 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -12018.0 to 649482181.0; 3966 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | CA, CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-NT, CA-NU, CA-ON, CA-PE, CA-QC, CA-SK, CA-YT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 5937 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Alberta: Electricity producer, electric utilities: Combustion turbine, Alberta: Electricity producer, electric utilities: Conventional steam turbine, Alberta: Electricity producer, electric utilities: Geothermal; 407 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statcan:25-10-0020-01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www150.statcan.gc.ca/n1/tbl/csv/25100020-eng.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T11:38:34Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-16T12:30:33Z | 0 |
| `x_class` | not yet written |  | text | Electricity producer, electric utilities, Electricity producer, industries, Total all classes of electricity producer | 0 |
| `x_type` | not yet written |  | text | Combustion turbine, Conventional steam turbine, Geothermal, Hydraulic turbine, Internal combustion turbine, Nuclear steam turbine, Other types of electricity generation, Solar, Tidal power turbine, Total all types of electricity generation, Total electricity production from combustible fuels, Total hydro, tidal, wind, solar and other generation, Total thermal generation, Wind power turbine | 0 |
| `x_vector` | not yet written |  | text | for example v1014073249, v1014073250, v1014073251; 407 distinct | 0 |
| `x_revised` | not yet written |  | text | r | 5840 |

Variables (14):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `combustion_turbine` |  | MWh | 255 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `conventional_steam_turbine` |  | MWh | 279 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `geothermal` |  | MWh | 24 | 2020-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `hydraulic_turbine` |  | MWh | 652 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `internal_combustion_turbine` |  | MWh | 296 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `nuclear_steam_turbine` |  | MWh | 162 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `other_types_of_electricity_generation` |  | MWh | 272 | 2009-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `solar` |  | MWh | 376 | 2009-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `tidal_power_turbine` |  | MWh | 84 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_all_types_of_electricity_generation` |  | MWh | 836 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_electricity_production_from_combustible_fuels` |  | MWh | 480 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_hydro_tidal_wind_solar_and_other_generation` |  | MWh | 761 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_thermal_generation` |  | MWh | 831 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `wind_power_turbine` |  | MWh | 629 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `statcan_oil_gas_supply_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 56007.

- **Source:** statcan:25-10-0063-01 Statistics Canada, Table 25-10-0063-01, Supply and disposition of crude oil and equivalent (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510006301)
- **Source:** statcan:25-10-0086-01 Statistics Canada, Table 25-10-0086-01, Natural gas supply and disposition, monthly (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510008601)
- **Method note:** [`docs/methods/statcan_oil_gas_supply_monthly.md`](../methods/statcan_oil_gas_supply_monthly.md)
- **Cite as:** Statistics Canada. Table 25-10-0063-01, Supply and disposition of crude oil and equivalent; Table 25-10-0086-01, Natural gas supply and disposition, monthly. Via the Energy Research Warehouse (ERW), table `statcan_oil_gas_supply_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | statcan_gas:ab, statcan_gas:bc, statcan_gas:ca, statcan_gas:mb, statcan_gas:nb, statcan_gas:ns, statcan_gas:nt, statcan_gas:on, statcan_gas:qc, statcan_gas:sk, statcan_gas:yt, statcan_oil:ab, statcan_oil:atl, statcan_oil:bc, statcan_oil:ca, statcan_oil:mb, statcan_oil:nb, statcan_oil:nl, statcan_oil:ns, statcan_oil:nt, statcan_oil:on, statcan_oil:qc, statcan_oil:sk | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2016-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 128 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -5245211000.0 to 31025428500.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count, m3 | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | CA, CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-NT, CA-ON, CA-QC, CA-SK, CA-YT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 56007 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Alberta: Closing  inventory, storage, Alberta: Closing inventory, Alberta: Commercial consumption; 383 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statcan:25-10-0063-01, statcan:25-10-0086-01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www150.statcan.gc.ca/n1/tbl/csv/25100063-eng.zip, https://www150.statcan.gc.ca/n1/tbl/csv/25100086-eng.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T01:35:55Z, 2026-10-24T01:37:35Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-09-29T12:30:43Z, 2026-10-23T12:30:28Z | 0 |
| `x_product` | not yet written |  | text | crude_oil, natural_gas | 0 |
| `x_item` | not yet written |  | text | for example Closing  inventory, storage, Closing inventory, Commercial consumption; 56 distinct | 0 |
| `x_parent` | not yet written |  | text | closing_inventory, crude_oil_production, equivalent_products_production, export_to_the_united_states, exports, imports, industrial_consumption, input_to_canadian_refineries, net_field_production_of_crude_oil, net_inventory_changes, non_upgraded_production_of_crude_bitumen, opening_inventory, total_deliveries_to_consumers, total_exports, total_imports | 22265 |
| `x_area_total` | not yet written |  | text | yes | 46778 |
| `x_table` | not yet written |  | text | 25-10-0063-01, 25-10-0086-01 | 0 |
| `x_vector` | not yet written |  | text | for example v1000143842, v1038108347, v1038108349; 463 distinct | 0 |
| `x_revised` | not yet written |  | empty | no cell holds a value | 56007 |

Variables (65):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `closing_inventory` |  | m3 | 1091 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `closing_inventory_fields_and_plants` |  | m3 | 1107 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `closing_inventory_refineries` |  | m3 | 746 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `closing_inventory_storage` |  | m3 | 768 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `closing_inventory_transporters` |  | m3 | 968 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `commercial_consumption` |  | m3 | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `commercial_consumption_customers` |  | count | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `condensate` |  | m3 | 381 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `crude_bitumen_sent_for_further_processing` |  | m3 | 254 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `crude_bitumen_used_as_an_input_in_refineries` |  | m3 | 504 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `crude_oil_production` |  | m3 | 1129 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `deliveries_to_natural_gas_processing_plants` |  | m3 | 512 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `deliveries_to_other_provinces` |  | m3 | 1024 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `equivalent_products_production` |  | m3 | 508 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `export_to_other_countries` |  | m3 | 858 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `export_to_the_united_states` |  | m3 | 944 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `export_to_the_united_states_by_other_modes_of_transport` |  | m3 | 895 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `export_to_the_united_states_by_pipelines` |  | m3 | 587 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `exports` |  | m3 | 944 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `exports_to_other_countries` |  | m3 | 28 | 2025-07-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `exports_to_the_united_states` |  | m3 | 1024 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `gross_withdrawals` |  | m3 | 1024 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `heavy_crude_oil` |  | m3 | 381 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `heavy_crude_oil_used_as_an_input_in_refineries` |  | m3 | 703 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `imports` |  | m3 | 1060 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `imports_from_other_countries` |  | m3 | 256 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `imports_from_the_united_states` |  | m3 | 897 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `imports_of_crude_oil_and_equivalent_products_by_other` |  | m3 | 429 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `imports_of_crude_oil_and_equivalent_products_by_refineries` |  | m3 | 1030 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `in_situ_crude_bitumen_production` |  | m3 | 254 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `industrial_consumption` |  | m3 | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `industrial_consumption_customers` |  | count | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `industrial_deliveries_from_distribution_pipelines` |  | m3 | 1152 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `industrial_deliveries_from_distribution_pipelines_customers` |  | count | 1152 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `industrial_deliveries_from_transmission_pipelines` |  | m3 | 896 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `industrial_deliveries_from_transmission_pipelines_customers` |  | count | 896 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `injections_to_storage` |  | m3 | 768 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `input_to_canadian_refineries` |  | m3 | 730 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `inventory_change_storage` |  | m3 | 768 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `light_and_medium_crude_oil` |  | m3 | 1129 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `light_and_medium_crude_oil_used_as_an_input_in_refineries` |  | m3 | 714 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `marketable_production` |  | m3 | 1260 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `metering_differences_line_losses_and_adjustments` |  | m3 | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `mined_crude_bitumen_production` |  | m3 | 254 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_field_production_of_crude_oil` |  | m3 | 1129 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_inventory_changes` |  | m3 | 1401 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `non_upgraded_production_of_crude_bitumen` |  | m3 | 254 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `opening_inventory` |  | m3 | 1091 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `opening_inventory_fields_and_plants` |  | m3 | 1107 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `opening_inventory_refineries` |  | m3 | 746 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `opening_inventory_storage` |  | m3 | 768 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `opening_inventory_transporters` |  | m3 | 968 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `pentanes_plus` |  | m3 | 381 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `pipeline_fuel` |  | m3 | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `receipts_from_other_provinces` |  | m3 | 1024 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `residential_consumption` |  | m3 | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `residential_consumption_customers` |  | count | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `storage_adjustments` |  | m3 | 768 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `synthetic_crude_oil_production` |  | m3 | 254 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `synthetic_crude_oil_used_as_an_input_in_refineries` |  | m3 | 602 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `total_deliveries_to_consumers` |  | m3 | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `total_deliveries_to_consumers_customers` |  | count | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `total_exports` |  | m3 | 1024 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `total_imports` |  | m3 | 897 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `withdrawals_from_storage` |  | m3 | 768 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `statcan_petroleum_products_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 112385.

- **Source:** statcan:25-10-0081-01 Statistics Canada, Table 25-10-0081-01, Petroleum products by supply and disposition, monthly (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510008101)
- **Method note:** [`docs/methods/statcan_petroleum_products_monthly.md`](../methods/statcan_petroleum_products_monthly.md)
- **Cite as:** Statistics Canada. Table 25-10-0081-01, Petroleum products by supply and disposition, monthly. Via the Energy Research Warehouse (ERW), table `statcan_petroleum_products_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example statcan_pp:ab:asphalt, statcan_pp:ab:aviation_gasoline_blending_components, statcan_pp:ab:butane; 406 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 91 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1222456.0 to 10421525.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | m3 | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | CA, CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-NT, CA-NU, CA-ON, CA-PE, CA-QC, CA-SK, CA-YT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 112385 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Alberta: Ending stocks: Asphalt, Alberta: Ending stocks: Aviation gasoline blending components, Alberta: Ending stocks: Distillate fuel oil; 1331 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statcan:25-10-0081-01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www150.statcan.gc.ca/n1/tbl/csv/25100081-eng.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T09:05:20Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-09-29T12:30:43Z | 0 |
| `x_product` | not yet written |  | text | for example Asphalt, Aviation gasoline blending components, Butane; 31 distinct | 0 |
| `x_parent` | not yet written |  | text | Finished petroleum products, Hydrocarbon gas liquids, Natural gas liquids, Other liquids, Renewable fuels | 8570 |
| `x_total` | not yet written |  | text | yes | 95056 |
| `x_vector` | not yet written |  | text | for example v1251227408, v1251227409, v1251227410; 1331 distinct | 0 |
| `x_revised` | not yet written |  | empty | no cell holds a value | 112385 |

Variables (10):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `adjustments` |  | m3 | 668 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `ending_stocks` |  | m3 | 16200 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `exports` |  | m3 | 20408 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `field_production` |  | m3 | 1183 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `imports` |  | m3 | 24206 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `products_supplied` |  | m3 | 1238 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `refinery_inputs` |  | m3 | 6381 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `refinery_production` |  | m3 | 15430 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `renewable_production` |  | m3 | 463 | 2020-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `stock_change` |  | m3 | 26208 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `statcan_power_disposition_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3909.

- **Source:** statcan:25-10-0021-01 Statistics Canada, Table 25-10-0021-01, Electric power, electric utilities and industry, annual supply and disposition (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002101)
- **Method note:** [`docs/methods/statcan_power_disposition_annual.md`](../methods/statcan_power_disposition_annual.md)
- **Cite as:** Statistics Canada. Table 25-10-0021-01, Electric power, electric utilities and industry, annual supply and disposition. Via the Energy Research Warehouse (ERW), table `statcan_power_disposition_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | statcan_pd:ab, statcan_pd:bc, statcan_pd:ca, statcan_pd:mb, statcan_pd:nb, statcan_pd:nl, statcan_pd:ns, statcan_pd:nt, statcan_pd:nu, statcan_pd:on, statcan_pd:pe, statcan_pd:qc, statcan_pd:sk, statcan_pd:yt | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -8356860.0 to 649482181.0; 3528 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | CA, CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-NT, CA-NU, CA-ON, CA-PE, CA-QC, CA-SK, CA-YT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 3909 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Alberta: Agriculture sales of electricity, Alberta: Electricity used by producers, Alberta: Exports of electricity to the United States, firm; 229 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statcan:25-10-0021-01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www150.statcan.gc.ca/n1/tbl/csv/25100021-eng.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T11:45:47Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-16T12:30:33Z | 0 |
| `x_component` | not yet written |  | text | Agriculture sales of electricity, Electricity used by producers, Exports of electricity to the United States, exchanged, Exports of electricity to the United States, firm, Exports of electricity to the United States, secondary, Imports of electricity from the United States, exchanged, Imports of electricity from the United States, purchased, Interprovincial deliveries of electricity, firm, Interprovincial deliveries of electricity, secondary, Interprovincial receipts of electricity, purchased, Mining and manufacturing sales of electricity, Other industries sales of electricity, Residential sales of electricity, Total electricity available for use within specific geographic border, Total exports of electricity to the United States, Total generation of electricity, Total imports of electricity from the United States, Total interprovincial deliveries of electricity, Total interprovincial receipts of electricity, Total sales of electricity to ultimate customers, Unallocated electricity | 0 |
| `x_vector` | not yet written |  | text | for example v1014073248, v1014074049, v1079014831; 229 distinct | 0 |
| `x_revised` | not yet written |  | text | r | 3824 |

Variables (21):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `agriculture_sales_of_electricity` |  | MWh | 231 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `electricity_used_by_producers` |  | MWh | 294 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `exports_of_electricity_to_the_united_states_exchanged` |  | MWh | 24 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `exports_of_electricity_to_the_united_states_firm` |  | MWh | 70 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `exports_of_electricity_to_the_united_states_secondary` |  | MWh | 78 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `imports_of_electricity_from_the_united_states_exchanged` |  | MWh | 22 | 2005-01-01T00:00:00Z | 2012-01-01T00:00:00Z |
| `imports_of_electricity_from_the_united_states_purchased` |  | MWh | 81 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `interprovincial_deliveries_of_electricity_firm` |  | MWh | 90 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `interprovincial_deliveries_of_electricity_secondary` |  | MWh | 48 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `interprovincial_receipts_of_electricity_purchased` |  | MWh | 93 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `mining_and_manufacturing_sales_of_electricity` |  | MWh | 270 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `other_industries_sales_of_electricity` |  | MWh | 294 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `residential_sales_of_electricity` |  | MWh | 294 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_electricity_available_for_use_within_specific_geographic_border` |  | MWh | 294 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_exports_of_electricity_to_the_united_states` |  | MWh | 199 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_generation_of_electricity` |  | MWh | 294 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_imports_of_electricity_from_the_united_states` |  | MWh | 199 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_interprovincial_deliveries_of_electricity` |  | MWh | 221 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_interprovincial_receipts_of_electricity` |  | MWh | 225 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_sales_of_electricity_to_ultimate_customers` |  | MWh | 294 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `unallocated_electricity` |  | MWh | 294 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

