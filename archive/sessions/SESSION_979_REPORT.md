# Session 979 report: hybrid power plants (Berkeley Lab)

23 October 2026, from 13:48 UTC, on lab-desktop (the data machine), a session of `queue/done/055-afternoon-23-october-data-outlook-hybrids-loans-dams.md`. Model spend USD 0. Pulls: 3 requests of 10 (eta-publications.lbl.gov's robots file, asked in a call of its own and read first: it disallows `/search/`, not `/publications`; the publications list filtered by title; the data file).

## Read these first

- **The edition:** "Hybrid Power Plants: Status of Operating and Proposed Plants, 2026 Data Update" (plants operating through 2025; the file last modified 29 September 2026), the newest of the six editions the list shows.
- **One table written, validated, archived, in coverage (sector power), held from the live set, and held internal:** `lbnl_hybrid_plants`, from the sheet "01. Operating Plants": 632 operating hybrid plants (86,263 MW of generators and storage: 436 PV+storage, 40 fossil+PV, 28 fossil+storage, 26 fossil+hydro, 24 wind+storage, 12 wind+PV, 6 wind+PV+storage, 60 others), each with its EIA plant id, state, place, generator and storage capacity, storage energy and duration, online dates, coupling, storage technology and the uses its battery reports; and the 436 storage-only plants LBNL lists beside them (their storage MW, MWh and duration given, no total).
- **Why internal:** this file's notice is the Department of Energy's contract notice only ("the U.S. Government retains ... a non-exclusive, paid-up, irrevocable, worldwide license to publish or reproduce the published form of this dataset, or allow others to do so, for U.S. Government purposes"), without the CC BY 4.0 statement LBNL's wind, solar and Queued Up files carry. The license record shows the flag stricter than Berkeley Lab's verdict, which rests on the CC BY statement.
- **Not taken: "03. Hybrids in Queues",** LBNL's Queued Up records, held as `lbnl_interconnection_queue`.
- **The cross-checks:** of `lbnl_solar_projects`' 160 PV+storage projects, 136 are PV+storage plants here by EIA id (the solar file's storage was added later at some); of the 479 plants with both PV and battery generators in `eia860m_operating_generators`, 411 are LBNL's PV+storage plants.

## Decisions made without you

- **Held internal** until Samuel rules (below); reversible by one line of `sources.csv`.
- **The storage-only plants kept,** typed "Storage" as LBNL types them, with the total capacity empty as LBNL leaves it.
- **A "missing" EIA id** (10 plants) named by the plant: `lbnl_hybrid:none-<name>`.

## For Samuel's ruling

- **Whether Berkeley Lab's hybrid plants file may be redistributed** like its other data files: it states no CC BY license, only the U.S. Government's license for its own purposes. If yes, one line of `sources.csv` (`license` public) and the Stanford upload.

## Files

- New: `warehouse/connectors/lbnl_hybrid_plants.py`, `tests/test_session979.py` (3 tests), this report.
- Changed: `build_coverage.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c055/s979/`, `runs/license_reads/s979/`, `runs/s979*`, `warehouse/raw/lbnl_hybrid_plants/`.
