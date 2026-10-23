# Method: energy projects for the project map

> **MISO is paused (4 October 2026).** MISO's terms forbid automated access to its site, so every pull of MISO's own servers is paused pending a review; MISO's interconnection queue stays as of its last weekly pull. What is held stays as it is. [`miso_pause.md`](miso_pause.md)

Energy Research Warehouse (ERW), session 16. Table: `energy_projects` (entities shape, derived, public). Code: `warehouse/derived/energy_projects.py`. The map that reads it: the site's `/map` (platform tool 3).

## What it is

One table that puts every generator EIA lists and every interconnection queue position the ERW holds on one map. It computes nothing new: each row is one row of an input table, with the fields renamed to one set of columns and, where the source has no coordinates, a county location added.

| kind | Input table | Rows (2026-09-27) | Coordinates |
|---|---|---|---|
| operating | `eia860m_operating_generators` | 28,605 | EIA's plant lat and lon |
| planned | `eia860m_planned_generators` | 2,316 | EIA's plant lat and lon |
| queue | `ercot_`, `caiso_`, `nyiso_`, `miso_`, `spp_`, `isone_interconnection_queue` | 14,567 | none from the ISOs: county internal point |

## Columns

The entities standard columns first (`docs/datastandard.md`), then:

| Column | Meaning |
|---|---|
| `project_id` | the input row's `entity_id` (for example `eia860:10003:GEN1`, `ercot_queue:15INR0064b`) |
| `kind` | operating, planned or queue |
| `technology_group` | see below |
| `mw` | `capacity_mw` as the source states it (EIA: nameplate; queues: the requested MW; a queue may state a negative repowering request) |
| `state`, `county` | as the source states them; the state is reduced to its postal code |
| `geo_precision` | `point` (EIA's coordinates), `county` (the county's internal point), `none` (not placed) |
| `geo_note` | for a county or none row: which county and gazetteer file, or why it was not placed |
| `operator`, `operator_role` | EIA's operator (`operator`), or the queue's interconnection customer (`developer`) |
| `date`, `date_kind` | EIA operating year (`operating_year`), EIA planned operation date (`planned_operation_date`) or the queue date (`queue_date`) |
| `technology`, `source_status` | the source's own technology text and status label |
| `source_table` | the input table |

`status` is the input's standard status (operating, planned, under_construction, active, completed, withdrawn, suspended). `source` is `erw:energy_projects` and `source_url` links this page (Decision 23).

## Coordinates

1. **Point.** Where EIA gives lat and lon, they are used as given. Every EIA-860M row in the 2026-08 vintage has them.
2. **County.** Otherwise the row's county and state are looked up in the U.S. Census Bureau's county gazetteer:
   - the file: 2025 Gazetteer Files, counties, national (`2025_Gaz_counties_national.zip`, https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2025_Gazetteer/), public domain;
   - it is downloaded on each run into `warehouse/raw/census_gazetteer/<run_id>/`, with a `manifest.csv` naming the URL, time and SHA-256;
   - lat and lon are the county's **internal point** (`INTPTLAT`, `INTPTLONG`). The Census Bureau places this point inside the county, at or near its geographic center. The session 16 prompt asked for the centroid; the internal point is the gazetteer's published point, and it is always inside the county, which a centroid is not.
   - **Connecticut:** since 2022 the Census Bureau publishes planning regions instead of Connecticut's eight counties, while the ISO-NE queue still names the counties. For names the 2025 file lacks, the 2020 file (`2020_Gaz_counties_national.zip`) is used; `geo_note` names the file.
   - **Matching:** names are compared without case, accents, punctuation and the words county, parish, borough, census area and municipality; "Saint" and "St." are the same. The whole text is tried first (a county may contain a hyphen, as in Miami-Dade), then each county of a list ("Tioga - Bradford", "Kern/Kings"): the first that matches is used, and `geo_note` says the row listed several.
