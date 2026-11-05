# Session 2697 report: the package's and the site's records

25 October 2026, about 13:36 to 13:38 UTC, on lab-desktop (the data machine), chain 135, unattended. It ran after session 2698, so that every table of the chain was in. Precheck passed (`runs/c135/pre2697.out`). Model spend USD 0. Pulls: none.

## Read these first

- **The license record** (`scripts/licenses.py tables --headers` with main's output folder, then `write` and `check`): 589 tables, 242 publishers with a verdict, 1,422 requests in the record; 0 problems. Nothing changed: the chain's sessions had written it.
- **`release_v1.py --check`:** passed (0 differences).
- **`package/tools/build_tables.py --check`** found the package's `tables.csv` stale by this chain's three tables, `desnz_regional_renewable_capacity_annual`, `desnz_gb_regional_consumption_annual` and `desnz_gb_regional_gas_consumption_annual`. It was rebuilt (589 tables: public 428, internal 111, unsettled 50), with the site's two files, and the check then passed.
- **Tests** 1001, 1008, 1009, 378, 205, 152 and the chain's own (2692, 2693, 2698) passed (72 tests).

## Decisions made without you

- **Run after session 2698,** whose source added a table (Great Britain's gas by region).

## For Samuel's ruling

- None.

## Files

- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`; this report.
- On the data machine only: `runs/c135/pre2697.out`, `lic2697.out`, `rel2697.out`, `bt2697*.out`, `t2697.out`.
