# Session 2159 report: the package's and the site's records

24 October 2026, from 00:22 UTC, on lab-desktop (the data machine), a session of `queue/done/092-day-30-october-data-bpa-snowpack-access-outlook-permits.md`. Model spend USD 0. Pulls: none.

## Read these first

- **Stale, as after every data chain:** `python package/tools/build_tables.py --check` exited 1. The package's `tables.csv` shipped 423 rows against 429 in the record, and the 6 that differ are this chain's new tables (`afdc_ev_charging_state_annual`, `bpa_ba_hourly`, `census_bps_state_annual`, `nrcs_snotel_swe_daily`, `wb_electricity_access_annual`, `wb_iea_electricity_annual`); the site's two files differed with it.
- **Rebuilt:** 429 tables (public 318, internal 61, unsettled 50); `--check` then exits 0. `nrcs_snotel_swe_daily` and `wb_iea_electricity_annual` are among the internal ones, as sessions 2149 and 2150 set them.
- **The tests of sessions 1001, 1008 and 1009 pass** against the rebuilt files.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`, this report.
