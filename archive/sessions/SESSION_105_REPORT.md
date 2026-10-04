# Session 105 report: the project map, version 2

**Built and on the live site, in review at `/map/v2`.** Every operating and planned generating unit of EIA's monthly inventory (Form EIA-860M, August 2026), batteries among them, on a map: 30,921 units and 1,706,668 MW. Chosen by grid, technology, status and size, with the interconnection queue's active capacity for the same grid beside it and a table of what is selected. The page states what the inventory leaves out. The older map, `/map`, is untouched. One deploy; the 25 live pages differ only in the home page's 15-minute prices.

## Read these first

1. **The queue is beside the inventory and never added to it.** They are two sources with different regions and different technologies, and a request is not a plant. For a grid of the map the page shows Berkeley Lab's row for that grid; for "outside the seven ISOs" it shows the queue's West and Southeast apart; for every grid, the queue's row for all regions. When a technology is chosen, the queue's rows that answer to it are marked (a battery answers to "storage, batteries alone" and to "solar with storage") and nothing is summed across them. The note under the table says so.
2. **8,957 units are "outside the seven ISOs", and 975 of them have no balancing authority in the inventory at all.** The grid of a unit is EIA's balancing authority code for it. The seven ISOs are named; every other balancing authority is one group, and the 975 blank ones are counted there. The page says so. A filter by each of the other balancing authorities would be a small addition.
3. **"Batteries" are the storage units whose prime mover is a battery: 1,619 units.** Pumped storage and the rest are "other storage" (167 units). The inventory's own group is "storage" for both.
4. **Puerto Rico's units are in the totals and the table and not on the drawing.** The map's projection (the one the older map and the state outlines use) has no place for them; the page counts them where they are selected.
5. **`/shoulder` on production still shows the table as it was before session 103's load** (checked again at 20:28 UTC: 99 of 3,482 checks differ). The load was at about 20:00 and the page keeps its reads for an hour, so this is still inside the hour. I will check after 21:00 UTC and say in session 106's report what it shows.

## The page

`/map/v2`, in review, in the battery page's layout: the header with the inventory's totals, a panel of four choices on the left (grid, technology, status, a size from and to in MW), then a sentence, three headline numbers (MW operating, under construction, planned), the map, the queue beside it, the table, two folds and the source line.

- **The map.** A dot is an operating unit; a ring is one under construction (the heavier ring) or planned. Color is technology, in the site's eight fuel colors; size grows with MW. Drag, zoom, hover for a unit's name, technology, MW, status, state, grid and year.
- **The table.** The fifty largest units selected, with a button for all of them: plant, state, grid, technology, status, MW, year.
- **Everything is computed in the browser** from the page's own copy of the inventory. A choice asks no server for anything.

**What the inventory leaves out, as the page states it:**

- Plants under 1 megawatt, in EIA's own words from its page for the form (read today): "existing and proposed generating units at electric power plants with 1 megawatt or greater of combined nameplate capacity". Rooftop solar is not in it. 3,868 units in the file are smaller than 1 MW; each is at a plant that passes the threshold.
- Retired units (they are in `eia860m_retired_generators`, not on this map).
- Projects known only to a grid operator: a planned unit is one its owner has reported to EIA.
- A grid for the 975 units with no balancing authority.
- Energy (MWh) for planned batteries: the inventory gives them power only.
- The 233 units in Puerto Rico, on the drawing.
- Anything since August 2026.

## What was built

| File | What |
|---|---|
| `warehouse/derived/project_map.py` | Writes `site/data/map_v2.json` from `eia860m_operating_generators` and `eia860m_planned_generators`: one compact column a field, a unit a position, largest first. No request, no warehouse table: the units are the two tables' rows, unchanged. Built by hand when a new month is in the warehouse, like the network's replay files |
| `site/lib/map2.ts` | The selection, the totals and the queue rows, apart from the page |
| `site/app/map/v2/` | The page (projects each unit onto the map's plane on the server) and its browser part |
| `site/scripts/check-map-v2.mjs` | Drives the page in a real browser |
| `tests/test_session105.py` | 7 tests |

No table was added, so nothing went to coverage, the archive, Redivis or Supabase. The file is 1.6 MB in the repository; the page's HTML carries the units to the browser, as the older map's does.

## Tests and checks

- **The site's copy is the two tables, unit for unit:** name, state, grid, technology, status, MW and year of all 30,921 units equal the tables' rows; the counts of units without a balancing authority, under 1 MW and of batteries equal the tables'.
- **The page's selection is the tables' own** for seven choices (every unit; ERCOT; ERCOT's batteries; California's solar under construction; nuclear outside the ISOs from 500 to 1,300 MW; PJM's planned gas; every unit under 1 MW): units, MW and the count by status.
- **The queue beside the map is the queue summary's** for ERCOT, for outside the ISOs and for all regions; a region with no request of a kind says "none in the file", never a zero.
- **In a browser, on this machine's build and on production: 41 of 41 checks.** A visitor gets the in-review page. In the internal view: the sentence, the three totals, the count of units drawn and the table's first row are the file's after each of a grid, a technology, a status and a size; a size no unit has says so; the queue's MW is the queue file's and the right rows are marked.
- The workflow (run 37232224207) passed and merged (`d9cc502`); Vercel accepted the deployment. The route check on this machine's build: 0 failed.

## Every difference, the 25 live pages

`before-105` (20:28 UTC) against `after-105` (20:35 UTC): 26 differences, all on the home page, all the latest real-time prices and their lines (the 15-minute feed). `/network` and the other 23 pages: 0.

## Errors and decisions

1. **EIA's sentence was read with a plain request to EIA's public page for the form,** not through a model. One request, to `eia.gov`, for documentation; no data was pulled.
2. **A unit, not a plant.** The inventory's row is a generating unit, and the page keeps it: a plant with four turbines is four rows. Grouping by plant would hide a planned unit at an operating plant.
3. **The size filter is on the unit's nameplate MW.**
4. **No model call, no pull, no table, no load. Model spend USD 0.00.**

## For Samuel

1. **The other balancing authorities by name** (second point above), if the map is to serve the West and the Southeast as well as it serves the ISOs.
2. **The file wants a line in the monthly routine:** `python warehouse/derived/project_map.py` after the EIA-860M connector has a new month, then a commit of `site/data/map_v2.json`.
3. **When it replaces `/map`:** version 2 leaves out the queue positions and the datacenters the older map draws as points. They could be a fifth choice.

Energy Research Warehouse (ERW), session 105, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 20:22 to 20:40 UTC, unattended.
