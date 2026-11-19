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
| 2 | 3 | The coal fields' area is in square kilometres; the basins' and the plays' areas are in square miles | Data: the coal fields' area is the data machine's own, computed on a sphere from the outline; the other two are the publisher's figures | data machine: request 552 asks for the area in square miles too, or the reason for the unit. The page shows each as its file gives it |
| 3 | 3 | In the method note under the map, the coal fields' "What it is not" begins with a file's name: "docs/methods/resource_layers_table.md. An outline of where coal fields lie ..." | Data: the entry's `notes_for_method`, shown as written | data machine: request 552 |
| 4 | 4 | "Datacenters: not read: license needed", with the publishers named | The table is held for a license; a held value is drawn blank with its reason | not a fault |
| 5 | 2 | At 31.80 N, 102.50 W the hover names the Permian basin and no play | The file's plays do not cover the point; the plays' outlines are EIA's general areas | not a fault |
| 6 | 1, 4, 5 | Every hover of a wind or sun layer repeats the file's vintage sentence, three lines of small words under the figure | The page's words since the layers were added (the vintage and the publisher with every value, so that every figure is sourced where it is read) | ruling: for Samuel, whether the sentence could stand once, in the legend. Default taken: left as it is |
| 7 | 3, 4 | Uranium and critical minerals are greyed | The two USGS hosts that serve them refuse automated reading | ruling: for Samuel (a person could download the two files by hand). Default taken: not fetched |
| 8 | 3 | On a phone the hover's card covers a third of the map while a finger rests on it | The card stands beside the finger and goes when the finger lifts | not a fault |

## What the read changed on the page

One site gap fixed at its cause with a test (row 1). Two rows are the data machine's, in one request (552). Two are rulings with the default taken (6 and 7).
