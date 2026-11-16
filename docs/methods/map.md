# The project map (`/map`): the tool as a reader meets it

Energy Research Warehouse (ERW). Session 7601 (chain 305), 16 November 2026. This note is the tool's: its three tabs, every figure it draws with the table and the rule behind it, each choice that moves a figure with its default and its source, and what the tool does not hold. It points to the tables' own notes and does not repeat them: [`energy_projects.md`](energy_projects.md) (the table, its coordinates, its technology groups, and the page's history in "The page: /map, one page"), [`eia860m_operating_generators.md`](eia860m_operating_generators.md) and [`eia860m_planned_generators.md`](eia860m_planned_generators.md), [`datacenter_facilities.md`](datacenter_facilities.md), [`resources.md`](resources.md) (every resource layer) and "Queue statistics" in `energy_projects.md` (the Queues tab's table).

The replication is `replication/map/` (section 13). It is written from this note and reads the generating units from EIA's own workbook, not from an ERW table.

## 1. The three tabs

| Tab | Address | What it draws | Computed where |
|---|---|---|---|
| Projects | `/map` | Every generating unit of EIA's monthly inventory, operating and planned; the queue positions of four grid operators that are not withdrawn; the datacenters the tracker places in a US state. A sentence, totals by status, a map, a table by technology, a card for a row | In the reader's browser, from the page's own file |
| Resources | `/map?tab=resources` | The 14 natural resource layers of the list of layers, each a publisher's file (wind, sun, geothermal, hydropower, biomass, oil and gas basins and plays, offshore wind leases), with the units, the queue and the datacenters laid over them | Nothing is computed: a hover reads the stored value of the cell or the row under the pointer |
| Queues | `/map?tab=queues&iso=caiso` | One grid operator's queue by the year a position entered it: entered, reached operation, withdrawn, still waiting, the withdrawal rate, the median wait | Nothing is computed: every figure is a row of `iso_queue_statistics` as the live set holds it |

## 2. What the Projects tab reads

One file, `site/data/map.json`, written by `warehouse/derived/project_map.py` from four tables. The tab asks no server for a figure. The file names its own month and days: on 16 November 2026, EIA's inventory of 2026-09 (retrieved 24 October 2026), the queue positions of 2026-10-26, the tracker of 2026-11-15, built 15 November 2026.

The one figure of the tab read from the live set is the count of queue positions that are not on the map (the second paragraph): the rows of `energy_projects` of kind `queue` whose `geo_precision` is `none`.

## 3. The four kinds

