# Session 1135 report: CARB's allowance auctions, a quarterly row

23 October 2026, 20:13 to 20:16 UTC, on samueloldlaptop, unattended, on `wip/1135-board` (cut from `wip/1139-board`). Chain `queue/done/076-day-24-october-code-ask-board-2.md`. Model spend USD 0. (The chain file's first plan for this session, on-peak and off-peak rows, was dropped by session 1125: the board draws them.)

## What was done

- **A fourth frequency, quarterly**, in the builder (`stats`: a move over a year only; the one-year range once four values are held), the page (`FREQ_WORDS`, `noMove`, `dateWords` and `shortDate` write a quarter as its month, `STALE_DAYS` 135: a quarter, a month and the 10 days) and the workbench (`chartFreq`: a quarterly series is charted on the months' axis, each point at its own month).
- **CARB's auctions drawn** in "Carbon and credits": the current and the advance auction's settlement prices (`carb_auction_allowance_prices`, public), a row each, USD per tonne. The current auction's row keeps the id of the grey row it replaces (`cca-auction`), so `page_keep.py` keeps no stale twin. On this machine's copy of the table the newest auction is August 2026: 41.76 (current) and 41.00 (advance). The rows reach the board on the data machine's next run of the builder.
- The method note's table of every price table says so.

## Checks

- `python -m unittest tests.test_session1135`: exit 0, 3 tests (the two rows from the table's real rows, with their figures; the page's words, dates, moves, stale mark and the workbench's axis).
- Every test that reads the board's files (15 files, 210 tests) and `test-board.mjs`, `test-board-1116.mjs`, `test-board-1137.mjs`: exit 0.
- Em dashes: 0.

## Decisions made without you

1. **A quarterly series charted on the months' axis**, not a fourth axis in the workbench. Reversible.

## For Samuel's ruling

- None new.
