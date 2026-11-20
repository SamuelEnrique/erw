# Chain 620, the portable laptop, 20 November 2026: where it stands

Energy Research Warehouse (ERW). Sessions 9600 and 9601, from 10:26 UTC. Written at 12:30 UTC and kept current; the last line says when. Model spend USD 0. Nothing published; `site/lib/release.ts` not touched; every page in review. Every read is of production (`https://erw-flame.vercel.app`) in the internal view, at 1280 px with a mouse and at 390 px with a finger's screen.

## Read these first: the five worst things found

1. **The live set has not been loaded since 16 November.** Demand and generation end on 15 November 23:00 UTC, carbon intensity on 12 November. On the Grid tool every authority reads "Demand: not held for this hour" for the 53 newest hours, ERCOT's page heads its demand "Nov 15, 5:00 PM CST", the map's carbon color is 12 November's, and the board's day-ahead prices are four days old. Data request 565 (it is request 543 again, a day after 543 was marked fixed).
2. **Three of the old laptop's branches read "landed" and their last fixes are not on production.** Sessions 8470, 8480 and 8490 (15 commits to the events, demand and supply pages). The landing rows took newer heads after the desk had landed the older ones, and the state stayed "landed". A note stands at the foot of `docs/state/landing_request_oldlaptop.md`.
3. **After the browser's back button a list keeps the later choice** while the page and its address go back: the table says PacifiCorp, the list says Duke. On every page that draws the site's shared list (13 page files). Mended on a branch.
4. **The menu's "Policy" opens a page that is the two words "license needed".** No heading, no way to the two views that do draw. Mended on a branch (nothing held is drawn).
5. **`/states` opens on Texas and says the ERW holds no large-load law for Texas.** The policy monitor's own files name Texas's SB 6. Data request 563.

## What was read

- **The list:** 26 pages and views landed since 17 November (`docs/reviews/browser-read-2026-11-20.md`). All 26 were opened at both widths; none shows "undefined", an empty chart or an error as it opens.
- **Read in full, with five readers' cases each and every marked figure set beside its page file:** `/queues/places`, `/curtailment/where-when`, `/storage/places`, `/states` (all 52 places), `/industry`, `/ai-energy`, the board's four new metals, the Grid map's Price color and each authority's own facts, the forecast section of `/demand`, the project map's two line layers, the findings review page, the five new problem sets, the dated edition. More than 14,000 figures set beside their files; none differs from its file.
- **Opened again for quiet faults:** 101 addresses of the pages chain 504 and the old laptop had read (the thirteen regions in the Grid tool, the nine events, `/demand` and `/supply` by region), and all 609 method pages at 390 px.
- **Part C, the same number in two places:** seven pairs. Three agree to the megawatt; three are different things and say so; one read as a contradiction and is mended.
- **Part D, the first minute:** as a stranger every address is the in-review page; as a reviewer 52 of 53 addresses of the menu, the home page and the tour answer with their heading.

## Faults: found, fixed, filed

- **Found:** 9 site faults, 4 data faults, 1 landing that did not happen.
- **Fixed, each on its own branch with a test (9):** the back button and the lists; the findings page at 390 px (470 px wide); the resource problem set's legend (it gave 2.81 to 6.50, the map shows 1.6 to 6.9); "Net imports met -592 percent of its demand" in the Grid tool's panel (26 of 58 authorities); the tour's stale headings (stops 1, 4, 11 and 12); the Policy page; the Grid map's "twelve months" (34.86 on the map, 34.59 on `/prices/compare`: different windows, now said); a transmission line's end printed as "UNKNOWN201257" (a third of the lines); six method pages that scroll sideways on a phone.
- **Filed for the data machine (4):** 562 (an entry of Arizona Public Service in North Carolina on `/queues/places`), 563 (Texas's law), 565 (the live set), 567 (the dated edition of the resource set).

## Not landed, and why

- **No fix has been seen in a build, so no landing is requested.** The chain asks for 2 GB of memory free before a build; this laptop had 1.0 to 1.9 GB free from 11:37 UTC (Samuel's own Chrome, the Claude programs and the mail and chat programs hold the rest). The whole suite is the desk's gate's, not this laptop's (rule 6 of 16 November); here each change's own tests pass, and the 79 test files that walk the whole site (1,134 tests) show the same four failures on the nine branches together as on main (`test_session161`, `test_session78`, `test_session8410_events_regions`, `test_session8430_supply_regions`), none of them new.
- The nine branches are pushed, and rows 44 to 52 of `docs/state/landing_request_portable.md` read "ready, not requested", each with what is left to do.
- What was seen without a build: the back button's mend on a plain page in a real browser, and its logic put into six of production's own pages (6 of 6 keep their lists true; 0 of 6 as production is); the mended tour and its check against production's pages (94 of 97, where it was 89 of 96); the findings page and the six method pages 390 px wide with the branch's style put on production's page; the tour's and the back button's checks failing on production as they should before the mend.

## Where the pictures are

- In the repository: `docs/reviews/browser-read-2026-11-20/`, a folder a page, two or three pictures each at 1280 px (as it opens; after its most telling choice).
- On this laptop: `C:\Users\lossa\Documents\erw\docs\reviews\browser-read-2026-11-20\`.
- On GitHub: `https://github.com/SamuelEnrique/erw/tree/main/docs/reviews/browser-read-2026-11-20`.

## What waits for you, each page left as it is

1. **A figure given only on hover cannot be read on a phone or with a keyboard.** It is the browser's own tooltip. On `/curtailment/where-when` that is every figure of the hour by month grid (288 cells): a phone shows shades and no number. This is the question chain 504 left you (should a reason also open on a tap?). Default: left.
2. **Six new pages have no way in from the menu.** `/states`, `/industry` and `/ai-energy` are reached only from the tour; `/queues/places`, `/storage/places` and `/curtailment/where-when` are linked from no page at all. Where each goes in the menu is yours. Default: left.
3. **The tour's Digest stop opens a page with no Digest.** None has been written since 12 November (the Digest is paused). Default: left.
4. **`/queues/places` names each queue owner by LBNL's abbreviation alone** ("S-C", "N-C", "IP", "CLPT"). Default: left.
5. **A stranger at the home address sees the heading "/"**; pages with no name in the release list show their address as a heading. Default: left (the release list is not touched).
6. **On the board, a monthly row's range over a year holds twelve months and the workbench's "Year" window thirteen**: tin's low reads 36,012 in one and 34,484 in the other. Default: left.
7. **On the Grid map an authority outside the seven ISOs reads "Demand: not held for this hour" at every hour**, which suggests another hour would hold it. Default: left.

## Decisions made without you

- The tour's fourth stop, written "One grid at a time, ERCOT first", now opens `/grid?grid=ercot`. `/grid` alone has opened on the Lower 48 since session 299, where two of the stop's headings are not. To put it back: one line of `site/lib/tour.ts` on `wip/9601-tour-headings`, and the address in `tests/test_session292.py`.
- The tour's first stop says "Assumptions" where it said "Your battery": the box was renamed by your ruling of 15 October.
- A note for the desk and the old laptop was added under the table of the old laptop's landing file; no row of it was changed.

## Needs the key

- Nothing.

Last written: 13:06 UTC, session 9602.
