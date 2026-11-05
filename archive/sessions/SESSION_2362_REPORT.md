# Session 2362 report: the licenses' thirty-third round

24 October 2026, from 08:39 UTC, on lab-desktop (the data machine), a session of `queue/done/110-day-12-november-data-pakistan-bangladesh-morocco-kazakhstan.md`. Model spend USD 0.

Pulls: 5 requests of 20, two pages a host:
- **stat.gov.mk:** its robots address (HTTP 404) and its English home page.
- **statistica.gov.md:** its robots file, its English home page and its terms of use of data.

## Read these first

- **The National Bureau of Statistics of the Republic of Moldova: may be public** (read 673). Its terms of use of data (updated 27 June 2022) say reuse "will be made under the license Creative Commons Attribution 4.0 International License":
  - commercial use is included;
  - the source must be named, with a link to the material;
  - any change must be indicated.
- **`statbank_moldova_electricity_monthly` is now public.**
  - Its connector's license lines were updated and the table was written again offline (the same 980 rows); its metadata rows were replaced by key.
  - It was added to the release package's held list and its rows in `docs/redivis/release-v1/` (the release check passes).
  - The license record shows flag and verdict agreeing.
  - It is not yet in the Stanford draft; session 2366 uploads it.
- **The State Statistical Office of North Macedonia: no verdict.** Its English home page carries only "(c) State Statistical Office", with no terms of reuse linked and no "all rights reserved". As for PSE in chain 102, no verdict is written; `makstat_macedonia_electricity_monthly` stays internal ("not settled").
- **This chain's reads, 636 to 673 (38):**
  - **Sessions 2357 to 2360's own requests:** robots files, listings and pages. The data downloads are not counted, as in chains 102 and 105.
  - **This round's five.**
  - **Numbering:** they follow main's 583, after chain 108's landing, which was merged into this branch first (one conflict, `docs/licenses.md`, rebuilt). Chain 109 landed next with its reads as 584 to 598, so at this chain's second merge they became 599 to 636. Chain 112 landed next with its reads as 599 to 635, so at session 2370's merge they became 636 to 673, and the numbers in this report were shifted with them.
- **`tests/test_session205.py`'s bound raised by 40** (580 later reads against 602 allowed). Tests 205 and 152 pass.
- **Statnett and Svenska kraftnät** (chain 105's) were not read again: their data pages state no terms, as chain 105 found.

## Errors

- **Test 205 failed once:** `docs/licenses.md` had not been rebuilt after the reads were recorded. It was rebuilt, and the test then failed only on the bound, which was raised.

## Decisions made without you

- **No verdict for North Macedonia's office:** a copyright mark alone is not terms.
- **Moldova's table made public** under its CC BY 4.0 terms.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed:
  - `warehouse/metadata/license_reads.csv` (636 to 673 after session 2370's merge), `license_verdicts.csv` (one verdict), `license_tables.csv`, `docs/licenses.md`, `tests/test_session205.py`;
  - `warehouse/connectors/statbank_moldova.py`, `warehouse/redivis/release_v1.py`, `docs/redivis/release-v1/`;
  - `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`;
  - `SESSION_2358_REPORT.md` (its license line).
- On the data machine only: `runs/c110/s2362/`, `runs/license_reads/s2362/`, `runs/s2362m_*`.
