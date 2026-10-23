# Session 2111 report: the licenses' seventeenth round (the Energy Commission, the Treasury, Open NY)

23 October 2026, from 22:22 UTC, on lab-desktop (the data machine), a session of `queue/done/069-day-27-october-data-public-lands-sunlight-spending-streams.md` (run while session 2110's notes were being written). Model spend USD 0. Pulls: 7 requests of 20, two pages a host beside its robots file. They were the Energy Commission's Conditions of Use; home.treasury.gov's robots file, its Site Policies and Notices and its Privacy and Legal Notices; and data.ny.gov's robots file, its home page and the record of its Terms of Use dataset. `license_verdicts.csv` was read first.

## Read these first

- **First, main merged into the branch** (chain 067 landed as `2da0fd4a`): 8 files in conflict, resolved by rule (`runs/c069/resolve_c067.py`).
  - Decision 61 (`tCO2e`) now stands before this chain's 62 (`acre`) and 63 (`MJ/m2-day`), in the standard and the validator.
  - The rule lists keep both sides.
  - The release README's held list is the union, with its true count (183).
  - `docs/coverage.md` had `census_metro_population` twice; main's line, with its new method link, was kept.
  - The license record was rebuilt: 0 problems; release check 0 differences.
  - No key is twice in sources, coverage, the license tables, the reads, the verdicts, the archive manifest or the upload record. The release package's 18 doubled variable pairs are main's too.
- **Reads 237 to 251:** this chain's robots files and pages of sessions 2106 to 2109 (BLM, NASA POWER, NCEI, BEA, data.openei.org, LEAD's CC BY 4.0 submission page, api.eia.gov, the Energy Commission), then this round's seven. They follow main's 236. Chain 079's agent was told, and numbers its reads from 255.
- **The California Energy Commission: may be public, needs written permission if commercial** (a new verdict on read 245, the sentence cut by code from the saved page). In the Commission's words, its materials are "free for public use consistent with the Public Records Act ... provided the Energy Commission is credited". Third-party materials and those bearing a copyright notice are excepted, and "use or modification of these materials or information for commercial or profit-making purposes is prohibited". This is read as RRC's noncommercial clause is read. `cec_total_system_generation_annual`'s header credits the Commission.
- **The Treasury: not settled.** home.treasury.gov's robots file allows `/`, but its Site Policies and Notices and its Privacy and Legal Notices state no terms of reuse and no copyright statement. The record's rule leaves a federal body's work that states no terms to the owner (`docs/methods/large_load_public.md`). So session 2112's 1603 table, if written, is unsettled and held from the Stanford draft.
- **Open NY: not settled yet.** data.ny.gov's robots file (crawl delay 1 second) disallows OData, tiles, login and browse filters, not `/api/views/` or `/resource/`. Its terms are the PDF attached to dataset 77gx-ii52, a third page of the host past this round's two. Session 2114 reads it first, as its own source's terms.
- **The other publishers of this chain have verdicts:** BLM (read 159), NOAA NCEI (read 9), EIA (read 1), USGS (read 87, for session 2113).
- **The record:** 417 tables, 92 publishers with a verdict, 249 requests; `licenses.py check` 0 problems. `tests/test_session205.py`'s bound is raised by one round (`+ 20`, with its comment); 14 tests pass.

## Errors

- **The first push of the merge failed on GitHub's side** ("unable to write file ... index-pack failed"); the same push a minute later went through.

## Decisions made without you

- **The Energy Commission read as noncommercial with credit,** as RRC's verdict is (reversible).
- **Open NY's PDF left to session 2114,** keeping the round's two pages a host.

## For Samuel's ruling

- **The Treasury's Section 1603 awards list:** the Treasury's site states no terms of reuse. Should a work of a federal agency that states none be public under 17 U.S.C. 105, as the NRC's reactor status was taken (`docs/methods/generation_mix_hourly.md`)? Or should it stay unsettled until the Treasury is asked?

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (237 to 251), `license_verdicts.csv` (the Commission), `license_tables.csv`, `docs/licenses.md`, `tests/test_session205.py` (the bound); the merge's files (above).
- On the data machine only: `runs/c069/s2111/`, `runs/c069/resolve_c067.py`, `runs/license_reads/s2111/`.
