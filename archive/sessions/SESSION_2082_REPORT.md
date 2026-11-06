# Session 2082 report: the package's and the site's records

23 October 2026, from 20:27 UTC, on lab-desktop (the data machine), the thirteenth session of `queue/done/067-day-25-october-data-neighbours-emitters-disasters-world-oil.md`. Model spend USD 0. Pulls: none.

## Read these first

- **Stale, as after every data chain:** `python package/tools/build_tables.py --check` exited 1. The package's `tables.csv` shipped 391 rows (chain 059's, as landed) against 395 in the record; the 4 that differ are this chain's new tables (`aeso_alberta_load_hourly`, `epa_ghgrp_facility_emissions`, `ieso_ontario_demand_hourly`, `noaa_ncei_billion_disasters`), and the site's two files differed with it.
- **Rebuilt:** `build_tables.py` wrote 395 tables (public 289, internal 56, unsettled 50); `--check` then exits 0.
- **The tests of sessions 1001, 1008 and 1009 pass** against the rebuilt files.
- **Chain 057's tables are not in this branch's record:** chain 057 landed after this branch was cut; the merge with main at this chain's landing brings them in, and the records are rebuilt then if the merge leaves them stale.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`, `site/data/table_verdicts.json`, `site/data/table_citations.json`.
- On the data machine only: `runs/c067/s2082*`.
