# Session 916 report: the hydropower and pumped storage pipeline (ORNL)

23 October 2026, from 08:33 UTC, on lab-desktop (the data machine), a session of `queue/done/051-day-23-october-data-world-gas-hydro.md`. Model spend USD 0. Pulls: 3 requests of 20, 11 seconds apart (HydroSource's robots file, asked alone first; the U.S. Hydropower Development Pipeline Data 2026 page; its workbook).

## Read these first

- **Why this source:** the ERW held the hydropower fleet in operation (session 911) but no list of proposed pumped storage, the largest long-duration storage in the country's plans. ORNL's pipeline is the national list, from FERC's permits, licenses and exemptions and Reclamation's leases, under the HydroSource policy session 914 recorded (may be public).
- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `ornl_hydropower_pipeline`, 196 projects on 31 December 2025: 128 hydropower (1,391 MW; non-powered dams, conduits, new stream-reaches) and 68 pumped storage (59,350 MW; 58 closed-loop, 10 open-loop). Each project's FERC docket, status (99 issued preliminary permits, 38 issued licenses, 23 issued exemptions, 26 pending, 7 under construction), capacity, place, developer and its type, dam and its owner, waterway, NERC region and hydrologic unit. An entities table: `status` `planned` or `under_construction`, ORNL's own status in `permit_status`.
- **The cross-checks:**
  - No pipeline docket is a plant of ORNL's operating fleet (`ornl_eha_hydropower_plants`), as the two databases intend.
  - Of the 37 plants with planned hydro or pumped storage generators in EIA-860M (`eia860m_planned_generators`, 3,031 MW), 30 are in the pipeline by name and state, read by hand from a list of shared name words (`runs/c051/s916/xcheck.py`). The 7 not found include the 1,000 MW Intermountain pumped storage project in Utah. The pipeline is twenty times EIA-860M's planned pumped storage (59,350 against 2,600 MW): EIA-860M lists only projects with a planned date, the pipeline every preliminary permit.

## Decisions made without you

- **The workbook taken by its public S3 link on the landing page, as in session 911.** The page shows a download form asking a name, e-mail address and company; no form was filled, and the policy says the data are shared without restriction.
- **The snapshot dated 31 December 2025,** as the workbook's summary and the page say; its field description still dates the status 31 December 2023. Named in the header.
- **A project with no FERC docket** (two Reclamation lease of power privilege authorizations and one preliminary lease) takes its name as its id.

## For Samuel's ruling

- **HydroSource's download form:** the ERW takes ORNL's workbooks by their public links without the form (name, e-mail, company). If the owner prefers the form filled, it is a person's step, once a file.

## Errors

- The metadata patch of the write met the previous session's rows in the same place (both ORNL tables sort together); `runs/union_resolve.py` joined the two sides and `finish_table.sh` was run again, passing.

## Files

- New: `warehouse/connectors/ornl_hydro_pipeline.py`, `tests/test_session916.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c051/s916/`, `runs/license_reads/s916/`, `runs/s916*`, `warehouse/raw/ornl_hydro_pipeline/`.
