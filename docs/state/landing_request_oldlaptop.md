# Landing requests: the old laptop's second window (chain 165, the price board)

Energy Research Warehouse (ERW). Written by chain 165 (`queue/done/165-day-6-november-oldlaptop-window2-price-board.md`), which never builds the site and never lands: the old laptop's memory holds one build, and its first window owns it. The desktop's second window (chain 164, its landing service) lands each row below through `scripts/land_check.py` with the task and port given, marks the row landed with the commit, and deletes the branch and its ancestors of this chain once they are ancestors of main.

| # | Branch | Head | Task | Port | Requested (UTC) | Tests on this machine | State |
|---:|---|---|---|---:|---|---|---|
| 1 | `wip/1605-board` | `19fd5c0c0` | `1600-1605-board` | 3600 | 2026-11-06 | the board's and the page's test files: 127 run, 1 skipped, 1 failure (below); the whole suite not run to the end (below) | held in row 7: land row 7 in its place |
| 2 | `wip/1610-board` | `edd783ea6` | `1600-1610-board` | 3600 | 2026-11-06 | the board's and the page's test files: 134 run, 1 skipped, 1 failure (the same, below); the whole suite not run here | held in row 7: land row 7 in its place |
| 3 | `wip/1615-board` | `93600319f` | `1600-1615-board` | 3600 | 2026-11-06 | the board's and the page's test files: 151 run, 1 skipped, 1 failure (the same, below); the whole suite not run here | held in row 7: land row 7 in its place |
| 4 | `wip/1619-board` | `643726a99` | `1600-1619-board` | 3600 | 2026-11-06 | every test file naming the board's code (40 files): 330 run, 1 failure (the same, below); this chain's 57 tests passed; the whole suite not run here | held in row 7: land row 7 in its place |
| 5 | `wip/1623-board` | `56766d6f1` | `1600-1623-board` | 3600 | 2026-11-06 | every test file naming the board's code and this chain's 63 tests (41 files): 334 run, 1 failure (the same, below); the whole suite not run here | held in row 7: land row 7 in its place |
| 6 | `wip/1627-board` | `eb471805b` | `1600-1627-board` | 3600 | 2026-11-06 | every test file naming the board's code and every `test_board_16*` (336 run, 1 failure, the same, below); the whole suite not run here | held in row 7: land row 7 in its place |
| 7 | `wip/1633-board` | `a60601ae6` | `1600-1633-board` | 3600 | 2026-11-06 | every test file naming the board's code and every `test_board_16*` (338 run, 1 failure, the same, below); the whole suite not run here | waiting |

## Row 1: what it holds

Sessions 1600 to 1605, stacked: `wip/1600-board` to `wip/1604-board` are ancestors of `wip/1605-board`.

