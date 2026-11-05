# Session 2789 report: the package's and the site's records

26 October 2026, about 02:23 UTC, on lab-desktop (the data machine), chain 141, unattended. It ran after session 2790, so that every table of the chain was in. Precheck passed (`runs/c141/pre2789.out`). Model spend USD 0. Pulls: none.

## Read these first

- **The license record** (`scripts/licenses.py tables --headers` with main's output folder, then `write` and `check`): 611 tables, 257 publishers with a verdict, 1,585 requests in the record; 0 problems. Nothing changed: the chain's sessions had written it.
- **`release_v1.py --check`:** passed (0 differences).
- **`package/tools/build_tables.py --check`** found the package's `tables.csv` stale by this chain's three tables: `statec_lu_power_capacity_annual`, `statec_lu_supplier_mix_annual` and `eurostat_import_dependency_annual`. It was rebuilt (611 tables: public 449, internal 112, unsettled 50), with the site's two files, and the check then passed.
- **Tests** 1001, 1008, 1009, 378, 205, 152, 2718, 444 (fixed in session 2777) and the chain's own (2784, 2785, 2790) passed (77 tests, 1 skipped).

## Decisions made without you

- **Run after session 2790,** whose source added a table (the import dependency).

## For Samuel's ruling

- None.

## Files

- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`; this report.
- On the data machine only: `runs/c141/pre2789.out`, `lic2789*.out`, `rel2789.out`, `bt2789*.out`, `t2789.out`.
