# Session 944 report: the wind fleet's 2025 capacity factors (Berkeley Lab)

23 October 2026, from 11:20 UTC, on lab-desktop (the data machine), a session of `queue/done/053-day-23-october-data-world-energy-dams-solar-projects.md`, the second of its two sessions of a source of its own choosing. Model spend USD 0. Pulls: none (the data file `lbnl_ppa_prices.py` saved, read again from `warehouse/raw/lbnl_ppa_prices/`).

## Read these first

- **Why this source:** the ERW holds what wind costs to contract (`lbnl_ppa_prices`) and where the turbines stand (`uswtdb_wind_turbines`, `eia860_wind_generators`), but not how hard each plant works. Berkeley Lab's wind data file gives every land-based plant's 2025 capacity factor with its commercial operation period and repower status, under the same CC BY 4.0 notice as the prices already held, and it was on the machine.
- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `lbnl_wind_capacity_factors`, 1,210 plants from the sheet "Capacity Factor in 2025 by COD" (project columns K to N): entity `lbnl_wind:<EIA plant code>`, capacity factor as a fraction (median 0.319, from 0.037 to 0.624), `x_cod` (1998-99 to 2024) and `x_repower` (101 partial, 22 full).
- **The cross-check against EIA:** every plant is in `eia860_wind_generators` (2025). For the 1,209 plants with twelve months of 2025 net generation in `eia923_plant_fuel_monthly`, generation over EIA-860 nameplate times 8,760 hours equals LBNL's figure within 0.01 at 1,138 plants (median difference 0.000); the capacity-weighted fleet figure is 0.340 by LBNL and 0.336 by EIA.

## Decisions made without you

- **A plant without a value is left out,** not written as empty; none was in this file (1,210 codes, 1,210 values).
- **LBNL names no project,** so `node` is "EIA plant <code>"; the name is one join away in `eia860_wind_generators`.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/lbnl_wind_capacity_factors.py`, `tests/test_session944.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c053/s944/`, `runs/s944*`.
