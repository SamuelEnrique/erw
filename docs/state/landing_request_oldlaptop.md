# Landing requests: the old laptop's second window (chain 165, the price board)

Energy Research Warehouse (ERW). Written by chain 165 (`queue/done/165-day-6-november-oldlaptop-window2-price-board.md`), which never builds the site and never lands: the old laptop's memory holds one build, and its first window owns it. The desktop's second window (chain 164, its landing service) lands each row below through `scripts/land_check.py` with the task and port given, marks the row landed with the commit, and deletes the branch and its ancestors of this chain once they are ancestors of main.

| # | Branch | Head | Task | Port | Requested (UTC) | Tests on this machine | State |
|---:|---|---|---|---:|---|---|---|
| 1 | `wip/1605-board` | `19fd5c0c0` | `1600-1605-board` | 3600 | 2026-11-06 | the board's and the page's test files: 127 run, 1 skipped, 1 failure (below); the whole suite not run to the end (below) | held in row 2: land row 2 in its place |
| 2 | `wip/1610-board` | `edd783ea6` | `1600-1610-board` | 3600 | 2026-11-06 | the board's and the page's test files: 134 run, 1 skipped, 1 failure (the same, below); the whole suite not run here | waiting |

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

## Known on this machine

- **`tests.test_session1116`, its node check 5** ("none of the top twelve is stale") fails on the committed `board.json` (ERCOT's day-ahead row at 30 October, built 5 November): **it fails the same way on `origin/main`**, so it is the file's state, not the branch. The gate's run may show it.
- **The whole suite** (`python -m unittest discover -s tests`) was stopped by the harness for low memory before it printed a result, and was not started again unattended. The gate's suite is the first whole run.
