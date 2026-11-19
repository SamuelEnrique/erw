# The natural resource map, read as its readers would read it

Energy Research Warehouse (ERW). Session 8608 (chain 504, the portable laptop), 19 November 2026, about 15:45 to 15:55 UTC. The map is the Resources tab of `/map`, opened by `/resources`, as `wip/8603-resources` builds it with the data machine's coal layer copied in from its branch (`wip/c501-desk-b`; the layer is not on main yet). Each case was taken in a real browser on a build, in the internal view, at 1280 px (cases 3 and 4 at 390 px too), by `runs/c504_resources_read.mjs`: the map opened by its address (the layers on, the zoom, the centre), the pointer at the place asked about and at three places around it. What the page said is in `runs/c504_resources_read2.out`; the pictures are `docs/reviews/resources-2026-11-19/case*.png`.

The question of each case: can the reader get the answer without leaving the page, without a figure that contradicts another on the page, and without a word they would not know?

## The five readers and their cases

1. **A transmission planner.** "The wind on the Great Plains, in central Nebraska: how strong is it, and what is waiting in the interconnection queue there?" Wind speed at 100 m, planned plants and the queue, centred on 41.5 N, 99.5 W.
2. **A power trader.** "The Permian: where does the basin lie, which plays are in it, and how large is each?" The basins and the plays, centred on 31.8 N, 102.5 W.
3. **A student.** "Where is the coal in Appalachia, how old is it, and of what rank?" The coal fields, centred on 38.0 N, 81.5 W, at 1280 and 390 px.
4. **An AI lab's siting analyst.** "A campus at Phoenix: how much sun, any hot water underground, which plants run nearby, and which datacenters?" Global horizontal irradiance, the known hydrothermal systems, operating plants and datacenters, centred on 33.45 N, 112.07 W, at 1280 and 390 px.
5. **A battery developer.** "Central Nevada: how much direct sun, and how much is asked for in the queue by county?" Direct normal irradiance and the queue, centred on 38.5 N, 116.5 W.

## What each reader got

- **Case 1.** Answered. At 41.50 N, 99.50 W the wind averages 8.496 m/s at 100 m (a cell of 0.05 degrees, 2007 to 2013), and the county's queue reads "Custer, NE: 3 requests, 355 MW asked for. A county, not a site." Lancaster County to the south-east: 18 requests, 3,306 MW. No planned plant lay under the pointer.
- **Case 2.** Answered for what the map is: outlines and their areas. The Permian basin is 61,763.2 square miles; 150 km to the west the hover names the Abo-Yeso play, 4,471.8 square miles, inside it. At the centre asked about the hover names the basin and no play: the file's plays do not cover that point. Not answered, and not the map's to answer: what the plays produce.
- **Case 3.** Answered. "Appalachian Region (Eastern) (coal field): 141,224.7 square kilometres. Province: Eastern; Name: Appalachian Region; Age: Pennsylvanian-Permian; Rank: Medium and High Volatile Bituminous. Vintage: 2013. U.S. Geological Survey (USGS)." At 390 px nothing is wider than the screen. The area is in square kilometres where the basins' and plays' are in square miles (row 2).
- **Case 4.** Half answered. The sun: 5.784 kWh per square meter a day. No known hot-water system at the point. The nearest plant under the pointer: "Phoenix Airport Rental Car Center: Solar, 1.6 MW. Operating, AZ, 2012." The datacenters are not drawn: the table is held for a license, and the switch says so with its reason. Before the fix of row 1 nothing on the page said that 33.45 N, 112.07 W is in Arizona.
- **Case 5.** Answered. 7.116 kWh per square meter a day of direct sun at 38.50 N, 116.50 W, and "Nye, NV: 8 requests, 2,044 MW asked for."

## The rows

| # | Case | What the reader met | What it is | State |
|---:|---|---|---|---|
| 1 | all | The hover gave a latitude and a longitude and no place: "33.45 N, 112.07 W" | Site gap: only the queue's switch, when on, named a county | fixed (session 8608): the hover names the state under the pointer after the coordinates ("33.45 N, 112.07 W, in Arizona"), from the states' outlines the map already draws; at sea it names none. `tests/test_session8608.py` |
| 2 | 3 | The coal fields' area is in square kilometres; the basins' and the plays' areas are in square miles | Data: the coal fields' area is the data machine's own, computed on a sphere from the outline; the other two are the publisher's figures | data machine: request 552 asks for the area in square miles too, or the reason for the unit. The page shows each as its file gives it. Done by the data machine (session 8011, on main since 18:10 UTC on 19 November): the area is in square miles, with the square kilometres it is computed from beside it; seen on the page on a build and on production |
| 3 | 3 | In the method note under the map, the coal fields' "What it is not" begins with a file's name: "docs/methods/resource_layers_table.md. An outline of where coal fields lie ..." | Data: the entry's `notes_for_method`, shown as written | data machine: request 552. Done by the data machine (session 8011): the sentence stands alone, the file's name is in a key of its own |
| 4 | 4 | "Datacenters: not read: license needed", with the publishers named | The table is held for a license; a held value is drawn blank with its reason | not a fault |
| 5 | 2 | At 31.80 N, 102.50 W the hover names the Permian basin and no play | The file's plays do not cover the point; the plays' outlines are EIA's general areas | not a fault |
| 6 | 1, 4, 5 | Every hover of a wind or sun layer repeats the file's vintage sentence, three lines of small words under the figure | The page's words since the layers were added (the vintage and the publisher with every value, so that every figure is sourced where it is read) | ruling: for Samuel, whether the sentence could stand once, in the legend. Default taken: left as it is |
| 7 | 3, 4 | Uranium and critical minerals are greyed | The two USGS hosts that serve them refuse automated reading | ruling: for Samuel (a person could download the two files by hand). Default taken: not fetched |
| 8 | 3 | On a phone the hover's card covers a third of the map while a finger rests on it | The card stands beside the finger and goes when the finger lifts | not a fault |

