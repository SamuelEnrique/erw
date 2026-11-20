# Codebook: iso

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 11 public tables (11 series; tiers: 5 derived, 6 source); 0 documented in full.

- [`iso_curtailment_monthly`](#iso_curtailment_monthly): Wind and solar curtailment by ISO, monthly, MWh (derived from the daily curtailment tables; platform tool 22)
- [`iso_dam_hub_prices`](#iso_dam_hub_prices): Rebuilt from the ERW archive by warehouse/archive/restore.py through the session 29 map (warehouse/metadata/table_migrations.csv), as of run 20261116T155131Z-github (2026-11-16T15:51:31Z); that run's own header of the table follows
- [`iso_hub_prices_history`](#iso_hub_prices_history): main-hub day-ahead and real-time prices, history from 2023-07-06 (session 49 from 2025-09-01; session 64 the year before, from 2024-09-01): CAISO SP15 and NP15, MISO Indiana Hub, NYISO N.Y.C., ISO-NE .H.INTERNAL_HUB, SPP SPPNORTH_HUB
- [`iso_hub_prices_history_2018`](#iso_hub_prices_history_2018): main-hub day-ahead and real-time prices from 2018-07-01 to 2023-07-05, before iso_hub_prices_history begins (session 7803, chain 401 part C, table 8), from hub_history.py's backfill; Energy Research Warehouse (ERW): main-hub day-ahead and real-time prices, history from 2018-07-01 (session 49 from 2025-09-01; session 64 the year before, from 2024-09-01): CAISO SP15 and NP15, MISO Indiana Hub, NYISO N.Y.C., ISO-NE .H.INTERNAL_HUB, SPP SPPNORTH_HUB
- [`iso_queue_snapshot_summary`](#iso_queue_snapshot_summary): the ISO interconnection queues summarized from their own snapshots: MW and requests by grid, status and fuel group; entered, completed and withdrawn by year; months from request to in-service (derived, session 2953)
- [`iso_queue_statistics`](#iso_queue_statistics): interconnection queue statistics by ISO and entry year (derived, session 348)
- [`iso_reserve_margin_reports`](#iso_reserve_margin_reports): grid operators' reserve margins as their own assessments print them, one row a figure (session 3798, chain 215)
- [`iso_rt_top_intervals`](#iso_rt_top_intervals): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261115T160738Z-github (2026-11-15T16:07:38Z); that run's own header of the table follows
- [`iso_rtm_hub_prices`](#iso_rtm_hub_prices): real-time hub prices, CAISO, ERCOT, MISO and SPP
- [`iso_trader_daily`](#iso_trader_daily): Rebuilt from the ERW archive by warehouse/archive/restore.py through the session 29 map (warehouse/metadata/table_migrations.csv), as of run 20261116T155131Z-github (2026-11-16T15:51:31Z); that run's own header of the table follows
- [`iso_zone_prices_history`](#iso_zone_prices_history): zone and hub prices, history from 2019 (session 140): NYISO's eleven load zones, CAISO ZP26 (TH_ZP26_GEN-APND) and SPP South (SPPSOUTH_HUB), day-ahead and real-time. ISO-NE's eight load zones are in isone_zone_prices_history: the same columns, internal (ISO-NE's notice); no ISO-NE row is in this table

### `iso_curtailment_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 3256.

- **Source:** erw:iso_curtailment_monthly ERW derived table, curtailment method (docs/methods/curtailment.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/curtailment.md)
- **Method note:** [`docs/methods/curtailment.md`](../methods/curtailment.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Curtailment by ISO, monthly (docs/methods/curtailment.md). Via the Energy Research Warehouse (ERW), table `iso_curtailment_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:ISO, spp:SPP | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2014-03-01T00:00:00Z to 2026-10-01T00:00:00Z; 152 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 12293967.0; 2148 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA | 1698 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 3256 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 3256 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:iso_curtailment_monthly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/curtailment.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-17T03:42:00Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 3256 |

Variables (19):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `curtailed_solar_economic_mwh` |  | MWh | 151 | 2014-03-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_local_mwh` |  | MWh | 58 | 2022-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_manual_mwh` |  | MWh | 151 | 2014-03-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh` |  | MWh | 300 | 2014-03-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_redispatch_mwh` |  | MWh | 151 | 2014-03-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_system_mwh` |  | MWh | 58 | 2022-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_economic_mwh` |  | MWh | 151 | 2014-03-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_local_mwh` |  | MWh | 58 | 2022-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_manual_mwh` |  | MWh | 151 | 2014-03-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh` |  | MWh | 300 | 2014-03-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_redispatch_mwh` |  | MWh | 151 | 2014-03-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_system_mwh` |  | MWh | 58 | 2022-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `share_curtailed_mwh` |  | MWh | 248 | 2014-05-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `share_curtailed_pct` |  | pct | 248 | 2014-05-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `share_hours_held` |  | count | 248 | 2014-05-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `share_hours_in_month` |  | count | 248 | 2014-05-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `share_output_mwh` |  | MWh | 248 | 2014-05-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_generation_mwh` |  | MWh | 139 | 2014-05-01T00:00:00Z | 2025-12-01T00:00:00Z |
| `wind_generation_mwh` |  | MWh | 139 | 2014-05-01T00:00:00Z | 2025-12-01T00:00:00Z |

### `iso_dam_hub_prices`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 29075.

- **Source:** caiso:PRC_LMP OASIS Locational Marginal Prices, day-ahead market (DAM) (https://oasis.caiso.com/mrioasis/logon.do)
- **Source:** ERCOT NP4-190-CD DAM Settlement Point Prices (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-190-CD)
- **Source:** miso:da_expost_lmp Day-Ahead Ex-Post LMP (daily csv) (https://www.misoenergy.org/markets-and-operations/real-time--market-data/market-reports/)
- **Source:** spp:DA-LMP-SL Day-Ahead LMP by Settlement Location (https://portal.spp.org/pages/da-lmp-by-location)
- **Method note:** [`docs/methods/iso_dam_hub_prices.md`](../methods/iso_dam_hub_prices.md)
- **Cite as:** California Independent System Operator (CAISO); Electric Reliability Council of Texas (ERCOT); Midcontinent Independent System Operator (MISO); Southwest Power Pool (SPP). DAM Settlement Point Prices; Day-Ahead Ex-Post LMP (daily csv) [PAUSED 2026-10-04: MISO's terms forbid automated access; pulls paused pending a review of MISO's terms by a person (docs/methods/miso_pause.md)]; Day-Ahead LMP by Settlement Location; OASIS Locational Marginal Prices, day-ahead market (DAM). Via the Energy Research Warehouse (ERW), table `iso_dam_hub_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, caiso:TH_ZP26_GEN-APND, ercot:HB_BUSAVG, ercot:HB_HOUSTON, ercot:HB_HUBAVG, ercot:HB_NORTH, ercot:HB_SOUTH, ercot:HB_WEST, miso:ARKANSAS.HUB, miso:ILLINOIS.HUB, miso:INDIANA.HUB, miso:LOUISIANA.HUB, miso:MICHIGAN.HUB, miso:MINN.HUB, miso:MS.HUB, miso:TEXAS.HUB, spp:SPPNORTH_HUB, spp:SPPSOUTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-08-26T05:00:00Z to 2026-11-17T07:00:00Z; 1995 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -40.0 to 719.54; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_dam, ercot_dam, miso_dam, spp_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | ARKANSAS.HUB, HB_BUSAVG, HB_HOUSTON, HB_HUBAVG, HB_NORTH, HB_SOUTH, HB_WEST, ILLINOIS.HUB, INDIANA.HUB, LOUISIANA.HUB, MICHIGAN.HUB, MINN.HUB, MS.HUB, SPPNORTH_HUB, SPPSOUTH_HUB, TEXAS.HUB, TH_NP15_GEN-APND, TH_SP15_GEN-APND, TH_ZP26_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:PRC_LMP, ercot:NP4-190-CD, miso:da_expost_lmp, spp:DA-LMP-SL | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://docs.misoenergy.org/marketreports/20260826_da_expost_lmp.csv, https://docs.misoenergy.org/marketreports/20260827_da_expost_lmp.csv, https://docs.misoenergy.org/marketreports/20260828_da_expost_lmp.csv; 285 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-25T06:59:51Z to 2026-11-16T14:17:39Z; 272 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-08-25T17:42:39Z to 2026-11-15T18:33:00Z; 120 distinct | 9917 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `lmp_dam` |  | USD/MWh | 17405 | 2026-08-26T05:00:00Z | 2026-11-17T07:00:00Z |
| `spp_dam` |  | USD/MWh | 11670 | 2026-08-26T05:00:00Z | 2026-11-17T05:00:00Z |

### `iso_hub_prices_history`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 610677.

- **Source:** caiso:PRC_INTVL_LMP OASIS Interval Locational Marginal Prices, real-time dispatch (RTD, 5-minute) (https://oasis.caiso.com/mrioasis/logon.do)
- **Source:** caiso:PRC_LMP OASIS Locational Marginal Prices, day-ahead market (DAM) (https://oasis.caiso.com/mrioasis/logon.do)
- **Source:** isone:da_lmp_hourly Day-Ahead Energy Market Hourly LMPs (https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/lmps-da-hourly)
- **Source:** isone:rt_lmp_5min Real-Time Energy Market Five-Minute LMPs (https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/lmps-rt-five-min-final)
- **Source:** miso:da_expost_lmp Day-Ahead Ex-Post LMP (daily csv) (https://www.misoenergy.org/markets-and-operations/real-time--market-data/market-reports/)
- **Source:** miso:rt_lmp_final Real-Time Final Market LMP, hourly (daily csv) (https://www.misoenergy.org/markets-and-operations/real-time--market-data/market-reports/)
- **Source:** miso:rt_lmp_prelim Real-Time Preliminary Ex-Post LMP, hourly (daily csv) (https://www.misoenergy.org/markets-and-operations/real-time--market-data/market-reports/)
- **Source:** nyiso:damlbmp Day-Ahead Market LBMP, zonal (P-2A) (http://mis.nyiso.com/public/P-2Alist.htm)
- **Source:** nyiso:realtime Real-Time Market LBMP, zonal, RTD 5-minute (P-24A) (http://mis.nyiso.com/public/P-24Alist.htm)
- **Source:** spp:DA-LMP-SL Day-Ahead LMP by Settlement Location (https://portal.spp.org/pages/da-lmp-by-location)
- **Source:** spp:RTBM-LMP-SL RTBM LMP by Settlement Location, 5-minute (https://portal.spp.org/pages/rtbm-lmp-by-location)
- **Method note:** [`docs/methods/automated_analysis_findings.md`](../methods/automated_analysis_findings.md)
- **Cite as:** California Independent System Operator (CAISO); ISO New England (ISO-NE); Midcontinent Independent System Operator (MISO); New York Independent System Operator (NYISO); Southwest Power Pool (SPP). Day-Ahead Energy Market Hourly LMPs; Day-Ahead Ex-Post LMP (daily csv) [PAUSED 2026-10-04: MISO's terms forbid automated access; pulls paused pending a review of MISO's terms by a person (docs/methods/miso_pause.md)]; Day-Ahead LMP by Settlement Location; Day-Ahead Market LBMP, zonal (P-2A); OASIS Interval Locational Marginal Prices, real-time dispatch (RTD, 5-minute); OASIS Locational Marginal Prices, day-ahead market (DAM); RTBM LMP by Settlement Location, 5-minute; Real-Time Energy Market Five-Minute LMPs; Real-Time Final Market LMP, hourly (daily csv) [PAUSED 2026-10-04: MISO's terms forbid automated access; pulls paused pending a review of MISO's terms by a person (docs/methods/miso_pause.md)]; Real-Time Market LBMP, zonal, RTD 5-minute (P-24A); Real-Time Preliminary Ex-Post LMP, hourly (daily csv) [PAUSED 2026-10-04: MISO's terms forbid automated access; pulls paused pending a review of MISO's terms by a person (docs/methods/miso_pause.md)]. Via the Energy Research Warehouse (ERW), table `iso_hub_prices_history`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, isone:.H.INTERNAL_HUB, miso:INDIANA.HUB, nyiso:N.Y.C., spp:SPPNORTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-07-06T07:00:00Z to 2026-11-17T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -241.5333 to 7627.01; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT15M, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-NY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_dam, caiso_rtm, isone_dam, isone_rtm, miso_dam, miso_rtm, nyiso_dam, nyiso_rtm, spp_dam, spp_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | .H.INTERNAL_HUB, INDIANA.HUB, N.Y.C., SPPNORTH_HUB, TH_NP15_GEN-APND, TH_SP15_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:PRC_INTVL_LMP, caiso:PRC_LMP, isone:da_lmp_hourly, isone:rt_lmp_5min, miso:da_expost_lmp, miso:rt_lmp_final, miso:rt_lmp_prelim, nyiso:damlbmp, nyiso:realtime, spp:DA-LMP-SL, spp:RTBM-LMP-SL | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example http://mis.nyiso.com/public/csv/damlbmp/20240901damlbmp_zone_csv.zip, http://mis.nyiso.com/public/csv/damlbmp/20241001damlbmp_zone_csv.zip, http://mis.nyiso.com/public/csv/damlbmp/20241101damlbmp_zone_csv.zip; more than 5000 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-25T07:12:46Z to 2026-11-17T05:03:58Z; more than 5000 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2024-08-31T16:32:46Z to 2026-11-16T04:57:07Z; 2398 distinct | 461703 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `lmp_dam` |  | USD/MWh | 135317 | 2023-07-06T07:00:00Z | 2026-11-17T07:00:00Z |
| `lmp_rtm` |  | USD/MWh | 18288 | 2024-09-01T05:00:00Z | 2026-10-03T04:00:00Z |
| `lmp_rtm_15m_mean` |  | USD/MWh | 457072 | 2023-07-06T07:00:00Z | 2026-11-16T07:45:00Z |

### `iso_hub_prices_history_2018`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 219720.

- **Source:** spp:DA-LMP-SL Day-Ahead LMP by Settlement Location (https://portal.spp.org/pages/da-lmp-by-location)
- **Source:** spp:RTBM-LMP-SL RTBM LMP by Settlement Location, 5-minute (https://portal.spp.org/pages/rtbm-lmp-by-location)
- **Method note:** [`docs/methods/hub_prices_history_2018.md`](../methods/hub_prices_history_2018.md)
- **Cite as:** Southwest Power Pool (SPP). Day-Ahead LMP by Settlement Location; RTBM LMP by Settlement Location, 5-minute. Via the Energy Research Warehouse (ERW), table `iso_hub_prices_history_2018`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | spp:SPPNORTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-01T05:00:00Z to 2023-07-06T04:45:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -215.3081 to 4556.3291; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT15M, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | spp_dam, spp_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | SPPNORTH_HUB | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | spp:DA-LMP-SL, spp:RTBM-LMP-SL | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://portal.spp.org/file-browser-api/download/rtbm-lmp-by-location?path=/2020/02/By_Day/RTBM-LMP-DAILY-SL-20200220.csv, https://portal.spp.org/file-browser-api/download/rtbm-lmp-by-location?path=/2020/03/By_Day/RTBM-LMP-DAILY-SL-20200302.csv, https://portal.spp.org/pages/da-lmp-by-location, https://portal.spp.org/pages/rtbm-lmp-by-location | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-18T01:26:04Z to 2026-11-18T03:19:21Z; 2011 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 219720 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `lmp_dam` |  | USD/MWh | 43944 | 2018-07-01T05:00:00Z | 2023-07-06T04:00:00Z |
| `lmp_rtm_15m_mean` |  | USD/MWh | 175776 | 2018-07-01T05:00:00Z | 2023-07-06T04:45:00Z |

### `iso_queue_snapshot_summary`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 570.

- **Source:** the ISOs' interconnection queues as gridstatus reads them (CAISO, ERCOT, SPP)
- **Method note:** [`docs/methods/iso_queue_snapshot_summary.md`](../methods/iso_queue_snapshot_summary.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The ISO interconnection queues summarized from their own snapshots (docs/methods/iso_queue_snapshot_summary.md). Via the Energy Research Warehouse (ERW), table `iso_queue_snapshot_summary`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example iso_queue:caiso, iso_queue:caiso:gas, iso_queue:caiso:hydro; 29 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1999-01-01T00:00:00Z to 2026-10-26T00:00:00Z; 30 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 184564.43; 383 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count, month | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 140 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 570 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 570 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:iso_queue_snapshot_summary | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/iso_queue_snapshot_summary.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-06T08:35:33Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | date | 2026-10-19, 2026-10-26 | 0 |
| `x_grid` | not yet written |  | text | caiso, ercot, spp | 0 |
| `x_fuel_group` | not yet written |  | text | gas, hybrid, hydro, nuclear, other, solar, solar_storage, storage, unknown, wind, wind_storage | 430 |
| `x_snapshot` | not yet written |  | date | 2026-10-19, 2026-10-26 | 0 |

Variables (14):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `active_count` |  | count | 22 | 2026-10-19T00:00:00Z | 2026-10-26T00:00:00Z |
| `active_mw` |  | MW | 22 | 2026-10-19T00:00:00Z | 2026-10-26T00:00:00Z |
| `completed_count` |  | count | 73 | 2002-01-01T00:00:00Z | 2026-10-26T00:00:00Z |
| `completed_mw` |  | MW | 73 | 2002-01-01T00:00:00Z | 2026-10-26T00:00:00Z |
| `entered_count` |  | count | 67 | 1999-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `entered_mw` |  | MW | 67 | 1999-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `in_service_dated` |  | count | 58 | 1999-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `median_months_to_in_service` |  | month | 42 | 2001-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `suspended_count` |  | count | 4 | 2026-10-26T00:00:00Z | 2026-10-26T00:00:00Z |
| `suspended_mw` |  | MW | 4 | 2026-10-26T00:00:00Z | 2026-10-26T00:00:00Z |
| `unknown_count` |  | count | 7 | 2026-10-26T00:00:00Z | 2026-10-26T00:00:00Z |
| `unknown_mw` |  | MW | 7 | 2026-10-26T00:00:00Z | 2026-10-26T00:00:00Z |
| `withdrawn_count` |  | count | 62 | 2002-01-01T00:00:00Z | 2026-10-26T00:00:00Z |
| `withdrawn_mw` |  | MW | 62 | 2002-01-01T00:00:00Z | 2026-10-26T00:00:00Z |

### `iso_queue_statistics`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 8990.

- **Source:** erw:iso_queue_statistics ERW derived table (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/energy_projects.md)
- **Method note:** [`docs/methods/energy_projects.md`](../methods/energy_projects.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Interconnection queue statistics by ISO and entry year (derived, session 348). Via the Energy Research Warehouse (ERW), table `iso_queue_statistics`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example caiso:queue_1999, caiso:queue_2000, caiso:queue_2001; 741 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1989-01-01T00:00:00Z to 2026-01-01T00:00:00Z; 32 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 175694.26; 2438 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count, ratio, year | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | empty | no cell holds a value | 8990 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_queue, ercot_queue, isone_queue, miso_queue, nyiso_queue, spp_queue | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 8990 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:iso_queue_statistics | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/energy_projects.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-26T00:06:45Z, 2026-11-16T14:52:19Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 8990 |
| `x_iso` | not yet written |  | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, SPP | 0 |
| `x_entry_year` | not yet written |  | integer | 1989 to 2026; 32 distinct | 0 |
| `x_rule` | not yet written |  | text | for example SPP's Commercial Operation Date, which may be the date requested rather than achieved, SPP's Commercial Operation Date, which may be the date requested rather than achieved; technology group gas (the queue's fuel_technology read by warehouse/derived/queue_statistics.py technology_group), SPP's Commercial Operation Date, which may be the date requested rather than achieved; technology group not_stated (the queue's fuel_technology read by warehouse/derived/queue_statistics.py technology_group); 32 distinct | 0 |
| `x_input_run` | not yet written |  | text | Rebuilt from the ERW archive by warehouse/archive/restore.py, as of run 20261004T023527Z-local (2026-10-04T02:35:27Z), Rebuilt from the ERW archive by warehouse/archive/restore.py, as of run 20261116T155131Z-github (2026-11-16T15:51:31Z) | 0 |

Variables (14):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `mw_entered` |  | MW | 719 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `mw_operating` |  | MW | 721 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `mw_status_not_stated` |  | MW | 741 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `mw_waiting` |  | MW | 741 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `mw_withdrawn` |  | MW | 662 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `positions_entered` |  | count | 741 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `positions_operating` |  | count | 741 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `positions_status_not_stated` |  | count | 741 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `positions_waiting` |  | count | 741 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `positions_withdrawn` |  | count | 677 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `wait_positions` |  | count | 506 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `wait_years_mean` |  | year | 291 | 1989-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `wait_years_median` |  | year | 291 | 1989-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `withdrawal_rate` |  | ratio | 677 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

### `iso_reserve_margin_reports`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 5.

- **Source:** the registry warehouse/sources/reserve_margins/ (one file a document, each figure with its page and words), filled by reading each grid operator's own assessment. No request is made by this connector.
- **Method note:** [`docs/methods/reserve_margin_reports.md`](../methods/reserve_margin_reports.md)
- **Cite as:** CAISO. CAISO, 2026 Summer Loads and Resources Assessment, May 2026. Via the Energy Research Warehouse (ERW), table `iso_reserve_margin_reports`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | reserve_report:caiso:caiso_2026_summer_loads_and_resources_assessment_may_2026 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-06-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 17.5, 25.0, 2547.0, 30.8, 46844.0 | 0 |
| `unit` | The unit of the row's value | none | text | MW, pct | 0 |
| `freq` | How long the interval of the row is | none | empty | no cell holds a value | 5 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 5 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | CAISO, 2026 Summer Loads and Resources Assessment, May 2026 | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:summer_loads_and_resources_assessment | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.caiso.com/documents/2026-summer-loads-and-resources-assessment.pdf | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-12T16:51:54Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 5 |
| `x_grid` | not yet written |  | text | CAISO | 0 |
| `x_body` | not yet written |  | text | California Independent System Operator (CAISO) | 0 |
| `x_document` | not yet written |  | text | CAISO, 2026 Summer Loads and Resources Assessment, May 2026 | 0 |
| `x_period` | not yet written |  | text | summer 2026 | 0 |
| `x_page` | not yet written |  | integer | 15, 3 | 0 |
| `x_printed` | not yet written |  | text | The 17.5 percent is the load-weighted average PRM across all LSE's., The CAISO's probabilistic assessment of "All Resource Adequacy (RA) eligible" resources shows a surplus of 2,547 MW for meeting a generally accepted "one day every 10 years loss-of-load expectation" ("1-in-10 or 0.1 LOLE") planning target., The California Energy Commission's 1-in-2 forecasted peak load for 2026 is 46,844 MW in September, hour ending 18., The model subsequently recalculates the PRM, resulting in a requirement of 25 percent to meet the reliability target., This results in an "achieved PRM" of 30.8 percent in the tightest hour based on the current portfolio. | 0 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity_surplus_mw` |  | MW | 1 | 2026-06-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `peak_forecast_mw` |  | MW | 1 | 2026-06-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `prm_achieved_pct` |  | pct | 1 | 2026-06-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `prm_required_pct` |  | pct | 1 | 2026-06-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `ra_prm_load_weighted_pct` |  | pct | 1 | 2026-06-01T00:00:00Z | 2026-06-01T00:00:00Z |

### `iso_rt_top_intervals`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 50.

- **Source:** erw:trader_view ERW derived table, trader view method (docs/methods/trader_view.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/trader_view.md)
- **Method note:** [`docs/methods/trader_view.md`](../methods/trader_view.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Trader view (docs/methods/trader_view.md). Via the Energy Research Warehouse (ERW), table `iso_rt_top_intervals`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, caiso:TH_ZP26_GEN-APND; 33 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-28T22:00:00Z, 2026-09-28T23:00:00Z, 2026-11-04T15:15:00Z, 2026-11-09T23:45:00Z, 2026-11-10T00:45:00Z, 2026-11-11T05:00:00Z, 2026-11-11T12:15:00Z, 2026-11-12T03:00:00Z, 2026-11-12T03:15:00Z, 2026-11-12T03:45:00Z, 2026-11-12T04:00:00Z, 2026-11-13T20:30:00Z, 2026-11-13T20:45:00Z, 2026-11-13T21:15:00Z, 2026-11-13T21:30:00Z, 2026-11-13T21:45:00Z, 2026-11-14T01:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 76.5668 to 1064.25; 50 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT15M, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | empty | no cell holds a value | 50 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso, ercot, isone, miso, nyiso | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example .H.INTERNAL_HUB, .Z.MAINE, .Z.NEMASSBOST; 33 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:trader_view | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/trader_view.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-30T19:20:02Z, 2026-11-12T21:47:23Z, 2026-11-13T14:43:23Z, 2026-11-15T15:01:14Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 50 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `rt_price_top10_week` |  | USD/MWh | 50 | 2026-09-28T22:00:00Z | 2026-11-14T01:00:00Z |

### `iso_rtm_hub_prices`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 85004.

- **Source:** caiso:PRC_INTVL_LMP OASIS Interval Locational Marginal Prices, real-time dispatch (RTD, 5-minute) (https://oasis.caiso.com/mrioasis/logon.do)
- **Source:** ERCOT NP6-785-ER Historical RTM Load Zone and Hub Prices (https://www.ercot.com/mp/data-products/data-product-details?id=NP6-785-ER)
- **Source:** ERCOT NP6-905-CD Settlement Point Prices at Resource Nodes, Hubs and Load Zones (https://www.ercot.com/mp/data-products/data-product-details?id=NP6-905-CD)
- **Source:** miso:rt_lmp_prelim Real-Time Preliminary Ex-Post LMP, hourly (daily csv) (https://www.misoenergy.org/markets-and-operations/real-time--market-data/market-reports/)
- **Source:** spp:RTBM-LMP-SL RTBM LMP by Settlement Location, 5-minute (https://portal.spp.org/pages/rtbm-lmp-by-location)
- **Method note:** [`docs/methods/automated_analysis_findings.md`](../methods/automated_analysis_findings.md)
- **Cite as:** California Independent System Operator (CAISO); Electric Reliability Council of Texas (ERCOT); Midcontinent Independent System Operator (MISO); Southwest Power Pool (SPP). Historical RTM Load Zone and Hub Prices; OASIS Interval Locational Marginal Prices, real-time dispatch (RTD, 5-minute); RTBM LMP by Settlement Location, 5-minute; Real-Time Final Market LMP, hourly (daily csv) [PAUSED 2026-10-04: MISO's terms forbid automated access; pulls paused pending a review of MISO's terms by a person (docs/methods/miso_pause.md)]; Real-Time Preliminary Ex-Post LMP, hourly (daily csv) [PAUSED 2026-10-04: MISO's terms forbid automated access; pulls paused pending a review of MISO's terms by a person (docs/methods/miso_pause.md)]; Settlement Point Prices at Resource Nodes, Hubs and Load Zones. Via the Energy Research Warehouse (ERW), table `iso_rtm_hub_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, caiso:TH_ZP26_GEN-APND, ercot:HB_BUSAVG, ercot:HB_HOUSTON, ercot:HB_HUBAVG, ercot:HB_NORTH, ercot:HB_SOUTH, ercot:HB_WEST, miso:ARKANSAS.HUB, miso:ILLINOIS.HUB, miso:INDIANA.HUB, miso:LOUISIANA.HUB, miso:MICHIGAN.HUB, miso:MINN.HUB, miso:MS.HUB, miso:TEXAS.HUB, spp:SPPNORTH_HUB, spp:SPPSOUTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-08-26T05:00:00Z to 2026-11-16T07:45:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -72.18 to 7627.01; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT15M, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_rtm, ercot_rtm, miso_rtm, spp_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | ARKANSAS.HUB, HB_BUSAVG, HB_HOUSTON, HB_HUBAVG, HB_NORTH, HB_SOUTH, HB_WEST, ILLINOIS.HUB, INDIANA.HUB, LOUISIANA.HUB, MICHIGAN.HUB, MINN.HUB, MS.HUB, SPPNORTH_HUB, SPPSOUTH_HUB, TEXAS.HUB, TH_NP15_GEN-APND, TH_SP15_GEN-APND, TH_ZP26_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:PRC_INTVL_LMP, ercot:NP6-785-ER, ercot:NP6-905-CD, miso:rt_lmp_final, miso:rt_lmp_prelim, spp:RTBM-LMP-SL | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://docs.misoenergy.org/marketreports/20260827_rt_lmp_final.csv, https://docs.misoenergy.org/marketreports/20260828_rt_lmp_final.csv, https://docs.misoenergy.org/marketreports/20260829_rt_lmp_final.csv; 3320 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-25T07:15:41Z to 2026-11-17T09:08:08Z; 1267 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-09-01T11:19:43Z to 2026-11-16T06:02:02Z; 3210 distinct | 33524 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `lmp_rtm` |  | USD/MWh | 7104 | 2026-08-27T05:00:00Z | 2026-10-03T04:00:00Z |
| `lmp_rtm_15m_mean` |  | USD/MWh | 33524 | 2026-08-26T07:00:00Z | 2026-11-16T07:45:00Z |
| `spp_rtm` |  | USD/MWh | 44376 | 2026-08-26T05:00:00Z | 2026-11-16T05:45:00Z |

### `iso_trader_daily`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 21879.

- **Source:** erw:trader_view ERW derived table, trader view method (docs/methods/trader_view.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/trader_view.md)
- **Method note:** [`docs/methods/iso_trader_daily.md`](../methods/iso_trader_daily.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Trader view (docs/methods/trader_view.md). Via the Energy Research Warehouse (ERW), table `iso_trader_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, caiso:TH_ZP26_GEN-APND; 39 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-08-26T00:00:00Z to 2026-11-16T00:00:00Z; 83 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -78.1525 to 7209.33; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMBtu/MWh, USD/MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | empty | no cell holds a value | 21879 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso, ercot, isone, miso, nyiso, spp | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example .H.INTERNAL_HUB, .Z.CONNECTICUT, .Z.MAINE; 39 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:trader_view | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/trader_view.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-27T10:18:41Z to 2026-11-16T14:38:24Z; 37 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 21879 |

Variables (9):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `da_mean_usd` |  | USD/MWh | 2831 | 2026-08-26T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_offpeak_mean_usd` |  | USD/MWh | 2831 | 2026-08-26T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_onpeak_mean_usd` |  | USD/MWh | 2012 | 2026-08-26T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_rt_spread_max_usd` |  | USD/MWh | 2503 | 2026-08-26T00:00:00Z | 2026-11-15T00:00:00Z |
| `da_rt_spread_mean_usd` |  | USD/MWh | 2503 | 2026-08-26T00:00:00Z | 2026-11-15T00:00:00Z |
| `da_volatility_30d_usd` |  | USD/MWh | 1393 | 2026-09-25T00:00:00Z | 2026-11-16T00:00:00Z |
| `hours_rt_over_da_50` |  | count | 2503 | 2026-08-26T00:00:00Z | 2026-11-15T00:00:00Z |
| `implied_heat_rate` |  | MMBtu/MWh | 2800 | 2026-08-26T00:00:00Z | 2026-11-15T00:00:00Z |
| `rt_mean_usd` |  | USD/MWh | 2503 | 2026-08-26T00:00:00Z | 2026-11-15T00:00:00Z |

### `iso_zone_prices_history`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1677533.

- **Source:** caiso:PRC_INTVL_LMP OASIS Interval Locational Marginal Prices, real-time dispatch (RTD, 5-minute) (https://oasis.caiso.com/mrioasis/logon.do)
- **Source:** caiso:PRC_LMP OASIS Locational Marginal Prices, day-ahead market (DAM) (https://oasis.caiso.com/mrioasis/logon.do)
- **Source:** nyiso:damlbmp Day-Ahead Market LBMP, zonal (P-2A) (http://mis.nyiso.com/public/P-2Alist.htm)
- **Source:** nyiso:rtlbmp Time-Weighted/Integrated Real-Time LBMP, zonal, hourly (P-4A) (http://mis.nyiso.com/public/P-4Alist.htm)
- **Source:** spp:DA-LMP-SL Day-Ahead LMP by Settlement Location (https://portal.spp.org/pages/da-lmp-by-location)
- **Method note:** [`docs/methods/iso_zone_prices_history.md`](../methods/iso_zone_prices_history.md)
- **Cite as:** California Independent System Operator (CAISO); New York Independent System Operator (NYISO); Southwest Power Pool (SPP). Day-Ahead LMP by Settlement Location; Day-Ahead Market LBMP, zonal (P-2A); OASIS Interval Locational Marginal Prices, real-time dispatch (RTD, 5-minute); OASIS Locational Marginal Prices, day-ahead market (DAM); Time-Weighted/Integrated Real-Time LBMP, zonal, hourly (P-4A) [terms: "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site"; the notice forbids republishing "any image or video on this website as a stand-alone file", not data (https://www.nyiso.com/legal-notice, read 6 October 2026)]. Via the Energy Research Warehouse (ERW), table `iso_zone_prices_history`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:TH_ZP26_GEN-APND, nyiso:CAPITL, nyiso:CENTRL, nyiso:DUNWOD, nyiso:GENESE, nyiso:HUD VL, nyiso:LONGIL, nyiso:MHK VL, nyiso:MILLWD, nyiso:N.Y.C., nyiso:NORTH, nyiso:WEST, spp:SPPSOUTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T05:00:00Z to 2026-11-17T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1300.74 to 4630.5689; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT15M, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-CA, US-NY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_dam, caiso_rtm, nyiso_dam, nyiso_rtm, spp_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | CAPITL, CENTRL, DUNWOD, GENESE, HUD VL, LONGIL, MHK VL, MILLWD, N.Y.C., NORTH, SPPSOUTH_HUB, TH_ZP26_GEN-APND, WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:PRC_INTVL_LMP, caiso:PRC_LMP, nyiso:damlbmp, nyiso:rtlbmp, spp:DA-LMP-SL | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example http://mis.nyiso.com/public/csv/damlbmp/20190101damlbmp_zone_csv.zip, http://mis.nyiso.com/public/csv/damlbmp/20190201damlbmp_zone_csv.zip, http://mis.nyiso.com/public/csv/damlbmp/20190301damlbmp_zone_csv.zip; 934 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T09:18:36Z to 2026-11-16T11:54:07Z; 3098 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2019-01-30T14:34:03Z to 2026-11-16T11:07:14Z; 190 distinct | 175516 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `lmp_dam` |  | USD/MWh | 851856 | 2019-01-01T05:00:00Z | 2026-11-17T07:00:00Z |
| `lmp_rtm` |  | USD/MWh | 748297 | 2019-01-01T05:00:00Z | 2026-11-16T11:00:00Z |
| `lmp_rtm_15m_mean` |  | USD/MWh | 77380 | 2024-09-01T07:00:00Z | 2026-11-16T07:45:00Z |

