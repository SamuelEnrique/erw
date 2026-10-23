# Session 2057 report: the federal energy loans, and FEMP's federal energy data: neither published as a file

23 October 2026, from 20:02 UTC, on lab-desktop (the data machine), a session of `queue/done/066-day-25-october-data-disasters-loans-drought-assistance.md`. Model spend USD 0. Pulls: 7 requests of 15 (www.energy.gov's robots file, asked in a call of its own: it disallows the site's code, search and user paths, none of the office pages; a guessed FEMP data page, HTTP 404; FEMP's home page; its reporting and data page; its comprehensive annual energy data page; ctsedwweb.ee.doe.gov's robots file, a new host, in a call of its own: none, HTTP 404; the data site's report page).

## Read these first

- **No table written.** The chain file said: if LPO's portfolio is still only a map application, take another public source the ERW does not hold.
  - **LPO (now the Office of Energy Dominance Financing):** session 980 read the portfolio and projects pages at 13:52 UTC today and found the project list only in an embedded application on `lpoapps.loanprograms.energy.gov`, whose robots file failed before any answer. Nothing has changed since, so no request was spent on it again.
  - **The replacement tried: FEMP's federal agencies' energy use** (the Federal Energy Management Program's Comprehensive Annual Energy Data: agencies' energy and water use and costs, fiscal 1975 to 2024). Its pages on www.energy.gov point to `https://ctsedwweb.ee.doe.gov/Annual/Report/Report.aspx`, an ASP.NET application: a disclaimer ("findings reported to the Department of Energy as of July 1, 2025") whose OK button posts the form back, and the reports behind it. No file is published; reading it would mean scripting the application's postbacks, which the ERW's connectors do not do.
- **For a later chain:** FEMP's data, if a file form of them is found (the annual report to Congress carries tables in PDF), and LPO's portfolio, if its application's host answers its robots file.

## Errors

- **One request spent on a guessed address** (`/femp/comprehensive-annual-energy-data-and-sustainability-performance`, 404) before the home page gave the real one, under `/cmei/femp/`.

## Decisions made without you

- **No table rather than a scraped application:** the session's ceiling and the connectors' form (a published file or API) kept.
- **LPO not asked again** on session 980's finding of this afternoon.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- On the data machine only: `runs/c066/s2057/`, `runs/license_reads/s2057/`.
