# Session 2257 report: the licenses' twenty-sixth round

24 October 2026, from 04:05 UTC, on lab-desktop (the data machine), a session of `queue/done/102-day-5-november-data-poland-belgium-new-zealand-columbia.md`, run beside session 2256 (whose notes a helper drafts). Model spend USD 0. Pulls: 4 requests of 20 (below). Also Supabase, for the lock and the archive.

## Read these first

- **This chain's publishers first: two new verdicts.**
  - **Energy-Charts.info (Fraunhofer ISE)** (may be public in both columns, read 442): its API's description says "Unless stated otherwise, the data provided by the Energy-Charts API is licensed under the CC BY 4.0 license. Proper attribution to Energy-Charts.info as the source is required." `energy_charts_belgium_hourly` is therefore public. Its connector's license line and header say so, it was written again offline (the same rows) and it joined the release package (release check: 0 differences).
  - **The Electricity Authority (New Zealand)** (may be public in both columns, read 450): its copyright statement licenses its material under CC BY 4.0, with attribution. `emi_nz_generation_demand_monthly` was already public.
- **PSE has no verdict.** Neither its reports app, its API's OpenAPI description, its home page nor its system data page (reads 431 to 436, 458 and 459) names any terms of use for its data. `pse_poland_balance_15min` stays internal. PSE's terms are a question for you below.
- **The hosts this chain found closed are recorded as reads:**
  - opendata.elia.be (its robots file closes the API and downloads to all but Google);
  - transparency.apg.at (no answer);
  - www.nwd-wc.usace.army.mil (its certificate fails verification);
  - cwms-data.usace.army.mil (its robots file closes the time series);
  - DART's `/dart/cs/`;
  - www.usbr.gov's `/pn-bin`.
- **The own-choice sessions' sources, chosen here so their terms are known:**
  - **Session 2258: the Census Bureau's construction spending (C30),** for spending on power construction. www.census.gov has no robots file (read 460), its C30 data page links the release workbook (read 461), and the Census Bureau's verdict is on record.
  - **Session 2259: Energy-Charts' Hungary, Romania, Greece and Bulgaria,** under the verdict above. Austria, Switzerland and Czechia were left to chain 103, whose agent asked first; Belgium is this chain's, and Italy is chain 104's fallback.
- **The record:** 31 reads, 381 to 411 on this branch when written, 431 to 461 since session 2261's merge (after chains 099 and 101's 381 to 430). The read numbers named in this report are the merged ones. `tests/test_session205.py`'s bound is raised by 40. The license check shows 460 tables, 113 publishers with a verdict, 409 requests and no problem.

## The pulls

1. PSE's home page (read 458): no terms linked.
2. PSE's system data page (read 459): no terms stated.
3. `www.census.gov/robots.txt` (read 460): HTTP 404, no file.
4. The C30 data page (read 461).

## Errors

- **`tests/test_session378` found Belgium's table internal under a public verdict.** The table was made public in this session, as above.
- **The Belgium table's rewrite carried other chains' metadata rows from the main checkout in its patch** (Eurostat's gas, Statistics Norway). Only its own rows were taken, by key (`runs/c102/s2257/be_only.patch`).

## Decisions made without you

- **Energy-Charts' Belgium made public** under its stated license.
- **Austria left to chain 103,** and southeastern Europe taken for session 2259.

## For Samuel's ruling

- **PSE's terms for its reports API:** none found on its pages. Is PSE's data public (it is published openly, with no license stated), or held until PSE answers?

## Files

- New: this report.
- Changed:
  - `warehouse/metadata/license_reads.csv` (381 to 411; 431 to 461 since session 2261's merge), `license_verdicts.csv` (Energy-Charts, the Electricity Authority), `license_tables.csv`, `docs/licenses.md`;
  - `tests/test_session205.py`;
  - `warehouse/connectors/energy_charts_belgium.py`, `warehouse/redivis/release_v1.py`, `docs/redivis/release-v1/`;
  - the Belgium table's rows in `docs/coverage.md`, `coverage.csv`, `sources.csv` and `archive_manifest.csv`;
  - `archive/sessions/SESSION_2253_REPORT.md`.
- On the data machine only: `runs/c102/s2257/`, `runs/license_reads/s2257/`.
