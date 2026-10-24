# Session 2355 report: the package's and the site's records

24 October 2026, from 07:13 UTC, on lab-desktop (the data machine), a session of `queue/done/105-day-8-november-data-mexico-india-peru-korea.md`, there numbered 2305 (renumbered: session 2350's report). Model spend USD 0. Pulls: none.

## Read these first

- **`package/tools/build_tables.py --check` found the records stale.** It counted 486 rows shipped against 491 in the record, the five differing tables being this chain's: `cea_india_psp_annual`, `kpx_korea_generation_annual`, `kpx_korea_demand_monthly`, `statnett_norway_daily` and `svk_sweden_production_hourly`. The site's two files already agreed.
- **Rebuilt:** `package/src/erw/data/tables.csv` (491 tables: public 372, internal 69, unsettled 50). Only the five tables' rows are added. The check then shows 0 differences, and the site's two files agree (`site/data/table_citations.json` and `table_verdicts.json`, unchanged in content).
- **The tests of sessions 1001, 1008 and 1009 pass** (22 tests).

## Errors

- None.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`.
- On the data machine only: `runs/c105/s2355/`.
