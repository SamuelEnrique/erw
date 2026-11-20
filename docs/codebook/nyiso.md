# Codebook: nyiso

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 7 public tables (2 entities, 5 series; tiers: 7 source); 5 documented in full.

- [`nyiso_as_prices`](#nyiso_as_prices): NYISO's day-ahead price of one ancillary service (a reserve product or regulation) in one reserve region for one hour.
- [`nyiso_dam_cleared_energy`](#nyiso_dam_cleared_energy): NYISO, load scheduled in the day-ahead market by hour, system-wide (P-30, Day-Ahead Market Daily Energy Report, Total Load Scheduled) (session 136)
- [`nyiso_dam_zone_prices`](#nyiso_dam_zone_prices): NYISO's day-ahead zonal energy price (LBMP, the marginal price of energy at a location) of one of its eleven load zones for one hour.
- [`nyiso_interconnection_queue`](#nyiso_interconnection_queue): One position (a request, or a unit or phase of one) in NYISO's interconnection queue of generation, storage and transmission projects asking to connect to the grid.
- [`nyiso_load_queue`](#nyiso_load_queue): One request by a large electricity user (a data center, a factory and others) to connect its load to NYISO's grid, a row of the queue workbook's sheet Load Projects.
- [`nyiso_rtm_zone_prices`](#nyiso_rtm_zone_prices): NYISO's real-time zonal energy price (LBMP, the marginal price of energy at a location) of one of its eleven load zones, as a 15-minute time-weighted mean of its 5-minute (RTD) prices.
- [`nyiso_zone_load_hourly`](#nyiso_zone_load_hourly): NYISO, hourly load by zone, the integrated real-time actual load of its eleven load zones (P-58C, palIntegrated) (session 138)

### `nyiso_as_prices`

NYISO's day-ahead price of one ancillary service (a reserve product or regulation) in one reserve region for one hour.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 293376.

- **Time:** ts_utc is the start of the hour in UTC; operating days are America/New_York days.
- **Revisions:** Merged by (entity, variable, ts_utc); one run (4 October 2026) wrote every row and none has refreshed it since. vintage is not filled.
- **Source:** nyiso:damasp NYISO, Day-Ahead Market Ancillary Services Prices (P-5) (http://mis.nyiso.com/public/P-5list.htm)
- **Method note:** [`docs/methods/nyiso_as_prices.md`](../methods/nyiso_as_prices.md)
- **Cite as:** New York Independent System Operator (NYISO). Day-Ahead Market Ancillary Services Prices (P-5). Via the Energy Research Warehouse (ERW), table `nyiso_as_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: nyiso:<region>, the reserve region as NYISO's file names it | none | text | nyiso:CAPITL, nyiso:HUD VL, nyiso:LONGIL, nyiso:N.Y.C., nyiso:NYCA, nyiso:WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2024-09-01T04:00:00Z to 2026-10-05T03:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.35 to 757.66; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MW-hour | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-NY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: nyiso_dam in every row: NYISO's day-ahead market | none | text | nyiso_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The reserve region: five of NYISO's eleven load zones, one for each set of zones that can price reserves apart (CAPITL, HUD VL, LONGIL, N.Y.C., WEST; WEST also stands for GENESE, CENTRL, NORTH and MHK VL, HUD VL for MILLWD and DUNWOD), and NYCA, the whole control area, for regulation | none | text | CAPITL, HUD VL, LONGIL, N.Y.C., NYCA, WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nyiso:damasp | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example http://mis.nyiso.com/public/csv/damasp/20240901damasp_csv.zip, http://mis.nyiso.com/public/csv/damasp/20241001damasp_csv.zip, http://mis.nyiso.com/public/csv/damasp/20241101damasp_csv.zip; 26 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-04T03:33:06Z to 2026-10-04T04:09:33Z; 26 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 293376 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `as_price_dam_nsync10` | Day-ahead price of 10-minute non-synchronous reserve (NYISO's 10 Min Non-Synchronous Reserve), USD per MW held for one hour | USD/MW-hour | 91680 | 2024-09-01T04:00:00Z | 2026-10-05T03:00:00Z |
| `as_price_dam_op30` | Day-ahead price of 30-minute operating reserve (NYISO's 30 Min Operating Reserve), USD per MW held for one hour | USD/MW-hour | 91680 | 2024-09-01T04:00:00Z | 2026-10-05T03:00:00Z |
| `as_price_dam_reg` | Day-ahead price of regulation capacity for the whole control area (NYISO's NYCA Regulation Capacity), USD per MW held for one hour | USD/MW-hour | 18336 | 2024-09-01T04:00:00Z | 2026-10-05T03:00:00Z |
| `as_price_dam_spin10` | Day-ahead price of 10-minute spinning reserve (NYISO's 10 Min Spinning Reserve), USD per MW held for one hour | USD/MW-hour | 91680 | 2024-09-01T04:00:00Z | 2026-10-05T03:00:00Z |

### `nyiso_dam_cleared_energy`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 10441.

- **Source:** nyiso:damenergy New York ISO (NYISO), P-30, Day-Ahead Market Daily Energy Report (http://mis.nyiso.com/public/P-30list.htm)
- **Method note:** [`docs/methods/nyiso_dam_cleared_energy.md`](../methods/nyiso_dam_cleared_energy.md)
- **Cite as:** New York ISO (NYISO). P-30, Day-Ahead Market Daily Energy Report. Via the Energy Research Warehouse (ERW), table `nyiso_dam_cleared_energy`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | nyiso:system | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-09-01T04:00:00Z to 2026-11-17T04:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 31245.5; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-NY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | nyiso_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | Total Load Scheduled | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nyiso:damenergy | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | http://mis.nyiso.com/public/csv/damenergy/20250901DAM_energy_rep_csv.zip, http://mis.nyiso.com/public/csv/damenergy/20251001DAM_energy_rep_csv.zip, http://mis.nyiso.com/public/csv/damenergy/20251101DAM_energy_rep_csv.zip, http://mis.nyiso.com/public/csv/damenergy/20251201DAM_energy_rep_csv.zip, http://mis.nyiso.com/public/csv/damenergy/20260101DAM_energy_rep_csv.zip, http://mis.nyiso.com/public/csv/damenergy/20260201DAM_energy_rep_csv.zip, http://mis.nyiso.com/public/csv/damenergy/20260301DAM_energy_rep_csv.zip, http://mis.nyiso.com/public/csv/damenergy/20260401DAM_energy_rep_csv.zip, http://mis.nyiso.com/public/csv/damenergy/20260501DAM_energy_rep_csv.zip, http://mis.nyiso.com/public/csv/damenergy/20260601DAM_energy_rep_csv.zip, http://mis.nyiso.com/public/csv/damenergy/20260701DAM_energy_rep_csv.zip, http://mis.nyiso.com/public/csv/damenergy/20260801DAM_energy_rep_csv.zip, http://mis.nyiso.com/public/csv/damenergy/20260901DAM_energy_rep_csv.zip, http://mis.nyiso.com/public/csv/damenergy/20261001DAM_energy_rep_csv.zip, http://mis.nyiso.com/public/csv/damenergy/20261101DAM_energy_rep_csv.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T20:22:03Z, 2026-10-06T20:22:06Z, 2026-10-06T20:22:09Z, 2026-10-06T20:22:12Z, 2026-10-06T20:22:14Z, 2026-10-06T20:22:17Z, 2026-10-06T20:22:20Z, 2026-10-06T20:22:23Z, 2026-10-06T20:22:25Z, 2026-10-06T20:22:28Z, 2026-10-06T20:22:31Z, 2026-10-06T20:22:34Z, 2026-10-06T20:38:25Z, 2026-10-06T20:38:28Z, 2026-10-09T07:22:05Z, 2026-10-10T15:00:05Z, 2026-10-24T15:04:13Z, 2026-11-16T11:49:30Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 10441 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dam_cleared_energy` |  | MW | 10441 | 2025-09-01T04:00:00Z | 2026-11-17T04:00:00Z |

### `nyiso_dam_zone_prices`

NYISO's day-ahead zonal energy price (LBMP, the marginal price of energy at a location) of one of its eleven load zones for one hour.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 21395.

- **Time:** ts_utc is the start of the hour in UTC; operating days are America/New_York days.
- **Revisions:** Merged by (entity, variable, ts_utc); each operating day is read on several consecutive runs (as a forward day, then in the window) and the last read stands. vintage is the file's HTTP Last-Modified.
- **Source:** nyiso:damlbmp Day-Ahead Market LBMP, zonal (P-2A) (http://mis.nyiso.com/public/P-2Alist.htm)
- **Method note:** [`docs/methods/nyiso_dam_zone_prices.md`](../methods/nyiso_dam_zone_prices.md)
- **Cite as:** New York Independent System Operator (NYISO). Day-Ahead Market LBMP, zonal (P-2A). Via the Energy Research Warehouse (ERW), table `nyiso_dam_zone_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: nyiso:<zone>, the zone's NYISO name | none | text | nyiso:CAPITL, nyiso:CENTRL, nyiso:DUNWOD, nyiso:GENESE, nyiso:HUD VL, nyiso:LONGIL, nyiso:MHK VL, nyiso:MILLWD, nyiso:N.Y.C., nyiso:NORTH, nyiso:WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-08-26T04:00:00Z to 2026-11-17T04:00:00Z; 1945 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 14.2 to 142.18; 4910 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-NY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: nyiso_dam in every row: NYISO's day-ahead market | none | text | nyiso_dam | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: NYISO's name of the load zone, one of eleven: CAPITL, CENTRL, DUNWOD, GENESE, HUD VL, LONGIL, MHK VL, MILLWD, N.Y.C., NORTH, WEST | none | text | CAPITL, CENTRL, DUNWOD, GENESE, HUD VL, LONGIL, MHK VL, MILLWD, N.Y.C., NORTH, WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nyiso:damlbmp | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example http://mis.nyiso.com/public/csv/damlbmp/20260801damlbmp_zone_csv.zip, http://mis.nyiso.com/public/csv/damlbmp/20260901damlbmp_zone_csv.zip, http://mis.nyiso.com/public/csv/damlbmp/20260919damlbmp_zone.csv; 59 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-25T07:12:46Z to 2026-11-16T14:20:33Z; 55 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The HTTP Last-Modified of the day's file (report P-2A) | none | utc time | 2026-08-30T13:33:05Z to 2026-11-15T14:32:05Z; 59 distinct | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `lmp_dam` | Day-ahead zonal LBMP (the price of energy in the zone in the day-ahead market), as NYISO prints it | USD/MWh | 21395 | 2026-08-26T04:00:00Z | 2026-11-17T04:00:00Z |

### `nyiso_interconnection_queue`

One position (a request, or a unit or phase of one) in NYISO's interconnection queue of generation, storage and transmission projects asking to connect to the grid.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 1814.

- **Time:** No time column. Dates are NYISO's, YYYY-MM-DD; vintage is the retrieval day. The table is a snapshot of the queue as read on its retrieved_at.
- **Revisions:** A snapshot rewritten whole by each run (Mondays); earlier snapshots stay in the raw files and the archive.
- **Source:** nyiso:interconnection_queue NYISO NYISO Interconnection Queue (https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx)
- **Method note:** [`docs/methods/nyiso_interconnection_queue.md`](../methods/nyiso_interconnection_queue.md)
- **Cite as:** New York Independent System Operator (NYISO). NYISO Interconnection Queue. Via the Energy Research Warehouse (ERW), table `nyiso_interconnection_queue`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: nyiso_queue:<queue id>, with :<n> added where NYISO lists one queue id on several rows, n in NYISO's row order | none | text | for example nyiso_queue:0001, nyiso_queue:0002, nyiso_queue:0003; 1814 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 0 Highland Lake Rd - Wallkill, 114 Hartley Rd-Goshen, 117656 North Creek Solar+Storage; 1689 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> from NYISO's State; empty where the state is not one two-letter code (NY-NJ, NY-PA, Quebec) | none | text | US-CT, US-DE, US-NJ, US-NY, US-PA | 6 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 1814 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 1814 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: NYISO's requested capacity as gridstatus reads it (Capacity (MW)) | MW | number | 0.0 to 2620.0; 391 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: active, withdrawn or completed, mapped from iso_status | none | text | active, completed, withdrawn | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The withdrawn date of a withdrawn row, the actual in-service date of a completed row where NYISO gives one | none | date | 2002-03-31 to 2026-08-31; 238 distinct | 311 |
| `operator` | The operator or owner, as the publisher writes it. Here: The interconnecting entity as NYISO writes it | none | text | for example 174 Power Global Properties, 174 Power Global Properties, LLC, 1st Rochdale Coop Group; 850 distinct | 210 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nyiso:interconnection_queue | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-26T00:06:50Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The retrieval day at 00:00:00Z, not a date NYISO prints | none | utc time | 2026-09-26T00:00:00Z | 0 |
| `queue_id` | NYISO's queue number of the request, as printed (with leading zeros) (the source's name: Queue ID) | none | text | for example 0001, 0002, 0003; 1812 distinct | 0 |
| `county` | The county (or counties) of the project as NYISO writes it (the source's name: County) | none | text | for example Alb.-Col.-Dutch., Albany, Albany-Dutchess; 217 distinct | 83: NYISO gives no county |
| `state` | The state of the project as NYISO writes it (a two-letter code, a pair such as NY-NJ, or Quebec) (the source's name: State) | none | text | CT, DE, NJ, NY, NY-NJ, NY-PA, PA, Quebec | 0 |
| `poi` | The point of interconnection: the substation or line where the project would connect (the source's name: Interconnection Location) | none | text | for example (137563) EASTOVER - (137895) SCHAGHTICOKW, 1 Stanco Street Substation via a dedicated feeder from the project site, 1. Moses 230 kV substation 2. Haverstock 345 kV sub (new) 3. Massena 230 kV substation 4. Adirondack 345 kV sub (new) 5. Willis 230 kV substation 6. Ryan & Patnode 230 kV substations 7. Chases Lake 345 kV sub (new) 8. Marcy 345 kV sub 9. Edic 345 kV sub; 1459 distinct | 10: NYISO gives no location |
| `zone` | NYISO's load zone letter (A to K) of the project, several where the project spans zones, as NYISO writes it (the source's name: Zone) | none | text | for example A, A, B, A,E,J; 39 distinct | 363: NYISO gives no zone |
| `transmission_owner` | The transmission owner the project connects to, as NYISO writes it (several joined by /) (the source's name: Transmission Owner) | none | text | for example CHG&E, CHGE, CHGE/NM-NG/NYSEG; 77 distinct | 6: NYISO gives none |
| `fuel_technology` | The project's type in NYISO's words (Energy Storage, Solar, Wind, AC Transmission, DC Transmission and others) (the source's name: Generation Type) | none | text | =Solid Waste, AC Transmission, Combined Cycle, Combustion Turbine, DC Transmission, Dual Fuel, Energy Storage, Flywheel, Fuel Cell, Hydro, Methane, Natural Gas, Nuclear, Pumped Storage, Solar, Steam Turbine, Wind, Wood | 212: NYISO gives no type |
| `iso_status` | NYISO's own status of the request (Active, Withdrawn, Completed) (the source's name: Status) | none | text | Active, Completed, Withdrawn | 0 |
| `queue_date` | The date the request entered the queue (the source's name: Queue Date) | none | date | 1989-09-15 to 2026-08-25; 1104 distinct | 0 |
| `proposed_in_service_date` | The date the project proposes to begin operating (the source's name: Proposed Completion Date) | none | date | 2022-04-01 to 2033-12-01; 51 distinct | 1613: NYISO gives no proposed date |
| `actual_in_service_date` | The date the project began operating (the source's name: Actual Completion Date, In-Service Date or Op Date (gridstatus)) | none | date | 2002-03-31 to 2025-10-31; 67 distinct | 1682: Not in service, or no date given |
| `withdrawn_date` | The date the request was withdrawn (the source's name: Withdrawn Date) | none | date | 2006-03-31 to 2026-08-31; 224 distinct | 443: Not withdrawn, or withdrawn with no date given |

### `nyiso_load_queue`

One request by a large electricity user (a data center, a factory and others) to connect its load to NYISO's grid, a row of the queue workbook's sheet Load Projects.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 74.

- **Time:** No time column. Dates are as the sheet prints them (<x>_printed) and as YYYY-MM-DD where the cell is a full date (<x>_date); vintage is the retrieval date. A snapshot of the sheet as read on its retrieved_at.
- **Revisions:** A snapshot rewritten whole by each weekly run; earlier sheets stay in the archive and the raw files.
- **Source:** nyiso:load_queue NYISO Interconnection Queue workbook, sheets "Load Projects" and "Load Project Tracking" (https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx)
- **Method note:** [`docs/methods/nyiso_load_queue.md`](../methods/nyiso_load_queue.md)
- **Cite as:** New York Independent System Operator (NYISO). NYISO Interconnection Queue workbook, sheets "Load Projects" and "Load Project Tracking" (load interconnection requests) [terms: "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site"; the notice forbids republishing "any image or video on this website as a stand-alone file", not data (https://www.nyiso.com/legal-notice, read 7 October 2026); held internal from session 149: the notice confers no license and reserves all rights]. Via the Energy Research Warehouse (ERW), table `nyiso_load_queue`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: nyiso_load_queue:<Queue Number as printed> | none | text | for example nyiso_load_queue:0290A, nyiso_load_queue:0311, nyiso_load_queue:0359; 74 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The sheet's Project: Project Name | none | text | for example 1 Gig Data Center East Fishkill, NY, 1547 CSR - Orangeburg LLC, 580 STAMP load increase; 72 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> where the state is a two-letter code or a state's name | none | text | US-NJ, US-NY, US-PA | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 74 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 74 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: The sheet's Peak MW load as printed: the request's peak load, not a generator's capacity | MW | number | 14.38 to 1935.0; 43 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Read from the words of the sheet's key: withdrawn where they hold Withdrawn (code 0), completed only for In Service Commercial (14), active for every other code | none | text | active, completed, withdrawn | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: Empty in every row: the sheet prints no date of withdrawal or of entering service | none | empty | no cell holds a value | 74 |
| `operator` | The operator or owner, as the publisher writes it. Here: The sheet's Developer Name | none | text | for example Advance Albany County Alliance, Air Products and Chemicals Inc, Alcoa; 59 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nyiso:load_queue | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T09:09:14Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The retrieval date (YYYY-MM-DD) | none | date | 2026-10-07 | 0 |
| `workbook_last_modified` | The HTTP Last-Modified time of NYISO's workbook as retrieved, UTC | none | utc time | 2026-09-11T17:26:02Z | 0 |
| `sheet` | The workbook sheet the row is read from (Load Projects) | none | text | Load Projects | 0 |
| `sheet_row` | The row number on that sheet | none | integer | 2 to 75; 74 distinct | 0 |
| `queue_id` | NYISO's queue number of the request, as printed (the source's name: Queue Number) | none | text | for example 0290A, 0311, 0359; 74 distinct | 0 |
| `county` | The county of the request, as typed on the sheet (the source's name: County) | none | text | for example Albany, Broome, Cattaraugus; 32 distinct | 0 |
| `state` | The state of the request, as typed on the sheet (a code, or a name such as New York) (the source's name: State) | none | text | NJ, NY, New York, PA | 0 |
| `poi` | The point (or points) of interconnection: the substation or line where the load would connect (the source's name: Points of Interconnection) | none | text | for example 115 kv STAMP substation, 138-872 Holbrook to Sills Rd, 138kV Line 703 between Corporate Drive and Harings Corner; 68 distinct | 0 |
| `zone` | NYISO's load zone letter, A to K (the source's name: NYISO Zone) | none | text | A, B, C, D, E, F, G, H, K | 0 |
| `zone_entity` | The zone's id in the ERW's NYISO price and load tables (nyiso:WEST for A, nyiso:CENTRL for C and so on) | none | text | nyiso:CAPITL, nyiso:CENTRL, nyiso:GENESE, nyiso:HUD VL, nyiso:LONGIL, nyiso:MHK VL, nyiso:MILLWD, nyiso:NORTH, nyiso:WEST | 0 |
| `transmission_owner` | The connecting transmission owner or utility, as the sheet writes it (the source's name: CTO/Utility) | none | text | CONED, Central Hudson, ConEd, IMEU, LIPA, NM-NG, NYPA, NYSEG, National Grid, O&R | 0 |
| `affected_transmission_owner` | Other transmission owners the request affects, as the sheet writes them (the source's name: Affected Transmission Owner (ATO)) | none | text | NGRID, NYPA, NM-NG, NYSEG/RGE, NY Transco, LSPNY, CHGE, NYPA, NYPA ,National Grid, NYPA, NM-NG, NYSEG, NYSEG, Central Hudson, National Grid, National Grid, NYSEG, Transco, IMEU | 58: The sheet's cell is blank |
| `end_use` | NYISO's code of what the load is for (DAT, DAT-AI, DAT-CM, M-CG, M-CH, M-IN, RD, O) (the source's name: End-Use) | none | text | DAT, DAT-AI, DAT-CM, M-CG, M-CH, M-IN, O, RD | 23: The sheet's cell is blank |
| `end_use_words` | The words of the end-use code from the sheet's own key (Data Center (general), AI Datacenter, Cryptocurrency mining and others) | none | text | AI Datacenter, Consumable Goods, Cryptocurrency mining, Data Center (general), Industrial Goods, Microchip fabrication, Other, Research and Development | 23: No end-use code printed |
| `record_type` | The sheet's record type (Load Interconnection on every row) (the source's name: Record Type Name) | none | text | Load Interconnection | 0 |
| `type_fuel` | The sheet's Type/Fuel code (L on every row) (the source's name: Type/Fuel) | none | text | L | 0 |
| `iso_status` | NYISO's status code of the request as printed (0 to 14) (the source's name: Project Status #) | none | integer | 0, 1, 10, 12, 14, 4, 5, 6, 7, 8, 9 | 0 |
| `iso_status_words` | The words of the status code from the sheet's own key (Withdrawn, SRIS/SIS Pending, Under Construction, In Service Commercial and others) | none | text | Accepted Cost Allocation/IA in Progress, FS Pending, FS in Progress, In Service Commercial, Rejected Cost Allocation/Next FS Pending, SRIS/SIS Approved, SRIS/SIS Pending, SRIS/SIS in Progress, Scoping Meeting Pending, Under Construction, Withdrawn | 0 |
| `sis_bundle` | The System Impact Study (SIS) bundle the request is studied in, as the sheet prints it (25-1, 26-4, N/A and others) (the source's name: SIS Bundle) | none | text | 25-1, 25-2, 25-3, 26-1, 26-2, 26-3, 26-4, N/A | 36: The sheet's cell is blank |
| `availability_of_studies` | Which studies are available for the request, as the sheet prints it (SIS, FS, N/A) (the source's name: Availability of Studies) | none | text | N/A, SIS, SIS, FS | 53: The sheet's cell is blank |
| `queue_date_printed` | The date the request was submitted, as the sheet shows it (the source's name: IR Submission Date) | none | text | for example 01-22-20, 01-23-24, 01-29-26; 64 distinct | 0 |
| `queue_date` | The date the request was submitted, YYYY-MM-DD (the source's name: IR Submission Date) | none | date | 2005-11-02 to 2026-08-28; 61 distinct | 0 |
| `last_updated_printed` | The date NYISO last updated the request's row, as the sheet shows it (the source's name: Last Updated Date) | none | text | 01-14-00, 01-31-26, 02-28-11, 03-31-13, 03-31-25, 03-31-26, 04-30-13, 04-30-24, 04-30-25, 04-30-26, 05-31-25, 05-31-26, 06-30-26, 07-31-14, 07-31-22, 07-31-24, 07-31-26, 08-31-26, 09-30-26, 11-30-11, 12-31-25 | 2: The sheet's cell is blank |
| `last_updated_date` | The date NYISO last updated the request's row, YYYY-MM-DD (the source's name: Last Updated Date) | none | date | 1900-01-14, 2011-02-28, 2011-11-30, 2013-03-31, 2013-04-30, 2014-07-31, 2022-07-31, 2024-04-30, 2024-07-31, 2025-03-31, 2025-04-30, 2025-05-31, 2025-12-31, 2026-01-31, 2026-03-31, 2026-04-30, 2026-05-31, 2026-06-30, 2026-07-31, 2026-08-31, 2026-09-30 | 2: The cell is blank or not a full date |
| `ia_tender_printed` | The sheet's IA Tender Date as shown (the source's name: IA Tender Date) | none | empty | no cell holds a value | 74: Empty in every row: the sheet's cells are blank |
| `ia_tender_date` | The sheet's IA Tender Date, YYYY-MM-DD (the source's name: IA Tender Date) | none | empty | no cell holds a value | 74: Empty in every row: the sheet's cells are blank |
| `fs_completion_printed` | The sheet's FS Completion Date as shown (the source's name: FS Completion Date) | none | empty | no cell holds a value | 74: Empty in every row: the sheet's cells are blank |
| `fs_completion_date` | The sheet's FS Completion Date, YYYY-MM-DD (the source's name: FS Completion Date) | none | empty | no cell holds a value | 74: Empty in every row: the sheet's cells are blank |
| `proposed_initial_backfeed_printed` | The proposed initial backfeed date as the sheet prints it, month and year (11-2026) (the source's name: Proposed Initial Backfeed Date) | none | text | for example 01-2026, 01-2027, 01-2028; 32 distinct | 6: The sheet's cell is blank |
| `proposed_initial_backfeed_date` | The proposed initial backfeed date, YYYY-MM-DD where the cell holds a full date (the source's name: Proposed Initial Backfeed Date) | none | empty | no cell holds a value | 74: Empty in every row: the sheet prints month and year only |
| `proposed_initial_backfeed_month` | The proposed initial backfeed month, YYYY-MM, no day added (the source's name: Proposed Initial Backfeed Date) | none | text | for example 2025-06, 2025-08, 2026-01; 31 distinct | 10: The cell is blank or does not read as a month and year |

Waiting for a second look: type_fuel holds L on every row; what NYISO's code L stands for is not documented by the source as the repository holds it.; The sheet's abbreviations IA (in IA Tender Date) and FS (in FS Completion Date) are not spelled out in the repository's documents..

### `nyiso_rtm_zone_prices`

NYISO's real-time zonal energy price (LBMP, the marginal price of energy at a location) of one of its eleven load zones, as a 15-minute time-weighted mean of its 5-minute (RTD) prices.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 80300.

- **Time:** ts_utc is the start of the quarter hour in UTC; operating days are America/New_York days. NYISO stamps each price at its interval end; the connector weights each by its interval length and splits an interval at a quarter-hour boundary.
- **Revisions:** Merged by (entity, variable, ts_utc); a day read again in a later run's three-day window replaces its rows. vintage is the file's Last-Modified.
- **Source:** nyiso:realtime Real-Time Market LBMP, zonal, RTD 5-minute (P-24A) (http://mis.nyiso.com/public/P-24Alist.htm)
- **Method note:** [`docs/methods/nyiso_rtm_zone_prices.md`](../methods/nyiso_rtm_zone_prices.md)
- **Cite as:** New York Independent System Operator (NYISO). Real-Time Market LBMP, zonal, RTD 5-minute (P-24A). Via the Energy Research Warehouse (ERW), table `nyiso_rtm_zone_prices`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: nyiso:<zone>, the zone's NYISO name | none | text | nyiso:CAPITL, nyiso:CENTRL, nyiso:DUNWOD, nyiso:GENESE, nyiso:HUD VL, nyiso:LONGIL, nyiso:MHK VL, nyiso:MILLWD, nyiso:N.Y.C., nyiso:NORTH, nyiso:WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-08-26T04:00:00Z to 2026-11-16T04:45:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -599.4267 to 2840.39; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT15M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-NY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: nyiso_rtm in every row: NYISO's real-time market, its 5-minute RTD prices | none | text | nyiso_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: NYISO's name of the load zone, one of eleven: CAPITL, CENTRL, DUNWOD, GENESE, HUD VL, LONGIL, MHK VL, MILLWD, N.Y.C., NORTH, WEST | none | text | CAPITL, CENTRL, DUNWOD, GENESE, HUD VL, LONGIL, MHK VL, MILLWD, N.Y.C., NORTH, WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nyiso:realtime | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example http://mis.nyiso.com/public/csv/realtime/20260801realtime_zone_csv.zip, http://mis.nyiso.com/public/csv/realtime/20260901realtime_zone_csv.zip, http://mis.nyiso.com/public/csv/realtime/20260919realtime_zone.csv; 54 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-25T07:13:04Z to 2026-11-16T14:20:36Z; 75 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The Last-Modified of the day's file (report P-24A) | none | utc time | 2026-09-01T03:57:09Z to 2026-11-16T04:57:07Z; 54 distinct | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `lmp_rtm_15m_mean` | Real-time zonal LBMP (the price of energy in the zone in the real-time market), the 15-minute time-weighted mean of NYISO's 5-minute RTD prices, rounded to 4 decimals | USD/MWh | 80300 | 2026-08-26T04:00:00Z | 2026-11-16T04:45:00Z |

### `nyiso_zone_load_hourly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 757328.

- **Source:** nyiso:palIntegrated New York ISO (NYISO), P-58C, Integrated Real-Time Actual Load (palIntegrated) (http://mis.nyiso.com/public/P-58Clist.htm)
- **Method note:** [`docs/methods/nyiso_zone_load_hourly.md`](../methods/nyiso_zone_load_hourly.md)
- **Cite as:** New York ISO (NYISO). P-58C, Integrated Real-Time Actual Load (palIntegrated), by zone [terms: "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site"; the notice forbids republishing "any image or video on this website as a stand-alone file", not data (https://www.nyiso.com/legal-notice, read 6 October 2026)]. Via the Energy Research Warehouse (ERW), table `nyiso_zone_load_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | nyiso:CAPITL, nyiso:CENTRL, nyiso:DUNWOD, nyiso:GENESE, nyiso:HUD VL, nyiso:LONGIL, nyiso:MHK VL, nyiso:MILLWD, nyiso:N.Y.C., nyiso:NORTH, nyiso:WEST | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T05:00:00Z to 2026-11-16T10:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 140.9046 to 10830.2864; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-NY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | nyiso_load | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | CAPITL, CENTRL, DUNWOD, GENESE, HUD VL, LONGIL, MHK VL, MILLWD, N.Y.C., NORTH, WEST | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nyiso:palIntegrated | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example http://mis.nyiso.com/public/csv/palIntegrated/20190101palIntegrated_csv.zip, http://mis.nyiso.com/public/csv/palIntegrated/20190201palIntegrated_csv.zip, http://mis.nyiso.com/public/csv/palIntegrated/20190301palIntegrated_csv.zip; 95 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-07T01:42:03Z to 2026-11-16T11:50:50Z; 95 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2019-02-01T05:04:05Z to 2026-11-16T11:30:08Z; 95 distinct | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `load` |  | MW | 757328 | 2019-01-01T05:00:00Z | 2026-11-16T10:00:00Z |

