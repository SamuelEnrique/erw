# Session 349 report: the map, phase two

20 October 2026, about 09:45 to 10:15 UTC, unattended, on portable-laptop (the third machine), the sixth session of the chain of 20 October, night. Branch `wip/348-map`, not landed. Model spend USD 0. Pulls: the Census Bureau's robots file and two gazetteers (2 of a ceiling of 4).

## Read these first

- **Queue positions placed by a city or a town.** `warehouse/derived/energy_projects.py` now tries county words that match no county, in the same state, against the Census Bureau's 2025 place gazetteer and then its county subdivision gazetteer; a name two places of one state share is never used. Such a row is `geo_precision` place, its `geo_note` names the place and the file, and its card says "city or town point; not the site itself".
- **The prompt's 1,172 unplaced positions were the count of 27 September.** In the table of 19 October (restored from the archive) 710 queue positions were unplaced; the two files place **355** of them (333 by a place, 22 by a town or township) and 355 stay unplaced (90 state no county, 76 no state, the rest name nothing either file holds). Measured on this machine (`runs/s349/placement.csv`); **no table was written**: `energy_projects` is the data machine's, and its daily run builds it with this code once landed.
- **The card links the generator tool** (`/cost-of-power/seller?iso=<grid>&asset=<technology>`) where that tool holds the grid and the technology (solar, wind, battery; a gas unit only when its own technology names a combustion turbine or a peaker), and says "not modeled" where it does not (MISO, which the tool leaves blank; PJM; NYISO solar; other technologies). The table of what it holds is tested against the tool's own snapshot.
- **A Queues tab on /map** (`/map?tab=queues&iso=<iso>`) draws `iso_queue_statistics`: entered against operating by year, the share withdrawn and the median wait, through the shared SeriesChart (Chart | Table), and every year in a table whose every figure is the table's own row, checked. What a queue does not hold is said (ERCOT's withdrawn positions; MISO's and ISO-NE's in-service dates; SPP's requested dates). A licensed grid is held from 21 October.
- **The count of unplaced positions** is above the map, a Num read from `energy_projects` (`projects|count|queue|none`).
- **The data machine's daily run rebuilds the map's copy** (`soft_step dm_project_map`, `site/data/map.json` and `map_v2.json` among its committed page paths), so new placements and the day's queues reach /map without waiting for the monthly run.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 349"` | 0 | |
| Census robots (`www2.census.gov/robots.txt`) | 200 | every path allowed to a general agent |
| the measurement (`runs/s349/measure.py`): the two gazetteers through the builder's own `fetch_gazetteer` | 0 | 355 of 710 placed; files kept in `warehouse/raw/census_gazetteer/20261020T094645Z/` |
| `eslint` on the changed page files | 0 | |
| `npm run build` | 0 | |
| `CHECK_VALUES_PAGES=/map,/impact check-values.mjs` | 0 | 907 of 907 (restricted: not the landing's gate) |
| `check-routes.mjs` | 0 | 216 pages in review, 0 failed |
| `bash -n warehouse/run_data_machine.sh` | 0 | |
| tests 349 (new), 239 (two pins move: the Economics menu has `/impact`, the map a third tab), 347, and the 50 modules that read the changed files | 0 for the chain's; the 50: 2 failures and 1 error left | the left ones read data tables absent or older here (sessions 90 and 92), as in session 347's suite |
| shots, `docs/brand/review-349/` | 0 | six |

## Decisions made without you

1. **One precision word, `place`, for both files**, with the file named in `geo_note`: the map already draws and words precision `place` (its datacenters use it), so no map code changed for it beyond the card's words "city or town point".
2. **The county comes first; a shared name is never used.** 212 place names and 3,540 subdivision names are shared within a state and dropped.
3. **No table and no map file was written here.** `energy_projects` and `site/data/map.json` are the data machine's; the measurement shows what its run will place. The landing changes the code and the daily step.
4. **A gas unit links the generator tool only when it is a peaker by its own words**: the tool's gas asset is a peaker, and a combined cycle is not one.
5. **The Queues tab opens on CAISO**, the queue with every measure held (withdrawals and waits); ERCOT lacks withdrawals.
6. **The tab's figures are the table's own rows**, so no new check family; the charts take the same values.

## For Samuel's ruling

- The resources tool (`/map?tab=resources`) counts only county and point rows as drawn: a position placed by a place stays "not drawn" there until its aggregation by county takes a place's county (the place files give no county). Leave it, or a session joins place to county.

## To finish

- On the data machine after the landing: its daily run places the positions and rebuilds the map's copy; nothing to run by hand.
- The code machine: Impeccable `detect` on `site/app/map/page.tsx`, `QueuesView.tsx`, `QueueCharts.tsx`, `ProjectMap.tsx` and `site/lib/projectmap.ts`.
