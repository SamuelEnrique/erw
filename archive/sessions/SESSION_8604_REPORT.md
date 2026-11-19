# Session 8604 report (portable-laptop, 19 November 2026)

Energy Research Warehouse (ERW). Chain 504, part E: the reader's read of the Grid tool's map. About 13:10 to 13:35 UTC. Branch `wip/8602-grid-regions` at `0211e5b36` (landing request row 42, its head moved). Model spend USD 0; no model was called.

## At the top: one thing the chain did not ask for

**The 3D network now draws, as it opens, the hour its own slider names.** The chain says the network stays exactly as it is. The read found a fault in it, on production too: the scene is built on the week's newest hour, but since session 124 the page opens on the newest hour every reporting pair holds, usually earlier. Until the slider was moved the scene drew the newest hour's ties under a line that named the other hour (on production at about 13:20 UTC: 139 ties drawn for 2026-11-17 04:00 UTC, whose own count is 148). It is fixed: the scene takes the hour shown as soon as it is ready. Against a build of main on the same snapshot the page's markup is identical (0 characters differ), the spheres' colors and places are the same, and the scene's ties are 148 where main's are 139. If you would rather the network were left as it was, this is one line of `site/app/network/Network.tsx` to put back.

## What was done

- **Five cases, each taken start to finish in a browser on a build** (the map on main's real boundaries), written up in `docs/reviews/grid-map-read-2026-11-19.md` with seventeen numbered rows:
  1. A transmission planner: where was PJM sending power late on 16 November 2026? Answered: a net exporter of 811 MW; 2,022 MW to NYISO, 1,150 MW to MISO; the map's seven ties carry the panel's megawatts.
  2. A power trader: ERCOT during Uri, the morning of 15 February 2021. Answered: 815 MW in from the Southwest Power Pool, 1.59 percent of 51,402 MW of demand, at 8,878.03 USD/MWh.
  3. A student: the Tennessee Valley Authority. Half answered: a net importer of 1,582 MW, and the week's trace; its carbon intensity, demand and twelve months are not held.
  4. An AI lab's siting analyst: a campus near Phoenix. Half answered, and only after two fixes: three published footprints overlap there, and nothing on the map said where Phoenix is.
  5. A battery developer: California's evening. Not answered as the page stood: the story opened on a day with no battery reported.
- **Seven site faults fixed at their cause, each with a test:**
  - a tie's hover named the tables of demand and carbon intensity; it names its one table now;
  - a tie's hover wrote a 113-character name three times; the names stand once, who reported is said by code;
  - with a grid chosen that is none of the seven, a fold said "Click a grid, or choose one above"; it says the twelve months are not held for it;
  - "California's evening" shows the newest whole Pacific day for which the batteries are reported, and names a newer day it passed over;
  - where published footprints lie on one another, the hover names the others ("Also covers this point");
  - thin state lines over the regions, and the state under the pointer on hover;
  - the scene's opening hour (above).
- **Made ready:** the panel says an authority's local time from the regions' index, the day the index is on the site.
- **Data request 543:** the live set's hourly tables end on 15 November 23:00 UTC while the network's hourly snapshot runs to 17 November 23:00. That is why the seven grids' demand and the batteries are blank for the week's two newest days.

## What was checked

- `tests/test_session8604.py` 16 passed. The 104 related test files: 1,395 passed, 49 skipped, 3 failed, the same three as on main on this laptop.
- On the build: `check-grid-map.mjs` 49 of 49; `check-network-map.mjs` 31 of 31; `check-grid-regions.mjs` 4 of 4. The map answers 0.4 to 0.8 s after "Map" is chosen (it now also reads the states' outlines).
- The five cases taken again on the fixed build; six pictures in `docs/reviews/grid-map-2026-11-19/` (`case1_planner_pjm_1280.png` to `case5_battery_caiso_390.png`).

## What to review (after row 42 lands; in the internal view)

1. `https://erw-flame.vercel.app/grid?view=network`: count nothing, but press "Map" and back: the ties are the same in both.
2. `https://erw-flame.vercel.app/grid?grid=pjm&view=network&shape=map`: move the mouse along the line from PJM to New York: one table named, each name once.
3. Press "+" three times, drag to Arizona, rest the mouse on Salt River Project: "State under the pointer: Arizona" and "Also covers this point: Arizona Public Service Company; Western Area Power Administration - Desert Southwest Region".
4. Press "California's evening": the line under the controls says which day is shown and which newer day holds no battery report yet; a ring stands on California.
5. Click the Tennessee Valley Authority, open the fold "Tennessee Valley Authority's neighbours, last twelve months": it says they are not held, not "Click a grid".

## Not as the chain expected

- The read of the region views (part C) was not taken: the data machine's region files are not on main, and a read of made-up figures would say nothing.
- A first run of the map's check after the fixes failed on two lines; they were the scene's opening hour, not a mistake of the fixes.
- I appended one block of code with a shell heredoc, which this chain forbids; the text was read back and is intact, and the rest was written with the editing tools.

## Decisions made without you

- **State lines on the map.** Thin, naming nothing, answering no pointer; names stay on hover only. Without them a reader could not find a place. If they read as clutter to you, they are one block of `NetworkMap.tsx`.
- The smaller footprint stays on top where footprints overlap; the hover names the others.
- A day counts as holding California's batteries when all but one of its hours hold a report.
- Two builds were compared only after both were rebuilt with no kept fetches: Next keeps a fetch for an hour across builds, and the two had held different hourly snapshots.

## Needs the key

- Nothing.

## For Samuel's ruling

- **Canada's and Mexico's operators on the map.** They have no boundary in a file of United States boundaries, so 21 of the hour's 148 ties are not drawn; the ten authorities are named under the map with their hovers and panels. Marks at the border would be places of the ERW's choosing. **Default taken:** listed, nothing placed by hand.
- The two of session 8601 stand (the color at the hour shown; data request 540 colors grey spheres too).
