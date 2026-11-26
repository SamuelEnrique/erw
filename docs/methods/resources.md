# Where the resources are: the natural resource layers

Session 146 (7 October 2026). The page `/resources` draws the natural resource itself, not what is built on it.
Every layer is a publisher's own file, reduced to a size a browser can draw. The file as downloaded keeps the
full resolution in the warehouse's raw store (`warehouse/raw/resources/`, with `downloads.csv`: the address,
the bytes, the hash and the retrieval time of every file and of every terms page). The connector is
`warehouse/connectors/resource_layers.py`; the layers it writes are in `site/data/resources/layers/` and are
described, one entry a layer, in `site/data/resources/manifest.json`.

## What holds for every layer

- **Nothing is filled, smoothed or interpolated.** Where the source has no value the layer has none, and the
  page says "no value in the source here".
- **Units are the source's own**, as the source writes them. Nothing is converted.
- **The vintage is what the source states** (the years averaged, the assessment's date, the file's date). Where
  the source states none, the layer says so and gives the file's own date.
- **A grid layer** is a regular grid of longitude and latitude (WGS84) at 0.2, 0.1, 0.05 and 0.025 degrees, and
  never finer than the source: a level whose cell would be smaller than the source's own cell is not built. A
  cell's value is the mean of the source's own valid cells whose centres fall inside it. A cell in which fewer
  than half of the source's cells hold a value is empty. For each level the connector prints the level's mean,
  weighted by the number of source cells in each cell, beside the source's mean over the same cells: the two
  agree to the last stored digit, and the build stops if they do not.
- **A shapes layer** is the source's polygons in WGS84 with each polygon simplified to a stated tolerance
  (topology kept, one feature at a time) and its coordinates written to 3 decimals (about 100 m). No feature
  is dropped; each keeps the source's own fields.
- **A points layer** holds the source's rows, each at the source's own longitude and latitude. None is placed
  by hand.
- **The ceiling.** All downloads together stay under 4 GB. The connector asks the size of a file before it
  reads it and refuses a download that would pass the ceiling.
- **A resource layer is not a siting study.** It says nothing of land that may be used, of the grid, of permits
  or of cost.
- **The laboratory's notice travels with its data.** The National Laboratory of the Rockies (until 2025 the
  National Renewable Energy Laboratory, NREL) grants the use of its data on the condition that its notice
  appears in every copy. Each web file made from its data (wind speed, the two solar layers, deep enhanced
  geothermal, biomass) carries the notice of the laboratory's site in a `notice` field, and the notice is
  printed in full at the end of this document. The archives themselves carry the laboratory's older notice,
  under NREL's name, as `data-disclaimer-opt.pdf` or in the shapefile's metadata; it is kept in the raw store
  and quoted below where the shapefile's metadata holds it.
- **The laboratory's old pages no longer exist.** The wind, solar, geothermal and biomass files were listed
  on NREL's resource map pages. Since the laboratory's site moved to nlr.gov those pages return "not found",
  and no page of the new site links the files, which still answer at `www.nlr.gov/docs/libraries/gis/`. The
  U.S. government's data catalogue (catalog.data.gov) still lists the wind and solar files under their old
  addresses.

## Session 159 (8 October 2026): hydropower, the gross capacity factor, the queue grid by grid

- **Hydropower is held, in the form its publisher publishes it.** The publisher is Oak Ridge National
  Laboratory, on HydroSource, for the U.S. Department of Energy (not USGS). Two assessments, two layers, each
  with its own section below:
  - non-powered dams: one point a dam, with the file's own nominal capacity (MW), annual average generation
    (MWh) and capacity factor;
  - new stream-reach development: the file's own total for each HUC10 watershed (MW), drawn on the watershed's
    own outline from the publisher's shapefile. The file does not say where in a watershed the stream-reaches
    lie, so nothing is drawn at a site.
  Nothing is estimated again, converted, spread over an area or filled in. A watershed for which the file gives
  no capacity (its code -9999) is not drawn.
- **How the files were fetched (the owner's ruling of 8 October 2026).** HydroSource's dataset pages print each
  file's own address; their download buttons open a form that asks for a name, an e-mail address, a company
  and an occupation. The files were fetched by their own addresses with a plain request whose only identifying
  header is the User-Agent `ERW research project, github.com/SamuelEnrique/erw`. The form was not filled and no
  name, address or other personal detail was sent. HydroSource's data use policy, quoted in full in each
  layer's section, says the data is "openly shared, without restriction".
- **The files hold persons' e-mail addresses** (the dams file's readme under "Dataset contacts"; the
  watershed workbook's metadata sheet and the shapefile's metadata under contact and creator). None is copied
  into a web file, the manifest or this document. The dams file's `dam_owner` column is left out of the web
  file: some owners are private persons.
- **No gross capacity factor layer.** No gross capacity factor was found among the files the laboratory (NLR,
  until 2025 NREL) offers without a key; its developer service needs a key issued to a named person. The
  owner's ruling of 8 October 2026: a layer that needs a personal key is not fetched. No key was asked for.
  The toggle is greyed, "not held", with that sentence on hover. The layer that is held, "Wind capacity factor
  (supply curve sites)", is the supply curve's own column and is not called gross.
- **The interconnection queue, grid by grid.** The overlay reads the queue rows of `energy_projects` in the
  live set. Read on 8 October 2026 it held 3,717: ERCOT 1,758, SPP 1,023, CAISO 514, ISO-NE 422, and none of
  MISO or NYISO. Why, from `warehouse/metadata/run_status.csv`:
  - **MISO: paused while terms are reviewed.** Every pull of MISO's servers is paused since 4 October 2026
    (`docs/methods/miso_pause.md`): MISO's terms say "You agree not use any automated means, including, without
    limitation, agents, robots, scripts, or spiders, to access, monitor, or copy any part of this Website or the
    App." The scheduled run of 5 October therefore skipped MISO's queue, and `energy_projects`, which is built
    from the queues the run holds, was written and loaded without it. Rows pulled before the pause (3,881 in the
    warehouse's `miso_interconnection_queue` of 30 September) are not put on this map while the review lasts: the
    overlay leaves out any MISO row the live set may hold and says "paused while terms are reviewed".
  - **NYISO: its terms do not allow it.** Since 27 September every scheduled request for NYISO's queue workbook
    has been answered "202" with no file (four attempts a run), so no run has held NYISO's queue and
    `energy_projects` has been written without it; the warehouse's own copy is of 26 September (1,814 rows).
    That is why the rows are absent. Whether they may be shown is a separate question, settled by NYISO's own
    words: the workbook is on www.nyiso.com, and that site's legal notice (read 7 October 2026 by session 149,
    which ruled NYISO's load queue internal on it) says "Access to this Web site does not confer any license or
    ownership interest in either the form or content of the Web site, including any confidential or proprietary
    information or intellectual property of any kind or nature, and the NYISO hereby expressly reserves such
    rights and property in its entirety." and closes "Copyright © 2026 New York Independent System Operator. All
    Rights Reserved." No sentence of the notice grants leave to copy, redistribute or display, and no other terms
    of NYISO's that grant reuse of the queue were found. So the rows are not shown and nothing is loaded: the
    overlay leaves out any NYISO row the live set may hold and says "NYISO's terms do not allow it". A person
    can rule otherwise (`QUEUE_GRIDS` in `site/lib/resources.ts` is the one list).
  - The count of rows drawn and not drawn, in all and for each grid, is computed from the live set each time
    the overlay is read; none of it is written into the page.

## Session 8603 (19 November 2026): the switches' lines, the kinds named, a replication, a cross-check, the decisions

Chain 504 set the map beside the owner's list of 7 October 2026 as that chain gives it: one simple map of every kind of energy resource as switches (sun, wind, geothermal heat, hydropower potential, oil and gas, coal, uranium, critical minerals), the resource itself and not what is built on it; a switch a layer; several on at once; a hover with the place, the value, its unit and its source; a short line under each switch. The map had most of it since sessions 146 and 159 (read in a browser at 1280 and 390 px on 19 November: three layers on at once, the hover with latitude and longitude, the value, the unit, the vintage and the publisher). It was not built again. What this session added:

- **A line under each switch** that says what the layer measures in plain words (`MEASURE` in `site/lib/resources.ts`), written from each layer's "What it is" below, not from the publisher's field names. A layer the table does not know says its own line when its entry of the list of layers carries one (`measure`), else the source's label of its value.
- **Coal, uranium and critical minerals are named.** Each has a group and a switch. No layer of the three is among the files, so each switch is greyed and says so on hover; nothing is drawn in its place. The day a layer of one of them is in the list of layers (its group written "coal", "uranium" or "critical minerals"), its switch is the layer's and the greyed one is gone, with no change of code. The data machine's chain of the same day names the layers it will write (coal fields, uranium, critical mineral deposits). (Session 10238: the coal fields arrived later that day, in the list of layers added beside the first, built 19 November 2026 16:51 UTC; since then coal is a layer, and only uranium and critical minerals are greyed.)
- **The map stays a tab of the project map** (`/map?tab=resources`; `/resources` opens it), as the owner's menu of 12 October 2026 has it. It is in review, as every page is.

### Replication: tight oil and shale gas plays (`oil_gas_plays`)

`replication/resources/replicate.py` reads the publisher's file as the publisher serves it and recomputes every figure the map holds for the layer. It is written from this note and the publisher's file, with Python's standard library alone (it reads the shapefile's table and its outlines itself).

- **The file:** <https://www.eia.gov/maps/map_data/TightOil_ShaleGas_Plays_Lower48_EIA.zip>, 323,424 bytes. Its sha256 on 19 November 2026 is the one the layer recorded on 7 October (`c09b3bd2982754cf...`): it is the same file. EIA's robots file allows every path; its terms are "Public domain and use of EIA content".
- **Result: 556 of 556 figures are the publisher's.** The count of plays (50); for each play its name, its area in square miles (the hover's figure, the source's `Area_sq_mi`) and the nine fields of the source the layer keeps; the smallest, mean and largest area (184.8, 10,280.3 and 59,054.2 square miles). `replication/resources/oil_gas_plays_figures.csv` holds every figure, the map's and the publisher's.
- **Stata:** `replication/resources/replicate.do` prints the five headline figures from the same table. It has not been run (Stata is not on the machine that wrote it).

### Replication: sedimentary basins (`oil_gas_basins`), the second layer (session 8619)

`replication/resources/replicate_basins.py` does the same for the basins, from this note and the publisher's file, with the same two readers and the same area on the ellipsoid.

