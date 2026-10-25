# Session 2627 report: the package's and the site's records

25 October 2026, about 07:10 to 07:13 UTC, on lab-desktop (the data machine), chain 130, unattended. It ran after session 2628, so that every table of the chain was in. Precheck passed (`runs/c130/pre2627.out`). Model spend USD 0. Pulls: none.

## Read these first

- **The license record** (`scripts/licenses.py tables --headers` with main's output folder, then `write` and `check`): 574 tables, 222 publishers with a verdict, 1,264 requests in the record; 0 problems.
- **`release_v1.py --check`:** passed (0 differences; Liechtenstein's public table was added to the package in session 2622).
- **`package/tools/build_tables.py --check`** found the package's `tables.csv` stale by this chain's two tables, `asli_liechtenstein_electricity_annual` and `nawec_gambia_electricity_monthly`. It was rebuilt (574 tables: public 417, internal 107, unsettled 50), with the site's two files, and the check then passed.
- **Tests** 1001, 1008, 1009, 378, 205 and the chain's own (2617, 2622) passed.

## Decisions made without you

- **Run after session 2628,** whose source might have added a table. It added none.

## For Samuel's ruling

- None.

## Files

- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`; this report.
- On the data machine only: `runs/c130/pre2627.out`, `lic2627.out`, `rel2627.out`, `bt2627*.out`, `t2627.out`.
