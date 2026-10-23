# California cap-and-trade allowance auction results, quarterly (California Air Resources Board, joint with Quebec)

Energy Research Warehouse (ERW), method note written in session 2032 (chain 058) for a table first written on 25 September 2026 (session 7).

Tables: `carb_auction_allowance_prices`

## Publisher and address

California Air Resources Board (CARB), "Summary of California and Joint Auction Settlement Prices and Results", a PDF (`https://ww2.arb.ca.gov/sites/default/files/2020-08/results_summary.pdf`, `CARB_URL`) linked from the auction information page (`https://ww2.arb.ca.gov/our-work/programs/cap-and-trade-program/auction-information`, `CARB_PAGE`). One GET a run, with the connector's user agent `UA`; the text is read page by page with pdfplumber. Source id `carb:auction-results-summary`. Connector: `warehouse/connectors/carbon_auctions.py` (session 7), function `carb`, one of its two tables (`--table carb`).

On GitHub's runner the table is a known gap (`warehouse/metadata/known_gaps.csv`: the PDF answers the runner HTTP 202 with no body); the data machine's run refreshes it (`warehouse/run_data_machine.sh`, step `dm_carb_auction`).

## Vintage and revision

The file on the data machine was written by run `20261023T172920Z` (23 October 2026) from the PDF "Last updated August 2026", as its header says. Every row carries `retrieved_at` 2026-10-23T17:29:20Z. Header: "File holds 336 rows, 2012-11-01T00:00:00Z to 2026-08-01T00:00:00Z. This run wrote 336 rows: 0 new, 336 replacing earlier rows".

Each run reads the whole PDF. The rows are merged into the existing file by (entity, variable, ts_utc) (`iso_prices.write_csv`, `merge_series`); the file is not deleted first. A value CARB changes replaces the old row; a row CARB no longer shows stays in the file. A table whose newest auction is more than `STALE_DAYS` (150) days before the day of the run is not written (`main`).

## Shape and variables

Series, 336 rows: 6 series on 2 entities, from 56 auctions, November 2012 to August 2026, 14 each in February, May, August and November, 89 to 92 days apart, none missing. `entity` `carb:current_auction` and `carb:advance_auction` (CARB sells current-vintage and advance-vintage allowances at each auction); `ts_utc` the first day of the auction month at 00:00:00Z, since the PDF gives no day; `freq` P3M; `geo` US-CA; `node` the auction as CARB numbers it, the same for both entities: "Auction #1" to "Auction #8" (California alone) and "Joint Auction #1" (November 2014) to "Joint Auction #48" (August 2026); `market` and `vintage` empty.

| Variable | Unit | Rows | Entities |
|---|---|---|---|
| `settlement_price` | USD/tCO2 | 112 | 56 each |
| `allowances_offered` | count | 112 | 56 each |
| `allowances_sold` | count | 112 | 56 each |

Prices are US dollars a metric ton of CO2e; one allowance is one metric ton (header).

## Reading the source

- An auction line is a line that matches `LINE_RE`: a month name, a year, the auction's name, "#", its number, then the rest. A line that does not match is skipped and not counted.
- The rest of an auction line must parse into exactly six numbers (`parse_carb_line`): current offered, current sold, current price, advance offered, advance sold, advance price. Spaces are dropped first (pdfplumber splits some numbers), the line must hold exactly two "$", prices must have two decimals, quantities are read by their comma grouping, and a character left over stops the table. Any auction line that fails stops the table.
- No auction line in the PDF stops the table ("layout changed"); two auctions in one month stop it.
- The PDF's "Last updated" line is kept for the header.
- The PDF is tried up to 4 times (`iso_prices.with_retries`, `RETRIES`), with a wait of 5 seconds times the attempt number after each failure; any answer but HTTP 200 is a failure; timeout 120 seconds (`get`).
- No row ceiling is set in the code.
- A failure writes no file. Under `iso_prices.gap_skip` it is a skip on GitHub's runner when the error is the publisher's refusal (this table is in `known_gaps.csv`). The age refusal reads "is <n> days old; not writing", without the words "(limit <m>)" that `gap_skip` reads as a publisher's lag, so a stale PDF is a failure.
- The connector does not call `iso_prices.paused()`; CARB is not in `warehouse/metadata/paused_sources.csv`.

## License

Public. `sources.csv` has `public` for `carb:auction-results-summary`; the header: "License: public (session 324, the document's clause wins: docs/licenses.md, read 10, the State of California's conditions of use: "information presented on this website, unless otherwise indicated, is considered in the public domain"; CARB's own page was not read). Credit: California Air Resources Board." `license_verdicts.csv`, CARB, read 10 (`https://www.ca.gov/use/`, read 12 October 2026): "may be public", and may be public for commercial use.

## Cross-checks (session 2032)

- The counts above were computed from the rows, read past the header lines; the 336 rows equal the header's count, and no (entity, variable, ts_utc) appears twice.
- `allowances_sold` never exceeds `allowances_offered` (0 of 112 auction rows); fewer were sold than offered in 26 of 112.
- The current auction's settlement price was lowest at 10.09 (November 2012) and highest at 41.76 (February 2024). Joint Auction #48 (August 2026): current 32.48 on 49,016,180 offered and sold, advance 32.75 on 6,481,750 offered and sold, the line `parse_carb_line`'s docstring gives as its example.
- The connector has no cross-check of its own beyond its reading rules. `price_board_carbon` is derived from this table ([`price_board_carbon.md`](price_board_carbon.md)).

## What it does not hold

- The day of an auction: only its month.
- Anything else on the PDF, and CARB's other auction reports; only the six numbers of each auction line are read.
- Separate figures for California and Quebec within a joint auction: a row is the auction's whole.
- RGGI's auctions: `rggi_auction_allowance_prices`.
