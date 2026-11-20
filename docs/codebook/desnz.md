# Codebook: desnz

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 17 public tables (1 entities, 16 series; tiers: 17 source); 0 documented in full.

- [`desnz_gb_regional_consumption_annual`](#desnz_gb_regional_consumption_annual): DESNZ, Subnational electricity consumption statistics: Great Britain's electricity consumption and meters by country and region, 2005 to 2024 (session 2693)
- [`desnz_gb_regional_gas_consumption_annual`](#desnz_gb_regional_gas_consumption_annual): DESNZ, Subnational gas consumption statistics: Great Britain's gas consumption and meters by country and region, weather corrected, 2005 to 2024 (session 2698)
- [`desnz_regional_renewable_capacity_annual`](#desnz_regional_renewable_capacity_annual): DESNZ, Regional Renewable Statistics: installed renewable capacity at year end by UK region and technology, 2003 to 2025 (session 2692)
- [`desnz_regional_renewables_annual`](#desnz_regional_renewables_annual): DESNZ, Regional Renewable Statistics: renewable electricity generation a year by UK region and technology, 2003 to 2025 (session 2684)
- [`desnz_uk_capacity_by_connection_annual`](#desnz_uk_capacity_by_connection_annual): DESNZ, Digest of UK Energy Statistics (DUKES) 2026, table 5.12: the UK's installed capacity at year end by connection (transmission or distribution) and fuel, 2011 to 2025, for Great Britain, Northern Ireland and the UK (session 2742)
- [`desnz_uk_co2_intensity_annual`](#desnz_uk_co2_intensity_annual): DESNZ, Digest of UK Energy Statistics (DUKES) 2026, table 5.14: the estimated CO2 intensity of the UK's electricity supplied, by fuel, 1996 to 2025 (session 2729)
- [`desnz_uk_derated_capacity_annual`](#desnz_uk_derated_capacity_annual): DESNZ, Digest of UK Energy Statistics (DUKES) 2026, table 5.7: the UK's de-rated generating capacity by kind of company and fuel, and its thermal stations by type, 1996 to 2025 (session 2734)
- [`desnz_uk_electricity_quarterly`](#desnz_uk_electricity_quarterly): UK Department for Energy Security and Net Zero (DESNZ), Energy Trends table 5.1, electricity generated and supplied by fuel, a quarter, 1998-01 to 2026-04 (session 2168)
- [`desnz_uk_fuel_used_generation_annual`](#desnz_uk_fuel_used_generation_annual): DESNZ, Digest of UK Energy Statistics (DUKES) 2026, table 5.3: the fuel used in UK electricity generation by kind of company and fuel, and the major power producers' by plant type, 1996 to 2025 (session 2748)
- [`desnz_uk_gas_quarterly`](#desnz_uk_gas_quarterly): UK Department for Energy Security and Net Zero (DESNZ), Energy Trends table 4.1, natural gas supply and consumption, a quarter, 1998-01 to 2026-04 (session 2226)
- [`desnz_uk_interconnector_flows_annual`](#desnz_uk_interconnector_flows_annual): DESNZ, Digest of UK Energy Statistics (DUKES) 2026, table 5.13: the UK's electricity imports, exports and net imports over each interconnector and their utilisation, 1998 to 2025, and the transfers between Scotland and England and Northern Ireland (session 2715)
- [`desnz_uk_mpp_capacity_countries_annual`](#desnz_uk_mpp_capacity_countries_annual): DESNZ, Digest of UK Energy Statistics (DUKES) 2026, table 5.8: the major power producers' de-rated capacity in England and Wales, Scotland and Northern Ireland by fuel and thermal plant type, and each country's share, 1999 to 2025 (session 2743)
- [`desnz_uk_nations_electricity_annual`](#desnz_uk_nations_electricity_annual): DESNZ, Electricity generation and supply in Scotland, Wales, Northern Ireland and England: generation by fuel and the supply balance for each UK nation, 2004 to 2025 (session 2678)
- [`desnz_uk_plant_loads_annual`](#desnz_uk_plant_loads_annual): DESNZ, Digest of UK Energy Statistics (DUKES) 2026, table 5.10: the UK's maximum load, plant load factors and thermal efficiency for the major power producers, 1996 to 2025 (session 2728)
- [`desnz_uk_power_stations`](#desnz_uk_power_stations): DESNZ, Digest of UK Energy Statistics (DUKES) 2026, table 5.11: the major power producers' power stations in the United Kingdom operational at 2026-05-31, one row a station (session 2714)
- [`desnz_uk_renewables_quarterly`](#desnz_uk_renewables_quarterly): UK Department for Energy Security and Net Zero (DESNZ), Energy Trends table 6.1, renewable electricity capacity and generation by technology, a quarter, 2010-01 to 2026-04 (session 2174)
- [`desnz_uk_storage_annual`](#desnz_uk_storage_annual): DESNZ, Digest of UK Energy Statistics (DUKES) 2026, table 5.16: the UK's electricity out of and into storage and its power capacity, by type, 1996 to 2025 (session 2720)

### `desnz_gb_regional_consumption_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2608.

- **Source:** desnz:subnational_electricity_consumption_2005_2024 Department for Energy Security and Net Zero, Subnational electricity consumption statistics, 2005 to 2024
- **Method note:** [`docs/methods/desnz_gb_regional_consumption_annual.md`](../methods/desnz_gb_regional_consumption_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Subnational electricity consumption statistics, 2005 to 2024 (countries and regions). Via the Energy Research Warehouse (ERW), table `desnz_gb_regional_consumption_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example desnz_sub:east_midlands:consumption_domestic, desnz_sub:east_midlands:consumption_domestic_e7, desnz_sub:east_midlands:consumption_domestic_standard; 190 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 4041.0 to 320314370.706; 2608 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | GB, GB-ENG, GB-ENG,GB-WLS, GB-SCT, GB-WLS | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 2608 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example East Midlands: Number of meters (thousands): All Domestic, East Midlands: Number of meters (thousands): All Non-Domestic, East Midlands: Number of meters (thousands): All meters; 246 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:subnational_electricity_consumption_2005_2024 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/69426e905431f4f94d7f0b5e/Subnational_electricity_consumption_statistics_2005-2024.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T13:03:48Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2025-12-17T08:49:20Z | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` |  | MWh | 1304 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `meters` |  | count | 1304 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `desnz_gb_regional_gas_consumption_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1966.

- **Source:** desnz:subnational_gas_consumption_2005_2024 Department for Energy Security and Net Zero, Subnational gas consumption statistics, 2005 to 2024 (weather corrected)
- **Method note:** [`docs/methods/desnz_gb_regional_gas_consumption_annual.md`](../methods/desnz_gb_regional_gas_consumption_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Subnational gas consumption statistics, 2005 to 2024 (countries and regions, weather corrected). Via the Energy Research Warehouse (ERW), table `desnz_gb_regional_gas_consumption_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example desnz_subgas:east_midlands:consumption_domestic, desnz_subgas:east_midlands:consumption_non_domestic, desnz_subgas:east_midlands:consumption_total; 130 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 17.0 to 667587368.386; 1965 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | GB, GB-ENG, GB-ENG,GB-WLS, GB-SCT, GB-WLS | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1966 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example East Midlands: Number of meters (thousands): All meters, East Midlands: Number of meters (thousands): Domestic, East Midlands: Number of meters (thousands): Non-Domestic; 130 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:subnational_gas_consumption_2005_2024 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/69f9bf208f3213f7384ecae6/Subnational_gas_consumption_statistics_2005-2024.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T13:14:17Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-05-05T09:57:52Z | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` |  | MWh | 903 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `meters` |  | count | 1063 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `desnz_regional_renewable_capacity_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3157.

- **Source:** desnz:regional_renewable_capacity_2003_2025 Department for Energy Security and Net Zero, Regional Renewable Statistics: Regional installed capacity MW 2003-2025
- **Method note:** [`docs/methods/desnz_regional_renewable_capacity_annual.md`](../methods/desnz_regional_renewable_capacity_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Regional Renewable Statistics: Regional installed capacity MW 2003-2025. Via the Energy Research Warehouse (ERW), table `desnz_regional_renewable_capacity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example desnz_rc:co_firing:biomass_waste, desnz_rc:co_firing:other_bioenergy, desnz_rc:co_firing:other_bioenergy_incl_sewage; 197 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2003-01-01T00:00:00Z, 2004-01-01T00:00:00Z, 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 65271.17; 2030 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | GB, GB-ENG, GB-NIR, GB-SCT, GB-WLS | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 3157 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Co-firing: Biomass and waste, Co-firing: Other bioenergy, Co-firing: Other bioenergy (incl Sewage gas; 197 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:regional_renewable_capacity_2003_2025 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6aba6ee6997a4b2950ccefec/Regional_installed_capacity_MW_2003-2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T12:56:48Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-09-28T13:43:02Z | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity` |  | MW | 3157 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_regional_renewables_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3002.

- **Source:** desnz:regional_renewable_generation_2003_2025 Department for Energy Security and Net Zero, Regional Renewable Statistics: Regional generation GWh 2003-2025
- **Method note:** [`docs/methods/desnz_regional_renewables_annual.md`](../methods/desnz_regional_renewables_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Regional Renewable Statistics: Regional generation GWh 2003-2025. Via the Energy Research Warehouse (ERW), table `desnz_regional_renewables_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example desnz_re:east_midlands:anaerobic_digestion, desnz_re:east_midlands:biomass_waste, desnz_re:east_midlands:hydro; 194 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2003-01-01T00:00:00Z, 2004-01-01T00:00:00Z, 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 152909011.524; 2472 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | GB, GB-ENG, GB-NIR, GB-SCT, GB-WLS | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 3002 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example East Midlands: AD, East Midlands: Biomass and waste, East Midlands: Hydro; 194 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:regional_renewable_generation_2003_2025 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6aba6ef6fe72ed1e2b02f152/Regional_generation_GWh_2003-2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T12:00:30Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-09-28T13:43:18Z | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `generation` |  | MWh | 3002 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_capacity_by_connection_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1245.

- **Source:** desnz:dukes_5_12_capacity_by_connection Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.12, Plant installed capacity, by connection
- **Method note:** [`docs/methods/desnz_uk_capacity_by_connection_annual.md`](../methods/desnz_uk_capacity_by_connection_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.12, Plant installed capacity, by connection. Via the Energy Research Warehouse (ERW), table `desnz_uk_capacity_by_connection_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example desnz_conn:gb:distribution:bioenergy, desnz_conn:gb:distribution:ccgt_gas, desnz_conn:gb:distribution:coal; 83 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 111103.434; 653 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | GB, GB-NIR | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1245 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example All: Bioenergy, All: CCGT gas, All: Coal; 43 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_12_capacity_by_connection | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a3668862aaf18d9c629ed/DUKES_5.12.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T20:54:18Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-07-29T17:20:40Z | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `installed_capacity` |  | MW | 1245 | 2011-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_co2_intensity_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 119.

- **Source:** desnz:dukes_5_14_co2_intensity Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.14, Estimated carbon dioxide intensity of electricity supplied
- **Method note:** [`docs/methods/desnz_uk_co2_intensity_annual.md`](../methods/desnz_uk_co2_intensity_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.14, Carbon dioxide intensity of electricity supplied. Via the Energy Research Warehouse (ERW), table `desnz_uk_co2_intensity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | desnz_ci:all_fuels, desnz_ci:coal, desnz_ci:gas, desnz_ci:non_renewable | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1996-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 30 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 147.25 to 1020.99; 119 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kgCO2/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | GB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 119 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | All fuels (including nuclear and renewables), All non renewable fuels, Coal, Gas | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_14_co2_intensity | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a3684bf4a7aca8f8976c4/DUKES_5.14.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T19:33:21Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-07-29T17:21:08Z | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `co2_intensity` |  | kgCO2/MWh | 119 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_derated_capacity_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1680.

- **Source:** desnz:dukes_5_7_plant_capacity Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.7, Plant capacity: United Kingdom
- **Method note:** [`docs/methods/desnz_uk_derated_capacity_annual.md`](../methods/desnz_uk_derated_capacity_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.7, Plant capacity: United Kingdom. Via the Energy Research Warehouse (ERW), table `desnz_uk_derated_capacity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example desnz_cap:all:bioenergy_and_waste, desnz_cap:all:ccgt_stations, desnz_cap:all:coal_fired; 50 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1996-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 30 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 90393.3079; 1158 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | GB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1680 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example All generating companies: Bioenergy and waste, All generating companies: CCGT stations, All generating companies: Coal fired; 53 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_7_plant_capacity | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a3622cceb23e8678976bf/DUKES_5.7.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T19:40:40Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-07-29T17:19:30Z | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `derated_capacity` |  | MW | 1200 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `thermal_capacity` |  | MW | 480 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_electricity_quarterly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 7862.

- **Source:** desnz:energy_trends_5_1 UK Department for Energy Security and Net Zero, Energy Trends section 5: electricity, table ET 5.1 (https://www.gov.uk/government/statistics/electricity-section-5-energy-trends)
- **Method note:** [`docs/methods/desnz_uk_electricity_quarterly.md`](../methods/desnz_uk_electricity_quarterly.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Energy Trends section 5: electricity, table ET 5.1 (fuel used in generation and electricity supplied). Via the Energy Research Warehouse (ERW), table `desnz_uk_electricity_quarterly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example desnz_et51:all_generating_companies:battery_storage, desnz_et51:all_generating_companies:bioenergy, desnz_et51:all_generating_companies:coal; 43 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1998-01-01T00:00:00Z to 2026-04-01T00:00:00Z; 114 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -4853100.0 to 112158100.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P3M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | GB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 7862 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example All generating companies, Battery storage, All generating companies, Bioenergy, All generating companies, Coal; 45 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:energy_trends_5_1 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6aba6dd9a9c3d267bcccefb0/ET_5.1_SEP_26.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T00:35:36Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-09-28T13:38:33Z | 0 |
| `x_generator_type` | not yet written |  | text | All generating companies, Major power producers, Other generators | 0 |
| `x_fuel` | not yet written |  | text | Battery storage, Bioenergy, Coal, Gas, Hydro (natural flow), Net imports, Nuclear, Offshore wind, Oil, Onshore wind, Other fuels, Pumped storage, Pumped storage (net supply), Shoreline wave / tidal, Solar, Total all generating companies, Total major power producers, Total other generators, Total wind | 0 |
| `x_provisional` | not yet written |  | text | no, yes | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `generated` |  | MWh | 3829 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `supplied` |  | MWh | 4033 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |

### `desnz_uk_fuel_used_generation_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 900.

- **Source:** desnz:dukes_5_3_fuel_used Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.3, Fuel used in generation
- **Method note:** [`docs/methods/desnz_uk_fuel_used_generation_annual.md`](../methods/desnz_uk_fuel_used_generation_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.3, Fuel used in generation. Via the Energy Research Warehouse (ERW), table `desnz_uk_fuel_used_generation_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example desnz_fuel:all:coal, desnz_fuel:all:gas, desnz_fuel:all:hydro_natural_flow; 30 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1996-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 30 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 1012550831.0; 749 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | GB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 900 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example All generating companies: Coal, All generating companies: Gas, All generating companies: Hydro (natural flow); 30 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_3_fuel_used | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a35ef0ddb7e4831c629f0/DUKES_5.3.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T21:04:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-07-29T17:18:39Z | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `fuel_used` |  | MWh | 840 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `fuel_used_by_plant` |  | MWh | 60 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_gas_quarterly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2394.

- **Source:** desnz:energy_trends_4_1 DESNZ, Energy Trends section 4 (gas) (https://www.gov.uk/government/statistics/gas-section-4-energy-trends)
- **Method note:** [`docs/methods/desnz_uk_gas_quarterly.md`](../methods/desnz_uk_gas_quarterly.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Energy Trends section 4: gas (table ET 4.1, natural gas supply and consumption). Via the Energy Research Warehouse (ERW), table `desnz_uk_gas_quarterly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | desnz_et41:uk | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1998-01-01T00:00:00Z to 2026-04-01T00:00:00Z; 114 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -24960040.0 to 376669000.0; 2263 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P3M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | GB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 2394 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | Domestic, Electricity generation, Energy industry use, Exports [note 2], Final Consumption, Heat generation [note 7], Imports [note 2], Imports of Liquefied Natural Gas [note 3], Indigenous production, Iron & steel, Losses [note 8], Non energy use, Other final users, Other industries, Statistical difference, Stock change [note 4] [note 5], Total demand, Total supply, Transfers [note 6], Transformation, Transport | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:energy_trends_4_1 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6aba6b15fceb6fb3a65012ba/ET_4.1_SEP_26.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T02:17:00Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-09-28T13:26:45Z | 0 |
| `x_provisional` | not yet written |  | text | no, yes | 0 |

Variables (21):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `domestic` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `electricity_generation` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `energy_industry_use` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `exports` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `final_consumption` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `heat_generation` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `imports` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `imports_of_liquefied_natural_gas` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `indigenous_production` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `iron_steel` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `losses` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `non_energy_use` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `other_final_users` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `other_industries` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `statistical_difference` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `stock_change` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `total_demand` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `total_supply` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `transfers` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `transformation` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `transport` |  | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |

### `desnz_uk_interconnector_flows_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 642.

- **Source:** desnz:dukes_5_13_interconnectors Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.13, Net imports and utilisation of interconnectors
- **Method note:** [`docs/methods/desnz_uk_interconnector_flows_annual.md`](../methods/desnz_uk_interconnector_flows_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.13, Net imports and utilisation of interconnectors. Via the Energy Research Warehouse (ERW), table `desnz_uk_interconnector_flows_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | desnz_ic:belgium, desnz_ic:denmark, desnz_ic:france, desnz_ic:ireland_northern_ireland, desnz_ic:ireland_wales, desnz_ic:netherlands, desnz_ic:norway, desnz_ic:scotland_england, desnz_ic:scotland_northern_ireland, desnz_ic:uk_total | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1998-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 28 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -9983570.5 to 43929487.9; 621 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | GB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 642 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Exports (Northern Ireland to Ireland), Exports (UK to Belgium), Exports (UK to Denmark); 37 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_13_interconnectors | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a3675bf4a7aca8f8976c3/DUKES_5.13.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T17:13:14Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-07-29T17:20:53Z | 0 |

Variables (8):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `exports` |  | MWh | 130 | 1998-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `imports` |  | MWh | 130 | 1998-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `net_imports` |  | MWh | 130 | 1998-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `net_transfers` |  | MWh | 50 | 2000-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `transfers_to_england` |  | MWh | 26 | 2000-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `transfers_to_northern_ireland` |  | MWh | 24 | 2002-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `transfers_to_scotland` |  | MWh | 50 | 2000-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `utilisation` |  | ratio | 102 | 1998-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_mpp_capacity_countries_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1539.

- **Source:** desnz:dukes_5_8_mpp_capacity_countries Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.8, Major power producers plant capacity, England and Wales, Scotland, and Northern Ireland
- **Method note:** [`docs/methods/desnz_uk_mpp_capacity_countries_annual.md`](../methods/desnz_uk_mpp_capacity_countries_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.8, Major power producers plant capacity by country. Via the Energy Research Warehouse (ERW), table `desnz_uk_mpp_capacity_countries_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example desnz_mppr:england_wales:bioenergy_and_waste, desnz_mppr:england_wales:ccgt_stations, desnz_mppr:england_wales:coal_fired; 51 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1999-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 27 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 70668.5042; 651 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | GB-ENG,GB-WLS, GB-NIR, GB-SCT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1539 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example England and Wales: Bioenergy and waste, England and Wales: CCGT stations, England and Wales: Coal fired; 54 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_8_mpp_capacity_countries | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a3631862aaf18d9c629ec/DUKES_5.8.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T20:58:43Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-07-29T17:19:45Z | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity_share` |  | ratio | 81 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `derated_capacity` |  | MW | 972 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `thermal_capacity` |  | MW | 486 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_nations_electricity_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 4167.

- **Source:** desnz:electricity_generation_supply_nations_2026 Department for Energy Security and Net Zero, Electricity generation and supply in Scotland, Wales, Northern Ireland and England, 2004 to 2025: data tables (Energy Trends, September 2026)
- **Method note:** [`docs/methods/desnz_uk_nations_electricity_annual.md`](../methods/desnz_uk_nations_electricity_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Electricity generation and supply in Scotland, Wales, Northern Ireland and England, 2004 to 2025: data tables (Energy Trends, September 2026). Via the Energy Research Warehouse (ERW), table `desnz_uk_nations_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example desnz:england:consumption_autogenerators, desnz:england:consumption_public, desnz:england:consumption_total; 200 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2004-01-01T00:00:00Z, 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -38480068.0 to 398359717.2; 3517 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | GB, GB-ENG, GB-NIR, GB-SCT, GB-WLS | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 4167 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Consumption by autogenerators, Consumption from public supply, Distribution losses and theft; 40 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:electricity_generation_supply_nations_2026 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6aba6c4afe72ed1e2b02f14b/Regional_Electricity_Generation_and_Supply_Timeseries_2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T11:46:03Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-09-28T13:31:54Z | 0 |

Variables (9):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` |  | MWh | 330 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `generation` |  | MWh | 2517 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `losses` |  | MWh | 220 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `net_supply` |  | MWh | 220 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `net_transfers` |  | MWh | 330 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `own_use` |  | MWh | 220 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `sales` |  | MWh | 110 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `statistical_difference` |  | MWh | 110 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `transfers` |  | MWh | 110 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_plant_loads_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 425.

- **Source:** desnz:dukes_5_10_plant_loads Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.10, Plant loads, demand and efficiency of major power producers
- **Method note:** [`docs/methods/desnz_uk_plant_loads_annual.md`](../methods/desnz_uk_plant_loads_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.10, Plant loads, demand and efficiency. Via the Energy Research Warehouse (ERW), table `desnz_uk_plant_loads_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | desnz_pl:all_plant, desnz_pl:ccgt, desnz_pl:coal, desnz_pl:conventional_thermal, desnz_pl:england_wales, desnz_pl:great_britain, desnz_pl:northern_ireland, desnz_pl:nuclear, desnz_pl:pumped_storage, desnz_pl:scotland, desnz_pl:uk | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1996-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 30 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 61717.0; 403 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | GB, GB-NIR, GB-SCT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 425 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | 5.10.B: All plant, 5.10.B: Combined cycle gas turbine stations, 5.10.B: Conventional thermal and other stations, 5.10.B: Nuclear stations, 5.10.B: Pumped storage hydro, 5.10.B: System load factor, 5.10.B: of which coal-fired stations, 5.10.C: Coal fired stations, 5.10.C: Combined cycle gas turbine stations, 5.10.C: Nuclear stations, Maximum demand as a percentage of major power producers' capacity UK, Simultaneous maximum load met, MW England and Wales, Simultaneous maximum load met, MW Great Britain, Simultaneous maximum load met, MW Northern Ireland, Simultaneous maximum load met, MW Scotland, Simultaneous maximum load met, MW Total | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_10_plant_loads | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a364b0ddb7e4831c629f2/DUKES_5.10.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T19:27:58Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-07-29T17:20:11Z | 0 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `load_factor` |  | pct | 179 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `max_demand_share_of_capacity` |  | pct | 30 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `max_load` |  | MW | 96 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `system_load_factor` |  | pct | 30 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `thermal_efficiency` |  | pct | 90 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_power_stations`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 1364.

- **Source:** desnz:dukes_5_11_power_stations Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.11, Power stations in the United Kingdom
- **Method note:** [`docs/methods/desnz_uk_power_stations.md`](../methods/desnz_uk_power_stations.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.11, Power stations in the United Kingdom. Via the Energy Research Warehouse (ERW), table `desnz_uk_power_stations`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example dukes:BIO-000108, dukes:BIO-000134, dukes:BIO-000137; 1364 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | plant | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 30Acres, A'Chruach, AOE; 1347 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | GB-ENG, GB-NIR, GB-SCT, GB-WLS | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 50.046506 to 60.339325; 1302 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -8.005005 to 2.249319; 1302 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | 0.05 to 2580.0; 901 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | operating | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | date | 2026-05-31 | 0 |
| `operator` | The operator or owner, as the publisher writes it | none | text | for example Anesco, Atmosclear, BayWa R.E; 61 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_11_power_stations | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a365b0ddb7e4831c629f3/DUKES_5.11.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T17:09:21Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-07-29T17:20:27Z | 0 |
| `technology` | not yet written |  | text | Bioenergy, Fossil Fuel, Hydro, Nuclear, Pumped Hydro, Solar, Wind | 0 |
| `type` | not yet written |  | text | AGR, Bioenergy, CCGT, Conventional steam, Large Hydro, Offshore, Onshore, PV, PWR, Pumped hydro, Single cycle, Small Hydro | 0 |
| `chp` | not yet written |  | text | No, Yes | 0 |
| `primary_fuel` | not yet written |  | text | Biomass, Diesel/Gas Oil, Hydro, MSW, Natural Gas, Nuclear, Pumped hydro, Solar, Wind | 0 |
| `secondary_fuel` | not yet written |  | text | Gas, Oil | 1360 |
| `grid_connection_type` | not yet written |  | text | HV, LV | 0 |
| `country` | not yet written |  | text | England, Northern Ireland, Scotland, Wales | 0 |
| `region` | not yet written |  | text | East Midlands, East of England, London, North East, North West, North west, Northern Ireland, Scotland, South East, South West, Wales, West Midlands, Yorkshire and the Humber | 0 |
| `postcode` | not yet written |  | text | for example AB39 3TE, AB39 3XZ, AB393QH; 977 distinct | 297 |
| `os_reference` | not yet written |  | text | for example CF828FU, EX144RD, EX169QH; 654 distinct | 673 |
| `x_coordinate` | not yet written |  | number | 10820.0 to 690118.0; 1303 distinct | 0 |
| `y_coordinate` | not yet written |  | number | 21200.0 to 1161960.0; 1302 distinct | 0 |
| `year_commissioned` | not yet written |  | integer | 1906 to 2026; 73 distinct | 0 |
| `desnz_site_code` | not yet written |  | text | for example BIO-000108, BIO-000134, BIO-000137; 1364 distinct | 0 |

### `desnz_uk_renewables_quarterly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1982.

- **Source:** desnz:energy_trends_6_1 UK Department for Energy Security and Net Zero, Energy Trends section 6: renewables, table ET 6.1 (https://www.gov.uk/government/statistics/energy-trends-section-6-renewables)
- **Method note:** [`docs/methods/desnz_uk_renewables_quarterly.md`](../methods/desnz_uk_renewables_quarterly.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Energy Trends section 6: renewables, table ET 6.1 (renewable electricity capacity and generation). Via the Energy Research Warehouse (ERW), table `desnz_uk_renewables_quarterly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | desnz_et61:anaerobic_digestion, desnz_et61:animal_biomass_non_ad, desnz_et61:co_firing, desnz_et61:co_firing_with_fossil_fuels, desnz_et61:energy_from_waste, desnz_et61:hydro, desnz_et61:landfill_gas, desnz_et61:large_scale_hydro, desnz_et61:liquid_biofuels, desnz_et61:non_biodegradable_wastes, desnz_et61:offshore_wind, desnz_et61:offshore_wind_floating, desnz_et61:offshore_wind_seabed, desnz_et61:onshore_wind, desnz_et61:plant_biomass, desnz_et61:sewage_sludge_digestion, desnz_et61:shoreline_wave_tidal, desnz_et61:small_scale_hydro, desnz_et61:solar_photovoltaics, desnz_et61:total | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z to 2026-04-01T00:00:00Z; 66 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 44054300.0; 1381 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P3M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | GB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1982 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | Anaerobic digestion, Animal Biomass (non-AD), Co-firing, Co-firing with fossil fuels, Energy from waste, Hydro, Landfill gas, Large scale hydro, Liquid biofuels, Non-biodegradable wastes, Offshore wind, Offshore wind - floating, Offshore wind - seabed, Onshore wind, Plant biomass, Sewage sludge digestion, Shoreline wave / tidal, Small scale hydro, Solar photovoltaics, TOTAL | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:energy_trends_6_1 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6aba724dfceb6fb3a65012d2/ET_6.1_SEP_26.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T00:55:17Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-09-28T13:57:33Z | 0 |
| `x_technology` | not yet written |  | text | Anaerobic digestion, Animal Biomass (non-AD), Co-firing, Co-firing with fossil fuels, Energy from waste, Hydro, Landfill gas, Large scale hydro, Liquid biofuels, Non-biodegradable wastes, Offshore wind, Offshore wind - floating, Offshore wind - seabed, Onshore wind, Plant biomass, Sewage sludge digestion, Shoreline wave / tidal, Small scale hydro, Solar photovoltaics, TOTAL | 0 |
| `x_provisional` | not yet written |  | text | no | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity` |  | MW | 1024 | 2010-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `generated` |  | MWh | 958 | 2010-01-01T00:00:00Z | 2026-04-01T00:00:00Z |

### `desnz_uk_storage_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 360.

- **Source:** desnz:dukes_5_16_energy_storage Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.16, Energy storage input electricity, output electricity, and capacity overview
- **Method note:** [`docs/methods/desnz_uk_storage_annual.md`](../methods/desnz_uk_storage_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.16, Energy storage overview. Via the Energy Research Warehouse (ERW), table `desnz_uk_storage_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | desnz_st:battery_grid_scale, desnz_st:other_storage, desnz_st:pumped_storage, desnz_st:total | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1996-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 30 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 5371305.0; 118 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | GB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 360 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | Table 5.16.: Battery storage - grid scale, Table 5.16.: Other energy storage, Table 5.16.: Pumped storage, Table 5.16.: Total | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_16_energy_storage | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a36a0bf4a7aca8f8976c6/DUKES_5.16.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T17:17:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-07-29T17:21:36Z | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `input` |  | MWh | 120 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `output` |  | MWh | 120 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `power_capacity` |  | MW | 120 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

