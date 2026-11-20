# Codebook: erw_derived

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 30 public tables (2 entities, 3 events, 25 series; tiers: 25 derived, 5 model_extracted); 30 documented in full.

- [`ai_power_regions`](#ai_power_regions): One ISO region's value of one measure of where the next gigawatts for AI can come from: cost, carbon, price stress, connection queues or reliance on imports.
- [`attention_index_weekly`](#attention_index_weekly): One sector and place's value of one Attention Index measure in one week, or one of the week's denominators (entity attention:corpus:all).
- [`attention_story_links`](#attention_story_links): One classified news story behind the Attention and Friction indices: its week, sector, place, opposition, kind, tone and link.
- [`clean_energy_hourly`](#clean_energy_hourly): One ISO grid's carbon-free share of its own generation in one held hour, with the hour's two sums.
- [`clean_energy_summary`](#clean_energy_summary): One ISO grid's value of one clean-energy measure for one local month (freq P1M) or one local year (freq P1Y).
- [`deal_counterparties`](#deal_counterparties): One counterparty of the deal tracker: a name a deal in energy_deals gives as its buyer or seller, once its spellings are joined, with its deal counts.
- [`event_study_estimates`](#event_study_estimates): One estimate of an event's effect on one grid's daily demand served or on a hub's daily mean real-time price: for one event day, pooled over the window, as the counterfactual mean, or for one local hour.
- [`event_window_daily`](#event_window_daily): One event's daily (or, for COVID-19, weekly) value of one figure for one grid, hub or weather station, on a day of the event window or a baseline day of earlier years.
- [`flex_alert_effects`](#flex_alert_effects): One value of the Flex Alert scorecard for CAISO's balancing authority: for one alert day (freq P1D), one hour of an alert day (PT1H) or one year (P1Y).
- [`flex_alert_model`](#flex_alert_model): One figure of the Flex Alert scorecard's demand model for CAISO: a pooled estimate, an out-of-sample check, a specification compared, a model setting, an hourly coefficient, or one held-out hot day's error.
- [`forecast_tool_parameters`](#forecast_tool_parameters): One parameter the forecast tool reads, for one technology and place: EIA's capital cost and case figures, JEDI's construction cost and taxable share, or the gas plant's fuel defaults.
- [`friction_index_weekly`](#friction_index_weekly): One sector and place's value of one Friction Index measure (opposition in the news) in one week.
- [`gas_balance_weekly`](#gas_balance_weekly): One EIA storage region's weekly working gas measure, or one monthly measure of the US natural gas balance.
- [`generation_mix_hourly_profile`](#generation_mix_hourly_profile): One ISO grid's value of one energy-mix measure for one local month: an hour of the month's average day, a source's MWh or share, or a count of days.
- [`generation_mix_records`](#generation_mix_records): One ISO grid's record of the energy mix (highest solar or wind share of an hour, cleanest or dirtiest hour) over the whole history or one local year.
- [`generator_pipeline_by_grid`](#generator_pipeline_by_grid): One cell of EIA-860M's planned generators (balancing authority, state, energy source, status, planned year) in one snapshot month, or one balancing authority's (or the US's) move of planned generators between two months.
- [`hub_price_comparison`](#hub_price_comparison): One public hub or zone's value of one price measure, day-ahead or real time, over the last twelve months (freq P1Y) or the last whole month (P1M), or its grid's carbon intensity over the same window.
- [`known_data_faults`](#known_data_faults): One known fault in a source's data, as the ERW's register of faults records it.
- [`merchant_revenue_monthly`](#merchant_revenue_monthly): One ISO main hub's value of one merchant revenue measure for one asset type (solar, wind, a 2-hour or 4-hour battery, a gas peaker) and one month, or the month's flat price and hours.
- [`nlr_jedi_multipliers`](#nlr_jedi_multipliers): One JEDI figure per MW for one technology, location, phase and effect: jobs, earnings or output, or the default project's MW, or the phase's local spending share.
- [`node_basis_daily`](#node_basis_daily): One ERCOT settlement point's value of one price measure (mean, four-hour spread, or basis against the hub average) for one operating day, day-ahead or real time.
- [`node_basis_summary`](#node_basis_summary): One month's statistic of the distribution of ERCOT's settlement points against the hub average, for one market and one class of points.
- [`nuclear_fleet_status`](#nuclear_fleet_status): One US reactor's, one grid's reactor fleet's or the whole US fleet's value of one measure (capacity, outages, available energy, uprates) for one year.
- [`region_weather_hourly`](#region_weather_hourly): One EIA region's population-weighted mean temperature in one hour, written only for an hour every one of its stations holds.
- [`resource_layer_features`](#resource_layer_features): One grid cell, site or area of one layer of the natural resource map (wind, solar, geothermal, hydropower, biomass, oil and gas basins and plays, coal fields), with its value.
- [`scarcity_hours_by_grid`](#scarcity_hours_by_grid): One grid's (ERCOT's or CAISO's) value of one scarcity measure in one hour: the USD 1,000 price counts and the grid's own scarcity signal.
- [`shoulder_hours_monthly`](#shoulder_hours_monthly): One grid's (ERCOT's or CAISO's) value of one shoulder-hours measure: for a local month's average day (P1M), one of a year's ten worst days (P1D), or a year (P1Y).
- [`state_generation_mix_monthly`](#state_generation_mix_monthly): One state's (or the nation's) net generation from one group of energy sources in one month.
- [`state_large_load_laws`](#state_large_load_laws): One US state law or bill of the 2025 and 2026 sessions that sets terms for large loads (data centers and others) or tells the utilities or the commission to set them.
- [`subregion_demand_growth`](#subregion_demand_growth): One EIA-930 sub-region's value of one demand measure (peak, average, energy, hours, growth) for one UTC calendar year.

### `ai_power_regions`

One ISO region's value of one measure of where the next gigawatts for AI can come from: cost, carbon, price stress, connection queues or reliance on imports.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 187.

- **Time:** ts_utc dates the measure's window, not an instant: 2025-09-01 for the twelve months 2025-09-01 to 2026-09-01, 2026-01-01 for Berkeley Lab's queue data, 2026-09-30 for the ISOs' own queues, 2018-07-01 for CAISO's emergency days; x_window says which.
- **Revisions:** Rewritten whole by each run of the builder (the old file removed first); vintage is not filled.
- **Source:** erw:ai_power_regions ERW derived table, the AI gigawatts report's methods appendix (docs/reports/ai_gigawatts_methods.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/reports/ai_gigawatts_methods.md)
- **Method note:** [`docs/methods/ai_power_regions.md`](../methods/ai_power_regions.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Where the next gigawatts for AI can come from (warehouse/derived/ai_power_regions.py). Via the Energy Research Warehouse (ERW), table `ai_power_regions`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: iso:<region>, one of caiso, ercot, isone, miso, nyiso, pjm, spp | none | text | iso:caiso, iso:ercot, iso:isone, iso:miso, iso:nyiso, iso:pjm, iso:spp | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-01T00:00:00Z, 2025-09-01T00:00:00Z, 2026-01-01T00:00:00Z, 2026-09-30T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -3.0021 to 855443603.0; 162 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD, USD/MWh, count, kgCO2/MWh, pct, tCO2, year | 0 |
| `freq` | How long the interval of the row is. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 187 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 187 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 187 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 187 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ai_power_regions | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/reports/ai_gigawatts_methods.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T09:42:46Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 187 |
| `x_window` | The period the measure covers, in words (the twelve months, the Berkeley Lab edition, the ISO queue's retrieval, the emergency report's span, or the studied event windows) | none | text | 2018-07 to 2025-04, CAISO's Grid Emergencies History Report, 2025-09-01 to 2026-09-01 (twelve months), Berkeley Lab Queued Up 2026 edition, requests through 2025, studied event windows (event_study_estimates), the ISO's queue as retrieved in late September 2026 | 0 |
| `x_note` | The event the largest-effect measure names (with temperature-controlled where held) and the day the ISO queue was retrieved | none | text | caiso_heat_2020 (temperature-controlled); retrieved 2026-09-30, elliott_2022 (temperature-controlled), elliott_2022 (temperature-controlled); retrieved 2026-09-26, elliott_2022 (temperature-controlled); retrieved 2026-09-30, ercot_heat_2023 (temperature-controlled); retrieved 2026-09-30 | 174: Empty on every measure but event_largest_effect_pct and queue_active_mw |

Variables (31):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `carbon_days` | Days held behind the carbon intensity (carbon_intensity_daily) | count | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `carbon_intensity_kg_mwh` | Mean of the year's daily consumption-based carbon intensity: the CO2 of the generation the region used, imports included, per MWh of demand | kgCO2/MWh | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `demand_mwh` | The year's demand over the hours of the EIA-930 workbook extract where demand and net generation are both held (the import share's denominator) | MWh | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `emergency_days` | CAISO only: days with an ISO-wide Flex Alert or grid emergency, 2018-07 to 2025-04, as the Flex Alert scorecard reads them | count | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `event_largest_effect_pct` | Among the studied events (COVID-19 left out), the pooled effect on daily demand with the largest size, as a percent of the event's counterfactual; temperature-controlled where held | pct | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `event_largest_is_caiso_heat_2020` | 1: the largest event effect is that of the August 2020 heat wave in CAISO (caiso_heat_2020) | count | 1 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `event_largest_is_elliott_2022` | 1: the largest event effect is that of Winter Storm Elliott, December 2022 (elliott_2022) | count | 5 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `event_largest_is_ercot_heat_2023` | 1: the largest event effect is that of the summer 2023 heat in ERCOT (ercot_heat_2023) | count | 1 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `flat_1gw_co2_t` | CO2 of a load that draws a flat 1 GW for a year (8,760 GWh) at that carbon intensity, tonnes | tCO2 | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `flat_1gw_cost_usd` | Wholesale energy cost of a load that draws a flat 1 GW for a year at the real-time flat price (8,760 MWh per MW times 1,000 MW) | USD | 6 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `flat_da_price_usd_mwh` | What a flat load pays per MWh at the region's main hub, day-ahead: the monthly simple mean of hourly prices weighted by hours, over the year | USD/MWh | 6 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `flat_rt_price_usd_mwh` | What a flat load pays per MWh at the region's main hub, real time: the monthly simple mean of hourly prices weighted by hours, over the year | USD/MWh | 6 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `interchange_days` | Complete days of the pair sums: every regular neighbour reported and no pair-day was screened out | count | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `interchange_days_reported` | Days of the year on which any interchange of the region is reported in eia930_daily_interchange | count | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `lbnl_active_mw` | MW of the interconnection requests with status active at the end of 2025 in Berkeley Lab's queue data, the region as Berkeley Lab assigns it | MW | 7 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `lbnl_active_requests` | Interconnection requests with status active at the end of 2025 in Berkeley Lab's queue data | count | 7 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `lbnl_cod_sample` | Requests that came online in 2018 to 2025, behind the median years to commercial operation | count | 7 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `lbnl_cohort_requests` | Requests made in 2000 to 2019, behind the completion rate | count | 7 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `lbnl_completion_pct` | Share of the requests made in 2000 to 2019 that came online | pct | 7 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `lbnl_median_years_to_cod` | Median years from request to commercial operation, over the requests that came online in 2018 to 2025 | year | 6 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `max_rt_hour_usd_mwh` | The year's highest hourly real-time hub price | USD/MWh | 6 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `net_import_days_pct` | Share of the complete days on which the region's summed interchange was negative (a net importer) | pct | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `net_import_share_pct` | Net imports as EIA's own balance: the year's demand less net generation, over demand, from the complete hours of the workbook extract | pct | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `pair_import_share_pct` | Net imports from the pair sums (minus the summed interchange with every neighbour) over demand, complete days only | pct | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `peak_import_share_pct` | Mean net import share on the year's ten highest-demand complete days | pct | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `queue_active_mw` | Active MW in the ISO's own interconnection queue as retrieved in late September 2026 | MW | 6 | 2026-09-30T00:00:00Z | 2026-09-30T00:00:00Z |
| `rt_hours_priced` | Real-time hours behind the flat prices (cost_of_power_monthly's rt_hours, summed over the year) | count | 6 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `rt_hours_seen` | Hours of real-time hub price held behind the scarcity counts | count | 6 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `scarcity_hours_1000` | Hours of the year whose real-time hub price (the mean of the hour's 15-minute prices; MISO's hourly price) was at least USD 1,000 per MWh | count | 6 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `scarcity_hours_200` | Hours of the year whose real-time hub price (the mean of the hour's 15-minute prices; MISO's hourly price) was at least USD 200 per MWh | count | 6 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |
| `screened_pair_days` | Pair-days left out as implausible: further than 10 median absolute deviations (at least 500 MWh) from the pair's own median | count | 7 | 2025-09-01T00:00:00Z | 2025-09-01T00:00:00Z |

Waiting for a second look: x_note on the queue_active_mw rows carries the region's largest-event name as well as the queue's retrieval date: the builder writes one notes string to both measures.; The report's methods appendix defines net_import_share_pct from the pair sums, while the header and the builder define it as EIA's balance (demand less net generation); the label follows the header and the code..

### `attention_index_weekly`

One sector and place's value of one Attention Index measure in one week, or one of the week's denominators (entity attention:corpus:all).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: model_extracted. Rows read on 2026-11-20: 1775.

- **Time:** ts_utc is the Monday 00:00Z of the week; weeks run Monday to Sunday, UTC; freq P1W.
- **Revisions:** Rewritten whole as one snapshot by each run of the index builder (a week only partly classified is a lower bound until its stories are classified).
- **Method note:** [`docs/methods/attention.md`](../methods/attention.md)
- **Cite as:** Energy Research Warehouse (ERW). The Attention and Friction indices: coverage and opposition by week, sector and place, from the classified news stories (the ERW's own derivation). Via the Energy Research Warehouse (ERW), table `attention_index_weekly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: attention:<sector>:<geo>: sector one of datacenters, transmission, gas, nuclear, solar_wind, storage, oil_lng or energy (any energy sector); geo all, US or a state code; attention:corpus:all holds the week's denominators | none | text | for example attention:corpus:all, attention:datacenters:US, attention:datacenters:US-AL; 185 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2024-12-30T00:00:00Z to 2026-11-09T00:00:00Z; 98 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1.0 to 3146.0; 384 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count, pct, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US or US-<state> for those places; empty for the place all and the corpus entity | none | text | for example US, US-AK, US-AL; 47 distinct | 512 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:attention | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/attention.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-06T20:14:48Z, 2026-11-06T20:34:52Z, 2026-11-16T09:23:15Z | 0 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `attention_index` | The cell's classified stories as a percent of the week's judged stories | pct | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `stories` | The cell's classified stories | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `stories_classified` | The week's stories classified by the model (corpus entity) | count | 98 | 2024-12-30T00:00:00Z | 2026-11-09T00:00:00Z |
| `stories_judged` | The week's judged stories: those classified plus those the news scorer gave significance 0, which count as not about energy (corpus entity) | count | 98 | 2024-12-30T00:00:00Z | 2026-11-09T00:00:00Z |
| `stories_unsent_zero` | The week's stories the news scorer gave significance 0, not sent to the classifier (corpus entity) | count | 98 | 2024-12-30T00:00:00Z | 2026-11-09T00:00:00Z |
| `stories_week` | Every story the news corpus holds in the week (corpus entity) | count | 98 | 2024-12-30T00:00:00Z | 2026-11-09T00:00:00Z |
| `tone_mean` | Mean tone of the cell's stories, from -1 (negative) to 1 (positive) | ratio | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |

### `attention_story_links`

One classified news story behind the Attention and Friction indices: its week, sector, place, opposition, kind, tone and link.

Shape: events. Keys: `event_id`. License: public; tier: model_extracted. Rows read on 2026-11-20: 8120.

- **Time:** event_date is the story's publish time, UTC; week is the Monday 00:00Z of its week.
- **Revisions:** Merged by event_id on each run, the newest classification of a story kept (by classified_at); rows of earlier runs not rewritten are kept.
- **Method note:** [`docs/methods/attention.md`](../methods/attention.md)
- **Cite as:** Energy Research Warehouse (ERW). The Attention and Friction indices: coverage and opposition by week, sector and place, from the classified news stories (the ERW's own derivation). Via the Energy Research Warehouse (ERW), table `attention_story_links`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: attn:<the story's news id> | none | text | for example attn:0007c90d93793ce0, attn:0010e7ad3689a2d6, attn:00111d8c171a3b8b; more than 5000 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which). Here: The story's publish time, UTC (YYYY-MM-DDTHH:MM:SSZ) | none | utc time | 2026-10-05T17:03:00Z to 2026-11-17T12:00:00Z; more than 5000 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: attention_link on every row | none | text | attention_link | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 8120 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 8120 |
| `mw` | The capacity involved, in megawatts. Here: Not filled: no cell holds a value | MW | empty | no cell holds a value | 8120 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise. Here: Not filled: no cell holds a value | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 8120 |
| `currency` | The currency of the price, as an ISO 4217 code (USD). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 8120 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 8120 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD). Here: The story's outlet, as the news corpus holds it | none | text | for example ANS Nuclear Newswire, Bloomberg, Bloomberg.com; 48 distinct | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://electrek.co/2026/10/05/byds-flagship-suv-topped-10000-sales-3-months-straight/, https://electrek.co/2026/10/05/department-of-war-drafts-ev-battery-factory-into-military-drone-duty-with-75m-grant/, https://electrek.co/2026/10/05/hyundai-testing-smaller-ev-could-be-ioniq-4-video/; more than 5000 distinct | 0 |
| `story_event_id` | The story's event_id in news_stories (news:<id>) | none | text | for example news:0007c90d93793ce0, news:0010e7ad3689a2d6, news:00111d8c171a3b8b; more than 5000 distinct | 0 |
| `week` | The Monday 00:00Z (UTC) of the week the story was published in | none | utc time | 2026-10-05T00:00:00Z, 2026-10-12T00:00:00Z, 2026-10-19T00:00:00Z, 2026-10-26T00:00:00Z, 2026-11-02T00:00:00Z, 2026-11-16T00:00:00Z | 0 |
| `sector` | What the story is mainly about, as the model classified it: one of the seven index sectors (datacenters, transmission, gas, nuclear, solar_wind, storage, oil_lng), other_energy, or not_energy | none | text | datacenters, gas, not_energy, nuclear, oil_lng, other_energy, solar_wind, storage, transmission | 0 |
| `us` | true when the story is about the United States (a US place, a US company's US project, a federal or state action), else false | none | boolean | false, true | 0 |
| `state` | The one US state the story is mainly about, postal code | none | text | for example AK, AL, AR; 49 distinct | 7364: No state, several states, or a story not about the US |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> where the story names one state, US where it is about the United States, else empty | none | text | for example US, US-AK, US-AL; 50 distinct | 4472 |
| `place` | The county, city or metro the text names as the project's or dispute's place, as written | none | text | for example Adelaide, Aiken, Albuquerque; 185 distinct | 7869: The text names no such place |
| `place_kind` | The kind of the named place: county, city or metro | none | text | city, county, metro | 7889: No place named |
| `opposition` | true when the story reports opposition to an energy or data center project, plant, line, pipeline, policy, permit, lease or rate, else false | none | boolean | false, true | 0 |
| `kind` | The main kind of opposition reported: moratorium, lawsuit, protest, permit_denied, rate_case, political_opposition, other_opposition, or none | none | text | lawsuit, moratorium, none, other_opposition, permit_denied, political_opposition, protest, rate_case | 0 |
| `tone` | The story's tone toward what it covers: -1 negative, 0 neutral or mixed, 1 positive | none | integer | -1, 0, 1 | 0 |
| `headline` | The story's headline in the ERW's own words: the news scorer's where it read the story, else the classifier model's neutral headline of at most fourteen words | none | text | for example $67.8 billion in Asian LNG-to-power projects scrapped or stalled since 2021, 120K customers without power in Southeastern US after Hurricane Isaias, 121 Gulf platforms evacuated as Isaias strengthens; more than 5000 distinct | 0 |
| `scorer_sector` | The sector the news scorer gave the story, in the scorer's own vocabulary (capital, company, datacenter_power, deal, gas and others) | none | text | capital, company, datacenter_power, deal, gas, generation, geopolitics, grid_conditions, hydrogen, interconnection, lng, nuclear, oil, other, policy, power_prices, ppa, renewables, storage, transmission, transport | 3548: The news scorer holds no score for the story |
| `significance` | The news scorer's significance score of the story (stories it scored 0 are not sent to the classifier) | none | integer | 1, 2, 3, 4, 5, 6, 7, 8, 9 | 3548: The news scorer holds no score for the story |
| `model_id` | The model that classified the story | none | text | claude-sonnet-5-5 | 0 |
| `prompt_version` | The version of the classifier's prompt the story was classified with | none | integer | 2 | 0 |
| `classified_at` | When the story was classified, UTC | none | utc time | 2026-11-06T19:58:37Z, 2026-11-06T20:16:40Z | 0 |
| `fixed` | Names any value of the model's answer that the code emptied or set to the neutral value when normalising it | none | empty | no cell holds a value | 8120: Nothing was changed (no cell holds a value) |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T09:23:15Z, 2026-11-16T09:24:19Z | 0 |

### `clean_energy_hourly`

One ISO grid's carbon-free share of its own generation in one held hour, with the hour's two sums.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 478164.

- **Time:** ts_utc is the hour's start, UTC; freq PT1H. Held hours only.
- **Revisions:** Rewritten whole by each run of mix_clean.py (the old file removed first); vintage is not filled.
- **Source:** erw:clean_energy EIA Form EIA-930 hourly net generation by energy source, the per-BA workbooks (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx); California from 2025-12-16T08:00:00Z is CAISO's own supply by fuel (caiso_fuel_supply), the warehouse's one join (docs/methods/eia930_caiso_break.md); read by this run from warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175834.883363Z_00002_CISO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175850.712544Z_00004_ERCO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175904.395449Z_00006_ISNE.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175918.956497Z_00008_MISO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175934.677962Z_00010_NYIS.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175949.986042Z_00012_PJM.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T180008.741327Z_00014_SWPP.xlsx (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx)
- **Method note:** [`docs/methods/generation_mix_hourly.md`](../methods/generation_mix_hourly.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. How clean each grid's generation is by hour, month and year; hourly against annual matching; load moved into the cleanest hours (docs/methods/clean_energy.md). Via the Energy Research Warehouse (ERW), table `clean_energy_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: iso:<grid>, the seven ISO grids | none | text | iso:caiso, iso:ercot, iso:isone, iso:miso, iso:nyiso, iso:pjm, iso:spp | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T05:00:00Z to 2026-11-16T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 95.207; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | pct | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-CA, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 478164 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 478164 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:clean_energy | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/clean_energy.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T18:00:39Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 478164 |
| `x_carbon_free_mwh` | The hour's carbon-free generation inside the grid: nuclear, wind, solar and hydro | MWh | number | 0.0 to 57449.0; more than 5000 distinct | 0 |
| `x_generation_mwh` | The hour's generation inside the grid: the carbon-free sources plus natural gas, coal and other (storage is not a source) | MWh | number | 5561.0 to 164281.0; more than 5000 distinct | 0 |
| `x_side` | The source of the hour: eia930 (EIA-930) or caiso (CAISO's own supply by fuel, California from the join of 2025-12-16) | none | text | caiso, eia930 | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `carbon_free_share_pct` | The hour's carbon-free MWh over its generation MWh | pct | 478164 | 2019-01-01T05:00:00Z | 2026-11-16T07:00:00Z |

### `clean_energy_summary`

One ISO grid's value of one clean-energy measure for one local month (freq P1M) or one local year (freq P1Y).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 27834.

- **Time:** ts_utc is the first day of the grid's local month or local year at 00:00:00Z; freq says which.
- **Revisions:** Rewritten whole by each run of mix_clean.py (the old file removed first); vintage is not filled.
- **Source:** erw:clean_energy EIA Form EIA-930 hourly net generation by energy source, the per-BA workbooks (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx); California from 2025-12-16T08:00:00Z is CAISO's own supply by fuel (caiso_fuel_supply), the warehouse's one join (docs/methods/eia930_caiso_break.md); read by this run from warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175834.883363Z_00002_CISO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175850.712544Z_00004_ERCO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175904.395449Z_00006_ISNE.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175918.956497Z_00008_MISO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175934.677962Z_00010_NYIS.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175949.986042Z_00012_PJM.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T180008.741327Z_00014_SWPP.xlsx (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx)
- **Method note:** [`docs/methods/clean_energy.md`](../methods/clean_energy.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. How clean each grid's generation is by hour, month and year; hourly against annual matching; load moved into the cleanest hours (docs/methods/clean_energy.md). Via the Energy Research Warehouse (ERW), table `clean_energy_summary`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: iso:<grid>, the seven ISO grids | none | text | iso:caiso, iso:ercot, iso:isone, iso:miso, iso:nyiso, iso:pjm, iso:spp | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-10-01T00:00:00Z; 94 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -54.1977 to 1482.9822; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count, hour, kgCO2/MWh, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M, P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-CA, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 27834 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 27834 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:clean_energy | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/clean_energy.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T18:00:39Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 27834 |

Variables (84):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `carbon_free_share_flat_pct` | Mean of the hours' shares: the carbon-free share met by a load that draws the same power every hour | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `carbon_free_share_pct` | Carbon-free MWh over generation MWh, over the complete days | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h00` | The month's average day: carbon-free share in local hour 00 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h01` | The month's average day: carbon-free share in local hour 01 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h02` | The month's average day: carbon-free share in local hour 02 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h03` | The month's average day: carbon-free share in local hour 03 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h04` | The month's average day: carbon-free share in local hour 04 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h05` | The month's average day: carbon-free share in local hour 05 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h06` | The month's average day: carbon-free share in local hour 06 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h07` | The month's average day: carbon-free share in local hour 07 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h08` | The month's average day: carbon-free share in local hour 08 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h09` | The month's average day: carbon-free share in local hour 09 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h10` | The month's average day: carbon-free share in local hour 10 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h11` | The month's average day: carbon-free share in local hour 11 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h12` | The month's average day: carbon-free share in local hour 12 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h13` | The month's average day: carbon-free share in local hour 13 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h14` | The month's average day: carbon-free share in local hour 14 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h15` | The month's average day: carbon-free share in local hour 15 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h16` | The month's average day: carbon-free share in local hour 16 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h17` | The month's average day: carbon-free share in local hour 17 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h18` | The month's average day: carbon-free share in local hour 18 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h19` | The month's average day: carbon-free share in local hour 19 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h20` | The month's average day: carbon-free share in local hour 20 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h21` | The month's average day: carbon-free share in local hour 21 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h22` | The month's average day: carbon-free share in local hour 22 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cf_share_pct_h23` | The month's average day: carbon-free share in local hour 23 (carbon-free MWh over generation MWh of that hour of the complete days) | pct | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cleanest_hour_1` | The local hour of the month's average day with the first highest carbon-free share | hour | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cleanest_hour_2` | The local hour of the month's average day with the second highest carbon-free share | hour | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cleanest_hour_3` | The local hour of the month's average day with the third highest carbon-free share | hour | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cleanest_hour_4` | The local hour of the month's average day with the fourth highest carbon-free share | hour | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `cost_days` | Days counted in the cost figures (every hour with a day-ahead hub price) | count | 204 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `days_held` | The complete days (every local hour held) the figures are over | count | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `days_in_month` | The days of the month | count | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `flat_cost_usd_per_mwh` | Cost per MWh of a flat 1 MW load at the grid's day-ahead hub price | USD/MWh | 204 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `flat_kgco2_per_mwh` | Carbon per MWh of a flat 1 MW load, each hour at the carbon intensity of generation (carbon_intensity_hourly) | kgCO2/MWh | 626 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `own_data` | 1 when the month rests on CAISO's own supply by fuel (California from the join), else 0 | count | 638 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift10_carbon_change_pct` | Change in carbon per MWh from moving 10 percent of each day's energy into the four cleanest hours, percent of the flat load's figure (below zero a fall) | pct | 626 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift10_cost_change_pct` | Change in cost per MWh from moving 10 percent of each day's energy into the four cleanest hours, percent of the flat load's figure (below zero a fall) | pct | 204 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift10_cost_usd_per_mwh` | Cost per MWh at the day-ahead hub price of the flat load with 10 percent of each day's energy moved into the four cleanest hours | USD/MWh | 204 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift10_kgco2_per_mwh` | Carbon per MWh of the flat load with 10 percent of each day's energy moved into the four cleanest hours of the month's average day | kgCO2/MWh | 626 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift20_carbon_change_pct` | Change in carbon per MWh from moving 20 percent of each day's energy into the four cleanest hours, percent of the flat load's figure (below zero a fall) | pct | 626 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift20_cost_change_pct` | Change in cost per MWh from moving 20 percent of each day's energy into the four cleanest hours, percent of the flat load's figure (below zero a fall) | pct | 204 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift20_cost_usd_per_mwh` | Cost per MWh at the day-ahead hub price of the flat load with 20 percent of each day's energy moved into the four cleanest hours | USD/MWh | 204 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift20_kgco2_per_mwh` | Carbon per MWh of the flat load with 20 percent of each day's energy moved into the four cleanest hours of the month's average day | kgCO2/MWh | 626 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shift_days` | Days counted in the carbon figures of the flat load and its shifts (every hour with a carbon intensity) | count | 626 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `year_carbon_free_share_flat_pct` | Year: mean of the hours' shares: the carbon-free share met by a load that draws the same power every hour | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_carbon_free_share_pct` | Year: carbon-free MWh over generation MWh, over the complete days | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_cost_days` | Year: days counted in the cost figures (every hour with a day-ahead hub price) | count | 20 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_days_held` | Year: the complete days of the months written, the days the yearly figures are over | count | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_flat_cost_usd_per_mwh` | Year: cost per MWh of a flat 1 MW load at the grid's day-ahead hub price | USD/MWh | 20 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_flat_kgco2_per_mwh` | Year: carbon per MWh of a flat 1 MW load, each hour at the carbon intensity of generation (carbon_intensity_hourly) | kgCO2/MWh | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_hours_cf_ge50_pct` | Year: share of the held hours whose carbon-free share is at or above 50 percent | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_hours_cf_ge75_pct` | Year: share of the held hours whose carbon-free share is at or above 75 percent | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_hours_cf_ge90_pct` | Year: share of the held hours whose carbon-free share is at or above 90 percent | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_mix_100_energy_pct` | Year: a flat load buys clean energy equal to 100 percent of its use, delivered in the shape of all the grid's carbon-free generation; share of the load's energy met in the hour it is used | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_mix_100_hours_pct` | Year: a flat load buys clean energy equal to 100 percent of its use, delivered in the shape of all the grid's carbon-free generation; share of hours in which the delivery covers the whole load | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_mix_150_energy_pct` | Year: a flat load buys clean energy equal to 150 percent of its use, delivered in the shape of all the grid's carbon-free generation; share of the load's energy met in the hour it is used | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_mix_150_hours_pct` | Year: a flat load buys clean energy equal to 150 percent of its use, delivered in the shape of all the grid's carbon-free generation; share of hours in which the delivery covers the whole load | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_mix_50_energy_pct` | Year: a flat load buys clean energy equal to 50 percent of its use, delivered in the shape of all the grid's carbon-free generation; share of the load's energy met in the hour it is used | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_mix_50_hours_pct` | Year: a flat load buys clean energy equal to 50 percent of its use, delivered in the shape of all the grid's carbon-free generation; share of hours in which the delivery covers the whole load | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_solar_100_energy_pct` | Year: a flat load buys clean energy equal to 100 percent of its use, delivered in the shape of the grid's solar generation; share of the load's energy met in the hour it is used | pct | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_solar_100_hours_pct` | Year: a flat load buys clean energy equal to 100 percent of its use, delivered in the shape of the grid's solar generation; share of hours in which the delivery covers the whole load | pct | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_solar_150_energy_pct` | Year: a flat load buys clean energy equal to 150 percent of its use, delivered in the shape of the grid's solar generation; share of the load's energy met in the hour it is used | pct | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_solar_150_hours_pct` | Year: a flat load buys clean energy equal to 150 percent of its use, delivered in the shape of the grid's solar generation; share of hours in which the delivery covers the whole load | pct | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_solar_50_energy_pct` | Year: a flat load buys clean energy equal to 50 percent of its use, delivered in the shape of the grid's solar generation; share of the load's energy met in the hour it is used | pct | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_solar_50_hours_pct` | Year: a flat load buys clean energy equal to 50 percent of its use, delivered in the shape of the grid's solar generation; share of hours in which the delivery covers the whole load | pct | 46 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_wind_100_energy_pct` | Year: a flat load buys clean energy equal to 100 percent of its use, delivered in the shape of the grid's wind generation; share of the load's energy met in the hour it is used | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_wind_100_hours_pct` | Year: a flat load buys clean energy equal to 100 percent of its use, delivered in the shape of the grid's wind generation; share of hours in which the delivery covers the whole load | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_wind_150_energy_pct` | Year: a flat load buys clean energy equal to 150 percent of its use, delivered in the shape of the grid's wind generation; share of the load's energy met in the hour it is used | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_wind_150_hours_pct` | Year: a flat load buys clean energy equal to 150 percent of its use, delivered in the shape of the grid's wind generation; share of hours in which the delivery covers the whole load | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_wind_50_energy_pct` | Year: a flat load buys clean energy equal to 50 percent of its use, delivered in the shape of the grid's wind generation; share of the load's energy met in the hour it is used | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_match_wind_50_hours_pct` | Year: a flat load buys clean energy equal to 50 percent of its use, delivered in the shape of the grid's wind generation; share of hours in which the delivery covers the whole load | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_months` | Year: months written (a year is written when at most one of its months due is missing) | count | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_months_due` | Year: months due, up to the last month written | count | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_own_data_months` | Year: months resting on CAISO's own supply by fuel | count | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift10_carbon_change_pct` | Year: change in carbon per MWh from moving 10 percent of each day's energy into the four cleanest hours, percent of the flat load's figure (below zero a fall) | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift10_cost_change_pct` | Year: change in cost per MWh from moving 10 percent of each day's energy into the four cleanest hours, percent of the flat load's figure (below zero a fall) | pct | 20 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift10_cost_usd_per_mwh` | Year: cost per MWh at the day-ahead hub price of the flat load with 10 percent of each day's energy moved into the four cleanest hours | USD/MWh | 20 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift10_kgco2_per_mwh` | Year: carbon per MWh of the flat load with 10 percent of each day's energy moved into the four cleanest hours of the month's average day | kgCO2/MWh | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift20_carbon_change_pct` | Year: change in carbon per MWh from moving 20 percent of each day's energy into the four cleanest hours, percent of the flat load's figure (below zero a fall) | pct | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift20_cost_change_pct` | Year: change in cost per MWh from moving 20 percent of each day's energy into the four cleanest hours, percent of the flat load's figure (below zero a fall) | pct | 20 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift20_cost_usd_per_mwh` | Year: cost per MWh at the day-ahead hub price of the flat load with 20 percent of each day's energy moved into the four cleanest hours | USD/MWh | 20 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift20_kgco2_per_mwh` | Year: carbon per MWh of the flat load with 20 percent of each day's energy moved into the four cleanest hours of the month's average day | kgCO2/MWh | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_shift_days` | Year: days counted in the carbon figures of the flat load and its shifts (every hour with a carbon intensity) | count | 52 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

### `deal_counterparties`

One counterparty of the deal tracker: a name a deal in energy_deals gives as its buyer or seller, once its spellings are joined, with its deal counts.

Shape: entities. Keys: `entity_id`. License: public; tier: model_extracted. Rows read on 2026-11-20: 532.

- **Time:** No time column; first_deal and last_deal are the dates of its earliest and latest deal; vintage is the build's run id.
- **Revisions:** Rewritten whole as one snapshot by each daily build from energy_deals; folded duplicates counted once.
- **Method note:** [`docs/methods/deal_counterparties.md`](../methods/deal_counterparties.md)
- **Cite as:** Energy Research Warehouse (ERW). Deal tracker counterparties (energy_deals, warehouse/deals/extract.py). Via the Energy Research Warehouse (ERW), table `deal_counterparties`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: counterparty:<the name's words> | none | text | for example counterparty:1komma5grad, counterparty:247_solar, counterparty:a_leading_frontier_ai_lab; 532 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: company on every row | none | text | company | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The canonical name: the spelling the deals use most | none | text | for example 1Komma5Grad, 247 Solar, ACME Solar; 532 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 532 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 532 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 532 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 532 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 532 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 532 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 532 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:energy_deals | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://electrek.co/2026/09/27/nio-power-geely-30-stake-battery-swap-rmb16-billion/, https://heatmap.news/climate-tech/coreshell-series-b, https://lngprime.com/americas/argent-lng-awards-feed-contract/197559/; 383 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-13T15:10:45Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The build's run id (a UTC timestamp), not a data date | none | text | 20261113T151045Z | 0 |
| `kind` | The kind of counterparty: utility (an exact EIA-861 utility name), ai_buyer (a name on the AI-power rule's party list), government, or company | none | text | ai_buyer, company, government | 0 |
| `parent` | The parent company, given only where the name's own words show it (a possessive, a unit or arm) or the alias list does | none | text | Aditya Birla, Adnoc, Amazon, BlackRock, Blackstone, Chevron, Constellation Energy, EIG, ExxonMobil, Geely Holding, General Motors, MAIRE, OGE Energy | 518: No parent shown by the name or the alias list |
| `eia861_utility_number` | The EIA-861 utility number, where the name is exactly one utility's name in EIA-861 | none | empty | no cell holds a value | 532: No counterparty matches one EIA-861 utility (no cell holds a value) |
| `spellings` | The spellings of the name the deals use, joined | none | text | for example 1Komma5Grad, 247 Solar, ACME Solar; 532 distinct | 0 |
| `deals` | The deals that name the counterparty, as buyer or seller | count | integer | 1, 10, 11, 12, 14, 18, 2, 22, 3, 4, 5, 6, 7, 8, 9 | 0 |
| `as_buyer` | The deals that name it as buyer | count | integer | 0, 1, 12, 13, 14, 15, 18, 2, 3, 4, 5, 6, 8, 9 | 0 |
| `as_seller` | The deals that name it as seller | count | integer | 0, 1, 2, 3, 4, 5, 6, 7, 8 | 0 |
| `mw_stated` | The sum of the MW its deals state | MW | number | 20.0 to 5400.0; 31 distinct | 478: None of its deals states a MW figure |
| `deals_with_mw` | How many of its deals state a MW figure | count | integer | 0, 1, 2, 3, 4 | 0 |
| `ai_power_deals` | How many of its deals are AI-power deals | count | integer | 0, 1, 12, 13, 18, 2, 3, 4, 5, 6, 7, 9 | 0 |
| `first_deal` | The date of its earliest deal | none | date | 2025-01-05 to 2026-11-13; 164 distinct | 0 |
| `last_deal` | The date of its latest deal | none | date | 2025-01-05 to 2026-11-13; 145 distinct | 0 |
| `event_ids` | The event_ids of its deals in energy_deals, joined by ; | none | text | for example deal:0046c6c22995488c, deal:0046c6c22995488c;deal:665d71e3ff9f1de4;deal:7e901b6ad732c6ca;deal:d64297631c27daa2, deal:006dc20ac6ffe6f3; 438 distinct | 0 |

### `event_study_estimates`

One estimate of an event's effect on one grid's daily demand served or on a hub's daily mean real-time price: for one event day, pooled over the window, as the counterfactual mean, or for one local hour.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 3040.

- **Time:** <outcome>_effect_day rows at the event day (local date at 00:00:00Z); pooled, counterfactual-mean and hour-of-day rows at the window's first day.
- **Revisions:** Rewritten whole each run (every estimate comes from this run); key (entity, variable, ts_utc, event); vintage is not filled.
- **Source:** erw:event_study ERW derived table, event study method (docs/methods/event_study.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/event_study.md)
- **Method note:** [`docs/methods/event_study.md`](../methods/event_study.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Event study estimates (warehouse/derived/event_study.py). Via the Energy Research Warehouse (ERW), table `event_study_estimates`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930:<BA> for demand; ercot:HB_HUBAVG and three other main hubs (isone:.H.INTERNAL_HUB, miso:INDIANA.HUB, nyiso:N.Y.C.) for the price | none | text | eia930:CISO, eia930:ERCO, eia930:ISNE, eia930:MISO, eia930:NYIS, eia930:PJM, eia930:SWPP, eia930:US48, ercot:HB_HUBAVG, isone:.H.INTERNAL_HUB, miso:INDIANA.HUB, nyiso:N.Y.C., spp:SPPNORTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2020-03-01T00:00:00Z to 2026-02-02T00:00:00Z; 217 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1238136.923077 to 10002125.478261; 3040 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1D, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-DE,US-DC,US-IL,US-IN,US-KY,US-MD,US-MI,US-NJ,US-NC,US-OH,US-PA,US-TN,US-VA,US-WV, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3040 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3040 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:event_study | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/event_study.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-19T09:46:06Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3040 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48) | none | text | ciso, erco, isne, miso, nyis, pjm, swpp, us48 | 0 |
| `event` | The event studied, a partition column (uri_2021, covid_2020, caiso_heat_2020, caiso_heat_2022, elliott_2022, ercot_heat_2023, cold_2025, cold_2026, east_heat_2025) | none | text | caiso_heat_2020, caiso_heat_2022, cold_2025, cold_2026, covid_2020, east_heat_2025, elliott_2022, ercot_heat_2023, uri_2021 | 0 |
| `x_std_error` | The estimate's heteroskedasticity-robust (HC1) standard error; a single day's adds the baseline residual variance | the row's unit | number | 1.558606 to 941905.482593; 1966 distinct | 65: Empty on the counterfactual-mean rows, which are means, not estimated effects |
| `x_ci_low` | Lower end of the 95 percent interval: the estimate less 1.96 standard errors | the row's unit | number | -2582448.607907 to 616062.554395; 2975 distinct | 65: Empty on the counterfactual-mean rows |
| `x_ci_high` | Upper end of the 95 percent interval: the estimate plus 1.96 standard errors | the row's unit | number | -468714.428903 to 4071124.723204; 2975 distinct | 65: Empty on the counterfactual-mean rows |
| `x_n` | Days (or hours, for the hour-of-day profile) in the regression | count | integer | 123, 182, 184, 21, 22, 26, 27, 275, 276, 30, 32, 33, 42, 54 | 0 |
| `x_spec` | The specification: dow_year_mean_v1 (day-of-week and year effects), dow_year_temp_v1 (plus heating and cooling degree days and their squares), dow_trend_v1 (a linear year trend in place of year effects, a robustness row) | none | text | dow_trend_v1, dow_year_mean_v1, dow_year_temp_v1 | 0 |
| `x_term` | What the estimate is, in words (event day <date>, pooled effect at local hour HH, and so on) | none | text | for example event day 2020-03-01, event day 2020-03-01, controlling for temperature, event day 2020-03-02; 431 distinct | 0 |

Variables (38):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `demand_mw_effect_h00` | Pooled effect of the event on demand at local hour 00 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h01` | Pooled effect of the event on demand at local hour 01 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h02` | Pooled effect of the event on demand at local hour 02 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h03` | Pooled effect of the event on demand at local hour 03 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h04` | Pooled effect of the event on demand at local hour 04 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h05` | Pooled effect of the event on demand at local hour 05 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h06` | Pooled effect of the event on demand at local hour 06 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h07` | Pooled effect of the event on demand at local hour 07 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h08` | Pooled effect of the event on demand at local hour 08 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h09` | Pooled effect of the event on demand at local hour 09 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h10` | Pooled effect of the event on demand at local hour 10 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h11` | Pooled effect of the event on demand at local hour 11 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h12` | Pooled effect of the event on demand at local hour 12 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h13` | Pooled effect of the event on demand at local hour 13 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h14` | Pooled effect of the event on demand at local hour 14 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h15` | Pooled effect of the event on demand at local hour 15 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h16` | Pooled effect of the event on demand at local hour 16 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h17` | Pooled effect of the event on demand at local hour 17 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h18` | Pooled effect of the event on demand at local hour 18 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h19` | Pooled effect of the event on demand at local hour 19 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h20` | Pooled effect of the event on demand at local hour 20 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h21` | Pooled effect of the event on demand at local hour 21 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h22` | Pooled effect of the event on demand at local hour 22 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mw_effect_h23` | Pooled effect of the event on demand at local hour 23 (the hour-of-day profile), MW | MW | 27 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mwh_counterfactual_mean` | Mean counterfactual daily demand served over the event days (the denominator of the pooled effect's percent) | MWh | 34 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mwh_counterfactual_mean_temp` | Mean counterfactual daily demand over the event days, temperature-controlled specification | MWh | 17 | 2020-03-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `demand_mwh_effect_day` | The event day's effect on demand served: the day's demand less its counterfactual | MWh | 1043 | 2020-03-01T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_mwh_effect_day_temp` | The event day's effect on demand served, temperature-controlled specification | MWh | 791 | 2020-03-01T00:00:00Z | 2023-09-10T00:00:00Z |
| `demand_mwh_effect_pooled` | Pooled effect on daily demand served over the event days (one indicator for every event day), MWh a day | MWh | 34 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `demand_mwh_effect_pooled_temp` | Pooled effect on daily demand served, temperature-controlled specification | MWh | 17 | 2020-03-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `demand_mwh_effect_pooled_trend` | Pooled effect on daily demand served with a linear year trend in place of the year effects (robustness) | MWh | 33 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `rt_mean_counterfactual_mean` | Mean counterfactual daily mean real-time hub price over the event days | USD/MWh | 10 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `rt_mean_counterfactual_mean_temp` | Mean counterfactual daily mean real-time hub price, temperature-controlled specification | USD/MWh | 4 | 2020-03-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `rt_mean_effect_day` | The event day's effect on the day's mean real-time hub price: the day's price less its counterfactual | USD/MWh | 227 | 2020-03-01T00:00:00Z | 2026-02-02T00:00:00Z |
| `rt_mean_effect_day_temp` | The event day's effect on the mean real-time hub price, temperature-controlled specification | USD/MWh | 162 | 2020-03-01T00:00:00Z | 2023-09-10T00:00:00Z |
| `rt_mean_effect_pooled` | Pooled effect on the daily mean real-time hub price over the event days, USD/MWh a day | USD/MWh | 10 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |
| `rt_mean_effect_pooled_temp` | Pooled effect on the daily mean real-time hub price, temperature-controlled specification | USD/MWh | 4 | 2020-03-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `rt_mean_effect_pooled_trend` | Pooled effect on the daily mean real-time hub price with a linear year trend (robustness) | USD/MWh | 6 | 2020-03-01T00:00:00Z | 2026-01-23T00:00:00Z |

### `event_window_daily`

One event's daily (or, for COVID-19, weekly) value of one figure for one grid, hub or weather station, on a day of the event window or a baseline day of earlier years.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 29953.

- **Time:** ts_utc is the local operating day at 00:00:00Z (America/Chicago for ERCOT, each BA's own zone for the others); weekly rows (freq P1W) at the week's first day.
- **Revisions:** Rewritten whole by each run; key (entity, variable, ts_utc, event), so a day may stand once for each event it belongs to; vintage is not filled.
- **Source:** erw:event_window ERW derived table, events method (docs/methods/events.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/events.md)
- **Method note:** [`docs/methods/events.md`](../methods/events.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Event windows, daily figures around an event and its baseline (docs/methods/events.md). Via the Energy Research Warehouse (ERW), table `event_window_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930:<BA> for demand, generation and intensity; ercot:HB_HUBAVG and <iso>:<hub> for prices; noaa:<station> for weather | none | text | eia930:CISO, eia930:ERCO, eia930:ISNE, eia930:MISO, eia930:NYIS, eia930:PJM, eia930:SWPP, eia930:US48, ercot:HB_HUBAVG, isone:.H.INTERNAL_HUB, miso:INDIANA.HUB, noaa:BOS, noaa:DFW, noaa:IAH, noaa:JFK, noaa:LAX, noaa:MSP, noaa:OKC, noaa:ORD, noaa:PHL, noaa:SAC, nyiso:N.Y.C., spp:SPPNORTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-03-04T00:00:00Z to 2026-02-02T00:00:00Z; 625 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -9334580.0 to 12200004.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD/MWh, degF, degF-day, kgCO2/MWh, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1D, P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Empty on the weather station rows (noaa:<station>) | none | text | US, US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-DE,US-DC,US-IL,US-IN,US-KY,US-MD,US-MI,US-NJ,US-NC,US-OH,US-PA,US-TN,US-VA,US-WV, US-NY, US-TX | 13375 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Filled on the hub price rows only: <iso>_dam or <iso>_rtm | none | text | ercot_dam, ercot_rtm, isone_dam, isone_rtm, miso_dam, miso_rtm, nyiso_dam, nyiso_rtm, spp_dam, spp_rtm | 27697 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The NOAA ISD station id on the weather rows; empty on the others | none | integer | 72243012960, 72259003927, 72295023174, 72353013967, 72408013739, 72483023232, 72509014739, 72530094846, 72658014922, 74486094789 | 16578 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:event_window | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/events.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-19T09:43:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 29953 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48) | none | text | ciso, erco, isne, miso, nyis, pjm, swpp, us48 | 0 |
| `event` | The event the row belongs to, a partition column (uri_2021, covid_2020, caiso_heat_2020, caiso_heat_2022, elliott_2022, ercot_heat_2023, cold_2025, cold_2026, east_heat_2025) | none | text | caiso_heat_2020, caiso_heat_2022, cold_2025, cold_2026, covid_2020, east_heat_2025, elliott_2022, ercot_heat_2023, uri_2021 | 0 |

Variables (23):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `cdd_65f` | The station's cooling degree days at 65 F for the local day, from (max + min) / 2 | degF-day | 2675 | 2018-03-04T00:00:00Z | 2023-09-10T00:00:00Z |
| `da_max` | The day's highest hourly day-ahead hub price | USD/MWh | 428 | 2019-02-07T00:00:00Z | 2026-02-02T00:00:00Z |
| `da_mean` | The day's mean hourly day-ahead hub price | USD/MWh | 704 | 2018-03-04T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_max_mw` | The day's highest hour of demand | MW | 3043 | 2018-03-04T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_max_mw_vs_baseline` | The day's highest hour of demand less the mean of the baseline days' highest hours | MW | 288 | 2020-08-12T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_max_pct_vs_baseline` | The day's highest hour of demand against the mean of the baseline days' highest hours, percent | pct | 288 | 2020-08-12T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_min_mw` | The day's lowest hour of demand | MW | 3043 | 2018-03-04T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_mwh` | EIA's hourly demand summed over the day's hours | MWh | 3043 | 2018-03-04T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_mwh_day_change` | Event days only: the day's demand less the previous day of the window | MWh | 17 | 2021-02-08T00:00:00Z | 2021-02-24T00:00:00Z |
| `demand_mwh_vs_baseline` | Event days only: the day's demand less the mean of its baseline days | MWh | 1039 | 2020-03-01T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_mwh_vs_baseline_week` | The week's demand less the mean of its baseline weeks (COVID-19, freq P1W) | MWh | 101 | 2020-03-01T00:00:00Z | 2020-05-24T00:00:00Z |
| `demand_pct_vs_baseline` | Event days only: (the day's demand over the mean of its baseline days, minus 1) times 100 | pct | 1021 | 2020-03-01T00:00:00Z | 2026-02-02T00:00:00Z |
| `demand_pct_vs_baseline_week` | The same over the week's seven days (COVID-19, freq P1W) | pct | 101 | 2020-03-01T00:00:00Z | 2020-05-24T00:00:00Z |
| `hdd_65f` | The station's heating degree days at 65 F for the local day, from (max + min) / 2 | degF-day | 2675 | 2018-03-04T00:00:00Z | 2023-09-10T00:00:00Z |
| `intensity_generation` | The day's CO2 generated times 1,000 over its net generation (carbon intensity of generation) | kgCO2/MWh | 2249 | 2018-08-13T00:00:00Z | 2026-02-02T00:00:00Z |
| `net_generation_mwh` | EIA's hourly net generation summed over the day | MWh | 54 | 2019-02-07T00:00:00Z | 2021-02-24T00:00:00Z |
| `net_generation_mwh_day_change` | Event days only: the day's net generation less the previous day of the window | MWh | 17 | 2021-02-08T00:00:00Z | 2021-02-24T00:00:00Z |
| `net_generation_mwh_vs_baseline` | Event days only: the day's net generation less the baseline mean of its calendar day | MWh | 18 | 2021-02-07T00:00:00Z | 2021-02-24T00:00:00Z |
| `rt_max` | The day's highest 15-minute real-time hub price (MISO's hourly real-time price) | USD/MWh | 424 | 2019-02-07T00:00:00Z | 2026-02-02T00:00:00Z |
| `rt_mean` | The day's mean real-time hub price | USD/MWh | 700 | 2018-03-04T00:00:00Z | 2026-02-02T00:00:00Z |
| `temp_max_f` | The station's highest temperature of the local day | degF | 2675 | 2018-03-04T00:00:00Z | 2023-09-10T00:00:00Z |
| `temp_mean_f` | The station's mean temperature of the local day (the mean of the clock hours' means) | degF | 2675 | 2018-03-04T00:00:00Z | 2023-09-10T00:00:00Z |
| `temp_min_f` | The station's lowest temperature of the local day | degF | 2675 | 2018-03-04T00:00:00Z | 2023-09-10T00:00:00Z |

### `flex_alert_effects`

One value of the Flex Alert scorecard for CAISO's balancing authority: for one alert day (freq P1D), one hour of an alert day (PT1H) or one year (P1Y).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 3429.

- **Time:** P1D rows at the Pacific day at 00:00:00Z; PT1H rows at the hour's start (local 12:00 to 23:00); P1Y rows at 1 January of the year.
- **Revisions:** Rewritten whole by each run of the scorecard builder (the old file removed first); vintage is not filled.
- **Source:** erw:flex_alert_scorecard ERW derived table, Flex Alert scorecard method (docs/methods/flex_alert_scorecard.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/flex_alert_scorecard.md)
- **Method note:** [`docs/methods/flex_alert_scorecard.md`](../methods/flex_alert_scorecard.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Flex Alert scorecard (warehouse/derived/flex_alert_scorecard.py). Via the Energy Research Warehouse (ERW), table `flex_alert_effects`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930:CISO on every row | none | text | eia930:CISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-01-01T00:00:00Z to 2024-07-25T06:00:00Z; 479 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -5804512.4267 to 380303.2757; 2755 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD, USD/MWh, count, degF, hour, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1D, P1Y, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3429 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3429 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:flex_alert_scorecard | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/flex_alert_scorecard.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-17T07:24:23Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3429 |

Variables (49):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `actual_mw` | Actual demand in the hour (EIA-930 hourly demand) | MW | 456 | 2018-07-24T19:00:00Z | 2024-07-25T06:00:00Z |
| `actual_mwh` | Actual demand summed over the day's alert hours | MWh | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `alert_first_hour` | The day's first alert hour, local | hour | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `alert_hour` | 1 when the hour is an alert hour, else 0 | count | 456 | 2018-07-24T19:00:00Z | 2024-07-25T06:00:00Z |
| `alert_hours` | The day's alert hours | count | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `alert_last_hour` | The end of the day's alert window, local hour (the last alert hour plus one) | hour | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `basis_flex_alert` | 1 where the day's hours are the Flex Alert's, else 0 (another notice gave them) | count | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `hours_assumed` | 1 where no notice gave hours and 16:00 to 21:00 was assumed, else 0 | count | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `predicted_mw` | The model's predicted demand in the hour, from the weather and the calendar | MW | 456 | 2018-07-24T19:00:00Z | 2024-07-25T06:00:00Z |
| `predicted_mw_hi` | Upper end of the 90 percent interval of the predicted demand in the hour | MW | 456 | 2018-07-24T19:00:00Z | 2024-07-25T06:00:00Z |
| `predicted_mw_lo` | Lower end of the 90 percent interval of the predicted demand in the hour | MW | 456 | 2018-07-24T19:00:00Z | 2024-07-25T06:00:00Z |
| `predicted_mwh` | Predicted demand summed over the day's alert hours | MWh | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `price_usd_mwh` | Mean day-ahead hub price over the day's alert hours (the mean of SP15 and NP15) | USD/MWh | 4 | 2023-07-20T00:00:00Z | 2024-07-24T00:00:00Z |
| `reduction_mw` | Mean over the day's alert hours of predicted less actual demand (positive: demand below the model, a cut) | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `reduction_mw_hi` | Upper end of the 90 percent interval of reduction_mw | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `reduction_mw_lo` | Lower end of the 90 percent interval of reduction_mw | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `reduction_mwh` | Predicted less actual demand summed over the day's alert hours | MWh | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `reduction_mwh_hi` | Upper end of the 90 percent interval of reduction_mwh | MWh | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `reduction_mwh_lo` | Lower end of the 90 percent interval of reduction_mwh | MWh | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `reduction_pct` | The day's cut as a percent of predicted demand over the alert hours | pct | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `temp_max_f` | The day's highest population-weighted temperature (Los Angeles 0.5, Sacramento 0.3, Fresno 0.2) | degF | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `train_days_as_hot` | Training days whose highest weighted temperature was at least the day's: the model's support | count | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `value_usd` | The cut times the day-ahead price, summed over the alert hours with a price (a wholesale lower bound) | USD | 4 | 2023-07-20T00:00:00Z | 2024-07-24T00:00:00Z |
| `value_usd_hi` | Upper end of the 90 percent interval of value_usd | USD | 4 | 2023-07-20T00:00:00Z | 2024-07-24T00:00:00Z |
| `value_usd_lo` | Lower end of the 90 percent interval of value_usd | USD | 4 | 2023-07-20T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_cdh_dew_reduction_mw` | The day's cut in MW under the specification base_cdh_dew (base plus CDH times dew point) | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_cdh_dew_reduction_mw_hi` | Upper end of the 90 percent interval of the day's cut under base_cdh_dew | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_cdh_dew_reduction_mw_lo` | Lower end of the 90 percent interval of the day's cut under base_cdh_dew | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_prev24sq_reduction_mw` | The day's cut in MW under the specification base_prev24sq (base plus the 24-hour cooling degree mean squared) | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_prev24sq_reduction_mw_hi` | Upper end of the 90 percent interval of the day's cut under base_prev24sq | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_prev24sq_reduction_mw_lo` | Lower end of the 90 percent interval of the day's cut under base_prev24sq | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_reduction_mw` | The day's cut in MW under the specification base (minimal plus the 24-hour cooling degree mean and the dew point) | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_reduction_mw_hi` | Upper end of the 90 percent interval of the day's cut under base | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_base_reduction_mw_lo` | Lower end of the 90 percent interval of the day's cut under base | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_minimal_reduction_mw` | The day's cut in MW under the specification minimal (cooling degree hours, their square and the calendar) | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_minimal_reduction_mw_hi` | Upper end of the 90 percent interval of the day's cut under minimal | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `variant_minimal_reduction_mw_lo` | Lower end of the 90 percent interval of the day's cut under minimal | MW | 38 | 2018-07-24T00:00:00Z | 2024-07-24T00:00:00Z |
| `year_days` | Alert days in the year | count | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_hours` | Alert hours in the year | count | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_reduction_mw` | Mean cut over the year's alert hours, predicted less actual demand | MW | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_reduction_mw_hi` | Upper end of the 90 percent interval of year_reduction_mw | MW | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_reduction_mw_lo` | Lower end of the 90 percent interval of year_reduction_mw | MW | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_reduction_mwh` | The cut summed over the year's alert hours | MWh | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_reduction_mwh_hi` | Upper end of the 90 percent interval of year_reduction_mwh | MWh | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_reduction_mwh_lo` | Lower end of the 90 percent interval of year_reduction_mwh | MWh | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_reduction_pct` | The year's cut as a percent of predicted demand over its alert hours | pct | 7 | 2018-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_value_usd` | The year's cut times the day-ahead price, summed over its alert hours with a price | USD | 2 | 2023-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_value_usd_hi` | Upper end of the 90 percent interval of year_value_usd | USD | 2 | 2023-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `year_value_usd_lo` | Lower end of the 90 percent interval of year_value_usd | USD | 2 | 2023-01-01T00:00:00Z | 2024-01-01T00:00:00Z |

### `flex_alert_model`

One figure of the Flex Alert scorecard's demand model for CAISO: a pooled estimate, an out-of-sample check, a specification compared, a model setting, an hourly coefficient, or one held-out hot day's error.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 881.

- **Time:** The model's figures are dated 2018-07-01T00:00:00Z, the sample's first day (freq blank: not a time series); held-out day rows (freq P1D) at the Pacific day at 00:00:00Z.
- **Revisions:** Rewritten whole by each run of the scorecard builder (the old file removed first); vintage is not filled.
- **Source:** erw:flex_alert_scorecard ERW derived table, Flex Alert scorecard method (docs/methods/flex_alert_scorecard.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/flex_alert_scorecard.md)
- **Method note:** [`docs/methods/flex_alert_scorecard.md`](../methods/flex_alert_scorecard.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Flex Alert scorecard (warehouse/derived/flex_alert_scorecard.py). Via the Energy Research Warehouse (ERW), table `flex_alert_model`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: erw:flex_alert_model on every row | none | text | erw:flex_alert_model | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-01T00:00:00Z to 2025-08-24T00:00:00Z; 129 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -8043179.4743 to 50464.9058; 841 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD, USD/MWh, count, degF, pct, ratio | 0 |
| `freq` | How long the interval of the row is. Here: Empty on the model's figures (a parameter, not a time series); P1D on the held-out days' rows | none | text | P1D | 584 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 881 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 881 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:flex_alert_scorecard | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/flex_alert_scorecard.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-17T07:24:23Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 881 |

Variables (587; the first 300 by name):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `alert_days_hotter_than_threshold` | Alert days at least as hot as the held-out threshold temperature | count | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `bootstrap_replicates` | Replicates behind the 90 percent intervals | count | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_cdh` | Demand model for local hour 00: coefficient of the cooling degree hour, max(T - 65 F, 0) of the weighted temperature in the hour (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_cdh2` | Demand model for local hour 00: coefficient of the cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_cdh_prev24` | Demand model for local hour 00: coefficient of the mean cooling degree hour over the 24 hours before (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_cdh_prev24_2` | Demand model for local hour 00: coefficient of the 24-hour mean cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_cdh_x_dew` | Demand model for local hour 00: coefficient of the cooling degree hour times the dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_dew_point` | Demand model for local hour 00: coefficient of the weighted dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_holiday` | Demand model for local hour 00: coefficient of a US federal holiday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_intercept` | Demand model for local hour 00: coefficient of the constant term (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_month10` | Demand model for local hour 00: coefficient of the month October, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_month6` | Demand model for local hour 00: coefficient of the month June, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_month7` | Demand model for local hour 00: coefficient of the month July, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_month8` | Demand model for local hour 00: coefficient of the month August, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_month9` | Demand model for local hour 00: coefficient of the month September, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_saturday` | Demand model for local hour 00: coefficient of a Saturday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_sunday` | Demand model for local hour 00: coefficient of a Sunday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_year2019` | Demand model for local hour 00: coefficient of the year 2019, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_year2020` | Demand model for local hour 00: coefficient of the year 2020, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_year2021` | Demand model for local hour 00: coefficient of the year 2021, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_year2022` | Demand model for local hour 00: coefficient of the year 2022, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_year2023` | Demand model for local hour 00: coefficient of the year 2023, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_year2024` | Demand model for local hour 00: coefficient of the year 2024, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h00_year2025` | Demand model for local hour 00: coefficient of the year 2025, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_cdh` | Demand model for local hour 01: coefficient of the cooling degree hour, max(T - 65 F, 0) of the weighted temperature in the hour (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_cdh2` | Demand model for local hour 01: coefficient of the cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_cdh_prev24` | Demand model for local hour 01: coefficient of the mean cooling degree hour over the 24 hours before (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_cdh_prev24_2` | Demand model for local hour 01: coefficient of the 24-hour mean cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_cdh_x_dew` | Demand model for local hour 01: coefficient of the cooling degree hour times the dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_dew_point` | Demand model for local hour 01: coefficient of the weighted dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_holiday` | Demand model for local hour 01: coefficient of a US federal holiday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_intercept` | Demand model for local hour 01: coefficient of the constant term (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_month10` | Demand model for local hour 01: coefficient of the month October, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_month6` | Demand model for local hour 01: coefficient of the month June, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_month7` | Demand model for local hour 01: coefficient of the month July, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_month8` | Demand model for local hour 01: coefficient of the month August, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_month9` | Demand model for local hour 01: coefficient of the month September, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_saturday` | Demand model for local hour 01: coefficient of a Saturday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_sunday` | Demand model for local hour 01: coefficient of a Sunday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_year2019` | Demand model for local hour 01: coefficient of the year 2019, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_year2020` | Demand model for local hour 01: coefficient of the year 2020, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_year2021` | Demand model for local hour 01: coefficient of the year 2021, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_year2022` | Demand model for local hour 01: coefficient of the year 2022, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_year2023` | Demand model for local hour 01: coefficient of the year 2023, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_year2024` | Demand model for local hour 01: coefficient of the year 2024, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h01_year2025` | Demand model for local hour 01: coefficient of the year 2025, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_cdh` | Demand model for local hour 02: coefficient of the cooling degree hour, max(T - 65 F, 0) of the weighted temperature in the hour (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_cdh2` | Demand model for local hour 02: coefficient of the cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_cdh_prev24` | Demand model for local hour 02: coefficient of the mean cooling degree hour over the 24 hours before (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_cdh_prev24_2` | Demand model for local hour 02: coefficient of the 24-hour mean cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_cdh_x_dew` | Demand model for local hour 02: coefficient of the cooling degree hour times the dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_dew_point` | Demand model for local hour 02: coefficient of the weighted dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_holiday` | Demand model for local hour 02: coefficient of a US federal holiday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_intercept` | Demand model for local hour 02: coefficient of the constant term (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_month10` | Demand model for local hour 02: coefficient of the month October, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_month6` | Demand model for local hour 02: coefficient of the month June, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_month7` | Demand model for local hour 02: coefficient of the month July, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_month8` | Demand model for local hour 02: coefficient of the month August, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_month9` | Demand model for local hour 02: coefficient of the month September, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_saturday` | Demand model for local hour 02: coefficient of a Saturday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_sunday` | Demand model for local hour 02: coefficient of a Sunday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_year2019` | Demand model for local hour 02: coefficient of the year 2019, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_year2020` | Demand model for local hour 02: coefficient of the year 2020, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_year2021` | Demand model for local hour 02: coefficient of the year 2021, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_year2022` | Demand model for local hour 02: coefficient of the year 2022, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_year2023` | Demand model for local hour 02: coefficient of the year 2023, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_year2024` | Demand model for local hour 02: coefficient of the year 2024, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h02_year2025` | Demand model for local hour 02: coefficient of the year 2025, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_cdh` | Demand model for local hour 03: coefficient of the cooling degree hour, max(T - 65 F, 0) of the weighted temperature in the hour (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_cdh2` | Demand model for local hour 03: coefficient of the cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_cdh_prev24` | Demand model for local hour 03: coefficient of the mean cooling degree hour over the 24 hours before (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_cdh_prev24_2` | Demand model for local hour 03: coefficient of the 24-hour mean cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_cdh_x_dew` | Demand model for local hour 03: coefficient of the cooling degree hour times the dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_dew_point` | Demand model for local hour 03: coefficient of the weighted dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_holiday` | Demand model for local hour 03: coefficient of a US federal holiday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_intercept` | Demand model for local hour 03: coefficient of the constant term (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_month10` | Demand model for local hour 03: coefficient of the month October, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_month6` | Demand model for local hour 03: coefficient of the month June, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_month7` | Demand model for local hour 03: coefficient of the month July, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_month8` | Demand model for local hour 03: coefficient of the month August, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_month9` | Demand model for local hour 03: coefficient of the month September, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_saturday` | Demand model for local hour 03: coefficient of a Saturday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_sunday` | Demand model for local hour 03: coefficient of a Sunday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_year2019` | Demand model for local hour 03: coefficient of the year 2019, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_year2020` | Demand model for local hour 03: coefficient of the year 2020, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_year2021` | Demand model for local hour 03: coefficient of the year 2021, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_year2022` | Demand model for local hour 03: coefficient of the year 2022, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_year2023` | Demand model for local hour 03: coefficient of the year 2023, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_year2024` | Demand model for local hour 03: coefficient of the year 2024, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h03_year2025` | Demand model for local hour 03: coefficient of the year 2025, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_cdh` | Demand model for local hour 04: coefficient of the cooling degree hour, max(T - 65 F, 0) of the weighted temperature in the hour (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_cdh2` | Demand model for local hour 04: coefficient of the cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_cdh_prev24` | Demand model for local hour 04: coefficient of the mean cooling degree hour over the 24 hours before (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_cdh_prev24_2` | Demand model for local hour 04: coefficient of the 24-hour mean cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_cdh_x_dew` | Demand model for local hour 04: coefficient of the cooling degree hour times the dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_dew_point` | Demand model for local hour 04: coefficient of the weighted dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_holiday` | Demand model for local hour 04: coefficient of a US federal holiday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_intercept` | Demand model for local hour 04: coefficient of the constant term (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_month10` | Demand model for local hour 04: coefficient of the month October, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_month6` | Demand model for local hour 04: coefficient of the month June, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_month7` | Demand model for local hour 04: coefficient of the month July, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_month8` | Demand model for local hour 04: coefficient of the month August, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_month9` | Demand model for local hour 04: coefficient of the month September, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_saturday` | Demand model for local hour 04: coefficient of a Saturday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_sunday` | Demand model for local hour 04: coefficient of a Sunday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_year2019` | Demand model for local hour 04: coefficient of the year 2019, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_year2020` | Demand model for local hour 04: coefficient of the year 2020, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_year2021` | Demand model for local hour 04: coefficient of the year 2021, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_year2022` | Demand model for local hour 04: coefficient of the year 2022, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_year2023` | Demand model for local hour 04: coefficient of the year 2023, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_year2024` | Demand model for local hour 04: coefficient of the year 2024, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h04_year2025` | Demand model for local hour 04: coefficient of the year 2025, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_cdh` | Demand model for local hour 05: coefficient of the cooling degree hour, max(T - 65 F, 0) of the weighted temperature in the hour (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_cdh2` | Demand model for local hour 05: coefficient of the cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_cdh_prev24` | Demand model for local hour 05: coefficient of the mean cooling degree hour over the 24 hours before (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_cdh_prev24_2` | Demand model for local hour 05: coefficient of the 24-hour mean cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_cdh_x_dew` | Demand model for local hour 05: coefficient of the cooling degree hour times the dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_dew_point` | Demand model for local hour 05: coefficient of the weighted dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_holiday` | Demand model for local hour 05: coefficient of a US federal holiday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_intercept` | Demand model for local hour 05: coefficient of the constant term (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_month10` | Demand model for local hour 05: coefficient of the month October, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_month6` | Demand model for local hour 05: coefficient of the month June, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_month7` | Demand model for local hour 05: coefficient of the month July, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_month8` | Demand model for local hour 05: coefficient of the month August, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_month9` | Demand model for local hour 05: coefficient of the month September, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_saturday` | Demand model for local hour 05: coefficient of a Saturday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_sunday` | Demand model for local hour 05: coefficient of a Sunday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_year2019` | Demand model for local hour 05: coefficient of the year 2019, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_year2020` | Demand model for local hour 05: coefficient of the year 2020, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_year2021` | Demand model for local hour 05: coefficient of the year 2021, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_year2022` | Demand model for local hour 05: coefficient of the year 2022, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_year2023` | Demand model for local hour 05: coefficient of the year 2023, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_year2024` | Demand model for local hour 05: coefficient of the year 2024, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h05_year2025` | Demand model for local hour 05: coefficient of the year 2025, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_cdh` | Demand model for local hour 06: coefficient of the cooling degree hour, max(T - 65 F, 0) of the weighted temperature in the hour (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_cdh2` | Demand model for local hour 06: coefficient of the cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_cdh_prev24` | Demand model for local hour 06: coefficient of the mean cooling degree hour over the 24 hours before (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_cdh_prev24_2` | Demand model for local hour 06: coefficient of the 24-hour mean cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_cdh_x_dew` | Demand model for local hour 06: coefficient of the cooling degree hour times the dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_dew_point` | Demand model for local hour 06: coefficient of the weighted dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_holiday` | Demand model for local hour 06: coefficient of a US federal holiday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_intercept` | Demand model for local hour 06: coefficient of the constant term (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_month10` | Demand model for local hour 06: coefficient of the month October, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_month6` | Demand model for local hour 06: coefficient of the month June, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_month7` | Demand model for local hour 06: coefficient of the month July, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_month8` | Demand model for local hour 06: coefficient of the month August, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_month9` | Demand model for local hour 06: coefficient of the month September, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_saturday` | Demand model for local hour 06: coefficient of a Saturday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_sunday` | Demand model for local hour 06: coefficient of a Sunday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_year2019` | Demand model for local hour 06: coefficient of the year 2019, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_year2020` | Demand model for local hour 06: coefficient of the year 2020, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_year2021` | Demand model for local hour 06: coefficient of the year 2021, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_year2022` | Demand model for local hour 06: coefficient of the year 2022, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_year2023` | Demand model for local hour 06: coefficient of the year 2023, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_year2024` | Demand model for local hour 06: coefficient of the year 2024, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h06_year2025` | Demand model for local hour 06: coefficient of the year 2025, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_cdh` | Demand model for local hour 07: coefficient of the cooling degree hour, max(T - 65 F, 0) of the weighted temperature in the hour (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_cdh2` | Demand model for local hour 07: coefficient of the cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_cdh_prev24` | Demand model for local hour 07: coefficient of the mean cooling degree hour over the 24 hours before (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_cdh_prev24_2` | Demand model for local hour 07: coefficient of the 24-hour mean cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_cdh_x_dew` | Demand model for local hour 07: coefficient of the cooling degree hour times the dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_dew_point` | Demand model for local hour 07: coefficient of the weighted dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_holiday` | Demand model for local hour 07: coefficient of a US federal holiday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_intercept` | Demand model for local hour 07: coefficient of the constant term (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_month10` | Demand model for local hour 07: coefficient of the month October, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_month6` | Demand model for local hour 07: coefficient of the month June, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_month7` | Demand model for local hour 07: coefficient of the month July, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_month8` | Demand model for local hour 07: coefficient of the month August, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_month9` | Demand model for local hour 07: coefficient of the month September, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_saturday` | Demand model for local hour 07: coefficient of a Saturday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_sunday` | Demand model for local hour 07: coefficient of a Sunday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_year2019` | Demand model for local hour 07: coefficient of the year 2019, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_year2020` | Demand model for local hour 07: coefficient of the year 2020, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_year2021` | Demand model for local hour 07: coefficient of the year 2021, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_year2022` | Demand model for local hour 07: coefficient of the year 2022, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_year2023` | Demand model for local hour 07: coefficient of the year 2023, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_year2024` | Demand model for local hour 07: coefficient of the year 2024, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h07_year2025` | Demand model for local hour 07: coefficient of the year 2025, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_cdh` | Demand model for local hour 08: coefficient of the cooling degree hour, max(T - 65 F, 0) of the weighted temperature in the hour (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_cdh2` | Demand model for local hour 08: coefficient of the cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_cdh_prev24` | Demand model for local hour 08: coefficient of the mean cooling degree hour over the 24 hours before (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_cdh_prev24_2` | Demand model for local hour 08: coefficient of the 24-hour mean cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_cdh_x_dew` | Demand model for local hour 08: coefficient of the cooling degree hour times the dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_dew_point` | Demand model for local hour 08: coefficient of the weighted dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_holiday` | Demand model for local hour 08: coefficient of a US federal holiday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_intercept` | Demand model for local hour 08: coefficient of the constant term (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_month10` | Demand model for local hour 08: coefficient of the month October, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_month6` | Demand model for local hour 08: coefficient of the month June, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_month7` | Demand model for local hour 08: coefficient of the month July, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_month8` | Demand model for local hour 08: coefficient of the month August, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_month9` | Demand model for local hour 08: coefficient of the month September, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_saturday` | Demand model for local hour 08: coefficient of a Saturday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_sunday` | Demand model for local hour 08: coefficient of a Sunday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_year2019` | Demand model for local hour 08: coefficient of the year 2019, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_year2020` | Demand model for local hour 08: coefficient of the year 2020, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_year2021` | Demand model for local hour 08: coefficient of the year 2021, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_year2022` | Demand model for local hour 08: coefficient of the year 2022, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_year2023` | Demand model for local hour 08: coefficient of the year 2023, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_year2024` | Demand model for local hour 08: coefficient of the year 2024, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h08_year2025` | Demand model for local hour 08: coefficient of the year 2025, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_cdh` | Demand model for local hour 09: coefficient of the cooling degree hour, max(T - 65 F, 0) of the weighted temperature in the hour (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_cdh2` | Demand model for local hour 09: coefficient of the cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_cdh_prev24` | Demand model for local hour 09: coefficient of the mean cooling degree hour over the 24 hours before (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_cdh_prev24_2` | Demand model for local hour 09: coefficient of the 24-hour mean cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_cdh_x_dew` | Demand model for local hour 09: coefficient of the cooling degree hour times the dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_dew_point` | Demand model for local hour 09: coefficient of the weighted dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_holiday` | Demand model for local hour 09: coefficient of a US federal holiday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_intercept` | Demand model for local hour 09: coefficient of the constant term (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_month10` | Demand model for local hour 09: coefficient of the month October, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_month6` | Demand model for local hour 09: coefficient of the month June, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_month7` | Demand model for local hour 09: coefficient of the month July, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_month8` | Demand model for local hour 09: coefficient of the month August, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_month9` | Demand model for local hour 09: coefficient of the month September, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_saturday` | Demand model for local hour 09: coefficient of a Saturday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_sunday` | Demand model for local hour 09: coefficient of a Sunday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_year2019` | Demand model for local hour 09: coefficient of the year 2019, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_year2020` | Demand model for local hour 09: coefficient of the year 2020, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_year2021` | Demand model for local hour 09: coefficient of the year 2021, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_year2022` | Demand model for local hour 09: coefficient of the year 2022, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_year2023` | Demand model for local hour 09: coefficient of the year 2023, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_year2024` | Demand model for local hour 09: coefficient of the year 2024, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h09_year2025` | Demand model for local hour 09: coefficient of the year 2025, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_cdh` | Demand model for local hour 10: coefficient of the cooling degree hour, max(T - 65 F, 0) of the weighted temperature in the hour (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_cdh2` | Demand model for local hour 10: coefficient of the cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_cdh_prev24` | Demand model for local hour 10: coefficient of the mean cooling degree hour over the 24 hours before (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_cdh_prev24_2` | Demand model for local hour 10: coefficient of the 24-hour mean cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_cdh_x_dew` | Demand model for local hour 10: coefficient of the cooling degree hour times the dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_dew_point` | Demand model for local hour 10: coefficient of the weighted dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_holiday` | Demand model for local hour 10: coefficient of a US federal holiday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_intercept` | Demand model for local hour 10: coefficient of the constant term (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_month10` | Demand model for local hour 10: coefficient of the month October, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_month6` | Demand model for local hour 10: coefficient of the month June, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_month7` | Demand model for local hour 10: coefficient of the month July, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_month8` | Demand model for local hour 10: coefficient of the month August, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_month9` | Demand model for local hour 10: coefficient of the month September, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_saturday` | Demand model for local hour 10: coefficient of a Saturday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_sunday` | Demand model for local hour 10: coefficient of a Sunday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_year2019` | Demand model for local hour 10: coefficient of the year 2019, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_year2020` | Demand model for local hour 10: coefficient of the year 2020, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_year2021` | Demand model for local hour 10: coefficient of the year 2021, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_year2022` | Demand model for local hour 10: coefficient of the year 2022, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_year2023` | Demand model for local hour 10: coefficient of the year 2023, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_year2024` | Demand model for local hour 10: coefficient of the year 2024, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h10_year2025` | Demand model for local hour 10: coefficient of the year 2025, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_cdh` | Demand model for local hour 11: coefficient of the cooling degree hour, max(T - 65 F, 0) of the weighted temperature in the hour (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_cdh2` | Demand model for local hour 11: coefficient of the cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_cdh_prev24` | Demand model for local hour 11: coefficient of the mean cooling degree hour over the 24 hours before (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_cdh_prev24_2` | Demand model for local hour 11: coefficient of the 24-hour mean cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_cdh_x_dew` | Demand model for local hour 11: coefficient of the cooling degree hour times the dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_dew_point` | Demand model for local hour 11: coefficient of the weighted dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_holiday` | Demand model for local hour 11: coefficient of a US federal holiday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_intercept` | Demand model for local hour 11: coefficient of the constant term (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_month10` | Demand model for local hour 11: coefficient of the month October, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_month6` | Demand model for local hour 11: coefficient of the month June, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_month7` | Demand model for local hour 11: coefficient of the month July, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_month8` | Demand model for local hour 11: coefficient of the month August, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_month9` | Demand model for local hour 11: coefficient of the month September, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_saturday` | Demand model for local hour 11: coefficient of a Saturday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_sunday` | Demand model for local hour 11: coefficient of a Sunday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_year2019` | Demand model for local hour 11: coefficient of the year 2019, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_year2020` | Demand model for local hour 11: coefficient of the year 2020, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_year2021` | Demand model for local hour 11: coefficient of the year 2021, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_year2022` | Demand model for local hour 11: coefficient of the year 2022, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_year2023` | Demand model for local hour 11: coefficient of the year 2023, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_year2024` | Demand model for local hour 11: coefficient of the year 2024, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h11_year2025` | Demand model for local hour 11: coefficient of the year 2025, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_cdh` | Demand model for local hour 12: coefficient of the cooling degree hour, max(T - 65 F, 0) of the weighted temperature in the hour (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_cdh2` | Demand model for local hour 12: coefficient of the cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_cdh_prev24` | Demand model for local hour 12: coefficient of the mean cooling degree hour over the 24 hours before (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_cdh_prev24_2` | Demand model for local hour 12: coefficient of the 24-hour mean cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_cdh_x_dew` | Demand model for local hour 12: coefficient of the cooling degree hour times the dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_dew_point` | Demand model for local hour 12: coefficient of the weighted dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_holiday` | Demand model for local hour 12: coefficient of a US federal holiday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_intercept` | Demand model for local hour 12: coefficient of the constant term (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_month10` | Demand model for local hour 12: coefficient of the month October, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_month6` | Demand model for local hour 12: coefficient of the month June, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_month7` | Demand model for local hour 12: coefficient of the month July, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_month8` | Demand model for local hour 12: coefficient of the month August, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_month9` | Demand model for local hour 12: coefficient of the month September, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_saturday` | Demand model for local hour 12: coefficient of a Saturday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_sunday` | Demand model for local hour 12: coefficient of a Sunday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_year2019` | Demand model for local hour 12: coefficient of the year 2019, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_year2020` | Demand model for local hour 12: coefficient of the year 2020, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_year2021` | Demand model for local hour 12: coefficient of the year 2021, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_year2022` | Demand model for local hour 12: coefficient of the year 2022, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_year2023` | Demand model for local hour 12: coefficient of the year 2023, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_year2024` | Demand model for local hour 12: coefficient of the year 2024, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h12_year2025` | Demand model for local hour 12: coefficient of the year 2025, against 2018 (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_cdh` | Demand model for local hour 13: coefficient of the cooling degree hour, max(T - 65 F, 0) of the weighted temperature in the hour (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_cdh2` | Demand model for local hour 13: coefficient of the cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_cdh_prev24` | Demand model for local hour 13: coefficient of the mean cooling degree hour over the 24 hours before (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_cdh_prev24_2` | Demand model for local hour 13: coefficient of the 24-hour mean cooling degree hour squared (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_cdh_x_dew` | Demand model for local hour 13: coefficient of the cooling degree hour times the dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_dew_point` | Demand model for local hour 13: coefficient of the weighted dew point (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_holiday` | Demand model for local hour 13: coefficient of a US federal holiday (1, else 0) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_intercept` | Demand model for local hour 13: coefficient of the constant term (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_month10` | Demand model for local hour 13: coefficient of the month October, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_month6` | Demand model for local hour 13: coefficient of the month June, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_month7` | Demand model for local hour 13: coefficient of the month July, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |
| `coef_h13_month8` | Demand model for local hour 13: coefficient of the month August, against May (the base) (MW per unit of the term; fitted on every non-alert day) | MW | 1 | 2018-07-01T00:00:00Z | 2018-07-01T00:00:00Z |

### `forecast_tool_parameters`

One parameter the forecast tool reads, for one technology and place: EIA's capital cost and case figures, JEDI's construction cost and taxable share, or the gas plant's fuel defaults.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 768.

- **Time:** ts_utc is 1 January of the value's dollar year where it has one, else 2026-01-01; no freq (a parameter, not a time series).
- **Revisions:** Rewritten whole by each run from the forecast tool's files (the old file removed first); vintage is not filled.
- **Source:** eia:capital_cost_aeo2025 U.S. Energy Information Administration (EIA), Capital Cost and Performance Characteristic Estimates for Utility Scale Electric Power Generating Technologies (AEO2025), Appendix A, https://www.eia.gov/analysis/studies/powerplants/capitalcost/pdf/capital_cost_AEO2025.pdf; nlr:jedi_models National Laboratory of the Rockies (NLR, formerly NREL), JEDI models (Jobs and Economic Development Impact), https://www.nlr.gov/analysis/jedi/models; erw:forecast_gas: the study's heat rate, JEDI's default capacity factor, eia_steo_forecasts' NGHHUUS and EIA's heat content (https://www.nlr.gov/analysis/jedi/models)
- **Method note:** [`docs/methods/forecast.md`](../methods/forecast.md)
- **Cite as:** Energy Research Warehouse (ERW); National Laboratory of the Rockies (NLR, formerly NREL); U.S. Energy Information Administration (EIA). Capital Cost and Performance Characteristic Estimates for Utility Scale Electric Power Generating Technologies (AEO2025), Appendix A; JEDI models (Jobs and Economic Development Impact); The forecast tool's gas fuel defaults (site/data/forecast/gas.json). Via the Energy Research Warehouse (ERW), table `forecast_tool_parameters`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: forecast:<file>:<technology>:<place>, file eia_capex, jedi_costs, jedi_taxable or gas; place us, a state code, or <state>_<city> | none | text | for example forecast:eia_capex:geothermal:ca, forecast:eia_capex:geothermal:ca_bakersfield, forecast:eia_capex:geothermal:ca_los_angeles; 559 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2025-01-01T00:00:00Z, 2026-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.605882 to 3756566.12; 311 distinct | 0 |
| `unit` | The unit of the row's value | none | text | Btu/ft3, MMBtu/MWh, MW, USD/MMBtu, USD/MW, USD/kW, month, ratio, year | 0 |
| `freq` | How long the interval of the row is. Here: Not filled: a parameter, not a time series | none | empty | no cell holds a value | 768 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, whatever the place (x_place names it) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 768 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 768 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | eia:capital_cost_aeo2025, erw:forecast_gas, nlr:jedi_models | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/forecast.md, https://www.eia.gov/analysis/studies/powerplants/capitalcost/pdf/capital_cost_AEO2025.pdf, https://www.nlr.gov/analysis/jedi/models | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-13T10:23:29Z, 2026-11-13T10:45:00Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 768 |
| `x_technology` | The generating technology: geothermal, land_based_wind, natural_gas or utility_pv | none | text | geothermal, land_based_wind, natural_gas, utility_pv | 0 |
| `x_place` | The place the value is for: us (the study's base case), a state's two-letter code, or <state>_<city> | none | text | for example ak, al, al_huntsville; 113 distinct | 0 |
| `x_dollar_year` | The dollar year of a money value (the study's 2023 dollars, a JEDI model's own year, 2025 for the gas price) | none | integer | 2010, 2017, 2023, 2025 | 212: The value is not money and has no dollar year |
| `x_detail` | Where the value was read: the study's table, case and basis, the city and state, or the JEDI file and cells with its arithmetic | none | text | for example 01d-jedi-geothermal-model-rel-gt12-23-16.xlsm (nameplate MW (the model's 10 MW net output)), ALABAMA: Summary Results!D7 45,928,513.17 USD over 12.2262 MW, 01d-jedi-geothermal-model-rel-gt12-23-16.xlsm (nameplate MW (the model's 10 MW net output)), ALASKA: Summary Results!D7 45,928,513.17 USD over 12.2262 MW, 01d-jedi-geothermal-model-rel-gt12-23-16.xlsm (nameplate MW (the model's 10 MW net output)), ARIZONA: Summary Results!D7 45,928,513.17 USD over 12.2262 MW; 328 distinct | 0 |

Variables (11):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity_factor` | The gas plant's capacity factor, JEDI's default | ratio | 1 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `case_mw` | The size of the study's case for the technology | MW | 4 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `construction_cost` | JEDI's default construction cost per MW of its default project, by technology and location, in the model's dollar year | USD/MW | 206 | 2010-01-01T00:00:00Z | 2017-01-01T00:00:00Z |
| `construction_months` | The study case's construction period | month | 4 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `fuel_price` | The gas price the tool uses: the 2025 mean of Henry Hub (eia_steo_forecasts' NGHHUUS) | USD/MMBtu | 1 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `heat_content` | Natural gas heat content, EIA's figure | Btu/ft3 | 1 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `heat_rate` | The plant's heat rate from the study (higher heating value), MMBtu per MWh | MMBtu/MWh | 2 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `location_variation` | The location variation the study's Appendix A (labor location-based cost adjustments) gives for the city | ratio | 193 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `operating_life` | The study case's operating life | year | 4 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `overnight_cost` | EIA's overnight capital cost (financing during construction excluded), per kW, in the study's dollar year | USD/kW | 349 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `taxable_share` | Share of construction spending that bears sales and use tax, JEDI's own taxable base | ratio | 3 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

### `friction_index_weekly`

One sector and place's value of one Friction Index measure (opposition in the news) in one week.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: model_extracted. Rows read on 2026-11-20: 4610.

- **Time:** ts_utc is the Monday 00:00Z of the week; weeks run Monday to Sunday, UTC; freq P1W.
- **Revisions:** Rewritten whole as one snapshot by each run of the index builder.
- **Method note:** [`docs/methods/attention.md`](../methods/attention.md)
- **Cite as:** Energy Research Warehouse (ERW). The Attention and Friction indices: coverage and opposition by week, sector and place, from the classified news stories (the ERW's own derivation). Via the Energy Research Warehouse (ERW), table `friction_index_weekly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: attention:<sector>:<geo>, the entities of attention_index_weekly | none | text | for example attention:datacenters:US, attention:datacenters:US-AL, attention:datacenters:US-AR; 184 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-10-05T00:00:00Z, 2026-10-12T00:00:00Z, 2026-10-19T00:00:00Z, 2026-10-26T00:00:00Z, 2026-11-02T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 100.0; 108 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US or US-<state> for those places; empty for the place all | none | text | for example US, US-AK, US-AL; 47 distinct | 400 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:attention | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/attention.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T09:24:19Z | 0 |

Variables (10):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `friction_index` | The cell's stories that report opposition, as a percent of the cell's stories | pct | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `kind_lawsuit` | The cell's stories whose main kind of opposition is a lawsuit or court challenge | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `kind_moratorium` | The cell's stories whose main kind of opposition is a moratorium or ban | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `kind_other_opposition` | The cell's stories whose main kind of opposition is another kind | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `kind_permit_denied` | The cell's stories whose main kind of opposition is a permit denied | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `kind_political_opposition` | The cell's stories whose main kind of opposition is political opposition | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `kind_protest` | The cell's stories whose main kind of opposition is a protest | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `kind_rate_case` | The cell's stories whose main kind of opposition is a rate-case fight | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `opposition_events` | Distinct news events behind the cell's opposition stories (a news cluster of the scorer counted once; a story clustered with none counts as its own) | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |
| `opposition_stories` | The cell's stories that report opposition (a moratorium or ban, a lawsuit, a protest, a permit denied, a rate-case fight, political or other opposition) | count | 461 | 2026-10-05T00:00:00Z | 2026-11-02T00:00:00Z |

### `gas_balance_weekly`

One EIA storage region's weekly working gas measure, or one monthly measure of the US natural gas balance.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 40507.

- **Time:** ts_utc is the storage report's week (freq P1W) or the first day of the month (freq P1M), at 00:00:00Z.
- **Revisions:** Rewritten whole as one snapshot by each run of the builder from the EIA source tables; vintage is not filled.
- **Source:** eia:natural-gas U.S. Energy Information Administration, Weekly Natural Gas Storage Report and Natural Gas Monthly
- **Method note:** [`docs/methods/gas_balance_weekly.md`](../methods/gas_balance_weekly.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The weekly gas storage balance and the monthly U.S. gas balance (docs/methods/gas_balance_weekly.md). Via the Energy Research Warehouse (ERW), table `gas_balance_weekly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: gas_storage:<EIA region> for the weekly rows, gas_balance:US for the monthly rows | none | text | gas_balance:US, gas_storage:east, gas_storage:lower48, gas_storage:midwest, gas_storage:mountain, gas_storage:nonsalt, gas_storage:pacific, gas_storage:salt, gas_storage:south_central | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z to 2026-10-16T00:00:00Z; 1154 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1047507.0 to 3921586.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf, bcf, pct | 0 |
| `freq` | How long the interval of the row is. Here: P1W for storage rows, P1M for balance rows | none | text | P1M, P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row, whatever the region | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 40507 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 40507 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:gas_balance_weekly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/gas_balance_weekly.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-06T08:28:34Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 40507 |
| `x_region` | EIA's storage region (east, midwest, south_central, mountain, pacific, salt, nonsalt, lower48), or US on the monthly balance rows | none | text | US, east, lower48, midwest, mountain, nonsalt, pacific, salt, south_central | 0 |

Variables (16):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `consumption` | US total natural gas consumption in the month | MMcf | 307 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `dry_production` | US dry natural gas production in the month | MMcf | 307 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `exports` | US natural gas exports in the month (pipeline to Canada and Mexico, and LNG) | MMcf | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `five_year_avg_bcf` | The average working gas of the same ISO week in the five years before (written only when all five are held) | bcf | 4912 | 2015-01-02T00:00:00Z | 2026-10-16T00:00:00Z |
| `five_year_max_bcf` | The highest working gas of the same ISO week in the five years before (written only when all five are held) | bcf | 4912 | 2015-01-02T00:00:00Z | 2026-10-16T00:00:00Z |
| `five_year_min_bcf` | The lowest working gas of the same ISO week in the five years before (written only when all five are held) | bcf | 4912 | 2015-01-02T00:00:00Z | 2026-10-16T00:00:00Z |
| `five_year_position_pct` | Working gas's place in the five-year range: 0 at the five-year low, 100 at the high | pct | 4912 | 2015-01-02T00:00:00Z | 2026-10-16T00:00:00Z |
| `implied_balance` | Dry production plus imports less consumption less exports: what went to storage, the losses and EIA's balancing item (written only when all four are held) | MMcf | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `imports` | US natural gas imports in the month (pipeline from Canada and Mexico, and LNG) | MMcf | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `lng_exports` | US LNG exports in the month | MMcf | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `lng_share_pct` | LNG exports as a percent of dry production | pct | 139 | 2015-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `net_change_bcf` | Working gas less the week exactly 7 days before | bcf | 7008 | 2010-01-08T00:00:00Z | 2026-10-16T00:00:00Z |
| `power_burn` | US natural gas consumed for electric power in the month | MMcf | 307 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `power_share_pct` | Power burn as a percent of consumption | pct | 307 | 2001-01-01T00:00:00Z | 2026-07-01T00:00:00Z |
| `vs_five_year_avg_bcf` | Working gas less the five-year average | bcf | 4912 | 2015-01-02T00:00:00Z | 2026-10-16T00:00:00Z |
| `working_gas_bcf` | Working gas in underground storage in the region at the report's week | bcf | 7016 | 2010-01-01T00:00:00Z | 2026-10-16T00:00:00Z |

### `generation_mix_hourly_profile`

One ISO grid's value of one energy-mix measure for one local month: an hour of the month's average day, a source's MWh or share, or a count of days.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 167573.

- **Time:** ts_utc is the first day of the grid's local month at 00:00:00Z; freq P1M; an hour HH is a local hour.
- **Revisions:** Rewritten whole by each run of mix_profile.py (the old file removed first); vintage is not filled.
- **Source:** erw:generation_mix_hourly EIA Form EIA-930 hourly net generation by energy source, the per-BA workbooks (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx); California from 2025-12-16T08:00:00Z is CAISO's own supply by fuel (caiso_fuel_supply; source erw:generation_mix_hourly_caiso), the warehouse's one join (docs/methods/eia930_caiso_break.md); read by this run from warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175834.883363Z_00002_CISO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175850.712544Z_00004_ERCO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175904.395449Z_00006_ISNE.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175918.956497Z_00008_MISO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175934.677962Z_00010_NYIS.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175949.986042Z_00012_PJM.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T180008.741327Z_00014_SWPP.xlsx (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx)
- **Method note:** [`docs/methods/generation_mix_hourly.md`](../methods/generation_mix_hourly.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The energy mix by hour: the average day of each month and the records, from EIA-930 (docs/methods/generation_mix_hourly.md); The same for California from 2025-12-16, from CAISO's own supply by fuel (docs/methods/eia930_caiso_break.md). Via the Energy Research Warehouse (ERW), table `generation_mix_hourly_profile`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: iso:<grid>, the seven ISO grids | none | text | iso:caiso, iso:ercot, iso:isone, iso:miso, iso:nyiso, iso:pjm, iso:spp | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-10-01T00:00:00Z; 94 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -243323.0 to 90489896.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-CA, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 167573 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 167573 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:generation_mix_hourly, erw:generation_mix_hourly_caiso | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/generation_mix_hourly.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T18:22:33Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 167573 |

Variables (259):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `avg_coal_mw_h00` | The month's average day: mean coal in local hour 00 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h01` | The month's average day: mean coal in local hour 01 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h02` | The month's average day: mean coal in local hour 02 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h03` | The month's average day: mean coal in local hour 03 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h04` | The month's average day: mean coal in local hour 04 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h05` | The month's average day: mean coal in local hour 05 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h06` | The month's average day: mean coal in local hour 06 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h07` | The month's average day: mean coal in local hour 07 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h08` | The month's average day: mean coal in local hour 08 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h09` | The month's average day: mean coal in local hour 09 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h10` | The month's average day: mean coal in local hour 10 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h11` | The month's average day: mean coal in local hour 11 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h12` | The month's average day: mean coal in local hour 12 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h13` | The month's average day: mean coal in local hour 13 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h14` | The month's average day: mean coal in local hour 14 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h15` | The month's average day: mean coal in local hour 15 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h16` | The month's average day: mean coal in local hour 16 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h17` | The month's average day: mean coal in local hour 17 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h18` | The month's average day: mean coal in local hour 18 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h19` | The month's average day: mean coal in local hour 19 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h20` | The month's average day: mean coal in local hour 20 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h21` | The month's average day: mean coal in local hour 21 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h22` | The month's average day: mean coal in local hour 22 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_coal_mw_h23` | The month's average day: mean coal in local hour 23 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h00` | The month's average day: mean demand in local hour 00 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h01` | The month's average day: mean demand in local hour 01 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h02` | The month's average day: mean demand in local hour 02 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h03` | The month's average day: mean demand in local hour 03 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h04` | The month's average day: mean demand in local hour 04 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h05` | The month's average day: mean demand in local hour 05 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h06` | The month's average day: mean demand in local hour 06 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h07` | The month's average day: mean demand in local hour 07 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h08` | The month's average day: mean demand in local hour 08 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h09` | The month's average day: mean demand in local hour 09 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h10` | The month's average day: mean demand in local hour 10 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h11` | The month's average day: mean demand in local hour 11 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h12` | The month's average day: mean demand in local hour 12 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h13` | The month's average day: mean demand in local hour 13 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h14` | The month's average day: mean demand in local hour 14 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h15` | The month's average day: mean demand in local hour 15 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h16` | The month's average day: mean demand in local hour 16 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h17` | The month's average day: mean demand in local hour 17 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h18` | The month's average day: mean demand in local hour 18 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h19` | The month's average day: mean demand in local hour 19 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h20` | The month's average day: mean demand in local hour 20 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h21` | The month's average day: mean demand in local hour 21 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h22` | The month's average day: mean demand in local hour 22 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h23` | The month's average day: mean demand in local hour 23 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h00` | The month's average day: mean hydro in local hour 00 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h01` | The month's average day: mean hydro in local hour 01 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h02` | The month's average day: mean hydro in local hour 02 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h03` | The month's average day: mean hydro in local hour 03 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h04` | The month's average day: mean hydro in local hour 04 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h05` | The month's average day: mean hydro in local hour 05 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h06` | The month's average day: mean hydro in local hour 06 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h07` | The month's average day: mean hydro in local hour 07 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h08` | The month's average day: mean hydro in local hour 08 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h09` | The month's average day: mean hydro in local hour 09 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h10` | The month's average day: mean hydro in local hour 10 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h11` | The month's average day: mean hydro in local hour 11 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h12` | The month's average day: mean hydro in local hour 12 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h13` | The month's average day: mean hydro in local hour 13 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h14` | The month's average day: mean hydro in local hour 14 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h15` | The month's average day: mean hydro in local hour 15 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h16` | The month's average day: mean hydro in local hour 16 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h17` | The month's average day: mean hydro in local hour 17 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h18` | The month's average day: mean hydro in local hour 18 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h19` | The month's average day: mean hydro in local hour 19 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h20` | The month's average day: mean hydro in local hour 20 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h21` | The month's average day: mean hydro in local hour 21 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h22` | The month's average day: mean hydro in local hour 22 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_hydro_mw_h23` | The month's average day: mean hydro in local hour 23 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h00` | The month's average day: mean natural gas in local hour 00 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h01` | The month's average day: mean natural gas in local hour 01 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h02` | The month's average day: mean natural gas in local hour 02 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h03` | The month's average day: mean natural gas in local hour 03 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h04` | The month's average day: mean natural gas in local hour 04 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h05` | The month's average day: mean natural gas in local hour 05 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h06` | The month's average day: mean natural gas in local hour 06 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h07` | The month's average day: mean natural gas in local hour 07 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h08` | The month's average day: mean natural gas in local hour 08 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h09` | The month's average day: mean natural gas in local hour 09 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h10` | The month's average day: mean natural gas in local hour 10 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h11` | The month's average day: mean natural gas in local hour 11 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h12` | The month's average day: mean natural gas in local hour 12 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h13` | The month's average day: mean natural gas in local hour 13 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h14` | The month's average day: mean natural gas in local hour 14 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h15` | The month's average day: mean natural gas in local hour 15 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h16` | The month's average day: mean natural gas in local hour 16 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h17` | The month's average day: mean natural gas in local hour 17 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h18` | The month's average day: mean natural gas in local hour 18 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h19` | The month's average day: mean natural gas in local hour 19 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h20` | The month's average day: mean natural gas in local hour 20 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h21` | The month's average day: mean natural gas in local hour 21 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h22` | The month's average day: mean natural gas in local hour 22 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_natural_gas_mw_h23` | The month's average day: mean natural gas in local hour 23 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h00` | The month's average day: mean net generation in local hour 00 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h01` | The month's average day: mean net generation in local hour 01 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h02` | The month's average day: mean net generation in local hour 02 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h03` | The month's average day: mean net generation in local hour 03 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h04` | The month's average day: mean net generation in local hour 04 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h05` | The month's average day: mean net generation in local hour 05 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h06` | The month's average day: mean net generation in local hour 06 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h07` | The month's average day: mean net generation in local hour 07 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h08` | The month's average day: mean net generation in local hour 08 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h09` | The month's average day: mean net generation in local hour 09 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h10` | The month's average day: mean net generation in local hour 10 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h11` | The month's average day: mean net generation in local hour 11 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h12` | The month's average day: mean net generation in local hour 12 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h13` | The month's average day: mean net generation in local hour 13 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h14` | The month's average day: mean net generation in local hour 14 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h15` | The month's average day: mean net generation in local hour 15 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h16` | The month's average day: mean net generation in local hour 16 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h17` | The month's average day: mean net generation in local hour 17 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h18` | The month's average day: mean net generation in local hour 18 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h19` | The month's average day: mean net generation in local hour 19 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h20` | The month's average day: mean net generation in local hour 20 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h21` | The month's average day: mean net generation in local hour 21 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h22` | The month's average day: mean net generation in local hour 22 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_generation_mw_h23` | The month's average day: mean net generation in local hour 23 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h00` | The month's average day: mean nuclear in local hour 00 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h01` | The month's average day: mean nuclear in local hour 01 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h02` | The month's average day: mean nuclear in local hour 02 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h03` | The month's average day: mean nuclear in local hour 03 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h04` | The month's average day: mean nuclear in local hour 04 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h05` | The month's average day: mean nuclear in local hour 05 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h06` | The month's average day: mean nuclear in local hour 06 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h07` | The month's average day: mean nuclear in local hour 07 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h08` | The month's average day: mean nuclear in local hour 08 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h09` | The month's average day: mean nuclear in local hour 09 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h10` | The month's average day: mean nuclear in local hour 10 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h11` | The month's average day: mean nuclear in local hour 11 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h12` | The month's average day: mean nuclear in local hour 12 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h13` | The month's average day: mean nuclear in local hour 13 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h14` | The month's average day: mean nuclear in local hour 14 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h15` | The month's average day: mean nuclear in local hour 15 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h16` | The month's average day: mean nuclear in local hour 16 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h17` | The month's average day: mean nuclear in local hour 17 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h18` | The month's average day: mean nuclear in local hour 18 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h19` | The month's average day: mean nuclear in local hour 19 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h20` | The month's average day: mean nuclear in local hour 20 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h21` | The month's average day: mean nuclear in local hour 21 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h22` | The month's average day: mean nuclear in local hour 22 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_nuclear_mw_h23` | The month's average day: mean nuclear in local hour 23 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h00` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 00 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h01` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 01 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h02` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 02 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h03` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 03 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h04` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 04 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h05` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 05 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h06` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 06 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h07` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 07 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h08` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 08 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h09` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 09 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h10` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 10 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h11` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 11 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h12` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 12 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h13` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 13 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h14` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 14 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h15` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 15 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h16` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 16 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h17` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 17 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h18` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 18 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h19` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 19 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h20` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 20 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h21` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 21 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h22` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 22 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_other_mw_h23` | The month's average day: mean other sources (oil, geothermal and unnamed) in local hour 23 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h00` | The month's average day: mean solar in local hour 00 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h01` | The month's average day: mean solar in local hour 01 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h02` | The month's average day: mean solar in local hour 02 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h03` | The month's average day: mean solar in local hour 03 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h04` | The month's average day: mean solar in local hour 04 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h05` | The month's average day: mean solar in local hour 05 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h06` | The month's average day: mean solar in local hour 06 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h07` | The month's average day: mean solar in local hour 07 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h08` | The month's average day: mean solar in local hour 08 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h09` | The month's average day: mean solar in local hour 09 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h10` | The month's average day: mean solar in local hour 10 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h11` | The month's average day: mean solar in local hour 11 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h12` | The month's average day: mean solar in local hour 12 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h13` | The month's average day: mean solar in local hour 13 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h14` | The month's average day: mean solar in local hour 14 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h15` | The month's average day: mean solar in local hour 15 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h16` | The month's average day: mean solar in local hour 16 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h17` | The month's average day: mean solar in local hour 17 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h18` | The month's average day: mean solar in local hour 18 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h19` | The month's average day: mean solar in local hour 19 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h20` | The month's average day: mean solar in local hour 20 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h21` | The month's average day: mean solar in local hour 21 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h22` | The month's average day: mean solar in local hour 22 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h23` | The month's average day: mean solar in local hour 23 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h00` | The month's average day: mean storage (negative when charging) in local hour 00 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h01` | The month's average day: mean storage (negative when charging) in local hour 01 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h02` | The month's average day: mean storage (negative when charging) in local hour 02 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h03` | The month's average day: mean storage (negative when charging) in local hour 03 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h04` | The month's average day: mean storage (negative when charging) in local hour 04 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h05` | The month's average day: mean storage (negative when charging) in local hour 05 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h06` | The month's average day: mean storage (negative when charging) in local hour 06 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h07` | The month's average day: mean storage (negative when charging) in local hour 07 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h08` | The month's average day: mean storage (negative when charging) in local hour 08 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h09` | The month's average day: mean storage (negative when charging) in local hour 09 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h10` | The month's average day: mean storage (negative when charging) in local hour 10 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h11` | The month's average day: mean storage (negative when charging) in local hour 11 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h12` | The month's average day: mean storage (negative when charging) in local hour 12 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h13` | The month's average day: mean storage (negative when charging) in local hour 13 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h14` | The month's average day: mean storage (negative when charging) in local hour 14 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h15` | The month's average day: mean storage (negative when charging) in local hour 15 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h16` | The month's average day: mean storage (negative when charging) in local hour 16 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h17` | The month's average day: mean storage (negative when charging) in local hour 17 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h18` | The month's average day: mean storage (negative when charging) in local hour 18 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h19` | The month's average day: mean storage (negative when charging) in local hour 19 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h20` | The month's average day: mean storage (negative when charging) in local hour 20 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h21` | The month's average day: mean storage (negative when charging) in local hour 21 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h22` | The month's average day: mean storage (negative when charging) in local hour 22 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_storage_mw_h23` | The month's average day: mean storage (negative when charging) in local hour 23 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h00` | The month's average day: mean wind in local hour 00 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h01` | The month's average day: mean wind in local hour 01 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h02` | The month's average day: mean wind in local hour 02 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h03` | The month's average day: mean wind in local hour 03 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h04` | The month's average day: mean wind in local hour 04 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h05` | The month's average day: mean wind in local hour 05 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h06` | The month's average day: mean wind in local hour 06 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h07` | The month's average day: mean wind in local hour 07 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h08` | The month's average day: mean wind in local hour 08 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h09` | The month's average day: mean wind in local hour 09 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h10` | The month's average day: mean wind in local hour 10 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h11` | The month's average day: mean wind in local hour 11 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h12` | The month's average day: mean wind in local hour 12 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h13` | The month's average day: mean wind in local hour 13 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h14` | The month's average day: mean wind in local hour 14 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h15` | The month's average day: mean wind in local hour 15 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h16` | The month's average day: mean wind in local hour 16 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h17` | The month's average day: mean wind in local hour 17 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h18` | The month's average day: mean wind in local hour 18 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h19` | The month's average day: mean wind in local hour 19 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h20` | The month's average day: mean wind in local hour 20 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h21` | The month's average day: mean wind in local hour 21 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h22` | The month's average day: mean wind in local hour 22 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h23` | The month's average day: mean wind in local hour 23 over the complete days | MW | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `coal_mwh` | Output of coal over the month's complete days | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `coal_share_pct` | Share of coal in the sum of the sources over the month's complete days | pct | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `days_held` | The month's complete days (every hour of the local day held), the days every figure is over | count | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `days_in_month` | The days of the month | count | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `hydro_mwh` | Output of hydro over the month's complete days | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `hydro_share_pct` | Share of hydro in the sum of the sources over the month's complete days | pct | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `natural_gas_mwh` | Output of natural gas over the month's complete days | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `natural_gas_share_pct` | Share of natural gas in the sum of the sources over the month's complete days | pct | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `net_generation_mwh` | Net generation over the month's complete days | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `nuclear_mwh` | Output of nuclear over the month's complete days | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `nuclear_share_pct` | Share of nuclear in the sum of the sources over the month's complete days | pct | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `other_mwh` | Output of other sources (oil, geothermal and unnamed) over the month's complete days | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `other_share_pct` | Share of other sources (oil, geothermal and unnamed) in the sum of the sources over the month's complete days | pct | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_mwh` | Output of solar over the month's complete days | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_share_pct` | Share of solar in the sum of the sources over the month's complete days | pct | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `storage_mwh` | Output of storage (negative when charging) over the month's complete days | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `storage_share_pct` | Share of storage (negative when charging) in the sum of the sources over the month's complete days | pct | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_mwh` | Output of wind over the month's complete days | MWh | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_share_pct` | Share of wind in the sum of the sources over the month's complete days | pct | 647 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |

### `generation_mix_records`

One ISO grid's record of the energy mix (highest solar or wind share of an hour, cleanest or dirtiest hour) over the whole history or one local year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 306.

- **Time:** ts_utc is the hour of the record (its start, UTC); freq PT1H; x_period says whether the record is of the whole history or of a local year.
- **Revisions:** Rewritten whole by each run of mix_profile.py; key (entity, variable, x_period); vintage is not filled.
- **Source:** erw:generation_mix_hourly EIA Form EIA-930 hourly net generation by energy source, the per-BA workbooks (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx); California from 2025-12-16T08:00:00Z is CAISO's own supply by fuel (caiso_fuel_supply; source erw:generation_mix_hourly_caiso), the warehouse's one join (docs/methods/eia930_caiso_break.md); read by this run from warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175834.883363Z_00002_CISO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175850.712544Z_00004_ERCO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175904.395449Z_00006_ISNE.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175918.956497Z_00008_MISO.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175934.677962Z_00010_NYIS.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T175949.986042Z_00012_PJM.xlsx; warehouse/raw/eia930_emissions/20261116T175833Z/20261116T180008.741327Z_00014_SWPP.xlsx (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx)
- **Method note:** [`docs/methods/generation_mix_hourly.md`](../methods/generation_mix_hourly.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The energy mix by hour: the average day of each month and the records, from EIA-930 (docs/methods/generation_mix_hourly.md); The same for California from 2025-12-16, from CAISO's own supply by fuel (docs/methods/eia930_caiso_break.md). Via the Energy Research Warehouse (ERW), table `generation_mix_records`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: iso:<grid>, the seven ISO grids | none | text | iso:caiso, iso:ercot, iso:isone, iso:miso, iso:nyiso, iso:pjm, iso:spp | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-14T05:00:00Z to 2026-10-31T06:00:00Z; 233 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.59 to 766.49; 249 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kgCO2/MWh, pct | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-CA, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 306 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 306 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:generation_mix_hourly, erw:generation_mix_hourly_caiso | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/generation_mix_hourly.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T18:22:33Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 306 |
| `x_period` | The span the record is over: all (the whole history from 2019) or a local year | none | text | 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, all | 0 |
| `x_side` | The source of the record's hour: eia930 (EIA-930) or caiso (CAISO's own supply by fuel) | none | text | caiso, eia930 | 0 |

Variables (10):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `cleanest_hour_kgco2_per_mwh` | The lowest carbon intensity of generation of any held hour (carbon_intensity_hourly's intensity_generation), whole history | kgCO2/MWh | 7 | 2019-05-07T05:00:00Z | 2026-10-18T16:00:00Z |
| `dirtiest_hour_kgco2_per_mwh` | The highest carbon intensity of generation of any held hour, whole history | kgCO2/MWh | 7 | 2019-01-17T04:00:00Z | 2026-01-26T02:00:00Z |
| `solar_share_max_pct` | The highest share of an hour's generation from solar, whole history | pct | 6 | 2026-04-26T18:00:00Z | 2026-10-17T20:00:00Z |
| `wind_share_max_pct` | The highest share of an hour's generation from wind, whole history | pct | 7 | 2021-05-08T09:00:00Z | 2026-10-31T06:00:00Z |
| `wind_solar_share_max_pct` | The highest share of an hour's generation from wind and solar together, whole history | pct | 7 | 2021-05-08T09:00:00Z | 2026-10-18T15:00:00Z |
| `year_cleanest_hour_kgco2_per_mwh` | The lowest carbon intensity of generation of any held hour of the local year | kgCO2/MWh | 56 | 2019-05-07T05:00:00Z | 2026-10-18T18:00:00Z |
| `year_dirtiest_hour_kgco2_per_mwh` | The highest carbon intensity of generation of any held hour of the local year | kgCO2/MWh | 56 | 2019-01-14T05:00:00Z | 2026-10-04T07:00:00Z |
| `year_solar_share_max_pct` | The highest share of an hour's generation from solar in the local year | pct | 48 | 2019-04-14T21:00:00Z | 2026-10-17T20:00:00Z |
| `year_wind_share_max_pct` | The highest share of an hour's generation from wind in the local year | pct | 56 | 2019-03-15T06:00:00Z | 2026-10-31T06:00:00Z |
| `year_wind_solar_share_max_pct` | The highest share of an hour's generation from wind and solar together in the local year | pct | 56 | 2019-03-15T06:00:00Z | 2026-10-18T15:00:00Z |

### `generator_pipeline_by_grid`

One cell of EIA-860M's planned generators (balancing authority, state, energy source, status, planned year) in one snapshot month, or one balancing authority's (or the US's) move of planned generators between two months.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 5147.

- **Time:** ts_utc is the first day of the snapshot month (for a move, the later month) at 00:00:00Z; freq P1M.
- **Revisions:** Rewritten whole as one snapshot by each run of the builder; it holds the snapshot months the machine keeps; vintage is the snapshot month (YYYY-MM).
- **Source:** eia:860m U.S. Energy Information Administration, EIA-860M Monthly Update to the Annual Electric Generator Report
- **Method note:** [`docs/methods/generator_pipeline_by_grid.md`](../methods/generator_pipeline_by_grid.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. EIA-860M's generator pipeline by grid and its monthly moves (docs/methods/generator_pipeline_by_grid.md). Via the Energy Research Warehouse (ERW), table `generator_pipeline_by_grid`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia860m_pipeline:<BA>:<state>:<energy source>:<status>:<planned year> for a cell; eia860m_pipeline:<BA> or eia860m_pipeline:US for a move | none | text | for example eia860m_pipeline:AECI:MO:NG:U:2027, eia860m_pipeline:AECI:MO:WND:P:2029, eia860m_pipeline:AECI:OK:NG:V:2027; 924 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-08-01T00:00:00Z, 2026-09-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 8832.0; 598 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> on a cell, US on a move row or where the state is not a two-letter code | none | text | for example US, US-AK, US-AL; 53 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5147 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5147 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:generator_pipeline_by_grid | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.eia.gov/electricity/data/eia860m/ | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-06T08:20:13Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The EIA-860M snapshot month (YYYY-MM) | none | text | 2026-08, 2026-09 | 0 |
| `x_ba` | The balancing authority of the generators' plants, EIA code (none where EIA gives none); US on the national move rows (the source's name: Balancing Authority Code) | none | text | for example AECI, AVA, AVRN; 50 distinct | 0 |
| `x_state` | The plants' state, two-letter code (the source's name: Plant State) | none | text | for example AK, AL, AR; 52 distinct | 134: Empty on the move rows |
| `x_energy_source` | EIA's energy source code of the generators (NG natural gas, SUN solar, WND wind, MWH battery storage, NUC nuclear and others) (the source's name: Energy Source Code) | none | text | AB, DFO, GEO, H2, LFG, MSW, MWH, NG, NUC, OBG, OBL, OBS, OTH, SUN, WAT, WH, WND | 134: Empty on the move rows |
| `x_status` | EIA's planned status code: P planned, regulatory approvals not started; L approvals pending; T approvals received, not under construction; U under construction, half or less complete; V under construction, more than half complete; TS construction complete, not yet operating (the source's name: Status) | none | text | L, P, T, TS, U, V | 134: Empty on the move rows |
| `x_planned_year` | The generators' planned operation year (the source's name: Planned Operation Year) | none | integer | 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2039 | 134: Empty on the move rows |
| `x_from_vintage` | The earlier snapshot month a move is measured from (YYYY-MM) | none | text | 2026-08 | 5013: Empty on the cell rows |

Variables (13):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `datacenter_mw` | The MW of the cell's generators whose plant or owner name names a datacenter or a lab | MW | 1671 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `entered_count` | Generators planned now and in neither list the month before | count | 14 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `entered_mw` | MW of generators planned now and in neither list the month before | MW | 14 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `left_count` | Generators planned the month before and in neither list now | count | 5 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `left_mw` | MW (the earlier month's) of generators planned the month before and in neither list now (cancelled, postponed or withdrawn, not told apart) | MW | 5 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `online_count` | Generators planned the month before and operating now | count | 18 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `online_mw` | MW (the earlier month's) of generators planned the month before and operating now | MW | 18 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `planned_count` | The cell's generators | count | 1671 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `planned_mw` | The cell's nameplate capacity as EIA gives it | MW | 1671 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `slipped_count` | Generators planned in both months whose planned year is later now | count | 12 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `slipped_mw` | MW of generators planned in both months whose planned year is later now | MW | 12 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `status_moved_count` | Generators planned in both months whose EIA status code changed | count | 18 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `status_moved_mw` | MW of generators planned in both months whose EIA status code changed | MW | 18 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `hub_price_comparison`

One public hub or zone's value of one price measure, day-ahead or real time, over the last twelve months (freq P1Y) or the last whole month (P1M), or its grid's carbon intensity over the same window.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 880.

- **Time:** ts_utc is the window's first day in the grid's local time; P1Y the twelve months from it, P1M its month.
- **Revisions:** Rewritten whole by each run (the windows move with the last whole month); vintage is not filled.
- **Source:** erw:hub_price_comparison from each grid operator's public price reports (CAISO OASIS; ERCOT NP4-180-ER, NP4-190-CD, NP6-785-ER, NP6-905-CD; ISO-NE hourly and five-minute LMPs; NYISO zonal LBMPs; SPP LMP by settlement location) and from EIA-930 emissions
- **Method note:** [`docs/methods/hub_price_comparison.md`](../methods/hub_price_comparison.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Where power is cheap: hub and zone prices compared (docs/methods/hub_price_comparison.md). Via the Energy Research Warehouse (ERW), table `hub_price_comparison`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: <iso>:<node>, every public hub and zone price held (MISO and PJM not included) | none | text | for example caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, caiso:TH_ZP26_GEN-APND; 39 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-11-01T00:00:00Z, 2026-10-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 8760.0; 375 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count, kgCO2/MWh, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M, P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: the market is in the variable's prefix (dam or rtm) | none | empty | no cell holds a value | 880 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example .H.INTERNAL_HUB, .Z.CONNECTICUT, .Z.MAINE; 39 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:hub_price_comparison | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/hub_price_comparison.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-17T07:41:45Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 880 |

Variables (18):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dam_above_200_hours_share_pct` | Day-ahead: share of the window's hours with a price above USD 200 per MWh | pct | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_avg_price` | Day-ahead: mean of the window's hourly prices | USD/MWh | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_daily_spread_days` | Day-ahead: the whole local days behind the mean daily spread | count | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_daily_spread_mean_top4_bottom4` | Day-ahead: mean over the window's whole local days of each day's four dearest hours less its four cheapest | USD/MWh | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_day_spread_top4_bottom4` | Day-ahead: on the window's average day, the mean of its four dearest hours less the mean of its four cheapest | USD/MWh | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_hours_held` | Day-ahead: hours of the window with a price held | count | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_hours_in_window` | Day-ahead: hours in the window | count | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_negative_hours_share_pct` | Day-ahead: share of the window's hours with a price below zero | pct | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `grid_carbon_days_held` | Days of the window with the grid's daily carbon intensity held | count | 58 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `grid_carbon_intensity` | Mean of the grid's daily carbon intensities of generation held in the window | kgCO2/MWh | 54 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_above_200_hours_share_pct` | Real time: share of the window's hours with a price above USD 200 per MWh | pct | 38 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_avg_price` | Real time: mean of the window's hourly prices | USD/MWh | 38 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_daily_spread_days` | Real time: the whole local days behind the mean daily spread | count | 38 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_daily_spread_mean_top4_bottom4` | Real time: mean over the window's whole local days of each day's four dearest hours less its four cheapest | USD/MWh | 38 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_day_spread_top4_bottom4` | Real time: on the window's average day, the mean of its four dearest hours less the mean of its four cheapest | USD/MWh | 38 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_hours_held` | Real time: hours of the window with a price held | count | 38 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_hours_in_window` | Real time: hours in the window | count | 38 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_negative_hours_share_pct` | Real time: share of the window's hours with a price below zero | pct | 38 | 2025-11-01T00:00:00Z | 2026-10-01T00:00:00Z |

### `known_data_faults`

One known fault in a source's data, as the ERW's register of faults records it.

Shape: events. Keys: `event_id`. License: public; tier: derived. Rows read on 2026-11-20: 30.

- **Time:** event_date is the fault's first day where a day is recorded, else the day the register recorded it (x_first is then empty).
- **Revisions:** Rewritten whole from the register (warehouse/faults/faults.yaml) by each run: an entry taken out of the register leaves the table.
- **Source:** erw:known_data_faults the ERW's register of faults found in its sources' data (warehouse/faults/faults.yaml), each entry naming where it is recorded
- **Method note:** [`docs/methods/known_data_faults.md`](../methods/known_data_faults.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Known faults in source data: the register of what each publisher's data holds that is wrong, missing, shifted or impossible (docs/methods/known_data_faults.md). Via the Energy Research Warehouse (ERW), table `known_data_faults`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: data_fault:<the register's id of the fault> | none | text | for example data_fault:caiso_curtailment_reason_blank, data_fault:caiso_curtailment_workbooks_overlap, data_fault:caiso_oasis_autumn_clock_day; 30 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2018-07-20, 2019-01-01, 2019-02-13, 2019-02-26, 2019-04-18, 2019-10-01, 2019-12-11, 2019-12-12, 2020-01-01, 2020-04-10, 2021-02-01, 2022-01-01, 2023-08-10, 2023-11-01, 2024-07-19, 2024-10-23, 2024-11-03, 2025-01-01, 2025-08-27, 2025-11-02, 2025-12-06, 2025-12-16, 2026-01-21, 2026-03-08, 2026-11-16 | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: data_fault on every row | none | text | data_fault | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: The publisher whose data holds the fault | none | text | California ISO (CAISO), Electric Reliability Council of Texas (ERCOT), Large Load Interconnection Status Update, Federal Energy Regulatory Commission (FERC), Electric Quarterly Reports, ISO New England; New York ISO, Lawrence Berkeley National Laboratory and GridTracker, Queued Up 2026 Edition, U.S. Energy Information Administration (EIA), Form EIA-930, U.S. Energy Information Administration (EIA), Forms EIA-930 and EIA-860M | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons. Here: The ERW tables the fault touches, joined by ';' (table names, not entity_id values) | none | text | for example ba_supply_monthly, caiso_curtailment_intervals, caiso_curtailment_intervals;caiso_curtailment_daily; 26 distinct | 1 |
| `mw` | The capacity involved, in megawatts. Here: Not filled: no cell holds a value | MW | empty | no cell holds a value | 30 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise. Here: Not filled: no cell holds a value | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 30 |
| `currency` | The currency of the price, as an ISO 4217 code (USD). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 30 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: What the ERW does with the fault: screened (left out by a stated rule), corrected (read as it should have been), worked_around (another source read for the period) or held_as_published | none | text | corrected, held_as_published, screened, worked_around | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:known_data_faults | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/known_data_faults.md | 0 |
| `x_title` | The fault in one sentence, the register's title (the source's name: title) | none | text | for example 24 hours of demand in the Winter Storm Uri window have no number at the source, A contract rate in FERC's quarterly reports that cannot be a monthly price, Berkeley Lab's queue file: missing years, statuses and operation dates; 30 distinct | 0 |
| `x_first` | The fault's first day, where recorded (the source's name: first) | none | date | 2018-07-20, 2019-01-01, 2019-02-13, 2019-02-26, 2019-04-18, 2019-10-01, 2019-12-11, 2019-12-12, 2020-01-01, 2020-04-10, 2021-02-01, 2022-01-01, 2023-08-10, 2023-11-01, 2024-07-19, 2024-10-23, 2024-11-03, 2025-01-01, 2025-08-27, 2025-11-02, 2025-12-06, 2025-12-16, 2026-01-21, 2026-03-08 | 6: No first day is recorded; x_dates_note says what is known |
| `x_last` | The fault's last day, where recorded | none | date | 2019-03-31, 2020-07-13, 2020-08-24, 2021-02-28, 2022-12-31, 2023-06-13, 2024-11-21, 2024-12-31, 2025-05-31, 2025-06-21, 2025-08-27, 2025-11-02, 2025-12-02, 2025-12-14, 2025-12-31, 2026-01-25, 2026-02-10, 2026-03-08, 2026-03-26, 2026-08-20, 2026-08-29, 2026-09-22, 2026-09-30 | 7: No last day is recorded |
| `x_dates_note` | What the register knows of the fault's dates, in words (the source's name: dates_note) | none | text | for example 38 hours not used; most from 13 February to 10 May 2019, then 19 to 22 December 2019, 8 October 2020, 31 July 2025 and 25 January 2026, 63 held hours by the rule: California 41, New York 13, PJM 6, New England 2, SPP 1 (measured in session 118 on the workbooks retrieved 2026-10-04), 7,869 hours in a row, from the hour starting 2019-10-01T21:00Z to the hour starting 2020-08-24T17:00Z, both included (measured in session 118 on the workbook retrieved 2026-10-04); 30 distinct | 0 |
| `x_publisher_source` | The publisher's report or product that holds the fault, as organization:report_id (the source's name: source) | none | text | caiso:PRC_LMP, caiso:daily_renewable_report, caiso:production_curtailments, caiso:todays_outlook_fuelsource, eia930:daily_interchange, eia:860m, eia:electricity/rto/region-data, eia:gridmonitor/knownissues/xls, ercot:large_load_status_update, ferc:eqr, isone:rt_lmp_hourly_final, lbnl:queued_up | 0 |
| `x_evidence` | What was measured, in the words of the session that measured it (the source's name: evidence) | none | text | for example 1,505 MW at 2025-06-21T09:00Z (04:00 Central), the hours around it 34,479; and 24,991 MW at 2024-07-19T04:00Z, the hours around it 35,083. 48 more hours are blank., 24 hours of demand in the Uri window had no number at the source and were not written (session 68)., 525,129 MW at 2020-04-10T03:00Z, the hours around it 380,115: the rule leaves that hour out. PJM's 224,345 MW of 2020-07-13T22:00Z is inside the Lower 48's 776,575 MW of the same hour, which stands only 12 percent above the hours around it and passes the rule.; 30 distinct | 0 |
| `x_erw_does` | What the ERW does about the fault (the source's name: erw_does) | none | text | for example A blank reason is kept blank ("local or system" is not guessed). The reason reaches back to 2022 in the interval table., A day that is not whole is not written; March, August and September 2026 then have no monthly figure for California. Nothing is filled., A day with a missing interval is not written. A twelve-month figure is written only when 95 percent of its hours are held, so ISO-NE's real-time figure in hub_price_comparison is not written.; 30 distinct | 0 |
| `x_open` | What remains open or unknown about the fault (the source's name: open) | none | text | A faulty hour inside the sum cannot be screened from the sum., A rule to fill a single missing interval was recommended in session 65 and not applied., EIA does not say why its California demand of early 2019 is low; CAISO's own load is the comparison, not a correction applied., EIA does not say why the column changed, nor whether the earlier rows will be published again as net output., Not applied in cost_of_power_monthly, which weighs SPP's price of June 2025 by that hour's 1,505 MW, nor in the other tables a live page reads., Not applied in the tables a live page reads (ba_supply_monthly, the cost of power tables, ai_power_regions) nor in the source table eia930_all_emissions, which holds EIA's hours as published. The Lower 48's demand is EIA's sum, with PJM's faulty hours inside it., Not applied in the tables a live page reads, nor in the source table, as for PJM., Not explained., The cause is not recorded., The energy mix tables test an hour another way (its sources must add up to its total), and are not put to this rule for generation: whether they should be is a ruling to make., The held carbon build is not yet the table: carbon_intensity_hourly, _daily and _monthly still carry those hours as EIA published them, so California's intensity there is computed without hydro until a person approves the build. eia930_all_generation is the source table and keeps them., The live /network page's hourly links are not screened: rule C is a rule for days. Settled in session 118: the supply table's count (2,732) and the replay's (1,072) count different things. The first is every report of every pair, both sides; 1,259 of them are between authorities the network draws, on 1,252 pair-days; the replay uses one report a pair and day and counts a day only when the report it used is left out., The looser test is a session's choice, not yet ruled on. PJM's residual since May 2025 is flagged as unexplained (session 73)., The two clock-change days are a limit of the ERW's conversion, not of CAISO's file., What the generation EIA stopped counting is, is not settled by these data. EIA's known-issues page refused a plain request (HTTP 403), so EIA's own account of the change was not read., Whether the 13 March figures were for part of the month is not said in either report., Whether the ERW's extract should read EIA's Adjusted columns in place of the unadjusted ones is a ruling to make: EIA has already replaced these values there, with its own imputation, which is a fill the ERW would then inherit., Which of the two forms is off (output or the inventory's MW) is not known., Which of the two is misstated is not known., Why is not known. Not corrected: eia930_all_emissions, the carbon intensity tables, ba_supply_monthly, ai_power_regions and event_window_daily hold the hours as EIA stamped them. From July 2018 to mid June 2022 the same measure sits about half an hour early; that is seen and not corrected., caiso_curtailment_daily uses the reason only from 2024., eia930_all_generation holds those hours as published. | 7: The register records nothing open |
| `x_recorded_in` | Where the fault is recorded: the session and the method note or file (the source's name: recorded_in) | none | text | session 106; docs/methods/ercot_large_load_status.md, session 118; docs/methods/impossible_hours.md, session 68, session 7019 (chain 301); docs/methods/shoulder_hours.md; docs/state/data_requests_done_line.md, row 6, session 7022 (chain 301); docs/methods/demand_growth.md; docs/state/data_requests_done_line.md, row 38, session 72, session 73, session 73; docs/methods/eia930_caiso_break.md, session 81, session 94, session 94; docs/methods/generation_mix_hourly.md, session 95; docs/methods/interconnection_queue_summary.md, session 97; docs/methods/demand_growth.md, session 97; docs/methods/demand_growth.md; measured again by the rule on 2026-10-04, session 97; docs/methods/demand_growth.md; the dates measured by the rule on 2026-10-04, session 98, session 98; docs/methods/caiso_curtailment_intervals.md, sessions 49 and 64, sessions 49, 64, 65 and 96, sessions 62, 68 and 93; docs/methods/grid_network.md, sessions 62, 68 and 96, sessions 73 and 82; docs/methods/eia930_caiso_break.md, sessions 73 and 94, sessions 80 and 82; docs/methods/eia930_caiso_break.md | 0 |
| `x_resolution` | Where the fault stands: fixed, held_for_approval (the fix is built and waits for a person because it moves a number on a live page) or open (the source's name: resolution) | none | text | fixed, held_for_approval, open | 0 |
| `x_resolution_reason` | Why the fault stands as x_resolution says, in words (the source's name: resolution_reason) | none | text | for example A day with a missing interval is not written. Session 65 recommended filling a single missing interval; the ERW's rule is to fill nothing, so it was not applied. Open for a ruling: the cost is ISO-NE's real-time twelve-month figure, which is not written., A faulty hour of one balancing authority cannot be taken out of EIA's sum. The rule leaves out the one hour of the sum that fails it (2020-04-10T03:00Z), and the Lower 48 is given no peak. The Lower 48's consumed intensity of April 2020 goes with the held carbon build. It stays open until EIA republishes the hours or the ERW builds its own sum from the screened authorities, which no session has been asked to do., A gap at the source: there is nothing for the ERW to fix, and nothing is filled. Each figure says how many days it rests on. Open because EIA has not been asked why SPP's days are missing, and a figure for SPP that rests on 200 of 365 days is a weak one however plainly it says so.; 30 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T20:49:30Z | 0 |

### `merchant_revenue_monthly`

One ISO main hub's value of one merchant revenue measure for one asset type (solar, wind, a 2-hour or 4-hour battery, a gas peaker) and one month, or the month's flat price and hours.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 8853.

- **Time:** ts_utc is the first day of the hub's local month at 00:00:00Z; freq P1M.
- **Revisions:** Rewritten whole by each run (the old file removed first); vintage is not filled; partition column ba.
- **Source:** erw:merchant_revenue ERW derived table, the seller's side of the cost of power (docs/methods/cost_of_power.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/cost_of_power.md)
- **Method note:** [`docs/methods/cost_of_power.md`](../methods/cost_of_power.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Merchant revenue per MW by ISO hub, asset and month (docs/methods/cost_of_power.md). Via the Energy Research Warehouse (ERW), table `merchant_revenue_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: <iso>:<hub>, each ISO's main hub (ercot:HB_HUBAVG, caiso:TH_SP15_GEN-APND, isone:.H.INTERNAL_HUB, miso:INDIANA.HUB, nyiso:N.Y.C., spp:SPPNORTH_HUB) | none | text | caiso:TH_SP15_GEN-APND, ercot:HB_HUBAVG, isone:.H.INTERNAL_HUB, miso:INDIANA.HUB, nyiso:N.Y.C., spp:SPPNORTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-06-01T00:00:00Z to 2026-10-01T00:00:00Z; 101 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -4275.8263 to 1017690.3025; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh/MW, USD/MW, USD/MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-IN, US-KS,US-NE,US-OK, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: <iso>_rtm on every row: real-time prices only | none | text | caiso_rtm, ercot_rtm, isone_rtm, miso_rtm, nyiso_rtm, spp_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | .H.INTERNAL_HUB, HB_HUBAVG, INDIANA.HUB, N.Y.C., SPPNORTH_HUB, TH_SP15_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:merchant_revenue | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/cost_of_power.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-19T22:20:44Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 8853 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48) | none | text | ciso, erco, isne, miso, nyis, swpp | 0 |

Variables (37):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `battery_2h_capture_price` | A 2-hour battery (perfect-foresight upper bound): capture price, sales over energy delivered | USD/MWh | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_2h_capture_rate` | A 2-hour battery (perfect-foresight upper bound): capture price over flat price, percent | pct | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_2h_energy_per_mw` | A 2-hour battery (perfect-foresight upper bound): energy delivered per MW in the month | MWh/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_2h_flat_price` | A 2-hour battery (perfect-foresight upper bound): mean real-time price over the hours the asset used | USD/MWh | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_2h_hours` | A 2-hour battery (perfect-foresight upper bound): priced hours used (for batteries, the days) | count | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_2h_revenue_per_mw` | A 2-hour battery (perfect-foresight upper bound): merchant revenue per MW in the month: sales less purchases (batteries) or less fuel and variable O&M (peaker) | USD/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_2h_sales_per_mw` | A 2-hour battery (perfect-foresight upper bound): sales per MW in the month at the real-time hub price | USD/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_4h_capture_price` | A 4-hour battery (perfect-foresight upper bound): capture price, sales over energy delivered | USD/MWh | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_4h_capture_rate` | A 4-hour battery (perfect-foresight upper bound): capture price over flat price, percent | pct | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_4h_energy_per_mw` | A 4-hour battery (perfect-foresight upper bound): energy delivered per MW in the month | MWh/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_4h_flat_price` | A 4-hour battery (perfect-foresight upper bound): mean real-time price over the hours the asset used | USD/MWh | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_4h_hours` | A 4-hour battery (perfect-foresight upper bound): priced hours used (for batteries, the days) | count | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_4h_revenue_per_mw` | A 4-hour battery (perfect-foresight upper bound): merchant revenue per MW in the month: sales less purchases (batteries) or less fuel and variable O&M (peaker) | USD/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_4h_sales_per_mw` | A 4-hour battery (perfect-foresight upper bound): sales per MW in the month at the real-time hub price | USD/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `flat_price` | The month's mean real-time price over all its priced hours | USD/MWh | 245 | 2018-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `hours_in_month` | The hours of the month | count | 245 | 2018-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `peaker_capture_price` | A gas peaker (runs when the hub price exceeds its fuel and variable cost): capture price, sales over energy delivered | USD/MWh | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `peaker_capture_rate` | A gas peaker (runs when the hub price exceeds its fuel and variable cost): capture price over flat price, percent | pct | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `peaker_energy_per_mw` | A gas peaker (runs when the hub price exceeds its fuel and variable cost): energy delivered per MW in the month | MWh/MW | 245 | 2018-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `peaker_flat_price` | A gas peaker (runs when the hub price exceeds its fuel and variable cost): mean real-time price over the hours the asset used | USD/MWh | 245 | 2018-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `peaker_hours` | A gas peaker (runs when the hub price exceeds its fuel and variable cost): priced hours used (for batteries, the days) | count | 245 | 2018-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `peaker_revenue_per_mw` | A gas peaker (runs when the hub price exceeds its fuel and variable cost): merchant revenue per MW in the month: sales less purchases (batteries) or less fuel and variable O&M (peaker) | USD/MW | 245 | 2018-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `peaker_sales_per_mw` | A gas peaker (runs when the hub price exceeds its fuel and variable cost): sales per MW in the month at the real-time hub price | USD/MW | 245 | 2018-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_capture_price` | Solar (fleet average per MW of nameplate): capture price, sales over energy delivered | USD/MWh | 218 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_capture_rate` | Solar (fleet average per MW of nameplate): capture price over flat price, percent | pct | 218 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_energy_per_mw` | Solar (fleet average per MW of nameplate): energy delivered per MW in the month | MWh/MW | 218 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_flat_price` | Solar (fleet average per MW of nameplate): mean real-time price over the hours the asset used | USD/MWh | 218 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_hours` | Solar (fleet average per MW of nameplate): priced hours used (for batteries, the days) | count | 218 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_revenue_per_mw` | Solar (fleet average per MW of nameplate): merchant revenue per MW in the month: sales less purchases (batteries) or less fuel and variable O&M (peaker) | USD/MW | 218 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_sales_per_mw` | Solar (fleet average per MW of nameplate): sales per MW in the month at the real-time hub price | USD/MW | 218 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_capture_price` | Wind (fleet average per MW of nameplate): capture price, sales over energy delivered | USD/MWh | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_capture_rate` | Wind (fleet average per MW of nameplate): capture price over flat price, percent | pct | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_energy_per_mw` | Wind (fleet average per MW of nameplate): energy delivered per MW in the month | MWh/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_flat_price` | Wind (fleet average per MW of nameplate): mean real-time price over the hours the asset used | USD/MWh | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_hours` | Wind (fleet average per MW of nameplate): priced hours used (for batteries, the days) | count | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_revenue_per_mw` | Wind (fleet average per MW of nameplate): merchant revenue per MW in the month: sales less purchases (batteries) or less fuel and variable O&M (peaker) | USD/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_sales_per_mw` | Wind (fleet average per MW of nameplate): sales per MW in the month at the real-time hub price | USD/MW | 244 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |

### `nlr_jedi_multipliers`

One JEDI figure per MW for one technology, location, phase and effect: jobs, earnings or output, or the default project's MW, or the phase's local spending share.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 5562.

- **Time:** ts_utc is 1 January of the model's dollar year; freq P1Y.
- **Revisions:** Rewritten whole as one snapshot by each run of the connector; vintage is not filled (x_version names the model release).
- **Source:** nlr:jedi National Laboratory of the Rockies (NLR, formerly NREL), Jobs and Economic Development Impact (JEDI) models (https://www.nlr.gov/analysis/jedi/models)
- **Method note:** [`docs/methods/economic_impact.md`](../methods/economic_impact.md)
- **Cite as:** National Laboratory of the Rockies (NLR, formerly NREL). Jobs and Economic Development Impact (JEDI) models: land-based wind W9.14.18, photovoltaics PV05.20.21, natural gas NG4.17.17, geothermal GT12.23.16. Via the Energy Research Warehouse (ERW), table `nlr_jedi_multipliers`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: nlr_jedi:<technology>:<state or us>:<phase>:<effect> | none | text | for example nlr_jedi:geothermal:ak:all:project, nlr_jedi:geothermal:ak:construction:induced, nlr_jedi:geothermal:ak:construction:onsite; 2266 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2010-01-01T00:00:00Z, 2017-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.008795 to 10251979.272115; 4347 distinct | 0 |
| `unit` | The unit of the row's value | none | text | FTE-year/MW, FTE/MW, MW, USD/MW, USD/MW-year, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5562 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5562 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nlr:jedi | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nlr.gov/docs/libraries/analysis/01d-jedi-geothermal-model-rel-gt12-23-16.xlsm, https://www.nlr.gov/docs/libraries/analysis/01d-jedi-land-based-wind-model-rel-w6-28-19.xlsm?sfvrsn=e1d95728_2, https://www.nlr.gov/docs/libraries/analysis/01d-jedi-ngas-model_rel-ng4-17-17.xlsm?sfvrsn=d9ff898_2, https://www.nlr.gov/docs/libraries/analysis/jedi-pv-model.xlsm?sfvrsn=837efebd_2 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-20T07:53:08Z, 2026-10-20T07:53:10Z, 2026-10-20T07:53:12Z, 2026-10-20T07:53:15Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5562 |
| `x_technology` | The technology of the JEDI model: geothermal, land_based_wind, natural_gas or utility_pv | none | text | geothermal, land_based_wind, natural_gas, utility_pv | 0 |
| `x_state` | The location's state, two-letter code | none | text | for example AK, AL, AR; 51 distinct | 108: The location is the United States as a whole |
| `x_location` | The location as the JEDI model's own list spells it | none | text | for example ALABAMA, ALASKA, ARIZONA; 54 distinct | 0 |
| `x_phase` | The phase: construction, operations, or all (the project row) | none | text | all, construction, operations | 0 |
| `x_effect` | The part of the effect: onsite, supply_chain, induced or total; project (the default project's MW) or spending (the local share) | none | text | induced, onsite, project, spending, supply_chain, total | 0 |
| `x_model` | The JEDI model's name | none | text | JEDI Geothermal Model, JEDI Land-based Wind Model, JEDI Natural Gas Model, JEDI Photovoltaics Model | 0 |
| `x_version` | The model's release (its About sheet) | none | text | GT12.23.16, NG4.17.17, PV05.20.21, W9.14.18 | 0 |
| `x_file` | The model's workbook file name | none | text | 01d-jedi-geothermal-model-rel-gt12-23-16.xlsm, 01d-jedi-land-based-wind-model-rel-w6-28-19.xlsm, 01d-jedi-ngas-model_rel-ng4-17-17.xlsm, jedi-pv-model.xlsm | 0 |
| `x_sheet` | The model's summary sheet the figure is read from | none | text | Summary Results, SummaryResults | 0 |
| `x_cells` | The workbook cells the figure is computed from (the figure's cell over the project's MW cell) | none | text | for example Summary Results!B23 / Summary Results!B7, Summary Results!B26 / Summary Results!B7, Summary Results!B27 / Summary Results!B7; 91 distinct | 0 |
| `x_project_mw` | The MW of JEDI's default project the figures are per | MW | number | 100.0, 12.226196, 300.0, 500.0 | 0 |
| `x_mw_basis` | What the project's MW measures (nameplate, DC nameplate, or the model's net output) | none | text | DC nameplate MW, nameplate MW, nameplate MW (the model's 10 MW net output) | 0 |
| `x_dollar_year` | The model's dollar year; the table converts nothing | none | integer | 2010, 2017 | 0 |
| `x_multiplier_data` | The year and source of the model's IMPLAN multipliers, as its Multipliers sheet states them | none | text | Multipliers!D2 (Year of Data) 2014; the sheet's note: Source: IMPLAN™, using 2012 state data., Multipliers!D2 (Year of Data) 2014; the sheet's note: Source: IMPLAN™, using 2014 state data., Multipliers!D2 (Year of Data) 2016; the sheet's note: Source: IMPLAN™, using 2016 state data., Multipliers!D2 (Year of Data) 2019; the sheet's note: Source: IMPLAN™, using 2019 state data. | 0 |
| `x_local_share` | JEDI's local spending over the phase's cost | ratio | number | 0.027304 to 1.037868; 195 distinct | 206: Empty on the project_mw rows |
| `x_local_share_cells` | The workbook cells the local share is computed from | none | text | Summary Results!D11 / Summary Results!D10, Summary Results!D8 / Summary Results!D7, SummaryResults!C12 / SummaryResults!C11, SummaryResults!C14 / SummaryResults!C13, SummaryResults!C15 / SummaryResults!C14, SummaryResults!C17 / SummaryResults!C16, SummaryResults!C18 / SummaryResults!C17 | 206: Empty on the project_mw rows |
| `x_settings` | Settings changed from the workbook's saved project (the PV model's System Application set to Utility) | none | text | ProjectData!B15 = Utility | 4158: No setting changed (every model but the PV model) |
| `x_method` | How the figure was computed: JEDI's own formulas from the workbook's constants with Project Location set to the location | none | text | JEDI's formulas computed from the workbook's constants with Project Location set to this location and ProjectData!B15 = Utility; nothing else changed (warehouse/connectors/jedi_recalc.py), JEDI's formulas computed from the workbook's constants with Project Location set to this location; nothing else changed (warehouse/connectors/jedi_recalc.py), the workbook's saved project, computed from its constants (every saved figure reproduced) | 0 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `earnings` | JEDI's earnings per MW: construction over the build (USD/MW), operations each year (USD/MW-year) | USD/MW; USD/MW-year | 1648 | 2010-01-01T00:00:00Z | 2017-01-01T00:00:00Z |
| `jobs` | JEDI's jobs per MW: construction job-years over the build (1 FTE = 2,080 hours), operations jobs each year | FTE-year/MW; FTE/MW | 1648 | 2010-01-01T00:00:00Z | 2017-01-01T00:00:00Z |
| `local_share` | JEDI's local spending over the phase's cost | ratio | 412 | 2010-01-01T00:00:00Z | 2017-01-01T00:00:00Z |
| `output` | JEDI's economic output per MW: construction over the build (USD/MW), operations each year (USD/MW-year) | USD/MW; USD/MW-year | 1648 | 2010-01-01T00:00:00Z | 2017-01-01T00:00:00Z |
| `project_mw` | The MW of JEDI's default project | MW | 206 | 2010-01-01T00:00:00Z | 2017-01-01T00:00:00Z |

### `node_basis_daily`

One ERCOT settlement point's value of one price measure (mean, four-hour spread, or basis against the hub average) for one operating day, day-ahead or real time.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 1035045.

- **Time:** ts_utc is the Central operating day at 00:00:00Z; freq P1D. A day is written only whole, for the point and the hub.
- **Revisions:** Rewritten whole by each run from ERCOT's saved files (the old file removed first); vintage is not filled.
- **Source:** erw:node_basis ERW derived table, the node basis (docs/methods/node_basis.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/node_basis.md)
- **Method note:** [`docs/methods/node_basis.md`](../methods/node_basis.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT's settlement points against the hub, by day and by month (warehouse/derived/node_basis.py). Via the Energy Research Warehouse (ERW), table `node_basis_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:<settlement point> | none | text | for example ercot:7RNCHSLR_ALL, ercot:A4_DGR1_RN, ercot:A4_DGR2_RN; 888 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-10-01T00:00:00Z to 2026-11-18T00:00:00Z; 383 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -650.1554 to 16571.1625; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_dam or ercot_rtm | none | text | ercot_dam, ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example 7RNCHSLR_ALL, A4_DGR1_RN, A4_DGR2_RN; 888 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:node_basis | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/node_basis.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T17:34:43Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1035045 |
| `x_hub` | The hub the basis is taken against: HB_HUBAVG, the hub average, for every point (the ERW holds no list of each node's zone and zonal hub) | none | text | HB_HUBAVG | 0 |
| `x_resource_type` | ERCOT's resource types at the point in the day's files, joined by + (PWRSTR, ESR, PVGR, WIND, CCGT90, SCGT90 and others); HU for a hub, LZ for a load zone | none | text | for example CCGT90, CCLE90, CLLIG; 33 distinct | 0 |
| `x_class` | The point's class: storage, solar, wind, gas, other or mixed (a resource node, by its types), hub, zone, or unknown (a point no disclosure names) | none | text | gas, hub, mixed, other, solar, storage, wind, zone | 0 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dam_basis` | Day-ahead: the point's daily mean less HB_HUBAVG's daily mean over the same hours | USD/MWh | 299831 | 2025-10-01T00:00:00Z | 2026-10-20T00:00:00Z |
| `dam_mean` | Day-ahead: the day's mean hourly price at the point | USD/MWh | 299831 | 2025-10-01T00:00:00Z | 2026-10-20T00:00:00Z |
| `dam_spread_4h` | Day-ahead: the mean of the day's four dearest hours less the mean of its four cheapest | USD/MWh | 299831 | 2025-10-01T00:00:00Z | 2026-10-20T00:00:00Z |
| `rtm_basis` | Real time: the point's daily mean less HB_HUBAVG's daily mean over the same hours | USD/MWh | 45184 | 2026-09-28T00:00:00Z | 2026-11-18T00:00:00Z |
| `rtm_mean` | Real time: the day's mean hourly price at the point | USD/MWh | 45184 | 2026-09-28T00:00:00Z | 2026-11-18T00:00:00Z |
| `rtm_spread_4h` | Real time: the mean of the day's four dearest hours less the mean of its four cheapest | USD/MWh | 45184 | 2026-09-28T00:00:00Z | 2026-11-18T00:00:00Z |

### `node_basis_summary`

One month's statistic of the distribution of ERCOT's settlement points against the hub average, for one market and one class of points.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 1344.

- **Time:** ts_utc is the first day of the Central month at 00:00:00Z; freq P1M.
- **Revisions:** Rewritten whole by each run from ERCOT's saved files; vintage is not filled.
- **Source:** erw:node_basis ERW derived table, the node basis (docs/methods/node_basis.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/node_basis.md)
- **Method note:** [`docs/methods/node_basis.md`](../methods/node_basis.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT's settlement points against the hub, by day and by month (warehouse/derived/node_basis.py). Via the Energy Research Warehouse (ERW), table `node_basis_summary`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:HB_HUBAVG on every row: the hub the points are compared with | none | text | ercot:HB_HUBAVG | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-10-01T00:00:00Z, 2025-11-01T00:00:00Z, 2025-12-01T00:00:00Z, 2026-01-01T00:00:00Z, 2026-02-01T00:00:00Z, 2026-03-01T00:00:00Z, 2026-04-01T00:00:00Z, 2026-05-01T00:00:00Z, 2026-06-01T00:00:00Z, 2026-07-01T00:00:00Z, 2026-08-01T00:00:00Z, 2026-09-01T00:00:00Z, 2026-10-01T00:00:00Z, 2026-11-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -32.0188 to 871.0; 1106 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_dam or ercot_rtm | none | text | ercot_dam, ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: HB_HUBAVG on every row | none | text | HB_HUBAVG | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:node_basis | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/node_basis.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T17:34:43Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1344 |
| `x_market` | The market: dam (day-ahead) or rtm (real time) | none | text | dam, rtm | 0 |
| `x_class` | The class of points: all (every resource node), storage, solar, wind, gas, or zone (the load zones) | none | text | all, gas, solar, storage, wind, zone | 0 |
| `x_stat` | The statistic: basis_p10 to basis_p90 and spread_4h_p10 to spread_4h_p90 (percentiles across the points), hub_spread_4h, share_wider_pct, points, days | none | text | basis_p10, basis_p25, basis_p50, basis_p75, basis_p90, days, hub_spread_4h, points, share_wider_pct, spread_4h_p10, spread_4h_p25, spread_4h_p50, spread_4h_p75, spread_4h_p90 | 0 |

Variables (168):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dam_all_basis_p10` | Day-ahead, every resource node: percentile 10 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_basis_p25` | Day-ahead, every resource node: percentile 25 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_basis_p50` | Day-ahead, every resource node: percentile 50 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_basis_p75` | Day-ahead, every resource node: percentile 75 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_basis_p90` | Day-ahead, every resource node: percentile 90 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_days` | Day-ahead, every resource node: the hub's days in the month | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_hub_spread_4h` | Day-ahead, every resource node: the hub's (HB_HUBAVG) own mean daily four-hour spread over the same days | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_points` | Day-ahead, every resource node: points with at least 90 percent of the hub's days in the month | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_share_wider_pct` | Day-ahead, every resource node: share of the points whose mean spread is wider than the hub's over the same days | pct | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_spread_4h_p10` | Day-ahead, every resource node: percentile 10 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_spread_4h_p25` | Day-ahead, every resource node: percentile 25 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_spread_4h_p50` | Day-ahead, every resource node: percentile 50 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_spread_4h_p75` | Day-ahead, every resource node: percentile 75 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_all_spread_4h_p90` | Day-ahead, every resource node: percentile 90 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_basis_p10` | Day-ahead, the gas resource nodes: percentile 10 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_basis_p25` | Day-ahead, the gas resource nodes: percentile 25 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_basis_p50` | Day-ahead, the gas resource nodes: percentile 50 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_basis_p75` | Day-ahead, the gas resource nodes: percentile 75 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_basis_p90` | Day-ahead, the gas resource nodes: percentile 90 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_days` | Day-ahead, the gas resource nodes: the hub's days in the month | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_hub_spread_4h` | Day-ahead, the gas resource nodes: the hub's (HB_HUBAVG) own mean daily four-hour spread over the same days | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_points` | Day-ahead, the gas resource nodes: points with at least 90 percent of the hub's days in the month | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_share_wider_pct` | Day-ahead, the gas resource nodes: share of the points whose mean spread is wider than the hub's over the same days | pct | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_spread_4h_p10` | Day-ahead, the gas resource nodes: percentile 10 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_spread_4h_p25` | Day-ahead, the gas resource nodes: percentile 25 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_spread_4h_p50` | Day-ahead, the gas resource nodes: percentile 50 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_spread_4h_p75` | Day-ahead, the gas resource nodes: percentile 75 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_gas_spread_4h_p90` | Day-ahead, the gas resource nodes: percentile 90 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_basis_p10` | Day-ahead, the solar resource nodes: percentile 10 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_basis_p25` | Day-ahead, the solar resource nodes: percentile 25 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_basis_p50` | Day-ahead, the solar resource nodes: percentile 50 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_basis_p75` | Day-ahead, the solar resource nodes: percentile 75 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_basis_p90` | Day-ahead, the solar resource nodes: percentile 90 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_days` | Day-ahead, the solar resource nodes: the hub's days in the month | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_hub_spread_4h` | Day-ahead, the solar resource nodes: the hub's (HB_HUBAVG) own mean daily four-hour spread over the same days | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_points` | Day-ahead, the solar resource nodes: points with at least 90 percent of the hub's days in the month | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_share_wider_pct` | Day-ahead, the solar resource nodes: share of the points whose mean spread is wider than the hub's over the same days | pct | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_spread_4h_p10` | Day-ahead, the solar resource nodes: percentile 10 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_spread_4h_p25` | Day-ahead, the solar resource nodes: percentile 25 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_spread_4h_p50` | Day-ahead, the solar resource nodes: percentile 50 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_spread_4h_p75` | Day-ahead, the solar resource nodes: percentile 75 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_solar_spread_4h_p90` | Day-ahead, the solar resource nodes: percentile 90 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_basis_p10` | Day-ahead, the storage resource nodes: percentile 10 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_basis_p25` | Day-ahead, the storage resource nodes: percentile 25 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_basis_p50` | Day-ahead, the storage resource nodes: percentile 50 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_basis_p75` | Day-ahead, the storage resource nodes: percentile 75 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_basis_p90` | Day-ahead, the storage resource nodes: percentile 90 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_days` | Day-ahead, the storage resource nodes: the hub's days in the month | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_hub_spread_4h` | Day-ahead, the storage resource nodes: the hub's (HB_HUBAVG) own mean daily four-hour spread over the same days | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_points` | Day-ahead, the storage resource nodes: points with at least 90 percent of the hub's days in the month | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_share_wider_pct` | Day-ahead, the storage resource nodes: share of the points whose mean spread is wider than the hub's over the same days | pct | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_spread_4h_p10` | Day-ahead, the storage resource nodes: percentile 10 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_spread_4h_p25` | Day-ahead, the storage resource nodes: percentile 25 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_spread_4h_p50` | Day-ahead, the storage resource nodes: percentile 50 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_spread_4h_p75` | Day-ahead, the storage resource nodes: percentile 75 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_storage_spread_4h_p90` | Day-ahead, the storage resource nodes: percentile 90 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_basis_p10` | Day-ahead, the wind resource nodes: percentile 10 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_basis_p25` | Day-ahead, the wind resource nodes: percentile 25 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_basis_p50` | Day-ahead, the wind resource nodes: percentile 50 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_basis_p75` | Day-ahead, the wind resource nodes: percentile 75 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_basis_p90` | Day-ahead, the wind resource nodes: percentile 90 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_days` | Day-ahead, the wind resource nodes: the hub's days in the month | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_hub_spread_4h` | Day-ahead, the wind resource nodes: the hub's (HB_HUBAVG) own mean daily four-hour spread over the same days | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_points` | Day-ahead, the wind resource nodes: points with at least 90 percent of the hub's days in the month | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_share_wider_pct` | Day-ahead, the wind resource nodes: share of the points whose mean spread is wider than the hub's over the same days | pct | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_spread_4h_p10` | Day-ahead, the wind resource nodes: percentile 10 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_spread_4h_p25` | Day-ahead, the wind resource nodes: percentile 25 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_spread_4h_p50` | Day-ahead, the wind resource nodes: percentile 50 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_spread_4h_p75` | Day-ahead, the wind resource nodes: percentile 75 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_wind_spread_4h_p90` | Day-ahead, the wind resource nodes: percentile 90 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_basis_p10` | Day-ahead, the load zones: percentile 10 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_basis_p25` | Day-ahead, the load zones: percentile 25 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_basis_p50` | Day-ahead, the load zones: percentile 50 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_basis_p75` | Day-ahead, the load zones: percentile 75 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_basis_p90` | Day-ahead, the load zones: percentile 90 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_days` | Day-ahead, the load zones: the hub's days in the month | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_hub_spread_4h` | Day-ahead, the load zones: the hub's (HB_HUBAVG) own mean daily four-hour spread over the same days | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_points` | Day-ahead, the load zones: points with at least 90 percent of the hub's days in the month | count | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_share_wider_pct` | Day-ahead, the load zones: share of the points whose mean spread is wider than the hub's over the same days | pct | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_spread_4h_p10` | Day-ahead, the load zones: percentile 10 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_spread_4h_p25` | Day-ahead, the load zones: percentile 25 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_spread_4h_p50` | Day-ahead, the load zones: percentile 50 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_spread_4h_p75` | Day-ahead, the load zones: percentile 75 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dam_zone_spread_4h_p90` | Day-ahead, the load zones: percentile 90 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 13 | 2025-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `rtm_all_basis_p10` | Real time, every resource node: percentile 10 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_basis_p25` | Real time, every resource node: percentile 25 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_basis_p50` | Real time, every resource node: percentile 50 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_basis_p75` | Real time, every resource node: percentile 75 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_basis_p90` | Real time, every resource node: percentile 90 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_days` | Real time, every resource node: the hub's days in the month | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_hub_spread_4h` | Real time, every resource node: the hub's (HB_HUBAVG) own mean daily four-hour spread over the same days | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_points` | Real time, every resource node: points with at least 90 percent of the hub's days in the month | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_share_wider_pct` | Real time, every resource node: share of the points whose mean spread is wider than the hub's over the same days | pct | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_spread_4h_p10` | Real time, every resource node: percentile 10 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_spread_4h_p25` | Real time, every resource node: percentile 25 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_spread_4h_p50` | Real time, every resource node: percentile 50 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_spread_4h_p75` | Real time, every resource node: percentile 75 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_all_spread_4h_p90` | Real time, every resource node: percentile 90 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_basis_p10` | Real time, the gas resource nodes: percentile 10 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_basis_p25` | Real time, the gas resource nodes: percentile 25 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_basis_p50` | Real time, the gas resource nodes: percentile 50 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_basis_p75` | Real time, the gas resource nodes: percentile 75 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_basis_p90` | Real time, the gas resource nodes: percentile 90 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_days` | Real time, the gas resource nodes: the hub's days in the month | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_hub_spread_4h` | Real time, the gas resource nodes: the hub's (HB_HUBAVG) own mean daily four-hour spread over the same days | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_points` | Real time, the gas resource nodes: points with at least 90 percent of the hub's days in the month | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_share_wider_pct` | Real time, the gas resource nodes: share of the points whose mean spread is wider than the hub's over the same days | pct | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_spread_4h_p10` | Real time, the gas resource nodes: percentile 10 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_spread_4h_p25` | Real time, the gas resource nodes: percentile 25 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_spread_4h_p50` | Real time, the gas resource nodes: percentile 50 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_spread_4h_p75` | Real time, the gas resource nodes: percentile 75 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_gas_spread_4h_p90` | Real time, the gas resource nodes: percentile 90 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_basis_p10` | Real time, the solar resource nodes: percentile 10 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_basis_p25` | Real time, the solar resource nodes: percentile 25 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_basis_p50` | Real time, the solar resource nodes: percentile 50 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_basis_p75` | Real time, the solar resource nodes: percentile 75 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_basis_p90` | Real time, the solar resource nodes: percentile 90 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_days` | Real time, the solar resource nodes: the hub's days in the month | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_hub_spread_4h` | Real time, the solar resource nodes: the hub's (HB_HUBAVG) own mean daily four-hour spread over the same days | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_points` | Real time, the solar resource nodes: points with at least 90 percent of the hub's days in the month | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_share_wider_pct` | Real time, the solar resource nodes: share of the points whose mean spread is wider than the hub's over the same days | pct | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_spread_4h_p10` | Real time, the solar resource nodes: percentile 10 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_spread_4h_p25` | Real time, the solar resource nodes: percentile 25 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_spread_4h_p50` | Real time, the solar resource nodes: percentile 50 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_spread_4h_p75` | Real time, the solar resource nodes: percentile 75 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_solar_spread_4h_p90` | Real time, the solar resource nodes: percentile 90 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_basis_p10` | Real time, the storage resource nodes: percentile 10 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_basis_p25` | Real time, the storage resource nodes: percentile 25 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_basis_p50` | Real time, the storage resource nodes: percentile 50 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_basis_p75` | Real time, the storage resource nodes: percentile 75 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_basis_p90` | Real time, the storage resource nodes: percentile 90 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_days` | Real time, the storage resource nodes: the hub's days in the month | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_hub_spread_4h` | Real time, the storage resource nodes: the hub's (HB_HUBAVG) own mean daily four-hour spread over the same days | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_points` | Real time, the storage resource nodes: points with at least 90 percent of the hub's days in the month | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_share_wider_pct` | Real time, the storage resource nodes: share of the points whose mean spread is wider than the hub's over the same days | pct | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_spread_4h_p10` | Real time, the storage resource nodes: percentile 10 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_spread_4h_p25` | Real time, the storage resource nodes: percentile 25 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_spread_4h_p50` | Real time, the storage resource nodes: percentile 50 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_spread_4h_p75` | Real time, the storage resource nodes: percentile 75 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_storage_spread_4h_p90` | Real time, the storage resource nodes: percentile 90 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_basis_p10` | Real time, the wind resource nodes: percentile 10 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_basis_p25` | Real time, the wind resource nodes: percentile 25 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_basis_p50` | Real time, the wind resource nodes: percentile 50 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_basis_p75` | Real time, the wind resource nodes: percentile 75 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_basis_p90` | Real time, the wind resource nodes: percentile 90 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_days` | Real time, the wind resource nodes: the hub's days in the month | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_hub_spread_4h` | Real time, the wind resource nodes: the hub's (HB_HUBAVG) own mean daily four-hour spread over the same days | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_points` | Real time, the wind resource nodes: points with at least 90 percent of the hub's days in the month | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_share_wider_pct` | Real time, the wind resource nodes: share of the points whose mean spread is wider than the hub's over the same days | pct | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_spread_4h_p10` | Real time, the wind resource nodes: percentile 10 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_spread_4h_p25` | Real time, the wind resource nodes: percentile 25 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_spread_4h_p50` | Real time, the wind resource nodes: percentile 50 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_spread_4h_p75` | Real time, the wind resource nodes: percentile 75 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_wind_spread_4h_p90` | Real time, the wind resource nodes: percentile 90 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_basis_p10` | Real time, the load zones: percentile 10 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_basis_p25` | Real time, the load zones: percentile 25 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_basis_p50` | Real time, the load zones: percentile 50 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_basis_p75` | Real time, the load zones: percentile 75 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_basis_p90` | Real time, the load zones: percentile 90 across the points of each point's mean daily basis in the month (its mean less HB_HUBAVG's) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_days` | Real time, the load zones: the hub's days in the month | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_hub_spread_4h` | Real time, the load zones: the hub's (HB_HUBAVG) own mean daily four-hour spread over the same days | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_points` | Real time, the load zones: points with at least 90 percent of the hub's days in the month | count | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_share_wider_pct` | Real time, the load zones: share of the points whose mean spread is wider than the hub's over the same days | pct | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_spread_4h_p10` | Real time, the load zones: percentile 10 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_spread_4h_p25` | Real time, the load zones: percentile 25 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_spread_4h_p50` | Real time, the load zones: percentile 50 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_spread_4h_p75` | Real time, the load zones: percentile 75 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rtm_zone_spread_4h_p90` | Real time, the load zones: percentile 90 across the points of each point's mean daily four-hour spread in the month (four dearest hours less four cheapest) | USD/MWh | 3 | 2026-09-01T00:00:00Z | 2026-11-01T00:00:00Z |

### `nuclear_fleet_status`

One US reactor's, one grid's reactor fleet's or the whole US fleet's value of one measure (capacity, outages, available energy, uprates) for one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 15048.

- **Time:** ts_utc is the year's first day at 00:00:00Z; freq P1Y; the newest year runs to the newest day held.
- **Revisions:** Rewritten whole as one snapshot by each run of the builder from EIA's daily outage table and EIA-860M; vintage is not filled.
- **Source:** eia:nuclear-outages U.S. Energy Information Administration, Status of U.S. Nuclear Outages (from the NRC's power reactor status reports); EIA-860M
- **Method note:** [`docs/methods/nuclear_fleet_status.md`](../methods/nuclear_fleet_status.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The U.S. reactor fleet by reactor and year, and by grid (docs/methods/nuclear_fleet_status.md). Via the Energy Research Warehouse (ERW), table `nuclear_fleet_status`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: nuclear_fleet:<facility>:<generator> for a reactor, nuclear_fleet:grid:<BA> for a grid's fleet, nuclear_fleet:US | none | text | for example nuclear_fleet:1060:1, nuclear_fleet:1590:1, nuclear_fleet:1715:1; 124 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z, 2026-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -88.9 to 804217344.384; 4533 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, count, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 15048 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The reactor's name (plant, reactor number) from EIA's outage table, not a pricing node; empty on the grid and US rows | none | text | for example Arkansas Nuclear One, reactor 1, Arkansas Nuclear One, reactor 2, Beaver Valley, reactor 1; 107 distinct | 1340 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:nuclear_fleet_status | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/nuclear_fleet_status.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T17:53:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 15048 |
| `x_facility` | EIA's plant id of the reactor | none | integer | 46 to 8907; 66 distinct | 1340: Empty on the grid and US rows |
| `x_generator` | EIA's reactor (generator) id within the plant | none | integer | 1, 2, 3, 4 | 1340: Empty on the grid and US rows |
| `x_ba` | The balancing authority of the reactor's plant in EIA-860M (none where EIA-860M lists no operating nuclear generator at the plant); on a grid row, the grid | none | text | BPAT, CISO, CPLE, DUK, ERCO, FPL, ISNE, MISO, NYIS, PJM, SCEG, SOCO, SRP, SWPP, TVA, none | 80: Empty on the US rows |
| `x_first` | The reactor's first day held (a day after 1 January 2007 is a restart) | none | date | 2007-01-01, 2015-10-27, 2022-10-13, 2023-08-21 | 1340: Empty on the grid and US rows |
| `x_last` | The reactor's last day held (a day before the newest day is a retirement) | none | date | 2012-12-31, 2014-11-30, 2016-09-30, 2018-08-31, 2019-04-30, 2019-08-31, 2020-03-31, 2020-10-31, 2021-03-31, 2026-11-19 | 1340: Empty on the grid and US rows |

Variables (8):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `available_mwh` | Capacity less outage, times 24, summed over the year's days (summed over reactors on a grid or US row) | MWh | 2308 | 2007-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `capacity_change_mw` | capacity_mw less the year before's: an uprate or a derate | MW | 1861 | 2008-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `capacity_mw` | The year's highest daily capacity (summed over the reactors on a grid or US row) | MW | 2308 | 2007-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `days_held` | Days of the year held | count | 1982 | 2007-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `full_outage_days` | Days in the year the reactor was 99 percent out or more | count | 1973 | 2007-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `long_outages` | Runs of 14 or more full-outage days in a row (refuelings and long outages) | count | 1973 | 2007-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `outage_share` | Outage MW-days over capacity MW-days in the year | ratio | 2308 | 2007-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `reactors` | Reactors counted in the grid's or the US fleet in the year | count | 335 | 2007-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

### `region_weather_hourly`

One EIA region's population-weighted mean temperature in one hour, written only for an hour every one of its stations holds.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 879553.

- **Time:** ts_utc is the hour's start, UTC; freq PT1H.
- **Revisions:** Rewritten whole as one snapshot by each run of the connector.
- **Source:** erw:region_weather_hourly the ERW's weighted means of noaa_region_station_hourly_<year> (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/region_weather.md)
- **Method note:** [`docs/methods/region_weather.md`](../methods/region_weather.md)
- **Cite as:** Energy Research Warehouse. Region temperature, population weighted. Via the Energy Research Warehouse (ERW), table `region_weather_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930:<region>, EIA-930's region code | none | text | eia930:CAL, eia930:CAR, eia930:CENT, eia930:FLA, eia930:MIDA, eia930:MIDW, eia930:NE, eia930:NW, eia930:NY, eia930:SE, eia930:SW, eia930:TEN, eia930:TEX | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-01T00:00:00Z to 2026-11-07T14:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -10.44 to 114.22; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:region_weather_hourly | 0 |
| `x_stations` | The region's stations whose temperatures the hour's weighted mean is over | count | integer | 12, 14, 16, 17, 19, 20, 21, 22, 5 | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `temperature_f` | The weighted mean of the region's stations' temperatures, stations weighted by county population | degF | 879553 | 2018-07-01T00:00:00Z | 2026-11-07T14:00:00Z |

### `resource_layer_features`

One grid cell, site or area of one layer of the natural resource map (wind, solar, geothermal, hydropower, biomass, oil and gas basins and plays, coal fields), with its value.

Shape: entities. Keys: `entity_id`. License: public; tier: derived. Rows read on 2026-11-20: 1371628.

- **Time:** No time column; vintage names the period or edition of the publisher's data; the table is a snapshot as built.
- **Revisions:** Rewritten whole as one snapshot by each run of the builder from the map's layer files and the saved USGS coal fields file.
- **Source:** erw:resource_layer_features the ERW's reduction of each publisher's file (warehouse/connectors/resource_layers.py): wind_speed_100m: National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL), https://www.nlr.gov/docs/libraries/gis/us-wind-data.zip (sha256 3c9f29dedc92e6ef8107ba0272575d255d91fee6d96a7c455c8365bbeae6d109); solar_ghi: National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL), https://www.nlr.gov/docs/libraries/gis/nsrdbv3_ghi.zip (sha256 55531ec07a5f4c47c0c8fe74407f71ca4733fa221c843063b13c9c1f93bca4fc); solar_dni: National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL), https://www.nlr.gov/docs/libraries/gis/nsrdbv3_dni.zip (sha256 97f0e7e621f6fef9d9b15f70a0163f46aa7a0837b66c1fe7d984fad0ff4c2dc0); wind_capacity_factor: National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL), https://data.openei.org/files/8314/lbw_open_access_2035_moderate_115hh_170rd_supply_curve.csv (sha256 ef13116bd66f31157b2f7db6369831d63f3098877e91c6163766dbe6da47eb7d); geothermal_hydrothermal_sites: U.S. Geological Survey (USGS), https://www.sciencebase.gov/catalog/file/get/6606f534d34e4df16bd58277?f=__disk__ae%2Fbd%2F32%2Faebd32c1cf3b64ce4f19dc6e2535e5a5bc3382da (sha256 7724cb19112c68c21e50883d7fb73bbe6b98a872f6e319753b5c8c2f7df2bfc7); hydropower_npd: Oak Ridge National Laboratory (HydroSource), for the U.S. Department of Energy, https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/hydropower-capacity-us-npd/TechPotentialNPDs.csv (sha256 84635b4faecc332c31ab53fbbd7c42be7469d75bb2c1ca3c6827d2ac296aaf2f); geothermal_hydrothermal_favorability: U.S. Geological Survey (USGS), https://www.sciencebase.gov/catalog/file/get/6606ed51d34e4df16bd58251?f=__disk__79%2Fb1%2Fce%2F79b1ce18796d6fc4ae5b9292c58bd8aaee4846e5 (sha256 d9eb255587626875580aab4c1705031d63717d79080b530ffe0ce30f206eff78); geothermal_egs_favorability: National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL), https://www.nlr.gov/docs/libraries/gis/egs.zip (sha256 fdf8bcfb6dcc98252ae9a7d6389d27fa0c579d3a72021790b38bf3eb8b76c6af); oil_gas_basins: U.S. Energy Information Administration (EIA), https://www.eia.gov/maps/map_data/SedimentaryBasins_US_EIA.zip (sha256 02a017ccb84bdcc15726838098e3cfa73450b9655cf06e28d2eca6f3c04edcff); oil_gas_plays: U.S. Energy Information Administration (EIA), https://www.eia.gov/maps/map_data/TightOil_ShaleGas_Plays_Lower48_EIA.zip (sha256 c09b3bd2982754cfb63d12bbbfde6c6c5e8c02eee73e54d231a7c7de73f0541e); hydropower_nsd: Oak Ridge National Laboratory (HydroSource), for the U.S. Department of Energy, https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/hydropower-potential-new-stream-reach-development-conterminous-united-states/ORNL_NHAAP_NSD_SR_All_v1.zip (sha256 a8ab06e4dfea4a31f1dd293d6358af932bd839f4a41d59a181600a3877fb28f9); biomass: National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL), https://www.nlr.gov/docs/libraries/gis/solid-biomass.zip (sha256 f48ee40d6de1859d6f3cabc841b631a55287c4282bfe974719fd89555672f54d); coal_fields: usgs:of2012_1205_coal_fields https://pubs.usgs.gov/of/2012/1205/Downloads/GIS.zip (sha256 e491215d0a937cae48cc5e9a2763ea43c85a4d11c183ec7c5b1ac559d2a585a5) (https://pubs.usgs.gov/of/2012/1205/Downloads/GIS.zip)
- **Method note:** [`docs/methods/resource_layers_table.md`](../methods/resource_layers_table.md)
- **Cite as:** Energy Research Warehouse (ERW), derived; National Laboratory of the Rockies (NLR, formerly NREL); Oak Ridge National Laboratory (HydroSource), for the U.S. Department of Energy; U.S. Energy Information Administration (EIA); U.S. Geological Survey (USGS). Favorability of deep enhanced geothermal systems, lower 48, shapefile (2009); Geothermal Favorability Map Derived From Logistic Regression Models (2008 assessment; ScienceBase, doi:10.5066/P137NMXE); Hydropower Potential from New Stream-Reach Development for the Conterminous United States, aggregated summary of HUC10 watersheds (2014, version 1); NSRDB Physical Solar Model version 3 Direct Normal Irradiance, multi-year (1998-2016) annual and monthly averages, GeoTIFF; NSRDB Physical Solar Model version 3 Global Horizontal Irradiance, multi-year (1998-2016) annual and monthly averages, GeoTIFF; Open-File Report 2012-1205: Coal fields of the conterminous United States, National Coal Resource Assessment updated version (East, 2013); Solid biomass resources by county, shapefile (data for 2012, published 2014); Technical Potential for Hydropower Capacity at Non-powered Dams (2024, revised 25 June 2025; doi:10.21951/HydroCapacity_NPD/2570407); The natural resource map's layers as a table (docs/methods/resource_layers_table.md); Tight Oil and Shale Gas Plays in the U.S., Lower 48, shapefile, updated December 2021; U.S. Sedimentary Basins, shapefile (EIA maps, layer information for interactive state maps); WIND Toolkit, Multi-year (2007-2013) Annual Average Wind Speed at all heights, GeoTIFF, 2 km. Via the Energy Research Warehouse (ERW), table `resource_layer_features`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: resource:<layer>:r<row>c<column> for a grid cell, resource:<layer>:<the feature's place in its layer> for a site or area | none | text | for example resource:wind_speed_100m:r0c685, resource:wind_speed_100m:r0c686, resource:wind_speed_100m:r0c687; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: resource on every row | none | text | resource | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example wind_speed_100m cell r0 c685, wind_speed_100m cell r0 c686, wind_speed_100m cell r0 c687; more than 5000 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: The cell's center or the feature's centroid | degree | number | 19.478 to 69.30839; more than 5000 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: The cell's center or the feature's centroid | degree | number | -176.616 to -65.675; more than 5000 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 1371628 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1371628 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 1371628 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 1371628 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:resource_layer_features, usgs:of2012_1205_coal_fields | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://data.openei.org/files/8314/lbw_open_access_2035_moderate_115hh_170rd_supply_curve.csv, https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/hydropower-capacity-us-npd/TechPotentialNPDs.csv, https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/hydropower-potential-new-stream-reach-development-conterminous-united-states/ORNL_NHAAP_NSD_SR_All_v1.zip, https://pubs.usgs.gov/of/2012/1205/Downloads/GIS.zip, https://www.eia.gov/maps/map_data/SedimentaryBasins_US_EIA.zip, https://www.eia.gov/maps/map_data/TightOil_ShaleGas_Plays_Lower48_EIA.zip, https://www.nlr.gov/docs/libraries/gis/egs.zip, https://www.nlr.gov/docs/libraries/gis/nsrdbv3_dni.zip, https://www.nlr.gov/docs/libraries/gis/nsrdbv3_ghi.zip, https://www.nlr.gov/docs/libraries/gis/solid-biomass.zip, https://www.nlr.gov/docs/libraries/gis/us-wind-data.zip, https://www.sciencebase.gov/catalog/file/get/6606ed51d34e4df16bd58251?f=__disk__79%2Fb1%2Fce%2F79b1ce18796d6fc4ae5b9292c58bd8aaee4846e5, https://www.sciencebase.gov/catalog/file/get/6606f534d34e4df16bd58277?f=__disk__ae%2Fbd%2F32%2Faebd32c1cf3b64ce4f19dc6e2535e5a5bc3382da | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T21:26:20Z, 2026-10-07T21:33:22Z, 2026-10-07T21:33:58Z, 2026-10-07T21:34:33Z, 2026-10-07T21:39:30Z, 2026-10-07T21:39:32Z, 2026-10-07T21:39:34Z, 2026-10-07T21:39:39Z, 2026-10-07T21:39:41Z, 2026-10-08T08:45:07Z, 2026-10-08T08:47:16Z, 2026-11-19T12:39:54Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The period or edition of the layer's data in words, from the publisher's file (for example 2007-2013 with the publication date) | none | text | 1998-2016 (the file's metadata: "The data are averaged from hourly model output over 19 years (1998-2016)"); publication date 2018, 2007-2013 (the file's metadata: "Multi-year (2007-2013) Annual Average Wind Speed, meters per second, at 100 meters above surface level"); publication date 2015, 2009 (the file's metadata: analyses "performed by NREL (2009)" on temperature at depth from Southern Methodist University Geothermal Laboratory, Blackwell and Richards, 2009); metadata dated 23 February 2012, 2013, as of 5-6-2011 (the file's metadata: "Sedimentary basins associated with the EIA shale plays as of 5-6-2011"); file modified 10 March 2016, data for 2012 (the file's metadata: "Data for 2012, in dry metric tons/year"); published 30 October 2014, published 3 October 2024, revised 25 June 2025 (HydroSource's page; the file on its server is dated 25 June 2025); the file's readme: "These estimates represent the conditions over the historical period of 1980-2015", published 31 December 2014 (HydroSource's page); the file's own metadata is dated 10 January 2014 and its workbook was created on 2013-03-15, version 1; the years of flow behind the estimate are not stated in the files, the 2008 assessment (USGS Fact Sheet 2008-3082); the data file is dated 2010 and was released again on ScienceBase on 29 March 2024 (metadata date 20240329), the 2008 assessment; the data file is dated 2010 and was released again on ScienceBase on 29 March 2024 (metadata date 20240329), the 2024 edition, published 2025-01-01 on the Open Energy Data Initiative; the file models a 2035 turbine ("2035 moderate", 115 m hub height, 170 m rotor diameter); the weather years behind the mean are not stated in the files, updated December 2021 (the file's metadata: "Updated December 2021 with addition of Spraberry and Wolfcamp Plays in the Permian Basin") | 0 |
| `x_layer` | The map layer the row belongs to (wind_speed_100m, solar_ghi, solar_dni, wind_capacity_factor, geothermal, hydropower, biomass, oil_gas_basins, oil_gas_plays, coal_fields) | none | text | biomass, coal_fields, geothermal_egs_favorability, geothermal_hydrothermal_favorability, geothermal_hydrothermal_sites, hydropower_npd, hydropower_nsd, oil_gas_basins, oil_gas_plays, solar_dni, solar_ghi, wind_capacity_factor, wind_speed_100m | 0 |
| `x_kind` | What the row is: grid cell, site, or the area's kind (county, HUC10 watershed, sedimentary basin, play, favorability class, coal field) | none | text | HUC10 watershed, coal field, county, deep enhanced geothermal favorability class, grid cell, relative favorability class, sedimentary basin, site, tight oil and shale gas play | 0 |
| `x_value` | The layer's value for the cell, site or area, in x_unit (x_value_label says what it is) | the row's x_unit | number | 0.0 to 2002700.0; more than 5000 distinct | 602: Empty on the coal fields, which have no value (province, field, age and rank are in x_extra) |
| `x_unit` | The unit of x_value (m/s, kWh/m2/day, ratio, MW, MWe, class, dry metric tons/year, square miles) | none | text | MW, MWe, class (1 most favorable, 5 least favorable, 999 not assessed), class (the source's GRIDCODE, 1 to 10), dry metric tons/year, kWh/m2/day, m/s, ratio, square miles | 602: Empty on the coal fields |
| `x_value_label` | What x_value is, in the publisher's words where it gives them | none | text | Mean Megawatts electric (MWe), the source's MWe_Mean, Mean capacity factor across 11.5km grid-cell (the source's capacity_factor_ac), Nominal capacity (the source's cap_mw), The HUC10-level Total Potential capacity from identified stream-reaches with capacity greater than 1MW (the source's P_MW_Sum, a HUC10 total), all solid biomass resources of the county (the source's Total), annual average daily total solar resource, annual mean wind speed, area of the basin (the source's Area_sq_mi), area of the play (the source's Area_sq_mi), coal field (province, age and rank as USGS gives them), relative favorability class (the source's GRIDCODE, with its Descript range), relative favorability of the deep enhanced geothermal resource (the source's CLASS) | 0 |
| `x_publisher` | The publisher of the layer's data | none | text | National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL), Oak Ridge National Laboratory (HydroSource), for the U.S. Department of Energy, U.S. Energy Information Administration (EIA), U.S. Geological Survey, U.S. Geological Survey (USGS) | 0 |
| `x_cell_deg` | The grid cell's size in degrees | degree | number | 0.05 | 66266: Empty on sites and areas |
| `x_area_km2` | The area's size on a sphere of radius 6,371.0088 km | km2 | number | 0.0 to 810228.9; more than 5000 distinct | 1364759: Empty on grid cells and sites |
| `x_extra` | The publisher's other fields for the site or area, as JSON | none | text | for example {"Basin":"Anadarko","Lithology":"Shale","Shale_play":"Woodford","References":"Hand-drawn boundary around wells from OK Geol Surv","Source":"EIA","Area_sq_mi":3351.7712898,"Area_sq_km":8681.04778802,"ID":"WOO001","Age_shale":"Devonian"}, {"Basin":"Appalachian","Lithology":"Mixed Shale & Limestone","Shale_play":"Utica","References":"Appalachian Oil and Natural Gas Research Consortium, and USGS","Source":"EIA","Area_sq_mi":59054.2252868,"Area_sq_km":152949.741338,"ID":"UTI001","Age_shale":"Ordovician"}, {"Basin":"Appalachian","Lithology":"Shale","Shale_play":"Chattanooga","References":"5 TN counties with wells operated by CNX and Magellan","Source":"EIA","Area_sq_mi":1448.13143073,"Area_sq_km":3750.6431873,"ID":"CHA001","Age_shale":"Devonian"}; more than 5000 distinct | 1305362: Empty on grid cells |
| `x_source_sha256` | The SHA-256 of the publisher's file the row was read from | none | text | 02a017ccb84bdcc15726838098e3cfa73450b9655cf06e28d2eca6f3c04edcff, 3c9f29dedc92e6ef8107ba0272575d255d91fee6d96a7c455c8365bbeae6d109, 55531ec07a5f4c47c0c8fe74407f71ca4733fa221c843063b13c9c1f93bca4fc, 7724cb19112c68c21e50883d7fb73bbe6b98a872f6e319753b5c8c2f7df2bfc7, 84635b4faecc332c31ab53fbbd7c42be7469d75bb2c1ca3c6827d2ac296aaf2f, 97f0e7e621f6fef9d9b15f70a0163f46aa7a0837b66c1fe7d984fad0ff4c2dc0, a8ab06e4dfea4a31f1dd293d6358af932bd839f4a41d59a181600a3877fb28f9, c09b3bd2982754cfb63d12bbbfde6c6c5e8c02eee73e54d231a7c7de73f0541e, d9eb255587626875580aab4c1705031d63717d79080b530ffe0ce30f206eff78, e491215d0a937cae48cc5e9a2763ea43c85a4d11c183ec7c5b1ac559d2a585a5, ef13116bd66f31157b2f7db6369831d63f3098877e91c6163766dbe6da47eb7d, f48ee40d6de1859d6f3cabc841b631a55287c4282bfe974719fd89555672f54d, fdf8bcfb6dcc98252ae9a7d6389d27fa0c579d3a72021790b38bf3eb8b76c6af | 0 |

### `scarcity_hours_by_grid`

One grid's (ERCOT's or CAISO's) value of one scarcity measure in one hour: the USD 1,000 price counts and the grid's own scarcity signal.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 201873.

- **Time:** ts_utc is the hour's start, UTC; freq PT1H. An hour without a row is not held, not a zero.
- **Revisions:** Rewritten whole by each run (the window moves with the month); vintage is not filled.
- **Source:** erw:scarcity_hours_by_grid ERW derived table, the scarcity signal rule (docs/methods/scarcity_hours_by_grid.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/scarcity_hours_by_grid.md)
- **Method note:** [`docs/methods/scarcity_hours_by_grid.md`](../methods/scarcity_hours_by_grid.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Each grid's own scarcity signal beside the USD 1,000 price count (warehouse/derived/scarcity_hours_by_grid.py). Via the Energy Research Warehouse (ERW), table `scarcity_hours_by_grid`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: iso:ercot or iso:caiso | none | text | iso:caiso, iso:ercot | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-11-01T06:00:00Z to 2026-11-01T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 0, 1, 2, 3, 4 | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: <iso>_rtm or <iso>_dam on the price rows; empty on the own_signal rows | none | text | caiso_dam, caiso_rtm, ercot_dam, ercot_rtm | 44097 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The hub priced (HB_HUBAVG, TH_SP15_GEN-APND) on the price rows; empty on the own_signal rows | none | text | HB_HUBAVG, TH_SP15_GEN-APND | 44097 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:scarcity_hours_by_grid | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/scarcity_hours_by_grid.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-13T18:42:41Z, 2026-11-03T17:34:00Z, 2026-11-16T20:24:10Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 201873 |
| `x_detail` | Detail of the row: held=<intervals held> on rt_intervals_ge_1000; on own_signal, ERCOT's hourly mean adder (rtorpa_mean=<USD/MWh>) or CAISO's notices in force as type@region | none | text | for example eea_watch@CAISO Grid, held=4, rmo@CAISO Grid; 351 distinct | 130312: Empty on the rt_hour_ge_1000 and da_hour_ge_1000 rows, and on CAISO's own_signal hours with no notice in force |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `da_hour_ge_1000` | 1 when the day-ahead hour's price is at or above USD 1,000 per MWh, else 0 | count | 52608 | 2023-11-01T06:00:00Z | 2026-11-01T07:00:00Z |
| `own_signal` | 1 when the grid's own scarcity signal is in force in the hour (ERCOT: the real-time reserve price adder's hourly mean above zero; CAISO: an EEA or an alert in any part of the hour), else 0 | count | 44097 | 2023-11-01T06:00:00Z | 2026-10-08T23:00:00Z |
| `rt_hour_ge_1000` | 1 when the mean of the hour's held real-time intervals is at or above USD 1,000 per MWh, else 0 | count | 52584 | 2023-11-01T06:00:00Z | 2026-11-01T07:00:00Z |
| `rt_intervals_ge_1000` | The hour's 15-minute real-time intervals at or above USD 1,000 per MWh | count | 52584 | 2023-11-01T06:00:00Z | 2026-11-01T07:00:00Z |

### `shoulder_hours_monthly`

One grid's (ERCOT's or CAISO's) value of one shoulder-hours measure: for a local month's average day (P1M), one of a year's ten worst days (P1D), or a year (P1Y).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 27489.

- **Time:** P1M rows at the first day of the local month at 00:00:00Z; P1D rows at the local day; P1Y rows at the year's first day.
- **Revisions:** Rewritten whole by each run (the old file removed first); vintage is not filled.
- **Source:** erw:shoulder_hours EIA Form EIA-930 hourly demand and net generation by energy source, the per-BA workbooks (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx), and CAISO's supply by fuel (caiso_fuel_supply); read by this run from warehouse/raw/eia930_emissions/20261102T174348Z/20261102T174425.135109Z_00004_ERCO.xlsx; warehouse/raw/eia930_emissions/20261102T174348Z/20261102T174403.134912Z_00002_CISO.xlsx; warehouse/output/caiso_fuel_supply.csv (https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx)
- **Method note:** [`docs/methods/shoulder_hours.md`](../methods/shoulder_hours.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The shoulder hours by grid and month (docs/methods/shoulder_hours.md). Via the Energy Research Warehouse (ERW), table `shoulder_hours_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: iso:ercot, iso:caiso (EIA-930, to 2025-11) or iso:caiso_own (CAISO's own supply by fuel, from 2025-06), never mixed | none | text | iso:caiso, iso:caiso_own, iso:ercot | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-10-17T00:00:00Z; 254 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -9165.1917 to 122254.2917; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, count, hour, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1D, P1M, P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 27489 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 27489 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:shoulder_hours | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/shoulder_hours.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-03T17:32:48Z, 2026-11-03T17:33:05Z, 2026-11-03T17:33:08Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 27489 |

Variables (192):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `avg_battery_mw_h00` | The month's average day: mean battery output (positive discharging) in local hour 00 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h01` | The month's average day: mean battery output (positive discharging) in local hour 01 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h02` | The month's average day: mean battery output (positive discharging) in local hour 02 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h03` | The month's average day: mean battery output (positive discharging) in local hour 03 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h04` | The month's average day: mean battery output (positive discharging) in local hour 04 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h05` | The month's average day: mean battery output (positive discharging) in local hour 05 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h06` | The month's average day: mean battery output (positive discharging) in local hour 06 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h07` | The month's average day: mean battery output (positive discharging) in local hour 07 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h08` | The month's average day: mean battery output (positive discharging) in local hour 08 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h09` | The month's average day: mean battery output (positive discharging) in local hour 09 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h10` | The month's average day: mean battery output (positive discharging) in local hour 10 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h11` | The month's average day: mean battery output (positive discharging) in local hour 11 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h12` | The month's average day: mean battery output (positive discharging) in local hour 12 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h13` | The month's average day: mean battery output (positive discharging) in local hour 13 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h14` | The month's average day: mean battery output (positive discharging) in local hour 14 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h15` | The month's average day: mean battery output (positive discharging) in local hour 15 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h16` | The month's average day: mean battery output (positive discharging) in local hour 16 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h17` | The month's average day: mean battery output (positive discharging) in local hour 17 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h18` | The month's average day: mean battery output (positive discharging) in local hour 18 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h19` | The month's average day: mean battery output (positive discharging) in local hour 19 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h20` | The month's average day: mean battery output (positive discharging) in local hour 20 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h21` | The month's average day: mean battery output (positive discharging) in local hour 21 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h22` | The month's average day: mean battery output (positive discharging) in local hour 22 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_mw_h23` | The month's average day: mean battery output (positive discharging) in local hour 23 over the complete days | MW | 43 | 2024-11-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h00` | The month's average day: mean demand in local hour 00 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h01` | The month's average day: mean demand in local hour 01 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h02` | The month's average day: mean demand in local hour 02 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h03` | The month's average day: mean demand in local hour 03 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h04` | The month's average day: mean demand in local hour 04 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h05` | The month's average day: mean demand in local hour 05 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h06` | The month's average day: mean demand in local hour 06 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h07` | The month's average day: mean demand in local hour 07 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h08` | The month's average day: mean demand in local hour 08 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h09` | The month's average day: mean demand in local hour 09 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h10` | The month's average day: mean demand in local hour 10 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h11` | The month's average day: mean demand in local hour 11 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h12` | The month's average day: mean demand in local hour 12 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h13` | The month's average day: mean demand in local hour 13 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h14` | The month's average day: mean demand in local hour 14 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h15` | The month's average day: mean demand in local hour 15 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h16` | The month's average day: mean demand in local hour 16 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h17` | The month's average day: mean demand in local hour 17 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h18` | The month's average day: mean demand in local hour 18 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h19` | The month's average day: mean demand in local hour 19 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h20` | The month's average day: mean demand in local hour 20 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h21` | The month's average day: mean demand in local hour 21 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h22` | The month's average day: mean demand in local hour 22 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_demand_mw_h23` | The month's average day: mean demand in local hour 23 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h00` | The month's average day: mean net load (demand less solar and wind) in local hour 00 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h01` | The month's average day: mean net load (demand less solar and wind) in local hour 01 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h02` | The month's average day: mean net load (demand less solar and wind) in local hour 02 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h03` | The month's average day: mean net load (demand less solar and wind) in local hour 03 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h04` | The month's average day: mean net load (demand less solar and wind) in local hour 04 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h05` | The month's average day: mean net load (demand less solar and wind) in local hour 05 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h06` | The month's average day: mean net load (demand less solar and wind) in local hour 06 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h07` | The month's average day: mean net load (demand less solar and wind) in local hour 07 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h08` | The month's average day: mean net load (demand less solar and wind) in local hour 08 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h09` | The month's average day: mean net load (demand less solar and wind) in local hour 09 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h10` | The month's average day: mean net load (demand less solar and wind) in local hour 10 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h11` | The month's average day: mean net load (demand less solar and wind) in local hour 11 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h12` | The month's average day: mean net load (demand less solar and wind) in local hour 12 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h13` | The month's average day: mean net load (demand less solar and wind) in local hour 13 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h14` | The month's average day: mean net load (demand less solar and wind) in local hour 14 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h15` | The month's average day: mean net load (demand less solar and wind) in local hour 15 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h16` | The month's average day: mean net load (demand less solar and wind) in local hour 16 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h17` | The month's average day: mean net load (demand less solar and wind) in local hour 17 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h18` | The month's average day: mean net load (demand less solar and wind) in local hour 18 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h19` | The month's average day: mean net load (demand less solar and wind) in local hour 19 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h20` | The month's average day: mean net load (demand less solar and wind) in local hour 20 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h21` | The month's average day: mean net load (demand less solar and wind) in local hour 21 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h22` | The month's average day: mean net load (demand less solar and wind) in local hour 22 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_net_load_mw_h23` | The month's average day: mean net load (demand less solar and wind) in local hour 23 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h00` | The month's average day: mean solar output in local hour 00 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h01` | The month's average day: mean solar output in local hour 01 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h02` | The month's average day: mean solar output in local hour 02 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h03` | The month's average day: mean solar output in local hour 03 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h04` | The month's average day: mean solar output in local hour 04 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h05` | The month's average day: mean solar output in local hour 05 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h06` | The month's average day: mean solar output in local hour 06 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h07` | The month's average day: mean solar output in local hour 07 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h08` | The month's average day: mean solar output in local hour 08 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h09` | The month's average day: mean solar output in local hour 09 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h10` | The month's average day: mean solar output in local hour 10 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h11` | The month's average day: mean solar output in local hour 11 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h12` | The month's average day: mean solar output in local hour 12 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h13` | The month's average day: mean solar output in local hour 13 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h14` | The month's average day: mean solar output in local hour 14 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h15` | The month's average day: mean solar output in local hour 15 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h16` | The month's average day: mean solar output in local hour 16 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h17` | The month's average day: mean solar output in local hour 17 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h18` | The month's average day: mean solar output in local hour 18 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h19` | The month's average day: mean solar output in local hour 19 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h20` | The month's average day: mean solar output in local hour 20 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h21` | The month's average day: mean solar output in local hour 21 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h22` | The month's average day: mean solar output in local hour 22 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_solar_mw_h23` | The month's average day: mean solar output in local hour 23 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h00` | The month's average day: mean wind output in local hour 00 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h01` | The month's average day: mean wind output in local hour 01 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h02` | The month's average day: mean wind output in local hour 02 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h03` | The month's average day: mean wind output in local hour 03 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h04` | The month's average day: mean wind output in local hour 04 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h05` | The month's average day: mean wind output in local hour 05 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h06` | The month's average day: mean wind output in local hour 06 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h07` | The month's average day: mean wind output in local hour 07 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h08` | The month's average day: mean wind output in local hour 08 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h09` | The month's average day: mean wind output in local hour 09 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h10` | The month's average day: mean wind output in local hour 10 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h11` | The month's average day: mean wind output in local hour 11 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h12` | The month's average day: mean wind output in local hour 12 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h13` | The month's average day: mean wind output in local hour 13 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h14` | The month's average day: mean wind output in local hour 14 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h15` | The month's average day: mean wind output in local hour 15 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h16` | The month's average day: mean wind output in local hour 16 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h17` | The month's average day: mean wind output in local hour 17 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h18` | The month's average day: mean wind output in local hour 18 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h19` | The month's average day: mean wind output in local hour 19 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h20` | The month's average day: mean wind output in local hour 20 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h21` | The month's average day: mean wind output in local hour 21 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h22` | The month's average day: mean wind output in local hour 22 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_wind_mw_h23` | The month's average day: mean wind output in local hour 23 over the complete days | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_mwh_per_day` | CAISO: the month's curtailed solar plus curtailed wind over the days of the month held | MWh | 97 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `day_battery_discharge_mwh` | Worst day: the batteries' output in the shoulder's hours, discharging only | MWh | 49 | 2024-11-13T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_battery_hours` | Worst day: that discharge over the fleet's MW (hours at rated power) | hour | 43 | 2024-11-13T00:00:00Z | 2026-09-26T00:00:00Z |
| `day_battery_peak_mw` | Worst day: the batteries' highest output in the shoulder's hours | MW | 49 | 2024-11-13T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_evening_peak_mw` | Worst day: net load's highest hour from the shoulder's start to midnight | MW | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_fleet_mw` | Worst day: the month's battery fleet, MW | MW | 164 | 2019-01-01T00:00:00Z | 2026-09-26T00:00:00Z |
| `day_net_load_mean_mw` | Worst day: net load's mean over the day | MW | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_shoulder2_end_hour` | Worst day: the second measure's last hour | hour | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_shoulder2_hours` | Worst day: the second measure's length | hour | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_shoulder2_hours_needed` | Worst day: the second measure's energy over the month's fleet MW | hour | 164 | 2019-01-01T00:00:00Z | 2026-09-26T00:00:00Z |
| `day_shoulder2_mwh_above_midpoint` | Worst day: the second measure's energy above the midpoint | MWh | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_shoulder2_start_hour` | Worst day: the second measure's first hour | hour | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_shoulder_hours` | Worst day: the shoulder's length | hour | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_shoulder_hours_needed` | Worst day: its shoulder energy above the mean over the month's fleet MW | hour | 164 | 2019-01-01T00:00:00Z | 2026-09-26T00:00:00Z |
| `day_shoulder_mwh_above_mean` | Worst day: the shoulder's energy above the day's own mean | MWh | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_shoulder_runs_to_midnight` | Worst day: 1 when the shoulder runs to midnight, else 0 | count | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `day_shoulder_start_hour` | Worst day: the shoulder's first hour | hour | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `days_held` | The month's complete days (every hour of demand, solar and wind held) | count | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `days_in_month` | The days of the month | count | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `evening_peak_hour` | The average day's evening peak: net load's highest hour from the shoulder's start to midnight, local hour | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `evening_peak_mw` | Net load at the average day's evening peak | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `fleet_hours` | The battery fleet's average duration: its MWh over its MW | hour | 190 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `fleet_mw` | The grid's operating battery fleet, power (EIA-860M, storage_buildout_monthly) | MW | 190 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `fleet_mwh` | The grid's operating battery fleet, energy (EIA-860M, storage_buildout_monthly) | MWh | 190 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `midday_low_hour` | The average day's hour of lowest net load, local | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `midday_surplus_hours` | Length of the midday surplus: the run of hours around net load's lowest hour in which net load is below its daily mean | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `midday_surplus_mwh` | Energy of the midday surplus: the sum of the daily mean less net load over those hours | MWh | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `net_load_mean_mw` | Net load's daily mean on the average day | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder2_end_hour` | Second measure: last hour of that run | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder2_hours` | Second measure: length of the run around the evening peak above the midpoint | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder2_hours_covered` | Second measure: the smaller of the run's length and the fleet's average duration | hour | 190 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `shoulder2_hours_needed` | Second measure: its energy above the midpoint over the fleet's MW | hour | 190 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `shoulder2_level_mw` | Second measure: the midpoint between net load's daily mean and the evening peak | MW | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder2_mwh_above_midpoint` | Second measure: net load less the midpoint, summed over the run | MWh | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder2_runs_to_midnight` | Second measure: 1 when the run reaches midnight, else 0 | count | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder2_start_hour` | Second measure: first hour of the run around the evening peak in which net load is above the midpoint between its daily mean and the peak | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder_end_hour` | The evening shoulder's end: the first hour, after net load has risen above its daily mean, in which it is back at or below it (midnight if never) | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder_hours` | Length of the evening shoulder | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder_hours_covered` | The smaller of the shoulder's length and the fleet's average duration: hours the fleet can run at rated power through it | hour | 190 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `shoulder_hours_needed` | The shoulder's energy above the mean over the fleet's MW: hours a fleet of that power would run at rated power to deliver it | hour | 190 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `shoulder_mwh_above_mean` | The shoulder's energy: net load less its daily mean, summed over the shoulder's hours in which net load is above the mean | MWh | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder_runs_to_midnight` | 1 when net load stays above its mean to midnight and the shoulder ends there, else 0 | count | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `shoulder_start_hour` | The evening shoulder's start: the first hour after solar's highest hour in which solar is below half of that value | hour | 192 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `worst_rank` | The day's rank among the year's ten complete days with the most shoulder energy above the day's own mean (1 the worst) | count | 170 | 2019-01-01T00:00:00Z | 2026-10-17T00:00:00Z |
| `year_days_ranked` | Year: complete days of 24 local hours with a shoulder of at least one hour, the days that could be ranked | count | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_end_fleet_hours` | Year, at its last month held that has a fleet: the battery fleet's average duration: its MWh over its MW | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_end_fleet_mw` | Year, at its last month held that has a fleet: the grid's operating battery fleet, power (EIA-860M, storage_buildout_monthly) | MW | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_end_fleet_mwh` | Year, at its last month held that has a fleet: the grid's operating battery fleet, energy (EIA-860M, storage_buildout_monthly) | MWh | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_curtailed_mwh_per_day` | Year, mean over its months held: cAISO: the month's curtailed solar plus curtailed wind over the days of the month held | MWh | 9 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_midday_surplus_hours` | Year, mean over its months held: length of the midday surplus: the run of hours around net load's lowest hour in which net load is below its daily mean | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_midday_surplus_mwh` | Year, mean over its months held: energy of the midday surplus: the sum of the daily mean less net load over those hours | MWh | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder2_hours` | Year, mean over its months held: second measure: length of the run around the evening peak above the midpoint | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder2_hours_covered` | Year, mean over its months held: second measure: the smaller of the run's length and the fleet's average duration | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder2_hours_needed` | Year, mean over its months held: second measure: its energy above the midpoint over the fleet's MW | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder2_mwh_above_midpoint` | Year, mean over its months held: second measure: net load less the midpoint, summed over the run | MWh | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder2_runs_to_midnight` | Year, mean over its months held: second measure: 1 when the run reaches midnight, else 0 | ratio | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder_hours` | Year, mean over its months held: length of the evening shoulder | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder_hours_covered` | Year, mean over its months held: the smaller of the shoulder's length and the fleet's average duration: hours the fleet can run at rated power through it | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder_hours_needed` | Year, mean over its months held: the shoulder's energy above the mean over the fleet's MW: hours a fleet of that power would run at rated power to deliver it | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder_mwh_above_mean` | Year, mean over its months held: the shoulder's energy: net load less its daily mean, summed over the shoulder's hours in which net load is above the mean | MWh | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder_runs_to_midnight` | Year, mean over its months held: 1 when net load stays above its mean to midnight and the shoulder ends there, else 0 | ratio | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_mean_shoulder_start_hour` | Year, mean over its months held: the evening shoulder's start: the first hour after solar's highest hour in which solar is below half of that value | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_months_held` | Year: months held | count | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_worst10_days` | Year: worst days ranked (up to ten) | count | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_worst10_days_with_battery` | Year: of the ten worst days, those whose every hour holds a battery output | count | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_worst10_max_shoulder_hours_needed` | Year: the largest shoulder hours needed among the ten worst days | hour | 15 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `year_worst10_mean_battery_hours` | Year: mean over the ten worst days of the hours the batteries ran at rated power in the shoulder | hour | 2 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `year_worst10_mean_shoulder2_hours` | Year: mean length of the second measure over the ten worst days | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_worst10_mean_shoulder2_hours_needed` | Year: mean hours needed by the second measure over the ten worst days | hour | 15 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `year_worst10_mean_shoulder_hours` | Year: mean shoulder length over the ten worst days | hour | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `year_worst10_mean_shoulder_hours_needed` | Year: mean shoulder hours needed over the ten worst days | hour | 15 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `year_worst10_mean_shoulder_mwh_above_mean` | Year: mean shoulder energy above the day's mean over the ten worst days | MWh | 17 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

### `state_generation_mix_monthly`

One state's (or the nation's) net generation from one group of energy sources in one month.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 108125.

- **Time:** ts_utc is the first of the month at 00:00:00Z; freq P1M.
- **Revisions:** Merged by (entity, variable, ts_utc): each run replaces the rows it writes and keeps the rest.
- **Source:** erw:generation_mix ERW derived table, generation mix method (docs/methods/generation_mix.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/generation_mix.md)
- **Method note:** [`docs/methods/generation_mix.md`](../methods/generation_mix.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Generation mix by state (docs/methods/generation_mix.md). Via the Energy Research Warehouse (ERW), table `state_generation_mix_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia:<state>, or eia:US for the nation | none | text | for example eia:AK, eia:AL, eia:AR; 53 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2001-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 308 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -196301.07 to 209842940.95; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 53 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 108125 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 108125 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:generation_mix | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/generation_mix.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-27T08:14:19Z, 2026-10-22T14:48:54Z, 2026-10-23T14:45:12Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 108125 |

Variables (9):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `net_generation_coal_mwh` | Net generation from coal (EIA's COW) | MWh | 15258 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_generation_hydro_mwh` | Net generation from conventional hydro (EIA's HYC) | MWh | 15171 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_generation_natural_gas_mwh` | Net generation from natural gas (EIA's NG) | MWh | 15716 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_generation_not_itemized_mwh` | EIA's all-fuels total less the groups, where not zero to the MWh | MWh | 1081 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_generation_nuclear_mwh` | Net generation from nuclear (EIA's NUC) | MWh | 9560 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_generation_oil_and_other_mwh` | Net generation from oil and other sources (EIA's PET, OOG, HPS and OTH) | MWh | 16104 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_generation_other_renewables_mwh` | Net generation from geothermal and biomass (EIA's GEO and BIO) | MWh | 15306 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_generation_solar_mwh` | Net generation from utility-scale solar (EIA's SUN; small-scale solar not included) | MWh | 8649 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `net_generation_wind_mwh` | Net generation from wind (EIA's WND) | MWh | 11280 | 2001-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `state_large_load_laws`

One US state law or bill of the 2025 and 2026 sessions that sets terms for large loads (data centers and others) or tells the utilities or the commission to set them.

Shape: events. Keys: `event_id`. License: public; tier: model_extracted. Rows read on 2026-11-20: 27.

- **Time:** event_date is the status date printed, else the day the document was read (x_date_kind says which).
- **Revisions:** Rewritten whole from the research file by each run (the old file removed first).
- **Source:** research:large_load_2026-11-13, docs/research/large_load/legislation_2026-11-13.csv (window P4 of the portable laptop, sessions 5300 to 5304; method https://github.com/SamuelEnrique/erw/blob/main/docs/research/large_load/README.md); each row's source_url is the document it was read in. No request is made by this connector. (https://github.com/SamuelEnrique/erw/blob/main/docs/research/large_load/README.md)
- **Method note:** [`docs/methods/large_load_research.md`](../methods/large_load_research.md)
- **Cite as:** US utilities, state commissions and legislatures, read by the ERW's research pass. Large-load rules, their changes and the states' laws (docs/research/large_load, 13 and 14 November 2026). Via the Energy Research Warehouse (ERW), table `state_large_load_laws`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: lllaw:<law_id> | none | text | for example lllaw:laws_midwest_northeast-01, lllaw:laws_midwest_northeast-02, lllaw:laws_midwest_northeast-03; 27 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2025-03-25, 2025-04-17, 2025-04-24, 2025-05-12, 2025-05-20, 2025-06-14, 2025-06-16, 2025-07-11, 2025-08-28, 2026-02-26, 2026-03-19, 2026-03-23, 2026-03-24, 2026-04-08, 2026-04-10, 2026-04-14, 2026-05-07, 2026-05-12, 2026-05-29, 2026-06-04, 2026-07-07, 2026-08-26, 2026-11-13, 2026-11-14 | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: large_load_law on every row | none | text | large_load_law | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: The state's legislature | none | text | AL legislature, CT legislature, DE legislature, FL legislature, IA legislature, ID legislature, KS legislature, MA legislature, MD legislature, MI legislature, MN legislature, MO legislature, NE legislature, NJ legislature, NY legislature, OH legislature, OR legislature, PA legislature, SC legislature, SD legislature, UT legislature, VA legislature, VT legislature, WI legislature, WV legislature | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 27 |
| `mw` | The capacity involved, in megawatts. Here: Not filled: the files print sizes as phrases, kept in x_threshold_mw | MW | empty | no cell holds a value | 27 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise. Here: Not filled: no cell holds a value | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 27 |
| `currency` | The currency of the price, as an ISO 4217 code (USD). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 27 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: The bill's status as printed: introduced, passed one chamber, passed, enacted, in effect, vetoed or died | none | text | died, enacted, in effect, introduced, passed, passed one chamber, vetoed | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | research:large_load_2026-11-13 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://alison.legislature.state.al.us/files/pdf/SearchableInstruments/2026RS/SB270-enr.pdf, https://code.wvlegislature.gov/signed_bills/2025/2025-RS-HB2014-SUB%20ENR_signed.pdf, https://docs.legis.wisconsin.gov/document/amends/2025/REG/AB840-ASA1.pdf; 27 distinct | 0 |
| `x_law_id` | The research file's id of the law (the source's name: law_id) | none | text | for example laws_midwest_northeast-01, laws_midwest_northeast-02, laws_midwest_northeast-03; 27 distinct | 0 |
| `x_group` | The research group of states the law was read in (the source's name: group) | none | text | laws_midwest_northeast, laws_south_west | 0 |
| `x_state` | The state, two-letter code (the source's name: state) | none | text | AL, CT, DE, FL, IA, ID, KS, MA, MD, MI, MN, MO, NE, NJ, NY, OH, OR, PA, SC, SD, UT, VA, VT, WI, WV | 0 |
| `x_bill` | The bill or act as the legislature numbers it (the source's name: bill) | none | text | for example 2026 Acts of Assembly, chapters 377 and 378 (Code of Virginia 56-596.7), A. 11560 (same as S. 10642), Responsible Data Center Development Act, A. 796 (Fourth Reprint), P.L. 2026, c.32 (Data Center Fair Share Act); 27 distinct | 0 |
| `x_session` | The legislative session (the source's name: session) | none | text | 101st Legislative Session, 2026, 102nd Legislature, 2024 regular session, 103rd General Assembly, 2025 first regular session, 103rd General Assembly, 2026 second regular session, 109th Legislature, 2026 second session, 126th General Assembly, 2025, 136th General Assembly, 2025-2026, 153rd General Assembly (2025-2026), 194th General Court (2025-2026), 2025 General Session, 2025 Regular Session (83rd Legislative Assembly), 2025 regular session, 2025-2026 Legislature, 2025-2026 Regular Session, 2025-2026 legislative session, 2026 Regular Session, 2026 Regular Session (68th Legislature, second regular session), 2026 regular session, 2026-2027 session, 91st General Assembly, 2026 session, 94th Legislature, 2025 First Special Session, February Session, 2026 | 0 |
| `x_title` | The bill's or act's own title (the source's name: title) | none | text | for example AN ACT CONCERNING COLOCATED ELECTRIC SUPPLIERS AND LARGE ELECTRIC LOAD CUSTOMERS., AN ACT TO AMEND THE SOUTH CAROLINA CODE OF LAWS BY ENACTING THE "SOUTH CAROLINA ENERGY SECURITY ACT", AN ACT TO AMEND TITLE 26 OF THE DELAWARE CODE RELATING TO LARGE ENERGY USE FACILITIES.; 27 distinct | 0 |
| `x_status_date` | The status date as printed (the source's name: status_date) | none | text | 2025-03-25, 2025-04-17, 2025-04-24, 2025-05-12, 2025-05-20, 2025-06-14, 2025-06-16, 2025-07-11, 2025-08-28, 2026-02-26, 2026-03-19, 2026-03-23, 2026-03-24, 2026-04-08, 2026-04-10, 2026-04-14, 2026-05-07, 2026-05-12, 2026-05-29, 2026-06-04, 2026-07-07, 2026-08-26, not published | 0 |
| `x_date_kind` | Which date event_date is: stated date (printed in the document) or date read | none | text | date read, stated date | 0 |
| `x_effective_date` | The law's effective date as printed, or not published (the source's name: effective_date) | none | text | 2025-04-17, 2025-05-07, 2025-05-12, 2025-06-01, 2025-06-16, 2025-07-11, 2025-08-28, 2026-07-01, 2026-07-07, 2026-08-26, 2026-10-01, not published | 0 |
| `x_status_cite` | Where the status and dates are printed: the document's address and the words (the source's name: status_cite) | none | text | for example https://docs.legis.wisconsin.gov/2025/proposals/ab840 (read 2026-11-14) p. 1, History, 1/20/2026 Asm.: "Read a third time and passed, Ayes 53, Noes 44, Paired 2" \| https://docs.legis.wisconsin.gov/2025/proposals/ab840 (read 2026-11-14) p. 1, History, 1/20/2026 Asm.: "Assembly Substitute Amendment 1 adopted" \| https://docs.legis.wisconsin.gov/2025/proposals/ab840 (read 2026-11-14) p. 1, History, 3/23/2026 Sen.: "Failed to concur in pursuant to Senate Joint Resolution 1" \| p. 1, heading: "ASSEMBLY SUBSTITUTE AMENDMENT 1, TO ASSEMBLY BILL 840", https://legis.delaware.gov/BillDetail/143381 (read 2026-11-14) p. 1, Status: "Signed 8/26/26" \| https://legis.delaware.gov/BillDetail/143381 (read 2026-11-14) p. 1, Volume:Chapter: "85:440" \| https://legis.delaware.gov/BillDetail/143381 (read 2026-11-14) p. 1, Effective Date: "8/26/26" \| p. 14, Section 6: "Section 6. This Act takes effect upon enactment.", https://legislature.idaho.gov/sessioninfo/2026/legislation/H0911/ (read 2026-11-13) p. 1, bill history: "Reported Signed by Governor on April 10, 2026" \| https://legislature.idaho.gov/sessioninfo/2026/legislation/H0911/ (read 2026-11-13) p. 1, bill history: "Session Law Chapter 335" \| https://legislature.idaho.gov/sessioninfo/2026/legislation/H0911/ (read 2026-11-13) p. 1, bill history: "Effective: 07/01/2026" \| p. 1, History: "[61-335, added 2026, ch. 335, sec. 1, p. 1315.]"; 27 distinct | 0 |
| `x_threshold_mw` | The size of load the law applies to, as the text's phrase (the source's name: threshold_mw) | none | text | 100 MW: new service expected to reach a cumulative demand of 100 MW or more, or added service of 100 MW or more, within five years of the requested start date, 150 MW expected total peak demand at one or more contiguous parcels, for a data processing center under Section 40-9B-3 operating solely for data processing, 20 MW: a facility that uses or is able to use 20 MW or more and is primarily engaged in a service under NAICS code 518210, 25 MW contracted or measured demand with an anticipated or measured average annual load factor of 75 percent or more (contracted defense facilities excluded), 50 MW anticipated monthly peak load (highest 15-minute average) at a single location; colocated customers at one location count together; loads at multiple locations are not aggregated, 50 MW at one point of delivery for a 'transformational customer' (with 500 new employees, $100,000,000 investment and a Department of Commerce designation); an existing customer above 20 MW contract demand signing a contract of five years or more is a 'qualifying customer', 50 MW: an increase of 50 MW or more in a service entrance's cumulative power requirement in any consecutive 60-month period, under a service contract entered into on or after July 1, 2026, Senate committee version only: a data center requires peak demand capacity greater than 25 MW at a single building or location; the self-supply duty applies to new data centers above 250 MW aggregate monthly maximum demand, a commercial data center has a peak demand of 25 MW or greater, a data center is a facility designed to have a load of not less than 20 MW, a data center uses or is able to use 20 MW or more and provides data processing and hosting services (NAICS 518210), a data center with a peak demand of 10 MW or greater, a large data center has a peak demand of 20 MW or more (5 MW for the covered data center labor and reporting duties), a large data center has an information-technology load above 20 GWh of consumption or 100 MW of demand (facilities under common ownership aggregated), a large electric load customer has a peak demand of not less than 50 MW, a large energy use facility uses or is projected to use 75 MW or more of monthly maximum demand at a load factor of 85 percent or more, or 100 MW or more of monthly maximum instantaneous demand, or 30 MW or more if primarily a data processing and hosting service (NAICS 518210); facilities may be aggregated; bulk petroleum facilities excluded, a retail load customer requesting a new or expanded interconnection where the total load at a single site would exceed 20 MW, customers reasonably projected to have an annual peak demand of 100 MW or more, for electrical corporations serving more than 250,000 customers; 50 MW or more for those serving 250,000 or fewer customers as of 1 January 2025, large load customer (new Part III): aggregate monthly demand of at least 25 MW and a load factor above 60 percent, excluding water and sewage companies, manufacturing, hospitals, district energy, agriculture; the 4-212 rate schedule threshold lowered from 100 MW to 25 MW, large load customer: aggregate monthly demand of at least 100 MW and a load factor over 80 percent; the specific rate schedule covers more than 100 MW at a single location or more than 100 MW aggregated contract capacity (lowered to 25 MW by Chapter 353 of 2026), no MW figure for the very large customer class: the Commission defines it for each utility by order by 15 December 2026; a data center is defined as a facility designed to have a load of 100 MW or more; the qualified large-scale data center fee starts at 100 MW of peak demand, no general size threshold for microgrid customers; the negotiation requirement does not apply to microgrid districts producing 300 MW or more; a high impact data center (special property valuation) has an aggregate critical IT load of 90 MW or more, not published, set by the BPU for each utility at not greater than 50 MW, with related data centers aggregated, would lower the 393.130.7 threshold for the larger electrical corporations from 100 MW to 50 MW of annual peak demand; the emergency curtailment duty applies above 25 MW of peak demand | 0 |
| `x_threshold_mw_cite` | Where the size is printed: page, section and words (the source's name: threshold_mw_cite) | none | text | for example p. 1, 56-596.7(A): "means a retail electric service customer that has a contracted or measured electric demand of 25 megawatts or greater and an anticipated or measured average annual electric load factor of 75 percent or greater", p. 1, 61-335(1)(c): "Results in an increase in a cumulative power requirement of such service entrance of fifty (50) megawatts or more in any consecutive sixty (60) month period" \| p. 1, 61-335(1)(c)(ii): "Is subject to a service contract with a public utility that was entered into on or after July 1, 2026.", p. 1, Sec. 2(1): "Large load customer means a retail load customer requesting a new or ... expanded interconnection where the total load at a single site would exceed twenty megawatts;"; 27 distinct | 0 |
| `x_requirements` | The duties the law sets, by topic (cost allocation, minimum term, collateral and others), as printed (the source's name: requirements) | none | text | for example collateral: the Commission's regulations must govern retail tariff terms that safeguard existing customers, including deposits or other financial security from a commercial data center [p. 19, tariff terms: "STRANDED INVESTMENT AND COST SHIFTING, INCLUDING ALL OF THE" \| p. 19, tariff terms (i): "(I) DEPOSITS OR OTHER FINANCIAL SECURITY REQUIRED"] \|\| minimum term: minimum contract terms and minimum load obligations requiring a data center that ceases operations early or engages in economic peak-shaving to take a minimum level of service for a minimum number of years, secured by a letter of credit or comparable instrument [p. 19, tariff terms (iii): "(III) MINIMUM CONTRACT TERMS AND MINIMUM LOAD" \| p. 19, tariff terms (iii): "OF SERVICE FOR A MINIMUM NUMBER OF YEARS SUFFICIENT TO" \| p. 19, tariff terms (iii): "THIS SUBPARAGRAPH BY A LETTER OF CREDIT OR OTHER"] \|\| exit fee: exit fees or early termination fees [p. 19, tariff terms (v): "(V) EXIT FEES OR EARLY TERMINATION FEES."] \|\| cost allocation: a prohibition on shifting to other customers costs caused in whole or part by a commercial data center's interconnection, service or load [p. 21, Section 4: "SECTION 4. PROHIBITION ON COST SHIFTING AND RECOVERY OF COSTS."] \|\| curtailment or backup generation: curtailment of a commercial data center's load under regional transmission organization curtailment programs, and curtailment standards [p. 20, regulations (2): "(2) CURTAILMENT OF A COMMERCIAL DATA CENTER'S LOAD UNDER"], commission rulemaking: A public utility serves a new large load only under a commission-approved service contract, filed with a no harm test; the commission approves or denies it within 270 days [p. 1, 61-335(2): "A public utility shall provide service to a new large load only pursuant to a commission-approved service contract." \| p. 1, 61-335(3), (4): "Such filing shall include a no harm test ... The commission shall review and approve or deny a new large load service contract within two hundred seventy (270) days of receiving such filing by the public utility."] \|\| cost allocation: The new large load funds its full cost of service, including its share of generation, transmission, substation and distribution investments needed only because of it; the commission reviews the contract's rates in each general rate case [p. 1, 61-335(4)(b): "The new large load is responsible for funding its full cost of service, including its share of generation, transmission, substation, and distribution infrastructure investments" \| p. 1, 61-335(7)(a): "In each general rate case filed by a public utility, the commission shall review the rates, charges, and cost recovery mechanisms applicable to an approved service contract"] \|\| collateral: Approval is conditioned on financial security, in a form and amount the commission approves, reasonably sufficient to protect the utility and its other customers from stranded or unrecoverable costs [p. 1, 61-335(6): "Approval of a service contract shall be conditioned on the new large load furnishing financial security, in a form and amount approved by the commission"] \|\| other: A new large load may not change its status by artifice, such as splitting its load among service entrances [p. 1, 61-335(5): "A new large load shall not change its status as such by means of artifice"], commission rulemaking: each investor-owned electric company and electric cooperative must submit a specific rate schedule for large load customers by 1 September 2026; the PSC must adopt regulations by 1 June 2026 on notice and deadlines for load studies and contract terminations, forms of collateral, and study completion [p. 17, PUA 4-212(c)(1): "SHALL SUBMIT TO THE COMMISSION FOR APPROVAL A SPECIFIC RATE SCHEDULE FOR LARGE LOAD CUSTOMERS." \| p. 19, PUA 4-212(f)(1): "ADOPT REGULATIONS TO CARRY OUT THIS SECTION." \| p. 19, PUA 4-212(f)(2)(ii): "COMMON FORMS OF ACCEPTABLE COLLATERAL TO SATISFY THE REQUIREMENTS OF"] \|\| minimum bill: in approving a schedule the PSC must consider minimum billing demand for distribution and transmission at a high percentage of contract capacity, long-term commitments and exit fees, guarantee or collateral requirements, and penalties if a project is delayed or cancelled after buildout begins [p. 18, PUA 4-212(d)(2)(ii): "AND TRANSMISSION SERVICE THAT IS A HIGH PERCENTAGE OF A LARGE LOAD" \| p. 18, PUA 4-212(d)(2)(iii): "(III) LONG-TERM CONTRACTUAL COMMITMENTS AND EXIT FEES;" \| p. 18, PUA 4-212(d)(2)(iv): "(IV) GUARANTEE OR COLLATERAL REQUIREMENTS; AND"] \|\| cost allocation: the schedule should require the customer to cover the just and reasonable costs of transmission or distribution buildout to interconnect or serve it, payable over multiple years of the contract not exceeding 5 years [p. 18, PUA 4-212(e): "THE COSTS ASSOCIATED WITH ANY ELECTRIC TRANSMISSION OR DISTRIBUTION SYSTEM BUILDOUT REQUIRED UNDER SUBSECTION (D)(1) OF THIS SECTION MAY BE PAID OVER MULTIPLE YEARS OF A LARGE LOAD CUSTOMER'S CONTRACT FOR SERVICE, NOT TO EXCEED 5 YEARS."] \|\| interconnection study: before signing a contract under the schedule the customer must request a load study to set its contract capacity and pay its fees, designate a site, and own or control the land [p. 19, PUA 4-212: "NECESSARY CONTRACT CAPACITY FOR THE LARGE LOAD CUSTOMER AND PAY ANY" \| p. 19, PUA 4-212: "APPLICABLE FEES ASSOCIATED WITH THE STUDY;"]; 27 distinct | 0 |
| `x_source_title` | The title of the document the law was read in (the source's name: source_title) | none | text | for example 2025 Session Laws of Kansas, Chapter 124: Senate Bill 98, Kansas Secretary of State, Act No. 207, Public Acts of 2024 (Enrolled House Bill No. 4906), Michigan Legislature, Assembly Bill A11560 (2025-2026), New York State Legislature (legislation.nysenate.gov); 27 distinct | 0 |
| `x_date_read` | The day the document was read (the source's name: date_read) | none | date | 2026-11-13, 2026-11-14 | 0 |
| `x_notes` | The research's notes on the law (the source's name: notes) | none | text | for example A 2024-session act approved 17 January 2025 and in effect in 2025. It sets terms for data centers' electric service as conditions of a sales and use tax exemption, not as a utility rule. The companion Act No. 208 of 2024 (Enrolled H.B. 5600, effective 2 April 2025) was opened but not read for terms. No 2025 or 2026 Michigan act on large loads was found (one web search; a Michigan moratorium bill is a news lead only)., Amends PUA 4-212 (from Chapter 625 of 2025) and adds Part III, 7-232 to 7-234; it keeps the 1 September 2026 rate schedule filing date (4-212(c)(1)(i), p.34). Dataset row pjm_east-03 (proposed COMAR 20.96.01, RM 93) cites this chapter for its threshold. Effective date: the chapter has several effective-date sections (July 1, 2026 for listed sections; the rest from enactment as an emergency measure); which section carries these provisions was not traced, so not published here. Existing large load customers whose load does not expand by more than 25 MW are outside the schedule (4-212(c)(2)(iii))., Coordinator's lead (a Governor's release: HB 233 signed 26 August 2026) confirmed on the General Assembly's bill page: House Substitute 1 for HB 233, Signed 8/26/26, Volume:Chapter 85:440, Effective Date 8/26/26. The text read is the engrossment of HS 1 as amended (House Amendments 1 and 3, Senate Amendment 2). The bill page's synopsis says rate applications are due within 180 days of the effective date; the engrossed Section 6 says within 180 days of the finalization of the Commission's regulations, and the engrossed text is quoted. No dataset statewide row exists for Delaware (Delmarva's tariff is Exelon's, whose site terms bar automated access).; 27 distinct | 0 |

### `subregion_demand_growth`

One EIA-930 sub-region's value of one demand measure (peak, average, energy, hours, growth) for one UTC calendar year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 3918.

- **Time:** ts_utc is the year's first hour (UTC); freq P1Y; years are UTC calendar years; x_at is the peak hour's start (UTC).
- **Revisions:** Rewritten whole as one snapshot by each run of the builder from the EIA-930 sub-region hourly tables; vintage is not filled.
- **Source:** eia:electricity/rto/region-sub-ba-data U.S. Energy Information Administration, Hourly Electric Grid Monitor, demand by subregion
- **Method note:** [`docs/methods/subregion_demand_growth.md`](../methods/subregion_demand_growth.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Every EIA-930 sub-region's peak and average demand by year (docs/methods/subregion_demand_growth.md). Via the Energy Research Warehouse (ERW), table `subregion_demand_growth`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930_subba:<parent>:<subba>, the source table's | none | text | for example eia930_subba:BHBA:BASI, eia930_subba:BHBA:SDE, eia930_subba:BHBA:WYE; 90 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z, 2026-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -41.0359 to 178311777.0; 2655 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3918 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The sub-region's code and name with its parent, from the source table, not a pricing node | none | text | for example AEPW American Electric Power West (Southwest Power Pool), Allegheny Power zone (PJM Interconnection, LLC), American Electric Power zone (PJM Interconnection, LLC); 90 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:subregion_demand_growth | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/subregion_demand_growth.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-05T22:06:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3918 |
| `x_at` | The peak hour's start, UTC | none | utc time | 2019-01-03T01:00:00Z to 2025-12-30T22:00:00Z; 360 distinct | 3366: Empty on every variable but peak_mw |
| `x_parent` | The sub-region's parent balancing authority, EIA-930 code | none | text | BHBA, CISO, ERCO, ISNE, MISO, NYIS, PJM, PNM, SWPP, SWPW | 0 |
| `x_subba` | The sub-region's EIA-930 code | none | text | for example 0001, 0004, 0006; 90 distinct | 0 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `avg_growth_pct` | Growth of avg_mw from the year before, percent | pct | 466 | 2020-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `avg_mw` | The mean demand over the hours used | MW | 552 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `energy_mwh` | The demand summed over the hours used | MWh | 552 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `hours_in_year` | Hours in the year | count | 665 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `hours_used` | Hours used (held and passing the screen of impossible hours) | count | 665 | 2019-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `peak_growth_pct` | Growth of peak_mw from the year before, percent | pct | 466 | 2020-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `peak_mw` | The year's highest used hour of demand | MW | 552 | 2019-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

