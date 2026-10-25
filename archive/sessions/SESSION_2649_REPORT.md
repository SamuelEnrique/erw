# Session 2649 report: the licenses' fifty-third round (EPPSO and INE Sao Tome need written permission)

25 October 2026, about 08:48 to 08:51 UTC, on lab-desktop (the data machine), chain 132, unattended. Precheck passed (`runs/c132/pre2649.out`). Model spend USD 0. Pulls: none of 20.

## Read these first

- **`license_verdicts.csv` was read first.** This chain has taken no table. This round takes the publishers it met whose pages were already saved; sessions 2650 and 2651 run after it.
- **Two verdicts** (`runs/c132/s2649/verdicts.py`), each line cut by code from a page saved earlier in this chain; both **need written permission** (ZIMSTAT's precedent):
  - **EPPSO, the Marshall Islands** (read 1300): "Copyright © 2023 | RMI Economic Policy, Planning and Statistics Office | All Rights Reserved".
  - **INE, Sao Tome and Principe** (read 1308): "Copyright © 2018 Instituto Nacional de Estatisticas da Republica Democratica de Sao Tome e Principe" (with its accents in the record).
  - Reads 1300 and 1308 had their outcomes set to exactly `read` (session 2593's form); their earlier notes were "read: its publications listed by a script plugin (placeholder links); a copyright line" and "read: its themes and documents; a copyright line".
  - The script's first run stopped at INE's "Principe" (written with its accent), after setting the two outcomes and before writing a row. It was set right and run again; each verdict is in the file once.
- **Not given a verdict:**
  - PUC Pohnpei: its robots file closes every path, and its page was asked in error (session 2645); nothing is taken from it.
  - INE Guinea-Bissau: its site answered 503.
  - FSM Statistics: it does not answer.
  - MEC: its certificate fails.
- **The record:** 576 tables, 229 publishers with a verdict, 1,310 requests, 0 problems. Tests 152, 205, 207 and 378 pass.

## Decisions made without you

- **No request this round:** the two pages were already saved.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/metadata/license_reads.csv` (two outcomes), `warehouse/metadata/license_verdicts.csv` (two rows), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c132/s2649/`.
