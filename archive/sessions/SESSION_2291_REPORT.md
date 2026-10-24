# Session 2291 report: the package's and the site's records

24 October 2026, from 05:35 UTC, on lab-desktop (the data machine), the twelfth session of `queue/done/104-day-7-november-data-portugal-italy-japan-argentina.md`, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **The records were stale by this chain's seven tables:** `package/tools/build_tables.py --check` found 470 shipped against 477 in the record (exit 1).
- **Rebuilt:** `package/src/erw/data/tables.csv` now holds 477 tables (public 364, internal 63, unsettled 50). The site's two record files were rebuilt with it.
- **`--check` again:** 0 differ (exit 0). The tests of sessions 1001, 1008 and 1009 pass.
- The landing's merge with main rebuilds them once more with chains 102's and 103's tables.

## Errors

- None.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`.
