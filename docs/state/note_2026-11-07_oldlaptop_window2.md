# The old laptop's second window, chain 165: the price board made complete (written 6 November 2026, about 12:35 UTC)

Energy Research Warehouse (ERW), session 1623, for Samuel. Chain 165 (`queue/done/165-day-6-november-oldlaptop-window2-price-board.md`, your file of 6 November), run unattended as sessions 1600 to 1623 in the old laptop's second Claude Code window (`samueloldlaptop-window2`), beside the first window's chain, from 10:55 UTC. Model spend USD 0. Nothing built, nothing landed from this window, by the file's rule: every three sessions the stack was pushed and `docs/state/landing_request_oldlaptop.md` written for the desktop's second window.

## Read these first

- **Nothing of this chain is on main yet** but its documents. The stack's head is `wip/1623-board`; row 5 of the landing request asks the desktop to land it (task `1600-1623-board`, port 3600), and rows 1 to 4 say they are held in it. When it lands, the new rows reach the page on the data machine's next `page_keep.py board` run, not before: `site/data/board.json` is not changed by this chain.
- **What the board gains** (rows from tables already in the warehouse, every figure keyed): ERCOT's eight load zones; the interval of every row stated on hover; ERCOT's node basis by class of point, linking the node view; ERCOT's reliability deployment adder; weekly gas storage, LNG export prices and volumes by terminal, the pipeline trade; North Dakota's first purchase price; US gasoline of all grades; ERCOT's coincident peaks; hub less hub within and across grids; the spark spread at every public hub; six cracks by product; the world gas spreads by the month; a fifth move, the year to date; the trend over 90 days, a year or three years; each power row's day high and low with their local hours, the week's and month's peak hour and the hours above 100, 250 and 1,000 USD/MWh; the twelve-month mean and the latest against it; the rows' CSV as shown, with Python and Stata readers. About 98 rows with values and 12 placeholders more; the file about 55 percent larger (265 KB compressed), not paged.
- **Every held series says "licensed source needed" and names its publisher**: RGGI's auctions and ISO-NE's reserves were "not held yet" with no publisher; the capacity row for four operators is one an auction; RIN prices, LNG feedgas, the regional basis and the LNG netback, the Texas delivery charges are new placeholders, each naming who would supply it.
- **Not run here**: the site's build and the gate (the file's rule); the whole Python suite (stopped by the harness for low memory at session 1605, not restarted unattended). The proof is the board's tests: every test file naming the board's code and this chain's 63 tests, 334 run on the head, with one failure that fails the same on `origin/main` (`test_session1116`'s check that no top-twelve row is stale: the committed file's ERCOT row is 6 days old). Three older tests this chain had broken were found at session 1617 and fixed.
- **Your rulings**: two, below.

## One line a session

