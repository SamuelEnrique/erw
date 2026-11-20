# Codebook: eurostat

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 27 public tables (27 series; tiers: 27 source); 27 documented in full.

- [`eurostat_crude_imports_by_field_monthly`](#eurostat_crude_imports_by_field_monthly): The EU's crude oil imports of one stream (field of production), or of all streams together, in one month, one measure (volume, value, price, API gravity or sulphur).
- [`eurostat_crude_imports_monthly`](#eurostat_crude_imports_monthly): One European country's (or EU aggregate's) crude oil imports from one partner in one month.
- [`eurostat_data_centre_electricity_annual`](#eurostat_data_centre_electricity_annual): One European country's data centres' electricity consumption in one year.
- [`eurostat_electricity_capacity_annual`](#eurostat_electricity_capacity_annual): One European country's (or EU aggregate's) net electricity production capacity, or capacity commissioned or decommissioned, for one fuel group and operator type in one year.
- [`eurostat_electricity_consumption_annual`](#eurostat_electricity_consumption_annual): One European country's (or the EU's) electricity for one balance item (available for final consumption, final consumption, a sector's use, losses, statistical differences) in one year.
- [`eurostat_electricity_monthly`](#eurostat_electricity_monthly): One European country's (or the EU's) net electricity production from one fuel, or one electricity flow, in one month.
- [`eurostat_electricity_production_annual`](#eurostat_electricity_production_annual): One European country's (or the EU's) gross electricity production from one fuel (SIEC product), all producers, in one year.
- [`eurostat_electricity_trade_annual`](#eurostat_electricity_trade_annual): One European country's (or EU aggregate's) electricity imports from, or exports to, one partner in one year, as the country reports them.
- [`eurostat_electrification_rate_annual`](#eurostat_electrification_rate_annual): One European country's (or the EU's) rate of electrification of one end-use item (final consumption, a sector or branch, or the energy sector's own use) in one year.
- [`eurostat_ev_recharging_annual`](#eurostat_ev_recharging_annual): One European country's count or power output of electric vehicle recharging infrastructure of one kind in one year.
- [`eurostat_ev_recharging_power_annual`](#eurostat_ev_recharging_power_annual): One European country's recharging points for electric vehicles in one power category in one year.
- [`eurostat_fossil_share_annual`](#eurostat_fossil_share_annual): One European country's (or the EU's) share of fossil fuels in its gross available energy in one year.
- [`eurostat_gas_balance_monthly`](#eurostat_gas_balance_monthly): One European country's (or EU aggregate's) natural gas for one balance item (production, trade, stock change, consumption, losses) in one month.
- [`eurostat_gas_import_origin_annual`](#eurostat_gas_import_origin_annual): One European country's (or the EU's) natural gas import dependency on one country of origin in one year, 2015 to 2020.
- [`eurostat_gas_imports_monthly`](#eurostat_gas_imports_monthly): One European country's (or EU aggregate's) imports of natural gas or of LNG from one partner in one month.
- [`eurostat_hard_coal_imports_annual`](#eurostat_hard_coal_imports_annual): One European country's (or EU aggregate's) hard coal imports from one partner in one year.
- [`eurostat_household_electricity_annual`](#eurostat_household_electricity_annual): One European country's (or the EU's) household electricity consumption, in total or for one end use, in one year.
- [`eurostat_import_concentration_annual`](#eurostat_import_concentration_annual): One EU country's import origin concentration index for one fuel in one year.
- [`eurostat_import_dependency_annual`](#eurostat_import_dependency_annual): One European country's (or the EU's) import dependency for one fuel (SIEC product) in one year.
- [`eurostat_industry_electricity_annual`](#eurostat_industry_electricity_annual): One European country's (or the EU's) electricity consumption of one industrial activity (NACE Rev. 2) in one year.
- [`eurostat_nonhousehold_bands_annual`](#eurostat_nonhousehold_bands_annual): One European country's (or EU aggregate's) share of non-household electricity consumption in one annual consumption band in one year.
- [`eurostat_nuclear_fuel_cycle_annual`](#eurostat_nuclear_fuel_cycle_annual): One European country's (or the EU's) value of one nuclear fuel cycle measure (enrichment, fuel fabrication, reprocessing, nuclear heat) in one year.
- [`eurostat_oil_monthly`](#eurostat_oil_monthly): One European country's (or the EU's) flow of one oil product (crude oil, oil products, motor gasoline, gas and diesel oil, jet fuel, fuel oil, LPG) in one month.
- [`eurostat_renewable_capacity_annual`](#eurostat_renewable_capacity_annual): One European country's (or EU aggregate's) net electricity capacity of one renewable (or waste) fuel in one year.
- [`eurostat_renewable_shares_annual`](#eurostat_renewable_shares_annual): One European country's (or the EU's) renewable share of gross final energy consumption, overall or for one sector, in one year.
- [`eurostat_solid_fuels_monthly`](#eurostat_solid_fuels_monthly): One European country's (or the EU's) flow of one solid fuel (hard coal, brown coal, coke oven coke, peat, oil shale and oil sands) in one month.
- [`eurostat_supply_diversity_annual`](#eurostat_supply_diversity_annual): One EU country's diversity index of energy supply in one year.

### `eurostat_crude_imports_by_field_monthly`

The EU's crude oil imports of one stream (field of production), or of all streams together, in one month, one measure (volume, value, price, API gravity or sulphur).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 51718.

- **Time:** ts_utc is the month's first day at 00:00:00Z (freq P1M).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised month replaces the old figure on a later run, no earlier version is kept; vintage is not filled.
- **Source:** eurostat:nrg_ti_coifpm_eu Eurostat, Crude oil imports by field of production - monthly data (nrg_ti_coifpm), the EU (EU_V) (https://ec.europa.eu/eurostat/databrowser/view/nrg_ti_coifpm/default/table)
- **Method note:** [`docs/methods/eurostat_crude_imports_by_field_monthly.md`](../methods/eurostat_crude_imports_by_field_monthly.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Crude oil imports by field of production - monthly data (nrg_ti_coifpm), the EU. Via the Energy Research Warehouse (ERW), table `eurostat_crude_imports_by_field_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_crude_field:EU:<Eurostat crude oil code>; TOTAL is every stream together | none | text | for example eurostat_crude_field:EU:AE_RAK_CNDS, eurostat_crude_field:EU:AE_RKT_MSC, eurostat_crude_field:EU:AFR_OTH; 819 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2016-01-01T00:00:00Z to 2026-09-01T00:00:00Z; 124 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 38679118314.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD, USD/bbl, degAPI, kbbl, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Empty on every row: the EU (Eurostat's EU_V, the member states of the month) | none | empty | no cell holds a value | 51718 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 51718 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The stream's name as Eurostat gives it, not a pricing node | none | text | for example Abu Dhabi - Abu Al Bu Khoosh, Abu Dhabi - Al Bunduq, Abu Dhabi - Arzanah; 819 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_ti_coifpm_eu | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ti_coifpm?format=JSON&lang=EN&geo=EU_V&sinceTimePeriod=2016-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T11:31:26Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 51718 |
| `x_crudeoil` | Eurostat's code of the crude oil stream (TOTAL every stream) | none | text | for example AE_RAK_CNDS, AE_RKT_MSC, AFR_OTH; 819 distinct | 0 |
| `x_indic_nrg` | Eurostat's indicator code of the measure: VOL_THS_BBL volume, VAL_THS_USD value, AVGPRC_USD_BBL price, API_DEG API gravity, SULPH_PC sulphur | none | text | API_DEG, AVGPRC_USD_BBL, SULPH_PC, VAL_THS_USD, VOL_THS_BBL | 0 |
| `x_flag` | Eurostat's status of the observation: b break in series | none | text | b | 51715: No flag on the observation |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `api_gravity` | API gravity of the stream, degrees API (kept as published, some above any crude oil's) | degAPI | 7991 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `price` | Average price, USD a barrel (a price of 0 is not taken) | USD/bbl | 2660 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `sulphur` | Sulphur content, percent by weight | pct | 8013 | 2020-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `value` | Value of the imports, USD (Eurostat's thousand USD times 1,000) | USD | 2660 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `volume` | Volume imported, thousand barrels | kbbl | 30394 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `eurostat_crude_imports_monthly`

One European country's (or EU aggregate's) crude oil imports from one partner in one month.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 565941.

- **Time:** ts_utc is the month's first day at 00:00:00Z (freq P1M).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_ti_oilm_crude Eurostat, Oil and petroleum products imports - monthly data (nrg_ti_oilm), crude oil (O4100_TOT) (https://ec.europa.eu/eurostat/databrowser/view/nrg_ti_oilm/default/table)
- **Method note:** [`docs/methods/eurostat_crude_imports_monthly.md`](../methods/eurostat_crude_imports_monthly.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Oil and petroleum products imports - monthly data (nrg_ti_oilm), crude oil by partner. Via the Energy Research Warehouse (ERW), table `eurostat_crude_imports_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_crude_imp:<Eurostat geo code>:<partner code> | none | text | for example eurostat_crude_imp:AL:AD, eurostat_crude_imp:AL:AE, eurostat_crude_imp:AL:AFR_OTH; more than 5000 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2016-01-01T00:00:00Z to 2026-09-01T00:00:00Z; 129 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 46193000.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | t | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: The importing country's ISO alpha-2 code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 and EA21 | none | text | for example AL, AT, BE; 35 distinct | 23183 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 565941 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Crude oil imports from <partner>, not a pricing node | none | text | for example Crude oil imports from Albania, Crude oil imports from Algeria, Crude oil imports from Andorra; 173 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_ti_oilm_crude | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ti_oilm?format=JSON&lang=EN&siec=O4100_TOT&sinceTimePeriod=2016-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T09:40:02Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 565941 |
| `x_geo_code` | Eurostat's geo code of the importing country or aggregate (EL for Greece; EU27_2020, EA21) | none | text | for example AL, AT, BE; 37 distinct | 0 |
| `x_partner` | Eurostat's partner code (a country, or an aggregate: TOTAL every partner, NSP not specified, _OTH groups; NA is Namibia) | none | text | for example AD, AE, AFR_OTH; 173 distinct | 0 |
| `x_partner_name` | Eurostat's name of the partner | none | text | for example Albania, Algeria, Andorra; 173 distinct | 0 |
| `x_flag` | Eurostat's status of the observation: p provisional | none | text | p | 564808: No flag on the observation |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `imports` | Crude oil imported from the partner, tonnes (Eurostat's thousand tonnes times 1,000) | t | 565941 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `eurostat_data_centre_electricity_annual`

One European country's data centres' electricity consumption in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 85.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:isoc_env_ict_nrg Eurostat, Data centres' electricity consumption (isoc_env_ict_nrg) (https://ec.europa.eu/eurostat/databrowser/view/isoc_env_ict_nrg/default/table)
- **Method note:** [`docs/methods/eurostat_data_centre_electricity_annual.md`](../methods/eurostat_data_centre_electricity_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Data centres' electricity consumption (isoc_env_ict_nrg). Via the Energy Research Warehouse (ERW), table `eurostat_data_centre_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_data_centres:<geo> | none | text | for example eurostat_data_centres:AL, eurostat_data_centres:AT, eurostat_data_centres:BE; 32 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 20000000.0; 58 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2 | none | text | for example AL, AT, BE; 32 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 85 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> data centres' electricity consumption, not a pricing node | none | text | for example AL data centres' electricity consumption, AT data centres' electricity consumption, BE data centres' electricity consumption; 32 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:isoc_env_ict_nrg | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/isoc_env_ict_nrg?format=SDMX-CSV&compressed=false | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T03:25:03Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 85 |
| `x_geo_code` | Eurostat's geo code of the country | none | text | for example AL, AT, BE; 32 distinct | 0 |
| `x_flag` | Eurostat's flag of the observation: e estimated | none | text | e | 80: No flag on the observation |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 85: Not filled: no cell holds a value (confidential observations have no row) |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `electricity_consumption` | Electricity consumed by data centres (NACE DATAC), MWh (Eurostat's GWh times 1,000); zeros kept as printed | MWh | 85 | 2020-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eurostat_electricity_capacity_annual`

One European country's (or EU aggregate's) net electricity production capacity, or capacity commissioned or decommissioned, for one fuel group and operator type in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 159060.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_inf_epc Eurostat, Electricity production capacities by main fuel groups and operator (nrg_inf_epc) (https://ec.europa.eu/eurostat/databrowser/view/nrg_inf_epc/default/table)
- **Method note:** [`docs/methods/eurostat_electricity_capacity_annual.md`](../methods/eurostat_electricity_capacity_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Electricity production capacities by main fuel groups and operator (nrg_inf_epc). Via the Energy Research Warehouse (ERW), table `eurostat_electricity_capacity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_epc:<Eurostat geo code>:<SIEC code>; fuel groups overlap, so a sum double counts | none | text | for example eurostat_epc:AL:C0000, eurostat_epc:AL:CF, eurostat_epc:AL:G3000; 1072 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 35 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 1169867.024; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 and EA21 | none | text | for example AL, AT, BA; 38 distinct | 12450 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 159060 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The SIEC code's English name (the fuel group), not a pricing node | none | text | for example Biofuels and waste, Coal and manufactured gases, Combustible fuels; 27 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_inf_epc | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_inf_epc?format=SDMX-CSV&compressed=false | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T07:17:31Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 159060 |
| `x_geo_code` | Eurostat's geo code of the country or aggregate | none | text | for example AL, AT, BA; 40 distinct | 0 |
| `x_siec` | Eurostat's SIEC code of the fuel group | none | text | for example C0000, CF, G3000; 27 distinct | 0 |
| `x_plant_tec` | Eurostat's capacity code: CAP_NET_ELC net capacity, CAP_NET_ELC_C commissioned, CAP_NET_ELC_DCM decommissioned | none | text | CAP_NET_ELC, CAP_NET_ELC_C, CAP_NET_ELC_DCM | 0 |
| `x_operator` | Eurostat's operator code: TOTAL, PRR_MAIN main activity producers, PRR_AUTO autoproducers | none | text | PRR_AUTO, PRR_MAIN, TOTAL | 0 |
| `x_flag` | Eurostat's flag of the observation: p provisional | none | text | p | 159059: No flag on the observation |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 159060: Not filled: no cell holds a value |

Variables (9):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `net_capacity_autoproducers` | Net capacity of autoproducers (producing mainly for their own use) | MW | 30450 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_capacity_commissioned_autoproducers` | Net capacity commissioned in the year, autoproducers | MW | 11285 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_capacity_commissioned_main_producers` | Net capacity commissioned in the year, main activity producers | MW | 11280 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_capacity_commissioned_total` | Net capacity commissioned in the year, all operators | MW | 11287 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_capacity_decommissioned_autoproducers` | Net capacity decommissioned in the year, autoproducers | MW | 11285 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_capacity_decommissioned_main_producers` | Net capacity decommissioned in the year, main activity producers | MW | 11286 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_capacity_decommissioned_total` | Net capacity decommissioned in the year, all operators | MW | 11287 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_capacity_main_producers` | Net capacity of main activity producers | MW | 30450 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_capacity_total` | Net maximum electrical capacity, all operators | MW | 30450 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eurostat_electricity_consumption_annual`

One European country's (or the EU's) electricity for one balance item (available for final consumption, final consumption, a sector's use, losses, statistical differences) in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 15667.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_cb_e Eurostat, Supply, transformation and consumption of electricity (nrg_cb_e) (https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_e/default/table)
- **Method note:** [`docs/methods/eurostat_electricity_consumption_annual.md`](../methods/eurostat_electricity_consumption_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Supply, transformation and consumption of electricity (nrg_cb_e). Via the Energy Research Warehouse (ERW), table `eurostat_electricity_consumption_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_electricity_consumption:<geo> | none | text | for example eurostat_electricity_consumption:AL, eurostat_electricity_consumption:AT, eurostat_electricity_consumption:BA; 40 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 36 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -5082476.0 to 2622873825.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 | none | text | for example AL, AT, BA; 39 distinct | 426 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 15667 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> electricity, <the balance item's name>, not a pricing node | none | text | for example AL electricity, Available for final consumption, AL electricity, Energy sector - energy use, AL electricity, Final consumption; 479 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_cb_e | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_e/A..E7000.GWH.?format=SDMX-CSV&compressed=false&startPeriod=1990 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T22:25:36Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 15667 |
| `x_geo_code` | Eurostat's geo code of the country or aggregate | none | text | for example AL, AT, BA; 40 distinct | 0 |
| `x_nrg_bal` | Eurostat's NRG_BAL code of the balance item | none | text | AFC, FC, FC_IND_E, FC_OTH_AF_E, FC_OTH_CP_E, FC_OTH_FISH_E, FC_OTH_HH_E, FC_OTH_NSP_E, FC_TRA_E, LOSS, NRG_E, STATDIFF | 0 |
| `x_flag` | Eurostat's flag of the observation: e estimated, p provisional | none | text | e, p | 15448: No flag on the observation |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 15667: Not filled: no cell holds a value |

Variables (12):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `agriculture_forestry` | Final consumption by agriculture and forestry (FC_OTH_AF_E) | MWh | 1290 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `available_for_final_consumption` | Electricity available for final consumption (AFC) | MWh | 1328 | 1990-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `commercial_public_services` | Final consumption by commercial and public services (FC_OTH_CP_E) | MWh | 1290 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `energy_sector_use` | The energy sector's own use of electricity (NRG_E) | MWh | 1326 | 1990-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `final_consumption` | Final consumption of electricity (FC), here including the energy sector's own use | MWh | 1326 | 1990-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `fishing` | Final consumption by fishing (FC_OTH_FISH_E) | MWh | 1290 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `households` | Final consumption by households (FC_OTH_HH_E) | MWh | 1290 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `industry` | Final consumption by industry (FC_IND_E) | MWh | 1326 | 1990-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `losses` | Electricity losses (LOSS) | MWh | 1259 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `other_not_specified` | Final consumption not elsewhere specified (FC_OTH_NSP_E) | MWh | 1289 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `statistical_differences` | Statistical differences of the balance (STATDIFF) | MWh | 1327 | 1990-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `transport` | Final consumption by transport (FC_TRA_E) | MWh | 1326 | 1990-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `eurostat_electricity_monthly`

One European country's (or the EU's) net electricity production from one fuel, or one electricity flow, in one month.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 130025.

- **Time:** ts_utc is the month's first day at 00:00:00Z (freq P1M).
- **Revisions:** A snapshot, the whole table replaced by each run; vintage is not filled.
- **Source:** eurostat:nrg_cb_pem_nrg_cb_em Eurostat, Net electricity generation by type of fuel, monthly data (nrg_cb_pem) and Supply, transformation and consumption of electricity, monthly data (nrg_cb_em) (https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_pem/default/table)
- **Method note:** [`docs/methods/eurostat_electricity_monthly.md`](../methods/eurostat_electricity_monthly.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Net electricity generation by type of fuel, monthly (nrg_cb_pem); Supply, transformation and consumption of electricity, monthly (nrg_cb_em). Via the Energy Research Warehouse (ERW), table `eurostat_electricity_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_elec:<Eurostat geo code> | none | text | for example eurostat_elec:AL, eurostat_elec:AT, eurostat_elec:BA; 40 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2016-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 128 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -2538.0 to 271874687.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 | none | text | for example AL, AT, BA; 39 distinct | 3406 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 130025 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The SIEC or NRG_BAL code's English name, not a pricing node | none | text | for example Available to internal market, Coal and manufactured gases, Combustible fuels; 30 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_cb_pem_nrg_cb_em | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_em?format=SDMX-CSV&compressed=false&startPeriod=2016-01, https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_pem?format=SDMX-CSV&compressed=false&startPeriod=2016-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T02:05:25Z, 2026-10-24T02:05:57Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 130025 |
| `x_geo_code` | Eurostat's geo code of the country or aggregate | none | text | for example AL, AT, BA; 40 distinct | 0 |
| `x_dataset` | The Eurostat dataset the row came from: nrg_cb_pem (net production by fuel) or nrg_cb_em (the flows) | none | text | nrg_cb_em, nrg_cb_pem | 0 |
| `x_flag` | Eurostat's flag of the observation: e estimated, p provisional, n not significant, u low reliability, d definition differs, b break in series | none | text | b, d, e, n, p, u | 124558: No flag on the observation |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 130025: Not filled: no cell holds a value |

Variables (30):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `flow:AIM` | Electricity available to the internal market (NRG_BAL AIM) | MWh | 4746 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `flow:DL` | Distribution losses (NRG_BAL DL) | MWh | 4145 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `flow:EXP` | Exports of electricity (NRG_BAL EXP) | MWh | 4745 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `flow:EXP_TO_EU` | Exports of electricity to the EU (NRG_BAL EXP_TO_EU) | MWh | 4337 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `flow:IMP` | Imports of electricity (NRG_BAL IMP) | MWh | 4745 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `flow:IMP_FROM_EU` | Imports of electricity from the EU (NRG_BAL IMP_FROM_EU) | MWh | 4337 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `flow:TI_EHG_EPS` | Transformation input, electricity for pumped storage (NRG_BAL TI_EHG_EPS) | MWh | 4734 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:C0000` | Net electricity production from coal and manufactured gases (SIEC C0000) | MWh | 4259 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:CF` | Net electricity production from combustible fuels (SIEC CF) | MWh | 4746 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:CF_NR_OTH` | Net electricity production from other non-renewable combustible fuels (SIEC CF_NR_OTH) | MWh | 4270 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:CF_R` | Net electricity production from renewable combustible fuels (SIEC CF_R) | MWh | 4294 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:FE` | Net electricity production from fossil energy (SIEC FE) | MWh | 1212 | 2023-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:G3000` | Net electricity production from natural gas (SIEC G3000) | MWh | 4201 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:N9000` | Net electricity production from nuclear fuels and other fuels n.e.c. (SIEC N9000) | MWh | 4746 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:O4000XBIO` | Net electricity production from oil and petroleum products, excluding biofuel portion (SIEC O4000XBIO) | MWh | 4120 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:RA000` | Net electricity production from renewables and biofuels (SIEC RA000) | MWh | 4350 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:RA100` | Net electricity production from hydro (SIEC RA100) | MWh | 4746 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:RA110` | Net electricity production from pure hydro power (SIEC RA110) | MWh | 4350 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:RA120` | Net electricity production from mixed hydro power (SIEC RA120) | MWh | 4230 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:RA130` | Net electricity production from pumped hydro power (SIEC RA130) | MWh | 4350 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:RA200` | Net electricity production from geothermal (SIEC RA200) | MWh | 4746 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:RA300` | Net electricity production from wind (SIEC RA300) | MWh | 4746 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:RA310` | Net electricity production from wind on shore (SIEC RA310) | MWh | 4311 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:RA320` | Net electricity production from wind off shore (SIEC RA320) | MWh | 4311 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:RA400` | Net electricity production from solar (SIEC RA400) | MWh | 4281 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:RA410` | Net electricity production from solar thermal (SIEC RA410) | MWh | 4261 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:RA420` | Net electricity production from solar photovoltaic (SIEC RA420) | MWh | 4317 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:RA500_5160` | Net electricity production from other renewable energies (SIEC RA500_5160) | MWh | 4293 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:TOTAL` | Net electricity production, all fuels (SIEC TOTAL) | MWh | 4746 | 2016-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_production:X9900` | Net electricity production from other fuels n.e.c. (SIEC X9900) | MWh | 4350 | 2017-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `eurostat_electricity_production_annual`

One European country's (or the EU's) gross electricity production from one fuel (SIEC product), all producers, in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 73988.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old one, and a figure Eurostat stops printing keeps its earlier value; vintage is not filled.
- **Source:** eurostat:nrg_bal_peh Eurostat, Production of electricity and derived heat by type of fuel (nrg_bal_peh), gross electricity production (https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_peh/default/table)
- **Method note:** [`docs/methods/eurostat_electricity_production_annual.md`](../methods/eurostat_electricity_production_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Production of electricity and derived heat by type of fuel (nrg_bal_peh), gross electricity production. Via the Energy Research Warehouse (ERW), table `eurostat_electricity_production_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_electricity_production:<geo>:<SIEC>; the products overlap, so a sum takes one level | none | text | for example eurostat_electricity_production:AL:BA100, eurostat_electricity_production:AL:BIOE, eurostat_electricity_production:AL:C0000X0350-0370; 2256 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 35 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 2998754778.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 | none | text | for example AL, AT, BA; 38 distinct | 1960 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 73988 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> gross electricity production, <the SIEC product's name>, not a pricing node | none | text | for example AL gross electricity production, Anthracite, AL gross electricity production, Batteries, AL gross electricity production, Bioenergy; 2256 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_bal_peh | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_bal_peh/A.GEP..GWH.?format=SDMX-CSV&compressed=false&startPeriod=1990 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T10:51:35Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 73988 |
| `x_geo_code` | Eurostat's geo code of the country or aggregate | none | text | for example AL, AT, BA; 39 distinct | 0 |
| `x_siec` | Eurostat's SIEC product code of the fuel | none | text | for example BA100, BIOE, C0000X0350-0370; 58 distinct | 0 |
| `x_flag` | Eurostat's flag of the observation | none | empty | no cell holds a value | 73988: Not filled: no cell holds a value (lines flagged m, missing, have no row) |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 73988: Not filled: no cell holds a value |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `gross_electricity_production` | Gross electricity production (GEP, the plants' own use included), MWh (Eurostat's GWh times 1,000) | MWh | 73988 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eurostat_electricity_trade_annual`

One European country's (or EU aggregate's) electricity imports from, or exports to, one partner in one year, as the country reports them.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 198783.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_ti_eh_nrg_te_eh Eurostat, Electricity and derived heat imports (nrg_ti_eh) and exports (nrg_te_eh), electricity (E7000) (https://ec.europa.eu/eurostat/databrowser/view/nrg_ti_eh/default/table)
- **Method note:** [`docs/methods/eurostat_electricity_trade_annual.md`](../methods/eurostat_electricity_trade_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Electricity and derived heat imports (nrg_ti_eh) and exports (nrg_te_eh), electricity by partner. Via the Energy Research Warehouse (ERW), table `eurostat_electricity_trade_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_elec_trade:<Eurostat geo code>:<partner code> | none | text | for example eurostat_elec_trade:AL:AD, eurostat_elec_trade:AL:AE, eurostat_elec_trade:AL:AFR_OTH; more than 5000 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 452548956.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: The reporting country's ISO alpha-2 code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 and EA21 | none | text | for example AL, AT, BA; 39 distinct | 10020 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 198783 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Electricity trade with <partner>, not a pricing node | none | text | for example Electricity trade with Albania, Electricity trade with Algeria, Electricity trade with Andorra; 167 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_ti_eh_nrg_te_eh | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_te_eh?format=JSON&lang=EN&siec=E7000&sinceTimePeriod=2010, https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ti_eh?format=JSON&lang=EN&siec=E7000&sinceTimePeriod=2010 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T11:43:38Z, 2026-10-24T11:43:45Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 198783 |
| `x_geo_code` | Eurostat's geo code of the reporting country or aggregate | none | text | for example AL, AT, BA; 41 distinct | 0 |
| `x_partner` | Eurostat's partner code (a country, or an aggregate: TOTAL every partner, NSP not specified, _OTH groups; NA is Namibia) | none | text | for example AD, AE, AFR_OTH; 167 distinct | 0 |
| `x_partner_name` | Eurostat's name of the partner | none | text | for example Albania, Algeria, Andorra; 167 distinct | 0 |
| `x_flag` | Eurostat's status of the observation | none | empty | no cell holds a value | 198783: Not filled: no cell holds a value |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `exports` | Electricity exported to the partner, as the reporting country reports it | MWh | 99392 | 2010-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `imports` | Electricity imported from the partner, as the reporting country reports it | MWh | 99391 | 2010-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eurostat_electrification_rate_annual`

One European country's (or the EU's) rate of electrification of one end-use item (final consumption, a sector or branch, or the energy sector's own use) in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 38269.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_ind_re Eurostat, Rate of electrification by end-user (nrg_ind_re) (https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_re/default/table)
- **Method note:** [`docs/methods/eurostat_electrification_rate_annual.md`](../methods/eurostat_electrification_rate_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Rate of electrification by end-user (nrg_ind_re). Via the Energy Research Warehouse (ERW), table `eurostat_electrification_rate_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_electrification:<geo>:<NRG_BAL code> | none | text | for example eurostat_electrification:AL:FC_E, eurostat_electrification:AL:FC_IND_CON_E, eurostat_electrification:AL:FC_IND_CPC_E; 1319 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2023-01-01T00:00:00Z; 34 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 100.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 | none | text | for example AL, AT, BA; 38 distinct | 1399 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 38269 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> electrification rate, <the item's name>, not a pricing node | none | text | for example AL electrification rate, Energy sector - coke ovens - energy use, AL electrification rate, Energy sector - electricity and heat generation - energy use, AL electrification rate, Energy sector - energy use; 1319 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_ind_re | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_re?format=SDMX-CSV&compressed=false | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T04:34:41Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 38269 |
| `x_geo_code` | Eurostat's geo code of the country or aggregate | none | text | for example AL, AT, BA; 39 distinct | 0 |
| `x_nrg_bal` | Eurostat's NRG_BAL code of the end-use item (FC_E final consumption, FC_IND_E industry, NRG_E the energy sector and their parts) | none | text | for example FC_E, FC_IND_CON_E, FC_IND_CPC_E; 43 distinct | 0 |
| `x_flag` | Eurostat's flag of the observation | none | empty | no cell holds a value | 38269: Not filled: no cell holds a value |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 38269: Not filled: no cell holds a value |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `electrification_rate` | Electricity's share of the item's energy use, percent, as Eurostat gives it | pct | 38269 | 1990-01-01T00:00:00Z | 2023-01-01T00:00:00Z |

### `eurostat_ev_recharging_annual`

One European country's count or power output of electric vehicle recharging infrastructure of one kind in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 465.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:road_if_rchev Eurostat, Electric vehicle recharging pools, stations and points and their power output (road_if_rchev) (https://ec.europa.eu/eurostat/databrowser/view/road_if_rchev/default/table)
- **Method note:** [`docs/methods/eurostat_ev_recharging_annual.md`](../methods/eurostat_ev_recharging_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Electric vehicle recharging pools, stations and points and their power output (road_if_rchev). Via the Energy Research Warehouse (ERW), table `eurostat_ev_recharging_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_ev_recharging:<geo> | none | text | for example eurostat_ev_recharging:AT, eurostat_ev_recharging:BE, eurostat_ev_recharging:BG; 33 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 209513.0; 411 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2 | none | text | for example AT, BE, BG; 33 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 465 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> <the infrastructure's name>, <number or power output>, not a pricing node | none | text | for example AT Recharging point, number, AT Recharging pool, power output, AT Recharging station, number; 119 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:road_if_rchev | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/road_if_rchev?format=SDMX-CSV&compressed=false | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T03:30:12Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 465 |
| `x_geo_code` | Eurostat's geo code of the country | none | text | for example AT, BE, BG; 33 distinct | 0 |
| `x_tra_infr` | Eurostat's TRA_INFR code: RCHRG_PNT recharging point, RCHRG_STN station, RCHRG_POOL pool, RCHRG_POOL_HVY heavy-duty pool | none | text | RCHRG_PNT, RCHRG_POOL, RCHRG_POOL_HVY, RCHRG_STN | 0 |
| `x_unit` | Eurostat's unit code of the figure: NR a number, KW power output | none | text | KW, NR | 0 |
| `x_flag` | Eurostat's flag of the observation: b break in series; i (see Eurostat's metadata) | none | text | b, i | 428: No flag on the observation |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 465: Not filled: no cell holds a value |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `heavy_duty_pools` | Recharging pools for heavy-duty vehicles | count | 27 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `heavy_duty_pools_power` | Power output of the heavy-duty recharging pools, MW (Eurostat's kW divided by 1,000) | MW | 29 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `recharging_points` | Recharging points for electric vehicles | count | 157 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `recharging_pools` | Recharging pools | count | 81 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `recharging_pools_power` | Power output of the recharging pools, MW (Eurostat's kW divided by 1,000) | MW | 80 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `recharging_stations` | Recharging stations | count | 91 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

Waiting for a second look: x_flag: the meaning of Eurostat's flag i is not written in the repository (the method note says to see Eurostat's metadata).

### `eurostat_ev_recharging_power_annual`

One European country's recharging points for electric vehicles in one power category in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1171.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:road_if_rchevpow Eurostat, Recharging points for electric vehicles by power category (road_if_rchevpow) (https://ec.europa.eu/eurostat/databrowser/view/road_if_rchevpow/default/table)
- **Method note:** [`docs/methods/eurostat_ev_recharging_power_annual.md`](../methods/eurostat_ev_recharging_power_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Recharging points for electric vehicles by power category (road_if_rchevpow). Via the Energy Research Warehouse (ERW), table `eurostat_ev_recharging_power_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_ev_power:<geo>:<POWER code> | none | text | for example eurostat_ev_power:AT:AC, eurostat_ev_power:AT:AC_KW_GT22, eurostat_ev_power:AT:AC_KW_LE7P4-LE22; 277 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 209513.0; 851 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2 | none | text | for example AT, BE, BG; 33 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1171 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> recharging points, <the power category>, not a pricing node | none | text | for example AT recharging points, AC 7.4 to 22 kW (medium-speed, three-phase), AT recharging points, AC above 22 kW (fast, three-phase), AT recharging points, AC below 7.4 kW (slow, single-phase); 277 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:road_if_rchevpow | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/road_if_rchevpow?format=SDMX-CSV&compressed=false | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T05:21:38Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1171 |
| `x_geo_code` | Eurostat's geo code of the country | none | text | for example AT, BE, BG; 33 distinct | 0 |
| `x_power` | Eurostat's POWER code of the category: TOTAL, AC, DC, AC_KW_LT7P4 below 7.4 kW, AC_KW_LE7P4-LE22 7.4 to 22 kW, AC_KW_GT22 above 22 kW, DC_KW_LT50 below 50 kW, DC_KW_LE50-LT150 50 to 150 kW, DC_KW_LE150-LT350 150 to 350 kW, DC_KW_GE350 350 kW and above | none | text | AC, AC_KW_GT22, AC_KW_LE7P4-LE22, AC_KW_LT7P4, DC, DC_KW_GE350, DC_KW_LE150-LT350, DC_KW_LE50-LT150, DC_KW_LT50, TOTAL | 0 |
| `x_flag` | Eurostat's flag of the observation: b break in series; i (see Eurostat's metadata) | none | text | b, i | 1086: No flag on the observation |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 1171: Not filled: no cell holds a value |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `recharging_points` | Recharging points for electric vehicles in the power category | count | 1171 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

Waiting for a second look: x_flag: the meaning of Eurostat's flag i is not written in the repository (the method note says to see Eurostat's metadata).

### `eurostat_fossil_share_annual`

One European country's (or the EU's) share of fossil fuels in its gross available energy in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1279.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_ind_ffgae Eurostat, Share of fossil fuels in gross available energy (nrg_ind_ffgae) (https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_ffgae/default/table)
- **Method note:** [`docs/methods/eurostat_fossil_share_annual.md`](../methods/eurostat_fossil_share_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Share of fossil fuels in gross available energy (nrg_ind_ffgae). Via the Energy Research Warehouse (ERW), table `eurostat_fossil_share_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_fossil_share:<geo> | none | text | for example eurostat_fossil_share:AL, eurostat_fossil_share:AT, eurostat_fossil_share:BA; 39 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 35 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 12.06 to 103.79; 1125 distinct | 0 |
| `unit` | The unit of the row's value | none | text | pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 | none | text | for example AL, AT, BA; 38 distinct | 35 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1279 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> share of fossil fuels in gross available energy, not a pricing node | none | text | for example AL share of fossil fuels in gross available energy, AT share of fossil fuels in gross available energy, BA share of fossil fuels in gross available energy; 39 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_ind_ffgae | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_ffgae?format=SDMX-CSV&compressed=false | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T06:54:40Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1279 |
| `x_geo_code` | Eurostat's geo code of the country or aggregate | none | text | for example AL, AT, BA; 39 distinct | 0 |
| `x_flag` | Eurostat's flag of the observation | none | empty | no cell holds a value | 1279: Not filled: no cell holds a value |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 1279: Not filled: no cell holds a value |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `fossil_share_gross_available_energy` | Share of fossil fuels in gross available energy, percent | pct | 1279 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eurostat_gas_balance_monthly`

One European country's (or EU aggregate's) natural gas for one balance item (production, trade, stock change, consumption, losses) in one month.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 53214.

- **Time:** ts_utc is the month's first day at 00:00:00Z (freq P1M).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised month replaces the old figure, and a month Eurostat stops printing keeps its earlier value; vintage is not filled.
- **Source:** eurostat:nrg_cb_gasm Eurostat, Supply, transformation and consumption of gas, monthly data (nrg_cb_gasm) (https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_gasm/default/table)
- **Method note:** [`docs/methods/eurostat_gas_balance_monthly.md`](../methods/eurostat_gas_balance_monthly.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Supply, transformation and consumption of gas, monthly data (nrg_cb_gasm). Via the Energy Research Warehouse (ERW), table `eurostat_gas_balance_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_gas_balance:<geo> | none | text | for example eurostat_gas_balance:AL, eurostat_gas_balance:AT, eurostat_gas_balance:BE; 38 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-09-01T00:00:00Z; 141 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -250448694.444 to 675186016.389; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 and EA21 | none | text | for example AL, AT, BE; 36 distinct | 1724 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 53214 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> natural gas <NRG_BAL code>, not a pricing node | none | text | for example AL natural gas DL, AL natural gas EXP, AL natural gas FC_IND; 580 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_cb_gasm | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_gasm?format=SDMX-CSV&compressed=false&startPeriod=2015-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T07:26:34Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 53214 |
| `x_geo_code` | Eurostat's geo code of the country or aggregate | none | text | for example AL, AT, BE; 38 distinct | 0 |
| `x_nrg_bal` | Eurostat's NRG_BAL code of the balance item | none | text | DL, EXP, FC_IND, FC_OTH, FLARE, IC_CAL_MG, IC_OBS, IMP, INTMARB, IPRD, STATDIFF, STK_CHG_CG, STK_CHG_MG, TI_EHG_MAP, TOS, VENT | 0 |
| `x_flag` | Eurostat's flag of the observation: p provisional, e estimated, n not significant | none | text | e, n, p | 52784: No flag on the observation |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 53214: Not filled: no cell holds a value |

Variables (16):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `distribution_losses` | Distribution losses (DL), MWh of gross calorific value | MWh | 4542 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `exports` | Exports of natural gas (EXP), MWh of gross calorific value | MWh | 4679 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `final_consumption_industry` | Final consumption by industry (FC_IND), MWh of gross calorific value | MWh | 779 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `final_consumption_other` | Final consumption by other sectors (FC_OTH), MWh of gross calorific value | MWh | 854 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flared` | Gas flared (FLARE), MWh of gross calorific value | MWh | 2126 | 2017-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `imports` | Imports of natural gas (IMP), MWh of gross calorific value | MWh | 4848 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `indigenous_production` | Indigenous production of natural gas (NRG_BAL IPRD), MWh of gross calorific value | MWh | 4609 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `inland_consumption_calculated` | Inland consumption, calculated (IC_CAL_MG), MWh of gross calorific value | MWh | 4871 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `inland_consumption_observed` | Inland consumption, observed (IC_OBS), MWh of gross calorific value | MWh | 4868 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `international_maritime_bunkers` | International maritime bunkers (INTMARB), MWh of gross calorific value | MWh | 2484 | 2017-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `statistical_differences` | Statistical differences (STATDIFF), MWh of gross calorific value | MWh | 2787 | 2017-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `stock_change` | Stock change (STK_CHG_MG), MWh of gross calorific value | MWh | 4758 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `stock_change_cushion_gas` | Stock change of cushion gas (STK_CHG_CG), MWh of gross calorific value | MWh | 1485 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `transfer_from_other_sources` | Transfer from other sources (TOS), MWh of gross calorific value | MWh | 2585 | 2017-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `transformation_input_electricity_heat_main` | Transformation input to electricity and heat generation, main activity producers (TI_EHG_MAP), MWh of gross calorific value | MWh | 4813 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `vented` | Gas vented (VENT), MWh of gross calorific value | MWh | 2126 | 2017-01-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `eurostat_gas_import_origin_annual`

One European country's (or the EU's) natural gas import dependency on one country of origin in one year, 2015 to 2020.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1253.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_ind_idogas Eurostat, Natural gas import dependency by country of origin (nrg_ind_idogas) (https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_idogas/default/table)
- **Method note:** [`docs/methods/eurostat_gas_import_origin_annual.md`](../methods/eurostat_gas_import_origin_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Natural gas import dependency by country of origin (nrg_ind_idogas). Via the Energy Research Warehouse (ERW), table `eurostat_gas_import_origin_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_gas_origin:<geo>:<partner> | none | text | for example eurostat_gas_origin:BA:DZ, eurostat_gas_origin:BA:NG, eurostat_gas_origin:BA:NO; 224 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 100.0; 432 distinct | 0 |
| `unit` | The unit of the row's value | none | text | pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 | none | text | for example BA, BE, BG; 32 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1253 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> natural gas import dependency on <origin>, not a pricing node | none | text | for example BA natural gas import dependency on Algeria, BA natural gas import dependency on Nigeria, BA natural gas import dependency on Norway; 224 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_ind_idogas | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_idogas?format=SDMX-CSV&compressed=false | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T06:35:59Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1253 |
| `x_geo_code` | Eurostat's geo code of the country or aggregate | none | text | for example BA, BE, BG; 32 distinct | 0 |
| `x_partner` | Eurostat's code of the country of origin: DZ Algeria, NG Nigeria, NO Norway, QA Qatar, RU Russia, UK the United Kingdom, US the United States | none | text | DZ, NG, NO, QA, RU, UK, US | 0 |
| `x_flag` | Eurostat's flag of the observation: i on every row (see Eurostat's metadata) | none | text | i | 0 |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 1253: Not filled: no cell holds a value |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `import_dependency_by_origin` | Natural gas (G3000) import dependency on the country of origin, percent, as Eurostat gives it | pct | 1253 | 2015-01-01T00:00:00Z | 2020-01-01T00:00:00Z |

Waiting for a second look: x_flag: the meaning of Eurostat's flag i is not written in the repository (the header says to see Eurostat's metadata).

### `eurostat_gas_imports_monthly`

One European country's (or EU aggregate's) imports of natural gas or of LNG from one partner in one month.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 34905.

- **Time:** ts_utc is the month's first day at 00:00:00Z (freq P1M).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_ti_gasm Eurostat, Imports of natural gas by partner country, monthly data (nrg_ti_gasm) (https://ec.europa.eu/eurostat/databrowser/view/nrg_ti_gasm/default/table)
- **Method note:** [`docs/methods/eurostat_gas_imports_monthly.md`](../methods/eurostat_gas_imports_monthly.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Imports of natural gas by partner country, monthly data (nrg_ti_gasm). Via the Energy Research Warehouse (ERW), table `eurostat_gas_imports_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_gas_imports:<geo>:<SIEC>:<partner> | none | text | for example eurostat_gas_imports:AL:G3000:EL, eurostat_gas_imports:AL:G3000:NSP, eurostat_gas_imports:AL:G3000:TOTAL; 865 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-09-01T00:00:00Z; 141 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.278 to 673357583.333; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 and EA21 | none | text | for example AL, AT, BE; 34 distinct | 7531 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 34905 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> <SIEC> from <partner>, not a pricing node | none | text | for example AL G3000 from EL, AL G3000 from NSP, AL G3000 from TOTAL; 865 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_ti_gasm | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/1.0/async/data/7330e3ef-4d8a-41e6-af23-bdfd15c46fd7 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T01:40:51Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 34905 |
| `x_geo_code` | Eurostat's geo code of the importing country or aggregate | none | text | for example AL, AT, BE; 36 distinct | 0 |
| `x_siec` | Eurostat's SIEC code: G3000 natural gas, G3200 liquefied natural gas (a part of G3000) | none | text | G3000, G3200 | 0 |
| `x_partner` | Eurostat's partner code (a country or an aggregate such as TOTAL, NSP not specified, _OTH groups) | none | text | for example AFR_OTH, AL, AME_OTH; 78 distinct | 0 |
| `x_flag` | Eurostat's flag of the observation: e estimated, p provisional | none | text | e, p | 34751: No flag on the observation |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 34905: Not filled: no cell holds a value |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `imports` | Gas imported from the partner, MWh of gross calorific value (Eurostat's TJ times 277.7778) | MWh | 34905 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `eurostat_hard_coal_imports_annual`

One European country's (or EU aggregate's) hard coal imports from one partner in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 99288.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_ti_sff_c0100 Eurostat, Solid fossil fuels imports (nrg_ti_sff), hard coal (C0100) (https://ec.europa.eu/eurostat/databrowser/view/nrg_ti_sff/default/table)
- **Method note:** [`docs/methods/eurostat_hard_coal_imports_annual.md`](../methods/eurostat_hard_coal_imports_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Solid fossil fuels imports (nrg_ti_sff), hard coal by partner. Via the Energy Research Warehouse (ERW), table `eurostat_hard_coal_imports_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_coal_imp:<Eurostat geo code>:<partner code> | none | text | for example eurostat_coal_imp:AL:AD, eurostat_coal_imp:AL:AE, eurostat_coal_imp:AL:AFR_OTH; more than 5000 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 175699086.0; 3994 distinct | 0 |
| `unit` | The unit of the row's value | none | text | t | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: The importing country's ISO alpha-2 code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 and EA21 | none | text | for example AL, AT, BA; 39 distinct | 5010 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 99288 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Hard coal imports from <partner>, not a pricing node | none | text | for example Hard coal imports from Albania, Hard coal imports from Algeria, Hard coal imports from Andorra; 167 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_ti_sff_c0100 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ti_sff?format=JSON&lang=EN&siec=C0100&sinceTimePeriod=2010 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T11:22:52Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 99288 |
| `x_geo_code` | Eurostat's geo code of the importing country or aggregate | none | text | for example AL, AT, BA; 41 distinct | 0 |
| `x_partner` | Eurostat's partner code (a country, or an aggregate: TOTAL every partner, NSP not specified, _OTH groups; NA is Namibia) | none | text | for example AD, AE, AFR_OTH; 167 distinct | 0 |
| `x_partner_name` | Eurostat's name of the partner | none | text | for example Albania, Algeria, Andorra; 167 distinct | 0 |
| `x_flag` | Eurostat's status of the observation | none | empty | no cell holds a value | 99288: Not filled: no cell holds a value |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `imports` | Hard coal (SIEC C0100) imported from the partner, tonnes (Eurostat's thousand tonnes times 1,000) | t | 99288 | 2010-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eurostat_household_electricity_annual`

One European country's (or the EU's) household electricity consumption, in total or for one end use, in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3150.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_d_hhq Eurostat, Disaggregated final energy consumption in households, quantities (nrg_d_hhq) (https://ec.europa.eu/eurostat/databrowser/view/nrg_d_hhq/default/table)
- **Method note:** [`docs/methods/eurostat_household_electricity_annual.md`](../methods/eurostat_household_electricity_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Disaggregated final energy consumption in households, quantities (nrg_d_hhq). Via the Energy Research Warehouse (ERW), table `eurostat_household_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_household_electricity:<geo> | none | text | for example eurostat_household_electricity:AL, eurostat_household_electricity:AT, eurostat_household_electricity:BA; 38 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 739394380.0; 2739 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 | none | text | for example AL, AT, BA; 37 distinct | 105 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 3150 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> households' electricity, <the NRG_BAL name>, not a pricing node | none | text | for example AL households' electricity, Final consumption - other sectors - households - energy use, AL households' electricity, Final consumption - other sectors - households - energy use - cooking, AL households' electricity, Final consumption - other sectors - households - energy use - lighting and electrical appliances; 266 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_d_hhq | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_d_hhq/A..E7000.GWH.?format=SDMX-CSV&compressed=false&startPeriod=1990 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T03:16:41Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 3150 |
| `x_geo_code` | Eurostat's geo code of the country or aggregate | none | text | for example AL, AT, BA; 38 distinct | 0 |
| `x_nrg_bal` | Eurostat's NRG_BAL code of the end use | none | text | FC_OTH_HH_E, FC_OTH_HH_E_CK, FC_OTH_HH_E_LE, FC_OTH_HH_E_OE, FC_OTH_HH_E_SC, FC_OTH_HH_E_SH, FC_OTH_HH_E_WH | 0 |
| `x_flag` | Eurostat's flag of the observation: e estimated, b break in series | none | text | b, e | 3067: No flag on the observation |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 3150: Not filled: no cell holds a value |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `cooking` | Households' electricity for cooking (FC_OTH_HH_E_CK) | MWh | 451 | 2010-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `lighting_appliances` | Households' electricity for lighting and appliances (FC_OTH_HH_E_LE) | MWh | 451 | 2010-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `other_end_use` | Households' electricity for other end uses (FC_OTH_HH_E_OE) | MWh | 444 | 2010-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `space_cooling` | Households' electricity for space cooling (FC_OTH_HH_E_SC) | MWh | 451 | 2010-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `space_heating` | Households' electricity for space heating (FC_OTH_HH_E_SH) | MWh | 451 | 2010-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `total` | Households' final consumption of electricity, all end uses (FC_OTH_HH_E) | MWh | 451 | 2010-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `water_heating` | Households' electricity for water heating (FC_OTH_HH_E_WH) | MWh | 451 | 2010-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eurostat_import_concentration_annual`

One EU country's import origin concentration index for one fuel in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 6497.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_ind_ioc Eurostat, Energy import origin concentration index by fuel (nrg_ind_ioc) (https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_ioc/default/table)
- **Method note:** [`docs/methods/eurostat_import_concentration_annual.md`](../methods/eurostat_import_concentration_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Energy import origin concentration index by fuel (nrg_ind_ioc). Via the Energy Research Warehouse (ERW), table `eurostat_import_concentration_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_ioc:<geo>:<SIEC code> | none | text | for example eurostat_ioc:AT:C0110, eurostat_ioc:AT:C0121, eurostat_ioc:AT:C0129; 713 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0544 to 1.0; 3745 distinct | 0 |
| `unit` | The unit of the row's value | none | text | index | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2 | none | text | for example AT, BE, BG; 27 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 6497 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> import origin concentration, <the fuel's name>, not a pricing node | none | text | for example AT import origin concentration, Anthracite, AT import origin concentration, Aviation gasoline, AT import origin concentration, Bitumen; 713 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_ind_ioc | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_ioc?format=SDMX-CSV&compressed=false | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T06:59:06Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 6497 |
| `x_geo_code` | Eurostat's geo code of the country | none | text | for example AT, BE, BG; 27 distinct | 0 |
| `x_siec` | Eurostat's SIEC code of the fuel | none | text | for example C0110, C0121, C0129; 43 distinct | 0 |
| `x_flag` | Eurostat's flag of the observation | none | empty | no cell holds a value | 6497: Not filled: no cell holds a value |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 6497: Not filled: no cell holds a value |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `import_origin_concentration` | Energy import origin concentration index: 0 for imports spread over many origins, 1 for one origin | index | 6497 | 2015-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eurostat_import_dependency_annual`

One European country's (or the EU's) import dependency for one fuel (SIEC product) in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 16627.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_ind_id Eurostat, Energy imports dependency (nrg_ind_id) (https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_id/default/table)
- **Method note:** [`docs/methods/eurostat_import_dependency_annual.md`](../methods/eurostat_import_dependency_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Energy imports dependency (nrg_ind_id). Via the Energy Research Warehouse (ERW), table `eurostat_import_dependency_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_import_dependency:<geo>:<SIEC> | none | text | for example eurostat_import_dependency:AL:C0000X0350-0370, eurostat_import_dependency:AL:C0110, eurostat_import_dependency:AL:C0121; 507 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 35 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -31930.25 to 3600.913; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 | none | text | for example AL, AT, BA; 38 distinct | 455 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 16627 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> import dependency, <the SIEC product's name>, not a pricing node | none | text | for example AL import dependency, Anthracite, AL import dependency, Coking coal, AL import dependency, Crude oil; 507 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_ind_id | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_id/A...?format=SDMX-CSV&compressed=false | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T02:04:16Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 16627 |
| `x_geo_code` | Eurostat's geo code of the country or aggregate | none | text | for example AL, AT, BA; 39 distinct | 0 |
| `x_siec` | Eurostat's SIEC product code of the fuel | none | text | C0000X0350-0370, C0110, C0121, C0129, C0210, C0220, G3000, O4000XBIO, O4100_TOT, O4200, P1100, S2000, TOTAL | 0 |
| `x_flag` | Eurostat's flag of the observation | none | empty | no cell holds a value | 16627: Not filled: no cell holds a value |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 16627: Not filled: no cell holds a value |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `import_dependency` | Net imports over gross available energy, times 100; negative for a net exporter | pct | 16627 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eurostat_industry_electricity_annual`

One European country's (or the EU's) electricity consumption of one industrial activity (NACE Rev. 2) in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 8307.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_d_indq_n Eurostat, Energy consumption in industry by NACE Rev. 2 activity, quantities (nrg_d_indq_n) (https://ec.europa.eu/eurostat/databrowser/view/nrg_d_indq_n/default/table)
- **Method note:** [`docs/methods/eurostat_industry_electricity_annual.md`](../methods/eurostat_industry_electricity_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Energy consumption in industry by NACE Rev. 2 activity, quantities (nrg_d_indq_n). Via the Energy Research Warehouse (ERW), table `eurostat_industry_electricity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_industry_electricity:<geo>:<NACE code>; the activities overlap, do not sum them | none | text | for example eurostat_industry_electricity:AL:B07-B09_X_EPRD, eurostat_industry_electricity:AL:B07_X_B0721, eurostat_industry_electricity:AL:B08_X_B0892; 1507 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 219328000.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 | none | text | for example AL, AT, BE; 33 distinct | 39 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 8307 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> industry electricity, <the activity's name>, not a pricing node | none | text | for example AL industry electricity, Aluminium production, AL industry electricity, Construction, AL industry electricity, Manufacture of basic metals; 1507 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_d_indq_n | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_d_indq_n/A.GWH.E7000..?format=SDMX-CSV&compressed=false | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T05:28:27Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 8307 |
| `x_geo_code` | Eurostat's geo code of the country or aggregate | none | text | for example AL, AT, BE; 34 distinct | 0 |
| `x_nace_r2` | Eurostat's NACE Rev. 2 code of the activity (divisions, their groups and aggregates) | none | text | for example B07-B09_X_EPRD, B07_X_B0721, B08_X_B0892; 55 distinct | 0 |
| `x_flag` | Eurostat's flag of the observation: e estimated, b break in series, d definition differs | none | text | b, d, e | 7941: No flag on the observation |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 8307: Not filled: no cell holds a value |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `electricity_consumption` | Electricity consumed by the activity, MWh (Eurostat's GWh times 1,000) | MWh | 8307 | 2017-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eurostat_nonhousehold_bands_annual`

One European country's (or EU aggregate's) share of non-household electricity consumption in one annual consumption band in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2013.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_pc_205_v Eurostat, Non-household consumption volumes of electricity by consumption bands (nrg_pc_205_v) (https://ec.europa.eu/eurostat/databrowser/view/nrg_pc_205_v/default/table)
- **Method note:** [`docs/methods/eurostat_nonhousehold_bands_annual.md`](../methods/eurostat_nonhousehold_bands_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Non-household consumption volumes of electricity by consumption bands (nrg_pc_205_v). Via the Energy Research Warehouse (ERW), table `eurostat_nonhousehold_bands_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_nonhh_bands:<geo>:<band> | none | text | for example eurostat_nonhh_bands:AL:MWH20-499, eurostat_nonhh_bands:AL:MWH2000-19999, eurostat_nonhh_bands:AL:MWH20000-69999; 253 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 84.1; 1658 distinct | 0 |
| `unit` | The unit of the row's value | none | text | pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2 | none | text | for example AL, AT, BA; 37 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 2013 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> non-household electricity, <the band>, not a pricing node | none | text | for example AL non-household electricity, band IA, less than 20 MWh a year, AL non-household electricity, band IB, 20 to 499 MWh, AL non-household electricity, band IC, 500 to 1,999 MWh; 253 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_pc_205_v | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_pc_205_v?format=SDMX-CSV&compressed=false | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T06:30:20Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 2013 |
| `x_geo_code` | Eurostat's geo code of the country or aggregate (EU27_2020, EA) | none | text | for example AL, AT, BA; 37 distinct | 0 |
| `x_nrg_cons` | Eurostat's consumption band code: MWH_LT20 (IA, under 20 MWh a year), MWH20-499 (IB), MWH500-1999 (IC), MWH2000-19999 (ID), MWH20000-69999 (IE), MWH70000-149999 (IF), MWH_GE150000 (IG, 150,000 MWh and over) | none | text | MWH20-499, MWH2000-19999, MWH20000-69999, MWH500-1999, MWH70000-149999, MWH_GE150000, MWH_LT20 | 0 |
| `x_flag` | Eurostat's flag of the observation: e estimated | none | text | e | 1931: No flag on the observation |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 2013: Not filled: no cell holds a value |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption_share` | The band's share of the country's non-household electricity consumption, percent | pct | 2013 | 2017-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `eurostat_nuclear_fuel_cycle_annual`

One European country's (or the EU's) value of one nuclear fuel cycle measure (enrichment, fuel fabrication, reprocessing, nuclear heat) in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 4247.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_inf_nuc Eurostat, Nuclear energy facilities (nrg_inf_nuc) (https://ec.europa.eu/eurostat/databrowser/view/nrg_inf_nuc/default/table)
- **Method note:** [`docs/methods/eurostat_nuclear_fuel_cycle_annual.md`](../methods/eurostat_nuclear_fuel_cycle_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Nuclear energy facilities (nrg_inf_nuc). Via the Energy Research Warehouse (ERW), table `eurostat_nuclear_fuel_cycle_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_nuclear:<geo> | none | text | for example eurostat_nuclear:AL, eurostat_nuclear:AT, eurostat_nuclear:BA; 40 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 2554188950.34; 421 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, SWU, t | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 | none | text | for example AL, AT, BA; 39 distinct | 128 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 4247 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> nuclear facilities, <the measure's name>, not a pricing node | none | text | for example AL nuclear facilities, Capacity (uranium and plutonium) of reprocessing plants (tHM), AL nuclear facilities, Enrichment capacity (tSWU), AL nuclear facilities, Production capacity of MOX fuel fabrication plants (tHM); 313 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_inf_nuc | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_inf_nuc?format=SDMX-CSV&compressed=false | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T05:15:23Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 4247 |
| `x_geo_code` | Eurostat's geo code of the country or aggregate | none | text | for example AL, AT, BA; 40 distinct | 0 |
| `x_plant_tec` | Eurostat's PLANT_TEC code of the measure (CAP_EN, PRD_FF, PRDCAP_FF, PRD_MOXF, PRDCAP_MOXF, PRD_UP, CAP_UP, PRD_NUCH) | none | text | CAP_EN, CAP_UP, PRDCAP_FF, PRDCAP_MOXF, PRD_FF, PRD_MOXF, PRD_NUCH, PRD_UP | 0 |
| `x_unit` | Eurostat's unit code of the figure as published: TSWU tonnes of separative work, THM tonnes of heavy metal, KTOE thousand tonnes of oil equivalent | none | text | KTOE, THM, TSWU | 0 |
| `x_flag` | Eurostat's flag of the observation: p provisional | none | text | p | 4246: No flag on the observation |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 4247: Not filled: no cell holds a value |

Variables (8):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `enrichment_capacity` | Enrichment capacity, separative work units (Eurostat's tSWU times 1,000; CAP_EN) | SWU | 541 | 2009-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `fresh_fuel_production` | Production of fresh fuel elements, tonnes of heavy metal (PRD_FF) | t | 531 | 2009-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `fresh_fuel_production_capacity` | Production capacity of fresh fuel elements, tonnes of heavy metal (PRDCAP_FF) | t | 531 | 2009-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `mox_fuel_production` | Production of MOX fuel elements, tonnes of heavy metal (PRD_MOXF) | t | 521 | 2009-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `mox_fuel_production_capacity` | Production capacity of MOX fuel fabrication plants, tonnes of heavy metal (PRDCAP_MOXF) | t | 521 | 2009-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `nuclear_heat_production` | Production of nuclear heat, MWh (Eurostat's ktoe times 11,630; PRD_NUCH) | MWh | 560 | 2009-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `reprocessing_capacity` | Capacity (uranium and plutonium) of reprocessing plants, tonnes of heavy metal (CAP_UP) | t | 521 | 2009-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `reprocessing_production` | Production of uranium and plutonium in reprocessing plants, tonnes of heavy metal (PRD_UP) | t | 521 | 2009-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eurostat_oil_monthly`

One European country's (or the EU's) flow of one oil product (crude oil, oil products, motor gasoline, gas and diesel oil, jet fuel, fuel oil, LPG) in one month.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 457009.

- **Time:** ts_utc is the month's first day at 00:00:00Z (freq P1M).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_cb_oilm Eurostat, Supply and transformation of oil and petroleum products - monthly data (nrg_cb_oilm) (https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_oilm/default/table)
- **Method note:** [`docs/methods/eurostat_oil_monthly.md`](../methods/eurostat_oil_monthly.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Supply and transformation of oil and petroleum products - monthly data (nrg_cb_oilm). Via the Energy Research Warehouse (ERW), table `eurostat_oil_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_oil:<Eurostat geo code>:<SIEC code> | none | text | for example eurostat_oil:AL:O4100_TOT, eurostat_oil:AL:O4600, eurostat_oil:AL:O4630; 252 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2016-01-01T00:00:00Z to 2026-09-01T00:00:00Z; 129 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -23830282.0 to 52091000.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | t | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 | none | text | for example AL, AT, BE; 35 distinct | 14959 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 457009 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <product>: <flow>, not a pricing node | none | text | for example Crude oil: Backflows, Crude oil: Change in stock, Crude oil: Direct use; 143 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_cb_oilm | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_oilm?format=SDMX-CSV&compressed=false&startPeriod=2016-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T08:51:54Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 457009 |
| `x_geo_code` | Eurostat's geo code of the country or aggregate | none | text | for example AL, AT, BE; 36 distinct | 0 |
| `x_siec` | Eurostat's SIEC code of the product: O4100_TOT crude oil, O4600 oil products, O4652XR5210B motor gasoline, O4671XR5220B gas oil and diesel oil, O4661XR5230B kerosene-type jet fuel (each without its biofuel portion), O4680 fuel oil, O4630 LPG | none | text | O4100_TOT, O4600, O4630, O4652XR5210B, O4661XR5230B, O4671XR5220B, O4680 | 0 |
| `x_nrg_bal` | Eurostat's NRG_BAL code of the flow (the part of the variable after flow:) | none | text | for example BKFLOW, DU, EXP; 26 distinct | 0 |
| `x_flag` | Eurostat's flag of the observation: p provisional, e estimated | none | text | e, p | 450288: No flag on the observation |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 457009: Not filled: no cell holds a value |

Variables (26):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `flow:BKFLOW` | Backflows of the product, tonnes (NRG_BAL BKFLOW) | t | 24335 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:DU` | Direct use, tonnes (DU) | t | 3894 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:EXP` | Exports, tonnes (EXP) | t | 29449 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:FC_TRA_RAIL_DNAVI_E` | Final consumption by rail and domestic navigation, energy use, tonnes (FC_TRA_RAIL_DNAVI_E) | t | 3905 | 2019-04-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:FC_TRA_ROAD_E` | Final consumption by road transport, energy use, tonnes (FC_TRA_ROAD_E) | t | 5431 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:GD_PI` | Gross deliveries to the petrochemical industry, tonnes (GD_PI) | t | 28037 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:GID_CAL` | Gross inland deliveries, calculated, tonnes (GID_CAL) | t | 26861 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:GID_OBS` | Gross inland deliveries, observed, tonnes (GID_OBS) | t | 29680 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:IMP` | Imports, tonnes (IMP) | t | 29889 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:INTAVI_E` | International aviation, energy use, tonnes (INTAVI_E) | t | 5592 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:INTMARB` | International maritime bunkers, tonnes (INTMARB) | t | 24588 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:IPRD` | Indigenous production, tonnes (IPRD) | t | 4176 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:IT` | Interproduct transfers, tonnes (IT) | t | 27883 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:ND_TP` | Net deliveries of total products, tonnes (ND_TP) | t | 4496 | 2018-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:PPR` | Primary product receipts, tonnes (PPR) | t | 27817 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:PT` | Products transferred, tonnes (PT) | t | 25010 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:RCV_RCY` | Recovered and recycled products, tonnes (RCV_RCY) | t | 23891 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:RF` | Refinery fuel, tonnes (RF) | t | 24405 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:RI_CAL` | Refinery intake, calculated, tonnes (RI_CAL) | t | 2788 | 2018-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:RI_OBS` | Refinery intake, observed, tonnes (RI_OBS) | t | 4230 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:RL` | Refinery losses, tonnes (RL) | t | 4180 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:STATDIFF` | Statistical differences, tonnes (STATDIFF) | t | 18583 | 2018-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:STK_CHG` | Change in stock, tonnes (STK_CHG) | t | 29926 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:TI_EHG_MAP` | Transformation input to electricity and heat generation, main activity producers, tonnes (TI_EHG_MAP) | t | 22094 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:TOS` | Transfer from other sources, tonnes (TOS) | t | 378 | 2020-12-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `flow:TO_RPI_RO` | Transformation output, refinery output, tonnes (TO_RPI_RO) | t | 25491 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `eurostat_renewable_capacity_annual`

One European country's (or EU aggregate's) net electricity capacity of one renewable (or waste) fuel in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 49313.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_inf_epcrw Eurostat, Electricity production capacities for renewables and wastes (nrg_inf_epcrw) (https://ec.europa.eu/eurostat/databrowser/view/nrg_inf_epcrw/default/table)
- **Method note:** [`docs/methods/eurostat_renewable_capacity_annual.md`](../methods/eurostat_renewable_capacity_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Electricity production capacities for renewables and wastes (nrg_inf_epcrw). Via the Energy Research Warehouse (ERW), table `eurostat_renewable_capacity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_epcrw:<Eurostat geo code>:<SIEC code> | none | text | for example eurostat_epcrw:AL:R5100, eurostat_epcrw:AL:R5210P, eurostat_epcrw:AL:R5220P; 1369 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1990-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 35 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 309405.458; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 and EA21 | none | text | for example AL, AT, BA; 39 distinct | 3024 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 49313 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The SIEC code's English name, not a pricing node | none | text | for example Biogases, Geothermal, Hydro; 34 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_inf_epcrw | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_inf_epcrw?format=SDMX-CSV&compressed=false | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T22:50:58Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 49313 |
| `x_geo_code` | Eurostat's geo code of the country or aggregate | none | text | for example AL, AT, BA; 41 distinct | 0 |
| `x_siec` | Eurostat's SIEC code of the fuel | none | text | for example R5100, R5210P, R5220P; 34 distinct | 0 |
| `x_plant_tec` | Eurostat's capacity code: CAP_NET_ELC net capacity; CAP_NET_ELC_AC and CAP_NET_ELC_DC solar photovoltaic's two ratings | none | text | CAP_NET_ELC, CAP_NET_ELC_AC, CAP_NET_ELC_DC | 0 |
| `x_flag` | Eurostat's flag of the observation | none | empty | no cell holds a value | 49313: Not filled: no cell holds a value |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 49313: Not filled: no cell holds a value |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `net_capacity` | Net maximum electrical capacity | MW | 36400 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_capacity_ac` | Solar photovoltaic net capacity, AC rating | MW | 6457 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `net_capacity_dc` | Solar photovoltaic net capacity, DC rating | MW | 6456 | 1990-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eurostat_renewable_shares_annual`

One European country's (or the EU's) renewable share of gross final energy consumption, overall or for one sector, in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3095.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_ind_ren Eurostat, Share of energy from renewable sources (nrg_ind_ren) (https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_ren/default/table)
- **Method note:** [`docs/methods/eurostat_renewable_shares_annual.md`](../methods/eurostat_renewable_shares_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Share of energy from renewable sources (nrg_ind_ren). Via the Energy Research Warehouse (ERW), table `eurostat_renewable_shares_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_renewable_shares:<geo> | none | text | for example eurostat_renewable_shares:AL, eurostat_renewable_shares:AT, eurostat_renewable_shares:BA; 37 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2004-01-01T00:00:00Z, 2005-01-01T00:00:00Z, 2006-01-01T00:00:00Z, 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 122.0; 2950 distinct | 0 |
| `unit` | The unit of the row's value | none | text | pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 | none | text | for example AL, AT, BA; 36 distinct | 95 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 3095 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> share, <the item's name>, not a pricing node | none | text | for example AL share, Renewable energy - electricity, AL share, Renewable energy - heating and cooling, AL share, Renewable energy - overall; 163 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_ind_ren | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_ren/A...?format=SDMX-CSV&compressed=false | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-25T22:32:49Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 3095 |
| `x_geo_code` | Eurostat's geo code of the country or aggregate | none | text | for example AL, AT, BA; 37 distinct | 0 |
| `x_nrg_bal` | Eurostat's NRG_BAL code of the share (REN, REN_ELC, REN_HEAT_CL, REN_TRA, REN_WHC_DHEAT_DCL, REN_HEAT_CL_WHC) | none | text | REN, REN_ELC, REN_HEAT_CL, REN_HEAT_CL_WHC, REN_TRA, REN_WHC_DHEAT_DCL | 0 |
| `x_flag` | Eurostat's flag of the observation: p provisional | none | text | p | 3032: No flag on the observation |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 3095: Not filled: no cell holds a value |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `renewable_share_electricity` | Renewable share of gross final consumption of electricity (REN_ELC) | pct | 774 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `renewable_share_heating_cooling` | Renewable share of gross final consumption for heating and cooling (REN_HEAT_CL) | pct | 744 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `renewable_share_overall` | Renewable share of gross final energy consumption, overall (REN), Eurostat's directive method | pct | 774 | 2004-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `renewable_share_transport` | Renewable share of gross final consumption in transport (REN_TRA), with the directive's multipliers | pct | 743 | 2004-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `renewable_waste_heat_share_district_heating_cooling` | Renewable and waste heat share of district heating and cooling (REN_WHC_DHEAT_DCL) | pct | 32 | 2021-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `waste_heat_share_heating_cooling` | Waste heat share of heating and cooling (REN_HEAT_CL_WHC) | pct | 28 | 2021-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `eurostat_solid_fuels_monthly`

One European country's (or the EU's) flow of one solid fuel (hard coal, brown coal, coke oven coke, peat, oil shale and oil sands) in one month.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 209040.

- **Time:** ts_utc is the month's first day at 00:00:00Z (freq P1M).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised month replaces the old figure; vintage is not filled.
- **Source:** eurostat:nrg_cb_sffm Eurostat, Supply and transformation of solid fuels - monthly data (nrg_cb_sffm) (https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_sffm/default/table)
- **Method note:** [`docs/methods/eurostat_solid_fuels_monthly.md`](../methods/eurostat_solid_fuels_monthly.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Supply and transformation of solid fuels - monthly data (nrg_cb_sffm). Via the Energy Research Warehouse (ERW), table `eurostat_solid_fuels_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_sff:<Eurostat geo code>:<SIEC code> | none | text | for example eurostat_sff:AL:C0100, eurostat_sff:AL:C0200, eurostat_sff:AL:C0311; 190 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2016-01-01T00:00:00Z to 2026-09-01T00:00:00Z; 129 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -2828701.0 to 42801000.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | t | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2; empty for EU27_2020 | none | text | for example AL, AT, BA; 37 distinct | 5681 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 209040 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <fuel>: <flow>, not a pricing node | none | text | for example Brown coal: Change in stock, Brown coal: Closing stocks on national territory, Brown coal: Exports; 49 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_cb_sffm | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_sffm?format=SDMX-CSV&compressed=false&startPeriod=2016-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T08:58:15Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 209040 |
| `x_geo_code` | Eurostat's geo code of the country or aggregate | none | text | for example AL, AT, BA; 38 distinct | 0 |
| `x_siec` | Eurostat's SIEC code of the fuel: C0100 hard coal, C0200 brown coal, C0311 coke oven coke, P1100 peat, S2000 oil shale and oil sands | none | text | C0100, C0200, C0311, P1100, S2000 | 0 |
| `x_nrg_bal` | Eurostat's NRG_BAL code of the flow (the part of the variable after flow:) | none | text | EXP, FC_IND, FC_IND_IS, FC_OTH, GID_CAL, GID_OBS, IMP, IMP_FROM_NEU, IPRD, RCV_RCY, STATDIFF, STKCL_NAT, STKOP_NAT, STK_CHG, TI_CO, TI_EHG_MAP | 0 |
| `x_flag` | Eurostat's flag of the observation: e estimated, n not significant, p provisional, b break in series, d definition differs, u low reliability, and the pairs be and bn | none | text | b, be, bn, d, e, n, p, u | 202168: No flag on the observation |
| `x_conf_status` | Eurostat's confidentiality status of the observation: C confidential | none | text | C | 209034: Not confidential |

Variables (16):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `flow:EXP` | Exports, tonnes (NRG_BAL EXP) | t | 22238 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:FC_IND` | Final consumption by the industry sector, tonnes (FC_IND) | t | 4358 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:FC_IND_IS` | Final consumption by iron and steel, tonnes (FC_IND_IS) | t | 8685 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:FC_OTH` | Final consumption by other sectors, tonnes (FC_OTH) | t | 4442 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:GID_CAL` | Gross inland deliveries, calculated, tonnes (GID_CAL) | t | 22450 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:GID_OBS` | Gross inland deliveries, observed, tonnes (GID_OBS) | t | 4199 | 2017-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:IMP` | Imports, tonnes (IMP) | t | 22435 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:IMP_FROM_NEU` | Imports from outside the EU, tonnes (IMP_FROM_NEU) | t | 8161 | 2017-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:IPRD` | Indigenous production, tonnes (IPRD) | t | 22239 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:RCV_RCY` | Recovered and recycled products, tonnes (RCV_RCY) | t | 4575 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:STATDIFF` | Statistical differences, tonnes (STATDIFF) | t | 4192 | 2017-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:STKCL_NAT` | Closing stocks on national territory, tonnes (STKCL_NAT) | t | 18173 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:STKOP_NAT` | Opening stocks on national territory, tonnes (STKOP_NAT) | t | 18174 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:STK_CHG` | Change in stock, tonnes (STK_CHG) | t | 22429 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:TI_CO` | Transformation input to coke ovens, tonnes (TI_CO) | t | 4413 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `flow:TI_EHG_MAP` | Transformation input to electricity and heat generation, main activity producers, tonnes (TI_EHG_MAP) | t | 17877 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `eurostat_supply_diversity_annual`

One EU country's diversity index of energy supply in one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 891.

- **Time:** ts_utc is the year's 1 January at 00:00:00Z, a label for the calendar year (freq P1Y).
- **Revisions:** Merged by key (entity, variable, ts_utc): a revised figure replaces the old; vintage is not filled.
- **Source:** eurostat:nrg_ind_di Eurostat, Diversity index of energy supply (nrg_ind_di) (https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_di/default/table)
- **Method note:** [`docs/methods/eurostat_supply_diversity_annual.md`](../methods/eurostat_supply_diversity_annual.md)
- **Cite as:** Eurostat (Statistical Office of the European Union). Diversity index of energy supply (nrg_ind_di). Via the Energy Research Warehouse (ERW), table `eurostat_supply_diversity_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eurostat_supply_diversity:<geo> | none | text | for example eurostat_supply_diversity:AT, eurostat_supply_diversity:BE, eurostat_supply_diversity:BG; 27 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1992-01-01T00:00:00Z to 2024-01-01T00:00:00Z; 33 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.1166 to 0.5504; 715 distinct | 0 |
| `unit` | The unit of the row's value | none | text | index | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: ISO alpha-2 country code (Eurostat's EL written GR), not ISO 3166-2 | none | text | for example AT, BE, BG; 27 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 891 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: <geo> diversity index of energy supply, not a pricing node | none | text | for example AT diversity index of energy supply, BE diversity index of energy supply, BG diversity index of energy supply; 27 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eurostat:nrg_ind_di | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_di?format=SDMX-CSV&compressed=false | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-26T07:04:02Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 891 |
| `x_geo_code` | Eurostat's geo code of the country | none | text | for example AT, BE, BG; 27 distinct | 0 |
| `x_flag` | Eurostat's flag of the observation | none | empty | no cell holds a value | 891: Not filled: no cell holds a value |
| `x_conf_status` | Eurostat's confidentiality status of the observation | none | empty | no cell holds a value | 891: Not filled: no cell holds a value |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `supply_diversity_index` | Eurostat's diversity index of energy supply (INX), as given; the ERW reads no direction into it | index | 891 | 1992-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

Waiting for a second look: supply_diversity_index: the file gives the index without its method; Eurostat's metadata for nrg_ind_di defines it, and the repository does not.