## What the read changed on the page

One site gap fixed at its cause with a test (row 1). Two rows are the data machine's, in one request (552). Two are rulings with the default taken (6 and 7).

## A second read (session 8614)

Session 8614, 19 November 2026, about 17:36 to 17:47 UTC, on a build of `wip/8603-resources` with main's coal layer, by `runs/c504_resources_read2.mjs` (what the page said: `runs/c504_resources_read2.out`; pictures `docs/reviews/resources-2026-11-19/case6*.png` to `case10*.png`). The same five readers, on the layers and the controls the first read did not touch. The phone was then read with a finger, not a mouse (`runs/c504_phone_tap.mjs`, `runs/c504_phone_card.mjs`).

### The five cases

6. **The transmission planner.** "Offshore wind off New Jersey: which lease is where, how large, and what of the planning areas?" The lease areas and the planning areas at 39.3 N, 74.0 W, then "Zoom out" twice.
7. **The power trader.** "The Columbia at The Dalles: how much hydropower is not built, at dams that have none and on streams that have no dam?" Non-powered dams and new stream-reach development at 45.7 N, 121.2 W.
8. **The student.** "How much sun in Alaska and in Hawaii, against Kansas?" Global horizontal irradiance and the three place buttons, at 1280 and 390 px.
9. **The siting analyst.** "Northern Nevada: how favorable is the ground for geothermal, and which geothermal plants already run there?" The two favorability layers, operating plants, and the plants' fuel switches with geothermal alone.
10. **The battery developer.** "West Texas: how good is the wind at the sites the laboratory models, and what is planned there?" Wind capacity factor, biomass and planned plants at 32.5 N, 101.5 W, the move buttons, a phone.

### What each reader got

- **Case 6.** Answered. At the centre: lease OCS-A 0570, Atlantic Shores Offshore Wind Project 2, a commercial lease of 43,439 acres, with BOEM's dates. The planning areas' legend says they were rescinded on 30 July 2025. At sea the hover names no state, which is right.
- **Case 7.** Answered. At the centre: the Lower Klickitat River watershed, 18.3 MW of new stream-reach potential in 17 reaches, with the years the estimate was published. 94 dams and 240 watersheds in view.
- **Case 8.** Answered for Kansas (4.603 kWh/m2/day) and for Hawaii's land. For Alaska the map is blank north of 60 degrees north and the hover says "no value in the source here"; why is in the method note under the map and not where the reader points (row 9).
- **Case 9.** Answered. Class 2 at the centre, class 1 to the north-west; with geothermal alone the address holds `fuel=geothermal`, the count reads 164 operating units, and a sweep of the map names NGP Blue Mountain I, 15.0 MW.
- **Case 10.** Answered in figures, not in words: "72732: 0.4359 ratio; resource: 8.35; capacity ac mw: 282; area developable sq km: 128.3" (row 10). On a phone, not answered at all as the page stood: a finger's tap showed nothing (row 11).

### The rows

