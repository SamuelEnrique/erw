# Session 2593 report: the licenses' forty-ninth round (INSTAT Mali's open data licence: may be public; SOMELEC and ARE in Mauritania need written permission)

25 October 2026, about 03:45 to 03:46 UTC, on lab-desktop (the data machine), chain 128, unattended. Precheck passed (`runs/c128/pre2593.out`). Model spend USD 0. Pulls: none of 20.

## Read these first

- **`license_verdicts.csv` was read first.** This chain's one table so far (Curacao) has CBS's verdict (session 2591); this round takes the publishers the chain met with no verdict, from pages already saved.
- **Three verdicts,** each sentence cut by code from the page as saved (`runs/c128/s2593/verdicts.py`):
  - **SOMELEC, Mauritania** (read 1144, its home page): "Tous Droits Reserves (c) 2026" (with its accents in the record). **Needs written permission** (ZIMSTAT's precedent).
  - **ARE, Mauritania** (read 1146, its electricity observatory page): "Copyright (c) 2023 ARE - Tous droits reserves." **Needs written permission.**
  - **INSTAT, Mali** (read 1151, its Accord de licence de donnees ouvertes, a PDF saved under a `.bin` name, its text read with pdfplumber): "L'INSTAT vous accorde ... une licence mondiale, gratuite et non exclusive ... a des fins commerciales et non commerciales, sous reserve des conditions de la presente licence." **May be public,** with the attribution it words; it does not extend to third parties' data, as its yearbook's energy table (EDM's figures) is.
  - The ERW holds no table of any of them.
- **The verdicts' reads now have the outcome exactly `read`** (test 205). Their earlier notes: read 1144 "Tous Droits Reserves (c) 2026; no report or figure linked"; 1146 "empty; Copyright (c) 2023 ARE - Tous droits reserves".
- **Not given a verdict:** ANSADE (its site drawn by script, no terms in its bytes), EDM SA and CREE (their hosts do not resolve), NSO PNG, PNG Power and the National Energy Authority (no terms page read; the ERW holds no table of theirs), Aqualectra (its certificate fails).
- **The record:** 567 tables, 204 publishers with a verdict, 1,160 requests, 0 problems. Tests 152, 205, 207 and 378 pass.

## Decisions made without you

- **No request this round:** the publishers' pages were already saved.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/metadata/license_verdicts.csv` (three rows), `warehouse/metadata/license_reads.csv` (two outcomes), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c128/s2593/`.
