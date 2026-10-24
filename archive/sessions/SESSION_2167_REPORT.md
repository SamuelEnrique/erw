# Session 2167 report: the licenses' twenty-first round

24 October 2026, from 00:33 UTC, on lab-desktop (the data machine), the sixth session of `queue/done/094-day-31-october-data-britain-imports-gas-use-waterways.md`, unattended. Model spend USD 0. Pulls: 5 requests of 20 (below). (Session 2166's six notes are drafted by a helper beside this session and checked in session 2166's report.)

## Read these first

- **This chain's publishers first:** Elexon's verdict was added in session 2162 (read 294); EIA is record 1; the Corps of Engineers refuses the reader (session 2165).
- **NESO** (a new verdict, may be public in both columns, read 299): the NESO Open Data Licence lets a user "copy, publish, distribute and transmit the Information; adapt the Information; exploit the Information commercially and non-commercially", acknowledging NESO with "Supported by National Energy SO Open Data". No ERW table holds NESO's data: the host that serves its files disallows every reader (session 2162).
- **Sessions 2168 and 2169's sources chosen first, so that this round could read their terms:**
  - **Hydro-Quebec's open data** were the first choice for session 2168: donnees.hydroquebec.com's robots file disallows `/api/` and every dataset download for every reader but Google's (read 300). Not asked further.
  - **The UK's Energy Trends electricity tables** (the Department for Energy Security and Net Zero, on GOV.UK) take its place: GOV.UK's robots file disallows print and search pages only (read 301); the Energy Trends section 5 page (read 303, last updated 29 September 2026) links tables ET 5.1 to 5.6 on assets.publishing.service.gov.uk and states, as every GOV.UK page does, "All content is available under the Open Government Licence v3.0, except where otherwise stated" (a new verdict, DESNZ, may be public in both columns).
  - **The Canada Energy Regulator's pipeline throughput and capacity data** for session 2169: the CER's verdict is on record (read 96).
- **The Railroad Commission of Texas** was considered and left: its terms (read 19) allow noncommercial use only.
- **The other publishers without a verdict** were not asked again (session 2125's reasons: standing rulings, or earlier rounds that found no terms).
- **The record:** 430 tables, 100 publishers with a verdict, 301 requests; the license check finds no problem.

## The pulls

1. NESO's Open Data Licence page (read 299).
2. `donnees.hydroquebec.com/robots.txt` (read 300).
3. `www.gov.uk/robots.txt` (read 301).
4. A wrong address for the Energy Trends page (read 302): HTTP 404, its footer the site's licence.
5. The Energy Trends section 5 page (read 303).

## Errors

- **One request spent on a guessed address** (pull 4).

## Decisions made without you

- **The own-choice sessions' sources chosen in this round,** so their terms were read before their pulls.
- **GOV.UK's sitewide licence taken for the Energy Trends tables,** the page stating no other terms.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (299 to 303), `warehouse/metadata/license_verdicts.csv` (NESO, DESNZ), `docs/licenses.md`.
- On the data machine only: `runs/c094/s2167/`, `runs/license_reads/s2167/`.
