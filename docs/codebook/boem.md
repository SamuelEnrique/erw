# Codebook: boem

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 3 public tables (2 entities, 1 series; tiers: 3 source); 0 documented in full.

- [`boem_offshore_platforms`](#boem_offshore_platforms): Bureau of Ocean Energy Management (BOEM), Data Center, Platform Structures, Platform Locations and Platform Masters: every oil and gas structure on the Outer Continental Shelf, installed or removed, with its place, dates and its complex's fields (session 2007)
- [`boem_ogor_lease_production_monthly`](#boem_ogor_lease_production_monthly): BOEM, offshore oil and gas production by lease, a month, the Gulf of America, from OGOR-A well production (session 611)
- [`boem_renewable_leases`](#boem_renewable_leases): BOEM, every renewable energy lease and grant on the Outer Continental Shelf (session 493)

### `boem_offshore_platforms`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 7092.

- **Source:** boem:platforms Bureau of Ocean Energy Management, Data Center, Platform (https://www.data.boem.gov/Main/Platform.aspx)
- **Method note:** [`docs/methods/boem_offshore_platforms.md`](../methods/boem_offshore_platforms.md)
- **Cite as:** Bureau of Ocean Energy Management (BOEM). Data Center: Platform Structures, Platform Locations and Platform Masters. Via the Energy Research Warehouse (ERW), table `boem_offshore_platforms`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example boem_platform:10-1, boem_platform:10001-1, boem_platform:10002-1; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | platform | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example #1, #1(A), #13; 979 distinct | 1 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 26.035697 to 30.194974; more than 5000 distinct | 8 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -97.113264 to -87.757633; more than 5000 distinct | 8 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 7092 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | active, retired | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | date | 1949-01-01 to 2026-09-21; 4065 distinct | 0 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 7092 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | boem:platforms | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.data.boem.gov/Platform/Files/platstrufixed.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T15:24:58Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-01T15:03:11Z | 0 |
| `x_complex_id` | not yet written |  | integer | 2 to 90028; more than 5000 distinct | 0 |
| `x_structure_number` | not yet written |  | integer | 1, 10, 11, 12, 13, 14, 15, 16, 17, 2, 3, 4, 5, 6, 7, 8, 9 | 0 |
| `x_area_code` | not yet written |  | text | for example AC, BA, BM; 35 distinct | 0 |
| `x_block_number` | not yet written |  | text | for example 1, 10, 100; 940 distinct | 0 |
| `x_district` | not yet written |  | integer | 1, 2, 3, 4, 5 | 8 |
| `x_structure_type` | not yet written |  | text | CAIS, CT, FIXED, FPSO, MOPU, MTLP, SEMI, SPAR, SSTMP, TLP, WP | 0 |
| `x_install_date` | not yet written |  | date | 1942-01-01 to 2025-07-17; 1894 distinct | 0 |
| `x_removal_date` | not yet written |  | date | 1973-12-31 to 2026-09-21; 3701 distinct | 1312 |
| `x_deck_count` | not yet written |  | integer | 0, 1, 2, 3, 4, 5, 6, 7 | 102 |
| `x_slot_count` | not yet written |  | integer | 0 to 62; 43 distinct | 217 |
| `x_major_structure` | not yet written |  | text | N, Y | 0 |
| `x_authority_status` | not yet written |  | text | ACT, Approved, EXP, EXPIR, NO-ISS, PRIMRY, PROD, RELINQ, RELQ, SOP, TERMIN, UNIT | 340 |
| `x_company_num` | not yet written |  | integer | 1 to 3748; 333 distinct | 0 |
| `x_water_depth_ft` | not yet written |  | integer | 1 to 9560; 474 distinct | 0 |
| `x_distance_to_shore_nmi` | not yet written |  | integer | 0 to 180; 143 distinct | 73 |
| `x_lease_number` | not yet written |  | text | for example 00016, 00018, 00019; 2808 distinct | 278 |
| `x_field_name_code` | not yet written |  | text | for example 313, 829A, AC025; 1114 distinct | 225 |
| `x_production` | not yet written |  | text | N, Y | 53 |
| `x_oil_production` | not yet written |  | text | N, Y | 272 |
| `x_gas_production` | not yet written |  | text | N, Y | 49 |
| `x_manned_24h` | not yet written |  | text | N, Y | 3 |
| `x_to_be_removed` | not yet written |  | text | N, Y | 5 |

### `boem_ogor_lease_production_monthly`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1131562.

- **Source:** boem:ogor_a Bureau of Ocean Energy Management, Oil and Gas Operations Reports Part A (OGOR-A), well production (https://www.data.boem.gov/Main/OGOR-A.aspx)
- **Method note:** [`docs/methods/boem_ogor_lease_production_monthly.md`](../methods/boem_ogor_lease_production_monthly.md)
- **Cite as:** Bureau of Ocean Energy Management (BOEM). Oil and Gas Operations Reports Part A (OGOR-A), well production, by year. Via the Energy Research Warehouse (ERW), table `boem_ogor_lease_production_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example boem_lease:00016, boem_lease:00018, boem_lease:00019; 4654 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1996-01-01T00:00:00Z to 2026-06-01T00:00:00Z; 366 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 10806.988; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf, kbbl | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1131562 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example AEDC USA INC, ALLIED NATURAL GAS CORPORATION, AMCO ENERGY INC; 1378 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | boem:ogor_a | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.data.boem.gov/Production/Files/ogora1996delimit.zip, https://www.data.boem.gov/Production/Files/ogora1997delimit.zip, https://www.data.boem.gov/Production/Files/ogora1998delimit.zip; 31 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-22T01:37:52Z to 2026-10-22T02:48:37Z; 31 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-01T11:32:32Z to 2026-10-15T17:57:37Z; 31 distinct | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `gas_production` |  | MMcf | 565781 | 1996-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `oil_production` |  | kbbl | 565781 | 1996-01-01T00:00:00Z | 2026-06-01T00:00:00Z |

### `boem_renewable_leases`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 52.

- **Source:** boem:lease_and_grant_information Bureau of Ocean Energy Management (BOEM), Lease and Grant Information (renewable energy) (https://www.boem.gov/renewable-energy/lease-and-grant-information)
- **Method note:** [`docs/methods/boem_renewable_leases.md`](../methods/boem_renewable_leases.md)
- **Cite as:** Bureau of Ocean Energy Management (BOEM). Renewable energy Lease and Grant Information. Via the Energy Research Warehouse (ERW), table `boem_renewable_leases`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example boem:ocs-a_0472, boem:ocs-a_0473, boem:ocs-a_0474; 52 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example Atlantic Offshore Wind, Atlantic Shores North, Atlantic Shores South; 43 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 52 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 52 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 52 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | active | 18 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 52 |
| `operator` | The operator or owner, as the publisher writes it | none | text | for example Atlantic Shores Offshore Wind Bight, LLC, Atlantic Shores Offshore Wind Project 1, LLC; Atlantic Shores Offshore Wind Project 2, LLC, Atlantic Shores Offshore Wind, LLC; 48 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | boem:lease_and_grant_information | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.boem.gov/renewable-energy/lease-and-grant-information | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T18:33:10Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 52 |
| `lease_number` | not yet written |  | text | for example OCS-A 0472, OCS-A 0473, OCS-A 0474; 52 distinct | 0 |
| `lessee` | not yet written |  | text | for example Atlantic Shores Offshore Wind Bight, LLC, Atlantic Shores Offshore Wind Project 1, LLC; Atlantic Shores Offshore Wind Project 2, LLC, Atlantic Shores Offshore Wind, LLC; 48 distinct | 0 |
| `authorization` | not yet written |  | text | Commercial Lease, Commercial Lease*, Interim Policy Lease*, Research Lease, Research Lease*, Right of Way Grant | 0 |
| `resource_type` | not yet written |  | text | Marine Hydrokinetic, Marine Hydrokinetic Wind, Wind | 0 |
| `effective_year` | not yet written |  | integer | 2009, 2010, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024 | 0 |
| `boem_status` | not yet written |  | text | Active, Cancelled, Consolidated, Expired, Relinquished | 0 |

