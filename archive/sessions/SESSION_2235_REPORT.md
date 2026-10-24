# Session 2235 report: the package's and the site's records

24 October 2026, from 03:15 UTC, on lab-desktop (the data machine), chain 099, unattended. Run after the merge of origin/main (chain 098), while session 2233's upload held the data lock; this session writes nothing to the warehouse. Model spend USD 0. Pulls: none.

## Read these first

- **The records were rebuilt at the merge** (`b1733474`): `python package/tools/build_tables.py` wrote `package/src/erw/data/tables.csv` with 457 tables (public 346, internal 61, unsettled 50), and `site/data/table_verdicts.json` and `site/data/table_citations.json` with it. This chain's seven tables are among them.
- **`python package/tools/build_tables.py --check`:** 457 rows shipped, 457 in the record, 0 differ; the site's two files agree (exit 0).
- **The tests of sessions 1001, 1008 and 1009** pass, run with the license tests after the merge.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report. The records changed at the merge (in its commit).
