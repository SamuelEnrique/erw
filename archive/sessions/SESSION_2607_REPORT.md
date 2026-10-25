# Session 2607 report: the licenses' fiftieth round (EDSA and EWRC in Sierra Leone need written permission)

25 October 2026, about 05:12 to 05:16 UTC, on lab-desktop (the data machine), chain 129, unattended. Precheck passed (`runs/c129/pre2607.out`). Model spend USD 0. Pulls: 3 requests of 20.

## Read these first

- **`license_verdicts.csv` was read first.** This chain's publishers so far already have verdicts from their own sessions: Solomon Power (2602), the Cook Islands Statistics Office (2603) and Statistics Sierra Leone (2604). This round takes the others it met that could be read. Sessions 2608 and 2609 run after this one, so their publishers are left to their own sessions or to the next round.
- **Two verdicts** (`runs/c129/s2607/verdicts.py`):
  - **EDSA, Sierra Leone** (read 1200, its Terms Of Use, the sentence cut by code): "All contents of the Energy Distribution and Supply Authority (EDSA), Sierra Leone Web Site are: Copyright 2026 by EDSA and/or its suppliers. All rights reserved." **Needs written permission.** Its Privacy Statement (read 1201) states no terms of reuse.
  - **EWRC, Sierra Leone** (read 1199, its home page): no statement on reuse at all, and its pages' sitemap lists no terms page (read 1185). **Needs written permission** (RGGI's form, no sentence). The code checks that the page names no copyright, terms or reproduction.
  - The ERW holds no table of either.
- **Not given a verdict:**
  - **The Solomon Islands National Statistics Office:** its certificate fails (read 1169).
  - **INSTAD, Djibouti:** its site is drawn by script, with no terms in its bytes (read 1195).
  - **EDD, Djibouti:** its hosts do not answer (reads 1194, 1196 and 1197).
  - **The Chambre de Commerce de Djibouti:** only its robots file was read, and the ERW holds nothing of it.
- **The record:** 570 tables, 210 publishers with a verdict, 1,199 requests, 0 problems. Tests 152, 205, 207 and 378 pass.

## Requests (3 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | ewrc.gov.sl's home page | 200 |
| 2, 3 | www.edsa.sl's Terms Of Use and Privacy Statement | 200 |

Reads recorded: 1199 to 1201. No robots file asked again: both hosts' were read in session 2604 (reads 1182 and 1183).

## Decisions made without you

- **No new robots requests:** session 2604 had read both hosts' an hour before.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/metadata/license_reads.csv` (reads 1199 to 1201), `warehouse/metadata/license_verdicts.csv` (two rows), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c129/s2607/`, `runs/license_reads/s2607/`.
