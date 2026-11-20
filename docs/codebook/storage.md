# Codebook: storage

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 4 public tables (1 entities, 3 series; tiers: 4 derived); 4 documented in full.

- [`storage_buildout_monthly`](#storage_buildout_monthly): One grid's (or the US's) value of one measure of the battery fleet, or of solar, at one month's end, rebuilt from one EIA-860M inventory.
- [`storage_capacity`](#storage_capacity): One battery generator (EIA prime mover BA) of the US, operating, planned or retired, from the EIA-860M tables.
- [`storage_daily_cycle`](#storage_daily_cycle): One balancing authority's value of one measure of its batteries' charging and discharging on one complete local day.
- [`storage_owners_monthly`](#storage_owners_monthly): One company's (EIA-860M Entity) or one grid's value of one measure of the battery fleet in one grid, at one EIA-860M inventory month.

### `storage_buildout_monthly`

One grid's (or the US's) value of one measure of the battery fleet, or of solar, at one month's end, rebuilt from one EIA-860M inventory.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 21382.

- **Time:** ts_utc is the first of the month at 00:00:00Z, and the value is the fleet at that month's end (freq P1M); the planned rows stand at the inventory month only.
- **Revisions:** Merged by key (entity, variable, ts_utc), a run's rows replacing earlier rows with the same key and earlier rows otherwise kept; every month is rebuilt from the one inventory read, its month named in the header. vintage is not filled.
- **Source:** erw:storage_buildout ERW derived table, storage build-out method (docs/methods/storage_buildout.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage_buildout.md)
- **Method note:** [`docs/methods/storage_buildout.md`](../methods/storage_buildout.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Storage build-out by grid and month (docs/methods/storage_buildout.md). Via the Energy Research Warehouse (ERW), table `storage_buildout_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: iso:<caiso\|ercot\|isone\|miso\|nyiso\|pjm\|spp> by the generator's balancing authority in EIA-860M; us:outside_isos for every other code and no code; us:total for every unit | none | text | iso:caiso, iso:ercot, iso:isone, iso:miso, iso:nyiso, iso:pjm, iso:spp, us:outside_isos, us:total | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-09-01T00:00:00Z; 141 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 172181.6; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, MWh/MW, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 21382 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 21382 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:storage_buildout | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage_buildout.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-03T08:00:34Z, 2026-10-24T14:50:31Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 21382 |

Variables (26):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `battery_mwh_per_solar_mw` | Operating battery MWh per MW of operating solar | MWh/MW | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mw` | Operating battery capacity, nameplate MW | MW | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mw_2to4h` | Operating battery MW of units of 2 to 4 hours | MW | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mw_4to6h` | Operating battery MW of units of 4 to 6 hours | MW | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mw_energy_not_reported` | Operating battery MW of units EIA gives no energy for (in no duration bucket) | MW | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mw_ge6h` | Operating battery MW of units of 6 hours and more | MW | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mw_lt2h` | Operating battery MW of units under 2 hours (MWh over MW) | MW | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mw_net_added_12m` | Operating battery MW less the value twelve months before (net of retirements) | MW | 1161 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mwh` | Operating battery energy capacity (EIA's Nameplate Energy Capacity) | MWh | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mwh_2to4h` | Operating battery MWh of units of 2 to 4 hours | MWh | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mwh_4to6h` | Operating battery MWh of units of 4 to 6 hours | MWh | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mwh_ge6h` | Operating battery MWh of units of 6 hours and more | MWh | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mwh_lt2h` | Operating battery MWh of units under 2 hours | MWh | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mwh_net_added_12m` | Operating battery MWh less the value twelve months before (net of retirements) | MWh | 1161 | 2016-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_mwh_per_mw` | Average battery duration: MWh over the MW of the units that report energy | MWh/MW | 1213 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_operating_units` | Operating battery units | count | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_mw` | Planned battery capacity in the inventory month, nameplate MW | MW | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_mw_online_2026` | Planned battery MW with EIA's planned operation date in 2026 | MW | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_mw_online_2027` | Planned battery MW with EIA's planned operation date in 2027 | MW | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_mw_online_2028` | Planned battery MW with EIA's planned operation date in 2028 | MW | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_mw_online_2029` | Planned battery MW with EIA's planned operation date in 2029 | MW | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_mw_online_2030` | Planned battery MW with EIA's planned operation date in 2030 | MW | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_mw_online_2031` | Planned battery MW with EIA's planned operation date in 2031 | MW | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_mw_under_construction` | Planned battery MW whose status is under construction | MW | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `battery_planned_units` | Planned battery units in the inventory month | count | 9 | 2026-09-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `solar_operating_mw` | Operating solar capacity (photovoltaic and solar thermal), nameplate MW | MW | 1269 | 2015-01-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `storage_capacity`

One battery generator (EIA prime mover BA) of the US, operating, planned or retired, from the EIA-860M tables.

Shape: entities. Keys: `entity_id`. License: public; tier: derived. Rows read on 2026-11-20: 1648.

- **Time:** No time column; vintage is the month of the EIA-860M inventory read (YYYY-MM), and the table is that inventory as read on its retrieved_at.
- **Revisions:** A snapshot, replaced whole by each run, so a unit EIA drops leaves the table.
- **Source:** erw:storage_capacity ERW derived table, storage method (docs/methods/storage.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage.md)
- **Method note:** [`docs/methods/storage.md`](../methods/storage.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Battery storage units from EIA-860M (docs/methods/storage.md). Via the Energy Research Warehouse (ERW), table `storage_capacity`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: eia860:<plant id>:<generator id> | none | text | for example eia860:10156:BESS1, eia860:1016:11, eia860:10444:LHC1; 1648 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 0 Hammond St CSG, 0 Middle, 1 Commercial; 1571 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 51 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 17.963472 to 66.837778; 1519 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -162.5569 to -65.9045; 1512 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: EIA's nameplate MW | MW | number | 0.1 to 1200.0; 344 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | operating, planned, retired, under_construction | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: As carried from the EIA-860M tables; empty on every planned unit (484 rows) | none | date | 2003-12-01 to 2026-09-01; 139 distinct | 484 |
| `operator` | The operator or owner, as the publisher writes it | none | text | for example 0HAM WHAM8 Solar, LLC, 147 Williamsville Solar 1, LLC, 160TIH WHAM8 Solar, LLC; 958 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:storage_capacity | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T14:50:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The EIA-860M inventory month (YYYY-MM), not a UTC time | none | text | 2026-09 | 0 |
| `plant_id` | EIA's plant code | none | integer | 141 to 70584; 1571 distinct | 0 |
| `generator_id` | EIA's generator code within the plant | none | text | for example 013A, 013B, 09170; 1296 distinct | 1: Not given for one unit |
| `state` | The plant's state, two-letter code | none | text | for example AK, AL, AR; 51 distinct | 0 |
| `county` | The plant's county as EIA writes it | none | text | for example Ada, Adams, Addison; 456 distinct | 1: Not given for one unit |
| `balancing_authority` | The unit's balancing authority, EIA's code as written | none | text | for example AVRN, AZPS, BANC; 43 distinct | 25: EIA gives no balancing authority code for the unit |
| `iso` | The ISO of the unit's balancing authority where it is one of the seven (CISO CAISO, ERCO ERCOT, ISNE ISO-NE, MISO, NYIS NYISO, PJM, SWPP SPP) | none | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP | 381: The balancing authority is not one of the seven ISOs, or is not given |
| `net_summer_mw` | EIA's net summer capacity of the unit | MW | number | 0.1 to 1200.0; 328 distinct | 0 |
| `eia_status` | EIA's own status code of the unit (OP, SB, OS, OA, P, L, T, U, V, TS, RE) | none | text | L, OA, OP, OS, P, RE, SB, T, TS, U, V | 0 |
| `operating_year` | EIA's operating year (operating and retired units) | none | integer | 2003, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 | 484: A planned unit |
| `planned_year` | The year of EIA's planned operation date (planned units) | none | integer | 2026, 2027, 2028, 2029, 2030, 2031 | 1164: An operating or retired unit |
| `retirement_date` | EIA's retirement date of the unit | none | date | 2025-01-01, 2025-06-01, 2025-07-01, 2025-08-01, 2025-09-01, 2026-02-01 | 1640: The unit is not retired |
| `source_table` | The ERW table the row was read from (eia860m_operating_generators, eia860m_planned_generators or eia860m_retired_generators) | none | text | eia860m_operating_generators, eia860m_planned_generators, eia860m_retired_generators | 0 |
| `input_source_url` | The address of the EIA-860M workbook the input table was read from | none | text | https://www.eia.gov/electricity/data/eia860m/xls/september_generator2026.xlsx | 0 |
| `energy_capacity_mwh` | EIA's Nameplate Energy Capacity of the unit, never estimated from MW (the source's name: Nameplate Energy Capacity (MWh)) | MWh | number | 0.2 to 2000.0; 316 distinct | 485: A planned unit (EIA's Planned sheet has no energy column), or an operating unit EIA gives no energy for |

### `storage_daily_cycle`

One balancing authority's value of one measure of its batteries' charging and discharging on one complete local day.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 15085.

- **Time:** ts_utc is the local day at 00:00:00Z (freq P1D): ERCO and SWPP America/Chicago, MISO EST, ISNE and US48 America/New_York, CISO America/Los_Angeles; only days that ended at least 48 hours before the area's newest hour held.
- **Revisions:** Rewritten whole by each run of the builder; vintage is not filled.
- **Source:** erw:storage_daily_cycle ERW derived table, storage method (docs/methods/storage.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage.md)
- **Source:** erw:storage_daily_cycle_caiso the CAISO rows (ba ciso, entity caiso:ISO), from CAISO's Today's Outlook Total batteries, 5-minute values averaged to hours (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage.md#caiso)
- **Method note:** [`docs/methods/storage.md`](../methods/storage.md)
- **Cite as:** Energy Research Warehouse (ERW), derived; Energy Research Warehouse (ERW), derived from California ISO. Battery storage daily cycle (docs/methods/storage.md); Battery storage daily cycle, CAISO rows, from CAISO Today's Outlook (caiso_battery_storage; docs/methods/storage.md). Via the Energy Research Warehouse (ERW), table `storage_daily_cycle`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930:<BA> from EIA-930; caiso:ISO for CAISO's own data | none | text | caiso:ISO, eia930:ERCO, eia930:ISNE, eia930:MISO, eia930:SWPP, eia930:US48 | 0 |
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
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48). Here: ciso on the caiso:ISO rows | none | text | ciso, erco, isne, miso, swpp, us48 | 0 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `mwh_charged` | Sum of the negative hourly battery net generation over the day, as a positive number (charging) | MWh | 3599 | 2024-11-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `mwh_discharged` | Sum of the positive hourly battery net generation over the day (discharging) | MWh | 3599 | 2024-11-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `peak_charge_hour` | The local hour (0 to 23, its start) of the day's largest charge | hour | 2159 | 2024-11-05T00:00:00Z | 2026-11-15T00:00:00Z |
| `peak_discharge_hour` | The local hour (0 to 23, its start) of the day's largest discharge; the earliest on a tie | hour | 3569 | 2024-11-01T00:00:00Z | 2026-11-15T00:00:00Z |
| `round_trip_ratio` | mwh_discharged over mwh_charged, a ratio of the day's energies as reported, not a measured efficiency | ratio | 2159 | 2024-11-05T00:00:00Z | 2026-11-15T00:00:00Z |

### `storage_owners_monthly`

One company's (EIA-860M Entity) or one grid's value of one measure of the battery fleet in one grid, at one EIA-860M inventory month.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 19180.

- **Time:** ts_utc is the inventory month's first day at 00:00:00Z (freq P1M).
- **Revisions:** Merged by key (entity, variable, ts_utc): each inventory month's rows are kept beside the earlier months'. vintage is not filled.
- **Source:** erw:storage_owners ERW derived table, storage owners method (docs/methods/storage_owners.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage_owners.md)
- **Method note:** [`docs/methods/storage_owners.md`](../methods/storage_owners.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Battery storage by reporting company and grid (docs/methods/storage_owners.md). Via the Energy Research Warehouse (ERW), table `storage_owners_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia860:utility:<EIA Entity ID> for a company; iso:<grid>, us:outside_isos or us:total for a grid's own totals | none | text | for example eia860:utility:10000, eia860:utility:10071, eia860:utility:1015; 967 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-08-01T00:00:00Z, 2026-09-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 154272.4; 1619 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, MWh/MW, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 19180 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 19180 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:storage_owners | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage_owners.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-04T04:46:37Z, 2026-11-03T17:31:50Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 19180 |
| `x_grid` | The grid of the measure: caiso, ercot, isone, miso, nyiso, pjm, spp, outside_isos or us (every unit) | none | text | caiso, ercot, isone, miso, nyiso, outside_isos, pjm, spp, us | 0 |
| `x_metric` | The measure, the part of the variable after <grid>_ | none | text | operating_hours, operating_mw, operating_mwh, operating_rank, operating_share_pct, operating_units, owners_operating, owners_planned, planned_mw, planned_units, top10_share_pct, top5_share_pct | 0 |
| `x_owner` | The company's name as EIA-860M writes its Entity Name (the source's name: Entity Name) | none | text | for example 0HAM WHAM8 Solar, LLC, 147 Williamsville Solar 1, LLC, 160TIH WHAM8 Solar, LLC; 960 distinct | 180: Empty on a grid's own rows (not a company) |

Variables (108):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `caiso_operating_hours` | CAISO: operating MWh over the MW of the same units (average duration) | MWh/MW | 356 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_operating_mw` | CAISO: operating battery capacity, nameplate MW (a company: its own; a grid row: the grid total) | MW | 357 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_operating_mwh` | CAISO: operating battery energy capacity, of the units that report it | MWh | 357 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_operating_rank` | CAISO: the company's position by operating MW in the grid (1 the largest) | count | 355 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_operating_share_pct` | CAISO: the company's share of the grid's operating MW, percent | pct | 355 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_operating_units` | CAISO: operating battery units | count | 357 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_owners_operating` | CAISO: companies with operating battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_owners_planned` | CAISO: companies with planned battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_planned_mw` | CAISO: planned battery capacity, nameplate MW | MW | 144 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_planned_units` | CAISO: planned battery units | count | 144 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_top10_share_pct` | CAISO: share of the grid's operating MW held by its 10 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `caiso_top5_share_pct` | CAISO: share of the grid's operating MW held by its 5 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_operating_hours` | ERCOT: operating MWh over the MW of the same units (average duration) | MWh/MW | 324 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_operating_mw` | ERCOT: operating battery capacity, nameplate MW (a company: its own; a grid row: the grid total) | MW | 324 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_operating_mwh` | ERCOT: operating battery energy capacity, of the units that report it | MWh | 324 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_operating_rank` | ERCOT: the company's position by operating MW in the grid (1 the largest) | count | 322 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_operating_share_pct` | ERCOT: the company's share of the grid's operating MW, percent | pct | 322 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_operating_units` | ERCOT: operating battery units | count | 324 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_owners_operating` | ERCOT: companies with operating battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_owners_planned` | ERCOT: companies with planned battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_planned_mw` | ERCOT: planned battery capacity, nameplate MW | MW | 202 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_planned_units` | ERCOT: planned battery units | count | 202 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_top10_share_pct` | ERCOT: share of the grid's operating MW held by its 10 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `ercot_top5_share_pct` | ERCOT: share of the grid's operating MW held by its 5 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_operating_hours` | ISO-NE: operating MWh over the MW of the same units (average duration) | MWh/MW | 200 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_operating_mw` | ISO-NE: operating battery capacity, nameplate MW (a company: its own; a grid row: the grid total) | MW | 200 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_operating_mwh` | ISO-NE: operating battery energy capacity, of the units that report it | MWh | 200 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_operating_rank` | ISO-NE: the company's position by operating MW in the grid (1 the largest) | count | 198 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_operating_share_pct` | ISO-NE: the company's share of the grid's operating MW, percent | pct | 198 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_operating_units` | ISO-NE: operating battery units | count | 200 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_owners_operating` | ISO-NE: companies with operating battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_owners_planned` | ISO-NE: companies with planned battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_planned_mw` | ISO-NE: planned battery capacity, nameplate MW | MW | 42 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_planned_units` | ISO-NE: planned battery units | count | 42 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_top10_share_pct` | ISO-NE: share of the grid's operating MW held by its 10 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `isone_top5_share_pct` | ISO-NE: share of the grid's operating MW held by its 5 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_operating_hours` | MISO: operating MWh over the MW of the same units (average duration) | MWh/MW | 50 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_operating_mw` | MISO: operating battery capacity, nameplate MW (a company: its own; a grid row: the grid total) | MW | 50 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_operating_mwh` | MISO: operating battery energy capacity, of the units that report it | MWh | 50 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_operating_rank` | MISO: the company's position by operating MW in the grid (1 the largest) | count | 48 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_operating_share_pct` | MISO: the company's share of the grid's operating MW, percent | pct | 48 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_operating_units` | MISO: operating battery units | count | 50 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_owners_operating` | MISO: companies with operating battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_owners_planned` | MISO: companies with planned battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_planned_mw` | MISO: planned battery capacity, nameplate MW | MW | 38 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_planned_units` | MISO: planned battery units | count | 38 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_top10_share_pct` | MISO: share of the grid's operating MW held by its 10 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `miso_top5_share_pct` | MISO: share of the grid's operating MW held by its 5 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_operating_hours` | NYISO: operating MWh over the MW of the same units (average duration) | MWh/MW | 68 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_operating_mw` | NYISO: operating battery capacity, nameplate MW (a company: its own; a grid row: the grid total) | MW | 68 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_operating_mwh` | NYISO: operating battery energy capacity, of the units that report it | MWh | 68 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_operating_rank` | NYISO: the company's position by operating MW in the grid (1 the largest) | count | 66 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_operating_share_pct` | NYISO: the company's share of the grid's operating MW, percent | pct | 66 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_operating_units` | NYISO: operating battery units | count | 68 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_owners_operating` | NYISO: companies with operating battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_owners_planned` | NYISO: companies with planned battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_planned_mw` | NYISO: planned battery capacity, nameplate MW | MW | 19 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_planned_units` | NYISO: planned battery units | count | 19 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_top10_share_pct` | NYISO: share of the grid's operating MW held by its 10 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `nyiso_top5_share_pct` | NYISO: share of the grid's operating MW held by its 5 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_operating_hours` | outside the seven ISOs: operating MWh over the MW of the same units (average duration) | MWh/MW | 311 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_operating_mw` | outside the seven ISOs: operating battery capacity, nameplate MW (a company: its own; a grid row: the grid total) | MW | 311 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_operating_mwh` | outside the seven ISOs: operating battery energy capacity, of the units that report it | MWh | 311 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_operating_rank` | outside the seven ISOs: the company's position by operating MW in the grid (1 the largest) | count | 309 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_operating_share_pct` | outside the seven ISOs: the company's share of the grid's operating MW, percent | pct | 309 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_operating_units` | outside the seven ISOs: operating battery units | count | 311 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_owners_operating` | outside the seven ISOs: companies with operating battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_owners_planned` | outside the seven ISOs: companies with planned battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_planned_mw` | outside the seven ISOs: planned battery capacity, nameplate MW | MW | 192 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_planned_units` | outside the seven ISOs: planned battery units | count | 192 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_top10_share_pct` | outside the seven ISOs: share of the grid's operating MW held by its 10 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `outside_isos_top5_share_pct` | outside the seven ISOs: share of the grid's operating MW held by its 5 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_operating_hours` | PJM: operating MWh over the MW of the same units (average duration) | MWh/MW | 74 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_operating_mw` | PJM: operating battery capacity, nameplate MW (a company: its own; a grid row: the grid total) | MW | 74 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_operating_mwh` | PJM: operating battery energy capacity, of the units that report it | MWh | 74 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_operating_rank` | PJM: the company's position by operating MW in the grid (1 the largest) | count | 72 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_operating_share_pct` | PJM: the company's share of the grid's operating MW, percent | pct | 72 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_operating_units` | PJM: operating battery units | count | 74 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_owners_operating` | PJM: companies with operating battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_owners_planned` | PJM: companies with planned battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_planned_mw` | PJM: planned battery capacity, nameplate MW | MW | 43 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_planned_units` | PJM: planned battery units | count | 43 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_top10_share_pct` | PJM: share of the grid's operating MW held by its 10 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `pjm_top5_share_pct` | PJM: share of the grid's operating MW held by its 5 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_operating_hours` | SPP: operating MWh over the MW of the same units (average duration) | MWh/MW | 30 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_operating_mw` | SPP: operating battery capacity, nameplate MW (a company: its own; a grid row: the grid total) | MW | 30 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_operating_mwh` | SPP: operating battery energy capacity, of the units that report it | MWh | 30 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_operating_rank` | SPP: the company's position by operating MW in the grid (1 the largest) | count | 28 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_operating_share_pct` | SPP: the company's share of the grid's operating MW, percent | pct | 28 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_operating_units` | SPP: operating battery units | count | 30 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_owners_operating` | SPP: companies with operating battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_owners_planned` | SPP: companies with planned battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_planned_mw` | SPP: planned battery capacity, nameplate MW | MW | 30 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_planned_units` | SPP: planned battery units | count | 30 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_top10_share_pct` | SPP: share of the grid's operating MW held by its 10 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `spp_top5_share_pct` | SPP: share of the grid's operating MW held by its 5 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_operating_hours` | the whole US: operating MWh over the MW of the same units (average duration) | MWh/MW | 1320 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_operating_mw` | the whole US: operating battery capacity, nameplate MW (a company: its own; a grid row: the grid total) | MW | 1321 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_operating_mwh` | the whole US: operating battery energy capacity, of the units that report it | MWh | 1321 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_operating_rank` | the whole US: the company's position by operating MW in the grid (1 the largest) | count | 1319 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_operating_share_pct` | the whole US: the company's share of the grid's operating MW, percent | pct | 1319 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_operating_units` | the whole US: operating battery units | count | 1321 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_owners_operating` | the whole US: companies with operating battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_owners_planned` | the whole US: companies with planned battery units (grid row) | count | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_planned_mw` | the whole US: planned battery capacity, nameplate MW | MW | 658 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_planned_units` | the whole US: planned battery units | count | 658 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_top10_share_pct` | the whole US: share of the grid's operating MW held by its 10 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `us_top5_share_pct` | the whole US: share of the grid's operating MW held by its 5 largest companies, percent (grid row) | pct | 2 | 2026-08-01T00:00:00Z | 2026-09-01T00:00:00Z |

