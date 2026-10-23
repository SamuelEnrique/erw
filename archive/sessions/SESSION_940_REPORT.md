# Session 940 report: PV+battery PPA prices (Berkeley Lab); REC prices held for a ruling

23 October 2026, from 11:12 UTC, on lab-desktop (the data machine), a session of `queue/done/053-day-23-october-data-world-energy-dams-solar-projects.md`. Model spend USD 0. Pulls: none (the files session 915 saved).

## Read these first

- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `lbnl_hybrid_ppa_prices`, 113 PV+battery PPAs executed from September 2015 to June 2025 (102 greenfield, 11 batteries retrofitted to an operating PV plant), from the solar file's "PV+Battery Hybrid PPA Price" sheet. Each PPA's plant, state, EIA ids, PV and battery size, duration and ratio, dates, and the levelized price of the PV, the battery adder (per MWh of PV, per MWh stored, per MW-month) and the two together, in real 2024 USD per MWh of PV output. The median combined price was 29.4 USD/MWh-PV for 2019's PPAs, 40.6 for 2021's, 70.0 for 2024's and 77.9 for 2025's.
- **The cross-checks:**
  - The combined price equals the sheet's own price column for its chart in all 113 rows.
  - Of the 114 EIA ids the rows name, 73 are projects of `lbnl_solar_projects` (the other 41 are not in that sheet); of 63 greenfield PPAs matched there, 39 give the same battery MW and PV MW-AC.
- **REC prices not taken:** the wind file's "REC Prices" sheet, monthly renewable energy certificate prices by state from 2010, names its source as Marex Spectron, a broker; LBNL's CC BY license covers its own work, and whether it extends to a broker's prices it republishes is a question for the owner.

## Decisions made without you

- **One events table for both kinds,** with `x_kind`; a retrofit is dated by its retrofit's execution.
- **The REC prices held,** as above, rather than taken under LBNL's license.

## For Samuel's ruling

- **The REC prices in Berkeley Lab's wind data file** (Marex Spectron's, as LBNL republishes them): whether the ERW may carry them under LBNL's CC BY 4.0 notice, or needs Marex's word.

## Files

- New: `warehouse/connectors/lbnl_hybrid_ppa_prices.py`, `tests/test_session940.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c053/s940/`, `runs/s940*`.
