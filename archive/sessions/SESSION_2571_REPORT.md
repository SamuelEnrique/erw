# Session 2571 report: the package's and the site's records

25 October 2026, about 01:33 to 01:35 UTC, on lab-desktop (the data machine), chain 126, unattended (after session 2572, so that every table of the chain was in). Precheck passed (`runs/c126/pre2571.out`, run at 01:25, before session 2572). Model spend USD 0. Pulls: none.

## Read these first

- **The license record** (`scripts/licenses.py tables --headers` main's output, `write`, `check`): 564 tables, 194 publishers with a verdict, 1,090 requests in the record; 0 problems.
- **`release_v1.py --check`:** passed (0 differences; the chain's three public tables' rows are in the package).
- **`package/tools/build_tables.py --check`** found the package's `tables.csv` stale by this chain's seven tables (`eec_eswatini_electricity_annual`, `arse_burkina_electricity_annual`, `nbs_maldives_electricity`, `abs_suriname_electricity_annual`, `bcrp_peru_electricity_monthly`, `bcrp_peru_hydrocarbons_monthly`, `vmme_paraguay_electricity_annual`) and the site's two files with it. Rebuilt (564 tables: public 415, internal 99, unsettled 50); the check then passed.
- **Tests** 1001, 1008, 1009, 378, 205 and the chain's own (2560 to 2563, 2566, 2567, 2572): 62 passed.
- **One dash in a rebuilt file was already on main:** `site/data/table_citations.json` holds a news outlet's own name as its feed gives it ("IEA" and an en dash before "International Energy Agency"), main's copy too. Left as it is; it comes from `news_stories`' `source` column.

## Decisions made without you

- **Run after session 2572,** whose source added a table.

## For Samuel's ruling

- None.

## Files

- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`; this report.
- On the data machine only: `runs/c126/pre2571.out`, `lic2571.out`, `rel2571.out`, `bt2571*.out`, `t2571.out`.
