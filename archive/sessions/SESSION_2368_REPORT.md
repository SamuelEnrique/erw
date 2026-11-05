# Session 2368 report: the package's and the site's records

24 October 2026, from 09:37 UTC, on lab-desktop (the data machine), a session of `queue/done/110-day-12-november-data-pakistan-bangladesh-morocco-kazakhstan.md`. Model spend USD 0. Pulls: none.

## Read these first

- **`package/tools/build_tables.py --check` found the records stale:** 505 rows shipped against 509 in the record. The four that differed are this chain's tables: `eurostat_oil_monthly`, `eurostat_solid_fuels_monthly`, `makstat_macedonia_electricity_monthly` and `statbank_moldova_electricity_monthly`. The site's two files differed with them.
- **Rebuilt:**
  - `package/src/erw/data/tables.csv` (509 tables: public 386, internal 73, unsettled 50);
  - `site/data/table_citations.json` (3 lines added) and `site/data/table_verdicts.json` (12 added).

  The check then shows 0 differences, and the site's two files agree.
- **The tests of sessions 1001, 1008 and 1009 pass** (22 tests).

## Errors

- None.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`.
- On the data machine only: `runs/c110/s2368/`.
