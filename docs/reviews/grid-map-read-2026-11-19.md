# The Grid tool's map, read as its readers would read it

Energy Research Warehouse (ERW). Session 8604 (chain 504, the portable laptop), 19 November 2026, about 13:10 to 13:35 UTC. The map is the Map shape of `/grid?view=network`, as `wip/8602-grid-regions` builds it on main's boundary file (HIFLD Control Areas, 60 of the network's 70 balancing authorities). Each case was taken start to finish in a real browser on a build, in the internal view, at 1280 px (case 5 at 390 px too), by `runs/c504_read_map.mjs`; what the page said is in `runs/c504_read_map.out`, and the pictures are `docs/reviews/grid-map-2026-11-19/case*.png`.

The question of each case: can the reader get the answer without leaving the page, without a figure that contradicts another on the page, and without a word they would not know?

## The five readers and their cases

1. **A transmission planner.** "Late on Monday 16 November 2026 (23:00 Eastern), where was PJM sending power, how much on its largest tie, and who reported it?" Address: `/grid?grid=pjm&view=network&shape=map`.
2. **A power trader.** "Texas during Uri, the morning of 15 February 2021 (07:00 Central): what was ERCOT taking from the Southwest Power Pool and from Mexico, at what price, and how did it move through the day?" Address: `/grid?view=network&net=uri_2021&node=ERCO&shape=map&t=2021-02-15T13:00:00Z`.
3. **A student of one grid.** "The Tennessee Valley Authority: who are its neighbours, is it importing or exporting, how clean is it, and where did its power come from this week?" The map, then a click on TVA.
4. **An AI lab's siting analyst.** "A 500 MW campus near Phoenix: whose footprint is it in, Salt River Project's or Arizona Public Service's, and what does each import late in the evening?" The map, zoomed to Arizona.
5. **A battery developer.** "California's evening: when do the batteries discharge, how many megawatts at the peak, and what is California importing then?" The story "California's evening" on the map, at 1280 and 390 px.

## What each reader got

- **Case 1.** Answered on the page. PJM was a net exporter of 811 MW over seven ties: 2,022 MW to NYISO and 1,150 MW to MISO, and it took 1,459 MW from Duke Energy Progress East. The seven ties on the map carry the megawatts of the panel's list, tie for tie, and the hover on PJM carries the panel's net figure and its carbon intensity (324.20 kg CO2/MWh). All seven of PJM's ties have both ends on the map. Not answered: PJM's demand that hour (row 5).
- **Case 2.** Answered. At 13:00 UTC on 15 February 2021 ERCOT took 815 MW from the Southwest Power Pool, 1.59 percent of its 51,402 MW demand, and 0 MW from Mexico, at 8,878.03 USD/MWh in real time; stepped every three hours, the import stayed between 547 and 815 MW until it fell to 56 MW at 13:00 UTC on the 16th. Play moved the map hour by hour and the address kept the hour. Mexico's operator has no boundary, so its tie is in the panel and not on the map (row 12).
- **Case 3.** Half answered. TVA was a net importer of 1,582 MW over seven ties (2,099 MW in from MISO; 448 MW out to PJM), and "Trace the power" gives the week: 88.47 percent of what came in came from MISO, half of which MISO had taken from PJM. Not answered: how clean it is (row 6), its demand (row 5), its local time (row 10), its twelve months (rows 3 and 11).
- **Case 4.** Half answered, and only after the fixes of rows 8 and 9. Before them the map showed one footprint at Phoenix and no line or name by which to find Phoenix. Salt River Project was exporting 3,764 MW over seven ties and Arizona Public Service importing 765 MW over nine. Not answered: demand and carbon intensity for either (rows 5 and 6).
- **Case 5.** Not answered as the page stood: the story opened on 16 November (Pacific), every hour read "Not reported for this hour" and no ring was drawn (row 4). On production, whose copy of the page was two hours older, the same story showed 15 November with the batteries discharging 2,105 MW at midnight Pacific and charging 8,388 MW at noon. After the fix the story shows the newest day that holds the batteries and says which day it passed over. On a phone the map is 356 by 223 px, the panel under it, nothing wider than the screen.

