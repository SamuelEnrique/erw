# Session 2062 report: energy assistance (HHS's LIHEAP): no table, its figures only in PDFs and dashboards

23 October 2026, from 20:30 UTC, on lab-desktop (the data machine), a session of `queue/done/066-day-25-october-data-disasters-loans-drought-assistance.md`. Model spend USD 0. Pulls: 8 requests of 20 (www.acf.hhs.gov's robots file, asked in a call of its own; the LIHEAP program page; the funding releases listing, which answered from acf.gov; acf.gov's robots file, a new host, in a call of its own (the same rules); the FFY 2025 final release; its state allocation PDF, through the raw capture; the LIHEAP data dashboard's robots file, a new host, in a call of its own (crawl delay 60 seconds, kept); the dashboard's dataset catalogue).

## Read these first

- **No table written.**
  - **The allocations by state are published a release at a time:** about fifty funding releases since FFY 2015 (first, second, third, final, reallotment, supplemental), each a page with its state table as a PDF. A year's allotment is the sum of its releases (the FFY 2025 final release, for one, is the last 10 percent of the year's block grant: USD 401,540,000, USD 396,987,327 of it to states, D.C. and territories). From 2015 that is some 100 requests, past the ceiling.
  - **And the PDFs' text cannot be read safely:** in the FFY 2025 final release's state table, the text layer puts the first page's figures out of line with its state names (`pdftotext -layout` gives Alabama no figures and Arkansas another state's), so no row could be trusted to its state.
  - **The data dashboard** (an ArcGIS hub) publishes no dataset as a file: its catalogue lists only apps and pages (quarterly use of funds, households served, benefits).
- **For a later chain:** the LIHEAP Performance Management data warehouse, if it publishes state tables as files; or the releases' PDFs, read with a table extractor that keeps each row's cells together, under a ceiling that allows the releases.

## Errors

- None beyond the dead ends above.

## Decisions made without you

- **No table rather than one whose rows might not belong to their states.**
- **The two years that would fit the ceiling not taken alone:** their releases share the PDF problem.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- On the data machine only: `runs/c066/s2062/`, `runs/license_reads/s2062/`, `warehouse/raw/acf_liheap/` (one PDF).
