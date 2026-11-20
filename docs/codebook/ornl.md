# Codebook: ornl

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 5 public tables (4 entities, 1 events; tiers: 5 source); 0 documented in full.

- [`ornl_eha_hydropower_plants`](#ornl_eha_hydropower_plants): Oak Ridge National Laboratory, Existing Hydropower Assets (EHA) Plant Database, 2026: every U.S. hydropower and pumped storage plant (session 911)
- [`ornl_eha_hydropower_units`](#ornl_eha_hydropower_units): Oak Ridge National Laboratory, Existing Hydropower Assets (EHA) Unit Database, 2026: every U.S. hydropower and pumped storage unit (session 943)
- [`ornl_hydropower_pipeline`](#ornl_hydropower_pipeline): Oak Ridge National Laboratory, U.S. Hydropower Development Pipeline, 2026: proposed hydropower and pumped storage projects on 31 December 2025 (session 916)
- [`ornl_hydropower_relicensing`](#ornl_hydropower_relicensing): Oak Ridge National Laboratory, U.S. Hydropower Relicensing and License Surrender data, 2026: every project in FERC relicensing or surrender on 31 December 2025 (session 930)
- [`ornl_npd_potential`](#ornl_npd_potential): Oak Ridge National Laboratory, U.S. hydropower potential at existing non-powered dams greater than 1 MW (the 2012 national assessment) (session 938)

### `ornl_eha_hydropower_plants`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 2257.

- **Source:** ornl:eha_plant M.M. Johnson, S.-C. Kao and R. Uria-Martinez, Existing Hydropower Assets (EHA) Plant Database, 2026, HydroSource, Oak Ridge National Laboratory, Oak Ridge, Tennessee, DOI 10.21951/EHA_FY2026/3374497 (https://hydrosource.ornl.gov/data/datasets/eha-plant-2026/)
- **Method note:** [`docs/methods/ornl_hydropower.md`](../methods/ornl_hydropower.md)
- **Cite as:** Oak Ridge National Laboratory (ORNL), HydroSource. Existing Hydropower Assets (EHA) Plant Database. Via the Energy Research Warehouse (ERW), table `ornl_eha_hydropower_plants`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example ornl_eha:hc0001_p01, ornl_eha:hc0002_p01, ornl_eha:hc0003_p01; 2257 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | plant | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 29 Mile Creek Diversion, 45-Mile Hydroelectric Project, 92nd Avenue Pressure Relief Valve Facility Project; 2192 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 49 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 18.017 to 61.6; 2183 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -174.197 to -65.794; 2192 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | 5e-05 to 6809.0; 783 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | empty | no cell holds a value | 2257 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 2257 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 2257 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ornl:eha_plant | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/EHA2026/ORNL_EHAHydroPlant_PublicFY2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T08:09:05Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-07-17T16:30:08Z | 0 |
| `eha_plant_id` | not yet written |  | text | for example hc0001_p01, hc0002_p01, hc0003_p01; 2257 distinct | 0 |
| `eia_plant_id` | not yet written |  | integer | 2 to 69673; 1624 distinct | 608 |
| `state` | not yet written |  | text | for example AK, AL, AR; 49 distinct | 0 |
| `county` | not yet written |  | text | for example Abbeville, Ada, Ada, Owyhee; 610 distinct | 23 |
| `county_fips` | not yet written |  | integer | 1001 to 56039; 639 distinct | 173 |
| `plant_owner` | not yet written |  | text | for example 2C Land & Cattle Company, LLC, 5440 Hydro, Inc., 8 CHURCH LANE, LLC.; 1053 distinct | 0 |
| `owner_type` | not yet written |  | text | Cooperative, Industrial, Investor-Owned Utility, Municipal, Political subdivision, Private Non-utility, Private non-utility, Publicly Owned Utility, Reclamation, State, TVA, USACE, Unknown, Wholesale Power Marketer | 0 |
| `dam_owner` | not yet written |  | text | for example 5440 Hydro, Inc., 8 CHURCH LANE, LLC., A & D Hydro, Inc.; 946 distinct | 163 |
| `plant_type` | not yet written |  | text | HY, HY/PSH, PSH | 0 |
| `ferc_docket` | not yet written |  | text | for example CD13-1, CD13-4, CD13-7; 1556 distinct | 369 |
| `ferc_issued` | not yet written |  | date | 1952-07-21 to 2025-11-26; 1151 distinct | 391 |
| `ferc_expires` | not yet written |  | date | 2003-04-26 to 2074-08-31; 411 distinct | 1034 |
| `mode` | not yet written |  | text | Canal/Conduit, Intermediate Peaking, Peaking, Reregulating, Run-of-river, Run-of-river/Peaking, Run-of-river/Upstream Peaking, Unknown | 764 |
| `permitting` | not yet written |  | text | FERC Exemption, FERC License, FERC Qualifying Conduit, LOPP, Non-FERC regulated, Not Required, Reclamation, Reclamation LOPP, Reclamation Others, Reclamation Transferred, TVA, USACE, Unknown | 2 |
| `units` | not yet written |  | integer | 1, 10, 11, 12, 13, 14, 15, 16, 19, 2, 20, 21, 24, 27, 3, 33, 4, 5, 6, 7, 73, 8, 9 | 2 |
| `hy_mw` | not yet written |  | number | 5e-05 to 6495.0; 761 distinct | 26 |
| `hy_avg_mwh` | not yet written |  | number | 0.012 to 19194991.32; 1808 distinct | 337 |
| `hy_capacity_factor_pct` | not yet written |  | number | 0.0273972602739726 to 6019.85901826484; 1858 distinct | 336 |
| `hy_first_year` | not yet written |  | integer | 1891 to 2024; 131 distinct | 117 |
| `psh_mw` | not yet written |  | number | 0.14 to 2862.0; 40 distinct | 2216 |
| `psh_avg_mwh` | not yet written |  | number | 13908.04 to 3809539.67; 39 distinct | 2218 |
| `psh_capacity_factor_pct` | not yet written |  | number | 3.08618663039871 to 34.2278807413376; 39 distinct | 2218 |
| `psh_first_year` | not yet written |  | integer | 1927, 1928, 1954, 1956, 1961, 1963, 1965, 1967, 1968, 1970, 1971, 1972, 1973, 1974, 1977, 1978, 1979, 1981, 1984, 1985, 1987, 1991, 1993, 1995, 2002 | 2218 |
| `waterway` | not yet written |  | text | for example -99 (canal), ALDER BROOK, ANCHORAGE WATER & WASTEWATER PL; 1149 distinct | 35 |
| `huc` | not yet written |  | number | 10100040901.0 to 210100050202.0; 1621 distinct | 3 |
| `nerc_region` | not yet written |  | text | MRO, NPCC, RFC, SERC, SPP, TRE, WECC | 85 |
| `balancing_authority` | not yet written |  | text | for example AECI, AVA, BANC; 44 distinct | 811 |
| `eia_sector` | not yet written |  | text | Commercial CHP, Commercial Non-CHP, Electric Utility, IPP, IPP CHP, IPP Non-CHP, Industrial, Industrial CHP, Industrial Non-CHP | 758 |
| `transmission_owner` | not yet written |  | text | for example AEP Texas Central Company, ALLETE, Inc., Alabama Power Co; 232 distinct | 769 |

### `ornl_eha_hydropower_units`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 5362.

- **Source:** ornl:eha_unit M.M. Johnson, S.-C. Kao and R. Uria-Martinez, Existing Hydropower Assets (EHA) Unit Database, 2026, HydroSource, Oak Ridge National Laboratory, Oak Ridge, Tennessee, DOI 10.21951/FY2026/3374522 (https://hydrosource.ornl.gov/data/datasets/eha-unit-2026/)
- **Method note:** [`docs/methods/ornl_hydropower.md`](../methods/ornl_hydropower.md)
- **Cite as:** Oak Ridge National Laboratory (ORNL), HydroSource. Existing Hydropower Assets (EHA) Unit Database. Via the Energy Research Warehouse (ERW), table `ornl_eha_hydropower_units`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example ornl_eha_unit:hc0001_p01_1, ornl_eha_unit:hc0001_p01_2, ornl_eha_unit:hc0002_p01_1; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example 29 Mile Creek Diversion, unit 1, 45 Mile Hydroelectric Project, unit 1, 45 Mile Hydroelectric Project, unit 2; more than 5000 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | empty | no cell holds a value | 5362 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 18.017 to 61.6; 2184 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -174.197 to -65.794; 2193 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | 0.0 to 805.0; 680 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | empty | no cell holds a value | 5362 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 5362 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 5362 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ornl:eha_unit | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/eha-unit-2026/ORNL_EHAHydroUnit_PublicFY2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T11:18:37Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-06-24T16:53:31Z | 0 |
| `eha_plant_id` | not yet written |  | text | for example hc0001_p01, hc0002_p01, hc0003_p01; 2258 distinct | 0 |
| `plant_owner` | not yet written |  | text | for example 2C Land & Cattle Company, LLC, 5440 Hydro, Inc., 8 CHURCH LANE, LLC.; 1049 distinct | 6 |
| `unit_type` | not yet written |  | text | HY, PS | 0 |
| `eia_plant_id` | not yet written |  | integer | 2 to 69673; 1622 distinct | 937 |
| `eia_generator_id` | not yet written |  | text | for example 1, 10, 10A; 673 distinct | 951 |
| `eha_unit_id` | not yet written |  | text | for example 1, 10, 11; 74 distinct | 0 |
| `ferc_plant_id` | not yet written |  | text | for example 01 - 29 Mile Creek, 01 - A J Allen, 01 - A-Plant Powerhouse; 1738 distinct | 1510 |
| `first_year` | not yet written |  | integer | 1891 to 2025; 132 distinct | 143 |
| `refurbished_year` | not yet written |  | text | for example 1950, 1956, 1971; 49 distinct | 16 |
| `turbine_type` | not yet written |  | text | 10TR2, 5TR2, Archimedes Screw, Centrifugal, Francis, Horizontal Impulse, Horizontal Pump, Kaplan, Pelton, Pump, Unknown, Vertical | 1 |
| `turbine_maker` | not yet written |  | text | for example A & D, ABNER DOBLE COMPANY ENGINEERS, ALSTH; 165 distinct | 1823 |
| `speed_rpm` | not yet written |  | number | 54.5 to 1730.0; 50 distinct | 4903 |
| `head_ft` | not yet written |  | number | 1.08 to 2558.0; 628 distinct | 1530 |
| `power_hp` | not yet written |  | number | 0.24 to 960000.0; 1104 distinct | 1695 |
| `min_load_mw` | not yet written |  | number | 0.0 to 320.0; 195 distinct | 1241 |
| `start_time` | not yet written |  | text | 1, 10M, 12H, 1H, OVER | 1246 |
| `huc` | not yet written |  | number | 10100040901.0 to 210100050202.0; 1621 distinct | 3 |
| `county_fips` | not yet written |  | integer | 1001 to 56039; 639 distinct | 369 |

### `ornl_hydropower_pipeline`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 196.

- **Source:** ornl:hydro_pipeline M.M. Johnson and R. Uria-Martinez, U.S. Hydropower Development Pipeline Data, 2026, HydroSource, Oak Ridge National Laboratory, Oak Ridge, Tennessee, DOI 10.21951/HMR_PipelineFY26/3025030 (https://hydrosource.ornl.gov/data/datasets/us-hydropower-development-pipeline-data-2026/)
- **Method note:** [`docs/methods/ornl_hydropower.md`](../methods/ornl_hydropower.md)
- **Cite as:** Oak Ridge National Laboratory (ORNL), HydroSource. U.S. Hydropower Development Pipeline Data. Via the Energy Research Warehouse (ERW), table `ornl_hydropower_pipeline`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example ornl_hydro_pipeline:CD20-8, ornl_hydro_pipeline:CD21-5*, ornl_hydro_pipeline:CD22-1; 196 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example A. I. Selden Dam, Aberdeen Hydroelectric Project, Allegheny Lock & Dam 2; 196 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 33 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 31.18667 to 60.457491; 195 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -153.306198 to -70.37631; 196 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | 0.003 to 5287.0; 123 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | planned, under_construction | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | date | 2025-12-31 | 0 |
| `operator` | The operator or owner, as the publisher writes it | none | text | for example 3R Valve, Aberdeen Hydro AE, LLC, Alaska Village Electric Cooperative, Inc.; 161 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ornl:hydro_pipeline | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/us-hydropower-development-pipeline-data-2026/ORNL_US_Hydropower_DevelopmentPipeline_Data_2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T08:33:21Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-04-20T17:05:22Z | 0 |
| `ferc_docket` | not yet written |  | text | for example CD20-8, CD21-5*, CD22-1; 193 distinct | 3 |
| `permit_status` | not yet written |  | text | Issued Exemption, Issued LOPP Authorization, Issued License, Issued Preliminary Lease, Issued Preliminary Permit, Pending Exemption, Pending License, Pending Preliminary Permit, Under Construction | 0 |
| `project_type` | not yet written |  | text | HY, PSH | 0 |
| `project_subcategory` | not yet written |  | text | Conduit, New Stream-Reach Development, Non-Powered Dam, Pumped Storage Hydropower | 0 |
| `state` | not yet written |  | text | for example AK, AL, AR; 33 distinct | 0 |
| `county` | not yet written |  | text | for example Adams, Alameda, Alleghany; 148 distinct | 0 |
| `county_fips` | not yet written |  | integer | 1023 to 56023; 150 distinct | 0 |
| `developer_type` | not yet written |  | text | Cooperative, Investor-owned utility, Municipal, Political subdivision, Private non-utility, State | 0 |
| `dam_name` | not yet written |  | text | for example A.I. Selden Lock and Dam, Aberdeen Lock and Dam, Allegheny Lock & Dam 4; 89 distinct | 106 |
| `dam_owner` | not yet written |  | text | Bard College, Beaver Falls Municiple Authority, Bureau of Reclamation, CELRP, CEMVK, CEMVR, CENAB, CENAO, CESAM, Central Hudson Gas & Electric Corp, Commonwealth of Kentucky, Commonwealth of Pennsylvania, Department of Environmental Protection, Kentucky River Authority, RIDEM, Reclamation, Rhode Island Department of Environmental Management, State of New York Canal Corporation, Town of Cumberland, Town of West Warwick, USACE, Village of Swanton | 112 |
| `waterway` | not yet written |  | text | for example Alabama River, Allegheny River, Antelope Valley Water Storage; 71 distinct | 77 |
| `psh_configuration` | not yet written |  | text | Closed-Loop, Open-Loop | 128 |
| `nerc_region` | not yet written |  | text | MRO, NPCC, RFC, SERC, SPP, WECC | 8 |
| `huc` | not yet written |  | integer | 10400020505 to 190207011806; 184 distinct | 0 |

### `ornl_hydropower_relicensing`

What a row is: not yet written.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 559.

- **Source:** ornl:hydro_relicensing M.M. Johnson and R. Uria-Martinez, U.S. Hydropower Relicensing and License Surrender Data and Metadata, 2026, HydroSource, Oak Ridge National Laboratory, Oak Ridge, Tennessee, DOI 10.21951/HMR_RelicenseSurrender/3031244 (https://hydrosource.ornl.gov/data/datasets/us-hydropower-relicensing-and-license-surrender-data-2026/)
- **Method note:** [`docs/methods/ornl_hydropower.md`](../methods/ornl_hydropower.md)
- **Cite as:** Oak Ridge National Laboratory (ORNL), HydroSource. U.S. Hydropower Relicensing and License Surrender Data. Via the Energy Research Warehouse (ERW), table `ornl_hydropower_relicensing`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | none | text | for example ornl_relicense:P-1005:relicense, ornl_relicense:P-10198:relicense, ornl_relicense:P-10200:surrender; 559 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2001-08-30 to 2025-12-23; 439 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others) | none | text | hydro_license_surrender, hydro_relicense | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | text | for example ALABAMA POWER CO, ALABAMA POWER COMPANY, ALASKA POWER & TELEPHONE CO; 430 distinct | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | text | for example ornl_eha:hc0124_p02, ornl_eha:hc0125_p01, ornl_eha:hc0126_p01; 546 distinct | 11 |
| `mw` | The capacity involved, in megawatts | MW | number | 0.0 to 2755.5; 403 distinct | 0 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 559 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 559 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | Converted to Exemption, Issued Exemption Termination, Issued License Termination, Issued Relicense, Issued Surrender, Pending Relicense, Pending Surrender, Submitted NOI to Relicense, Submitted NOI to Surrender | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ornl:hydro_relicensing | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/us-hydropower-relicensing-and-license-surrender-data-2026/ORNL_US_Hydropower_Relicensing_and_License_Surrender_2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T10:14:02Z | 0 |
| `x_record` | not yet written |  | text | relicense, surrender | 0 |
| `x_date_kind` | not yet written |  | text | application, ferc_issued, notice_of_intent | 0 |
| `x_ferc_docket` | not yet written |  | text | for example P-1005, P-10198, P-10200; 558 distinct | 0 |
| `x_eha_plant_id` | not yet written |  | text | for example hc0124_p02, hc0125_p01, hc0126_p01; 546 distinct | 11 |
| `x_project_name` | not yet written |  | text | for example 5 in 1 Dame hydropower facility, ALICE FALLS, AMES; 558 distinct | 0 |
| `x_licensee_type` | not yet written |  | text | Cooperative, Industrial, Investor-Owned Utility, Municipality, Political subdivision, Private Non-utility, Private non-utility, Publicly Owned Utility, State, Wholesale Power Marketer, private non-utility | 0 |
| `x_waterway` | not yet written |  | text | for example Allegheny River, Androscoggin River, Angels Creek; 340 distinct | 52 |
| `x_project_type` | not yet written |  | text | HY, HY/PS, PS | 0 |
| `x_lat` | not yet written |  | number | 29.13 to 61.09; 539 distinct | 0 |
| `x_lon` | not yet written |  | number | -153.046 to -67.734; 544 distinct | 0 |
| `x_state` | not yet written |  | text | for example AK, AL, AZ; 41 distinct | 0 |
| `x_noi_date` | not yet written |  | date | 1989-03-07 to 2025-12-17; 363 distinct | 121 |
| `x_application_date` | not yet written |  | date | 1991-12-10 to 2025-12-23; 364 distinct | 81 |
| `x_process` | not yet written |  | text | ALP, ILP, TLP | 161 |
| `x_ferc_issued` | not yet written |  | date | 2007-01-19 to 2025-12-18; 274 distinct | 246 |
| `x_ferc_expires` | not yet written |  | date | 2037-08-29 to 2074-08-31; 132 distinct | 361 |
| `x_mode_new` | not yet written |  | text | Run-of-river, canal/conduit, flow-based_regime_target discharges, intermediate peaking, peaking, peaking/reregulating, peaking/run-of-river, reregulating, run-of-release, run-of-river, run-of-river/peaking | 418 |
| `x_settlement` | not yet written |  | integer | 0, 1 | 152 |
| `x_construction` | not yet written |  | integer | 0, 1 | 152 |
| `x_turbine_generator_investment` | not yet written |  | integer | 0, 1 | 152 |
| `x_capacity_new_mw` | not yet written |  | number | 0.0 to 2755.5; 335 distinct | 152 |
| `x_capacity_old_mw` | not yet written |  | number | 0.0 to 168.973; 103 distinct | 407 |
| `x_dam_removal` | not yet written |  | text | No, Yes | 407 |
| `x_reason` | not yet written |  | text | for example Abandoned, Aboonded project and no replies, Aquatic ecosystem restoration project; 90 distinct | 408 |

### `ornl_npd_potential`

What a row is: not yet written.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 597.

- **Source:** ornl:npd_potential Oak Ridge National Laboratory, HydroSource, U.S. Hydropower Potential from Existing Non-powered Dams (greater than 1MW), NHAAP_NPD_FY11_1MW (B. Hadjerioua, Y. Wei and S.-C. Kao, 2012, DOE/EE-0711) (https://hydrosource.ornl.gov/data/datasets/us-hydropower-potential-existing-non-powered-dams-greater-1mw/)
- **Method note:** [`docs/methods/ornl_hydropower.md`](../methods/ornl_hydropower.md)
- **Cite as:** Oak Ridge National Laboratory (ORNL), HydroSource. U.S. Hydropower Potential from Existing Non-powered Dams (greater than 1MW). Via the Energy Research Warehouse (ERW), table `ornl_npd_potential`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id | none | text | for example ornl_npd:AL00017, ornl_npd:AL00977, ornl_npd:AL01137; 597 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example A.I.SELDEN, ABERDEEN LK/DM (TENN-TOM, AL & MS), ADAM T. BOWER MEMORIAL; 597 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AL, US-AR, US-AZ; 44 distinct | 36 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 26.78863 to 48.950757; 597 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -123.8 to -71.453535; 597 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | number | 1.022157 to 496.049783; 597 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | empty | no cell holds a value | 597 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 597 |
| `operator` | The operator or owner, as the publisher writes it | none | text | for example AMERGEN ENERGY CO., ANGELINA NACOGDOCHES COUNTIES WCID 1, ATLANTIC RICHFIELD CO; 238 distinct | 22 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ornl:npd_potential | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/us-hydropower-potential-existing-non-powered-dams-greater-1mw/NHAAP_NPD_FY11_1MW.XLS | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T11:05:59Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2024-08-29T14:41:15Z | 0 |
| `nid_id` | not yet written |  | text | for example AL00017, AL00977, AL01137; 597 distinct | 0 |
| `state` | not yet written |  | text | for example AL, AL/GA, AR; 56 distinct | 0 |
| `county` | not yet written |  | text | for example ADAMS, ALFALFA, ALLEGHANY; 376 distinct | 4 |
| `city` | not yet written |  | text | for example ., ABERDEEN,MS, ADEL; 462 distinct | 45 |
| `river` | not yet written |  | text | for example ALABAMA RIVER, ALLEGHENY RIVER, ALUM CREEK OF BIG WALNUT CRK.; 402 distinct | 5 |
| `year_built` | not yet written |  | integer | 0 to 2006; 120 distinct | 0 |
| `storage_acre_ft` | not yet written |  | integer | 0 to 11100000; 503 distinct | 0 |
| `federal_regulator` | not yet written |  | text | CE, CE; FERC, CE; USDA FS, DOD USAF, DOI BIA, DOI BR, FERC, IBWC, TVA, USDA FS,DOI BR, USDA FS; DOI BR | 321 |
| `head_ft` | not yet written |  | integer | 4 to 320; 142 distinct | 0 |
| `head_source` | not yet written |  | text | Head estimated by upstream/downstream pool elevation, Head estimated from NID, Head from Reclamation Resource Assessment, Lock/Dam lift from USACE | 0 |
| `huc02` | not yet written |  | integer | 1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 2, 3, 4, 5, 6, 7, 8, 9 | 0 |
| `flow_cfs` | not yet written |  | number | 38.445518 to 276989.9288; 595 distinct | 0 |
| `potential_mwh_year` | not yet written |  | number | 2200.334619 to 2084906.651; 597 distinct | 0 |
| `capacity_factor_pct` | not yet written |  | number | 24.573493, 26.661058, 28.26325, 31.091212, 31.247569, 34.013302, 35.843137, 38.316111, 42.601335, 42.753157, 43.076382, 44.163864, 46.912745, 47.572699, 47.979668, 52.226725, 55.990009, 66.299637 | 0 |
| `coordinates_from` | not yet written |  | text | NHD, NID | 0 |