- The audit, `docs/reviews/board-audit-2026-11-06.md` (29 gaps, their states).
- `warehouse/derived/board_page.py`: ERCOT's load zones; the zone history read; every power row's interval (`basis`); ERCOT's node basis by class with a link to `/cost-of-power`; ERCOT's real-time adders; one capacity placeholder an auction; a group "Natural gas in storage and LNG exports"; three more gas hubs named; North Dakota's first purchase price; US gasoline of all grades; a group "Delivery charges and transmission peaks" (ERCOT's coincident peaks, the Texas delivery charges' placeholder); RGGI, ISO-NE's reserves and RINs as "licensed source needed" with the publisher named.
- `site/lib/board.ts` (`basis`, `link`, `nameTitle`), `site/components/board/BoardView.tsx` (the hover through `nameTitle`, the row's link), `site/app/board/page.tsx` (ten more tables in `TABLES`). **Not built on this machine**: the gate's build is the first.
- `site/data/board.json` is not changed: the new rows appear on the first data machine run of `page_keep.py board` after the landing. That run reads two more large tables (`ercot_zone_prices_history`, about 560 MB here, and `iso_zone_prices_history`, about 360 MB).
- Tests: `tests/test_board_1601.py` to `test_board_1604.py` with their fixtures; `tests/test_session328.py`'s count of the page's tables, 19 to 29.

## Row 2: what it adds to row 1

Sessions 1606 to 1609, stacked on row 1 (`wip/1606-board` to `wip/1609-board` are its ancestors):

- A group "Hub spreads, within and across grids" (seven pairs, both markets); the spark spread at every public hub behind a Show filter; the stated heat rates beside EIA's fleet averages where `eia_heat_rates_annual` is on the machine.
- Cracks by product; a group "Gas spreads, monthly" from the World Bank; the regional basis and LNG netback placeholders.
- A fifth move, YTD (`moves.ytd`), a fifth column on the page; a stale row's moves blank with its status (`shownMove`, used by `check-board.mjs` and `check-board-v4.mjs` too).
- The trend line over 90 days (daily), a year (weekly), three years (monthly, quarterly), up to 90 points; the column named "Trend".
- `tests/test_session132.py` and `tests/test_session1139.py` take a file built before YTD as it is (both are daily-run board tests); `test_session132`'s trend cap 30 to 90.
- More TypeScript not built here: `site/lib/board.ts` (`MoveKey`, `shownMove`, the moves typed partial, `inputsWords` for a product crack, `hubspread` among the power groups), `BoardView.tsx` (the column count from `MOVES`).

## Row 3: what it adds to row 2

Sessions 1611 to 1614 (`wip/1611-board` to `wip/1614-board` are its ancestors):

- The power group's column "Day's high / low" (`ext`: the latest day's highest and lowest hour with their local times, and under them the last 7 and 30 days' peak hour and the hours above 100, 250 and 1,000 USD/MWh), a group flag `extremes`.
- A column "12-month avg" on every group (`avg365`: the trailing twelve-month mean and the latest less it).
- The rows' CSV widened to the board as shown; two new routes, `/board/rows/python` and `/board/rows/stata` (dynamic, like `/api/download`'s readers), linked from the footer.
- `ext` and `avg365` among the figures `holdRows` drops from a held grid's rows. `site/scripts/check-board.mjs` expects every new number.

## Row 4: what it adds to row 3

Sessions 1616 to 1618 (`wip/1616-board` to `wip/1618-board` are its ancestors):

- `boardFileChecks` in `site/lib/board.ts` and `check-board.mjs --file`: the file's own checks, with no server; `check-board.mjs` runs them first on a served page too.
- The method note's part by part at its head (`docs/methods/price_board.md`).
- Three older tests that this chain's changes broke, fixed: `tests/test_session207.py` (by renaming the two new `held =` lines), `tests/test_session166.py` and `tests/test_session247.py` (their expectations follow the chain's intended changes).
- `tests/test_board_1618.py`: the file's budget (2.5 MB as written, 400 KB compressed), with this chain's figures about 1.54 MB.

## Row 5: what it adds to row 4

Sessions 1620 to 1623: every row states its step (`STEP_BASIS`), a monthly row's extremes cell says "monthly", the adder's extremes; the keys the Digest and Ask read checked unchanged; the chain's note (`docs/state/note_2026-11-07_oldlaptop_window2.md`). Once row 5 is an ancestor of main, `wip/1600-board` to `wip/1623-board` can be deleted on origin.

## Row 6: what it adds to row 5

Chain 167's sessions 1624 to 1626: `cp4_price` in the builder, a row of the cost group, the hub average's 15-minute real-time price at each 4CP interval (read from `ercot_all_hub_prices_history` and `iso_rtm_hub_prices`, each filtered to the hub as it streams); `tests/test_session247.py`'s list of whole-table readers takes it. Once row 6 is an ancestor of main, `wip/1600-board` to `wip/1627-board` can be deleted on origin.

## Row 7: what it adds to row 6

Chain 167's sessions 1628 to 1632: the rows' CSV carries the week's and month's peak and hours above 100, 250 and 1,000 (eight columns inside the figures' span); `holdRows` drops `basis` and `heat_ref`, and the builder writes a row with no value without them, so a row with no figure prints its words and no digit; `boardFileChecks` catches a kept `basis`. Once row 7 is an ancestor of main, `wip/1600-board` to `wip/1633-board` can be deleted on origin.

## Known on this machine

- **`tests.test_session1116`, its node check 5** ("none of the top twelve is stale") fails on the committed `board.json` (ERCOT's day-ahead row at 30 October, built 5 November): **it fails the same way on `origin/main`**, so it is the file's state, not the branch. The gate's run may show it.
- **The whole suite** (`python -m unittest discover -s tests`) was stopped by the harness for low memory before it printed a result, and was not started again unattended. The gate's suite is the first whole run.