3. **Place (session 349).** County words that match no county are tried, in the same state, as a place of the Census Bureau's place gazetteer (cities, towns, villages and census-designated places, `2025_Gaz_place_national.zip`), then as a town or township of its county subdivision gazetteer (`2025_Gaz_cousubs_national.zip`), with the same matching less the place's kind ("Austin city", "Hartford town", "Milford CDP"). A name two places of one state share is never used (212 place names and 3,540 subdivision names on 20 October 2026). lat and lon are the place's internal point: `geo_precision` place, and `geo_note` names the place, the file and the words it came from. Its card says "city or town point; not the site itself".
4. **None.** No fuzzy matching: a misspelled name ("Wocester") or a row without a state or a county stays unplaced, with the reason in `geo_note`. On 2026-09-27: 1,172 queue positions (286 without a state, 214 without a county, the rest a name the county gazetteer does not hold). On 2026-10-19's table, 710; of those, the two place files place 355 (333 by a place, 22 by a town or township), measured on 20 October 2026 (session 349; `runs/s349/placement.csv` on the third machine), and 355 stay unplaced: 90 state no county, 76 no state, the rest name nothing either file holds. The map's Projects tab gives the count of the table it reads.

A county point is drawn differently from an exact one on the map, and the click card says which it is.

## Technology groups

- **EIA rows:** EIA's technology text grouped by the EIA-860M connector (`TECH_GROUPS` in `warehouse/connectors/eia860.py`): solar, wind, storage (batteries, flywheels, pumped storage), natural_gas, coal, nuclear, hydro, petroleum, biomass, geothermal, other; `unknown` where EIA gives no technology.
- **Queue rows:** the ISO's fuel or technology text is grouped by `QUEUE_TECH` in the script, into the same groups plus:
  - `hybrid`: the text names more than one of solar, wind, storage or another technology ("Photovoltaic + Storage", "SUN BAT", "Hybrid - Solar/Storage");
  - `transmission`: merchant transmission requests (AC, DC, variable frequency transformer);
  - several fossil fuels only ("DFO NG") take the first one named.
  - An ISO that states no technology gives `unknown`; text that matches no group gives `other`.

## Live set

`energy_projects` repeats rows that are already in Supabase in their source tables. To stay under the live set's size limit (`max_mb` in `warehouse/supabase/live_set.yaml`), Supabase holds it without withdrawn queue positions and with only the columns the map uses (the `select` rule in `live_set.yaml`). The CSV and Redivis hold every row and column.

## Refresh

The table is a snapshot (Decision 21), rebuilt by `warehouse/run_daily.sh` after the EIA-860M and queue connectors. In CI the queue tables are on the runner only on Mondays (and on a manual run with `queues` set to 1); on other days the script skips with a warning and the previous load stays in Supabase.

## The page: /map, one page (session 167)

Since session 167 the project map is one page at `/map`: the layout and data of version 2 (session 105, `/map/v2`, which now redirects to `/map`) with what version 1 offered (sessions 16 and 22) carried over. Both earlier versions are kept, unrouted, in `site/app/_retired/map-v1` and `map-v2`. This section is the page's Method note; the page itself carries one source line.

### What the page reads

The site's own copy of four tables, `site/data/map.json`, written by `warehouse/derived/project_map.py` (`build_page`). The page asks Supabase for nothing; the unit card's fields come from the same file (below). The file is rebuilt with the monthly job (`warehouse/run_monthly.sh`, step `project_map`) and by hand after a write of one of the four tables; a rebuild that changes nothing but the built stamp leaves the file as it was.

| Kind | Rows of | Which |
|---|---|---|
| Operating units | `eia860m_operating_generators` | every row (EIA status OP, SB, OA, OS) |
| Planned units | `eia860m_planned_generators` | every row (EIA status P, L, T, U, V, TS, OT) |
| Queue positions | `energy_projects`, kind `queue` | not withdrawn (as version 1: a withdrawn position is not on the map), and only the queues whose rows may be drawn (below) |
| Datacenters | `datacenter_facilities` | the rows the table places in a US state |

