# Session 990 report: the package's and the site's records

23 October 2026, from 16:44 UTC, on lab-desktop (the data machine), a session of `queue/done/055-afternoon-23-october-data-outlook-hybrids-loans-dams.md`, run by the second agent. Model spend USD 0. Pulls: none.

## Read these first

- **Stale, as after every data chain:** `python package/tools/build_tables.py --check` exited 1. The package's `tables.csv` shipped 372 rows against 379 in the record, and the 7 that differ are this chain's new tables (`egrid_subregions_annual`, `eia_capacity_factors_annual`, `eia_capacity_factors_monthly`, `eia_heat_rates_annual`, `eia_ieo_projections`, `lbnl_hybrid_plants`, `usace_nid_dams`); the site's two files differed with it.
- **Rebuilt:** `build_tables.py` wrote 379 tables (public 274, internal 55, unsettled 50); `--check` then exits 0.
- **The tests of sessions 1001, 1008 and 1009 pass** against the rebuilt files (22 tests).

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`, `site/data/table_verdicts.json`, `site/data/table_citations.json`.
