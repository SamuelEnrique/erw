# Session 2487 report: the package's and the site's records, rebuilt for this chain's three tables

24 October 2026, about 13:48 UTC, on lab-desktop (the data machine), chain 120, unattended. Precheck passed (`runs/c120/pre2487.out`). Model spend USD 0. Pulls: none.

## Read these first

- **`python package/tools/build_tables.py --check` found the records stale:** 537 rows shipped against 540 in the record. The 3 that differed were this chain's `mireme_mozambique_electricity_annual`, `statcan_manufacturing_energy_annual` and `statcan_thermal_fuel_annual`, and the site's two files differed with them.
- **Rebuilt:** `package/src/erw/data/tables.csv`, `site/data/table_citations.json` and `site/data/table_verdicts.json`, now 540 tables (public 407, internal 83, unsettled 50). The check then passed: 0 differ, the site's two files agree.
- **This chain's three tables in them:** `mireme_mozambique_electricity_annual` internal; the two Statistics Canada tables public.
- **The tests of sessions 1001, 1008, 1009 and 378 pass.** Test 378 finds no table held internal whose verdicts allow it public.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`. New: this report.
- On the data machine only: `runs/c120/s2487_*.out`.
