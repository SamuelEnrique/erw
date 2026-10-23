# Session 2122 report: retail electricity prices and costs (Berkeley Lab): not taken, the data file is not where the ERW can read it

23 October 2026, from 22:47 UTC, on lab-desktop (the data machine), the third session of `queue/done/079-day-28-october-data-quakes-credits-rates-world-renewables.md`, unattended. Model spend USD 0. Pulls: 8 requests of 15 (below). No table written.

## Read these first

- **Berkeley Lab's Retail Electricity Price and Cost Trends data file is not published on eta-publications.lbl.gov,** the host that serves Berkeley Lab's files to the ERW's reader:
  - The 2024 Update's publication page (`/publications/retail-electricity-price-and-cost`) links only the report's PDF; the research area "Retail Electricity Price Trends" lists six publications and no data file among them.
  - The data and its visualization tools live on emp.lbl.gov, which refuses the ERW's reader (HTTP 403, read 14, 12 October 2026).
- **Two other Berkeley Lab files were looked at and not taken:**
  - **The data and code of Wiser et al. 2025, "Factors Influencing Recent Trends in Retail Electricity Prices"** (`pub.zip`, 0.9 MB, the 2025 paper's "Data File"): a state-and-year panel, 2010 to 2024 (720 rows, 25 columns: the real and nominal average rate, the residential rate, sales, generation by source, coal retirements, a gas hub price, public power and retail switching shares, meters, behind-the-meter solar, efficiency, demand response, electric vehicles, SAIFI, expected wildfire losses). Its readme says some underlying data are proprietary and given in aggregated form; several columns' units are stated only in the paper's methods PDF (`expected_loss_mwh`, `btm`, `ee`); and it holds no cost components, which is what the session asks for. Taking it would mean guessing units and redistributing aggregates of proprietary data, so it is left; the file is saved in `runs/license_reads/s2122/` for a session with a ruling.
  - **"Electric Utility Distribution Costs: Scoping Study"** (2026): its page links only the report's PDF.
- **No replacement source** was taken in this session: the file's rule replaces a source another chain took first, and this one was not taken, only out of reach. Session 2127 (a source of the session's own choosing) can take another.

## The pulls

1. `eta-publications.lbl.gov/robots.txt` (read 241): disallows Drupal's own paths and `/search/`.
2. The 2024 Update's publication page.
3 and 4. Two guesses at a later edition's page (`-0`, `-1`): HTTP 404.
5. The research area page "Retail Electricity Price Trends".
6. The 2025 paper's publication page.
7. Its `pub.zip`.
8. The distribution costs study's page.

## Errors

- **Two requests spent on guessed addresses** (pulls 3 and 4, HTTP 404): the site's search is disallowed, so a later edition could only be looked for by its address.

## Decisions made without you

- **No table from the 2025 paper's data file:** units not stated in the file, aggregates of proprietary data, and not the cost components asked for.
- **No replacement source here;** session 2127 is the chain's own choice.

## For Samuel's ruling

- **Berkeley Lab's retail price and cost trends data file** is on emp.lbl.gov only, which refuses the ERW's reader; a person can download it in a browser if it is wanted, or ask Berkeley Lab.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (241), `docs/licenses.md`.
- On the data machine only: `runs/c079/s2122/`, `runs/license_reads/s2122/`.
