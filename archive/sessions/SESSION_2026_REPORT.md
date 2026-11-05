# Session 2026 report: the package's and the site's records

23 October 2026, from 19:14 UTC, on lab-desktop (the data machine), a session of `queue/done/057-night-23-october-data-wholesale-solar-industry-buildings.md`, run out of order while session 2024's upload was being proved (it writes nothing to the warehouse and needs no lock). Model spend USD 0. Pulls: none.

## Read these first

- **Stale, as after every data chain:** `python package/tools/build_tables.py --check` exited 1: the package's `tables.csv` shipped 385 rows (chain 056's) against 391 in the record, and the 6 that differ are this chain's new tables (`eia_ice_electricity_daily`, `lbnl_tracking_the_sun`, `eia_mecs_manufacturing`, `eia_cbecs_commercial_buildings`, `eia_recs_households`, `eia_lng_liquefaction_projects`); the site's two files differed with it.
- **Rebuilt:** `build_tables.py` wrote 391 tables (public 285, internal 56, unsettled 50); `--check` then exits 0. `eia_ice_electricity_daily` is among the internal ones.
- **The tests of sessions 1001, 1008 and 1009 pass** against the rebuilt files (22 tests).

## Decisions made without you

- **Run before session 2023's notes and session 2024's proof were done:** the records read the license record, not the notes or Redivis.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`, `site/data/table_verdicts.json`, `site/data/table_citations.json`.
- On the data machine only: `runs/c057/s2026/`.
