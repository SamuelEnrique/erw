# Session 1048 report: a node's county, zone and wires utility

23 October 2026, from about 07:55 UTC, on samueloldlaptop, unattended, on `wip/1042-allgrids` (cut from chain 071's `wip/1039-allgrids`, main merged). Chain `queue/done/072-day-23-october-code-allgrids-packages-2.md`, session 1048. Model spend USD 0. No request to a publisher; no warehouse data written. Tables read: `ercot_node_places` and `ercot_transmission_projects`, rebuilt from the archive's bucket into `runs/archive_restore/`.

## Read these first

- **569 of the 873 nodes have a county and a load zone** (`ercot_node_places`, the data machine's chain 049, public): the county and zone ERCOT's CDR gives every unit at the node's station. The other 304 are blank and sort last: 295 with no CDR unit at their station, 9 whose units disagree (the table's own words, in the panel's tip).
- **The node list gains two columns, County and Zone**, after Days held (so that every figure stays in view at 1280; placed first, they pushed All-in and Days held off the screen). Both sort; two new filters (`nzone`, `ncounty` in the address); both go into the download (`node,class,county,zone,...`).
- **A node's panel names them**, or says "not placed" with the table's words. **Its wires utility stays "not held"**: the CDR names no EIA plant number, so no owner can be joined without a guess.
- **With the county, the panel counts ERCOT's transmission project phases with an end in it** (`ercot_transmission_projects`, the owners' report of 2026-07-13) by status, keyed `allgrids|nodeprojects|<node>|future|planned|completed`, names the earliest in-service date among the future and planned ones, and says "a project in the county is not a project at the node". Chain 071's session 1028 asked for this line.
- **No figure moved**: only `nodes.json`'s new keys were written (`county` and `zone` on a placed node, `places`, `projects`); every other value equals the file as built before (checked before the keys were added). Decision 31 of `docs/methods/siting.md`.
- Open items line 11 closed in part (county and zone; hub and wires utility open), line 12 closed in part (projects by county; substations and lines wait on HIFLD).

## What to review

1. `docs/brand/review-1048/n03_panel_1280.png`: 7RNCHSLR_ALL's panel, FAYETTE County, SOUTH zone; 7 future, 0 planned, 1 completed project phases; the earliest, 2029-05-15, LCRATSC Paige - Winchester Transmission Line Upgrade (138 kV).
2. `n02_county_sort_1280.png`: the list in zone WEST, sorted by county.
3. `n04_unplaced_1280.png`: ABINDUST_RN, "not placed".
4. On a build, internal view: `/cost-of-power?view=allgrids&rows=nodes&node=ercot%3A7RNCHSLR_ALL`, then choose a Zone and a County above the list, then "Download these N rows (CSV)".

## Screenshots

`docs/brand/review-1048/`: `n01_list` (1280, 390), `n02_county_sort` (1280), `n03_panel` (1280, 390), `n04_unplaced` (1280), `n05_reserve_tip` (1280, session 1047's tip), each with its page text. The "before" is session 1027's (`docs/brand/review-1027/`) and 1029's walk.

## Checks

| Check | Exit | Result |
|---|---|---|
| tests 1048, 1047, 1027, 724, 711, 700, 746, 795 | 0 | the builder's two functions on small files; the tab's file; the sort with the unplaced last; the filters and download; the panel; the replication |
| `npx tsc --noEmit` | 0 | after one fix: the library's `Files.nodes` type gains `projects` |
| `npm run build` (three times: after the type fix, the column order, the date's form) | 0 | no statement timeout |
| `walk.mjs`, 7 steps | 0 | the shots above |
| the replication's new figures (`project_figures`, test) | 0 | 7RNCHSLR_ALL: 7, 0, 1, equal to the page |

## The landing

Landed with sessions 1043 to 1061 in one push: `wip/1042-allgrids` gated by `scripts/land_check.py` at `a8a91dde` (freeze, main merged, task branches, the clean-copy suite 6,224 tests OK, npm ci, the build: pass; check-values: 12 failures, all the chain's known three: the ten license-held floors, `/digest` before the day's issue, and the 21 October Digest's revised WTI; every All grids value matched). As the rules say, the same commit was built locally on its own and checked by hand: check-routes 0 (225 pages in review, 0 failed), check-cross-checks 0 (92 passed), check-csp 0 (97 pages, 0 violations). Main then gained one queue file only (data chain 052's), merged without a third gate (`3306941d`). Snapshot `c072a-before` as its own command at 08:58 UTC; pushed to `task/1042-1061-allgrids` after the ancestry check; merged by run 39928557187 as `cbf8662e`; production served the node list's county filter (`data-node-county`) at 09:18 UTC (9 minutes of probing); `c072a-after` and `compare`: **0 differences** on the 25 pages (every page is in review: a visitor sees the in-review page), expected.

## Decisions made without you

1. **County and Zone after Days held**, not beside the name: the figures keep their place at 1280.
2. **Projects counted by either end's county**, a phase with both ends in it once; ERCOT's 9999-01-01 is no date.
3. **The report's date written 2026-07-13** (the workbook says "AS OF 7/13/2026"), the panel's other dates' form.
4. **The planned generation by county** stays a line that says "not drawn": the county is known, the sum is not built (a session of its own).

## For Samuel's ruling

- None new (the county map is rulings item 24, session 1049).

## Files

- Changed: `warehouse/derived/siting_page.py` (`node_places`, `county_projects`), `site/data/siting/nodes.json` (new keys), `site/lib/siting.ts`, `site/app/cost-of-power/AllGridsNodes.tsx`, `site/app/cost-of-power/AllGridsView.tsx`, `warehouse/replication/siting.py` (`project_figures`, the panel's address), `docs/methods/siting.md` (decision 31), `tests/test_session711.py` (the panel's words). New: `tests/test_session1048.py`, `docs/brand/review-1048/`, this report.
