# Session 2581 report: a second own choice, none taken (TEIAS's reports load by script from a route in lazily loaded chunks; Puerto Rico's figures are already in EIA-923; ONEI Cuba's certificate fails)

25 October 2026, about 02:44 to 02:52 UTC, on lab-desktop (the data machine), chain 127, unattended. Precheck passed (`runs/c127/pre2581.out`). Model spend USD 0. Pulls: 6 requests of 20. No table.

## Read these first

- **Puerto Rico** (US first) was looked at first, by search only: its plant-level generation is already in the ERW through EIA's Form EIA-923, and the Energy Bureau's own monthly figures are filings in a docket (NEPR-MI-2019-0007), LUMA's monthly reports PDFs of sales. No request was made to Puerto Rico's hosts.
- **Turkiye (TEIAS),** not held (EPIAS's API needs a login ticket, chain 106): www.teias.gov.tr's robots file names `*` with no rule (read 1130). The site is built by script (read 1131); its monthly production and consumption reports page (read 1133) lists file galleries by year, 2023 to 2026, loaded by script from webim.teias.gov.tr; the page script (read 1134) does not hold the galleries' route, which sits in lazily loaded chunks. Not taken, rather than guess the route (as eSett's, closed by chain 105).
- **Cuba (ONEI):** www.onei.gob.cu's certificate fails verification (read 1135); not asked again.
- **No verdict given:** no table was taken.

## Requests (6 of 20)

| n | What | Outcome |
|---|---|---|
| 1 to 5 | TEIAS's robots file, home page, sector reports page, monthly reports page, page script | 200 |
| 6 | www.onei.gob.cu's robots file | a certificate failure |

Reads recorded: 1130 to 1135.

## Decisions made without you

- **No table from guessed routes.**

## For Samuel's ruling

- None new.

## Files

- Changed: the license record (reads 1130 to 1135) and `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c127/s2581/`.
