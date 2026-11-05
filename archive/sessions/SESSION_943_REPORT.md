# Session 943 report: the hydropower fleet's units (ORNL)

23 October 2026, from 11:17 UTC, on lab-desktop (the data machine), a session of `queue/done/053-day-23-october-data-world-energy-dams-solar-projects.md`, the first of its two sessions of a source of its own choosing. Model spend USD 0. Pulls: 3 requests of 20, 11 seconds apart (HydroSource's robots file, asked in a call of its own and read first; the EHA Unit Database 2026 page; its workbook).

## Read these first

- **Why this source:** `ornl_eha_hydropower_plants` (session 911) holds each plant; its units are how a hydro plant's flexibility is judged (how many machines, how small a load they hold, how fast they start). ORNL publishes them beside the plants, under the same policy.
- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `ornl_eha_hydropower_units`, 5,362 units, 102,688 MW in 2,258 plants: each unit's plant, owner, type, EIA plant and generator ids, capacity, first and refurbishment years, turbine type (Francis 2,347, Kaplan 1,282, Pelton 342, pumps 170, unknown 1,213) and maker, speed, rated head, power, minimum load and start time from cold shutdown.
- **The cross-check against `ornl_eha_hydropower_plants`:** every one of its 2,257 plants has units here; the units' capacity summed equals the plant's within 1 MW at 2,247 plants (102,778 and 102,684 MW in all), and the units counted equal the plant's number of units at 2,246 of 2,255. One plant of the unit table is not in the plant table.

## Decisions made without you

- **`geo` empty:** the sheet gives a county FIPS code but no state; the plant's state is one join away (`eha_plant_id`).
- **ORNL's "Unknown" kept as written** in the refurbishment year, turbine type and maker.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/ornl_eha_units.py`, `tests/test_session943.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c053/s943/`, `runs/license_reads/s943/`, `runs/s943*`, `warehouse/raw/ornl_eha_units/`.
