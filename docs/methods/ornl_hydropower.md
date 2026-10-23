# The hydropower fleet and its pipeline (Oak Ridge National Laboratory, HydroSource)

Energy Research Warehouse (ERW), method note written in session 918 (chain 051) for tables first written on 23 October 2026.

Tables: `ornl_eha_hydropower_plants`, `ornl_hydropower_pipeline`, `ornl_hydropower_relicensing`, `ornl_npd_potential`, `ornl_eha_hydropower_units`

## Publisher and address

Oak Ridge National Laboratory (ORNL), HydroSource, for the U.S. Department of Energy's Water Power Technologies Office. Two datasets, each workbook linked from its landing page and kept on ORNL's S3 bucket:

- Existing Hydropower Assets (EHA) Plant Database, 2026 (M.M. Johnson, S.-C. Kao and R. Uria-Martinez; published July 2026; DOI 10.21951/EHA_FY2026/3374497): `https://hydrosource.ornl.gov/data/datasets/eha-plant-2026/`, workbook `ORNL_EHAHydroPlant_PublicFY2026.xlsx`. Connector: `warehouse/connectors/ornl_eha.py` (session 911).
- U.S. Hydropower Development Pipeline Data, 2026 (M.M. Johnson and R. Uria-Martinez; published April 2026; DOI 10.21951/HMR_PipelineFY26/3025030): `https://hydrosource.ornl.gov/data/datasets/us-hydropower-development-pipeline-data-2026/`, workbook `ORNL_US_Hydropower_DevelopmentPipeline_Data_2026.xlsx`. Connector: `warehouse/connectors/ornl_hydro_pipeline.py` (session 916).

HydroSource's robots file allows the landing pages and asks a crawl delay of 10 seconds; sessions 911 and 916 waited 11 between requests. The S3 host has no robots file (HTTP 403). The landing pages show a download form (a name, an e-mail address and a company, required); the workbooks were taken by their public links without it (a question for the owner, session 916).

## Vintage and revision

