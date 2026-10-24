# Session 2229 report: the licenses' twenty-fourth round

24 October 2026, from 02:58 UTC, on lab-desktop (the data machine), chain 099, unattended. Run after sessions 2230 and 2231 so that their publishers are in the round; session 2236's are left for the next round. Model spend USD 0. Pulls: none of 20. Every verdict rests on a read this chain's sessions made.

## Read these first

- **Four verdicts** (`warehouse/metadata/license_verdicts.csv`, read first; none of the four had one):
  - **Statistics Norway (SSB), read 365: may be public.** SSB's API page, where data.ssb.no/robots.txt redirects: "I likhet med resten av ssb.no benytter API-ene lisensen CC BY 4.0" (like the rest of ssb.no, the APIs use the CC BY 4.0 license). `ssb_norway_electricity_monthly` is public.
  - **Bundesnetzagentur (SMARD), read 368: may be public.** Its Data use page: market data "is licensed under a Creative Commons Attribution 4.0 International Licence", attributed "Bundesnetzagentur | SMARD.de". `smard_germany_monthly` is public.
  - **Statistics Netherlands (CBS), read 376: may be public.** Table 84575NED's own License property, https://creativecommons.org/licenses/by/4.0/, as CBS's catalog gives it. `cbs_netherlands_electricity_monthly` is public.
  - **EirGrid, read 373: needs written permission.** Its website disclaimer bars copying, republishing or distributing its materials "for any public or commercial purposes" without EirGrid's written authority. No table is held from EirGrid.
- **No verdict for MBIE (New Zealand) or Hydro-Quebec:** neither's terms were read. MBIE's page answered a bot challenge (read 370); Hydro-Quebec's robots file bars its API and downloads (read 371).
- **The other publishers of this chain have verdicts:** the IESO (read 225), Eurostat, DESNZ (the Open Government Licence).
- **The license record:** 452 tables, 110 publishers with a verdict, 359 requests in the record, 0 problems. The 663 tests of the license record and the release package pass (7 skipped). `tests/test_session205.py`'s bound holds without a raise.

## Decisions made without you

- **No request this round:** each publisher's terms were read by the session that took its source.
- **SSB's verdict from its API page,** the page its own robots address leads to.

## For Samuel's ruling

- EirGrid: a letter for its System and Renewable Data reports (in session 2231's report).

## Files

- New: this report.
- Changed: `warehouse/metadata/license_verdicts.csv`, `license_tables.csv` (rebuilt), `docs/licenses.md`.
