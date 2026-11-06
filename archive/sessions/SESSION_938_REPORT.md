# Session 938 report: hydropower potential at non-powered dams (ORNL)

23 October 2026, from 11:05 UTC, on lab-desktop (the data machine), a session of `queue/done/053-day-23-october-data-world-energy-dams-solar-projects.md`. Model spend USD 0. Pulls: 3 requests of 10, 11 seconds apart (HydroSource's robots file, asked in a call of its own and read first; the dataset's page; its workbook).

## Read these first

- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `ornl_npd_potential`, 597 existing U.S. dams without power whose estimated potential is above 1 MW, 10,801 MW in all, from ORNL's "U.S. Hydropower Potential from Existing Non-powered Dams (greater than 1MW)", the 2012 national assessment (Hadjerioua, Wei and Kao, DOE/EE-0711). Each dam's National Inventory of Dams id, name, owner, place, river, year built, storage, federal regulator, estimated head and flow, potential annual energy, regional capacity factor and potential capacity. 23 dams hold more than 100 MW each, the largest the Ohio River's Locks and Dams 52 and 53 (495 and 496 MW) and John T. Myers (395 MW), all Corps of Engineers navigation dams.
- **An old assessment:** the data were created in April 2012 from flows and heads not measured at the dams; ORNL says they "do not represent the actual numbers for engineering design". The header says so.
- **The cross-check against `ornl_hydropower_pipeline`'s 92 non-powered dam projects:** 67 have a dam of this table in the same state sharing a word of its name, a loose match read by hand in part (Tygart Dam, 30 MW proposed against 47 MW of potential; Dresden Island, 11 and 16; Demopolis, 48 and 238; Overton, 49 and 125). Proposals are often a part of a dam's estimated potential, and sometimes more where ORNL's head estimate is low.

## Decisions made without you

- **`entity_type` `project`, `status` empty:** a potential site, not a plan.
- **`geo` empty for the 36 dams on a state border** (IL/MO, IA/IL, MN/WI and the rest): the entities shape takes one code, and ORNL's pair stays in `state`.
- **The monthly flows and energies not taken;** the annual ones are.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/ornl_npd.py`, `tests/test_session938.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c053/s938/`, `runs/license_reads/s938/`, `runs/s938*`, `warehouse/raw/ornl_npd/`.
