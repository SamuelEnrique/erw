# Session 2146 report: the package's and the site's records

24 October 2026, from 00:43 UTC, on lab-desktop (the data machine), chain 090, unattended. Run after the merge of origin/main (chains 069 and 079), while session 2144's upload held the data lock; this session writes nothing to the warehouse. Model spend USD 0. Pulls: none.

## Read these first

- **`python package/tools/build_tables.py --check` failed first**, as it should after this chain's tables and verdicts: 428 rows shipped against 434 in the record, 7 differing. Those are this chain's six tables, and `irena_capacity_annual`, whose verdict session 2139 recorded.
- **Rebuilt:** `package/src/erw/data/tables.csv` now has 434 tables (public 325, internal 59, unsettled 50); `site/data/table_verdicts.json` and `site/data/table_citations.json` were rebuilt with it. `--check` then exits 0.
- **The tests of sessions 1001, 1008 and 1009:** 22, all pass.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`, `site/data/table_verdicts.json`, `site/data/table_citations.json`.
- On the data machine only: `runs/c090/s2146_*`.
