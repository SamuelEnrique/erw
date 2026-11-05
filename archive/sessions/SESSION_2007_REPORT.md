# Session 2007 report: offshore oil and gas platforms (BOEM's platform files)

23 October 2026, from 15:22 UTC, on lab-desktop (the data machine), the second of `queue/done/056-evening-23-october-data-jobs-reactors-large-loads-hydro.md`'s two sessions of a source of its own choosing. Model spend USD 0. Pulls: 11 requests of 20 (www.data.boem.gov's robots file, asked in a call of its own and read first: it names 446 other readers and has no rule for every reader; the Platform page; the three layout pages; then the trial's six: the three layouts and the three zips). The write, at 16:32 UTC when the lock was free, reused the saved files with the branch's validator copied into the main checkout for the one run (below), and main's put back.

## Read these first

- **Why this source:** the ERW holds BOEM's lease production and renewable leases, but not the structures that produce offshore oil and gas: where they stand, when they were installed and removed, how deep the water is, and whether they produce.
- **One table written, validated, archived, in coverage (sectors oil and gas, public), in the release package, both holds:** `boem_offshore_platforms`, 7,092 structures in 6,181 complexes on the Outer Continental Shelf: 1,312 active (666 on complexes flagged producing) and 5,780 removed, installed from 1942 to 2025, each with its place (7,084 with coordinates), area and block, structure type (fixed 3,796, caisson 2,584, well protector 642, and floating designs), install and removal dates, slots and decks, and its complex's water depth, distance to shore, lease, field, operator number and production flags.
- **A new entity type, `platform`** (Decision 58), added to `docs/datastandard.md` and the validator together; until this chain lands, writes, Method-cell runs and uploads of the table run with the branch's validator copied in. The data standard's entity type row now also names `dam` (Decision 57), which session 982 added to the decisions only.
- **The cross-check against `boem_ogor_lease_production_monthly`** (to June 2026): of the 335 leases on the masters rows of the 666 producing active structures, 201 report production in 2026; a complex's masters row names one lease, and production from a unit or a neighbouring lease is reported under others.
- **Each layout read from BOEM's own page** (start, length and name of each field), never assumed.

## Decisions made without you

- **One row a structure,** the complex's fields repeated on each of its structures; a removed structure keeps its row with `status` retired.
- **No operator names:** BOEM's files give a company number; its company list is not taken.
- **The approvals, removals and rig files not taken.**

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/boem_platforms.py`, `tests/test_session2007.py` (4 tests), this report.
- Changed: `docs/datastandard.md` (Decision 58), `warehouse/validate/erw_validate.py`, `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c056/s2007/`, `runs/license_reads/s2007/`, `runs/s2007*`, `warehouse/raw/boem_platforms/`.
