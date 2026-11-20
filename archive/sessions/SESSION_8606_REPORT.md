# Session 8606 report (portable-laptop, 19 November 2026)

Energy Research Warehouse (ERW). Chain 504: part A again, then part E's done line for the map and for the thirteen regions, in chain 303's form. About 14:15 to 15:00 UTC. Branch `wip/8602-grid-regions` at `eb6bb737c` (landing request row 42, its head moved). Model spend USD 0; no model was called.

## At the top

- Nothing changed that was not meant. The Network shape's markup is not touched: the new decisions fold is inside the map's own frame.
- **The cross-check found something a reader should know, and you may want to rule on.** The map and the panel say PJM was a net exporter of 811 MW late on 16 November. PJM's own total, as it files it with EIA for that hour, is 82 MW. Both are true: the map sums the pairs, each read from one side, and the two sides of a tie do not agree. It differs for 21 of 60 authorities. The page now says so in "Decisions on this map". Default taken: the sum stays, as the Network view has had it.
- A stray command hung a shell once (a bare `python -`); it was stopped, and the commit before it had gone through.

## What was done

- **Part A.** The old laptop's stacks and the region files are on production. Nineteen addresses read there at 1280 and 390 px: every one loads, none is wider than the screen, none shows a page error. Rows 378, 379, 380, 385 and 410 marked seen, with five pictures. 26 rows still wait (five of them new); twenty minutes were up.
- **The map's replication.** What the map draws, read from a built page, against the same figures computed from the snapshot and the boundary file with none of the page's code: 439 of 439 (all 60 regions' hovers, 127 ties, the 10 authorities listed, the width key).
- **The map's cross-check.** Against EIA's own interchange for the hour: each of the 159 pairs is the report EIA publishes, to 1 MW.
- **The regions' replication.** Every figure of the Mix and trade tabs of the thirteen regions: 1,349 of 1,349.
- **The regions' cross-check.** Against EIA's own regional series, three hours a region: 383 of 430 figures the same to 1 MW. It also showed:
  - the file's hour is EIA's period at the hour's end;
  - the files write 0 where EIA publishes no series at all (storage for New York and the Mid-Atlantic, wind for the Carolinas and Florida, coal for New England);
  - California's "other" is EIA's own: minus 10,253 MW in EIA's code OTH at midday on 8 November, its battery code minus 151 MW;
  - four hours differ by more than 100 MW (the Southeast's demand by 1,102 MW on 11 November).
- **On the page:** "Decisions on this map (9)" under the map; five more lines on the regions' decisions fold.
- **For your signature:** a sign-off block in `docs/methods/grid_network.md`, and the pack `docs/reviews/grid-map-regions-signature-pack-2026-11-19.md`, about thirty minutes, no Stata.
- **Data request 551** (the zeros, the four hours).

## What was checked

- `tests/test_session8606.py` 32 passed. The related test files with the five sessions' own: 1,451 passed, 49 skipped, 3 failed, the same three as on main on this laptop.
- On a build with the real files: `check-grid-map.mjs` 50 of 50, `check-network-map.mjs` 31 of 31, `check-grid-regions.mjs` 25 of 25.
- Each replication fails when a page figure is altered (run by hand and held by a test).
- The EIA key is in no output file (searched).

## What to review (after row 42 lands; in the internal view)

1. `https://erw-flame.vercel.app/grid?view=network&shape=map`: open "Decisions on this map" under the map; line 3 has PJM's two figures.
2. `https://erw-flame.vercel.app/grid?region=cal`: open "Decisions on this page" at the foot: twelve lines.
3. On this laptop: `python replication/grid/replicate_map.py` and `python replication/grid/replicate_regions.py`: each ends "... of ... figures met" and exit 0.
4. The pack: `docs/reviews/grid-map-regions-signature-pack-2026-11-19.md` on the branch.

## Not as the chain expected

- Part A: five rows of 26 in its twenty minutes. The rows ask for hovers and clicks by hand; the next session reads more from what is already harvested.
- The data machine answered request 544's months (the files will hold more) and left its other three points as "the page's own". The cross-check then settled two of them by figures; the third (Florida's hours ending on 11 November) is still open and is not asked again tonight.
- No Stata do-file for these two parts: the existing one covers the network's figures, which the map shares.

## Decisions made without you

- The cross-checks read EIA's open data API with the ERW's own key, as the connectors do. About 160 requests in all, half a second apart. The key is never printed or written.
- The decisions fold is inside the map's frame, not under the tool, so the Network view's page is as it was.
- The replications compare what a browser reads from a built page, not what the page's functions return.
- EIA's codes are folded into the eight sources as the contract folds them.

## Needs the key

- Nothing. (The two cross-checks need `EIA_API_KEY`, which this laptop has.)

## For Samuel's ruling

The signature pack lists eight, each with its default taken. The three new today:

- **A region's net exchange: the sum of its pairs, or the authority's own total beside it** (PJM: 811 against 82 MW). Default taken: the sum, the difference said in the decisions block.
- **California's "other" far below zero at midday:** should the page say so, and say what is in it? Default taken: nothing beyond the figure and the Storage row's hover.
- **The average day's chart draws a thin line to zero where a source crosses zero.** It is the seven grids' own chart. Default taken: left as it is.
