# Session 2781 report: SMUD not taken (its figures are in annual-report PDFs and a current-only chart)

26 October 2026, about 01:51 to 01:53 UTC, on lab-desktop (the data machine), chain 141, unattended. Precheck passed (`runs/c141/pre2781.out`). Model spend USD 0. Pulls: 2 requests of 15, both by the probe; one web search.

## Read these first

- **SMUD not taken:**
  - www.smud.org's robots file holds only a sitemap line, no rule, and names no Claude agent (read 1580); smud.org redirects to it (read 1581).
  - The search found SMUD's operating statistics (sales, power supply by source, peak demand) in **its annual reports' five-year summaries, PDF pages**. Its "Current and expected energy use" page charts demand and generation refreshed every 15 minutes, with no history offered as a file, and the generation chart excludes some power purchase agreements.
  - SMUD's load is held through EIA-930's BANC balancing authority, and its sales through EIA-861.
- **The hosts did not bar the reader,** so file 141's "another public grid source" does not apply; the own-choice sessions follow.
- **This chain's four utilities gave no table.** Large US public power utilities publish their figures in reports and filings, not data files; the ERW already holds each through EIA's forms. File 142's four (SRP, Santee Cooper, NYPA, CPS Energy) may fare the same; session 2791 says so in that file.
- **No table.**

## Requests (2 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.smud.org's robots file (its own request) | 200, a sitemap line |
| 2 | smud.org's robots file (its own request) | redirected to www's |

Reads recorded: 1580 and 1581.

## Decisions made without you

- **The 15-minute chart not polled:** a current-only feed, as chain 137 found PEI's, builds a series only by reading it on a clock, which is a ruling's to start.

## For Samuel's ruling

- None new.

## Files

- New: this report. Changed: the license record (reads 1580 and 1581) and `docs/licenses.md`.
- On the data machine only: `runs/c141/s2781/`, `runs/license_reads/s2781/`.
