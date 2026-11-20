# Codebook: iso

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 11 public tables (11 series; tiers: 5 derived, 6 source); 10 documented in full.

- [`iso_curtailment_monthly`](#iso_curtailment_monthly): One month's wind or solar curtailment figure (in all, or by reason) or wind and solar output, or one part of the month's curtailment share, for CAISO or SPP.
- [`iso_dam_hub_prices`](#iso_dam_hub_prices): The day-ahead price at one trading hub of CAISO, ERCOT, MISO or SPP for one hour.
- [`iso_hub_prices_history`](#iso_hub_prices_history): The day-ahead or real-time price at the main hub of CAISO, MISO, NYISO, ISO-NE or SPP for one interval, a history from 2023-07-06 (CAISO) or 2024-09-01.
- [`iso_hub_prices_history_2018`](#iso_hub_prices_history_2018): main-hub day-ahead and real-time prices from 2018-07-01 to 2023-07-05, before iso_hub_prices_history begins (session 7803, chain 401 part C, table 8), from hub_history.py's backfill; Energy Research Warehouse (ERW): main-hub day-ahead and real-time prices, history from 2018-07-01 (session 49 from 2025-09-01; session 64 the year before, from 2024-09-01): CAISO SP15 and NP15, MISO Indiana Hub, NYISO N.Y.C., ISO-NE .H.INTERNAL_HUB, SPP SPPNORTH_HUB
- [`iso_queue_snapshot_summary`](#iso_queue_snapshot_summary): One summary figure of CAISO's, ERCOT's or SPP's interconnection queue, either at the queue's snapshot by status and fuel group, or for one request year by grid.
- [`iso_queue_statistics`](#iso_queue_statistics): One statistic of one ISO's interconnection queue for the positions that entered it in one year, all positions or one technology group.
- [`iso_reserve_margin_reports`](#iso_reserve_margin_reports): One reserve margin figure printed in a grid operator's own resource adequacy assessment for a season or a year.
- [`iso_rt_top_intervals`](#iso_rt_top_intervals): One of the 10 highest real-time price intervals, over all hubs, of one ISO's latest 7 complete local days.
- [`iso_rtm_hub_prices`](#iso_rtm_hub_prices): The real-time price at one trading hub of CAISO, ERCOT, MISO or SPP for one interval (15 minutes, or an hour for MISO).
- [`iso_trader_daily`](#iso_trader_daily): One daily trading metric (day-ahead mean, real-time spread, implied heat rate and others) for one hub or zone of one ISO.
- [`iso_zone_prices_history`](#iso_zone_prices_history): The day-ahead or real-time price of one NYISO load zone, CAISO's ZP26 hub or SPP's South hub for one interval, a history from 2019.

### `iso_curtailment_monthly`

One month's wind or solar curtailment figure (in all, or by reason) or wind and solar output, or one part of the month's curtailment share, for CAISO or SPP.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 3256.

- **Time:** ts_utc is the first of the month at 00:00:00Z; the month is the daily tables' local operating days. A month is written only when every day of it is present; the month in progress is never written.
- **Revisions:** Merged by (entity, variable, ts_utc); each run writes the months it can complete and the merge writer keeps the earlier months. vintage is not filled.
- **Source:** erw:iso_curtailment_monthly ERW derived table, curtailment method (docs/methods/curtailment.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/curtailment.md)
- **Method note:** [`docs/methods/curtailment.md`](../methods/curtailment.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Curtailment by ISO, monthly (docs/methods/curtailment.md). Via the Energy Research Warehouse (ERW), table `iso_curtailment_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: caiso:ISO (CAISO's whole system) or spp:SPP (SPP's balancing authority area) | none | text | caiso:ISO, spp:SPP | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2014-03-01T00:00:00Z to 2026-10-01T00:00:00Z; 152 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 12293967.0; 2148 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-CA on CAISO's rows; empty on SPP's rows | none | text | US-CA | 1698 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3256 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3256 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:iso_curtailment_monthly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/curtailment.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-17T03:42:00Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3256 |

Variables (19):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `curtailed_solar_economic_mwh` | SPP: solar 'curtailed for energy' (economic dispatch), MWh | MWh | 151 | 2014-03-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_local_mwh` | CAISO: solar curtailed for local congestion (CAISO's reason Local), MWh | MWh | 58 | 2022-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_manual_mwh` | SPP: solar curtailed by manual operator instruction, MWh | MWh | 151 | 2014-03-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_mwh` | Solar energy curtailed in the month, the exact sum of the daily values, MWh | MWh | 300 | 2014-03-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_redispatch_mwh` | SPP: solar curtailed by redispatch (congestion), MWh | MWh | 151 | 2014-03-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_solar_system_mwh` | CAISO: solar curtailed for system-wide oversupply (CAISO's reason System), MWh | MWh | 58 | 2022-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_economic_mwh` | SPP: wind 'curtailed for energy' (economic dispatch), MWh | MWh | 151 | 2014-03-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_local_mwh` | CAISO: wind curtailed for local congestion (CAISO's reason Local), MWh | MWh | 58 | 2022-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_manual_mwh` | SPP: wind curtailed by manual operator instruction, MWh | MWh | 151 | 2014-03-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_mwh` | Wind energy curtailed in the month, the exact sum of the daily values, MWh | MWh | 300 | 2014-03-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_redispatch_mwh` | SPP: wind curtailed by redispatch (congestion), MWh | MWh | 151 | 2014-03-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `curtailed_wind_system_mwh` | CAISO: wind curtailed for system-wide oversupply (CAISO's reason System), MWh | MWh | 58 | 2022-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `share_curtailed_mwh` | The curtailed MWh of the share, cut to the days both are held | MWh | 248 | 2014-05-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `share_curtailed_pct` | Curtailed MWh over curtailed plus wind and solar output MWh, over the days both are held, percent (CAISO's output its own; SPP's EIA-930's hourly net generation) | pct | 248 | 2014-05-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `share_hours_held` | The hours of the month both curtailment and output are held | count | 248 | 2014-05-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `share_hours_in_month` | The hours of the month | count | 248 | 2014-05-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `share_output_mwh` | The wind and solar output MWh of the share, over the same days | MWh | 248 | 2014-05-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `solar_generation_mwh` | CAISO: its solar output in the month, curtailment not included, MWh | MWh | 139 | 2014-05-01T00:00:00Z | 2025-12-01T00:00:00Z |
| `wind_generation_mwh` | CAISO: its wind output in the month, curtailment not included, MWh | MWh | 139 | 2014-05-01T00:00:00Z | 2025-12-01T00:00:00Z |

### `iso_dam_hub_prices`

The day-ahead price at one trading hub of CAISO, ERCOT, MISO or SPP for one hour.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 29075.

- **Time:** ts_utc is the start of the hour in UTC; operating days are each grid's local days.
- **Revisions:** Merged by (entity, variable, ts_utc) into each grid's member and consolidated by market; a day is asked on about three runs (and once more as a forward day), a value asked again replacing the old one; nothing trims the table. vintage is the operator's publish time where known (ERCOT's document time, MISO's file Last-Modified), empty for CAISO and SPP.
- **Source:** caiso:PRC_LMP OASIS Locational Marginal Prices, day-ahead market (DAM) (https://oasis.caiso.com/mrioasis/logon.do)
- **Source:** ERCOT NP4-190-CD DAM Settlement Point Prices (https://www.ercot.com/mp/data-products/data-product-details?id=NP4-190-CD)
- **Source:** miso:da_expost_lmp Day-Ahead Ex-Post LMP (daily csv) (https://www.misoenergy.org/markets-and-operations/real-time--market-data/market-reports/)
- **Source:** spp:DA-LMP-SL Day-Ahead LMP by Settlement Location (https://portal.spp.org/pages/da-lmp-by-location)
- **Method note:** [`docs/methods/iso_dam_hub_prices.md`](../methods/iso_dam_hub_prices.md)
- **Cite as:** California Independent System Operator (CAISO); Electric Reliability Council of Texas (ERCOT); Midcontinent Independent System Operator (MISO); Southwest Power Pool (SPP). DAM Settlement Point Prices; Day-Ahead Ex-Post LMP (daily csv) [PAUSED 2026-10-04: MISO's terms forbid automated access; pulls paused pending a review of MISO's terms by a person (docs/methods/miso_pause.md)]; Day-Ahead LMP by Settlement Location; OASIS Locational Marginal Prices, day-ahead market (DAM). Via the Energy Research Warehouse (ERW), table `iso_dam_hub_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: <iso>:<hub>, the operator's hub name | none | text | caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, caiso:TH_ZP26_GEN-APND, ercot:HB_BUSAVG, ercot:HB_HOUSTON, ercot:HB_HUBAVG, ercot:HB_NORTH, ercot:HB_SOUTH, ercot:HB_WEST, miso:ARKANSAS.HUB, miso:ILLINOIS.HUB, miso:INDIANA.HUB, miso:LOUISIANA.HUB, miso:MICHIGAN.HUB, miso:MINN.HUB, miso:MS.HUB, miso:TEXAS.HUB, spp:SPPNORTH_HUB, spp:SPPSOUTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-08-26T05:00:00Z to 2026-11-17T07:00:00Z; 1995 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -40.0 to 719.54; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-CA for CAISO, US-TX for ERCOT, a list of 15 states for MISO and of 14 for SPP | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: caiso_dam, ercot_dam, miso_dam or spp_dam: the day-ahead market of the grid the row belongs to | none | text | caiso_dam, ercot_dam, miso_dam, spp_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The operator's trading hub: CAISO TH_NP15_GEN-APND, TH_SP15_GEN-APND, TH_ZP26_GEN-APND; ERCOT HB_HOUSTON, HB_NORTH, HB_SOUTH, HB_WEST and the averages HB_BUSAVG and HB_HUBAVG; MISO's eight hubs (ARKANSAS.HUB to TEXAS.HUB); SPP SPPNORTH_HUB and SPPSOUTH_HUB | none | text | ARKANSAS.HUB, HB_BUSAVG, HB_HOUSTON, HB_HUBAVG, HB_NORTH, HB_SOUTH, HB_WEST, ILLINOIS.HUB, INDIANA.HUB, LOUISIANA.HUB, MICHIGAN.HUB, MINN.HUB, MS.HUB, SPPNORTH_HUB, SPPSOUTH_HUB, TEXAS.HUB, TH_NP15_GEN-APND, TH_SP15_GEN-APND, TH_ZP26_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:PRC_LMP, ercot:NP4-190-CD, miso:da_expost_lmp, spp:DA-LMP-SL | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://docs.misoenergy.org/marketreports/20260826_da_expost_lmp.csv, https://docs.misoenergy.org/marketreports/20260827_da_expost_lmp.csv, https://docs.misoenergy.org/marketreports/20260828_da_expost_lmp.csv; 285 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-25T06:59:51Z to 2026-11-16T14:17:39Z; 272 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: ERCOT's document publish time or MISO's file Last-Modified; empty on CAISO's and SPP's rows (publish time not given by the source) | none | utc time | 2026-08-25T17:42:39Z to 2026-11-15T18:33:00Z; 120 distinct | 9917 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `lmp_dam` | Day-ahead locational marginal price (the price of energy at the hub in the day-ahead market): CAISO, MISO (ex-post) and SPP | USD/MWh | 17405 | 2026-08-26T05:00:00Z | 2026-11-17T07:00:00Z |
| `spp_dam` | ERCOT's day-ahead settlement point price at the hub (spp here is ERCOT's 'settlement point price', not the grid SPP) | USD/MWh | 11670 | 2026-08-26T05:00:00Z | 2026-11-17T05:00:00Z |

### `iso_hub_prices_history`

The day-ahead or real-time price at the main hub of CAISO, MISO, NYISO, ISO-NE or SPP for one interval, a history from 2023-07-06 (CAISO) or 2024-09-01.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 610677.

- **Time:** ts_utc is the start of the interval in UTC; day-ahead and MISO's real-time are hourly, the other real-time prices 15-minute means of 5-minute prices.
- **Revisions:** The daily run merges the live tables' rows of these hubs into this table by (entity, variable, ts_utc); never trimmed. A day is written only when every interval of every hub is there.
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
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: <iso>:<hub>, the operator's hub or zone name | none | text | caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, isone:.H.INTERNAL_HUB, miso:INDIANA.HUB, nyiso:N.Y.C., spp:SPPNORTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-07-06T07:00:00Z to 2026-11-17T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -241.5333 to 7627.01; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is. Here: PT1H for day-ahead and MISO's real-time rows, PT15M for the other real-time rows | none | text | PT15M, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-NY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: <iso>_dam or <iso>_rtm for caiso, isone, miso, nyiso and spp: the grid's day-ahead or real-time market | none | text | caiso_dam, caiso_rtm, isone_dam, isone_rtm, miso_dam, miso_rtm, nyiso_dam, nyiso_rtm, spp_dam, spp_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Each grid's main hub: CAISO TH_SP15_GEN-APND and TH_NP15_GEN-APND, MISO INDIANA.HUB, NYISO the N.Y.C. zone, ISO-NE .H.INTERNAL_HUB, SPP SPPNORTH_HUB | none | text | .H.INTERNAL_HUB, INDIANA.HUB, N.Y.C., SPPNORTH_HUB, TH_NP15_GEN-APND, TH_SP15_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:PRC_INTVL_LMP, caiso:PRC_LMP, isone:da_lmp_hourly, isone:rt_lmp_5min, miso:da_expost_lmp, miso:rt_lmp_final, miso:rt_lmp_prelim, nyiso:damlbmp, nyiso:realtime, spp:DA-LMP-SL, spp:RTBM-LMP-SL | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example http://mis.nyiso.com/public/csv/damlbmp/20240901damlbmp_zone_csv.zip, http://mis.nyiso.com/public/csv/damlbmp/20241001damlbmp_zone_csv.zip, http://mis.nyiso.com/public/csv/damlbmp/20241101damlbmp_zone_csv.zip; more than 5000 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-25T07:12:46Z to 2026-11-17T05:03:58Z; more than 5000 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The file's publish time where the source gives one; empty on most rows | none | utc time | 2024-08-31T16:32:46Z to 2026-11-16T04:57:07Z; 2398 distinct | 461703 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `lmp_dam` | Day-ahead locational marginal price (NYISO's LBMP), hourly | USD/MWh | 135317 | 2023-07-06T07:00:00Z | 2026-11-17T07:00:00Z |
| `lmp_rtm` | MISO's hourly real-time locational marginal price (final, or preliminary ex-post until final) | USD/MWh | 18288 | 2024-09-01T05:00:00Z | 2026-10-03T04:00:00Z |
| `lmp_rtm_15m_mean` | Real-time locational marginal price as a 15-minute mean of the 5-minute prices (the mean of exactly three; NYISO's time-weighted), rounded to 4 decimals | USD/MWh | 457072 | 2023-07-06T07:00:00Z | 2026-11-16T07:45:00Z |

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

One summary figure of CAISO's, ERCOT's or SPP's interconnection queue, either at the queue's snapshot by status and fuel group, or for one request year by grid.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 570.

- **Time:** For snapshot rows ts_utc is the snapshot's retrieval day and freq is empty; for year rows ts_utc is the year's first day with freq P1Y.
- **Revisions:** Rebuilt from the queue tables' current snapshots by each run; one snapshot a grid, so withdrawals between snapshots are not counted. vintage is the snapshot date.
- **Source:** the ISOs' interconnection queues as gridstatus reads them (CAISO, ERCOT, SPP)
- **Method note:** [`docs/methods/iso_queue_snapshot_summary.md`](../methods/iso_queue_snapshot_summary.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The ISO interconnection queues summarized from their own snapshots (docs/methods/iso_queue_snapshot_summary.md). Via the Energy Research Warehouse (ERW), table `iso_queue_snapshot_summary`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: iso_queue:<grid>:<fuel group> for a snapshot row, iso_queue:<grid> for a year row | none | text | for example iso_queue:caiso, iso_queue:caiso:gas, iso_queue:caiso:hydro; 29 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1999-01-01T00:00:00Z to 2026-10-26T00:00:00Z; 30 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 184564.43; 383 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count, month | 0 |
| `freq` | How long the interval of the row is. Here: Empty on the snapshot rows; P1Y on the year rows | none | text | P1Y | 140 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US in every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 570 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 570 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:iso_queue_snapshot_summary | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/iso_queue_snapshot_summary.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-06T08:35:33Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The snapshot's date (YYYY-MM-DD), the queue table's retrieval day | none | date | 2026-10-19, 2026-10-26 | 0 |
| `x_grid` | The grid whose queue the row summarizes (caiso, ercot, spp) | none | text | caiso, ercot, spp | 0 |
| `x_fuel_group` | The fuel group the queue's fuel labels are mapped to by the first matching rule (solar, wind, storage, solar_storage, wind_storage, gas, nuclear, hydro, hybrid, other, unknown) | none | text | gas, hybrid, hydro, nuclear, other, solar, solar_storage, storage, unknown, wind, wind_storage | 430: Empty on the year rows (by grid, not by fuel) |
| `x_snapshot` | The date of the queue snapshot summarized | none | date | 2026-10-19, 2026-10-26 | 0 |

Variables (14):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `active_count` | Requests with status active at the snapshot | count | 22 | 2026-10-19T00:00:00Z | 2026-10-26T00:00:00Z |
| `active_mw` | MW of the requests with status active at the snapshot | MW | 22 | 2026-10-19T00:00:00Z | 2026-10-26T00:00:00Z |
| `completed_count` | Snapshot rows: requests with status completed; year rows: requests completed in the year | count | 73 | 2002-01-01T00:00:00Z | 2026-10-26T00:00:00Z |
| `completed_mw` | Snapshot rows: MW with status completed; year rows: MW completed in the year (in-service date of a completed request, on or before the snapshot) | MW | 73 | 2002-01-01T00:00:00Z | 2026-10-26T00:00:00Z |
| `entered_count` | Requests that entered the queue in the year (queue date) | count | 67 | 1999-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `entered_mw` | MW of the requests that entered the queue in the year (queue date) | MW | 67 | 1999-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `in_service_dated` | Requests of that request year with both a queue date and an in-service date | count | 58 | 1999-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `median_months_to_in_service` | Median months from queue date to in-service date for that request year, written at 5 or more dated requests | month | 42 | 2001-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `suspended_count` | Requests with status suspended at the snapshot | count | 4 | 2026-10-26T00:00:00Z | 2026-10-26T00:00:00Z |
| `suspended_mw` | MW of the requests with status suspended at the snapshot | MW | 4 | 2026-10-26T00:00:00Z | 2026-10-26T00:00:00Z |
| `unknown_count` | Requests with no status at the snapshot | count | 7 | 2026-10-26T00:00:00Z | 2026-10-26T00:00:00Z |
| `unknown_mw` | MW of the requests with no status at the snapshot | MW | 7 | 2026-10-26T00:00:00Z | 2026-10-26T00:00:00Z |
| `withdrawn_count` | Snapshot rows: requests with status withdrawn; year rows: requests withdrawn in the year | count | 62 | 2002-01-01T00:00:00Z | 2026-10-26T00:00:00Z |
| `withdrawn_mw` | Snapshot rows: MW with status withdrawn; year rows: MW withdrawn in the year (withdrawn date) | MW | 62 | 2002-01-01T00:00:00Z | 2026-10-26T00:00:00Z |

### `iso_queue_statistics`

One statistic of one ISO's interconnection queue for the positions that entered it in one year, all positions or one technology group.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 8990.

- **Time:** ts_utc is the first day of the entry year (the year of the ISO's queue date) at 00:00:00Z.
- **Revisions:** Rebuilt whole from the six ISO queue tables by each run of the builder; vintage is not filled.
- **Source:** erw:iso_queue_statistics ERW derived table (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/energy_projects.md)
- **Method note:** [`docs/methods/energy_projects.md`](../methods/energy_projects.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Interconnection queue statistics by ISO and entry year (derived, session 348). Via the Energy Research Warehouse (ERW), table `iso_queue_statistics`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: <iso>:queue_<entry year> for all positions, <iso>:tech_<group>:queue_<entry year> for a technology group (storage, solar, solar_storage, wind, gas, other, not_stated) | none | text | for example caiso:queue_1999, caiso:queue_2000, caiso:queue_2001; 741 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1989-01-01T00:00:00Z to 2026-01-01T00:00:00Z; 32 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 175694.26; 2438 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count, ratio, year | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 8990 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: <iso>_queue: the queue of the ISO the row summarizes | none | text | caiso_queue, ercot_queue, isone_queue, miso_queue, nyiso_queue, spp_queue | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 8990 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:iso_queue_statistics | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/energy_projects.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-26T00:06:45Z, 2026-11-16T14:52:19Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 8990 |
| `x_iso` | The ISO whose queue the row summarizes (CAISO, ERCOT, ISO-NE, MISO, NYISO, SPP) | none | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, SPP | 0 |
| `x_entry_year` | The year the positions entered the queue (the year of the queue date) | none | integer | 1989 to 2026; 32 distinct | 0 |
| `x_rule` | In words, how the ISO's status words were read for this variable, and the technology group rule where the row is a group's | none | text | for example SPP's Commercial Operation Date, which may be the date requested rather than achieved, SPP's Commercial Operation Date, which may be the date requested rather than achieved; technology group gas (the queue's fuel_technology read by warehouse/derived/queue_statistics.py technology_group), SPP's Commercial Operation Date, which may be the date requested rather than achieved; technology group not_stated (the queue's fuel_technology read by warehouse/derived/queue_statistics.py technology_group); 32 distinct | 0 |
| `x_input_run` | The header line naming the archive run the input queue table was rebuilt from | none | text | Rebuilt from the ERW archive by warehouse/archive/restore.py, as of run 20261004T023527Z-local (2026-10-04T02:35:27Z), Rebuilt from the ERW archive by warehouse/archive/restore.py, as of run 20261116T155131Z-github (2026-11-16T15:51:31Z) | 0 |

Variables (14):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `mw_entered` | MW the queue states for the positions entered, summed | MW | 719 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `mw_operating` | MW of the positions that reached operation | MW | 721 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `mw_status_not_stated` | MW of the positions with no status | MW | 741 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `mw_waiting` | MW of the positions still waiting | MW | 741 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `mw_withdrawn` | MW of the positions withdrawn | MW | 662 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `positions_entered` | Positions that entered the queue in the year | count | 741 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `positions_operating` | Of those, positions that reached operation (completed; for ERCOT a signed interconnection agreement) | count | 741 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `positions_status_not_stated` | Of those, positions the ISO lists with no status | count | 741 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `positions_waiting` | Of those, positions still waiting (active or suspended) | count | 741 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `positions_withdrawn` | Of those, positions withdrawn (none held for ERCOT) | count | 677 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `wait_positions` | Operating positions with a queue date and an in-service date on or after it | count | 506 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `wait_years_mean` | Mean years from queue date to in-service date of those positions | year | 291 | 1989-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `wait_years_median` | Median years from queue date to in-service date (days over 365.25) of those positions | year | 291 | 1989-01-01T00:00:00Z | 2024-01-01T00:00:00Z |
| `withdrawal_rate` | Withdrawn positions over positions entered, by count | ratio | 677 | 1989-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

### `iso_reserve_margin_reports`

One reserve margin figure printed in a grid operator's own resource adequacy assessment for a season or a year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 5.

- **Time:** ts_utc is the first day of the period the assessment covers, at 00:00:00Z; freq is empty.
- **Revisions:** Rewritten from the registry files under warehouse/sources/reserve_margins/ by each run; no request is made. vintage is not filled.
- **Source:** the registry warehouse/sources/reserve_margins/ (one file a document, each figure with its page and words), filled by reading each grid operator's own assessment. No request is made by this connector.
- **Method note:** [`docs/methods/reserve_margin_reports.md`](../methods/reserve_margin_reports.md)
- **Cite as:** CAISO. CAISO, 2026 Summer Loads and Resources Assessment, May 2026. Via the Energy Research Warehouse (ERW), table `iso_reserve_margin_reports`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: reserve_report:<grid>:<document slug> | none | text | reserve_report:caiso:caiso_2026_summer_loads_and_resources_assessment_may_2026 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-06-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 17.5, 25.0, 2547.0, 30.8, 46844.0 | 0 |
| `unit` | The unit of the row's value | none | text | MW, pct | 0 |
| `freq` | How long the interval of the row is. Here: Not filled: the period is named in x_period | none | empty | no cell holds a value | 5 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US in every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The document's title, not a price node | none | text | CAISO, 2026 Summer Loads and Resources Assessment, May 2026 | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:summer_loads_and_resources_assessment | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.caiso.com/documents/2026-summer-loads-and-resources-assessment.pdf | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-12T16:51:54Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5 |
| `x_grid` | The grid the assessment covers | none | text | CAISO | 0 |
| `x_body` | The body that wrote the assessment | none | text | California Independent System Operator (CAISO) | 0 |
| `x_document` | The assessment's title and date | none | text | CAISO, 2026 Summer Loads and Resources Assessment, May 2026 | 0 |
| `x_period` | The period the figure is for, in words (summer 2026) | none | text | summer 2026 | 0 |
| `x_page` | The page of the document the figure is printed on | none | integer | 15, 3 | 0 |
| `x_printed` | The words the document prints the figure in | none | text | The 17.5 percent is the load-weighted average PRM across all LSE's., The CAISO's probabilistic assessment of "All Resource Adequacy (RA) eligible" resources shows a surplus of 2,547 MW for meeting a generally accepted "one day every 10 years loss-of-load expectation" ("1-in-10 or 0.1 LOLE") planning target., The California Energy Commission's 1-in-2 forecasted peak load for 2026 is 46,844 MW in September, hour ending 18., The model subsequently recalculates the PRM, resulting in a requirement of 25 percent to meet the reliability target., This results in an "achieved PRM" of 30.8 percent in the tightest hour based on the current portfolio. | 0 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity_surplus_mw` | The capacity above that reliability target, MW | MW | 1 | 2026-06-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `peak_forecast_mw` | The peak demand the assessment plans for, MW | MW | 1 | 2026-06-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `prm_achieved_pct` | The planning reserve margin the assessment's model achieves in its tightest hour, percent | pct | 1 | 2026-06-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `prm_required_pct` | The reserve margin the assessment finds is needed to meet its reliability target, percent | pct | 1 | 2026-06-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `ra_prm_load_weighted_pct` | The reserve margin the load-serving entities must carry for resource adequacy, load-weighted, percent | pct | 1 | 2026-06-01T00:00:00Z | 2026-06-01T00:00:00Z |

### `iso_rt_top_intervals`

One of the 10 highest real-time price intervals, over all hubs, of one ISO's latest 7 complete local days.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 50.

- **Time:** ts_utc is the interval start in UTC; freq is the real-time table's interval (PT15M or PT1H).
- **Revisions:** A snapshot replaced whole by each run; the header names each ISO's week. Ties go to the earlier interval.
- **Source:** erw:trader_view ERW derived table, trader view method (docs/methods/trader_view.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/trader_view.md)
- **Method note:** [`docs/methods/trader_view.md`](../methods/trader_view.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Trader view (docs/methods/trader_view.md). Via the Energy Research Warehouse (ERW), table `iso_rt_top_intervals`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: The hub or zone of the real-time price table, <iso>:<node> | none | text | for example caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, caiso:TH_ZP26_GEN-APND; 33 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-28T22:00:00Z, 2026-09-28T23:00:00Z, 2026-11-04T15:15:00Z, 2026-11-09T23:45:00Z, 2026-11-10T00:45:00Z, 2026-11-11T05:00:00Z, 2026-11-11T12:15:00Z, 2026-11-12T03:00:00Z, 2026-11-12T03:15:00Z, 2026-11-12T03:45:00Z, 2026-11-12T04:00:00Z, 2026-11-13T20:30:00Z, 2026-11-13T20:45:00Z, 2026-11-13T21:15:00Z, 2026-11-13T21:30:00Z, 2026-11-13T21:45:00Z, 2026-11-14T01:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 76.5668 to 1064.25; 50 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT15M, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 50 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: The ISO (caiso, ercot, isone, miso, nyiso), not a market code | none | text | caiso, ercot, isone, miso, nyiso | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The hub or zone name as in the real-time price table | none | text | for example .H.INTERNAL_HUB, .Z.MAINE, .Z.NEMASSBOST; 33 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:trader_view | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/trader_view.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-30T19:20:02Z, 2026-11-12T21:47:23Z, 2026-11-13T14:43:23Z, 2026-11-15T15:01:14Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 50 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `rt_price_top10_week` | A real-time price among the ISO's 10 highest intervals of the week, USD/MWh | USD/MWh | 50 | 2026-09-28T22:00:00Z | 2026-11-14T01:00:00Z |

### `iso_rtm_hub_prices`

The real-time price at one trading hub of CAISO, ERCOT, MISO or SPP for one interval (15 minutes, or an hour for MISO).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 85004.

- **Time:** ts_utc is the start of the interval in UTC; operating days are each grid's local days.
- **Revisions:** Merged by (entity, variable, ts_utc) into each grid's member and consolidated by market; a day read again replaces its rows, every other row is kept. vintage is the publish time where the source gives one (ERCOT's document time, MISO's file Last-Modified).
- **Source:** caiso:PRC_INTVL_LMP OASIS Interval Locational Marginal Prices, real-time dispatch (RTD, 5-minute) (https://oasis.caiso.com/mrioasis/logon.do)
- **Source:** ERCOT NP6-785-ER Historical RTM Load Zone and Hub Prices (https://www.ercot.com/mp/data-products/data-product-details?id=NP6-785-ER)
- **Source:** ERCOT NP6-905-CD Settlement Point Prices at Resource Nodes, Hubs and Load Zones (https://www.ercot.com/mp/data-products/data-product-details?id=NP6-905-CD)
- **Source:** miso:rt_lmp_prelim Real-Time Preliminary Ex-Post LMP, hourly (daily csv) (https://www.misoenergy.org/markets-and-operations/real-time--market-data/market-reports/)
- **Source:** spp:RTBM-LMP-SL RTBM LMP by Settlement Location, 5-minute (https://portal.spp.org/pages/rtbm-lmp-by-location)
- **Method note:** [`docs/methods/automated_analysis_findings.md`](../methods/automated_analysis_findings.md)
- **Cite as:** California Independent System Operator (CAISO); Electric Reliability Council of Texas (ERCOT); Midcontinent Independent System Operator (MISO); Southwest Power Pool (SPP). Historical RTM Load Zone and Hub Prices; OASIS Interval Locational Marginal Prices, real-time dispatch (RTD, 5-minute); RTBM LMP by Settlement Location, 5-minute; Real-Time Final Market LMP, hourly (daily csv) [PAUSED 2026-10-04: MISO's terms forbid automated access; pulls paused pending a review of MISO's terms by a person (docs/methods/miso_pause.md)]; Real-Time Preliminary Ex-Post LMP, hourly (daily csv) [PAUSED 2026-10-04: MISO's terms forbid automated access; pulls paused pending a review of MISO's terms by a person (docs/methods/miso_pause.md)]; Settlement Point Prices at Resource Nodes, Hubs and Load Zones. Via the Energy Research Warehouse (ERW), table `iso_rtm_hub_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: <iso>:<hub>, the operator's hub name | none | text | caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, caiso:TH_ZP26_GEN-APND, ercot:HB_BUSAVG, ercot:HB_HOUSTON, ercot:HB_HUBAVG, ercot:HB_NORTH, ercot:HB_SOUTH, ercot:HB_WEST, miso:ARKANSAS.HUB, miso:ILLINOIS.HUB, miso:INDIANA.HUB, miso:LOUISIANA.HUB, miso:MICHIGAN.HUB, miso:MINN.HUB, miso:MS.HUB, miso:TEXAS.HUB, spp:SPPNORTH_HUB, spp:SPPSOUTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-08-26T05:00:00Z to 2026-11-16T07:45:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -72.18 to 7627.01; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is. Here: PT15M, or PT1H for MISO's hourly rows | none | text | PT15M, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-CA for CAISO, US-TX for ERCOT, a list of 15 states for MISO and of 14 for SPP | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: caiso_rtm, ercot_rtm, miso_rtm or spp_rtm: the real-time market of the grid the row belongs to | none | text | caiso_rtm, ercot_rtm, miso_rtm, spp_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The operator's trading hub: CAISO TH_NP15_GEN-APND, TH_SP15_GEN-APND, TH_ZP26_GEN-APND; ERCOT HB_HOUSTON, HB_NORTH, HB_SOUTH, HB_WEST and the averages HB_BUSAVG and HB_HUBAVG; MISO's eight hubs; SPP SPPNORTH_HUB and SPPSOUTH_HUB | none | text | ARKANSAS.HUB, HB_BUSAVG, HB_HOUSTON, HB_HUBAVG, HB_NORTH, HB_SOUTH, HB_WEST, ILLINOIS.HUB, INDIANA.HUB, LOUISIANA.HUB, MICHIGAN.HUB, MINN.HUB, MS.HUB, SPPNORTH_HUB, SPPSOUTH_HUB, TEXAS.HUB, TH_NP15_GEN-APND, TH_SP15_GEN-APND, TH_ZP26_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:PRC_INTVL_LMP, ercot:NP6-785-ER, ercot:NP6-905-CD, miso:rt_lmp_final, miso:rt_lmp_prelim, spp:RTBM-LMP-SL | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://docs.misoenergy.org/marketreports/20260827_rt_lmp_final.csv, https://docs.misoenergy.org/marketreports/20260828_rt_lmp_final.csv, https://docs.misoenergy.org/marketreports/20260829_rt_lmp_final.csv; 3320 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-25T07:15:41Z to 2026-11-17T09:08:08Z; 1267 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: ERCOT's document publish time or MISO's file Last-Modified; empty where the source gives no publish time (CAISO, SPP) | none | utc time | 2026-09-01T11:19:43Z to 2026-11-16T06:02:02Z; 3210 distinct | 33524 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `lmp_rtm` | MISO: hourly real-time ex-post locational marginal price (preliminary report rows have source miso:rt_lmp_prelim) | USD/MWh | 7104 | 2026-08-27T05:00:00Z | 2026-10-03T04:00:00Z |
| `lmp_rtm_15m_mean` | CAISO and SPP: real-time locational marginal price, the arithmetic mean of exactly three 5-minute prices of the quarter hour, rounded to 4 decimals | USD/MWh | 33524 | 2026-08-26T07:00:00Z | 2026-11-16T07:45:00Z |
| `spp_rtm` | ERCOT's real-time settlement point price at the hub, 15-minute (spp here is ERCOT's 'settlement point price', not the grid SPP) | USD/MWh | 44376 | 2026-08-26T05:00:00Z | 2026-11-16T05:45:00Z |

### `iso_trader_daily`

One daily trading metric (day-ahead mean, real-time spread, implied heat rate and others) for one hub or zone of one ISO.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 21879.

- **Time:** ts_utc is the ISO's local operating day at 00:00:00Z.
- **Revisions:** Each daily run computes every day the price tables hold again and merges it by (entity, variable, ts_utc); a row whose value has not moved keeps the retrieved_at of the run that first wrote it. vintage is not filled.
- **Source:** erw:trader_view ERW derived table, trader view method (docs/methods/trader_view.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/trader_view.md)
- **Method note:** [`docs/methods/iso_trader_daily.md`](../methods/iso_trader_daily.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Trader view (docs/methods/trader_view.md). Via the Energy Research Warehouse (ERW), table `iso_trader_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: The price table's own entity, <iso>:<node> | none | text | for example caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, caiso:TH_ZP26_GEN-APND; 39 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-08-26T00:00:00Z to 2026-11-16T00:00:00Z; 83 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -78.1525 to 7209.33; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMBtu/MWh, USD/MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 21879 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: The ISO the row belongs to (caiso, ercot, isone, miso, nyiso, spp), not a market code | none | text | caiso, ercot, isone, miso, nyiso, spp | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The hub or zone, the part of entity after the colon | none | text | for example .H.INTERNAL_HUB, .Z.CONNECTICUT, .Z.MAINE; 39 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:trader_view | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/trader_view.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-27T10:18:41Z to 2026-11-16T14:38:24Z; 37 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 21879 |

Variables (9):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `da_mean_usd` | Mean of the day's day-ahead hourly prices (every hour required), USD/MWh | USD/MWh | 2831 | 2026-08-26T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_offpeak_mean_usd` | Mean of the day-ahead prices over every other hour of the day (the whole day on weekends and holidays), USD/MWh | USD/MWh | 2831 | 2026-08-26T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_onpeak_mean_usd` | Mean of the day-ahead prices over on-peak hours (hours starting 06:00 to 21:00 local on weekdays that are not NERC holidays), USD/MWh | USD/MWh | 2012 | 2026-08-26T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_rt_spread_max_usd` | The largest hourly real-time minus day-ahead of the day, USD/MWh | USD/MWh | 2503 | 2026-08-26T00:00:00Z | 2026-11-15T00:00:00Z |
| `da_rt_spread_mean_usd` | Mean over the day's hours of real-time minus day-ahead, USD/MWh | USD/MWh | 2503 | 2026-08-26T00:00:00Z | 2026-11-15T00:00:00Z |
| `da_volatility_30d_usd` | Sample standard deviation of the 30 day-over-day changes in da_mean_usd over the 31 days ending on the day, USD/MWh | USD/MWh | 1393 | 2026-09-25T00:00:00Z | 2026-11-16T00:00:00Z |
| `hours_rt_over_da_50` | Hours in which real-time exceeded day-ahead by more than 50 USD/MWh | count | 2503 | 2026-08-26T00:00:00Z | 2026-11-15T00:00:00Z |
| `implied_heat_rate` | da_mean_usd over the Henry Hub gas spot price: how many MMBtu of gas a MWh sells for, MMBtu/MWh | MMBtu/MWh | 2800 | 2026-08-26T00:00:00Z | 2026-11-15T00:00:00Z |
| `rt_mean_usd` | Mean of the day's hourly real-time prices, USD/MWh | USD/MWh | 2503 | 2026-08-26T00:00:00Z | 2026-11-15T00:00:00Z |

### `iso_zone_prices_history`

The day-ahead or real-time price of one NYISO load zone, CAISO's ZP26 hub or SPP's South hub for one interval, a history from 2019.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1677533.

- **Time:** ts_utc is the start of the interval in UTC; day-ahead and NYISO's real-time are hourly, CAISO's real-time 15-minute.
- **Revisions:** Merged by (entity, variable, ts_utc); a month refetched after it ended replaces its rows. An interval the publisher's file does not hold is not written. vintage is the file's Last-Modified for NYISO, empty for CAISO and SPP.
- **Source:** caiso:PRC_INTVL_LMP OASIS Interval Locational Marginal Prices, real-time dispatch (RTD, 5-minute) (https://oasis.caiso.com/mrioasis/logon.do)
- **Source:** caiso:PRC_LMP OASIS Locational Marginal Prices, day-ahead market (DAM) (https://oasis.caiso.com/mrioasis/logon.do)
- **Source:** nyiso:damlbmp Day-Ahead Market LBMP, zonal (P-2A) (http://mis.nyiso.com/public/P-2Alist.htm)
- **Source:** nyiso:rtlbmp Time-Weighted/Integrated Real-Time LBMP, zonal, hourly (P-4A) (http://mis.nyiso.com/public/P-4Alist.htm)
- **Source:** spp:DA-LMP-SL Day-Ahead LMP by Settlement Location (https://portal.spp.org/pages/da-lmp-by-location)
- **Method note:** [`docs/methods/iso_zone_prices_history.md`](../methods/iso_zone_prices_history.md)
- **Cite as:** California Independent System Operator (CAISO); New York Independent System Operator (NYISO); Southwest Power Pool (SPP). Day-Ahead LMP by Settlement Location; Day-Ahead Market LBMP, zonal (P-2A); OASIS Interval Locational Marginal Prices, real-time dispatch (RTD, 5-minute); OASIS Locational Marginal Prices, day-ahead market (DAM); Time-Weighted/Integrated Real-Time LBMP, zonal, hourly (P-4A) [terms: "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site"; the notice forbids republishing "any image or video on this website as a stand-alone file", not data (https://www.nyiso.com/legal-notice, read 6 October 2026)]. Via the Energy Research Warehouse (ERW), table `iso_zone_prices_history`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: <iso>:<node>: nyiso:<zone> for NYISO's eleven load zones, caiso:TH_ZP26_GEN-APND, spp:SPPSOUTH_HUB | none | text | caiso:TH_ZP26_GEN-APND, nyiso:CAPITL, nyiso:CENTRL, nyiso:DUNWOD, nyiso:GENESE, nyiso:HUD VL, nyiso:LONGIL, nyiso:MHK VL, nyiso:MILLWD, nyiso:N.Y.C., nyiso:NORTH, nyiso:WEST, spp:SPPSOUTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T05:00:00Z to 2026-11-17T07:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1300.74 to 4630.5689; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is. Here: PT1H, or PT15M for CAISO's real-time rows | none | text | PT15M, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-CA, US-NY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: caiso_dam, caiso_rtm, nyiso_dam, nyiso_rtm or spp_dam: the grid's day-ahead or real-time market | none | text | caiso_dam, caiso_rtm, nyiso_dam, nyiso_rtm, spp_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: NYISO's eleven load zones (CAPITL, CENTRL, DUNWOD, GENESE, HUD VL, LONGIL, MHK VL, MILLWD, N.Y.C., NORTH, WEST), CAISO's ZP26 hub TH_ZP26_GEN-APND, SPP's South hub SPPSOUTH_HUB; no ISO-NE row | none | text | CAPITL, CENTRL, DUNWOD, GENESE, HUD VL, LONGIL, MHK VL, MILLWD, N.Y.C., NORTH, SPPSOUTH_HUB, TH_ZP26_GEN-APND, WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | caiso:PRC_INTVL_LMP, caiso:PRC_LMP, nyiso:damlbmp, nyiso:rtlbmp, spp:DA-LMP-SL | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example http://mis.nyiso.com/public/csv/damlbmp/20190101damlbmp_zone_csv.zip, http://mis.nyiso.com/public/csv/damlbmp/20190201damlbmp_zone_csv.zip, http://mis.nyiso.com/public/csv/damlbmp/20190301damlbmp_zone_csv.zip; 934 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T09:18:36Z to 2026-11-16T11:54:07Z; 3098 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: NYISO's file Last-Modified; empty on CAISO's and SPP's rows | none | utc time | 2019-01-30T14:34:03Z to 2026-11-16T11:07:14Z; 190 distinct | 175516 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `lmp_dam` | Day-ahead locational marginal price (NYISO's zonal LBMP), hourly | USD/MWh | 851856 | 2019-01-01T05:00:00Z | 2026-11-17T07:00:00Z |
| `lmp_rtm` | NYISO's own time-weighted integrated hourly real-time LBMP (report P-4A) | USD/MWh | 748297 | 2019-01-01T05:00:00Z | 2026-11-16T11:00:00Z |
| `lmp_rtm_15m_mean` | CAISO: real-time locational marginal price, the 15-minute mean of the 5-minute RTD prices, a quarter hour only when its three prices are held | USD/MWh | 77380 | 2024-09-01T07:00:00Z | 2026-11-16T07:45:00Z |

