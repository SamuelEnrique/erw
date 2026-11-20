# Session 8617 report (portable-laptop, 19 November 2026)

Energy Research Warehouse (ERW). Chain 504, part E: the 3D network read under a finger on production. About 19:19 to 19:24 UTC. Branch `wip/8602-grid-regions` at `6ebefa10a` (landing row 42). Model spend USD 0; no model was called.

## At the top

- Nothing changed that was not meant. No code changed this session.
- The laptop is still short of memory (about 1.7 GB free of 16; the memory is held by the laptop's other programs, none of them this chain's). No build, no local server and no whole suite since 19:00 UTC. What that leaves unproven is in session 8616's report, under "To finish".

## What was done

- **Part A.** 5 rows still wanted (418 to 422); the old laptop's three branches are not in main.
- **The 3D network under a finger, at 390 px, on production.** Every read of it at that width had pointed with a mouse.
  - It works. The scene is fetched when the reader scrolls to it (on the page 270 ms after); a tap on a sphere opens its panel; the address names it; nothing scrolls sideways; "Close" closes it.
  - Two things a phone reader meets, both the centerpiece's own, left for your ruling (rows 43 and 44 of the review).
- A picture: `docs/reviews/grid-map-2026-11-19/network_390_tap.png`.

## What was checked

- The grid branch's twelve sessions' own tests: 182 passed.
- Nothing else: there was no code to check.

## Needs the key

- Nothing.

## Decisions made without you

- The centerpiece is read and not touched, as the chain says.
- With memory short, the reads go on against production, one small browser at a time, and nothing is built.

## For Samuel's ruling

- On a phone the foot of the 3D scene reads "Left-click: rotate, Mouse-wheel/middle-click: zoom, Right-click: pan". It is the drawing library's own hint, for a mouse. Switch it off, or say it for a finger? Default taken: left.
- The panel's "Close" is 24 px tall on a phone; the brand asks 44. Default taken: left (the panel is the network's own).
