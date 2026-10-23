# Session 956 report: the licenses' eighth round

23 October 2026, from 12:45 UTC, on lab-desktop (the data machine), a session of `queue/done/054-day-23-october-data-federal-royalties-wind-costs-minerals.md`. Model spend USD 0. Pulls: 3 requests of 20 (the Department of the Interior's robots file, asked in a call of its own and read first; its Disclaimer of Liability and Endorsement; its Copyright, Restrictions and Permissions notice); sessions 951 to 955's eight reads recorded with them (reads 149 to 159).

## Read these first

- **This chain's publishers first:** EIA, Berkeley Lab and the USGS already had verdicts; the two new ones are Interior's bureaus, the Office of Natural Resources Revenue (session 951) and the Bureau of Land Management (session 955).
- **Two new verdicts** (80 publishers with one): **ONRR: may be public** and **BLM: may be public**, both on the Department's notice (read 159), the same text BOEM's verdict rests on: "Generally, materials produced by federal agencies are in the public domain and may be reproduced without permission. However, not all materials appearing on this web site are in the public domain. Some materials have been donated or obtained from individuals or organizations and may be subject to restrictions on use." ONRR's production and revenue records and BLM's rights-of-way are the bureaus' own. BLM California's service adds its own notice (read 156): data as is, BLM cited as the source, modifications described, nothing represented as approved by BLM; the table's header says so.
- **The four ONRR tables and BLM's are now settled public,** agreeing with their flags (`docs/licenses.md`).
- **Recorded from this chain's sessions:** revenuedata.doi.gov's and revenuedata.onrr.gov's robots files (951), api.eia.gov's answer (953: no robots file, HTTP 403 "API key missing"), ScienceBase's robots file with its content signals (954), gis.blm.gov (no robots file), www.arcgis.com and services1.arcgis.com (no robots file) and BLM California's service notice (955).
- **The record's bound not raised:** the record holds 159 reads, 118 after session 205's 41, within `tests/test_session205.py`'s 122.

## Decisions made without you

- **Two pages of one host, the robots file apart:** the Department's disclaimer and then its copyright notice, which is the page that speaks to reuse; the disclaimer only to liability.
- **The Department's notice for its bureaus,** as for BOEM: ONRR's site is drawn in the browser and states no terms that its page data showed.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (149 to 159), `license_verdicts.csv` (two rows), `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c054/s956/`, `runs/license_reads/s956/`.
