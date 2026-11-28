# Codebook: spp

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 6 public tables (1 entities, 5 series; tiers: 6 source); 5 documented in full.

- [`spp_as_prices`](#spp_as_prices): The day-ahead market clearing price of one operating reserve product, for one of SPP's two named reserve regions, for one hour.
- [`spp_as_quantities`](#spp_as_quantities): The MW of one operating reserve product cleared in SPP's day-ahead market for one hour, for one of the regions the file's BAA column names.
- [`spp_curtailment_daily`](#spp_curtailment_daily): The wind or solar energy SPP reports curtailed for one reason (or in all) in one balancing authority area on one day.
- [`spp_dam_cleared_energy`](#spp_dam_cleared_energy): The demand cleared in SPP's day-ahead market for one hour and one balancing authority area.
- [`spp_interconnection_queue`](#spp_interconnection_queue): One position in SPP's Generation Interconnection Queue summary, a project asking to connect generation or storage to SPP's grid.
- [`spp_mtlf_hourly`](#spp_mtlf_hourly): One hour of one SPP area (the footprint, or its western area) as one daily publication of SPP's mid-term load forecast file printed it: the forecast for the hour, or the averaged actual load beside it.

### `spp_as_prices`

The day-ahead market clearing price of one operating reserve product, for one of SPP's two named reserve regions, for one hour.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 159432.

- **Time:** ts_utc is the start of the hour in UTC (SPP's GMTIntervalEnd less one hour); operating days are Central (America/Chicago) days.
- **Revisions:** Merged by (entity, variable, ts_utc), a day already in the raw files is not asked again; one run (4 October 2026) wrote every row and none has refreshed it since. vintage is not filled.
- **Source:** spp:DA-MCP SPP, Day-Ahead Market Clearing Prices (MCP) for operating reserve (https://portal.spp.org/pages/da-mcp)
- **Method note:** [`docs/methods/spp_as_prices.md`](../methods/spp_as_prices.md)
- **Cite as:** Southwest Power Pool (SPP). Day-Ahead Market Clearing Prices (MCP) for operating reserve. Via the Energy Research Warehouse (ERW), table `spp_as_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: spp:SPP (every file) or spp:SWPW (files from 2026-04-01), the reserve region the file names; SPP's file does not spell out SWPW, which EIA's 930 reference tables name the Southwest Power Pool West Balancing Authority Area, active from 1 April 2026 (EIA930_Reference_Tables.xlsx sheet BAs, saved under warehouse/raw/eia930_reference, read 2026-11-20) | none | text | spp:SPP, spp:SWPW | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2024-09-01T05:00:00Z to 2026-10-04T04:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 447.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MW-hour | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: The same list of fourteen states in every row (SPP's footprint), whatever the region | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: spp_dam in every row: SPP's day-ahead market | none | text | spp_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The reserve region as SPP's file names it, SPP or SWPW; SPP's numbered reserve zones are not held | none | text | SPP, SWPW | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | spp:DA-MCP | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://portal.spp.org/file-browser-api/download/da-mcp?path=/2024/2024.zip, https://portal.spp.org/file-browser-api/download/da-mcp?path=/2025/01/DA-MCP-202501010100.csv, https://portal.spp.org/file-browser-api/download/da-mcp?path=/2025/01/DA-MCP-202501020100.csv; 642 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-04T03:33:35Z to 2026-10-04T03:56:53Z; 642 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 159432 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `as_price_dam_rampdn` | Day-ahead clearing price of ramp capability down (SPP's RampDN), USD per MW held for one hour; 0.0 in every hour held | USD/MW-hour | 22776 | 2024-09-01T05:00:00Z | 2026-10-04T04:00:00Z |
| `as_price_dam_rampup` | Day-ahead clearing price of ramp capability up (SPP's RampUP), USD per MW held for one hour | USD/MW-hour | 22776 | 2024-09-01T05:00:00Z | 2026-10-04T04:00:00Z |
| `as_price_dam_regdn` | Day-ahead clearing price of regulation down (SPP's RegDN), USD per MW held for one hour | USD/MW-hour | 22776 | 2024-09-01T05:00:00Z | 2026-10-04T04:00:00Z |
| `as_price_dam_regup` | Day-ahead clearing price of regulation up (SPP's RegUP), USD per MW held for one hour | USD/MW-hour | 22776 | 2024-09-01T05:00:00Z | 2026-10-04T04:00:00Z |
| `as_price_dam_spin` | Day-ahead clearing price of spinning reserve (SPP's Spin), USD per MW held for one hour | USD/MW-hour | 22776 | 2024-09-01T05:00:00Z | 2026-10-04T04:00:00Z |
| `as_price_dam_supp` | Day-ahead clearing price of supplemental reserve (SPP's Supp), USD per MW held for one hour | USD/MW-hour | 22776 | 2024-09-01T05:00:00Z | 2026-10-04T04:00:00Z |
| `as_price_dam_uncup` | Day-ahead clearing price of uncertainty reserve up (SPP's UncUP), USD per MW held for one hour | USD/MW-hour | 22776 | 2024-09-01T05:00:00Z | 2026-10-04T04:00:00Z |

### `spp_as_quantities`

The MW of one operating reserve product cleared in SPP's day-ahead market for one hour, for one of the regions the file's BAA column names.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 159768.

- **Time:** ts_utc is the start of the hour in UTC (the file's GMTIntervalEnd less one hour); operating days are Central (America/Chicago) days.
- **Revisions:** Merged by (entity, variable, ts_utc); each run reads every day from 1 September 2024 again, from the raw files where a day's file is saved (a saved file is never asked again). A (region, product, day) is written only when every hour of the day is there. vintage is not filled.
- **Source:** spp:DA-MC SPP, Day-Ahead Market Clearing (operating reserve cleared, by hour) (https://portal.spp.org/pages/market-clearing)
- **Method note:** [`docs/methods/spp_as_quantities.md`](../methods/spp_as_quantities.md)
- **Cite as:** Southwest Power Pool (SPP). Day-Ahead Market Clearing (operating reserve cleared, by hour). Via the Energy Research Warehouse (ERW), table `spp_as_quantities`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: spp:SPP (every file) or spp:SWPW (files from 2026-04-01), the file's BAA column; SPP's file does not spell out SWPW, which EIA's 930 reference tables name the Southwest Power Pool West Balancing Authority Area, active from 1 April 2026 (EIA930_Reference_Tables.xlsx sheet BAs, saved under warehouse/raw/eia930_reference, read 2026-11-20) | none | text | spp:SPP, spp:SWPW | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2024-09-01T05:00:00Z to 2026-10-05T04:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 0 to 4970; 3008 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: The same list of fourteen states in every row (SPP's footprint), whatever the region | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: spp_dam in every row: SPP's day-ahead market | none | text | spp_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The region as the file's BAA column names it, SPP or SWPW | none | text | SPP, SWPW | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | spp:DA-MC | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://portal.spp.org/file-browser-api/download/market-clearing?path=/2024/2024.zip, https://portal.spp.org/file-browser-api/download/market-clearing?path=/2025/01/DA-MC-202501010100.csv, https://portal.spp.org/file-browser-api/download/market-clearing?path=/2025/01/DA-MC-202501020100.csv; 643 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-04T11:32:49Z to 2026-10-04T11:50:47Z; 642 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 159768 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `quantity_mw_dam_rampdn` | MW of the ramp capability product RampDN (SPP's column RampDN) cleared in the day-ahead market for the hour | MW | 22824 | 2024-09-01T05:00:00Z | 2026-10-05T04:00:00Z |
| `quantity_mw_dam_rampup` | MW of the ramp capability product RampUP (SPP's column RampUP) cleared in the day-ahead market for the hour | MW | 22824 | 2024-09-01T05:00:00Z | 2026-10-05T04:00:00Z |
| `quantity_mw_dam_regdn` | MW of Regulation Down (SPP's column RegDN) cleared in the day-ahead market for the hour | MW | 22824 | 2024-09-01T05:00:00Z | 2026-10-05T04:00:00Z |
| `quantity_mw_dam_regup` | MW of Regulation Up (SPP's column RegUP) cleared in the day-ahead market for the hour | MW | 22824 | 2024-09-01T05:00:00Z | 2026-10-05T04:00:00Z |
| `quantity_mw_dam_spin` | MW of Spinning Reserve (SPP's column Spin) cleared in the day-ahead market for the hour | MW | 22824 | 2024-09-01T05:00:00Z | 2026-10-05T04:00:00Z |
| `quantity_mw_dam_supp` | MW of Supplemental Reserve (SPP's column Supp) cleared in the day-ahead market for the hour | MW | 22824 | 2024-09-01T05:00:00Z | 2026-10-05T04:00:00Z |
| `quantity_mw_dam_uncup` | MW of the uncertainty product UncUP (SPP's column UncUP) cleared in the day-ahead market for the hour | MW | 22824 | 2024-09-01T05:00:00Z | 2026-10-05T04:00:00Z |

### `spp_curtailment_daily`

The wind or solar energy SPP reports curtailed for one reason (or in all) in one balancing authority area on one day.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 38800.

- **Time:** ts_utc is the Central (America/Chicago) date of the 5-minute intervals' starts, at 00:00:00Z.
- **Revisions:** Merged by (entity, variable, ts_utc) into the table held; the daily run re-reads the 10 days before today, so SPP's changes to those days replace the old rows. vintage is not filled.
- **Source:** spp:ver_curtailments VER Curtailments (5-minute, by BAA), https://portal.spp.org/pages/ver-curtailments (files (https://portal.spp.org/file-browser-api/download/ver-curtailments)
- **Method note:** [`docs/methods/spp_curtailment_daily.md`](../methods/spp_curtailment_daily.md)
- **Cite as:** Southwest Power Pool (SPP). VER Curtailments (5-minute, by BAA). Via the Energy Research Warehouse (ERW), table `spp_curtailment_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: The balancing authority area: spp:SPP, or spp:SWPW (SPP's western area, in the files since SPP's western expansion); older files with no area column are SPP's | none | text | spp:SPP, spp:SWPW | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2014-03-01T00:00:00Z to 2026-11-15T00:00:00Z; 4642 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 225848.743; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 38800 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 38800 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 38800 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | spp:ver_curtailments | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://portal.spp.org/file-browser-api/download/ver-curtailments?path=/2014/2014.zip, https://portal.spp.org/file-browser-api/download/ver-curtailments?path=/2015/2015.zip, https://portal.spp.org/file-browser-api/download/ver-curtailments?path=/2016/2016.zip; 695 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-27T08:42:33Z to 2026-11-16T14:50:06Z; 32 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 38800 |

Variables (8):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `curtailed_solar_economic_mwh` | Solar energy SPP reports 'curtailed for energy' (economic dispatch) in the day, MWh | MWh | 4850 | 2014-03-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `curtailed_solar_manual_mwh` | Solar energy curtailed by manual operator instruction in the day, MWh | MWh | 4850 | 2014-03-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `curtailed_solar_mwh` | Solar energy curtailed in the day, the sum of redispatch, manual and economic, MWh | MWh | 4850 | 2014-03-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `curtailed_solar_redispatch_mwh` | Solar energy curtailed by redispatch (congestion) in the day, MWh (5-minute MW x 5/60, summed) | MWh | 4850 | 2014-03-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `curtailed_wind_economic_mwh` | Wind energy SPP reports 'curtailed for energy' (economic dispatch) in the day, MWh | MWh | 4850 | 2014-03-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `curtailed_wind_manual_mwh` | Wind energy curtailed by manual operator instruction in the day, MWh | MWh | 4850 | 2014-03-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `curtailed_wind_mwh` | Wind energy curtailed in the day, the sum of redispatch, manual and economic, MWh | MWh | 4850 | 2014-03-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `curtailed_wind_redispatch_mwh` | Wind energy curtailed by redispatch (congestion) in the day, MWh (5-minute MW x 5/60, summed) | MWh | 4850 | 2014-03-01T00:00:00Z | 2026-11-15T00:00:00Z |

### `spp_dam_cleared_energy`

The demand cleared in SPP's day-ahead market for one hour and one balancing authority area.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 16178.

- **Time:** ts_utc is the hour's start in UTC.
- **Revisions:** Merged by (entity, variable, ts_utc); an hour read again replaces the one held, and the table keeps days SPP's window no longer covers. vintage is not filled.
- **Source:** spp:DA-MC:cleared Southwest Power Pool (SPP), Marketplace portal, Market Clearing, day-ahead files (DA-MC), cleared demand (https://portal.spp.org/pages/market-clearing)
- **Method note:** [`docs/methods/spp_dam_cleared_energy.md`](../methods/spp_dam_cleared_energy.md)
- **Cite as:** Southwest Power Pool (SPP). Marketplace portal, Market Clearing, day-ahead files (DA-MC), cleared demand. Via the Energy Research Warehouse (ERW), table `spp_dam_cleared_energy`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: spp:SPP, or spp:SWPW from 1 April 2026 when the file names two areas; before it one row an hour, written as spp:SPP. SPP's file does not spell out SWPW, which EIA's 930 reference tables name the Southwest Power Pool West Balancing Authority Area, active from 1 April 2026 (EIA930_Reference_Tables.xlsx sheet BAs, saved under warehouse/raw/eia930_reference, read 2026-11-20) | none | text | spp:SPP, spp:SWPW | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-09-01T05:00:00Z to 2026-11-18T05:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1934.3 to 61332.1; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: The same list of fourteen states in every row (SPP's footprint), whatever the area | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: spp_dam in every row: SPP's day-ahead market | none | text | spp_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Total Demand in every row: SPP's column read, not a place | none | text | Total Demand | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | spp:DA-MC:cleared | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://portal.spp.org/file-browser-api/download/market-clearing?path=/2025/09/DA-MC-202509010100.csv, https://portal.spp.org/file-browser-api/download/market-clearing?path=/2025/09/DA-MC-202509020100.csv, https://portal.spp.org/file-browser-api/download/market-clearing?path=/2025/09/DA-MC-202509030100.csv; 443 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-04T11:40:59Z to 2026-11-17T08:40:15Z; 442 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 16178 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dam_cleared_energy` | SPP's column Total Demand for the hour and the balancing authority area, MW over the hour (Market Clearing, DA-MC files) | MW | 16178 | 2025-09-01T05:00:00Z | 2026-11-18T05:00:00Z |

### `spp_interconnection_queue`

One position in SPP's Generation Interconnection Queue summary, a project asking to connect generation or storage to SPP's grid.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 3079.

- **Time:** No time column. Dates are SPP's, YYYY-MM-DD; vintage is the retrieval day. The table is a snapshot of the queue as read on its retrieved_at.
- **Revisions:** A snapshot rewritten whole by each run (Mondays); earlier snapshots stay in the raw files and the archive.
- **Source:** spp:interconnection_queue SPP Generation Interconnection Queue summary (https://opsportal.spp.org/Studies/GenerateSummaryCSV)
- **Method note:** [`docs/methods/spp_interconnection_queue.md`](../methods/spp_interconnection_queue.md)
- **Cite as:** Southwest Power Pool (SPP). Generation Interconnection Queue summary. Via the Energy Research Warehouse (ERW), table `spp_interconnection_queue`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: spp_queue:<GEN number> | none | text | for example spp_queue:2017-G2, spp_queue:2018-G6, spp_queue:2019-G1; 3079 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: project in every row | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it. Here: Empty in every row | none | empty | no cell holds a value | 3079 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> from SPP's state; empty where no single two-letter state is given (one row has TX/OK) | none | text | US-AR, US-AZ, US-CO, US-IA, US-KS, US-LA, US-MN, US-MO, US-MT, US-ND, US-NE, US-NM, US-OK, US-SD, US-TX, US-WY | 27 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 3079 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 3079 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: SPP's requested capacity as gridstatus reads it | MW | number | 0.0 to 4000.0; 642 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: active, withdrawn, completed or suspended, mapped from SPP's status (IA FULLY EXECUTED/ON SUSPENSION is suspended); empty on 34 rows with no status in SPP's file | none | text | active, completed, suspended, withdrawn | 34 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The withdrawn date of a withdrawn row, the commercial operation date of a completed row where given | none | date | 2002-01-01 to 2026-10-19; 749 distinct | 1264 |
| `operator` | The operator or owner, as the publisher writes it. Here: Empty in every row | none | empty | no cell holds a value | 3079 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | spp:interconnection_queue | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://opsportal.spp.org/Studies/GenerateSummaryCSV | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-05T23:22:47Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The retrieval day (YYYY-MM-DD), not a date SPP prints | none | date | 2026-11-05 | 0 |
| `queue_id` | SPP's GEN number of the request (2019-G1, GEN-2023-172 and others) (the source's name: Queue ID) | none | text | for example 2017-G2, 2018-G6, 2019-G1; 3079 distinct | 0 |
| `county` | The county or place of the project as SPP writes it (the source's name: County) | none | text | for example 8 Sites, Aberdeen, Abernathy; 949 distinct | 28: SPP gives no county |
| `state` | The state of the project as SPP writes it (a two-letter code, or a pair such as TX/OK) (the source's name: State) | none | text | AR, AZ, CO, IA, KS, LA, MN, MO, MT, ND, NE, NM, OK, SD, TX, TX/OK, WY | 26: SPP gives no state |
| `poi` | The point of interconnection: the substation or line where the project would connect (the source's name: Interconnection Location) | none | text | for example 115 kV Fort Dodge Substation, 115kV Monolith Substation, 115kV North Fort Dodge Substation; 1885 distinct | 424: SPP gives no location |
| `zone` | The zone of the project (the source's name: Zone) | none | empty | no cell holds a value | 3079: Empty in every row: SPP's file does not give it |
| `transmission_owner` | The transmission owner the project connects to, SPP's code (SPS, OGE, AEP, NPPD, WERE and others) (the source's name: Transmission Owner) | none | text | for example AECC, AECI, AEP; 74 distinct | 99: SPP gives none |
| `fuel_technology` | The project's generation type in SPP's words (Wind, Solar, Battery/Storage, Hybrid - Solar/Storage, Thermal - Gas and others, some under two spellings) (the source's name: Generation Type) | none | text | for example Battery/Storage, Battery/Storage - Battery, Hybrid; 44 distinct | 11: SPP gives no type |
| `iso_status` | SPP's own status of the request, its Status (Original) text (DISIS STAGE, IA PENDING, IA FULLY EXECUTED/COMMERCIAL OPERATION, WITHDRAWN and others) (the source's name: Status (Original)) | none | text | DISIS STAGE, FACILITY STUDY STAGE, IA FULLY EXECUTED/COMMERCIAL OPERATION, IA FULLY EXECUTED/ON SCHEDULE, IA FULLY EXECUTED/ON SUSPENSION, IA PENDING, ICS, SPECIAL STUDY, TERMINATED, WITHDRAWN | 34: No status in SPP's file (affected-system requests) |
| `queue_date` | The date the request entered the queue (the source's name: Queue Date) | none | date | 1999-09-20 to 2026-09-09; 916 distinct | 47: SPP gives no queue date |
| `proposed_in_service_date` | The date the project proposes to begin operating (the source's name: Proposed Completion Date) | none | date | 2002-01-01 to 2035-02-01; 582 distinct | 1110: SPP gives no date |
| `actual_in_service_date` | SPP's Commercial Operation Date, which equals proposed_in_service_date on every row (not a completed project's date; some lie in the future) (the source's name: Commercial Operation Date) | none | date | 2002-01-01 to 2035-02-01; 582 distinct | 1110: SPP gives no date |
| `withdrawn_date` | The date the request was withdrawn (the source's name: Withdrawn Date) | none | date | 2002-03-04 to 2026-10-19; 534 distinct | 1562: Not withdrawn, or withdrawn with no date given |

### `spp_mtlf_hourly`

One hour of one SPP area (the footprint, or its western area) as one daily publication of SPP's mid-term load forecast file printed it: the forecast for the hour, or the averaged actual load beside it.

Shape: series. Keys: `entity`, `variable`, `ts_utc`, `vintage`. License: public; tier: source. Rows read on 2026-11-28: 1073626.

- **Time:** ts_utc is the hour's start, UTC (SPP's GMT hour ending less one hour; in the early files, which give only central time, placed by row order). vintage is the hour the file was published (09:00 central time), UTC.
- **Revisions:** Revisions kept: one row per publication (vintage), so a forecast once made is never replaced and each publication's actuals stand as printed. The key is entity, variable, ts_utc and vintage.
- **Source:** spp:MTLF-VS-ACTUAL Southwest Power Pool (SPP), Marketplace portal, Mid-Term Load Forecast vs Actual (https://portal.spp.org/pages/mtlf-vs-actual)
- **Method note:** [`docs/methods/spp_mtlf.md`](../methods/spp_mtlf.md)
- **Cite as:** Southwest Power Pool (SPP). Mid-Term Load Forecast vs Actual (MTLF). Via the Energy Research Warehouse (ERW), table `spp_mtlf_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | spp:SPP, spp:SWPW | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2013-06-28T14:00:00Z to 2026-12-04T14:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 113.0 to 59416.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1073626 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 1073626 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | spp:MTLF-VS-ACTUAL | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://portal.spp.org/file-browser-api/download/mtlf-vs-actual?path=/2013/2013.zip, https://portal.spp.org/file-browser-api/download/mtlf-vs-actual?path=/2014/2014.zip, https://portal.spp.org/file-browser-api/download/mtlf-vs-actual?path=/2015/2015.zip; 707 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-28T09:10:37Z, 2026-11-28T10:09:44Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2013-06-29T14:00:00Z to 2026-11-27T15:00:00Z; 4887 distinct | 0 |
| `x_horizon_hours` | Hours from the file's publication to the hour's start; negative for an hour already past (an actual) | h | integer | -25 to 167; 193 distinct | 0 |
| `x_interval_end_cpt` | SPP's own label of the hour: its hour ending in central prevailing time, as printed |  | text | for example 01/01/2014 00:00:00, 01/01/2014 01:00:00, 01/01/2014 02:00:00; more than 5000 distinct | 0 |
| `x_file` | The file read, OP-MTLF-<YYYYMMDDHH00>.csv (the publication's hour in central prevailing time) |  | text | for example OP-MTLF-201306290900.csv, OP-MTLF-201306300900.csv, OP-MTLF-201307010900.csv; 4887 distinct | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `load_actual_mw` | SPP's averaged actual load for the hour, MW, as printed beside the forecast | MW | 132894 | 2013-06-28T14:00:00Z | 2026-11-27T14:00:00Z |
| `load_forecast_mtlf_mw` | SPP's mid-term load forecast (MTLF) for the hour, MW, as published | MW | 940732 | 2013-06-28T14:00:00Z | 2026-12-04T14:00:00Z |