## The rows

| # | Case | What the reader met | What it is | State |
|---:|---|---|---|---|
| 1 | 1, 2 | A tie's hover named three tables, demand's and carbon intensity's among them. A tie's megawatts come from one | Site fault: the hover carried the region's list of tables | fixed (session 8604): a tie's hover names the interchange table of the view alone (`flowTable`); `tests/test_session8604.py`, `check-grid-map.mjs` |
| 2 | 1 | The hover of the tie from LG&E and KU wrote that operator's name of 113 characters three times | Site fault: the line on who reported repeated both names | fixed (session 8604): the two names stand once, in the hover's head; who reported is said by code ("Reported by LGEE, the first of the two by code; where LGEE filed nothing for this hour, by PJM. The file does not mark which.") |
| 3 | 3, 4 | With TVA chosen, the fold under the map, "Tennessee Valley Authority's neighbours, last twelve months", read "Click a grid, or choose one above" | Site fault, in the Network shape too: the words for no grid chosen were shown for a grid whose twelve months are not held | fixed (session 8604): "Not held for Tennessee Valley Authority: the neighbours' twelve months need a grid's demand, which the table behind them (ba_supply_monthly) holds for the seven ISO grids only." With no grid chosen the words are as they were |
| 4 | 5 | "California's evening" showed a day with no battery reported in any hour, and no ring | Site fault, in the Network shape too: the story took the newest whole Pacific day of the week whatever it held. The live set's battery table ended on 16 November 07:55 UTC and the week's interchange ran to 17 November 23:00 | fixed (session 8604): the newest whole Pacific day for which California's batteries are reported (`eveningDay` in `site/lib/networkV3.ts`); a newer whole day with none is passed over and named in the line under the controls; with no report in the week, the newest whole day, as before. The lag itself: row 5 |
| 5 | 1, 3, 4, 5 | "its demand for this hour is not held" for PJM, CAISO and the other seven grids in the week's two newest days, so a net exchange cannot be read against demand | Data: in the live set `eia930_all_demand`, `eia930_all_storage` and `eia930_all_generation` end at 2026-11-15 23:00 UTC and `caiso_battery_storage` at 2026-11-16 07:55 UTC (read 19 November 13:13 UTC), while the network's hourly snapshot runs to 2026-11-17 23:00 UTC | data machine: data request 543 of `docs/state/data_requests_done_line.md` |
| 6 | 3, 4 | "Carbon intensity of generation: not held" for TVA, Salt River Project, Arizona Public Service; 53 of the 60 regions are grey | Data: the warehouse computes it for the seven ISO balancing authorities only | data machine: data request 540 |
| 7 | 1 | The key says the color is of 2026-11-12 23:00 UTC; the hour shown is 2026-11-17 04:00 UTC | Data and a ruling: `carbon_intensity_hourly` ends on 12 November in the live set (request 543); and in the live week the color is the latest hour held, not the hour shown | ruling: the color at the hour shown (the note for Samuel, with the default taken: the region has its sphere's color); the table's lag is in request 543 |
| 8 | 4 | At Phoenix three published footprints lie on one another (Salt River Project, Arizona Public Service, Western Area Power Administration's Desert Southwest region); the map showed the top one and gave no sign of the others | Site gap: a published boundary is a planning footprint, and footprints overlap | fixed (session 8604): a region's hover lists the other footprints that hold the point under the pointer ("Also covers this point: ...") |
| 9 | 4 | Nothing on the map says where Phoenix is: no state line, no name | Site gap: names are on hover only by the owner's ruling, and the regions' own edges are not the states' | fixed (session 8604): the states' outlines as thin lines over the regions, which name nothing and answer no pointer, and the hover's line "State under the pointer: Arizona". A decision made without the owner, said in the note |
| 10 | 3, 4 | "2026-11-17 04:00 UTC (its local time is not held)" for TVA and Salt River Project | Site gap: the page knew the time zone of the seven grids only. The whole country's index carries every authority's zone | fixed (session 8604) for the day the index is on the site: the panel takes the zone from `index.json` (`bas[].tz`). Until then the words are as they were |
| 11 | 3, 4 | "Over the last twelve months: Not held: a share needs the grid's demand, which the warehouse holds for the seven ISO grids only" | Data: `ba_supply_monthly` is built for the seven. The demand files of the whole country hold 58 authorities' demand | data machine: not asked tonight (it is a new table's worth of work, for a later chain); the row stands so it is not lost |
| 12 | 1, 2 | The seven operators of Canada and Mexico (and Black Hills, Sikeston, SPP's western area) have no boundary: 21 of the hour's 148 ties are not on the map. They are named under the map, each with its hover and its panel | A map of United States boundaries holds no place for them | ruling: draw them as marks at the border, at places of the ERW's choosing, or leave them listed. Default taken: listed, nothing placed by hand |
| 13 | 1, 2 | The tie's hover says who reported by rule, not for the hour ("The file does not mark which") | Data: the snapshot and the story files do not record which side's report an hour's flow is | data machine: data request 541 |
| 14 | 2 | The hub price is in the panel (8,878.03 USD/MWh), not on the map: the Prices switch draws its ring in the Network shape only | Said under the map: "The prices' ring is drawn in the Network view; the panel holds its numbers here" | not a fault: the figure is on the page, one click from the map |
| 15 | 3 | A student who wants TVA's region (Tennessee) finds no link to it: the panel's line "EIA region" is drawn only when the regions' index is on the site | The data machine's `index.json` is not on main | waiting: the code is on `wip/8602-grid-regions`; nothing more to do here |
| 16 | 5 | On a phone the story, the ring, the panel under the map | Seen at 390 px: 356 by 223 px of map, nothing wider than the screen | not a fault |
| 17 | 1 | Set side by side as the page opens, the 3D network drew 139 ties and the map 148, for one hour on the slider (2026-11-17 04:00 UTC) | Site fault in the Network shape, on production (read there 19 November, about 13:20 UTC): the scene is built on the week's newest hour, and since session 124 the page opens on the newest hour every reporting pair holds, usually earlier. Until the slider was moved the scene drew the newest hour's ties under a line and a slider that named another hour; moved one hour on and back, it drew 148 | fixed (session 8604): when the scene is ready it takes the hour, view and selection shown, as it has done since session 180 on coming back from the map. Found by `check-grid-map.mjs`, which sets the scene's ties against the map's for the same hour. It changes what the 3D network draws as it opens, to the hour its own line names: said at the top of the session's report |

## What the read changed on the page

Seven site faults or gaps fixed at their cause, each with a test (rows 1, 2, 3, 4, 8, 9, 17), and one made ready for the index (row 10). Three of them were in the Network shape too: the fold's words for a chosen grid (row 3), the day "California's evening" shows (row 4), and the hour the 3D scene draws as the page opens (row 17). Row 17 is the one change to what the 3D network shows as it opens: it now draws the hour its own slider and line name.

Five rows are the data machine's (5, 6, 11, 13, and the table behind 7); two are rulings with the default taken (7 and 12).

## The regions in the Grid tool, read on the data machine's real files (session 8605)

Session 8605, 19 November 2026, about 13:40 to 14:10 UTC. The thirteen regions' files (`site/data/regions/index.json`, `mix/`, `trade/`, `demand/`) reached main at about 13:35 UTC with the landing of rows 41 and 42. Until then the region tabs had been seen only on the tests' made-up fixture. The same five readers were given a case each on the real files, in a real browser on a build of `wip/8602-grid-regions` merged with main, at 1280 px (cases 3 and 5 at 390 px too), by `runs/c504_region_read.mjs`; the pictures are `docs/reviews/grid-regions-2026-11-19/case*.png` and `also_*.png`.

### The five cases

1. **The transmission planner.** "The Mid-Atlantic and its neighbours this month: who takes its power, and do the two sides agree?" Address: `/grid?region=mida&view=gravity`.
2. **The power trader.** "Texas in July 2025: what made the power, hour by hour of the average day?" Address: `/grid?region=tex&period=2025-07`.
3. **The student.** "Tennessee, the region the Tennessee Valley Authority is: what generates its power?" Address: `/grid?region=ten`, at 1280 and 390 px.
4. **The siting analyst.** "The Southwest, where Phoenix is: what is the mix, and which balancing authorities are in it?" Addresses: `/grid?region=sw` and `/grid?region=sw&view=network`.
5. **The battery developer.** "California: when do the batteries charge and discharge, and how much?" Addresses: `/grid?region=cal` at 1280 and 390 px, and `/grid?region=cal&view=clean`.

### What each reader got

- **Case 1.** Answered, after the fix of row 21. In November 2026 the Mid-Atlantic's own reports give net exports of 595,806 MWh to New York and 471,694 MWh to the Midwest, and net imports of 388,607 MWh from the Carolinas and 247,551 MWh from Tennessee. New York's own report of the same flow is 739,194 MWh; over the 336 hours both reported, the gap is 92,049 MWh. "All neighbours" is blank, with its reason on hover (the Carolinas' row holds 228 hours, under half the month). Before the fix nothing said that November held 336 of its 721 hours, and the chart's last point fell beside whole months.
- **Case 2.** Answered. In July 2025 Texas made 45.1 percent of its power from natural gas, 19.2 from wind, 15.1 from solar, 12.8 from coal and 7.8 from nuclear; the average day, the hours and the years are drawn. One month of the 100 from July 2018 is not held (December 2025), and the page now says so. The picker's hover says in the data machine's sentence why Texas and ERCOT differ.
- **Case 3.** Answered for the mix, which the map could not give (row 15 of the first read is closed: TVA's panel now has its line "EIA region" and it opens Tennessee). In October 2026: nuclear 41.6 percent, natural gas 30.5, coal 15.5, hydro 9.6, solar 2.7. The latest hour held, 2026-11-17 05:00 UTC: demand 18,344 MW, net generation 16,689 MW, net imports 1,653 MW. Not answered: how clean it is (the Clean tab's three parts are blank for every region, row 6 and request 540). At 390 px nothing is wider than the screen.
- **Case 4.** Half answered. The region's latest hour, 2026-11-16 15:00 UTC: demand 12,180 MW, net generation 15,529 MW, net exports 3,731 MW; natural gas 40.4 percent, solar 27.1, nuclear 19.8. The Network tab lists its ten authorities, Salt River Project and Arizona Public Service among them, each opening its panel. Not answered: the mix of one authority (row 27), and the months: 40 of the 76 from May 2020 are not held and none after August 2026, which the page did not say (rows 19 and 20).
- **Case 5.** Not answered, and before the fix of row 22 answered wrongly: the Storage row read 6 MW in the latest hour and between minus 182 and 182 MW over the 35 days, which a reader would take for California's batteries. CAISO files no battery series in Form EIA-930, as the Storage page says; the row now says so on hover and points there. In the same file "Other" runs from minus 9,070 to 10,404 MW (row 23). The first chart of the 35 days could not be read at all (row 18).

### The rows

| # | Case | What the reader met | What it is | State |
|---:|---|---|---|---|
| 18 | all | "Generation by source, hour by hour: the last 35 days" was a comb of vertical lines: on the real files solar, hydro and storage are below zero for hundreds of the 840 hours, and the chart drew a line to zero at each crossing | Site fault of session 8602: the chart was the average day's, seen only on a fixture | fixed (session 8605): a chart of its own, `site/components/grid/RegionHours.tsx`, one column an hour, a source above zero up from zero and one below zero down from it (the mix library's own rule), an hour not held a gap, demand a line, the hour and every source's megawatts under the mouse, the same hours as a table. A first repair with the grids' time chart filled the plot with the crossing sources and was dropped |
| 19 | 4, 5 | California's month chips go from October 2026 to January 2026 with no word. 22 of its 83 months are absent; the Southwest 40 of 76, the Mid-Atlantic 57 of 97, Florida 35 of 97 | Site gap, and data: the data machine writes a month when at least 90 percent of its days hold every hour of every source (`docs/methods/regions_pages.md`) | fixed on the page: the count under the chips ("22 of the 83 months from December 2019 to October 2026 are not held"), the months named and the rule given on hover, up to three named in the line. Data request 544 asks which authority and source leave the days short |
| 20 | 4 | The Northwest opens on the average day of December 2025: no month of 2026 is in its file, and only the title said which month was shown | Site gap, and data (request 544) | fixed on the page: "No month from January 2026 to October 2026 is held: the newest month held is December 2025", the rule on hover. The Southwest (none after August 2026) and Florida (October 2026) say the same |
| 21 | 1 | November 2026 stood beside whole months with 336 of its 721 hours, and the chart's last point fell | Site gap: the file gives the hours of each month and the page did not use them | fixed: "November 2026 is a part of a month here: the region's own reports hold at most 336 of its 721 hours", and the same under the chart for its last point. A whole month says nothing |
| 22 | 5 | California's Storage row: 6 MW in the latest hour. New York's and the Mid-Atlantic's: 0 MW in every hour | Site gap: CAISO, NYISO and PJM file no battery series in Form EIA-930 (the Storage page, since session 34), and this tab did not say it | fixed: the Storage row says it on hover in both tables, for the three regions that hold one of them, and for California points to the Storage page. The figure is not changed |
| 23 | 5 | California's "Other" runs from minus 9,070 to 10,404 MW over the 35 days and is below zero at midday | Data question. My reading, not a held fact: CAISO's batteries are inside EIA's "Other" for California. The page does not say so, because no document of the ERW says so | data machine: request 544 |
| 24 | 3 | New York's and the Mid-Atlantic's Storage is 0 MW, not blank, in every hour, where NYISO and PJM file no series | Data question: a zero or a figure not held | data machine: request 544; the hover of row 22 says who files none |
| 25 | 4 | Florida's hours end at 2026-11-11 04:00 UTC in its mix file, where the index gives its last hour as 2026-11-17 04:00 UTC and the other regions' files run to 16 or 17 November | Data: the hourly window of Florida's mix file starts and ends six days early | data machine: request 544. The page says the hour it shows |
| 26 | 1, phone | At 390 px the trade chart's six month labels lay on one another | Site fault of session 8602 | fixed: a label a year; the check counts labels that touch |
| 27 | 4 | The analyst wants Salt River Project's own mix; a region gives its ten authorities together | Data: no file of the contract holds a mix by balancing authority | data machine: not asked tonight; named for a later chain |
| 28 | 2, 5 | The average day's chart draws a thin line down to zero where a source crosses zero (solar at dusk, storage, California's "Other") | The seven grids' own chart (`components/mix/Charts.tsx`, the same on CAISO's Mix tab). Changing it changes the seven grids' tabs, which this chain leaves as they are | ruling: for Samuel. Default taken: left as the grids have it |
| 29 | 1 | A hover read "Carolinas's own balancing authorities" | Site fault: a name ending in s | fixed: "the region's own" |
| 30 | 1 | New York's own report less its neighbour's is not the gap shown (minus 595,806 and minus 739,194 give 143,388; the gap is 92,049) | Not a fault: the gap is over the hours both reported (336), the neighbour's report over its own 361; the column heads say so on hover | not a fault |
| 31 | 1 of the first read | The map and the panel say PJM was a net exporter of 811 MW late on 16 November. PJM's own total interchange for that hour, as it files it with EIA, is 82 MW exported | Found by the done line's cross-check (session 8606, `replication/grid/crosscheck_map.csv`): the map's net exchange is the sum of the pairs, each read from one side by the pair rule, and the two sides of a tie need not agree. Each of the 159 pairs is the report EIA publishes, to 1 MW; the sum differs from the authority's own total for 21 of 60 authorities (CAISO: 4,119 MW imported by the pairs, 5,076 MW by its own total) | ruling: whether the hover and the panel should carry the authority's own total beside the sum. Default taken: the sum, as the Network view has had it; the difference is now said in the map's decisions block, with the two figures and their source |
| 32 | 3, 5 | "Wind 0 MW, 0.0%" for the Carolinas; storage 0 MW for New York and the Mid-Atlantic | Found by the cross-check (`replication/grid/crosscheck_regions.csv`): EIA returns no code at all for those sources in those regions, and the files write 0. A figure not held drawn as zero | data machine: request 551, point 1 |
| 33 | 5 | California's "other" below zero at midday (row 23) | The cross-check settles what the figure is: in the hour to 2026-11-08 19:00 UTC EIA's own code OTH for California is minus 10,253 MW and its battery code BAT minus 151 MW; the file's "other" is EIA's four codes summed, to the megawatt. What is inside EIA's OTH is EIA's to say | ruling: whether the page should say that California's "other" goes below zero, and how. Default taken: the page says nothing beyond the figure and the Storage row's hover |

