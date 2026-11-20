# Session 8614 report (portable-laptop, 19 November 2026)

Energy Research Warehouse (ERW). Chain 504, part E: a second reader's read of the resource map, and the phone read with a finger. About 17:17 to 17:55 UTC. Branches `wip/8603-resources` at `21e16543d` (landing row 43) and `wip/8602-grid-regions` at `ca7ba644e` (row 42). Model spend USD 0; no model was called.

## At the top

- Nothing changed that was not meant.
- **A fault on production since the resource map was built, now fixed on the branch: on a phone, a tap on the map shows no value.**
  - Measured: the card comes up 166 ms after the finger goes down and is taken off 11 ms later.
  - Cause: a finger that lifts is also a pointer that leaves the map, and the leave took the card off.
  - Why it was missed: every read at 390 px, mine included, pointed with a mouse. That is my miss.
- **The same on a region's hour by hour chart** (session 8605's, on production since stack d): a tap showed no card. Fixed on the branch.
- The map of balancing authorities was built for a finger from the start. Tested again: nothing to change.

## What was done

- **Part A.** 5 rows still wanted (418 to 422); the old laptop's three branches are not in main.
- **The check's failures that came and went, traced to the page.** The map's record of what it drew was written by a timer, sometimes before a late frame, and then stayed wrong. No reader sees the record; the check does. The rest now draws a pending frame first.
  - The check holds every frame back 400 ms: failed before the change, passes after. Three runs in a row clean.
  - It also reads both lists of layers since session 8613, so the coal fields are switched on by it.
- **Five more cases on the resource map** (rows 9 to 14 of `docs/reviews/resources-read-2026-11-19.md`):
  6. The planner, offshore wind off New Jersey. Answered: lease OCS-A 0570, 43,439 acres; the planning areas said to be rescinded.
  7. The trader, hydropower on the Columbia. Answered: the Lower Klickitat watershed, 18.3 MW in 17 reaches.
  8. The student, the sun in Alaska and Hawaii. Answered for Kansas and Hawaii; Alaska is blank north of 60 degrees north.
  9. The siting analyst, geothermal in northern Nevada. Answered; the plants' fuel switch keeps geothermal alone, 164 units.
  10. The battery developer, West Texas wind. Answered in figures, with raw column names for words; on a phone, not at all until the fix.
- **Three site faults fixed, each with a test:**
  - a finger's tap shows the value and it stays (until the next tap, a drag, or a map button);
  - on a map narrower than 480 px the card takes the map's width. It was a column 160 px wide, longer than the screen;
  - the record at rest (above).
- **The regions' chart:** a finger's press reads the hour; the card stays. One test file, one check.
- **Data request 553:** plain words and units for the hover fields of two point layers (the wind sites and the hot-water systems).

## What was checked

- Resources branch: the map's own tests 132 passed; `test-resources.mjs` 92 of 92; `check-resources.mjs` 99 of 102. The three that fail are the datacenter overlay, held for a license, as on main.
- Grid branch: the eleven sessions' own tests 175 passed; `check-grid-regions.mjs` 30 of 30; `check-grid-map.mjs` 53 of 53.
- Each new check was run on the build before its fix and failed there.
- Pictures: `docs/reviews/resources-2026-11-19/` (`case6` to `case10`, two of the phone) and `docs/reviews/grid-regions-2026-11-19/region_car_mix_390_tap.png`.

## What to review (after the rows land; in the internal view, on a phone)

1. `https://erw-flame.vercel.app/map?tab=resources&on=wind_speed_100m`: tap the map. A card with the wind speed stays.
2. `https://erw-flame.vercel.app/grid?region=tex`: tap the chart of the last 35 days. The hour's card stays.
3. On a wide screen, the same two: nothing differs.

## Not as the chain expected

- The first cause I wrote for the check's failures was wrong (a later file moving the rest back). The second run's own lines showed the right one: the hover read the finer level's value while the record said the coarser.
- The desk's stack e (with rows 42 and 43 as they stood at 16:42) was at the gate from 17:33 and had not landed at 17:54.

## Needs the key

- Nothing.

## Decisions made without you

- A tap's card stays until the next tap, a drag or a map button. No close button was added.
- The card's full width on a narrow map (under 480 px). A wide screen is as it was.
- The hover words of the two point layers are left as the files' column names until the data machine names them (request 553). I did not write units of my own.

## For Samuel's ruling

- With a sun layer on, Alaska is blank north of 60 degrees north (the source's file ends there). Should the hover say so where the reader points? Default taken: left; the layer's entry under the map says it.
- A card that stays on a phone: should it have a close mark? Default taken: none.
