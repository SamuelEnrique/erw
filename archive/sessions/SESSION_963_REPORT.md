# Session 963 report: the package's and the site's records

23 October 2026, from 13:12 UTC, on lab-desktop (the data machine), a session of `queue/done/054-day-23-october-data-federal-royalties-wind-costs-minerals.md`. Model spend USD 0. Pulls: none.

## Read these first

- **Stale, as after every data chain:** `python package/tools/build_tables.py --check` exited 1. The package's `tables.csv` shipped 361 rows against 372 in the record, and the 11 that differ are this chain's new tables (`onrr_production_monthly`, `onrr_production_annual`, `onrr_revenue_monthly`, `lbnl_wind_costs`, `lbnl_wind_turbine_orders`, `eia_primary_energy_monthly`, `usgs_mcs_critical_minerals`, `blm_ca_renewable_rows`, `eia_coal_distribution_quarterly`, `eia_uranium_production_quarterly`, `eia_uranium_facilities`); the site's two files differed with it.
- **Rebuilt:** `build_tables.py` wrote 372 tables (public 269, internal 54, unsettled 49); `--check` then exits 0.
- **The tests of sessions 1001, 1008 and 1009 pass** against the rebuilt files (22 tests).

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`, `site/data/table_verdicts.json`, `site/data/table_citations.json`.