### What this read changed on the page

Six site faults or gaps fixed at their cause, each with a test in `tests/test_session8605.py` (rows 18, 19, 20, 21, 22, 26) and one wording (29). Four rows are the data machine's, in one request (544: rows 19 and 20's cause, 23, 24, 25). One is a ruling with the default taken (28). `site/scripts/check-grid-regions.mjs` on the real files: 25 of 25.

## A second read of the map (session 8612)

Session 8612, 19 November 2026, about 16:25 to 16:35 UTC, on a build of `wip/8602-grid-regions`. The same five readers, each with a case on what the first read did not touch, by `runs/c504_read_map2.mjs` (what the page said: `runs/c504_read_map2.out`; pictures `docs/reviews/grid-map-2026-11-19/case6*.png` to `case10*.png`).

### The five cases

6. **The transmission planner.** "A day from the archive: Winter Storm Elliott, 23 December 2022. Where did PJM send power that day?" The map, then 2022-12-23 in "A day since 2019".
7. **The power trader.** "The June 2025 heat: what was New England taking, from whom, at what price?" The map, then the story "The June 2025 heat".
8. **The student.** "The Southwest as a region: which balancing authorities, and the Salt River Project among them on the map." `/grid?region=sw&view=network&shape=map`, at 1280 and 390 px.
9. **The siting analyst.** "Play the year: how does Arizona's trade move through 2026?" The map, then "Play the year".
10. **The battery developer.** "ERCOT's batteries this week: charging or discharging, and how much?" `/grid?grid=ercot&view=network&shape=map&batteries=1`.

