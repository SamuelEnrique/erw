# Codebook: boem

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 3 public tables (2 entities, 1 series; tiers: 3 source); 3 documented in full.

- [`boem_offshore_platforms`](#boem_offshore_platforms): One structure of an oil and gas platform complex on the Outer Continental Shelf, installed or removed, with its place, dates and its complex's fields, from BOEM's Platform Structures, Locations and Masters files.
- [`boem_ogor_lease_production_monthly`](#boem_ogor_lease_production_monthly): The oil or gas produced on one offshore lease (or unit agreement) in the Gulf of America in one month, summed over its completions, from BOEM's OGOR-A well production reports.
- [`boem_renewable_leases`](#boem_renewable_leases): One renewable energy lease or grant on the Outer Continental Shelf, as BOEM's Lease and Grant Information page lists it.

### `boem_offshore_platforms`

One structure of an oil and gas platform complex on the Outer Continental Shelf, installed or removed, with its place, dates and its complex's fields, from BOEM's Platform Structures, Locations and Masters files.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 7092.

- **Time:** No time column; status_date is the removal date where BOEM gives one, else the install date.
- **Revisions:** A snapshot; each run replaces the table whole. vintage is the structures file's last-modified time.
- **Source:** boem:platforms Bureau of Ocean Energy Management, Data Center, Platform (https://www.data.boem.gov/Main/Platform.aspx)
- **Method note:** [`docs/methods/boem_offshore_platforms.md`](../methods/boem_offshore_platforms.md)
- **Cite as:** Bureau of Ocean Energy Management (BOEM). Data Center: Platform Structures, Platform Locations and Platform Masters. Via the Energy Research Warehouse (ERW), table `boem_offshore_platforms`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: boem_platform:<complex id>-<structure number> | none | text | for example boem_platform:10-1, boem_platform:10001-1, boem_platform:10002-1; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always platform | none | text | platform | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The structure's name (one has none) | none | text | for example #1, #1(A), #13; 979 distinct | 1 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always US (federal waters) | none | text | US | 0 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: From the locations file; empty for 8 structures with no location row | degree | number | 26.035697 to 30.194974; more than 5000 distinct | 8 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: From the locations file; empty for 8 structures with no location row | degree | number | -97.113264 to -87.757633; more than 5000 distinct | 8 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: Not filled | MW | empty | no cell holds a value | 7092 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: retired where BOEM gives a removal date, else active | none | text | active, retired | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The removal date, else the install date | none | date | 1949-01-01 to 2026-09-21; 4065 distinct | 0 |
| `operator` | The operator or owner, as the publisher writes it. Here: Not filled: BOEM gives a company number (x_company_num), not a name | none | empty | no cell holds a value | 7092 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | boem:platforms | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.data.boem.gov/Platform/Files/platstrufixed.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T15:24:58Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The structures file's last-modified time | none | utc time | 2026-10-01T15:03:11Z | 0 |
| `x_complex_id` | BOEM's complex identifier (leading zeros dropped) (the source's name: Complex Id Num) | none | integer | 2 to 90028; more than 5000 distinct | 0 |
| `x_structure_number` | The structure's number within its complex (leading zeros dropped) (the source's name: Structure Number) | none | integer | 1, 10, 11, 12, 13, 14, 15, 16, 17, 2, 3, 4, 5, 6, 7, 8, 9 | 0 |
| `x_area_code` | BOEM's code of the offshore area (the source's name: Area Code) | none | text | for example AC, BA, BM; 35 distinct | 0 |
| `x_block_number` | The block number within the area (the source's name: Block Number) | none | text | for example 1, 10, 100; 940 distinct | 0 |
| `x_district` | BOEM's district code, from the locations file (the source's name: District Code) | none | integer | 1, 2, 3, 4, 5 | 8: No location row (8 structures) |
| `x_structure_type` | BOEM's structure type code: FIXED fixed, CAIS caisson, WP well protector, and SEMI, SPAR, TLP, MTLP, MOPU, CT, FPSO, SSTMP as BOEM codes them (the source's name: Structure Type Code) | none | text | CAIS, CT, FIXED, FPSO, MOPU, MTLP, SEMI, SPAR, SSTMP, TLP, WP | 0 |
| `x_install_date` | The date the structure was installed (the source's name: Install Date) | none | date | 1942-01-01 to 2025-07-17; 1894 distinct | 0 |
| `x_removal_date` | The date the structure was removed (the source's name: Removal Date) | none | date | 1973-12-31 to 2026-09-21; 3701 distinct | 1312: Not removed (active) |
| `x_deck_count` | The structure's number of decks (the source's name: Deck Count) | count | integer | 0, 1, 2, 3, 4, 5, 6, 7 | 102: BOEM gives none |
| `x_slot_count` | The structure's number of slots (the source's name: Slot Count) | count | integer | 0 to 62; 43 distinct | 217: BOEM gives none |
| `x_major_structure` | BOEM's major structure flag, Y or N (the source's name: Major Structure Flag) | none | text | N, Y | 0 |
| `x_authority_status` | BOEM's authority status code of the structure (TERMIN, RELINQ, UNIT, PROD and the others), as BOEM writes it (the source's name: Authority Status) | none | text | ACT, Approved, EXP, EXPIR, NO-ISS, PRIMRY, PROD, RELINQ, RELQ, SOP, TERMIN, UNIT | 340: BOEM gives none |
| `x_company_num` | BOEM's company number of the complex's company (no name given) (the source's name: Mms Company Num) | none | integer | 1 to 3748; 333 distinct | 0 |
| `x_water_depth_ft` | The complex's water depth (the source's name: Water Depth) | ft | integer | 1 to 9560; 474 distinct | 0 |
| `x_distance_to_shore_nmi` | The complex's distance to shore (the source's name: Distance To Shore) | nautical mile | integer | 0 to 180; 143 distinct | 73: BOEM gives none |
| `x_lease_number` | The lease named on the complex's masters row (the source's name: Lease Number) | none | text | for example 00016, 00018, 00019; 2808 distinct | 278: BOEM gives none |
| `x_field_name_code` | BOEM's field name code of the complex (the source's name: Field Name Code) | none | text | for example 313, 829A, AC025; 1114 distinct | 225: BOEM gives none |
| `x_production` | BOEM's production flag of the complex, Y or N (the source's name: Production Flag) | none | text | N, Y | 53: BOEM gives none |
| `x_oil_production` | BOEM's oil production flag of the complex, Y or N (the source's name: Oil Prod Flag) | none | text | N, Y | 272: BOEM gives none |
| `x_gas_production` | BOEM's gas production flag of the complex, Y or N (the source's name: Gas Prod Flag) | none | text | N, Y | 49: BOEM gives none |
| `x_manned_24h` | Whether the complex is manned 24 hours, Y or N (the source's name: Manned 24 Hr Fl) | none | text | N, Y | 3: BOEM gives none |
| `x_to_be_removed` | BOEM's abandon flag (to be removed), Y or N (the source's name: Abandon Flag) | none | text | N, Y | 5: BOEM gives none |

