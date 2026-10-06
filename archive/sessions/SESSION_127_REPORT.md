# Session 127 report: the price board, to finished

## To finish

**The freeze is on** (`REVIEW_FREEZE`, 5 to 7 October). This session pushed `wip/127-board-v4` only, deployed nothing, and loaded nothing into the live set. The branch is from main (`e33f4e0`) and builds on no other. When `python scripts/freeze.py status` exits 0:

```bash
git checkout wip/127-board-v4 && git fetch origin && git merge origin/main
node site/scripts/snapshot-live.mjs take before-127
git push origin wip/127-board-v4 && git push origin wip/127-board-v4:task/127-board-v4
python runs/session118/watch_run.py task/127-board-v4 15
node site/scripts/snapshot-live.mjs take after-127 && node site/scripts/snapshot-live.mjs compare before-127 after-127
cd site && node --import ./scripts/alias-loader.mjs scripts/check-board-v4.mjs https://erw-flame.vercel.app && cd ..
git push origin --delete wip/127-board-v4
```

- **What the comparison should show on the three open pages: nothing but the clock.** The page is `review`; its two tables are under `catalogue_hold` and their three sources under `sources_hold`; it is not in the menu.
- **If the merge conflicts**, it is in the generated metadata the daily run rewrites. Take main's copy and run, under the lock: `python warehouse/metadata/build_coverage.py --only '^(eia_all_futures_prices|price_board_stats)$'`, then `python warehouse/archive/archive.py --tables '^(eia_all_futures_prices|price_board_stats)$' write`.
- **To make the board refresh daily** (after it opens): add `python warehouse/health.py run --step "price_board_v4" -- python warehouse/derived/price_board_v4.py` to `warehouse/run_daily.sh` after `price_board`; take `price_board_stats` off `catalogue_hold`, give it a live-set rule, and point the page at the live set. Until then the page shows the day it was built (5 October).

## Verdict: ready to open, once two things are ruled

The board is finished as a page: every price held, the four moves, the one-year range, three kinds of spread with their formulas, and the seven prices that cannot be had, greyed with their sources. Two things are yours:

1. **The license of EIA's futures**, which I marked internal (below). Nothing on the board shows them, so this does not hold the page.
2. **Whether the page reads the live set daily or stays a copy.** As pushed it is a copy built on 5 October. A price board that is a day old is not a price board; switching the refresh on is three lines (above) and a deploy.

## Read these first

1. **The pull was small because EIA has less than the plan hoped.** 21,312 rows of the 600,000 allowed.
   - **Refined products were already held.** EIA's API has 11 daily spot series; all 11 have been in the warehouse since session 7, back to 1986. I pulled none again.
   - **EIA publishes no daily crude grade beyond WTI and Brent.** Its daily spot route holds those two.
   - **EIA's futures stopped on 5 April 2024.** Its pages say "Futures prices after April 5, 2024, are not available", and the API's newest day for all sixteen contracts is that day. There is no current natural gas futures price to set beside Henry Hub from a free source. I pulled the sixteen from 2019 (21,240 rows, a closed history) and the board shows the row greyed.
2. **I marked the futures internal, on a reading, not on words.** EIA's policy says its publications are public domain and that items "licensed by private individuals, companies, or organizations ... may be protected". It names NYMEX as the source of the futures and Refinitiv as the source of the spot prices. No notice forbids republishing either. The futures are an exchange's settlement prices and EIA stopped carrying them, so I held them back. **The same reading touches the spot tables**, which have been public since session 7 and which I did not change. Yours to rule on both.
3. **The spark spread's newest day is older than the newest power price.** EIA publishes spot gas about a week behind (newest: 29 September). The rule takes gas up to four days old, so the newest spark spread is for 3 October.

## What the board shows

`/board/v4`, in review, in the shared components. Built from tables already in the warehouse; the page reads the site's own copy.

| Group | Lines | Newest day |
|---|---|---|
| Power, day-ahead (ERCOT, CAISO, NYISO, SPP, ISO-NE main hubs) | 5 | 4 or 5 October |
| Power, real time (the same hubs) | 5 | 3 October |
| Natural gas (Henry Hub) | 1 | 29 September |
| Crude oil (WTI, Brent) | 2 | 29 September |
| Refined products (gasoline at 3 places, diesel at 3, jet fuel, heating oil, propane) | 9 | 29 September |
| Spark spread, indicative (5 grids) | 5 | 3 October |
| Day-ahead less real time (5 hubs) | 5 | 3 October |
| 3-2-1 crack spread (Gulf Coast products, WTI) | 1 | 29 September |

