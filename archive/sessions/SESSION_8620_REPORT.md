# Session 8620 report (portable-laptop, 19 November 2026)

Energy Research Warehouse (ERW). Chain 504, part E: two reads on production. About 19:49 to 19:52 UTC. Branch `wip/8602-grid-regions` at `cd7a504d4` (landing row 42). Model spend USD 0; no model was called.

## At the top

- Nothing changed that was not meant. No code changed this session.
- Memory came back at about 19:48 UTC (3.4 GB free). I had been told not to start the three stopped jobs again on my own (the whole suite, the two local servers), and have not. What that leaves unproven is in session 8616's report, under "To finish".

## What was done

- **Part A.** 5 rows still wanted (418 to 422); the old laptop's three branches are not in main.
- **The site's shared charts under a finger, on production** (a region's Mix tab at 390 px): the average day's chart and the year after year chart each put their card up on a tap and keep it. So the hour by hour chart was the only chart of the regions' tabs that did not, and its fix (session 8614, waiting at the desk) follows the same behaviour.
- **How long the map takes to open, on production**, three tries each:
  - from a press of "Map" on the open Network tab: 905 ms the first time (its code and the boundary file are fetched then), about 200 ms after;
  - from a cold open of the map's own address: 0.7 to 1.1 seconds, at 1280 and at 390 px, with its 60 regions drawn.
- The method note has both.

## What was checked

- The grid branch's twelve sessions' own tests: 182 passed. There was no code to check.

## Needs the key

- Nothing.

## Decisions made without you

- Nothing new.

## For Samuel's ruling

- Nothing new.
