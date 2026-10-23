# The hydropower fleet and its pipeline (Oak Ridge National Laboratory, HydroSource)

Energy Research Warehouse (ERW), method note written in session 918 (chain 051) for tables first written on 23 October 2026.

Tables: `ornl_eha_hydropower_plants`, `ornl_hydropower_pipeline`, `ornl_hydropower_relicensing`

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

- ORNL's unit database (EHA Unit, each turbine), its generation and capacity factor time series, and capacity additions at existing plants (ORNL leaves them out of the pipeline: they rest on a proprietary source).

## The relicensing and surrender records (session 930; added by session 932)

`ornl_hydropower_relicensing`: ORNL's U.S. Hydropower Relicensing and License Surrender Data, 2026 (M.M. Johnson and R. Uria-Martinez; published May 2026; DOI 10.21951/HMR_RelicenseSurrender/3031244), sheets "Relicenses" and "Surrenders" of the workbook its landing page links (`https://hydrosource.ornl.gov/data/datasets/us-hydropower-relicensing-and-license-surrender-data-2026/`). Connector: `warehouse/connectors/ornl_hydro_relicensing.py`. A snapshot of 31 December 2025, retrieved 2026-10-23T10:14:02Z (last modified 6 May 2026); ceiling one request.

Events, 559 records. `event_id` `ornl_relicense:<FERC docket>:<relicense|surrender>` (one surrender docket the sheet gives twice keeps `-2`); `event_date` FERC's issuance where given (313), else the application's (194), else the notice of intent's (52), with `x_date_kind`; `event_type` `hydro_relicense` (407) or `hydro_license_surrender` (152); `parties` the licensee; `entity_ids` `ornl_eha:<EHA_PtID>` where ORNL gives the plant (548); `mw` the new license's capacity (relicense) or the surrendered project's (surrender); `status` ORNL's own (Issued Relicense 198, Pending Relicense 160, Submitted NOI to Relicense 40, Converted to Exemption 9; Issued Surrender 82, Pending Surrender 31, Submitted NOI to Surrender 9, Issued License Termination 15, Issued Exemption Termination 15). `x_*` the other fields: the old capacity, the dates, the process (TLP 219, ILP 157, ALP 22), the new mode, the settlement (57), construction and turbine-generator flags, the dam's removal (28 surrenders) and the reason. A heading not in the map or a record without a date stops the run.

Cross-checks against `ornl_eha_hydropower_plants` (session 930): of the 405 relicensing records that name a plant, 401 are in the fleet table and 396 carry its docket; 193 of 197 issued relicenses give the fleet table's FERC expiry; the new capacity equals the fleet table's within 1 MW for 130 of 197; 46 of the 143 surrenders that name a plant are still in the fleet table.
