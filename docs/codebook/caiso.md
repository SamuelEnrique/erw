# Codebook: caiso

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 15 public tables (1 entities, 1 events, 13 series; tiers: 2 derived, 13 source); 15 documented in full.

- [`caiso_area_load_hourly`](#caiso_area_load_hourly): CAISO's actual load in one of its TAC areas (transmission access charge areas), or the ISO's own total, for one hour.
- [`caiso_as_prices`](#caiso_as_prices): CAISO's day-ahead clearing price of one ancillary service (regulation or a reserve) in one of its two system regions for one trading hour.
- [`caiso_battery_storage`](#caiso_battery_storage): The output of the batteries on CAISO's grid (all, standalone or hybrid) over one 5-minute interval, from CAISO's Today's Outlook.
- [`caiso_curtailment_daily`](#caiso_curtailment_daily): CAISO's wind or solar curtailment (all, or by reason) or wind or solar output for one Pacific day.
- [`caiso_curtailment_intervals`](#caiso_curtailment_intervals): CAISO's wind or solar curtailment at the finest interval CAISO publishes (5 minutes to 2025, an hour from 2026), by reason where published, or the day's total.
- [`caiso_curtailment_profile`](#caiso_curtailment_profile): One figure of CAISO's wind and solar curtailment for one Pacific month (in all, by reason, by category, by local hour) or, where battery output is held, of curtailment against battery charging.
- [`caiso_dam_alert_day_hub_prices`](#caiso_dam_alert_day_hub_prices): CAISO's day-ahead locational marginal price at the NP15 or SP15 trading hub for one hour of an alert or emergency day, or of a comparison day of the Flex Alert scorecard.
- [`caiso_dam_cleared_energy`](#caiso_dam_cleared_energy): The ISO's total demand cleared in CAISO's day-ahead market for one hour.
- [`caiso_fuel_supply`](#caiso_fuel_supply): CAISO's supply from one fuel source (or imports) over one hour, from Today's Outlook.
- [`caiso_fuel_supply_history`](#caiso_fuel_supply_history): CAISO's supply from one fuel source (or imports) over one hour, from Today's Outlook history files, June 2018 to May 2025.
- [`caiso_grid_emergencies`](#caiso_grid_emergencies): One CAISO grid emergency notice (Flex Alert, Restricted Maintenance Operations, Energy Emergency Alert, stage emergency, transmission emergency and others) for one region, time frame and local day it covered.
- [`caiso_interconnection_queue`](#caiso_interconnection_queue): One position in CAISO's Public Queue Report, a project asking to connect generation or storage to CAISO's grid.
- [`caiso_outlook_demand`](#caiso_outlook_demand): CAISO's demand, or one of its two demand forecasts, for one 5-minute interval of a Pacific day asked (the Flex Alert days of 2018 to 2024), from Today's Outlook.
- [`caiso_reliability_daily`](#caiso_reliability_daily): One measure of how tight CAISO's grid was on one Pacific day (demand peak and evening ramp, battery output at the evening peak, notices issued).
- [`caiso_wind_solar_forecast`](#caiso_wind_solar_forecast): CAISO's wind or solar output at one trading hub for one hour, the day-ahead forecast or the actual.

### `caiso_area_load_hourly`

CAISO's actual load in one of its TAC areas (transmission access charge areas), or the ISO's own total, for one hour.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 271644.

- **Time:** ts_utc is the hour's start in UTC; the interval's start and end are CAISO's, in GMT.
- **Revisions:** Merged by (entity, variable, ts_utc); a 30-day window ending in the last 35 days is asked of CAISO again each run and replaces the hours held, an earlier window is read from the raw file kept, and hours no longer asked are kept. vintage is not filled.
- **Source:** caiso:SLD_FCST California ISO (CAISO), OASIS SLD_FCST, CAISO Demand Forecast, the actual run (Total Actual Hourly Integrated Load), by TAC area (https://oasis.caiso.com/mrioasis/logon.do)
- **Method note:** [`docs/methods/caiso_area_load_hourly.md`](../methods/caiso_area_load_hourly.md)
- **Cite as:** California ISO (CAISO). OASIS SLD_FCST, CAISO Demand Forecast, the actual run (Total Actual Hourly Integrated Load), by TAC area [terms: materials "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO when using such materials and/or information." (https://www.caiso.com/privacy-terms-of-use, read 6 October 2026)]. Via the Energy Research Warehouse (ERW), table `caiso_area_load_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: caiso:<TAC area> under CAISO's own names (PGE-TAC, SCE-TAC, SDGE-TAC, VEA-TAC, MWD-TAC), or caiso:system for the area CAISO names CA ISO-TAC, its own total | none | text | caiso:MWD-TAC, caiso:PGE-TAC, caiso:SCE-TAC, caiso:SDGE-TAC, caiso:VEA-TAC, caiso:system | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2021-09-17T00:00:00Z to 2026-11-16T10:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -80.0 to 51292.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: caiso_load in every row | none | text | caiso_load | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The TAC area as CAISO names it (CA ISO-TAC for the total); a TAC area is not a trading hub (NP15, SP15, ZP26) | none | text | CA ISO-TAC, MWD-TAC, PGE-TAC, SCE-TAC, SDGE-TAC, VEA-TAC | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:SLD_FCST | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://oasis.caiso.com/oasisapi/SingleZip?queryname=SLD_FCST&market_run_id=ACTUAL&tac_area_name=CA%20ISO-TAC,PGE-TAC,SCE-TAC,SDGE-TAC,VEA-TAC,MWD-TAC&startdatetime=20210917T00:00-0000&enddatetime=20211017T00:00-0000&version=1&resultformat=6, https://oasis.caiso.com/oasisapi/SingleZip?queryname=SLD_FCST&market_run_id=ACTUAL&tac_area_name=CA%20ISO-TAC,PGE-TAC,SCE-TAC,SDGE-TAC,VEA-TAC,MWD-TAC&startdatetime=20211017T00:00-0000&enddatetime=20211116T00:00-0000&version=1&resultformat=6, https://oasis.caiso.com/oasisapi/SingleZip?queryname=SLD_FCST&market_run_id=ACTUAL&tac_area_name=CA%20ISO-TAC,PGE-TAC,SCE-TAC,SDGE-TAC,VEA-TAC,MWD-TAC&startdatetime=20211116T00:00-0000&enddatetime=20211216T00:00-0000&version=1&resultformat=6; 63 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T01:43:01Z to 2026-11-16T11:51:28Z; 63 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 271644 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `load` | CAISO's SYS_FCST_ACT_MW, Total Actual Hourly Integrated Load, for the area and hour, MW over the hour (OASIS SLD_FCST, the actual run) | MW | 271644 | 2021-09-17T00:00:00Z | 2026-11-16T10:00:00Z |

### `caiso_as_prices`

CAISO's day-ahead clearing price of one ancillary service (regulation or a reserve) in one of its two system regions for one trading hour.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 234056.

- **Time:** ts_utc is the start of the trading hour in UTC; operating days are Pacific days.
- **Revisions:** Merged by (entity, variable, ts_utc); a day already saved in the raw files is never asked again, so a later revision by CAISO of a saved day is not taken. vintage is not filled.
- **Source:** caiso:PRC_AS CAISO, OASIS AS Clearing Prices (PRC_AS), day-ahead market (DAM) (https://oasis.caiso.com/mrioasis/logon.do)
- **Method note:** [`docs/methods/caiso_as_prices.md`](../methods/caiso_as_prices.md)
- **Cite as:** California Independent System Operator (CAISO). OASIS AS Clearing Prices (PRC_AS), day-ahead market (DAM). Via the Energy Research Warehouse (ERW), table `caiso_as_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: caiso:AS_CAISO or caiso:AS_CAISO_EXP, the ancillary service region | none | text | caiso:AS_CAISO, caiso:AS_CAISO_EXP | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-07-14T07:00:00Z to 2026-11-17T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 1011.71778; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MW-hour | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: caiso_dam in every row: CAISO's day-ahead market | none | text | caiso_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The ancillary service region: AS_CAISO the CAISO system, AS_CAISO_EXP the system with the interties; the sub-regions are not pulled | none | text | AS_CAISO, AS_CAISO_EXP | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:PRC_AS | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://oasis.caiso.com/oasisapi/GroupZip?groupid=DAM_PRC_AS_GRP&startdatetime=20230714T07:00-0000&resultformat=6&version=12, https://oasis.caiso.com/oasisapi/GroupZip?groupid=DAM_PRC_AS_GRP&startdatetime=20230715T07:00-0000&resultformat=6&version=12, https://oasis.caiso.com/oasisapi/GroupZip?groupid=DAM_PRC_AS_GRP&startdatetime=20230716T07:00-0000&resultformat=6&version=12; 1219 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T15:22:15Z to 2026-11-16T15:04:43Z; 1219 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 234056 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `as_price_dam_nr` | Day-ahead clearing price of non-spinning reserve (CAISO's Non-Spinning Reserve), USD per MW held for one hour | USD/MW-hour | 58514 | 2023-07-14T07:00:00Z | 2026-11-17T07:00:00Z |
| `as_price_dam_rd` | Day-ahead clearing price of regulation down (CAISO's Regulation Down), USD per MW held for one hour | USD/MW-hour | 58514 | 2023-07-14T07:00:00Z | 2026-11-17T07:00:00Z |
| `as_price_dam_ru` | Day-ahead clearing price of regulation up (CAISO's Regulation Up), USD per MW held for one hour | USD/MW-hour | 58514 | 2023-07-14T07:00:00Z | 2026-11-17T07:00:00Z |
| `as_price_dam_sr` | Day-ahead clearing price of spinning reserve (CAISO's Spinning Reserve), USD per MW held for one hour | USD/MW-hour | 58514 | 2023-07-14T07:00:00Z | 2026-11-17T07:00:00Z |

### `caiso_battery_storage`

The output of the batteries on CAISO's grid (all, standalone or hybrid) over one 5-minute interval, from CAISO's Today's Outlook.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 386172.

- **Time:** ts_utc is the start of the 5-minute interval in UTC; days are Pacific days.
- **Revisions:** Merged by (entity, variable, ts_utc); each run asks again for the last 30 complete Pacific days, so an interval read again replaces the held one and older intervals are kept. vintage is not filled.
- **Source:** caiso:todays_outlook_storage California ISO, Today's Outlook, storage history files ( (https://www.caiso.com/outlook/history/YYYYMMDD/storage.csv)
- **Method note:** [`docs/methods/caiso_battery_storage.md`](../methods/caiso_battery_storage.md)
- **Cite as:** California ISO (CAISO). Today's Outlook: batteries trend (storage.csv history). Via the Energy Research Warehouse (ERW), table `caiso_battery_storage`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: caiso:ISO in every row: CAISO's whole system | none | text | caiso:ISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-08-24T07:00:00Z to 2026-11-16T07:55:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -11838.0 to 13441.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT5M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 386172 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 386172 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:todays_outlook_storage | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.caiso.com/outlook/history/20250824/storage.csv, https://www.caiso.com/outlook/history/20250825/storage.csv, https://www.caiso.com/outlook/history/20250826/storage.csv; 447 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-28T08:35:35Z to 2026-11-16T13:55:46Z; 120 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 386172 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `batteries_mw` | Output of all batteries (CAISO's Total batteries), MW: positive is discharge to the grid, negative is charging | MW | 128724 | 2025-08-24T07:00:00Z | 2026-11-16T07:55:00Z |
| `hybrid_batteries_mw` | Output of hybrid batteries, the other part of the total as CAISO publishes them, MW (positive discharge) | MW | 128724 | 2025-08-24T07:00:00Z | 2026-11-16T07:55:00Z |
| `standalone_batteries_mw` | Output of standalone batteries, one of the two parts of the total as CAISO publishes them, MW (positive discharge) | MW | 128724 | 2025-08-24T07:00:00Z | 2026-11-16T07:55:00Z |

### `caiso_curtailment_daily`

CAISO's wind or solar curtailment (all, or by reason) or wind or solar output for one Pacific day.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 25308.

- **Time:** ts_utc is the local (Pacific) operating day at 00:00:00Z.
- **Revisions:** Merged by (entity, variable, ts_utc); a daily run re-reads the reports of the last 14 days, so a day read again replaces its rows and the rest is kept. vintage is not filled.
- **Source:** caiso:production_curtailments Production and curtailments data (5-minute), https://www.caiso.com/library/production-curtailments-data (days before 2026-01-01) (https://www.caiso.com/library/production-curtailments-data)
- **Source:** caiso:daily_renewable_report Daily Renewable Report (curtailment and output), https://www.caiso.com/library/daily-renewable-reports (days from 2026-01-01) (https://www.caiso.com/library/daily-renewable-reports)
- **Method note:** [`docs/methods/caiso_curtailment_daily.md`](../methods/caiso_curtailment_daily.md)
- **Cite as:** California ISO (CAISO). Daily Renewable Report (curtailment and output); Production and curtailments data (5-minute). Via the Energy Research Warehouse (ERW), table `caiso_curtailment_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: caiso:ISO in every row: CAISO's whole system | none | text | caiso:ISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2014-05-01T00:00:00Z to 2026-11-14T00:00:00Z; 4581 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 234439.18; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 25308 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 25308 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD). Here: caiso:production_curtailments for days before 2026-01-01, caiso:daily_renewable_report from 2026-01-01 | none | text | caiso:daily_renewable_report, caiso:production_curtailments | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.caiso.com/documents/daily-renewable-report-apr-01-2026.html, https://www.caiso.com/documents/daily-renewable-report-apr-02-2026.html, https://www.caiso.com/documents/daily-renewable-report-apr-03-2026.html; 329 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-27T09:23:46Z to 2026-11-16T14:49:48Z; 33 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 25308 |

Variables (8):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `curtailed_solar_local_mwh` | Solar energy curtailed to relieve local congestion (CAISO's reason Local, published from 2022), MWh | MWh | 1779 | 2022-01-01T00:00:00Z | 2026-11-14T00:00:00Z |
| `curtailed_solar_mwh` | Solar energy CAISO curtailed in the day, all reasons, MWh | MWh | 4580 | 2014-05-02T00:00:00Z | 2026-11-14T00:00:00Z |
| `curtailed_solar_system_mwh` | Solar energy curtailed for system-wide oversupply (CAISO's reason System, published from 2022), MWh | MWh | 1779 | 2022-01-01T00:00:00Z | 2026-11-14T00:00:00Z |
| `curtailed_wind_local_mwh` | Wind energy curtailed to relieve local congestion (CAISO's reason Local, published from 2022), MWh | MWh | 1779 | 2022-01-01T00:00:00Z | 2026-11-14T00:00:00Z |
| `curtailed_wind_mwh` | Wind energy CAISO curtailed in the day, all reasons, MWh | MWh | 4580 | 2014-05-02T00:00:00Z | 2026-11-14T00:00:00Z |
| `curtailed_wind_system_mwh` | Wind energy curtailed for system-wide oversupply (CAISO's reason System, published from 2022), MWh | MWh | 1779 | 2022-01-01T00:00:00Z | 2026-11-14T00:00:00Z |
| `solar_generation_mwh` | CAISO's solar output in the day, MWh; curtailed energy is not in it | MWh | 4516 | 2014-05-01T00:00:00Z | 2026-11-14T00:00:00Z |
| `wind_generation_mwh` | CAISO's wind output in the day, MWh; curtailed energy is not in it | MWh | 4516 | 2014-05-01T00:00:00Z | 2026-11-14T00:00:00Z |

### `caiso_curtailment_intervals`

CAISO's wind or solar curtailment at the finest interval CAISO publishes (5 minutes to 2025, an hour from 2026), by reason where published, or the day's total.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 486469.

- **Time:** ts_utc is the interval's start in UTC; a day row's ts_utc is the Pacific day at 00:00:00Z. Only intervals with a curtailment above zero are written; every day covered has a day row, zero included.
- **Revisions:** Merged by (entity, variable, ts_utc); a run that asks no workbook keeps the rows of 2019 to 2025 the table holds. vintage is the yearly workbook's last-modified time; empty on the rows from the daily reports.
- **Source:** caiso:production_curtailments California ISO, Production and curtailments data (5-minute), https://www.caiso.com/library/production-curtailments-data; 0 workbooks (https://www.caiso.com/library/production-curtailments-data)
- **Source:** caiso:daily_renewable_report California ISO, Daily Renewable Report, https://www.caiso.com/library/daily-renewable-reports; 305 daily reports (0 not written) (https://www.caiso.com/library/daily-renewable-reports)
- **Method note:** [`docs/methods/caiso_curtailment_intervals.md`](../methods/caiso_curtailment_intervals.md)
- **Cite as:** California ISO (CAISO). Daily Renewable Report (curtailment and output); Production and curtailments data (5-minute). Via the Energy Research Warehouse (ERW), table `caiso_curtailment_intervals`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: caiso:ISO in every row: CAISO's whole system; the data does not locate a curtailment | none | text | caiso:ISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-11-02T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 98685.462; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh | 0 |
| `freq` | How long the interval of the row is. Here: PT5M for the 5-minute rows (MW, to 2025-12-31), PT1H for the hourly rows (MWh, from 2026-01-01), P1D for the day totals | none | text | P1D, PT1H, PT5M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 486469 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 486469 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD). Here: caiso:production_curtailments (yearly workbooks, to 2025) or caiso:daily_renewable_report (from 2026) | none | text | caiso:daily_renewable_report, caiso:production_curtailments | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.caiso.com/documents/daily-renewable-report-apr-01-2026.html, https://www.caiso.com/documents/daily-renewable-report-apr-02-2026.html, https://www.caiso.com/documents/daily-renewable-report-apr-03-2026.html; 313 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-04T10:35:56Z to 2026-11-03T17:30:05Z; 164 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time (UTC); empty on the rows from the Daily Renewable Report | none | utc time | 2024-05-16T08:33:39Z, 2024-05-28T05:43:35Z, 2024-05-28T05:43:36Z, 2024-05-28T05:43:40Z, 2024-05-28T05:43:41Z, 2025-01-22T19:26:14Z, 2026-01-07T18:50:30Z, 2026-02-13T23:52:51Z | 18189 |

Variables (20):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `curtailed_solar_day_mwh` | Solar curtailed in the Pacific day, MWh; one row for every day covered, zero included | MWh | 2862 | 2019-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `curtailed_solar_econ_local_mwh` | Solar curtailed in the hour by market dispatch of economic bids to relieve local congestion (CAISO's Economic - Local), MWh | MWh | 3939 | 2026-01-01T15:00:00Z | 2026-11-02T00:00:00Z |
| `curtailed_solar_econ_system_mwh` | Solar curtailed in the hour by market dispatch of economic bids for system-wide oversupply (CAISO's Economic - System), MWh | MWh | 4109 | 2026-01-01T14:00:00Z | 2026-11-02T00:00:00Z |
| `curtailed_solar_local_mw` | Solar curtailed in the 5-minute interval for local congestion (CAISO's reason Local), MW | MW | 145884 | 2022-04-01T14:15:00Z | 2025-12-31T23:45:00Z |
| `curtailed_solar_mw` | Solar curtailed in the 5-minute interval, no reason published, MW (the interval's average) | MW | 132082 | 2019-01-01T16:45:00Z | 2022-04-01T01:15:00Z |
| `curtailed_solar_oi_local_mwh` | Solar curtailed in the hour by operator instruction to relieve local congestion (CAISO's Operator Instruction - Local), MWh | MWh | 396 | 2026-01-26T21:00:00Z | 2026-10-23T23:00:00Z |
| `curtailed_solar_oi_system_mwh` | Solar curtailed in the hour by operator instruction for system-wide oversupply (CAISO's Operator Instruction - System), MWh | MWh | 70 | 2026-01-26T21:00:00Z | 2026-10-22T22:00:00Z |
| `curtailed_solar_ss_local_mwh` | Solar curtailed in the hour by market dispatch of self-schedules to relieve local congestion (CAISO's SelfSchCut - Local), MWh | MWh | 1562 | 2026-01-01T23:00:00Z | 2026-11-01T23:00:00Z |
| `curtailed_solar_ss_system_mwh` | Solar curtailed in the hour by market dispatch of self-schedules for system-wide oversupply (CAISO's SelfSchCut - System), MWh | MWh | 221 | 2026-01-02T22:00:00Z | 2026-11-01T23:00:00Z |
| `curtailed_solar_system_mw` | Solar curtailed in the 5-minute interval for system-wide oversupply (CAISO's reason System), MW | MW | 38753 | 2022-04-01T15:00:00Z | 2026-01-01T00:15:00Z |
| `curtailed_wind_day_mwh` | Wind curtailed in the Pacific day, MWh; one row for every day covered, zero included | MWh | 2862 | 2019-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `curtailed_wind_econ_local_mwh` | Wind curtailed in the hour by market dispatch of economic bids to relieve local congestion (CAISO's Economic - Local), MWh | MWh | 3842 | 2026-01-01T08:00:00Z | 2026-11-02T07:00:00Z |
| `curtailed_wind_econ_system_mwh` | Wind curtailed in the hour by market dispatch of economic bids for system-wide oversupply (CAISO's Economic - System), MWh | MWh | 3241 | 2026-01-01T08:00:00Z | 2026-11-02T07:00:00Z |
| `curtailed_wind_local_mw` | Wind curtailed in the 5-minute interval for local congestion (CAISO's reason Local), MW | MW | 79412 | 2022-04-01T15:35:00Z | 2025-12-31T23:05:00Z |
| `curtailed_wind_mw` | Wind curtailed in the 5-minute interval, no reason published, MW (the interval's average) | MW | 46655 | 2019-01-01T16:45:00Z | 2022-04-01T00:05:00Z |
| `curtailed_wind_oi_local_mwh` | Wind curtailed in the hour by operator instruction to relieve local congestion (CAISO's Operator Instruction - Local), MWh | MWh | 97 | 2026-01-10T02:00:00Z | 2026-10-22T22:00:00Z |
| `curtailed_wind_oi_system_mwh` | Wind curtailed in the hour by operator instruction for system-wide oversupply (CAISO's Operator Instruction - System), MWh | MWh | 14 | 2026-03-01T22:00:00Z | 2026-10-22T22:00:00Z |
| `curtailed_wind_ss_local_mwh` | Wind curtailed in the hour by market dispatch of self-schedules to relieve local congestion (CAISO's SelfSchCut - Local), MWh | MWh | 69 | 2026-02-25T20:00:00Z | 2026-10-20T05:00:00Z |
| `curtailed_wind_ss_system_mwh` | Wind curtailed in the hour by market dispatch of self-schedules for system-wide oversupply (CAISO's SelfSchCut - System), MWh | MWh | 19 | 2026-03-06T17:00:00Z | 2026-08-15T13:00:00Z |
| `curtailed_wind_system_mw` | Wind curtailed in the 5-minute interval for system-wide oversupply (CAISO's reason System), MW | MW | 20380 | 2022-04-01T20:45:00Z | 2026-01-01T06:50:00Z |

### `caiso_curtailment_profile`

One figure of CAISO's wind and solar curtailment for one Pacific month (in all, by reason, by category, by local hour) or, where battery output is held, of curtailment against battery charging.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 6240.

- **Time:** ts_utc is the first day of the Pacific month at 00:00:00Z; a month is written when at least 90 percent of its days are held, its figures summed over the days held, never scaled up.
- **Revisions:** Rebuilt whole from caiso_curtailment_intervals and caiso_battery_storage by each run of the builder; vintage is not filled.
- **Source:** erw:caiso_curtailment_profile from California ISO, Production and curtailments data and the Daily Renewable Report (curtailment), and Today's Outlook (batteries)
- **Method note:** [`docs/methods/caiso_curtailment_intervals.md`](../methods/caiso_curtailment_intervals.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. CAISO curtailment by hour, month and reason, against battery charging (docs/methods/caiso_curtailment_intervals.md). Via the Energy Research Warehouse (ERW), table `caiso_curtailment_profile`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: caiso:ISO in every row: one figure for CAISO's whole system | none | text | caiso:ISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-10-01T00:00:00Z; 94 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 1729843.0; 3528 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 6240 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 6240 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:caiso_curtailment_profile | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/caiso_curtailment_intervals.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T18:25:58Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 6240 |

Variables (116):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `avg_battery_charging_mw_h00` | Battery charging (as a positive number) on the average battery day, local hour 00, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h01` | Battery charging (as a positive number) on the average battery day, local hour 01, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h02` | Battery charging (as a positive number) on the average battery day, local hour 02, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h03` | Battery charging (as a positive number) on the average battery day, local hour 03, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h04` | Battery charging (as a positive number) on the average battery day, local hour 04, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h05` | Battery charging (as a positive number) on the average battery day, local hour 05, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h06` | Battery charging (as a positive number) on the average battery day, local hour 06, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h07` | Battery charging (as a positive number) on the average battery day, local hour 07, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h08` | Battery charging (as a positive number) on the average battery day, local hour 08, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h09` | Battery charging (as a positive number) on the average battery day, local hour 09, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h10` | Battery charging (as a positive number) on the average battery day, local hour 10, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h11` | Battery charging (as a positive number) on the average battery day, local hour 11, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h12` | Battery charging (as a positive number) on the average battery day, local hour 12, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h13` | Battery charging (as a positive number) on the average battery day, local hour 13, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h14` | Battery charging (as a positive number) on the average battery day, local hour 14, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h15` | Battery charging (as a positive number) on the average battery day, local hour 15, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h16` | Battery charging (as a positive number) on the average battery day, local hour 16, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h17` | Battery charging (as a positive number) on the average battery day, local hour 17, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h18` | Battery charging (as a positive number) on the average battery day, local hour 18, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h19` | Battery charging (as a positive number) on the average battery day, local hour 19, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h20` | Battery charging (as a positive number) on the average battery day, local hour 20, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h21` | Battery charging (as a positive number) on the average battery day, local hour 21, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h22` | Battery charging (as a positive number) on the average battery day, local hour 22, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h23` | Battery charging (as a positive number) on the average battery day, local hour 23, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h00` | Wind and solar curtailed on the average battery day, local hour 00, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h01` | Wind and solar curtailed on the average battery day, local hour 01, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h02` | Wind and solar curtailed on the average battery day, local hour 02, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h03` | Wind and solar curtailed on the average battery day, local hour 03, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h04` | Wind and solar curtailed on the average battery day, local hour 04, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h05` | Wind and solar curtailed on the average battery day, local hour 05, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h06` | Wind and solar curtailed on the average battery day, local hour 06, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h07` | Wind and solar curtailed on the average battery day, local hour 07, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h08` | Wind and solar curtailed on the average battery day, local hour 08, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h09` | Wind and solar curtailed on the average battery day, local hour 09, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h10` | Wind and solar curtailed on the average battery day, local hour 10, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h11` | Wind and solar curtailed on the average battery day, local hour 11, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h12` | Wind and solar curtailed on the average battery day, local hour 12, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h13` | Wind and solar curtailed on the average battery day, local hour 13, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h14` | Wind and solar curtailed on the average battery day, local hour 14, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h15` | Wind and solar curtailed on the average battery day, local hour 15, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h16` | Wind and solar curtailed on the average battery day, local hour 16, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h17` | Wind and solar curtailed on the average battery day, local hour 17, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h18` | Wind and solar curtailed on the average battery day, local hour 18, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h19` | Wind and solar curtailed on the average battery day, local hour 19, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h20` | Wind and solar curtailed on the average battery day, local hour 20, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h21` | Wind and solar curtailed on the average battery day, local hour 21, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h22` | Wind and solar curtailed on the average battery day, local hour 22, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h23` | Wind and solar curtailed on the average battery day, local hour 23, MW | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_charging_mwh` | What the batteries took in (charging, as a positive number) over the battery days, MWh | MWh | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_days_held` | The days both the curtailment input and caiso_battery_storage hold | count | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_mwh_battery_days` | Wind and solar curtailed over the battery days, MWh | MWh | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_econ_mwh` | Solar curtailed by market dispatch of economic bids (CAISO's category Economic, from 2026), MWh | MWh | 10 | 2026-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_local_mwh` | Solar curtailed for local congestion (CAISO's reason Local), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh` | Solar energy curtailed over the days held, MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h00` | Solar curtailed in the month in local hour 00 (00:00 to 01:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h01` | Solar curtailed in the month in local hour 01 (01:00 to 02:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h02` | Solar curtailed in the month in local hour 02 (02:00 to 03:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h03` | Solar curtailed in the month in local hour 03 (03:00 to 04:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h04` | Solar curtailed in the month in local hour 04 (04:00 to 05:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h05` | Solar curtailed in the month in local hour 05 (05:00 to 06:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h06` | Solar curtailed in the month in local hour 06 (06:00 to 07:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h07` | Solar curtailed in the month in local hour 07 (07:00 to 08:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h08` | Solar curtailed in the month in local hour 08 (08:00 to 09:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h09` | Solar curtailed in the month in local hour 09 (09:00 to 10:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h10` | Solar curtailed in the month in local hour 10 (10:00 to 11:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h11` | Solar curtailed in the month in local hour 11 (11:00 to 12:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h12` | Solar curtailed in the month in local hour 12 (12:00 to 13:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h13` | Solar curtailed in the month in local hour 13 (13:00 to 14:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h14` | Solar curtailed in the month in local hour 14 (14:00 to 15:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h15` | Solar curtailed in the month in local hour 15 (15:00 to 16:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h16` | Solar curtailed in the month in local hour 16 (16:00 to 17:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h17` | Solar curtailed in the month in local hour 17 (17:00 to 18:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h18` | Solar curtailed in the month in local hour 18 (18:00 to 19:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h19` | Solar curtailed in the month in local hour 19 (19:00 to 20:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h20` | Solar curtailed in the month in local hour 20 (20:00 to 21:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h21` | Solar curtailed in the month in local hour 21 (21:00 to 22:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h22` | Solar curtailed in the month in local hour 22 (22:00 to 23:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h23` | Solar curtailed in the month in local hour 23 (23:00 to 24:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_oi_mwh` | Solar curtailed by operator instruction (CAISO's category Operator Instruction, from 2026), MWh | MWh | 10 | 2026-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_ss_mwh` | Solar curtailed by market dispatch of self-schedules (CAISO's category SelfSchCut, from 2026), MWh | MWh | 10 | 2026-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_system_mwh` | Solar curtailed for system-wide oversupply (CAISO's reason System), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_unspecified_mwh` | Solar curtailed where CAISO published no reason, MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_while_charging_share_pct` | The share of the curtailed MWh in hours in which the batteries were charging on balance, percent | pct | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_econ_mwh` | Wind curtailed by market dispatch of economic bids (CAISO's category Economic, from 2026), MWh | MWh | 10 | 2026-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_local_mwh` | Wind curtailed for local congestion (CAISO's reason Local), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh` | Wind energy curtailed over the days held, MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h00` | Wind curtailed in the month in local hour 00 (00:00 to 01:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h01` | Wind curtailed in the month in local hour 01 (01:00 to 02:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h02` | Wind curtailed in the month in local hour 02 (02:00 to 03:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h03` | Wind curtailed in the month in local hour 03 (03:00 to 04:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h04` | Wind curtailed in the month in local hour 04 (04:00 to 05:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h05` | Wind curtailed in the month in local hour 05 (05:00 to 06:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h06` | Wind curtailed in the month in local hour 06 (06:00 to 07:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h07` | Wind curtailed in the month in local hour 07 (07:00 to 08:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h08` | Wind curtailed in the month in local hour 08 (08:00 to 09:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h09` | Wind curtailed in the month in local hour 09 (09:00 to 10:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h10` | Wind curtailed in the month in local hour 10 (10:00 to 11:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h11` | Wind curtailed in the month in local hour 11 (11:00 to 12:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h12` | Wind curtailed in the month in local hour 12 (12:00 to 13:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h13` | Wind curtailed in the month in local hour 13 (13:00 to 14:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h14` | Wind curtailed in the month in local hour 14 (14:00 to 15:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h15` | Wind curtailed in the month in local hour 15 (15:00 to 16:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h16` | Wind curtailed in the month in local hour 16 (16:00 to 17:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h17` | Wind curtailed in the month in local hour 17 (17:00 to 18:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h18` | Wind curtailed in the month in local hour 18 (18:00 to 19:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h19` | Wind curtailed in the month in local hour 19 (19:00 to 20:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h20` | Wind curtailed in the month in local hour 20 (20:00 to 21:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h21` | Wind curtailed in the month in local hour 21 (21:00 to 22:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h22` | Wind curtailed in the month in local hour 22 (22:00 to 23:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h23` | Wind curtailed in the month in local hour 23 (23:00 to 24:00), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_oi_mwh` | Wind curtailed by operator instruction (CAISO's category Operator Instruction, from 2026), MWh | MWh | 10 | 2026-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_ss_mwh` | Wind curtailed by market dispatch of self-schedules (CAISO's category SelfSchCut, from 2026), MWh | MWh | 10 | 2026-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_system_mwh` | Wind curtailed for system-wide oversupply (CAISO's reason System), MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_unspecified_mwh` | Wind curtailed where CAISO published no reason, MWh | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `days_held` | The days of the month the curtailment input holds | count | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `days_in_month` | The days of the month | count | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |

### `caiso_dam_alert_day_hub_prices`

CAISO's day-ahead locational marginal price at the NP15 or SP15 trading hub for one hour of an alert or emergency day, or of a comparison day of the Flex Alert scorecard.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3024.

- **Time:** ts_utc is the start of the hour in UTC; the days are Pacific days, scattered, not a window.
- **Revisions:** Merged by (entity, variable, ts_utc); a day once written is not asked again. vintage is not filled.
- **Source:** caiso:PRC_LMP OASIS Locational Marginal Prices, day-ahead market (DAM) (https://oasis.caiso.com/mrioasis/logon.do)
- **Method note:** [`docs/methods/caiso_dam_alert_day_hub_prices.md`](../methods/caiso_dam_alert_day_hub_prices.md)
- **Cite as:** California Independent System Operator (CAISO). OASIS Locational Marginal Prices, day-ahead market (DAM). Via the Energy Research Warehouse (ERW), table `caiso_dam_alert_day_hub_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: caiso:<node>, the hub's CAISO name | none | text | caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-07-14T07:00:00Z to 2025-08-25T06:00:00Z; 1512 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -45.0 to 1247.6335; 3001 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: caiso_dam in every row: CAISO's day-ahead market | none | text | caiso_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: CAISO's name of the trading hub price node: TH_NP15_GEN-APND (NP15) or TH_SP15_GEN-APND (SP15) | none | text | TH_NP15_GEN-APND, TH_SP15_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:PRC_LMP | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_LMP&version=12&market_run_id=DAM&node=TH_NP15_GEN-APND,TH_SP15_GEN-APND&startdatetime=20230714T07:00-0000&enddatetime=20230715T07:00-0000, https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_LMP&version=12&market_run_id=DAM&node=TH_NP15_GEN-APND,TH_SP15_GEN-APND&startdatetime=20230716T07:00-0000&enddatetime=20230717T07:00-0000, https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_LMP&version=12&market_run_id=DAM&node=TH_NP15_GEN-APND,TH_SP15_GEN-APND&startdatetime=20230717T07:00-0000&enddatetime=20230718T07:00-0000; 63 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T04:57:02Z to 2026-10-02T05:04:36Z; 63 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3024 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `lmp_dam` | Day-ahead locational marginal price (the price of energy at the hub in the day-ahead market), from CAISO's OASIS | USD/MWh | 3024 | 2023-07-14T07:00:00Z | 2025-08-25T06:00:00Z |

### `caiso_dam_cleared_energy`

The ISO's total demand cleared in CAISO's day-ahead market for one hour.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 10640.

- **Time:** ts_utc is the hour's start in UTC.
- **Revisions:** Merged by (entity, variable, ts_utc); a half month of this month or the last is asked of CAISO again and replaces the hours held, an earlier half is read from the raw file kept, and the table grows past the window CAISO keeps. vintage is not filled.
- **Source:** caiso:ENE_SLRS California ISO (CAISO), OASIS ENE_SLRS, Market Schedules, day-ahead market, ISO totals (https://oasis.caiso.com/mrioasis/logon.do)
- **Method note:** [`docs/methods/caiso_dam_cleared_energy.md`](../methods/caiso_dam_cleared_energy.md)
- **Cite as:** California ISO (CAISO). OASIS ENE_SLRS, Market Schedules, day-ahead market, ISO totals. Via the Energy Research Warehouse (ERW), table `caiso_dam_cleared_energy`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: caiso:system in every row: the ISO's total | none | text | caiso:system | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-09-01T00:00:00Z to 2026-11-18T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 13048.03 to 44253.94; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: caiso_dam in every row: CAISO's day-ahead market | none | text | caiso_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: ISO_TOT_LOAD_MW in every row: the data item read, not a place | none | text | ISO_TOT_LOAD_MW | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:ENE_SLRS | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://oasis.caiso.com/oasisapi/SingleZip?queryname=ENE_SLRS&market_run_id=DAM&tac_zone_name=Caiso_Totals&schedule=ALL&startdatetime=20250901T00:00-0000&enddatetime=20250916T00:00-0000&version=1&resultformat=6, https://oasis.caiso.com/oasisapi/SingleZip?queryname=ENE_SLRS&market_run_id=DAM&tac_zone_name=Caiso_Totals&schedule=ALL&startdatetime=20250916T00:00-0000&enddatetime=20251001T00:00-0000&version=1&resultformat=6, https://oasis.caiso.com/oasisapi/SingleZip?queryname=ENE_SLRS&market_run_id=DAM&tac_zone_name=Caiso_Totals&schedule=ALL&startdatetime=20251001T00:00-0000&enddatetime=20251016T00:00-0000&version=1&resultformat=6; 30 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T20:24:14Z to 2026-11-17T08:39:40Z; 30 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 10640 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dam_cleared_energy` | CAISO's ISO_TOT_LOAD_MW, the ISO's total MW cleared as demand in the day-ahead market for the hour, MW over the hour (OASIS ENE_SLRS, Market Schedules) | MW | 10640 | 2025-09-01T00:00:00Z | 2026-11-18T07:00:00Z |

### `caiso_fuel_supply`

CAISO's supply from one fuel source (or imports) over one hour, from Today's Outlook.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 165035.

- **Time:** ts_utc is the start of the hour in UTC; days are Pacific days. The value is the mean of the hour's twelve 5-minute values.
- **Revisions:** Merged by (entity, variable, ts_utc); each day is read on three consecutive runs and the last read stands. vintage is not filled.
- **Source:** caiso:todays_outlook_fuelsource California ISO, Today's Outlook, supply by fuel source history files ( (https://www.caiso.com/outlook/history/YYYYMMDD/fuelsource.csv)
- **Method note:** [`docs/methods/caiso_fuel_supply.md`](../methods/caiso_fuel_supply.md)
- **Cite as:** California ISO (CAISO). Today's Outlook: supply by fuel source (fuelsource.csv history). Via the Energy Research Warehouse (ERW), table `caiso_fuel_supply`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: caiso:ISO in every row: CAISO's whole system | none | text | caiso:ISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-06-01T07:00:00Z to 2026-11-16T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -11548.5 to 23780.4167; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 165035 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 165035 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:todays_outlook_fuelsource | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.caiso.com/outlook/history/20250601/fuelsource.csv, https://www.caiso.com/outlook/history/20250602/fuelsource.csv, https://www.caiso.com/outlook/history/20250603/fuelsource.csv; 529 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-03T09:42:30Z to 2026-11-17T08:57:09Z; 102 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 165035 |

Variables (13):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `batteries_mw` | Supply from batteries (CAISO's column Batteries), the hour's mean MW, positive discharging | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `biogas_mw` | Supply from biogas (CAISO's column Biogas), the hour's mean MW | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `biomass_mw` | Supply from biomass (CAISO's column Biomass), the hour's mean MW | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `coal_mw` | Supply from coal (CAISO's column Coal), the hour's mean MW | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `geothermal_mw` | Supply from geothermal plants (CAISO's column Geothermal), the hour's mean MW | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `imports_mw` | Imports (CAISO's column Imports), the hour's mean MW | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `large_hydro_mw` | Supply from large hydro (CAISO's column Large Hydro), the hour's mean MW | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `natural_gas_mw` | Supply from natural gas (CAISO's column Natural Gas), the hour's mean MW | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `nuclear_mw` | Supply from nuclear (CAISO's column Nuclear), the hour's mean MW | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `other_mw` | Supply from other sources (CAISO's column Other), the hour's mean MW | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `small_hydro_mw` | Supply from small hydro (CAISO's column Small hydro), the hour's mean MW | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `solar_mw` | Supply from solar (CAISO's column Solar), the hour's mean MW (also its MWh) | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `wind_mw` | Supply from wind (CAISO's column Wind), the hour's mean MW | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |

### `caiso_fuel_supply_history`

CAISO's supply from one fuel source (or imports) over one hour, from Today's Outlook history files, June 2018 to May 2025.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 782808.

- **Time:** ts_utc is the start of the hour in UTC; days are Pacific days. The value is the mean of the hour's twelve 5-minute values; a day short of any 5-minute interval is not written.
- **Revisions:** Written once by one run (6 October 2026), merged by (entity, variable, ts_utc); no schedule asks the files again. caiso_fuel_supply holds 2025-06-01 on. vintage is not filled.
- **Source:** caiso:todays_outlook_fuelsource_history California ISO, Today's Outlook, supply by fuel source history files ( (https://www.caiso.com/outlook/history/YYYYMMDD/fuelsource.csv)
- **Method note:** [`docs/methods/caiso_fuel_supply_history.md`](../methods/caiso_fuel_supply_history.md)
- **Cite as:** California ISO (CAISO). Today's Outlook: supply by fuel source (fuelsource.csv history), June 2018 to May 2025. Via the Energy Research Warehouse (ERW), table `caiso_fuel_supply_history`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: caiso:ISO in every row: CAISO's whole system | none | text | caiso:ISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-06-01T07:00:00Z to 2025-06-01T06:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -35159.6667 to 36178.6667; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 782808 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 782808 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:todays_outlook_fuelsource_history | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.caiso.com/outlook/history/20180601/fuelsource.csv, https://www.caiso.com/outlook/history/20180602/fuelsource.csv, https://www.caiso.com/outlook/history/20180603/fuelsource.csv; 2509 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T09:17:10Z to 2026-10-06T09:22:05Z; 296 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 782808 |

Variables (13):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `batteries_mw` | Supply from batteries (CAISO's column Batteries), the hour's mean MW, positive discharging | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `biogas_mw` | Supply from biogas (CAISO's column Biogas), the hour's mean MW | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `biomass_mw` | Supply from biomass (CAISO's column Biomass), the hour's mean MW | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `coal_mw` | Supply from coal (CAISO's column Coal), the hour's mean MW | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `geothermal_mw` | Supply from geothermal plants (CAISO's column Geothermal), the hour's mean MW | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `imports_mw` | Imports (CAISO's column Imports), the hour's mean MW | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `large_hydro_mw` | Supply from large hydro (CAISO's column Large Hydro), the hour's mean MW | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `natural_gas_mw` | Supply from natural gas (CAISO's column Natural Gas), the hour's mean MW | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `nuclear_mw` | Supply from nuclear (CAISO's column Nuclear), the hour's mean MW | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `other_mw` | Supply from other sources (CAISO's column Other), the hour's mean MW | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `small_hydro_mw` | Supply from small hydro (CAISO's column Small hydro), the hour's mean MW | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `solar_mw` | Supply from solar (CAISO's column Solar), the hour's mean MW (also its MWh) | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `wind_mw` | Supply from wind (CAISO's column Wind), the hour's mean MW | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |

### `caiso_grid_emergencies`

One CAISO grid emergency notice (Flex Alert, Restricted Maintenance Operations, Energy Emergency Alert, stage emergency, transmission emergency and others) for one region, time frame and local day it covered.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 1906.

- **Time:** event_date is the local (Pacific) day the notice covered; a notice of several days is one row a day, because CAISO counts days.
- **Revisions:** Rewritten whole by each run from the report's current revision, so CAISO's changes to past years are taken. The table has no retrieved_at column; the header names the run and the report's revision date.
- **Source:** caiso:grid_emergencies_history California ISO, Grid Emergencies History Report (1998 to present) (https://www.caiso.com/documents/grid-emergencies-history-report-1998-to-present.pdf)
- **Method note:** [`docs/methods/caiso_grid_emergencies.md`](../methods/caiso_grid_emergencies.md)
- **Cite as:** California Independent System Operator (CAISO). Grid Emergencies History Report (1998 to present). Via the Energy Research Warehouse (ERW), table `caiso_grid_emergencies`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: caiso_awe:<day>:<type>:<key>, the key the first 10 hex characters of a SHA-1 of the day, type, region (lower case) and time frame | none | text | for example caiso_awe:1998-05-30:alert:c7046d023c, caiso_awe:1998-07-26:alert:efb4878194, caiso_awe:1998-07-27:alert:4c4cdaae48; 1906 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 1998-05-30 to 2026-10-08; 814 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: CAISO's notice type, lower case: flex_alert (also Power Watch), rmo (Restricted Maintenance Operations, also No Touch), transmission_emergency, eea_watch, eea1 to eea3 (Energy Emergency Alerts, May 2022 on), alert, warning, stage1 to stage3, vlrp (Voluntary Load Reduction Program), load_interruption (1-Hour Probable Load Interruptions) | none | text | alert, eea1, eea2, eea3, eea_watch, flex_alert, load_interruption, rmo, stage1, stage2, stage3, transmission_emergency, vlrp, warning | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: California ISO on every row | none | text | California ISO | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 1906 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 1906 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 1906 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 1906 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: declared on every row | none | text | declared | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:grid_emergencies_history | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.caiso.com/documents/grid-emergencies-history-report-1998-to-present.pdf | 0 |
| `x_label` | The notice's name as printed in CAISO's report (Power Watch, No Touch, RMO*, EEA1 and others) | none | text | 1-hour Notification, Alert, EEA Watch, EEA1, EEA2, EEA3, Flex Alert, Generation RMO, No Touch, Power Watch, RMO, RMO*, Restricted Maintenance Operations, Stage 1, Stage 2, Stage 3, Transmission Emergency, VLRP, Warning | 0 |
| `x_region` | The region the notice covered, as printed (ISO, Southern CA, Northern CA, CAISO Grid and other spellings) | none | text | CAISO Grid, ISO, Northern CA, Northern CA Region, Southern, Southern CA, Southern CA Region | 0 |
| `x_time_frame` | The notice's time frame as printed (hours such as 0000-2359, or dates and times) | none | text | for example 0000-0956, 0000-0957, 0000-1220; 515 distinct | 878: The report gives no time frame (the day lists of 1998 to 2004) |
| `x_start` | The notice's start as printed (date and 24-hour time) | none | text | for example 2011-02-03 1201, 2011-02-04 1201, 2011-07-06 0800; 307 distinct | 1347: The report's table gives no start |
| `x_end` | The notice's end as printed (date and 24-hour time) | none | text | for example 2011-02-03 1200, 2011-02-04 1200, 2011-07-06 2000; 281 distinct | 1347: The report's table gives no end |
| `x_notice` | CAISO's notice number | none | text | for example 201802374, 202002406, 202002423; 82 distinct | 1755: The page gives none, or its table has more than one row |
| `x_issued_at` | The time the notice was issued, as printed | none | text | for example 01/17/2020 06:06, 02/04/2024 17:21:47, 02/12/2021 14:14; 73 distinct | 1768: The page gives none, or its table has more than one row |
| `x_reason` | The reason for the notice as printed, cut to 300 characters | none | text | for example (http://wwwcaisocom/Documents/SystemAlertsWarningsandEmergenciesFactSheetpdf) The California ISO has issued a Flex Alert for the CAISO Grid effective Friday, June 18, 2021. Californians are urged to conserve electricity from June 18 at 6:00 PM to June 18 at 9:00 PM to avoid power disruptions. A news, -, A shortage of natural gas triggered by extreme cold weather in much of the United States and Canada is impacting fuel supplies to Southern CA power plants and reducing electricity generation.; 261 distinct | 1330: The report gives no reason (layouts before 2011) |
| `x_layout` | Which of the report's table layouts the row was read from (records, stages, day_lists; matrix in no row) | none | text | day_lists, records, stages | 0 |
| `x_page` | The page of the report's PDF the row was read from | none | integer | 6 to 196; 189 distinct | 0 |

### `caiso_interconnection_queue`

One position in CAISO's Public Queue Report, a project asking to connect generation or storage to CAISO's grid.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 2278.

- **Time:** No time column. Dates are CAISO's, YYYY-MM-DD; vintage is the retrieval day. The table is a snapshot of the report as read on its retrieved_at.
- **Revisions:** A snapshot rewritten whole by each run (Mondays); earlier snapshots stay in the raw files and the archive.
- **Source:** caiso:interconnection_queue CAISO Public Queue Report (https://www.caiso.com/documents/publicqueuereport.xlsx)
- **Method note:** [`docs/methods/caiso_interconnection_queue.md`](../methods/caiso_interconnection_queue.md)
- **Cite as:** California Independent System Operator (CAISO). Public Queue Report. Via the Energy Research Warehouse (ERW), table `caiso_interconnection_queue`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: caiso_queue:<queue id> | none | text | for example caiso_queue:10, caiso_queue:100, caiso_queue:1000; 2278 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: project in every row | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 20 MW SOLAR PROJECT #1, 819 HANFORD SOLAR I, ACACIA; 2270 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> for any two-letter state CAISO gives, so CAISO's MX (Mexico) gives US-MX on 18 rows; empty where no state is given | none | text | US-AZ, US-CA, US-ID, US-NM, US-NV, US-WY | 22 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: Empty in every row | degree | empty | no cell holds a value | 2278 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: Empty in every row | degree | empty | no cell holds a value | 2278 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: CAISO's requested capacity as gridstatus reads it | MW | number | 0.0 to 3200.0; 535 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: active, withdrawn or completed, mapped one to one from iso_status; no suspended status | none | text | active, completed, withdrawn | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The withdrawn date of a withdrawn row, the in-service date of a completed row where given; empty on every active row | none | date | 2005-09-30 to 2026-10-06; 1057 distinct | 313 |
| `operator` | The operator or owner, as the publisher writes it. Here: Empty in every row | none | empty | no cell holds a value | 2278 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:interconnection_queue | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.caiso.com/documents/publicqueuereport.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-05T23:21:54Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The retrieval day (YYYY-MM-DD), not a date CAISO prints | none | date | 2026-11-05 | 0 |
| `queue_id` | CAISO's queue position number of the request (the source's name: Queue ID) | none | text | for example 10, 100, 1000; 2278 distinct | 0 |
| `county` | The county of the project as CAISO writes it (the source's name: County) | none | text | for example ALAMEDA, ALAMEDA COUNTY, AMADOR; 100 distinct | 5: CAISO gives no county |
| `state` | The state of the project as CAISO writes it (a two-letter code; MX for Mexico) (the source's name: State) | none | text | AZ, CA, ID, MX, NM, NV, WY | 4: CAISO gives no state |
| `poi` | The point of interconnection: the substation or line where the project would connect (the source's name: Interconnection Location) | none | text | for example 0.2 miles from Monsrate Tap  on the Monsrate Tap-Pala 69 kV line, 0.2-mile from Moro hill tap on the Moro Hill Tap - Monserate 69 kV line, 115 KV Panoche Sub; 1661 distinct | 0 |
| `zone` | The zone of the project (the source's name: Zone) | none | empty | no cell holds a value | 2278: Empty in every row: CAISO's report does not give it |
| `transmission_owner` | The transmission owner the project connects to, CAISO's code (PGAE, SCE, SDGE, GLW, VEA and others) (the source's name: Transmission Owner) | none | text | DCRT, DSLK, GLW, IID, PGAE, SCE, SDGE, VEA | 2: CAISO gives none (2 rows) |
| `fuel_technology` | The project's generation type in CAISO's words (Photovoltaic, Storage, Wind Turbine, Steam Turbine, combinations and others) (the source's name: Generation Type) | none | text | for example Cogeneration, Combined Cycle, Combined Cycle + Combined Cycle; 41 distinct | 0 |
| `iso_status` | CAISO's own status of the request (ACTIVE, WITHDRAWN, COMPLETED) (the source's name: Status) | none | text | ACTIVE, COMPLETED, WITHDRAWN | 0 |
| `queue_date` | The date the request entered the queue (the source's name: Queue Date) | none | date | 1999-11-01 to 2023-03-02; 411 distinct | 0 |
| `proposed_in_service_date` | The date the project proposes to begin operating (the source's name: Proposed Completion Date) | none | date | 2005-12-08 to 2036-05-05; 723 distinct | 257: CAISO gives no proposed date |
| `actual_in_service_date` | The date the project began operating (the source's name: Actual Completion Date (gridstatus)) | none | date | 2005-09-30 to 2026-09-14; 204 distinct | 2039: Not in service, or no date given |
| `withdrawn_date` | The date the request was withdrawn (the source's name: Withdrawn Date) | none | date | 2006-01-11 to 2026-10-06; 888 distinct | 552: Not withdrawn, or withdrawn with no date given |

### `caiso_outlook_demand`

CAISO's demand, or one of its two demand forecasts, for one 5-minute interval of a Pacific day asked (the Flex Alert days of 2018 to 2024), from Today's Outlook.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 33927.

- **Time:** ts_utc is the start of the 5-minute interval in UTC; days are Pacific days.
- **Revisions:** Merged by (entity, variable, ts_utc) into earlier runs; a day is written only when the three MW columns hold every 5-minute interval of it. vintage is not filled.
- **Source:** caiso:todays_outlook_demand California ISO, Today's Outlook, demand history files ( (https://www.caiso.com/outlook/history/YYYYMMDD/demand.csv)
- **Method note:** [`docs/methods/caiso_outlook_demand.md`](../methods/caiso_outlook_demand.md)
- **Cite as:** California ISO (CAISO). Today's Outlook: demand trend (demand.csv history). Via the Energy Research Warehouse (ERW), table `caiso_outlook_demand`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: caiso:ISO in every row: CAISO's whole system | none | text | caiso:ISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-24T07:00:00Z to 2024-07-25T06:55:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.0 to 51929.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count | 0 |
| `freq` | How long the interval of the row is | none | text | PT5M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 33927 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 33927 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:todays_outlook_demand | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.caiso.com/outlook/history/20180724/demand.csv, https://www.caiso.com/outlook/history/20180725/demand.csv, https://www.caiso.com/outlook/history/20190611/demand.csv; 39 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-17T09:23:17Z to 2026-11-17T09:24:39Z; 39 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 33927 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `demand_forecast_day_ahead_mw` | CAISO's day-ahead forecast of demand for the interval, MW | MW | 11232 | 2018-07-24T07:00:00Z | 2024-07-25T06:55:00Z |
| `demand_forecast_hour_ahead_mw` | CAISO's hour-ahead forecast of demand for the interval, MW | MW | 11232 | 2018-07-24T07:00:00Z | 2024-07-25T06:55:00Z |
| `demand_mw` | CAISO's Current demand for the interval, MW | MW | 11232 | 2018-07-24T07:00:00Z | 2024-07-25T06:55:00Z |
| `demand_response_marked` | 1 in an interval CAISO's Demand response column marks; no row where it is blank (count) | count | 231 | 2022-09-01T02:25:00Z | 2023-07-21T03:25:00Z |

### `caiso_reliability_daily`

One measure of how tight CAISO's grid was on one Pacific day (demand peak and evening ramp, battery output at the evening peak, notices issued).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 20832.

- **Time:** ts_utc is the local (Pacific) day at 00:00:00Z; a day is written only when every hour of it is held.
- **Revisions:** Rebuilt whole from caiso_battery_storage, caiso_grid_emergencies and eia930_all_demand by each run of the builder; vintage is not filled.
- **Source:** erw:caiso_reliability ERW derived table, California reliability method (docs/methods/california_reliability.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/california_reliability.md)
- **Method note:** [`docs/methods/california_reliability.md`](../methods/california_reliability.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. California reliability, how tight was it (warehouse/derived/caiso_reliability.py). Via the Energy Research Warehouse (ERW), table `caiso_reliability_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930:CISO for the demand measures (EIA-930 demand of CAISO's balancing authority), caiso:ISO for the battery and notice measures | none | text | caiso:ISO, eia930:CISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1998-05-30T00:00:00Z to 2026-11-13T00:00:00Z; 3704 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -3416.0 to 51104.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count, hour, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 20832 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 20832 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:caiso_reliability | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/california_reliability.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T17:44:49Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 20832 |

Variables (22):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `afternoon_mean_mw` | The mean demand of the hours starting 12:00, 13:00 and 14:00, MW | MW | 3025 | 2018-07-01T00:00:00Z | 2026-11-13T00:00:00Z |
| `battery_mw_evening_peak` | The batteries' mean output over the evening peak hour (its twelve 5-minute intervals), MW, positive discharge; from 2025-08-24 | MW | 438 | 2025-08-24T00:00:00Z | 2026-11-13T00:00:00Z |
| `battery_share_pct` | The batteries' output at the evening peak as a percent of the evening peak's demand | pct | 438 | 2025-08-24T00:00:00Z | 2026-11-13T00:00:00Z |
| `evening_peak_hour` | The local start of the evening peak hour, the earliest on a tie | hour | 3025 | 2018-07-01T00:00:00Z | 2026-11-13T00:00:00Z |
| `evening_peak_mw` | The highest demand of the hours starting 17:00 to 20:00, MW | MW | 3025 | 2018-07-01T00:00:00Z | 2026-11-13T00:00:00Z |
| `evening_ramp_mw` | The evening peak less the afternoon mean: the rise into the evening, MW | MW | 3025 | 2018-07-01T00:00:00Z | 2026-11-13T00:00:00Z |
| `notices_alert` | The day's CAISO notices of type alert | count | 245 | 1998-05-30T00:00:00Z | 2020-10-15T00:00:00Z |
| `notices_eea1` | The day's Energy Emergency Alert 1 notices | count | 7 | 2022-08-31T00:00:00Z | 2023-07-20T00:00:00Z |
| `notices_eea2` | The day's Energy Emergency Alert 2 notices | count | 4 | 2022-09-05T00:00:00Z | 2022-09-08T00:00:00Z |
| `notices_eea3` | The day's Energy Emergency Alert 3 notices | count | 1 | 2022-09-06T00:00:00Z | 2022-09-06T00:00:00Z |
| `notices_eea_watch` | The day's Energy Emergency Alert watch notices | count | 12 | 2022-08-31T00:00:00Z | 2024-07-24T00:00:00Z |
| `notices_flex_alert` | The day's Flex Alert notices (Power Watch included) | count | 137 | 2000-05-22T00:00:00Z | 2022-09-09T00:00:00Z |
| `notices_load_interruption` | The day's 1-Hour Probable Load Interruption notices | count | 1 | 2020-08-18T00:00:00Z | 2020-08-18T00:00:00Z |
| `notices_rmo` | The day's Restricted Maintenance Operations notices (No Touch included) | count | 689 | 1998-07-27T00:00:00Z | 2026-10-08T00:00:00Z |
| `notices_stage1` | The day's stage 1 emergency notices | count | 146 | 1998-07-27T00:00:00Z | 2017-05-03T00:00:00Z |
| `notices_stage2` | The day's stage 2 emergency notices | count | 118 | 1998-07-27T00:00:00Z | 2021-07-09T00:00:00Z |
| `notices_stage3` | The day's stage 3 emergency notices | count | 41 | 2000-12-07T00:00:00Z | 2020-08-15T00:00:00Z |
| `notices_transmission_emergency` | The day's transmission emergency notices | count | 77 | 2004-01-12T00:00:00Z | 2025-04-30T00:00:00Z |
| `notices_vlrp` | The day's Voluntary Load Reduction Program notices | count | 8 | 2004-02-03T00:00:00Z | 2006-07-25T00:00:00Z |
| `notices_warning` | The day's CAISO notices of type warning | count | 320 | 1998-07-27T00:00:00Z | 2021-07-29T00:00:00Z |
| `peak_demand_mw` | The day's highest hour of demand, MW (each hour's mean) | MW | 3025 | 2018-07-01T00:00:00Z | 2026-11-13T00:00:00Z |
| `peak_hour` | The local start (0 to 23) of the day's highest hour of demand, the earliest on a tie | hour | 3025 | 2018-07-01T00:00:00Z | 2026-11-13T00:00:00Z |

### `caiso_wind_solar_forecast`

CAISO's wind or solar output at one trading hub for one hour, the day-ahead forecast or the actual.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 352393.

- **Time:** ts_utc is the hour's start in UTC.
- **Revisions:** Merged by (entity, variable, ts_utc); every span asked is asked of CAISO again, so a revised hour replaces the one held, and hours no longer asked are kept. vintage is not filled.
- **Source:** caiso:SLD_REN_FCST California ISO, OASIS, Wind and Solar Forecast (SLD_REN_FCST) (https://oasis.caiso.com/mrioasis/logon.do)
- **Method note:** [`docs/methods/caiso_wind_solar_forecast.md`](../methods/caiso_wind_solar_forecast.md)
- **Cite as:** California ISO (CAISO). OASIS: Wind and Solar Forecast (SLD_REN_FCST), day-ahead forecast and actual generation. Via the Energy Research Warehouse (ERW), table `caiso_wind_solar_forecast`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: caiso:<trading hub>: NP15, SP15 or ZP26 | none | text | caiso:NP15, caiso:SP15, caiso:ZP26 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-06-01T07:00:00Z to 2026-11-19T06:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -307.9097 to 14948.67; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 352393 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: CAISO's trading hub: NP15, SP15 or ZP26 | none | text | NP15, SP15, ZP26 | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:SLD_REN_FCST | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=SLD_REN_FCST&version=1&market_run_id=ACTUAL&startdatetime=20230531T07:00-0000&enddatetime=20230630T07:00-0000, https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=SLD_REN_FCST&version=1&market_run_id=ACTUAL&startdatetime=20230630T07:00-0000&enddatetime=20230730T07:00-0000, https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=SLD_REN_FCST&version=1&market_run_id=ACTUAL&startdatetime=20230730T07:00-0000&enddatetime=20230829T07:00-0000; 156 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T09:35:39Z to 2026-11-19T17:40:04Z; 156 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 352393 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `solar_actual_mw` | Actual solar generation (market run ACTUAL) for the hub and hour, MW | MW | 91021 | 2023-06-01T07:00:00Z | 2026-11-19T06:00:00Z |
| `solar_forecast_dam_mw` | CAISO's day-ahead forecast of solar output (market run DAM) for the hub and hour, MW | MW | 91224 | 2023-06-01T07:00:00Z | 2026-11-19T06:00:00Z |
| `wind_actual_mw` | Actual wind generation (market run ACTUAL) for the hub and hour, MW | MW | 84973 | 2023-06-01T07:00:00Z | 2026-11-19T06:00:00Z |
| `wind_forecast_dam_mw` | CAISO's day-ahead forecast of wind output (market run DAM) for the hub and hour, MW (OASIS SLD_REN_FCST) | MW | 85175 | 2023-06-01T07:00:00Z | 2026-11-19T06:00:00Z |

