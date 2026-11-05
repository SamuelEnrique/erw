# Session 2220 report: the package's and the site's records

24 October 2026, from 02:06 UTC, on lab-desktop (the data machine), the eleventh session of `queue/done/098-day-2-november-data-price-indexes-reservoirs-rooftops.md`, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **The records were rebuilt at session 2218's merge** (`package/tools/build_tables.py`, commits 25864715 and fd2029ef), with chain 098's three tables and verdicts and chain 090's. `package/src/erw/data/tables.csv` holds 449 tables: public 338, internal 61, unsettled 50. `site/data/table_citations.json` and `table_verdicts.json` were rebuilt with it.
- **`build_tables.py --check`:** 449 rows shipped, 449 in the record, 0 differ; the site's two files agree (exit 0).
- **The tests of sessions 1001, 1008 and 1009:** 22 tests, all pass.
- Session 2221's table, when written, joins the records at the landing's rebuild.

## Errors

- None.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report. On the data machine only: `runs/c098/s2220_*`.
