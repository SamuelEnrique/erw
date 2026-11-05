# Session 2096 report: the package's and the site's records

23 October 2026, from 22:31 UTC, on lab-desktop (the data machine), the thirteenth session of `queue/done/068-day-26-october-data-mexico-renewables-loans-credits-pipelines.md`, on chain 068's branch after its merge with chain 066's landing. Model spend USD 0. Pulls: none.

## Read these first

- **Stale, as after every data chain:** `python package/tools/build_tables.py --check` exited 1. The package's `tables.csv` shipped 409 rows against 413 in the record, and 5 differ: this chain's four tables (`eia_state_to_state_capacity`, `irena_capacity_annual`, `irs_soi_energy_credits_annual`, `noaa_cpc_oni_monthly`) and chain 066's `usdm_drought_state_weekly`, whose verdict session 2089 recorded (the Drought Monitor's Permission page); the site's two files differed with it.
- **Rebuilt:** `build_tables.py` wrote 413 tables (public 305, internal 58, unsettled 50); `--check` then exits 0.
- **The tests of sessions 1001, 1008 and 1009 pass** against the rebuilt files (22 tests).

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`, `site/data/table_verdicts.json`, `site/data/table_citations.json`.
