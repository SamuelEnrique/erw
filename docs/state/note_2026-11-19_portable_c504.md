# Chain 504, the portable laptop, 19 November 2026: where it stands

Energy Research Warehouse (ERW). Sessions 8600 to 8613 so far (10:40 to 17:17 UTC). Written at 16:13 UTC and kept current; the last line says when. Model spend USD 0. Nothing published; `site/lib/release.ts` not touched; every page in review.

## Read these first

- **The 3D network changed in one thing.** As it opens it now draws the hour its own slider names (148 ties where it drew the newest hour's 139). It was a fault, on production too. One line of `site/app/network/Network.tsx` to put back if you would rather.
- **Two packs to sign, about 45 minutes together, no Stata:** `docs/reviews/grid-map-regions-signature-pack-2026-11-19.md` (on `wip/8602-grid-regions`) and `docs/reviews/resources-signature-pack-2026-11-19.md` (on `wip/8603-resources`).
- **On production until the desk's stack e lands (in review, so no visitor sees it):** the data machine's rebuilt region files are there with the page of session 8605. For the Carolinas, October's shares read "Wind 0.0%" and "0" MWh where the file holds blank, and the net load by hour is empty. The fix (session 8610) is in stack e, at the gate since 17:08 UTC.
- **Two faults on the old laptop's page `/demand?view=country`, on production** (its rows 386 and 391): a list keeps its old value after a click on a region; a table lists 500 of 3,061 days and the view opens three times slower than its neighbour.

## The parts against the chain

- **Part A, the browser reads.** About forty rows settled over the day; 5 left, each waiting for the old laptop's next landing (418 to 422).
- **Part B, the map of balancing authorities.** Done to the done line. Landed through session 8605 (the desk's stack d, 16:50 UTC) and read on production at 1280 and 390 px: main's own check 49 of 49. The rest waits at the desk.
  - The toggle Map, Network, Gravity in the address; regions colored on the spheres' scale; ties with width and motion; hovers; the same controls; a phone.
  - Opens in 0.4 to 0.8 s after "Map" is chosen, and is not loaded before.
  - Replication 439 of 439. Cross-check: each of 159 pairs is the report EIA publishes, to 1 MW.
  - Accessibility: two faults found and fixed (a keyboard and a screen reader now reach each region).
- **Part C, the thirteen regions in the Grid tool.** Done to the done line on the data machine's real files.
  - On the data machine's rebuilt files (on main since 16:50 UTC): replication 1,483 of 1,483. Cross-check read again: 388 of 439 figures are EIA's own regional figure to 1 MW.
  - A source never reported is blank, not zero, read for real (the Carolinas' wind). The trade tab reaches every year since 2018; a year's shares say of which months.
  - On production through session 8605: main's own check 25 of 25.
- **Part D, the natural resource map.** Done to the done line. The coal fields are on main; the branch draws them (602 fields) and its check switches them on. Production has the page of session 8603, which says "Coal fields not held" until row 43's newer head lands.
  - Replication of one layer 556 of 556; two cross-checks; ten decisions; a sign-off block.
  - Uranium and critical minerals: not fetched (the two hosts refuse automated reading).
- **Part E, the readers' reads.** Five reads, five readers each: the map twice (22 rows), the regions twice (19 rows), the resource map (8 rows). Every site fault fixed at its cause with a test.

## Waiting at the landing desk (`docs/state/landing_request_portable.md`)

- Row 42, `wip/8602-grid-regions` at `c527a0bb7` (main merged in). Stack e holds `43863e85d`; the two commits after it wait for the gate after that.
- Row 43, `wip/8603-resources` at `4e2b2b54c` (main merged in). Stack e holds `180880ef6`.

## Asked of the data machine (`docs/state/data_requests_done_line.md`)

- 540, 541: came back as yours (each changes an existing page file). Default: left as it is.
- 543: the live set's lag. Cause found and fixed by the data machine.
- 544, 549, 551: the region files (months left out, zeros for a source never reported, hours that differ from EIA's). Answered or done on its branches.
- 542: coal done; uranium and critical minerals not fetched.
- 552: the coal fields' unit and one sentence. Requested.

## Needs the key

- Nothing.

## For your ruling (each has its default taken; nothing waits)

1. A region's net exchange on the map: the sum of its pairs (PJM 811 MW), or the authority's own total beside it (82 MW)? Default: the sum, the difference said.
2. Canada's and Mexico's operators: marks at the border, or listed? Default: listed.
3. Thin state lines on the map. Default: drawn.
4. A region's color: of the latest hour held, not of the hour shown. Default: as the Network view.
5. California's "other" far below zero at midday (EIA's own figure): say more? Default: no.
6. The average day's chart draws a thin line to zero where a source crosses zero (the seven grids' own chart). Default: left.
7. Net load where solar or wind was never reported (New York, the Carolinas, Florida, the Southeast). Default: demand less what is reported, said on the page.
8. A wind or sun layer's hover repeats its vintage sentence. Default: left.
9. Uranium and critical minerals by a person's hand? Default: not fetched.
10. The 3D network's opening hour (first line above). Default: kept.

## Not done

- The Clean tab for a region is blank: carbon intensity is computed for the seven grids only (request 540).
- A balancing authority's own mix is in no file.
- No Stata do-file for the map or the regions; the resource map's has not been run.

Last written: 17:17 UTC, session 8613.
