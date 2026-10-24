# Session 2360 report: Kazakhstan, no table

24 October 2026, from 08:34 UTC, on lab-desktop (the data machine), a session of `queue/done/110-day-12-november-data-pakistan-bangladesh-morocco-kazakhstan.md`. Model spend USD 0.

Pulls: 5 requests of 15:
- www.kegoc.kz's robots file;
- its sitemap and file sitemap;
- its page on Kazakhstan's power industry;
- its analysis of the wholesale market in 2025 (a PDF under `/upload/iblock/`, which its robots file allows).

## Read these first

- **KEGOC's robots file closes `.pdf`, `.docx`, `.pptx` and `.xlsx` files** except PDFs under `/upload/iblock/`, and names no AI agent.
- **KEGOC publishes no table of generation and consumption that the reader can take:**
  - **Its page on Kazakhstan's power industry** (answered in Kazakh at its English address) is narrative. It gives installed capacity on 1 January 2026 (26,807.0 MW) and available capacity (22,844.2 MW), but no series.
  - **Its 2025 wholesale market analysis** (42 pages, Kazakh) gives its history of capacity, peak load and generation as charts: their numbers come out of the PDF as a jumble with no years or months to attach them to. Its monthly sections compare 2024 and 2025 by plant, not as one balance.
- **The Bureau of National Statistics' figures** sit behind its Taldau portal, whose API needs index identifiers that the session did not have. Finding them would have been guessing, so it was not tried.
- **No table.**
- **One figure worth recording** (from the analysis, not taken into a table): the system's record peak load, 17,724 MW, on 18 December 2025 at 17:55, with generation at 16,684 MW and a deficit of 831 MW.

## Errors

- None.

## Decisions made without you

- **KEGOC's charts not read as data**: their numbers cannot be tied to years without guessing.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- On the data machine only: `runs/c110/s2360/`, `runs/license_reads/s2360/`.
