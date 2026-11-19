# Chain 504, the portable laptop, 19 November 2026: where it stands

Energy Research Warehouse (ERW). Sessions 8600 to 8615 so far (10:40 to 18:45 UTC). Written at 16:13 UTC and kept current; the last line says when. Model spend USD 0. Nothing published; `site/lib/release.ts` not touched; every page in review.

## Read these first

- **The 3D network changed in one thing.** As it opens it now draws the hour its own slider names (148 ties where it drew the newest hour's 139). It was a fault, on production too. One line of `site/app/network/Network.tsx` to put back if you would rather.
- **Two packs to sign, about 45 minutes together, no Stata:** `docs/reviews/grid-map-regions-signature-pack-2026-11-19.md` (on `wip/8602-grid-regions`) and `docs/reviews/resources-signature-pack-2026-11-19.md` (on `wip/8603-resources`).
- **On a phone, a tap on the resource map shows no value; on production since the page was built.** A finger's lift counted as leaving the map and took the card off after 11 ms. The same on a region's hour by hour chart. Both fixed on the branches (session 8614) and waiting at the desk; measured on production again at 18:16 UTC. Every earlier read at 390 px had pointed with a mouse.
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
- **Part D, the natural resource map.** Done to the done line. The coal fields are on production since stack e (18:10 UTC): 602 fields, in square miles. Main's own check there: 94 of 97, the three the datacenter overlay's license hold.
  - On the branch since: a finger's tap, the keyboard's reading of the map's centre, one heading of level 1.
  - Replication of one layer 556 of 556; two cross-checks; ten decisions; a sign-off block.
  - Uranium and critical minerals: not fetched (the two hosts refuse automated reading).
- **Part E, the readers' reads.** Six reads, five readers each: the map twice, the regions twice (42 rows together), the resource map twice (17 rows). The phone read with a finger, the resource map with the keyboard, the new views probed for a screen reader. Every site fault fixed at its cause with a test.

## Waiting at the landing desk (`docs/state/landing_request_portable.md`)

- Row 42, `wip/8602-grid-regions` at `629d8ce96` (main merged in). Landed through `c527a0bb7` (stacks e and f, the second at 18:28 UTC); what came after waits for the desk's next gate.
- Row 43, `wip/8603-resources` at `6a368ed44` (main merged in). Landed through `4e2b2b54c` (stacks e and f); what came after waits for the desk's next gate.

## Asked of the data machine (`docs/state/data_requests_done_line.md`)

- 540, 541: came back as yours (each changes an existing page file). Default: left as it is.
- 543: the live set's lag. Cause found and fixed by the data machine.
- 544, 549, 551: the region files (months left out, zeros for a source never reported, hours that differ from EIA's). Answered or done on its branches.
- 542: coal done; uranium and critical minerals not fetched.
- 552: the coal fields' unit and one sentence. Requested.
- 553: plain words and units for the hover of the wind sites and the hot-water systems (they read as raw column names). Done by the data machine on its stack g, not landed yet.

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
13. **Site-wide:** a reason given on hover is the browser's own tooltip (about 1,100 on the site), which a finger never opens. Should a reason also open on a tap? Default: left as the site has it.
14. The shared Chart and Table switch is 22 px tall; the brand asks 24. Default: left (it is on every chart of the site).
11. A sun layer on Alaska is blank north of 60 degrees north (the source ends there): say so in the hover? Default: left; the layer's entry says it.
12. A card that stays after a tap on a phone: a close mark? Default: none; the next tap or a drag takes it off.

## Not done

- The Clean tab for a region is blank: carbon intensity is computed for the seven grids only (request 540).
- A balancing authority's own mix is in no file.
- No Stata do-file for the map or the regions; the resource map's has not been run.

Last written: 18:45 UTC, session 8615.