| Session | What it did |
|---|---|
| 1600 | The next file (`queue/next/167`, pushed alone); the audit `docs/reviews/board-audit-2026-11-06.md`: 1,200 rows by group, every public price table against them, 29 gaps |
| 1601 | Power: ERCOT's load zones, the zone history, every row's interval, the node basis, the real-time adders, a capacity row an auction |
| 1602 | Gas: weekly storage, LNG export prices and volumes by terminal, the pipeline trade, three more hubs named, feedgas a placeholder |
| 1603 | Oil: North Dakota's first purchase price, US gasoline of all grades (Mars Blend and the US regular and diesel rows found to be duplicates), the coal placeholders point at the world rows |
| 1604 | Carbon and costs: RGGI, ISO-NE's reserves, RINs as "licensed source needed" with publishers; ERCOT's coincident peaks and the Texas delivery charges |
| 1605 | The first push and landing request; the ten new tables named on the license line and the downloads; the whole suite stopped for memory |
| 1606 | The power spreads: hub less hub, the spark spread at every public hub, the heat rates beside EIA's fleet averages |
| 1607 | The gas and oil spreads: cracks by product, the world gas spreads by the month, the basis and netback placeholders |
| 1608 | The moves: the year to date; a stale row's moves blank with its status |
| 1609 | The trend line: 90 days, a year, three years |
| 1610 | The second push and landing request |
| 1611 | The day's extremes: high and low hour with their local times |
| 1612 | The week and the month in one cell: the peak hour and the hours above 100, 250 and 1,000 |
| 1613 | The comparison: the twelve-month mean and the latest against it |
| 1614 | The downloads: the rows' CSV as shown, a Python and a Stata reader |
| 1615 | The third push and landing request |
| 1616 | The checks: `boardFileChecks` and `check-board.mjs --file` (a key per cell, a floor a group, the held rows' words) |
| 1617 | The method note part by part; three older tests fixed |
| 1618 | The file's size measured and its budget held by a test; the build's time estimated |
| 1619 | The fourth push and landing request |
| 1620 | The second read: every row states its step, a monthly row's extremes cell says so, the adder's extremes |
| 1621 | The keys the Digest and Ask read: unchanged; the new keys offered |
| 1622 | The records: nothing landed yet; the audit's rows each with a state; the tests on the head |
| 1623 | This note, the next file, the last push and landing request, the queue |

## The rows and columns added, by group, with their keys

Every figure's key on the page is the row's id and the figure's name (`data-n`), checked by `site/scripts/check-board.mjs` against the file.

| Group | Added | Keys |
|---|---|---|
| Power, by hub and zone | 8 load zones (12 rows), 5 node basis rows, 1 adder row; the column "Day's high / low" | `ercot-lz-<zone>-da`, `-rt`; `ercot-nodes-<class>-basis-p50`; `ercot-system-rtrdpa`; `<id>|ext|hi`, `|ext|lo`, `|ext|w|peak`, `|ext|w|100` and the others |
| Battery spread, day-ahead less real time | the zones' (16 rows) | `ercot-lz-<zone>-<da|rt>-battery`, `-da-minus-rt` |
| Spark and dark spreads | the spark spread at every other public hub (about 8) | `<hub>-spark` |
| Hub spreads (new) | 7 pairs, 14 rows | `<hub>-<hub>-<da|rt>` |
| Natural gas | 3 hub placeholders | `gashub-<name>` |
| Natural gas in storage and LNG exports (new) | 8 storage, 8 LNG prices, 9 LNG volumes, 4 trade rows, feedgas | `eia-nw2-...`, `eia-ngm-...`, `eia-n9133us2` and the others, `lng-feedgas` |
| Crude oil | North Dakota first purchase | `eia-f002038-3-first-purchase-price` |
| Oil spreads | 6 cracks by product | `<product>-less-<crude>` |
| Gas spreads (new) | 3 monthly spreads, 2 placeholders | `erw-wb-<a>-less-<b>`, `gasbasis-regional`, `lng-netback` |
| Retail gasoline and diesel | US all grades | `eia-emm-epm0-pte-nus-dpg-retail` |
| Carbon and credits | RINs placeholder; RGGI as licensed | `rin-price`, `rggi-auction` |
| Delivery charges and transmission peaks (new) | ERCOT coincident peak load; delivery charges placeholder | `ercot-system-cp4-load-mw`, `texas-delivery` |
| Capacity and equities | one placeholder an auction | `capacity` (PJM, its id kept), `capacity-nyiso`, `capacity-isone`, `capacity-miso` |
| Every group | YTD move; 12-month avg and its difference; the trend over 90 days, a year or three years; the interval on hover | `<id>|ytd`, `<id>|avg365`, `<id>|vs365` |

## The held placeholders, by publisher

MISO (paused); PJM; NYISO and ISO-NE (license needed); CME Group (futures); S&P Global Commodity Insights and Natural Gas Intelligence (regional hubs, their basis, JKM); ICE Endex and LSEG (TTF, EUA); S&P Global (coal by basin); UxC, TradeTech, Fastmarkets, Benchmark Mineral Intelligence (uranium and lithium by the day); OPIS and Argus Media (RINs); S&P Global Commodity Insights and ICE (RECs); RGGI, Inc. (its auctions); data vendors (LNG feedgas); shipping assessments (the netback's freight); the Texas utilities at the PUCT (delivery charges); an exchange data vendor (equities). Each row's note names them; the method note's table "What the board cannot show" has every one.

## What landed through the desktop, and what waits

- Landed: nothing yet (the desktop's second window had not reached the request by 12:30 UTC).
- Waits: `wip/1623-board` (row 5 of the request), which holds rows 1 to 4. Once it is an ancestor of main, `wip/1600-board` to `wip/1623-board` can be deleted on origin.

## What did not finish, and why

- **The ERCOT 4CP exposure** (audit row 28): the hub's 15-minute price in each coincident-peak interval; the board's hourly store keeps hours. In the next file.
- **The page's checks on a build** (`check-board.mjs` without `--file`), the screenshots and the keyboard walk: no build in this window. The desktop's gate runs the page checks.
- **The whole Python suite**: stopped for memory once, not restarted unattended.
- **The rows on the real file**: they appear after the landing and the data machine's next build; the next chain reads that file as session 1620 read the made-again one.
- **EIA's fleet heat rates beside the assumptions** are written only where `eia_heat_rates_annual` is on the building machine (it is not on the old laptop, nor in the live set).

## Decisions made without you

- This window's identity is a worktree of its own whose `.erw/machine.json` names `samueloldlaptop-window2` (the main checkout's is the first window's); the precheck read the main checkout's Supabase keys into its process.
- One worktree for every session's branch; no full builder run (memory); this machine's tables (2 to 5 weeks old) read for shapes only, never for a figure in a document.
- Hours, not intervals, for the day's extremes and the counts above a price; the reader's own threshold stays the workbench's.
- The year to date measured from the last value of the year before within a step's slack; a stale row's moves, extremes and twelve-month cells blank with its status.
- The trend's "granularity's equivalent" read as a year of weeks and three years of months.
- The gas spreads by the World Bank's months, labeled monthly.
- Older tests changed where this chain's change was intended (`test_session132`, `1139`, `166`, `247`, `328`, `207` by a rename), each with a comment.
- No paging of the file (about 55 percent larger, not double); a budget held by a test.

## For your ruling

1. **CFTC positions and EIA's STEO price forecasts on the board** (audit rows 24, 25): rows beside the prices they concern, or not at all. Recommended: not on the board; they are not prices.
2. **The hub's real-time price in each 4CP interval** as a row beside the coincident peak load (what a load that curtails avoids): recommended yes, in the next chain (row 28).

## Cost

USD 0 of the model; no request to any publisher; no data written.
