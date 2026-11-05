# Session 952 report: wind turbine prices, capital and levelized costs (Berkeley Lab)

23 October 2026, from 12:20 UTC, on lab-desktop (the data machine), a session of `queue/done/054-day-23-october-data-federal-royalties-wind-costs-minerals.md`. Model spend USD 0. Pulls: none (the 2026 wind data file session 915 saved, `warehouse/raw/lbnl_ppa_prices/`).

## Read these first

- **Two tables written, validated, archived, in coverage (sector power, public), in the release package, both holds,** from LBNL's Land-Based Wind Energy Technology Data Update, 2026 Edition, all in real 2025 dollars:
  - `lbnl_wind_costs` (series, 119 rows): the turbine makers' global average prices (Vestas 21 half-years from 2005, Siemens Gamesa 9 and Nordex 10 from 2016) and LBNL's average turbine price a year (2006 to 2025, 1,751 to 1,101 USD/kW, its low 990 in 2020); the capacity-weighted installed cost of each commercial operation year's projects (31 years, 1983 to 2025: 2,133 USD/kW in 2015, 1,583 in 2022, 2,096 in 2025); and the generation-weighted levelized cost (28 years, 1998 to 2025: 107 USD/MWh in 1998, 39.8 in 2022, 52.1 in 2025), each with its sample.
  - `lbnl_wind_turbine_orders` (events, 122 orders): the reported U.S. turbine orders, February 1997 to July 2016, each with its price (median 1,741 USD/kW); LBNL names no buyer, maker or size.
- **The cross-check against `nlr_atb_electricity_costs`' land-based wind (moderate case, its dollars of 2023):** LBNL's 2023 installed cost, 1,858 USD/kW, is 6 percent under the ATB's base year (1,968); 2024's, 1,891, is within 2 percent of the ATB's class 4 default (1,920); 2025's, 2,096, is 9 percent over the ATB's projection (1,872 to 1,944), and LBNL calls EIA's 2024 and 2025 cost estimates preliminary. LBNL's LCOE of 2023 to 2025 (48 to 52 USD/MWh) falls inside the ATB's range across wind classes (33 to 99).
- **What chain 053 already held from the file is not taken again:** the 2025 capacity factors (`lbnl_wind_capacity_factors`); the REC prices wait on the owner.

## Decisions made without you

- **Not taken: "Recent CapEx by Region"** (five regions' costs, but the sheet does not say which commercial operation years they average) **and "O&M Over Time"** (about 215 projects' average O&M costs, each with no project and no date beyond its COD year, some suppressed by LBNL for confidentiality). Said in the header.
- **The makers' averages at LBNL's own mid-year dates** (30 June), `freq` P1Y, `geo` empty (they are global); LBNL's own average a year, `geo` US.
- **A year with a sample and no cost** (LBNL withholds a cost from one or two projects) has no row.
- **The orders as events,** each id a hash of its date and price, as `lbnl_ppa_prices` did for PPAs without names.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/lbnl_wind_costs.py`, `tests/test_session952.py` (4 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv` (one row for the two tables, merged by hand after the resolver), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c054/s952/`, `runs/s952*`.
