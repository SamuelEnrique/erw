# Codebook: ornl

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 5 public tables (4 entities, 1 events; tiers: 5 source); 5 documented in full.

- [`ornl_eha_hydropower_plants`](#ornl_eha_hydropower_plants): One U.S. hydropower or pumped storage plant in operation, from ORNL's Existing Hydropower Assets (EHA) Plant Database, 2026.
- [`ornl_eha_hydropower_units`](#ornl_eha_hydropower_units): One U.S. hydropower or pumped storage generating unit, from ORNL's Existing Hydropower Assets (EHA) Unit Database, 2026.
- [`ornl_hydropower_pipeline`](#ornl_hydropower_pipeline): One proposed U.S. hydropower or pumped storage project in permitting, licensing or exemption, or under construction, on 31 December 2025, from ORNL's U.S. Hydropower Development Pipeline, 2026.
- [`ornl_hydropower_relicensing`](#ornl_hydropower_relicensing): One hydropower project in FERC relicensing or license surrender on 31 December 2025, from ORNL's U.S. Hydropower Relicensing and License Surrender data, 2026 (sheets Relicenses and Surrenders).
- [`ornl_npd_potential`](#ornl_npd_potential): One existing U.S. dam without power whose estimated hydropower potential is above 1 MW, from ORNL's 2012 national assessment of non-powered dams.

### `ornl_eha_hydropower_plants`

One U.S. hydropower or pumped storage plant in operation, from ORNL's Existing Hydropower Assets (EHA) Plant Database, 2026.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 2257.

- **Time:** No time column; the table is a snapshot of the 2026 edition; vintage is the workbook's last-modified time (UTC).
- **Revisions:** A snapshot of one yearly edition, replaced whole by each run; a new edition has a new address.
- **Source:** ornl:eha_plant M.M. Johnson, S.-C. Kao and R. Uria-Martinez, Existing Hydropower Assets (EHA) Plant Database, 2026, HydroSource, Oak Ridge National Laboratory, Oak Ridge, Tennessee, DOI 10.21951/EHA_FY2026/3374497 (https://hydrosource.ornl.gov/data/datasets/eha-plant-2026/)
- **Method note:** [`docs/methods/ornl_hydropower.md`](../methods/ornl_hydropower.md)
- **Cite as:** Oak Ridge National Laboratory (ORNL), HydroSource. Existing Hydropower Assets (EHA) Plant Database. Via the Energy Research Warehouse (ERW), table `ornl_eha_hydropower_plants`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: ornl_eha:<EHA_PtID> | none | text | for example ornl_eha:hc0001_p01, ornl_eha:hc0002_p01, ornl_eha:hc0003_p01; 2257 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always plant | none | text | plant | 0 |
| `name` | The thing's name, as the publisher writes it. Here: ORNL's plant name (PtName) | none | text | for example 29 Mile Creek Diversion, 45-Mile Hydroelectric Project, 92nd Avenue Pressure Relief Valve Facility Project; 2192 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> | none | text | for example US-AK, US-AL, US-AR; 49 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: NAD83 as ORNL gives it | degree | number | 18.017 to 61.6; 2183 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: NAD83 as ORNL gives it | degree | number | -174.197 to -65.794; 2192 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: hy_mw plus psh_mw: the plant's conventional hydro and pumped storage capacity | MW | number | 5e-05 to 6809.0; 783 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: the database lists plants in operation | none | empty | no cell holds a value | 2257 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 2257 |
| `operator` | The operator or owner, as the publisher writes it. Here: Not filled: the database names owners (plant_owner, dam_owner), not operators | none | empty | no cell holds a value | 2257 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ornl:eha_plant | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/EHA2026/ORNL_EHAHydroPlant_PublicFY2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T08:09:05Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time, UTC | none | utc time | 2026-07-17T16:30:08Z | 0 |
| `eha_plant_id` | ORNL's EHA identifier of the plant, which links it to EHA's other datasets (the source's name: EHA_PtID) | none | text | for example hc0001_p01, hc0002_p01, hc0003_p01; 2257 distinct | 0 |
| `eia_plant_id` | EIA's plant identification code (the source's name: EIA_PtID) | none | integer | 2 to 69673; 1624 distinct | 608: ORNL gives no EIA plant id (608 plants, mostly small) |
| `state` | The plant's state, two-letter postal code (the source's name: State) | none | text | for example AK, AL, AR; 49 distinct | 0 |
| `county` | The plant's U.S. county as ORNL writes it (the source's name: County) | none | text | for example Abbeville, Ada, Ada, Owyhee; 610 distinct | 23: ORNL gives no county |
| `county_fips` | The county's FIPS (Federal Information Processing Standards) code (the source's name: FIPS_Census) | none | integer | 1001 to 56039; 639 distinct | 173: ORNL gives no code |
| `plant_owner` | The owner of the plant facility (the source's name: Pt_Own) | none | text | for example 2C Land & Cattle Company, LLC, 5440 Hydro, Inc., 8 CHURCH LANE, LLC.; 1053 distinct | 0 |
| `owner_type` | The type of the plant's owner (Investor-Owned Utility, Publicly Owned Utility, Private Non-utility, USACE and the others) (the source's name: OwType) | none | text | Cooperative, Industrial, Investor-Owned Utility, Municipal, Political subdivision, Private Non-utility, Private non-utility, Publicly Owned Utility, Reclamation, State, TVA, USACE, Unknown, Wholesale Power Marketer | 0 |
| `dam_owner` | The owner of the dam where the plant is located (the source's name: Dam_Own) | none | text | for example 5440 Hydro, Inc., 8 CHURCH LANE, LLC., A & D Hydro, Inc.; 946 distinct | 163: ORNL names no dam owner |
| `plant_type` | The type of facility: HY conventional hydro, PSH pumped storage, HY/PSH both (the source's name: Type) | none | text | HY, HY/PSH, PSH | 0 |
| `ferc_docket` | The plant's FERC (Federal Energy Regulatory Commission) license docket number (the source's name: FC_Dock) | none | text | for example CD13-1, CD13-4, CD13-7; 1556 distinct | 369: ORNL gives no FERC docket (federal plants need no FERC authorization) |
| `ferc_issued` | The date FERC issued the plant's most recent authorization (the source's name: FcIssue) | none | date | 1952-07-21 to 2025-11-26; 1151 distinct | 391: ORNL gives no issue date |
| `ferc_expires` | The date the plant's most recent FERC authorization expires (the source's name: FcExpire) | none | date | 2003-04-26 to 2074-08-31; 411 distinct | 1034: No expiry: exemptions and qualifying conduits do not expire, and federal plants need no FERC authorization |
| `mode` | The plant's mode of operation (Run-of-river, Peaking, Canal/Conduit and the others) (the source's name: Mode) | none | text | Canal/Conduit, Intermediate Peaking, Peaking, Reregulating, Run-of-river, Run-of-river/Peaking, Run-of-river/Upstream Peaking, Unknown | 764: ORNL gives no mode |
| `permitting` | The permitting agency or authorization (FERC License, FERC Exemption, Reclamation, USACE, TVA and the others) (the source's name: Pm_Type) | none | text | FERC Exemption, FERC License, FERC Qualifying Conduit, LOPP, Non-FERC regulated, Not Required, Reclamation, Reclamation LOPP, Reclamation Others, Reclamation Transferred, TVA, USACE, Unknown | 2: ORNL gives none (2 plants) |
| `units` | The total number of generators in the plant (the source's name: Number_of_Units) | count | integer | 1, 10, 11, 12, 13, 14, 15, 16, 19, 2, 20, 21, 24, 27, 3, 33, 4, 5, 6, 7, 73, 8, 9 | 2: ORNL gives no number (2 plants) |
| `hy_mw` | The plant's conventional hydro capacity (its pumped storage units excluded) (the source's name: HY_MW) | MW | number | 5e-05 to 6495.0; 761 distinct | 26: A pumped storage plant with no conventional units |
| `hy_avg_mwh` | The plant's average annual net hydro generation since 2002, or the estimate stated in its FERC authorization (the source's name: HY_MWh) | MWh | number | 0.012 to 19194991.32; 1808 distinct | 337: ORNL gives none |
| `hy_capacity_factor_pct` | The hydro capacity factor: net hydro generation over hydro capacity times the hours of a year, percent (the source's name: HY_Pf) | pct | number | 0.0273972602739726 to 6019.85901826484; 1858 distinct | 336: ORNL gives none (it blanks factors outside 0 to 120 percent) |
| `hy_first_year` | The year the plant's first conventional hydro generator came online (the source's name: HY_OpYear) | none | integer | 1891 to 2024; 131 distinct | 117: ORNL gives no year |
| `psh_mw` | The plant's pumped storage capacity (the source's name: PSH_MW) | MW | number | 0.14 to 2862.0; 40 distinct | 2216: Not a pumped storage plant |
| `psh_avg_mwh` | The plant's average annual gross pumped storage generation since 2002, or the estimate stated in its FERC authorization (the source's name: PSH_MWh) | MWh | number | 13908.04 to 3809539.67; 39 distinct | 2218: Not a pumped storage plant, or ORNL gives none |
| `psh_capacity_factor_pct` | The pumped storage capacity factor: gross pumped storage generation over its capacity times the hours of a year, percent (the source's name: PSH_Pf) | pct | number | 3.08618663039871 to 34.2278807413376; 39 distinct | 2218: Not a pumped storage plant, or ORNL gives none |
| `psh_first_year` | The year the plant's first pumped storage generator came online (the source's name: PSH_OpYear) | none | integer | 1927, 1928, 1954, 1956, 1961, 1963, 1965, 1967, 1968, 1970, 1971, 1972, 1973, 1974, 1977, 1978, 1979, 1981, 1984, 1985, 1987, 1991, 1993, 1995, 2002 | 2218: Not a pumped storage plant, or ORNL gives no year |
| `waterway` | The waterway where the plant is located, as ORNL writes it (the source's name: Water) | none | text | for example -99 (canal), ALDER BROOK, ANCHORAGE WATER & WASTEWATER PL; 1149 distinct | 35: ORNL gives none |
| `huc` | The 12-digit hydrologic unit code (HUC12, the watershed) of the plant, held as a number as ORNL gives it (the plant file's field description says 10-digit, the unit file's says 12-digit) (the source's name: HUC12_All) | none | number | 10100040901.0 to 210100050202.0; 1621 distinct | 3: ORNL gives none (3 plants) |
| `nerc_region` | The plant's North American Electric Reliability Corporation region (WECC, NPCC, SERC and the others) (the source's name: NERC) | none | text | MRO, NPCC, RFC, SERC, SPP, TRE, WECC | 85: ORNL gives none |
| `balancing_authority` | The code of the plant's balancing authority (the grid operator of its area) (the source's name: BACode) | none | text | for example AECI, AVA, BANC; 44 distinct | 811: ORNL gives none |
| `eia_sector` | EIA's sector name of the plant (Electric Utility, IPP Non-CHP and the others) (the source's name: Sector) | none | text | Commercial CHP, Commercial Non-CHP, Electric Utility, IPP, IPP CHP, IPP Non-CHP, Industrial, Industrial CHP, Industrial Non-CHP | 758: ORNL gives none |
| `transmission_owner` | The owner of the transmission or distribution system the plant connects to (the source's name: Trans) | none | text | for example AEP Texas Central Company, ALLETE, Inc., Alabama Power Co; 232 distinct | 769: ORNL gives none |

Waiting for a second look: hy_capacity_factor_pct: ORNL's field description says factors outside 0 to 120 percent are shown as null, yet 5 plants hold values above 120 (the highest 6,019.9). Read again on 20 November 2026 in the saved plant workbook's Field Descriptions sheet (HY_Pf: the 0 to 120 percent rule, nothing on larger values): not found..

### `ornl_eha_hydropower_units`

One U.S. hydropower or pumped storage generating unit, from ORNL's Existing Hydropower Assets (EHA) Unit Database, 2026.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 5362.

- **Time:** No time column; the table is a snapshot of the 2026 edition; vintage is the workbook's last-modified time (UTC).
- **Revisions:** A snapshot of one yearly edition, replaced whole by each run.
- **Source:** ornl:eha_unit M.M. Johnson, S.-C. Kao and R. Uria-Martinez, Existing Hydropower Assets (EHA) Unit Database, 2026, HydroSource, Oak Ridge National Laboratory, Oak Ridge, Tennessee, DOI 10.21951/FY2026/3374522 (https://hydrosource.ornl.gov/data/datasets/eha-unit-2026/)
- **Method note:** [`docs/methods/ornl_hydropower.md`](../methods/ornl_hydropower.md)
- **Cite as:** Oak Ridge National Laboratory (ORNL), HydroSource. Existing Hydropower Assets (EHA) Unit Database. Via the Energy Research Warehouse (ERW), table `ornl_eha_hydropower_units`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: ornl_eha_unit:<EHA_PtGnID> | none | text | for example ornl_eha_unit:hc0001_p01_1, ornl_eha_unit:hc0001_p01_2, ornl_eha_unit:hc0002_p01_1; more than 5000 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always generator | none | text | generator | 0 |
| `name` | The thing's name, as the publisher writes it. Here: '<plant name>, unit <EHA unit id>' | none | text | for example 29 Mile Creek Diversion, unit 1, 45 Mile Hydroelectric Project, unit 1, 45 Mile Hydroelectric Project, unit 2; more than 5000 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: the sheet gives no state; the plant's state is in ornl_eha_hydropower_plants, joined by eha_plant_id | none | empty | no cell holds a value | 5362 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: The plant's | degree | number | 18.017 to 61.6; 2184 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: The plant's | degree | number | -174.197 to -65.794; 2193 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: The unit's capacity | MW | number | 0.0 to 805.0; 680 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 5362 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 5362 |
| `operator` | The operator or owner, as the publisher writes it. Here: Not filled: the plant's owner is in plant_owner | none | empty | no cell holds a value | 5362 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ornl:eha_unit | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/eha-unit-2026/ORNL_EHAHydroUnit_PublicFY2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T11:18:37Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time, UTC | none | utc time | 2026-06-24T16:53:31Z | 0 |
| `eha_plant_id` | ORNL's EHA identifier of the unit's plant, the key to ornl_eha_hydropower_plants (the source's name: EHA_PtID) | none | text | for example hc0001_p01, hc0002_p01, hc0003_p01; 2258 distinct | 0 |
| `plant_owner` | The owner of the plant facility (where the plant is not in EIA's data, the original licensed or exempted owner, which may be out of date) (the source's name: Pt_Own) | none | text | for example 2C Land & Cattle Company, LLC, 5440 Hydro, Inc., 8 CHURCH LANE, LLC.; 1049 distinct | 6: ORNL names no owner |
| `unit_type` | The type of unit: HY conventional hydro or PS pumped storage (the source's name: Type) | none | text | HY, PS | 0 |
| `eia_plant_id` | EIA's plant identification code (the source's name: EIA_PtID) | none | integer | 2 to 69673; 1622 distinct | 937: ORNL gives no EIA plant id |
| `eia_generator_id` | EIA's identification code of the unit (generator) (the source's name: EIA_GnID) | none | text | for example 1, 10, 10A; 673 distinct | 951: ORNL gives no EIA generator id |
| `eha_unit_id` | ORNL's EHA identification code of the unit within its plant (the source's name: EHA_GnID) | none | text | for example 1, 10, 11; 74 distinct | 0 |
| `ferc_plant_id` | FERC's plant identification code, as ORNL writes it (the source's name: FC_PtID) | none | text | for example 01 - 29 Mile Creek, 01 - A J Allen, 01 - A-Plant Powerhouse; 1738 distinct | 1510: ORNL gives no FERC plant id |
| `first_year` | The year the unit came online (the source's name: OpYear) | none | integer | 1891 to 2025; 132 distinct | 143: ORNL gives no year |
| `refurbished_year` | The year the unit was refurbished or rehabilitated, or Unknown as ORNL writes it (most units) (the source's name: RhYear) | none | text | for example 1950, 1956, 1971; 49 distinct | 16: ORNL's cell is blank (16 units) |
| `turbine_type` | The original turbine type (Francis, Kaplan, Pelton, Pump, Unknown and others) (the source's name: TbType) | none | text | 10TR2, 5TR2, Archimedes Screw, Centrifugal, Francis, Horizontal Impulse, Horizontal Pump, Kaplan, Pelton, Pump, Unknown, Vertical | 1: ORNL's cell is blank (1 unit) |
| `turbine_maker` | The manufacturer of the turbine (the source's name: Maker) | none | text | for example A & D, ABNER DOBLE COMPANY ENGINEERS, ALSTH; 165 distinct | 1823: ORNL names no maker |
| `speed_rpm` | The turbine's speed, revolutions per minute (the source's name: Speed_rpm) | rpm | number | 54.5 to 1730.0; 50 distinct | 4903: ORNL gives none |
| `head_ft` | The turbine's rated head (the height the water falls), in feet (the source's name: Head_ft) | ft | number | 1.08 to 2558.0; 628 distinct | 1530: ORNL gives none |
| `power_hp` | The turbine's power, in horsepower (the source's name: Power_hp) | hp | number | 0.24 to 960000.0; 1104 distinct | 1695: ORNL gives none |
| `min_load_mw` | The unit's minimum load (the source's name: MinMW) | MW | number | 0.0 to 320.0; 195 distinct | 1241: ORNL gives none |
| `start_time` | The time from cold shutdown to full load as given: M minutes, H hours (10M, 1H, 12H) (the source's name: StTime) | none | text | 1, 10M, 12H, 1H, OVER | 1246: ORNL gives none |
| `huc` | The 12-digit hydrologic unit code (the watershed), as given (the source's name: HUC12_All) | none | number | 10100040901.0 to 210100050202.0; 1621 distinct | 3: ORNL gives none (3 units) |
| `county_fips` | The county's FIPS (Federal Information Processing Standards) code (the source's name: FIPS_Census) | none | integer | 1001 to 56039; 639 distinct | 369: ORNL gives no code |

Waiting for a second look: start_time: ORNL defines M (minutes) and H (hours); the values '1' (2 units) and 'OVER' (4 units) are not explained. Read again on 20 November 2026 in the saved unit workbook under warehouse/raw/ornl_eha_units (sheets Field Descriptions, StTime: M or H only, and Acronyms and Nomenclature): not found..

### `ornl_hydropower_pipeline`

One proposed U.S. hydropower or pumped storage project in permitting, licensing or exemption, or under construction, on 31 December 2025, from ORNL's U.S. Hydropower Development Pipeline, 2026.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 196.

- **Time:** No time column; status_date is the snapshot's day, 2025-12-31; vintage is the workbook's last-modified time (UTC).
- **Revisions:** A snapshot of one yearly edition, replaced whole by each run.
- **Source:** ornl:hydro_pipeline M.M. Johnson and R. Uria-Martinez, U.S. Hydropower Development Pipeline Data, 2026, HydroSource, Oak Ridge National Laboratory, Oak Ridge, Tennessee, DOI 10.21951/HMR_PipelineFY26/3025030 (https://hydrosource.ornl.gov/data/datasets/us-hydropower-development-pipeline-data-2026/)
- **Method note:** [`docs/methods/ornl_hydropower.md`](../methods/ornl_hydropower.md)
- **Cite as:** Oak Ridge National Laboratory (ORNL), HydroSource. U.S. Hydropower Development Pipeline Data. Via the Energy Research Warehouse (ERW), table `ornl_hydropower_pipeline`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: ornl_hydro_pipeline:<FERC docket>, or ornl_hydro_pipeline:none-<project name slug> where there is no docket | none | text | for example ornl_hydro_pipeline:CD20-8, ornl_hydro_pipeline:CD21-5*, ornl_hydro_pipeline:CD22-1; 196 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always project | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example A. I. Selden Dam, Aberdeen Hydroelectric Project, Allegheny Lock & Dam 2; 196 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> | none | text | for example US-AK, US-AL, US-AR; 33 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 31.18667 to 60.457491; 195 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -153.306198 to -70.37631; 196 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: The project's proposed capacity (Capacity_MW) | MW | number | 0.003 to 5287.0; 123 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: under_construction where ORNL writes Under Construction, else planned (issued or pending permits, licenses and exemptions included) | none | text | planned, under_construction | 0 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown. Here: The snapshot's day, 2025-12-31, not the date the status took effect | none | date | 2025-12-31 | 0 |
| `operator` | The operator or owner, as the publisher writes it. Here: The developer (Project_developer) | none | text | for example 3R Valve, Aberdeen Hydro AE, LLC, Alaska Village Electric Cooperative, Inc.; 161 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ornl:hydro_pipeline | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/us-hydropower-development-pipeline-data-2026/ORNL_US_Hydropower_DevelopmentPipeline_Data_2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T08:33:21Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time, UTC | none | utc time | 2026-04-20T17:05:22Z | 0 |
| `ferc_docket` | The project's FERC docket number (P- a license or exemption, CD- a qualifying conduit), as ORNL writes it (the source's name: FERC_docket) | none | text | for example CD20-8, CD21-5*, CD22-1; 193 distinct | 3: No docket: the project seeks authorization from the Bureau of Reclamation (lease of power privilege) or a preliminary lease |
| `permit_status` | ORNL's status of the project (Issued Preliminary Permit, Issued License, Pending License, Under Construction and the others) (the source's name: Status) | none | text | Issued Exemption, Issued LOPP Authorization, Issued License, Issued Preliminary Lease, Issued Preliminary Permit, Pending Exemption, Pending License, Pending Preliminary Permit, Under Construction | 0 |
| `project_type` | HY conventional hydropower or PSH pumped storage (the source's name: Project_type) | none | text | HY, PSH | 0 |
| `project_subcategory` | Whether the project is a conduit, a new stream-reach development, a non-powered dam or pumped storage (the source's name: Project_subcategory) | none | text | Conduit, New Stream-Reach Development, Non-Powered Dam, Pumped Storage Hydropower | 0 |
| `state` | The project's state, two-letter postal code (the source's name: State) | none | text | for example AK, AL, AR; 33 distinct | 0 |
| `county` | The project's U.S. county as ORNL writes it (the source's name: County) | none | text | for example Adams, Alameda, Alleghany; 148 distinct | 0 |
| `county_fips` | The county's FIPS (Federal Information Processing Standards) code (the source's name: FIPS_Census) | none | integer | 1023 to 56023; 150 distinct | 0 |
| `developer_type` | The type of developer (Private non-utility, Investor-owned utility, Municipal, Political subdivision and the others) (the source's name: Developer_type) | none | text | Cooperative, Investor-owned utility, Municipal, Political subdivision, Private non-utility, State | 0 |
| `dam_name` | The name of the dam where the project would be located (the source's name: Dam_Name) | none | text | for example A.I. Selden Lock and Dam, Aberdeen Lock and Dam, Allegheny Lock & Dam 4; 89 distinct | 106: No dam named (conduits, new stream-reach and most pumped storage projects) |
| `dam_owner` | The owner of that dam as ORNL writes it (Corps of Engineers districts by code, such as CELRP) (the source's name: Dam_Owner) | none | text | Bard College, Beaver Falls Municiple Authority, Bureau of Reclamation, CELRP, CEMVK, CEMVR, CENAB, CENAO, CESAM, Central Hudson Gas & Electric Corp, Commonwealth of Kentucky, Commonwealth of Pennsylvania, Department of Environmental Protection, Kentucky River Authority, RIDEM, Reclamation, Rhode Island Department of Environmental Management, State of New York Canal Corporation, Town of Cumberland, Town of West Warwick, USACE, Village of Swanton | 112: No dam owner named |
| `waterway` | The water source where the project would be located (the source's name: Waterway) | none | text | for example Alabama River, Allegheny River, Antelope Valley Water Storage; 71 distinct | 77: ORNL gives none |
| `psh_configuration` | Whether a pumped storage project would be open-loop or closed-loop (the source's name: PSH_configuration) | none | text | Closed-Loop, Open-Loop | 128: Not a pumped storage project |
| `nerc_region` | The project's North American Electric Reliability Corporation region (the source's name: NERC) | none | text | MRO, NPCC, RFC, SERC, SPP, WECC | 8: ORNL gives none |
| `huc` | The 12-digit hydrologic unit code (the watershed), as given (the source's name: HUC12_All) | none | integer | 10400020505 to 190207011806; 184 distinct | 0 |

### `ornl_hydropower_relicensing`

One hydropower project in FERC relicensing or license surrender on 31 December 2025, from ORNL's U.S. Hydropower Relicensing and License Surrender data, 2026 (sheets Relicenses and Surrenders).

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 559.

- **Time:** event_date is FERC's issuance date where given, else the application's date, else the notice of intent's (x_date_kind says which); a date.
- **Revisions:** A snapshot of one yearly edition, replaced whole by each run.
- **Source:** ornl:hydro_relicensing M.M. Johnson and R. Uria-Martinez, U.S. Hydropower Relicensing and License Surrender Data and Metadata, 2026, HydroSource, Oak Ridge National Laboratory, Oak Ridge, Tennessee, DOI 10.21951/HMR_RelicenseSurrender/3031244 (https://hydrosource.ornl.gov/data/datasets/us-hydropower-relicensing-and-license-surrender-data-2026/)
- **Method note:** [`docs/methods/ornl_hydropower.md`](../methods/ornl_hydropower.md)
- **Cite as:** Oak Ridge National Laboratory (ORNL), HydroSource. U.S. Hydropower Relicensing and License Surrender Data. Via the Energy Research Warehouse (ERW), table `ornl_hydropower_relicensing`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: ornl_relicense:<FERC docket>:<relicense\|surrender>, with -2 for a docket a sheet gives twice | none | text | for example ornl_relicense:P-1005:relicense, ornl_relicense:P-10198:relicense, ornl_relicense:P-10200:surrender; 559 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | date | 2001-08-30 to 2025-12-23; 439 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: hydro_relicense or hydro_license_surrender | none | text | hydro_license_surrender, hydro_relicense | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: The project's current licensee | none | text | for example ALABAMA POWER CO, ALABAMA POWER COMPANY, ALASKA POWER & TELEPHONE CO; 430 distinct | 0 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons. Here: ornl_eha:<EHA_PtID>, the plant in ornl_eha_hydropower_plants, where ORNL gives one | none | text | for example ornl_eha:hc0124_p02, ornl_eha:hc0125_p01, ornl_eha:hc0126_p01; 546 distinct | 11 |
| `mw` | The capacity involved, in megawatts. Here: The new license's capacity (relicense) or the surrendered project's capacity (surrender) | MW | number | 0.0 to 2755.5; 403 distinct | 0 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 559 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 559 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: ORNL's own status on 31 December 2025 (Issued Relicense, Pending Relicense, Issued Surrender and the others) | none | text | Converted to Exemption, Issued Exemption Termination, Issued License Termination, Issued Relicense, Issued Surrender, Pending Relicense, Pending Surrender, Submitted NOI to Relicense, Submitted NOI to Surrender | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ornl:hydro_relicensing | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/us-hydropower-relicensing-and-license-surrender-data-2026/ORNL_US_Hydropower_Relicensing_and_License_Surrender_2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T10:14:02Z | 0 |
| `x_record` | Which of ORNL's sheets the row is from: relicense or surrender | none | text | relicense, surrender | 0 |
| `x_date_kind` | Which date event_date is: ferc_issued, application or notice_of_intent | none | text | application, ferc_issued, notice_of_intent | 0 |
| `x_ferc_docket` | The project's FERC docket number (P- a project seeking a FERC license) (the source's name: FERC_docket) | none | text | for example P-1005, P-10198, P-10200; 558 distinct | 0 |
| `x_eha_plant_id` | ORNL's EHA identifier of the plant, the key to ornl_eha_hydropower_plants (the source's name: EHA_PtID) | none | text | for example hc0124_p02, hc0125_p01, hc0126_p01; 546 distinct | 11: ORNL gives no EHA plant |
| `x_project_name` | The hydropower project's name (the source's name: Project_name) | none | text | for example 5 in 1 Dame hydropower facility, ALICE FALLS, AMES; 558 distinct | 0 |
| `x_licensee_type` | The type of licensee (Private Non-utility, Investor-Owned Utility, Publicly Owned Utility and the others), as ORNL writes it (the source's name: Licensee_type) | none | text | Cooperative, Industrial, Investor-Owned Utility, Municipality, Political subdivision, Private Non-utility, Private non-utility, Publicly Owned Utility, State, Wholesale Power Marketer, private non-utility | 0 |
| `x_waterway` | The water source where the project is located (the source's name: Waterway) | none | text | for example Allegheny River, Androscoggin River, Angels Creek; 340 distinct | 52: ORNL gives none |
| `x_project_type` | HY hydropower, PS pumped storage, or HY/PS both (the source's name: Project_type) | none | text | HY, HY/PS, PS | 0 |
| `x_lat` | The project's latitude, decimal degrees (the source's name: Latitude) | degree | number | 29.13 to 61.09; 539 distinct | 0 |
| `x_lon` | The project's longitude, decimal degrees (west negative) (the source's name: Longitude) | degree | number | -153.046 to -67.734; 544 distinct | 0 |
| `x_state` | The project's state, two-letter postal code (the source's name: State) | none | text | for example AK, AL, AZ; 41 distinct | 0 |
| `x_noi_date` | The date the licensee filed its notice of intent to seek a relicense or to surrender (the source's name: NOI_date) | none | date | 1989-03-07 to 2025-12-17; 363 distinct | 121: ORNL gives no notice date |
| `x_application_date` | The date the licensee filed its relicense or surrender application (the source's name: Application_date) | none | date | 1991-12-10 to 2025-12-23; 364 distinct | 81: No application date given (not yet filed, or not given) |
| `x_process` | The type of licensing process: ALP, TLP or ILP (the source's name: Proc_type) | none | text | ALP, ILP, TLP | 161: ORNL gives none (surrender rows and some relicenses) |
| `x_ferc_issued` | The date FERC issued the relicense or surrender (covers those issued since 2007) (the source's name: FcIssue) | none | date | 2007-01-19 to 2025-12-18; 274 distinct | 246: Not issued, or issued before 2007 |
| `x_ferc_expires` | The date the relicense FERC issued expires (the source's name: FcExpire) | none | date | 2037-08-29 to 2074-08-31; 132 distinct | 361: No relicense issued, or ORNL gives none |
| `x_mode_new` | The operating mode under the newest relicense, as ORNL writes it (the source's name: Mode_new) | none | text | Run-of-river, canal/conduit, flow-based_regime_target discharges, intermediate peaking, peaking, peaking/reregulating, peaking/run-of-river, reregulating, run-of-release, run-of-river, run-of-river/peaking | 418: A surrender row, or ORNL gives none |
| `x_settlement` | 1 if a settlement agreement was submitted to FERC in the relicensing, 0 if not (the source's name: Settlement) | none | integer | 0, 1 | 152: A surrender row |
| `x_construction` | 1 if construction is planned as part of the relicense, 0 if not (the source's name: Construction) | none | integer | 0, 1 | 152: A surrender row |
| `x_turbine_generator_investment` | 1 if investment in turbines or generators is planned as part of the relicense, 0 if not (the source's name: T_G_investment) | none | integer | 0, 1 | 152: A surrender row |
| `x_capacity_new_mw` | The project's total hydro turbine-generator capacity under the new license (equal to mw on relicense rows) (the source's name: Capacity_new_MW) | MW | number | 0.0 to 2755.5; 335 distinct | 152: A surrender row |
| `x_capacity_old_mw` | The surrendered project's total hydro turbine-generator capacity (equal to mw on surrender rows) (the source's name: Capacity_old_MW) | MW | number | 0.0 to 168.973; 103 distinct | 407: A relicense row |
| `x_dam_removal` | Whether a dam was removed as part of the surrender: Yes or No (the source's name: Dam_removal) | none | text | No, Yes | 407: A relicense row |
| `x_reason` | Why the owner decided to surrender the project, as ORNL writes it (the source's name: Reason_category) | none | text | for example Abandoned, Aboonded project and no replies, Aquatic ecosystem restoration project; 90 distinct | 408: A relicense row, or ORNL gives no reason (1 surrender) |

### `ornl_npd_potential`

One existing U.S. dam without power whose estimated hydropower potential is above 1 MW, from ORNL's 2012 national assessment of non-powered dams.

Shape: entities. Keys: `entity_id`. License: public; tier: source. Rows read on 2026-11-20: 597.

- **Time:** No time column; the data were created in April 2012; vintage is the workbook's last-modified time (UTC).
- **Revisions:** A snapshot of the one edition, replaced whole by each run.
- **Source:** ornl:npd_potential Oak Ridge National Laboratory, HydroSource, U.S. Hydropower Potential from Existing Non-powered Dams (greater than 1MW), NHAAP_NPD_FY11_1MW (B. Hadjerioua, Y. Wei and S.-C. Kao, 2012, DOE/EE-0711) (https://hydrosource.ornl.gov/data/datasets/us-hydropower-potential-existing-non-powered-dams-greater-1mw/)
- **Method note:** [`docs/methods/ornl_hydropower.md`](../methods/ornl_hydropower.md)
- **Cite as:** Oak Ridge National Laboratory (ORNL), HydroSource. U.S. Hydropower Potential from Existing Non-powered Dams (greater than 1MW). Via the Energy Research Warehouse (ERW), table `ornl_npd_potential`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: ornl_npd:<National Inventory of Dams id> | none | text | for example ornl_npd:AL00017, ornl_npd:AL00977, ornl_npd:AL01137; 597 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists). Here: Always project: a potential site at a dam, not a plan | none | text | project | 0 |
| `name` | The thing's name, as the publisher writes it. Here: The dam's name | none | text | for example A.I.SELDEN, ABERDEEN LK/DM (TENN-TOM, AL & MS), ADAM T. BOWER MEMORIAL; 597 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>; empty for a dam on a state border, whose pair (IL/KY) is in state | none | text | for example US-AL, US-AR, US-AZ; 44 distinct | 36 |
| `lat` | Latitude, in decimal degrees (WGS84) | degree | number | 26.78863 to 48.950757; 597 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84) | degree | number | -123.8 to -71.453535; 597 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it. Here: ORNL's potential capacity: the potential annual energy over a regional capacity factor, an estimate | MW | number | 1.022157 to 496.049783; 597 distinct | 0 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: a potential, not a plan | none | empty | no cell holds a value | 597 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 597 |
| `operator` | The operator or owner, as the publisher writes it. Here: The dam's owner | none | text | for example AMERGEN ENERGY CO., ANGELINA NACOGDOCHES COUNTIES WCID 1, ATLANTIC RICHFIELD CO; 238 distinct | 22 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | ornl:npd_potential | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/us-hydropower-potential-existing-non-powered-dams-greater-1mw/NHAAP_NPD_FY11_1MW.XLS | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T11:05:59Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's last-modified time, UTC | none | utc time | 2024-08-29T14:41:15Z | 0 |
| `nid_id` | The dam's National Inventory of Dams identifier (the source's name: nid_id1) | none | text | for example AL00017, AL00977, AL01137; 597 distinct | 0 |
| `state` | The dam's state, two-letter postal code, or a pair for a dam on a border (IL/KY) (the source's name: state) | none | text | for example AL, AL/GA, AR; 56 distinct | 0 |
| `county` | The dam's county as ORNL writes it (the source's name: county) | none | text | for example ADAMS, ALFALFA, ALLEGHANY; 376 distinct | 4: ORNL gives no county |
| `city` | The nearest city as ORNL writes it (the source's name: city) | none | text | for example ., ABERDEEN,MS, ADEL; 462 distinct | 45: ORNL gives no city |
| `river` | The river the dam is on (the source's name: water) | none | text | for example ALABAMA RIVER, ALLEGHENY RIVER, ALUM CREEK OF BIG WALNUT CRK.; 402 distinct | 5: ORNL gives no river |
| `year_built` | The year the dam was built (0 for 21 dams, as ORNL writes it) (the source's name: btyear) | none | integer | 0 to 2006; 120 distinct | 0 |
| `storage_acre_ft` | The dam's storage, in acre-feet (the source's name: stor) | acre-ft | integer | 0 to 11100000; 503 distinct | 0 |
| `federal_regulator` | The dam's federal regulator as ORNL writes it (CE the Corps of Engineers, DOI BR the Bureau of Reclamation, FERC, TVA and others) (the source's name: fedreg) | none | text | CE, CE; FERC, CE; USDA FS, DOD USAF, DOI BIA, DOI BR, FERC, IBWC, TVA, USDA FS,DOI BR, USDA FS; DOI BR | 321: ORNL names no federal regulator |
| `head_ft` | The estimated head (the height the water would fall), in feet (the source's name: esth) | ft | integer | 4 to 320; 142 distinct | 0 |
| `head_source` | How the head was estimated (from the National Inventory of Dams, a lock's lift from USACE, pool elevations, Reclamation's assessment) (the source's name: esthfr) | none | text | Head estimated by upstream/downstream pool elevation, Head estimated from NID, Head from Reclamation Resource Assessment, Lock/Dam lift from USACE | 0 |
| `huc02` | The 2-digit hydrologic region of the dam (the source's name: huc02) | none | integer | 1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 2, 3, 4, 5, 6, 7, 8, 9 | 0 |
| `flow_cfs` | The estimated annual mean flow, in cubic feet per second (the source's name: qyr) | cfs | number | 38.445518 to 276989.9288; 595 distinct | 0 |
| `potential_mwh_year` | The estimated potential annual energy (the source's name: mwhyr) | MWh | number | 2200.334619 to 2084906.651; 597 distinct | 0 |
| `capacity_factor_pct` | The regional capacity factor ORNL applies to turn the potential energy into capacity, percent (the source's name: cf) | pct | number | 24.573493, 26.661058, 28.26325, 31.091212, 31.247569, 34.013302, 35.843137, 38.316111, 42.601335, 42.753157, 43.076382, 44.163864, 46.912745, 47.572699, 47.979668, 52.226725, 55.990009, 66.299637 | 0 |
| `coordinates_from` | The source of the dam's coordinates: NHD or NID (the National Inventory of Dams) (the source's name: cordfrom) | none | text | NHD, NID | 0 |