- **The file:** <https://www.eia.gov/maps/map_data/SedimentaryBasins_US_EIA.zip>, 440,871 bytes. Its sha256 on 19 November 2026 is the one the layer recorded on 7 October (`02a017ccb84bdcc1...`): it is the same file. The same robots file and terms as the plays' file.
- **Result: 199 of 199 figures are the publisher's.** The count of basins (32); for each its name as shown, its area in square miles (the hover's figure, the source's `Area_sq_mi`), the unit, and the three fields of the source the layer keeps; the smallest, mean and largest area (1,289.0, 35,362.7 and 160,408.4 square miles). `replication/resources/oil_gas_basins_figures.csv`.
- **Its cross-checks.** The 32 areas sum to 1,131,605 square miles by the publisher's field and 1,131,631 by its outlines, 0.002 percent apart; every basin agrees within 0.2 percent (the widest: Valley and Ridge, 18,886.4 against 18,920.5). The publisher's square kilometres are its square miles times 2.589988 in every basin. `replication/resources/crosscheck_basins.csv`.
- **One rule is the layer's own:** a basin's name. EIA writes names in capitals; the layer shows each word with a capital first. The rule is reproduced as it is, with the one name it serves badly: EIA's "TX-LA-MS SALT", three states' codes, reads "Tx-La-Ms Salt" on the map (data request 554).
- Held by `tests/test_session8619_resources.py`, which builds a small file of the same kind and tries the comparison on it (an altered area and an altered name are each caught), since the publisher's file is not kept in the repository.

### Replication: hydropower at non-powered dams (`hydropower_npd`), the third layer (session 8621)

`replication/resources/replicate_dams.py` compares the layer with Oak Ridge National Laboratory's own table, row for row. The layer keeps every row of it.

- **The file:** <https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/hydropower-capacity-us-npd/TechPotentialNPDs.csv>, 1,594,027 bytes. Its sha256 on 19 November 2026 is the one the layer recorded on 7 October (`84635b4faecc332c...`): it is the same file. HydroSource's robots file allows the read and asks ten seconds between requests (two requests to that site, its robots file and its policy page, were made a second apart before the delay had been read; the file itself is on a storage host with no robots file, and was asked for once). Its terms: "Data hosted on HydroSource is openly shared, without restriction".
- **Result: 34,014 of 34,014 figures are the publisher's.** The count of dams (2,616); for each its place (the source's longitude and latitude to four decimals), its name, its capacity in MW (the hover's figure, the source's `cap_mw`) and the nine columns kept beside it; the smallest, mean and largest capacity. Only figures that differ are kept, in `replication/resources/hydropower_npd_figures_differ.csv`, which holds none.
- **Cross-check 1, against the laboratory's own words.** The 2,616 capacities sum to 3,939.3 MW; the file's readme says "A total of nearly 4 GW capacity is estimated across all 2,616 NPDs included in the dataset".
- **Cross-check 2, the annual generation the hover lists.** The publisher's file also holds twelve monthly figures for each dam, which the web file leaves out. They do not sum to the annual figure: 15,311,641 MWh against 15,244,927 MWh in all, 0.44 percent apart, and dam by dam within 1 percent for 560 and within 5 percent for 2,012 of 2,615. The readme calls each an average over 1980 to 2015 of its own ("averaged for each month of the year", and "average annual generation"), so they are two summaries of one daily series and are not built to sum. The hover shows the publisher's annual figure under the publisher's words, and no month. `replication/resources/crosscheck_dams.csv`.
- Held by `tests/test_session8621_resources.py`, on rows made up for the test (an altered capacity, a moved place, a changed name and a blank written as zero are each caught).

### Replication: the wind supply curve's sites (`wind_capacity_factor`), the fourth layer (session 8622)

`replication/resources/replicate_wind_sites.py` compares the layer with the laboratory's own table, row for row. The layer keeps every row and seven of its columns.

- **The file:** <https://data.openei.org/files/8314/lbw_open_access_2035_moderate_115hh_170rd_supply_curve.csv>, 12,829,421 bytes. Its sha256 on 19 November 2026 is the one the layer recorded on 7 October (`ef13116bd66f3115...`): it is the same file. The host has no robots file; the dataset's terms: "Content is available under Creative Commons Attribution 4.0 unless otherwise noted".
- **Result: 395,703 of 395,703 figures are the publisher's**, each to the rounding the web file keeps. The count of sites (56,528); for each its place, its number, its capacity factor (the hover's figure, the source's `capacity_factor_ac`) and the three columns listed under it; the smallest, mean and largest capacity factor from the source's own digits. Only figures that differ are kept, in `replication/resources/wind_capacity_factor_figures_differ.csv`, which holds none.
- **The web file's rounding, found here:** the place to three decimals and the capacity factor to four, as the layer's entry says; and the wind speed to two decimals and the developable area to one, which the entry does not say (data request 555).
- **Cross-check.** The sites lie from 25.40 to 49.33 degrees north and from 124.66 to 67.07 degrees west; the dataset's own page states its coverage as 24.91 to 49.49 north and 125.45 to 66.53 west, and the sites of all 49 states of the file lie inside it. The page states no total of sites, capacity or area, so none is set beside the file's (13,662,438 MW on 5,680,243 square kilometres of developable land, summed from its rows). A first cross-check tried, capacity over developable area against the file's capacity density, was dropped: that column is over another area, and the two are not meant to agree. `replication/resources/crosscheck_wind_sites.csv`.
- Held by `tests/test_session8622_resources.py`, on rows made up for the test.

### Replication: offshore wind lease areas (`offshore_wind_leases`), the fifth layer (session 8623)

`replication/resources/replicate_leases.py` compares the layer with the outlines table of BOEM's own archive.

- **The file:** <https://www.boem.gov/renewable-energy/boem-renewable-energy-shapefiles>, a zip of 1,031,812 bytes. Its sha256 on 19 November 2026 is the one the layer recorded on 7 October (`47c5f33f5d16cede...`): it is the same file. BOEM is an agency of the United States government; its robots file allows the path.
- **Result: 1,129 of 1,129 figures are the publisher's.** The count of outlines (51); for each its name, its kind (lease area, with the source's `LEASE_TYPE`), its area in acres (the hover's figure, the source's `ACRES`; none where that is 0) and the 18 fields kept; the smallest, mean and largest area. `replication/resources/offshore_wind_leases_figures.csv`.
- **Cross-check 1: BOEM's acres against the area of its own outline.** For the 46 outlines with an area, the stated acres sum to 3,455,708 and the outlines' own areas to 3,458,946, 0.09 percent apart; 45 agree within 1 percent. The one that does not is the easement of lease OCS-A 0517 (South Fork Wind): 2,723 acres stated against 4,086 for the shape the map draws. The hover shows the stated figure.
- **Cross-check 2: a lease's type in BOEM's two tables.** The archive also holds a table of lease blocks. For 48 of the 50 outlines found in it, the outline's type is one that table gives the lease. For two it is not, and the map shows the outlines table's word: OCS-A 0497 (Virginia Department of Energy) reads "lease area (Commercial)" and is "Research" and "Easement" in the blocks table; OCS-A 0506 (The Narragansett Electric Company, a cable) reads "lease area (Commercial)" and is "Right-of-Way Grant" there. Data request 556 puts the two before the data machine. `replication/resources/crosscheck_leases.csv`.
- Held by `tests/test_session8623_resources.py`, on outlines made up for the test.

Why this layer and not the geothermal one, which is smaller: the geothermal files are on ScienceBase, whose robots file names Claude's agents and disallows every path for them, so that host was not read by the session that wrote this (19 November 2026). The layer itself was fetched on 7 October by the data machine's connector under the terms recorded below.

### Cross-check 1: the publisher's area against the area of its own outline

For each play the script computes the area of the publisher's outline on the WGS 84 ellipsoid (the file's own coordinate system) and sets it beside the publisher's `Area_sq_mi`. The 50 areas sum to 514,017 square miles by the publisher's field and 514,014 by its outlines, 0.001 percent apart; every play agrees within 0.04 percent (the largest gap: Floyd-Neal, 5,191.3 against 5,189.3). So the figure the hover shows is the area of the shape the map draws. `replication/resources/crosscheck.csv`.

### Cross-check 2: against areas the same publisher printed earlier

EIA's "Review of Emerging Resources: U.S. Shale Gas and Shale Oil Plays" (July 2011) states an area for several plays. Set beside the layer (`replication/resources/crosscheck_published.csv`, with the review's words and the page of its file):

| Play | The map, square miles | The 2011 review, square miles | Difference | Why |
|---|---:|---:|---:|---|
| Marcellus | 58,326.4 | 95,000 | -36,673.6 | the review: the whole formation as the USGS estimated it; the file: the general area of the play |
| New Albany | 12,564.7 | 43,500 | -30,935.3 | the review: the play's total area, 1,600 of it active |
| Antrim | 43,796.0 | 12,000 | +31,796.0 | the review: the developed and undeveloped area as it counts them; the file's outline is 41 percent of the Michigan basin |
| Haynesville-Bossier | 11,166.7 | 9,000 | +2,166.7 | the file outlines the Haynesville and the Bossier together |
| Fayetteville | 5,852.7 | 9,000 | -3,147.3 | the review counts the central and the western Fayetteville |
| Woodford-Caney (Arkoma) | 2,892.5 | 2,900 | -7.5 | the two agree |
| Woodford (Ardmore) | 1,200.3 | 1,800 | -599.7 | the review: a consultant's estimate of the total area |
| Barnett | 26,311.4 | 6,458 | +19,853.4 | the review: two sections as the USGS estimated them; the file's outline is 75 percent of the Fort Worth basin |
| Bakken | 25,929.2 | 6,522 | +19,407.2 | the review: the acreage companies had leased in 2011 |

No figure is adjusted to match. The two documents answer different questions under the same names: the 2011 review counts an assessed, leased or active area for its resource estimates, and the 2021 file draws "general areas for shale plays". What follows for a reader is said on the page: a play's area is the area of the outline drawn, not the formation's extent and not a measure of oil or gas (the decision "outline-area").

### Decisions (session 8603)

The page's fold "Decisions on this page" under the map (`site/app/resources/Decisions.tsx`) carries ten choices (nine of session 8603 and one of session 8607), each with its default and its source on hover; `tests/test_session8603.py` holds this list and the page's to one list.

