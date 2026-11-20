# Chain 620, the portable laptop, 20 November 2026: where it stands

Energy Research Warehouse (ERW). Sessions 9600 and 9601, from 10:26 UTC. Written at 12:30 UTC and kept current; the last line says when. Model spend USD 0. Nothing published; `site/lib/release.ts` not touched; every page in review. Every read is of production (`https://erw-flame.vercel.app`) in the internal view, at 1280 px with a mouse and at 390 px with a finger's screen.

## Read this first: since 19:20 UTC the chain is the desktop's second window's

At Samuel's word the desktop's second window (`C:\Users\Shared\Documents\erw-w2`, session 9203) took the chain over when this laptop stood down. Its own rules held: no landing, no warehouse table, no data lock, every build and browser check under `scripts/buildlock.py`. `queue/next/621-resume-chain-620.md` is removed and no resume file is written.

- **The ten fixes are seen in a build and their landing is requested,** as one row: row 4 of `docs/state/landing_request_window2.md`, branch `wip/w2-c620-fixes` at `1d7b451a6`. That branch is the ten branches merged onto main without a conflict, plus one more fix (below). Built twice on the desktop (68 s and 99 s, 6.5 to 8 GB free). In the build: the back button 16 of 16, the tour 101 of 103 (the Digest pair, a ruling), the other eight fixes 16 of 16. The tests that name a changed file: 544 passed, and the 2 that fail fail the same way on main. Rows 44 to 53 of this laptop's landing file are left as they were, with a note under them.
- **One more fix, found walking the tour as a reader:** stop 8 sent a reader to Tennessee's Network tab "for the map". That tab opens on the 3D network, as your ruling has it, and the map is one more press, on Map. The stop also said "Ask" stands "at the foot of the page", where on a wide screen it is beside the tool. Both mended in the stop's words, with a test; seen in the build.
- **Read in full, with five readers' cases, every figure against its page file and the hand checks:** `/demand?view=country` (6,431 figures), `/supply#whole-country` (11,119), the events' whole-country section over four events (912). None differs from its file. The keyboard reached the foot on each (62, 236 and 101 stops), a finger brought up a card on every chart (8, 14 and 15), and the back button and fresh links kept their lists true.
- **New for your ruling** (each page left as it is):
  - On an event page, a pair of regions' mean and its baseline's each rest on their own hours. The section's own note says every figure uses the hours both hold. This touches 10 of the 224 pairs, and Elliott's Central and Canada most (17 MW over 267 hours against a baseline over 219). The old laptop's pending branch rewrites the same lines and keeps the same rule, so it is not edited here.
  - On `/supply`, a pair with both reports at 0 reads its percent as "not held yet". That percent can never be held.
- **After that (21:30 UTC to 00:30 UTC on 21 November):**
  - A third fix, on `/curtailment/where-when`: the trend table named no fuel over solar alone (3,482 GWh "curtailment", where `/curtailment` gives 3,765.6 for wind and solar). It now names its fuel, seen in a build, and row 4 names `4f3247287`.
  - Every page check-values knows: 9,067 of 9,067 figures match Supabase.
  - The pages that draw from files were set beside them, with none differing: the board's 271 rows (4,150 figures over two widths), `/prices/compare`, `/contracts` (227 rows in `ferc_eqr_contracts`), `/companies` and `/severance`'s calculator.
  - The keyboard alone reaches the foot of all 27 menu pages, with a focus mark at every stop.
  - Part C has eleven pairs now. CAISO's curtailment by year agrees between its two pages, and WTI agrees between the severance tool and the board.
  - A fourth fix: `/events/covid-2020` was 392 px wide at 390 px with a chart switched to its table. It is mended, seen in a build, and row 4 now names `923d4cb4f`.
  - On the nine event pages, 146 held figures read "license needed MW" or "license needed%": the unit stays after the hold's words. Not mended here; it goes with your ruling on those pages' hold.
  - Rows 418 to 422: the old laptop's three branches, which never reached main, each do what their row asks on a build of today's main. Their landing is the desk's.
- **Filed:** data request 570. The region page files have not been rebuilt since 19 November, so Tennessee's latest hour held is 17 November 05:00 UTC while the Lower 48 beside it reads 19 November.
- **Pictures:** the tour's stops 8 to 16 and each page they open (`tour/`); the demand, supply and events reads (`demand-country/`, `supply-country/`, `events-country/`); the fixes as the build shows them (`fixes-seen-in-a-build/`); and ten pages that had none (`more/`). All are under `docs/reviews/browser-read-2026-11-20/`, also on GitHub at `https://github.com/SamuelEnrique/erw/tree/main/docs/reviews/browser-read-2026-11-20`.

