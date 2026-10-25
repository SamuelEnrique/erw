# Session 2663 report: the licenses' fifty-fourth round (INE Angola and IRSEA need written permission)

25 October 2026, about 10:23 to 10:25 UTC, on lab-desktop (the data machine), chain 133, unattended. Precheck passed (`runs/c133/pre2663.out`). Model spend USD 0. Pulls: none of 20.

## Read these first

- **`license_verdicts.csv` was read first.** Sessions 2659 and 2661 gave their own publishers' verdicts with their tables: the Agency on Statistics of Tajikistan (CC BY 4.0, may be public) and COSIT (needs written permission). This round takes the publishers session 2660 met, whose pages were already saved. Sessions 2664 and 2665 run after it.
- **Two verdicts** (`runs/c133/s2663/verdicts.py`), each line cut by code from a page session 2660 saved. Both **need written permission** (ZIMSTAT's precedent):
  - **INE, Angola** (read 1351, its home page): "Copyright 2021 - | Instituto Nacional de Estatistica | Todos os direitos reservados" (with its accent in the record).
  - **IRSEA, Angola's regulator** (read 1355, its publications page): "(c) 2026 IRSEA | Todos Direitos Reservados".
  - Both reads' outcomes were already exactly `read`.
- **Not given a verdict:**
  - Belstat: its main site did not answer, and its data portal shows no terms.
  - PRODEL: its site is drawn by script, and only its robots address was asked.
- **The record:** 580 tables, 235 publishers with a verdict, 1,359 requests, 0 problems. Tests 152, 205, 207 and 378 pass.

## Decisions made without you

- **No request this round:** the two pages were already saved.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/metadata/license_verdicts.csv` (two rows), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c133/s2663/`.
