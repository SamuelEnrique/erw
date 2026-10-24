# Session 2212 report: California's rooftop solar (California DG Stats): not taken, its terms forbid it

24 October 2026, from 01:38 UTC, on lab-desktop (the data machine), the third session of `queue/done/098-day-2-november-data-price-indexes-reservoirs-rooftops.md`, unattended. Model spend USD 0. Pulls: 3 requests of 15 (below). No table written.

## Read these first

- **California Distributed Generation Statistics publishes the data** the file asks for (the Rule 21 interconnection data sets of PG&E, SCE and SDG&E, every interconnected system from 1982, under CPUC Decision 14-11-001; read 349), on a host with no robots file (read 348).
- **Its Terms of Use forbid what the ERW does** (read 350, a new verdict: needs written permission, in both columns): the site grants "a limited ... license ... to access the Platform and review the Content on the screen of your computer", says "YOU HAVE NO RIGHT TO EXTRACT, PRINT, COPY, REPRODUCE, USE, MODIFY, OR DISPLAY EXCEPT ON YOUR COMPUTER FOR YOUR OWN INTERNAL PERSONAL USE, ANY OF THE CONTENT other than for the purposes of NEM", forbids disclosing content to a third party without the Administrators' written consent, and forbids "any robot, spider or other automatic device ... to access, retrieve, scrape ... or otherwise distribute any portion of the Site or the Platform". No data file was asked.
- **No replacement source** in this session: the chain's three own-choice sessions (2213, 2217, 2221) can take others. California's small-scale solar stays as the warehouse holds it in `eia861_distributed_generation` and `lbnl_tracking_the_sun`.

## The pulls

1. `www.californiadgstats.ca.gov/robots.txt` (read 348): HTTP 404.
2. The Download Data page (read 349).
3. The Terms of Use (read 350).

## Errors

- None.

## Decisions made without you

- **The terms read before any data file,** and their prohibition of automated access and copying taken as decisive.

## For Samuel's ruling

- **California DG Stats** (the IOUs' Rule 21 interconnections): its terms need the Administrators' written consent for any copy; a request to them, or a ruling, would open it.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (327 to 329), `warehouse/metadata/license_verdicts.csv` (California DG Stats), `docs/licenses.md`.
- On the data machine only: `runs/c098/s2212/`, `runs/license_reads/s2212/`.
