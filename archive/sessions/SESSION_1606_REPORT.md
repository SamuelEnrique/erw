# Session 1606 report: the power spreads

6 November 2026, on samueloldlaptop's second window, chain 165. Branch `wip/1606-board`, cut from `wip/1605-board` with `origin/main` merged. Model spend USD 0.

## What it did

- `warehouse/derived/board_page.py`:
  - `build_hubspreads` and a group "Hub spreads, within and across grids": seven pairs, day-ahead and real time, 14 rows (gap 3: the trader path's step 15 asked for North to Houston and West to North).
  - The spark spread at every other public hub, behind a new Show filter of the spark group (main hubs by default).
  - `fleet_heat_rates` and `heat_basis`: every spark and dark row's hover says its heat rate is the board's assumption and gives EIA's fleet average beside it, written as `heat_ref` too (gap 27).
- `site/lib/board.ts`: `hubspread` among the power groups for the stale rule.
- The method note's section; the audit's gaps 3 and 27 closed, 28 left open with its reason.
- `tests/test_board_1606.py` (5 tests), on real rows (`tests/fixtures/board_1606/`, 419 rows).

## Proof

- The board's and the page's test files with `test_board_1601` to `1606`: 132 run, 1 skipped, 1 failure, the known `test_session1116` node check (the committed file's staleness; the same on `origin/main`). Node: `test-board.mjs`, `1137`, `1193`, `1311` exit 0.

## Decisions made without you

- **The pairs**: the trader path's two (North to Houston, West to North), South to Houston, each grid's north-south pair (CAISO NP15 to SP15, SPP North to South), and two across grids (ERCOT to SPP, CAISO to ERCOT): every pair is public on both sides. Held grids' pairs are not built.
- **A cross-grid spread compares the same date**, each mean on its own local operating day, and says so in the formula and the hover.
- **EIA's fleet heat rate is read where the table is**: `eia_heat_rates_annual` is neither on this machine nor in the live set, so the rows built here say the assumption alone. The test of the words with EIA's number uses an in-memory reading, not a fixture file of invented values.
- **No 4CP exposure**: it needs a 15-minute price the hourly store does not keep (session 1604 offered the same for the next chain).

## For Samuel's ruling

- None new.
