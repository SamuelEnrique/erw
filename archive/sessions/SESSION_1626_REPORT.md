# Session 1626 report: the 4CP exposure

6 November 2026, on samueloldlaptop's second window, chain 167. Branch `wip/1626-board`, cut from `wip/1625-board` with `origin/main` merged. Model spend USD 0.

## What it did

- `warehouse/derived/board_page.py`, `cp4_price`: a monthly row of the cost group, the hub average's 15-minute real-time price in each 4CP interval, read from the ERCOT history and the rolling real-time table filtered as they stream (audit row 28, closed).
- `tests/test_session247.py`: the list of the builder's whole-table readers takes `cp4_price` (behind `here()`).
- The method note's section; `tests/test_board_1626.py` (2 tests) on ERCOT's 28 intervals and the hub's real prices in them (`tests/fixtures/board_1626/`).

## Proof

- The wide set (every test file naming the board's code, every `test_board_16*`): 336 run, the known `test_session1116` failure only.
- On the old laptop's tables: 28 of 28 intervals priced (the fixture's cut found every one in the history).

## Decisions made without you

- **The price at the interval, not at the hour**: the chain's question is what a load paid in the interval that sets its charge; the history holds the 15-minute price, so the hourly store is not needed.
- **Your ruling 2 of chain 165's note taken as recommended** (a row beside the load): it was offered as the default, and the row is data the warehouse holds, with nothing sent or posted.

## For Samuel's ruling

- None new.
