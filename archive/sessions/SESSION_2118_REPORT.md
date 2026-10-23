# Session 2118 report: the package's and the site's records

23 October 2026, from 23:04 UTC, on lab-desktop (the data machine), a session of `queue/done/069-day-27-october-data-public-lands-sunlight-spending-streams.md`. Model spend USD 0. Pulls: none.

## Read these first

- **Stale, as after every data chain:** `python package/tools/build_tables.py --check` exited 1. The package's `tables.csv` shipped 413 rows against 419 in the record, and the 6 that differ are this chain's new tables (`blm_oil_gas_statistics_annual`, `cec_total_system_generation_annual`, `eia_seds_residential_annual`, `noaa_uscrn_solar_monthly`, `treasury_1603_awards`, `usgs_streamflow_daily`); the site's two files differed with it.
- **Rebuilt:** 419 tables (public 310, internal 58, unsettled 51); `--check` then exits 0. `treasury_1603_awards` is internal there: "the ERW holds it for its own use only (not settled ...)", as session 2116 set it.
- **The tests of sessions 1001, 1008 and 1009 pass** against the rebuilt files.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`, this report.
