# Session 2677 report: the licenses' fifty-fifth round (the CSO of Myanmar may be public; EDL and the Turkmen statistics committee need written permission)

25 October 2026, about 11:43 to 11:47 UTC, on lab-desktop (the data machine), chain 134, unattended. Precheck passed (`runs/c134/pre2677.out`). Model spend USD 0. Pulls: none of 20.

## Read these first

- **`license_verdicts.csv` was read first.** This chain has taken no table so far. This round takes the publishers it met whose pages were already saved; sessions 2678 and 2679 run after it.
- **Three verdicts** (`runs/c134/s2677/verdicts.py`), each line cut by code from a page saved earlier in this chain:
  - **The CSO, Myanmar** (read 1383, its Terms Of Use): "Except where otherwise noted, all statistical data and metadata published on this website are licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license ... for any purpose, including commercial purposes". **May be public.**
  - **EDL, Lebanon** (read 1375, its home page): "جميع الحقوق محفوظة ©" (all rights reserved). **Needs written permission** (ZIMSTAT's precedent).
  - **The State Committee of Turkmenistan on Statistics** (read 1388, its English home page): "© year. All rights reserved". **Needs written permission.**
  - Reads 1375 and 1388 had their outcomes set to exactly `read` (session 2593's form); their earlier notes are kept in the verdicts' notes.
- **The script's first run stopped** at EDL's line, which holds an en dash between the company's name and "all rights reserved". It had already written the CSO's row. The cut was moved to begin after the dash, the script made to skip a row already written, and it was run again; each verdict is in the file once.
- **Not given a verdict:**
  - CAS and LCEC (Lebanon): their robots files close every path to Claude's agents, so nothing of theirs is taken.
  - Tavanir, the Statistical Centre of Iran and IGMC: they do not answer.
  - Turkmenistan's energy ministry: no terms were read.
- **The record:** 583 tables, 240 publishers with a verdict, 1,389 requests, 0 problems. Tests 152, 205, 207 and 378 pass.

## Decisions made without you

- **No request this round:** the three pages were already saved.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/metadata/license_reads.csv` (two outcomes), `warehouse/metadata/license_verdicts.csv` (three rows), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c134/s2677/`.
