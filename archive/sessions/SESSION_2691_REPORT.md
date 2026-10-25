# Session 2691 report: the licenses' fifty-sixth round (the IHSI needs written permission)

25 October 2026, about 12:55 to 12:58 UTC, on lab-desktop (the data machine), chain 135, unattended. Precheck passed (`runs/c135/pre2691.out`). Model spend USD 0. Pulls: none of 20.

## Read these first

- **`license_verdicts.csv` was read first.** This chain has taken no table so far. This round takes the publishers it met whose pages were already saved; sessions 2692 and 2693 run after it.
- **One verdict** (`runs/c135/s2691/verdicts.py`), its line cut by code from a page saved in session 2689:
  - **The IHSI, Haiti** (read 1416, its home page): "IHSI (c) Copyright 2026. Tous droits reserves." (with its accents in the record). **Needs written permission** (ZIMSTAT's precedent).
  - Read 1416's outcome was set to exactly `read` (session 2593's form); its earlier note is kept in the verdict's note.
  - The script's first run stopped at a misspelt end word, after setting the outcome and before writing the row. It was set right and run again; the verdict is in the file once.
- **Not given a verdict:**
  - The OC, the CNE and the SIE (the Dominican Republic): the OC's files are closed by its robots file, and the other two refused the reader.
  - Ukrenergo and Ukrstat: a challenge, and a certificate failure; stat.gov.ua: only its robots file was read.
  - GECOL and Libya's statistics bureau: no answer, and no terms read.
  - EDH: the name does not resolve.
- **The record:** 586 tables, 242 publishers with a verdict, 1,415 requests, 0 problems. Tests 152, 205, 207 and 378 pass.

## Decisions made without you

- **No request this round:** the page was already saved.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/metadata/license_reads.csv` (one outcome), `warehouse/metadata/license_verdicts.csv` (one row), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c135/s2691/`.
