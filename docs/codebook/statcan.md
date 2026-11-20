# Codebook: statcan

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 8 public tables (8 series; tiers: 8 source); 8 documented in full.

- [`statcan_electricity_generation_monthly`](#statcan_electricity_generation_monthly): One area's (Canada, a province or a territory) electricity generation by one class of producer and one type of generation in one month, from Statistics Canada table 25-10-0015-01.
- [`statcan_electricity_trade_monthly`](#statcan_electricity_trade_monthly): One area's (Canada, a province or a territory) value of one component of electricity supply and disposition (generation, receipts, deliveries, availability) in one month, from Statistics Canada table 25-10-0016-01.
- [`statcan_energy_balance_annual`](#statcan_energy_balance_annual): One area's value of one supply or demand line for one fuel in one year, from Statistics Canada's energy balance, table 25-10-0029-01, converted from terajoules to MWh.
- [`statcan_generating_capacity_annual`](#statcan_generating_capacity_annual): One area's installed generating capacity of one type for one class of producer in one year, from Statistics Canada table 25-10-0022-01.
- [`statcan_generation_class_annual`](#statcan_generation_class_annual): One area's electricity generation of one type by one class of producer in one year, from Statistics Canada table 25-10-0020-01.
- [`statcan_oil_gas_supply_monthly`](#statcan_oil_gas_supply_monthly): One area's value of one supply or disposition item of crude oil and equivalent (table 25-10-0063-01) or of natural gas (table 25-10-0086-01) in one month, from Statistics Canada.
- [`statcan_petroleum_products_monthly`](#statcan_petroleum_products_monthly): One area's value of one supply or disposition item for one petroleum product in one month, from Statistics Canada table 25-10-0081-01.
- [`statcan_power_disposition_annual`](#statcan_power_disposition_annual): One area's value of one component of electricity supply and disposition (generation, trade, sales, losses) in one year, from Statistics Canada table 25-10-0021-01.

### `statcan_electricity_generation_monthly`

One area's (Canada, a province or a territory) electricity generation by one class of producer and one type of generation in one month, from Statistics Canada table 25-10-0015-01.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 58361.

- **Time:** ts_utc is the month's first day at 00:00:00Z (a month, not an instant); freq P1M.
- **Revisions:** Each run writes the whole table again (a snapshot), since StatCan revises the table at the same address; vintage is the zip's Last-Modified time, the same in every row.
- **Source:** statcan:25-10-0015-01 Statistics Canada, Table 25-10-0015-01, Electric power generation, monthly generation by type of electricity (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510001501)
- **Method note:** [`docs/methods/statcan_electricity_generation_monthly.md`](../methods/statcan_electricity_generation_monthly.md)
- **Cite as:** Statistics Canada. Table 25-10-0015-01, Electric power generation, monthly generation by type of electricity. Via the Energy Research Warehouse (ERW), table `statcan_electricity_generation_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statcan_gen:<area>:<class>:<type>, the area ca or the province's or territory's postal code in lower case | none | text | for example statcan_gen:ab:all:combustion_turbine, statcan_gen:ab:all:conventional_steam_turbine, statcan_gen:ab:all:hydraulic_turbine; 458 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2008-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 223 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -155428.0 to 66771096.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: CA for Canada, CA-<province> for a province or territory | none | text | CA, CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-NT, CA-NU, CA-ON, CA-PE, CA-QC, CA-SK, CA-YT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 58361 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The area, class and type as StatCan names them, not a pricing node | none | text | for example Alberta: Electricity producers, electric utilities: Combustion turbine, Alberta: Electricity producers, electric utilities: Conventional steam turbine, Alberta: Electricity producers, electric utilities: Hydraulic turbine; 458 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statcan:25-10-0015-01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www150.statcan.gc.ca/n1/tbl/csv/25100015-eng.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T00:49:55Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The Last-Modified time of StatCan's zip | none | utc time | 2026-09-29T12:30:43Z | 0 |
| `x_class` | The class of electricity producer: all (StatCan's total of all classes), utilities (electric utilities) or industries (the source's name: Class of electricity producer) | none | text | all, industries, utilities | 0 |
| `x_type` | The type of electricity generation, StatCan's name as a slug (hydraulic_turbine, solar, total_all_types_of_electricity_generation and the others) (the source's name: Type of electricity generation) | none | text | combustion_turbine, conventional_steam_turbine, hydraulic_turbine, internal_combustion_turbine, nuclear_steam_turbine, other_types_of_electricity_generation, solar, tidal_power_turbine, total_all_types_of_electricity_generation, total_electricity_production_from_biomass, total_electricity_production_from_combustible_fuels, total_electricity_production_from_non_renewable_combustible_fuels, wind_power_turbine | 0 |
| `x_total` | yes where the class or the type is one of StatCan's totals, never to be summed with its parts | none | text | yes | 23310: Neither the class nor the type is a total |
| `x_vector` | StatCan's vector identifier of the series (the source's name: VECTOR) | none | text | for example v105899358, v105899359, v1059484806; 458 distinct | 0 |
| `x_revised` | r where StatCan marks the figure revised (the source's name: SYMBOL) | none | text | r | 57663: StatCan gives no revision mark |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `generation` | Electricity generated in the month by the class and type of the row, MWh | MWh | 58361 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `statcan_electricity_trade_monthly`

One area's (Canada, a province or a territory) value of one component of electricity supply and disposition (generation, receipts, deliveries, availability) in one month, from Statistics Canada table 25-10-0016-01.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 25215.

- **Time:** ts_utc is the month's first day at 00:00:00Z (a month, not an instant); freq P1M.
- **Revisions:** A snapshot; each run replaces the whole file, so a revised month is revised at the next run; vintage is the zip's Last-Modified time.
- **Source:** statcan:25-10-0016-01 Statistics Canada, Table 25-10-0016-01, Electric power generation, monthly receipts, deliveries and availability (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510001601)
- **Method note:** [`docs/methods/statcan_electricity_trade_monthly.md`](../methods/statcan_electricity_trade_monthly.md)
- **Cite as:** Statistics Canada. Table 25-10-0016-01, Electric power generation, monthly receipts, deliveries and availability. Via the Energy Research Warehouse (ERW), table `statcan_electricity_trade_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statcan_trade:<area>, the area ca or the province's or territory's postal code in lower case | none | text | statcan_trade:ab, statcan_trade:bc, statcan_trade:ca, statcan_trade:mb, statcan_trade:nb, statcan_trade:nl, statcan_trade:ns, statcan_trade:nt, statcan_trade:nu, statcan_trade:on, statcan_trade:pe, statcan_trade:qc, statcan_trade:sk, statcan_trade:yt | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2008-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 223 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -11739.0 to 66771096.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: CA for Canada, CA-<province> for a province or territory | none | text | CA, CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-NT, CA-NU, CA-ON, CA-PE, CA-QC, CA-SK, CA-YT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 25215 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <area>: <component> as StatCan names them, not a pricing node | none | text | for example Alberta: Deliveries to other provinces, Alberta: Deliveries to the United States, Alberta: Firm deliveries to other provinces; 170 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statcan:25-10-0016-01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www150.statcan.gc.ca/n1/tbl/csv/25100016-eng.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T07:22:19Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The Last-Modified time of StatCan's zip | none | utc time | 2026-10-08T12:30:35Z | 0 |
| `x_total` | yes where the component is one of StatCan's totals (its name begins Total), never to be summed with its parts | none | text | yes | 11998: The component is not a total |
| `x_vector` | StatCan's vector identifier of the series (the source's name: VECTOR) | none | text | for example v1059484942, v1061444191, v44158996; 170 distinct | 0 |
| `x_revised` | r where StatCan marks the figure revised (the source's name: SYMBOL) | none | text | r | 24961: StatCan gives no revision mark |

Variables (17):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `available_for_use` | Total electricity available for use within the area's border, MWh | MWh | 3122 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `deliveries_firm_other_provinces` | Firm deliveries to other provinces, MWh | MWh | 641 | 2008-01-01T00:00:00Z | 2015-12-01T00:00:00Z |
| `deliveries_firm_total` | Total firm deliveries, MWh | MWh | 936 | 2008-01-01T00:00:00Z | 2015-12-01T00:00:00Z |
| `deliveries_firm_us` | Firm deliveries to the United States, MWh | MWh | 728 | 2008-01-01T00:00:00Z | 2015-12-01T00:00:00Z |
| `deliveries_non_firm_other_provinces` | Non-firm deliveries to other provinces, MWh | MWh | 690 | 2008-01-01T00:00:00Z | 2015-12-01T00:00:00Z |
| `deliveries_non_firm_total` | Total non-firm deliveries, MWh | MWh | 875 | 2008-01-01T00:00:00Z | 2015-12-01T00:00:00Z |
| `deliveries_non_firm_us` | Non-firm deliveries to the United States, MWh | MWh | 786 | 2008-01-01T00:00:00Z | 2015-12-01T00:00:00Z |
| `deliveries_other_provinces` | Deliveries to other provinces, MWh | MWh | 2159 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `deliveries_other_total` | Total other deliveries, MWh | MWh | 319 | 2008-01-01T00:00:00Z | 2013-12-01T00:00:00Z |
| `deliveries_other_us` | Other deliveries to the United States, MWh | MWh | 319 | 2008-01-01T00:00:00Z | 2013-12-01T00:00:00Z |
| `deliveries_total` | Total deliveries, MWh: for Canada its deliveries to the United States only, for a province also to other provinces | MWh | 2390 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `deliveries_us` | Deliveries to the United States, MWh | MWh | 2077 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `generation` | Total generation in the month, MWh (StatCan's Total generation) | MWh | 3122 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `receipts_other_provinces` | Receipts from other provinces, MWh | MWh | 2225 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `receipts_total` | Total receipts, MWh: for Canada its receipts from the United States only, for a province also from other provinces | MWh | 2453 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `receipts_us_other` | Other receipts from the United States, MWh | MWh | 283 | 2008-01-01T00:00:00Z | 2011-12-01T00:00:00Z |
| `receipts_us_purchased` | Purchased receipts from the United States, MWh | MWh | 2090 | 2008-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `statcan_energy_balance_annual`

One area's value of one supply or demand line for one fuel in one year, from Statistics Canada's energy balance, table 25-10-0029-01, converted from terajoules to MWh.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 128420.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z (a year, not an instant); freq P1Y.
- **Revisions:** A snapshot; each run writes the whole table again; vintage is the zip's Last-Modified time (the release the figures come from).
- **Source:** statcan:25-10-0029-01 Statistics Canada, Table 25-10-0029-01, Supply and demand of primary and secondary energy in terajoules, annual (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002901)
- **Method note:** [`docs/methods/statcan_energy_balance_annual.md`](../methods/statcan_energy_balance_annual.md)
- **Cite as:** Statistics Canada. Table 25-10-0029-01, Supply and demand of primary and secondary energy in terajoules, annual. Via the Energy Research Warehouse (ERW), table `statcan_energy_balance_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statcan_eb:<area>:<fuel>, the area ca, a province's or territory's postal code, atl (the Atlantic provinces) or ter (the three territories together) | none | text | for example statcan_eb:ab:aviation_gasoline, statcan_eb:ab:aviation_turbo_fuel, statcan_eb:ab:coke; 354 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1995-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 30 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -2000892777.778 to 6851210277.778; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: CA or CA-<province>; empty for the Atlantic provinces (atl) and the three territories together (ter), which no single code names | none | text | CA, CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-NT, CA-NU, CA-ON, CA-PE, CA-QC, CA-SK, CA-YT | 15966 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 128420 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <area>: <fuel>: <line> as StatCan names them, not a pricing node | none | text | for example Alberta: Aviation gasoline: All other manufacturing, Alberta: Aviation gasoline: Availability, Alberta: Aviation gasoline: Canadian airlines; more than 5000 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statcan:25-10-0029-01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www150.statcan.gc.ca/n1/tbl/csv/25100029-eng.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T09:09:49Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The Last-Modified time of StatCan's zip | none | utc time | 2025-11-13T13:30:17Z | 0 |
| `x_fuel` | The fuel, StatCan's name (28 fuels, totals among them) (the source's name: Fuel type) | none | text | for example Aviation gasoline, Aviation turbo fuel, Canadian bituminous; 28 distinct | 0 |
| `x_line` | The supply and demand line, StatCan's name (the variable is its slug) (the source's name: Supply and demand characteristics) | none | text | for example Agriculture, fishing, hunting and trapping, All other manufacturing, Aluminum and non-ferrous metal manufacturing; 46 distinct | 0 |
| `x_vector` | StatCan's vector identifier of the series (the source's name: VECTOR) | none | text | for example v1038098890, v1038098891, v1038098894; more than 5000 distinct | 0 |
| `x_terminated` | t where StatCan has ended the series (the source's name: TERMINATED) | none | text | t | 128229: The series is not ended |

Variables (46):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `agriculture_fishing_hunting_and_trapping` | Agriculture, fishing, hunting and trapping use, MWh | MWh | 3947 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `all_other_manufacturing` | All other manufacturing use, MWh | MWh | 2759 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `aluminum_and_non_ferrous_metal_manufacturing` | Aluminum and non-ferrous metal manufacturing use, MWh | MWh | 697 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `availability` | Availability, MWh (StatCan's line) | MWh | 7398 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `canadian_airlines` | Canadian airlines use, MWh | MWh | 1475 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `canadian_marine` | Canadian marine use, MWh | MWh | 1670 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `cement_manufacturing` | Cement manufacturing use, MWh | MWh | 777 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `chemicals_manufacturing` | Chemicals manufacturing use, MWh | MWh | 1620 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `commercial_and_other_institutional` | Commercial and other institutional use, MWh | MWh | 5340 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `construction` | Construction use, MWh | MWh | 3199 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `energy_use_final_demand` | Energy use, final demand, MWh | MWh | 6556 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `exports` | Exports, MWh (subtracted in the balance) | MWh | 3509 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `foreign_airlines` | Foreign airlines use, MWh | MWh | 794 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `foreign_marine` | Foreign marine use, MWh | MWh | 997 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `forestry_logging_and_support_activities` | Forestry, logging and support activities use, MWh | MWh | 2132 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `imports` | Imports, MWh | MWh | 3888 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `inter_product_transfers` | Inter-product transfers, MWh (signed and added) | MWh | 2904 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `inter_regional_transfers` | Inter-regional transfers, MWh (signed and added) | MWh | 4289 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `iron_and_steel_manufacturing` | Iron and steel manufacturing use, MWh | MWh | 936 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_supply` | Net supply, MWh (StatCan's line) | MWh | 8313 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `non_energy_use` | Non-energy use, MWh | MWh | 1817 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `other_adjustments` | Other adjustments, MWh (signed and added) | MWh | 3331 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `pipelines` | Pipelines use, MWh | MWh | 1631 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `producer_consumption` | Producer consumption, MWh | MWh | 3077 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `production` | Production of the fuel in the year, MWh | MWh | 4178 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `public_administration` | Public administration use, MWh | MWh | 4795 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `pulp_and_paper_manufacturing` | Pulp and paper manufacturing use, MWh | MWh | 1661 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `railways` | Railways use, MWh | MWh | 1417 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `refined_petroleum_products_manufacturing` | Refined petroleum products manufacturing use, MWh | MWh | 447 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `residential` | Residential use, MWh | MWh | 3356 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `retail_pump_sales` | Retail pump sales, MWh | MWh | 2126 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `road_transport_and_urban_transit` | Road transport and urban transit use, MWh | MWh | 2946 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `statistical_difference` | Statistical difference, MWh (not part of final demand) | MWh | 4680 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `stock_change_utilities_and_industry` | Stock change, utilities and industry, MWh | MWh | 32 | 2005-01-01T00:00:00Z | 2009-01-01T00:00:00Z |
| `stock_variation` | Stock variation, MWh (positive for a build; subtracted in the balance) | MWh | 3580 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_airlines` | Total airlines use, MWh | MWh | 1755 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_industrial` | Total industrial use, MWh | MWh | 5528 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_manufacturing` | Total manufacturing use, MWh | MWh | 3372 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_marine` | Total marine use, MWh | MWh | 1887 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_mining_and_oil_and_gas_extraction` | Total mining and oil and gas extraction use, MWh | MWh | 4113 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total_transportation` | Total transportation use, MWh | MWh | 4194 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `transformed_to_coke_and_manufactured_gases` | Transformed to coke and manufactured gases, MWh (subtracted) | MWh | 178 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `transformed_to_electricity_by_industry` | Transformed to electricity by industry, MWh (subtracted) | MWh | 1001 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `transformed_to_electricity_by_utilities` | Transformed to electricity by utilities, MWh (subtracted) | MWh | 1306 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `transformed_to_refined_petroleum_products` | Transformed to refined petroleum products, MWh (subtracted) | MWh | 987 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `transformed_to_steam_generation` | Transformed to steam generation, MWh (subtracted) | MWh | 1825 | 1995-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `statcan_generating_capacity_annual`

One area's installed generating capacity of one type for one class of producer in one year, from Statistics Canada table 25-10-0022-01.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 5952.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z (a year, not an instant); freq P1Y.
- **Revisions:** A snapshot; each run asks the zip again and writes the whole table; vintage is the zip's Last-Modified time.
- **Source:** statcan:25-10-0022-01 Statistics Canada, Table 25-10-0022-01, Installed plants, annual generating capacity by type of electricity generation (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002201)
- **Method note:** [`docs/methods/statcan_generating_capacity_annual.md`](../methods/statcan_generating_capacity_annual.md)
- **Cite as:** Statistics Canada. Table 25-10-0022-01, Installed plants, annual generating capacity by type of electricity generation. Via the Energy Research Warehouse (ERW), table `statcan_generating_capacity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statcan_cap:<area>:<class>, the class all, public utilities, private utilities or industry | none | text | for example statcan_cap:ab:all, statcan_cap:ab:industry, statcan_cap:ab:private; 55 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 155906.393; 3211 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: CA for Canada, CA-<province> for a province or territory | none | text | CA, CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-NT, CA-NU, CA-ON, CA-PE, CA-QC, CA-SK, CA-YT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5952 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <area>: <class>: <type> as StatCan names them, not a pricing node | none | text | for example Alberta: Electricity producer, industries: Combustion turbine, Alberta: Electricity producer, industries: Conventional steam turbine, Alberta: Electricity producer, industries: Internal combustion turbine; 392 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statcan:25-10-0022-01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www150.statcan.gc.ca/n1/tbl/csv/25100022-eng.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T11:01:55Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The Last-Modified time of StatCan's zip | none | utc time | 2026-10-19T12:30:44Z | 0 |
| `x_class` | The class of electricity producer, StatCan's name (public or private electric utilities, industries, or the total of all classes) (the source's name: Class of electricity producer) | none | text | Electricity producer, industries, Electricity producer, private electric utilities, Electricity producer, public electric utilities, Total all classes of electricity producer | 0 |
| `x_type` | The type of electricity generation, StatCan's name (the source's name: Type of electricity generation) | none | text | Combustion turbine, Conventional steam turbine, Geothermal, Hydraulic turbine, Internal combustion turbine, Nuclear steam turbine, Other non-combustibles, Solar power, Tidal power turbine, Total installed capacity, Total thermal, Wind power turbine | 0 |
| `x_vector` | StatCan's vector identifier of the series (the source's name: VECTOR) | none | text | for example v105775408, v105775409, v105775410; 392 distinct | 0 |
| `x_symbol` | StatCan's symbol of the figure: r revised (the source's name: SYMBOL) | none | text | r | 5772: StatCan gives no symbol |
| `x_terminated` | StatCan's mark of an ended series (TERMINATED); no row holds one (the source's name: TERMINATED) | none | empty | no cell holds a value | 5952: Always empty: no series of the table is ended |

Variables (12):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity_combustion_turbine` | Installed capacity of combustion turbines, MW | MW | 668 | 2006-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_conventional_steam_turbine` | Installed capacity of conventional steam turbines, MW | MW | 707 | 2006-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_geothermal` | Installed capacity of geothermal plants, MW | MW | 12 | 2023-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_hydraulic_turbine` | Installed capacity of hydraulic turbines, MW | MW | 698 | 2006-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_internal_combustion_turbine` | Installed capacity of internal combustion engines, MW | MW | 707 | 2006-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_nuclear_steam_turbine` | Installed capacity of nuclear steam turbines, MW | MW | 160 | 2006-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_other_non_combustibles` | Installed capacity of other non-combustible types, MW | MW | 43 | 2018-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_solar_power` | Installed capacity of solar power, MW (below 100 kW counted only from 2024) | MW | 319 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_tidal_power_turbine` | Installed capacity of tidal power turbines, MW | MW | 60 | 2006-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `capacity_total` | Total installed capacity, MW (gross, at the generators' terminals) | MW | 988 | 2006-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_total_thermal` | Total thermal installed capacity, MW (the four turbine types below) | MW | 927 | 2006-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `capacity_wind_power_turbine` | Installed capacity of wind power turbines, MW | MW | 663 | 2006-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `statcan_generation_class_annual`

One area's electricity generation of one type by one class of producer in one year, from Statistics Canada table 25-10-0020-01.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 5937.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z (a year, not an instant); freq P1Y.
- **Revisions:** Every run that is not offline asks again and writes the whole table again; vintage is the zip's Last-Modified time.
- **Source:** statcan:25-10-0020-01 Statistics Canada, Table 25-10-0020-01, Electric power, annual generation by class of producer (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002001)
- **Method note:** [`docs/methods/statcan_generation_class_annual.md`](../methods/statcan_generation_class_annual.md)
- **Cite as:** Statistics Canada. Table 25-10-0020-01, Electric power, annual generation by class of producer. Via the Energy Research Warehouse (ERW), table `statcan_generation_class_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statcan_gc:<area>:<class>, the class all, utilities or industries | none | text | for example statcan_gc:ab:all, statcan_gc:ab:industries, statcan_gc:ab:utilities; 42 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -12018.0 to 649482181.0; 3966 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: CA for Canada, CA-<province> for a province or territory | none | text | CA, CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-NT, CA-NU, CA-ON, CA-PE, CA-QC, CA-SK, CA-YT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5937 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <area>: <class>: <type> as StatCan names them, not a pricing node | none | text | for example Alberta: Electricity producer, electric utilities: Combustion turbine, Alberta: Electricity producer, electric utilities: Conventional steam turbine, Alberta: Electricity producer, electric utilities: Geothermal; 407 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statcan:25-10-0020-01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www150.statcan.gc.ca/n1/tbl/csv/25100020-eng.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T11:38:34Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The Last-Modified time of StatCan's zip | none | utc time | 2026-10-16T12:30:33Z | 0 |
| `x_class` | The class of electricity producer, StatCan's name (electric utilities, industries, or the total of all classes) (the source's name: Class of electricity producer) | none | text | Electricity producer, electric utilities, Electricity producer, industries, Total all classes of electricity producer | 0 |
| `x_type` | The type of electricity generation, StatCan's name (the source's name: Type of electricity generation) | none | text | Combustion turbine, Conventional steam turbine, Geothermal, Hydraulic turbine, Internal combustion turbine, Nuclear steam turbine, Other types of electricity generation, Solar, Tidal power turbine, Total all types of electricity generation, Total electricity production from combustible fuels, Total hydro, tidal, wind, solar and other generation, Total thermal generation, Wind power turbine | 0 |
| `x_vector` | StatCan's vector identifier of the series (the source's name: VECTOR) | none | text | for example v1014073249, v1014073250, v1014073251; 407 distinct | 0 |
| `x_revised` | r where StatCan marks the figure revised (the source's name: SYMBOL) | none | text | r | 5840: StatCan gives no revision mark |

Variables (14):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `combustion_turbine` | Generation by combustion turbines, MWh | MWh | 255 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `conventional_steam_turbine` | Generation by conventional steam turbines, MWh | MWh | 279 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `geothermal` | Geothermal generation, MWh | MWh | 24 | 2020-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `hydraulic_turbine` | Generation by hydraulic turbines, MWh | MWh | 652 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `internal_combustion_turbine` | Generation by internal combustion engines, MWh | MWh | 296 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `nuclear_steam_turbine` | Generation by nuclear steam turbines, MWh | MWh | 162 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `other_types_of_electricity_generation` | Other types of electricity generation, MWh | MWh | 272 | 2009-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `solar` | Solar generation, MWh | MWh | 376 | 2009-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `tidal_power_turbine` | Generation by tidal power turbines, MWh | MWh | 84 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_all_types_of_electricity_generation` | Total generation of all types in the year, MWh | MWh | 836 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_electricity_production_from_combustible_fuels` | Total generation from combustible fuels, MWh | MWh | 480 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_hydro_tidal_wind_solar_and_other_generation` | Total hydro, tidal, wind, solar and other generation, MWh | MWh | 761 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_thermal_generation` | Total thermal generation, MWh | MWh | 831 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `wind_power_turbine` | Generation by wind power turbines, MWh | MWh | 629 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `statcan_oil_gas_supply_monthly`

One area's value of one supply or disposition item of crude oil and equivalent (table 25-10-0063-01) or of natural gas (table 25-10-0086-01) in one month, from Statistics Canada.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 56007.

- **Time:** ts_utc is the month's first day at 00:00:00Z (a month, not an instant); freq P1M.
- **Revisions:** Each run writes the whole table again (a snapshot), both zips asked again; vintage is each zip's Last-Modified time (one for crude, one for gas).
- **Source:** statcan:25-10-0063-01 Statistics Canada, Table 25-10-0063-01, Supply and disposition of crude oil and equivalent (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510006301)
- **Source:** statcan:25-10-0086-01 Statistics Canada, Table 25-10-0086-01, Natural gas supply and disposition, monthly (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510008601)
- **Method note:** [`docs/methods/statcan_oil_gas_supply_monthly.md`](../methods/statcan_oil_gas_supply_monthly.md)
- **Cite as:** Statistics Canada. Table 25-10-0063-01, Supply and disposition of crude oil and equivalent; Table 25-10-0086-01, Natural gas supply and disposition, monthly. Via the Energy Research Warehouse (ERW), table `statcan_oil_gas_supply_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statcan_oil:<area> or statcan_gas:<area>, the area ca, atl (the Atlantic provinces) or a province's or territory's postal code in lower case | none | text | statcan_gas:ab, statcan_gas:bc, statcan_gas:ca, statcan_gas:mb, statcan_gas:nb, statcan_gas:ns, statcan_gas:nt, statcan_gas:on, statcan_gas:qc, statcan_gas:sk, statcan_gas:yt, statcan_oil:ab, statcan_oil:atl, statcan_oil:bc, statcan_oil:ca, statcan_oil:mb, statcan_oil:nb, statcan_oil:nl, statcan_oil:ns, statcan_oil:nt, statcan_oil:on, statcan_oil:qc, statcan_oil:sk | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2016-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 128 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -5245211000.0 to 31025428500.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count, m3 | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: CA for Canada and also for the Atlantic provinces' rows (filter on entity, not geo); CA-<province> otherwise | none | text | CA, CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-NT, CA-ON, CA-QC, CA-SK, CA-YT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 56007 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <area>: <item> as StatCan names them, not a pricing node | none | text | for example Alberta: Closing  inventory, storage, Alberta: Closing inventory, Alberta: Commercial consumption; 383 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statcan:25-10-0063-01, statcan:25-10-0086-01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www150.statcan.gc.ca/n1/tbl/csv/25100063-eng.zip, https://www150.statcan.gc.ca/n1/tbl/csv/25100086-eng.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T01:35:55Z, 2026-10-24T01:37:35Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The Last-Modified time of the StatCan zip the row came from | none | utc time | 2026-09-29T12:30:43Z, 2026-10-23T12:30:28Z | 0 |
| `x_product` | The product: crude_oil or natural_gas | none | text | crude_oil, natural_gas | 0 |
| `x_item` | The supply or disposition item, StatCan's name (the source's name: Supply and disposition) | none | text | for example Closing  inventory, storage, Closing inventory, Commercial consumption; 56 distinct | 0 |
| `x_parent` | The variable of the item this one is part of, never to be summed with it | none | text | closing_inventory, crude_oil_production, equivalent_products_production, export_to_the_united_states, exports, imports, industrial_consumption, input_to_canadian_refineries, net_field_production_of_crude_oil, net_inventory_changes, non_upgraded_production_of_crude_bitumen, opening_inventory, total_deliveries_to_consumers, total_exports, total_imports | 22265: The item is part of no other item in the table |
| `x_area_total` | yes for Canada and the Atlantic provinces (areas that hold others) | none | text | yes | 46778: A single province or territory |
| `x_table` | StatCan's table the row came from: 25-10-0063-01 (crude oil) or 25-10-0086-01 (natural gas) | none | text | 25-10-0063-01, 25-10-0086-01 | 0 |
| `x_vector` | StatCan's vector identifier of the series (the source's name: VECTOR) | none | text | for example v1000143842, v1038108347, v1038108349; 463 distinct | 0 |
| `x_revised` | r where StatCan marks the figure revised; no row holds one in this run (the source's name: SYMBOL) | none | empty | no cell holds a value | 56007: StatCan gives no revision mark (every row now) |

Variables (65):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `closing_inventory` | Crude oil: closing inventory, m3 | m3 | 1091 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `closing_inventory_fields_and_plants` | Crude oil: closing inventory at fields and plants, m3 | m3 | 1107 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `closing_inventory_refineries` | Crude oil: closing inventory at refineries, m3 | m3 | 746 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `closing_inventory_storage` | Natural gas: closing inventory in storage, m3 | m3 | 768 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `closing_inventory_transporters` | Crude oil: closing inventory held by transporters, m3 | m3 | 968 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `commercial_consumption` | Natural gas: commercial consumption, m3 | m3 | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `commercial_consumption_customers` | Natural gas: commercial customers, count | count | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `condensate` | Crude oil: condensate production, m3 (part of equivalent products) | m3 | 381 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `crude_bitumen_sent_for_further_processing` | Crude oil: crude bitumen sent for further processing, m3 (part of non-upgraded bitumen) | m3 | 254 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `crude_bitumen_used_as_an_input_in_refineries` | Crude oil: crude bitumen used as an input in refineries, m3 | m3 | 504 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `crude_oil_production` | Crude oil: crude oil production, m3 | m3 | 1129 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `deliveries_to_natural_gas_processing_plants` | Natural gas: deliveries to natural gas processing plants, m3 | m3 | 512 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `deliveries_to_other_provinces` | Natural gas: deliveries to other provinces, m3 | m3 | 1024 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `equivalent_products_production` | Crude oil: equivalent products production, m3 | m3 | 508 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `export_to_other_countries` | Crude oil: exports to other countries, m3 (part of exports) | m3 | 858 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `export_to_the_united_states` | Crude oil: exports to the United States, m3 (part of exports) | m3 | 944 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `export_to_the_united_states_by_other_modes_of_transport` | Crude oil: exports to the United States by other modes of transport, m3 | m3 | 895 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `export_to_the_united_states_by_pipelines` | Crude oil: exports to the United States by pipelines, m3 | m3 | 587 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `exports` | Crude oil: exports, m3 | m3 | 944 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `exports_to_other_countries` | Natural gas: exports to other countries, m3 (part of total exports) | m3 | 28 | 2025-07-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `exports_to_the_united_states` | Natural gas: exports to the United States, m3 (part of total exports) | m3 | 1024 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `gross_withdrawals` | Natural gas: gross withdrawals, m3 (StatCan's thousand m3 times 1,000) | m3 | 1024 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `heavy_crude_oil` | Crude oil: heavy crude oil production, m3 (part of net field production) | m3 | 381 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `heavy_crude_oil_used_as_an_input_in_refineries` | Crude oil: heavy crude oil used as an input in refineries, m3 | m3 | 703 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `imports` | Crude oil: imports, m3 | m3 | 1060 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `imports_from_other_countries` | Natural gas: imports from other countries, m3 (part of total imports) | m3 | 256 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `imports_from_the_united_states` | Natural gas: imports from the United States, m3 (part of total imports) | m3 | 897 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `imports_of_crude_oil_and_equivalent_products_by_other` | Crude oil: imports of crude oil and equivalent products by others, m3 (part of imports) | m3 | 429 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `imports_of_crude_oil_and_equivalent_products_by_refineries` | Crude oil: imports of crude oil and equivalent products by refineries, m3 (part of imports) | m3 | 1030 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `in_situ_crude_bitumen_production` | Crude oil: in-situ crude bitumen production, m3 (part of non-upgraded bitumen) | m3 | 254 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `industrial_consumption` | Natural gas: industrial consumption, m3 | m3 | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `industrial_consumption_customers` | Natural gas: industrial customers, count | count | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `industrial_deliveries_from_distribution_pipelines` | Natural gas: industrial deliveries from distribution pipelines, m3 | m3 | 1152 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `industrial_deliveries_from_distribution_pipelines_customers` | Natural gas: industrial customers served from distribution pipelines, count | count | 1152 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `industrial_deliveries_from_transmission_pipelines` | Natural gas: industrial deliveries from transmission pipelines, m3 | m3 | 896 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `industrial_deliveries_from_transmission_pipelines_customers` | Natural gas: industrial customers served from transmission pipelines, count | count | 896 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `injections_to_storage` | Natural gas: injections to storage, m3 | m3 | 768 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `input_to_canadian_refineries` | Crude oil: input to Canadian refineries, m3 | m3 | 730 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `inventory_change_storage` | Natural gas: inventory change in storage, m3 | m3 | 768 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `light_and_medium_crude_oil` | Crude oil: light and medium crude oil production, m3 (part of net field production) | m3 | 1129 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `light_and_medium_crude_oil_used_as_an_input_in_refineries` | Crude oil: light and medium crude oil used as an input in refineries, m3 | m3 | 714 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `marketable_production` | Natural gas: marketable production, m3 | m3 | 1260 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `metering_differences_line_losses_and_adjustments` | Natural gas: metering differences, line losses and adjustments, m3 | m3 | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `mined_crude_bitumen_production` | Crude oil: mined crude bitumen production, m3 (part of non-upgraded bitumen) | m3 | 254 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_field_production_of_crude_oil` | Crude oil: net field production of crude oil, m3 (part of crude oil production) | m3 | 1129 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_inventory_changes` | Crude oil: net inventory changes, m3 | m3 | 1401 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `non_upgraded_production_of_crude_bitumen` | Crude oil: non-upgraded production of crude bitumen, m3 (part of net field production) | m3 | 254 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `opening_inventory` | Crude oil: opening inventory, m3 | m3 | 1091 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `opening_inventory_fields_and_plants` | Crude oil: opening inventory at fields and plants, m3 | m3 | 1107 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `opening_inventory_refineries` | Crude oil: opening inventory at refineries, m3 | m3 | 746 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `opening_inventory_storage` | Natural gas: opening inventory in storage, m3 | m3 | 768 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `opening_inventory_transporters` | Crude oil: opening inventory held by transporters, m3 | m3 | 968 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `pentanes_plus` | Crude oil: pentanes plus production, m3 (part of equivalent products) | m3 | 381 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `pipeline_fuel` | Natural gas: pipeline fuel, m3 | m3 | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `receipts_from_other_provinces` | Natural gas: receipts from other provinces, m3 | m3 | 1024 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `residential_consumption` | Natural gas: residential consumption, m3 | m3 | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `residential_consumption_customers` | Natural gas: residential customers, count | count | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `storage_adjustments` | Natural gas: storage adjustments, m3 | m3 | 768 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `synthetic_crude_oil_production` | Crude oil: synthetic crude oil production, m3 (part of crude oil production) | m3 | 254 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `synthetic_crude_oil_used_as_an_input_in_refineries` | Crude oil: synthetic crude oil used as an input in refineries, m3 | m3 | 602 | 2016-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `total_deliveries_to_consumers` | Natural gas: total deliveries to consumers, m3 | m3 | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `total_deliveries_to_consumers_customers` | Natural gas: customers of total deliveries to consumers, count | count | 1280 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `total_exports` | Natural gas: total exports, m3 | m3 | 1024 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `total_imports` | Natural gas: total imports, m3 | m3 | 897 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `withdrawals_from_storage` | Natural gas: withdrawals from storage, m3 | m3 | 768 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `statcan_petroleum_products_monthly`

One area's value of one supply or disposition item for one petroleum product in one month, from Statistics Canada table 25-10-0081-01.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 112385.

- **Time:** ts_utc is the month's first day at 00:00:00Z (a month, not an instant); freq P1M.
- **Revisions:** A snapshot; each run asks the zip again and writes the whole table; vintage is the zip's Last-Modified time.
- **Source:** statcan:25-10-0081-01 Statistics Canada, Table 25-10-0081-01, Petroleum products by supply and disposition, monthly (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510008101)
- **Method note:** [`docs/methods/statcan_petroleum_products_monthly.md`](../methods/statcan_petroleum_products_monthly.md)
- **Cite as:** Statistics Canada. Table 25-10-0081-01, Petroleum products by supply and disposition, monthly. Via the Energy Research Warehouse (ERW), table `statcan_petroleum_products_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statcan_pp:<area>:<product>, the area ca or a province's or territory's postal code in lower case | none | text | for example statcan_pp:ab:asphalt, statcan_pp:ab:aviation_gasoline_blending_components, statcan_pp:ab:butane; 406 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-07-01T00:00:00Z; 91 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1222456.0 to 10421525.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | m3 | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: CA for Canada, CA-<province> for a province or territory | none | text | CA, CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-NT, CA-NU, CA-ON, CA-PE, CA-QC, CA-SK, CA-YT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 112385 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <area>: <item>: <product> as StatCan names them, not a pricing node | none | text | for example Alberta: Ending stocks: Asphalt, Alberta: Ending stocks: Aviation gasoline blending components, Alberta: Ending stocks: Distillate fuel oil; 1331 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statcan:25-10-0081-01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www150.statcan.gc.ca/n1/tbl/csv/25100081-eng.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T09:05:20Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The Last-Modified time of StatCan's zip | none | utc time | 2026-09-29T12:30:43Z | 0 |
| `x_product` | The petroleum product, StatCan's name (31 products) (the source's name: Products) | none | text | for example Asphalt, Aviation gasoline blending components, Butane; 31 distinct | 0 |
| `x_parent` | The product this one is part of, StatCan's name | none | text | Finished petroleum products, Hydrocarbon gas liquids, Natural gas liquids, Other liquids, Renewable fuels | 8570: One of the three top products (hydrocarbon gas liquids, other liquids, finished petroleum products) |
| `x_total` | yes where the product has parts in the table, never to be summed with them | none | text | yes | 95056: The product has no parts in the table |
| `x_vector` | StatCan's vector identifier of the series (the source's name: VECTOR) | none | text | for example v1251227408, v1251227409, v1251227410; 1331 distinct | 0 |
| `x_revised` | r where StatCan marks the figure revised; no row holds one (the source's name: SYMBOL) | none | empty | no cell holds a value | 112385: StatCan gives no symbol (every row now) |

Variables (10):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `adjustments` | Adjustments, m3 (Canada only) | m3 | 668 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `ending_stocks` | Ending stocks, m3 | m3 | 16200 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `exports` | Exports, m3 | m3 | 20408 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `field_production` | Field production, m3 | m3 | 1183 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `imports` | Imports, m3 | m3 | 24206 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `products_supplied` | Products supplied, m3 (Canada only) | m3 | 1238 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `refinery_inputs` | Refinery and blender net inputs, m3 (net, can be negative) | m3 | 6381 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `refinery_production` | Refinery and blender net production, m3 (net, can be negative) | m3 | 15430 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `renewable_production` | Renewable fuel plant net production, m3 | m3 | 463 | 2020-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `stock_change` | Stock change, m3 (positive for a build) | m3 | 26208 | 2019-01-01T00:00:00Z | 2026-07-01T00:00:00Z |

### `statcan_power_disposition_annual`

One area's value of one component of electricity supply and disposition (generation, trade, sales, losses) in one year, from Statistics Canada table 25-10-0021-01.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3909.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z (a year, not an instant); freq P1Y.
- **Revisions:** Every run that is not offline asks again and writes the whole table again; vintage is the zip's Last-Modified time.
- **Source:** statcan:25-10-0021-01 Statistics Canada, Table 25-10-0021-01, Electric power, electric utilities and industry, annual supply and disposition (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002101)
- **Method note:** [`docs/methods/statcan_power_disposition_annual.md`](../methods/statcan_power_disposition_annual.md)
- **Cite as:** Statistics Canada. Table 25-10-0021-01, Electric power, electric utilities and industry, annual supply and disposition. Via the Energy Research Warehouse (ERW), table `statcan_power_disposition_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statcan_pd:<area>, the area ca or a province's or territory's postal code in lower case | none | text | statcan_pd:ab, statcan_pd:bc, statcan_pd:ca, statcan_pd:mb, statcan_pd:nb, statcan_pd:nl, statcan_pd:ns, statcan_pd:nt, statcan_pd:nu, statcan_pd:on, statcan_pd:pe, statcan_pd:qc, statcan_pd:sk, statcan_pd:yt | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -8356860.0 to 649482181.0; 3528 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: CA for Canada, CA-<province> for a province or territory | none | text | CA, CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-NT, CA-NU, CA-ON, CA-PE, CA-QC, CA-SK, CA-YT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3909 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <area>: <component> as StatCan names them, not a pricing node | none | text | for example Alberta: Agriculture sales of electricity, Alberta: Electricity used by producers, Alberta: Exports of electricity to the United States, firm; 229 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statcan:25-10-0021-01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www150.statcan.gc.ca/n1/tbl/csv/25100021-eng.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T11:45:47Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The Last-Modified time of StatCan's zip | none | utc time | 2026-10-16T12:30:33Z | 0 |
| `x_component` | The component of supply and disposition, StatCan's name (the variable is its slug) (the source's name: Electric power, components) | none | text | Agriculture sales of electricity, Electricity used by producers, Exports of electricity to the United States, exchanged, Exports of electricity to the United States, firm, Exports of electricity to the United States, secondary, Imports of electricity from the United States, exchanged, Imports of electricity from the United States, purchased, Interprovincial deliveries of electricity, firm, Interprovincial deliveries of electricity, secondary, Interprovincial receipts of electricity, purchased, Mining and manufacturing sales of electricity, Other industries sales of electricity, Residential sales of electricity, Total electricity available for use within specific geographic border, Total exports of electricity to the United States, Total generation of electricity, Total imports of electricity from the United States, Total interprovincial deliveries of electricity, Total interprovincial receipts of electricity, Total sales of electricity to ultimate customers, Unallocated electricity | 0 |
| `x_vector` | StatCan's vector identifier of the series (the source's name: VECTOR) | none | text | for example v1014073248, v1014074049, v1079014831; 229 distinct | 0 |
| `x_revised` | r where StatCan marks the figure revised (the source's name: SYMBOL) | none | text | r | 3824: StatCan gives no revision mark |

Variables (21):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `agriculture_sales_of_electricity` | Agriculture sales of electricity, MWh | MWh | 231 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `electricity_used_by_producers` | Electricity used by producers, MWh | MWh | 294 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `exports_of_electricity_to_the_united_states_exchanged` | Exports of electricity to the United States, exchanged, MWh | MWh | 24 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `exports_of_electricity_to_the_united_states_firm` | Exports of electricity to the United States, firm, MWh | MWh | 70 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `exports_of_electricity_to_the_united_states_secondary` | Exports of electricity to the United States, secondary, MWh | MWh | 78 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `imports_of_electricity_from_the_united_states_exchanged` | Imports of electricity from the United States, exchanged, MWh | MWh | 22 | 2005-01-01T00:00:00Z | 2012-01-01T00:00:00Z |
| `imports_of_electricity_from_the_united_states_purchased` | Imports of electricity from the United States, purchased, MWh | MWh | 81 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `interprovincial_deliveries_of_electricity_firm` | Interprovincial deliveries of electricity, firm, MWh | MWh | 90 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `interprovincial_deliveries_of_electricity_secondary` | Interprovincial deliveries of electricity, secondary, MWh | MWh | 48 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `interprovincial_receipts_of_electricity_purchased` | Interprovincial receipts of electricity, purchased, MWh | MWh | 93 | 2005-01-01T00:00:00Z | 2013-01-01T00:00:00Z |
| `mining_and_manufacturing_sales_of_electricity` | Mining and manufacturing sales of electricity, MWh | MWh | 270 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `other_industries_sales_of_electricity` | Other industries sales of electricity, MWh | MWh | 294 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `residential_sales_of_electricity` | Residential sales of electricity, MWh | MWh | 294 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_electricity_available_for_use_within_specific_geographic_border` | Total electricity available for use within the area's border, MWh | MWh | 294 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_exports_of_electricity_to_the_united_states` | Total exports of electricity to the United States, MWh | MWh | 199 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_generation_of_electricity` | Total generation of electricity in the year, MWh | MWh | 294 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_imports_of_electricity_from_the_united_states` | Total imports of electricity from the United States, MWh | MWh | 199 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_interprovincial_deliveries_of_electricity` | Total interprovincial deliveries of electricity, MWh | MWh | 221 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_interprovincial_receipts_of_electricity` | Total interprovincial receipts of electricity, MWh | MWh | 225 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_sales_of_electricity_to_ultimate_customers` | Total sales of electricity to ultimate customers, MWh | MWh | 294 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `unallocated_electricity` | Unallocated electricity, MWh | MWh | 294 | 2005-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