### What each reader got

- **Case 6.** Answered. On 23 December 2022 (EIA's Eastern day, the day's average) PJM was a net exporter of 7,481 MW over seven ties: 3,197 MW to MISO, 1,879 MW to the Tennessee Valley Authority, 1,226 MW to NYISO. PJM's demand averaged 112,989 MW; TVA was a net importer of 5,789 MW. The address holds the day (`net=day&t=2022-12-23`); the slider steps day by day through the year.
- **Case 7.** Answered. Early on 20 June 2025 New England was a net importer of 1,160 MW over three ties (848 MW from New York), on 13,057 MW of demand; its panel gives the hub price that hour (35.52 USD/MWh in real time). The story plays as soon as it is pressed, so three hovers a moment apart read three hours (row 38).
- **Case 8.** Answered after the fix of row 35. The list names the region's ten authorities; the Salt River Project's hover on the map gives its figures. Before the fix a click on it in the list opened its panel in the 3D network and the map was gone.
- **Case 9.** Answered. The year plays at about five days a second (8 January to 8 March 2026 in twelve seconds); a hover answers while it plays (Arizona Public Service on 9 March: demand 3,916 MW on average, net imports 1,607 MW over eight ties); stopped, the address holds the day.
- **Case 10.** Not answered as the page stood: at the hour the map opens on, ERCOT's batteries read "not reported for this hour" and no ring is drawn anywhere, with no word on where a report is. Thirty hours back five grids report (ERCOT charging 978 MW at 2026-11-15 22:00 UTC). After the fix of row 36 the map says so and names the newest hour that holds a report.

