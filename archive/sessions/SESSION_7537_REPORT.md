# Session 7537 report: `/map` read as its reader (chain 304, part C, samueloldlaptop, 16 November 2026)

Branch `wip/7537-map-read`, from origin/main `f00c3168c`. The read: `docs/reviews/map-read-2026-11-16.md`.

## What was done

- The reader: a developer checking what is planned within 30 miles of a candidate site. Five cases: Abilene TX (ERCOT), Amarillo TX, New Albany OH (PJM), Mason City IA (MISO), Bakersfield CA (Kern County, CAISO), each 30 miles, on the page's file (EIA 2026-09, queues 2026-11-05, tracker 2026-11-15).
- 18 rows: 7 site faults fixed, 2 data machine, 5 browser, 4 rulings. Part A's rows 6 and 7 cited.
- The main gap: the tab could not answer "within 30 miles of here" at all (a state was the smallest choice, and rows were named only one hover at a time). Now: "Near a point" (latitude, longitude, miles) in the panel and the address; a list under the map of every row chosen, nearest first, with what each date is and where each point is; the point and a dashed circle on the drawing; "Measure from this row" on a card.
- Also fixed: the sentence names the queues the map holds none of (PJM, MISO, NYISO) when queue positions are chosen (Mason City's empty answer said nothing); ERCOT's "Completed" reads "Agreement signed, built or not" in the list and the tiles' tip; a mark's hover says what its date is.
- Tests: `site/scripts/test-map-read.mjs` 42 of 42 (the rows chosen and every distance held to the test's own haversine, for the five cases). Touched-module tests: `tests/test_session7601_map.py`, `test_session167.py`, `test_session105.py`, `test_session114_part2.py`, `test_session241c.py`, `test_session318.py`, `test_session349.py`, `test_session371.py`: 98 passed, 4 skipped by their own rules (tables not on this machine); `site/scripts/test-map-sources.mjs` 37 of 37. `tsc --noEmit`: no error in the changed files (the 15 it reports are the build's generated types and content files, absent without a build).

## Files of the other machine's stack touched (session 7601's, now on main)

- `site/app/map/ProjectMap.tsx` (the panel's point and distance, the list `NearList`, the queues line, the circle, the card's button, the hover's date words, an optional `serverSearch` prop the page does not pass).
- `site/lib/projectmap.ts` (`at` and `within` in the choice and the address; `pointOf`, `milesBetween`, `nearOf`, `circleOf`, `nearest`, `PLACED_AT`, `DATE_WORDS`, `statusWords`; `select` keeps a row inside the distance). With no point, every function returns what it did: the 123 views of `map-figures.mjs` are unchanged.
- `site/app/map/Decisions.tsx` (a twelfth line, "near"), `docs/methods/map.md` (sections 8, 10 and 14 extended), `tests/test_session7601_map.py` (11 decisions become 12).
- New: `site/scripts/map-read-page.mjs`, `site/scripts/test-map-read.mjs`, `docs/reviews/map-read-2026-11-16.md`.

## What to review

1. `https://erw-flame.vercel.app/map?kind=planned,queue,datacenter&at=32.4487,-99.7331&within=30`: the sentence "within 30 miles of 32.4487, -99.7331 ... 9 planned units ... 2,232 MW; ... 38 queue positions, 11,559 MW requested"; a pin and a dashed circle around Abilene; the list "Within 30 miles of ..., nearest first", Summerhill BESS first at 5.7 miles.
2. Click "Buffalo Gap 3 Wind Repower" in the list: its card opens; the status reads "Agreement signed, built or not (ERCOT; the table says completed)".
3. Clear the point; click a unit on the drawing; press "Measure from this row"; type 30 in miles: the list appears around that unit.
4. `https://erw-flame.vercel.app/map?kind=planned,queue,datacenter&at=43.1536,-93.201&within=30`: "Nothing on this map matches these choices. Queue positions are those of ERCOT, CAISO, SPP and ISO-NE alone: no queue position of PJM, MISO or NYISO is on this map."
5. `https://erw-flame.vercel.app/map?kind=planned,queue,datacenter&at=35.3733,-119.0187&within=30`: "89 of the 89 queue positions are measured from their county's or town's point".
6. Open "Decisions on this page": 12 lines, the new one on the distance.

## Needs the key

Nothing.

## Decisions made without you

- A point is typed as coordinates (no gazetteer on the site); both a point and a distance are needed, one alone chooses nothing.
- The list draws the nearest 1,000 rows and says so when there are more; the totals count every row.
- Distance from a queue position is from its county's or town's point, said in the list and the tip; no position is moved.
- The tile "Completed" keeps the file's word; the list and the tip say what ERCOT's is (the file's change is the data machine's).

## For Samuel's ruling

- Row 8: a planned unit and its own queue position are both listed (Chimney Rock BESS, Funston Solar, Tiger Solar near Abilene). Default: both stay, each kind its own sum. Other: match by name and county.
- Row 9: place names. Default: coordinates or a card. Other: Census places in the page's file.
- Row 10: Project Matador's 161 units in Carson County read "Grid: ERCOT" (EIA's code). Default: EIA's code stands.
- Row 11: the unplaced count "Some ... held (license needed)" is blanked by ISO-NE's hold though its key names no held grid (the sibling sessions' known fault). Default: recorded; hold logic unchanged.

