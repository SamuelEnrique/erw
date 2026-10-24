# Session 2243 report: the licenses' twenty-fifth round

24 October 2026, from 03:36 UTC, on lab-desktop (the data machine), the sixth session of `queue/done/101-day-4-november-data-france-spain-brazil-australia.md`, unattended (run before session 2242, whose notes a helper drafts beside it). Model spend USD 0. Pulls: 5 requests of 20 (below).

## Read these first

- **Sessions 2238 to 2241's publishers were read in their own sessions,** with four new verdicts:
  - RTE: may be public, read 365.
  - REE: may be public, needs written permission if the ERW sells, read 369.
  - ONS: CC BY, read 371.
  - Swissgrid: needs written permission, read 380.

  Hosts closed to the reader: ODRE (its robots file), AEMO's nemweb (a challenge), www.energy.gov.au and www.aer.gov.au (the connection reset).
- **Sessions 2244 and 2245's candidates read first,** so that their sources would be settled before their pulls:
  - **Eskom's data portal** (South Africa's hourly demand and generation). Its robots file disallows only WordPress paths (read 382). **Its disclaimer** (read 384) gives a new verdict, needs written permission in both columns: "The information or data published or displayed remains the sole property of Eskom and may not be exploited by the User for any purposes, including but not limited to, commercial purposes." Not taken.
  - **Taiwan Power's open data:** data.gov.tw's robots file answers HTTP 500 (read 381). www.taipower.com.tw has no robots file (read 385). No dataset address could be found without data.gov.tw, so Taiwan is left.
  - **So sessions 2244 and 2245 take U.S. EIA data,** whose verdict is on record (public domain): two series the ERW does not hold, the crude oil quality at refineries and natural gas heat content.
- **The other publishers without a verdict** were not asked again (session 2125's reasons: standing rulings, or earlier rounds that found no terms).
- **The record:** 453 tables, 113 publishers with a verdict, 383 requests; the license check finds no problem.

## The pulls

1. data.gov.tw/robots.txt (read 381): HTTP 500.
2. www.eskom.co.za/robots.txt (read 382).
3. Eskom's data portal (read 383).
4. Its disclaimer (read 384).
5. www.taipower.com.tw/robots.txt (read 385): no robots file.

## Errors

- None.

## Decisions made without you

- **Eskom and Taiwan dropped** as sessions 2244 and 2245's sources, for the reasons above; EIA in their place.

## For Samuel's ruling

- None new. Eskom's data, like Swissgrid's, would need the publisher's consent.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (381 to 385), `warehouse/metadata/license_verdicts.csv` (Eskom), `docs/licenses.md`.
- On the data machine only: `runs/c101/s2243/`, `runs/license_reads/s2243/`.
