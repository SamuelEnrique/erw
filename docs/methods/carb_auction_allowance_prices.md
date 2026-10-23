# California cap-and-trade allowance auctions, a quarter (CARB's Summary of Joint Auction Settlement Prices and Results)

Energy Research Warehouse (ERW), method note written in session 2046 (chain 059) for a table first written on 25 September 2026 (session 7).

Tables: `carb_auction_allowance_prices`

## Publisher and address

California Air Resources Board (CARB), Summary of California and Joint Auction Settlement Prices and Results, a PDF at a fixed address, `https://ww2.arb.ca.gov/sites/default/files/2020-08/results_summary.pdf`, linked from `https://ww2.arb.ca.gov/our-work/programs/cap-and-trade-program/auction-information`. The file on the data machine read the edition marked "Last updated August 2026". Source id `carb:auction-results-summary`. Connector: `warehouse/connectors/carbon_auctions.py` (session 7), which also writes `rggi_auction_allowance_prices`; this note describes the CARB table only.

CARB's host answers GitHub's runners HTTP 202 with no body (`known_gaps.csv`, every run since 27 September 2026), so the table is refreshed on the data machine (`carbon_auctions.py --table carb` in `warehouse/run_data_machine.sh`); on the runner the step is recorded as skipped, not failed.

## Vintage and revision

November 2012 to August 2026 in the file on the data machine, written by run `20261023T172920Z` (23 October 2026). Header: "This run wrote 336 rows: 0 new, 336 replacing earlier rows ...; 0 rows are kept from earlier runs."

Each run reads the whole PDF and merges its rows into the file on (entity, variable, ts_utc): a figure CARB revises replaces the old one, and a row the PDF no longer gives stays. A table whose newest auction is more than 150 days old is not written.

## Shape and variables

Series, 336 rows: 56 auctions, each with 6 rows. `entity` `carb:current_auction` (the current-vintage allowances sold at the auction) or `carb:advance_auction` (the advance-vintage allowances); `ts_utc` the first day of the auction month at 00:00:00Z, since the summary gives no day; `freq` P3M; `geo` US-CA; `node` the auction as CARB numbers it; `market` and `vintage` empty.

| Variable | Unit | Rows |
|---|---|---|
| `settlement_price` | USD/tCO2 (one allowance is one metric ton of CO2 equivalent) | 112 |
| `allowances_offered` | count (allowances) | 112 |
| `allowances_sold` | count (allowances) | 112 |

The auctions are "Auction #1" to "Auction #8" (November 2012 to August 2014) and "Joint Auction #1" to "Joint Auction #48" (November 2014 to August 2026; the header: CARB, joint with Quebec), all in February, May, August or November. Joint Auction #48 (August 2026): current 49,016,180 offered and sold at 32.48; advance 6,481,750 offered and sold at 32.75. Current settlement prices ran from 10.09 (November 2012) to 41.76; advance from 10.00 to 41.00.

## Reading the source

- Only the PDF's lines that begin with a month, a year and an auction number are read. Each such line must give exactly six numbers (current offered, sold, price; advance offered, sold, price), read by their comma grouping after the stray spaces of the PDF's text are dropped; a line that does not, or that leaves characters unread, stops the run.
- A PDF with no auction line, or two auctions in one month, stops the run. An answer other than HTTP 200 stops it, after four tries.
- One request a run (the PDF, about 56 auctions); the code counts no row ceiling.

## License

`license_verdicts.csv` records CARB, read 10: "may be public", for public and for commercial use, on the State of California's conditions of use: "In general, information presented on this website, unless otherwise indicated, is considered in the public domain. It may be distributed or copied as permitted by law." Its note: CARB's own page was not read. `license_tables.csv` lists the table under CARB, and the header says public (session 324). Credit: California Air Resources Board.

## Cross-checks (session 2046)

- The counts above were computed from the rows, read past the header lines: 56 auctions times 6 is the 336 rows; no (entity, variable, ts_utc) is given twice.
- Allowances sold never exceed allowances offered, in any of the 112 auction and entity pairs. Fewer were sold than offered at 8 current auctions (February 2016 to February 2017, May and August 2020, May 2025) and 18 advance auctions, the latest February 2026 (6,263,000 of 6,481,750).
- Successive auctions are 89 to 92 days apart: no quarter is missing from November 2012 to August 2026.

## What it does not hold

- The auction day (the month only), and anything on the summary's lines beyond the six numbers.
- RGGI's auctions: `rggi_auction_allowance_prices`, from the same connector.
- Prices between auctions: settlement prices only.
