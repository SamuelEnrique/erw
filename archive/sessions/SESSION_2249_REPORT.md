# Session 2249 report: the package's and the site's records

24 October 2026, from 03:49 UTC, on lab-desktop (the data machine), the twelfth session of `queue/done/101-day-4-november-data-france-spain-brazil-australia.md`, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **The records were stale by six tables:** chain 098's `usbr_crsp_reservoirs_daily` (written after its merge) and this chain's five. `package/tools/build_tables.py --check` found 449 shipped against 455 in the record (exit 1).
- **Rebuilt:** `package/src/erw/data/tables.csv` now holds 455 tables (public 344, internal 61, unsettled 50). `site/data/table_citations.json` and `table_verdicts.json` were rebuilt with it.
- **`--check` again:** 455 shipped, 455 in the record, 0 differ; the site's two files agree (exit 0). The tests of sessions 1001, 1008 and 1009 pass.
- The landing's merge with main rebuilds them once more with chain 097's tables.

## Errors

- None.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`.
