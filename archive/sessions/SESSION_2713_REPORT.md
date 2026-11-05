# Session 2713 report: the licenses' fifty-seventh round (NS Power, Manitoba Hydro and SaskPower need written permission)

25 October 2026, about 17:07 to 17:09 UTC, on lab-desktop (the data machine), chain 136, unattended. Precheck passed (`runs/c136/pre2713.out`). Model spend USD 0. Pulls: none of 20: each verdict comes from a page this chain had already saved.

## Read these first

- **`license_verdicts.csv` was read first.** None of this chain's publishers had a verdict.
- **Three verdicts** (`runs/c136/s2713/verdicts.py`), each line cut by code from the saved terms: the two web pages with session 2495's `cut`, and SaskPower's PDF with pdfplumber (chain 128's lesson). Each source read's outcome was first set to exactly `read`, its earlier note kept in the verdict's note.

  | Publisher | Read | The line | Verdict |
  |---|---|---|---|
  | Nova Scotia Power | 1427 | "You will not use our Intellectual Property Rights (or anything that is confusingly similar to our Intellectual Property Rights) for any purpose." (Terms of Service, 3.1) | needs written permission |
  | Manitoba Hydro | 1435 | "You must have the written permission of Manitoba Hydro before you can reproduce, download, modify, or distribute any of our website content, in whole or in part, no matter which format or language." (Terms of use, Ownership) | needs written permission |
  | SaskPower | 1441 | "You shall not market, commercially exploit, reproduce, copy, download, derivatize, modify or distribute any content, this Website or any services, in whole or in part, without SaskPower's written permission." (Digital Terms and Conditions, 10) | needs written permission |

- **NS Power's verdict matches its table:** `nspower_ns_load_hourly` (session 2708) is internal, and test 378 passes.
- **Not given a verdict:**
  - NL Hydro (session 2711), whose terms were not read because no file was to be taken from it.
  - The CCEI (session 2709), whose host's certificate fails verification.
- **The record:** 589 tables, 245 publishers with a verdict, 0 problems. Tests 378, 205 and 152 pass. Test 205's bound was raised for this chain in session 2708 and needs no more.

## Decisions made without you

- **SaskPower's terms read from its PDF,** the page's text giving only links to it.

## For Samuel's ruling

- **Three permission requests would open three Canadian provinces' figures:**
  - NS Power: making `nspower_ns_load_hourly` public;
  - Manitoba Hydro: its operating statistics;
  - SaskPower: its generation and interchange.

## Files

- New: this report. Changed: `warehouse/metadata/license_verdicts.csv` (three rows), `warehouse/metadata/license_reads.csv` (three outcomes), `docs/licenses.md`.
- On the data machine only: `runs/c136/s2713/`.
