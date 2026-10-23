# Session 897 report: each plant's monthly generation and fuel (EIA-923)

23 October 2026, from 06:27 UTC, on lab-desktop (the data machine), a session of `queue/done/049-day-23-october-data-margins-schedules-emissions.md`. Model spend USD 0. Pulls: EIA, 4 requests of 4 (the EIA-923 page, the 2025 and 2026 zips through the probe, and the 2025 zip again through the connector's trial).

## Read these first

- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `eia923_plant_fuel_monthly`, 660,531 rows, 14,091 plants, January to December 2025. It holds each plant's monthly net generation (MWh) and fuel consumed in all and for electricity (TBtu), by reported prime mover and fuel, with EIA's operator, NERC region, balancing authority, sector, combined heat and power flag and whether the plant reports monthly or annually.
- **Only 2025, not "from 2020":**
  - The EIA-923 page links 2008 to 2024 under `/archive/`, which EIA's robots file disallows, and only 2025 and 2026 (to date) outside it.
  - The 2026 zip was fetched whole, but only through the probe, and the ceiling was spent before the connector could save it. A later run takes it with one request (`--years 2025 2026`).
- **The cross-check:**
  - `eia923_plant_fuel_annual` ends in 2024, so the two do not overlap.
  - Against `eia_state_generation_monthly` instead: the plants' net generation summed by state and month equals EIA's state figure within 0.5 percent in 567 of 624 state-months, and within 2 percent in 606.
  - The U.S. in 2025: 4,428.9 TWh here against 4,441.4 TWh. The left-out state increments are part of the gap.
- **Plant 99999, EIA's "State-Fuel Level Increment"** (an aggregate by state and fuel, not a plant), is left out, as the EIA-861 connectors leave EIA's 99999 out.

## Decisions made without you

- **The connector asks for the year's zip directly** (`xls/f923_<year>.zip`), not the page first: one request a year. An older year answers 404 there and stops the run rather than being sought under `/archive/`.
- **MMBtu as TBtu,** as `eia923_plant_fuel_annual` gives fuel.
- **Not taken:** the physical quantities (each fuel in its own unit), the heat content per unit and the energy storage sheet.
- **My fault, the second time in two chains:** the probe script cut the 23 MB zip at 20 MB, wasting a request. The script's limit is raised and a memory written: data files go through the connector's trial.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia923_monthly.py`, `tests/test_session897.py` (4 tests), this report.
- Changed:
  - `build_coverage.py`, `release_v1.py`, `live_set.yaml`
  - `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`
  - `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`
- On the data machine only: `runs/c049/`, `runs/license_reads/s897/`, `runs/s897*`.

## Corrected by session 905

The method notes' checks (session 905) found these against the code and the tables:

- `x_respondent_frequency` holds M (210,003 rows), A (106,407) and AM (344,121), not only monthly or annual.
- One entity (`eia923m:8825:ST:RFO:`, 36 rows) has no state and no name in EIA's file, so its `geo` is US and its `node` empty. The docstring now says so.