| # | Case | What the reader met | What it is | State |
|---:|---|---|---|---|
| 9 | 8 | With a sun layer on, "Alaska" shows the state blank north of 60 degrees north; the hover there reads "no value in the source here" | The source's file for Alaska ends at 60 degrees north. The layer's entry under the map says so ("Alaska south of 60 degrees north"); the hover does not | ruling: for Samuel (should the hover say where the source's file ends?). Default taken: left as it is |
| 10 | 10, 9 | A wind site's hover reads "72732: 0.4359 ratio; resource: 8.35; capacity ac mw: 282; area developable sq km: 128.3"; a hot-water system's reads "Temp C Li", "Vol km3 Mn" | Data: two point layers name no hover fields in the list of layers, so the page falls back on the file's column names. The words and units are the publisher's and are not the page's to make up | data machine: request 553 (the fields' words and units for `wind_capacity_factor` and `geothermal_hydrothermal_sites`, as the hydropower layers have them). Done by the data machine the same evening in a file of its own, `hover_fields_added.json`, in the publishers' words ("Annual average wind speed at the modeled turbine hub-height, meters/second"); the page reads that file where a layer's own entry names no fields (session 8618, with a test). The wind sites' name is the source's `sc_point_gid`, a number with no plain word for it: shown as it was, for Samuel's ruling |
| 11 | 10, 8 | On a phone a tap on the map showed nothing. Measured: the card was put up 166 ms after the finger went down and taken off 11 ms later | Site fault, on production since the page was built: a finger that lifts is also a pointer that leaves the map, and the leave took the card off. Every earlier read at 390 px pointed with a mouse | fixed (session 8614): a touch's leave is let pass; the card of a tap stays until the next tap, a drag, or a press of a map button. The check taps with a finger at 390 px |
| 12 | 10 | On a phone the card stood beside the finger as a column some 160 px wide, longer than the screen with three layers on | Site gap: the card's place was made for a mouse on a wide map | fixed (session 8614): on a map narrower than 480 px the card takes the map's width, under or over the finger; with five layers on it is 782 px tall and is read to its end by scrolling, the card staying |
| 13 | all | The check failed two layers on some runs ("0 cells in view" with the layer on the canvas) | Site fault in the map's own record of what it drew, read by the check and by no reader: the record was written by a timer before a late frame | fixed (session 8614): the rest draws a pending frame before it writes the record. The check holds frames back 400 ms |
| 14 | 6 | At sea, and on a thin strip of coast, the hover names no state ("37.89 N, 75.28 W") | The state outlines are land, simplified | not a fault |

### What the second read changed on the page

Three site faults fixed at their cause, each with a test in `tests/test_session8614_resources.py` (rows 11, 12 and 13). One row is the data machine's (request 553). One ruling with the default taken (row 9). On a build: `check-resources.mjs` 99 of 102, the three that fail the datacenter overlay's license hold.

## The keyboard (session 8615)

Session 8615, 19 November 2026, about 17:56 to 18:03 UTC, on a build. The brand asks that whatever a hover card says be reachable by keyboard (`docs/brand.md`, the hover card). The map was read with the Tab key and the arrow keys alone (picture `docs/reviews/resources-2026-11-19/keyboard_centre_1280.png`).

| # | Case | What the reader met | What it is | State |
|---:|---|---|---|---|
| 15 | all | With the keyboard, the arrow keys moved the map and plus and minus zoomed it, and no value could be read from it | Site gap since the page was built: a value came up only under a pointer | fixed (session 8615): when the map takes the keyboard's focus the card reads the place at the map's centre, marked by a small ring, and reads it again after each move or zoom; it is announced as it changes; a pointer takes the reading back. The check does it with the Tab key and an arrow |
| 16 | all | A reason given on hover as a plain tooltip (the greyed "not held" beside a layer that is not held, a figure drawn blank) does not come up under a finger; a phone has no hover | The site's way of giving a reason everywhere: the browser's own tooltip, which a touch screen never shows (about 1,100 such tooltips across the site's pages, 12 in this map) | ruling: for Samuel (a site-wide matter: should a reason on hover also open on a tap?). Default taken: left as the site has it |
| 17 | all | With the method note under the map open, a screen reader finds two headings of level 1: the page's and the method document's own title | Site gap of session 146: the document is shown inside the page with its headings as written (found by `runs/c504_a11y_probe.mjs`, which also found every control named, every field labelled, no id used twice and no level skipped) | ruling: for Samuel (the level of a document's headings can only be set inside the site's one renderer, `site/lib/markdown.ts`, which every page shares). Default taken: left as it is. A fix tried in session 8615 wrote the levels from the page, round the renderer; the site's rule is that markup reaches a page only through the renderer (tests 177 and 5153), the landing desk's suite caught it, and session 8616 took it out |

One site gap fixed at its cause with a test in `tests/test_session8615_resources.py` (row 15). Two rulings with the default taken (rows 16 and 17). On a build: `check-resources.mjs` 102 of 105, the three that fail the datacenter overlay's license hold.

## Found while replicating a second layer (session 8619)

Session 8619, 19 November 2026. The sedimentary basins were replicated against EIA's own file (199 of 199 figures; `replication/resources/replicate_basins.py`). One thing a reader meets came out of it.

| # | Case | What the reader met | What it is | State |
|---:|---|---|---|---|
| 18 | 2 | One basin's name on the map is "Tx-La-Ms Salt" | Data: EIA writes the basins' names in capitals ("TX-LA-MS SALT", the codes of three states and the word salt), and the layer shows each word with a capital first, which is right for the other 31 ("Fort Worth") and wrong for this one. "Valley And Ridge" has its "And" with a capital for the same reason | data machine: request 554 (the name as a reader would write it, or EIA's own spelling kept). The page shows the name as its file gives it |