| Kind | Rows of | Which rows |
|---|---|---|
| Operating units | `eia860m_operating_generators` (EIA's sheets Operating and Operating_PR) | every row |
| Planned units | `eia860m_planned_generators` (EIA's sheets Planned and Planned_PR) | every row |
| Queue positions | `energy_projects`, kind `queue` | status not `withdrawn`, and of a queue that may be drawn (section 6) |
| Datacenters | `datacenter_facilities` | the facilities whose `state` is not empty (a US state) |

A row is a generating unit, not a plant. MW is never added across kinds: a unit's nameplate, a queue position's request and a datacenter's stated load are three different things.

## 4. A unit's grid

EIA's balancing authority code for the unit. Seven codes are a grid by name: ERCO (ERCOT), CISO (CAISO), PJM, MISO, SWPP (SPP), NYIS (NYISO), ISNE (ISO-NE). Every other code, and a unit with no code, is "Outside the seven ISOs". A unit with no code is one whose cell EIA leaves blank (727 in the inventory of 2026-09: 508 in Alaska, 184 in Hawaii, 35 in Puerto Rico) or fills with the text "NA" (246: 196 in Puerto Rico, 38 in Alaska, 7 in Hawaii, 4 in Rhode Island, 1 in Maine): 973 in all, the file's `counts.without_balancing_authority`. A queue position's grid is the grid operator whose queue it is. A datacenter's grid is "Grid not stated": the tracker's own grid is not read by the map.

## 5. A unit's technology group

EIA's technology, grouped. The group of each of EIA's 27 technologies:

| Group | EIA's technology |
|---|---|
| Solar | Solar Photovoltaic; Solar Thermal with Energy Storage; Solar Thermal without Energy Storage |
| Wind | Onshore Wind Turbine; Offshore Wind Turbine |
| Batteries | Batteries, Flywheels, Hydroelectric Pumped Storage and Natural Gas with Compressed Air Storage whose prime mover code is BA |
| Other storage | the same four technologies with any other prime mover |
| Natural gas | Natural Gas Fired Combined Cycle; Natural Gas Fired Combustion Turbine; Natural Gas Internal Combustion Engine; Natural Gas Steam Turbine; Other Natural Gas |
| Coal | Conventional Steam Coal; Coal Integrated Gasification Combined Cycle |
| Nuclear | Nuclear |
| Hydro | Conventional Hydroelectric |
| Geothermal | Geothermal |
| Petroleum | Petroleum Liquids; Petroleum Coke |
| Biomass | Wood/Wood Waste Biomass; Landfill Gas; Municipal Solid Waste; Other Waste Biomass |
| Other | Other Gases; All Other |
| Not stated | a unit with no technology |

A queue position's group is the table's `technology_group` (the grid operator's own fuel text, grouped as `energy_projects.md` says), with two changes: `storage` is drawn as "Storage (queue positions)", since a queue does not say what kind of storage; no group is "Not stated". A datacenter has no technology: it is "Datacenter (a load)" and is left out of the table by technology.

## 6. A row's status, and which queues are drawn

- **An operating unit** is "Operating" whatever EIA's code (OP, SB, OA, OS); its card names EIA's own label when the code is not OP.
- **A planned unit** keeps EIA's own status code, the letters in brackets that open the workbook's Status cell: P, L, T, U, V, TS, OT, in the plain words of `energy_projects.md`, "Statuses".
- **A queue position** shows the table's standard status: active, suspended, completed, or not stated. Withdrawn positions are not on the map.
- **A datacenter** shows the tracker's cleaned status.
- **The queues drawn:** ERCOT's, SPP's, CAISO's and ISO-NE's. MISO's and NYISO's are held back (the one list a person switches is `QUEUE_GRIDS` in `site/lib/resources.ts`); the ERW holds no queue of PJM.

## 7. A row's megawatts

- A unit: EIA's nameplate capacity, as the workbook gives it (one decimal).
- A queue position: the megawatts requested, kept to one decimal in the page's file. A sum of the file's megawatts can therefore stand a megawatt from the same sum over the table's own figures: on the file of 15 November the sentence reads 761,479 MW requested, and the table's own figures sum to 761,478.2.
- A datacenter: the megawatts a story or the operator states, where one does; the count of facilities that state one is given beside the sum.
- A row with no megawatts is in the counts and in no sum, and is left out as soon as a size is asked for: it cannot be said to fit one.

## 8. A view: the choices and the address

Five lists (kind, grid, technology, status, state) and a size from and to. The address keeps the choice: `?kind=operating,planned&grid=ercot&tech=solar,battery&status=u,v&state=TX,CA&min=100&max=500`. A list is slugs with commas between them. A list that is absent or empty means every option; `none` means none; a slug the page does not know is passed over, and a list none of whose slugs is known means every option. A state's slug is its postal code; `na` is a row whose source names no state. A size is a number at or above zero; both ends are counted in (`min=100` keeps a unit of exactly 100 MW).

Since session 7537 (the read of 16 November 2026, `docs/reviews/map-read-2026-11-16.md`), a point and a distance: `?at=32.4487,-99.7331&within=30`, typed in the panel as "Near a point" (latitude, longitude in decimal degrees, the form a web map copies) or set from a row's card ("Measure from this row"). Both are needed; one alone chooses nothing. A row is kept when the great-circle distance from the point to the row's own point, on a sphere of the Earth's mean radius (3,958.8 miles, the haversine formula), is at or under the distance. The row's own point is EIA's coordinates for a unit, the county's or the town's internal point for a queue position, the city's point for a datacenter (the file's precision code, drawn as "Placed at"): a queue position is kept when its county's point is inside, wherever its site is. A row with no point is left out once a distance is asked for. The point and the circle are drawn on the map.

## 9. The drawing

The plane is the Albers projection the state outlines are drawn with (us-atlas: scale 1300, the centre at 487.5 and 305): the lower 48 in one conic equal-area projection, Alaska and Hawaii each in its own, in a box at the lower left. A row is drawn when its source gives a latitude and a longitude and the place falls inside one of the three boxes. Puerto Rico falls in none. The line under the map's heading counts the rows chosen that are not drawn; they are in the totals and the table. A unit is at EIA's own coordinates; a queue position at its county's or its town's point from the Census Bureau's gazetteer, not at its site (`energy_projects.md`, "Coordinates").

## 10. The figures of a view

| Figure | Rule |
|---|---|
| The sentence: generating units and their MW | the count of the operating and planned units chosen; the sum of their megawatts, rounded once to the megawatt |
| The sentence: queue positions and MW requested | the count of the queue positions chosen; the sum of their megawatts |
| The sentence: datacenters, MW stated, at how many | the count; the sum over the facilities that state megawatts; how many state them |
| A tile, by status | for each status with a row chosen: the sum of megawatts, and the count under it. Units are grouped under "by EIA's status", queue positions and datacenters each under their own heading |
| The map | the count of rows drawn (its accessible name), and the count not drawn (section 9) |
| By technology | for each technology group and each of the kinds chosen among operating, planned and queue: the count and the megawatts |
| A mark's hover and a row's card | the row's own fields, as the file holds them |
| The list under the map, when a point and a distance are chosen (session 7537) | every row chosen, nearest first (the file's order among equals; the nearest 1,000 drawn, the count of all given): miles to a tenth, name, kind, technology group, status, MW, the date and what it is (began operating, planned operation, entered the queue, planned year as stated), and "Placed at". ERCOT's queue status "completed" reads "Agreement signed, built or not": ERCOT's report has no status column (`energy_projects.md`, "ERCOT's 'Completed' is not ERCOT's word") |
| The line on the queues drawn (session 7537) | when queue positions are chosen and a grid chosen has no queue position in the file: the grids whose queues the file holds and those it holds none of, read from the file's rows |

## 11. The file's own counts

`counts` in the file: the rows of each kind and their megawatts; `units` and `units_mw` (the two EIA kinds together); `batteries` (section 5); `under_1_mw` (units under 1 MW: each is at a plant that passes EIA's threshold of 1 MW of combined nameplate); `without_balancing_authority` (section 4); `without_mw` (rows of any kind that state none); `not_placed` (rows whose source gives no location); `datacenters_without_state` (facilities the tracker places in no US state, counted and not written); `queue_rows_held` (positions of a queue held back that the table holds: none since the table itself stopped holding them).

## 12. What published figures stand against

EIA publishes its own totals of the same inventory: the Electric Power Monthly, Table 6.1, "Electric Generating Summer Capacity Changes (MW)", net summer capacity of utility-scale facilities in service at the end of a month, by technology. It differs from the map's figure in two ways, both EIA's own: it is one month behind the inventory (the table read on 16 November 2026 is of the end of August 2026; the map holds September 2026), and it is net summer capacity where the map sums nameplate. So the cross-check (`replication/map/crosscheck.py`, `crosscheck.csv`) sets three columns side by side for each of EIA's 27 technologies: the map's nameplate megawatts; the same operating units' net summer megawatts from the same workbook, for the 50 states and the District of Columbia; EIA's table.

- For 18 of the 27 technologies the two net summer figures are the same to the tenth of a megawatt (nuclear 98,423.3; conventional steam coal 167,235.5; natural gas combined cycle 295,138.4; conventional hydroelectric 80,046.2).
- The others differ by what a month added or took away: solar photovoltaic 169,644.1 against 166,677.0 (2,967.1 more, 1.78 percent); batteries 55,707.8 against 54,097.0 (1,610.8 more, 2.98 percent); natural gas combustion turbines 491.7 more; onshore wind 224.8 more; geothermal 30.0 more; landfill gas 4.0 less; petroleum liquids 3.6 less.
- Every technology together: 1,324,124.6 MW net summer in the map's units against 1,318,801.0 MW in EIA's table: 5,323.6 MW more, 0.40 percent, one month of change.
- The map's own figure, nameplate, is 1,423,491.7 MW for the same 28,712 units: 7.5 percent above their net summer capacity. A reader comparing the map with a published "US capacity" should expect that gap; it is the difference of the two measures, not of the units.
- The queue positions and the Queues tab: the cross-check against Berkeley Lab's Queued Up is in `energy_projects.md`, "The cross-check against LBNL's Queued Up". The datacenters: the tracker's own cross-check (`datacenter_tracker.md` once chain 303's stack lands).

No figure is adjusted to match.

## 13. The replication

`replication/map/`:

- `fetch_rows.py` reads EIA's own workbook of the month the page's file names (from the address the file carries), the queue positions of `energy_projects` and the facilities of `datacenter_facilities` from the live set, into `rows/` (never in git: the tracker's rows are held).
- `site/scripts/map-figures.mjs` runs the page's own functions on the page's own file for 123 views (no choice; every option of the five lists alone; 20 combinations) and writes the figure the page draws for each: 6,094 figures.
- `replicate.py` computes each of them again from the rows by sections 3 to 11 of this note, and compares a row's own fields (grid, technology, status, state, MW, latitude, longitude) for every row in both. `page_figures.json` and `page_figures.csv` hold both sides.
- `replicate.do` gives the five headline figures in Stata from `rows/units.csv`, with the expected values at its top.
- `crosscheck.py` is section 12.

On 16 November 2026: the figures that read the generating units alone, 3,790 of 3,790 inside half a megawatt or half a row; 31,071 of the 31,073 units carry the same seven fields on both sides and the other two differ in their id alone (section 15); the 278 datacenters the same. The queue positions are of another day in the page's copy (26 October) than in the live set (5 November): 3,631 are in both, 70 of them with a field that differs, 78 only on the page, 53 only in the live set, and the 301 figures that sum them differ for that reason and are named, each with both sides.

## 14. The decisions of the tool

Each is on the page, in "Decisions on this page", with its default and its source on hover.

| Choice | Default | Source |
|---|---|---|
| What a unit's megawatts are | Nameplate capacity | EIA, Form EIA-860M, "Nameplate Capacity (MW)". Net summer capacity is lower: 7.5 percent lower over the operating units of 2026-09 (section 12) |
| Megawatts are never added across kinds | Each kind has its own count and sum | A queue position is a request and most are withdrawn before they are built (`energy_projects.md`); a datacenter's megawatts are a stated load |
| Which queue positions are on the map | Not withdrawn: active, suspended, completed, not stated | Version 1 of the map (session 16); a completed position may be a unit the inventory already lists, which is one reason megawatts are not added across kinds |
| Which queues are drawn | ERCOT, SPP, CAISO, ISO-NE | The terms of each grid operator: MISO's pulls are paused (`miso_pause.md`), NYISO's notice confers no license |
| A unit's grid | EIA's balancing authority code; no code is "Outside the seven ISOs" | EIA, Form EIA-860M, "Balancing Authority Code" |
| What a battery is | A storage unit whose prime mover code is BA | EIA, Form EIA-860 instructions, prime mover codes |
| A planned unit's status | EIA's own seven codes, not folded into "planned" and "under construction" | EIA, Form EIA-860 instructions; the owner's words of 8 October 2026 |
| Where a queue position is drawn | Its county's, city's or town's internal point | U.S. Census Bureau, 2025 Gazetteer Files; no fuzzy matching (`energy_projects.md`, "Coordinates") |
| A row with no megawatts and a size asked for | Left out | It cannot be said to fit a size |
| A distance from a point (session 7537) | No point: every row; both ends counted in; a row with no point left out once a distance is asked for | The great-circle distance (haversine) on a sphere of 3,958.8 miles, from the row's own point: EIA's coordinates, the county's or town's point for a queue position, the city's point for a datacenter (`docs/reviews/map-read-2026-11-16.md`, row 1) |
| Which datacenters are drawn | Those the tracker places in a US state | The map is of the United States (`datacenter_facilities.md`) |
| Retired units | Not on the map | They are in `eia860m_retired_generators` |

## 15. What the tool does not hold

- Units under 1 megawatt at plants under EIA's threshold; rooftop solar and other small generators.
- Retired units, and anything since the inventory's month.
- A planned battery's energy in megawatt-hours: the inventory gives its power alone.
- Projects that have told no one but a grid operator are queue positions, not planned units; MISO's, NYISO's and PJM's queue positions are not drawn at all.
- A place for Puerto Rico's units on the drawing (they are in the totals).
- A queue position's site: it is at its county's or its town's point.
- Two units' generator ids: EIA's workbook gives "NA" as the generator id of Cranberry Point Energy Storage (plant 62844) and Silver Queen Wind Farm (plant 64835), and the two tables hold them with no generator id (`eia860:62844:`), so their cards show the id cut short. Their other fields are EIA's. (Faults row 2 of `docs/reviews/map-faults-2026-11-16.md`.)
- The datacenters and ISO-NE's queue positions are drawn from the page's file while the tables they come from are held for a license: an open ruling (`docs/reviews/datacenter-faults-2026-11-11.md`, row 7).
- A census of datacenters: the tracker holds the facilities the news names since 2025, the operators' public site lists it reads, and the queue positions that name a large load.
