# Codebook: statec

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 4 public tables (4 series; tiers: 4 source); 4 documented in full.

- [`statec_lu_electricity_generation_annual`](#statec_lu_electricity_generation_annual): Luxembourg's gross or net electricity generation of one STATEC category (total, primary or secondary generation, or a plant type) in one year, 1928 to 2024, from LUSTAT table DF_A4203.
- [`statec_lu_electricity_trade_annual`](#statec_lu_electricity_trade_annual): Luxembourg's electricity imports from one origin or exports to one destination (or the totals) in one year, 1933 to 2024, from LUSTAT table DF_A4208.
- [`statec_lu_power_capacity_annual`](#statec_lu_power_capacity_annual): Luxembourg's power stations of one STATEC category (total, primary or secondary generation, or a station type) in one year, as net maximum power or as a number of stations, 1960 to 2024, from LUSTAT table DF_A4201.
- [`statec_lu_supplier_mix_annual`](#statec_lu_supplier_mix_annual): The share of one energy source (or group of sources) in the national mix of electricity supplied to Luxembourg's end users in one year, 2009 to 2024, from LUSTAT table DF_A4209; the suppliers' disclosed mix, not generation in Luxembourg.

### `statec_lu_electricity_generation_annual`

Luxembourg's gross or net electricity generation of one STATEC category (total, primary or secondary generation, or a plant type) in one year, 1928 to 2024, from LUSTAT table DF_A4203.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 942.

- **Time:** ts_utc is the year's first day at 00:00:00Z (a year, not an instant); freq P1Y.
- **Revisions:** Rewritten whole by each run (a snapshot of STATEC's file); STATEC adds a year each year and may revise earlier ones. vintage is not filled.
- **Source:** statec:lustat_df_a4203 STATEC, LUSTAT, DF_A4203 Electricity generation
- **Method note:** [`docs/methods/statec_lu_electricity_generation_annual.md`](../methods/statec_lu_electricity_generation_annual.md)
- **Cite as:** STATEC (Luxembourg). LUSTAT DF_A4203 Electricity generation. Via the Energy Research Warehouse (ERW), table `statec_lu_electricity_generation_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statec_elec:lu:<STATEC's category code, lower-cased> (l01 total gross, l02 net, sl.. and ssl.. its parts) | none | text | statec_elec:lu:l01, statec_elec:lu:l02, statec_elec:lu:sl01, statec_elec:lu:sl02, statec_elec:lu:sl03, statec_elec:lu:sl04, statec_elec:lu:sl05, statec_elec:lu:sl06, statec_elec:lu:sl07, statec_elec:lu:ssl01, statec_elec:lu:ssl02, statec_elec:lu:ssl03, statec_elec:lu:ssl04, statec_elec:lu:ssl05, statec_elec:lu:sssl01, statec_elec:lu:sssl02, statec_elec:lu:sssl03, statec_elec:lu:sssl04, statec_elec:lu:sssl05 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1928-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 97 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 40.278 to 4591514.722; 771 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always LU (Luxembourg) | none | text | LU | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 942 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: STATEC's category code and label (L02 Net generation), not a pricing node | none | text | L01 Total gross generation, L02 Net generation, SL01 Gross primary generation, SL02 Gross secondary generation, SL03 Hydro, SL04 Wind, SL05 Solar, SL06 Thermal, SL07 Combined Heat and Power, SSL01 Hydro, SSL02 Wind, SSL03 Solar, SSL04 Thermal, SSL05 Combined Heat and Power, SSSL01 of which pumping, SSSL02 Siderurgy, SSSL03 Biogas, SSSL04 Wood wastes, SSSL05 Pellets | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statec:lustat_df_a4203 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://lustat.statec.lu/rest/data/LU1,DF_A4203,1.0/all?format=csvfilewithlabels | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T00:09:49Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 942 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `electricity_generation` | Electricity generated in the year by the row's category (gross or net, as the node says), MWh (STATEC's GWh times 1,000) | MWh | 942 | 1928-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `statec_lu_electricity_trade_annual`

Luxembourg's electricity imports from one origin or exports to one destination (or the totals) in one year, 1933 to 2024, from LUSTAT table DF_A4208.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 584.

- **Time:** ts_utc is the year's first day at 00:00:00Z (a year, not an instant); freq P1Y.
- **Revisions:** Rewritten whole by each run (a snapshot of STATEC's file); STATEC adds a year each year and may revise earlier ones. vintage is not filled.
- **Source:** statec:lustat_df_a4208 STATEC, LUSTAT, DF_A4208 Electricity imports and exports by country
- **Method note:** [`docs/methods/statec_lu_electricity_generation_annual.md`](../methods/statec_lu_electricity_generation_annual.md)
- **Cite as:** STATEC (Luxembourg). LUSTAT DF_A4208 Electricity imports and exports by country. Via the Energy Research Warehouse (ERW), table `statec_lu_electricity_trade_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statec_trade:lu:<STATEC's code, lower-cased>: l01 imports, l02 exports, sl01 to sl06 by country, ssl01 and ssl02 Germany's split | none | text | statec_trade:lu:l01, statec_trade:lu:l02, statec_trade:lu:sl01, statec_trade:lu:sl02, statec_trade:lu:sl03, statec_trade:lu:sl04, statec_trade:lu:sl05, statec_trade:lu:sl06, statec_trade:lu:ssl01, statec_trade:lu:ssl02 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1933-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 92 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.0 to 7718393.333; 564 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always LU (Luxembourg) | none | text | LU | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 584 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: STATEC's code and label (SL01 From Belgium), not a pricing node | none | text | L01 Imports, L02 Exports, SL01 From Belgium, SL02 From France, SL03 From Germany, SL04 To Belgium, SL05 To France, SL06 To Germany (RWE grid), SSL01 Société Électrique de l'Our (SEO), SSL02 Others | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statec:lustat_df_a4208 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://lustat.statec.lu/rest/data/LU1,DF_A4208,1.0/all?format=csvfilewithlabels | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T00:17:03Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 584 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `electricity_exports` | Electricity Luxembourg exported in the year, to the destination the node names (or in total), MWh (STATEC's GWh times 1,000) | MWh | 227 | 1933-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `electricity_imports` | Electricity Luxembourg imported in the year, from the origin the node names (or in total), MWh (STATEC's GWh times 1,000) | MWh | 357 | 1933-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `statec_lu_power_capacity_annual`

Luxembourg's power stations of one STATEC category (total, primary or secondary generation, or a station type) in one year, as net maximum power or as a number of stations, 1960 to 2024, from LUSTAT table DF_A4201.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 951.

- **Time:** ts_utc is the year's first day at 00:00:00Z (a year, not an instant); freq P1Y.
- **Revisions:** Rewritten whole by each run (a snapshot of STATEC's file); STATEC adds a year each year and may revise earlier ones. vintage is not filled.
- **Source:** statec:lustat_df_a4201 STATEC, LUSTAT, DF_A4201 Net maximum power (in MWe) and units of the power stations
- **Method note:** [`docs/methods/statec_lu_power_capacity_annual.md`](../methods/statec_lu_power_capacity_annual.md)
- **Cite as:** STATEC (Luxembourg). LUSTAT DF_A4201 Net maximum power (in MWe) and units of the power stations. Via the Energy Research Warehouse (ERW), table `statec_lu_power_capacity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statec_cap:lu:<STATEC's category code, lower-cased> (l01 total, sl.. ssl.. sssl.. its parts) | none | text | statec_cap:lu:l01, statec_cap:lu:sl01, statec_cap:lu:sl02, statec_cap:lu:ssl01, statec_cap:lu:ssl02, statec_cap:lu:ssl03, statec_cap:lu:ssl04, statec_cap:lu:ssl05, statec_cap:lu:sssl01, statec_cap:lu:sssl02, statec_cap:lu:sssl03, statec_cap:lu:sssl04, statec_cap:lu:sssl05, statec_cap:lu:sssl06 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1960-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 44 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 22861.0; 430 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always LU (Luxembourg) | none | text | LU | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 951 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: STATEC's category code and label (SSL01 Hydropower stations), not a pricing node | none | text | L01 Total, SL01 Primary generation stations, SL02 Secondary generation stations, SSL01 Hydropower stations, SSL02 Wind power stations, SSL03 Solar power stations, SSL04 Classic thermal stations, SSL05 Combined heat and power stations, SSSL01 pumping stations, SSSL02 large stations, SSSL03 micro stations, SSSL04 biomethanation stations, SSSL05 woodwaste stations, SSSL06 woodpellets stations | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statec:lustat_df_a4201 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://lustat.statec.lu/rest/data/LU1,DF_A4201,1.0/all?format=csvfilewithlabels | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T01:53:49Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 951 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `net_maximum_power` | The net maximum power of the category's power stations in the year, MW (STATEC's MWe) | MW | 476 | 1960-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `power_stations` | The number of the category's power stations in the year, count | count | 475 | 1960-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `statec_lu_supplier_mix_annual`

The share of one energy source (or group of sources) in the national mix of electricity supplied to Luxembourg's end users in one year, 2009 to 2024, from LUSTAT table DF_A4209; the suppliers' disclosed mix, not generation in Luxembourg.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 196.

- **Time:** ts_utc is the year's first day at 00:00:00Z (a year, not an instant); freq P1Y.
- **Revisions:** Rewritten whole by each run (a snapshot of STATEC's file); STATEC adds a year each year and may revise earlier ones. vintage is not filled.
- **Source:** statec:lustat_df_a4209 STATEC, LUSTAT, DF_A4209 National mix of electricity provided to the end-users (in %)
- **Method note:** [`docs/methods/statec_lu_power_capacity_annual.md`](../methods/statec_lu_power_capacity_annual.md)
- **Cite as:** STATEC (Luxembourg). LUSTAT DF_A4209 National mix of electricity provided to the end-users (in %). Via the Energy Research Warehouse (ERW), table `statec_lu_supplier_mix_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: statec_mix:lu:<STATEC's code, lower-cased>: l01 fossil, l02 nuclear, l03 renewable, l04 other and unidentified, sl.. their parts | none | text | statec_mix:lu:l01, statec_mix:lu:l02, statec_mix:lu:l03, statec_mix:lu:l04, statec_mix:lu:sl01, statec_mix:lu:sl02, statec_mix:lu:sl03, statec_mix:lu:sl04, statec_mix:lu:sl05, statec_mix:lu:sl06, statec_mix:lu:sl07, statec_mix:lu:sl08, statec_mix:lu:sl09 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.1 to 68.1; 131 distinct | 0 |
| `unit` | The unit of the row's value | none | text | pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always LU (Luxembourg) | none | text | LU | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 196 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: STATEC's code and label (L03 Renewable energy), not a pricing node | none | text | L01 Fossil energy, L02 Nuclear energy, L03 Renewable energy, L04 Other sources and unidentified sources, SL01 Hard coal, SL02 Brown coal, SL03 Naturel gas, SL04 Other fossil energies (oil, others), SL05 Biomass and biogas, SL06 Wind energy, SL07 Hydroelectricity, SL08 Solar energy, SL09 Other sources of renewable energy | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | statec:lustat_df_a4209 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://lustat.statec.lu/rest/data/LU1,DF_A4209,1.0/all?format=csvfilewithlabels | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T01:59:35Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 196 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `supply_mix_share` | The source's share of the electricity supplied to end users in the year, percent (l01 to l04 make 100) | pct | 196 | 2009-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

