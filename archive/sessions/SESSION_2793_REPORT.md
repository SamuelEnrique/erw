# Session 2793 report: Santee Cooper not taken (its figures are in annual-report PDFs)

26 October 2026, about 03:02 to 03:04 UTC, on lab-desktop (the data machine), chain 142, unattended. Precheck passed (`runs/c142/pre2793.out`). Model spend USD 0. Pulls: 2 requests of 15, both by the probe; one web search.

## Read these first

- **Santee Cooper not taken,** as file 142 foresaw:
  - www.santeecooper.com's robots file closes `/Currently/`, `/Employees/` and two pages, and names no Claude agent (read 1590); santeecooper.com redirects to it (read 1591).
  - The search found Santee Cooper's generation by source and energy sales (27,353 GWh in 2014) in **annual-report PDFs**, five years a report, archived by the South Carolina state library and statehouse. There is no data file.
  - Santee Cooper's load is held hourly through EIA-930's SC balancing authority, and its sales through EIA-861.
- **No table.**

## Requests (2 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.santeecooper.com's robots file (its own request) | 200 |
| 2 | santeecooper.com's robots file (its own request) | redirected to www's |

Reads recorded: 1590 and 1591.

## Decisions made without you

- **The annual-report PDFs not read:** five years a report in GWh, from archives of other hosts, would not make a current series within the ceiling.

## For Samuel's ruling

- None new.

## Files

- New: this report. Changed: the license record (reads 1590 and 1591) and `docs/licenses.md`.
- On the data machine only: `runs/c142/s2793/`, `runs/license_reads/s2793/`.