### The rows

| # | Case | What the reader met | What it is | State |
|---:|---|---|---|---|
| 34 | 7, 9 | While a story or the year plays, the address does not name it (it reads `?grid=us48&view=network&shape=map`); paused, it does (`net=east_heat_2025&t=...`). The page says "The address holds what you are looking at: copy it to share the view" | The network's own rule, in both shapes and on production: "while it plays the address would change five times a second" (`site/app/network/Network.tsx`) | ruling: whether the address should take the story's name at once and the hour when it is paused. Default taken: left as the network has it |
| 35 | 8 | In the Map shape, a click on an authority in a region's list opened its panel in the 3D network: the map was gone | Site fault of session 8602: the list's links are drawn on the server, which does not know the shape the reader switched to | fixed (session 8612): the link keeps the shape (`site/components/grid/BaLink.tsx`, `keepShape`); a check clicks one in the Map shape |
| 36 | 10 | With the Batteries switch on, the map opened on an hour with no battery report: no ring, and nothing said | Site gap, made visible by the live set's lag (request 543) | fixed (session 8612): under the map, "No battery is reported for this hour. The newest hour of this view that holds a report: 2026-11-16 07:00 UTC (1 grid). Move the slider there to see the rings." With a ring drawn the line is not there |
| 37 | 6 | In a replayed day a region's carbon intensity is a whole number (405 kg CO2/MWh) where the live hour gives two decimals (405.71) | Two tables: the day's figure is `carbon_intensity_daily`, the hour's `carbon_intensity_hourly`; each is shown as the Network view's panel shows it | not a fault |
| 38 | 7 | A story plays as soon as it is pressed, so a hover's hour moves on under the reader | "Watch" plays; Pause stops it, and the address then holds the hour | not a fault |

