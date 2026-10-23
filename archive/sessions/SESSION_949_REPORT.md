# Session 949 report: the package's and the site's records

23 October 2026, from 11:43 UTC, on lab-desktop (the data machine), a session of `queue/done/053-day-23-october-data-world-energy-dams-solar-projects.md`. Model spend USD 0. Pulls: none.

## Read these first

- **Stale, as after chains 048, 051 and 052:** `python package/tools/build_tables.py --check` exited 1. The package's `tables.csv` shipped 353 rows against 361 in the record, and 9 differ: this chain's eight new tables (`eia_world_coal_annual`, `eia_world_energy_co2_annual`, `ornl_npd_potential`, `lbnl_solar_projects`, `lbnl_hybrid_ppa_prices`, `ornl_eha_hydropower_units`, `lbnl_wind_capacity_factors`, `ercot_node_wires_utilities`) and `impact_tax_rules`, whose reason no longer counts the Texas Comptroller among the publishers not settled (session 942's verdict); it stays unsettled. The site's two files differed with it.
- **Rebuilt:** `build_tables.py` wrote 361 tables (public 258, internal 54, unsettled 49); `--check` then exits 0.
- **The tests of sessions 1001, 1008 and 1009 pass** against the rebuilt files (22 tests).

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`, `site/data/table_verdicts.json`, `site/data/table_citations.json`.
