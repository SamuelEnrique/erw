# Codebook: storage

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 4 public tables (1 entities, 3 series; tiers: 4 derived); 0 documented in full.

- [`storage_buildout_monthly`](#storage_buildout_monthly): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261024T153933Z-github (2026-10-24T15:39:33Z); that run's own header of the table follows
- [`storage_capacity`](#storage_capacity): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261024T153933Z-github (2026-10-24T15:39:33Z); that run's own header of the table follows
- [`storage_daily_cycle`](#storage_daily_cycle): battery storage daily cycle per balancing authority, from EIA-930 (derived, session 31) and, for CAISO, from CAISO's own data (session 34)
- [`storage_owners_monthly`](#storage_owners_monthly): Who owns the batteries: operating and planned battery storage by reporting company and grid; EIA-860M inventory of 2026-09 (derived, session 87)

### `storage_buildout_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 21382.

- **Source:** erw:storage_buildout ERW derived table, storage build-out method (docs/methods/storage_buildout.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage_buildout.md)
- **Method note:** [`docs/methods/storage_buildout.md`](../methods/storage_buildout.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Storage build-out by grid and month (docs/methods/storage_buildout.md). Via the Energy Research Warehouse (ERW), table `storage_buildout_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | iso:caiso, iso:ercot, iso:isone, iso:miso, iso:nyiso, iso:pjm, iso:spp, us:outside_isos, us:total | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-09-01T00:00:00Z; 141 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 172181.6; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, MWh/MW, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 21382 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 21382 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:storage_buildout | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage_buildout.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-03T08:00:34Z, 2026-10-24T14:50:31Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 21382 |

Variables (26):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `battery_mwh_per_solar_mw` |  | MWh/MW | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mw` |  | MW | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mw_2to4h` |  | MW | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mw_4to6h` |  | MW | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mw_energy_not_reported` |  | MW | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mw_ge6h` |  | MW | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mw_lt2h` |  | MW | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mw_net_added_12m` |  | MW | 1161 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mwh` |  | MWh | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mwh_2to4h` |  | MWh | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mwh_4to6h` |  | MWh | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mwh_ge6h` |  | MWh | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mwh_lt2h` |  | MWh | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mwh_net_added_12m` |  | MWh | 1161 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mwh_per_mw` |  | MWh/MW | 1213 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_units` |  | count | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_mw` |  | MW | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_mw_online_2026` |  | MW | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_mw_online_2027` |  | MW | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_mw_online_2028` |  | MW | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_mw_online_2029` |  | MW | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_mw_online_2030` |  | MW | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_mw_online_2031` |  | MW | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_mw_under_construction` |  | MW | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_units` |  | count | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `solar_operating_mw` |  | MW | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `storage_capacity`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: derived. Rows read on 2026-11-20: 1648.

- **Source:** erw:storage_capacity ERW derived table, storage method (docs/methods/storage.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage.md)
- **Method note:** [`docs/methods/storage.md`](../methods/storage.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Battery storage units from EIA-860M (docs/methods/storage.md). Via the Energy Research Warehouse (ERW), table `storage_capacity`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example eia860:10156:BESS1, eia860:1016:11, eia860:10444:LHC1; 1648 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 0 Hammond St CSG, 0 Middle, 1 Commercial; 1571 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 51 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 17.963472 to 66.837778; 1519 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -162.5569 to -65.9045; 1512 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | 0.1 to 1200.0; 344 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | operating, planned, retired, under_construction | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | date | 2003-12-01 to 2026-09-01; 139 distinct | 484 |
| `operator` | The operator or owner, as the publisher writes it | none | text | for example 0HAM WHAM8 Solar, LLC, 147 Williamsville Solar 1, LLC, 160TIH WHAM8 Solar, LLC; 958 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:storage_capacity | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T14:50:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | text | 2026-09 | 0 |
| `plant_id` | not yet written |  | integer | 141 to 70584; 1571 distinct | 0 |
| `generator_id` | not yet written |  | text | for example 013A, 013B, 09170; 1296 distinct | 1 |
| `state` | not yet written |  | text | for example AK, AL, AR; 51 distinct | 0 |
| `county` | not yet written |  | text | for example Ada, Adams, Addison; 456 distinct | 1 |
| `balancing_authority` | not yet written |  | text | for example AVRN, AZPS, BANC; 43 distinct | 25 |
| `iso` | not yet written |  | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP | 381 |
| `net_summer_mw` | not yet written |  | number | 0.1 to 1200.0; 328 distinct | 0 |
| `eia_status` | not yet written |  | text | L, OA, OP, OS, P, RE, SB, T, TS, U, V | 0 |
| `operating_year` | not yet written |  | integer | 2003, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 | 484 |
| `planned_year` | not yet written |  | integer | 2026, 2027, 2028, 2029, 2030, 2031 | 1164 |
| `retirement_date` | not yet written |  | date | 2025-01-01, 2025-06-01, 2025-07-01, 2025-08-01, 2025-09-01, 2026-02-01 | 1640 |
| `source_table` | not yet written |  | text | eia860m_operating_generators, eia860m_planned_generators, eia860m_retired_generators | 0 |
| `input_source_url` | not yet written |  | text | https://www.eia.gov/electricity/data/eia860m/xls/september_generator2026.xlsx | 0 |
| `energy_capacity_mwh` | not yet written |  | number | 0.2 to 2000.0; 316 distinct | 485 |

### `storage_daily_cycle`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 15085.

- **Source:** erw:storage_daily_cycle ERW derived table, storage method (docs/methods/storage.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage.md)
- **Source:** erw:storage_daily_cycle_caiso the CAISO rows (ba ciso, entity caiso:ISO), from CAISO's Today's Outlook Total batteries, 5-minute values averaged to hours (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage.md#caiso)
- **Method note:** [`docs/methods/storage.md`](../methods/storage.md)
- **Cite as:** Energy Research Warehouse (ERW), derived; Energy Research Warehouse (ERW), derived from California ISO. Battery storage daily cycle (docs/methods/storage.md); Battery storage daily cycle, CAISO rows, from CAISO Today's Outlook (caiso_battery_storage; docs/methods/storage.md). Via the Energy Research Warehouse (ERW), table `storage_daily_cycle`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:ISO, eia930:ERCO, eia930:ISNE, eia930:MISO, eia930:SWPP, eia930:US48 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2024-11-01T00:00:00Z to 2026-11-15T00:00:00Z; 745 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 65097.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, hour, ratio | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 15085 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 15085 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:storage_daily_cycle, erw:storage_daily_cycle_caiso | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage.md, https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage.md#caiso | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T23:43:39Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 15085 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48) | none | text | ciso, erco, isne, miso, swpp, us48 | 0 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `mwh_charged` |  | MWh | 3599 | 2024-11-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `mwh_discharged` |  | MWh | 3599 | 2024-11-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `peak_charge_hour` |  | hour | 2159 | 2024-11-05T00:00:00Z | 2026-11-15T00:00:00Z |
| `peak_discharge_hour` |  | hour | 3569 | 2024-11-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `round_trip_ratio` |  | ratio | 2159 | 2024-11-05T00:00:00Z | 2026-11-15T00:00:00Z |

### `storage_owners_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 19180.

- **Source:** erw:storage_owners ERW derived table, storage owners method (docs/methods/storage_owners.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage_owners.md)
- **Method note:** [`docs/methods/storage_owners.md`](../methods/storage_owners.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Battery storage by reporting company and grid (docs/methods/storage_owners.md). Via the Energy Research Warehouse (ERW), table `storage_owners_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example eia860:utility:10000, eia860:utility:10071, eia860:utility:1015; 967 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-08-01T00:00:00Z, 2026-09-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 154272.4; 1619 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, MWh/MW, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 19180 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 19180 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:storage_owners | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage_owners.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-04T04:46:37Z, 2026-11-03T17:31:50Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 19180 |
| `x_grid` | not yet written |  | text | caiso, ercot, isone, miso, nyiso, outside_isos, pjm, spp, us | 0 |
| `x_metric` | not yet written |  | text | operating_hours, operating_mw, operating_mwh, operating_rank, operating_share_pct, operating_units, owners_operating, owners_planned, planned_mw, planned_units, top10_share_pct, top5_share_pct | 0 |
| `x_owner` | not yet written |  | text | for example 0HAM WHAM8 Solar, LLC, 147 Williamsville Solar 1, LLC, 160TIH WHAM8 Solar, LLC; 960 distinct | 180 |

Variables (108):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `caiso_operating_hours` |  | MWh/MW | 356 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_operating_mw` |  | MW | 357 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_operating_mwh` |  | MWh | 357 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_operating_rank` |  | count | 355 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_operating_share_pct` |  | pct | 355 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_operating_units` |  | count | 357 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_owners_operating` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_owners_planned` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_planned_mw` |  | MW | 144 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_planned_units` |  | count | 144 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_top10_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_top5_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_operating_hours` |  | MWh/MW | 324 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_operating_mw` |  | MW | 324 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_operating_mwh` |  | MWh | 324 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_operating_rank` |  | count | 322 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_operating_share_pct` |  | pct | 322 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_operating_units` |  | count | 324 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_owners_operating` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_owners_planned` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_planned_mw` |  | MW | 202 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_planned_units` |  | count | 202 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_top10_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_top5_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_operating_hours` |  | MWh/MW | 200 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_operating_mw` |  | MW | 200 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_operating_mwh` |  | MWh | 200 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_operating_rank` |  | count | 198 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_operating_share_pct` |  | pct | 198 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_operating_units` |  | count | 200 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_owners_operating` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_owners_planned` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_planned_mw` |  | MW | 42 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_planned_units` |  | count | 42 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_top10_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_top5_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_operating_hours` |  | MWh/MW | 50 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_operating_mw` |  | MW | 50 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_operating_mwh` |  | MWh | 50 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_operating_rank` |  | count | 48 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_operating_share_pct` |  | pct | 48 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_operating_units` |  | count | 50 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_owners_operating` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_owners_planned` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_planned_mw` |  | MW | 38 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_planned_units` |  | count | 38 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_top10_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_top5_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_operating_hours` |  | MWh/MW | 68 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_operating_mw` |  | MW | 68 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_operating_mwh` |  | MWh | 68 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_operating_rank` |  | count | 66 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_operating_share_pct` |  | pct | 66 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_operating_units` |  | count | 68 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_owners_operating` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_owners_planned` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_planned_mw` |  | MW | 19 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_planned_units` |  | count | 19 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_top10_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_top5_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_operating_hours` |  | MWh/MW | 311 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_operating_mw` |  | MW | 311 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_operating_mwh` |  | MWh | 311 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_operating_rank` |  | count | 309 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_operating_share_pct` |  | pct | 309 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_operating_units` |  | count | 311 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_owners_operating` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_owners_planned` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_planned_mw` |  | MW | 192 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_planned_units` |  | count | 192 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_top10_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_top5_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_operating_hours` |  | MWh/MW | 74 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_operating_mw` |  | MW | 74 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_operating_mwh` |  | MWh | 74 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_operating_rank` |  | count | 72 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_operating_share_pct` |  | pct | 72 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_operating_units` |  | count | 74 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_owners_operating` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_owners_planned` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_planned_mw` |  | MW | 43 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_planned_units` |  | count | 43 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_top10_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_top5_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_operating_hours` |  | MWh/MW | 30 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_operating_mw` |  | MW | 30 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_operating_mwh` |  | MWh | 30 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_operating_rank` |  | count | 28 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_operating_share_pct` |  | pct | 28 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_operating_units` |  | count | 30 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_owners_operating` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_owners_planned` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_planned_mw` |  | MW | 30 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_planned_units` |  | count | 30 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_top10_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_top5_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_operating_hours` |  | MWh/MW | 1320 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_operating_mw` |  | MW | 1321 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_operating_mwh` |  | MWh | 1321 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_operating_rank` |  | count | 1319 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_operating_share_pct` |  | pct | 1319 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_operating_units` |  | count | 1321 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_owners_operating` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_owners_planned` |  | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_planned_mw` |  | MW | 658 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_planned_units` |  | count | 658 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_top10_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_top5_share_pct` |  | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |

