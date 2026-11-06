# Session 1601 report: the power rows

6 November 2026, on samueloldlaptop's second window, chain 165. Branch `wip/1601-board`, cut from `wip/1600-board` with `origin/main` merged. Model spend USD 0.

## What it did

- `warehouse/derived/board_page.py`:
  - ERCOT's 8 load zones (day-ahead; Houston, North, South and West in real time) from `ercot_zone_prices_history`, with their battery spreads and day-ahead less real time, ordered after the hubs (gap 1).
  - `iso_zone_prices_history` read too, for CAISO ZP26's and SPP South's history before 26 August 2026 (gap 26).
  - Every power, battery, peak, day-ahead less real time and ancillary row carries `basis`, its interval in words, read from the newest table that holds the hub (`INTERVALS`, `hour_words`, `basis_of`) (gap 2).
  - `build_nodes`: five monthly rows of ERCOT's node basis by class of point, from `node_basis_summary`, each linking to `/cost-of-power` (gap 4).
  - `build_adders`: ERCOT's real-time adders as daily rows; an ended adder is no row, so RTRDPA alone today (gap 6).
  - The capacity placeholder split into one row an auction (PJM, NYISO, ISO-NE, MISO), each naming the publisher and the hold; PJM's keeps the id `capacity` (gap 5).
- `site/lib/board.ts`: `basis` and `link` on the row type; `nameTitle`, the name's hover, now with "Interval: ...". `site/components/board/BoardView.tsx`: the hover through `nameTitle`, and the row's link beside its words (its click does not open the workbench). No layout or style change.
- `docs/methods/price_board.md`: a section for this session. The audit's gaps 1, 2, 4, 5, 6 and 26 marked closed.
- `tests/test_board_1601.py` (9 tests) on real rows cut from this machine's tables (`tests/fixtures/board_1601/`, three CSVs, 1,074 rows).

## Proof

- `tests.test_board_1601`: 9 passed (the node test included).
- The board's tests (`test_session132`, `240`, `1118`, `1139`, `1135`, `1117`, `1116`, `168_board`): 67 run, 1 failure, `test_session1116`'s node check "none of the top twelve is stale". **It fails the same way on `origin/main`** (`742abc575`, run in the queue worktree): the committed `board.json` (built 5 November) has ERCOT's day-ahead row at 30 October, 6 days old against the power rows' 3. It is the file's state, which the next data machine build changes, not this branch.
- `site/scripts/test-board.mjs`, `test-board-1137.mjs`, `test-board-1193.mjs`, `test-board-1311.mjs`: exit 0.
- The new steps on this machine's own tables (zones from 1 August only): 34 rows with values, every zone to 17 October here (this copy's newest), RTRDPA to 16 October, the three ORDC adders logged as ended on 2025-12-04/05, the five node rows to October 2026. Those figures are this copy's, not the warehouse's newest, and go in no document.

## Decisions made without you

- **A zone the warehouse holds in day-ahead only** gets its real-time row "not held yet", as a hub with one market already does: ERCOT publishes every load zone in real time, and the warehouse's table holds four.
- **The node basis by its median only**, one row a class, the 10th to 90th percentiles left to the node view the row links to: five rows in place of twenty-five, and each figure keyed by its row.
- **An adder that ended is no row** (the rule the carbon block already follows for a discontinued auction series), with the end dates in the method note; the threshold is 90 days behind the table's newest hour.
- **The site's `node_modules` reached through a junction** (`site\node_modules` in the worktree to the main checkout's), so the node tests run here; nothing is built. The junction is removed before the worktree is.

## For Samuel's ruling

- None new.
