# Session 2473 report: the package's and the site's records

24 October 2026, from 13:46 UTC, on lab-desktop (the data machine), a session of `queue/done/119-day-19-november-data-kyrgyzstan-cote-divoire-jamaica-laos.md`, run while session 2471's upload and note drafts were in progress. Precheck passed (`runs/c119/precheck_2473.out`). Model spend USD 0. Pulls: none.

## Read these first

- **`package/tools/build_tables.py --check` found the records stale:** 537 rows shipped against 541 in the record. The four that differed are this chain's tables: `nsc_kyrgyzstan_electricity_annual`, `anare_cotedivoire_electricity_annual`, `eurostat_gasoline_exports_monthly` and `eurostat_gas_exports_monthly`. The site's two files differed with them.
- **Rebuilt:**
  - `package/src/erw/data/tables.csv` (541 tables: public 408, internal 83, unsettled 50);
  - `site/data/table_citations.json` (3 lines added) and `site/data/table_verdicts.json` (12 added).

  The check then shows 0 differences, and the site's two files agree.
- **The tests of sessions 1001, 1008 and 1009 pass.**
- **At landing:** the records are rebuilt again if a merge of main brings tables.

## Errors

- None.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- Changed: `package/src/erw/data/tables.csv`, `site/data/table_citations.json`, `site/data/table_verdicts.json`.
- New: this report.
