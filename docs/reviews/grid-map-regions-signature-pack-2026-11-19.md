# The Grid tool's map and its thirteen regions: a signature pack for Samuel (19 November 2026)

Energy Research Warehouse (ERW). Written by session 8606 of chain 504 (`queue/done/504-night-19-november-portable-grid-map-whole-country.md`), the portable laptop, for one sitting. It is in the form of the trackers' pack (`docs/reviews/trackers-signature-pack-2026-11-16.md`). The done line asks each part for a method note you sign, a replication a reader can run, a cross-check against published figures, and a decisions block on the page.

- **What a signature is.** You fill the three lines of the block "Sign-off: the map and the thirteen regions" in `docs/methods/grid_network.md` and commit it, or say it in a prompt and a session writes your words there. A session never signs.
- **What you sign accepts** the rules the block lists, at the defaults of the rulings below. It does not freeze the figures: they move with the hourly snapshot and with the data machine's files.
- **Nothing here is published.** `/grid` is in review, as every page is. Signing does not open it.
- **Where it is.** Branch `wip/8602-grid-regions` (landing request row 42). The addresses below are for the internal view once the row has landed.
- **Order of the sitting.** The map, the regions, the rulings. About thirty minutes; no Stata is needed, the replications are Python and run in seconds.

---

## 1. The map (`/grid?view=network&shape=map`)

**You sign:** the block above, its first three lines.

**The choices that matter most** (on the page: "Decisions on this map (9)", under the map; each with its rule and its source):

| Choice | Default | Source |
|---|---|---|
| The hour the map opens on | The newest hour every reporting pair holds, as the Network view | the hourly snapshot |
| Whose report a tie's megawatts are | The authority whose code sorts first; the other's, sign turned, where the first filed nothing | the snapshot's own rule |
| A region's net exchange | The sum of its pairs so read; not the authority's own total interchange | `replication/grid/crosscheck_map.csv` |
| An authority with no boundary | Listed under the map, not placed by hand (ten of the 70; 21 of the hour's 148 ties are not drawn) | the boundary file holds United States control areas only |
| The shape of a region | The published footprint, simplified; the smaller on top where footprints overlap | HIFLD Control Areas, as the data machine's file holds them |

**Replication** (run it: `python replication/grid/replicate_map.py`; exit 0):

- What the map draws, read from a built page (`map_figures.mjs`), against the same figures computed from the snapshot and the boundary file with none of the page's code: **439 of 439 met** on 19 November 2026 (60 regions with their hovers, 127 ties on the map of the hour's 148, 10 authorities listed, the largest flow of the week 4,761 MW).
- An altered figure is caught (a test alters two and expects two failures).

**Cross-check** (`python replication/grid/crosscheck_map.py`; needs `EIA_API_KEY`; two requests):

| Our figure | Published figure | Source | Result |
|---|---|---|---|
| Each of the 159 pairs' flow at 2026-11-17 04:00 UTC | The report of the same authority in EIA's interchange series | EIA open data, `electricity/rto/interchange-data`, read 19 November 14:49 UTC | 159 of 159 the same to 1 MW |
| Each authority's net exchange (the sum of its pairs) | Its own total interchange | `electricity/rto/region-data`, type TI | 39 of 60 the same to 1 MW; 21 differ |
| PJM: 811 MW exported | 82 MW exported | the same | the two sides of PJM's ties do not agree; the pair rule takes its neighbours' reports for six of its seven ties |
| CAISO: 4,119 MW imported | 5,076 MW imported | the same | as above |

**What to look at** (five minutes):
1. `/grid?view=network`: the network opens first, as before. Press "Map" and back: the same ties in both.
2. Rest the mouse on PJM, then on the line from PJM to New York: one table named, each name once.
3. Open "Decisions on this map" under the map: line 3 gives PJM's two figures.
4. Press "California's evening": the line under the controls says which day is shown.

## 2. The thirteen regions (`/grid?region=cal` and the row "EIA region" under the grid picker)

**You sign:** the block above, its last two lines.

**The choices that matter most** (on the page: "Decisions on this page (the thirteen regions)", thirteen lines):

