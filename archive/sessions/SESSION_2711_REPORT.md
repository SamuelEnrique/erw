# Session 2711 report: Newfoundland and Labrador's electricity not taken (NL Hydro publishes no data file; its figures are in report PDFs)

25 October 2026, about 17:04 to 17:07 UTC, on lab-desktop (the data machine), chain 136, unattended, while this machine's own daily task held the data lock. Precheck passed (`runs/c136/pre2711.out`). Model spend USD 0. Pulls: 4 requests of 15, all by the probe; one web search.

## Read these first

- **The ERW held Newfoundland and Labrador only in Statistics Canada's tables;** no source or read named NL Hydro or the Public Utilities Board.
- **NL Hydro** (nlhydro.com):
  - A WordPress site. Its robots file closes only `/wp-admin/` and names no Claude agent (read 1442).
  - Its media library, searched for "load" and listed for spreadsheets and for CSV files, holds six images and no data file (reads 1443 to 1445).
  - The search found its figures only in annual reports and in the Muskrat Falls inquiry's exhibits on the House of Assembly's site, as PDFs. Peaks and annual totals are given in prose and tables, not as a series.
- **No table.** The Board of Commissioners of Public Utilities' filings (pub.nl.ca) were not asked: they are NL Hydro's reports as PDFs, which a table would need parsing page by page. The 11 requests left were kept.

## Requests (4 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | nlhydro.com's robots file (its own request) | 200 |
| 2 | the media library searched for "load" | 200, six images |
| 3 | the media library listed for spreadsheets | 200, none |
| 4 | the media library listed for CSV files | 200, none |

Reads recorded: 1442 to 1445.

## Decisions made without you

- **No replacement for Newfoundland and Labrador:** the file's alternative (another public grid source) goes to the session's own choices (2714, 2715, 2720), which have their own ceilings.
- **NL Hydro's terms not read:** no file was to be taken from it. Its publisher is left for a later licenses round if a file appears.

## For Samuel's ruling

- None new.

## Files

- New: this report. Changed: the license record (reads 1442 to 1445) and `docs/licenses.md`.
- On the data machine only: `runs/c136/s2711/`, `runs/license_reads/s2711/`.
