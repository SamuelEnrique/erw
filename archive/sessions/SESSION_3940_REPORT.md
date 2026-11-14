# Session 3940 report: request 28, no public file for a held grid's board row

Energy Research Warehouse (ERW). Chain 267, data machine (lab-desktop), 14 November 2026 at about 09:35 UTC. Opus 5.5. Model spend USD 0. No request.

- **Read first:** a scratch build of `board_page.py` from the main checkout (`--site-dir` in the scratchpad, 3 min 28 s): 1,225 rows, 1,116 series files, 46 hourly files. Of the held grids it wrote six files only: `isone-h-internal-hub-{spark,heat,dark}.json` and `nyiso-n-y-c-{spark,heat,dark}.json`.
- **The cause:** `build_spreads` drew the spark, heat and dark rows of every operator's main hub without asking `ls.held_grids()`. The battery, peak, day-ahead less real-time and reserve rows already skip a held grid; the other 104 files the review lists are kept by the page keeper from earlier builds.
- **The fix:** a held grid's main hub builds no row data and no series file; one row reads "licensed" with the grid's note, as the power rows do. `test_session207`'s count of four `held = ls.held_grids()` holds.
- **Test 3940:** red on the old code (3 of 4 failed), green now; with the board's eight nearest test files, 89 passed.
- **Not done:** the files already in `site/public/` stay, and the page keeper still keeps them; removing them is the owner's ruling (`docs/reviews/held-public-files-2026-11-13.md`).
- **Request 28 marked done** with this commit when the chain's branch lands.

## Decisions made without you

- **One "licensed" row a held grid in the spark group,** in place of three, as the reserves group has one.

## For Samuel's ruling

- None new (the removal of the 138 files waits on the ruling the review asks).
