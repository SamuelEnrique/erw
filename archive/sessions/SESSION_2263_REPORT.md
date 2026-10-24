# Session 2263 report: the package's and the site's records

24 October 2026, from 04:40 UTC, on lab-desktop (the data machine), a session of `queue/done/102-day-5-november-data-poland-belgium-new-zealand-columbia.md`, run while session 2261's draft upload ran. Model spend USD 0. Pulls: none.

## Read these first

- **`package/tools/build_tables.py --check` found the records stale:** 470 rows shipped against 475 in the record. The five that differed are this chain's tables (`pse_poland_balance_15min`, `energy_charts_belgium_hourly`, `emi_nz_generation_demand_monthly`, `census_c30_construction_monthly`, `energy_charts_southeast_europe_daily`), and the site's two files differed with them.
- **Rebuilt:** `package/src/erw/data/tables.csv` (475 tables: public 362, internal 63, unsettled 50), `site/data/table_citations.json` and `site/data/table_verdicts.json`. Only the five tables' rows are added (5, 4 and 16 lines). The check then shows 0 differences, and the site's two files agree.
- **The tests of sessions 1001, 1008 and 1009 pass** (22 tests).

## Errors

- None.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`.
