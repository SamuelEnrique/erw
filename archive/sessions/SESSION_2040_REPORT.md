# Session 2040 report: the package's and the site's records

23 October 2026, from 20:11 UTC, on lab-desktop (the data machine), the thirteenth session of `queue/done/058-day-24-october-data-outages-fuels-mines-vehicles.md`, on chain 058's branch. Model spend USD 0. Pulls: none.

## Read these first

- **Stale, as after every data chain:** `python package/tools/build_tables.py --check` exited 1. The package's `tables.csv` shipped 385 rows (chain 056's, rebuilt by its session 2012) against 393 in the record; the 8 that differ are this chain's new tables (`afdc_vehicle_registrations_annual`, `doe_oe417_events`, `eia_biofuel_plants`, `epa_rfs_fuel_annual`, `epa_rfs_rins_monthly`, `fhwa_motor_fuel_monthly`, `msha_coal_mines`, `msha_coal_production_quarterly`); the site's two files differed with it.
- **Rebuilt:** `build_tables.py` wrote 393 tables (public 288, internal 55, unsettled 50); `--check` then exits 0.
- **The tests of sessions 1001, 1008 and 1009 pass** against the rebuilt files.
- Chains 057 and 059's tables are not in this branch; the landing's merge of origin/main brings chain 059's, and the records are rebuilt then if the check says so.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`, `site/data/table_verdicts.json`, `site/data/table_citations.json`.
