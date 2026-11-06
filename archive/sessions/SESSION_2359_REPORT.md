# Session 2359 report: Morocco closed, no table

24 October 2026, from 08:31 UTC, on lab-desktop (the data machine), a session of `queue/done/110-day-12-november-data-pakistan-bangladesh-morocco-kazakhstan.md`. Model spend USD 0.

Pulls: 10 requests of 15:
- **Morocco:**
  - www.one.org.ma's robots address (HTTP 404) and home page;
  - www.mem.gov.ma's robots address (HTTP 404);
  - data.gov.ma's robots address (the connection closed);
  - www.hcp.ma's robots file.
- **Replacements:**
  - pc-axis.geostat.ge's robots address (HTTP 404) and three listings of its PxWeb API;
  - databaza.instat.gov.al's robots address (a connection timeout).

## Read these first

- **Morocco is closed to the reader:**
  - **ONEE** (the Office National de l'Electricite et de l'Eau Potable): its pages answer with a fingerprinting script that sets a bot-check cookie before any content, a bot challenge.
  - **data.gov.ma**, the open data portal: it closes the connection at its robots file.
  - **The Haut-Commissariat au Plan:** its robots file disallows `/docs/` and `/download/`, where its data files are.
  - **The energy ministry** (www.mem.gov.ma): no robots file, but its statistics pages would have had to be guessed. Not asked further.
- **No replacement found within the ceiling:**
  - Georgia's Geostat PxWeb holds no energy section (Industry holds only NACE activity tables).
  - Albania's INSTAT database host times out.
- **No table.** The chain's later sessions of its own choosing can take another grid.

## Errors

- None.

## Decisions made without you

- **ONEE's bot-check script read as a challenge,** not worked around.
- **Stopped at 10 of 15 requests,** with no source within reach.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- On the data machine only: `runs/c110/s2359/`, `runs/license_reads/s2359/`.
