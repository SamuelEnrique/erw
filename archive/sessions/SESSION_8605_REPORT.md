# Session 8605 report (portable-laptop, 19 November 2026)

Energy Research Warehouse (ERW). Chain 504, part E: the reader's read of the Grid tool's region tabs, on the data machine's real files. About 13:40 to 14:20 UTC. Branch `wip/8602-grid-regions` at `e97d4614a` (landing request row 42, its head moved; the desk gates it next). Model spend USD 0; no model was called.

## At the top

- Nothing changed that was not meant. Nothing of the seven grids' tabs or of the 3D network is touched by this session.
- **A fault of my own, session 8602, found and fixed.** The region's chart "hour by hour: the last 35 days" was unreadable on real figures: a comb of vertical lines. I had seen it only on the tests' made-up fixture. It is now a chart of its own, one column an hour.
- One commit was pushed to the branch before its tests were read (a row's state used a word the session 8604 test does not know). Corrected in the next commit, 83 of 83 then. The branch is not landed, so nothing reached main.

## What was done

- **The region files reached main at about 13:35 UTC** (chain 501's desk landed rows 41 and 42, `ce36c2541`). Main merged into the branch and built. The page's own readers take all thirteen files: 13 regions, 81 balancing authorities.
- **Five cases on the real files**, in a browser on the build, rows 18 to 30 of `docs/reviews/grid-map-read-2026-11-19.md`:
  1. The planner, the Mid-Atlantic's trade in November 2026. Answered after a fix: net exports of 595,806 MWh to New York, 471,694 MWh to the Midwest.
  2. The trader, Texas in July 2025. Answered: natural gas 45.1 percent, wind 19.2, solar 15.1.
  3. The student, Tennessee. Answered for the mix, which the map could not give: nuclear 41.6 percent in October 2026. Carbon intensity is still not held.
  4. The siting analyst, the Southwest. Half answered: the region's mix and its ten authorities; not one authority's own mix.
  5. The battery developer, California. Not answered: CAISO files no battery series with EIA, and the Storage row (6 MW) read as if it were California's batteries.
- **Six site faults fixed at their cause, each with a test:**
  - the hour by hour chart (above);
  - months absent from a file are counted under the chips and named on hover, with the data machine's rule (California: 22 of 83);
  - "No month from January 2026 to October 2026 is held" for the Northwest, and the like for the Southwest and Florida;
  - a part of a month is said on the trade tab ("at most 336 of its 721 hours");
  - the Storage row says on hover that CAISO, NYISO or PJM files no battery series, for the three regions that hold one;
  - the trade chart's month labels lay on one another on a phone: a label a year.
- **Data request 544**: California's "Other" below zero at midday, storage written as zero for New York and the Mid-Atlantic, Florida's hours ending on 11 November.

## What was checked

- `tests/test_session8605.py` 24 passed. The related test files with the four sessions' own: 1,419 passed, 49 skipped, 3 failed, the same three as on main on this laptop.
- On a build with the real files: `check-grid-regions.mjs` 25 of 25 (the Carolinas' figures on the page equal to the file's), `check-grid-map.mjs` 49 of 49, `check-network-map.mjs` 31 of 31.
- Seen at 1280 and 390 px; twelve pictures in `docs/reviews/grid-regions-2026-11-19/`.

## What to review (after row 42 lands; in the internal view)

1. `https://erw-flame.vercel.app/grid?region=cal`: the chart of the last 35 days reads as days, with red below zero at midday. Rest the mouse on "Storage" in the first table.
2. Same page: under the month chips, "22 of the 83 months ... are not held"; rest the mouse on it.
3. `https://erw-flame.vercel.app/grid?region=nw`: "No month from January 2026 to October 2026 is held".
4. `https://erw-flame.vercel.app/grid?region=mida&view=gravity`: under the table, "November 2026 is a part of a month here".
5. `https://erw-flame.vercel.app/grid?view=network&shape=map`: click the Tennessee Valley Authority, then "EIA region" in its panel: it opens Tennessee.

## Not as the chain expected

- The data machine is already changing the rule that leaves months out (session 8009, on its own branch): the Mid-Atlantic will hold 95 months where it holds 40. The counts on the page will fall by themselves when that lands.
- The data machine answered request 542 in part: the coal fields exist as a layer, in a new file beside the manifest. The resource map does not read that file yet. Next session.

## Decisions made without you

- The new hour by hour chart draws a source below zero down from zero, by the rule the mix library already has for the average day.
- The Storage row's figure is not changed or blanked; only the hover is added. Whether a zero should be blank is asked of the data machine (544).
- I did not write on the page that California's batteries are inside EIA's "Other". The figures suggest it; no document of the ERW says it.
- The landing row stays one row (42) with a moved head, not a new row: the branch is the same and only grew.

## Needs the key

- Nothing.

## For Samuel's ruling

- **The average day's chart draws a thin line down to zero where a source crosses zero** (solar at dusk, storage). It is the seven grids' own chart, the same on CAISO's Mix tab today. Changing it changes the seven grids' tabs. **Default taken:** left as the grids have it.
- Requests 540 and 541 came back from the data machine as yours: both change an existing page file, which chain 501's rule forbids. Default on both: left as it is.
