# Session 2775 report: the package's and the site's records

26 October 2026, about 00:39 to 00:41 UTC, on lab-desktop (the data machine), chain 140, unattended. It ran after session 2776, so that every table of the chain was in. Precheck passed (`runs/c140/pre2775.out`). Model spend USD 0. Pulls: none.

## Read these first

- **The license record** (`scripts/licenses.py tables --headers` with main's output folder, then `write` and `check`): 608 tables, 257 publishers with a verdict, 1,563 requests in the record; 0 problems. Nothing changed: the chain's sessions had written it.
- **`release_v1.py --check`:** passed (0 differences).
- **`package/tools/build_tables.py --check`** found the package's `tables.csv` stale by this chain's five tables: `statat_austria_electricity_annual`, `ine_es_dwellings_electricity_2021`, `statbel_be_electricity_production_annual`, `statec_lu_electricity_generation_annual` and `statec_lu_electricity_trade_annual`. It was rebuilt (608 tables: public 446, internal 112, unsettled 50), with the site's two files, and the check then passed.
- **Tests** 1001, 1008, 1009, 378, 205, 152, 2718 and the chain's own (2764, 2765, 2770, 2771, 2776) passed (78 tests).

## Decisions made without you

- **Run after session 2776,** whose source added a table (Luxembourg's trade).

## For Samuel's ruling

- None.

## Files

- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`; this report.
- On the data machine only: `runs/c140/pre2775.out`, `lic2775*.out`, `rel2775.out`, `bt2775*.out`, `t2775.out`.