## Rows for the coordinator

### (a) Landing request row 35 (`docs/state/landing_request_oldlaptop.md`)

| 35 | `wip/7537-map-read` | `<head>` | `7537-map-read` | 7537 | 2026-11-16 | `site/scripts/test-map-read.mjs` (42 of 42, the Projects tab drawn to HTML without a build on the page's own file, five cases); `tests/test_session7601_map.py`, `test_session167`, `test_session105`, `test_session114_part2`, `test_session241c`, `test_session318`, `test_session349`, `test_session371`: 98 passed, 4 skipped by their own rules; `test-map-sources.mjs` 37 of 37; no build made here | requested |

## Row 35: what it holds (chain 304, session 7537, the project map read as a developer checking what is planned within 30 miles of a site)

- **From** origin/main `f00c3168c`. Report: `archive/sessions/SESSION_7537_REPORT.md` on the branch. The read: `docs/reviews/map-read-2026-11-16.md` (18 rows).
- **What changes:**
  - `site/lib/projectmap.ts`: the choice gains `at` and `within` (address `?at=lat,lon&within=miles`); `select` keeps a row whose own point is within the distance when both are given; new pure functions `pointOf`, `milesBetween`, `nearOf`, `circleOf`, `nearest`, `statusWords`, and the word lists `PLACED_AT`, `DATE_WORDS`.
  - `site/app/map/ProjectMap.tsx`: "Near a point" in the panel; the list of rows within the distance, nearest first, under the map; the point and a dashed circle on the drawing; the sentence names the queues drawn and not drawn when queue positions are chosen; "Measure from this row" on a card; a mark's hover says what its date is; the queue tiles' tip says what ERCOT's "Completed" is; an optional `serverSearch` prop the page does not pass.
  - `site/app/map/Decisions.tsx`: a twelfth line (the distance); `docs/methods/map.md`: sections 8, 10 and 14 extended; `tests/test_session7601_map.py`: 11 decisions become 12.
  - New: `site/scripts/map-read-page.mjs`, `site/scripts/test-map-read.mjs`, `docs/reviews/map-read-2026-11-16.md`, this report.
- **What does not change:** `site/data/map.json` and its builder, `site/app/map/page.tsx`, the Resources and Queues tabs, `/map/card`, `components/Num.tsx` and every hold, `site/lib/release.ts`, every table. With no point in the address the tab draws what it drew (the 123 views of `map-figures.mjs` are unchanged).
- **Before landing:** a site build of the merged commit (none made here); `check-map.mjs` (the controls and the address in a browser); `check-csp.mjs` on `/map` (no new request is made: the list is computed from the page's file).
- **Snapshot differences to expect:** none on the 25 addresses (every page is in review; a visitor sees the in-review page). With the review cookie, on `/map`: the panel's new "Near a point" line under "Size, MW", and the queue line after the sentence ("Queue positions are those of ERCOT, CAISO, SPP and ISO-NE alone: ..."), shown on the opening view since every grid is chosen. **Tables:** none.
- **After the landing:** rows 136 to 140 of `docs/state/browser_reads_wanted.md`. Rows 109 and 110 of `docs/state/data_requests_done_line.md` are the data machine's and do not hold this row.

### (b) Browser reads (`docs/state/browser_reads_wanted.md`)

| 136 | 2026-11-16 | 7537 | `wip/7537-map-read` (row 35) | `https://erw-flame.vercel.app/map?kind=planned,queue,datacenter&at=32.4487,-99.7331&within=30` | The drawing around Abilene, zoomed in; the list under the map | A pin at the point and a dashed circle around it, the marks inside it; the list "Within 30 miles of 32.4487, -99.7331, nearest first", 47 rows, Summerhill BESS first at 5.7 miles | wanted |
| 137 | 2026-11-16 | 7537 | `wip/7537-map-read` (row 35) | `https://erw-flame.vercel.app/map` | Type "32.4487, -99.7331" in "Near a point", then 30 in miles; then type letters in miles | The address gains `at=32.4487,-99.7331&within=30` and the sentence, tiles and list follow; letters leave the list gone and the address without `within` | wanted |
| 138 | 2026-11-16 | 7537 | `wip/7537-map-read` (row 35) | `https://erw-flame.vercel.app/map` | Click a unit on the drawing; press "Measure from this row" on its card; type 30 in miles | The point box holds the unit's coordinates; the list appears with the rows of its plant at the top, at 0.0 miles | wanted |
| 139 | 2026-11-16 | 7537 | `wip/7537-map-read` (row 35) | `https://erw-flame.vercel.app/map?kind=planned,queue,datacenter&at=35.3733,-119.0187&within=30` | At 390 px: the list, and the tips "how the distance is measured", "why some queues are not on the map", "the figures of this list" | No sideways scroll of the page; the table scrolls inside its frame; each tip stays inside the screen | wanted |
| 140 | 2026-11-16 | 7537 | `wip/7537-map-read` (row 35) | `https://erw-flame.vercel.app/map?kind=planned,queue,datacenter&at=43.1536,-93.201&within=30` | The sentence and the list | "Nothing on this map matches these choices. Queue positions are those of ERCOT, CAISO, SPP and ISO-NE alone: no queue position of PJM, MISO or NYISO is on this map."; the list "No row chosen lies within 30 miles of the point." | wanted |

### (c) Data requests (`docs/state/data_requests_done_line.md`)

| 109 | 2026-11-16 | 7537 (chain 304, samueloldlaptop; branch `wip/7537-map-read`) | `energy_projects` and `site/data/map.json` (`warehouse/derived/project_map.py`) | A queue position's only date in the table and the map's file is its queue date (`date_kind = queue_date`). A developer reading the map asks when a position plans to operate. Carry the queue report's proposed or projected operation date (where the grid operator's report states one: ERCOT, CAISO, SPP, ISO-NE) into `energy_projects` as a second date and into the map's file, so the list and the card can show it beside the queue date. Whether the ERW's per-ISO queue tables already keep it was not read on this machine | `docs/reviews/map-read-2026-11-16.md`, row 12 | requested |
| 110 | 2026-11-16 | 7537 (chain 304, samueloldlaptop; branch `wip/7537-map-read`) | `site/data/map.json` (`warehouse/derived/project_map.py`, its queue statuses) | The file's queue status "Completed" covers ERCOT's positions with a signed interconnection agreement, built or not (ERCOT's report has no status column; `energy_projects.md`, session 7518) and CAISO's, SPP's and ISO-NE's completed alike; the map's tile "Completed" cannot tell them apart. Write ERCOT's as its own status ("Agreement signed") in the file, as `/explore/interconnection` heads it, or as the data machine's fix to `energy_projects` rules | `docs/reviews/map-read-2026-11-16.md`, rows 5 and 13 | requested |

### (d) Progress line, part C (`docs/state/progress_c304.md`)

| C | `/map` | done `<head>` on `wip/7537-map-read` (landing row 35): the reader a developer checking what is planned within 30 miles of a candidate site; five cases (Abilene TX: 9 planned units 2,232 MW and 38 queue positions 11,559 MW requested, Summerhill BESS nearest at 5.7 miles; Amarillo TX: 163 planned units, 161 of them Project Matador's at one point 15.4 miles off; New Albany OH: 6 planned units, Flint 200 MW battery 4.1 miles off, PJM's queue not held; Mason City IA: nothing within 30 miles and MISO's queue not drawn; Bakersfield CA: 89 queue positions all at Kern County's point 16.4 miles off); the tab had no distance at all: now "Near a point", a list nearest first, the circle, a card's "Measure from this row"; rows: 18 (7 site fixed, 2 data machine, 5 browser, 4 rulings) | 7537 |