| Choice | Default | Source |
|---|---|---|
| What a region is | One of EIA's thirteen, with the authorities EIA places in it; none of the ERW's making | Form EIA-930 |
| A part of a tab the file does not hold | Drawn, blank, with its reason on hover; none hidden, none filled | the page standard |
| A month not in the file | Absent, counted under the month chips and named on hover; never zero | the data machine's rule: 90 percent of a month's days complete |
| A source below zero, hour by hour | Drawn down from zero (batteries charging, pumped storage pumping) | the mix library's rule for the average day |
| Storage where CAISO, NYISO or PJM is in the region | The file's figure, with a hover saying who files no battery series | the Storage page, since session 34 |
| The newest month of trade | Shown as held, with its hours ("at most 336 of its 721 hours"), not scaled up | the file's own hours |

**Replication** (run it: `python replication/grid/replicate_regions.py`; exit 0):

- Every figure of the Mix and trade tabs of the thirteen regions, read from a built page (`regions_figures.mjs`), against the same figures computed from the region files with none of the page's code: **1,483 of 1,483 met** on 19 November 2026, on the data machine's rebuilt files (1,349 on the first files; the rebuilt ones hold more months, and session 8610 added two checks a region).
- It replicates the page from its files. The files from the warehouse's tables are the data machine's replication.

**Cross-check** (`python replication/grid/crosscheck_regions.py`; needs `EIA_API_KEY`; about 160 requests, two minutes):

| Our figure | Published figure | Source | Result |
|---|---|---|---|
| Three hours of each region: demand, net imports, the eight sources, their sum | EIA's own regional series for the same hour | EIA open data, `region-data` and `fuel-type-data`, read 19 November 16:55 UTC on the data machine's rebuilt files | 388 of 439 the same to 1 MW (383 of 430 on the first files, at 14:37) |
| Net generation (the sum of the eight sources) | EIA's reported total | the same | 17 of 39: EIA's total is not always the sum of its own codes (the Central region by 315 and 424 MW) |
| The Southeast, 2026-11-11 19:00 UTC: demand 23,757 MW | 24,859 MW | the same | 1,102 MW under; data request 551 |
| California's "other", hour to 2026-11-08 19:00 UTC: minus 9,070 MW | EIA's OTH minus 10,253 MW with petroleum, geothermal and unknown: minus 9,070 MW | the same | the same to the megawatt; EIA's battery code that hour: minus 151 MW |
| Storage for New York and the Mid-Atlantic, wind for the Carolinas and Florida: 0 MW on the first files | no series at all | the same | a figure not held written as zero; data request 551, answered the same day: the rebuilt files hold them blank, and the page draws them blank with why |

**What to look at** (five minutes):
1. `/grid?region=cal`: the chart of the last 35 days; rest the mouse on "Storage"; under the month chips, the count of months not held.
2. `/grid?region=mida&view=gravity`: the line "November 2026 is a part of a month here".
3. `/grid?view=network&shape=map`, click the Tennessee Valley Authority, then "EIA region" in its panel.

## 3. For your ruling (each has its default taken; nothing waits on you)

| # | The question | Default taken |
|---:|---|---|
| 1 | Should a region's hover and panel carry the authority's own total interchange beside the sum of its pairs (PJM: 811 against 82 MW)? | The sum alone, as the Network view has had it; the difference said in the decisions block |
| 2 | Canada's and Mexico's operators have no boundary: marks at the border, or listed? | Listed under the map; nothing placed by hand |
| 3 | Thin state lines on the map, so a place can be found (names stay on hover) | Drawn |
| 4 | The color of a region is the carbon intensity of the latest hour held, not of the hour shown (session 8601) | As the Network view |
| 5 | Should the page say that California's "other" goes far below zero at midday, and what is in it? | Nothing beyond the figure and the Storage row's hover |
| 6 | The average day's chart draws a thin line to zero where a source crosses zero; it is the seven grids' own chart | Left as the grids have it |
| 7 | Data requests 540 (carbon intensity for every authority) and 541 (which side reported, hour by hour) came back as yours: each changes an existing page file | Left as it is |
| 8 | **The 3D network now draws, as it opens, the hour its own slider names** (148 ties where it drew the newest hour's 139; session 8604). It is the one change to the centerpiece | Kept; one line of `site/app/network/Network.tsx` to put back |

## 4. What is not done

- The Clean tab for a region is blank (three parts not held): carbon intensity is computed for the seven grids only (request 540).
- A balancing authority's own mix is in no file; a region gives its authorities together.
- The data machine is rebuilding the region files under a wider rule (the Mid-Atlantic will hold 95 months where it holds 40). When they land, `regions_figures.mjs` is to be run again before `replicate_regions.py`; the script says so and stops.
- No Stata do-file was written for these two: the existing `replication/grid/replicate.do` covers the network's figures, which the map shares.
