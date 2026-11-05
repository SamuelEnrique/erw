# Session 2501 report: the package's and the site's records, rebuilt for this chain's seven tables

24 October 2026, about 16:52 UTC, on lab-desktop (the data machine), chain 121, unattended. Precheck passed (`runs/c121/pre2501.out`). Model spend USD 0. Pulls: none.

## Read these first

- **`python package/tools/build_tables.py --check` found the records stale:** 537 rows shipped against 544 in the record. The 7 that differed were this chain's tables, and the site's two files differed with them.
- **Rebuilt:** `package/src/erw/data/tables.csv`, `site/data/table_citations.json` and `site/data/table_verdicts.json`, now 544 tables (public 407, internal 87, unsettled 50). The check then passed: 0 differ, the site's two files agree.
- **This chain's tables in them:** `fbos_fiji_electricity_annual` and `hagstova_faroe_electricity_annual` public; the other five internal (`slu_cso_electricity_annual` under both its publishers, the CSO and LUCELEC).
- **The tests of sessions 1001, 1008, 1009 and 378 pass.** Test 378 finds no table held internal whose verdicts allow it public.
- **On main these records count 537 tables;** chains 118, 119 and 120, unlanded, add theirs when they land, and the second to land rebuilds.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`. New: this report.
- On the data machine only: `runs/c121/s2501_*.out`.
