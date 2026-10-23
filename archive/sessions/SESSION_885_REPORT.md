# Session 885 report: EIA-860's other schedules (owners, energy storage, solar, wind)

23 October 2026, from 04:45 UTC, on lab-desktop (the data machine), a session of `queue/done/048-night-23-october-data-utility-files-products.md`. Model spend USD 0. Pulls: none (`eia8602025.zip`, saved by session 873).

## Read these first

- **Four entities tables written, validated, archived, in coverage (sector power, public), in the release package, both holds**, from EIA-860's 2025 schedules, the generators' details that EIA-860M's tables do not carry:
  - `eia860_generator_owners` (5,680 rows): each owner's share of 4,018 jointly owned generators, with the owner's name, address and ownership ID and EIA's fraction owned;
  - `eia860_storage_generators` (1,782: 1,012 operable, 607 proposed, 163 retired or canceled): energy capacity (MWh), charge and discharge rates, storage technologies, enclosure, the uses EIA marks (arbitrage, frequency regulation, peak shaving and the rest), AC or DC coupling, and the units each supports;
  - `eia860_solar_generators` (8,520: 8,011 operable, 509 retired or canceled): tracking, tilt and azimuth, DC capacity, cell materials, net metering;
  - `eia860_wind_generators` (1,745: 1,573 operable, 172 retired or canceled): the number of turbines, their maker and model, design wind speed, wind class and hub height.
- **The cross-check, against `eia860m_operating_generators` (EIA-860M, August 2026) by plant and generator:** of the operable storage generators, 1,010 of 1,012 are there with the same nameplate in 1,010 of 1,010; solar 8,009 of 8,011, all with the same nameplate; wind 1,564 of 1,573, the same nameplate in 1,563. EIA-860M's operating list is longer (10,008 solar generators against 8,011), since it runs eight months past the 2025 year end. Owners: the shares of 4,014 of the 4,018 generators sum to 1; four do not as EIA gives them (Plant 341 CT5 sums to 1.5; one sums to 0; two to 0.9).
- **Status as the data standard's words**, EIA's code kept in `x_eia_status`: OP, SB, OA, OS operating; P, L, T, OT planned; U, V, TS under construction; RE retired; CN withdrawn (canceled); IP suspended (indefinitely postponed). No key was given twice.

## Decisions made without you

- One connector (`eia860_schedules.py`) writes the four tables, as they come from one zip; it reuses `eia860_plants.py`'s page, zip and reader helpers. A new write script, `runs/c048/write_tables.sh`, takes any number of a connector's tables under one lock, one coverage build and one archive run, so a single metadata patch reaches the branch (session 883's conflict does not recur).
- An owner's share is an entity of its own (`entity_type company`, the owner as its name); the plant's name is kept in `x_plant_name`.
- The canceled as `withdrawn` and the indefinitely postponed as `suspended` (Decision 20's words).
- The 6_1 and 6_2 environmental schedules and 3_5 multifuel are left to chain 049's session 896, as its file says.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia860_schedules.py`, `tests/test_session885.py` (5 tests), this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c048/write_tables.sh`, `runs/c048/`, `runs/s885*`.

## Corrected by session 891

The method notes' checks (session 891) found these against the code, the tables and EIA's files:

- The owners' shares: 4,014 of the 4,018 generators sum to 1 within half a percent (plant 70387 BESS1 sums to 1.0009). The generator that "sums to 0" (plant 69201, generator 11220) has one owner whose share EIA leaves empty.
- `x_owner_zip` has lost the leading zeros of some ZIP codes (8540, 2458), as the workbook's cells are numbers; kept as read, named in the method note.
- `status_date` is empty for the suspended (IP) generators as well as the proposed and the canceled.
