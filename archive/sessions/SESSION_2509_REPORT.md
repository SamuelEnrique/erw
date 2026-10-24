# Session 2509 report: the licenses' forty-third round (CYSTAT may be public; Vanuatu's URA needs written permission)

24 October 2026, about 17:52 UTC, on lab-desktop (the data machine), chain 122, unattended. Precheck passed (`runs/c122/pre2509.out`). Model spend USD 0. Pulls: 3 requests of 20.

## Read these first

- **`license_verdicts.csv` was read first.** This chain's sessions 2504 to 2507 had already written one verdict: NCSI (Oman), may be public under the Open Government Licence of the Sultanate of Oman (session 2504, read 873).
- **Two verdicts,** each sentence cut by code from the page as it was saved (`runs/c122/s2509/verdicts.py`):
  - **Statistical Service of Cyprus (CYSTAT)** (read 905, the Data Reusability page): "According to the Dissemination Policy of the Statistical Service of Cyprus (CYSTAT), statistical data, metadata and all other statistical information are provided on CYSTAT's web portal free of charge, as a high-quality public good, irrespective of subsequent commercial or non-commercial use, provided that the source is acknowledged when republishing." **May be public,** sold or not. Microdata, tailor-made data and third parties' material are excluded. The ERW holds no CYSTAT table (session 2505).
  - **Utilities Regulatory Authority, Vanuatu (URA)** (read 906, the copyright statement): personal and non-commercial use only; "You may not, except with our express written permission, distribute or commercially exploit the content." **Needs written permission.** The ERW holds no URA table.
- **Not given a verdict:**
  - **Guyana Power and Light:** its terms and conditions (read 907) are its online account's and say nothing on reuse.
  - **Kuwait's ministry** (its TLS handshake fails) and **Central Statistical Bureau** (Arabic pages, no terms read); **Guyana's Bureau of Statistics** (its robots file bars Claude agents by name, so nothing more is asked); **the Guyana Energy Agency, LEC, LEWA, TSO Cyprus, the Tonga Statistics Department:** no terms page read, and the ERW holds no table of theirs.
- **The record:** 544 tables, 168 publishers with a verdict, 905 requests, 0 problems. Tests 205, 207, 887 and 888 pass.
- Sessions 2510 and 2511 come after this one; their publishers' verdicts are written in their own sessions.

## Requests (3 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | CYSTAT's Data Reusability page | 200 |
| 2 | URA's copyright statement | 200 |
| 3 | GPL's terms and conditions | 200: the online account's terms |

Reads recorded: 905 to 907 (on this branch).

## Decisions made without you

- **CYSTAT read as may be public** for its own statistics, the exclusions noted.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/metadata/license_verdicts.csv` (two rows), `warehouse/metadata/license_reads.csv` (reads 905 to 907), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c122/s2509/`.
