# Codebook: erw_derived

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 30 public tables (2 entities, 3 events, 25 series; tiers: 25 derived, 5 model_extracted); 0 documented in full.

- [`ai_power_regions`](#ai_power_regions): where the next gigawatts for AI can come from, one row of measures per ISO region (derived, session 62)
- [`attention_index_weekly`](#attention_index_weekly): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261116T092425Z-local (2026-11-16T09:24:25Z); that run's own header of the table follows
- [`attention_story_links`](#attention_story_links): the stories behind the Attention and Friction indices, one row a classified story (session 3402)
- [`clean_energy_hourly`](#clean_energy_hourly): the carbon-free share of each grid's generation by hour, the seven ISO grids (derived, session 122)
- [`clean_energy_summary`](#clean_energy_summary): how clean each grid's generation is by month and year, what an annual clean purchase covers hour by hour, and what moving load into the cleanest hours changes (derived, session 122)
- [`deal_counterparties`](#deal_counterparties): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261113T155514Z-github (2026-11-13T15:55:14Z); that run's own header of the table follows
- [`event_study_estimates`](#event_study_estimates): event studies, the estimated effect of each event on each grid's daily demand served and ERCOT's daily hub price (derived, research, session 47)
- [`event_window_daily`](#event_window_daily): event windows, daily figures around an event and the same calendar days of earlier years (Historical Event Analyzer v0, derived, session 36B)
- [`flex_alert_effects`](#flex_alert_effects): the Flex Alert scorecard, per alert day, CAISO (derived, session 60)
- [`flex_alert_model`](#flex_alert_model): the Flex Alert scorecard's model, CAISO (derived, session 60)
- [`forecast_tool_parameters`](#forecast_tool_parameters): the forecast tool's parameters (EIA's capital cost by technology, state and city; JEDI's taxable share; the gas plant's fuel defaults) (session 3938)
- [`friction_index_weekly`](#friction_index_weekly): the Friction Index by week, sector and place (session 3402)
- [`gas_balance_weekly`](#gas_balance_weekly): working gas in storage by region each week, its change and its place in the five years before; and the monthly U.S. gas balance with LNG's and power's shares (derived, session 2956)
- [`generation_mix_hourly_profile`](#generation_mix_hourly_profile): the energy mix by hour, the average day of each month, the seven ISO grids (session 94)
- [`generation_mix_records`](#generation_mix_records): the energy mix's records by grid: the highest solar and wind shares of an hour, the cleanest and the dirtiest hour (session 94)
- [`generator_pipeline_by_grid`](#generator_pipeline_by_grid): EIA-860M's planned generators by balancing authority, state, fuel, status and planned year, each snapshot month, and the moves between two months (derived, session 2951)
- [`hub_price_comparison`](#hub_price_comparison): where power is cheap, every public hub and zone price held, compared over twelve months and over the last whole month (session 96)
- [`known_data_faults`](#known_data_faults): known faults in source data, one row per fault (session 103)
- [`merchant_revenue_monthly`](#merchant_revenue_monthly): merchant revenue per MW at each ISO's main hub, by asset type and month (derived, session 51, the seller's side of the cost of power)
- [`nlr_jedi_multipliers`](#nlr_jedi_multipliers): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261020T084621Z-local (2026-10-20T08:46:21Z); that run's own header of the table follows
- [`node_basis_daily`](#node_basis_daily): ERCOT's settlement points against the hub average, by operating day (derived, session 358)
- [`node_basis_summary`](#node_basis_summary): ERCOT's settlement points against the hub average, the distribution by month (derived, session 358)
- [`nuclear_fleet_status`](#nuclear_fleet_status): the U.S. reactor fleet by reactor and year, and by grid and year: capacity, outages, long outages, available energy, uprates, restarts and retirements (derived, session 2955)
- [`region_weather_hourly`](#region_weather_hourly): each EIA region's temperature by hour, its stations weighted by county population (session 7803)
- [`resource_layer_features`](#resource_layer_features): the natural resource map's layers, every cell, site and area, with the USGS coal fields (session 8006, chain 501)
- [`scarcity_hours_by_grid`](#scarcity_hours_by_grid): each grid's own scarcity signal beside the USD 1,000 price count, hour by hour (derived, session 254)
- [`shoulder_hours_monthly`](#shoulder_hours_monthly): the shoulder hours, ERCOT and CAISO, by local month (sessions 75 and 80)
- [`state_generation_mix_monthly`](#state_generation_mix_monthly): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261023T152740Z-github (2026-10-23T15:27:40Z); that run's own header of the table follows
- [`state_large_load_laws`](#state_large_load_laws): US states' large-load laws and bills of the 2025 and 2026 sessions, one row a law or bill (session 3937, chain 267)
- [`subregion_demand_growth`](#subregion_demand_growth): every EIA-930 sub-region's peak hour and average demand by year, and the growth of each (derived, session 2877)

### `ai_power_regions`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 187.

- **Source:** erw:ai_power_regions ERW derived table, the AI gigawatts report's methods appendix (docs/reports/ai_gigawatts_methods.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/reports/ai_gigawatts_methods.md)
- **Method note:** [`docs/methods/ai_power_regions.md`](../methods/ai_power_regions.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Where the next gigawatts for AI can come from (warehouse/derived/ai_power_regions.py). Via the Energy Research Warehouse (ERW), table `ai_power_regions`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | iso:caiso, iso:ercot, iso:isone, iso:miso, iso:nyiso, iso:pjm, iso:spp | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-01T00:00:00Z, 2025-09-01T00:00:00Z, 2026-01-01T00:00:00Z, 2026-09-30T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -3.0021 to 855443603.0; 162 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD, USD/MWh, count, kgCO2/MWh, pct, tCO2, year | 0 |
| `freq` | How long the interval of the row is | none | empty | no cell holds a value | 187 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | empty | no cell holds a value | 187 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 187 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 187 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ai_power_regions | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/reports/ai_gigawatts_methods.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T09:42:46Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 187 |
| `x_window` | not yet written |  | text | 2018-07 to 2025-04, CAISO's Grid Emergencies History Report, 2025-09-01 to 2026-09-01 (twelve months), Berkeley Lab Queued Up 2026 edition, requests through 2025, studied event windows (event_study_estimates), the ISO's queue as retrieved in late September 2026 | 0 |
| `x_note` | not yet written |  | text | caiso_heat_2020 (temperature-controlled); retrieved 2026-09-30, elliott_2022 (temperature-controlled), elliott_2022 (temperature-controlled); retrieved 2026-09-26, elliott_2022 (temperature-controlled); retrieved 2026-09-30, ercot_heat_2023 (temperature-controlled); retrieved 2026-09-30 | 174 |

Variables (31):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `carbon_days` |  | count | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `carbon_intensity_kg_mwh` |  | kgCO2/MWh | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `demand_mwh` |  | MWh | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `emergency_days` |  | count | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `event_largest_effect_pct` |  | pct | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `event_largest_is_caiso_heat_2020` |  | count | 1 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `event_largest_is_elliott_2022` |  | count | 5 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `event_largest_is_ercot_heat_2023` |  | count | 1 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `flat_1gw_co2_t` |  | tCO2 | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `flat_1gw_cost_usd` |  | USD | 6 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `flat_da_price_usd_mwh` |  | USD/MWh | 6 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `flat_rt_price_usd_mwh` |  | USD/MWh | 6 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `interchange_days` |  | count | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `interchange_days_reported` |  | count | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `lbnl_active_mw` |  | MW | 7 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `lbnl_active_requests` |  | count | 7 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `lbnl_cod_sample` |  | count | 7 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `lbnl_cohort_requests` |  | count | 7 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `lbnl_completion_pct` |  | pct | 7 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `lbnl_median_years_to_cod` |  | year | 6 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `max_rt_hour_usd_mwh` |  | USD/MWh | 6 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `net_import_days_pct` |  | pct | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `net_import_share_pct` |  | pct | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `pair_import_share_pct` |  | pct | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `peak_import_share_pct` |  | pct | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `queue_active_mw` |  | MW | 6 | 2026-09-30T00:00:00Z | 2026-09-30T00:00:00Z |
| `rt_hours_priced` |  | count | 6 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `rt_hours_seen` |  | count | 6 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `scarcity_hours_1000` |  | count | 6 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `scarcity_hours_200` |  | count | 6 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `screened_pair_days` |  | count | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |

### `attention_index_weekly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: model_extracted. Rows read on 2026-11-20: 1775.

- **Method note:** [`docs/methods/attention.md`](../methods/attention.md)
- **Cite as:** Energy Research Warehouse (ERW). The Attention and Friction indices: coverage and opposition by week, sector and place, from the classified news stories (the ERW's own derivation). Via the Energy Research Warehouse (ERW), table `attention_index_weekly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example attention:corpus:all, attention:datacenters:US, attention:datacenters:US-AL; 185 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2024-12-30T00:00:00Z to 2026-11-09T00:00:00Z; 98 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1.0 to 3146.0; 384 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count, pct, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 47 distinct | 512 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:attention | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/attention.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-06T20:14:48Z, 2026-11-06T20:34:52Z, 2026-11-16T09:23:15Z | 0 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `attention_index` |  | pct | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `stories` |  | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `stories_classified` |  | count | 98 | 2024-12-30T00:00:00Z | 2026-11-09T00:00:00Z |
| `stories_judged` |  | count | 98 | 2024-12-30T00:00:00Z | 2026-11-09T00:00:00Z |
| `stories_unsent_zero` |  | count | 98 | 2024-12-30T00:00:00Z | 2026-11-09T00:00:00Z |
| `stories_week` |  | count | 98 | 2024-12-30T00:00:00Z | 2026-11-09T00:00:00Z |
| `tone_mean` |  | ratio | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |

### `attention_story_links`

What a row is: not yet written.

Shape: events. Keys: `event_id`. License: public; tier: model_extracted. Rows read on 2026-11-20: 8120.

- **Method note:** [`docs/methods/attention.md`](../methods/attention.md)
- **Cite as:** Energy Research Warehouse (ERW). The Attention and Friction indices: coverage and opposition by week, sector and place, from the classified news stories (the ERW's own derivation). Via the Energy Research Warehouse (ERW), table `attention_story_links`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | none | text | for example attn:0007c90d93793ce0, attn:0010e7ad3689a2d6, attn:00111d8c171a3b8b; more than 5000 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | utc time | 2026-10-05T17:03:00Z to 2026-11-17T12:00:00Z; more than 5000 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others) | none | text | attention_link | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | empty | no cell holds a value | 8120 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 8120 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 8120 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 8120 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 8120 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | empty | no cell holds a value | 8120 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | for example ANS Nuclear Newswire, Bloomberg, Bloomberg.com; 48 distinct | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://electrek.co/2026/10/05/byds-flagship-suv-topped-10000-sales-3-months-straight/, https://electrek.co/2026/10/05/department-of-war-drafts-ev-battery-factory-into-military-drone-duty-with-75m-grant/, https://electrek.co/2026/10/05/hyundai-testing-smaller-ev-could-be-ioniq-4-video/; more than 5000 distinct | 0 |
| `story_event_id` | not yet written |  | text | for example news:0007c90d93793ce0, news:0010e7ad3689a2d6, news:00111d8c171a3b8b; more than 5000 distinct | 0 |
| `week` | not yet written |  | utc time | 2026-10-05T00:00:00Z, 2026-10-12T00:00:00Z, 2026-10-19T00:00:00Z, 2026-10-26T00:00:00Z, 2026-11-02T00:00:00Z, 2026-11-16T00:00:00Z | 0 |
| `sector` | not yet written |  | text | datacenters, gas, not_energy, nuclear, oil_lng, other_energy, solar_wind, storage, transmission | 0 |
| `us` | not yet written |  | boolean | false, true | 0 |
| `state` | not yet written |  | text | for example AK, AL, AR; 49 distinct | 7364 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 50 distinct | 4472 |
| `place` | not yet written |  | text | for example Adelaide, Aiken, Albuquerque; 185 distinct | 7869 |
| `place_kind` | not yet written |  | text | city, county, metro | 7889 |
| `opposition` | not yet written |  | boolean | false, true | 0 |
| `kind` | not yet written |  | text | lawsuit, moratorium, none, other_opposition, permit_denied, political_opposition, protest, rate_case | 0 |
| `tone` | not yet written |  | integer | -1, 0, 1 | 0 |
| `headline` | not yet written |  | text | for example $67.8 billion in Asian LNG-to-power projects scrapped or stalled since 2021, 120K customers without power in Southeastern US after Hurricane Isaias, 121 Gulf platforms evacuated as Isaias strengthens; more than 5000 distinct | 0 |
| `scorer_sector` | not yet written |  | text | capital, company, datacenter_power, deal, gas, generation, geopolitics, grid_conditions, hydrogen, interconnection, lng, nuclear, oil, other, policy, power_prices, ppa, renewables, storage, transmission, transport | 3548 |
| `significance` | not yet written |  | integer | 1, 2, 3, 4, 5, 6, 7, 8, 9 | 3548 |
| `model_id` | not yet written |  | text | claude-sonnet-5-5 | 0 |
| `prompt_version` | not yet written |  | integer | 2 | 0 |
| `classified_at` | not yet written |  | utc time | 2026-11-06T19:58:37Z, 2026-11-06T20:16:40Z | 0 |
| `fixed` | not yet written |  | empty | no cell holds a value | 8120 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T09:23:15Z, 2026-11-16T09:24:19Z | 0 |

### `clean_energy_hourly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 478164.

- **Source:** erw:clean_energy EIA Form EIA-930 hourly net generation by energy source, the per-BA workbooks ( California from 2025-12-16T08:00:00Z is CAISO's own supply by fuel (caiso_fuel_supply), the warehouse's one join (docs/methods/eia930_caiso_break.md); read by this run from warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175834.883363Z_00002_CISO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175850.712544Z_00004_ERCO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175904.395449Z_00006_ISNE.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175918.956497Z_00008_MISO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175934.677962Z_00010_NYIS.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175949.986042Z_00012_PJM.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T180008.741327Z_00014_SWPP.xlsx (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx)
- **Method note:** [`docs/methods/generation_mix_hourly.md`](../methods/generation_mix_hourly.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. How clean each grid's generation is by hour, month and year; hourly against annual matching; load moved into the cleanest hours (docs/methods/clean_energy.md). Via the Energy Research Warehouse (ERW), table `clean_energy_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | iso:caiso, iso:ercot, iso:isone, iso:miso, iso:nyiso, iso:pjm, iso:spp | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T05:00:00Z to 2026-11-16T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 95.207; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | pct | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-CA, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 478164 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 478164 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:clean_energy | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/clean_energy.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T18:00:39Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 478164 |
| `x_carbon_free_mwh` | not yet written |  | number | 0.0 to 57449.0; more than 5000 distinct | 0 |
| `x_generation_mwh` | not yet written |  | number | 5561.0 to 164281.0; more than 5000 distinct | 0 |
| `x_side` | not yet written |  | text | caiso, eia930 | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `carbon_free_share_pct` |  | pct | 478164 | 2019-01-01T05:00:00Z | 2026-11-16T07:00:00Z |

### `clean_energy_summary`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 27834.

- **Source:** erw:clean_energy EIA Form EIA-930 hourly net generation by energy source, the per-BA workbooks ( California from 2025-12-16T08:00:00Z is CAISO's own supply by fuel (caiso_fuel_supply), the warehouse's one join (docs/methods/eia930_caiso_break.md); read by this run from warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175834.883363Z_00002_CISO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175850.712544Z_00004_ERCO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175904.395449Z_00006_ISNE.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175918.956497Z_00008_MISO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175934.677962Z_00010_NYIS.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175949.986042Z_00012_PJM.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T180008.741327Z_00014_SWPP.xlsx (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx)
- **Method note:** [`docs/methods/clean_energy.md`](../methods/clean_energy.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. How clean each grid's generation is by hour, month and year; hourly against annual matching; load moved into the cleanest hours (docs/methods/clean_energy.md). Via the Energy Research Warehouse (ERW), table `clean_energy_summary`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | iso:caiso, iso:ercot, iso:isone, iso:miso, iso:nyiso, iso:pjm, iso:spp | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-10-01T00:00:00Z; 94 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -54.1977 to 1482.9822; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count, hour, kgCO2/MWh, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M, P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-CA, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 27834 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 27834 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:clean_energy | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/clean_energy.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T18:00:39Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 27834 |

Variables (84):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `carbon_free_share_flat_pct` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `carbon_free_share_pct` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h00` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h01` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h02` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h03` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h04` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h05` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h06` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h07` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h08` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h09` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h10` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h11` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h12` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h13` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h14` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h15` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h16` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h17` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h18` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h19` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h20` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h21` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h22` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h23` |  | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cleanest_hour_1` |  | hour | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cleanest_hour_2` |  | hour | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cleanest_hour_3` |  | hour | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cleanest_hour_4` |  | hour | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cost_days` |  | count | 204 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `days_held` |  | count | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `days_in_month` |  | count | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `flat_cost_usd_per_mwh` |  | USD/MWh | 204 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `flat_kgco2_per_mwh` |  | kgCO2/MWh | 626 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `own_data` |  | count | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift10_carbon_change_pct` |  | pct | 626 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift10_cost_change_pct` |  | pct | 204 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift10_cost_usd_per_mwh` |  | USD/MWh | 204 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift10_kgco2_per_mwh` |  | kgCO2/MWh | 626 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift20_carbon_change_pct` |  | pct | 626 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift20_cost_change_pct` |  | pct | 204 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift20_cost_usd_per_mwh` |  | USD/MWh | 204 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift20_kgco2_per_mwh` |  | kgCO2/MWh | 626 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift_days` |  | count | 626 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `year_carbon_free_share_flat_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_carbon_free_share_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_cost_days` |  | count | 20 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_days_held` |  | count | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_flat_cost_usd_per_mwh` |  | USD/MWh | 20 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_flat_kgco2_per_mwh` |  | kgCO2/MWh | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_hours_cf_ge50_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_hours_cf_ge75_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_hours_cf_ge90_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_mix_100_energy_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_mix_100_hours_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_mix_150_energy_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_mix_150_hours_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_mix_50_energy_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_mix_50_hours_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_solar_100_energy_pct` |  | pct | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_solar_100_hours_pct` |  | pct | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_solar_150_energy_pct` |  | pct | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_solar_150_hours_pct` |  | pct | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_solar_50_energy_pct` |  | pct | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_solar_50_hours_pct` |  | pct | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_wind_100_energy_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_wind_100_hours_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_wind_150_energy_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_wind_150_hours_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_wind_50_energy_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_wind_50_hours_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_months` |  | count | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_months_due` |  | count | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_own_data_months` |  | count | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift10_carbon_change_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift10_cost_change_pct` |  | pct | 20 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift10_cost_usd_per_mwh` |  | USD/MWh | 20 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift10_kgco2_per_mwh` |  | kgCO2/MWh | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift20_carbon_change_pct` |  | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift20_cost_change_pct` |  | pct | 20 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift20_cost_usd_per_mwh` |  | USD/MWh | 20 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift20_kgco2_per_mwh` |  | kgCO2/MWh | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift_days` |  | count | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

### `deal_counterparties`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: model_extracted. Rows read on 2026-11-20: 532.

- **Method note:** [`docs/methods/deal_counterparties.md`](../methods/deal_counterparties.md)
- **Cite as:** Energy Research Warehouse (ERW). Deal tracker counterparties (energy_deals, warehouse/deals/extract.py). Via the Energy Research Warehouse (ERW), table `deal_counterparties`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example counterparty:1komma5grad, counterparty:247_solar, counterparty:a_leading_frontier_ai_lab; 532 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | company | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 1Komma5Grad, 247 Solar, ACME Solar; 532 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | empty | no cell holds a value | 532 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 532 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 532 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 532 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | empty | no cell holds a value | 532 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 532 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 532 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:energy_deals | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://electrek.co/2026/09/27/nio-power-geely-30-stake-battery-swap-rmb16-billion/, https://heatmap.news/climate-tech/coreshell-series-b, https://lngprime.com/americas/argent-lng-awards-feed-contract/197559/; 383 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-13T15:10:45Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | text | 20261113T151045Z | 0 |
| `kind` | not yet written |  | text | ai_buyer, company, government | 0 |
| `parent` | not yet written |  | text | Aditya Birla, Adnoc, Amazon, BlackRock, Blackstone, Chevron, Constellation Energy, EIG, ExxonMobil, Geely Holding, General Motors, MAIRE, OGE Energy | 518 |
| `eia861_utility_number` | not yet written |  | empty | no cell holds a value | 532 |
| `spellings` | not yet written |  | text | for example 1Komma5Grad, 247 Solar, ACME Solar; 532 distinct | 0 |
| `deals` | not yet written |  | integer | 1, 10, 11, 12, 14, 18, 2, 22, 3, 4, 5, 6, 7, 8, 9 | 0 |
| `as_buyer` | not yet written |  | integer | 0, 1, 12, 13, 14, 15, 18, 2, 3, 4, 5, 6, 8, 9 | 0 |
| `as_seller` | not yet written |  | integer | 0, 1, 2, 3, 4, 5, 6, 7, 8 | 0 |
| `mw_stated` | not yet written |  | number | 20.0 to 5400.0; 31 distinct | 478 |
| `deals_with_mw` | not yet written |  | integer | 0, 1, 2, 3, 4 | 0 |
| `ai_power_deals` | not yet written |  | integer | 0, 1, 12, 13, 18, 2, 3, 4, 5, 6, 7, 9 | 0 |
| `first_deal` | not yet written |  | date | 2025-01-05 to 2026-11-13; 164 distinct | 0 |
| `last_deal` | not yet written |  | date | 2025-01-05 to 2026-11-13; 145 distinct | 0 |
| `event_ids` | not yet written |  | text | for example deal:0046c6c22995488c, deal:0046c6c22995488c;deal:665d71e3ff9f1de4;deal:7e901b6ad732c6ca;deal:d64297631c27daa2, deal:006dc20ac6ffe6f3; 438 distinct | 0 |

### `event_study_estimates`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 3040.

- **Source:** erw:event_study ERW derived table, event study method (docs/methods/event_study.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/event_study.md)
- **Method note:** [`docs/methods/event_study.md`](../methods/event_study.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Event study estimates (warehouse/derived/event_study.py). Via the Energy Research Warehouse (ERW), table `event_study_estimates`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | eia930:CISO, eia930:ERCO, eia930:ISNE, eia930:MISO, eia930:NYIS, eia930:PJM, eia930:SWPP, eia930:US48, ercot:HB_HUBAVG, isone:.H.INTERNAL_HUB, miso:INDIANA.HUB, nyiso:N.Y.C., spp:SPPNORTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2020-03-01T00:00:00Z to 2026-02-02T00:00:00Z; 217 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1238136.923077 to 10002125.478261; 3040 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1D, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-DE,US-DC,US-IL,US-IN,US-KY,US-MD,US-MI,US-NJ,US-NC,US-OH,US-PA,US-TN,US-VA,US-WV, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 3040 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 3040 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:event_study | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/event_study.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-19T09:46:06Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 3040 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48) | none | text | ciso, erco, isne, miso, nyis, pjm, swpp, us48 | 0 |
| `event` | not yet written |  | text | caiso_heat_2020, caiso_heat_2022, cold_2025, cold_2026, covid_2020, east_heat_2025, elliott_2022, ercot_heat_2023, uri_2021 | 0 |
| `x_std_error` | not yet written |  | number | 1.558606 to 941905.482593; 1966 distinct | 65 |
| `x_ci_low` | not yet written |  | number | -2582448.607907 to 616062.554395; 2975 distinct | 65 |
| `x_ci_high` | not yet written |  | number | -468714.428903 to 4071124.723204; 2975 distinct | 65 |
| `x_n` | not yet written |  | integer | 123, 182, 184, 21, 22, 26, 27, 275, 276, 30, 32, 33, 42, 54 | 0 |
| `x_spec` | not yet written |  | text | dow_trend_v1, dow_year_mean_v1, dow_year_temp_v1 | 0 |
| `x_term` | not yet written |  | text | for example event day 2020-03-01, event day 2020-03-01, controlling for temperature, event day 2020-03-02; 431 distinct | 0 |

Variables (38):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `demand_mw_effect_h00` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h01` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h02` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h03` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h04` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h05` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h06` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h07` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h08` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h09` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h10` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h11` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h12` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h13` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h14` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h15` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h16` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h17` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h18` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h19` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h20` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h21` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h22` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h23` |  | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mwh_counterfactual_mean` |  | MWh | 34 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mwh_counterfactual_mean_temp` |  | MWh | 17 | 2020-03-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `demand_mwh_effect_day` |  | MWh | 1043 | 2020-03-01T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_mwh_effect_day_temp` |  | MWh | 791 | 2020-03-01T00:00:00Z | 2023-09-10T00:00:00Z |
| `demand_mwh_effect_pooled` |  | MWh | 34 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mwh_effect_pooled_temp` |  | MWh | 17 | 2020-03-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `demand_mwh_effect_pooled_trend` |  | MWh | 33 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `rt_mean_counterfactual_mean` |  | USD/MWh | 10 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `rt_mean_counterfactual_mean_temp` |  | USD/MWh | 4 | 2020-03-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `rt_mean_effect_day` |  | USD/MWh | 227 | 2020-03-01T00:00:00Z | 2026-02-02T00:00:00Z |
| `rt_mean_effect_day_temp` |  | USD/MWh | 162 | 2020-03-01T00:00:00Z | 2023-09-10T00:00:00Z |
| `rt_mean_effect_pooled` |  | USD/MWh | 10 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `rt_mean_effect_pooled_temp` |  | USD/MWh | 4 | 2020-03-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `rt_mean_effect_pooled_trend` |  | USD/MWh | 6 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |

### `event_window_daily`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 29953.

- **Source:** erw:event_window ERW derived table, events method (docs/methods/events.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/events.md)
- **Method note:** [`docs/methods/events.md`](../methods/events.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Event windows, daily figures around an event and its baseline (docs/methods/events.md). Via the Energy Research Warehouse (ERW), table `event_window_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | eia930:CISO, eia930:ERCO, eia930:ISNE, eia930:MISO, eia930:NYIS, eia930:PJM, eia930:SWPP, eia930:US48, ercot:HB_HUBAVG, isone:.H.INTERNAL_HUB, miso:INDIANA.HUB, noaa:BOS, noaa:DFW, noaa:IAH, noaa:JFK, noaa:LAX, noaa:MSP, noaa:OKC, noaa:ORD, noaa:PHL, noaa:SAC, nyiso:N.Y.C., spp:SPPNORTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-03-04T00:00:00Z to 2026-02-02T00:00:00Z; 625 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -9334580.0 to 12200004.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD/MWh, degF, degF-day, kgCO2/MWh, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1D, P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-DE,US-DC,US-IL,US-IN,US-KY,US-MD,US-MI,US-NJ,US-NC,US-OH,US-PA,US-TN,US-VA,US-WV, US-NY, US-TX | 13375 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_dam, ercot_rtm, isone_dam, isone_rtm, miso_dam, miso_rtm, nyiso_dam, nyiso_rtm, spp_dam, spp_rtm | 27697 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | integer | 72243012960, 72259003927, 72295023174, 72353013967, 72408013739, 72483023232, 72509014739, 72530094846, 72658014922, 74486094789 | 16578 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:event_window | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/events.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-19T09:43:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 29953 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48) | none | text | ciso, erco, isne, miso, nyis, pjm, swpp, us48 | 0 |
| `event` | not yet written |  | text | caiso_heat_2020, caiso_heat_2022, cold_2025, cold_2026, covid_2020, east_heat_2025, elliott_2022, ercot_heat_2023, uri_2021 | 0 |

Variables (23):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `cdd_65f` |  | degF-day | 2675 | 2018-03-04T00:00:00Z | 2023-09-10T00:00:00Z |
| `da_max` |  | USD/MWh | 428 | 2019-02-07T00:00:00Z | 2026-02-02T00:00:00Z |
| `da_mean` |  | USD/MWh | 704 | 2018-03-04T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_max_mw` |  | MW | 3043 | 2018-03-04T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_max_mw_vs_baseline` |  | MW | 288 | 2020-08-12T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_max_pct_vs_baseline` |  | pct | 288 | 2020-08-12T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_min_mw` |  | MW | 3043 | 2018-03-04T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_mwh` |  | MWh | 3043 | 2018-03-04T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_mwh_day_change` |  | MWh | 17 | 2021-02-08T00:00:00Z | 2021-02-24T00:00:00Z |
| `demand_mwh_vs_baseline` |  | MWh | 1039 | 2020-03-01T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_mwh_vs_baseline_week` |  | MWh | 101 | 2020-03-01T00:00:00Z | 2020-05-24T00:00:00Z |
| `demand_pct_vs_baseline` |  | pct | 1021 | 2020-03-01T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_pct_vs_baseline_week` |  | pct | 101 | 2020-03-01T00:00:00Z | 2020-05-24T00:00:00Z |
| `hdd_65f` |  | degF-day | 2675 | 2018-03-04T00:00:00Z | 2023-09-10T00:00:00Z |
| `intensity_generation` |  | kgCO2/MWh | 2249 | 2018-08-13T00:00:00Z | 2026-02-02T00:00:00Z |
| `net_generation_mwh` |  | MWh | 54 | 2019-02-07T00:00:00Z | 2021-02-24T00:00:00Z |
| `net_generation_mwh_day_change` |  | MWh | 17 | 2021-02-08T00:00:00Z | 2021-02-24T00:00:00Z |
| `net_generation_mwh_vs_baseline` |  | MWh | 18 | 2021-02-07T00:00:00Z | 2021-02-24T00:00:00Z |
| `rt_max` |  | USD/MWh | 424 | 2019-02-07T00:00:00Z | 2026-02-02T00:00:00Z |
| `rt_mean` |  | USD/MWh | 700 | 2018-03-04T00:00:00Z | 2026-02-02T00:00:00Z |
| `temp_max_f` |  | degF | 2675 | 2018-03-04T00:00:00Z | 2023-09-10T00:00:00Z |
| `temp_mean_f` |  | degF | 2675 | 2018-03-04T00:00:00Z | 2023-09-10T00:00:00Z |
| `temp_min_f` |  | degF | 2675 | 2018-03-04T00:00:00Z | 2023-09-10T00:00:00Z |

### `flex_alert_effects`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 3429.

- **Source:** erw:flex_alert_scorecard ERW derived table, Flex Alert scorecard method (docs/methods/flex_alert_scorecard.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/flex_alert_scorecard.md)
- **Method note:** [`docs/methods/flex_alert_scorecard.md`](../methods/flex_alert_scorecard.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Flex Alert scorecard (warehouse/derived/flex_alert_scorecard.py). Via the Energy Research Warehouse (ERW), table `flex_alert_effects`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | eia930:CISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-01-01T00:00:00Z to 2024-07-25T06:00:00Z; 479 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -5804512.4267 to 380303.2757; 2755 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD, USD/MWh, count, degF, hour, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1D, P1Y, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 3429 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 3429 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:flex_alert_scorecard | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/flex_alert_scorecard.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-17T07:24:23Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 3429 |

Variables (49):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `actual_mw` |  | MW | 456 | 2018-07-24T19:00:00Z | 2024-07-25T06:00:00Z |
| `actual_mwh` |  | MWh | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `alert_first_hour` |  | hour | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `alert_hour` |  | count | 456 | 2018-07-24T19:00:00Z | 2024-07-25T06:00:00Z |
| `alert_hours` |  | count | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `alert_last_hour` |  | hour | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `basis_flex_alert` |  | count | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `hours_assumed` |  | count | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `predicted_mw` |  | MW | 456 | 2018-07-24T19:00:00Z | 2024-07-25T06:00:00Z |
| `predicted_mw_hi` |  | MW | 456 | 2018-07-24T19:00:00Z | 2024-07-25T06:00:00Z |
| `predicted_mw_lo` |  | MW | 456 | 2018-07-24T19:00:00Z | 2024-07-25T06:00:00Z |
| `predicted_mwh` |  | MWh | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `price_usd_mwh` |  | USD/MWh | 4 | 2023-07-20T00:00:00Z | 2024-07-24T00:00:00Z |
| `reduction_mw` |  | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `reduction_mw_hi` |  | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `reduction_mw_lo` |  | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `reduction_mwh` |  | MWh | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `reduction_mwh_hi` |  | MWh | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `reduction_mwh_lo` |  | MWh | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `reduction_pct` |  | pct | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `temp_max_f` |  | degF | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `train_days_as_hot` |  | count | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `value_usd` |  | USD | 4 | 2023-07-20T00:00:00Z | 2024-07-24T00:00:00Z |
| `value_usd_hi` |  | USD | 4 | 2023-07-20T00:00:00Z | 2024-07-24T00:00:00Z |
| `value_usd_lo` |  | USD | 4 | 2023-07-20T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_cdh_dew_reduction_mw` |  | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_cdh_dew_reduction_mw_hi` |  | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_cdh_dew_reduction_mw_lo` |  | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_prev24sq_reduction_mw` |  | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_prev24sq_reduction_mw_hi` |  | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_prev24sq_reduction_mw_lo` |  | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_reduction_mw` |  | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_reduction_mw_hi` |  | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_reduction_mw_lo` |  | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_minimal_reduction_mw` |  | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_minimal_reduction_mw_hi` |  | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_minimal_reduction_mw_lo` |  | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `year_days` |  | count | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_hours` |  | count | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_reduction_mw` |  | MW | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_reduction_mw_hi` |  | MW | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_reduction_mw_lo` |  | MW | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_reduction_mwh` |  | MWh | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_reduction_mwh_hi` |  | MWh | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_reduction_mwh_lo` |  | MWh | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_reduction_pct` |  | pct | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_value_usd` |  | USD | 2 | 2023-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_value_usd_hi` |  | USD | 2 | 2023-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_value_usd_lo` |  | USD | 2 | 2023-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `flex_alert_model`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 881.

- **Source:** erw:flex_alert_scorecard ERW derived table, Flex Alert scorecard method (docs/methods/flex_alert_scorecard.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/flex_alert_scorecard.md)
- **Method note:** [`docs/methods/flex_alert_scorecard.md`](../methods/flex_alert_scorecard.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Flex Alert scorecard (warehouse/derived/flex_alert_scorecard.py). Via the Energy Research Warehouse (ERW), table `flex_alert_model`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | erw:flex_alert_model | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-01T00:00:00Z to 2025-08-24T00:00:00Z; 129 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -8043179.4743 to 50464.9058; 841 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD, USD/MWh, count, degF, pct, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 584 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 881 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 881 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:flex_alert_scorecard | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/flex_alert_scorecard.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-17T07:24:23Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 881 |

Variables (587; the first 300 by name):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `alert_days_hotter_than_threshold` |  | count | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `bootstrap_replicates` |  | count | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_cdh` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_cdh2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_cdh_prev24` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_cdh_prev24_2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_cdh_x_dew` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_dew_point` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_holiday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_intercept` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_month10` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_month6` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_month7` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_month8` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_month9` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_saturday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_sunday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_year2019` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_year2020` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_year2021` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_year2022` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_year2023` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_year2024` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_year2025` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_cdh` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_cdh2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_cdh_prev24` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_cdh_prev24_2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_cdh_x_dew` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_dew_point` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_holiday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_intercept` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_month10` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_month6` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_month7` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_month8` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_month9` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_saturday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_sunday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_year2019` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_year2020` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_year2021` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_year2022` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_year2023` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_year2024` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_year2025` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_cdh` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_cdh2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_cdh_prev24` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_cdh_prev24_2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_cdh_x_dew` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_dew_point` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_holiday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_intercept` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_month10` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_month6` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_month7` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_month8` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_month9` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_saturday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_sunday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_year2019` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_year2020` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_year2021` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_year2022` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_year2023` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_year2024` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_year2025` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_cdh` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_cdh2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_cdh_prev24` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_cdh_prev24_2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_cdh_x_dew` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_dew_point` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_holiday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_intercept` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_month10` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_month6` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_month7` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_month8` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_month9` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_saturday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_sunday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_year2019` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_year2020` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_year2021` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_year2022` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_year2023` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_year2024` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_year2025` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_cdh` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_cdh2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_cdh_prev24` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_cdh_prev24_2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_cdh_x_dew` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_dew_point` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_holiday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_intercept` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_month10` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_month6` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_month7` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_month8` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_month9` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_saturday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_sunday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_year2019` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_year2020` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_year2021` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_year2022` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_year2023` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_year2024` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_year2025` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_cdh` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_cdh2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_cdh_prev24` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_cdh_prev24_2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_cdh_x_dew` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_dew_point` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_holiday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_intercept` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_month10` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_month6` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_month7` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_month8` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_month9` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_saturday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_sunday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_year2019` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_year2020` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_year2021` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_year2022` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_year2023` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_year2024` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_year2025` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_cdh` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_cdh2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_cdh_prev24` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_cdh_prev24_2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_cdh_x_dew` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_dew_point` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_holiday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_intercept` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_month10` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_month6` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_month7` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_month8` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_month9` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_saturday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_sunday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_year2019` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_year2020` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_year2021` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_year2022` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_year2023` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_year2024` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_year2025` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_cdh` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_cdh2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_cdh_prev24` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_cdh_prev24_2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_cdh_x_dew` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_dew_point` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_holiday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_intercept` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_month10` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_month6` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_month7` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_month8` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_month9` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_saturday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_sunday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_year2019` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_year2020` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_year2021` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_year2022` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_year2023` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_year2024` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_year2025` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_cdh` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_cdh2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_cdh_prev24` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_cdh_prev24_2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_cdh_x_dew` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_dew_point` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_holiday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_intercept` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_month10` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_month6` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_month7` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_month8` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_month9` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_saturday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_sunday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_year2019` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_year2020` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_year2021` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_year2022` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_year2023` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_year2024` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_year2025` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_cdh` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_cdh2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_cdh_prev24` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_cdh_prev24_2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_cdh_x_dew` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_dew_point` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_holiday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_intercept` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_month10` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_month6` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_month7` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_month8` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_month9` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_saturday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_sunday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_year2019` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_year2020` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_year2021` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_year2022` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_year2023` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_year2024` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_year2025` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_cdh` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_cdh2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_cdh_prev24` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_cdh_prev24_2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_cdh_x_dew` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_dew_point` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_holiday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_intercept` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_month10` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_month6` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_month7` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_month8` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_month9` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_saturday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_sunday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_year2019` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_year2020` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_year2021` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_year2022` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_year2023` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_year2024` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_year2025` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_cdh` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_cdh2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_cdh_prev24` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_cdh_prev24_2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_cdh_x_dew` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_dew_point` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_holiday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_intercept` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_month10` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_month6` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_month7` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_month8` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_month9` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_saturday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_sunday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_year2019` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_year2020` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_year2021` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_year2022` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_year2023` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_year2024` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_year2025` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_cdh` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_cdh2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_cdh_prev24` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_cdh_prev24_2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_cdh_x_dew` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_dew_point` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_holiday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_intercept` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_month10` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_month6` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_month7` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_month8` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_month9` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_saturday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_sunday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_year2019` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_year2020` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_year2021` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_year2022` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_year2023` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_year2024` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_year2025` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_cdh` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_cdh2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_cdh_prev24` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_cdh_prev24_2` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_cdh_x_dew` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_dew_point` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_holiday` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_intercept` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_month10` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_month6` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_month7` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_month8` |  | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |

### `forecast_tool_parameters`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 768.

- **Source:** eia:capital_cost_aeo2025 U.S. Energy Information Administration (EIA), Capital Cost and Performance Characteristic Estimates for Utility Scale Electric Power Generating Technologies (AEO2025), Appendix A,  nlr:jedi_models National Laboratory of the Rockies (NLR, formerly NREL), JEDI models (Jobs and Economic Development Impact),  erw:forecast_gas: the study's heat rate, JEDI's default capacity factor, eia_steo_forecasts' NGHHUUS and EIA's heat content (https://www.nlr.gov/analysis/jedi/models)
- **Method note:** [`docs/methods/forecast.md`](../methods/forecast.md)
- **Cite as:** Energy Research Warehouse (ERW); National Laboratory of the Rockies (NLR, formerly NREL); U.S. Energy Information Administration (EIA). Capital Cost and Performance Characteristic Estimates for Utility Scale Electric Power Generating Technologies (AEO2025), Appendix A; JEDI models (Jobs and Economic Development Impact); The forecast tool's gas fuel defaults (site/data/forecast/gas.json). Via the Energy Research Warehouse (ERW), table `forecast_tool_parameters`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example forecast:eia_capex:geothermal:ca, forecast:eia_capex:geothermal:ca_bakersfield, forecast:eia_capex:geothermal:ca_los_angeles; 559 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2025-01-01T00:00:00Z, 2026-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.605882 to 3756566.12; 311 distinct | 0 |
| `unit` | The unit of the row's value | none | text | Btu/ft3, MMBtu/MWh, MW, USD/MMBtu, USD/MW, USD/kW, month, ratio, year | 0 |
| `freq` | How long the interval of the row is | none | empty | no cell holds a value | 768 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 768 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 768 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:capital_cost_aeo2025, erw:forecast_gas, nlr:jedi_models | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/forecast.md, https://www.eia.gov/analysis/studies/powerplants/capitalcost/pdf/capital_cost_AEO2025.pdf, https://www.nlr.gov/analysis/jedi/models | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-13T10:23:29Z, 2026-11-13T10:45:00Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 768 |
| `x_technology` | not yet written |  | text | geothermal, land_based_wind, natural_gas, utility_pv | 0 |
| `x_place` | not yet written |  | text | for example ak, al, al_huntsville; 113 distinct | 0 |
| `x_dollar_year` | not yet written |  | integer | 2010, 2017, 2023, 2025 | 212 |
| `x_detail` | not yet written |  | text | for example 01d-jedi-geothermal-model-rel-gt12-23-16.xlsm (nameplate MW (the model's 10 MW net output)), ALABAMA: Summary Results!D7 45,928,513.17 USD over 12.2262 MW, 01d-jedi-geothermal-model-rel-gt12-23-16.xlsm (nameplate MW (the model's 10 MW net output)), ALASKA: Summary Results!D7 45,928,513.17 USD over 12.2262 MW, 01d-jedi-geothermal-model-rel-gt12-23-16.xlsm (nameplate MW (the model's 10 MW net output)), ARIZONA: Summary Results!D7 45,928,513.17 USD over 12.2262 MW; 328 distinct | 0 |

Variables (11):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity_factor` |  | ratio | 1 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `case_mw` |  | MW | 4 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `construction_cost` |  | USD/MW | 206 | 2010-01-01T00:00:00Z | 2017-01-01T00:00:00Z |
| `construction_months` |  | month | 4 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `fuel_price` |  | USD/MMBtu | 1 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `heat_content` |  | Btu/ft3 | 1 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `heat_rate` |  | MMBtu/MWh | 2 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `location_variation` |  | ratio | 193 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `operating_life` |  | year | 4 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `overnight_cost` |  | USD/kW | 349 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `taxable_share` |  | ratio | 3 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

### `friction_index_weekly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: model_extracted. Rows read on 2026-11-20: 4610.

- **Method note:** [`docs/methods/attention.md`](../methods/attention.md)
- **Cite as:** Energy Research Warehouse (ERW). The Attention and Friction indices: coverage and opposition by week, sector and place, from the classified news stories (the ERW's own derivation). Via the Energy Research Warehouse (ERW), table `friction_index_weekly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example attention:datacenters:US, attention:datacenters:US-AL, attention:datacenters:US-AR; 184 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-10-05T00:00:00Z, 2026-10-12T00:00:00Z, 2026-10-19T00:00:00Z, 2026-10-26T00:00:00Z, 2026-11-02T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 100.0; 108 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 47 distinct | 400 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:attention | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/attention.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T09:24:19Z | 0 |

Variables (10):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `friction_index` |  | pct | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `kind_lawsuit` |  | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `kind_moratorium` |  | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `kind_other_opposition` |  | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `kind_permit_denied` |  | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `kind_political_opposition` |  | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `kind_protest` |  | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `kind_rate_case` |  | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `opposition_events` |  | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `opposition_stories` |  | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |

### `gas_balance_weekly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 40507.

- **Source:** eia:natural-gas U.S. Energy Information Administration, Weekly Natural Gas Storage Report and Natural Gas Monthly
- **Method note:** [`docs/methods/gas_balance_weekly.md`](../methods/gas_balance_weekly.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The weekly gas storage balance and the monthly U.S. gas balance (docs/methods/gas_balance_weekly.md). Via the Energy Research Warehouse (ERW), table `gas_balance_weekly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | gas_balance:US, gas_storage:east, gas_storage:lower48, gas_storage:midwest, gas_storage:mountain, gas_storage:nonsalt, gas_storage:pacific, gas_storage:salt, gas_storage:south_central | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z to 2026-10-16T00:00:00Z; 1154 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1047507.0 to 3921586.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf, bcf, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M, P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 40507 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 40507 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:gas_balance_weekly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/gas_balance_weekly.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-06T08:28:34Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 40507 |
| `x_region` | not yet written |  | text | US, east, lower48, midwest, mountain, nonsalt, pacific, salt, south_central | 0 |

Variables (16):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` |  | MMcf | 307 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `dry_production` |  | MMcf | 307 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `exports` |  | MMcf | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `five_year_avg_bcf` |  | bcf | 4912 | 2015-01-02T00:00:00Z | 2026-10-16T00:00:00Z |
| `five_year_max_bcf` |  | bcf | 4912 | 2015-01-02T00:00:00Z | 2026-10-16T00:00:00Z |
| `five_year_min_bcf` |  | bcf | 4912 | 2015-01-02T00:00:00Z | 2026-10-16T00:00:00Z |
| `five_year_position_pct` |  | pct | 4912 | 2015-01-02T00:00:00Z | 2026-10-16T00:00:00Z |
| `implied_balance` |  | MMcf | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `imports` |  | MMcf | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `lng_exports` |  | MMcf | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `lng_share_pct` |  | pct | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_change_bcf` |  | bcf | 7008 | 2010-01-08T00:00:00Z | 2026-10-16T00:00:00Z |
| `power_burn` |  | MMcf | 307 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `power_share_pct` |  | pct | 307 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `vs_five_year_avg_bcf` |  | bcf | 4912 | 2015-01-02T00:00:00Z | 2026-10-16T00:00:00Z |
| `working_gas_bcf` |  | bcf | 7016 | 2010-01-01T00:00:00Z | 2026-10-16T00:00:00Z |

### `generation_mix_hourly_profile`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 167573.

- **Source:** erw:generation_mix_hourly EIA Form EIA-930 hourly net generation by energy source, the per-BA workbooks ( California from 2025-12-16T08:00:00Z is CAISO's own supply by fuel (caiso_fuel_supply; source erw:generation_mix_hourly_caiso), the warehouse's one join (docs/methods/eia930_caiso_break.md); read by this run from warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175834.883363Z_00002_CISO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175850.712544Z_00004_ERCO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175904.395449Z_00006_ISNE.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175918.956497Z_00008_MISO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175934.677962Z_00010_NYIS.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175949.986042Z_00012_PJM.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T180008.741327Z_00014_SWPP.xlsx (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx)
- **Method note:** [`docs/methods/generation_mix_hourly.md`](../methods/generation_mix_hourly.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The energy mix by hour: the average day of each month and the records, from EIA-930 (docs/methods/generation_mix_hourly.md); The same for California from 2025-12-16, from CAISO's own supply by fuel (docs/methods/eia930_caiso_break.md). Via the Energy Research Warehouse (ERW), table `generation_mix_hourly_profile`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | iso:caiso, iso:ercot, iso:isone, iso:miso, iso:nyiso, iso:pjm, iso:spp | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-10-01T00:00:00Z; 94 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -243323.0 to 90489896.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-CA, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 167573 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 167573 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:generation_mix_hourly, erw:generation_mix_hourly_caiso | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/generation_mix_hourly.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T18:22:33Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 167573 |

Variables (259):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `avg_coal_mw_h00` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h01` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h02` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h03` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h04` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h05` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h06` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h07` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h08` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h09` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h10` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h11` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h12` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h13` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h14` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h15` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h16` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h17` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h18` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h19` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h20` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h21` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h22` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h23` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h00` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h01` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h02` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h03` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h04` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h05` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h06` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h07` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h08` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h09` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h10` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h11` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h12` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h13` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h14` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h15` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h16` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h17` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h18` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h19` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h20` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h21` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h22` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h23` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h00` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h01` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h02` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h03` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h04` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h05` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h06` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h07` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h08` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h09` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h10` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h11` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h12` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h13` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h14` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h15` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h16` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h17` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h18` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h19` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h20` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h21` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h22` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h23` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h00` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h01` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h02` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h03` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h04` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h05` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h06` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h07` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h08` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h09` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h10` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h11` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h12` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h13` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h14` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h15` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h16` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h17` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h18` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h19` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h20` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h21` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h22` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h23` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h00` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h01` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h02` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h03` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h04` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h05` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h06` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h07` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h08` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h09` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h10` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h11` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h12` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h13` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h14` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h15` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h16` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h17` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h18` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h19` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h20` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h21` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h22` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h23` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h00` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h01` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h02` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h03` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h04` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h05` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h06` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h07` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h08` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h09` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h10` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h11` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h12` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h13` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h14` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h15` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h16` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h17` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h18` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h19` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h20` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h21` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h22` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h23` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h00` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h01` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h02` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h03` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h04` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h05` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h06` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h07` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h08` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h09` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h10` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h11` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h12` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h13` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h14` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h15` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h16` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h17` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h18` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h19` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h20` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h21` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h22` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h23` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h00` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h01` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h02` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h03` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h04` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h05` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h06` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h07` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h08` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h09` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h10` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h11` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h12` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h13` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h14` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h15` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h16` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h17` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h18` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h19` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h20` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h21` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h22` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h23` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h00` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h01` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h02` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h03` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h04` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h05` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h06` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h07` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h08` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h09` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h10` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h11` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h12` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h13` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h14` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h15` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h16` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h17` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h18` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h19` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h20` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h21` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h22` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h23` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h00` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h01` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h02` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h03` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h04` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h05` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h06` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h07` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h08` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h09` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h10` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h11` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h12` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h13` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h14` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h15` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h16` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h17` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h18` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h19` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h20` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h21` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h22` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h23` |  | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `coal_mwh` |  | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `coal_share_pct` |  | pct | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `days_held` |  | count | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `days_in_month` |  | count | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `hydro_mwh` |  | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `hydro_share_pct` |  | pct | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `natural_gas_mwh` |  | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `natural_gas_share_pct` |  | pct | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `net_generation_mwh` |  | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `nuclear_mwh` |  | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `nuclear_share_pct` |  | pct | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `other_mwh` |  | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `other_share_pct` |  | pct | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_mwh` |  | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_share_pct` |  | pct | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `storage_mwh` |  | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `storage_share_pct` |  | pct | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_mwh` |  | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_share_pct` |  | pct | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |

### `generation_mix_records`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 306.

- **Source:** erw:generation_mix_hourly EIA Form EIA-930 hourly net generation by energy source, the per-BA workbooks ( California from 2025-12-16T08:00:00Z is CAISO's own supply by fuel (caiso_fuel_supply; source erw:generation_mix_hourly_caiso), the warehouse's one join (docs/methods/eia930_caiso_break.md); read by this run from warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175834.883363Z_00002_CISO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175850.712544Z_00004_ERCO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175904.395449Z_00006_ISNE.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175918.956497Z_00008_MISO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175934.677962Z_00010_NYIS.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175949.986042Z_00012_PJM.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T180008.741327Z_00014_SWPP.xlsx (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx)
- **Method note:** [`docs/methods/generation_mix_hourly.md`](../methods/generation_mix_hourly.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The energy mix by hour: the average day of each month and the records, from EIA-930 (docs/methods/generation_mix_hourly.md); The same for California from 2025-12-16, from CAISO's own supply by fuel (docs/methods/eia930_caiso_break.md). Via the Energy Research Warehouse (ERW), table `generation_mix_records`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | iso:caiso, iso:ercot, iso:isone, iso:miso, iso:nyiso, iso:pjm, iso:spp | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-14T05:00:00Z to 2026-10-31T06:00:00Z; 233 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.59 to 766.49; 249 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kgCO2/MWh, pct | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-CA, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 306 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 306 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:generation_mix_hourly, erw:generation_mix_hourly_caiso | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/generation_mix_hourly.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T18:22:33Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 306 |
| `x_period` | not yet written |  | text | 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, all | 0 |
| `x_side` | not yet written |  | text | caiso, eia930 | 0 |

Variables (10):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `cleanest_hour_kgco2_per_mwh` |  | kgCO2/MWh | 7 | 2019-05-07T05:00:00Z | 2026-10-18T16:00:00Z |
| `dirtiest_hour_kgco2_per_mwh` |  | kgCO2/MWh | 7 | 2019-01-17T04:00:00Z | 2026-01-26T02:00:00Z |
| `solar_share_max_pct` |  | pct | 6 | 2026-04-26T18:00:00Z | 2026-10-17T20:00:00Z |
| `wind_share_max_pct` |  | pct | 7 | 2021-05-08T09:00:00Z | 2026-10-31T06:00:00Z |
| `wind_solar_share_max_pct` |  | pct | 7 | 2021-05-08T09:00:00Z | 2026-10-18T15:00:00Z |
| `year_cleanest_hour_kgco2_per_mwh` |  | kgCO2/MWh | 56 | 2019-05-07T05:00:00Z | 2026-10-18T18:00:00Z |
| `year_dirtiest_hour_kgco2_per_mwh` |  | kgCO2/MWh | 56 | 2019-01-14T05:00:00Z | 2026-10-04T07:00:00Z |
| `year_solar_share_max_pct` |  | pct | 48 | 2019-04-14T21:00:00Z | 2026-10-17T20:00:00Z |
| `year_wind_share_max_pct` |  | pct | 56 | 2019-03-15T06:00:00Z | 2026-10-31T06:00:00Z |
| `year_wind_solar_share_max_pct` |  | pct | 56 | 2019-03-15T06:00:00Z | 2026-10-18T15:00:00Z |

### `generator_pipeline_by_grid`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 5147.

- **Source:** eia:860m U.S. Energy Information Administration, EIA-860M Monthly Update to the Annual Electric Generator Report
- **Method note:** [`docs/methods/generator_pipeline_by_grid.md`](../methods/generator_pipeline_by_grid.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. EIA-860M's generator pipeline by grid and its monthly moves (docs/methods/generator_pipeline_by_grid.md). Via the Energy Research Warehouse (ERW), table `generator_pipeline_by_grid`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example eia860m_pipeline:AECI:MO:NG:U:2027, eia860m_pipeline:AECI:MO:WND:P:2029, eia860m_pipeline:AECI:OK:NG:V:2027; 924 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-08-01T00:00:00Z, 2026-09-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 8832.0; 598 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 53 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 5147 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 5147 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:generator_pipeline_by_grid | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/electricity/data/eia860m/ | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-06T08:20:13Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | text | 2026-08, 2026-09 | 0 |
| `x_ba` | not yet written |  | text | for example AECI, AVA, AVRN; 50 distinct | 0 |
| `x_state` | not yet written |  | text | for example AK, AL, AR; 52 distinct | 134 |
| `x_energy_source` | not yet written |  | text | AB, DFO, GEO, H2, LFG, MSW, MWH, NG, NUC, OBG, OBL, OBS, OTH, SUN, WAT, WH, WND | 134 |
| `x_status` | not yet written |  | text | L, P, T, TS, U, V | 134 |
| `x_planned_year` | not yet written |  | integer | 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2039 | 134 |
| `x_from_vintage` | not yet written |  | text | 2026-08 | 5013 |

Variables (13):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `datacenter_mw` |  | MW | 1671 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `entered_count` |  | count | 14 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `entered_mw` |  | MW | 14 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `left_count` |  | count | 5 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `left_mw` |  | MW | 5 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `online_count` |  | count | 18 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `online_mw` |  | MW | 18 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `planned_count` |  | count | 1671 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `planned_mw` |  | MW | 1671 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `slipped_count` |  | count | 12 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `slipped_mw` |  | MW | 12 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `status_moved_count` |  | count | 18 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `status_moved_mw` |  | MW | 18 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `hub_price_comparison`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 880.

- **Source:** erw:hub_price_comparison from each grid operator's public price reports (CAISO OASIS; ERCOT NP4-180-ER, NP4-190-CD, NP6-785-ER, NP6-905-CD; ISO-NE hourly and five-minute LMPs; NYISO zonal LBMPs; SPP LMP by settlement location) and from EIA-930 emissions
- **Method note:** [`docs/methods/hub_price_comparison.md`](../methods/hub_price_comparison.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Where power is cheap: hub and zone prices compared (docs/methods/hub_price_comparison.md). Via the Energy Research Warehouse (ERW), table `hub_price_comparison`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, caiso:TH_ZP26_GEN-APND; 39 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-11-01T00:00:00Z, 2026-10-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 8760.0; 375 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count, kgCO2/MWh, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M, P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 880 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example .H.INTERNAL_HUB, .Z.CONNECTICUT, .Z.MAINE; 39 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:hub_price_comparison | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/hub_price_comparison.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-17T07:41:45Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 880 |

Variables (18):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dam_above_200_hours_share_pct` |  | pct | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_avg_price` |  | USD/MWh | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_daily_spread_days` |  | count | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_daily_spread_mean_top4_bottom4` |  | USD/MWh | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_day_spread_top4_bottom4` |  | USD/MWh | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_hours_held` |  | count | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_hours_in_window` |  | count | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_negative_hours_share_pct` |  | pct | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `grid_carbon_days_held` |  | count | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `grid_carbon_intensity` |  | kgCO2/MWh | 54 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_above_200_hours_share_pct` |  | pct | 38 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_avg_price` |  | USD/MWh | 38 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_daily_spread_days` |  | count | 38 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_daily_spread_mean_top4_bottom4` |  | USD/MWh | 38 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_day_spread_top4_bottom4` |  | USD/MWh | 38 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_hours_held` |  | count | 38 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_hours_in_window` |  | count | 38 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_negative_hours_share_pct` |  | pct | 38 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |

### `known_data_faults`

What a row is: not yet written.

Shape: events. Keys: `event_id`. License: public; tier: derived. Rows read on 2026-11-20: 30.

- **Source:** erw:known_data_faults the ERW's register of faults found in its sources' data (warehouse/faults/faults.yaml), each entry naming where it is recorded
- **Method note:** [`docs/methods/known_data_faults.md`](../methods/known_data_faults.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Known faults in source data: the register of what each publisher's data holds that is wrong, missing, shifted or impossible (docs/methods/known_data_faults.md). Via the Energy Research Warehouse (ERW), table `known_data_faults`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | none | text | for example data_fault:caiso_curtailment_reason_blank, data_fault:caiso_curtailment_workbooks_overlap, data_fault:caiso_oasis_autumn_clock_day; 30 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2018-07-20, 2019-01-01, 2019-02-13, 2019-02-26, 2019-04-18, 2019-10-01, 2019-12-11, 2019-12-12, 2020-01-01, 2020-04-10, 2021-02-01, 2022-01-01, 2023-08-10, 2023-11-01, 2024-07-19, 2024-10-23, 2024-11-03, 2025-01-01, 2025-08-27, 2025-11-02, 2025-12-06, 2025-12-16, 2026-01-21, 2026-03-08, 2026-11-16 | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others) | none | text | data_fault | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | text | California ISO (CAISO), Electric Reliability Council of Texas (ERCOT), Large Load Interconnection Status Update, Federal Energy Regulatory Commission (FERC), Electric Quarterly Reports, ISO New England; New York ISO, Lawrence Berkeley National Laboratory and GridTracker, Queued Up 2026 Edition, U.S. Energy Information Administration (EIA), Form EIA-930, U.S. Energy Information Administration (EIA), Forms EIA-930 and EIA-860M | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | text | for example ba_supply_monthly, caiso_curtailment_intervals, caiso_curtailment_intervals;caiso_curtailment_daily; 26 distinct | 1 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 30 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 30 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 30 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | corrected, held_as_published, screened, worked_around | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:known_data_faults | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/known_data_faults.md | 0 |
| `x_title` | not yet written |  | text | for example 24 hours of demand in the Winter Storm Uri window have no number at the source, A contract rate in FERC's quarterly reports that cannot be a monthly price, Berkeley Lab's queue file: missing years, statuses and operation dates; 30 distinct | 0 |
| `x_first` | not yet written |  | date | 2018-07-20, 2019-01-01, 2019-02-13, 2019-02-26, 2019-04-18, 2019-10-01, 2019-12-11, 2019-12-12, 2020-01-01, 2020-04-10, 2021-02-01, 2022-01-01, 2023-08-10, 2023-11-01, 2024-07-19, 2024-10-23, 2024-11-03, 2025-01-01, 2025-08-27, 2025-11-02, 2025-12-06, 2025-12-16, 2026-01-21, 2026-03-08 | 6 |
| `x_last` | not yet written |  | date | 2019-03-31, 2020-07-13, 2020-08-24, 2021-02-28, 2022-12-31, 2023-06-13, 2024-11-21, 2024-12-31, 2025-05-31, 2025-06-21, 2025-08-27, 2025-11-02, 2025-12-02, 2025-12-14, 2025-12-31, 2026-01-25, 2026-02-10, 2026-03-08, 2026-03-26, 2026-08-20, 2026-08-29, 2026-09-22, 2026-09-30 | 7 |
| `x_dates_note` | not yet written |  | text | for example 38 hours not used; most from 13 February to 10 May 2019, then 19 to 22 December 2019, 8 October 2020, 31 July 2025 and 25 January 2026, 63 held hours by the rule: California 41, New York 13, PJM 6, New England 2, SPP 1 (measured in session 118 on the workbooks retrieved 2026-10-04), 7,869 hours in a row, from the hour starting 2019-10-01T21:00Z to the hour starting 2020-08-24T17:00Z, both included (measured in session 118 on the workbook retrieved 2026-10-04); 30 distinct | 0 |
| `x_publisher_source` | not yet written |  | text | caiso:PRC_LMP, caiso:daily_renewable_report, caiso:production_curtailments, caiso:todays_outlook_fuelsource, eia930:daily_interchange, eia:860m, eia:electricity/rto/region-data, eia:gridmonitor/knownissues/xls, ercot:large_load_status_update, ferc:eqr, isone:rt_lmp_hourly_final, lbnl:queued_up | 0 |
| `x_evidence` | not yet written |  | text | for example 1,505 MW at 2025-06-21T09:00Z (04:00 Central), the hours around it 34,479; and 24,991 MW at 2024-07-19T04:00Z, the hours around it 35,083. 48 more hours are blank., 24 hours of demand in the Uri window had no number at the source and were not written (session 68)., 525,129 MW at 2020-04-10T03:00Z, the hours around it 380,115: the rule leaves that hour out. PJM's 224,345 MW of 2020-07-13T22:00Z is inside the Lower 48's 776,575 MW of the same hour, which stands only 12 percent above the hours around it and passes the rule.; 30 distinct | 0 |
| `x_erw_does` | not yet written |  | text | for example A blank reason is kept blank ("local or system" is not guessed). The reason reaches back to 2022 in the interval table., A day that is not whole is not written; March, August and September 2026 then have no monthly figure for California. Nothing is filled., A day with a missing interval is not written. A twelve-month figure is written only when 95 percent of its hours are held, so ISO-NE's real-time figure in hub_price_comparison is not written.; 30 distinct | 0 |
| `x_open` | not yet written |  | text | A faulty hour inside the sum cannot be screened from the sum., A rule to fill a single missing interval was recommended in session 65 and not applied., EIA does not say why its California demand of early 2019 is low; CAISO's own load is the comparison, not a correction applied., EIA does not say why the column changed, nor whether the earlier rows will be published again as net output., Not applied in cost_of_power_monthly, which weighs SPP's price of June 2025 by that hour's 1,505 MW, nor in the other tables a live page reads., Not applied in the tables a live page reads (ba_supply_monthly, the cost of power tables, ai_power_regions) nor in the source table eia930_all_emissions, which holds EIA's hours as published. The Lower 48's demand is EIA's sum, with PJM's faulty hours inside it., Not applied in the tables a live page reads, nor in the source table, as for PJM., Not explained., The cause is not recorded., The energy mix tables test an hour another way (its sources must add up to its total), and are not put to this rule for generation: whether they should be is a ruling to make., The held carbon build is not yet the table: carbon_intensity_hourly, _daily and _monthly still carry those hours as EIA published them, so California's intensity there is computed without hydro until a person approves the build. eia930_all_generation is the source table and keeps them., The live /network page's hourly links are not screened: rule C is a rule for days. Settled in session 118: the supply table's count (2,732) and the replay's (1,072) count different things. The first is every report of every pair, both sides; 1,259 of them are between authorities the network draws, on 1,252 pair-days; the replay uses one report a pair and day and counts a day only when the report it used is left out., The looser test is a session's choice, not yet ruled on. PJM's residual since May 2025 is flagged as unexplained (session 73)., The two clock-change days are a limit of the ERW's conversion, not of CAISO's file., What the generation EIA stopped counting is, is not settled by these data. EIA's known-issues page refused a plain request (HTTP 403), so EIA's own account of the change was not read., Whether the 13 March figures were for part of the month is not said in either report., Whether the ERW's extract should read EIA's Adjusted columns in place of the unadjusted ones is a ruling to make: EIA has already replaced these values there, with its own imputation, which is a fill the ERW would then inherit., Which of the two forms is off (output or the inventory's MW) is not known., Which of the two is misstated is not known., Why is not known. Not corrected: eia930_all_emissions, the carbon intensity tables, ba_supply_monthly, ai_power_regions and event_window_daily hold the hours as EIA stamped them. From July 2018 to mid June 2022 the same measure sits about half an hour early; that is seen and not corrected., caiso_curtailment_daily uses the reason only from 2024., eia930_all_generation holds those hours as published. | 7 |
| `x_recorded_in` | not yet written |  | text | session 106; docs/methods/ercot_large_load_status.md, session 118; docs/methods/impossible_hours.md, session 68, session 7019 (chain 301); docs/methods/shoulder_hours.md; docs/state/data_requests_done_line.md, row 6, session 7022 (chain 301); docs/methods/demand_growth.md; docs/state/data_requests_done_line.md, row 38, session 72, session 73, session 73; docs/methods/eia930_caiso_break.md, session 81, session 94, session 94; docs/methods/generation_mix_hourly.md, session 95; docs/methods/interconnection_queue_summary.md, session 97; docs/methods/demand_growth.md, session 97; docs/methods/demand_growth.md; measured again by the rule on 2026-10-04, session 97; docs/methods/demand_growth.md; the dates measured by the rule on 2026-10-04, session 98, session 98; docs/methods/caiso_curtailment_intervals.md, sessions 49 and 64, sessions 49, 64, 65 and 96, sessions 62, 68 and 93; docs/methods/grid_network.md, sessions 62, 68 and 96, sessions 73 and 82; docs/methods/eia930_caiso_break.md, sessions 73 and 94, sessions 80 and 82; docs/methods/eia930_caiso_break.md | 0 |
| `x_resolution` | not yet written |  | text | fixed, held_for_approval, open | 0 |
| `x_resolution_reason` | not yet written |  | text | for example A day with a missing interval is not written. Session 65 recommended filling a single missing interval; the ERW's rule is to fill nothing, so it was not applied. Open for a ruling: the cost is ISO-NE's real-time twelve-month figure, which is not written., A faulty hour of one balancing authority cannot be taken out of EIA's sum. The rule leaves out the one hour of the sum that fails it (2020-04-10T03:00Z), and the Lower 48 is given no peak. The Lower 48's consumed intensity of April 2020 goes with the held carbon build. It stays open until EIA republishes the hours or the ERW builds its own sum from the screened authorities, which no session has been asked to do., A gap at the source: there is nothing for the ERW to fix, and nothing is filled. Each figure says how many days it rests on. Open because EIA has not been asked why SPP's days are missing, and a figure for SPP that rests on 200 of 365 days is a weak one however plainly it says so.; 30 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T20:49:30Z | 0 |

### `merchant_revenue_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 8853.

- **Source:** erw:merchant_revenue ERW derived table, the seller's side of the cost of power (docs/methods/cost_of_power.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/cost_of_power.md)
- **Method note:** [`docs/methods/cost_of_power.md`](../methods/cost_of_power.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Merchant revenue per MW by ISO hub, asset and month (docs/methods/cost_of_power.md). Via the Energy Research Warehouse (ERW), table `merchant_revenue_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:TH_SP15_GEN-APND, ercot:HB_HUBAVG, isone:.H.INTERNAL_HUB, miso:INDIANA.HUB, nyiso:N.Y.C., spp:SPPNORTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-06-01T00:00:00Z to 2026-10-01T00:00:00Z; 101 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -4275.8263 to 1017690.3025; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh/MW, USD/MW, USD/MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-IN, US-KS,US-NE,US-OK, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_rtm, ercot_rtm, isone_rtm, miso_rtm, nyiso_rtm, spp_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | .H.INTERNAL_HUB, HB_HUBAVG, INDIANA.HUB, N.Y.C., SPPNORTH_HUB, TH_SP15_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:merchant_revenue | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/cost_of_power.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-19T22:20:44Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 8853 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48) | none | text | ciso, erco, isne, miso, nyis, swpp | 0 |

Variables (37):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `battery_2h_capture_price` |  | USD/MWh | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_2h_capture_rate` |  | pct | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_2h_energy_per_mw` |  | MWh/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_2h_flat_price` |  | USD/MWh | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_2h_hours` |  | count | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_2h_revenue_per_mw` |  | USD/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_2h_sales_per_mw` |  | USD/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_4h_capture_price` |  | USD/MWh | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_4h_capture_rate` |  | pct | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_4h_energy_per_mw` |  | MWh/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_4h_flat_price` |  | USD/MWh | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_4h_hours` |  | count | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_4h_revenue_per_mw` |  | USD/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_4h_sales_per_mw` |  | USD/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `flat_price` |  | USD/MWh | 245 | 2018-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `hours_in_month` |  | count | 245 | 2018-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `peaker_capture_price` |  | USD/MWh | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `peaker_capture_rate` |  | pct | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `peaker_energy_per_mw` |  | MWh/MW | 245 | 2018-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `peaker_flat_price` |  | USD/MWh | 245 | 2018-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `peaker_hours` |  | count | 245 | 2018-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `peaker_revenue_per_mw` |  | USD/MW | 245 | 2018-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `peaker_sales_per_mw` |  | USD/MW | 245 | 2018-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_capture_price` |  | USD/MWh | 218 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_capture_rate` |  | pct | 218 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_energy_per_mw` |  | MWh/MW | 218 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_flat_price` |  | USD/MWh | 218 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_hours` |  | count | 218 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_revenue_per_mw` |  | USD/MW | 218 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_sales_per_mw` |  | USD/MW | 218 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_capture_price` |  | USD/MWh | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_capture_rate` |  | pct | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_energy_per_mw` |  | MWh/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_flat_price` |  | USD/MWh | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_hours` |  | count | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_revenue_per_mw` |  | USD/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_sales_per_mw` |  | USD/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |

### `nlr_jedi_multipliers`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 5562.

- **Source:** nlr:jedi National Laboratory of the Rockies (NLR, formerly NREL), Jobs and Economic Development Impact (JEDI) models (https://www.nlr.gov/analysis/jedi/models)
- **Method note:** [`docs/methods/economic_impact.md`](../methods/economic_impact.md)
- **Cite as:** National Laboratory of the Rockies (NLR, formerly NREL). Jobs and Economic Development Impact (JEDI) models: land-based wind W9.14.18, photovoltaics PV05.20.21, natural gas NG4.17.17, geothermal GT12.23.16. Via the Energy Research Warehouse (ERW), table `nlr_jedi_multipliers`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example nlr_jedi:geothermal:ak:all:project, nlr_jedi:geothermal:ak:construction:induced, nlr_jedi:geothermal:ak:construction:onsite; 2266 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z, 2017-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.008795 to 10251979.272115; 4347 distinct | 0 |
| `unit` | The unit of the row's value | none | text | FTE-year/MW, FTE/MW, MW, USD/MW, USD/MW-year, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 5562 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 5562 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nlr:jedi | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nlr.gov/docs/libraries/analysis/01d-jedi-geothermal-model-rel-gt12-23-16.xlsm, https://www.nlr.gov/docs/libraries/analysis/01d-jedi-land-based-wind-model-rel-w6-28-19.xlsm?sfvrsn=e1d95728_2, https://www.nlr.gov/docs/libraries/analysis/01d-jedi-ngas-model_rel-ng4-17-17.xlsm?sfvrsn=d9ff898_2, https://www.nlr.gov/docs/libraries/analysis/jedi-pv-model.xlsm?sfvrsn=837efebd_2 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-20T07:53:08Z, 2026-10-20T07:53:10Z, 2026-10-20T07:53:12Z, 2026-10-20T07:53:15Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 5562 |
| `x_technology` | not yet written |  | text | geothermal, land_based_wind, natural_gas, utility_pv | 0 |
| `x_state` | not yet written |  | text | for example AK, AL, AR; 51 distinct | 108 |
| `x_location` | not yet written |  | text | for example ALABAMA, ALASKA, ARIZONA; 54 distinct | 0 |
| `x_phase` | not yet written |  | text | all, construction, operations | 0 |
| `x_effect` | not yet written |  | text | induced, onsite, project, spending, supply_chain, total | 0 |
| `x_model` | not yet written |  | text | JEDI Geothermal Model, JEDI Land-based Wind Model, JEDI Natural Gas Model, JEDI Photovoltaics Model | 0 |
| `x_version` | not yet written |  | text | GT12.23.16, NG4.17.17, PV05.20.21, W9.14.18 | 0 |
| `x_file` | not yet written |  | text | 01d-jedi-geothermal-model-rel-gt12-23-16.xlsm, 01d-jedi-land-based-wind-model-rel-w6-28-19.xlsm, 01d-jedi-ngas-model_rel-ng4-17-17.xlsm, jedi-pv-model.xlsm | 0 |
| `x_sheet` | not yet written |  | text | Summary Results, SummaryResults | 0 |
| `x_cells` | not yet written |  | text | for example Summary Results!B23 / Summary Results!B7, Summary Results!B26 / Summary Results!B7, Summary Results!B27 / Summary Results!B7; 91 distinct | 0 |
| `x_project_mw` | not yet written |  | number | 100.0, 12.226196, 300.0, 500.0 | 0 |
| `x_mw_basis` | not yet written |  | text | DC nameplate MW, nameplate MW, nameplate MW (the model's 10 MW net output) | 0 |
| `x_dollar_year` | not yet written |  | integer | 2010, 2017 | 0 |
| `x_multiplier_data` | not yet written |  | text | Multipliers!D2 (Year of Data) 2014; the sheet's note: Source: IMPLAN™, using 2012 state data., Multipliers!D2 (Year of Data) 2014; the sheet's note: Source: IMPLAN™, using 2014 state data., Multipliers!D2 (Year of Data) 2016; the sheet's note: Source: IMPLAN™, using 2016 state data., Multipliers!D2 (Year of Data) 2019; the sheet's note: Source: IMPLAN™, using 2019 state data. | 0 |
| `x_local_share` | not yet written |  | number | 0.027304 to 1.037868; 195 distinct | 206 |
| `x_local_share_cells` | not yet written |  | text | Summary Results!D11 / Summary Results!D10, Summary Results!D8 / Summary Results!D7, SummaryResults!C12 / SummaryResults!C11, SummaryResults!C14 / SummaryResults!C13, SummaryResults!C15 / SummaryResults!C14, SummaryResults!C17 / SummaryResults!C16, SummaryResults!C18 / SummaryResults!C17 | 206 |
| `x_settings` | not yet written |  | text | ProjectData!B15 = Utility | 4158 |
| `x_method` | not yet written |  | text | JEDI's formulas computed from the workbook's constants with Project Location set to this location and ProjectData!B15 = Utility; nothing else changed (warehouse/connectors/jedi_recalc.py), JEDI's formulas computed from the workbook's constants with Project Location set to this location; nothing else changed (warehouse/connectors/jedi_recalc.py), the workbook's saved project, computed from its constants (every saved figure reproduced) | 0 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `earnings` |  | USD/MW; USD/MW-year | 1648 | 2010-01-01T00:00:00Z | 2017-01-01T00:00:00Z |
| `jobs` |  | FTE-year/MW; FTE/MW | 1648 | 2010-01-01T00:00:00Z | 2017-01-01T00:00:00Z |
| `local_share` |  | ratio | 412 | 2010-01-01T00:00:00Z | 2017-01-01T00:00:00Z |
| `output` |  | USD/MW; USD/MW-year | 1648 | 2010-01-01T00:00:00Z | 2017-01-01T00:00:00Z |
| `project_mw` |  | MW | 206 | 2010-01-01T00:00:00Z | 2017-01-01T00:00:00Z |

### `node_basis_daily`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 1035045.

- **Source:** erw:node_basis ERW derived table, the node basis (docs/methods/node_basis.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/node_basis.md)
- **Method note:** [`docs/methods/node_basis.md`](../methods/node_basis.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT's settlement points against the hub, by day and by month (warehouse/derived/node_basis.py). Via the Energy Research Warehouse (ERW), table `node_basis_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example ercot:7RNCHSLR_ALL, ercot:A4_DGR1_RN, ercot:A4_DGR2_RN; 888 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-10-01T00:00:00Z to 2026-11-18T00:00:00Z; 383 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -650.1554 to 16571.1625; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_dam, ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example 7RNCHSLR_ALL, A4_DGR1_RN, A4_DGR2_RN; 888 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:node_basis | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/node_basis.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T17:34:43Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1035045 |
| `x_hub` | not yet written |  | text | HB_HUBAVG | 0 |
| `x_resource_type` | not yet written |  | text | for example CCGT90, CCLE90, CLLIG; 33 distinct | 0 |
| `x_class` | not yet written |  | text | gas, hub, mixed, other, solar, storage, wind, zone | 0 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dam_basis` |  | USD/MWh | 299831 | 2025-10-01T00:00:00Z | 2026-10-20T00:00:00Z |
| `dam_mean` |  | USD/MWh | 299831 | 2025-10-01T00:00:00Z | 2026-10-20T00:00:00Z |
| `dam_spread_4h` |  | USD/MWh | 299831 | 2025-10-01T00:00:00Z | 2026-10-20T00:00:00Z |
| `rtm_basis` |  | USD/MWh | 45184 | 2026-09-28T00:00:00Z | 2026-11-18T00:00:00Z |
| `rtm_mean` |  | USD/MWh | 45184 | 2026-09-28T00:00:00Z | 2026-11-18T00:00:00Z |
| `rtm_spread_4h` |  | USD/MWh | 45184 | 2026-09-28T00:00:00Z | 2026-11-18T00:00:00Z |

### `node_basis_summary`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 1344.

- **Source:** erw:node_basis ERW derived table, the node basis (docs/methods/node_basis.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/node_basis.md)
- **Method note:** [`docs/methods/node_basis.md`](../methods/node_basis.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT's settlement points against the hub, by day and by month (warehouse/derived/node_basis.py). Via the Energy Research Warehouse (ERW), table `node_basis_summary`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:HB_HUBAVG | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-10-01T00:00:00Z, 2025-11-01T00:00:00Z, 2025-12-01T00:00:00Z, 2026-01-01T00:00:00Z, 2026-02-01T00:00:00Z, 2026-03-01T00:00:00Z, 2026-04-01T00:00:00Z, 2026-05-01T00:00:00Z, 2026-06-01T00:00:00Z, 2026-07-01T00:00:00Z, 2026-08-01T00:00:00Z, 2026-09-01T00:00:00Z, 2026-10-01T00:00:00Z, 2026-11-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -32.0188 to 871.0; 1106 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_dam, ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | HB_HUBAVG | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:node_basis | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/node_basis.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T17:34:43Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1344 |
| `x_market` | not yet written |  | text | dam, rtm | 0 |
| `x_class` | not yet written |  | text | all, gas, solar, storage, wind, zone | 0 |
| `x_stat` | not yet written |  | text | basis_p10, basis_p25, basis_p50, basis_p75, basis_p90, days, hub_spread_4h, points, share_wider_pct, spread_4h_p10, spread_4h_p25, spread_4h_p50, spread_4h_p75, spread_4h_p90 | 0 |

Variables (168):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dam_all_basis_p10` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_basis_p25` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_basis_p50` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_basis_p75` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_basis_p90` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_days` |  | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_hub_spread_4h` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_points` |  | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_share_wider_pct` |  | pct | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_spread_4h_p10` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_spread_4h_p25` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_spread_4h_p50` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_spread_4h_p75` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_spread_4h_p90` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_basis_p10` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_basis_p25` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_basis_p50` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_basis_p75` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_basis_p90` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_days` |  | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_hub_spread_4h` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_points` |  | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_share_wider_pct` |  | pct | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_spread_4h_p10` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_spread_4h_p25` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_spread_4h_p50` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_spread_4h_p75` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_spread_4h_p90` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_basis_p10` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_basis_p25` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_basis_p50` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_basis_p75` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_basis_p90` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_days` |  | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_hub_spread_4h` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_points` |  | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_share_wider_pct` |  | pct | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_spread_4h_p10` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_spread_4h_p25` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_spread_4h_p50` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_spread_4h_p75` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_spread_4h_p90` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_basis_p10` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_basis_p25` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_basis_p50` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_basis_p75` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_basis_p90` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_days` |  | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_hub_spread_4h` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_points` |  | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_share_wider_pct` |  | pct | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_spread_4h_p10` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_spread_4h_p25` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_spread_4h_p50` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_spread_4h_p75` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_spread_4h_p90` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_basis_p10` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_basis_p25` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_basis_p50` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_basis_p75` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_basis_p90` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_days` |  | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_hub_spread_4h` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_points` |  | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_share_wider_pct` |  | pct | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_spread_4h_p10` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_spread_4h_p25` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_spread_4h_p50` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_spread_4h_p75` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_spread_4h_p90` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_basis_p10` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_basis_p25` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_basis_p50` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_basis_p75` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_basis_p90` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_days` |  | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_hub_spread_4h` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_points` |  | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_share_wider_pct` |  | pct | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_spread_4h_p10` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_spread_4h_p25` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_spread_4h_p50` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_spread_4h_p75` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_spread_4h_p90` |  | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_all_basis_p10` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_basis_p25` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_basis_p50` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_basis_p75` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_basis_p90` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_days` |  | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_hub_spread_4h` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_points` |  | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_share_wider_pct` |  | pct | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_spread_4h_p10` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_spread_4h_p25` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_spread_4h_p50` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_spread_4h_p75` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_spread_4h_p90` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_basis_p10` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_basis_p25` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_basis_p50` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_basis_p75` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_basis_p90` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_days` |  | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_hub_spread_4h` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_points` |  | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_share_wider_pct` |  | pct | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_spread_4h_p10` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_spread_4h_p25` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_spread_4h_p50` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_spread_4h_p75` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_spread_4h_p90` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_basis_p10` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_basis_p25` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_basis_p50` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_basis_p75` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_basis_p90` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_days` |  | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_hub_spread_4h` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_points` |  | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_share_wider_pct` |  | pct | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_spread_4h_p10` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_spread_4h_p25` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_spread_4h_p50` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_spread_4h_p75` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_spread_4h_p90` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_basis_p10` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_basis_p25` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_basis_p50` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_basis_p75` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_basis_p90` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_days` |  | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_hub_spread_4h` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_points` |  | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_share_wider_pct` |  | pct | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_spread_4h_p10` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_spread_4h_p25` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_spread_4h_p50` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_spread_4h_p75` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_spread_4h_p90` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_basis_p10` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_basis_p25` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_basis_p50` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_basis_p75` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_basis_p90` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_days` |  | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_hub_spread_4h` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_points` |  | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_share_wider_pct` |  | pct | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_spread_4h_p10` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_spread_4h_p25` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_spread_4h_p50` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_spread_4h_p75` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_spread_4h_p90` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_basis_p10` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_basis_p25` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_basis_p50` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_basis_p75` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_basis_p90` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_days` |  | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_hub_spread_4h` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_points` |  | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_share_wider_pct` |  | pct | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_spread_4h_p10` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_spread_4h_p25` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_spread_4h_p50` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_spread_4h_p75` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_spread_4h_p90` |  | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |

### `nuclear_fleet_status`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 15048.

- **Source:** eia:nuclear-outages U.S. Energy Information Administration, Status of U.S. Nuclear Outages (from the NRC's power reactor status reports); EIA-860M
- **Method note:** [`docs/methods/nuclear_fleet_status.md`](../methods/nuclear_fleet_status.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The U.S. reactor fleet by reactor and year, and by grid (docs/methods/nuclear_fleet_status.md). Via the Energy Research Warehouse (ERW), table `nuclear_fleet_status`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example nuclear_fleet:1060:1, nuclear_fleet:1590:1, nuclear_fleet:1715:1; 124 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z, 2026-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -88.9 to 804217344.384; 4533 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, count, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 15048 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Arkansas Nuclear One, reactor 1, Arkansas Nuclear One, reactor 2, Beaver Valley, reactor 1; 107 distinct | 1340 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:nuclear_fleet_status | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/nuclear_fleet_status.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T17:53:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 15048 |
| `x_facility` | not yet written |  | integer | 46 to 8907; 66 distinct | 1340 |
| `x_generator` | not yet written |  | integer | 1, 2, 3, 4 | 1340 |
| `x_ba` | not yet written |  | text | BPAT, CISO, CPLE, DUK, ERCO, FPL, ISNE, MISO, NYIS, PJM, SCEG, SOCO, SRP, SWPP, TVA, none | 80 |
| `x_first` | not yet written |  | date | 2007-01-01, 2015-10-27, 2022-10-13, 2023-08-21 | 1340 |
| `x_last` | not yet written |  | date | 2012-12-31, 2014-11-30, 2016-09-30, 2018-08-31, 2019-04-30, 2019-08-31, 2020-03-31, 2020-10-31, 2021-03-31, 2026-11-19 | 1340 |

Variables (8):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `available_mwh` |  | MWh | 2308 | 2007-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `capacity_change_mw` |  | MW | 1861 | 2008-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `capacity_mw` |  | MW | 2308 | 2007-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `days_held` |  | count | 1982 | 2007-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `full_outage_days` |  | count | 1973 | 2007-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `long_outages` |  | count | 1973 | 2007-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `outage_share` |  | ratio | 2308 | 2007-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `reactors` |  | count | 335 | 2007-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

### `region_weather_hourly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 879553.

- **Source:** erw:region_weather_hourly the ERW's weighted means of noaa_region_station_hourly_<year> (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/region_weather.md)
- **Method note:** [`docs/methods/region_weather.md`](../methods/region_weather.md)
- **Cite as:** Energy Research Warehouse. Region temperature, population weighted. Via the Energy Research Warehouse (ERW), table `region_weather_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | eia930:CAL, eia930:CAR, eia930:CENT, eia930:FLA, eia930:MIDA, eia930:MIDW, eia930:NE, eia930:NW, eia930:NY, eia930:SE, eia930:SW, eia930:TEN, eia930:TEX | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-01T00:00:00Z to 2026-11-07T14:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -10.44 to 114.22; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:region_weather_hourly | 0 |
| `x_stations` | not yet written |  | integer | 12, 14, 16, 17, 19, 20, 21, 22, 5 | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `temperature_f` |  | degF | 879553 | 2018-07-01T00:00:00Z | 2026-11-07T14:00:00Z |

### `resource_layer_features`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: derived. Rows read on 2026-11-20: 1371628.

- **Source:** erw:resource_layer_features the ERW's reduction of each publisher's file (warehouse/connectors/resource_layers.py): wind_speed_100m: National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL),  (sha256 3c9f29dedc92e6ef8107ba0272575d255d91fee6d96a7c455c8365bbeae6d109); solar_ghi: National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL),  (sha256 55531ec07a5f4c47c0c8fe74407f71ca4733fa221c843063b13c9c1f93bca4fc); solar_dni: National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL),  (sha256 97f0e7e621f6fef9d9b15f70a0163f46aa7a0837b66c1fe7d984fad0ff4c2dc0); wind_capacity_factor: National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL),  (sha256 ef13116bd66f31157b2f7db6369831d63f3098877e91c6163766dbe6da47eb7d); geothermal_hydrothermal_sites: U.S. Geological Survey (USGS),  (sha256 7724cb19112c68c21e50883d7fb73bbe6b98a872f6e319753b5c8c2f7df2bfc7); hydropower_npd: Oak Ridge National Laboratory (HydroSource), for the U.S. Department of Energy,  (sha256 84635b4faecc332c31ab53fbbd7c42be7469d75bb2c1ca3c6827d2ac296aaf2f); geothermal_hydrothermal_favorability: U.S. Geological Survey (USGS),  (sha256 d9eb255587626875580aab4c1705031d63717d79080b530ffe0ce30f206eff78); geothermal_egs_favorability: National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL),  (sha256 fdf8bcfb6dcc98252ae9a7d6389d27fa0c579d3a72021790b38bf3eb8b76c6af); oil_gas_basins: U.S. Energy Information Administration (EIA),  (sha256 02a017ccb84bdcc15726838098e3cfa73450b9655cf06e28d2eca6f3c04edcff); oil_gas_plays: U.S. Energy Information Administration (EIA),  (sha256 c09b3bd2982754cfb63d12bbbfde6c6c5e8c02eee73e54d231a7c7de73f0541e); hydropower_nsd: Oak Ridge National Laboratory (HydroSource), for the U.S. Department of Energy,  (sha256 a8ab06e4dfea4a31f1dd293d6358af932bd839f4a41d59a181600a3877fb28f9); biomass: National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL),  (sha256 f48ee40d6de1859d6f3cabc841b631a55287c4282bfe974719fd89555672f54d); coal_fields: usgs:of2012_1205_coal_fields  (sha256 e491215d0a937cae48cc5e9a2763ea43c85a4d11c183ec7c5b1ac559d2a585a5) (https://pubs.usgs.gov/of/2012/1205/Downloads/GIS.zip)
- **Method note:** [`docs/methods/resource_layers_table.md`](../methods/resource_layers_table.md)
- **Cite as:** Energy Research Warehouse (ERW), derived; National Laboratory of the Rockies (NLR, formerly NREL); Oak Ridge National Laboratory (HydroSource), for the U.S. Department of Energy; U.S. Energy Information Administration (EIA); U.S. Geological Survey (USGS). Favorability of deep enhanced geothermal systems, lower 48, shapefile (2009); Geothermal Favorability Map Derived From Logistic Regression Models (2008 assessment; ScienceBase, doi:10.5066/P137NMXE); Hydropower Potential from New Stream-Reach Development for the Conterminous United States, aggregated summary of HUC10 watersheds (2014, version 1); NSRDB Physical Solar Model version 3 Direct Normal Irradiance, multi-year (1998-2016) annual and monthly averages, GeoTIFF; NSRDB Physical Solar Model version 3 Global Horizontal Irradiance, multi-year (1998-2016) annual and monthly averages, GeoTIFF; Open-File Report 2012-1205: Coal fields of the conterminous United States, National Coal Resource Assessment updated version (East, 2013); Solid biomass resources by county, shapefile (data for 2012, published 2014); Technical Potential for Hydropower Capacity at Non-powered Dams (2024, revised 25 June 2025; doi:10.21951/HydroCapacity_NPD/2570407); The natural resource map's layers as a table (docs/methods/resource_layers_table.md); Tight Oil and Shale Gas Plays in the U.S., Lower 48, shapefile, updated December 2021; U.S. Sedimentary Basins, shapefile (EIA maps, layer information for interactive state maps); WIND Toolkit, Multi-year (2007-2013) Annual Average Wind Speed at all heights, GeoTIFF, 2 km. Via the Energy Research Warehouse (ERW), table `resource_layer_features`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example resource:wind_speed_100m:r0c685, resource:wind_speed_100m:r0c686, resource:wind_speed_100m:r0c687; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | resource | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example wind_speed_100m cell r0 c685, wind_speed_100m cell r0 c686, wind_speed_100m cell r0 c687; more than 5000 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 19.478 to 69.30839; more than 5000 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -176.616 to -65.675; more than 5000 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 1371628 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | empty | no cell holds a value | 1371628 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 1371628 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 1371628 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:resource_layer_features, usgs:of2012_1205_coal_fields | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://data.openei.org/files/8314/lbw_open_access_2035_moderate_115hh_170rd_supply_curve.csv, https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/hydropower-capacity-us-npd/TechPotentialNPDs.csv, https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/hydropower-potential-new-stream-reach-development-conterminous-united-states/ORNL_NHAAP_NSD_SR_All_v1.zip, https://pubs.usgs.gov/of/2012/1205/Downloads/GIS.zip, https://www.eia.gov/maps/map_data/SedimentaryBasins_US_EIA.zip, https://www.eia.gov/maps/map_data/TightOil_ShaleGas_Plays_Lower48_EIA.zip, https://www.nlr.gov/docs/libraries/gis/egs.zip, https://www.nlr.gov/docs/libraries/gis/nsrdbv3_dni.zip, https://www.nlr.gov/docs/libraries/gis/nsrdbv3_ghi.zip, https://www.nlr.gov/docs/libraries/gis/solid-biomass.zip, https://www.nlr.gov/docs/libraries/gis/us-wind-data.zip, https://www.sciencebase.gov/catalog/file/get/6606ed51d34e4df16bd58251?f=__disk__79%2Fb1%2Fce%2F79b1ce18796d6fc4ae5b9292c58bd8aaee4846e5, https://www.sciencebase.gov/catalog/file/get/6606f534d34e4df16bd58277?f=__disk__ae%2Fbd%2F32%2Faebd32c1cf3b64ce4f19dc6e2535e5a5bc3382da | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T21:26:20Z, 2026-10-07T21:33:22Z, 2026-10-07T21:33:58Z, 2026-10-07T21:34:33Z, 2026-10-07T21:39:30Z, 2026-10-07T21:39:32Z, 2026-10-07T21:39:34Z, 2026-10-07T21:39:39Z, 2026-10-07T21:39:41Z, 2026-10-08T08:45:07Z, 2026-10-08T08:47:16Z, 2026-11-19T12:39:54Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | text | 1998-2016 (the file's metadata: "The data are averaged from hourly model output over 19 years (1998-2016)"); publication date 2018, 2007-2013 (the file's metadata: "Multi-year (2007-2013) Annual Average Wind Speed, meters per second, at 100 meters above surface level"); publication date 2015, 2009 (the file's metadata: analyses "performed by NREL (2009)" on temperature at depth from Southern Methodist University Geothermal Laboratory, Blackwell and Richards, 2009); metadata dated 23 February 2012, 2013, as of 5-6-2011 (the file's metadata: "Sedimentary basins associated with the EIA shale plays as of 5-6-2011"); file modified 10 March 2016, data for 2012 (the file's metadata: "Data for 2012, in dry metric tons/year"); published 30 October 2014, published 3 October 2024, revised 25 June 2025 (HydroSource's page; the file on its server is dated 25 June 2025); the file's readme: "These estimates represent the conditions over the historical period of 1980-2015", published 31 December 2014 (HydroSource's page); the file's own metadata is dated 10 January 2014 and its workbook was created on 2013-03-15, version 1; the years of flow behind the estimate are not stated in the files, the 2008 assessment (USGS Fact Sheet 2008-3082); the data file is dated 2010 and was released again on ScienceBase on 29 March 2024 (metadata date 20240329), the 2008 assessment; the data file is dated 2010 and was released again on ScienceBase on 29 March 2024 (metadata date 20240329), the 2024 edition, published 2025-01-01 on the Open Energy Data Initiative; the file models a 2035 turbine ("2035 moderate", 115 m hub height, 170 m rotor diameter); the weather years behind the mean are not stated in the files, updated December 2021 (the file's metadata: "Updated December 2021 with addition of Spraberry and Wolfcamp Plays in the Permian Basin") | 0 |
| `x_layer` | not yet written |  | text | biomass, coal_fields, geothermal_egs_favorability, geothermal_hydrothermal_favorability, geothermal_hydrothermal_sites, hydropower_npd, hydropower_nsd, oil_gas_basins, oil_gas_plays, solar_dni, solar_ghi, wind_capacity_factor, wind_speed_100m | 0 |
| `x_kind` | not yet written |  | text | HUC10 watershed, coal field, county, deep enhanced geothermal favorability class, grid cell, relative favorability class, sedimentary basin, site, tight oil and shale gas play | 0 |
| `x_value` | not yet written |  | number | 0.0 to 2002700.0; more than 5000 distinct | 602 |
| `x_unit` | not yet written |  | text | MW, MWe, class (1 most favorable, 5 least favorable, 999 not assessed), class (the source's GRIDCODE, 1 to 10), dry metric tons/year, kWh/m2/day, m/s, ratio, square miles | 602 |
| `x_value_label` | not yet written |  | text | Mean Megawatts electric (MWe), the source's MWe_Mean, Mean capacity factor across 11.5km grid-cell (the source's capacity_factor_ac), Nominal capacity (the source's cap_mw), The HUC10-level Total Potential capacity from identified stream-reaches with capacity greater than 1MW (the source's P_MW_Sum, a HUC10 total), all solid biomass resources of the county (the source's Total), annual average daily total solar resource, annual mean wind speed, area of the basin (the source's Area_sq_mi), area of the play (the source's Area_sq_mi), coal field (province, age and rank as USGS gives them), relative favorability class (the source's GRIDCODE, with its Descript range), relative favorability of the deep enhanced geothermal resource (the source's CLASS) | 0 |
| `x_publisher` | not yet written |  | text | National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL), Oak Ridge National Laboratory (HydroSource), for the U.S. Department of Energy, U.S. Energy Information Administration (EIA), U.S. Geological Survey, U.S. Geological Survey (USGS) | 0 |
| `x_cell_deg` | not yet written |  | number | 0.05 | 66266 |
| `x_area_km2` | not yet written |  | number | 0.0 to 810228.9; more than 5000 distinct | 1364759 |
| `x_extra` | not yet written |  | text | for example {"Basin":"Anadarko","Lithology":"Shale","Shale_play":"Woodford","References":"Hand-drawn boundary around wells from OK Geol Surv","Source":"EIA","Area_sq_mi":3351.7712898,"Area_sq_km":8681.04778802,"ID":"WOO001","Age_shale":"Devonian"}, {"Basin":"Appalachian","Lithology":"Mixed Shale & Limestone","Shale_play":"Utica","References":"Appalachian Oil and Natural Gas Research Consortium, and USGS","Source":"EIA","Area_sq_mi":59054.2252868,"Area_sq_km":152949.741338,"ID":"UTI001","Age_shale":"Ordovician"}, {"Basin":"Appalachian","Lithology":"Shale","Shale_play":"Chattanooga","References":"5 TN counties with wells operated by CNX and Magellan","Source":"EIA","Area_sq_mi":1448.13143073,"Area_sq_km":3750.6431873,"ID":"CHA001","Age_shale":"Devonian"}; more than 5000 distinct | 1305362 |
| `x_source_sha256` | not yet written |  | text | 02a017ccb84bdcc15726838098e3cfa73450b9655cf06e28d2eca6f3c04edcff, 3c9f29dedc92e6ef8107ba0272575d255d91fee6d96a7c455c8365bbeae6d109, 55531ec07a5f4c47c0c8fe74407f71ca4733fa221c843063b13c9c1f93bca4fc, 7724cb19112c68c21e50883d7fb73bbe6b98a872f6e319753b5c8c2f7df2bfc7, 84635b4faecc332c31ab53fbbd7c42be7469d75bb2c1ca3c6827d2ac296aaf2f, 97f0e7e621f6fef9d9b15f70a0163f46aa7a0837b66c1fe7d984fad0ff4c2dc0, a8ab06e4dfea4a31f1dd293d6358af932bd839f4a41d59a181600a3877fb28f9, c09b3bd2982754cfb63d12bbbfde6c6c5e8c02eee73e54d231a7c7de73f0541e, d9eb255587626875580aab4c1705031d63717d79080b530ffe0ce30f206eff78, e491215d0a937cae48cc5e9a2763ea43c85a4d11c183ec7c5b1ac559d2a585a5, ef13116bd66f31157b2f7db6369831d63f3098877e91c6163766dbe6da47eb7d, f48ee40d6de1859d6f3cabc841b631a55287c4282bfe974719fd89555672f54d, fdf8bcfb6dcc98252ae9a7d6389d27fa0c579d3a72021790b38bf3eb8b76c6af | 0 |

### `scarcity_hours_by_grid`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 201873.

- **Source:** erw:scarcity_hours_by_grid ERW derived table, the scarcity signal rule (docs/methods/scarcity_hours_by_grid.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/scarcity_hours_by_grid.md)
- **Method note:** [`docs/methods/scarcity_hours_by_grid.md`](../methods/scarcity_hours_by_grid.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Each grid's own scarcity signal beside the USD 1,000 price count (warehouse/derived/scarcity_hours_by_grid.py). Via the Energy Research Warehouse (ERW), table `scarcity_hours_by_grid`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | iso:caiso, iso:ercot | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-11-01T06:00:00Z to 2026-11-01T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 0, 1, 2, 3, 4 | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_dam, caiso_rtm, ercot_dam, ercot_rtm | 44097 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | HB_HUBAVG, TH_SP15_GEN-APND | 44097 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:scarcity_hours_by_grid | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/scarcity_hours_by_grid.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-13T18:42:41Z, 2026-11-03T17:34:00Z, 2026-11-16T20:24:10Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 201873 |
| `x_detail` | not yet written |  | text | for example eea_watch@CAISO Grid, held=4, rmo@CAISO Grid; 351 distinct | 130312 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `da_hour_ge_1000` |  | count | 52608 | 2023-11-01T06:00:00Z | 2026-11-01T07:00:00Z |
| `own_signal` |  | count | 44097 | 2023-11-01T06:00:00Z | 2026-10-08T23:00:00Z |
| `rt_hour_ge_1000` |  | count | 52584 | 2023-11-01T06:00:00Z | 2026-11-01T07:00:00Z |
| `rt_intervals_ge_1000` |  | count | 52584 | 2023-11-01T06:00:00Z | 2026-11-01T07:00:00Z |

### `shoulder_hours_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 27489.

- **Source:** erw:shoulder_hours EIA Form EIA-930 hourly demand and net generation by energy source, the per-BA workbooks ( and CAISO's supply by fuel (caiso_fuel_supply); read by this run from warehouse/raw/eia930_emissions/20261102T174348Z/20261102T174425.135109Z_00004_ERCO.xlsx; warehouse/raw/eia930_emissions/20261102T174348Z/20261102T174403.134912Z_00002_CISO.xlsx; warehouse/output/caiso_fuel_supply.csv (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx)
- **Method note:** [`docs/methods/shoulder_hours.md`](../methods/shoulder_hours.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The shoulder hours by grid and month (docs/methods/shoulder_hours.md). Via the Energy Research Warehouse (ERW), table `shoulder_hours_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | iso:caiso, iso:caiso_own, iso:ercot | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-10-17T00:00:00Z; 254 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -9165.1917 to 122254.2917; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, count, hour, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1D, P1M, P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 27489 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 27489 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:shoulder_hours | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/shoulder_hours.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-03T17:32:48Z, 2026-11-03T17:33:05Z, 2026-11-03T17:33:08Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 27489 |

Variables (192):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `avg_battery_mw_h00` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h01` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h02` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h03` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h04` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h05` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h06` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h07` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h08` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h09` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h10` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h11` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h12` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h13` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h14` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h15` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h16` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h17` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h18` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h19` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h20` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h21` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h22` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h23` |  | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h00` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h01` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h02` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h03` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h04` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h05` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h06` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h07` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h08` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h09` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h10` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h11` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h12` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h13` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h14` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h15` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h16` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h17` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h18` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h19` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h20` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h21` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h22` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h23` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h00` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h01` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h02` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h03` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h04` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h05` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h06` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h07` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h08` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h09` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h10` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h11` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h12` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h13` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h14` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h15` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h16` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h17` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h18` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h19` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h20` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h21` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h22` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h23` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h00` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h01` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h02` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h03` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h04` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h05` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h06` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h07` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h08` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h09` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h10` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h11` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h12` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h13` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h14` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h15` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h16` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h17` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h18` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h19` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h20` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h21` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h22` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h23` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h00` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h01` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h02` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h03` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h04` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h05` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h06` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h07` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h08` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h09` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h10` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h11` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h12` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h13` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h14` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h15` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h16` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h17` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h18` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h19` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h20` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h21` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h22` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h23` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_mwh_per_day` |  | MWh | 97 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `day_battery_discharge_mwh` |  | MWh | 49 | 2024-11-13T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_battery_hours` |  | hour | 43 | 2024-11-13T00:00:00Z | 2026-09-26T00:00:00Z |
| `day_battery_peak_mw` |  | MW | 49 | 2024-11-13T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_evening_peak_mw` |  | MW | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_fleet_mw` |  | MW | 164 | 2019-01-01T00:00:00Z | 2026-09-26T00:00:00Z |
| `day_net_load_mean_mw` |  | MW | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_shoulder2_end_hour` |  | hour | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_shoulder2_hours` |  | hour | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_shoulder2_hours_needed` |  | hour | 164 | 2019-01-01T00:00:00Z | 2026-09-26T00:00:00Z |
| `day_shoulder2_mwh_above_midpoint` |  | MWh | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_shoulder2_start_hour` |  | hour | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_shoulder_hours` |  | hour | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_shoulder_hours_needed` |  | hour | 164 | 2019-01-01T00:00:00Z | 2026-09-26T00:00:00Z |
| `day_shoulder_mwh_above_mean` |  | MWh | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_shoulder_runs_to_midnight` |  | count | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_shoulder_start_hour` |  | hour | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `days_held` |  | count | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `days_in_month` |  | count | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `evening_peak_hour` |  | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `evening_peak_mw` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `fleet_hours` |  | hour | 190 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `fleet_mw` |  | MW | 190 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `fleet_mwh` |  | MWh | 190 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `midday_low_hour` |  | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `midday_surplus_hours` |  | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `midday_surplus_mwh` |  | MWh | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `net_load_mean_mw` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder2_end_hour` |  | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder2_hours` |  | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder2_hours_covered` |  | hour | 190 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `shoulder2_hours_needed` |  | hour | 190 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `shoulder2_level_mw` |  | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder2_mwh_above_midpoint` |  | MWh | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder2_runs_to_midnight` |  | count | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder2_start_hour` |  | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder_end_hour` |  | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder_hours` |  | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder_hours_covered` |  | hour | 190 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `shoulder_hours_needed` |  | hour | 190 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `shoulder_mwh_above_mean` |  | MWh | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder_runs_to_midnight` |  | count | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder_start_hour` |  | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `worst_rank` |  | count | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `year_days_ranked` |  | count | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_end_fleet_hours` |  | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_end_fleet_mw` |  | MW | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_end_fleet_mwh` |  | MWh | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_curtailed_mwh_per_day` |  | MWh | 9 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_midday_surplus_hours` |  | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_midday_surplus_mwh` |  | MWh | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder2_hours` |  | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder2_hours_covered` |  | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder2_hours_needed` |  | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder2_mwh_above_midpoint` |  | MWh | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder2_runs_to_midnight` |  | ratio | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder_hours` |  | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder_hours_covered` |  | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder_hours_needed` |  | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder_mwh_above_mean` |  | MWh | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder_runs_to_midnight` |  | ratio | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder_start_hour` |  | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_months_held` |  | count | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_worst10_days` |  | count | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_worst10_days_with_battery` |  | count | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_worst10_max_shoulder_hours_needed` |  | hour | 15 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `year_worst10_mean_battery_hours` |  | hour | 2 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `year_worst10_mean_shoulder2_hours` |  | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_worst10_mean_shoulder2_hours_needed` |  | hour | 15 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `year_worst10_mean_shoulder_hours` |  | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_worst10_mean_shoulder_hours_needed` |  | hour | 15 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `year_worst10_mean_shoulder_mwh_above_mean` |  | MWh | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

### `state_generation_mix_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 108125.

- **Source:** erw:generation_mix ERW derived table, generation mix method (docs/methods/generation_mix.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/generation_mix.md)
- **Method note:** [`docs/methods/generation_mix.md`](../methods/generation_mix.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Generation mix by state (docs/methods/generation_mix.md). Via the Energy Research Warehouse (ERW), table `state_generation_mix_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example eia:AK, eia:AL, eia:AR; 53 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 308 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -196301.07 to 209842940.95; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 53 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 108125 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 108125 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:generation_mix | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/generation_mix.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-27T08:14:19Z, 2026-10-22T14:48:54Z, 2026-10-23T14:45:12Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 108125 |

Variables (9):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `net_generation_coal_mwh` |  | MWh | 15258 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_generation_hydro_mwh` |  | MWh | 15171 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_generation_natural_gas_mwh` |  | MWh | 15716 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_generation_not_itemized_mwh` |  | MWh | 1081 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_generation_nuclear_mwh` |  | MWh | 9560 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_generation_oil_and_other_mwh` |  | MWh | 16104 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_generation_other_renewables_mwh` |  | MWh | 15306 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_generation_solar_mwh` |  | MWh | 8649 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_generation_wind_mwh` |  | MWh | 11280 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `state_large_load_laws`

What a row is: not yet written.

Shape: events. Keys: `event_id`. License: public; tier: model_extracted. Rows read on 2026-11-20: 27.

- **Source:** research:large_load_2026-11-13, docs/research/large_load/legislation_2026-11-13.csv (window P4 of the portable laptop, sessions 5300 to 5304; method  each row's source_url is the document it was read in. No request is made by this connector. (https://github.com/SamuelEnrique/erw/blob/main/docs/research/large_load/README.md)
- **Method note:** [`docs/methods/large_load_research.md`](../methods/large_load_research.md)
- **Cite as:** US utilities, state commissions and legislatures, read by the ERW's research pass. Large-load rules, their changes and the states' laws (docs/research/large_load, 13 and 14 November 2026). Via the Energy Research Warehouse (ERW), table `state_large_load_laws`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | none | text | for example lllaw:laws_midwest_northeast-01, lllaw:laws_midwest_northeast-02, lllaw:laws_midwest_northeast-03; 27 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2025-03-25, 2025-04-17, 2025-04-24, 2025-05-12, 2025-05-20, 2025-06-14, 2025-06-16, 2025-07-11, 2025-08-28, 2026-02-26, 2026-03-19, 2026-03-23, 2026-03-24, 2026-04-08, 2026-04-10, 2026-04-14, 2026-05-07, 2026-05-12, 2026-05-29, 2026-06-04, 2026-07-07, 2026-08-26, 2026-11-13, 2026-11-14 | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others) | none | text | large_load_law | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | text | AL legislature, CT legislature, DE legislature, FL legislature, IA legislature, ID legislature, KS legislature, MA legislature, MD legislature, MI legislature, MN legislature, MO legislature, NE legislature, NJ legislature, NY legislature, OH legislature, OR legislature, PA legislature, SC legislature, SD legislature, UT legislature, VA legislature, VT legislature, WI legislature, WV legislature | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 27 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 27 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 27 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 27 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | died, enacted, in effect, introduced, passed, passed one chamber, vetoed | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | research:large_load_2026-11-13 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://alison.legislature.state.al.us/files/pdf/SearchableInstruments/2026RS/SB270-enr.pdf, https://code.wvlegislature.gov/signed_bills/2025/2025-RS-HB2014-SUB%20ENR_signed.pdf, https://docs.legis.wisconsin.gov/document/amends/2025/REG/AB840-ASA1.pdf; 27 distinct | 0 |
| `x_law_id` | not yet written |  | text | for example laws_midwest_northeast-01, laws_midwest_northeast-02, laws_midwest_northeast-03; 27 distinct | 0 |
| `x_group` | not yet written |  | text | laws_midwest_northeast, laws_south_west | 0 |
| `x_state` | not yet written |  | text | AL, CT, DE, FL, IA, ID, KS, MA, MD, MI, MN, MO, NE, NJ, NY, OH, OR, PA, SC, SD, UT, VA, VT, WI, WV | 0 |
| `x_bill` | not yet written |  | text | for example 2026 Acts of Assembly, chapters 377 and 378 (Code of Virginia 56-596.7), A. 11560 (same as S. 10642), Responsible Data Center Development Act, A. 796 (Fourth Reprint), P.L. 2026, c.32 (Data Center Fair Share Act); 27 distinct | 0 |
| `x_session` | not yet written |  | text | 101st Legislative Session, 2026, 102nd Legislature, 2024 regular session, 103rd General Assembly, 2025 first regular session, 103rd General Assembly, 2026 second regular session, 109th Legislature, 2026 second session, 126th General Assembly, 2025, 136th General Assembly, 2025-2026, 153rd General Assembly (2025-2026), 194th General Court (2025-2026), 2025 General Session, 2025 Regular Session (83rd Legislative Assembly), 2025 regular session, 2025-2026 Legislature, 2025-2026 Regular Session, 2025-2026 legislative session, 2026 Regular Session, 2026 Regular Session (68th Legislature, second regular session), 2026 regular session, 2026-2027 session, 91st General Assembly, 2026 session, 94th Legislature, 2025 First Special Session, February Session, 2026 | 0 |
| `x_title` | not yet written |  | text | for example AN ACT CONCERNING COLOCATED ELECTRIC SUPPLIERS AND LARGE ELECTRIC LOAD CUSTOMERS., AN ACT TO AMEND THE SOUTH CAROLINA CODE OF LAWS BY ENACTING THE "SOUTH CAROLINA ENERGY SECURITY ACT", AN ACT TO AMEND TITLE 26 OF THE DELAWARE CODE RELATING TO LARGE ENERGY USE FACILITIES.; 27 distinct | 0 |
| `x_status_date` | not yet written |  | text | 2025-03-25, 2025-04-17, 2025-04-24, 2025-05-12, 2025-05-20, 2025-06-14, 2025-06-16, 2025-07-11, 2025-08-28, 2026-02-26, 2026-03-19, 2026-03-23, 2026-03-24, 2026-04-08, 2026-04-10, 2026-04-14, 2026-05-07, 2026-05-12, 2026-05-29, 2026-06-04, 2026-07-07, 2026-08-26, not published | 0 |
| `x_date_kind` | not yet written |  | text | date read, stated date | 0 |
| `x_effective_date` | not yet written |  | text | 2025-04-17, 2025-05-07, 2025-05-12, 2025-06-01, 2025-06-16, 2025-07-11, 2025-08-28, 2026-07-01, 2026-07-07, 2026-08-26, 2026-10-01, not published | 0 |
| `x_status_cite` | not yet written |  | text | for example https://docs.legis.wisconsin.gov/2025/proposals/ab840 (read 2026-11-14) p. 1, History, 1/20/2026 Asm.: "Read a third time and passed, Ayes 53, Noes 44, Paired 2" \| https://docs.legis.wisconsin.gov/2025/proposals/ab840 (read 2026-11-14) p. 1, History, 1/20/2026 Asm.: "Assembly Substitute Amendment 1 adopted" \| https://docs.legis.wisconsin.gov/2025/proposals/ab840 (read 2026-11-14) p. 1, History, 3/23/2026 Sen.: "Failed to concur in pursuant to Senate Joint Resolution 1" \| p. 1, heading: "ASSEMBLY SUBSTITUTE AMENDMENT 1, TO ASSEMBLY BILL 840", https://legis.delaware.gov/BillDetail/143381 (read 2026-11-14) p. 1, Status: "Signed 8/26/26" \| https://legis.delaware.gov/BillDetail/143381 (read 2026-11-14) p. 1, Volume:Chapter: "85:440" \| https://legis.delaware.gov/BillDetail/143381 (read 2026-11-14) p. 1, Effective Date: "8/26/26" \| p. 14, Section 6: "Section 6. This Act takes effect upon enactment.", https://legislature.idaho.gov/sessioninfo/2026/legislation/H0911/ (read 2026-11-13) p. 1, bill history: "Reported Signed by Governor on April 10, 2026" \| https://legislature.idaho.gov/sessioninfo/2026/legislation/H0911/ (read 2026-11-13) p. 1, bill history: "Session Law Chapter 335" \| https://legislature.idaho.gov/sessioninfo/2026/legislation/H0911/ (read 2026-11-13) p. 1, bill history: "Effective: 07/01/2026" \| p. 1, History: "[61-335, added 2026, ch. 335, sec. 1, p. 1315.]"; 27 distinct | 0 |
| `x_threshold_mw` | not yet written |  | text | 100 MW: new service expected to reach a cumulative demand of 100 MW or more, or added service of 100 MW or more, within five years of the requested start date, 150 MW expected total peak demand at one or more contiguous parcels, for a data processing center under Section 40-9B-3 operating solely for data processing, 20 MW: a facility that uses or is able to use 20 MW or more and is primarily engaged in a service under NAICS code 518210, 25 MW contracted or measured demand with an anticipated or measured average annual load factor of 75 percent or more (contracted defense facilities excluded), 50 MW anticipated monthly peak load (highest 15-minute average) at a single location; colocated customers at one location count together; loads at multiple locations are not aggregated, 50 MW at one point of delivery for a 'transformational customer' (with 500 new employees, $100,000,000 investment and a Department of Commerce designation); an existing customer above 20 MW contract demand signing a contract of five years or more is a 'qualifying customer', 50 MW: an increase of 50 MW or more in a service entrance's cumulative power requirement in any consecutive 60-month period, under a service contract entered into on or after July 1, 2026, Senate committee version only: a data center requires peak demand capacity greater than 25 MW at a single building or location; the self-supply duty applies to new data centers above 250 MW aggregate monthly maximum demand, a commercial data center has a peak demand of 25 MW or greater, a data center is a facility designed to have a load of not less than 20 MW, a data center uses or is able to use 20 MW or more and provides data processing and hosting services (NAICS 518210), a data center with a peak demand of 10 MW or greater, a large data center has a peak demand of 20 MW or more (5 MW for the covered data center labor and reporting duties), a large data center has an information-technology load above 20 GWh of consumption or 100 MW of demand (facilities under common ownership aggregated), a large electric load customer has a peak demand of not less than 50 MW, a large energy use facility uses or is projected to use 75 MW or more of monthly maximum demand at a load factor of 85 percent or more, or 100 MW or more of monthly maximum instantaneous demand, or 30 MW or more if primarily a data processing and hosting service (NAICS 518210); facilities may be aggregated; bulk petroleum facilities excluded, a retail load customer requesting a new or expanded interconnection where the total load at a single site would exceed 20 MW, customers reasonably projected to have an annual peak demand of 100 MW or more, for electrical corporations serving more than 250,000 customers; 50 MW or more for those serving 250,000 or fewer customers as of 1 January 2025, large load customer (new Part III): aggregate monthly demand of at least 25 MW and a load factor above 60 percent, excluding water and sewage companies, manufacturing, hospitals, district energy, agriculture; the 4-212 rate schedule threshold lowered from 100 MW to 25 MW, large load customer: aggregate monthly demand of at least 100 MW and a load factor over 80 percent; the specific rate schedule covers more than 100 MW at a single location or more than 100 MW aggregated contract capacity (lowered to 25 MW by Chapter 353 of 2026), no MW figure for the very large customer class: the Commission defines it for each utility by order by 15 December 2026; a data center is defined as a facility designed to have a load of 100 MW or more; the qualified large-scale data center fee starts at 100 MW of peak demand, no general size threshold for microgrid customers; the negotiation requirement does not apply to microgrid districts producing 300 MW or more; a high impact data center (special property valuation) has an aggregate critical IT load of 90 MW or more, not published, set by the BPU for each utility at not greater than 50 MW, with related data centers aggregated, would lower the 393.130.7 threshold for the larger electrical corporations from 100 MW to 50 MW of annual peak demand; the emergency curtailment duty applies above 25 MW of peak demand | 0 |
| `x_threshold_mw_cite` | not yet written |  | text | for example p. 1, 56-596.7(A): "means a retail electric service customer that has a contracted or measured electric demand of 25 megawatts or greater and an anticipated or measured average annual electric load factor of 75 percent or greater", p. 1, 61-335(1)(c): "Results in an increase in a cumulative power requirement of such service entrance of fifty (50) megawatts or more in any consecutive sixty (60) month period" \| p. 1, 61-335(1)(c)(ii): "Is subject to a service contract with a public utility that was entered into on or after July 1, 2026.", p. 1, Sec. 2(1): "Large load customer means a retail load customer requesting a new or ... expanded interconnection where the total load at a single site would exceed twenty megawatts;"; 27 distinct | 0 |
| `x_requirements` | not yet written |  | text | for example collateral: the Commission's regulations must govern retail tariff terms that safeguard existing customers, including deposits or other financial security from a commercial data center [p. 19, tariff terms: "STRANDED INVESTMENT AND COST SHIFTING, INCLUDING ALL OF THE" \| p. 19, tariff terms (i): "(I) DEPOSITS OR OTHER FINANCIAL SECURITY REQUIRED"] \|\| minimum term: minimum contract terms and minimum load obligations requiring a data center that ceases operations early or engages in economic peak-shaving to take a minimum level of service for a minimum number of years, secured by a letter of credit or comparable instrument [p. 19, tariff terms (iii): "(III) MINIMUM CONTRACT TERMS AND MINIMUM LOAD" \| p. 19, tariff terms (iii): "OF SERVICE FOR A MINIMUM NUMBER OF YEARS SUFFICIENT TO" \| p. 19, tariff terms (iii): "THIS SUBPARAGRAPH BY A LETTER OF CREDIT OR OTHER"] \|\| exit fee: exit fees or early termination fees [p. 19, tariff terms (v): "(V) EXIT FEES OR EARLY TERMINATION FEES."] \|\| cost allocation: a prohibition on shifting to other customers costs caused in whole or part by a commercial data center's interconnection, service or load [p. 21, Section 4: "SECTION 4. PROHIBITION ON COST SHIFTING AND RECOVERY OF COSTS."] \|\| curtailment or backup generation: curtailment of a commercial data center's load under regional transmission organization curtailment programs, and curtailment standards [p. 20, regulations (2): "(2) CURTAILMENT OF A COMMERCIAL DATA CENTER'S LOAD UNDER"], commission rulemaking: A public utility serves a new large load only under a commission-approved service contract, filed with a no harm test; the commission approves or denies it within 270 days [p. 1, 61-335(2): "A public utility shall provide service to a new large load only pursuant to a commission-approved service contract." \| p. 1, 61-335(3), (4): "Such filing shall include a no harm test ... The commission shall review and approve or deny a new large load service contract within two hundred seventy (270) days of receiving such filing by the public utility."] \|\| cost allocation: The new large load funds its full cost of service, including its share of generation, transmission, substation and distribution investments needed only because of it; the commission reviews the contract's rates in each general rate case [p. 1, 61-335(4)(b): "The new large load is responsible for funding its full cost of service, including its share of generation, transmission, substation, and distribution infrastructure investments" \| p. 1, 61-335(7)(a): "In each general rate case filed by a public utility, the commission shall review the rates, charges, and cost recovery mechanisms applicable to an approved service contract"] \|\| collateral: Approval is conditioned on financial security, in a form and amount the commission approves, reasonably sufficient to protect the utility and its other customers from stranded or unrecoverable costs [p. 1, 61-335(6): "Approval of a service contract shall be conditioned on the new large load furnishing financial security, in a form and amount approved by the commission"] \|\| other: A new large load may not change its status by artifice, such as splitting its load among service entrances [p. 1, 61-335(5): "A new large load shall not change its status as such by means of artifice"], commission rulemaking: each investor-owned electric company and electric cooperative must submit a specific rate schedule for large load customers by 1 September 2026; the PSC must adopt regulations by 1 June 2026 on notice and deadlines for load studies and contract terminations, forms of collateral, and study completion [p. 17, PUA 4-212(c)(1): "SHALL SUBMIT TO THE COMMISSION FOR APPROVAL A SPECIFIC RATE SCHEDULE FOR LARGE LOAD CUSTOMERS." \| p. 19, PUA 4-212(f)(1): "ADOPT REGULATIONS TO CARRY OUT THIS SECTION." \| p. 19, PUA 4-212(f)(2)(ii): "COMMON FORMS OF ACCEPTABLE COLLATERAL TO SATISFY THE REQUIREMENTS OF"] \|\| minimum bill: in approving a schedule the PSC must consider minimum billing demand for distribution and transmission at a high percentage of contract capacity, long-term commitments and exit fees, guarantee or collateral requirements, and penalties if a project is delayed or cancelled after buildout begins [p. 18, PUA 4-212(d)(2)(ii): "AND TRANSMISSION SERVICE THAT IS A HIGH PERCENTAGE OF A LARGE LOAD" \| p. 18, PUA 4-212(d)(2)(iii): "(III) LONG-TERM CONTRACTUAL COMMITMENTS AND EXIT FEES;" \| p. 18, PUA 4-212(d)(2)(iv): "(IV) GUARANTEE OR COLLATERAL REQUIREMENTS; AND"] \|\| cost allocation: the schedule should require the customer to cover the just and reasonable costs of transmission or distribution buildout to interconnect or serve it, payable over multiple years of the contract not exceeding 5 years [p. 18, PUA 4-212(e): "THE COSTS ASSOCIATED WITH ANY ELECTRIC TRANSMISSION OR DISTRIBUTION SYSTEM BUILDOUT REQUIRED UNDER SUBSECTION (D)(1) OF THIS SECTION MAY BE PAID OVER MULTIPLE YEARS OF A LARGE LOAD CUSTOMER'S CONTRACT FOR SERVICE, NOT TO EXCEED 5 YEARS."] \|\| interconnection study: before signing a contract under the schedule the customer must request a load study to set its contract capacity and pay its fees, designate a site, and own or control the land [p. 19, PUA 4-212: "NECESSARY CONTRACT CAPACITY FOR THE LARGE LOAD CUSTOMER AND PAY ANY" \| p. 19, PUA 4-212: "APPLICABLE FEES ASSOCIATED WITH THE STUDY;"]; 27 distinct | 0 |
| `x_source_title` | not yet written |  | text | for example 2025 Session Laws of Kansas, Chapter 124: Senate Bill 98, Kansas Secretary of State, Act No. 207, Public Acts of 2024 (Enrolled House Bill No. 4906), Michigan Legislature, Assembly Bill A11560 (2025-2026), New York State Legislature (legislation.nysenate.gov); 27 distinct | 0 |
| `x_date_read` | not yet written |  | date | 2026-11-13, 2026-11-14 | 0 |
| `x_notes` | not yet written |  | text | for example A 2024-session act approved 17 January 2025 and in effect in 2025. It sets terms for data centers' electric service as conditions of a sales and use tax exemption, not as a utility rule. The companion Act No. 208 of 2024 (Enrolled H.B. 5600, effective 2 April 2025) was opened but not read for terms. No 2025 or 2026 Michigan act on large loads was found (one web search; a Michigan moratorium bill is a news lead only)., Amends PUA 4-212 (from Chapter 625 of 2025) and adds Part III, 7-232 to 7-234; it keeps the 1 September 2026 rate schedule filing date (4-212(c)(1)(i), p.34). Dataset row pjm_east-03 (proposed COMAR 20.96.01, RM 93) cites this chapter for its threshold. Effective date: the chapter has several effective-date sections (July 1, 2026 for listed sections; the rest from enactment as an emergency measure); which section carries these provisions was not traced, so not published here. Existing large load customers whose load does not expand by more than 25 MW are outside the schedule (4-212(c)(2)(iii))., Coordinator's lead (a Governor's release: HB 233 signed 26 August 2026) confirmed on the General Assembly's bill page: House Substitute 1 for HB 233, Signed 8/26/26, Volume:Chapter 85:440, Effective Date 8/26/26. The text read is the engrossment of HS 1 as amended (House Amendments 1 and 3, Senate Amendment 2). The bill page's synopsis says rate applications are due within 180 days of the effective date; the engrossed Section 6 says within 180 days of the finalization of the Commission's regulations, and the engrossed text is quoted. No dataset statewide row exists for Delaware (Delmarva's tariff is Exelon's, whose site terms bar automated access).; 27 distinct | 0 |

### `subregion_demand_growth`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 3918.

- **Source:** eia:electricity/rto/region-sub-ba-data U.S. Energy Information Administration, Hourly Electric Grid Monitor, demand by subregion
- **Method note:** [`docs/methods/subregion_demand_growth.md`](../methods/subregion_demand_growth.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Every EIA-930 sub-region's peak and average demand by year (docs/methods/subregion_demand_growth.md). Via the Energy Research Warehouse (ERW), table `subregion_demand_growth`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example eia930_subba:BHBA:BASI, eia930_subba:BHBA:SDE, eia930_subba:BHBA:WYE; 90 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z, 2026-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -41.0359 to 178311777.0; 2655 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 3918 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example AEPW American Electric Power West (Southwest Power Pool), Allegheny Power zone (PJM Interconnection, LLC), American Electric Power zone (PJM Interconnection, LLC); 90 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:subregion_demand_growth | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/subregion_demand_growth.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-05T22:06:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 3918 |
| `x_at` | not yet written |  | utc time | 2019-01-03T01:00:00Z to 2025-12-30T22:00:00Z; 360 distinct | 3366 |
| `x_parent` | not yet written |  | text | BHBA, CISO, ERCO, ISNE, MISO, NYIS, PJM, PNM, SWPP, SWPW | 0 |
| `x_subba` | not yet written |  | text | for example 0001, 0004, 0006; 90 distinct | 0 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `avg_growth_pct` |  | pct | 466 | 2020-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `avg_mw` |  | MW | 552 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `energy_mwh` |  | MWh | 552 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `hours_in_year` |  | count | 665 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `hours_used` |  | count | 665 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `peak_growth_pct` |  | pct | 466 | 2020-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `peak_mw` |  | MW | 552 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