Both are ORNL's yearly editions. EHA's workbook was retrieved 2026-10-23T08:09:05Z (last modified 17 July 2026, after a revision of 16 July that added EIA-923's revised generation); the pipeline's 2026-10-23T08:33:21Z (last modified 20 April 2026), a snapshot of 31 December 2025. Each table is a snapshot, replaced whole by a run (ceiling: one request each, the workbook, reused offline). A new edition has a new address and needs the connector's `URL` changed.

## Shape and variables

Both are entities tables. Their columns other than the standard ones are ORNL's own fields, renamed with their units, as each workbook's "Field Descriptions" sheet defines them.

`ornl_eha_hydropower_plants` (2,257 plants: 2,216 conventional hydro, 26 pumped storage, 15 both; 102,778 MW; 48 states and Puerto Rico): `entity_id` `ornl_eha:<EHA_PtID>`; `entity_type` `plant`; `capacity_mw` the hydro and pumped storage capacity summed (each also in `hy_mw`, `psh_mw`); `hy_avg_mwh` the average annual net hydro generation since 2002, or the FERC authorization's estimate, and `psh_avg_mwh` the same for gross pumped storage generation; `*_capacity_factor_pct`; `*_first_year` the year the first unit came online (1891 to 2024); `ferc_docket`, `ferc_issued`, `ferc_expires` (exemptions and conduits do not expire); `permitting`; `mode`; `plant_owner`, `owner_type`, `dam_owner`; `waterway`, `huc`, `county_fips`, `nerc_region`, `balancing_authority`, `eia_sector`, `transmission_owner`. `status` and `operator` are empty: the database lists plants in operation and names owners, not operators. The largest: Grand Coulee (6,809 MW), Bath County (2,862), Chief Joseph (2,456), Robert Moses Niagara (2,429).

`ornl_hydropower_pipeline` (196 projects: 128 hydro, 1,391 MW; 68 pumped storage, 59,350 MW; 33 states): `entity_id` `ornl_hydro_pipeline:<FERC docket>`, or `none-<name>` for the three without one (two Reclamation lease of power privilege authorizations and a preliminary lease); `entity_type` `project`; `status` `under_construction` (7) or `planned`, ORNL's own in `permit_status` (99 issued preliminary permits, 38 issued licenses, 23 issued exemptions, 26 pending, 7 under construction, 3 Reclamation); `status_date` 2025-12-31; `operator` the developer; `project_type` HY or PSH; `project_subcategory`; `psh_configuration` (58 closed-loop, 10 open-loop). The largest: Camp Pendleton (5,287 MW), Maxwell (3,600), Red Lake (3,000), all pumped storage on preliminary permits.

## Reading the workbooks

- Sheet "Data", every cell read as text; a heading not in the connector's map, or one missing, stops the run.
- Numbers are written as numbers (whole ones as integers); a cell that is not a number where one is expected stops the run. Dates (EHA's FERC dates) are written as YYYY-MM-DD.
- An id given twice stops the run. EHA keeps the 39 plants that share an EIA plant id with another, as ORNL gives them, and counts them in the header.
- A blank stays blank; nothing is filled.
- The pipeline's field description dates its status "as of December 31, 2023"; its summary and the landing page date the snapshot 31 December 2025, which the table takes and the header names.

## License

HydroSource's Data Use Policy (read 116 of `license_reads.csv`): "Data hosted on HydroSource is openly shared, without restriction, in accordance with Department of Energy's Public Access Plan." Its citation policy asks for the authors, title, publisher and DOI, which each header carries. Verdict "may be public" (session 914).

## Cross-checks (sessions 911, 916 and 918)

- EHA against EIA-860M's operating generators by EIA plant id (the tables read past their header lines, not with `comment="#"`, session 917): of the 1,465 plants with hydro or pumped storage generators, 1,456 are in EHA; hydro capacity equal within 1 MW at 1,429 of 1,432 ids (80,129 and 80,134 MW), pumped storage at 39 of 39 (22,224 MW). The 608 EHA plants without an EIA id are small (median 0.3 MW, 290 MW in all; 389 under FERC exemptions).
- The pipeline against the fleet: no pipeline docket is an EHA plant. Against EIA-860M's planned generators: 30 of the 37 planned plants with hydro or pumped storage are in the pipeline by name and state (read by hand); the pipeline's pumped storage is 59,350 MW against EIA-860M's 2,600, since EIA-860M lists only projects with a planned date.
- Session 918, against the code: `capacity_mw` is `hy_mw` plus `psh_mw` where either is given, empty where neither is; `status` is `under_construction` only where ORNL writes "Under Construction".

## What they do not hold

- EHA's generation and capacity factor time series, and capacity additions at existing plants (ORNL leaves them out of the pipeline: they rest on a proprietary source). ORNL's unit database is `ornl_eha_hydropower_units` (session 943, below).

## The relicensing and surrender records (session 930; added by session 932)

`ornl_hydropower_relicensing`: ORNL's U.S. Hydropower Relicensing and License Surrender Data, 2026 (M.M. Johnson and R. Uria-Martinez; published May 2026; DOI 10.21951/HMR_RelicenseSurrender/3031244), sheets "Relicenses" and "Surrenders" of the workbook its landing page links (`https://hydrosource.ornl.gov/data/datasets/us-hydropower-relicensing-and-license-surrender-data-2026/`). Connector: `warehouse/connectors/ornl_hydro_relicensing.py`. A snapshot of 31 December 2025, retrieved 2026-10-23T10:14:02Z (last modified 6 May 2026); ceiling one request.

Events, 559 records. `event_id` `ornl_relicense:<FERC docket>:<relicense|surrender>` (one surrender docket the sheet gives twice keeps `-2`); `event_date` FERC's issuance where given (313), else the application's (194), else the notice of intent's (52), with `x_date_kind`; `event_type` `hydro_relicense` (407) or `hydro_license_surrender` (152); `parties` the licensee; `entity_ids` `ornl_eha:<EHA_PtID>` where ORNL gives the plant (548); `mw` the new license's capacity (relicense) or the surrendered project's (surrender); `status` ORNL's own (Issued Relicense 198, Pending Relicense 160, Submitted NOI to Relicense 40, Converted to Exemption 9; Issued Surrender 82, Pending Surrender 31, Submitted NOI to Surrender 9, Issued License Termination 15, Issued Exemption Termination 15). `x_*` the other fields: the old capacity, the dates, the process (TLP 219, ILP 157, ALP 22), the new mode, the settlement (57), construction and turbine-generator flags, the dam's removal (28 surrenders) and the reason. A heading not in the map or a record without a date stops the run.

Cross-checks against `ornl_eha_hydropower_plants` (session 930): of the 405 relicensing records that name a plant, 401 are in the fleet table and 396 carry its docket; 193 of 197 issued relicenses give the fleet table's FERC expiry; the new capacity equals the fleet table's within 1 MW for 130 of 197; 46 of the 143 surrenders that name a plant are still in the fleet table.

## The potential at non-powered dams (session 938; added by session 946)

`ornl_npd_potential`: ORNL's U.S. Hydropower Potential from Existing Non-powered Dams (greater than 1MW), the dataset of the 2012 national assessment (B. Hadjerioua, Y. Wei and S.-C. Kao, An Assessment of Energy Potential at Non-Powered Dams in the United States, DOE/EE-0711), sheet "NPD" of the workbook `NHAAP_NPD_FY11_1MW.XLS` its landing page links (`https://hydrosource.ornl.gov/data/datasets/us-hydropower-potential-existing-non-powered-dams-greater-1mw/`). Connector: `warehouse/connectors/ornl_npd.py`. Retrieved 2026-10-23T11:05:59Z (last modified 29 August 2024; the data created April 2012); ceiling one request.

Entities, 597 dams, 10,801 MW of potential (median 4.5 MW; 23 above 100 MW, the largest the Ohio River's Locks and Dams 53 and 52, 496 and 495 MW, and John T. Myers, 395 MW, all Corps of Engineers navigation dams). `entity_id` `ornl_npd:<National Inventory of Dams id>`; `entity_type` `project` (a potential site, not a plan; `status` empty); `geo` `US-<state>`, empty for the 36 dams on a state border, whose pair (IL/KY and the like) stays in `state` (44 single states and 12 pairs); `operator` the dam's owner (Corps of Engineers districts and the Bureau of Reclamation the most frequent); `capacity_mw` ORNL's potential capacity, its potential annual energy over a regional capacity factor; the rest ORNL's fields: county, city, river, `year_built` (0 for 21 dams, as ORNL writes it), storage (acre-feet), federal regulator (Corps 233, Reclamation 22, empty 321), estimated head (ft) and its source, the hydrologic region, annual mean flow (cfs), `potential_mwh_year` and `capacity_factor_pct`. The monthly flows and energies are not taken.

ORNL's caution, carried in the header: the flows and heads are estimates not measured at the dams, and "do not represent the actual numbers for engineering design". Cross-check (session 938): of `ornl_hydropower_pipeline`'s 92 non-powered dam projects, 67 have a dam of this table in the same state sharing a word of its name, read by hand in part (Tygart, 30 MW proposed against 47 of potential; Demopolis, 48 and 238). Session 946, against the code: the header's three largest gave an empty state for the border dams; the header now gives ORNL's pair (IL/KY), and the table was written again (the rows unchanged).

## The units (session 943; added by session 946)

`ornl_eha_hydropower_units`: ORNL's Existing Hydropower Assets (EHA) Unit Database, 2026 (M.M. Johnson, S.-C. Kao and R. Uria-Martinez; DOI 10.21951/FY2026/3374522), sheet "Data" of `ORNL_EHAHydroUnit_PublicFY2026.xlsx`, linked from `https://hydrosource.ornl.gov/data/datasets/eha-unit-2026/`. Connector: `warehouse/connectors/ornl_eha_units.py`. Ceiling one request.

Entities, 5,362 units (5,204 hydro, 158 pumped storage: `unit_type` HY or PS, as ORNL writes them), 102,688 MW in 2,258 plants. `entity_id` `ornl_eha_unit:<EHA_PtGnID>`; `entity_type` `generator`; `name` "<plant>, unit <EHA unit id>"; `geo` empty (the sheet gives a county FIPS code, no state; the plant's state is in `ornl_eha_hydropower_plants`, by `eha_plant_id`); `lat`, `lon` the plant's; `capacity_mw` the unit's; the rest ORNL's: owner, EIA plant and generator ids, FERC id, first and refurbishment years, turbine type (Francis 2,347, Kaplan 1,282, Pelton 342, pumps 170, Unknown 1,213) and maker, speed (rpm), rated head (ft), power (hp), minimum load (MW, given for 4,121 units) and start time from cold shutdown (given for 4,116: 10M 2,879, 1H 1,037, 12H 194, OVER 4), hydrologic unit and county FIPS code. "Unknown" is kept as ORNL writes it.

Cross-check (session 943): every plant of `ornl_eha_hydropower_plants` has units here; the units summed equal the plant's capacity within 1 MW at 2,247 of 2,257 plants, and their count the plant's number of units at 2,246 of 2,255. One plant of the unit table is not in the plant table. Session 946, against the code: the connector's description gave the pumped storage type as PSH; ORNL writes PS, and the description is corrected.
