# Session 2719 report: the package's and the site's records

25 October 2026, about 18:47 to 18:49 UTC, on lab-desktop (the data machine), chain 136, unattended. It ran after session 2720, so that every table of the chain was in. Precheck passed (`runs/c136/pre2719.out`). Model spend USD 0. Pulls: none.

## Read these first

- **The license record** (`scripts/licenses.py tables --headers` with main's output folder, then `write` and `check`): 593 tables, 245 publishers with a verdict, 1,447 requests in the record; 0 problems. Nothing changed: the chain's sessions had written it.
- **`release_v1.py --check`:** passed (0 differences).
- **`package/tools/build_tables.py --check`** found the package's `tables.csv` stale by this chain's four tables: `nspower_ns_load_hourly`, `desnz_uk_power_stations`, `desnz_uk_interconnector_flows_annual` and `desnz_uk_storage_annual`. It was rebuilt (593 tables: public 431, internal 112, unsettled 50), with the site's two files, and the check then passed.
- **Tests** 1001, 1008, 1009, 378, 205, 152 and the chain's own (2708, 2714, 2715, 2718, 2720) passed (83 tests).

## Decisions made without you

- **Run after session 2720,** whose source added a table (the UK's storage).

## For Samuel's ruling

- None.

## Files

- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`; this report.
- On the data machine only: `runs/c136/pre2719.out`, `lic2719.out`, `rel2719.out`, `bt2719*.out`, `t2719.out`.
