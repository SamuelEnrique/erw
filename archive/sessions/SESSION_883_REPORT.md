# Session 883 report: distribution circuits and distributed generation by utility

23 October 2026, from 04:33 UTC, on lab-desktop (the data machine), a session of `queue/done/048-night-23-october-data-utility-files-products.md`. Model spend USD 0. Pulls: none (the saved EIA-861 zips).

## Read these first

- **Two tables written, validated, archived, in coverage (sector power, public), in the release package, both holds:**
  - `eia861_distribution_systems`: 34,947 rows, 2,862 utilities, 2015 to 2025, from `Distribution_Systems_<year>.xlsx`: each utility's distribution circuits by state, and those with voltage or VAR optimization. All utilities: 204,884 circuits in 2015 and 206,255 in 2025; those optimized rose from 44,006 to 59,566.
  - `eia861_distributed_generation`: 179,161 rows, 705 utilities, 2016 to 2025, from `Non_Net_Metering_Distributed_<year>.xlsx`: the generators on distribution systems that are not net metered, by utility and state: their number, capacity, back-up-only and utility-owned capacity, and capacity by technology (solar, battery, wind, hydro, fuel cells, internal combustion, combustion turbines, steam, other) and sector (including directly connected). All utilities: 2,143 MW in 2016, 6,922 MW in 2025 (3,897 MW solar, 939 MW and 2,937 MWh of batteries).
- **Dynamic pricing's file was already taken** by chain 047's session 868 (`eia861_dynamic_pricing`), so the session's second slot took the distributed generation file, the other EIA-861 file by utility the ERW did not hold.
- **The cross-checks:**
  - circuits with optimization never exceed the circuits (15,914 of 15,914 records);
  - for distributed generation, the technologies sum to the total in 4,884 of 4,884 records, the solar sectors to solar's total in 4,010 of 4,010, and the total capacity equals the technologies' total in 4,869 of 4,872;
  - 2025's utilities summed by state against EIA's own state-level sheet: 6,884 MW against 6,864, apart by EIA's "State Adjustment" rows (utility 99999), which the table leaves out as every EIA-861 table does.
- **Not taken:** 2015's distributed generation file, which has another form (technology totals without sectors, and a separate dispersed generation sheet); 2025's state-level sheet (no utility).
- No record had two values under one key.

## Decisions made without you

- "Storage" (2016 to 2024) and "Battery" (2025) read as one technology, `battery`, in MW; 2025's new "Battery Energy" kept apart as `battery_energy_<sector>` in MWh.
- Two connectors, one for each file, each written on its own. The second table's metadata patch met the first's uncommitted lines in the branch; `runs/union_resolve.py` joined them (both sides only added lines) and the finish step was run again.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia861_distribution_systems.py`, `warehouse/connectors/eia861_distributed_generation.py`, `tests/test_session883.py` (6 tests), this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c048/`, `runs/s883*`.
