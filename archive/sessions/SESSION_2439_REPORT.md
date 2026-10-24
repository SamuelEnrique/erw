# Session 2439 report: the licenses' thirty-eighth round (Tunisia's ministry and EEHC need written permission; Kyrgyzstan's statistics are non-commercial)

24 October 2026, about 11:38 UTC, on lab-desktop (the data machine), chain 117, unattended. Precheck passed (`runs/c117/pre2439.out`). Model spend USD 0. Pulls: none of 20. Every verdict rests on a page this chain's source sessions already read.

## Read these first

- **Three verdicts:**
  - **Ministry of Industry, Mines and Energy, Tunisia (ONEM)** (read 705): its home page's footer, "2020©" followed by the ministry's name in Arabic, with no reuse statement anywhere on the page. Verdict: **needs written permission**, sold or not. The ERW holds no table of it.
  - **Egyptian Electricity Holding Company (EEHC)** (read 708): "All Rights Reserved ©2022", with no reuse granted. Verdict: **needs written permission**, sold or not. It is read as POWER Magazine's notice was (read 29). `eehc_egypt_electricity_annual` stays internal.
  - **National Statistical Committee of the Kyrgyz Republic** (read 716): "Open data created by the National Statistics Committee of the Kyrgyz Republic is published under the terms of the Creative Commons Attribution-NonCommercial-ShareAlike license ... 4.0 Worldwide." Verdict: **may be public; needs written permission if commercial**, as RRC's noncommercial grant (read 19) reads. The ERW holds no table of it.
- **Read 705's outcome is now exactly `read`,** as test 205 requires of a verdict's read; its detail moved to the verdict's note.
- **Not given a verdict:**
  - STEG, Armstat, the PSRC, NEA and Uruguay's ministry and catalogue: no page of theirs was read past a robots file that failed or was absent;
  - Statistics Iceland and ILR already have theirs (chain 113).
- **The record:** `licenses.py tables`, `write` and `check` give 520 tables, 151 publishers with a verdict, and 0 problems. Tests 205, 207 and 887 pass; test 205's bound did not need raising.

## Decisions made without you

- **A copyright line with no reuse statement read as needs written permission,** as the record reads EEHC's and POWER Magazine's.
- **CC BY-NC-SA read as RRC's noncommercial grant:** may be public, written permission if commercial.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/metadata/license_verdicts.csv` (three rows), `warehouse/metadata/license_reads.csv` (read 705's outcome), `warehouse/metadata/license_tables.csv`, `docs/licenses.md`. New: this report.
