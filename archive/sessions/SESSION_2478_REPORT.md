# Session 2478 report: Bhutan's electricity, not taken (no table found on the statistics bureau's site)

24 October 2026, from 13:28 UTC to 13:31 UTC, on lab-desktop (the data machine), chain 120, unattended. Precheck passed (`runs/c120/pre2478.out`). Model spend USD 0. Pulls: 3 requests of 15.

## Read these first

- **The ERW holds no Bhutanese source** (`sources.csv` and the connectors on main searched for BPC, Druk Green, NSB and Bhutan).
- **Bhutan is not taken:**
  - The National Statistics Bureau's robots file (www.nsb.gov.bt, answered at nsb.gov.bt) closes its admin path only and names no AI agent (read 817).
  - The site's own search (its WordPress API) finds nothing for "electricity" and only a food balance sheet for "energy" (reads 818 and 819).
  - A web search found no official table from the bureau, the Bhutan Power Corporation, Druk Green Power or the energy ministry. It found only press figures and a 2010 finance ministry PDF.
  - Ember's table already holds Bhutan's yearly generation.
- **Not tried, for the ceiling and the session's span:** the Bhutan Power Corporation's and Druk Green Power's annual reports (PDFs). A later chain can read them.

## Requests (3 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.nsb.gov.bt/robots.txt | 200 (at nsb.gov.bt): `/wp-admin/` closed |
| 2 | NSB's site search, "electricity" | 200: no result |
| 3 | NSB's site search, "energy" | 200: a food balance sheet only |

Reads recorded: 817 to 819 (on this branch). One web search looked for official tables; it reached no publisher's host.

## Decisions made without you

- **No table for Bhutan** rather than figures from the press.

## For Samuel's ruling

- None.

## Files

- New: this report. Changed: `warehouse/metadata/license_reads.csv` (reads 817 to 819). On the data machine only: `runs/c120/s2478/`.
