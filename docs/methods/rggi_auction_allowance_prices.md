# RGGI CO2 allowance auction results, quarterly (Regional Greenhouse Gas Initiative)

Energy Research Warehouse (ERW), method note written in session 2032 (chain 058) for a table first written on 25 September 2026 (session 7).

Tables: `rggi_auction_allowance_prices`

## Publisher and address

Regional Greenhouse Gas Initiative (RGGI, Inc.), "Allowance Prices and Volumes" (`https://www.rggi.org/auctions/auction-results/prices-volumes`, `RGGI_URL`), an HTML table linked from the auction results page (`https://www.rggi.org/auctions/auction-results`, `RGGI_PAGE`). One GET a run, with the connector's user agent `UA`. Source id `rggi:prices-volumes`. Connector: `warehouse/connectors/carbon_auctions.py` (session 7), function `rggi`, one of its two tables (`--table rggi`); the daily sequence runs it as the step `carbon_auctions` (`warehouse/run_daily.sh`).

## Vintage and revision

The file on the data machine was written by run `20261010T144334Z` (10 October 2026) and restored from the Redivis draft by `scripts/sync.py`, as its last header line says. Every row carries `retrieved_at` 2026-10-10T14:44:25Z. Header: "File holds 304 rows, 2008-09-25T00:00:00Z to 2026-09-09T00:00:00Z. This run wrote 304 rows: 304 new".

Each run reads the whole page. The rows are merged into the existing file by (entity, variable, ts_utc) (`iso_prices.write_csv`, `merge_series`); the file is not deleted first. A value RGGI changes replaces the old row; a row RGGI no longer shows stays in the file. A table whose newest auction is more than `STALE_DAYS` (150) days before the day of the run is not written (`main`).

## Shape and variables

Series, 304 rows: 7 series on 2 entities, from 85 auctions. `entity` `rggi:current_auction` (73 auctions, 25 September 2008 to 9 September 2026, one in each quarter from the third quarter of 2008 to the third quarter of 2026) and `rggi:future_auction` (12 auctions of future-vintage allowances, 18 March 2009 to 7 December 2011, each held on the same day as a current auction). `ts_utc` the auction date at 00:00:00Z; `freq` P3M; `geo` US; `node` the auction as RGGI names it ("Auction 73", "Auction 14 (Future)"); `market` and `vintage` empty.

| Variable | Unit | Rows | First | Last |
|---|---|---|---|---|
| `clearing_price` | USD/short_ton | 83 (73 current, 10 future) | 2008-09-25 | 2026-09-09 |
| `allowances_offered` | count | 85 (73, 12) | 2008-09-25 | 2026-09-09 |
| `allowances_sold` | count | 85 (73, 12) | 2008-09-25 | 2026-09-09 |
| `ccr_allowances_sold` | count | 51 (current only) | 2014-03-05 | 2026-09-09 |

One allowance is one short ton of CO2 (header). 85 auctions times 4 measures is 340 cells; 36 are not in the table: the Cost Containment Reserve (CCR) cell of the 22 current auctions before March 2014 and of the 12 future auctions, and the clearing price of Auction 13 (Future) and Auction 14 (Future), at which 0 allowances were sold.

## Reading the source

- The page must hold exactly one table whose columns are, in order, Auction, Date, Quantity Offered, CCR Sold, Quantity Sold, Clearing Price, Total Proceeds; otherwise the table stops ("layout changed").
- Every auction name must read "Auction <n>", with " (Future)" or nothing after it; a name with "(Future)" goes to `rggi:future_auction`. A name that does not parse stops the table.
- Every date must be YYYY-MM-DD, or the table stops.
- "$" and "," are removed from a cell. A cell that is "--", empty or "nan" is not written; the code keeps no count of them. Any other cell that is not a number stops the table.
- Total Proceeds is read and not written.
- The page is tried up to 4 times (`iso_prices.with_retries`, `RETRIES`), with a wait of 5 seconds times the attempt number after each failure; any answer but HTTP 200 is a failure; timeout 120 seconds (`get`).
- No row ceiling is set in the code.
- A failure writes no file. It is a skip rather than a failure only under `iso_prices.gap_skip`: on GitHub's runner for a table of `known_gaps.csv` (this one is not), or when the error is a publisher's lag in the words "<n> days old (limit <m>)". This connector's age refusal reads "is <n> days old; not writing", so it stays a failure.
- The connector does not call `iso_prices.paused()`; RGGI is not in `warehouse/metadata/paused_sources.csv`.

## License

Internal. `sources.csv` has `internal` for `rggi:prices-volumes`; the header: "License: internal. The page says only '(c) RGGI'; terms unconfirmed." `license_verdicts.csv`, RGGI, read 18 (RGGI's home page, read 12 October 2026): "needs written permission", for any use and for commercial use; the page read carries no statement on reuse, and a search found no terms page.

## Cross-checks (session 2032)

- The counts above were computed from the rows, read past the header lines; the 304 rows equal the header's count, and no (entity, variable, ts_utc) appears twice.
- In each of the 8 auctions with CCR allowances sold, `allowances_sold` exceeds `allowances_offered` by exactly `ccr_allowances_sold`, so RGGI's offered quantity does not count the reserve. In no auction with CCR sold is `allowances_sold` at or below `allowances_offered`. 16 of the 85 auctions sold fewer than were offered.
- The current auction's clearing price was 3.07 at the first auction (25 September 2008), lowest at 1.86 (8 September 2010) and highest at 37.65 at the newest (9 September 2026).
- The connector has no cross-check of its own beyond its reading rules. `price_board_carbon` is derived from this table ([`price_board_carbon.md`](price_board_carbon.md)).

## What it does not hold

- Total proceeds, and the clearing price of the two future auctions that sold nothing.
- A CCR figure for the auctions before March 2014: on the page read, those cells were "--", empty or "nan", the only cells the code leaves out without stopping.
- RGGI's other pages (auction notices, market reports); only the prices and volumes table is read.
- California's auctions: `carb_auction_allowance_prices`.
