# Session 2431 report: the package's and the site's records

24 October 2026, from 11:43 UTC, on lab-desktop (the data machine), a session of `queue/done/115-day-16-november-data-zambia-botswana-mongolia-cambodia.md`, run while session 2429's two note drafts were being written. Precheck passed (`runs/c115/precheck_2431.out`). Model spend USD 0. Pulls: none.

## Read these first

- **`package/tools/build_tables.py --check` found the records stale:** 519 rows shipped against 525 in the record. The six that differed are this chain's tables: `erb_zambia_electricity_annual`, `statsbots_botswana_electricity_monthly`, `erc_mongolia_electricity_annual`, `esco_georgia_electricity_monthly`, `eurostat_hard_coal_imports_annual` and `eurostat_crude_imports_by_field_monthly`. The site's two files differed with them.
- **Rebuilt:**
  - `package/src/erw/data/tables.csv` (525 tables: public 395, internal 80, unsettled 50);
  - `site/data/table_citations.json` (3 lines added) and `site/data/table_verdicts.json` (12 added).

  The check then shows 0 differences, and the site's two files agree.
- **The tests of sessions 1001, 1008 and 1009 pass** (22 tests).
- **At landing:** the records are rebuilt again if a merge of main brings tables (chain 114's).

## Errors

- None.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`.
- New: this report.
