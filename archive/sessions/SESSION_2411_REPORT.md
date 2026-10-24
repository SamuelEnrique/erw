# Session 2411 report: the licenses' thirty-sixth round

24 October 2026, from 10:39 UTC, on lab-desktop (the data machine), the sixth session of `queue/done/114-day-15-november-data-paraguay-panama-guatemala-namibia.md`, unattended, beside session 2410's notes (drafted by a helper). Precheck passed (`runs/c114/pre2411.out`). Model spend USD 0. Pulls: none.

## Read these first

- **Sessions 2406 to 2409's publishers were read in their own sessions** (reads 703 to 746 on this branch's numbering):
  - **ANDE, Paraguay:** a browser challenge; not read (read 704).
  - **Paraguay's open data portal:** under maintenance (read 707).
  - **CND, Panama:** its figures load only through its private site's key, which was not used (reads 708 to 713).
  - **The Secretaria Nacional de Energia, Panama:** a new verdict, may be public (read 716).
  - **AMM, Guatemala:** no terms stated, so its table is internal and has no verdict (reads 719 to 723).
  - **NamPower, Namibia:** a new verdict, needs written permission (read 734).
  - **The Electricity Control Board, Namibia, and Honduras's ODS:** their certificates do not verify, and TLS was not bypassed (reads 736 and 738).
  - **El Salvador's UT:** HTTP 403 (read 737).
  - **Statistics Mauritius:** a new verdict, may be public (read 741).
- **Sessions 2412 and 2413's publishers** are read in those sessions, before their pulls.
- **The other publishers without a verdict** were not asked again (session 2125's reasons).
- **One fix:** the Secretaria's verdict key carried "(SNE)", which the source registry's publisher name does not, so its two tables showed as "not read". The key is now the registry's name, and both tables carry the verdict.
- **The record:** 514 tables, 145 publishers with a verdict, 677 requests on this branch. The license check finds no problem.
- **Three tables are flagged internal where the sentence read allows them:** `sne_panama_electricity_annual`, `sne_panama_generation_monthly` and `statsmu_mauritius_electricity_annual`. They stay internal until your ruling (sessions 2407 and 2409).

## Errors

- **The Secretaria's verdict key did not match its publisher name** (session 2407). Fixed here.

## Decisions made without you

- **No request in this round,** since every publisher this chain has met was read in its own session.

## For Samuel's ruling

- None new beyond sessions 2407, 2408 and 2409's:
  - the Secretaria's and Statistics Mauritius's figures: public or internal;
  - AMM's terms;
  - NamPower's consent.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_verdicts.csv` (the Secretaria's key), `license_tables.csv`, `docs/licenses.md`.
