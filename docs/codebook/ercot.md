# Codebook: ercot

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 38 public tables (6 entities, 2 events, 30 series; tiers: 12 derived, 26 source); 38 documented in full.

- [`ercot_4cp_intervals`](#ercot_4cp_intervals): One of ERCOT's four coincident peaks of a year (the 15-minute interval of the system's highest load in each summer month, June to September) with ERCOT's load in it.
- [`ercot_all_hub_prices_history`](#ercot_all_hub_prices_history): ERCOT's settlement point price at one of its six trading hubs for one interval of one operating year from 2015, day-ahead (hourly) or real-time (15-minute).
- [`ercot_as_prices`](#ercot_as_prices): ERCOT's day-ahead market clearing price for capacity (MCPC) of one ancillary service for one delivery hour.
- [`ercot_as_prices_daily`](#ercot_as_prices_daily): One daily summary of ERCOT's hourly day-ahead clearing prices for capacity of one ancillary service, for one local day.
- [`ercot_as_prices_monthly`](#ercot_as_prices_monthly): One monthly summary of ERCOT's hourly day-ahead clearing prices for capacity of one ancillary service, for one local month.
- [`ercot_as_quantities`](#ercot_as_quantities): The MW of one ancillary service ERCOT planned to procure in its day-ahead market for one delivery hour, from the plan published the day before delivery.
- [`ercot_cdr_reserve_margins`](#ercot_cdr_reserve_margins): One line of the Seasonal Summary of ERCOT's Capacity, Demand and Reserves report (CDR) for one season at its peak load hour or its peak net load hour.
- [`ercot_cdr_units`](#ercot_cdr_units): One generating or storage unit (or one planned group of small generators) listed on the Unit Details sheet of ERCOT's Capacity, Demand and Reserves report (CDR).
- [`ercot_dam_cleared_energy`](#ercot_dam_cleared_energy): The energy bought in ERCOT's day-ahead market in one delivery hour, summed over every settlement point.
- [`ercot_dam_esr_awards`](#ercot_dam_esr_awards): One ERCOT Energy Storage Resource (a battery) in one hour of the day-ahead market, its High Sustained Limit with its awards and limits as ERCOT's 60-day disclosure prints them.
- [`ercot_grid_notices`](#ercot_grid_notices): One ERCOT notice (an Energy Emergency Alert, rotating outages, a conservation appeal, a watch, a control-room message and others) for one Central day it covers.
- [`ercot_hub_prices_daily`](#ercot_hub_prices_daily): One daily statistic of ERCOT's day-ahead or real-time price at one of its six trading hubs, for one complete local operating day from 2015.
- [`ercot_interconnection_queue`](#ercot_interconnection_queue): One position in ERCOT's Generation Interconnection Status (GIS) report, a project asking to connect generation or storage to ERCOT's grid.
- [`ercot_large_load_status`](#ercot_large_load_status): One figure stated in words in one of ERCOT's monthly Large Load Interconnection Status Update reports.
- [`ercot_node_places`](#ercot_node_places): One ERCOT resource node (a settlement point where a generating or storage resource is settled) placed in a county and load zone by the CDR units at its station.
- [`ercot_node_planned_generation`](#ercot_node_planned_generation): One placed ERCOT resource node with the planned generation in its county, from ERCOT's active interconnection queue and EIA-860M's planned generators.
- [`ercot_node_transmission`](#ercot_node_transmission): One placed ERCOT resource node with the transmission project phases of ERCOT's TPIT workbook (Transmission Project and Information Tracking) that start or end in its county.
- [`ercot_node_wires_utilities`](#ercot_node_wires_utilities): One placed ERCOT resource node with the wires utilities EIA-861 lists as serving its county, Texas's delivery-only companies named apart.
- [`ercot_peak_premium_annual`](#ercot_peak_premium_annual): One price statistic of ERCOT's 15-minute real-time prices at one trading hub over one ERCOT operating year, for all intervals or one block of the day, or the same over the year to date.
- [`ercot_peak_premium_monthly`](#ercot_peak_premium_monthly): One price statistic of ERCOT's 15-minute real-time prices at one trading hub over one local calendar month, for all intervals or one block of the day.
- [`ercot_peak_premium_node_monthly`](#ercot_peak_premium_node_monthly): One price statistic of ERCOT's 15-minute real-time prices at one settlement point over one local calendar month, for all intervals or one block of the day.
- [`ercot_rtm_node_prices`](#ercot_rtm_node_prices): ERCOT's real-time settlement point price at one settlement point (a storage resource's node, a hub, a load zone or a DC tie) for one 15-minute interval.
- [`ercot_rtm_price_adders`](#ercot_rtm_price_adders): One of ERCOT's real-time reserve price adders (added to the real-time energy price) over one hour, its time-weighted mean or its highest interval value.
- [`ercot_sced_esr_hourly`](#ercot_sced_esr_hourly): One ERCOT Energy Storage Resource (a battery) in one hour of real-time dispatch (SCED), its telemetered net output and limits, state of charge and real-time ancillary service awards, from ERCOT's 60-day SCED disclosure.
- [`ercot_storage_dam_awards_monthly`](#ercot_storage_dam_awards_monthly): What ERCOT's Energy Storage Resources (batteries) were awarded in the day-ahead market in one local month, for the whole fleet or one duration class.
- [`ercot_storage_dam_offers_daily`](#ercot_storage_dam_offers_daily): What ERCOT's Energy Storage Resources offered in the day-ahead market, and how much of it was awarded, summed over one operating day for the whole fleet.
- [`ercot_storage_dam_offers_monthly`](#ercot_storage_dam_offers_monthly): What ERCOT's Energy Storage Resources offered in the day-ahead market, and how much of it was awarded, summed over one local month for the whole fleet.
- [`ercot_storage_node_basis`](#ercot_storage_node_basis): For one storage resource's settlement point (or all of them summed up), its real-time price against the hub average HB_HUBAVG over the days of node prices held.
- [`ercot_storage_rt_monthly`](#ercot_storage_rt_monthly): What ERCOT's storage resources did in real time beside what they were awarded day-ahead, over the operating days both disclosures hold in one local month, for the fleet or one duration class.
- [`ercot_storage_rt_offers_monthly`](#ercot_storage_rt_offers_monthly): What ERCOT's storage fleet offered to sell in real-time dispatch (SCED), by price limit, summed over one local month.
- [`ercot_transmission_projects`](#ercot_transmission_projects): One phase of a transmission project the transmission owners report to ERCOT's Transmission Project and Information Tracking (TPIT) workbook, future, planned, completed or cancelled.
- [`ercot_wind_solar_forecast`](#ercot_wind_solar_forecast): ERCOT's system-wide wind or solar output for one hour, actual or as forecast a day ahead.
- [`ercot_wind_solar_hsl_daily`](#ercot_wind_solar_hsl_daily): ERCOT's system-wide wind or solar output, High Sustained Limit (HSL), or output below the HSL, summed over one operating day.
- [`ercot_wind_solar_hsl_hourly`](#ercot_wind_solar_hsl_hourly): ERCOT's wind or solar output or High Sustained Limit for one hour, system-wide or in one of ERCOT's wind or solar regions.
- [`ercot_wind_solar_hsl_monthly`](#ercot_wind_solar_hsl_monthly): ERCOT's wind or solar output, High Sustained Limit (HSL), or output below the HSL, summed over one Central month, system-wide or in one of ERCOT's wind or solar regions.
- [`ercot_wind_solar_output_hourly`](#ercot_wind_solar_output_hourly): ERCOT's system-wide wind or solar output for one hour, from ERCOT's yearly Hourly Aggregated Wind and Solar Output workbooks (2023 to 2025).
- [`ercot_zone_load_hourly`](#ercot_zone_load_hourly): ERCOT's native load in one weather zone, or ERCOT's total, for one hour, from its Hourly Load Data Archives.
- [`ercot_zone_prices_history`](#ercot_zone_prices_history): ERCOT's settlement point price at one load zone for one interval of one operating year from 2015, day-ahead (hourly, eight load zones) or real-time (15-minute, the four competitive load zones).

### `ercot_4cp_intervals`

One of ERCOT's four coincident peaks of a year (the 15-minute interval of the system's highest load in each summer month, June to September) with ERCOT's load in it.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 28.

- **Time:** ts_utc is the interval's start in UTC, 15 minutes before the time ERCOT prints, read as the interval's end in Central prevailing time.
- **Revisions:** Each write deletes the file and builds the table again from every saved workbook. vintage is the list's posting date at 00:00:00Z; empty for the years of the 1996-2020 zip.
- **Source:** ercot:NP9-83-M ERCOT, Four Coincident Peak Calculations (report type 13037; prior years: the page's Key Documents) (https://www.ercot.com/mktinfo/data_agg/4cp)
- **Method note:** [`docs/methods/ercot_4cp_intervals.md`](../methods/ercot_4cp_intervals.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Four Coincident Peak Calculations (NP9-83-M; the years before 2021 from the page's 1996-2020 zip). Via the Energy Research Warehouse (ERW), table `ercot_4cp_intervals`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:system in every row: ERCOT's whole system | none | text | ercot:system | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-06-27T21:45:00Z to 2025-09-04T22:15:00Z; 28 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 64692.523772 to 85636.884588; 28 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT15M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_4cp in every row: the four coincident peak calculation | none | text | ercot_4cp | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: ERCOT in every row, not a price node | none | text | ERCOT | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP9-83-M | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/files/docs/2022/01/13/1996-2020_FourCoincidentPeakCalculations.zip, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1055377059, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1164129560, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=879528147, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=961277079 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-20T10:12:39Z, 2026-10-20T10:12:41Z, 2026-10-20T10:12:43Z, 2026-10-20T10:12:45Z, 2026-10-20T10:12:47Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: ERCOT's posting date of the workbook at 00:00:00Z; empty for the years of the 1996-2020 zip, which states none | none | utc time | 2022-11-28T00:00:00Z, 2023-11-27T00:00:00Z, 2024-11-25T00:00:00Z, 2025-11-24T00:00:00Z | 12 |
| `x_year` | The year of the summer whose peaks the row is one of | none | integer | 2018, 2019, 2020, 2022, 2023, 2024, 2025 | 0 |
| `x_month` | The month of the peak, YYYY-MM | none | text | for example 2018-06, 2018-07, 2018-08; 28 distinct | 0 |
| `x_interval_local` | The time ERCOT prints for the interval, read as the interval's end in Central prevailing time | none | text | for example 2018-06-27 17:00, 2018-07-19 17:00, 2018-08-23 16:45; 28 distinct | 0 |
| `x_published` | ERCOT's posting date of the workbook (the date part of the list's PublishDate) | none | date | 2022-11-28, 2023-11-27, 2024-11-25, 2025-11-24 | 12: The years of the 1996-2020 zip, which states no posting date |
| `x_document` | The file name of the workbook the row is read from | none | text | ERCOTFourCoincidentPeakLoadCalculation2018.xlsx, ERCOTFourCoincidentPeakLoadCalculation2019.xlsx, ERCOTFourCoincidentPeakLoadCalculation2020.xlsx, rpt.00013037.0000000000000000.20221128.090923347.4CP20221128.xlsx, rpt.00013037.0000000000000000.20231127.102940992.4CP20231127.xlsx, rpt.00013037.0000000000000000.20241125.121105134.4CP20241125.xlsx, rpt.00013037.0000000000000000.20251124.083820245.4CP20251124.xlsx | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `cp4_load_mw` | ERCOT's coincident peak load of the month: the Total row of its Four Coincident Peak Load Calculation, the sum of the load entities' load in the interval (DC tie exports, block load transfer exports and wholesale storage load excluded), MW | MW | 28 | 2018-06-27T21:45:00Z | 2025-09-04T22:15:00Z |

### `ercot_all_hub_prices_history`

ERCOT's settlement point price at one of its six trading hubs for one interval of one operating year from 2015, day-ahead (hourly) or real-time (15-minute).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3124224.

- **Time:** ts_utc is the start of the interval in UTC; the year is ERCOT's operating year in Central time (America/Chicago).
- **Revisions:** Merged by (entity, variable, ts_utc) into each year's member and consolidated by market and year; a year is written from ERCOT's yearly archive, the current year extended from the live window, and a workbook read later replaces the appended rows. vintage is ERCOT's document publish time.
- **Source:** ERCOT NP4-180-ER Historical DAM Load Zone and Hub Prices (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-180-ER)
- **Source:** ERCOT NP6-785-ER Historical RTM Load Zone and Hub Prices (https://www.ercot.com/mp/data-products/data-product-details?id=NP6-785-ER)
- **Method note:** [`docs/methods/automated_analysis_findings.md`](../methods/automated_analysis_findings.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Historical DAM Load Zone and Hub Prices; Historical RTM Load Zone and Hub Prices. Via the Energy Research Warehouse (ERW), table `ercot_all_hub_prices_history`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:<hub> | none | text | ercot:HB_BUSAVG, ercot:HB_HOUSTON, ercot:HB_HUBAVG, ercot:HB_NORTH, ercot:HB_SOUTH, ercot:HB_WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T06:00:00Z to 2026-11-19T05:45:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -251.0 to 9315.45; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT15M, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_dam (day-ahead, hourly) or ercot_rtm (real-time, 15-minute) | none | text | ercot_dam, ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: ERCOT's trading hub: HB_HOUSTON, HB_NORTH, HB_SOUTH, HB_WEST (the four regional hubs), HB_HUBAVG (ERCOT's average of the four) and HB_BUSAVG (ERCOT's average over the hubs' buses) | none | text | HB_BUSAVG, HB_HOUSTON, HB_HUBAVG, HB_NORTH, HB_SOUTH, HB_WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP4-180-ER, ercot:NP4-190-CD, ercot:NP6-785-ER, ercot:NP6-905-CD | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1065468714, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1065471230, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1177667469; 4531 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-26T00:09:58Z to 2026-11-19T17:27:27Z; 2184 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: ERCOT's document publish time; empty on a few rows | none | utc time | 2016-01-01T14:03:08Z to 2026-11-16T06:02:02Z; 3763 distinct | 4608 |
| `year` | The operating year a history table was published by. Here: ERCOT's operating year in Central time, the member the row came from | none | integer | 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `spp_dam` | ERCOT's day-ahead settlement point price at the hub, hourly (spp here is ERCOT's 'settlement point price', not the grid SPP) | USD/MWh | 624384 | 2015-01-01T06:00:00Z | 2026-11-17T05:00:00Z |
| `spp_rtm` | ERCOT's real-time settlement point price at the hub, 15-minute (spp here is ERCOT's 'settlement point price', not the grid SPP) | USD/MWh | 2499840 | 2015-01-01T06:00:00Z | 2026-11-19T05:45:00Z |

### `ercot_as_prices`

ERCOT's day-ahead market clearing price for capacity (MCPC) of one ancillary service for one delivery hour.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 339332.

- **Time:** ts_utc is the start of the delivery hour in UTC (ERCOT publishes the hour ending, Central time).
- **Revisions:** Every run reads the whole series again (every yearly file from 2018, then the daily files) and merges it by (entity, variable, ts_utc), so an hour read again replaces the one held; a day first held from the daily report is replaced by the yearly file's row. vintage is the document's publish time.
- **Source:** ercot:NP4-181-ER ERCOT, Historical DAM Clearing Prices for Capacity (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-181-ER)
- **Source:** ercot:NP4-188-CD ERCOT, DAM Clearing Prices for Capacity (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-188-CD)
- **Method note:** [`docs/methods/ercot_as_prices.md`](../methods/ercot_as_prices.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). DAM Clearing Prices for Capacity; Historical DAM Clearing Prices for Capacity. Via the Energy Research Warehouse (ERW), table `ercot_as_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:<service>, the ancillary service | none | text | ercot:ECRS, ercot:NSPIN, ercot:REGDN, ercot:REGUP, ercot:RRS | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-01-01T06:00:00Z to 2026-10-31T04:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 25674.3; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MW-hour | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_dam in every row: ERCOT's day-ahead market | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The ancillary service, not a place: REGUP Regulation Up, REGDN Regulation Down, RRS Responsive Reserve, NSPIN Non-Spin, ECRS ERCOT Contingency Reserve Service (from June 2023) | none | text | ECRS, NSPIN, REGDN, REGUP, RRS | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP4-181-ER, ercot:NP4-188-CD | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1065466940, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1177658395, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1290346030, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1290652168, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1290729005, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1291119920, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1291545998, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1291928786, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1292323467, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=642564840, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=694281905, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=751350601, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=814917148, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=886625668, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=969797266 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T15:15:21Z, 2026-10-02T15:15:25Z, 2026-10-02T15:15:29Z, 2026-10-02T15:15:33Z, 2026-10-02T15:15:37Z, 2026-10-02T15:15:41Z, 2026-10-02T15:15:45Z, 2026-10-02T15:15:49Z, 2026-10-25T14:54:34Z, 2026-10-25T14:54:44Z, 2026-10-26T15:05:41Z, 2026-10-27T14:57:31Z, 2026-10-28T15:05:55Z, 2026-10-29T14:53:35Z, 2026-10-30T15:04:41Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The publish time of ERCOT's yearly or daily document the row came from | none | utc time | 2019-01-01T13:00:48Z, 2020-01-01T13:01:16Z, 2021-01-01T13:04:29Z, 2022-01-01T13:04:42Z, 2023-01-01T13:03:38Z, 2024-01-01T13:00:55Z, 2025-01-01T13:01:05Z, 2026-01-01T13:18:09Z, 2026-10-24T17:32:44Z, 2026-10-25T13:01:00Z, 2026-10-25T17:33:05Z, 2026-10-26T17:33:14Z, 2026-10-27T18:15:55Z, 2026-10-28T17:32:48Z, 2026-10-29T17:33:24Z | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `mcpc_dam` | Day-ahead market clearing price for capacity of the service (MCPC), USD per MW held for one hour | USD/MW-hour | 339332 | 2018-01-01T06:00:00Z | 2026-10-31T04:00:00Z |

### `ercot_as_prices_daily`

One daily summary of ERCOT's hourly day-ahead clearing prices for capacity of one ancillary service, for one local day.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 70695.

- **Time:** ts_utc is the local (America/Chicago) operating day at 00:00:00Z.
- **Revisions:** Rebuilt from ercot_as_prices by each run of the builder; vintage is not filled.
- **Source:** erw:ercot_as_prices_rollup ERW derived daily and monthly summary of ERCOT reserve prices (docs/methods/ercot_as_prices_rollup.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_as_prices_rollup.md)
- **Method note:** [`docs/methods/ercot_as_prices_rollup.md`](../methods/ercot_as_prices_rollup.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT reserve prices by day and by month (docs/methods/ercot_as_prices_rollup.md). Via the Energy Research Warehouse (ERW), table `ercot_as_prices_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:<service>, the ancillary service (ECRS, NSPIN, REGDN, REGUP, RRS) | none | text | ercot:ECRS, ercot:NSPIN, ercot:REGDN, ercot:REGUP, ercot:RRS | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-01-01T00:00:00Z to 2026-10-30T00:00:00Z; 3225 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 25674.3; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MW-hour, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_dam in every row: ERCOT's day-ahead market | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The ancillary service, not a place | none | text | ECRS, NSPIN, REGDN, REGUP, RRS | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_as_prices_rollup | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_as_prices_rollup.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T22:00:13Z, 2026-10-08T15:09:03Z, 2026-10-09T15:01:20Z, 2026-10-10T15:08:34Z, 2026-10-11T15:33:44Z, 2026-10-12T15:02:16Z, 2026-10-13T15:02:46Z, 2026-10-14T15:37:34Z, 2026-10-15T15:45:50Z, 2026-10-19T16:25:27Z, 2026-10-19T20:48:32Z, 2026-10-21T15:10:55Z, 2026-10-22T15:04:35Z, 2026-10-23T15:03:51Z, 2026-10-24T15:11:29Z, 2026-10-25T14:54:52Z, 2026-10-26T15:05:51Z, 2026-10-27T14:57:42Z, 2026-10-28T15:06:06Z, 2026-10-29T14:53:43Z, 2026-10-30T15:04:50Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 70695 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `mcpc_dam_hours` | The hours of the day held | count | 14139 | 2018-01-01T00:00:00Z | 2026-10-30T00:00:00Z |
| `mcpc_dam_hours_in_day` | The hours the local day has: 24, or 23 and 25 on the clock-change days | count | 14139 | 2018-01-01T00:00:00Z | 2026-10-30T00:00:00Z |
| `mcpc_dam_max` | Highest hourly clearing price of the day, as published, USD per MW held for one hour | USD/MW-hour | 14139 | 2018-01-01T00:00:00Z | 2026-10-30T00:00:00Z |
| `mcpc_dam_mean` | Mean of the day's hourly clearing prices held, four decimals, USD per MW held for one hour | USD/MW-hour | 14139 | 2018-01-01T00:00:00Z | 2026-10-30T00:00:00Z |
| `mcpc_dam_min` | Lowest hourly clearing price of the day, as published, USD per MW held for one hour | USD/MW-hour | 14139 | 2018-01-01T00:00:00Z | 2026-10-30T00:00:00Z |

### `ercot_as_prices_monthly`

One monthly summary of ERCOT's hourly day-ahead clearing prices for capacity of one ancillary service, for one local month.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 2325.

- **Time:** ts_utc is the first day of the local (America/Chicago) month at 00:00:00Z.
- **Revisions:** Rebuilt from ercot_as_prices by each run of the builder; vintage is not filled.
- **Source:** erw:ercot_as_prices_rollup ERW derived daily and monthly summary of ERCOT reserve prices (docs/methods/ercot_as_prices_rollup.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_as_prices_rollup.md)
- **Method note:** [`docs/methods/ercot_as_prices_rollup.md`](../methods/ercot_as_prices_rollup.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT reserve prices by day and by month (docs/methods/ercot_as_prices_rollup.md). Via the Energy Research Warehouse (ERW), table `ercot_as_prices_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:<service>, the ancillary service (ECRS, NSPIN, REGDN, REGUP, RRS) | none | text | ercot:ECRS, ercot:NSPIN, ercot:REGDN, ercot:REGUP, ercot:RRS | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-01-01T00:00:00Z to 2026-10-01T00:00:00Z; 106 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 25674.3; 997 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MW-hour, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_dam in every row: ERCOT's day-ahead market | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The ancillary service, not a place | none | text | ECRS, NSPIN, REGDN, REGUP, RRS | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_as_prices_rollup | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_as_prices_rollup.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T22:00:13Z, 2026-10-08T15:09:03Z, 2026-10-14T15:37:34Z, 2026-10-19T16:25:27Z, 2026-10-19T20:48:32Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2325 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `mcpc_dam_hours` | The hours of the month held | count | 465 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `mcpc_dam_hours_in_month` | The hours the local month has | count | 465 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `mcpc_dam_max` | Highest hourly clearing price of the month, as published, USD per MW held for one hour | USD/MW-hour | 465 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `mcpc_dam_mean` | Mean of the month's hourly clearing prices held, four decimals, USD per MW held for one hour | USD/MW-hour | 465 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `mcpc_dam_min` | Lowest hourly clearing price of the month, as published, USD per MW held for one hour | USD/MW-hour | 465 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |

### `ercot_as_quantities`

The MW of one ancillary service ERCOT planned to procure in its day-ahead market for one delivery hour, from the plan published the day before delivery.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 4800.

- **Time:** ts_utc is the start of the delivery hour in UTC (ERCOT gives the hour ending in Central time; DSTFlag Y marks the repeated autumn hour).
- **Revisions:** Merged by (entity, variable, ts_utc); a run keeps of each daily file only the delivery day after its publish day, a day read again replaces the one held, and days ERCOT's list has dropped are kept. vintage is the file's PublishDate.
- **Source:** ercot:np4-33-cd ERCOT, DAM Ancillary Service Plan, NP4-33-CD ( (https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=12316)
- **Method note:** [`docs/methods/ercot_as_quantities.md`](../methods/ercot_as_quantities.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). DAM Ancillary Service Plan (NP4-33-CD). Via the Energy Research Warehouse (ERW), table `ercot_as_quantities`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:<service>, the ancillary service | none | text | ercot:ECRS, ercot:NSPIN, ercot:REGDN, ercot:REGUP, ercot:RRS | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-03T05:00:00Z to 2026-10-13T04:00:00Z; 960 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 246 to 3936; 189 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_dam in every row: ERCOT's day-ahead market | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The ancillary service, not a place: REGUP Regulation Up, REGDN Regulation Down, RRS Responsive Reserve, NSPIN Non-Spin, ECRS ERCOT Contingency Reserve Service | none | text | ECRS, NSPIN, REGDN, REGUP, RRS | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:np4-33-cd | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1269584411, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1269981073, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1270379366; 40 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-03T10:23:53Z to 2026-10-11T20:04:22Z; 34 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The PublishDate of ERCOT's daily file (10:00 UTC the day before delivery) | none | utc time | 2026-09-02T10:00:00Z to 2026-10-11T10:00:00Z; 40 distinct | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `quantity_mw_plan` | The MW of the service ERCOT plans to procure in the day-ahead market for the hour (DAM Ancillary Service Plan, NP4-33-CD) | MW | 4800 | 2026-09-03T05:00:00Z | 2026-10-13T04:00:00Z |

### `ercot_cdr_reserve_margins`

One line of the Seasonal Summary of ERCOT's Capacity, Demand and Reserves report (CDR) for one season at its peak load hour or its peak net load hour.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1600.

- **Time:** ts_utc is the season's first day at 00:00:00Z (spring 1 March, summer 1 June, fall 1 September, winter 1 December of its first year).
- **Revisions:** A snapshot replaced whole by each run with the newest report ERCOT's page links; vintage is the report's posting date.
- **Source:** ercot:cdr Electric Reliability Council of Texas (ERCOT), Capacity, Demand and Reserves Report (https://www.ercot.com/gridinfo/resource)
- **Method note:** [`docs/methods/ercot_cdr_reserve_margins.md`](../methods/ercot_cdr_reserve_margins.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Capacity, Demand and Reserves Report. Via the Energy Research Warehouse (ERW), table `ercot_cdr_reserve_margins`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot_cdr:<season>:<peak_load \| peak_net_load>: each season at ERCOT's peak load hour and at its peak net load hour | none | text | ercot_cdr:fall:peak_load, ercot_cdr:fall:peak_net_load, ercot_cdr:spring:peak_load, ercot_cdr:spring:peak_net_load, ercot_cdr:summer:peak_load, ercot_cdr:summer:peak_net_load, ercot_cdr:winter:peak_load, ercot_cdr:winter:peak_net_load | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-03-01T00:00:00Z, 2026-06-01T00:00:00Z, 2026-09-01T00:00:00Z, 2026-12-01T00:00:00Z, 2027-03-01T00:00:00Z, 2027-06-01T00:00:00Z, 2027-09-01T00:00:00Z, 2027-12-01T00:00:00Z, 2028-03-01T00:00:00Z, 2028-06-01T00:00:00Z, 2028-09-01T00:00:00Z, 2028-12-01T00:00:00Z, 2029-03-01T00:00:00Z, 2029-06-01T00:00:00Z, 2029-09-01T00:00:00Z, 2029-12-01T00:00:00Z, 2030-03-01T00:00:00Z, 2030-06-01T00:00:00Z, 2030-09-01T00:00:00Z, 2030-12-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -3693.245562235888 to 141703.70549374598; 608 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P3M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot in every row | none | text | ercot | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: ERCOT's season and hour as printed (Summer 2026, peak load hour 17), not a price node | none | text | for example Fall 2026, peak load hour 17, Fall 2026, peak net load hour 20, Fall 2027, peak load hour 17; 40 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:cdr | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/files/docs/2025/12/19/CapacityDemandandReservesReport_December2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T01:40:30Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The report's posting date at 00:00:00Z (from its address) | none | utc time | 2025-12-19T00:00:00Z | 0 |
| `x_hour` | The hour ending ERCOT names for the season's peak load or peak net load | none | integer | 17, 19, 20, 21, 8 | 0 |
| `x_report` | The file name of the CDR report | none | text | CapacityDemandandReservesReport_December2025.xlsx | 0 |

Variables (40):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dc_ties` | Non-Synchronous Ties (ERCOT's DC ties), MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `energy_efficiency_savings` | Energy Efficiency Program Savings, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `firm_peak_load` | Firm Peak Load: the load forecast after the adjustments, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `less_controllable_load` | Less: Controllable Load Resources not included elsewhere, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `less_emergency_response_service` | Less: Emergency Response Service, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `less_load_resources_ecrs` | Less: Load Resources providing ERCOT Contingency Reserve Service, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `less_load_resources_nonspin` | Less: Load Resources providing Non-Spinning Reserves, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `less_load_resources_rrs` | Less: Load Resources providing Responsive Reserves, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `less_rooftop_pv` | Less: Incremental Rooftop PV (rooftop solar), MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `less_tdsp_load_management` | Less: TDSP Standard Offer load management programs, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `less_voltage_reduction` | Less: Distribution Voltage Reduction, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_coastal_wind` | Operational capacity: Coastal Wind, counted at ERCOT's ELCC, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_far_west_solar` | Operational capacity: Far West Solar, counted at ERCOT's ELCC, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_hydro` | Operational capacity: Hydroelectric, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_less_switchable_unavailable` | Operational capacity: less Switchable Capacity Unavailable to ERCOT, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_mothballed` | Operational capacity: Available Mothballed, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_other_solar` | Operational capacity: Other Solar, counted at ERCOT's ELCC, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_other_wind` | Operational capacity: Other Wind, counted at ERCOT's ELCC, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_panhandle_wind` | Operational capacity: Panhandle Wind, counted at ERCOT's ELCC, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_pending_retirement` | Operational capacity: Capacity Pending Retirement, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_private_use_networks` | Operational capacity: Private Use Networks, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_rmr` | Operational capacity: RMR Capacity, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_storage` | Operational capacity: Energy Storage, counted at ERCOT's ELCC, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_switchable` | Operational capacity: Switchable Capacity, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_thermal` | Operational capacity: Installed Seasonal-rated Thermal, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_total` | Operational Generation Capacity, Total, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `operational_west_solar` | Operational capacity: West Solar, counted at ERCOT's ELCC, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_coastal_wind` | Planned resource additions: Coastal Wind, counted at ERCOT's ELCC, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_far_west_solar` | Planned resource additions: Far West Solar, counted at ERCOT's ELCC, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_other_solar` | Planned resource additions: Other Solar, counted at ERCOT's ELCC, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_other_wind` | Planned resource additions: Other Wind, counted at ERCOT's ELCC, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_panhandle_wind` | Planned resource additions: Panhandle Wind, counted at ERCOT's ELCC, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_storage` | Planned resource additions: Energy Storage, counted at ERCOT's ELCC, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_thermal` | Planned resource additions: Thermal Resources, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_total` | Planned Generation Capacity Total, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_unconfirmed_retirements` | Unconfirmed Planned Retirements, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `planned_west_solar` | Planned resource additions: West Solar, counted at ERCOT's ELCC, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `reserve_margin` | ERCOT's reserve margin: total capacity less firm peak load, over firm peak load, times 100 (pct) | pct | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `total_capacity` | Total Capacity, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |
| `total_seasonal_load` | Total Seasonal Load: ERCOT's load forecast for the season, MW | MW | 40 | 2026-03-01T00:00:00Z | 2030-12-01T00:00:00Z |

### `ercot_cdr_units`

One generating or storage unit (or one planned group of small generators) listed on the Unit Details sheet of ERCOT's Capacity, Demand and Reserves report (CDR).

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 1772.

- **Time:** No time column. vintage is the report's posting date; the table is a snapshot of the newest report as read on its retrieved_at.
- **Revisions:** A snapshot replaced whole by each run with the newest CDR workbook ERCOT's resource adequacy page links; earlier editions are not kept.
- **Source:** ercot:cdr:unit_details Electric Reliability Council of Texas (ERCOT), Capacity, Demand and Reserves Report, Unit Details (https://www.ercot.com/gridinfo/resource)
- **Method note:** [`docs/methods/ercot_cdr_units.md`](../methods/ercot_cdr_units.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Capacity, Demand and Reserves Report, Unit Details. Via the Energy Research Warehouse (ERW), table `ercot_cdr_units`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: ercot_cdr_unit:<unit code, else INR, else the unit's name>:<fuel> | none | text | for example ercot_cdr_unit:16INR0049:SOLAR_W, ercot_cdr_unit:19599_1_GOLD_SPIKE:SOLAR_O, ercot_cdr_unit:19599_2_GOLD_SPIKE:SOLAR_O; 1772 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: generator in every row | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it. Here: ERCOT's unit name | none | text | for example 7V SOLAR U1, 7V SOLAR U2, 7V SOLAR U3; 1755 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-TX in every row | none | text | US-TX | 0 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: Empty in every row: the sheet gives no coordinates | degree | empty | no cell holds a value | 1772 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: Empty in every row: the sheet gives no coordinates | degree | empty | no cell holds a value | 1772 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: ERCOT's installed capacity of the unit | MW | number | -400.0 to 1390.0; 989 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Mapped from the first part of ERCOT's CDR status (x_cdr_status): OPER and RMR to operating, PLAN to planned, MOTH and EXT to suspended | none | text | operating, planned, suspended | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The in-service date as ERCOT gives it; empty for the four DC ties and the planned group row | none | date | 1928-01-01 to 2029-07-01; 873 distinct | 5 |
| `operator` | The operator or owner, as the publisher writes it. Here: Empty in every row: the sheet names no operator | none | empty | no cell holds a value | 1772 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:cdr:unit_details | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/files/docs/2025/12/19/CapacityDemandandReservesReport_December2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T01:40:30Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The report's posting date (from the workbook's address) | none | utc time | 2025-12-19T00:00:00Z | 0 |
| `x_unit_code` | ERCOT's unit code (the source's name: Unit Code) | none | text | for example 19599_1_GOLD_SPIKE, 19599_2_GOLD_SPIKE, 19599_GOLD_SPIKE; 1458 distinct | 312: ERCOT gives no unit code (312 planned units, keyed by their INR) |
| `x_inr` | The interconnection request number (INR) of the unit (the source's name: Interconnection Request Number (INR)) | none | text | for example 12INR0059b, 15INR0064b, 16INR0049; 431 distinct | 1269: ERCOT gives no INR |
| `x_technology` | ERCOT's technology code of the unit, as printed (PV, BA, WT, CC, GT, ST, IC, HY, MWH) (the source's name: Technology) | none | text | BA, CC, GT, HY, IC, MWH, PV, ST, WT | 0 |
| `x_fuel` | ERCOT's fuel code of the unit, as printed (GAS, STORAGE, SOLAR-O, WIND-O, COAL, NUCLEAR and others) (the source's name: Fuel) | none | text | BIOMASS, COAL, DIESEL, GAS, HYDRO, MWH, NUCLEAR, SOLAR-FW, SOLAR-O, SOLAR-W, STORAGE, WIND-C, WIND-O, WIND-P | 0 |
| `x_cdr_status` | ERCOT's own CDR status code (OPER, PLAN, OPER-SYN, MOTH-IND, EXT-OUT and others), from which status is mapped (the source's name: CDR Status) | none | text | EXT-OUT, MOTH-IND, MOTH-SEA, OPER, OPER-SLF, OPER-SYN, OPER-SYN-SLF, OPER-UNFC, OPER-UNR, PLAN, PLAN-RPR, PLAN-SLF, RMR | 0 |
| `x_attribute` | ERCOT's CDR resource attribute code, as printed (CONV, CONV-DGR, DC-TIE, SWGR-AVA and others) (the source's name: CDR Resource Attribute) | none | text | CONV, CONV-DGR, CONV-SLF, CONV-SODG, CONV-TGR, DC-TIE, SWGR-AVA, SWGR-UNA | 0 |
| `x_county` | The county of the unit, as ERCOT prints it (the source's name: County) | none | text | for example ANDERSON, ANDREWS, ANGELINA; 184 distinct | 1: The planned group row of small generators, which has no county |
| `x_zone` | ERCOT's zone of the unit (COASTAL, HOUSTON, NORTH, PANHANDLE, SOUTH, WEST) (the source's name: Zone) | none | text | COASTAL, HOUSTON, NORTH, PANHANDLE, SOUTH, WEST | 1: The planned group row of small generators, which has no zone |
| `x_summer_2026` | The capability ERCOT lists for the unit at the start of summer 2026 | MW | number | -400.0 to 1293.2; 679 distinct | 0 |
| `x_summer_2027` | The capability ERCOT lists for the unit at the start of summer 2027 | MW | number | -400.0 to 1293.2; 747 distinct | 0 |
| `x_summer_2028` | The capability ERCOT lists for the unit at the start of summer 2028 | MW | number | -400.0 to 1293.2; 803 distinct | 0 |
| `x_summer_2029` | The capability ERCOT lists for the unit at the start of summer 2029 | MW | number | -400.0 to 1300.0; 818 distinct | 0 |
| `x_summer_2030` | The capability ERCOT lists for the unit at the start of summer 2030 | MW | number | -400.0 to 1300.0; 817 distinct | 0 |
| `x_winter_2026_2027` | The capability ERCOT lists for the unit at the start of winter 2026-2027 | MW | number | -389.0 to 1353.2; 700 distinct | 0 |
| `x_winter_2027_2028` | The capability ERCOT lists for the unit at the start of winter 2027-2028 | MW | number | -389.0 to 1353.2; 772 distinct | 0 |
| `x_winter_2028_2029` | The capability ERCOT lists for the unit at the start of winter 2028-2029 | MW | number | -389.0 to 1353.2; 806 distinct | 0 |
| `x_winter_2029_2030` | The capability ERCOT lists for the unit at the start of winter 2029-2030 | MW | number | -389.0 to 1353.2; 812 distinct | 0 |
| `x_winter_2030_2031` | The capability ERCOT lists for the unit at the start of winter 2030-2031 | MW | number | -389.0 to 1353.2; 810 distinct | 0 |
| `x_spring_2026` | The capability ERCOT lists for the unit at the start of spring 2026 | MW | number | -179.0 to 1323.2; 653 distinct | 0 |
| `x_spring_2027` | The capability ERCOT lists for the unit at the start of spring 2027 | MW | number | -389.0 to 1323.2; 722 distinct | 0 |
| `x_spring_2028` | The capability ERCOT lists for the unit at the start of spring 2028 | MW | number | -389.0 to 1323.2; 793 distinct | 0 |
| `x_spring_2029` | The capability ERCOT lists for the unit at the start of spring 2029 | MW | number | -389.0 to 1350.0; 815 distinct | 0 |
| `x_spring_2030` | The capability ERCOT lists for the unit at the start of spring 2030 | MW | number | -389.0 to 1350.0; 818 distinct | 0 |
| `x_fall_2026` | The capability ERCOT lists for the unit at the start of fall 2026 | MW | number | -195.0 to 1323.2; 696 distinct | 0 |
| `x_fall_2027` | The capability ERCOT lists for the unit at the start of fall 2027 | MW | number | -195.0 to 1323.2; 769 distinct | 0 |
| `x_fall_2028` | The capability ERCOT lists for the unit at the start of fall 2028 | MW | number | -195.0 to 1323.2; 808 distinct | 0 |
| `x_fall_2029` | The capability ERCOT lists for the unit at the start of fall 2029 | MW | number | -195.0 to 1350.0; 815 distinct | 0 |
| `x_fall_2030` | The capability ERCOT lists for the unit at the start of fall 2030 | MW | number | -195.0 to 1350.0; 815 distinct | 0 |

Waiting for a second look: x_technology: ERCOT's codes (PV, BA, WT, CC, GT, ST, IC, HY, MWH) are kept as printed; their meanings are not spelled out in the method note or the connector.; x_attribute: ERCOT's CDR resource attribute codes (CONV, CONV-DGR, CONV-SLF, CONV-SODG, CONV-TGR, DC-TIE, SWGR-AVA, SWGR-UNA) are not spelled out in the repository's documents.; x_fuel: the suffixes of ERCOT's fuel codes (SOLAR-FW, SOLAR-W, SOLAR-O, WIND-C, WIND-P, WIND-O) are not spelled out in the method note or the connector..

### `ercot_dam_cleared_energy`

The energy bought in ERCOT's day-ahead market in one delivery hour, summed over every settlement point.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 816.

- **Time:** ts_utc is the start of the hour in UTC (ERCOT gives the hour ending in Central time; RepeatedHourFlag Y marks the repeated autumn hour).
- **Revisions:** Merged by (entity, variable, ts_utc); an hour read again replaces the one held, and the table grows past the 31 days ERCOT lists. vintage is not filled.
- **Source:** ercot:NP4-192-CD Electric Reliability Council of Texas (ERCOT), NP4-192-CD, DAM Total Energy Purchased (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-192-CD)
- **Method note:** [`docs/methods/ercot_dam_cleared_energy.md`](../methods/ercot_dam_cleared_energy.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). NP4-192-CD, DAM Total Energy Purchased. Via the Energy Research Warehouse (ERW), table `ercot_dam_cleared_energy`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:system in every row: ERCOT's whole system | none | text | ercot:system | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-23T05:00:00Z to 2026-11-17T05:00:00Z; 816 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 27811.1 to 52634.7; 812 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_dam in every row: ERCOT's day-ahead market | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The text 'Total_DAM_Energy_Bought, summed over settlement points' in every row: the figure summed, not a place | none | text | Total_DAM_Energy_Bought, summed over settlement points | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP4-192-CD | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1277674205, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1278079535, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1278479657; 34 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T20:27:09Z to 2026-11-16T11:49:05Z; 34 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 816 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dam_cleared_energy` | The sum of ERCOT's Total_DAM_Energy_Bought over every settlement point for the hour (NP4-192-CD); ERCOT names no unit, read as MWh | MWh | 816 | 2026-09-23T05:00:00Z | 2026-11-17T05:00:00Z |

### `ercot_dam_esr_awards`

One ERCOT Energy Storage Resource (a battery) in one hour of the day-ahead market, its High Sustained Limit with its awards and limits as ERCOT's 60-day disclosure prints them.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2042277.

- **Time:** ts_utc is the start of the hour in UTC (ERCOT gives the Delivery Date and the Hour Ending in Central prevailing time).
- **Revisions:** One operating day appended at a time after the last held; a day is never rewritten once held. vintage is ERCOT's publication time of the day's zip (the operating day plus 60 days).
- **Source:** ercot:NP3-966-ER ERCOT, 60-Day DAM Disclosure Reports,  document list (https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13051)
- **Method note:** [`docs/methods/ercot_dam_esr_awards.md`](../methods/ercot_dam_esr_awards.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). 60-Day DAM Disclosure Reports (the file 60d_DAM_ESR_Data: Energy Storage Resources). Via the Energy Research Warehouse (ERW), table `ercot_dam_esr_awards`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:<Resource Name>, the storage resource | none | text | for example ercot:ABINDUST_ESR1, ercot:ADL_ESR1, ercot:AE_ESR1; 339 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-12-06T06:00:00Z to 2026-09-01T04:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -9.9 to 240.0; 1141 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_dam in every row: ERCOT's day-ahead market | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The resource's settlement point | none | text | for example ABINDUST_RN, ADL_RN, AE_RN; 295 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP3-966-ER | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1190045004, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1190315373, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1190560109; 269 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-04T21:33:39Z to 2026-11-15T15:54:05Z; 269 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: ERCOT's publication time of the day's zip; its Central date is the operating day plus 60 days | none | utc time | 2026-02-04T22:53:33Z to 2026-10-30T12:41:46Z; 269 distinct | 0 |
| `x_qse` | The scheduling entity (QSE) of the resource, ERCOT's code (the source's name: QSE) | none | text | for example QAETE1, QAETEL, QAMA1; 120 distinct | 0 |
| `x_dme` | not documented by the source (the source's name: DME) | none | text | for example Y2WPER, YAETEL, YAGPC2; 185 distinct | 1895: ERCOT's cell is blank |
| `x_resource_status` | ERCOT's status of the resource for the hour, as printed (ON, OUT, ONTEST, ONOS) (the source's name: Resource Status) | none | text | ON, ONOS, ONTEST, OUT | 0 |
| `x_lsl_mw` | The resource's Low Sustained Limit for the hour (negative: charging) (the source's name: LSL) | MW | number | -240.0 to 156.0; 376 distinct | 0 |
| `x_energy_award_mw` | The day-ahead energy award (negative is a purchase, charging) (the source's name: Awarded Quantity) | MW | number | -240.0 to 216.0; 2982 distinct | 1046971: No award (a blank award stays blank, not zero) |
| `x_energy_price_usd_per_mwh` | The day-ahead energy price at the resource's own settlement point (the source's name: Energy Settlement Point Price) | USD/MWh | number | -205.72 to 22618.19; more than 5000 distinct | 0 |
| `x_regup_award_mw` | The day-ahead award of Regulation Up (the source's name: RegUp Awarded) | MW | number | 0.0 to 350.0; 1708 distinct | 848995: No award |
| `x_regup_mcpc` | The day-ahead market clearing price for capacity (MCPC) of Regulation Up (the source's name: RegUp MCPC) | USD per MW per hour | number | 0.0 to 896.96; 776 distinct | 848995: Blank on the same rows as the award columns (no ancillary service award printed) |
| `x_regdn_award_mw` | The day-ahead award of Regulation Down (the source's name: RegDown Awarded) | MW | number | 0.0 to 308.9; 1633 distinct | 848995: No award |
| `x_regdn_mcpc` | The day-ahead market clearing price for capacity (MCPC) of Regulation Down (the source's name: RegDown MCPC) | USD per MW per hour | number | 0.0 to 26.71; 560 distinct | 848995: Blank on the same rows as the award columns (no ancillary service award printed) |
| `x_rrspfr_award_mw` | The day-ahead award of Responsive Reserve, its PFR kind (the source's name: RRSPFR Awarded) | MW | number | 0.0 to 157.0; 1560 distinct | 848995: No award |
| `x_rrsffr_award_mw` | The day-ahead award of Responsive Reserve, its FFR kind (the source's name: RRSFFR Awarded) | MW | number | 0.0 to 62.5; 340 distinct | 848995: No award |
| `x_rrsufr_award_mw` | The day-ahead award of Responsive Reserve, its UFR kind (the source's name: RRSUFR Awarded) | MW | integer | 0 | 848995: No award |
| `x_rrs_mcpc` | The day-ahead market clearing price for capacity (MCPC) of Responsive Reserve, one price for its three kinds (the source's name: RRS MCPC) | USD per MW per hour | number | 0.05 to 999.02; 602 distinct | 848995: Blank on the same rows as the award columns (no ancillary service award printed) |
| `x_ecrs_award_mw` | The day-ahead award of ERCOT Contingency Reserve Service (ECRS) (the source's name: ECRSSD Awarded) | MW | number | 0.0 to 240.0; 1747 distinct | 848995: No award |
| `x_ecrs_mcpc` | The day-ahead market clearing price for capacity (MCPC) of ECRS (the source's name: ECRS MCPC) | USD per MW per hour | number | 0.01 to 1000.65; 669 distinct | 848995: Blank on the same rows as the award columns (no ancillary service award printed) |
| `x_nonspin_award_mw` | The day-ahead award of Non-Spinning Reserve (Non-Spin) (the source's name: NonSpin Awarded) | MW | number | 0.0 to 302.0; 1369 distinct | 848995: No award |
| `x_nonspin_mcpc` | The day-ahead market clearing price for capacity (MCPC) of Non-Spin (the source's name: NonSpin MCPC) | USD per MW per hour | number | 0.25 to 432.13; 975 distinct | 848995: Blank on the same rows as the award columns (no ancillary service award printed) |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `hsl_mw` | The resource's High Sustained Limit (HSL) for the hour, the most it can sustain, MW, as ERCOT prints it | MW | 2042277 | 2025-12-06T06:00:00Z | 2026-09-01T04:00:00Z |

Waiting for a second look: x_dme: the meaning of ERCOT's DME column is not written in the header, the connector or the method note.; x_resource_status: ERCOT's codes ON, OUT, ONTEST and ONOS are kept as printed and not spelled out in the repository's documents..

### `ercot_grid_notices`

One ERCOT notice (an Energy Emergency Alert, rotating outages, a conservation appeal, a watch, a control-room message and others) for one Central day it covers.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 178.

- **Time:** event_date is the Central day the notice covers (the days it names, else the day it was issued); x_issued_at is when it was issued.
- **Revisions:** Merged by event_id; each run keeps the rows it read before, so the table only grows. No vintage column.
- **Source:** ercot:news_releases ERCOT, News Releases,  ercot:operations_messages ERCOT, Operations Messages (https://www.ercot.com/services/comm/mkt_notices/opsmessages)
- **Method note:** [`docs/methods/ercot_grid_notices.md`](../methods/ercot_grid_notices.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). News Releases (grid conditions: EEAs, conservation appeals, watches); Operations Messages (the control room's notices). Via the Energy Research Warehouse (ERW), table `ercot_grid_notices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: ercot_notice:<day>:<event_type>:<a 10-character hash of the source, address, issue time and text> | none | text | for example ercot_notice:2011-02-02:rotating_outages:940f126d07, ercot_notice:2011-02-03:update:0ab5ac164a, ercot_notice:2011-02-08:power_watch:129e58267d; 178 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which). Here: The Central day the notice covers, YYYY-MM-DD | none | date | 2011-02-02 to 2026-10-15; 142 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: Read from the notice's words: eea1 to eea3, rotating_outages, conservation_appeal, voluntary_conservation, weather_watch, power_watch, ocn_weather, ocn, advisory, watch, emergency_notice, emergency_test, update, statement | none | text | advisory, conservation_appeal, eea1, eea2, emergency_test, ocn_weather, power_watch, rotating_outages, statement, update, voluntary_conservation, watch, weather_watch | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: ERCOT in every row | none | text | ERCOT | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 178 |
| `mw` | The capacity involved, in megawatts. Here: Not filled: no cell holds a value | MW | empty | no cell holds a value | 178 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise. Here: Not filled: no cell holds a value | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 178 |
| `currency` | The currency of the price, as an ISO 4217 code (USD). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 178 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: ended for a news release that ends or cancels a notice, issued for other releases; for a control-room message the status ERCOT's page prints (active, cancelled), else issued | none | text | active, cancelled, ended, issued | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:news_releases, ercot:operations_messages | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/news/release/01052025-ercot-issues-weather, https://www.ercot.com/news/release/01172025-ercot-issues-weather, https://www.ercot.com/news/release/01212026-ercot-issues-weather; 105 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-19T21:02:01Z | 0 |
| `x_label` | The news release's title, or the control-room message's notice type as ERCOT's page gives it (Advisory, Watch, OCN and others) | none | text | for example Advisory, Cold weather, risk of rotating outages return to the Valley tonight, Conservation Alert extended through Tuesday morning; 83 distinct | 0 |
| `x_region` | The area the notice is for: ERCOT (system-wide) or Rio Grande Valley, read from the release's words | none | text | ERCOT, Rio Grande Valley | 0 |
| `x_issued_at` | When the notice was issued: the day of a news release (YYYY-MM-DD), the UTC time of a control-room message | none | text | for example 2011-02-02, 2011-02-03, 2011-02-08; 108 distinct | 0 |
| `x_counts` | yes when the notice is a system-wide call on supply or demand, the kinds grid_stress_days counts; no otherwise | none | text | no, yes | 0 |
| `x_text` | The notice's own words: the release's title and first two paragraphs, or the message, as ERCOT wrote them | none | text | for example Advisory issued for a geomagnetic disturbance of K-7 until October 10, 2026 1900., Advisory issued for a geomagnetic disturbance of K7 until 0100 on 07/05/26., At 10:22 ERCOT has issued an Advisory due to TSAT not solving in the last 30 minutes.; 125 distinct | 0 |

### `ercot_hub_prices_daily`

One daily statistic of ERCOT's day-ahead or real-time price at one of its six trading hubs, for one complete local operating day from 2015.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 348420.

- **Time:** ts_utc is the local (America/Chicago) operating day at 00:00:00Z.
- **Revisions:** Rebuilt whole by each run from the hub price tables; days the inputs on the machine hold no interval of are carried from the last run's table. vintage is not filled.
- **Source:** erw:ercot_hub_prices_daily ERW derived daily summary of ERCOT hub prices (docs/methods/ercot_hub_prices_daily.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_hub_prices_daily.md)
- **Method note:** [`docs/methods/ercot_hub_prices_daily.md`](../methods/ercot_hub_prices_daily.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT hub prices by day (docs/methods/ercot_hub_prices_daily.md). Via the Energy Research Warehouse (ERW), table `ercot_hub_prices_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:<hub> | none | text | ercot:HB_BUSAVG, ercot:HB_HOUSTON, ercot:HB_HUBAVG, ercot:HB_NORTH, ercot:HB_SOUTH, ercot:HB_WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-11-16T00:00:00Z; 4336 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -251.0 to 9315.45; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_dam for the da_ statistics, ercot_rtm for the rt_ statistics | none | text | ercot_dam, ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: ERCOT's trading hub: HB_HOUSTON, HB_NORTH, HB_SOUTH, HB_WEST, HB_HUBAVG (average of the four) and HB_BUSAVG (average over the hubs' buses) | none | text | HB_BUSAVG, HB_HOUSTON, HB_HUBAVG, HB_NORTH, HB_SOUTH, HB_WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_hub_prices_daily | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_hub_prices_daily.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-05T02:03:57Z to 2026-11-16T14:59:45Z; 30 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 348420 |

Variables (14):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `da_hours_above_200` | Hours of the day whose day-ahead price was above 200 USD/MWh | count | 26016 | 2015-01-01T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_hours_below_zero` | Hours of the day whose day-ahead price was below 0 | count | 26016 | 2015-01-01T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_max` | Highest day-ahead hourly price of the day, USD/MWh | USD/MWh | 26016 | 2015-01-01T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_mean` | Mean of the day's hourly day-ahead prices, USD/MWh | USD/MWh | 26016 | 2015-01-01T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_min` | Lowest day-ahead hourly price of the day, USD/MWh | USD/MWh | 26016 | 2015-01-01T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_offpeak_mean` | Mean day-ahead price over the off-peak hours, USD/MWh | USD/MWh | 26016 | 2015-01-01T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_peak_mean` | Mean day-ahead price over peak hours (hours ending 7 to 22 local, Monday to Friday, NERC holidays off-peak), USD/MWh; no row for a day with no peak hour | USD/MWh | 18198 | 2015-01-02T00:00:00Z | 2026-11-16T00:00:00Z |
| `rt_hours_above_200` | Hours of the day priced above 200 USD/MWh in real time, a 15-minute interval counting 0.25 | count | 25992 | 2015-01-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `rt_hours_below_zero` | Hours of the day priced below 0 in real time, a 15-minute interval counting 0.25 | count | 25992 | 2015-01-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `rt_max` | Highest 15-minute real-time price of the day, USD/MWh | USD/MWh | 25992 | 2015-01-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `rt_mean` | Mean of the day's 15-minute real-time prices, USD/MWh | USD/MWh | 25992 | 2015-01-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `rt_min` | Lowest 15-minute real-time price of the day, USD/MWh | USD/MWh | 25992 | 2015-01-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `rt_offpeak_mean` | Mean real-time price over the off-peak hours, USD/MWh | USD/MWh | 25992 | 2015-01-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `rt_peak_mean` | Mean real-time price over peak hours (hours ending 7 to 22 local, Monday to Friday, NERC holidays off-peak), USD/MWh; no row for a day with no peak hour | USD/MWh | 18174 | 2015-01-02T00:00:00Z | 2026-11-13T00:00:00Z |

### `ercot_interconnection_queue`

One position in ERCOT's Generation Interconnection Status (GIS) report, a project asking to connect generation or storage to ERCOT's grid.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 1736.

- **Time:** No time column. Dates are ERCOT's, YYYY-MM-DD; vintage is the retrieval date. The table is a snapshot of the report as read on its retrieved_at.
- **Revisions:** A snapshot rewritten whole by each run (Mondays); earlier queues stay in the archive and the raw files.
- **Source:** ercot:interconnection_queue ERCOT Generation Interconnection Status (GIS) report (https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1293955078)
- **Method note:** [`docs/methods/ercot_interconnection_queue.md`](../methods/ercot_interconnection_queue.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Generation Interconnection Status (GIS) report. Via the Energy Research Warehouse (ERW), table `ercot_interconnection_queue`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: ercot_queue:<queue id> | none | text | for example ercot_queue:15INR0064b, ercot_queue:16INR0049, ercot_queue:16INR0081; 1736 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 18-ALPHA BESS, 18-BRAVO BESS, 2 Cedar Wind; 1736 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-TX in every row | none | text | US-TX | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 1736 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 1736 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: ERCOT's requested capacity as gridstatus reads it (Capacity (MW)) | MW | number | -53.3 to 2992.0; 1206 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: active or completed; ERCOT's report lists no withdrawn positions | none | text | active, completed | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The in-service date of a completed row where one is given | none | date | 2017-12-20 to 2026-10-23; 96 distinct | 1633 |
| `operator` | The operator or owner, as the publisher writes it. Here: The interconnecting entity, filled on every row | none | text | for example 174 Power Global Properties, 174 Power Global Properties, LLC, 180 Wind LLC; 1295 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:interconnection_queue | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1293955078 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-05T23:21:53Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The retrieval date (YYYY-MM-DD), not a publication date | none | date | 2026-11-05 | 0 |
| `queue_id` | ERCOT's identifier of the interconnection request (INR number) (the source's name: Queue ID) | none | text | for example 15INR0064b, 16INR0049, 16INR0081; 1736 distinct | 0 |
| `county` | The county of the project (the source's name: County) | none | text | for example Anderson, Andrews, Angelina; 193 distinct | 0 |
| `state` | The state of the project (TX) (the source's name: State) | none | text | TX | 0 |
| `poi` | The point of interconnection: the substation or line where the project would connect (the source's name: Interconnection Location) | none | text | for example # 38900 Hidden Lakes - # 42015 PHR 138 KV, # 7044 Marion 345kV, # 79601 Stillman Substation 138 kV; 1386 distinct | 0 |
| `zone` | The zone of the project (the source's name: Zone) | none | empty | no cell holds a value | 1736: Empty in every row: ERCOT's report does not give it |
| `transmission_owner` | The transmission owner the project connects to (the source's name: Transmission Owner) | none | empty | no cell holds a value | 1736: Empty in every row: ERCOT's report does not give it |
| `fuel_technology` | The fuel and technology in ERCOT's words (Other - Battery Energy Storage, Solar - Photovoltaic Solar, Wind - Wind Turbine, Gas - Combined-Cycle and others) (the source's name: Generation Type) | none | text | Fuel Oil - Other, Gas - Combined-Cycle, Gas - Combustion (gas) Turbine, but not part of a Combined-Cycle, Gas - Internal Combustion Engine, eg. Reciprocating, Gas - Steam Turbine other than Combined-Cycle, Hydrogen - Other, Nuclear - Steam Turbine other than Combined-Cycle, Other - Battery Energy Storage, Other - Other, Solar - Photovoltaic Solar, Water - Other, Wind - Wind Turbine | 1: ERCOT gives no generation type (one row) |
| `iso_status` | The status as gridstatus reads ERCOT's report: Completed where the IA Signed day is filled (a signed interconnection agreement, not a plant in operation), else Active (the source's name: Status (gridstatus)) | none | text | Active, Completed | 0 |
| `queue_date` | The date the request entered the queue (the source's name: Queue Date) | none | date | 2013-11-27 to 2026-10-22; 411 distinct | 12: ERCOT gives no queue date |
| `proposed_in_service_date` | The date the project proposes to begin operating (the source's name: Proposed Completion Date) | none | date | 2025-03-27 to 2033-06-15; 526 distinct | 0 |
| `actual_in_service_date` | The date the project began operating (ERCOT's Approved for Synchronization date, as gridstatus copies it) (the source's name: Actual Completion Date (gridstatus)) | none | date | 2017-12-20 to 2026-10-23; 100 distinct | 1627: No date given |
| `withdrawn_date` | The date the request was withdrawn (the source's name: Withdrawn Date) | none | empty | no cell holds a value | 1736: Empty in every row: ERCOT's report lists no withdrawn positions |

### `ercot_large_load_status`

One figure stated in words in one of ERCOT's monthly Large Load Interconnection Status Update reports.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 38.

- **Time:** ts_utc is the day on the report's first page at 00:00:00Z; the month the sentence names is in x_month_as_written.
- **Revisions:** Merged by (entity, variable, ts_utc); vintage is the report's date at 00:00:00Z.
- **Source:** ercot:large_load_status_update ERCOT, Large Load Interconnection Status Update (the Large Load Integration team's monthly report to TAC and the LLWG); found on the meeting pages of  and (https://www.ercot.com/committees/tac)
- **Method note:** [`docs/methods/ercot_large_load_status.md`](../methods/ercot_large_load_status.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Large Load Interconnection Status Update (the Large Load Integration team's monthly report to TAC and the LLWG). Via the Energy Research Warehouse (ERW), table `ercot_large_load_status`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:large_load in every row: ERCOT's large loads together | none | text | ercot:large_load | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-05-28T00:00:00Z, 2025-07-30T00:00:00Z, 2025-08-27T00:00:00Z, 2025-10-17T00:00:00Z, 2025-11-19T00:00:00Z, 2026-01-21T00:00:00Z, 2026-02-25T00:00:00Z, 2026-03-13T00:00:00Z, 2026-03-26T00:00:00Z, 2026-04-24T00:00:00Z, 2026-05-21T00:00:00Z, 2026-06-19T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 137.0 to 140000.0; 32 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 38 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 38 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:large_load_status_update | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/files/docs/2025/05/27/11.-LLWG-Report.zip#LLI Queue Status Update - 2025-5.pdf, https://www.ercot.com/files/docs/2025/07/29/12.-LLWG-Report.zip#LLI Queue Status Update - 2025-07-21.pdf, https://www.ercot.com/files/docs/2025/08/26/13.-LLWG-Report.zip#LLI Queue Status Update - 2025-08-27.pdf, https://www.ercot.com/files/docs/2025/10/21/11.-LLWG-Report.zip#October TAC Report.pptx, https://www.ercot.com/files/docs/2025/11/18/11-LLWG-Report.zip#November TAC Report.pdf, https://www.ercot.com/files/docs/2026/01/20/16.-Large-Load-Issues.zip#January TAC Report.pdf, https://www.ercot.com/files/docs/2026/03/05/February-TAC-Report.pdf, https://www.ercot.com/files/docs/2026/03/12/March-TAC-Report.pdf, https://www.ercot.com/files/docs/2026/03/27/March-TAC-Report-Updated_03262026.pptx, https://www.ercot.com/files/docs/2026/04/24/April-24-LLWG-Report_042426.pptx, https://www.ercot.com/files/docs/2026/05/21/May-21-LLWG-Report.pptx, https://www.ercot.com/files/docs/2026/06/18/June-19-LLWG-Report.pptx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T17:45:38Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The day on the report's first page at 00:00:00Z | none | utc time | 2025-05-28T00:00:00Z, 2025-07-30T00:00:00Z, 2025-08-27T00:00:00Z, 2025-10-17T00:00:00Z, 2025-11-19T00:00:00Z, 2026-01-21T00:00:00Z, 2026-02-25T00:00:00Z, 2026-03-13T00:00:00Z, 2026-03-26T00:00:00Z, 2026-04-24T00:00:00Z, 2026-05-21T00:00:00Z, 2026-06-19T00:00:00Z | 0 |
| `x_month_as_written` | The month the report's sentence names, as ERCOT wrote it | none | text | August 2025, February 2025, January 2025, July 2025, June 2026, March 2025, March 2026, May 2025, May 2026, November 2025, October 2025 | 14: The sentence names no month (the approved-to-energize and new-submission figures) |
| `x_document` | The file name of the report | none | text | April-24-LLWG-Report_042426.pptx, February-TAC-Report.pdf, January TAC Report.pdf, June-19-LLWG-Report.pptx, LLI Queue Status Update - 2025-07-21.pdf, LLI Queue Status Update - 2025-08-27.pdf, LLI Queue Status Update - 2025-5.pdf, March-TAC-Report-Updated_03262026.pptx, March-TAC-Report.pdf, May-21-LLWG-Report.pptx, November TAC Report.pdf, October TAC Report.pptx | 0 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `approved_to_energize_mw` | MW of large load that has received ERCOT's Approval to Energize | MW | 12 | 2025-05-28T00:00:00Z | 2026-06-19T00:00:00Z |
| `new_submissions_count` | New large load interconnection submissions ERCOT had recently received | count | 1 | 2026-03-13T00:00:00Z | 2026-03-13T00:00:00Z |
| `new_submissions_mw` | The approximate MW of those new submissions, by ERCOT's preliminary review | MW | 1 | 2026-03-13T00:00:00Z | 2026-03-13T00:00:00Z |
| `observed_nonsimultaneous_peak_mw` | The sum of each approved load's own highest consumption in the month: how much approved load ERCOT believes is operational, MW | MW | 12 | 2025-05-28T00:00:00Z | 2026-06-19T00:00:00Z |
| `observed_simultaneous_peak_mw` | The highest consumption of all the large loads together at one point in the month, MW | MW | 12 | 2025-05-28T00:00:00Z | 2026-06-19T00:00:00Z |

### `ercot_node_places`

One ERCOT resource node (a settlement point where a generating or storage resource is settled) placed in a county and load zone by the CDR units at its station.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 569.

- **Time:** No time column; a snapshot computed from the tables held when the builder ran.
- **Revisions:** Rebuilt whole from node_basis_daily and ercot_cdr_units by each run of the builder; no request is made.
- **Source:** ercot:cdr Electric Reliability Council of Texas (ERCOT), Capacity, Demand and Reserves Report (the units' county and zone), and ERCOT's settlement points as node_basis_daily holds them
- **Method note:** [`docs/methods/ercot_node_places.md`](../methods/ercot_node_places.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT's resource nodes with the county and zone of their CDR units (docs/methods/ercot_node_places.md). Via the Energy Research Warehouse (ERW), table `ercot_node_places`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: ercot_node:<settlement point> | none | text | for example ercot_node:7RNCHSLR_ALL, ercot_node:A4_DGR1_RN, ercot_node:A4_DGR2_RN; 569 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: generator: the resource ERCOT settles at the node | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The settlement point's name | none | text | for example 7RNCHSLR_ALL, A4_DGR1_RN, A4_DGR2_RN; 569 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-TX in every row | none | text | US-TX | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 569 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 569 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 569 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 569 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 569 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 569 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_node_places | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_node_places.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T06:46:36Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 569 |
| `x_station` | The settlement point's name up to the first underscore, the station code (7RNCHSLR_ALL gives 7RNCHSLR) | none | text | for example 7RNCHSLR, A4, ADL; 496 distinct | 0 |
| `x_county` | The county ERCOT's CDR gives every unit at that station | none | text | for example ANDREWS, ANGELINA, ARCHER; 148 distinct | 0 |
| `x_zone` | The load zone ERCOT's CDR gives every unit at that station (COASTAL, HOUSTON, NORTH, PANHANDLE, SOUTH, WEST) | none | text | COASTAL, HOUSTON, NORTH, PANHANDLE, SOUTH, WEST | 0 |
| `x_class` | The node's class in node_basis_daily (gas, wind, solar, storage, mixed, other) | none | text | gas, mixed, other, solar, storage, wind | 0 |
| `x_resource_type` | ERCOT's resource type of the node as node_basis_daily holds it (CCGT90, CLLIG, DSL and others) | none | text | for example CCGT90, CCLE90, CLLIG; 26 distinct | 0 |
| `x_cdr_units` | The CDR units matched to the station, joined with ; | none | text | for example 7RNCHSLR_UNIT1;7RNCHSLR_UNIT2;7RNCHSLR_UNIT3, A4_DGR1;A4_DGR2, ADL_SOLAR1; 496 distinct | 0 |
| `x_cdr_units_n` | The number of CDR units matched | count | integer | 1, 10, 12, 17, 2, 3, 4, 5, 6, 7, 8, 9 | 0 |

### `ercot_node_planned_generation`

One placed ERCOT resource node with the planned generation in its county, from ERCOT's active interconnection queue and EIA-860M's planned generators.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 569.

- **Time:** No time column; a snapshot computed from the tables held when the builder ran.
- **Revisions:** Rewritten whole by each run of the builder from ercot_node_places, ercot_interconnection_queue and eia860m_planned_generators; no request is made. vintage is not filled.
- **Source:** ercot:interconnection_queue Electric Reliability Council of Texas (ERCOT), GIS report; eia:eia860m U.S. Energy Information Administration, Form EIA-860M; ercot:cdr ERCOT, Capacity, Demand and Reserves Report (the nodes' counties, through ercot_node_places)
- **Method note:** [`docs/methods/ercot_node_planned_generation.md`](../methods/ercot_node_planned_generation.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The planned generation in a placed ERCOT node's county (docs/methods/ercot_node_planned_generation.md). Via the Energy Research Warehouse (ERW), table `ercot_node_planned_generation`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: ercot_node:<settlement point>, the same ids as ercot_node_places | none | text | for example ercot_node:7RNCHSLR_ALL, ercot_node:A4_DGR1_RN, ercot_node:A4_DGR2_RN; 569 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: generator in every row | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The settlement point | none | text | for example 7RNCHSLR_ALL, A4_DGR1_RN, A4_DGR2_RN; 569 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-TX in every row | none | text | US-TX | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 569 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 569 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 569 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 569 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 569 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 569 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_node_planned_generation | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_node_planned_generation.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T10:20:32Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 569 |
| `x_county` | The node's county, as ercot_node_places gives it | none | text | for example ANDREWS, ANGELINA, ARCHER; 148 distinct | 0 |
| `x_zone` | The node's load zone, as ercot_node_places gives it (COASTAL, HOUSTON, NORTH, PANHANDLE, SOUTH, WEST) | none | text | COASTAL, HOUSTON, NORTH, PANHANDLE, SOUTH, WEST | 0 |
| `x_queue_projects` | The number of ERCOT's active interconnection queue projects in the node's county (not at the node) | count | integer | 0, 1, 10, 11, 12, 13, 14, 15, 17, 19, 2, 20, 21, 22, 23, 25, 3, 36, 4, 5, 6, 7, 8, 9 | 0 |
| `x_queue_mw` | The capacity of those active queue projects, summed | MW | number | 0.0 to 16312.91; 139 distinct | 0 |
| `x_queue_solar_mw` | Of that capacity, the solar projects' (the queue's fuel and technology beginning Solar), as the queue gives it | MW | number | -53.3 to 6534.3; 103 distinct | 0 |
| `x_queue_wind_mw` | Of that capacity, the wind projects' (fuel and technology beginning Wind) | MW | number | 0.0 to 2287.88; 41 distinct | 0 |
| `x_queue_storage_mw` | Of that capacity, the storage projects' (Other - Battery Energy Storage) | MW | number | 0.0 to 5280.63; 126 distinct | 0 |
| `x_queue_gas_mw` | Of that capacity, the gas projects' (fuel and technology beginning Gas) | MW | number | 0.0 to 5886.29; 44 distinct | 0 |
| `x_queue_other_mw` | Of that capacity, every other kind's | MW | number | 0.0, 1232.0, 132.0, 1320.0, 1336.52, 50.0, 79.63 | 0 |
| `x_queue_next_in_service` | The earliest proposed in-service date among those projects (the developers' dates; some fall before the table's day) | none | date | 2025-08-26 to 2030-03-01; 100 distinct | 18: No active queue project in the county |
| `x_eia_planned_generators` | The number of EIA-860M's planned generators in the node's county (state TX) | count | integer | 0, 1, 10, 11, 12, 13, 161, 2, 3, 4, 5, 6, 7, 8, 9 | 0 |
| `x_eia_planned_mw` | The nameplate capacity of those planned generators, summed | MW | number | 0.0 to 16147.3; 95 distinct | 0 |
| `x_eia_solar_mw` | Of that capacity, EIA-860M's technology group solar | MW | number | 0.0 to 1609.6; 66 distinct | 0 |
| `x_eia_wind_mw` | Of that capacity, EIA-860M's technology group wind | MW | number | 0.0, 110.4, 162.1, 200.0, 225.6, 265.0, 265.5, 276.0, 316.2, 355.5, 440.0, 500.0, 670.5 | 0 |
| `x_eia_storage_mw` | Of that capacity, EIA-860M's technology group storage | MW | number | 0.0 to 1385.9; 55 distinct | 0 |
| `x_eia_natural_gas_mw` | Of that capacity, EIA-860M's technology group natural gas | MW | number | 0.0, 10.0, 11679.3, 121.8, 199.8, 2334.9, 43.4, 447.0, 5.0, 721.0 | 0 |
| `x_eia_nuclear_mw` | Of that capacity, EIA-860M's technology group nuclear | MW | number | 0.0, 4468.0 | 0 |
| `x_eia_petroleum_mw` | Of that capacity, EIA-860M's technology group petroleum | MW | number | 0.0, 9.9 | 0 |
| `x_eia_hydro_mw` | Of that capacity, EIA-860M's technology group hydro | MW | number | 0.0 | 0 |
| `x_eia_biomass_mw` | Of that capacity, EIA-860M's technology group biomass | MW | number | 0.0 | 0 |
| `x_eia_geothermal_mw` | Of that capacity, EIA-860M's technology group geothermal | MW | number | 0.0 | 0 |
| `x_eia_other_mw` | Of that capacity, EIA-860M's technology group other | MW | number | 0.0, 28.6, 9.9 | 0 |

### `ercot_node_transmission`

One placed ERCOT resource node with the transmission project phases of ERCOT's TPIT workbook (Transmission Project and Information Tracking) that start or end in its county.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 569.

- **Time:** No time column; a snapshot computed from the tables held when the builder ran. x_tpit_edition names the TPIT edition read.
- **Revisions:** Rewritten whole by each run of the builder from ercot_node_places and ercot_transmission_projects; no request is made. vintage is not filled.
- **Source:** ercot:tpit Electric Reliability Council of Texas (ERCOT), Transmission Project and Information Tracking; ercot:cdr ERCOT, Capacity, Demand and Reserves Report (the nodes' counties, through ercot_node_places)
- **Method note:** [`docs/methods/ercot_node_transmission.md`](../methods/ercot_node_transmission.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT's TPIT projects by a resource node's county (docs/methods/ercot_node_transmission.md). Via the Energy Research Warehouse (ERW), table `ercot_node_transmission`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: ercot_node:<settlement point>, the same ids as ercot_node_places | none | text | for example ercot_node:7RNCHSLR_ALL, ercot_node:A4_DGR1_RN, ercot_node:A4_DGR2_RN; 569 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: generator in every row | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The settlement point | none | text | for example 7RNCHSLR_ALL, A4_DGR1_RN, A4_DGR2_RN; 569 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-TX in every row | none | text | US-TX | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 569 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 569 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 569 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 569 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 569 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 569 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_node_transmission | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_node_transmission.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-06T05:23:43Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 569 |
| `x_county` | The node's county, as ercot_node_places gives it | none | text | for example ANDREWS, ANGELINA, ARCHER; 148 distinct | 0 |
| `x_zone` | The node's load zone, as ercot_node_places gives it (COASTAL, HOUSTON, NORTH, PANHANDLE, SOUTH, WEST) | none | text | COASTAL, HOUSTON, NORTH, PANHANDLE, SOUTH, WEST | 0 |
| `x_phases_future` | TPIT project phases on the Future sheet whose start or end county is the node's county | count | integer | 0 to 109; 33 distinct | 0 |
| `x_phases_planned` | TPIT project phases on the Planned sheet whose start or end county is the node's county | count | integer | 0, 1, 12, 2, 3, 4, 44, 5, 6, 7 | 0 |
| `x_phases_completed` | TPIT project phases on the Completed sheet whose start or end county is the node's county | count | integer | 0, 1, 12, 13, 2, 3, 39, 4, 5, 6, 7 | 0 |
| `x_phases_cancelled` | TPIT project phases on the Cancelled sheet whose start or end county is the node's county | count | integer | 0, 1, 2, 3, 4, 5, 6, 7, 8 | 0 |
| `x_open_projects` | Distinct TPIT project numbers among the future and planned phases touching the county | count | integer | 0 to 153; 38 distinct | 0 |
| `x_open_new_circuit_miles` | New circuit miles of those future and planned phases, summed | miles | number | 0.0 to 685.67; 82 distinct | 0 |
| `x_open_upgraded_circuit_miles` | Upgraded circuit miles of those future and planned phases, summed | miles | number | 0.0 to 424.18; 115 distinct | 0 |
| `x_open_max_kv` | The highest voltage among those future and planned phases | kV | integer | 138, 345, 69, 765 | 24: No future or planned phase touches the county |
| `x_open_next_in_service` | The earliest projected in-service date among those future and planned phases (the owners' dates; some fall before the table's day) | none | date | 2025-05-01 to 2031-06-01; 78 distinct | 24: No future or planned phase touches the county |
| `x_tpit_edition` | The TPIT workbook's title line, naming the edition read | none | text | OCTOBER BASE FOR TRANSMISSION OWNER SUBMISSION FILE - TRANSMISSION PROJECT INFORMATION TRACKING (TPIT) FUTURE PROJECTS AS OF 10/1/2026 | 0 |

### `ercot_node_wires_utilities`

One placed ERCOT resource node with the wires utilities EIA-861 lists as serving its county, Texas's delivery-only companies named apart.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 569.

- **Time:** No time column; a snapshot computed from the tables held when the builder ran. vintage names the EIA-861 year.
- **Revisions:** Rewritten whole by each run of the builder from ercot_node_places, utility_service_territories, eia861_delivery_only and eia861_utility_data; no request is made.
- **Source:** eia:eia861_territory and eia:eia861 U.S. Energy Information Administration, Form EIA-861 (service territories, delivery companies, utility data); ercot:cdr ERCOT, Capacity, Demand and Reserves Report (the nodes' counties, through ercot_node_places)
- **Method note:** [`docs/methods/ercot_node_wires_utilities.md`](../methods/ercot_node_wires_utilities.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The wires utilities in a placed ERCOT node's county (docs/methods/ercot_node_wires_utilities.md). Via the Energy Research Warehouse (ERW), table `ercot_node_wires_utilities`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: ercot_node:<settlement point>, the same ids as ercot_node_places | none | text | for example ercot_node:7RNCHSLR_ALL, ercot_node:A4_DGR1_RN, ercot_node:A4_DGR2_RN; 569 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: generator in every row | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The settlement point | none | text | for example 7RNCHSLR_ALL, A4_DGR1_RN, A4_DGR2_RN; 569 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-TX in every row | none | text | US-TX | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 569 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 569 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 569 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 569 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 569 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 569 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_node_wires_utilities | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_node_wires_utilities.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T11:28:45Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The text 'EIA-861 <year>' (EIA-861 2025 in every row), the data year read, not a publication time | none | text | EIA-861 2025 | 0 |
| `x_county` | The node's county, as ercot_node_places gives it | none | text | for example ANDREWS, ANGELINA, ARCHER; 148 distinct | 0 |
| `x_zone` | The node's load zone, as ercot_node_places gives it (COASTAL, HOUSTON, NORTH, PANHANDLE, SOUTH, WEST) | none | text | COASTAL, HOUSTON, NORTH, PANHANDLE, SOUTH, WEST | 0 |
| `x_utilities_n` | The number of utilities EIA-861 lists as serving the node's county (state TX) | count | integer | 1, 2, 3, 4, 5, 6, 7, 8 | 0 |
| `x_utilities` | Those utilities, each '<name> (<EIA utility number>)', sorted, joined by '; ' | none | text | for example AEP Texas Central Company (3278); Bandera Electric Coop, Inc (1175); Medina Electric Coop, Inc (12268); Rio Grande Electric Coop, Inc (16057), AEP Texas Central Company (3278); Bluebonnet Electric Coop, Inc (1892); CenterPoint Energy (8901); City of Weimar - (TX) (20331); Fayette Electric Coop, Inc (6183); San Bernard Electric Coop, Inc (16638); Wharton County Elec Coop, Inc (20472), AEP Texas Central Company (3278); Bluebonnet Electric Coop, Inc (1892); City of Lockhart - (TX) (11119); City of Luling - (TX) (11316); Guadalupe Valley Elec Coop Inc (7752); Pedernales Electric Coop, Inc (14626); 139 distinct | 0 |
| `x_delivery_only_n` | The number of delivery-only companies (wires companies that sell no power, as eia861_delivery_only holds them for Texas) among those utilities | count | integer | 0, 1, 2, 3 | 0 |
| `x_delivery_only` | Those delivery-only companies, each '<name> (<EIA utility number>)', joined by '; ' | none | text | AEP Texas Central Company (3278), AEP Texas Central Company (3278); CenterPoint Energy (8901), AEP Texas Central Company (3278); CenterPoint Energy (8901); Texas-New Mexico Power Co (40051), AEP Texas Central Company (3278); Nueces Electric Cooperative (13830), AEP Texas Central Company (3278); Oncor Electric Delivery Company LLC (44372), AEP Texas North Company (20404), AEP Texas North Company (20404); Oncor Electric Delivery Company LLC (44372), AEP Texas North Company (20404); Oncor Electric Delivery Company LLC (44372); Texas-New Mexico Power Co (40051), AEP Texas North Company (20404); Texas-New Mexico Power Co (40051), CenterPoint Energy (8901), CenterPoint Energy (8901); Texas-New Mexico Power Co (40051), Oncor Electric Delivery Company LLC (44372), Oncor Electric Delivery Company LLC (44372); Texas-New Mexico Power Co (40051), Texas-New Mexico Power Co (40051) | 52: No delivery-only company serves the county |
| `x_outside_tre_n` | The number of those utilities whose EIA-861 utility data names a NERC region but not Texas RE (so part of the county is outside ERCOT's reliability region) | count | integer | 0, 1, 2, 3, 4 | 0 |
| `x_outside_tre` | Those utilities outside Texas RE, each '<name> (<EIA utility number>)', joined by '; ' | none | text | Bailey County Elec Coop Assn (1169); Deaf Smith Electric Coop, Inc (4939); Lamb County Electric Coop, Inc (10625); Southwestern Public Service Co (17718), Bailey County Elec Coop Assn (1169); Deaf Smith Electric Coop, Inc (4939); Southwestern Public Service Co (17718), Deaf Smith Electric Coop, Inc (4939); Rita Blanca Electric Coop, Inc (16063); Southwestern Public Service Co (17718), Deaf Smith Electric Coop, Inc (4939); Southwestern Public Service Co (17718), El Paso Electric Co (5701), Entergy Texas Inc. (55937), Greenbelt Electric Coop, Inc (7561), Greenbelt Electric Coop, Inc (7561); North Plains Electric Coop Inc (13757); Southwestern Public Service Co (17718), Greenbelt Electric Coop, Inc (7561); Southwestern Public Service Co (17718), Jasper-Newton Elec Coop, Inc (9668); Sam Houston Electric Coop Inc (16613), Lamb County Electric Coop, Inc (10625); Southwestern Public Service Co (17718), Rusk County Electric Coop, Inc (16461), Rusk County Electric Coop, Inc (16461); Upshur Rural Elec Coop Corp (19579), Southwestern Public Service Co (17718), Wood County Electric Coop, Inc (20927) | 441: No utility of the county is outside Texas RE |
| `x_short_form_n` | The number of those utilities filing EIA's short form, whose utility data gives no region | count | integer | 0, 1, 2, 3 | 0 |

### `ercot_peak_premium_annual`

One price statistic of ERCOT's 15-minute real-time prices at one trading hub over one ERCOT operating year, for all intervals or one block of the day, or the same over the year to date.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 4032.

- **Time:** ts_utc is 1 January of the ERCOT operating year at 00:00:00Z; the period is local (America/Chicago) time. The current year is partial (n_intervals says how many intervals it holds).
- **Revisions:** Merged by (entity, variable, ts_utc) through the merge writer; each run recomputes the years from the hub price tables, and a past year is written only when complete. vintage is not filled.
- **Source:** erw:ercot_peak_premium ERW derived metrics, ERCOT peak premium method (docs/methods/ercot_peak_premium.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_peak_premium.md)
- **Method note:** [`docs/methods/ercot_peak_premium.md`](../methods/ercot_peak_premium.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT peak premium metrics (docs/methods/ercot_peak_premium.md). Via the Energy Research Warehouse (ERW), table `ercot_peak_premium_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:<hub> | none | text | ercot:HB_BUSAVG, ercot:HB_HOUSTON, ercot:HB_HUBAVG, ercot:HB_NORTH, ercot:HB_SOUTH, ercot:HB_WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z, 2026-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -251.0 to 35136.0; 2555 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_rtm in every row: ERCOT's real-time market | none | text | ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: ERCOT's trading hub: HB_HOUSTON, HB_NORTH, HB_SOUTH, HB_WEST, HB_HUBAVG (average of the four) and HB_BUSAVG (average over the hubs' buses) | none | text | HB_BUSAVG, HB_HOUSTON, HB_HUBAVG, HB_NORTH, HB_SOUTH, HB_WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_peak_premium | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_peak_premium.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T17:54:52Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 4032 |

Variables (56):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `all_iqr` | 75th less 25th percentile of all intervals' prices, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `all_max` | Highest price of all intervals, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `all_median` | Median of all intervals' prices, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `all_min` | Lowest price of all the year's intervals, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `all_p999` | 99.9th percentile of all intervals' prices, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `all_q1` | 25th percentile of all intervals' prices, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `all_q3` | 75th percentile of all intervals' prices, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `midday_max` | Highest price of the midday block, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `midday_median` | Median of the midday block, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `midday_min` | Lowest price of the midday block (intervals starting 12:00 to 16:00 local), USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `midday_q1` | 25th percentile of the midday block, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `midday_q3` | 75th percentile of the midday block, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `n_intervals` | The 15-minute intervals the period holds | count | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `n_negative` | Intervals priced at or below 0 USD/MWh | count | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `n_scarcity` | Intervals priced at or above 1,000 USD/MWh | count | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `overnight_max` | Highest price of the overnight block, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `overnight_median` | Median of the overnight block, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `overnight_min` | Lowest price of the overnight block (intervals starting 21:00 to 12:00 local), USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `overnight_q1` | 25th percentile of the overnight block, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `overnight_q3` | 75th percentile of the overnight block, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `peak_iqr` | 75th less 25th percentile of the peak block, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `peak_max` | Highest price of the peak block, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `peak_median` | Median of the peak block, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `peak_min` | Lowest price of the peak block (intervals starting 16:00 to 21:00 local), USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `peak_minus_midday_median` | Peak block median less midday block median, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `peak_q1` | 25th percentile of the peak block, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `peak_q3` | 75th percentile of the peak block, USD/MWh | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `worst_interval_multiple` | 99.9th percentile over median of all intervals (ratio) | ratio | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_all_iqr` | all_iqr over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_all_max` | all_max over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_all_median` | all_median over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_all_min` | all_min over the year to date (1 January to the month, day and time of the last input interval) | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_all_p999` | all_p999 over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_all_q1` | all_q1 over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_all_q3` | all_q3 over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_midday_max` | midday_max over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_midday_median` | midday_median over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_midday_min` | midday_min over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_midday_q1` | midday_q1 over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_midday_q3` | midday_q3 over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_n_intervals` | n_intervals over the year to date | count | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_n_negative` | n_negative over the year to date | count | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_n_scarcity` | n_scarcity over the year to date | count | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_overnight_max` | overnight_max over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_overnight_median` | overnight_median over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_overnight_min` | overnight_min over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_overnight_q1` | overnight_q1 over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_overnight_q3` | overnight_q3 over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_peak_iqr` | peak_iqr over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_peak_max` | peak_max over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_peak_median` | peak_median over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_peak_min` | peak_min over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_peak_minus_midday_median` | peak_minus_midday_median over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_peak_q1` | peak_q1 over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_peak_q3` | peak_q3 over the year to date | USD/MWh | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `ytd_worst_interval_multiple` | worst_interval_multiple over the year to date | ratio | 72 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

### `ercot_peak_premium_monthly`

One price statistic of ERCOT's 15-minute real-time prices at one trading hub over one local calendar month, for all intervals or one block of the day.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 24024.

- **Time:** ts_utc is the first day of the local (America/Chicago) month at 00:00:00Z. The current month is partial (n_intervals says how many intervals it holds).
- **Revisions:** Merged by (entity, variable, ts_utc) through the merge writer; a past month is written only when complete. vintage is not filled.
- **Source:** erw:ercot_peak_premium ERW derived metrics, ERCOT peak premium method (docs/methods/ercot_peak_premium.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_peak_premium.md)
- **Method note:** [`docs/methods/ercot_peak_premium.md`](../methods/ercot_peak_premium.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT peak premium metrics (docs/methods/ercot_peak_premium.md). Via the Energy Research Warehouse (ERW), table `ercot_peak_premium_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:<hub> | none | text | ercot:HB_BUSAVG, ercot:HB_HOUSTON, ercot:HB_HUBAVG, ercot:HB_NORTH, ercot:HB_SOUTH, ercot:HB_WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-11-01T00:00:00Z; 143 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -251.0 to 9315.45; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_rtm in every row: ERCOT's real-time market | none | text | ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: ERCOT's trading hub: HB_HOUSTON, HB_NORTH, HB_SOUTH, HB_WEST, HB_HUBAVG (average of the four) and HB_BUSAVG (average over the hubs' buses) | none | text | HB_BUSAVG, HB_HOUSTON, HB_HUBAVG, HB_NORTH, HB_SOUTH, HB_WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_peak_premium | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_peak_premium.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T17:54:52Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 24024 |

Variables (28):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `all_iqr` | 75th less 25th percentile of all intervals' prices, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_max` | Highest price of all intervals, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_median` | Median of all intervals' prices, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_min` | Lowest price of all the month's intervals, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_p999` | 99.9th percentile of all intervals' prices, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_q1` | 25th percentile of all intervals' prices, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_q3` | 75th percentile of all intervals' prices, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_max` | Highest price of the midday block, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_median` | Median of the midday block, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_min` | Lowest price of the midday block (intervals starting 12:00 to 16:00 local), USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_q1` | 25th percentile of the midday block, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_q3` | 75th percentile of the midday block, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `n_intervals` | The 15-minute intervals the period holds | count | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `n_negative` | Intervals priced at or below 0 USD/MWh | count | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `n_scarcity` | Intervals priced at or above 1,000 USD/MWh | count | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_max` | Highest price of the overnight block, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_median` | Median of the overnight block, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_min` | Lowest price of the overnight block (intervals starting 21:00 to 12:00 local), USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_q1` | 25th percentile of the overnight block, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_q3` | 75th percentile of the overnight block, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_iqr` | 75th less 25th percentile of the peak block, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_max` | Highest price of the peak block, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_median` | Median of the peak block, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_min` | Lowest price of the peak block (intervals starting 16:00 to 21:00 local), USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_minus_midday_median` | Peak block median less midday block median, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_q1` | 25th percentile of the peak block, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_q3` | 75th percentile of the peak block, USD/MWh | USD/MWh | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `worst_interval_multiple` | 99.9th percentile over median of all intervals (ratio) | ratio | 858 | 2015-01-01T00:00:00Z | 2026-11-01T00:00:00Z |

### `ercot_peak_premium_node_monthly`

One price statistic of ERCOT's 15-minute real-time prices at one settlement point over one local calendar month, for all intervals or one block of the day.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 17472.

- **Time:** ts_utc is the first day of the local (America/Chicago) month at 00:00:00Z. The month in progress is partial (n_intervals says how many intervals it holds).
- **Revisions:** Merged by (entity, variable, ts_utc) through the merge writer; an ended month is written for a point only with every interval of it, the month in progress as far as it is held. vintage is not filled.
- **Source:** erw:ercot_node_peak_premium ERW derived metrics, ERCOT peak premium method (docs/methods/ercot_peak_premium.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_peak_premium.md)
- **Method note:** [`docs/methods/ercot_peak_premium.md`](../methods/ercot_peak_premium.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT peak premium metrics per settlement point (docs/methods/ercot_peak_premium.md). Via the Energy Research Warehouse (ERW), table `ercot_peak_premium_node_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:<settlement point>, every point of ercot_rtm_node_prices (resource nodes, hubs and load zones) | none | text | for example ercot:ABINDUST_RN, ercot:ADL_RN, ercot:AE_RN; 312 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-10-01T00:00:00Z, 2026-11-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -251.0 to 3522.5; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_rtm in every row: ERCOT's real-time market | none | text | ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The settlement point's name | none | text | for example ABINDUST_RN, ADL_RN, AE_RN; 312 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_node_peak_premium | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_peak_premium.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T19:57:05Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 17472 |

Variables (28):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `all_iqr` | 75th less 25th percentile of all intervals' prices, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_max` | Highest price of all intervals, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_median` | Median of all intervals' prices, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_min` | Lowest price of all the month's intervals, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_p999` | 99.9th percentile of all intervals' prices, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_q1` | 25th percentile of all intervals' prices, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `all_q3` | 75th percentile of all intervals' prices, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_max` | Highest price of the midday block, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_median` | Median of the midday block, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_min` | Lowest price of the midday block (intervals starting 12:00 to 16:00 local), USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_q1` | 25th percentile of the midday block, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `midday_q3` | 75th percentile of the midday block, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `n_intervals` | The 15-minute intervals the month holds | count | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `n_negative` | Intervals priced at or below 0 USD/MWh | count | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `n_scarcity` | Intervals priced at or above 1,000 USD/MWh | count | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_max` | Highest price of the overnight block, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_median` | Median of the overnight block, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_min` | Lowest price of the overnight block (intervals starting 21:00 to 12:00 local), USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_q1` | 25th percentile of the overnight block, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `overnight_q3` | 75th percentile of the overnight block, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_iqr` | 75th less 25th percentile of the peak block, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_max` | Highest price of the peak block, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_median` | Median of the peak block, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_min` | Lowest price of the peak block (intervals starting 16:00 to 21:00 local), USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_minus_midday_median` | Peak block median less midday block median, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_q1` | 25th percentile of the peak block, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `peak_q3` | 75th percentile of the peak block, USD/MWh | USD/MWh | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `worst_interval_multiple` | 99.9th percentile over median of all intervals (ratio) | ratio | 624 | 2026-10-01T00:00:00Z | 2026-11-01T00:00:00Z |

### `ercot_rtm_node_prices`

ERCOT's real-time settlement point price at one settlement point (a storage resource's node, a hub, a load zone or a DC tie) for one 15-minute interval.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1570608.

- **Time:** ts_utc is the interval's start in UTC, read from the file's DeliveryDate, DeliveryHour and DeliveryInterval in Central time.
- **Revisions:** Merged by (entity, variable, ts_utc); each run with a new file reads every saved zip again, and the table keeps intervals ERCOT's seven-day list has dropped. An interval posted twice with different prices is left out. vintage is not filled.
- **Source:** ercot:NP6-905-CD ERCOT, Settlement Point Prices at Resource Nodes, Hubs and Load Zones (report type 12301) (https://www.ercot.com/mp/data-products/data-product-details?id=NP6-905-CD)
- **Method note:** [`docs/methods/ercot_rtm_node_prices.md`](../methods/ercot_rtm_node_prices.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Settlement Point Prices at Resource Nodes, Hubs and Load Zones. Via the Energy Research Warehouse (ERW), table `ercot_rtm_node_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:<settlement point> | none | text | for example ercot:ABINDUST_RN, ercot:ADL_RN, ercot:AE_RN; 312 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-28T04:45:00Z to 2026-11-19T17:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -251.0 to 3522.5; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT15M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_rtm in every row: ERCOT's real-time market | none | text | ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The settlement point's name | none | text | for example ABINDUST_RN, ADL_RN, AE_RN; 312 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP6-905-CD | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1279835460, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1279839306, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1279843107; more than 5000 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-05T09:23:38Z to 2026-11-19T17:28:49Z; more than 5000 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1570608 |
| `x_point_type` | ERCOT's type of the settlement point: RN resource node, LZ load zone, HU hub, LZ_DC DC tie, SH HB_BUSAVG, AH HB_HUBAVG (the source's name: SettlementPointType) | none | text | AH, HU, LZ, LZ_DC, RN, SH | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `spp_rtm` | ERCOT's real-time settlement point price at the point, 15-minute, as ERCOT prints it (spp here is ERCOT's 'settlement point price', not the grid SPP) | USD/MWh | 1570608 | 2026-09-28T04:45:00Z | 2026-11-19T17:00:00Z |

### `ercot_rtm_price_adders`

One of ERCOT's real-time reserve price adders (added to the real-time energy price) over one hour, its time-weighted mean or its highest interval value.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 603156.

- **Time:** ts_utc is the start of the hour in UTC (ERCOT publishes a row per SCED interval, stamped in Central time); an hour is written only when all of its seconds are covered.
- **Revisions:** Merged by (entity, variable, ts_utc); ERCOT republishes the current year's workbook weekly, and a run that finds it rereads it and replaces that year's rows. vintage is the document's publish time.
- **Source:** ercot:NP6-792-ER ERCOT, Historical Real-Time ORDC and Reliability Deployment Price Adders and Reserves (https://www.ercot.com/mp/data-products/data-product-details?id=NP6-792-ER)
- **Method note:** [`docs/methods/ercot_rtm_price_adders.md`](../methods/ercot_rtm_price_adders.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Historical Real-Time ORDC and Reliability Deployment Price Adders and Reserves. Via the Energy Research Warehouse (ERW), table `ercot_rtm_price_adders`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:system in every row: ERCOT's whole system | none | text | ercot:system | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2014-06-01T06:00:00Z to 2026-11-15T04:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 8993.6045; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_rtm in every row: ERCOT's real-time market | none | text | ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The adder as ERCOT names it (RTORPA, RTOFFPA, RTORDPA, RTRDPA), not a place | none | text | RTOFFPA, RTORDPA, RTORPA, RTRDPA | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP6-792-ER | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1065495488, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1169113636, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1180319793, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1298996044, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=468554538, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=505964801, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=643552126, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=644817014, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=644817015, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=694452063, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=751366904, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=814938847, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=899479048, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=969827183 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-13T06:34:15Z, 2026-10-13T06:34:23Z, 2026-10-13T06:34:28Z, 2026-10-13T06:34:32Z, 2026-10-13T06:34:36Z, 2026-10-13T06:34:41Z, 2026-10-13T06:34:45Z, 2026-10-13T06:34:49Z, 2026-10-13T06:34:54Z, 2026-10-13T06:34:57Z, 2026-10-13T06:35:03Z, 2026-10-13T06:35:07Z, 2026-10-13T06:35:10Z, 2026-11-15T17:50:32Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The publish time of ERCOT's yearly workbook the row came from | none | utc time | 2015-01-02T16:00:28Z, 2016-01-07T21:44:38Z, 2019-01-08T15:53:35Z, 2019-01-17T20:19:27Z, 2020-01-02T18:30:02Z, 2021-01-01T15:26:33Z, 2022-01-01T15:26:31Z, 2023-03-02T20:04:14Z, 2024-01-01T15:09:09Z, 2025-01-01T15:09:34Z, 2025-12-08T17:21:55Z, 2026-01-08T23:58:14Z, 2026-11-15T16:12:49Z | 0 |

Variables (8):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `rtoffpa_max` | Off-line reserve price adder (RTOFFPA), the largest value an interval of the hour carried, USD/MWh | USD/MWh | 100878 | 2014-06-01T06:00:00Z | 2025-12-05T05:00:00Z |
| `rtoffpa_mean` | Off-line reserve price adder (RTOFFPA), the hour's time-weighted mean, USD/MWh (1 June 2014 to 4 December 2025) | USD/MWh | 100878 | 2014-06-01T06:00:00Z | 2025-12-05T05:00:00Z |
| `rtordpa_max` | On-line reliability deployment price adder (RTORDPA), the largest value an interval of the hour carried, USD/MWh | USD/MWh | 91547 | 2015-06-25T06:00:00Z | 2025-12-05T05:00:00Z |
| `rtordpa_mean` | On-line reliability deployment price adder (RTORDPA), the hour's time-weighted mean, USD/MWh (June 2015 to 4 December 2025) | USD/MWh | 91547 | 2015-06-25T06:00:00Z | 2025-12-05T05:00:00Z |
| `rtorpa_max` | On-line reserve price adder (RTORPA), the largest value an interval of the hour carried, USD/MWh | USD/MWh | 100878 | 2014-06-01T06:00:00Z | 2025-12-05T05:00:00Z |
| `rtorpa_mean` | On-line reserve price adder (RTORPA), the hour's time-weighted mean over the SCED intervals, USD/MWh (1 June 2014 to 4 December 2025) | USD/MWh | 100878 | 2014-06-01T06:00:00Z | 2025-12-05T05:00:00Z |
| `rtrdpa_max` | Reliability deployment price adder for energy (RTRDPA), the largest value an interval of the hour carried, USD/MWh | USD/MWh | 8275 | 2025-12-05T07:00:00Z | 2026-11-15T04:00:00Z |
| `rtrdpa_mean` | Reliability deployment price adder for energy (RTRDPA), the hour's time-weighted mean, USD/MWh (from 5 December 2025) | USD/MWh | 8275 | 2025-12-05T07:00:00Z | 2026-11-15T04:00:00Z |

### `ercot_sced_esr_hourly`

One ERCOT Energy Storage Resource (a battery) in one hour of real-time dispatch (SCED), its telemetered net output and limits, state of charge and real-time ancillary service awards, from ERCOT's 60-day SCED disclosure.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1637727.

- **Time:** ts_utc is the start of the hour in UTC; operating days are Central (America/Chicago) days.
- **Revisions:** Each operating day is reduced to resource-hours once and added; a day already reduced is not read again unless asked. vintage is the operating day plus 60 days at 00:00:00Z.
- **Source:** ercot:NP3-965-ER ERCOT, 60-Day SCED Disclosure Reports (report type 13052),  document list (https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13052)
- **Method note:** [`docs/methods/ercot_sced_esr_hourly.md`](../methods/ercot_sced_esr_hourly.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). 60-Day SCED Disclosure Reports (the file 60d_ESR_Data_in_SCED: Energy Storage Resources in real time). Via the Energy Research Warehouse (ERW), table `ercot_sced_esr_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:<Resource Name>, the storage resource | none | text | for example ercot:ABINDUST_ESR1, ercot:ADL_ESR1, ercot:AE_ESR1; 342 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-02-01T06:00:00Z to 2026-08-28T04:00:00Z; 4991 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -240.00002 to 240.00002; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_rtm in every row: ERCOT's real-time market | none | text | ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The resource's settlement point as ercot_dam_esr_awards names it; empty for the three resources that file never names | none | text | for example ABINDUST_RN, ADL_RN, AE_RN; 293 distinct | 6935 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP3-965-ER | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1210699966, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1211087392, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1211618930; 208 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-05T09:15:29Z to 2026-10-26T17:49:02Z; 208 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The operating day plus 60 days at 00:00:00Z (when ERCOT publishes the disclosure) | none | utc time | 2026-04-02T00:00:00Z to 2026-10-26T00:00:00Z; 208 distinct | 0 |
| `x_qse` | The scheduling entity (QSE) of the resource, ERCOT's code (the source's name: QSE) | none | text | for example QAETE1, QAETEL, QAMA1; 120 distinct | 0 |
| `x_sced_runs` | The SCED dispatch runs in the hour that hold the resource | count | integer | 11, 12, 13, 14, 15, 16, 17, 18, 19, 7 | 0 |
| `x_net_q1_mwh` | Telemetered net output integrated over the hour's first 15-minute settlement interval (positive is discharge) | MWh | number | -60.000005 to 60.000005; more than 5000 distinct | 0 |
| `x_net_q2_mwh` | Telemetered net output integrated over the hour's second 15-minute settlement interval (positive is discharge) | MWh | number | -60.000005 to 60.000005; more than 5000 distinct | 0 |
| `x_net_q3_mwh` | Telemetered net output integrated over the hour's third 15-minute settlement interval (positive is discharge) | MWh | number | -60.000005 to 60.000005; more than 5000 distinct | 0 |
| `x_net_q4_mwh` | Telemetered net output integrated over the hour's fourth 15-minute settlement interval (positive is discharge); the four add up to the value | MWh | number | -60.000005 to 60.000005; more than 5000 distinct | 0 |
| `x_discharge_mwh` | The positive part of the integrated net output: energy discharged in the hour | MWh | number | 0.0 to 240.00002; more than 5000 distinct | 0 |
| `x_charge_mwh` | The negative part of the integrated net output, as a positive number: energy charged in the hour | MWh | number | 0.0 to 240.00002; more than 5000 distinct | 0 |
| `x_base_point_mwh` | The Base Point (what SCED instructed) integrated over the hour the same way (the source's name: Base Point) | MWh | number | -240.000015 to 240.000015; more than 5000 distinct | 0 |
| `x_hsl_mw` | The hour's highest High Sustained Limit (the source's name: HSL) | MW | number | -8.8 to 240.0; 2335 distinct | 0 |
| `x_lsl_mw` | The hour's lowest Low Sustained Limit (negative: charging) (the source's name: LSL) | MW | number | -240.0 to 195.0; 2248 distinct | 0 |
| `x_soc_start_mwh` | The State of Charge (energy stored) at the hour's first SCED run (the source's name: State of Charge) | MWh | number | -703.6 to 974.9; more than 5000 distinct | 0 |
| `x_soc_min_mwh` | The lowest State of Charge in the hour (the source's name: State of Charge) | MWh | number | -703.6 to 974.9; more than 5000 distinct | 0 |
| `x_soc_max_mwh` | The highest State of Charge in the hour (the source's name: State of Charge) | MWh | number | -0.3718 to 974.9; more than 5000 distinct | 0 |
| `x_as_regup_mwh` | The real-time award of Regulation Up integrated over the hour (a MW for an hour) (the source's name: AS Awards REGUP) | MWh | number | 0.0 to 269.745653; more than 5000 distinct | 0 |
| `x_as_regdn_mwh` | The real-time award of Regulation Down integrated over the hour (a MW for an hour) (the source's name: AS Awards REGDN) | MWh | number | 0.0 to 200.0; more than 5000 distinct | 0 |
| `x_as_rrspfr_mwh` | The real-time award of Responsive Reserve, PFR kind, integrated over the hour (a MW for an hour) (the source's name: AS Awards RRSPFR) | MWh | number | 0.0 to 157.0; more than 5000 distinct | 0 |
| `x_as_rrsffr_mwh` | The real-time award of Responsive Reserve, FFR kind, integrated over the hour (a MW for an hour) (the source's name: AS Awards RRSFFR) | MWh | number | 0.0 to 175.672674; more than 5000 distinct | 0 |
| `x_as_rrsufr_mwh` | The real-time award of Responsive Reserve, UFR kind, integrated over the hour (a MW for an hour) (the source's name: AS Awards RRSUFR) | MWh | integer | 0 | 0 |
| `x_as_ecrs_mwh` | The real-time award of ERCOT Contingency Reserve Service integrated over the hour (a MW for an hour) (the source's name: AS Awards ECRS) | MWh | number | 0.0 to 237.127168; more than 5000 distinct | 0 |
| `x_as_nspin_mwh` | The real-time award of Non-Spin integrated over the hour (a MW for an hour) (the source's name: AS Awards NSPIN) | MWh | number | 0.0 to 118.98; more than 5000 distinct | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `net_output_mwh` | The resource's Telemetered Net Output integrated over the hour, MWh (positive is discharge; each SCED run's MW held until the next run of the day, never across a run the resource is not in); telemetry, not the settlement meter | MWh | 1637727 | 2026-02-01T06:00:00Z | 2026-08-28T04:00:00Z |

### `ercot_storage_dam_awards_monthly`

What ERCOT's Energy Storage Resources (batteries) were awarded in the day-ahead market in one local month, for the whole fleet or one duration class.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 1244.

- **Time:** ts_utc is the first day of the local (Central) month at 00:00:00Z.
- **Revisions:** Rewritten whole by each run of the builder from ercot_dam_esr_awards; a row whose value has not moved keeps its earlier retrieved_at. vintage is not filled.
- **Source:** erw:ercot_storage_dam_awards ERW derived table, ERCOT storage resources' day-ahead awards by month (docs/methods/ercot_storage_dam_awards.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_dam_awards.md)
- **Method note:** [`docs/methods/ercot_storage_dam_awards.md`](../methods/ercot_storage_dam_awards.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT storage resources' day-ahead awards by month (docs/methods/ercot_storage_dam_awards.md). Via the Energy Research Warehouse (ERW), table `ercot_storage_dam_awards_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:esr_fleet (every storage resource), or a duration class ercot:esr_class_under_2h, _2_to_4h, _4h_and_over, _not_seen_rt (a resource's class is its highest state of charge seen in real time over its highest HSL there, a floor on its hours) | none | text | ercot:esr_class_2_to_4h, ercot:esr_class_4h_and_over, ercot:esr_class_not_seen_rt, ercot:esr_class_under_2h, ercot:esr_fleet | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-12-01T00:00:00Z, 2026-01-01T00:00:00Z, 2026-02-01T00:00:00Z, 2026-03-01T00:00:00Z, 2026-04-01T00:00:00Z, 2026-05-01T00:00:00Z, 2026-06-01T00:00:00Z, 2026-07-01T00:00:00Z, 2026-08-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 40491721.2; 725 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD, USD/MW, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_dam in every row: ERCOT's day-ahead market | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1244 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_storage_dam_awards | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_dam_awards.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-05T03:29:22Z, 2026-10-27T17:23:55Z, 2026-11-15T17:37:22Z, 2026-11-16T16:48:22Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1244 |

Variables (28):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `days_held` | Operating days of the month held | count | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `days_in_month` | The days of the month | count | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `days_missing` | Operating days of the month missing between the first and last held | count | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_bought_mwh` | Energy the resources were awarded to buy (charging) day-ahead, MWh | MWh | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_bought_usd` | Energy bought, each award at the resource's own day-ahead settlement point price, USD | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_sold_mwh` | Energy the resources were awarded to sell day-ahead, MWh | MWh | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_sold_usd` | Energy sold, each award at the resource's own day-ahead settlement point price, USD | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `mw` | The sum of each resource's highest High Sustained Limit (HSL) in the month, MW; a resource with no award is in it | MW | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours` | Resource-hours of the month | count | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours_energy_award` | Resource-hours with a day-ahead energy award | count | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resources` | Storage resources with a row in the month | count | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resources_with_award` | Of those, resources with any award (not blank and not zero) in the month | count | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_ancillary_usd` | The five ancillary service awards valued at their clearing prices, together, USD | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_ancillary_usd_per_mw` | revenue_ancillary_usd over the month's mw, USD/MW | USD/MW | 43 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_ecrs_usd` | ERCOT Contingency Reserve Service awards times their clearing price (MCPC), USD | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_ecrs_usd_per_mw` | revenue_ecrs_usd over the month's mw, USD/MW | USD/MW | 43 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_energy_usd` | Energy sold less energy bought (net of charging), valued day-ahead, USD | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_energy_usd_per_mw` | revenue_energy_usd over the month's mw, USD/MW | USD/MW | 43 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_nspin_usd` | Non-Spin awards times their clearing price (MCPC), USD | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_nspin_usd_per_mw` | revenue_nspin_usd over the month's mw, USD/MW | USD/MW | 43 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_regdn_usd` | Regulation Down awards times their clearing price (MCPC), USD | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_regdn_usd_per_mw` | revenue_regdn_usd over the month's mw, USD/MW | USD/MW | 43 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_regup_usd` | Regulation Up awards times their clearing price (MCPC), USD | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_regup_usd_per_mw` | revenue_regup_usd over the month's mw, USD/MW | USD/MW | 43 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_rrs_usd` | Responsive Reserve awards times their clearing price (MCPC), USD | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_rrs_usd_per_mw` | revenue_rrs_usd over the month's mw, USD/MW | USD/MW | 43 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_total_usd` | Energy and ancillary service awards valued day-ahead, together, USD (a floor on market revenue, not what any battery earned) | USD | 45 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_total_usd_per_mw` | revenue_total_usd over the month's mw, USD/MW | USD/MW | 43 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `ercot_storage_dam_offers_daily`

What ERCOT's Energy Storage Resources offered in the day-ahead market, and how much of it was awarded, summed over one operating day for the whole fleet.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 20982.

- **Time:** ts_utc is the operating day (local, Central) at 00:00:00Z. A MWh here is a MW for an hour, of limit, offered or awarded capacity, or energy.
- **Revisions:** A day added is appended, and a day already held is replaced whole by its new rows; a rebuild from the zips rewrites the table. vintage is ERCOT's publication of the day's disclosure (the operating day plus 60 days).
- **Source:** erw:ercot_storage_dam_offers ERW derived table, ERCOT storage resources' day-ahead offers (docs/methods/ercot_storage_dam_offers.md),  computed from ERCOT's 60-Day DAM Disclosure Reports (NP3-966-ER), the files 60d_DAM_ESR_Data and 60d_DAM_ESR_ASOffers (https://www.ercot.com/mp/data-products/data-product-details?id=NP3-966-ER)
- **Method note:** [`docs/methods/ercot_storage_dam_offers.md`](../methods/ercot_storage_dam_offers.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT storage resources' day-ahead offers by day and by month (docs/methods/ercot_storage_dam_offers.md). Via the Energy Research Warehouse (ERW), table `ercot_storage_dam_offers_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:esr_fleet in every row: every storage resource | none | text | ercot:esr_fleet | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-12-06T00:00:00Z to 2026-08-31T00:00:00Z; 269 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 14698250.15; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, USD, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_dam in every row: ERCOT's day-ahead market | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 20982 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_storage_dam_offers | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1190045004, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1190315373, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1190560109; 269 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-04T21:33:39Z to 2026-11-15T15:54:05Z; 269 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: ERCOT's publication time of the day's 60-day disclosure zip | none | utc time | 2026-02-04T22:53:33Z to 2026-10-30T12:41:46Z; 269 distinct | 0 |

Variables (78):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `as_award_mwh` | The five ancillary services' awards together, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `as_offer_mwh` | Every ancillary service offer block counted once, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `as_offer_mwh_unlisted` | Ancillary service offer blocks of resources with no row in the ESR data file that hour, in no other sum, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_award_mwh` | ECRS: the awards, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_award_usd` | ECRS: the awards at the clearing price, USD | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_offer_mwh` | ERCOT Contingency Reserve Service (online and offline together): the offer blocks priced for the service, added up, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_offer_mwh_le_1` | ECRS: blocks priced at 1 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_offer_mwh_le_100` | ECRS: blocks priced at 100 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_offer_mwh_le_1000` | ECRS: blocks priced at 1,000 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_offer_mwh_le_20` | ECRS: blocks priced at 20 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_offer_mwh_le_5` | ECRS: blocks priced at 5 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_offer_mwh_le_mcpc` | ECRS: of those, blocks priced at or below the hour's clearing price, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `ecrs_unawarded_usd` | ECRS: offered less awarded, each resource and hour, at the hour's clearing price, USD | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_bid_mwh` | The most energy the curves bid to buy (charging), MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_bid_mwh_at_clearing` | Energy bid to buy at the hour's own day-ahead price, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_bought_mwh` | Energy awarded to buy (charging), MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_offer_mwh` | Energy the curves offer to sell at any price (each curve's highest MW when above zero), MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_offer_mwh_at_clearing` | Energy offered to sell at the hour's own day-ahead price at the resource's settlement point, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_offer_mwh_le_0` | Energy offered to sell at a price of 0 USD/MWh or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_offer_mwh_le_100` | Energy offered to sell at 100 USD/MWh or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_offer_mwh_le_1000` | Energy offered to sell at 1,000 USD/MWh or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_offer_mwh_le_25` | Energy offered to sell at 25 USD/MWh or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_offer_mwh_le_250` | Energy offered to sell at 250 USD/MWh or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_offer_mwh_le_50` | Energy offered to sell at 50 USD/MWh or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `energy_sold_mwh` | Energy awarded to sell, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `limit_mwh` | The sum of the High Sustained Limit (HSL), hour by hour (a negative HSL counts as zero), MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `limit_mwh_as_offer` | Of limit_mwh, the rows with an ancillary service offer, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `limit_mwh_award` | Of limit_mwh, the rows with any day-ahead award, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `limit_mwh_energy_offer` | Of limit_mwh, the rows whose curve offers to sell, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `limit_mwh_no_offer` | Of limit_mwh, the rows with no energy curve and no ancillary service offer, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `limit_mwh_no_offer_out` | Of those, the rows with status OUT, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `limit_mwh_out` | Of limit_mwh, the rows with status OUT, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_award_mwh` | Non-Spin: the awards, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_award_usd` | Non-Spin: the awards at the clearing price, USD | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_offer_mwh` | Non-Spin (online and offline together): the offer blocks priced for the service, added up, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_offer_mwh_le_1` | Non-Spin: blocks priced at 1 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_offer_mwh_le_100` | Non-Spin: blocks priced at 100 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_offer_mwh_le_1000` | Non-Spin: blocks priced at 1,000 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_offer_mwh_le_20` | Non-Spin: blocks priced at 20 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_offer_mwh_le_5` | Non-Spin: blocks priced at 5 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_offer_mwh_le_mcpc` | Non-Spin: of those, blocks priced at or below the hour's clearing price, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `nspin_unawarded_usd` | Non-Spin: offered less awarded, each resource and hour, at the hour's clearing price, USD | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_award_mwh` | Regulation Down: the awards, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_award_usd` | Regulation Down: the awards at the clearing price, USD | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_offer_mwh` | Regulation Down: the offer blocks priced for the service, added up, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_offer_mwh_le_1` | Regulation Down: blocks priced at 1 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_offer_mwh_le_100` | Regulation Down: blocks priced at 100 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_offer_mwh_le_1000` | Regulation Down: blocks priced at 1,000 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_offer_mwh_le_20` | Regulation Down: blocks priced at 20 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_offer_mwh_le_5` | Regulation Down: blocks priced at 5 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_offer_mwh_le_mcpc` | Regulation Down: of those, blocks priced at or below the hour's clearing price, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regdn_unawarded_usd` | Regulation Down: offered less awarded, each resource and hour, at the hour's clearing price, USD | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_award_mwh` | Regulation Up: the awards, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_award_usd` | Regulation Up: the awards at the clearing price, USD | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_offer_mwh` | Regulation Up: the offer blocks priced for the service, added up, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_offer_mwh_le_1` | Regulation Up: blocks priced at 1 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_offer_mwh_le_100` | Regulation Up: blocks priced at 100 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_offer_mwh_le_1000` | Regulation Up: blocks priced at 1,000 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_offer_mwh_le_20` | Regulation Up: blocks priced at 20 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_offer_mwh_le_5` | Regulation Up: blocks priced at 5 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_offer_mwh_le_mcpc` | Regulation Up: of those, blocks priced at or below the hour's clearing price, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `regup_unawarded_usd` | Regulation Up: offered less awarded, each resource and hour, at the hour's clearing price, USD | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `resource_hours` | Resource-hours (rows) of the day | count | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `resource_hours_as_offer` | Resource-hours with an ancillary service offer | count | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `resource_hours_energy_offer` | Resource-hours with an energy offer curve | count | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `resource_hours_no_offer` | Resource-hours with neither an energy curve nor an ancillary service offer | count | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `resource_hours_out` | Resource-hours with status OUT | count | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `resources` | Storage resources with a row that day | count | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_award_mwh` | Responsive Reserve: the awards, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_award_usd` | Responsive Reserve: the awards at the clearing price, USD | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_offer_mwh` | Responsive Reserve (any of its three kinds): the offer blocks priced for the service, added up, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_offer_mwh_le_1` | Responsive Reserve: blocks priced at 1 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_offer_mwh_le_100` | Responsive Reserve: blocks priced at 100 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_offer_mwh_le_1000` | Responsive Reserve: blocks priced at 1,000 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_offer_mwh_le_20` | Responsive Reserve: blocks priced at 20 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_offer_mwh_le_5` | Responsive Reserve: blocks priced at 5 USD per MW or less, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_offer_mwh_le_mcpc` | Responsive Reserve: of those, blocks priced at or below the hour's clearing price, MWh | MWh | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |
| `rrs_unawarded_usd` | Responsive Reserve: offered less awarded, each resource and hour, at the hour's clearing price, USD | USD | 269 | 2025-12-06T00:00:00Z | 2026-08-31T00:00:00Z |

### `ercot_storage_dam_offers_monthly`

What ERCOT's Energy Storage Resources offered in the day-ahead market, and how much of it was awarded, summed over one local month for the whole fleet.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 819.

- **Time:** ts_utc is the first day of the local (Central) month at 00:00:00Z. A MWh here is a MW for an hour, of limit, offered or awarded capacity, or energy.
- **Revisions:** Rewritten whole by each run of the builder from ercot_storage_dam_offers_daily and ercot_storage_dam_awards_monthly; vintage is not filled.
- **Source:** erw:ercot_storage_dam_offers ERW derived table, ERCOT storage resources' day-ahead offers (docs/methods/ercot_storage_dam_offers.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_dam_offers.md)
- **Method note:** [`docs/methods/ercot_storage_dam_offers.md`](../methods/ercot_storage_dam_offers.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT storage resources' day-ahead offers by day and by month (docs/methods/ercot_storage_dam_offers.md). Via the Energy Research Warehouse (ERW), table `ercot_storage_dam_offers_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:esr_fleet in every row: every storage resource | none | text | ercot:esr_fleet | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-12-01T00:00:00Z, 2026-01-01T00:00:00Z, 2026-02-01T00:00:00Z, 2026-03-01T00:00:00Z, 2026-04-01T00:00:00Z, 2026-05-01T00:00:00Z, 2026-06-01T00:00:00Z, 2026-07-01T00:00:00Z, 2026-08-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 28508190.28; 797 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD, USD/MW, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_dam in every row: ERCOT's day-ahead market | none | text | ercot_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 819 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_storage_dam_offers | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_dam_offers.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-05T04:24:13Z, 2026-10-19T21:05:17Z, 2026-11-15T17:37:50Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 819 |

Variables (91):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `as_award_mwh` | The five ancillary services' awards together, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_offer_mwh` | Every ancillary service offer block counted once, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_offer_mwh_unlisted` | Ancillary service offer blocks of resources with no row in the ESR data file that hour, in no other sum, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `days_held` | Operating days of the month held | count | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `days_in_month` | The days of the month | count | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `days_missing` | Operating days of the month missing | count | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_award_mwh` | ECRS: the awards, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_award_usd` | ECRS: the awards at the clearing price, USD | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_award_usd_per_mw` | ECRS: ecrs_award_usd over the month's mw, USD/MW | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_offer_mwh` | ERCOT Contingency Reserve Service (online and offline together): the offer blocks priced for the service, added up, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_offer_mwh_le_1` | ECRS: blocks priced at 1 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_offer_mwh_le_100` | ECRS: blocks priced at 100 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_offer_mwh_le_1000` | ECRS: blocks priced at 1,000 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_offer_mwh_le_20` | ECRS: blocks priced at 20 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_offer_mwh_le_5` | ECRS: blocks priced at 5 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_offer_mwh_le_mcpc` | ECRS: of those, blocks priced at or below the hour's clearing price, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_unawarded_usd` | ECRS: offered less awarded, each resource and hour, at the hour's clearing price, USD | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `ecrs_unawarded_usd_per_mw` | ECRS: ecrs_unawarded_usd over the month's mw, USD/MW | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_bid_mwh` | The most energy the curves bid to buy (charging), MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_bid_mwh_at_clearing` | Energy bid to buy at the hour's own day-ahead price, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_bought_mwh` | Energy awarded to buy, as in ercot_storage_dam_awards_monthly, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_offer_mwh` | Energy the curves offer to sell at any price (each curve's highest MW when above zero), MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_offer_mwh_at_clearing` | Energy offered to sell at the hour's own day-ahead price, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_offer_mwh_le_0` | Energy offered to sell at a price of 0 USD/MWh or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_offer_mwh_le_100` | Energy offered to sell at 100 USD/MWh or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_offer_mwh_le_1000` | Energy offered to sell at 1,000 USD/MWh or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_offer_mwh_le_25` | Energy offered to sell at 25 USD/MWh or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_offer_mwh_le_250` | Energy offered to sell at 250 USD/MWh or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_offer_mwh_le_50` | Energy offered to sell at 50 USD/MWh or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `energy_sold_mwh` | Energy awarded to sell, as in ercot_storage_dam_awards_monthly, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `limit_mwh` | The sum of the High Sustained Limit (HSL), hour by hour (a negative HSL counts as zero), MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `limit_mwh_as_offer` | Of limit_mwh, the rows with an ancillary service offer, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `limit_mwh_award` | Of limit_mwh, the rows with any day-ahead award, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `limit_mwh_energy_offer` | Of limit_mwh, the rows whose curve offers to sell, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `limit_mwh_no_offer` | Of limit_mwh, the rows with no energy curve and no ancillary service offer, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `limit_mwh_no_offer_out` | Of those, the rows with status OUT, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `limit_mwh_out` | Of limit_mwh, the rows with status OUT, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `mw` | The month's fleet, from ercot_storage_dam_awards_monthly, MW | MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_award_mwh` | Non-Spin: the awards, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_award_usd` | Non-Spin: the awards at the clearing price, USD | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_award_usd_per_mw` | Non-Spin: nspin_award_usd over the month's mw, USD/MW | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_offer_mwh` | Non-Spin (online and offline together): the offer blocks priced for the service, added up, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_offer_mwh_le_1` | Non-Spin: blocks priced at 1 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_offer_mwh_le_100` | Non-Spin: blocks priced at 100 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_offer_mwh_le_1000` | Non-Spin: blocks priced at 1,000 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_offer_mwh_le_20` | Non-Spin: blocks priced at 20 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_offer_mwh_le_5` | Non-Spin: blocks priced at 5 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_offer_mwh_le_mcpc` | Non-Spin: of those, blocks priced at or below the hour's clearing price, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_unawarded_usd` | Non-Spin: offered less awarded, each resource and hour, at the hour's clearing price, USD | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `nspin_unawarded_usd_per_mw` | Non-Spin: nspin_unawarded_usd over the month's mw, USD/MW | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_award_mwh` | Regulation Down: the awards, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_award_usd` | Regulation Down: the awards at the clearing price, USD | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_award_usd_per_mw` | Regulation Down: regdn_award_usd over the month's mw, USD/MW | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_offer_mwh` | Regulation Down: the offer blocks priced for the service, added up, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_offer_mwh_le_1` | Regulation Down: blocks priced at 1 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_offer_mwh_le_100` | Regulation Down: blocks priced at 100 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_offer_mwh_le_1000` | Regulation Down: blocks priced at 1,000 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_offer_mwh_le_20` | Regulation Down: blocks priced at 20 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_offer_mwh_le_5` | Regulation Down: blocks priced at 5 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_offer_mwh_le_mcpc` | Regulation Down: of those, blocks priced at or below the hour's clearing price, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_unawarded_usd` | Regulation Down: offered less awarded, each resource and hour, at the hour's clearing price, USD | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regdn_unawarded_usd_per_mw` | Regulation Down: regdn_unawarded_usd over the month's mw, USD/MW | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_award_mwh` | Regulation Up: the awards, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_award_usd` | Regulation Up: the awards at the clearing price, USD | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_award_usd_per_mw` | Regulation Up: regup_award_usd over the month's mw, USD/MW | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_offer_mwh` | Regulation Up: the offer blocks priced for the service, added up, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_offer_mwh_le_1` | Regulation Up: blocks priced at 1 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_offer_mwh_le_100` | Regulation Up: blocks priced at 100 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_offer_mwh_le_1000` | Regulation Up: blocks priced at 1,000 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_offer_mwh_le_20` | Regulation Up: blocks priced at 20 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_offer_mwh_le_5` | Regulation Up: blocks priced at 5 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_offer_mwh_le_mcpc` | Regulation Up: of those, blocks priced at or below the hour's clearing price, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_unawarded_usd` | Regulation Up: offered less awarded, each resource and hour, at the hour's clearing price, USD | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `regup_unawarded_usd_per_mw` | Regulation Up: regup_unawarded_usd over the month's mw, USD/MW | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours` | Resource-hours (rows) of the month | count | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours_as_offer` | Resource-hours with an ancillary service offer | count | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours_energy_offer` | Resource-hours with an energy offer curve | count | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours_no_offer` | Resource-hours with neither an energy curve nor an ancillary service offer | count | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours_out` | Resource-hours with status OUT | count | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_award_mwh` | Responsive Reserve: the awards, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_award_usd` | Responsive Reserve: the awards at the clearing price, USD | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_award_usd_per_mw` | Responsive Reserve: rrs_award_usd over the month's mw, USD/MW | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_offer_mwh` | Responsive Reserve (any of its three kinds): the offer blocks priced for the service, added up, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_offer_mwh_le_1` | Responsive Reserve: blocks priced at 1 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_offer_mwh_le_100` | Responsive Reserve: blocks priced at 100 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_offer_mwh_le_1000` | Responsive Reserve: blocks priced at 1,000 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_offer_mwh_le_20` | Responsive Reserve: blocks priced at 20 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_offer_mwh_le_5` | Responsive Reserve: blocks priced at 5 USD per MW or less, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_offer_mwh_le_mcpc` | Responsive Reserve: of those, blocks priced at or below the hour's clearing price, MWh | MWh | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_unawarded_usd` | Responsive Reserve: offered less awarded, each resource and hour, at the hour's clearing price, USD | USD | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rrs_unawarded_usd_per_mw` | Responsive Reserve: rrs_unawarded_usd over the month's mw, USD/MW | USD/MW | 9 | 2025-12-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `ercot_storage_node_basis`

For one storage resource's settlement point (or all of them summed up), its real-time price against the hub average HB_HUBAVG over the days of node prices held.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 2064.

- **Time:** ts_utc is the first day held at 00:00:00Z; freq P1W, though the span is every day of ercot_rtm_node_prices.
- **Revisions:** Rewritten whole by each run of the builder from ercot_rtm_node_prices and ercot_dam_esr_awards; vintage is not filled.
- **Source:** erw:ercot_storage_realtime ERW derived table (docs/methods/ercot_storage_realtime.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_realtime.md)
- **Method note:** [`docs/methods/ercot_storage_realtime.md`](../methods/ercot_storage_realtime.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT storage in real time beside its day-ahead awards, by month, and the storage nodes' prices against the hub (docs/methods/ercot_storage_realtime.md). Via the Energy Research Warehouse (ERW), table `ercot_storage_node_basis`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:<settlement point> of a storage resource, or ercot:esr_nodes for the rows that sum the points up | none | text | for example ercot:ABINDUST_RN, ercot:ADL_RN, ercot:AE_RN; 294 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-28T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 4.9614 to 4746.0; 767 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1W | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_rtm in every row: ERCOT's real-time market | none | text | ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The settlement point's name; empty on the ercot:esr_nodes summary rows | none | text | for example ABINDUST_RN, ADL_RN, AE_RN; 293 distinct | 13 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_storage_realtime | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_realtime.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T19:55:40Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2064 |

Variables (17):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `intervals` | 15-minute intervals both the node's and the hub's prices hold | count | 293 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `intervals_median` | ercot:esr_nodes: median of the points' interval counts | count | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `mean_abs_difference` | Mean of the absolute difference between node and hub price, USD/MWh | USD/MWh | 293 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `mean_abs_difference_median` | ercot:esr_nodes: median of the points' mean absolute differences from the hub, USD/MWh | USD/MWh | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `mean_hub` | Mean real-time price at HB_HUBAVG over the same intervals, USD/MWh (on ercot:esr_nodes, the median over the points) | USD/MWh | 294 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `mean_node` | Mean real-time price at the node over those intervals, USD/MWh | USD/MWh | 293 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `mean_node_median` | ercot:esr_nodes: median of the points' mean prices, USD/MWh | USD/MWh | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `nodes` | ercot:esr_nodes: the settlement points summed up, each counted once | count | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `nodes_spread_above_hub` | ercot:esr_nodes: points whose spread is wider than the hub's | count | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `nodes_with_spread` | ercot:esr_nodes: points with every whole day the hub has, which enter the spread figures | count | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `spread_hub` | The same spread at HB_HUBAVG, USD/MWh | USD/MWh | 294 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `spread_node` | At the node, a day's 16 dearest intervals less its 16 cheapest, averaged over the whole days: what moving four hours a day could capture, before losses, USD/MWh | USD/MWh | 293 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `spread_node_mean` | ercot:esr_nodes: mean of the points' spreads, USD/MWh | USD/MWh | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `spread_node_median` | ercot:esr_nodes: median of the points' spreads, USD/MWh | USD/MWh | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `spread_node_p10` | ercot:esr_nodes: 10th percentile of the points' spreads, USD/MWh | USD/MWh | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `spread_node_p90` | ercot:esr_nodes: 90th percentile of the points' spreads, USD/MWh | USD/MWh | 1 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |
| `whole_days` | The whole days the spreads are averaged over | count | 294 | 2026-09-28T00:00:00Z | 2026-09-28T00:00:00Z |

### `ercot_storage_rt_monthly`

What ERCOT's storage resources did in real time beside what they were awarded day-ahead, over the operating days both disclosures hold in one local month, for the fleet or one duration class.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 1620.

- **Time:** ts_utc is the first day of the local (Central) month at 00:00:00Z.
- **Revisions:** Rewritten whole by each run of the builder from ercot_sced_esr_hourly, ercot_dam_esr_awards and the hub price tables; vintage is not filled.
- **Source:** erw:ercot_storage_realtime ERW derived table (docs/methods/ercot_storage_realtime.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_realtime.md)
- **Method note:** [`docs/methods/ercot_storage_realtime.md`](../methods/ercot_storage_realtime.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT storage in real time beside its day-ahead awards, by month, and the storage nodes' prices against the hub (docs/methods/ercot_storage_realtime.md). Via the Energy Research Warehouse (ERW), table `ercot_storage_rt_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:esr_fleet, or a duration class ercot:esr_class_under_2h, _2_to_4h, _4h_and_over, _not_seen_rt | none | text | ercot:esr_class_2_to_4h, ercot:esr_class_4h_and_over, ercot:esr_class_not_seen_rt, ercot:esr_class_under_2h, ercot:esr_fleet | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-02-01T00:00:00Z, 2026-03-01T00:00:00Z, 2026-04-01T00:00:00Z, 2026-05-01T00:00:00Z, 2026-06-01T00:00:00Z, 2026-07-01T00:00:00Z, 2026-08-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -283942.331 to 42395561.48; 1040 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, USD, USD/MW, USD/MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1620 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1620 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_storage_realtime | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_realtime.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T19:55:40Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1620 |

Variables (47):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `as_da_ecrs_mwh` | ERCOT Contingency Reserve Service awarded day-ahead, a MW for an hour | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_da_nspin_mwh` | Non-Spin awarded day-ahead, a MW for an hour | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_da_regdn_mwh` | Regulation Down awarded day-ahead, a MW for an hour | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_da_regup_mwh` | Regulation Up awarded day-ahead, a MW for an hour | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_da_rrs_mwh` | Responsive Reserve awarded day-ahead, a MW for an hour | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_imbalance_ecrs_mwh` | ERCOT Contingency Reserve Service, real time less day-ahead (not valued here) | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_imbalance_nspin_mwh` | Non-Spin, real time less day-ahead (not valued here) | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_imbalance_regdn_mwh` | Regulation Down, real time less day-ahead (not valued here) | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_imbalance_regup_mwh` | Regulation Up, real time less day-ahead: the quantity ERCOT settles at the real-time price (not valued here) | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_imbalance_rrs_mwh` | Responsive Reserve, real time less day-ahead (not valued here) | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_rt_ecrs_mwh` | ERCOT Contingency Reserve Service awarded in real time, a MW for an hour | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_rt_nspin_mwh` | Non-Spin awarded in real time, a MW for an hour | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_rt_regdn_mwh` | Regulation Down awarded in real time, a MW for an hour | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_rt_regup_mwh` | Regulation Up awarded in real time, a MW for an hour | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `as_rt_rrs_mwh` | Responsive Reserve awarded in real time, a MW for an hour | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `da_bought_mwh` | Day-ahead energy awarded to buy on the same days, MWh | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `da_net_mwh` | Day-ahead net energy award, MWh | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `da_node_minus_hub_bought` | Day-ahead price at the resources' own settlement points less the hub average's, weighted by the MWh bought, USD/MWh | USD/MWh | 22 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `da_node_minus_hub_sold` | Day-ahead price at the resources' own settlement points less the hub average's, weighted by the MWh sold, USD/MWh | USD/MWh | 23 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `da_sold_mwh` | Day-ahead energy awarded to sell on the same days, MWh | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `days_held` | Operating days both disclosures hold in the month | count | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `days_in_month` | The days of the month | count | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `intervals` | Resource-intervals in the month | count | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `intervals_priced` | Of those, intervals with a hub price (only those are valued) | count | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `mw` | The sum of each resource's highest day-ahead High Sustained Limit of the month, MW | MW | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours` | Resource-hours in the month | count | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours_day_ahead_only` | Resource-hours in the day-ahead file only | count | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resource_hours_real_time_only` | Resource-hours in the real-time file only | count | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resources` | Storage resources in the month | count | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_da_ancillary_usd` | Day-ahead ancillary service awards at their clearing prices, on the matched days, USD | USD | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_da_ancillary_usd_per_mw` | revenue_da_ancillary_usd over the month's mw, USD/MW | USD/MW | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_da_energy_usd` | Day-ahead energy awards at the node's day-ahead price, on the matched days, USD | USD | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_da_energy_usd_per_mw` | revenue_da_energy_usd over the month's mw, USD/MW | USD/MW | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_da_position_hub_usd` | A quarter of the hour's day-ahead award (sales less purchases) at the same hub price: the day-ahead position settled back in real time, USD | USD | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_da_position_hub_usd_per_mw` | revenue_da_position_hub_usd over the month's mw, USD/MW | USD/MW | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_da_usd` | revenue_da_energy_usd plus revenue_da_ancillary_usd, USD | USD | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_da_usd_per_mw` | revenue_da_usd over the month's mw, USD/MW | USD/MW | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_market_hub_usd` | revenue_da_usd plus revenue_rt_deviation_hub_usd, USD (not what any battery earned) | USD | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_market_hub_usd_per_mw` | revenue_market_hub_usd over the month's mw, USD/MW | USD/MW | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_rt_deviation_hub_usd` | revenue_rt_output_hub_usd less revenue_da_position_hub_usd, USD | USD | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_rt_deviation_hub_usd_per_mw` | revenue_rt_deviation_hub_usd over the month's mw, USD/MW | USD/MW | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_rt_output_hub_usd` | All real-time energy, each resource and 15-minute interval, at the real-time price of HB_HUBAVG (not the resource's node), USD | USD | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `revenue_rt_output_hub_usd_per_mw` | revenue_rt_output_hub_usd over the month's mw, USD/MW | USD/MW | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rt_charge_mwh` | Real-time charging: the Telemetered Net Output below zero, integrated, MWh | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rt_deviation_mwh` | rt_net_mwh less da_net_mwh: what the fleet did beyond its day-ahead position, MWh | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rt_discharge_mwh` | Real-time discharge: the fleet's Telemetered Net Output above zero, integrated, MWh | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `rt_net_mwh` | Real-time net output, integrated, MWh | MWh | 35 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `ercot_storage_rt_offers_monthly`

What ERCOT's storage fleet offered to sell in real-time dispatch (SCED), by price limit, summed over one local month.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 175.

- **Time:** ts_utc is the first day of the local (Central) month at 00:00:00Z; months from February 2026.
- **Revisions:** Merged by (entity, variable, ts_utc); each run recomputes every month from the 60-day SCED zips held on the data machine. vintage is not filled.
- **Source:** ercot:NP3-965-ER ERCOT, 60-Day SCED Disclosure Reports (60d_ESR_Data_in_SCED) (https://www.ercot.com/mp/data-products/data-product-details?id=NP3-965-ER)
- **Method note:** [`docs/methods/ercot_storage_realtime.md`](../methods/ercot_storage_realtime.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERCOT storage fleet's real-time energy offers to sell by price band, by month, from ERCOT's 60-Day SCED Disclosure Reports (60d_ESR_Data_in_SCED, NP3-965-ER). Via the Energy Research Warehouse (ERW), table `ercot_storage_rt_offers_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:esr_fleet in every row: every storage resource | none | text | ercot:esr_fleet | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-02-01T00:00:00Z, 2026-03-01T00:00:00Z, 2026-04-01T00:00:00Z, 2026-05-01T00:00:00Z, 2026-06-01T00:00:00Z, 2026-07-01T00:00:00Z, 2026-08-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0249 to 14114469.608; 164 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, MWh/MW-day, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_rtm in every row: ERCOT's real-time market | none | text | ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 175 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_storage_rt_offers | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_realtime.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T21:12:53Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 175 |

Variables (25):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `days_held` | Operating days of the month held | count | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `days_in_month` | The days of the month | count | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `mw` | The fleet's MW: each resource's highest High Sustained Limit (HSL) of the month, added up | MW | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_any_mwh` | Energy offered to sell at any price (each curve's highest MW), summed over the month, MWh | MWh | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_any_mwh_per_mw_day` | offered_sell_any_mwh over the fleet's mw and the days held, MWh per MW per day | MWh/MW-day | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_0_mwh` | Energy offered to sell at a price of 0 USD/MWh or less: each SCED run's curve MW at that price (clipped at zero) held until the next run, summed over the month, MWh | MWh | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_0_mwh_per_mw_day` | offered_sell_le_0_mwh over the fleet's mw and the days held, MWh per MW per day | MWh/MW-day | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_0_share_pct` | offered_sell_le_0_mwh as a percent of offered_sell_any_mwh | pct | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_1000_mwh` | Energy offered to sell at 1,000 USD/MWh or less, summed over the month, MWh | MWh | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_1000_mwh_per_mw_day` | offered_sell_le_1000_mwh over the fleet's mw and the days held, MWh per MW per day | MWh/MW-day | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_1000_share_pct` | offered_sell_le_1000_mwh as a percent of offered_sell_any_mwh | pct | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_100_mwh` | Energy offered to sell at 100 USD/MWh or less, summed over the month, MWh | MWh | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_100_mwh_per_mw_day` | offered_sell_le_100_mwh over the fleet's mw and the days held, MWh per MW per day | MWh/MW-day | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_100_share_pct` | offered_sell_le_100_mwh as a percent of offered_sell_any_mwh | pct | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_250_mwh` | Energy offered to sell at 250 USD/MWh or less, summed over the month, MWh | MWh | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_250_mwh_per_mw_day` | offered_sell_le_250_mwh over the fleet's mw and the days held, MWh per MW per day | MWh/MW-day | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_250_share_pct` | offered_sell_le_250_mwh as a percent of offered_sell_any_mwh | pct | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_25_mwh` | Energy offered to sell at 25 USD/MWh or less, summed over the month, MWh | MWh | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_25_mwh_per_mw_day` | offered_sell_le_25_mwh over the fleet's mw and the days held, MWh per MW per day | MWh/MW-day | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_25_share_pct` | offered_sell_le_25_mwh as a percent of offered_sell_any_mwh | pct | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_50_mwh` | Energy offered to sell at 50 USD/MWh or less, summed over the month, MWh | MWh | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_50_mwh_per_mw_day` | offered_sell_le_50_mwh over the fleet's mw and the days held, MWh per MW per day | MWh/MW-day | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `offered_sell_le_50_share_pct` | offered_sell_le_50_mwh as a percent of offered_sell_any_mwh | pct | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `resources` | Storage resources in the month | count | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `runs` | Resource-runs of the month: each SCED run counted once for each resource it holds | count | 7 | 2026-02-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `ercot_transmission_projects`

One phase of a transmission project the transmission owners report to ERCOT's Transmission Project and Information Tracking (TPIT) workbook, future, planned, completed or cancelled.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 2203.

- **Time:** event_date is the actual in-service date where ERCOT gives one, else the projected one (x_date_kind says which).
- **Revisions:** A snapshot replaced whole by each run with the workbook ERCOT's planning page names; earlier editions are not kept.
- **Source:** ercot:tpit Electric Reliability Council of Texas (ERCOT), Transmission Project and Information Tracking (https://www.ercot.com/gridinfo/planning)
- **Method note:** [`docs/methods/ercot_transmission_projects.md`](../methods/ercot_transmission_projects.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Transmission Project and Information Tracking (TPIT). Via the Energy Research Warehouse (ERW), table `ercot_transmission_projects`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: ercot_tpit:<ERCOT project number>:<phase number> | none | text | for example ercot_tpit:07TPIT0069:10446, ercot_tpit:100018:100019, ercot_tpit:100020:100021; 2203 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which). Here: The actual in-service date, else the projected one; ERCOT's 9999-01-01 is no date | none | date | 2023-05-25 to 2033-12-15; 511 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: transmission_project in every row | none | text | transmission_project | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: The transmission owner as ERCOT names it | none | text | for example AEN, AEP, AEP TCC; 55 distinct | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 2203 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 2203 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 2203 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 2203 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: The sheet the project is on: future, planned, completed, cancelled | none | text | cancelled, completed, future, planned | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:tpit | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/files/docs/2022/03/02/ERCOT-October-TPIT-No-Cost-100126.xlsx | 0 |
| `x_project_number` | ERCOT's project number (the source's name: ERCOT Project Number) | none | text | for example 07TPIT0069, 100018, 100020; 2203 distinct | 0 |
| `x_phase` | ERCOT's phase number (the source's name: Phase Number) | none | integer | 8143 to 116033; 2203 distinct | 0 |
| `x_title` | The project's title, ERCOT's text (the source's name: Project Title) | none | text | for example 138kV Flewellen to Fort Bend Ckt 09G-60E Upgrades, 138kV transmission upgrade to serve Kirkland large load., 16th Street auto transformer replacement/addition.; 1803 distinct | 41: ERCOT gives no title |
| `x_description` | The project's description, ERCOT's text (the source's name: Project Description) | none | text | for example (5705) FOWLERTON to (5723) LOS ANGELES 138 kV Ckt 1 Rebuild [245 MVA Minimum] or double circuit existing, (5727) PAWNEE SWITCHING STATION to (5902) SAN MIGUEL GEN 138 kV Ckt 1 Rebuild [276 MVA Minimum], (In terms of completed Waterfowl substation) Loop new CEHE 138kV substation Odin (ODI) into Ckt.36 to create new Ckt.36 COPPER to Odin to Booster tap to Jones Creek.; 1794 distinct | 345: ERCOT gives no description |
| `x_comment` | ERCOT's comments or reasons for the project (the source's name: Comments/Reasons) | none | text | for example 1/10/2023: Added information to clarify circuit rating., 1/10/2023: Added information to clarify timing for final circuit rating upgrade., 1/10/2023: Changes to description based on final design.; 83 distinct | 1821: ERCOT gives no comment |
| `x_from` | The terminal the line or facility runs from, as ERCOT gives it (the source's name: Terminal "From") | none | text | for example 0, 199, 240; 1275 distinct | 255: ERCOT gives none |
| `x_to` | The terminal the line or facility runs to, as ERCOT gives it (the source's name: Terminal "To") | none | text | for example -, 0, 170722; 1086 distinct | 797: ERCOT gives none |
| `x_ercot_status` | ERCOT's own status text (Conceptual, Planned, Under Construction, In-Service) (the source's name: Transmission Status) | none | text | Conceptual, In-Service, Planned, Under Construction | 31: ERCOT gives none |
| `x_owner` | The transmission owner (same as parties) (the source's name: Transmission Owner (Text)) | none | text | for example AEN, AEP, AEP TCC; 55 distinct | 0 |
| `x_projected_in_service` | The projected in-service date, as given (the source's name: Projected In-Service) | none | date | 2022-11-30 to 2033-12-15; 448 distinct | 0 |
| `x_actual_in_service` | The actual in-service date, as given (9999-01-01 is ERCOT's no date) (the source's name: Actual In-Service) | none | date | 2023-05-25 to 9999-01-01; 175 distinct | 1852: Not in service or no date given |
| `x_kv` | The service level (voltage) (the source's name: Service Level kV) | kV | integer | 115, 138, 345, 69, 765 | 1: ERCOT gives none (one row) |
| `x_new_circuit_miles` | New transmission circuit miles (the source's name: Trans Circuit Miles New) | miles | number | 0.0 to 257.45; 183 distinct | 6: ERCOT gives none |
| `x_upgraded_circuit_miles` | Rebuilt or upgraded transmission circuit miles (the source's name: Trans Circuit Miles Rebuilt) | miles | number | 0.0 to 292.8; 436 distinct | 10: ERCOT gives none |
| `x_autotransformer_mva` | Autotransformer capacity (the source's name: Autotransformer Capacity) | MVA | integer | -536 to 8316; 35 distinct | 1: ERCOT gives none (one row) |
| `x_reactive_mvar` | Reactive capability, ERCOT's cell kept as text (some cells hold two figures, such as 0,28.8) (the source's name: Reactive Capability) | Mvar | text | for example -100,0, -1200,0, -140,0; 90 distinct | 2005: ERCOT gives none |
| `x_county_start` | The county of the substation or the start of the line (the source's name: County Location for Substation) | none | text | for example Anderson, Andrews, Angelina; 185 distinct | 193: ERCOT gives none |
| `x_county_end` | The county of the end of the line (the source's name: County Location for Ending) | none | text | for example Anderson, Andrews, Angelina; 175 distinct | 769: ERCOT gives none |
| `x_tier` | ERCOT's planning charter tier (Tier 1 to Tier 4) (the source's name: Planning Charter Tier) | none | text | Tier 1, Tier 2, Tier 3, Tier 4 | 0 |
| `x_rpg_number` | ERCOT's RPG project number (the source's name: RPG Number) | none | text | for example 18RPG012, 19RPG013, 19RPG018; 166 distinct | 1663: ERCOT gives none |
| `x_rtp_number` | ERCOT's RTP project number (the source's name: RTP Project Number) | none | text | for example 2013-R102, 2013-R104, 2013-R25; 65 distinct | 2086: ERCOT gives none |
| `x_date_kind` | Which date event_date is: actual or projected | none | text | actual, projected | 0 |
| `x_sheet` | The workbook sheet the row is on (Future, Planned, Completed, Cancelled) | none | text | Cancelled, Completed, Future, Planned | 0 |

### `ercot_wind_solar_forecast`

ERCOT's system-wide wind or solar output for one hour, actual or as forecast a day ahead.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 5322.

- **Time:** ts_utc is the hour's start in UTC.
- **Revisions:** Merged by (entity, variable, ts_utc); a run replaces an hour's actual with a newer posting's and its forecast with one from a newer posting still at least 24 hours ahead, and the table keeps hours ERCOT's list has dropped. vintage is not filled.
- **Source:** ercot:NP4-732-CD ERCOT, NP4-732-CD (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-732-CD)
- **Source:** ercot:NP4-745-CD ERCOT, NP4-745-CD (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-745-CD)
- **Method note:** [`docs/methods/ercot_wind_solar_forecast.md`](../methods/ercot_wind_solar_forecast.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). NP4-732-CD: hourly averaged actual and forecasted values; NP4-745-CD: hourly averaged actual and forecasted values. Via the Energy Research Warehouse (ERW), table `ercot_wind_solar_forecast`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:SYSTEM in every row: ERCOT's whole system | none | text | ercot:SYSTEM | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-27T05:00:00Z to 2026-11-26T15:00:00Z; 1451 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 47852.8; 4175 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5322 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: SYSTEM in every row, not a price node | none | text | SYSTEM | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP4-732-CD, ercot:NP4-745-CD | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13028, https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13483 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T09:30:26Z to 2026-11-19T17:41:55Z; 76 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5322 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `solar_actual_mw` | Actual solar output, ERCOT's SYSTEM_WIDE_GEN from the newest posting that holds the hour (NP4-745-CD), MW | MW | 1283 | 2026-09-27T05:00:00Z | 2026-11-19T15:00:00Z |
| `solar_forecast_24h_mw` | ERCOT's short-term solar power forecast (STPPF) for the hour, from the newest posting published at least 24 hours before the hour began, MW | MW | 1378 | 2026-09-30T06:00:00Z | 2026-11-26T15:00:00Z |
| `wind_actual_mw` | Actual wind output, ERCOT's SYSTEM_WIDE_GEN from the newest posting that holds the hour (NP4-732-CD), MW | MW | 1283 | 2026-09-27T05:00:00Z | 2026-11-19T15:00:00Z |
| `wind_forecast_24h_mw` | ERCOT's short-term wind power forecast (STWPF) for the hour, from the newest posting published at least 24 hours before the hour began, MW | MW | 1378 | 2026-09-30T06:00:00Z | 2026-11-26T15:00:00Z |

### `ercot_wind_solar_hsl_daily`

ERCOT's system-wide wind or solar output, High Sustained Limit (HSL), or output below the HSL, summed over one operating day.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 300.

- **Time:** ts_utc is the ERCOT operating day (Central) at 00:00:00Z; a day is written only with every hour's output and HSL.
- **Revisions:** Merged by (entity, variable, ts_utc); a daily run reads the last postings of the last three publish days, and a day read again replaces the one held. vintage is not filled.
- **Source:** ercot:np4_732_745 Wind and Solar Power Production, Hourly Averaged Actual and Forecasted Values (NP4-732-CD, NP4-745-CD) (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-745-CD)
- **Method note:** [`docs/methods/ercot_wind_solar_hsl_daily.md`](../methods/ercot_wind_solar_hsl_daily.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Wind and Solar Power Production, Hourly Averaged Actual and Forecasted Values (NP4-732-CD, NP4-745-CD). Via the Energy Research Warehouse (ERW), table `ercot_wind_solar_hsl_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:system in every row: ERCOT's whole system | none | text | ercot:system | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-19T00:00:00Z to 2026-11-15T00:00:00Z; 50 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 2600.84 to 653022.27; 300 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 300 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 300 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:np4_732_745 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1277035825, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1277448708, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1277855609; 50 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-27T08:30:58Z to 2026-11-16T14:49:57Z; 33 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 300 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `solar_below_hsl_mwh` | Solar output below the HSL: the sum over hours of HSL less GEN where positive, MWh; the ERW's estimate of curtailment, not ERCOT's figure | MWh | 50 | 2026-09-19T00:00:00Z | 2026-11-15T00:00:00Z |
| `solar_generation_mwh` | Solar output in the day: the sum of ERCOT's hourly system-wide GEN, MWh | MWh | 50 | 2026-09-19T00:00:00Z | 2026-11-15T00:00:00Z |
| `solar_hsl_mwh` | The sum of the hourly system-wide High Sustained Limit of solar, MWh | MWh | 50 | 2026-09-19T00:00:00Z | 2026-11-15T00:00:00Z |
| `wind_below_hsl_mwh` | Wind output below the HSL: the sum over hours of HSL less GEN where positive, MWh; the ERW's estimate of curtailment, not ERCOT's figure | MWh | 50 | 2026-09-19T00:00:00Z | 2026-11-15T00:00:00Z |
| `wind_generation_mwh` | Wind output in the day: the sum of ERCOT's hourly system-wide GEN, MWh | MWh | 50 | 2026-09-19T00:00:00Z | 2026-11-15T00:00:00Z |
| `wind_hsl_mwh` | The sum of the hourly system-wide High Sustained Limit of wind (the output the resources report they could sustain), MWh | MWh | 50 | 2026-09-19T00:00:00Z | 2026-11-15T00:00:00Z |

### `ercot_wind_solar_hsl_hourly`

ERCOT's wind or solar output or High Sustained Limit for one hour, system-wide or in one of ERCOT's wind or solar regions.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 17757.

- **Time:** ts_utc is the hour's start in UTC (ERCOT's DELIVERY_DATE and HOUR_ENDING are Central time, the hour named by its end).
- **Revisions:** Merged by (entity, variable, ts_utc); an hour's value is the newest posting's that holds it. vintage is not filled.
- **Source:** ercot:np4_742_745_region ERCOT NP4-742-CD, Wind Power Production, Hourly Averaged Actual and Forecasted Values by Geographical Region (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-742-CD)
- **Source:** ercot:np4_742_745_region ERCOT NP4-745-CD, Solar Power Production, Hourly Averaged Actual and Forecasted Values by Geographical Region (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-745-CD)
- **Method note:** [`docs/methods/ercot_wind_solar_hsl_hourly.md`](../methods/ercot_wind_solar_hsl_hourly.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Wind and Solar Power Production, Hourly Averaged Actual and Forecasted Values by Geographical Region (NP4-742-CD, NP4-745-CD) [terms: "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." (https://www.ercot.com/help/terms, read 6 October 2026)]. Via the Energy Research Warehouse (ERW), table `ercot_wind_solar_hsl_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:system (ERCOT's SYSTEM_WIDE columns), ercot:wind:<REGION> (PANHANDLE, COASTAL, SOUTH, WEST, NORTH) or ercot:solar:<Region> (CenterWest, NorthWest, FarWest, FarEast, SouthEast, CenterEast): ERCOT's wind and solar regions, not its weather zones | none | text | ercot:solar:CenterEast, ercot:solar:CenterWest, ercot:solar:FarEast, ercot:solar:FarWest, ercot:solar:NorthWest, ercot:solar:SouthEast, ercot:system, ercot:wind:COASTAL, ercot:wind:NORTH, ercot:wind:PANHANDLE, ercot:wind:SOUTH, ercot:wind:WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-28T05:00:00Z to 2026-11-16T12:00:00Z; 1184 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 33464.82; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 17757 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The region as ERCOT prints it; empty on the system-wide rows | none | text | COASTAL, CenterEast, CenterWest, FarEast, FarWest, NORTH, NorthWest, PANHANDLE, SOUTH, SouthEast, WEST | 4733 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:np4_742_745_region | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1280661939, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1280661943, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1281045111; 146 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T09:32:02Z to 2026-11-16T14:51:24Z; 172 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 17757 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `solar_generation_mw` | ERCOT's GEN for solar: the hourly average of actual output, MW | MW | 8288 | 2026-09-28T05:00:00Z | 2026-11-16T12:00:00Z |
| `solar_hsl_mw` | ERCOT's SYSTEM_WIDE_HSL for solar: the hourly average of the High Sustained Limit, MW (system-wide only) | MW | 1182 | 2026-09-28T05:00:00Z | 2026-11-16T12:00:00Z |
| `wind_generation_mw` | ERCOT's GEN for wind: the hourly average of actual output, MW | MW | 7104 | 2026-09-28T05:00:00Z | 2026-11-16T12:00:00Z |
| `wind_hsl_mw` | ERCOT's SYSTEM_WIDE_HSL for wind: the hourly average of the High Sustained Limit, the output the resources report they could sustain, MW (system-wide only) | MW | 1183 | 2026-09-28T05:00:00Z | 2026-11-16T12:00:00Z |

### `ercot_wind_solar_hsl_monthly`

ERCOT's wind or solar output, High Sustained Limit (HSL), or output below the HSL, summed over one Central month, system-wide or in one of ERCOT's wind or solar regions.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 45.

- **Time:** ts_utc is the first day of the Central (America/Chicago) month at 00:00:00Z.
- **Revisions:** Merged by (entity, variable, ts_utc), built from ercot_wind_solar_hsl_hourly and nothing else; a month is written only with at least 95 percent of its hours held. vintage is not filled.
- **Source:** erw:ercot_wind_solar_hsl_monthly ERW derived table (warehouse/connectors/ercot_wind_solar_history.py) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/curtailment.md)
- **Method note:** [`docs/methods/curtailment.md`](../methods/curtailment.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. ERW derived table: ERCOT output below HSL by month, the ERW's estimate (docs/methods/curtailment.md). Via the Energy Research Warehouse (ERW), table `ercot_wind_solar_hsl_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:system, ercot:wind:<REGION> (COASTAL, NORTH, PANHANDLE, SOUTH, WEST) or ercot:solar:<Region> (CenterEast, CenterWest, FarEast, FarWest, NorthWest, SouthEast): ERCOT's wind and solar regions, not its weather zones | none | text | ercot:solar:CenterEast, ercot:solar:CenterWest, ercot:solar:FarEast, ercot:solar:FarWest, ercot:solar:NorthWest, ercot:solar:SouthEast, ercot:system, ercot:wind:COASTAL, ercot:wind:NORTH, ercot:wind:PANHANDLE, ercot:wind:SOUTH, ercot:wind:WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-10-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1113619.43, 2607227.26, 365821.2, 420812.25, 5.5953, 5061592.3, 590543.8, 6.3796, 613736.39, 6274391.08, 6537999.76, 695505.64, 744.0, 844441.06, 8668423.42, 874816.54, 877076.59, 911097.53, 922889.51, 9256808.64 | 0 |
| `unit` | The unit of the row's value | none | text | MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 45 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The region as ERCOT prints it; empty on the system-wide rows | none | text | COASTAL, CenterEast, CenterWest, FarEast, FarWest, NORTH, NorthWest, PANHANDLE, SOUTH, SouthEast, WEST | 12 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ercot_wind_solar_hsl_monthly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/warehouse/connectors/ercot_wind_solar_history.py | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-05T23:20:19Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 45 |

Variables (12):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `solar_below_hsl_mwh` | Solar output below the HSL: the sum over hours of HSL less GEN where positive, MWh; the ERW's estimate of curtailment, not ERCOT's figure | MWh | 1 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_below_hsl_share_pct` | solar_below_hsl_mwh over solar_hsl_mwh, times 100 | pct | 1 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_generation_mwh` | Solar output in the month: the sum of hourly GEN, MWh | MWh | 7 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_hours_held` | Hours of the month held for solar (with both GEN and HSL where the area has an HSL, with GEN for a region) | count | 7 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_hours_in_month` | The hours the Central month has | count | 7 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_hsl_mwh` | The sum of the hourly High Sustained Limit of solar, MWh (system-wide only) | MWh | 1 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_below_hsl_mwh` | Wind output below the HSL: the sum over hours of HSL less GEN where positive, MWh; the ERW's estimate of curtailment, not ERCOT's figure | MWh | 1 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_below_hsl_share_pct` | wind_below_hsl_mwh over wind_hsl_mwh, times 100 | pct | 1 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_generation_mwh` | Wind output in the month: the sum of hourly GEN, MWh | MWh | 6 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_hours_held` | Hours of the month held for wind (with both GEN and HSL where the area has an HSL, with GEN for a region) | count | 6 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_hours_in_month` | The hours the Central month has | count | 6 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `wind_hsl_mwh` | The sum of the hourly High Sustained Limit of wind (the output the resources report they could sustain), MWh (system-wide only) | MWh | 1 | 2026-10-01T00:00:00Z | 2026-10-01T00:00:00Z |

### `ercot_wind_solar_output_hourly`

ERCOT's system-wide wind or solar output for one hour, from ERCOT's yearly Hourly Aggregated Wind and Solar Output workbooks (2023 to 2025).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 52608.

- **Time:** ts_utc is the hour's start in UTC (the workbook's Time (Hour-Ending) is Central clock time).
- **Revisions:** Merged by (entity, variable, ts_utc); where two saved workbooks hold the same hour the later published is kept, and a new year's workbook is added when ERCOT posts it. vintage is not filled.
- **Source:** ercot:PG7-126-M ERCOT PG7-126-M, Hourly Aggregated Wind and Solar Output (https://www.ercot.com/mp/data-products/data-product-details?id=PG7-126-M)
- **Method note:** [`docs/methods/ercot_wind_solar_output_hourly.md`](../methods/ercot_wind_solar_output_hourly.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Hourly Aggregated Wind and Solar Output (yearly workbook: system-wide hourly wind and solar output) [terms: "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." (https://www.ercot.com/help/terms, read 6 October 2026)]. Via the Energy Research Warehouse (ERW), table `ercot_wind_solar_output_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:system in every row: ERCOT's whole system | none | text | ercot:system | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-01-01T06:00:00Z to 2026-01-01T05:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.0000046131608542e-05 to 29503.08663357205; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 52608 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 52608 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:PG7-126-M | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1068801799, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1182433954, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=971575038 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T09:22:54Z, 2026-10-07T09:32:46Z, 2026-10-07T09:32:54Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 52608 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `solar_generation_mw` | Hourly aggregated solar output, the workbook's ERCOT.PVGR.GEN (sheet Solar Data), MW | MW | 26304 | 2023-01-01T06:00:00Z | 2026-01-01T05:00:00Z |
| `wind_generation_mw` | Hourly aggregated wind output, the workbook's ERCOT.WIND.GEN (sheet Wind Data), MW | MW | 26304 | 2023-01-01T06:00:00Z | 2026-01-01T05:00:00Z |

### `ercot_zone_load_hourly`

ERCOT's native load in one weather zone, or ERCOT's total, for one hour, from its Hourly Load Data Archives.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 933534.

- **Time:** ts_utc is the hour's start in UTC (ERCOT gives the hour's end, Central; the repeated autumn hour is in the file twice, the second marked DST).
- **Revisions:** Merged by (entity, variable, ts_utc) into the table held; ERCOT extends the current year's file month by month. vintage is the yearly file's publish time.
- **Source:** ercot:load_hist Electric Reliability Council of Texas (ERCOT), Hourly Load Data Archives, native load by weather zone (https://www.ercot.com/gridinfo/load/load_hist)
- **Method note:** [`docs/methods/ercot_zone_load_hourly.md`](../methods/ercot_zone_load_hourly.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Hourly Load Data Archives, native load by weather zone [terms: "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." (https://www.ercot.com/help/terms, read 6 October 2026)]. Via the Energy Research Warehouse (ERW), table `ercot_zone_load_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:<weather zone> (COAST, EAST, FWEST, NCENT, NORTH, SCENT, SOUTH, WEST) or ercot:system (ERCOT's own total column, never a sum made here); weather zones are not load zones | none | text | ercot:COAST, ercot:EAST, ercot:FWEST, ercot:NCENT, ercot:NORTH, ercot:SCENT, ercot:SOUTH, ercot:WEST, ercot:system | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T06:00:00Z to 2026-11-01T04:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 488.272293 to 91133.727696; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_load in every row | none | text | ercot_load | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The zone's column name in ERCOT's file; older files' FAR_WEST, NORTH_C, SOUTHERN and SOUTH_C are FWEST, NCENT, SOUTH and SCENT; ERCOT for the total | none | text | COAST, EAST, ERCOT, FAR_WEST, FWEST, NCENT, NORTH, NORTH_C, SCENT, SOUTH, SOUTHERN, SOUTH_C, WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:load_hist | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/files/docs/2016/01/07/native_load_2015.xls, https://www.ercot.com/files/docs/2017/01/10/native_Load_2016.zip, https://www.ercot.com/files/docs/2018/01/09/native_load_2017.zip, https://www.ercot.com/files/docs/2019/01/07/native_load_2018.zip, https://www.ercot.com/files/docs/2020/01/09/Native_Load_2019.zip, https://www.ercot.com/files/docs/2021/01/12/Native_Load_2020.zip, https://www.ercot.com/files/docs/2021/11/12/Native_Load_2021.zip, https://www.ercot.com/files/docs/2022/02/08/Native_Load_2022.zip, https://www.ercot.com/files/docs/2023/02/09/Native_Load_2023.zip, https://www.ercot.com/files/docs/2024/02/06/Native_Load_2024.zip, https://www.ercot.com/files/docs/2025/02/11/Native_Load_2025.zip, https://www.ercot.com/files/docs/2026/02/10/Native_Load_2026.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T01:43:07Z, 2026-10-07T01:43:12Z, 2026-10-07T01:43:18Z, 2026-10-07T01:43:23Z, 2026-10-07T01:43:28Z, 2026-10-07T01:43:33Z, 2026-10-07T01:43:38Z, 2026-10-07T01:43:43Z, 2026-10-07T01:43:49Z, 2026-10-07T01:43:54Z, 2026-10-07T01:43:59Z, 2026-11-16T11:50:31Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The publish time of ERCOT's yearly file | none | utc time | 2021-11-13T17:29:09Z, 2021-11-13T17:30:35Z, 2021-11-13T17:31:05Z, 2021-11-13T17:31:54Z, 2021-11-13T17:32:35Z, 2021-11-13T17:34:44Z, 2022-01-07T22:39:00Z, 2023-01-31T16:39:00Z, 2024-01-08T19:15:00Z, 2025-01-10T16:32:00Z, 2026-02-04T22:35:00Z, 2026-11-06T19:50:00Z | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `load` | ERCOT's native load for the weather zone (or the system) and hour, MW over the hour | MW | 933534 | 2015-01-01T06:00:00Z | 2026-11-01T04:00:00Z |

### `ercot_zone_prices_history`

ERCOT's settlement point price at one load zone for one interval of one operating year from 2015, day-ahead (hourly, eight load zones) or real-time (15-minute, the four competitive load zones).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2497536.

- **Time:** ts_utc is the interval start in UTC; the year is ERCOT's operating year in Central time. The hour the clocks repeat in autumn is two distinct UTC hours.
- **Revisions:** Merged by (entity, variable, ts_utc); ERCOT posts the current year's workbook again each week, and a later copy replaces that year's rows. vintage is ERCOT's document publish time.
- **Source:** ERCOT NP4-180-ER Historical DAM Load Zone and Hub Prices (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-180-ER)
- **Source:** ERCOT NP6-785-ER Historical RTM Load Zone and Hub Prices (https://www.ercot.com/mp/data-products/data-product-details?id=NP6-785-ER)
- **Method note:** [`docs/methods/ercot_zone_prices_history.md`](../methods/ercot_zone_prices_history.md)
- **Cite as:** Electric Reliability Council of Texas (ERCOT). Historical DAM Load Zone and Hub Prices; Historical RTM Load Zone and Hub Prices. Via the Energy Research Warehouse (ERW), table `ercot_zone_prices_history`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ercot:<load zone> | none | text | ercot:LZ_AEN, ercot:LZ_CPS, ercot:LZ_HOUSTON, ercot:LZ_LCRA, ercot:LZ_NORTH, ercot:LZ_RAYBN, ercot:LZ_SOUTH, ercot:LZ_WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T06:00:00Z to 2026-11-15T05:45:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -147.45 to 9349.19; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT15M, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: ercot_dam (hourly) or ercot_rtm (15-minute) | none | text | ercot_dam, ercot_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: ERCOT's load zone: LZ_HOUSTON, LZ_NORTH, LZ_SOUTH, LZ_WEST (both markets) and LZ_AEN, LZ_CPS, LZ_LCRA, LZ_RAYBN (day-ahead only) | none | text | LZ_AEN, LZ_CPS, LZ_HOUSTON, LZ_LCRA, LZ_NORTH, LZ_RAYBN, LZ_SOUTH, LZ_WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ercot:NP4-180-ER, ercot:NP6-785-ER | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1065468714, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1065471230, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1177667469, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1177737535, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1298953847, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1298966804, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=505281022, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=505283161, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=547013266, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=547016749, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=592990685, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=592992943, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=642564845, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=642564849, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=694281912, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=694284436, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=751351545, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=751356439, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=814918746, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=814922832, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=886627599, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=886632075, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=969803138, https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=969805139 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T09:15:51Z, 2026-10-07T09:16:03Z, 2026-10-07T09:17:32Z, 2026-10-07T09:17:38Z, 2026-10-07T09:17:44Z, 2026-10-07T09:17:50Z, 2026-10-07T09:17:56Z, 2026-10-07T09:18:02Z, 2026-10-07T09:18:08Z, 2026-10-07T09:18:15Z, 2026-10-07T09:18:21Z, 2026-10-07T09:18:27Z, 2026-10-07T09:18:44Z, 2026-10-07T09:18:51Z, 2026-10-07T09:18:58Z, 2026-10-07T09:19:06Z, 2026-10-07T09:19:12Z, 2026-10-07T09:19:19Z, 2026-10-07T09:19:26Z, 2026-10-07T09:19:32Z, 2026-10-07T09:19:39Z, 2026-10-07T09:19:45Z, 2026-11-15T18:09:45Z, 2026-11-15T18:09:58Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: ERCOT's publish time of the yearly workbook | none | utc time | 2016-01-01T14:03:08Z, 2016-01-01T14:21:39Z, 2017-01-01T14:03:36Z, 2017-01-01T14:33:00Z, 2018-01-01T14:02:53Z, 2018-01-01T14:24:25Z, 2019-01-01T14:02:39Z, 2019-01-01T14:25:24Z, 2020-01-01T14:03:19Z, 2020-01-01T14:25:15Z, 2021-01-01T14:08:09Z, 2021-01-01T14:41:25Z, 2022-01-01T14:13:33Z, 2022-01-01T14:38:17Z, 2023-01-01T14:11:13Z, 2023-01-01T14:34:04Z, 2024-01-01T14:10:11Z, 2024-01-01T14:19:08Z, 2025-01-01T14:07:33Z, 2025-01-01T14:18:28Z, 2026-01-01T14:44:09Z, 2026-01-01T19:25:58Z, 2026-11-15T14:01:47Z, 2026-11-15T14:38:34Z | 0 |
| `year` | The operating year a history table was published by. Here: ERCOT's operating year in Central time | none | integer | 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `spp_dam` | ERCOT's day-ahead settlement point price at the load zone, hourly (spp here is ERCOT's 'settlement point price', not the grid SPP) | USD/MWh | 832512 | 2015-01-01T06:00:00Z | 2026-11-15T05:00:00Z |
| `spp_rtm` | ERCOT's real-time settlement point price at the load zone, 15-minute (spp here is ERCOT's 'settlement point price', not the grid SPP) | USD/MWh | 1665024 | 2015-01-01T06:00:00Z | 2026-11-15T05:45:00Z |

