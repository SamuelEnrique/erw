# Codebook: interconnection

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 5 public tables (2 entities, 3 series; tiers: 5 derived); 0 documented in full.

- [`interconnection_agreements_by_grid`](#interconnection_agreements_by_grid): generation with a signed interconnection agreement by grid, fuel and year of agreement, 2026 edition (through 2025) (session 854)
- [`interconnection_agreements_signed`](#interconnection_agreements_signed): interconnection requests with a signed agreement, not yet operating, 2026 edition (through 2025) (session 854)
- [`interconnection_durations`](#interconnection_durations): interconnection request to operation, every completed project with both dates, 2026 edition (through 2025) (session 671)
- [`interconnection_durations_summary`](#interconnection_durations_summary): interconnection request to operation by grid and year of operation, 2026 edition (through 2025) (session 671)
- [`interconnection_queue_summary`](#interconnection_queue_summary): the interconnection queue summarized by grid and technology (session 95)

### `interconnection_agreements_by_grid`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 438.

- **Source:** lbnl:queued_up Lawrence Berkeley National Laboratory and GridTracker, Queued Up data file (https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics)
- **Method note:** [`docs/methods/interconnection_agreements.md`](../methods/interconnection_agreements.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Generation with a signed interconnection agreement, from Berkeley Lab's Queued Up file (docs/methods/interconnection_agreements.md). Via the Energy Research Warehouse (ERW), table `interconnection_agreements_by_grid`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example interconnection_agreements:caiso, interconnection_agreements:caiso:battery, interconnection_agreements:caiso:gas_battery; 118 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2002-01-01T00:00:00Z, 2004-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.0 to 2001973.87; 283 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 438 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example CAISO, CAISO, Battery, CAISO, Gas+Battery; 118 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:interconnection_agreements | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://eta-publications.lbl.gov/sites/default/files/2026-05/lbnl_ix_queue_data_file_thru2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T09:16:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 438 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `active_mw` |  | MW | 10 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `active_projects` |  | count | 10 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `mw_signed` |  | MW | 118 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `mw_signed_in_year` |  | MW | 86 | 2002-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `projects_signed` |  | count | 118 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `projects_signed_in_year` |  | count | 86 | 2002-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `signed_share_pct` |  | pct | 10 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `interconnection_agreements_signed`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: derived. Rows read on 2026-11-20: 2522.

- **Source:** lbnl:queued_up Lawrence Berkeley National Laboratory and GridTracker, Queued Up data file (https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics)
- **Method note:** [`docs/methods/interconnection_agreements.md`](../methods/interconnection_agreements.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Generation with a signed interconnection agreement, from Berkeley Lab's Queued Up file (docs/methods/interconnection_agreements.md). Via the Energy Research Warehouse (ERW), table `interconnection_agreements_signed`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example lbnl:AEC:GI-101, lbnl:AEC:GI-102, lbnl:AEC:GI-103; 2522 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 1, 1008, 11; 2428 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AL, US-AR, US-AZ; 49 distinct | 5 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 2522 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 2522 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | -27.0 to 4357.4; 1008 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | active, suspended | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | date | 2002-06-10 to 2025-12-31; 785 distinct | 1146 |
| `operator` | The operator or owner, as the publisher writes it | none | text | for example AEC, AEP, AMEREN ILLINOIS; 133 distinct | 680 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:interconnection_agreements | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://eta-publications.lbl.gov/sites/default/files/2026-05/lbnl_ix_queue_data_file_thru2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T09:16:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | text | 2026 edition (through 2025) | 0 |
| `queue_id` | not yet written |  | text | for example 1, 1002, 1003; 2499 distinct | 0 |
| `grid` | not yet written |  | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP, Southeast, West | 0 |
| `state` | not yet written |  | text | for example AL, AR, AZ; 49 distinct | 5 |
| `county` | not yet written |  | text | for example Acadia Parish, Accomack, Ada; 758 distinct | 13 |
| `utility` | not yet written |  | text | for example AEC, AEP, AMEREN ILLINOIS; 133 distinct | 680 |
| `transmission_provider` | not yet written |  | text | for example AEC, APS, Avista; 37 distinct | 0 |
| `fuel` | not yet written |  | text | Battery, Coal, Diesel, Gas, Gas+Battery, Gas+Diesel, Gas+Oil, Geothermal, Hydro, Hydro+Battery, Nuclear, Offshore Wind, Oil, Other, Other Storage, Other+Battery, Solar, Solar+Battery, Solar+Gas+Battery, Solar+Geothermal, Solar+Other, Solar+Wind+Battery, Wind, Wind+Battery | 0 |
| `ia_date` | not yet written |  | date | 2002-06-10 to 2025-12-31; 785 distinct | 1146 |
| `ia_phase` | not yet written |  | text | Cluster Study, Construction, Facility Study, IA Executed, IA Pending, In Progress (unknown study), Suspended, System Impact Study | 11 |
| `request_date` | not yet written |  | date | 2001-02-06 to 2025-11-05; 1003 distinct | 33 |
| `proposed_date` | not yet written |  | date | 1990-12-03 to 2036-12-31; 836 distinct | 24 |
| `signed_by` | not yet written |  | text | date, phase, phase+date | 0 |

### `interconnection_durations`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: derived. Rows read on 2026-11-20: 3098.

- **Source:** lbnl:queued_up Lawrence Berkeley National Laboratory and GridTracker, Queued Up data file (https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics)
- **Method note:** [`docs/methods/interconnection_durations.md`](../methods/interconnection_durations.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Interconnection request to operation, completed projects, from Berkeley Lab's Queued Up file (docs/methods/interconnection_durations.md). Via the Energy Research Warehouse (ERW), table `interconnection_durations`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example lbnl:Avista:17, lbnl:Avista:45, lbnl:CAISO:1003A; 3098 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 1, 10230, 105; 2839 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AL, US-AR, US-AZ; 43 distinct | 177 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 3098 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 3098 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | -15.0 to 3576.0; 925 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | operating | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | date | 1999-06-30 to 2025-12-31; 1734 distinct | 0 |
| `operator` | The operator or owner, as the publisher writes it | none | text | for example AEC, AEP, AMEREN ILLINOIS; 95 distinct | 888 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:interconnection_durations | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://eta-publications.lbl.gov/sites/default/files/2026-05/lbnl_ix_queue_data_file_thru2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T09:16:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | text | 2026 edition (through 2025) | 0 |
| `queue_id` | not yet written |  | text | for example 0160A, 0201A, 0201B; 2964 distinct | 0 |
| `grid` | not yet written |  | text | CAISO, ERCOT, MISO, NYISO, PJM, SPP, Southeast, West | 0 |
| `state` | not yet written |  | text | for example AL, AR, AZ; 43 distinct | 177 |
| `county` | not yet written |  | text | for example Accomack, Ada, Adair; 714 distinct | 197 |
| `utility` | not yet written |  | text | for example AEC, AEP, AMEREN ILLINOIS; 95 distinct | 888 |
| `transmission_provider` | not yet written |  | text | Avista, CAISO, CSU, Duke, ERCOT, FPL, IP, LADWP, LGE-KU, MISO, MPC, NWMT, NYISO, OUC, PJM, PSE, SOCO, SPP, SRP, SRP_ANPP, SRP_PV-PC, TEC, TSGT | 0 |
| `fuel` | not yet written |  | text | Battery, Coal, Diesel, Gas, Gas+Battery, Gas+Oil, Geothermal, Geothermal+Other, Hydro, Nuclear, Offshore Wind, Oil, Other, Other Storage, Solar, Solar+Battery, Solar+Gas, Wind, Wind+Battery | 0 |
| `request_date` | not yet written |  | date | 1997-04-01 to 2025-06-06; 1771 distinct | 0 |
| `operation_date` | not yet written |  | date | 1999-06-30 to 2025-12-31; 1734 distinct | 0 |
| `months_to_operation` | not yet written |  | number | 0.0 to 217.8; 1009 distinct | 0 |
| `request_year` | not yet written |  | integer | 1997 to 2025; 29 distinct | 0 |
| `operation_year` | not yet written |  | integer | 1999 to 2025; 27 distinct | 0 |

### `interconnection_durations_summary`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 1365.

- **Source:** lbnl:queued_up Lawrence Berkeley National Laboratory and GridTracker, Queued Up data file (https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics)
- **Method note:** [`docs/methods/interconnection_durations.md`](../methods/interconnection_durations.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Interconnection request to operation, completed projects, from Berkeley Lab's Queued Up file (docs/methods/interconnection_durations.md). Via the Energy Research Warehouse (ERW), table `interconnection_durations_summary`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | lbnl_durations:caiso, lbnl_durations:ercot, lbnl_durations:miso, lbnl_durations:nyiso, lbnl_durations:pjm, lbnl_durations:southeast, lbnl_durations:spp, lbnl_durations:us, lbnl_durations:west | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1999-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 27 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 1.0 to 33634.54; 879 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count, month | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1365 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | CAISO, ERCOT, MISO, NYISO, PJM, SPP, Southeast, US, West | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:interconnection_durations | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://eta-publications.lbl.gov/sites/default/files/2026-05/lbnl_ix_queue_data_file_thru2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T09:16:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1365 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `median_months` |  | month | 195 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `median_months_5y` |  | month | 195 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `mw` |  | MW | 195 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `p25_months` |  | month | 195 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `p75_months` |  | month | 195 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `projects` |  | count | 195 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `projects_5y` |  | count | 195 | 1999-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `interconnection_queue_summary`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 17296.

- **Source:** erw:interconnection_queue_summary from lbnl:queued_up, Lawrence Berkeley National Laboratory and GridTracker, Queued Up: 2026 Edition data file (https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics)
- **Method note:** [`docs/methods/interconnection_queue_summary.md`](../methods/interconnection_queue_summary.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The interconnection queue summarized by grid and technology, from Berkeley Lab and GridTracker's Queued Up data file (CC BY 4.0). Via the Energy Research Warehouse (ERW), table `interconnection_queue_summary`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example queue:caiso:all, queue:caiso:battery, queue:caiso:gas; 76 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1995-01-01T00:00:00Z to 2025-01-01T00:00:00Z; 30 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 7098748.5; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, count, pct, year | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-CA, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 17296 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 17296 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:interconnection_queue_summary | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/interconnection_queue_summary.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-17T07:52:10Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 17296 |

Variables (35):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `active_mw_parts_battery` |  | count | 10 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `active_mw_parts_gas` |  | count | 10 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `active_mw_parts_other_storage` |  | count | 10 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `active_mw_parts_solar` |  | count | 10 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `active_mw_parts_wind` |  | count | 10 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `median_years_to_operation` |  | year | 56 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `mw_active` |  | MW | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `mw_entered` |  | MW | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `mw_operating` |  | MW | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `mw_suspended` |  | MW | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `mw_withdrawn` |  | MW | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `on_median_years_to_operation` |  | year | 463 | 2000-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `on_requests_dated` |  | count | 463 | 2000-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `operating_requests` |  | count | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `past_mw` |  | MW | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `past_mw_open_share_pct` |  | pct | 73 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `past_mw_operating_share_pct` |  | pct | 73 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `past_mw_withdrawn_share_pct` |  | pct | 73 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `past_open_share_pct` |  | pct | 73 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `past_operating_share_pct` |  | pct | 73 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `past_requests` |  | count | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `past_withdrawn_share_pct` |  | pct | 73 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `requests_active` |  | count | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `requests_entered` |  | count | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `requests_operating` |  | count | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `requests_suspended` |  | count | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `requests_withdrawn` |  | count | 1499 | 1995-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `requests_without_year` |  | count | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_active_mw` |  | MW | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_active_requests` |  | count | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_mw` |  | MW | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_requests` |  | count | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_suspended_mw` |  | MW | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `total_suspended_requests` |  | count | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `years_to_operation_n` |  | count | 76 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

