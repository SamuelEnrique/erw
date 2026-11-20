# Codebook: interconnection

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 5 public tables (2 entities, 3 series; tiers: 5 derived); 5 documented in full.

- [`interconnection_agreements_by_grid`](#interconnection_agreements_by_grid): One grid's (or one grid and fuel's) count, MW or share of interconnection requests still in the queue with a signed interconnection agreement, at the end of 2025 or in one year of agreement, from Berkeley Lab's Queued Up file.
- [`interconnection_agreements_signed`](#interconnection_agreements_signed): One interconnection request still in the queue (active or suspended) that has a signed interconnection agreement (study phase IA Executed, or an agreement date) and gives no operation date, from Berkeley Lab and GridTracker's Queued Up, 2026 edition (through 2025).
- [`interconnection_durations`](#interconnection_durations): One interconnection request that reached operation and gives both a request date and an operation date, with the months between them, from Berkeley Lab's Queued Up file (2026 edition, through 2025).
- [`interconnection_durations_summary`](#interconnection_durations_summary): One grid's (or the whole US's) measure of how long the interconnection requests that began operating in one year took from request to operation, from Berkeley Lab and GridTracker's Queued Up, 2026 edition (through 2025).
- [`interconnection_queue_summary`](#interconnection_queue_summary): One grid and technology's count, MW, share or median of interconnection requests, by year entered, by year operation began, or for the whole file, from Berkeley Lab's Queued Up file (2026 edition).

### `interconnection_agreements_by_grid`

One grid's (or one grid and fuel's) count, MW or share of interconnection requests still in the queue with a signed interconnection agreement, at the end of 2025 or in one year of agreement, from Berkeley Lab's Queued Up file.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 438.

- **Time:** ts_utc is 2025-01-01 for the queue at the end of 2025, or the first day of the year of agreement for the _in_year variables (a year, not an instant); freq P1Y.
- **Revisions:** Rewritten whole by each run of the builder (warehouse/derived/interconnection_agreements.py) from lbnl_interconnection_queue; vintage is not filled.
- **Source:** lbnl:queued_up Lawrence Berkeley National Laboratory and GridTracker, Queued Up data file (https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics)
- **Method note:** [`docs/methods/interconnection_agreements.md`](../methods/interconnection_agreements.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Generation with a signed interconnection agreement, from Berkeley Lab's Queued Up file (docs/methods/interconnection_agreements.md). Via the Energy Research Warehouse (ERW), table `interconnection_agreements_by_grid`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: interconnection_agreements:<grid> (the seven ISOs, west, southeast, us) or interconnection_agreements:<grid>:<fuel> | none | text | for example interconnection_agreements:caiso, interconnection_agreements:caiso:battery, interconnection_agreements:caiso:gas_battery; 118 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2002-01-01T00:00:00Z, 2004-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.0 to 2001973.87; 283 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always US | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 438 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The grid, or the grid and fuel, in words (CAISO, Battery), not a pricing node | none | text | for example CAISO, CAISO, Battery, CAISO, Gas+Battery; 118 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:interconnection_agreements | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://eta-publications.lbl.gov/sites/default/files/2026-05/lbnl_ix_queue_data_file_thru2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T09:16:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 438 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `active_mw` | The MW of every request still in the queue | MW | 10 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `active_projects` | Every request still in the queue (active or suspended), count | count | 10 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `mw_signed` | The MW of those requests | MW | 118 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `mw_signed_in_year` | The MW of requests whose agreement date falls in the year | MW | 86 | 2002-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `projects_signed` | Requests still in the queue (active or suspended) with a signed interconnection agreement and no operation date, count | count | 118 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `projects_signed_in_year` | Requests whose agreement date falls in the year, count (requests that give an agreement date) | count | 86 | 2002-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `signed_share_pct` | Signed MW over the MW still in the queue, percent | pct | 10 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `interconnection_agreements_signed`

One interconnection request still in the queue (active or suspended) that has a signed interconnection agreement (study phase IA Executed, or an agreement date) and gives no operation date, from Berkeley Lab and GridTracker's Queued Up, 2026 edition (through 2025).

Shape: entities. Keys: `entity_id`. License: public; tier: derived. Rows read on 2026-11-20: 2522.

- **Time:** No time column; status_date is the agreement date where the file gives one. vintage is the edition, as text.
- **Revisions:** Rebuilt whole from lbnl_interconnection_queue by each run of the builder; one edition.
- **Source:** lbnl:queued_up Lawrence Berkeley National Laboratory and GridTracker, Queued Up data file (https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics)
- **Method note:** [`docs/methods/interconnection_agreements.md`](../methods/interconnection_agreements.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Generation with a signed interconnection agreement, from Berkeley Lab's Queued Up file (docs/methods/interconnection_agreements.md). Via the Energy Research Warehouse (ERW), table `interconnection_agreements_signed`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: The queue table's own entity_id (lbnl:<Berkeley Lab's entity>:<q_id>) | none | text | for example lbnl:AEC:GI-101, lbnl:AEC:GI-102, lbnl:AEC:GI-103; 2522 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always project | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 1, 1008, 11; 2428 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>; empty where the file gives no state | none | text | for example US-AL, US-AR, US-AZ; 49 distinct | 5 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 2522 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 2522 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: The request's MW, as the queue table gives it | MW | number | -27.0 to 4357.4; 1008 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Berkeley Lab's status: active or suspended | none | text | active, suspended | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The agreement date (ia_date) where given, else empty | none | date | 2002-06-10 to 2025-12-31; 785 distinct | 1146 |
| `operator` | The operator or owner, as the publisher writes it | none | text | for example AEC, AEP, AMEREN ILLINOIS; 133 distinct | 680 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:interconnection_agreements | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://eta-publications.lbl.gov/sites/default/files/2026-05/lbnl_ix_queue_data_file_thru2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T09:16:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The edition as text ('2026 edition (through 2025)'), not a UTC time | none | text | 2026 edition (through 2025) | 0 |
| `queue_id` | The request's queue identifier as Berkeley Lab's file gives it (q_id) (the source's name: q_id) | none | text | for example 1, 1002, 1003; 2499 distinct | 0 |
| `grid` | Berkeley Lab's region: the seven ISOs, West and Southeast (outside the ISOs) (the source's name: region) | none | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP, Southeast, West | 0 |
| `state` | The state as the file gives it, two-letter postal code | none | text | for example AL, AR, AZ; 49 distinct | 5: The file gives no state |
| `county` | The county as the file gives it | none | text | for example Acadia Parish, Accomack, Ada; 758 distinct | 13: The file gives no county |
| `utility` | The file's own utility field | none | text | for example AEC, AEP, AMEREN ILLINOIS; 133 distinct | 680: The file names no utility |
| `transmission_provider` | The transmission provider whose queue holds the request (Berkeley Lab's entity field) (the source's name: entity) | none | text | for example AEC, APS, Avista; 37 distinct | 0 |
| `fuel` | Berkeley Lab's clean type of the request (Solar, Battery, Gas, Wind, Solar+Battery and the others) (the source's name: type_clean) | none | text | Battery, Coal, Diesel, Gas, Gas+Battery, Gas+Diesel, Gas+Oil, Geothermal, Hydro, Hydro+Battery, Nuclear, Offshore Wind, Oil, Other, Other Storage, Other+Battery, Solar, Solar+Battery, Solar+Gas+Battery, Solar+Geothermal, Solar+Other, Solar+Wind+Battery, Wind, Wind+Battery | 0 |
| `ia_date` | The date of the signed interconnection agreement | none | date | 2002-06-10 to 2025-12-31; 785 distinct | 1146: The file gives no agreement date (the request is counted by its IA Executed phase) |
| `ia_phase` | The request's study phase as the file gives it (IA Executed meaning a signed agreement; other phases on rows counted by their agreement date) (the source's name: IA_phase_clean) | none | text | Cluster Study, Construction, Facility Study, IA Executed, IA Pending, In Progress (unknown study), Suspended, System Impact Study | 11: The file gives no phase |
| `request_date` | The date the request entered the queue (the source's name: q_date) | none | date | 2001-02-06 to 2025-11-05; 1003 distinct | 33: The file gives no request date |
| `proposed_date` | The request's proposed operation date (the source's name: prop_date) | none | date | 1990-12-03 to 2036-12-31; 836 distinct | 24: The file gives no proposed date |
| `signed_by` | Which mark counts the request as signed: phase (study phase IA Executed), date (an agreement date) or phase+date (both) | none | text | date, phase, phase+date | 0 |

### `interconnection_durations`

One interconnection request that reached operation and gives both a request date and an operation date, with the months between them, from Berkeley Lab's Queued Up file (2026 edition, through 2025).

Shape: entities. Keys: `entity_id`. License: public; tier: derived. Rows read on 2026-11-20: 3098.

- **Time:** No time column; status_date is the operation date. vintage is the edition ('2026 edition (through 2025)').
- **Revisions:** Rewritten whole by each run of the builder (warehouse/derived/interconnection_durations.py) from lbnl_interconnection_queue, one edition.
- **Source:** lbnl:queued_up Lawrence Berkeley National Laboratory and GridTracker, Queued Up data file (https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics)
- **Method note:** [`docs/methods/interconnection_durations.md`](../methods/interconnection_durations.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Interconnection request to operation, completed projects, from Berkeley Lab's Queued Up file (docs/methods/interconnection_durations.md). Via the Energy Research Warehouse (ERW), table `interconnection_durations`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: The queue table's (lbnl_interconnection_queue's) own entity_id | none | text | for example lbnl:Avista:17, lbnl:Avista:45, lbnl:CAISO:1003A; 3098 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always project | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 1, 10230, 105; 2839 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AL, US-AR, US-AZ; 43 distinct | 177 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 3098 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 3098 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | -15.0 to 3576.0; 925 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Always operating | none | text | operating | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The operation date | none | date | 1999-06-30 to 2025-12-31; 1734 distinct | 0 |
| `operator` | The operator or owner, as the publisher writes it | none | text | for example AEC, AEP, AMEREN ILLINOIS; 95 distinct | 888 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:interconnection_durations | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://eta-publications.lbl.gov/sites/default/files/2026-05/lbnl_ix_queue_data_file_thru2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T09:16:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The Queued Up edition, as text | none | text | 2026 edition (through 2025) | 0 |
| `queue_id` | The request's queue identifier as Berkeley Lab's file gives it (the source's name: q_id) | none | text | for example 0160A, 0201A, 0201B; 2964 distinct | 0 |
| `grid` | Berkeley Lab's region: the seven ISOs, West and Southeast (the source's name: region) | none | text | CAISO, ERCOT, MISO, NYISO, PJM, SPP, Southeast, West | 0 |
| `state` | The state as the file gives it (the source's name: state) | none | text | for example AL, AR, AZ; 43 distinct | 177: The file gives no state |
| `county` | The county as the file gives it (the source's name: county) | none | text | for example Accomack, Ada, Adair; 714 distinct | 197: The file gives no county |
| `utility` | The file's own utility field (the source's name: utility) | none | text | for example AEC, AEP, AMEREN ILLINOIS; 95 distinct | 888: The file names no utility |
| `transmission_provider` | The transmission provider: Berkeley Lab's entity field (the source's name: entity) | none | text | Avista, CAISO, CSU, Duke, ERCOT, FPL, IP, LADWP, LGE-KU, MISO, MPC, NWMT, NYISO, OUC, PJM, PSE, SOCO, SPP, SRP, SRP_ANPP, SRP_PV-PC, TEC, TSGT | 0 |
| `fuel` | Berkeley Lab's clean type of the request (Solar, Battery, Gas, Wind, Solar+Battery and the others) (the source's name: type_clean) | none | text | Battery, Coal, Diesel, Gas, Gas+Battery, Gas+Oil, Geothermal, Geothermal+Other, Hydro, Nuclear, Offshore Wind, Oil, Other, Other Storage, Solar, Solar+Battery, Solar+Gas, Wind, Wind+Battery | 0 |
| `request_date` | The date the request entered the queue (the source's name: q_date) | none | date | 1997-04-01 to 2025-06-06; 1771 distinct | 0 |
| `operation_date` | The date the project began operating (the source's name: on_date) | none | date | 1999-06-30 to 2025-12-31; 1734 distinct | 0 |
| `months_to_operation` | Days from request_date to operation_date divided by 30.4375 (the mean month), one decimal | month | number | 0.0 to 217.8; 1009 distinct | 0 |
| `request_year` | The year of request_date | none | integer | 1997 to 2025; 29 distinct | 0 |
| `operation_year` | The year of operation_date | none | integer | 1999 to 2025; 27 distinct | 0 |

### `interconnection_durations_summary`

One grid's (or the whole US's) measure of how long the interconnection requests that began operating in one year took from request to operation, from Berkeley Lab and GridTracker's Queued Up, 2026 edition (through 2025).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 1365.

- **Time:** ts_utc is 1 January of the year the projects began operating (a year, not an instant); freq P1Y.
- **Revisions:** Rebuilt whole from lbnl_interconnection_queue by each run of the builder; one edition; vintage is not filled.
- **Source:** lbnl:queued_up Lawrence Berkeley National Laboratory and GridTracker, Queued Up data file (https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics)
- **Method note:** [`docs/methods/interconnection_durations.md`](../methods/interconnection_durations.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Interconnection request to operation, completed projects, from Berkeley Lab's Queued Up file (docs/methods/interconnection_durations.md). Via the Energy Research Warehouse (ERW), table `interconnection_durations_summary`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: lbnl_durations:<grid>: the seven ISOs' codes as held, west, southeast, or us for every counted project | none | text | lbnl_durations:caiso, lbnl_durations:ercot, lbnl_durations:miso, lbnl_durations:nyiso, lbnl_durations:pjm, lbnl_durations:southeast, lbnl_durations:spp, lbnl_durations:us, lbnl_durations:west | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1999-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 27 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.0 to 33634.54; 879 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count, month | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always US, also for a single grid's rows | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1365 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Berkeley Lab's region name (CAISO, West, Southeast and the others) or US, not a pricing node | none | text | CAISO, ERCOT, MISO, NYISO, PJM, SPP, Southeast, US, West | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:interconnection_durations | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://eta-publications.lbl.gov/sites/default/files/2026-05/lbnl_ix_queue_data_file_thru2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T09:16:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1365 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `median_months` | The median time from request to operation of the year's projects, months of 30.4375 days | month | 195 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `median_months_5y` | The median time from request to operation over the five years ending in the row's year, months | month | 195 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `mw` | The capacity of the projects that began operating in the year, MW | MW | 195 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `p25_months` | The 25th percentile of the year's projects' time from request to operation, months | month | 195 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `p75_months` | The 75th percentile of the year's projects' time from request to operation, months | month | 195 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `projects` | The number of projects that began operating in the year | count | 195 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `projects_5y` | The number of projects that began operating in the five years ending in the row's year | count | 195 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `interconnection_queue_summary`

One grid and technology's count, MW, share or median of interconnection requests, by year entered, by year operation began, or for the whole file, from Berkeley Lab's Queued Up file (2026 edition).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 17296.

- **Time:** ts_utc is the first day of the year entered (requests_ and mw_ variables), of the year operation began (on_ variables), or 2025-01-01 for the whole file; a year, not an instant. freq P1Y.
- **Revisions:** Rewritten whole by each run of the builder (warehouse/derived/queue_summary.py) from lbnl_interconnection_queue; vintage is not filled.
- **Source:** erw:interconnection_queue_summary from lbnl:queued_up, Lawrence Berkeley National Laboratory and GridTracker, Queued Up: 2026 Edition data file (https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics)
- **Method note:** [`docs/methods/interconnection_queue_summary.md`](../methods/interconnection_queue_summary.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The interconnection queue summarized by grid and technology, from Berkeley Lab and GridTracker's Queued Up data file (CC BY 4.0). Via the Energy Research Warehouse (ERW), table `interconnection_queue_summary`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: queue:<grid>:<technology>; grid caiso, ercot, isone, miso, nyiso, pjm, spp, west, southeast or us; technology solar, solar_battery, battery, wind, offshore_wind, gas, other or all | none | text | for example queue:caiso:all, queue:caiso:battery, queue:caiso:gas; 76 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1995-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 30 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 7098748.5; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count, pct, year | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US, or the state of a one-state grid (US-CA, US-NY, US-TX) | none | text | US, US-CA, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 17296 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 17296 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:interconnection_queue_summary | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/interconnection_queue_summary.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-17T07:52:10Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 17296 |

Variables (35):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `active_mw_parts_battery` | Over the active requests, the MW of every battery part (a hybrid's battery beside a battery alone); the unit column says count, the method says MW | count | 10 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `active_mw_parts_gas` | Over the active requests, the MW of every gas part; the unit column says count, the method says MW | count | 10 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `active_mw_parts_other_storage` | Over the active requests, the MW of every other storage part; the unit column says count, the method says MW | count | 10 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `active_mw_parts_solar` | Over the active requests, the MW of every solar part; the unit column says count, the method says MW | count | 10 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `active_mw_parts_wind` | Over the active requests, the MW of every wind part (onshore and offshore); the unit column says count, the method says MW | count | 10 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `median_years_to_operation` | The median over those of the days from request date to operation date, over 365.25 (written when at least five) | year | 56 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `mw_active` | The MW of requests entered in the year whose status is active | MW | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `mw_entered` | The MW of requests that entered in the year (all parts of a hybrid) | MW | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `mw_operating` | The MW of requests entered in the year that reached operation | MW | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `mw_suspended` | The MW of requests entered in the year whose status is suspended | MW | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `mw_withdrawn` | The MW of requests entered in the year that were withdrawn | MW | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `on_median_years_to_operation` | The median years from request to operation of the requests that began operating in the year (at least five dated) | year | 463 | 2000-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `on_requests_dated` | Requests that began operating in the year with both dates in order, count | count | 463 | 2000-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `operating_requests` | Requests that reached operation, count | count | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `past_mw` | The MW of those past requests | MW | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `past_mw_open_share_pct` | Of past_mw, the share still open (active or suspended), percent | pct | 73 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `past_mw_operating_share_pct` | Of past_mw, the share that reached operation, percent | pct | 73 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `past_mw_withdrawn_share_pct` | Of past_mw, the share withdrawn, percent | pct | 73 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `past_open_share_pct` | Of past_requests, the share still open (active or suspended), percent | pct | 73 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `past_operating_share_pct` | Of past_requests, the share that reached operation, percent (written when at least 20) | pct | 73 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `past_requests` | Requests that entered from 2000 to 2020 with a known status, count | count | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `past_withdrawn_share_pct` | Of past_requests, the share withdrawn, percent | pct | 73 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `requests_active` | Requests entered in the year whose status is active, count | count | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `requests_entered` | Requests that entered the queue in the year, count | count | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `requests_operating` | Requests entered in the year that reached operation, count | count | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `requests_suspended` | Requests entered in the year whose status is suspended, count | count | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `requests_withdrawn` | Requests entered in the year that were withdrawn, count | count | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `requests_without_year` | Requests with no year entered, count | count | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_active_mw` | The MW of requests whose status is active | MW | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_active_requests` | Requests whose status is active, count | count | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_mw` | The MW of every request of the view | MW | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_requests` | Every request of the view, count | count | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_suspended_mw` | The MW of requests whose status is suspended | MW | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_suspended_requests` | Requests whose status is suspended (not in the active figures), count | count | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `years_to_operation_n` | Of those, the requests with both a request and an operation date in order, count | count | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

Waiting for a second look: active_mw_parts_battery, _solar, _wind, _gas and _other_storage carry unit count in the table, while the method note (session 7051) and the builder say they are MW: the unit column looks wrong..

