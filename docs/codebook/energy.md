# Codebook: energy

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 8 public tables (2 entities, 1 events, 5 series; tiers: 1 derived, 2 model_extracted, 5 source); 0 documented in full.

- [`energy_charts_belgium_hourly`](#energy_charts_belgium_hourly): Energy-Charts (Fraunhofer ISE), Belgium's public net electricity production by type, load, residual load and cross-border trading, an hour, 2019-12-31T23:00:00Z to 2026-10-23T21:00:00Z (session 2253)
- [`energy_charts_central_europe`](#energy_charts_central_europe): Energy-Charts (Fraunhofer ISE), Austria's, Switzerland's and Czechia's public net electricity production by type, load, residual load and cross-border trading, 2022-12-31T23:00:00Z to 2026-10-23T21:00:00Z (session 2272)
- [`energy_charts_italy_power`](#energy_charts_italy_power): Energy-Charts (Fraunhofer ISE), Italy's public net electricity production by type, load and cross-border trading, 2019-12-31 to 2026-10-22 (session 2281)
- [`energy_charts_portugal_power`](#energy_charts_portugal_power): Energy-Charts (Fraunhofer ISE), Portugal's public net electricity production by type, load and cross-border trading, 2020-01-01 to 2026-10-22 (session 2282)
- [`energy_charts_southeast_europe_daily`](#energy_charts_southeast_europe_daily): Energy-Charts (Fraunhofer ISE), public net electricity production by type, load, residual load and cross-border trading for Hungary, Romania, Greece and Bulgaria, a UTC day, 2020-01-01 to 2026-10-22 (session 2259)
- [`energy_companies`](#energy_companies): energy companies, the company database (tool 10): companies the Thesis Builder (tool 27) researched, and every party of the deal tracker's deals (energy_deals)
- [`energy_deals`](#energy_deals): Energy deals extracted from scored news stories (platform tool 6)
- [`energy_projects`](#energy_projects): Energy projects for the project map: EIA-860M generators and ISO interconnection queue positions (derived, platform tool 3)

### `energy_charts_belgium_hourly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 908600.

- **Source:** energy_charts:public_power_be Energy-Charts.info (Fraunhofer Institute for Solar Energy Systems ISE), public net electricity production, Belgium (https://energy-charts.info/charts/power/chart.htm?l=en&c=BE)
- **Method note:** [`docs/methods/energy_charts_belgium_hourly.md`](../methods/energy_charts_belgium_hourly.md)
- **Cite as:** Energy-Charts.info (Fraunhofer ISE). Public net electricity production, Belgium (API public_power). Via the Energy Research Warehouse (ERW), table `energy_charts_belgium_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | energy_charts:be:battery, energy_charts:be:biomass, energy_charts:be:cross_border_electricity_trading, energy_charts:be:fossil_gas, energy_charts:be:fossil_oil, energy_charts:be:hydro_pumped_storage, energy_charts:be:hydro_pumped_storage_consumption, energy_charts:be:hydro_run_of_river, energy_charts:be:load, energy_charts:be:nuclear, energy_charts:be:others, energy_charts:be:residual_load, energy_charts:be:solar, energy_charts:be:waste, energy_charts:be:wind_offshore, energy_charts:be:wind_onshore | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-12-31T23:00:00Z to 2026-10-23T21:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -5343.2 to 13515.7; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | BE | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 908600 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | Belgium: Battery, Belgium: Biomass, Belgium: Cross border electricity trading, Belgium: Fossil gas, Belgium: Fossil oil, Belgium: Hydro Run-of-River, Belgium: Hydro pumped storage, Belgium: Hydro pumped storage consumption, Belgium: Load, Belgium: Nuclear, Belgium: Others, Belgium: Residual load, Belgium: Solar, Belgium: Waste, Belgium: Wind offshore, Belgium: Wind onshore | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | energy_charts:public_power_be | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.energy-charts.info/public_power?country=be&start=2020-01-01&end=2020-12-31, https://api.energy-charts.info/public_power?country=be&start=2021-01-01&end=2021-12-31, https://api.energy-charts.info/public_power?country=be&start=2022-01-01&end=2022-12-31, https://api.energy-charts.info/public_power?country=be&start=2023-01-01&end=2023-12-31, https://api.energy-charts.info/public_power?country=be&start=2024-01-01&end=2024-12-31, https://api.energy-charts.info/public_power?country=be&start=2025-01-01&end=2025-12-31, https://api.energy-charts.info/public_power?country=be&start=2026-01-01&end=2026-10-23 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T03:46:02Z, 2026-10-24T03:46:18Z, 2026-10-24T03:46:55Z, 2026-10-24T03:47:33Z, 2026-10-24T03:48:10Z, 2026-10-24T03:48:47Z, 2026-10-24T03:49:24Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 908600 |
| `x_type` | not yet written |  | text | Battery, Biomass, Cross border electricity trading, Fossil gas, Fossil oil, Hydro Run-of-River, Hydro pumped storage, Hydro pumped storage consumption, Load, Nuclear, Others, Residual load, Solar, Waste, Wind offshore, Wind onshore | 0 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `cross_border_trading` |  | MW | 59711 | 2019-12-31T23:00:00Z | 2026-10-23T21:00:00Z |
| `load` |  | MW | 59711 | 2019-12-31T23:00:00Z | 2026-10-23T21:00:00Z |
| `public_net_power` |  | MW | 729467 | 2019-12-31T23:00:00Z | 2026-10-23T21:00:00Z |
| `residual_load` |  | MW | 59711 | 2019-12-31T23:00:00Z | 2026-10-23T21:00:00Z |

### `energy_charts_central_europe`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1419805.

- **Source:** energy_charts:public_power_at_ch_cz Energy-Charts.info (Fraunhofer Institute for Solar Energy Systems ISE), public net electricity production (https://energy-charts.info/charts/power/chart.htm?l=en)
- **Method note:** [`docs/methods/energy_charts_central_europe.md`](../methods/energy_charts_central_europe.md)
- **Cite as:** Energy-Charts.info (Fraunhofer ISE). Public net electricity production, Austria, Switzerland and Czechia (API public_power). Via the Energy Research Warehouse (ERW), table `energy_charts_central_europe`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example energy_charts:at:biomass, energy_charts:at:cross_border_electricity_trading, energy_charts:at:fossil_gas; 43 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2022-12-31T23:00:00Z to 2026-10-23T21:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -8812.9 to 12234.1; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | AT, CH, CZ | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1419805 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Austria: Biomass, Austria: Cross border electricity trading, Austria: Fossil gas; 43 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | energy_charts:public_power_at_ch_cz | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.energy-charts.info/public_power?country=at&start=2023-01-01&end=2023-12-31, https://api.energy-charts.info/public_power?country=at&start=2024-01-01&end=2024-12-31, https://api.energy-charts.info/public_power?country=at&start=2025-01-01&end=2025-12-31, https://api.energy-charts.info/public_power?country=at&start=2026-01-01&end=2026-10-23, https://api.energy-charts.info/public_power?country=ch&start=2023-01-01&end=2023-12-31, https://api.energy-charts.info/public_power?country=ch&start=2024-01-01&end=2024-12-31, https://api.energy-charts.info/public_power?country=ch&start=2025-01-01&end=2025-12-31, https://api.energy-charts.info/public_power?country=ch&start=2026-01-01&end=2026-10-23, https://api.energy-charts.info/public_power?country=cz&start=2023-01-01&end=2023-12-31, https://api.energy-charts.info/public_power?country=cz&start=2024-01-01&end=2024-12-31, https://api.energy-charts.info/public_power?country=cz&start=2025-01-01&end=2025-12-31, https://api.energy-charts.info/public_power?country=cz&start=2026-01-01&end=2026-10-23 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T04:07:03Z, 2026-10-24T04:07:43Z, 2026-10-24T04:08:23Z, 2026-10-24T04:09:04Z, 2026-10-24T04:09:42Z, 2026-10-24T04:10:20Z, 2026-10-24T04:10:57Z, 2026-10-24T04:11:34Z, 2026-10-24T04:12:12Z, 2026-10-24T04:12:50Z, 2026-10-24T04:13:30Z, 2026-10-24T04:14:11Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1419805 |
| `x_type` | not yet written |  | text | Biomass, Cross border electricity trading, Fossil brown coal / lignite, Fossil coal-derived gas, Fossil gas, Fossil hard coal, Fossil oil, Geothermal, Hydro Run-of-River, Hydro pumped storage, Hydro pumped storage consumption, Hydro water reservoir, Load, Nuclear, Other renewables, Others, Residual load, Solar, Waste, Wind onshore | 0 |
| `x_resolution` | not yet written |  | text | PT15M, PT1H | 0 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `cross_border_trading` |  | MW | 100221 | 2022-12-31T23:00:00Z | 2026-10-23T21:00:00Z |
| `load` |  | MW | 100220 | 2022-12-31T23:00:00Z | 2026-10-23T21:00:00Z |
| `public_net_power` |  | MW | 1119144 | 2022-12-31T23:00:00Z | 2026-10-23T21:00:00Z |
| `residual_load` |  | MW | 100220 | 2022-12-31T23:00:00Z | 2026-10-23T21:00:00Z |

### `energy_charts_italy_power`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1329375.

- **Source:** energy_charts:public_power_it Energy-Charts.info (Fraunhofer ISE), API, public_power, country it (https://api.energy-charts.info/)
- **Method note:** [`docs/methods/energy_charts_italy_power.md`](../methods/energy_charts_italy_power.md)
- **Cite as:** Energy-Charts.info (Fraunhofer ISE). Energy-Charts API, public_power, Italy. Via the Energy Research Warehouse (ERW), table `energy_charts_italy_power`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | energy_charts:IT | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-12-31T23:00:00Z to 2026-10-22T21:45:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -4779.0 to 52503.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT15M, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | IT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1329375 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | Italy | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | energy_charts:public_power_it | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.energy-charts.info/public_power?country=it&start=2020-01-01&end=2020-12-31, https://api.energy-charts.info/public_power?country=it&start=2021-01-01&end=2021-12-31, https://api.energy-charts.info/public_power?country=it&start=2022-01-01&end=2022-12-31, https://api.energy-charts.info/public_power?country=it&start=2023-01-01&end=2023-12-31, https://api.energy-charts.info/public_power?country=it&start=2024-01-01&end=2024-12-31, https://api.energy-charts.info/public_power?country=it&start=2025-01-01&end=2025-12-31, https://api.energy-charts.info/public_power?country=it&start=2026-01-01&end=2026-10-22 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T04:58:12Z, 2026-10-24T04:58:47Z, 2026-10-24T04:59:21Z, 2026-10-24T04:59:55Z, 2026-10-24T05:00:30Z, 2026-10-24T05:01:04Z, 2026-10-24T05:01:39Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1329375 |

Variables (20):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `battery` |  | MW | 20354 | 2024-12-31T23:00:00Z | 2026-10-22T21:15:00Z |
| `battery_consumption` |  | MW | 20353 | 2024-12-31T23:00:00Z | 2026-10-22T21:15:00Z |
| `biomass` |  | MW | 80924 | 2019-12-31T23:00:00Z | 2026-10-22T21:45:00Z |
| `cross_border_electricity_trading` |  | MW | 80924 | 2019-12-31T23:00:00Z | 2026-10-22T21:45:00Z |
| `fossil_coal_derived_gas` |  | MW | 78182 | 2019-12-31T23:00:00Z | 2026-09-25T07:30:00Z |
| `fossil_gas` |  | MW | 80924 | 2019-12-31T23:00:00Z | 2026-10-22T21:45:00Z |
| `fossil_hard_coal` |  | MW | 78575 | 2019-12-31T23:00:00Z | 2026-10-20T12:00:00Z |
| `fossil_oil` |  | MW | 79691 | 2019-12-31T23:00:00Z | 2026-10-22T21:45:00Z |
| `geothermal` |  | MW | 70185 | 2019-12-31T23:00:00Z | 2026-10-22T21:45:00Z |
| `hydro_pumped_storage` |  | MW | 62671 | 2019-12-31T23:00:00Z | 2026-10-22T19:00:00Z |
| `hydro_pumped_storage_consumption` |  | MW | 62671 | 2019-12-31T23:00:00Z | 2026-10-22T19:00:00Z |
| `hydro_run_of_river` |  | MW | 80924 | 2019-12-31T23:00:00Z | 2026-10-22T21:45:00Z |
| `hydro_water_reservoir` |  | MW | 80900 | 2019-12-31T23:00:00Z | 2026-10-22T21:45:00Z |
| `load` |  | MW | 80924 | 2019-12-31T23:00:00Z | 2026-10-22T21:45:00Z |
| `other_renewables` |  | MW | 4060 | 2024-12-31T23:00:00Z | 2025-07-08T23:00:00Z |
| `others` |  | MW | 80924 | 2019-12-31T23:00:00Z | 2026-10-22T21:45:00Z |
| `solar` |  | MW | 80922 | 2019-12-31T23:00:00Z | 2026-10-22T21:45:00Z |
| `waste` |  | MW | 64597 | 2019-12-31T23:00:00Z | 2026-05-06T14:00:00Z |
| `wind_offshore` |  | MW | 59757 | 2022-05-31T22:00:00Z | 2026-10-22T21:45:00Z |
| `wind_onshore` |  | MW | 80913 | 2019-12-31T23:00:00Z | 2026-10-22T21:45:00Z |

### `energy_charts_portugal_power`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 725799.

- **Source:** energy_charts:public_power_pt Energy-Charts.info (Fraunhofer ISE), API, public_power, country pt (https://api.energy-charts.info/)
- **Method note:** [`docs/methods/energy_charts_portugal_power.md`](../methods/energy_charts_portugal_power.md)
- **Cite as:** Energy-Charts.info (Fraunhofer ISE). Energy-Charts API, public_power, Portugal. Via the Energy Research Warehouse (ERW), table `energy_charts_portugal_power`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | energy_charts:PT | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2020-01-01T00:00:00Z to 2026-10-22T22:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -4410.0 to 10176.6; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | PT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 725799 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | Portugal | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | energy_charts:public_power_pt | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.energy-charts.info/public_power?country=pt&start=2020-01-01&end=2020-12-31, https://api.energy-charts.info/public_power?country=pt&start=2021-01-01&end=2021-12-31, https://api.energy-charts.info/public_power?country=pt&start=2022-01-01&end=2022-12-31, https://api.energy-charts.info/public_power?country=pt&start=2023-01-01&end=2023-12-31, https://api.energy-charts.info/public_power?country=pt&start=2024-01-01&end=2024-12-31, https://api.energy-charts.info/public_power?country=pt&start=2025-01-01&end=2025-12-31, https://api.energy-charts.info/public_power?country=pt&start=2026-01-01&end=2026-10-22 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T05:08:12Z, 2026-10-24T05:08:46Z, 2026-10-24T05:09:20Z, 2026-10-24T05:09:55Z, 2026-10-24T05:10:29Z, 2026-10-24T05:11:03Z, 2026-10-24T05:11:38Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 725799 |

Variables (13):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `biomass` |  | MW | 59687 | 2020-01-01T00:00:00Z | 2026-10-22T22:00:00Z |
| `cross_border_electricity_trading` |  | MW | 59687 | 2020-01-01T00:00:00Z | 2026-10-22T22:00:00Z |
| `fossil_gas` |  | MW | 59687 | 2020-01-01T00:00:00Z | 2026-10-22T22:00:00Z |
| `fossil_hard_coal` |  | MW | 16080 | 2020-01-01T00:00:00Z | 2021-11-30T23:00:00Z |
| `hydro_pumped_storage` |  | MW | 59687 | 2020-01-01T00:00:00Z | 2026-10-22T22:00:00Z |
| `hydro_pumped_storage_consumption` |  | MW | 59687 | 2020-01-01T00:00:00Z | 2026-10-22T22:00:00Z |
| `hydro_run_of_river` |  | MW | 59687 | 2020-01-01T00:00:00Z | 2026-10-22T22:00:00Z |
| `hydro_water_reservoir` |  | MW | 59687 | 2020-01-01T00:00:00Z | 2026-10-22T22:00:00Z |
| `load` |  | MW | 59687 | 2020-01-01T00:00:00Z | 2026-10-22T22:00:00Z |
| `others` |  | MW | 59687 | 2020-01-01T00:00:00Z | 2026-10-22T22:00:00Z |
| `solar` |  | MW | 59687 | 2020-01-01T00:00:00Z | 2026-10-22T22:00:00Z |
| `wind_offshore` |  | MW | 53162 | 2020-05-31T22:00:00Z | 2026-10-22T22:00:00Z |
| `wind_onshore` |  | MW | 59687 | 2020-01-01T00:00:00Z | 2026-10-22T22:00:00Z |

### `energy_charts_southeast_europe_daily`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 128530.

- **Source:** energy_charts:public_power_southeast Energy-Charts.info (Fraunhofer Institute for Solar Energy Systems ISE), public net electricity production (https://energy-charts.info/charts/power/chart.htm?l=en)
- **Method note:** [`docs/methods/energy_charts_southeast_europe_daily.md`](../methods/energy_charts_southeast_europe_daily.md)
- **Cite as:** Energy-Charts.info (Fraunhofer ISE). Public net electricity production, Hungary, Romania, Greece and Bulgaria (API public_power). Via the Energy Research Warehouse (ERW), table `energy_charts_southeast_europe_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example energy_charts:bg:battery, energy_charts:bg:battery_consumption, energy_charts:bg:biomass; 58 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2020-01-01T00:00:00Z to 2026-10-22T00:00:00Z; 2487 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -68958.6 to 215445.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | BG, GR, HU, RO | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 128530 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example BG: Battery, BG: Battery Consumption, BG: Biomass; 58 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | energy_charts:public_power_southeast | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://api.energy-charts.info/public_power?country=bg&start=2020-01-01&end=2026-10-23, https://api.energy-charts.info/public_power?country=gr&start=2020-01-01&end=2026-10-23, https://api.energy-charts.info/public_power?country=hu&start=2020-01-01&end=2026-10-23, https://api.energy-charts.info/public_power?country=ro&start=2020-01-01&end=2026-10-23 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T04:22:15Z, 2026-10-24T04:25:34Z, 2026-10-24T04:26:16Z, 2026-10-24T04:26:54Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 128530 |
| `x_type` | not yet written |  | text | Battery, Battery Consumption, Biomass, Cross border electricity trading, Fossil brown coal / lignite, Fossil gas, Fossil hard coal, Fossil oil, Geothermal, Hydro Run-of-River, Hydro pumped storage, Hydro pumped storage consumption, Hydro water reservoir, Load, Nuclear, Other renewables, Others, Residual load, Solar, Waste, Wind onshore | 0 |
| `x_periods` | not yet written |  | integer | 24, 30, 96 | 0 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `cross_border_trading` |  | MWh | 9948 | 2020-01-01T00:00:00Z | 2026-10-22T00:00:00Z |
| `load` |  | MWh | 9897 | 2020-01-01T00:00:00Z | 2026-10-22T00:00:00Z |
| `public_net_energy` |  | MWh | 98788 | 2020-01-01T00:00:00Z | 2026-10-22T00:00:00Z |
| `residual_load` |  | MWh | 9897 | 2020-01-01T00:00:00Z | 2026-10-22T00:00:00Z |

### `energy_companies`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: model_extracted. Rows read on 2026-11-20: 562.

- **Source:** erw:thesis_builder (public web sources, each row's sources column); erw:energy_deals (the deals' stories).
- **Method note:** [`docs/methods/thesis_builder.md`](../methods/thesis_builder.md)
- **Cite as:** Energy Research Warehouse (ERW). Deal tracker counterparties (energy_deals, warehouse/deals/extract.py); Thesis Builder company finds (warehouse/thesis/build.py), from public web sources. Via the Energy Research Warehouse (ERW), table `energy_companies`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example erwco:1komma5grad, erwco:247-solar, erwco:acme-solar; 562 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | company | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 1Komma5Grad, 247 Solar, ACME Solar; 562 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | empty | no cell holds a value | 562 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 562 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 562 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 562 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | empty | no cell holds a value | 562 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 562 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 562 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:energy_deals, erw:thesis_builder | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://bakercityherald.com/2025/02/06/tyba-raises-13-9m-series-a-to-improve-the-profitability-of-energy-storage-projects/, https://bessmanufacturers.com/resources/fluence-energy-2025-annual-results-energy-storage/, https://electrek.co/2026/09/27/nio-power-geely-30-stake-battery-swap-rmb16-billion/; 411 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-28T17:04:21Z, 2026-09-28T17:07:17Z, 2026-09-28T20:42:40Z, 2026-09-28T20:50:50Z, 2026-09-30T05:12:39Z, 2026-11-15T15:22:21Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | text | 20260928T170409Z, 20260928T170427Z, 20260928T203525Z, 20260928T204245Z, 20260930T050541Z, 20261115T152221Z | 0 |
| `description` | not yet written |  | text | AI energy forecasting software giving utilities, traders and asset operators load, price and renewable forecasts., AI-driven geothermal exploration company that analyzes subsurface data with machine learning, acoustic imaging and seismic imaging, using sensors repurposed from oil and gas, to find geothermal heat resources before drilling., AI-driven smart orchestration platform for distributed energy resources, including batteries, EVs and flexible load., AI-enabled power marketer delivering optimization of renewables and grid-scale batteries., AI-powered, end-to-end simulation and operating platform for developing, managing, and optimizing standalone and hybrid energy storage projects., Algorithmic trading and optimization platform for grid-scale batteries, with route to market in wholesale and balancing markets., Athena AI platform and PowerTrack suite for asset performance management of storage, solar and hybrid portfolios., Battery-storage analytics and benchmarking platform; research and benchmarking, not dispatch., Bid-optimization software (Mosaic) and asset performance management (Nispera) alongside battery-storage hardware products., Designs geothermal design and installation technology combining autonomous drilling and advanced subsurface modeling, for heating and cooling buildings., Develops enhanced geothermal systems (EGS) using horizontal drilling and fiber-optic subsurface sensing to site and produce wells for power generation., Geothermal developer that entered a commercial agreement with Baker Hughes to accelerate large-scale geothermal energy deployment across North America., Heat-harvesting geothermal technology that drills a single directional well into rock at 250 degrees C or higher and pulls heat into the well through a network of thermally conductive material., It builds closed-loop geothermal, the Eavor-Loop., It develops geopressured geothermal systems that use oilfield technology and equipment., It is developing millimeter-wave deep drilling to reach superhot rock., It is developing superhot rock geothermal at Newberry, Oregon., Management software for battery storage and renewable generation, covering AI forecasting, energy arbitrage, distribution network support and capacity market participation., Market intelligence and battery bid-optimization software; its SmartBidder is used by more than 30 customers representing over 4 GW., Nonprofit that builds GeoMap, a free interactive geothermal exploration tool. The North America module has 150+ layers of subsurface and surface data., Software and hardware integrator for grid infrastructure; proprietary energy management platform HybridOS deploys power market strategies for storage owners. | 541 |
| `sector` | not yet written |  | text | for example capital, capital;datacenter_power, capital;datacenter_power;deal; 55 distinct | 0 |
| `niche_tags` | not yet written |  | text | for example deal:behind_the_meter, deal:behind_the_meter;deal:m_and_a;deal:other;tech:gas;tech:oil, deal:behind_the_meter;deal:other;tech:data center; 186 distinct | 0 |
| `stage` | not yet written |  | text | Equity round, Nonprofit, Series A, Series A (extended), Series B, Series C, Series D, acquired by Schneider Electric (2022), later resold to Uplight (2023) (not confirmed: 2023), not disclosed, private, dedicated storage fund (not a conventional VC round), public (NASDAQ: FRVO), public, NYSE: STEM, public, Nasdaq: FLNC | 541 |
| `raised` | not yet written |  | text | $100 million Series C, anchored by Vitol, $115 million Series C (announced 2026-01-21), bringing total equity funding to date to $180 million, $12 million equity round (Series D); total funding of $89.9M across 12 rounds to date, $13.9 million Series A, bringing total funding to $18.15 million, $135M of new capital, including an oversubscribed Series B (reported 2026-09-17) (not confirmed: 2026, 9, 17), $16.6 million in research investments to date, self-reported, $180M Series B final close (2026-08-27), with $35M from Nabors; total funding $280M; first close was $134M (2026-07-07) (not confirmed: 8, 27, 35, 280), $182M, in Canadian dollars per ThinkGeoEnergy, $50 million cumulative capital commitments, second closing of its first energy storage fund, $8.5 million seed led by Wireframe Ventures (2023-10-11); $12 million Series A led by Titanium Ventures, with Energy Impact Partners and Sustainable Future Ventures (2025-01), Has raised $56.7 million across 4 funding rounds: $9.7 million led by Constellation Technology Ventures, $14 million Series A led by Anzu Partners, a $20 million Series A extension led by Valo Ventures and VoLo Earth Ventures (2024-05-21, total Series A of $34.5 million), and $13 million in additional financing (2025-03) (not confirmed: 9.7, 14, 2024, 5), Over $97M, co-led by Ormat and Carbon Direct Capital (2026-01-22) (not confirmed: 22), Series B closed at $20 million, bringing total funding to $30 million (not confirmed: 30), not confirmed, not disclosed, not disclosed (acquisition price undisclosed in both transactions), not disclosed; backed by EnCap Energy Transition Fund III (amount not disclosed) | 544 |
| `location` | not yet written |  | text | for example AK, AL, AZ; 93 distinct | 346 |
| `founders` | not yet written |  | text | Amit Narayan, Carl Hoiland, Joel Edwards, Carlos Araque (CEO), spun out of MIT in 2018, Cindy Taff (CEO), Lev Ring (President), Lance Cook (CTO), Co-founded 2017 by CEO Tim Latimer and CTO Jack Norbeck, Joselyn Lai (CEO), Silviu Livescu (CTO), Led by CEO Josh Prueher, COO Ghazal Izadi and CTO Axel-Pierre Bois, Matt Wytock, founded 2016, Michael Phelan and Padraig Curran, founded 2007 (one company release states 2010), Quentin Scrimshire and Tim Overton, founded 2019, Sean Kelly and Abraham Stanway, founded 2017, Tyler Nisonoff, Michael Baker and Tom Thunell, founded 2022, not disclosed, not disclosed (Jamie Beard is executive director), not disclosed, founded 2009 | 541 |
| `website` | not yet written |  | text | amperon.co, ascendanalytics.com, fervoenergy.com, flexgen.com, fluenceenergy.com, geomap.projectinnerspace.org, gridbeyond.com, gridmatic.com, habitat.energy, mantlereach.com, modoenergy.com, not disclosed, quaise.com, sagegeo.com, stem.com, tyba.ai, xgsenergy.com, zanskar.com | 541 |
| `sources` | not yet written |  | text | for example https://bakercityherald.com/2025/02/06/tyba-raises-13-9m-series-a-to-improve-the-profitability-of-energy-storage-projects/;https://startupintros.com/orgs/tyba;https://www.tyba.ai/series-a-fundraise-announcement/;https://tracxn.com/d/companies/tyba/__bKcyPLaKKDpIRfY2-TeE366G4bu5yseqv38XRlU0Bq8;https://www.prnewswire.com/news-releases/tyba-raises-13-9m-series-a-to-improve-the-profitability-of-energy-storage-projects-302369741.html;https://www.thesaasnews.com/news/tyba-raises-13-9-million-in-series-a/;https://heatmap.news/climate-tech/tyba-series-a;https://www.crunchbase.com/funding_round/tyba-10be-series-a--e4227725, https://bessmanufacturers.com/resources/fluence-energy-2025-annual-results-energy-storage/;https://modoenergy.com/research/en/battery-energy-storage-optimizers-operators-usa-ercot-caiso-miso-spp-pjm-nyiso-isone-serc-wecc;https://blog.fluenceenergy.com/beating-bidding-benchmark-evolving-energy-storage;https://www.sec.gov/Archives/edgar/data/1868941/000186894125000081/flnc-20250930.htm;https://www.sec.gov/Archives/edgar/data/1868941/000186894125000075/flncq3fy25earningspressrel.htm;https://www.sec.gov/Archives/edgar/data/1868941/000186894125000079/flncq4andfullfy25earningsp.htm, https://electrek.co/2026/09/27/nio-power-geely-30-stake-battery-swap-rmb16-billion/; 462 distinct | 0 |
| `confidence` | not yet written |  | integer | 100, 40, 50, 60, 80, 90 | 0 |
| `confidence_note` | not yet written |  | text | for example 2 independent sources, latest 2023; stage not confirmed and raised not confirmed by a primary source, 2 independent sources, latest 2026; stage not confirmed and raised not confirmed by a primary source, 3 independent sources, latest 2022; stage confirmed and raised confirmed by a primary source; 57 distinct | 0 |
| `first_seen` | not yet written |  | date | 2025-01-05 to 2026-11-12; 165 distinct | 0 |

### `energy_deals`

What a row is: not yet written.

Shape: events. Keys: `event_id`. License: public; tier: model_extracted. Rows read on 2026-11-20: 583.

- **Method note:** [`docs/methods/energy_deals.md`](../methods/energy_deals.md)
- **Cite as:** ANS Nuclear Newswire; Bloomberg; Bloomberg.com; Canary Media; DOE newsroom; Data Center Dynamics; Data Center Frontier; Electrek; Energy-Storage.news; Financial Times; Hart Energy; Heatmap News; JPT Homepage; LNG Prime; Latitude Media; Natural Gas Intelligence; OilPrice.com; POWER Magazine; Reuters; Rigzone; Utility Dive; WSJ; World Nuclear News; hartenergy.com; jpt.spe.org; pv magazine USA. news stories; news stories via feed 'Bloomberg energy (via Google News)'; news stories via feed 'Canary Media'; news stories via feed 'DOE newsroom'; news stories via feed 'Data Center Frontier'; news stories via feed 'Electrek'; news stories via feed 'Energy-Storage.news'; news stories via feed 'FT energy (via Google News)'; news stories via feed 'Hart Energy'; news stories via feed 'JPT (SPE)'; news stories via feed 'LNG Prime'; news stories via feed 'Latitude Media'; news stories via feed 'Natural Gas Intelligence'; news stories via feed 'POWER Magazine'; news stories via feed 'Reuters energy (via Google News)'; news stories via feed 'Rigzone'; news stories via feed 'Utility Dive'; news stories via feed 'WSJ energy (via Google News)'; news stories via feed 'World Nuclear News'. Via the Energy Research Warehouse (ERW), table `energy_deals`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | none | text | for example deal:0046c6c22995488c, deal:006dc20ac6ffe6f3, deal:01b0163eef7a0337; 583 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | text | for example 2025-01-05T08:00:00Z, 2025-01-09T08:00:00Z, 2025-01-10T08:00:00Z; 408 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others) | none | text | deal | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | text | for example 1Komma5Grad, AD Ports;Nimex, ADNOC's XRG;Eni; 538 distinct | 2 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 583 |
| `mw` | The capacity involved, in megawatts | MW | number | 20.0 to 6000.0; 34 distinct | 547 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 583 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 583 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | announced, cancelled, closed, rumored, signed | 98 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ANS Nuclear Newswire, Bloomberg, Bloomberg.com, DOE newsroom, Data Center Dynamics, Data Center Frontier, Electrek, Energy-Storage.news, Financial Times, Hart Energy, Heatmap News, JPT Homepage, LNG Prime, Latitude Media, Natural Gas Intelligence, OilPrice.com, POWER Magazine, Reuters, Rigzone, Utility Dive, WSJ, World Nuclear News, hartenergy.com, jpt.spe.org, pv magazine USA | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://electrek.co/2026/09/27/nio-power-geely-30-stake-battery-swap-rmb16-billion/, https://heatmap.news/climate-tech/coreshell-series-b, https://lngprime.com/americas/argent-lng-awards-feed-contract/197559/; 576 distinct | 0 |
| `deal_type` | not yet written |  | text | behind_the_meter, debt, equity_raise, fuel_supply, joint_venture, lease, m_and_a, nuclear_restart, offtake, other, ppa, project_finance, smr | 0 |
| `buyer` | not yet written |  | text | for example AD Ports, ADNOC's XRG, AEP; 273 distinct | 168 |
| `seller` | not yet written |  | text | for example 1Komma5Grad, 247 Solar, ACME Solar; 341 distinct | 109 |
| `other_parties` | not yet written |  | text | for example ADQ;ECP, AMD, Advent;ADIA; 86 distinct | 490 |
| `asset` | not yet written |  | text | for example 1 gigawatt AI data centre, 100-Acre AI Data Center, 1Komma5Grad; 518 distinct | 25 |
| `technology` | not yet written |  | text | for example AI, AI chips, AI cloud; 45 distinct | 270 |
| `state` | not yet written |  | text | AK, AL, AZ, CA, IA, IL, IN, KY, LA, MD, MI, MN, NC, NV, OH, OK, PA, TN, TX, UT, VA, VT, WV, WY | 530 |
| `country` | not yet written |  | text | for example Angola, Argentina, Australia; 39 distinct | 473 |
| `mwh` | not yet written |  | integer | 1200, 3300000, 462 | 580 |
| `dollars` | not yet written |  | integer | 30000000 to 1250000000000; 154 distinct | 285 |
| `price_value` | not yet written |  | integer | 12, 80 | 581 |
| `price_unit` | not yet written |  | text | %, CAD/share | 581 |
| `term_years` | not yet written |  | integer | 10, 11, 20, 27, 5 | 562 |
| `announced_date` | not yet written |  | date | 2026-01-05, 2026-10-27, 2026-11-12 | 579 |
| `date_basis` | not yet written |  | text | first_story_published, stated | 0 |
| `ai_power` | not yet written |  | boolean | False, false, true | 0 |
| `confidence` | not yet written |  | number | 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.88, 0.9, 0.92, 0.93, 0.95 | 0 |
| `n_stories` | not yet written |  | integer | 1, 10, 11, 12, 2, 3, 4, 5, 6, 7, 8 | 0 |
| `story_ids` | not yet written |  | text | for example news:002c70a07e0f31cf;news:c541ea6f5afafd84;news:a59324e18ffefd35;news:83da2e1baec42285, news:008d77926c1be7ac, news:013b0a168e7a0f3a; 576 distinct | 0 |
| `story_urls` | not yet written |  | text | for example https://electrek.co/2026/09/27/nio-power-geely-30-stake-battery-swap-rmb16-billion/, https://heatmap.news/climate-tech/coreshell-series-b, https://lngprime.com/americas/argent-lng-awards-feed-contract/197559/; 576 distinct | 0 |
| `model_id` | not yet written |  | text | claude-sonnet-5, claude-sonnet-5-5 | 0 |
| `extracted_at` | not yet written |  | utc time | 2026-09-27T01:52:23Z to 2026-11-12T22:08:35Z; 28 distinct | 0 |
| `kind` | not yet written |  | text | behind_the_meter, capital, compute_capacity, fuel_supply, gas_buildout, m_and_a, nuclear_restart_uprate, offtake, other, ppa, project_finance, smr, storage | 0 |
| `kind_basis` | not yet written |  | text | for example a data center between two named parties as the deal's asset, a lease of a data center, a nuclear deal whose stories say: uprates; 31 distinct | 0 |
| `stage` | not yet written |  | text | announced, cancelled, closed, financed, rumored, signed | 535 |
| `grid` | not yet written |  | text | PJM | 582 |
| `usd` | not yet written |  | integer | 30000000 to 1250000000000; 154 distinct | 285 |
| `usd_per_mwh` | not yet written |  | empty | no cell holds a value | 583 |
| `ai_power_basis` | not yet written |  | text | datacenter load: data center, datacenter load: data centers, datacenter load: hyperscale, datacenter load: hyperscaler, party AWS, party AirTrunk, party Brookfield, Nvidia, party CoreWeave, party Google, party Microsoft, party NTT DATA, party NVIDIA, party Nvidia, party OpenAI, party Oracle | 567 |
| `flags` | not yet written |  | text | headline: 1000 MW; record: none, headline: 1100 MW, 3700 MW; record: none, headline: 1200 MW; record: none, headline: 20000 MW; record: none, headline: 700 MW; record: 2100 MW, headline: 890 MW, 3600 MW; record: none, headline: USD 1 billion; record: none, headline: USD 1.07 billion; record: none, headline: USD 10 billion; record: USD 2.4 billion, headline: USD 100 billion; record: none, headline: USD 103 billion; record: none, headline: USD 2 billion; record: USD 2.4 billion, usd 1250000000000 above the bound 500000000000 | 569 |
| `fields_version` | not yet written |  | text | 2232, upgraded | 0 |
| `status_history` | not yet written |  | text | for example 2026-10-01 announced (first record); 2026-10-27 signed (news:83da2e1baec42285), 2026-10-22 signed (first record), 2026-10-23 announced (first record); 2026-10-27 signed (news:8069d44f6e606faf); 50 distinct | 533 |
| `buyer_name` | not yet written |  | text | for example AD Ports, ADNOC's XRG, Adani; 259 distinct | 168 |
| `seller_name` | not yet written |  | text | for example 1Komma5Grad, 247 Solar, ACME Solar; 331 distinct | 109 |
| `buyer_parent` | not yet written |  | text | Adnoc, Amazon, BlackRock, EIG, Geely Holding, General Motors | 577 |
| `seller_parent` | not yet written |  | text | Aditya Birla, Amazon, Blackstone, Chevron, Constellation Energy, ExxonMobil, Leviathan, MAIRE, OGE Energy, Vivek Ramaswamy | 573 |
| `buyer_eia861` | not yet written |  | empty | no cell holds a value | 583 |
| `seller_eia861` | not yet written |  | empty | no cell holds a value | 583 |

### `energy_projects`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: derived. Rows read on 2026-11-20: 45612.

- **Source:** erw:energy_projects ERW derived table, energy projects method (docs/methods/energy_projects.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/energy_projects.md)
- **Method note:** [`docs/methods/energy_projects.md`](../methods/energy_projects.md)
- **Cite as:** Energy Research Warehouse (ERW), derived; U.S. Census Bureau. Energy projects for the project map (docs/methods/energy_projects.md); Gazetteer Files, counties (2025), county internal points; Gazetteer Files, county subdivisions (2025), internal points; Gazetteer Files, places (2025), place internal points. Via the Energy Research Warehouse (ERW), table `energy_projects`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example caiso_queue:10, caiso_queue:100, caiso_queue:1000; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | generator, project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example (3K) 59 Hetcheltown Rd, (Offshore wind Increase (Q700 +Q1154), 0 Hammond St CSG; more than 5000 distinct | 6960 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 53 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 17.947115 to 71.292; more than 5000 distinct | 790 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -171.7124 to -65.27956; more than 5000 distinct | 790 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | -53.3 to 4000.0; 4395 distinct | 278 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | active, completed, operating, planned, suspended, under_construction, withdrawn | 34 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | date | 1891-01-01 to 2026-10-29; 3733 distinct | 8193 |
| `operator` | The operator or owner, as the publisher writes it | none | text | for example 0HAM WHAM8 Solar, LLC, 1000 Mile Solar, LLC, 1001 Ebenezer Church Solar, LLC; more than 5000 distinct | 11199 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:energy_projects | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/energy_projects.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-26T00:06:50Z, 2026-09-30T23:33:22Z, 2026-10-24T14:49:59Z, 2026-11-05T23:21:53Z, 2026-11-05T23:21:54Z, 2026-11-05T23:22:47Z, 2026-11-05T23:22:50Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | text | 2026-09, 2026-09-26T00:00:00Z, 2026-09-30T00:00:00Z, 2026-11-05 | 0 |
| `project_id` | not yet written |  | text | for example caiso_queue:10, caiso_queue:100, caiso_queue:1000; more than 5000 distinct | 0 |
| `kind` | not yet written |  | text | operating, planned, queue | 0 |
| `technology_group` | not yet written |  | text | biomass, coal, geothermal, hybrid, hydro, natural_gas, nuclear, other, petroleum, solar, storage, transmission, unknown, wind | 0 |
| `mw` | The capacity involved, in megawatts | MW | number | -53.3 to 4000.0; 4395 distinct | 278 |
| `state` | not yet written |  | text | for example AK, AL, AR; 52 distinct | 297 |
| `county` | not yet written |  | text | for example 8 Sites, ALAMEDA, ALAMEDA COUNTY; 2868 distinct | 488 |
| `geo_precision` | not yet written |  | text | county, none, place, point | 0 |
| `geo_note` | not yet written |  | text | for example county "Wsch'r/Bkln/Qns" not found in the gazetteer for NY, county '8 Sites' not found in the gazetteer for NE, county 'Alb.-Col.-Dutch.' not found in the gazetteer for NY; 1578 distinct | 31073 |
| `operator_role` | not yet written |  | text | developer, operator | 11199 |
| `date` | not yet written |  | text | for example 1891, 1893, 1896; 3543 distinct | 65 |
| `date_kind` | not yet written |  | text | operating_year, planned_operation_date, queue_date | 65 |
| `technology` | not yet written |  | text | for example =Solid Waste, AC Transmission, All Other; 178 distinct | 818 |
| `source_status` | not yet written |  | text | for example ACTIVE, Active, COMPLETED; 29 distinct | 34 |
| `source_table` | not yet written |  | text | caiso_interconnection_queue, eia860m_operating_generators, eia860m_planned_generators, ercot_interconnection_queue, isone_interconnection_queue, miso_interconnection_queue, nyiso_interconnection_queue, spp_interconnection_queue | 0 |
| `proposed_date` | not yet written |  | date | 1990-12-03 to 2036-05-05; 1989 distinct | 37537 |

