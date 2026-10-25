# Session 2515 report: the package's and the site's records, rebuilt for this chain's three tables

24 October 2026, about 18:40 UTC, on lab-desktop (the data machine), chain 122, unattended. Precheck passed (`runs/c122/pre2515.out`). Model spend USD 0. Pulls: none.

## Read these first

- **`licenses.py tables`, `write` and `check`:** 547 tables, 169 publishers with a verdict, 927 requests, 0 problems. `release_v1.py --check`: 0 differences.
- **`python package/tools/build_tables.py --check` found the records stale:** 544 rows shipped against 547 in the record; the 3 that differed were this chain's tables, and the site's two files differed with them.
- **Rebuilt:** `package/src/erw/data/tables.csv`, `site/data/table_citations.json` and `site/data/table_verdicts.json`, now 547 tables (public 409, internal 88, unsettled 50). The check then passed.
- **This chain's tables in them:** `ncsi_oman_electricity_annual` and `nve_norway_reservoirs_weekly` public; `statgl_greenland_electricity_annual` internal.
- **The tests of sessions 1001, 1008, 1009 and 378 pass.**

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`. New: this report.
- On the data machine only: `runs/c122/s2515_*.out`.
