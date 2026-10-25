# Session 2579 report: the licenses' forty-eighth round (the Ministry of Energy of Algeria, DGS and SEEG in Gabon, URCA in the Bahamas: each needs written permission)

25 October 2026, about 02:35 to 02:40 UTC, on lab-desktop (the data machine), chain 127, unattended. Precheck passed (`runs/c127/pre2579.out`). Model spend USD 0. Pulls: 2 requests of 20.

## Read these first

- **`license_verdicts.csv` was read first.** This chain's only table so far (Samoa) has SBS's verdict (session 2574); this round takes the publishers the chain met with no verdict.
- **Four verdicts,** each sentence cut by code from the page as saved (`runs/c127/s2579/verdicts.py`); each is a copyright line with no reuse statement, read as ZIMSTAT's (session 2495): **needs written permission**. The ERW holds no table of any of them.
  - **The Ministry of Energy, Algeria** (read 1103, its home page): "(c) Ministry of Energy 2026".
  - **DGS, Gabon** (read 1112, its home page): "Copyright 2020 Direction Generale des Statistiques du Gabon." (with its accents in the record).
  - **SEEG, Gabon** (read 1113, its home page): "(c) 2026 SEEG. Tous droits reserves" (with its accent in the record); its Mentions legales page was not read.
  - **URCA, the Bahamas** (read 1121, its home page, this session): "Copyright (c) The Utilities Regulation and Competition Authority (URCA) 2026 | All Rights Reserved." Its Terms of Use and Service page (read 1122) holds its title and no terms.
- **The verdicts' reads now have the outcome exactly `read`** (test 205). Their earlier notes: read 1103 "(c) Ministry of Energy 2026; no terms of reuse; its 2022 energy balance's address now answers with the site's page"; 1112 "Copyright 2020 DGS; its publications end in 2012"; 1113 "(c) 2026 SEEG. Tous droits reserves; no figures or reports linked".
- **Not given a verdict:** EPC Samoa (its robots address only), ONS Algeria (its certificate fails), CREG (no terms page read; the ERW holds no table of it), Sonelgaz, BPL (no terms page read), the Bahamas' statistics institute (its host does not resolve).
- **The record:** 565 tables, 199 publishers with a verdict, 1,120 requests, 0 problems. Tests 152, 205, 207 and 378 pass.

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1, 2 | URCA's home page and its Terms of Use and Service page | 200 |

Reads recorded: 1121, 1122.

## Decisions made without you

- **No other request:** the other publishers' pages were already saved.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/metadata/license_verdicts.csv` (four rows), `warehouse/metadata/license_reads.csv` (reads 1121, 1122; three outcomes), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c127/s2579/`.
