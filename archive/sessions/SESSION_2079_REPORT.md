# Session 2079 report: method notes for this chain's tables

23 October 2026, from 20:27 UTC, on lab-desktop (the data machine), the tenth session of `queue/done/067-day-25-october-data-neighbours-emitters-disasters-world-oil.md`. Model spend USD 0. Pulls: none.

## Read these first

- **Four notes written,** one for each of this chain's tables, by a helper agent and checked by this session: `docs/methods/ieso_ontario_demand_hourly.md`, `aeso_alberta_load_hourly.md`, `epa_ghgrp_facility_emissions.md`, `noaa_ncei_billion_disasters.md`. Each session's cross-check was recomputed and agrees (Ontario's exports against EIA-930, 0.905; Alberta's 2025 average 10,316.3 MW and peaks; CO2e over CO2 at the power plants, median 1.0010; 27 of 29 cyclones with storm events).
- **Each note's claims were checked against the code, the table and the reports, as session 960 did; every point was acted on.**
  - **Reports corrected** (each line marked): session 2070 said the U.S. flow never exceeds Ontario's exports (it does in 7 hours of 6 October 2026, by at most 202 MW), and missed the hour the IESO's file lacks (2025-05-01T05:00Z, the market renewal's first); session 2071 said the AESO's other table is public (`large_load_waits` is internal); session 2072 said seven distribution companies keep the facility's id (one row of the table does; the others have no value from 2015); session 2073 said Beryl's events record no damage (USD 14,000).
  - **Descriptions corrected, two tables written again** (their rows unchanged, offline): `ghgrp_facilities.py`'s header now names the `ghgrp:<facility id>:<state>` entities and counts pipelines and distribution companies as facility-states; `noaa_billion_disasters.py`'s header says NCEI gave no last-modified time instead of ending blank. `aeso_load.py`'s docstring now says the first request ends with 30 December.
  - **Session 2074's two descriptions corrected** with them (`weather_nws.py`, `lbnl_queues.py`).
  - **Not a fault:** the events tables' `source_report` in `coverage.csv` reads "1 outlets", `build_coverage.py`'s summary for an events table (the storm events read the same).
- **The Method cells** of the four (and session 2074's six) are filled in `docs/coverage.md`.

## Errors

- **The rewrites' metadata patches met their own older rows:** union-resolving kept both rows of each table in `coverage.csv`, `docs/coverage.md` and the archive manifest, and the second patch did not apply until the first's conflicts were staged; the older rows were dropped by hand and `runs/c059/resolve.sh` found no row twice.

## Decisions made without you

- **The tables written again for the header's words alone,** since the corrections concern what the header says the rows are.

## For Samuel's ruling

- None new.

## Files

- New: the four notes, this report.
- Changed: `warehouse/connectors/ghgrp_facilities.py`, `noaa_billion_disasters.py`, `aeso_load.py`, `weather_nws.py`, `lbnl_queues.py` (descriptions and headers), the reports of sessions 2070 to 2073, `docs/coverage.md`, `coverage.csv` and `archive_manifest.csv` (the two tables written again).
- On the data machine only: `runs/s2079a*`, `runs/s2079b*`, `runs/c067/s2079*`.
