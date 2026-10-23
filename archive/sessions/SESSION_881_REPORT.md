# Session 881 report: chain 049 written first; each utility's energy efficiency programs

23 October 2026, from 04:23 UTC, on lab-desktop (the data machine), the first session of `queue/done/048-night-23-october-data-utility-files-products.md`. Model spend USD 0. Pulls: none (the saved EIA-861 zips).

## Read these first

- **Chain 049 written and pushed first:** `queue/next/049-day-23-october-data-margins-schedules-emissions.md` (sessions 895 to 908, machine: data), committed alone and pushed to main (`85c41ab6`) with a snapshot pair (0 differences), before any other work. It takes the siting gaps' reserve margins (EIA's Electric Power Annual by NERC assessment area), EIA-860's environmental and multifuel schedules, EIA-923's monthly generation by plant, EPA's unit emissions, EIA's pipeline projects, BOEM's offshore wind leases and an ERCOT node's county and zone as a derived table.
- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `eia861_energy_efficiency`, 187,850 rows, 734 utilities, 794 entities, 2015 to 2025, from `Energy_Efficiency_<year>.xlsx`: by sector, the reporting year's incremental savings (MWh, MW) and costs (customer incentives and other costs, USD), the same programs' savings and costs over their life, and the weighted average life (years). All utilities' first-year savings: 26.1 TWh in 2015, 28.2 in 2020, 24.2 in 2025; customer incentives USD 3.45 billion, 3.15 billion and 4.36 billion.
- **The cross-check, against `eia_energy_efficiency_state_annual` (EIA's state profiles, by API):** the utilities summed by state and year equal the state table's first-year energy savings within 1 percent in 255 of 255 state-years (253 within 0.1 percent), its life cycle savings in 509 of 509, its customer incentives in 249 of 249. Peak savings agree within 1 percent in 248 of 252; the four apart are small states' totals of a few MW (Alaska 2018 and 2019, Delaware 2017), where EIA's rounding of single utilities shows.
- **Utilities reporting fall from 653 in 2019 to 417 in 2020:** EIA moved the small utilities to the short form (EIA-861S) from 2020, which carries no efficiency figures; the table holds what EIA holds.
- No record had two values under one key.

## Decisions made without you

- A connector of its own (`eia861_efficiency.py`) that imports `eia861_programs.py`'s stacked-heading reader, rather than a third table in that connector: a run writes only this table.
- Variables `annual_` and `life_` for EIA's "Reporting Year Incremental" and "Incremental Life Cycle" groups; the group headings read as prefixes, since EIA writes "Cost" in 2015 and "Costs" later. EIA's Website column kept as `x_website`.

## For Samuel's ruling

- None new.

## Files

- New: `queue/next/049-day-23-october-data-margins-schedules-emissions.md` (on main), `warehouse/connectors/eia861_efficiency.py`, `tests/test_session881.py` (5 tests), this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c048/`, `runs/s881*`.
