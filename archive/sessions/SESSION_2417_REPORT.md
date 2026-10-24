# Session 2417 report: the package's and the site's records rebuilt (526)

24 October 2026, from 11:11 UTC, on lab-desktop (the data machine), the twelfth session of `queue/done/114-day-15-november-data-paraguay-panama-guatemala-namibia.md`, unattended. It ran after session 2418 and the merge with main (session 2415), so that the records hold all of this chain's tables. Precheck passed (`runs/c114/pre2417.out`). Model spend USD 0. Pulls: none.

## Read these first

- **`package/tools/build_tables.py --check` exited 1 at first:** 519 rows shipped against 526 in the license record, with seven differing (this chain's seven tables) and the site's two files differing.
- **Rebuilt** (`package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`): 526 tables, public 395, internal 81, unsettled 50. `--check` now exits 0.
- **This chain's seven tables in the record:**
  - `sne_panama_electricity_annual`, `sne_panama_generation_monthly`, `amm_guatemala_generation_monthly` and `statsmu_mauritius_electricity_annual`: internal (the Secretaria's and Statistics Mauritius's verdicts await your ruling; AMM states no terms);
  - `eia_net_imports_monthly`, `eurostat_electricity_production_annual` and `statcan_generating_capacity_annual`: public.
- **Tests of sessions 1001, 1008 and 1009:** 22 tests, all pass.
- The landing (session 2419) rebuilds the records again if main has moved.

## Errors

- None.

## Decisions made without you

- **Run after sessions 2418 and 2415's merge.**

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`.
