# The energy project map (`/map`): the model audited as a hostile expert would

Session 10216, 26 November 2026, chain 710 (part D), the old laptop. Read as a developer's siting analyst, who would pick a site with this map and wants to find it wrong, and as a transmission planner, who reads it for where generation sits against the grid. In the form of `docs/reviews/queues-model-audit-2026-11-26.md`.

- Nothing changed on main but this file and its folder of evidence (`docs/reviews/map-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no request to any service.
- Each finding's test is on its own branch, `wip/audit-map-<n>`. Branches that change only words are for landing (the rows at the foot), also merged together as `wip/audit-map-words`; a branch whose fix would move a figure carries the test only and is not for landing.
- Not repeated: the read of 16 November (`docs/reviews/map-read-2026-11-16.md`: "Near a point", the list, the county point said, ERCOT's status in the list, a planned unit and its queue position both drawn, Project Matador's grid), the done-line faults of 16 November (`map-faults-2026-11-16.md`: the copy's age, the cut ids, the rounding of the queue's MW, the held tables drawn), the two ruling files of 17 November (`ruling-impact-map-2026-11-17.md`, `ruling-alternatives-map-2026-11-17.md`), and tonight's queue audit (`/queues`, `/queues/places`). They are cited where they bear.

## In short

- **The arithmetic is right.** An independent restatement written from the method note with the standard library (`restate_map.py`; it does not import the page's functions or the builder, and draws the projection from d3's published constants) gives all 142 figures and checks of the default view to the digit: the sentence, the 18 tiles with their counts, the 15 rows by technology, the 367 rows with no place on the drawing (231 in Puerto Rico, 136 with no point) and the 34,668 drawn. The page's 31,073 units carry the same eight fields (MW, latitude, longitude, state, grid, technology, status, name) as EIA's two tables of September 2026, all 31,073; the 3,400 queue positions placed at a county that the restatement finds are at the Census Bureau's internal point to the fourth decimal, all 3,400.
- **ERCOT's "Completed" is worded for one copy of the queue (finding 1).** The list and the tile's hover say an ERCOT "completed" position is a signed agreement, built or not, which is true of the page's copy (the queue of 5 November: 544 of ERCOT's 577 "completed" positions plan to operate after November 2026). Since session 7022 (16 November) the connector writes "completed" only for a position ERCOT approved to synchronize; at the file's next rebuild the same words would call a running plant a mere agreement. The Queues tab's ERCOT chart says "reached operation" of the same signed agreements. Words, for landing.
- **Where a point is (finding 2).** The decisions and the hover of "Near a point" place a datacenter at "the city's point": 80 of the 278 are at the operator's coordinates, 28 at a county's point, 120 at a city's or town's, and 50 at none, and those 50 hold 25,158 of the 28,254 MW stated. The key puts every queue position "at its county's point" (184 are at a city's or town's). A unit's point is called "exact coordinates": it is EIA's point for the plant (31,073 units stand at 16,022 points, 161 at one). Words, for landing.
- **Smaller, words.** "Operating" holds 2,334 units on standby or out of service, 26,568.6 MW, 538 of them not expected back within a year (finding 3); the heavier ring "under construction" also marks 158 units EIA lists as built and not yet operating. The transmission layer draws every line of 230 kV and above alike, whatever HIFLD's status, and dates it by the day the ERW read it, not by HIFLD's data (finding 4). "Nothing since the inventory's month" is in the map, says a decision, beside queue positions of 5 November and datacenters of 15 November; seven in ten operating units are drawn at one size (finding 5).
- **One figure for ruling (finding 6):** seven units outside Alaska whose EIA point is 230 to 2,600 miles from the internal point of the county EIA names, five of them planned (1,464.2 MW: a 400 MW solar plant in Arkansas drawn in California, a 489.7 MW unit in Missouri drawn in Kansas, two 250 MW units of Placer County drawn on California's central coast, a 74.5 MW unit of Florida's Panhandle drawn in central Florida). Default "left as it is".
- **Checked and right:** the queue's MW are each operator's own measure (CAISO's "Net MWs to Grid", ISO-NE's "Net MW"), not Berkeley Lab's sum of a hybrid's parts; no planned date has passed; the drawing's not-drawn line; no EIA point falls in the wrong box of the projection; the line layers' voltages are all 230 kV and above. Still open, not repeated: ISO-NE's queue (414 positions, 21,901.8 MW) and the datacenter tracker are drawn while their tables are "license needed" (the faults' row 6, `wip/alt-map-1`).
- **What a siting analyst would add:** the county point stands a median of 12.5 miles from a planned plant in it (90th percentile 29.5): at 30 miles, 11.0 percent of the planned units truly near a planned site are left out and 6.3 percent of those listed are not near. The point of interconnection, named for 96.5 to 100 percent of the public queues' positions, is not on the map; the proposed in-service date is in the page's file for 3,252 of 3,684 positions and on no card; the distance to the grid (a planned unit of 100 MW or more stands a median of 1.5 miles from a line of 230 kV and above, 13.8 percent over 10 miles).
- **Five branches fix words and move no figure (1 to 5); one shows a figure for ruling (6).** Two data requests. Nothing needs the key.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/map/page.tsx` | `/map`, three tabs (`?tab=` projects, resources, queues). The Projects tab: the lead with the unit count, the paragraph of queue positions not placed (the one figure read from the live set, `projects\|count\|queue\|none`), `ProjectMap`, the decisions, the source line naming each kind's vintage and the copy's build day; the downloads of the four tables |
| `site/app/map/ProjectMap.tsx` | The tab, computed in the browser from the page's file: the panel (kind, grid, technology, status, state, size, "Near a point", the two line switches, Reset); the sentence; the tiles by status; the map (ECharts on us-atlas's Albers plane, a mark a row: dot operating, ring planned, heavier ring EIA's U, V, TS, triangle a queue position, diamond a datacenter; size 2 + 0.2 times the square root of MW, from 3 to 18 px); the key; the held queues; the card; the list within a distance; the table by technology |
| `site/lib/projectmap.ts` | Pure: the address and back, `select`, `totals`, `nearOf`, `milesBetween` (haversine, 3,958.8 miles), `circleOf`, `nearest`, `PLACED_AT`, `DATE_WORDS`, `statusWords` (ERCOT's "completed"), the source words, the colors, `cardOf`, `generatorLink` |
| `site/lib/maplayers.ts`, `site/app/map/lines/[name]/route.ts` | The two line layers (HIFLD's transmission lines of 230 kV and above, EIA's HGL pipelines of January 2020), read when a switch is turned on; the hover (ends, owner, kV and km, the source and the day it was read) |
| `site/app/map/card/route.ts` | The card's fields of the same file, served once at the first click |
| `site/app/map/Decisions.tsx` | The twelve decisions, held to `docs/methods/map.md` section 14 by `tests/test_session7601_map.py` |
| `site/app/map/QueuesView.tsx`, `QueueCharts.tsx` | The Queues tab: one operator's queue by entry year from `iso_queue_statistics` in the live set (each figure a check key); held grids (NYISO, MISO, ISO-NE) shown as "license needed" |
| `site/data/map.json` | The page's file: 35,035 rows (28,712 operating and 2,361 planned units of EIA-860M 2026-09, retrieved 24 October; 3,684 queue positions of 2026-11-05; 278 datacenters of 2026-11-15), built 19 November 2026 19:39 UTC; counts; MISO's 1,733 and NYISO's 361 queue rows counted, not written |
| `site/data/map_layers/transmission_230kv.json`, `hgl_pipelines.json` | 10,692 lines (299,994 km) and 133 pipelines (57,715 km), read from PASDA on 20 November 2026, simplified at 0.005 degrees; the transmission file carries id, kV, owner, the two ends and km, not HIFLD's status, inferred flag or dates |
| `warehouse/derived/project_map.py` | The builder: the four kinds, the held queues, the statuses, the precision codes, the card's fields |
| `warehouse/derived/energy_projects.py` | The queue positions' rows and places: the county gazetteer (2025, then 2020 for names it lacks), the place and county subdivision gazetteers, no fuzzy matching; MW `capacity_mw` as each operator gives it |
| `warehouse/connectors/iso_queues.py`, `hifld_lines.py` | The queues through gridstatus 0.36.0 (`STATUS_MAP`, ERCOT's milestones since session 7022); the line layers |
| `warehouse/derived/queue_statistics.py` | `iso_queue_statistics`, the Queues tab's table |
| Notes | `docs/methods/map.md` (the tool, fifteen sections), `energy_projects.md` (the table, "Coordinates", "The page"), `map_layers.md`, `datacenter_facilities.md`, `miso_pause.md` |
| Scripts | `site/scripts/map-read-page.mjs` (the tab drawn with its own component), `test-map-read.mjs` (42 checks), `map-figures.mjs` and `replication/map/` (123 views) |
| Read from the main copy, never written | `eia860m_operating_generators.csv`, `eia860m_planned_generators.csv` (vintage 2026-09, the page's own), the public queue tables of CAISO, ERCOT and SPP (pulled 26 September, for the point of interconnection only), the Census Bureau's county gazetteers of 2025 and 2020 (`warehouse/raw/census_gazetteer/20261009T073645Z/`) |

## How every number here was computed

- **The drawing:** `draw.mjs` draws `ProjectMap` and `MapDecisions` with the site's own code (`node --import ./scripts/tsx-register.mjs`) on `site/data/map.json` of origin/main, for the default address (`draw_default.txt`). The map canvas does not draw without a browser; every text around it does. The lead and the source line are the page's server part (it reads the live set for one count); their figures are the file's (`counts.units`, the vintages) and were read from it.
- **The restatement:** `restate_map.py` (standard library): every figure of the default view from the file's rows by the note's rules, the projection's boxes from d3's constants, against the drawing's marked figures; the units against EIA's tables; the county points against the gazetteer zips.
- **One rule at a time and the claims:** `measures_map.py` and `measures2_map.py`. Copies of every script and printout are in `docs/reviews/map-model-audit-2026-11-26/` (written to run from `runs/c10216/` of a worktree).

## The arithmetic re-done

| Figure (default view) | The page | Restated | Gap |
|---|---|---|---|
| Generating units, MW | 31,073 units of EIA's inventory of 2026-09, 1,713,756 MW | the same | 0 |
| Queue positions, MW requested | 3,684, 768,297 MW | the same (the rows as the file rounds them sum to 768,296.9; the file's own count reads 768,296.0: the rounding ruled on 17 November, line 3) | 0 |
| Datacenters, MW stated, how many state it | 278, 28,254 MW, 21 | the same | 0 |
| Units by EIA's status, 7 tiles | Operating 1,423,492 MW, 28,712 units; P 100,557 (695); L 64,727 (406); T 27,036 (228); U 54,089 (465); V 26,135 (409); TS 17,720 (158) | the same | 0 |
| Queue positions by status, 4 tiles | Active 525,944 MW (2,095); Suspended 3,852 (22); Completed 237,247 (1,533); Not stated 1,254 (34) | the same | 0 |
| Datacenters by status, 7 tiles | Operating 75 MW (25, stated at 1) ... Not stated 6,766 (193, stated at 11); Active, Completed, Withdrawn "not stated" | the same | 0 |
| By technology, 15 rows of 3 kinds | Solar 8,387, 172,182; 1,103, 122,247; 967, 190,229 ... Not stated 0; 4, 500; 15, 2,497 | the same, every count and MW | 0 |
| Rows with no place on the drawing | 367 | 367: 231 in Puerto Rico (each with EIA's point, outside the three boxes), 136 with no point (86 queue positions, 50 datacenters) | 0 |
| Rows drawn (the map's name) | 34,668 | 34,668: 547 in Alaska's box (every one of Alaska's), 251 in Hawaii's (every one), 33,870 in the lower 48's (no row of another state in Alaska's or Hawaii's box) | 0 |
| The held queues | "MISO queue positions: paused while terms are reviewed"; "NYISO queue positions: NYISO's terms do not allow it" | the file's `held` (1,733 and 361 rows) | 0 |
| The lead's unit count | 31,073 as of 2026-09 | `counts.units` | 0 |

- **The file against its sources.** All 31,073 units equal EIA's tables (vintage 2026-09, retrieved 24 October 2026) in MW to the tenth, latitude and longitude to the fourth decimal, state, grid (the balancing authority code), technology group (batteries by prime mover BA), status (EIA's code) and name. The operating MW from EIA's table round to the tile's 1,423,492.
- **The county points.** Of the 3,414 queue positions placed at a county, the restatement (its own name rule, the 2025 gazetteer first and 2020's for names it lacks, as the builder does) finds 3,400 and every one sits at the gazetteer's internal point to four decimals. The other 14 name two counties ("Linn & Bates", "Caddo & Kiowa Counties") or abbreviate ("Le Flore Co", "Caddo Prsh."), which the builder's rule reads and this one did not; each is at its first county's point. The 184 at a city's or town's point were not restated: the place gazetteers are not held here.
- **The queue positions themselves** cannot be restated from their table on this machine: the main copy holds `energy_projects` of 2 October, the page's copy is of 5 November. The page's sums of them are restated from the file (above).
- **What a visitor sees:** the page is in review; drawn with the site's code, no em dash.

## One rule changed at a time

| Choice the page makes | The other choice | Worth | Said on the page? |
|---|---|---|---|
| A queue position at its county's internal point (no site is in the queues) | a plant's own point, sized on EIA's planned units, which have both | A planned unit stands a median of 12.5 miles from its county's internal point (75th percentile 17.2, 90th 29.5; operating units 11.2, 17.3, 30.0). With every planned unit as a site and every other as a row, at 30 miles: 46,980 pairs truly near, 44,606 by the county point; 5,172 lost (11.0 percent of the truly near) and 2,798 gained (6.3 percent of those listed). Of the read's five sites, Bakersfield lists 36 planned units by the county point against 7 truly within 30 miles; New Albany loses 2 of 6 | yes: "not at its site", and the list counts the positions measured from a county's point |
| A unit at EIA's point for its plant | at its county's point | the rule above; 31,073 units at 16,022 points | "exact coordinates" (finding 2) |
| "Operating" is EIA's operating sheet | EIA's code OP alone | 28,712 units, 1,423,491.7 MW, become 26,378 and 1,396,923.1 (-26,568.6 MW, 1.9 percent): SB 1,577 units 8,897.5 MW, OA 219 units 7,103.4 MW, OS 538 units 10,567.7 MW | on the card, a unit at a time (finding 3) |
| Nameplate | net summer | 7.5 percent lower over the operating units (the note's section 12) | yes, decision 1 |
| A queue position on the map unless withdrawn | active and suspended only | 3,684 positions, 768,296.9 MW, become 2,117 and 529,796.3 (the 1,533 completed, 237,246.6 MW, and 34 of no status, 1,254.0 MW, leave) | yes, decision 3 |
| A completed position drawn beside the inventory's units | left out where it names an operating unit of its state | 244 of the 1,533 completed positions bear the name of an operating unit in their state (32,799.3 MW): CAISO 103 of 252, ISO-NE 83 of 364, ERCOT 58 of 577, SPP none of 340 (SPP's names are its own numbers). A floor: names that differ are not matched | "a completed position may be a unit the inventory already lists" (decision 3). The planned units against active positions: the ruling of 17 November, line 2 (154 to 163 positions) |
| Datacenters drawn where the tracker places them | | 50 of 278 have no point and are not drawn; they hold 25,158 of the 28,254 MW stated (89.0 percent). The 228 drawn state 3,096 MW | the not-drawn line counts them with Puerto Rico, not their MW (finding 2) |
| A mark's diameter 2 + 0.2 times the square root of MW, from 3 to 18 px | proportional to MW | 19,947 of 28,712 operating units (69.5 percent), 891 of 2,361 planned and 605 of 3,684 positions are under 25 MW and drawn at one size; none reaches the largest | "its area grows with its MW" (the note); the key "size: MW" (finding 5) |

## Each claim against the code

| Claim, or question | Where | What the code does | Verdict |
|---|---|---|---|
| Where a unit is placed | the card ("exact coordinates"), the list's "Placed at", the decisions | EIA's latitude and longitude of the plant, to four decimals; every unit of a plant at one point | **Finding 2**: EIA's plant point, not an exact site. Seven units outside Alaska disagree with EIA's own county by 230 to 2,600 miles (finding 6) |
| Where a queue position is placed | the key ("at its county's point"), the decisions, the card, the list | County internal point (3,414), a city's or town's internal point (184), none (86) | Right in the decisions and card; **the key leaves out the city and town** (finding 2) |
| Where a datacenter is placed | decision "near", the hover of "Near a point" ("the city's point for a datacenter") | The operator's coordinates (80), a city's or town's point (120), a county's point (28), none (50) | **Finding 2** |
| A queue position against its point of interconnection | the card | No point of interconnection is carried: `energy_projects` keeps county and state only. CAISO's, ERCOT's and SPP's tables name one for 100, 100 and 96.5 percent of their positions | Not claimed; an expert's gap (below) |
| A project in two sources drawn twice | decision 3, the list's hover | A planned unit and its queue position: two rows (ruled 17 November, line 2). A completed position and its operating unit: two rows, sized here, 244 positions by name | **Right as stated**; sized |
| Operating, planned, withdrawn | tiles, the panel, decision 3 | Operating holds SB, OA and OS; planned keeps EIA's seven codes; withdrawn queue positions are left out, withdrawn datacenters (4) are drawn under their own tile | Operating: **finding 3**. The rest **right** |
| The heavier ring "planned, under construction" | the key | EIA's U, V and TS; TS is "Construction complete, not yet operating" (158 units, 17,720 MW) | **Finding 3** |
| Nameplate MW | decision 1, the tiles' hovers | `capacity_mw`, EIA's nameplate; net summer 7.5 percent lower | **Right** |
| A queue position's MW | the hover "MW requested", the tiles' hover "what each position asks to connect" | gridstatus's `Capacity (MW)`: CAISO's "Net MWs to Grid", ISO-NE's "Net MW", SPP's "Capacity", ERCOT's report's capacity | **Right**: the operators' figure at the point of interconnection, not Berkeley Lab's sum of a hybrid's parts (the queue audit's finding 1 does not reach this page) |
| ERCOT's "Completed" | the list, the queue tiles' hover, the Queues tab | True of the copy's queue (5 November, gridstatus's word for a signed agreement); since session 7022 the connector writes ERCOT's own milestones | **Finding 1** |
| The lines' voltage, source and year | the switch "Transmission lines, 230 kV and above", its hover and tip | HIFLD's layer 178 as PASDA serves it, every line with VOLTAGE 230 or more (7,205 at 230 kV, 2,600 at 345, 813 at 500, 46 at 765, one coded 1,000); asked with no status filter; the web file keeps no status, no inferred flag, no date | kV right; **status and date not said** (finding 4). HGL "January 2020" **right** |
| "Near a substation" | | No substation is on the map: the tip says HIFLD's substations are not in a public service the ERW reads, and the distance is from a typed point or a row's point only | **Right**: no such claim is made |
| The distance and its method | "Near a point", decision "near" | Haversine on 3,958.8 miles from each row's point, both ends counted in; the test of the read holds it (42 checks) | **Right**, but for the datacenter's point (finding 2) |
| A card's figures against the tables | the card | `cardOf` writes the file's own fields; MW to one decimal as the hover (fixed 16 November) | **Right**; the proposed in-service date the file carries is not shown (an expert's gap) |
| Held grids and licensed layers reaching a public figure | the sentence, the tiles, the list | MISO's and NYISO's queue rows are counted, never written; ISO-NE's 414 positions (21,901.8 MW) and the 278 datacenters are drawn while `energy_projects` (for ISO-NE) and `datacenter_facilities` are "license needed" | **Open ruling**, not repeated (faults row 6; `wip/alt-map-1`) |
| The as-of date of each layer | the source line, the card, the line hover | Units: EIA's month 2026-09, retrieved 24 October; queue: 2026-11-05; datacenters: 2026-11-15; built 19 November; lines: retrieved 20 November | **Right**, but for the lines' data date (finding 4) and the decision "nothing since the inventory's month" (finding 5) |
| Rows not drawn | the map's note: "Puerto Rico, or no location in the source" | 231 in Puerto Rico and 136 with no point | **Right** |
| A unit's grid | decision 5 | EIA's balancing authority code; 973 with none | **Right**; Project Matador's case ruled 16 November |
| Planned dates | the hover "planned operation" | EIA's planned month; none before the inventory's month | **Right** |

## What a siting analyst's or a transmission planner's own number would hold that this does not

| Item | Size | From |
|---|---|---|
| A queue position's point of interconnection (the substation or line it would connect at) | named for 514 of 514 of CAISO's positions not withdrawn, 1,778 of 1,778 of ERCOT's and 987 of 1,023 of SPP's (pull of 26 September); not in `energy_projects`, the file or the card | `measures2_map.out` |
| The proposed in-service date | in the page's file for 3,252 of 3,684 positions (`more.queue.proposed`, session 7052), on no card or list; 94 of 2,095 active positions' dates had passed by the queue's vintage | the same |
| The distance to the grid | a planned unit of 100 MW or more stands a median of 1.5 miles from a line of 230 kV and above (13.8 percent over 10 miles; operating ones 0.2 miles, 9.1 percent); 60.8 percent of planned units (67.2 percent of their MW) within 5 miles. On the simplified web lines, so to about a third of a mile | `measures_map.out` |
| The error of a county point at the distances a siting search uses | 11.0 percent of truly near planned units lost and 6.3 percent of those listed not near, at 30 miles | the rule above |
| A capacity weighted by its chance of being built, and the study phase | the queue audit's numbers (11.2 percent of active MW; 22.8 percent with an executed agreement) are for `/queues`; the map's queue tables hold neither | `queues-model-audit-2026-11-26.md` |
| Substations, hosting capacity, a line's rating and loading, retirements nearby | not held (substations not in a public service read; ratings and loading not public; retired units in `eia860m_retired_generators`, not drawn) | the tip, decision 12 |
| The line layer's status and age | not in the web file: HIFLD's status, inferred flag and source dates are in `hifld_transmission_lines`, which this machine does not hold | data request (a) |

## Findings

| # | Severity | Finding | Effect | Fix | Branch |
|---|---|---|---|---|---|
| 1 | Medium | ERCOT's "Completed" is worded for one copy of the queue; the Queues tab's ERCOT "reached operation" counts signed agreements | the page's copy: 577 ERCOT positions (137,410.0 MW), 544 planning to operate after November 2026; at the next rebuild the words would describe another group | words | `wip/audit-map-1` (`039848841`) |
| 2 | Medium | Where a point is: a datacenter's point, the key's county point, "exact coordinates" | 108 of 228 placed datacenters not at a city's or town's point; 50 not placed with 89.0 percent of the MW stated; 184 positions at a city's or town's point; 31,073 units at 16,022 plant points | words | `wip/audit-map-2` (`2bc19f476`) |
| 3 | Low | "Operating" holds standby and out-of-service units; the heavier ring marks built units as under construction | 2,334 units, 26,568.6 MW (1.9 percent), 538 not expected back; 158 units, 17,720 MW | words | `wip/audit-map-3` (`188639c7b`) |
| 4 | Low | The transmission layer's status and date are not said | every line of 230 kV and above drawn alike; the date shown is the reading day | words | `wip/audit-map-4` (`b6845e95c`) |
| 5 | Very low | "Nothing since the inventory's month is in it"; the marks' size | queue 2026-11-05 and datacenters 2026-11-15 beside units of 2026-09; 69.5 percent of operating units at one size | words | `wip/audit-map-5` (`0631f1ed9`) |
| 6 | Very low | Seven EIA points far from EIA's own county | 7 units, 1,469.2 MW (five planned, 1,464.2 MW), 230 to 2,600 miles | figure, for ruling | `wip/audit-map-6` (`5b7abadbf`) |

## 1. ERCOT's "Completed" is worded for one copy of the queue (Medium)

- **Where.** `site/lib/projectmap.ts`, `statusWords` ("Agreement signed, built or not (ERCOT; the table says completed)"); `ProjectMap.tsx`, the queue tiles' hover ("For ERCOT's positions, "Completed" is a signed interconnection agreement, built or not"); `QueuesView.tsx` and `QueueCharts.tsx`, ERCOT's "Operating" and "Entered and reached operation"; `docs/methods/map.md` section 10.
- **Why it is wrong.** The words were true of gridstatus's word, which the connector kept until session 7022 (`warehouse/connectors/iso_queues.py`, `ercot_milestone`, landed 16 November 2026 19:58 UTC): from a pull after that, ERCOT is "completed" only with its day of approval to synchronize, and a signed agreement alone is "active". The page's copy is of the queue of 5 November: ERCOT's 577 "completed" positions carry gridstatus's "Completed", and 544 of them have a proposed in-service date after November 2026, so the words hold today. The table was pulled again on 23 November (`coverage.csv`); the monthly job's next rebuild of `map.json` would bring the milestones, and the list would then call a plant ERCOT let run "Agreement signed, built or not". The Queues tab reads `iso_queue_statistics`, built 16 November 20:48 UTC from the queue as pulled by then (whether that pull carried ERCOT's milestones is data request b): if it did not, its ERCOT "Operating" counts signed agreements, while the chart says "how many of them reached operation" and the page says nothing of it; `/explore/interconnection` heads the same group "Agreement signed" (another tool, not changed here).
- **The test.** `tests/test_audit_map_1.py` on `wip/audit-map-1`: in the page's file ERCOT's completed positions carry gridstatus's "Completed" and 544 of 577 plan to operate after November 2026 (passes on main); the connector writes ERCOT's milestones (passes); the words test fails on main.
- **The fix on the branch, words only.** `statusWords` reads the copy's queue vintage: before 17 November 2026, "Agreement signed, built or not (ERCOT; the table says completed)" as now; from then, "Approved for synchronization (ERCOT; the table says completed)". The tiles' hover says the same by the vintage. The Queues tab's ERCOT line says that "Operating" follows the queue as last pulled: from a pull before 17 November 2026 every position with a signed agreement, built or not, and from later pulls those ERCOT approved to synchronize. The note says both. No figure moves.

## 2. Where a point is (Medium)

- **Where.** `site/app/map/Decisions.tsx`, decision "near" ("the city's point for a datacenter"); `ProjectMap.tsx`, the hover of "Near a point" (the same words, and "EIA's coordinates for a unit"), the key ("queue position, at its county's point"), the list's note ("their county's or town's point"); `site/lib/projectmap.ts`, `PLACED_AT[0]` "exact coordinates" and the card's "exact coordinates"; `docs/methods/map.md` sections 8 and 14.
- **Why it is wrong.** Datacenters: 80 of the 278 are at the operator's own coordinates, 120 at a city's or town's point, 28 at a county's point and 50 at none (by source: 34 of the 65 from the news and 16 of the 210 from operators' lists have no point). The 50 not drawn hold 25,158 of the 28,254 MW the sentence prints (89.0 percent); a reader measuring from a site for nearby load misses them, and the not-drawn line names Puerto Rico and "no location" without them. Queue positions: 184 of the 3,598 placed are at a city's or town's point (session 349), which the key does not say. Units: the point is EIA's for the plant, to four decimals; 31,073 units stand at 16,022 points (161 at Project Matador's), and seven outside Alaska disagree with EIA's own county by 230 miles or more (finding 6). "Exact coordinates" claims more.
- **The test.** `tests/test_audit_map_2.py` on `wip/audit-map-2`: the precision codes of the file (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The decision and the hover read "EIA's coordinates of the unit's plant for a unit, the county's, city's or town's point for a queue position, and for a datacenter the operator's own coordinates, its city's or town's point or its county's point (the list's "Placed at" says which)"; the key "queue position, at its county's, city's or town's point"; the list "their county's, city's or town's point"; `PLACED_AT[0]` "EIA's plant coordinates" and the card "EIA's coordinates of the plant". The note's sections 8 and 14 the same, with the counts. `site/scripts/test-map-read.mjs` reads the new words.

## 3. Operating and under construction (Low)

- **Where.** `ProjectMap.tsx`, the units' tiles' hover ("The MW is nameplate capacity, summed over the units of the status") and the key ("planned, under construction"); `docs/methods/energy_projects.md`, "The marks".
- **Why it is wrong.** The tile "Operating" is EIA's operating sheet: 1,577 units on standby (8,897.5 MW), 219 out of service and expected back within the next calendar year (7,103.4 MW) and 538 out of service and not expected back (10,567.7 MW) are in its 28,712 units and 1,423,492 MW. The card names a unit's code, one at a time; the tile and its hover do not. The heavier ring is drawn for EIA's U, V and TS, and TS is "Construction complete, not yet operating" (158 units, 17,720 MW): the key calls all three "under construction".
- **The test.** `tests/test_audit_map_3.py` on `wip/audit-map-3`: the codes and MW from the file (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The hover adds that "Operating" is EIA's operating inventory, which also holds units on standby and units out of service, some not expected back within the next calendar year (EIA's SB, OA and OS; a unit's card names its code). The key reads "planned, under construction or built and not yet operating". The note the same. No figure moves.

## 4. The transmission layer's status and date (Low)

- **Where.** `ProjectMap.tsx`, the tip of "Lines on the map"; `site/lib/maplayers.ts`, the hover's source line ("retrieved 2026-11-20"); `docs/methods/map_layers.md`.
- **Why it is wrong.** `hifld_lines.py` asks PASDA for every line with VOLTAGE 230 or more, with no status filter, and the web file keeps id, kV, owner, the ends and km: a line HIFLD lists as under construction, or of a status it does not state, is drawn as a line in service, and a voltage HIFLD inferred is drawn as a measured one. The one date a reader meets is the day the ERW read PASDA's copy; HIFLD's own source and validation dates are in the table, line by line (`x_source_date`, `x_val_date`), and not on the page. HIFLD's open catalog was retired on 26 August 2025 (the note), so the copy may be older than its reading day suggests. A planner reading a line near a site as existing may be reading a proposal or an old record. The sizes need the table (data request a).
- **The test.** `tests/test_audit_map_4.py` on `wip/audit-map-4`: the connector's query has no status filter and the web file carries no status or date (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The tip adds: every line HIFLD lists at 230 kV or more is drawn alike, whatever its status and whether HIFLD inferred its voltage; the date in a line's hover is the day the ERW read PASDA's copy, not the date of HIFLD's data, which the table keeps line by line. The note the same.

## 5. The inventory's month, and the marks' size (Very low)

- **Where.** `Decisions.tsx`, decision "retired" ("Retired units are not on the map, and nothing since the inventory's month is in it"); the key ("size: MW"); `energy_projects.md`, "The marks" ("its area grows with its MW").
- **Why it is wrong.** The queue positions are of 5 November and the datacenters of 15 November, two months after the units' September; the source line says so. And a mark's diameter is 2 + 0.2 times the square root of MW, held at 3 px below 25 MW: 69.5 percent of operating units, 37.7 percent of planned and 16.4 percent of positions are drawn at that one size, and a datacenter is always one size.
- **The test.** `tests/test_audit_map_5.py` on `wip/audit-map-5`: the shares from the file (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The decision reads "nothing since the inventory's month is in its units (the queue positions and the datacenters are of their own, later days, in the source line)"; the key "size: MW, above 25 MW (smaller rows and every datacenter at one size)"; the note the same. No figure moves.

## 6. Seven EIA points far from EIA's own county (Very low)

- **Where.** `site/data/map.json`, the units' `la` and `lo` (EIA's, unchanged); the drawing, the list and "Near a point".
- **What.** Outside Alaska (where Aleutians West's internal point is 590 miles from Dutch Harbor), seven units stand over 200 miles from the internal point of the county EIA names for them (`far.out`): AmericoldCA - Plainville, CT (2 MW, operating, Hartford County, drawn in California, 2,600 miles off); Big Creek Solar LLC (400 MW, planned, Lee County, Arkansas, drawn in California, 1,537 miles); Hardwood Hammock (74.5 MW, planned, Walton County, Florida, drawn in central Florida, 349 miles); Rangeley (3 MW, Franklin County, Maine, drawn at sea south of Massachusetts, 276 miles); Athens Solar I (Hybrid) (two units of 250 MW, planned, Placer County, California, drawn on the central coast, 232 miles); Mullin Creek #1 Generating Station (489.7 MW, planned, Nodaway County, Missouri, drawn in Kansas, 230 miles). Either EIA's point or EIA's county is wrong; the map draws the point, so a search near Lee County misses a 400 MW planned plant and a search in the Mojave lists it. A looser screen (over 50 miles from the own county's point and nearer another state's county points, `measures2_map.out`) gives 121 units, mostly sound plants in large border counties (Riverside's and San Bernardino's along the Colorado River), so it is not used.
- **The test.** `tests/test_audit_map_6.py` on `wip/audit-map-6`, a test only (passes on main with the gazetteer named by `ERW_GAZETTEER_DIR`; skipped where it is not held).
- **For Samuel's ruling.** Default "left as it is" (EIA's point, as the decisions say). The other choice: a unit whose EIA point is over 200 miles from its EIA county's point outside Alaska is drawn at the county's point and marked: 7 units (1,469.2 MW; 5 planned, 1,464.2 MW) move on the drawing and in "Near a point"; no count or sum changes.

## The decisions block, line by line

1. Nameplate: **right**.
2. MW never added across kinds: **right**.
3. Not withdrawn, a completed position may be a unit already listed: **right**; sized (244 by name, a floor).
4. The queues drawn: **right** as to MISO, NYISO, PJM; ISO-NE's held table is the open ruling.
5. A unit's grid: **right**.
6. A battery: **right**.
7. EIA's seven codes: **right**.
8. A queue position at its county's, city's or town's point: **right**.
9. No size, a row with no MW left out: **right**.
10. The distance: **right** but for the datacenter's point (finding 2).
11. A datacenter drawn when placed in a US state: **right**; 50 placed in a state have no point.
12. Retired units, "nothing since the inventory's month": **finding 5**.

## Not covered, or left open

- **The Queues tab's figures** come from the live set (`iso_queue_statistics`), which this machine does not read; only its words were checked (finding 1).
- **The Resources tab** (fourteen natural resource layers) is another note's (`resources.md`); not read.
- **The queue positions against their table** of 5 November: not held here (the page's sums are restated from the file).
- **The map canvas, a hover and a click** need a browser; drawn to HTML only.
- **The 184 city and town points** were not restated: the place gazetteers are not held here.

## The words branches drawn and read

Each branch's words were drawn to HTML with the site's own code (`node --import ./scripts/tsx-register.mjs`, `draw.mjs` for `ProjectMap` and `MapDecisions`, `draw_vintage.mjs` for finding 1 with a later queue vintage) and read in the drawn text. No em dash in any drawing.

| Branch | Where the words are drawn | Read |
|---|---|---|
| `wip/audit-map-1` (`039848841`) | the list near Abilene (ERCOT's positions) and the queue tiles' hover; the same with the file's queue vintage set to 2026-11-23 | pass: "Agreement signed, built or not (ERCOT; the table says completed)" and "... this copy of the queue predates the connector's reading of ERCOT's own milestones"; with the later vintage, "Approved for synchronization (ERCOT; the table says completed)" and "\"Completed\" is a position ERCOT approved to synchronize". The Queues tab's ERCOT line was read in its source: its component reads the live set and was not drawn |
| `wip/audit-map-2` (`2bc19f476`) | the hover of "Near a point" and decision "near" (Bakersfield, 30 miles), the key, the list's note and "Placed at" | pass: "... and for a datacenter the operator's own coordinates, its city's or town's point or its county's point (the list's "Placed at" says which)", "queue position, at its county's, city's or town's point", "measured from their county's, city's or town's point, not their site", "EIA's plant coordinates" |
| `wip/audit-map-3` (`188639c7b`) | the units' tiles' hover, the key (default view) | pass: "\"Operating\" is EIA's operating inventory: it also holds units on standby and units out of service, some not expected back within the next calendar year (EIA's codes SB, OA and OS; a unit's card names its code)."; "planned, under construction or built and not yet operating" |
| `wip/audit-map-4` (`b6845e95c`) | the tip of "Lines on the map" | pass: "Every line HIFLD lists at 230 kV or more is drawn alike, whatever its status ..." |
| `wip/audit-map-5` (`0631f1ed9`) | decision "retired", the key | pass: "... nothing since the inventory's month is in its units (the queue positions and the datacenters are of their own, later days, in the source line)"; "size: MW, above 25 MW (smaller rows and every datacenter at one size)" |
| `wip/audit-map-words` (`09b5862d0`) | the five merged, the default view and Abilene | pass: every new sentence drawn once; the restatement on the merged drawing gives the same 142 of 142 (`restate_words.out`): no figure moved |

- **Tests.** Each words test fails on origin/main and each behaviour test passes there. On each branch and on the merge: its audit test, and every test file that reads the changed files (`test_session167`, `241c`, `318`, `349`, `371`, `405`, `7518_interconnection_read`, `7601_map`, `8014_map_layers`, `9601_line_ends_unnamed`, `9818`, and for the notes `2204`, `330`, `472`, `538`, `89_miso_pause`): 147 passed, 10 skipped on the merge; `site/scripts/test-map-read.mjs` 42 of 42 (its two checks of the old words follow branch 2) and `test-map-sources.mjs` 37 of 37.
- **The merge.** Branches 1 and 3 both change the units' and queue tiles' hover line, and 2, 3 and 5 neighbouring lines of the key and of `energy_projects.md`'s "The marks": `wip/audit-map-words` is origin/main with the five merged and each branch's words kept whole.

## Landing, rulings and data (returned to the chain's main session)

- **For landing (words only):** `wip/audit-map-words` (`09b5862d0`, the five merged, conflicts resolved), or each alone: `wip/audit-map-1` (`039848841`), `-2` (`2bc19f476`), `-3` (`188639c7b`), `-4` (`b6845e95c`), `-5` (`0631f1ed9`); 1 and 3 conflict with each other, as do 2, 3 and 5. Each was drawn and read (pass). No figure moves.
- **For Samuel's ruling, default "left as it is":** finding 6, `wip/audit-map-6` (`5b7abadbf`), not for landing: seven units whose EIA point is over 200 miles from their EIA county's point outside Alaska, drawn at the county's point and marked; 7 units, 1,469.2 MW (5 planned, 1,464.2 MW), move on the drawing; no count or sum changes.
- **Data requests:** (a) from `hifld_transmission_lines`, the 10,692 lines by `x_status`, by `x_inferred`, and by the year of `x_source_date` and of `x_val_date` (counts and km, no rows copied): it sizes finding 4. (b) From `iso_queue_statistics` as the live set holds it and from `ercot_interconnection_queue` of 23 November: ERCOT's operating positions by entry year in each, so that the Queues tab's ERCOT "Operating" can be said to be agreements or synchronized plants: it sizes finding 1.
- **Needs the key:** nothing.