- **Queues held back.** The list of queues whose rows may be drawn is `QUEUE_GRIDS` in `site/lib/resources.ts` (one list, switched by a person; `QUEUE_SHOWN` and `QUEUE_HELD` in `project_map.py` follow it, and a test holds the two equal). MISO: every pull of MISO's servers is paused since 4 October 2026 while a person reviews MISO's terms ([`miso_pause.md`](miso_pause.md)); MISO's queue rows are not written to the file and the page reads "MISO queue positions: paused while terms are reviewed". NYISO: its site's legal notice confers no license, so its queue rows are not shown either (energy_projects held none of them on 9 October 2026). The file counts the rows held back (`counts.queue_rows_held`). EIA's units in MISO's and NYISO's footprints are EIA's and are on the map.
- **Datacenters in no US state.** A facility the tracker places in no US state (a facility abroad, or one the news names no state for) is counted in `counts.datacenters_without_state` and not written: the map is a map of the United States.
- **The rest of the inventory.** These notes stood on version 2's face, as "What the inventory leaves out" and "How to read it":
  - Plants under 1 megawatt are not in EIA's inventory. EIA describes the form as covering "existing and proposed generating units at electric power plants with 1 megawatt or greater of combined nameplate capacity". Rooftop solar and other small generators at homes and businesses are not in it. Units smaller than 1 MW that are in it (`counts.under_1_mw`) are each at a plant that passes the threshold.
  - Retired units: the inventory lists them; this map does not. They are in the table `eia860m_retired_generators`.
  - Projects that have told no one but a grid operator: a planned unit is one its owner has reported to EIA. A request in an interconnection queue is not a planned unit until then, which is why the queue positions far outnumber the planned units. A queue position is a request, not a plant; most are withdrawn before they are built, and a completed position may be a unit the inventory already lists. That is why the page never adds a queue position's MW to a unit's.
  - The grid of a unit is EIA's balancing authority for it. The seven ISOs are named; every other balancing authority, and a blank one (`counts.without_balancing_authority` units), is "Outside the seven ISOs". A queue position's grid is the ISO whose queue it is. A datacenter's grid is "Grid not stated": the tracker names none, and none is guessed from the state.
  - A row is a generating unit, not a plant: a plant with four turbines is four units. MW is the unit's nameplate capacity.
  - Batteries are the storage units whose prime mover is a battery (EIA prime mover BA); pumped storage and the other kinds are "Other storage". A queue's storage request does not say what kind of storage it is: it is "Storage (queue positions)", in the storage color.
  - Energy for planned batteries: the inventory gives a planned battery its power in MW and no energy in MWh.
  - Puerto Rico's units are in the totals and the table; the drawing's projection (Albers, the lower 48 with Alaska and Hawaii) has no place for them. A row with no location in its source is not drawn either. The map's line says how many of the rows chosen are not drawn.
  - The inventory is monthly and published about a month after the month it describes: nothing since its vintage is in it.
- **From version 1's face** (its scope line, "What the map holds" and the line under its table): the datacenters are those of the datacenter power tracker (`datacenter_facilities`, [`datacenter_facilities.md`](datacenter_facilities.md)): the facilities the news names since 2025-01-01, the public site lists of the operators it reads and the queue positions that name a datacenter or a large load; this is not a census of every facility. MW is as each source states it: EIA's nameplate capacity; for a queue position, the MW requested; for a datacenter, the MW a story or the operator states, where one does. A queue position is drawn at its county's internal point from the Census Bureau's gazetteer (above), as a triangle, not at a site. A datacenter is placed at the operator's coordinates or at the stated county or city. Colors are the site's eight fuel colors; petroleum, biomass, geothermal, hybrid, transmission, other and "Not stated" share the color of "Everything else". Hybrid is a queue position naming more than one technology (solar and storage, for example).

### Statuses

