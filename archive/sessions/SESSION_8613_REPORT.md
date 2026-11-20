# Session 8613 report (portable-laptop, 19 November 2026)

Energy Research Warehouse (ERW). Chain 504, part E: a second reader's read of the region tabs, then the data machine's files from main. About 16:37 to 17:17 UTC. Branches `wip/8602-grid-regions` at `c527a0bb7` (landing row 42) and `wip/8603-resources` at `4e2b2b54c` (row 43). Model spend USD 0; no model was called.

## At the top

- Nothing changed that was not meant.
- **On production now, in review, until the desk's stack e lands:** the data machine's rebuilt region files arrived with stack d, and production draws them with the page of session 8605.
  - The Carolinas, October 2026: the shares read "Wind 0.0%" and "0" MWh. The file holds blank (no authority there has ever reported wind).
  - The Carolinas' net load by hour, year after year: empty, every figure "not held".
  - Both are fixed by session 8610, which is in stack e (at the gate since 17:08 UTC). No visitor sees the page.
- A merge conflict in `docs/state/landing_request_portable.md`: the desk wrote rows 42 and 43 while I moved row 42's head. Resolved by hand: the desk's states kept as written, my head and note put back. No force, no amend.

## What was done

- **Five more cases on the region tabs** (rows 39 to 41 of `docs/reviews/grid-map-read-2026-11-19.md`):
  11. The planner, New England and Canada in January 2026. Answered: 951,533 MWh from New York (New York's report: 953,454), 184,354 MWh from Canada.
  12. The trader, the Midwest over 2025. Answered: natural gas 35.4 percent, coal 31.7, wind 13.6, nuclear 12.8.
  13. The student, New York in July across nine years. Answered for the load; not for how clean (the Clean tab is blank, request 540).
  14. The siting analyst, from Central to the Southwest to ERCOT. Answered: the tab is kept.
  15. The battery developer, Texas's batteries hour by hour. Answered: charging 2,622 MW at 18:00 UTC, discharging 5,213 MW at 00:00 UTC (6 and 7 November).
- **Two gaps fixed, each with a test:**
  - the trade tab offered the newest thirteen months of the file's 101. It now has a row of years, back to 2018;
  - a year's shares said "301 days held" and not of which months. They now say "in 10 of the year's 12 months" and name the two not held.
- **Main merged into both branches** (the desk's stack d landed at `d89580bd3` about 16:50 UTC).
  - Regions, on the rebuilt files: the check 29 of 29. The Carolinas' wind is blank in both tables with why; the net load says it is without wind.
  - The replication, read again: 1,483 of 1,483. The cross-check against EIA's own series, read again: 388 of 439 to 1 MW (383 of 430 on the first files).
  - Resources: one conflict, in `tests/test_session8603.py`, where the desk and I had each widened the same guard. Both rules kept.
  - The coal fields are main's file now: 602 fields drawn, square kilometres, name and area on hover.
- **Two faults in my own checking tools, found by the merge and fixed:**
  - the replication compared an old read of the page with the new files (403 "not met") because only the index's stamp was looked at, and the index was not rebuilt. The page read now keeps each file's stamp, and the comparison stops when one changed;
  - `check-resources.mjs` read the first list of layers alone, so it never switched the coal fields on. It reads both now: 99 checks where there were 97.
- **Production read at 1280 and 390 px** after stack d: main's own checks, the regions 25 of 25, the map 49 of 49. Four pictures in `docs/reviews/production-reads-2026-11-19/`.

## What was checked

- Grid branch: the ten sessions' own tests 168 passed; the related files 1,504 passed, 3 failed (143, 148, 7203: they fail on main on this laptop). Type check clean.
- On a build of the grid branch: `check-grid-regions.mjs` 29 of 29, `check-grid-map.mjs` 53 of 53, `check-network-map.mjs` 31 of 31.
- Resources branch: the five sessions' own tests 55 passed; `test-resources.mjs` 92 of 92; `check-resources.mjs` 96 of 99. The three that fail are the datacenter overlay, held for a license, as on main.
- Part A: 5 rows still wanted (418 to 422); the old laptop's three branches are not in main yet.

## What to review (in the internal view)

1. Now: `https://erw-flame.vercel.app/grid?region=car`: the two production faults named at the top.
2. After row 42 lands: `https://erw-flame.vercel.app/grid?region=ne&view=gravity`: the row of years; press 2018.
3. After row 42 lands: `https://erw-flame.vercel.app/grid?region=midw&period=2025`: the line under the shares.
4. After row 43 lands: `https://erw-flame.vercel.app/map?tab=resources&on=coal_fields`: the coal fields.

## Not as the chain expected

- The data machine rebuilt the mix files without rebuilding the index, so `index.json` says 12:16 UTC and the mix files 14:52. The page is right; the replication's last line still prints the index's time.
- On production, `check-resources.mjs` failed two layers that pass on the build ("0 cells in view" for one sun layer and one hydropower layer). They differ by run and passed on the next layer of the same kind. Not yet traced: it may be the check's wait, or a layer drawn late.

## Needs the key

- Nothing.

## Decisions made without you

- In the conflict on the landing file, the desk's words win for the state cells; mine for the head and the note.
- In the conflict on test 8603, both rules stand: a file is the data side's when a listed layer's id begins its name, or when a listed entry names it with its source.
- The count in the regions' decisions fold ("388 of 439") is now tested against the kept file, so it cannot drift from it.
- The chart of trade still draws the newest 36 months whatever month is chosen (row 41, not a fault: its title says its span; older months are in the table).

## For Samuel's ruling

- Should the chart of trade follow the year chosen (2018 shown, 2018's months drawn)? Default taken: the newest 36 months, as its title says.
- The index's stamp: should the page's foot give each file's own time where it differs from the index's? Default taken: the page shows each file's own time already; nothing changed.