- **For each line:** the latest value and its day; the move over a day, a week, a month and a year; and a mark showing where the latest sits between the lowest and highest day of the past year, with both ends in numbers. All 33 lines hold all of it.
- **A move is against a day actually held.** A week is the newest day held at least 7 days before, no more than 6 days older than that; otherwise the move is "not held". Hovering a move shows the value and day it is measured from.
- **Formulas on the page:** spark spread = day-ahead daily mean at the hub - 7.0 MMBtu/MWh x Henry Hub, labeled indicative, with the reason (an assumed heat rate, and gas priced in Louisiana); day-ahead less real time, same day and hub; 3-2-1 crack = (2 x Gulf Coast gasoline + 1 x Gulf Coast diesel) x 42 / 3 - WTI.
- **Greyed, with the source that would supply each:** regional gas hubs, TTF, JKM, uranium, carbon allowances by the day, lithium, and NYMEX futures after 5 April 2024. Where the warehouse holds a monthly average (IMF, for European gas, Japan's LNG and uranium) the row says so and does not show it as a daily price.
- **PJM (licensed) and MISO (paused) in words**, the same words `/board/v3` uses. MISO's hub is in the history table and the builder does not read it.
- **A percent beside a move only for fuels.** Power prices and spreads can be negative.

Three figures from the board as built, to show it reads sensibly (5 October): Henry Hub 3.18 USD/MMBtu on 29 September, +0.28 on the week, near the bottom of a one-year range of 2.54 to 30.72; the Gulf Coast 3-2-1 crack spread 73.63 USD/bbl, +49.37 on the year; ERCOT's day-ahead hub average 37.28 USD/MWh on 4 October against a year's range of 9.08 to 654.03.

## The tables

| Table | Rows | License | Validator | Coverage, archive, Redivis draft |
|---|---|---|---|---|
| `price_board_stats` | 297 | public | pass | done (public dataset's draft, 297 rows counted) |
| `eia_all_futures_prices` | 21,240 | internal | pass | done (internal dataset's draft, 21,240 counted) |

Nothing released on Redivis. Neither table is loaded into Supabase.

## EIA's terms, quoted

From EIA's "Copyrights and Reuse" page, read 5 October 2026:

> U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.

> You may see on our website documents, illustrations, photographs, or other information resources contributed or licensed by private individuals, companies, or organizations that may be protected by U.S. and foreign copyright laws. Transmission or reproduction of protected items beyond that allowed by fair use as defined in the copyright laws requires the written permission of the copyright owners.

EIA's notices on the series themselves: spot prices, "Sources: Refinitiv, an LSEG business"; futures, "Futures Prices: New York Mercantile Exchange (NYMEX)" and "(Futures prices after April 5, 2024, are not available)". The method (`docs/methods/price_board_v4.md`) holds all of it.

## The daily refresh

`warehouse/refresh_board_v4.sh`: the builder and the validator, each under `warehouse/health.py` (retried once, recorded in `erw_health`, never failing a job). **Written, not scheduled:** no workflow and no line of `run_daily.sh` calls it, and a test holds that. It needs no request of its own, because the daily run already refreshes the four tables it reads.

## Checks

- Session tests: `tests/test_session127.py`, 19 tests on real samples (twelve rows of EIA's own answer for natural gas futures; fifteen months of the daily series the board reads, as held on 5 October). They hold: EIA's rows unchanged; a date with no value left out and counted; a value that is not a number stops the pull; Henry Hub's figures as held; every move is the last value less a day actually held; a move whose earlier day is missing is not made; a range needs 180 days; the three spreads by their formulas; MISO not read; the page in review and the other boards untouched; the refresh not scheduled; the tables held and the futures internal.
- Full suite: 1,277 passed, 19 skipped, exit 0.
- Site build exit 0. Route check exit 0: 8 live pages and 117 in review, 0 failed. The page's own check (`site/scripts/check-board-v4.mjs`): 10 of 10, every marked number equal to the copy.
- I looked at the page at desktop width and fixed two things (a percent was shown beside power prices; the summary lowercased "RBOB"). Not looked at on a phone.

## Decisions made without you

- **The futures internal** (above).
- **No new spot pull**: the series were held.
- **The heat rate stays 7.0**, the figure the first board has used since session 7.
- **Five grids, each at the hub the site already calls its main one.** More hubs per grid are held for some grids and are not on this board.
- **No sparkline.** You asked for depth over layout; the range mark is the one drawing.
- **The page reads a copy, not the live set**, because a load is a change under the freeze.

## What is left

1. Your ruling on the futures' license, and on whether the same reading applies to the spot tables.
2. Switching the refresh on and pointing the page at the live set (three lines and a deploy, above).
3. More hubs per grid, if you want them: the tables hold NP15 for California and all ERCOT hubs.
4. A licensed source, for any of the seven greyed rows.
