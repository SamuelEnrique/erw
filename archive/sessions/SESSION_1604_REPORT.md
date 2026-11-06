# Session 1604 report: carbon, the held rows' words, the costs

6 November 2026, on samueloldlaptop's second window, chain 165. Branch `wip/1604-board`, cut from `wip/1603-board` with `origin/main` merged. Model spend USD 0.

## What it did

- `warehouse/derived/board_page.py`:
  - RGGI's auction row and ISO-NE's reserves row: status `licensed`, note naming the publisher and the internal table (gaps 17, 18). Ids kept.
  - A RIN price placeholder in the carbon group (gap 19).
  - `build_costs` and a group "Delivery charges and transmission peaks": ERCOT's coincident peak load, a monthly row of four summer months a year (gap 7); the Texas delivery charges' placeholder naming the utilities' tariffs at the PUCT.
- The method note's section; the audit's gaps 7, 17, 18, 19 closed, 20 noted.
- `tests/test_board_1604.py` (4 tests), on ERCOT's 28 published 4CP rows (`tests/fixtures/board_1604/`).

## Proof

- `tests.test_board_1601` to `1604` with the board's tests: 85 run, 1 failure, the known `test_session1116` node check on the committed file's staleness (session 1601's report; fails the same on `origin/main`). `test-board.mjs`, `1137`, `1193`, `1311`: exit 0; `test-board-1116.mjs`: its check 5 only, the same.

## Decisions made without you

- **4CP as a monthly row, not an annual one**: the board's rows are daily, weekly, monthly or quarterly, and an annual step would need new rules on both sides; dated by its month, the row's moves read as a trader would (the month before in the summer, the same month a year before), and it is marked stale when the summer is old, which it is until ERCOT publishes 2026's by December.
- **A load, on a price board**: the chain asks for 4CP in a cost group; the row's unit says MW and its hover says what the peaks set. No price at the peak interval is drawn (the 15-minute hub price at each interval would need the history read at that step: offered, not done).
- **The delivery charges stay a placeholder**: the internal table is a model's reading of news reports, not a tariff.

## For Samuel's ruling

- Whether the hub's real-time price in each 4CP interval should be a row beside the load (what a large load avoided by curtailing): the price history is held; recommended yes, in the next chain.
