# Price board: the latest CARB and RGGI allowance auctions

Energy Research Warehouse (ERW), method note written in session 696 (chain 045) for a table first written on 29 September 2026.

Tables: `price_board_carbon`

## Sources and builder

The ERW derives this table from two of its own tables: `carb_auction_allowance_prices` (California Air Resources Board,
its joint allowance auctions) and `rggi_auction_allowance_prices` (the Regional Greenhouse Gas Initiative). Builder:
`warehouse/derived/price_board.py` (session 30, Part A, the price board, platform tool 2), function `build_carbon`, run
daily by `warehouse/run_daily.sh` (step `price_board`). Method: [`price_board.md`](price_board.md), section
"price_board_carbon". `source` is `erw:price_board` on every row, and `source_url` links that method note. No model
writes any value.

For each auction series of each input (an `entity`), the builder takes the newest auction holding a price (CARB
`settlement_price`, RGGI `clearing_price`) and writes:
- `latest_price`, with `allowances_offered` and `allowances_sold` of the same auction;
- `previous_price`, the auction before it, dated with that auction's date;
- `price_change`, latest minus previous.

A series whose last auction is over 366 days before its program's newest is left out as discontinued (RGGI's
future-vintage auctions, which ended in 2011). Prices are rounded to 4 decimals.

## Vintage and revision

Rewritten whole by each run from its inputs as they stand. When an input table is absent from the machine (on GitHub
CARB's server answers HTTP 202, a known gap in `warehouse/metadata/known_gaps.csv`), the rows the last run derived for it
are carried as they were, and the header says so; with no earlier rows the run fails.

The copy on the data machine was rebuilt from the ERW archive by `warehouse/restore_tables.py`, as of run
`20261020T063359Z-github`. That run's header says its 10 CARB rows were carried from the last run. All 15 rows carry
`retrieved_at` 2026-09-29T10:35:16Z; `vintage` is empty.

## Shape and variables

Series, `freq` `P3M`. Key: `entity`, `variable`, `ts_utc`. `ts_utc` is the auction's date as its input table gives it;
CARB publishes only the month, so its dates are the first of the month. `market` is empty. `node` is the auction's name.

| Entity | `geo` | Program |
|---|---|---|
| `carb:current_auction` | US-CA | CARB, the current auction |
| `carb:advance_auction` | US-CA | CARB, the advance auction |
| `rggi:current_auction` | US | RGGI |

| Variable | Unit |
|---|---|
| `latest_price` | `USD/tCO2` (CARB), `USD/short_ton` (RGGI) |
| `previous_price` | as `latest_price` |
| `price_change` | as `latest_price` |
| `allowances_offered` | `count` |
| `allowances_sold` | `count` |

As of 23 October 2026: 15 rows, 3 entities, 5 variables, `ts_utc` 2026-05-01 to 2026-09-09 (4 dates), 4 auction names.

| Entity | Latest auction | Latest price | Previous auction | Previous price | Change | Offered | Sold |
|---|---|---|---|---|---|---|---|
| `carb:current_auction` | Joint Auction #48, 2026-08-01 | 32.48 | Joint Auction #47, 2026-05-01 | 28.81 | 3.67 | 49,016,180 | 49,016,180 |
| `carb:advance_auction` | Joint Auction #48, 2026-08-01 | 32.75 | Joint Auction #47, 2026-05-01 | 28.76 | 3.99 | 6,481,750 | 6,481,750 |
| `rggi:current_auction` | Auction 73, 2026-09-09 | 37.65 | Auction 72, 2026-06-03 | 35.0 | 2.65 | 27,389,847 | 28,537,847 |

RGGI's Auction 73 sold 1,148,000 more allowances than it offered. That difference equals the `ccr_allowances_sold` of
the same auction in `rggi_auction_allowance_prices`, a variable this table does not carry.

## License

The ERW verdict in `docs/licenses.md`: internal. The row reads: publishers "CARB; RGGI"; verdict today "needs written
permission"; decided by "RGGI"; flag in `coverage.csv` internal; flag and verdict "agrees"; if the ERW sells anything
"needs written permission"; ERW verdict "internal". The header says: "Its inputs are licensed internal (CARB and RGGI
terms unconfirmed)." The public price board shows none of its values while it is internal.

## Cross-check

None in the code. Session 30 uploaded the table to the internal Redivis dataset and recorded that its `count(*)` equals
the CSV.

## What it does not hold

- No secondary-market or futures carbon prices: the ERW holds none.
- No auction before the previous one: the full history is in the two input tables.
- No cost containment reserve (CCR) volumes, reserve prices or bidder statistics.
- No discontinued auction series, and no other carbon program.