## Before that: a build was started and stopped on the laptop, and the laptop stood down

- At 18:29 UTC the laptop had 2.2 GB of memory free and the one build of the ten fixes was started (`local/c620-build` in `C:\Users\lossa\Documents\erw-c504`). Claude Code stopped it before it finished, because the system ran critically low on memory; at 18:47 UTC 425 MB were free with nothing of the chain's running. It left no process and no changed file.
- It is not started again: Claude Code's own instruction is to start it again only when asked. So the ten fixes are still on their branches, not seen in a build, and no landing is requested (rows 44 to 53 of `docs/state/landing_request_portable.md`).
- Since 18:47 UTC the chain runs nothing heavy on this laptop: no build, no browser, no watcher. The resume file `queue/next/621-resume-chain-620.md` is kept.
- To land the fixes: close what holds the memory (Chrome held 2.1 to 3.8 GB through the night), then the steps under "To finish" of `archive/sessions/SESSION_9601_REPORT.md`; or let the data machine's desk build `local/c620-build`'s ten branches, whose rows say what to look at.

## Read these first: the five worst things found

1. **The live set was not loaded from 16 November until about 16:00 UTC on 20 November** (it now holds demand to 19 November 23:00 UTC and the Grid tool shows it again; the load left 16 November out, data request 569). As read through the night: Demand and generation end on 15 November 23:00 UTC, carbon intensity on 12 November. On the Grid tool every authority reads "Demand: not held for this hour" for the 53 newest hours, ERCOT's page heads its demand "Nov 15, 5:00 PM CST", the map's carbon color is 12 November's, and the board's day-ahead prices are four days old. Data request 565 (it is request 543 again, a day after 543 was marked fixed).
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
- **Part E:** the five sellable tools and 22 more pages of the menu at 390 px with a finger, and the five tools with the keyboard alone: no fault. Every page with a fixed address (80) at both widths: one more phone fault (`/data/faults`).
- **Landed during the night and read on production (13:50 UTC):** the data machine's `/congestion` (4,290 figures agree with its file; no fault) and `/conditions` (one fault, filed and since fixed).

## Faults: found, fixed, filed

- **Found:** 10 site faults of pages this laptop may mend, 1 on the data machine's new page, 4 data faults, 1 landing that did not happen.
- **On `/conditions` (filed, request 568; fixed by the data machine at 16:32 UTC and seen fixed on production):** as the page opened, two charts were drawn with axes and nothing on them (ERCOT's reserve adder ended in December 2025). A second point of mine was wrong and is withdrawn: the chart's table pages 500 rows at a time.
- **`/data/faults` at 390 px** (417 px wide) is the tenth fix, on `wip/9602-faults-page-phone`.
- **Fixed, each on its own branch with a test (the first 9):** the back button and the lists; the findings page at 390 px (470 px wide); the resource problem set's legend (it gave 2.81 to 6.50, the map shows 1.6 to 6.9); "Net imports met -592 percent of its demand" in the Grid tool's panel (26 of 58 authorities); the tour's stale headings (stops 1, 4, 11 and 12); the Policy page; the Grid map's "twelve months" (34.86 on the map, 34.59 on `/prices/compare`: different windows, now said); a transmission line's end printed as "UNKNOWN201257" (a third of the lines); six method pages that scroll sideways on a phone.
- **Filed for the data machine (6, with 569: no hour of 16 November in the live set):** 562 (an entry of Arizona Public Service in North Carolina on `/queues/places`), 563 (Texas's law; answered at 13:43 UTC: the page now says S.B. 6 was found and is withheld), 565 (the live set), 567 (the dated edition of the resource set), 568 (`/conditions`).

## Not landed, and why

- **No fix has been seen in a build, so no landing is requested.** The chain asks for 2 GB of memory free before a build; this laptop had 1.0 to 1.9 GB free from 11:37 UTC (Samuel's own Chrome, the Claude programs and the mail and chat programs hold the rest). The whole suite is the desk's gate's, not this laptop's (rule 6 of 16 November); here each change's own tests pass, and the 79 test files that walk the whole site (1,134 tests) show the same four failures on the nine branches together as on main (`test_session161`, `test_session78`, `test_session8410_events_regions`, `test_session8430_supply_regions`), none of them new. The changed files and what they import type-check (0 errors).
- The ten branches are pushed, and rows 44 to 53 of `docs/state/landing_request_portable.md` read "ready, not requested", each with what is left to do.
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

Last written: 18:48 UTC, session 9602; the section at the top by the desktop's second window, last at 00:35 UTC on 21 November, session 9203.