### What the second read changed on the page

Two site faults fixed at their cause, each with a test in `tests/test_session8612.py` (rows 35 and 36). One ruling with the default taken (34). On a build: `check-grid-map.mjs` 53 of 53, `check-grid-regions.mjs` 26 of 26.

## A second read of the regions (session 8613)

Session 8613, 19 November 2026, about 16:42 to 16:50 UTC, on a build of `wip/8602-grid-regions` with the data machine's real files, by `runs/c504_region_read2.mjs` (what the page said: `runs/c504_region_read2b.out`; pictures `docs/reviews/grid-regions-2026-11-19/case11*.png` to `case15*.png`). The same five readers, each on a control the first read did not exercise.

### The five cases

11. **The transmission planner.** "New England and Canada in January 2026, and the months before." The trade tab, a past month, the chart's Table.
12. **The power trader.** "The Midwest over the whole of 2025: what made the power?" The Mix tab with a year as the period.
13. **The student.** "New York in July, year after year; and how New York the region differs from NYISO." The calendar months, the picker's hover, the Clean tab.
14. **The siting analyst.** "From the Central region to the Southwest, then to ERCOT, without losing the tab." The two pickers.
15. **The battery developer.** "Texas's batteries hour by hour: when do they charge, when do they discharge, and how much?" The hour by hour chart, its Table, a phone.

