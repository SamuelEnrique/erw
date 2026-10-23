# Session 1116 report: the price board's held rows and stale closes

23 October 2026, 18:29 to 18:45 UTC, on samueloldlaptop, unattended, on `wip/1116-board` (cut from `wip/1112-ask`, while the landing gate of sessions 1108 to 1112 ran). Chain `queue/done/075-morning-23-october-code-ask-board.md`. Taken before sessions 1113 to 1115, which need a build and a model run after that landing. Model spend USD 0. No database read, no web request.

## Read these first

- `site/lib/board.ts`: `holdRows`, `heldNote`, `closeAge`, `STALE_DAYS`.
- `docs/methods/price_board.md`, "The held rows and the stale closes".

## What was done

- **A gap found: 94 rows of held figures on the board.** The builder holds ISO-NE's and NYISO's hub rows, but their on-peak and off-peak rows, spark and dark spreads, day-ahead less real time, battery spreads, NYISO's ancillary prices, their week rows and spikes were drawn with figures, from tables "license needed" for those grids since 21 October (`price_board_peak_offpeak`, `price_board_spreads`, `nyiso_as_prices`, `iso_hub_prices_history`). Every such row is now "license needed" in place, its name, label, group and tags kept and every figure dropped, with the hold's words on hover; the week's table has one line for each held grid, as MISO's and PJM's have. The hold is applied on the server (`site/app/board/page.tsx`), so no held figure is in the page's payload; the grids held are the status file's on the build day.
- **MISO's pause in the tip**: its rows already say "paused while terms are reviewed" with the pause's reason on hover; unchanged.
- **Every close's age** is in the hover of its date ("3 days before the board was built on 23 Oct 2026"), counted as the Digest counts its fuel closes (session 804). **Stale** past 10 days for a daily series (session 304's ruling), 17 for a weekly, 132 for a monthly: a small "stale" mark beside the date, on the wall and in the top tiles. On today's file: SPP's 14 ancillary rows (3 October), CARB's 2 weekly credit rows (14 September) and the monthly series a publisher stopped.
- **An old test brought to the data**: `site/scripts/test-board.mjs` expected five grids with a priced main hub; since the builder's hold there are three (ERCOT, CAISO, SPP), and the test failed on main before this session. It now counts the grids the file prices.

## What to review

1. Open `/board` on the internal view, fold open "Power, on-peak and off-peak": ISO-NE's and NYISO's rows read "license needed"; hover one for the reason.
2. Fold open "Ancillary services, day-ahead": SPP's rows carry "stale" beside 3 Oct; hover the date for its age.
3. "The week, by hub": the lines "ISO-NE hubs" and "NYISO hubs", "license needed".

## Checks

- `node --import ./scripts/alias-register.mjs scripts/test-board-1116.mjs` (in `site/`): exit 0, 5 of 5.
- `node --import ./scripts/alias-register.mjs scripts/test-board.mjs`: exit 0, 11 (exit 1 on main before, at the headline's grid count).
- `python -m unittest tests.test_session1116 tests.test_session132 tests.test_session240 tests.test_session304 tests.test_session168_board`: exit 0, 60 tests.
- `site/scripts/check-board.mjs` now checks that the held grids' rows are blank with "license needed", that none of their figures is in the page's HTML, and that every stale row shown is marked: run on the build of the landing (below).
- `npx tsc --noEmit`: no error in a changed file (the 12 it prints are Next's generated route types, absent before a build).
- Em dashes in the changed files: 0. Screenshots at 1280 and 390: taken on the landing's build, under `docs/brand/review-1116/` (below).

## The landing

With sessions 1113 to 1116 (below).

## Decisions made without you

1. **The board holds every row of a held grid, not only its hubs**: the status file holds the derived tables for those grids, so the board does too. This changes what the internal view draws on 94 rows (the page is in review: a visitor sees the in-review page before and after). Reversible: one call in `page.tsx`.
2. **The thresholds** (10, 17 and 132 days) rest on session 304's ruling for daily series and on EIA's publishing lag for the others. Reversible: one line, `STALE_DAYS`.
3. **The stale mark is drawn, never a figure withheld**: a stale close stays on the board with its date, as the method's "nothing is filled" asks.

## For Samuel's ruling

- The workbench's series files of the held grids (`site/public/board/s/isone-*.json`, `nyiso-*.json`) are still written by the builder and served at their addresses, though no row opens them: holding them is the builder's, on the data machine (`warehouse/derived/board_page.py`). Recommendation: the builder writes no series file for a grid the status file holds.
