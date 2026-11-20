# Codebook: caiso

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 15 public tables (1 entities, 1 events, 13 series; tiers: 2 derived, 13 source); 0 documented in full.

- [`caiso_area_load_hourly`](#caiso_area_load_hourly): CAISO, hourly actual load by TAC area and the ISO's total (OASIS SLD_FCST, the actual run, data item SYS_FCST_ACT_MW) (session 138)
- [`caiso_as_prices`](#caiso_as_prices): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261116T155131Z-github (2026-11-16T15:51:31Z); that run's own header of the table follows
- [`caiso_battery_storage`](#caiso_battery_storage): CAISO battery storage output, 5-minute (Today's Outlook)
- [`caiso_curtailment_daily`](#caiso_curtailment_daily): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261116T155131Z-github (2026-11-16T15:51:31Z); that run's own header of the table follows
- [`caiso_curtailment_intervals`](#caiso_curtailment_intervals): CAISO wind and solar curtailment at the finest interval CAISO publishes, by reason, from 2019 (session 98)
- [`caiso_curtailment_profile`](#caiso_curtailment_profile): CAISO wind and solar curtailment by hour of the day, by month and by reason, against battery charging (session 98)
- [`caiso_dam_alert_day_hub_prices`](#caiso_dam_alert_day_hub_prices): CAISO day-ahead LMPs at the SP15 and NP15 hubs on alert and emergency days and the Flex Alert scorecard's comparison days (session 60)
- [`caiso_dam_cleared_energy`](#caiso_dam_cleared_energy): CAISO, demand cleared in the day-ahead market by hour, the ISO's total (OASIS ENE_SLRS, Market Schedules, data item ISO_TOT_LOAD_MW) (session 136)
- [`caiso_fuel_supply`](#caiso_fuel_supply): CAISO supply by fuel source, hourly (Today's Outlook)
- [`caiso_fuel_supply_history`](#caiso_fuel_supply_history): CAISO supply by fuel source, hourly (Today's Outlook), June 2018 to May 2025 (session 133)
- [`caiso_grid_emergencies`](#caiso_grid_emergencies): CAISO grid emergencies, every Flex Alert, Restricted Maintenance Operations notice, Energy Emergency Alert, stage emergency and transmission emergency in CAISO's Grid Emergencies History Report (session 58)
- [`caiso_interconnection_queue`](#caiso_interconnection_queue): Rebuilt from the ERW archive by warehouse/archive/restore.py, as of run 20261106T003628Z-github (2026-11-06T00:36:28Z); that run's own header of the table follows
- [`caiso_outlook_demand`](#caiso_outlook_demand): CAISO demand, 5-minute, on the days asked (Today's Outlook)
- [`caiso_reliability_daily`](#caiso_reliability_daily): how tight was it, CAISO's evenings day by day (derived, session 58, California reliability v1)
- [`caiso_wind_solar_forecast`](#caiso_wind_solar_forecast): CAISO wind and solar, the day-ahead forecast and the actual output, hourly, by trading hub (session 133)

### `caiso_area_load_hourly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 271644.

- **Source:** caiso:SLD_FCST California ISO (CAISO), OASIS SLD_FCST, CAISO Demand Forecast, the actual run (Total Actual Hourly Integrated Load), by TAC area (https://oasis.caiso.com/mrioasis/logon.do)
- **Method note:** [`docs/methods/caiso_area_load_hourly.md`](../methods/caiso_area_load_hourly.md)
- **Cite as:** California ISO (CAISO). OASIS SLD_FCST, CAISO Demand Forecast, the actual run (Total Actual Hourly Integrated Load), by TAC area [terms: materials "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO when using such materials and/or information." (https://www.caiso.com/privacy-terms-of-use, read 6 October 2026)]. Via the Energy Research Warehouse (ERW), table `caiso_area_load_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:MWD-TAC, caiso:PGE-TAC, caiso:SCE-TAC, caiso:SDGE-TAC, caiso:VEA-TAC, caiso:system | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2021-09-17T00:00:00Z to 2026-11-16T10:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -80.0 to 51292.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_load | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | CA ISO-TAC, MWD-TAC, PGE-TAC, SCE-TAC, SDGE-TAC, VEA-TAC | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:SLD_FCST | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://oasis.caiso.com/oasisapi/SingleZip?queryname=SLD_FCST&market_run_id=ACTUAL&tac_area_name=CA%20ISO-TAC,PGE-TAC,SCE-TAC,SDGE-TAC,VEA-TAC,MWD-TAC&startdatetime=20210917T00:00-0000&enddatetime=20211017T00:00-0000&version=1&resultformat=6, https://oasis.caiso.com/oasisapi/SingleZip?queryname=SLD_FCST&market_run_id=ACTUAL&tac_area_name=CA%20ISO-TAC,PGE-TAC,SCE-TAC,SDGE-TAC,VEA-TAC,MWD-TAC&startdatetime=20211017T00:00-0000&enddatetime=20211116T00:00-0000&version=1&resultformat=6, https://oasis.caiso.com/oasisapi/SingleZip?queryname=SLD_FCST&market_run_id=ACTUAL&tac_area_name=CA%20ISO-TAC,PGE-TAC,SCE-TAC,SDGE-TAC,VEA-TAC,MWD-TAC&startdatetime=20211116T00:00-0000&enddatetime=20211216T00:00-0000&version=1&resultformat=6; 63 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T01:43:01Z to 2026-11-16T11:51:28Z; 63 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 271644 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `load` |  | MW | 271644 | 2021-09-17T00:00:00Z | 2026-11-16T10:00:00Z |

### `caiso_as_prices`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 234056.

- **Source:** caiso:PRC_AS CAISO, OASIS AS Clearing Prices (PRC_AS), day-ahead market (DAM) (https://oasis.caiso.com/mrioasis/logon.do)
- **Method note:** [`docs/methods/caiso_as_prices.md`](../methods/caiso_as_prices.md)
- **Cite as:** California Independent System Operator (CAISO). OASIS AS Clearing Prices (PRC_AS), day-ahead market (DAM). Via the Energy Research Warehouse (ERW), table `caiso_as_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:AS_CAISO, caiso:AS_CAISO_EXP | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-07-14T07:00:00Z to 2026-11-17T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 1011.71778; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MW-hour | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | AS_CAISO, AS_CAISO_EXP | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:PRC_AS | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://oasis.caiso.com/oasisapi/GroupZip?groupid=DAM_PRC_AS_GRP&startdatetime=20230714T07:00-0000&resultformat=6&version=12, https://oasis.caiso.com/oasisapi/GroupZip?groupid=DAM_PRC_AS_GRP&startdatetime=20230715T07:00-0000&resultformat=6&version=12, https://oasis.caiso.com/oasisapi/GroupZip?groupid=DAM_PRC_AS_GRP&startdatetime=20230716T07:00-0000&resultformat=6&version=12; 1219 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T15:22:15Z to 2026-11-16T15:04:43Z; 1219 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 234056 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `as_price_dam_nr` |  | USD/MW-hour | 58514 | 2023-07-14T07:00:00Z | 2026-11-17T07:00:00Z |
| `as_price_dam_rd` |  | USD/MW-hour | 58514 | 2023-07-14T07:00:00Z | 2026-11-17T07:00:00Z |
| `as_price_dam_ru` |  | USD/MW-hour | 58514 | 2023-07-14T07:00:00Z | 2026-11-17T07:00:00Z |
| `as_price_dam_sr` |  | USD/MW-hour | 58514 | 2023-07-14T07:00:00Z | 2026-11-17T07:00:00Z |

### `caiso_battery_storage`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 386172.

- **Source:** caiso:todays_outlook_storage California ISO, Today's Outlook, storage history files ( (https://www.caiso.com/outlook/history/YYYYMMDD/storage.csv)
- **Method note:** [`docs/methods/caiso_battery_storage.md`](../methods/caiso_battery_storage.md)
- **Cite as:** California ISO (CAISO). Today's Outlook: batteries trend (storage.csv history). Via the Energy Research Warehouse (ERW), table `caiso_battery_storage`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:ISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-08-24T07:00:00Z to 2026-11-16T07:55:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -11838.0 to 13441.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT5M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 386172 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 386172 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:todays_outlook_storage | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.caiso.com/outlook/history/20250824/storage.csv, https://www.caiso.com/outlook/history/20250825/storage.csv, https://www.caiso.com/outlook/history/20250826/storage.csv; 447 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-28T08:35:35Z to 2026-11-16T13:55:46Z; 120 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 386172 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `batteries_mw` |  | MW | 128724 | 2025-08-24T07:00:00Z | 2026-11-16T07:55:00Z |
| `hybrid_batteries_mw` |  | MW | 128724 | 2025-08-24T07:00:00Z | 2026-11-16T07:55:00Z |
| `standalone_batteries_mw` |  | MW | 128724 | 2025-08-24T07:00:00Z | 2026-11-16T07:55:00Z |

### `caiso_curtailment_daily`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 25308.

- **Source:** caiso:production_curtailments Production and curtailments data (5-minute),  (days before 2026-01-01) (https://www.caiso.com/library/production-curtailments-data)
- **Source:** caiso:daily_renewable_report Daily Renewable Report (curtailment and output),  (days from 2026-01-01) (https://www.caiso.com/library/daily-renewable-reports)
- **Method note:** [`docs/methods/caiso_curtailment_daily.md`](../methods/caiso_curtailment_daily.md)
- **Cite as:** California ISO (CAISO). Daily Renewable Report (curtailment and output); Production and curtailments data (5-minute). Via the Energy Research Warehouse (ERW), table `caiso_curtailment_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:ISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2014-05-01T00:00:00Z to 2026-11-14T00:00:00Z; 4581 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 234439.18; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 25308 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 25308 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:daily_renewable_report, caiso:production_curtailments | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.caiso.com/documents/daily-renewable-report-apr-01-2026.html, https://www.caiso.com/documents/daily-renewable-report-apr-02-2026.html, https://www.caiso.com/documents/daily-renewable-report-apr-03-2026.html; 329 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-27T09:23:46Z to 2026-11-16T14:49:48Z; 33 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 25308 |

Variables (8):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `curtailed_solar_local_mwh` |  | MWh | 1779 | 2022-01-01T00:00:00Z | 2026-11-14T00:00:00Z |
| `curtailed_solar_mwh` |  | MWh | 4580 | 2014-05-02T00:00:00Z | 2026-11-14T00:00:00Z |
| `curtailed_solar_system_mwh` |  | MWh | 1779 | 2022-01-01T00:00:00Z | 2026-11-14T00:00:00Z |
| `curtailed_wind_local_mwh` |  | MWh | 1779 | 2022-01-01T00:00:00Z | 2026-11-14T00:00:00Z |
| `curtailed_wind_mwh` |  | MWh | 4580 | 2014-05-02T00:00:00Z | 2026-11-14T00:00:00Z |
| `curtailed_wind_system_mwh` |  | MWh | 1779 | 2022-01-01T00:00:00Z | 2026-11-14T00:00:00Z |
| `solar_generation_mwh` |  | MWh | 4516 | 2014-05-01T00:00:00Z | 2026-11-14T00:00:00Z |
| `wind_generation_mwh` |  | MWh | 4516 | 2014-05-01T00:00:00Z | 2026-11-14T00:00:00Z |

### `caiso_curtailment_intervals`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 486469.

- **Source:** caiso:production_curtailments California ISO, Production and curtailments data (5-minute),  0 workbooks (https://www.caiso.com/library/production-curtailments-data)
- **Source:** caiso:daily_renewable_report California ISO, Daily Renewable Report,  305 daily reports (0 not written) (https://www.caiso.com/library/daily-renewable-reports)
- **Method note:** [`docs/methods/caiso_curtailment_intervals.md`](../methods/caiso_curtailment_intervals.md)
- **Cite as:** California ISO (CAISO). Daily Renewable Report (curtailment and output); Production and curtailments data (5-minute). Via the Energy Research Warehouse (ERW), table `caiso_curtailment_intervals`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:ISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-11-02T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 98685.462; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1D, PT1H, PT5M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 486469 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 486469 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:daily_renewable_report, caiso:production_curtailments | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.caiso.com/documents/daily-renewable-report-apr-01-2026.html, https://www.caiso.com/documents/daily-renewable-report-apr-02-2026.html, https://www.caiso.com/documents/daily-renewable-report-apr-03-2026.html; 313 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-04T10:35:56Z to 2026-11-03T17:30:05Z; 164 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2024-05-16T08:33:39Z, 2024-05-28T05:43:35Z, 2024-05-28T05:43:36Z, 2024-05-28T05:43:40Z, 2024-05-28T05:43:41Z, 2025-01-22T19:26:14Z, 2026-01-07T18:50:30Z, 2026-02-13T23:52:51Z | 18189 |

Variables (20):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `curtailed_solar_day_mwh` |  | MWh | 2862 | 2019-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `curtailed_solar_econ_local_mwh` |  | MWh | 3939 | 2026-01-01T15:00:00Z | 2026-11-02T00:00:00Z |
| `curtailed_solar_econ_system_mwh` |  | MWh | 4109 | 2026-01-01T14:00:00Z | 2026-11-02T00:00:00Z |
| `curtailed_solar_local_mw` |  | MW | 145884 | 2022-04-01T14:15:00Z | 2025-12-31T23:45:00Z |
| `curtailed_solar_mw` |  | MW | 132082 | 2019-01-01T16:45:00Z | 2022-04-01T01:15:00Z |
| `curtailed_solar_oi_local_mwh` |  | MWh | 396 | 2026-01-26T21:00:00Z | 2026-10-23T23:00:00Z |
| `curtailed_solar_oi_system_mwh` |  | MWh | 70 | 2026-01-26T21:00:00Z | 2026-10-22T22:00:00Z |
| `curtailed_solar_ss_local_mwh` |  | MWh | 1562 | 2026-01-01T23:00:00Z | 2026-11-01T23:00:00Z |
| `curtailed_solar_ss_system_mwh` |  | MWh | 221 | 2026-01-02T22:00:00Z | 2026-11-01T23:00:00Z |
| `curtailed_solar_system_mw` |  | MW | 38753 | 2022-04-01T15:00:00Z | 2026-01-01T00:15:00Z |
| `curtailed_wind_day_mwh` |  | MWh | 2862 | 2019-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `curtailed_wind_econ_local_mwh` |  | MWh | 3842 | 2026-01-01T08:00:00Z | 2026-11-02T07:00:00Z |
| `curtailed_wind_econ_system_mwh` |  | MWh | 3241 | 2026-01-01T08:00:00Z | 2026-11-02T07:00:00Z |
| `curtailed_wind_local_mw` |  | MW | 79412 | 2022-04-01T15:35:00Z | 2025-12-31T23:05:00Z |
| `curtailed_wind_mw` |  | MW | 46655 | 2019-01-01T16:45:00Z | 2022-04-01T00:05:00Z |
| `curtailed_wind_oi_local_mwh` |  | MWh | 97 | 2026-01-10T02:00:00Z | 2026-10-22T22:00:00Z |
| `curtailed_wind_oi_system_mwh` |  | MWh | 14 | 2026-03-01T22:00:00Z | 2026-10-22T22:00:00Z |
| `curtailed_wind_ss_local_mwh` |  | MWh | 69 | 2026-02-25T20:00:00Z | 2026-10-20T05:00:00Z |
| `curtailed_wind_ss_system_mwh` |  | MWh | 19 | 2026-03-06T17:00:00Z | 2026-08-15T13:00:00Z |
| `curtailed_wind_system_mw` |  | MW | 20380 | 2022-04-01T20:45:00Z | 2026-01-01T06:50:00Z |

### `caiso_curtailment_profile`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 6240.

- **Source:** erw:caiso_curtailment_profile from California ISO, Production and curtailments data and the Daily Renewable Report (curtailment), and Today's Outlook (batteries)
- **Method note:** [`docs/methods/caiso_curtailment_intervals.md`](../methods/caiso_curtailment_intervals.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. CAISO curtailment by hour, month and reason, against battery charging (docs/methods/caiso_curtailment_intervals.md). Via the Energy Research Warehouse (ERW), table `caiso_curtailment_profile`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:ISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-10-01T00:00:00Z; 94 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 1729843.0; 3528 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 6240 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 6240 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:caiso_curtailment_profile | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/caiso_curtailment_intervals.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T18:25:58Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 6240 |

Variables (116):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `avg_battery_charging_mw_h00` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h01` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h02` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h03` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h04` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h05` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h06` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h07` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h08` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h09` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h10` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h11` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h12` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h13` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h14` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h15` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h16` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h17` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h18` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h19` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h20` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h21` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h22` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_battery_charging_mw_h23` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h00` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h01` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h02` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h03` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h04` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h05` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h06` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h07` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h08` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h09` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h10` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h11` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h12` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h13` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h14` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h15` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h16` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h17` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h18` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h19` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h20` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h21` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h22` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `avg_curtailed_mw_h23` |  | MW | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_charging_mwh` |  | MWh | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `battery_days_held` |  | count | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_mwh_battery_days` |  | MWh | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_econ_mwh` |  | MWh | 10 | 2026-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_local_mwh` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h00` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h01` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h02` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h03` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h04` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h05` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h06` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h07` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h08` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h09` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h10` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h11` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h12` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h13` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h14` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h15` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h16` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h17` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h18` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h19` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h20` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h21` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h22` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh_h23` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_oi_mwh` |  | MWh | 10 | 2026-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_ss_mwh` |  | MWh | 10 | 2026-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_system_mwh` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_unspecified_mwh` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_while_charging_share_pct` |  | pct | 14 | 2025-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_econ_mwh` |  | MWh | 10 | 2026-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_local_mwh` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h00` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h01` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h02` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h03` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h04` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h05` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h06` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h07` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h08` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h09` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h10` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h11` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h12` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h13` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h14` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h15` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h16` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h17` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h18` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h19` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h20` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h21` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h22` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh_h23` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_oi_mwh` |  | MWh | 10 | 2026-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_ss_mwh` |  | MWh | 10 | 2026-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_system_mwh` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_unspecified_mwh` |  | MWh | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `days_held` |  | count | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `days_in_month` |  | count | 94 | 2019-01-01T00:00:00Z | 2026-10-01T00:00:00Z |

### `caiso_dam_alert_day_hub_prices`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3024.

- **Source:** caiso:PRC_LMP OASIS Locational Marginal Prices, day-ahead market (DAM) (https://oasis.caiso.com/mrioasis/logon.do)
- **Method note:** [`docs/methods/caiso_dam_alert_day_hub_prices.md`](../methods/caiso_dam_alert_day_hub_prices.md)
- **Cite as:** California Independent System Operator (CAISO). OASIS Locational Marginal Prices, day-ahead market (DAM). Via the Energy Research Warehouse (ERW), table `caiso_dam_alert_day_hub_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-07-14T07:00:00Z to 2025-08-25T06:00:00Z; 1512 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -45.0 to 1247.6335; 3001 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | TH_NP15_GEN-APND, TH_SP15_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:PRC_LMP | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_LMP&version=12&market_run_id=DAM&node=TH_NP15_GEN-APND,TH_SP15_GEN-APND&startdatetime=20230714T07:00-0000&enddatetime=20230715T07:00-0000, https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_LMP&version=12&market_run_id=DAM&node=TH_NP15_GEN-APND,TH_SP15_GEN-APND&startdatetime=20230716T07:00-0000&enddatetime=20230717T07:00-0000, https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_LMP&version=12&market_run_id=DAM&node=TH_NP15_GEN-APND,TH_SP15_GEN-APND&startdatetime=20230717T07:00-0000&enddatetime=20230718T07:00-0000; 63 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T04:57:02Z to 2026-10-02T05:04:36Z; 63 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 3024 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `lmp_dam` |  | USD/MWh | 3024 | 2023-07-14T07:00:00Z | 2025-08-25T06:00:00Z |

### `caiso_dam_cleared_energy`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 10640.

- **Source:** caiso:ENE_SLRS California ISO (CAISO), OASIS ENE_SLRS, Market Schedules, day-ahead market, ISO totals (https://oasis.caiso.com/mrioasis/logon.do)
- **Method note:** [`docs/methods/caiso_dam_cleared_energy.md`](../methods/caiso_dam_cleared_energy.md)
- **Cite as:** California ISO (CAISO). OASIS ENE_SLRS, Market Schedules, day-ahead market, ISO totals. Via the Energy Research Warehouse (ERW), table `caiso_dam_cleared_energy`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:system | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-09-01T00:00:00Z to 2026-11-18T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 13048.03 to 44253.94; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | ISO_TOT_LOAD_MW | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:ENE_SLRS | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://oasis.caiso.com/oasisapi/SingleZip?queryname=ENE_SLRS&market_run_id=DAM&tac_zone_name=Caiso_Totals&schedule=ALL&startdatetime=20250901T00:00-0000&enddatetime=20250916T00:00-0000&version=1&resultformat=6, https://oasis.caiso.com/oasisapi/SingleZip?queryname=ENE_SLRS&market_run_id=DAM&tac_zone_name=Caiso_Totals&schedule=ALL&startdatetime=20250916T00:00-0000&enddatetime=20251001T00:00-0000&version=1&resultformat=6, https://oasis.caiso.com/oasisapi/SingleZip?queryname=ENE_SLRS&market_run_id=DAM&tac_zone_name=Caiso_Totals&schedule=ALL&startdatetime=20251001T00:00-0000&enddatetime=20251016T00:00-0000&version=1&resultformat=6; 30 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T20:24:14Z to 2026-11-17T08:39:40Z; 30 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 10640 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dam_cleared_energy` |  | MW | 10640 | 2025-09-01T00:00:00Z | 2026-11-18T07:00:00Z |

### `caiso_fuel_supply`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 165035.

- **Source:** caiso:todays_outlook_fuelsource California ISO, Today's Outlook, supply by fuel source history files ( (https://www.caiso.com/outlook/history/YYYYMMDD/fuelsource.csv)
- **Method note:** [`docs/methods/caiso_fuel_supply.md`](../methods/caiso_fuel_supply.md)
- **Cite as:** California ISO (CAISO). Today's Outlook: supply by fuel source (fuelsource.csv history). Via the Energy Research Warehouse (ERW), table `caiso_fuel_supply`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:ISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-06-01T07:00:00Z to 2026-11-16T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -11548.5 to 23780.4167; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 165035 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 165035 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:todays_outlook_fuelsource | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.caiso.com/outlook/history/20250601/fuelsource.csv, https://www.caiso.com/outlook/history/20250602/fuelsource.csv, https://www.caiso.com/outlook/history/20250603/fuelsource.csv; 529 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-03T09:42:30Z to 2026-11-17T08:57:09Z; 102 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 165035 |

Variables (13):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `batteries_mw` |  | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `biogas_mw` |  | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `biomass_mw` |  | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `coal_mw` |  | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `geothermal_mw` |  | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `imports_mw` |  | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `large_hydro_mw` |  | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `natural_gas_mw` |  | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `nuclear_mw` |  | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `other_mw` |  | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `small_hydro_mw` |  | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `solar_mw` |  | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |
| `wind_mw` |  | MW | 12695 | 2025-06-01T07:00:00Z | 2026-11-16T07:00:00Z |

### `caiso_fuel_supply_history`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 782808.

- **Source:** caiso:todays_outlook_fuelsource_history California ISO, Today's Outlook, supply by fuel source history files ( (https://www.caiso.com/outlook/history/YYYYMMDD/fuelsource.csv)
- **Method note:** [`docs/methods/caiso_fuel_supply_history.md`](../methods/caiso_fuel_supply_history.md)
- **Cite as:** California ISO (CAISO). Today's Outlook: supply by fuel source (fuelsource.csv history), June 2018 to May 2025. Via the Energy Research Warehouse (ERW), table `caiso_fuel_supply_history`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:ISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-06-01T07:00:00Z to 2025-06-01T06:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -35159.6667 to 36178.6667; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 782808 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 782808 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:todays_outlook_fuelsource_history | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.caiso.com/outlook/history/20180601/fuelsource.csv, https://www.caiso.com/outlook/history/20180602/fuelsource.csv, https://www.caiso.com/outlook/history/20180603/fuelsource.csv; 2509 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T09:17:10Z to 2026-10-06T09:22:05Z; 296 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 782808 |

Variables (13):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `batteries_mw` |  | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `biogas_mw` |  | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `biomass_mw` |  | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `coal_mw` |  | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `geothermal_mw` |  | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `imports_mw` |  | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `large_hydro_mw` |  | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `natural_gas_mw` |  | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `nuclear_mw` |  | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `other_mw` |  | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `small_hydro_mw` |  | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `solar_mw` |  | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |
| `wind_mw` |  | MW | 60216 | 2018-06-01T07:00:00Z | 2025-06-01T06:00:00Z |

### `caiso_grid_emergencies`

What a row is: not yet written.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 1906.

- **Source:** caiso:grid_emergencies_history California ISO, Grid Emergencies History Report (1998 to present) (https://www.caiso.com/documents/grid-emergencies-history-report-1998-to-present.pdf)
- **Method note:** [`docs/methods/caiso_grid_emergencies.md`](../methods/caiso_grid_emergencies.md)
- **Cite as:** California Independent System Operator (CAISO). Grid Emergencies History Report (1998 to present). Via the Energy Research Warehouse (ERW), table `caiso_grid_emergencies`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | none | text | for example caiso_awe:1998-05-30:alert:c7046d023c, caiso_awe:1998-07-26:alert:efb4878194, caiso_awe:1998-07-27:alert:4c4cdaae48; 1906 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 1998-05-30 to 2026-10-08; 814 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others) | none | text | alert, eea1, eea2, eea3, eea_watch, flex_alert, load_interruption, rmo, stage1, stage2, stage3, transmission_emergency, vlrp, warning | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | text | California ISO | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 1906 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 1906 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 1906 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 1906 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | declared | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:grid_emergencies_history | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.caiso.com/documents/grid-emergencies-history-report-1998-to-present.pdf | 0 |
| `x_label` | not yet written |  | text | 1-hour Notification, Alert, EEA Watch, EEA1, EEA2, EEA3, Flex Alert, Generation RMO, No Touch, Power Watch, RMO, RMO*, Restricted Maintenance Operations, Stage 1, Stage 2, Stage 3, Transmission Emergency, VLRP, Warning | 0 |
| `x_region` | not yet written |  | text | CAISO Grid, ISO, Northern CA, Northern CA Region, Southern, Southern CA, Southern CA Region | 0 |
| `x_time_frame` | not yet written |  | text | for example 0000-0956, 0000-0957, 0000-1220; 515 distinct | 878 |
| `x_start` | not yet written |  | text | for example 2011-02-03 1201, 2011-02-04 1201, 2011-07-06 0800; 307 distinct | 1347 |
| `x_end` | not yet written |  | text | for example 2011-02-03 1200, 2011-02-04 1200, 2011-07-06 2000; 281 distinct | 1347 |
| `x_notice` | not yet written |  | text | for example 201802374, 202002406, 202002423; 82 distinct | 1755 |
| `x_issued_at` | not yet written |  | text | for example 01/17/2020 06:06, 02/04/2024 17:21:47, 02/12/2021 14:14; 73 distinct | 1768 |
| `x_reason` | not yet written |  | text | for example (http://wwwcaisocom/Documents/SystemAlertsWarningsandEmergenciesFactSheetpdf) The California ISO has issued a Flex Alert for the CAISO Grid effective Friday, June 18, 2021. Californians are urged to conserve electricity from June 18 at 6:00 PM to June 18 at 9:00 PM to avoid power disruptions. A news, -, A shortage of natural gas triggered by extreme cold weather in much of the United States and Canada is impacting fuel supplies to Southern CA power plants and reducing electricity generation.; 261 distinct | 1330 |
| `x_layout` | not yet written |  | text | day_lists, records, stages | 0 |
| `x_page` | not yet written |  | integer | 6 to 196; 189 distinct | 0 |

### `caiso_interconnection_queue`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 2278.

- **Source:** caiso:interconnection_queue CAISO Public Queue Report (https://www.caiso.com/documents/publicqueuereport.xlsx)
- **Method note:** [`docs/methods/caiso_interconnection_queue.md`](../methods/caiso_interconnection_queue.md)
- **Cite as:** California Independent System Operator (CAISO). Public Queue Report. Via the Energy Research Warehouse (ERW), table `caiso_interconnection_queue`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example caiso_queue:10, caiso_queue:100, caiso_queue:1000; 2278 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 20 MW SOLAR PROJECT #1, 819 HANFORD SOLAR I, ACACIA; 2270 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AZ, US-CA, US-ID, US-NM, US-NV, US-WY | 22 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 2278 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 2278 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | 0.0 to 3200.0; 535 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | active, completed, withdrawn | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | date | 2005-09-30 to 2026-10-06; 1057 distinct | 313 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 2278 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:interconnection_queue | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.caiso.com/documents/publicqueuereport.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-05T23:21:54Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | date | 2026-11-05 | 0 |
| `queue_id` | not yet written |  | text | for example 10, 100, 1000; 2278 distinct | 0 |
| `county` | not yet written |  | text | for example ALAMEDA, ALAMEDA COUNTY, AMADOR; 100 distinct | 5 |
| `state` | not yet written |  | text | AZ, CA, ID, MX, NM, NV, WY | 4 |
| `poi` | not yet written |  | text | for example 0.2 miles from Monsrate Tap  on the Monsrate Tap-Pala 69 kV line, 0.2-mile from Moro hill tap on the Moro Hill Tap - Monserate 69 kV line, 115 KV Panoche Sub; 1661 distinct | 0 |
| `zone` | not yet written |  | empty | no cell holds a value | 2278 |
| `transmission_owner` | not yet written |  | text | DCRT, DSLK, GLW, IID, PGAE, SCE, SDGE, VEA | 2 |
| `fuel_technology` | not yet written |  | text | for example Cogeneration, Combined Cycle, Combined Cycle + Combined Cycle; 41 distinct | 0 |
| `iso_status` | not yet written |  | text | ACTIVE, COMPLETED, WITHDRAWN | 0 |
| `queue_date` | not yet written |  | date | 1999-11-01 to 2023-03-02; 411 distinct | 0 |
| `proposed_in_service_date` | not yet written |  | date | 2005-12-08 to 2036-05-05; 723 distinct | 257 |
| `actual_in_service_date` | not yet written |  | date | 2005-09-30 to 2026-09-14; 204 distinct | 2039 |
| `withdrawn_date` | not yet written |  | date | 2006-01-11 to 2026-10-06; 888 distinct | 552 |

### `caiso_outlook_demand`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 33927.

- **Source:** caiso:todays_outlook_demand California ISO, Today's Outlook, demand history files ( (https://www.caiso.com/outlook/history/YYYYMMDD/demand.csv)
- **Method note:** [`docs/methods/caiso_outlook_demand.md`](../methods/caiso_outlook_demand.md)
- **Cite as:** California ISO (CAISO). Today's Outlook: demand trend (demand.csv history). Via the Energy Research Warehouse (ERW), table `caiso_outlook_demand`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:ISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-24T07:00:00Z to 2024-07-25T06:55:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.0 to 51929.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count | 0 |
| `freq` | How long the interval of the row is | none | text | PT5M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 33927 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 33927 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:todays_outlook_demand | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.caiso.com/outlook/history/20180724/demand.csv, https://www.caiso.com/outlook/history/20180725/demand.csv, https://www.caiso.com/outlook/history/20190611/demand.csv; 39 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-17T09:23:17Z to 2026-11-17T09:24:39Z; 39 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 33927 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `demand_forecast_day_ahead_mw` |  | MW | 11232 | 2018-07-24T07:00:00Z | 2024-07-25T06:55:00Z |
| `demand_forecast_hour_ahead_mw` |  | MW | 11232 | 2018-07-24T07:00:00Z | 2024-07-25T06:55:00Z |
| `demand_mw` |  | MW | 11232 | 2018-07-24T07:00:00Z | 2024-07-25T06:55:00Z |
| `demand_response_marked` |  | count | 231 | 2022-09-01T02:25:00Z | 2023-07-21T03:25:00Z |

### `caiso_reliability_daily`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 20832.

- **Source:** erw:caiso_reliability ERW derived table, California reliability method (docs/methods/california_reliability.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/california_reliability.md)
- **Method note:** [`docs/methods/california_reliability.md`](../methods/california_reliability.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. California reliability, how tight was it (warehouse/derived/caiso_reliability.py). Via the Energy Research Warehouse (ERW), table `caiso_reliability_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:ISO, eia930:CISO | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1998-05-30T00:00:00Z to 2026-11-13T00:00:00Z; 3704 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -3416.0 to 51104.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count, hour, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 20832 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 20832 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:caiso_reliability | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/california_reliability.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T17:44:49Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 20832 |

Variables (22):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `afternoon_mean_mw` |  | MW | 3025 | 2018-07-01T00:00:00Z | 2026-11-13T00:00:00Z |
| `battery_mw_evening_peak` |  | MW | 438 | 2025-08-24T00:00:00Z | 2026-11-13T00:00:00Z |
| `battery_share_pct` |  | pct | 438 | 2025-08-24T00:00:00Z | 2026-11-13T00:00:00Z |
| `evening_peak_hour` |  | hour | 3025 | 2018-07-01T00:00:00Z | 2026-11-13T00:00:00Z |
| `evening_peak_mw` |  | MW | 3025 | 2018-07-01T00:00:00Z | 2026-11-13T00:00:00Z |
| `evening_ramp_mw` |  | MW | 3025 | 2018-07-01T00:00:00Z | 2026-11-13T00:00:00Z |
| `notices_alert` |  | count | 245 | 1998-05-30T00:00:00Z | 2020-10-15T00:00:00Z |
| `notices_eea1` |  | count | 7 | 2022-08-31T00:00:00Z | 2023-07-20T00:00:00Z |
| `notices_eea2` |  | count | 4 | 2022-09-05T00:00:00Z | 2022-09-08T00:00:00Z |
| `notices_eea3` |  | count | 1 | 2022-09-06T00:00:00Z | 2022-09-06T00:00:00Z |
| `notices_eea_watch` |  | count | 12 | 2022-08-31T00:00:00Z | 2024-07-24T00:00:00Z |
| `notices_flex_alert` |  | count | 137 | 2000-05-22T00:00:00Z | 2022-09-09T00:00:00Z |
| `notices_load_interruption` |  | count | 1 | 2020-08-18T00:00:00Z | 2020-08-18T00:00:00Z |
| `notices_rmo` |  | count | 689 | 1998-07-27T00:00:00Z | 2026-10-08T00:00:00Z |
| `notices_stage1` |  | count | 146 | 1998-07-27T00:00:00Z | 2017-05-03T00:00:00Z |
| `notices_stage2` |  | count | 118 | 1998-07-27T00:00:00Z | 2021-07-09T00:00:00Z |
| `notices_stage3` |  | count | 41 | 2000-12-07T00:00:00Z | 2020-08-15T00:00:00Z |
| `notices_transmission_emergency` |  | count | 77 | 2004-01-12T00:00:00Z | 2025-04-30T00:00:00Z |
| `notices_vlrp` |  | count | 8 | 2004-02-03T00:00:00Z | 2006-07-25T00:00:00Z |
| `notices_warning` |  | count | 320 | 1998-07-27T00:00:00Z | 2021-07-29T00:00:00Z |
| `peak_demand_mw` |  | MW | 3025 | 2018-07-01T00:00:00Z | 2026-11-13T00:00:00Z |
| `peak_hour` |  | hour | 3025 | 2018-07-01T00:00:00Z | 2026-11-13T00:00:00Z |

### `caiso_wind_solar_forecast`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 352393.

- **Source:** caiso:SLD_REN_FCST California ISO, OASIS, Wind and Solar Forecast (SLD_REN_FCST) (https://oasis.caiso.com/mrioasis/logon.do)
- **Method note:** [`docs/methods/caiso_wind_solar_forecast.md`](../methods/caiso_wind_solar_forecast.md)
- **Cite as:** California ISO (CAISO). OASIS: Wind and Solar Forecast (SLD_REN_FCST), day-ahead forecast and actual generation. Via the Energy Research Warehouse (ERW), table `caiso_wind_solar_forecast`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:NP15, caiso:SP15, caiso:ZP26 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-06-01T07:00:00Z to 2026-11-19T06:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -307.9097 to 14948.67; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 352393 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | NP15, SP15, ZP26 | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:SLD_REN_FCST | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=SLD_REN_FCST&version=1&market_run_id=ACTUAL&startdatetime=20230531T07:00-0000&enddatetime=20230630T07:00-0000, https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=SLD_REN_FCST&version=1&market_run_id=ACTUAL&startdatetime=20230630T07:00-0000&enddatetime=20230730T07:00-0000, https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=SLD_REN_FCST&version=1&market_run_id=ACTUAL&startdatetime=20230730T07:00-0000&enddatetime=20230829T07:00-0000; 156 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T09:35:39Z to 2026-11-19T17:40:04Z; 156 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 352393 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `solar_actual_mw` |  | MW | 91021 | 2023-06-01T07:00:00Z | 2026-11-19T06:00:00Z |
| `solar_forecast_dam_mw` |  | MW | 91224 | 2023-06-01T07:00:00Z | 2026-11-19T06:00:00Z |
| `wind_actual_mw` |  | MW | 84973 | 2023-06-01T07:00:00Z | 2026-11-19T06:00:00Z |
| `wind_forecast_dam_mw` |  | MW | 85175 | 2023-06-01T07:00:00Z | 2026-11-19T06:00:00Z |