As many as the sources give. A proposed unit keeps EIA's own status code (the connector's `eia_status` column, kept beside the folded `status` since session 8: the folded column is not used by the page and stays in the table), in plain words: "Planned, regulatory approvals not started" (P), "Regulatory approvals pending" (L), "Regulatory approvals received, not under construction" (T), "Under construction, half or less complete" (U), "Under construction, more than half complete" (V), "Construction complete, not yet operating" (TS), "Other" (OT). An operating unit is "Operating"; its card names EIA's own label when EIA's code is not OP (standby, or out of service). A queue position shows the table's standard status (active, suspended, completed, or not stated) and its card the ISO's own words. A datacenter shows the tracker's cleaned status, never the raw field of an operator's list. A status of a kind appears in the panel only while that kind is chosen.

### Totals

The sentence and the totals follow every choice. MW is never added across kinds: a unit's nameplate, a queue position's request and a datacenter's stated load are different things, so the sentence gives each kind its own count and MW, and the totals are by status, grouped by kind. A datacenter's MW is summed over the facilities that state one, and the count of those is given. A row whose source states no MW is left out as soon as a size is asked for: it cannot be said to fit one. "By technology" counts the operating units, planned units and queue positions chosen, by technology group and kind; datacenters have no technology and are not in it.

### The marks

A dot is an operating unit; a ring a planned unit (a heavier ring: under construction, EIA's U, V and TS); a triangle a queue position at its county's point; a diamond a datacenter. A mark's color is its technology and its area grows with its MW. The key under the map is plain: it toggles nothing (version 2's legend toggled statuses; the lists of the panel do that now).

### The address

Every list (kind, grid, technology, status, state) is a multi-select with "Select all" and "Clear", and the address keeps the choice: `?kind=operating,planned&grid=ercot,caiso&tech=solar,battery&status=u,v&state=CA,TX&min=100&max=500`. A list is the options' slugs with commas between them, in the page's own order; a parameter that is absent or empty means every one, and `none` means none. A slug the page does not know is passed over, so an address written today reads the same after the file gains a grid, a status or a state. A click on a state on the drawing chooses that state alone when every state is shown, then adds or takes away a state; taking the last one away shows every state again. Reset empties the address.

### The unit card

