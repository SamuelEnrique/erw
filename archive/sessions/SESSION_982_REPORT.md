# Session 982 report: the nation's dams (the U.S. Army Corps of Engineers' National Inventory of Dams)

23 October 2026, from 13:58 UTC, on lab-desktop (the data machine), a session of `queue/done/055-afternoon-23-october-data-outlook-hybrids-loans-dams.md`. Model spend USD 0. Pulls: 3 requests of 15 (nid.sec.usace.army.mil's robots file: none, HTTP 404; a HEAD request for the national download's size; the download, 70 MB).

## Read these first

- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `usace_nid_dams`, 92,788 dams in 52 states and territories (the inventory's data last updated 22 October 2026), each with its NID and Federal IDs, owners and owner types, primary purpose and purposes (2,532 list hydroelectric), place, county, river, dam type, height, length, year completed, NID and normal storage, surface and drainage area, maximum discharge and locks.
- **A new entity type, `dam`** (Decision 57), added to the data standard and the validator together; until this chain lands, writes and uploads of the table run with the branch's validator copied in.
- **The key is the Federal ID:** the NID ID repeats for a dam's associated structures (787 repeats), the Federal ID is unique.
- **Not taken:** the inventory's inspection, condition assessment, hazard potential and emergency action plan fields; the ERW holds dams for the energy they hold or could.
- **The cross-check against `ornl_npd_potential`:** 545 of its 597 non-powered dams (the 2012 assessment) are in today's inventory by NID id, every one in the same state where ORNL gives one; 18 of them now list hydroelectric among their purposes. `ornl_eha_hydropower_plants` carries no NID id, so it cannot be joined.

## Decisions made without you

- **Two dams with one coordinate of the two:** the pair left empty, the one given kept in `coordinate_given` (the validator refuses half a pair).
- **The safety fields left out,** as above; reversible by the connector's field map.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/usace_nid.py`, `tests/test_session982.py` (4 tests), this report.
- Changed: `warehouse/validate/erw_validate.py`, `docs/datastandard.md` (Decision 57), `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c055/s982/`, `runs/license_reads/s982/`, `runs/s982*`, `warehouse/raw/usace_nid/`.
