# Codebook: ercot

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 38 public tables (6 entities, 2 events, 30 series; tiers: 12 derived, 26 source); 0 documented in full.

- [`ercot_4cp_intervals`](#ercot_4cp_intervals): ERCOT's four coincident peaks, the summer months' peak intervals and ERCOT's load in them, by year (session 359)
- [`ercot_all_hub_prices_history`](#ercot_all_hub_prices_history): ERCOT trading hub prices, day-ahead and real-time, one row per interval of each operating year from 2015 (the yearly history)
- [`ercot_as_prices`](#ercot_as_prices): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261030T153444Z-github (2026-10-30T15:34:44Z); that run's own header of the table follows
- [`ercot_as_prices_daily`](#ercot_as_prices_daily): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261030T153444Z-github (2026-10-30T15:34:44Z); that run's own header of the table follows
- [`ercot_as_prices_monthly`](#ercot_as_prices_monthly): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261020T011604Z-github (2026-10-20T01:16:04Z); that run's own header of the table follows
- [`ercot_as_quantities`](#ercot_as_quantities): ERCOT DAM Ancillary Service Plan, MW by product and hour (NP4-33-CD)
- [`ercot_cdr_reserve_margins`](#ercot_cdr_reserve_margins): ERCOT, Capacity, Demand and Reserves report (CDR): load forecast, capacity counted and planning reserve margin by season (session 851)
- [`ercot_cdr_units`](#ercot_cdr_units): ERCOT, the units of the Capacity, Demand and Reserves report: each resource's code, county, zone, fuel, status, in-service date and capacity (session 872)
- [`ercot_dam_cleared_energy`](#ercot_dam_cleared_energy): ERCOT, energy bought in the day-ahead market by hour, system-wide (NP4-192-CD, DAM Total Energy Purchased) (session 136)
- [`ercot_dam_esr_awards`](#ercot_dam_esr_awards): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261115T160738Z-github (2026-11-15T16:07:38Z); that run's own header of the table follows
- [`ercot_grid_notices`](#ercot_grid_notices): ERCOT's grid notices, Energy Emergency Alerts, rotating outages, conservation appeals, watches and the control room's operating notices (session 322)
- [`ercot_hub_prices_daily`](#ercot_hub_prices_daily): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261116T155131Z-github (2026-11-16T15:51:31Z); that run's own header of the table follows
- [`ercot_interconnection_queue`](#ercot_interconnection_queue): Rebuilt from the ERW archive by warehouse/archive/restore.py, as of run 20261106T003628Z-github (2026-11-06T00:36:28Z); that run's own header of the table follows
- [`ercot_large_load_status`](#ercot_large_load_status): ERCOT's Large Load Interconnection Status Update, the figures each report states in words (session 106)
- [`ercot_node_places`](#ercot_node_places): ERCOT's resource nodes with the county and load zone of the CDR units at their station (session 901)
- [`ercot_node_planned_generation`](#ercot_node_planned_generation): the planned generation in each placed ERCOT resource node's county: ERCOT's active queue projects and EIA-860M's planned generators (session 931)
- [`ercot_node_transmission`](#ercot_node_transmission): ERCOT's transmission projects (TPIT) by the county of each placed resource node (session 917)
- [`ercot_node_wires_utilities`](#ercot_node_wires_utilities): the wires utilities in each placed ERCOT resource node's county, from EIA-861's service territories, with Texas's delivery-only companies named apart (session 945)
- [`ercot_peak_premium_annual`](#ercot_peak_premium_annual): ERCOT peak premium metrics per hub and ERCOT operating year (derived)
- [`ercot_peak_premium_monthly`](#ercot_peak_premium_monthly): ERCOT peak premium metrics per hub and calendar month (derived)
- [`ercot_peak_premium_node_monthly`](#ercot_peak_premium_node_monthly): ERCOT peak premium metrics per settlement point and calendar month (derived)
- [`ercot_rtm_node_prices`](#ercot_rtm_node_prices): ERCOT real-time Settlement Point Prices at the storage resources' settlement points, the hubs and the Load Zones, by 15-minute interval (session 120)
- [`ercot_rtm_price_adders`](#ercot_rtm_price_adders): ERCOT's real-time reserve price adders, hourly: the operating reserve demand curve's adders and the reliability deployment price adder
- [`ercot_sced_esr_hourly`](#ercot_sced_esr_hourly): ERCOT Energy Storage Resources in real time, by resource and hour, from ERCOT's 60-Day SCED Disclosure Reports, the file 60d_ESR_Data_in_SCED, each day reduced to resource-hour totals as it was read (session 120)
- [`ercot_storage_dam_awards_monthly`](#ercot_storage_dam_awards_monthly): what ERCOT's Energy Storage Resources were awarded day-ahead, the fleet by local month (derived, session 115)
- [`ercot_storage_dam_offers_daily`](#ercot_storage_dam_offers_daily): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261115T160738Z-github (2026-11-15T16:07:38Z); that run's own header of the table follows
- [`ercot_storage_dam_offers_monthly`](#ercot_storage_dam_offers_monthly): what ERCOT's Energy Storage Resources offered day-ahead and how much of it was awarded, the fleet by local month (derived, session 116)
- [`ercot_storage_node_basis`](#ercot_storage_node_basis): the real-time price at each storage resource's settlement point against the hub average, over the days of node prices held (derived, session 120)
- [`ercot_storage_rt_monthly`](#ercot_storage_rt_monthly): what ERCOT's storage resources did in real time, beside what they were awarded day-ahead, by month (derived, session 120)
- [`ercot_storage_rt_offers_monthly`](#ercot_storage_rt_offers_monthly): what ERCOT's storage fleet offered to sell in real time, by price, by local month (derived, session 7019)
- [`ercot_transmission_projects`](#ercot_transmission_projects): ERCOT, Transmission Project and Information Tracking (TPIT): every transmission project the owners report, future, planned, completed and cancelled (session 852)
- [`ercot_wind_solar_forecast`](#ercot_wind_solar_forecast): ERCOT wind and solar, the forecast a day ahead and the actual output, hourly, system-wide (session 133)
- [`ercot_wind_solar_hsl_daily`](#ercot_wind_solar_hsl_daily): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261116T155131Z-github (2026-11-16T15:51:31Z); that run's own header of the table follows
- [`ercot_wind_solar_hsl_hourly`](#ercot_wind_solar_hsl_hourly): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261116T155131Z-github (2026-11-16T15:51:31Z); that run's own header of the table follows
- [`ercot_wind_solar_hsl_monthly`](#ercot_wind_solar_hsl_monthly): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261106T003628Z-github (2026-11-06T00:36:28Z); that run's own header of the table follows
- [`ercot_wind_solar_output_hourly`](#ercot_wind_solar_output_hourly): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261020T063359Z-github (2026-10-20T06:33:59Z); that run's own header of the table follows
- [`ercot_zone_load_hourly`](#ercot_zone_load_hourly): ERCOT, hourly native load by weather zone and ERCOT's total (Hourly Load Data Archives) (session 138)
- [`ercot_zone_prices_history`](#ercot_zone_prices_history): ERCOT load zone settlement point prices, day-ahead (hourly, the eight load zones) and real time (15-minute, the four competitive load zones), one row per interval of each operating year from 2015 (session 140)

### `ercot_4cp_intervals`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 28.

- **Source:** ercot:NP9-83-M ERCOT, Four Coincident Peak Calculations (report type 13037; prior years: the page's Key Documents) (https://www.ercot.com/mktinfo/data_agg/4cp)
- **Method note:** [`docs/methods/ercot_4cp_intervals.md`](../methods/ercot_4cp_intervals.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Four Coincident Peak Calculations (NP9-83-M; the years before 2021 from the page's 1996-2020 zip). Via the Energy Research Warehouse (ERW), table `ercot_4cp_intervals`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:system | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-06-27T21:45:00Z to 2025-09-04T22:15:00Z; 28 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 64692.523772 to 85636.884588; 28 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT15M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_4cp | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | ERCOT | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP9-83-M | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/files/docs/2022/01/13/1996-2020_FourCoincidentPeakCalculations.zip, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1055377059, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1164129560, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=879528147, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=961277079 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-20T10:12:39Z, 2026-10-20T10:12:41Z, 2026-10-20T10:12:43Z, 2026-10-20T10:12:45Z, 2026-10-20T10:12:47Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2022-11-28T00:00:00Z, 2023-11-27T00:00:00Z, 2024-11-25T00:00:00Z, 2025-11-24T00:00:00Z | 12 |
| `x_year` | not yet written |  | integer | 2018, 2019, 2020, 2022, 2023, 2024, 2025 | 0 |
| `x_month` | not yet written |  | text | for example 2018-06, 2018-07, 2018-08; 28 distinct | 0 |
| `x_interval_local` | not yet written |  | text | for example 2018-06-27 17:00, 2018-07-19 17:00, 2018-08-23 16:45; 28 distinct | 0 |
| `x_published` | not yet written |  | date | 2022-11-28, 2023-11-27, 2024-11-25, 2025-11-24 | 12 |
| `x_document` | not yet written |  | text | ERCOTFourCoincidentPeakLoadCalculation2018.xlsx, ERCOTFourCoincidentPeakLoadCalculation2019.xlsx, ERCOTFourCoincidentPeakLoadCalculation2020.xlsx, rpt.00013037.0000000000000000.20221128.090923347.4CP20221128.xlsx, rpt.00013037.0000000000000000.20231127.102940992.4CP20231127.xlsx, rpt.00013037.0000000000000000.20241125.121105134.4CP20241125.xlsx, rpt.00013037.0000000000000000.20251124.083820245.4CP20251124.xlsx | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `cp4_load_mw` |  | MW | 28 | 2018-06-27T21:45:00Z | 2025-09-04T22:15:00Z |

### `ercot_all_hub_prices_history`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3124224.

- **Source:** ERCOT NP4-180-ER Historical DAM Load Zone and Hub Prices (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-180-ER)
- **Source:** ERCOT NP6-785-ER Historical RTM Load Zone and Hub Prices (https://www.ercot.com/mp/data-products/data-product-details?id=NP6-785-ER)
- **Method note:** [`docs/methods/automated_analysis_findings.md`](../methods/automated_analysis_findings.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Historical DAM Load Zone and Hub Prices; Historical RTM Load Zone and Hub Prices. Via the Energy Research Warehouse (ERW), table `ercot_all_hub_prices_history`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:HB_BUSAVG, ercot:HB_HOUSTON, ercot:HB_HUBAVG, ercot:HB_NORTH, ercot:HB_SOUTH, ercot:HB_WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T06:00:00Z to 2026-11-19T05:45:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -251.0 to 9315.45; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT15M, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_dam, ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | HB_BUSAVG, HB_HOUSTON, HB_HUBAVG, HB_NORTH, HB_SOUTH, HB_WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP4-180-ER, ercot:NP4-190-CD, ercot:NP6-785-ER, ercot:NP6-905-CD | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1065468714, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1065471230, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1177667469; 4531 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-26T00:09:58Z to 2026-11-19T17:27:27Z; 2184 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2016-01-01T14:03:08Z to 2026-11-16T06:02:02Z; 3763 distinct | 4608 |
| `year` | The operating year a history table was published by | none | integer | 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `spp_dam` |  | USD/MWh | 624384 | 2015-01-01T06:00:00Z | 2026-11-17T05:00:00Z |
| `spp_rtm` |  | USD/MWh | 2499840 | 2015-01-01T06:00:00Z | 2026-11-19T05:45:00Z |

### `ercot_as_prices`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 339332.

- **Source:** ercot:NP4-181-ER ERCOT, Historical DAM Clearing Prices for Capacity (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-181-ER)
- **Source:** ercot:NP4-188-CD ERCOT, DAM Clearing Prices for Capacity (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-188-CD)
- **Method note:** [`docs/methods/ercot_as_prices.md`](../methods/ercot_as_prices.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). DAM Clearing Prices for Capacity; Historical DAM Clearing Prices for Capacity. Via the Energy Research Warehouse (ERW), table `ercot_as_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:ECRS, ercot:NSPIN, ercot:REGDN, ercot:REGUP, ercot:RRS | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-01-01T06:00:00Z to 2026-10-31T04:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 25674.3; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MW-hour | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | ECRS, NSPIN, REGDN, REGUP, RRS | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP4-181-ER, ercot:NP4-188-CD | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1065466940, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1177658395, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1290346030, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1290652168, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1290729005, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1291119920, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1291545998, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1291928786, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1292323467, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=642564840, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=694281905, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=751350601, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=814917148, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=886625668, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=969797266 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T15:15:21Z, 2026-10-02T15:15:25Z, 2026-10-02T15:15:29Z, 2026-10-02T15:15:33Z, 2026-10-02T15:15:37Z, 2026-10-02T15:15:41Z, 2026-10-02T15:15:45Z, 2026-10-02T15:15:49Z, 2026-10-25T14:54:34Z, 2026-10-25T14:54:44Z, 2026-10-26T15:05:41Z, 2026-10-27T14:57:31Z, 2026-10-28T15:05:55Z, 2026-10-29T14:53:35Z, 2026-10-30T15:04:41Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2019-01-01T13:00:48Z, 2020-01-01T13:01:16Z, 2021-01-01T13:04:29Z, 2022-01-01T13:04:42Z, 2023-01-01T13:03:38Z, 2024-01-01T13:00:55Z, 2025-01-01T13:01:05Z, 2026-01-01T13:18:09Z, 2026-10-24T17:32:44Z, 2026-10-25T13:01:00Z, 2026-10-25T17:33:05Z, 2026-10-26T17:33:14Z, 2026-10-27T18:15:55Z, 2026-10-28T17:32:48Z, 2026-10-29T17:33:24Z | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `mcpc_dam` |  | USD/MW-hour | 339332 | 2018-01-01T06:00:00Z | 2026-10-31T04:00:00Z |

### `ercot_as_prices_daily`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 70695.

- **Source:** erw:ercot_as_prices_rollup ERW derived daily and monthly summary of ERCOT reserve prices (docs/methods/ercot_as_prices_rollup.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_as_prices_rollup.md)
- **Method note:** [`docs/methods/ercot_as_prices_rollup.md`](../methods/ercot_as_prices_rollup.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT reserve prices by day and by month (docs/methods/ercot_as_prices_rollup.md). Via the Energy Research Warehouse (ERW), table `ercot_as_prices_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:ECRS, ercot:NSPIN, ercot:REGDN, ercot:REGUP, ercot:RRS | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-01-01T00:00:00Z to 2026-10-30T00:00:00Z; 3225 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 25674.3; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MW-hour, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | ECRS, NSPIN, REGDN, REGUP, RRS | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_as_prices_rollup | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_as_prices_rollup.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T22:00:13Z, 2026-10-08T15:09:03Z, 2026-10-09T15:01:20Z, 2026-10-10T15:08:34Z, 2026-10-11T15:33:44Z, 2026-10-12T15:02:16Z, 2026-10-13T15:02:46Z, 2026-10-14T15:37:34Z, 2026-10-15T15:45:50Z, 2026-10-19T16:25:27Z, 2026-10-19T20:48:32Z, 2026-10-21T15:10:55Z, 2026-10-22T15:04:35Z, 2026-10-23T15:03:51Z, 2026-10-24T15:11:29Z, 2026-10-25T14:54:52Z, 2026-10-26T15:05:51Z, 2026-10-27T14:57:42Z, 2026-10-28T15:06:06Z, 2026-10-29T14:53:43Z, 2026-10-30T15:04:50Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 70695 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `mcpc_dam_hours` |  | count | 14139 | 2018-01-01T00:00:00Z | 2026-10-30T00:00:00Z |
| `mcpc_dam_hours_in_day` |  | count | 14139 | 2018-01-01T00:00:00Z | 2026-10-30T00:00:00Z |
| `mcpc_dam_max` |  | USD/MW-hour | 14139 | 2018-01-01T00:00:00Z | 2026-10-30T00:00:00Z |
| `mcpc_dam_mean` |  | USD/MW-hour | 14139 | 2018-01-01T00:00:00Z | 2026-10-30T00:00:00Z |
| `mcpc_dam_min` |  | USD/MW-hour | 14139 | 2018-01-01T00:00:00Z | 2026-10-30T00:00:00Z |

### `ercot_as_prices_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 2325.

- **Source:** erw:ercot_as_prices_rollup ERW derived daily and monthly summary of ERCOT reserve prices (docs/methods/ercot_as_prices_rollup.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_as_prices_rollup.md)
- **Method note:** [`docs/methods/ercot_as_prices_rollup.md`](../methods/ercot_as_prices_rollup.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT reserve prices by day and by month (docs/methods/ercot_as_prices_rollup.md). Via the Energy Research Warehouse (ERW), table `ercot_as_prices_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:ECRS, ercot:NSPIN, ercot:REGDN, ercot:REGUP, ercot:RRS | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-01-01T00:00:00Z to 2026-10-01T00:00:00Z; 106 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 25674.3; 997 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MW-hour, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | ECRS, NSPIN, REGDN, REGUP, RRS | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_as_prices_rollup | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_as_prices_rollup.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T22:00:13Z, 2026-10-08T15:09:03Z, 2026-10-14T15:37:34Z, 2026-10-19T16:25:27Z, 2026-10-19T20:48:32Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 2325 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `mcpc_dam_hours` |  | count | 465 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `mcpc_dam_hours_in_month` |  | count | 465 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `mcpc_dam_max` |  | USD/MW-hour | 465 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `mcpc_dam_mean` |  | USD/MW-hour | 465 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `mcpc_dam_min` |  | USD/MW-hour | 465 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |

### `ercot_as_quantities`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 4800.

- **Source:** ercot:np4-33-cd ERCOT, DAM Ancillary Service Plan, NP4-33-CD ( (https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=12316)
- **Method note:** [`docs/methods/ercot_as_quantities.md`](../methods/ercot_as_quantities.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). DAM Ancillary Service Plan (NP4-33-CD). Via the Energy Research Warehouse (ERW), table `ercot_as_quantities`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:ECRS, ercot:NSPIN, ercot:REGDN, ercot:REGUP, ercot:RRS | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-03T05:00:00Z to 2026-10-13T04:00:00Z; 960 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 246 to 3936; 189 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | ECRS, NSPIN, REGDN, REGUP, RRS | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:np4-33-cd | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1269584411, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1269981073, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1270379366; 40 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-03T10:23:53Z to 2026-10-11T20:04:22Z; 34 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-09-02T10:00:00Z to 2026-10-11T10:00:00Z; 40 distinct | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `quantity_mw_plan` |  | MW | 4800 | 2026-09-03T05:00:00Z | 2026-10-13T04:00:00Z |

### `ercot_cdr_reserve_margins`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1600.

- **Source:** ercot:cdr Electric Reliability Council of Texas (ERCOT), Capacity, Demand and Reserves Report (https://www.ercot.com/gridinfo/resource)
- **Method note:** [`docs/methods/ercot_cdr_reserve_margins.md`](../methods/ercot_cdr_reserve_margins.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Capacity, Demand and Reserves Report. Via the Energy Research Warehouse (ERW), table `ercot_cdr_reserve_margins`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot_cdr:fall:peak_load, ercot_cdr:fall:peak_net_load, ercot_cdr:spring:peak_load, ercot_cdr:spring:peak_net_load, ercot_cdr:summer:peak_load, ercot_cdr:summer:peak_net_load, ercot_cdr:winter:peak_load, ercot_cdr:winter:peak_net_load | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-03-01T00:00:00Z, 2026-06-01T00:00:00Z, 2026-09-01T00:00:00Z, 2026-12-01T00:00:00Z, 2027-03-01T00:00:00Z, 2027-06-01T00:00:00Z, 2027-09-01T00:00:00Z, 2027-12-01T00:00:00Z, 2028-03-01T00:00:00Z, 2028-06-01T00:00:00Z, 2028-09-01T00:00:00Z, 2028-12-01T00:00:00Z, 2029-03-01T00:00:00Z, 2029-06-01T00:00:00Z, 2029-09-01T00:00:00Z, 2029-12-01T00:00:00Z, 2030-03-01T00:00:00Z, 2030-06-01T00:00:00Z, 2030-09-01T00:00:00Z, 2030-12-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -3693.245562235888 to 141703.70549374598; 608 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P3M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Fall 2026, peak load hour 17, Fall 2026, peak net load hour 20, Fall 2027, peak load hour 17; 40 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:cdr | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/files/docs/2025/12/19/CapacityDemandandReservesReport_December2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T01:40:30Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2025-12-19T00:00:00Z | 0 |
| `x_hour` | not yet written |  | integer | 17, 19, 20, 21, 8 | 0 |
| `x_report` | not yet written |  | text | CapacityDemandandReservesReport_December2025.xlsx | 0 |

Variables (40):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dc_ties` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `energy_efficiency_savings` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `firm_peak_load` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `less_controllable_load` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `less_emergency_response_service` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `less_load_resources_ecrs` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `less_load_resources_nonspin` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `less_load_resources_rrs` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `less_rooftop_pv` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `less_tdsp_load_management` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `less_voltage_reduction` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_coastal_wind` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_far_west_solar` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_hydro` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_less_switchable_unavailable` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_mothballed` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_other_solar` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_other_wind` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_panhandle_wind` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_pending_retirement` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_private_use_networks` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_rmr` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_storage` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_switchable` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_thermal` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_total` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_west_solar` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_coastal_wind` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_far_west_solar` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_other_solar` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_other_wind` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_panhandle_wind` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_storage` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_thermal` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_total` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_unconfirmed_retirements` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_west_solar` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `reserve_margin` |  | pct | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `total_capacity` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `total_seasonal_load` |  | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |

### `ercot_cdr_units`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 1772.

- **Source:** ercot:cdr:unit_details Electric Reliability Council of Texas (ERCOT), Capacity, Demand and Reserves Report, Unit Details (https://www.ercot.com/gridinfo/resource)
- **Method note:** [`docs/methods/ercot_cdr_units.md`](../methods/ercot_cdr_units.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Capacity, Demand and Reserves Report, Unit Details. Via the Energy Research Warehouse (ERW), table `ercot_cdr_units`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example ercot_cdr_unit:16INR0049:SOLAR_W, ercot_cdr_unit:19599_1_GOLD_SPIKE:SOLAR_O, ercot_cdr_unit:19599_2_GOLD_SPIKE:SOLAR_O; 1772 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 7V SOLAR U1, 7V SOLAR U2, 7V SOLAR U3; 1755 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 1772 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 1772 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | -400.0 to 1390.0; 989 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | operating, planned, suspended | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | date | 1928-01-01 to 2029-07-01; 873 distinct | 5 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 1772 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:cdr:unit_details | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/files/docs/2025/12/19/CapacityDemandandReservesReport_December2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T01:40:30Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2025-12-19T00:00:00Z | 0 |
| `x_unit_code` | not yet written |  | text | for example 19599_1_GOLD_SPIKE, 19599_2_GOLD_SPIKE, 19599_GOLD_SPIKE; 1458 distinct | 312 |
| `x_inr` | not yet written |  | text | for example 12INR0059b, 15INR0064b, 16INR0049; 431 distinct | 1269 |
| `x_technology` | not yet written |  | text | BA, CC, GT, HY, IC, MWH, PV, ST, WT | 0 |
| `x_fuel` | not yet written |  | text | BIOMASS, COAL, DIESEL, GAS, HYDRO, MWH, NUCLEAR, SOLAR-FW, SOLAR-O, SOLAR-W, STORAGE, WIND-C, WIND-O, WIND-P | 0 |
| `x_cdr_status` | not yet written |  | text | EXT-OUT, MOTH-IND, MOTH-SEA, OPER, OPER-SLF, OPER-SYN, OPER-SYN-SLF, OPER-UNFC, OPER-UNR, PLAN, PLAN-RPR, PLAN-SLF, RMR | 0 |
| `x_attribute` | not yet written |  | text | CONV, CONV-DGR, CONV-SLF, CONV-SODG, CONV-TGR, DC-TIE, SWGR-AVA, SWGR-UNA | 0 |
| `x_county` | not yet written |  | text | for example ANDERSON, ANDREWS, ANGELINA; 184 distinct | 1 |
| `x_zone` | not yet written |  | text | COASTAL, HOUSTON, NORTH, PANHANDLE, SOUTH, WEST | 1 |
| `x_summer_2026` | not yet written |  | number | -400.0 to 1293.2; 679 distinct | 0 |
| `x_summer_2027` | not yet written |  | number | -400.0 to 1293.2; 747 distinct | 0 |
| `x_summer_2028` | not yet written |  | number | -400.0 to 1293.2; 803 distinct | 0 |
| `x_summer_2029` | not yet written |  | number | -400.0 to 1300.0; 818 distinct | 0 |
| `x_summer_2030` | not yet written |  | number | -400.0 to 1300.0; 817 distinct | 0 |
| `x_winter_2026_2027` | not yet written |  | number | -389.0 to 1353.2; 700 distinct | 0 |
| `x_winter_2027_2028` | not yet written |  | number | -389.0 to 1353.2; 772 distinct | 0 |
| `x_winter_2028_2029` | not yet written |  | number | -389.0 to 1353.2; 806 distinct | 0 |
| `x_winter_2029_2030` | not yet written |  | number | -389.0 to 1353.2; 812 distinct | 0 |
| `x_winter_2030_2031` | not yet written |  | number | -389.0 to 1353.2; 810 distinct | 0 |
| `x_spring_2026` | not yet written |  | number | -179.0 to 1323.2; 653 distinct | 0 |
| `x_spring_2027` | not yet written |  | number | -389.0 to 1323.2; 722 distinct | 0 |
| `x_spring_2028` | not yet written |  | number | -389.0 to 1323.2; 793 distinct | 0 |
| `x_spring_2029` | not yet written |  | number | -389.0 to 1350.0; 815 distinct | 0 |
| `x_spring_2030` | not yet written |  | number | -389.0 to 1350.0; 818 distinct | 0 |
| `x_fall_2026` | not yet written |  | number | -195.0 to 1323.2; 696 distinct | 0 |
| `x_fall_2027` | not yet written |  | number | -195.0 to 1323.2; 769 distinct | 0 |
| `x_fall_2028` | not yet written |  | number | -195.0 to 1323.2; 808 distinct | 0 |
| `x_fall_2029` | not yet written |  | number | -195.0 to 1350.0; 815 distinct | 0 |
| `x_fall_2030` | not yet written |  | number | -195.0 to 1350.0; 815 distinct | 0 |

### `ercot_dam_cleared_energy`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 816.

- **Source:** ercot:NP4-192-CD Electric Reliability Council of Texas (ERCOT), NP4-192-CD, DAM Total Energy Purchased (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-192-CD)
- **Method note:** [`docs/methods/ercot_dam_cleared_energy.md`](../methods/ercot_dam_cleared_energy.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). NP4-192-CD, DAM Total Energy Purchased. Via the Energy Research Warehouse (ERW), table `ercot_dam_cleared_energy`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:system | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-23T05:00:00Z to 2026-11-17T05:00:00Z; 816 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 27811.1 to 52634.7; 812 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | Total_DAM_Energy_Bought, summed over settlement points | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP4-192-CD | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1277674205, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1278079535, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1278479657; 34 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T20:27:09Z to 2026-11-16T11:49:05Z; 34 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 816 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dam_cleared_energy` |  | MWh | 816 | 2026-09-23T05:00:00Z | 2026-11-17T05:00:00Z |

### `ercot_dam_esr_awards`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2042277.

- **Source:** ercot:NP3-966-ER ERCOT, 60-Day DAM Disclosure Reports,  document list (https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13051)
- **Method note:** [`docs/methods/ercot_dam_esr_awards.md`](../methods/ercot_dam_esr_awards.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). 60-Day DAM Disclosure Reports (the file 60d_DAM_ESR_Data: Energy Storage Resources). Via the Energy Research Warehouse (ERW), table `ercot_dam_esr_awards`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example ercot:ABINDUST_ESR1, ercot:ADL_ESR1, ercot:AE_ESR1; 339 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-12-06T06:00:00Z to 2026-09-01T04:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -9.9 to 240.0; 1141 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example ABINDUST_RN, ADL_RN, AE_RN; 295 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP3-966-ER | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1190045004, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1190315373, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1190560109; 269 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-04T21:33:39Z to 2026-11-15T15:54:05Z; 269 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-02-04T22:53:33Z to 2026-10-30T12:41:46Z; 269 distinct | 0 |
| `x_qse` | not yet written |  | text | for example QAETE1, QAETEL, QAMA1; 120 distinct | 0 |
| `x_dme` | not yet written |  | text | for example Y2WPER, YAETEL, YAGPC2; 185 distinct | 1895 |
| `x_resource_status` | not yet written |  | text | ON, ONOS, ONTEST, OUT | 0 |
| `x_lsl_mw` | not yet written |  | number | -240.0 to 156.0; 376 distinct | 0 |
| `x_energy_award_mw` | not yet written |  | number | -240.0 to 216.0; 2982 distinct | 1046971 |
| `x_energy_price_usd_per_mwh` | not yet written |  | number | -205.72 to 22618.19; more than 5000 distinct | 0 |
| `x_regup_award_mw` | not yet written |  | number | 0.0 to 350.0; 1708 distinct | 848995 |
| `x_regup_mcpc` | not yet written |  | number | 0.0 to 896.96; 776 distinct | 848995 |
| `x_regdn_award_mw` | not yet written |  | number | 0.0 to 308.9; 1633 distinct | 848995 |
| `x_regdn_mcpc` | not yet written |  | number | 0.0 to 26.71; 560 distinct | 848995 |
| `x_rrspfr_award_mw` | not yet written |  | number | 0.0 to 157.0; 1560 distinct | 848995 |
| `x_rrsffr_award_mw` | not yet written |  | number | 0.0 to 62.5; 340 distinct | 848995 |
| `x_rrsufr_award_mw` | not yet written |  | integer | 0 | 848995 |
| `x_rrs_mcpc` | not yet written |  | number | 0.05 to 999.02; 602 distinct | 848995 |
| `x_ecrs_award_mw` | not yet written |  | number | 0.0 to 240.0; 1747 distinct | 848995 |
| `x_ecrs_mcpc` | not yet written |  | number | 0.01 to 1000.65; 669 distinct | 848995 |
| `x_nonspin_award_mw` | not yet written |  | number | 0.0 to 302.0; 1369 distinct | 848995 |
| `x_nonspin_mcpc` | not yet written |  | number | 0.25 to 432.13; 975 distinct | 848995 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `hsl_mw` |  | MW | 2042277 | 2025-12-06T06:00:00Z | 2026-09-01T04:00:00Z |

### `ercot_grid_notices`

What a row is: not yet written.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 178.

- **Source:** ercot:news_releases ERCOT, News Releases,  ercot:operations_messages ERCOT, Operations Messages (https://www.ercot.com/services/comm/mkt_notices/opsmessages)
- **Method note:** [`docs/methods/ercot_grid_notices.md`](../methods/ercot_grid_notices.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). News Releases (grid conditions: EEAs, conservation appeals, watches); Operations Messages (the control room's notices). Via the Energy Research Warehouse (ERW), table `ercot_grid_notices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | none | text | for example ercot_notice:2011-02-02:rotating_outages:940f126d07, ercot_notice:2011-02-03:update:0ab5ac164a, ercot_notice:2011-02-08:power_watch:129e58267d; 178 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2011-02-02 to 2026-10-15; 142 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others) | none | text | advisory, conservation_appeal, eea1, eea2, emergency_test, ocn_weather, power_watch, rotating_outages, statement, update, voluntary_conservation, watch, weather_watch | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | text | ERCOT | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 178 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 178 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 178 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 178 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | active, cancelled, ended, issued | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:news_releases, ercot:operations_messages | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/news/release/01052025-ercot-issues-weather, https://www.ercot.com/news/release/01172025-ercot-issues-weather, https://www.ercot.com/news/release/01212026-ercot-issues-weather; 105 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-19T21:02:01Z | 0 |
| `x_label` | not yet written |  | text | for example Advisory, Cold weather, risk of rotating outages return to the Valley tonight, Conservation Alert extended through Tuesday morning; 83 distinct | 0 |
| `x_region` | not yet written |  | text | ERCOT, Rio Grande Valley | 0 |
| `x_issued_at` | not yet written |  | text | for example 2011-02-02, 2011-02-03, 2011-02-08; 108 distinct | 0 |
| `x_counts` | not yet written |  | text | no, yes | 0 |
| `x_text` | not yet written |  | text | for example Advisory issued for a geomagnetic disturbance of K-7 until October 10, 2026 1900., Advisory issued for a geomagnetic disturbance of K7 until 0100 on 07/05/26., At 10:22 ERCOT has issued an Advisory due to TSAT not solving in the last 30 minutes.; 125 distinct | 0 |

### `ercot_hub_prices_daily`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 348420.

- **Source:** erw:ercot_hub_prices_daily ERW derived daily summary of ERCOT hub prices (docs/methods/ercot_hub_prices_daily.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_hub_prices_daily.md)
- **Method note:** [`docs/methods/ercot_hub_prices_daily.md`](../methods/ercot_hub_prices_daily.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT hub prices by day (docs/methods/ercot_hub_prices_daily.md). Via the Energy Research Warehouse (ERW), table `ercot_hub_prices_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:HB_BUSAVG, ercot:HB_HOUSTON, ercot:HB_HUBAVG, ercot:HB_NORTH, ercot:HB_SOUTH, ercot:HB_WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-11-16T00:00:00Z; 4336 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -251.0 to 9315.45; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_dam, ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | HB_BUSAVG, HB_HOUSTON, HB_HUBAVG, HB_NORTH, HB_SOUTH, HB_WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_hub_prices_daily | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_hub_prices_daily.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-05T02:03:57Z to 2026-11-16T14:59:45Z; 30 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 348420 |

Variables (14):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `da_hours_above_200` |  | count | 26016 | 2015-01-01T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_hours_below_zero` |  | count | 26016 | 2015-01-01T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_max` |  | USD/MWh | 26016 | 2015-01-01T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_mean` |  | USD/MWh | 26016 | 2015-01-01T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_min` |  | USD/MWh | 26016 | 2015-01-01T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_offpeak_mean` |  | USD/MWh | 26016 | 2015-01-01T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_peak_mean` |  | USD/MWh | 18198 | 2015-01-02T00:00:00Z | 2026-11-16T00:00:00Z |
| `rt_hours_above_200` |  | count | 25992 | 2015-01-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `rt_hours_below_zero` |  | count | 25992 | 2015-01-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `rt_max` |  | USD/MWh | 25992 | 2015-01-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `rt_mean` |  | USD/MWh | 25992 | 2015-01-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `rt_min` |  | USD/MWh | 25992 | 2015-01-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `rt_offpeak_mean` |  | USD/MWh | 25992 | 2015-01-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `rt_peak_mean` |  | USD/MWh | 18174 | 2015-01-02T00:00:00Z | 2026-11-13T00:00:00Z |

### `ercot_interconnection_queue`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 1736.

- **Source:** ercot:interconnection_queue ERCOT Generation Interconnection Status (GIS) report (https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1293955078)
- **Method note:** [`docs/methods/ercot_interconnection_queue.md`](../methods/ercot_interconnection_queue.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Generation Interconnection Status (GIS) report. Via the Energy Research Warehouse (ERW), table `ercot_interconnection_queue`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example ercot_queue:15INR0064b, ercot_queue:16INR0049, ercot_queue:16INR0081; 1736 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 18-ALPHA BESS, 18-BRAVO BESS, 2 Cedar Wind; 1736 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 1736 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 1736 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | -53.3 to 2992.0; 1206 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | active, completed | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | date | 2017-12-20 to 2026-10-23; 96 distinct | 1633 |
| `operator` | The operator or owner, as the publisher writes it | none | text | for example 174 Power Global Properties, 174 Power Global Properties, LLC, 180 Wind LLC; 1295 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:interconnection_queue | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1293955078 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-05T23:21:53Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | date | 2026-11-05 | 0 |
| `queue_id` | not yet written |  | text | for example 15INR0064b, 16INR0049, 16INR0081; 1736 distinct | 0 |
| `county` | not yet written |  | text | for example Anderson, Andrews, Angelina; 193 distinct | 0 |
| `state` | not yet written |  | text | TX | 0 |
| `poi` | not yet written |  | text | for example # 38900 Hidden Lakes - # 42015 PHR 138 KV, # 7044 Marion 345kV, # 79601 Stillman Substation 138 kV; 1386 distinct | 0 |
| `zone` | not yet written |  | empty | no cell holds a value | 1736 |
| `transmission_owner` | not yet written |  | empty | no cell holds a value | 1736 |
| `fuel_technology` | not yet written |  | text | Fuel Oil - Other, Gas - Combined-Cycle, Gas - Combustion (gas) Turbine, but not part of a Combined-Cycle, Gas - Internal Combustion Engine, eg. Reciprocating, Gas - Steam Turbine other than Combined-Cycle, Hydrogen - Other, Nuclear - Steam Turbine other than Combined-Cycle, Other - Battery Energy Storage, Other - Other, Solar - Photovoltaic Solar, Water - Other, Wind - Wind Turbine | 1 |
| `iso_status` | not yet written |  | text | Active, Completed | 0 |
| `queue_date` | not yet written |  | date | 2013-11-27 to 2026-10-22; 411 distinct | 12 |
| `proposed_in_service_date` | not yet written |  | date | 2025-03-27 to 2033-06-15; 526 distinct | 0 |
| `actual_in_service_date` | not yet written |  | date | 2017-12-20 to 2026-10-23; 100 distinct | 1627 |
| `withdrawn_date` | not yet written |  | empty | no cell holds a value | 1736 |

### `ercot_large_load_status`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 38.

- **Source:** ercot:large_load_status_update ERCOT, Large Load Interconnection Status Update (the Large Load Integration team's monthly report to TAC and the LLWG); found on the meeting pages of  and (https://www.ercot.com/committees/tac)
- **Method note:** [`docs/methods/ercot_large_load_status.md`](../methods/ercot_large_load_status.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Large Load Interconnection Status Update (the Large Load Integration team's monthly report to TAC and the LLWG). Via the Energy Research Warehouse (ERW), table `ercot_large_load_status`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:large_load | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-05-28T00:00:00Z, 2025-07-30T00:00:00Z, 2025-08-27T00:00:00Z, 2025-10-17T00:00:00Z, 2025-11-19T00:00:00Z, 2026-01-21T00:00:00Z, 2026-02-25T00:00:00Z, 2026-03-13T00:00:00Z, 2026-03-26T00:00:00Z, 2026-04-24T00:00:00Z, 2026-05-21T00:00:00Z, 2026-06-19T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 137.0 to 140000.0; 32 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 38 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 38 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:large_load_status_update | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/files/docs/2025/05/27/11.-LLWG-Report.zip#LLI Queue Status Update - 2025-5.pdf, https://www.ercot.com/files/docs/2025/07/29/12.-LLWG-Report.zip#LLI Queue Status Update - 2025-07-21.pdf, https://www.ercot.com/files/docs/2025/08/26/13.-LLWG-Report.zip#LLI Queue Status Update - 2025-08-27.pdf, https://www.ercot.com/files/docs/2025/10/21/11.-LLWG-Report.zip#October TAC Report.pptx, https://www.ercot.com/files/docs/2025/11/18/11-LLWG-Report.zip#November TAC Report.pdf, https://www.ercot.com/files/docs/2026/01/20/16.-Large-Load-Issues.zip#January TAC Report.pdf, https://www.ercot.com/files/docs/2026/03/05/February-TAC-Report.pdf, https://www.ercot.com/files/docs/2026/03/12/March-TAC-Report.pdf, https://www.ercot.com/files/docs/2026/03/27/March-TAC-Report-Updated_03262026.pptx, https://www.ercot.com/files/docs/2026/04/24/April-24-LLWG-Report_042426.pptx, https://www.ercot.com/files/docs/2026/05/21/May-21-LLWG-Report.pptx, https://www.ercot.com/files/docs/2026/06/18/June-19-LLWG-Report.pptx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T17:45:38Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2025-05-28T00:00:00Z, 2025-07-30T00:00:00Z, 2025-08-27T00:00:00Z, 2025-10-17T00:00:00Z, 2025-11-19T00:00:00Z, 2026-01-21T00:00:00Z, 2026-02-25T00:00:00Z, 2026-03-13T00:00:00Z, 2026-03-26T00:00:00Z, 2026-04-24T00:00:00Z, 2026-05-21T00:00:00Z, 2026-06-19T00:00:00Z | 0 |
| `x_month_as_written` | not yet written |  | text | August 2025, February 2025, January 2025, July 2025, June 2026, March 2025, March 2026, May 2025, May 2026, November 2025, October 2025 | 14 |
| `x_document` | not yet written |  | text | April-24-LLWG-Report_042426.pptx, February-TAC-Report.pdf, January TAC Report.pdf, June-19-LLWG-Report.pptx, LLI Queue Status Update - 2025-07-21.pdf, LLI Queue Status Update - 2025-08-27.pdf, LLI Queue Status Update - 2025-5.pdf, March-TAC-Report-Updated_03262026.pptx, March-TAC-Report.pdf, May-21-LLWG-Report.pptx, November TAC Report.pdf, October TAC Report.pptx | 0 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `approved_to_energize_mw` |  | MW | 12 | 2025-05-28T00:00:00Z | 2026-06-19T00:00:00Z |
| `new_submissions_count` |  | count | 1 | 2026-03-13T00:00:00Z | 2026-03-13T00:00:00Z |
| `new_submissions_mw` |  | MW | 1 | 2026-03-13T00:00:00Z | 2026-03-13T00:00:00Z |
| `observed_nonsimultaneous_peak_mw` |  | MW | 12 | 2025-05-28T00:00:00Z | 2026-06-19T00:00:00Z |
| `observed_simultaneous_peak_mw` |  | MW | 12 | 2025-05-28T00:00:00Z | 2026-06-19T00:00:00Z |

### `ercot_node_places`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 569.

- **Source:** ercot:cdr Electric Reliability Council of Texas (ERCOT), Capacity, Demand and Reserves Report (the units' county and zone), and ERCOT's settlement points as node_basis_daily holds them
- **Method note:** [`docs/methods/ercot_node_places.md`](../methods/ercot_node_places.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT's resource nodes with the county and zone of their CDR units (docs/methods/ercot_node_places.md). Via the Energy Research Warehouse (ERW), table `ercot_node_places`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example ercot_node:7RNCHSLR_ALL, ercot_node:A4_DGR1_RN, ercot_node:A4_DGR2_RN; 569 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 7RNCHSLR_ALL, A4_DGR1_RN, A4_DGR2_RN; 569 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 569 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 569 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 569 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | empty | no cell holds a value | 569 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 569 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 569 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_node_places | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_node_places.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T06:46:36Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 569 |
| `x_station` | not yet written |  | text | for example 7RNCHSLR, A4, ADL; 496 distinct | 0 |
| `x_county` | not yet written |  | text | for example ANDREWS, ANGELINA, ARCHER; 148 distinct | 0 |
| `x_zone` | not yet written |  | text | COASTAL, HOUSTON, NORTH, PANHANDLE, SOUTH, WEST | 0 |
| `x_class` | not yet written |  | text | gas, mixed, other, solar, storage, wind | 0 |
| `x_resource_type` | not yet written |  | text | for example CCGT90, CCLE90, CLLIG; 26 distinct | 0 |
| `x_cdr_units` | not yet written |  | text | for example 7RNCHSLR_UNIT1;7RNCHSLR_UNIT2;7RNCHSLR_UNIT3, A4_DGR1;A4_DGR2, ADL_SOLAR1; 496 distinct | 0 |
| `x_cdr_units_n` | not yet written |  | integer | 1, 10, 12, 17, 2, 3, 4, 5, 6, 7, 8, 9 | 0 |

### `ercot_node_planned_generation`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 569.

- **Source:** ercot:interconnection_queue Electric Reliability Council of Texas (ERCOT), GIS report; eia:eia860m U.S. Energy Information Administration, Form EIA-860M; ercot:cdr ERCOT, Capacity, Demand and Reserves Report (the nodes' counties, through ercot_node_places)
- **Method note:** [`docs/methods/ercot_node_planned_generation.md`](../methods/ercot_node_planned_generation.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The planned generation in a placed ERCOT node's county (docs/methods/ercot_node_planned_generation.md). Via the Energy Research Warehouse (ERW), table `ercot_node_planned_generation`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example ercot_node:7RNCHSLR_ALL, ercot_node:A4_DGR1_RN, ercot_node:A4_DGR2_RN; 569 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 7RNCHSLR_ALL, A4_DGR1_RN, A4_DGR2_RN; 569 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 569 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 569 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 569 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | empty | no cell holds a value | 569 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 569 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 569 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_node_planned_generation | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_node_planned_generation.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T10:20:32Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 569 |
| `x_county` | not yet written |  | text | for example ANDREWS, ANGELINA, ARCHER; 148 distinct | 0 |
| `x_zone` | not yet written |  | text | COASTAL, HOUSTON, NORTH, PANHANDLE, SOUTH, WEST | 0 |
| `x_queue_projects` | not yet written |  | integer | 0, 1, 10, 11, 12, 13, 14, 15, 17, 19, 2, 20, 21, 22, 23, 25, 3, 36, 4, 5, 6, 7, 8, 9 | 0 |
| `x_queue_mw` | not yet written |  | number | 0.0 to 16312.91; 139 distinct | 0 |
| `x_queue_solar_mw` | not yet written |  | number | -53.3 to 6534.3; 103 distinct | 0 |
| `x_queue_wind_mw` | not yet written |  | number | 0.0 to 2287.88; 41 distinct | 0 |
| `x_queue_storage_mw` | not yet written |  | number | 0.0 to 5280.63; 126 distinct | 0 |
| `x_queue_gas_mw` | not yet written |  | number | 0.0 to 5886.29; 44 distinct | 0 |
| `x_queue_other_mw` | not yet written |  | number | 0.0, 1232.0, 132.0, 1320.0, 1336.52, 50.0, 79.63 | 0 |
| `x_queue_next_in_service` | not yet written |  | date | 2025-08-26 to 2030-03-01; 100 distinct | 18 |
| `x_eia_planned_generators` | not yet written |  | integer | 0, 1, 10, 11, 12, 13, 161, 2, 3, 4, 5, 6, 7, 8, 9 | 0 |
| `x_eia_planned_mw` | not yet written |  | number | 0.0 to 16147.3; 95 distinct | 0 |
| `x_eia_solar_mw` | not yet written |  | number | 0.0 to 1609.6; 66 distinct | 0 |
| `x_eia_wind_mw` | not yet written |  | number | 0.0, 110.4, 162.1, 200.0, 225.6, 265.0, 265.5, 276.0, 316.2, 355.5, 440.0, 500.0, 670.5 | 0 |
| `x_eia_storage_mw` | not yet written |  | number | 0.0 to 1385.9; 55 distinct | 0 |
| `x_eia_natural_gas_mw` | not yet written |  | number | 0.0, 10.0, 11679.3, 121.8, 199.8, 2334.9, 43.4, 447.0, 5.0, 721.0 | 0 |
| `x_eia_nuclear_mw` | not yet written |  | number | 0.0, 4468.0 | 0 |
| `x_eia_petroleum_mw` | not yet written |  | number | 0.0, 9.9 | 0 |
| `x_eia_hydro_mw` | not yet written |  | number | 0.0 | 0 |
| `x_eia_biomass_mw` | not yet written |  | number | 0.0 | 0 |
| `x_eia_geothermal_mw` | not yet written |  | number | 0.0 | 0 |
| `x_eia_other_mw` | not yet written |  | number | 0.0, 28.6, 9.9 | 0 |

### `ercot_node_transmission`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 569.

- **Source:** ercot:tpit Electric Reliability Council of Texas (ERCOT), Transmission Project and Information Tracking; ercot:cdr ERCOT, Capacity, Demand and Reserves Report (the nodes' counties, through ercot_node_places)
- **Method note:** [`docs/methods/ercot_node_transmission.md`](../methods/ercot_node_transmission.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT's TPIT projects by a resource node's county (docs/methods/ercot_node_transmission.md). Via the Energy Research Warehouse (ERW), table `ercot_node_transmission`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example ercot_node:7RNCHSLR_ALL, ercot_node:A4_DGR1_RN, ercot_node:A4_DGR2_RN; 569 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 7RNCHSLR_ALL, A4_DGR1_RN, A4_DGR2_RN; 569 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 569 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 569 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 569 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | empty | no cell holds a value | 569 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 569 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 569 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_node_transmission | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_node_transmission.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-06T05:23:43Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 569 |
| `x_county` | not yet written |  | text | for example ANDREWS, ANGELINA, ARCHER; 148 distinct | 0 |
| `x_zone` | not yet written |  | text | COASTAL, HOUSTON, NORTH, PANHANDLE, SOUTH, WEST | 0 |
| `x_phases_future` | not yet written |  | integer | 0 to 109; 33 distinct | 0 |
| `x_phases_planned` | not yet written |  | integer | 0, 1, 12, 2, 3, 4, 44, 5, 6, 7 | 0 |
| `x_phases_completed` | not yet written |  | integer | 0, 1, 12, 13, 2, 3, 39, 4, 5, 6, 7 | 0 |
| `x_phases_cancelled` | not yet written |  | integer | 0, 1, 2, 3, 4, 5, 6, 7, 8 | 0 |
| `x_open_projects` | not yet written |  | integer | 0 to 153; 38 distinct | 0 |
| `x_open_new_circuit_miles` | not yet written |  | number | 0.0 to 685.67; 82 distinct | 0 |
| `x_open_upgraded_circuit_miles` | not yet written |  | number | 0.0 to 424.18; 115 distinct | 0 |
| `x_open_max_kv` | not yet written |  | integer | 138, 345, 69, 765 | 24 |
| `x_open_next_in_service` | not yet written |  | date | 2025-05-01 to 2031-06-01; 78 distinct | 24 |
| `x_tpit_edition` | not yet written |  | text | OCTOBER BASE FOR TRANSMISSION OWNER SUBMISSION FILE - TRANSMISSION PROJECT INFORMATION TRACKING (TPIT) FUTURE PROJECTS AS OF 10/1/2026 | 0 |

### `ercot_node_wires_utilities`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 569.

- **Source:** eia:eia861_territory and eia:eia861 U.S. Energy Information Administration, Form EIA-861 (service territories, delivery companies, utility data); ercot:cdr ERCOT, Capacity, Demand and Reserves Report (the nodes' counties, through ercot_node_places)
- **Method note:** [`docs/methods/ercot_node_wires_utilities.md`](../methods/ercot_node_wires_utilities.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The wires utilities in a placed ERCOT node's county (docs/methods/ercot_node_wires_utilities.md). Via the Energy Research Warehouse (ERW), table `ercot_node_wires_utilities`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example ercot_node:7RNCHSLR_ALL, ercot_node:A4_DGR1_RN, ercot_node:A4_DGR2_RN; 569 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 7RNCHSLR_ALL, A4_DGR1_RN, A4_DGR2_RN; 569 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 569 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 569 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 569 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | empty | no cell holds a value | 569 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 569 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 569 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_node_wires_utilities | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_node_wires_utilities.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T11:28:45Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | text | EIA-861 2025 | 0 |
| `x_county` | not yet written |  | text | for example ANDREWS, ANGELINA, ARCHER; 148 distinct | 0 |
| `x_zone` | not yet written |  | text | COASTAL, HOUSTON, NORTH, PANHANDLE, SOUTH, WEST | 0 |
| `x_utilities_n` | not yet written |  | integer | 1, 2, 3, 4, 5, 6, 7, 8 | 0 |
| `x_utilities` | not yet written |  | text | for example AEP Texas Central Company (3278); Bandera Electric Coop, Inc (1175); Medina Electric Coop, Inc (12268); Rio Grande Electric Coop, Inc (16057), AEP Texas Central Company (3278); Bluebonnet Electric Coop, Inc (1892); CenterPoint Energy (8901); City of Weimar - (TX) (20331); Fayette Electric Coop, Inc (6183); San Bernard Electric Coop, Inc (16638); Wharton County Elec Coop, Inc (20472), AEP Texas Central Company (3278); Bluebonnet Electric Coop, Inc (1892); City of Lockhart - (TX) (11119); City of Luling - (TX) (11316); Guadalupe Valley Elec Coop Inc (7752); Pedernales Electric Coop, Inc (14626); 139 distinct | 0 |
| `x_delivery_only_n` | not yet written |  | integer | 0, 1, 2, 3 | 0 |
| `x_delivery_only` | not yet written |  | text | AEP Texas Central Company (3278), AEP Texas Central Company (3278); CenterPoint Energy (8901), AEP Texas Central Company (3278); CenterPoint Energy (8901); Texas-New Mexico Power Co (40051), AEP Texas Central Company (3278); Nueces Electric Cooperative (13830), AEP Texas Central Company (3278); Oncor Electric Delivery Company LLC (44372), AEP Texas North Company (20404), AEP Texas North Company (20404); Oncor Electric Delivery Company LLC (44372), AEP Texas North Company (20404); Oncor Electric Delivery Company LLC (44372); Texas-New Mexico Power Co (40051), AEP Texas North Company (20404); Texas-New Mexico Power Co (40051), CenterPoint Energy (8901), CenterPoint Energy (8901); Texas-New Mexico Power Co (40051), Oncor Electric Delivery Company LLC (44372), Oncor Electric Delivery Company LLC (44372); Texas-New Mexico Power Co (40051), Texas-New Mexico Power Co (40051) | 52 |
| `x_outside_tre_n` | not yet written |  | integer | 0, 1, 2, 3, 4 | 0 |
| `x_outside_tre` | not yet written |  | text | Bailey County Elec Coop Assn (1169); Deaf Smith Electric Coop, Inc (4939); Lamb County Electric Coop, Inc (10625); Southwestern Public Service Co (17718), Bailey County Elec Coop Assn (1169); Deaf Smith Electric Coop, Inc (4939); Southwestern Public Service Co (17718), Deaf Smith Electric Coop, Inc (4939); Rita Blanca Electric Coop, Inc (16063); Southwestern Public Service Co (17718), Deaf Smith Electric Coop, Inc (4939); Southwestern Public Service Co (17718), El Paso Electric Co (5701), Entergy Texas Inc. (55937), Greenbelt Electric Coop, Inc (7561), Greenbelt Electric Coop, Inc (7561); North Plains Electric Coop Inc (13757); Southwestern Public Service Co (17718), Greenbelt Electric Coop, Inc (7561); Southwestern Public Service Co (17718), Jasper-Newton Elec Coop, Inc (9668); Sam Houston Electric Coop Inc (16613), Lamb County Electric Coop, Inc (10625); Southwestern Public Service Co (17718), Rusk County Electric Coop, Inc (16461), Rusk County Electric Coop, Inc (16461); Upshur Rural Elec Coop Corp (19579), Southwestern Public Service Co (17718), Wood County Electric Coop, Inc (20927) | 441 |
| `x_short_form_n` | not yet written |  | integer | 0, 1, 2, 3 | 0 |

### `ercot_peak_premium_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 4032.

- **Source:** erw:ercot_peak_premium ERW derived metrics, ERCOT peak premium method (docs/methods/ercot_peak_premium.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_peak_premium.md)
- **Method note:** [`docs/methods/ercot_peak_premium.md`](../methods/ercot_peak_premium.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT peak premium metrics (docs/methods/ercot_peak_premium.md). Via the Energy Research Warehouse (ERW), table `ercot_peak_premium_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:HB_BUSAVG, ercot:HB_HOUSTON, ercot:HB_HUBAVG, ercot:HB_NORTH, ercot:HB_SOUTH, ercot:HB_WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z, 2026-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -251.0 to 35136.0; 2555 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | HB_BUSAVG, HB_HOUSTON, HB_HUBAVG, HB_NORTH, HB_SOUTH, HB_WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_peak_premium | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_peak_premium.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T17:54:52Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 4032 |

Variables (56):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `all_iqr` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `all_max` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `all_median` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `all_min` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `all_p999` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `all_q1` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `all_q3` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `midday_max` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `midday_median` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `midday_min` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `midday_q1` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `midday_q3` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `n_intervals` |  | count | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `n_negative` |  | count | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `n_scarcity` |  | count | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `overnight_max` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `overnight_median` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `overnight_min` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `overnight_q1` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `overnight_q3` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `peak_iqr` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `peak_max` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `peak_median` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `peak_min` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `peak_minus_midday_median` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `peak_q1` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `peak_q3` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `worst_interval_multiple` |  | ratio | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_all_iqr` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_all_max` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_all_median` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_all_min` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_all_p999` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_all_q1` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_all_q3` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_midday_max` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_midday_median` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_midday_min` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_midday_q1` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_midday_q3` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_n_intervals` |  | count | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_n_negative` |  | count | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_n_scarcity` |  | count | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_overnight_max` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_overnight_median` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_overnight_min` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_overnight_q1` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_overnight_q3` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_peak_iqr` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_peak_max` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_peak_median` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_peak_min` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_peak_minus_midday_median` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_peak_q1` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_peak_q3` |  | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_worst_interval_multiple` |  | ratio | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

### `ercot_peak_premium_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 24024.

- **Source:** erw:ercot_peak_premium ERW derived metrics, ERCOT peak premium method (docs/methods/ercot_peak_premium.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_peak_premium.md)
- **Method note:** [`docs/methods/ercot_peak_premium.md`](../methods/ercot_peak_premium.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT peak premium metrics (docs/methods/ercot_peak_premium.md). Via the Energy Research Warehouse (ERW), table `ercot_peak_premium_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:HB_BUSAVG, ercot:HB_HOUSTON, ercot:HB_HUBAVG, ercot:HB_NORTH, ercot:HB_SOUTH, ercot:HB_WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-11-01T00:00:00Z; 143 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -251.0 to 9315.45; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | HB_BUSAVG, HB_HOUSTON, HB_HUBAVG, HB_NORTH, HB_SOUTH, HB_WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_peak_premium | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_peak_premium.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T17:54:52Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 24024 |

Variables (28):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `all_iqr` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_max` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_median` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_min` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_p999` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_q1` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_q3` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_max` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_median` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_min` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_q1` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_q3` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `n_intervals` |  | count | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `n_negative` |  | count | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `n_scarcity` |  | count | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_max` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_median` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_min` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_q1` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_q3` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_iqr` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_max` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_median` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_min` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_minus_midday_median` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_q1` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_q3` |  | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `worst_interval_multiple` |  | ratio | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |

### `ercot_peak_premium_node_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 17472.

- **Source:** erw:ercot_node_peak_premium ERW derived metrics, ERCOT peak premium method (docs/methods/ercot_peak_premium.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_peak_premium.md)
- **Method note:** [`docs/methods/ercot_peak_premium.md`](../methods/ercot_peak_premium.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT peak premium metrics per settlement point (docs/methods/ercot_peak_premium.md). Via the Energy Research Warehouse (ERW), table `ercot_peak_premium_node_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example ercot:ABINDUST_RN, ercot:ADL_RN, ercot:AE_RN; 312 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-10-01T00:00:00Z, 2026-11-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -251.0 to 3522.5; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example ABINDUST_RN, ADL_RN, AE_RN; 312 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_node_peak_premium | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_peak_premium.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T19:57:05Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 17472 |

Variables (28):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `all_iqr` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_max` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_median` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_min` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_p999` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_q1` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_q3` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_max` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_median` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_min` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_q1` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_q3` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `n_intervals` |  | count | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `n_negative` |  | count | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `n_scarcity` |  | count | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_max` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_median` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_min` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_q1` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_q3` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_iqr` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_max` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_median` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_min` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_minus_midday_median` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_q1` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_q3` |  | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `worst_interval_multiple` |  | ratio | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |

### `ercot_rtm_node_prices`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1570608.

- **Source:** ercot:NP6-905-CD ERCOT, Settlement Point Prices at Resource Nodes, Hubs and Load Zones (report type 12301) (https://www.ercot.com/mp/data-products/data-product-details?id=NP6-905-CD)
- **Method note:** [`docs/methods/ercot_rtm_node_prices.md`](../methods/ercot_rtm_node_prices.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Settlement Point Prices at Resource Nodes, Hubs and Load Zones. Via the Energy Research Warehouse (ERW), table `ercot_rtm_node_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example ercot:ABINDUST_RN, ercot:ADL_RN, ercot:AE_RN; 312 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-28T04:45:00Z to 2026-11-19T17:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -251.0 to 3522.5; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT15M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example ABINDUST_RN, ADL_RN, AE_RN; 312 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP6-905-CD | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1279835460, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1279839306, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1279843107; more than 5000 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-05T09:23:38Z to 2026-11-19T17:28:49Z; more than 5000 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1570608 |
| `x_point_type` | not yet written |  | text | AH, HU, LZ, LZ_DC, RN, SH | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `spp_rtm` |  | USD/MWh | 1570608 | 2026-09-28T04:45:00Z | 2026-11-19T17:00:00Z |

### `ercot_rtm_price_adders`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 603156.

- **Source:** ercot:NP6-792-ER ERCOT, Historical Real-Time ORDC and Reliability Deployment Price Adders and Reserves (https://www.ercot.com/mp/data-products/data-product-details?id=NP6-792-ER)
- **Method note:** [`docs/methods/ercot_rtm_price_adders.md`](../methods/ercot_rtm_price_adders.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Historical Real-Time ORDC and Reliability Deployment Price Adders and Reserves. Via the Energy Research Warehouse (ERW), table `ercot_rtm_price_adders`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:system | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2014-06-01T06:00:00Z to 2026-11-15T04:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 8993.6045; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | RTOFFPA, RTORDPA, RTORPA, RTRDPA | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP6-792-ER | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1065495488, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1169113636, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1180319793, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1298996044, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=468554538, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=505964801, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=643552126, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=644817014, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=644817015, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=694452063, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=751366904, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=814938847, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=899479048, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=969827183 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-13T06:34:15Z, 2026-10-13T06:34:23Z, 2026-10-13T06:34:28Z, 2026-10-13T06:34:32Z, 2026-10-13T06:34:36Z, 2026-10-13T06:34:41Z, 2026-10-13T06:34:45Z, 2026-10-13T06:34:49Z, 2026-10-13T06:34:54Z, 2026-10-13T06:34:57Z, 2026-10-13T06:35:03Z, 2026-10-13T06:35:07Z, 2026-10-13T06:35:10Z, 2026-11-15T17:50:32Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2015-01-02T16:00:28Z, 2016-01-07T21:44:38Z, 2019-01-08T15:53:35Z, 2019-01-17T20:19:27Z, 2020-01-02T18:30:02Z, 2021-01-01T15:26:33Z, 2022-01-01T15:26:31Z, 2023-03-02T20:04:14Z, 2024-01-01T15:09:09Z, 2025-01-01T15:09:34Z, 2025-12-08T17:21:55Z, 2026-01-08T23:58:14Z, 2026-11-15T16:12:49Z | 0 |

Variables (8):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `rtoffpa_max` |  | USD/MWh | 100878 | 2014-06-01T06:00:00Z | 2025-12-05T05:00:00Z |
| `rtoffpa_mean` |  | USD/MWh | 100878 | 2014-06-01T06:00:00Z | 2025-12-05T05:00:00Z |
| `rtordpa_max` |  | USD/MWh | 91547 | 2015-06-25T06:00:00Z | 2025-12-05T05:00:00Z |
| `rtordpa_mean` |  | USD/MWh | 91547 | 2015-06-25T06:00:00Z | 2025-12-05T05:00:00Z |
| `rtorpa_max` |  | USD/MWh | 100878 | 2014-06-01T06:00:00Z | 2025-12-05T05:00:00Z |
| `rtorpa_mean` |  | USD/MWh | 100878 | 2014-06-01T06:00:00Z | 2025-12-05T05:00:00Z |
| `rtrdpa_max` |  | USD/MWh | 8275 | 2025-12-05T07:00:00Z | 2026-11-15T04:00:00Z |
| `rtrdpa_mean` |  | USD/MWh | 8275 | 2025-12-05T07:00:00Z | 2026-11-15T04:00:00Z |

### `ercot_sced_esr_hourly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1637727.

- **Source:** ercot:NP3-965-ER ERCOT, 60-Day SCED Disclosure Reports (report type 13052),  document list (https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13052)
- **Method note:** [`docs/methods/ercot_sced_esr_hourly.md`](../methods/ercot_sced_esr_hourly.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). 60-Day SCED Disclosure Reports (the file 60d_ESR_Data_in_SCED: Energy Storage Resources in real time). Via the Energy Research Warehouse (ERW), table `ercot_sced_esr_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example ercot:ABINDUST_ESR1, ercot:ADL_ESR1, ercot:AE_ESR1; 342 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-02-01T06:00:00Z to 2026-08-28T04:00:00Z; 4991 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -240.00002 to 240.00002; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example ABINDUST_RN, ADL_RN, AE_RN; 293 distinct | 6935 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP3-965-ER | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1210699966, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1211087392, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1211618930; 208 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-05T09:15:29Z to 2026-10-26T17:49:02Z; 208 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-04-02T00:00:00Z to 2026-10-26T00:00:00Z; 208 distinct | 0 |
| `x_qse` | not yet written |  | text | for example QAETE1, QAETEL, QAMA1; 120 distinct | 0 |
| `x_sced_runs` | not yet written |  | integer | 11, 12, 13, 14, 15, 16, 17, 18, 19, 7 | 0 |
| `x_net_q1_mwh` | not yet written |  | number | -60.000005 to 60.000005; more than 5000 distinct | 0 |
| `x_net_q2_mwh` | not yet written |  | number | -60.000005 to 60.000005; more than 5000 distinct | 0 |
| `x_net_q3_mwh` | not yet written |  | number | -60.000005 to 60.000005; more than 5000 distinct | 0 |
| `x_net_q4_mwh` | not yet written |  | number | -60.000005 to 60.000005; more than 5000 distinct | 0 |
| `x_discharge_mwh` | not yet written |  | number | 0.0 to 240.00002; more than 5000 distinct | 0 |
| `x_charge_mwh` | not yet written |  | number | 0.0 to 240.00002; more than 5000 distinct | 0 |
| `x_base_point_mwh` | not yet written |  | number | -240.000015 to 240.000015; more than 5000 distinct | 0 |
| `x_hsl_mw` | not yet written |  | number | -8.8 to 240.0; 2335 distinct | 0 |
| `x_lsl_mw` | not yet written |  | number | -240.0 to 195.0; 2248 distinct | 0 |
| `x_soc_start_mwh` | not yet written |  | number | -703.6 to 974.9; more than 5000 distinct | 0 |
| `x_soc_min_mwh` | not yet written |  | number | -703.6 to 974.9; more than 5000 distinct | 0 |
| `x_soc_max_mwh` | not yet written |  | number | -0.3718 to 974.9; more than 5000 distinct | 0 |
| `x_as_regup_mwh` | not yet written |  | number | 0.0 to 269.745653; more than 5000 distinct | 0 |
| `x_as_regdn_mwh` | not yet written |  | number | 0.0 to 200.0; more than 5000 distinct | 0 |
| `x_as_rrspfr_mwh` | not yet written |  | number | 0.0 to 157.0; more than 5000 distinct | 0 |
| `x_as_rrsffr_mwh` | not yet written |  | number | 0.0 to 175.672674; more than 5000 distinct | 0 |
| `x_as_rrsufr_mwh` | not yet written |  | integer | 0 | 0 |
| `x_as_ecrs_mwh` | not yet written |  | number | 0.0 to 237.127168; more than 5000 distinct | 0 |
| `x_as_nspin_mwh` | not yet written |  | number | 0.0 to 118.98; more than 5000 distinct | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `net_output_mwh` |  | MWh | 1637727 | 2026-02-01T06:00:00Z | 2026-08-28T04:00:00Z |

### `ercot_storage_dam_awards_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 1244.

- **Source:** erw:ercot_storage_dam_awards ERW derived table, ERCOT storage resources' day-ahead awards by month (docs/methods/ercot_storage_dam_awards.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_dam_awards.md)
- **Method note:** [`docs/methods/ercot_storage_dam_awards.md`](../methods/ercot_storage_dam_awards.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT storage resources' day-ahead awards by month (docs/methods/ercot_storage_dam_awards.md). Via the Energy Research Warehouse (ERW), table `ercot_storage_dam_awards_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:esr_class_2_to_4h, ercot:esr_class_4h_and_over, ercot:esr_class_not_seen_rt, ercot:esr_class_under_2h, ercot:esr_fleet | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-12-01T00:00:00Z, 2026-01-01T00:00:00Z, 2026-02-01T00:00:00Z, 2026-03-01T00:00:00Z, 2026-04-01T00:00:00Z, 2026-05-01T00:00:00Z, 2026-06-01T00:00:00Z, 2026-07-01T00:00:00Z, 2026-08-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 40491721.2; 725 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD, USD/MW, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 1244 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_storage_dam_awards | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_dam_awards.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-05T03:29:22Z, 2026-10-27T17:23:55Z, 2026-11-15T17:37:22Z, 2026-11-16T16:48:22Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1244 |

Variables (28):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `days_held` |  | count | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `days_in_month` |  | count | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `days_missing` |  | count | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_bought_mwh` |  | MWh | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_bought_usd` |  | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_sold_mwh` |  | MWh | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_sold_usd` |  | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `mw` |  | MW | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours` |  | count | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours_energy_award` |  | count | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resources` |  | count | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resources_with_award` |  | count | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_ancillary_usd` |  | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_ancillary_usd_per_mw` |  | USD/MW | 43 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_ecrs_usd` |  | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_ecrs_usd_per_mw` |  | USD/MW | 43 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_energy_usd` |  | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_energy_usd_per_mw` |  | USD/MW | 43 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_nspin_usd` |  | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_nspin_usd_per_mw` |  | USD/MW | 43 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_regdn_usd` |  | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_regdn_usd_per_mw` |  | USD/MW | 43 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_regup_usd` |  | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_regup_usd_per_mw` |  | USD/MW | 43 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_rrs_usd` |  | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_rrs_usd_per_mw` |  | USD/MW | 43 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_total_usd` |  | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_total_usd_per_mw` |  | USD/MW | 43 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `ercot_storage_dam_offers_daily`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 20982.

- **Source:** erw:ercot_storage_dam_offers ERW derived table, ERCOT storage resources' day-ahead offers (docs/methods/ercot_storage_dam_offers.md),  computed from ERCOT's 60-Day DAM Disclosure Reports (NP3-966-ER), the files 60d_DAM_ESR_Data and 60d_DAM_ESR_ASOffers (https://www.ercot.com/mp/data-products/data-product-details?id=NP3-966-ER)
- **Method note:** [`docs/methods/ercot_storage_dam_offers.md`](../methods/ercot_storage_dam_offers.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT storage resources' day-ahead offers by day and by month (docs/methods/ercot_storage_dam_offers.md). Via the Energy Research Warehouse (ERW), table `ercot_storage_dam_offers_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:esr_fleet | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-12-06T00:00:00Z to 2026-08-31T00:00:00Z; 269 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 14698250.15; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, USD, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 20982 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_storage_dam_offers | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1190045004, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1190315373, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1190560109; 269 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-04T21:33:39Z to 2026-11-15T15:54:05Z; 269 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-02-04T22:53:33Z to 2026-10-30T12:41:46Z; 269 distinct | 0 |

Variables (78):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `as_award_mwh` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `as_offer_mwh` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `as_offer_mwh_unlisted` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_award_mwh` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_award_usd` |  | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_offer_mwh` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_offer_mwh_le_1` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_offer_mwh_le_100` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_offer_mwh_le_1000` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_offer_mwh_le_20` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_offer_mwh_le_5` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_offer_mwh_le_mcpc` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_unawarded_usd` |  | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_bid_mwh` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_bid_mwh_at_clearing` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_bought_mwh` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_offer_mwh` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_offer_mwh_at_clearing` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_offer_mwh_le_0` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_offer_mwh_le_100` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_offer_mwh_le_1000` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_offer_mwh_le_25` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_offer_mwh_le_250` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_offer_mwh_le_50` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_sold_mwh` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `limit_mwh` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `limit_mwh_as_offer` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `limit_mwh_award` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `limit_mwh_energy_offer` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `limit_mwh_no_offer` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `limit_mwh_no_offer_out` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `limit_mwh_out` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_award_mwh` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_award_usd` |  | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_offer_mwh` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_offer_mwh_le_1` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_offer_mwh_le_100` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_offer_mwh_le_1000` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_offer_mwh_le_20` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_offer_mwh_le_5` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_offer_mwh_le_mcpc` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_unawarded_usd` |  | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_award_mwh` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_award_usd` |  | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_offer_mwh` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_offer_mwh_le_1` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_offer_mwh_le_100` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_offer_mwh_le_1000` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_offer_mwh_le_20` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_offer_mwh_le_5` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_offer_mwh_le_mcpc` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_unawarded_usd` |  | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_award_mwh` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_award_usd` |  | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_offer_mwh` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_offer_mwh_le_1` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_offer_mwh_le_100` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_offer_mwh_le_1000` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_offer_mwh_le_20` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_offer_mwh_le_5` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_offer_mwh_le_mcpc` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_unawarded_usd` |  | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `resource_hours` |  | count | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `resource_hours_as_offer` |  | count | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `resource_hours_energy_offer` |  | count | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `resource_hours_no_offer` |  | count | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `resource_hours_out` |  | count | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `resources` |  | count | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_award_mwh` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_award_usd` |  | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_offer_mwh` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_offer_mwh_le_1` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_offer_mwh_le_100` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_offer_mwh_le_1000` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_offer_mwh_le_20` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_offer_mwh_le_5` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_offer_mwh_le_mcpc` |  | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_unawarded_usd` |  | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |

### `ercot_storage_dam_offers_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 819.

- **Source:** erw:ercot_storage_dam_offers ERW derived table, ERCOT storage resources' day-ahead offers (docs/methods/ercot_storage_dam_offers.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_dam_offers.md)
- **Method note:** [`docs/methods/ercot_storage_dam_offers.md`](../methods/ercot_storage_dam_offers.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT storage resources' day-ahead offers by day and by month (docs/methods/ercot_storage_dam_offers.md). Via the Energy Research Warehouse (ERW), table `ercot_storage_dam_offers_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:esr_fleet | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-12-01T00:00:00Z, 2026-01-01T00:00:00Z, 2026-02-01T00:00:00Z, 2026-03-01T00:00:00Z, 2026-04-01T00:00:00Z, 2026-05-01T00:00:00Z, 2026-06-01T00:00:00Z, 2026-07-01T00:00:00Z, 2026-08-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 28508190.28; 797 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD, USD/MW, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 819 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_storage_dam_offers | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_dam_offers.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-05T04:24:13Z, 2026-10-19T21:05:17Z, 2026-11-15T17:37:50Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 819 |

Variables (91):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `as_award_mwh` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_offer_mwh` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_offer_mwh_unlisted` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `days_held` |  | count | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `days_in_month` |  | count | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `days_missing` |  | count | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_award_mwh` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_award_usd` |  | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_award_usd_per_mw` |  | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_offer_mwh` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_offer_mwh_le_1` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_offer_mwh_le_100` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_offer_mwh_le_1000` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_offer_mwh_le_20` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_offer_mwh_le_5` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_offer_mwh_le_mcpc` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_unawarded_usd` |  | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_unawarded_usd_per_mw` |  | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_bid_mwh` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_bid_mwh_at_clearing` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_bought_mwh` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_offer_mwh` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_offer_mwh_at_clearing` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_offer_mwh_le_0` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_offer_mwh_le_100` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_offer_mwh_le_1000` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_offer_mwh_le_25` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_offer_mwh_le_250` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_offer_mwh_le_50` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_sold_mwh` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `limit_mwh` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `limit_mwh_as_offer` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `limit_mwh_award` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `limit_mwh_energy_offer` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `limit_mwh_no_offer` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `limit_mwh_no_offer_out` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `limit_mwh_out` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `mw` |  | MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_award_mwh` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_award_usd` |  | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_award_usd_per_mw` |  | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_offer_mwh` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_offer_mwh_le_1` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_offer_mwh_le_100` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_offer_mwh_le_1000` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_offer_mwh_le_20` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_offer_mwh_le_5` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_offer_mwh_le_mcpc` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_unawarded_usd` |  | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_unawarded_usd_per_mw` |  | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_award_mwh` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_award_usd` |  | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_award_usd_per_mw` |  | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_offer_mwh` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_offer_mwh_le_1` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_offer_mwh_le_100` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_offer_mwh_le_1000` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_offer_mwh_le_20` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_offer_mwh_le_5` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_offer_mwh_le_mcpc` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_unawarded_usd` |  | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_unawarded_usd_per_mw` |  | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_award_mwh` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_award_usd` |  | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_award_usd_per_mw` |  | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_offer_mwh` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_offer_mwh_le_1` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_offer_mwh_le_100` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_offer_mwh_le_1000` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_offer_mwh_le_20` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_offer_mwh_le_5` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_offer_mwh_le_mcpc` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_unawarded_usd` |  | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_unawarded_usd_per_mw` |  | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours` |  | count | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours_as_offer` |  | count | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours_energy_offer` |  | count | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours_no_offer` |  | count | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours_out` |  | count | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_award_mwh` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_award_usd` |  | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_award_usd_per_mw` |  | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_offer_mwh` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_offer_mwh_le_1` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_offer_mwh_le_100` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_offer_mwh_le_1000` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_offer_mwh_le_20` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_offer_mwh_le_5` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_offer_mwh_le_mcpc` |  | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_unawarded_usd` |  | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_unawarded_usd_per_mw` |  | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `ercot_storage_node_basis`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 2064.

- **Source:** erw:ercot_storage_realtime ERW derived table (docs/methods/ercot_storage_realtime.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_realtime.md)
- **Method note:** [`docs/methods/ercot_storage_realtime.md`](../methods/ercot_storage_realtime.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT storage in real time beside its day-ahead awards, by month, and the storage nodes' prices against the hub (docs/methods/ercot_storage_realtime.md). Via the Energy Research Warehouse (ERW), table `ercot_storage_node_basis`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example ercot:ABINDUST_RN, ercot:ADL_RN, ercot:AE_RN; 294 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-28T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 4.9614 to 4746.0; 767 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example ABINDUST_RN, ADL_RN, AE_RN; 293 distinct | 13 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_storage_realtime | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_realtime.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T19:55:40Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 2064 |

Variables (17):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `intervals` |  | count | 293 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `intervals_median` |  | count | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `mean_abs_difference` |  | USD/MWh | 293 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `mean_abs_difference_median` |  | USD/MWh | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `mean_hub` |  | USD/MWh | 294 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `mean_node` |  | USD/MWh | 293 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `mean_node_median` |  | USD/MWh | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `nodes` |  | count | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `nodes_spread_above_hub` |  | count | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `nodes_with_spread` |  | count | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `spread_hub` |  | USD/MWh | 294 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `spread_node` |  | USD/MWh | 293 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `spread_node_mean` |  | USD/MWh | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `spread_node_median` |  | USD/MWh | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `spread_node_p10` |  | USD/MWh | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `spread_node_p90` |  | USD/MWh | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `whole_days` |  | count | 294 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |

### `ercot_storage_rt_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 1620.

- **Source:** erw:ercot_storage_realtime ERW derived table (docs/methods/ercot_storage_realtime.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_realtime.md)
- **Method note:** [`docs/methods/ercot_storage_realtime.md`](../methods/ercot_storage_realtime.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT storage in real time beside its day-ahead awards, by month, and the storage nodes' prices against the hub (docs/methods/ercot_storage_realtime.md). Via the Energy Research Warehouse (ERW), table `ercot_storage_rt_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:esr_class_2_to_4h, ercot:esr_class_4h_and_over, ercot:esr_class_not_seen_rt, ercot:esr_class_under_2h, ercot:esr_fleet | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-02-01T00:00:00Z, 2026-03-01T00:00:00Z, 2026-04-01T00:00:00Z, 2026-05-01T00:00:00Z, 2026-06-01T00:00:00Z, 2026-07-01T00:00:00Z, 2026-08-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -283942.331 to 42395561.48; 1040 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD, USD/MW, USD/MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1620 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 1620 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_storage_realtime | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_realtime.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T19:55:40Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1620 |

Variables (47):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `as_da_ecrs_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_da_nspin_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_da_regdn_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_da_regup_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_da_rrs_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_imbalance_ecrs_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_imbalance_nspin_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_imbalance_regdn_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_imbalance_regup_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_imbalance_rrs_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_rt_ecrs_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_rt_nspin_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_rt_regdn_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_rt_regup_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_rt_rrs_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `da_bought_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `da_net_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `da_node_minus_hub_bought` |  | USD/MWh | 22 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `da_node_minus_hub_sold` |  | USD/MWh | 23 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `da_sold_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `days_held` |  | count | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `days_in_month` |  | count | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `intervals` |  | count | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `intervals_priced` |  | count | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `mw` |  | MW | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours` |  | count | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours_day_ahead_only` |  | count | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours_real_time_only` |  | count | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resources` |  | count | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_da_ancillary_usd` |  | USD | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_da_ancillary_usd_per_mw` |  | USD/MW | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_da_energy_usd` |  | USD | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_da_energy_usd_per_mw` |  | USD/MW | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_da_position_hub_usd` |  | USD | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_da_position_hub_usd_per_mw` |  | USD/MW | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_da_usd` |  | USD | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_da_usd_per_mw` |  | USD/MW | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_market_hub_usd` |  | USD | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_market_hub_usd_per_mw` |  | USD/MW | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_rt_deviation_hub_usd` |  | USD | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_rt_deviation_hub_usd_per_mw` |  | USD/MW | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_rt_output_hub_usd` |  | USD | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_rt_output_hub_usd_per_mw` |  | USD/MW | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rt_charge_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rt_deviation_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rt_discharge_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rt_net_mwh` |  | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `ercot_storage_rt_offers_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 175.

- **Source:** ercot:NP3-965-ER ERCOT, 60-Day SCED Disclosure Reports (60d_ESR_Data_in_SCED) (https://www.ercot.com/mp/data-products/data-product-details?id=NP3-965-ER)
- **Method note:** [`docs/methods/ercot_storage_realtime.md`](../methods/ercot_storage_realtime.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT storage fleet's real-time energy offers to sell by price band, by month, from ERCOT's 60-Day SCED Disclosure Reports (60d_ESR_Data_in_SCED, NP3-965-ER). Via the Energy Research Warehouse (ERW), table `ercot_storage_rt_offers_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:esr_fleet | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-02-01T00:00:00Z, 2026-03-01T00:00:00Z, 2026-04-01T00:00:00Z, 2026-05-01T00:00:00Z, 2026-06-01T00:00:00Z, 2026-07-01T00:00:00Z, 2026-08-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0249 to 14114469.608; 164 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, MWh/MW-day, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 175 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_storage_rt_offers | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_realtime.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T21:12:53Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 175 |

Variables (25):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `days_held` |  | count | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `days_in_month` |  | count | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `mw` |  | MW | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_any_mwh` |  | MWh | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_any_mwh_per_mw_day` |  | MWh/MW-day | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_0_mwh` |  | MWh | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_0_mwh_per_mw_day` |  | MWh/MW-day | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_0_share_pct` |  | pct | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_1000_mwh` |  | MWh | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_1000_mwh_per_mw_day` |  | MWh/MW-day | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_1000_share_pct` |  | pct | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_100_mwh` |  | MWh | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_100_mwh_per_mw_day` |  | MWh/MW-day | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_100_share_pct` |  | pct | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_250_mwh` |  | MWh | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_250_mwh_per_mw_day` |  | MWh/MW-day | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_250_share_pct` |  | pct | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_25_mwh` |  | MWh | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_25_mwh_per_mw_day` |  | MWh/MW-day | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_25_share_pct` |  | pct | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_50_mwh` |  | MWh | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_50_mwh_per_mw_day` |  | MWh/MW-day | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_50_share_pct` |  | pct | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resources` |  | count | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `runs` |  | count | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `ercot_transmission_projects`

What a row is: not yet written.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 2203.

- **Source:** ercot:tpit Electric Reliability Council of Texas (ERCOT), Transmission Project and Information Tracking (https://www.ercot.com/gridinfo/planning)
- **Method note:** [`docs/methods/ercot_transmission_projects.md`](../methods/ercot_transmission_projects.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Transmission Project and Information Tracking (TPIT). Via the Energy Research Warehouse (ERW), table `ercot_transmission_projects`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | none | text | for example ercot_tpit:07TPIT0069:10446, ercot_tpit:100018:100019, ercot_tpit:100020:100021; 2203 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2023-05-25 to 2033-12-15; 511 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others) | none | text | transmission_project | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | text | for example AEN, AEP, AEP TCC; 55 distinct | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 2203 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 2203 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 2203 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 2203 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | cancelled, completed, future, planned | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:tpit | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/files/docs/2022/03/02/ERCOT-October-TPIT-No-Cost-100126.xlsx | 0 |
| `x_project_number` | not yet written |  | text | for example 07TPIT0069, 100018, 100020; 2203 distinct | 0 |
| `x_phase` | not yet written |  | integer | 8143 to 116033; 2203 distinct | 0 |
| `x_title` | not yet written |  | text | for example 138kV Flewellen to Fort Bend Ckt 09G-60E Upgrades, 138kV transmission upgrade to serve Kirkland large load., 16th Street auto transformer replacement/addition.; 1803 distinct | 41 |
| `x_description` | not yet written |  | text | for example (5705) FOWLERTON to (5723) LOS ANGELES 138 kV Ckt 1 Rebuild [245 MVA Minimum] or double circuit existing, (5727) PAWNEE SWITCHING STATION to (5902) SAN MIGUEL GEN 138 kV Ckt 1 Rebuild [276 MVA Minimum], (In terms of completed Waterfowl substation) Loop new CEHE 138kV substation Odin (ODI) into Ckt.36 to create new Ckt.36 COPPER to Odin to Booster tap to Jones Creek.; 1794 distinct | 345 |
| `x_comment` | not yet written |  | text | for example 1/10/2023: Added information to clarify circuit rating., 1/10/2023: Added information to clarify timing for final circuit rating upgrade., 1/10/2023: Changes to description based on final design.; 83 distinct | 1821 |
| `x_from` | not yet written |  | text | for example 0, 199, 240; 1275 distinct | 255 |
| `x_to` | not yet written |  | text | for example -, 0, 170722; 1086 distinct | 797 |
| `x_ercot_status` | not yet written |  | text | Conceptual, In-Service, Planned, Under Construction | 31 |
| `x_owner` | not yet written |  | text | for example AEN, AEP, AEP TCC; 55 distinct | 0 |
| `x_projected_in_service` | not yet written |  | date | 2022-11-30 to 2033-12-15; 448 distinct | 0 |
| `x_actual_in_service` | not yet written |  | date | 2023-05-25 to 9999-01-01; 175 distinct | 1852 |
| `x_kv` | not yet written |  | integer | 115, 138, 345, 69, 765 | 1 |
| `x_new_circuit_miles` | not yet written |  | number | 0.0 to 257.45; 183 distinct | 6 |
| `x_upgraded_circuit_miles` | not yet written |  | number | 0.0 to 292.8; 436 distinct | 10 |
| `x_autotransformer_mva` | not yet written |  | integer | -536 to 8316; 35 distinct | 1 |
| `x_reactive_mvar` | not yet written |  | text | for example -100,0, -1200,0, -140,0; 90 distinct | 2005 |
| `x_county_start` | not yet written |  | text | for example Anderson, Andrews, Angelina; 185 distinct | 193 |
| `x_county_end` | not yet written |  | text | for example Anderson, Andrews, Angelina; 175 distinct | 769 |
| `x_tier` | not yet written |  | text | Tier 1, Tier 2, Tier 3, Tier 4 | 0 |
| `x_rpg_number` | not yet written |  | text | for example 18RPG012, 19RPG013, 19RPG018; 166 distinct | 1663 |
| `x_rtp_number` | not yet written |  | text | for example 2013-R102, 2013-R104, 2013-R25; 65 distinct | 2086 |
| `x_date_kind` | not yet written |  | text | actual, projected | 0 |
| `x_sheet` | not yet written |  | text | Cancelled, Completed, Future, Planned | 0 |

### `ercot_wind_solar_forecast`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 5322.

- **Source:** ercot:NP4-732-CD ERCOT, NP4-732-CD (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-732-CD)
- **Source:** ercot:NP4-745-CD ERCOT, NP4-745-CD (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-745-CD)
- **Method note:** [`docs/methods/ercot_wind_solar_forecast.md`](../methods/ercot_wind_solar_forecast.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). NP4-732-CD: hourly averaged actual and forecasted values; NP4-745-CD: hourly averaged actual and forecasted values. Via the Energy Research Warehouse (ERW), table `ercot_wind_solar_forecast`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:SYSTEM | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-27T05:00:00Z to 2026-11-26T15:00:00Z; 1451 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 47852.8; 4175 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 5322 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | SYSTEM | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP4-732-CD, ercot:NP4-745-CD | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13028, https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13483 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T09:30:26Z to 2026-11-19T17:41:55Z; 76 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 5322 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `solar_actual_mw` |  | MW | 1283 | 2026-09-27T05:00:00Z | 2026-11-19T15:00:00Z |
| `solar_forecast_24h_mw` |  | MW | 1378 | 2026-09-30T06:00:00Z | 2026-11-26T15:00:00Z |
| `wind_actual_mw` |  | MW | 1283 | 2026-09-27T05:00:00Z | 2026-11-19T15:00:00Z |
| `wind_forecast_24h_mw` |  | MW | 1378 | 2026-09-30T06:00:00Z | 2026-11-26T15:00:00Z |

### `ercot_wind_solar_hsl_daily`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 300.

- **Source:** ercot:np4_732_745 Wind and Solar Power Production, Hourly Averaged Actual and Forecasted Values (NP4-732-CD, NP4-745-CD) (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-745-CD)
- **Method note:** [`docs/methods/ercot_wind_solar_hsl_daily.md`](../methods/ercot_wind_solar_hsl_daily.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Wind and Solar Power Production, Hourly Averaged Actual and Forecasted Values (NP4-732-CD, NP4-745-CD). Via the Energy Research Warehouse (ERW), table `ercot_wind_solar_hsl_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:system | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-19T00:00:00Z to 2026-11-15T00:00:00Z; 50 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 2600.84 to 653022.27; 300 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 300 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 300 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:np4_732_745 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1277035825, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1277448708, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1277855609; 50 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-27T08:30:58Z to 2026-11-16T14:49:57Z; 33 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 300 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `solar_below_hsl_mwh` |  | MWh | 50 | 2026-09-19T00:00:00Z | 2026-11-15T00:00:00Z |
| `solar_generation_mwh` |  | MWh | 50 | 2026-09-19T00:00:00Z | 2026-11-15T00:00:00Z |
| `solar_hsl_mwh` |  | MWh | 50 | 2026-09-19T00:00:00Z | 2026-11-15T00:00:00Z |
| `wind_below_hsl_mwh` |  | MWh | 50 | 2026-09-19T00:00:00Z | 2026-11-15T00:00:00Z |
| `wind_generation_mwh` |  | MWh | 50 | 2026-09-19T00:00:00Z | 2026-11-15T00:00:00Z |
| `wind_hsl_mwh` |  | MWh | 50 | 2026-09-19T00:00:00Z | 2026-11-15T00:00:00Z |

### `ercot_wind_solar_hsl_hourly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 17757.

- **Source:** ercot:np4_742_745_region ERCOT NP4-742-CD, Wind Power Production, Hourly Averaged Actual and Forecasted Values by Geographical Region (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-742-CD)
- **Source:** ercot:np4_742_745_region ERCOT NP4-745-CD, Solar Power Production, Hourly Averaged Actual and Forecasted Values by Geographical Region (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-745-CD)
- **Method note:** [`docs/methods/ercot_wind_solar_hsl_hourly.md`](../methods/ercot_wind_solar_hsl_hourly.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Wind and Solar Power Production, Hourly Averaged Actual and Forecasted Values by Geographical Region (NP4-742-CD, NP4-745-CD) [terms: "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." (https://www.ercot.com/help/terms, read 6 October 2026)]. Via the Energy Research Warehouse (ERW), table `ercot_wind_solar_hsl_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:solar:CenterEast, ercot:solar:CenterWest, ercot:solar:FarEast, ercot:solar:FarWest, ercot:solar:NorthWest, ercot:solar:SouthEast, ercot:system, ercot:wind:COASTAL, ercot:wind:NORTH, ercot:wind:PANHANDLE, ercot:wind:SOUTH, ercot:wind:WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-28T05:00:00Z to 2026-11-16T12:00:00Z; 1184 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 33464.82; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 17757 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | COASTAL, CenterEast, CenterWest, FarEast, FarWest, NORTH, NorthWest, PANHANDLE, SOUTH, SouthEast, WEST | 4733 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:np4_742_745_region | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1280661939, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1280661943, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1281045111; 146 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T09:32:02Z to 2026-11-16T14:51:24Z; 172 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 17757 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `solar_generation_mw` |  | MW | 8288 | 2026-09-28T05:00:00Z | 2026-11-16T12:00:00Z |
| `solar_hsl_mw` |  | MW | 1182 | 2026-09-28T05:00:00Z | 2026-11-16T12:00:00Z |
| `wind_generation_mw` |  | MW | 7104 | 2026-09-28T05:00:00Z | 2026-11-16T12:00:00Z |
| `wind_hsl_mw` |  | MW | 1183 | 2026-09-28T05:00:00Z | 2026-11-16T12:00:00Z |

### `ercot_wind_solar_hsl_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 45.

- **Source:** erw:ercot_wind_solar_hsl_monthly ERW derived table (warehouse/connectors/ercot_wind_solar_history.py) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/curtailment.md)
- **Method note:** [`docs/methods/curtailment.md`](../methods/curtailment.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERW derived table: ERCOT output below HSL by month, the ERW's estimate (docs/methods/curtailment.md). Via the Energy Research Warehouse (ERW), table `ercot_wind_solar_hsl_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:solar:CenterEast, ercot:solar:CenterWest, ercot:solar:FarEast, ercot:solar:FarWest, ercot:solar:NorthWest, ercot:solar:SouthEast, ercot:system, ercot:wind:COASTAL, ercot:wind:NORTH, ercot:wind:PANHANDLE, ercot:wind:SOUTH, ercot:wind:WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-10-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1113619.43, 2607227.26, 365821.2, 420812.25, 5.5953, 5061592.3, 590543.8, 6.3796, 613736.39, 6274391.08, 6537999.76, 695505.64, 744.0, 844441.06, 8668423.42, 874816.54, 877076.59, 911097.53, 922889.51, 9256808.64 | 0 |
| `unit` | The unit of the row's value | none | text | MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 45 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | COASTAL, CenterEast, CenterWest, FarEast, FarWest, NORTH, NorthWest, PANHANDLE, SOUTH, SouthEast, WEST | 12 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_wind_solar_hsl_monthly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/warehouse/connectors/ercot_wind_solar_history.py | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-05T23:20:19Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 45 |

Variables (12):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `solar_below_hsl_mwh` |  | MWh | 1 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_below_hsl_share_pct` |  | pct | 1 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_generation_mwh` |  | MWh | 7 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_hours_held` |  | count | 7 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_hours_in_month` |  | count | 7 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_hsl_mwh` |  | MWh | 1 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_below_hsl_mwh` |  | MWh | 1 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_below_hsl_share_pct` |  | pct | 1 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_generation_mwh` |  | MWh | 6 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_hours_held` |  | count | 6 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_hours_in_month` |  | count | 6 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_hsl_mwh` |  | MWh | 1 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |

### `ercot_wind_solar_output_hourly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 52608.

- **Source:** ercot:PG7-126-M ERCOT PG7-126-M, Hourly Aggregated Wind and Solar Output (https://www.ercot.com/mp/data-products/data-product-details?id=PG7-126-M)
- **Method note:** [`docs/methods/ercot_wind_solar_output_hourly.md`](../methods/ercot_wind_solar_output_hourly.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Hourly Aggregated Wind and Solar Output (yearly workbook: system-wide hourly wind and solar output) [terms: "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." (https://www.ercot.com/help/terms, read 6 October 2026)]. Via the Energy Research Warehouse (ERW), table `ercot_wind_solar_output_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:system | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-01-01T06:00:00Z to 2026-01-01T05:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.0000046131608542e-05 to 29503.08663357205; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 52608 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 52608 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:PG7-126-M | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1068801799, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1182433954, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=971575038 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T09:22:54Z, 2026-10-07T09:32:46Z, 2026-10-07T09:32:54Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 52608 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `solar_generation_mw` |  | MW | 26304 | 2023-01-01T06:00:00Z | 2026-01-01T05:00:00Z |
| `wind_generation_mw` |  | MW | 26304 | 2023-01-01T06:00:00Z | 2026-01-01T05:00:00Z |

### `ercot_zone_load_hourly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 933534.

- **Source:** ercot:load_hist Electric Reliability Council of Texas (ERCOT), Hourly Load Data Archives, native load by weather zone (https://www.ercot.com/gridinfo/load/load_hist)
- **Method note:** [`docs/methods/ercot_zone_load_hourly.md`](../methods/ercot_zone_load_hourly.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Hourly Load Data Archives, native load by weather zone [terms: "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." (https://www.ercot.com/help/terms, read 6 October 2026)]. Via the Energy Research Warehouse (ERW), table `ercot_zone_load_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:COAST, ercot:EAST, ercot:FWEST, ercot:NCENT, ercot:NORTH, ercot:SCENT, ercot:SOUTH, ercot:WEST, ercot:system | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T06:00:00Z to 2026-11-01T04:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 488.272293 to 91133.727696; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_load | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | COAST, EAST, ERCOT, FAR_WEST, FWEST, NCENT, NORTH, NORTH_C, SCENT, SOUTH, SOUTHERN, SOUTH_C, WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:load_hist | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/files/docs/2016/01/07/native_load_2015.xls, https://www.ercot.com/files/docs/2017/01/10/native_Load_2016.zip, https://www.ercot.com/files/docs/2018/01/09/native_load_2017.zip, https://www.ercot.com/files/docs/2019/01/07/native_load_2018.zip, https://www.ercot.com/files/docs/2020/01/09/Native_Load_2019.zip, https://www.ercot.com/files/docs/2021/01/12/Native_Load_2020.zip, https://www.ercot.com/files/docs/2021/11/12/Native_Load_2021.zip, https://www.ercot.com/files/docs/2022/02/08/Native_Load_2022.zip, https://www.ercot.com/files/docs/2023/02/09/Native_Load_2023.zip, https://www.ercot.com/files/docs/2024/02/06/Native_Load_2024.zip, https://www.ercot.com/files/docs/2025/02/11/Native_Load_2025.zip, https://www.ercot.com/files/docs/2026/02/10/Native_Load_2026.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T01:43:07Z, 2026-10-07T01:43:12Z, 2026-10-07T01:43:18Z, 2026-10-07T01:43:23Z, 2026-10-07T01:43:28Z, 2026-10-07T01:43:33Z, 2026-10-07T01:43:38Z, 2026-10-07T01:43:43Z, 2026-10-07T01:43:49Z, 2026-10-07T01:43:54Z, 2026-10-07T01:43:59Z, 2026-11-16T11:50:31Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2021-11-13T17:29:09Z, 2021-11-13T17:30:35Z, 2021-11-13T17:31:05Z, 2021-11-13T17:31:54Z, 2021-11-13T17:32:35Z, 2021-11-13T17:34:44Z, 2022-01-07T22:39:00Z, 2023-01-31T16:39:00Z, 2024-01-08T19:15:00Z, 2025-01-10T16:32:00Z, 2026-02-04T22:35:00Z, 2026-11-06T19:50:00Z | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `load` |  | MW | 933534 | 2015-01-01T06:00:00Z | 2026-11-01T04:00:00Z |

### `ercot_zone_prices_history`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2497536.

- **Source:** ERCOT NP4-180-ER Historical DAM Load Zone and Hub Prices (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-180-ER)
- **Source:** ERCOT NP6-785-ER Historical RTM Load Zone and Hub Prices (https://www.ercot.com/mp/data-products/data-product-details?id=NP6-785-ER)
- **Method note:** [`docs/methods/ercot_zone_prices_history.md`](../methods/ercot_zone_prices_history.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Historical DAM Load Zone and Hub Prices; Historical RTM Load Zone and Hub Prices. Via the Energy Research Warehouse (ERW), table `ercot_zone_prices_history`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | ercot:LZ_AEN, ercot:LZ_CPS, ercot:LZ_HOUSTON, ercot:LZ_LCRA, ercot:LZ_NORTH, ercot:LZ_RAYBN, ercot:LZ_SOUTH, ercot:LZ_WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T06:00:00Z to 2026-11-15T05:45:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -147.45 to 9349.19; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT15M, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | ercot_dam, ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | LZ_AEN, LZ_CPS, LZ_HOUSTON, LZ_LCRA, LZ_NORTH, LZ_RAYBN, LZ_SOUTH, LZ_WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP4-180-ER, ercot:NP6-785-ER | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1065468714, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1065471230, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1177667469, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1177737535, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1298953847, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1298966804, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=505281022, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=505283161, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=547013266, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=547016749, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=592990685, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=592992943, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=642564845, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=642564849, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=694281912, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=694284436, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=751351545, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=751356439, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=814918746, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=814922832, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=886627599, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=886632075, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=969803138, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=969805139 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T09:15:51Z, 2026-10-07T09:16:03Z, 2026-10-07T09:17:32Z, 2026-10-07T09:17:38Z, 2026-10-07T09:17:44Z, 2026-10-07T09:17:50Z, 2026-10-07T09:17:56Z, 2026-10-07T09:18:02Z, 2026-10-07T09:18:08Z, 2026-10-07T09:18:15Z, 2026-10-07T09:18:21Z, 2026-10-07T09:18:27Z, 2026-10-07T09:18:44Z, 2026-10-07T09:18:51Z, 2026-10-07T09:18:58Z, 2026-10-07T09:19:06Z, 2026-10-07T09:19:12Z, 2026-10-07T09:19:19Z, 2026-10-07T09:19:26Z, 2026-10-07T09:19:32Z, 2026-10-07T09:19:39Z, 2026-10-07T09:19:45Z, 2026-11-15T18:09:45Z, 2026-11-15T18:09:58Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2016-01-01T14:03:08Z, 2016-01-01T14:21:39Z, 2017-01-01T14:03:36Z, 2017-01-01T14:33:00Z, 2018-01-01T14:02:53Z, 2018-01-01T14:24:25Z, 2019-01-01T14:02:39Z, 2019-01-01T14:25:24Z, 2020-01-01T14:03:19Z, 2020-01-01T14:25:15Z, 2021-01-01T14:08:09Z, 2021-01-01T14:41:25Z, 2022-01-01T14:13:33Z, 2022-01-01T14:38:17Z, 2023-01-01T14:11:13Z, 2023-01-01T14:34:04Z, 2024-01-01T14:10:11Z, 2024-01-01T14:19:08Z, 2025-01-01T14:07:33Z, 2025-01-01T14:18:28Z, 2026-01-01T14:44:09Z, 2026-01-01T19:25:58Z, 2026-11-15T14:01:47Z, 2026-11-15T14:38:34Z | 0 |
| `year` | The operating year a history table was published by | none | integer | 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `spp_dam` |  | USD/MWh | 832512 | 2015-01-01T06:00:00Z | 2026-11-15T05:00:00Z |
| `spp_rtm` |  | USD/MWh | 1665024 | 2015-01-01T06:00:00Z | 2026-11-15T05:45:00Z |

