# Session 2012 report: the package's and the site's records

23 October 2026, from 17:03 UTC, on lab-desktop (the data machine), a session of `queue/done/056-evening-23-october-data-jobs-reactors-large-loads-hydro.md`, on chain 056's branch after chain 055's was merged into it. Model spend USD 0. Pulls: none.

## Read these first

- **Stale, as after every data chain:** `python package/tools/build_tables.py --check` exited 1. The package's `tables.csv` shipped 379 rows (chain 055's, rebuilt by its session 990) against 385 in the record, and the 6 that differ are this chain's new tables (`boem_offshore_platforms`, `doe_useer_employment`, `noaa_cpc_degree_days_daily`, `nrc_advanced_reactor_preapplicants`, `nrc_new_reactor_applications`, `usbr_hydropower_monthly`); the site's two files differed with it.
- **Rebuilt:** `build_tables.py` wrote 385 tables (public 280, internal 55, unsettled 50); `--check` then exits 0.
- **The tests of sessions 1001, 1008 and 1009 pass** against the rebuilt files (22 tests).

## Decisions made without you

- **Run before session 2010's upload,** while chain 055's landing ran its checks; the records read the license record, not Redivis.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`, `site/data/table_verdicts.json`, `site/data/table_citations.json`.
