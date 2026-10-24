# Session 2390 report: the licenses' thirty-fifth round (ERA, ICE and CNDC need written permission)

24 October 2026, from 09:24 UTC to 09:26 UTC, on lab-desktop (the data machine), chain 113, unattended. Model spend USD 0. Pulls: none of 20.

## Read these first

- **Three verdicts, each from a read this chain's source sessions recorded**, every one **needs written permission**, sold or not:
  - **ERA (Uganda)** (read 637): "Electricity Regulatory Authority authorizes to view and download the information ("Materials") at this Web site ("Site") only for personal, non-commercial use." The same disclaimer bars reproducing or distributing the materials "for any public or commercial purpose".
  - **CENCE, ICE (Costa Rica)** (read 640): "Declaración de Privacidad © 2025 ICE Todos los Derechos Reservados.", the line that ends every answer of CENCE's web services. All rights reserved and no reuse granted, read as POWER Magazine's notice was (read 29). `cence_costarica_generation_monthly` stays internal.
  - **CNDC (Bolivia)** (read 642): "© 2026 CNDC, Comité Nacional de Despacho de Carga de Bolivia. Todos los derechos reservados." The page's dash after CNDC is written as a comma here: the repository writes no dash of that kind.
- **Reads 640 and 642 now have the outcome exactly `read`,** as test 205 requires of a verdict's read. Their details moved to the verdicts' notes.
- **Not given a verdict:** EWURA (Tanzania), whose terms were not found and from which no data was taken.
- **The record:** `licenses.py tables`, `write` and `check`: 506 tables, 143 publishers with a verdict, 0 problems. `tests.test_session205`, `207` and `887` pass; test 205's bound raised by 40 (564 later reads against 562 before it).

## Decisions made without you

- **"All rights reserved" with no reuse granted read as needs written permission,** as the record's earlier verdict for POWER Magazine reads it.

## For Samuel's ruling

- **The consent of ERA, ICE and CNDC,** if Uganda's, Costa Rica's (public) and Bolivia's data are wanted.

## Files

- Changed: `warehouse/metadata/license_verdicts.csv` (three rows), `warehouse/metadata/license_reads.csv` (two outcomes), `tests/test_session205.py`, the license record. New: this report.
