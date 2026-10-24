# Session 2164 report: natural gas by end use and state (EIA's Natural Gas Annual), the uses the warehouse did not hold

24 October 2026, from 00:23 UTC, on lab-desktop (the data machine), the third session of `queue/done/094-day-31-october-data-britain-imports-gas-use-waterways.md`, unattended. Model spend USD 0. Pulls: 2 requests of 15 (the route's facet list and the data, one page).

## Read these first

- **First, what the ERW already holds:** `eia_gas_consumption_state_monthly` (session 518) takes EIA's consumption by state from the API route `natural-gas/cons/sum`, residential, commercial, industrial, electric power and total, in MMcf, a month; `eia_gas_balance_annual` holds the supply and disposition. The file's end uses residential to electric power are therefore held; the others are not.
- **One table written, validated, archived, in coverage (sector gas), in the release package, both holds:** `eia_gas_other_uses_state_annual`, the same route's four other processes, a year, 2001 to 2025: vehicle fuel (VDV), lease and plant fuel (VGL, one figure: EIA does not part the two here), pipeline and distribution fuel (VGP) and the volume delivered to consumers (VGT); 3,838 rows, 157 series in MMcf: vehicle fuel, pipeline fuel and deliveries for the states, DC and the nation (52 each), lease and plant fuel for the nation only (1; corrected in session 2171, this line had all four by state); 2025 is partial (pipeline fuel for the nation only, deliveries for 43 places). For the nation in 2025: 30,181,736 MMcf delivered, 2,038,482 lease and plant fuel, 1,295,483 pipeline fuel, 53,149 vehicle fuel.
- **Its own source id** (`eia:natural-gas/cons/sum:annual`), so that registering it leaves the monthly table's row of `sources.csv` as it is.
- **The cross-check** (`runs/c094/s2164/cross.py`): EIA's arithmetic holds.
  - Delivered plus lease and plant plus pipeline fuel equals the nation's total consumption (the monthly table's VC0 summed over each full year) to 1 MMcf in 17 of 25 years, and within 0.5% in the other 8 (2020: 30,602,565 against 30,574,245, 0.09%); the monthly total is held for the nation only.
  - Delivered to consumers equals the monthly table's residential, commercial, industrial and electric power summed to the year plus vehicle fuel: median 1.0000 over 1,214 state-years (from 0.9994 to 1.1987, a few small states' years where the monthly figures are withheld or revised).
  - The file's cross-check against `eia923_plant_fuel_monthly` concerned the electric power use, which the warehouse already holds; it was not run.

## The pulls

1. The process facet of `natural-gas/cons/sum` (a script that keeps the key out of every saved address): VCS, VDV, VRS, VGT, VEU, VC0, VIN, VGL, VGP.
2. The connector's trial: the four processes, annual, one page (3,838 records), reused by the write (`--offline`).

EIA's terms are the record's (record 1); api.eia.gov's robots file was read by an earlier chain (HTTP 403 without a key).

## Errors

- **The trial's first header named `frequency=monthly` in its access line, and the connector first reused the monthly table's source id;** both corrected before the write (a second trial offline).
- **The first cross-check compared against the wrong row** (`eia_gas_balance_annual` holds several entities under `total_consumption` for one place); it now compares against EIA's VC0.

## Decisions made without you

- **The four processes the warehouse lacked,** not the Natural Gas Annual's whole consumption table, whose other uses are held monthly.
- **Lease and plant fuel as EIA's one figure,** never split.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_gas_other_uses_state.py`, `tests/test_session2164.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, the coverage, sources, archive manifest and license files, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c094/s2164/`, `runs/s2164_*`, `warehouse/raw/eia_gas_other_uses_state/`.
