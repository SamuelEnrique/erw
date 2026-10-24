# Session 2464 report: Jamaica, no table

24 October 2026, from 13:00 UTC, on lab-desktop (the data machine), a session of `queue/done/119-day-19-november-data-kyrgyzstan-cote-divoire-jamaica-laos.md`. Precheck passed (`runs/c119/precheck_2464.out`). Model spend USD 0.

Pulls: 10 requests of 15:
- **our.org.jm, 4,** at least 10 seconds apart: its robots file, the home page, the electricity sector page and the quarterly performance reports.
- **statinja.gov.jm, 2:** its robots address (HTTP 404: none) and the home page.
- **www.jpsco.com, 4:** its robots file, the sitemap index, the page sitemap and the annual reports page.

## Read these first

- **Jamaica is closed to the reader within the ceiling:**
  - **The Office of Utilities Regulation:**
    - its robots file disallows only `/wp-admin/` and asks a crawl delay of 10 seconds, kept;
    - its electricity sector page carries net-billing notices, not generation statistics;
    - its quarterly performance reports cover the utility's service standards.
  - **STATIN:** no robots file. Its home page links trade, prices, population and survey data, and no energy or production statistics; their address would have had to be guessed, so it was not tried.
  - **Jamaica Public Service (JPS):** its robots file disallows nothing, and its page sitemap lists `/annual-reports/`. That page answers with an Incapsula challenge (a script and no content), which the ERW does not work around.
- **No table.** With five requests left, no replacement grid was tried, as chain 110's session 2359 left Morocco. A later session of this chain's own choosing can take one.
- **The crawl delay was kept across runs:** each run of the probe to our.org.jm began with a 10-second wait, since the probe's own pause applies only within a run (session 2429's finding, from Botswana).

## Errors

- None.

## Decisions made without you

- **No guessed addresses on STATIN,** and no replacement with five requests left.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- On the data machine only: `runs/c119/s2464/`, `runs/license_reads/s2464/`.
