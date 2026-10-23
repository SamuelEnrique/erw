# Session 939 report: utility-scale solar projects' costs and output (Berkeley Lab)

23 October 2026, from 11:09 UTC, on lab-desktop (the data machine), a session of `queue/done/053-day-23-october-data-world-energy-dams-solar-projects.md`. Model spend USD 0. Pulls: none (the 2025 solar data file session 915 saved).

## Read these first

- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `lbnl_solar_projects`, 1,775 projects (1,759 PV, 16 CSP), 112,820 MW-AC, from the "Individual_Project_Data" sheet of LBNL's Utility-Scale Solar, 2025 Data Update. Each project's EIA id, place, irradiance, technology and design (DC capacity, inverter loading ratio, mount, tracking, tilt, azimuth), hybrid configuration and storage (198 projects), offtaker, 2024 energy and capacity value, LCOE with and without federal tax credits, levelized PPA price (425 projects) and its capacity factor in each year from 2008 to 2024. The median PV project ran at a 21.9 percent capacity factor in 2024.
- **The cross-checks, by EIA plant id:**
  - 1,772 projects carry an EIA id (1,767 plants); 1,740 of them are in `uspvdb_solar_facilities`, 1,755 have PV generators in `eia860m_operating_generators`.
  - The AC capacity equals EIA-860M's PV nameplate within 5 percent at 1,637 of 1,750 plants and within 10 percent at 1,686 (109,926 and 110,626 MW in all).
- **The same file as `lbnl_ppa_prices`:** the connector reads lbnl_ppa_prices.py's saved file and asks nothing while it is on the machine.

## Decisions made without you

- **LBNL's EIA ids kept as it writes them,** with their suffixes ("ret", "a", "b"), not mapped to a status; the three projects without one take their name as id.
- **The capacity factors as columns, one a year,** in an entities table, rather than a series table of their own; they are LBNL's figures for each project.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/lbnl_solar_projects.py`, `tests/test_session939.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c053/s939/`, `runs/s939*`.