Waiting for a second look: x_structure_type: SEMI, SPAR, TLP, MTLP, MOPU, CT, FPSO and SSTMP are kept as BOEM codes them; the method note does not expand them.; x_authority_status: its codes (ACT, EXP, EXPIR, NO-ISS, PRIMRY, PROD, RELINQ, RELQ, SOP, TERMIN, UNIT, Approved) are not expanded in the method note or the connector..

### `boem_ogor_lease_production_monthly`

The oil or gas produced on one offshore lease (or unit agreement) in the Gulf of America in one month, summed over its completions, from BOEM's OGOR-A well production reports.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1131562.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M.
- **Revisions:** Rewritten whole by each run (write_snapshot); a year's saved file is reused unless asked again, so BOEM's revision reaches the table only then. vintage is each year's file's Last-Modified time.
- **Source:** boem:ogor_a Bureau of Ocean Energy Management, Oil and Gas Operations Reports Part A (OGOR-A), well production (https://www.data.boem.gov/Main/OGOR-A.aspx)
- **Method note:** [`docs/methods/boem_ogor_lease_production_monthly.md`](../methods/boem_ogor_lease_production_monthly.md)
- **Cite as:** Bureau of Ocean Energy Management (BOEM). Oil and Gas Operations Reports Part A (OGOR-A), well production, by year. Via the Energy Research Warehouse (ERW), table `boem_ogor_lease_production_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: boem_lease:<lease number>, or boem_unit:<unit agreement> where BOEM gives no lease | none | text | for example boem_lease:00016, boem_lease:00018, boem_lease:00019; 4654 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1996-01-01T00:00:00Z to 2026-06-01T00:00:00Z; 366 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 10806.988; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMcf, kbbl | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always US | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1131562 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The lease's operators that month, not a pricing node | none | text | for example AEDC USA INC, ALLIED NATURAL GAS CORPORATION, AMCO ENERGY INC; 1378 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | boem:ogor_a | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.data.boem.gov/Production/Files/ogora1996delimit.zip, https://www.data.boem.gov/Production/Files/ogora1997delimit.zip, https://www.data.boem.gov/Production/Files/ogora1998delimit.zip; 31 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-22T01:37:52Z to 2026-10-22T02:48:37Z; 31 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The year's file's Last-Modified time | none | utc time | 2026-10-01T11:32:32Z to 2026-10-15T17:57:37Z; 31 distinct | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `gas_production` | Gas produced on the lease in the month, MMcf (BOEM's thousand cubic feet over 1,000) | MMcf | 565781 | 1996-01-01T00:00:00Z | 2026-06-01T00:00:00Z |
| `oil_production` | Oil produced on the lease in the month, kbbl (BOEM's barrels over 1,000) | kbbl | 565781 | 1996-01-01T00:00:00Z | 2026-06-01T00:00:00Z |

### `boem_renewable_leases`

One renewable energy lease or grant on the Outer Continental Shelf, as BOEM's Lease and Grant Information page lists it.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 52.

- **Time:** No time column; status_date is not filled.
- **Revisions:** A snapshot; each run replaces the table whole, and a lease that leaves BOEM's page leaves the table. vintage is not filled (the page carries no date).
- **Source:** boem:lease_and_grant_information Bureau of Ocean Energy Management (BOEM), Lease and Grant Information (renewable energy) (https://www.boem.gov/renewable-energy/lease-and-grant-information)
- **Method note:** [`docs/methods/boem_renewable_leases.md`](../methods/boem_renewable_leases.md)
- **Cite as:** Bureau of Ocean Energy Management (BOEM). Renewable energy Lease and Grant Information. Via the Energy Research Warehouse (ERW), table `boem_renewable_leases`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: boem:<lease or grant number> | none | text | for example boem:ocs-a_0472, boem:ocs-a_0473, boem:ocs-a_0474; 52 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always project | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example Atlantic Offshore Wind, Atlantic Shores North, Atlantic Shores South; 43 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always US: the page names no state | none | text | US | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 52 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | empty | no cell holds a value | 52 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 52 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: active for BOEM's Active, empty for its other words (kept in boem_status) | none | text | active | 18 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 52 |
| `operator` | The operator or owner, as the publisher writes it. Here: The lessee or grantee | none | text | for example Atlantic Shores Offshore Wind Bight, LLC, Atlantic Shores Offshore Wind Project 1, LLC; Atlantic Shores Offshore Wind Project 2, LLC, Atlantic Shores Offshore Wind, LLC; 48 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | boem:lease_and_grant_information | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.boem.gov/renewable-energy/lease-and-grant-information | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-21T18:33:10Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 52 |
| `lease_number` | BOEM's lease or grant number (OCS-A 0472) | none | text | for example OCS-A 0472, OCS-A 0473, OCS-A 0474; 52 distinct | 0 |
| `lessee` | The lessee or grantee, as BOEM names it (the source's name: Lessee or Grantee) | none | text | for example Atlantic Shores Offshore Wind Bight, LLC, Atlantic Shores Offshore Wind Project 1, LLC; Atlantic Shores Offshore Wind Project 2, LLC, Atlantic Shores Offshore Wind, LLC; 48 distinct | 0 |
| `authorization` | BOEM's authorization resource type (Commercial Lease, Interim Policy Lease, Research Lease, Right of Way Grant), with its '*' note mark kept (the source's name: Authorization Resource Type) | none | text | Commercial Lease, Commercial Lease*, Interim Policy Lease*, Research Lease, Research Lease*, Right of Way Grant | 0 |
| `resource_type` | BOEM's resource type (Wind, Marine Hydrokinetic, Marine Hydrokinetic Wind) (the source's name: Resource Type) | none | text | Marine Hydrokinetic, Marine Hydrokinetic Wind, Wind | 0 |
| `effective_year` | The lease's effective year, as BOEM gives it | none | integer | 2009, 2010, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024 | 0 |
| `boem_status` | BOEM's own status word (Active, Cancelled, Relinquished, Expired, Consolidated) (the source's name: Status) | none | text | Active, Cancelled, Consolidated, Expired, Relinquished | 0 |

Waiting for a second look: authorization: what BOEM's '*' note mark means is not documented; it is kept as BOEM writes it..