A click on a unit opens version 1's card: name and entity id, kind, technology group (with the source's own technology text), MW, status, state, county, city, grid, operator or developer, developer, date, power, location, the source table, the stories (datacenters) and the line naming the ERW table it was read from with its vintage. Version 1 read the card from Supabase through `/api/entity`, one request a click. The one page reads it from its own file: `project_map.py` writes the card's fields into `site/data/map.json`, and the page leaves them out of what it loads and asks for them once, at the first click on a unit, from `/map/card` (a route built with the site from the same file, behind the same release gate as the page; it never asks Supabase). Measured on the file of 9 October 2026 (gzip): the page's data without the card is 430 KB, with the entity ids a request per click would need 582 KB, with every field of the card 835 KB (3.3 MB before compression); the whole page as served (local `next start`, gzip) was 994 KB with the card inside and is 646 KB without it (the dates stay on the page: the hover shows them). Read at the first click, the card costs a reader who never clicks nothing, and the card is always of the same vintage as the map (the ids of the datacenter tracker change when its merge rule does, so a card read from Supabase could miss a facility the page's file still holds). If the page's file was rebuilt between the load and the click, the card says so and asks for a reload, rather than show another row's fields.

### The page as it stands (session 330, 20 October 2026)

- **Two tabs** since session 239: the projects (this section) and the resources (the natural resource layers, with
  the units, the queue and the datacenters laid over them; `/resources` redirects there); session 349 added a third, the
  queues (`iso_queue_statistics`, "Queue statistics" below), whose downloads line offers that table.
- **The maps stay drawn by the chart library on a canvas** (session 318: a map is not a chart of the owner's ruling of
  13 October on charts); whether they should leave it is a question for the owner.
- **The numbers** (the units held, the totals by status, the line of what is drawn) are the file's, and `check-map`
  reads them against it.
- **Downloads** (session 330): under both tabs, the four tables the file is built from, each as the live set's CSV with
  a Python and a Stata reader of that CSV, or named with its place on Redivis where the live set does not hold it
  (session 328's shared line). The CSV is the table as the live set holds it today; the map's copy is the file's, built
  on the day its source line says.
- **The copy and its tables, on 20 October 2026:** the file was built on 9 October (EIA-860M of August 2026, the queues
  as `energy_projects` held them on 30 September, the tracker of 9 October); `energy_projects` last ran on 5 October,
  `datacenter_facilities` and the two EIA-860M tables on 20 October. The file follows them at its next rebuild (the
  monthly job, or by hand).

## Queue statistics

Session 348, 20 October 2026. `iso_queue_statistics` (the chain prompt's `queue_statistics`; a series table's name has three parts), built by `warehouse/derived/queue_statistics.py` from the six ISO queue tables (`<iso>_interconnection_queue`), the same rows `energy_projects` takes its queue positions from. For each ISO and each year a position entered the queue: how many positions entered, were withdrawn, reached operation and are still waiting, the MW of each, the withdrawal rate, and the median and mean years from entry to operation of the positions that reached it. The map's Queues tab draws it (session 349).

### What counts, in each ISO's own words

The status is the queue connector's (`STATUS_MAP` of `warehouse/connectors/iso_queues.py`), which maps every word an ISO uses and fails on a new one. This section reads it as follows.

| ISO | Withdrawn | Operating | Still waiting |
|---|---|---|---|
| ERCOT | none held: its GIS report lists active and completed positions only | Completed | Active |
| CAISO | WITHDRAWN | COMPLETED | ACTIVE |
| NYISO | Withdrawn | Completed | Active |
| MISO | Withdrawn | Done, LEGACY: Done | Active, Pending Revision Approval, Pending Transfer |
| SPP | WITHDRAWN, TERMINATED | IA FULLY EXECUTED/COMMERCIAL OPERATION | IA FULLY EXECUTED/ON SCHEDULE, IA PENDING, DISIS STAGE, FACILITY STUDY STAGE, SPECIAL STUDY, ERAS, ICS; and IA FULLY EXECUTED/ON SUSPENSION (suspended) |
| ISO-NE | Withdrawn | Completed | Active |

- **Status not stated.** A position the ISO lists with no status (SPP's affected-system requests, and rows of other ISOs whose status cell is blank) is counted as `positions_status_not_stated`, in none of the three.
- **The entry year** is the year of the ISO's queue date. A position with no queue date is in no year and is counted in the table's header: ERCOT 1, CAISO 0, NYISO 0, MISO 6, SPP 48, ISO-NE 0 (the rebuild of 21 October 2026, below).
- **The withdrawal rate** is withdrawn positions over positions entered, by count. ERCOT has none (above).
- **The wait** is the years from the queue date to the in-service date (days over 365.25), for operating positions with both dates and an in-service date on or after the queue date (`wait_positions` counts them). MISO's and ISO-NE's tables hold no in-service date, so they have no wait. SPP's in-service date is its "Commercial Operation Date", which the table fills for active and withdrawn positions too: for an operating position it may be the date requested rather than achieved, and its rows say so (`x_rule`).
- **MW** is the capacity the queue states, summed (a repowering request may be negative); a position with no MW is in the counts and not in the MW.
- **Nothing is filled.** A variable an ISO does not give has no row for it.
- **Rebuilt whole on 21 October 2026 (session 432).** Session 348's first build read the six queue tables with `comment="#"`, which cut a data row at a "#" inside a cell (a project named "Unit #2") and lost its queue date (session 367 found it; `queue_statistics.py` now skips the header by its count of lines, session 103's rule). The rebuild from the same six tables on the data machine regained **868 positions** with their queue dates: ERCOT 455, CAISO 169, NYISO 104, ISO-NE 94, MISO 30, SPP 16 (positions entered: ERCOT 1,302 to 1,757, CAISO 2,109 to 2,278, NYISO 1,710 to 1,814, ISO-NE 1,657 to 1,751, MISO 3,845 to 3,875, SPP 3,014 to 3,030; ERCOT's MW entered 306,952 to 438,194). The table keeps its 1,511 rows (the same ISOs, years and variables); 474 of their values changed. Positions with no queue date now: ERCOT 1, CAISO 0, NYISO 0, MISO 6, SPP 48, ISO-NE 0.

### The inputs read

The data machine's copies, restored from the ERW archive (`warehouse/archive/restore.py --from-bucket`, session 348): ERCOT, CAISO, SPP and ISO-NE as of the run of 19 October 2026; NYISO and MISO as of 4 October 2026 (their last run). The table's header names each run. 1,511 rows: six ISOs, entry years 1989 to 2026 (CAISO's dated positions end in 2023; MISO's begin in 2015).

### Licenses

The six queues' tables are flagged public, and NYISO's, MISO's and ISO-NE's are "license needed" from 21 October 2026 (`docs/licenses.md`). The table's publishers are the six ISOs (`scripts/licenses.py`, by hand), so it is held by grid: from that day a page shows its ERCOT, CAISO and SPP rows and holds the other three, as it holds their prices.

### The cross-check against LBNL's Queued Up

From the copy held in `warehouse/raw/lbnl_queues/20261002T091624Z/` (Berkeley Lab's queue data file through 2025; no request to LBNL), for CAISO:

| What | This table (CAISO's queue as of October 2026) | LBNL (as of the end of 2025) |
|---|---|---|
| Requests entered 2000 to 2020: operating | 233 | 232 (sheet 25, count by status) |
| the same: withdrawn | 1,379 | 1,492 |
| the same: still waiting | 150 | 185 active and 1 suspended |
| Request to operation, positions online 2018 to 2025: count | 94 | 99 (sheet 38, box plot data) |
| the same: median, months | 92.35 | 91.39 |
| the same: mean, months | 94.46 | 91.88 |

The operating counts and the waits agree within a few positions and about a month. The other counts differ: CAISO's current report holds 148 fewer positions of those years than LBNL counted (113 fewer withdrawn, 36 fewer still waiting, one more operating). LBNL builds its file from many years of each ISO's reports; the ERW holds the current one. The withdrawal rate of those years is close all the same: 78.3 percent here (1,379 of 1,762), 78.1 percent in LBNL's counts (1,492 of 1,910).

### The explorer (session 405, 21 October 2026)

`/explore/interconnection`, in review and not in the menu, the third signature explorer (platform tool 5), on the frame of `/explore/ercot-peak-premium` (session 403). It draws this table as it stands and computes no figure: every number is one row of `iso_queue_statistics` with that row's check key, or the one count the table's header states for the queue (its positions with no queue date), with a `series_hdr|` key that `site/scripts/check-values.mjs` reads from the header.

- **Filters, in the address:** `queue` (one of the six; CAISO by default, as on the map's Queues tab), `measure` (`positions` or `mw`), `from` and `to` (the first and last entry year drawn; by default every year the queue holds, to the newest whose year is over).
- **What it draws:** three headline figures for the last entry year (entered, reached operation, and the withdrawn share, or for ERCOT, which holds no withdrawn positions, still waiting), each with the first year's beside it; the entry years by status as stacked bars (reached operation, withdrawn, still waiting, status not stated: the four this section defines, each a row of the table, never a sum the page makes); the withdrawn share and the median wait by entry year where the queue holds them; the table of every entry year; and the six queues side by side in the last entry year.
- **A year not over:** an entry year at or after the year the queue was retrieved (the header's "Inputs read" line) is marked partial and hatched.
- **The fault of the first build:** while the table's header says it was built before the fix (session 367's commit of 20 October 2026, 19:45 UTC), the page says in one line that its counts are that build's and not the queues', and shows them as the table holds them, never a corrected figure. The line goes when the data machine's rebuild writes a later "Retrieved" time; a header the page cannot read is said so.
- **Licenses:** NYISO's, MISO's and ISO-NE's queues are held from 21 October 2026 (Licenses, above): the page does not read their rows and shows the catalogue's words, "license needed", in their place, as the map's Queues tab does.
- **Freshness:** the catalogue's line for this table and for the chosen queue's table (the shared frame), and the header's build time and the queue's retrieval date under it. On 21 October the live catalogue did not list `iso_queue_statistics`, and the line says so.
- **The figures in MW and their keys:** with the measure MW (`measure=mw`), `iso_queue_statistics`, `mw_operating`, `mw_withdrawn`, `mw_waiting` and `mw_status_not_stated` are the MW, as the queue states them, of the entry year's positions that reached operation, were withdrawn, are still waiting and have no status stated: the parts of the stacked bars, the columns of the table of every entry year and of the six queues side by side, and the headline "Reached operation" (and, for ERCOT, "Still waiting"). Each is one row of the table; a position with no MW is counted in the positions and not in the MW (finished on the combined branch of chain 015, 21 October 2026).


### Decisions of the explorer (each dated, and reversible unless said)

The choices made on `/explore/interconnection`, one line each with its session; session 405's are gathered here from "The explorer" above.

1. 2026-10-21, session 405: four filters in the address, `queue`, `measure`, `from` and `to`; CAISO in positions by default, every entry year to the newest whose year is over; a value the table does not hold falls back to the default and the page says so.
2. 2026-10-21, 405: the stacked bars are the four statuses this section defines, each a row of the table, never a sum the page makes; an entry year at or after the queue's retrieval year is partial and hatched.
3. 2026-10-21, 405: while the header says the table is the first build's, the page says so in one line and shows the counts as the table holds them, never a corrected figure.
4. 2026-10-21, 405: a queue whose publisher asks for permission (NYISO, MISO, ISO-NE from 21 October 2026) is not read and shows "license needed" in its place, on the page and in the six-queue table.
5. 2026-10-23, session 2202: every figure carries its source in its hover (the table, the queue and its entry year, the variable, the year, the ISO's own queue table and this note), read from the figure's key by `site/lib/explore/source.ts`; the header's count names the header line it is read from; the three headline numbers carry the same words in the brand's tip; a held queue's figures carry no source words, the hold being drawn first.
6. 2026-10-23, 2202: the tool pages' stacked and line chart (`site/components/tool/SeriesChart.tsx`) draws the brand's hover card for the entry year under the pointer or the keyboard's arrows, with the total under a rule where more than one series stacks; its `<title>` a category stays. Every tool page that draws the chart gains the card.
7. 2026-10-23, session 2204: on reading, nothing of the page's type, color, tables or charts stood outside `docs/brand.md`; no change.

## The figures on the page and their keys

Each number `/map` shows carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs` checks against the live set and `site/scripts/check-methods.mjs` against this note (session 409). The keys the sections above do not name:

- `projects|count|queue|none`: under the map, the queue positions the ERW holds (withdrawn ones among them) that are not on the map, because their county words name no county, city or town of their state, or they state no county or no state.
- `iso_queue_statistics`, `positions_operating`, `positions_withdrawn`, `positions_waiting`: on the Queues tab, in the table "Every entry year", the positions of the entry year that reached operation, were withdrawn and are still waiting (the columns Operating, Withdrawn and Still waiting).
- `iso_queue_statistics`, `wait_years_median`: the column "Median wait, years", the median years from entry to operation of the year's positions that reached it.
- `iso_queue_statistics`, `mw_entered`: the column "MW entered", the MW of the positions that entered the queue that year.

## The figures on the grid page and their keys

Each number `/grid` shows carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs` checks against the live set and `site/scripts/check-methods.mjs` against this note (session 409). The keys the sections above do not name:

- `gridq|<queue table>|active|<kind>|n`, `gridq|<queue table>|active|<kind>|mw`, `gridq|<queue table>|completed|<kind>|n`: a grid's block "What is being built" (`components/grid/YourGrid.tsx`), the table of the grid's interconnection queue (`caiso_interconnection_queue` for CAISO), one row a kind of project as `energy_projects` groups the ISO's own fuel names: the positions waiting (active), their MW, and the positions completed. Withdrawn positions are left out.
