# Session 8602 report (portable-laptop, 19 November 2026)

Energy Research Warehouse (ERW). Chain 504: part A again, the map on the data machine's real boundary file, and part C, the whole country in the Grid tool. About 11:40 to 12:30 UTC. Branch `wip/8602-grid-regions` at `0b3ccff0a` (it holds `wip/8601-grid-map` whole), landing request row 42. Model spend USD 0; no model was called.

## Part A: the old laptop's rows

Ten rows of `docs/state/browser_reads_wanted.md` had come back to `wanted` since 10:40. Seven were read on one production build of the old laptop's five branches merged in a local worktree (never pushed), internal view, 1280 and 390 px:

- **341 fixed** (`/impact`, the A and B table on a phone): 390 px wide; each figure inside its own third, broken at a space.
- **363 fixed** (`/storage`, the newest whole month): US Lower 48 1,612,269, ERCOT 824,477, CAISO 1,420,460.50, each "2026-10" and 31 days; ISO-NE, MISO and SPP show September, 30 days.
- **366 fixed** (`/supply`, two grids side by side on a phone): 390 px wide; the table scrolls inside its box; no white band.
- **362 fault** (`/prices`, the second hub): on a built site every hub price page of `wip/alt-prices-3` answers "This page couldn't load" (`DYNAMIC_SERVER_USAGE`), with or without a second hub. The page reads its address while the route stays prerendered. A dev server, which the earlier read used, does not show it.
- **377 seen**, **381 and 382 seen in the state before the data files** (the event pages' section "The whole country" reads "not built yet"; outside it the seven pages are production's line for line). The state after the files is still `wanted`; 378 to 380 wait for the files.
- Pictures: `docs/reviews/ruling-alternatives/` (four new) and `docs/reviews/browser-reads-2026-11-19/` on main.

## The map on the real boundaries

- The data machine's `site/data/regions/ba_boundaries.json` (HIFLD Control Areas, 67 boundaries) was read from its branch at 11:45 and landed on main at 12:10. The map's reader takes it as it stands, with no change of code.
- **60 of the network's 70 authorities are now drawn** (44 with the county file) and **127 of the hour's 148 ties**. Ten are listed under the map with no boundary: the seven operators of Canada and Mexico, and Black Hills Energy, Sikeston and SPP's western area.
- Both checks pass on it (44 of 44; 31 of 31); the map still answers in about 0.4 s. The pictures in `docs/reviews/grid-map-2026-11-19/` on `wip/8602-grid-regions` are retaken on this file.

## Part C: what a reader of `/grid` can do once the region files are on the site

- **Choose any of EIA's thirteen regions** under the seven grids, the six never drawn before among them (the Southeast, Florida, the Carolinas, Tennessee, the Northwest, the Southwest). A region has its own address (`/grid?region=se`) and the tool's four tabs.
- **Mix:** the latest hour held, the last 35 days hour by hour, the average day of any month or year, the shares by source, one calendar month year after year. The seven parts of a grid's tab that a region's file does not hold (a hub price, forecasts, records and the rest) are drawn blank, "not held for this region", each with its reason on hover.
- **Gravity:** the power exchanged with each neighbouring region by month, from both sides' reports, with the gap. **Network:** the region's balancing authorities as links over the network. **Clean:** three parts blank with their reasons.
- **From an authority to its region:** a panel's new line "EIA region" opens the region; the map's hover names it.
- **Texas, New York, New England, the Mid-Atlantic:** the hover says in the data machine's own sentence why the region and its grid differ.

## The state today, plainly

- **The region files are not on main** (`index.json`, `mix/`, `trade/`): only the boundaries are. So today the new row under the grids reads **"EIA region: not built yet"**, with the file's name on hover, and the tool is otherwise as it was. That state was seen at 1280 and 390 px (`docs/reviews/grid-regions-2026-11-19/`).
- The region tabs themselves were seen in a browser only on the tests' own fixture (the contract's form, figures that are not a region's). Those pictures are not in the review folder. No figure of a real region has been seen by this laptop yet.
- When the files land, no code changes; `site/scripts/check-grid-regions.mjs` reads the same files the server reads and checks the page's figures against them.

## What was checked

- The seven grids and the Lower 48 on their four tabs, a build of main against the branch's: **32 pages, 6,423 lines and every checked figure the same.**
- `tests/test_session8602.py` 20 passed, `tests/test_session8601.py` 23. `check-grid-regions.mjs` 4 of 4 as main stands, 21 of 21 with the fixture copied in for the run and removed after.
- The 101 test files that name a changed module: three fail, the same three that fail on main on this machine (`test_session143.py` and `test_session148.py`, their Node tests; `test_session7203_allgrids_read.py`, row 10).

## Not as the chain expected

- A first run of those 101 files found four failures that were this branch's, all fixed before the request: the line that tells the server which files to carry had moved a line session 138's test reads; the line that draws the network had gained a prop two older tests pin (the regions now reach it another way, and the line is as it was); the brand test's list of who may draw the Mix tab's pieces did not know the new file (one line added to that test).
- A link from a region's list of authorities did not open the panel when followed inside the page (the network restores its view from the address once). Fixed; found by the browser check.

## Decisions made without you

- A region has its own word in the address (`region=`), not the grid's word: every address shared before reads as it did.
- "Clicking a region on the map or the network opens it": what is drawn there is balancing authorities, not regions. A click still opens the authority's panel; the panel's new line opens its region.
- On the Gravity tab a region shows its trade table and chart, not the gravity shape (that shape is of the seven grids around the Lower 48).
- With a region in view the Ask panel is the Lower 48's and says so.
- The fixture's mix file is cut from the site's own ERCOT file so the drawing meets a real file's shape; it is labelled a fixture in the file and never shipped.

## Needs the key

- Nothing. Ask was not touched.

## For Samuel's ruling

- Nothing new from this session. The two of session 8601 stand (the color at the hour shown; data request 540).