### What each reader got

- **Case 11.** Answered for January 2026: New England took 951,533 MWh from New York (New York's own report: 953,454) and 184,354 MWh from Canada, whose side files nothing. The chart's Table lists 36 months with the same figures. Before the fix of row 39 no control reached a month older than November 2025, though the file goes back to July 2018.
- **Case 12.** Answered. Over 2025 the Midwest made 35.4 percent of its power from natural gas, 31.7 from coal, 13.6 from wind, 12.8 from nuclear. Before the fix of row 40 the line under the shares read "301 days held", with no word that January and February are not in the year.
- **Case 13.** Answered for the load: New York's July net load by hour for nine years, with each year's midday low, evening high and ramp, and a box of every year's figure under the pointer. The picker's hover says why New York and NYISO can differ. Not answered: how clean (the Clean tab is blank for every region; request 540).
- **Case 14.** Answered. The region picker keeps the tab (Central's trade to the Southwest's trade); the grid picker opens ERCOT on the same tab.
- **Case 15.** Answered. On 6 and 7 November the batteries of Texas charged 2,622 MW at 18:00 UTC with 27,865 MW of solar, discharged 5,213 MW at 00:00 UTC as the sun was gone, and charged 3,866 MW at 17:00 UTC the next day. The Table holds the 840 hours with its head kept in place; at 390 px the names stand at the right, inside the screen.

### The rows

| # | Case | What the reader met | What it is | State |
|---:|---|---|---|---|
| 39 | 11 | The trade tab offered the newest thirteen months and no way to an older one; the file holds 101, from July 2018 | Site gap of session 8602 | fixed (session 8613): a row of years, every year the file holds; the months offered are those of the year shown; a year opens on its newest month. The check opens 2018 and reads the file's figures |
| 40 | 12 | With a year as the period, "301 days held" and not of which months | Site gap: the file's year says how many months it holds, how many were due and which are missing, and the page did not use it | fixed (session 8613): "301 days held, in 10 of the year's 12 months (not held: January 2025, February 2025)"; for the year in progress, "of the year's 11 months so far" |
| 41 | 11 | The chart of trade draws the newest 36 months, whatever month is chosen | The chart's own span, said in its title ("2023-12 to 2026-11"); the months before are reached by the years' row and read in the table | not a fault |

### What the second read of the regions changed on the page

Two site gaps fixed at their cause, each with a test in `tests/test_session8613.py` (rows 39 and 40). On a build of the real files: `check-grid-regions.mjs` 28 of 28; the replication read again, 1,375 of 1,375.

## A finger on a phone (session 8614)

Session 8614, 19 November 2026, about 17:47 to 17:53 UTC. The read of the resource map found that a finger's tap showed no value there, and that every read at 390 px so far had pointed with a mouse. The Grid tool's two new views were then tapped with a finger at 390 px on a build (`runs/c504_finger_tap.mjs`).

- **The map of balancing authorities.** Built for a finger since session 8601: a tap on a region opens its panel, a finger on a tie shows the tie's figures, two fingers zoom. Its check uses fingers. Nothing to change. (Session 8616: the check had tried the tie, the two fingers and the one finger's move, and not the tap on a region; it does now, and the tap opens the region's panel with the address naming it. Picture `docs/reviews/grid-map-2026-11-19/map_390_region_tap.png`; `check-grid-map.mjs` 54 of 54.)
- **The hour by hour chart of a region.** A tap showed nothing (row 42).

| # | Case | What the reader met | What it is | State |
|---:|---|---|---|---|
| 42 | 15 | On a phone a tap on the hour by hour chart showed no card; the hour's figures could be read only in the chart's Table | Site fault of session 8605: the card came up on a pointer's move, and a tap is a press and a lift with no move; the lift is also the touch pointer's leave | fixed (session 8614): a finger's press reads the hour, and a touch's leave is let pass, so the card stays until the next tap. The check taps with a finger at 390 px (picture `region_car_mix_390_tap.png`) |

One site fault fixed at its cause with a test in `tests/test_session8614.py`. On a build: `check-grid-regions.mjs` 30 of 30, `check-grid-map.mjs` 53 of 53.
