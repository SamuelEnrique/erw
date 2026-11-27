# Codebook: desnz

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 17 public tables (1 entities, 16 series; tiers: 17 source); 17 documented in full.

- [`desnz_gb_regional_consumption_annual`](#desnz_gb_regional_consumption_annual): One Great Britain country's or region's electricity consumption or number of meters, for one kind of customer (domestic, non-domestic, total and Economy 7 splits), in one year, 2005 to 2024.
- [`desnz_gb_regional_gas_consumption_annual`](#desnz_gb_regional_gas_consumption_annual): One Great Britain country's or region's weather-corrected gas consumption or number of consuming meters, for one kind of customer, in one gas year, 2005 to 2024.
- [`desnz_regional_renewable_capacity_annual`](#desnz_regional_renewable_capacity_annual): One UK region's installed renewable electricity capacity of one technology at the end of one year, 2003 to 2025.
- [`desnz_regional_renewables_annual`](#desnz_regional_renewables_annual): One UK region's renewable electricity generation from one technology in one year, 2003 to 2025.
- [`desnz_uk_capacity_by_connection_annual`](#desnz_uk_capacity_by_connection_annual): One area's (Great Britain, Northern Ireland or the UK) installed generating capacity of one fuel, connected to the transmission or the distribution network or both, at the end of one year, 2011 to 2025 (DUKES table 5.12).
- [`desnz_uk_co2_intensity_annual`](#desnz_uk_co2_intensity_annual): The estimated carbon dioxide intensity of the UK's electricity supplied from one fuel group (coal, gas, all non-renewable fuels, all fuels) in one year, 1996 to 2025 (DUKES table 5.14).
- [`desnz_uk_derated_capacity_annual`](#desnz_uk_derated_capacity_annual): One kind of company's (major power producers, other generators, or all) de-rated generating capacity of one fuel or thermal station type in one year, 1996 to 2025 (DUKES table 5.7).
- [`desnz_uk_electricity_quarterly`](#desnz_uk_electricity_quarterly): The UK's electricity generated or supplied by one kind of generator (major power producers, other generators, all) from one fuel in one quarter, 1998 to 2026 (Energy Trends table 5.1).
- [`desnz_uk_fuel_used_generation_annual`](#desnz_uk_fuel_used_generation_annual): The fuel one group of generating companies used for UK electricity generation, by fuel, or the major power producers' by plant type, in one year, 1996 to 2025 (DUKES table 5.3).
- [`desnz_uk_gas_quarterly`](#desnz_uk_gas_quarterly): One line of the UK's natural gas balance (supply, demand and the consuming sectors) in one quarter, 1998 to 2026 (Energy Trends table 4.1).
- [`desnz_uk_interconnector_flows_annual`](#desnz_uk_interconnector_flows_annual): The UK's electricity imports, exports, net imports or utilisation over one interconnector border in one year, or the transfers between Scotland and England or Northern Ireland, 1998 to 2025 (DUKES table 5.13).
- [`desnz_uk_mpp_capacity_countries_annual`](#desnz_uk_mpp_capacity_countries_annual): The major power producers' de-rated capacity of one fuel or thermal plant type in England and Wales, Scotland or Northern Ireland, or the country's share of their capacity, in one year, 1999 to 2025 (DUKES table 5.8).
- [`desnz_uk_nations_electricity_annual`](#desnz_uk_nations_electricity_annual): One item of the electricity generation by fuel or the supply balance of the UK or one of its nations (England, Scotland, Wales, Northern Ireland) in one year, 2004 to 2025.
- [`desnz_uk_plant_loads_annual`](#desnz_uk_plant_loads_annual): One of the major power producers' load, load factor or efficiency figures for the UK, one of its areas or one plant type in one year, 1996 to 2025 (DUKES table 5.10).
- [`desnz_uk_power_stations`](#desnz_uk_power_stations): One of the major power producers' power stations in the United Kingdom operational at the end of May 2026, as DUKES table 5.11 lists it.
- [`desnz_uk_renewables_quarterly`](#desnz_uk_renewables_quarterly): The UK's cumulative installed renewable capacity or renewable electricity generated for one technology in one quarter, 2010 to 2026 (Energy Trends table 6.1).
- [`desnz_uk_storage_annual`](#desnz_uk_storage_annual): The UK's electricity out of or into storage, or storage power capacity, for one storage type in one year, 1996 to 2025 (DUKES table 5.16).

### `desnz_gb_regional_consumption_annual`

One Great Britain country's or region's electricity consumption or number of meters, for one kind of customer (domestic, non-domestic, total and Economy 7 splits), in one year, 2005 to 2024.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2608.

- **Time:** ts_utc is the year's first day at 00:00:00Z (a year, not an instant); freq P1Y.
- **Revisions:** Rewritten whole by each run (a snapshot of DESNZ's latest workbook, which DESNZ republishes with each new year); vintage is the workbook's last-modified time.
- **Source:** desnz:subnational_electricity_consumption_2005_2024 Department for Energy Security and Net Zero, Subnational electricity consumption statistics, 2005 to 2024
- **Method note:** [`docs/methods/desnz_gb_regional_consumption_annual.md`](../methods/desnz_gb_regional_consumption_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Subnational electricity consumption statistics, 2005 to 2024 (countries and regions). Via the Energy Research Warehouse (ERW), table `desnz_gb_regional_consumption_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: desnz_sub:<area>:<item>; from 2015 Great Britain, England and Wales and Scotland carry _inc_unallocated (their rows include consumption not placed in a local authority) | none | text | for example desnz_sub:east_midlands:consumption_domestic, desnz_sub:east_midlands:consumption_domestic_e7, desnz_sub:east_midlands:consumption_domestic_standard; 190 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 4041.0 to 320314370.706; 2608 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: GB, GB-ENG (England and its regions), GB-WLS, GB-SCT, or GB-ENG,GB-WLS for England and Wales | none | text | GB, GB-ENG, GB-ENG,GB-WLS, GB-SCT, GB-WLS | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2608 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The area and the workbook's column heading, not a pricing node | none | text | for example East Midlands: Number of meters (thousands): All Domestic, East Midlands: Number of meters (thousands): All Non-Domestic, East Midlands: Number of meters (thousands): All meters; 246 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:subnational_electricity_consumption_2005_2024 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/69426e905431f4f94d7f0b5e/Subnational_electricity_consumption_statistics_2005-2024.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T13:03:48Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time | none | utc time | 2025-12-17T08:49:20Z | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` | Electricity consumption in the year, MWh (the workbook's GWh times 1,000) | MWh | 1304 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `meters` | Number of electricity meters, count (the workbook's thousands times 1,000) | count | 1304 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `desnz_gb_regional_gas_consumption_annual`

One Great Britain country's or region's weather-corrected gas consumption or number of consuming meters, for one kind of customer, in one gas year, 2005 to 2024.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1966.

- **Time:** ts_utc is the first day of the calendar year DESNZ labels the gas year with, at 00:00:00Z; the gas year itself runs October to September to 2015, then mid-year to mid-year (mid-May to mid-May from 2018), as DESNZ's cover sheet states.
- **Revisions:** Rewritten whole by each run (a snapshot of DESNZ's latest workbook; DESNZ revises the years from 2015 each year); vintage is the workbook's last-modified time.
- **Source:** desnz:subnational_gas_consumption_2005_2024 Department for Energy Security and Net Zero, Subnational gas consumption statistics, 2005 to 2024 (weather corrected)
- **Method note:** [`docs/methods/desnz_gb_regional_gas_consumption_annual.md`](../methods/desnz_gb_regional_gas_consumption_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Subnational gas consumption statistics, 2005 to 2024 (countries and regions, weather corrected). Via the Energy Research Warehouse (ERW), table `desnz_gb_regional_gas_consumption_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: desnz_subgas:<area>:<item>; from 2015 Great Britain, England and Wales and Scotland include the unallocated consumption | none | text | for example desnz_subgas:east_midlands:consumption_domestic, desnz_subgas:east_midlands:consumption_non_domestic, desnz_subgas:east_midlands:consumption_total; 130 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 17.0 to 667587368.386; 1965 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: GB, GB-ENG (England and its regions), GB-WLS, GB-SCT, or GB-ENG,GB-WLS for England and Wales | none | text | GB, GB-ENG, GB-ENG,GB-WLS, GB-SCT, GB-WLS | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1966 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The area and the workbook's column heading, not a pricing node | none | text | for example East Midlands: Number of meters (thousands): All meters, East Midlands: Number of meters (thousands): Domestic, East Midlands: Number of meters (thousands): Non-Domestic; 130 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:subnational_gas_consumption_2005_2024 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/69f9bf208f3213f7384ecae6/Subnational_gas_consumption_statistics_2005-2024.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T13:14:17Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time | none | utc time | 2026-05-05T09:57:52Z | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` | Gas consumption in the gas year, weather corrected, MWh (the workbook's GWh times 1,000) | MWh | 903 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `meters` | Number of consuming gas meters, count (the workbook's thousands times 1,000) | count | 1063 | 2005-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `desnz_regional_renewable_capacity_annual`

One UK region's installed renewable electricity capacity of one technology at the end of one year, 2003 to 2025.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3157.

- **Time:** ts_utc is the year's first day at 00:00:00Z; the capacity is as at 31 December of that year; freq P1Y.
- **Revisions:** Rewritten whole by each run (DESNZ republishes the whole series each year); vintage is the workbook's last-modified time.
- **Source:** desnz:regional_renewable_capacity_2003_2025 Department for Energy Security and Net Zero, Regional Renewable Statistics: Regional installed capacity MW 2003-2025
- **Method note:** [`docs/methods/desnz_regional_renewable_capacity_annual.md`](../methods/desnz_regional_renewable_capacity_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Regional Renewable Statistics: Regional installed capacity MW 2003-2025. Via the Energy Research Warehouse (ERW), table `desnz_regional_renewable_capacity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: desnz_rc:<region>:<technology> | none | text | for example desnz_rc:co_firing:biomass_waste, desnz_rc:co_firing:other_bioenergy, desnz_rc:co_firing:other_bioenergy_incl_sewage; 197 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2003-01-01T00:00:00Z, 2004-01-01T00:00:00Z, 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 65271.17; 2030 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: GB for the UK and the other sites, GB-SCT, GB-WLS, GB-NIR, or GB-ENG for England and its regions | none | text | GB, GB-ENG, GB-NIR, GB-SCT, GB-WLS | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3157 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The region and the workbook's column, not a pricing node | none | text | for example Co-firing: Biomass and waste, Co-firing: Other bioenergy, Co-firing: Other bioenergy (incl Sewage gas; 197 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:regional_renewable_capacity_2003_2025 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6aba6ee6997a4b2950ccefec/Regional_installed_capacity_MW_2003-2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T12:56:48Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time | none | utc time | 2026-09-28T13:43:02Z | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity` | Installed renewable capacity at 31 December, MW | MW | 3157 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_regional_renewables_annual`

One UK region's renewable electricity generation from one technology in one year, 2003 to 2025.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3002.

- **Time:** ts_utc is the year's first day at 00:00:00Z (a year, not an instant); freq P1Y.
- **Revisions:** Rewritten whole by each run (DESNZ republishes the whole series each year); vintage is the workbook's last-modified time.
- **Source:** desnz:regional_renewable_generation_2003_2025 Department for Energy Security and Net Zero, Regional Renewable Statistics: Regional generation GWh 2003-2025
- **Method note:** [`docs/methods/desnz_regional_renewables_annual.md`](../methods/desnz_regional_renewables_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Regional Renewable Statistics: Regional generation GWh 2003-2025. Via the Energy Research Warehouse (ERW), table `desnz_regional_renewables_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: desnz_re:<region>:<technology> | none | text | for example desnz_re:east_midlands:anaerobic_digestion, desnz_re:east_midlands:biomass_waste, desnz_re:east_midlands:hydro; 194 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2003-01-01T00:00:00Z, 2004-01-01T00:00:00Z, 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 152909011.524; 2472 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: GB for the UK and the other sites, GB-SCT, GB-WLS, GB-NIR, or GB-ENG for England and its regions | none | text | GB, GB-ENG, GB-NIR, GB-SCT, GB-WLS | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3002 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The region and the workbook's column, not a pricing node | none | text | for example East Midlands: AD, East Midlands: Biomass and waste, East Midlands: Hydro; 194 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:regional_renewable_generation_2003_2025 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6aba6ef6fe72ed1e2b02f152/Regional_generation_GWh_2003-2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T12:00:30Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time | none | utc time | 2026-09-28T13:43:18Z | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `generation` | Renewable electricity generated in the year, MWh (the workbook's GWh times 1,000) | MWh | 3002 | 2003-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_capacity_by_connection_annual`

One area's (Great Britain, Northern Ireland or the UK) installed generating capacity of one fuel, connected to the transmission or the distribution network or both, at the end of one year, 2011 to 2025 (DUKES table 5.12).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1245.

- **Time:** ts_utc is the year's first day at 00:00:00Z; the capacity is as at 31 December of that year; freq P1Y.
- **Revisions:** Rewritten whole by each run (a snapshot of the DUKES edition read, here 2026); vintage is the workbook's last-modified time.
- **Source:** desnz:dukes_5_12_capacity_by_connection Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.12, Plant installed capacity, by connection
- **Method note:** [`docs/methods/desnz_uk_capacity_by_connection_annual.md`](../methods/desnz_uk_capacity_by_connection_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.12, Plant installed capacity, by connection. Via the Energy Research Warehouse (ERW), table `desnz_uk_capacity_by_connection_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: desnz_conn:<gb\|ni\|uk>:<transmission\|distribution\|all>:<fuel> | none | text | for example desnz_conn:gb:distribution:bioenergy, desnz_conn:gb:distribution:ccgt_gas, desnz_conn:gb:distribution:coal; 83 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 111103.434; 653 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: GB on the Great Britain and the UK rows, GB-NIR on Northern Ireland's | none | text | GB, GB-NIR | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1245 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The sheet's labels (connection and fuel), not a pricing node | none | text | for example All: Bioenergy, All: CCGT gas, All: Coal; 43 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_12_capacity_by_connection | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a3668862aaf18d9c629ed/DUKES_5.12.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T20:54:18Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time | none | utc time | 2026-07-29T17:20:40Z | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `installed_capacity` | Installed generating capacity at 31 December (not de-rated), MW | MW | 1245 | 2011-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_co2_intensity_annual`

The estimated carbon dioxide intensity of the UK's electricity supplied from one fuel group (coal, gas, all non-renewable fuels, all fuels) in one year, 1996 to 2025 (DUKES table 5.14).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 119.

- **Time:** ts_utc is the year's first day at 00:00:00Z (a year, not an instant); freq P1Y.
- **Revisions:** Rewritten whole by each run (a snapshot of the DUKES edition read, here 2026); vintage is the workbook's last-modified time. 2025's emissions are provisional (DESNZ's note 3).
- **Source:** desnz:dukes_5_14_co2_intensity Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.14, Estimated carbon dioxide intensity of electricity supplied
- **Method note:** [`docs/methods/desnz_uk_co2_intensity_annual.md`](../methods/desnz_uk_co2_intensity_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.14, Carbon dioxide intensity of electricity supplied. Via the Energy Research Warehouse (ERW), table `desnz_uk_co2_intensity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: desnz_ci:<fuel> (coal, gas, non_renewable, all_fuels) | none | text | desnz_ci:all_fuels, desnz_ci:coal, desnz_ci:gas, desnz_ci:non_renewable | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1996-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 30 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 147.25 to 1020.99; 119 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kgCO2/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always GB, standing for the UK | none | text | GB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 119 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The sheet's row label, not a pricing node | none | text | All fuels (including nuclear and renewables), All non renewable fuels, Coal, Gas | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_14_co2_intensity | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a3684bf4a7aca8f8976c4/DUKES_5.14.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T19:33:21Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time | none | utc time | 2026-07-29T17:21:08Z | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `co2_intensity` | Estimated CO2 emitted per unit of electricity supplied, kgCO2/MWh (the sheet's tonnes per GWh supplied) | kgCO2/MWh | 119 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_derated_capacity_annual`

One kind of company's (major power producers, other generators, or all) de-rated generating capacity of one fuel or thermal station type in one year, 1996 to 2025 (DUKES table 5.7).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1680.

- **Time:** ts_utc is the year's first day at 00:00:00Z (a year, not an instant); freq P1Y.
- **Revisions:** Rewritten whole by each run (a snapshot of the DUKES edition read, here 2026); vintage is the workbook's last-modified time.
- **Source:** desnz:dukes_5_7_plant_capacity Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.7, Plant capacity: United Kingdom
- **Method note:** [`docs/methods/desnz_uk_derated_capacity_annual.md`](../methods/desnz_uk_derated_capacity_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.7, Plant capacity: United Kingdom. Via the Energy Research Warehouse (ERW), table `desnz_uk_derated_capacity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: desnz_cap:<mpp\|other\|all>:<item> | none | text | for example desnz_cap:all:bioenergy_and_waste, desnz_cap:all:ccgt_stations, desnz_cap:all:coal_fired; 50 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1996-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 30 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 90393.3079; 1158 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always GB, standing for the UK | none | text | GB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1680 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The sheet's two labels (company group and item), not a pricing node | none | text | for example All generating companies: Bioenergy and waste, All generating companies: CCGT stations, All generating companies: Coal fired; 53 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_7_plant_capacity | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a3622cceb23e8678976bf/DUKES_5.7.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T19:40:40Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time | none | utc time | 2026-07-29T17:19:30Z | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `derated_capacity` | De-rated generating capacity by fuel (table 5.7.A): small hydro, wind and solar multiplied by 0.365, 0.43 and 0.17 for intermittency, MW | MW | 1200 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `thermal_capacity` | Capacity of thermal power stations by type (table 5.7.B), MW | MW | 480 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_electricity_quarterly`

The UK's electricity generated or supplied by one kind of generator (major power producers, other generators, all) from one fuel in one quarter, 1998 to 2026 (Energy Trends table 5.1).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 7862.

- **Time:** ts_utc is the quarter's first day at 00:00:00Z; freq P3M.
- **Revisions:** Merged by (entity, variable, ts_utc), a later issue replacing the rows it revises and keeping the rest; vintage is the workbook's last-modified time; a quarter DESNZ marks provisional carries x_provisional yes.
- **Source:** desnz:energy_trends_5_1 UK Department for Energy Security and Net Zero, Energy Trends section 5: electricity, table ET 5.1 (https://www.gov.uk/government/statistics/electricity-section-5-energy-trends)
- **Method note:** [`docs/methods/desnz_uk_electricity_quarterly.md`](../methods/desnz_uk_electricity_quarterly.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Energy Trends section 5: electricity, table ET 5.1 (fuel used in generation and electricity supplied). Via the Energy Research Warehouse (ERW), table `desnz_uk_electricity_quarterly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: desnz_et51:<generator type>:<fuel> | none | text | for example desnz_et51:all_generating_companies:battery_storage, desnz_et51:all_generating_companies:bioenergy, desnz_et51:all_generating_companies:coal; 43 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1998-01-01T00:00:00Z to 2026-04-01T00:00:00Z; 114 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -4853100.0 to 112158100.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P3M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always GB, standing for the UK | none | text | GB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 7862 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The generator type and fuel in DESNZ's words, not a pricing node | none | text | for example All generating companies, Battery storage, All generating companies, Bioenergy, All generating companies, Coal; 45 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:energy_trends_5_1 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6aba6dd9a9c3d267bcccefb0/ET_5.1_SEP_26.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T00:35:36Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time | none | utc time | 2026-09-28T13:38:33Z | 0 |
| `x_generator_type` | The kind of generating company: Major power producers, Other generators or All generating companies | none | text | All generating companies, Major power producers, Other generators | 0 |
| `x_fuel` | The fuel or source as DESNZ writes it (Coal, Gas, Nuclear, Offshore wind, Net imports and the others, totals included) | none | text | Battery storage, Bioenergy, Coal, Gas, Hydro (natural flow), Net imports, Nuclear, Offshore wind, Oil, Onshore wind, Other fuels, Pumped storage, Pumped storage (net supply), Shoreline wave / tidal, Solar, Total all generating companies, Total major power producers, Total other generators, Total wind | 0 |
| `x_provisional` | yes for a quarter DESNZ marks provisional (revised in a later issue), else no | none | text | no, yes | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `generated` | Electricity generated in the quarter (table 5.1b), MWh (DESNZ's TWh times 1,000,000) | MWh | 3829 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `supplied` | Electricity supplied in the quarter (table 5.1c), MWh; pumped storage's is its net supply and net imports appear only here | MWh | 4033 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |

### `desnz_uk_fuel_used_generation_annual`

The fuel one group of generating companies used for UK electricity generation, by fuel, or the major power producers' by plant type, in one year, 1996 to 2025 (DUKES table 5.3).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 900.

- **Time:** ts_utc is the year's first day at 00:00:00Z (a year, not an instant); freq P1Y.
- **Revisions:** Rewritten whole by each run (a snapshot of the DUKES edition read, here 2026); vintage is the workbook's last-modified time.
- **Source:** desnz:dukes_5_3_fuel_used Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.3, Fuel used in generation
- **Method note:** [`docs/methods/desnz_uk_fuel_used_generation_annual.md`](../methods/desnz_uk_fuel_used_generation_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.3, Fuel used in generation. Via the Energy Research Warehouse (ERW), table `desnz_uk_fuel_used_generation_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: desnz_fuel:<group>:<fuel> (groups mpp, other_transport, other_industrial, other, all) | none | text | for example desnz_fuel:all:coal, desnz_fuel:all:gas, desnz_fuel:all:hydro_natural_flow; 30 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1996-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 30 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 1012550831.0; 749 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always GB, standing for the UK | none | text | GB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 900 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The sheet's labels, not a pricing node | none | text | for example All generating companies: Coal, All generating companies: Gas, All generating companies: Hydro (natural flow); 30 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_3_fuel_used | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a35ef0ddb7e4831c629f0/DUKES_5.3.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T21:04:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time | none | utc time | 2026-07-29T17:18:39Z | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `fuel_used` | Fuel used in generation, by fuel (table 5.3.B), MWh (the sheet's million tonnes of oil equivalent times 11,630,000) | MWh | 840 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `fuel_used_by_plant` | Fuel used by the major power producers' plants, by plant type (table 5.3.C), MWh (million tonnes of oil equivalent times 11,630,000) | MWh | 60 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_gas_quarterly`

One line of the UK's natural gas balance (supply, demand and the consuming sectors) in one quarter, 1998 to 2026 (Energy Trends table 4.1).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2394.

- **Time:** ts_utc is the quarter's first day at 00:00:00Z; freq P3M.
- **Revisions:** Merged by (entity, variable, ts_utc), a row of the new issue replacing the same row and a row the new issue no longer gives kept; vintage is the workbook's last-modified time; a quarter DESNZ marks provisional carries x_provisional yes.
- **Source:** desnz:energy_trends_4_1 DESNZ, Energy Trends section 4 (gas) (https://www.gov.uk/government/statistics/gas-section-4-energy-trends)
- **Method note:** [`docs/methods/desnz_uk_gas_quarterly.md`](../methods/desnz_uk_gas_quarterly.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Energy Trends section 4: gas (table ET 4.1, natural gas supply and consumption). Via the Energy Research Warehouse (ERW), table `desnz_uk_gas_quarterly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: Always desnz_et41:uk | none | text | desnz_et41:uk | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1998-01-01T00:00:00Z to 2026-04-01T00:00:00Z; 114 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -24960040.0 to 376669000.0; 2263 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P3M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always GB, standing for the UK | none | text | GB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2394 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The balance line as DESNZ writes it, notes included, not a pricing node | none | text | Domestic, Electricity generation, Energy industry use, Exports [note 2], Final Consumption, Heat generation [note 7], Imports [note 2], Imports of Liquefied Natural Gas [note 3], Indigenous production, Iron & steel, Losses [note 8], Non energy use, Other final users, Other industries, Statistical difference, Stock change [note 4] [note 5], Total demand, Total supply, Transfers [note 6], Transformation, Transport | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:energy_trends_4_1 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6aba6b15fceb6fb3a65012ba/ET_4.1_SEP_26.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T02:17:00Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time | none | utc time | 2026-09-28T13:26:45Z | 0 |
| `x_provisional` | yes for a quarter DESNZ marks provisional (revised in a later issue), else no | none | text | no, yes | 0 |

Variables (21):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `domestic` | Final consumption by households (domestic), MWh | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `electricity_generation` | Gas used for electricity generation, MWh | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `energy_industry_use` | Gas used by the energy industries themselves, MWh | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `exports` | Gas exports, MWh (positive, subtracted in the balance) | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `final_consumption` | Final consumption of gas, MWh | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `heat_generation` | Gas used for heat generation, MWh (the latest year estimated from the previous year's, note 7) | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `imports` | Gas imports, MWh (physical flows from 2000, DESNZ's note 2) | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `imports_of_liquefied_natural_gas` | Imports of liquefied natural gas (LNG), part of imports, MWh (cargoes counted from 2016, note 3) | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `indigenous_production` | Gas produced in the UK in the quarter, MWh (DESNZ's GWh times 1,000) | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `iron_steel` | Final consumption by iron and steel, MWh | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `losses` | Gas losses, MWh (revised from 2013, note 8) | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `non_energy_use` | Gas used for non-energy purposes, MWh | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `other_final_users` | Final consumption by other final users, MWh | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `other_industries` | Final consumption by other industries, MWh | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `statistical_difference` | Statistical difference between supply and demand, DESNZ's line, MWh | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `stock_change` | Stock change, MWh: positive a draw from stocks, negative a build (DESNZ's note 4) | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `total_demand` | Total gas demand, DESNZ's line, MWh | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `total_supply` | Total gas supply, DESNZ's line, MWh | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `transfers` | Transfers, MWh (biomethane transfers may be estimated, note 6) | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `transformation` | Gas used in transformation (to make electricity and heat), MWh | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `transport` | Final consumption by transport, MWh | MWh | 114 | 1998-01-01T00:00:00Z | 2026-04-01T00:00:00Z |

### `desnz_uk_interconnector_flows_annual`

The UK's electricity imports, exports, net imports or utilisation over one interconnector border in one year, or the transfers between Scotland and England or Northern Ireland, 1998 to 2025 (DUKES table 5.13).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 642.

- **Time:** ts_utc is the year's first day at 00:00:00Z (a year, not an instant); freq P1Y.
- **Revisions:** Rewritten whole by each run (a snapshot of the DUKES edition read, here 2026); vintage is the workbook's last-modified time.
- **Source:** desnz:dukes_5_13_interconnectors Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.13, Net imports and utilisation of interconnectors
- **Method note:** [`docs/methods/desnz_uk_interconnector_flows_annual.md`](../methods/desnz_uk_interconnector_flows_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.13, Net imports and utilisation of interconnectors. Via the Energy Research Warehouse (ERW), table `desnz_uk_interconnector_flows_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: desnz_ic:<pair>: seven interconnector borders, uk_total, and the transfers scotland_england and scotland_northern_ireland (Moyle) | none | text | desnz_ic:belgium, desnz_ic:denmark, desnz_ic:france, desnz_ic:ireland_northern_ireland, desnz_ic:ireland_wales, desnz_ic:netherlands, desnz_ic:norway, desnz_ic:scotland_england, desnz_ic:scotland_northern_ireland, desnz_ic:uk_total | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1998-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 28 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -9983570.5 to 43929487.9; 621 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always GB, standing for the UK | none | text | GB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 642 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The sheet's heading, not a pricing node | none | text | for example Exports (Northern Ireland to Ireland), Exports (UK to Belgium), Exports (UK to Denmark); 37 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_13_interconnectors | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a3675bf4a7aca8f8976c3/DUKES_5.13.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T17:13:14Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time | none | utc time | 2026-07-29T17:20:53Z | 0 |

Variables (8):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `exports` | Electricity exported over the border in the year, MWh | MWh | 130 | 1998-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `imports` | Electricity imported over the border in the year, MWh (the sheet's GWh times 1,000) | MWh | 130 | 1998-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `net_imports` | Imports less exports, MWh (negative a net export) | MWh | 130 | 1998-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `net_transfers` | Net transfer between the two parts of the UK in the year, MWh | MWh | 50 | 2000-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `transfers_to_england` | Electricity sent from Scotland to England in the year, MWh | MWh | 26 | 2000-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `transfers_to_northern_ireland` | Electricity sent from Scotland to Northern Ireland in the year, MWh | MWh | 24 | 2002-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `transfers_to_scotland` | Electricity sent to Scotland (from England or Northern Ireland) in the year, MWh | MWh | 50 | 2000-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `utilisation` | The year's imports and exports over the possible flow at the interconnector's capacity (table 5.13A), ratio | ratio | 102 | 1998-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_mpp_capacity_countries_annual`

The major power producers' de-rated capacity of one fuel or thermal plant type in England and Wales, Scotland or Northern Ireland, or the country's share of their capacity, in one year, 1999 to 2025 (DUKES table 5.8).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1539.

- **Time:** ts_utc is the year's first day at 00:00:00Z (a year, not an instant); freq P1Y.
- **Revisions:** Rewritten whole by each run (a snapshot of the DUKES edition read, here 2026); vintage is the workbook's last-modified time.
- **Source:** desnz:dukes_5_8_mpp_capacity_countries Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.8, Major power producers plant capacity, England and Wales, Scotland, and Northern Ireland
- **Method note:** [`docs/methods/desnz_uk_mpp_capacity_countries_annual.md`](../methods/desnz_uk_mpp_capacity_countries_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.8, Major power producers plant capacity by country. Via the Energy Research Warehouse (ERW), table `desnz_uk_mpp_capacity_countries_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: desnz_mppr:<country>:<item> (england_wales, scotland, northern_ireland) | none | text | for example desnz_mppr:england_wales:bioenergy_and_waste, desnz_mppr:england_wales:ccgt_stations, desnz_mppr:england_wales:coal_fired; 51 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1999-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 27 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 70668.5042; 651 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: GB-ENG,GB-WLS for England and Wales, GB-SCT or GB-NIR | none | text | GB-ENG,GB-WLS, GB-NIR, GB-SCT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1539 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The sheet's labels, not a pricing node | none | text | for example England and Wales: Bioenergy and waste, England and Wales: CCGT stations, England and Wales: Coal fired; 54 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_8_mpp_capacity_countries | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a3631862aaf18d9c629ec/DUKES_5.8.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T20:58:43Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time | none | utc time | 2026-07-29T17:19:45Z | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity_share` | The country's share of the major power producers' capacity (table 5.8.B), ratio (the sheet's heading says per cent, its cells hold fractions) | ratio | 81 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `derated_capacity` | The major power producers' de-rated capacity by fuel (table 5.8.A), MW | MW | 972 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `thermal_capacity` | The major power producers' capacity by thermal plant type (table 5.8.C), MW | MW | 486 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_nations_electricity_annual`

One item of the electricity generation by fuel or the supply balance of the UK or one of its nations (England, Scotland, Wales, Northern Ireland) in one year, 2004 to 2025.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 4167.

- **Time:** ts_utc is the year's first day at 00:00:00Z (a year, not an instant); freq P1Y.
- **Revisions:** Rewritten whole by each run (DESNZ republishes the whole series each year, with revisions); vintage is the workbook's last-modified time.
- **Source:** desnz:electricity_generation_supply_nations_2026 Department for Energy Security and Net Zero, Electricity generation and supply in Scotland, Wales, Northern Ireland and England, 2004 to 2025: data tables (Energy Trends, September 2026)
- **Method note:** [`docs/methods/desnz_uk_nations_electricity_annual.md`](../methods/desnz_uk_nations_electricity_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Electricity generation and supply in Scotland, Wales, Northern Ireland and England, 2004 to 2025: data tables (Energy Trends, September 2026). Via the Energy Research Warehouse (ERW), table `desnz_uk_nations_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: desnz:<nation>:<item>, nation uk, england, scotland, wales or northern_ireland | none | text | for example desnz:england:consumption_autogenerators, desnz:england:consumption_public, desnz:england:consumption_total; 200 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2004-01-01T00:00:00Z, 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -38480068.0 to 398359717.2; 3517 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: GB on the UK's rows, GB-ENG, GB-SCT, GB-WLS or GB-NIR on a nation's | none | text | GB, GB-ENG, GB-NIR, GB-SCT, GB-WLS | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 4167 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The row's label (note marks dropped), not a pricing node | none | text | for example Consumption by autogenerators, Consumption from public supply, Distribution losses and theft; 40 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:electricity_generation_supply_nations_2026 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6aba6c4afe72ed1e2b02f14b/Regional_Electricity_Generation_and_Supply_Timeseries_2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T11:46:03Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time | none | utc time | 2026-09-28T13:31:54Z | 0 |

Variables (9):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` | Consumption from the public supply, by autogenerators, or in total, MWh | MWh | 330 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `generation` | Electricity generated, by fuel (table 2a) or in the supply balance (table 1), MWh (the tables' GWh times 1,000) | MWh | 2517 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `losses` | Transmission or distribution losses, MWh | MWh | 220 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `net_supply` | Net supply of electricity of the major power producers, the other generators or all, MWh | MWh | 220 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `net_transfers` | Net transfers to England, Northern Ireland or Europe, net of receipts as published (negative a net import), MWh | MWh | 330 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `own_use` | Electricity used by the generators themselves, MWh | MWh | 220 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `sales` | Electricity sales, MWh | MWh | 110 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `statistical_difference` | Statistical difference of the supply balance, MWh | MWh | 110 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `transfers` | Transfers from other generators to the public supply, MWh | MWh | 110 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_plant_loads_annual`

One of the major power producers' load, load factor or efficiency figures for the UK, one of its areas or one plant type in one year, 1996 to 2025 (DUKES table 5.10).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 425.

- **Time:** ts_utc is the first day of DESNZ's year at 00:00:00Z; the maximum load's year runs to March of the next (DESNZ's note 3); freq P1Y.
- **Revisions:** Rewritten whole by each run (a snapshot of the DUKES edition read, here 2026); vintage is the workbook's last-modified time.
- **Source:** desnz:dukes_5_10_plant_loads Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.10, Plant loads, demand and efficiency of major power producers
- **Method note:** [`docs/methods/desnz_uk_plant_loads_annual.md`](../methods/desnz_uk_plant_loads_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.10, Plant loads, demand and efficiency. Via the Energy Research Warehouse (ERW), table `desnz_uk_plant_loads_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: desnz_pl:<area or plant type> | none | text | desnz_pl:all_plant, desnz_pl:ccgt, desnz_pl:coal, desnz_pl:conventional_thermal, desnz_pl:england_wales, desnz_pl:great_britain, desnz_pl:northern_ireland, desnz_pl:nuclear, desnz_pl:pumped_storage, desnz_pl:scotland, desnz_pl:uk | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1996-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 30 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 61717.0; 403 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: GB (the UK, Great Britain, England and Wales and the plant types), GB-SCT or GB-NIR | none | text | GB, GB-NIR, GB-SCT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 425 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The sheet's row, prefixed with its part (5.10.A, B or C), not a pricing node | none | text | 5.10.B: All plant, 5.10.B: Combined cycle gas turbine stations, 5.10.B: Conventional thermal and other stations, 5.10.B: Nuclear stations, 5.10.B: Pumped storage hydro, 5.10.B: System load factor, 5.10.B: of which coal-fired stations, 5.10.C: Coal fired stations, 5.10.C: Combined cycle gas turbine stations, 5.10.C: Nuclear stations, Maximum demand as a percentage of major power producers' capacity UK, Simultaneous maximum load met, MW England and Wales, Simultaneous maximum load met, MW Great Britain, Simultaneous maximum load met, MW Northern Ireland, Simultaneous maximum load met, MW Scotland, Simultaneous maximum load met, MW Total | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_10_plant_loads | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a364b0ddb7e4831c629f2/DUKES_5.10.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T19:27:58Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time | none | utc time | 2026-07-29T17:20:11Z | 0 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `load_factor` | Plant load factor of a plant type (5.10.B), pct | pct | 179 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `max_demand_share_of_capacity` | Maximum demand as a percentage of the major power producers' capacity (5.10.A), pct | pct | 30 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `max_load` | The simultaneous maximum load met by the transmission network, net of demand met by embedded generation (table 5.10.A), MW | MW | 96 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `system_load_factor` | Average electricity available as a percentage of maximum demand (5.10.B), pct | pct | 30 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `thermal_efficiency` | Electricity generated as a percentage of the fuel used, gross calorific value (5.10.C), pct | pct | 90 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `desnz_uk_power_stations`

One of the major power producers' power stations in the United Kingdom operational at the end of May 2026, as DUKES table 5.11 lists it.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 1364.

- **Time:** No time column; status_date is 2026-05-31, the end of the month the sheet's title names.
- **Revisions:** Rewritten whole by each run (a snapshot of the DUKES edition read, here 2026); vintage is the workbook's last-modified time.
- **Source:** desnz:dukes_5_11_power_stations Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.11, Power stations in the United Kingdom
- **Method note:** [`docs/methods/desnz_uk_power_stations.md`](../methods/desnz_uk_power_stations.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.11, Power stations in the United Kingdom. Via the Energy Research Warehouse (ERW), table `desnz_uk_power_stations`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: dukes:<DESNZ site code> | none | text | for example dukes:BIO-000108, dukes:BIO-000134, dukes:BIO-000137; 1364 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always plant | none | text | plant | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The site name as DESNZ writes it | none | text | for example 30Acres, A'Chruach, AOE; 1347 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: GB-ENG, GB-SCT, GB-WLS or GB-NIR from the sheet's country | none | text | GB-ENG, GB-NIR, GB-SCT, GB-WLS | 0 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: Converted from the sheet's British National Grid X and Y (EPSG:27700) | degree | number | 50.046506 to 60.339325; 1302 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: Converted from the sheet's British National Grid X and Y (EPSG:27700) | degree | number | -8.005005 to 2.249319; 1302 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: The sheet's installed capacity, as stated | MW | number | 0.05 to 2580.0; 901 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Always operating | none | text | operating | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: 2026-05-31, the day the list is as of | none | date | 2026-05-31 | 0 |
| `operator` | The operator or owner, as the publisher writes it. Here: The company name as DESNZ writes it | none | text | for example Anesco, Atmosclear, BayWa R.E; 61 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_11_power_stations | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a365b0ddb7e4831c629f3/DUKES_5.11.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T17:09:21Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time | none | utc time | 2026-07-29T17:20:27Z | 0 |
| `technology` | DESNZ's technology of the station (Bioenergy, Fossil Fuel, Hydro, Nuclear, Pumped Hydro, Solar, Wind) (the source's name: Technology) | none | text | Bioenergy, Fossil Fuel, Hydro, Nuclear, Pumped Hydro, Solar, Wind | 0 |
| `type` | DESNZ's type of the station within its technology, as printed (CCGT, Single cycle, Onshore, Offshore, PV and the others); for nuclear, AGR an advanced gas-cooled reactor and PWR a pressurised water reactor, as the government's table of past and present UK nuclear reactors expands them (the source's name: Type) | none | text | AGR, Bioenergy, CCGT, Conventional steam, Large Hydro, Offshore, Onshore, PV, PWR, Pumped hydro, Single cycle, Small Hydro | 0 |
| `chp` | Whether the station is combined heat and power (CHP): Yes or No (the source's name: CHP) | none | text | No, Yes | 0 |
| `primary_fuel` | The station's main fuel as DESNZ writes it (Natural Gas, Wind, Solar, Nuclear, Biomass and the others) (the source's name: Primary Fuel) | none | text | Biomass, Diesel/Gas Oil, Hydro, MSW, Natural Gas, Nuclear, Pumped hydro, Solar, Wind | 0 |
| `secondary_fuel` | The station's second fuel as DESNZ writes it (Gas or Oil) (the source's name: Secondary Fuel) | none | text | Gas, Oil | 1360: The sheet gives no secondary fuel (1,360 of 1,364 stations) |
| `grid_connection_type` | The sheet's grid connection type of the station, HV or LV as printed (the source's name: Grid Connection Type) | none | text | HV, LV | 0 |
| `country` | The UK country the station is in, as the sheet writes it (England, Scotland, Wales, Northern Ireland) (the source's name: Country) | none | text | England, Northern Ireland, Scotland, Wales | 0 |
| `region` | The region the station is in, as the sheet writes it (England's regions, Scotland, Wales, Northern Ireland) (the source's name: Region) | none | text | East Midlands, East of England, London, North East, North West, North west, Northern Ireland, Scotland, South East, South West, Wales, West Midlands, Yorkshire and the Humber | 0 |
| `postcode` | The station's postcode as the sheet prints it (the source's name: Postcode) | none | text | for example AB39 3TE, AB39 3XZ, AB393QH; 977 distinct | 297: The sheet gives no postcode |
| `os_reference` | The sheet's OS Reference of the station, as text as printed (the source's name: OS Reference) | none | text | for example CF828FU, EX144RD, EX169QH; 654 distinct | 673: The sheet gives none |
| `x_coordinate` | The station's British National Grid easting (EPSG:27700), as the sheet gives it (the source's name: X-Coordinate) | m | number | 10820.0 to 690118.0; 1303 distinct | 0 |
| `y_coordinate` | The station's British National Grid northing (EPSG:27700), as the sheet gives it (the source's name: Y-Coordinate) | m | number | 21200.0 to 1161960.0; 1302 distinct | 0 |
| `year_commissioned` | The year the station was commissioned, as the sheet gives it (the source's name: Year Commissioned) | none | integer | 1906 to 2026; 73 distinct | 0 |
| `desnz_site_code` | DESNZ's site code of the station, unique on the sheet (SOL-000443, WON-001539 and the like) (the source's name: DESNZ site code) | none | text | for example BIO-000108, BIO-000134, BIO-000137; 1364 distinct | 0 |

Waiting for a second look: grid_connection_type: the meaning of HV and LV is not written in the connector, the method note or the header. Read again on 20 November 2026 in DUKES 5.11 as saved (sheets Cover Sheet, Notes and 5.11 Full list): not found. Read again on 27 November 2026 in DESNZ's Electricity statistics methodology note (assets.publishing.service.gov.uk, fetched once, 463,498 bytes), section 4.10.4: Table 5.12 separates capacity by connection to the transmission (higher voltage) or distribution (lower voltage) networks, from the grid connection the monthly survey records; HV and LV very likely name those two, but no document read pairs the letters with them, so the label does not say it.; os_reference: what the sheet's OS Reference holds is not documented; its values mix grid references and postcode-like strings. Read again on 20 November 2026 in DUKES 5.11 as saved (sheets Cover Sheet, Notes and 5.11 Full list): not found..

### `desnz_uk_renewables_quarterly`

The UK's cumulative installed renewable capacity or renewable electricity generated for one technology in one quarter, 2010 to 2026 (Energy Trends table 6.1).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1982.

- **Time:** ts_utc is the quarter's first day at 00:00:00Z; capacity is cumulative at the quarter's end; freq P3M.
- **Revisions:** Merged by (entity, variable, ts_utc), a later issue replacing the rows it revises and keeping the rest; vintage is the workbook's last-modified time.
- **Source:** desnz:energy_trends_6_1 UK Department for Energy Security and Net Zero, Energy Trends section 6: renewables, table ET 6.1 (https://www.gov.uk/government/statistics/energy-trends-section-6-renewables)
- **Method note:** [`docs/methods/desnz_uk_renewables_quarterly.md`](../methods/desnz_uk_renewables_quarterly.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Energy Trends section 6: renewables, table ET 6.1 (renewable electricity capacity and generation). Via the Energy Research Warehouse (ERW), table `desnz_uk_renewables_quarterly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: desnz_et61:<technology>; capacity and generation name offshore wind, hydro and co-firing differently | none | text | desnz_et61:anaerobic_digestion, desnz_et61:animal_biomass_non_ad, desnz_et61:co_firing, desnz_et61:co_firing_with_fossil_fuels, desnz_et61:energy_from_waste, desnz_et61:hydro, desnz_et61:landfill_gas, desnz_et61:large_scale_hydro, desnz_et61:liquid_biofuels, desnz_et61:non_biodegradable_wastes, desnz_et61:offshore_wind, desnz_et61:offshore_wind_floating, desnz_et61:offshore_wind_seabed, desnz_et61:onshore_wind, desnz_et61:plant_biomass, desnz_et61:sewage_sludge_digestion, desnz_et61:shoreline_wave_tidal, desnz_et61:small_scale_hydro, desnz_et61:solar_photovoltaics, desnz_et61:total | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z to 2026-04-01T00:00:00Z; 66 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 44054300.0; 1381 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P3M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always GB, standing for the UK | none | text | GB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1982 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The technology in DESNZ's words, not a pricing node | none | text | Anaerobic digestion, Animal Biomass (non-AD), Co-firing, Co-firing with fossil fuels, Energy from waste, Hydro, Landfill gas, Large scale hydro, Liquid biofuels, Non-biodegradable wastes, Offshore wind, Offshore wind - floating, Offshore wind - seabed, Onshore wind, Plant biomass, Sewage sludge digestion, Shoreline wave / tidal, Small scale hydro, Solar photovoltaics, TOTAL | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:energy_trends_6_1 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6aba724dfceb6fb3a65012d2/ET_6.1_SEP_26.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T00:55:17Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time | none | utc time | 2026-09-28T13:57:33Z | 0 |
| `x_technology` | The renewable technology in DESNZ's words (Onshore wind, Offshore wind, Anaerobic digestion, Landfill gas and the others, totals included) | none | text | Anaerobic digestion, Animal Biomass (non-AD), Co-firing, Co-firing with fossil fuels, Energy from waste, Hydro, Landfill gas, Large scale hydro, Liquid biofuels, Non-biodegradable wastes, Offshore wind, Offshore wind - floating, Offshore wind - seabed, Onshore wind, Plant biomass, Sewage sludge digestion, Shoreline wave / tidal, Small scale hydro, Solar photovoltaics, TOTAL | 0 |
| `x_provisional` | yes for a quarter DESNZ marks provisional, else no (no in every row of this issue) | none | text | no | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity` | Cumulative installed renewable capacity at the quarter's end, MW | MW | 1024 | 2010-01-01T00:00:00Z | 2026-04-01T00:00:00Z |
| `generated` | Renewable electricity generated in the quarter, MWh (DESNZ's GWh times 1,000; estimated where no actual figure exists) | MWh | 958 | 2010-01-01T00:00:00Z | 2026-04-01T00:00:00Z |

### `desnz_uk_storage_annual`

The UK's electricity out of or into storage, or storage power capacity, for one storage type in one year, 1996 to 2025 (DUKES table 5.16).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 360.

- **Time:** ts_utc is the year's first day at 00:00:00Z (a year, not an instant); freq P1Y.
- **Revisions:** Rewritten whole by each run (a snapshot of the DUKES edition read, here 2026); vintage is the workbook's last-modified time.
- **Source:** desnz:dukes_5_16_energy_storage Department for Energy Security and Net Zero, Digest of UK Energy Statistics (DUKES) 2026, table 5.16, Energy storage input electricity, output electricity, and capacity overview
- **Method note:** [`docs/methods/desnz_uk_storage_annual.md`](../methods/desnz_uk_storage_annual.md)
- **Cite as:** UK Department for Energy Security and Net Zero (DESNZ). Digest of UK Energy Statistics (DUKES) 2026, table 5.16, Energy storage overview. Via the Energy Research Warehouse (ERW), table `desnz_uk_storage_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: desnz_st:<type> (pumped_storage, battery_grid_scale, other_storage, total) | none | text | desnz_st:battery_grid_scale, desnz_st:other_storage, desnz_st:pumped_storage, desnz_st:total | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1996-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 30 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 5371305.0; 118 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always GB, standing for the UK | none | text | GB | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 360 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The table and the storage type, not a pricing node | none | text | Table 5.16.: Battery storage - grid scale, Table 5.16.: Other energy storage, Table 5.16.: Pumped storage, Table 5.16.: Total | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | desnz:dukes_5_16_energy_storage | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://assets.publishing.service.gov.uk/media/6a6a36a0bf4a7aca8f8976c6/DUKES_5.16.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T17:17:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time | none | utc time | 2026-07-29T17:21:36Z | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `input` | Electricity into storage in the year (table 5.16.B), MWh | MWh | 120 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `output` | Electricity out of storage in the year (table 5.16.A), MWh (the sheet's GWh times 1,000) | MWh | 120 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `power_capacity` | The rate at which the sites may supply their stored energy (table 5.16.C), MW | MW | 120 | 1996-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