| Key | The choice | Default |
|---|---|---|
| `one-file` | Each switch is one publisher's file, drawn as published; layers are never added or blended | One layer, one file, one publisher |
| `the-resource` | The layers are the resource itself; what is built or planned is a separate set of switches | The resource first; the overlays off until switched on |
| `kinds-named` | Every kind the list names has a switch; a kind with no layer is greyed and says why | A greyed switch with its reason on hover |
| `plain-line` | The line under a switch is the page's own plain words; the publisher's description is in this note | One short sentence a layer |
| `opens-on-wind` | The map opens with the wind speed at 100 meters on | Wind speed at 100 m |
| `grid-level` | A grid layer is drawn at the finest of its cell sizes whose cell is at least three quarters of a screen pixel | Three quarters of a pixel |
| `outline-area` | A play's or a basin's area is the publisher's figure for its outline, not the formation's extent | The file's own area |
| `simplified` | A shape's outline is simplified for the web and no feature is dropped | As each layer's `reduction` says |
| `one-tab` | The resource map is a tab of the project map, and `/resources` opens it | A tab of `/map` |
| `two-lists` | The layers come in two lists, the first and one of layers added beside it; they are read as one (session 8607) | The first list wins a name |

## Session 8607 (19 November 2026): a second list of layers, read beside the first

Data request 542 asked the data machine for the coal fields, uranium and critical minerals in the map's form. Its answer is a second list, `site/data/resources/manifest_added.json`, in the first list's form (`built_at_utc`, `layers`, `missing`), because chain 501's rule is that an existing page file is not changed. It holds one layer, the coal fields (602 polygons of the U.S. Geological Survey's Open-File Report 2012-1205, `layers/coal_fields.json`), and names uranium deposits and critical mineral deposits as missing, each with why (the two USGS hosts that serve them refuse automated reading).

What the page does with it (`mergeManifests` in `site/lib/resources.ts`, read on the server in `site/lib/resourcesdata.ts`):

- The two lists are one: the first's layers in their order, then each added layer whose id the first does not hold. Where both name a layer, the first list's entry is drawn.
- The missing lists are joined: an entry already named in the first, or one that is now a layer, is not repeated. A missing entry's own reason is the one its greyed switch shows.
- With no second list on the server the page is as it was. A second list that is there and cannot be read is said under the switches ("layers not read", with why on hover), and the first list's layers are drawn.
- An added layer's file is checked and served like any other: a layer whose file is not on the server joins the missing list with that reason; its address is under `/resources/layer`, behind the release gate.
- A layer may ask the hover to list fields of its source. The first list writes each as a pair, the field and the words for it; the added list writes the field alone, and then the words are the field's own name in sentence case (`PROVINCE` reads "Province"). No value is computed: a field is printed as the file holds it.
- The line under the coal fields' switch is the entry's own `measure`. The foot of the method note says when each list was built.

Seen on a build with the data machine's two files copied in from its branch (`wip/c501-desk-b`; they are not on main and are not committed by this session): the switch "Coal fields" is live in its own group with its line; uranium and critical minerals are greyed, each with the data machine's reason on hover; switched on, the fields draw in the coal color over any other layer, and a hover reads, for example, "Blackfeet-Valier Region (Northern Great Plains) (coal field): 7,729.5 square kilometres. Province: Northern Great Plains; Name: Blackfeet-Valier Region; Age: Cretaceous; Rank: Medium and High Volatile Bituminous. Vintage: 2013. U.S. Geological Survey (USGS)". At 390 px nothing is wider than the screen. Pictures: `docs/reviews/resources-2026-11-19/resources-coal-1280.png`, `-390.png` and the two of the switches.

The area in that hover is the data machine's, computed on a sphere from the source's polygon; it is the outline's area and not a measure of coal in place, as the layer's own note says. Held by `tests/test_session8607.py`.

## Session 8608 (19 November 2026): the reader's read, and the state in the hover

Five cases a reader would bring were taken on a build that holds the coal layer (`docs/reviews/resources-read-2026-11-19.md`: a transmission planner on the wind of the Plains, a power trader on the Permian's basin and plays, a student on Appalachia's coal, an AI lab's siting analyst at Phoenix, a battery developer on central Nevada's sun). Four were answered on the page and one half answered (the datacenters are held for a license). The read's one site gap is fixed:

- **The hover names the state under the pointer.** It gave a latitude and a longitude and no place. After the coordinates it now says the state ("33.45 N, 112.07 W, in Arizona"), found among the states' outlines the map already draws (the Census Bureau's cartographic boundaries as `us-atlas` holds them; `stateAt` in `site/lib/resources.ts`). A point at sea, or in no state's outline, names none: the nearest state is never given. No layer's value is touched by it.

Left as they are, each a row of the read: the coal fields' area is in square kilometres where the basins' and plays' are in square miles, and the coal fields' "What it is not" begins with a file's name (both the data machine's, data request 552); a wind or sun layer's hover repeats its vintage sentence with every value (for the owner's ruling). Held by `tests/test_session8608.py`.

## Session 8611 (19 November 2026): the map against the brand

Measured in a browser on a build at 390 and 1280 px against `docs/brand.md`. Two things did not follow it and now do: on a phone the map's nine controls (zoom in and out, the four moves, the three places) are 44 px in both directions, where they were 24 px tall at every width (section 3); and the hover card is fog with a rule-colored edge and no shadow, where it was white with a shadow (sections 3 and 6). Left as it is: the small "i" beside each decision, 16 px, which is the site's shared button on every page with a decisions fold. No figure is touched. Held by `tests/test_session8611_resources.py`.

## Session 8613 (19 November 2026): the coal fields from main, and the check that reads them

The data machine's coal layer and its list reached main on 19 November (the landing desk's stack d), and the branch was merged with main: the layer on the page is now the file main holds, the same bytes the trial of session 8607 used. Seen in a browser on a build at 1280 and 390 px: the Coal group holds "Coal fields" as a switch, 602 fields drawn, the legend in square kilometres, a field's name, area, vintage and publisher on hover; Uranium and Critical minerals stay "not held" with their reasons; the foot names both lists with their dates; no sideways scroll at 390 px.

One gap in the check itself, fixed: `site/scripts/check-resources.mjs` read the first list alone, so an added layer was never switched on by it. It now joins the two lists by the page's rule, written out on its own (the first list wins a name), and checks the coal fields as it checks the other fourteen: 99 checks where there were 97. Three fail, on main too, and all three are the datacenter overlay, which is held for a license and is not read. Held by `tests/test_session8613_resources.py`.

## Session 8614 (19 November 2026): the map's record of what it has drawn

The check failed two layers on some runs and not on others ("0 cells in view", or the coarser level, with the layer on the canvas and the right value under the pointer). The cause was in the page. The map writes a record of what it has drawn when the view comes to rest, by a timer of 160 ms, and the frame the record describes is drawn by the browser's own clock for frames. Where the frame came later than the timer (a busy machine, a tab in the background), the record was written first and stayed wrong until the map next moved. The record is read by the check and by no reader, so no figure and no picture was wrong; the rest now draws a frame that is asked for and not yet drawn before it writes the record, the same frame and no other. The check holds every frame back 400 ms and reads the record: it failed on the build before the change and passes on the build after, and three runs in a row end at 97 of 100, the three the license hold's. Held by `tests/test_session8614_resources.py`.

**A finger on a phone (the same session, the second read).** Until this session a tap on the map showed nothing on a phone. A touch pointer cannot hover, so the browser sends the map a "leave" with the finger's lift, and the leave took off the card the tap had just put up: measured on a build, the card was on the page for 11 ms. It had been so since the page was built; every read at 390 px had pointed with a mouse. A touch's leave is now let pass. The card of a tap stays until the next tap, a drag of the map or a press of one of its buttons, so a long card is read to its end by scrolling the page. On a map narrower than 480 px the card takes the map's width, under or over the finger, where it was a column some 160 px wide beside it. A wide screen is as it was. The check now taps with a finger at 390 px and drags: 102 checks. Rows 11 and 12 of the read; held by the same test file.

## Session 8615 (19 November 2026): the map read by the keyboard

The brand asks that whatever a hover card says be reachable by keyboard. On this map the arrow keys moved the map, plus and minus zoomed it, and no value could be read. When the map takes the keyboard's focus, the card now reads the place at the map's centre, marked by a small ring, and reads it again after each move or zoom; the card is announced to a screen reader as it changes, and only then (under a pointer it is silent, as it was). A pointer takes the reading back, and leaving the map ends it. The map's label says what the keys do. No figure and no picture of a layer is touched; the keys are the ones they were. The check uses the Tab key and an arrow: 105 checks. Row 15 of the read; held by `tests/test_session8615_resources.py`. What the brand also asks, a table under the chart, is not given for a map of up to 150,000 cells: the layers' entries under the map say what each file holds.

The same session probed the page's main part in a browser for what a screen reader needs (`runs/c504_a11y_probe.mjs`): every control a keyboard reaches has a name, every field a label, no id is used twice, no heading skips a level. One thing is wrong and is left for a ruling: this document, shown in the fold under the map, brings its own title as a second heading of level 1. A fix written that session set the levels from the page, round the site's renderer; the site's rule is that markup reaches a page only through the renderer (tests 177 and 5153), so session 8616 took the fix out. The level of a shown document's headings belongs in the renderer itself, which every page shares. Row 17 of the read.

## Session 8618 (19 November 2026): the hover's words for two point layers

