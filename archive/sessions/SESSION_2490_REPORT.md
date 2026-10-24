# Session 2490 report: the next file first; Qatar not reachable, Bahrain's electricity taken instead (EWA's Statistical Book 2024), internal

24 October 2026, from 14:45 UTC (chain 121's start) to about 14:56 UTC for the reads and the connector; the table written under the data lock at 16:27 UTC, after GitHub's daily run released it. On lab-desktop (the data machine), the first session of `queue/done/121-day-21-november-data-qatar-zimbabwe-fiji-malawi.md`, unattended. Precheck passed (`runs/c121/pre2490.out`). Model spend USD 0. Pulls: 10 requests of 15 (9 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **The chain was taken at 14:45 UTC by a new agent** under the owner's instruction (run the file the queue step prints). Chains 118, 119 and 120 had written their notes but not landed, and no agent of theirs was running: their Claude processes were gone, leaving three shells asleep (waiting for 16:17 UTC, for 16:20 UTC, and for chain 120's merge). See "For Samuel's ruling".
- **The next file first:** `queue/next/122-day-22-november-data-kuwait-cyprus-guyana-lesotho.md`, sessions 2504 to 2517, machine data, committed alone in a detached worktree and pushed to main as `a5490d56` between two snapshots (both read HTTP 402 on all 25 pages, so they cannot be compared). Number 122 and sessions 2504 to 2517 were free on main and on every branch. Its rules are file 121's word for word, with chain 120's closed hosts added. Its sources: Kuwait, Cyprus, Guyana and Lesotho, none in `sources.csv`, the connectors or the queue on main or on chains 118's to 120's branches.
- **The queue move** (`f25e3517`, file 121 to `queue/done`) was pushed to main between snapshots (`q2490-before`, `q2490-after`; 402 on both).
- **Qatar is not taken:**
  - Kahramaa's www.km.qa and km.qa served a firewall's "Request Rejected" page for their robots files (reads 810, 811);
  - the Planning and Statistics Authority's www.psa.gov.qa did not answer (a connection timeout, read 812);
  - its open data portal, www.data.gov.qa (Opendatasoft), closes `/api/` and every download to all but Googlebot (read 813), as odre.opendatasoft.com and opendata.elia.be do.
- **Bahrain replaced it** (the ERW held no Bahraini source): the Electricity and Water Authority's (EWA) robots file allows every path (read 814). Its publications page links the Statistical Books 2003 to 2024 from an S3 bucket, which answers HTTP 403 for a robots file, S3's answer for an object that is not there (read 818). The 2024 book (28.2 MB, 66 pages, last modified 3 September 2025) was fetched once.
- **A new table, `ewa_bahrain_electricity_annual`** (series, 135 rows, 16 entities, 10 variables, `power`), 2020 to 2024, from five of the book's tables:
  - units sent out by station and the GCC and ALBA links' net flows, and their sum (`supply`);
  - EWA's own and the independent producers' production (checked against the stations, not doubled);
  - the stations' maximum generation capacity at 40 degrees C and the links' transfer capacity;
  - the annual maximum and minimum load and the installed capacity;
  - consumption by sector.
  - Energy in GWh (consumption in million kWh) is multiplied by 1,000 to MWh.
  - The book prints Arabic-Indic digits in places, read as ASCII digits, and keeps an older edition's years in white under the visible ones; characters drawn in white are dropped before a page is read.
  - Not written: one cell out of form (2023's commercial consumption, "5.348" in a table of whole numbers), counted.
  - Written by run `20261024T162744Z`, validated (0 errors, 0 warnings), archived, and held from the Redivis storage and the live set.
- **Internal.** EWA's terms of use: "Reproduction is prohibited other than in accordance with the copyright notice" (read 816). Session 2495's verdict: needs written permission.

## Cross-checks

- Within the book: page 10's total and imports equal page 9's sums each year (the run stops otherwise); page 10's EWA and IPP production equal page 9's stations (2021: 400 GWh = Riffa 308 + Sitra 92).
- `supply` over `owid_ember_electricity_annual`'s demand for Bahrain: 0.508 to 0.548 (2020 to 2024). Ember's figure includes the aluminium smelter ALBA's own generation; EWA's grid figures do not.
- Supply, TWh: 17.62 in 2020, 18.66 in 2022, 19.87 in 2024; peak load 3,662 MW in 2020 and 3,900 MW in 2024.

## Requests (10 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.km.qa/robots.txt | 200: a firewall's "Request Rejected" page |
| 2 | km.qa/robots.txt | the same |
| 3 | www.psa.gov.qa/robots.txt | a connection timeout |
| 4 | www.data.gov.qa/robots.txt | 200: `/api/` and downloads closed to all but Googlebot |
| 5 | www.ewa.bh/robots.txt | 200: every path allowed |
| 6 | www.ewa.bh/sitemap.xml | 200 |
| 7 | EWA's terms of use | 200 |
| 8 | EWA's publications page | 200: the books' links |
| 9 | the bucket's robots.txt | 403: no such object |
| 10 | the Statistical Book 2024 (the fetch) | 200, 28.2 MB |

Reads recorded: 810 to 818 (on this branch; chains 118, 119 and 120 also number from 810, so the chain that lands second renumbers). Two web searches found Kahramaa's reports and EWA's books; they reached no publisher's host.

## Decisions made without you

- **Bahrain for Qatar,** a Gulf grid the ERW did not hold, rather than no table.
- **The bucket's HTTP 403 at its robots file read as no robots file,** S3's answer for a key that is not there.
- **`internal`** under EWA's terms.
- **The trial was the connector run offline from the worktree into `runs/c121/trial/2490/`** (no file copied into the main checkout, so no lock), its table validated there, and the write under the lock reused the saved book.
- **The malformed 2023 commercial cell left out** and counted, though the year's total shows it is 5,348.

## For Samuel's ruling

- **Chains 118, 119 and 120 are unlanded and their agents gone.** Their branches (`wip/2448-2461-data`, `wip/2462-2475-data`, `wip/2476-2489-data`) hold finished work and notes, each waiting for the 16:15 UTC landing window. This chain does not land them: they are other chains' branches. A person, or a session told to, should land them, renumbering their reads (all four chains begin at 810).
- **EWA's consent,** if Bahrain's table is wanted public.

## Files

- New: `warehouse/connectors/ewa_bahrain_electricity.py`, `tests/test_session2490.py`, this report; `queue/next/122-...md` (on main).
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`;
  - `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`;
  - the license record (reads 810 to 818).
- On the data machine only: `runs/c121/s2490/`, `runs/c121/write_122.py`, `warehouse/raw/ewa_bahrain_statistics/`, `warehouse/output/ewa_bahrain_electricity_annual.csv`.