Two point layers, the wind supply curve's sites and the identified hot-water systems, named no fields for the hover in the list of layers, so a hover showed their files' column names as written ("resource: 8.35; capacity ac mw: 282"; "Temp C Li: 85"). The data machine answered data request 553 with a file of its own, `site/data/resources/hover_fields_added.json`: for each of the two layers, the columns to list and the words for each, which are the publisher's own description of the column with its unit (the laboratory's column lookup for the wind sites; USGS's metadata for the hot-water systems). The page reads that file where a layer's own entry names no fields; a layer that names its own keeps them, and nothing else of a layer is touched (`withHoverFields` in `site/lib/resources.ts`). On a day the file is not there the hover is as it was. The file also says what the wind sites' name is, the source's `sc_point_gid`; the page shows the number as before and does not yet say that word, which is no plain noun (for the owner's ruling). Row 10 of the read; held by `tests/test_session8618_resources.py`. The words were tried on the real lists with the data machine's real file, which reaches main with its next landing; they have not yet been seen in a browser.

## Sign-off

Session 8609 (chain 504) added this block; the note had none. A session never signs it. Signing it accepts, as the map's rules:
- each switch is one publisher's file, drawn as published; nothing is computed across layers, and two layers that are on are never added or blended;
- the layers are the resource itself; what is built or planned is a separate set of switches;
- every kind the owner's list names has a switch, and a kind with no layer is greyed and says why (uranium and critical minerals today);
- a play's, a basin's or a coal field's area is the area of the outline drawn, not the formation's extent and not a measure of what is in the ground;
- the layers come in two lists read as one, the first winning a name;
- the hover gives the place (coordinates and the state), the value, its unit, the vintage and the publisher.

It leaves open the rulings the signature pack lists (`docs/reviews/resources-signature-pack-2026-11-19.md`), each with its default taken, and data requests 542 (uranium and critical minerals) and 552.

- Signed off by:
- Date:
- Items left open ruled, and how:

<!-- The sections below are written from the manifest by resource_layers.py --method-doc -->

## Wind speed at 100 m (`wind_speed_100m`)

- **What it is.** The publisher's words: "This data provides modeled annual average wind speed for the contiguous United States both onshore and offshore for the period 2007-2013." "Raster value: Multi-year (2007-2013) Annual Average Wind Speed, meters per second, at 100 meters above surface level." It is a model's long-run average, not a measurement at a mast and not a forecast; it says nothing of a turbine's output, of land that may be used or of the grid. The source's cell is 2 km in a Lambert projection, which is wider than 0.025 degrees of longitude in the north, so the finest level is 0.05 degrees. The landing page that listed the file (NREL's wind resource maps page) no longer exists since the laboratory's site moved to nlr.gov; the file itself is still on the laboratory's server.
- **Publisher.** National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL). Wind Integration National Dataset (WIND) Toolkit, Multi-year Annual Average (wtk_conus_100m_mean_masked.tif).
- **File.** `nlr/us-wind-data.zip` in the raw store, 185,455,757 bytes, sha256 `3c9f29dedc92e6ef`, retrieved 2026-10-07T21:33:22Z from <https://www.nlr.gov/docs/libraries/gis/us-wind-data.zip>.
- **Vintage.** 2007-2013 (the file's metadata: "Multi-year (2007-2013) Annual Average Wind Speed, meters per second, at 100 meters above surface level"); publication date 2015.
- **Extent.** contiguous United States, onshore and offshore. Source resolution: 2 km ("2km x 2km").
- **Reduction.** each source cell is assigned by its centre to a cell of a longitude and latitude grid (WGS84); a cell's value is the mean of the source's own valid cells in it; a cell with fewer than half of its source cells valid is empty; no interpolation, no filling, no smoothing; no level finer than the source's own cell.
- **Unit.** m/s (annual mean wind speed). The source's own cells: minimum 1.364, mean 6.948, maximum 14.2 over 2,329,810 cells with a value.
- **Levels.**

  | cell (degrees) | file | columns x rows | cells with a value | bytes | mean weighted by source cells | the source's mean over the same cells | share of the source's cells kept |
  |---|---|---|---|---|---|---|---|
  | 0.2 | `wind_speed_100m_0p2.json` | 319 x 128 | 27,060 | 111,014 | 6.9471 | 6.9471 | 99.64% |
  | 0.1 | `wind_speed_100m_0p1.json` | 638 x 256 | 108,190 | 437,670 | 6.9475 | 6.9475 | 99.79% |
  | 0.05 | `wind_speed_100m_0p05.json` | 1276 x 512 | 433,080 | 1,744,297 | 6.9479 | 6.9479 | 99.91% |
- **Terms.** <https://www.nlr.gov/disclaimer> (saved as `nlr/terms/nlr_disclaimer.html`, sha256 `a31b7d7f8d333e16`): "The user is granted the right, without any fee or cost, to use or copy the Data, provided that this entire notice appears in all copies of the Data. Further, the user agrees to credit the U.S. Department of Energy (DOE)/NLR/ALLIANCE in any publication that results from the use of the Data."
- **The laboratory's notice** travels with the data: it is printed in full at the end of this document.
- **Credit.** U.S. Department of Energy (DOE)/NLR/ALLIANCE.

## Wind capacity factor (supply curve sites) (`wind_capacity_factor`)

- **What it is.** No gross capacity factor raster was found among the files the laboratory offers without a key, so this is not one, and it is not named one. It is the capacity factor column of the laboratory's 2024 land-based wind supply curve, in the source's words: "Mean capacity factor across 11.5km grid-cell", unit "ratio". The column's name is capacity_factor_ac; the file's column list does not say whether losses are taken off, and the technical report (NREL/TP-6A20-91900) was not read, so the layer does not say gross or net. It is the modelled output of a 2035 turbine (115 m hub, 170 m rotor), one value for each 11.5 km cell that has land left to build on under the "open access" siting scenario: a cell with no developable land is absent, which is an absence of land in the model, not of wind. The resource column is the source's "Annual average wind speed at the modeled turbine hub-height".
- **Publisher.** National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL). United States Land-based Wind Supply Curves 2024, open access siting, 2035 moderate technology, 115 m hub height, 170 m rotor diameter (lbw_open_access_2035_moderate_115hh_170rd_supply_curve.csv).
- **File.** `openei/lbw_open_access_2035_moderate_115hh_170rd_supply_curve.csv` in the raw store, 12,829,421 bytes, sha256 `ef13116bd66f3115`, retrieved 2026-10-07T21:39:41Z from <https://data.openei.org/files/8314/lbw_open_access_2035_moderate_115hh_170rd_supply_curve.csv>.
- **Vintage.** the 2024 edition, published 2025-01-01 on the Open Energy Data Initiative; the file models a 2035 turbine ("2035 moderate", 115 m hub height, 170 m rotor diameter); the weather years behind the mean are not stated in the files.
- **Extent.** contiguous United States, land only, where the open access scenario leaves developable area. Source resolution: 11.5 km ("Centroid latitude of the 11.5km grid-cell").
- **Reduction.** none: every row of the source at the source's own centroid (coordinates to 3 decimals, the capacity factor to 4); the state, county, cost and transmission columns are left out of the web file.
- **Web file.** `wind_capacity_factor.json`, 2,746,451 bytes, 56,528 rows. Mean capacity factor across 11.5km grid-cell (the source's capacity_factor_ac), in ratio: minimum 0.01179, mean 0.3116, maximum 0.5445 over 56,528 rows.
- **Terms.** <https://data.openei.org/submissions/8314> (saved as `openei/terms/openei_submission_8314.html`, sha256 `fe920bd0f61a40aa`): "Content is available under Creative Commons Attribution 4.0 unless otherwise noted."
- **Credit.** U.S. Department of Energy (DOE)/NLR/ALLIANCE; Creative Commons Attribution 4.0.

## Global Horizontal Irradiance (`solar_ghi`)

- **What it is.** The publisher's words: "This data provides annual average daily total solar resource averaged over surface cells of 0.038 degrees in both latitude and longitude, or nominally 4 km in size. The solar radiation values represent the resource available to solar energy systems." "The data are averaged from hourly model output over 19 years (1998-2016)." The unit: the metadata's line reads "Raster value: solar irradiance in kWh/m2/year", but its description says annual average daily total, and the values are daily totals (a few kWh a square metre); the layer is labelled kWh/m2/day and the values are the file's own, unconverted. It is a satellite-based model's long-run average, not a measurement on the ground, and not the output of a solar plant. The source's file covers most of the Americas up to 60 degrees north; this layer keeps the box of the contiguous states. The landing page that listed the file (NREL's solar resource maps page) no longer exists since the laboratory's site moved to nlr.gov; the file itself is still on the laboratory's server.
- **Publisher.** National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL). Physical Solar Model version 3 Global Horizontal Irradiance Multi-year Annual Average (nsrdb3_ghi.tif), National Solar Radiation Database.
- **File.** `nlr/nsrdbv3_ghi.zip` in the raw store, 140,087,273 bytes, sha256 `55531ec07a5f4c47`, retrieved 2026-10-07T21:33:58Z from <https://www.nlr.gov/docs/libraries/gis/nsrdbv3_ghi.zip>.
- **Vintage.** 1998-2016 (the file's metadata: "The data are averaged from hourly model output over 19 years (1998-2016)"); publication date 2018.
- **Extent.** the box of the contiguous United States, longitude -125.0 to -66.8, latitude 24.4 to 49.6 (the source also holds values for the parts of Canada and Mexico inside the box, and they are kept); Hawaii and Alaska south of 60 degrees north are in files of their own. Source resolution: 0.04 degrees in the file (the metadata: "surface cells of 0.038 degrees in both latitude and longitude, or nominally 4 km in size").
- **Reduction.** each source cell is assigned by its centre to a cell of a longitude and latitude grid (WGS84); a cell's value is the mean of the source's own valid cells in it; a cell with fewer than half of its source cells valid is empty; no interpolation, no filling, no smoothing; no level finer than the source's own cell.
- **Unit.** kWh/m2/day (annual average daily total solar resource). The source's own cells: minimum 2.76, mean 4.604, maximum 6.504 over 680,754 cells with a value.
- **Levels.**

  | cell (degrees) | file | columns x rows | cells with a value | bytes | mean weighted by source cells | the source's mean over the same cells | share of the source's cells kept |
  |---|---|---|---|---|---|---|---|
  | 0.2 | `solar_ghi_0p2.json` | 291 x 126 | 27,237 | 99,902 | 4.6023 | 4.6023 | 99.72% |
  | 0.1 | `solar_ghi_0p1.json` | 582 x 252 | 109,086 | 393,230 | 4.6032 | 4.6032 | 99.90% |
  | 0.05 | `solar_ghi_0p05.json` | 1164 x 504 | 436,141 | 1,566,545 | 4.6036 | 4.6036 | 99.99% |
- **Also held: Hawaii.** `solar_ghi_hawaii_0p2.json` (0.2 degrees, 3,644 bytes), `solar_ghi_hawaii_0p1.json` (0.1 degrees, 8,204 bytes), `solar_ghi_hawaii_0p05.json` (0.05 degrees, 26,447 bytes). The source's own cells there: minimum 2.88, mean 5.513, maximum 6.912 over 3,200 cells.
- **Also held: Alaska south of 60 degrees north, with the part of Canada inside the same box.** `solar_ghi_alaska_0p2.json` (0.2 degrees, 32,245 bytes), `solar_ghi_alaska_0p1.json` (0.1 degrees, 122,605 bytes), `solar_ghi_alaska_0p05.json` (0.05 degrees, 484,049 bytes). The source's own cells there: minimum 1.56, mean 2.38, maximum 3.36 over 58,634 cells.
- **Terms.** <https://www.nlr.gov/disclaimer> (saved as `nlr/terms/nlr_disclaimer.html`, sha256 `a31b7d7f8d333e16`): "The user is granted the right, without any fee or cost, to use or copy the Data, provided that this entire notice appears in all copies of the Data. Further, the user agrees to credit the U.S. Department of Energy (DOE)/NLR/ALLIANCE in any publication that results from the use of the Data."
- **The laboratory's notice** travels with the data: it is printed in full at the end of this document.
- **Credit.** U.S. Department of Energy (DOE)/NLR/ALLIANCE.

## Direct Normal Irradiance (`solar_dni`)

- **What it is.** The publisher's words: "This data provides annual average daily total solar resource averaged over surface cells of 0.038 degrees in both latitude and longitude, or nominally 4 km in size. The solar radiation values represent the resource available to solar energy systems." "The data are averaged from hourly model output over 19 years (1998-2016)." The unit: the metadata's line reads "Raster value: solar irradiance in kWh/m2/year", but its description says annual average daily total, and the values are daily totals (a few kWh a square metre); the layer is labelled kWh/m2/day and the values are the file's own, unconverted. It is a satellite-based model's long-run average, not a measurement on the ground, and not the output of a solar plant. The source's file covers most of the Americas up to 60 degrees north; this layer keeps the box of the contiguous states. The landing page that listed the file (NREL's solar resource maps page) no longer exists since the laboratory's site moved to nlr.gov; the file itself is still on the laboratory's server.
- **Publisher.** National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL). Physical Solar Model version 3 Direct Normal Irradiance Multi-year Annual Average (nsrdb3_dni.tif), National Solar Radiation Database.
- **File.** `nlr/nsrdbv3_dni.zip` in the raw store, 143,634,924 bytes, sha256 `97f0e7e621f6fef9`, retrieved 2026-10-07T21:34:33Z from <https://www.nlr.gov/docs/libraries/gis/nsrdbv3_dni.zip>.
- **Vintage.** 1998-2016 (the file's metadata: "The data are averaged from hourly model output over 19 years (1998-2016)"); publication date 2018.
- **Extent.** the box of the contiguous United States, longitude -125.0 to -66.8, latitude 24.4 to 49.6 (the source also holds values for the parts of Canada and Mexico inside the box, and they are kept); Hawaii and Alaska south of 60 degrees north are in files of their own. Source resolution: 0.04 degrees in the file (the metadata: "surface cells of 0.038 degrees in both latitude and longitude, or nominally 4 km in size").
- **Reduction.** each source cell is assigned by its centre to a cell of a longitude and latitude grid (WGS84); a cell's value is the mean of the source's own valid cells in it; a cell with fewer than half of its source cells valid is empty; no interpolation, no filling, no smoothing; no level finer than the source's own cell.
- **Unit.** kWh/m2/day (annual average daily total solar resource). The source's own cells: minimum 2.76, mean 5.415, maximum 9 over 680,754 cells with a value.
- **Levels.**

  | cell (degrees) | file | columns x rows | cells with a value | bytes | mean weighted by source cells | the source's mean over the same cells | share of the source's cells kept |
  |---|---|---|---|---|---|---|---|
  | 0.2 | `solar_dni_0p2.json` | 291 x 126 | 27,237 | 99,902 | 5.415 | 5.415 | 99.72% |
  | 0.1 | `solar_dni_0p1.json` | 582 x 252 | 109,086 | 393,230 | 5.4152 | 5.4152 | 99.90% |
  | 0.05 | `solar_dni_0p05.json` | 1164 x 504 | 436,141 | 1,566,545 | 5.4152 | 5.4152 | 99.99% |
- **Also held: Hawaii.** `solar_dni_hawaii_0p2.json` (0.2 degrees, 3,644 bytes), `solar_dni_hawaii_0p1.json` (0.1 degrees, 8,204 bytes), `solar_dni_hawaii_0p05.json` (0.05 degrees, 26,447 bytes). The source's own cells there: minimum 1.992, mean 5.547, maximum 8.976 over 3,200 cells.
- **Also held: Alaska south of 60 degrees north, with the part of Canada inside the same box.** `solar_dni_alaska_0p2.json` (0.2 degrees, 32,245 bytes), `solar_dni_alaska_0p1.json` (0.1 degrees, 122,605 bytes), `solar_dni_alaska_0p05.json` (0.05 degrees, 484,049 bytes). The source's own cells there: minimum 0.912, mean 2.473, maximum 4.272 over 58,634 cells.
- **Terms.** <https://www.nlr.gov/disclaimer> (saved as `nlr/terms/nlr_disclaimer.html`, sha256 `a31b7d7f8d333e16`): "The user is granted the right, without any fee or cost, to use or copy the Data, provided that this entire notice appears in all copies of the Data. Further, the user agrees to credit the U.S. Department of Energy (DOE)/NLR/ALLIANCE in any publication that results from the use of the Data."
- **The laboratory's notice** travels with the data: it is printed in full at the end of this document.
- **Credit.** U.S. Department of Energy (DOE)/NLR/ALLIANCE.

## Identified hydrothermal systems (`geothermal_hydrothermal_sites`)

- **What it is.** Hydrothermal: the natural hot-water systems already identified. USGS's words: "This layer contains the locations of identified moderate (90 - 150° C) and high (> 150° C) temperature geothermal systems and associated reservoir volumes, temperatures, and estimated electric power generation potential. These results were used in characterizing the geothermal resource potential in the United States." "This is to be used to identify locations and characteristics of identified geothermal systems." Each point is one identified system with USGS's estimate of the electric power it could generate (the mean, and the 95 and 5 percent values). It is an estimate of a reservoir's potential, not a power plant and not what is installed. Undiscovered systems and enhanced geothermal are not in this layer.
- **Publisher.** U.S. Geological Survey (USGS). Identified Moderate and High Temperature Geothermal Systems (IdentifiedGeothermalSystems.shp), DeAngelo and Williams, 2010, from the 2008 Assessment of moderate- and high-temperature geothermal resources of the United States.
- **File.** `usgs/IdentifiedGeothermalSystems/IdentifiedGeothermalSystems.shp` in the raw store, 7,184 bytes, sha256 `7724cb19112c68c2`, retrieved 2026-10-07T21:39:30Z from <https://www.sciencebase.gov/catalog/file/get/6606f534d34e4df16bd58277?f=__disk__ae%2Fbd%2F32%2Faebd32c1cf3b64ce4f19dc6e2535e5a5bc3382da>.
- **Vintage.** the 2008 assessment (USGS Fact Sheet 2008-3082); the data file is dated 2010 and was released again on ScienceBase on 29 March 2024 (metadata date 20240329).
- **Extent.** United States: the western states, Alaska and Hawaii. Source resolution: one point for each identified system.
- **Reduction.** none: every row of the source, at the source's own longitude and latitude (NAD83 read as WGS84, coordinates to 4 decimals).
- **Web file.** `geothermal_hydrothermal_sites.json`, 24,677 bytes, 253 rows. Mean Megawatts electric (MWe), the source's MWe_Mean, in MWe: minimum 0.6, mean 35.81, maximum 2,210 over 253 rows.
- **Terms.** <https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits> (saved as `usgs/terms/usgs_copyrights_and_credits.html`, sha256 `be68d363d1ab447e`): "USGS-authored or produced data and information are considered to be in the U.S. Public Domain. [...] When using information from USGS information products, publications, or websites, we ask that proper credit be given."
- **The file's own notice.** "Use constraints: None. No warranty, expressed or implied, is made regarding the accuracy or utility of this data for general or scientific purposes, nor shall the act of distribution constitute any such warranty. The U.S. Geological Survey shall not be held liable for improper or incorrect use of this data."
- **Credit.** Credit: U.S. Geological Survey.

## Hydrothermal favorability (western states) (`geothermal_hydrothermal_favorability`)

- **What it is.** Hydrothermal, undiscovered: where such systems are more likely to be found. USGS's words: "This is a surface showing relative favorability for the presence of geothermal systems in the western United States. It is an average of 12 models that correlates different geological and geophysical factors to the known presence of moderate (90 - 150° C) to high (> 150° C) temperature geothermal systems. as discussed in the reference in the 'Larger Work' section of this metadata file. The data is represented as a polygon contour file as well as a raster." "This is intended to highlight areas of elevated potential for the presence of undiscovered moderate (90 - 150° C) to high (> 150° C) temperature geothermal systems. It is not meant to be used to locate exact areas for exploration." The file gives ten classes (GRIDCODE 1 to 10), each with a range in its Descript field (from "< 0.1" to "> 15"); the file's metadata does not say what unit those ranges are in, so the layer shows the class and the range as written and nothing more. It covers the western states only. It is not enhanced geothermal.
- **Publisher.** U.S. Geological Survey (USGS). Geothermal Favorability Map Derived From Logistic Regression Models (FavorabilitySurface.shp), DeAngelo and Williams, 2010.
- **File.** `usgs/FavorabilitySurface/FavorabilitySurface.shp` in the raw store, 3,302,616 bytes, sha256 `d9eb255587626875`, retrieved 2026-10-07T21:39:32Z from <https://www.sciencebase.gov/catalog/file/get/6606ed51d34e4df16bd58251?f=__disk__79%2Fb1%2Fce%2F79b1ce18796d6fc4ae5b9292c58bd8aaee4846e5>.
- **Vintage.** the 2008 assessment; the data file is dated 2010 and was released again on ScienceBase on 29 March 2024 (metadata date 20240329).
- **Extent.** western United States. Source resolution: polygon contours of a favorability surface.
- **Reduction.** the polygons simplified together as one coverage, so that neighbours still meet along one line (tolerance 0.03 degrees); coordinates to 3 decimals; no feature dropped.
- **Web file.** `geothermal_hydrothermal_favorability.json`, 1,602,513 bytes, 10 features.
- **Classes, in the source's words.** 1: < 0.1; 2: 0.1 - 0.5; 3: 0.5 - 1; 4: 1 - 2; 5: 2 - 3; 6: 3 - 4; 7: 4 - 5; 8: 5 - 10; 9: 10 - 15; 10: > 15.
- **Terms.** <https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits> (saved as `usgs/terms/usgs_copyrights_and_credits.html`, sha256 `be68d363d1ab447e`): "USGS-authored or produced data and information are considered to be in the U.S. Public Domain. [...] When using information from USGS information products, publications, or websites, we ask that proper credit be given."
- **The file's own notice.** "Use constraints: None. No warranty, expressed or implied, is made regarding the accuracy or utility of this data for general or scientific purposes, nor shall the act of distribution constitute any such warranty. The U.S. Geological Survey shall not be held liable for improper or incorrect use of this data."
- **Credit.** Credit: U.S. Geological Survey.

## Deep enhanced geothermal favorability (`geothermal_egs_favorability`)

- **What it is.** Enhanced geothermal (EGS): heat in deep rock that would need an engineered reservoir, kept apart from the hydrothermal layers. The publisher's words: "This dataset is a qualitative assessment of geothermal potential (Enhanced Geothermal System EGS) for the US based on Levelized Cost of Electricity, with CLASS 1 being most favorable, and CLASS 5 being least favorable. This dataset does not include shallow EGS resources located near hydrothermal sites or USGS assessment of undiscovered hydrothermal resources. The source data for deep EGS includes temperature at depth from 3 to 10 km provided by Southern Methodist University Geothermal Laboratory (Blackwell & Richards, 2009) and analyses (for regions with temperatures equal to or greater than 150°C) performed by NREL (2009). CLASS 999 regions have temperatures less than 150°C at 10 km depth and were not assessed for deep EGS potential. Temperature at depth data for deep EGS in Alaska and Hawaii not available." The classes rank relative favorability; they are not megawatts, and the ranking rests on a 2009 estimate of the levelized cost of electricity. The landing page that listed the file (NREL's geothermal maps page) no longer exists since the laboratory's site moved to nlr.gov; the file itself is still on the laboratory's server.
- **Publisher.** National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL). Geothermal Resource of the United States: favorability of deep enhanced geothermal systems (GeothermalLCOE_NoExclusionsforAtlas.shp).
- **File.** `nlr/egs.zip` in the raw store, 5,773,628 bytes, sha256 `fdf8bcfb6dcc9825`, retrieved 2026-10-07T21:39:34Z from <https://www.nlr.gov/docs/libraries/gis/egs.zip>.
- **Vintage.** 2009 (the file's metadata: analyses "performed by NREL (2009)" on temperature at depth from Southern Methodist University Geothermal Laboratory, Blackwell and Richards, 2009); metadata dated 23 February 2012.
- **Extent.** contiguous United States (the source: "Temperature at depth data for deep EGS in Alaska and Hawaii not available"). Source resolution: polygons of classes.
- **Reduction.** the polygons simplified together as one coverage, so that neighbours still meet along one line (tolerance 0.02 degrees); coordinates to 3 decimals; no feature dropped.
- **Web file.** `geothermal_egs_favorability.json`, 873,490 bytes, 1,007 features.
- **Classes, in the source's words.** 1: Class 1 (most favorable); 2: Class 2; 3: Class 3; 4: Class 4; 5: Class 5 (least favorable); 999: Class 999 (temperatures less than 150 C at 10 km depth: not assessed for deep EGS potential).
- **Terms.** <https://www.nlr.gov/disclaimer> (saved as `nlr/terms/nlr_disclaimer.html`, sha256 `a31b7d7f8d333e16`): "The user is granted the right, without any fee or cost, to use or copy the Data, provided that this entire notice appears in all copies of the Data. Further, the user agrees to credit the U.S. Department of Energy (DOE)/NLR/ALLIANCE in any publication that results from the use of the Data."
- **The file's own notice.** "This GIS data was developed by the National Renewable Energy Laboratory ("NREL"), which is operated by the Alliance for Sustainable Energy, LLC for the U.S. Department of Energy ("DOE"). The user is granted the right, without any fee or cost, to use, copy, modify, alter, enhance and distribute this data for any purpose whatsoever, provided that this entire notice appears in all copies of the data. Further, the user of this data agrees to credit NREL in any publications or software that incorporate or use the data. Access to and use of the GIS data shall further impose the following obligations on the User. The names DOE/NREL may not be used in any advertising or publicity to endorse or promote any product or commercial entity using or incorporating the GIS data unless specific written authorization is obtained from DOE/NREL. The User also understands that DOE/NREL shall not be obligated to provide updates, support, consulting, training or assistance of any kind whatsoever with regard to the use of the GIS data. THE GIS DATA IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL DOE/NREL BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER, INCLUDING BUT NOT LIMITED TO CLAIMS ASSOCIATED WITH THE LOSS OF DATA OR PROFITS, WHICH MAY RESULT FROM AN ACTION IN CONTRACT, NEGLIGENCE OR OTHER TORTIOUS CLAIM THAT ARISES OUT OF OR IN CONNECTION WITH THE ACCESS OR USE OF THE GIS DATA. The User acknowledges that access to the GIS data is subject to U.S. Export laws and regulations and any use or transfer of the GIS data must be authorized under those regulations. The User shall not use, distribute, transfer, or transmit GIS data or any products incorporating the GIS data except in compliance with U.S. export regulations. If requested by DOE/NREL, the User agrees to sign written assurances and other export-related documentation as may be required to comply with U.S. export regulations."
- **The laboratory's notice** travels with the data: it is printed in full at the end of this document.
- **Credit.** NREL (the file's notice); U.S. Department of Energy (DOE)/NLR/ALLIANCE.

## Sedimentary basins (`oil_gas_basins`)

- **What it is.** EIA's words: "Sedimentary basins associated with the EIA shale plays as of 5-6-2011. Sedimentary basin which do not have shale plays as of publication date are not included in this file. Sources for the basins are mostly from the US Geological Survey and state agencies such as the WY Geological Survey." It is an outline of where the basins lie, not a measure of oil or gas in place or of what can be recovered. The file's own limit: "These data and related graphics, if available, are not legal documents and are not intended to be used as such. The information contained in these data is dynamic and may change over time."
- **Publisher.** U.S. Energy Information Administration (EIA). U.S. Sedimentary Basins (SedimentaryBasins_US_May2011_v2.shp).
- **File.** `eia/SedimentaryBasins_US_EIA.zip` in the raw store, 440,871 bytes, sha256 `02a017ccb84bdcc1`, retrieved 2026-10-07T21:26:20Z from <https://www.eia.gov/maps/map_data/SedimentaryBasins_US_EIA.zip>.
- **Vintage.** as of 5-6-2011 (the file's metadata: "Sedimentary basins associated with the EIA shale plays as of 5-6-2011"); file modified 10 March 2016.
- **Extent.** contiguous United States. Source resolution: polygons, no scale stated by the source.
- **Reduction.** each polygon simplified to 0.01 degrees with its topology kept (Douglas-Peucker, one feature at a time); coordinates to 3 decimals; no feature dropped.
- **Web file.** `oil_gas_basins.json`, 68,698 bytes, 32 features. area of the basin (the source's Area_sq_mi), in square miles: minimum 1,289, mean 35,363, maximum 160,408 over 32 features.
- **Terms.** <https://www.eia.gov/about/copyrights_reuse.php> (saved as `eia/terms/eia_copyrights_reuse.html`, sha256 `a9747722112b2c55`): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service. However, if you use or reproduce any of our information products, you should use an acknowledgment, which includes the publication date, such as: "Source: U.S. Energy Information Administration (Oct 2008).""
- **Acknowledgment.** Source: U.S. Energy Information Administration (May 2011).

## Tight oil and shale gas plays (`oil_gas_plays`)

- **What it is.** EIA's words: "General areas for shale plays in the U.S. Source: EIA based on Enverus DrillingInfo Inc., the U.S. Geological Survey, publicly available peer-reviewed research papers, academic theses, and publications of State Geological Agencies. Updated December 2021 with addition of Spraberry and Wolfcamp Plays in the Permian Basin." A play's outline is a general area, not a reserve estimate and not a lease map. The file's own limit: "None (public use). Users are advised to thoroughly review the metadata to understand the appropriate use and limitations of the data."
- **Publisher.** U.S. Energy Information Administration (EIA). Tight Oil and Shale Gas Plays in the U.S. (ShalePlays_US_EIA_Dec2021.shp).
- **File.** `eia/TightOil_ShaleGas_Plays_Lower48_EIA.zip` in the raw store, 323,424 bytes, sha256 `c09b3bd2982754cf`, retrieved 2026-10-07T21:26:20Z from <https://www.eia.gov/maps/map_data/TightOil_ShaleGas_Plays_Lower48_EIA.zip>.
- **Vintage.** updated December 2021 (the file's metadata: "Updated December 2021 with addition of Spraberry and Wolfcamp Plays in the Permian Basin").
- **Extent.** contiguous United States (the source's Lower 48). Source resolution: polygons, "General areas for shale plays in the U.S.".
- **Reduction.** each polygon simplified to 0.01 degrees with its topology kept (Douglas-Peucker, one feature at a time); coordinates to 3 decimals; no feature dropped.
- **Web file.** `oil_gas_plays.json`, 55,755 bytes, 50 features. area of the play (the source's Area_sq_mi), in square miles: minimum 184.8, mean 10,280, maximum 59,054 over 50 features.
- **Terms.** <https://www.eia.gov/about/copyrights_reuse.php> (saved as `eia/terms/eia_copyrights_reuse.html`, sha256 `a9747722112b2c55`): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service. However, if you use or reproduce any of our information products, you should use an acknowledgment, which includes the publication date, such as: "Source: U.S. Energy Information Administration (Oct 2008).""
- **Acknowledgment.** Source: U.S. Energy Information Administration (Dec 2021).

## Hydropower potential at non-powered dams (`hydropower_npd`)

- **What it is.** Oak Ridge's words (the file's readme): "In the last decade, retrofits of existing nonpowered dams (NPDs) have made up the largest share of capacity increases for US hydropower. Accurate estimates of potential capacity and generation at NPDs help identify sites that may be worth investing in detailed feasibility analyses and design exploration. This dataset contains estimates of technical potential capacity and generation at 2,616 NPDs in the conterminous US. This is based on a subset of dams that were found by earlier resource assessments to have at least 100kW of theoretical potential. Historical daily streamflow (modeled or from USGS gauge records) and hydraulic head (based on historical observations or primary purpose and dam height) are the main inputs to the HydroGenerate model, which determines design flow, turbine efficiencies, and assumed friction losses and then calculates nominal capacity, daily generation, and capacity factor. These estimates represent the conditions over the historical period of 1980-2015, and are summarized on a monthly basis (i.e., averaged for each month of the year) and overall (i.e., nominal capacity, average annual generation (MWh), and average annual capacity factor). A total of nearly 4 GW capacity is estimated across all 2,616 NPDs included in the dataset." "Data were acquired from the NID (USACE, 2024), and subset based on estimated hydropower potential from the 2012 resource assessment (Hadjerioua et al, 2012) and spatial proximity to the National Hydrography Dataset, medium resolution network (NHDPlusV2). Design flow was determined as the 30% exceedance flow based on historical modeled streamflow data (Ganesh et al, 2024) or observed streamflow records from USGS gages. Turbine type, efficiency, and nominal capacity were then calculated, along with a daily time series of estimated generation. Finally, capacity factor was determined on a daily basis (daily generation compared to the 24-hour generation at design capacity). All of these values were summarized on a monthly and annual basis." A non-powered dam is a dam that exists and has no power plant. Each point is one such dam with the laboratory's own estimate of the capacity a retrofit could have, the generation of an average year and the capacity factor, from a model of 1980 to 2015 flows; nothing is estimated again here. It is a technical potential: not a plant, not a proposal, not a finding that a retrofit would pay, and not every dam in the country (the file holds the dams an earlier assessment gave at least 100 kW). Alaska and Hawaii are not in the file. The publisher is Oak Ridge National Laboratory, with Idaho National Laboratory; it is not a USGS layer. The file was fetched by its own address, the one HydroSource's dataset page prints, with a plain request; the download form on that page (a name, an e-mail address, a company, an occupation) was not filled and nothing was sent to it (the owner's ruling of 8 October 2026).
- **Publisher.** Oak Ridge National Laboratory (HydroSource), for the U.S. Department of Energy. Technical Potential for Hydropower Capacity at Non-powered Dams (TechPotentialNPDs.csv), Oak Ridge National Laboratory and Idaho National Laboratory, doi:10.21951/HydroCapacity_NPD/2570407.
- **File.** `ornl/npd/TechPotentialNPDs.csv` in the raw store, 1,594,027 bytes, sha256 `84635b4faecc332c`, retrieved 2026-10-08T08:45:07Z from <https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/hydropower-capacity-us-npd/TechPotentialNPDs.csv>.
- **Vintage.** published 3 October 2024, revised 25 June 2025 (HydroSource's page; the file on its server is dated 25 June 2025); the file's readme: "These estimates represent the conditions over the historical period of 1980-2015".
- **Extent.** conterminous United States (the readme: "2,616 NPDs in the conterminous US"). Source resolution: one row for each dam, at the dam's own latitude and longitude.
- **Reduction.** none: every row of the source at the source's own longitude and latitude (North American Datum 83 read as WGS84, coordinates to 4 decimals); the capacity, the generation and the capacity factor are the file's own figures, unconverted; the monthly columns are left out of the web file.
- **Web file.** `hydropower_npd.json`, 401,438 bytes, 2,616 rows. Nominal capacity (the source's cap_mw), in MW: minimum 0.001, mean 1.506, maximum 222.1 over 2,616 rows.
- **Terms.** <https://hydrosource.ornl.gov/data-use-policy/> (saved as `ornl/terms/hydrosource_data_use_policy.html`, sha256 `b6560e74d46f6c13`): "Data hosted on HydroSource is openly shared, without restriction, in accordance with Department of Energy's Public Access Plan. [...] Bibliographic citations should be included in the References section of publications and other media to acknowledge those who have created the data, services, and tools provided by HydroSource. Proper citations include the authors, title, publisher, and Digital Object Identifier (DOI) and will allow the products to be discovered and re-used by others. The proper citation for each HydroSource product is provided on its landing page."
- **Credit.** Citation, as the publisher asks: Hansen, CH, J Gallego Calderon, C Bastidas Pachecho, C Davis, R Mendadhala, and G Russell. 2025. Technical Potential for Hydropower Capacity at Nonpowered Dams. HydroSource. Oak Ridge National Laboratory, Oak Ridge, Tennessee, USA. https://hydrosource.ornl.gov/data/datasets/hydropower-capacity-us-npd/.

## Hydropower potential of new stream-reach development (`hydropower_nsd`)

- **What it is.** Oak Ridge's words (the file's metadata): "This dataset is a summary of hydropower potential from new stream-reach development (NSD). This dataset consists of geo-referenced digital data and associated attributes created by the DOE/ORNL NSD Resource Assessment (http://nhaap.ornl.gov/nsd)." New stream-reach development is the hydropower that could be built on stretches of river that have no dam and no plant today. Oak Ridge publishes it summed to the HUC10 watershed (a drainage area of the federal Watershed Boundary Dataset), and that is what is drawn: each watershed is shaded by the file's own total for it, in the file's words "The HUC10-level Total Potential capacity from identified stream-reaches with capacity greater than 1MW". The figure belongs to the watershed as a whole: the file does not say where in it the reaches lie, so nothing is drawn at a site and nothing is spread or estimated again here. A larger watershed can show more than a smaller one with the same rivers. Of the 15,401 watersheds in the file, 2,027 hold a capacity and are drawn; 9,484 count no stream-reach above 1 MW and 3,890 carry the file's code -999 in that count (the file does not say what the code stands for); both carry -9999 as their capacity and are not drawn. For 1 of the watersheds drawn (1705010103) the shapefile holds no annual energy and no capacity factor, where the publisher's workbook writes 0: none is shown. It is a potential before any study of a site. The file's own limit: "The distributor shall not be held liable for improper or incorrect use of this data, based on the description of appropriate/inappropriate uses described in this metadata document. It is strongly recommended that this data is directly acquired from the distributor and not indirectly through other sources which may have changed the data in some way. The ORNL should be acknowledged as the data source in products derived from these data. The New Stream-reach Potential is public information and may be interpreted by all organizations, agencies, units of government, or others based on needs; however, they are responsible for the appropriate application of the data. The limitations of computed potential hydropower energy and capacity are described by Hadjerioua et al (2013), in which these estimates do not represent the actual numbers feasible for engineering design. It will be the users' sole responsibility to determine whether if any site is worthy for further investment." Alaska and Hawaii are not in this file. The publisher is Oak Ridge National Laboratory; it is not a USGS layer. The outlines are simplified for the web. The file was fetched by its own address, the one HydroSource's dataset page prints, with a plain request; the download form on that page (a name, an e-mail address, a company, an occupation) was not filled and nothing was sent to it (the owner's ruling of 8 October 2026).
- **Publisher.** Oak Ridge National Laboratory (HydroSource), for the U.S. Department of Energy. Hydropower Potential from New Stream-Reach Development, Aggregated Summary of HUC10 Watersheds for the Conterminous United States (ORNL_NHAAP_NSD_SR_All_v1.shp, version 1), Oak Ridge National Laboratory.
- **File.** `ornl/nsd/ORNL_NHAAP_NSD_SR_All_v1.zip` in the raw store, 564,790,485 bytes, sha256 `a8ab06e4dfea4a31`, retrieved 2026-10-08T08:47:16Z from <https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/hydropower-potential-new-stream-reach-development-conterminous-united-states/ORNL_NHAAP_NSD_SR_All_v1.zip>.
- **Vintage.** published 31 December 2014 (HydroSource's page); the file's own metadata is dated 10 January 2014 and its workbook was created on 2013-03-15, version 1; the years of flow behind the estimate are not stated in the files.
- **Extent.** conterminous United States, by HUC10 watershed (the file's words: "Hydropower Potential from New Stream-Reach Development, Aggregated Summary of HUC10 Watersheds for the Conterminous United States."). Source resolution: the HUC10 watershed of the Watershed Boundary Dataset: 15,401 watersheds in the file, each a total over its stream-reaches of more than 1 MW.
- **Reduction.** each polygon simplified to 0.01 degrees with its topology kept (Douglas-Peucker, one feature at a time: a thin gap or overlap can show between neighbours when zoomed far in); coordinates to 3 decimals; no feature dropped; only the 2,027 watersheds for which the file gives a capacity are in the web file.
- **Web file.** `hydropower_nsd.json`, 1,717,503 bytes, 2,027 features. The HUC10-level Total Potential capacity from identified stream-reaches with capacity greater than 1MW (the source's P_MW_Sum, a HUC10 total), in MW: minimum 1, mean 25.41, maximum 922.2 over 2,027 features.
- **Terms.** <https://hydrosource.ornl.gov/data-use-policy/> (saved as `ornl/terms/hydrosource_data_use_policy.html`, sha256 `b6560e74d46f6c13`): "Data hosted on HydroSource is openly shared, without restriction, in accordance with Department of Energy's Public Access Plan. [...] Bibliographic citations should be included in the References section of publications and other media to acknowledge those who have created the data, services, and tools provided by HydroSource. Proper citations include the authors, title, publisher, and Digital Object Identifier (DOI) and will allow the products to be discovered and re-used by others. The proper citation for each HydroSource product is provided on its landing page."
- **The file's own notice.** "The distributor shall not be held liable for improper or incorrect use of this data, based on the description of appropriate/inappropriate uses described in this metadata document. It is strongly recommended that this data is directly acquired from the distributor and not indirectly through other sources which may have changed the data in some way. The ORNL should be acknowledged as the data source in products derived from these data. The New Stream-reach Potential is public information and may be interpreted by all organizations, agencies, units of government, or others based on needs; however, they are responsible for the appropriate application of the data. The limitations of computed potential hydropower energy and capacity are described by Hadjerioua et al (2013), in which these estimates do not represent the actual numbers feasible for engineering design. It will be the users' sole responsibility to determine whether if any site is worthy for further investment."
- **Credit.** The file asks: "The ORNL should be acknowledged as the data source in products derived from these data." Source: Oak Ridge National Laboratory, New Stream-reach Development Resource Assessment, 2014. Funding and support for the Oak Ridge National Laboratory (ORNL) New Stream-reach Development (NSD) Resource Assessment were provided by the Department of Energy (DOE) Office of Energy Efficiency and Renewable Energy (EERE) Water Power Program. Support from the U.S. Army Corps of Engineers (USACE), Bureau of Reclamation (Reclamation), U.S. Geological Survey (USGS), National Hydropower Association (NHA), and external reviewers are crucial and deeply appreciated..

## Solid biomass resources by county (`biomass`)

- **What it is.** This is the Energy Department laboratory's county file, not the Billion-Ton study (whose county downloads need an account, so they were left). The publisher's words: "This dataset contains information about the biomass resources generated by county in the United States. It includes the following feedstock categories: crop residues, forest residues, primary mill residues, secondary mill residues, and urban wood waste." The Total field: "This field combines all solid biomass resources by county: crop residues, forest residues, primary mill residues, secondary mill residues, and urban wood waste. Data for 2012, in dry metric tons/year." The value is a county's total, so a large county shows more than a small one with the same resource a square mile. The outlines are simplified for the web: a very small county or independent city (a few square miles) can lose much of its shape, and its value is unchanged. Of primary mill residues the file says: "Note that most of this resource is currently utilized." It is a 2012 estimate of what is generated, not of what is available to a new plant at a price. The landing page that listed the file no longer exists since the laboratory's site moved to nlr.gov; the file itself is still on the laboratory's server.
- **Publisher.** National Laboratory of the Rockies (NLR), until 2025 the National Renewable Energy Laboratory (NREL). Solid biomass resources by county (SolidBiomass.shp), Anelia Milbrandt, NREL.
- **File.** `nlr/solid-biomass.zip` in the raw store, 73,018,962 bytes, sha256 `f48ee40d6de1859d`, retrieved 2026-10-07T21:39:39Z from <https://www.nlr.gov/docs/libraries/gis/solid-biomass.zip>.
- **Vintage.** data for 2012 (the file's metadata: "Data for 2012, in dry metric tons/year"); published 30 October 2014.
- **Extent.** United States by county: the contiguous states, Alaska and Hawaii. Source resolution: county.
- **Reduction.** the polygons simplified together as one coverage, so that neighbours still meet along one line (tolerance 0.015 degrees); coordinates to 3 decimals; no feature dropped.
- **Web file.** `biomass.json`, 2,656,168 bytes, 3,141 features. all solid biomass resources of the county (the source's Total), in dry metric tons/year: minimum 0, mean 100,542, maximum 2,002,700 over 3,141 features.
- **Terms.** <https://www.nlr.gov/disclaimer> (saved as `nlr/terms/nlr_disclaimer.html`, sha256 `a31b7d7f8d333e16`): "The user is granted the right, without any fee or cost, to use or copy the Data, provided that this entire notice appears in all copies of the Data. Further, the user agrees to credit the U.S. Department of Energy (DOE)/NLR/ALLIANCE in any publication that results from the use of the Data."
- **The file's own notice.** "This GIS data was developed by the National Renewable Energy Laboratory ("NREL"), which is operated by the Alliance for Sustainable Energy, LLC for the U.S. Department of Energy ("DOE"). The user is granted the right, without any fee or cost, to use, copy, modify, alter, enhance and distribute this data for any purpose whatsoever, provided that this entire notice appears in all copies of the data. Further, the user of this data agrees to credit NREL in any publications or software that incorporate or use the data. Access to and use of the GIS data shall further impose the following obligations on the User. The names DOE/NREL may not be used in any advertising or publicity to endorse or promote any product or commercial entity using or incorporating the GIS data unless specific written authorization is obtained from DOE/NREL. The User also understands that DOE/NREL shall not be obligated to provide updates, support, consulting, training or assistance of any kind whatsoever with regard to the use of the GIS data. THE GIS DATA IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL DOE/NREL BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER, INCLUDING BUT NOT LIMITED TO CLAIMS ASSOCIATED WITH THE LOSS OF DATA OR PROFITS, WHICH MAY RESULT FROM AN ACTION IN CONTRACT, NEGLIGENCE OR OTHER TORTIOUS CLAIM THAT ARISES OUT OF OR IN CONNECTION WITH THE ACCESS OR USE OF THE GIS DATA. The User acknowledges that access to the GIS data is subject to U.S. Export laws and regulations and any use or transfer of the GIS data must be authorized under those regulations. The User shall not use, distribute, transfer, or transmit GIS data or any products incorporating the GIS data except in compliance with U.S. export regulations. If requested by DOE/NREL, the User agrees to sign written assurances and other export-related documentation as may be required to comply with U.S. export regulations."
- **The laboratory's notice** travels with the data: it is printed in full at the end of this document.
- **Credit.** NREL (the file's notice); U.S. Department of Energy (DOE)/NLR/ALLIANCE.

## Offshore wind lease areas (`offshore_wind_leases`)

- **What it is.** BOEM's words: "Boundaries of renewable energy lease areas, wind planning areas, and marine hydrokinetic planning areas (last file update on 02/05/2025)." These are the outlines of leases, easements and research leases BOEM has issued; a lease is a right to propose a project, not a wind farm and not a measure of the wind. A lease's status may have changed since the file's date. Where the source's ACRES field is 0 (some easements and cable routes) no area is shown: the field is kept as the source wrote it and the value is left empty.
- **Publisher.** Bureau of Ocean Energy Management (BOEM). Renewable Energy Leases and Planning Areas, All Shapefile (Offshore_Wind_Leases_outlines.shp).
- **File.** `boem/boem-renewable-energy-shapefiles.zip` in the raw store, 1,031,812 bytes, sha256 `47c5f33f5d16cede`, retrieved 2026-10-07T21:26:22Z from <https://www.boem.gov/renewable-energy/boem-renewable-energy-shapefiles>.
- **Vintage.** last file update on 02/05/2025 (BOEM's page); the archive on BOEM's server is dated 6 August 2025.
- **Extent.** US Outer Continental Shelf: Atlantic, Gulf and Pacific. Source resolution: lease outlines built from Outer Continental Shelf blocks.
- **Reduction.** coordinates to 4 decimals (about 10 m), so that a narrow easement keeps its shape; no other simplification; no feature dropped.
- **Web file.** `offshore_wind_leases.json`, 208,263 bytes, 51 features. area of the lease (the source's ACRES), in acres: minimum 578, mean 75,124, maximum 176,505 over 46 features.
- **Terms.** <https://www.boem.gov/renewable-energy/mapping-and-data/renewable-energy-gis-data> (saved as `boem/terms/boem_renewable_energy_gis_data.html`, sha256 `f337e0627c8370d8`): "Note to users: Data downloaded from this site is to be used for informational and planning purposes only."
  Also <https://www.doi.gov/copyright> (saved as `boem/terms/doi_copyright.html`, sha256 `6d3ba323adc7d2a4`): "Generally, materials produced by federal agencies are in the public domain and may be reproduced without permission. However, not all materials appearing on this web site are in the public domain."

## Offshore wind planning areas (rescinded July 30, 2025) (`offshore_wind_planning_areas`)

- **What it is.** BOEM's words: "These data are an outline version of BOEM's offshore wind planning areas. These areas represent the current investigations by BOEM for new areas of interest in wind energy development. Individual blocks within each wind planning area dissolved into single polygons to generate the area outlines." BOEM's own name for the layer is "Offshore Wind Planning Area Outlines (Rescinded July 30, 2025)": the planning areas were rescinded, and are shown as the record of where BOEM had been looking, not as areas open to leasing. The archive BOEM offers for download holds the leases only; the planning areas come from BOEM's public map service, which BOEM's page links. The service holds 19 rows; one has no shape and no name and is not drawn. Each area's AREA_STATUS (Active or Inactive) is the source's own field and was last edited before the rescission.
- **Publisher.** Bureau of Ocean Energy Management (BOEM). Offshore Wind Planning Area Outlines (Rescinded July 30, 2025).
- **File.** `boem/Wind_Planning_Area_Boundaries_layer0.geojson` in the raw store, 131,232 bytes, sha256 `bc0623cee11e64bb`, retrieved 2026-10-07T21:28:41Z from <https://services7.arcgis.com/G5Ma95RzqJRPKsWL/ArcGIS/rest/services/Wind_Planning_Area_Boundaries__BOEM_/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson>.
- **Vintage.** data last edited 2025-02-20 (the service's own date); BOEM names the layer "Offshore Wind Planning Area Outlines (Rescinded July 30, 2025)".
- **Extent.** US Outer Continental Shelf. Source resolution: planning area outlines built from Outer Continental Shelf blocks.
- **Reduction.** coordinates to 4 decimals (about 10 m), so that a narrow easement keeps its shape; no other simplification; no feature dropped.
- **Web file.** `offshore_wind_planning_areas.json`, 82,679 bytes, 18 features.
- **Terms.** <https://www.boem.gov/renewable-energy/mapping-and-data/renewable-energy-gis-data> (saved as `boem/terms/boem_renewable_energy_gis_data.html`, sha256 `f337e0627c8370d8`): "Note to users: Data downloaded from this site is to be used for informational and planning purposes only."
  Also <https://www.doi.gov/copyright> (saved as `boem/terms/doi_copyright.html`, sha256 `6d3ba323adc7d2a4`): "Generally, materials produced by federal agencies are in the public domain and may be reproduced without permission. However, not all materials appearing on this web site are in the public domain."

## Not held

- **Gross capacity factor** (`wind_gross_capacity_factor`): Not fetched: no gross capacity factor was found among the files the laboratory (NLR, until 2025 NREL) offers without a key, its developer service needs a key issued to a named person, and no key is asked for.

## Looked for and left

A source that asks for a login, an account or a person's details before it hands over a file is recorded and left. Nothing below was downloaded.

- **Hydropower Potential from New Stream-Reach Development for the Conterminous United States (2014): the environmental attributes (the files named EA).** Oak Ridge National Laboratory (HydroSource), for the U.S. Department of Energy. <https://hydrosource.ornl.gov/data/datasets/hydropower-potential-new-stream-reach-development-conterminous-united-states/>. Left because they describe the environment of each watershed, not the hydropower resource, so the map has no layer for them; the page's file links also open a form that asks for a name, an e-mail address, a company and an occupation, which is never filled. Files: `ORNL_NHAAP_NSD_EA_All_v1.zip` (564,645,432 bytes by the server's own count); `ORNL_NHAAP_NSD_EA_All_v1.xlsx` (575,614 bytes by the server's own count). Its data use policy: <https://hydrosource.ornl.gov/data-use-policy/>.
- **2023 Billion-Ton Report, county data downloads.** Oak Ridge National Laboratory (Bioenergy Knowledge Discovery Framework), for the U.S. Department of Energy. <https://bioenergykdf.ornl.gov/bt23-data-portal>. Left because the county downloads need an account ("Log in to download data").

## The laboratory's notice, in full

The National Laboratory of the Rockies (until 2025 the National Renewable Energy Laboratory) grants the use of its data "provided that this entire notice appears in all copies of the Data". The notice, from <https://www.nlr.gov/disclaimer> as saved on the day of the pull:

> Access to or use of any data or software made available on this server ("Data") shall impose the following obligations on the user, and use of the Data constitutes user's agreement to these terms. The user is granted the right, without any fee or cost, to use or copy the Data, provided that this entire notice appears in all copies of the Data. Further, the user agrees to credit the U.S. Department of Energy (DOE)/NLR/ALLIANCE in any publication that results from the use of the Data. The names DOE/NLR/ALLIANCE, however, may not be used in any advertising or publicity to endorse or promote any products or commercial entities unless specific written permission is obtained from DOE/NLR/ ALLIANCE. The user also understands that DOE/NLR/ALLIANCE are not obligated to provide the user with any support, consulting, training or assistance of any kind with regard to the use of the Data or to provide the user with any updates, revisions or new versions thereof. DOE, NLR, and ALLIANCE do not guarantee or endorse any results generated by use of the Data, and user is entirely responsible for the results and any reliance on the results or the Data in general. USER AGREES TO INDEMNIFY DOE/NLR/ALLIANCE AND ITS SUBSIDIARIES, AFFILIATES, OFFICERS, AGENTS, AND EMPLOYEES AGAINST ANY CLAIM OR DEMAND, INCLUDING REASONABLE ATTORNEYS' FEES, RELATED TO USER'S USE OF THE DATA. THE DATA ARE PROVIDED BY DOE/NLR/ALLIANCE "AS IS," AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL DOE/NLR/ALLIANCE BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER, INCLUDING BUT NOT LIMITED TO CLAIMS ASSOCIATED WITH THE LOSS OF DATA OR PROFITS, THAT MAY RESULT FROM AN ACTION IN CONTRACT, NEGLIGENCE OR OTHER TORTIOUS CLAIM THAT ARISES OUT OF OR IN CONNECTION WITH THE ACCESS, USE OR PERFORMANCE OF THE DATA.
